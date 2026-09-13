import os
import json
import logging
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from config import AnalysisConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_data(cfg: AnalysisConfig) -> pd.DataFrame:
    """Load H-E1 LLM CSV + BBQ per-model CSV, join on model_name, normalize bbq_accuracy.
    Raises RuntimeError if N < cfg.n_min."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, cfg.data_path)
    if not os.path.exists(data_path):
        raise RuntimeError(f"Data file not found: {data_path}")

    df_llm = pd.read_csv(data_path)
    logger.info(f"Loaded LLM CSV: {len(df_llm)} rows, columns: {list(df_llm.columns)}")

    # If bbq_accuracy already in the main CSV (future-proofing), use it directly
    if "bbq_accuracy" not in df_llm.columns and "BBQ_accuracy" not in df_llm.columns:
        # Join with separate BBQ per-model scores (same data dir as LLM CSV)
        bbq_path = os.path.join(os.path.dirname(data_path), "..", "bbq_scores", "bbq_per_model.csv")
        bbq_path = os.path.normpath(bbq_path)
        if not os.path.exists(bbq_path):
            raise RuntimeError(f"BBQ scores file not found: {bbq_path}")
        df_bbq = pd.read_csv(bbq_path)
        logger.info(f"Loaded BBQ CSV: {len(df_bbq)} rows, columns: {list(df_bbq.columns)}")
        df = pd.merge(df_llm, df_bbq, on="model_name", how="inner")
        logger.info(f"After inner join: {len(df)} rows")
    else:
        df = df_llm.copy()
        if "BBQ_accuracy" in df.columns and "bbq_accuracy" not in df.columns:
            df = df.rename(columns={"BBQ_accuracy": "bbq_accuracy"})

    required = ["model_name", "TruthfulQA_MC2", "bbq_accuracy", "MMLU"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing columns: {missing}. Available: {list(df.columns)}")

    df = df[required].dropna()
    logger.info(f"After dropna: {len(df)} rows")

    # Normalize bbq_accuracy to [0,100] if stored as fraction
    if df["bbq_accuracy"].max() <= 1.0:
        df["bbq_accuracy"] = df["bbq_accuracy"] * 100
        logger.info("Normalized bbq_accuracy from [0,1] to [0,100]")

    if len(df) < cfg.n_min:
        raise RuntimeError(f"N={len(df)} < n_min={cfg.n_min} after cleaning")

    return df


def compute_correlations(df: pd.DataFrame) -> dict:
    """Compute Spearman rho and R² for 3 column pairs. Returns full results dict."""
    N = len(df)

    res1 = stats.spearmanr(df["MMLU"], df["TruthfulQA_MC2"])
    rho_mt = float(res1.statistic)
    p_mt = float(res1.pvalue)
    R2_mt = rho_mt ** 2

    res2 = stats.spearmanr(df["MMLU"], df["bbq_accuracy"])
    rho_mb = float(res2.statistic)
    p_mb = float(res2.pvalue)
    R2_mb = rho_mb ** 2

    res3 = stats.spearmanr(df["TruthfulQA_MC2"], df["bbq_accuracy"])
    rho_tb = float(res3.statistic)
    p_tb = float(res3.pvalue)

    gate_pass = (R2_mt > 0.05) and (R2_mb > 0.05)
    gate_str = "PASS" if gate_pass else "FAIL"
    logger.info(f"H-M1 gate: MMLU R²(TruthfulQA)={R2_mt:.3f}, R²(BBQ)={R2_mb:.3f} — {gate_str}")

    return {
        "hypothesis_id": "h-m1",
        "N": N,
        "rho_mmlu_truthqa": rho_mt,
        "R2_mmlu_truthqa": R2_mt,
        "p_mmlu_truthqa": p_mt,
        "rho_mmlu_bbq": rho_mb,
        "R2_mmlu_bbq": R2_mb,
        "p_mmlu_bbq": p_mb,
        "raw_rho_truth_bbq": rho_tb,
        "p_raw_truth_bbq": p_tb,
        "gate_pass": gate_pass,
    }


def verify_mechanism_activated(results: dict) -> tuple:
    """Validate results dict integrity. Returns (all_valid: bool, indicators: dict)."""
    indicators = {
        "n_valid": results.get("N", 0) >= 30,
        "r2_truthqa_valid": (
            not np.isnan(results.get("R2_mmlu_truthqa", float("nan")))
            and 0 <= results.get("R2_mmlu_truthqa", -1) <= 1
        ),
        "r2_bbq_valid": (
            not np.isnan(results.get("R2_mmlu_bbq", float("nan")))
            and 0 <= results.get("R2_mmlu_bbq", -1) <= 1
        ),
        "gate_computed": "gate_pass" in results,
        "baseline_rho_computed": "raw_rho_truth_bbq" in results,
    }
    all_valid = all(indicators.values())
    return all_valid, indicators


def _resolve_dir(cfg_dir: str, base: str) -> str:
    if os.path.isabs(cfg_dir):
        return cfg_dir
    return os.path.normpath(os.path.join(base, cfg_dir))


def plot_r2_bar(results: dict, cfg: AnalysisConfig) -> str:
    """Bar chart R²(MMLU×TruthfulQA) and R²(MMLU×BBQ) with 0.05 threshold line."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = _resolve_dir(cfg.figures_dir, script_dir)
    os.makedirs(fig_dir, exist_ok=True)

    labels = ["R²(MMLU×TruthfulQA)", "R²(MMLU×BBQ)"]
    values = [results["R2_mmlu_truthqa"], results["R2_mmlu_bbq"]]
    colors = [cfg.color_pass if v > cfg.r2_threshold else cfg.color_fail for v in values]

    fig, ax = plt.subplots(figsize=cfg.fig_bar_size, dpi=cfg.fig_dpi)
    bars = ax.bar(labels, values, color=colors, edgecolor="black", linewidth=0.8)
    ax.axhline(cfg.r2_threshold, color=cfg.color_threshold, linestyle="--", linewidth=1.5,
               label=f"Threshold = {cfg.r2_threshold}")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.005, f"{val:.3f}",
                ha="center", va="bottom", fontsize=10)
    ax.set_ylabel("Spearman R²")
    ax.set_title("H-M1: MMLU Scale Confound Pre-Test\nSpearman R² vs 0.05 Threshold")
    ax.legend()
    ax.set_ylim(0, max(max(values) * 1.2, cfg.r2_threshold * 1.5))
    plt.tight_layout()

    save_path = os.path.join(fig_dir, "h_m1_r2_bar.png")
    fig.savefig(save_path)
    plt.close(fig)
    logger.info(f"Saved: {save_path}")
    return save_path


