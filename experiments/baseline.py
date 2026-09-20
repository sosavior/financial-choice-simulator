import sys
import os

# Add the project root to the system path so Python can find the src folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.household import Household
from src.model.choice_set import Action, ChoiceSet
from src.model.simulation import Simulation

def run_baseline():
    # 1. Define the universe of financial actions (Universe A)
    universal_actions = [
        Action(name="Pay in Full", immediate_cost=0.0, cognitive_cost=0.1),
        Action(name="Standard Minimum Payment", immediate_cost=50.0, cognitive_cost=0.2),
        Action(name="Complex Refinance", immediate_cost=10.0, cognitive_cost=0.8),
        Action(name="Payday Loan", immediate_cost=150.0, cognitive_cost=0.1)
    ]
    choice_set = ChoiceSet(universal_actions)

    # 2. Initialize a financially strained household
    # High obligations and debt relative to income creates a fragile baseline
    household = Household(
        initial_balance=1000.0, 
        debt=5000.0, 
        obligations=1200.0, 
        base_income=1500.0,
        attention_sensitivity=0.6
    )

    # 3. Run a 12-month simulation with a high probability of negative income shocks
    sim = Simulation(
        household=household, 
        choice_set=choice_set, 
        periods=12, 
        shock_prob=0.3, 
        shock_size=-600.0,
        random_seed=42
    )
    
    print("Starting Baseline Simulation...")
    sim.run()

    # 4. Display the trajectory to observe the feedback loop
    print("\nMonth | Balance  | Attention | Accessible Options | Chosen Action Cost")
    print("-" * 73)
    for t, res in enumerate(sim.results):
        hist = sim.household.history[t]
        print(f"{t:5} | ${hist['balance']:7.2f} | {hist['attention']:9.2f} | {res['accessible_options_count']:18} | ${res['chosen_action_cost']:.2f}")

if __name__ == "__main__":
    run_baseline()