import pandas as pd
import sys

def run_calibration():
    print("Loading 2025 Fed SHED microdata...")
    try:
        # low_memory=False prevents dtype warnings on massive CSVs
        df = pd.read_csv('public2025.csv', low_memory=False)
    except FileNotFoundError:
        print("Error: public2025.csv not found in the current directory.")
        sys.exit(1)

    # In the 2025 SHED, EF1 is a binary "Yes"/"No". 
    # "No" means they cannot cover a $400 expense without high friction.
    total_responses = df['EF1'].notna().sum()
    high_friction_count = (df['EF1'] == 'No').sum()
    
    empirical_shock_prob = high_friction_count / total_responses

    print(f"\n--- CALIBRATION RESULT ---")
    print(f"Total Valid Respondents: {total_responses}")
    print(f"High-Friction ('No') Respondents: {high_friction_count}")
    print(f"Empirical Baseline Probability: {empirical_shock_prob:.4f}")
    print(f"--------------------------\n")
    
    return empirical_shock_prob

if __name__ == "__main__":
    run_calibration()