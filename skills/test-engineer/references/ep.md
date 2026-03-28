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
