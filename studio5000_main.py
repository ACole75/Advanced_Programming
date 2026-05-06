import os
from studio5000_parser import parse_docx
from studio5000_formatter import format_studio5000

def convert(input_path: str, outdir: str, seq_name: str) -> tuple[str, int]:
    """
    Convert FDS document to Studio 5000 ASCII format.
    Only processes STEP information.
    """
    records = parse_docx(input_path)
    # Use the base name of the input file for the output if a user defined sequence name is not provided
    base = seq_name or os.path.splitext(os.path.basename(input_path))[0]
    output_file = os.path.join(outdir, f"{base}_steps.txt")
    
    os.makedirs(outdir, exist_ok=True)
    # Write formatted output with ASCII encode
    with open(output_file, 'w', encoding="ascii", errors="ignore") as f:
        for rec in records:
            formatted = format_studio5000(rec, base)
            f.write(formatted + "\n")
    
    return output_file, len(records)
