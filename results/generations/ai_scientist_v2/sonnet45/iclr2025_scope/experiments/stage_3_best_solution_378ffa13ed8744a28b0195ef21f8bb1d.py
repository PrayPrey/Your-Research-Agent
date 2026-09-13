import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from datasets import load_dataset
from collections import Counter

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)


# Synthetic dataset for text classification
class SyntheticTextDataset(Dataset):
    def __init__(self, num_samples=1000, seq_len=128, vocab_size=5000, num_classes=4):
        self.num_samples = num_samples
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.num_classes = num_classes
        torch.manual_seed(42)
        self.data = torch.randint(0, vocab_size, (num_samples, seq_len))
        self.labels = torch.sum(self.data[:, :10], dim=1) % num_classes

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return {"input_ids": self.data[idx], "labels": self.labels[idx]}


# HuggingFace dataset wrapper
class HFTextDataset(Dataset):
    def __init__(self, hf_dataset, vocab_size=5000, seq_len=128, num_classes=2):
        self.data = []
        self.labels = []
        self.vocab_size = vocab_size
        self.seq_len = seq_len

        # Build simple vocabulary from first 1000 samples
        word_to_id = {"<PAD>": 0, "<UNK>": 1}
        word_counts = Counter()

        for i, item in enumerate(hf_dataset):
            if i >= 1000:
                break
            text = item["text"] if "text" in item else item["sentence"]
            words = text.lower().split()
            word_counts.update(words)

        # Take most common words
        for word, _ in word_counts.most_common(vocab_size - 2):
            if len(word_to_id) >= vocab_size:
                break
            word_to_id[word] = len(word_to_id)

        self.word_to_id = word_to_id

        # Tokenize dataset
        for item in hf_dataset:
            text = item["text"] if "text" in item else item["sentence"]
            label = item["label"]

            words = text.lower().split()
            token_ids = [
                word_to_id.get(w, word_to_id["<UNK>"]) for w in words[:seq_len]
            ]

            # Pad or truncate
            if len(token_ids) < seq_len:
                token_ids += [word_to_id["<PAD>"]] * (seq_len - len(token_ids))
            else:
                token_ids = token_ids[:seq_len]

            self.data.append(torch.tensor(token_ids, dtype=torch.long))
            self.labels.append(label)

        self.labels = torch.tensor(self.labels, dtype=torch.long)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return {"input_ids": self.data[idx], "labels": self.labels[idx]}


# LoRA adapter module
class LoRALayer(nn.Module):
    def __init__(self, in_features, out_features, rank=8):
        super().__init__()
        self.rank = rank
        self.lora_A = nn.Parameter(torch.randn(in_features, rank) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(rank, out_features))
        self.scaling = 0.5

    def forward(self, x):
        return (x @ self.lora_A @ self.lora_B) * self.scaling


# Gumbel-Softmax routing gate
class SparseRoutingGate(nn.Module):
    def __init__(self, dim, temperature=1.0):
        super().__init__()
        self.gate_weights = nn.Parameter(torch.ones(dim))
        self.temperature = temperature

    def forward(self, training=True):
        if training:
            logits = torch.stack([self.gate_weights, -self.gate_weights], dim=-1)
            gumbel_noise = -torch.log(-torch.log(torch.rand_like(logits) + 1e-8) + 1e-8)
            logits_with_noise = (logits + gumbel_noise) / self.temperature
            soft_mask = F.softmax(logits_with_noise, dim=-1)[..., 0]
            hard_mask = (soft_mask > 0.5).float()
            mask = hard_mask - soft_mask.detach() + soft_mask
        else:
            mask = (torch.sigmoid(self.gate_weights) > 0.5).float()
        return mask


