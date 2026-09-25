# From Simulation to Identification: Empirical Strategy

## 1. Research Question & Causal Estimand
Does the timing of financial intervention causally preserve household choice sets and prevent long-term insolvency?

We define our ideal causal estimand as the Average Treatment Effect (ATE) of early versus delayed intervention:
$$\tau = E[Y_i(1) - Y_i(0)]$$
where $Y_i(1)$ represents the downstream choice-set capacity under early treatment, and $Y_i(0)$ represents capacity under delayed treatment.

## 2. Ideal Experimental Design
The gold standard for identifying this effect would be a multi-arm randomized controlled trial (RCT):
- **Arm 1 (Treatment Early):** Unconditional cash transfer or debt restructuring delivered immediately upon the onset of a verified income shock.
- **Arm 2 (Treatment Late):** Identical transfer delivered 6 to 12 months post-shock after compounding obligations have accumulated.
- **Arm 3 (Control):** Standard institutional tracking without intervention.

## 3. Quasi-Experimental Alternatives
Because random assignment of financial distress relief is frequently constrained by operational or ethical realities, empirical researchers can leverage:
- **Regression Discontinuity Designs (RDD):** Exploiting score-based eligibility thresholds (e.g., credit score cutoffs or income-to-debt ratios) for emergency relief programs.
- **Lottery-Based Random Assignment:** Leveraging oversubscribed relief programs that allocate scarce vouchers or grants via random lottery (similar to mechanisms studied in housing and public finance literature).

## 4. Threats to Identification
1. **Attrition & Noncompliance:** Households assigned to treatment arms may fail to take up assistance due to administrative friction or stigma.
2. **Spillovers:** Relief provided to one household may alter local market prices or informal credit networks within the community.
3. **Measurement Error:** Proxy measures for choice-set capacity (such as revolving credit utilization or delinquency flags) may imperfectly capture true cognitive bandwidth and option sets.