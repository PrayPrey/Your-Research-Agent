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

warnings.filterwarnings("ignore")

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Initialize experiment data structure
experiment_data = {
    "synthetic_qa": {
        "consensus_scores": [],
        "hallucination_labels": [],
        "correlations": [],
        "generated_texts": [],
        "ground_truth": [],
    }
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
    {
        "question": "How many continents are there?",
        "answer": "seven",
        "hallucination_answer": "six",
    },
    {
        "question": "What year did World War 2 end?",
        "answer": "1945",
        "hallucination_answer": "1944",
    },
    {
        "question": "What is the speed of light?",
        "answer": "299792458",
        "hallucination_answer": "300000000",
    },
]

print("Loading model and tokenizer...")
model_name = "gpt2"  # Using smaller model for faster experimentation
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, output_hidden_states=True)
model = model.to(device)
model.eval()

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


def get_layer_predictions(hidden_states, layer_indices: List[int]) -> torch.Tensor:
    """Extract predictions from specific layers"""
    predictions = []
    for layer_idx in layer_indices:
        hidden = hidden_states[layer_idx]
        # Get last token's hidden state and project to vocab
        last_hidden = hidden[:, -1, :]
        logits = model.lm_head(last_hidden)
        probs = F.softmax(logits, dim=-1)
        predictions.append(probs)
    return torch.stack(predictions)


def compute_consensus_score(
    early_probs: torch.Tensor, late_probs: torch.Tensor
) -> float:
    """Compute Jensen-Shannon divergence between early and late layer predictions"""
    early_np = early_probs.cpu().detach().numpy().flatten()
    late_np = late_probs.cpu().detach().numpy().flatten()
    # Jensen-Shannon divergence (lower = more agreement)
    js_div = jensenshannon(early_np, late_np)
    # Convert to consensus score (higher = more agreement)
    consensus = 1.0 - min(js_div, 1.0)
    return consensus


def generate_with_layer_monitoring(
    prompt: str, max_new_tokens: int = 15
) -> Tuple[str, List[float]]:
    """Generate text while monitoring layer consensus at each step"""
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    consensus_scores = []

    num_layers = len(model.transformer.h)
    early_layer_idx = num_layers // 4  # First quarter
    late_layer_idx = num_layers - 1  # Last layer

    for _ in range(max_new_tokens):
        with torch.no_grad():
            outputs = model(input_ids, output_hidden_states=True)
            hidden_states = outputs.hidden_states

            # Get predictions from early and late layers
            early_hidden = hidden_states[early_layer_idx][:, -1, :]
            late_hidden = hidden_states[late_layer_idx][:, -1, :]

            early_logits = model.lm_head(early_hidden)
            late_logits = model.lm_head(late_hidden)

            early_probs = F.softmax(early_logits, dim=-1)
            late_probs = F.softmax(late_logits, dim=-1)

            # Compute consensus score
            consensus = compute_consensus_score(early_probs[0], late_probs[0])
            consensus_scores.append(consensus)

            # Use final layer for actual prediction (baseline greedy decoding)
            next_token = torch.argmax(late_probs, dim=-1)
            input_ids = torch.cat([input_ids, next_token.unsqueeze(0)], dim=-1)

            # Stop if EOS token
            if next_token.item() == tokenizer.eos_token_id:
                break

    generated_text = tokenizer.decode(input_ids[0], skip_special_tokens=True)
    return generated_text, consensus_scores


def label_hallucination(
    generated_text: str, ground_truth: str, question: str
) -> List[int]:
    """Label tokens as hallucination (1) or correct (0) based on ground truth"""
    # Simple heuristic: if ground truth answer appears in generated text, label as correct
    generated_lower = generated_text.lower()
    ground_truth_lower = ground_truth.lower()

    # Extract the part after the question
    question_lower = question.lower()
    if question_lower in generated_lower:
        answer_part = generated_lower.split(question_lower)[-1]
    else:
        answer_part = generated_lower

    # Check if ground truth is in the answer
    contains_truth = ground_truth_lower in answer_part

    # Create per-token labels (simplified: all tokens get same label for this baseline)
    # In practice, this would be more fine-grained
    return 0 if contains_truth else 1


print("\nGenerating text and computing layer consensus scores...")
all_consensus_scores = []
all_hallucination_labels = []

for idx, qa_pair in enumerate(synthetic_qa_data):
    question = qa_pair["question"]
    ground_truth = qa_pair["answer"]

    prompt = f"Q: {question}\nA:"

    print(f"\n--- Example {idx + 1} ---")
    print(f"Question: {question}")
    print(f"Ground truth: {ground_truth}")

    generated_text, consensus_scores = generate_with_layer_monitoring(
        prompt, max_new_tokens=10
    )

    print(f"Generated: {generated_text}")
    print(f"Consensus scores: {[f'{s:.3f}' for s in consensus_scores]}")

    # Label hallucination for this generation
    hallucination_label = label_hallucination(generated_text, ground_truth, question)

    # Store results
    experiment_data["synthetic_qa"]["generated_texts"].append(generated_text)
    experiment_data["synthetic_qa"]["ground_truth"].append(ground_truth)

    # Compute average consensus for this sample
    avg_consensus = np.mean(consensus_scores) if len(consensus_scores) > 0 else 0.5
    all_consensus_scores.append(avg_consensus)
    all_hallucination_labels.append(hallucination_label)

    experiment_data["synthetic_qa"]["consensus_scores"].append(consensus_scores)
    experiment_data["synthetic_qa"]["hallucination_labels"].append(hallucination_label)

    print(f"Hallucination label: {hallucination_label} (0=correct, 1=hallucination)")
    print(f"Average consensus: {avg_consensus:.3f}")

