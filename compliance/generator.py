import json
import os
from datetime import datetime

def generate_report(results, output_dir="reports", file_format="json"):
    """
    Generate compliance report from analysis results.
    
    Args:
        results (list): List of dicts with compliance results from LLM.
        output_dir (str): Directory to save reports.
        file_format (str): "json" or "txt".
        
    Returns:
        str: Path to the saved report.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(output_dir, f"compliance_report_{timestamp}.{file_format}")

    if file_format == "json":
        with open(file_path, "w") as f:
            json.dump(results, f, indent=4)
    else:
        raise ValueError("Unsupported file format. Use 'json' or 'txt'.")

    print(f"📄 Compliance report saved at: {file_path}")
    return file_path


def convert_json_to_txt(json_path, txt_path=None):
    import json, os
    
    with open(json_path, "r") as f:
        results = json.load(f)

    if txt_path is None:
        txt_path = os.path.splitext(json_path)[0] + ".txt"

    with open(txt_path, "w") as f:
        for i, r in enumerate(results, 1):
            f.write(f"--- Chunk {i} ---\n")
            
            result = r.get("result", r)  
            
            f.write(f"✅ Compliant: {result.get('compliant', 'Unknown')}\n")
            f.write(f"❌ Issue: {result.get('reason', 'N/A')}\n")
            f.write(f"💡 Suggestion: {result.get('suggestion', 'N/A')}\n\n")

    print(f"📄 TXT report saved at: {txt_path}")
    return txt_path
