#!/usr/bin/env python3
"""
Eval runner for bomb-skills.

Uses Claude Code CLI (claude -p) as subagent to execute evals.
Each eval runs twice: with_skill (SKILL.md loaded) and without_skill (baseline).
A separate grading call evaluates assertions against actual output.

Parallelism:
- All evals run concurrently (ThreadPoolExecutor)
- Within each eval, with_skill and without_skill run concurrently
- Grading uses haiku model for speed

Follows the agentskills.io eval format:
- Evals defined in evals/<skill-name>/evals.json
- Results stored in <skill-name>-workspace/iteration-N/
- Outputs: grading.json, timing.json, benchmark.json, feedback.json

Usage:
    python3 evals/run_evals.py <skill-name>              # Run skill-only evals (fast, no baseline)
    python3 evals/run_evals.py <skill-name> --baseline   # Run with baseline comparison
    python3 evals/run_evals.py <skill-name> --eval 1,2   # Run specific eval IDs only
    python3 evals/run_evals.py --all                     # Run all evals
    python3 evals/run_evals.py --list                    # List available evals
    python3 evals/run_evals.py <skill-name> --improve    # Suggest SKILL.md improvements from latest iteration
    python3 evals/run_evals.py <skill-name> --deploy     # Deploy skill to testing folder for manual testing
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

EVALS_DIR = Path(__file__).parent
PROJECT_DIR = EVALS_DIR.parent
SKILLS_DIR = PROJECT_DIR / "skills"

MODEL_EVAL = "sonnet"
MODEL_GRADING = "sonnet"
DEPLOY_DIR = PROJECT_DIR.parent / f"deploy-{PROJECT_DIR.name}"


def load_eval_spec(skill_name: str) -> dict:
    """Load the evals.json for a given skill."""
    eval_file = EVALS_DIR / skill_name / "evals.json"
    if not eval_file.exists():
        print(f"Error: No eval spec found at {eval_file}")
        sys.exit(1)
    with open(eval_file) as f:
        return json.load(f)


def check_skill_exists(skill_name: str) -> bool:
    """Check if the skill implementation exists."""
    skill_md = SKILLS_DIR / skill_name / "SKILL.md"
    return skill_md.exists()


def validate_eval_spec(spec: dict) -> list[str]:
    """Validate an eval spec and return any errors."""
    errors = []
    if "skill_name" not in spec:
        errors.append("Missing 'skill_name' field")
    if "evals" not in spec:
        errors.append("Missing 'evals' field")
    elif not isinstance(spec["evals"], list):
        errors.append("'evals' must be a list")
    else:
        for i, ev in enumerate(spec["evals"]):
            if "id" not in ev:
                errors.append(f"Eval {i}: missing 'id'")
            if "prompt" not in ev:
                errors.append(f"Eval {i}: missing 'prompt'")
            if "expected_output" not in ev:
                errors.append(f"Eval {i}: missing 'expected_output'")
    return errors


def get_next_iteration(workspace_dir: Path) -> int:
    """Get the next iteration number for a workspace."""
    if not workspace_dir.exists():
        return 1
    existing = [
        int(d.name.split("-")[1])
        for d in workspace_dir.iterdir()
        if d.is_dir() and d.name.startswith("iteration-")
    ]
    return max(existing, default=0) + 1


def create_workspace_structure(skill_name: str, spec: dict, run_baseline: bool = True) -> Path:
    """Create workspace directory structure for an eval iteration."""
    workspace_dir = PROJECT_DIR / f"{skill_name}-workspace"
    iteration = get_next_iteration(workspace_dir)
    iteration_dir = workspace_dir / f"iteration-{iteration}"

    variants = ["with_skill"]
    if run_baseline:
        variants.append("without_skill")

    for ev in spec["evals"]:
        eval_name = f"eval-{ev['id']}"
        for variant in variants:
            outputs_dir = iteration_dir / eval_name / variant / "outputs"
            outputs_dir.mkdir(parents=True, exist_ok=True)

    return iteration_dir


def run_claude(prompt: str, system_prompt: str | None = None, model: str = MODEL_EVAL) -> dict:
    """Run a prompt through Claude Code CLI and return parsed JSON result."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--no-session-persistence",
        "--model", model,
    ]
    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip(), "result": "", "duration_ms": 0, "usage": {}}
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"error": "Timeout after 120s", "result": "", "duration_ms": 120000, "usage": {}}
    except json.JSONDecodeError:
        return {"error": "Failed to parse Claude output", "result": result.stdout, "duration_ms": 0, "usage": {}}


