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
    "baseline": {
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
        },
        "code_search_net": {
            "spec_adherence": [],
            "satisfaction_rates": [],
            "swpr_scores": [],
            "perplexity": [],
            "structural_validity": [],
        },
        "mbpp": {
            "spec_adherence": [],
            "satisfaction_rates": [],
            "swpr_scores": [],
            "perplexity": [],
            "structural_validity": [],
        },
        "partial_specs": {
            "spec_adherence": [],
            "satisfaction_rates": [],
            "perplexity": [],
            "structural_validity": [],
        },
        "weak_specs": {
            "spec_adherence": [],
            "satisfaction_rates": [],
            "perplexity": [],
            "structural_validity": [],
        },
    },
    "ablation": {
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
        },
        "code_search_net": {
            "spec_adherence": [],
            "satisfaction_rates": [],
            "swpr_scores": [],
            "perplexity": [],
            "structural_validity": [],
        },
        "mbpp": {
            "spec_adherence": [],
            "satisfaction_rates": [],
            "swpr_scores": [],
            "perplexity": [],
            "structural_validity": [],
        },
        "partial_specs": {
            "spec_adherence": [],
            "satisfaction_rates": [],
            "perplexity": [],
            "structural_validity": [],
        },
        "weak_specs": {
            "spec_adherence": [],
            "satisfaction_rates": [],
            "perplexity": [],
            "structural_validity": [],
        },
    },
    "metrics": {"weights": [0.0, 0.3, 0.5, 0.7, 1.0]},
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


class ViolationTracker:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.violation_history = deque(maxlen=window_size)
        self.forbidden_attempts = {}
        self.structural_violations = []

    def record_violation(self, violation_type, token=None):
        self.violation_history.append({"type": violation_type, "token": token})
        if violation_type == "forbidden" and token:
            self.forbidden_attempts[token] = self.forbidden_attempts.get(token, 0) + 1
        elif violation_type == "structural":
            self.structural_violations.append(len(self.violation_history))

    def get_violation_penalty(self, violation_type, token=None):
        base_penalty = 1.5
        if violation_type == "forbidden" and token:
            attempts = self.forbidden_attempts.get(token, 0)
            repeat_penalty = base_penalty * (1.5**attempts)
            recent_violations = sum(
                1 for v in self.violation_history if v["type"] == "forbidden"
            )
            recency_penalty = 0.3 * recent_violations
            return repeat_penalty + recency_penalty
        elif violation_type == "structural":
            num_structural = len(self.structural_violations)
            return base_penalty * (1.2**num_structural)
        return base_penalty

    def get_cumulative_penalty_factor(self):
        if len(self.violation_history) == 0:
            return 1.0
        violation_ratio = len(self.violation_history) / self.window_size
        return 1.0 + (violation_ratio * 0.5)


class SpecificationScorer:
    def __init__(self, dataset, spec_level="full", use_violation_penalty=False):
        self.dataset = dataset
        self.spec_level = spec_level
        self.use_violation_penalty = use_violation_penalty

    def score_partial_code(
        self, problem_idx, current_tokens, candidate_token, violation_tracker=None
    ):
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
                if self.use_violation_penalty and violation_tracker:
                    penalty = violation_tracker.get_violation_penalty(
                        "forbidden", candidate_token
                    )
                    cumulative_factor = (
                        violation_tracker.get_cumulative_penalty_factor()
                    )
                    score -= penalty * cumulative_factor
                else:
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

        if self.use_violation_penalty and violation_tracker:
            if (
                candidate_token == "return"
                and "return" not in current_tokens
                and len(current_tokens) >= 8
            ):
                score += 0.6 if self.spec_level != "weak" else 0.2
            elif len(current_tokens) >= 10 and "return" not in current_tokens:
                if candidate_token != "return":
                    penalty = violation_tracker.get_violation_penalty("structural")
                    score -= penalty * 0.5
        else:
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


