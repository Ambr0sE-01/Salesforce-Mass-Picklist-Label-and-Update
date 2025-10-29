****Salesforce Picklist Auto-Updater****



_**Overview**_

This project automates the process of updating picklist values in Salesforce fields using a Python script. Instead of manually editing each picklist value (which can be tedious for large datasets), this solution leverages metadata and an Excel reference file to update API names efficiently.

_**Why This Project?**_

Manually updating picklist values in Salesforce is simple for a few entries, but consider scenarios with hundreds or thousands of values. For example:

A client requires dropdowns for Shipping, Selling, Pay By, and Invoice Address fields.
Each dropdown needs picklists for Country, State, and City.
Integration with InforLN demands that Salesforce picklist API names match InforLN codes (e.g., United Arab Emirates → ARE).

Doing this manually for 800+ countries (and their states/cities) is time-consuming and error-prone. Users should see friendly labels like United Arab Emirates, but the backend must use correct API names for integration.

_**Solution**_

The Python script automates this process by:

Reading Salesforce metadata for the target field.
Referencing an Excel file containing:

Label (user-friendly name)
API Name (integration code)


Updating the metadata with correct API names and generating a new metadata file ready for deployment.


_**Prerequisites_**

Before running the script, ensure you have:


_**Salesforce Metadata**_

Export the metadata of the field containing the old picklist values.


Excel Reference File

Two columns only:

Label → Picklist value label
API Name → Corresponding API name/code


Example:
Label,API Name
United Arab Emirates,ARE
India,IND





Python Environment

Python 3.x installed
Required libraries (install via pip install -r requirements.txt if provided)




Directory Structure
project-root/
│
├── metadata/          # Original Salesforce metadata files
├── excel/             # Excel file with Label and API Names
├── script.py          # Python automation script
└── README.md          # Project documentation


How It Works

Place the Salesforce metadata file in the metadata/ folder.
Place the Excel file in the excel/ folder.
Run the Python script:
Shellpython script.pyShow more lines

The script will:

Parse the metadata XML.
Match labels with API names from Excel.
Generate an updated metadata file for deployment.




Benefits

Eliminates manual effort for large picklists.
Ensures consistency between Salesforce and external systems (e.g., InforLN).
Reduces human error during integration setup.


Notes

Ensure the Excel file has only two columns: Label and API Name.
Keep files in the correct directories before running the script.
Validate the updated metadata before deploying to Salesforce.


Future Enhancements

Support for multiple fields in one run.
Integration with Salesforce Metadata API for direct updates.
Error handling and logging improvements.
