# Combination Method: State Transition Testing (STT)

Use this method when **any condition is a status, workflow, or state machine** (input type = state/workflow in Step 1). STT treats the state lifecycle as the primary axis of combination — other conditions (BVA, EP) are woven in at the transition level and at the journey level.

This method produces two levels of output that together replace the flat Test Scenarios table used by other combination methods:

| Level | Output | ID prefix | Purpose |
|---|---|---|---|
| Level 1 | Transition Test Cases | ST-xx | One test per individual transition, including condition-combined cases (BVA/EP × state) |
| Level 2 | State Journey Scenarios | SJ-xx | End-to-end paths from start state to each terminal state |

Follow the full STT workflow in [references/stt.md](stt.md) to build both levels.

## When to Offer This Method

Offer as option 1 in the combination method question whenever **at least one condition** has input type `state/workflow`. Typical signals:
- Requirement mentions status, lifecycle, workflow, approval flow, or state machine
- Conditions include a field whose values are states (e.g. Active/Expired/Cancelled)
- Requirement describes transitions between named statuses

## How Non-STT Conditions Are Handled

When the requirement has both a state/workflow condition AND other conditions (BVA or EP):

**At the transition level (Level 1)**
- Identify which transitions are triggered or gated by the other conditions
- For each such transition, generate combined test cases:
  - BVA condition gating a transition → generate boundary values paired with the state transition
  - EP condition gating a transition → generate one test case per partition paired with the state transition
- Example: `Active → Expired` triggered by "180 days since activation" — generate BVA cases (179, 180, 181 days) each paired with the `Active → Expired` transition

**At the journey level (Level 2)**
- Include the relevant input values for each transition step in the Business Story
- Add an "Input Conditions" column to the State Journey Scenarios table to record which EP/BVA values apply at each step of the journey

### Extended SJ table when other conditions are present

| ID | Journey Name | Business Story | State Path | Input Conditions | Expected Final State |
|---|---|---|---|---|---|
| SJ-01 | Points expire before redemption | Member earns points and they are activated. No redemption occurs for 181 days past the activation date. Auto-expiry job triggers at the 180-day boundary and moves points to Expired. | Earned → Active → Expired | Days since activation: 181 (BVA — over boundary) | Expired — points lost |
| SJ-02 | Points still active just before expiry | Member earns and activates points. On day 179 — one day before the expiry threshold — no auto-expiry fires. Points remain Active. | Earned → Active (no expiry) | Days since activation: 179 (BVA — under boundary) | Active — points still valid |

## Rules

- Always run the full STT workflow (Steps 1–3 in stt.md): hidden state analysis → transition identification with gap check → terminal state quasi-terminal check
- The Level 1 ST-xx test cases are the equivalent of per-condition unit test cases
- The Level 2 SJ-xx scenarios are the equivalent of the Test Scenarios table used in other combination methods
- Follow the **Test Scenarios Table Format** in [references/common.md](common.md) for the SJ table's Journey Name, Business Story, and Expected Final State columns
- Label: **"State Journey Scenarios (state transition — for acceptance/integration testing)"**
