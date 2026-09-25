import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

# --- SIMULATION PARAMETERS ---
N_SIMS = 1000
MONTHS = 12
np.random.seed(42)

R_STD = 0.21 / 12
R_PRED = 3.91 / 12
GAMMA = 0.10

MU_INC, SIGMA_INC = np.log(3000), 0.2
MU_COST, SIGMA_COST = np.log(2500), 0.2
P_SHOCK = 0.15
MU_SHOCK, SIGMA_SHOCK = np.log(500), 0.6

R_BW = 15
ALPHA = 30
BETA = 0.01
K_STEEPNESS = 0.35
SIGMA_BW = 1.5
INFLECTION = 85

# --- SIMULATION FUNCTION ---
def run_simulation(global_sludge, intervention_month=None):
    income = np.random.lognormal(MU_INC, SIGMA_INC, N_SIMS)
    costs = np.random.lognormal(MU_COST, SIGMA_COST, N_SIMS)
    skill = np.random.uniform(0, 1, N_SIMS)
    
    bw = np.full(N_SIMS, 100.0)
    normal_debt = np.zeros(N_SIMS)
    predatory_debt = np.zeros(N_SIMS)
    deficit = np.maximum(0, costs - income)
    
    history = {'bw': [], 'p_capture': [], 'capture': [], 'normal_debt': [], 'predatory_debt': []}
    
    for m in range(1, MONTHS + 1):
        current_sludge = 0.1 if (intervention_month and m >= intervention_month) else global_sludge
        effective_sludge = current_sludge * (1 - skill)
        
        hit = np.random.binomial(1, P_SHOCK, N_SIMS)
        shock_magnitude = np.random.lognormal(MU_SHOCK, SIGMA_SHOCK, N_SIMS)
        cost_shock = hit * shock_magnitude
        
        noise = np.random.normal(0, SIGMA_BW, N_SIMS)
        bw = bw + R_BW - (ALPHA * effective_sludge) - (BETA * cost_shock) + noise
        bw = np.clip(bw, 0, 100)
        
        p_capture = 1 / (1 + np.exp(K_STEEPNESS * (bw - INFLECTION)))
        capture = np.random.binomial(1, p_capture)
        
        penalty = capture * (costs * GAMMA)
        delta_normal = deficit + (cost_shock * (1 - capture))
        delta_predatory = penalty + (cost_shock * capture)
        
        normal_debt = (normal_debt + delta_normal) * (1 + R_STD)
        predatory_debt = (predatory_debt + delta_predatory) * (1 + R_PRED)
        
        history['bw'].append(bw.copy())
        history['p_capture'].append(p_capture.copy())
        history['capture'].append(capture.copy())
        history['normal_debt'].append(normal_debt.copy())
        history['predatory_debt'].append(predatory_debt.copy())
        
    return {k: np.array(v) for k, v in history.items()}

# --- GRAPH A: DEBT DIVERGENCE ---
print("Generating Graph A...")
sim_low = run_simulation(global_sludge=0.1)
sim_high = run_simulation(global_sludge=0.9)

months = list(range(1, 13))
debt_low_95 = [np.percentile(sim_low['normal_debt'][m] + sim_low['predatory_debt'][m], 95) for m in range(12)]
debt_high_95 = [np.percentile(sim_high['normal_debt'][m] + sim_high['predatory_debt'][m], 95) for m in range(12)]

fig_a = go.Figure()
fig_a.add_trace(go.Scatter(x=months, y=debt_low_95, mode='lines+markers', name='Low Sludge (0.1)', line=dict(color='blue', width=3)))
fig_a.add_trace(go.Scatter(x=months, y=debt_high_95, mode='lines+markers', name='High Sludge (0.9)', line=dict(color='red', width=3, dash='dash')))

fig_a.update_layout(
    title='95th Percentile Total Debt Trajectory by Friction Level',
    xaxis_title='Month',
    yaxis_title='Total Debt ($)',
    template='simple_white',
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)
pio.write_image(fig_a, 'debt_divergence.png', width=800, height=500, scale=2)

# --- GRAPH B: CASCADE SWEEP ---
print("Generating Graph B...")
sludge_levels = np.linspace(0.0, 1.0, 11)
cascade_probs = []

for s in sludge_levels:
    sim = run_simulation(global_sludge=s)
    cascade_prob = np.mean(np.max(sim['capture'], axis=0)) * 100
    cascade_probs.append(cascade_prob)

fig_b = go.Figure()
fig_b.add_trace(go.Scatter(x=sludge_levels, y=cascade_probs, mode='lines+markers', line=dict(color='black', width=3)))

fig_b.update_layout(
    title='Cascade Probability as a Function of Administrative Sludge',
    xaxis_title='Administrative Sludge Coefficient',
    yaxis_title='Probability of Cognitive Capture (%)',
    template='simple_white'
)
pio.write_image(fig_b, 'cascade_sweep.png', width=800, height=500, scale=2)

print("Success! Check your folder for debt_divergence.png and cascade_sweep.png")