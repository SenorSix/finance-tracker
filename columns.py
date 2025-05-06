import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, Border, Side

# Load your cleaned data
df = pd.read_csv("/home/mr6/Desktop/1/Money/Finance/Tracker/Excel/cleaned_descriptions.csv")

# Convert date column
df["Date"] = pd.to_datetime(df["Date"])

# Clean dollar signs and convert to float
df[["Amount", "Balance"]] = df[["Amount", "Balance"]].replace('[\$,]', '', regex=True).astype(float)

# Create pivot table (Date as index, Vendors as columns, Amounts as values)
pivot_df = df.pivot_table(
    index="Date",
    columns="Cleaned_Description_1",
    values="Amount",
    aggfunc="sum",    # Summing in case there are multiple charges per vendor per day
    fill_value=""
)

# Build full date range from earliest to latest date
full_range = pd.date_range(start=df["Date"].min(), end=df["Date"].max(), freq='D')

# Reindex to include all days (even if no transactions)
pivot_df = pivot_df.reindex(full_range)

# Reset index so "Date" becomes a column instead of index
pivot_df = pivot_df.reset_index()
pivot_df.columns.name = None  # Remove the 'Cleaned_Description_1' header

# Format date
pivot_df["index"] = pivot_df["index"].dt.strftime("%-m-%-d-%Y")  # Use %#m/%#d on Windows if needed
pivot_df.rename(columns={"index": "Date"}, inplace=True)

# Add totals row at the bottom
totals = pivot_df.iloc[:, 1:].replace("", 0).astype(float).sum()
totals_row = ["Total"] + totals.tolist()
pivot_df.loc[len(pivot_df)] = totals_row

# Save to Excel
excel_path = "/home/mr6/Desktop/1/Money/Finance/Tracker/Excel/output_by_date.xlsx"
pivot_df.to_excel(excel_path, index=False)

# Auto-adjust column widths
wb = load_workbook(excel_path)
ws = wb.active
ws.freeze_panes = "B2"
last_row = ws.max_row

scaling_factor = 1.1
padding = 2
max_column_width = 40

for col in ws.columns:
    max_length = 0
    col_letter = col[0].column_letter
    for cell in col:
        try:
            if cell.value:
                length = len(str(cell.value).strip())
                if length < 100:
                    max_length = max(max_length, length)
        except:
            pass
    adjusted_width = min((max_length * scaling_factor) + padding, max_column_width)
    ws.column_dimensions[col_letter].width = adjusted_width

# Bold and border the totals row
bold_border = Border(
    left=Side(style='medium'),
    right=Side(style='medium'),
    top=Side(style='medium'),
    bottom=Side(style='medium')
)

for cell in ws[last_row]:
    cell.font = Font(bold=True)
    cell.border = bold_border

wb.save(excel_path)

print("✅ Output with full date range and totals row saved!")
