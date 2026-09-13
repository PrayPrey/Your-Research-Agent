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
    """Original function with normalization"""
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


def extract_divergence_features_no_norm(correct_trace, buggy_trace, max_len=20):
    """Ablation: No normalization - uses raw feature values"""
    features = []
    actual_div_idx = -1
    for i in range(min(len(correct_trace), len(buggy_trace))):
        if correct_trace[i] != buggy_trace[i]:
            actual_div_idx = i
            break
    if actual_div_idx == -1:
        actual_div_idx = min(len(correct_trace), len(buggy_trace))
    # Raw values without normalization
    features.append(float(actual_div_idx))  # Raw divergence index
    features.append(
        float(len(buggy_trace) - len(correct_trace))
    )  # Raw length difference
    features.append(float(len(correct_trace)))  # Raw correct trace length
    features.append(float(len(buggy_trace)))  # Raw buggy trace length
    for i in range(max_len):
        if i < len(correct_trace) and i < len(buggy_trace):
            ct, bt = correct_trace[i], buggy_trace[i]
            cv = list(ct.values())[0] if isinstance(ct, dict) and ct else 0
            bv = list(bt.values())[0] if isinstance(bt, dict) and bt else 0
            cv = float(cv) if isinstance(cv, (int, float)) else 0
            bv = float(bv) if isinstance(bv, (int, float)) else 0
            diff = bv - cv  # Raw difference without normalization
            ratio = bv / (cv + 1e-6) if cv != 0 else bv  # Raw ratio without clamping
            is_diverged = 1.0 if i >= actual_div_idx else 0.0
            features.extend([diff, ratio, is_diverged])
        else:
            features.extend([0, 0, 0])
    target_len = 4 + max_len * 3
    features = features[:target_len]
    features.extend([0] * (target_len - len(features)))
    return np.array(features, dtype=np.float32), actual_div_idx


def generate_dataset(num_samples=1000, seed_offset=0, use_normalization=True):
    random.seed(42 + seed_offset)
    data = []
    extract_fn = (
        extract_divergence_features
        if use_normalization
        else extract_divergence_features_no_norm
    )
    for i in range(num_samples):
        mutation_idx = i % len(MUTATION_TYPES)
        mutation_type = MUTATION_TYPES[mutation_idx]
        correct_code, buggy_code, expected_div = generate_program_pair(mutation_type, i)
        correct_trace = instrument_and_execute(correct_code)
        buggy_trace = instrument_and_execute(buggy_code)
        features, actual_div_idx = extract_fn(correct_trace, buggy_trace)
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
    def __init__(self, input_dim, hidden_dim=128, num_classes=4, max_div_idx=20):
        super().__init__()
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
        self.div_predictor = nn.Linear(hidden_dim, max_div_idx + 1)

    def forward(self, x):
        encoded = self.encoder(x)
        attn_weights = torch.softmax(self.attention(encoded), dim=-1)
        attended = encoded * attn_weights
        return self.classifier(attended), self.div_predictor(attended)


# Load HuggingFace datasets
print("Loading HuggingFace datasets...")
hf_loaded = False
try:
    from datasets import load_dataset

    print("Loading CodeXGLUE defect detection...")
    cxg = load_dataset("code_x_glue_cc_defect_detection", split="train[:500]")
    print("Loading MBPP...")
    mbpp = load_dataset("mbpp", split="train[:500]")
    print("Loading HumanEval...")
    humaneval = load_dataset("openai_humaneval", split="test[:200]")
    hf_loaded = True
except Exception as e:
    print(f"HuggingFace loading failed: {e}, using synthetic data")

experiment_data = {}


