import numpy as np
from src.model import (Params, Household, ChoiceSet, default_actions, Simulation,
                       sample_population, generate_shock_path, generate_offer_path)

P = Params()

def make_world(n=200, seed=11, T=48, onset=6, alpha_scale=1.0, params=P):
    ss = np.random.SeedSequence(seed)
    pop_ss, shock_ss = ss.spawn(2)
    pop = sample_population(n, np.random.default_rng(pop_ss), alpha_scale)
    shocks, offers = [], []
    for child in shock_ss.spawn(n):
        rng = np.random.default_rng(child)
        shocks.append(generate_shock_path(T, rng, onset=onset))
        offers.append(generate_offer_path(T, rng))
    return pop, shocks, offers

def run_one(pop, i, shock, offer, shock_size=0.3, intervention=None, alpha=None,
            onset=6, params=P):
    cs = ChoiceSet(default_actions(params), params)
    a = pop["alpha"][i] if alpha is None else alpha
    h = Household(pop["income"][i], pop["obligations"][i], pop["balance"][i],
                  pop["debt"][i], a, params)
    sim = Simulation(h, cs, shock, shock_size, intervention, onset=onset, offer_path=offer)
    sim.run()
    return sim