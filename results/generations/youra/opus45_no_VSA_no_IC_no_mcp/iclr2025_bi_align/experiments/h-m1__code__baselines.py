"""Baseline models for comparison."""
import torch
from transformers import AutoModelForSequenceClassification


def build_random_baseline(cfg):
    """Build untrained model with random classification head."""
    model = AutoModelForSequenceClassification.from_pretrained(
        cfg.base_model,
        num_labels=1,
        torch_dtype=torch.bfloat16 if cfg.bf16 else torch.float32,
    )
    model.config.pad_token_id = model.config.eos_token_id

    with torch.no_grad():
        model.score.weight.normal_(mean=0.0, std=0.02)

    return model


def run_baseline_metrics(cfg, model, tokenizer, test_pairs, device: str) -> dict:
    """Run all metric suites on baseline model."""
    from metrics.gradient import compute_gradient_stats
    from metrics.distribution import analyze_reward_distribution
    from metrics.interpolation import test_interpolation

    model = model.to(device)
    model.eval()

    test_texts = [c for c, r in test_pairs[:500]]
    grad_stats = compute_gradient_stats(model, tokenizer, test_texts, device)
    dist_stats = analyze_reward_distribution(model, tokenizer, test_pairs[:500], device)
    interp_stats = test_interpolation(model, tokenizer, test_pairs[:100], device, n_steps=10)

    return {
        "gradient": grad_stats,
        "distribution": dist_stats,
        "interpolation": interp_stats,
    }
