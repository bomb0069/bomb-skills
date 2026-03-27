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
│   │   ├── eval.yaml      # Eval scenarios and expected outcomes
│   │   └── cases/         # Test case files
│   └── run_evals.py       # Eval runner
├── template/         # Starter templates for new skills + evals
├── CLAUDE.md         # Claude Code project instructions
└── README.md
```

## Workflow (TDD-style)

1. **Define** — Write the skill's eval spec in `evals/<skill-name>/eval.yaml`
2. **Evaluate** — Run evals to confirm they fail (no implementation yet)
3. **Implement** — Build the skill in `skills/<skill-name>/`
4. **Validate** — Run evals again to confirm they pass

## Creating a New Skill

```bash
# 1. Copy templates
cp -r template/skill skills/<skill-name>
cp -r template/eval evals/<skill-name>

# 2. Edit the eval spec first (TDD)
# Define expected behavior in evals/<skill-name>/eval.yaml

# 3. Implement the skill
# Edit skills/<skill-name>/SKILL.md and add supporting files

# 4. Run evals
python evals/run_evals.py <skill-name>
```

## Skill Specification

Each skill follows the [Agent Skills Specification](https://agentskills.io/specification):

- **`SKILL.md`** is the only required file
- YAML frontmatter must include `name` and `description`
- Directory name must match the `name` field
- Names: lowercase alphanumeric + hyphens, no leading/trailing/consecutive hyphens
- Progressive disclosure: metadata → instructions → resources

## References

- [Agent Skills Specification](https://agentskills.io/specification)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
