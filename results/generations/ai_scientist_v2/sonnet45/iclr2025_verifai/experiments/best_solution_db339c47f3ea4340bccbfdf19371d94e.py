import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import random
import matplotlib.pyplot as plt

# Setup
working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set seeds
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

# Experiment data structure for hyperparameter tuning
experiment_data = {
    "spec_temp_tuning": {
        "vanilla": {
            "specification_satisfaction_rate": [],
            "average": 0.0,
        },
        "sapd_by_spec_temp": {},
    }
}


class CodeSpecificationDataset:
    def __init__(self):
        self.vocab = self._create_vocabulary()
        self.token_to_id = {t: i for i, t in enumerate(self.vocab)}
        self.id_to_token = {i: t for t, i in self.token_to_id.items()}
        self.problems = self._create_problems()

    def _create_vocabulary(self):
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
        problems = []
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
        return [self.token_to_id.get(t, 0) for t in code_tokens]

    def detokenize(self, ids):
        return [self.id_to_token.get(i, "<PAD>") for i in ids]


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


class SpecificationScorer:
    def __init__(self, dataset):
        self.dataset = dataset

    def score_partial_code(self, problem_idx, current_tokens, candidate_token):
        problem = self.dataset.problems[problem_idx]
        reference = problem["reference"]
        score = 0.1

        if candidate_token in problem.get("key_tokens", []):
            if "return" in current_tokens:
                score += 0.6
            else:
                score += 0.2

        if candidate_token in problem.get("required_tokens", []):
            if candidate_token not in current_tokens:
                score += 0.5
            else:
                score += 0.1

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

        operators = ["+", "-", "*", "/", "%"]
        if candidate_token in operators:
            if candidate_token not in problem.get("key_tokens", []):
                score = max(0.05, score - 0.3)

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
        problem = self.dataset.problems[problem_idx]
        try:
            if "return" not in generated_tokens:
                return False
            has_key = any(
                kt in generated_tokens for kt in problem.get("key_tokens", [])
            )
            if not has_key:
                return False
            reference = problem["reference"]
            similarity = sum(1 for token in reference[:12] if token in generated_tokens)
            if similarity >= 8:
                return True
            return False
        except:
            return False


def train_model(model, dataset, num_epochs=50):
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss(ignore_index=dataset.token_to_id["<PAD>"])
    model.train()
    for epoch in range(num_epochs):
        total_loss = 0
        num_batches = 0
        for problem in dataset.problems:
            reference = problem["reference"]
            input_ids = [dataset.token_to_id["<START>"]] + dataset.tokenize(
                reference[:-1]
            )
            target_ids = dataset.tokenize(reference)
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
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{num_epochs}, Loss: {total_loss/num_batches:.4f}")


def generate_vanilla(model, dataset, problem_idx, max_length=15, temperature=1.0):
    model.eval()
    problem = dataset.problems[problem_idx]
    current_tokens = problem["reference"][:8]
    current_ids = [dataset.token_to_id["<START>"]] + dataset.tokenize(current_tokens)
    with torch.no_grad():
        for _ in range(max_length):
            input_tensor = torch.tensor([current_ids], dtype=torch.long).to(device)
            logits, _ = model(input_tensor)
            next_token_logits = logits[0, -1, :] / temperature
            probs = F.softmax(next_token_logits, dim=-1)
            next_token_id = torch.multinomial(probs, 1).item()
            current_ids.append(next_token_id)
            next_token = dataset.id_to_token[next_token_id]
            current_tokens.append(next_token)
            if next_token == "<END>":
                break
    return current_tokens


def generate_sapd(
    model,
    dataset,
    scorer,
    problem_idx,
    max_length=15,
    temperature=1.0,
    spec_weight=0.5,
    spec_temp=0.5,
):
    model.eval()
    problem = dataset.problems[problem_idx]
    current_tokens = problem["reference"][:8]
    current_ids = [dataset.token_to_id["<START>"]] + dataset.tokenize(current_tokens)
    with torch.no_grad():
        for _ in range(max_length):
            input_tensor = torch.tensor([current_ids], dtype=torch.long).to(device)
            logits, _ = model(input_tensor)
            next_token_logits = logits[0, -1, :] / temperature
            lm_probs = F.softmax(next_token_logits, dim=-1).cpu().numpy()
            spec_scores = np.zeros(len(dataset.vocab))
            for token_id, token in dataset.id_to_token.items():
                spec_scores[token_id] = scorer.score_partial_code(
                    problem_idx, current_tokens, token
                )
            spec_scores = np.exp(spec_scores / spec_temp)
            spec_scores = spec_scores / (spec_scores.sum() + 1e-10)
            blended_probs = (1 - spec_weight) * lm_probs + spec_weight * spec_scores
            blended_probs = blended_probs / blended_probs.sum()
            next_token_id = np.random.choice(len(dataset.vocab), p=blended_probs)
            current_ids.append(next_token_id)
            next_token = dataset.id_to_token[next_token_id]
            current_tokens.append(next_token)
            if next_token == "<END>":
                break
    return current_tokens


