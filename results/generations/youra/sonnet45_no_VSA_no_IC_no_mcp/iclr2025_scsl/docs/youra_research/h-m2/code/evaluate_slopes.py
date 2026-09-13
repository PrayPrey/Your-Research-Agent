import os
import glob
import numpy as np
import pandas as pd
from scipy.stats import linregress


def compute_slope(gap_trajectory, epochs):
    """Linear regression: gap = β₀ + β₁ × epoch."""
    slope, intercept, r_value, p_value, std_err = linregress(epochs, gap_trajectory)
    return slope


def bootstrap_ci(slopes, n_bootstrap=1000, confidence=0.95, seed=42):
    """Bootstrap CI for mean slope."""
    rng = np.random.default_rng(seed)
    bootstrap_means = []
    for _ in range(n_bootstrap):
        resample = rng.choice(slopes, size=len(slopes), replace=True)
        bootstrap_means.append(resample.mean())

    alpha = (1 - confidence) / 2
    ci_lower = np.percentile(bootstrap_means, alpha * 100)
    ci_upper = np.percentile(bootstrap_means, (1 - alpha) * 100)
    return ci_lower, slopes.mean(), ci_upper


def cohens_d(slopes_a, slopes_b):
    """Cohen's d effect size."""
    mean_a = slopes_a.mean()
    mean_b = slopes_b.mean()
    var_a = slopes_a.var(ddof=1)
    var_b = slopes_b.var(ddof=1)
    pooled_std = np.sqrt((var_a + var_b) / 2)
    if pooled_std == 0:
        return 0.0
    return (mean_a - mean_b) / pooled_std


def compute_slopes_per_architecture(logs_dir, architecture, start_epoch=20, end_epoch=50):
    """Compute slopes for all seeds of an architecture."""
    pattern = os.path.join(logs_dir, f"{architecture}_*.csv")
    files = sorted(glob.glob(pattern))

    slopes = []
    for fpath in files:
        df = pd.read_csv(fpath)
        window = df[(df['epoch'] >= start_epoch) & (df['epoch'] <= end_epoch)]
        if len(window) < 2:
            continue
        epochs = window['epoch'].values
        gaps = window['worst_group_gap'].values
        slope = compute_slope(gaps, epochs)
        slopes.append(slope)

    return np.array(slopes)


def evaluate_slopes(logs_dir='../results/logs/', start_epoch=20, end_epoch=50):
    """Compute slopes, CIs, Cohen's d for all architectures."""
    architectures = ['resnet_bn', 'resnet_cbam', 'vit_small']
    results = []

    baseline_slopes = compute_slopes_per_architecture(logs_dir, 'resnet_bn', start_epoch, end_epoch)

    for arch in architectures:
        slopes = compute_slopes_per_architecture(logs_dir, arch, start_epoch, end_epoch)
        if len(slopes) == 0:
            print(f"No slopes for {arch}")
            continue

        ci_lower, mean_slope, ci_upper = bootstrap_ci(slopes)
        d = cohens_d(slopes, baseline_slopes) if arch != 'resnet_bn' else 0.0

        results.append({
            'architecture': arch,
            'mean_slope': mean_slope,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'cohens_d': d
        })

    df = pd.DataFrame(results)
    df.to_csv('../results/slopes.csv', index=False)
    return df


def check_hypothesis(slope_stats, slope_threshold=0.3, effect_size_threshold=0.8):
    """Test hypothesis against success criteria."""
    bn_row = slope_stats[slope_stats['architecture'] == 'resnet_bn'].iloc[0]
    cbam_row = slope_stats[slope_stats['architecture'] == 'resnet_cbam'].iloc[0]
    vit_row = slope_stats[slope_stats['architecture'] == 'vit_small'].iloc[0]

    bn_mean = bn_row['mean_slope']
    bn_ci_lower = bn_row['ci_lower']
    bn_ci_upper = bn_row['ci_upper']

    def test_success(row):
        ci_overlap = not (row['ci_upper'] < bn_ci_lower or row['ci_lower'] > bn_ci_upper)
        slope_diff = bn_mean - row['mean_slope']
        d = abs(row['cohens_d'])
        success = (not ci_overlap) and (slope_diff >= slope_threshold) and (d >= effect_size_threshold)
        return success

    cbam_success = test_success(cbam_row)
    vit_success = test_success(vit_row)

    if cbam_success and vit_success:
        interpretation = "Attention enables correction"
    elif cbam_success and not vit_success:
        interpretation = "Channel attention sufficient"
    elif not cbam_success and vit_success:
        interpretation = "Global architecture, not attention"
    else:
        interpretation = "Hypothesis falsified"

    return {
        'cbam_success': cbam_success,
        'vit_success': vit_success,
        'interpretation': interpretation,
        'details': {
            'bn_mean': bn_mean,
            'cbam_mean': cbam_row['mean_slope'],
            'vit_mean': vit_row['mean_slope'],
            'cbam_d': cbam_row['cohens_d'],
            'vit_d': vit_row['cohens_d']
        }
    }


if __name__ == '__main__':
    print("Computing slopes...")
    slopes_df = evaluate_slopes()
    print(slopes_df)

    print("\nTesting hypothesis...")
    result = check_hypothesis(slopes_df)
    print(result)