def plot_scatter_mmlu_truthqa(df: pd.DataFrame, results: dict, cfg: AnalysisConfig) -> str:
    """Scatter MMLU vs TruthfulQA_MC2, annotated with rho value."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = _resolve_dir(cfg.figures_dir, script_dir)
    os.makedirs(fig_dir, exist_ok=True)

    rho = results["rho_mmlu_truthqa"]
    R2 = results["R2_mmlu_truthqa"]
    N = results["N"]

    fig, ax = plt.subplots(figsize=cfg.fig_scatter_size, dpi=cfg.fig_dpi)
    ax.scatter(df["MMLU"], df["TruthfulQA_MC2"], alpha=0.4, s=20,
               color=cfg.color_scatter, edgecolors="none")
    ax.set_xlabel("MMLU Score (0-100)")
    ax.set_ylabel("TruthfulQA MC2 (0-100)")
    ax.set_title(f"MMLU vs TruthfulQA MC2 (N={N})\nSpearman ρ={rho:.3f}, R²={R2:.3f}")
    ax.annotate(f"ρ = {rho:.3f}\nR² = {R2:.3f}",
                xy=(0.05, 0.88), xycoords="axes fraction", fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.7))
    plt.tight_layout()

    save_path = os.path.join(fig_dir, "h_m1_scatter_mmlu_truthqa.png")
    fig.savefig(save_path)
    plt.close(fig)
    logger.info(f"Saved: {save_path}")
    return save_path


def plot_scatter_mmlu_bbq(df: pd.DataFrame, results: dict, cfg: AnalysisConfig) -> str:
    """Scatter MMLU vs bbq_accuracy, annotated with rho value."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = _resolve_dir(cfg.figures_dir, script_dir)
    os.makedirs(fig_dir, exist_ok=True)

    rho = results["rho_mmlu_bbq"]
    R2 = results["R2_mmlu_bbq"]
    N = results["N"]

    fig, ax = plt.subplots(figsize=cfg.fig_scatter_size, dpi=cfg.fig_dpi)
    ax.scatter(df["MMLU"], df["bbq_accuracy"], alpha=0.4, s=20,
               color=cfg.color_scatter, edgecolors="none")
    ax.set_xlabel("MMLU Score (0-100)")
    ax.set_ylabel("BBQ Accuracy (0-100)")
    ax.set_title(f"MMLU vs BBQ Accuracy (N={N})\nSpearman ρ={rho:.3f}, R²={R2:.3f}")
    ax.annotate(f"ρ = {rho:.3f}\nR² = {R2:.3f}",
                xy=(0.05, 0.88), xycoords="axes fraction", fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.7))
    plt.tight_layout()

    save_path = os.path.join(fig_dir, "h_m1_scatter_mmlu_bbq.png")
    fig.savefig(save_path)
    plt.close(fig)
    logger.info(f"Saved: {save_path}")
    return save_path


