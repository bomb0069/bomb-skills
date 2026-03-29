# Common: Test Case Output Format & Business Test Data

## Test Case Table Format

Do not use emojis anywhere in your output. Use plain text and markdown formatting only.

**Input columns** must use the `Input:` prefix followed by the field name. This enables grouping when exported to spreadsheets.

For a **single direct input** field:

| ID | Name | Description | Input: {FieldName} | Expected Output |
|---|---|---|---|---|
| TC-01 | {short name} | {business description} | {value} | {result} |

For **calculated fields** with direct and indirect inputs:

| ID | Name | Description | Input: {DirectField} (direct) | Input: {IndirectField} (indirect) | Calculated: {ResultField} | Expected Output |
|---|---|---|---|---|---|---|

- **(direct)** = what the user actually enters (e.g., birthdate)
- **(indirect)** = the reference value used in the calculation (e.g., transaction date)
- **Calculated:** = the computed value that the condition checks against

### Column Definitions

- **ID**: Sequential test case ID (TC-01, TC-02, ...)
- **Name**: Short name describing what this test case covers (e.g., "Below minimum age")
- **Description**: Business-understandable explanation in **1–2 sentences**
- **Input: {FieldName}**: Concrete test data value, ready to copy-paste. Always include field name after `Input:`
- **Expected Output**: Accept or reject (e.g., "Invalid - rejected", "Valid - accepted")

### ID Prefixes by Type

| Type | Prefix | Used for |
|---|---|---|
| Unit test case | TC-01 | BVA boundaries, EP partitions |
| State transition | ST-01 | Valid/invalid state transitions |
| Business test case | BT-01 | Realistic domain values |
| Test scenario | TS-01 | Combined multi-condition scenarios |

## Test Scenarios Table Format (TS)

The **Test Scenarios** table (TS-01, TS-02, …) combines multiple conditions into cross-condition scenarios. It uses a richer format than the per-condition unit test case table.

### Column Structure

| ID | Scenario Name | Business Scenario | {Condition columns} | Covers | Expected Output |
|---|---|---|---|---|---|

**Column definitions:**

**ID** — `TS-01`, `TS-02`, … sequential

**Scenario Name** — one short business-readable sentence synthesized from the **Business Test Case names** (BT-xx) of the contributing conditions (see Covers column).
- Merge the key ideas from each contributing BT name into one sentence that describes the combined business situation
- Write from a business perspective, not a technical one
- Capture both the actor/subject AND the key condition that makes this combination meaningful
- Examples:
  - BT names: `"Developer submits for annual review"` + `"Employee on salary freeze"` → `"Developer employee applies for raise during salary freeze period"`
  - BT names: `"QA tester standard review"` + `"Eligible employee"` → `"Tester receives standard performance raise"`
- NOT: `"C1=Developer, C2=Not Eligible"` or a copy-paste of one BT name

**Business Scenario** — 2–3 sentences synthesized from the **Business Test Case descriptions** (BT-xx) of the contributing conditions, joined into an end-to-end business story.
- Combine the individual BT descriptions into a flowing narrative covering: **who** is involved, **what action** they take, **what data** goes in, and **what result** the system produces
- The reader should understand the full journey from start to finish without needing to look up conditions separately
- Each sentence should connect logically: setup → action → outcome
- Examples:
  - BT descriptions: `"A system developer submits annual salary review through HR portal"` + `"HR system finds active salary freeze on the employee account"` → `"A system developer submits an annual salary review request through the HR portal. The system checks eligibility and detects an active salary freeze on the account. The raise is blocked and the employee receives a notification with the freeze reason and the original salary unchanged."`
- NOT a bullet list, NOT a copy of the Expected Output, NOT a repeat of the Scenario Name

**Condition columns** — expand each condition into sub-columns so testers can copy values directly into the system under test:

For an **EP condition with an associated business value** (rate, price, discount %, etc.):
- Sub-column 1: `{Condition name}` — the value to select or enter (the partition)
- Sub-column 2: `{Parameter name}` — the associated business value linked to that partition

For a **plain EP / BVA condition** (no associated parameter):
- Single column: `{Condition name} ({key constraint})` — the value to enter

Use a **business-readable header** that is self-explanatory without reading the full analysis:
- `Employee Department` not `Input: Department`
- `Raise Rate (%)` not `Input: Raise Rate`
- `File Type (PDF/DOCX/XLSX only)` not `Input: File Type`
- `Order Quantity (1–100 units)` not `Input: Quantity`

