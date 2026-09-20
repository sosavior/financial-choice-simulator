from typing import List
from .household import Household

class Action:
    """
    A specific financial choice available to a household in the universe of actions A.
    """
    def __init__(self, name: str, immediate_cost: float, cognitive_cost: float = 0.1):
        self.name = name
        self.immediate_cost = immediate_cost
        
        # How much cognitive bandwidth (attention) is required to discover/evaluate this option
        # A simple default payday loan might be 0.1, while a complex refinancing might be 0.8
        self.cognitive_cost = cognitive_cost 

class ChoiceSet:
    """
    Evaluates the feasible and accessible choices for a given household state.
    """
    def __init__(self, universal_actions: List[Action]):
        self.universal_actions = universal_actions

    def get_feasible_actions(self, household: Household) -> List[Action]:
        """
        Returns actions technically affordable given current liquidity.
        C_t = {a in A : Cost(a) <= B_t + Y_t}
        """
        available_liquidity = household.balance + household.income
        return [
            action for action in self.universal_actions
            if action.immediate_cost <= available_liquidity
        ]

    def get_accessible_actions(self, household: Household) -> List[Action]:
        """
        Returns actions the household actually evaluates, constrained by cognitive bandwidth.
        C_tilde_t = {a in C_t : CognitiveCost(a) <= A_t}
        """
        feasible_actions = self.get_feasible_actions(household)
        
        # Filter out actions that require more attention than the household currently possesses
        return [
            action for action in feasible_actions
            if action.cognitive_cost <= household.attention
        ]