#!/usr/bin/env python3
"""Generate Phase 4 figures from experiment results"""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Load results
with open('../experiment_results.json') as f:
    results = json.load(f)

transformer = results['transformer']
gnn = results['gnn']

# Figure 1: Symmetry Differential Comparison (required)
fig, ax = plt.subplots(figsize=(8, 6))
models = ['Transformer', 'GNN']
differentials = [transformer['differential'], gnn['differential']]
colors = ['#3498db', '#e74c3c']

bars = ax.bar(models, differentials, color=colors, alpha=0.7, edgecolor='black')
ax.axhline(y=0.30, color='red', linestyle='--', linewidth=2, label='GNN Gate (>30%)')
ax.axhline(y=0.10, color='blue', linestyle='--', linewidth=2, label='Transformer Gate (<10%)')

ax.set_ylabel('Symmetry Differential', fontsize=12)
ax.set_title('Symmetry Differential: Transformer vs GNN', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.set_ylim(0, 0.35)

for i, (bar, val) in enumerate(zip(bars, differentials)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{val:.1%}', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('differential_comparison.png', dpi=150, bbox_inches='tight')
plt.savefig('differential_comparison.pdf', bbox_inches='tight')
print("✓ differential_comparison.png/pdf")

# Figure 2: Accuracy Degradation Heatmap
fig, ax = plt.subplots(figsize=(10, 4))
data = np.array([
    [transformer['unperturbed'], transformer['within_layer'], transformer['across_layer']],
    [gnn['unperturbed'], gnn['within_layer'], gnn['across_layer']]
])

im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(['Unperturbed', 'Within-layer', 'Across-layer'])
ax.set_yticks([0, 1])
ax.set_yticklabels(['Transformer', 'GNN'])
ax.set_title('Accuracy Degradation Under Perturbations', fontsize=14, fontweight='bold')

for i in range(2):
    for j in range(3):
        text = ax.text(j, i, f'{data[i, j]:.1%}',
                      ha="center", va="center", color="black", fontsize=12, fontweight='bold')

cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Accuracy', rotation=270, labelpad=20)

plt.tight_layout()
plt.savefig('degradation_heatmap.png', dpi=150, bbox_inches='tight')
plt.savefig('degradation_heatmap.pdf', bbox_inches='tight')
print("✓ degradation_heatmap.png/pdf")

print("\nFigures generated in figures/ folder")
