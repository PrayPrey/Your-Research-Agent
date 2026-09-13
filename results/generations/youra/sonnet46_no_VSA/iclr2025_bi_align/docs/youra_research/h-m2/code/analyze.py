"""H-M2: Partial Spearman + Fisher Z Difference Test."""
import os
import json
import logging
import warnings
from typing import Tuple

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm as scipy_norm
import pingouin as pg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import ExperimentConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FR-1: Data Loading
# ---------------------------------------------------------------------------

def load_data(cfg: ExperimentConfig) -> pd.DataFrame:
    """Load H-E1 CSV, dropna on required cols, normalize BBQ_accuracy, add family col."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.normpath(os.path.join(script_dir, cfg.data_path))
    if not os.path.exists(data_path):
        raise RuntimeError(f"Data file not found: {data_path}")

    df = pd.read_csv(data_path)
    logger.info(f"Loaded CSV: {len(df)} rows, columns: {list(df.columns)}")

    # Rename BBQ_accuracy → bbq_accuracy for internal use
    if "BBQ_accuracy" in df.columns and "bbq_accuracy" not in df.columns:
        df = df.rename(columns={"BBQ_accuracy": "bbq_accuracy"})

    # Merge BBQ data from separate file if not present in main CSV
    if "bbq_accuracy" not in df.columns:
        bbq_path = os.path.normpath(os.path.join(script_dir, cfg.bbq_path))
        if not os.path.exists(bbq_path):
            raise RuntimeError(f"BBQ file not found: {bbq_path}")
        bbq_df = pd.read_csv(bbq_path)
        df = df.merge(bbq_df[["model_name", "bbq_accuracy"]], on="model_name", how="inner")
        logger.info(f"Merged BBQ data: {len(df)} rows after inner join")

    required_internal = ["model_name", "TruthfulQA_MC2", "bbq_accuracy", "MMLU"]
    missing = [c for c in required_internal if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing columns: {missing}. Available: {list(df.columns)}")

    df = df[required_internal].dropna().copy()
    logger.info(f"After dropna: {len(df)} rows")

    # Normalize bbq_accuracy to [0, 100] if stored as fraction
    if df["bbq_accuracy"].max() <= 1.0:
        df["bbq_accuracy"] = df["bbq_accuracy"] * 100.0
        logger.info("Normalized bbq_accuracy from [0,1] to [0,100]")

    # Extract model family (org-prefix before '/')
    df["family"] = df["model_name"].str.split("/").str[0]

    if len(df) < cfg.n_min:
        raise RuntimeError(f"N={len(df)} < n_min={cfg.n_min} after cleaning")

    logger.info(f"load_data OK: N={len(df)}, families={df['family'].nunique()}")
    return df


# ---------------------------------------------------------------------------
# FR-2: Raw Spearman Correlation
# ---------------------------------------------------------------------------

def compute_raw_spearman(df: pd.DataFrame) -> dict:
    """Compute raw Spearman rho(TruthfulQA_MC2, bbq_accuracy). Returns {raw_rho, raw_p}."""
    result = stats.spearmanr(df["TruthfulQA_MC2"], df["bbq_accuracy"])
    raw_rho = float(result.statistic)
    raw_p = float(result.pvalue)
    if not (abs(raw_rho) < 1.0):
        raise RuntimeError(f"arctanh domain error: raw_rho={raw_rho}")
    logger.info(f"raw_rho={raw_rho:.4f}, raw_p={raw_p:.4e}")
    return {"raw_rho": raw_rho, "raw_p": raw_p}


# ---------------------------------------------------------------------------
# FR-3: Partial Spearman Correlation
# ---------------------------------------------------------------------------

def compute_partial_spearman(df: pd.DataFrame, raw_rho: float) -> dict:
    """Compute partial Spearman(TruthfulQA_MC2, bbq_accuracy | MMLU)."""
    # Singular matrix guard: check zero-variance columns
    for col in ["TruthfulQA_MC2", "bbq_accuracy", "MMLU"]:
        if df[col].std() == 0.0:
            raise RuntimeError(f"Zero variance in column '{col}' — singular matrix would result")

    with warnings.catch_warnings():
        warnings.filterwarnings("error", category=RuntimeWarning)
        try:
            result = pg.partial_corr(
                data=df,
                x="TruthfulQA_MC2",
                y="bbq_accuracy",
                covar=["MMLU"],
                method="spearman",
            )
        except RuntimeWarning as e:
            raise RuntimeError(f"pingouin singular matrix: {e}") from e

    partial_rho = float(result["r"].iloc[0])
    # pingouin >= 0.5.4 uses 'p-val', older uses 'p_val'
    p_col = "p-val" if "p-val" in result.columns else "p_val"
    partial_p = float(result[p_col].iloc[0])

    if not (abs(partial_rho) < 1.0):
        raise RuntimeError(f"arctanh domain error: partial_rho={partial_rho}")

    # Mechanism activation check
    if not (abs(partial_rho - raw_rho) > 1e-6):
        raise RuntimeError(
            f"Mechanism activation failed: partial_rho={partial_rho:.6f} == raw_rho={raw_rho:.6f}"
        )

    logger.info(f"partial_rho={partial_rho:.4f}, partial_p={partial_p:.4e}")
    return {"partial_rho": partial_rho, "partial_p": partial_p}


# ---------------------------------------------------------------------------
# FR-4: Fisher Z Difference Test
# ---------------------------------------------------------------------------

def fisher_z_difference_test(raw_rho: float, partial_rho: float, N: int) -> dict:
    """Same-sample Fisher z difference test. SE=sqrt(2/(N-3))."""
    z_raw = float(np.arctanh(raw_rho))
    z_partial = float(np.arctanh(partial_rho))
    se = float(np.sqrt(2.0 / (N - 3)))
    z_diff = float((z_raw - z_partial) / se)
    p_value = float(2.0 * (1.0 - scipy_norm.cdf(abs(z_diff))))
    outcome = "SIGNIFICANT" if p_value < 0.05 else "NULL"
    logger.info(
        f"raw_rho={raw_rho:.4f}, partial_rho={partial_rho:.4f}, "
        f"z_diff={z_diff:.4f}, p={p_value:.4f}, outcome={outcome}"
    )
    return {
        "z_raw": z_raw,
        "z_partial": z_partial,
        "z_diff": z_diff,
        "p_value": p_value,
        "outcome": outcome,
    }


# ---------------------------------------------------------------------------
# FR-5: BCa Bootstrap Confidence Intervals
# ---------------------------------------------------------------------------

def _bca_partial_rho_with_dist(
    df: pd.DataFrame, n_boot: int, seed: int
) -> Tuple[Tuple[float, float], np.ndarray]:
    """BCa CI for partial_rho via manual bootstrap. Returns (ci_tuple, boot_dist)."""
    rng = np.random.default_rng(seed)
    N = len(df)

    obs_result = pg.partial_corr(
        data=df, x="TruthfulQA_MC2", y="bbq_accuracy", covar=["MMLU"], method="spearman"
    )
    obs_rho = float(obs_result["r"].iloc[0])

    # Bootstrap distribution
    boot_rhos = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, N, size=N)
        df_boot = df.iloc[idx].reset_index(drop=True)
        try:
            r = pg.partial_corr(
                data=df_boot, x="TruthfulQA_MC2", y="bbq_accuracy",
                covar=["MMLU"], method="spearman"
            )
            boot_rhos[i] = float(r["r"].iloc[0])
        except Exception:
            boot_rhos[i] = obs_rho

    # BCa bias correction z0
    z0 = scipy_norm.ppf(np.mean(boot_rhos < obs_rho))

    # Acceleration a: jackknife estimate
    jack_rhos = np.empty(N)
    for j in range(N):
        df_jack = df.drop(index=df.index[j]).reset_index(drop=True)
        try:
            r = pg.partial_corr(
                data=df_jack, x="TruthfulQA_MC2", y="bbq_accuracy",
                covar=["MMLU"], method="spearman"
            )
            jack_rhos[j] = float(r["r"].iloc[0])
        except Exception:
            jack_rhos[j] = obs_rho

    jack_mean = np.mean(jack_rhos)
    num = np.sum((jack_mean - jack_rhos) ** 3)
    den = 6.0 * (np.sum((jack_mean - jack_rhos) ** 2) ** 1.5)
    a = float(num / den) if den != 0 else 0.0

    # CI quantile bounds
    alpha = 0.05
    z_alpha = scipy_norm.ppf(alpha / 2)
    z_1ma = scipy_norm.ppf(1.0 - alpha / 2)

    def _adj(z_a: float) -> float:
        return float(scipy_norm.cdf(z0 + (z0 + z_a) / (1.0 - a * (z0 + z_a))))

    lo_q = _adj(z_alpha)
    hi_q = _adj(z_1ma)

    sorted_boot = np.sort(boot_rhos)
    lo = float(np.percentile(sorted_boot, lo_q * 100))
    hi = float(np.percentile(sorted_boot, hi_q * 100))
    return (lo, hi), boot_rhos


def compute_bca_cis(df: pd.DataFrame, cfg: ExperimentConfig) -> dict:
    """BCa CIs for raw_rho and partial_rho; overlap status."""
    x = df["TruthfulQA_MC2"].to_numpy()
    y = df["bbq_accuracy"].to_numpy()

    logger.info("Computing BCa CI for raw_rho via pingouin.compute_bootci...")
    ci_raw_arr, boot_raw = pg.compute_bootci(
        x=x, y=y, func="spearman", method="bca",
        paired=True, n_boot=cfg.n_boot, seed=cfg.seed,
        return_dist=True,
    )
    ci_raw = (float(ci_raw_arr[0]), float(ci_raw_arr[1]))

    logger.info("Computing BCa CI for partial_rho via manual bootstrap + jackknife...")
    ci_partial, boot_partial = _bca_partial_rho_with_dist(df, cfg.n_boot, cfg.seed)

    # CI overlap
    overlapping = (ci_raw[0] <= ci_partial[1]) and (ci_partial[0] <= ci_raw[1])
    status = "overlapping" if overlapping else "non-overlapping"
    logger.info(f"ci_raw={ci_raw}, ci_partial={ci_partial}, overlap={status}")

    return {
        "ci_raw": ci_raw,
        "ci_partial": ci_partial,
        "ci_overlap_status": status,
        "boot_dist_raw": boot_raw,
        "boot_dist_partial": boot_partial,
    }


# ---------------------------------------------------------------------------
# FR-5 (cont.): Family Robustness
# ---------------------------------------------------------------------------

def compute_family_robustness(df: pd.DataFrame, cfg: ExperimentConfig) -> dict:
    """Per-family Spearman rho for families with >= min_family_size members."""
    family_sizes = df.groupby("family").size()
    valid_families = family_sizes[family_sizes >= cfg.min_family_size].index

    family_rhos = {}
    for fam in valid_families:
        sub = df[df["family"] == fam]
        if len(sub) < 3:
            continue
        try:
            r = stats.spearmanr(sub["TruthfulQA_MC2"], sub["bbq_accuracy"])
            family_rhos[fam] = float(r.statistic)
        except Exception:
            pass

    family_rho_series = pd.Series(family_rhos, name="spearman_rho")
    sizes = family_sizes[valid_families]
    # Weighted mean (by family size)
    weighted_rho = float(
        np.average(list(family_rhos.values()), weights=[sizes.get(f, 1) for f in family_rhos])
    ) if family_rhos else float("nan")

    logger.info(f"Family robustness: {len(family_rhos)} families, weighted_rho={weighted_rho:.4f}")
    return {"family_rhos": family_rho_series, "weighted_rho": weighted_rho}


# ---------------------------------------------------------------------------
# FR-6: Gate Evaluation
# ---------------------------------------------------------------------------

def evaluate_gate(results: dict) -> dict:
    """Gate PASS if p_value is a valid float in [0,1]. Assigns SIGNIFICANT/NULL."""
    p_value = results.get("p_value")
    gate_pass = (
        p_value is not None
        and not np.isnan(float(p_value) if p_value is not None else float("nan"))
        and 0.0 <= p_value <= 1.0
    )
    outcome = results.get("outcome", "NULL")
    # Outcome override: SIGNIFICANT if p<0.05 OR non-overlapping CIs
    ci_status = results.get("ci_overlap_status", "overlapping")
    if (p_value is not None and p_value < 0.05) or ci_status == "non-overlapping":
        outcome = "SIGNIFICANT"
    else:
        outcome = "NULL"

    results["gate_pass"] = gate_pass
    results["outcome"] = outcome
    p_str = f"{p_value:.4f}" if p_value is not None else "None"
    logger.info(
        f"Gate: p={p_str}, ci_overlap={ci_status}, "
        f"gate_pass={gate_pass}, outcome={outcome}"
    )
    return results


# ---------------------------------------------------------------------------
# FR-7: Visualization (5 figures)
# ---------------------------------------------------------------------------

def _resolve_dir(cfg_dir: str, base: str) -> str:
    if os.path.isabs(cfg_dir):
        return cfg_dir
    return os.path.normpath(os.path.join(base, cfg_dir))


def plot_rho_comparison(results: dict, cfg: ExperimentConfig) -> str:
    """Fig1: Grouped bar chart raw_rho vs partial_rho with BCa CI error bars."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = _resolve_dir(cfg.figures_dir, script_dir)
    os.makedirs(fig_dir, exist_ok=True)

    raw_rho = results["raw_rho"]
    partial_rho = results["partial_rho"]
    ci_raw = results["ci_raw"]
    ci_partial = results["ci_partial"]
    p_value = results["p_value"]
    outcome = results["outcome"]

    color = cfg.color_significant if outcome == "SIGNIFICANT" else cfg.color_null

    raw_yerr = np.array([[raw_rho - ci_raw[0]], [ci_raw[1] - raw_rho]])
    par_yerr = np.array([[partial_rho - ci_partial[0]], [ci_partial[1] - partial_rho]])
    all_yerr = np.hstack([raw_yerr, par_yerr])  # shape (2, 2)

    fig, ax = plt.subplots(figsize=cfg.fig_size, dpi=cfg.fig_dpi)
    x_pos = [0, 1]
    ax.bar(x_pos, [raw_rho, partial_rho], yerr=all_yerr, color=color,
           width=0.4, capsize=5, error_kw={"elinewidth": 1.5})
    ax.set_xticks(x_pos)
    ax.set_xticklabels(["Raw ρ", "Partial ρ\n(covar=MMLU)"])
    ax.set_ylabel("Spearman ρ")
    ax.set_title("TruthfulQA×BBQ Correlation: Raw vs Partial Spearman")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

    p_str = f"p={p_value:.4f}" if p_value >= 0.001 else f"p={p_value:.2e}"
    sig_str = "SIGNIFICANT" if outcome == "SIGNIFICANT" else "NULL"
    ax.annotate(
        f"Fisher z: {p_str}\n({sig_str})",
        xy=(0.5, 0.95), xycoords="axes fraction",
        ha="center", va="top", fontsize=10,
    )

    fig.tight_layout()
    out_path = os.path.join(fig_dir, "fig1_rho_comparison.png")
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved: {out_path}")
    return out_path


