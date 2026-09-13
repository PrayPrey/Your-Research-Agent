#!/usr/bin/env python3
"""
Main Experiment Script: h-e1 - Oracle Gap Validation
Based on: 03_prd.md, 03_architecture.md, 03_logic.md
"""

import os
import json
import torch
import argparse
from pathlib import Path
import sys

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from config.config import DEFAULT_CONFIG, EVAL_CONFIG, get_task_config
from train.orchestrator import MultiTaskOrchestrator
from eval.metrics import OracleGapCalculator
from visualization.plots import ExperimentVisualizer


def set_seed(seed: int = 42):
    """Set random seeds for reproducibility."""
    import random
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def main():
    parser = argparse.ArgumentParser(description='Run h-e1 Oracle Gap Experiment')
    parser.add_argument('--output_dir', type=str, default='./outputs',
                       help='Output directory')
    parser.add_argument('--batch_size', type=int, default=16,
                       help='Batch size')
    parser.add_argument('--lr', type=float, default=3e-4,
                       help='Learning rate')
    parser.add_argument('--device', type=str, default='cuda',
                       help='Device (cuda or cpu)')
    parser.add_argument('--ranks', type=int, nargs='+', default=[4, 8, 16, 32],
                       help='LoRA ranks to train')
    parser.add_argument('--tasks', type=str, nargs='+', default=None,
                       help='Tasks to train (default: all 17)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    parser.add_argument('--skip_training', action='store_true',
                       help='Skip training and only run evaluation (load from results.json)')

    args = parser.parse_args()

    # Set seed
    set_seed(args.seed)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save configuration
    config = {
        **DEFAULT_CONFIG,
        'output_dir': str(output_dir),
        'batch_size': args.batch_size,
        'learning_rate': args.lr,
        'device': args.device,
        'lora_ranks': args.ranks,
        'seed': args.seed,
    }

    config_file = output_dir / 'config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✓ Configuration saved to {config_file}")

    # Define all 17 tasks
    all_tasks = DEFAULT_CONFIG['glue_tasks'].copy()
    for lang in DEFAULT_CONFIG['xtreme_languages']:
        all_tasks.append(f'xnli_{lang}')
        all_tasks.append(f'pawsx_{lang}')

    # Use specified tasks or all tasks
    tasks = args.tasks if args.tasks else all_tasks

    print("\n" + "="*80)
    print("h-e1: ORACLE GAP VALIDATION EXPERIMENT")
    print("="*80)
    print(f"Tasks: {len(tasks)}")
    print(f"Ranks: {args.ranks}")
    print(f"Total configurations: {len(tasks) * len(args.ranks)}")
    print(f"Device: {args.device}")
    print(f"Output: {output_dir}")
    print("="*80)

    # Check for existing results
    results_file = output_dir / 'results.json'

    if not args.skip_training:
        # STEP 1: Training
        print("\n" + "="*80)
        print("STEP 1: MULTI-TASK TRAINING")
        print("="*80)

        orchestrator = MultiTaskOrchestrator(
            tasks=tasks,
            ranks=args.ranks,
            output_dir=str(output_dir),
            base_model=config['model_name'],
            batch_size=args.batch_size,
            learning_rate=args.lr,
            device=args.device
        )

        results = orchestrator.train_all_configurations()

        # Save results
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Training results saved to {results_file}")

    else:
        # Load existing results
        print("\n✓ Skipping training, loading existing results...")
        if not results_file.exists():
            print(f"✗ ERROR: Results file not found: {results_file}")
            print("   Run without --skip_training first")
            return

        with open(results_file, 'r') as f:
            results = json.load(f)
        print(f"✓ Loaded results from {results_file}")

    # STEP 2: Oracle Gap Evaluation
    print("\n" + "="*80)
    print("STEP 2: ORACLE GAP EVALUATION")
    print("="*80)

    calculator = OracleGapCalculator(
        ref_point=EVAL_CONFIG['hypervolume_ref_point']
    )

    oracle_results = calculator.compute_oracle_gap(results)

    # Save oracle gap results
    oracle_file = output_dir / 'oracle_gap.json'
    with open(oracle_file, 'w') as f:
        json.dump(oracle_results, f, indent=2)
    print(f"\n✓ Oracle gap results saved to {oracle_file}")

    # STEP 3: Generate Figures
    print("\n" + "="*80)
    print("STEP 3: VISUALIZATION")
    print("="*80)

    figures_dir = output_dir.parent.parent / 'figures'
    visualizer = ExperimentVisualizer(str(figures_dir))

    visualizer.save_all_figures(
        results=results,
        oracle_results=oracle_results,
        target_gap=EVAL_CONFIG['target_oracle_gap'] * 100  # Convert to percentage
    )

    # STEP 4: Final Summary
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)

    oracle_gap_pct = oracle_results['oracle_gap_pct']
    target_gap_pct = EVAL_CONFIG['target_oracle_gap'] * 100

    print(f"\nRESULTS:")
    print(f"  Oracle Gap: {oracle_gap_pct:.2f}%")
    print(f"  Target: {target_gap_pct:.2f}%")
    print(f"  Gate Status: {'✓ PASS' if oracle_gap_pct >= target_gap_pct else '✗ FAIL'}")
    print(f"\nOUTPUTS:")
    print(f"  Configuration: {config_file}")
    print(f"  Results: {results_file}")
    print(f"  Oracle Gap: {oracle_file}")
    print(f"  Figures: {figures_dir}/")
    print("="*80)

    # Return exit code based on gate
    if oracle_gap_pct >= target_gap_pct:
        print("\n✓ Hypothesis h-e1 VALIDATED: Oracle gap exists (≥10%)")
        return 0
    else:
        print("\n✗ Hypothesis h-e1 FAILED: Oracle gap below threshold (<10%)")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