def extract_timing(claude_result: dict) -> dict:
    """Extract timing data from Claude CLI JSON result."""
    usage = claude_result.get("usage", {})
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    cache_creation = usage.get("cache_creation_input_tokens", 0)
    return {
        "total_tokens": input_tokens + output_tokens + cache_read + cache_creation,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_input_tokens": cache_read,
        "cache_creation_input_tokens": cache_creation,
        "duration_ms": claude_result.get("duration_ms", 0),
        "cost_usd": claude_result.get("total_cost_usd", 0),
    }


def grade_assertions(output: str, assertions: list[str]) -> dict:
    """Use Claude (haiku) to grade assertions against actual output."""
    if not assertions:
        return {
            "assertion_results": [],
            "summary": {"passed": 0, "failed": 0, "total": 0, "pass_rate": 0.0},
        }

    assertions_text = "\n".join(f"{i+1}. {a}" for i, a in enumerate(assertions))
    grading_prompt = f"""Grade each assertion against the actual output below.
For each assertion, respond with PASS or FAIL and brief evidence.

ACTUAL OUTPUT:
---
{output}
---

ASSERTIONS:
{assertions_text}

Respond in this exact JSON format (no markdown, no code fences):
{{
  "assertion_results": [
    {{"text": "assertion text", "passed": true/false, "evidence": "brief quote or reason"}}
  ]
}}"""

    result = run_claude(
        grading_prompt,
        system_prompt="You are an eval grader. Output only valid JSON, no markdown fences.",
        model=MODEL_GRADING,
    )

    response_text = result.get("result", "")

    # Try to parse grading response as JSON
    try:
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
        if cleaned.endswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[:-1])
        grading = json.loads(cleaned.strip())
    except (json.JSONDecodeError, ValueError):
        grading = {
            "assertion_results": [
                {"text": a, "passed": None, "evidence": f"Grading parse failed. Raw: {response_text[:200]}"}
                for a in assertions
            ]
        }

    # Compute summary
    results_list = grading.get("assertion_results", [])
    passed = sum(1 for r in results_list if r.get("passed") is True)
    failed = sum(1 for r in results_list if r.get("passed") is False)
    total = len(results_list)
    grading["summary"] = {
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": round(passed / total, 2) if total > 0 else 0.0,
    }

    return grading


def run_variant(ev: dict, variant: str, skill_name: str, iteration_dir: Path) -> dict:
    """Run a single variant (with_skill or without_skill) for one eval."""
    eval_name = f"eval-{ev['id']}"
    prompt = ev["prompt"]
    assertions = ev.get("assertions", [])
    eval_dir = iteration_dir / eval_name / variant

    # Build system prompt
    if variant == "with_skill":
        skill_md_path = SKILLS_DIR / skill_name / "SKILL.md"
        skill_content = skill_md_path.read_text()

        # Inline references/ files (simulates Claude Code's progressive disclosure)
        refs_dir = SKILLS_DIR / skill_name / "references"
        if refs_dir.exists():
            for ref_file in sorted(refs_dir.iterdir()):
                if ref_file.is_file():
                    skill_content += f"\n\n## Reference: {ref_file.name}\n{ref_file.read_text()}"

        system_prompt = f"Follow the instructions in this skill:\n\n{skill_content}"
    else:
        system_prompt = None

    # Execute prompt via Claude CLI
    claude_result = run_claude(prompt, system_prompt)

    # Save raw output
    output_text = claude_result.get("result", "")
    with open(eval_dir / "outputs" / "response.txt", "w") as f:
        f.write(output_text)

    # Write timing
    timing = extract_timing(claude_result)
    with open(eval_dir / "timing.json", "w") as f:
        json.dump(timing, f, indent=2)

    # Grade assertions
    if output_text and assertions:
        grading = grade_assertions(output_text, assertions)
    elif not output_text:
        error = claude_result.get("error", "No output")
        grading = {
            "assertion_results": [
                {"text": a, "passed": False, "evidence": f"No output: {error}"}
                for a in assertions
            ],
            "summary": {
                "passed": 0,
                "failed": len(assertions),
                "total": len(assertions),
                "pass_rate": 0.0,
            },
        }
    else:
        grading = {
            "assertion_results": [],
            "summary": {"passed": 0, "failed": 0, "total": 0, "pass_rate": 0.0},
        }

    with open(eval_dir / "grading.json", "w") as f:
        json.dump(grading, f, indent=2)

    return {
        "pass_rate": grading.get("summary", {}).get("pass_rate"),
        "timing": timing,
    }


