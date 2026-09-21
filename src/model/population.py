from typing import Dict
import numpy as np

CORR = np.array([
    [1.00, -0.20,  0.10,  0.40, -0.20],
    [-0.20, 1.00,  0.20, -0.20,  0.10],
    [0.10,  0.20,  1.00, -0.30,  0.10],
    [0.40, -0.20, -0.30,  1.00, -0.15],
    [-0.20, 0.10,  0.10, -0.15,  1.00],
])

def sample_population(n: int, rng: np.random.Generator, alpha_scale: float = 1.0) -> Dict[str, np.ndarray]:
    z = rng.standard_normal((n, 5)) @ np.linalg.cholesky(CORR).T
    income = np.exp(np.log(3200.0) + 0.35 * z[:, 0])
    
    debt = np.exp(np.log(6000.0) + 0.80 * z[:, 2])
    debt = np.minimum(debt, 6.0 * income)
    
    max_ratio = 0.97 - 1.018 * 0.03 * debt / income
    obl_ratio = np.exp(np.log(0.78) + 0.15 * z[:, 1])
    obl_ratio = np.clip(obl_ratio, 0.35, np.maximum(max_ratio, 0.35))
    
    balance = np.exp(np.log(1500.0) + 0.90 * z[:, 3])
    alpha = np.clip(0.50 + 0.15 * z[:, 4], 0.05, 1.20) * alpha_scale
    
    return {"income": income, "obligations": income * obl_ratio, "debt": debt,
            "balance": balance, "alpha": alpha}