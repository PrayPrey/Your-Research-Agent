import os
import sys
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModel
import warnings
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)


class StdoutWrapper:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, name):
        if name == "isatty":
            return lambda: False
        return getattr(self.wrapped, name)

    def write(self, text):
        return self.wrapped.write(text)

    def flush(self):
        return self.wrapped.flush()


sys.stdout = StdoutWrapper(sys.stdout)
sys.stderr = StdoutWrapper(sys.stderr)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

experiment_data = {
    "imdb": {
        "metrics": {
            "train_acc": [],
            "val_acc": [],
            "sparsity": [],
            "eats": [],
            "layer_sparsity": [],
        },
        "losses": {"train": [], "val": [], "task": [], "sparsity": []},
        "times": [],
    },
    "agnews": {
        "metrics": {
            "train_acc": [],
            "val_acc": [],
            "sparsity": [],
            "eats": [],
            "layer_sparsity": [],
        },
        "losses": {"train": [], "val": [], "task": [], "sparsity": []},
        "times": [],
    },
    "sst2": {
        "metrics": {
            "train_acc": [],
            "val_acc": [],
            "sparsity": [],
            "eats": [],
            "layer_sparsity": [],
        },
        "losses": {"train": [], "val": [], "task": [], "sparsity": []},
        "times": [],
    },
}

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({"pad_token": "[PAD]"})


class LayerWiseSRPEFT(nn.Module):
    def __init__(
        self, base_model_name, num_classes, lora_rank=8, num_layers=6, dropout=0.4
    ):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model_name)
        if len(tokenizer) > self.encoder.config.vocab_size:
            self.encoder.resize_token_embeddings(len(tokenizer))

        hidden_size = self.encoder.config.hidden_size
        self.num_layers = num_layers

        # Layer-wise LoRA adapters with heterogeneous gates
        self.lora_down_layers = nn.ModuleList(
            [nn.Linear(hidden_size, lora_rank, bias=False) for _ in range(num_layers)]
        )
        self.lora_up_layers = nn.ModuleList(
            [nn.Linear(lora_rank, hidden_size, bias=False) for _ in range(num_layers)]
        )

        # Layer-specific routing gates (different sparsity patterns per layer)
        self.layer_gates = nn.ParameterList(
            [nn.Parameter(torch.randn(hidden_size) * 0.05) for _ in range(num_layers)]
        )

        # Global sparsity control (learnable temperature)
        self.temperature = nn.Parameter(torch.ones(1))

        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_size, num_classes)

        for param in self.encoder.parameters():
            param.requires_grad = False

    def forward(
        self, input_ids, attention_mask, apply_sparsity=True, temperature_scale=1.0
    ):
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
        )
        hidden_states = outputs.hidden_states

        final_hidden = hidden_states[-1][:, 0, :]
        adapted = final_hidden.clone()

        all_gate_probs = []
        layer_contributions = []

        # Apply layer-wise routing
        for i in range(min(self.num_layers, len(hidden_states) - 1)):
            layer_hidden = hidden_states[i + 1][:, 0, :]

            # LoRA transformation
            lora_out = self.lora_up_layers[i](self.lora_down_layers[i](layer_hidden))

            # Gating with temperature annealing
            gate_logits = self.layer_gates[i] / (self.temperature.abs() + 1e-6)
            gate_probs = torch.sigmoid(gate_logits * temperature_scale)
            all_gate_probs.append(gate_probs)

            if apply_sparsity:
                if self.training:
                    # Gumbel-Softmax during training for smooth gradients
                    mask = gate_probs
                else:
                    # Hard thresholding during eval
                    mask = (gate_probs > 0.5).float()
            else:
                mask = torch.ones_like(gate_probs)

            adapted = adapted + lora_out * mask
            layer_contributions.append(mask.mean().item())

        adapted = self.dropout(adapted)
        logits = self.classifier(adapted)

        return logits, all_gate_probs, layer_contributions

    def get_sparsity_stats(self):
        with torch.no_grad():
            layer_sparsities = []
            for gate in self.layer_gates:
                gate_probs = torch.sigmoid(gate)
                sparsity = (gate_probs < 0.5).float().mean().item()
                layer_sparsities.append(sparsity)
            overall_sparsity = np.mean(layer_sparsities)
        return overall_sparsity, layer_sparsities


class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt",
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids": self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels": self.labels[idx],
        }