def plot_scatter_mmlu_gradient(df: pd.DataFrame, cfg: ExperimentConfig) -> str:
    """Fig2: TruthfulQA_MC2 vs bbq_accuracy scatter with MMLU as color gradient."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = _resolve_dir(cfg.figures_dir, script_dir)
    os.makedirs(fig_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=cfg.fig_size, dpi=cfg.fig_dpi)
    sc = ax.scatter(
        df["TruthfulQA_MC2"], df["bbq_accuracy"],
        c=df["MMLU"], cmap="viridis", alpha=0.7, s=30, edgecolors="none",
    )
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("MMLU score (0-100)")
    ax.set_xlabel("TruthfulQA MC2 (%)")
    ax.set_ylabel("BBQ accuracy (%)")
    ax.set_title(f"TruthfulQA MC2 vs BBQ Accuracy (N={len(df)}, colored by MMLU)")

    fig.tight_layout()
    out_path = os.path.join(fig_dir, "fig2_scatter_mmlu_gradient.png")
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved: {out_path}")
    return out_path


def plot_bootstrap_distributions(results: dict, cfg: ExperimentConfig) -> str:
    """Fig3: Overlaid bootstrap distribution histograms for raw_rho and partial_rho."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = _resolve_dir(cfg.figures_dir, script_dir)
    os.makedirs(fig_dir, exist_ok=True)

    boot_raw = results["boot_dist_raw"]
    boot_partial = results["boot_dist_partial"]
    ci_raw = results["ci_raw"]
    ci_partial = results["ci_partial"]

    fig, ax = plt.subplots(figsize=cfg.fig_size, dpi=cfg.fig_dpi)
    ax.hist(boot_raw, bins=60, alpha=0.5, color="steelblue", label="Raw ρ bootstrap")
    ax.hist(boot_partial, bins=60, alpha=0.5, color="darkorange", label="Partial ρ bootstrap")
    ax.axvline(ci_raw[0], color="steelblue", linestyle="--", linewidth=1, label="Raw 95% CI")
    ax.axvline(ci_raw[1], color="steelblue", linestyle="--", linewidth=1)
    ax.axvline(ci_partial[0], color="darkorange", linestyle="--", linewidth=1, label="Partial 95% CI")
    ax.axvline(ci_partial[1], color="darkorange", linestyle="--", linewidth=1)
    ax.set_xlabel("Spearman ρ")
    ax.set_ylabel("Bootstrap count")
    ax.set_title("Bootstrap Distributions: Raw vs Partial Spearman ρ")
    ax.legend()

    fig.tight_layout()
    out_path = os.path.join(fig_dir, "fig3_bootstrap_distributions.png")
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved: {out_path}")
    return out_path


