import os
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from scipy.stats import spearmanr
from scipy.spatial.distance import jensenshannon
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    roc_curve,
    precision_recall_curve,
)
import matplotlib.pyplot as plt
from datasets import load_dataset
import warnings

warnings.filterwarnings("ignore")

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Initialize experiment data structure with ablation types
experiment_data = {
    "uniform": {},  # Baseline
    "exponential_decay": {},  # Early tokens weighted more
    "exponential_growth": {},  # Later tokens weighted more
    "middle_emphasis": {},  # Middle tokens weighted more
}

for weighting_scheme in experiment_data.keys():
    for dataset_name in ["trivia_qa", "boolq", "commonsense_qa"]:
        experiment_data[weighting_scheme][dataset_name] = {
            "consensus_scores": [],
            "hallucination_labels": [],
            "generated_texts": [],
            "ground_truth": [],
            "per_token_consensus": [],
            "metrics": {
                "HPR": [],
                "accuracy": [],
                "auroc": [],
                "auprc": [],
            },
        }

print("Loading datasets from HuggingFace...")
trivia_dataset = load_dataset(
    "trivia_qa", "unfiltered.nocontext", split="validation[:200]"
)
boolq_dataset = load_dataset("boolq", split="validation[:200]")
commonsense_dataset = load_dataset("commonsense_qa", split="validation[:200]")

print("Loading model and tokenizer...")
model_name = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, output_hidden_states=True, torch_dtype=torch.float16, device_map="auto"
)
model.eval()

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


def compute_consensus_metrics(
    early_probs: torch.Tensor, mid_probs: torch.Tensor, late_probs: torch.Tensor
) -> dict:
    """Compute consensus metrics between layer predictions"""
    eps = 1e-10

    early_np = early_probs.cpu().detach().numpy().flatten()
    late_np = late_probs.cpu().detach().numpy().flatten()

    early_np = np.clip(early_np, eps, 1.0)
    late_np = np.clip(late_np, eps, 1.0)

    early_np = early_np / np.sum(early_np)
    late_np = late_np / np.sum(late_np)

    js_div = jensenshannon(early_np, late_np)
    if np.isnan(js_div) or np.isinf(js_div):
        js_div = 0.5

    return {"js_divergence": float(js_div)}


def apply_position_weighting(per_token_scores: list, scheme: str) -> float:
    """Apply different position weighting schemes to aggregate per-token scores"""
    if len(per_token_scores) == 0:
        return 0.0

    scores = np.array(per_token_scores)
    n = len(scores)

    if scheme == "uniform":
        # Baseline: simple mean
        weights = np.ones(n)
    elif scheme == "exponential_decay":
        # Early tokens weighted more: exp(-alpha * position)
        alpha = 0.1
        positions = np.arange(n)
        weights = np.exp(-alpha * positions)
    elif scheme == "exponential_growth":
        # Later tokens weighted more: exp(alpha * position)
        alpha = 0.1
        positions = np.arange(n)
        weights = np.exp(alpha * positions)
    elif scheme == "middle_emphasis":
        # Middle tokens weighted more: Gaussian centered at middle
        center = n / 2
        sigma = n / 4
        positions = np.arange(n)
        weights = np.exp(-((positions - center) ** 2) / (2 * sigma**2))
    else:
        weights = np.ones(n)

    # Normalize weights
    weights = weights / np.sum(weights)

    # Compute weighted sum
    weighted_score = np.sum(scores * weights)
    return float(weighted_score)


