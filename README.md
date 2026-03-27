# bomb-skills

AI Agent Skills project following the [Agent Skills Specification](https://agentskills.io/specification).

## Project Structure

```
bomb-skills/
├── skills/           # Individual skills (each follows agentskills.io spec)
│   └── <skill-name>/
│       ├── SKILL.md       # Required: metadata + instructions
│       ├── scripts/       # Optional: executable code
│       ├── references/    # Optional: documentation
│       └── assets/        # Optional: templates, resources
├── evals/            # TDD-style evaluations (written before implementation)
│   ├── <skill-name>/
│   │   └── evals.json     # Eval cases (agentskills.io format)
│   └── run_evals.py       # Eval runner
├── <skill-name>-workspace/  # Eval results (auto-generated)
│   └── iteration-N/
│       ├── eval-<id>/
│       │   ├── with_skill/    # grading.json, timing.json, outputs/
│       │   └── without_skill/ # grading.json, timing.json, outputs/
│       ├── benchmark.json
│       └── feedback.json
├── template/         # Starter templates
├── CLAUDE.md
└── README.md
```

## Workflow (TDD-style)

1. **Define** — Write eval cases in `evals/<skill-name>/evals.json`
2. **Evaluate** — Run evals to confirm they fail (no implementation yet)
3. **Implement** — Build the skill in `skills/<skill-name>/`
4. **Validate** — Run evals again to confirm they pass

## Creating a New Skill

```bash
# 1. Copy templates
cp -r template/skill skills/<skill-name>
cp -r template/eval evals/<skill-name>

# 2. Edit the eval spec first (TDD)
# Define expected behavior in evals/<skill-name>/evals.json

# 3. Run evals (should skip — no implementation)
python evals/run_evals.py <skill-name>

# 4. Implement the skill
# Edit skills/<skill-name>/SKILL.md

# 5. Run evals again (should pass)
python evals/run_evals.py <skill-name>
```

## References

- [Agent Skills Specification](https://agentskills.io/specification)
- [Evaluating Skills](https://agentskills.io/skill-creation/evaluating-skills)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