def plot_family_rho_bar(results: dict, cfg: ExperimentConfig) -> str:
    """Fig4: Per-family Spearman rho bar chart (families >= min_family_size)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = _resolve_dir(cfg.figures_dir, script_dir)
    os.makedirs(fig_dir, exist_ok=True)

    family_rhos = results["family_rhos"]
    family_rhos_sorted = family_rhos.sort_values(ascending=False)
    colors = [cfg.color_significant if r > 0 else cfg.color_null for r in family_rhos_sorted]

    fig_w = max(8.0, len(family_rhos_sorted) * 0.6)
    fig, ax = plt.subplots(figsize=(fig_w, 5.0), dpi=cfg.fig_dpi)
    ax.bar(range(len(family_rhos_sorted)), family_rhos_sorted.values, color=colors)
    ax.set_xticks(range(len(family_rhos_sorted)))
    ax.set_xticklabels(family_rhos_sorted.index, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Spearman ρ")
    ax.set_title(f"Per-Family Spearman ρ (families ≥ {cfg.min_family_size} models)")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    weighted_rho = results.get("weighted_rho", float("nan"))
    if not np.isnan(weighted_rho):
        ax.axhline(weighted_rho, color="grey", linewidth=1.5, linestyle=":",
                   label=f"Weighted mean ρ={weighted_rho:.3f}")
        ax.legend()

    fig.tight_layout()
    out_path = os.path.join(fig_dir, "fig4_family_rho_bar.png")
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved: {out_path}")
    return out_path


def plot_fisher_z_numberline(results: dict, cfg: ExperimentConfig) -> str:
    """Fig5: Horizontal number-line showing z_raw and z_partial with 95% CIs."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = _resolve_dir(cfg.figures_dir, script_dir)
    os.makedirs(fig_dir, exist_ok=True)

    z_raw = results["z_raw"]
    z_partial = results["z_partial"]
    N = results["N"]
    p_value = results["p_value"]
    outcome = results["outcome"]

    se_single = 1.0 / np.sqrt(N - 3)
    z_crit = 1.96

    fig, ax = plt.subplots(figsize=(10, 3), dpi=cfg.fig_dpi)
    ax.set_yticks([])
    ax.axhline(0, color="black", linewidth=0.8)

    for z_val, label, color, y_offset in [
        (z_raw, "z_raw", "steelblue", 0.15),
        (z_partial, "z_partial", "darkorange", -0.15),
    ]:
        lo = z_val - z_crit * se_single
        hi = z_val + z_crit * se_single
        ax.plot([lo, hi], [y_offset, y_offset], color=color, linewidth=3, solid_capstyle="round")
        ax.plot(z_val, y_offset, "o", color=color, markersize=8, label=f"{label}={z_val:.3f}")

    ax.axvline(0, color="black", linewidth=1, linestyle="--", alpha=0.5)
    ax.axvline(1.96, color="red", linewidth=0.8, linestyle=":", alpha=0.5, label="±1.96")
    ax.axvline(-1.96, color="red", linewidth=0.8, linestyle=":", alpha=0.5)

    p_str = f"p={p_value:.4f}" if p_value >= 0.001 else f"p={p_value:.2e}"
    ax.set_title(f"Fisher Z Number-Line: {p_str} ({outcome})")
    ax.set_xlabel("Fisher z-transformed ρ")
    ax.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    out_path = os.path.join(fig_dir, "fig5_fisher_z_numberline.png")
    fig.savefig(out_path)
    plt.close(fig)
    logger.info(f"Saved: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# FR-8: Results Persistence
# ---------------------------------------------------------------------------

def save_results(results: dict, cfg: ExperimentConfig) -> None:
    """Save results dict to h_m2_results.json and h_m2_summary.txt."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = _resolve_dir(cfg.results_dir, script_dir)
    os.makedirs(results_dir, exist_ok=True)

    # Serialize numpy arrays as lists for JSON
    def _jsonify(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Series):
            return obj.to_dict()
        return obj

    json_safe = {k: _jsonify(v) for k, v in results.items()}
    json_path = os.path.join(results_dir, "h_m2_results.json")
    with open(json_path, "w") as f:
        json.dump(json_safe, f, indent=2)
    logger.info(f"Saved: {json_path}")

    gate_str = "PASS" if results.get("gate_pass") else "FAIL"
    outcome = results.get("outcome", "N/A")
    summary = f"""H-M2 Results Summary
====================
Hypothesis: Partial Spearman + Fisher Z Difference Test
N: {results.get('N', 'N/A')}
Gate: MUST_WORK — p_value computed without error

Raw Spearman (TruthfulQA MC2 × BBQ accuracy):
  rho    = {results.get('raw_rho', float('nan')):.4f}
  p      = {results.get('raw_p', float('nan')):.4e}
  CI 95% = {results.get('ci_raw', ('N/A', 'N/A'))}

Partial Spearman (controlling MMLU):
  rho    = {results.get('partial_rho', float('nan')):.4f}
  p      = {results.get('partial_p', float('nan')):.4e}
  CI 95% = {results.get('ci_partial', ('N/A', 'N/A'))}

CI overlap: {results.get('ci_overlap_status', 'N/A')}

Fisher Z Difference Test (same-sample):
  z_raw     = {results.get('z_raw', float('nan')):.4f}
  z_partial = {results.get('z_partial', float('nan')):.4f}
  z_diff    = {results.get('z_diff', float('nan')):.4f}
  p_value   = {results.get('p_value', float('nan')):.4f}

Outcome: {outcome}
Gate result: {gate_str}
"""
    txt_path = os.path.join(results_dir, "h_m2_summary.txt")
    with open(txt_path, "w") as f:
        f.write(summary)
    logger.info(f"Saved: {txt_path}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run(cfg: ExperimentConfig) -> dict:
    """Orchestrate: load → raw_spearman → partial_spearman → fisher_z
    → bca_cis → family_robustness → gate_eval → plot×5 → save → return results."""
    np.random.seed(cfg.seed)

    logger.info("=== H-M2: Partial Spearman + Fisher Z Difference Test ===")

    df = load_data(cfg)
    N = len(df)

    raw = compute_raw_spearman(df)
    partial = compute_partial_spearman(df, raw["raw_rho"])
    fisher = fisher_z_difference_test(raw["raw_rho"], partial["partial_rho"], N)

    logger.info("Computing BCa bootstrap CIs (this may take ~30-60s)...")
    bca = compute_bca_cis(df, cfg)

    family = compute_family_robustness(df, cfg)

    results = {
        "hypothesis_id": "h-m2",
        "N": N,
        **raw,
        **partial,
        **fisher,
        "ci_raw": bca["ci_raw"],
        "ci_partial": bca["ci_partial"],
        "ci_overlap_status": bca["ci_overlap_status"],
        "boot_dist_raw": bca["boot_dist_raw"],
        "boot_dist_partial": bca["boot_dist_partial"],
        "family_rhos": family["family_rhos"],
        "weighted_rho": family["weighted_rho"],
    }

    results = evaluate_gate(results)

    fig1 = plot_rho_comparison(results, cfg)
    fig2 = plot_scatter_mmlu_gradient(df, cfg)
    fig3 = plot_bootstrap_distributions(results, cfg)
    fig4 = plot_family_rho_bar(results, cfg)
    fig5 = plot_fisher_z_numberline(results, cfg)

    results["figures"] = {
        "fig1_rho_comparison": fig1,
        "fig2_scatter_mmlu_gradient": fig2,
        "fig3_bootstrap_distributions": fig3,
        "fig4_family_rho_bar": fig4,
        "fig5_fisher_z_numberline": fig5,
    }

    save_results(results, cfg)

    gate_str = "PASS" if results["gate_pass"] else "FAIL"
    logger.info(f"=== H-M2 COMPLETE: gate={gate_str}, outcome={results['outcome']} ===")
    return results
