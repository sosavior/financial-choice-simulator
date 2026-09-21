"""Experiment 1 - Baseline dynamics, Model A (attention on) vs Model B (attention off), NO aid."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *

def main():
    world = build_world()
    rows = {}
    for label, shock in [("no shock", 0.0), ("shock", SHOCK_SIZE)]:
        for model, mult in [("A: attention on", 1.0), ("B: attention off", 0.0)]:
            d = simulate(world, shock_size=shock, alpha_mult=mult)
            rows[(label, model)] = d
            
    table = []
    for (label, model), d in rows.items():
        table.append({
            "scenario": label, "model": model,
            "share severe payday debt": d.severe.mean(),
            "share ever payday loan": d.ever_payday_loan.mean(),
            "share ever refinanced": d.ever_refinanced.mean(),
            "mean months in arrears": d.months_in_arrears.mean(),
            "mean cost of inattention ($)": d.cum_inattention_cost.mean(),
            "mean choice-set contraction": d.mean_contraction.mean(),
            "median final net worth ($)": d.nw_final.median(),
            "mean final net worth ($)": d.nw_final.mean(),
        })
    tab = save_table(pd.DataFrame(table), "baseline_population")
    
    A, B = rows[("shock", "A: attention on")], rows[("shock", "B: attention off")]
    dnw = A.nw_final - B.nw_final
    m, se, ci = paired_summary(dnw.values)
    
    p = world.pop
    frag = (pd.Series(-p["balance"]).rank(pct=True) + pd.Series(p["alpha"]).rank(pct=True)
            + pd.Series(p["obligations"] / p["income"]).rank(pct=True)) / 3
    picks = {"fragile (90th pct)": int((frag - 0.90).abs().idxmin()),
             "middle (50th pct)": int((frag - 0.50).abs().idxmin()),
             "robust (10th pct)": int((frag - 0.10).abs().idxmin())}
             
    fig, ax = plt.subplots(3, 3, figsize=(12, 7), sharex=True)
    for c, (name, i) in enumerate(picks.items()):
        ha, hb = history(world, i, alpha_mult=1.0), history(world, i, alpha_mult=0.0)
        t = [r["t"] for r in ha]
        ax[0, c].plot(t, [r["attention"] for r in ha], label="A: attention on")
        ax[0, c].plot(t, [r["attention"] for r in hb], "--", label="B: off")
        ax[0, c].axhline(PARAMS.cog_refi, color="grey", lw=.6)
        ax[0, c].axhline(PARAMS.cog_defer, color="grey", lw=.6)
        ax[0, c].set_title(name); ax[0, c].set_ylim(0, 1.05)
        ax[1, c].plot(t, [r["balance"] for r in ha]); ax[1, c].plot(t, [r["balance"] for r in hb], "--")
        ax[2, c].plot(t, [r["payday_debt"] for r in ha]); ax[2, c].plot(t, [r["payday_debt"] for r in hb], "--")
        for a_ in ax[:, c]:
            sh = [r["t"] for r in ha if r["shock"]]
            if sh: a_.axvspan(min(sh) - .5, max(sh) + .5, color="red", alpha=.08)
    ax[0, 0].set_ylabel("attention A_t\n(grey: refi / defer thresholds)"); ax[1, 0].set_ylabel("liquid balance ($)")
    ax[2, 0].set_ylabel("payday debt ($)"); ax[2, 1].set_xlabel("month")
    ax[0, 0].legend(fontsize=8)
    fig.suptitle("Figure 1. Example household trajectories (shaded = income shock)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_example_trajectories.png"), dpi=140); plt.close(fig)
    
    mult = 1.0
    cs = ChoiceSet(default_actions(PARAMS), PARAMS)
    contr = np.zeros(world.T); locked = np.zeros(world.T); inshock = np.zeros(world.T)
    for i in range(world.n):
        for r in history(world, i, alpha_mult=mult):
            contr[r["t"]] += (r["n_feasible"] - r["n_accessible"] > 0)
            locked[r["t"]] += r["attention"] < PARAMS.cog_refi
            inshock[r["t"]] += r["shock"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(contr / world.n, label="share with a feasible option that is inaccessible")
    ax.plot(locked / world.n, label="share with attention below refinancing threshold")
    ax.plot(inshock / world.n, ":", label="share in an income-shock spell")
    ax.set_xlabel("month"); ax.set_ylabel("share of households"); ax.legend(fontsize=8)
    ax.set_title("Figure 2. Choice-set contraction over time (Model A)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig2_choice_set_contraction.png"), dpi=140); plt.close(fig)
    
    return {"table": tab, "attention_effect_on_nw": (m, se, ci),
            "share_differing": float((dnw.abs() > 1e-6).mean())}

if __name__ == "__main__":
    out = main()
    print(out["table"].to_string(index=False))