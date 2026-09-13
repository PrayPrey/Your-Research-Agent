"""Statistical analysis: Kruskal-Wallis + Dunn + effect size."""
import numpy as np
import pandas as pd
import scipy.stats
import scikit_posthocs as sp


def _epsilon_squared(H: float, n: int) -> float:
    return H / (n - 1) if n > 1 else 0.0


def _pairwise_diff_pct(per_verifier: dict) -> dict:
    pairs = [("z3", "pyright"), ("z3", "mypy"), ("pyright", "execution"), ("mypy", "execution")]
    result = {}
    for a, b in pairs:
        ma = per_verifier.get(a, {}).get("mean", 0)
        mb = per_verifier.get(b, {}).get("mean", 0)
        key = f"{a}_vs_{b}"
        result[key] = round((ma - mb) / mb * 100, 1) if mb > 0 else None
    return result


def _ordering_confirmed(per_verifier: dict, dunn_df: pd.DataFrame) -> bool:
    means = {v: per_verifier[v]["mean"] for v in per_verifier}
    smt_ge_static = (
        means.get("z3", 0) >= means.get("pyright", 0) and
        means.get("z3", 0) >= means.get("mypy", 0)
    )
    static_gt_exec = (
        means.get("pyright", 0) > means.get("execution", 0) and
        means.get("mypy", 0) > means.get("execution", 0)
    )
    try:
        p_z3_exec = dunn_df.loc["z3", "execution"]
        sig = float(p_z3_exec) < 0.05
    except (KeyError, TypeError):
        sig = False
    return bool(smt_ge_static and static_gt_exec and sig)


def run_analysis(records: list[dict]) -> dict:
    df = pd.DataFrame(records)

    # For Z3: exclude records where char_count==0 AND timeout==False (missing data, not zero feedback)
    z3_mask = (df["verifier"] == "z3")
    z3_missing = z3_mask & (df["char_count"] == 0) & (~df["timeout"])
    df_analysis = df[~z3_missing].copy()

    # Separate timeout records (exclude from primary KW test)
    df_notimeout = df_analysis[~df_analysis["timeout"]]

    verifiers = ["execution", "pyright", "mypy", "z3"]
    groups = {}
    for v in verifiers:
        vals = df_notimeout[df_notimeout["verifier"] == v]["char_count"].values
        if len(vals) >= 2:
            groups[v] = vals

    per_verifier = {}
    for v, g in groups.items():
        per_verifier[v] = {
            "mean": float(np.mean(g)),
            "median": float(np.median(g)),
            "std": float(np.std(g)),
            "n": int(len(g)),
        }

    # Kruskal-Wallis
    group_arrays = [g for g in groups.values()]
    H, p = scipy.stats.kruskal(*group_arrays)
    n_total = sum(len(g) for g in group_arrays)
    eps2 = _epsilon_squared(H, n_total)

    # Dunn post-hoc
    df_kw = df_notimeout[df_notimeout["verifier"].isin(groups.keys())].copy()
    try:
        dunn_df = sp.posthoc_dunn(df_kw, val_col="char_count", group_col="verifier", p_adjust="bonferroni")
    except Exception:
        dunn_df = pd.DataFrame()

    ordering = _ordering_confirmed(per_verifier, dunn_df)
    pairwise = _pairwise_diff_pct(per_verifier)

    # Direction-only check (PoC pass even without full significance)
    means = {v: per_verifier[v]["mean"] for v in per_verifier}
    direction_confirmed = (
        means.get("z3", 0) >= max(means.get("pyright", 0), means.get("mypy", 0)) and
        min(means.get("pyright", 0), means.get("mypy", 0)) > means.get("execution", 0)
    )

    # Z3 coverage
    z3_total = int((df["verifier"] == "z3").sum())
    z3_active = int(((df["verifier"] == "z3") & (df["char_count"] > 0)).sum())
    z3_coverage_pct = round(z3_active / z3_total * 100, 1) if z3_total > 0 else 0.0

    return {
        "per_verifier": per_verifier,
        "kruskal_wallis": {"H": float(H), "p": float(p)},
        "effect_size_epsilon2": float(eps2),
        "dunn_pvalues": dunn_df.to_dict() if not dunn_df.empty else {},
        "ordering_confirmed": ordering,
        "direction_confirmed": direction_confirmed,
        "pairwise_diff_pct": pairwise,
        "z3_coverage_pct": z3_coverage_pct,
        "n_failing_solutions": len(df["task_id"].unique()),
    }
