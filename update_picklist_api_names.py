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

def update_picklist_api_names(xml_file, excel_dir, output_file, report_file, backup=False):
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
            df = pd.read_excel(os.path.join(excel_dir, excel_file), engine="openpyxl")
            if "Label" not in df.columns or "API_Name" not in df.columns:
                print(f"[WARN] Skipping {excel_file}, missing required columns (Label, API_Name)")
                continue
            for _, row in df.iterrows():
                label = str(row["Label"]).strip().lower()   # lowercase for matching
                api_name = str(row["API_Name"]).strip()
                mapping[label] = api_name

    print(f"[INFO] Loaded {len(mapping)} mappings from Excel")

    # Track updates
    changes = []
    unmapped = []

    # Iterate over picklist values
    for val in root.findall(".//sf:valueSet/sf:valueSetDefinition/sf:value", ns):
        api_name_el = val.find("sf:fullName", ns)
        label_el = val.find("sf:label", ns)

        if label_el is not None and api_name_el is not None:
            label = label_el.text.strip()
            key = label.lower()
            if key in mapping:
                new_api = mapping[key]
                old_api = api_name_el.text.strip() if api_name_el.text else ""
                if old_api != new_api:
                    api_name_el.text = new_api
                    changes.append((label, old_api, new_api))
        else:
            # If no <fullName>, just log it — don’t create new
            if label_el is not None:
                unmapped.append(label_el.text.strip())

    # Strip namespace before saving
    tree = remove_namespace(tree)

    # Save updated XML
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"[INFO] Updated XML saved at {output_file}")

    # Save report for changed values
    if changes:
        df_report = pd.DataFrame(changes, columns=["Label", "Old_API_Name", "New_API_Name"])
        df_report.to_csv(report_file, index=False)
        print(f"[INFO] Report saved at {report_file}")
    else:
        print("[INFO] No changes made (API names already matched).")

    # Save unmapped values report
    if unmapped:
        df_unmapped = pd.DataFrame(unmapped, columns=["Unmapped_Labels_No_FullName"])
        unmapped_file = report_file.replace(".csv", "_unmapped.csv")
        df_unmapped.to_csv(unmapped_file, index=False)
        print(f"[INFO] Unmapped labels saved at {unmapped_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Salesforce picklist API names from Excel mapping")
    parser.add_argument("--xml", required=True, help="Path to input XML metadata file (e.g., Account.object)")
    parser.add_argument("--excel_dir", required=True, help="Folder containing Excel mapping files")
    parser.add_argument("--out", required=True, help="Path to save updated XML")
    parser.add_argument("--report", required=True, help="Path to save CSV change report")
    parser.add_argument("--backup", action="store_true", help="Backup original XML before updating")

    args = parser.parse_args()
    update_picklist_api_names(args.xml, args.excel_dir, args.out, args.report, args.backup)
