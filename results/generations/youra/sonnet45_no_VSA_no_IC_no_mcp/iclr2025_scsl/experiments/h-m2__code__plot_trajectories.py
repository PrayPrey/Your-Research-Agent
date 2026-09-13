import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress


def plot_trajectories(logs_dir='../results/logs/', slopes_csv='../results/slopes.csv', output_path='../results/trajectories.png'):
    """Plot gap trajectories with regression overlays."""
    architectures = ['resnet_bn', 'resnet_cbam', 'vit_small']
    arch_labels = {'resnet_bn': 'ResNet-BN (control)', 'resnet_cbam': 'ResNet-CBAM', 'vit_small': 'ViT-Small'}
    colors = {'resnet_bn': 'blue', 'resnet_cbam': 'green', 'vit_small': 'red'}

    fig, ax = plt.subplots(figsize=(10, 6))

    for arch in architectures:
        pattern = os.path.join(logs_dir, f"{arch}_*.csv")
        files = sorted(glob.glob(pattern))

        all_gaps = []
        for fpath in files:
            df = pd.read_csv(fpath)
            gaps = df['worst_group_gap'].values
            all_gaps.append(gaps)

        all_gaps = np.array(all_gaps)
        mean_gaps = all_gaps.mean(axis=0)
        stderr_gaps = all_gaps.std(axis=0) / np.sqrt(len(all_gaps))

        epochs = np.arange(len(mean_gaps))
        ax.plot(epochs, mean_gaps, label=arch_labels[arch], color=colors[arch], linewidth=2)
        ax.fill_between(epochs, mean_gaps - stderr_gaps, mean_gaps + stderr_gaps, color=colors[arch], alpha=0.2)

        window_epochs = epochs[20:51]
        window_gaps = mean_gaps[20:51]
        slope, intercept, _, _, _ = linregress(window_epochs, window_gaps)
        regression_line = slope * window_epochs + intercept
        ax.plot(window_epochs, regression_line, linestyle='--', color=colors[arch], linewidth=1.5, alpha=0.8)

    ax.axvspan(20, 50, color='gray', alpha=0.1, label='Analysis window (epochs 20-50)')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Worst-Group Gap (avg - worst)')
    ax.set_title('Worst-Group Gap Trajectories')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Plot saved to {output_path}")


def generate_summary_table(slopes_csv='../results/slopes.csv', output_path='../results/statistical_summary.md'):
    """Generate markdown summary table."""
    df = pd.read_csv(slopes_csv)

    with open(output_path, 'w') as f:
        f.write("# Statistical Summary\n\n")
        f.write("| Architecture | Mean Slope (pp/epoch) | 95% CI Lower | 95% CI Upper | Cohen's d |\n")
        f.write("|--------------|----------------------|--------------|--------------|----------|\n")

        for _, row in df.iterrows():
            f.write(f"| {row['architecture']} | {row['mean_slope']:.4f} | {row['ci_lower']:.4f} | {row['ci_upper']:.4f} | {row['cohens_d']:.4f} |\n")

        f.write("\n## Interpretation\n\n")
        f.write("- Negative slope = gap reduction over time\n")
        f.write("- Success criteria: (CBAM OR ViT) slope < BN slope - 0.3pp/epoch, non-overlapping CIs, Cohen's d ≥ 0.8\n")

    print(f"Summary table saved to {output_path}")


if __name__ == '__main__':
    plot_trajectories()
    generate_summary_table()
