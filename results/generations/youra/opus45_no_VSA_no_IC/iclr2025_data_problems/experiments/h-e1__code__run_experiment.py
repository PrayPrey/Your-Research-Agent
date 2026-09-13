"""Main experiment orchestrator for h-e1: Attribution Method Distinctness."""

import os
import sys
import json
import torch
import numpy as np

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data import get_loaders, get_datasets, get_test_subset, get_train_subset
from model import build_model
from train import train_or_load
from attrib_trak import run_trak
from attrib_tracin import run_tracin
from attrib_kronfluence import run_kronfluence
from evaluate import verify_mathematical_distinctness
from figures import generate_all_figures


def main():
    # Setup
    torch.manual_seed(config.SEED)
    np.random.seed(config.SEED)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    # Data
    print("\n=== Loading data ===")
    train_loader, test_loader = get_loaders()
    train_dataset, test_dataset = get_datasets()
    train_subset = get_train_subset(train_dataset)
    test_subset = get_test_subset(test_dataset, config.EVAL_SUBSET_SIZE)
    print(f"Train subset: {len(train_subset)}, Test subset: {len(test_subset)}")

    # Model + training
    print("\n=== Building/loading model ===")
    model = build_model()
    checkpoints = train_or_load(model, train_loader, device)
    print(f"Using {len(checkpoints)} checkpoints")

    # Attribution methods
    scores_dict = {}

    print("\n=== Running TRAK ===")
    try:
        from torch.utils.data import DataLoader
        train_subset_loader = DataLoader(
            train_subset, batch_size=config.BATCH_SIZE,
            shuffle=False, num_workers=0
        )
        test_subset_loader = DataLoader(
            test_subset, batch_size=config.EVAL_BATCH_SIZE,
            shuffle=False, num_workers=0
        )
        scores_trak = run_trak(model, train_subset_loader, test_subset_loader, checkpoints, device)
        scores_dict['trak'] = scores_trak
        torch.save(scores_trak, os.path.join(config.OUTPUT_DIR, 'scores_trak.pt'))
        print(f"TRAK scores shape: {scores_trak.shape}")
    except Exception as e:
        print(f"TRAK failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== Running TracIn ===")
    try:
        # Reset model for TracIn
        model = build_model()
        scores_tracin = run_tracin(model, train_subset, test_subset, checkpoints, device)
        scores_dict['tracin'] = scores_tracin
        torch.save(scores_tracin, os.path.join(config.OUTPUT_DIR, 'scores_tracin.pt'))
        print(f"TracIn scores shape: {scores_tracin.shape}")
    except Exception as e:
        print(f"TracIn failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== Running Kronfluence ===")
    try:
        # Reset model for Kronfluence
        model = build_model()
        ckpt = torch.load(checkpoints[-1], map_location=device)
        model.load_state_dict(ckpt['model_state_dict'])
        scores_kron = run_kronfluence(model, train_subset, test_subset, device)
        scores_dict['kronfluence'] = scores_kron
        torch.save(scores_kron, os.path.join(config.OUTPUT_DIR, 'scores_kronfluence.pt'))
        print(f"Kronfluence scores shape: {scores_kron.shape}")
    except Exception as e:
        print(f"Kronfluence failed: {e}")
        import traceback
        traceback.print_exc()

    # Evaluation
    print("\n=== Evaluating distinctness ===")
    if len(scores_dict) < 2:
        print(f"ERROR: Only {len(scores_dict)} method(s) succeeded, need at least 2")
        return False

    passed, evidence = verify_mathematical_distinctness(scores_dict, config.CORR_THRESHOLD)

    print(f"\nMax correlation: {evidence['max_correlation']:.4f}")
    print(f"Threshold: {evidence['threshold']}")
    print(f"Verdict: {evidence['verdict']}")
    print(f"Gate passed: {passed}")

    print("\nAll correlations:")
    for pair, corrs in evidence['all_correlations'].items():
        print(f"  {pair}: pearson={corrs['pearson']:.4f}, spearman={corrs['spearman']:.4f}")

    # Save results
    results_path = os.path.join(config.OUTPUT_DIR, 'correlations.json')
    with open(results_path, 'w') as f:
        json.dump(evidence, f, indent=2)
    print(f"\nSaved: {results_path}")

    # Figures
    print("\n=== Generating figures ===")
    generate_all_figures(scores_dict, evidence['all_correlations'])

    print("\n=== EXPERIMENT COMPLETE ===")
    print(f"Gate result: {'PASS' if passed else 'FAIL'}")

    return passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
