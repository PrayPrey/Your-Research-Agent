import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import time

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# Experiment data storage
experiment_data = {
    "synthetic_classification": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "sparsity": {"train": [], "val": []},
        "sparsity_adjusted_accuracy": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "epoch_times": [],
    }
}


# ============ Synthetic Dataset ============
class SyntheticClassificationDataset(Dataset):
    def __init__(self, num_samples=1000, seq_len=32, hidden_dim=128, num_classes=2):
        self.num_samples = num_samples
        self.seq_len = seq_len
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes

        # Generate synthetic data with structure
        # Task: classify based on mean of specific feature dimensions
        self.data = torch.randn(num_samples, seq_len, hidden_dim)

        # Create labels based on specific feature dimensions (task-specific pattern)
        # Only dimensions 0-31 are relevant, others are noise
        relevant_features = self.data[:, :, :32].mean(dim=(1, 2))
        self.labels = (relevant_features > 0).long()

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return {"input": self.data[idx], "label": self.labels[idx]}


# ============ LoRA Module ============
class LoRALayer(nn.Module):
    def __init__(self, in_features, out_features, rank=8):
        super().__init__()
        self.rank = rank
        self.lora_A = nn.Parameter(torch.randn(in_features, rank) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(rank, out_features))
        self.scaling = 0.5

    def forward(self, x):
        return (x @ self.lora_A @ self.lora_B) * self.scaling


# ============ Gumbel-Softmax Routing Gate ============
class GumbelRoutingGate(nn.Module):
    def __init__(self, num_units, temperature=1.0):
        super().__init__()
        self.num_units = num_units
        self.temperature = temperature
        # Learnable routing logits (initialize to favor keeping units)
        self.routing_logits = nn.Parameter(torch.ones(num_units))

    def forward(self, x, training=True):
        if training:
            # Gumbel-Softmax for differentiable sampling
            # Create binary choice: keep or drop
            logits = torch.stack(
                [self.routing_logits, torch.zeros_like(self.routing_logits)], dim=-1
            )

            # Add Gumbel noise
            uniform = torch.rand_like(logits)
            gumbel = -torch.log(-torch.log(uniform + 1e-10) + 1e-10)
            logits_with_noise = (logits + gumbel) / self.temperature

            # Softmax and take "keep" probability
            soft_mask = F.softmax(logits_with_noise, dim=-1)[..., 0]

            # Straight-through estimator for hard mask
            hard_mask = (soft_mask > 0.5).float()
            mask = hard_mask - soft_mask.detach() + soft_mask
        else:
            # During inference, use hard threshold
            mask = (torch.sigmoid(self.routing_logits) > 0.5).float()

        # Apply mask
        if len(x.shape) == 3:  # (batch, seq, features)
            mask = mask.unsqueeze(0).unsqueeze(0)
        elif len(x.shape) == 2:  # (batch, features)
            mask = mask.unsqueeze(0)

        return x * mask, mask

    def get_sparsity(self):
        """Return fraction of pruned units"""
        with torch.no_grad():
            active = (torch.sigmoid(self.routing_logits) > 0.5).float()
            return 1.0 - active.mean().item()


# ============ Sparse-Routing FFN with LoRA ============
class SparseRoutingFFN(nn.Module):
    def __init__(self, hidden_dim, intermediate_dim, lora_rank=8, use_routing=True):
        super().__init__()
        self.use_routing = use_routing

        # Original frozen layers
        self.fc1 = nn.Linear(hidden_dim, intermediate_dim)
        self.fc2 = nn.Linear(intermediate_dim, hidden_dim)

        # LoRA adapters
        self.lora1 = LoRALayer(hidden_dim, intermediate_dim, rank=lora_rank)
        self.lora2 = LoRALayer(intermediate_dim, hidden_dim, rank=lora_rank)

        # Routing gates
        if use_routing:
            self.routing_gate1 = GumbelRoutingGate(intermediate_dim)
            self.routing_gate2 = GumbelRoutingGate(hidden_dim)

        # Freeze original weights
        for param in [self.fc1.weight, self.fc1.bias, self.fc2.weight, self.fc2.bias]:
            param.requires_grad = False

    def forward(self, x, training=True):
        # First layer with LoRA
        h = self.fc1(x) + self.lora1(x)
        h = F.gelu(h)

        # Apply routing
        masks = []
        if self.use_routing:
            h, mask1 = self.routing_gate1(h, training=training)
            masks.append(mask1)

        # Second layer with LoRA
        out = self.fc2(h) + self.lora2(h)

        if self.use_routing:
            out, mask2 = self.routing_gate2(out, training=training)
            masks.append(mask2)

        return out, masks