# Transformer layer with SR-PEFT
class SRPEFTTransformerLayer(nn.Module):
    def __init__(self, d_model=256, nhead=4, dim_feedforward=512, lora_rank=8):
        super().__init__()
        self.d_model = d_model
        self.self_attn = nn.MultiheadAttention(d_model, nhead, batch_first=True)
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.linear2 = nn.Linear(dim_feedforward, d_model)
        self.attn_lora = LoRALayer(d_model, d_model, rank=lora_rank)
        self.ffn_lora1 = LoRALayer(d_model, dim_feedforward, rank=lora_rank)
        self.ffn_lora2 = LoRALayer(dim_feedforward, d_model, rank=lora_rank)
        self.attn_gate = SparseRoutingGate(d_model)
        self.ffn_gate = SparseRoutingGate(dim_feedforward)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x, training=True):
        residual = x
        x = self.norm1(x)
        attn_out, _ = self.self_attn(x, x, x)
        lora_out = self.attn_lora(x)
        attn_mask = self.attn_gate(training)
        x = residual + self.dropout(
            attn_out + lora_out * attn_mask.unsqueeze(0).unsqueeze(0)
        )
        residual = x
        x = self.norm2(x)
        ffn_out = self.linear1(x)
        ffn_out = ffn_out + self.ffn_lora1(x)
        ffn_mask = self.ffn_gate(training)
        ffn_out = F.relu(ffn_out * ffn_mask.unsqueeze(0).unsqueeze(0))
        ffn_out = self.linear2(ffn_out) + self.ffn_lora2(ffn_out)
        x = residual + self.dropout(ffn_out)
        return x


