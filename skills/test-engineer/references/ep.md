# EP: Equivalence Partitioning

## When to Use

Non-numeric fields: text, dropdown, enum, boolean, or any field where values fall into distinct classes.

## Partition Diagram

**Before generating test cases**, show a partition diagram.

Single EP condition:
```
{Field name} — Equivalence Partitions

  ┌─────────────────────────────┐
  │  VALID PARTITIONS           │
  │  [{value1}] [{value2}] ... │
  └─────────────────────────────┘
  ┌─────────────────────────────┐
  │  INVALID PARTITIONS         │
  │  [{invalid1}] [{invalid2}] │
  └─────────────────────────────┘
```

Multiple EP conditions → see [references/combination-all.md](combination-all.md) (All-EP Combined Partition Diagram section).

## Generic Partition Detection

Before generating test cases, scan all partition names for **broad/generic labels** — names that bundle multiple unstated values rather than naming a specific value. Common signals:

- "ทั่วไป", "อื่น ๆ", "กลุ่มที่เหลือ", "นอกนั้น", "อื่น"
- "General", "Others", "Other", "Remaining", "Miscellaneous", "Default", "Else"
- Any label ending with "etc." or "…"

When detected, **stop and ask via `AskUserQuestion` before generating test cases.** In the question:
1. State which partition name triggered the question
2. Suggest 2–4 concrete examples drawn from the business domain in the prompt (e.g., for an HR system: "Contractor", "Part-time", "Executive"; for a banking system: "Savings Account", "Current Account")
3. Ask whether those examples are all in this group, or if some should be separate partitions

If the user confirms all examples belong to one group, treat the partition as a single equivalence class and pick one representative value. If the user identifies distinct sub-groups, split them into separate partitions and re-run from Step 1.

## Steps

1. **Identify valid partitions** — each allowed value or class of valid inputs
   - Dropdown/enum: each option is a partition
   - Text: valid format (normal name, name with spaces, accents)
   - Boolean: true, false

2. **Identify invalid partitions** — inputs that should be rejected
   - Empty/blank input (if required)
   - Values not in the allowed set
   - Special characters (if not allowed)
   - Extremely long input (if practical limit)

3. **Generate one test case per partition** — same table format as BVA:
   - ID prefix: `TC-01`, `TC-02`
   - Each row tests one partition value
   - Valid → "Valid - accepted", Invalid → "Invalid - rejected"
