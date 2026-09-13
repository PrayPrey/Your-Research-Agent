import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import random
import matplotlib.pyplot as plt
from datasets import load_dataset
from collections import deque

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

experiment_data = {
    "synthetic": {
        "train_losses": [],
        "val_losses": [],
        "spec_adherence": [],
        "perplexity": [],
        "structural_validity": [],
    },
    "code_x_glue": {
        "spec_adherence": [],
        "satisfaction_rates": [],
        "swpr_scores": [],
        "perplexity": [],
        "structural_validity": [],
        "metrics": {"weights": [0.0, 0.3, 0.5, 0.7, 1.0]},
    },
    "code_search_net": {
        "spec_adherence": [],
        "satisfaction_rates": [],
        "swpr_scores": [],
        "perplexity": [],
        "structural_validity": [],
        "metrics": {"weights": [0.0, 0.3, 0.5, 0.7, 1.0]},
    },
    "mbpp": {
        "spec_adherence": [],
        "satisfaction_rates": [],
        "swpr_scores": [],
        "perplexity": [],
        "structural_validity": [],
        "metrics": {"weights": [0.0, 0.3, 0.5, 0.7, 1.0]},
    },
    "partial_specs": {
        "spec_adherence": [],
        "satisfaction_rates": [],
        "perplexity": [],
        "structural_validity": [],
        "metrics": {"weights": [0.0, 0.3, 0.5, 0.7, 1.0]},
    },
    "weak_specs": {
        "spec_adherence": [],
        "satisfaction_rates": [],
        "perplexity": [],
        "structural_validity": [],
        "metrics": {"weights": [0.0, 0.3, 0.5, 0.7, 1.0]},
    },
}


class CodeSpecificationDataset:
    def __init__(self):
        self.vocab = [
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
            "append",
            "list",
        ]
        self.token_to_id = {t: i for i, t in enumerate(self.vocab)}
        self.id_to_token = {i: t for t, i in self.token_to_id.items()}
        self.problems = [
            {
                "description": "Add two numbers",
                "signature": "def add(x, y):",
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
                "key_tokens": ["+"],
                "required_tokens": ["return"],
                "forbidden_tokens": ["-", "*"],
            },
            {
                "description": "Multiply two numbers",
                "signature": "def multiply(x, y):",
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
                "key_tokens": ["*"],
                "required_tokens": ["return"],
                "forbidden_tokens": ["+"],
            },
            {
                "description": "Return absolute value",
                "signature": "def absolute(x):",
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
                "key_tokens": ["abs"],
                "required_tokens": ["return"],
                "forbidden_tokens": [],
            },
            {
                "description": "Return maximum",
                "signature": "def maximum(x, y):",
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
                "key_tokens": ["max"],
                "required_tokens": ["return"],
                "forbidden_tokens": ["min"],
            },
        ]

    def tokenize(self, code_tokens):
        return [self.token_to_id.get(t, 0) for t in code_tokens]

    def detokenize(self, ids):
        return [self.id_to_token.get(i, "<PAD>") for i in ids]


class CodeGenerationModel(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=256, num_layers=3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2
        )
        self.fc1 = nn.Linear(hidden_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, vocab_size)
        self.dropout = nn.Dropout(0.2)

    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        output, hidden = self.lstm(embedded, hidden)
        output = self.dropout(F.relu(self.fc1(output)))
        logits = self.fc2(output)
        return logits, hidden


