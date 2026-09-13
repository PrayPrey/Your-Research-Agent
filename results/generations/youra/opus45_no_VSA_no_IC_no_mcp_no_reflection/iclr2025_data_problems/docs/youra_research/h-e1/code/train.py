"""Main entrypoint for h-e1 experiment."""

import os
import json
import torch
import numpy as np

from config import CONFIG
from data import load_pile_subset, load_pile_subset_synthetic, load_mmlu_validation, cache_processed, load_cached
from model import load_embedder, embed_domains, embed_tasks, random_baseline_embeddings, compute_domain_scores
from analysis import descriptive_stats, anova_test, reproducibility_check, plot_domain_bar, write_report


def run_single_seed(model, domain_texts: list[str], domain_labels: list[str],
                    task_texts: list[str], seed: int) -> tuple[dict[str, float], list[np.ndarray]]:
    """Run embedding + similarity for single seed.

    Returns (domain_scores, per_sample_scores_by_domain)
    """
    torch.manual_seed(seed)
    np.random.seed(seed)

    print(f"\n=== Running seed {seed} ===")

    print("Embedding domains...")
    domain_emb = embed_domains(model, domain_texts)

    print("Embedding tasks...")
    task_emb = embed_tasks(model, task_texts)

    print("Computing similarity matrix...")
    sim_matrix = domain_emb @ task_emb.T
    per_sample_mean = sim_matrix.mean(dim=1).cpu().numpy()

    # Compute per-domain scores
    domain_scores = compute_domain_scores(domain_emb, task_emb, domain_labels)

    # Group per-sample scores by domain for ANOVA
    per_sample_by_domain = []
    for domain in CONFIG["domains"]:
        mask = [l == domain for l in domain_labels]
        domain_samples = per_sample_mean[mask]
        per_sample_by_domain.append(domain_samples)

    return domain_scores, per_sample_by_domain


def run_baselines(domain_texts: list[str], domain_labels: list[str],
                  task_texts: list[str]) -> dict[str, float]:
    """Run random embedding baseline."""
    print("\n=== Running random embedding baseline ===")

    n_domain = len(domain_texts)
    n_task = len(task_texts)

    domain_emb = random_baseline_embeddings(n_domain, CONFIG["embed_dim"], seed=42)
    task_emb = random_baseline_embeddings(n_task, CONFIG["embed_dim"], seed=43)

    return compute_domain_scores(domain_emb.cuda() if torch.cuda.is_available() else domain_emb,
                                  task_emb.cuda() if torch.cuda.is_available() else task_emb,
                                  domain_labels)


def main():
    print("=" * 60)
    print("h-e1: E5-large Embedding Similarity Experiment")
    print("=" * 60)

    os.makedirs(CONFIG["data_dir"], exist_ok=True)
    os.makedirs("embeddings", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)

    # Load or cache data
    cached = load_cached(CONFIG["data_dir"])
    if cached:
        print("Loading cached data...")
        domain_texts, domain_labels, task_texts = cached
    else:
        print("Loading domain samples (8 domains, 1000 samples each)...")
        print("Using synthetic domain data for fast PoC validation...")
        domain_texts, domain_labels = load_pile_subset_synthetic(
            CONFIG["domains"], CONFIG["samples_per_domain"], seed=42
        )
        print(f"Loaded {len(domain_texts)} domain samples")

        print("Loading MMLU validation set...")
        task_texts = load_mmlu_validation()
        print(f"Loaded {len(task_texts)} task exemplars")

        print("Caching data...")
        cache_processed(domain_texts, domain_labels, task_texts, CONFIG["data_dir"])

    # Summary
    domain_counts = {}
    for label in domain_labels:
        domain_counts[label] = domain_counts.get(label, 0) + 1
    print("\nDomain sample counts:")
    for d, c in sorted(domain_counts.items()):
        print(f"  {d}: {c}")
    print(f"Task exemplars: {len(task_texts)}")

    # Load model
    print("\nLoading E5-large-v2 model...")
    model = load_embedder()

    # Run multiple seeds for reproducibility
    all_runs = []
    all_per_sample = None  # Keep last run for ANOVA

    for seed in CONFIG["seeds"]:
        scores, per_sample = run_single_seed(model, domain_texts, domain_labels, task_texts, seed)
        all_runs.append(scores)
        all_per_sample = per_sample

    # Use first seed as primary result
    primary_scores = all_runs[0]

    # Compute statistics
    print("\n=== Analysis ===")
    stats = descriptive_stats(primary_scores)
    print(f"Descriptive stats: mean={stats['mean']:.4f}, std={stats['std']:.4f}")

    f_stat, p_val = anova_test(all_per_sample)
    print(f"ANOVA: F={f_stat:.2f}, p={p_val:.4e}")

    repro_var = reproducibility_check(all_runs)
    print(f"Reproducibility variance: {repro_var:.6f}")

    # Run baseline
    baseline_scores = run_baselines(domain_texts, domain_labels, task_texts)

    # Evaluate success criteria
    std_pass = stats['std'] > CONFIG['min_cross_domain_std']
    anova_pass = p_val < CONFIG['anova_p_threshold']
    repro_pass = repro_var < CONFIG['max_reproducibility_variance']

    overall_pass = std_pass and anova_pass and repro_pass

    print("\n=== Success Criteria ===")
    print(f"1. Non-trivial variance (std > {CONFIG['min_cross_domain_std']}): "
          f"{'PASS' if std_pass else 'FAIL'} (std = {stats['std']:.4f})")
    print(f"2. ANOVA significance (p < {CONFIG['anova_p_threshold']}): "
          f"{'PASS' if anova_pass else 'FAIL'} (p = {p_val:.4e})")
    print(f"3. Reproducibility (var < {CONFIG['max_reproducibility_variance']}): "
          f"{'PASS' if repro_pass else 'FAIL'} (var = {repro_var:.6f})")
    print(f"\nOverall: {'PASS' if overall_pass else 'FAIL'}")

    # Save outputs
    print("\n=== Saving outputs ===")

    # Domain scores JSON
    with open(CONFIG['domain_scores_path'], 'w') as f:
        json.dump({
            "primary_scores": primary_scores,
            "all_runs": all_runs,
            "baseline_scores": baseline_scores,
            "statistics": stats,
            "anova": {"f_stat": f_stat, "p_value": p_val},
            "reproducibility_variance": repro_var,
            "pass": overall_pass
        }, f, indent=2)
    print(f"Saved: {CONFIG['domain_scores_path']}")

    # Plot
    plot_domain_bar(primary_scores, CONFIG['figure_path'])
    print(f"Saved: {CONFIG['figure_path']}")

    # Report
    write_report(primary_scores, stats, (f_stat, p_val), repro_var, overall_pass,
                 baseline_scores, CONFIG['report_path'])
    print(f"Saved: {CONFIG['report_path']}")

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE - Gate Verdict: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 60)

    return overall_pass


if __name__ == "__main__":
    main()
