"""
Tests for institutional budget allocation mechanisms, administrative sludge,
and dynamic predatory credit tiering.
"""
import pytest
from src.models.lending import DynamicCreditMarket
from src.mechanisms.allocator import ReliefAllocator


def test_predatory_lending_trigger():
    market = DynamicCreditMarket(distress_threshold=0.70)

    # Low attention, zero liquidity -> should force predatory terms
    distressed_terms = market.evaluate_terms(
        amount_needed=500.0,
        liquidity=0.0,
        monthly_income=1200.0,
        attention_level=0.10,
    )
    assert distressed_terms.is_predatory is True
    assert distressed_terms.origination_fee >= 15.0

    # High attention, solid liquidity -> prime tier
    prime_terms = market.evaluate_terms(
        amount_needed=500.0,
        liquidity=2500.0,
        monthly_income=3000.0,
        attention_level=0.95,
    )
    assert prime_terms.is_predatory is False
    assert prime_terms.apr < 0.20


def test_sludge_vs_centralized_allocation():
    allocator = ReliefAllocator(monthly_budget=1000.0, grant_amount=500.0)

    pool = [
        {"id": "h1_distressed", "liquidity": 10.0, "fixed_costs": 600.0, "attention": 0.15},
        {"id": "h2_moderate", "liquidity": 300.0, "fixed_costs": 500.0, "attention": 0.85},
        {"id": "h3_stable", "liquidity": 1200.0, "fixed_costs": 500.0, "attention": 0.90},
    ]

    # Sludge drops the most distressed household because attention is below cognitive friction
    sludge_res = allocator.allocate_with_administrative_sludge(pool, paperwork_cognitive_cost=0.30)
    assert "h1_distressed" in sludge_res["dropped_due_to_friction"]
    assert "h1_distressed" not in sludge_res["recipients"]

    # Centralized mechanism targets the highest shortfall first regardless of attention
    central_res = allocator.allocate_centralized_optimal(pool)
    assert central_res["recipients"][0] == "h1_distressed"
    assert len(central_res["dropped_due_to_friction"]) == 0