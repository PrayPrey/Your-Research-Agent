"""
H-M3 Experiment: Method Disagreement Analysis
Gate: min(top-k Jaccard) < 0.70 (>30% disagreement on influential examples)

This experiment tests whether methods with different design paradigms
(random projection vs HVP iteration vs gradient similarity) identify
different training examples as influential.
"""

import os
import sys
import importlib.util
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Tuple, Any
from datetime import datetime

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
he1_code_dir = os.path.abspath(os.path.join(script_dir, '../../h-e1/code'))

# Import local modules FIRST
from config import H3Config, get_config
from jaccard import JaccardAnalyzer
from persistence import PersistenceAnalyzer
from visualize import Visualizer


def _load_he1_module(name, filepath):
    """Load a module from h-e1 code directory using importlib."""
    spec = importlib.util.spec_from_file_location(f"he1_{name}", filepath)
    module = importlib.util.module_from_spec(spec)

    # Temporarily modify sys.modules to resolve h-e1 internal imports
    old_modules = {}
    for mod_name in list(sys.modules.keys()):
        if mod_name in ('config', 'data', 'model', 'attribution'):
            old_modules[mod_name] = sys.modules.pop(mod_name)

    # Add he1 dir to path temporarily
    sys.path.insert(0, he1_code_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(he1_code_dir)
        # Restore old modules
        for mod_name, mod in old_modules.items():
            sys.modules[mod_name] = mod

    return module


# Load h-e1 modules
_he1_config = _load_he1_module('config', os.path.join(he1_code_dir, 'config.py'))
HE1Config = _he1_config.ExperimentConfig

# For attribution, data, model we need them in sys.modules for cross-imports
# Use a subprocess approach or inline the needed functions

# Inline the h-e1 imports by running in h-e1 context
_saved_cwd = os.getcwd()
_saved_path = sys.path.copy()
_saved_modules = {k: v for k, v in sys.modules.items() if k in ('config', 'data', 'model', 'attribution')}

# Clear conflicting modules and change context
for mod_name in ('config', 'data', 'model', 'attribution'):
    sys.modules.pop(mod_name, None)

os.chdir(he1_code_dir)
sys.path.insert(0, he1_code_dir)

# Now import h-e1 modules
from config import ExperimentConfig as HE1Config
from attribution import TRAKMethod, TracInMethod, IFMethod, FastIFMethod, get_method
from data import get_cifar10_loaders
from model import build_model

# Remove h-e1 config from modules to avoid confusion
sys.modules.pop('config', None)

# Restore working directory but keep h-e1 modules in sys.modules (needed for their execution)
os.chdir(_saved_cwd)


def load_model(cfg: H3Config, device: str) -> nn.Module:
    """Load ResNet-18 from h-e1 checkpoint."""
    model = build_model(device)
    checkpoint_path = os.path.join(script_dir, cfg.checkpoint_path)

    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    state_dict = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()
    print(f"Loaded model from {checkpoint_path}")
    return model


def load_data(cfg: H3Config) -> Tuple[DataLoader, DataLoader]:
    """Load CIFAR-10 subsets using H-E1 configuration."""
    he1_cfg = HE1Config(
        data_root=os.path.join(he1_code_dir, 'data'),
        train_subset_size=cfg.train_subset_size,
        loo_test_size=cfg.loo_test_size,
        subset_seed=cfg.subset_seed,
        train_batch_size=cfg.train_batch_size,
        test_batch_size=cfg.test_batch_size,
    )

    train_loader, test_loader, _ = get_cifar10_loaders(he1_cfg)
    print(f"Loaded data: {len(train_loader.dataset)} train, {len(test_loader.dataset)} test samples")
    return train_loader, test_loader


def load_or_compute_scores(
    cfg: H3Config,
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    device: str,
) -> Dict[int, Dict[str, np.ndarray]]:
    """
    Compute or load cached attribution scores.

    Returns: {budget: {method: scores[n_test, n_train]}}
    Note: H-E1 returns [n_train, n_test]; we transpose to [n_test, n_train].
    """
    cache_path = os.path.join(cfg.results_dir, 'attribution_scores.npz')

    # Try loading from cache
    if os.path.exists(cache_path):
        print(f"Loading cached scores from {cache_path}")
        data = np.load(cache_path)

        results = {b: {} for b in cfg.compute_budgets}
        for key in data.files:
            parts = key.split('_')
            method = parts[0]
            budget = int(parts[1])
            if budget in results:
                results[budget][method] = data[key]

        # Verify all methods/budgets present
        complete = all(
            len(results[b]) == len(cfg.methods)
            for b in cfg.compute_budgets
        )
        if complete:
            return results
        print("Cache incomplete, recomputing...")

    # Compute scores
    print("Computing attribution scores...")
    he1_cfg = HE1Config(
        data_root=os.path.join(he1_code_dir, 'data'),
        train_subset_size=cfg.train_subset_size,
        loo_test_size=cfg.loo_test_size,
        subset_seed=cfg.subset_seed,
        results_dir=cfg.results_dir,
        checkpoint_dir=os.path.join(he1_code_dir, 'checkpoints'),
    )

    method_instances = {
        'TRAK': TRAKMethod(),
        'TracIn': TracInMethod(),
        'IF': IFMethod(),
        'FastIF': FastIFMethod(),
    }

    results = {b: {} for b in cfg.compute_budgets}
    save_dict = {}

    for budget in cfg.compute_budgets:
        print(f"\n=== Budget {budget} ===")
        for method_name in cfg.methods:
            print(f"  Computing {method_name}...", end=" ", flush=True)

            seed_scores = []
            for seed in cfg.method_seeds:
                method = method_instances[method_name]
                raw_scores = method.compute_scores(
                    model=model,
                    train_loader=train_loader,
                    test_loader=test_loader,
                    budget=budget,
                    seed=seed,
                    cfg=he1_cfg,
                    device=device,
                )
                # Transpose: [n_train, n_test] -> [n_test, n_train]
                seed_scores.append(raw_scores.T)

            # Average across seeds
            avg_scores = np.mean(seed_scores, axis=0)
            results[budget][method_name] = avg_scores
            save_dict[f"{method_name}_{budget}"] = avg_scores
            print(f"shape={avg_scores.shape}")

    # Save cache
    np.savez(cache_path, **save_dict)
    print(f"\nSaved scores to {cache_path}")

    return results


def evaluate_gate(
    jaccard_by_budget: Dict[int, Dict[str, Any]],
    cfg: H3Config,
) -> Dict[str, Any]:
    """
    Evaluate the SHOULD_WORK gate: min(Jaccard) < 0.70.

    Returns gate result with three-tier classification:
    - PASS: min < 0.70 (>30% disagreement)
    - PARTIAL: 0.70 <= min < 0.80
    - FAIL: min >= 0.80
    """
    per_budget_min = {b: data['min'] for b, data in jaccard_by_budget.items()}
    overall_min = min(per_budget_min.values())
    min_budget = min(per_budget_min, key=per_budget_min.get)

    # Three-tier classification
    if overall_min < cfg.jaccard_threshold:
        gate_result = 'PASS'
        gate_pass = True
    elif overall_min < 0.80:
        gate_result = 'PARTIAL'
        gate_pass = False
    else:
        gate_result = 'FAIL'
        gate_pass = False

    return {
        'gate_pass': gate_pass,
        'gate_result': gate_result,
        'min_jaccard': overall_min,
        'min_budget': min_budget,
        'per_budget_min': per_budget_min,
        'threshold': cfg.jaccard_threshold,
        'details': f"min(Jaccard)={overall_min:.4f} at budget={min_budget}, threshold={cfg.jaccard_threshold}",
    }


def save_jaccard_analysis(
    jaccard_by_budget: Dict[int, Dict[str, Any]],
    methods: list,
    cfg: H3Config,
) -> str:
    """Save Jaccard analysis results to CSV."""
    rows = []
    for budget, data in sorted(jaccard_by_budget.items()):
        matrix = data['matrix']
        for i, m1 in enumerate(methods):
            for j, m2 in enumerate(methods):
                if i < j:
                    rows.append({
                        'budget': budget,
                        'method_1': m1,
                        'method_2': m2,
                        'jaccard': matrix[i, j],
                    })
        rows.append({
            'budget': budget,
            'method_1': 'SUMMARY',
            'method_2': 'min',
            'jaccard': data['min'],
        })
        rows.append({
            'budget': budget,
            'method_1': 'SUMMARY',
            'method_2': 'mean',
            'jaccard': data['mean'],
        })

    df = pd.DataFrame(rows)
    output_path = os.path.join(cfg.results_dir, 'jaccard_analysis.csv')
    df.to_csv(output_path, index=False)
    return output_path


def run(cfg: H3Config) -> Dict[str, Any]:
    """Main experiment orchestrator."""
    print("=" * 60)
    print("H-M3: Method Disagreement Analysis")
    print(f"Gate: min(top-k Jaccard) < {cfg.jaccard_threshold}")
    print("=" * 60)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Ensure output directories exist
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    # Load model and data
    print("\n[1/6] Loading model and data...")
    model = load_model(cfg, device)
    train_loader, test_loader = load_data(cfg)

    # Compute attribution scores
    print("\n[2/6] Computing attribution scores...")
    scores = load_or_compute_scores(cfg, model, train_loader, test_loader, device)

    # Jaccard analysis
    print("\n[3/6] Computing Jaccard similarities...")
    analyzer = JaccardAnalyzer(cfg)
    jaccard_by_budget = analyzer.compute_jaccard_by_budget(
        scores, cfg.compute_budgets, cfg.top_k
    )

    # Print per-budget results
    for budget in sorted(jaccard_by_budget.keys()):
        data = jaccard_by_budget[budget]
        print(f"  Budget {budget}: min={data['min']:.4f}, mean={data['mean']:.4f}")

    # Save Jaccard results
    save_jaccard_analysis(jaccard_by_budget, cfg.methods, cfg)

    # Gate evaluation
    print("\n[4/6] Evaluating gate...")
    gate = evaluate_gate(jaccard_by_budget, cfg)
    print(f"  Gate Result: {gate['gate_result']}")
    print(f"  min(Jaccard) = {gate['min_jaccard']:.4f} (threshold: {gate['threshold']})")
    print(f"  Best budget: {gate['min_budget']}")

    # Persistence analysis
    print("\n[5/6] Running persistence analysis...")
    persistence_analyzer = PersistenceAnalyzer(cfg)
    advantages = persistence_analyzer.compute_relative_advantages(jaccard_by_budget, cfg.methods)
    persistence = persistence_analyzer.check_persistence(advantages)
    paradigm_analysis = persistence_analyzer.compute_paradigm_consistency(jaccard_by_budget, cfg.methods)
    persistence_analyzer.save_results(advantages, persistence, paradigm_analysis, jaccard_by_budget, cfg.methods)

    print(f"  Cross-paradigm mean Jaccard: {paradigm_analysis['cross_paradigm_mean']:.4f}")
    print(f"  Same-paradigm mean Jaccard: {paradigm_analysis['same_paradigm_mean']:.4f}")

    # Visualization
    print("\n[6/6] Generating figures...")
    viz = Visualizer(cfg)

    # Gate figure (heatmap at best budget)
    best_budget = gate['min_budget']
    viz.plot_jaccard_heatmap(
        jaccard_by_budget[best_budget]['matrix'],
        cfg.methods,
        best_budget,
        os.path.join(cfg.figures_dir, 'jaccard_heatmap.png'),
        min_jaccard=gate['min_jaccard'],
    )

    # Jaccard by budget
    viz.plot_jaccard_by_budget(
        jaccard_by_budget,
        cfg.compute_budgets,
        os.path.join(cfg.figures_dir, 'jaccard_by_budget.png'),
    )

    # Top-k overlap for representative test samples
    topk_sets = {m: analyzer.get_topk_indices(scores[best_budget][m], cfg.top_k) for m in cfg.methods}
    viz.plot_topk_overlap(
        topk_sets,
        [0, 50, 99],  # Representative test samples
        os.path.join(cfg.figures_dir, 'topk_overlap.png'),
    )

    # Method ranking persistence
    viz.plot_method_ranking_persistence(
        advantages,
        cfg.compute_budgets,
        cfg.methods,
        os.path.join(cfg.figures_dir, 'ranking_persistence.png'),
    )

    # Paradigm clustering
    viz.plot_paradigm_clustering(
        jaccard_by_budget[best_budget]['matrix'],
        cfg.methods,
        os.path.join(cfg.figures_dir, 'paradigm_clustering.png'),
    )

    # Gate summary figure
    viz.plot_gate_summary(
        jaccard_by_budget,
        cfg.compute_budgets,
        gate,
        os.path.join(cfg.figures_dir, 'gate_summary.png'),
    )

    print("\nFigures saved:")
    for fname in os.listdir(cfg.figures_dir):
        print(f"  - {fname}")

    # Final summary
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate: min(Jaccard) = {gate['min_jaccard']:.4f}")
    print(f"Threshold: {gate['threshold']}")
    print(f"Result: {gate['gate_result']}")

    return {
        **gate,
        'jaccard_by_budget': jaccard_by_budget,
        'advantages': advantages,
        'persistence': persistence,
        'paradigm_analysis': paradigm_analysis,
        'timestamp': datetime.now().isoformat(),
    }


if __name__ == '__main__':
    # Set CUDA device
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
        os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # Use GPU 1 (lowest memory)

    cfg = get_config()
    results = run(cfg)

    print(f"\nGate: min(Jaccard)={results['min_jaccard']:.4f}, Result={results['gate_result']}")
