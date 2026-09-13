"""H-M3: Orthogonality verification between entropy and consistency signals.

Tests whether token entropy (H-M1) and n-sample consistency (H-M2) capture
orthogonal uncertainty signals with differential predictive value.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, rankdata
from sklearn.metrics import roc_auc_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yaml


@dataclass
class PathsConfig:
    h_m1_results: str = "../h-m1/results/entropy_scores.json"
    h_m2_results: str = "../h-m2/results/consistency_scores.json"
    output_dir: str = "results/"
    figures_dir: str = "results/figures/"
    correlation_output: str = "results/correlation_analysis.json"
    discordant_output: str = "results/discordant_cases.csv"
    subset_auroc_output: str = "results/subset_auroc.json"
    scatter_plot: str = "results/figures/scatter_entropy_consistency.png"
    quadrant_plot: str = "results/figures/quadrant_analysis.png"


@dataclass
class ThresholdsConfig:
    correlation_threshold: float = 0.3
    discordant_rank_diff: float = 0.5
    discordant_proportion_threshold: float = 0.15
    subset_auroc_threshold: float = 0.6
    min_subset_size: int = 50


@dataclass
class HM3Config:
    paths: PathsConfig = field(default_factory=PathsConfig)
    thresholds: ThresholdsConfig = field(default_factory=ThresholdsConfig)
    seed: int = 42
    n_questions: int = 817

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "HM3Config":
        with open(path) as f:
            raw = yaml.safe_load(f)
        return cls(
            paths=PathsConfig(**raw.get("paths", {})),
            thresholds=ThresholdsConfig(**raw.get("thresholds", {})),
            seed=raw.get("seed", 42),
            n_questions=raw.get("n_questions", 817),
        )


def load_scores(h_m1_path: str, h_m2_path: str) -> tuple:
    """Load entropy and consistency scores from H-M1 and H-M2 results."""
    with open(h_m1_path) as f:
        m1 = json.load(f)
    with open(h_m2_path) as f:
        m2 = json.load(f)

    entropy = np.array(m1['entropy_scores'])
    consistency = np.array(m2['consistency_scores'])
    labels = np.array(m1['labels'])

    return entropy, consistency, labels


def compute_correlation(entropy: np.ndarray, consistency: np.ndarray) -> dict:
    """Compute Pearson and Spearman correlation between entropy and (1-consistency)."""
    inv_consistency = 1 - consistency

    r_pearson, p_pearson = pearsonr(entropy, inv_consistency)
    r_spearman, p_spearman = spearmanr(entropy, inv_consistency)

    return {
        'pearson_r': float(r_pearson),
        'pearson_p': float(p_pearson),
        'spearman_r': float(r_spearman),
        'spearman_p': float(p_spearman),
    }


def identify_discordant(entropy: np.ndarray, consistency: np.ndarray,
                        rank_diff_threshold: float = 0.5) -> dict:
    """Identify discordant cases where methods disagree on suspicion ranking."""
    n = len(entropy)

    e_rank = rankdata(entropy) / n
    c_rank_inv = 1 - rankdata(consistency) / n

    rank_diff = np.abs(e_rank - c_rank_inv)
    discordant = rank_diff > rank_diff_threshold

    high_entropy_only = discordant & (e_rank > c_rank_inv)
    high_inconsistency_only = discordant & (c_rank_inv > e_rank)

    return {
        'discordant_mask': discordant,
        'high_entropy_only': high_entropy_only,
        'high_inconsistency_only': high_inconsistency_only,
        'discordant_proportion': float(discordant.sum() / n),
        'n_discordant': int(discordant.sum()),
        'n_high_entropy_only': int(high_entropy_only.sum()),
        'n_high_inconsistency_only': int(high_inconsistency_only.sum()),
    }


def compute_subset_auroc(entropy: np.ndarray, consistency: np.ndarray,
                          labels: np.ndarray, disc: dict,
                          min_subset_size: int = 50) -> dict:
    """Compute AUROC on discordant subsets to verify differential predictive value."""
    results = {}

    mask_e = disc['high_entropy_only']
    if mask_e.sum() >= min_subset_size:
        subset_labels = labels[mask_e]
        if len(np.unique(subset_labels)) > 1:
            results['auroc_entropy_subset'] = float(roc_auc_score(
                subset_labels, -entropy[mask_e]
            ))
            results['n_entropy_subset'] = int(mask_e.sum())

    mask_c = disc['high_inconsistency_only']
    if mask_c.sum() >= min_subset_size:
        subset_labels = labels[mask_c]
        if len(np.unique(subset_labels)) > 1:
            results['auroc_consistency_subset'] = float(roc_auc_score(
                subset_labels, consistency[mask_c]
            ))
            results['n_consistency_subset'] = int(mask_c.sum())

    return results


def plot_scatter(entropy: np.ndarray, consistency: np.ndarray,
                 labels: np.ndarray, output_path: str) -> None:
    """Scatter plot of entropy vs (1-consistency) colored by correctness."""
    plt.figure(figsize=(10, 8))

    correct = labels.astype(bool)
    plt.scatter(entropy[correct], 1 - consistency[correct],
                c='green', alpha=0.5, s=20, label='Correct')
    plt.scatter(entropy[~correct], 1 - consistency[~correct],
                c='red', alpha=0.5, s=20, label='Incorrect')

    z = np.polyfit(entropy, 1 - consistency, 1)
    p = np.poly1d(z)
    x_line = np.linspace(entropy.min(), entropy.max(), 100)
    plt.plot(x_line, p(x_line), 'b--', alpha=0.7, label=f'Linear fit')

    r, _ = pearsonr(entropy, 1 - consistency)
    plt.title(f'Entropy vs Inconsistency (r = {r:.3f})')
    plt.xlabel('Token Entropy (higher = more uncertain)')
    plt.ylabel('1 - Consistency (higher = more unstable)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_quadrant(entropy: np.ndarray, consistency: np.ndarray,
                  labels: np.ndarray, output_path: str) -> None:
    """Quadrant plot with median splits on both axes."""
    plt.figure(figsize=(10, 8))

    e_med = np.median(entropy)
    c_med = np.median(1 - consistency)

    correct = labels.astype(bool)
    plt.scatter(entropy[correct], 1 - consistency[correct],
                c='green', alpha=0.5, s=20, label='Correct')
    plt.scatter(entropy[~correct], 1 - consistency[~correct],
                c='red', alpha=0.5, s=20, label='Incorrect')

    plt.axvline(x=e_med, color='gray', linestyle='--', alpha=0.7)
    plt.axhline(y=c_med, color='gray', linestyle='--', alpha=0.7)

    q_labels = ['Low E, Low I', 'High E, Low I', 'Low E, High I', 'High E, High I']
    positions = [(e_med*0.3, c_med*0.3), (e_med*1.7, c_med*0.3),
                 (e_med*0.3, c_med*1.7), (e_med*1.7, c_med*1.7)]
    for txt, pos in zip(q_labels, positions):
        plt.text(pos[0], pos[1], txt, fontsize=9, alpha=0.7)

    plt.title('Quadrant Analysis: Entropy vs Inconsistency')
    plt.xlabel('Token Entropy')
    plt.ylabel('1 - Consistency')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def save_discordant_csv(disc: dict, n: int, output_path: str) -> None:
    """Save discordant case details to CSV."""
    df = pd.DataFrame({
        'question_id': range(n),
        'discordant': disc['discordant_mask'],
        'high_entropy_only': disc['high_entropy_only'],
        'high_inconsistency_only': disc['high_inconsistency_only'],
    })
    df.to_csv(output_path, index=False)


def evaluate_gate(corr: dict, disc: dict, subset: dict,
                  thresholds: ThresholdsConfig) -> dict:
    """Evaluate MUST_WORK gate criteria."""
    primary_pass = corr['pearson_r'] < thresholds.correlation_threshold

    discordant_pass = disc['discordant_proportion'] > thresholds.discordant_proportion_threshold
    auroc_e = subset.get('auroc_entropy_subset', 0)
    auroc_c = subset.get('auroc_consistency_subset', 0)
    auroc_pass = auroc_e > thresholds.subset_auroc_threshold and auroc_c > thresholds.subset_auroc_threshold

    secondary_pass = discordant_pass and auroc_pass

    return {
        'primary_pass': primary_pass,
        'secondary_pass': secondary_pass,
        'discordant_pass': discordant_pass,
        'auroc_pass': auroc_pass,
        'gate_result': 'PASS' if (primary_pass and secondary_pass) else 'FAIL'
    }


def main():
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    config_path = script_dir / "config.yaml"
    if config_path.exists():
        cfg = HM3Config.from_yaml(str(config_path))
    else:
        cfg = HM3Config()

    np.random.seed(cfg.seed)

    os.makedirs(cfg.paths.output_dir, exist_ok=True)
    os.makedirs(cfg.paths.figures_dir, exist_ok=True)

    print("=== H-M3: Orthogonality Verification ===\n")

    print(f"Loading scores from H-M1: {cfg.paths.h_m1_results}")
    print(f"Loading scores from H-M2: {cfg.paths.h_m2_results}")
    entropy, consistency, labels = load_scores(
        cfg.paths.h_m1_results,
        cfg.paths.h_m2_results
    )
    print(f"Loaded {len(entropy)} questions\n")

    print("Step 1: Correlation Analysis")
    corr = compute_correlation(entropy, consistency)
    print(f"  Pearson r: {corr['pearson_r']:.4f} (p = {corr['pearson_p']:.2e})")
    print(f"  Spearman ρ: {corr['spearman_r']:.4f} (p = {corr['spearman_p']:.2e})")
    print(f"  Primary criterion (r < {cfg.thresholds.correlation_threshold}): "
          f"{'PASS' if corr['pearson_r'] < cfg.thresholds.correlation_threshold else 'FAIL'}\n")

    print("Step 2-3: Discordant Case Identification")
    disc = identify_discordant(entropy, consistency, cfg.thresholds.discordant_rank_diff)
    print(f"  Discordant proportion: {disc['discordant_proportion']:.2%} ({disc['n_discordant']} questions)")
    print(f"  High-entropy-only: {disc['n_high_entropy_only']}")
    print(f"  High-inconsistency-only: {disc['n_high_inconsistency_only']}\n")

    print("Step 4: Subset AUROC Analysis")
    subset = compute_subset_auroc(entropy, consistency, labels, disc, cfg.thresholds.min_subset_size)
    if 'auroc_entropy_subset' in subset:
        print(f"  Entropy subset AUROC: {subset['auroc_entropy_subset']:.4f} (n={subset['n_entropy_subset']})")
    else:
        print(f"  Entropy subset: insufficient samples (< {cfg.thresholds.min_subset_size})")
    if 'auroc_consistency_subset' in subset:
        print(f"  Consistency subset AUROC: {subset['auroc_consistency_subset']:.4f} (n={subset['n_consistency_subset']})")
    else:
        print(f"  Consistency subset: insufficient samples (< {cfg.thresholds.min_subset_size})\n")

    print("Step 5: Gate Evaluation")
    gate = evaluate_gate(corr, disc, subset, cfg.thresholds)
    print(f"  Primary (correlation < 0.3): {'PASS' if gate['primary_pass'] else 'FAIL'}")
    print(f"  Secondary (discordant > 15% + AUROC > 0.6): {'PASS' if gate['secondary_pass'] else 'FAIL'}")
    print(f"    - Discordant check: {'PASS' if gate['discordant_pass'] else 'FAIL'}")
    print(f"    - AUROC check: {'PASS' if gate['auroc_pass'] else 'FAIL'}")

    results = {
        **corr,
        'discordant_proportion': disc['discordant_proportion'],
        'n_discordant': disc['n_discordant'],
        'n_high_entropy_only': disc['n_high_entropy_only'],
        'n_high_inconsistency_only': disc['n_high_inconsistency_only'],
        **subset,
        **gate,
    }

    with open(cfg.paths.correlation_output, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {cfg.paths.correlation_output}")

    with open(cfg.paths.subset_auroc_output, 'w') as f:
        json.dump(subset, f, indent=2)
    print(f"Saved: {cfg.paths.subset_auroc_output}")

    save_discordant_csv(disc, len(entropy), cfg.paths.discordant_output)
    print(f"Saved: {cfg.paths.discordant_output}")

    print("\nGenerating visualizations...")
    plot_scatter(entropy, consistency, labels, cfg.paths.scatter_plot)
    print(f"Saved: {cfg.paths.scatter_plot}")
    plot_quadrant(entropy, consistency, labels, cfg.paths.quadrant_plot)
    print(f"Saved: {cfg.paths.quadrant_plot}")

    print(f"\n{'='*50}")
    print(f"H-M3 GATE RESULT: {gate['gate_result']}")
    print(f"{'='*50}")

    return results


if __name__ == '__main__':
    main()
