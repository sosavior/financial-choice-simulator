"""Experiment 3 - Who benefits from acting early? Early(0)-late(6) gap by baseline characteristics."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *
from timing import EARLY, LATE

def main(world=None):
    world = world or build_world()
    g = {}
    for m, mult in [("A", 1.0), ("B", 0.0)]:
        for d in (EARLY, LATE):
            g[(m, d)] = simulate(world, SHOCK_SIZE, mult, transfer_factory(AMOUNT, world.onset + d)).nw_final.values
            
    gapA, gapB = g[("A", EARLY)] - g[("A", LATE)], g[("B", EARLY)] - g[("B", LATE)]
    p = world.pop
    
    groupings = {
        "initial balance": pd.qcut(p["balance"], 4, labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]),
        "attention sensitivity alpha": pd.qcut(p["alpha"], 4, labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]),
        "shock spell length": pd.cut(world.spell_len, [0, 3, 11, 100], labels=["short (<=3 mo)", "medium (4-11)", "long (>=12)"]),
    }
    
    rows = []
    for var, lab in groupings.items():
        lab = np.asarray(lab)
        for level in pd.unique(lab):
            idx = lab == level
            a, b = gapA[idx], gapB[idx]
            ma, sa, _ = paired_summary(a); mb, sb, _ = paired_summary(b); md, sd, _ = paired_summary(a - b)
            rows.append({"grouping": var, "group": str(level), "n": int(idx.sum()),
                         "gap_A": ma, "se_A": sa, "gap_B": mb, "se_B": sb,
                         "attention_added_value(A-B)": md, "se_diff": sd})
                         
    tab = save_table(pd.DataFrame(rows), "heterogeneity_early_vs_late")
    
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, var in zip(axes, groupings):
        s = tab[tab.grouping == var]
        x = np.arange(len(s))
        ax.bar(x - 0.2, s.gap_A, 0.4, yerr=1.96 * s.se_A, label="A: attention on", capsize=3)
        ax.bar(x + 0.2, s.gap_B, 0.4, yerr=1.96 * s.se_B, label="B: attention off", capsize=3)
        ax.set_xticks(x); ax.set_xticklabels(s.group, fontsize=8, rotation=15); ax.set_title(var, fontsize=10)
    axes[0].set_ylabel("early - late gain in final net worth ($)"); axes[0].legend(fontsize=8)
    fig.suptitle("Figure 5. Heterogeneity in the value of early (month 0) vs late (month 6) aid")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig5_heterogeneity.png"), dpi=140); plt.close(fig)
    return {"table": tab}

if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print("Heterogeneity generated.")
    main()