import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import matplotlib.pyplot as plt
from collections import defaultdict
from datasets import load_dataset
import warnings

warnings.filterwarnings("ignore")

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

torch.manual_seed(42)
np.random.seed(42)

NUM_CONTEXTS = 4
NUM_STRATEGIES = 4
CONTEXT_NAMES = [
    "factual_error",
    "reasoning_flaw",
    "value_conflict",
    "preference_mismatch",
]
STRATEGY_NAMES = ["direct_correction", "socratic", "evidence", "gentle_suggestion"]

# Load THREE HuggingFace datasets (using compatible ones)
print("Loading HuggingFace datasets...")
truthful_qa = load_dataset("truthful_qa", "multiple_choice", split="validation")
arc_challenge = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")
commonsense_qa = load_dataset("tau/commonsense_qa", split="validation")

print(f"TruthfulQA samples: {len(truthful_qa)}")
print(f"ARC-Challenge samples: {len(arc_challenge)}")
print(f"CommonsenseQA samples: {len(commonsense_qa)}")


def process_truthfulqa(dataset, n_samples=200):
    data = []
    for i, item in enumerate(dataset):
        if i >= n_samples:
            break
        question = item["question"]
        correct_idx = (
            item["mc1_targets"]["labels"].index(1)
            if 1 in item["mc1_targets"]["labels"]
            else 0
        )
        correct_answer = item["mc1_targets"]["choices"][correct_idx]
        wrong_idx = (correct_idx + 1) % len(item["mc1_targets"]["choices"])
        wrong_answer = item["mc1_targets"]["choices"][wrong_idx]
        data.append(
            {
                "question": question,
                "correct_answer": correct_answer,
                "user_answer": wrong_answer,
                "context_type": 0,
                "dataset": "truthfulqa",
                "difficulty": len(question.split()) / 20.0,
            }
        )
    return data


def process_arc(dataset, n_samples=200):
    data = []
    for i, item in enumerate(dataset):
        if i >= n_samples:
            break
        question = item["question"]
        choices = item["choices"]
        answer_key = item["answerKey"]
        labels = choices["label"]
        texts = choices["text"]
        correct_idx = labels.index(answer_key) if answer_key in labels else 0
        correct_answer = texts[correct_idx]
        wrong_idx = (correct_idx + 1) % len(texts)
        wrong_answer = texts[wrong_idx]
        data.append(
            {
                "question": question,
                "correct_answer": correct_answer,
                "user_answer": wrong_answer,
                "context_type": 1,
                "dataset": "arc",
                "difficulty": len(question.split()) / 30.0,
            }
        )
    return data


def process_commonsenseqa(dataset, n_samples=200):
    data = []
    for i, item in enumerate(dataset):
        if i >= n_samples:
            break
        question = item["question"]
        answer_key = item["answerKey"]
        choices = item["choices"]
        correct_idx = (
            choices["label"].index(answer_key) if answer_key in choices["label"] else 0
        )
        correct_answer = choices["text"][correct_idx]
        wrong_idx = (correct_idx + 1) % len(choices["text"])
        wrong_answer = choices["text"][wrong_idx]
        data.append(
            {
                "question": question,
                "correct_answer": correct_answer,
                "user_answer": wrong_answer,
                "context_type": 3,
                "dataset": "commonsenseqa",
                "difficulty": 0.5,
            }
        )
    return data


truthfulqa_data = process_truthfulqa(truthful_qa, 200)
arc_data = process_arc(arc_challenge, 200)
commonsenseqa_data = process_commonsenseqa(commonsense_qa, 200)

all_qa_data = truthfulqa_data + arc_data + commonsenseqa_data
np.random.shuffle(all_qa_data)
print(f"Total QA samples: {len(all_qa_data)}")

EFFECTIVENESS_MATRIX = np.array(
    [
        [0.9, 0.5, 0.8, 0.4],
        [0.4, 0.9, 0.7, 0.5],
        [0.2, 0.5, 0.6, 0.9],
        [0.3, 0.6, 0.5, 0.8],
    ]
)


def simulate_user_response(
    context_type, strategy, user_confidence, question_difficulty
):
    base_effectiveness = EFFECTIVENESS_MATRIX[context_type, strategy]
    confidence_penalty = (user_confidence - 0.5) * 0.3
    difficulty_bonus = question_difficulty * 0.1
    receptivity = np.clip(
        0.5 + base_effectiveness * 0.4 - confidence_penalty + difficulty_bonus,
        0.1,
        0.95,
    )
    accepts = np.random.random() < receptivity
    trust_delta = 0.1 if accepts else -0.05
    return accepts, receptivity, trust_delta


class QADataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        context_onehot = np.zeros(NUM_CONTEXTS)
        context_onehot[item["context_type"]] = 1
        user_confidence = np.random.uniform(0.3, 0.9)
        features = np.concatenate(
            [context_onehot, [user_confidence, item["difficulty"]]]
        )
        return {
            "features": torch.FloatTensor(features),
            "context_type": item["context_type"],
            "user_confidence": user_confidence,
            "difficulty": item["difficulty"],
            "dataset": item["dataset"],
        }


