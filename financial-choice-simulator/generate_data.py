import numpy as np
import pandas as pd

# ==========================================
# TABLE 1: SIMULATION PARAMETERS
# ==========================================
N_SIMS = 1000
MONTHS = 12
np.random.seed(42) # For reproducible results in your paper

# Credit & Penalty
R_STD = 0.21 / 12       # 21% APR monthly
R_PRED = 3.91 / 12      # 391% APR monthly
GAMMA = 0.10            # 10% behavioral penalty on fixed costs

# Lognormal Financial Parameters
MU_INC, SIGMA_INC = np.log(3000), 0.2
MU_COST, SIGMA_COST = np.log(2500), 0.2
P_SHOCK = 0.15
MU_SHOCK, SIGMA_SHOCK = np.log(500), 0.6

# Cognitive Evolution Parameters
R_BW = 15               # Baseline monthly bandwidth recovery
ALPHA = 30              # Sludge drain multiplier
BETA = 0.01             # Shock cognitive tax multiplier
K_STEEPNESS = 0.35      # Logistic steepness (calibrated for 15-point gap)
SIGMA_BW = 1.5          # Stochastic bandwidth noise
INFLECTION = 85         # 50% capture probability threshold

def run_simulation(global_sludge, intervention_month=None):
    """
    Runs the vectorized Monte Carlo simulation.
    intervention_month: If set, drops global_sludge to 0.1 at this month.
    """
    # 1. Initialize State Space
    income = np.random.lognormal(MU_INC, SIGMA_INC, N_SIMS)
    costs = np.random.lognormal(MU_COST, SIGMA_COST, N_SIMS)
    skill = np.random.uniform(0, 1, N_SIMS)
    
    bw = np.full(N_SIMS, 100.0)
    normal_debt = np.zeros(N_SIMS)
    predatory_debt = np.zeros(N_SIMS)
    
    deficit = np.maximum(0, costs - income)
    
    history = {'bw': [], 'p_capture': [], 'capture': [], 'normal_debt': [], 'predatory_debt': []}
    
    for m in range(1, MONTHS + 1):
        # Apply Policy Intervention (Sludge drops to 0.1)
        current_sludge = 0.1 if (intervention_month and m >= intervention_month) else global_sludge
        effective_sludge = current_sludge * (1 - skill)
        
        # Shocks
        hit = np.random.binomial(1, P_SHOCK, N_SIMS)
        shock_magnitude = np.random.lognormal(MU_SHOCK, SIGMA_SHOCK, N_SIMS)
        cost_shock = hit * shock_magnitude
        
        # Bandwidth Evolution
        noise = np.random.normal(0, SIGMA_BW, N_SIMS)
        bw = bw + R_BW - (ALPHA * effective_sludge) - (BETA * cost_shock) + noise
        bw = np.clip(bw, 0, 100)
        
        # Logistic Capture
        p_capture = 1 / (1 + np.exp(K_STEEPNESS * (bw - INFLECTION)))
        capture = np.random.binomial(1, p_capture)
        
        # Financial Accumulation
        penalty = capture * (costs * GAMMA)
        
        delta_normal = deficit + (cost_shock * (1 - capture))
        delta_predatory = penalty + (cost_shock * capture)
        
        normal_debt = (normal_debt + delta_normal) * (1 + R_STD)
        predatory_debt = (predatory_debt + delta_predatory) * (1 + R_PRED)
        
        # Log History
        history['bw'].append(bw.copy())
        history['p_capture'].append(p_capture.copy())
        history['capture'].append(capture.copy())
        history['normal_debt'].append(normal_debt.copy())
        history['predatory_debt'].append(predatory_debt.copy())
        
    return {k: np.array(v) for k, v in history.items()}

# ==========================================
# EXECUTE EXPERIMENTS & GENERATE PAPER DATA
# ==========================================
print("--- DATA FOR SECTION 4.1: DEGENERATE-CASE VALIDATION ---")
base_sim = run_simulation(global_sludge=0.0)
mean_p_capture = np.mean(base_sim['p_capture'])
print(f"Noise Parameter (sigma_bw): {SIGMA_BW}")
print(f"Steepness Parameter (k): {K_STEEPNESS}")
print(f"[INSERT EXACT MEAN P(CAPTURE)]: {mean_p_capture:.4f} ({mean_p_capture*100:.2f}%)\n")

print("--- DATA FOR SECTION 4.2: CONTINUOUS SLUDGE SWEEP (SLUDGE = 0.9) ---")
high_sludge_sim = run_simulation(global_sludge=0.9)
total_debt_m12 = high_sludge_sim['normal_debt'][-1] + high_sludge_sim['predatory_debt'][-1]
tail_risk_95 = np.percentile(total_debt_m12, 95)
cascade_prob = np.mean(np.max(high_sludge_sim['capture'], axis=0)) * 100
print(f"Cascade Probability at Sludge 0.9: {cascade_prob:.1f}%")
print(f"[INSERT DEBT] (95th Percentile Total Debt at month 12): ${tail_risk_95:,.2f}\n")

print("--- DATA FOR SECTION 5: POLICY COUNTERFACTUAL ---")
control_sim = run_simulation(global_sludge=0.8)
treatment_sim = run_simulation(global_sludge=0.8, intervention_month=6)

# Extract Capture Rates at Month 6 and Month 8
control_capture_m6 = np.mean(control_sim['capture'][5]) * 100
treatment_capture_m6 = np.mean(treatment_sim['capture'][5]) * 100
treatment_capture_m8 = np.mean(treatment_sim['capture'][7]) * 100

control_total_debt = control_sim['normal_debt'][-1] + control_sim['predatory_debt'][-1]
treatment_total_debt = treatment_sim['normal_debt'][-1] + treatment_sim['predatory_debt'][-1]

print(f"[INSERT %] (Treatment Capture Rate at Month 6): {treatment_capture_m6:.1f}%")
print(f"[INSERT %] (Treatment Capture Rate at Month 8): {treatment_capture_m8:.1f}%")
print(f"Control 95th Percentile Debt: ${np.percentile(control_total_debt, 95):,.2f}")
print(f"Treatment 95th Percentile Debt: ${np.percentile(treatment_total_debt, 95):,.2f}")