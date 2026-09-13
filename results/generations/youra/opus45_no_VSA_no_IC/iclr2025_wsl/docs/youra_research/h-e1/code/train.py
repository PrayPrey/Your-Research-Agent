"""Main experiment: data efficiency sweep for statistics baseline."""
import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, List
from tqdm import tqdm

import config
from data import download_model_zoo, load_checkpoints, split_test_set
from features import build_feature_matrix, extract_weight_statistics
from model import fit_ridge, evaluate


def sample_models(
    pool_X: np.ndarray,
    pool_y: np.ndarray,
    n: int,
    seed: int
) -> Tuple[np.ndarray, np.ndarray]:
    """Sample n models from pool with given seed."""
    rng = np.random.RandomState(seed)
    if n > len(pool_y):
        n = len(pool_y)
    idx = rng.choice(len(pool_y), size=n, replace=False)
    return pool_X[idx], pool_y[idx]


def run_sweep(
    pool_X: np.ndarray,
    pool_y: np.ndarray,
    test_X: np.ndarray,
    test_y: np.ndarray,
    N_values: List[int] = config.N_VALUES,
    n_seeds: int = config.N_SEEDS
) -> pd.DataFrame:
    """Run N x seed sweep, return results DataFrame."""
    results = []

    for n in tqdm(N_values, desc="N values"):
        for seed in range(n_seeds):
            X_train, y_train = sample_models(pool_X, pool_y, n, seed)
            model = fit_ridge(X_train, y_train)
            r2 = evaluate(model, test_X, test_y)
            results.append({
                'n': n,
                'seed': seed,
                'r2': r2,
                'alpha': model.alpha_
            })

    return pd.DataFrame(results)


def plot_learning_curve(df: pd.DataFrame, output_path: str = config.PLOT_PATH):
    """Plot R² vs N with error bars."""
    grouped = df.groupby('n')['r2']
    means = grouped.mean()
    stds = grouped.std()

    plt.figure(figsize=(8, 5))
    plt.errorbar(means.index, means.values, yerr=stds.values,
                 marker='o', capsize=5, linewidth=2, markersize=8)
    plt.xlabel('Training Set Size (N)')
    plt.ylabel('R² Score')
    plt.title('Statistics Baseline: R² vs Training Size')
    plt.xscale('log')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved learning curve plot to {output_path}")


def main():
    """Main entry point: run full experiment pipeline."""
    os.makedirs('outputs', exist_ok=True)

    print("=" * 60)
    print("H-E1: Statistics Baseline Experiment")
    print("=" * 60)

    print("\n[1/5] Loading data...")
    zoo_dir = download_model_zoo()
    items = load_checkpoints(zoo_dir)

    if len(items) < config.TEST_SIZE + max(config.N_VALUES):
        print(f"Warning: Only {len(items)} models available, adjusting N_VALUES")
        max_train = len(items) - config.TEST_SIZE
        N_VALUES = [n for n in config.N_VALUES if n <= max_train]
        if not N_VALUES:
            raise ValueError("Not enough models for experiment")
    else:
        N_VALUES = config.N_VALUES

    print("\n[2/5] Splitting train/test...")
    train_pool, test_set = split_test_set(items)
    print(f"Train pool: {len(train_pool)}, Test set: {len(test_set)}")

    print("\n[3/5] Extracting features...")
    pool_X, pool_y = build_feature_matrix(train_pool)
    test_X, test_y = build_feature_matrix(test_set)
    print(f"Feature shape: {pool_X.shape[1]} dimensions")

    np.savez(config.FEATURES_PATH,
             pool_X=pool_X, pool_y=pool_y,
             test_X=test_X, test_y=test_y)
    print(f"Saved features to {config.FEATURES_PATH}")

    print("\n[4/5] Running data efficiency sweep...")
    results_df = run_sweep(pool_X, pool_y, test_X, test_y, N_VALUES)
    results_df.to_csv(config.RESULTS_PATH, index=False)
    print(f"Saved results to {config.RESULTS_PATH}")

    print("\n[5/5] Generating plot...")
    plot_learning_curve(results_df)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    summary = results_df.groupby('n')['r2'].agg(['mean', 'std'])
    print(summary)

    max_n = results_df['n'].max()
    r2_at_max = results_df[results_df['n'] == max_n]['r2'].mean()
    print(f"\nR² at N={max_n}: {r2_at_max:.4f}")

    gate_passed = r2_at_max > 0.85
    print(f"Gate (R² > 0.85): {'PASSED' if gate_passed else 'FAILED'}")

    return results_df


if __name__ == "__main__":
    main()
