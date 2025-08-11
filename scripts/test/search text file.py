import os

folder_path = r"E:\MG data"
search_text = "ConnectionName"

for root, dirs, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                if search_text.lower() in f.read().lower():
                    print(f"Found in: {file_path}")
        except Exception as e:
            print(f"Could not read {file_path}: {e}")
