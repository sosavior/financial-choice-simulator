"""Accounting identities and structural invariants. If any of these fail, results are meaningless."""
import numpy as np
import pytest
from src.model import (Params, Household, LiquidityTransfer, NoIntervention, PAY_MIN,
                       PAYDAY, sample_population, generate_shock_path)
from src.model.population import CORR
from tests.helpers import make_world, run_one, P

def test_net_worth_accounting_identity_every_period():
    pop, shocks, offers = make_world(n=150, seed=3)
    seen_actions = set()
    for i in range(150):
        sim = run_one(pop, i, shocks[i], offers[i], shock_size=0.35,
                      intervention=LiquidityTransfer(1500.0, 9))
        prev = sim.initial_net_worth
        for r in sim.history:
            expected = r["income"] + r["transfer"] - r["obligations"] - r["interest"] - r["fees"]
            assert r["net_worth"] - prev == pytest.approx(expected, abs=1e-6)
            prev = r["net_worth"]
            seen_actions.add(r["action"])
    assert {"pay_min", "refinance", "defer_payment", "payday_loan"} <= seen_actions

def test_state_variables_never_negative_and_attention_bounded():
    pop, shocks, offers = make_world(n=150, seed=4)
    for i in range(150):
        sim = run_one(pop, i, shocks[i], offers[i], shock_size=0.45)
        for r in sim.history:
            assert r["balance"] >= -1e-9 and r["debt"] >= -1e-9 and r["payday_debt"] >= -1e-9
            assert P.a_min - 1e-12 <= r["attention"] <= 1.0 + 1e-12
            assert r["payday_debt"] <= P.payday_cap_months * pop["income"][i] + 1e-6

def test_feasible_and_accessible_sets_are_well_formed():
    pop, shocks, offers = make_world(n=150, seed=5)
    for i in range(150):
        sim = run_one(pop, i, shocks[i], offers[i], shock_size=0.4)
        for r in sim.history:
            assert r["n_feasible"] >= 1                      
            assert 1 <= r["n_accessible"] <= r["n_feasible"]  
            assert r["cost_gap"] >= 0.0

def test_params_reject_configurations_that_could_empty_the_choice_set():
    with pytest.raises(ValueError):
        Params(a_min=0.05)          
    with pytest.raises(ValueError):
        Params(rho=0.0)

def test_transfers_are_recorded_and_conserved():
    pop, shocks, offers = make_world(n=20, seed=6)
    for i in range(20):
        sim = run_one(pop, i, shocks[i], offers[i], intervention=LiquidityTransfer(1234.0, 8))
        assert sum(r["transfer"] for r in sim.history) == pytest.approx(1234.0)
        assert sim.history[8]["transfer"] == pytest.approx(1234.0)

def test_transfer_scheduled_after_horizon_is_an_exact_placebo():
    pop, shocks, offers = make_world(n=60, seed=7)
    for i in range(60):
        a = run_one(pop, i, shocks[i], offers[i], intervention=NoIntervention()).outcomes()
        b = run_one(pop, i, shocks[i], offers[i], intervention=LiquidityTransfer(2000.0, 10_000)).outcomes()
        assert a["nw_final"] == pytest.approx(b["nw_final"], abs=1e-9)

def test_zero_shock_comfortable_household_never_borrows():
    h = Household(income=4000, obligations=2500, balance=3000, debt=4000, alpha=0.5, params=P)
    from src.model import ChoiceSet, default_actions, Simulation
    sim = Simulation(h, ChoiceSet(default_actions(P), P), np.zeros(36, bool), 0.3)
    hist = sim.run()
    assert all(r["action"] != PAYDAY for r in hist)
    assert all(r["gap"] == 0 for r in hist)
    assert hist[-1]["net_worth"] > sim.initial_net_worth

def test_population_is_viable_and_correlation_matrix_valid():
    pop = sample_population(5000, np.random.default_rng(0))
    surplus = pop["income"] - pop["obligations"] - 1.018 * 0.03 * pop["debt"]
    assert (surplus > 0).all()
    assert np.linalg.eigvalsh(CORR).min() > 0
    assert (pop["income"] > 0).all() and (pop["balance"] > 0).all() and (pop["debt"] > 0).all()
    assert (pop["alpha"] >= 0).all()

def test_shock_path_properties():
    rng = np.random.default_rng(1)
    path = generate_shock_path(60, rng, onset=6, p_out=0.0, max_spell=10)
    assert not path[:6].any() and path[6]
    assert path.sum() == 10                                 
    a = generate_shock_path(48, np.random.default_rng(5), onset=6)
    b = generate_shock_path(48, np.random.default_rng(5), onset=6)
    assert (a == b).all()