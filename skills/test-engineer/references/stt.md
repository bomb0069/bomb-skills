# STT: State Transition Testing

## When to Use

Requirements that describe status workflows, approval flows, or state machines. Look for keywords: "status", "workflow", "state", "flow", "lifecycle", "approval", or transitions between states.

## Steps

1. **Identify all states** — list every status/state (e.g., New, Confirmed, Shipped, Delivered, Cancelled)

2. **Identify all valid transitions** — which state-to-state moves are allowed

3. **Identify terminal states** — states with no outgoing transitions

## State Transition Diagram

Draw a state diagram in a code block:

```
{Workflow name}

                          {action}              {action}
  [Start] ──────────► [{State A}] ──────────► [{State B}] ──────► [{Terminal}]
                           │                       │
                       {action}                    │ (no transition)
                           ▼                       │
                      [{State C}] ◄────────────────┘
                           │                  {action}
                       (terminal)
```

For branching paths (e.g., Approved OR Rejected):
```
                                    ┌─── Approve ──► [Approved] ──► [Published]
  [Draft] ──► [Submitted] ──► [Review] ─┤
                                    └─── Reject ───► [Rejected] ──► [Draft] (cycle)
```

## State Transition Table

Build a matrix of Current State × Action → Next State:

| Current State | Action | Next State | Valid? |
|---|---|---|---|
| New | Confirm | Confirmed | Valid |
| New | Cancel | Cancelled | Valid |
| Confirmed | Ship | Shipped | Valid |
| Shipped | Confirm | - | Invalid |
| Delivered | Cancel | - | Invalid |

## Test Case Generation

Generate test cases for:
- **Valid transitions**: one test per valid transition (verify state changes correctly)
- **Invalid transitions**: attempt transitions that should NOT be allowed (verify system rejects)
- **Happy path**: end-to-end flow from start to terminal state
- **Cycles**: if any cycle exists (e.g., Rejected→Draft), test the loop

Test case format:

| ID | Name | Description | Input: Current State | Input: Action | Expected: Next State | Expected Output |
|---|---|---|---|---|---|---|

- ID prefix: `ST-01`, `ST-02` (for State Transition)
- Valid → "Valid - state changed to {next}"
- Invalid → "Invalid - transition not allowed"