def run_single_eval(ev: dict, skill_name: str, iteration_dir: Path, run_baseline: bool = True) -> dict:
    """Run a single eval — with_skill and optionally without_skill in parallel."""
    eval_result = {"id": ev["id"], "variants": {}}

    variants = ["with_skill"]
    if run_baseline:
        variants.append("without_skill")

    with ThreadPoolExecutor(max_workers=len(variants)) as executor:
        futures = {
            executor.submit(run_variant, ev, variant, skill_name, iteration_dir): variant
            for variant in variants
        }
        for future in as_completed(futures):
            variant = futures[future]
            eval_result["variants"][variant] = future.result()

    return eval_result


def run_eval(skill_name: str, spec: dict, run_baseline: bool = True) -> dict:
    """Run all evaluations for a skill — all evals in parallel."""
    skill_exists = check_skill_exists(skill_name)
    iteration_dir = create_workspace_structure(skill_name, spec, run_baseline)

    results = {
        "skill_name": skill_name,
        "skill_exists": skill_exists,
        "iteration_dir": str(iteration_dir),
        "evals": [],
    }

    if not skill_exists:
        print(f"  Skill '{skill_name}' not yet implemented (TDD: this is expected)")
        for ev in spec["evals"]:
            eval_name = f"eval-{ev['id']}"
            eval_dir = iteration_dir / eval_name / "with_skill"

            timing = {"total_tokens": 0, "duration_ms": 0}
            with open(eval_dir / "timing.json", "w") as f:
                json.dump(timing, f, indent=2)

            grading = {
                "assertion_results": [
                    {"text": a, "passed": False, "evidence": "Skill not yet implemented"}
                    for a in ev.get("assertions", [])
                ],
                "summary": {
                    "passed": 0,
                    "failed": len(ev.get("assertions", [])),
                    "total": len(ev.get("assertions", [])),
                    "pass_rate": 0.0,
                },
            }
            with open(eval_dir / "grading.json", "w") as f:
                json.dump(grading, f, indent=2)

            results["evals"].append({
                "id": ev["id"],
                "status": "skipped",
                "reason": "skill not implemented",
            })

        write_benchmark(iteration_dir, results["evals"], spec)
        return results

    # Run all evals in parallel
    mode = "with baseline" if run_baseline else "skill-only"
    print(f"  Running {len(spec['evals'])} evals in parallel ({mode})...")
    all_eval_results = []

    with ThreadPoolExecutor(max_workers=len(spec["evals"])) as executor:
        futures = {
            executor.submit(run_single_eval, ev, skill_name, iteration_dir, run_baseline): ev
            for ev in spec["evals"]
        }
        for future in as_completed(futures):
            ev = futures[future]
            eval_result = future.result()
            all_eval_results.append(eval_result)

            with_pr = eval_result["variants"].get("with_skill", {}).get("pass_rate")
            without_pr = eval_result["variants"].get("without_skill", {}).get("pass_rate")
            status = "passed" if with_pr == 1.0 else "partial" if (with_pr or 0) > 0 else "failed"

            if run_baseline:
                print(f"  Eval {ev['id']}: with_skill={with_pr}, without={without_pr} [{status}]")
            else:
                print(f"  Eval {ev['id']}: {with_pr} [{status}]")

            result_entry = {
                "id": ev["id"],
                "status": status,
                "with_skill_pass_rate": with_pr,
            }
            if run_baseline:
                result_entry["without_skill_pass_rate"] = without_pr
            results["evals"].append(result_entry)

    # Sort results by eval id for consistent output
    results["evals"].sort(key=lambda e: e["id"])
    all_eval_results.sort(key=lambda e: e["id"])

    write_benchmark(iteration_dir, results["evals"], spec, all_eval_results)
    return results


