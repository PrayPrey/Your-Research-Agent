#!/usr/bin/env python3
"""
Generate Test Dataset for H-E1 Code Validation

IMPORTANT: This generates SYNTHETIC data ONLY for code validation purposes.
The real experiment REQUIRES actual GitHub data collected via phase1a_data_collection.py

This synthetic data:
- Does NOT guarantee hypothesis validation (outcome is randomized)
- Allows testing of analysis pipeline implementation
- Clearly marked as TEST data in all outputs
- Should NOT be used for final hypothesis evaluation

Purpose: Enable development/testing when real data collection (22+ hours) is impractical
"""
import json
import numpy as np
from pathlib import Path
import argparse


def generate_test_dataset(
    n_commits: int = 10000,
    output_dir: str = "data",
    random_seed: int = 42
):
    """
    Generate synthetic test dataset matching real data structure.

    This creates:
    - commits_10k.jsonl: Commit metadata with aspect labels
    - outcome_matrix.npy: [N, 4] quality metrics (Δcorrectness, Δquality, Δsecurity, Δefficiency)

    The synthetic data has realistic distributions but NO guaranteed aspect-dominant structure.
    Outcome depends on random generation, not hardcoded to pass/fail.
    """
    print("=" * 80)
    print("SYNTHETIC TEST DATASET GENERATION")
    print("=" * 80)
    print()
    print("⚠️  WARNING: This is SYNTHETIC data for CODE VALIDATION ONLY")
    print()
    print("This dataset:")
    print("  ✓ Matches real data structure (for testing pipeline code)")
    print("  ✓ Has realistic distributions and correlations")
    print("  ✗ Does NOT guarantee hypothesis validation")
    print("  ✗ Should NOT be used for final experiment results")
    print()
    print("For REAL experiment, run:")
    print("  1. python scripts/phase1a_data_collection.py --n-commits 10000")
    print("  2. python scripts/phase1a_metric_computation.py --commits data/commits_10k.jsonl")
    print()
    print("=" * 80)
    print()

    np.random.seed(random_seed)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Define aspects
    aspects = ['security', 'refactor', 'performance', 'bugfix']
    aspect_distribution = [0.25, 0.25, 0.25, 0.25]  # Equal distribution

    # Generate commits
    print(f"Generating {n_commits} synthetic commits...")
    commits = []

    for i in range(n_commits):
        aspect = np.random.choice(aspects, p=aspect_distribution)

        commit = {
            'commit_id': f'test_{i:06d}',
            'repo_name': f'test_org/repo_{i % 100}',
            'message': f'[TEST] {aspect} commit {i}',
            'aspect_label': aspect,
            'metrics': {}  # Will be filled from outcome matrix
        }
        commits.append(commit)

    print(f"  ✅ Generated {len(commits)} commits")

    # Generate outcome matrix with realistic structure
    print()
    print("Generating outcome matrix...")
    print("  Strategy: Realistic correlations WITHOUT guaranteed separability")

    # Generate base effects for each aspect
    # Each aspect has some primary effect on its corresponding metric
    # But cross-effects are also present (realistic entanglement)

    Y = np.zeros((n_commits, 4))

    for i, commit in enumerate(commits):
        aspect = commit['aspect_label']
        aspect_idx = aspects.index(aspect)

        # Base quality change (independent of aspect)
        base = np.random.randn(4) * 0.5

        # Aspect-specific primary effect (moderate, not guaranteed strong)
        primary_strength = np.random.uniform(0.3, 1.5)  # Variable strength
        primary_effect = np.zeros(4)
        primary_effect[aspect_idx] = primary_strength

        # Cross-aspect coupling (realistic entanglement)
        coupling_strength = np.random.uniform(0.1, 0.4)
        for j in range(4):
            if j != aspect_idx:
                primary_effect[j] = np.random.randn() * coupling_strength

        # Combine effects
        Y[i] = base + primary_effect + np.random.randn(4) * 0.3

    # Add realistic confound effects
    # Edit size effect (larger edits → larger metric changes)
    edit_sizes = np.random.exponential(10, n_commits)
    for j in range(4):
        Y[:, j] += edit_sizes * np.random.uniform(0.01, 0.05)

    # Repository effect (some repos have systematically higher/lower quality)
    repo_effects = np.random.randn(100, 4) * 0.3
    for i, commit in enumerate(commits):
        repo_id = i % 100
        Y[i] += repo_effects[repo_id]

    print(f"  ✅ Generated outcome matrix shape: {Y.shape}")
    print()

    # Compute actual structure for info
    Sigma = np.cov(Y.T)
    eigenvalues = np.linalg.eigvalsh(Sigma)[::-1]
    spectral_gap = eigenvalues[3] / (eigenvalues[4] if len(eigenvalues) > 4 else 0.01) if len(eigenvalues) > 4 else eigenvalues[3] / 0.01

    print("Dataset characteristics:")
    print(f"  Eigenvalues: {eigenvalues[:4]}")
    print(f"  Spectral gap: {spectral_gap:.3f}")
    print(f"  (Note: Outcome is random, may pass or fail gate)")
    print()

    # Fill metrics in commit objects
    metric_names = ['correctness', 'quality', 'security', 'efficiency']
    for i, commit in enumerate(commits):
        commit['metrics'] = {
            name: float(Y[i, j]) for j, name in enumerate(metric_names)
        }

    # Save commits
    commits_file = output_path / "commits_10k.jsonl"
    print(f"Saving commits to {commits_file}...")
    with open(commits_file, 'w') as f:
        for commit in commits:
            f.write(json.dumps(commit) + '\n')
    print(f"  ✅ Saved")

    # Save outcome matrix
    outcome_file = output_path / "outcome_matrix.npy"
    print(f"Saving outcome matrix to {outcome_file}...")
    np.save(outcome_file, Y)
    print(f"  ✅ Saved")

    # Create metadata file marking this as synthetic
    metadata_file = output_path / "DATASET_INFO.txt"
    with open(metadata_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("SYNTHETIC TEST DATASET - NOT FOR FINAL RESULTS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated: {n_commits} commits\n")
        f.write(f"Random seed: {random_seed}\n")
        f.write(f"Purpose: Code validation and testing\n\n")
        f.write("This dataset is SYNTHETIC and should NOT be used for:\n")
        f.write("  ✗ Final hypothesis validation\n")
        f.write("  ✗ Publication results\n")
        f.write("  ✗ Empirical claims about real GitHub commits\n\n")
        f.write("For REAL experiment, collect actual GitHub data via:\n")
        f.write("  python scripts/phase1a_data_collection.py\n")
        f.write("  python scripts/phase1a_metric_computation.py\n\n")
        f.write("=" * 80 + "\n")

    print()
    print("=" * 80)
    print("SYNTHETIC DATASET GENERATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Files created in {output_dir}/:")
    print(f"  ✅ commits_10k.jsonl ({len(commits)} commits)")
    print(f"  ✅ outcome_matrix.npy ({Y.shape[0]} × {Y.shape[1]})")
    print(f"  ✅ DATASET_INFO.txt (metadata)")
    print()
    print("⚠️  REMINDER: This is TEST data only")
    print("   Real data collection required for actual hypothesis validation")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic test dataset for H-E1 code validation"
    )
    parser.add_argument(
        "--n-commits",
        type=int,
        default=10000,
        help="Number of commits to generate (default: 10000)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data",
        help="Output directory (default: data)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)"
    )

    args = parser.parse_args()

    generate_test_dataset(
        n_commits=args.n_commits,
        output_dir=args.output,
        random_seed=args.seed
    )


if __name__ == '__main__':
    main()
