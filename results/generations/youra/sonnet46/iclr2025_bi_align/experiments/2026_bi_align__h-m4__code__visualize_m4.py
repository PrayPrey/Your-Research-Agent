"""
visualize_m4.py - 6 visualization functions for h-m4 regression results.

Figures:
  1. beta_PM comparison (full model) with 95% CI across 3 SBERT models
  2. Mediation decomposition: beta_PM_reduced vs beta_PM_full
  3. Coefficient forest plot with all OLS coefficients
  4. C_sem vs PM_proxy scatter per tier
  5. Partial regression plot
  6. Tier x branch grouped bar chart
"""
import os
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from typing import Dict

from regression import MediationResult

logger = logging.getLogger(__name__)

TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
TIER_PALETTE = {
    "helpful-base": "#4C72B0",
    "helpful-rejection-sampled": "#DD8452",
    "helpful-online": "#55A868",
}
BRANCH_PALETTE = {
    "chosen": "#2196F3",
    "rejected": "#F44336",
}


def _ensure_figures_dir(figures_dir: str) -> None:
    os.makedirs(figures_dir, exist_ok=True)


def plot_beta_pm_comparison(
    mediation_results: Dict[str, MediationResult],
    figures_dir: str,
) -> str:
    """Fig 1: beta_PM (full model) with 95% CI across 3 SBERT models (bar + error bars)."""
    _ensure_figures_dir(figures_dir)

    model_names = list(mediation_results.keys())
    betas = [mediation_results[m].beta_pm_full for m in model_names]
    ci_lower = [mediation_results[m].stage_full.beta_pm_ci[0] for m in model_names]
    ci_upper = [mediation_results[m].stage_full.beta_pm_ci[1] for m in model_names]

    short_labels = [m.replace('all-', '').replace('-v2', '').replace('-L6', '') for m in model_names]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(model_names))
    colors = ['#4C72B0', '#DD8452', '#55A868'][:len(model_names)]

    ax.bar(x, betas, color=colors, alpha=0.7)
    yerr_lower = [b - lo for b, lo in zip(betas, ci_lower)]
    yerr_upper = [hi - b for b, hi in zip(betas, ci_upper)]
    ax.errorbar(x, betas, yerr=[yerr_lower, yerr_upper], fmt='none', color='black', capsize=5)

    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=20, ha='right')
    ax.set_xlabel("SBERT Model")
    ax.set_ylabel(r"$\hat{\beta}_{PM}$ (Full Model)")
    ax.set_title("H-M4: PM-Proxy Effect on C_sem (Full Model with Surface Controls)")
    plt.tight_layout()

    save_path = os.path.join(figures_dir, "fig1_beta_pm_comparison.png")
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info(f"Fig 1 saved: {save_path}")
    return save_path


def plot_mediation_decomposition(
    mediation_results: Dict[str, MediationResult],
    figures_dir: str,
) -> str:
    """Fig 2: beta_PM_reduced vs beta_PM_full per model (grouped bar)."""
    _ensure_figures_dir(figures_dir)

    model_names = list(mediation_results.keys())
    short_labels = [m.replace('all-', '').replace('-v2', '').replace('-L6', '') for m in model_names]

    beta_reduced = [mediation_results[m].beta_pm_reduced for m in model_names]
    beta_full = [mediation_results[m].beta_pm_full for m in model_names]

    x = np.arange(len(model_names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, beta_reduced, width, label='PM-only (Stage 1)', color='#4C72B0', alpha=0.7)
    ax.bar(x + width/2, beta_full, width, label='Full Model (Stage 2)', color='#DD8452', alpha=0.7)

    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=20, ha='right')
    ax.set_xlabel("SBERT Model")
    ax.set_ylabel(r"$\hat{\beta}_{PM}$")
    ax.set_title("H-M4: Mediation Decomposition — PM Effect Before/After Controls")
    ax.legend()
    plt.tight_layout()

    save_path = os.path.join(figures_dir, "fig2_mediation_decomposition.png")
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info(f"Fig 2 saved: {save_path}")
    return save_path