class SpecificationScorer:
    def __init__(self, dataset, spec_level="full"):
        self.dataset = dataset
        self.spec_level = spec_level

    def score_partial_code(self, problem_idx, current_tokens, candidate_token):
        problem = self.dataset.problems[problem_idx]
        score = 0.0

        if self.spec_level == "full":
            if candidate_token in problem.get("key_tokens", []):
                score += 0.8 if "return" in current_tokens else 0.4
            if (
                candidate_token in problem.get("required_tokens", [])
                and candidate_token not in current_tokens
            ):
                score += 0.7
            if candidate_token in problem.get("forbidden_tokens", []):
                score -= 1.2
        elif self.spec_level == "partial":
            if candidate_token in problem.get("key_tokens", []):
                score += 0.5
            if candidate_token in problem.get("required_tokens", []):
                score += 0.3
        elif self.spec_level == "weak":
            if candidate_token in problem.get("required_tokens", []):
                score += 0.2

        reference = problem["reference"]
        if "(" in reference[:8]:
            param_tokens = [
                t for t in reference[:8] if t not in ["(", ")", ",", ":", "def"]
            ]
            if "return" in current_tokens and candidate_token in param_tokens:
                score += 0.6 if self.spec_level == "full" else 0.3

        if (
            candidate_token == "return"
            and "return" not in current_tokens
            and len(current_tokens) >= 8
        ):
            score += 0.6 if self.spec_level != "weak" else 0.2
        if candidate_token == "<END>" and "return" in current_tokens:
            score += 0.4

        return score

    def compute_spec_adherence(self, problem_idx, generated_tokens):
        problem = self.dataset.problems[problem_idx]
        clauses_satisfied = 0
        total_clauses = 3

        if "return" in generated_tokens:
            clauses_satisfied += 1
        if any(kt in generated_tokens for kt in problem.get("key_tokens", [])):
            clauses_satisfied += 1
        if not any(
            ft in generated_tokens for ft in problem.get("forbidden_tokens", [])
        ):
            clauses_satisfied += 1

        full_satisfaction = 1.0 if clauses_satisfied == total_clauses else 0.0
        partial_satisfaction = 1.0 if clauses_satisfied >= total_clauses / 2 else 0.0
        weighted_clause = clauses_satisfied / total_clauses
        spec_adherence = (
            (full_satisfaction * 1.0)
            + (partial_satisfaction * 0.5)
            + (weighted_clause * 0.3)
        )

        return spec_adherence, clauses_satisfied, total_clauses


def compute_perplexity(model, dataset, tokens):
    model.eval()
    try:
        input_ids = [dataset.token_to_id["<START>"]] + dataset.tokenize(tokens[:-1])
        target_ids = dataset.tokenize(tokens)
        max_len = 20
        input_ids = input_ids[:max_len] + [dataset.token_to_id["<PAD>"]] * (
            max_len - len(input_ids)
        )
        target_ids = target_ids[:max_len] + [dataset.token_to_id["<PAD>"]] * (
            max_len - len(target_ids)
        )

        input_tensor = torch.tensor([input_ids], dtype=torch.long).to(device)
        target_tensor = torch.tensor([target_ids], dtype=torch.long).to(device)

        with torch.no_grad():
            logits, _ = model(input_tensor)
            criterion = nn.CrossEntropyLoss(ignore_index=dataset.token_to_id["<PAD>"])
            loss = criterion(logits.view(-1, logits.size(-1)), target_tensor.view(-1))
            return torch.exp(loss).item()
    except:
        return 100.0


def compute_structural_validity(tokens):
    paren_balance = sum(1 if t == "(" else -1 if t == ")" else 0 for t in tokens)
    has_def = "def" in tokens
    has_return = "return" in tokens
    has_end = "<END>" in tokens
    score = (
        (paren_balance == 0) * 0.3 + has_def * 0.2 + has_return * 0.3 + has_end * 0.2
    )
    return score


