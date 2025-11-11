import pandas as pd
from clientCalls import fetch_cut_list_by_date

# Read an Excel file stored in the same directory as this script
excel_file = 'data.xlsx'  # replace with your actual filename
df = pd.read_excel(excel_file)

print('Excel data loaded successfully:')
print(df.head())

# Example usage of your existing function
cut_list = fetch_cut_list_by_date("11-11-25")

for prodType, size, orderNum in cut_list:
    print(f"Product Type: {prodType}, Size: {size}, Order Number: {orderNum}")