def write_benchmark(iteration_dir: Path, eval_results: list, spec: dict, detailed_results: list | None = None):
    """Write benchmark.json and feedback.json."""
    if detailed_results:
        with_rates = [r["variants"]["with_skill"]["pass_rate"] or 0 for r in detailed_results]
        with_times = [r["variants"]["with_skill"]["timing"]["duration_ms"] / 1000 for r in detailed_results]
        with_tokens = [r["variants"]["with_skill"]["timing"]["total_tokens"] for r in detailed_results]

        has_baseline = "without_skill" in detailed_results[0]["variants"]
        if has_baseline:
            without_rates = [r["variants"]["without_skill"]["pass_rate"] or 0 for r in detailed_results]
            without_times = [r["variants"]["without_skill"]["timing"]["duration_ms"] / 1000 for r in detailed_results]
            without_tokens = [r["variants"]["without_skill"]["timing"]["total_tokens"] for r in detailed_results]
        else:
            without_rates = [0] * len(detailed_results)
            without_times = [0] * len(detailed_results)
            without_tokens = [0] * len(detailed_results)

        n = len(detailed_results)
        benchmark = {
            "run_summary": {
                "with_skill": {
                    "pass_rate": {"mean": round(sum(with_rates) / n, 2)},
                    "time_seconds": {"mean": round(sum(with_times) / n, 1)},
                    "tokens": {"mean": round(sum(with_tokens) / n)},
                },
                "without_skill": {
                    "pass_rate": {"mean": round(sum(without_rates) / n, 2) if has_baseline else None},
                    "time_seconds": {"mean": round(sum(without_times) / n, 1) if has_baseline else None},
                    "tokens": {"mean": round(sum(without_tokens) / n) if has_baseline else None},
                },
                "delta": {
                    "pass_rate": round(sum(with_rates) / n - sum(without_rates) / n, 2) if has_baseline else None,
                    "time_seconds": round(sum(with_times) / n - sum(without_times) / n, 1) if has_baseline else None,
                    "tokens": round(sum(with_tokens) / n - sum(without_tokens) / n) if has_baseline else None,
                },
            }
        }
    else:
        benchmark = {
            "run_summary": {
                "with_skill": {"pass_rate": {"mean": 0.0}, "time_seconds": {"mean": 0.0}, "tokens": {"mean": 0}},
                "without_skill": {"pass_rate": {"mean": 0.0}, "time_seconds": {"mean": 0.0}, "tokens": {"mean": 0}},
                "delta": {"pass_rate": 0.0, "time_seconds": 0.0, "tokens": 0},
            }
        }

    with open(iteration_dir / "benchmark.json", "w") as f:
        json.dump(benchmark, f, indent=2)

    feedback = {f"eval-{ev['id']}": "" for ev in spec["evals"]}
    with open(iteration_dir / "feedback.json", "w") as f:
        json.dump(feedback, f, indent=2)


def get_latest_iteration(skill_name: str) -> Path | None:
    """Find the latest iteration directory for a skill."""
    workspace_dir = PROJECT_DIR / f"{skill_name}-workspace"
    if not workspace_dir.exists():
        return None
    iterations = sorted(
        [d for d in workspace_dir.iterdir() if d.is_dir() and d.name.startswith("iteration-")],
        key=lambda d: int(d.name.split("-")[1]),
    )
    return iterations[-1] if iterations else None


