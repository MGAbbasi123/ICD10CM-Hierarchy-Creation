import pandas as pd
from pathlib import Path


def mark_sections():
    print("Marking ICD codes with sections...")

    # Set base directories dynamically relative to script's location
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / 'data'
    OUTPUT_DIR = BASE_DIR / 'output'

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load the latest ICD-10 hierarchy data
    icd_file = OUTPUT_DIR / 'icd10_hierarchy_dynamic_paired.csv'
    df = pd.read_csv(icd_file)

    # Load section definitions (CSV now)
    sections_file = DATA_DIR / 'icd10_sections.csv'
    sections = pd.read_csv(sections_file)  # columns: Range, Description

    # Build section mapping list (handling both ranges and single codes)
    section_ranges = []
    for _, row in sections.iterrows():
        range_value = str(row['Range']).strip()
        if '-' in range_value:
            start, end = range_value.split('-')
        else:
            start = end = range_value  # single code treated as both start and end

        section_ranges.append({
            'Section': row['Description'],
            'Start': start,
            'End': end
        })

    # Mapping function for assigning section to each ICD code
    def assign_section(icd_code):
        for section in section_ranges:
            if section['Start'] <= icd_code <= section['End']:
                return section['Section']
            if icd_code.startswith(section['End']):
                return section['Section']
        return 'Unclassified'

    # Apply section mapping
    df['SECTION_NAME'] = df['ICD_CODE'].apply(assign_section)

    # Define final column order (SECTION_NAME before TOP_LEVEL_CODE)
    final_columns = [
        'ORDER',
        'SECTION_NAME',
        'TOP_LEVEL_CODE',
        'LEVEL_1_PARENT',
        'LEVEL_1_DESC',
        'LEVEL_2_PARENT',
        'LEVEL_2_DESC',
        'LEVEL_3_PARENT',
        'LEVEL_3_DESC',
        'LEVEL_4_PARENT',
        'LEVEL_4_DESC',
        'ICD_CODE',
        'DESCRIPTION',
        'INDENT_LEVEL'
    ]

    # Check which columns exist in the dataframe
    available_columns = [col for col in final_columns if col in df.columns]
    missing_columns = [col for col in final_columns if col not in df.columns]

    if missing_columns:
        print(f"⚠️ Warning: These columns are missing in the data and will be skipped: {missing_columns}")

    # Reorder DataFrame
    df = df[available_columns]

    # Save output
    output_file = OUTPUT_DIR / 'icd10_hierarchy_with_sections.csv'
    df.to_csv(output_file, index=False)

    print(f"\n✅ ICD-10 codes successfully mapped to sections.")
    print(f"📁 Output saved to: {output_file}")

    # Preview output
    print("\n📄 Section Mapping Sample Preview:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    mark_sections()