def plot_coefficient_forest(
    mediation_results: Dict[str, MediationResult],
    figures_dir: str,
) -> str:
    """Fig 3: All OLS coefficients with 95% CI per model (forest plot)."""
    _ensure_figures_dir(figures_dir)

    model_names = list(mediation_results.keys())
    if not model_names:
        return ""

    model_name = model_names[0]
    stage2 = mediation_results[model_name].stage_full

    params = stage2.all_params
    cis = stage2.all_ci

    coef_names = [k for k in params.keys() if k != 'const']
    coef_vals = [params[k] for k in coef_names]
    ci_lo = [cis[k][0] if k in cis else float('nan') for k in coef_names]
    ci_hi = [cis[k][1] if k in cis else float('nan') for k in coef_names]

    fig, ax = plt.subplots(figsize=(10, 7))
    y = np.arange(len(coef_names))

    ax.scatter(coef_vals, y, zorder=3, color='steelblue', s=50)
    for i, (lo, hi) in enumerate(zip(ci_lo, ci_hi)):
        if not (np.isnan(lo) or np.isnan(hi)):
            ax.plot([lo, hi], [i, i], color='steelblue', linewidth=1.5, alpha=0.7)

    ax.axvline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(coef_names)
    ax.set_xlabel("Coefficient Value (95% CI)")
    ax.set_title(f"H-M4: Forest Plot — Full Model Coefficients\n({model_name})")
    plt.tight_layout()

    save_path = os.path.join(figures_dir, "fig3_coefficient_forest.png")
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info(f"Fig 3 saved: {save_path}")
    return save_path


def plot_csem_vs_pm_scatter(
    df: pd.DataFrame,
    figures_dir: str,
) -> str:
    """Fig 4: C_sem vs PM_proxy per tier with mean markers per PM value."""
    _ensure_figures_dir(figures_dir)

    fig, ax = plt.subplots(figsize=(8, 5))

    rng = np.random.default_rng(42)
    for tier in TIER_ORDER:
        tier_df = df[df['tier'] == tier]
        if len(tier_df) == 0:
            continue
        color = TIER_PALETTE.get(tier, 'gray')
        jitter = rng.uniform(-0.05, 0.05, size=len(tier_df))
        ax.scatter(
            tier_df['pm_proxy'].values + jitter,
            tier_df['c_sem'].values,
            color=color, alpha=0.15, s=4, label=tier
        )
        for pm_val in [0, 1]:
            sub = tier_df[tier_df['pm_proxy'] == pm_val]['c_sem']
            if len(sub) > 0:
                ax.scatter(pm_val, sub.mean(), color=color, s=80, marker='D', zorder=5)

    ax.set_xlabel("PM Proxy (1=chosen, 0=rejected)")
    ax.set_ylabel(r"$C_{sem}^{H \leftarrow A}$")
    ax.set_title("H-M4: C_sem vs PM_proxy per Tier")
    ax.legend(loc='upper left', fontsize=8)
    plt.tight_layout()

    save_path = os.path.join(figures_dir, "fig4_csem_vs_pm_scatter.png")
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info(f"Fig 4 saved: {save_path}")
    return save_path


def plot_partial_regression(
    df: pd.DataFrame,
    mediation_results: Dict[str, MediationResult],
    figures_dir: str,
) -> str:
    """Fig 5: C_sem residuals vs PM_proxy residuals (partial regression)."""
    _ensure_figures_dir(figures_dir)

    try:
        import statsmodels.api as sm

        controls = ['response_length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len']
        tier_dummies = pd.get_dummies(df['tier'], prefix='tier', drop_first=True).astype(float)

        X_ctrl = sm.add_constant(pd.concat([df[controls], tier_dummies], axis=1))
        y_resid = sm.OLS(df['c_sem'], X_ctrl).fit().resid
        pm_resid = sm.OLS(df['pm_proxy'].astype(float), X_ctrl).fit().resid

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(pm_resid, y_resid, alpha=0.15, s=4, color='steelblue')

        X_fit = sm.add_constant(pm_resid)
        fit = sm.OLS(y_resid, X_fit).fit()
        x_line = np.linspace(pm_resid.min(), pm_resid.max(), 100)
        ax.plot(x_line, fit.params[0] + fit.params[1] * x_line, color='red', linewidth=2)

        ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
        ax.axvline(0, color='gray', linestyle='--', linewidth=0.8)
        ax.set_xlabel("PM_proxy Residuals (after controls)")
        ax.set_ylabel(r"$C_{sem}$ Residuals (after controls)")
        ax.set_title("H-M4: Partial Regression Plot — PM_proxy Effect on C_sem")
        plt.tight_layout()

    except Exception as e:
        logger.warning(f"Partial regression plot failed: {e}")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, f"Plot unavailable:\n{e}", ha='center', va='center', transform=ax.transAxes)

    save_path = os.path.join(figures_dir, "fig5_partial_regression.png")
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info(f"Fig 5 saved: {save_path}")
    return save_path


