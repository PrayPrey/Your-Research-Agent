import os
import sys
import torch
import yaml
import json
from pathlib import Path

from config import CONFIG
from model import build_resnet50
from data import get_loaders
from analyzer import FeatureProbeAnalyzer
from commitment import check_commitment
from visualize import (plot_probe_accuracy_timeline, plot_gate_metrics_comparison,
                       plot_commitment_summary)

def main():
    torch.manual_seed(CONFIG.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Verify checkpoints exist
    checkpoint_dir = Path(__file__).parent / CONFIG.h_m1_checkpoint_dir
    epochs_to_analyze = CONFIG.get_analysis_epochs()
    for epoch in epochs_to_analyze:
        ckpt = checkpoint_dir / CONFIG.checkpoint_pattern.format(epoch=epoch)
        if not ckpt.exists():
            print(f"ERROR: Checkpoint not found: {ckpt}")
            sys.exit(1)
    print(f"All checkpoints verified: epochs {epochs_to_analyze}")

    # Load data
    print("Loading Waterbirds dataset...")
    loaders = get_loaders("waterbirds", CONFIG.batch_size, CONFIG.data_root)
    print(f"Val samples: {len(loaders['val'].dataset)}, Test samples: {len(loaders['test'].dataset)}")

    # Initialize analyzer
    analyzer = FeatureProbeAnalyzer(
        model_builder=lambda: build_resnet50(num_classes=2, pretrained=False),
        checkpoint_dir=str(checkpoint_dir),
        crystallization_epoch=CONFIG.crystallization_epoch,
        final_epoch=CONFIG.final_epoch,
        hidden_dim=CONFIG.feature_dim,
        probe_lr=CONFIG.probe_lr,
        probe_iterations=CONFIG.probe_iterations,
        checkpoint_pattern=CONFIG.checkpoint_pattern
    )

    # Run analysis
    print(f"\nAnalyzing epochs {CONFIG.crystallization_epoch} to {CONFIG.final_epoch}...")
    history = analyzer.analyze_all(loaders['val'], loaders['test'], device)

    # Check commitment
    commitment_result = check_commitment(
        history['spurious_acc_history'],
        history['core_acc_history'],
        CONFIG.noise_margin,
        CONFIG.core_suppression_threshold
    )

    # Print results
    print("\n" + "="*50)
    print("COMMITMENT ANALYSIS RESULTS")
    print("="*50)
    print(f"Spurious Initial: {commitment_result['spurious_initial']:.4f}")
    print(f"Spurious Final:   {commitment_result['spurious_final']:.4f}")
    print(f"Core Final:       {commitment_result['core_final']:.4f}")
    print(f"Spurious Trend:   {commitment_result['spurious_trend']}")
    print(f"Committed:        {commitment_result['committed']}")
    print(f"Core Suppressed:  {commitment_result['core_suppressed']}")
    print(f"\nGATE RESULT: {'PASS' if commitment_result['gate_pass'] else 'FAIL'}")
    print("="*50)

    # Save outputs
    os.makedirs(CONFIG.output_dir, exist_ok=True)
    os.makedirs(CONFIG.figures_dir, exist_ok=True)

    results = {
        'epochs': history['epochs'],
        'spurious_acc_history': history['spurious_acc_history'],
        'core_acc_history': history['core_acc_history'],
        'commitment': commitment_result,
        'config': {
            'crystallization_epoch': CONFIG.crystallization_epoch,
            'final_epoch': CONFIG.final_epoch,
            'noise_margin': CONFIG.noise_margin,
            'core_threshold': CONFIG.core_suppression_threshold,
            'probe_lr': CONFIG.probe_lr,
            'probe_iterations': CONFIG.probe_iterations
        }
    }

    with open(f"{CONFIG.output_dir}/{CONFIG.results_file}", 'w') as f:
        yaml.dump(results, f, default_flow_style=False)

    # Generate figures
    plot_probe_accuracy_timeline(
        history['spurious_acc_history'], history['core_acc_history'],
        history['epochs'], CONFIG.crystallization_epoch,
        f"{CONFIG.figures_dir}/probe_timeline.png"
    )
    plot_gate_metrics_comparison(commitment_result, f"{CONFIG.figures_dir}/gate_comparison.png")
    plot_commitment_summary(
        history['spurious_acc_history'], history['core_acc_history'],
        history['epochs'], commitment_result,
        f"{CONFIG.figures_dir}/commitment_summary.png"
    )

    print(f"\nOutputs saved to {CONFIG.output_dir}/")
    print(f"Figures saved to {CONFIG.figures_dir}/")

    return commitment_result['gate_pass']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
