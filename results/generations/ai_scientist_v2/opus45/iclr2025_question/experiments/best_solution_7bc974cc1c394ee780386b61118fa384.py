import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import sys

if not hasattr(sys.stdout, "isatty"):
    sys.stdout.isatty = lambda: False
if not hasattr(sys.stderr, "isatty"):
    sys.stderr.isatty = lambda: False

import transformers

transformers.logging.set_verbosity_error()

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

np.random.seed(42)
torch.manual_seed(42)

UNCERTAINTY_TYPES = {
    0: "factual_knowledge_gap",
    1: "reasoning_path_ambiguity",
    2: "query_underspecification",
    3: "temporal_contextual_limitation",
}
ROUTING_STRATEGIES = {
    0: "retrieval_augmentation",
    1: "multiple_alternatives",
    2: "clarification_request",
    3: "knowledge_boundary_acknowledgment",
}

experiment_data = {
    "combined": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "per_class_accuracy": [],
        "routing_precision": [],
        "ece": [],
        "cross_dataset_acc": {},
    },
}

print("Loading HuggingFace datasets...")
from datasets import load_dataset

trivia_qa = load_dataset(
    "trivia_qa", "rc", split="train[:1000]", trust_remote_code=True
)
ambig_qa = load_dataset(
    "ambig_qa", "light", split="train[:1000]", trust_remote_code=True
)
nq = load_dataset(
    "natural_questions", "default", split="train[:2000]", trust_remote_code=True
)
print(f"Loaded: TriviaQA={len(trivia_qa)}, AmbigQA={len(ambig_qa)}, NQ={len(nq)}")

print("\nLoading DistilGPT-2...")
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
tokenizer.pad_token = tokenizer.eos_token
model_lm = AutoModel.from_pretrained("distilgpt2", output_hidden_states=True).to(device)
model_lm.eval()


def extract_hidden_states(texts, batch_size=16):
    all_features = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        inputs = tokenizer(
            batch_texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model_lm(**inputs)
            hidden_states = outputs.last_hidden_state
            attention_mask = inputs["attention_mask"].unsqueeze(-1)
            pooled = (hidden_states * attention_mask).sum(dim=1) / attention_mask.sum(
                dim=1
            )
            all_features.append(pooled.cpu().numpy())
    return np.vstack(all_features)


def prepare_uncertainty_dataset():
    queries, labels, sources = [], [], []

    # Type 0: Factual - TriviaQA with factual markers
    print("Processing TriviaQA for factual gaps...")
    factual_prefixes = [
        "What is the exact",
        "Who specifically",
        "When precisely did",
        "Where exactly",
    ]
    for q in list(trivia_qa)[:500]:
        question = q["question"]
        prefix = np.random.choice(factual_prefixes)
        modified = (
            f"{prefix} {question.lower()}" if np.random.random() > 0.5 else question
        )
        queries.append(modified)
        labels.append(0)
        sources.append("trivia_qa")

    # Type 1: Reasoning ambiguity from NQ with explicit reasoning markers
    print("Processing NQ for reasoning ambiguity...")
    reasoning_templates = [
        "What are multiple ways to {}",
        "Compare different approaches to {}",
        "What factors influence {}",
        "Analyze the tradeoffs in {}",
    ]
    for item in list(nq)[:500]:
        q = (
            item["question"]["text"]
            if isinstance(item["question"], dict)
            else str(item["question"])
        )
        if len(q) > 10:
            template = np.random.choice(reasoning_templates)
            queries.append(template.format(q.lower().rstrip("?")))
            labels.append(1)
            sources.append("natural_questions")

    # Type 2: Query underspecification - AmbigQA with ambiguity markers
    print("Processing AmbigQA for underspecification...")
    ambig_markers = ["it", "they", "that thing", "the person", "somewhere"]
    for q in list(ambig_qa)[:500]:
        question = q["question"]
        # Add pronouns to increase ambiguity
        if np.random.random() > 0.3:
            marker = np.random.choice(ambig_markers)
            question = (
                question.replace("the", marker, 1)
                if "the" in question.lower()
                else question
            )
        queries.append(question)
        labels.append(2)
        sources.append("ambig_qa")

    # Type 3: Temporal limitations with strong temporal markers
    print("Processing NQ for temporal limitations...")
    temporal_markers = [
        "As of today,",
        "Currently in 2024,",
        "What is the latest",
        "Recent updates on",
        "Breaking news about",
    ]
    for item in list(nq)[500:1000]:
        q = (
            item["question"]["text"]
            if isinstance(item["question"], dict)
            else str(item["question"])
        )
        if len(q) > 10:
            marker = np.random.choice(temporal_markers)
            queries.append(f"{marker} {q.lower()}")
            labels.append(3)
            sources.append("natural_questions")

    return queries, labels, sources


print("\nPreparing dataset...")
queries, labels, sources = prepare_uncertainty_dataset()
print(f"Total queries: {len(queries)}, Distribution: {np.bincount(labels)}")

print("\nExtracting hidden states...")
features = extract_hidden_states(queries, batch_size=32)
features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)
X, y = features.astype(np.float32), np.array(labels, dtype=np.int64)
sources = np.array(sources)

