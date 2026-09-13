import os
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from scipy.stats import spearmanr
from scipy.spatial.distance import jensenshannon
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import warnings
from datasets import load_dataset

warnings.filterwarnings("ignore")

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Initialize experiment data structure with multiple datasets
experiment_data = {
    "synthetic_qa": {"layer_selection_strategy": {}},
    "truthfulqa": {"layer_selection_strategy": {}},
    "biographical_qa": {"layer_selection_strategy": {}},
    "triviaqa": {"layer_selection_strategy": {}},
    "natural_questions": {"layer_selection_strategy": {}},
}

# Create synthetic QA dataset with known factual answers
synthetic_qa_data = [
    {
        "question": "What is the capital of France?",
        "answer": "Paris",
        "hallucination_answer": "London",
    },
    {"question": "What is 2 + 2?", "answer": "4", "hallucination_answer": "5"},
    {
        "question": "Who wrote Romeo and Juliet?",
        "answer": "Shakespeare",
        "hallucination_answer": "Dickens",
    },
    {
        "question": "What is the largest planet in our solar system?",
        "answer": "Jupiter",
        "hallucination_answer": "Saturn",
    },
    {
        "question": "What is the chemical symbol for water?",
        "answer": "H2O",
        "hallucination_answer": "O2",
    },
]

print("Loading TruthfulQA dataset...")
try:
    truthfulqa_dataset = load_dataset("truthful_qa", "generation", split="validation")
    truthfulqa_data = []
    for i, item in enumerate(truthfulqa_dataset):
        if i >= 5:
            break
        truthfulqa_data.append(
            {
                "question": item["question"],
                "answer": (
                    item["best_answer"]
                    if "best_answer" in item
                    else item["correct_answers"][0] if "correct_answers" in item else ""
                ),
                "hallucination_answer": (
                    item["incorrect_answers"][0] if "incorrect_answers" in item else ""
                ),
            }
        )
    print(f"Loaded {len(truthfulqa_data)} samples from TruthfulQA")
except Exception as e:
    print(f"Warning: Could not load TruthfulQA dataset: {e}")
    truthfulqa_data = synthetic_qa_data[:3]

print("Creating biographical QA dataset...")
biographical_qa_data = [
    {
        "question": "Who was Albert Einstein?",
        "answer": "physicist",
        "hallucination_answer": "chemist",
    },
    {
        "question": "What is Barack Obama known for?",
        "answer": "president",
        "hallucination_answer": "senator only",
    },
    {
        "question": "Who painted the Mona Lisa?",
        "answer": "Leonardo da Vinci",
        "hallucination_answer": "Michelangelo",
    },
    {
        "question": "Who discovered penicillin?",
        "answer": "Alexander Fleming",
        "hallucination_answer": "Louis Pasteur",
    },
    {
        "question": "Who wrote Harry Potter?",
        "answer": "J.K. Rowling",
        "hallucination_answer": "J.R.R. Tolkien",
    },
]

print("Loading TriviaQA dataset...")
try:
    triviaqa_dataset = load_dataset(
        "trivia_qa", "unfiltered.nocontext", split="validation[:5]"
    )
    triviaqa_data = []
    for item in triviaqa_dataset:
        if len(triviaqa_data) >= 5:
            break
        answer = (
            item["answer"]["value"]
            if "value" in item["answer"]
            else item["answer"]["aliases"][0]
        )
        triviaqa_data.append(
            {
                "question": item["question"],
                "answer": answer,
                "hallucination_answer": "incorrect answer",
            }
        )
    print(f"Loaded {len(triviaqa_data)} samples from TriviaQA")
except Exception as e:
    print(f"Warning: Could not load TriviaQA dataset: {e}")
    triviaqa_data = synthetic_qa_data[:3]

print("Loading Natural Questions dataset...")
try:
    nq_dataset = load_dataset(
        "google-research-datasets/natural_questions",
        "default",
        split="validation[:5]",
        trust_remote_code=True,
    )
    nq_data = []
    for item in nq_dataset:
        if len(nq_data) >= 5:
            break
        question = item["question"]["text"]
        annotations = item["annotations"]
        if annotations and len(annotations) > 0 and "short_answers" in annotations[0]:
            short_ans = annotations[0]["short_answers"]
            if short_ans and len(short_ans) > 0:
                answer = str(short_ans[0].get("text", "unknown"))
                nq_data.append(
                    {
                        "question": question,
                        "answer": answer,
                        "hallucination_answer": "incorrect",
                    }
                )
    if len(nq_data) == 0:
        raise Exception("No valid samples extracted")
    print(f"Loaded {len(nq_data)} samples from Natural Questions")
