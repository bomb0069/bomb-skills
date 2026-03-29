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

### Transition Identification (3 phases)

#### Phase 1 — Derive transitions from requirement + domain knowledge

Using the confirmed states from Step 1 and the identified domain, propose all plausible transitions. Do **not** limit to only what the requirement explicitly states — domain knowledge fills gaps the author assumed were obvious.

**Step 1a — Show the proposal diagram first**, using different arrow styles to distinguish sources:
- Solid arrow `──►` = from the requirement
- Dashed arrow `- - ►` = suggested from domain knowledge
- Label each dashed arrow with `[?]` to mark it as pending confirmation

```
📋 Proposed Transition Diagram

Solid arrows (──►) = from requirement   Dashed arrows (- - ►) = domain knowledge suggestion [?]

                    customer confirms          warehouse ships           customer receives
  [New] ──────────────────────────► [Confirmed] ────────────► [Shipped] ──────────────► [Delivered]
    │                                    │                        │
    │ customer cancels                   │ customer cancels [?]   │ return request [?]
    ▼                                    ▼                        ▼
[Cancelled] ◄────────────────────── [Cancelled]            [Returned]
    ▲
    │ auto-expire (no action 24h) [?]
  [New]
    │
    └─ - - - - - - - - - - - - - - - - ► [Expired]
```

**Step 1b — Show the proposal pivot matrix** to accompany the diagram.

Use the pivot matrix format: **rows = From State**, **columns = To State**, cells show the **action/event name** with a source tag:
- No tag = from the requirement (always included)
- `[?]` tag = domain knowledge suggestion (pending user confirmation)

```
| From \ To   | Confirmed              | Shipped         | Delivered        | Cancelled                   | Returned                    | Expired                          |
|-------------|------------------------|-----------------|------------------|-----------------------------|-----------------------------|----------------------------------|
| New         | Customer confirms      |                 |                  | Customer cancels            |                             | Auto-expire (no action 24h) [?]  |
| Confirmed   |                        | Warehouse ships |                  | Customer cancels [?]        |                             |                                  |
| Shipped     |                        |                 | Customer receives |                            | Return request [?]          |                                  |
| Delivered   |                        |                 |                  |                             |                             |                                  |
| Cancelled   |                        |                 |                  |                             |                             |                                  |
| Returned    |                        |                 |                  |                             |                             |                                  |
| Expired     |                        |                 |                  |                             |                             |                                  |

[?] = domain knowledge suggestion — please confirm whether to include
```

Then call `AskUserQuestion` to confirm: present each `[?]` transition and ask the user to approve or remove. Requirement transitions are always included. After confirmation, redraw the diagram with only confirmed transitions (all solid arrows, no `[?]` labels).

#### Domain Transition Reference

Use this as a starting point when proposing transitions. Add or remove based on the confirmed states from Step 1.

**Order / Fulfillment**

| From | Action | To | Notes |
|---|---|---|---|
| New | Payment initiated | Processing | if payment step exists |
| Processing | Payment succeeds | Confirmed | |
| Processing | Payment fails | Payment Failed | retry path |
| Payment Failed | Retry | Processing | |
| Payment Failed | Max retries exceeded | Cancelled | auto-cancel |
| Confirmed | Ship | Shipped | |
| Confirmed | Cancel | Cancelled | pre-shipment cancel |
| Shipped | Deliver | Delivered | |
| Shipped | Return request | Returned | post-ship return |
| Delivered | Return within window | Returned | post-delivery return |
| Any active state | Timeout | Expired | if time-based rule |

**Document / Approval**

| From | Action | To | Notes |
|---|---|---|---|
| Draft | Submit | Submitted | |
| Draft | Withdraw | Withdrawn | before submission |
| Submitted | Begin review | Under Review | |
| Submitted | Withdraw | Withdrawn | after submission |
| Under Review | Approve | Approved | |
| Under Review | Reject | Rejected | |
| Under Review | Put on hold | On Hold | |
| On Hold | Resume | Under Review | hold lifted |
| Rejected | Revise | Draft | rework cycle |
| Approved | Publish | Published | |
| Published | Archive | Archived | end of life |
| Published | Supersede | Superseded | new version replaces |

**User Account**

| From | Action | To | Notes |
|---|---|---|---|
| Pending Verification | Verify email | Active | |
| Pending Verification | Timeout | Expired | link expired |
| Active | Too many failed logins | Locked | security |
| Active | Policy violation | Suspended | admin action |
| Active | User closes account | Deactivated | |
| Locked | Admin unlocks | Active | |
| Suspended | Admin reinstates | Active | |

**Task / Ticket**

| From | Action | To | Notes |
|---|---|---|---|
| Open | Assign | In Progress | |
| In Progress | Block | Blocked | |
| Blocked | Unblock | In Progress | |
| In Progress | Resolve | Resolved | |
| Resolved | Reopen | In Progress | found again |
| Resolved | Close | Closed | |
| Any | Mark duplicate | Duplicate | |

**Booking / Reservation**

| From | Action | To | Notes |
|---|---|---|---|
| Requested | Add to waitlist | Waitlisted | no capacity |
| Waitlisted | Slot opens | Confirmed | |
| Confirmed | Check in | Checked In | |
| Confirmed | No-show | Expired | missed appointment |
| Confirmed | Cancel | Cancelled | |

---

#### Phase 2 — Cross-domain gap check

