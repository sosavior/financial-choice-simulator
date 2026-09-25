import numpy as np
import pytest
from src.model import LiquidityTransfer
from tests.helpers import make_world, run_one

def _fingerprint(seed):
    pop, shocks, offers = make_world(n=60, seed=seed)
    return [run_one(pop, i, shocks[i], offers[i], intervention=LiquidityTransfer(1000.0, 8)
                    ).outcomes()["nw_final"] for i in range(60)]

def test_same_seed_gives_identical_results():
    assert _fingerprint(5) == _fingerprint(5)

def test_different_seed_gives_different_results():
    assert _fingerprint(5) != _fingerprint(6)

def test_common_random_numbers_shock_and_offer_paths_identical_across_arms():
    pop, shocks, offers = make_world(n=30, seed=8)
    for i in range(30):
        base = run_one(pop, i, shocks[i], offers[i])
        aided = run_one(pop, i, shocks[i], offers[i], intervention=LiquidityTransfer(3000.0, 7))
        off = run_one(pop, i, shocks[i], offers[i], alpha=0.0)
        assert [r["shock"] for r in base.history] == [r["shock"] for r in aided.history]
        assert [r["shock"] for r in base.history] == [r["shock"] for r in off.history]

def test_simulation_is_deterministic_given_inputs():
    pop, shocks, offers = make_world(n=10, seed=9)
    a = run_one(pop, 0, shocks[0], offers[0]).history
    b = run_one(pop, 0, shocks[0], offers[0]).history
    assert a == b