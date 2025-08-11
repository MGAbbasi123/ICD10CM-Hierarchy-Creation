import pandas as pd
from pathlib import Path


def mark_chapters():
    print("Marking ICD codes with chapters...")

    # Set base directories dynamically relative to script's location
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / 'data'
    OUTPUT_DIR = BASE_DIR / 'output'

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load the latest ICD-10 hierarchy data (the dynamic one)
    icd_file = OUTPUT_DIR / 'icd10_hierarchy_dynamic_paired.csv'
    df = pd.read_csv(icd_file)

    # Load chapter definitions
    chapters_file = DATA_DIR / 'icd10_chapters.csv'
    chapters = pd.read_csv(chapters_file)  # columns: ID, Name, Range

    # Build a clean mapping list
    chapter_ranges = []
    for _, row in chapters.iterrows():
        start, end = row['Range'].split('-')
        chapter_ranges.append({
            'ID': row['ID'],
            'Name': row['Name'],
            'Start': start,
            'End': end,
            'Range': row['Range']
        })

    # Mapping function
    def assign_chapter(icd_code):
        for chapter in chapter_ranges:
            start = chapter['Start']
            end = chapter['End']

            if start <= icd_code <= end:
                return chapter['Name'], chapter['Range']
            if icd_code.startswith(end):
                return chapter['Name'], chapter['Range']

        return 'Unclassified', 'NA'

    # Apply chapter mapping
    df[['CHAPTER_NAME', 'CHAPTER_RANGE']] = df['ICD_CODE'].apply(lambda x: pd.Series(assign_chapter(x)))

    # Reorder columns as per your provided sequence
    final_columns = [
        'ORDER',
        'CHAPTER_RANGE',
        'CHAPTER_NAME',
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

    # Ensure all required columns exist — warn if missing any
    missing_cols = [col for col in final_columns if col not in df.columns]
    if missing_cols:
        print(f"⚠️ Warning: These columns are missing in the data and will be skipped: {missing_cols}")
        final_columns = [col for col in final_columns if col in df.columns]

    # Reorder DataFrame
    df = df[final_columns]

    # Save final output
    output_file = OUTPUT_DIR / 'icd10_hierarchy_final.csv'
    df.to_csv(output_file, index=False)

    print(f"\n✅ ICD-10 codes successfully mapped to chapters and reordered.")
    print(f"📁 Final output saved to: {output_file}")

    # Show a preview
    print("\n📄 Final Output Sample Preview:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    mark_chapters()