# Compute Spearman correlation between consensus and hallucination
print("\n" + "=" * 50)
print("EVALUATION METRICS")
print("=" * 50)

all_consensus_scores = np.array(all_consensus_scores)
all_hallucination_labels = np.array(all_hallucination_labels)

# For correlation, we expect: low consensus (disagreement) -> hallucination (1)
# So we compute correlation between (1 - consensus) and hallucination_label
inverted_consensus = 1.0 - all_consensus_scores

if len(np.unique(all_hallucination_labels)) > 1:
    correlation, p_value = spearmanr(inverted_consensus, all_hallucination_labels)
    print(
        f"\nLayer Consensus-Hallucination Correlation: {correlation:.4f} (p={p_value:.4f})"
    )
    print(
        f"Interpretation: {'Positive' if correlation > 0 else 'Negative'} correlation"
    )
    print(
        f"  - Higher layer disagreement {'predicts' if correlation > 0 else 'does not predict'} hallucinations"
    )
else:
    correlation = 0.0
    p_value = 1.0
    print(f"\nLayer Consensus-Hallucination Correlation: N/A (all labels are the same)")

experiment_data["synthetic_qa"]["correlations"].append(
    {
        "spearman_correlation": float(correlation),
        "p_value": float(p_value),
        "mean_consensus_correct": (
            float(np.mean(all_consensus_scores[all_hallucination_labels == 0]))
            if np.any(all_hallucination_labels == 0)
            else 0.0
        ),
        "mean_consensus_hallucination": (
            float(np.mean(all_consensus_scores[all_hallucination_labels == 1]))
            if np.any(all_hallucination_labels == 1)
            else 0.0
        ),
    }
)

print(
    f"\nMean consensus for correct generations: {experiment_data['synthetic_qa']['correlations'][0]['mean_consensus_correct']:.4f}"
)
print(
    f"Mean consensus for hallucinations: {experiment_data['synthetic_qa']['correlations'][0]['mean_consensus_hallucination']:.4f}"
)

# Visualization
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Consensus scores vs Hallucination labels
axes[0].scatter(
    all_consensus_scores[all_hallucination_labels == 0],
    np.zeros(np.sum(all_hallucination_labels == 0)),
    label="Correct",
    alpha=0.6,
    s=100,
    color="green",
)
axes[0].scatter(
    all_consensus_scores[all_hallucination_labels == 1],
    np.ones(np.sum(all_hallucination_labels == 1)),
    label="Hallucination",
    alpha=0.6,
    s=100,
    color="red",
)
axes[0].set_xlabel("Average Consensus Score")
axes[0].set_ylabel("Hallucination Label")
axes[0].set_title("Layer Consensus vs Hallucination")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Distribution of consensus scores
axes[1].hist(
    all_consensus_scores[all_hallucination_labels == 0],
    alpha=0.5,
    label="Correct",
    bins=5,
    color="green",
)
axes[1].hist(
    all_consensus_scores[all_hallucination_labels == 1],
    alpha=0.5,
    label="Hallucination",
    bins=5,
    color="red",
)
axes[1].set_xlabel("Average Consensus Score")
axes[1].set_ylabel("Frequency")
axes[1].set_title("Distribution of Consensus Scores")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "synthetic_qa_consensus_analysis.png"),
    dpi=150,
    bbox_inches="tight",
)
print(
    f"\nSaved visualization to {os.path.join(working_dir, 'synthetic_qa_consensus_analysis.png')}"
)

# Save all experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"Saved experiment data to {os.path.join(working_dir, 'experiment_data.npy')}")

# Summary statistics
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
print(f"Total samples: {len(all_consensus_scores)}")
print(f"Correct generations: {np.sum(all_hallucination_labels == 0)}")
print(f"Hallucinations: {np.sum(all_hallucination_labels == 1)}")
print(
    f"Overall consensus score range: [{all_consensus_scores.min():.3f}, {all_consensus_scores.max():.3f}]"
)
print(f"Spearman correlation (layer disagreement vs hallucination): {correlation:.4f}")

if correlation > 0.3:
    print(
        "\n✓ HYPOTHESIS SUPPORTED: Layer disagreement positively correlates with hallucinations"
    )
elif correlation < -0.3:
    print(
        "\n✗ HYPOTHESIS CONTRADICTED: Layer disagreement negatively correlates with hallucinations"
    )
else:
    print(
        "\n~ HYPOTHESIS UNCLEAR: Weak correlation observed, need more data or refinement"
    )

print("\nBaseline implementation complete!")
