import re
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from studio5000_parser import StepRecord

def format_string(s: str) -> str:
    """
    Format the string by removing non-ASCII characters and any whitespace.
    """
    if not s:
        return ""
    # Remove non-ASCII characters and collapse whitespace
    cleaned = ''.join(c for c in s if ord(c) < 128)
    return ' '.join(cleaned.split())

def parse_evaluation(eval_text: str) -> List[tuple[str, str]]:
    """
    Parse evaluation text into pairs for device/instruction
    Returns a list of device, instruction tuples
    """
    if not eval_text:
        return []
    
    # Split by common delimiters (AND, commas, etc.) All common within FDS specs
    parts = re.split(r'(?:AND|,|\s{2,})', eval_text.strip(), flags=re.IGNORECASE)
    
    conditions = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Check if ending with OFF, ON, CLOSE or OPEN and assign instruction type accordingly
        if part.upper().endswith(' OFF'):
            device = part[:-4].strip()
            instruction = 'XIC'
        elif part.upper().endswith(' ON'):
            device = part[:-3].strip()
            instruction = 'XIO'
        elif part.upper().endswith(' OPEN'):
            device = part[:-5].strip()
            instruction = 'XIO'
        elif part.upper().endswith(' CLOSE'):
            device = part[:-5].strip()
            instruction = 'XIC'
        else:
            # Default to XIC if not explicitly matching one of the types above, this is both a reasonable assumption and a way to prevent errors from unrecognized formats
            device = part
            instruction = 'XIC'
        
        if device:
            conditions.append((device, instruction))
    
    return conditions

def format_studio5000(rec, seq_name: str) -> str:
    """
    Convert StepRecords to ASCII (PLC ladder) format.
    """
    instructions = []
    
    # Step number is always the first insutrction on a ladder rung, and takes the form of an EQU instruction
    instructions.append(f"EQU {seq_name}.Step {rec.step}")
    
    # Parse evaluation column for XIC/XIO conditions, which relate to device logic
    if rec.evaluation:
        conditions = parse_evaluation(rec.evaluation)
        for device, instr_type in conditions:
            instructions.append(f"{instr_type} {device}")
    
    # Always add GRT instruction for step time, since this is standard FDS functionality, hardcode with 2 second time
    instructions.append(f"GRT {seq_name}.StepTime.Seconds 2")
    
    # Parse 'result' column for the addition of step transitions which use a MOV instruction
    if rec.result:
        result_value = rec.result.strip()
        if result_value:
            instructions.append(f"MOV {result_value} {seq_name}.Goto")
    
    return " ".join(instructions)
