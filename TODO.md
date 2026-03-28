# TODO — bomb-skills

## test-engineer skill

### In Progress
- [ ] Restructure workflow: per-condition BVA loop → combined test scenarios decision table

### Future
- [ ] Decision table method: add pairwise combination option to reduce scenario count for 3+ conditions
- [ ] Decision table method: add business-driven selection (pick only realistic/important combinations based on context)
- [ ] Export to spreadsheet (CSV/XLSX) with grouped column headers (Input: prefix → merged header)
- [ ] Run full eval suite on git push (CI integration)

## Eval Runner
- [ ] Fix AskUserQuestion tool-call output capture in `claude -p` mode (text before tool call gets swallowed)
