"""Visualization for H-C1"""
import numpy as np
import matplotlib.pyplot as plt
import os


def plot_ifr_boxplot(ifr_contaminated: np.ndarray, ifr_non_contaminated: np.ndarray,
                     pvalue: float, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    data = [ifr_contaminated, ifr_non_contaminated]
    bp = ax.boxplot(data, labels=['Contaminated', 'Non-contaminated'], patch_artist=True)
    bp['boxes'][0].set_facecolor('#ff6b6b')
    bp['boxes'][1].set_facecolor('#4ecdc4')

    ax.set_ylabel('IFR (Influence Fragility Ratio)')
    ax.set_title(f'IFR Distribution by Contamination Status\n(Mann-Whitney U p={pvalue:.4f})')

    sig_marker = '***' if pvalue < 0.001 else ('**' if pvalue < 0.01 else ('*' if pvalue < 0.05 else 'n.s.'))
    y_max = max(np.percentile(ifr_contaminated, 95), np.percentile(ifr_non_contaminated, 95))
    ax.annotate(sig_marker, xy=(1.5, y_max * 1.05), ha='center', fontsize=14)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_ifr_redundancy_scatter(ifr: np.ndarray, redundancy: np.ndarray,
                                 rho: float, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    sample_idx = np.random.choice(len(ifr), min(2000, len(ifr)), replace=False)
    ax.scatter(redundancy[sample_idx], ifr[sample_idx], alpha=0.3, s=10)

    z = np.polyfit(redundancy, ifr, 1)
    p = np.poly1d(z)
    x_line = np.linspace(redundancy.min(), redundancy.max(), 100)
    ax.plot(x_line, p(x_line), 'r-', linewidth=2, label=f'ρ = {rho:.3f}')

    ax.set_xlabel('Redundancy')
    ax.set_ylabel('IFR')
    ax.set_title(f'IFR vs Redundancy (Spearman ρ = {rho:.3f})')
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_redundancy_by_contamination(redundancy: np.ndarray, contaminated_mask: np.ndarray,
                                      out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.hist(redundancy[contaminated_mask], bins=50, alpha=0.5, label='Contaminated', color='#ff6b6b')
    ax.hist(redundancy[~contaminated_mask], bins=50, alpha=0.5, label='Non-contaminated', color='#4ecdc4')

    ax.set_xlabel('Redundancy')
    ax.set_ylabel('Count')
    ax.set_title('Redundancy Distribution by Contamination Status')
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_trak_by_contamination(trak_scores: np.ndarray, contaminated_mask: np.ndarray,
                                out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.hist(np.abs(trak_scores[contaminated_mask]), bins=50, alpha=0.5, label='Contaminated', color='#ff6b6b')
    ax.hist(np.abs(trak_scores[~contaminated_mask]), bins=50, alpha=0.5, label='Non-contaminated', color='#4ecdc4')

    ax.set_xlabel('|TRAK Score|')
    ax.set_ylabel('Count')
    ax.set_title('TRAK Score Distribution by Contamination Status')
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
