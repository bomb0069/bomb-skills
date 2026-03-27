#!/usr/bin/env python3
"""
Eval runner for bomb-skills.

Loads eval specs from evals/<skill-name>/eval.yaml and runs them
against the corresponding skill in skills/<skill-name>/.

Usage:
    python evals/run_evals.py <skill-name>       # Run evals for one skill
    python evals/run_evals.py --all               # Run all evals
    python evals/run_evals.py --list              # List available evals
"""

import argparse
import sys
import yaml
from pathlib import Path

EVALS_DIR = Path(__file__).parent
SKILLS_DIR = EVALS_DIR.parent / "skills"
RESULTS_DIR = EVALS_DIR / "results"


def load_eval_spec(skill_name: str) -> dict:
    """Load the eval.yaml for a given skill."""
    eval_file = EVALS_DIR / skill_name / "eval.yaml"
    if not eval_file.exists():
        print(f"Error: No eval spec found at {eval_file}")
        sys.exit(1)
    with open(eval_file) as f:
        return yaml.safe_load(f)


def check_skill_exists(skill_name: str) -> bool:
    """Check if the skill implementation exists."""
    skill_dir = SKILLS_DIR / skill_name
    skill_md = skill_dir / "SKILL.md"
    return skill_dir.exists() and skill_md.exists()


def validate_eval_spec(spec: dict) -> list[str]:
    """Validate an eval spec and return any errors."""
    errors = []
    if "skill" not in spec:
        errors.append("Missing 'skill' field")
    if "scenarios" not in spec:
        errors.append("Missing 'scenarios' field")
    elif not isinstance(spec["scenarios"], list):
        errors.append("'scenarios' must be a list")
    else:
        for i, scenario in enumerate(spec["scenarios"]):
            if "name" not in scenario:
                errors.append(f"Scenario {i}: missing 'name'")
            if "prompt" not in scenario:
                errors.append(f"Scenario {i}: missing 'prompt'")
            if "expected" not in scenario:
                errors.append(f"Scenario {i}: missing 'expected'")
    return errors


def run_eval(skill_name: str, spec: dict) -> dict:
    """Run evaluations for a skill. Returns results dict."""
    results = {
        "skill": skill_name,
        "skill_exists": check_skill_exists(skill_name),
        "scenarios": [],
    }

    if not results["skill_exists"]:
        print(f"  Skill '{skill_name}' not yet implemented (TDD: this is expected)")
        for scenario in spec.get("scenarios", []):
            results["scenarios"].append({
                "name": scenario["name"],
                "status": "skipped",
                "reason": "skill not implemented",
            })
        return results

    # When skill exists, run each scenario
    for scenario in spec.get("scenarios", []):
        print(f"  Running: {scenario['name']}...")
        # TODO: Integrate with Claude API or agent framework to actually
        # execute the prompt against the skill and check expected outcomes.
        # For now, mark as pending manual review.
        results["scenarios"].append({
            "name": scenario["name"],
            "status": "pending_review",
            "prompt": scenario["prompt"],
            "expected": scenario["expected"],
        })

    return results


def list_evals():
    """List all available eval specs."""
    eval_dirs = sorted(
        d for d in EVALS_DIR.iterdir()
        if d.is_dir() and (d / "eval.yaml").exists()
    )
    if not eval_dirs:
        print("No eval specs found. Create one in evals/<skill-name>/eval.yaml")
        return
    print("Available evals:")
    for d in eval_dirs:
        spec = load_eval_spec(d.name)
        implemented = "implemented" if check_skill_exists(d.name) else "not implemented"
        scenarios = len(spec.get("scenarios", []))
        print(f"  {d.name}: {scenarios} scenarios ({implemented})")


def main():
    parser = argparse.ArgumentParser(description="Run skill evaluations")
    parser.add_argument("skill", nargs="?", help="Skill name to evaluate")
    parser.add_argument("--all", action="store_true", help="Run all evals")
    parser.add_argument("--list", action="store_true", help="List available evals")
    parser.add_argument("--tags", nargs="+", help="Filter scenarios by tags")
    args = parser.parse_args()

    if args.list:
        list_evals()
        return

    if args.all:
        eval_dirs = sorted(
            d.name for d in EVALS_DIR.iterdir()
            if d.is_dir() and (d / "eval.yaml").exists()
        )
        if not eval_dirs:
            print("No eval specs found.")
            return
        for skill_name in eval_dirs:
            print(f"\n=== {skill_name} ===")
            spec = load_eval_spec(skill_name)
            run_eval(skill_name, spec)
        return

    if not args.skill:
        parser.print_help()
        sys.exit(1)

    spec = load_eval_spec(args.skill)

    # Validate the spec
    errors = validate_eval_spec(spec)
    if errors:
        print(f"Invalid eval spec for '{args.skill}':")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"=== Evaluating: {args.skill} ===")
    scenarios = spec.get("scenarios", [])

    # Filter by tags if specified
    if args.tags:
        tag_set = set(args.tags)
        scenarios = [s for s in scenarios if tag_set & set(s.get("tags", []))]
        spec["scenarios"] = scenarios

    print(f"Scenarios: {len(scenarios)}")
    results = run_eval(args.skill, spec)

    # Summary
    print(f"\n--- Results ---")
    for s in results["scenarios"]:
        print(f"  [{s['status']}] {s['name']}")


if __name__ == "__main__":
    main()
