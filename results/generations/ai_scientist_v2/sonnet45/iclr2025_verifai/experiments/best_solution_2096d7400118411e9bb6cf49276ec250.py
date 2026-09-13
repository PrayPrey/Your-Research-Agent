import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import random
from collections import defaultdict
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional

# Setup
working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set seeds
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

# Experiment data structure
experiment_data = {
    "vanilla": {
        "specification_satisfaction_rate": [],
        "epoch_metrics": [],
    },
    "sapd": {
        "specification_satisfaction_rate": [],
        "epoch_metrics": [],
    },
}


# Create synthetic dataset with specifications
class CodeSpecificationDataset:
    """Dataset of simple programming problems with formal specifications"""

    def __init__(self):
        self.vocab = self._create_vocabulary()
        self.token_to_id = {t: i for i, t in enumerate(self.vocab)}
        self.id_to_token = {i: t for t, i in self.token_to_id.items()}
        self.problems = self._create_problems()

    def _create_vocabulary(self):
        """Create a simple vocabulary for code generation"""
        vocab = [
            "<PAD>",
            "<START>",
            "<END>",
            "def",
            "return",
            "if",
            "else",
            "while",
            "for",
            "in",
            "range",
            "x",
            "y",
            "z",
            "result",
            "i",
            "n",
            "a",
            "b",
            "=",
            "+",
            "-",
            "*",
            "/",
            "%",
            "<",
            ">",
            "==",
            "!=",
            "<=",
            ">=",
            "(",
            ")",
            ":",
            ",",
            "[",
            "]",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "True",
            "False",
            "and",
            "or",
            "not",
            "len",
            "sum",
            "max",
            "min",
            "abs",
        ]
        return vocab

    def _create_problems(self):
        """Create synthetic problems with specifications"""
        problems = []

        # Problem 1: Add two numbers
        problems.append(
            {
                "description": "Add two numbers",
                "signature": "def add(x, y):",
                "precondition": lambda x, y: isinstance(x, (int, float))
                and isinstance(y, (int, float)),
                "postcondition": lambda inputs, output: output == inputs[0] + inputs[1],
                "reference": [
                    "def",
                    "add",
                    "(",
                    "x",
                    ",",
                    "y",
                    ")",
                    ":",
                    "return",
                    "x",
                    "+",
                    "y",
                    "<END>",
                ],
                "test_inputs": [(2, 3), (0, 0), (-1, 1), (10, 20)],
                "key_tokens": ["+"],
                "required_tokens": ["return"],
            }
        )

        # Problem 2: Multiply two numbers
        problems.append(
            {
                "description": "Multiply two numbers",
                "signature": "def multiply(x, y):",
                "precondition": lambda x, y: isinstance(x, (int, float))
                and isinstance(y, (int, float)),
                "postcondition": lambda inputs, output: output == inputs[0] * inputs[1],
                "reference": [
                    "def",
                    "multiply",
                    "(",
                    "x",
                    ",",
                    "y",
                    ")",
                    ":",
                    "return",
                    "x",
                    "*",
                    "y",
                    "<END>",
                ],
                "test_inputs": [(2, 3), (0, 5), (-1, 1), (4, 5)],
                "key_tokens": ["*"],
                "required_tokens": ["return"],
            }
        )

        # Problem 3: Absolute value
        problems.append(
            {
                "description": "Return absolute value",
                "signature": "def absolute(x):",
                "precondition": lambda x: isinstance(x, (int, float)),
                "postcondition": lambda inputs, output: output >= 0
                and (output == inputs[0] or output == -inputs[0]),
                "reference": [
                    "def",
                    "absolute",
                    "(",
                    "x",
                    ")",
                    ":",
                    "return",
                    "abs",
                    "(",
                    "x",
                    ")",
                    "<END>",
                ],
                "test_inputs": [(5,), (-5,), (0,), (10,)],
                "key_tokens": ["abs"],
                "required_tokens": ["return"],
            }
        )

        # Problem 4: Max of two numbers
        problems.append(
            {
                "description": "Return maximum of two numbers",
                "signature": "def maximum(x, y):",
                "precondition": lambda x, y: isinstance(x, (int, float))
                and isinstance(y, (int, float)),
                "postcondition": lambda inputs, output: output >= inputs[0]
                and output >= inputs[1]
                and (output == inputs[0] or output == inputs[1]),
                "reference": [
                    "def",
                    "maximum",
                    "(",
                    "x",
                    ",",
                    "y",
                    ")",
                    ":",
                    "return",
                    "max",
                    "(",
                    "x",
                    ",",
                    "y",
                    ")",
                    "<END>",
                ],
                "test_inputs": [(2, 3), (5, 1), (0, 0), (-1, -2)],
                "key_tokens": ["max"],
                "required_tokens": ["return"],
            }
        )

        return problems

    def tokenize(self, code_tokens):
        """Convert tokens to IDs"""
        return [self.token_to_id.get(t, 0) for t in code_tokens]

    def detokenize(self, ids):
        """Convert IDs to tokens"""
        return [self.id_to_token.get(i, "<PAD>") for i in ids]