def generate_with_layer_monitoring(prompt: str, max_new_tokens: int = 20) -> tuple:
    """Generate text while monitoring layer consensus metrics at each step"""
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    token_metrics = []

    num_layers = len(model.model.layers)
    early_layer_idx = num_layers // 4
    mid_layer_idx = num_layers // 2
    late_layer_idx = num_layers - 1

    for step in range(max_new_tokens):
        with torch.no_grad():
            outputs = model(input_ids, output_hidden_states=True)
            hidden_states = outputs.hidden_states

            early_hidden = hidden_states[early_layer_idx][:, -1, :]
            mid_hidden = hidden_states[mid_layer_idx][:, -1, :]
            late_hidden = hidden_states[late_layer_idx][:, -1, :]

            early_logits = model.lm_head(early_hidden)
            mid_logits = model.lm_head(mid_hidden)
            late_logits = model.lm_head(late_hidden)

            early_probs = F.softmax(early_logits, dim=-1)
            mid_probs = F.softmax(mid_logits, dim=-1)
            late_probs = F.softmax(late_logits, dim=-1)

            metrics = compute_consensus_metrics(
                early_probs[0], mid_probs[0], late_probs[0]
            )
            token_metrics.append(metrics)

            next_token = torch.argmax(late_probs, dim=-1)
            input_ids = torch.cat([input_ids, next_token.unsqueeze(0)], dim=-1)

            if next_token.item() == tokenizer.eos_token_id:
                break

    generated_text = tokenizer.decode(input_ids[0], skip_special_tokens=True)
    return generated_text, token_metrics


def extract_answer(generated_text: str, prompt: str) -> str:
    """Extract the answer portion after the prompt"""
    if "[/INST]" in generated_text:
        answer = generated_text.split("[/INST]")[-1].strip()
    elif prompt in generated_text:
        answer = generated_text.split(prompt)[-1].strip()
    else:
        answer = generated_text.strip()
    answer = answer.split("\n")[0][:100].strip().lower()
    return answer


def process_trivia_qa(samples, num_samples=150):
    """Process TriviaQA dataset"""
    print(f"\n{'='*60}")
    print(f"Processing TRIVIA_QA - {num_samples} samples")
    print(f"{'='*60}")

    for idx, sample in enumerate(samples):
        if idx >= num_samples:
            break

        question = sample["question"]
        ground_truth = sample["answer"]["value"].lower().strip()

        prompt = f"[INST] Answer this question with a short factual answer: {question} [/INST]"

        generated_text, token_metrics = generate_with_layer_monitoring(
            prompt, max_new_tokens=15
        )
        answer = extract_answer(generated_text, prompt)

        is_correct = (
            ground_truth in answer
            or answer in ground_truth
            or any(alias.lower() in answer for alias in sample["answer"]["aliases"])
        )
        hallucination_label = 0 if is_correct else 1

        per_token_js = [m["js_divergence"] for m in token_metrics]

        # Apply all weighting schemes
        for scheme in [
            "uniform",
            "exponential_decay",
            "exponential_growth",
            "middle_emphasis",
        ]:
            weighted_score = apply_position_weighting(per_token_js, scheme)
            experiment_data[scheme]["trivia_qa"]["consensus_scores"].append(
                weighted_score
            )
            experiment_data[scheme]["trivia_qa"]["hallucination_labels"].append(
                hallucination_label
            )
            experiment_data[scheme]["trivia_qa"]["generated_texts"].append(answer)
            experiment_data[scheme]["trivia_qa"]["ground_truth"].append(ground_truth)
            experiment_data[scheme]["trivia_qa"]["per_token_consensus"].append(
                per_token_js
            )

        if idx < 3 or idx % 50 == 0:
            print(f"\nExample {idx+1}:")
            print(f"Q: {question[:80]}...")
            print(f"GT: {ground_truth}")
            print(f"Generated: {answer}")
            print(f"Correct: {is_correct}")


