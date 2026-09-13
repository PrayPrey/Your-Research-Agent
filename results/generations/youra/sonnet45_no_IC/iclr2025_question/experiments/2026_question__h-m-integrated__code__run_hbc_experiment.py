#!/usr/bin/env python3
"""
HBC Experiment Main Script (h-m-integrated)
Implements all 8 tasks (M-1 through M-8) in integrated workflow.

Author: Anonymous
Date: 2026-07-13
Hypothesis: h-m-integrated (MECHANISM)
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from datasets import load_dataset

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import base modules (from h-e1)
from src.consistency_scorer import ConsistencyScorer
from src.conformal_predictor import ConformalPredictor
from src.baseline_model import LlamaGenerator
from src.data_loader import MultiDatasetLoader

# Import new HBC modules
from src.hbc_calibrator import HierarchicalBayesianCalibrator
from src.baseline_suite import BaselineEvaluationWrapper
from src.ece_metric import ECEMetric, ComputationalCostTracker
from src.multi_method_evaluator import MultiMethodEvaluator


def main():
    print("="*80)
    print("HBC EXPERIMENT: h-m-integrated")
    print("="*80)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # Configuration
    config = {
        'model_name': 'meta-llama/Llama-2-7b-hf',
        'n_samples': 5,
        'alpha': 0.1,  # 90% coverage target
        'calibration_size': 500,  # Statistically meaningful calibration set
        'test_size': 817,  # Full TruthfulQA test set (817 samples), use at least 500 for others
        'datasets': ['truthfulqa/truthful_qa', 'Anthropic/hh-rlhf', 'rajpurkar/squad_v2'],
        'seed': 42
    }

    np.random.seed(config['seed'])

    # Step 1: Load datasets (M-1 dependency)
    print("📊 Loading datasets...")
    datasets_dict = {}

    # TruthfulQA
    tqa = load_dataset("truthfulqa/truthful_qa", "generation")
    tqa_samples = tqa["validation"].select(range(min(config['test_size'], len(tqa["validation"]))))
    datasets_dict['TruthfulQA'] = [
        {
            'question': s['question'],
            'correct_answer': s['best_answer'] if 'best_answer' in s else s['correct_answers'][0] if 'correct_answers' in s else "",
            'is_correct_fn': lambda pred, truth: pred.strip().lower() in truth.strip().lower()
        }
        for s in tqa_samples
    ]

    # HH-RLHF
    hh = load_dataset("Anthropic/hh-rlhf")
    hh_samples = hh["test"].select(range(min(config['test_size'], len(hh["test"]))))
    datasets_dict['HH-RLHF'] = [
        {
            'question': s['chosen'].split('\n\n')[0] if '\n\n' in s['chosen'] else s['chosen'][:200],
            'correct_answer': s['chosen'] if 'chosen' in s else "",
            'is_correct_fn': lambda pred, truth: len(pred) > 10  # Simple heuristic
        }
        for s in hh_samples
    ]

    # SQuAD
    squad = load_dataset("rajpurkar/squad_v2")
    squad_samples = squad["validation"].select(range(min(config['test_size'], len(squad["validation"]))))
    datasets_dict['SQuAD'] = [
        {
            'question': s['question'],
            'correct_answer': s['answers']['text'][0] if s['answers']['text'] else "",
            'is_correct_fn': lambda pred, truth: truth.lower() in pred.lower() if truth else False
        }
        for s in squad_samples
    ]

    print(f"✓ Loaded: TruthfulQA ({len(datasets_dict['TruthfulQA'])}), HH-RLHF ({len(datasets_dict['HH-RLHF'])}), SQuAD ({len(datasets_dict['SQuAD'])})")

    # Step 2: Initialize base modules (from h-e1)
    print("\n🤖 Initializing models...")
    generator = LlamaGenerator(model_name=config['model_name'], device='cuda')
    consistency_scorer = ConsistencyScorer(device='cuda')
    conformal_predictor = ConformalPredictor(alpha=config['alpha'])

    # Step 3: Initialize HBC (M-1)
    print("\n🔧 Initializing HBC...")
    hbc = HierarchicalBayesianCalibrator(
        consistency_scorer=consistency_scorer,
        conformal_predictor=conformal_predictor,
        generator=generator,
        alpha=config['alpha'],
        max_iterations=3,
        n_samples=config['n_samples']
    )

    # Step 4: Initialize baselines (M-2)
    print("🔧 Initializing baselines...")
    baselines = BaselineEvaluationWrapper(
        consistency_scorer=consistency_scorer,
        conformal_predictor=conformal_predictor,
        generator=generator
    )

    # Step 5: Calibration on first dataset
    print("\n📋 Calibration Phase...")
    calibration_data = datasets_dict['TruthfulQA'][:config['calibration_size']]

    print("  HBC calibration...")
    hbc.calibrate(calibration_data)

    print("  Baseline calibration...")
    baselines.calibrate_all(calibration_data)

    # Step 6: Initialize evaluator (M-3, M-4)
    print("\n📊 Initializing evaluator...")
    ece_metric = ECEMetric(n_bins=10)
    cost_tracker = ComputationalCostTracker()
    evaluator = MultiMethodEvaluator(hbc, baselines, ece_metric, cost_tracker)

    # Step 7: Evaluation on all datasets (M-4)
    print("\n🧪 Evaluation Phase...")
    test_datasets = {
        'TruthfulQA': datasets_dict['TruthfulQA'][config['calibration_size']:],
        'HH-RLHF': datasets_dict['HH-RLHF'][:config['test_size']],
        'SQuAD': datasets_dict['SQuAD'][:config['test_size']]
    }

    results = evaluator.evaluate_all_methods(test_datasets)

    # Step 8: Gate validation (M-4)
    gate_result = evaluator.validate_gate()

    # Step 9: Save results (M-8)
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    results_file = output_dir / "experiment_results.json"
    evaluator.save_results(str(results_file))

    # Save gate result
    gate_file = output_dir / "gate_validation.json"
    with open(gate_file, 'w') as f:
        json.dump({
            'gate_type': gate_result.gate_type,
            'passed': gate_result.passed,
            'criteria': gate_result.criteria_results,
            'failure_reason': gate_result.failure_reason,
            'recommendations': gate_result.recommendations
        }, f, indent=2)

    # Final summary
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)
    print(f"Gate result: {'✅ PASS' if gate_result.passed else '❌ FAIL'}")
    print(f"Results: {results_file}")
    print(f"Gate: {gate_file}")
    print(f"End time: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
