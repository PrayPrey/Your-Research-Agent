"""Main experiment runner for h-e1: UQ for Selective Prediction."""
import os
import json
from pathlib import Path

from data.loader import TruthfulQALoader
from models.llama_wrapper import LlamaWrapper
from uq.methods import TemperatureScaling, ConformalPrediction, MCDropout
from eval.metrics import compute_auroc, compute_spearman, check_gate, compute_roc_data
from visualize import plot_auroc_comparison, plot_uncertainty_distributions, plot_roc_curves


def main():
    """Run UQ experiment on TruthfulQA."""
    print("=" * 80)
    print("H-E1: Uncertainty Quantification for Selective Prediction")
    print("=" * 80)

    # === 1. Load Data ===
    print("\n[1/7] Loading TruthfulQA dataset...")
    loader = TruthfulQALoader(seed=42)
    cal_data, test_data = loader.load_and_split(cal_ratio=0.4)
    print(f" Calibration: {len(cal_data)} questions")
    print(f" Test: {len(test_data)} questions")

    # === 2. Load Model ===
    print("\n[2/7] Loading Llama-3.1-8B-Instruct...")
    model = LlamaWrapper()

    # === 3. Generate Answers ===
    print("\n[3/7] Generating answers for test set...")
    test_questions = [q["question"] for q in test_data]
    test_results = model.generate(test_questions, batch_size=8)
    test_answers = [answer for answer, _ in test_results]
    test_logits = [logits for _, logits in test_results]

    # Label correctness
    for i, q in enumerate(test_data):
        label = loader.label_correctness(
            q["question"],
            test_answers[i],
            q.get("correct_answers", [])
        )
        q["label"] = label
        q["answer"] = test_answers[i]

    labels = [q["label"] for q in test_data]
    print(f" Generated {len(test_answers)} answers")
    print(f" Accuracy: {1 - sum(labels)/len(labels):.2%}")

    # === 4. Calibrate UQ Methods ===
    print("\n[4/7] Calibrating UQ methods...")

    # Generate calibration answers
    cal_questions = [q["question"] for q in cal_data]
    cal_results = model.generate(cal_questions, batch_size=8)
    cal_logits = [logits for _, logits in cal_results]
    cal_labels = [
        loader.label_correctness(q["question"], answer, q.get("correct_answers", []))
        for q, (answer, _) in zip(cal_data, cal_results)
    ]

    # Temperature Scaling
    temp_scaling = TemperatureScaling()
    T = temp_scaling.calibrate(cal_logits, cal_labels)
    print(f" Temperature Scaling: T={T:.3f}")

    # Conformal Prediction
    conformal = ConformalPrediction(alpha=0.1)
    threshold = conformal.calibrate(cal_logits, cal_labels)
    print(f" Conformal Prediction: threshold={threshold:.3f}")

    # === 5. Compute Uncertainties ===
    print("\n[5/7] Computing uncertainties...")

    uncertainties_by_method = {}

    # Temperature Scaling
    uncertainties_by_method["temp_scaling"] = [
        temp_scaling.compute_uncertainty(logits, T) for logits in test_logits
    ]

    # Conformal Prediction
    uncertainties_by_method["conformal"] = [
        conformal.compute_uncertainty(logits) for logits in test_logits
    ]

    # MC Dropout (k=1, 3, 5, 10)
    for k in [1, 3, 5, 10]:
        print(f" MC Dropout k={k}...")
        mc = MCDropout(k=k)
        uncertainties_by_method[f"mc_k{k}"] = mc.compute_uncertainty(
            test_questions, model.model, model.tokenizer
        )

    # === 6. Evaluate AUROC ===
    print("\n[6/7] Computing AUROC...")

    auroc_scores = {}
    roc_data_by_method = {}

    for method, uncertainties in uncertainties_by_method.items():
        auroc = compute_auroc(labels, uncertainties)
        spearman_rho = compute_spearman(uncertainties, labels)
        auroc_scores[method] = auroc
        roc_data_by_method[method] = compute_roc_data(labels, uncertainties)

        print(f" {method:15s}: AUROC={auroc:.3f}, Spearman={spearman_rho:.3f}")

    # === 7. Check Gate & Visualize ===
    print("\n[7/7] Checking gate condition...")

    gate_passed = check_gate(auroc_scores, threshold=0.70)
    max_auroc = max(auroc_scores.values())
    best_method = max(auroc_scores, key=auroc_scores.get)

    print(f" Max AUROC: {max_auroc:.3f} ({best_method})")
    print(f" Gate (AUROC >= 0.70): {'PASSED ✓' if gate_passed else 'FAILED ✗'}")

    # Save results
    results = {
        "auroc_scores": auroc_scores,
        "gate_passed": gate_passed,
        "max_auroc": max_auroc,
        "best_method": best_method,
        "test_accuracy": 1 - sum(labels)/len(labels),
        "calibration_size": len(cal_data),
        "test_size": len(test_data)
    }

    results_path = "experiment_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n Results saved to {results_path}")

    # Generate figures
    print("\n Generating figures...")
    os.makedirs("figures", exist_ok=True)

    plot_auroc_comparison(auroc_scores, 0.70, "figures/auroc_comparison.png")
    plot_uncertainty_distributions(test_data, uncertainties_by_method, "figures/uncertainty_distributions.png")
    plot_roc_curves(roc_data_by_method, "figures/roc_curves.png")

    print(f" Figures saved to figures/")

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
