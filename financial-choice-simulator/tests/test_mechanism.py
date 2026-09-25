"""Tests that the attention mechanism is not vacuous, and that limiting cases behave."""
import numpy as np
import pytest
from src.model import (Params, Household, ChoiceSet, default_actions, Simulation,
                       LiquidityTransfer, REFI, PAY_MIN, DEFER, PAYDAY)
from tests.helpers import make_world, run_one, P

def _refi_state(alpha):
    h = Household(income=3000, obligations=2200, balance=900, debt=9000, alpha=alpha, params=P)
    h.attention = 0.3 if alpha > 0 else 1.0
    ctx = h.begin_period(0, 3000, 0.0, refi_offer=True)
    return h, ctx

def test_attention_removes_a_feasible_option_and_changes_the_choice():
    cs = ChoiceSet(default_actions(P), P)
    h_on, ctx_on = _refi_state(alpha=0.9)
    h_off, ctx_off = _refi_state(alpha=0.0)
    dec_on, dec_off = cs.choose(h_on, ctx_on), cs.choose(h_off, ctx_off)
    names = lambda L: {a.name for a in L}
    assert REFI in names(dec_on.feasible)                    
    assert REFI not in names(dec_on.accessible)              
    assert dec_off.chosen.name == REFI                       
    assert dec_on.chosen.name == PAY_MIN                     
    assert dec_on.cost_gap > 0 and dec_off.cost_gap == 0     

def test_low_attention_pushes_short_household_from_deferral_to_payday():
    cs = ChoiceSet(default_actions(P), P)
    def state(alpha):
        h = Household(income=3000, obligations=2000, balance=100, debt=9000, alpha=alpha, params=P)
        h.attention = 0.3 if alpha > 0 else 1.0
        ctx = h.begin_period(0, 2100, 0.0, refi_offer=False)
        assert 0 <= ctx.resources < ctx.required
        return h, ctx
    h1, c1 = state(0.9); h0, c0 = state(0.0)
    assert cs.choose(h0, c0).chosen.name == DEFER            
    assert cs.choose(h1, c1).chosen.name == PAYDAY           

def test_alpha_zero_means_attention_never_moves_and_no_inattention_cost():
    pop, shocks, offers = make_world(n=80, seed=21, alpha_scale=1.0)
    for i in range(80):
        sim = run_one(pop, i, shocks[i], offers[i], alpha=0.0, shock_size=0.4)
        assert all(r["attention"] == pytest.approx(1.0) for r in sim.history)
        assert all(r["cost_gap"] == 0.0 for r in sim.history)

def test_attention_on_vs_off_produces_different_trajectories():
    pop, shocks, offers = make_world(n=300, seed=22)
    diff = 0
    for i in range(300):
        a = run_one(pop, i, shocks[i], offers[i], shock_size=0.3).outcomes()["nw_final"]
        b = run_one(pop, i, shocks[i], offers[i], alpha=0.0, shock_size=0.3).outcomes()["nw_final"]
        diff += abs(a - b) > 1e-6
    assert diff / 300 > 0.05

def test_attention_has_memory_and_recovers_gradually():
    p = Params(rho=0.3)
    h = Household(income=3000, obligations=2000, balance=6000, debt=1000, alpha=0.8, params=p)
    h.attention = 0.2
    path = []
    for t in range(8):                                        
        h.begin_period(t, 3000, 0.0)
        path.append(h.attention)
    assert all(b > a for a, b in zip(path, path[1:]))         
    assert path[0] < 0.5 and path[-1] > path[0]               

def test_rho_one_is_memoryless():
    p = Params(rho=1.0)
    h = Household(income=3000, obligations=2000, balance=500, debt=3000, alpha=0.7, params=p)
    h.attention = 0.15
    ctx = h.begin_period(0, 3000, 0.0)
    target = min(1.0, max(p.a_min, 1.0 - 0.7 * ctx.stress))
    assert h.attention == pytest.approx(target)

def test_more_aid_never_hurts_on_average():
    pop, shocks, offers = make_world(n=250, seed=23)
    means = []
    for amt in [0.0, 1000.0, 2000.0]:
        nw = [run_one(pop, i, shocks[i], offers[i], shock_size=0.3,
                      intervention=LiquidityTransfer(amt, 7)).outcomes()["nw_final"] for i in range(250)]
        means.append(np.mean(nw))
    assert means[0] <= means[1] + 1e-6 <= means[2] + 2e-6