def improve_skill(skill_name: str):
    """Read latest iteration results + feedback, ask Claude to suggest SKILL.md improvements."""
    iteration_dir = get_latest_iteration(skill_name)
    if not iteration_dir:
        print(f"Error: No eval results found for '{skill_name}'. Run evals first.")
        sys.exit(1)

    skill_md_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_md_path.exists():
        print(f"Error: No SKILL.md found at {skill_md_path}")
        sys.exit(1)

    spec = load_eval_spec(skill_name)
    skill_content = skill_md_path.read_text()

    # Load feedback
    feedback_path = iteration_dir / "feedback.json"
    feedback = {}
    if feedback_path.exists():
        with open(feedback_path) as f:
            feedback = json.load(f)

    has_feedback = any(v.strip() for v in feedback.values())
    if not has_feedback:
        print(f"Warning: feedback.json in {iteration_dir.name} is empty.")
        print(f"Edit {feedback_path} to add your review comments, then run --improve again.")
        print(f"\nExample feedback.json:")
        print(json.dumps({f"eval-{ev['id']}": "your feedback here or empty string if ok" for ev in spec["evals"]}, indent=2))
        sys.exit(0)

    # Collect per-eval signals: grading results, actual outputs, feedback
    eval_signals = []
    for ev in spec["evals"]:
        eval_name = f"eval-{ev['id']}"
        signal = {
            "eval_id": ev["id"],
            "prompt": ev["prompt"],
            "expected_output": ev["expected_output"],
            "feedback": feedback.get(eval_name, ""),
        }

        # Load with_skill grading and output
        with_skill_dir = iteration_dir / eval_name / "with_skill"
        grading_path = with_skill_dir / "grading.json"
        output_path = with_skill_dir / "outputs" / "response.txt"

        if grading_path.exists():
            with open(grading_path) as f:
                grading = json.load(f)
            failed = [r for r in grading.get("assertion_results", []) if r.get("passed") is False]
            signal["failed_assertions"] = failed
            signal["pass_rate"] = grading.get("summary", {}).get("pass_rate")

        if output_path.exists():
            signal["actual_output"] = output_path.read_text()

        eval_signals.append(signal)

    # Build the improve prompt
    signals_text = ""
    for s in eval_signals:
        signals_text += f"\n### Eval {s['eval_id']}\n"
        signals_text += f"**Prompt:** {s['prompt']}\n"
        signals_text += f"**Expected:** {s['expected_output']}\n"
        signals_text += f"**Pass rate:** {s.get('pass_rate', 'N/A')}\n"

        if s.get("failed_assertions"):
            signals_text += "**Failed assertions:**\n"
            for fa in s["failed_assertions"]:
                signals_text += f"  - {fa['text']} (evidence: {fa.get('evidence', 'N/A')})\n"

        if s.get("feedback"):
            signals_text += f"**Human feedback:** {s['feedback']}\n"

        if s.get("actual_output"):
            # Truncate long outputs
            output = s["actual_output"]
            if len(output) > 500:
                output = output[:500] + "\n... (truncated)"
            signals_text += f"**Actual output:**\n```\n{output}\n```\n"

    improve_prompt = f"""You are improving an AI agent skill based on eval results and human feedback.

## Current SKILL.md
```markdown
{skill_content}
```

## Eval Results from {iteration_dir.name}
{signals_text}

## Instructions

Based on the failed assertions and human feedback above, suggest specific improvements to the SKILL.md.
Each suggestion should be a single, independent change that can be approved or rejected separately.

Guidelines:
- Generalize from feedback — fixes should address underlying issues, not just patch specific test cases
- Keep the skill lean — fewer, better instructions outperform exhaustive rules
- Explain the why — reasoning-based instructions work better than rigid directives
- If all evals pass and feedback is only about quality, focus on clarity and precision

Respond in this exact JSON format (no markdown fences, no other text):
{{
  "suggestions": [
    {{
      "title": "Short title of the change",
      "reason": "Why this change is needed, referencing specific eval feedback",
      "old_text": "The exact text in SKILL.md to replace (must match exactly, use enough context to be unique)",
      "new_text": "The replacement text"
    }}
  ]
}}

IMPORTANT:
- old_text must be an exact substring of the current SKILL.md
- Each suggestion must be independent — do not assume other suggestions are applied
- If no changes are needed, return {{"suggestions": []}}"""

    print(f"=== Improving: {skill_name} (based on {iteration_dir.name}) ===")
    print(f"Sending {len(eval_signals)} eval signals to Claude...\n")

    result = run_claude(improve_prompt, model=MODEL_EVAL)
    response_text = result.get("result", "")

    if not response_text:
        print(f"Error: No response from Claude. {result.get('error', '')}")
        sys.exit(1)

    # Parse suggestions JSON
    try:
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
        if cleaned.endswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[:-1])
        data = json.loads(cleaned.strip())
        suggestions = data.get("suggestions", [])
    except (json.JSONDecodeError, ValueError):
        print("Error: Could not parse suggestions from Claude.")
        print(f"Raw response:\n{response_text[:500]}")
        # Save raw response for debugging
        suggestion_path = iteration_dir / "improvement_suggestion_raw.md"
        with open(suggestion_path, "w") as f:
            f.write(response_text)
        print(f"Raw response saved to: {suggestion_path}")
        sys.exit(1)

    if not suggestions:
        print("No suggestions — Claude thinks the skill is fine as-is.")
        return

    # Save all suggestions to workspace
    suggestion_path = iteration_dir / "improvement_suggestions.json"
    with open(suggestion_path, "w") as f:
        json.dump(data, f, indent=2)

    # Present each suggestion for approval
    print(f"Claude proposed {len(suggestions)} suggestion(s):\n")
    approved = []
    current_content = skill_content

    for i, s in enumerate(suggestions, 1):
        print(f"{'='*60}")
        print(f"Suggestion {i}/{len(suggestions)}: {s['title']}")
        print(f"{'='*60}")
        print(f"Reason: {s['reason']}\n")
        print(f"--- REMOVE ---")
        print(s["old_text"])
        print(f"\n--- REPLACE WITH ---")
        print(s["new_text"])
        print()

        # Check if old_text exists in current content
        if s["old_text"] not in current_content:
            print("[!] Warning: old_text not found in current SKILL.md — skipping.")
            print()
            continue

        while True:
            choice = input(f"Apply this change? [y]es / [n]o / [q]uit: ").strip().lower()
            if choice in ("y", "yes", "n", "no", "q", "quit"):
                break
            print("Please enter y, n, or q.")

        if choice in ("q", "quit"):
            print("\nStopping — no more suggestions will be reviewed.")
            break
        elif choice in ("y", "yes"):
            current_content = current_content.replace(s["old_text"], s["new_text"], 1)
            approved.append(s)
            print("[+] Approved.\n")
        else:
            print("[-] Skipped.\n")

    if not approved:
        print("No suggestions approved. SKILL.md unchanged.")
        return

    # Write updated SKILL.md
    with open(skill_md_path, "w") as f:
        f.write(current_content)

    print(f"\n{'='*60}")
    print(f"Applied {len(approved)}/{len(suggestions)} suggestions to skills/{skill_name}/SKILL.md")

    # Save applied changes log
    applied_path = iteration_dir / "applied_suggestions.json"
    with open(applied_path, "w") as f:
        json.dump({"applied": approved}, f, indent=2)

    # Ask to run evals
    print()
    run_now = input("Run evals now to verify? [y/n]: ").strip().lower()
    if run_now in ("y", "yes"):
        print()
        spec = load_eval_spec(skill_name)
        results = run_eval(skill_name, spec)
        print_results(results)


