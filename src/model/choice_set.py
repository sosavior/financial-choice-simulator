from dataclasses import dataclass
from typing import List, Optional
from .household import Household, PeriodContext
from .params import Params, PAY_MIN, REFI, DEFER, PAYDAY

EPS = 1e-9

@dataclass(frozen=True)
class Action:
    name: str
    cognitive_cost: float

@dataclass
class Decision:
    chosen: Action
    feasible: List[Action]
    accessible: List[Action]
    cost_gap: float          

def default_actions(params: Optional[Params] = None) -> List[Action]:
    p = params or Params()
    return [Action(PAY_MIN, p.cog_pay_min), Action(REFI, p.cog_refi),
            Action(DEFER, p.cog_defer), Action(PAYDAY, p.cog_payday)]

class ChoiceSet:
    def __init__(self, actions: List[Action], params: Optional[Params] = None):
        self.actions = list(actions)
        self.p = params or Params()

    def is_feasible(self, a: Action, hh: Household, ctx: PeriodContext) -> bool:
        X, R = ctx.resources, ctx.required
        if a.name == PAY_MIN:
            return X >= R - EPS
        if a.name == REFI:
            return (ctx.refi_offer and (not hh.refinanced)
                    and X >= R + self.p.refi_fee - EPS)
        if a.name == DEFER:
            return ctx.pay_payday - EPS <= X < R - EPS
        if a.name == PAYDAY:
            return X < R - EPS
        raise ValueError(a.name)

    def get_feasible_actions(self, hh: Household, ctx: PeriodContext) -> List[Action]:
        return [a for a in self.actions if self.is_feasible(a, hh, ctx)]

    def get_accessible_actions(self, hh: Household, ctx: PeriodContext,
                               feasible: Optional[List[Action]] = None) -> List[Action]:
        feasible = self.get_feasible_actions(hh, ctx) if feasible is None else feasible
        return [a for a in feasible if a.cognitive_cost <= hh.attention + EPS]

    def expected_cost(self, a: Action, hh: Household, ctx: PeriodContext) -> float:
        p, H = self.p, self.p.horizon
        if a.name == PAY_MIN:
            return 0.0
        if a.name == REFI:
            balance_after = ctx.d_hat - ctx.pay_formal
            return p.refi_fee - H * balance_after * (hh.rate - p.r_formal_low)
        if a.name == DEFER:
            return p.defer_fee + H * hh.rate * ctx.pay_formal
        if a.name == PAYDAY:
            loan, gap = hh.payday_split(ctx)
            return (loan * (p.payday_fee + p.r_payday * H)
                    + gap * (p.late_fee_rate + hh.rate * H))
        raise ValueError(a.name)

    def choose(self, hh: Household, ctx: PeriodContext) -> Decision:
        feasible = self.get_feasible_actions(hh, ctx)
        accessible = self.get_accessible_actions(hh, ctx, feasible)
        if not accessible:
            raise RuntimeError("empty accessible set")
        costs = {a.name: self.expected_cost(a, hh, ctx) for a in feasible}
        chosen = min(accessible, key=lambda a: (costs[a.name], a.cognitive_cost, a.name))
        gap = costs[chosen.name] - min(costs.values())
        return Decision(chosen, feasible, accessible, max(0.0, gap))