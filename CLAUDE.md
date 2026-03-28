# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

bomb-skills — AI Agent Skills following the [Agent Skills Specification](https://agentskills.io/specification). Uses a TDD workflow: write evaluations first, then implement skills.

## Build & Development

```bash
# Run evals for a specific skill
python3 evals/run_evals.py <skill-name>

# Run all evals
python3 evals/run_evals.py --all

# List available evals
python3 evals/run_evals.py --list

# Suggest SKILL.md improvements from human feedback
python3 evals/run_evals.py <skill-name> --improve

# Deploy skill to testing folder for manual testing with Claude Code
python3 evals/run_evals.py <skill-name> --deploy
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
- **agentskills.io eval format**: JSON with `id`, `prompt`, `expected_output`, `assertions` — this is the project standard, do NOT change to typed assertions (Promptfoo-style) or rename fields to `expectations` (Anthropic skill-creator style)
- **Assertions are natural language strings** graded by Claude (LLM-as-judge). Do NOT add assertion types, weights, or thresholds
- **Multi-turn evals**: Use optional `turns` array with `respond` and `assertions` per turn. Uses `claude -p --resume <session_id>` to continue sessions
- **Workspace results**: `grading.json`, `timing.json`, `benchmark.json`, `feedback.json`
- **Progressive disclosure**: SKILL.md body < 500 lines; split into references/, scripts/, assets/
- **Reference specs**: [agentskills.io specification](https://agentskills.io/specification), [agentskills.io evaluating skills](https://agentskills.io/skill-creation/evaluating-skills)

### Development Workflow

Every feature follows this TDD cycle. **Always commit after evals pass.**

#### New Skill
1. Write eval spec in `evals/<skill-name>/evals.json`
2. Run evals — they should fail/skip (skill not yet implemented)
3. Implement skill in `skills/<skill-name>/`
4. Run evals — they should all pass
5. **Commit** the eval spec, skill, and any supporting files

#### Adding a Feature to an Existing Skill
1. Add new eval cases (or update existing assertions) in `evals/<skill-name>/evals.json`
2. Run evals — new cases should fail, existing cases should still pass
3. Update `skills/<skill-name>/SKILL.md` (and supporting files) to implement the feature
4. Run evals — all cases (new and existing) should pass
5. **Commit** the updated eval spec and skill together

#### Improving a Skill via Feedback
1. Run evals: `python3 evals/run_evals.py <skill-name>`
2. Review outputs in `<skill-name>-workspace/iteration-N/eval-*/with_skill/outputs/`
3. Edit `<skill-name>-workspace/iteration-N/feedback.json` with specific comments per eval
4. Run `python3 evals/run_evals.py <skill-name> --improve` to get Claude's suggestions
5. Apply changes to SKILL.md, run evals, commit

#### Deploy & Manual Testing
1. Evals must pass before deploying
2. Deploy: `python3 evals/run_evals.py <skill-name> --deploy`
3. Copies skill to `../deploy-<project-folder-name>/.claude/skills/<skill-name>/`
4. Open Claude Code in the deploy folder to test the skill interactively
5. After testing, capture any issues as feedback or new eval cases back in this project

#### Rules
- Never commit a feature without running evals first
- Eval results must show all assertions passing before committing
- Each commit should include both the eval changes and the skill changes for that feature
- Every commit must include the `chats/` folder — always `git add chats/` when staging
- Workspace results (`*-workspace/`) are generated artifacts — do not commit them
- Do NOT push to remote automatically — the creator will push manually when ready
