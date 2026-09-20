import random
from typing import List, Optional
from .household import Household
from .choice_set import Action, ChoiceSet
from .intervention import Intervention

class Simulation:
    """
    Runs a discrete-time simulation of a household facing financial constraints.
    """
    def __init__(self, 
                 household: Household, 
                 choice_set: ChoiceSet, 
                 periods: int = 24, 
                 shock_prob: float = 0.2, 
                 shock_size: float = -500.0,
                 intervention: Optional[Intervention] = None,
                 random_seed: int = None):
        
        self.household = household
        self.choice_set = choice_set
        self.periods = periods
        self.shock_prob = shock_prob
        self.shock_size = shock_size
        self.intervention = intervention
        self.results = []
        
        if random_seed is not None:
            random.seed(random_seed)

    def run(self):
        """Executes the simulation over the specified number of periods."""
        for t in range(self.periods):
            # 1. Determine stochastic shock realization
            current_shock = self.shock_size if random.random() < self.shock_prob else 0.0
            
            # 2. Apply exogenous intervention if scheduled for this period
            intervention_triggered = False
            if self.intervention:
                intervention_triggered = self.intervention.apply(self.household, t)
            
            # 3. Evaluate options constrained by current bandwidth
            accessible_actions = self.choice_set.get_accessible_actions(self.household)
            
            # 4. Decision Rule: Household attempts to minimize immediate costs
            if accessible_actions:
                chosen_action = min(accessible_actions, key=lambda a: a.immediate_cost)
                action_cost = chosen_action.immediate_cost
            else:
                # Total constraint: no accessible actions due to zero bandwidth or liquidity
                action_cost = 250.0  # Represents a severe default/late penalty
            
            # 5. Advance the household state (S_t -> S_t+1)
            self.household.step(chosen_action_cost=action_cost, income_shock=current_shock)
            
            # 6. Log the time-series data for analysis
            self.results.append({
                'period': t,
                'shock_applied': current_shock,
                'intervention_triggered': intervention_triggered,
                'accessible_options_count': len(accessible_actions),
                'chosen_action_cost': action_cost
            })
            
        return self.household.history