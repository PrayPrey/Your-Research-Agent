"""Orchestrator — end-to-end H-E1 pipeline."""
import os
import sys
import json
import subprocess

# Resolve paths relative to this file's location
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(CODE_DIR, "results")
FIGURES_DIR = os.path.join(CODE_DIR, "..", "figures")
PAIRS_FILE = os.path.join(CODE_DIR, "model_pairs.json")
SUMMARY_FILE = os.path.join(RESULTS_DIR, "summary.json")

sys.path.insert(0, CODE_DIR)


def load_model_ids(pairs_path: str) -> list[str]:
    with open(pairs_path) as f:
        pairs = json.load(f)
    ids = []
    for p in pairs:
        ids.append(p["sft_model_id"])
        ids.append(p["dpo_model_id"])
    return ids


def main() -> None:
    print("\n" + "="*60)
    print("H-E1: DPO/SFT Alignment Fingerprint Detection")
    print("="*60 + "\n")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    # Step 1: Curate model pairs
    print("Step 1: Model Pair Curation")
    import curate_pairs
    pairs = curate_pairs.main()

    # Step 2: Run benchmark evaluations
    print("\nStep 2: Benchmark Evaluation (lm-evaluation-harness)")
    import run_evaluations_wrapper as eval_wrapper
    eval_wrapper.run_all_evaluations(pairs_path=PAIRS_FILE, results_dir=RESULTS_DIR)

    # Step 3: Build score matrix
    print("\nStep 3: Score Matrix Construction")
    import build_score_matrix
    X, y, model_ids = build_score_matrix.build_matrix(
        pairs_path=PAIRS_FILE, results_dir=RESULTS_DIR
    )

    # Step 4: Classification pipeline
    print("\nStep 4: Classification Pipeline (k-NN LOO + Permutation Test)")
    import classify
    results = classify.main(X, y)

    # Step 5: Visualization
    print("\nStep 5: Visualization")
    import visualize
    visualize.main(X, y, results, model_ids, out_dir=FIGURES_DIR)

    # Step 6: Reporting
    print("\nStep 6: Reporting")
    import report
    report.SUMMARY_FILE = SUMMARY_FILE
    outcome = report.main(results)

    # Save experiment_results.json
    import numpy as np
    exp_results = {
        **results,
        "outcome": outcome,
        "model_ids": model_ids,
        "X": X.tolist(),
        "y": y.tolist(),
    }
    exp_path = os.path.join(CODE_DIR, "..", "experiment_results.json")
    with open(exp_path, "w") as f:
        json.dump(exp_results, f, indent=2)
    print(f"\n✓ experiment_results.json saved: {exp_path}")

    print(f"\n{'='*60}")
    print(f"PIPELINE COMPLETE — OUTCOME: {outcome}")
    print(f"{'='*60}")

    sys.exit(0 if outcome == "PASS" else 1)


if __name__ == "__main__":
    main()
