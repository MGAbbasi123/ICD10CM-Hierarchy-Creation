📖 ICD-10-CM Code Processor
📑 Overview
This project processes ICD-10-CM (International Classification of Diseases, 10th Revision, Clinical Modification) code data. It reads source files containing ICD codes, reconstructs a hierarchical structure based on code indent levels, maps each code to its corresponding medical chapter and range, and outputs clean, structured CSV files for further use.

📁 Project Structure
icd10/
├── data/
│   ├── icd10cm_order_2020.txt         # Source ICD-10-CM codes file
│   └── icd10_chapters.csv             # Chapter definitions with code ranges
├── output/
│   ├── icd10_hierarchy.csv            # Generated hierarchy with indent levels and parent codes
│   └── icd10_hierarchy_with_chapters.csv # Hierarchy with mapped chapters and ranges
├── _1_load_icd_hierarchy.py           # Script to build the ICD hierarchy
├── _2_mark_chapters.py                # Script to map codes to chapters and ranges
├── _3_main.py                         # Main orchestrator script to run the entire workflow
└── README.md                          # Project documentation (this file)
📝 Script Descriptions
📄 _1_load_icd_hierarchy.py
Purpose: Reads raw ICD-10-CM code file, infers indent levels based on code length, and reconstructs parent-child hierarchical relationships.

Output: output/icd10_hierarchy.csv

Key Functions:

load_icd_hierarchy(): Processes the raw file, builds hierarchy columns (INDENT_LEVEL, PARENT_CODE, TOP_LEVEL_CODE), and saves results.

📄 _2_mark_chapters.py
Purpose: Loads the processed hierarchy, assigns each ICD code to a chapter based on predefined code ranges, and adds the chapter’s name and range.

Output: output/icd10_hierarchy_with_chapters.csv

Key Functions:

mark_chapters(): Maps codes to their medical chapters and saves the annotated CSV.

📄 _3_main.py
Purpose: Orchestrates the workflow by calling both _1_load_icd_hierarchy and _2_mark_chapters scripts sequentially.

📦 File Path Handling
This project uses dynamic, relative file paths for better portability:

All data files are placed inside data/

All outputs are saved in output/

File paths are constructed using Python’s os and pathlib libraries to remain flexible across environments (suggested improvement).

Example:


from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
source_file = base_dir / 'data' / 'icd10cm_order_2020.txt'
✅ How to Run
Ensure Python 3.x and pandas are installed.

Place your source files in the data/ folder.

Open terminal in the project directory.

Run the main script:


python _3_main.py