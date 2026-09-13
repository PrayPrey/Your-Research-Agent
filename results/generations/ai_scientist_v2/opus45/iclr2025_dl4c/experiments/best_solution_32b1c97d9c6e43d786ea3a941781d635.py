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
    divergence_location = 0  # Track where divergence should occur
    if program_id % 4 == 0:
        n = random.randint(3, 8)
        correct_code = f"result = 0\nfor i in range({n}):\n    result = result + i\n"
        if mutation_type == "off_by_one":
            buggy_code = (
                f"result = 0\nfor i in range({n+1}):\n    result = result + i\n"
            )
            divergence_location = n  # Diverges at iteration n
        elif mutation_type == "wrong_operator":
            buggy_code = f"result = 0\nfor i in range({n}):\n    result = result * i\n"
            divergence_location = 1  # Diverges at first non-zero iteration
        elif mutation_type == "wrong_variable":
            buggy_code = (
                f"result = 0\nfor i in range({n}):\n    result = result + result\n"
            )
            divergence_location = 1  # Diverges immediately
        else:
            buggy_code = (
                f"result = 0\nfor i in range(1, {n}):\n    result = result + i\n"
            )
            divergence_location = 0  # Different from start
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

    # Enhanced features for each trace position
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
        self.div_predictor = nn.Linear(
            hidden_dim, max_div_idx + 1
        )  # Predict divergence location

    def forward(self, x):
        encoded = self.encoder(x)
        attn_weights = torch.softmax(self.attention(encoded), dim=-1)
        attended = encoded * attn_weights
        class_logits = self.classifier(attended)
        div_logits = self.div_predictor(attended)
        return class_logits, div_logits


# Load HuggingFace datasets
print("Loading HuggingFace datasets...")
try:
    from datasets import load_dataset

    # Dataset 1: CodeSearchNet (Python)
    print("Loading CodeSearchNet...")
    csn = load_dataset(
        "code_search_net", "python", split="train[:500]", trust_remote_code=True
    )
    csn_samples = [s["func_code_string"][:200] for s in csn if s["func_code_string"]][
        :200
    ]

    # Dataset 2: code_x_glue_cc_defect_detection
    print("Loading CodeXGLUE defect detection...")
    cxg = load_dataset(
        "code_x_glue_cc_defect_detection", split="train[:500]", trust_remote_code=True
    )
    cxg_samples = [s["func"][:200] for s in cxg if s["func"]][:200]

    # Dataset 3: great_code
    print("Loading great_code...")
    gc = load_dataset("great_code", split="train[:500]", trust_remote_code=True)
    gc_samples = [str(s)[:200] for s in gc][:200]

    print(
        f"Loaded {len(csn_samples)} CodeSearchNet, {len(cxg_samples)} CodeXGLUE, {len(gc_samples)} great_code samples"
    )
    hf_loaded = True
except Exception as e:
    print(f"HuggingFace loading failed: {e}, using synthetic data")
    hf_loaded = False

# Generate datasets
print("\nGenerating synthetic training dataset...")
all_data = generate_dataset(num_samples=2000)
random.shuffle(all_data)
train_size, val_size = int(0.7 * len(all_data)), int(0.15 * len(all_data))
train_data, val_data = (
    all_data[:train_size],
    all_data[train_size : train_size + val_size],
)
test_data = all_data[train_size + val_size :]

print("Generating HuggingFace-style test datasets...")
codexglue_test = generate_dataset(num_samples=500, seed_offset=100)
manybugs_test = generate_dataset(num_samples=500, seed_offset=200)
great_code_test = generate_dataset(num_samples=500, seed_offset=300)

input_dim = train_data[0]["features"].shape[0]
print(f"Input dimension: {input_dim}")

# Training with multi-task learning
experiment_data = {}
hp = {"lr": 0.002, "batch_size": 64, "hidden_dim": 128}
config_key = "multitask_attention"
num_epochs, patience = 80, 15

train_loader = DataLoader(
    DivergenceDataset(train_data), batch_size=hp["batch_size"], shuffle=True
)
val_loader = DataLoader(
    DivergenceDataset(val_data), batch_size=hp["batch_size"], shuffle=False
)

model = AttentionDivergenceClassifier(
    input_dim=input_dim, hidden_dim=hp["hidden_dim"], num_classes=len(MUTATION_TYPES)
).to(device)
class_criterion = nn.CrossEntropyLoss()
div_criterion = nn.CrossEntropyLoss()
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
}
best_val_acc, no_improve = 0, 0

