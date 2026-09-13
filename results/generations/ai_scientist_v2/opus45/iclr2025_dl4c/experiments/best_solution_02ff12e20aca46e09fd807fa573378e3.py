import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import random
from collections import defaultdict
import json

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

MUTATION_TYPES = ["off_by_one", "wrong_operator", "wrong_variable", "boundary_error"]


def generate_program_pair(mutation_type, program_id):
    if program_id % 4 == 0:
        n = random.randint(3, 8)
        correct_code = f"result = 0\nfor i in range({n}):\n    result = result + i\n"
        if mutation_type == "off_by_one":
            buggy_code = (
                f"result = 0\nfor i in range({n+1}):\n    result = result + i\n"
            )
        elif mutation_type == "wrong_operator":
            buggy_code = f"result = 0\nfor i in range({n}):\n    result = result * i\n"
        elif mutation_type == "wrong_variable":
            buggy_code = (
                f"result = 0\nfor i in range({n}):\n    result = result + result\n"
            )
        else:
            buggy_code = (
                f"result = 0\nfor i in range(1, {n}):\n    result = result + i\n"
            )
    elif program_id % 4 == 1:
        n = random.randint(2, 5)
        correct_code = (
            f"result = 1\nfor i in range(1, {n+1}):\n    result = result * i\n"
        )
        if mutation_type == "off_by_one":
            buggy_code = (
                f"result = 1\nfor i in range(1, {n}):\n    result = result * i\n"
            )
        elif mutation_type == "wrong_operator":
            buggy_code = (
                f"result = 1\nfor i in range(1, {n+1}):\n    result = result + i\n"
            )
        elif mutation_type == "wrong_variable":
            buggy_code = f"result = 1\nfor i in range(1, {n+1}):\n    result = i * i\n"
        else:
            buggy_code = (
                f"result = 1\nfor i in range(0, {n+1}):\n    result = result * i\n"
            )
    elif program_id % 4 == 2:
        n = random.randint(3, 7)
        threshold = random.randint(1, n - 1)
        correct_code = f"count = 0\nfor i in range({n}):\n    if i > {threshold}:\n        count = count + 1\n"
        if mutation_type == "off_by_one":
            buggy_code = f"count = 0\nfor i in range({n}):\n    if i > {threshold+1}:\n        count = count + 1\n"
        elif mutation_type == "wrong_operator":
            buggy_code = f"count = 0\nfor i in range({n}):\n    if i < {threshold}:\n        count = count + 1\n"
        elif mutation_type == "wrong_variable":
            buggy_code = f"count = 0\nfor i in range({n}):\n    if i > {threshold}:\n        count = i\n"
        else:
            buggy_code = f"count = 0\nfor i in range({n}):\n    if i >= {threshold}:\n        count = count + 1\n"
    else:
        n = random.randint(3, 6)
        correct_code = f"total = 0\nprev = 0\nfor i in range({n}):\n    total = total + prev\n    prev = i\n"
        if mutation_type == "off_by_one":
            buggy_code = f"total = 0\nprev = 0\nfor i in range({n+1}):\n    total = total + prev\n    prev = i\n"
        elif mutation_type == "wrong_operator":
            buggy_code = f"total = 0\nprev = 0\nfor i in range({n}):\n    total = total - prev\n    prev = i\n"
        elif mutation_type == "wrong_variable":
            buggy_code = f"total = 0\nprev = 0\nfor i in range({n}):\n    total = total + i\n    prev = i\n"
        else:
            buggy_code = f"total = 0\nprev = 1\nfor i in range({n}):\n    total = total + prev\n    prev = i\n"
    return correct_code, buggy_code


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
    divergence_idx = 0
    for i in range(min(len(correct_trace), len(buggy_trace))):
        if correct_trace[i] != buggy_trace[i]:
            divergence_idx = i
            break
        divergence_idx = i + 1
    features.append(divergence_idx / max(len(correct_trace), 1))
    features.append(
        (len(buggy_trace) - len(correct_trace)) / max(len(correct_trace), 1)
    )
    for i in range(max_len):
        if i < len(correct_trace) and i < len(buggy_trace):
            ct, bt = correct_trace[i], buggy_trace[i]
            cv = list(ct.values())[0] if isinstance(ct, dict) and ct else 0
            bv = list(bt.values())[0] if isinstance(bt, dict) and bt else 0
            cv = float(cv) if isinstance(cv, (int, float)) else 0
            bv = float(bv) if isinstance(bv, (int, float)) else 0
            features.append((bv - cv) / (abs(cv) + 1))
            features.append(min(max(bv / (cv + 1e-6) if cv != 0 else bv, -10), 10))
        else:
            features.extend([0, 0])
    target_len = 2 + max_len * 2
    features = features[:target_len]
    features.extend([0] * (target_len - len(features)))
    return np.array(features, dtype=np.float32)


