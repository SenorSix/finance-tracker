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
    if row["Cleaned_Description_1"] in ["XXXXXXXXXX"]:
        full_desc = row["Description"].lower()
        for key in fallback_map:
            if key in full_desc:
                return fallback_map[key]
    return row["Cleaned_Description_1"]

# Apply mapping and fallback logic
df["Mapped_Name"] = df["Cleaned_Description"].map(name_map).fillna(df["Cleaned_Description"])
df["Cleaned_Description_1"] = df.apply(
    lambda row: resolve_edge_case({
        "Description": row["Description"],
        "Cleaned_Description_1": row["Mapped_Name"]
    }),
    axis=1
)

# Save cleaned data as CSV (no formatting)
output_path = "excel/cleaned_descriptions.csv"
df[["Date", "Description", "Cleaned_Description", "Cleaned_Description_1", "Amount", "Balance"]].to_csv(output_path, index=False)

print(f"✅ Cleaned descriptions saved to {output_path}!")
