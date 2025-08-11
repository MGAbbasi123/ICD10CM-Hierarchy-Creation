import pandas as pd
from pathlib import Path


def load_icd_hierarchy():
    print("Loading ICD hierarchy...")

    # Set base directories
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / 'data'
    OUTPUT_DIR = BASE_DIR / 'output'

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Source file
    source_file = DATA_DIR / 'icd10cm_order.txt'

    # Read file with colspecs including HEADER_FLAG at position 15 (14 in 0-based index)
    cols = ['ORDER', 'ICD_CODE', 'HEADER_FLAG', 'DESCRIPTION']
    df = pd.read_fwf(source_file, colspecs=[(0, 5), (6, 14), (14, 15), (15, 77)], names=cols)

    # Clean whitespace
    df['ICD_CODE'] = df['ICD_CODE'].str.strip()
    df['DESCRIPTION'] = df['DESCRIPTION'].str.strip()

    # Infer indent by code length
    df['INDENT_LEVEL'] = df['ICD_CODE'].apply(lambda x: len(str(x)) - 3)

    # Determine max indent level dynamically
    max_indent = df['INDENT_LEVEL'].max()
    print(f"📊 Max indent level detected: {max_indent}")

    # Initialize parent stack and ancestor columns
    parent_stack = {}
    ancestor_columns = {f'LEVEL_{i}_PARENT': [] for i in range(1, max_indent + 1)}

    for _, row in df.iterrows():
        indent = row['INDENT_LEVEL']

        # Remove deeper levels if moving up
        keys_to_remove = [key for key in parent_stack if key >= indent]
        for key in keys_to_remove:
            del parent_stack[key]

        # Add ancestors for each level
        for i in range(1, max_indent + 1):
            ancestor_columns[f'LEVEL_{i}_PARENT'].append(parent_stack.get(i - 1, ''))

        # Update stack with current code
        parent_stack[indent] = row['ICD_CODE']

    # Add ancestor code columns to dataframe
    for col_name, values in ancestor_columns.items():
        df[col_name] = values

    # Build description mapping
    code_to_desc = df.set_index('ICD_CODE')['DESCRIPTION'].to_dict()

    # Add description columns paired with each parent code column
    for i in range(1, max_indent + 1):
        parent_col = f'LEVEL_{i}_PARENT'
        desc_col = f'LEVEL_{i}_DESC'
        df[desc_col] = df[parent_col].map(code_to_desc)

    # Top-level code column
    df['TOP_LEVEL_CODE'] = df.apply(lambda x: x['ICD_CODE'] if x['INDENT_LEVEL'] == 0 else '', axis=1)
    df['TOP_LEVEL_CODE'] = df['TOP_LEVEL_CODE'].replace('', pd.NA).ffill()

    # Reorder columns
    level_columns = []
    for i in range(1, max_indent + 1):
        level_columns.extend([f'LEVEL_{i}_PARENT', f'LEVEL_{i}_DESC'])

    base_columns = ['ORDER', 'ICD_CODE', 'HEADER_FLAG', 'DESCRIPTION', 'INDENT_LEVEL']
    final_columns = base_columns + level_columns + ['TOP_LEVEL_CODE']

    df = df[final_columns]

    # Preview first 10 rows
    print("\n📄 ICD-10 Hierarchy Sample Preview:")
    print(df.head(10).to_string(index=False))

    # Save output
    output_file = OUTPUT_DIR / 'icd10_hierarchy_dynamic_paired.csv'
    df.to_csv(output_file, index=False)

    print(f"\n✅ Hierarchy rebuilt dynamically up to Level {max_indent} with header flags and paired descriptions.")
    print(f"📁 Output saved to: {output_file}")


if __name__ == "__main__":
    load_icd_hierarchy()
