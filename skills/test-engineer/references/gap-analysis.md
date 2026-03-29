# Gap Analysis: Hidden Requirements Detection

After generating combined test scenarios, analyze calculated output values to detect missing (hidden) requirements — conditions that were never stated but are implied by the business context.

## When to Apply

Apply gap analysis **after Step 5 (Combined Test Scenarios)** when the requirement includes a **calculated output** — any output field whose value is derived from a formula combining two or more conditions.

Examples:
- New price = base price + (base price × bonus rate)
- Final premium = base premium × (1 + risk rate)
- Total = quantity × unit price
- Score = raw score × weight factor

---

## Step 0: Domain Inheritance Check *(before calculating)*

**Before computing any output values**, check whether the output field shares the same type or unit as any input condition.

- Look at the output field name and its unit (e.g., "New Price" → Thai Baht price)
- Compare against each input condition's type/unit (e.g., "Base Price" → Thai Baht price, range 100–50,000)
- If a match is found, the output *may or may not* inherit the input's constraint — this must be confirmed by the user before proceeding

When a domain match is found, show:

```
🔍 Domain Overlap Detected

Output field "{output field}" appears to be the same type as input "{input field}".
"{input field}" has condition: {constraint}

Should "{output field}" inherit the same constraint, or have its own separate rule?
```

Then ask via `AskUserQuestion`:
- **Header**: `Output Constraint: {output field}`
- **Question**: `"{output field}" is the same type as "{input field}" ({constraint}). Does the output inherit this constraint?`
- **Options**:
  - `"Yes — {output field} inherits {input field}'s constraint ({constraint}). The output must stay within the same bounds."`
  - `"No — {output field} has its own separate range (I will specify it)"`
  - `"No — {output field} has no range constraint, only the precision/type rule applies"`

Record the user's answer as the **output condition** before proceeding to Step 1.
If the user confirms inheritance, Step 2 will detect a Condition Conflict whenever the formula breaks those shared bounds.

---

## Step 1: Build the Unified Test Scenarios Table

**All scenarios go in a single table** — do not split by gap type, scenario category, or whether a gap exists.

### Formula Decomposition — one column per step

**Before building the table**, decompose the formula into its atomic steps. Each step becomes its own column using the `Step:` prefix. When rounding is applied at any step, show two adjacent sub-columns: the raw value and the rounded value.

**Decomposition rules:**
1. Start with all `Input:` columns (one per condition)
2. For each arithmetic operation in the formula, add a `Step:` column showing the intermediate result
3. If a rounding or adjustment rule applies to that intermediate result, add a second `Step: Rounded …` column immediately after
4. End with `Calculated: {output}` (the final raw formula result) and `Expected: {output}` (after any final adjustment)

**Example — `New Price = Base Price + (Base Price × Bonus Rate)`:**

Formula breakdown:
- Step A: `Base Price × Bonus Rate` → may be fractional
- Step B: `Rounded (Base Price × Bonus Rate)` → after rounding the adjustment (if a rounding rule was confirmed)
- Final: `New Price = Base Price + Rounded Adjustment`

Resulting columns:

| ID | Name | Description | Input: Base Price | Input: Bonus Rate | Step: Base Price × Bonus Rate | Step: Rounded Adjustment | Calculated: New Price | Expected: New Price | Result |
|---|---|---|---|---|---|---|---|---|---|
| TS-01 | Normal case | Adjustment 33.3 → rounded up to 34. New price 333+34=367. | 333 | 10% | 33.3 | 34 | 367 | 367 | Valid - accepted |
| TS-02 | Whole number | Adjustment 30.0, no rounding needed. New price 300+30=330. | 300 | 10% | 30.0 | 30 | 330 | 330 | Valid - accepted |
| TS-03 | Max base, high rate | Adjustment 10000.0. New price 50000+10000=60000 — conflict. | 50000 | 20% | 10000.0 | 10000 | 60000 | 50000 | Valid - accepted |
| TS-04 | Invalid base | Below minimum base price. | 99 | 10% | 9.9 | — | — | — | Invalid - rejected |

**Column naming convention:**

| Prefix | When to use | Example |
|---|---|---|
| `Input: {field}` | Every input condition | `Input: Base Price` |
| `Step: {expression}` | Each intermediate arithmetic result | `Step: Base Price × Bonus Rate` |
| `Step: Rounded {expression}` | Immediately after a `Step:` that gets rounded | `Step: Rounded Adjustment` |
| `Calculated: {output}` | The raw final formula result (before final adjustment) | `Calculated: New Price` |
| `Expected: {output}` | The final value the system must produce | `Expected: New Price` |

**Rules:**
- Always show `Step:` values even when no rounding occurred — testers must be able to verify each arithmetic step independently
- If the formula has only one operation (e.g., `A × B`), the `Step:` column IS the `Calculated:` column — no need to repeat it
- For rejected rows where an input is already invalid, show `—` from the first invalid step onward
- `Expected:` starts as `?` before gap resolution; fill in after the user answers

