import os
import json
import numpy as np
from config import Config, AnalysisConfig, SEEDS
from cross_correlation import compute_lagged_cross_correlation, bootstrap_ci_tau

def evaluate_all_seeds(results_dir: str, max_lag: int = 5) -> dict:
    analysis_cfg = AnalysisConfig(max_lag=max_lag)
    tau_per_seed = []
    corr_per_seed = []
    for seed in SEEDS:
        seed_file = os.path.join(results_dir, f"seed_{seed}.json")
        if not os.path.exists(seed_file):
            continue
        with open(seed_file, "r") as f:
            data = json.load(f)
        r_series = np.array(data["r_series"])
        sr_series = np.array(data["sr_series"])
        tau, corr, lags = compute_lagged_cross_correlation(r_series, sr_series, max_lag)
        tau_per_seed.append(tau)
        corr_per_seed.append({"corr": corr.tolist(), "lags": lags.tolist()})
    if not tau_per_seed:
        return {"error": "No seed results found"}
    mean_tau, ci_low, ci_high = bootstrap_ci_tau(tau_per_seed, analysis_cfg.confidence, analysis_cfg.n_bootstrap)
    gate_pass = bool(ci_low > 0)
    return {
        "tau_per_seed": tau_per_seed,
        "tau_mean": float(mean_tau),
        "tau_ci": (float(ci_low), float(ci_high)),
        "gate_pass": gate_pass,
        "corr_per_seed": corr_per_seed,
    }

def main():
    cfg = Config()
    result = evaluate_all_seeds(cfg.results_dir)
    print(f"Tau per seed: {result.get('tau_per_seed')}")
    print(f"Mean tau: {result.get('tau_mean'):.4f}")
    print(f"95% CI: ({result.get('tau_ci')[0]:.4f}, {result.get('tau_ci')[1]:.4f})")
    print(f"Gate PASS: {result.get('gate_pass')}")
    with open(os.path.join(cfg.results_dir, "evaluation.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
