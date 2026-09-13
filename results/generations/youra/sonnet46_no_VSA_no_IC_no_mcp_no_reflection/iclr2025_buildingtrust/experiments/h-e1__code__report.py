"""FR-6: Validation & Reporting — PASS/FAIL determination and summary.json."""
import json
import os

PASS_THRESHOLD_ACC = 0.67
PASS_THRESHOLD_P   = 0.05
FAIL_THRESHOLD_ACC = 0.50


def determine_outcome(loo_accuracy: float, p_value: float) -> str:
    if loo_accuracy >= PASS_THRESHOLD_ACC and p_value <= PASS_THRESHOLD_P:
        return "PASS"
    if loo_accuracy < FAIL_THRESHOLD_ACC:
        return "FAIL"
    return "INCONCLUSIVE"


def print_report(results: dict, outcome: str) -> None:
    sensitivity = results.get("sensitivity", {})
    print("\n" + "="*60)
    print("H-E1 CLASSIFICATION REPORT")
    print("="*60)
    print(f"Models evaluated : {results.get('n_models', '?')} ({results.get('n_pairs', '?')} pairs)")
    print(f"LOO Accuracy (k=1): {results['loo_accuracy']:.4f}")
    print(f"Permutation p-value: {results['p_value']:.4f}")
    print(f"Threshold (acc): ≥ {PASS_THRESHOLD_ACC}")
    print(f"Threshold (p)  : ≤ {PASS_THRESHOLD_P}")
    print(f"\nSensitivity:")
    for k, acc in sensitivity.items():
        print(f"  k={k}: LOO acc = {acc:.4f}")
    perm_scores = results.get("perm_scores", [])
    if perm_scores:
        import numpy as np
        ps = np.array(perm_scores)
        print(f"\nPermutation null distribution:")
        print(f"  mean={ps.mean():.4f}, std={ps.std():.4f}, "
              f"max={ps.max():.4f}")
    print(f"\n{'='*60}")
    print(f"OUTCOME: {outcome}")
    if outcome == "PASS":
        print("→ H-E1 gate SATISFIED. DPO/SFT fingerprint detectable.")
        print("→ Proceed to H-M1 activation.")
    elif outcome == "FAIL":
        print("→ H-E1 FAILS. LOO accuracy below chance level.")
        print("→ Publish as informative null; halt mechanism hypotheses.")
    else:
        print("→ H-E1 INCONCLUSIVE. Accuracy above chance but below threshold.")
        print("→ Explore additional pairs or alternative metrics.")
    print("="*60)


def save_summary(
    results: dict,
    outcome: str,
    output_path: str = "results/summary.json",
) -> None:
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    summary = {
        "hypothesis_id": "H-E1",
        "outcome": outcome,
        "gate": {
            "type": "MUST_WORK",
            "satisfied": outcome == "PASS",
            "criteria": {
                "loo_accuracy_threshold": PASS_THRESHOLD_ACC,
                "p_value_threshold": PASS_THRESHOLD_P,
            },
        },
        "metrics": {
            "loo_accuracy_k1": results["loo_accuracy"],
            "p_value": results["p_value"],
            "sensitivity": results.get("sensitivity", {}),
            "n_models": results.get("n_models"),
            "n_pairs": results.get("n_pairs"),
            "n_sft": results.get("n_sft"),
            "n_dpo": results.get("n_dpo"),
        },
        "permutation_test": {
            "n_permutations": len(results.get("perm_scores", [])),
        },
    }
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Summary saved: {output_path}")


def main(results: dict) -> str:
    outcome = determine_outcome(results["loo_accuracy"], results["p_value"])
    print_report(results, outcome)
    save_summary(results, outcome)
    return outcome


if __name__ == "__main__":
    # Self-test
    results = {
        "loo_accuracy": 0.75,
        "p_value": 0.02,
        "perm_scores": [0.5]*1000,
        "sensitivity": {1: 0.75, 3: 0.67, 5: 0.58},
        "n_models": 12,
        "n_pairs": 6,
        "n_sft": 6,
        "n_dpo": 6,
    }
    outcome = main(results)
    assert outcome == "PASS"
    print("✓ Self-test passed")