def train_epoch(
    model,
    dataloader,
    optimizer,
    epoch,
    total_epochs,
    warmup_epochs=3,
    target_sparsity=0.6,
    lambda_base=0.5,
):
    model.train()
    total_loss = 0
    task_loss_sum = 0
    sparsity_loss_sum = 0
    correct = 0
    total = 0

    # Two-stage training: warmup without sparsity, then progressive sparsity
    if epoch < warmup_epochs:
        apply_sparsity = False
        lambda_sparsity = 0.0
        temperature_scale = 1.0
    else:
        apply_sparsity = True
        # Progressive sparsity annealing
        progress = (epoch - warmup_epochs) / (total_epochs - warmup_epochs)
        lambda_sparsity = lambda_base * (1 + progress)  # Increase regularization
        temperature_scale = 1.0 + 2.0 * progress  # Sharpen gates over time

    for batch in dataloader:
        batch = {
            k: v.to(device) for k, v in batch.items() if isinstance(v, torch.Tensor)
        }

        optimizer.zero_grad()
        logits, gate_probs_list, _ = model(
            batch["input_ids"],
            batch["attention_mask"],
            apply_sparsity=apply_sparsity,
            temperature_scale=temperature_scale,
        )

        task_loss = F.cross_entropy(logits, batch["labels"])

        # Sparsity loss with target-based penalty
        if apply_sparsity and len(gate_probs_list) > 0:
            avg_gate_probs = torch.stack([gp.mean() for gp in gate_probs_list]).mean()
            # L1 + target sparsity penalty
            l1_loss = avg_gate_probs
            target_loss = (1.0 - avg_gate_probs - target_sparsity) ** 2
            sparsity_loss = l1_loss + 0.5 * target_loss
        else:
            sparsity_loss = torch.tensor(0.0, device=device)

        loss = task_loss + lambda_sparsity * sparsity_loss

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        total_loss += loss.item()
        task_loss_sum += task_loss.item()
        sparsity_loss_sum += sparsity_loss.item()
        preds = torch.argmax(logits, dim=1)
        correct += (preds == batch["labels"]).sum().item()
        total += len(batch["labels"])

    return (
        total_loss / len(dataloader),
        task_loss_sum / len(dataloader),
        sparsity_loss_sum / len(dataloader),
        correct / total,
    )


def validate(model, dataloader):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in dataloader:
            batch = {
                k: v.to(device) for k, v in batch.items() if isinstance(v, torch.Tensor)
            }
            logits, _, _ = model(
                batch["input_ids"], batch["attention_mask"], apply_sparsity=True
            )
            loss = F.cross_entropy(logits, batch["labels"])
            total_loss += loss.item()
            preds = torch.argmax(logits, dim=1)
            correct += (preds == batch["labels"]).sum().item()
            total += len(batch["labels"])

    return total_loss / len(dataloader), correct / total


def compute_eats(val_acc, sparsity, time_ratio, epsilon=1e-8):
    if sparsity < epsilon or time_ratio < epsilon:
        return 0.0
    return (val_acc * sparsity) / np.sqrt(max(time_ratio, epsilon))


print("\nLoading datasets...")
imdb_data = load_dataset("imdb", split="train[:2000]")
imdb_texts, imdb_labels = imdb_data["text"], imdb_data["label"]
imdb_train_texts, imdb_train_labels = imdb_texts[:1600], imdb_labels[:1600]
imdb_val_texts, imdb_val_labels = imdb_texts[1600:], imdb_labels[1600:]

agnews_data = load_dataset("ag_news", split="train[:2000]")
agnews_texts, agnews_labels = agnews_data["text"], agnews_data["label"]
agnews_train_texts, agnews_train_labels = agnews_texts[:1600], agnews_labels[:1600]
agnews_val_texts, agnews_val_labels = agnews_texts[1600:], agnews_labels[1600:]

sst2_data = load_dataset("glue", "sst2", split="train[:2000]")
sst2_texts, sst2_labels = sst2_data["sentence"], sst2_data["label"]
sst2_train_texts, sst2_train_labels = sst2_texts[:1600], sst2_labels[:1600]
sst2_val_texts, sst2_val_labels = sst2_texts[1600:], sst2_labels[1600:]

datasets_config = [
    ("imdb", imdb_train_texts, imdb_train_labels, imdb_val_texts, imdb_val_labels, 2),
    (
        "agnews",
        agnews_train_texts,
        agnews_train_labels,
        agnews_val_texts,
        agnews_val_labels,
        4,
    ),
    ("sst2", sst2_train_texts, sst2_train_labels, sst2_val_texts, sst2_val_labels, 2),
]

