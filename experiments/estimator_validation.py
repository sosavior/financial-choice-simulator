"""Experiment 6 - Synthetic estimator validation, placebo tests, and a confounding demonstration."""
import numpy as np
import pandas as pd
from common import *
from src.estimation import coverage_study, diff_in_means
from timing import EARLY, LATE

N_POP, N_RCT, REPS = 6000, 1000, 2000

def main():
    world = build_world(N_POP)
    y1 = simulate(world, SHOCK_SIZE, 1.0, transfer_factory(AMOUNT, world.onset + EARLY),
                  snapshot=(world.onset - 1,))
    y0 = simulate(world, SHOCK_SIZE, 1.0, transfer_factory(AMOUNT, world.onset + LATE),
                  snapshot=(world.onset - 1,))
    rng = np.random.default_rng(SEED + 1)
    rows = []
    
    r = coverage_study(y1.nw_final.values, y0.nw_final.values, N_RCT, REPS, rng)
    rows.append({"exercise": "RCT: early vs late aid, difference in means", **r})
    
    pre = y0[f"nw_at_{world.onset - 1}"].values
    r = coverage_study(pre, pre, N_RCT, REPS, rng)
    rows.append({"exercise": "placebo: pre-treatment outcome (true effect = 0)", **r})
    
    r = coverage_study(y1.nw_final.values, y0.nw_final.values, N_RCT, REPS, rng, null=True)
    rows.append({"exercise": "placebo: both arms receive late aid (true effect = 0)", **r})
    
    true = float((y1.nw_final - y0.nw_final).mean())
    bal = world.pop["balance"]
    p_treat = 1 / (1 + np.exp((np.log(bal) - np.log(np.median(bal))) * 2.0))
    ests, cover = [], 0
    
    for _ in range(REPS):
        idx = rng.choice(N_POP, N_RCT, replace=False)
        assign = rng.random(N_RCT) < p_treat[idx]
        if assign.sum() < 10 or (~assign).sum() < 10:
            continue
        yobs = np.where(assign, y1.nw_final.values[idx], y0.nw_final.values[idx])
        est, se, (lo, hi) = diff_in_means(yobs, assign)
        ests.append(est); cover += lo <= true <= hi
        
    ests = np.array(ests)
    rows.append({"exercise": "NON-random assignment (early aid to low-balance households)",
                 "true_effect": true, "mean_estimate": ests.mean(), "bias": ests.mean() - true,
                 "rmse": float(np.sqrt(((ests - true) ** 2).mean())), "ci_coverage": cover / len(ests),
                 "rejection_rate_5pct": np.nan})
                 
    tab = save_table(pd.DataFrame(rows), "estimator_validation")
    return {"table": tab}

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(main()["table"].round(3).to_string(index=False))