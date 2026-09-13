import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, Subset
import math
import matplotlib.pyplot as plt
from collections import deque

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

torch.manual_seed(42)
np.random.seed(42)


class SyntheticTextDataset(Dataset):
    def __init__(self, num_samples=5000, seq_len=32, vocab_size=100):
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.data = []
        for i in range(num_samples):
            pattern_type = i % 5
            seq = np.zeros(seq_len, dtype=np.int64)
            if pattern_type == 0:
                start = np.random.randint(0, vocab_size - seq_len)
                seq = np.arange(start, start + seq_len) % vocab_size
            elif pattern_type == 1:
                pattern_len = np.random.randint(2, 6)
                pattern = np.random.randint(0, vocab_size, pattern_len)
                seq = np.tile(pattern, seq_len // pattern_len + 1)[:seq_len]
            elif pattern_type == 2:
                base = np.random.randint(0, vocab_size // 2)
                seq = np.random.randint(base, base + vocab_size // 2, seq_len)
            elif pattern_type == 3:
                seq[0] = np.random.randint(1, 10)
                seq[1] = np.random.randint(1, 10)
                for j in range(2, seq_len):
                    seq[j] = (seq[j - 1] + seq[j - 2]) % vocab_size
            else:
                seq = np.random.randint(0, vocab_size, seq_len)
            self.data.append(seq)
        self.data = np.array(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        seq = self.data[idx]
        return {"input_ids": torch.tensor(seq[:-1]), "labels": torch.tensor(seq[1:])}


class HFTextDataset(Dataset):
    def __init__(self, texts, seq_len=32, vocab_size=100):
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.data = []
        for text in texts:
            if len(text) >= seq_len:
                tokens = [ord(c) % vocab_size for c in text[:seq_len]]
                self.data.append(np.array(tokens, dtype=np.int64))
        if len(self.data) == 0:
            self.data = [
                np.random.randint(0, vocab_size, seq_len, dtype=np.int64)
                for _ in range(100)
            ]
        self.data = np.array(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        seq = self.data[idx]
        return {"input_ids": torch.tensor(seq[:-1]), "labels": torch.tensor(seq[1:])}


def load_wikitext_dataset(num_samples=3000, seq_len=32, vocab_size=100):
    try:
        from datasets import load_dataset

        dataset = load_dataset(
            "wikitext", "wikitext-2-raw-v1", split="train", trust_remote_code=True
        )
        texts = [t for t in dataset["text"] if len(t) >= seq_len][: num_samples * 2]
        return HFTextDataset(texts[:num_samples], seq_len, vocab_size), HFTextDataset(
            texts[num_samples : num_samples + 500], seq_len, vocab_size
        )
    except:
        return SyntheticTextDataset(
            num_samples, seq_len, vocab_size
        ), SyntheticTextDataset(500, seq_len, vocab_size)


def load_agnews_dataset(num_samples=3000, seq_len=32, vocab_size=100):
    try:
        from datasets import load_dataset

        dataset = load_dataset("ag_news", split="train", trust_remote_code=True)
        texts = [t for t in dataset["text"] if len(t) >= seq_len][: num_samples * 2]
        return HFTextDataset(texts[:num_samples], seq_len, vocab_size), HFTextDataset(
            texts[num_samples : num_samples + 500], seq_len, vocab_size
        )
    except:
        return SyntheticTextDataset(
            num_samples, seq_len, vocab_size
        ), SyntheticTextDataset(500, seq_len, vocab_size)


class SmallTransformer(nn.Module):
    def __init__(self, vocab_size=100, d_model=128, nhead=4, num_layers=2, dim_ff=256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Parameter(torch.randn(1, 64, d_model) * 0.1)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model, nhead, dim_ff, dropout=0.1, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.fc_out = nn.Linear(d_model, vocab_size)
        self.d_model = d_model

    def forward(self, x):
        seq_len = x.size(1)
        x = self.embedding(x) * math.sqrt(self.d_model)
        x = x + self.pos_encoding[:, :seq_len, :]
        mask = nn.Transformer.generate_square_subsequent_mask(seq_len).to(x.device)
        x = self.transformer(x, mask=mask, is_causal=True)
        return self.fc_out(x)


class PhaseDetector:
    def __init__(self, window_size=5):
        self.val_losses = deque(maxlen=window_size)
        self.window_size = window_size
        self.epoch = 0

    def update(self, val_loss):
        self.val_losses.append(val_loss)
        self.epoch += 1

    def get_phase(self):
        if self.epoch < 3:
            return "memorization"
        losses = list(self.val_losses)
        if len(losses) < 3:
            return "memorization"
        recent_improvement = losses[-3] - losses[-1]
        avg_loss = np.mean(losses)
        if recent_improvement > 0.05 * avg_loss:
            return "memorization"
        elif recent_improvement > 0.01 * avg_loss:
            return "generalization"
        else:
            return "refinement"


class PADASampler:
    def __init__(self, model, dataset, sample_ratio=0.7):
        self.model = model
        self.dataset = dataset
        self.sample_ratio = sample_ratio
        self.gradient_cache = {}
        self.uncertainty_cache = {}
        self.loss_cache = {}

    def compute_sample_scores(self, indices, phase):
        scores = []
        self.model.eval()
        for idx in indices:
            batch = self.dataset[idx]
            input_ids = batch["input_ids"].unsqueeze(0).to(device)
            labels = batch["labels"].unsqueeze(0).to(device)
            with torch.enable_grad():
                self.model.zero_grad()
                output = self.model(input_ids)
                loss = F.cross_entropy(
                    output.view(-1, output.size(-1)), labels.view(-1)
                )
                loss.backward()
                grad_norm = 0
                for p in self.model.parameters():
                    if p.grad is not None:
                        grad_norm += p.grad.norm().item() ** 2
                grad_norm = math.sqrt(grad_norm)
            with torch.no_grad():
                probs = F.softmax(output, dim=-1)
                entropy = -(probs * torch.log(probs + 1e-10)).sum(dim=-1).mean().item()
            self.gradient_cache[idx] = grad_norm
            self.uncertainty_cache[idx] = entropy
            self.loss_cache[idx] = loss.item()

            if phase == "memorization":
                score = grad_norm + 0.5 * loss.item()
            elif phase == "generalization":
                grad_values = list(self.gradient_cache.values())
                median_grad = (
                    np.median(grad_values) if len(grad_values) > 10 else grad_norm
                )
                score = 1.0 / (1.0 + abs(grad_norm - median_grad)) + 0.3 * entropy
            else:
                score = entropy + 0.2 * loss.item()
            scores.append(score)
        self.model.train()
        return np.array(scores)

    def select_samples(self, phase, num_samples=None, warmup=False):
        all_indices = list(range(len(self.dataset)))
        if num_samples is None:
            num_samples = int(len(all_indices) * self.sample_ratio)
        if warmup:
            return np.random.choice(all_indices, num_samples, replace=False)
        score_subset_size = min(300, len(all_indices))
        score_subset = np.random.choice(all_indices, score_subset_size, replace=False)
        scores = self.compute_sample_scores(score_subset, phase)
        sorted_indices = np.argsort(scores)[::-1]
        top_k = min(num_samples, len(sorted_indices))
        selected = list(score_subset[sorted_indices[:top_k]])
        remaining = list(set(all_indices) - set(selected))
        if len(selected) < num_samples and remaining:
            extra = np.random.choice(
                remaining,
                min(num_samples - len(selected), len(remaining)),
                replace=False,
            )
            selected.extend(extra)
        return np.array(selected[:num_samples])


def evaluate(model, dataloader):
    model.eval()
    total_loss, total_samples = 0, 0
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            output = model(input_ids)
            loss = F.cross_entropy(output.view(-1, output.size(-1)), labels.view(-1))
            total_loss += loss.item() * input_ids.size(0)
            total_samples += input_ids.size(0)
    return total_loss / total_samples if total_samples > 0 else float("inf")


def train_epoch(model, optimizer, dataloader):
    model.train()
    total_loss, total_samples = 0, 0
    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        labels = batch["labels"].to(device)
        optimizer.zero_grad()
        output = model(input_ids)
        loss = F.cross_entropy(output.view(-1, output.size(-1)), labels.view(-1))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss += loss.item() * input_ids.size(0)
        total_samples += input_ids.size(0)
    return total_loss / total_samples if total_samples > 0 else 0, total_samples


def run_experiment(
    train_dataset,
    val_dataset,
    dataset_name,
    num_epochs=15,
    batch_size=32,
    lr=5e-4,
    sample_ratio=0.7,
):
    print(f"\n{'='*60}")
    print(f"Running experiment on: {dataset_name}")
    print(f"{'='*60}")

    results = {
        "pada": {
            "losses": {"train": [], "val": []},
            "samples_used": [],
            "phases": [],
            "sample_efficiency": [],
        },
        "random": {
            "losses": {"train": [], "val": []},
            "samples_used": [],
            "sample_efficiency": [],
        },
        "full": {
            "losses": {"train": [], "val": []},
            "samples_used": [],
            "sample_efficiency": [],
        },
    }

    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    warmup_epochs = 2

    # PADA Training
    print(f"\n--- PADA ---")
    torch.manual_seed(42)
    model_pada = SmallTransformer().to(device)
    optimizer_pada = torch.optim.AdamW(
        model_pada.parameters(), lr=lr, weight_decay=0.01
    )
    scheduler_pada = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer_pada, T_max=num_epochs
    )
    phase_detector = PhaseDetector(window_size=5)
    pada_sampler = PADASampler(model_pada, train_dataset, sample_ratio=sample_ratio)
    initial_val_loss = evaluate(model_pada, val_loader)
    total_samples_pada = 0

    for epoch in range(num_epochs):
        warmup = epoch < warmup_epochs
        phase = phase_detector.get_phase()
        selected_indices = pada_sampler.select_samples(
            phase, num_samples=int(len(train_dataset) * sample_ratio), warmup=warmup
        )
        subset = Subset(train_dataset, selected_indices)
        train_loader = DataLoader(subset, batch_size=batch_size, shuffle=True)
        train_loss, samples_used = train_epoch(model_pada, optimizer_pada, train_loader)
        scheduler_pada.step()
        total_samples_pada += samples_used
        val_loss = evaluate(model_pada, val_loader)
        phase_detector.update(val_loss)
        loss_improvement = initial_val_loss - val_loss
        sample_efficiency = (
            loss_improvement / total_samples_pada * 10000
            if total_samples_pada > 0
            else 0
        )
        results["pada"]["losses"]["train"].append(train_loss)
        results["pada"]["losses"]["val"].append(val_loss)
        results["pada"]["samples_used"].append(total_samples_pada)
        results["pada"]["phases"].append(phase)
        results["pada"]["sample_efficiency"].append(sample_efficiency)
        print(f"Epoch {epoch}: validation_loss = {val_loss:.4f}, phase = {phase}")

    # Random Training
    print(f"\n--- Random ---")
    torch.manual_seed(42)
    model_random = SmallTransformer().to(device)
    optimizer_random = torch.optim.AdamW(
        model_random.parameters(), lr=lr, weight_decay=0.01
    )
    scheduler_random = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer_random, T_max=num_epochs
    )
    initial_val_loss_random = evaluate(model_random, val_loader)
    total_samples_random = 0

    for epoch in range(num_epochs):
        np.random.seed(42 + epoch)
        selected_indices = np.random.choice(
            len(train_dataset), int(len(train_dataset) * sample_ratio), replace=False
        )
        subset = Subset(train_dataset, selected_indices)
        train_loader = DataLoader(subset, batch_size=batch_size, shuffle=True)
        train_loss, samples_used = train_epoch(
            model_random, optimizer_random, train_loader
        )
        scheduler_random.step()
        total_samples_random += samples_used
        val_loss = evaluate(model_random, val_loader)
        loss_improvement = initial_val_loss_random - val_loss
        sample_efficiency = (
            loss_improvement / total_samples_random * 10000
            if total_samples_random > 0
            else 0
        )
        results["random"]["losses"]["train"].append(train_loss)
        results["random"]["losses"]["val"].append(val_loss)
        results["random"]["samples_used"].append(total_samples_random)
        results["random"]["sample_efficiency"].append(sample_efficiency)
        print(f"Epoch {epoch}: validation_loss = {val_loss:.4f}")

    # Full Training
    print(f"\n--- Full ---")
    torch.manual_seed(42)
    model_full = SmallTransformer().to(device)
    optimizer_full = torch.optim.AdamW(
        model_full.parameters(), lr=lr, weight_decay=0.01
    )
    scheduler_full = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer_full, T_max=num_epochs
    )
    initial_val_loss_full = evaluate(model_full, val_loader)
    total_samples_full = 0
    train_loader_full = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    for epoch in range(num_epochs):
        train_loss, samples_used = train_epoch(
            model_full, optimizer_full, train_loader_full
        )
        scheduler_full.step()
        total_samples_full += samples_used
        val_loss = evaluate(model_full, val_loader)
        loss_improvement = initial_val_loss_full - val_loss
        sample_efficiency = (
            loss_improvement / total_samples_full * 10000
            if total_samples_full > 0
            else 0
        )
        results["full"]["losses"]["train"].append(train_loss)
        results["full"]["losses"]["val"].append(val_loss)
        results["full"]["samples_used"].append(total_samples_full)
        results["full"]["sample_efficiency"].append(sample_efficiency)
        print(f"Epoch {epoch}: validation_loss = {val_loss:.4f}")

    return results


# Create datasets
print("Creating datasets...")
train_synthetic = SyntheticTextDataset(num_samples=3000, seq_len=32, vocab_size=100)
val_synthetic = SyntheticTextDataset(num_samples=500, seq_len=32, vocab_size=100)

print("Loading WikiText-2...")
train_wiki, val_wiki = load_wikitext_dataset(
    num_samples=3000, seq_len=32, vocab_size=100
)

print("Loading AG News...")
train_agnews, val_agnews = load_agnews_dataset(
    num_samples=3000, seq_len=32, vocab_size=100
)

datasets = [
    ("Synthetic", train_synthetic, val_synthetic),
    ("WikiText-2", train_wiki, val_wiki),
    ("AG_News", train_agnews, val_agnews),
]

experiment_data = {}
for dataset_name, train_ds, val_ds in datasets:
    results = run_experiment(
        train_ds,
        val_ds,
        dataset_name,
        num_epochs=15,
        batch_size=32,
        lr=5e-4,
        sample_ratio=0.7,
    )
    experiment_data[dataset_name] = results

# Print summary
print("\n" + "=" * 60)
print("FINAL RESULTS SUMMARY")
print("=" * 60)

for dataset_name in experiment_data:
    print(f"\n{dataset_name}:")
    pada_final = experiment_data[dataset_name]["pada"]["losses"]["val"][-1]
    random_final = experiment_data[dataset_name]["random"]["losses"]["val"][-1]
    full_final = experiment_data[dataset_name]["full"]["losses"]["val"][-1]
    pada_eff = experiment_data[dataset_name]["pada"]["sample_efficiency"][-1]
    print(f"  PADA   - Val Loss: {pada_final:.4f}, Efficiency: {pada_eff:.6f}")
    print(f"  Random - Val Loss: {random_final:.4f}")
    print(f"  Full   - Val Loss: {full_final:.4f}")

    # Calculate sample_efficiency_ratio
    pada_perf = 1.0 / pada_final
    full_perf = 1.0 / full_final
    perf_ratio = pada_perf / full_perf
    sample_fraction = 0.7
    sample_efficiency_ratio = perf_ratio / sample_fraction
    print(f"  sample_efficiency_ratio (PADA): {sample_efficiency_ratio:.4f}")

# Plotting
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

for i, dataset_name in enumerate(experiment_data):
    ax = axes[0, i]
    ax.plot(
        experiment_data[dataset_name]["pada"]["losses"]["val"],
        label="PADA",
        marker="o",
        markersize=3,
    )
    ax.plot(
        experiment_data[dataset_name]["random"]["losses"]["val"],
        label="Random",
        marker="s",
        markersize=3,
    )
    ax.plot(
        experiment_data[dataset_name]["full"]["losses"]["val"],
        label="Full",
        marker="^",
        markersize=3,
    )
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Validation Loss")
    ax.set_title(f"{dataset_name}: Validation Loss")
    ax.legend()
    ax.grid(True)

for i, dataset_name in enumerate(experiment_data):
    ax = axes[1, i]
    ax.plot(
        experiment_data[dataset_name]["pada"]["sample_efficiency"],
        label="PADA",
        marker="o",
        markersize=3,
    )
    ax.plot(
        experiment_data[dataset_name]["random"]["sample_efficiency"],
        label="Random",
        marker="s",
        markersize=3,
    )
    ax.plot(
        experiment_data[dataset_name]["full"]["sample_efficiency"],
        label="Full",
        marker="^",
        markersize=3,
    )
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Sample Efficiency")
    ax.set_title(f"{dataset_name}: Sample Efficiency")
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "multi_dataset_results.png"), dpi=150)
plt.close()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nResults saved to {working_dir}")
