"""Experiment 5 - Universal vs targeted transfers."""
import numpy as np
import pandas as pd
from common import *

def main(world=None):
    world = world or build_world()
    median_bal = np.median(world.pop["balance"])
    rows = []
    
    for m, mult in [("A", 1.0), ("B", 0.0)]:
        none = simulate(world, SHOCK_SIZE, mult)
        arms = {
            "universal (month 1)": lambda i: LiquidityTransfer(AMOUNT, world.onset + 1),
            "means-tested ex ante (balance < median)": lambda i: (LiquidityTransfer(AMOUNT, world.onset + 1)
                                                                  if world.pop["balance"][i] < median_bal else None),
            "state-triggered (balance < $250)": lambda i: StateTriggeredTransfer(AMOUNT, 250.0, min_period=world.onset),
        }
        would_be_severe = none.severe.values > 0
        for name, fac in arms.items():
            out = simulate(world, SHOCK_SIZE, mult, fac)
            cost = out.total_transfer.sum()
            rescued = would_be_severe & (out.severe.values == 0)
            rows.append({"model": m, "policy": name, "share_treated": (out.total_transfer > 0).mean(),
                         "total_cost($)": cost, "share_severe": out.severe.mean(),
                         "rescue_rate (of would-be-severe)": rescued.sum() / max(1, would_be_severe.sum()),
                         "cost_per_rescue($)": cost / max(1, rescued.sum()),
                         "mean_nw_gain_per_$_spent": (out.nw_final - none.nw_final).sum() / cost})
                         
    tab = save_table(pd.DataFrame(rows), "targeting")
    return {"table": tab}

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(main()["table"].round(3).to_string(index=False))