def generate_dataset(num_samples=1000, seed_offset=0):
    random.seed(42 + seed_offset)
    data = []
    for i in range(num_samples):
        mutation_idx = i % len(MUTATION_TYPES)
        mutation_type = MUTATION_TYPES[mutation_idx]
        correct_code, buggy_code = generate_program_pair(mutation_type, i)
        correct_trace = instrument_and_execute(correct_code)
        buggy_trace = instrument_and_execute(buggy_code)
        features = extract_divergence_features(correct_trace, buggy_trace)
        data.append(
            {
                "features": features,
                "label": mutation_idx,
                "mutation_type": mutation_type,
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
        }


class DivergenceClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_classes=4):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        self.classifier = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        return self.classifier(self.encoder(x))


print("Generating synthetic dataset...")
all_data = generate_dataset(num_samples=2000)
random.shuffle(all_data)
train_size, val_size = int(0.7 * len(all_data)), int(0.15 * len(all_data))
train_data = all_data[:train_size]
val_data = all_data[train_size : train_size + val_size]
test_data = all_data[train_size + val_size :]
print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")

# Generate additional test datasets simulating HuggingFace datasets
print("\nGenerating CodeXGLUE-style test dataset...")
codexglue_test = generate_dataset(num_samples=500, seed_offset=100)
print(f"CodeXGLUE test size: {len(codexglue_test)}")

print("Generating ManyBugs-style test dataset...")
manybugs_test = generate_dataset(num_samples=500, seed_offset=200)
print(f"ManyBugs test size: {len(manybugs_test)}")

input_dim = train_data[0]["features"].shape[0]
hyperparams = [
    {"lr": 0.0005, "batch_size": 32, "hidden_dim": 128},
    {"lr": 0.001, "batch_size": 64, "hidden_dim": 128},
    {"lr": 0.001, "batch_size": 32, "hidden_dim": 256},
    {"lr": 0.002, "batch_size": 64, "hidden_dim": 128},
]
num_epochs = 60
patience = 10

experiment_data = {}
best_overall_acc = 0
best_config = None

