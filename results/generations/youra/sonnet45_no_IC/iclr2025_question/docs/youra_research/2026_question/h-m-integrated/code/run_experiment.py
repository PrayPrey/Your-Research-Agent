#!/usr/bin/env python3
"""
H-E1 Experiment: Correlation Between Consistency and Conformal Prediction

This experiment validates the existence of complementary uncertainty signals
between consistency-based (epistemic) and conformal prediction (aleatoric) methods.

Gate Condition: 0.3 ≤ ρ(C,I) ≤ 0.7 on all three datasets
"""

import json
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from datasets import load_dataset
from scipy.stats import pearsonr
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSequenceClassification, logging as hf_logging

# Suppress warnings
warnings.filterwarnings('ignore')
hf_logging.set_verbosity_error()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data_loader import MultiDatasetLoader
from src.baseline_model import LlamaGenerator
from src.consistency_scorer import ConsistencyScorer
from src.conformal_predictor import ConformalPredictor
from src.correlation_analyzer import CorrelationAnalyzer
from src.evaluator import ExperimentEvaluator


def main():
    """Run full experiment pipeline."""

    print("="*80)
    print("H-E1 EXPERIMENT: Consistency-Conformal Correlation")
    print("="*80)
    print()

    # Setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    print()

    # Configuration
    config = {
        "datasets": ["truthful_qa", "Anthropic/hh-rlhf", "squad"],
        "model_name": "meta-llama/Llama-2-7b-hf",
        "num_samples": 5,  # For consistency scoring
        "calibration_size": 1000,
        "test_size": 1000,
        "coverage_target": 0.9,
        "temperature": 0.7,
        "max_tokens": 256,
        "seed": 42
    }

    print("Configuration:")
    for key, val in config.items():
        print(f"  {key}: {val}")
    print()

    # Set seed
    torch.manual_seed(config["seed"])
    np.random.seed(config["seed"])

    # Initialize components
    print("Loading components...")
    print()

    print("1/6 Loading data loader...")
    data_loader = MultiDatasetLoader(
        datasets=config["datasets"],
        tokenizer_name=config["model_name"],
        calibration_size=config["calibration_size"],
        test_size=config["test_size"]
    )

    print("2/6 Loading Llama-2-7B model...")
    generator = LlamaGenerator(
        model_name=config["model_name"],
        device=device
    )

    print("3/6 Loading consistency scorer...")
    consistency_scorer = ConsistencyScorer(
        nli_model="roberta-large-mnli",
        device=device
    )

    print("4/6 Initializing conformal predictor...")
    conformal_predictor = ConformalPredictor(
        coverage_target=config["coverage_target"]
    )

    print("5/6 Initializing correlation analyzer...")
    correlation_analyzer = CorrelationAnalyzer()

    print("6/6 Initializing evaluator...")
    evaluator = ExperimentEvaluator(
        output_folder="outputs",
        figures_folder="../figures"
    )

    print()
    print("="*80)
    print("Running experiment...")
    print("="*80)
    print()

    # Run experiment
    results = evaluator.run_experiment(
        generator=generator,
        consistency_scorer=consistency_scorer,
        conformal_predictor=conformal_predictor,
        correlation_analyzer=correlation_analyzer,
        data_loader=data_loader,
        config=config
    )

    # Save results
    output_path = Path("outputs/experiment_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print("="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)
    print()
    print(f"Results saved to: {output_path}")
    print()

    # Print summary
    print("Summary:")
    print()
    for dataset_name, metrics in results["per_dataset_results"].items():
        print(f"  {dataset_name}:")
        print(f"    Correlation ρ(C,I): {metrics['correlation']:.4f}")
        print(f"    P-value: {metrics['p_value']:.4e}")
        print(f"    Coverage: {metrics['coverage']:.2%}")
        print()

    # Gate check
    gate_satisfied = results["gate_result"]["satisfied"]
    print(f"Gate Status: {'PASS' if gate_satisfied else 'FAIL'}")
    print()

    if gate_satisfied:
        print("✅ HYPOTHESIS VALIDATED: Complementary signals confirmed (0.3 ≤ ρ ≤ 0.7)")
    else:
        print("❌ HYPOTHESIS REJECTED: Correlation outside expected range")

    return 0 if gate_satisfied else 1


if __name__ == "__main__":
    sys.exit(main())