def plot_tier_pm_interaction(
    df: pd.DataFrame,
    figures_dir: str,
) -> str:
    """Fig 6: C_sem by tier x branch (chosen/rejected) grouped bar chart."""
    _ensure_figures_dir(figures_dir)

    tiers = TIER_ORDER
    branches = ['chosen', 'rejected']
    x = np.arange(len(tiers))
    width = 0.35

    means = {}
    sems = {}
    for branch in branches:
        means[branch] = []
        sems[branch] = []
        for tier in tiers:
            sub = df[(df['tier'] == tier) & (df['branch'] == branch)]['c_sem']
            if len(sub) > 0:
                means[branch].append(float(sub.mean()))
                sems[branch].append(float(sub.sem()))
            else:
                means[branch].append(0.0)
                sems[branch].append(0.0)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width/2, means['chosen'], width, yerr=sems['chosen'],
           label='Chosen (PM=1)', color=BRANCH_PALETTE['chosen'], alpha=0.7, capsize=4)
    ax.bar(x + width/2, means['rejected'], width, yerr=sems['rejected'],
           label='Rejected (PM=0)', color=BRANCH_PALETTE['rejected'], alpha=0.7, capsize=4)

    short_tiers = [t.replace('helpful-', '').replace('-', '\n') for t in tiers]
    ax.set_xticks(x)
    ax.set_xticklabels(short_tiers)
    ax.set_xlabel("RLHF Tier")
    ax.set_ylabel(r"Mean $C_{sem}^{H \leftarrow A}$")
    ax.set_title("H-M4: C_sem by Tier x Branch (Chosen vs Rejected)")
    ax.legend()
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.tight_layout()

    save_path = os.path.join(figures_dir, "fig6_tier_pm_interaction.png")
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info(f"Fig 6 saved: {save_path}")
    return save_path


def generate_all_figures(
    mediation_results: Dict[str, MediationResult],
    df: pd.DataFrame,
    figures_dir: str,
) -> Dict[str, str]:
    """Run all 6 figure generators. Returns dict of {fig_name: saved_path}."""
    figure_paths = {}

    generators = [
        ('fig1_beta_pm_comparison', lambda: plot_beta_pm_comparison(mediation_results, figures_dir)),
        ('fig2_mediation_decomposition', lambda: plot_mediation_decomposition(mediation_results, figures_dir)),
        ('fig3_coefficient_forest', lambda: plot_coefficient_forest(mediation_results, figures_dir)),
    ]

    if df is not None and len(df) > 0:
        generators += [
            ('fig4_csem_vs_pm_scatter', lambda: plot_csem_vs_pm_scatter(df, figures_dir)),
            ('fig5_partial_regression', lambda: plot_partial_regression(df, mediation_results, figures_dir)),
            ('fig6_tier_pm_interaction', lambda: plot_tier_pm_interaction(df, figures_dir)),
        ]

    for name, gen_fn in generators:
        try:
            figure_paths[name] = gen_fn()
        except Exception as e:
            logger.error(f"{name} failed: {e}")

    logger.info(f"Generated {len(figure_paths)}/6 figures in {figures_dir}")
    return figure_paths