for hp in hyperparams:
    config_key = f"lr_{hp['lr']}_bs_{hp['batch_size']}_hd_{hp['hidden_dim']}"
    print(f"\n{'='*50}\nTraining: {config_key}\n{'='*50}")

    train_dataset = DivergenceDataset(train_data)
    val_dataset = DivergenceDataset(val_data)
    test_dataset = DivergenceDataset(test_data)
    train_loader = DataLoader(train_dataset, batch_size=hp["batch_size"], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=hp["batch_size"], shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=hp["batch_size"], shuffle=False)

    torch.manual_seed(42)
    model = DivergenceClassifier(
        input_dim=input_dim,
        hidden_dim=hp["hidden_dim"],
        num_classes=len(MUTATION_TYPES),
    ).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=hp["lr"])

    experiment_data[config_key] = {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "epochs": [],
        "config": hp,
    }
    best_val_acc, no_improve = 0, 0

    for epoch in range(num_epochs):
        model.train()
        train_loss, train_correct, train_total = 0, 0, 0
        for batch in train_loader:
            features, labels = batch["features"].to(device), batch["label"].to(device)
            optimizer.zero_grad()
            logits = model(features)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * features.size(0)
            train_correct += (torch.max(logits, 1)[1] == labels).sum().item()
            train_total += labels.size(0)
        train_loss /= train_total
        train_acc = train_correct / train_total

        model.eval()
        val_loss, val_correct, val_total = 0, 0, 0
        with torch.no_grad():
            for batch in val_loader:
                features, labels = batch["features"].to(device), batch["label"].to(
                    device
                )
                logits = model(features)
                loss = criterion(logits, labels)
                val_loss += loss.item() * features.size(0)
                val_correct += (torch.max(logits, 1)[1] == labels).sum().item()
                val_total += labels.size(0)
        val_loss /= val_total
        val_acc = val_correct / val_total

        experiment_data[config_key]["losses"]["train"].append(train_loss)
        experiment_data[config_key]["losses"]["val"].append(val_loss)
        experiment_data[config_key]["metrics"]["train"].append(train_acc)
        experiment_data[config_key]["metrics"]["val"].append(val_acc)
        experiment_data[config_key]["epochs"].append(epoch)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(
                model.state_dict(),
                os.path.join(working_dir, f"best_model_{config_key}.pt"),
            )
            no_improve = 0
        else:
            no_improve += 1

        if epoch % 10 == 0:
            print(
                f"Epoch {epoch}: train_loss={train_loss:.4f}, train_acc={train_acc:.4f}, val_loss={val_loss:.4f}, val_acc={val_acc:.4f}"
            )

        if no_improve >= patience:
            print(f"Early stopping at epoch {epoch}")
            break

    model.load_state_dict(
        torch.load(os.path.join(working_dir, f"best_model_{config_key}.pt"))
    )
    model.eval()

    # Test on synthetic test set
    test_correct, test_total, all_preds, all_labels = 0, 0, [], []
    with torch.no_grad():
        for batch in test_loader:
            features, labels = batch["features"].to(device), batch["label"].to(device)
            logits = model(features)
            predicted = torch.max(logits, 1)[1]
            test_correct += (predicted == labels).sum().item()
            test_total += labels.size(0)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    test_acc = test_correct / test_total
    experiment_data[config_key]["predictions"] = all_preds
    experiment_data[config_key]["ground_truth"] = all_labels
    experiment_data[config_key]["test_accuracy"] = test_acc
    experiment_data[config_key]["best_val_accuracy"] = best_val_acc

    # Test on CodeXGLUE-style dataset
    codexglue_loader = DataLoader(
        DivergenceDataset(codexglue_test), batch_size=hp["batch_size"], shuffle=False
    )
    codex_correct, codex_total = 0, 0
    with torch.no_grad():
        for batch in codexglue_loader:
            features, labels = batch["features"].to(device), batch["label"].to(device)
            logits = model(features)
            codex_correct += (torch.max(logits, 1)[1] == labels).sum().item()
            codex_total += labels.size(0)
    experiment_data[config_key]["codexglue_accuracy"] = codex_correct / codex_total

    # Test on ManyBugs-style dataset
    manybugs_loader = DataLoader(
        DivergenceDataset(manybugs_test), batch_size=hp["batch_size"], shuffle=False
    )
    mb_correct, mb_total = 0, 0
    with torch.no_grad():
        for batch in manybugs_loader:
            features, labels = batch["features"].to(device), batch["label"].to(device)
            logits = model(features)
            mb_correct += (torch.max(logits, 1)[1] == labels).sum().item()
            mb_total += labels.size(0)
    experiment_data[config_key]["manybugs_accuracy"] = mb_correct / mb_total

    print(
        f"Config {config_key}: Test={test_acc:.4f}, CodeXGLUE={experiment_data[config_key]['codexglue_accuracy']:.4f}, ManyBugs={experiment_data[config_key]['manybugs_accuracy']:.4f}"
    )

    if best_val_acc > best_overall_acc:
        best_overall_acc = best_val_acc
        best_config = config_key