def process_boolq(samples, num_samples=150):
    """Process BoolQ dataset"""
    print(f"\n{'='*60}")
    print(f"Processing BOOLQ - {num_samples} samples")
    print(f"{'='*60}")

    for idx, sample in enumerate(samples):
        if idx >= num_samples:
            break

        passage = sample["passage"][:300]
        question = sample["question"]
        ground_truth = "yes" if sample["answer"] else "no"

        prompt = f"[INST] Based on the passage, answer yes or no.\nPassage: {passage}\nQuestion: {question}\nAnswer: [/INST]"

        generated_text, token_metrics = generate_with_layer_monitoring(
            prompt, max_new_tokens=10
        )
        answer = extract_answer(generated_text, prompt)

        is_correct = ground_truth in answer
        hallucination_label = 0 if is_correct else 1

        per_token_js = [m["js_divergence"] for m in token_metrics]

        for scheme in [
            "uniform",
            "exponential_decay",
            "exponential_growth",
            "middle_emphasis",
        ]:
            weighted_score = apply_position_weighting(per_token_js, scheme)
            experiment_data[scheme]["boolq"]["consensus_scores"].append(weighted_score)
            experiment_data[scheme]["boolq"]["hallucination_labels"].append(
                hallucination_label
            )
            experiment_data[scheme]["boolq"]["generated_texts"].append(answer)
            experiment_data[scheme]["boolq"]["ground_truth"].append(ground_truth)
            experiment_data[scheme]["boolq"]["per_token_consensus"].append(per_token_js)

        if idx < 3 or idx % 50 == 0:
            print(f"\nExample {idx+1}:")
            print(f"Q: {question[:80]}...")
            print(f"GT: {ground_truth}")
            print(f"Generated: {answer}")
            print(f"Correct: {is_correct}")


def process_commonsense_qa(samples, num_samples=150):
    """Process CommonsenseQA dataset"""
    print(f"\n{'='*60}")
    print(f"Processing COMMONSENSE_QA - {num_samples} samples")
    print(f"{'='*60}")

    for idx, sample in enumerate(samples):
        if idx >= num_samples:
            break

        question = sample["question"]
        choices = sample["choices"]["text"]
        labels = sample["choices"]["label"]
        correct_label = sample["answerKey"]

        choices_str = "\n".join([f"{l}: {t}" for l, t in zip(labels, choices)])
        prompt = f"[INST] Answer with just the letter (A-E).\nQuestion: {question}\n{choices_str}\nAnswer: [/INST]"

        generated_text, token_metrics = generate_with_layer_monitoring(
            prompt, max_new_tokens=8
        )
        answer = extract_answer(generated_text, prompt)

        is_correct = correct_label.lower() in answer[:5]
        hallucination_label = 0 if is_correct else 1

        per_token_js = [m["js_divergence"] for m in token_metrics]

        for scheme in [
            "uniform",
            "exponential_decay",
            "exponential_growth",
            "middle_emphasis",
        ]:
            weighted_score = apply_position_weighting(per_token_js, scheme)
            experiment_data[scheme]["commonsense_qa"]["consensus_scores"].append(
                weighted_score
            )
            experiment_data[scheme]["commonsense_qa"]["hallucination_labels"].append(
                hallucination_label
            )
            experiment_data[scheme]["commonsense_qa"]["generated_texts"].append(answer)
            experiment_data[scheme]["commonsense_qa"]["ground_truth"].append(
                correct_label
            )
            experiment_data[scheme]["commonsense_qa"]["per_token_consensus"].append(
                per_token_js
            )

        if idx < 3 or idx % 50 == 0:
            print(f"\nExample {idx+1}:")
            print(f"Q: {question[:80]}...")
            print(f"GT: {correct_label}")
            print(f"Generated: {answer}")
            print(f"Correct: {is_correct}")


# Process all three datasets
process_trivia_qa(trivia_dataset, num_samples=150)
process_boolq(boolq_dataset, num_samples=150)
process_commonsense_qa(commonsense_dataset, num_samples=150)

# Evaluate all weighting schemes
print(f"\n{'='*60}")
print("ABLATION STUDY EVALUATION")
print(f"{'='*60}")

results_summary = {}

