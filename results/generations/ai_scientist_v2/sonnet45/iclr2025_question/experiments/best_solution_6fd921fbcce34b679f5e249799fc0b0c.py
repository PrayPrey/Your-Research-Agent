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

# Initialize experiment data structure with expanded metrics
experiment_data = {
    "trivia_qa": {
        "consensus_scores": [],
        "hallucination_labels": [],
        "generated_texts": [],
        "ground_truth": [],
        "per_token_consensus": [],
        "top1_agreement": [],
        "rank_correlation": [],
        "entropy_gap": [],
        "early_spike": [],
        "metrics": {
            "HPR": [],
            "accuracy": [],
            "rejection_rate": [],
            "auroc": [],
            "auprc": [],
        },
    },
    "boolq": {
        "consensus_scores": [],
        "hallucination_labels": [],
        "generated_texts": [],
        "ground_truth": [],
        "per_token_consensus": [],
        "top1_agreement": [],
        "rank_correlation": [],
        "entropy_gap": [],
        "early_spike": [],
        "metrics": {
            "HPR": [],
            "accuracy": [],
            "rejection_rate": [],
            "auroc": [],
            "auprc": [],
        },
    },
    "commonsense_qa": {
        "consensus_scores": [],
        "hallucination_labels": [],
        "generated_texts": [],
        "ground_truth": [],
        "per_token_consensus": [],
        "top1_agreement": [],
        "rank_correlation": [],
        "entropy_gap": [],
        "early_spike": [],
        "metrics": {
            "HPR": [],
            "accuracy": [],
            "rejection_rate": [],
            "auroc": [],
            "auprc": [],
        },
    },
}

print("Loading datasets from HuggingFace...")
# Significantly increase sample size for proper scaling
trivia_dataset = load_dataset(
    "trivia_qa", "unfiltered.nocontext", split="validation[:200]"
)
boolq_dataset = load_dataset("boolq", split="validation[:200]")
commonsense_dataset = load_dataset("commonsense_qa", split="validation[:200]")

print("Loading larger model (7B) and tokenizer...")
model_name = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, output_hidden_states=True, torch_dtype=torch.float16, device_map="auto"
)
model.eval()

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


def compute_entropy(probs: torch.Tensor) -> float:
    """Compute entropy of probability distribution"""
    probs_np = probs.cpu().detach().numpy().flatten()
    probs_np = np.clip(probs_np, 1e-10, 1.0)
    probs_np = probs_np / np.sum(probs_np)
    entropy = -np.sum(probs_np * np.log(probs_np + 1e-10))
    return float(entropy)


def compute_consensus_metrics(
    early_probs: torch.Tensor, mid_probs: torch.Tensor, late_probs: torch.Tensor
) -> dict:
    """Compute multiple consensus metrics between layer predictions"""
    eps = 1e-10

    # Convert to numpy
    early_np = early_probs.cpu().detach().numpy().flatten()
    mid_np = mid_probs.cpu().detach().numpy().flatten()
    late_np = late_probs.cpu().detach().numpy().flatten()

    # Normalize
    early_np = np.clip(early_np, eps, 1.0)
    mid_np = np.clip(mid_np, eps, 1.0)
    late_np = np.clip(late_np, eps, 1.0)

    early_np = early_np / np.sum(early_np)
    mid_np = mid_np / np.sum(mid_np)
    late_np = late_np / np.sum(late_np)

    # 1. JS Divergence (early vs late)
    js_div = jensenshannon(early_np, late_np)
    if np.isnan(js_div) or np.isinf(js_div):
        js_div = 0.5

    # 2. Top-1 Agreement
    early_top1 = np.argmax(early_np)
    late_top1 = np.argmax(late_np)
    top1_agreement = 1.0 if early_top1 == late_top1 else 0.0

    # 3. Rank Correlation (Spearman on top-100 tokens)
    top_k = min(100, len(early_np))
    early_topk_idx = np.argsort(early_np)[-top_k:]
    late_topk_idx = np.argsort(late_np)[-top_k:]
    common_idx = np.intersect1d(early_topk_idx, late_topk_idx)

    if len(common_idx) > 5:
        early_ranks = early_np[common_idx]
        late_ranks = late_np[common_idx]
        rank_corr, _ = spearmanr(early_ranks, late_ranks)
        if np.isnan(rank_corr):
            rank_corr = 0.0
    else:
        rank_corr = 0.0

    # 4. Entropy Gap (late - early)
    early_entropy = -np.sum(early_np * np.log(early_np + eps))
    late_entropy = -np.sum(late_np * np.log(late_np + eps))
    entropy_gap = late_entropy - early_entropy

    return {
        "js_divergence": float(js_div),
        "top1_agreement": float(top1_agreement),
        "rank_correlation": float(rank_corr),
        "entropy_gap": float(entropy_gap),
    }


