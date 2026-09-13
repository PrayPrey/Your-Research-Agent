import torch
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from config import Config


def eval_mmlu_accuracy(model, tokenizer, benchmark: list[dict], device: torch.device) -> float:
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for sample in benchmark:
            q = sample["question"]
            choices = sample["choices"]
            answer_idx = sample["answer"]

            choice_losses = []
            for choice in choices:
                text = f"Question: {q}\nAnswer: {choice}"
                inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256).to(device)
                outputs = model(**inputs, labels=inputs["input_ids"])
                choice_losses.append(outputs.loss.item())

            pred = np.argmin(choice_losses)
            if pred == answer_idx:
                correct += 1
            total += 1

    return correct / total if total > 0 else 0.0


def fit_ccr_regression(injection_rates: list[float], ccr_values: list[float]) -> float:
    X = np.array(injection_rates).reshape(-1, 1)
    y = np.array(ccr_values)
    reg = LinearRegression().fit(X, y)
    r2 = reg.score(X, y)
    return r2


def verify_mechanism_activation(ccr_values: list[float], injection_rates: list[float]) -> bool:
    for i in range(1, len(ccr_values)):
        if ccr_values[i] < ccr_values[i-1]:
            print(f"WARNING: Non-monotonic at {injection_rates[i]}: {ccr_values[i]} < {ccr_values[i-1]}")

    r2 = fit_ccr_regression(injection_rates, ccr_values)
    print(f"R² = {r2:.4f} (target: ≥0.9)")
    return r2 >= 0.9


def plot_ccr_scaling(injection_rates: list[float], ccr_values: list[float], r2: float, out_dir: str):
    plt.figure(figsize=(8, 6))
    plt.plot(injection_rates, ccr_values, 'bo-', markersize=10, linewidth=2)
    plt.xlabel("Injection Rate", fontsize=12)
    plt.ylabel("CCR (Contamination Contribution Ratio)", fontsize=12)
    plt.title(f"CCR vs Injection Rate (R² = {r2:.3f})", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{out_dir}/ccr_scaling.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out_dir}/ccr_scaling.png")


def plot_mmlu_vs_injection(injection_rates: list[float], accs: list[float], out_dir: str):
    plt.figure(figsize=(8, 6))
    plt.plot(injection_rates, accs, 'ro-', markersize=10, linewidth=2)
    plt.xlabel("Injection Rate", fontsize=12)
    plt.ylabel("MMLU Accuracy", fontsize=12)
    plt.title("MMLU Accuracy vs Injection Rate", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{out_dir}/mmlu_vs_injection.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out_dir}/mmlu_vs_injection.png")


def plot_attribution_distribution(scores: np.ndarray, injected_positions: list[int], out_dir: str):
    all_scores = scores.flatten()
    inj_scores = scores[:, injected_positions].flatten()

    plt.figure(figsize=(8, 6))
    plt.hist(all_scores, bins=50, alpha=0.5, label="All docs", density=True)
    if len(inj_scores) > 0:
        plt.hist(inj_scores, bins=50, alpha=0.5, label="Injected docs", density=True)
    plt.xlabel("Attribution Score", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.title("Attribution Score Distribution", fontsize=14)
    plt.legend()
    plt.savefig(f"{out_dir}/attribution_dist.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out_dir}/attribution_dist.png")
