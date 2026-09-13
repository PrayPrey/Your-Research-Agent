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
    "with_attention_mask": {
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
    },
    "no_attention_mask": {
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


def extract_hidden_states(texts, batch_size=16, use_attention_mask=True):
    """Extract hidden states with or without attention mask weighted pooling"""
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
            if use_attention_mask:
                # Baseline: attention-mask-weighted mean pooling
                attention_mask = inputs["attention_mask"].unsqueeze(-1)
                pooled = (hidden_states * attention_mask).sum(
                    dim=1
                ) / attention_mask.sum(dim=1)
            else:
                # Ablation: simple mean pooling across all positions (including padding)
                pooled = hidden_states.mean(dim=1)
            all_features.append(pooled.cpu().numpy())
    return np.vstack(all_features)


def prepare_uncertainty_dataset():
    queries, labels, sources = [], [], []
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

    print("Processing AmbigQA for underspecification...")
    ambig_markers = ["it", "they", "that thing", "the person", "somewhere"]
    for q in list(ambig_qa)[:500]:
        question = q["question"]
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
    confidences, predictions = probs.max(axis=1), probs.argmax(axis=1)
    accuracies = (predictions == labels).astype(float)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (confidences > bin_boundaries[i]) & (
            confidences <= bin_boundaries[i + 1]
        )
        if mask.sum() > 0:
            ece += mask.sum() * abs(accuracies[mask].mean() - confidences[mask].mean())
    return ece / len(labels)


def compute_routing_precision(preds, labels, probs):
    correct = preds == labels
    confident = probs.max(axis=1) > 0.6
    return (correct & confident).sum() / max(confident.sum(), 1)


def train_epoch(model, loader, criterion, optimizer, scheduler):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for features, lbls in loader:
        features, lbls = features.to(device), lbls.to(device)
        optimizer.zero_grad()
        outputs = model(features)
        loss = criterion(outputs, lbls)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total_loss += loss.item()
        correct += (outputs.argmax(1) == lbls).sum().item()
        total += lbls.size(0)
    return total_loss / len(loader), correct / total


def evaluate(model, loader, criterion, calibrate=False):
    model.eval()
    total_loss, all_preds, all_labels, all_probs = 0, [], [], []
    with torch.no_grad():
        for features, lbls in loader:
            features, lbls = features.to(device), lbls.to(device)
            outputs = model(features, calibrate=calibrate)
            total_loss += criterion(outputs, lbls).item()
            probs = torch.softmax(outputs, dim=1)
            all_preds.extend(outputs.argmax(1).cpu().numpy())
            all_labels.extend(lbls.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    return (
        total_loss / len(loader),
        accuracy_score(all_labels, all_preds),
        np.array(all_preds),
        np.array(all_labels),
        np.array(all_probs),
    )


def run_experiment(ablation_name, use_attention_mask):
    print(
        f"\n{'='*60}\nRunning: {ablation_name} (use_attention_mask={use_attention_mask})\n{'='*60}"
    )

    np.random.seed(42)
    torch.manual_seed(42)

    print("Extracting hidden states...")
    features = extract_hidden_states(
        queries, batch_size=32, use_attention_mask=use_attention_mask
    )
    features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)
    X, y = features.astype(np.float32), np.array(labels, dtype=np.int64)
    src_arr = np.array(sources)

    X_train, X_temp, y_train, y_temp, src_train, src_temp = train_test_split(
        X, y, src_arr, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test, src_val, src_test = train_test_split(
        X_temp, y_temp, src_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    print(f"Split: Train={len(y_train)}, Val={len(y_val)}, Test={len(y_test)}")

    train_loader = DataLoader(
        TensorDataset(torch.FloatTensor(X_train), torch.LongTensor(y_train)),
        batch_size=32,
        shuffle=True,
    )
    val_loader = DataLoader(
        TensorDataset(torch.FloatTensor(X_val), torch.LongTensor(y_val)), batch_size=32
    )
    test_loader = DataLoader(
        TensorDataset(torch.FloatTensor(X_test), torch.LongTensor(y_test)),
        batch_size=32,
    )

    class_counts = np.bincount(y_train)
    class_weights = torch.FloatTensor(
        len(y_train) / (len(class_counts) * class_counts)
    ).to(device)

    model = CalibratedUncertaintyProbe(
        input_dim=X.shape[1], hidden_dim=256, num_classes=4, dropout=0.4
    ).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.05)
    scheduler = optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=0.001, epochs=80, steps_per_epoch=len(train_loader)
    )

    best_val_acc, best_state, patience = 0, None, 0
    exp_data = experiment_data[ablation_name]["combined"]

    for epoch in range(80):
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, scheduler
        )
        val_loss, val_acc, val_preds, val_labels, val_probs = evaluate(
            model, val_loader, criterion
        )
        ece = compute_ece(val_probs, val_labels)
        routing_prec = compute_routing_precision(val_preds, val_labels, val_probs)

        exp_data["losses"]["train"].append(train_loss)
        exp_data["losses"]["val"].append(val_loss)
        exp_data["metrics"]["train"].append(train_acc)
        exp_data["metrics"]["val"].append(val_acc)
        exp_data["routing_precision"].append(routing_prec)
        exp_data["ece"].append(ece)

        if val_acc > best_val_acc:
            best_val_acc, best_state, patience = val_acc, model.state_dict().copy(), 0
        else:
            patience += 1

        if (epoch + 1) % 10 == 0:
            print(
                f"Epoch {epoch+1}: val_loss={val_loss:.4f}, acc={val_acc:.4f}, ECE={ece:.4f}, routing_prec={routing_prec:.4f}"
            )

        if patience >= 15:
            print(f"Early stopping at epoch {epoch+1}")
            break

    model.load_state_dict(best_state)
    test_loss, test_acc, test_preds, test_labels_out, test_probs = evaluate(
        model, test_loader, criterion, calibrate=True
    )
    test_ece = compute_ece(test_probs, test_labels_out)
    test_routing_precision = compute_routing_precision(
        test_preds, test_labels_out, test_probs
    )

    print(f"\nFINAL TEST RESULTS for {ablation_name}:")
    print(
        f"Accuracy: {test_acc:.4f}, ECE: {test_ece:.4f}, Routing Precision: {test_routing_precision:.4f}"
    )
    print(
        classification_report(
            test_labels_out,
            test_preds,
            target_names=[UNCERTAINTY_TYPES[i] for i in range(4)],
        )
    )

    for src in ["trivia_qa", "ambig_qa", "natural_questions"]:
        mask = src_test == src
        if mask.sum() > 0:
            acc = accuracy_score(test_labels_out[mask], test_preds[mask])
            exp_data["cross_dataset_acc"][src] = acc
            print(f"{src}: {acc:.4f} (n={mask.sum()})")

    conf_matrix = confusion_matrix(test_labels_out, test_preds)
    exp_data["per_class_accuracy"] = (
        conf_matrix.diagonal() / (conf_matrix.sum(axis=1) + 1e-8)
    ).tolist()
    exp_data["predictions"] = test_preds.tolist()
    exp_data["ground_truth"] = test_labels_out.tolist()
    exp_data["final_test_acc"] = test_acc
    exp_data["final_ece"] = test_ece
    exp_data["final_routing_precision"] = test_routing_precision

    return test_acc, test_ece, test_routing_precision, conf_matrix