def deploy_skill(skill_name: str):
    """Deploy a skill to the testing folder for manual testing with Claude Code."""
    import shutil

    skill_src = SKILLS_DIR / skill_name
    if not skill_src.exists():
        print(f"Error: Skill '{skill_name}' not found at {skill_src}")
        sys.exit(1)

    skill_md = skill_src / "SKILL.md"
    if not skill_md.exists():
        print(f"Error: No SKILL.md found at {skill_md}")
        sys.exit(1)

    if not DEPLOY_DIR.exists():
        print(f"Error: Deploy directory not found at {DEPLOY_DIR}")
        sys.exit(1)

    # Deploy to .claude/skills/<skill-name>/ for Claude Code discovery
    deploy_skill_dir = DEPLOY_DIR / ".claude" / "skills" / skill_name

    # Show what will be deployed
    files = list(skill_src.rglob("*"))
    files = [f for f in files if f.is_file()]
    print(f"=== Deploying: {skill_name} ===")
    print(f"From: {skill_src}")
    print(f"To:   {deploy_skill_dir}")
    print(f"Files: {len(files)}")
    for f in files:
        print(f"  {f.relative_to(skill_src)}")

    # Clean and copy
    if deploy_skill_dir.exists():
        shutil.rmtree(deploy_skill_dir)
    shutil.copytree(skill_src, deploy_skill_dir)

    print(f"\nDeployed successfully.")
    print(f"To test: cd {DEPLOY_DIR} and use Claude Code with the skill.")