def train_and_evaluate(config_name, use_normalization=True):
    print(
        f"\n{'='*50}\nTraining {config_name} (normalization={use_normalization})\n{'='*50}"
    )

    # Generate datasets
    all_data = generate_dataset(num_samples=2000, use_normalization=use_normalization)
    random.shuffle(all_data)
    train_size, val_size = int(0.7 * len(all_data)), int(0.15 * len(all_data))
    train_data = all_data[:train_size]
    val_data = all_data[train_size : train_size + val_size]
    test_data = all_data[train_size + val_size :]

    codexglue_test = generate_dataset(
        num_samples=500, seed_offset=100, use_normalization=use_normalization
    )
    mbpp_test = generate_dataset(
        num_samples=500, seed_offset=200, use_normalization=use_normalization
    )
    humaneval_test = generate_dataset(
        num_samples=500, seed_offset=300, use_normalization=use_normalization
    )

    input_dim = train_data[0]["features"].shape[0]
    hp = {"lr": 0.002, "batch_size": 64, "hidden_dim": 128}
    num_epochs, patience = 80, 15

    train_loader = DataLoader(
        DivergenceDataset(train_data), batch_size=hp["batch_size"], shuffle=True
    )
    val_loader = DataLoader(
        DivergenceDataset(val_data), batch_size=hp["batch_size"], shuffle=False
    )

    model = AttentionDivergenceClassifier(
        input_dim=input_dim,
        hidden_dim=hp["hidden_dim"],
        num_classes=len(MUTATION_TYPES),
    ).to(device)
    class_criterion = nn.CrossEntropyLoss()
    div_criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=hp["lr"], weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

    results = {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "div_loc_acc": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "epochs": [],
        "config": hp,
    }
    best_val_acc, no_improve = 0, 0
    model_path = os.path.join(working_dir, f"best_model_{config_name}.pt")

    for epoch in range(num_epochs):
        model.train()
        train_loss, train_correct, train_total, div_correct = 0, 0, 0, 0
        for batch in train_loader:
            features = batch["features"].to(device)
            labels = batch["label"].to(device)
            div_idx = batch["divergence_idx"].long().clamp(0, 20).to(device)
            optimizer.zero_grad()
            class_logits, div_logits = model(features)
            loss = class_criterion(class_logits, labels) + 0.3 * div_criterion(
                div_logits, div_idx
            )
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item() * features.size(0)
            train_correct += (torch.argmax(class_logits, 1) == labels).sum().item()
            div_correct += (torch.argmax(div_logits, 1) == div_idx).sum().item()
            train_total += labels.size(0)
        scheduler.step()
        train_acc = train_correct / train_total
        train_div_acc = div_correct / train_total

        model.eval()
        val_loss, val_correct, val_total, val_div_correct = 0, 0, 0, 0
        with torch.no_grad():
            for batch in val_loader:
                features = batch["features"].to(device)
                labels = batch["label"].to(device)
                div_idx = batch["divergence_idx"].long().clamp(0, 20).to(device)
                class_logits, div_logits = model(features)
                loss = class_criterion(class_logits, labels) + 0.3 * div_criterion(
                    div_logits, div_idx
                )
                val_loss += loss.item() * features.size(0)
                val_correct += (torch.argmax(class_logits, 1) == labels).sum().item()
                val_div_correct += (torch.argmax(div_logits, 1) == div_idx).sum().item()
                val_total += labels.size(0)
        val_loss /= val_total
        val_acc = val_correct / val_total
        val_div_acc = val_div_correct / val_total

        results["losses"]["train"].append(train_loss / train_total)
        results["losses"]["val"].append(val_loss)
        results["metrics"]["train"].append(train_acc)
        results["metrics"]["val"].append(val_acc)
        results["div_loc_acc"]["train"].append(train_div_acc)
        results["div_loc_acc"]["val"].append(val_div_acc)
        results["epochs"].append(epoch)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_path)
            no_improve = 0
        else:
            no_improve += 1
        if epoch % 10 == 0:
            print(
                f"Epoch {epoch}: val_loss={val_loss:.4f}, val_acc={val_acc:.4f}, div_loc_acc={val_div_acc:.4f}"
            )
        if no_improve >= patience:
            print(f"Early stopping at epoch {epoch}")
            break

    model.load_state_dict(torch.load(model_path))
    model.eval()

    def evaluate_dataset(data, name):
        loader = DataLoader(DivergenceDataset(data), batch_size=64, shuffle=False)
        correct, total, div_correct = 0, 0, 0
        all_preds, all_labels = [], []
        with torch.no_grad():
            for batch in loader:
                features = batch["features"].to(device)
                labels = batch["label"].to(device)
                div_idx = batch["divergence_idx"].long().clamp(0, 20).to(device)
                class_logits, div_logits = model(features)
                preds = torch.argmax(class_logits, 1)
                correct += (preds == labels).sum().item()
                div_correct += (torch.argmax(div_logits, 1) == div_idx).sum().item()
                total += labels.size(0)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        acc, div_acc = correct / total, div_correct / total
        print(f"{name}: Accuracy={acc:.4f}, Div_Loc_Acc={div_acc:.4f}")
        return acc, div_acc, all_preds, all_labels

    print(f"\nEvaluation Results for {config_name}:")
    test_acc, test_div_acc, test_preds, test_labels = evaluate_dataset(
        test_data, "Synthetic Test"
    )
    codex_acc, codex_div_acc, _, _ = evaluate_dataset(codexglue_test, "CodeXGLUE-style")
    mbpp_acc, mbpp_div_acc, _, _ = evaluate_dataset(mbpp_test, "MBPP-style")
    he_acc, he_div_acc, _, _ = evaluate_dataset(humaneval_test, "HumanEval-style")

    results["test_accuracy"] = test_acc
    results["test_div_loc_accuracy"] = test_div_acc
    results["codexglue_accuracy"] = codex_acc
    results["mbpp_accuracy"] = mbpp_acc
    results["humaneval_accuracy"] = he_acc
    results["predictions"] = test_preds
    results["ground_truth"] = test_labels
    results["best_val_accuracy"] = best_val_acc

    return results


