# Gap Analysis: Hidden Requirements Detection

After generating combined test scenarios, analyze calculated output values to detect missing (hidden) requirements — conditions that were never stated but are implied by the business context.

## When to Apply

Apply gap analysis **after Step 5 (Combined Test Scenarios)** when the requirement includes a **calculated output** — any output field whose value is derived from a formula combining two or more conditions.

Examples:
- New price = base price + (base price × bonus rate)
- Final premium = base premium × (1 + risk rate)
- Total = quantity × unit price
- Score = raw score × weight factor

## Step 1: Calculate Outputs for Each Scenario

For each row in the Test Scenarios table, compute the output value using the stated formula. Use representative values (boundary values for BVA conditions, one sample per EP partition).

## Step 2: Detect Gap Types

For each calculated output, check against all stated output conditions:

### Precision Gap
Result has more decimal places than the output field type allows.
- Example: price must be integer, but base 333 × rate 10% = 333.3 → new price 366.3 ❌
- Signals a missing **rounding rule**

### Range Gap
Result falls outside the valid range of the output field.
- Example: new price = base 50000 + 20% = 60000, but max price = 50000 ❌
- Signals a missing **cap, reject, or override rule**

### Business Format Gap
Result does not fit an expected business format (unstated but implied).
- Example: price result is 12,590.75 — in this domain prices are always whole baht ❌
- Signals a missing **formatting or rounding convention**

## Step 3: Flag and Ask

When a gap is found, show a warning block:

```
⚠️ Requirement Gap Detected

Scenario TS-XX: {formula} = {calculated value}
This result is {gap description} (output condition: {output field constraint}).

This suggests a hidden rule is missing from the requirement.
```

Then ask via `AskUserQuestion`:
- **Header**: `Hidden Requirement: {output field name}`
- **Question**: `How should the system handle {gap description}?`
- **Options** based on gap type:

| Gap type | Suggested options |
|---|---|
| Precision gap (decimal → integer) | "Round up (ceiling) — e.g. 366.3 → 367", "Round down (floor) — e.g. 366.3 → 366", "Round to nearest — e.g. 366.5 → 367", "Truncate — e.g. 366.3 → 366" |
| Range gap (exceeds max) | "Cap at maximum — clamp result to max", "Reject the transaction — result is invalid", "Apply different formula for edge case" |
| Range gap (below min) | "Use minimum value — floor at min", "Reject the transaction — result is invalid" |
| Business format gap | Describe domain-specific options (e.g. round to nearest 100, nearest 10, etc.) |

## Step 4: Add Hidden Condition and Update Test Scenarios

After the user responds:
1. Add the hidden rule as a new condition in the **Input Analysis** section (label it `[Hidden]`)
2. **Regenerate the Test Scenarios table** with two output columns to make the gap visible:
   - `Calculated: {output field name}` — the raw formula result (before the hidden rule)
   - `Expected: {output field name}` — the adjusted value after applying the hidden rule
3. Add a short note in the Description column explaining the applied rule

**Table template with before/after columns (example: New Price):**

| ID | Name | Description | Input: Base Price | Input: Bonus Rate | Calculated: New Price | Expected: New Price | Result |
|---|---|---|---|---|---|---|---|
| TS-01 | Normal case | Base 333, rate 10%. Raw 366.3 → ceiling 367. | 333 | 10% | 366.3 | 367 | Valid - accepted |
| TS-02 | Whole number case | Base 300, rate 10%. No rounding needed. | 300 | 10% | 330.0 | 330 | Valid - accepted |
| TS-03 | Exceeds max | Base 50000, rate 20%. Raw 60000 exceeds max 50000. | 50000 | 20% | 60000.0 | — | Invalid - rejected |

Rules for the two-column output:
- Always show the **raw calculated value** in `Calculated: {name}` — even when it is already a whole number — so the tester can verify the formula
- Show the **adjusted value** in `Expected: {name}` — this is what the system must produce
- When both values are identical (no rounding needed), show them both anyway for consistency
- When the result is invalid/rejected, show `—` in `Expected: {name}` (no output produced)
- The `Result` column (Valid/Invalid) is based on the **Expected** value, not the Calculated value

The hidden condition becomes a permanent part of the test suite — future test cases should also respect it.
