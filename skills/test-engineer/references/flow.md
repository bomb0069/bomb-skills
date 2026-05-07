# Test Engineer Skill — Workflow

## Summary (Single Screen)

```
                    ┌─────────────────────────────────────────────────────┐
                    │           User provides requirement                  │
                    └─────────────────────────────────────────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    ▼                       ▼                       ▼
             Numeric/Time             Text/Dropdown           Status/Workflow
                 BVA                      EP                      STT
             Clarify:                 Clarify:
          - Age → int/date?       - Generic label?
          - Duration → int/date?    (ทั่วไป/Others)
          - Money → precision?      Ask to split
                    │                       │                       │
                    └───────────────────────┴───────────────────────┘
                                            │
                           ┌────────────────┼────────────────┐
                           ▼                ▼                ▼
                        1 cond.         2+ cond.         2+ cond.
                        skip            all EP           mixed/STT
                                    All-EP diagram    Ask method:
                                                      All / Pairwise /
                                                      Business / Sequential /
                                                      STT
                                            │
                                            ▼
                    ┌─────────────────────────────────────────────────────┐
                    │  Step 3  Per-condition: Diagram + Unit Test Cases    │
                    │          BVA → 6 boundary values (TC-xx)            │
                    │          EP  → 1 case per partition (TC-xx)         │
                    │          STT → valid/invalid transitions (ST-xx)    │
                    └─────────────────────────────────────────────────────┘
                                            │
                                            ▼
                    ┌─────────────────────────────────────────────────────┐
                    │  Step 4  Business Test Cases (BT-xx)                │
                    │          Realistic valid AND invalid values          │
                    └─────────────────────────────────────────────────────┘
                                            │
                                            ▼  (2+ conditions only)
                    ┌─────────────────────────────────────────────────────┐
                    │  Step 5  Combined Test Scenarios (TS-xx)            │
                    │          Decision table across all conditions        │
                    └─────────────────────────────────────────────────────┘
                                            │
                                            ▼  (if calculated output)
                    ┌─────────────────────────────────────────────────────┐
                    │  Step 5b  Gap Analysis                              │
                    │           Compute output → flag hidden rules        │
                    └─────────────────────────────────────────────────────┘
                                            │
                                            ▼
                    ┌─────────────────────────────────────────────────────┐
                    │  Step 6  Save Results                               │
                    │          Excel · Markdown · Both · Skip             │
                    └─────────────────────────────────────────────────────┘
```

---

## Mermaid Diagram

```mermaid
flowchart TD
    A([User provides requirement]) --> B[Step 1: Analyze & count conditions\nAssign C1, C2, C3...]

    B --> C{Input type?}
    C -->|Numeric / Time range| D[BVA]
    C -->|Text / Dropdown / Enum / Boolean| E[EP]
    C -->|Status / Workflow| F[STT]

    D --> D1{Precision clear?}
    D1 -->|Age field| D2[Ask: integer or birthdate-calculated?]
    D1 -->|Duration field\ntenure, period, term...| D2
    D1 -->|Money — no decimals stated| D3[Ask: decimal precision?]
    D1 -->|Clear| D4[BVA ready]
    D2 --> D4
    D3 --> D4

    E --> E1{Generic partition label?\nทั่วไป / Others / Remaining...}
    E1 -->|Yes| E2[Ask: one class or split?\nSuggest domain examples]
    E2 -->|Split into sub-groups| B
    E2 -->|Single class — pick representative| E3[EP ready]
    E1 -->|No| E3

    F --> F3[STT ready]

    D4 & E3 & F3 --> G{How many conditions?}

    G -->|1 condition| H
    G -->|2+ all EP| I[All-EP combined\npartition diagram]
    G -->|2+ any STT| J[Ask combination method]
    G -->|2+ mixed BVA/EP| J

    J --> K{Method}
    K -->|STT| L1[STT combination]
    K -->|All combinations| L2[All combinations]
    K -->|Pairwise| L3[Pairwise]
    K -->|Business-driven| L4[Business-driven]
    K -->|Sequential| L5[Sequential]

    I & L1 & L2 & L3 & L4 & L5 --> H

    H[Step 3: Per-condition loop\nDiagram + Unit Test Cases]
    H --> N[Step 4: Business Test Cases\nValid AND invalid realistic values]

    N --> O{2+ conditions?}
    O -->|Yes| P[Step 5: Combined Test Scenarios\ndecision table TS-01, TS-02...]
    O -->|No| Q
    P --> Q

    Q{Calculated output\nin requirement?}
    Q -->|Yes| R[Step 5b: Gap Analysis\ncompute output for each scenario]
    R --> R1{Gap found?}
    R1 -->|Yes| R2[Ask hidden rule\nvia AskUserQuestion]
    R2 --> R3[Add Hidden condition\nupdate affected test cases]
    R3 --> S
    R1 -->|No| S
    Q -->|No| S

    S[Step 6: Ask how to save\nAskUserQuestion]
    S --> T{Choice}
    T -->|Excel| U[Python script → .xlsx\none sheet per condition\n+ test-scenarios sheet]
    T -->|Markdown| V[Save to test-cases/name.md]
    T -->|Both| W[.xlsx + .md]
    T -->|Skip| X
    U & V & W --> X([Done])
```

