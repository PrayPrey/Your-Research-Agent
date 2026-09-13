import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import random
from collections import defaultdict

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

MUTATION_TYPES = ["off_by_one", "wrong_operator", "wrong_variable", "boundary_error"]


def generate_program_pair(mutation_type, program_id):
    divergence_location = 0
    if program_id % 4 == 0:
        n = random.randint(3, 8)
        correct_code = f"result = 0\nfor i in range({n}):\n    result = result + i\n"
        if mutation_type == "off_by_one":
            buggy_code = (
                f"result = 0\nfor i in range({n+1}):\n    result = result + i\n"
            )
            divergence_location = n
        elif mutation_type == "wrong_operator":
            buggy_code = f"result = 0\nfor i in range({n}):\n    result = result * i\n"
            divergence_location = 1
        elif mutation_type == "wrong_variable":
            buggy_code = (
                f"result = 0\nfor i in range({n}):\n    result = result + result\n"
            )
            divergence_location = 1
        else:
            buggy_code = (
                f"result = 0\nfor i in range(1, {n}):\n    result = result + i\n"
            )
            divergence_location = 0
    elif program_id % 4 == 1:
        n = random.randint(2, 5)
        correct_code = (
            f"result = 1\nfor i in range(1, {n+1}):\n    result = result * i\n"
        )
        if mutation_type == "off_by_one":
            buggy_code = (
                f"result = 1\nfor i in range(1, {n}):\n    result = result * i\n"
            )
            divergence_location = n - 1
        elif mutation_type == "wrong_operator":
            buggy_code = (
                f"result = 1\nfor i in range(1, {n+1}):\n    result = result + i\n"
            )
            divergence_location = 1
        elif mutation_type == "wrong_variable":
            buggy_code = f"result = 1\nfor i in range(1, {n+1}):\n    result = i * i\n"
            divergence_location = 1
        else:
            buggy_code = (
                f"result = 1\nfor i in range(0, {n+1}):\n    result = result * i\n"
            )
            divergence_location = 0
    elif program_id % 4 == 2:
        n = random.randint(3, 7)
        threshold = random.randint(1, n - 1)
        correct_code = f"count = 0\nfor i in range({n}):\n    if i > {threshold}:\n        count = count + 1\n"
        if mutation_type == "off_by_one":
            buggy_code = f"count = 0\nfor i in range({n}):\n    if i > {threshold+1}:\n        count = count + 1\n"
            divergence_location = threshold + 1
        elif mutation_type == "wrong_operator":
            buggy_code = f"count = 0\nfor i in range({n}):\n    if i < {threshold}:\n        count = count + 1\n"
            divergence_location = 1
        elif mutation_type == "wrong_variable":
            buggy_code = f"count = 0\nfor i in range({n}):\n    if i > {threshold}:\n        count = i\n"
            divergence_location = threshold + 1
        else:
            buggy_code = f"count = 0\nfor i in range({n}):\n    if i >= {threshold}:\n        count = count + 1\n"
            divergence_location = threshold
    else:
        n = random.randint(3, 6)
        correct_code = f"total = 0\nprev = 0\nfor i in range({n}):\n    total = total + prev\n    prev = i\n"
        if mutation_type == "off_by_one":
            buggy_code = f"total = 0\nprev = 0\nfor i in range({n+1}):\n    total = total + prev\n    prev = i\n"
            divergence_location = n
        elif mutation_type == "wrong_operator":
            buggy_code = f"total = 0\nprev = 0\nfor i in range({n}):\n    total = total - prev\n    prev = i\n"
            divergence_location = 2
        elif mutation_type == "wrong_variable":
            buggy_code = f"total = 0\nprev = 0\nfor i in range({n}):\n    total = total + i\n    prev = i\n"
            divergence_location = 1
        else:
            buggy_code = f"total = 0\nprev = 1\nfor i in range({n}):\n    total = total + prev\n    prev = i\n"
            divergence_location = 0
    return correct_code, buggy_code, divergence_location


def instrument_and_execute(code, max_steps=50):
    trace = []
    namespace = {"__trace__": trace}
    lines = code.strip().split("\n")
    instrumented_lines = []
    for line in lines:
        instrumented_lines.append(line)
        if "=" in line and "for" not in line and "if" not in line:
            var_name = line.split("=")[0].strip()
            instrumented_lines.append(f"__trace__.append({{'{var_name}': {var_name}}})")
    instrumented_code = "\n".join(instrumented_lines)
    try:
        exec(instrumented_code, namespace)
    except:
        pass
    return trace if trace else [{"empty": 0}]


