import argparse
import os
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import shutil

def remove_namespace(tree):
    """Remove XML namespaces so Salesforce metadata looks clean."""
    for elem in tree.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]  # strip namespace prefix
    return tree

def update_picklist_labels(xml_file, excel_dir, output_file, report_file, backup=False):
    # Backup original file if asked
    if backup:
        backup_file = xml_file + ".bak"
        shutil.copy(xml_file, backup_file)
        print(f"[INFO] Backup created: {backup_file}")

    # Load XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Namespace for parsing (used only for reading, will be stripped before saving)
    ns = {"sf": "http://soap.sforce.com/2006/04/metadata"}

    # Build mapping from all Excel files in folder 
    mapping = {}
    for excel_file in os.listdir(excel_dir):
        if excel_file.endswith(".xlsx"):
            # ✅ force openpyxl engine
            df = pd.read_excel(os.path.join(excel_dir, excel_file), engine="openpyxl")
            if "API_Name" not in df.columns or "Label" not in df.columns:
                print(f"[WARN] Skipping {excel_file}, missing required columns (API_Name, Label)")
                continue
            for _, row in df.iterrows():
                mapping[str(row["API_Name"]).strip()] = str(row["Label"]).strip()

    print(f"[INFO] Loaded {len(mapping)} mappings from Excel")

    # Track updates
    changes = []

    # Iterate over picklist values
    for val in root.findall(".//sf:valueSet/sf:valueSetDefinition/sf:value", ns):
        api_name = val.find("sf:fullName", ns).text
        label_el = val.find("sf:label", ns)

        if api_name in mapping:
            old_label = label_el.text if label_el is not None else ""
            new_label = mapping[api_name]
            if old_label != new_label:
                if label_el is None:
                    label_el = ET.SubElement(val, "label")
                label_el.text = new_label
                changes.append((api_name, old_label, new_label))

    # Strip namespace before saving
    tree = remove_namespace(tree)

    # Save updated XML
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"[INFO] Updated XML saved at {output_file}")

    # Save report
    if changes:
        df_report = pd.DataFrame(changes, columns=["API_Name", "Old_Label", "New_Label"])
        df_report.to_csv(report_file, index=False)
        print(f"[INFO] Report saved at {report_file}")
    else:
        print("[INFO] No changes made (labels already matched).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Salesforce picklist labels from Excel mapping")
    parser.add_argument("--xml", required=True, help="Path to input XML metadata file (e.g., Account.object)")
    parser.add_argument("--excel_dir", required=True, help="Folder containing Excel mapping files")
    parser.add_argument("--out", required=True, help="Path to save updated XML")
    parser.add_argument("--report", required=True, help="Path to save CSV change report")
    parser.add_argument("--backup", action="store_true", help="Backup original XML before updating")

    args = parser.parse_args()
    update_picklist_labels(args.xml, args.excel_dir, args.out, args.report, args.backup)