def generate_with_layer_monitoring(prompt: str, max_new_tokens: int = 20) -> tuple:
    """Generate text while monitoring multiple layer consensus metrics at each step"""
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

            # Get logits from each layer
            early_logits = model.lm_head(early_hidden)
            mid_logits = model.lm_head(mid_hidden)
            late_logits = model.lm_head(late_hidden)

            early_probs = F.softmax(early_logits, dim=-1)
            mid_probs = F.softmax(mid_logits, dim=-1)
            late_probs = F.softmax(late_logits, dim=-1)

            # Compute all consensus metrics
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


def process_trivia_qa(samples, dataset_name="trivia_qa", num_samples=150):
    """Process TriviaQA dataset with improved prompting"""
    print(f"\n{'='*60}")
    print(f"Processing {dataset_name.upper()} - {num_samples} samples")
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

        # Aggregate metrics across tokens
        avg_js = (
            np.mean([m["js_divergence"] for m in token_metrics])
            if token_metrics
            else 0.0
        )
        avg_top1 = (
            np.mean([m["top1_agreement"] for m in token_metrics])
            if token_metrics
            else 1.0
        )
        avg_rank = (
            np.mean([m["rank_correlation"] for m in token_metrics])
            if token_metrics
            else 1.0
        )
        avg_entropy_gap = (
            np.mean([m["entropy_gap"] for m in token_metrics]) if token_metrics else 0.0
        )
        early_spike = token_metrics[0]["js_divergence"] if token_metrics else 0.0

        experiment_data[dataset_name]["consensus_scores"].append(avg_js)
        experiment_data[dataset_name]["hallucination_labels"].append(
            hallucination_label
        )
        experiment_data[dataset_name]["generated_texts"].append(answer)
        experiment_data[dataset_name]["ground_truth"].append(ground_truth)
        experiment_data[dataset_name]["per_token_consensus"].append(
            [m["js_divergence"] for m in token_metrics]
        )
        experiment_data[dataset_name]["top1_agreement"].append(avg_top1)
        experiment_data[dataset_name]["rank_correlation"].append(avg_rank)
        experiment_data[dataset_name]["entropy_gap"].append(avg_entropy_gap)
        experiment_data[dataset_name]["early_spike"].append(early_spike)

        if idx < 3 or idx % 50 == 0:
            print(f"\nExample {idx+1}:")
            print(f"Q: {question[:80]}...")
            print(f"GT: {ground_truth}")
            print(f"Generated: {answer}")
            print(
                f"Correct: {is_correct}, JS: {avg_js:.3f}, Top1: {avg_top1:.3f}, Rank: {avg_rank:.3f}"
            )


