"""Model parameters. All rates are MONTHLY; all money amounts are dollars.
IMPORTANT: none of these numbers is estimated from data. They are stated
assumptions chosen to be roughly plausible for a US household."""
from dataclasses import dataclass

PAY_MIN = "pay_min"
REFI = "refinance"
DEFER = "defer_payment"
PAYDAY = "payday_loan"

@dataclass(frozen=True)
class Params:
    r_formal_high: float = 0.018   
    r_formal_low: float = 0.009    
    r_payday: float = 0.12         
    payday_fee: float = 0.20       
    min_pay_rate: float = 0.03     
    refi_fee: float = 150.0        
    defer_fee: float = 35.0        
    payday_cap_months: float = 1.0 
    late_fee_rate: float = 0.10    
    horizon: int = 12              
    a_min: float = 0.10            
    rho: float = 0.40              
    stress_cap: float = 3.0        
    buffer_months: float = 0.5     
    cog_pay_min: float = 0.10      
    cog_payday: float = 0.10       
    cog_defer: float = 0.60        
    cog_refi: float = 0.70         

    def __post_init__(self):
        if self.a_min < max(self.cog_pay_min, self.cog_payday):
            raise ValueError("a_min must be >= cognitive cost of PAY_MIN and PAYDAY.")
        if not (0 < self.rho <= 1):
            raise ValueError("rho must be in (0, 1]")
        if self.r_formal_low > self.r_formal_high:
            raise ValueError("refinancing must not raise the rate")