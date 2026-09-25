import pandas as pd
import numpy as np
from typing import List
from .household import Household
from .params import Params

def load_empirical_households(csv_path: str = 'public2025.csv', sample_size: int = 5000, seed: int = 42) -> List[Household]:
    """
    Ingests 2025 Fed SHED microdata to initialize empirically grounded agents.
    Converts categorical survey responses into continuous financial state variables.
    """
    print(f"Loading {sample_size} empirical agents from {csv_path}...")
    
    # Load only the columns we mapped
    cols = ['ppinc7', 'EF7A', 'GH14', 'C3P', 'ND0']
    df = pd.read_csv(csv_path, usecols=cols, low_memory=False)
    
    # Drop rows with missing critical data
    df = df.dropna(subset=['ppinc7'])
    
    # Randomly sample the target population size
    np.random.seed(seed)
    df_sample = df.sample(n=sample_size, replace=True)
    
    # Mapping Dictionaries: Categorical to Continuous Midpoints (Monthly)
    income_map = {
        'Less than $5,000': 2500 / 12,
        '$5,000 to $9,999': 7500 / 12,
        '$10,000 to $24,999': 17500 / 12,
        '$25,000 to $49,999': 37500 / 12,
        '$50,000 to $74,999': 62500 / 12,
        '$75,000 to $99,999': 87500 / 12,
        '$100,000 to $149,999': 125000 / 12,
        '$150,000 or more': 175000 / 12
    }
    
    savings_map = {
        'Less than $100': 50,
        '$100 to $499': 300,
        '$500 to $999': 750,
        '$1,000 to $1,999': 1500,
        '$2,000 to $4,999': 3500,
        '$5,000 or more': 6000
    }
    
    households = []
    params = Params()
    
    for _, row in df_sample.iterrows():
        # 1. Income
        inc_str = str(row['ppinc7']).strip()
        income = income_map.get(inc_str, 50000 / 12) # Default to 50k if malformed
        
        # 2. Balance (Liquid Savings)
        sav_str = str(row['EF7A']).strip()
        balance = savings_map.get(sav_str, 100) # Default low liquidity if missing
        
        # 3. Obligations (Housing)
        # Handle "Refused" or blank string entries safely
        try:
            obligations = float(row['GH14'])
        except (ValueError, TypeError):
            obligations = income * 0.30 # Standard 30% rule if missing
            
        # 4. Debt (Revolving Credit)
        # If they don't pay the full balance, estimate revolving debt relative to income
        c3p = str(row['C3P'])
        debt = 0.0
        if "Paid at least the minimum" in c3p or "Paid less than the minimum" in c3p:
            debt = income * 1.5 
            
        # 5. Cognitive Baseline / Stress Alpha
        # If they use Alternative Financial Services (ND0 = Yes), they have higher baseline friction
        nd0 = str(row['ND0'])
        alpha = 0.8 if nd0 == 'Yes' else 0.5
        
        hh = Household(
            income=income,
            obligations=obligations,
            balance=balance,
            debt=debt,
            alpha=alpha,
            params=params
        )
        households.append(hh)
        
    print(f"Successfully initialized {len(households)} empirical households.")
    return households