def process_boolq(samples, dataset_name="boolq", num_samples=150):
    """Process BoolQ dataset"""
    print(f"\n{'='*60}")
    print(f"Processing {dataset_name.upper()} - {num_samples} samples")
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

        avg_js = (
            np.mean([m["js_divergence"] for m in token_metrics])
            if token_metrics
            else 0.0
        )
        avg_top1 = (
            np.mean([m["top1_agreement"] for m in token_metrics])
            if token_metrics
            else 1.0
        )
        avg_rank = (
            np.mean([m["rank_correlation"] for m in token_metrics])
            if token_metrics
            else 1.0
        )
        avg_entropy_gap = (
            np.mean([m["entropy_gap"] for m in token_metrics]) if token_metrics else 0.0
        )
        early_spike = token_metrics[0]["js_divergence"] if token_metrics else 0.0

        experiment_data[dataset_name]["consensus_scores"].append(avg_js)
        experiment_data[dataset_name]["hallucination_labels"].append(
            hallucination_label
        )
        experiment_data[dataset_name]["generated_texts"].append(answer)
        experiment_data[dataset_name]["ground_truth"].append(ground_truth)
        experiment_data[dataset_name]["per_token_consensus"].append(
            [m["js_divergence"] for m in token_metrics]
        )
        experiment_data[dataset_name]["top1_agreement"].append(avg_top1)
        experiment_data[dataset_name]["rank_correlation"].append(avg_rank)
        experiment_data[dataset_name]["entropy_gap"].append(avg_entropy_gap)
        experiment_data[dataset_name]["early_spike"].append(early_spike)

        if idx < 3 or idx % 50 == 0:
            print(f"\nExample {idx+1}:")
            print(f"Q: {question[:80]}...")
            print(f"GT: {ground_truth}")
            print(f"Generated: {answer}")
            print(f"Correct: {is_correct}, JS: {avg_js:.3f}")


def process_commonsense_qa(samples, dataset_name="commonsense_qa", num_samples=150):
    """Process CommonsenseQA dataset"""
    print(f"\n{'='*60}")
    print(f"Processing {dataset_name.upper()} - {num_samples} samples")
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

        avg_js = (
            np.mean([m["js_divergence"] for m in token_metrics])
            if token_metrics
            else 0.0
        )
        avg_top1 = (
            np.mean([m["top1_agreement"] for m in token_metrics])
            if token_metrics
            else 1.0
        )
        avg_rank = (
            np.mean([m["rank_correlation"] for m in token_metrics])
            if token_metrics
            else 1.0
        )
        avg_entropy_gap = (
            np.mean([m["entropy_gap"] for m in token_metrics]) if token_metrics else 0.0
        )
        early_spike = token_metrics[0]["js_divergence"] if token_metrics else 0.0

        experiment_data[dataset_name]["consensus_scores"].append(avg_js)
        experiment_data[dataset_name]["hallucination_labels"].append(
            hallucination_label
        )
        experiment_data[dataset_name]["generated_texts"].append(answer)
        experiment_data[dataset_name]["ground_truth"].append(correct_label)
        experiment_data[dataset_name]["per_token_consensus"].append(
            [m["js_divergence"] for m in token_metrics]
        )
        experiment_data[dataset_name]["top1_agreement"].append(avg_top1)
        experiment_data[dataset_name]["rank_correlation"].append(avg_rank)
        experiment_data[dataset_name]["entropy_gap"].append(avg_entropy_gap)
        experiment_data[dataset_name]["early_spike"].append(early_spike)

        if idx < 3 or idx % 50 == 0:
            print(f"\nExample {idx+1}:")
            print(f"Q: {question[:80]}...")
            print(f"GT: {correct_label}")
            print(f"Generated: {answer}")
            print(f"Correct: {is_correct}, JS: {avg_js:.3f}")


# Process all three datasets with increased sample size
process_trivia_qa(trivia_dataset, num_samples=150)
process_boolq(boolq_dataset, num_samples=150)
process_commonsense_qa(commonsense_dataset, num_samples=150)

# Compute comprehensive metrics for each dataset
print(f"\n{'='*60}")
print("COMPREHENSIVE EVALUATION METRICS")
print(f"{'='*60}")

