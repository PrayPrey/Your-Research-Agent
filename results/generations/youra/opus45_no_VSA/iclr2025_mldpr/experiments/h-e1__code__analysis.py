# Statistical analysis module for h-e1
import os
import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from config import PATHS, N_BOOTSTRAP, RANDOM_SEED


def compute_reproducibility_iqr(runs_df: pd.DataFrame) -> pd.DataFrame:
    """Compute IQR of predictive_accuracy per (dataset, flow, setup) group."""
    def iqr(x):
        return x.quantile(0.75) - x.quantile(0.25)

    result = runs_df.groupby(["data_id", "flow_id", "setup_id"])["predictive_accuracy"].agg([
        ("iqr", iqr),
        ("mean", "mean"),
        ("std", "std"),
        ("count", "count")
    ]).reset_index()
    return result


def build_analysis_dataset(matched_runs: pd.DataFrame, metadata_scores: pd.DataFrame,
                           controls: dict) -> pd.DataFrame:
    """Merge all data into analysis dataset."""
    # Compute reproducibility metrics
    repro = compute_reproducibility_iqr(matched_runs)

    # Merge metadata scores
    repro = repro.rename(columns={"data_id": "dataset_id"})
    df = repro.merge(metadata_scores, on="dataset_id", how="left")

    # Add controls
    df["stability"] = df["dataset_id"].map(lambda x: controls.get(x, {}).get("stability", 0.0))
    df["algo_family"] = df["flow_id"].map(lambda x: controls.get(x, {}).get("algo_family", "Other"))
    df["sklearn_version"] = df["flow_id"].map(lambda x: controls.get(x, {}).get("sklearn_version", "unknown"))

    # Popularity: log(run count per dataset)
    run_counts = matched_runs.groupby("data_id").size().reset_index(name="run_count")
    run_counts = run_counts.rename(columns={"data_id": "dataset_id"})
    df = df.merge(run_counts, on="dataset_id", how="left")
    df["log_popularity"] = np.log1p(df["run_count"].fillna(0))

    # Log n_instances
    df["log_n_instances"] = np.log1p(df["n_instances"].fillna(0))

    # Drop rows with missing critical values
    df = df.dropna(subset=["iqr", "metadata_score"])

    os.makedirs(os.path.dirname(PATHS["analysis"]), exist_ok=True)
    df.to_parquet(PATHS["analysis"], index=False)
    print(f"  Saved analysis dataset ({len(df)} rows) to {PATHS['analysis']}")
    return df


def fit_mixed_model(df: pd.DataFrame):
    """Random intercept per dataset_id. Formula: iqr ~ metadata_score + controls."""
    df = df.copy()
    df["algo_family"] = df["algo_family"].astype("category")

    # Handle case where only one group
    if df["dataset_id"].nunique() < 2:
        print("Warning: Not enough groups for mixed model, using OLS")
        model = smf.ols(
            "iqr ~ metadata_score + stability + log_popularity + C(algo_family)",
            data=df
        )
        result = model.fit()
        return result

    model = smf.mixedlm(
        "iqr ~ metadata_score + stability + log_popularity + C(algo_family)",
        data=df,
        groups=df["dataset_id"]
    )
    result = model.fit(reml=False)

    if not result.converged:
        print("Warning: Model did not converge")

    return result


def compute_quartile_effect(df: pd.DataFrame) -> dict:
    """Compare IQR: top vs bottom metadata_score quartile."""
    q1 = df["metadata_score"].quantile(0.25)
    q3 = df["metadata_score"].quantile(0.75)

    bottom = df[df["metadata_score"] <= q1]["iqr"]
    top = df[df["metadata_score"] >= q3]["iqr"]

    if len(bottom) == 0 or len(top) == 0:
        return {
            "iqr_top": None, "iqr_bottom": None,
            "relative_reduction": None, "absolute_reduction": None
        }

    iqr_bottom = float(bottom.median())
    iqr_top = float(top.median())

    if iqr_bottom == 0:
        rel_red = 0.0
    else:
        rel_red = (iqr_bottom - iqr_top) / iqr_bottom

    abs_red = iqr_bottom - iqr_top

    return {
        "iqr_top": iqr_top,
        "iqr_bottom": iqr_bottom,
        "relative_reduction": rel_red,
        "absolute_reduction": abs_red
    }


def bootstrap_ci(df: pd.DataFrame, n_boot: int = N_BOOTSTRAP) -> dict:
    """Percentile bootstrap 95% CI on relative_reduction (resample datasets)."""
    np.random.seed(RANDOM_SEED)
    dataset_ids = df["dataset_id"].unique()
    estimates = []

    for _ in range(n_boot):
        sample_ids = np.random.choice(dataset_ids, len(dataset_ids), replace=True)
        boot_df = df[df["dataset_id"].isin(sample_ids)]
        effect = compute_quartile_effect(boot_df)
        if effect["relative_reduction"] is not None:
            estimates.append(effect["relative_reduction"])

    if len(estimates) < 10:
        return {"ci_lower": None, "ci_upper": None, "boot_estimates": estimates}

    ci_lower, ci_upper = np.percentile(estimates, [2.5, 97.5])
    return {
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "boot_estimates": estimates
    }


def save_results(model_result, effects: dict, bootstrap: dict):
    """Save results to JSON files."""
    os.makedirs("results", exist_ok=True)

    # Model results
    model_dict = {
        "params": {k: float(v) for k, v in model_result.params.items()},
        "pvalues": {k: float(v) for k, v in model_result.pvalues.items()},
        "converged": getattr(model_result, "converged", True),
        "llf": float(model_result.llf) if hasattr(model_result, "llf") else None,
        "aic": float(model_result.aic) if hasattr(model_result, "aic") else None,
    }
    with open(PATHS["model_results"], "w") as f:
        json.dump(model_dict, f, indent=2)

    # Effects
    effects_dict = {
        "quartile_effect": effects,
        "bootstrap_ci": {
            "ci_lower": bootstrap["ci_lower"],
            "ci_upper": bootstrap["ci_upper"],
            "n_boot": len(bootstrap["boot_estimates"])
        }
    }
    with open(PATHS["effects"], "w") as f:
        json.dump(effects_dict, f, indent=2)

    print(f"  Saved model results to {PATHS['model_results']}")
    print(f"  Saved effects to {PATHS['effects']}")
