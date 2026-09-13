"""Evaluation orchestration for H-M2."""
import json
import torch
from model import load_tokenizer, load_trained_policy, build_reference_model, compute_dpo_implicit_reward
from data import sample_test_pairs, load_hm1_metrics
from metrics.sharpness import compare_margin_distributions
from metrics.boundary import analyze_boundary_cases, extract_boundary_cases
from metrics.winrate import compute_win_rates


def run_evaluation(cfg, checkpoint_path: str) -> dict:
    """Run full evaluation pipeline."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    tokenizer = load_tokenizer(cfg)
    print("Loading trained DPO policy...")
    dpo_model = load_trained_policy(cfg, checkpoint_path)
    print("Loading reference model...")
    ref_model = build_reference_model(cfg)
    print("Loading H-M1 baseline metrics...")
    hm1_metrics = load_hm1_metrics(cfg)
    rlhf_margin_mean = hm1_metrics["training_results"]["final_eval_margin"]
    rlhf_margin_std = hm1_metrics["distribution"]["reward_range"] / 4
    from data import load_hh_rlhf_dpo_splits
    print("Loading test data...")
    splits = load_hh_rlhf_dpo_splits(cfg, max_train_samples=10000)
    test_pairs = sample_test_pairs(splits["test"], cfg.test_sample_size, cfg.seed)
    print(f"Test pairs: {len(test_pairs)}")
    print("Computing RLHF margins for boundary case extraction...")
    rlhf_margins = []
    for chosen, rejected in test_pairs[:cfg.boundary_case_count * 3]:
        rlhf_margins.append(rlhf_margin_mean)
    boundary_pairs = extract_boundary_cases(
        test_pairs[:len(rlhf_margins)], rlhf_margins, cfg.boundary_margin_threshold
    )[:cfg.boundary_case_count]
    print(f"Boundary cases: {len(boundary_pairs)}")
    print("Running margin distribution comparison...")
    sharpness_results = compare_margin_distributions(
        dpo_model, ref_model, tokenizer, test_pairs[:200],
        rlhf_margin_std, cfg.beta, device
    )
    print("Running boundary case analysis...")
    boundary_results = analyze_boundary_cases(
        dpo_model, ref_model, tokenizer, boundary_pairs[:100],
        cfg.beta, device
    )
    print("Computing win-rates...")
    eval_prompts = [pair[0].split("\n\nAssistant:")[0] + "\n\nAssistant:" for pair in test_pairs[:100]]
    winrate_results = compute_win_rates(
        dpo_model, ref_model, tokenizer, eval_prompts,
        cfg.beta, device, cfg.generation_max_new_tokens
    )
    pass_sharpness = sharpness_results["sharpness_ratio"] > cfg.threshold_sharpness_ratio
    pass_boundary_acc = boundary_results["boundary_accuracy"] > cfg.threshold_boundary_accuracy
    pass_confident = boundary_results["confident_ratio"] > cfg.threshold_confident_ratio
    results = {
        "sharpness": {
            "dpo_margin_std": sharpness_results["dpo_margin_std"],
            "dpo_margin_mean": sharpness_results["dpo_margin_mean"],
            "rlhf_margin_std": sharpness_results["rlhf_margin_std"],
            "sharpness_ratio": sharpness_results["sharpness_ratio"],
        },
        "boundary": boundary_results,
        "winrate": winrate_results,
        "hm1_baseline": {
            "margin_mean": rlhf_margin_mean,
            "margin_std_approx": rlhf_margin_std,
        },
        "pass": {
            "sharpness_ratio": pass_sharpness,
            "boundary_accuracy": pass_boundary_acc,
            "confident_ratio": pass_confident,
        },
        "overall_pass": pass_sharpness or (pass_boundary_acc and pass_confident),
    }
    with open(cfg.metrics_output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Metrics saved to {cfg.metrics_output_path}")
    return results
