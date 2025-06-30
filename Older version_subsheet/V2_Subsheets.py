#This version of subsheet contains nine sheets-PM01, PM02, Breakdown Maintenance,
#Shutdown jobs, Vibration monitoring, Lube Oil Analysis, Spares Management,
#Running Contracts, and Gate Pass Details.

import pandas as pd
import os

# Folder containing the monthly MPR Excel files
folder_path = r"/Users/omkarkadam/Documents/Automate with Python/Dashboard"  # Replace with the path to your folder

# List of months for which MPR files are present
months = ['JUNE', 'JULY']  # Modify this based on the actual files in the folder

# Function to extract tables from a single Excel file
def extract_tables_from_file(file_path):
    # Read the first sheet of the Excel file and skip unnecessary rows
    df = pd.read_excel(file_path, sheet_name=0, skiprows=5)
    
    # Extract the tables
    table_1 = df.iloc[1:4, 1:4]
    table_1.columns = ['Plant', 'Planned', 'Executed']
    
    table_2 = df.iloc[7:10, 1:4]
    table_2.columns = ['Plant', 'Planned', 'Executed']
    
    # For table_3, include an extra column for 'Short description of the job'
    table_3 = df.iloc[13:16, 1:4]
    table_3.columns = ['Plant', 'No. of Breakdown Jobs', 'Short description of the job']
    
    # Extract table_4 for Jobs Hold for Shutdown
    table_4 = df.iloc[20:23, 1:4]
    table_4.columns = ['Plant', 'No. of Jobs hold', 'Short description of the job']
    
    # Extract table_5 for Vibration Monitoring
    table_5 = df.iloc[27:30, 1:5]
    table_5.columns = ['Plant', 'No. of Equipment Scheduled', 'No. of Equipment Monitored (Executed)', 'Reasons for Equipment not monitored']

    # Add the extra columns next to the existing table_5
    # First two columns from df.iloc[31:34, 2:4]
    extra_cols_5_1 = df.iloc[31:34, 2:4]
    extra_cols_5_1.columns = ['No. of Equipment With Normal Health', 'Health Index']
    
    # Next two columns from df.iloc[35:38, 2:4]
    extra_cols_5_2 = df.iloc[35:38, 2:4]
    extra_cols_5_2.columns = ['No. of Equipment With Critical Health', 'Critical Index']
    
    # Last three columns from df.iloc[39:42, 2:5]
    extra_cols_5_3 = df.iloc[39:42, 2:5]
    extra_cols_5_3.columns = ['Corrective Actions Initiated', 'Corrective Actions Pending', 'Short Description of Issue and Action taken/Reasons for actions pending']
    
    # Concatenate the columns horizontally to table_5
    table_5 = pd.concat([table_5.reset_index(drop=True), extra_cols_5_1.reset_index(drop=True), extra_cols_5_2.reset_index(drop=True), extra_cols_5_3.reset_index(drop=True)], axis=1)

    # Extract table_6 for Lube Oil Analysis (Monthly Moisture Analysis)
    table_6 = df.iloc[45:48, 1:4]
    table_6.columns = ['Plant', 'No. Scheduled for Analysis', 'No Samples analysed']

    # Add additional columns to table_6 - NEW ADDITION
    extra_cols_6_1 = df.iloc[49:52, 2:4]
    extra_cols_6_1.columns = ['Corrective Actions Required', 'Corrective Actions Taken']
    table_6 = pd.concat([table_6.reset_index(drop=True), extra_cols_6_1.reset_index(drop=True)], axis=1)

    # Extract table_7 for SPARES MANAGEMENT - NEW ADDITION
    table_7 = df.iloc[55:58, 1:6]
    table_7.columns = ['Plant', 'Indents Scheduled for Review in this month', 'No. of PR Raised in this month', 'Cumul. No. of Indents Scheduled for Review till this month in F.Y. 24-25', 'Cumul. No. of PR Raised till this month in F.Y. 24-25']

    # Extract table_8 for Running Contracts - NEW ADDITION
    table_8 = df.iloc[67:70, 1:5]
    table_8.columns = ['Plant', 'Total Current Running Contracts', 'Contracts requiring Renewal (& expiring in this/next six months)', 'Contracts Expired in this month (& not requiring renewal)']

    # Extract table_9 for Gate Pass Details - NEW ADDITION
    table_9 = df.iloc[106:109, 1:6]
    table_9.columns = ['plant', 'New Gate Pass Created in this month', 'Gate Pass open till last month', 'Gate Pass Closed in this month', 'Total current open Gate Pass']
    
    return table_1, table_2, table_3, table_4, table_5, table_6, table_7, table_8, table_9