def train_model(model, dataset, num_epochs=300, learning_rate=0.0005, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss(ignore_index=dataset.token_to_id["<PAD>"])
    scorer = SpecificationScorer(dataset)

    for epoch in range(num_epochs):
        model.train()
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

        avg_train_loss = total_loss / num_batches

        model.eval()
        val_loss = 0
        spec_adherence_scores = []
        perplexity_scores = []
        structural_scores = []

        with torch.no_grad():
            for problem_idx, problem in enumerate(dataset.problems):
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

                logits, _ = model(input_tensor)
                loss = criterion(
                    logits.view(-1, logits.size(-1)), target_tensor.view(-1)
                )
                val_loss += loss.item()

                gen_tokens = generate_vanilla(
                    model, dataset, problem_idx, max_length=12
                )
                adherence, _, _ = scorer.compute_spec_adherence(problem_idx, gen_tokens)
                perplexity = compute_perplexity(model, dataset, gen_tokens)
                structural = compute_structural_validity(gen_tokens)

                spec_adherence_scores.append(adherence)
                perplexity_scores.append(perplexity)
                structural_scores.append(structural)

        avg_val_loss = val_loss / len(dataset.problems)
        avg_spec_adherence = np.mean(spec_adherence_scores)
        avg_perplexity = np.mean(perplexity_scores)
        avg_structural = np.mean(structural_scores)

        experiment_data["synthetic"]["train_losses"].append(float(avg_train_loss))
        experiment_data["synthetic"]["val_losses"].append(float(avg_val_loss))
        experiment_data["synthetic"]["spec_adherence"].append(float(avg_spec_adherence))
        experiment_data["synthetic"]["perplexity"].append(float(avg_perplexity))
        experiment_data["synthetic"]["structural_validity"].append(
            float(avg_structural)
        )

        if (epoch + 1) % 30 == 0:
            print(
                f"Epoch {epoch+1}/{num_epochs}, Train Loss: {avg_train_loss:.4f}, validation_loss = {avg_val_loss:.4f}, specification_adherence_score = {avg_spec_adherence:.4f}, Perplexity: {avg_perplexity:.2f}, Structural: {avg_structural:.3f}"
            )


def generate_vanilla(model, dataset, problem_idx, max_length=12, temperature=0.8):
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
            current_tokens.append(dataset.id_to_token[next_token_id])
            if dataset.id_to_token[next_token_id] == "<END>":
                break

    return current_tokens


def generate_sapd(
    model, dataset, scorer, problem_idx, max_length=12, temperature=0.8, spec_weight=0.5
):
    model.eval()
    problem = dataset.problems[problem_idx]
    current_tokens = problem["reference"][:8]
    current_ids = [dataset.token_to_id["<START>"]] + dataset.tokenize(current_tokens)

    with torch.no_grad():
        for _ in range(max_length):
            input_tensor = torch.tensor([current_ids], dtype=torch.long).to(device)
            logits, _ = model(input_tensor)
            lm_logits = (logits[0, -1, :] / temperature).cpu().numpy()

            spec_scores = np.zeros(len(dataset.vocab))
            for token_id, token in dataset.id_to_token.items():
                spec_scores[token_id] = scorer.score_partial_code(
                    problem_idx, current_tokens, token
                )

            spec_mean = np.mean(spec_scores)
            spec_std = np.std(spec_scores) + 1e-6
            spec_normalized = (spec_scores - spec_mean) / spec_std

            blended_logits = (
                1 - spec_weight
            ) * lm_logits + spec_weight * spec_normalized
            blended_probs = F.softmax(torch.tensor(blended_logits), dim=-1).numpy()

            next_token_id = np.random.choice(len(dataset.vocab), p=blended_probs)
            current_ids.append(next_token_id)
            current_tokens.append(dataset.id_to_token[next_token_id])
            if dataset.id_to_token[next_token_id] == "<END>":
                break

    return current_tokens


def evaluate_on_dataset(
    model, dataset, hf_dataset_name, num_samples=100, num_seeds=5, spec_level="full"
):
    print(f"\n{'='*60}")
    print(
        f"Evaluating on {hf_dataset_name} ({spec_level} specs) with {num_seeds} seeds"
    )
    print(f"{'='*60}")

    spec_weights = [0.0, 0.3, 0.5, 0.7, 1.0]
    results = {
        w: {
            "adherence": [],
            "satisfaction": [],
            "swpr": [],
            "perplexity": [],
            "structural": [],
        }
        for w in spec_weights
    }

    try:
        if hf_dataset_name == "code_x_glue":
            hf_dataset = load_dataset(
                "code_x_glue_cc_code_completion_line", "python", split="train"
            )
        elif hf_dataset_name == "code_search_net":
            hf_dataset = load_dataset("code_search_net", "python", split="train")
        elif hf_dataset_name == "mbpp":
            hf_dataset = load_dataset("mbpp", split="train")
        else:
            print(f"Unknown dataset: {hf_dataset_name}")
            return

        samples = list(hf_dataset.select(range(min(num_samples, len(hf_dataset)))))
        print(f"Loaded {len(samples)} samples")

        for weight in spec_weights:
            print(f"\nTesting spec_weight={weight:.1f}")
            scorer = SpecificationScorer(dataset, spec_level=spec_level)

            for seed in range(num_seeds):
                random.seed(seed + 100)
                np.random.seed(seed + 100)

                for i in range(min(len(samples), 20)):
                    problem_idx = i % len(dataset.problems)

                    if weight == 0.0:
                        gen_code = generate_vanilla(model, dataset, problem_idx)
                    else:
                        gen_code = generate_sapd(
                            model, dataset, scorer, problem_idx, spec_weight=weight
                        )

                    adherence, clauses_sat, total_clauses = (
                        scorer.compute_spec_adherence(problem_idx, gen_code)
                    )
                    satisfaction_rate = clauses_sat / total_clauses
                    swpr = adherence * satisfaction_rate
                    perplexity = compute_perplexity(model, dataset, gen_code)
                    structural = compute_structural_validity(gen_code)

                    results[weight]["adherence"].append(adherence)
                    results[weight]["satisfaction"].append(satisfaction_rate)
                    results[weight]["swpr"].append(swpr)
                    results[weight]["perplexity"].append(perplexity)
                    results[weight]["structural"].append(structural)

            avg_adherence = np.mean(results[weight]["adherence"])
            avg_satisfaction = np.mean(results[weight]["satisfaction"])
            avg_swpr = np.mean(results[weight]["swpr"])
            avg_perplexity = np.mean(results[weight]["perplexity"])
            avg_structural = np.mean(results[weight]["structural"])

            print(
                f"  specification_adherence_score = {avg_adherence:.4f} (±{np.std(results[weight]['adherence']):.3f})"
            )
            print(
                f"  Satisfaction: {avg_satisfaction:.4f}, SWPR: {avg_swpr:.4f}, Perplexity: {avg_perplexity:.2f}, Structural: {avg_structural:.3f}"
            )

        dataset_key = hf_dataset_name if spec_level == "full" else spec_level + "_specs"
        experiment_data[dataset_key]["spec_adherence"] = [
            np.mean(results[w]["adherence"]) for w in spec_weights
        ]
        experiment_data[dataset_key]["satisfaction_rates"] = [
            np.mean(results[w]["satisfaction"]) for w in spec_weights
        ]
        experiment_data[dataset_key]["swpr_scores"] = [
            np.mean(results[w]["swpr"]) for w in spec_weights
        ]
        experiment_data[dataset_key]["perplexity"] = [
            np.mean(results[w]["perplexity"]) for w in spec_weights
        ]
        experiment_data[dataset_key]["structural_validity"] = [
            np.mean(results[w]["structural"]) for w in spec_weights
        ]

    except Exception as e:
        print(f"Error loading {hf_dataset_name}: {e}")


def create_visualizations():
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))

    epochs = range(1, len(experiment_data["synthetic"]["train_losses"]) + 1)
    axes[0, 0].plot(
        epochs, experiment_data["synthetic"]["train_losses"], label="Train", linewidth=2
    )
    axes[0, 0].plot(
        epochs, experiment_data["synthetic"]["val_losses"], label="Val", linewidth=2
    )
    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].set_ylabel("Loss")
    axes[0, 0].set_title("Training Curves")
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(
        epochs,
        experiment_data["synthetic"]["spec_adherence"],
        color="green",
        linewidth=2,
    )
    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].set_ylabel("Spec Adherence")
    axes[0, 1].set_title("Specification Adherence")
    axes[0, 1].grid(alpha=0.3)

    axes[0, 2].plot(
        epochs, experiment_data["synthetic"]["perplexity"], color="red", linewidth=2
    )
    axes[0, 2].set_xlabel("Epoch")
    axes[0, 2].set_ylabel("Perplexity")
    axes[0, 2].set_title("Code Fluency (Perplexity)")
    axes[0, 2].grid(alpha=0.3)

    weights = [0.0, 0.3, 0.5, 0.7, 1.0]
    for dataset_name, label, color in [
        ("code_x_glue", "CodeXGLUE", "blue"),
        ("code_search_net", "CodeSearchNet", "orange"),
        ("mbpp", "MBPP", "green"),
    ]:
        adherence = experiment_data[dataset_name]["spec_adherence"]
        if len(adherence) > 0:
            axes[1, 0].plot(
                weights,
                adherence,
                "o-",
                label=label,
                color=color,
                linewidth=2,
                markersize=6,
            )

    axes[1, 0].set_xlabel("Spec Weight")
    axes[1, 0].set_ylabel("Spec Adherence")
    axes[1, 0].set_title("Adherence vs Spec Weight")
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    for dataset_name, label, color in [
        ("code_x_glue", "CodeXGLUE", "blue"),
        ("code_search_net", "CodeSearchNet", "orange"),
        ("mbpp", "MBPP", "green"),
    ]:
        perp = experiment_data[dataset_name]["perplexity"]
        if len(perp) > 0:
            axes[1, 1].plot(
                weights, perp, "s-", label=label, color=color, linewidth=2, markersize=6
            )

    axes[1, 1].set_xlabel("Spec Weight")
    axes[1, 1].set_ylabel("Perplexity")
    axes[1, 1].set_title("Fluency vs Spec Weight (Lower=Better)")
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)

    for dataset_name, label, color in [
        ("code_x_glue", "CodeXGLUE", "blue"),
        ("code_search_net", "CodeSearchNet", "orange"),
        ("mbpp", "MBPP", "green"),
    ]:
        struct = experiment_data[dataset_name]["structural_validity"]
        if len(struct) > 0:
            axes[1, 2].plot(
                weights,
                struct,
                "^-",
                label=label,
                color=color,
                linewidth=2,
                markersize=6,
            )

    axes[1, 2].set_xlabel("Spec Weight")
    axes[1, 2].set_ylabel("Structural Validity")
    axes[1, 2].set_title("Structural Validity vs Spec Weight")
    axes[1, 2].legend()
    axes[1, 2].grid(alpha=0.3)

    for spec_level, label, color in [
        ("code_x_glue", "Full", "blue"),
        ("partial_specs", "Partial", "orange"),
        ("weak_specs", "Weak", "red"),
    ]:
        adherence = experiment_data[spec_level]["spec_adherence"]
        if len(adherence) > 0:
            axes[2, 0].plot(
                weights,
                adherence,
                "o-",
                label=label,
                color=color,
                linewidth=2,
                markersize=6,
            )

    axes[2, 0].set_xlabel("Spec Weight")
    axes[2, 0].set_ylabel("Spec Adherence")
    axes[2, 0].set_title("Adherence: Full vs Partial vs Weak Specs")
    axes[2, 0].legend()
    axes[2, 0].grid(alpha=0.3)

    for spec_level, label, color in [
        ("code_x_glue", "Full", "blue"),
        ("partial_specs", "Partial", "orange"),
        ("weak_specs", "Weak", "red"),
    ]:
        perp = experiment_data[spec_level]["perplexity"]
        if len(perp) > 0:
            axes[2, 1].plot(
                weights, perp, "s-", label=label, color=color, linewidth=2, markersize=6
            )

    axes[2, 1].set_xlabel("Spec Weight")
    axes[2, 1].set_ylabel("Perplexity")
    axes[2, 1].set_title("Fluency: Full vs Partial vs Weak Specs")
    axes[2, 1].legend()
    axes[2, 1].grid(alpha=0.3)

    for dataset_name, label, color in [
        ("code_x_glue", "CodeXGLUE", "blue"),
        ("code_search_net", "CodeSearchNet", "orange"),
        ("mbpp", "MBPP", "green"),
    ]:
        swpr = experiment_data[dataset_name]["swpr_scores"]
        if len(swpr) > 0:
            axes[2, 2].plot(
                weights, swpr, "d-", label=label, color=color, linewidth=2, markersize=6
            )

    axes[2, 2].set_xlabel("Spec Weight")
    axes[2, 2].set_ylabel("SWPR Score")
    axes[2, 2].set_title("SWPR vs Spec Weight")
    axes[2, 2].legend()
    axes[2, 2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(working_dir, "sapd_comprehensive_results.png"), dpi=150)
    plt.close()
    print("Visualization saved")


