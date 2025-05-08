import pandas as pd
import json

# Load bank statement CSV
file_path = "excel/3-22-25.csv"
df = pd.read_csv(file_path)

def extract_vendor(description):
    description = description.lower() # Ensures the script works with POS PURCHASE or pos purchase

    if "pos purchase" in description:
        # Find the part after "POS PURCHASE" to copy
        words = description.split("pos purchase", 1)[1].strip()

        # If first character after "POS PURCHASE" is not a letter or space, return "XXXX"
        if words and not words[0].isalpha():
            return "XXXX"

        # Start extracting letters and spaces
        vendor = ""
        for char in words:
            if char.isalpha() or char == " ": # Allows letters and spaces
                vendor += char
            else:   # Stop at the first non-letter, non-space character
                break

        return " ".join(vendor.strip().title().split()[:2]) # Capitalizes properly and copy no more than 2 words
    else:
        # If first character isn't a letter, flag as "XXXX"
        if description and not description[0].isalpha():
            return "XXXX"
        
        # Extract only letters and spaces for non-POS transactions (Stop at first non-alphabetical character)
        vendor = ""
        for char in description:
            if char.isalpha() or char == " ": # Allows letters and spaces
                vendor += char
            else:  # Stop at the first non-letter, non-space character
                break

        # If the first character was a number/symbol, or nothing was copied, flag as "XXXX"
        return " ".join(vendor.strip().title().split()[:2]) if vendor and vendor[0].isalpha() else "XXXX"
    
# Apply the extract_vendor function to the Description column
df["Cleaned_Description"] = df["Description"].astype(str).apply(extract_vendor)

with open("data/clean_names.json", "r") as f:
    name_map = json.load(f)

# Load fallback map for full descriptions
with open("data/fallback_map.json", "r") as f:
    fallback_map = json.load(f)

def resolve_edge_case(row):
    if row["Cleaned_Description_1"] in ["XXXX", "Xx", "Sq"]:
        full_desc = row["Description"].lower()
        for key in fallback_map:
            if key in full_desc:
                return fallback_map[key]
    return row["Cleaned_Description_1"]

# First, create the mapped version
df["Mapped_Name"] = df["Cleaned_Description"].map(name_map).fillna(df["Cleaned_Description"])

# Then apply the fallback logic *after* the mapping
df["Cleaned_Description_1"] = df.apply(lambda row: resolve_edge_case({"Description": row["Description"], "Cleaned_Description_1": row["Mapped_Name"]}), axis=1)

# Create a new CSV with only the cleaned descriptions
output_path = "excel/cleaned_descriptions.csv"
df[["Date", "Description", "Cleaned_Description", "Cleaned_Description_1", "Amount", "Balance"]].to_csv(output_path, index=False)

print(f"✅ Cleaned descriptions saved to {output_path}!")