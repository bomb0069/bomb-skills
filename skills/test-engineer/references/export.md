# Export: Save Test Cases to Excel

When the user confirms they want to save to Excel, generate and run a Python script using `openpyxl` to produce a `.xlsx` file.

## Sheet Structure

| Sheet order | Sheet name | Content |
|---|---|---|
| 1 | `test-scenarios` | **Condition Summary** (top) + Combined Test Scenarios table (TS-xx or SJ-xx) |
| 2+ | `{CX}-{ConditionName}` | Unit Test Cases (TC-xx or ST-xx) + Business Test Cases (BT-xx) for that condition |

**Sheet naming rules:**
- Test scenarios sheet always first, always named `test-scenarios`
- Condition sheets named as `C1-Department`, `C2-Eligibility`, `C3-FileSize` — condition ID + short condition name
- Max 31 characters per sheet name (Excel limit) — truncate condition name if needed
- Replace spaces with `-`, strip special characters

### Condition Summary Section (top of `test-scenarios` sheet)

Before the scenarios table, output a condition summary block:

| Column | Content |
|---|---|
| ID | `C1`, `C2`, `C3`… |
| Condition Name | Full condition name |
| Type | `EP`, `BVA`, `STT`, `Business Rule`, etc. |
| Partitions / Values | All valid + invalid partitions or boundary points (comma-separated) |
| Test Technique | Which technique was applied (`Equivalence Partitioning`, `Boundary Value Analysis`, `State Transition Testing`) |

After the condition summary rows, leave **one blank row**, then a bold label row `"Test Scenarios"`, then the scenarios table headers and rows.

## How to Generate

1. After the user confirms Excel export, generate a Python script that embeds the test data
2. Run the script with `python3`
3. Save the file as `test-cases/{requirement-name}.xlsx` (create `test-cases/` folder if needed)
4. Confirm the saved path to the user

## Python Script Template

