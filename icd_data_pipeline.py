# main.py
from scripts import load_icd_hierarchy
from scripts import mark_sec_and_chap


def main():
    print("Main script running...")

    # Calling
    load_icd_hierarchy.load_icd_hierarchy()

    mark_sec_and_chap.mark_chapters_and_sections()

    print("✅ Process completed successfully.")


if __name__ == "__main__":
    main()