for dataset_name in ["trivia_qa", "boolq", "commonsense_qa"]:
    print(f"\n{dataset_name.upper()}:")

    consensus_scores = np.array(experiment_data[dataset_name]["consensus_scores"])
    hallucination_labels = np.array(
        experiment_data[dataset_name]["hallucination_labels"]
    )
    top1_agreement = np.array(experiment_data[dataset_name]["top1_agreement"])
    rank_correlation = np.array(experiment_data[dataset_name]["rank_correlation"])
    entropy_gap = np.array(experiment_data[dataset_name]["entropy_gap"])
    early_spike = np.array(experiment_data[dataset_name]["early_spike"])

    # Filter valid values
    valid_mask = np.isfinite(consensus_scores)
    consensus_scores = consensus_scores[valid_mask]
    hallucination_labels = hallucination_labels[valid_mask]
    top1_agreement = top1_agreement[valid_mask]
    rank_correlation = rank_correlation[valid_mask]
    entropy_gap = entropy_gap[valid_mask]
    early_spike = early_spike[valid_mask]

    n_correct = np.sum(hallucination_labels == 0)
    n_hallucination = np.sum(hallucination_labels == 1)
    accuracy = (
        n_correct / len(hallucination_labels) if len(hallucination_labels) > 0 else 0
    )

    print(f"Total samples: {len(hallucination_labels)}")
    print(f"Correct: {n_correct} ({accuracy*100:.1f}%)")
    print(f"Hallucinations: {n_hallucination} ({(1-accuracy)*100:.1f}%)")

    if len(np.unique(hallucination_labels)) > 1:
        # Compute AUROC and AUPRC for each metric
        auroc_js = roc_auc_score(hallucination_labels, consensus_scores)
        auprc_js = average_precision_score(hallucination_labels, consensus_scores)

        auroc_top1 = roc_auc_score(hallucination_labels, 1 - top1_agreement)
        auroc_rank = roc_auc_score(hallucination_labels, 1 - rank_correlation)
        auroc_entropy = roc_auc_score(hallucination_labels, np.abs(entropy_gap))
        auroc_spike = roc_auc_score(hallucination_labels, early_spike)

        print(f"\nAUROC Scores:")
        print(f"  JS Divergence: {auroc_js:.4f}")
        print(f"  Top-1 Disagreement: {auroc_top1:.4f}")
        print(f"  Rank Anti-correlation: {auroc_rank:.4f}")
        print(f"  Abs Entropy Gap: {auroc_entropy:.4f}")
        print(f"  Early Spike: {auroc_spike:.4f}")
        print(f"AUPRC (JS): {auprc_js:.4f}")

        # Spearman correlations
        corr_js, _ = spearmanr(consensus_scores, hallucination_labels)
        corr_top1, _ = spearmanr(top1_agreement, hallucination_labels)
        corr_rank, _ = spearmanr(rank_correlation, hallucination_labels)
        corr_entropy, _ = spearmanr(entropy_gap, hallucination_labels)

        print(f"\nSpearman Correlations with Hallucination:")
        print(f"  JS Divergence: {corr_js:.4f}")
        print(f"  Top-1 Agreement: {corr_top1:.4f}")
        print(f"  Rank Correlation: {corr_rank:.4f}")
        print(f"  Entropy Gap: {corr_entropy:.4f}")

        # Test multiple thresholds
        percentiles = [50, 60, 70, 80, 90]
        best_hpr = -np.inf
        best_threshold = 0

        for p in percentiles:
            threshold = np.percentile(consensus_scores, p)
            rejected_mask = consensus_scores > threshold
            rejection_rate = np.mean(rejected_mask)

            errors_in_rejected = np.sum((rejected_mask) & (hallucination_labels == 1))
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
                best_threshold = threshold

            print(f"\nThreshold p{p} ({threshold:.4f}):")
            print(f"  Rejection rate: {rejection_rate*100:.1f}%")
            print(f"  HPR: {HPR:.4f}")

        experiment_data[dataset_name]["metrics"]["HPR"].append(float(best_hpr))
        experiment_data[dataset_name]["metrics"]["accuracy"].append(float(accuracy))
        experiment_data[dataset_name]["metrics"]["auroc"].append(float(auroc_js))
        experiment_data[dataset_name]["metrics"]["auprc"].append(float(auprc_js))

        # Generate comprehensive visualizations
        fig, axes = plt.subplots(3, 3, figsize=(18, 15))

        correct_mask = hallucination_labels == 0
        halluc_mask = hallucination_labels == 1

        # Plot 1: JS Divergence scatter
        if np.any(correct_mask):
            axes[0, 0].scatter(
                consensus_scores[correct_mask],
                np.zeros(np.sum(correct_mask)),
                label="Correct",
                alpha=0.6,
                s=50,
                color="green",
            )
        if np.any(halluc_mask):
            axes[0, 0].scatter(
                consensus_scores[halluc_mask],
                np.ones(np.sum(halluc_mask)),
                label="Hallucination",
                alpha=0.6,
                s=50,
                color="red",
            )
        axes[0, 0].set_xlabel("JS Divergence")
        axes[0, 0].set_ylabel("Label")
        axes[0, 0].set_title(f"JS Divergence vs Label (AUROC={auroc_js:.3f})")
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Plot 2: Top-1 agreement
        if np.any(correct_mask):
            axes[0, 1].scatter(
                top1_agreement[correct_mask],
                np.zeros(np.sum(correct_mask)),
                alpha=0.6,
                s=50,
                color="green",
            )
        if np.any(halluc_mask):
            axes[0, 1].scatter(
                top1_agreement[halluc_mask],
                np.ones(np.sum(halluc_mask)),
                alpha=0.6,
                s=50,
                color="red",
            )
        axes[0, 1].set_xlabel("Top-1 Agreement")
        axes[0, 1].set_title(f"Top-1 Agreement (AUROC={auroc_top1:.3f})")
        axes[0, 1].grid(True, alpha=0.3)

        # Plot 3: Rank correlation
        if np.any(correct_mask):
            axes[0, 2].scatter(
                rank_correlation[correct_mask],
                np.zeros(np.sum(correct_mask)),
                alpha=0.6,
                s=50,
                color="green",
            )
        if np.any(halluc_mask):
            axes[0, 2].scatter(
                rank_correlation[halluc_mask],
                np.ones(np.sum(halluc_mask)),
                alpha=0.6,
                s=50,
                color="red",
            )
        axes[0, 2].set_xlabel("Rank Correlation")
        axes[0, 2].set_title(f"Rank Correlation (AUROC={auroc_rank:.3f})")
        axes[0, 2].grid(True, alpha=0.3)

        # Plot 4: ROC Curve
        fpr, tpr, _ = roc_curve(hallucination_labels, consensus_scores)
        axes[1, 0].plot(fpr, tpr, label=f"AUROC={auroc_js:.3f}", linewidth=2)
        axes[1, 0].plot([0, 1], [0, 1], "k--", alpha=0.3)
        axes[1, 0].set_xlabel("False Positive Rate")
        axes[1, 0].set_ylabel("True Positive Rate")
        axes[1, 0].set_title("ROC Curve")
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # Plot 5: Precision-Recall Curve
        precision, recall, _ = precision_recall_curve(
            hallucination_labels, consensus_scores
        )
        axes[1, 1].plot(recall, precision, label=f"AUPRC={auprc_js:.3f}", linewidth=2)
        axes[1, 1].set_xlabel("Recall")
        axes[1, 1].set_ylabel("Precision")
        axes[1, 1].set_title("Precision-Recall Curve")
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

        # Plot 6: Histogram comparison
        axes[1, 2].hist(
            consensus_scores[correct_mask],
            alpha=0.5,
            bins=20,
            label="Correct",
            color="green",
            density=True,
        )
        axes[1, 2].hist(
            consensus_scores[halluc_mask],
            alpha=0.5,
            bins=20,
            label="Hallucination",
            color="red",
            density=True,
        )
        axes[1, 2].set_xlabel("JS Divergence")
        axes[1, 2].set_ylabel("Density")
        axes[1, 2].set_title("Distribution Comparison")
        axes[1, 2].legend()
        axes[1, 2].grid(True, alpha=0.3)

        # Plot 7: Per-token trajectories (first 10 samples)
        for i in range(
            min(10, len(experiment_data[dataset_name]["per_token_consensus"]))
        ):
            token_scores = experiment_data[dataset_name]["per_token_consensus"][i]
            if len(token_scores) > 0:
                label = hallucination_labels[i]
                color = "red" if label == 1 else "green"
                axes[2, 0].plot(token_scores, alpha=0.4, color=color)
        axes[2, 0].set_xlabel("Token Position")
        axes[2, 0].set_ylabel("JS Divergence")
        axes[2, 0].set_title("Per-Token Trajectories")
        axes[2, 0].grid(True, alpha=0.3)

        # Plot 8: Early spike analysis
        if np.any(correct_mask):
            axes[2, 1].scatter(
                early_spike[correct_mask],
                np.zeros(np.sum(correct_mask)),
                alpha=0.6,
                s=50,
                color="green",
            )
        if np.any(halluc_mask):
            axes[2, 1].scatter(
                early_spike[halluc_mask],
                np.ones(np.sum(halluc_mask)),
                alpha=0.6,
                s=50,
                color="red",
            )
        axes[2, 1].set_xlabel("First Token JS Divergence")
        axes[2, 1].set_title(f"Early Spike (AUROC={auroc_spike:.3f})")
        axes[2, 1].grid(True, alpha=0.3)

        # Plot 9: Summary metrics
        metrics_text = f"Dataset: {dataset_name}\n"
        metrics_text += f"Samples: {len(hallucination_labels)}\n"
        metrics_text += f"Accuracy: {accuracy*100:.1f}%\n"
        metrics_text += f"Best HPR: {best_hpr:.4f}\n"
        metrics_text += f"AUROC: {auroc_js:.4f}\n"
        metrics_text += f"AUPRC: {auprc_js:.4f}\n"
        metrics_text += f"\nBest Metrics:\n"
        metrics_text += f"Top-1: {auroc_top1:.4f}\n"
        metrics_text += f"Rank: {auroc_rank:.4f}\n"
        metrics_text += f"Entropy: {auroc_entropy:.4f}"
        axes[2, 2].text(
            0.1,
            0.5,
            metrics_text,
            fontsize=11,
            verticalalignment="center",
            family="monospace",
        )
        axes[2, 2].axis("off")

        plt.tight_layout()
        plt.savefig(
            os.path.join(working_dir, f"{dataset_name}_comprehensive_analysis.png"),
            dpi=150,
            bbox_inches="tight",
        )
        plt.close()
        print(f"\nSaved comprehensive visualization for {dataset_name}")
    else:
        print("WARNING: Insufficient class diversity")
        experiment_data[dataset_name]["metrics"]["HPR"].append(0.0)
        experiment_data[dataset_name]["metrics"]["accuracy"].append(float(accuracy))
        experiment_data[dataset_name]["metrics"]["auroc"].append(0.5)
        experiment_data[dataset_name]["metrics"]["auprc"].append(0.5)

# Save all experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nSaved experiment data to {os.path.join(working_dir, 'experiment_data.npy')}")

print("\n" + "=" * 60)
print("EXPERIMENT COMPLETE")
print("=" * 60)
print(f"\nFinal Summary:")
for dataset_name in ["trivia_qa", "boolq", "commonsense_qa"]:
    metrics = experiment_data[dataset_name]["metrics"]
    print(
        f"{dataset_name}: Acc={metrics['accuracy'][0]*100:.1f}%, HPR={metrics['HPR'][0]:.4f}, AUROC={metrics['auroc'][0]:.4f}"
    )
