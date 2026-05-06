import re
from typing import List, Dict, Optional
from docx import Document
from dataclasses import dataclass, field
from studio5000_formatter import format_string

# Step Token definition, matching typical FDS step formats
STEP_TOKEN_RE = re.compile(r"^\s*(>?)(S?\d+(\s*-\s*\d+)?|\d+(\s*-\s*\d+)?)\s*$", re.IGNORECASE)

# Step token must be a valid integer or numeric range, and may also be prefixed with an 's'
def Step_Token(s: str) -> bool:
    return bool(STEP_TOKEN_RE.match((s or "").strip()))

# Detect devices from plant reference, physical devices are identified by their location in table and an underscore
def extract_dev_token(plant_ref: str) -> List[str]:
    if not plant_ref:
        return []
    token_re = re.compile(r"\b[A-Z]{2,}(?:_[A-Z0-9]{2,})+\b")
    tokens = token_re.findall(plant_ref)

# Remove any duplicates    
    seen = set()
    out = []
    for t in tokens:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out

# Definition for step record
@dataclass
class StepRecord:
    step: str = "?"
    desc: str = ""
    evaluation: str = ""
    result: str = ""
    cont: List[str] = field(default_factory=list)
    devices: List[str] = field(default_factory=list)

# Check to see if a steps table is present in the input file
def table_is_fds_steps_table(table) -> bool:
    if not table.rows:
        return False
    header = " | ".join(format_string(c.text).lower() for c in table.rows[0].cells)
    return ("step" in header) and ("description" in header)

# Mapping of column names and exclusion for blanks
def map_columns(header_cells) -> Dict[str, Optional[int]]:
    header = [format_string(c.text).lower() for c in header_cells]

# Find required columns by keyword identification and map column name
    def find_col(*needles):
        for i, h in enumerate(header):
            if any(n in h for n in needles):
                return i
        return None

# Return column mapping
    return {
        "step": find_col("step"),
        "desc": find_col("description"),
        "evaluation": find_col("evaluation"),
        "result": find_col("result"),
    }

# Main parse logic handle step records 
def parse_docx(docx_path: str) -> List[StepRecord]:
    records: List[StepRecord] = []
    current: Optional[StepRecord] = None

    doc = Document(docx_path)

    for table in doc.tables:
        if not table_is_fds_steps_table(table):
            continue

        colmap = map_columns(table.rows[0].cells)

# Retrieve cell text and format it to remove any whitespace and non ascii compatible characters
        def cell_text(row, idx):
            if idx is None:
                return ""
            if idx >= len(row.cells):
                return ""
            return format_string(row.cells[idx].text)

# Run through table rows and extract the step information to create new step records
        for r in range(1, len(table.rows)):
            row = table.rows[r]

            step_cell = cell_text(row, colmap["step"])
            desc_cell = cell_text(row, colmap["desc"])
            eval_cell = cell_text(row, colmap["evaluation"])
            result_cell = cell_text(row, colmap["result"])

            row_has_any = any(x.strip() for x in [step_cell, desc_cell, eval_cell, result_cell])
            if not row_has_any:
                continue

            if step_cell.strip() and Step_Token(step_cell):
                # Skip stages (steps starting with 'S' which are stage columns, not actual steps)
                step_stripped = step_cell.strip().upper()
                if step_stripped.startswith('S'):
                    continue
                
                # Start a new record 
                if current:
                    records.append(current)

                current = StepRecord(
                    step=step_cell.strip(),
                    desc=desc_cell.strip(),
                    evaluation=eval_cell.strip(),
                    result=result_cell.strip(),
                    cont=[]
                )

            else:
               
                continue

        if current:
            records.append(current)
            current = None

    return records
