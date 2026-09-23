# The Cognitive Cost of Friction: A Stochastic Monte Carlo Microsimulation

**Status:** USRESP Manuscript Submitted (12-page format) | **Language:** Python (NumPy, Matplotlib)

## Architecture Overview
This repository houses a 5,000-agent stochastic microsimulation designed to model how administrative sludge and bureaucratic friction act as a continuous drain on cognitive bandwidth. By isolating these variables, the model maps the exact boundary conditions where financial capture becomes a deterministic floor-absorption process.

## Methodology & Epistemic Boundaries
This model utilizes parameterized continuous bandwidth evolution and lognormal stochastic shocks to test the hypothesis that extreme financial distress is often a product of structural bandwidth depletion rather than baseline logic failure. 

**Note on Causal Inference:** This computational model shows what its parameters imply; it does not independently identify real-world causal effects. It serves as the theoretical mechanism design framework, intended to be paired with randomized administrative datasets for formal structural estimation.

## Core Mechanics
1. **Agent Generation:** 5,000 heterogeneous agents with baseline financial capital and cognitive bandwidth parameters.
2. **Lognormal Shocks:** Introduction of stochastic financial shocks (e.g., unexpected medical bills, delayed payroll).
3. **Bandwidth Depletion (Sludge):** A continuous drain function representing the administrative friction of navigating the shocks.
4. **2D Parameter Sensitivity Sweep:** A replication-based grid evaluating capture thresholds across varying friction multipliers.