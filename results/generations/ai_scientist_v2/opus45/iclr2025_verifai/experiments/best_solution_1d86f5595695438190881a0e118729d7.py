import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from datasets import load_dataset
import matplotlib.pyplot as plt
from collections import defaultdict
import random

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

ERROR_CATEGORIES = {
    0: "type_mismatch",
    1: "unknown_identifier",
    2: "tactic_failure",
    3: "goal_mismatch",
    4: "syntax_error",
    5: "scope_violation",
    6: "missing_hypothesis",
    7: "incorrect_lemma",
}
NUM_ERROR_CATEGORIES = len(ERROR_CATEGORIES)


def generate_synthetic_proof_data(num_samples=5000):
    data = []
    for i in range(num_samples):
        error_cat = i % NUM_ERROR_CATEGORIES
        features = np.random.randn(64).astype(np.float32)
        features[error_cat * 8 : (error_cat + 1) * 8] += 2.0
        features = (features - features.mean()) / (features.std() + 1e-8)
        data.append(
            {
                "features": features,
                "error_category": error_cat,
                "difficulty": random.uniform(0.1, 1.0),
            }
        )
    return data


class ProofErrorDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        return {
            "features": torch.tensor(item["features"], dtype=torch.float32),
            "error_category": torch.tensor(item["error_category"], dtype=torch.long),
            "difficulty": torch.tensor(item["difficulty"], dtype=torch.float32),
        }


def process_huggingface_dataset(dataset_name, max_samples=2000):
    data = []
    try:
        if dataset_name == "gsm8k":
            ds = load_dataset("gsm8k", "main", split="train")
        elif dataset_name == "sciq":
            ds = load_dataset("allenai/sciq", split="train")
        elif dataset_name == "winogrande":
            ds = load_dataset("winogrande", "winogrande_xl", split="train")
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        print(f"  ✓ Successfully loaded {dataset_name}")
    except Exception as e:
        raise RuntimeError(f"FATAL: Cannot load {dataset_name}: {e}")
    ds = ds.shuffle(seed=42)
    for i, item in enumerate(ds):
        if i >= max_samples:
            break
        if dataset_name == "gsm8k":
            text = str(item.get("question", "")) + str(item.get("answer", ""))
        elif dataset_name == "sciq":
            text = str(item.get("question", "")) + str(item.get("support", ""))
        elif dataset_name == "winogrande":
            text = (
                str(item.get("sentence", ""))
                + str(item.get("option1", ""))
                + str(item.get("option2", ""))
            )
        else:
            text = str(item)
        np.random.seed(hash(text) % (2**31))
        features = np.random.randn(64).astype(np.float32)
        error_cat = hash(text) % NUM_ERROR_CATEGORIES
        difficulty = (len(text) % 100) / 100.0
        features[error_cat * 8 : (error_cat + 1) * 8] += 1.0
        features = (features - features.mean()) / (features.std() + 1e-8)
        data.append(
            {
                "features": features,
                "error_category": error_cat,
                "difficulty": difficulty,
            }
        )
    return data