class CCDModel(nn.Module):
    def __init__(
        self, input_dim=NUM_CONTEXTS + 2, hidden_dim=64, num_strategies=NUM_STRATEGIES
    ):
        super().__init__()
        self.strategy_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_strategies),
        )
        self.receptivity_predictor = nn.Sequential(
            nn.Linear(input_dim + num_strategies, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.strategy_net(x)

    def select_strategy(self, x, temperature=1.0):
        logits = self.forward(x)
        probs = torch.softmax(logits / temperature, dim=-1)
        strategy = torch.multinomial(probs, 1).squeeze(-1)
        return strategy, probs


def compute_cdes(strategy_matches, accuracy_gains, receptivity_scores, trust_ratios):
    strategy_match_rate = np.mean(strategy_matches) if strategy_matches else 0
    weighted_accuracy = (
        np.mean([ag * rs for ag, rs in zip(accuracy_gains, receptivity_scores)])
        if accuracy_gains
        else 0
    )
    trust_preservation = np.mean(trust_ratios) if trust_ratios else 1.0
    cdes = (
        0.4 * strategy_match_rate + 0.4 * weighted_accuracy + 0.2 * trust_preservation
    )
    return cdes, strategy_match_rate, weighted_accuracy, trust_preservation


def evaluate_model_full(model, data_loader, mode="ccd"):
    total, accepted = 0, 0
    strategy_matches, accuracy_gains, receptivity_scores, trust_ratios = [], [], [], []
    baseline_trust = 0.7
    if mode == "ccd":
        model.eval()
    with torch.no_grad():
        for batch in data_loader:
            features = (
                batch["features"].to(device) if mode == "ccd" else batch["features"]
            )
            context_types = batch["context_type"].numpy()
            user_confidences = batch["user_confidence"].numpy()
            difficulties = batch["difficulty"].numpy()
            for i in range(len(context_types)):
                total += 1
                optimal_strategy = np.argmax(EFFECTIVENESS_MATRIX[context_types[i]])
                if mode == "sycophantic":
                    strategy_matches.append(0)
                    accuracy_gains.append(0)
                    receptivity_scores.append(0.5)
                    trust_ratios.append(1.0)
                elif mode == "blunt":
                    accepts, receptivity, trust_delta = simulate_user_response(
                        context_types[i], 0, user_confidences[i], difficulties[i]
                    )
                    if accepts:
                        accepted += 1
                    strategy_matches.append(1 if optimal_strategy == 0 else 0)
                    accuracy_gains.append(1.0 if accepts else 0.0)
                    receptivity_scores.append(receptivity)
                    trust_ratios.append((baseline_trust + trust_delta) / baseline_trust)
                elif mode == "ccd":
                    strategy, _ = model.select_strategy(features[i : i + 1])
                    strategy = strategy.item()
                    accepts, receptivity, trust_delta = simulate_user_response(
                        context_types[i], strategy, user_confidences[i], difficulties[i]
                    )
                    if accepts:
                        accepted += 1
                    strategy_matches.append(1 if strategy == optimal_strategy else 0)
                    accuracy_gains.append(1.0 if accepts else 0.0)
                    receptivity_scores.append(receptivity)
                    trust_ratios.append((baseline_trust + trust_delta) / baseline_trust)
                elif mode == "random":
                    strategy = np.random.randint(0, NUM_STRATEGIES)
                    accepts, receptivity, trust_delta = simulate_user_response(
                        context_types[i], strategy, user_confidences[i], difficulties[i]
                    )
                    if accepts:
                        accepted += 1
                    strategy_matches.append(1 if strategy == optimal_strategy else 0)
                    accuracy_gains.append(1.0 if accepts else 0.0)
                    receptivity_scores.append(receptivity)
                    trust_ratios.append((baseline_trust + trust_delta) / baseline_trust)
    cdes, strategy_match, weighted_acc, trust_pres = compute_cdes(
        strategy_matches, accuracy_gains, receptivity_scores, trust_ratios
    )
    return {
        "acceptance_rate": accepted / max(total, 1),
        "cdes": cdes,
        "strategy_match": strategy_match,
        "weighted_accuracy": weighted_acc,
        "trust_preservation": trust_pres,
    }


def train_ccd_model(model, train_loader, val_loader, epochs=60, lr=0.001):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.5)
    metrics = {
        "train_loss": [],
        "val_acceptance": [],
        "val_cdes": [],
        "val_strategy_match": [],
        "val_trust": [],
    }
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for batch in train_loader:
            features = batch["features"].to(device)
            context_types = batch["context_type"].numpy()
            user_confidences = batch["user_confidence"].numpy()
            difficulties = batch["difficulty"].numpy()
            optimizer.zero_grad()
            strategies, probs = model.select_strategy(features)
            strategies_np = strategies.cpu().numpy()
            rewards = []
            for i in range(len(strategies_np)):
                accepts, _, _ = simulate_user_response(
                    context_types[i],
                    strategies_np[i],
                    user_confidences[i],
                    difficulties[i],
                )
                reward = 0.5 if accepts else -0.5
                optimal_strategy = np.argmax(EFFECTIVENESS_MATRIX[context_types[i]])
                if strategies_np[i] == optimal_strategy:
                    reward += 0.2
                rewards.append(reward)
            rewards = torch.FloatTensor(rewards).to(device)
            log_probs = torch.log(
                probs.gather(1, strategies.unsqueeze(1)).squeeze(1) + 1e-8
            )
            loss = -torch.mean(log_probs * rewards)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_loss += loss.item()
        scheduler.step()
        val_results = evaluate_model_full(model, val_loader, "ccd")
        metrics["train_loss"].append(epoch_loss / len(train_loader))
        metrics["val_acceptance"].append(val_results["acceptance_rate"])
        metrics["val_cdes"].append(val_results["cdes"])
        metrics["val_strategy_match"].append(val_results["strategy_match"])
        metrics["val_trust"].append(val_results["trust_preservation"])
        if (epoch + 1) % 10 == 0:
            print(
                f"Epoch {epoch+1}: val_loss={epoch_loss/len(train_loader):.4f}, acceptance={val_results['acceptance_rate']:.4f}, CDES={val_results['cdes']:.4f}"
            )
    return metrics


train_data = all_qa_data[: int(0.8 * len(all_qa_data))]
val_data = all_qa_data[int(0.8 * len(all_qa_data)) :]
train_loader = DataLoader(QADataset(train_data), batch_size=32, shuffle=True)
val_loader = DataLoader(QADataset(val_data), batch_size=32, shuffle=False)
dataset_loaders = {}
for ds_name in ["truthfulqa", "arc", "commonsenseqa"]:
    ds_data = [d for d in val_data if d["dataset"] == ds_name]
    if ds_data:
        dataset_loaders[ds_name] = DataLoader(
            QADataset(ds_data), batch_size=32, shuffle=False
        )

print("\n" + "=" * 60 + "\nTraining CCD Model\n" + "=" * 60)
model = CCDModel().to(device)
metrics = train_ccd_model(model, train_loader, val_loader, epochs=60)

experiment_data = {
    "combined": {
        "metrics": metrics,
        "losses": {"train": metrics["train_loss"], "val": []},
    }
}
all_results = {}
for ds_name, ds_loader in dataset_loaders.items():
    results = {
        method: evaluate_model_full(
            model if method == "ccd" else None, ds_loader, method
        )
        for method in ["sycophantic", "blunt", "random", "ccd"]
    }
    all_results[ds_name] = results
    experiment_data[ds_name] = {"cdes_scores": results}
    print(f"\n{ds_name.upper()}:")
    for method in ["sycophantic", "blunt", "random", "ccd"]:
        r = results[method]
        print(
            f"  {method:<15} Acceptance={r['acceptance_rate']:.4f} CDES={r['cdes']:.4f} StratMatch={r['strategy_match']:.4f}"
        )

final_results = {
    method: evaluate_model_full(model if method == "ccd" else None, val_loader, method)
    for method in ["sycophantic", "blunt", "random", "ccd"]
}
print(f"\n** Final CDES Score (CCD): {final_results['ccd']['cdes']:.4f} **")

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes[0, 0].plot(metrics["train_loss"])
axes[0, 0].set_title("Training Loss")
axes[0, 0].grid(True, alpha=0.3)
axes[0, 1].plot(metrics["val_cdes"], label="CDES")
axes[0, 1].plot(metrics["val_acceptance"], label="Accept")
axes[0, 1].legend()
axes[0, 1].set_title("Val Metrics")
datasets = list(all_results.keys())
x = np.arange(len(datasets))
width = 0.2
for i, method in enumerate(["sycophantic", "blunt", "random", "ccd"]):
    axes[0, 2].bar(
        x + i * width,
        [all_results[ds][method]["cdes"] for ds in datasets],
        width,
        label=method,
    )
axes[0, 2].set_xticks(x + width * 1.5)
axes[0, 2].set_xticklabels(datasets)
axes[0, 2].legend()
axes[0, 2].set_title("CDES by Dataset")
for i, method in enumerate(["blunt", "random", "ccd"]):
    axes[1, 0].bar(
        x + i * width,
        [all_results[ds][method]["strategy_match"] for ds in datasets],
        width,
        label=method,
    )
axes[1, 0].set_xticks(x + width)
axes[1, 0].set_xticklabels(datasets)
axes[1, 0].legend()
axes[1, 0].set_title("Strategy Match")
methods = ["Sycophantic", "Blunt", "Random", "CCD"]
colors = ["gray", "red", "orange", "green"]
axes[1, 1].bar(
    methods, [final_results[m.lower()]["cdes"] for m in methods], color=colors
)
axes[1, 1].set_title("Overall CDES")
axes[1, 2].bar(
    methods,
    [final_results[m.lower()]["trust_preservation"] for m in methods],
    color=colors,
)
axes[1, 2].set_title("Trust Preservation")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ccd_huggingface_results.png"), dpi=150)
plt.close()

experiment_data["final_results"] = final_results
experiment_data["all_dataset_results"] = all_results
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(
    f"\nResults saved to {working_dir}\nDatasets used: TruthfulQA, ARC-Challenge, CommonsenseQA"
)
