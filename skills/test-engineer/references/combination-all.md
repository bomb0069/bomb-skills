# Combination Method: All Combinations

Generate every possible combination of business test data values across all conditions.

If condition A has N values and condition B has M values → N×M scenarios.

## Rules
- ID prefix: `TS-01`, `TS-02`
- Table has `Input:` columns for ALL applicable conditions
- Combine ALL business test data including **both valid and invalid values** — some pass, some fail
- Label: **"Test Scenarios (all combinations — for acceptance/integration testing)"**
- Description: explain business meaning and why it passes or fails
