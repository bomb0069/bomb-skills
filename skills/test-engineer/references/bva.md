# BVA: Boundary Value Analysis

## When to Use

Numeric fields (integer, decimal) or time fields (HH:MM, HH:MM:SS) with min/max ranges.

## Precision Clarification

If the precision/step size is NOT clear, ask the user before generating test cases.

**When clear** — generate directly:
- Format stated explicitly (e.g., "integer", "2 decimal places", "HH:MM")
- Values have visible format (e.g., "09:00 to 17:00" = HH:MM, "0.01 to 9999.99" = 2 decimals)
- Unambiguous domain (e.g., "quantity 1 to 100" = integer)

**When ambiguous** — always ask:
- **Age** — always ambiguous. Could be integer OR birthdate-calculated. Always ask.
- **Money** — ambiguous unless decimals explicit. "30,000 baht" could be step 0.01, 1, or 100.
- **Percentage** — could be integer or decimal.

## Single-Bound Requirements

If only lower or upper limit is given:
1. Tell user which bound you found
2. Use `AskUserQuestion` to present choices for the missing bound
3. Wait for response before generating

## Number Line Diagram

**Before generating test cases**, show a number line diagram.

Both boundaries (6 points):
```
        Requirement: {field} must be between {min} and {max}

  [✗ Invalid]  [✓ Valid]  [✓ Valid]           [✓ Valid]  [✓ Valid]  [✗ Invalid]
       ↑            ↑          ↑                   ↑          ↑          ↑
       |            |          |                   |          |          |
  ◄─── {min-1} ──── {min} ──── {min+1} ── ··· ──── {max-1} ── {max} ──── {max+1} ───►
     Below Min   Min (on)  Above Min           Below Max  Max (on)  Above Max
```

Single boundary (3 points):
```
        Requirement: {field} max {max} (unit = {step})

                      [✓ Valid]       [✓ Valid]      [✗ Invalid]
                           ↑               ↑              ↑
                           |               |              |
                ◄───── {max-1} ────── {max} ────── {max+1} ───►
                        Below Max        Max (on)      Above Max
```

## 6 Core Boundary Values

| Position | Value | Expected Result |
|---|---|---|
| Just below minimum | min - 1 step | Invalid |
| Minimum (boundary) | min | Valid |
| Just above minimum | min + 1 step | Valid |
| Just below maximum | max - 1 step | Valid |
| Maximum (boundary) | max | Valid |
| Just above maximum | max + 1 step | Invalid |

**Step size by precision:**
- Integer: step = 1
- Decimal (N places): step = 10^(-N)
- Time (HH:MM): step = 1 minute
- Time (HH:MM:SS): step = 1 second

## Calculated Fields (Direct vs Indirect Input)

When a condition depends on a calculation (e.g., age from birthdate):
- Split Input column into: `Input: {DirectField} (direct)` and `Input: {IndirectField} (indirect)`
- Add `Calculated: {ResultField}` column
- Direct = what user enters (birthdate), Indirect = reference value (transaction date)
