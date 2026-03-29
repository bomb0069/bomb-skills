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

## Step 4: Add Hidden Condition and Update

After the user responds:
1. Add the hidden rule as a new condition in the **Input Analysis** section (label it `[Hidden]`)
2. Update the affected test case rows with corrected expected output values
3. Add a note explaining the applied rule (e.g. "New price 366.3 → 367 (ceiling)")

The hidden condition becomes a permanent part of the test suite — future test cases should also respect it.
