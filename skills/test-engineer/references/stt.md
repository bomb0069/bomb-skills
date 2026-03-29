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

Then call **one** `AskUserQuestion` with **`multiSelect: true`** — list all detected hidden states as options in a single question. The user selects all they want to include in one response. Include the business reason in each option's description.

After confirmation: add only the selected states to the full states list and proceed to Step 2.

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

Then call **one** `AskUserQuestion` with **`multiSelect: true`** — list all `[?]` transitions as selectable options in a single question. The user picks which ones to include in one response. Requirement transitions are always included regardless of the answer. After confirmation, redraw the diagram with only confirmed transitions (all solid arrows, no `[?]` labels).

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

Call **one** `AskUserQuestion` with **`multiSelect: true`** — list all `[GAP?]` transitions as selectable options in a single question:
- Selected → add to confirmed transitions (solid arrow in final diagram)
- Not selected → treated as explicitly out of scope — cell becomes `-` (generates an invalid transition test case)

After the single response, produce the **final diagram and pivot matrix** with everything resolved — all arrows solid, no `[?]` or `[GAP?]` labels. Then proceed to Step 3.

3. **Identify terminal states** — states with no outgoing transitions (discovered from the confirmed transition map — any state with no outgoing arrow is terminal by definition)

### Terminal State Analysis

#### Step 3a — Derive terminals from the transition map

Scan the final pivot matrix: any row where every cell is empty or `-` is a terminal state.

```
Derived terminal states:

| State | Reason |
|---|---|
| Delivered | No outgoing transitions in confirmed map |
| Cancelled | No outgoing transitions in confirmed map |
| Expired | No outgoing transitions in confirmed map |
```

#### Step 3b — Quasi-terminal check (domain knowledge)

Not all terminal-looking states are truly final in every business scenario. Some states can be "resurrected" in extreme or exceptional cases — edge cases the requirement author may not have considered. Use domain knowledge to flag these.

**Quasi-terminal signals by domain:**

| Domain | Apparent terminal | Possible resurrection | Business trigger |
|---|---|---|---|
| Order / Fulfillment | Delivered | → Return / Refund | Fraud, wrong item, damage |
| Order / Fulfillment | Cancelled | → Reinstated | Customer calls to undo cancel within window |
| Points / Loyalty | Expired | → Restored | Points expired due to system error or fraud investigation |
| Points / Loyalty | Redeemed | → Reversed | Redemption was fraudulent or transaction rolled back |
| Payment | Refunded | → Disputed | Refund itself challenged |
| User Account | Deactivated | → Reactivated | Account closed by mistake, legal obligation to restore |
| Document | Archived | → Reinstated | Archived in error, regulation requires reinstatement |
| Task / Ticket | Closed | → Reopened | Issue resurfaces after closure |
| Booking | No-show / Expired | → Rescheduled | System error caused missed slot |

#### Proposal format

Present flagged quasi-terminals and ask the user to decide:

```
🔍 Quasi-Terminal State Review

The following states appear terminal (no outgoing transitions) but may have escape paths
in exceptional business scenarios. Please confirm whether each is truly final or needs an
exit transition:

| # | State | Currently terminal | Possible escape | Business scenario | Keep terminal? |
|---|---|---|---|---|---|
| 1 | Cancelled | Yes | → Reinstated (New) | Customer calls within 1 hour to undo cancellation — does the business allow this? | ? |
| 2 | Delivered | Yes | → Returned | Fraud investigation reveals item was not actually delivered or was counterfeit | ? |
| 3 | Expired | Yes | → Restored | Points expired due to a system bug; operations team needs to restore them manually | ? |
```

Call **one** `AskUserQuestion` with **`multiSelect: true`** — list all flagged quasi-terminal states as selectable options in a single question. Include the business scenario and the proposed escape path in each option description. Selected states get an escape transition added; unselected states remain truly terminal.

After the single response: finalize terminal states list and update the diagram if any escapes were added.

## State Transition Diagram

All state transition diagrams are generated in **both ASCII and Mermaid (`stateDiagram-v2`)** format. See [references/mermaid.md](mermaid.md) for the full format, examples, and legend rules.

Three diagram variants are produced during the workflow:

1. **Phase 1 proposal diagram** — requirement transitions (no tag) + domain knowledge suggestions labeled `[?]`
2. **Phase 2 gap check diagram** — confirmed transitions + unconfirmed plausible transitions labeled `[GAP?]`; quasi-terminal escape paths labeled `[ESCAPE?]`
3. **Final diagram** — produced after all Phase 2 and Step 3b decisions are resolved; all transitions confirmed, no tags

The final diagram and pivot matrix are produced **after Phase 2** (once all `[GAP?]` and `[ESCAPE?]` decisions are resolved).

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

Generate two levels of tests:

### Level 1 — Transition Test Cases (per-transition)

One test case per transition. When a transition has an associated condition (e.g., BVA boundary, time rule, EP partition), **combine the state transition with that condition's test cases** to fully cover the boundary.

Example: `Active → Expired` triggered by "auto-expire after 180 days" — combine with BVA:

| ID | Name | Description | Input: Current State | Input: Days Since Activation | Expected: Next State | Expected Output |
|---|---|---|---|---|---|---|
| ST-01 | Points expire at boundary | Points active exactly 180 days — expire trigger fires | Active | 180 | Expired | State changed to Expired |
| ST-02 | Points still active just before | One day before the expiry boundary — no trigger | Active | 179 | Active | State unchanged — still Active |
| ST-03 | Points already expired on day after | Day 181 — expiry should have been triggered at 180 | Active | 181 | Expired | State changed to Expired |
| ST-04 | Invalid: Expired → Active directly | Attempt to reactivate without restoration process | Expired | - | - | Invalid — transition not allowed |

**Rules for transition test cases:**
- **Valid transitions**: one test per valid transition (verify state changes correctly)
- **Invalid transitions**: one test per `-` cell in the pivot matrix (verify system rejects)
- **Condition-combined transitions**: when a transition has a numeric threshold, date rule, or EP partition — generate BVA/EP test cases for that condition and pair each with the transition
- **Cycles**: if any cycle exists (e.g., Rejected→Draft→Submitted), generate tests for each step in the loop
- ID prefix: `ST-01`, `ST-02`
- Valid → `"Valid - state changed to {next state}"`
- Invalid → `"Invalid - transition not allowed"`

---

### Level 2 — State Journey Scenarios (end-to-end paths)

Generate one scenario per distinct **path from start state to a terminal state**. Each scenario is a complete business story — the sequence of states and events a real entity travels through from creation to its final resting state.

**Path enumeration rules:**
- Start from the initial state (the state an entity enters when first created)
- Enumerate every distinct path to every terminal state
- For branches (Approved vs Rejected), each branch = a separate scenario
- For cycles (Rejected→Draft→Submitted), test the loop once then continue to terminal
- For long paths, collapse obvious linear chains: `New→Processing→Confirmed` can be one step description if there are no branches in between

**State Journey Scenarios table format:**

| ID | Journey Name | Business Story | State Path | Expected Final State |
|---|---|---|---|---|

**Column definitions:**

**Journey Name** — one sentence describing the full arc of this path in business terms:
- `"Loyalty member earns and redeems points normally"`
- `"Points expire before member has a chance to redeem"`
- `"Fraudulent redemption reversed by operations team"`

**Business Story** — 3–5 sentences narrating the full end-to-end event sequence. Each sentence = one state transition in the path. Written as a business scenario, not technical steps.

**State Path** — the sequence of states, e.g.: `Active → Redeemed → (terminal)`
- Show the action/event on each arrow: `Active --[redeems]--> Redeemed`

**Expected Final State** — the terminal state this path ends in, and what it means in business terms.

**Example** (Loyalty Points system — states: Earned, Active, Redeemed, Expired, Cancelled):

| ID | Journey Name | Business Story | State Path | Expected Final State |
|---|---|---|---|---|
| SJ-01 | Member earns and redeems points successfully | Member completes a purchase and points are issued in Earned state. System activates the points after verification. Member browses the rewards catalogue and selects a reward to redeem. System processes the redemption and points move to Redeemed. Points record is closed — no further changes possible. | Earned --[activate]--> Active --[redeem]--> Redeemed | Redeemed — points consumed, record closed |
| SJ-02 | Points expire before redemption | Member earns points but does not log in or redeem within 180 days. The auto-expiry job runs at the 180-day mark and moves points to Expired. Points are permanently lost unless restored by operations. | Earned --[activate]--> Active --[auto-expire 180d]--> Expired | Expired — points lost, no further transitions |
| SJ-03 | Admin cancels points due to fraud | Fraud team detects suspicious earn transaction. Admin cancels the points directly from Active state. Points are locked and closed. Member is notified. | Earned --[activate]--> Active --[admin cancels]--> Cancelled | Cancelled — points invalidated |
| SJ-04 | Fraudulent redemption reversed | Member redeems points but fraud detection flags the transaction post-redemption. Operations team triggers reversal, returning points to Active state for reassessment. Member is placed under review. Points eventually cancelled by admin. | Active --[redeem]--> Redeemed --[reverse]--> Active --[admin cancels]--> Cancelled | Cancelled — fraud case resolved |

**SJ ID prefix**: `SJ-01`, `SJ-02` (State Journey)

**Coverage goal**: every terminal state must be reached by at least one journey scenario. Every branch point in the diagram must be covered by at least two scenarios (one per branch).