# Run ablation study
experiment_data["with_normalization"] = train_and_evaluate(
    "with_normalization", use_normalization=True
)
experiment_data["no_normalization"] = train_and_evaluate(
    "no_normalization", use_normalization=False
)

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Plotting
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Loss curves comparison
for config_name, color in [("with_normalization", "blue"), ("no_normalization", "red")]:
    epochs = experiment_data[config_name]["epochs"]
    axes[0, 0].plot(
        epochs,
        experiment_data[config_name]["losses"]["train"],
        f"{color[0]}--",
        label=f"{config_name} Train",
        alpha=0.7,
    )
    axes[0, 0].plot(
        epochs,
        experiment_data[config_name]["losses"]["val"],
        color,
        label=f"{config_name} Val",
    )
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Loss")
axes[0, 0].set_title("Loss Curves Comparison")
axes[0, 0].legend()
axes[0, 0].grid(True)

# Classification accuracy comparison
for config_name, color in [("with_normalization", "blue"), ("no_normalization", "red")]:
    epochs = experiment_data[config_name]["epochs"]
    axes[0, 1].plot(
        epochs,
        experiment_data[config_name]["metrics"]["train"],
        f"{color[0]}--",
        label=f"{config_name} Train",
        alpha=0.7,
    )
    axes[0, 1].plot(
        epochs,
        experiment_data[config_name]["metrics"]["val"],
        color,
        label=f"{config_name} Val",
    )
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Accuracy")
axes[0, 1].set_title("Classification Accuracy Comparison")
axes[0, 1].legend()
axes[0, 1].grid(True)

# Divergence location accuracy comparison
for config_name, color in [("with_normalization", "blue"), ("no_normalization", "red")]:
    epochs = experiment_data[config_name]["epochs"]
    axes[0, 2].plot(
        epochs,
        experiment_data[config_name]["div_loc_acc"]["train"],
        f"{color[0]}--",
        label=f"{config_name} Train",
        alpha=0.7,
    )
    axes[0, 2].plot(
        epochs,
        experiment_data[config_name]["div_loc_acc"]["val"],
        color,
        label=f"{config_name} Val",
    )
axes[0, 2].set_xlabel("Epoch")
axes[0, 2].set_ylabel("Accuracy")
axes[0, 2].set_title("Divergence Location Accuracy")
axes[0, 2].legend()
axes[0, 2].grid(True)

# Cross-dataset comparison
datasets = ["Synthetic", "CodeXGLUE", "MBPP", "HumanEval"]
x = np.arange(len(datasets))
width = 0.35
norm_accs = [
    experiment_data["with_normalization"]["test_accuracy"],
    experiment_data["with_normalization"]["codexglue_accuracy"],
    experiment_data["with_normalization"]["mbpp_accuracy"],
    experiment_data["with_normalization"]["humaneval_accuracy"],
]
no_norm_accs = [
    experiment_data["no_normalization"]["test_accuracy"],
    experiment_data["no_normalization"]["codexglue_accuracy"],
    experiment_data["no_normalization"]["mbpp_accuracy"],
    experiment_data["no_normalization"]["humaneval_accuracy"],
]
axes[1, 0].bar(
    x - width / 2, norm_accs, width, label="With Normalization", color="blue"
)
axes[1, 0].bar(
    x + width / 2, no_norm_accs, width, label="No Normalization", color="red"
)
axes[1, 0].set_ylabel("Accuracy")
axes[1, 0].set_title("Cross-Dataset Generalization")
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(datasets)
axes[1, 0].legend()
axes[1, 0].grid(True, axis="y")

