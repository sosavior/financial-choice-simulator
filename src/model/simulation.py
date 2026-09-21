from typing import Dict, List, Optional, Sequence
import numpy as np
from .choice_set import ChoiceSet
from .household import Household
from .intervention import Intervention, NoIntervention
from .params import PAY_MIN, REFI, DEFER, PAYDAY

class Simulation:
    def __init__(self, household: Household, choice_set: ChoiceSet, shock_path: np.ndarray,
                 shock_size: float = 0.4, intervention: Optional[Intervention] = None,
                 onset: Optional[int] = None, snapshot_periods: Sequence[int] = (),
                 offer_path: Optional[np.ndarray] = None):
        self.hh = household
        self.cs = choice_set
        self.shock_path = np.asarray(shock_path, dtype=bool)
        self.T = len(self.shock_path)
        self.shock_size = shock_size
        self.intervention = intervention or NoIntervention()
        self.onset = onset
        self.offer_path = (np.ones(self.T, dtype=bool) if offer_path is None
                           else np.asarray(offer_path, dtype=bool))
        self.snapshot_periods = set(snapshot_periods)
        self.history: List[Dict] = []
        self.initial_net_worth = household.net_worth
        self.snapshots: Dict[int, float] = {}

    def run(self) -> List[Dict]:
        hh = self.hh
        for t in range(self.T):
            active = bool(self.shock_path[t])
            income_t = hh.income * (1.0 - self.shock_size) if active else hh.income
            transfer = self.intervention.transfer(t, hh)
            ctx = hh.begin_period(t, income_t, transfer, bool(self.offer_path[t]))
            dec = self.cs.choose(hh, ctx)
            flows = hh.apply_action(dec.chosen.name, ctx)
            self.history.append({
                "t": t, "shock": active, "income": income_t, "transfer": transfer,
                "obligations": hh.obligations, "action": dec.chosen.name,
                "n_feasible": len(dec.feasible), "n_accessible": len(dec.accessible),
                "cost_gap": dec.cost_gap, "attention": hh.attention, "stress": ctx.stress,
                "interest": flows["interest"], "fees": flows["fees"], "loan": flows["loan"], "gap": flows["gap"],
                "balance": hh.balance, "debt": hh.debt, "payday_debt": hh.payday_debt,
                "net_worth": hh.net_worth,
            })
            if t in self.snapshot_periods:
                self.snapshots[t] = hh.net_worth
        return self.history

    def outcomes(self) -> Dict[str, float]:
        h = self.history
        hh = self.hh
        start = self.onset if self.onset is not None else 0
        win = [r for r in h if r["t"] >= start]
        n = max(1, len(win))
        acts = [r["action"] for r in h]
        peak_pd = max(r["payday_debt"] for r in h)
        out = {
            "nw_final": h[-1]["net_worth"],
            "balance_final": h[-1]["balance"],
            "debt_final": h[-1]["debt"],
            "payday_final": h[-1]["payday_debt"],
            "total_interest": sum(r["interest"] for r in h),
            "total_fees": sum(r["fees"] for r in h),
            "total_transfer": sum(r["transfer"] for r in h),
            "months_payday_debt": sum(r["payday_debt"] > 1.0 for r in h),
            "peak_payday_over_income": peak_pd / hh.income,
            "severe": float(peak_pd > 0.5 * hh.income),
            "ever_payday_loan": float(PAYDAY in acts),
            "months_in_arrears": sum(r["gap"] > 1e-9 for r in h),
            "ever_refinanced": float(hh.refinanced),
            "n_refi": acts.count(REFI), "n_defer": acts.count(DEFER),
            "n_payday": acts.count(PAYDAY),
            "cum_inattention_cost": sum(r["cost_gap"] for r in h),
            "months_with_foregone_option": sum(r["cost_gap"] > 1e-9 for r in h),
            "mean_contraction": sum(r["n_feasible"] - r["n_accessible"] for r in win) / n,
            "mean_accessible": sum(r["n_accessible"] for r in win) / n,
            "min_attention": min(r["attention"] for r in h),
            "final_attention": h[-1]["attention"],
        }
        for s, v in self.snapshots.items():
            out[f"nw_at_{s}"] = v
        return out