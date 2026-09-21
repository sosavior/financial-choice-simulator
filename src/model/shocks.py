import numpy as np

def generate_shock_path(T: int, rng: np.random.Generator, onset: int = None,
                        p_out: float = 0.125, p_in: float = 0.0,
                        max_spell: int = 18) -> np.ndarray:
    u = rng.random(T)
    path = np.zeros(T, dtype=bool)
    in_shock = False
    length = 0
    for t in range(T):
        if onset is not None and t < onset:
            in_shock = False
        elif onset is not None and t == onset:
            in_shock = True
        elif in_shock:
            in_shock = (u[t] >= p_out) and (length < max_spell)
        else:
            in_shock = u[t] < p_in
        length = length + 1 if in_shock else 0
        path[t] = in_shock
    return path

def generate_offer_path(T: int, rng: np.random.Generator, p_offer: float = 0.15) -> np.ndarray:
    return rng.random(T) < p_offer