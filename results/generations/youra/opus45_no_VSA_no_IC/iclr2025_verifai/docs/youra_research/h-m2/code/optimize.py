import numpy as np
from ensemble import compute_ensemble_score
from correlate import partial_corr_loc
from config import CONFIG

def grid_search_weights(
    df,
    metrics: list[str] = ["pylint_score", "radon_cc"],
) -> tuple[dict[str, float], float, float, list[tuple[float, float]]]:
    best_r, best_p, best_weights = None, None, None
    weight_r_pairs = []

    for w in np.arange(CONFIG.weight_min, CONFIG.weight_max + CONFIG.weight_grid_step / 2, CONFIG.weight_grid_step):
        w = round(w, 2)
        weights = {"pylint_score": w, "radon_cc": 1 - w}
        df_e = compute_ensemble_score(df, weights, metrics)
        r, p = partial_corr_loc(df_e, "ensemble")
        weight_r_pairs.append((w, r))
        if best_r is None or abs(r) > abs(best_r):
            best_r, best_p, best_weights = r, p, weights

    return best_weights, best_r, best_p, weight_r_pairs
