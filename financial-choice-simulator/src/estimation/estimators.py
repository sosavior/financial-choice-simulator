"""Simple, transparent estimators used in the synthetic-data validation.
Everything here is applied to SIMULATED data; it shows that the estimator recovers a known
effect under randomisation, not that the effect exists in real households."""
import numpy as np

def diff_in_means(y: np.ndarray, treat: np.ndarray):
    """Difference in means with Welch (unequal-variance) standard error and 95% CI."""
    y = np.asarray(y, float)
    t = np.asarray(treat, bool)
    y1, y0 = y[t], y[~t]
    est = y1.mean() - y0.mean()
    se = np.sqrt(y1.var(ddof=1) / len(y1) + y0.var(ddof=1) / len(y0))
    return est, se, (est - 1.96 * se, est + 1.96 * se)

def paired_summary(d: np.ndarray):
    """Mean, SE and 95% CI of household-level paired differences (common random numbers)."""
    d = np.asarray(d, float)
    m = d.mean()
    se = d.std(ddof=1) / np.sqrt(len(d))
    return m, se, (m - 1.96 * se, m + 1.96 * se)

def coverage_study(y1: np.ndarray, y0: np.ndarray, n_rct: int, reps: int,
                   rng: np.random.Generator, null: bool = False):
    """Repeatedly draw an RCT sample from a synthetic population with known potential outcomes."""
    y1 = np.asarray(y0 if null else y1, float)
    y0 = np.asarray(y0, float)
    true = float((y1 - y0).mean())
    ests, cover, reject = [], 0, 0
    N = len(y0)
    for _ in range(reps):
        idx = rng.choice(N, size=n_rct, replace=False)
        assign = np.zeros(n_rct, bool)
        assign[rng.choice(n_rct, size=n_rct // 2, replace=False)] = True
        y_obs = np.where(assign, y1[idx], y0[idx])
        est, se, (lo, hi) = diff_in_means(y_obs, assign)
        ests.append(est)
        cover += (lo <= true <= hi)
        reject += (lo > 0 or hi < 0)
    ests = np.array(ests)
    return {"true_effect": true, "mean_estimate": ests.mean(), "bias": ests.mean() - true,
            "rmse": float(np.sqrt(((ests - true) ** 2).mean())),
            "ci_coverage": cover / reps, "rejection_rate_5pct": reject / reps}