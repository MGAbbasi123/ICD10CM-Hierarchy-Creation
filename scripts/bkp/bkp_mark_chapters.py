import pandas as pd


def mark_chapters():
    print("Marking ICD codes with chapters...")


# Load the ICD-10 hierarchy data
icd_file = 'H:/Projects/icd10/output/icd10_hierarchy.csv'
df = pd.read_csv(icd_file)

# Load chapter definitions
chapters_file = 'H:/Projects/icd10/data/icd10_chapters.csv'
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
        'Range': row['Range']  # Adding Range to chapter data
    })


# Revised mapping function
def assign_chapter(icd_code):
    for chapter in chapter_ranges:
        start = chapter['Start']
        end = chapter['End']

        # If exact code in between
        if start <= icd_code <= end:
            return chapter['Name'], chapter['Range']

        # Handle edge prefix overlap — if at end of range like D49 and code starts with D49
        if icd_code.startswith(end):
            return chapter['Name'], chapter['Range']

    return 'Unclassified', 'NA'


# Apply mapping
df[['CHAPTER_NAME', 'CHAPTER_RANGE']] = df['ICD_CODE'].apply(lambda x: pd.Series(assign_chapter(x)))

# Save output
output_file = 'H:/Projects/icd10/output/icd10_hierarchy_with_chapters.csv'
df.to_csv(output_file, index=False)

print("✅ ICD-10 codes are successfully mapped to chapters and ranges.")