**Covers** — Business Test Case IDs that combine to form this scenario, format `CX-BTxx`:
- `C1` = Condition 1 (from the C1/C2/C3 IDs assigned in Step 1)
- `BT02` = business test case 02 from that condition's Business Test Cases table
- List all conditions: `C1-BT03 + C2-BT01 + C3-BT02`

**Expected Output** — write as a business outcome sentence:
- Include what actually happens in the system
- Examples:
  - `"Raise applied — salary increases by 7%"` not `"Valid - accepted"`
  - `"Upload rejected — invalid file type, user sees error message"` not `"Invalid - rejected"`
  - `"Order confirmed — quantity 50 within allowed range"` not `"Valid - accepted"`

### Example

Conditions from Step 1:
- **C1**: Employee Department (EP) — General 5%, System Developer 7%, Tester 10%, Finance 6.5%
- **C2**: Raise Eligibility (EP) — Eligible, Not Eligible

C1 has an associated business value (raise rate %) → split into two sub-columns.
C2 is a plain EP condition (no associated parameter) → single column.

| ID | Scenario Name | Business Scenario | Employee Department | Raise Rate (%) | Raise Eligibility | Covers | Expected Output |
|---|---|---|---|---|---|---|---|
| TS-01 | Developer receives standard raise | A system developer submits an annual salary review request through the HR portal. HR confirms the employee is eligible with no active freeze. The system applies the 7% raise rate to the current salary. | System Developer | 7% | Eligible | C1-BT02 + C2-BT01 | Raise applied — salary increases by 7% |
| TS-02 | Developer frozen — raise blocked | A system developer submits for review but the HR system detects an active salary freeze on the account. The raise is blocked regardless of the role's standard rate. The employee receives a notification showing the freeze reason and the original salary unchanged. | System Developer | 7% | Not Eligible | C1-BT02 + C2-BT02 | No raise — salary unchanged, freeze reason shown |
| TS-03 | Tester receives highest raise | A QA tester submits for annual review and is confirmed eligible. The system looks up the tester's standard rate of 10% — the highest among all departments — and applies it to the current salary. | Tester | 10% | Eligible | C1-BT03 + C2-BT01 | Raise applied — salary increases by 10% |
| TS-04 | Finance staff frozen | A finance department employee on salary freeze submits for review. The HR system detects the freeze and blocks the raise. The employee's salary remains unchanged. | Finance | 6.5% | Not Eligible | C1-BT04 + C2-BT02 | No raise — salary unchanged |



For each condition, generate **Business Test Cases** alongside unit test cases.

Business test data = realistic values from the business domain — what real users actually enter. **Must include both valid AND invalid** realistic values.

**IMPORTANT: Include failure scenarios.** Real users submit invalid data (oversized files, wrong formats, out-of-range values). Examples:
- File size: valid (3MB, 15MB) AND invalid (150MB oversized, 0MB empty)
- File type: valid (PDF, DOCX) AND invalid (JPG photo, EXE)
- Age: valid (25, 35) AND invalid (10 child, 80 elderly)

**How to identify business test data:**
1. Look for business context in the user's prompt
2. Generate realistic **valid** values (common/typical usage)
3. Generate realistic **invalid** values (common mistakes users actually hit)
4. If no context, ask the user via `AskUserQuestion` or generate generic data with an offer to customize

**Business Test Cases table format:**
- ID prefix: `BT-01`, `BT-02`
- Name: business scenario (e.g., "Typical young professional", "Oversized upload attempt")
- Include both valid AND invalid values
- Label: **"Business Test Cases (for acceptance/integration testing)"**

## How to Ask Clarification Questions

**IMPORTANT**: Whenever you need to ask the user a clarification question, you MUST call the `AskUserQuestion` tool. Do NOT write the question as text output.

Rules:
- First, output your input analysis as text (field name, type, what's missing)
- Then STOP outputting text and CALL `AskUserQuestion` with your questions
- Each question needs: `question`, short `header` (max 12 chars), 2-4 `options` each with `label` and `description`, `multiSelect: false`
- "Other" option is added automatically — do NOT include it
- If you recommend an option, put it first and add "(Recommended)" to the label

**Multiple independent questions**: pass all questions in a single `AskUserQuestion` call (up to 4). Each becomes a tab.
