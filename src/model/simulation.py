import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from .params import Params, PAY_MIN, REFI, DEFER, PAYDAY
from .choice_set import ChoiceSet, Action
from .empirical_agents import load_empirical_households

def run_simulation(households, p_shock=0.4335, shock_amount=400.0, friction_multiplier=1.0, periods=12):
    """
    Executes the cognitive friction simulation over H periods using empirical agents.
    Tracks deterministic capture into high-friction debt traps.
    """
    params = Params()
    
    # Scale administrative sludge (cognitive cost of refinancing/deferring) based on the multiplier
    custom_actions = [
        Action(PAY_MIN, params.cog_pay_min),
        Action(PAYDAY, params.cog_payday),
        Action(REFI, min(1.0, params.cog_refi * friction_multiplier)),
        Action(DEFER, min(1.0, params.cog_defer * friction_multiplier))
    ]
    choice_set = ChoiceSet(custom_actions, params)
    
    capture_count = 0
    
    for hh in households:
        captured = False
        for t in range(periods):
            # Stochastic Shock: Fed SHED empirical probability (baseline = 0.4335)
            # Modeled as a direct hit to liquid resources via negative transfer
            shock = shock_amount if np.random.rand() < p_shock else 0.0
            
            # Continuous bandwidth and state update
            ctx = hh.begin_period(t, income_t=hh.income, transfer=-shock, refi_offer=True)
            
            try:
                decision = choice_set.choose(hh, ctx)
                hh.apply_action(decision.chosen.name, ctx)
                
                # If they default to payday due to cognitive depletion or strict feasibility
                if decision.chosen.name == PAYDAY:
                    captured = True
            except RuntimeError:
                # Empty accessible set = complete systemic collapse / floor absorption
                captured = True
                break
                
        if captured:
            capture_count += 1
            
    # Return percentage of households captured by the debt trap
    return (capture_count / len(households)) * 100.0


def generate_heatmap():
    """
    Monte Carlo 2D Sweep: Maps vulnerability across friction multipliers and shock probabilities.
    """
    print("Executing Empirical Sensitivity Sweep...")
    
    # Define grid boundaries
    friction_levels = np.linspace(0.5, 2.0, 5) # 0.5x to 2.0x administrative sludge
    shock_probs = np.linspace(0.2, 0.6, 5)     # 20% to 60% shock likelihood
    results = np.zeros((len(friction_levels), len(shock_probs)))
    
    # Run the grid
    total_runs = len(friction_levels) * len(shock_probs)
    current_run = 1
    
    for i, f_mult in enumerate(friction_levels):
        for j, p_shock in enumerate(shock_probs):
            print(f"Run {current_run}/{total_runs} | Friction: {f_mult:.2f}x | Shock Prob: {p_shock:.2f}")
            
            # Re-initialize fresh empirical agents for independent runs
            hh_run = load_empirical_households(csv_path='public2025.csv', sample_size=5000)
            
            capture_rate = run_simulation(hh_run, p_shock=p_shock, friction_multiplier=f_mult)
            results[i, j] = capture_rate
            current_run += 1
            
    # Render the empirical heatmap
    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(results, annot=True, fmt=".1f", cmap="flare", 
                     xticklabels=np.round(shock_probs, 2), 
                     yticklabels=np.round(friction_levels, 2))
    plt.title("Empirical Sensitivity Grid: Vulnerability to Administrative Sludge")
    plt.xlabel("Fed SHED Shock Probability (Baseline = 0.43)")
    plt.ylabel("Cognitive Friction Multiplier")
    
    # Save the asset
    os.makedirs("results", exist_ok=True)
    save_path = "results/sensitivity_heatmap_calibrated.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\nSuccess. Graph saved to {save_path}")

if __name__ == "__main__":
    generate_heatmap()