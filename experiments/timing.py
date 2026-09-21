"""Experiment 2 - Does the TIMING of an identical transfer matter, and does attention change that?"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *

DELAYS = [0, 1, 2, 3, 4, 6, 9, 12]
EARLY, LATE = 0, 6

def arm(world, mult, delay, amount, shock=SHOCK_SIZE):
    return simulate(world, shock, mult, transfer_factory(amount, world.onset + delay))

def main(world=None):
    world = world or build_world()
    none = {m: simulate(world, SHOCK_SIZE, mult) for m, mult in [("A", 1.0), ("B", 0.0)]}
    rows, store = [], {}

    for variant in ["nominal", "pv_adjusted"]:
        for m, mult in [("A", 1.0), ("B", 0.0)]:
            for d in DELAYS:
                amt = AMOUNT if variant == "nominal" else pv_adjusted_amount(AMOUNT, d, PARAMS.r_formal_high)
                out = arm(world, mult, d, amt)
                store[(variant, m, d)] = out
                dnw = (out.nw_final - none[m].nw_final).values
                mean, se, (lo, hi) = paired_summary(dnw)
                rows.append({"variant": variant, "model": m, "delay_months": d, "amount": amt,
                             "mean_gain_nw": mean, "se": se, "ci_lo": lo, "ci_hi": hi,
                             "share_severe": out.severe.mean(),
                             "reduction_in_severe_share": none[m].severe.mean() - out.severe.mean(),
                             "mean_cost_of_inattention": out.cum_inattention_cost.mean()})
    tab = save_table(pd.DataFrame(rows), "timing_effects")

    contrast = []
    for variant in ["nominal", "pv_adjusted"]:
        gap = {}
        for m in ["A", "B"]:
            d = (store[(variant, m, EARLY)].nw_final - store[(variant, m, LATE)].nw_final).values
            gap[m] = d
            mean, se, ci = paired_summary(d)
            contrast.append({"variant": variant, "contrast": f"early(0) - late({LATE}), model {m}",
                             "mean": mean, "se": se, "ci_lo": ci[0], "ci_hi": ci[1]})
        did = gap["A"] - gap["B"]
        mean, se, ci = paired_summary(did)
        contrast.append({"variant": variant, "contrast": "DiD: (A gap) - (B gap) = added value of early aid from attention channel",
                         "mean": mean, "se": se, "ci_lo": ci[0], "ci_hi": ci[1]})
    contrast = save_table(pd.DataFrame(contrast), "timing_headline_contrasts")

    dbl = arm(world, 1.0, LATE, 2 * AMOUNT)
    mag = paired_summary((dbl.nw_final - store[("nominal", "A", LATE)].nw_final).values)
    tim = paired_summary((store[("nominal", "A", EARLY)].nw_final - store[("nominal", "A", LATE)].nw_final).values)
    magtim = pd.DataFrame([
        {"comparison (model A)": f"double the amount (${2*AMOUNT:,.0f} vs ${AMOUNT:,.0f}), both at delay {LATE}",
         "mean gain in final net worth ($)": mag[0], "se": mag[1]},
        {"comparison (model A)": f"same ${AMOUNT:,.0f}, delay 0 instead of {LATE}",
         "mean gain in final net worth ($)": tim[0], "se": tim[1]}])
    magtim = save_table(magtim, "timing_vs_magnitude")

    trig = []
    for m, mult in [("A", 1.0), ("B", 0.0)]:
        out = simulate(world, SHOCK_SIZE, mult,
                       lambda i: StateTriggeredTransfer(AMOUNT, 250.0, min_period=world.onset))
        treated = out.total_transfer > 0
        trig.append({"model": m, "share_receiving_aid": treated.mean(),
                     "mean_delay_months_after_onset": (out.delivered_at[treated] - world.onset).mean(),
                     "mean_gain_nw_all": (out.nw_final - none[m].nw_final).mean(),
                     "mean_gain_nw_if_treated": (out.nw_final - none[m].nw_final)[treated].mean(),
                     "share_severe": out.severe.mean(),
                     "early_calendar_share_severe": store[("nominal", m, 0)].severe.mean(),
                     "no_aid_share_severe": none[m].severe.mean()})
    trig = save_table(pd.DataFrame(trig), "timing_state_triggered")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, variant in zip(axes, ["nominal", "pv_adjusted"]):
        for m, col in [("A", "C0"), ("B", "C1")]:
            s = tab[(tab.variant == variant) & (tab.model == m)]
            ax.errorbar(s.delay_months, s.mean_gain_nw, yerr=1.96 * s.se, marker="o", color=col,
                        capsize=3, label=("A: attention on" if m == "A" else "B: attention off"))
        ax.set_title("same dollars" if variant == "nominal" else "same present value")
        ax.set_xlabel("months after shock onset that the transfer arrives")
    axes[0].set_ylabel(f"mean gain in final net worth vs no aid ($)")
    axes[0].legend()
    fig.suptitle(f"Figure 3. Value of a ${AMOUNT:,.0f} transfer by delivery delay (95% CI, paired)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig3_intervention_timing.png"), dpi=140); plt.close(fig)

    return {"effects": tab, "contrast": contrast, "magtim": magtim, "triggered": trig}

if __name__ == "__main__":
    pd.set_option("display.width", 200)
    out = main()
    print("Timing generated.")