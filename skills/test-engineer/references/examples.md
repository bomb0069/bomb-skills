# test-engineer Skill — Examples

## Example: Basic Numeric BVA with Business Test Data

**User prompt**: "Age field accepts 18 to 60 (integer). This is for a car insurance application targeting working adults."

**Output**:

**Input Analysis**
- Field: Age
- Type: Numeric (integer)
- Range: 18 to 60
- Business context: Car insurance for working adults

**Unit Test Cases (BVA boundaries)**

| ID | Name | Description | Input: Age | Expected Output |
|---|---|---|---|---|
| TC-01 | Below minimum age | Enter age 17, one below the minimum of 18. System should reject. | 17 | Invalid - rejected |
| TC-02 | Minimum age boundary | Enter age 18, the lowest allowed. System should accept. | 18 | Valid - accepted |
| TC-03 | Above minimum age | Enter age 19, just above minimum. System should accept. | 19 | Valid - accepted |
| TC-04 | Below maximum age | Enter age 59, just below maximum of 60. System should accept. | 59 | Valid - accepted |
| TC-05 | Maximum age boundary | Enter age 60, the highest allowed. System should accept. | 60 | Valid - accepted |
| TC-06 | Above maximum age | Enter age 61, one above maximum of 60. System should reject. | 61 | Invalid - rejected |

**Business Test Cases (for acceptance/integration testing)**

| ID | Name | Description | Input: Age | Expected Output |
|---|---|---|---|---|
| BT-01 | New driver | Age 22, a typical young driver just starting to drive. Common first-time insurance buyer. | 22 | Valid - accepted |
| BT-02 | Young professional | Age 28, early career working adult. High volume segment for car insurance. | 28 | Valid - accepted |
| BT-03 | Mid-career family | Age 38, established professional with family. Typical policyholder. | 38 | Valid - accepted |
| BT-04 | Senior professional | Age 50, experienced worker. May have different risk profile. | 50 | Valid - accepted |
| BT-05 | Near-retirement | Age 58, close to maximum age. Important to verify late-career coverage. | 58 | Valid - accepted |

## Example: Single-Bound Requirement

**User prompt**: "The score field must be at least 0. Generate BVA test cases."

**Output**:

**Input Analysis**
- Field: Score
- Type: Numeric
- Lower limit: 0
- Upper limit: **not specified**

I found a lower limit of **0**, but no upper limit was provided. To generate complete BVA test cases, I need both boundaries.

*[Then call `AskUserQuestion` with header "Upper limit", question "What is the maximum allowed value for the score field?", and options: "100" (common for percentage-like scores), "999" (three-digit maximum), "10,000" (large-range score field)]*

## Example: Ambiguous Age Precision

**User prompt**: "Registration requires users to be not over 65 years old. Create BVA test cases."

**Output**:

**Input Analysis**
- Field: Age
- Constraint: not over 65 years old
- Precision: **unclear — need to clarify**

Before I generate test cases, I need to clarify the **minimum unit of age data** in your system, because it changes the boundary values significantly:

| If the input is... | Step size | Boundary just below 65 | Boundary at 65 | Boundary just above 65 |
|---|---|---|---|---|
| Age as whole years (integer) | 1 year | 64 | 65 | 66 |
| Birthdate (year-month-day) | 1 day | 64 years, 11 months, 29 days | Exactly 65 years | 65 years, 0 months, 1 day |

*[Then call `AskUserQuestion` with header "Age input", question "How does your system capture age?", and options: "Whole number" (user enters age as integer, step = 1 year), "Birthdate" (user enters birthdate, system calculates age, step = 1 day)]*

## Example: Ambiguous Money Precision

**User prompt**: "Daily deposit limit is not over 30,000 baht. Generate BVA test cases."

**Output**:

**Input Analysis**
- Field: Deposit amount
- Constraint: not over 30,000 baht
- Precision: **unclear — need to clarify**

Before I generate test cases, I need to clarify the **minimum unit of money** your system accepts:

| If the minimum unit is... | Boundary just below 30,000 | At 30,000 | Just above 30,000 |
|---|---|---|---|
| 0.01 (satang) | 29,999.99 | 30,000.00 | 30,000.01 |
| 1 (whole baht) | 29,999 | 30,000 | 30,001 |
| 100 (hundred baht) | 29,900 | 30,000 | 30,100 |

*[Then call `AskUserQuestion` with header "Precision", question "What is the smallest deposit amount the system accepts?", and options: "0.01 (satang)" (boundary below 30,000 = 29,999.99), "1 (whole baht)" (boundary below 30,000 = 29,999), "100 (hundred baht)" (boundary below 30,000 = 29,900)]*

## Example: Multiple Independent Questions

**User prompt**: "Registration form: user must be not over 65 years old, and the registration fee is not over 5,000 baht. Generate BVA test cases."

**Output**:

**Input Analysis**
- Field 1: Age — constraint: not over 65, precision: **unclear**
- Field 2: Registration fee — constraint: not over 5,000 baht, precision: **unclear**

I need to clarify a few things before generating test cases.

*[Then call `AskUserQuestion` with TWO questions in a single call — each becomes a tab:
- Tab 1 header "Age", question "How does your system capture age?", options: "Whole number" (integer, step = 1 year), "Birthdate" (system calculates, step = 1 day)
- Tab 2 header "Fee", question "What is the smallest fee amount?", options: "0.01 (satang)" (boundary = 4,999.99), "1 (whole baht)" (boundary = 4,999), "100 (hundred baht)" (boundary = 4,900)
]*

## Example: Birthdate-Based Age (Calculated Field)

**User prompt**: "Registration requires users to be between 18 and 65 years old. The user enters their birthdate and the system calculates age. Generate BVA test cases."

**Output**:

**Input Analysis**
- Field: Age (calculated from birthdate)
- Type: Calculated — direct input is birthdate, indirect input is transaction date
- Range: 18 to 65 years old
- Step: 1 day

**BVA Test Cases**

Assuming transaction date = **2026-03-28**:

| ID | Name | Description | Input: Birthdate (direct) | Input: Transaction Date (indirect) | Calculated: Age | Expected Output |
|---|---|---|---|---|---|---|
| TC-01 | Below minimum age | Born 1 day after cutoff. Not yet 18. | 2008-03-29 | 2026-03-28 | 17y 364d | Invalid - rejected |
| TC-02 | Minimum age boundary | Born exactly 18 years ago. | 2008-03-28 | 2026-03-28 | 18y 0d | Valid - accepted |
| TC-03 | Above minimum age | Born 1 day before cutoff. Just turned 18. | 2008-03-27 | 2026-03-28 | 18y 1d | Valid - accepted |
| TC-04 | Below maximum age | Born 1 day after cutoff. Not yet 65. | 1961-03-29 | 2026-03-28 | 64y 364d | Valid - accepted |
| TC-05 | Maximum age boundary | Born exactly 65 years ago. | 1961-03-28 | 2026-03-28 | 65y 0d | Valid - accepted |
| TC-06 | Above maximum age | Born 1 day before cutoff. Over 65. | 1961-03-27 | 2026-03-28 | 65y 1d | Invalid - rejected |
