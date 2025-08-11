import pandas as pd
from pathlib import Path


def mark_chapters_and_sections():
    print("Marking ICD codes with chapters and sections...")

    # Set base directories
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / 'data'
    OUTPUT_DIR = BASE_DIR / 'output'

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load the latest ICD-10 hierarchy data
    icd_file = OUTPUT_DIR / 'icd10_hierarchy_dynamic_paired.csv'
    df = pd.read_csv(icd_file)

    # Load chapter definitions
    chapters_file = DATA_DIR / 'icd10_chapters.csv'
    chapters = pd.read_csv(chapters_file)

    # Load section definitions (CSV)
    sections_file = DATA_DIR / 'icd10_sections.csv'
    sections = pd.read_csv(sections_file)

    # Build chapter mapping list
    chapter_ranges = []
    for _, row in chapters.iterrows():
        start, end = row['Range'].split('-')
        chapter_ranges.append({
            'Name': row['Name'],
            'Range': row['Range'],
            'Start': start,
            'End': end
        })

    # Build section mapping list (handling ranges + single codes)
    section_ranges = []
    for _, row in sections.iterrows():
        range_value = str(row['Range']).strip()
        if '-' in range_value:
            start, end = range_value.split('-')
        else:
            start = end = range_value
        section_ranges.append({
            'Description': row['Description'],
            'Range': range_value,
            'Start': start,
            'End': end
        })

    # Function for assigning chapter to each ICD code
    def assign_chapter(icd_code):
        for chapter in chapter_ranges:
            if chapter['Start'] <= icd_code <= chapter['End']:
                return chapter['Name'], chapter['Range']
            if icd_code.startswith(chapter['End']):
                return chapter['Name'], chapter['Range']
        return 'Unclassified', 'NA'

    # Function for assigning section to each ICD code
    def assign_section(icd_code):
        for section in section_ranges:
            if section['Start'] <= icd_code <= section['End']:
                return section['Description'], section['Range']
            if icd_code.startswith(section['End']):
                return section['Description'], section['Range']
        return 'Unclassified', 'NA'

    # Apply chapter and section mappings
    df[['CHAPTER_NAME', 'CHAPTER_RANGE']] = df['ICD_CODE'].apply(lambda x: pd.Series(assign_chapter(x)))
    df[['SECTION_NAME', 'SECTION_RANGE']] = df['ICD_CODE'].apply(lambda x: pd.Series(assign_section(x)))

    # Define final column order — HEADER_FLAG at the end now
    final_columns = [
        'ORDER',
        'CHAPTER_RANGE',
        'CHAPTER_NAME',
        'SECTION_RANGE',
        'SECTION_NAME',
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
        'INDENT_LEVEL',
        'HEADER_FLAG'
    ]

    # Check which columns exist in the dataframe
    available_columns = [col for col in final_columns if col in df.columns]
    missing_columns = [col for col in final_columns if col not in df.columns]

    if missing_columns:
        print(f"⚠️ Warning: These columns are missing in the data and will be skipped: {missing_columns}")

    # Reorder DataFrame
    df = df[available_columns]

    # Save final output to Excel
    output_file = OUTPUT_DIR / 'icd10_hierarchy_final.xlsx'
    df.to_excel(output_file, index=False, sheet_name='ICD10 Hierarchy')

    print(f"\n✅ ICD-10 codes successfully mapped to chapters and sections, with HEADER_FLAG included.")
    print(f"📁 Final Excel output saved to: {output_file}")

    # Preview result
    print("\n📄 Final Output Sample Preview:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    mark_chapters_and_sections()