def list_evals():
    """List all available eval specs."""
    eval_dirs = sorted(
        d for d in EVALS_DIR.iterdir()
        if d.is_dir() and (d / "evals.json").exists()
    )
    if not eval_dirs:
        print("No eval specs found. Create one in evals/<skill-name>/evals.json")
        return
    print("Available evals:")
    for d in eval_dirs:
        spec = load_eval_spec(d.name)
        implemented = "implemented" if check_skill_exists(d.name) else "not implemented"
        num_evals = len(spec.get("evals", []))
        print(f"  {d.name}: {num_evals} evals ({implemented})")


def print_results(results: dict):
    """Print eval results summary."""
    print(f"\n--- Results ---")
    print(f"Workspace: {results['iteration_dir']}")
    for ev in results["evals"]:
        status_str = f"[eval-{ev['id']}] {ev['status']}"
        if "with_skill_pass_rate" in ev:
            if "without_skill_pass_rate" in ev:
                status_str += f"  (with_skill: {ev['with_skill_pass_rate']}, without: {ev['without_skill_pass_rate']})"
            else:
                status_str += f"  (pass_rate: {ev['with_skill_pass_rate']})"
        if "reason" in ev:
            status_str += f"  ({ev['reason']})"
        print(f"  {status_str}")


def main():
    parser = argparse.ArgumentParser(description="Run skill evaluations")
    parser.add_argument("skill", nargs="?", help="Skill name to evaluate")
    parser.add_argument("--all", action="store_true", help="Run all evals")
    parser.add_argument("--list", action="store_true", help="List available evals")
    parser.add_argument("--improve", action="store_true", help="Suggest SKILL.md improvements from latest iteration feedback")
    parser.add_argument("--deploy", action="store_true", help="Deploy skill to testing folder for manual testing")
    parser.add_argument("--baseline", action="store_true", help="Also run without_skill baseline for comparison (skipped by default)")
    parser.add_argument("--eval", type=str, help="Run specific eval IDs only (comma-separated, e.g. --eval 1,2,3)")
    args = parser.parse_args()

    if args.list:
        list_evals()
        return

    if args.deploy:
        if not args.skill:
            print("Error: --deploy requires a skill name")
            sys.exit(1)
        deploy_skill(args.skill)
        return

    if args.improve:
        if not args.skill:
            print("Error: --improve requires a skill name")
            sys.exit(1)
        improve_skill(args.skill)
        return

    if args.all:
        eval_dirs = sorted(
            d.name for d in EVALS_DIR.iterdir()
            if d.is_dir() and (d / "evals.json").exists()
        )
        if not eval_dirs:
            print("No eval specs found.")
            return
        for skill_name in eval_dirs:
            print(f"\n=== {skill_name} ===")
            spec = load_eval_spec(skill_name)
            results = run_eval(skill_name, spec)
            print_results(results)
        return

    if not args.skill:
        parser.print_help()
        sys.exit(1)

    spec = load_eval_spec(args.skill)

    errors = validate_eval_spec(spec)
    if errors:
        print(f"Invalid eval spec for '{args.skill}':")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # Filter to specific eval IDs if requested
    if args.eval:
        eval_ids = set(int(x.strip()) for x in args.eval.split(","))
        spec["evals"] = [ev for ev in spec["evals"] if ev["id"] in eval_ids]
        if not spec["evals"]:
            print(f"Error: No evals found with IDs {eval_ids}")
            sys.exit(1)

    print(f"=== Evaluating: {args.skill} ===")
    print(f"Evals: {len(spec['evals'])}" + (f" (IDs: {args.eval})" if args.eval else ""))
    results = run_eval(args.skill, spec, run_baseline=args.baseline)
    print_results(results)


if __name__ == "__main__":
    main()
