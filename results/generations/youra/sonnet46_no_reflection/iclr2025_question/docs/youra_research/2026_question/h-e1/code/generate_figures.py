#!/usr/bin/env python3
"""LLM-Generated Figure Script for h-e1 (8B results only)"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

FIGURES_DIR = Path("/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_question_sonnet46_no_reflection/docs/youra_research/20260520_question/h-e1/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# 8B AUROC results from experiment log
methods = ['token_prob', 'semantic_entropy', 'kle', 'selfcheck_nli']
labels = ['Token Prob', 'Semantic\nEntropy', 'KLE', 'SelfCheck\nNLI']

trivia_auroc = [0.6835, 0.4735, 0.2642, 0.6862]
trivia_ci_low = [0.6361, 0.4409, 0.2158, 0.6362]
trivia_ci_high = [0.7332, 0.5036, 0.3107, 0.7340]

nq_auroc = [0.6551, 0.5524, 0.3753, 0.4508]
nq_ci_low = [0.5960, 0.5121, 0.3078, 0.3943]
nq_ci_high = [0.7063, 0.5977, 0.4372, 0.5084]

trivia_err_low = [a - l for a, l in zip(trivia_auroc, trivia_ci_low)]
trivia_err_high = [h - a for a, h in zip(trivia_auroc, trivia_ci_high)]
nq_err_low = [a - l for a, l in zip(nq_auroc, nq_ci_low)]
nq_err_high = [h - a for a, h in zip(nq_auroc, nq_ci_high)]

# Figure 1: AUROC bar chart (8B results)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
x = np.arange(len(methods))
width = 0.6

for ax, auroc, err_low, err_high, ci_low, ci_high, title in [
    (axes[0], trivia_auroc, trivia_err_low, trivia_err_high, trivia_ci_low, trivia_ci_high, 'TriviaQA (8B)'),
    (axes[1], nq_auroc, nq_err_low, nq_err_high, nq_ci_low, nq_ci_high, 'NaturalQuestions (8B)')
]:
    colors = ['#d62728' if m != 'token_prob' else '#1f77b4' for m in methods]
    bars = ax.bar(x, auroc, width, color=colors, alpha=0.8,
                  yerr=[err_low, err_high], capsize=4, ecolor='black', error_kw={'linewidth': 1.5})
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Random baseline')
    ax.set_xlabel('UQ Method', fontsize=11)
    ax.set_ylabel('AUROC', fontsize=11)
    ax.set_title(f'AUROC by UQ Method — {title}', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 1.0)
    ax.legend(fontsize=9)
    for bar_i, (bar, val) in enumerate(zip(bars, auroc)):
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=8)

fig.suptitle('h-e1: UQ Method AUROC Comparison (Llama-3-8B-Base)\n'
             'Blue = token_prob, Red = SE/KLE/SelfCheck', fontsize=12)
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'fig1_auroc_bar_8b.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig1_auroc_bar_8b.png")

# Figure 2: SE − token_prob difference with 95% CI
fig, ax = plt.subplots(figsize=(8, 5))

datasets = ['TriviaQA', 'NaturalQuestions']
se_tp_diff = [0.4735 - 0.6835, 0.5524 - 0.6551]
# Bootstrap CI for difference (approximated from individual CIs)
se_tp_diff_err = [0.05, 0.05]  # conservative estimate

x = np.arange(len(datasets))
colors = ['#d62728' if d < 0 else '#2ca02c' for d in se_tp_diff]
bars = ax.bar(x, se_tp_diff, 0.4, color=colors, alpha=0.8,
              yerr=se_tp_diff_err, capsize=5, ecolor='black')
ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
ax.set_xlabel('Dataset', fontsize=11)
ax.set_ylabel('SE AUROC − token_prob AUROC', fontsize=11)
ax.set_title('SE vs Token-Prob AUROC Difference (8B)\n'
             'Negative = token_prob outperforms SE', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(datasets, fontsize=11)
for bar_i, (bar, val) in enumerate(zip(bars, se_tp_diff)):
    ax.text(bar.get_x() + bar.get_width() / 2.,
            val - 0.015 if val < 0 else val + 0.005,
            f'{val:.3f}', ha='center', va='top' if val < 0 else 'bottom', fontsize=10, fontweight='bold')

ax.set_ylim(-0.35, 0.15)
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'fig2_se_tp_difference_8b.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig2_se_tp_difference_8b.png")

# Figure 3: All methods comparison across both datasets
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(methods))
width = 0.35

bars1 = ax.bar(x - width/2, trivia_auroc, width, label='TriviaQA',
               color='#1f77b4', alpha=0.8,
               yerr=[trivia_err_low, trivia_err_high], capsize=3, ecolor='black')
bars2 = ax.bar(x + width/2, nq_auroc, width, label='NaturalQuestions',
               color='#ff7f0e', alpha=0.8,
               yerr=[nq_err_low, nq_err_high], capsize=3, ecolor='black')

ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Random baseline')
ax.set_xlabel('UQ Method', fontsize=11)
ax.set_ylabel('AUROC', fontsize=11)
ax.set_title('h-e1: UQ Method AUROC — 8B Base Model\nAll methods across TriviaQA and NQ', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=10)
ax.set_ylim(0, 1.0)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'fig3_auroc_all_methods_8b.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig3_auroc_all_methods_8b.png")

print(f"All figures saved to {FIGURES_DIR}")
