"""Entry point: orchestrates all pipeline stages in order."""
import json
import pathlib
import sys
import os

# Ensure code/ is on sys.path when invoked from any cwd
_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE))

from config import FIGURES_DIR, RESULTS_DIR
from precondition_check import run_all_checks
from evaluator import evaluate_both_models
from metrics import evaluate_hypothesis
from figures import generate_all


def main() -> None:
    print("=" * 60)
    print("H-E1: Corpus Curation Generalization Balance — PoC Pipeline")
    print("=" * 60)

    # Stage 1: Preconditions
    print("\n[STAGE 1] Precondition checks...")
    run_all_checks()

    # Stage 2 & 3: Evaluate both models
    print("\n[STAGE 2/3] Evaluating both models (resume-safe)...")
    pythia_results, olmo_results = evaluate_both_models()

    # Stage 4: Compute metrics
    print("\n[STAGE 4] Computing metrics...")
    metrics = evaluate_hypothesis(pythia_results, olmo_results)

    # Stage 5: Figures
    print("\n[STAGE 5] Generating figures...")
    generate_all(pythia_results, olmo_results, metrics, out_dir=FIGURES_DIR)

    # Stage 6: Save results
    results_out = pathlib.Path(RESULTS_DIR) / "metrics_summary.json"
    results_out.parent.mkdir(parents=True, exist_ok=True)

    # Strip bootstrap_diffs list (large) from JSON but keep summary
    metrics_to_save = {k: v for k, v in metrics.items() if k != "bootstrap"}
    metrics_to_save["bootstrap_summary"] = {
        "mean_diff": metrics["bootstrap"]["mean_diff"],
        "ci_95": metrics["bootstrap"]["ci_95"],
        "p_value": metrics["bootstrap"]["p_value"],
    }
    with open(results_out, "w") as f:
        json.dump(metrics_to_save, f, indent=2)
    print(f"\n[RESULT] Metrics saved to {results_out}")

    # Print verdict
    print("\n" + "=" * 60)
    print(f"VERDICT: {metrics['verdict']}")
    print(f"Evidence: {metrics['evidence']}")
    print("=" * 60)

    if metrics["verdict"] == "FAILED":
        sys.exit(2)


if __name__ == "__main__":
    main()
