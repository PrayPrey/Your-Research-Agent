"""Orchestrator for H-M1 experiment."""
import os
import sys
import argparse
import logging

# Allow imports from this code dir
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from cache_loader import load_or_recompute
from analysis import filter_eligible_questions, run_analysis
from evaluate import verify_mechanism_activated, compute_secondary_metrics, save_results
from visualize import plot_all

BASE = os.path.join(CODE_DIR, "../../../..")
BASE = os.path.abspath(BASE)

CONFIG = {
    "he1_results_dir": os.path.join(BASE, "docs/youra_research/h-e1/results/"),
    "he1_code_dir": os.path.join(BASE, "docs/youra_research/h-e1/code/"),
    "nli_model_id": "cross-encoder/nli-deberta-v3-large",
    "nli_device": 0,
    "n": 98,
    "seed": 42,
    "out_dir": os.path.join(BASE, "docs/youra_research/h-m1/results/"),
    "figures_dir": os.path.join(BASE, "docs/youra_research/h-m1/figures/"),
    "intra_var_threshold": 0.1,
    "min_passing_questions": 15,
    "min_eligible_questions": 20,
    "variance_thresholds": [0.05, 0.1, 0.2, 0.5],
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("h-m1")


def main(cfg: dict = None, smoke_test: bool = False) -> None:
    if cfg is None:
        cfg = CONFIG

    n = 5 if smoke_test else cfg["n"]
    print(f"[H-M1] Starting experiment (n={n}, smoke_test={smoke_test})")

    # Step 1: Load/recompute
    data = load_or_recompute(
        he1_results_dir=cfg["he1_results_dir"],
        he1_code_dir=cfg["he1_code_dir"],
        n=n,
        seed=cfg["seed"],
        nli_model_id=cfg["nli_model_id"],
        nli_device=cfg["nli_device"],
    )
    questions = data["questions"]
    cluster_assignments = data["cluster_assignments"]
    per_sample_te = data["per_sample_te"]
    se_scores = data["se_scores"]

    # Step 2: Analysis
    results = run_analysis(questions, cluster_assignments, per_sample_te, se_scores)

    # Step 3: Gate verification
    primary_pass, indicators = verify_mechanism_activated(
        results,
        intra_var_threshold=cfg["intra_var_threshold"],
        min_passing=cfg["min_passing_questions"],
        min_eligible=cfg["min_eligible_questions"] if not smoke_test else 1,
    )

    # Step 4: Secondary metrics
    secondary = compute_secondary_metrics(results, variance_thresholds=cfg["variance_thresholds"])

    # Step 5: Save results
    save_results(results, indicators, secondary, primary_pass, cfg["out_dir"])

    # Step 6: Visualize
    plot_all(results, indicators, secondary, cfg["figures_dir"], threshold=cfg["intra_var_threshold"])

    verdict = "PASS" if primary_pass else "FAIL"
    print(f"[H-M1] Experiment complete. Gate verdict: {verdict}")
    print(f"[H-M1] n_eligible={indicators['n_eligible_questions']}, "
          f"n_passing={indicators['n_passing_primary_threshold']}, "
          f"mean_var={indicators['mean_variance_overall']:.4f} nats²")

    # Write to experiment.log
    log_path = os.path.join(cfg["out_dir"], "experiment.log")
    with open(log_path, "a") as f:
        f.write(f"VERDICT={verdict}\n")
        f.write(f"n_eligible={indicators['n_eligible_questions']}\n")
        f.write(f"n_passing={indicators['n_passing_primary_threshold']}\n")
        f.write(f"mean_var={indicators['mean_variance_overall']:.6f}\n")
        f.write(f"fraction_passing={indicators['fraction_passing']:.4f}\n")
    return primary_pass, indicators, secondary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    main(smoke_test=args.smoke_test)
    if not args.smoke_test:
        print("[H-M1 self-check] PASS — no crash")
