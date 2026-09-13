from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import scipy.stats


def save_all_figures(df, ols_result: dict, vif: dict, gate_result: dict, figures_dir: str) -> list:
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    paths = [
        _dominance_bar(ols_result, figures_dir),
        _coef_plot(ols_result, figures_dir),
        _vif_bar(vif, figures_dir),
        _residuals_vs_fitted(ols_result, figures_dir),
        _qq_plot(ols_result, figures_dir),
        _scatter_by_length_quartile(df, figures_dir),
    ]
    assert len(paths) == 6
    return paths


def _dominance_bar(ols_result: dict, figures_dir: str) -> str:
    labels = ['|β_win_rate_std|', '|β_avg_length_std|']
    values = [abs(ols_result['beta_win']), abs(ols_result['beta_len'])]
    colors = ['steelblue', 'tomato']
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=colors, alpha=0.8)
    y_offset = max(values) * 0.03
    ax.text(0, values[0] + y_offset, f"p={ols_result['p_win']:.2e}", ha='center', fontsize=9)
    ax.text(1, values[1] + y_offset, f"p={ols_result['p_len']:.2e}", ha='center', fontsize=9)
    ax.set_ylabel('|Standardized Coefficient|')
    ax.set_title('Dominance: Capability vs Verbosity (OLS β)')
    ax.set_ylim(0, max(values) * 1.2)
    path = Path(figures_dir) / 'fig1_dominance_bar.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)


def _coef_plot(ols_result: dict, figures_dir: str) -> str:
    model = ols_result['_model']
    params = model.params[['win_rate_std', 'avg_length_std']]
    ci = model.conf_int().loc[['win_rate_std', 'avg_length_std']]
    xerr_lo = params.values - ci[0].values
    xerr_hi = ci[1].values - params.values
    fig, ax = plt.subplots(figsize=(7, 4))
    y_pos = [1, 0]
    ax.barh(y_pos, params.values, xerr=[xerr_lo, xerr_hi], align='center', alpha=0.8,
            color=['steelblue', 'tomato'])
    ax.axvline(0, color='gray', lw=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(['win_rate_std', 'avg_length_std'])
    ax.set_xlabel('Standardized Coefficient (95% CI)')
    ax.set_title('OLS Coefficient Plot')
    path = Path(figures_dir) / 'fig2_coef_plot.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)


def _vif_bar(vif: dict, figures_dir: str) -> str:
    labels = ['win_rate_std', 'avg_length_std']
    values = [vif['win_rate'], vif['avg_length']]
    colors = ['tomato' if v >= 5.0 else 'steelblue' for v in values]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=colors, alpha=0.8)
    ax.axhline(5.0, color='red', linestyle='--', lw=1.5, label='VIF=5.0 threshold')
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    ax.legend(fontsize=9)
    ax.set_ylabel('VIF')
    ax.set_title('Variance Inflation Factor (Standardized Predictors)')
    path = Path(figures_dir) / 'fig3_vif_bar.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)


def _residuals_vs_fitted(ols_result: dict, figures_dir: str) -> str:
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(ols_result['fitted'], ols_result['residuals'], alpha=0.5, s=20, color='steelblue')
    ax.axhline(0, color='red', linestyle='--', lw=1)
    ax.set_xlabel('Fitted Values')
    ax.set_ylabel('Residuals')
    ax.set_title('OLS Residuals vs Fitted')
    path = Path(figures_dir) / 'fig4_residuals_vs_fitted.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)


def _qq_plot(ols_result: dict, figures_dir: str) -> str:
    fig, ax = plt.subplots(figsize=(6, 5))
    scipy.stats.probplot(ols_result['residuals'], dist='norm', plot=ax)
    ax.set_title('Q-Q Plot of OLS Residuals')
    path = Path(figures_dir) / 'fig5_qq_plot.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)


def _scatter_by_length_quartile(df, figures_dir: str) -> str:
    quartiles = df['avg_length'].quantile([0.25, 0.5, 0.75])
    colors = []
    for v in df['avg_length']:
        if v <= quartiles[0.25]:
            colors.append('steelblue')
        elif v <= quartiles[0.5]:
            colors.append('mediumseagreen')
        elif v <= quartiles[0.75]:
            colors.append('orange')
        else:
            colors.append('tomato')
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(df['win_rate_std'], df['length_controlled_winrate'],
               c=colors, alpha=0.6, s=20)
    ax.set_xlabel('win_rate_std')
    ax.set_ylabel('LC_winrate')
    ax.set_title('win_rate_std vs LC_winrate (color = avg_length quartile)')
    legend = [
        mpatches.Patch(color='steelblue', label='Q1 (shortest)'),
        mpatches.Patch(color='mediumseagreen', label='Q2'),
        mpatches.Patch(color='orange', label='Q3'),
        mpatches.Patch(color='tomato', label='Q4 (longest)'),
    ]
    ax.legend(handles=legend, fontsize=8)
    path = Path(figures_dir) / 'fig6_scatter_by_length_quartile.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)