```python
import subprocess, sys

# Ensure openpyxl is available
try:
    import openpyxl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl", "-q"])
    import openpyxl

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os

wb = Workbook()

# ── Helper: style a header row ──────────────────────────────────────────────
HEADER_FILL = PatternFill("solid", fgColor="2E75B6")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
ALT_FILL    = PatternFill("solid", fgColor="D9E1F2")
THIN        = Side(style="thin", color="AAAAAA")
BORDER      = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def style_sheet(ws, headers, rows):
    """Write headers + rows, apply styling, auto-fit column widths."""
    ws.append(headers)
    for cell in ws[1]:
        cell.font    = HEADER_FONT
        cell.fill    = HEADER_FILL
        cell.border  = BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for i, row in enumerate(rows, start=2):
        ws.append(row)
        fill = ALT_FILL if i % 2 == 0 else PatternFill()
        for cell in ws[i]:
            cell.fill      = fill
            cell.border    = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    # Auto-fit column widths (capped at 60)
    for col_idx, header in enumerate(headers, start=1):
        col_letter = get_column_letter(col_idx)
        max_len = len(str(header))
        for row in ws.iter_rows(min_col=col_idx, max_col=col_idx):
            for cell in row:
                if cell.value:
                    max_len = max(max_len, min(len(str(cell.value)), 60))
        ws.column_dimensions[col_letter].width = max_len + 4
    ws.row_dimensions[1].height = 30

# ── Sheet 1: test-scenarios ───────────────────────────────────────────────────
ws_ts = wb.active
ws_ts.title = "test-scenarios"

SECTION_FONT  = Font(bold=True, size=12)
SUMMARY_FILL  = PatternFill("solid", fgColor="1F4E79")   # dark blue for summary header
SUMMARY_FONT  = Font(bold=True, color="FFFFFF", size=11)

# ── Part A: Condition Summary ────────────────────────────────────────────────
ws_ts.append(["Condition Summary"])
ws_ts[ws_ts.max_row][0].font = SECTION_FONT

summary_headers = ["ID", "Condition Name", "Type", "Partitions / Values", "Test Technique"]
ws_ts.append(summary_headers)
for cell in ws_ts[ws_ts.max_row]:
    cell.font      = SUMMARY_FONT
    cell.fill      = SUMMARY_FILL
    cell.border    = BORDER
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

summary_rows = [
    # ["C1", "Department", "EP", "General, System Developer, IT Support, Finance, HR, Other", "Equivalence Partitioning"],
    # ["C2", "Performance Rating", "EP", "Outstanding (1), Good (2), Average (3), Below Average (4)", "Equivalence Partitioning"],
]

for i, row in enumerate(summary_rows, start=1):
    ws_ts.append(row)
    fill = ALT_FILL if i % 2 == 0 else PatternFill()
    for cell in ws_ts[ws_ts.max_row]:
        cell.fill      = fill
        cell.border    = BORDER
        cell.alignment = Alignment(vertical="top", wrap_text=True)

ws_ts.append([])  # blank separator

# ── Part B: Test Scenarios ────────────────────────────────────────────────────
ws_ts.append(["Test Scenarios"])
ws_ts[ws_ts.max_row][0].font = SECTION_FONT

ts_headers = ["ID", "Scenario Name", "Business Scenario",
              # {condition columns — expand as needed}
              "C1: Department", "Raise Rate (%)", "C2: Eligibility",
              "Covers", "Expected Output"]

ts_rows = [
    # ["TS-01", "scenario name", "business story...", "value", "value", "value", "C1-BT01+C2-BT01", "outcome..."],
]

# Write ts headers
ws_ts.append(ts_headers)
for cell in ws_ts[ws_ts.max_row]:
    cell.font      = HEADER_FONT
    cell.fill      = HEADER_FILL
    cell.border    = BORDER
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

for i, row in enumerate(ts_rows, start=2):
    ws_ts.append(row)
    fill = ALT_FILL if i % 2 == 0 else PatternFill()
    for cell in ws_ts[ws_ts.max_row]:
        cell.fill      = fill
        cell.border    = BORDER
        cell.alignment = Alignment(vertical="top", wrap_text=True)

# Auto-fit all columns in test-scenarios sheet
all_headers = summary_headers + ts_headers
for col_idx in range(1, max(len(summary_headers), len(ts_headers)) + 1):
    col_letter = get_column_letter(col_idx)
    max_len = 10
    for row in ws_ts.iter_rows(min_col=col_idx, max_col=col_idx):
        for cell in row:
            if cell.value:
                max_len = max(max_len, min(len(str(cell.value)), 60))
    ws_ts.column_dimensions[col_letter].width = max_len + 4

# ── Condition sheets ─────────────────────────────────────────────────────────
# One sheet per condition. Each sheet has two sections:
# 1) Unit Test Cases (TC-xx / ST-xx)
# 2) Business Test Cases (BT-xx)
# Separated by a blank row and a section label row.

def write_condition_sheet(wb, sheet_name, unit_headers, unit_rows, biz_headers, biz_rows):
    ws = wb.create_sheet(title=sheet_name)

    # Section label: Unit Test Cases
    ws.append(["Unit Test Cases"])
    ws[ws.max_row][0].font = Font(bold=True, size=12)
    ws.append(unit_headers)
    for cell in ws[ws.max_row]:
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for i, row in enumerate(unit_rows):
        ws.append(row)
        fill = ALT_FILL if i % 2 == 0 else PatternFill()
        for cell in ws[ws.max_row]:
            cell.fill = fill
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    ws.append([])  # blank separator

    # Section label: Business Test Cases
    ws.append(["Business Test Cases"])
    ws[ws.max_row][0].font = Font(bold=True, size=12)
    ws.append(biz_headers)
    for cell in ws[ws.max_row]:
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for i, row in enumerate(biz_rows):
        ws.append(row)
        fill = ALT_FILL if i % 2 == 0 else PatternFill()
        for cell in ws[ws.max_row]:
            cell.fill = fill
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    # Auto-fit
    for col_idx in range(1, max(len(unit_headers), len(biz_headers)) + 1):
        col_letter = get_column_letter(col_idx)
        max_len = 10
        for row in ws.iter_rows(min_col=col_idx, max_col=col_idx):
            for cell in row:
                if cell.value:
                    max_len = max(max_len, min(len(str(cell.value)), 60))
        ws.column_dimensions[col_letter].width = max_len + 4

# Example condition sheet — C1: Department
write_condition_sheet(
    wb,
    sheet_name="C1-Department",
    unit_headers=["ID", "Name", "Description", "Input: Department", "Expected Output"],
    unit_rows=[
        # ["TC-01", "General dept", "...", "General", "Valid - accepted"],
    ],
    biz_headers=["ID", "Name", "Description", "Input: Department", "Input: Raise Rate", "Expected Output"],
    biz_rows=[
        # ["BT-01", "Developer standard review", "...", "System Developer", "7%", "Valid - raise 7%"],
    ]
)

# ── Save ─────────────────────────────────────────────────────────────────────
os.makedirs("test-cases", exist_ok=True)
output_path = "test-cases/{requirement-name}.xlsx"
wb.save(output_path)
print(f"Saved: {output_path}")
```

## Rules for Generating the Script

When generating the actual script:
- Replace `{requirement-name}` with a slugified version of the requirement name (lowercase, hyphens, no spaces)
- Fill in `summary_rows` with one row per condition: ID, name, type, all partitions/values joined by `, `, technique name
- Fill in the actual column headers and row data from the generated test cases
- For STT: `test-scenarios` sheet contains SJ-xx journeys; condition sheets contain ST-xx transition test cases + BT-xx
- Add one `write_condition_sheet(...)` call per condition (C1, C2, C3…)
- Keep all data as Python string literals embedded in the script
- Run with `python3 {script_path}` and confirm the saved file path
