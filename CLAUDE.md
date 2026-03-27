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
```

## Architecture

```
bomb-skills/
├── skills/           # Individual skills (agentskills.io spec)
├── evals/            # Eval specs (agentskills.io JSON format)
│   ├── <skill-name>/evals.json
│   └── run_evals.py
├── <skill-name>-workspace/  # Eval results per iteration
├── template/         # Starter templates
└── CLAUDE.md
```

### Key Design Decisions

- **TDD-first**: Always write `evals/<skill-name>/evals.json` before implementing the skill
- **agentskills.io eval format**: JSON with `id`, `prompt`, `expected_output`, `assertions`
- **Workspace results**: `grading.json`, `timing.json`, `benchmark.json`, `feedback.json`
- **Progressive disclosure**: SKILL.md body < 500 lines; split into references/, scripts/, assets/

### Workflow

1. Write eval spec in `evals/<skill-name>/evals.json`
2. Run evals — they should fail/skip (skill not yet implemented)
3. Implement skill in `skills/<skill-name>/`
4. Run evals — they should pass
