from .household import Household

class Intervention:
    """
    Represents an exogenous policy intervention applied to a household.
    """
    def __init__(self, name: str, amount: float, target_period: int):
        self.name = name
        self.amount = amount  # The size of the liquidity transfer
        self.target_period = target_period
        
    def apply(self, household: Household, current_period: int) -> bool:
        """
        Applies the intervention if the current period matches the target.
        Returns True if the intervention triggered, False otherwise.
        """
        if current_period == self.target_period:
            # Inject liquidity directly into the household balance
            household.balance += self.amount
            
            # Immediately recalculate cognitive bandwidth, as the financial stress 
            # has been artificially relieved by the intervention.
            household.update_attention()
            return True
            
        return False