"""Ablation studies for H-M2 temperature scaling."""

from temperature_optim import optimize_temperature_per_cluster
from metrics import compute_cv_and_range
from config import T_BOUNDS, T_INIT, ABLATION_BOUNDS, ABLATION_T_INIT


def run_bounds_ablation(logits_by_cluster, labels_by_cluster, bounds_list=ABLATION_BOUNDS):
    """A1: Optimization bounds sensitivity ablation.

    Returns:
        dict[str, dict]: {bounds_key: {optimal_temps, cv, range}}
    """
    results = {}
    for bounds in bounds_list:
        temps = optimize_temperature_per_cluster(
            logits_by_cluster, labels_by_cluster, bounds=bounds, t_init=T_INIT
        )
        cv, t_range = compute_cv_and_range(temps)
        results[f"bounds_{bounds}"] = {
            "optimal_temps": temps,
            "cv": cv,
            "range": t_range,
            "bounds": bounds,
        }
    return results


def run_init_ablation(logits_by_cluster, labels_by_cluster, t_init_list=ABLATION_T_INIT):
    """A2: Initialization sensitivity ablation.

    Returns:
        dict[str, dict]: {init_key: {optimal_temps, cv, range}}
    """
    results = {}
    for t_init in t_init_list:
        temps = optimize_temperature_per_cluster(
            logits_by_cluster, labels_by_cluster, bounds=T_BOUNDS, t_init=t_init
        )
        cv, t_range = compute_cv_and_range(temps)
        results[f"t_init_{t_init}"] = {
            "optimal_temps": temps,
            "cv": cv,
            "range": t_range,
            "t_init": t_init,
        }
    return results