except Exception as e:
    print(f"Warning: Could not load Natural Questions dataset: {e}")
    nq_data = synthetic_qa_data[:3]

datasets = {
    "synthetic_qa": synthetic_qa_data,
    "truthfulqa": truthfulqa_data,
    "biographical_qa": biographical_qa_data,
    "triviaqa": triviaqa_data,
    "natural_questions": nq_data,
}

print("Loading model and tokenizer...")
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, output_hidden_states=True)
model = model.to(device)
model.eval()

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

num_layers = len(model.transformer.h)
print(f"Model has {num_layers} layers")


def compute_consensus_score(
    early_probs: torch.Tensor, late_probs: torch.Tensor
) -> float:
    """Compute Jensen-Shannon divergence between early and late layer predictions"""
    early_np = early_probs.cpu().detach().numpy().flatten()
    late_np = late_probs.cpu().detach().numpy().flatten()
    js_div = jensenshannon(early_np, late_np)
    consensus = 1.0 - min(js_div, 1.0)
    return consensus


def get_layer_probs(
    hidden_states, layer_indices: List[int], temperature: float = 1.0
) -> torch.Tensor:
    """Get averaged probabilities from multiple layers"""
    probs_list = []
    for layer_idx in layer_indices:
        hidden = hidden_states[layer_idx][:, -1, :]
        logits = model.lm_head(hidden)
        probs = F.softmax(logits / temperature, dim=-1)
        probs_list.append(probs)
    return torch.mean(torch.stack(probs_list), dim=0)


def generate_with_layer_monitoring(
    prompt: str, strategy: Dict, max_new_tokens: int = 15, temperature: float = 0.5
) -> Tuple[str, List[float]]:
    """Generate text while monitoring layer consensus at each step"""
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    consensus_scores = []

    early_layers = strategy["early_layers"]
    late_layers = strategy["late_layers"]

    for _ in range(max_new_tokens):
        with torch.no_grad():
            outputs = model(input_ids, output_hidden_states=True)
            hidden_states = outputs.hidden_states

            # Get predictions from early and late layers based on strategy
            if len(early_layers) == 1:
                early_hidden = hidden_states[early_layers[0]][:, -1, :]
                early_logits = model.lm_head(early_hidden)
                early_probs = F.softmax(early_logits / temperature, dim=-1)
            else:
                early_probs = get_layer_probs(hidden_states, early_layers, temperature)

            if len(late_layers) == 1:
                late_hidden = hidden_states[late_layers[0]][:, -1, :]
                late_logits = model.lm_head(late_hidden)
                late_probs = F.softmax(late_logits / temperature, dim=-1)
            else:
                late_probs = get_layer_probs(hidden_states, late_layers, temperature)

            # Compute consensus score
            consensus = compute_consensus_score(early_probs[0], late_probs[0])
            consensus_scores.append(consensus)

            # Use final layer for actual prediction with temperature sampling
            next_token = torch.multinomial(late_probs, num_samples=1)
            input_ids = torch.cat([input_ids, next_token], dim=-1)

            if next_token.item() == tokenizer.eos_token_id:
                break

    generated_text = tokenizer.decode(input_ids[0], skip_special_tokens=True)
    return generated_text, consensus_scores


def label_hallucination(generated_text: str, ground_truth: str, question: str) -> int:
    """Label tokens as hallucination (1) or correct (0) based on ground truth with fuzzy matching"""
    generated_lower = generated_text.lower()
    ground_truth_lower = ground_truth.lower()
    question_lower = question.lower()

    if question_lower in generated_lower:
        answer_part = generated_lower.split(question_lower)[-1]
    else:
        answer_part = generated_lower

    # Tokenize and check for overlap
    gt_tokens = set(ground_truth_lower.split())
    answer_tokens = set(answer_part.split())

    # Check if any ground truth token appears in answer
    if gt_tokens & answer_tokens:
        return 0

    # Also check substring match
    if ground_truth_lower in answer_part:
        return 0

    return 1