for (
    dataset_name,
    train_texts,
    train_labels,
    val_texts,
    val_labels,
    num_classes,
) in datasets_config:
    print(f"\n{'='*60}")
    print(f"Training on {dataset_name.upper()} with Two-Stage SR-PEFT")
    print(f"{'='*60}")

    train_dataset = TextDataset(train_texts, train_labels, tokenizer)
    val_dataset = TextDataset(val_texts, val_labels, tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

    model = LayerWiseSRPEFT(
        "distilbert-base-uncased", num_classes=num_classes, dropout=0.4
    )
    model = model.to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=15)

    num_epochs = 15
    warmup_epochs = 3
    best_val_loss = float("inf")
    patience = 5
    patience_counter = 0
    baseline_time = None

    for epoch in range(num_epochs):
        epoch_start_time = time.time()

        train_loss, task_loss, sparsity_loss, train_acc = train_epoch(
            model,
            train_loader,
            optimizer,
            epoch,
            num_epochs,
            warmup_epochs=warmup_epochs,
            target_sparsity=0.6,
            lambda_base=0.5,
        )
        val_loss, val_acc = validate(model, val_loader)

        sparsity, layer_sparsities = model.get_sparsity_stats()
        epoch_time = time.time() - epoch_start_time

        if baseline_time is None:
            baseline_time = epoch_time
        time_ratio = epoch_time / baseline_time
        eats = compute_eats(val_acc, sparsity, time_ratio)

        experiment_data[dataset_name]["metrics"]["train_acc"].append(train_acc)
        experiment_data[dataset_name]["metrics"]["val_acc"].append(val_acc)
        experiment_data[dataset_name]["metrics"]["sparsity"].append(sparsity)
        experiment_data[dataset_name]["metrics"]["eats"].append(eats)
        experiment_data[dataset_name]["metrics"]["layer_sparsity"].append(
            layer_sparsities
        )
        experiment_data[dataset_name]["losses"]["train"].append(train_loss)
        experiment_data[dataset_name]["losses"]["val"].append(val_loss)
        experiment_data[dataset_name]["losses"]["task"].append(task_loss)
        experiment_data[dataset_name]["losses"]["sparsity"].append(sparsity_loss)
        experiment_data[dataset_name]["times"].append(epoch_time)

        print(
            f"Epoch {epoch+1}/{num_epochs} [{'Warmup' if epoch < warmup_epochs else 'Sparsity'}]:"
        )
        print(
            f"  Train: Loss={train_loss:.4f} (Task={task_loss:.4f}, Sparsity={sparsity_loss:.4f}), Acc={train_acc:.4f}"
        )
        print(f"  Val: Loss={val_loss:.4f}, Acc={val_acc:.4f}")
        print(
            f"  Sparsity={sparsity:.4f}, Layer Sparsity={[f'{s:.2f}' for s in layer_sparsities[:3]]}"
        )
        print(f"  EATS={eats:.4f}, Time={epoch_time:.2f}s")

        scheduler.step()

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(
                model.state_dict(),
                os.path.join(working_dir, f"{dataset_name}_best_model.pt"),
            )
        else:
            patience_counter += 1
            if patience_counter >= patience and epoch >= warmup_epochs:
                print(f"Early stopping at epoch {epoch+1}")
                break

    print(
        f"\n{dataset_name.upper()} Final: Val Acc={experiment_data[dataset_name]['metrics']['val_acc'][-1]:.4f}, "
        f"Sparsity={experiment_data[dataset_name]['metrics']['sparsity'][-1]:.4f}, "
        f"EATS={experiment_data[dataset_name]['metrics']['eats'][-1]:.4f}"
    )

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print(f"\n{'='*60}")
print("FINAL SUMMARY")
print(f"{'='*60}")
for ds in ["imdb", "agnews", "sst2"]:
    print(
        f"{ds.upper()}: Val Acc={experiment_data[ds]['metrics']['val_acc'][-1]:.4f}, "
        f"Sparsity={experiment_data[ds]['metrics']['sparsity'][-1]:.4f}, "
        f"EATS={experiment_data[ds]['metrics']['eats'][-1]:.4f}"
    )

# Generate Pareto frontier plots
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for idx, ds in enumerate(["imdb", "agnews", "sst2"]):
    acc = experiment_data[ds]["metrics"]["val_acc"]
    sparsity = experiment_data[ds]["metrics"]["sparsity"]
    axes[idx].scatter(sparsity, acc, c=range(len(acc)), cmap="viridis")
    axes[idx].set_xlabel("Sparsity")
    axes[idx].set_ylabel("Validation Accuracy")
    axes[idx].set_title(f"{ds.upper()} Accuracy-Sparsity Tradeoff")
    axes[idx].grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pareto_frontiers.png"), dpi=150)
plt.close()

print("\nExperiment complete. Data saved.")
