"""
USRESP 5,000-Agent Stochastic Monte Carlo & 2D Parameter Sweep
Exports sensitivity grid for manuscript inclusion.
"""
import os
import numpy as np
import matplotlib.pyplot as plt

def run_simulation(agents=5000, periods=36, sludge_multiplier=1.2, shock_mu=0.5, shock_sigma=0.3):
    """
    Simulates the depletion of cognitive bandwidth and financial capital
    under stochastic lognormal shocks and continuous administrative sludge.
    """
    np.random.seed(42) # Common random numbers for USRESP replication
    
    capital = np.random.normal(5000, 1000, agents)
    bandwidth = np.random.uniform(0.7, 1.0, agents)
    survival_tracker = np.ones(agents, dtype=bool)
    
    for t in range(periods):
        shocks = np.random.lognormal(mean=shock_mu, sigma=shock_sigma, size=agents)
        bandwidth -= (shocks / capital) * sludge_multiplier * 0.1
        bandwidth = np.clip(bandwidth, 0.01, 1.0)
        
        penalty_rates = 1.0 / bandwidth 
        capital -= (shocks + (penalty_rates * 50)) 
        
        ruined = capital <= 0
        survival_tracker[ruined] = False
        
    return np.sum(survival_tracker) / agents

def execute_2d_sweep():
    print("Executing 5,000-Agent USRESP Stochastic Pipeline...")
    sludge_levels = np.linspace(1.0, 3.0, 5)
    shock_severities = np.linspace(0.2, 0.8, 5)
    results_grid = np.zeros((len(sludge_levels), len(shock_severities)))

    for i, sludge in enumerate(sludge_levels):
        for j, shock in enumerate(shock_severities):
            results_grid[i, j] = run_simulation(sludge_multiplier=sludge, shock_mu=shock)

    # Output routing
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    results_dir = os.path.join(root_dir, "results", "tables")
    os.makedirs(results_dir, exist_ok=True)
    
    output_path = os.path.join(results_dir, "usresp_2d_sweep.csv")
    np.savetxt(output_path, results_grid, delimiter=",", fmt="%.4f")
    
    print(f"USRESP Sensitivity Grid successfully saved to {output_path}")

if __name__ == "__main__":
    execute_2d_sweep()