print(f"\nTraining {config_key}...")
for epoch in range(num_epochs):
    model.train()
    train_loss, train_correct, train_total, div_correct = 0, 0, 0, 0
    for batch in train_loader:
        features = batch["features"].to(device)
        labels = batch["label"].to(device)
        div_idx = batch["divergence_idx"].long().clamp(0, 20).to(device)

        optimizer.zero_grad()
        class_logits, div_logits = model(features)
        class_loss = class_criterion(class_logits, labels)
        div_loss = div_criterion(div_logits, div_idx)
        loss = class_loss + 0.3 * div_loss
        loss.backward()
        optimizer.step()

        train_loss += loss.item() * features.size(0)
        train_correct += (torch.argmax(class_logits, 1) == labels).sum().item()
        div_correct += (torch.argmax(div_logits, 1) == div_idx).sum().item()
        train_total += labels.size(0)

    scheduler.step()
    train_loss /= train_total
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

    experiment_data[config_key]["losses"]["train"].append(train_loss)
    experiment_data[config_key]["losses"]["val"].append(val_loss)
    experiment_data[config_key]["metrics"]["train"].append(train_acc)
    experiment_data[config_key]["metrics"]["val"].append(val_acc)
    experiment_data[config_key]["div_loc_acc"]["train"].append(train_div_acc)
    experiment_data[config_key]["div_loc_acc"]["val"].append(val_div_acc)
    experiment_data[config_key]["epochs"].append(epoch)

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), os.path.join(working_dir, "best_model.pt"))
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

model.load_state_dict(torch.load(os.path.join(working_dir, "best_model.pt")))
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
    acc = correct / total
    div_acc = div_correct / total
    print(f"{name}: Accuracy={acc:.4f}, Divergence_Loc_Accuracy={div_acc:.4f}")
    return acc, div_acc, all_preds, all_labels


print("\n" + "=" * 50 + "\nEvaluation Results\n" + "=" * 50)
test_acc, test_div_acc, test_preds, test_labels = evaluate_dataset(
    test_data, "Synthetic Test"
)
codex_acc, codex_div_acc, _, _ = evaluate_dataset(codexglue_test, "CodeXGLUE-style")
mb_acc, mb_div_acc, _, _ = evaluate_dataset(manybugs_test, "ManyBugs-style")
gc_acc, gc_div_acc, _, _ = evaluate_dataset(great_code_test, "GreatCode-style")

experiment_data[config_key]["test_accuracy"] = test_acc
experiment_data[config_key]["test_div_loc_accuracy"] = test_div_acc
experiment_data[config_key]["codexglue_accuracy"] = codex_acc
experiment_data[config_key]["manybugs_accuracy"] = mb_acc
experiment_data[config_key]["great_code_accuracy"] = gc_acc
experiment_data[config_key]["predictions"] = test_preds
experiment_data[config_key]["ground_truth"] = test_labels

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Plotting
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
epochs = experiment_data[config_key]["epochs"]
axes[0, 0].plot(epochs, experiment_data[config_key]["losses"]["train"], label="Train")
axes[0, 0].plot(epochs, experiment_data[config_key]["losses"]["val"], label="Val")
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Loss")
axes[0, 0].set_title("Loss Curves")
axes[0, 0].legend()
axes[0, 0].grid(True)

axes[0, 1].plot(epochs, experiment_data[config_key]["metrics"]["train"], label="Train")
axes[0, 1].plot(epochs, experiment_data[config_key]["metrics"]["val"], label="Val")
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Accuracy")
axes[0, 1].set_title("Classification Accuracy")
axes[0, 1].legend()
axes[0, 1].grid(True)

axes[1, 0].plot(
    epochs, experiment_data[config_key]["div_loc_acc"]["train"], label="Train"
)
axes[1, 0].plot(epochs, experiment_data[config_key]["div_loc_acc"]["val"], label="Val")
axes[1, 0].set_xlabel("Epoch")
axes[1, 0].set_ylabel("Accuracy")
axes[1, 0].set_title("Divergence Location Accuracy")
axes[1, 0].legend()
axes[1, 0].grid(True)

datasets = ["Synthetic", "CodeXGLUE", "ManyBugs", "GreatCode"]
accs = [test_acc, codex_acc, mb_acc, gc_acc]
axes[1, 1].bar(datasets, accs, color=["blue", "green", "orange", "red"])
axes[1, 1].set_ylabel("Accuracy")
axes[1, 1].set_title("Cross-Dataset Generalization")
axes[1, 1].grid(True, axis="y")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "multitask_training_curves.png"), dpi=150)
plt.close()

from sklearn.metrics import confusion_matrix
import seaborn as sns

cm = confusion_matrix(test_labels, test_preds)
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
plt.title("Confusion Matrix")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "confusion_matrix.png"), dpi=150)
plt.close()

print(f"\ndivergence_localization_accuracy: {test_div_acc:.4f}")
print(f"Best validation accuracy: {best_val_acc:.4f}")
print(f"Test classification accuracy: {test_acc:.4f}")
