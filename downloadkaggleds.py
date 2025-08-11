import os
import zipfile

# Download via system call
os.system('kaggle datasets download -d choongqianzheng/disease-and-symptoms-dataset')

# Extract the zip
with zipfile.ZipFile("disease-and-symptoms-dataset.zip", 'r') as zip_ref:
    zip_ref.extractall("disease_dataset")

print("Dataset extracted to disease_dataset/")
