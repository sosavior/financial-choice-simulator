import sys
import os
import random

# Add the project root to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.household import Household
from src.model.choice_set import Action, ChoiceSet
from src.model.simulation import Simulation
from src.model.intervention import Intervention

def run_monte_carlo(iterations: int = 10000):
    universal_actions = [
        Action(name="Pay in Full", immediate_cost=0.0, cognitive_cost=0.1),
        Action(name="Standard Min Payment", immediate_cost=50.0, cognitive_cost=0.2),
        Action(name="Complex Refinance", immediate_cost=10.0, cognitive_cost=0.8),
        Action(name="Payday Loan", immediate_cost=150.0, cognitive_cost=0.1)
    ]
    choice_set = ChoiceSet(universal_actions)
    
    # Dictionaries to track aggregate outcomes
    results = {
        "Control (None)": {"final_balances": [], "severe_constraint_count": 0},
        "Early (Month 2)": {"final_balances": [], "severe_constraint_count": 0},
        "Late (Month 8)": {"final_balances": [], "severe_constraint_count": 0}
    }
    
    print(f"Running Monte Carlo Simulation with {iterations:,} iterations...")
    print("This may take a few seconds...\n")
    
    for i in range(iterations):
        # A unique seed for this specific parallel universe, applied to all three groups
        universe_seed = random.randint(0, 1000000)
        
        # Helper to generate identical starting households
        def new_household():
            return Household(initial_balance=1000.0, debt=5000.0, obligations=1200.0, 
                             base_income=1500.0, attention_sensitivity=0.6)
        
        # 1. Control
        sim_control = Simulation(new_household(), choice_set, periods=12, 
                                 shock_prob=0.3, shock_size=-600.0, random_seed=universe_seed)
        sim_control.run()
        results["Control (None)"]["final_balances"].append(sim_control.household.balance)
        if sim_control.household.attention < 0.8: # Threshold where they lose "Complex Refinance"
            results["Control (None)"]["severe_constraint_count"] += 1
            
        # 2. Early Intervention
        sim_early = Simulation(new_household(), choice_set, periods=12, 
                               shock_prob=0.3, shock_size=-600.0, 
                               intervention=Intervention("Early", 600.0, 2), random_seed=universe_seed)
        sim_early.run()
        results["Early (Month 2)"]["final_balances"].append(sim_early.household.balance)
        if sim_early.household.attention < 0.8:
            results["Early (Month 2)"]["severe_constraint_count"] += 1

        # 3. Late Intervention
        sim_late = Simulation(new_household(), choice_set, periods=12, 
                              shock_prob=0.3, shock_size=-600.0, 
                              intervention=Intervention("Late", 600.0, 8), random_seed=universe_seed)
        sim_late.run()
        results["Late (Month 8)"]["final_balances"].append(sim_late.household.balance)
        if sim_late.household.attention < 0.8:
            results["Late (Month 8)"]["severe_constraint_count"] += 1

    # Output statistical aggregates
    print(f"{'Scenario':<20} | {'Avg Final Balance':<18} | {'Constraint Probability'}")
    print("-" * 65)
    for name, data in results.items():
        avg_balance = sum(data["final_balances"]) / iterations
        prob_constraint = (data["severe_constraint_count"] / iterations) * 100
        print(f"{name:<20} | ${avg_balance:<17.2f} | {prob_constraint:.1f}%")

if __name__ == "__main__":
    run_monte_carlo()