# Run both experiments
results = {}
results["with_attention_mask"] = run_experiment(
    "with_attention_mask", use_attention_mask=True
)
results["no_attention_mask"] = run_experiment(
    "no_attention_mask", use_attention_mask=False
)

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Comparison summary
print("\n" + "=" * 60)
print("ABLATION STUDY COMPARISON: Attention Mask Pooling")
print("=" * 60)
print(f"{'Method':<25} {'Accuracy':>10} {'ECE':>10} {'Routing Prec':>12}")
print("-" * 60)
for name, (acc, ece, rp, _) in results.items():
    print(f"{name:<25} {acc:>10.4f} {ece:>10.4f} {rp:>12.4f}")
print("-" * 60)

acc_diff = results["with_attention_mask"][0] - results["no_attention_mask"][0]
print(f"\nDifference (with_mask - no_mask): Accuracy={acc_diff:+.4f}")

# Create comparison plots
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

for idx, (ablation_name, color) in enumerate(
    [("with_attention_mask", "blue"), ("no_attention_mask", "orange")]
):
    exp_data = experiment_data[ablation_name]["combined"]
    epochs_range = range(1, len(exp_data["losses"]["train"]) + 1)

    axes[0, 0].plot(
        epochs_range,
        exp_data["losses"]["train"],
        color=color,
        linestyle="-",
        label=f"{ablation_name} train",
    )
    axes[0, 0].plot(
        epochs_range,
        exp_data["losses"]["val"],
        color=color,
        linestyle="--",
        label=f"{ablation_name} val",
    )

    axes[0, 1].plot(
        epochs_range,
        exp_data["metrics"]["train"],
        color=color,
        linestyle="-",
        label=f"{ablation_name} train",
    )
    axes[0, 1].plot(
        epochs_range,
        exp_data["metrics"]["val"],
        color=color,
        linestyle="--",
        label=f"{ablation_name} val",
    )

    axes[0, 2].plot(
        epochs_range, exp_data["routing_precision"], color=color, label=ablation_name
    )
    axes[1, 0].plot(epochs_range, exp_data["ece"], color=color, label=ablation_name)