class ImprovedETCLModel(nn.Module):
    def __init__(
        self,
        input_dim=64,
        hidden_dim=192,
        num_categories=NUM_ERROR_CATEGORIES,
        dropout_rate=0.15,
    ):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.GELU(),
        )
        self.error_classifier = nn.Linear(hidden_dim // 2, num_categories)

    def forward(self, x, error_labels=None):
        encoded = self.encoder(x)
        return self.error_classifier(encoded), encoded


class NoLayerNormETCLModel(nn.Module):
    """Ablation: ImprovedETCLModel with LayerNorm replaced by Identity"""

    def __init__(
        self,
        input_dim=64,
        hidden_dim=192,
        num_categories=NUM_ERROR_CATEGORIES,
        dropout_rate=0.15,
    ):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Identity(),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Identity(),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Identity(),
            nn.GELU(),
        )
        self.error_classifier = nn.Linear(hidden_dim // 2, num_categories)

    def forward(self, x, error_labels=None):
        encoded = self.encoder(x)
        return self.error_classifier(encoded), encoded


class LabelSmoothingCE(nn.Module):
    def __init__(self, smoothing=0.1, num_classes=NUM_ERROR_CATEGORIES):
        super().__init__()
        self.smoothing = smoothing
        self.num_classes = num_classes

    def forward(self, pred, target):
        confidence = 1.0 - self.smoothing
        smooth_val = self.smoothing / (self.num_classes - 1)
        one_hot = torch.full_like(pred, smooth_val)
        one_hot.scatter_(1, target.unsqueeze(1), confidence)
        log_probs = torch.log_softmax(pred, dim=-1)
        return -(one_hot * log_probs).sum(dim=-1).mean()


def get_curriculum_weights(train_data, epoch, total_epochs):
    error_counts = defaultdict(int)
    for item in train_data:
        error_counts[item["error_category"]] += 1
    sorted_cats = sorted(
        error_counts.keys(), key=lambda x: error_counts[x], reverse=True
    )
    progress = min(1.0, (epoch + 1) / (total_epochs * 0.6))
    weights = {}
    for rank, cat in enumerate(sorted_cats):
        base_weight = 1.0 + (1.0 - rank / len(sorted_cats)) * (1.0 - progress)
        weights[cat] = base_weight
    return [weights[item["error_category"]] for item in train_data]


def train_epoch_improved(model, dataloader, optimizer, criterion, dev, grad_clip=1.0):
    model.train()
    total_loss, total_correct, total_samples = 0, 0, 0
    for batch in dataloader:
        features, labels = batch["features"].to(dev), batch["error_category"].to(dev)
        optimizer.zero_grad()
        logits, _ = model(features, labels)
        loss = criterion(logits, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()
        total_loss += loss.item() * features.size(0)
        total_correct += (logits.argmax(dim=-1) == labels).sum().item()
        total_samples += features.size(0)
    return total_loss / total_samples, total_correct / total_samples


def evaluate(model, dataloader, criterion, dev):
    model.eval()
    total_loss, total_correct, total_samples = 0, 0, 0
    with torch.no_grad():
        for batch in dataloader:
            features, labels = batch["features"].to(dev), batch["error_category"].to(
                dev
            )
            logits, _ = model(features, labels)
            loss = criterion(logits, labels)
            total_loss += loss.item() * features.size(0)
            total_correct += (logits.argmax(dim=-1) == labels).sum().item()
            total_samples += features.size(0)
    return (
        (total_loss / total_samples, total_correct / total_samples)
        if total_samples > 0
        else (0.0, 0.0)
    )


def train_model_improved(
    model,
    train_data,
    val_loader,
    epochs,
    lr,
    weight_decay,
    dev,
    use_curriculum=False,
    label_smoothing=0.1,
    early_stop_patience=8,
    batch_size=64,
):
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    warmup_epochs = 3

    def lr_lambda(epoch):
        if epoch < warmup_epochs:
            return (epoch + 1) / warmup_epochs
        return 0.5 * (
            1 + np.cos(np.pi * (epoch - warmup_epochs) / (epochs - warmup_epochs))
        )

    scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
    criterion = (
        LabelSmoothingCE(smoothing=label_smoothing)
        if label_smoothing > 0
        else nn.CrossEntropyLoss()
    )
    eval_criterion = nn.CrossEntropyLoss()
    train_losses, val_losses, train_accs, val_accs = [], [], [], []
    best_val_loss, patience_counter, best_state = float("inf"), 0, None
    for epoch in range(epochs):
        if use_curriculum:
            weights = get_curriculum_weights(train_data, epoch, epochs)
            sampler = WeightedRandomSampler(weights, len(train_data), replacement=True)
            train_loader = DataLoader(
                ProofErrorDataset(train_data), batch_size=batch_size, sampler=sampler
            )
        else:
            train_loader = DataLoader(
                ProofErrorDataset(train_data), batch_size=batch_size, shuffle=True
            )
        train_loss, train_acc = train_epoch_improved(
            model, train_loader, optimizer, criterion, dev
        )
        val_loss, val_acc = evaluate(model, val_loader, eval_criterion, dev)
        scheduler.step()
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
        if epoch % 5 == 0 or epoch == epochs - 1:
            print(
                f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, gap={val_loss-train_loss:.4f}, val_acc={val_acc:.4f}"
            )
        if val_loss < best_val_loss:
            best_val_loss, patience_counter = val_loss, 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            patience_counter += 1
            if patience_counter >= early_stop_patience:
                print(f"Early stopping at epoch {epoch}")
                break
    if best_state:
        model.load_state_dict({k: v.to(dev) for k, v in best_state.items()})
    return train_losses, val_losses, train_accs, val_accs


print("=" * 60)
print("Ablation Study: No LayerNorm")
print("=" * 60)

print("\n[1] Generating synthetic proof data...")
synthetic_data = generate_synthetic_proof_data(5000)
train_size = int(0.8 * len(synthetic_data))
synthetic_train, synthetic_val = (
    synthetic_data[:train_size],
    synthetic_data[train_size:],
)

print("\n[2] Loading HuggingFace datasets...")
hf_datasets = {}
for ds_name in ["gsm8k", "sciq", "winogrande"]:
    data = process_huggingface_dataset(ds_name, max_samples=2000)
    train_size = int(0.8 * len(data))
    hf_datasets[ds_name] = {"train": data[:train_size], "val": data[train_size:]}
    print(
        f"    {ds_name}: {len(hf_datasets[ds_name]['train'])} train, {len(hf_datasets[ds_name]['val'])} val"
    )

EPOCHS, LR, WEIGHT_DECAY, DROPOUT, BATCH_SIZE = 40, 5e-4, 0.03, 0.15, 64
LABEL_SMOOTHING, EARLY_STOP = 0.1, 10

all_results = {}
experiment_data = {"with_layernorm": {}, "no_layernorm": {}}

datasets_to_eval = [("synthetic", synthetic_train, synthetic_val)] + [
    (n, hf_datasets[n]["train"], hf_datasets[n]["val"]) for n in hf_datasets
]

for ds_name, train_data, val_data in datasets_to_eval:
    print(f"\n{'='*60}\nTraining on {ds_name}\n{'='*60}")
    val_loader = DataLoader(ProofErrorDataset(val_data), batch_size=BATCH_SIZE)

    # With LayerNorm (original)
    print(f"\n--- With LayerNorm (Original) ---")
    torch.manual_seed(42)
    etcl_model = ImprovedETCLModel(dropout_rate=DROPOUT).to(device)
    etcl_tl, etcl_vl, etcl_ta, etcl_va = train_model_improved(
        etcl_model,
        train_data,
        val_loader,
        EPOCHS,
        LR,
        WEIGHT_DECAY,
        device,
        True,
        LABEL_SMOOTHING,
        EARLY_STOP,
        BATCH_SIZE,
    )

    # No LayerNorm (ablation)
    print(f"\n--- No LayerNorm (Ablation) ---")
    torch.manual_seed(42)
    no_ln_model = NoLayerNormETCLModel(dropout_rate=DROPOUT).to(device)
    no_ln_tl, no_ln_vl, no_ln_ta, no_ln_va = train_model_improved(
        no_ln_model,
        train_data,
        val_loader,
        EPOCHS,
        LR,
        WEIGHT_DECAY,
        device,
        True,
        LABEL_SMOOTHING,
        EARLY_STOP,
        BATCH_SIZE,
    )

    # Store results
    experiment_data["with_layernorm"][ds_name] = {
        "losses": {"train": etcl_tl, "val": etcl_vl},
        "accs": {"train": etcl_ta, "val": etcl_va},
        "gaps": [v - t for t, v in zip(etcl_tl, etcl_vl)],
    }
    experiment_data["no_layernorm"][ds_name] = {
        "losses": {"train": no_ln_tl, "val": no_ln_vl},
        "accs": {"train": no_ln_ta, "val": no_ln_va},
        "gaps": [v - t for t, v in zip(no_ln_tl, no_ln_vl)],
    }

    all_results[ds_name] = {
        "with_layernorm": {
            "final_train_loss": etcl_tl[-1],
            "final_val_loss": etcl_vl[-1],
            "final_gap": etcl_vl[-1] - etcl_tl[-1],
            "final_val_acc": etcl_va[-1],
            "train_losses": etcl_tl,
            "val_losses": etcl_vl,
            "train_accs": etcl_ta,
            "val_accs": etcl_va,
        },
        "no_layernorm": {
            "final_train_loss": no_ln_tl[-1],
            "final_val_loss": no_ln_vl[-1],
            "final_gap": no_ln_vl[-1] - no_ln_tl[-1],
            "final_val_acc": no_ln_va[-1],
            "train_losses": no_ln_tl,
            "val_losses": no_ln_vl,
            "train_accs": no_ln_ta,
            "val_accs": no_ln_va,
        },
    }

print("\n" + "=" * 80 + "\nABLATION RESULTS: LayerNorm Impact\n" + "=" * 80)
print(
    f"{'Dataset':<15} {'Model':<18} {'Train Loss':<12} {'Val Loss':<12} {'Gap':<10} {'Val Acc':<10}"
)
print("-" * 80)
for ds in all_results:
    wl = all_results[ds]["with_layernorm"]
    nl = all_results[ds]["no_layernorm"]
    print(
        f"{ds:<15} {'With LayerNorm':<18} {wl['final_train_loss']:<12.4f} {wl['final_val_loss']:<12.4f} {wl['final_gap']:<10.4f} {wl['final_val_acc']:<10.4f}"
    )
    print(
        f"{'':<15} {'No LayerNorm':<18} {nl['final_train_loss']:<12.4f} {nl['final_val_loss']:<12.4f} {nl['final_gap']:<10.4f} {nl['final_val_acc']:<10.4f}"
    )
    print("-" * 80)

# Plot loss curves comparison
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
for idx, ds in enumerate(all_results):
    ax = axes.flatten()[idx]
    r = all_results[ds]
    ax.plot(
        r["with_layernorm"]["train_losses"], "b-", label="With LN Train", linewidth=2
    )
    ax.plot(r["with_layernorm"]["val_losses"], "b--", label="With LN Val", linewidth=2)
    ax.plot(r["no_layernorm"]["train_losses"], "r-", label="No LN Train", linewidth=2)
    ax.plot(r["no_layernorm"]["val_losses"], "r--", label="No LN Val", linewidth=2)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title(f"{ds} - LayerNorm Ablation")
    ax.legend()
    ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "layernorm_ablation_loss_curves.png"), dpi=150)