# SR-PEFT Model
class SRPEFTModel(nn.Module):
    def __init__(
        self, vocab_size=5000, d_model=256, num_layers=4, num_classes=4, lora_rank=8
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList(
            [
                SRPEFTTransformerLayer(
                    d_model, nhead=4, dim_feedforward=512, lora_rank=lora_rank
                )
                for _ in range(num_layers)
            ]
        )
        self.classifier = nn.Linear(d_model, num_classes)
        self.num_layers = num_layers

    def forward(self, input_ids, training=True):
        x = self.embedding(input_ids)
        for layer in self.layers:
            x = layer(x, training)
        x = torch.mean(x, dim=1)
        logits = self.classifier(x)
        return logits

    def get_sparsity_ratio(self):
        total_params = 0
        active_params = 0
        for layer in self.layers:
            attn_mask = (torch.sigmoid(layer.attn_gate.gate_weights) > 0.5).float()
            total_params += len(attn_mask)
            active_params += attn_mask.sum().item()
            ffn_mask = (torch.sigmoid(layer.ffn_gate.gate_weights) > 0.5).float()
            total_params += len(ffn_mask)
            active_params += ffn_mask.sum().item()
        sparsity_ratio = 1.0 - (active_params / total_params)
        return sparsity_ratio


# Training function
def train_epoch(model, dataloader, optimizer, sparsity_weight=0.01):
    model.train()
    total_loss = 0
    total_correct = 0
    total_samples = 0

    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        labels = batch["labels"].to(device)
        optimizer.zero_grad()
        logits = model(input_ids, training=True)
        task_loss = F.cross_entropy(logits, labels)
        sparsity_loss = 0
        for layer in model.layers:
            attn_gate_prob = torch.sigmoid(layer.attn_gate.gate_weights)
            ffn_gate_prob = torch.sigmoid(layer.ffn_gate.gate_weights)
            sparsity_loss += torch.mean(attn_gate_prob) + torch.mean(ffn_gate_prob)
        loss = task_loss + sparsity_weight * sparsity_loss
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        preds = torch.argmax(logits, dim=-1)
        total_correct += (preds == labels).sum().item()
        total_samples += len(labels)

    avg_loss = total_loss / len(dataloader)
    accuracy = total_correct / total_samples
    return avg_loss, accuracy


# Evaluation function
def evaluate(model, dataloader, baseline_accuracy=None):
    model.eval()
    total_loss = 0
    total_correct = 0
    total_samples = 0

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            logits = model(input_ids, training=False)
            loss = F.cross_entropy(logits, labels)
            total_loss += loss.item()
            preds = torch.argmax(logits, dim=-1)
            total_correct += (preds == labels).sum().item()
            total_samples += len(labels)

    avg_loss = total_loss / len(dataloader)
    accuracy = total_correct / total_samples
    sparsity_ratio = model.get_sparsity_ratio()
    activated_params_ratio = 1.0 - sparsity_ratio

    # Compute EATS metric
    if baseline_accuracy is not None and baseline_accuracy > 0:
        eats = (accuracy / baseline_accuracy) / (activated_params_ratio**0.5)
    else:
        eats = 0.0

    return avg_loss, accuracy, sparsity_ratio, eats


# Load HuggingFace datasets
print("Loading HuggingFace datasets...")
try:
    imdb_train = load_dataset("imdb", split="train[:1000]")
    imdb_test = load_dataset("imdb", split="test[:500]")
    print(f"Loaded IMDB dataset: {len(imdb_train)} train, {len(imdb_test)} test")
except Exception as e:
    print(f"Error loading IMDB: {e}")
    imdb_train = None
    imdb_test = None

try:
    agnews_train = load_dataset("ag_news", split="train[:1000]")
    agnews_test = load_dataset("ag_news", split="test[:500]")
    print(f"Loaded AG News dataset: {len(agnews_train)} train, {len(agnews_test)} test")
except Exception as e:
    print(f"Error loading AG News: {e}")
    agnews_train = None
    agnews_test = None

# Initialize experiment data
experiment_data = {"synthetic_text": {}, "imdb": {}, "agnews": {}}

# Dataset configurations
dataset_configs = [
    ("synthetic_text", None, None, 5000, 128, 4),
]

if imdb_train is not None:
    dataset_configs.append(("imdb", imdb_train, imdb_test, 5000, 128, 2))

if agnews_train is not None:
    dataset_configs.append(("agnews", agnews_train, agnews_test, 5000, 128, 4))

# Hyperparameter configurations
hyperparam_configs = [
    {"lr": 1e-3, "batch_size": 32, "num_epochs": 30},
    {"lr": 5e-4, "batch_size": 32, "num_epochs": 30},
    {"lr": 1e-3, "batch_size": 16, "num_epochs": 30},
    {"lr": 1e-3, "batch_size": 64, "num_epochs": 30},
]

print("\n" + "=" * 80)
print("HYPERPARAMETER TUNING: Learning Rate and Batch Size")
print("=" * 80)

for (
    dataset_name,
    hf_train,
    hf_test,
    vocab_size,
    seq_len,
    num_classes,
) in dataset_configs:
    print(f"\n{'='*80}")
    print(f"Dataset: {dataset_name}")
    print(f"{'='*80}")

    # Create datasets
    if dataset_name == "synthetic_text":
        train_dataset = SyntheticTextDataset(
            num_samples=2000,
            seq_len=seq_len,
            vocab_size=vocab_size,
            num_classes=num_classes,
        )
        val_dataset = SyntheticTextDataset(
            num_samples=500,
            seq_len=seq_len,
            vocab_size=vocab_size,
            num_classes=num_classes,
        )
    else:
        train_dataset = HFTextDataset(
            hf_train, vocab_size=vocab_size, seq_len=seq_len, num_classes=num_classes
        )
        val_dataset = HFTextDataset(
            hf_test, vocab_size=vocab_size, seq_len=seq_len, num_classes=num_classes
        )

    # Compute baseline accuracy (dense model without sparsity)
    print("Computing baseline accuracy...")
    torch.manual_seed(42)
    baseline_model = SRPEFTModel(
        vocab_size=vocab_size,
        d_model=256,
        num_layers=4,
        num_classes=num_classes,
        lora_rank=8,
    )
    baseline_model = baseline_model.to(device)

    # Freeze gates to prevent sparsity
    for layer in baseline_model.layers:
        layer.attn_gate.gate_weights.requires_grad = False
        layer.ffn_gate.gate_weights.requires_grad = False

    baseline_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    baseline_optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, baseline_model.parameters()), lr=1e-3
    )

    # Train baseline for 10 epochs
    baseline_train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    for epoch in range(10):
        train_epoch(
            baseline_model,
            baseline_train_loader,
            baseline_optimizer,
            sparsity_weight=0.0,
        )

    baseline_loss, baseline_accuracy, _, _ = evaluate(
        baseline_model, baseline_loader, baseline_accuracy=None
    )
    print(f"Baseline accuracy: {baseline_accuracy:.4f}")

    del baseline_model
    torch.cuda.empty_cache()

    for config_idx, config in enumerate(hyperparam_configs):
        lr = config["lr"]
        batch_size = config["batch_size"]
        num_epochs = config["num_epochs"]

        print(f"\n{'-'*80}")
        print(
            f"Config {config_idx+1}: lr={lr}, batch_size={batch_size}, num_epochs={num_epochs}"
        )
        print(f"{'-'*80}")

        torch.manual_seed(42)
        np.random.seed(42)

        model = SRPEFTModel(
            vocab_size=vocab_size,
            d_model=256,
            num_layers=4,
            num_classes=num_classes,
            lora_rank=8,
        )
        model = model.to(device)

        # Freeze original parameters
        for name, param in model.named_parameters():
            if "lora" not in name and "gate" not in name and "classifier" not in name:
                param.requires_grad = False

        optimizer = torch.optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()), lr=lr
        )

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        config_key = f"lr{lr}_bs{batch_size}_ep{num_epochs}"
        experiment_data[dataset_name][config_key] = {
            "metrics": {
                "train": {"accuracy": [], "sparsity": [], "eats": []},
                "val": {"accuracy": [], "sparsity": [], "eats": []},
            },
            "losses": {"train": [], "val": []},
            "epochs": [],
            "baseline_accuracy": baseline_accuracy,
        }

        for epoch in range(num_epochs):
            train_loss, train_acc = train_epoch(
                model, train_loader, optimizer, sparsity_weight=0.01
            )
            val_loss, val_acc, val_sparsity, val_eats = evaluate(
                model, val_loader, baseline_accuracy=baseline_accuracy
            )

            model.eval()
            with torch.no_grad():
                train_sparsity = model.get_sparsity_ratio()
                train_activated_ratio = 1.0 - train_sparsity
                train_eats = (
                    (train_acc / baseline_accuracy) / (train_activated_ratio**0.5)
                    if baseline_accuracy > 0
                    else 0.0
                )

            experiment_data[dataset_name][config_key]["epochs"].append(epoch)
            experiment_data[dataset_name][config_key]["losses"]["train"].append(
                train_loss
            )
            experiment_data[dataset_name][config_key]["losses"]["val"].append(val_loss)
            experiment_data[dataset_name][config_key]["metrics"]["train"][
                "accuracy"
            ].append(train_acc)
            experiment_data[dataset_name][config_key]["metrics"]["train"][
                "sparsity"
            ].append(train_sparsity)
            experiment_data[dataset_name][config_key]["metrics"]["train"][
                "eats"
            ].append(train_eats)
            experiment_data[dataset_name][config_key]["metrics"]["val"][
                "accuracy"
            ].append(val_acc)
            experiment_data[dataset_name][config_key]["metrics"]["val"][
                "sparsity"
            ].append(val_sparsity)
            experiment_data[dataset_name][config_key]["metrics"]["val"]["eats"].append(
                val_eats
            )

            if (epoch + 1) % 10 == 0 or epoch == num_epochs - 1:
                print(
                    f"Epoch {epoch+1}/{num_epochs}: validation_loss = {val_loss:.4f}, Val Acc: {val_acc:.4f}, Val Sparsity: {val_sparsity:.4f}, Val EATS: {val_eats:.4f}"
                )

        del model
        torch.cuda.empty_cache()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nExperiment data saved to {working_dir}/experiment_data.npy")

