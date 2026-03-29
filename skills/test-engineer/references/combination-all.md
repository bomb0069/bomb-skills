# Combination Method: All Combinations

Generate every possible combination of partition values across all conditions.

## All-EP: Combined Partition Diagram

**When all conditions are EP type**, show a combined partition diagram **before** the test scenarios table. Each overlap zone is a test case.

```
Combined Partitions: {Condition A} × {Condition B} → {Result}

┌────────────────────────────────────────────────┐
│  Universal set                                 │
│    ┌─ {A1} ──┐   ┌─ {A2} ──┐                  │
│  ┌─┼─────────┼───┼─────────┼─┐  {B1}          │
│  │ │ A1+B1   │   │ A2+B1   │ │                │
│  │ │ {result}│   │ {result}│ │                │
│  └─┼─────────┼───┼─────────┼─┘                │
│  ┌─┼─────────┼───┼─────────┼─┐  {B2}          │
│  │ │ A1+B2   │   │ A2+B2   │ │                │
│  │ │ {result}│   │ {result}│ │                │
│  └─┼─────────┼───┼─────────┼─┘                │
│    └─────────┘   └─────────┘                   │
│  INVALID: [{special cases}]                    │
└────────────────────────────────────────────────┘
```

Steps:
1. **Build the combined partition diagram** — show every valid partition intersection across all conditions
2. **Each overlap zone = one test case** — every combination of one valid value from each condition
3. **Add invalid partitions** — one case per invalid partition per condition (other conditions at a valid value)
4. **Derive test scenarios table from the diagram** — overlap zones map directly to rows in the TS table

## Mixed Conditions: Decision Matrix

**When conditions include BVA or STT**, show a decision matrix (checkmark table) summarising all combinations **before** the detailed test scenarios table.

```
| Scenario | {Condition A} valid? | {Condition B} valid? | Expected |
|----------|---------------------|---------------------|----------|
| TS-01    | ✓                   | ✓                   | Pass     |
| TS-02    | ✗                   | ✓                   | Fail     |
| TS-03    | ✓                   | ✗                   | Fail     |
| TS-04    | ✗                   | ✗                   | Fail     |
```

Then generate the full test scenarios table with actual input values for each row.

## Rules
- ID prefix: `TS-01`, `TS-02`
- Follow the **Test Scenarios Table Format** in [references/common.md](common.md): business-readable column headers, condition sub-columns split into select value + parameter, Business Scenario narrative, and Covers traceability column
- Combine ALL business test data including **both valid and invalid values** — some pass, some fail
- Label: **"Test Scenarios (all combinations — for acceptance/integration testing)"**