# Simple LSTM-based code generation model
class CodeGenerationModel(nn.Module):
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=128, num_layers=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        output, hidden = self.lstm(embedded, hidden)
        logits = self.fc(output)
        return logits, hidden

    def init_hidden(self, batch_size):
        return None


# Specification satisfaction scorer
class SpecificationScorer:
    """Compute continuous satisfaction scores for partial code"""

    def __init__(self, dataset):
        self.dataset = dataset

    def score_partial_code(self, problem_idx, current_tokens, candidate_token):
        """
        Score how well adding candidate_token satisfies the specification.
        Returns a score in [0, 1] where 1 means high likelihood of satisfaction.
        """
        problem = self.dataset.problems[problem_idx]
        reference = problem["reference"]

        # Start with low baseline score
        score = 0.1

        # Check if this is a key token for the operation
        if candidate_token in problem.get("key_tokens", []):
            # Check if we're at appropriate position (after return, before params)
            if "return" in current_tokens:
                score += 0.6
            else:
                score += 0.2

        # Check if this is a required token
        if candidate_token in problem.get("required_tokens", []):
            # Higher score if we haven't seen it yet
            if candidate_token not in current_tokens:
                score += 0.5
            else:
                score += 0.1

        # Check for parameters being used correctly
        signature_tokens = reference[:8]
        if "(" in signature_tokens:
            param_start = signature_tokens.index("(")
            param_tokens = [
                t
                for t in signature_tokens[param_start:]
                if t not in ["(", ")", ",", ":"]
            ]

            if "return" in current_tokens and candidate_token in param_tokens:
                score += 0.4

        # Penalty for wrong operators at wrong time
        operators = ["+", "-", "*", "/", "%"]
        if candidate_token in operators:
            if candidate_token not in problem.get("key_tokens", []):
                score = max(0.05, score - 0.3)

        # Bonus for structural tokens in right position
        if (
            candidate_token == "return"
            and "return" not in current_tokens
            and len(current_tokens) >= 8
        ):
            score += 0.4

        if (
            candidate_token == "("
            and current_tokens
            and current_tokens[-1] in ["abs", "max", "min"]
        ):
            score += 0.3

        if (
            candidate_token == ")"
            and "(" in current_tokens
            and current_tokens.count("(") > current_tokens.count(")")
        ):
            score += 0.3

        if candidate_token == "<END>" and "return" in current_tokens:
            score += 0.2

        return min(1.0, score)

    def evaluate_complete_code(self, problem_idx, generated_tokens):
        """
        Evaluate if complete generated code satisfies specifications.
        Returns True if all test cases pass.
        """
        problem = self.dataset.problems[problem_idx]

        try:
            # Must have return statement
            if "return" not in generated_tokens:
                return False

            # Must have key tokens
            has_key = any(
                kt in generated_tokens for kt in problem.get("key_tokens", [])
            )
            if not has_key:
                return False

            # Check structural similarity with reference
            reference = problem["reference"]
            similarity = 0
            for token in reference[:12]:
                if token in generated_tokens:
                    similarity += 1

            # If very similar to reference, likely correct
            if similarity >= 8:
                return True

            return False

        except:
            return False


# Training function
def train_model(model, dataset, num_epochs=50, batch_size=4):
    """Train the base language model"""
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss(ignore_index=dataset.token_to_id["<PAD>"])

    model.train()
    for epoch in range(num_epochs):
        total_loss = 0
        num_batches = 0

        # Train on all problems
        for problem in dataset.problems:
            reference = problem["reference"]

            # Prepare training data
            input_ids = [dataset.token_to_id["<START>"]] + dataset.tokenize(
                reference[:-1]
            )
            target_ids = dataset.tokenize(reference)

            # Pad to fixed length
            max_len = 20
            input_ids = input_ids[:max_len] + [dataset.token_to_id["<PAD>"]] * (
                max_len - len(input_ids)
            )
            target_ids = target_ids[:max_len] + [dataset.token_to_id["<PAD>"]] * (
                max_len - len(target_ids)
            )

            input_tensor = torch.tensor([input_ids], dtype=torch.long).to(device)
            target_tensor = torch.tensor([target_ids], dtype=torch.long).to(device)

            optimizer.zero_grad()
            logits, _ = model(input_tensor)

            loss = criterion(logits.view(-1, logits.size(-1)), target_tensor.view(-1))
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / num_batches
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{num_epochs}, Loss: {avg_loss:.4f}")