# Visualizations for each dataset
for dataset_name in experiment_data.keys():
    if not experiment_data[dataset_name]:
        continue

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    colors = ["blue", "green", "red", "purple"]
    markers = ["o", "s", "^", "d"]

    for idx, config_key in enumerate(list(experiment_data[dataset_name].keys())[:4]):
        data = experiment_data[dataset_name][config_key]

        axes[0, 0].plot(
            data["epochs"],
            data["losses"]["train"],
            label=config_key,
            color=colors[idx],
            marker=markers[idx],
            markevery=max(1, len(data["epochs"]) // 10),
        )
        axes[0, 1].plot(
            data["epochs"],
            data["losses"]["val"],
            label=config_key,
            color=colors[idx],
            marker=markers[idx],
            markevery=max(1, len(data["epochs"]) // 10),
        )
        axes[0, 2].plot(
            data["epochs"],
            data["metrics"]["val"]["accuracy"],
            label=config_key,
            color=colors[idx],
            marker=markers[idx],
            markevery=max(1, len(data["epochs"]) // 10),
        )
        axes[1, 0].plot(
            data["epochs"],
            data["metrics"]["train"]["accuracy"],
            label=config_key,
            color=colors[idx],
            marker=markers[idx],
            markevery=max(1, len(data["epochs"]) // 10),
        )
        axes[1, 1].plot(
            data["epochs"],
            data["metrics"]["val"]["sparsity"],
            label=config_key,
            color=colors[idx],
            marker=markers[idx],
            markevery=max(1, len(data["epochs"]) // 10),
        )
        axes[1, 2].plot(
            data["epochs"],
            data["metrics"]["val"]["eats"],
            label=config_key,
            color=colors[idx],
            marker=markers[idx],
            markevery=max(1, len(data["epochs"]) // 10),
        )

    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].set_ylabel("Train Loss")
    axes[0, 0].set_title(f"{dataset_name} - Training Loss")
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].set_ylabel("Validation Loss")
    axes[0, 1].set_title(f"{dataset_name} - Validation Loss")
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    axes[0, 2].set_xlabel("Epoch")
    axes[0, 2].set_ylabel("Validation Accuracy")
    axes[0, 2].set_title(f"{dataset_name} - Validation Accuracy")
    axes[0, 2].legend()
    axes[0, 2].grid(True)

    axes[1, 0].set_xlabel("Epoch")
    axes[1, 0].set_ylabel("Train Accuracy")
    axes[1, 0].set_title(f"{dataset_name} - Training Accuracy")
    axes[1, 0].legend()
    axes[1, 0].grid(True)

    axes[1, 1].set_xlabel("Epoch")
    axes[1, 1].set_ylabel("Validation Sparsity")
    axes[1, 1].set_title(f"{dataset_name} - Validation Sparsity")
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    axes[1, 2].set_xlabel("Epoch")
    axes[1, 2].set_ylabel("Val EATS")
    axes[1, 2].set_title(f"{dataset_name} - EATS Metric")
    axes[1, 2].legend()
    axes[1, 2].grid(True)

    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"{dataset_name}_hyperparameter_tuning.png"), dpi=150
    )
    print(
        f"Saved visualization: {working_dir}/{dataset_name}_hyperparameter_tuning.png"
    )

# Summary comparison
print("\n" + "=" * 80)
print("HYPERPARAMETER TUNING RESULTS SUMMARY")
print("=" * 80)

for dataset_name in experiment_data.keys():
    if not experiment_data[dataset_name]:
        continue

    print(f"\nDataset: {dataset_name}")
    print(
        f"{'Config':<30} {'Final Val Acc':<15} {'Final Sparsity':<15} {'Final EATS':<15}"
    )
    print("-" * 75)

    best_config = None
    best_eats = 0

    for config_key in experiment_data[dataset_name].keys():
        data = experiment_data[dataset_name][config_key]
        final_val_acc = data["metrics"]["val"]["accuracy"][-1]
        final_val_sparsity = data["metrics"]["val"]["sparsity"][-1]
        final_val_eats = data["metrics"]["val"]["eats"][-1]

        print(
            f"{config_key:<30} {final_val_acc:<15.4f} {final_val_sparsity:<15.4f} {final_val_eats:<15.4f}"
        )

        if final_val_eats > best_eats:
            best_eats = final_val_eats
            best_config = config_key

    print("-" * 75)
    print(f"Best configuration: {best_config} with EATS = {best_eats:.4f}")

print("\n" + "=" * 80)