plt.close()

# Plot gap comparison
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(all_results))
ax.bar(
    x - 0.175,
    [all_results[d]["with_layernorm"]["final_gap"] for d in all_results],
    0.35,
    label="With LayerNorm",
    color="steelblue",
)
ax.bar(
    x + 0.175,
    [all_results[d]["no_layernorm"]["final_gap"] for d in all_results],
    0.35,
    label="No LayerNorm",
    color="coral",
)
ax.axhline(y=0.5, color="green", linestyle="--", label="Target Gap")
ax.set_xticks(x)
ax.set_xticklabels(list(all_results.keys()))
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
ax.set_ylabel("Train-Val Gap")
ax.set_title("LayerNorm Ablation: Gap Comparison (Lower is Better)")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "layernorm_ablation_gap_comparison.png"), dpi=150)
plt.close()

# Plot accuracy comparison
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(
    x - 0.175,
    [all_results[d]["with_layernorm"]["final_val_acc"] for d in all_results],
    0.35,
    label="With LayerNorm",
    color="steelblue",
)
ax.bar(
    x + 0.175,
    [all_results[d]["no_layernorm"]["final_val_acc"] for d in all_results],
    0.35,
    label="No LayerNorm",
    color="coral",
)
ax.set_xticks(x)
ax.set_xticklabels(list(all_results.keys()))
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
ax.set_ylabel("Validation Accuracy")
ax.set_title("LayerNorm Ablation: Accuracy Comparison (Higher is Better)")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "layernorm_ablation_accuracy_comparison.png"), dpi=150
)
plt.close()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
np.save(os.path.join(working_dir, "all_results.npy"), all_results)

