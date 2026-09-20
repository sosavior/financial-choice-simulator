import sys
import os

# Add the project root to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.household import Household
from src.model.choice_set import Action, ChoiceSet
from src.model.simulation import Simulation
from src.model.intervention import Intervention

def create_base_household():
    """Helper function to guarantee identical starting states."""
    return Household(
        initial_balance=1000.0, 
        debt=5000.0, 
        obligations=1200.0, 
        base_income=1500.0,
        attention_sensitivity=0.6
    )

def run_intervention_experiment():
    universal_actions = [
        Action(name="Pay in Full", immediate_cost=0.0, cognitive_cost=0.1),
        Action(name="Standard Min Payment", immediate_cost=50.0, cognitive_cost=0.2),
        Action(name="Complex Refinance", immediate_cost=10.0, cognitive_cost=0.8),
        Action(name="Payday Loan", immediate_cost=150.0, cognitive_cost=0.1)
    ]
    choice_set = ChoiceSet(universal_actions)
    
    # We use random_seed=42 for all three to ensure identical stochastic shocks.
    # Scenario 1: Control (No Intervention)
    sim_control = Simulation(create_base_household(), choice_set, 
                             periods=12, shock_prob=0.3, shock_size=-600.0, random_seed=42)
    sim_control.run()

    # Scenario 2: Early Intervention (Month 2)
    early_policy = Intervention(name="Early Transfer", amount=600.0, target_period=2)
    sim_early = Simulation(create_base_household(), choice_set, 
                           periods=12, shock_prob=0.3, shock_size=-600.0, 
                           intervention=early_policy, random_seed=42)
    sim_early.run()

    # Scenario 3: Late Intervention (Month 8)
    late_policy = Intervention(name="Late Transfer", amount=600.0, target_period=8)
    sim_late = Simulation(create_base_household(), choice_set, 
                          periods=12, shock_prob=0.3, shock_size=-600.0, 
                          intervention=late_policy, random_seed=42)
    sim_late.run()

    # Output Results
    print(f"{'Scenario':<20} | {'Final Balance':<15} | {'Final Attention Capacity'}")
    print("-" * 65)
    print(f"{'Control (None)':<20} | ${sim_control.household.balance:<14.2f} | {sim_control.household.attention:.2f}")
    print(f"{'Early (Month 2)':<20} | ${sim_early.household.balance:<14.2f} | {sim_early.household.attention:.2f}")
    print(f"{'Late (Month 8)':<20} | ${sim_late.household.balance:<14.2f} | {sim_late.household.attention:.2f}")

if __name__ == "__main__":
    run_intervention_experiment()