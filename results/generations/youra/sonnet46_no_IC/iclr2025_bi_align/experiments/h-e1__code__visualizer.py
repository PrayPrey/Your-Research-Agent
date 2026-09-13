from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.stats
import statsmodels.api as sm


def save_all_figures(df, boot_rs, vif, corr_result, output_dir) -> list:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    paths = []
    paths.append(_scatter_winrate_lc(df, output_dir))
    paths.append(_partial_regression(df, corr_result, output_dir))
    paths.append(_bootstrap_distribution(boot_rs, corr_result, output_dir))
    paths.append(_vif_diagnostic(vif, output_dir))
    paths.append(_delta_scatter(df, output_dir))
    return paths


def _scatter_winrate_lc(df, output_dir) -> str:
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
    ax.scatter(df['win_rate'], df['length_controlled_winrate'], c=colors, alpha=0.6, s=20)
    ax.set_xlabel('win_rate')
    ax.set_ylabel('LC_winrate')
    ax.set_title('win_rate vs LC_winrate (color = avg_length quartile)')
    import matplotlib.patches as mpatches
    legend = [
        mpatches.Patch(color='steelblue', label='Q1 (shortest)'),
        mpatches.Patch(color='mediumseagreen', label='Q2'),
        mpatches.Patch(color='orange', label='Q3'),
        mpatches.Patch(color='tomato', label='Q4 (longest)'),
    ]
    ax.legend(handles=legend, fontsize=8)
    path = Path(output_dir) / 'fig1_scatter_winrate_lc.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)


def _partial_regression(df, corr_result, output_dir) -> str:
    X_ctrl = sm.add_constant(df['avg_length'])
    resid_win = sm.OLS(df['win_rate'], X_ctrl).fit().resid
    resid_lc = sm.OLS(df['length_controlled_winrate'], X_ctrl).fit().resid

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(resid_win, resid_lc, alpha=0.5, s=20, color='steelblue')
    m, b = np.polyfit(resid_win, resid_lc, deg=1)
    x_line = np.linspace(resid_win.min(), resid_win.max(), 200)
    ax.plot(x_line, m * x_line + b, color='tomato', lw=1.5,
            label=f"r={corr_result['r_partial']:.3f}, p={corr_result['p_val']:.4f}")
    ax.legend(fontsize=9)
    ax.set_xlabel('win_rate residual (partialled on avg_length)')
    ax.set_ylabel('LC_winrate residual (partialled on avg_length)')
    ax.set_title('Partial Regression: win_rate → LC_winrate | avg_length')
    path = Path(output_dir) / 'fig2_partial_regression.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)


def _bootstrap_distribution(boot_rs, corr_result, output_dir) -> str:
    arr = np.array(boot_rs)
    ci_lower = np.percentile(arr, 2.5)
    ci_upper = np.percentile(arr, 97.5)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(arr, bins=40, color='steelblue', alpha=0.7, edgecolor='white')
    ax.axvline(ci_lower, color='tomato', linestyle='--', lw=1.5, label=f'95% CI [{ci_lower:.3f}, {ci_upper:.3f}]')
    ax.axvline(ci_upper, color='tomato', linestyle='--', lw=1.5)
    ax.axvline(corr_result['r_partial'], color='gold', lw=2, label=f"r_partial={corr_result['r_partial']:.3f}")
    ax.set_xlabel('Bootstrap r_partial')
    ax.set_ylabel('Count')
    ax.set_title('Bootstrap Distribution of Spearman Partial r (1000 resamples)')
    ax.legend(fontsize=9)
    path = Path(output_dir) / 'fig3_bootstrap_distribution.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)


def _vif_diagnostic(vif, output_dir) -> str:
    labels = ['win_rate', 'avg_length']
    values = [vif['win_rate'], vif['avg_length']]
    colors = ['tomato' if v >= 5.0 else 'steelblue' for v in values]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=colors, alpha=0.8)
    ax.axhline(5.0, color='red', linestyle='--', lw=1.5, label='VIF=5.0 threshold')
    ax.set_ylabel('VIF')
    ax.set_title('Variance Inflation Factor Diagnostic')
    ax.legend(fontsize=9)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, f'{val:.2f}', ha='center', va='bottom')
    path = Path(output_dir) / 'fig4_vif_diagnostic.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)


def _delta_scatter(df, output_dir) -> str:
    delta = df['length_controlled_winrate'] - df['win_rate']
    x = df['win_rate']
    slope, intercept, r_val, p_val, se = scipy.stats.linregress(x, delta)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(x, delta, alpha=0.5, s=20, color='mediumpurple')
    ax.axhline(0, color='gray', lw=0.8, linestyle='--')
    x_line = np.linspace(x.min(), x.max(), 200)
    ax.plot(x_line, slope * x_line + intercept, color='tomato', lw=1.5,
            label=f'r={r_val:.3f}, p={p_val:.3f}')
    ax.legend(fontsize=9)
    ax.set_xlabel('win_rate')
    ax.set_ylabel('Δ = LC_winrate − win_rate')
    ax.set_title('Length-Control Delta vs Win Rate')
    path = Path(output_dir) / 'fig5_delta_scatter.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return str(path)
