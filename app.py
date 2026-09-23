import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Page Config
st.set_page_config(page_title="Monte Carlo Financial Simulator", layout="wide", initial_sidebar_state="collapsed")

st.markdown("<h1 style='text-align: center;'>Financial Choice Simulator: Structural Monte Carlo</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Simulating 1,000 households using dynamic confidence intervals, variable shock severities, and bandwidth recovery mechanics.</p>", unsafe_allow_html=True)
st.divider()

col_left, col_center, col_right = st.columns([1.2, 2.5, 1], gap="medium")

# --- LEFT COLUMN: CONTROLS ---
with col_left:
    st.subheader("Financial Variables")
    starting_income = st.slider("Baseline Income ($)", 1000, 8000, 3000)
    fixed_costs = st.slider("Fixed Living Expenses ($)", 1000, 5000, 2500, help="Rent, food, utilities. If this exceeds income, baseline debt accumulates regardless of bandwidth.")
    payday_apr = st.slider("Predatory APR (%)", 10, 400, 300, help="Annual interest rate for emergency credit.")
    
    st.markdown("---")
    st.subheader("Cognitive Variables")
    initial_bandwidth = st.slider("Initial Bandwidth", 0, 100, 80)
    admin_sludge = st.slider("Administrative Sludge", 0.0, 1.0, 0.5, help="Continuous daily bandwidth drain from structural friction.")
    recovery_rate = st.slider("Bandwidth Recovery", 0, 50, 15, help="How much bandwidth the agent regains in a month with no shocks.")
    
    st.markdown("---")
    st.subheader("Stochastic & Math Variables")
    shock_probability = st.slider(
        "Monthly Shock Risk (%)", 0, 100, 15, 
        help="The percentage probability that a household experiences a random financial emergency in any given month."
    )
    shock_magnitude = st.slider(
        "Shock Magnitude ($)", 100, 3000, 500, 
        help="The specific dollar amount of the random financial emergency when it strikes."
    )
    confidence_interval = st.slider("Confidence Interval (%)", 50, 99, 95, help="Determines the spread of the shaded area (e.g., 95% CI maps to the 2.5th and 97.5th percentiles).")

# --- MONTE CARLO SIMULATION MATH ---
N_SIMS = 1000
months = list(range(1, 13))

current_bw = np.full(N_SIMS, float(initial_bandwidth))
current_debt = np.zeros(N_SIMS)

history_bw = []
history_debt = []
cascade_triggered = np.zeros(N_SIMS, dtype=bool)

# Baseline monthly cash flow (can be negative)
monthly_deficit = max(0, fixed_costs - starting_income)

for m in months:
    # 1. Stochastic Shocks
    shock_hits = np.random.rand(N_SIMS) < (shock_probability / 100)
    
    # 2. Bandwidth Mechanics (Drain + Shocks vs. Recovery)
    noise = np.random.normal(0, 2, N_SIMS)
    sludge_drain = admin_sludge * 20
    shock_drain = shock_hits * 25  # A shock heavily taxes bandwidth
    
    # Apply drains, but allow recovery
    net_bw_change = recovery_rate - sludge_drain - shock_drain + noise
    current_bw = np.clip(current_bw + net_bw_change, 0, 100)
    
    # 3. Cognitive Capture & Debt Allocation
    in_cascade = current_bw < 30
    cascade_triggered = cascade_triggered | in_cascade
    
    # Debt accrued this month = baseline deficit + cost of shocks
    # If in cascade, they incur a "Cognitive Penalty"
    cognitive_penalty = in_cascade * (fixed_costs * 0.10) 
    
    new_debt = monthly_deficit + (shock_hits * shock_magnitude) + cognitive_penalty
    current_debt += new_debt
    
    # 4. Predatory Compounding (Only applies to existing debt)
    current_debt = current_debt * (1 + (payday_apr / 100 / 12))
    
    history_bw.append(current_bw.copy())
    history_debt.append(current_debt.copy())

history_bw = np.array(history_bw)
history_debt = np.array(history_debt)

# Dynamic Percentile Math based on the user's Confidence Interval
lower_p = (100 - confidence_interval) / 2
upper_p = 100 - lower_p

