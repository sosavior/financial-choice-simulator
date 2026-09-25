"""Shared configuration and helpers for all experiments.
Design choices below are FIXED IN ADVANCE and are assumptions, not estimates."""
import os
import sys
from dataclasses import dataclass
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.model import (Params, Household, ChoiceSet, default_actions, Simulation,
                       LiquidityTransfer, StateTriggeredTransfer, pv_adjusted_amount,
                       sample_population, generate_shock_path, generate_offer_path)
from src.estimation import paired_summary

SEED = 20260101
T = 48                 
ONSET = 6              
SHOCK_SIZE = 0.30      
SPELL_MEAN = 8         
AMOUNT = 1500.0        
N_MAIN = 3000          
PARAMS = Params()
RESULTS = os.path.join(ROOT, "results")
FIG = os.path.join(RESULTS, "figures")
TAB = os.path.join(RESULTS, "tables")

for d in (FIG, TAB):
    os.makedirs(d, exist_ok=True)

@dataclass
class World:
    pop: dict
    shocks: list
    offers: list
    n: int
    T: int
    onset: int
    spell_len: np.ndarray

def build_world(n=N_MAIN, seed=SEED, T=T, onset=ONSET, spell_mean=SPELL_MEAN, p_offer=0.15):
    ss = np.random.SeedSequence(seed)
    pop_ss, hh_ss = ss.spawn(2)
    pop = sample_population(n, np.random.default_rng(pop_ss))
    shocks, offers = [], []
    for child in hh_ss.spawn(n):
        rng = np.random.default_rng(child)
        shocks.append(generate_shock_path(T, rng, onset=onset, p_out=1.0 / spell_mean))
        offers.append(generate_offer_path(T, rng, p_offer))
    return World(pop, shocks, offers, n, T, onset, np.array([s.sum() for s in shocks]))

def _household(world, i, alpha_mult, params):
    p = world.pop
    return Household(p["income"][i], p["obligations"][i], p["balance"][i], p["debt"][i],
                     p["alpha"][i] * alpha_mult, params)

def simulate(world, shock_size=SHOCK_SIZE, alpha_mult=1.0, intervention_factory=None,
             params=PARAMS, snapshot=()):
    cs = ChoiceSet(default_actions(params), params)
    rows = []
    for i in range(world.n):
        iv = intervention_factory(i) if intervention_factory else None
        sim = Simulation(_household(world, i, alpha_mult, params), cs, world.shocks[i],
                         shock_size, iv, onset=world.onset, snapshot_periods=snapshot,
                         offer_path=world.offers[i])
        sim.run()
        o = sim.outcomes()
        o["i"] = i
        if isinstance(iv, StateTriggeredTransfer):
            o["delivered_at"] = iv.delivered_at if iv.delivered else np.nan
        rows.append(o)
    return pd.DataFrame(rows)

def history(world, i, shock_size=SHOCK_SIZE, alpha_mult=1.0, params=PARAMS):
    cs = ChoiceSet(default_actions(params), params)
    sim = Simulation(_household(world, i, alpha_mult, params), cs, world.shocks[i], shock_size,
                     onset=world.onset, offer_path=world.offers[i])
    return sim.run()

def transfer_factory(amount, period):
    return lambda i: LiquidityTransfer(amount, period)

def save_table(df, name):
    df.to_csv(os.path.join(TAB, name + ".csv"), index=False)
    return df