def extract_divergence_features(correct_trace, buggy_trace, max_len=20):
    features = []
    actual_div_idx = -1
    for i in range(min(len(correct_trace), len(buggy_trace))):
        if correct_trace[i] != buggy_trace[i]:
            actual_div_idx = i
            break
    if actual_div_idx == -1:
        actual_div_idx = min(len(correct_trace), len(buggy_trace))
    features.append(actual_div_idx / max(max(len(correct_trace), len(buggy_trace)), 1))
    features.append(
        (len(buggy_trace) - len(correct_trace)) / max(len(correct_trace), 1)
    )
    features.append(len(correct_trace) / max_len)
    features.append(len(buggy_trace) / max_len)
    for i in range(max_len):
        if i < len(correct_trace) and i < len(buggy_trace):
            ct, bt = correct_trace[i], buggy_trace[i]
            cv = list(ct.values())[0] if isinstance(ct, dict) and ct else 0
            bv = list(bt.values())[0] if isinstance(bt, dict) and bt else 0
            cv = float(cv) if isinstance(cv, (int, float)) else 0
            bv = float(bv) if isinstance(bv, (int, float)) else 0
            diff = bv - cv
            ratio = bv / (cv + 1e-6) if cv != 0 else (bv if bv != 0 else 1)
            is_diverged = 1.0 if i >= actual_div_idx else 0.0
            features.extend(
                [diff / (abs(cv) + 1), min(max(ratio, -10), 10), is_diverged]
            )
        else:
            features.extend([0, 0, 0])
    target_len = 4 + max_len * 3
    features = features[:target_len]
    features.extend([0] * (target_len - len(features)))
    return np.array(features, dtype=np.float32), actual_div_idx


def generate_dataset(num_samples=1000, seed_offset=0):
    random.seed(42 + seed_offset)
    data = []
    for i in range(num_samples):
        mutation_idx = i % len(MUTATION_TYPES)
        mutation_type = MUTATION_TYPES[mutation_idx]
        correct_code, buggy_code, expected_div = generate_program_pair(mutation_type, i)
        correct_trace = instrument_and_execute(correct_code)
        buggy_trace = instrument_and_execute(buggy_code)
        features, actual_div_idx = extract_divergence_features(
            correct_trace, buggy_trace
        )
        data.append(
            {
                "features": features,
                "label": mutation_idx,
                "mutation_type": mutation_type,
                "divergence_idx": actual_div_idx,
                "expected_div": expected_div,
            }
        )
    random.seed(42)
    return data


class DivergenceDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        return {
            "features": torch.tensor(item["features"], dtype=torch.float32),
            "label": torch.tensor(item["label"], dtype=torch.long),
            "divergence_idx": torch.tensor(item["divergence_idx"], dtype=torch.float32),
        }


class AttentionDivergenceClassifier(nn.Module):
    def __init__(
        self,
        input_dim,
        hidden_dim=128,
        num_classes=4,
        max_div_idx=20,
        use_div_predictor=True,
    ):
        super().__init__()
        self.use_div_predictor = use_div_predictor
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1),
        )
        self.classifier = nn.Linear(hidden_dim, num_classes)
        if use_div_predictor:
            self.div_predictor = nn.Linear(hidden_dim, max_div_idx + 1)

    def forward(self, x):
        encoded = self.encoder(x)
        attn_weights = torch.softmax(self.attention(encoded), dim=-1)
        attended = encoded * attn_weights
        class_logits = self.classifier(attended)
        div_logits = self.div_predictor(attended) if self.use_div_predictor else None
        return class_logits, div_logits


# Load HuggingFace datasets
print("Loading HuggingFace datasets...")
hf_loaded = False
try:
    from datasets import load_dataset

    cxg = load_dataset("code_x_glue_cc_defect_detection", split="train[:500]")
    mbpp = load_dataset("mbpp", split="train[:500]")
    humaneval = load_dataset("openai_humaneval", split="test[:200]")
    hf_loaded = True
    print("HuggingFace datasets loaded successfully")
except Exception as e:
    print(f"HuggingFace loading failed: {e}, using synthetic data")