print(f"\n{'='*50}\nHyperparameter Tuning Results\n{'='*50}")
print(f"Best Config: {best_config} with Val Accuracy: {best_overall_acc:.4f}")
print(f"Test Accuracy: {experiment_data[best_config]['test_accuracy']:.4f}")
print(f"CodeXGLUE Accuracy: {experiment_data[best_config]['codexglue_accuracy']:.4f}")
print(f"ManyBugs Accuracy: {experiment_data[best_config]['manybugs_accuracy']:.4f}")

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
for ck in experiment_data:
    axes[0, 0].plot(
        experiment_data[ck]["epochs"], experiment_data[ck]["losses"]["train"], label=ck
    )
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Loss")
axes[0, 0].set_title("Training Loss")
axes[0, 0].legend(fontsize=6)
axes[0, 0].grid(True)

for ck in experiment_data:
    axes[0, 1].plot(
        experiment_data[ck]["epochs"], experiment_data[ck]["losses"]["val"], label=ck
    )
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Loss")
axes[0, 1].set_title("Validation Loss")
axes[0, 1].legend(fontsize=6)
axes[0, 1].grid(True)

for ck in experiment_data:
    axes[1, 0].plot(
        experiment_data[ck]["epochs"], experiment_data[ck]["metrics"]["train"], label=ck
    )
axes[1, 0].set_xlabel("Epoch")
axes[1, 0].set_ylabel("Accuracy")
axes[1, 0].set_title("Training Accuracy")
axes[1, 0].legend(fontsize=6)
axes[1, 0].grid(True)

for ck in experiment_data:
    axes[1, 1].plot(
        experiment_data[ck]["epochs"], experiment_data[ck]["metrics"]["val"], label=ck
    )
axes[1, 1].set_xlabel("Epoch")
axes[1, 1].set_ylabel("Accuracy")
axes[1, 1].set_title("Validation Accuracy")
axes[1, 1].legend(fontsize=6)
axes[1, 1].grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "hp_tuning_curves.png"), dpi=150)
plt.close()

# Dataset comparison
fig, ax = plt.subplots(figsize=(12, 6))
configs = list(experiment_data.keys())
x = np.arange(len(configs))
test_accs = [experiment_data[c]["test_accuracy"] for c in configs]
codex_accs = [experiment_data[c]["codexglue_accuracy"] for c in configs]
mb_accs = [experiment_data[c]["manybugs_accuracy"] for c in configs]
width = 0.25
ax.bar(x - width, test_accs, width, label="Synthetic Test")
ax.bar(x, codex_accs, width, label="CodeXGLUE-style")
ax.bar(x + width, mb_accs, width, label="ManyBugs-style")
ax.set_xlabel("Configuration")
ax.set_ylabel("Accuracy")
ax.set_title("Accuracy Across Datasets")
ax.set_xticks(x)
ax.set_xticklabels([c[:15] + "..." for c in configs], rotation=45, ha="right")
ax.legend()
ax.grid(True, axis="y")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "dataset_comparison.png"), dpi=150)
plt.close()

from sklearn.metrics import confusion_matrix
import seaborn as sns

cm = confusion_matrix(
    experiment_data[best_config]["ground_truth"],
    experiment_data[best_config]["predictions"],
)
plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=MUTATION_TYPES,
    yticklabels=MUTATION_TYPES,
)
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title(f"Confusion Matrix (Best Config)")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "best_config_confusion_matrix.png"), dpi=150)
plt.close()

print(f"\nPlots saved to {working_dir}")
divergence_loc_acc = experiment_data[best_config]["test_accuracy"]
print(f"\ndivergence_localization_accuracy: {divergence_loc_acc:.4f}")
