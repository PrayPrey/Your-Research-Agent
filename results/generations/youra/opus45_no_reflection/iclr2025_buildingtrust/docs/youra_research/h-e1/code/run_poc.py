"""H-E1: PoC Runner - Validates pipeline with quick evaluation on subset"""

import json
import os
import sys
import numpy as np
from datetime import datetime

from config import MODEL_IDS, MODEL_PARAMS, MODEL_FAMILY, SEED, RESULTS_PATH, ANALYSIS_PATH, FIGURES_DIR
from analyze import evaluate_hypothesis, save_analysis, print_analysis_summary
from visualize import generate_all_figures
from run_eval import eval_textfooler_asr

POC_MODELS = [
    "google/flan-t5-base",
    "google/flan-t5-large",
    "google/flan-t5-xl",
    "microsoft/phi-2",
]


def eval_truthfulqa_mc1_quick(model_id: str) -> float:
    """Quick TruthfulQA eval on 100 questions."""
    import torch
    try:
        from lm_eval import evaluator
        from lm_eval.models.huggingface import HFLM
    except ImportError:
        print(f"  lm-eval not available, using estimated values")
        return None

    print(f"  Quick TruthfulQA MC1 for {model_id}...")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        lm = HFLM(
            pretrained=model_id,
            batch_size=8,
            device=device,
        )

        results = evaluator.simple_evaluate(
            model=lm,
            tasks=["truthfulqa_mc1"],
            batch_size=8,
            limit=100
        )

        acc = results["results"]["truthfulqa_mc1"]["acc,none"]
        print(f"  MC1 Accuracy: {acc:.4f}")

        del lm
        torch.cuda.empty_cache()
        return float(acc)

    except Exception as e:
        print(f"  Error: {e}")
        return None


def run_poc():
    """Run PoC pipeline on small models."""
    print("=" * 70)
    print("H-E1 PoC: Factuality-Robustness Correlation (Quick Validation)")
    print("=" * 70)
    print(f"Start: {datetime.now().isoformat()}")
    print(f"Models: {len(POC_MODELS)} (small models only)")
    print()

    results = {
        "model": [],
        "mc1_acc": [],
        "asr": [],
        "robustness": [],
        "log_params": []
    }

    for i, model_id in enumerate(POC_MODELS):
        print(f"\n[{i+1}/{len(POC_MODELS)}] {model_id}")
        print("-" * 40)

        mc1 = eval_truthfulqa_mc1_quick(model_id)
        asr = eval_textfooler_asr(model_id, num_examples=200)

        if mc1 is not None and asr is not None:
            results["model"].append(model_id)
            results["mc1_acc"].append(mc1)
            results["asr"].append(asr)
            results["robustness"].append(1.0 - asr)
            results["log_params"].append(np.log10(MODEL_PARAMS[model_id]))

    print("\n" + "=" * 60)
    print(f"PoC complete: {len(results['model'])}/{len(POC_MODELS)} models")

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {RESULTS_PATH}")

    print("\n[Phase 2/3] Analyzing Correlations...")
    analysis = evaluate_hypothesis(results)
    save_analysis(analysis, ANALYSIS_PATH)
    print_analysis_summary(analysis)

    print("\n[Phase 3/3] Generating Figures...")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    figures = generate_all_figures(results, analysis, FIGURES_DIR)

    print("\n" + "=" * 70)
    print("POC COMPLETE")
    print("=" * 70)
    print(f"End: {datetime.now().isoformat()}")
    print(f"Gate Result: {analysis['gate_result']}")
    print(f"Action: {analysis['gate_action']}")

    experiment_results = {
        "hypothesis_id": "h-e1",
        "experiment_type": "poc",
        "completed_at": datetime.now().isoformat(),
        "n_models": analysis["n_models"],
        "pearson_r": analysis["pearson_r"],
        "p_value": analysis["p_value"],
        "ci_95": analysis["ci_95"],
        "partial_r": analysis["partial_r"],
        "gate_result": analysis["gate_result"],
        "gate_action": analysis["gate_action"],
        "note": "PoC validation with real TextFooler attacks (200 samples)"
    }

    with open("results/experiment_results.json", "w") as f:
        json.dump(experiment_results, f, indent=2)

    return analysis


if __name__ == "__main__":
    result = run_poc()
    sys.exit(0 if result.get("gate_passed", False) else 1)
