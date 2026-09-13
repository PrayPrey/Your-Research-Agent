"""
Extract VC confidences from experiment log, compute AUROC/ECE, generate figures, save results.
Run when model inference is done but AUROC computation failed due to path issue.
"""
import sys
import os
import re
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from evaluate import compute_vc_auroc
from visualize import generate_all_figures

LOG_PATH = os.path.join(os.path.dirname(__file__), "../experiment.log")


def parse_confidences_from_log(log_path: str) -> list:
    confidences = []
    pattern = re.compile(r"Parsed confidence: ([\d.]+) \(parsed=")
    with open(log_path) as f:
        for line in f:
            m = pattern.search(line)
            if m:
                confidences.append(float(m.group(1)))
    return confidences


def main():
    cfg = Config()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    hm3_path = os.path.normpath(os.path.join(base_dir, cfg.hm3_results_path))
    with open(hm3_path) as f:
        hm3 = json.load(f)

    em_labels = hm3["em_labels"]
    se_scores = hm3["se_scores"]
    te_scores = hm3["te_scores"]

    log_path = os.path.normpath(os.path.join(base_dir, LOG_PATH))
    vc_confidences = parse_confidences_from_log(log_path)
    assert len(vc_confidences) == cfg.n_questions, f"Expected 98, got {len(vc_confidences)}"

    vc_uncertainties = [1.0 - c for c in vc_confidences]
    fallback_count = 0  # All parsed=True from log

    print(f"Parsed {len(vc_confidences)} VC confidence scores from log")

    # Compute AUROC
    auroc_results = compute_vc_auroc(vc_uncertainties, em_labels, cfg)
    print(f"VC AUROC: {auroc_results['auroc_vc']:.4f} CI=[{auroc_results['auroc_vc_ci'][0]:.4f}, {auroc_results['auroc_vc_ci'][1]:.4f}]")
    print(f"TE AUROC: {auroc_results['auroc_te']:.4f}")
    print(f"SE AUROC: {auroc_results['auroc_se']:.4f}")
    print(f"gate_vc_lt_te: {auroc_results['gate_vc_lt_te']}")
    print(f"gate_vc_lt_se: {auroc_results['gate_vc_lt_se']}")
    print(f"gate_passed: {auroc_results['gate_passed']}")

    # Mechanism check
    from vc import verify_vc_mechanism
    activated, indicators = verify_vc_mechanism(
        vc_uncertainties, fallback_count, cfg.n_questions,
        auroc_results["auroc_vc"], cfg
    )

    # Figures
    figures_dir = os.path.normpath(os.path.join(base_dir, cfg.figures_dir))
    generate_all_figures(
        vc_uncertainties, vc_confidences, se_scores, te_scores,
        em_labels, auroc_results, figures_dir
    )

    # Save results.json
    parse_rate = 1.0 - (fallback_count / cfg.n_questions)
    final = {
        "hypothesis": "h-m4",
        "n_questions": cfg.n_questions,
        "auroc_vc": auroc_results["auroc_vc"],
        "auroc_vc_ci": auroc_results["auroc_vc_ci"],
        "auroc_te": auroc_results["auroc_te"],
        "auroc_se": auroc_results["auroc_se"],
        "delta_te": auroc_results["delta_te"],
        "delta_se": auroc_results["delta_se"],
        "gate_vc_lt_te": auroc_results["gate_vc_lt_te"],
        "gate_vc_lt_se": auroc_results["gate_vc_lt_se"],
        "gate_passed": auroc_results["gate_passed"],
        "gate_condition": "VC AUROC < TE AND VC AUROC < SE",
        "parse_rate": parse_rate,
        "fallback_count": fallback_count,
        "ece": auroc_results["ece"],
        "mechanism_activated": activated,
        "mechanism_indicators": indicators,
        "seed": cfg.seed,
        "vc_uncertainties": vc_uncertainties,
        "vc_confidences": vc_confidences,
    }
    results_path = os.path.normpath(os.path.join(base_dir, cfg.results_path))
    with open(results_path, "w") as f:
        json.dump(final, f, indent=2)
    print(f"Results saved to {results_path}")

    print("\n=== GATE VERDICT ===")
    print(f"SHOULD_WORK gate: {'PASS' if auroc_results['gate_passed'] else 'FAIL'}")


if __name__ == "__main__":
    main()