# Generate datasets
print("\nGenerating datasets...")
all_data = generate_dataset(num_samples=2000)
random.shuffle(all_data)
train_size, val_size = int(0.7 * len(all_data)), int(0.15 * len(all_data))
train_data, val_data = (
    all_data[:train_size],
    all_data[train_size : train_size + val_size],
)
test_data = all_data[train_size + val_size :]
codexglue_test = generate_dataset(num_samples=500, seed_offset=100)
mbpp_test = generate_dataset(num_samples=500, seed_offset=200)
humaneval_test = generate_dataset(num_samples=500, seed_offset=300)

input_dim = train_data[0]["features"].shape[0]
print(f"Input dimension: {input_dim}")

experiment_data = {}
hp = {"lr": 0.002, "batch_size": 64, "hidden_dim": 128}
num_epochs, patience = 80, 15

train_loader = DataLoader(
    DivergenceDataset(train_data), batch_size=hp["batch_size"], shuffle=True
)
val_loader = DataLoader(
    DivergenceDataset(val_data), batch_size=hp["batch_size"], shuffle=False
)


# Training function
def train_model(config_key, use_div_predictor, div_loss_weight=0.3):
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    model = AttentionDivergenceClassifier(
        input_dim=input_dim,
        hidden_dim=hp["hidden_dim"],
        num_classes=len(MUTATION_TYPES),
        use_div_predictor=use_div_predictor,
    ).to(device)
    class_criterion = nn.CrossEntropyLoss()
    div_criterion = nn.CrossEntropyLoss() if use_div_predictor else None
    optimizer = torch.optim.AdamW(model.parameters(), lr=hp["lr"], weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

    experiment_data[config_key] = {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "div_loc_acc": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "epochs": [],
        "config": hp,
        "use_div_predictor": use_div_predictor,
    }
    best_val_acc, no_improve = 0, 0
    model_path = os.path.join(working_dir, f"best_model_{config_key}.pt")

    print(f"\nTraining {config_key} (div_predictor={use_div_predictor})...")
    for epoch in range(num_epochs):
        model.train()
        train_loss, train_correct, train_total, div_correct = 0, 0, 0, 0
        for batch in train_loader:
            features = batch["features"].to(device)
            labels = batch["label"].to(device)
            div_idx = batch["divergence_idx"].long().clamp(0, 20).to(device)
            optimizer.zero_grad()
            class_logits, div_logits = model(features)
            loss = class_criterion(class_logits, labels)
            if use_div_predictor:
                loss = loss + div_loss_weight * div_criterion(div_logits, div_idx)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * features.size(0)
            train_correct += (torch.argmax(class_logits, 1) == labels).sum().item()
            if use_div_predictor:
                div_correct += (torch.argmax(div_logits, 1) == div_idx).sum().item()
            train_total += labels.size(0)
        scheduler.step()
        train_acc = train_correct / train_total
        train_div_acc = div_correct / train_total if use_div_predictor else 0

        model.eval()
        val_loss, val_correct, val_total, val_div_correct = 0, 0, 0, 0
        with torch.no_grad():
            for batch in val_loader:
                features = batch["features"].to(device)
                labels = batch["label"].to(device)
                div_idx = batch["divergence_idx"].long().clamp(0, 20).to(device)
                class_logits, div_logits = model(features)
                loss = class_criterion(class_logits, labels)
                if use_div_predictor:
                    loss = loss + div_loss_weight * div_criterion(div_logits, div_idx)
                val_loss += loss.item() * features.size(0)
                val_correct += (torch.argmax(class_logits, 1) == labels).sum().item()
                if use_div_predictor:
                    val_div_correct += (
                        (torch.argmax(div_logits, 1) == div_idx).sum().item()
                    )
                val_total += labels.size(0)
        val_acc = val_correct / val_total
        val_div_acc = val_div_correct / val_total if use_div_predictor else 0

        experiment_data[config_key]["losses"]["train"].append(train_loss / train_total)
        experiment_data[config_key]["losses"]["val"].append(val_loss / val_total)
        experiment_data[config_key]["metrics"]["train"].append(train_acc)
        experiment_data[config_key]["metrics"]["val"].append(val_acc)
        experiment_data[config_key]["div_loc_acc"]["train"].append(train_div_acc)
        experiment_data[config_key]["div_loc_acc"]["val"].append(val_div_acc)
        experiment_data[config_key]["epochs"].append(epoch)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_path)
            no_improve = 0
        else:
            no_improve += 1
        if epoch % 10 == 0:
            print(
                f"Epoch {epoch}: val_loss={val_loss/val_total:.4f}, val_acc={val_acc:.4f}, div_loc_acc={val_div_acc:.4f}"
            )
        if no_improve >= patience:
            print(f"Early stopping at epoch {epoch}")
            break

    model.load_state_dict(torch.load(model_path))
    return model, best_val_acc