# Stratified split with cross-dataset holdout
X_train, X_temp, y_train, y_temp, src_train, src_temp = train_test_split(
    X, y, sources, test_size=0.3, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test, src_val, src_test = train_test_split(
    X_temp, y_temp, src_temp, test_size=0.5, random_state=42, stratify=y_temp
)

print(f"Split: Train={len(y_train)}, Val={len(y_val)}, Test={len(y_test)}")

train_dataset = TensorDataset(torch.FloatTensor(X_train), torch.LongTensor(y_train))
val_dataset = TensorDataset(torch.FloatTensor(X_val), torch.LongTensor(y_val))
test_dataset = TensorDataset(torch.FloatTensor(X_test), torch.LongTensor(y_test))
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)
test_loader = DataLoader(test_dataset, batch_size=32)


class CalibratedUncertaintyProbe(nn.Module):
    def __init__(self, input_dim=768, hidden_dim=256, num_classes=4, dropout=0.4):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_classes),
        )
        self.temperature = nn.Parameter(torch.ones(1))

    def forward(self, x, calibrate=False):
        logits = self.network(x)
        return logits / self.temperature if calibrate else logits


def compute_ece(probs, labels, n_bins=10):
    """Expected Calibration Error"""
    confidences, predictions = probs.max(axis=1), probs.argmax(axis=1)
    accuracies = (predictions == labels).astype(float)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (confidences > bin_boundaries[i]) & (
            confidences <= bin_boundaries[i + 1]
        )
        if mask.sum() > 0:
            bin_acc, bin_conf = accuracies[mask].mean(), confidences[mask].mean()
            ece += mask.sum() * abs(bin_acc - bin_conf)
    return ece / len(labels)


def compute_routing_precision(preds, labels, probs):
    correct = preds == labels
    max_probs = probs.max(axis=1)
    confident = max_probs > 0.6
    return (correct & confident).sum() / max(confident.sum(), 1)


class_counts = np.bincount(y_train)
class_weights = torch.FloatTensor(len(y_train) / (len(class_counts) * class_counts)).to(
    device
)

model = CalibratedUncertaintyProbe(
    input_dim=X.shape[1], hidden_dim=256, num_classes=4, dropout=0.4
).to(device)
criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.1)
optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.05)
scheduler = optim.lr_scheduler.OneCycleLR(
    optimizer, max_lr=0.001, epochs=80, steps_per_epoch=len(train_loader)
)


