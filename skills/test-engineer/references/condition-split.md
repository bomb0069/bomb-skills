# Condition Splitting: Detecting Hidden Sub-Conditions

When analyzing requirements, some business descriptions bundle multiple orthogonal conditions into a single list. Detect and split these **before** assigning techniques or moving to Step 2.

## Detection Signals

A list of values likely contains hidden sub-conditions when **one or more** of these signals appear:

| Signal | Description | Example |
|---|---|---|
| **Override/exception item** | One item negates or bypasses all others — it is not a peer of the other values | "No raise" in a list of role-based rates — it overrides the rate entirely |
| **Mixed category types** | Items belong to fundamentally different categories (role vs. status, type vs. flag) | Developer, Tester, Finance (roles) mixed with "Not eligible" (status) |
| **Cross-cutting item** | One item applies regardless of the other items' values | "Employee does not get a raise" can apply to ANY role |
| **Multiple business questions** | The list is simultaneously answering more than one question | "What rate does the role get?" AND "Is the employee eligible at all?" |
| **Different output behaviours** | Some values lead to a calculation; one value leads to no calculation at all | Role values → apply percentage; "No raise" → skip calculation entirely |

## Step: Detect and Propose Split

When signals are found, show the detected structure before continuing:

```
🔍 Hidden Sub-Conditions Detected

The requirement describes these values as one condition:
  {original list}

These values appear to encode {N} separate conditions:

  Condition 1: {name}
    Values: {list}
    Answers: "{business question 1}"

  Condition 2: {name}
    Values: {list}
    Answers: "{business question 2}"

Splitting these produces clearer, more complete test cases.
```

Then ask via `AskUserQuestion`:
- **Header**: `Condition Split: {original condition name}`
- **Question**: `Should I split this into {N} separate conditions?`
- **Options**:
  - `"Yes — split into {Condition 1 name} and {Condition 2 name} (Recommended)"`
  - `"No — treat the entire list as a single condition"`

## After Confirmation

If the user confirms the split:
1. Replace the original condition with the N split conditions in the **Input Analysis** section
2. Assign a technique to each split condition independently (EP, BVA, STT)
3. Continue with the normal workflow — combination method (Step 2), per-condition tables (Step 3), etc.

If the user declines the split:
- Keep the original condition as-is and assign a single technique to it

## Example

**Original requirement (Thai):**
> การคำนวนการขึ้นเงินเดือนพนักงาน
> - พนักงานทั่วไป 5%
> - นักพัฒนาระบบ 7%
> - Tester 10%
> - ฝ่ายการเงิน 6.5%
> - พนักงานไม่ได้ขึ้น

**Detection:**
- `พนักงานไม่ได้ขึ้น` (No raise) is NOT a role — it overrides the rate for any role
- Signals: override item + cross-cutting item + multiple business questions

**Proposed split:**

```
🔍 Hidden Sub-Conditions Detected

The requirement lists these as one condition:
  พนักงานทั่วไป 5%, นักพัฒนาระบบ 7%, Tester 10%, ฝ่ายการเงิน 6.5%, พนักงานไม่ได้ขึ้น

These appear to encode 2 separate conditions:

  Condition 1: Department / Role  (EP)
    Values: พนักงานทั่วไป, นักพัฒนาระบบ, Tester, ฝ่ายการเงิน
    Answers: "What raise rate does this role receive?"

  Condition 2: Raise Eligibility  (EP / Boolean)
    Values: Eligible (ได้ขึ้นเงินเดือน), Not eligible (ไม่ได้ขึ้น)
    Answers: "Is this employee eligible for a raise at all?"

"พนักงานไม่ได้ขึ้น" is not a role — it applies regardless of department
and overrides the rate calculation entirely.
```

**After split, the test scenarios cover:** Role × Eligibility combinations
- Eligible + Developer → apply 7%
- Not eligible + Developer → no raise (0%)
- Eligible + Finance → apply 6.5%
- Not eligible + Finance → no raise (0%)
- etc.