for scheme in ["uniform", "exponential_decay", "exponential_growth", "middle_emphasis"]:
    print(f"\n{'='*60}")
    print(f"WEIGHTING SCHEME: {scheme.upper()}")
    print(f"{'='*60}")

    results_summary[scheme] = {}

    for dataset_name in ["trivia_qa", "boolq", "commonsense_qa"]:
        print(f"\n{dataset_name.upper()}:")

        consensus_scores = np.array(
            experiment_data[scheme][dataset_name]["consensus_scores"]
        )
        hallucination_labels = np.array(
            experiment_data[scheme][dataset_name]["hallucination_labels"]
        )

        valid_mask = np.isfinite(consensus_scores)
        consensus_scores = consensus_scores[valid_mask]
        hallucination_labels = hallucination_labels[valid_mask]

        n_correct = np.sum(hallucination_labels == 0)
        n_hallucination = np.sum(hallucination_labels == 1)
        accuracy = (
            n_correct / len(hallucination_labels)
            if len(hallucination_labels) > 0
            else 0
        )

        print(f"Total samples: {len(hallucination_labels)}")
        print(f"Correct: {n_correct} ({accuracy*100:.1f}%)")
        print(f"Hallucinations: {n_hallucination} ({(1-accuracy)*100:.1f}%)")

        if len(np.unique(hallucination_labels)) > 1:
            auroc = roc_auc_score(hallucination_labels, consensus_scores)
            auprc = average_precision_score(hallucination_labels, consensus_scores)

            print(f"AUROC: {auroc:.4f}")
            print(f"AUPRC: {auprc:.4f}")

            # Compute HPR
            percentiles = [50, 60, 70, 80, 90]
            best_hpr = -np.inf

            for p in percentiles:
                threshold = np.percentile(consensus_scores, p)
                rejected_mask = consensus_scores > threshold
                rejection_rate = np.mean(rejected_mask)

                errors_in_rejected = np.sum(
                    (rejected_mask) & (hallucination_labels == 1)
                )
                baseline_errors = n_hallucination
                method_errors = baseline_errors - errors_in_rejected

                if baseline_errors > 0 and rejection_rate > 0:
                    HPR = (baseline_errors - method_errors) / (
                        baseline_errors * np.sqrt(rejection_rate + 0.01)
                    )
                else:
                    HPR = 0.0

                if HPR > best_hpr:
                    best_hpr = HPR

            print(f"Best HPR: {best_hpr:.4f}")

            experiment_data[scheme][dataset_name]["metrics"]["HPR"].append(
                float(best_hpr)
            )
            experiment_data[scheme][dataset_name]["metrics"]["accuracy"].append(
                float(accuracy)
            )
            experiment_data[scheme][dataset_name]["metrics"]["auroc"].append(
                float(auroc)
            )
            experiment_data[scheme][dataset_name]["metrics"]["auprc"].append(
                float(auprc)
            )

            results_summary[scheme][dataset_name] = {
                "auroc": float(auroc),
                "auprc": float(auprc),
                "hpr": float(best_hpr),
                "accuracy": float(accuracy),
            }
        else:
            print("WARNING: Insufficient class diversity")
            experiment_data[scheme][dataset_name]["metrics"]["HPR"].append(0.0)
            experiment_data[scheme][dataset_name]["metrics"]["accuracy"].append(
                float(accuracy)
            )
            experiment_data[scheme][dataset_name]["metrics"]["auroc"].append(0.5)
            experiment_data[scheme][dataset_name]["metrics"]["auprc"].append(0.5)

            results_summary[scheme][dataset_name] = {
                "auroc": 0.5,
                "auprc": 0.5,
                "hpr": 0.0,
                "accuracy": float(accuracy),
            }

# Generate comparison visualizations
print(f"\n{'='*60}")
print("GENERATING COMPARISON VISUALIZATIONS")
print(f"{'='*60}")

schemes = ["uniform", "exponential_decay", "exponential_growth", "middle_emphasis"]
scheme_labels = [
    "Uniform (Baseline)",
    "Exponential Decay",
    "Exponential Growth",
    "Middle Emphasis",
]
datasets = ["trivia_qa", "boolq", "commonsense_qa"]

# Plot 1: AUROC comparison across schemes and datasets
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