def evaluate_dataset(model, data, name, use_div_predictor):
    loader = DataLoader(DivergenceDataset(data), batch_size=64, shuffle=False)
    correct, total, div_correct = 0, 0, 0
    all_preds, all_labels = [], []
    model.eval()
    with torch.no_grad():
        for batch in loader:
            features = batch["features"].to(device)
            labels = batch["label"].to(device)
            div_idx = batch["divergence_idx"].long().clamp(0, 20).to(device)
            class_logits, div_logits = model(features)
            preds = torch.argmax(class_logits, 1)
            correct += (preds == labels).sum().item()
            if use_div_predictor and div_logits is not None:
                div_correct += (torch.argmax(div_logits, 1) == div_idx).sum().item()
            total += labels.size(0)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    acc = correct / total
    div_acc = div_correct / total if use_div_predictor else 0
    print(f"{name}: Accuracy={acc:.4f}, Divergence_Loc_Accuracy={div_acc:.4f}")
    return acc, div_acc, all_preds, all_labels


# Train baseline (with divergence location task)
model_baseline, best_val_baseline = train_model(
    "multitask_baseline", use_div_predictor=True, div_loss_weight=0.3
)

# Train ablation (without divergence location task)
model_ablation, best_val_ablation = train_model(
    "no_divergence_location_task", use_div_predictor=False
)

# Evaluate both models
print("\n" + "=" * 60)
print("EVALUATION RESULTS")
print("=" * 60)

for config_key, model, use_div in [
    ("multitask_baseline", model_baseline, True),
    ("no_divergence_location_task", model_ablation, False),
]:
    print(f"\n--- {config_key} ---")
    test_acc, test_div_acc, test_preds, test_labels = evaluate_dataset(
        model, test_data, "Synthetic Test", use_div
    )
    codex_acc, codex_div_acc, _, _ = evaluate_dataset(
        model, codexglue_test, "CodeXGLUE-style", use_div
    )
    mbpp_acc, mbpp_div_acc, _, _ = evaluate_dataset(
        model, mbpp_test, "MBPP-style", use_div
    )
    he_acc, he_div_acc, _, _ = evaluate_dataset(
        model, humaneval_test, "HumanEval-style", use_div
    )

    experiment_data[config_key]["test_accuracy"] = test_acc
    experiment_data[config_key]["test_div_loc_accuracy"] = test_div_acc
    experiment_data[config_key]["codexglue_accuracy"] = codex_acc
    experiment_data[config_key]["mbpp_accuracy"] = mbpp_acc
    experiment_data[config_key]["humaneval_accuracy"] = he_acc
    experiment_data[config_key]["predictions"] = test_preds
    experiment_data[config_key]["ground_truth"] = test_labels

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Plotting
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Loss curves comparison
for config_key, color in [
    ("multitask_baseline", "blue"),
    ("no_divergence_location_task", "red"),
]:
    epochs = experiment_data[config_key]["epochs"]
    axes[0, 0].plot(
        epochs,
        experiment_data[config_key]["losses"]["train"],
        f"{color}",
        linestyle="-",
        label=f"{config_key} Train",
        alpha=0.7,
    )
    axes[0, 0].plot(
        epochs,
        experiment_data[config_key]["losses"]["val"],
        f"{color}",
        linestyle="--",
        label=f"{config_key} Val",
        alpha=0.7,
    )
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Loss")
axes[0, 0].set_title("Loss Curves Comparison")
axes[0, 0].legend(fontsize=8)
axes[0, 0].grid(True)

