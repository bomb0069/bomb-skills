# Combination Method: Sequential (Short-Circuit)

Follow the business validation order. If an earlier condition fails, stop — don't test later conditions for that scenario.

## Flowchart Diagram

Show a flowchart before the table:
```
Sequential Validation: {Condition1} → {Condition2} → ...

                ┌──────────┐
                │  Input   │
                └────┬─────┘
                     │
                ┌────▼─────┐
                │  Check   │──FAIL──► ✗ Rejected
                │ {Cond1}  │          ({reason})
                └────┬─────┘
                   PASS
                     │
                ┌────▼─────┐
                │  Check   │──FAIL──► ✗ Rejected
                │ {Cond2}  │          ({reason})
                └────┬─────┘
                   PASS
                     │
                ┌────▼─────┐
                │ Accepted │
                └──────────┘
```

## Rules
- For each invalid value of condition 1: ONE scenario (fails at step 1, other fields use nominal)
- For valid condition 1 × invalid condition 2: scenarios (passes step 1, fails at step 2)
- Continue until all conditions pass (happy path)
- Add "Fails At" column to show which step rejected
- Label: **"Test Scenarios (sequential — for acceptance/integration testing)"**

## Validation Order

Ask user to confirm the validation order using `AskUserQuestion` with header "Order":
- Suggest 2-3 possible orders based on business domain
- Put recommended order first with "(Recommended)" label
- Explain why each order makes business sense
- Examples:
  - File upload: "Type → Size (Recommended)" (check format before processing large files)
  - Loan: "Age → Income → Credit (Recommended)" (cheapest checks first)