for i, metric in enumerate(["auroc", "auprc", "hpr", "accuracy"]):
    ax = axes[i // 2, i % 2]

    x = np.arange(len(datasets))
    width = 0.2

    for j, scheme in enumerate(schemes):
        values = [results_summary[scheme][ds][metric] for ds in datasets]
        ax.bar(x + j * width, values, width, label=scheme_labels[j])

    ax.set_xlabel("Dataset")
    ax.set_ylabel(metric.upper())
    ax.set_title(f"{metric.upper()} Comparison Across Weighting Schemes")
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(datasets)
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ablation_comparison.png"), dpi=150, bbox_inches="tight"
)
plt.close()
print("Saved ablation comparison plot")

# Plot 2: Per-dataset ROC curves
for dataset_name in datasets:
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    for scheme, label in zip(schemes, scheme_labels):
        consensus_scores = np.array(
            experiment_data[scheme][dataset_name]["consensus_scores"]
        )
        hallucination_labels = np.array(
            experiment_data[scheme][dataset_name]["hallucination_labels"]
        )

        valid_mask = np.isfinite(consensus_scores)
        consensus_scores = consensus_scores[valid_mask]
        hallucination_labels = hallucination_labels[valid_mask]

        if len(np.unique(hallucination_labels)) > 1:
            fpr, tpr, _ = roc_curve(hallucination_labels, consensus_scores)
            auroc = results_summary[scheme][dataset_name]["auroc"]
            ax.plot(fpr, tpr, label=f"{label} (AUROC={auroc:.3f})", linewidth=2)

    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"ROC Curves - {dataset_name.upper()}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"roc_{dataset_name}.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()
    print(f"Saved ROC curve for {dataset_name}")

# Plot 3: Weight visualization
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

n_tokens = 20
positions = np.arange(n_tokens)

for ax, scheme in zip(
    axes, ["exponential_decay", "exponential_growth", "middle_emphasis"]
):
    if scheme == "exponential_decay":
        alpha = 0.1
        weights = np.exp(-alpha * positions)
    elif scheme == "exponential_growth":
        alpha = 0.1
        weights = np.exp(alpha * positions)
    elif scheme == "middle_emphasis":
        center = n_tokens / 2
        sigma = n_tokens / 4
        weights = np.exp(-((positions - center) ** 2) / (2 * sigma**2))

    weights = weights / np.sum(weights)

    ax.bar(positions, weights, color="steelblue")
    ax.set_xlabel("Token Position")
    ax.set_ylabel("Normalized Weight")
    ax.set_title(f"{scheme.replace('_', ' ').title()} Weighting")
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "weighting_schemes_visualization.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()
print("Saved weighting schemes visualization")

# Save all experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nSaved experiment data to {os.path.join(working_dir, 'experiment_data.npy')}")

# Print final summary table
print("\n" + "=" * 80)
print("FINAL ABLATION STUDY SUMMARY")
print("=" * 80)
print(
    f"\n{'Scheme':<25} {'Dataset':<20} {'AUROC':<10} {'AUPRC':<10} {'HPR':<10} {'Acc':<10}"
)
print("-" * 80)

for scheme, label in zip(schemes, scheme_labels):
    for dataset_name in datasets:
        res = results_summary[scheme][dataset_name]
        print(
            f"{label:<25} {dataset_name:<20} {res['auroc']:<10.4f} {res['auprc']:<10.4f} {res['hpr']:<10.4f} {res['accuracy']:<10.4f}"
        )

# Compute average improvements over baseline
print("\n" + "=" * 80)
print("IMPROVEMENT OVER BASELINE (Uniform)")
print("=" * 80)

for scheme, label in zip(schemes[1:], scheme_labels[1:]):
    print(f"\n{label}:")
    for dataset_name in datasets:
        baseline_auroc = results_summary["uniform"][dataset_name]["auroc"]
        scheme_auroc = results_summary[scheme][dataset_name]["auroc"]
        improvement = scheme_auroc - baseline_auroc
        print(f"  {dataset_name}: AUROC improvement = {improvement:+.4f}")

print("\n" + "=" * 80)
print("ABLATION STUDY COMPLETE")
print("=" * 80)
