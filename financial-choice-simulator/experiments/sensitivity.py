"""Experiment 4 - How fragile are the timing conclusions to the assumed parameters?"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dataclasses import replace
from common import *
from timing import EARLY, LATE

N_SENS = 1000

def cell(world, shock=SHOCK_SIZE, alpha_mult=1.0, params=PARAMS, amount=AMOUNT):
    res = {}
    for m, mult in [("A", alpha_mult), ("B", 0.0)]:
        for d in (EARLY, LATE):
            res[(m, d)] = simulate(world, shock, mult, transfer_factory(amount, world.onset + d), params).nw_final.values
    gA, gB = res[("A", EARLY)] - res[("A", LATE)], res[("B", EARLY)] - res[("B", LATE)]
    ma, sa, _ = paired_summary(gA); mb, sb, _ = paired_summary(gB); md, sd, _ = paired_summary(gA - gB)
    return {"gap_A": ma, "se_A": sa, "gap_B": mb, "se_B": sb, "attention_added(A-B)": md, "se_added": sd}

def main():
    base = build_world(N_SENS)
    shocks, mults = [0.20, 0.30, 0.40], [0.5, 1.0, 1.5, 2.0]
    grid = []
    for s in shocks:
        for k in mults:
            grid.append({"shock_size": s, "alpha_mult": k, **cell(base, shock=s, alpha_mult=k)})
    grid = save_table(pd.DataFrame(grid), "sensitivity_grid")
    
    oat = []
    def add(name, value, **kw):
        oat.append({"parameter": name, "value": value, **cell(**kw)})
        
    for r in [0.2, 0.4, 0.7, 1.0]:
        add("rho (attention adjustment speed)", r, world=base, params=replace(PARAMS, rho=r))
    for r in [0.06, 0.12, 0.20]:
        add("payday monthly rate", r, world=base, params=replace(PARAMS, r_payday=r))
    for c in [0.5, 0.7, 0.9]:
        add("cognitive cost of refinancing", c, world=base, params=replace(PARAMS, cog_refi=c))
    for c in [0.4, 0.6, 0.8]:
        add("cognitive cost of deferral", c, world=base, params=replace(PARAMS, cog_defer=c))
    for h in [6, 12, 24]:
        add("decision horizon (months)", h, world=base, params=replace(PARAMS, horizon=h))
    for a in [750.0, 1500.0, 3000.0]:
        add("transfer amount ($)", a, world=base, amount=a)
    for q in [0.05, 0.15, 0.30]:
        add("refinance-offer probability", q, world=build_world(N_SENS, p_offer=q))
    for sm in [4, 8, 12]:
        add("mean shock-spell length (months)", sm, world=build_world(N_SENS, spell_mean=sm))
    oat = save_table(pd.DataFrame(oat), "sensitivity_one_at_a_time")
    
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax, col, ttl in [(axes[0], "gap_A", "early - late gap, Model A ($)"),
                         (axes[1], "attention_added(A-B)", "added by attention channel (A - B) ($)")]:
        M = grid.pivot(index="shock_size", columns="alpha_mult", values=col)
        im = ax.imshow(M.values, aspect="auto", origin="lower")
        ax.set_xticks(range(len(mults))); ax.set_xticklabels(mults); ax.set_yticks(range(len(shocks))); ax.set_yticklabels(shocks)
        ax.set_xlabel("attention sensitivity multiplier"); ax.set_ylabel("income loss during shock"); ax.set_title(ttl, fontsize=10)
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                ax.text(j, i, f"{M.values[i, j]:.0f}", ha="center", va="center", color="w", fontsize=9)
        fig.colorbar(im, ax=ax)
    fig.suptitle("Figure 4. Sensitivity of the timing result (N=1000 per cell)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig4_sensitivity_heatmap.png"), dpi=140); plt.close(fig)
    
    fig, ax = plt.subplots(figsize=(8, 7))
    labels = [f"{r.parameter} = {r.value}" for r in oat.itertuples()]
    y = np.arange(len(oat))
    ax.errorbar(oat["attention_added(A-B)"], y, xerr=1.96 * oat.se_added, fmt="o", capsize=3)
    ax.axvline(0, color="k", lw=.6); ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=7); ax.invert_yaxis()
    ax.set_xlabel("attention channel's added value of early over late aid ($, 95% CI)")
    ax.set_title("Figure 6. Robustness, one parameter at a time")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig6_robustness.png"), dpi=140); plt.close(fig)
    return {"grid": grid, "oat": oat}

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    main()
    print("Sensitivity generated.")