bw_lower, bw_median, bw_upper = np.percentile(history_bw, [lower_p, 50, upper_p], axis=1)
debt_lower, debt_median, debt_upper = np.percentile(history_debt, [lower_p, 50, upper_p], axis=1)

cascade_probability = (np.sum(cascade_triggered) / N_SIMS) * 100

# --- CENTER COLUMN: GRAPH ---
with col_center:
    st.subheader(f"{confidence_interval}% Confidence Distribution")
    
    fig = go.Figure()
    x_shade = months + months[::-1]
    
    # Bandwidth Cone
    fig.add_trace(go.Scatter(
        x=x_shade, y=np.concatenate([bw_upper, bw_lower[::-1]]),
        fill='toself', fillcolor='rgba(31, 119, 180, 0.2)', line=dict(color='rgba(255,255,255,0)'),
        name=f"BW {confidence_interval}% CI", showlegend=False
    ))
    # Bandwidth Median
    fig.add_trace(go.Scatter(x=months, y=bw_median, name="Median Bandwidth", line=dict(color="#1f77b4", width=2)))

    # Debt Cone
    fig.add_trace(go.Scatter(
        x=x_shade, y=np.concatenate([debt_upper, debt_lower[::-1]]),
        fill='toself', fillcolor='rgba(214, 39, 40, 0.2)', line=dict(color='rgba(255,255,255,0)'),
        name=f"Debt {confidence_interval}% CI", yaxis="y2", showlegend=False
    ))
    # Debt Median (Dashed to distinguish easily)
    fig.add_trace(go.Scatter(x=months, y=debt_median, name="Median Debt ($)", line=dict(color="#d62728", width=2, dash='dash'), yaxis="y2"))

    # Academic Layout Overhaul
    fig.update_layout(
        plot_bgcolor="white", 
        paper_bgcolor="white", 
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(color="black"), # Forces all numbers/text to black
        xaxis=dict(
            title=dict(text="Month", font=dict(color="black", size=14)), 
            showgrid=True, 
            gridcolor="#e0e0e0",
            tickfont=dict(color="black"),
            showline=True, linewidth=1.5, linecolor='black', mirror=True # Creates the classic black box border
        ),
        yaxis=dict(
            title=dict(text="Bandwidth Remaining", font=dict(color="#1f77b4", size=14)), 
            range=[0, 100], 
            showgrid=False,
            tickfont=dict(color="black"),
            showline=True, linewidth=1.5, linecolor='black', mirror=True
        ),
        yaxis2=dict(
            title=dict(text="Debt Level ($)", font=dict(color="#d62728", size=14)), 
            overlaying="y", 
            side="right", 
            showgrid=False,
            tickfont=dict(color="black"),
            showline=True, linewidth=1.5, linecolor='black'
        ),
        legend=dict(
            x=0.01, y=0.99, 
            bgcolor="rgba(255,255,255,0.9)", 
            bordercolor="black", 
            borderwidth=1
        )
    )
    
    # theme=None forces Streamlit to respect our strict white/black formatting
    st.plotly_chart(fig, use_container_width=True, theme=None)

# --- RIGHT COLUMN: INSIGHTS ---
with col_right:
    st.subheader("Structural Diagnostics")
    
    st.metric(label="Cascade Probability", value=f"{cascade_probability:.1f}%", help="Percentage of households whose bandwidth broke, triggering the cognitive penalty.")
    st.metric(label="Median 12-Month Debt", value=f"${debt_median[-1]:,.2f}")
    st.metric(label=f"Worst-Case Debt ({upper_p}th %ile)", value=f"${debt_upper[-1]:,.2f}", delta="Tail Risk", delta_color="inverse")
    
    st.markdown(f"""
    **Behavioral vs. Cost Mechanics:**  
    By separating *Fixed Costs* from *Cognitive Bandwidth*, we isolate the behavioral tax of poverty. 
    
    With a **{confidence_interval}% Confidence Interval**, the graph proves that even if baseline income technically covers fixed expenses, the combination of a **{shock_probability}%** shock risk and an administrative sludge of **{admin_sludge}** overcomes the agent's {recovery_rate} point recovery rate.
    
    Once captured (Bandwidth < 30), the agent absorbs a 10% structural penalty on fixed costs due to suboptimal decision-routing (late fees, missed deadlines), rapidly accelerating the {payday_apr}% debt spiral.
    """)