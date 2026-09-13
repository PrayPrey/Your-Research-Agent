"""H-M2: 5 research figures."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

FIGURES_DIR: str = "figures"
C0_R2: float = 0.984


def _ensure_dir():
    os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_mse_decomposition(mse_total: float, mse_perm: float, mse_res: float, ratio: float) -> None:
    """Figure 1 (MANDATORY): bar chart MSE_perm / MSE_res / MSE_total + 10% threshold line."""
    _ensure_dir()
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Left: stacked bar of MSE components
    ax = axes[0]
    components = [mse_perm, max(mse_res, 0.0)]
    labels = ['MSE_perm\n(orbit variance)', 'MSE_res\n(residual)']
    colors = ['#e74c3c', '#3498db']
    bottom = 0.0
    bars = []
    for val, lbl, col in zip(components, labels, colors):
        b = ax.bar(0, val, bottom=bottom, color=col, label=lbl, width=0.4)
        bars.append(b)
        bottom += val
    ax.axhline(mse_total * 0.10, color='orange', linestyle='--', lw=2, label='10% threshold')
    ax.set_xticks([])
    ax.set_ylabel('MSE')
    ax.set_title('MSE Decomposition')
    ax.legend(loc='upper right', fontsize=8)
    ax.set_xlim(-0.5, 0.5)

    # Right: ratio bar
    ax2 = axes[1]
    color = '#e74c3c' if ratio >= 0.10 else '#95a5a6'
    ax2.bar(['MSE_perm / MSE_total'], [ratio], color=color, width=0.4)
    ax2.axhline(0.10, color='orange', linestyle='--', lw=2, label='Gate: 0.10')
    ax2.set_ylim(0, max(ratio * 1.3, 0.15))
    ax2.set_ylabel('Ratio')
    ax2.set_title(f'Ratio = {ratio:.4f}  [Gate: ≥0.10 {"✓" if ratio >= 0.10 else "✗"}]')
    ax2.legend(fontsize=8)

    plt.suptitle('H-M2: OrbitVar Propagation to Prediction Space', fontsize=12)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig1_mse_decomposition.png'), dpi=150)
    plt.close(fig)
    print(f"Figure 1 saved: {FIGURES_DIR}/fig1_mse_decomposition.png")


def plot_orbit_var_histogram(per_model_orbit_var: np.ndarray) -> None:
    """Figure 2: histogram of Var_k(ŷ(π_k·W_v)) across 100 models."""
    _ensure_dir()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(per_model_orbit_var, bins=20, color='#3498db', edgecolor='white', alpha=0.8)
    ax.axvline(float(np.mean(per_model_orbit_var)), color='red', lw=2,
               linestyle='--', label=f'Mean = {np.mean(per_model_orbit_var):.4f}')
    ax.set_xlabel('Var_k(ŷ) per model')
    ax.set_ylabel('Count')
    ax.set_title('H-M2: Per-Model Prediction Orbit Variance Distribution')
    ax.legend(fontsize=9)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig2_orbit_var_histogram.png'), dpi=150)
    plt.close(fig)
    print(f"Figure 2 saved: {FIGURES_DIR}/fig2_orbit_var_histogram.png")


def plot_r2_comparison(r2_c1: float, r2_c1_avg: float, r2_c0: float = C0_R2) -> None:
    """Figure 3: bar chart R²(C0), R²(C1), R²(C1_avg)."""
    _ensure_dir()
    fig, ax = plt.subplots(figsize=(7, 5))
    names = ['C0\n(weight stats)', 'C1\n(CISE OOF)', 'C1_avg\n(orbit avg)']
    values = [r2_c0, r2_c1, r2_c1_avg]
    colors = ['#95a5a6', '#e74c3c', '#e67e22']
    bars = ax.bar(names, values, color=colors, edgecolor='white', width=0.5)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel('R²')
    ax.set_title('H-M2: R² Comparison (C0 vs C1 vs C1_avg)')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig3_r2_comparison.png'), dpi=150)
    plt.close(fig)
    print(f"Figure 3 saved: {FIGURES_DIR}/fig3_r2_comparison.png")


def plot_orbitvar_vs_pred_var(embed_orbit_vars: list, pred_orbit_vars: np.ndarray) -> None:
    """Figure 4: scatter OrbitVar(embed) vs Var_k(ŷ) per model."""
    _ensure_dir()
    x = np.array(embed_orbit_vars, dtype=np.float64)
    y = np.array(pred_orbit_vars, dtype=np.float64)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(x, y, alpha=0.6, s=30, color='#3498db', edgecolors='none')
    ax.set_xlabel('OrbitVar(embed) — H-M1')
    ax.set_ylabel('Var_k(ŷ) — H-M2')
    ax.set_title('H-M2: Embedding OrbitVar vs Prediction Orbit Variance')
    # Add correlation annotation
    if np.std(x) > 0 and np.std(y) > 0:
        corr = float(np.corrcoef(x, y)[0, 1])
        ax.annotate(f'r = {corr:.3f}', xy=(0.05, 0.92), xycoords='axes fraction', fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig4_orbitvar_vs_predvar.png'), dpi=150)
    plt.close(fig)
    print(f"Figure 4 saved: {FIGURES_DIR}/fig4_orbitvar_vs_predvar.png")


def plot_orbit_fan(orbit_preds: np.ndarray, model_indices: list = None) -> None:
    """Figure 5: violin plot of K=50 orbit predictions for 5 representative models."""
    _ensure_dir()
    N, K = orbit_preds.shape
    if model_indices is None:
        # Pick 5 spread evenly across the sorted per-model variance
        per_var = np.var(orbit_preds, axis=1)
        sorted_idx = np.argsort(per_var)
        model_indices = [sorted_idx[int(i * N / 5)] for i in range(5)]

    fig, ax = plt.subplots(figsize=(9, 5))
    data = [orbit_preds[i, :] for i in model_indices]
    positions = list(range(1, len(model_indices) + 1))
    vp = ax.violinplot(data, positions=positions, showmedians=True)
    for pc in vp['bodies']:
        pc.set_facecolor('#3498db')
        pc.set_alpha(0.7)
    ax.set_xticks(positions)
    ax.set_xticklabels([f'M{i}' for i in model_indices], fontsize=9)
    ax.set_xlabel('Model index')
    ax.set_ylabel('Prediction ŷ(π_k · W_v)')
    ax.set_title('H-M2: Orbit Fan — K=50 Permuted Predictions per Model')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig5_orbit_fan.png'), dpi=150)
    plt.close(fig)
    print(f"Figure 5 saved: {FIGURES_DIR}/fig5_orbit_fan.png")