# ============ Simple Transformer with SR-PEFT ============
class SimpleTransformerWithSRPEFT(nn.Module):
    def __init__(
        self,
        hidden_dim=128,
        num_layers=2,
        num_classes=2,
        intermediate_dim=256,
        lora_rank=8,
        use_routing=True,
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.use_routing = use_routing

        # Simple transformer layers
        self.layers = nn.ModuleList(
            [
                SparseRoutingFFN(hidden_dim, intermediate_dim, lora_rank, use_routing)
                for _ in range(num_layers)
            ]
        )

        # Classifier head
        self.classifier = nn.Linear(hidden_dim, num_classes)

    def forward(self, x, training=True):
        # x: (batch, seq_len, hidden_dim)
        all_masks = []

        for layer in self.layers:
            residual = x
            out, masks = layer(x, training=training)
            x = residual + out
            all_masks.extend(masks)

        # Pool over sequence dimension
        x = x.mean(dim=1)

        # Classify
        logits = self.classifier(x)

        return logits, all_masks

    def get_total_sparsity(self):
        """Compute average sparsity across all routing gates"""
        if not self.use_routing:
            return 0.0

        sparsities = []
        for layer in self.layers:
            if hasattr(layer, "routing_gate1"):
                sparsities.append(layer.routing_gate1.get_sparsity())
            if hasattr(layer, "routing_gate2"):
                sparsities.append(layer.routing_gate2.get_sparsity())

        return np.mean(sparsities) if sparsities else 0.0


# ============ Training Function ============
def train_epoch(model, dataloader, optimizer, sparsity_weight=0.01, training=True):
    model.train() if training else model.eval()

    total_loss = 0.0
    total_correct = 0
    total_samples = 0
    total_sparsity = 0.0

    for batch in dataloader:
        inputs = batch["input"].to(device)
        labels = batch["label"].to(device)

        if training:
            optimizer.zero_grad()

        # Forward pass
        with torch.set_grad_enabled(training):
            logits, masks = model(inputs, training=training)

            # Task loss
            task_loss = F.cross_entropy(logits, labels)

            # Sparsity regularization (encourage pruning)
            sparsity_loss = 0.0
            if model.use_routing and len(masks) > 0:
                for mask in masks:
                    # Encourage sparsity by penalizing active units
                    if mask.numel() > 0:
                        sparsity_loss += mask.mean()
                sparsity_loss = sparsity_loss / len(masks)

            # Total loss
            loss = task_loss + sparsity_weight * sparsity_loss

            if training:
                loss.backward()
                optimizer.step()

        # Metrics
        total_loss += loss.item() * inputs.size(0)
        preds = logits.argmax(dim=1)
        total_correct += (preds == labels).sum().item()
        total_samples += inputs.size(0)

    avg_loss = total_loss / total_samples
    accuracy = total_correct / total_samples
    sparsity = model.get_total_sparsity()

    return avg_loss, accuracy, sparsity


# ============ Main Training Loop ============
def main():
    print("=" * 50)
    print("Sparse-Routing PEFT Baseline Implementation")
    print("=" * 50)

    # Hyperparameters
    hidden_dim = 128
    num_layers = 2
    intermediate_dim = 256
    lora_rank = 8
    num_classes = 2
    batch_size = 32
    num_epochs = 20
    learning_rate = 1e-3
    sparsity_weight_stage1 = 0.001  # Weak sparsity encouragement
    sparsity_weight_stage2 = 0.01  # Strong sparsity encouragement

    # Create datasets
    print("\nCreating synthetic datasets...")
    train_dataset = SyntheticClassificationDataset(
        num_samples=800, seq_len=32, hidden_dim=hidden_dim, num_classes=num_classes
    )
    val_dataset = SyntheticClassificationDataset(
        num_samples=200, seq_len=32, hidden_dim=hidden_dim, num_classes=num_classes
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # Create models: one with routing, one baseline without
    print("\nInitializing models...")
    model_with_routing = SimpleTransformerWithSRPEFT(
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        num_classes=num_classes,
        intermediate_dim=intermediate_dim,
        lora_rank=lora_rank,
        use_routing=True,
    ).to(device)

    print(
        f"Model parameters: {sum(p.numel() for p in model_with_routing.parameters() if p.requires_grad):,}"
    )

    # Optimizer
    optimizer = torch.optim.AdamW(
        [p for p in model_with_routing.parameters() if p.requires_grad],
        lr=learning_rate,
    )

    # Two-stage training
    print("\n" + "=" * 50)
    print("Stage 1: Learning task representations (weak sparsity)")
    print("=" * 50)

    stage1_epochs = num_epochs // 2
    stage2_epochs = num_epochs - stage1_epochs

    for epoch in range(stage1_epochs):
        start_time = time.time()

        # Train
        train_loss, train_acc, train_sparsity = train_epoch(
            model_with_routing,
            train_loader,
            optimizer,
            sparsity_weight=sparsity_weight_stage1,
            training=True,
        )

        # Validate
        val_loss, val_acc, val_sparsity = train_epoch(
            model_with_routing,
            val_loader,
            optimizer,
            sparsity_weight=sparsity_weight_stage1,
            training=False,
        )

        epoch_time = time.time() - start_time

        # Compute sparsity-adjusted accuracy
        train_spa = train_acc * (1 + train_sparsity)
        val_spa = val_acc * (1 + val_sparsity)

        # Store metrics
        experiment_data["synthetic_classification"]["losses"]["train"].append(
            train_loss
        )
        experiment_data["synthetic_classification"]["losses"]["val"].append(val_loss)
        experiment_data["synthetic_classification"]["metrics"]["train"].append(
            train_acc
        )
        experiment_data["synthetic_classification"]["metrics"]["val"].append(val_acc)
        experiment_data["synthetic_classification"]["sparsity"]["train"].append(
            train_sparsity
        )
        experiment_data["synthetic_classification"]["sparsity"]["val"].append(
            val_sparsity
        )
        experiment_data["synthetic_classification"]["sparsity_adjusted_accuracy"][
            "train"
        ].append(train_spa)
        experiment_data["synthetic_classification"]["sparsity_adjusted_accuracy"][
            "val"
        ].append(val_spa)
        experiment_data["synthetic_classification"]["epoch_times"].append(epoch_time)

        print(
            f"Epoch {epoch+1}/{stage1_epochs}: "
            f"train_loss={train_loss:.4f}, train_acc={train_acc:.4f}, train_sparsity={train_sparsity:.3f}, "
            f"val_loss={val_loss:.4f}, val_acc={val_acc:.4f}, val_sparsity={val_sparsity:.3f}, "
            f"val_spa={val_spa:.4f}, time={epoch_time:.2f}s"
        )

    print("\n" + "=" * 50)
    print("Stage 2: Optimizing routing under compute budgets (strong sparsity)")
    print("=" * 50)

    for epoch in range(stage2_epochs):
        start_time = time.time()

        # Train
        train_loss, train_acc, train_sparsity = train_epoch(
            model_with_routing,
            train_loader,
            optimizer,
            sparsity_weight=sparsity_weight_stage2,
            training=True,
        )

        # Validate
        val_loss, val_acc, val_sparsity = train_epoch(
            model_with_routing,
            val_loader,
            optimizer,
            sparsity_weight=sparsity_weight_stage2,
            training=False,
        )

        epoch_time = time.time() - start_time

        # Compute sparsity-adjusted accuracy
        train_spa = train_acc * (1 + train_sparsity)
        val_spa = val_acc * (1 + val_sparsity)

        # Store metrics
        experiment_data["synthetic_classification"]["losses"]["train"].append(
            train_loss
        )
        experiment_data["synthetic_classification"]["losses"]["val"].append(val_loss)
        experiment_data["synthetic_classification"]["metrics"]["train"].append(
            train_acc
        )
        experiment_data["synthetic_classification"]["metrics"]["val"].append(val_acc)
        experiment_data["synthetic_classification"]["sparsity"]["train"].append(
            train_sparsity
        )
        experiment_data["synthetic_classification"]["sparsity"]["val"].append(
            val_sparsity
        )
        experiment_data["synthetic_classification"]["sparsity_adjusted_accuracy"][
            "train"
        ].append(train_spa)
        experiment_data["synthetic_classification"]["sparsity_adjusted_accuracy"][
            "val"
        ].append(val_spa)
        experiment_data["synthetic_classification"]["epoch_times"].append(epoch_time)

        total_epoch = stage1_epochs + epoch + 1
        print(
            f"Epoch {total_epoch}/{num_epochs}: "
            f"train_loss={train_loss:.4f}, train_acc={train_acc:.4f}, train_sparsity={train_sparsity:.3f}, "
            f"val_loss={val_loss:.4f}, val_acc={val_acc:.4f}, val_sparsity={val_sparsity:.3f}, "
            f"val_spa={val_spa:.4f}, time={epoch_time:.2f}s"
        )

    # Final evaluation and predictions
    print("\n" + "=" * 50)
    print("Final Evaluation")
    print("=" * 50)

    model_with_routing.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in val_loader:
            inputs = batch["input"].to(device)
            labels = batch["label"].to(device)

            logits, _ = model_with_routing(inputs, training=False)
            preds = logits.argmax(dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    experiment_data["synthetic_classification"]["predictions"] = all_preds
    experiment_data["synthetic_classification"]["ground_truth"] = all_labels

    final_val_acc = np.mean(np.array(all_preds) == np.array(all_labels))
    final_sparsity = model_with_routing.get_total_sparsity()
    final_spa = final_val_acc * (1 + final_sparsity)

    print(f"\nFinal Results:")
    print(f"  Validation Accuracy: {final_val_acc:.4f}")
    print(
        f"  Achieved Sparsity: {final_sparsity:.4f} ({final_sparsity*100:.1f}% parameters pruned)"
    )
    print(f"  Sparsity-Adjusted Accuracy: {final_spa:.4f}")
    print(f"  Inference Speedup (theoretical): {1/(1-final_sparsity):.2f}x")

    # Visualization
    print("\nGenerating visualizations...")

    # Plot 1: Training curves
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    epochs_range = range(1, num_epochs + 1)

    # Loss
    axes[0, 0].plot(
        epochs_range,
        experiment_data["synthetic_classification"]["losses"]["train"],
        label="Train",
        marker="o",
        markersize=3,
    )
    axes[0, 0].plot(
        epochs_range,
        experiment_data["synthetic_classification"]["losses"]["val"],
        label="Val",
        marker="s",
        markersize=3,
    )
    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].set_ylabel("Loss")
    axes[0, 0].set_title("Training and Validation Loss")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Accuracy
    axes[0, 1].plot(
        epochs_range,
        experiment_data["synthetic_classification"]["metrics"]["train"],
        label="Train",
        marker="o",
        markersize=3,
    )
    axes[0, 1].plot(
        epochs_range,
        experiment_data["synthetic_classification"]["metrics"]["val"],
        label="Val",
        marker="s",
        markersize=3,
    )
    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].set_ylabel("Accuracy")
    axes[0, 1].set_title("Training and Validation Accuracy")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Sparsity evolution
    axes[1, 0].plot(
        epochs_range,
        experiment_data["synthetic_classification"]["sparsity"]["train"],
        label="Train",
        marker="o",
        markersize=3,
    )
    axes[1, 0].plot(
        epochs_range,
        experiment_data["synthetic_classification"]["sparsity"]["val"],
        label="Val",
        marker="s",
        markersize=3,
    )
    axes[1, 0].axvline(
        x=stage1_epochs, color="red", linestyle="--", alpha=0.5, label="Stage 2 Start"
    )
    axes[1, 0].set_xlabel("Epoch")
    axes[1, 0].set_ylabel("Sparsity Ratio")
    axes[1, 0].set_title("Learned Sparsity Over Time")
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Sparsity-Adjusted Accuracy
    axes[1, 1].plot(
        epochs_range,
        experiment_data["synthetic_classification"]["sparsity_adjusted_accuracy"][
            "train"
        ],
        label="Train",
        marker="o",
        markersize=3,
    )
    axes[1, 1].plot(
        epochs_range,
        experiment_data["synthetic_classification"]["sparsity_adjusted_accuracy"][
            "val"
        ],
        label="Val",
        marker="s",
        markersize=3,
    )
    axes[1, 1].axhline(
        y=1.0, color="green", linestyle="--", alpha=0.5, label="Target (1.0)"
    )
    axes[1, 1].set_xlabel("Epoch")
    axes[1, 1].set_ylabel("Sparsity-Adjusted Accuracy")
    axes[1, 1].set_title("Composite Metric: Accuracy × (1 + Sparsity)")
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, "training_curves_synthetic.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # Plot 2: Accuracy vs Sparsity trade-off
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    val_accs = experiment_data["synthetic_classification"]["metrics"]["val"]
    val_sparsities = experiment_data["synthetic_classification"]["sparsity"]["val"]

    scatter = ax.scatter(
        val_sparsities,
        val_accs,
        c=range(len(val_accs)),
        cmap="viridis",
        s=100,
        alpha=0.7,
        edgecolors="black",
        linewidth=0.5,
    )
    ax.plot(val_sparsities, val_accs, "k--", alpha=0.3, linewidth=1)

    ax.set_xlabel("Sparsity Ratio (fraction pruned)", fontsize=12)
    ax.set_ylabel("Validation Accuracy", fontsize=12)
    ax.set_title("Accuracy vs Sparsity Trade-off", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Epoch", fontsize=10)

    # Annotate first and last points
    ax.annotate(
        "Start",
        (val_sparsities[0], val_accs[0]),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=10,
        color="red",
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
    )
    ax.annotate(
        "End",
        (val_sparsities[-1], val_accs[-1]),
        xytext=(10, -15),
        textcoords="offset points",
        fontsize=10,
        color="blue",
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="blue", lw=1.5),
    )

    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, "accuracy_vs_sparsity_synthetic.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # Save experiment data
    print("\nSaving experiment data...")
    np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

    print("\n" + "=" * 50)
    print("Experiment completed successfully!")
    print(f"Results saved to: {working_dir}")
    print("=" * 50)

    return final_spa


# Run the main experiment
final_metric = main()
print(f"\nFinal Sparsity-Adjusted Accuracy: {final_metric:.4f}")
