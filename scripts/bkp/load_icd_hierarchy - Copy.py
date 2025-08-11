import pandas as pd
from pathlib import Path


def load_icd_hierarchy():
    print("Loading ICD hierarchy...")

    # Set base directories dynamically relative to script's location
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / 'data'
    OUTPUT_DIR = BASE_DIR / 'output'

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Source File
    source_file = DATA_DIR / 'icd10cm_order.txt'  # ICD Code File

    # Read file without indent
    cols = ['ORDER', 'ICD_CODE', 'DESCRIPTION']
    df = pd.read_fwf(source_file, colspecs=[(0, 5), (6, 14), (15, 70)], names=cols)

    # Infer indent by code length (e.g. A00 = 3 chars -> 0, A000 = 4 chars -> 1)
    df['INDENT_LEVEL'] = df['ICD_CODE'].apply(lambda x: len(str(x)) - 3)

    # Now build parent-child hierarchy
    parent_stack = {}
    parent_codes = []

    for idx, row in df.iterrows():
        indent = row['INDENT_LEVEL']

        # Remove deeper levels if moving up
        keys_to_remove = [key for key in parent_stack if key >= indent]
        for key in keys_to_remove:
            del parent_stack[key]

        # Set parent code
        if indent == 0:
            parent_codes.append('')
        else:
            possible_parents = [parent_stack[level] for level in parent_stack if level < indent]
            parent_codes.append(possible_parents[-1] if possible_parents else '')

        # Update stack with current code
        parent_stack[indent] = row['ICD_CODE']

    # Add parent code column
    df['PARENT_CODE'] = parent_codes

    # Top-level code column
    df['TOP_LEVEL_CODE'] = df.apply(lambda x: x['ICD_CODE'] if x['INDENT_LEVEL'] == 0 else '', axis=1)
    df['TOP_LEVEL_CODE'] = df['TOP_LEVEL_CODE'].replace('', pd.NA).ffill()

    # Save output
    output_file = OUTPUT_DIR / 'icd10_hierarchy.csv'
    df.to_csv(output_file, index=False)

    print(f"✅ Hierarchy rebuilt correctly with inferred indent levels. Output saved to {output_file}")


# Only run if directly called (good practice if reused elsewhere)
if __name__ == "__main__":
    load_icd_hierarchy()