axes[0, 0].set_title("Loss Curves")
axes[0, 0].legend(fontsize=8)
axes[0, 0].grid(True)
axes[0, 1].set_title("Accuracy Curves")
axes[0, 1].legend(fontsize=8)
axes[0, 1].grid(True)
axes[0, 2].set_title("Routing Precision")
axes[0, 2].legend()
axes[0, 2].grid(True)
axes[1, 0].set_title("Expected Calibration Error")
axes[1, 0].legend()
axes[1, 0].grid(True)

# Bar chart comparison
methods = list(results.keys())
test_accs = [results[m][0] for m in methods]
test_eces = [results[m][1] for m in methods]
x = np.arange(len(methods))
axes[1, 1].bar(x - 0.2, test_accs, 0.4, label="Accuracy", color="green")
axes[1, 1].bar(x + 0.2, [1 - e for e in test_eces], 0.4, label="1-ECE", color="red")
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(["With Mask", "No Mask"], rotation=15)
axes[1, 1].set_title("Final Test Metrics Comparison")
axes[1, 1].legend()
axes[1, 1].grid(True)

# Confusion matrix for no_attention_mask ablation
im = axes[1, 2].imshow(results["no_attention_mask"][3], cmap="Blues")
axes[1, 2].set_xticks(range(4))
axes[1, 2].set_yticks(range(4))
axes[1, 2].set_xticklabels(
    [UNCERTAINTY_TYPES[i][:10] for i in range(4)], rotation=45, ha="right"
)
axes[1, 2].set_yticklabels([UNCERTAINTY_TYPES[i][:10] for i in range(4)])
axes[1, 2].set_title("Confusion Matrix (No Attention Mask)")
for i in range(4):
    for j in range(4):
        val = results["no_attention_mask"][3][i, j]
        axes[1, 2].text(
            j,
            i,
            val,
            ha="center",
            va="center",
            color=(
                "white" if val > results["no_attention_mask"][3].max() / 2 else "black"
            ),
        )

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_comparison.png"), dpi=150)
plt.close()

print(f"\nPlots saved to {working_dir}/ablation_comparison.png")
print(f"Data saved to {working_dir}/experiment_data.npy")
