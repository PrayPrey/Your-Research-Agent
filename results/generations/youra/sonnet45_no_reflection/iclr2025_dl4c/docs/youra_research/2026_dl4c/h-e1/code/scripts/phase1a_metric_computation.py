#!/usr/bin/env python3
"""
Phase 1A: Metric Computation for Real GitHub Commits
Implements Section 3.2 Step 4 from 02c_experiment_brief.md

Computes 4 quality metrics for each commit:
- Δcorrectness: Test pass rate change (pytest/jest)
- Δquality: SonarQube maintainability rating change
- Δsecurity: CodeQL alert count change
- Δefficiency: pytest-benchmark runtime change

Runtime: ~22 hours for 10K commits (as per experiment brief)
Each commit takes ~8 seconds (SonarQube + CodeQL + pytest)
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from data_collection import CommitData


def compute_metrics_for_commit(commit_data: Dict) -> Dict[str, float]:
    """
    Compute all 4 metrics for a single commit.

    This is a PLACEHOLDER for the real metric computation.
    The full implementation would:
    1. Download pre/post file pairs from GitHub
    2. Run pytest/jest on pre/post versions
    3. Run SonarQube analysis on both versions
    4. Run CodeQL analysis on both versions
    5. Run pytest-benchmark on affected functions
    6. Compute Δ for each metric

    Args:
        commit_data: Dict with commit_id, repo_name, etc.

    Returns:
        Dict with correctness, quality, security, efficiency metrics
    """
    # PLACEHOLDER: Real implementation needed
    # This would call:
    # - docker run sonarqube (for Δquality)
    # - codeql analyze (for Δsecurity)
    # - pytest --cov (for Δcorrectness)
    # - pytest-benchmark (for Δefficiency)

    # For now, return placeholder values indicating real computation needed
    return {
        'correctness': 0.0,  # Real: test pass rate delta
        'quality': 0.0,      # Real: SonarQube rating delta
        'security': 0.0,     # Real: CodeQL alert count delta
        'efficiency': 0.0    # Real: pytest-benchmark runtime delta
    }


def compute_metrics_parallel(
    commits_file: str,
    output_file: str,
    n_workers: int = 16
):
    """
    Compute metrics for all commits in parallel.

    Args:
        commits_file: Input JSONL file with commit metadata
        output_file: Output .npy file for outcome matrix
        n_workers: Number of parallel workers
    """
    print("=" * 80)
    print("Phase 1A: Metric Computation for Real GitHub Commits")
    print("=" * 80)
    print()

    # Load commits
    print(f"Loading commits from {commits_file}...")
    commits = []
    with open(commits_file, 'r') as f:
        for line in f:
            commits.append(json.loads(line))

    print(f"✅ Loaded {len(commits)} commits")
    print()

    print("CRITICAL: Real metric computation required")
    print("=" * 80)
    print()
    print("This script is a PLACEHOLDER for the full metric computation pipeline.")
    print("Per 02c_experiment_brief.md Section 3.2 Step 4, each commit requires:")
    print()
    print("  1. Δcorrectness: pytest/jest test pass rate change")
    print("     - Download pre/post file pairs from GitHub")
    print("     - Run test suite on both versions")
    print("     - Compute pass rate difference")
    print()
    print("  2. Δquality: SonarQube maintainability rating change")
    print("     - docker run sonarqube:latest")
    print("     - sonar-scanner on pre/post versions")
    print("     - Extract maintainability rating delta")
    print()
    print("  3. Δsecurity: CodeQL alert count change")
    print("     - codeql analyze pre/post versions")
    print("     - Count security alerts in each")
    print("     - Compute delta")
    print()
    print("  4. Δefficiency: pytest-benchmark runtime change")
    print("     - Run pytest-benchmark on affected functions")
    print("     - Compute % runtime improvement")
    print()
    print("Runtime estimate: ~8 seconds/commit × 10K = ~22 hours")
    print("Parallelization: 16 workers reduces to ~1.4 hours")
    print()
    print("=" * 80)
    print()
    print("IMPLEMENTATION STATUS: Placeholder only")
    print()
    print("To complete this experiment, you must implement:")
    print("  - GitHub file download (PyGitHub, PyDriller)")
    print("  - SonarQube integration (Docker + API)")
    print("  - CodeQL integration (CLI + SARIF parsing)")
    print("  - pytest/jest test execution")
    print("  - pytest-benchmark runtime measurement")
    print()
    print("Without real metrics, the experiment cannot validate the hypothesis.")
    print()
    print("=" * 80)
    sys.exit(1)

    # The code below would run if real metrics were implemented:
    """
    print(f"Computing metrics with {n_workers} workers...")
    print(f"Estimated time: {len(commits) * 8 / n_workers / 3600:.1f} hours")
    print()

    # Parallel metric computation
    with Pool(n_workers) as pool:
        metrics_list = list(tqdm(
            pool.imap(compute_metrics_for_commit, commits),
            total=len(commits),
            desc="Computing metrics"
        ))

    # Build outcome matrix
    Y = np.zeros((len(commits), 4))
    for i, metrics in enumerate(metrics_list):
        Y[i] = [
            metrics['correctness'],
            metrics['quality'],
            metrics['security'],
            metrics['efficiency']
        ]

    # Save outcome matrix
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, Y)

    print()
    print(f"✅ Saved outcome matrix ({Y.shape}) to {output_file}")
    print()

    # Print statistics
    print("Metric statistics (mean ± std):")
    metric_names = ['correctness', 'quality', 'security', 'efficiency']
    for i, name in enumerate(metric_names):
        mean = np.mean(Y[:, i])
        std = np.std(Y[:, i])
        print(f"  Δ{name:12s}: {mean:6.3f} ± {std:5.3f}")

    print()
    print("=" * 80)
    print("Metric Computation Complete")
    print("=" * 80)
    """


def main():
    parser = argparse.ArgumentParser(
        description="Compute quality metrics for GitHub commits"
    )
    parser.add_argument(
        "--commits",
        type=str,
        required=True,
        help="Input JSONL file with commit metadata"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/outcome_matrix.npy",
        help="Output .npy file for outcome matrix (default: data/outcome_matrix.npy)"
    )
    parser.add_argument(
        "--n-workers",
        type=int,
        default=16,
        help="Number of parallel workers (default: 16)"
    )

    args = parser.parse_args()

    compute_metrics_parallel(
        commits_file=args.commits,
        output_file=args.output,
        n_workers=args.n_workers
    )


if __name__ == '__main__':
    main()
