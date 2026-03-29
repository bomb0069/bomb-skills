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

Multiple EP conditions (combined partition diagram with overlaps):
```
Combined Partitions: {Condition A} × {Condition B} → {Result}

┌────────────────────────────────────────────────┐
│  Universal set                                 │
│    ┌─ {A1} ──┐   ┌─ {A2} ──┐                  │
│  ┌─┼─────────┼───┼─────────┼─┐  {B1}          │
│  │ │ A1+B1   │   │ A2+B1   │ │                │
│  │ │ {calc}  │   │ {calc}  │ │                │
│  └─┼─────────┼───┼─────────┼─┘                │
│  ┌─┼─────────┼───┼─────────┼─┐  {B2}          │
│  │ │ A1+B2   │   │ A2+B2   │ │                │
│  │ │ {calc}  │   │ {calc}  │ │                │
│  └─┼─────────┼───┼─────────┼─┘                │
│    └─────────┘   └─────────┘                   │
│  INVALID: [{special cases}]                    │
└────────────────────────────────────────────────┘
```

Each overlap zone IS a test case.

## All-EP Combination Workflow

**When all conditions are EP type** (no BVA or STT), skip the combination method question and apply the EP combined partition diagram directly:

1. **Build the combined partition diagram** — show every valid partition intersection across all conditions
2. **Each overlap zone = one test case** — every combination of one valid value from each condition
3. **Add invalid partitions** — one test case per invalid partition per condition (other conditions at a valid value)
4. **Generate test cases from the diagram** — ID prefix `TC-01` for per-condition unit tests, then `TS-01` for combined scenarios from overlap zones

This produces a minimal complete set: all meaningful combinations are covered without asking the user to pick a method.

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
