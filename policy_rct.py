import copy
import numpy as np
from src.model.params import Params, PAY_MIN, REFI, DEFER, PAYDAY
from src.model.choice_set import ChoiceSet, Action
from src.model.empirical_agents import load_empirical_households
from src.model.intervention import LiquidityTransfer, NoIntervention

def simulate_cohort(cohort, choice_set, policy, periods=12):
    """Simulates a cohort over 12 months, tracking debt trap capture rates."""
    captures = 0
    for hh in cohort:
        captured = False
        for t in range(periods):
            # Empirical 0.4335 shock probability (from Fed SHED calibration)
            shock = 400.0 if np.random.rand() < 0.4335 else 0.0
            
            # Inject policy transfer (if any)
            transfer = policy.transfer(t, hh)
            
            # Continuous bandwidth and state update
            ctx = hh.begin_period(t, income_t=hh.income, transfer=transfer - shock, refi_offer=True)
            
            try:
                decision = choice_set.choose(hh, ctx)
                if decision.chosen.name == PAYDAY:
                    captured = True
                    break  # Once trapped, they are counted as captured
                hh.apply_action(decision.chosen.name, ctx)
            except RuntimeError:
                # Systemic cognitive collapse
                captured = True
                break
        
        if captured:
            captures += 1
            
    return captures

def run_rct():
    print("Initializing Synthetic RCT with SMM Parameters...\n")
    
    # 1. Lock in the estimated SMM parameters from the optimization run
    smm_alpha = 0.525
    smm_cog_payday = 0.100
    params = Params(cog_payday=smm_cog_payday)
    
    actions = [
        Action(PAY_MIN, params.cog_pay_min),
        Action(PAYDAY, params.cog_payday),
        Action(REFI, params.cog_refi),
        Action(DEFER, params.cog_defer)
    ]
    choice_set = ChoiceSet(actions, params)
    
    # 2. Load the empirical Fed SHED population (2,000 agents for the RCT)
    population = load_empirical_households(csv_path='public2025.csv', sample_size=2000, seed=42)
    for hh in population:
        hh.alpha = smm_alpha  # Inject the estimated stress elasticity
        
    # Split into perfectly randomized Control and Treatment groups
    control_group = copy.deepcopy(population[:1000])
    treatment_group = copy.deepcopy(population[1000:])
    
    # 3. Define the Interventions
    control_policy = NoIntervention()
    treatment_policy = LiquidityTransfer(amount=500.0, period=2)  # $500 transferred at Month 3
    
    print("Running Control Group (No Intervention)...")
    control_captures = simulate_cohort(control_group, choice_set, control_policy)
    
    print("Running Treatment Group ($500 Cash Transfer at Month 3)...")
    treatment_captures = simulate_cohort(treatment_group, choice_set, treatment_policy)
    
    # 4. Calculate Average Treatment Effect (ATE)
    control_rate = (control_captures / len(control_group)) * 100
    treatment_rate = (treatment_captures / len(treatment_group)) * 100
    ate = control_rate - treatment_rate
    
    print("\n" + "="*65)
    print("SYNTHETIC RCT RESULTS: LIQUIDITY VS. COGNITIVE SLUDGE")
    print("="*65)
    print(f"Control Group Capture Rate:       {control_rate:.1f}%")
    print(f"Treatment Group Capture Rate:     {treatment_rate:.1f}%")
    print("-" * 65)
    print(f"Absolute Treatment Effect (ATE): -{ate:.1f}%")
    print(f"Relative Risk Reduction:          {(ate/control_rate)*100:.1f}%")
    print("="*65)

if __name__ == "__main__":
    run_rct()