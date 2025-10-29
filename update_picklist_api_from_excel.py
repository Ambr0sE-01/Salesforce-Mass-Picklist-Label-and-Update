import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
import datetime
import xml.dom.minidom as minidom

def backup_file(file_path):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak_path = file_path.with_name(file_path.name + f".bak_{ts}")
    shutil.copy(file_path, bak_path)
    print(f"[INFO] Backup created: {bak_path}")

def read_excel_mapping(excel_file):
    df = pd.read_excel(excel_file, engine="openpyxl", dtype=str)
    df = df.rename(columns=lambda c: c.strip())
    if "Label" not in df.columns or "API_Name" not in df.columns:
        raise ValueError("Excel must have columns: Label, API_Name")
    df = df.dropna(subset=["Label", "API_Name"])
    df["Label"] = df["Label"].str.strip()
    df["API_Name"] = df["API_Name"].str.strip()
    mapping = dict(zip(df["Label"], df["API_Name"]))
    print(f"[INFO] Loaded {len(mapping)} label->API mappings from Excel.")
    return mapping

def remove_namespace(tree):
    """Strip all namespaces from the XML tree in-place."""
    for elem in tree.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]  # remove namespace
    return tree

def update_picklist_api(xml_file, excel_file, output_file):
    xml_path = Path(xml_file)
    output_path = Path(output_file)
    
    # Backup original XML
    backup_file(xml_path)

    # Load Excel mapping
    mapping = read_excel_mapping(excel_file)

    # Parse XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Remove namespaces first
    remove_namespace(tree)

    # Find all picklist values
    value_tags = root.findall(".//value")
    updated_count = 0
    for val in value_tags:
        label_el = val.find("label")
        fullName_el = val.find("fullName")
        if label_el is not None and fullName_el is not None:
            label_text = label_el.text.strip()
            if label_text in mapping:
                old_api = fullName_el.text.strip()
                new_api = mapping[label_text]
                if old_api != new_api:
                    fullName_el.text = new_api
                    updated_count += 1

    # Pretty print XML
    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")
    # Remove empty lines
    pretty_xml = "\n".join([line for line in pretty_xml.splitlines() if line.strip()])

    # Save output
    output_path.write_text(pretty_xml, encoding="utf-8")
    print(f"[SUCCESS] Updated {updated_count} API names in picklist.")
    print(f"[INFO] Output saved to {output_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update Salesforce picklist API names from Excel")
    parser.add_argument("--xml", required=True, help="Path to picklist XML file (Account.object, etc.)")
    parser.add_argument("--excel", required=True, help="Path to Excel file with Label & API_Name columns")
    parser.add_argument("--out", required=True, help="Path to save updated XML file")

    args = parser.parse_args()
    update_picklist_api(args.xml, args.excel, args.out)
