# When Does Financial Scarcity Become Irreversible? 
### A Computational Model of Choice-Set Contraction and Intervention Timing

This repository contains a reproducible computational model of how sustained financial shocks narrow household choice sets, and a framework for testing whether early intervention preserves future options.

## Research at a Glance
* **Question:** Does sustained financial scarcity contract household choice sets?
* **Mechanism:** Liquidity constraints interact with limited attention and fixed obligations to filter out optimal but complex financial recovery actions.
* **Model:** Dynamic household state model with stochastic income shocks.
* **Finding:** Simulated intervention timing matters as much as intervention magnitude; early intervention prevents long-term choice-set collapse.
* **Limitation:** This simulation *cannot* identify real-world causal effects. It proves what the assumptions imply, not what real households do.
* **Next Test:** Estimate true treatment effects using randomized or quasi-random empirical intervention timing (see `docs/identification.md`).

---

## 1. Core Hypotheses
* **H1:** Sustained negative income shocks reduce a household’s feasible choice set through increased fixed-cost commitments, liquidity constraints, and reduced capacity to evaluate alternatives.
* **H2:** Interventions delivered before severe liquidity depletion preserve more future options than equivalent interventions delivered after the household has entered a highly constrained state.

## 2. Theoretical Framework

### The Household State
The simulated household is defined by a dynamic state vector:
$S_t = (B_t, D_t, P_t, O_t, Y_t, A_t, r_t)$
Where $B_t$ is liquid balance, $D_t$ is formal debt, $P_t$ is payday/high-cost debt, $O_t$ is fixed obligations, $Y_t$ is base income, $A_t \in [a_{min}, 1]$ is cognitive bandwidth/attention, and $r_t$ is the current interest rate.

### Formal Choice-Set Definition
We explicitly distinguish between *feasible* and *accessible* choices:
* **Feasible Set ($F_t$):** $\{ a \in \mathcal{A} : a \text{ is affordable given current liquidity } B_t, O_t \}$
* **Accessible Set ($C_t$):** $\{ a \in F_t : \text{cognitive\_cost}(a) \le A_t \}$

The cost of inattention is strictly measured as the difference in expected future cost between the best action in $F_t$ and the chosen action in $C_t$.

---

## 3. Claims vs. Evidence
| Claim | Evidence Type | Strength |
| :--- | :--- | :--- |
| Scarcity can contract simulated choice sets | Simulation | Model-dependent |
| Early intervention preserves simulated options | Simulation | Model-dependent |
| Real households behave this way | None yet | Unknown |
| Intervention causally preserves real-world options | None yet | Unknown |
| Proposed mechanisms are empirically testable | Research design | Strong conceptual claim |

---

## 4. What This Project Does *Not* Establish
* The model **does not establish** that financial scarcity causes reduced choice sets in real households.
* The simulated intervention effects are conditional on assumed parameters.
* The model **does not estimate** a treatment effect. Synthetic data are not evidence about real populations.
* The attention parameter ($\alpha$) is not currently identified from observed behavioral data.

These limitations motivate the empirical research design described in the Identification Strategy (`docs/identification.md`).

---

## 5. Reproducibility
This repository is designed for immaculate reproducibility. To generate all results, figures, tables, and sensitivity heatmaps from scratch:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the master experiment pipeline
python experiments/run_all.py