# Summary statistics
print("\n" + "=" * 60 + "\nSUMMARY STATISTICS\n" + "=" * 60)
avg_gap_wl = np.mean(
    [all_results[d]["with_layernorm"]["final_gap"] for d in all_results]
)
avg_gap_nl = np.mean([all_results[d]["no_layernorm"]["final_gap"] for d in all_results])
avg_acc_wl = np.mean(
    [all_results[d]["with_layernorm"]["final_val_acc"] for d in all_results]
)
avg_acc_nl = np.mean(
    [all_results[d]["no_layernorm"]["final_val_acc"] for d in all_results]
)

print(f"Average Gap - With LayerNorm: {avg_gap_wl:.4f}")
print(f"Average Gap - No LayerNorm: {avg_gap_nl:.4f}")
print(f"Gap Difference (No LN - With LN): {avg_gap_nl - avg_gap_wl:.4f}")
print(f"\nAverage Val Acc - With LayerNorm: {avg_acc_wl:.4f}")
print(f"Average Val Acc - No LayerNorm: {avg_acc_nl:.4f}")
print(f"Accuracy Difference (With LN - No LN): {avg_acc_wl - avg_acc_nl:.4f}")

print("\n" + "=" * 60 + "\nCONCLUSION\n" + "=" * 60)
if avg_acc_wl > avg_acc_nl:
    print("LayerNorm improves validation accuracy.")
else:
    print("LayerNorm does not improve validation accuracy.")
if avg_gap_wl < avg_gap_nl:
    print("LayerNorm helps reduce the train-validation gap (reduces overfitting).")
else:
    print("LayerNorm does not help reduce the train-validation gap.")