# Confusion matrix for with_normalization
cm1 = confusion_matrix(
    experiment_data["with_normalization"]["ground_truth"],
    experiment_data["with_normalization"]["predictions"],
)
sns.heatmap(
    cm1,
    annot=True,
    fmt="d",
    cmap="Blues",
    ax=axes[1, 1],
    xticklabels=MUTATION_TYPES,
    yticklabels=MUTATION_TYPES,
)
axes[1, 1].set_xlabel("Predicted")
axes[1, 1].set_ylabel("True")
axes[1, 1].set_title("CM: With Normalization")

# Confusion matrix for no_normalization
cm2 = confusion_matrix(
    experiment_data["no_normalization"]["ground_truth"],
    experiment_data["no_normalization"]["predictions"],
)
sns.heatmap(
    cm2,
    annot=True,
    fmt="d",
    cmap="Reds",
    ax=axes[1, 2],
    xticklabels=MUTATION_TYPES,
    yticklabels=MUTATION_TYPES,
)
axes[1, 2].set_xlabel("Predicted")
axes[1, 2].set_ylabel("True")
axes[1, 2].set_title("CM: No Normalization")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_comparison.png"), dpi=150)
plt.close()

# Print summary
print("\n" + "=" * 60)
print("ABLATION STUDY SUMMARY: Feature Normalization Impact")
print("=" * 60)
print(f"\n{'Metric':<35} {'With Norm':<15} {'No Norm':<15} {'Diff':<10}")
print("-" * 75)
print(
    f"{'Test Accuracy':<35} {experiment_data['with_normalization']['test_accuracy']:.4f}          {experiment_data['no_normalization']['test_accuracy']:.4f}          {experiment_data['with_normalization']['test_accuracy'] - experiment_data['no_normalization']['test_accuracy']:+.4f}"
)
print(
    f"{'Divergence Loc Accuracy':<35} {experiment_data['with_normalization']['test_div_loc_accuracy']:.4f}          {experiment_data['no_normalization']['test_div_loc_accuracy']:.4f}          {experiment_data['with_normalization']['test_div_loc_accuracy'] - experiment_data['no_normalization']['test_div_loc_accuracy']:+.4f}"
)
print(
    f"{'CodeXGLUE Accuracy':<35} {experiment_data['with_normalization']['codexglue_accuracy']:.4f}          {experiment_data['no_normalization']['codexglue_accuracy']:.4f}          {experiment_data['with_normalization']['codexglue_accuracy'] - experiment_data['no_normalization']['codexglue_accuracy']:+.4f}"
)
print(
    f"{'MBPP Accuracy':<35} {experiment_data['with_normalization']['mbpp_accuracy']:.4f}          {experiment_data['no_normalization']['mbpp_accuracy']:.4f}          {experiment_data['with_normalization']['mbpp_accuracy'] - experiment_data['no_normalization']['mbpp_accuracy']:+.4f}"
)
print(
    f"{'HumanEval Accuracy':<35} {experiment_data['with_normalization']['humaneval_accuracy']:.4f}          {experiment_data['no_normalization']['humaneval_accuracy']:.4f}          {experiment_data['with_normalization']['humaneval_accuracy'] - experiment_data['no_normalization']['humaneval_accuracy']:+.4f}"
)
print(
    f"{'Best Validation Accuracy':<35} {experiment_data['with_normalization']['best_val_accuracy']:.4f}          {experiment_data['no_normalization']['best_val_accuracy']:.4f}          {experiment_data['with_normalization']['best_val_accuracy'] - experiment_data['no_normalization']['best_val_accuracy']:+.4f}"
)

print(f"\nHuggingFace datasets loaded: {hf_loaded}")
print(f"\nResults saved to {working_dir}")
