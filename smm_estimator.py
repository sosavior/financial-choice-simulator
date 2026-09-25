import json
import numpy as np
from scipy.optimize import minimize
from src.model.params import Params, PAY_MIN, PAYDAY, REFI, DEFER
from src.model.choice_set import ChoiceSet, Action
from src.model.empirical_agents import load_empirical_households

def simulate_moments(theta, households):
    """
    Runs the cognitive engine using a candidate parameter vector.
    theta[0] = alpha (stress elasticity - how fast bandwidth breaks)
    theta[1] = cog_payday (administrative sludge of AFS)
    """
    alpha_candidate, cog_payday_candidate = theta
    params = Params(cog_payday=cog_payday_candidate, a_min=max(0.10, cog_payday_candidate))
    
    actions = [
        Action(PAY_MIN, params.cog_pay_min),
        Action(PAYDAY, params.cog_payday),
        Action(REFI, params.cog_refi),
        Action(DEFER, params.cog_defer)
    ]
    choice_set = ChoiceSet(actions, params)
    
    payday_count = 0
    pay_min_count = 0
    
    for hh in households:
        # Inject the candidate alpha into the empirical agent
        hh.alpha = alpha_candidate 
        hh.attention = 1.0
        
        # Single-period steady state test with the 0.4335 empirical shock probability
        shock = 400.0 if np.random.rand() < 0.4335 else 0.0
        ctx = hh.begin_period(0, income_t=hh.income, transfer=-shock)
        
        try:
            decision = choice_set.choose(hh, ctx)
            if decision.chosen.name == PAYDAY:
                payday_count += 1
            elif decision.chosen.name == PAY_MIN:
                pay_min_count += 1
        except RuntimeError:
            # Complete cognitive collapse defaults to the trap
            payday_count += 1 
            
    n = len(households)
    return np.array([payday_count / n, pay_min_count / n])

def objective(theta, households, target_moments):
    """Loss function: Sum of Squared Errors (SSE) between simulation and reality."""
    sim_moments = simulate_moments(theta, households)
    error = np.sum((sim_moments - target_moments)**2)
    print(f"Evaluating θ = [alpha: {theta[0]:.3f}, cog_payday: {theta[1]:.3f}] --> SSE Loss: {error:.4f}")
    return error

def run_smm():
    print("Initializing Simulated Method of Moments (SMM) Estimator...\n")
    
    with open('target_moments.json', 'r') as f:
        targets = json.load(f)
        
    target_vec = np.array([targets['m_payday'], targets['m_pay_min']])
    print(f"Empirical Targets: m_payday = {target_vec[0]:.4f}, m_pay_min = {target_vec[1]:.4f}\n")
    
    # Load a 1,000-agent subset for rapid algorithmic optimization
    households = load_empirical_households(csv_path='public2025.csv', sample_size=1000)
    
    # Initial Guesses
    theta0 = np.array([0.5, 0.1]) 
    
    # Mathematical bounds: alpha between [0.1, 1.0], cog_payday between [0.01, 0.5]
    bounds = ((0.1, 1.0), (0.01, 0.5))
    
    print("\nCommencing Nelder-Mead Optimization Grid...")
    res = minimize(objective, theta0, args=(households, target_vec), 
                   method='Nelder-Mead', bounds=bounds, options={'maxiter': 30})
                   
    print("\n" + "="*60)
    print("SMM ESTIMATION COMPLETE: LATENT VARIABLES RECOVERED")
    print("="*60)
    print(f"Optimal Stress Elasticity (alpha):       {res.x[0]:.4f}")
    print(f"Optimal Cognitive Friction (cog_payday): {res.x[1]:.4f}")
    print(f"Final Model Loss (SSE):                  {res.fun:.6f}")
    print("="*60)

if __name__ == "__main__":
    run_smm()