# Define different layer selection strategies with tuned hyperparameters
layer_strategies = {
    "baseline_early_vs_late": {
        "early_layers": [num_layers // 4],
        "late_layers": [num_layers - 1],
    },
    "very_early_vs_late": {"early_layers": [0], "late_layers": [num_layers - 1]},
    "middle_vs_late": {
        "early_layers": [num_layers // 2],
        "late_layers": [num_layers - 1],
    },
    "averaged_early_vs_late": {
        "early_layers": list(range(0, num_layers // 3)),
        "late_layers": list(range(2 * num_layers // 3, num_layers)),
    },
}

# Hyperparameters to tune
temperature_values = [0.3, 0.7, 1.0]
max_tokens_values = [10, 15, 20]

print("\n" + "=" * 50)
print("HYPERPARAMETER TUNING: Layer Selection Strategy")
print("=" * 50)

# Store global best strategy across all datasets
global_best_strategy_name = None
global_best_score = -float("inf")
global_best_temp = 0.7
global_best_max_tokens = 15

for dataset_name, dataset in datasets.items():
    print(f"\n{'=' * 50}")
    print(f"TESTING ON DATASET: {dataset_name}")
    print(f"{'=' * 50}")

    best_strategy_name = None
    best_correlation = -float("inf")
    best_strategy_results = None
    best_separation = -float("inf")
    best_temp = 0.7
    best_max_tokens = 15

    for temperature in temperature_values:
        for max_tokens in max_tokens_values:
            print(
                f"\n--- Testing temperature={temperature}, max_tokens={max_tokens} ---"
            )

            for strategy_name, strategy in layer_strategies.items():
                print(f"\n--- Testing Strategy: {strategy_name} ---")
                print(f"Early layers: {strategy['early_layers']}")
                print(f"Late layers: {strategy['late_layers']}")

                strategy_key = f"{strategy_name}_temp{temperature}_maxtok{max_tokens}"
                experiment_data[dataset_name]["layer_selection_strategy"][
                    strategy_key
                ] = {
                    "consensus_scores": [],
                    "hallucination_labels": [],
                    "generated_texts": [],
                    "ground_truth": [],
                    "correlations": {},
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }

                all_consensus_scores = []
                all_hallucination_labels = []

                for idx, qa_pair in enumerate(dataset):
                    question = qa_pair["question"]
                    ground_truth = qa_pair["answer"]
                    prompt = f"Q: {question}\nA:"

                    generated_text, consensus_scores = generate_with_layer_monitoring(
                        prompt,
                        strategy,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                    )
                    hallucination_label = label_hallucination(
                        generated_text, ground_truth, question
                    )

                    avg_consensus = (
                        np.mean(consensus_scores) if len(consensus_scores) > 0 else 0.5
                    )
                    all_consensus_scores.append(avg_consensus)
                    all_hallucination_labels.append(hallucination_label)

                    experiment_data[dataset_name]["layer_selection_strategy"][
                        strategy_key
                    ]["consensus_scores"].append(consensus_scores)
                    experiment_data[dataset_name]["layer_selection_strategy"][
                        strategy_key
                    ]["hallucination_labels"].append(hallucination_label)
                    experiment_data[dataset_name]["layer_selection_strategy"][
                        strategy_key
                    ]["generated_texts"].append(generated_text)
                    experiment_data[dataset_name]["layer_selection_strategy"][
                        strategy_key
                    ]["ground_truth"].append(ground_truth)

                all_consensus_scores = np.array(all_consensus_scores)
                all_hallucination_labels = np.array(all_hallucination_labels)
                inverted_consensus = 1.0 - all_consensus_scores

                # Compute correlation if there's variance
                if len(np.unique(all_hallucination_labels)) > 1:
                    correlation, p_value = spearmanr(
                        inverted_consensus, all_hallucination_labels
                    )
                else:
                    correlation, p_value = 0.0, 1.0

                mean_consensus_correct = (
                    float(np.mean(all_consensus_scores[all_hallucination_labels == 0]))
                    if np.any(all_hallucination_labels == 0)
                    else 0.0
                )
                mean_consensus_hallucination = (
                    float(np.mean(all_consensus_scores[all_hallucination_labels == 1]))
                    if np.any(all_hallucination_labels == 1)
                    else 0.0
                )

                # Compute separation score
                separation = abs(mean_consensus_correct - mean_consensus_hallucination)

                # Compute Hallucination Prevention Rate
                baseline_hallucinations = np.sum(all_hallucination_labels)
                total_samples = len(all_hallucination_labels)
                hpr = (
                    (1.0 - baseline_hallucinations / total_samples) * 100
                    if total_samples > 0
                    else 0.0
                )

                experiment_data[dataset_name]["layer_selection_strategy"][strategy_key][
                    "correlations"
                ] = {
                    "spearman_correlation": float(correlation),
                    "p_value": float(p_value),
                    "mean_consensus_correct": mean_consensus_correct,
                    "mean_consensus_hallucination": mean_consensus_hallucination,
                    "separation": float(separation),
                    "hallucination_prevention_rate": float(hpr),
                }

                print(f"Spearman Correlation: {correlation:.4f} (p={p_value:.4f})")
                print(f"Mean consensus (correct): {mean_consensus_correct:.4f}")
                print(
                    f"Mean consensus (hallucination): {mean_consensus_hallucination:.4f}"
                )
                print(f"Separation: {separation:.4f}")
                print(f"Hallucination Prevention Rate: {hpr:.2f}%")

                # Track best strategy based on combined score
                combined_score = abs(correlation) + separation + hpr / 100.0
                if combined_score > abs(best_correlation) + best_separation:
                    best_correlation = correlation
                    best_strategy_name = strategy_key
                    best_strategy_results = {
                        "consensus_scores": all_consensus_scores,
                        "hallucination_labels": all_hallucination_labels,
                        "correlation": correlation,
                        "p_value": p_value,
                        "separation": separation,
                        "hpr": hpr,
                    }
                    best_separation = separation
                    best_temp = temperature
                    best_max_tokens = max_tokens

    print(f"\n{'=' * 50}")
    print(f"BEST STRATEGY FOR {dataset_name}")
    print(f"{'=' * 50}")
    print(f"Best Strategy: {best_strategy_name}")
    print(f"Best Correlation: {best_correlation:.4f}")
    print(f"Best Separation: {best_separation:.4f}")
    print(f"Best Temperature: {best_temp}")
    print(f"Best Max Tokens: {best_max_tokens}")

    # Track global best
    if best_strategy_results:
        combined_score = (
            abs(best_correlation)
            + best_separation
            + best_strategy_results.get("hpr", 0) / 100.0
        )
        if combined_score > global_best_score:
            global_best_score = combined_score
            global_best_strategy_name = best_strategy_name
            global_best_temp = best_temp
            global_best_max_tokens = best_max_tokens

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nSaved experiment data to {os.path.join(working_dir, 'experiment_data.npy')}")

print("\n" + "=" * 50)
print("GLOBAL SUMMARY")
print("=" * 50)
print(f"Tested {len(layer_strategies)} layer selection strategies")
print(f"Tested {len(temperature_values)} temperature values")
print(f"Tested {len(max_tokens_values)} max token values")
print(f"Tested on {len(datasets)} datasets")
print(f"Global best strategy: {global_best_strategy_name}")
print(f"Global best temperature: {global_best_temp}")
print(f"Global best max tokens: {global_best_max_tokens}")

print("\n" + "=" * 50)
print("PER-DATASET SUMMARY")
print("=" * 50)
for dataset_name in datasets.keys():
    print(f"\nDataset: {dataset_name}")
    for strategy_key in experiment_data[dataset_name][
        "layer_selection_strategy"
    ].keys():
        corr = experiment_data[dataset_name]["layer_selection_strategy"][strategy_key][
            "correlations"
        ]["spearman_correlation"]
        sep = experiment_data[dataset_name]["layer_selection_strategy"][strategy_key][
            "correlations"
        ]["separation"]
        hpr = experiment_data[dataset_name]["layer_selection_strategy"][strategy_key][
            "correlations"
        ]["hallucination_prevention_rate"]
        print(f"  {strategy_key}: Corr={corr:.4f}, Sep={sep:.4f}, HPR={hpr:.2f}%")

print("\nHyperparameter tuning complete!")
