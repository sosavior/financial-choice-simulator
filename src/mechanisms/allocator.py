"""
Public assistance allocator comparing administrative friction (sludge)
vs. centralized automated clearing under a fixed municipal budget constraint.
"""

from typing import List, Dict
import numpy as np


class ReliefAllocator:
    def __init__(self, monthly_budget: float, grant_amount: float = 500.0):
        self.monthly_budget = monthly_budget
        self.grant_amount = grant_amount

    def allocate_with_administrative_sludge(
        self,
        applicant_pool: List[Dict],
        paperwork_cognitive_cost: float = 0.35,
    ) -> Dict[str, any]:
        """
        Simulates traditional welfare distribution:
        Households must expend attention to apply.
        Severely depleted households fail to complete verification paperwork.
        """
        remaining_budget = self.monthly_budget
        recipients = []
        dropped_out = []

        # Sort by arrival order / first-come first-served
        shuffled_pool = np.random.permutation(applicant_pool)

        for household in shuffled_pool:
            if remaining_budget < self.grant_amount:
                break

            # If household attention is lower than paperwork friction, application is abandoned
            if household["attention"] < paperwork_cognitive_cost:
                dropped_out.append(household["id"])
                continue

            recipients.append(household["id"])
            remaining_budget -= self.grant_amount

        return {
            "regime": "administrative_sludge",
            "recipients": recipients,
            "dropped_due_to_friction": dropped_out,
            "funds_exhausted": self.monthly_budget - remaining_budget,
            "funds_remaining": remaining_budget,
        }

    def allocate_centralized_optimal(
        self,
        applicant_pool: List[Dict],
    ) -> Dict[str, any]:
        """
        Mechanism Design approach:
        Zero-friction centralized assignment based on objective vulnerability
        (liquidity shortfall * marginal return on avoiding default).
        """
        remaining_budget = self.monthly_budget
        recipients = []

        # Priority ranking: greatest risk of immediate downward spiral
        # Priority score = shortfall normalized by attention deficit
        def priority_score(h):
            shortfall = max(0.0, h["fixed_costs"] - h["liquidity"])
            attention_penalty = 1.0 - max(0.01, h["attention"])
            return shortfall * (1.0 + attention_penalty)

        ranked_applicants = sorted(applicant_pool, key=priority_score, reverse=True)

        for household in ranked_applicants:
            if remaining_budget < self.grant_amount:
                break
            recipients.append(household["id"])
            remaining_budget -= self.grant_amount

        return {
            "regime": "centralized_mechanism",
            "recipients": recipients,
            "dropped_due_to_friction": [],
            "funds_exhausted": self.monthly_budget - remaining_budget,
            "funds_remaining": remaining_budget,
        }