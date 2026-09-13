"""Evaluation for H-M4: accuracy + sharpness + effective rank"""

import torch
from tqdm import tqdm

from config import SHARPNESS_CONFIG, RANK_CONFIG
from sharpness import measure_task_sharpness
from rank import compute_model_effective_rank


def evaluate_accuracy(model, dataloader, device=None):
    """Compute accuracy on a task (next-token prediction accuracy)."""
    if device is None:
        device = next(model.parameters()).device

    model.eval()
    total_correct = 0
    total_tokens = 0

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            attention_mask = batch.get("attention_mask")
            if attention_mask is not None:
                attention_mask = attention_mask.to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits

            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()

            preds = shift_logits.argmax(dim=-1)

            if attention_mask is not None:
                mask = attention_mask[..., 1:].contiguous()
                correct = ((preds == shift_labels) & (mask == 1)).sum().item()
                tokens = mask.sum().item()
            else:
                correct = (preds == shift_labels).sum().item()
                tokens = shift_labels.numel()

            total_correct += correct
            total_tokens += tokens

    accuracy = total_correct / total_tokens if total_tokens > 0 else 0.0
    return accuracy


def evaluate_model_full(model, dataloader, device=None):
    """Full evaluation: accuracy + sharpness + effective rank."""
    if device is None:
        device = next(model.parameters()).device

    accuracy = evaluate_accuracy(model, dataloader, device)

    sharpness_result = measure_task_sharpness(
        model, dataloader,
        max_batches=SHARPNESS_CONFIG["max_batches"],
        sam_epsilon=SHARPNESS_CONFIG["sam_epsilon"]
    )

    rank_result = compute_model_effective_rank(model, RANK_CONFIG["default_threshold"])

    return {
        "accuracy": accuracy,
        "sharpness": sharpness_result["mean_sharpness"],
        "effective_rank": rank_result["effective_rank"],
        "mean_effective_rank": rank_result.get("mean_effective_rank", rank_result["effective_rank"]),
    }


def compute_deltas(transformer_metrics: dict, mamba_metrics: dict):
    """Compute per-task deltas: mamba - transformer."""
    return {
        "accuracy_delta": mamba_metrics["accuracy"] - transformer_metrics["accuracy"],
        "sharpness_delta": mamba_metrics["sharpness"] - transformer_metrics["sharpness"],
        "rank_delta": mamba_metrics["effective_rank"] - transformer_metrics["effective_rank"],
    }


def build_results_table(training_results: dict, benchmark_suite: dict):
    """
    Build full results table from training results.
    Returns {task_name: {'transformer': metrics, 'mamba': metrics, 'delta': deltas, 'density': float}}
    """
    results = {}

    tasks = list(benchmark_suite.keys())
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    for task_name in tasks:
        task_info = benchmark_suite[task_name]

        transformer_result = training_results.get(("transformer", task_name))
        mamba_result = training_results.get(("mamba", task_name))

        if transformer_result is None or mamba_result is None:
            print(f"  Skipping {task_name}: missing training result")
            continue

        print(f"\n  Evaluating {task_name}...")

        transformer_model = transformer_result["model"]
        mamba_model = mamba_result["model"]

        transformer_metrics = evaluate_model_full(transformer_model, task_info["loader"], device)
        mamba_metrics = evaluate_model_full(mamba_model, task_info["loader"], device)

        deltas = compute_deltas(transformer_metrics, mamba_metrics)

        results[task_name] = {
            "transformer": transformer_metrics,
            "mamba": mamba_metrics,
            "delta": deltas,
            "density": task_info["density"],
            "loss_curves": {
                "transformer": transformer_result["loss_curve"],
                "mamba": mamba_result["loss_curve"],
            }
        }

        print(f"    Transformer acc: {transformer_metrics['accuracy']:.4f}, Mamba acc: {mamba_metrics['accuracy']:.4f}")
        print(f"    Delta: {deltas['accuracy_delta']:.4f}")

    return results