# Initialize dictionaries to store tables for each month
merged_tables = {
    "table_1": [],
    "table_2": [],
    "table_3": [],
    "table_4": [],
    "table_5": [],
    "table_6": [],
    "table_7": [], # Added for the new table_7
    "table_8": [], # Added for the new table_8
    "table_9": []  # Added for the new table_9
}

# Loop through each month, read the corresponding file, and extract tables
for month in months:
    file_name = f'MPR {month}.xlsx'  # Construct the filename
    file_path = os.path.join(folder_path, file_name)
    
    # Extract tables from the current month's file (now including table_6, 7, 8, 9)
    table_1, table_2, table_3, table_4, table_5, table_6, table_7, table_8, table_9 = extract_tables_from_file(file_path)
    
    # Add a 'Month' column to each table
    table_1['Month'] = month
    table_2['Month'] = month
    table_3['Month'] = month
    table_4['Month'] = month
    table_5['Month'] = month
    table_6['Month'] = month
    table_7['Month'] = month # Added for the new table_7
    table_8['Month'] = month # Added for the new table_8
    table_9['Month'] = month # Added for the new table_9
    
    # Append tables to the respective list in merged_tables
    merged_tables["table_1"].append(table_1)
    merged_tables["table_2"].append(table_2)
    merged_tables["table_3"].append(table_3)
    merged_tables["table_4"].append(table_4)
    merged_tables["table_5"].append(table_5)
    merged_tables["table_6"].append(table_6)
    merged_tables["table_7"].append(table_7) # Added for the new table_7
    merged_tables["table_8"].append(table_8) # Added for the new table_8
    merged_tables["table_9"].append(table_9) # Added for the new table_9

# Concatenate tables from all months
merged_table_1 = pd.concat(merged_tables["table_1"], ignore_index=True)
merged_table_2 = pd.concat(merged_tables["table_2"], ignore_index=True)
merged_table_3 = pd.concat(merged_tables["table_3"], ignore_index=True)
merged_table_4 = pd.concat(merged_tables["table_4"], ignore_index=True)
merged_table_5 = pd.concat(merged_tables["table_5"], ignore_index=True)
merged_table_6 = pd.concat(merged_tables["table_6"], ignore_index=True)
merged_table_7 = pd.concat(merged_tables["table_7"], ignore_index=True) # Added for the new table_7
merged_table_8 = pd.concat(merged_tables["table_8"], ignore_index=True) # Added for the new table_8
merged_table_9 = pd.concat(merged_tables["table_9"], ignore_index=True) # Added for the new table_9

# Create a new Excel writer to save the merged tables
output_file = r"/Users/omkarkadam/Documents/Automate with Python/Merged_MPR.xlsx"  # Replace with your desired output path

# Write each merged table to its own sheet using the new sheet names
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Write each merged table to its respective sheet
    merged_table_1.to_excel(writer, sheet_name='PM02', index=False)
    merged_table_2.to_excel(writer, sheet_name='PM01', index=False)
    merged_table_3.to_excel(writer, sheet_name='Breakdown Maintenance', index=False)
    merged_table_4.to_excel(writer, sheet_name='Jobs Hold for Shutdown', index=False)
    merged_table_5.to_excel(writer, sheet_name='Vibration Monitoring', index=False)
    merged_table_6.to_excel(writer, sheet_name='Monthly Lube Oil Analysis)', index=False)
    merged_table_7.to_excel(writer, sheet_name='SPARES MANAGMENT', index=False) # Added for the new table_7
    merged_table_8.to_excel(writer, sheet_name='Running Contracts', index=False) # Added for the new table_8
    merged_table_9.to_excel(writer, sheet_name='Gate Pass Details', index=False) # Added for the new table_9

print(f"Merged file created successfully with all specified sheets at {output_file}")
