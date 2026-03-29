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

**Scenario Name** — one short business-readable sentence describing what this combination tests.
- Write from a business perspective, not a technical one
- Example: `"Developer employee applies for raise during salary freeze period"`
- NOT: `"C1=Developer, C2=Not Eligible"`

**Business Scenario** — 2–3 sentences describing the full business process for this row: who is involved, what they do, what data goes in, and what the system should produce.
- Example: `"A system developer submits a salary review request. HR checks eligibility and finds a current salary freeze. The system blocks the raise and returns the original salary unchanged."`

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

**Covers** — condition test case IDs that combine to form this scenario, format `CX-TCxx`:
- `C1` = Condition 1 (from the C1/C2/C3 IDs assigned in Step 1)
- `TC02` = test case 02 from that condition's unit test case table
- List all conditions: `C1-TC03 + C2-TC01 + C3-TC02`

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
| TS-01 | Developer receives standard raise | A system developer submits for annual review. HR confirms eligibility. System applies the 7% raise rate to current salary. | System Developer | 7% | Eligible | C1-TC02 + C2-TC01 | Raise applied — salary increases by 7% |
| TS-02 | Developer frozen — raise blocked | A system developer submits for review but is on salary freeze. The system blocks the raise regardless of the role's rate. | System Developer | 7% | Not Eligible | C1-TC02 + C2-TC02 | No raise — salary unchanged, freeze reason shown |
| TS-03 | Tester receives highest raise | A QA tester eligible for the highest standard raise rate of 10% submits for annual review. System applies full rate. | Tester | 10% | Eligible | C1-TC03 + C2-TC01 | Raise applied — salary increases by 10% |
| TS-04 | Finance staff frozen | A finance department employee on salary freeze submits for review. System blocks the raise. | Finance | 6.5% | Not Eligible | C1-TC04 + C2-TC02 | No raise — salary unchanged |



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