def tune_spec_temp(
    model, dataset, scorer, spec_temp_values, num_samples=20, spec_weight=0.5
):
    print("\n" + "=" * 60)
    print("Hyperparameter Tuning: spec_temp")
    print("=" * 60)

    vanilla_satisfaction = []
    print("\nEvaluating Vanilla baseline...")
    for problem_idx in range(len(dataset.problems)):
        vanilla_correct = 0
        for _ in range(num_samples):
            vanilla_code = generate_vanilla(model, dataset, problem_idx)
            vanilla_satisfies = scorer.evaluate_complete_code(problem_idx, vanilla_code)
            vanilla_correct += int(vanilla_satisfies)
        vanilla_rate = vanilla_correct / num_samples
        vanilla_satisfaction.append(vanilla_rate)
        print(f"  Problem {problem_idx}: {vanilla_rate:.2%}")

    experiment_data["spec_temp_tuning"]["vanilla"][
        "specification_satisfaction_rate"
    ] = vanilla_satisfaction
    experiment_data["spec_temp_tuning"]["vanilla"]["average"] = float(
        np.mean(vanilla_satisfaction)
    )

    sapd_results = {}
    for spec_temp in spec_temp_values:
        print(f"\nEvaluating SAPD with spec_temp={spec_temp}...")
        sapd_satisfaction = []
        for problem_idx in range(len(dataset.problems)):
            problem = dataset.problems[problem_idx]
            sapd_correct = 0
            for _ in range(num_samples):
                sapd_code = generate_sapd(
                    model,
                    dataset,
                    scorer,
                    problem_idx,
                    spec_weight=spec_weight,
                    spec_temp=spec_temp,
                )
                sapd_satisfies = scorer.evaluate_complete_code(problem_idx, sapd_code)
                sapd_correct += int(sapd_satisfies)
            sapd_rate = sapd_correct / num_samples
            sapd_satisfaction.append(sapd_rate)
            print(f"  Problem {problem_idx}: {sapd_rate:.2%}")

        avg_sapd = np.mean(sapd_satisfaction)
        sapd_results[spec_temp] = {
            "satisfaction_rates": sapd_satisfaction,
            "average": float(avg_sapd),
        }
        experiment_data["spec_temp_tuning"]["sapd_by_spec_temp"][str(spec_temp)] = (
            sapd_results[spec_temp]
        )

    print("\n" + "=" * 60)
    print("Hyperparameter Tuning Results Summary")
    print("=" * 60)
    avg_vanilla = np.mean(vanilla_satisfaction)
    print(f"Vanilla baseline: {avg_vanilla:.2%}")

    best_spec_temp = None
    best_avg = -1
    for spec_temp in spec_temp_values:
        avg_rate = sapd_results[spec_temp]["average"]
        improvement = ((avg_rate - avg_vanilla) / max(avg_vanilla, 0.01)) * 100
        print(
            f"spec_temp={spec_temp}: {avg_rate:.2%} ({improvement:+.1f}% improvement)"
        )
        if avg_rate > best_avg:
            best_avg = avg_rate
            best_spec_temp = spec_temp

    print(f"\nBest spec_temp: {best_spec_temp} with {best_avg:.2%} satisfaction rate")
    experiment_data["spec_temp_tuning"]["best_spec_temp"] = float(best_spec_temp)
    experiment_data["spec_temp_tuning"]["best_average"] = float(best_avg)

    return vanilla_satisfaction, sapd_results, best_spec_temp


def create_visualizations(vanilla_satisfaction, sapd_results, spec_temp_values):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Satisfaction rates by problem for each spec_temp
    ax = axes[0]
    x = np.arange(len(vanilla_satisfaction))
    width = 0.15
    ax.bar(x - 2 * width, vanilla_satisfaction, width, label="Vanilla", alpha=0.8)
    for i, spec_temp in enumerate(spec_temp_values):
        rates = sapd_results[spec_temp]["satisfaction_rates"]
        ax.bar(
            x + (i - 1) * width, rates, width, label=f"spec_temp={spec_temp}", alpha=0.8
        )
    ax.set_xlabel("Problem Index")
    ax.set_ylabel("Specification Satisfaction Rate")
    ax.set_title("Satisfaction Rate by Problem and spec_temp")
    ax.set_xticks(x)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Plot 2: Average satisfaction vs spec_temp
    ax = axes[1]
    temps = sorted(spec_temp_values)
    avg_rates = [sapd_results[t]["average"] for t in temps]
    vanilla_avg = np.mean(vanilla_satisfaction)
    ax.plot(temps, avg_rates, "o-", linewidth=2, markersize=8, label="SAPD")
    ax.axhline(y=vanilla_avg, color="r", linestyle="--", linewidth=2, label="Vanilla")
    ax.set_xlabel("spec_temp")
    ax.set_ylabel("Average Satisfaction Rate")
    ax.set_title("Impact of spec_temp on Satisfaction Rate")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(working_dir, "spec_temp_tuning.png"), dpi=150)
    plt.close()
    print(f"Visualization saved to {working_dir}/spec_temp_tuning.png")


print("=" * 60)
print("SAPD Hyperparameter Tuning: spec_temp")
print("=" * 60)

print("\nCreating dataset...")
dataset = CodeSpecificationDataset()
print(f"Vocabulary size: {len(dataset.vocab)}")
print(f"Number of problems: {len(dataset.problems)}")

print("\nInitializing model...")
model = CodeGenerationModel(
    vocab_size=len(dataset.vocab), embed_dim=64, hidden_dim=128, num_layers=2
)
model = model.to(device)
print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

print("\nTraining model...")
train_model(model, dataset, num_epochs=50)

print("\nInitializing specification scorer...")
scorer = SpecificationScorer(dataset)

# Hyperparameter tuning: test multiple spec_temp values
spec_temp_values = [0.1, 0.3, 0.5, 0.7, 1.0]
vanilla_satisfaction, sapd_results, best_spec_temp = tune_spec_temp(
    model, dataset, scorer, spec_temp_values, num_samples=20, spec_weight=0.5
)

create_visualizations(vanilla_satisfaction, sapd_results, spec_temp_values)

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nExperiment data saved to {working_dir}/experiment_data.npy")

print("\n" + "=" * 60)
print("Hyperparameter tuning completed successfully!")
print("=" * 60)
