import sys
import os
import json
import torch

# Add code dir to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from vc import load_vc_model, run_vc_inference, verify_vc_mechanism
from evaluate import load_hm3_baselines, compute_vc_auroc
from visualize import generate_all_figures


def load_artifacts(cfg: Config) -> tuple:
    """
    Loads em_labels + se/te scores from h-m3/results.json.
    Returns (questions, em_labels, se_scores, te_scores).
    """
    # Resolve path relative to this file's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    hm3_path = os.path.join(base_dir, cfg.hm3_results_path)
    hm3_path = os.path.normpath(hm3_path)

    auroc_te, auroc_se, em_labels, se_scores, te_scores = load_hm3_baselines(hm3_path, cfg)

    assert len(em_labels) == cfg.n_questions, (
        f"Expected {cfg.n_questions} questions, got {len(em_labels)} from h-m3 results"
    )

    # Use question IDs as surrogate question strings (actual text not needed for VC prompting)
    # Load actual questions from HuggingFace dataset
    from datasets import load_dataset
    dataset = load_dataset("mandarjoshi/trivia_qa", "rc", split="validation")
    questions = [ex["question"] for ex in dataset.select(range(cfg.n_questions))]

    print(f"Loaded {len(em_labels)} EM labels from h-m3 results")
    print(f"TE AUROC baseline: {auroc_te:.4f}")
    print(f"SE AUROC baseline: {auroc_se:.4f}")

    return questions, em_labels, se_scores, te_scores


def save_results(results: dict, path: str) -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(base_dir, path)
    abs_path = os.path.normpath(abs_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {abs_path}")


def main() -> None:
    import random
    import numpy as np

    cfg = Config()
    random.seed(cfg.seed)
    np.random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)

    print("=" * 60)
    print("H-M4: Verbalized Confidence (VC) Experiment")
    print("=" * 60)

    # 1. Load artifacts
    print("\n[1/7] Loading artifacts...")
    questions, em_labels, se_scores, te_scores = load_artifacts(cfg)

    # 2. Load VC model
    print("\n[2/7] Loading Llama-2-7B-Chat...")
    model, tokenizer = load_vc_model(cfg)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Model loaded on device: {model.device}")

    # 3. Run VC inference
    print(f"\n[3/7] Running VC inference on {cfg.n_questions} questions...")
    vc_uncertainties, fallback_count = run_vc_inference(questions, model, tokenizer, device)
    vc_confidences = [1.0 - u for u in vc_uncertainties]

    # 4. Compute AUROC
    print("\n[4/7] Computing AUROC...")
    auroc_results = compute_vc_auroc(vc_uncertainties, em_labels, cfg)
    print(f"VC AUROC: {auroc_results['auroc_vc']:.4f} (95% CI: [{auroc_results['auroc_vc_ci'][0]:.4f}, {auroc_results['auroc_vc_ci'][1]:.4f}])")
    print(f"TE AUROC: {auroc_results['auroc_te']:.4f}")
    print(f"SE AUROC: {auroc_results['auroc_se']:.4f}")

    # 5. Mechanism verification
    print("\n[5/7] Verifying mechanism...")
    activated, indicators = verify_vc_mechanism(
        vc_uncertainties, fallback_count, cfg.n_questions,
        auroc_results["auroc_vc"], cfg
    )

    # 6. Generate figures
    print("\n[6/7] Generating figures...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.normpath(os.path.join(base_dir, cfg.figures_dir))
    generate_all_figures(
        vc_uncertainties, vc_confidences, se_scores, te_scores,
        em_labels, auroc_results, figures_dir
    )

    # 7. Save results
    print("\n[7/7] Saving results...")
    parse_rate = 1.0 - (fallback_count / cfg.n_questions)

    final_results = {
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

    save_results(final_results, cfg.results_path)

    # Gate verdict
    print("\n" + "=" * 60)
    print("GATE VERDICT (SHOULD_WORK)")
    print(f"  VC AUROC ({auroc_results['auroc_vc']:.4f}) < TE AUROC ({auroc_results['auroc_te']:.4f}): {auroc_results['gate_vc_lt_te']}")
    print(f"  VC AUROC ({auroc_results['auroc_vc']:.4f}) < SE AUROC ({auroc_results['auroc_se']:.4f}): {auroc_results['gate_vc_lt_se']}")
    print(f"  Gate PASSED: {auroc_results['gate_passed']}")
    print(f"  Parse Rate: {parse_rate:.3f} (threshold: {cfg.parse_rate_gate})")
    print(f"  Mechanism Activated: {activated}")
    print("=" * 60)


if __name__ == "__main__":
    main()
