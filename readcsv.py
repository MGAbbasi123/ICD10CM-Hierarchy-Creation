from datasets import load_dataset
import pandas as pd

# Load the dataset
dataset = load_dataset("AdithyaSNair/disease")

# Convert to DataFrame
df = dataset["train"].to_pandas()

# Save as CSV locally
df.to_csv('E:/disease_dataset.csv', index=False)

print("✅ CSV exported successfully as 'disease_dataset.csv'")
