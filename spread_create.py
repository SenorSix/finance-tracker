import pandas as pd
import json

# Load bank statement CSV
file_path = "excel/3-22-25.csv"
df = pd.read_csv(file_path)

# Clean and extract vendor names
def extract_vendor(description):
    description = description.lower()

    if "pos purchase" in description:
        words = description.split("pos purchase", 1)[1].strip()
        if words and not words[0].isalpha():
            return "XXXX"

        vendor = ""
        for char in words:
            if char.isalpha() or char == " ":
                vendor += char
            else:
                break
        return " ".join(vendor.strip().title().split()[:2])

    else:
        if description and not description[0].isalpha():
            return "XXXX"

        vendor = ""
        for char in description:
            if char.isalpha() or char == " ":
                vendor += char
            else:
                break

        return " ".join(vendor.strip().title().split()[:2]) if vendor and vendor[0].isalpha() else "XXXX"

# Apply cleaning
df["Cleaned_Description"] = df["Description"].astype(str).apply(extract_vendor)
df["Cleaned_Description"] = df["Cleaned_Description"].replace(["XXXX", "Xx", "Sq"], "XXXXXXXXXX")
# "XXXX" was the output originally for POS PURCHASE errors above. "Xx" and "Sq" were bad outputs that the code naturally generated that identified other edge cases. I put them all into a single placeholder value "XXXXXXXXXX" for clarity so they'd be easy to identify and correct on the generated CSV file

# Load mappings
with open("data/clean_names.json", "r") as f:
    name_map = json.load(f)

with open("data/fallback_map.json", "r") as f:
    fallback_map = json.load(f)

# Handle edge cases
def resolve_edge_case(row):
    if row["Mapped_Name"] in ["XXXXXXXXXX"]:
        full_desc = row["Description"].lower()
        for key in fallback_map:
            if key in full_desc:
                return fallback_map[key]
    return row["Mapped_Name"]

# Apply mapping and fallback logic
df["Mapped_Name"] = df["Cleaned_Description"].map(name_map).fillna(df["Cleaned_Description"])
df["Cleaned_Description_1"] = df.apply(resolve_edge_case, axis=1)



#____________________________________________________________________________________________#

# Separate part of script to create a JSON file categorizing vendors

category_path = "data/category.json"

# Load existing category mapping or start fresh
try:
    with open(category_path, 'r') as f:
        category_map = json.load(f)
except FileNotFoundError:
    category_map =  {}

# Get current vendors
current_vendors = df["Cleaned_Description_1"].dropna().unique()

# Track new vendors added
new_entries = 0

# Add any new vendors not already in the file
for vendor in current_vendors:
    if vendor not in category_map:
        category_map[vendor] = ""
        new_entries += 1

# Save updated category map
with open(category_path, 'w') as f:
    json.dump(category_map, f, indent=2)

output_path = "excel/cleaned_descriptions.csv"

df["Categories"] = df["Cleaned_Description_1"].map(category_map).fillna("")

columns_to_export = ["Date", "Description", "Cleaned_Description", "Cleaned_Description_1", "Categories", "Amount", "Balance"]

df[columns_to_export].to_csv(output_path, index=False)

if new_entries:
    print(f"🆕🆕🆕🆕🆕🆕🆕🆕🆕🆕🆕 NEW VENDORS. CATEGORIZE")
else:
    print("✅ No new vendors found. Category map is up to date")

print(f"✅ Cleaned descriptions saved to {output_path}!")


