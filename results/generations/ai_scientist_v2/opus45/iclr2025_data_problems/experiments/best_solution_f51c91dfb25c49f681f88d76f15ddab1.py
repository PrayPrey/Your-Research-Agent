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

# Set seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# Experiment data storage
experiment_data = {
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


# Synthetic dataset: simple pattern sequences
class SyntheticTextDataset(Dataset):
    def __init__(self, num_samples=5000, seq_len=32, vocab_size=100):
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.data = []

        for i in range(num_samples):
            pattern_type = i % 5
            seq = np.zeros(seq_len, dtype=np.int64)

            if pattern_type == 0:  # Arithmetic sequence
                start = np.random.randint(0, vocab_size - seq_len)
                seq = np.arange(start, start + seq_len) % vocab_size
            elif pattern_type == 1:  # Repeating pattern
                pattern_len = np.random.randint(2, 6)
                pattern = np.random.randint(0, vocab_size, pattern_len)
                seq = np.tile(pattern, seq_len // pattern_len + 1)[:seq_len]
            elif pattern_type == 2:  # Random with structure
                base = np.random.randint(0, vocab_size // 2)
                seq = np.random.randint(base, base + vocab_size // 2, seq_len)
            elif pattern_type == 3:  # Fibonacci-like
                seq[0] = np.random.randint(1, 10)
                seq[1] = np.random.randint(1, 10)
                for j in range(2, seq_len):
                    seq[j] = (seq[j - 1] + seq[j - 2]) % vocab_size
            else:  # Pure noise (harder samples)
                seq = np.random.randint(0, vocab_size, seq_len)

            self.data.append(seq)

        self.data = np.array(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        seq = self.data[idx]
        return {"input_ids": torch.tensor(seq[:-1]), "labels": torch.tensor(seq[1:])}


# Small Transformer Model
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


# Phase Detector
class PhaseDetector:
    def __init__(self, window_size=5):
        self.val_losses = deque(maxlen=window_size)
        self.window_size = window_size

    def update(self, val_loss):
        self.val_losses.append(val_loss)

    def get_phase(self):
        if len(self.val_losses) < 3:
            return "memorization"

        losses = list(self.val_losses)
        recent_trend = losses[-1] - losses[-3] if len(losses) >= 3 else 0
        avg_improvement = (
            (losses[0] - losses[-1]) / len(losses) if len(losses) > 1 else 0
        )

        if len(losses) < self.window_size:
            return "memorization"
        elif abs(recent_trend) > 0.1 * abs(avg_improvement) and recent_trend < 0:
            return "generalization"
        else:
            return "refinement"


# PADA Sampler
class PADASampler:
    def __init__(self, model, dataset, sample_ratio=0.7):
        self.model = model
        self.dataset = dataset
        self.sample_ratio = sample_ratio
        self.gradient_cache = {}
        self.uncertainty_cache = {}

    def compute_sample_scores(self, indices, phase):
        """Compute scores for sample selection based on current phase"""
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

                # Compute gradient norm as attribution signal
                loss.backward()
                grad_norm = 0
                for p in self.model.parameters():
                    if p.grad is not None:
                        grad_norm += p.grad.norm().item() ** 2
                grad_norm = math.sqrt(grad_norm)

            # Compute uncertainty (entropy of predictions)
            with torch.no_grad():
                probs = F.softmax(output, dim=-1)
                entropy = -(probs * torch.log(probs + 1e-10)).sum(dim=-1).mean().item()

            self.gradient_cache[idx] = grad_norm
            self.uncertainty_cache[idx] = entropy

            if phase == "memorization":
                # High gradient, diverse samples
                score = grad_norm
            elif phase == "generalization":
                # Boundary cases (medium gradient, medium uncertainty)
                score = 1.0 / (
                    1.0 + abs(grad_norm - np.median(list(self.gradient_cache.values())))
                )
            else:  # refinement
                # High uncertainty samples
                score = entropy

            scores.append(score)

        self.model.train()
        return np.array(scores)

    def select_samples(self, phase, num_samples=None):
        """Select samples based on phase-specific criteria"""
        all_indices = list(range(len(self.dataset)))

        if num_samples is None:
            num_samples = int(len(all_indices) * self.sample_ratio)

        # Subsample for efficiency in scoring
        score_subset = np.random.choice(
            all_indices, min(500, len(all_indices)), replace=False
        )
        scores = self.compute_sample_scores(score_subset, phase)

        # Select top scoring samples
        sorted_indices = np.argsort(scores)[::-1]
        selected = score_subset[sorted_indices[:num_samples]]

        # Add some random samples for diversity
        remaining = list(set(all_indices) - set(selected))
        if remaining and num_samples < len(all_indices):
            extra = np.random.choice(
                remaining, min(num_samples // 5, len(remaining)), replace=False
            )
            selected = np.concatenate([selected, extra])

        return selected[:num_samples]


def evaluate(model, dataloader):
    model.eval()
    total_loss = 0
    total_samples = 0

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)

            output = model(input_ids)
            loss = F.cross_entropy(output.view(-1, output.size(-1)), labels.view(-1))
            total_loss += loss.item() * input_ids.size(0)
            total_samples += input_ids.size(0)

    return total_loss / total_samples


def train_epoch(model, optimizer, dataloader):
    model.train()
    total_loss = 0
    total_samples = 0

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

    return total_loss / total_samples, total_samples


# Create datasets
print("Creating datasets...")
train_dataset = SyntheticTextDataset(num_samples=3000, seq_len=32, vocab_size=100)
val_dataset = SyntheticTextDataset(num_samples=500, seq_len=32, vocab_size=100)

val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

# Training parameters
num_epochs = 20
batch_size = 32
lr = 1e-3

# Training with PADA
print("\n=== Training with PADA ===")
model_pada = SmallTransformer().to(device)
optimizer_pada = torch.optim.Adam(model_pada.parameters(), lr=lr)
phase_detector = PhaseDetector(window_size=5)
pada_sampler = PADASampler(model_pada, train_dataset, sample_ratio=0.6)

initial_val_loss_pada = evaluate(model_pada, val_loader)
total_samples_pada = 0

for epoch in range(num_epochs):
    # Detect phase and select samples
    phase = phase_detector.get_phase()
    selected_indices = pada_sampler.select_samples(
        phase, num_samples=int(len(train_dataset) * 0.6)
    )

    subset = Subset(train_dataset, selected_indices)
    train_loader = DataLoader(subset, batch_size=batch_size, shuffle=True)

    train_loss, samples_used = train_epoch(model_pada, optimizer_pada, train_loader)
    total_samples_pada += samples_used

    val_loss = evaluate(model_pada, val_loader)
    phase_detector.update(val_loss)

    # Calculate sample efficiency
    loss_improvement = initial_val_loss_pada - val_loss
    sample_efficiency = (
        loss_improvement / total_samples_pada if total_samples_pada > 0 else 0
    )

    experiment_data["pada"]["losses"]["train"].append(train_loss)
    experiment_data["pada"]["losses"]["val"].append(val_loss)
    experiment_data["pada"]["samples_used"].append(total_samples_pada)
    experiment_data["pada"]["phases"].append(phase)
    experiment_data["pada"]["sample_efficiency"].append(sample_efficiency)

    print(
        f"Epoch {epoch}: validation_loss = {val_loss:.4f}, phase = {phase}, samples_used = {total_samples_pada}"
    )

# Training with Random Selection (same sample ratio)
print("\n=== Training with Random Selection ===")
model_random = SmallTransformer().to(device)
optimizer_random = torch.optim.Adam(model_random.parameters(), lr=lr)

initial_val_loss_random = evaluate(model_random, val_loader)
total_samples_random = 0

for epoch in range(num_epochs):
    # Random selection
    selected_indices = np.random.choice(
        len(train_dataset), int(len(train_dataset) * 0.6), replace=False
    )
    subset = Subset(train_dataset, selected_indices)
    train_loader = DataLoader(subset, batch_size=batch_size, shuffle=True)

    train_loss, samples_used = train_epoch(model_random, optimizer_random, train_loader)
    total_samples_random += samples_used

    val_loss = evaluate(model_random, val_loader)

    loss_improvement = initial_val_loss_random - val_loss
    sample_efficiency = (
        loss_improvement / total_samples_random if total_samples_random > 0 else 0
    )

    experiment_data["random"]["losses"]["train"].append(train_loss)
    experiment_data["random"]["losses"]["val"].append(val_loss)
    experiment_data["random"]["samples_used"].append(total_samples_random)
    experiment_data["random"]["sample_efficiency"].append(sample_efficiency)

    print(
        f"Epoch {epoch}: validation_loss = {val_loss:.4f}, samples_used = {total_samples_random}"
    )

# Training with Full Data
print("\n=== Training with Full Data ===")
model_full = SmallTransformer().to(device)
optimizer_full = torch.optim.Adam(model_full.parameters(), lr=lr)

initial_val_loss_full = evaluate(model_full, val_loader)
total_samples_full = 0

train_loader_full = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

for epoch in range(num_epochs):
    train_loss, samples_used = train_epoch(
        model_full, optimizer_full, train_loader_full
    )
    total_samples_full += samples_used

    val_loss = evaluate(model_full, val_loader)

    loss_improvement = initial_val_loss_full - val_loss
    sample_efficiency = (
        loss_improvement / total_samples_full if total_samples_full > 0 else 0
    )

    experiment_data["full"]["losses"]["train"].append(train_loss)
    experiment_data["full"]["losses"]["val"].append(val_loss)
    experiment_data["full"]["samples_used"].append(total_samples_full)
    experiment_data["full"]["sample_efficiency"].append(sample_efficiency)

    print(
        f"Epoch {epoch}: validation_loss = {val_loss:.4f}, samples_used = {total_samples_full}"
    )

# Final Results
print("\n=== Final Results ===")
final_pada_efficiency = experiment_data["pada"]["sample_efficiency"][-1]
final_random_efficiency = experiment_data["random"]["sample_efficiency"][-1]
final_full_efficiency = experiment_data["full"]["sample_efficiency"][-1]

print(
    f"PADA - Final Val Loss: {experiment_data['pada']['losses']['val'][-1]:.4f}, "
    f"Total Samples: {experiment_data['pada']['samples_used'][-1]}, "
    f"Sample Efficiency: {final_pada_efficiency:.6f}"
)
print(
    f"Random - Final Val Loss: {experiment_data['random']['losses']['val'][-1]:.4f}, "
    f"Total Samples: {experiment_data['random']['samples_used'][-1]}, "
    f"Sample Efficiency: {final_random_efficiency:.6f}"
)
print(
    f"Full - Final Val Loss: {experiment_data['full']['losses']['val'][-1]:.4f}, "
    f"Total Samples: {experiment_data['full']['samples_used'][-1]}, "
    f"Sample Efficiency: {final_full_efficiency:.6f}"
)

print(f"\n*** sample_efficiency_ratio (PADA): {final_pada_efficiency:.6f} ***")

# Plotting
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Validation Loss over Epochs
ax1 = axes[0, 0]
ax1.plot(experiment_data["pada"]["losses"]["val"], label="PADA", marker="o")
ax1.plot(experiment_data["random"]["losses"]["val"], label="Random", marker="s")
ax1.plot(experiment_data["full"]["losses"]["val"], label="Full Data", marker="^")
ax1.set_xlabel("Epoch")
ax1.set_ylabel("Validation Loss")
ax1.set_title("Validation Loss Comparison")
ax1.legend()
ax1.grid(True)

# Validation Loss vs Samples Used
ax2 = axes[0, 1]
ax2.plot(
    experiment_data["pada"]["samples_used"],
    experiment_data["pada"]["losses"]["val"],
    label="PADA",
    marker="o",
)
ax2.plot(
    experiment_data["random"]["samples_used"],
    experiment_data["random"]["losses"]["val"],
    label="Random",
    marker="s",
)
ax2.plot(
    experiment_data["full"]["samples_used"],
    experiment_data["full"]["losses"]["val"],
    label="Full Data",
    marker="^",
)
ax2.set_xlabel("Total Samples Used")
ax2.set_ylabel("Validation Loss")
ax2.set_title("Sample Efficiency: Val Loss vs Samples")
ax2.legend()
ax2.grid(True)

# Sample Efficiency over Time
ax3 = axes[1, 0]
ax3.plot(experiment_data["pada"]["sample_efficiency"], label="PADA", marker="o")
ax3.plot(experiment_data["random"]["sample_efficiency"], label="Random", marker="s")
ax3.plot(experiment_data["full"]["sample_efficiency"], label="Full Data", marker="^")
ax3.set_xlabel("Epoch")
ax3.set_ylabel("Sample Efficiency Ratio")
ax3.set_title("Sample Efficiency Over Training")
ax3.legend()
ax3.grid(True)

# Phase Distribution for PADA
ax4 = axes[1, 1]
phases = experiment_data["pada"]["phases"]
phase_counts = {
    "memorization": phases.count("memorization"),
    "generalization": phases.count("generalization"),
    "refinement": phases.count("refinement"),
}
ax4.bar(phase_counts.keys(), phase_counts.values(), color=["blue", "green", "orange"])
ax4.set_xlabel("Phase")
ax4.set_ylabel("Epochs")
ax4.set_title("PADA Phase Distribution")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pada_comparison_results.png"), dpi=150)
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print(f"\nResults saved to {working_dir}")
print(f"Plot saved as pada_comparison_results.png")
