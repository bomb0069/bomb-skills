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

For each calculated output, check against **two groups** of conditions:
- **Output conditions** — constraints explicitly stated for the output field (type, range, format)
- **Existing input conditions** — constraints stated for any input field that shares the same domain as the output (e.g., new price sharing the same range as base price)

### Precision Gap
Result has more decimal places than the output field type allows.
- Example: price must be integer, but base 333 × rate 10% = 333.3 → new price 366.3 ❌
- Signals a missing **rounding rule**

### Range Gap — Output Condition Violated
Result falls outside the valid range stated for the output field itself.
- Example: new price has its own stated max 55,000, but result = 60,000 ❌
- Signals a missing **cap, reject, or override rule** specific to the output field

### Condition Conflict Gap *(secondary)*
Result violates the range of an **existing input condition** — the output re-enters the same value domain as an input but exceeds its bounds.
- Example: base price max = 50,000; new price (same domain: Thai Baht price) = 60,000 ❌ — the output conflicts with the input condition's ceiling
- This is a **secondary hidden requirement**: the two conditions are using the same domain but the formula breaks the shared boundary
- Signals a missing **business rule** for how the system resolves this conflict

### Business Format Gap
Result does not fit an expected business format (unstated but implied).
- Example: price result is 12,590.75 — in this domain prices are always whole baht ❌
- Signals a missing **formatting or rounding convention**

## Step 3: Flag and Ask with Business Suggestions

### Standard gaps (Precision, Range, Format)

Show a warning block:

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

### Condition Conflict Gap — business-context-aware suggestions

Show an expanded warning that names the conflicting condition explicitly:

```
⚠️ Condition Conflict Detected

Scenario TS-XX: {formula} = {calculated value}
This result conflicts with the existing condition "{conflicting condition name}" ({conflicting range/constraint}).

The output shares the same domain as {conflicting field} but the formula can produce a value outside its bounds.
This means the requirement is incomplete — a business rule must decide which condition wins.
```

Then ask via `AskUserQuestion`:
- **Header**: `Condition Conflict: {output field} vs {conflicting field}`
- **Question**: `When {formula} produces {calculated value} which exceeds {conflicting condition}, what should the business do?`
- **Options** — generate based on the domain context; always include at least these patterns:

| Business pattern | Suggested option text |
|---|---|
| Separate ceiling for output | "Allow {output} to exceed {conflicting max} — the output has its own higher limit (ask for the new max)" |
| Clamp to shared max | "Cap {output} at {conflicting max} — the output must stay within the same bounds as {conflicting field}" |
| Block the combination | "Reject this scenario — the input combination that causes the overflow is not a valid business case" |
| Tiered / conditional rule | "Apply a different formula or rate when the result would exceed {conflicting max} (e.g. progressive pricing, rate cap)" |

Always explain **why** each option matters in business terms in the option text — do not just list technical actions.

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
