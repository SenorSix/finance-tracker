import pandas as pd

# load CSV file
file_path = "/home/mr6/Desktop/1/Money/Finance/Tracker/3-22-25.csv"
df = pd.read_csv(file_path)

# Convert "Date" to proper datetime format and ensure readable format
df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime('%m-%d-%Y')

# Define category mapping
category_mapping = {
    "MCM": "Paycheck",
    "ELDRIDGE MUSIC ACADEMY": "Piano Lessons",
    "RIVER PARK RP": "HOA",
    "GPC": "Georgia Power",
    "COMCAST": "Comcast",
    "RACETRAC": "Racetrac",
    "KROGER": "Kroger",
    "WAL-MART": "Walmart",
    "PAPA JOHN'S": "Papa Johns",
    "INTEGRATORS": "HOA fee",
    "QT": "Quik Trip",
    "TURNERTECH": "CNN",
    "WENDYS": "Wendys",
    "CHICK-FIL-A": "Chik",
    "XFINITY": "Cell Phone",
    "LINODE": "Linode",
    "MARCOS": "Marcos",
    "BUC-EE": "Buckys",
    "TACO MAC": "Taco Mac",
    "PATREON": "Patreon",
}

# Apply category mapping
def categorize_transaction(description):
    for key in category_mapping:
        if key in str(description).upper():  # Convert to uppercase for matching
            return category_mapping[key]
    return "Other" # If it's not in our list, mark it as "Other"

df["Category"] = df["Description"].astype(str).apply(categorize_transaction)

# Convert "Amount" to numeric values
df["Amount"] = df["Amount"].replace('[\$,]', '', regex=True).astype(float)

# Separate income & expenses
income_df = df[df["Amount"] > 0]
expenses_df = df[df["Amount"] < 0]

# Sort transactions by date
income_df = income_df.sort_values(by="Date")
expenses_df = expenses_df.sort_values(by="Date")

# Pivot tables (Each business has its own column)
income_pivot = income_df.pivot_table(index="Date", columns="Category", values="Amount", aggfunc="sum")
expenses_pivot = expenses_df.pivot_table(index="Date", columns="Category", values="Amount", aggfunc="sum")

# Only keep mapped businesses that actually appear in the transactions
expenses_pivot = expenses_pivot[[col for col in expenses_pivot.columns if col in category_mapping.values()]]

# Merge everything into final format
final_df = pd.concat([income_pivot, pd.DataFrame(index=income_pivot.index), expenses_pivot], axis=1).sort_index()

# Save to CSV
output_path = "/home/mr6/Desktop/1/Money/Finance/Tracker/final_finance.csv"
final_df.to_csv(output_path)

# Preview the output
print(final_df.head())