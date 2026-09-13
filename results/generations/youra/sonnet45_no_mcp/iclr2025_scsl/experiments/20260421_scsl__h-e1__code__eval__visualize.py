"""
Visualization module for H-E1
Generates 5 required figures
"""

import matplotlib.pyplot as plt
import numpy as np
import os


def plot_alignment_comparison(erm_alignment, dro_alignment, save_path):
    """
    Figure 1: Alignment comparison bar chart.

    Args:
        erm_alignment: ERM alignment value
        dro_alignment: DRO alignment value
        save_path: Output path
    """
    plt.figure(figsize=(8, 6))

    methods = ['ERM', 'Group-DRO']
    alignments = [erm_alignment, dro_alignment]
    colors = ['red', 'blue']

    plt.bar(methods, alignments, color=colors, alpha=0.7)
    plt.ylabel('Alignment A(w)', fontsize=12)
    plt.title('Curvature Subspace Alignment: ERM vs Group-DRO', fontsize=14)
    plt.ylim(0, 1.0)
    plt.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_hessian_spectrum(eigenvalues, bulk_edge, method_name, save_path):
    """
    Figure 2/3: Hessian eigenvalue spectrum with MP bulk edge.

    Args:
        eigenvalues: Array of eigenvalues
        bulk_edge: MP bulk edge value
        method_name: 'ERM' or 'Group-DRO'
        save_path: Output path
    """
    plt.figure(figsize=(10, 6))

    plt.plot(eigenvalues, 'o-', markersize=4, alpha=0.7, label='Eigenvalues')
    plt.axhline(y=bulk_edge, color='red', linestyle='--', linewidth=2,
                label=f'MP Bulk Edge (λ+ = {bulk_edge:.2f})')

    plt.xlabel('Index', fontsize=12)
    plt.ylabel('Eigenvalue', fontsize=12)
    plt.title(f'Hessian Spectrum: {method_name}', fontsize=14)
    plt.yscale('log')
    plt.legend()
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_training_curves(history_erm, history_dro, save_path):
    """
    Figure 4: Training curves (loss and accuracy).

    Args:
        history_erm: ERM training history dict
        history_dro: DRO training history dict
        save_path: Output path
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    epochs_erm = range(1, len(history_erm['train_loss']) + 1)
    epochs_dro = range(1, len(history_dro['train_loss']) + 1)

    # Train loss
    axes[0, 0].plot(epochs_erm, history_erm['train_loss'], 'r-', label='ERM')
    axes[0, 0].plot(epochs_dro, history_dro['train_loss'], 'b-', label='Group-DRO')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Train Loss')
    axes[0, 0].set_title('Training Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    # Val loss
    axes[0, 1].plot(epochs_erm, history_erm['val_loss'], 'r-', label='ERM')
    axes[0, 1].plot(epochs_dro, history_dro['val_loss'], 'b-', label='Group-DRO')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Val Loss')
    axes[0, 1].set_title('Validation Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    # Val accuracy
    axes[1, 0].plot(epochs_erm, history_erm['val_acc'], 'r-', label='ERM')
    axes[1, 0].plot(epochs_dro, history_dro['val_acc'], 'b-', label='Group-DRO')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('Val Accuracy (%)')
    axes[1, 0].set_title('Validation Accuracy')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    # Worst-group accuracy
    axes[1, 1].plot(epochs_erm, history_erm['val_worst_group_acc'], 'r-', label='ERM')
    axes[1, 1].plot(epochs_dro, history_dro['val_worst_group_acc'], 'b-', label='Group-DRO')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('Worst-Group Accuracy (%)')
    axes[1, 1].set_title('Worst-Group Accuracy')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_group_accuracy_heatmap(group_accs_erm, group_accs_dro, save_path):
    """
    Figure 5: Group accuracy heatmap (4 groups × 2 methods).

    Args:
        group_accs_erm: List of 4 group accuracies for ERM
        group_accs_dro: List of 4 group accuracies for DRO
        save_path: Output path
    """
    plt.figure(figsize=(8, 6))

    data = np.array([group_accs_erm, group_accs_dro])

    im = plt.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

    # Labels
    plt.xticks(range(4), ['Group 0', 'Group 1', 'Group 2', 'Group 3'])
    plt.yticks(range(2), ['ERM', 'Group-DRO'])
    plt.xlabel('Group', fontsize=12)
    plt.ylabel('Method', fontsize=12)
    plt.title('Group-wise Accuracy (%)', fontsize=14)

    # Annotate cells
    for i in range(2):
        for j in range(4):
            text = plt.text(j, i, f'{data[i, j]:.1f}',
                           ha='center', va='center', color='black', fontsize=12)

    plt.colorbar(im, label='Accuracy (%)')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_worst_group_vs_alignment(
    erm_worst_group, erm_alignment,
    dro_worst_group, dro_alignment,
    save_path
):
    """
    Figure 6: Scatter plot of worst-group accuracy vs alignment.

    Args:
        erm_worst_group: ERM worst-group accuracy
        erm_alignment: ERM alignment
        dro_worst_group: DRO worst-group accuracy
        dro_alignment: DRO alignment
        save_path: Output path
    """
    plt.figure(figsize=(8, 6))

    plt.scatter([erm_alignment], [erm_worst_group], s=200, c='red',
                marker='o', alpha=0.7, label='ERM', edgecolors='black', linewidths=2)
    plt.scatter([dro_alignment], [dro_worst_group], s=200, c='blue',
                marker='s', alpha=0.7, label='Group-DRO', edgecolors='black', linewidths=2)

    plt.xlabel('Alignment A(w)', fontsize=12)
    plt.ylabel('Worst-Group Accuracy (%)', fontsize=12)
    plt.title('Worst-Group Accuracy vs Curvature Alignment', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_all_figures(results, figures_dir, viz_config):
    """
    Generate all 5 required figures.

    Args:
        results: Dict with all experimental results
        figures_dir: Output directory
        viz_config: Visualization configuration
    """
    os.makedirs(figures_dir, exist_ok=True)

    # Figure 1: Alignment comparison
    plot_alignment_comparison(
        results['erm_alignment'],
        results['dro_alignment'],
        os.path.join(figures_dir, viz_config['fig_alignment'])
    )

    # Figure 2: ERM spectrum
    plot_hessian_spectrum(
        results['erm_eigenvalues'],
        results['erm_bulk_edge'],
        'ERM',
        os.path.join(figures_dir, viz_config['fig_spectrum_erm'])
    )

    # Figure 3: DRO spectrum
    plot_hessian_spectrum(
        results['dro_eigenvalues'],
        results['dro_bulk_edge'],
        'Group-DRO',
        os.path.join(figures_dir, viz_config['fig_spectrum_dro'])
    )

    # Figure 4: Training curves
    plot_training_curves(
        results['erm_history'],
        results['dro_history'],
        os.path.join(figures_dir, viz_config['fig_training'])
    )

    # Figure 5: Group accuracy heatmap
    plot_group_accuracy_heatmap(
        results['erm_group_accs'],
        results['dro_group_accs'],
        os.path.join(figures_dir, viz_config['fig_heatmap'])
    )

    print(f"✓ Generated 5 figures in {figures_dir}")
