#!/usr/bin/env python3
"""H-E2: CV_PR vs ImageNet Accuracy Correlation Analysis"""

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Configuration
CONFIG = {
    "cv_pr_path": "h-e1/h-e1/results/results.csv",
    "accuracy_url": "https://raw.githubusercontent.com/huggingface/pytorch-image-models/main/results/results-imagenet.csv",
    "results_path": "h-e2/results/correlation_results.json",
    "figure_path": "h-e2/figures/scatter_cv_pr_vs_accuracy.png",
    "cache_path": "h-e2/results/accuracy_cache.csv",
    "r_threshold": -0.3,
    "p_threshold": 0.05,
    "min_matched_models": 80,
    "n_bootstrap": 10000,
    "ci_level": 0.95,
    "seed": 42,
    "figure_dpi": 150,
    "figure_size": (10, 8),
    "scatter_alpha": 0.6,
}


class DataLoader:
    @staticmethod
    def load_cvpr(path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        print(f"Loaded CV_PR data: {len(df)} models")
        return df

    @staticmethod
    def load_accuracy(url: str, cache_path: str) -> pd.DataFrame:
        if os.path.exists(cache_path):
            print(f"Loading cached accuracy data from {cache_path}")
            return pd.read_csv(cache_path)

        print(f"Downloading accuracy data from {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w') as f:
            f.write(response.text)

        df = pd.read_csv(cache_path)
        print(f"Downloaded accuracy data: {len(df)} models")
        return df


class Merger:
    @staticmethod
    def normalize_name(name: str) -> str:
        n = name.strip().lower()
        for suffix in ['.in1k', '.in22k', '.in21k', '.in22ft1k', '.in21ft1k',
                       '_in1k', '_in22k', '_in21k', '.a1', '.a2', '.a3']:
            if n.endswith(suffix):
                n = n[:-len(suffix)]
        return n

    @staticmethod
    def merge(cvpr_df: pd.DataFrame, acc_df: pd.DataFrame) -> tuple:
        cvpr_df = cvpr_df.copy()
        acc_df = acc_df.copy()

        cvpr_df['key'] = cvpr_df['model'].apply(Merger.normalize_name)
        acc_df['key'] = acc_df['model'].apply(Merger.normalize_name)

        # Handle duplicate keys in accuracy df - keep highest top1
        acc_df = acc_df.sort_values('top1', ascending=False).drop_duplicates(subset='key', keep='first')

        merged = cvpr_df.merge(acc_df[['key', 'top1', 'top5', 'param_count']], on='key', how='inner')
        match_rate = len(merged) / len(cvpr_df) if len(cvpr_df) > 0 else 0

        print(f"Matched {len(merged)}/{len(cvpr_df)} models ({match_rate*100:.1f}%)")

        unmatched = cvpr_df[~cvpr_df['key'].isin(merged['key'])]['model'].tolist()
        if unmatched:
            print(f"Unmatched models: {unmatched[:10]}{'...' if len(unmatched) > 10 else ''}")

        return merged, match_rate


class Correlator:
    @staticmethod
    def analyze(merged: pd.DataFrame, n_bootstrap: int = 10000, seed: int = 42) -> dict:
        x = merged['model_cv_pr'].values
        y = merged['top1'].values

        r_pearson, p_pearson = pearsonr(x, y)
        r_spearman, p_spearman = spearmanr(x, y)

        ci_low, ci_high = Correlator.bootstrap_ci(x, y, n_bootstrap=n_bootstrap, seed=seed)

        outliers = Correlator.find_outliers(merged, r_pearson)

        return {
            'pearson_r': float(r_pearson),
            'pearson_p': float(p_pearson),
            'spearman_r': float(r_spearman),
            'spearman_p': float(p_spearman),
            'n': len(merged),
            'ci_low': float(ci_low),
            'ci_high': float(ci_high),
            'ci_level': 0.95,
            'n_bootstrap': n_bootstrap,
            'outliers': outliers.to_dict('records') if len(outliers) > 0 else [],
            'cv_pr_mean': float(x.mean()),
            'cv_pr_std': float(x.std()),
            'top1_mean': float(y.mean()),
            'top1_std': float(y.std()),
        }

    @staticmethod
    def bootstrap_ci(x: np.ndarray, y: np.ndarray, n_bootstrap: int = 10000,
                     ci: float = 0.95, seed: int = 42) -> tuple:
        rng = np.random.default_rng(seed)
        n = len(x)
        boot_stats = np.zeros(n_bootstrap)

        for i in range(n_bootstrap):
            idx = rng.integers(0, n, size=n)
            xb, yb = x[idx], y[idx]
            if xb.std() == 0 or yb.std() == 0:
                boot_stats[i] = np.nan
            else:
                boot_stats[i] = pearsonr(xb, yb)[0]

        alpha = (1 - ci) / 2
        lo, hi = np.nanpercentile(boot_stats, [100*alpha, 100*(1-alpha)])
        return lo, hi

    @staticmethod
    def find_outliers(merged: pd.DataFrame, r: float, z_thresh: float = 2.5) -> pd.DataFrame:
        x = merged['model_cv_pr'].values
        y = merged['top1'].values

        x_norm = (x - x.mean()) / x.std()
        y_norm = (y - y.mean()) / y.std()

        # Residuals from regression line
        slope = r * (y.std() / x.std())
        intercept = y.mean() - slope * x.mean()
        y_pred = slope * x + intercept
        residuals = y - y_pred
        residual_std = residuals.std()
        z_residuals = residuals / residual_std if residual_std > 0 else np.zeros_like(residuals)

        outlier_mask = np.abs(z_residuals) > z_thresh
        return merged[outlier_mask][['model', 'model_cv_pr', 'top1']].copy()


class Visualizer:
    @staticmethod
    def plot(merged: pd.DataFrame, stats: dict, out_path: str, config: dict) -> None:
        fig, ax = plt.subplots(figsize=config['figure_size'])

        x = merged['model_cv_pr'].values
        y = merged['top1'].values

        ax.scatter(x, y, alpha=config['scatter_alpha'], s=50, c='steelblue', edgecolor='white', linewidth=0.5)

        # Regression line
        slope = stats['pearson_r'] * (y.std() / x.std())
        intercept = y.mean() - slope * x.mean()
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, 'r-', linewidth=2, label=f"r={stats['pearson_r']:.3f}")

        # Annotations
        textstr = (f"Pearson r = {stats['pearson_r']:.4f}\n"
                   f"p-value = {stats['pearson_p']:.2e}\n"
                   f"95% CI = [{stats['ci_low']:.4f}, {stats['ci_high']:.4f}]\n"
                   f"n = {stats['n']}")
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right', bbox=props)

        ax.set_xlabel('CV_PR (Coefficient of Variation of Participation Ratio)', fontsize=12)
        ax.set_ylabel('ImageNet Top-1 Accuracy (%)', fontsize=12)
        ax.set_title('H-E2: CV_PR vs ImageNet Accuracy Correlation', fontsize=14)
        ax.grid(True, alpha=0.3)

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=config['figure_dpi'], bbox_inches='tight')
        plt.close()
        print(f"Saved figure to {out_path}")


