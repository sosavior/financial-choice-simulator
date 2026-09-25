from dataclasses import dataclass
from typing import Optional

class Intervention:
    def transfer(self, t: int, household) -> float:
        return 0.0

class NoIntervention(Intervention):
    pass

@dataclass
class LiquidityTransfer(Intervention):
    amount: float
    period: int
    def transfer(self, t: int, household) -> float:
        return self.amount if t == self.period else 0.0

@dataclass
class StateTriggeredTransfer(Intervention):
    amount: float
    balance_below: float
    min_period: int = 0
    delivered: bool = False
    delivered_at: Optional[int] = None

    def transfer(self, t: int, household) -> float:
        if (not self.delivered) and t >= self.min_period and household.balance < self.balance_below:
            self.delivered = True
            self.delivered_at = t
            return self.amount
        return 0.0

def pv_adjusted_amount(amount: float, delay: int, monthly_rate: float) -> float:
    return amount * (1.0 + monthly_rate) ** delay