def train_model(
    model,
    dataset,
    num_epochs=300,
    learning_rate=0.0005,
    seed=42,
    use_violation_penalty=False,
    exp_type="baseline",
):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss(ignore_index=dataset.token_to_id["<PAD>"])
    scorer = SpecificationScorer(dataset, use_violation_penalty=use_violation_penalty)

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

        experiment_data[exp_type]["synthetic"]["train_losses"].append(
            float(avg_train_loss)
        )
        experiment_data[exp_type]["synthetic"]["val_losses"].append(float(avg_val_loss))
        experiment_data[exp_type]["synthetic"]["spec_adherence"].append(
            float(avg_spec_adherence)
        )
        experiment_data[exp_type]["synthetic"]["perplexity"].append(
            float(avg_perplexity)
        )
        experiment_data[exp_type]["synthetic"]["structural_validity"].append(
            float(avg_structural)
        )

        if (epoch + 1) % 30 == 0:
            print(
                f"[{exp_type.upper()}] Epoch {epoch+1}/{num_epochs}, Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}, Spec Adherence: {avg_spec_adherence:.4f}, Perplexity: {avg_perplexity:.2f}, Structural: {avg_structural:.3f}"
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
    violation_tracker = (
        ViolationTracker(window_size=5) if scorer.use_violation_penalty else None
    )

    with torch.no_grad():
        for step in range(max_length):
            input_tensor = torch.tensor([current_ids], dtype=torch.long).to(device)
            logits, _ = model(input_tensor)
            lm_logits = (logits[0, -1, :] / temperature).cpu().numpy()
            spec_scores = np.zeros(len(dataset.vocab))
            for token_id, token in dataset.id_to_token.items():
                spec_scores[token_id] = scorer.score_partial_code(
                    problem_idx, current_tokens, token, violation_tracker
                )
            spec_mean = np.mean(spec_scores)
            spec_std = np.std(spec_scores) + 1e-6
            spec_normalized = (spec_scores - spec_mean) / spec_std
            blended_logits = (
                1 - spec_weight
            ) * lm_logits + spec_weight * spec_normalized
            blended_probs = F.softmax(torch.tensor(blended_logits), dim=-1).numpy()
            next_token_id = np.random.choice(len(dataset.vocab), p=blended_probs)
            next_token = dataset.id_to_token[next_token_id]

            if violation_tracker:
                if next_token in problem.get("forbidden_tokens", []):
                    violation_tracker.record_violation("forbidden", next_token)
                elif (
                    step >= 10
                    and "return" not in current_tokens
                    and next_token != "return"
                ):
                    violation_tracker.record_violation("structural")

            current_ids.append(next_token_id)
            current_tokens.append(next_token)
            if next_token == "<END>":
                break
    return current_tokens


def evaluate_on_dataset(
    model,
    dataset,
    hf_dataset_name,
    num_samples=100,
    num_seeds=5,
    spec_level="full",
    use_violation_penalty=False,
    exp_type="baseline",
):
    print(
        f"\n[{exp_type.upper()}] Evaluating on {hf_dataset_name} ({spec_level} specs) with {num_seeds} seeds"
    )
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
            return
        samples = list(hf_dataset.select(range(min(num_samples, len(hf_dataset)))))

        for weight in spec_weights:
            scorer = SpecificationScorer(
                dataset,
                spec_level=spec_level,
                use_violation_penalty=use_violation_penalty,
            )
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

        dataset_key = hf_dataset_name if spec_level == "full" else spec_level + "_specs"
        experiment_data[exp_type][dataset_key]["spec_adherence"] = [
            np.mean(results[w]["adherence"]) for w in spec_weights
        ]
        experiment_data[exp_type][dataset_key]["satisfaction_rates"] = [
            np.mean(results[w]["satisfaction"]) for w in spec_weights
        ]
        experiment_data[exp_type][dataset_key]["swpr_scores"] = [
            np.mean(results[w]["swpr"]) for w in spec_weights
        ]
        experiment_data[exp_type][dataset_key]["perplexity"] = [
            np.mean(results[w]["perplexity"]) for w in spec_weights
        ]
        experiment_data[exp_type][dataset_key]["structural_validity"] = [
            np.mean(results[w]["structural"]) for w in spec_weights
        ]
    except Exception as e:
        print(f"Error loading {hf_dataset_name}: {e}")


def create_visualizations():
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    weights = [0.0, 0.3, 0.5, 0.7, 1.0]

    epochs = range(1, len(experiment_data["baseline"]["synthetic"]["train_losses"]) + 1)
    axes[0, 0].plot(
        epochs,
        experiment_data["baseline"]["synthetic"]["train_losses"],
        label="Baseline Train",
        linewidth=2,
        linestyle="--",
    )
    axes[0, 0].plot(
        epochs,
        experiment_data["ablation"]["synthetic"]["train_losses"],
        label="Ablation Train",
        linewidth=2,
    )
    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].set_ylabel("Loss")
    axes[0, 0].set_title("Training Loss Comparison")
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(
        epochs,
        experiment_data["baseline"]["synthetic"]["spec_adherence"],
        label="Baseline",
        linewidth=2,
        linestyle="--",
        color="blue",
    )
    axes[0, 1].plot(
        epochs,
        experiment_data["ablation"]["synthetic"]["spec_adherence"],
        label="Ablation",
        linewidth=2,
        color="green",
    )
    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].set_ylabel("Spec Adherence")
    axes[0, 1].set_title("Specification Adherence Comparison")
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    axes[0, 2].plot(
        epochs,
        experiment_data["baseline"]["synthetic"]["perplexity"],
        label="Baseline",
        linewidth=2,
        linestyle="--",
        color="red",
    )
    axes[0, 2].plot(
        epochs,
        experiment_data["ablation"]["synthetic"]["perplexity"],
        label="Ablation",
        linewidth=2,
        color="orange",
    )
    axes[0, 2].set_xlabel("Epoch")
    axes[0, 2].set_ylabel("Perplexity")
    axes[0, 2].set_title("Perplexity Comparison")
    axes[0, 2].legend()
    axes[0, 2].grid(alpha=0.3)

    for dataset_name, label, color in [
        ("code_x_glue", "CodeXGLUE", "blue"),
        ("code_search_net", "CodeSearchNet", "orange"),
        ("mbpp", "MBPP", "green"),
    ]:
        base_adherence = experiment_data["baseline"][dataset_name]["spec_adherence"]
        abl_adherence = experiment_data["ablation"][dataset_name]["spec_adherence"]
        if len(base_adherence) > 0:
            axes[1, 0].plot(
                weights,
                base_adherence,
                "o--",
                label=f"{label} Base",
                color=color,
                linewidth=2,
                markersize=6,
                alpha=0.6,
            )
            axes[1, 0].plot(
                weights,
                abl_adherence,
                "o-",
                label=f"{label} Abl",
                color=color,
                linewidth=2,
                markersize=6,
            )
    axes[1, 0].set_xlabel("Spec Weight")
    axes[1, 0].set_ylabel("Spec Adherence")
    axes[1, 0].set_title("Adherence: Baseline vs Ablation")
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(alpha=0.3)

    for dataset_name, label, color in [
        ("code_x_glue", "CodeXGLUE", "blue"),
        ("code_search_net", "CodeSearchNet", "orange"),
        ("mbpp", "MBPP", "green"),
    ]:
        base_perp = experiment_data["baseline"][dataset_name]["perplexity"]
        abl_perp = experiment_data["ablation"][dataset_name]["perplexity"]
        if len(base_perp) > 0:
            axes[1, 1].plot(
                weights,
                base_perp,
                "s--",
                label=f"{label} Base",
                color=color,
                linewidth=2,
                markersize=6,
                alpha=0.6,
            )
            axes[1, 1].plot(
                weights,
                abl_perp,
                "s-",
                label=f"{label} Abl",
                color=color,
                linewidth=2,
                markersize=6,
            )
    axes[1, 1].set_xlabel("Spec Weight")
    axes[1, 1].set_ylabel("Perplexity")
    axes[1, 1].set_title("Perplexity: Baseline vs Ablation")
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(alpha=0.3)

    for dataset_name, label, color in [
        ("code_x_glue", "CodeXGLUE", "blue"),
        ("code_search_net", "CodeSearchNet", "orange"),
        ("mbpp", "MBPP", "green"),
    ]:
        base_struct = experiment_data["baseline"][dataset_name]["structural_validity"]
        abl_struct = experiment_data["ablation"][dataset_name]["structural_validity"]
        if len(base_struct) > 0:
            axes[1, 2].plot(
                weights,
                base_struct,
                "^--",
                label=f"{label} Base",
                color=color,
                linewidth=2,
                markersize=6,
                alpha=0.6,
            )
            axes[1, 2].plot(
                weights,
                abl_struct,
                "^-",
                label=f"{label} Abl",
                color=color,
                linewidth=2,
                markersize=6,
            )
    axes[1, 2].set_xlabel("Spec Weight")
    axes[1, 2].set_ylabel("Structural Validity")
    axes[1, 2].set_title("Structural: Baseline vs Ablation")
    axes[1, 2].legend(fontsize=8)
    axes[1, 2].grid(alpha=0.3)

    for spec_level, label, color in [
        ("code_x_glue", "Full", "blue"),
        ("partial_specs", "Partial", "orange"),
        ("weak_specs", "Weak", "red"),
    ]:
        base_adh = experiment_data["baseline"][spec_level]["spec_adherence"]
        abl_adh = experiment_data["ablation"][spec_level]["spec_adherence"]
        if len(base_adh) > 0:
            axes[2, 0].plot(
                weights,
                base_adh,
                "o--",
                label=f"{label} Base",
                color=color,
                linewidth=2,
                markersize=6,
                alpha=0.6,
            )
            axes[2, 0].plot(
                weights,
                abl_adh,
                "o-",
                label=f"{label} Abl",
                color=color,
                linewidth=2,
                markersize=6,
            )
    axes[2, 0].set_xlabel("Spec Weight")
    axes[2, 0].set_ylabel("Spec Adherence")
    axes[2, 0].set_title("Multi-level Specs: Baseline vs Ablation")
    axes[2, 0].legend(fontsize=8)
    axes[2, 0].grid(alpha=0.3)

    for dataset_name, label, color in [
        ("code_x_glue", "CodeXGLUE", "blue"),
        ("code_search_net", "CodeSearchNet", "orange"),
        ("mbpp", "MBPP", "green"),
    ]:
        base_swpr = experiment_data["baseline"][dataset_name]["swpr_scores"]
        abl_swpr = experiment_data["ablation"][dataset_name]["swpr_scores"]
        if len(base_swpr) > 0:
            axes[2, 1].plot(
                weights,
                base_swpr,
                "d--",
                label=f"{label} Base",
                color=color,
                linewidth=2,
                markersize=6,
                alpha=0.6,
            )
            axes[2, 1].plot(
                weights,
                abl_swpr,
                "d-",
                label=f"{label} Abl",
                color=color,
                linewidth=2,
                markersize=6,
            )
    axes[2, 1].set_xlabel("Spec Weight")
    axes[2, 1].set_ylabel("SWPR Score")
    axes[2, 1].set_title("SWPR: Baseline vs Ablation")
    axes[2, 1].legend(fontsize=8)
    axes[2, 1].grid(alpha=0.3)

    improvement_data = []
    for dataset_name in ["code_x_glue", "code_search_net", "mbpp"]:
        base_adh = experiment_data["baseline"][dataset_name]["spec_adherence"]
        abl_adh = experiment_data["ablation"][dataset_name]["spec_adherence"]
        if len(base_adh) > 0 and len(abl_adh) > 0:
            improvement = [(abl_adh[i] - base_adh[i]) for i in range(len(weights))]
            improvement_data.append(np.mean(improvement))
    if improvement_data:
        axes[2, 2].bar(
            ["CodeXGLUE", "CodeSearchNet", "MBPP"][: len(improvement_data)],
            improvement_data,
            color=["blue", "orange", "green"][: len(improvement_data)],
        )
        axes[2, 2].set_ylabel("Avg Adherence Improvement")
        axes[2, 2].set_title("Ablation Impact on Adherence")
        axes[2, 2].grid(alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(os.path.join(working_dir, "ablation_comparison.png"), dpi=150)
    plt.close()
    print("Visualization saved")


print("=" * 60)
print("ABLATION STUDY: Violation Penalty Mechanism")
print("=" * 60)

dataset = CodeSpecificationDataset()
print(f"Vocab: {len(dataset.vocab)}, Problems: {len(dataset.problems)}")

print("\n[BASELINE] Training model with fixed penalty...")
model_baseline = CodeGenerationModel(
    vocab_size=len(dataset.vocab), embed_dim=128, hidden_dim=256, num_layers=3
).to(device)
train_model(
    model_baseline,
    dataset,
    num_epochs=300,
    learning_rate=0.0005,
    seed=42,
    use_violation_penalty=False,
    exp_type="baseline",
)

print("\n[ABLATION] Training model with graduated violation penalty...")
model_ablation = CodeGenerationModel(
    vocab_size=len(dataset.vocab), embed_dim=128, hidden_dim=256, num_layers=3
).to(device)
train_model(
    model_ablation,
    dataset,
    num_epochs=300,
    learning_rate=0.0005,
    seed=42,
    use_violation_penalty=True,
    exp_type="ablation",
)

print("\n[BASELINE] Evaluating on datasets...")
for ds in ["code_x_glue", "code_search_net", "mbpp"]:
    evaluate_on_dataset(
        model_baseline,
        dataset,
        ds,
        num_samples=100,
        num_seeds=5,
        spec_level="full",
        use_violation_penalty=False,
        exp_type="baseline",
    )
evaluate_on_dataset(
    model_baseline,
    dataset,
    "code_x_glue",
    num_samples=100,
    num_seeds=5,
    spec_level="partial",
    use_violation_penalty=False,
    exp_type="baseline",
)
evaluate_on_dataset(
    model_baseline,
    dataset,
    "code_x_glue",
    num_samples=100,
    num_seeds=5,
    spec_level="weak",
    use_violation_penalty=False,
    exp_type="baseline",
)

print("\n[ABLATION] Evaluating on datasets...")
for ds in ["code_x_glue", "code_search_net", "mbpp"]:
    evaluate_on_dataset(
        model_ablation,
        dataset,
        ds,
        num_samples=100,
        num_seeds=5,
        spec_level="full",
        use_violation_penalty=True,
        exp_type="ablation",
    )
evaluate_on_dataset(
    model_ablation,
    dataset,
    "code_x_glue",
    num_samples=100,
    num_seeds=5,
    spec_level="partial",
    use_violation_penalty=True,
    exp_type="ablation",
)
evaluate_on_dataset(
    model_ablation,
    dataset,
    "code_x_glue",
    num_samples=100,
    num_seeds=5,
    spec_level="weak",
    use_violation_penalty=True,
    exp_type="ablation",
)

create_visualizations()
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nData saved to {working_dir}")
print("=" * 60)
print("Ablation study completed!")
print("=" * 60)
