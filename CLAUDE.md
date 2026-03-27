# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

bomb-skills — AI Agent Skills following the [Agent Skills Specification](https://agentskills.io/specification). Uses a TDD workflow: write evaluations first, then implement skills.

## Build & Development

```bash
# Run evals for a specific skill
python evals/run_evals.py <skill-name>

# Run all evals
python evals/run_evals.py --all

# List available evals
python evals/run_evals.py --list

# Create a new skill (TDD workflow)
cp -r template/skill skills/<skill-name>
cp -r template/eval evals/<skill-name>
```

## Architecture

```
bomb-skills/
├── skills/           # Individual skills (agentskills.io spec)
├── evals/            # TDD-style evaluations (written BEFORE skills)
│   └── run_evals.py  # Eval runner
├── template/         # Starter templates
│   ├── skill/        # Skill template (SKILL.md)
│   └── eval/         # Eval template (eval.yaml)
└── CLAUDE.md
```

### Key Design Decisions

- **TDD-first**: Always write `evals/<skill-name>/eval.yaml` before implementing the skill
- **agentskills.io spec**: Each skill's directory name must match its SKILL.md `name` field
- **Progressive disclosure**: SKILL.md body < 500 lines; split into references/, scripts/, assets/ as needed
- **Eval-driven development**: Evals define expected behavior as scenarios with prompts and expected outcomes

### Skill Structure (agentskills.io spec)

Every skill directory must contain:
- `SKILL.md` (required) — YAML frontmatter with `name` + `description`, then markdown instructions
- `scripts/` (optional) — Executable helper scripts
- `references/` (optional) — Additional documentation
- `assets/` (optional) — Templates, images, data files

### Workflow

1. Write eval spec in `evals/<skill-name>/eval.yaml`
2. Run evals — they should fail/skip (skill not yet implemented)
3. Implement skill in `skills/<skill-name>/`
4. Run evals — they should pass
