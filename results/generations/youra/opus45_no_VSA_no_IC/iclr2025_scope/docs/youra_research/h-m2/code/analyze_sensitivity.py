"""Phase transition analysis: sensitivity ratio test for h-m2 hypothesis."""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

from config import MODELS, Paths, StatsConfig


def check_phase_transition(
    sens_1b: list[float],
    sens_12b: list[float],
    cfg: StatsConfig | None = None,
) -> dict:
    """Test if 12B sensitivity > 2x 1B sensitivity.

    H0: S(12B) <= 2*S(1B)
    H1: S(12B) > 2*S(1B)

    Returns:
        dict with ratio, ci_low, ci_high, p_value, pass
    """
    cfg = cfg or StatsConfig()

    sens_1b = np.array(sens_1b)
    sens_12b = np.array(sens_12b)

    ratio_obs = np.mean(sens_12b) / np.mean(sens_1b)

    diff = sens_12b - cfg.ratio_threshold * sens_1b
    t_stat, p_two = stats.ttest_1samp(diff, 0.0)
    p_value = p_two / 2 if t_stat > 0 else 1 - p_two / 2

    np.random.seed(42)
    boot_ratios = []
    for _ in range(cfg.n_bootstrap):
        s1b = np.random.choice(sens_1b, len(sens_1b), replace=True)
        s12b = np.random.choice(sens_12b, len(sens_12b), replace=True)
        if np.mean(s1b) > 0:
            boot_ratios.append(np.mean(s12b) / np.mean(s1b))

    ci_low, ci_high = np.percentile(boot_ratios, [2.5, 97.5])

    passes = (
        ratio_obs > cfg.ratio_threshold
        and ci_low > cfg.ci_lower_threshold
        and p_value < cfg.alpha
    )

    return {
        "ratio": float(ratio_obs),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "p_value": float(p_value),
        "pass": bool(passes),
    }


def fit_power_law(sensitivities_df: pd.DataFrame, n_bootstrap: int = 1000) -> dict:
    """Fit S = a * N^gamma via log-log OLS, bootstrap CI for gamma."""
    results = {}

    for dataset in sensitivities_df["dataset"].unique():
        ds_df = sensitivities_df[sensitivities_df["dataset"] == dataset]

        agg = ds_df.groupby("model").agg({"sensitivity": "mean"}).reset_index()
        agg["N"] = agg["model"].map(MODELS)

        x = np.log(agg["N"].values)
        y = np.log(agg["sensitivity"].values)

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        gamma = slope
        a = np.exp(intercept)
        r2 = r_value ** 2

        np.random.seed(42)
        boot_gammas = []
        for _ in range(n_bootstrap):
            idx = np.random.choice(len(x), len(x), replace=True)
            if len(np.unique(x[idx])) < 2:
                continue
            s, *_ = stats.linregress(x[idx], y[idx])
            boot_gammas.append(s)

        ci_low, ci_high = np.percentile(boot_gammas, [2.5, 97.5])

        results[dataset] = {
            "gamma": float(gamma),
            "gamma_ci_low": float(ci_low),
            "gamma_ci_high": float(ci_high),
            "a": float(a),
            "r2": float(r2),
            "super_linear": bool(ci_low > 1),
        }

    return results


def run_full_analysis(sensitivities_csv: str, output_json: str | None = None) -> dict:
    """Run complete phase transition analysis."""
    paths = Paths()
    output_json = output_json or paths.phase_transition_json

    sens_df = pd.read_csv(sensitivities_csv)

    all_results = {}

    for dataset in sens_df["dataset"].unique():
        ds_df = sens_df[sens_df["dataset"] == dataset]

        sens_1b = ds_df[ds_df["model"] == "pythia-1b"]["sensitivity"].tolist()
        sens_12b = ds_df[ds_df["model"] == "pythia-12b"]["sensitivity"].tolist()

        if sens_1b and sens_12b:
            phase_result = check_phase_transition(sens_1b, sens_12b)
            all_results[f"phase_transition_{dataset}"] = phase_result

    power_law = fit_power_law(sens_df)
    all_results["power_law_fit"] = power_law

    sens_1b_all = sens_df[sens_df["model"] == "pythia-1b"]["sensitivity"].tolist()
    sens_12b_all = sens_df[sens_df["model"] == "pythia-12b"]["sensitivity"].tolist()
    if sens_1b_all and sens_12b_all:
        all_results["phase_transition_combined"] = check_phase_transition(sens_1b_all, sens_12b_all)

    overall_pass = all(
        v.get("pass", True) for k, v in all_results.items()
        if k.startswith("phase_transition")
    )
    all_results["overall_pass"] = overall_pass

    os.makedirs(os.path.dirname(output_json) or ".", exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(all_results, f, indent=2)

    return all_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze rank sensitivity for phase transition")
    parser.add_argument("--sensitivities-csv", default="results/h-m2_sensitivities.csv")
    parser.add_argument("--output-json", default="results/h-m2_phase_transition.json")
    args = parser.parse_args()

    results = run_full_analysis(args.sensitivities_csv, args.output_json)

    print("\n=== Phase Transition Analysis ===")
    for k, v in results.items():
        if isinstance(v, dict):
            print(f"\n{k}:")
            for kk, vv in v.items():
                print(f"  {kk}: {vv}")
        else:
            print(f"{k}: {v}")