After the user confirms the transition list in Phase 1, review the transitions that were **not included** from the domain reference above. Present only those that are plausible given the confirmed states — these are potential requirement gaps.

Show **both a diagram and a pivot matrix** — same pattern as Phase 1.

**Step 2a — Gap diagram**: start from the confirmed diagram (all solid arrows from Phase 1) and overlay `[GAP?]` dashed arrows for each plausible missing transition:

```
⚠️ Possible Missing Transitions (Requirement Gap Check)

Solid arrows (──►) = confirmed   Dashed arrows (- - ►) with [GAP?] = may be missing from requirement

                    customer confirms          warehouse ships           customer receives
  [New] ──────────────────────────► [Confirmed] ────────────► [Shipped] ──────────────► [Delivered]
    │                                    │                        │                           │
    │ customer cancels                   │ customer cancels        │ return request             │ return within window [GAP?]
    ▼                                    ▼                        ▼                           ▼
[Cancelled]                         [Cancelled]              [Returned] ◄─ - - - - - - - [Delivered]
                                         │
    [New] - - - - - - - - - - - - - - - -│- - - - ► [Expired]  auto-expire if not shipped 30d [GAP?]
                                         └─ - - - - ► [Expired]

[Payment Failed] - - - - - - - - - - - - - - - - ► [Processing]  retry payment [GAP?]
[Payment Failed] - - - - - - - - - - - - - - - - ► [Cancelled]   max retries exceeded [GAP?]
```

**Step 2b — Gap pivot matrix**: show the confirmed matrix with `[GAP?]` cells overlaid:

```
Confirmed transitions are shown normally. [GAP?] cells are common in [domain] but not yet confirmed.
Please decide for each [GAP?]: include (add to scope) or exclude (mark as '-' → invalid transition TC).

| From \ To      | Confirmed | Shipped         | Delivered         | Cancelled                   | Returned                      | Expired                               | Processing           |
|----------------|-----------|-----------------|-------------------|-----------------------------|-------------------------------|---------------------------------------|----------------------|
| New            | Customer confirms |           |                   | Customer cancels            |                               | Auto-expire (24h)                     |                      |
| Confirmed      |           | Warehouse ships |                   | Customer cancels            |                               | Auto-expire if not shipped 30d [GAP?] |                      |
| Shipped        |           |                 | Customer receives |                             | Return request                |                                       |                      |
| Delivered      |           |                 |                   | -                           | Return within window [GAP?]   |                                       |                      |
| Payment Failed |           |                 |                   | Max retries exceeded [GAP?] |                               |                                       | Retry payment [GAP?] |

[GAP?] = common in [domain] domain but not in confirmed scope — include or exclude?
```

Call `AskUserQuestion` for each `[GAP?]` entry:
- **Yes** → add to confirmed transitions (solid arrow in final diagram)
- **No / out of scope** → replace with `-` (explicitly blocked — generates an invalid transition test case)

After all `[GAP?]` decisions are made, produce the **final diagram and pivot matrix** with everything resolved — all arrows solid, no `[?]` or `[GAP?]` labels. Then proceed to Step 3.

3. **Identify terminal states** — states with no outgoing transitions (discovered from the confirmed transition map — any state with no outgoing arrow is terminal by definition)

## State Transition Diagram

The final state diagram and pivot matrix are produced **after Phase 2** (once all `[GAP?]` decisions are resolved). All arrows are solid — no `[?]` or `[GAP?]` labels remain.

Draw the diagram in a code block using the format below. Show the action/event label on every arrow.

```
{Workflow name}

                          {action}              {action}
  [Start] ──────────► [{State A}] ──────────► [{State B}] ──────► [{Terminal}]
                           │                       │
                       {action}                    │ (no outgoing — terminal)
                           ▼                       │
                      [{State C}] ◄────────────────┘
                                         {action}
```

For branching paths (e.g., Approved OR Rejected):
```
                                    ┌─── Approve ──► [Approved] ──► [Published]
  [Draft] ──► [Submitted] ──► [Review] ─┤
                                    └─── Reject ───► [Rejected] ──► [Draft] (cycle)
```

## State Transition Table (Pivot Matrix)

Build a pivot matrix where **rows = From State**, **columns = To State**, and **cells = Action/Event** that causes the transition. Use `-` for transitions that are explicitly invalid (tested as invalid transition test cases). Leave the cell blank (``) if the transition is simply not applicable.

```
| From \ To   | Confirmed      | Shipped        | Delivered        | Cancelled          | Returned           | Expired            |
|-------------|----------------|----------------|------------------|--------------------|--------------------|--------------------|
| New         | Customer confirms |              |                  | Customer cancels   |                    | Auto-expire (24h)  |
| Confirmed   |                | Warehouse ships |                 | Customer cancels   |                    |                    |
| Shipped     |                |                | Customer receives |                   | Return request     |                    |
| Delivered   |                |                |                  | -                  | Return within window |                  |
| Cancelled   |                |                |                  |                    |                    |                    |
| Returned    |                |                |                  |                    |                    |                    |
| Expired     |                |                |                  |                    |                    |                    |
```

**Pivot matrix rules:**
- Each cell contains the **action/event name** that triggers the transition (keep it short)
- `-` = transition explicitly blocked (system should reject it) — generates an invalid transition test case
- Empty = not applicable (no business reason to attempt)
- The diagonal (From = To) is always empty (a state cannot transition to itself)
- Terminal states = rows where every cell is empty or `-`

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
