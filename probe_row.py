import pandas as pd

print("Extracting sample respondent from Fed SHED...\n")
# We only need to load the first row to see the column headers and data types
df = pd.read_csv('public2025.csv', low_memory=False, nrows=1)

# Convert the first row to a dictionary and drop empty values
respondent = df.iloc[0].dropna().to_dict()

for col, val in respondent.items():
    # Filter out empty space strings common in SAS/Stata CSV dumps
    if str(val).strip(): 
        print(f"{col}: {val}")