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
    print("Initializing Comparative Synthetic RCT...\n")
    
    smm_alpha = 0.525
    smm_cog_payday = 0.100
    
    # Standard Environment (For Control & Liquidity Treatment)
    params_std = Params(cog_payday=smm_cog_payday)
    choice_set_std = ChoiceSet([
        Action(PAY_MIN, params_std.cog_pay_min),
        Action(PAYDAY, params_std.cog_payday),
        Action(REFI, params_std.cog_refi), # Standard high friction (0.70)
        Action(DEFER, params_std.cog_defer)
    ], params_std)

    # Frictionless Environment (For Sludge Eradication Treatment & Synthesis)
    params_frictionless = Params(cog_payday=smm_cog_payday, cog_refi=0.100) # Friction neutralized
    choice_set_frictionless = ChoiceSet([
        Action(PAY_MIN, params_frictionless.cog_pay_min),
        Action(PAYDAY, params_frictionless.cog_payday),
        Action(REFI, params_frictionless.cog_refi), # Friction neutralized
        Action(DEFER, params_frictionless.cog_defer)
    ], params_frictionless)
    
    # Load population (4,000 agents for 4 distinct cohorts)
    population = load_empirical_households(csv_path='public2025.csv', sample_size=4000, seed=42)
    for hh in population:
        hh.alpha = smm_alpha 
        
    control_group = copy.deepcopy(population[:1000])
    treatment_cash = copy.deepcopy(population[1000:2000])
    treatment_sludge = copy.deepcopy(population[2000:3000])
    treatment_synthesis = copy.deepcopy(population[3000:])
    
    print("Running Control Group (Baseline)...")
    control_captures = simulate_cohort(control_group, choice_set_std, NoIntervention())
    
    print("Running Treatment A ($500 Cash Transfer)...")
    cash_captures = simulate_cohort(treatment_cash, choice_set_std, LiquidityTransfer(amount=500.0, period=2))

    print("Running Treatment B (Sludge Eradication, No Cash)...")
    sludge_captures = simulate_cohort(treatment_sludge, choice_set_frictionless, NoIntervention())
    
    print("Running Treatment C (Synthesis: Cash + Sludge Eradication)...")
    synthesis_captures = simulate_cohort(treatment_synthesis, choice_set_frictionless, LiquidityTransfer(amount=500.0, period=2))
    
    c_rate = (control_captures / len(control_group)) * 100
    t_cash_rate = (cash_captures / len(treatment_cash)) * 100
    t_sludge_rate = (sludge_captures / len(treatment_sludge)) * 100
    t_synthesis_rate = (synthesis_captures / len(treatment_synthesis)) * 100
    
    print("\n" + "="*75)
    print("COMPARATIVE RCT: LIQUIDITY INJECTION VS. SLUDGE ERADICATION")
    print("="*75)
    print(f"Control Capture Rate:                 {c_rate:.1f}%")
    print(f"Treatment A (Cash) Capture Rate:      {t_cash_rate:.1f}% (ATE: {t_cash_rate - c_rate:.1f}%)")
    print(f"Treatment B (Sludge) Capture Rate:    {t_sludge_rate:.1f}% (ATE: {t_sludge_rate - c_rate:.1f}%)")
    print(f"Treatment C (Synthesis) Capture Rate: {t_synthesis_rate:.1f}% (ATE: {t_synthesis_rate - c_rate:.1f}%)")
    print("="*75)

if __name__ == "__main__":
    run_rct()