#!/usr/bin/env python3
import argparse
import json
import os
import numpy as np
from tqdm import tqdm
from config import CONFIG
from data import load_truthfulqa, load_halueval_qa
from generate import ResponseGenerator
from detectors import SemanticEntropyDetector, SelfConsistencyDetector
from labels import label_truthfulqa, label_halueval
from evaluate import compute_auroc, check_gate
from plots import plot_gate_comparison, plot_roc_curves, plot_score_distributions

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-samples", type=int, default=None, help="Limit samples per dataset (PoC mode)")
    args = parser.parse_args()
    max_samples = args.max_samples
    print(f"[Config] seed={CONFIG.seed}, n_samples={CONFIG.n_samples}, temp={CONFIG.temperature}")
    os.makedirs(CONFIG.figures_dir, exist_ok=True)

    print("[1/6] Loading datasets...")
    truthfulqa = load_truthfulqa()
    halueval = load_halueval_qa(max_samples=1000)
    if max_samples:
        truthfulqa = truthfulqa[:max_samples]
        halueval = halueval[:max_samples]
        print(f"  [PoC mode] Limited to {max_samples} samples each")
    print(f"  TruthfulQA: {len(truthfulqa)} samples")
    print(f"  HaluEval-QA: {len(halueval)} samples")

    print("[2/6] Loading models...")
    generator = ResponseGenerator(CONFIG.generator_model, CONFIG.seed)
    se_detector = SemanticEntropyDetector(CONFIG.nli_model)
    sc_detector = SelfConsistencyDetector(CONFIG.bertscore_lang)

    all_labels = {}
    all_scores = {}

    # TruthfulQA
    print("[3/6] Processing TruthfulQA...")
    tqa_labels, tqa_se, tqa_sc = [], [], []
    for sample in tqdm(truthfulqa, desc="TruthfulQA"):
        responses = generator.generate_n(sample["question"], CONFIG.n_samples, CONFIG.temperature, CONFIG.max_tokens)
        label = label_truthfulqa(sample, responses)
        se_score = se_detector.compute_entropy(responses, CONFIG.entailment_threshold)
        sc_score = 1.0 - sc_detector.compute_consistency(responses)  # invert: low consistency = high hallucination
        tqa_labels.append(label)
        tqa_se.append(se_score)
        tqa_sc.append(sc_score)
    all_labels["TruthfulQA"] = np.array(tqa_labels)
    all_scores["TruthfulQA"] = {"semantic_entropy": np.array(tqa_se), "self_consistency": np.array(tqa_sc)}

    # HaluEval - use dataset's hallucination label directly
    print("[4/6] Processing HaluEval...")
    he_labels, he_se, he_sc = [], [], []
    for sample in tqdm(halueval, desc="HaluEval"):
        responses = generator.generate_n(sample["question"], CONFIG.n_samples, CONFIG.temperature, CONFIG.max_tokens)
        label = 1 if sample["hallucination"] == "yes" else 0
        se_score = se_detector.compute_entropy(responses, CONFIG.entailment_threshold)
        sc_score = 1.0 - sc_detector.compute_consistency(responses)
        he_labels.append(label)
        he_se.append(se_score)
        he_sc.append(sc_score)
    all_labels["HaluEval"] = np.array(he_labels)
    all_scores["HaluEval"] = {"semantic_entropy": np.array(he_se), "self_consistency": np.array(he_sc)}

    # Evaluate
    print("[5/6] Computing metrics...")
    results = {}
    for dataset in ["TruthfulQA", "HaluEval"]:
        results[dataset] = {}
        for method in ["semantic_entropy", "self_consistency"]:
            auroc, ci_low, ci_high = compute_auroc(all_labels[dataset], all_scores[dataset][method], CONFIG.n_bootstrap)
            results[dataset][method] = {"auroc": auroc, "ci_low": ci_low, "ci_high": ci_high}
            print(f"  {dataset} - {method}: AUROC={auroc:.4f} [{ci_low:.4f}, {ci_high:.4f}]")

    gate_pass = check_gate(results, CONFIG.gate_threshold)
    print(f"\n[Gate] threshold={CONFIG.gate_threshold}, pass={gate_pass}")

    # Save results
    output = {
        "config": {
            "seed": CONFIG.seed,
            "n_samples": CONFIG.n_samples,
            "temperature": CONFIG.temperature,
            "gate_threshold": CONFIG.gate_threshold,
        },
        "results": results,
        "gate_pass": gate_pass,
    }
    with open(CONFIG.results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Saved results to {CONFIG.results_path}")

    # Plots
    print("[6/6] Generating plots...")
    plot_gate_comparison(results, CONFIG.gate_threshold, f"{CONFIG.figures_dir}/gate_comparison.png")
    plot_roc_curves(results, all_labels, all_scores, f"{CONFIG.figures_dir}/roc_curves.png")
    plot_score_distributions(all_scores, all_labels, f"{CONFIG.figures_dir}/score_distributions.png")
    print("  Done.")

if __name__ == "__main__":
    main()
