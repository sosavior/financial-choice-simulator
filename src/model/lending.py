"""
Dynamic credit tiering and predatory rollover mechanism.
Models how borrowing rates scale endogenously with household distress and attention.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class CreditTerms:
    principal: float
    apr: float
    origination_fee: float
    min_payment: float
    is_predatory: bool


class DynamicCreditMarket:
    def __init__(
        self,
        prime_rate: float = 0.08,
        subprime_max_rate: float = 0.36,
        predatory_rate: float = 3.91,  # Typical ~400% APR payday rate annualized
        distress_threshold: float = 0.70,
    ):
        self.prime_rate = prime_rate
        self.subprime_max_rate = subprime_max_rate
        self.predatory_rate = predatory_rate
        self.distress_threshold = distress_threshold

    def evaluate_terms(
        self,
        amount_needed: float,
        liquidity: float,
        monthly_income: float,
        attention_level: float,
    ) -> CreditTerms:
        """
        Calculates loan terms based on balance-sheet distress and available cognitive bandwidth.
        Lower attention restricts the household from shopping for prime alternatives.
        """
        # Debt-to-liquidity distress indicator (0.0 to 1.0)
        liquidity_buffer = max(liquidity, 0.0)
        income_coverage = liquidity_buffer / max(monthly_income, 1.0)
        raw_distress = np.clip(1.0 - (income_coverage / 2.0), 0.0, 1.0)

        # Attention deficit locks out prime search, forcing reliance on immediate storefront liquidity
        effective_distress = 0.6 * raw_distress + 0.4 * (1.0 - np.clip(attention_level, 0.0, 1.0))

        if effective_distress >= self.distress_threshold:
            # Pushed into short-term predatory liquidity / payday rollover
            apr = self.predatory_rate
            fee = max(15.0, 0.15 * amount_needed)  # Standard $15 per $100 borrowed
            min_payment = amount_needed + fee
            return CreditTerms(
                principal=amount_needed,
                apr=apr,
                origination_fee=fee,
                min_payment=min_payment,
                is_predatory=True,
            )

        # Tiered non-predatory credit
        apr = self.prime_rate + (self.subprime_max_rate - self.prime_rate) * effective_distress
        fee = 0.0
        min_payment = (amount_needed * (apr / 12.0)) + (0.02 * amount_needed)
        return CreditTerms(
            principal=amount_needed,
            apr=apr,
            origination_fee=fee,
            min_payment=min_payment,
            is_predatory=False,
        )