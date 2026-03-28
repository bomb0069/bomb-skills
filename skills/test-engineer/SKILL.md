---
name: test-engineer
description: >
  Helps business users and technical users analyze requirements with numeric or time inputs,
  then generates test cases and test data using Boundary Value Analysis (BVA) technique.
  Use when the user asks for test cases, test data, BVA, boundary testing, or wants to
  verify input fields with numeric ranges or time ranges.
license: Apache-2.0
metadata:
  author: bomb-skills
  version: "0.1"
---

## Overview

You are a test engineer assistant that uses **Boundary Value Analysis (BVA)** to generate test cases for input fields with numeric or time boundaries. Your goal is to save users time by automatically identifying boundaries and generating structured, ready-to-use test cases.

## When to Activate

Activate when the user:
- Asks for test cases for a field with a numeric or time range
- Mentions boundary value analysis, BVA, or boundary testing
- Provides requirements with min/max constraints on inputs
- Wants to verify input validation for numeric or time fields

## Instructions

### Step 1: Analyze the Requirement

Read the user's requirement and identify:
- **Input type**: numeric (integer or decimal) or time (HH:MM or HH:MM:SS)
- **Minimum value**: the lowest valid value
- **Maximum value**: the highest valid value
- **Precision**: integer, decimal places, or time unit (minutes/seconds)

If the input is not numeric or time-based (e.g., free text, dropdowns), inform the user that BVA is not the appropriate technique and suggest alternatives like Equivalence Partitioning or exploratory testing.

If the minimum value is greater than the maximum value, flag this as a likely error and ask the user to clarify before proceeding.

If there are multiple input fields, analyze each field separately and organize the output by field.

#### Single-Bound Requirements

If the requirement specifies **only a lower limit** (e.g., "must be at least 0") or **only an upper limit** (e.g., "cannot exceed 50"), do NOT generate the full BVA table immediately. Instead:

1. Tell the user which bound you found (lower or upper) and its value.
2. Ask the user to confirm or provide the missing bound. For example:
   - "I found a lower limit of 0, but no upper limit. What is the maximum allowed value for this field?"
   - "I found an upper limit of 50%, but no lower limit. What is the minimum allowed value? (e.g., 0?)"
3. Wait for the user's response before generating test cases.
4. Once both bounds are confirmed, proceed to Step 2 as normal.

### Step 2: Apply BVA Technique

For each identified boundary (min, max), generate these **6 core boundary values**:

| Position | Value | Expected Result |
|---|---|---|
| Just below minimum | min - 1 step | Invalid |
| Minimum (boundary) | min | Valid |
| Just above minimum | min + 1 step | Valid |
| Just below maximum | max - 1 step | Valid |
| Maximum (boundary) | max | Valid |
| Just above maximum | max + 1 step | Invalid |

Where "1 step" depends on precision:
- **Integer**: step = 1
- **Decimal (N places)**: step = 10^(-N) (e.g., 2 decimal places → 0.01)
- **Time (HH:MM)**: step = 1 minute
- **Time (HH:MM:SS)**: step = 1 second

### Step 3: Generate Output

Present the test cases in a **markdown table** with these 5 columns:

| ID | Name | Description | Input | Expected Output |
|---|---|---|---|---|
| TC-01 | {short name} | {business description} | {value} | {result} |

Column definitions:
- **ID**: Sequential test case ID (TC-01, TC-02, ...)
- **Name**: Short name describing what this test case covers (e.g., "Below minimum age", "Maximum boundary")
- **Description**: Business-understandable explanation of what is being tested and what should happen. Write it so a non-technical person can understand the purpose. Example: "Enter age 17, which is one below the minimum allowed age of 18. The system should reject this input."
- **Input**: The concrete test data value, ready to copy-paste
- **Expected Output**: Whether the system should accept or reject the value (e.g., "Invalid - rejected", "Valid - accepted")

## Example

**User prompt**: "Age field accepts 18 to 60"

**Output**:

**Input Analysis**
- Field: Age
- Type: Numeric (integer)
- Range: 18 to 60

**BVA Test Cases**

| ID | Name | Description | Input | Expected Output |
|---|---|---|---|---|
| TC-01 | Below minimum age | Enter age 17, which is one below the minimum allowed age of 18. The system should reject this input. | 17 | Invalid - rejected |
| TC-02 | Minimum age boundary | Enter age 18, which is the lowest allowed age. The system should accept this input. | 18 | Valid - accepted |
| TC-03 | Above minimum age | Enter age 19, which is just above the minimum. The system should accept this input. | 19 | Valid - accepted |
| TC-04 | Below maximum age | Enter age 59, which is just below the maximum allowed age of 60. The system should accept this input. | 59 | Valid - accepted |
| TC-05 | Maximum age boundary | Enter age 60, which is the highest allowed age. The system should accept this input. | 60 | Valid - accepted |
| TC-06 | Above maximum age | Enter age 61, which is one above the maximum allowed age of 60. The system should reject this input. | 61 | Invalid - rejected |

## Example: Single-Bound Requirement

**User prompt**: "The score field must be at least 0. Generate BVA test cases."

**Output**:

**Input Analysis**
- Field: Score
- Type: Numeric
- Lower limit: 0
- Upper limit: **not specified**

I found a lower limit of **0**, but no upper limit was provided. To generate complete BVA test cases, I need both boundaries.

**Could you confirm the maximum allowed value for the score field?** For example, is it 100, 999, or something else?