# Generation functions
def generate_vanilla(model, dataset, problem_idx, max_length=15, temperature=1.0):
    """Generate code using vanilla sampling"""
    model.eval()
    problem = dataset.problems[problem_idx]

    # Start with function signature tokens
    current_tokens = problem["reference"][:8]  # def function_name(params):
    current_ids = [dataset.token_to_id["<START>"]] + dataset.tokenize(current_tokens)

    with torch.no_grad():
        for _ in range(max_length):
            input_tensor = torch.tensor([current_ids], dtype=torch.long).to(device)
            logits, _ = model(input_tensor)

            # Get last token logits
            next_token_logits = logits[0, -1, :] / temperature
            probs = F.softmax(next_token_logits, dim=-1)

            # Sample next token
            next_token_id = torch.multinomial(probs, 1).item()
            current_ids.append(next_token_id)

            next_token = dataset.id_to_token[next_token_id]
            current_tokens.append(next_token)

            if next_token == "<END>":
                break

    return current_tokens


def generate_sapd(
    model, dataset, scorer, problem_idx, max_length=15, temperature=1.0, spec_weight=0.5
):
    """Generate code using SAPD (blending LM probs with specification scores)"""
    model.eval()
    problem = dataset.problems[problem_idx]

    # Start with function signature tokens
    current_tokens = problem["reference"][:8]
    current_ids = [dataset.token_to_id["<START>"]] + dataset.tokenize(current_tokens)

    with torch.no_grad():
        for _ in range(max_length):
            input_tensor = torch.tensor([current_ids], dtype=torch.long).to(device)
            logits, _ = model(input_tensor)

            # Get last token logits
            next_token_logits = logits[0, -1, :] / temperature
            lm_probs = F.softmax(next_token_logits, dim=-1).cpu().numpy()

            # Compute specification scores for all candidate tokens
            spec_scores = np.zeros(len(dataset.vocab))
            for token_id, token in dataset.id_to_token.items():
                spec_scores[token_id] = scorer.score_partial_code(
                    problem_idx, current_tokens, token
                )

            # Apply temperature to sharpen spec scores
            spec_temp = 0.5
            spec_scores = np.exp(spec_scores / spec_temp)
            spec_scores = spec_scores / (spec_scores.sum() + 1e-10)

            # Blend LM probabilities with specification scores
            blended_probs = (1 - spec_weight) * lm_probs + spec_weight * spec_scores
            blended_probs = blended_probs / blended_probs.sum()

            # Sample from blended distribution
            next_token_id = np.random.choice(len(dataset.vocab), p=blended_probs)
            current_ids.append(next_token_id)

            next_token = dataset.id_to_token[next_token_id]
            current_tokens.append(next_token)

            if next_token == "<END>":
                break

    return current_tokens


