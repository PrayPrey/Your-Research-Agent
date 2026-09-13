"""Main experiment script for H-M2 width-scaling validation."""

import sys
from pathlib import Path
import json
import argparse

# Add src to path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Use absolute imports to avoid conflicts
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

config_mod = load_module("config", src_path / "config.py")
data_loader_mod = load_module("data_loader", src_path / "data_loader.py")
mlp_mod = load_module("mlp_encoder", src_path / "models" / "mlp_encoder.py")
nfn_mod = load_module("nfn_encoder", src_path / "models" / "nfn_encoder.py")
train_mod = load_module("train", src_path / "train.py")
eval_mod = load_module("evaluate", src_path / "evaluate.py")
viz_mod = load_module("visualize", src_path / "visualize.py")

CONFIG = config_mod.CONFIG
WeightSpaceDataLoader = data_loader_mod.WeightSpaceDataLoader
MLPWeightEncoder = mlp_mod.MLPWeightEncoder
NFNWeightEncoder = nfn_mod.NFNWeightEncoder
WidthScalingTrainer = train_mod.WidthScalingTrainer
WidthScalingEvaluator = eval_mod.WidthScalingEvaluator
WidthScalingVisualizer = viz_mod.WidthScalingVisualizer


def model_factory(model_type: str, width: int):
    """
    Create model instance.

    Args:
        model_type: 'mlp' or 'nfn'
        width: Hidden dimension / output width

    Returns:
        Model instance
    """
    if model_type == 'mlp':
        return MLPWeightEncoder(
            input_dim=CONFIG['mlp_input_dim'],
            hidden_dims=CONFIG['mlp_hidden_dims'],
            output_dim=width
        )
    elif model_type == 'nfn':
        return NFNWeightEncoder(
            input_dim=CONFIG['mlp_input_dim'],  # Same input dimension
            num_layers=CONFIG['nfn_num_layers'],
            hidden_dim=width,
            input_channels=CONFIG['nfn_input_channels']
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def main():
    """Run complete width-scaling experiment."""
    parser = argparse.ArgumentParser(description='H-M2 Width-Scaling Experiment')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip training and only evaluate')
    parser.add_argument('--skip-evaluation', action='store_true',
                       help='Skip evaluation and only visualize')
    args = parser.parse_args()

    print("="*60)
    print("H-M2 WIDTH-SCALING MECHANISM VALIDATION")
    print("="*60)

    # Step 1: Load data
    print("\n[1/4] Loading ModelZoo data...")
    data_loader = WeightSpaceDataLoader(CONFIG)
    dataloaders = data_loader.get_dataloaders()

    # Auto-detect input dimension from data
    sample_batch = next(iter(dataloaders['mlp']['train']))
    input_dim = sample_batch[0].shape[1]
    CONFIG['mlp_input_dim'] = input_dim
    print(f"  Auto-detected input dimension: {input_dim}")
    print(f"  Train samples: {len(dataloaders['mlp']['train'].dataset)}")
    print(f"  Val samples: {len(dataloaders['mlp']['val'].dataset)}")
    print(f"  Test samples: {len(dataloaders['mlp']['test'].dataset)}")

    # Step 2: Train models
    if not args.skip_training:
        print("\n[2/4] Training models across widths...")
        trainer = WidthScalingTrainer(CONFIG)
        training_results = trainer.train_all_widths(model_factory, dataloaders)

        # Check loss matching
        all_matched = all(
            info['matched']
            for info in training_results['loss_matching'].values()
        )
        print(f"\nLoss Matching Status: {'PASS' if all_matched else 'FAIL'}")
        if not all_matched:
            print("Warning: Some widths failed loss matching constraint")
    else:
        print("\n[2/4] Skipping training (--skip-training)")

    # Step 3: Evaluate test errors
    if not args.skip_evaluation:
        print("\n[3/4] Evaluating test errors...")
        evaluator = WidthScalingEvaluator(CONFIG)
        eval_results = evaluator.evaluate_all_widths(
            model_factory,
            dataloaders,
            Path(CONFIG['checkpoint_dir'])
        )

        # Compute gate metrics
        gate_metrics = evaluator.compute_gate_metrics(eval_results['test_errors'])

        # Save gate metrics
        gate_metrics_file = Path(CONFIG['results_dir']) / 'gate_metrics.json'
        with open(gate_metrics_file, 'w') as f:
            json.dump(gate_metrics, f, indent=2)

        print(f"\nGate Status: {'PASS' if gate_metrics['gate_pass'] else 'FAIL'}")
        print(f"  Monotonicity: {'YES' if gate_metrics['monotonicity_satisfied'] else 'NO'}")
        print(f"  All Deltas Positive: {'YES' if gate_metrics['all_deltas_positive'] else 'NO'}")
        print(f"  Mean Δ_test: {gate_metrics['mean_delta']:.4f}")
    else:
        print("\n[3/4] Skipping evaluation (--skip-evaluation)")
        # Load gate metrics if available
        gate_metrics_file = Path(CONFIG['results_dir']) / 'gate_metrics.json'
        if gate_metrics_file.exists():
            with open(gate_metrics_file, 'r') as f:
                gate_metrics = json.load(f)
        else:
            gate_metrics = None

    # Step 4: Generate visualizations
    print("\n[4/4] Generating visualizations...")
    visualizer = WidthScalingVisualizer(CONFIG)
    visualizer.generate_all_visualizations(Path(CONFIG['results_dir']))

    # Final summary
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)

    if gate_metrics:
        print(f"Final Gate Verdict: {'PASS' if gate_metrics['gate_pass'] else 'FAIL'}")
        print(f"\nHypothesis: {'VALIDATED' if gate_metrics['gate_pass'] else 'REJECTED'}")
    else:
        print("Gate metrics not available (evaluation skipped)")

    print(f"\nResults saved to: {CONFIG['results_dir']}")
    print(f"Figures saved to: {CONFIG['figures_dir']}")
    print(f"Checkpoints saved to: {CONFIG['checkpoint_dir']}")


if __name__ == "__main__":
    main()
