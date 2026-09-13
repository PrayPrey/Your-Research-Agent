"""Reliability analysis using Cronbach's alpha."""
import numpy as np
import pandas as pd

try:
    import pingouin as pg
    HAS_PINGOUIN = True
except ImportError:
    HAS_PINGOUIN = False


def compute_cronbach_alpha_manual(df: pd.DataFrame) -> dict:
    """Compute Cronbach's alpha manually (fallback if pingouin unavailable)."""
    n_items = df.shape[1]
    item_vars = df.var(axis=0, ddof=1)
    total_var = df.sum(axis=1).var(ddof=1)

    alpha = (n_items / (n_items - 1)) * (1 - item_vars.sum() / total_var)

    # Bootstrap CI (simple percentile method)
    n_boot = 1000
    rng = np.random.default_rng(42)
    alphas = []
    for _ in range(n_boot):
        idx = rng.choice(len(df), size=len(df), replace=True)
        boot_df = df.iloc[idx]
        iv = boot_df.var(axis=0, ddof=1)
        tv = boot_df.sum(axis=1).var(ddof=1)
        a = (n_items / (n_items - 1)) * (1 - iv.sum() / tv)
        alphas.append(a)

    ci_lower, ci_upper = np.percentile(alphas, [2.5, 97.5])

    return {"alpha": float(alpha), "ci_lower": float(ci_lower), "ci_upper": float(ci_upper)}


def compute_cronbach_alpha(df: pd.DataFrame) -> dict:
    """Compute Cronbach's alpha with 95% CI."""
    if HAS_PINGOUIN:
        alpha, ci = pg.cronbach_alpha(data=df)
        return {"alpha": float(alpha), "ci_lower": float(ci[0]), "ci_upper": float(ci[1])}
    else:
        return compute_cronbach_alpha_manual(df)


def compute_item_total_correlations(df: pd.DataFrame) -> dict[str, float]:
    """Correlation of each item (mode) with total of other items."""
    result = {}
    for col in df.columns:
        other_total = df.drop(columns=[col]).sum(axis=1)
        result[col] = float(df[col].corr(other_total))
    return result


def compute_alpha_if_dropped(df: pd.DataFrame) -> dict[str, float]:
    """Alpha when each item (mode) is dropped."""
    result = {}
    for col in df.columns:
        dropped_df = df.drop(columns=[col])
        result[col] = compute_cronbach_alpha(dropped_df)["alpha"]
    return result


def analyze_all_methods(
    profiles: dict[str, pd.DataFrame],
    threshold: float
) -> dict:
    """Run full reliability analysis for all methods."""
    results = {}
    all_pass = True

    for method, df in profiles.items():
        alpha_info = compute_cronbach_alpha(df)
        item_total = compute_item_total_correlations(df)
        alpha_dropped = compute_alpha_if_dropped(df)

        method_pass = alpha_info["alpha"] > threshold
        all_pass = all_pass and method_pass

        results[method] = {
            "alpha": alpha_info["alpha"],
            "ci_lower": alpha_info["ci_lower"],
            "ci_upper": alpha_info["ci_upper"],
            "n_probes": len(df),
            "item_total_correlations": item_total,
            "alpha_if_dropped": alpha_dropped,
            "pass": method_pass
        }

    results["gate_pass"] = all_pass
    return results
