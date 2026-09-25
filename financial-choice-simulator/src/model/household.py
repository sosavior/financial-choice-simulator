from dataclasses import dataclass
from typing import Optional
from .params import Params, PAY_MIN, REFI, DEFER, PAYDAY

@dataclass
class PeriodContext:
    t: int
    income: float      
    transfer: float    
    resources: float   
    d_hat: float       
    p_hat: float       
    pay_formal: float  
    pay_payday: float  
    required: float    
    stress: float      
    refi_offer: bool = True   

class Household:
    def __init__(self, income: float, obligations: float, balance: float,
                 debt: float, alpha: float, params: Optional[Params] = None):
        self.p = params or Params()
        self.income = float(income)
        self.obligations = float(obligations)
        self.balance = float(balance)
        self.debt = float(debt)
        self.payday_debt = 0.0
        self.alpha = float(alpha)          
        self.rate = self.p.r_formal_high
        self.refinanced = False
        self.attention = 1.0               

    @property
    def net_worth(self) -> float:
        return self.balance - self.debt - self.payday_debt

    def begin_period(self, t: int, income_t: float, transfer: float = 0.0,
                     refi_offer: bool = True) -> PeriodContext:
        p = self.p
        self.balance += transfer
        d_hat = self.debt * (1.0 + self.rate)
        p_hat = self.payday_debt * (1.0 + p.r_payday)
        pay_formal = p.min_pay_rate * d_hat
        pay_payday = p.r_payday * self.payday_debt
        required = pay_formal + pay_payday
        resources = self.balance + income_t - self.obligations
        stress = min((self.obligations + required) / max(self.balance + income_t, 1.0),
                     p.stress_cap)
        target = min(1.0, max(p.a_min, 1.0 - self.alpha * stress))
        a = (1.0 - p.rho) * self.attention + p.rho * target
        self.attention = min(1.0, max(p.a_min, a))
        return PeriodContext(t, income_t, transfer, resources, d_hat, p_hat,
                             pay_formal, pay_payday, required, stress, bool(refi_offer))

    def payday_split(self, ctx: PeriodContext):
        p = self.p
        shortfall = max(0.0, ctx.required - ctx.resources)
        room = max(0.0, p.payday_cap_months * self.income - self.payday_debt)
        loan = min(shortfall, room / (1.0 + p.payday_fee))
        return loan, shortfall - loan

    def apply_action(self, name: str, ctx: PeriodContext) -> dict:
        p = self.p
        X = ctx.resources
        interest = self.debt * self.rate + self.payday_debt * p.r_payday
        fees = 0.0
        loan = 0.0
        gap = 0.0
        d_after = ctx.d_hat
        p_after = ctx.p_hat

        if name == PAY_MIN:
            new_balance = X - ctx.required
            d_after -= ctx.pay_formal
            p_after -= ctx.pay_payday
        elif name == REFI:
            fees = p.refi_fee
            new_balance = X - ctx.required - fees
            d_after -= ctx.pay_formal
            p_after -= ctx.pay_payday
            self.rate = p.r_formal_low          
            self.refinanced = True
        elif name == DEFER:
            fees = p.defer_fee
            new_balance = X - ctx.pay_payday    
            d_after += fees                     
            p_after -= ctx.pay_payday
        elif name == PAYDAY:
            if ctx.required - X <= 0:
                raise ValueError("PAYDAY chosen without a shortfall")
            loan, gap = self.payday_split(ctx)  
            fees = p.payday_fee * loan + p.late_fee_rate * gap
            new_balance = 0.0                   
            d_after -= ctx.pay_formal
            d_after += gap * (1.0 + p.late_fee_rate)
            p_after = p_after - ctx.pay_payday + loan * (1.0 + p.payday_fee)
        else:
            raise ValueError(f"unknown action {name!r}")

        new_balance = max(0.0, new_balance)
        buffer = p.buffer_months * self.obligations
        excess = new_balance - buffer
        if excess > 0:
            q1 = min(p_after, excess)
            p_after -= q1
            q2 = min(d_after, excess - q1)
            d_after -= q2
            new_balance -= (q1 + q2)
            
        self.balance = new_balance
        self.debt = max(0.0, d_after)
        self.payday_debt = max(0.0, p_after)
        return {"interest": interest, "fees": fees, "loan": loan, "gap": gap}