def plot_correlation_heatmap(df: pd.DataFrame, cfg: AnalysisConfig) -> str:
    """Spearman correlation heatmap for {MMLU, TruthfulQA_MC2, bbq_accuracy}."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = _resolve_dir(cfg.figures_dir, script_dir)
    os.makedirs(fig_dir, exist_ok=True)

    cols = ["MMLU", "TruthfulQA_MC2", "bbq_accuracy"]
    corr_matrix = df[cols].corr(method="spearman")

    fig, ax = plt.subplots(figsize=cfg.fig_heatmap_size, dpi=cfg.fig_dpi)
    sns.heatmap(corr_matrix, annot=True, fmt=".3f", cmap="RdYlGn",
                vmin=-1, vmax=1, ax=ax, linewidths=0.5,
                xticklabels=["MMLU", "TruthfulQA", "BBQ"],
                yticklabels=["MMLU", "TruthfulQA", "BBQ"])
    ax.set_title("Spearman Correlation Matrix\n{MMLU, TruthfulQA MC2, BBQ accuracy}")
    plt.tight_layout()

    save_path = os.path.join(fig_dir, "h_m1_heatmap.png")
    fig.savefig(save_path)
    plt.close(fig)
    logger.info(f"Saved: {save_path}")
    return save_path


def save_results(results: dict, cfg: AnalysisConfig) -> None:
    """Write results to h_m1_results.json and h_m1_summary.txt in cfg.results_dir."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = _resolve_dir(cfg.results_dir, script_dir)
    os.makedirs(results_dir, exist_ok=True)

    json_path = os.path.join(results_dir, "h_m1_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved results JSON: {json_path}")

    gate_str = "PASS" if results.get("gate_pass") else "FAIL"
    summary = f"""H-M1 Results Summary
====================
Hypothesis: MMLU as Scale Covariate Pre-Test
N: {results['N']}
Gate: MUST_WORK — both R² > 0.05

MMLU × TruthfulQA MC2:
  rho  = {results['rho_mmlu_truthqa']:.4f}
  R²   = {results['R2_mmlu_truthqa']:.4f}
  p    = {results['p_mmlu_truthqa']:.4e}

MMLU × BBQ accuracy:
  rho  = {results['rho_mmlu_bbq']:.4f}
  R²   = {results['R2_mmlu_bbq']:.4f}
  p    = {results['p_mmlu_bbq']:.4e}

Baseline (TruthfulQA × BBQ, for H-M2):
  rho  = {results['raw_rho_truth_bbq']:.4f}
  p    = {results['p_raw_truth_bbq']:.4e}

Gate result: {gate_str}
"""
    txt_path = os.path.join(results_dir, "h_m1_summary.txt")
    with open(txt_path, "w") as f:
        f.write(summary)
    logger.info(f"Saved summary: {txt_path}")


def run(cfg: AnalysisConfig) -> dict:
    """Orchestrate: load → correlate → verify → plot×4 → save → return results."""
    np.random.seed(cfg.seed)

    logger.info("=== H-M1: MMLU Scale Covariate Pre-Test ===")

    df = load_data(cfg)
    results = compute_correlations(df)
    mechanism_ok, indicators = verify_mechanism_activated(results)

    if not mechanism_ok:
        failed = [k for k, v in indicators.items() if not v]
        raise RuntimeError(f"Mechanism activation failed: {failed}")
    logger.info(f"Mechanism activated: {indicators}")

    fig_bar = plot_r2_bar(results, cfg)
    fig_scatter_mt = plot_scatter_mmlu_truthqa(df, results, cfg)
    fig_scatter_mb = plot_scatter_mmlu_bbq(df, results, cfg)
    fig_heatmap = plot_correlation_heatmap(df, cfg)

    results["figures"] = {
        "r2_bar": fig_bar,
        "scatter_mmlu_truthqa": fig_scatter_mt,
        "scatter_mmlu_bbq": fig_scatter_mb,
        "heatmap": fig_heatmap,
    }
    results["mechanism_activated"] = mechanism_ok
    results["mechanism_indicators"] = indicators

    save_results(results, cfg)

    gate_str = "PASS" if results["gate_pass"] else "FAIL"
    logger.info(f"=== H-M1 COMPLETE: gate={gate_str} ===")
    return results
