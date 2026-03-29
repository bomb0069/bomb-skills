# STT: State Transition Testing

## When to Use

Requirements that describe status workflows, approval flows, or state machines. Look for keywords: "status", "workflow", "state", "flow", "lifecycle", "approval", or transitions between states.

## Steps

1. **Identify all states** — list every status/state from the requirement, then run Hidden State Analysis to surface states implied by domain knowledge but not explicitly mentioned

### Hidden State Analysis

After listing the explicit states from the requirement, analyse the domain and business context to detect states that are **implied but unstated**. Suggest them to the user before building the transition table.

#### Detection Signals

| Signal in requirement | Likely hidden state |
|---|---|
| "expires in X days / within X hours" | **Expired** — what happens when time runs out |
| "payment", "charge", "invoice" | **Payment Failed** / **Refunded** — financial error path |
| Multiple approvers ("manager approves, then finance") | One intermediate state per approval tier |
| "cancel" or "withdraw" mentioned | **Cancelling** (async cancel in progress) if cancel takes time |
| "retry", "fail", "error" mentioned | **Failed** — explicit error terminal state |
| "archive", "history", "record" mentioned | **Archived** — soft-end state after terminal |
| "edit", "update", "modify" after submission | **Draft** — locked editing state before re-submit |
| "on hold", "pause", "suspend" mentioned | **On Hold** / **Suspended** |
| "partial", "installment", "progress" mentioned | **Partially {action}** — incomplete fulfillment state |
| "lock", "block", "too many attempts" mentioned | **Locked** — security or rate-limit state |
| Background processing ("async", "queue", "batch") | **Processing** / **Pending** — intermediate waiting state |
| "no-show", "missed", "not responded" | **Expired** or **Abandoned** — implicit timeout state |

#### Domain Knowledge Patterns

When the requirement names a domain, apply these typical hidden states:

| Domain | Common hidden states not mentioned |
|---|---|
| Order / Fulfillment | Processing, Partially Shipped, Backordered, Returned, Expired |
| Payment / Finance | Payment Failed, Refunded, Disputed, Partially Paid, Expired (link) |
| User Account | Pending Verification, Locked, Suspended, Deactivated |
| Document / Approval | Draft, On Hold, Withdrawn, Archived, Superseded |
| Booking / Reservation | Waitlisted, No-show, Checked-in, Expired |
| Task / Ticket | Blocked, In Progress, Reopened, Duplicate, Won't Fix |
| Subscription | Trial, Grace Period, Past Due, Paused |
| Inventory / Stock | Reserved, Backordered, Recalled, Quarantined |

#### Proposal Format

Present detected hidden states before asking for confirmation:

```
🔍 Hidden States Detected

Based on [domain] domain knowledge, these states may be implied by the requirement but are not explicitly mentioned:

| # | State | Why it may exist | Signal |
|---|---|---|---|
| 1 | Expired | Orders that are not confirmed within the allowed window should move to an end state | "expires in X days" in requirement |
| 2 | Payment Failed | Payment step can fail; system needs a state to hold the order for retry | Financial domain pattern |
| 3 | Processing | Background fulfillment takes time; system needs an intermediate state between Confirmed and Shipped | Async operation pattern |

Please confirm which of these to include before I build the transition diagram.
```

Then call `AskUserQuestion` — present each detected hidden state as a confirm/reject choice, or use multi-select to let the user pick which ones to include. Include a brief business-context suggestion in each option description.

After confirmation: add the confirmed hidden states to the full states list and proceed to Step 2.

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