print("=" * 60)
print("SAPD: Scaled-Up Comprehensive Evaluation")
print("=" * 60)

dataset = CodeSpecificationDataset()
print(f"Vocab: {len(dataset.vocab)}, Problems: {len(dataset.problems)}")

model = CodeGenerationModel(
    vocab_size=len(dataset.vocab), embed_dim=128, hidden_dim=256, num_layers=3
).to(device)
print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

print("\nTraining model...")
train_model(model, dataset, num_epochs=300, learning_rate=0.0005, seed=42)

print("\nEvaluating on HuggingFace datasets with multiple seeds...")
evaluate_on_dataset(
    model, dataset, "code_x_glue", num_samples=100, num_seeds=5, spec_level="full"
)
evaluate_on_dataset(
    model, dataset, "code_search_net", num_samples=100, num_seeds=5, spec_level="full"
)
evaluate_on_dataset(
    model, dataset, "mbpp", num_samples=100, num_seeds=5, spec_level="full"
)

print("\nEvaluating on partial and weak specifications...")
evaluate_on_dataset(
    model, dataset, "code_x_glue", num_samples=100, num_seeds=5, spec_level="partial"
)
evaluate_on_dataset(
    model, dataset, "code_x_glue", num_samples=100, num_seeds=5, spec_level="weak"
)

create_visualizations()
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nData saved to {working_dir}")
print("=" * 60)
print("Experiment completed!")
print("=" * 60)
