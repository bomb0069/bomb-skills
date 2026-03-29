# TODO — bomb-skills

## test-engineer skill

### In Progress
- [x] Restructure workflow: per-condition BVA loop → combined test scenarios decision table
  - Moved AskUserQuestion (combination method) to Step 2, before per-condition loop
  - Fixed sequential nominal value rule (explicit: never vary conditions after failure point)
  - Fixed sequential validation order: text presentation of 2-3 orders instead of AskUserQuestion
  - Evals 19, 22, 23, 24 targeted; full eval run pending (usage limit resets Mar 31)

### Future
- [ ] Decision table method: add pairwise combination option to reduce scenario count for 3+ conditions
- [ ] Decision table method: add business-driven selection (pick only realistic/important combinations based on context)
- [ ] Export to spreadsheet (CSV/XLSX) with grouped column headers (Input: prefix → merged header)
- [ ] Run full eval suite on git push (CI integration)

## Eval Runner
- [ ] Fix AskUserQuestion tool-call output capture in `claude -p` mode (text before tool call gets swallowed)
