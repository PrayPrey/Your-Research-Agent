"""Quick validation run with 10% data subset for Phase 4 validation."""
import os
import sys
import json
import torch
from dataclasses import dataclass

from config import HM1Config, set_seed, get_reward_config, get_peft_config
from data import load_hh_rlhf_splits, sample_test_pairs
from model import load_tokenizer, build_reward_model, get_reward

from transformers import AutoModelForSequenceClassification
from peft import get_peft_model, PeftModel
from trl import RewardTrainer

from metrics.gradient import compute_gradient_stats
from metrics.distribution import analyze_reward_distribution
from metrics.interpolation import test_interpolation


@dataclass
class QuickConfig(HM1Config):
    """Quick validation config with smaller dataset."""
    max_train_samples: int = 15000  # ~10% of full
    num_train_epochs: int = 1
    eval_steps: int = 100
    save_steps: int = 500
    test_sample_size: int = 1000
    interpolation_pair_count: int = 100
    output_dir: str = "./reward_model_h-m1_quick"


def run_quick_training(cfg: QuickConfig) -> str:
    """Quick training with subset."""
    set_seed(cfg.seed)

    print("Loading tokenizer...")
    tokenizer = load_tokenizer(cfg)

    print("Loading dataset...")
    splits = load_hh_rlhf_splits(cfg, tokenizer)

    # Subsample train data
    train_ds = splits["train"].shuffle(seed=cfg.seed).select(range(min(cfg.max_train_samples, len(splits["train"]))))
    val_ds = splits["validation"].shuffle(seed=cfg.seed).select(range(min(1000, len(splits["validation"]))))

    print(f"Train samples: {len(train_ds)}, Val samples: {len(val_ds)}")

    print("Building model...")
    model = build_reward_model(cfg, use_lora=True)

    print("Building trainer...")
    reward_config = get_reward_config(cfg)

    trainer = RewardTrainer(
        model=model,
        processing_class=tokenizer,
        args=reward_config,
        train_dataset=train_ds,
        eval_dataset=val_ds,
    )

    print("Starting training...")
    trainer.train()

    final_path = os.path.join(cfg.output_dir, "final")
    trainer.save_model(final_path)
    tokenizer.save_pretrained(final_path)
    print(f"Saved model to {final_path}")

    return final_path


def run_quick_evaluation(cfg: QuickConfig, checkpoint_path: str) -> dict:
    """Run smoothness evaluation."""
    set_seed(cfg.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Loading model from {checkpoint_path}...")
    tokenizer = load_tokenizer(cfg)

    base_model = AutoModelForSequenceClassification.from_pretrained(
        cfg.base_model,
        num_labels=1,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
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
    test_texts = [c for c, r in test_pairs[:500]]
    grad_stats = compute_gradient_stats(model, tokenizer, test_texts, device)

    print("Analyzing reward distribution...")
    dist_stats = analyze_reward_distribution(model, tokenizer, test_pairs, device)

    print("Testing interpolation...")
    interp_stats = test_interpolation(model, tokenizer, interp_pairs, device, cfg.n_interp_steps)

    results = {
        "gradient": grad_stats,
        "distribution": dist_stats,
        "interpolation": interp_stats,
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
    print(f"  Margin (chosen - rejected): {dist_stats['margin']:.4f}")
    print(f"  Overall PASS: {results['overall_pass']}")

    with open(cfg.metrics_output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved metrics to {cfg.metrics_output_path}")

    return results


def main():
    cfg = QuickConfig()
    set_seed(cfg.seed)

    os.makedirs(cfg.output_dir, exist_ok=True)

    print("=" * 60)
    print("H-M1: Quick Validation (10% data)")
    print("=" * 60)
    print(f"Base model: {cfg.base_model}")
    print(f"Train samples: {cfg.max_train_samples}")
    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    print()

    checkpoint_path = run_quick_training(cfg)
    results = run_quick_evaluation(cfg, checkpoint_path)

    print("\n" + "=" * 60)
    print("QUICK VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Gradient smoothness: {'PASS' if results['pass']['gradient'] else 'FAIL'}")
    print(f"Distribution continuity: {'PASS' if results['pass']['distribution'] else 'FAIL'}")
    print(f"Interpolation smoothness: {'PASS' if results['pass']['interpolation'] else 'FAIL'}")
    print(f"OVERALL: {'PASS' if results['overall_pass'] else 'FAIL'}")
    print("=" * 60)

    return 0 if results["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