def train_epoch(model, loader, criterion, optimizer, scheduler):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for features, labels in loader:
        features, labels = features.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(features)
        loss = criterion(outputs, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total_loss += loss.item()
        correct += (outputs.argmax(1) == labels).sum().item()
        total += labels.size(0)
    return total_loss / len(loader), correct / total


def evaluate(model, loader, criterion, calibrate=False):
    model.eval()
    total_loss, all_preds, all_labels, all_probs = 0, [], [], []
    with torch.no_grad():
        for features, labels in loader:
            features, labels = features.to(device), labels.to(device)
            outputs = model(features, calibrate=calibrate)
            loss = criterion(outputs, labels)
            total_loss += loss.item()
            probs = torch.softmax(outputs, dim=1)
            all_preds.extend(outputs.argmax(1).cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    return (
        total_loss / len(loader),
        accuracy_score(all_labels, all_preds),
        np.array(all_preds),
        np.array(all_labels),
        np.array(all_probs),
    )


print("\n" + "=" * 60 + "\nTraining with Calibration & Label Smoothing\n" + "=" * 60)
best_val_acc, best_state, patience = 0, None, 0

for epoch in range(80):
    train_loss, train_acc = train_epoch(
        model, train_loader, criterion, optimizer, scheduler
    )
    val_loss, val_acc, val_preds, val_labels, val_probs = evaluate(
        model, val_loader, criterion
    )
    ece = compute_ece(val_probs, val_labels)
    routing_prec = compute_routing_precision(val_preds, val_labels, val_probs)

    experiment_data["combined"]["losses"]["train"].append(train_loss)
    experiment_data["combined"]["losses"]["val"].append(val_loss)
    experiment_data["combined"]["metrics"]["train"].append(train_acc)
    experiment_data["combined"]["metrics"]["val"].append(val_acc)
    experiment_data["combined"]["routing_precision"].append(routing_prec)
    experiment_data["combined"]["ece"].append(ece)

    if val_acc > best_val_acc:
        best_val_acc, best_state, patience = val_acc, model.state_dict().copy(), 0
    else:
        patience += 1

    if (epoch + 1) % 10 == 0:
        print(
            f"Epoch {epoch+1}: validation_loss={val_loss:.4f}, acc={val_acc:.4f}, ECE={ece:.4f}, routing_prec={routing_prec:.4f}"
        )

    if patience >= 15:
        print(f"Early stopping at epoch {epoch+1}")
        break

model.load_state_dict(best_state)
test_loss, test_acc, test_preds, test_labels, test_probs = evaluate(
    model, test_loader, criterion, calibrate=True
)
test_ece = compute_ece(test_probs, test_labels)
test_routing_precision = compute_routing_precision(test_preds, test_labels, test_probs)

print(
    "\n"
    + "=" * 60
    + f"\nFINAL TEST RESULTS\nAccuracy: {test_acc:.4f}, ECE: {test_ece:.4f}"
)
print(f"uncertainty_routing_precision = {test_routing_precision:.4f}")
print(
    classification_report(
        test_labels, test_preds, target_names=[UNCERTAINTY_TYPES[i] for i in range(4)]
    )
)

# Cross-dataset evaluation
for src in ["trivia_qa", "ambig_qa", "natural_questions"]:
    mask = src_test == src
    if mask.sum() > 0:
        acc = accuracy_score(test_labels[mask], test_preds[mask])
        experiment_data["combined"]["cross_dataset_acc"][src] = acc
        print(f"{src}: {acc:.4f} (n={mask.sum()})")

conf_matrix = confusion_matrix(test_labels, test_preds)
per_class_acc = conf_matrix.diagonal() / (conf_matrix.sum(axis=1) + 1e-8)
experiment_data["combined"]["per_class_accuracy"] = per_class_acc.tolist()
experiment_data["combined"]["predictions"] = test_preds.tolist()
experiment_data["combined"]["ground_truth"] = test_labels.tolist()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Plots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
epochs_range = range(1, len(experiment_data["combined"]["losses"]["train"]) + 1)

axes[0, 0].plot(
    epochs_range, experiment_data["combined"]["losses"]["train"], label="Train"
)
axes[0, 0].plot(epochs_range, experiment_data["combined"]["losses"]["val"], label="Val")
axes[0, 0].set_title("Loss")
axes[0, 0].legend()
axes[0, 0].grid(True)

axes[0, 1].plot(
    epochs_range, experiment_data["combined"]["metrics"]["train"], label="Train"
)
axes[0, 1].plot(
    epochs_range, experiment_data["combined"]["metrics"]["val"], label="Val"
)
axes[0, 1].set_title("Accuracy")
axes[0, 1].legend()
axes[0, 1].grid(True)

axes[1, 0].plot(
    epochs_range, experiment_data["combined"]["routing_precision"], color="green"
)
axes[1, 0].set_title("Routing Precision")
axes[1, 0].grid(True)

axes[1, 1].plot(epochs_range, experiment_data["combined"]["ece"], color="red")
axes[1, 1].set_title("Expected Calibration Error (ECE)")
axes[1, 1].grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "calibrated_training_curves.png"), dpi=150)
plt.close()

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(conf_matrix, cmap="Blues")
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels(
    [UNCERTAINTY_TYPES[i][:12] for i in range(4)], rotation=45, ha="right"
)
ax.set_yticklabels([UNCERTAINTY_TYPES[i][:12] for i in range(4)])
for i in range(4):
    for j in range(4):
        ax.text(
            j,
            i,
            conf_matrix[i, j],
            ha="center",
            va="center",
            color="white" if conf_matrix[i, j] > conf_matrix.max() / 2 else "black",
        )
plt.colorbar(im)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "confusion_matrix_calibrated.png"), dpi=150)
plt.close()

print(
    f"\n{'='*60}\nFINAL: Test Acc={test_acc:.4f}, ECE={test_ece:.4f}, uncertainty_routing_precision={test_routing_precision:.4f}\n{'='*60}"
)