Compute values using representative inputs (BVA boundary values, one sample per EP partition).

---
## Step 2: Detect Gap Types

For each `Calculated:` value in the table, check against the output condition confirmed in Step 0:

### Precision Gap
Result has more decimal places than the output field type allows.
- Example: price must be integer, but base 333 × rate 10% = 333.3 → new price 366.3 ❌
- Signals a missing **rounding rule**

### Range Gap — Output Condition Violated
Result falls outside the valid range stated for the output field.
- Example: new price has its own stated max 55,000, but result = 60,000 ❌
- Signals a missing **cap, reject, or override rule**

### Condition Conflict Gap *(when inheritance confirmed in Step 0)*
Result violates the inherited constraint from the input condition.
- Example: user confirmed "New Price inherits Base Price condition 100–50,000"; formula produces 60,000 ❌
- The output shares the domain and bounds of the input — the formula breaks those shared bounds
- Signals a missing **business rule** for how the system resolves this conflict

### Business Format Gap
Result does not fit an expected business format (unstated but implied).
- Example: price result is 12,590.75 — in this domain prices are always whole baht ❌
- Signals a missing **formatting or rounding convention**

---

## Step 3: Flag and Ask with Business Suggestions

Mark the conflicting rows in the table (annotate the `Calculated:` cell or add a flag emoji) then show the appropriate warning block below the table.

### Standard gaps (Precision, Range, Format)

```
⚠️ Requirement Gap Detected

Rows: TS-XX, TS-YY
{formula} = {calculated value} — {gap description} (output condition: {output field constraint}).

This suggests a hidden rule is missing from the requirement.
```

Ask via `AskUserQuestion`:
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

```
⚠️ Condition Conflict Detected

Rows: TS-XX, TS-YY
{formula} = {calculated value} — conflicts with inherited condition "{input field}" ({constraint}).

The output uses the same domain as {input field}. The formula can produce values outside the shared bounds.
A business rule must decide which condition takes priority.
```

Ask via `AskUserQuestion`:
- **Header**: `Condition Conflict: {output field} vs {input field}`
- **Question**: `When {formula} produces {calculated value} which exceeds the inherited constraint from "{input field}" ({constraint}), what should the business do?`
- **Options** — always include at least these patterns; explain the business reason in each option:

| Business pattern | Suggested option text |
|---|---|
| Separate ceiling for output | "Allow {output} to exceed {conflicting max} — the output field has its own higher limit (provide the new max)" |
| Clamp to shared max | "Cap {output} at {conflicting max} — output must stay within the same bounds as {input field}" |
| Block the combination | "Reject this scenario — the input combination causing the overflow is not a valid business case" |
| Tiered / conditional rule | "Apply a different formula or rate when the result would exceed {conflicting max} (e.g. progressive pricing, rate cap)" |

Always explain **why** each option matters in business terms — do not just list technical actions.

---

## Step 4: Update the Unified Table

After the user answers, update the **same table** (do not create a new one):
1. Add the hidden rule as a `[Hidden]` condition in the **Input Analysis** section
2. Fill in the `Expected: {output field}` column for every row using the resolved rule
3. Add a short note in the Description column explaining what was applied (e.g. "ceiling: 366.3 → 367")
4. Update the `Result` column based on the `Expected` value (not `Calculated`)

**Complete table example after resolution (ceiling rule, decomposed formula):**

| ID | Name | Description | Input: Base Price | Input: Bonus Rate | Step: Base Price × Bonus Rate | Step: Rounded Adjustment | Calculated: New Price | Expected: New Price | Result |
|---|---|---|---|---|---|---|---|---|---|
| TS-01 | Normal | Adj 33.3 → ceiling 34. New price 333+34=367. | 333 | 10% | 33.3 | 34 | 367 | 367 | Valid - accepted |
| TS-02 | Whole number | Adj 30.0, no rounding. New price 300+30=330. | 300 | 10% | 30.0 | 30 | 330 | 330 | Valid - accepted |
| TS-03 | Conflict capped | Adj 10000.0. 60000 capped at 50000. | 50000 | 20% | 10000.0 | 10000 | 60000 | 50000 | Valid - accepted |
| TS-04 | Invalid base | Below minimum base price. | 99 | 10% | — | — | — | — | Invalid - rejected |

Rules:
- **One table only** — all scenarios in one place, including valid, invalid, and gap-affected rows
- Always show `Calculated:` even when no rounding was needed — testers verify the formula
- `—` in `Expected:` means the system produces no output (rejected)
- `Result` is always judged from `Expected:`, not `Calculated:`

The hidden condition becomes a permanent part of the test suite — future test cases must also respect it.