def evaluate_success(stats: dict, config: dict) -> tuple:
    r = stats['pearson_r']
    p = stats['pearson_p']
    n = stats['n']

    r_pass = r < config['r_threshold']
    p_pass = p < config['p_threshold']
    n_pass = n >= config['min_matched_models']

    success = r_pass and p_pass and n_pass

    details = {
        'r_threshold': config['r_threshold'],
        'p_threshold': config['p_threshold'],
        'min_matched_models': config['min_matched_models'],
        'r_pass': r_pass,
        'p_pass': p_pass,
        'n_pass': n_pass,
        'overall_pass': success,
    }

    return success, details


def main():
    base_path = Path(__file__).parent.parent.parent
    os.chdir(base_path)

    print("=" * 60)
    print("H-E2: CV_PR vs ImageNet Accuracy Correlation Analysis")
    print("=" * 60)

    # Step 1: Load data
    print("\n[Step 1] Loading data...")
    cvpr_df = DataLoader.load_cvpr(CONFIG['cv_pr_path'])
    acc_df = DataLoader.load_accuracy(CONFIG['accuracy_url'], CONFIG['cache_path'])

    # Step 2: Merge
    print("\n[Step 2] Merging datasets...")
    merged, match_rate = Merger.merge(cvpr_df, acc_df)

    if len(merged) < CONFIG['min_matched_models']:
        print(f"\nERROR: Only {len(merged)} models matched (need >= {CONFIG['min_matched_models']})")
        sys.exit(1)

    # Step 3: Correlation analysis
    print("\n[Step 3] Computing correlations...")
    stats = Correlator.analyze(merged, n_bootstrap=CONFIG['n_bootstrap'], seed=CONFIG['seed'])

    print(f"  Pearson r  = {stats['pearson_r']:.4f} (p = {stats['pearson_p']:.2e})")
    print(f"  Spearman r = {stats['spearman_r']:.4f} (p = {stats['spearman_p']:.2e})")
    print(f"  95% CI     = [{stats['ci_low']:.4f}, {stats['ci_high']:.4f}]")
    print(f"  n          = {stats['n']}")

    # Step 4: Visualization
    print("\n[Step 4] Creating visualization...")
    Visualizer.plot(merged, stats, CONFIG['figure_path'], CONFIG)

    # Step 5: Evaluate success
    print("\n[Step 5] Evaluating success criteria...")
    success, details = evaluate_success(stats, CONFIG)

    results = {
        'hypothesis': 'h-e2',
        'statement': 'CV_PR correlates negatively with ImageNet accuracy (r < -0.3, p < 0.05)',
        'gate': 'MUST_WORK',
        **stats,
        'match_rate': match_rate,
        'success_criteria': details,
        'verdict': 'PASS' if success else 'FAIL',
    }

    # Save results
    os.makedirs(os.path.dirname(CONFIG['results_path']), exist_ok=True)
    with open(CONFIG['results_path'], 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved results to {CONFIG['results_path']}")

    # Final verdict
    print("\n" + "=" * 60)
    if success:
        print(f"VERDICT: PASS")
        print(f"  - Pearson r = {stats['pearson_r']:.4f} < {CONFIG['r_threshold']} ✓")
        print(f"  - p-value = {stats['pearson_p']:.2e} < {CONFIG['p_threshold']} ✓")
        print(f"  - n = {stats['n']} >= {CONFIG['min_matched_models']} ✓")
    else:
        print(f"VERDICT: FAIL")
        if not details['r_pass']:
            print(f"  - Pearson r = {stats['pearson_r']:.4f} >= {CONFIG['r_threshold']} ✗")
        if not details['p_pass']:
            print(f"  - p-value = {stats['pearson_p']:.2e} >= {CONFIG['p_threshold']} ✗")
        if not details['n_pass']:
            print(f"  - n = {stats['n']} < {CONFIG['min_matched_models']} ✗")
    print("=" * 60)
    print("\nEXPERIMENT COMPLETE")

    return results


if __name__ == "__main__":
    results = main()
