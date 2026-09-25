import pandas as pd

print("Scanning 2025 Fed SHED Data Dictionary...")
df = pd.read_csv('public2025.csv', low_memory=False)

# Search the headers for keywords related to our Household initialization parameters
income_cols = [c for c in df.columns if 'inc' in c.lower()][:15]
debt_cols = [c for c in df.columns if 'debt' in c.lower() or 'loan' in c.lower() or 'credit' in c.lower()][:15]
savings_cols = [c for c in df.columns if 'save' in c.lower() or 'liquid' in c.lower() or 'bank' in c.lower()][:15]

print(f"\nPotential Income Variables: {income_cols}")
print(f"Potential Debt Variables: {debt_cols}")
print(f"Potential Savings Variables: {savings_cols}")