---

## Text Diagram

### Overview

```
User provides requirement
         │
         ▼
┌─────────────────────────────────┐
│  Step 1: Analyze & count        │
│  conditions — assign C1, C2...  │
└─────────────────────────────────┘
         │
         ▼
  ┌──────────────────┐
  │  Input type?     │
  └──────────────────┘
    │        │        │
    ▼        ▼        ▼
  BVA        EP      STT
```

### BVA — Precision Check

```
BVA condition
      │
      ▼
┌─────────────────────┐
│  Precision clear?   │
└─────────────────────┘
  │           │           │           │
  ▼           ▼           ▼           ▼
Age /      Money —     Percentage   Clear
Duration   no decimal  ambiguous      │
  field    stated          │          │
  │            │           ▼          │
  ▼            ▼     Ask: integer     │
Ask:        Ask:     or decimal?      │
integer or  decimal      │            │
date-calc?  precision    │            │
  │            │          │           │
  └────────────┴──────────┴───────────┘
                          │
                          ▼
                      BVA ready
```

**Duration fields** = tenure, period, term, service years, subscription length, contract duration, seniority, probation

When date-calculated: use **direct input** (hire date / start date) + **indirect input** (reference date) + **Calculated** column. Step = 1 day.

### EP — Generic Partition Check

```
EP condition
      │
      ▼
┌──────────────────────────────────────┐
│  Any generic label?                  │
│  ทั่วไป / อื่น ๆ / Others /          │
│  Remaining / Miscellaneous / Else... │
└──────────────────────────────────────┘
        │                   │
       Yes                  No
        │                   │
        ▼                   ▼
Ask: one class          EP ready
or split?
Suggest domain
examples
        │
   ┌────┴────┐
   ▼         ▼
Split      Single class —
into       pick one
sub-groups representative
   │         │
   ▼         ▼
Re-analyze  EP ready
(back to
 Step 1)
```

### Step 2: Combination Method

```
All conditions analyzed
         │
         ▼
┌────────────────────┐
│  How many          │
│  conditions?       │
└────────────────────┘
    │           │
    ▼           ▼
  Only 1      2 or more
    │               │
    │       ┌───────┴───────────┐
    │       ▼                   ▼
    │   All EP?          Any STT or
    │       │            mixed BVA/EP?
    │       ▼                   │
    │  All-EP combined          ▼
    │  partition diagram   Ask combination
    │       │              method:
    │       │              1. STT (if STT exists)
    │       │              2. All combinations
    │       │              3. Pairwise
    │       │              4. Business-driven
    │       │              5. Sequential
    │       │                   │
    └───────┴───────────────────┘
                    │
                    ▼
           Proceed to Step 3
```

### Step 3–4: Per-Condition Loop

```
For each condition (C1, C2, C3...):
         │
         ▼
┌──────────────────────────────────┐
│  Show diagram                    │
│  BVA → number line diagram       │
│  EP  → partition diagram         │
│  STT → state diagram             │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Unit Test Cases                 │
│  TC-01, TC-02... / ST-01...      │
│  BVA: 6 boundary values          │
│  EP: one case per partition      │
│  STT: valid + invalid transitions│
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Business Test Cases  BT-01...   │
│  Realistic valid AND invalid     │
│  values from the business domain │
└──────────────────────────────────┘
```

### Step 5: Combined Test Scenarios

```
2 or more conditions?
         │
        Yes
         │
         ▼
┌──────────────────────────────────┐
│  Test Scenarios  TS-01, TS-02... │
│  Decision table combining all    │
│  conditions per chosen method    │
│                                  │
│  Columns:                        │
│  ID | Scenario Name |            │
│  Business Scenario |             │
│  {condition columns} |           │
│  Covers | Expected Output        │
└──────────────────────────────────┘
```

### Step 5b: Gap Analysis

```
Does the requirement have
a calculated output?
         │
    ┌────┴────┐
    ▼         ▼
   Yes        No — skip
    │
    ▼
Compute output for
each scenario row
    │
    ▼
┌──────────────────┐
│  Gap found?      │
└──────────────────┘
    │         │
   Yes        No
    │
    ▼
Ask hidden rule
via AskUserQuestion
    │
    ▼
Add [Hidden] condition
Update affected test cases
```

### Step 6: Save Results

```
Ask how to save
(AskUserQuestion)
         │
   ┌─────┼──────┬──────┐
   ▼     ▼      ▼      ▼
Excel  Markdown Both  Skip
   │     │      │      │
   ▼     ▼      ▼      │
.xlsx   .md  .xlsx      │
Python  save  + .md     │
script  to    both      │
        test-           │
        cases/          │
   └─────┴──────┴───────┘
                │
                ▼
              Done
```
