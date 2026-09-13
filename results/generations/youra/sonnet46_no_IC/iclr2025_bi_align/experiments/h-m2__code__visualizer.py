import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path

H_E1_R_PARTIAL: float = 0.9851


def save_all_figures(
    df: pd.DataFrame,
    win_resid: np.ndarray,
    lc_resid: np.ndarray,
    boot_rhos: np.ndarray,
    rho: float,
    ci: tuple,
    fwl_delta: float,
    figures_dir: str,
) -> list:
    """Save 5 figures; return list of absolute file paths."""
    d = Path(figures_dir)
    d.mkdir(parents=True, exist_ok=True)
    return [
        _residuals_scatter(win_resid, lc_resid, rho, str(d / 'fig1_residuals_scatter.png')),
        _residual_distributions(win_resid, lc_resid, str(d / 'fig2_residual_distributions.png')),
        _partial_regression(df, str(d / 'fig3_partial_regression.png')),
        _fwl_consistency(rho, H_E1_R_PARTIAL, fwl_delta, str(d / 'fig4_fwl_consistency.png')),
        _bootstrap_distribution(boot_rhos, ci, str(d / 'fig5_bootstrap_distribution.png')),
    ]


def _residuals_scatter(win_resid: np.ndarray, lc_resid: np.ndarray, rho: float, out_path: str) -> str:
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(win_resid, lc_resid, alpha=0.5, s=20)
    m, b = np.polyfit(win_resid, lc_resid, 1)
    x_line = np.linspace(win_resid.min(), win_resid.max(), 100)
    ax.plot(x_line, m * x_line + b, color='tomato')
    ax.annotate(f"Spearman ρ={rho:.4f}\nN={len(win_resid)}", xy=(0.05, 0.90), xycoords='axes fraction')
    ax.set_xlabel('win_rate residual | avg_length')
    ax.set_ylabel('LC_winrate residual | avg_length')
    ax.set_title('H-M2: Residuals Scatter (FWL Theorem)')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def _residual_distributions(win_resid: np.ndarray, lc_resid: np.ndarray, out_path: str) -> str:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.hist(win_resid, bins=30, color='steelblue', alpha=0.7)
    ax1.set_title('win_rate Residuals')
    ax1.set_xlabel('Residual value')
    ax2.hist(lc_resid, bins=30, color='tomato', alpha=0.7)
    ax2.set_title('LC_winrate Residuals')
    ax2.set_xlabel('Residual value')
    fig.suptitle('H-M2: Residual Distributions')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def _partial_regression(df: pd.DataFrame, out_path: str) -> str:
    X_ctrl = sm.add_constant(df['avg_length'])
    resid_win = sm.OLS(df['win_rate'], X_ctrl).fit().resid
    resid_lc = sm.OLS(df['length_controlled_winrate'], X_ctrl).fit().resid
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(resid_win, resid_lc, alpha=0.5, s=20)
    m, b = np.polyfit(resid_win.values, resid_lc.values, 1)
    x_line = np.linspace(resid_win.min(), resid_win.max(), 100)
    ax.plot(x_line, m * x_line + b, color='tomato')
    ax.set_xlabel('win_rate | avg_length (residuals)')
    ax.set_ylabel('LC_winrate | avg_length (residuals)')
    ax.set_title('H-M2: Partial Regression Plot (Added-Variable)')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def _fwl_consistency(rho: float, h_e1_r_partial: float, fwl_delta: float, out_path: str) -> str:
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(['H-E1 r_partial', 'H-M2 ρ'], [h_e1_r_partial, rho], color=['steelblue', 'tomato'])
    ax.axhspan(h_e1_r_partial - 0.02, h_e1_r_partial + 0.02, alpha=0.15, color='green', label='±0.02 tolerance')
    ax.annotate(f"Δ={fwl_delta:.4f}", xy=(0.5, 0.5), xycoords='axes fraction', ha='center')
    ax.set_ylim(0.9, 1.0)
    ax.set_ylabel('Correlation coefficient')
    ax.set_title('FWL Consistency: H-E1 vs H-M2')
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def _bootstrap_distribution(boot_rhos: np.ndarray, ci: tuple, out_path: str) -> str:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(boot_rhos, bins=40, color='steelblue', alpha=0.7)
    ax.axvline(ci[0], color='tomato', linestyle='--', label=f'95% CI [{ci[0]:.3f}, {ci[1]:.3f}]')
    ax.axvline(ci[1], color='tomato', linestyle='--')
    ax.axvline(0.0, color='black', lw=0.8, label='null ρ=0')
    rho_val = float(np.mean(boot_rhos))
    ax.axvline(rho_val, color='gold', lw=2, label=f'mean ρ≈{rho_val:.4f}')
    ax.set_xlabel('Bootstrap ρ')
    ax.set_ylabel('Count')
    ax.set_title('H-M2: Bootstrap Distribution of Spearman ρ')
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
