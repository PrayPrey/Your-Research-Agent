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

# Initialize experiment data structure with vocabulary overlap metrics
experiment_data = {
    "trivia_qa": {
        "baseline_js": [],
        "vocab_overlap_k5": [],
        "vocab_overlap_k10": [],
        "vocab_overlap_k20": [],
        "vocab_overlap_k50": [],
        "intersection_size_k5": [],
        "intersection_size_k10": [],
        "intersection_size_k20": [],
        "intersection_size_k50": [],
        "hallucination_labels": [],
        "generated_texts": [],
        "ground_truth": [],
        "metrics": {
            "baseline_auroc": [],
            "vocab_k5_auroc": [],
            "vocab_k10_auroc": [],
            "vocab_k20_auroc": [],
            "vocab_k50_auroc": [],
            "baseline_auprc": [],
            "vocab_k5_auprc": [],
            "vocab_k10_auprc": [],
            "vocab_k20_auprc": [],
            "vocab_k50_auprc": [],
        },
    },
    "boolq": {
        "baseline_js": [],
        "vocab_overlap_k5": [],
        "vocab_overlap_k10": [],
        "vocab_overlap_k20": [],
        "vocab_overlap_k50": [],
        "intersection_size_k5": [],
        "intersection_size_k10": [],
        "intersection_size_k20": [],
        "intersection_size_k50": [],
        "hallucination_labels": [],
        "generated_texts": [],
        "ground_truth": [],
        "metrics": {
            "baseline_auroc": [],
            "vocab_k5_auroc": [],
            "vocab_k10_auroc": [],
            "vocab_k20_auroc": [],
            "vocab_k50_auroc": [],
            "baseline_auprc": [],
            "vocab_k5_auprc": [],
            "vocab_k10_auprc": [],
            "vocab_k20_auprc": [],
            "vocab_k50_auprc": [],
        },
    },
    "commonsense_qa": {
        "baseline_js": [],
        "vocab_overlap_k5": [],
        "vocab_overlap_k10": [],
        "vocab_overlap_k20": [],
        "vocab_overlap_k50": [],
        "intersection_size_k5": [],
        "intersection_size_k10": [],
        "intersection_size_k20": [],
        "intersection_size_k50": [],
        "hallucination_labels": [],
        "generated_texts": [],
        "ground_truth": [],
        "metrics": {
            "baseline_auroc": [],
            "vocab_k5_auroc": [],
            "vocab_k10_auroc": [],
            "vocab_k20_auroc": [],
            "vocab_k50_auroc": [],
            "baseline_auprc": [],
            "vocab_k5_auprc": [],
            "vocab_k10_auprc": [],
            "vocab_k20_auprc": [],
            "vocab_k50_auprc": [],
        },
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


def compute_topk_jaccard_similarity(
    early_probs: torch.Tensor, late_probs: torch.Tensor, k: int
) -> tuple:
    """
    Compute Jaccard similarity of top-K token sets between early and late layers.
    Returns: (jaccard_similarity, intersection_size)
    """
    # Get top-K token indices
    early_topk = torch.topk(early_probs, k=k, dim=-1).indices.cpu().numpy().flatten()
    late_topk = torch.topk(late_probs, k=k, dim=-1).indices.cpu().numpy().flatten()

    # Convert to sets
    early_set = set(early_topk)
    late_set = set(late_topk)

    # Compute Jaccard similarity
    intersection = early_set & late_set
    union = early_set | late_set

    jaccard = len(intersection) / len(union) if len(union) > 0 else 0.0
    intersection_size = len(intersection)

    return jaccard, intersection_size


def compute_baseline_js_divergence(
    early_probs: torch.Tensor, late_probs: torch.Tensor
) -> float:
    """Compute baseline JS divergence for comparison"""
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

    return float(js_div)


def compute_vocab_overlap_metrics(
    early_probs: torch.Tensor, late_probs: torch.Tensor
) -> dict:
    """Compute vocabulary overlap metrics for multiple K values"""
    k_values = [5, 10, 20, 50]
    metrics = {}

    # Baseline JS divergence
    metrics["baseline_js"] = compute_baseline_js_divergence(early_probs, late_probs)

    # Vocabulary overlap for different K values
    for k in k_values:
        jaccard, intersection = compute_topk_jaccard_similarity(
            early_probs, late_probs, k
        )
        metrics[f"jaccard_k{k}"] = jaccard
        metrics[f"intersection_k{k}"] = intersection

    return metrics


def generate_with_vocab_overlap_monitoring(
    prompt: str, max_new_tokens: int = 20
) -> tuple:
    """Generate text while monitoring vocabulary overlap metrics"""
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    token_metrics = []

    num_layers = len(model.model.layers)
    early_layer_idx = num_layers // 4
    late_layer_idx = num_layers - 1

    for step in range(max_new_tokens):
        with torch.no_grad():
            outputs = model(input_ids, output_hidden_states=True)
            hidden_states = outputs.hidden_states

            early_hidden = hidden_states[early_layer_idx][:, -1, :]
            late_hidden = hidden_states[late_layer_idx][:, -1, :]

            # Get logits from each layer
            early_logits = model.lm_head(early_hidden)
            late_logits = model.lm_head(late_hidden)

            early_probs = F.softmax(early_logits, dim=-1)
            late_probs = F.softmax(late_logits, dim=-1)

            # Compute vocabulary overlap metrics
            metrics = compute_vocab_overlap_metrics(early_probs[0], late_probs[0])
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
    """Process TriviaQA dataset"""
    print(f"\n{'='*60}")
    print(f"Processing {dataset_name.upper()} - {num_samples} samples")
    print(f"{'='*60}")

    for idx, sample in enumerate(samples):
        if idx >= num_samples:
            break

        question = sample["question"]
        ground_truth = sample["answer"]["value"].lower().strip()

        prompt = f"[INST] Answer this question with a short factual answer: {question} [/INST]"

        generated_text, token_metrics = generate_with_vocab_overlap_monitoring(
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
        avg_baseline_js = (
            np.mean([m["baseline_js"] for m in token_metrics]) if token_metrics else 0.0
        )

        # Vocabulary overlap metrics (use 1 - jaccard as divergence score)
        avg_jaccard_k5 = (
            np.mean([m["jaccard_k5"] for m in token_metrics]) if token_metrics else 1.0
        )
        avg_jaccard_k10 = (
            np.mean([m["jaccard_k10"] for m in token_metrics]) if token_metrics else 1.0
        )
        avg_jaccard_k20 = (
            np.mean([m["jaccard_k20"] for m in token_metrics]) if token_metrics else 1.0
        )
        avg_jaccard_k50 = (
            np.mean([m["jaccard_k50"] for m in token_metrics]) if token_metrics else 1.0
        )

        avg_intersection_k5 = (
            np.mean([m["intersection_k5"] for m in token_metrics])
            if token_metrics
            else 5.0
        )
        avg_intersection_k10 = (
            np.mean([m["intersection_k10"] for m in token_metrics])
            if token_metrics
            else 10.0
        )
        avg_intersection_k20 = (
            np.mean([m["intersection_k20"] for m in token_metrics])
            if token_metrics
            else 20.0
        )
        avg_intersection_k50 = (
            np.mean([m["intersection_k50"] for m in token_metrics])
            if token_metrics
            else 50.0
        )

        experiment_data[dataset_name]["baseline_js"].append(avg_baseline_js)
        experiment_data[dataset_name]["vocab_overlap_k5"].append(
            1.0 - avg_jaccard_k5
        )  # Use divergence
        experiment_data[dataset_name]["vocab_overlap_k10"].append(1.0 - avg_jaccard_k10)
        experiment_data[dataset_name]["vocab_overlap_k20"].append(1.0 - avg_jaccard_k20)
        experiment_data[dataset_name]["vocab_overlap_k50"].append(1.0 - avg_jaccard_k50)
        experiment_data[dataset_name]["intersection_size_k5"].append(
            avg_intersection_k5
        )
        experiment_data[dataset_name]["intersection_size_k10"].append(
            avg_intersection_k10
        )
        experiment_data[dataset_name]["intersection_size_k20"].append(
            avg_intersection_k20
        )
        experiment_data[dataset_name]["intersection_size_k50"].append(
            avg_intersection_k50
        )
        experiment_data[dataset_name]["hallucination_labels"].append(
            hallucination_label
        )
        experiment_data[dataset_name]["generated_texts"].append(answer)
        experiment_data[dataset_name]["ground_truth"].append(ground_truth)

        if idx < 3 or idx % 50 == 0:
            print(f"\nExample {idx+1}:")
            print(f"Q: {question[:80]}...")
            print(f"GT: {ground_truth}")
            print(f"Generated: {answer}")
            print(f"Correct: {is_correct}")
            print(f"Baseline JS: {avg_baseline_js:.3f}")
            print(f"Vocab Overlap K=10 (1-J): {1.0 - avg_jaccard_k10:.3f}")


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

        generated_text, token_metrics = generate_with_vocab_overlap_monitoring(
            prompt, max_new_tokens=10
        )
        answer = extract_answer(generated_text, prompt)

        is_correct = ground_truth in answer
        hallucination_label = 0 if is_correct else 1

        avg_baseline_js = (
            np.mean([m["baseline_js"] for m in token_metrics]) if token_metrics else 0.0
        )

        avg_jaccard_k5 = (
            np.mean([m["jaccard_k5"] for m in token_metrics]) if token_metrics else 1.0
        )
        avg_jaccard_k10 = (
            np.mean([m["jaccard_k10"] for m in token_metrics]) if token_metrics else 1.0
        )
        avg_jaccard_k20 = (
            np.mean([m["jaccard_k20"] for m in token_metrics]) if token_metrics else 1.0
        )
        avg_jaccard_k50 = (
            np.mean([m["jaccard_k50"] for m in token_metrics]) if token_metrics else 1.0
        )

        avg_intersection_k5 = (
            np.mean([m["intersection_k5"] for m in token_metrics])
            if token_metrics
            else 5.0
        )
        avg_intersection_k10 = (
            np.mean([m["intersection_k10"] for m in token_metrics])
            if token_metrics
            else 10.0
        )
        avg_intersection_k20 = (
            np.mean([m["intersection_k20"] for m in token_metrics])
            if token_metrics
            else 20.0
        )
        avg_intersection_k50 = (
            np.mean([m["intersection_k50"] for m in token_metrics])
            if token_metrics
            else 50.0
        )

        experiment_data[dataset_name]["baseline_js"].append(avg_baseline_js)
        experiment_data[dataset_name]["vocab_overlap_k5"].append(1.0 - avg_jaccard_k5)
        experiment_data[dataset_name]["vocab_overlap_k10"].append(1.0 - avg_jaccard_k10)
        experiment_data[dataset_name]["vocab_overlap_k20"].append(1.0 - avg_jaccard_k20)
        experiment_data[dataset_name]["vocab_overlap_k50"].append(1.0 - avg_jaccard_k50)
        experiment_data[dataset_name]["intersection_size_k5"].append(
            avg_intersection_k5
        )
        experiment_data[dataset_name]["intersection_size_k10"].append(
            avg_intersection_k10
        )
        experiment_data[dataset_name]["intersection_size_k20"].append(
            avg_intersection_k20
        )
        experiment_data[dataset_name]["intersection_size_k50"].append(
            avg_intersection_k50
        )
        experiment_data[dataset_name]["hallucination_labels"].append(
            hallucination_label
        )
        experiment_data[dataset_name]["generated_texts"].append(answer)
        experiment_data[dataset_name]["ground_truth"].append(ground_truth)

        if idx < 3 or idx % 50 == 0:
            print(f"\nExample {idx+1}:")
            print(f"Q: {question[:80]}...")
            print(f"GT: {ground_truth}")
            print(f"Generated: {answer}")
            print(f"Correct: {is_correct}")


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

        generated_text, token_metrics = generate_with_vocab_overlap_monitoring(
            prompt, max_new_tokens=8
        )
        answer = extract_answer(generated_text, prompt)

        is_correct = correct_label.lower() in answer[:5]
        hallucination_label = 0 if is_correct else 1

        avg_baseline_js = (
            np.mean([m["baseline_js"] for m in token_metrics]) if token_metrics else 0.0
        )

        avg_jaccard_k5 = (
            np.mean([m["jaccard_k5"] for m in token_metrics]) if token_metrics else 1.0
        )
        avg_jaccard_k10 = (
            np.mean([m["jaccard_k10"] for m in token_metrics]) if token_metrics else 1.0
        )
        avg_jaccard_k20 = (
            np.mean([m["jaccard_k20"] for m in token_metrics]) if token_metrics else 1.0
        )
        avg_jaccard_k50 = (
            np.mean([m["jaccard_k50"] for m in token_metrics]) if token_metrics else 1.0
        )

        avg_intersection_k5 = (
            np.mean([m["intersection_k5"] for m in token_metrics])
            if token_metrics
            else 5.0
        )
        avg_intersection_k10 = (
            np.mean([m["intersection_k10"] for m in token_metrics])
            if token_metrics
            else 10.0
        )
        avg_intersection_k20 = (
            np.mean([m["intersection_k20"] for m in token_metrics])
            if token_metrics
            else 20.0
        )
        avg_intersection_k50 = (
            np.mean([m["intersection_k50"] for m in token_metrics])
            if token_metrics
            else 50.0
        )

        experiment_data[dataset_name]["baseline_js"].append(avg_baseline_js)
        experiment_data[dataset_name]["vocab_overlap_k5"].append(1.0 - avg_jaccard_k5)
        experiment_data[dataset_name]["vocab_overlap_k10"].append(1.0 - avg_jaccard_k10)
        experiment_data[dataset_name]["vocab_overlap_k20"].append(1.0 - avg_jaccard_k20)
        experiment_data[dataset_name]["vocab_overlap_k50"].append(1.0 - avg_jaccard_k50)
        experiment_data[dataset_name]["intersection_size_k5"].append(
            avg_intersection_k5
        )
        experiment_data[dataset_name]["intersection_size_k10"].append(
            avg_intersection_k10
        )
        experiment_data[dataset_name]["intersection_size_k20"].append(
            avg_intersection_k20
        )
        experiment_data[dataset_name]["intersection_size_k50"].append(
            avg_intersection_k50
        )
        experiment_data[dataset_name]["hallucination_labels"].append(
            hallucination_label
        )
        experiment_data[dataset_name]["generated_texts"].append(answer)
        experiment_data[dataset_name]["ground_truth"].append(correct_label)

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

# Comprehensive evaluation
print(f"\n{'='*60}")
print("ABLATION STUDY: VOCABULARY OVERLAP vs BASELINE JS DIVERGENCE")
print(f"{'='*60}")

for dataset_name in ["trivia_qa", "boolq", "commonsense_qa"]:
    print(f"\n{dataset_name.upper()}:")

    baseline_js = np.array(experiment_data[dataset_name]["baseline_js"])
    vocab_k5 = np.array(experiment_data[dataset_name]["vocab_overlap_k5"])
    vocab_k10 = np.array(experiment_data[dataset_name]["vocab_overlap_k10"])
    vocab_k20 = np.array(experiment_data[dataset_name]["vocab_overlap_k20"])
    vocab_k50 = np.array(experiment_data[dataset_name]["vocab_overlap_k50"])
    hallucination_labels = np.array(
        experiment_data[dataset_name]["hallucination_labels"]
    )

    # Filter valid values
    valid_mask = np.isfinite(baseline_js) & np.isfinite(vocab_k10)
    baseline_js = baseline_js[valid_mask]
    vocab_k5 = vocab_k5[valid_mask]
    vocab_k10 = vocab_k10[valid_mask]
    vocab_k20 = vocab_k20[valid_mask]
    vocab_k50 = vocab_k50[valid_mask]
    hallucination_labels = hallucination_labels[valid_mask]

    n_correct = np.sum(hallucination_labels == 0)
    n_hallucination = np.sum(hallucination_labels == 1)
    accuracy = (
        n_correct / len(hallucination_labels) if len(hallucination_labels) > 0 else 0
    )

    print(f"Total samples: {len(hallucination_labels)}")
    print(f"Correct: {n_correct} ({accuracy*100:.1f}%)")
    print(f"Hallucinations: {n_hallucination} ({(1-accuracy)*100:.1f}%)")

    if len(np.unique(hallucination_labels)) > 1:
        # Compute AUROC and AUPRC for all metrics
        auroc_baseline = roc_auc_score(hallucination_labels, baseline_js)
        auprc_baseline = average_precision_score(hallucination_labels, baseline_js)

        auroc_k5 = roc_auc_score(hallucination_labels, vocab_k5)
        auprc_k5 = average_precision_score(hallucination_labels, vocab_k5)

        auroc_k10 = roc_auc_score(hallucination_labels, vocab_k10)
        auprc_k10 = average_precision_score(hallucination_labels, vocab_k10)

        auroc_k20 = roc_auc_score(hallucination_labels, vocab_k20)
        auprc_k20 = average_precision_score(hallucination_labels, vocab_k20)

        auroc_k50 = roc_auc_score(hallucination_labels, vocab_k50)
        auprc_k50 = average_precision_score(hallucination_labels, vocab_k50)

        print(f"\nAUROC Scores:")
        print(f"  Baseline (JS Divergence): {auroc_baseline:.4f}")
        print(
            f"  Vocab Overlap K=5:        {auroc_k5:.4f} (Δ={auroc_k5-auroc_baseline:+.4f})"
        )
        print(
            f"  Vocab Overlap K=10:       {auroc_k10:.4f} (Δ={auroc_k10-auroc_baseline:+.4f})"
        )
        print(
            f"  Vocab Overlap K=20:       {auroc_k20:.4f} (Δ={auroc_k20-auroc_baseline:+.4f})"
        )
        print(
            f"  Vocab Overlap K=50:       {auroc_k50:.4f} (Δ={auroc_k50-auroc_baseline:+.4f})"
        )

        print(f"\nAUPRC Scores:")
        print(f"  Baseline (JS Divergence): {auprc_baseline:.4f}")
        print(
            f"  Vocab Overlap K=5:        {auprc_k5:.4f} (Δ={auprc_k5-auprc_baseline:+.4f})"
        )
        print(
            f"  Vocab Overlap K=10:       {auprc_k10:.4f} (Δ={auprc_k10-auprc_baseline:+.4f})"
        )
        print(
            f"  Vocab Overlap K=20:       {auprc_k20:.4f} (Δ={auprc_k20-auprc_baseline:+.4f})"
        )
        print(
            f"  Vocab Overlap K=50:       {auprc_k50:.4f} (Δ={auprc_k50-auprc_baseline:+.4f})"
        )

        # Store metrics
        experiment_data[dataset_name]["metrics"]["baseline_auroc"].append(
            float(auroc_baseline)
        )
        experiment_data[dataset_name]["metrics"]["vocab_k5_auroc"].append(
            float(auroc_k5)
        )
        experiment_data[dataset_name]["metrics"]["vocab_k10_auroc"].append(
            float(auroc_k10)
        )
        experiment_data[dataset_name]["metrics"]["vocab_k20_auroc"].append(
            float(auroc_k20)
        )
        experiment_data[dataset_name]["metrics"]["vocab_k50_auroc"].append(
            float(auroc_k50)
        )
        experiment_data[dataset_name]["metrics"]["baseline_auprc"].append(
            float(auprc_baseline)
        )
        experiment_data[dataset_name]["metrics"]["vocab_k5_auprc"].append(
            float(auprc_k5)
        )
        experiment_data[dataset_name]["metrics"]["vocab_k10_auprc"].append(
            float(auprc_k10)
        )
        experiment_data[dataset_name]["metrics"]["vocab_k20_auprc"].append(
            float(auprc_k20)
        )
        experiment_data[dataset_name]["metrics"]["vocab_k50_auprc"].append(
            float(auprc_k50)
        )

        # Spearman correlations
        corr_baseline, _ = spearmanr(baseline_js, hallucination_labels)
        corr_k10, _ = spearmanr(vocab_k10, hallucination_labels)

        print(f"\nSpearman Correlations with Hallucination:")
        print(f"  Baseline: {corr_baseline:.4f}")
        print(f"  Vocab K=10: {corr_k10:.4f}")

        # Create comprehensive visualization
        fig, axes = plt.subplots(3, 3, figsize=(18, 15))

        correct_mask = hallucination_labels == 0
        halluc_mask = hallucination_labels == 1

        # Plot 1: Baseline JS scatter
        if np.any(correct_mask):
            axes[0, 0].scatter(
                baseline_js[correct_mask],
                np.zeros(np.sum(correct_mask)),
                label="Correct",
                alpha=0.6,
                s=50,
                color="green",
            )
        if np.any(halluc_mask):
            axes[0, 0].scatter(
                baseline_js[halluc_mask],
                np.ones(np.sum(halluc_mask)),
                label="Hallucination",
                alpha=0.6,
                s=50,
                color="red",
            )
        axes[0, 0].set_xlabel("Baseline JS Divergence")
        axes[0, 0].set_ylabel("Label")
        axes[0, 0].set_title(f"Baseline (AUROC={auroc_baseline:.3f})")
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Plot 2: Vocab Overlap K=5
        if np.any(correct_mask):
            axes[0, 1].scatter(
                vocab_k5[correct_mask],
                np.zeros(np.sum(correct_mask)),
                alpha=0.6,
                s=50,
                color="green",
            )
        if np.any(halluc_mask):
            axes[0, 1].scatter(
                vocab_k5[halluc_mask],
                np.ones(np.sum(halluc_mask)),
                alpha=0.6,
                s=50,
                color="red",
            )
        axes[0, 1].set_xlabel("Vocab Overlap K=5 (1-Jaccard)")
        axes[0, 1].set_title(f"K=5 (AUROC={auroc_k5:.3f})")
        axes[0, 1].grid(True, alpha=0.3)

        # Plot 3: Vocab Overlap K=10
        if np.any(correct_mask):
            axes[0, 2].scatter(
                vocab_k10[correct_mask],
                np.zeros(np.sum(correct_mask)),
                alpha=0.6,
                s=50,
                color="green",
            )
        if np.any(halluc_mask):
            axes[0, 2].scatter(
                vocab_k10[halluc_mask],
                np.ones(np.sum(halluc_mask)),
                alpha=0.6,
                s=50,
                color="red",
            )
        axes[0, 2].set_xlabel("Vocab Overlap K=10 (1-Jaccard)")
        axes[0, 2].set_title(f"K=10 (AUROC={auroc_k10:.3f})")
        axes[0, 2].grid(True, alpha=0.3)

        # Plot 4: Vocab Overlap K=20
        if np.any(correct_mask):
            axes[1, 0].scatter(
                vocab_k20[correct_mask],
                np.zeros(np.sum(correct_mask)),
                alpha=0.6,
                s=50,
                color="green",
            )
        if np.any(halluc_mask):
            axes[1, 0].scatter(
                vocab_k20[halluc_mask],
                np.ones(np.sum(halluc_mask)),
                alpha=0.6,
                s=50,
                color="red",
            )
        axes[1, 0].set_xlabel("Vocab Overlap K=20 (1-Jaccard)")
        axes[1, 0].set_title(f"K=20 (AUROC={auroc_k20:.3f})")
        axes[1, 0].grid(True, alpha=0.3)

        # Plot 5: Vocab Overlap K=50
        if np.any(correct_mask):
            axes[1, 1].scatter(
                vocab_k50[correct_mask],
                np.zeros(np.sum(correct_mask)),
                alpha=0.6,
                s=50,
                color="green",
            )
        if np.any(halluc_mask):
            axes[1, 1].scatter(
                vocab_k50[halluc_mask],
                np.ones(np.sum(halluc_mask)),
                alpha=0.6,
                s=50,
                color="red",
            )
        axes[1, 1].set_xlabel("Vocab Overlap K=50 (1-Jaccard)")
        axes[1, 1].set_title(f"K=50 (AUROC={auroc_k50:.3f})")
        axes[1, 1].grid(True, alpha=0.3)

        # Plot 6: ROC Curves Comparison
        fpr_baseline, tpr_baseline, _ = roc_curve(hallucination_labels, baseline_js)
        fpr_k10, tpr_k10, _ = roc_curve(hallucination_labels, vocab_k10)
        fpr_k20, tpr_k20, _ = roc_curve(hallucination_labels, vocab_k20)

        axes[1, 2].plot(
            fpr_baseline,
            tpr_baseline,
            label=f"Baseline ({auroc_baseline:.3f})",
            linewidth=2,
        )
        axes[1, 2].plot(fpr_k10, tpr_k10, label=f"K=10 ({auroc_k10:.3f})", linewidth=2)
        axes[1, 2].plot(fpr_k20, tpr_k20, label=f"K=20 ({auroc_k20:.3f})", linewidth=2)
        axes[1, 2].plot([0, 1], [0, 1], "k--", alpha=0.3)
        axes[1, 2].set_xlabel("False Positive Rate")
        axes[1, 2].set_ylabel("True Positive Rate")
        axes[1, 2].set_title("ROC Curves Comparison")
        axes[1, 2].legend()
        axes[1, 2].grid(True, alpha=0.3)

        # Plot 7: Histogram comparison (Baseline)
        axes[2, 0].hist(
            baseline_js[correct_mask],
            alpha=0.5,
            bins=20,
            label="Correct",
            color="green",
            density=True,
        )
        axes[2, 0].hist(
            baseline_js[halluc_mask],
            alpha=0.5,
            bins=20,
            label="Hallucination",
            color="red",
            density=True,
        )
        axes[2, 0].set_xlabel("Baseline JS Divergence")
        axes[2, 0].set_ylabel("Density")
        axes[2, 0].set_title("Baseline Distribution")
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3)

        # Plot 8: Histogram comparison (K=10)
        axes[2, 1].hist(
            vocab_k10[correct_mask],
            alpha=0.5,
            bins=20,
            label="Correct",
            color="green",
            density=True,
        )
        axes[2, 1].hist(
            vocab_k10[halluc_mask],
            alpha=0.5,
            bins=20,
            label="Hallucination",
            color="red",
            density=True,
        )
        axes[2, 1].set_xlabel("Vocab Overlap K=10")
        axes[2, 1].set_ylabel("Density")
        axes[2, 1].set_title("K=10 Distribution")
        axes[2, 1].legend()
        axes[2, 1].grid(True, alpha=0.3)

        # Plot 9: AUROC comparison bar chart
        k_values = ["Baseline", "K=5", "K=10", "K=20", "K=50"]
        auroc_values = [auroc_baseline, auroc_k5, auroc_k10, auroc_k20, auroc_k50]
        colors = ["blue" if v < auroc_baseline else "green" for v in auroc_values[1:]]
        colors.insert(0, "blue")

        axes[2, 2].bar(k_values, auroc_values, color=colors, alpha=0.7)
        axes[2, 2].axhline(y=0.5, color="k", linestyle="--", alpha=0.3)
        axes[2, 2].set_ylabel("AUROC")
        axes[2, 2].set_title("AUROC Comparison")
        axes[2, 2].grid(True, alpha=0.3, axis="y")
        axes[2, 2].tick_params(axis="x", rotation=45)

        plt.tight_layout()
        plt.savefig(
            os.path.join(working_dir, f"{dataset_name}_vocab_overlap_ablation.png"),
            dpi=150,
            bbox_inches="tight",
        )
        plt.close()
        print(f"\nSaved visualization for {dataset_name}")
    else:
        print("WARNING: Insufficient class diversity")

# Save all experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nSaved experiment data to {os.path.join(working_dir, 'experiment_data.npy')}")

print("\n" + "=" * 60)
print("ABLATION STUDY COMPLETE")
print("=" * 60)
print(f"\nFinal Summary:")
for dataset_name in ["trivia_qa", "boolq", "commonsense_qa"]:
    metrics = experiment_data[dataset_name]["metrics"]
    if metrics["baseline_auroc"]:
        baseline = metrics["baseline_auroc"][0]
        k10 = metrics["vocab_k10_auroc"][0]
        k20 = metrics["vocab_k20_auroc"][0]
        print(
            f"{dataset_name}: Baseline AUROC={baseline:.4f}, K=10 AUROC={k10:.4f} (Δ={k10-baseline:+.4f}), K=20 AUROC={k20:.4f} (Δ={k20-baseline:+.4f})"
        )
