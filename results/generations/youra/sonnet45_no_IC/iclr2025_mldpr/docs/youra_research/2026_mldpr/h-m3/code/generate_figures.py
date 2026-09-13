"""
Generate required figures for H-M3 validation report.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

# Load data
results_path = Path("outputs/experiment_results.json")
variance_path = Path("outputs/variance_results.csv")

with open(results_path, 'r') as f:
    results = json.load(f)

df = pd.read_csv(variance_path)

# Create figures directory
figures_dir = Path("../figures")
figures_dir.mkdir(exist_ok=True)

print("Generating H-M3 validation figures...")

# ============================================================================
# Figure 1: Gate Metrics Comparison (MANDATORY)
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: p-value vs threshold
ax1 = axes[0]
p_value = results['primary_analysis']['mann_whitney']['p_value']
alpha = results['primary_analysis']['mann_whitney']['alpha']

bars1 = ax1.bar(['p-value', 'α threshold'], [p_value, alpha],
                color=['red' if p_value >= alpha else 'green', 'blue'],
                alpha=0.7, edgecolor='black', linewidth=1.5)
ax1.axhline(y=alpha, color='blue', linestyle='--', linewidth=2, label=f'α = {alpha}')
ax1.set_ylabel('Value', fontsize=12, fontweight='bold')
ax1.set_title('Statistical Significance Test\n(Mann-Whitney U)', fontsize=13, fontweight='bold')
ax1.set_ylim([0, max(p_value, alpha) * 1.3])
ax1.legend(fontsize=10)

# Add pass/fail annotation
status1 = "FAIL" if p_value >= alpha else "PASS"
color1 = 'red' if status1 == "FAIL" else 'green'
ax1.text(0.5, 0.95, f'Gate: {status1}', transform=ax1.transAxes,
         fontsize=14, fontweight='bold', color=color1,
         ha='center', va='top',
         bbox=dict(boxstyle='round', facecolor='white', edgecolor=color1, linewidth=2))

# Panel B: Cohen's d vs threshold
ax2 = axes[1]
cohens_d = results['primary_analysis']['cohens_d']['effect_size']
threshold = results['primary_analysis']['cohens_d']['threshold']

bars2 = ax2.bar(["Cohen's d", 'Threshold'], [cohens_d, threshold],
                color=['red' if cohens_d < threshold else 'green', 'blue'],
                alpha=0.7, edgecolor='black', linewidth=1.5)
ax2.axhline(y=threshold, color='blue', linestyle='--', linewidth=2, label=f'Target = {threshold}')
ax2.set_ylabel('Effect Size', fontsize=12, fontweight='bold')
ax2.set_title('Effect Size\n(Cohen\'s d)', fontsize=13, fontweight='bold')
ax2.set_ylim([0, max(cohens_d, threshold) * 1.3])
ax2.legend(fontsize=10)

# Add pass/fail annotation
status2 = "FAIL" if cohens_d < threshold else "PASS"
color2 = 'red' if status2 == "FAIL" else 'green'
ax2.text(0.5, 0.95, f'Gate: {status2}', transform=ax2.transAxes,
         fontsize=14, fontweight='bold', color=color2,
         ha='center', va='top',
         bbox=dict(boxstyle='round', facecolor='white', edgecolor=color2, linewidth=2))

plt.tight_layout()
plt.savefig(figures_dir / "01_gate_metrics.png", bbox_inches='tight')
print("✓ Figure 1: Gate metrics comparison saved")
plt.close()

# ============================================================================
# Figure 2: CV Distribution Comparison (Box + Violin)
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

# Violin plot
parts = ax.violinplot(
    [df[df['artifact_group'] == 'high']['cv'].values,
     df[df['artifact_group'] == 'low']['cv'].values],
    positions=[0, 1],
    widths=0.7,
    showmeans=True,
    showmedians=True
)

# Customize violin colors
for pc in parts['bodies']:
    pc.set_facecolor('lightblue')
    pc.set_alpha(0.5)

# Box plot overlay
bp = ax.boxplot(
    [df[df['artifact_group'] == 'high']['cv'].values,
     df[df['artifact_group'] == 'low']['cv'].values],
    positions=[0, 1],
    widths=0.3,
    patch_artist=True,
    boxprops=dict(facecolor='white', alpha=0.8),
    medianprops=dict(color='red', linewidth=2),
    whiskerprops=dict(linewidth=1.5),
    capprops=dict(linewidth=1.5)
)

ax.set_xticks([0, 1])
ax.set_xticklabels(['High Artifact (≥2)', 'Low Artifact (<2)'], fontsize=11, fontweight='bold')
ax.set_ylabel('Coefficient of Variation (CV)', fontsize=12, fontweight='bold')
ax.set_title('Performance Variance by Artifact Group\n(Box + Violin Plot)',
             fontsize=13, fontweight='bold')

# Add sample sizes
n_high = (df['artifact_group'] == 'high').sum()
n_low = (df['artifact_group'] == 'low').sum()
ax.text(0, ax.get_ylim()[1] * 0.95, f'n={n_high}', ha='center', fontsize=10, fontweight='bold')
ax.text(1, ax.get_ylim()[1] * 0.95, f'n={n_low}', ha='center', fontsize=10, fontweight='bold')

# Add means
mean_high = df[df['artifact_group'] == 'high']['cv'].mean()
mean_low = df[df['artifact_group'] == 'low']['cv'].mean()
ax.plot([0], [mean_high], 'ro', markersize=10, label=f'Mean (high): {mean_high:.4f}')
ax.plot([1], [mean_low], 'ro', markersize=10, label=f'Mean (low): {mean_low:.4f}')

ax.legend(fontsize=9, loc='upper right')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(figures_dir / "02_cv_distribution.png", bbox_inches='tight')
print("✓ Figure 2: CV distribution comparison saved")
plt.close()

# ============================================================================
# Figure 3: Dose-Response Scatter Plot
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

# Scatter plot with jitter
artifact_counts = df['artifact_count'].values
cvs = df['cv'].values

# Add jitter to avoid overlap
jitter = np.random.normal(0, 0.05, size=len(artifact_counts))
artifact_counts_jittered = artifact_counts + jitter

# Color by group
colors = ['red' if x < 2 else 'blue' for x in artifact_counts]

ax.scatter(artifact_counts_jittered, cvs, c=colors, s=100, alpha=0.6, edgecolors='black', linewidth=1)

# Fit line
from scipy import stats
slope, intercept, r_value, p_value_corr, std_err = stats.linregress(artifact_counts, cvs)
line = slope * artifact_counts + intercept
ax.plot(sorted(artifact_counts), [slope * x + intercept for x in sorted(artifact_counts)],
        'k--', linewidth=2, label=f'Linear fit (R²={r_value**2:.3f})')

# Spearman correlation
rho = results['secondary_analysis']['spearman']['rho']
p_rho = results['secondary_analysis']['spearman']['p_value']

ax.set_xlabel('Artifact Count (0-3)', fontsize=12, fontweight='bold')
ax.set_ylabel('Coefficient of Variation (CV)', fontsize=12, fontweight='bold')
ax.set_title(f'Dose-Response: Artifact Count vs Performance Variance\n'
             f'Spearman ρ = {rho:.3f}, p = {p_rho:.3f}',
             fontsize=13, fontweight='bold')
ax.set_xticks([0, 1, 2, 3])
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)

# Add color legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='blue', edgecolor='black', label='High Artifact (≥2)'),
    Patch(facecolor='red', edgecolor='black', label='Low Artifact (<2)')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig(figures_dir / "03_dose_response.png", bbox_inches='tight')
print("✓ Figure 3: Dose-response scatter plot saved")
plt.close()

# ============================================================================
# Figure 4: Summary Statistics Table
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 4))
ax.axis('off')

summary_data = []
for group in ['high', 'low']:
    group_data = df[df['artifact_group'] == group]['cv']
    summary_data.append([
        'High Artifact' if group == 'high' else 'Low Artifact',
        len(group_data),
        f"{group_data.mean():.4f}",
        f"{group_data.median():.4f}",
        f"{group_data.std():.4f}",
        f"{group_data.min():.4f}",
        f"{group_data.max():.4f}"
    ])

# Add overall statistics
all_data = df['cv']
summary_data.append([
    'Overall',
    len(all_data),
    f"{all_data.mean():.4f}",
    f"{all_data.median():.4f}",
    f"{all_data.std():.4f}",
    f"{all_data.min():.4f}",
    f"{all_data.max():.4f}"
])

table = ax.table(
    cellText=summary_data,
    colLabels=['Group', 'N', 'Mean CV', 'Median CV', 'SD', 'Min', 'Max'],
    cellLoc='center',
    loc='center',
    bbox=[0, 0, 1, 1]
)

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

# Style header
for i in range(7):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Style rows
for i in range(1, 4):
    for j in range(7):
        if i == 3:
            table[(i, j)].set_facecolor('#E8F5E9')
        else:
            table[(i, j)].set_facecolor('#F5F5F5' if i % 2 == 0 else 'white')

ax.set_title('Summary Statistics: Performance Variance by Group',
             fontsize=13, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(figures_dir / "04_summary_statistics.png", bbox_inches='tight')
print("✓ Figure 4: Summary statistics table saved")
plt.close()

# ============================================================================
# Figure 5: Hypothesis Testing Results Summary
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')

test_results = [
    ['Mann-Whitney U Test',
     f"{results['primary_analysis']['mann_whitney']['statistic']:.2f}",
     f"{results['primary_analysis']['mann_whitney']['p_value']:.4f}",
     "FAIL" if results['primary_analysis']['mann_whitney']['p_value'] >= 0.05 else "PASS",
     "p ≥ 0.05 (not significant)"],
    ['Cohen\'s d Effect Size',
     f"{results['primary_analysis']['cohens_d']['effect_size']:.3f}",
     "N/A",
     "FAIL" if results['primary_analysis']['cohens_d']['effect_size'] < 0.5 else "PASS",
     f"{results['primary_analysis']['cohens_d']['interpretation']} effect, below threshold"],
    ['Spearman Correlation',
     f"{results['secondary_analysis']['spearman']['rho']:.3f}",
     f"{results['secondary_analysis']['spearman']['p_value']:.4f}",
     "FAIL" if results['secondary_analysis']['spearman']['p_value'] >= 0.05 else "PASS",
     "No dose-response relationship"],
]

table = ax.table(
    cellText=test_results,
    colLabels=['Test', 'Statistic', 'p-value', 'Gate', 'Interpretation'],
    cellLoc='left',
    loc='center',
    bbox=[0, 0.2, 1, 0.7]
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2.5)

# Style header
for i in range(5):
    table[(0, i)].set_facecolor('#2196F3')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Style rows - color by gate result
for i in range(1, 4):
    gate_result = test_results[i-1][3]
    row_color = '#FFCDD2' if gate_result == 'FAIL' else '#C8E6C9'

    for j in range(5):
        table[(i, j)].set_facecolor(row_color)
        if j == 3:  # Gate column
            table[(i, j)].set_text_props(weight='bold')

# Overall gate result
overall_gate = "FAIL" if results['gate_evaluation']['gate_satisfied'] == False else "PASS"
gate_color = 'red' if overall_gate == "FAIL" else 'green'

ax.text(0.5, 0.1, f'Overall Gate Result: {overall_gate}',
        ha='center', va='center', fontsize=16, fontweight='bold',
        color=gate_color,
        bbox=dict(boxstyle='round', facecolor='white', edgecolor=gate_color, linewidth=3))

ax.set_title('Hypothesis Testing Results Summary',
             fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(figures_dir / "05_test_results_summary.png", bbox_inches='tight')
print("✓ Figure 5: Test results summary saved")
plt.close()

print("\n" + "="*60)
print("✅ All figures generated successfully!")
print("="*60)
print(f"Figures saved to: {figures_dir.absolute()}")
print("\nGenerated figures:")
print("  1. 01_gate_metrics.png - Gate metrics comparison (MANDATORY)")
print("  2. 02_cv_distribution.png - CV distribution by group")
print("  3. 03_dose_response.png - Artifact count vs CV scatter")
print("  4. 04_summary_statistics.png - Summary statistics table")
print("  5. 05_test_results_summary.png - Hypothesis testing results")
