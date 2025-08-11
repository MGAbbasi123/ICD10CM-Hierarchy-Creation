import pandas as pd


def load_icd_hierarchy():
    print("Loading ICD hierarchy...")


# Source File
source_file = 'H:/Projects/icd10/data/icd10cm_order_2020.txt'

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
df.to_csv('H:/Projects/icd10/output/icd10_hierarchy.csv', index=False)

print("✅ Hierarchy rebuilt correctly with inferred indent levels.")