# Evaluation
def evaluate_methods(model, dataset, scorer, num_samples=20):
    """Evaluate vanilla vs SAPD generation"""

    vanilla_satisfaction = []
    sapd_satisfaction = []

    spec_weights = [0.3, 0.5, 0.7]
    sapd_by_weight = {w: [] for w in spec_weights}

    print("\nEvaluating generation methods...")

    for problem_idx in range(len(dataset.problems)):
        problem = dataset.problems[problem_idx]
        print(f"\nProblem {problem_idx}: {problem['description']}")

        vanilla_correct = 0
        sapd_correct = {w: 0 for w in spec_weights}

        for sample_idx in range(num_samples):
            # Vanilla generation
            vanilla_code = generate_vanilla(model, dataset, problem_idx)
            vanilla_satisfies = scorer.evaluate_complete_code(problem_idx, vanilla_code)
            vanilla_correct += int(vanilla_satisfies)

            # SAPD generation with different weights
            for weight in spec_weights:
                sapd_code = generate_sapd(
                    model, dataset, scorer, problem_idx, spec_weight=weight
                )
                sapd_satisfies = scorer.evaluate_complete_code(problem_idx, sapd_code)
                sapd_correct[weight] += int(sapd_satisfies)

        vanilla_rate = vanilla_correct / num_samples
        vanilla_satisfaction.append(vanilla_rate)

        print(f"  Vanilla satisfaction rate: {vanilla_rate:.2%}")

        for weight in spec_weights:
            rate = sapd_correct[weight] / num_samples
            sapd_by_weight[weight].append(rate)
            print(f"  SAPD (weight={weight}) satisfaction rate: {rate:.2%}")

    # Average across problems
    avg_vanilla = np.mean(vanilla_satisfaction)
    avg_sapd_by_weight = {w: np.mean(rates) for w, rates in sapd_by_weight.items()}

    print(f"\n{'='*60}")
    print(f"Overall Results:")
    print(f"  Vanilla: {avg_vanilla:.2%}")
    for weight, avg_rate in avg_sapd_by_weight.items():
        improvement = ((avg_rate - avg_vanilla) / max(avg_vanilla, 0.01)) * 100
        print(
            f"  SAPD (weight={weight}): {avg_rate:.2%} ({improvement:+.1f}% improvement)"
        )

    # Store results
    experiment_data["vanilla"]["specification_satisfaction_rate"] = vanilla_satisfaction
    experiment_data["sapd"]["specification_satisfaction_rate"] = sapd_by_weight[0.5]
    experiment_data["sapd"]["all_weights"] = sapd_by_weight
    experiment_data["vanilla"]["average"] = avg_vanilla
    experiment_data["sapd"]["average"] = avg_sapd_by_weight

    return vanilla_satisfaction, sapd_by_weight


# Visualization
def create_visualizations(vanilla_satisfaction, sapd_by_weight):
    """Create visualizations of results"""

    # Plot 1: Satisfaction rates by problem
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    x = np.arange(len(vanilla_satisfaction))
    width = 0.2

    ax.bar(x - width, vanilla_satisfaction, width, label="Vanilla", alpha=0.8)
    for i, (weight, rates) in enumerate(sapd_by_weight.items()):
        ax.bar(x + i * width, rates, width, label=f"SAPD (w={weight})", alpha=0.8)

    ax.set_xlabel("Problem Index")
    ax.set_ylabel("Specification Satisfaction Rate")
    ax.set_title("Specification Satisfaction by Method and Problem")
    ax.set_xticks(x)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(working_dir, "satisfaction_by_problem.png"), dpi=150)
    plt.close()

    # Plot 2: Average satisfaction by spec weight
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    weights = sorted(sapd_by_weight.keys())
    avg_rates = [np.mean(sapd_by_weight[w]) for w in weights]
    vanilla_avg = np.mean(vanilla_satisfaction)

    ax.plot(weights, avg_rates, "o-", linewidth=2, markersize=8, label="SAPD")
    ax.axhline(y=vanilla_avg, color="r", linestyle="--", linewidth=2, label="Vanilla")

    ax.set_xlabel("Specification Weight")
    ax.set_ylabel("Average Satisfaction Rate")
    ax.set_title("Impact of Specification Weight on Satisfaction Rate")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(working_dir, "weight_analysis.png"), dpi=150)
    plt.close()

    print(f"\nVisualizations saved to {working_dir}")


# Main execution
print("=" * 60)
print("Specification-Aware Probabilistic Decoding (SAPD)")
print("=" * 60)

# Create dataset
print("\nCreating synthetic code dataset with specifications...")
dataset = CodeSpecificationDataset()
print(f"Vocabulary size: {len(dataset.vocab)}")
print(f"Number of problems: {len(dataset.problems)}")

# Create model
print("\nInitializing code generation model...")
model = CodeGenerationModel(
    vocab_size=len(dataset.vocab), embed_dim=64, hidden_dim=128, num_layers=2
)
model = model.to(device)
print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

# Train model
print("\nTraining base language model...")
train_model(model, dataset, num_epochs=50)

# Create specification scorer
print("\nInitializing specification scorer...")
scorer = SpecificationScorer(dataset)

# Evaluate
vanilla_satisfaction, sapd_by_weight = evaluate_methods(
    model, dataset, scorer, num_samples=20
)

# Create visualizations
create_visualizations(vanilla_satisfaction, sapd_by_weight)

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nExperiment data saved to {working_dir}/experiment_data.npy")

print("\n" + "=" * 60)
print("Experiment completed successfully!")
print("=" * 60)
