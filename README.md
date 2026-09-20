# When Does Financial Scarcity Become Irreversible?

A computational model of how sustained financial shocks may narrow household choice sets, and a framework for testing whether early intervention preserves future options.

## Research Overview

This repository contains a dynamic computational model designed to explore the mechanics of financial scarcity. Rather than modeling households as having a simple "budget constraint," this project models the interaction between liquidity, fixed obligations, and cognitive bandwidth (attention) to understand how financial shocks restrict a household's feasible and accessible choice set over time.

### Core Hypotheses

* **H1 (The Mechanism):** Sustained negative income shocks reduce a household's effective choice set through a feedback loop: decreased liquidity increases the relative burden of fixed obligations, which constrains attention capacity and reduces the household's ability to evaluate and select optimal alternative actions.
* **H2 (Intervention Timing):** Interventions delivered before severe liquidity depletion (early intervention) preserve significantly more future options than mathematically equivalent interventions delivered after the household has entered a highly constrained cognitive and financial state (late intervention).

### Note on Scope and Evidence

**This is a theoretical and computational simulation, not a causal empirical estimate.** 
The model demonstrates how these mechanisms *could* operate under defined mathematical assumptions. It does not establish that financial scarcity causes these exact effects in real households, nor does it estimate a real-world treatment effect. These limitations motivate the empirical identification strategy and synthetic data estimators outlined in the `docs/` directory, which detail the evidence required to test these hypotheses in the field.