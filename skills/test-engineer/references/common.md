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

## Business Test Data (Step 4)

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
