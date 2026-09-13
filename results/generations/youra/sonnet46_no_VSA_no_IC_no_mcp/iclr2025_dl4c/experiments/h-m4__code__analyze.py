"""A-8: Visualization — 4 figures for h-m4."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from config import H_M4_Config, BENCHMARK_ORDER, FigureConfig


BM_LABELS = ["HumanEval", "MBPP", "LCB-Easy", "LCB-Medium", "LCB-Hard"]


def _save(fig, path: str, cfg: FigureConfig):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=cfg.dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[Fig] Saved {path}")


def plot_7b_delta_by_difficulty(deltas_7b: dict, cis: dict, cfg: FigureConfig) -> str:
    fig, ax = plt.subplots(figsize=(cfg.fig_width, cfg.fig_height))
    x = np.arange(len(BENCHMARK_ORDER))
    vals = [deltas_7b[bm] for bm in BENCHMARK_ORDER]
    yerr_lo = [vals[i] - cis[bm][0] for i, bm in enumerate(BENCHMARK_ORDER)]
    yerr_hi = [cis[bm][1] - vals[i] for i, bm in enumerate(BENCHMARK_ORDER)]

    bars = ax.bar(x, vals, color=cfg.color_7b, alpha=0.8, label="RLEF-Fraction − SFT")
    ax.errorbar(x, vals, yerr=[yerr_lo, yerr_hi], fmt="none", color="black", capsize=5)
    ax.plot(x, vals, "o--", color=cfg.color_trend, linewidth=1.5, label="trend")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(BM_LABELS, fontsize=10)
    ax.set_ylabel("Δ pass@1 (RLEF-Fraction − SFT)", fontsize=11)
    ax.set_title("7B: Δ(RLEF-Fraction, SFT) by Difficulty (h-e1 data)")
    ax.legend()
    out = str(Path(cfg.output_dir) / cfg.fig1_name)
    _save(fig, out, cfg)
    return out


def plot_jt_test_result(jt_z: float, jt_p: float, is_monotone: bool,
                        violations: list, cfg: FigureConfig) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(cfg.fig_width, cfg.fig_height * 0.8))

    ax_left = axes[0]
    color = cfg.color_trend if jt_p < 0.05 else "#F44336"
    ax_left.bar(["JT z-score"], [jt_z], color=color, alpha=0.85)
    ax_left.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax_left.set_title(f"JT z = {jt_z:.3f}\np = {jt_p:.4f}")
    ax_left.set_ylabel("z-score")

    ax_right = axes[1]
    result_text = (
        f"Gate: {'PASS' if (jt_p < 0.05 and jt_z > 0) else 'FAIL'}\n"
        f"Monotone: {is_monotone}\n"
        f"Violations: {len(violations)}\n"
        f"p = {jt_p:.4f}"
    )
    ax_right.text(0.5, 0.5, result_text, transform=ax_right.transAxes,
                  ha="center", va="center", fontsize=12,
                  bbox=dict(boxstyle="round,pad=0.5", facecolor=color, alpha=0.3))
    ax_right.axis("off")
    ax_right.set_title("JT Test Summary")

    fig.suptitle("Jonckheere-Terpstra Monotonicity Test")
    plt.tight_layout()
    out = str(Path(cfg.output_dir) / cfg.fig2_name)
    _save(fig, out, cfg)
    return out


def plot_1b3_delta_by_difficulty(deltas_1b3: dict, cfg: FigureConfig) -> str:
    fig, ax = plt.subplots(figsize=(cfg.fig_width, cfg.fig_height))
    x = np.arange(len(BENCHMARK_ORDER))
    vals = [deltas_1b3.get(bm, float("nan")) for bm in BENCHMARK_ORDER]
    finite = [v for v in vals if not np.isnan(v)]

    ax.bar(x, [v if not np.isnan(v) else 0 for v in vals], color=cfg.color_1b3, alpha=0.8)
    if finite:
        ax.plot(x[:len(finite)], finite, "s--", color=cfg.color_trend, linewidth=1.5)
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(BM_LABELS, fontsize=10)
    ax.set_ylabel("Δ pass@1 (RLEF-Fraction − SFT)", fontsize=11)
    ax.set_title("1.3B: Δ(RLEF-Fraction, SFT) by Difficulty")
    out = str(Path(cfg.output_dir) / cfg.fig3_name)
    _save(fig, out, cfg)
    return out


def plot_delta_ratio_gate(delta_ratio: float, threshold: float, cfg: FigureConfig) -> str:
    fig, ax = plt.subplots(figsize=(cfg.fig_width * 0.6, cfg.fig_height))
    color = cfg.color_trend if delta_ratio >= threshold else "#F44336"
    ratio_plot = min(delta_ratio, 5.0) if not np.isinf(delta_ratio) else 5.0
    ax.bar(["Δ_ratio (1.3B)"], [ratio_plot], color=color, alpha=0.85)
    ax.axhline(threshold, color="navy", linestyle="--", linewidth=1.5,
               label=f"Gate threshold = {threshold}")
    ax.set_ylabel("Δ_LCB-Hard / Δ_HumanEval")
    ax.set_title(f"1.3B Delta Ratio Gate\n"
                 f"ratio = {delta_ratio:.3f} — {'PASS' if delta_ratio >= threshold else 'FAIL'}")
    ax.legend()
    out = str(Path(cfg.output_dir) / cfg.fig4_name)
    _save(fig, out, cfg)
    return out


def generate_all_figures(results: dict, cfg: H_M4_Config) -> list:
    """Generate all 4 figures. Returns list of output paths."""
    fig_cfg = cfg.figure
    Path(fig_cfg.output_dir).mkdir(parents=True, exist_ok=True)
    paths = []

    deltas_7b = results.get("deltas_7b", {})
    cis = results.get("cis_7b", {bm: (deltas_7b.get(bm, 0)-0.02, deltas_7b.get(bm, 0)+0.02) for bm in BENCHMARK_ORDER})
    paths.append(plot_7b_delta_by_difficulty(deltas_7b, cis, fig_cfg))

    paths.append(plot_jt_test_result(
        results.get("jt_z_7b", 0.0),
        results.get("jt_p_7b", 1.0),
        results.get("is_monotone_7b", False),
        results.get("violations_7b", []),
        fig_cfg,
    ))

    deltas_1b3 = results.get("deltas_1b3", {bm: float("nan") for bm in BENCHMARK_ORDER})
    paths.append(plot_1b3_delta_by_difficulty(deltas_1b3, fig_cfg))

    paths.append(plot_delta_ratio_gate(
        results.get("delta_ratio_1b3", float("nan")),
        cfg.gate.delta_ratio_min,
        fig_cfg,
    ))

    return paths