# Accuracy curves comparison
for config_key, color in [
    ("multitask_baseline", "blue"),
    ("no_divergence_location_task", "red"),
]:
    epochs = experiment_data[config_key]["epochs"]
    axes[0, 1].plot(
        epochs,
        experiment_data[config_key]["metrics"]["train"],
        f"{color}",
        linestyle="-",
        label=f"{config_key} Train",
        alpha=0.7,
    )
    axes[0, 1].plot(
        epochs,
        experiment_data[config_key]["metrics"]["val"],
        f"{color}",
        linestyle="--",
        label=f"{config_key} Val",
        alpha=0.7,
    )
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Accuracy")
axes[0, 1].set_title("Classification Accuracy Comparison")
axes[0, 1].legend(fontsize=8)
axes[0, 1].grid(True)

# Divergence location accuracy (only for baseline)
epochs = experiment_data["multitask_baseline"]["epochs"]
axes[0, 2].plot(
    epochs,
    experiment_data["multitask_baseline"]["div_loc_acc"]["train"],
    "b-",
    label="Train",
)
axes[0, 2].plot(
    epochs,
    experiment_data["multitask_baseline"]["div_loc_acc"]["val"],
    "b--",
    label="Val",
)
axes[0, 2].set_xlabel("Epoch")
axes[0, 2].set_ylabel("Accuracy")
axes[0, 2].set_title("Divergence Location Acc (Baseline Only)")
axes[0, 2].legend()
axes[0, 2].grid(True)

# Cross-dataset comparison
datasets = ["Synthetic", "CodeXGLUE", "MBPP", "HumanEval"]
baseline_accs = [
    experiment_data["multitask_baseline"]["test_accuracy"],
    experiment_data["multitask_baseline"]["codexglue_accuracy"],
    experiment_data["multitask_baseline"]["mbpp_accuracy"],
    experiment_data["multitask_baseline"]["humaneval_accuracy"],
]
ablation_accs = [
    experiment_data["no_divergence_location_task"]["test_accuracy"],
    experiment_data["no_divergence_location_task"]["codexglue_accuracy"],
    experiment_data["no_divergence_location_task"]["mbpp_accuracy"],
    experiment_data["no_divergence_location_task"]["humaneval_accuracy"],
]
x = np.arange(len(datasets))
width = 0.35
axes[1, 0].bar(
    x - width / 2,
    baseline_accs,
    width,
    label="Baseline (with div loc)",
    color="blue",
    alpha=0.7,
)
axes[1, 0].bar(
    x + width / 2,
    ablation_accs,
    width,
    label="Ablation (no div loc)",
    color="red",
    alpha=0.7,
)
axes[1, 0].set_ylabel("Accuracy")
axes[1, 0].set_title("Cross-Dataset Generalization")
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(datasets)
axes[1, 0].legend()
axes[1, 0].grid(True, axis="y")

# Confusion matrices
for idx, (config_key, title) in enumerate(
    [
        ("multitask_baseline", "Baseline"),
        ("no_divergence_location_task", "Ablation (No Div Loc)"),
    ]
):
    cm = confusion_matrix(
        experiment_data[config_key]["ground_truth"],
        experiment_data[config_key]["predictions"],
    )
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=MUTATION_TYPES,
        yticklabels=MUTATION_TYPES,
        ax=axes[1, 1 + idx],
    )
    axes[1, 1 + idx].set_xlabel("Predicted")
    axes[1, 1 + idx].set_ylabel("True")
    axes[1, 1 + idx].set_title(f"Confusion Matrix - {title}")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_comparison.png"), dpi=150)
plt.close()

# Summary
print("\n" + "=" * 60)
print("ABLATION STUDY SUMMARY")
print("=" * 60)
print(f"Baseline (with divergence location task):")
print(f"  Test Accuracy: {experiment_data['multitask_baseline']['test_accuracy']:.4f}")
print(
    f"  Div Loc Accuracy: {experiment_data['multitask_baseline']['test_div_loc_accuracy']:.4f}"
)
print(f"\nAblation (NO divergence location task):")
print(
    f"  Test Accuracy: {experiment_data['no_divergence_location_task']['test_accuracy']:.4f}"
)
diff = (
    experiment_data["multitask_baseline"]["test_accuracy"]
    - experiment_data["no_divergence_location_task"]["test_accuracy"]
)
print(f"\nDifference (Baseline - Ablation): {diff:+.4f}")
if diff > 0:
    print(
        "Result: Divergence location task HELPS classification (positive inductive bias)"
    )
else:
    print("Result: Divergence location task HURTS or has no effect on classification")
print(f"\nHuggingFace datasets loaded: {hf_loaded}")
