# Combination Method: Pairwise

Ensure every pair of values from any two conditions appears in at least one scenario. Much fewer rows than all combinations while covering important interactions.

Example: A(5) × B(4) × C(3) → ~15-20 instead of 60.

## Rules
- ID prefix: `TS-01`, `TS-02`
- Ensure all pairs: (a1,b1), (a1,b2), (a2,b1), etc. AND (a1,c1), etc. AND (b1,c1), etc.
- Use algorithm or manual selection to minimize rows
- Include both valid and invalid values
- Follow the **Test Scenarios Table Format** in [references/common.md](common.md): business-readable column headers, condition sub-columns split into select value + parameter, Business Scenario narrative, and Covers traceability column
- Label: **"Test Scenarios (pairwise — for acceptance/integration testing)"**
