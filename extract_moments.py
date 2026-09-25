import pandas as pd
import json

def extract_empirical_moments(csv_path='public2025.csv'):
    print("Extracting macroeconomic target moments from Fed SHED...\n")
    
    # Load relevant columns
    cols = ['ND0', 'C3P', 'A0', 'A0B']
    df = pd.read_csv(csv_path, usecols=cols, low_memory=False)
    
    # Total valid respondents
    total_respondents = len(df)
    
    # Moment 1: Payday / AFS Usage Rate (ND0 = Yes)
    afs_users = len(df[df['ND0'].astype(str).str.contains('Yes', na=False)])
    m_payday = afs_users / total_respondents
    
    # Moment 2: Minimum Payment / Revolving Debt Default Rate (C3P contains 'minimum')
    min_payers = len(df[df['C3P'].astype(str).str.contains('minimum', case=False, na=False)])
    m_pay_min = min_payers / total_respondents
    
    # Moment 3: Credit Friction / Rejection Rate (Applied A0=Yes, Rejected A0B=Yes)
    applied = df[df['A0'].astype(str).str.contains('Yes', na=False)]
    rejected = len(applied[applied['A0B'].astype(str).str.contains('Yes', na=False)])
    m_credit_friction = rejected / len(applied) if len(applied) > 0 else 0.0

    moments = {
        "m_payday": m_payday,
        "m_pay_min": m_pay_min,
        "m_credit_friction": m_credit_friction
    }
    
    print(f"Target Moment 1 (Payday/AFS Usage): {m_payday:.4f}")
    print(f"Target Moment 2 (Revolving Debt Default): {m_pay_min:.4f}")
    print(f"Target Moment 3 (Credit Rejection Rate): {m_credit_friction:.4f}\n")
    
    # Export for the SMM optimizer to ingest
    with open('target_moments.json', 'w') as f:
        json.dump(moments, f, indent=4)
    print("Saved to target_moments.json. Ready for SMM Estimator.")

if __name__ == "__main__":
    extract_empirical_moments()