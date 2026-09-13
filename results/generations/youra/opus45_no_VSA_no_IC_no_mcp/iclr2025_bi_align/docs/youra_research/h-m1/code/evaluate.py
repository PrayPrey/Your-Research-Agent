"""Evaluation orchestration for H-M1."""
import json
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from peft import PeftModel

from config import HM1Config, set_seed
from data import load_hh_rlhf_splits, sample_test_pairs
from model import load_tokenizer
from metrics.gradient import compute_gradient_stats
from metrics.distribution import analyze_reward_distribution
from metrics.interpolation import test_interpolation
from baselines import build_random_baseline, run_baseline_metrics


def run_evaluation(cfg: HM1Config, checkpoint_path: str) -> dict:
    """Run all smoothness evaluations and check thresholds."""
    set_seed(cfg.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Loading model from {checkpoint_path}...")
    tokenizer = load_tokenizer(cfg)

    # Load trained model (PEFT)
    base_model = AutoModelForSequenceClassification.from_pretrained(
        cfg.base_model,
        num_labels=1,
        torch_dtype=torch.bfloat16 if cfg.bf16 else torch.float32,
    )
    model = PeftModel.from_pretrained(base_model, checkpoint_path)
    model = model.merge_and_unload()
    model = model.to(device)
    model.eval()

    print("Loading test data...")
    splits = load_hh_rlhf_splits(cfg, tokenizer)
    test_pairs = sample_test_pairs(splits["test"], cfg.test_sample_size, cfg.seed)
    interp_pairs = test_pairs[:cfg.interpolation_pair_count]

    print("Computing gradient statistics...")
    test_texts = [c for c, r in test_pairs]
    grad_stats = compute_gradient_stats(model, tokenizer, test_texts, device)

    print("Analyzing reward distribution...")
    dist_stats = analyze_reward_distribution(model, tokenizer, test_pairs, device)

    print("Testing interpolation...")
    interp_stats = test_interpolation(model, tokenizer, interp_pairs, device, cfg.n_interp_steps)

    print("Running baseline comparison...")
    baseline_model = build_random_baseline(cfg)
    baseline_stats = run_baseline_metrics(cfg, baseline_model, tokenizer, test_pairs, device)

    results = {
        "gradient": grad_stats,
        "distribution": dist_stats,
        "interpolation": interp_stats,
        "baseline": baseline_stats,
        "pass": {
            "gradient": grad_stats["mean_gradient_norm"] < cfg.threshold_gradient_norm,
            "distribution": dist_stats["bimodality_coefficient"] < cfg.threshold_bimodality,
            "interpolation": interp_stats["mean_interpolation_error"] < cfg.threshold_interp_error,
        },
    }
    results["overall_pass"] = all(results["pass"].values())

    print(f"\nResults:")
    print(f"  Gradient norm: {grad_stats['mean_gradient_norm']:.4f} (threshold: {cfg.threshold_gradient_norm})")
    print(f"  Bimodality: {dist_stats['bimodality_coefficient']:.4f} (threshold: {cfg.threshold_bimodality})")
    print(f"  Interpolation error: {interp_stats['mean_interpolation_error']:.4f} (threshold: {cfg.threshold_interp_error})")
    print(f"  Overall PASS: {results['overall_pass']}")

    with open(cfg.metrics_output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved metrics to {cfg.metrics_output_path}")

    return results


if __name__ == "__main__":
    import sys
    cfg = HM1Config()
    checkpoint = sys.argv[1] if len(sys.argv) > 1 else cfg.output_dir + "/final"
    run_evaluation(cfg, checkpoint)
