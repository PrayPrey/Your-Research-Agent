import os
import numpy as np
import matplotlib.pyplot as plt


def plot_mps_distribution(mps_verbatim: np.ndarray, mps_paraphrase: np.ndarray, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))

    bins = np.linspace(0.5, 1.0, 51)
    ax.hist(mps_verbatim, bins=bins, alpha=0.6, label=f'Verbatim (mean={np.mean(mps_verbatim):.3f})',
            color='steelblue', edgecolor='black', linewidth=0.5)
    ax.hist(mps_paraphrase, bins=bins, alpha=0.6, label=f'Paraphrase (mean={np.mean(mps_paraphrase):.3f})',
            color='coral', edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Mean Paraphrase Similarity (MPS)', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution of Representation Similarity Across Training Conditions', fontsize=14)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mps_distribution.png'), dpi=150)
    plt.close()
    print(f"Saved: {output_dir}/mps_distribution.png")


def plot_mps_boxplot(mps_verbatim: np.ndarray, mps_paraphrase: np.ndarray, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))

    data = [mps_verbatim, mps_paraphrase]
    bp = ax.boxplot(data, patch_artist=True, labels=['Verbatim', 'Paraphrase-Augmented'])

    colors = ['steelblue', 'coral']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ax.set_ylabel('Mean Paraphrase Similarity (MPS)', fontsize=12)
    ax.set_title('Representation Invariance by Training Condition', fontsize=14)
    ax.grid(True, alpha=0.3, axis='y')

    diff = np.mean(mps_paraphrase) - np.mean(mps_verbatim)
    ax.annotate(f'Δ = {diff:.3f}', xy=(1.5, max(np.max(mps_verbatim), np.max(mps_paraphrase))),
                fontsize=11, ha='center')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mps_boxplot.png'), dpi=150)
    plt.close()
    print(f"Saved: {output_dir}/mps_boxplot.png")


def plot_seed_comparison(results_per_seed: list, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))

    seeds = [r["seed"] for r in results_per_seed]
    mps_v = [r["mps_verbatim"] for r in results_per_seed]
    mps_p = [r["mps_paraphrase"] for r in results_per_seed]

    x = np.arange(len(seeds))
    width = 0.35

    ax.bar(x - width/2, mps_v, width, label='Verbatim', color='steelblue', alpha=0.7)
    ax.bar(x + width/2, mps_p, width, label='Paraphrase', color='coral', alpha=0.7)

    ax.set_xlabel('Seed', fontsize=12)
    ax.set_ylabel('Mean Paraphrase Similarity', fontsize=12)
    ax.set_title('MPS Comparison Across Seeds', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([str(s) for s in seeds])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'seed_comparison.png'), dpi=150)
    plt.close()
    print(f"Saved: {output_dir}/seed_comparison.png")
