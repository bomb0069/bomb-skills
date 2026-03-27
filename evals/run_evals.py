#!/usr/bin/env python3
"""
Eval runner for bomb-skills.

Follows the agentskills.io eval format:
- Evals defined in evals/<skill-name>/evals.json
- Results stored in <skill-name>-workspace/iteration-N/
- Outputs: grading.json, timing.json, benchmark.json, feedback.json

Usage:
    python evals/run_evals.py <skill-name>       # Run evals for one skill
    python evals/run_evals.py --all               # Run all evals
    python evals/run_evals.py --list              # List available evals
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

EVALS_DIR = Path(__file__).parent
PROJECT_DIR = EVALS_DIR.parent
SKILLS_DIR = PROJECT_DIR / "skills"


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


def create_workspace_structure(skill_name: str, spec: dict) -> Path:
    """Create workspace directory structure for an eval iteration."""
    workspace_dir = PROJECT_DIR / f"{skill_name}-workspace"
    iteration = get_next_iteration(workspace_dir)
    iteration_dir = workspace_dir / f"iteration-{iteration}"

    for ev in spec["evals"]:
        eval_name = f"eval-{ev['id']}"
        for variant in ["with_skill", "without_skill"]:
            outputs_dir = iteration_dir / eval_name / variant / "outputs"
            outputs_dir.mkdir(parents=True, exist_ok=True)

    return iteration_dir


def run_eval(skill_name: str, spec: dict) -> dict:
    """Run evaluations for a skill. Returns results dict."""
    skill_exists = check_skill_exists(skill_name)
    iteration_dir = create_workspace_structure(skill_name, spec)

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

            # Write timing (zero — not run)
            timing = {"total_tokens": 0, "duration_ms": 0}
            with open(eval_dir / "timing.json", "w") as f:
                json.dump(timing, f, indent=2)

            # Write grading (all skipped)
            grading = {
                "assertion_results": [
                    {
                        "text": assertion,
                        "passed": False,
                        "evidence": "Skill not yet implemented",
                    }
                    for assertion in ev.get("assertions", [])
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

        # Write benchmark
        benchmark = {
            "run_summary": {
                "with_skill": {
                    "pass_rate": {"mean": 0.0},
                    "time_seconds": {"mean": 0.0},
                    "tokens": {"mean": 0},
                },
                "without_skill": {
                    "pass_rate": {"mean": 0.0},
                    "time_seconds": {"mean": 0.0},
                    "tokens": {"mean": 0},
                },
                "delta": {
                    "pass_rate": 0.0,
                    "time_seconds": 0.0,
                    "tokens": 0,
                },
            }
        }
        with open(iteration_dir / "benchmark.json", "w") as f:
            json.dump(benchmark, f, indent=2)

        # Write empty feedback
        feedback = {f"eval-{ev['id']}": "" for ev in spec["evals"]}
        with open(iteration_dir / "feedback.json", "w") as f:
            json.dump(feedback, f, indent=2)

        return results

    # When skill exists, run each eval
    for ev in spec["evals"]:
        eval_name = f"eval-{ev['id']}"
        print(f"  Running eval {ev['id']}: {ev.get('expected_output', '')[:60]}...")

        # TODO: Integrate with Claude API or agent framework to actually
        # execute the prompt against the skill and check expected outcomes.
        # For now, create placeholder result files for manual review.
        for variant in ["with_skill", "without_skill"]:
            eval_dir = iteration_dir / eval_name / variant

            timing = {"total_tokens": 0, "duration_ms": 0}
            with open(eval_dir / "timing.json", "w") as f:
                json.dump(timing, f, indent=2)

            grading = {
                "assertion_results": [
                    {
                        "text": assertion,
                        "passed": None,
                        "evidence": "Pending manual review",
                    }
                    for assertion in ev.get("assertions", [])
                ],
                "summary": {
                    "passed": 0,
                    "failed": 0,
                    "total": len(ev.get("assertions", [])),
                    "pass_rate": None,
                },
            }
            with open(eval_dir / "grading.json", "w") as f:
                json.dump(grading, f, indent=2)

        results["evals"].append({
            "id": ev["id"],
            "status": "pending_review",
        })

    # Write benchmark placeholder
    benchmark = {
        "run_summary": {
            "with_skill": {
                "pass_rate": {"mean": None},
                "time_seconds": {"mean": None},
                "tokens": {"mean": None},
            },
            "without_skill": {
                "pass_rate": {"mean": None},
                "time_seconds": {"mean": None},
                "tokens": {"mean": None},
            },
            "delta": {
                "pass_rate": None,
                "time_seconds": None,
                "tokens": None,
            },
        }
    }
    with open(iteration_dir / "benchmark.json", "w") as f:
        json.dump(benchmark, f, indent=2)

    feedback = {f"eval-{ev['id']}": "" for ev in spec["evals"]}
    with open(iteration_dir / "feedback.json", "w") as f:
        json.dump(feedback, f, indent=2)

    return results


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


def main():
    parser = argparse.ArgumentParser(description="Run skill evaluations")
    parser.add_argument("skill", nargs="?", help="Skill name to evaluate")
    parser.add_argument("--all", action="store_true", help="Run all evals")
    parser.add_argument("--list", action="store_true", help="List available evals")
    args = parser.parse_args()

    if args.list:
        list_evals()
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

    print(f"=== Evaluating: {args.skill} ===")
    print(f"Evals: {len(spec['evals'])}")
    results = run_eval(args.skill, spec)
    print_results(results)


def print_results(results: dict):
    """Print eval results summary."""
    print(f"\n--- Results ---")
    print(f"Workspace: {results['iteration_dir']}")
    for ev in results["evals"]:
        print(f"  [eval-{ev['id']}] {ev['status']}")
        if "reason" in ev:
            print(f"    reason: {ev['reason']}")


if __name__ == "__main__":
    main()
