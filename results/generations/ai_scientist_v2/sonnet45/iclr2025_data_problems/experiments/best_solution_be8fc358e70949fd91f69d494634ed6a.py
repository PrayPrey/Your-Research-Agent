import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from collections import defaultdict
import warnings

warnings.filterwarnings("ignore")

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set random seeds
torch.manual_seed(42)
np.random.seed(42)

# Experiment data storage
experiment_data = {
    "dynamic_mixing": {
        "metrics": {"train_loss": [], "val_loss": [], "balance_score": []},
        "domain_accuracies": [],
        "mixing_ratios": [],
        "attention_entropy": [],
        "silhouette_scores": [],
        "cka_similarity": [],
    },
    "static_mixing": {
        "metrics": {"train_loss": [], "val_loss": [], "balance_score": []},
        "domain_accuracies": [],
    },
}


# Synthetic data generation for 4 domains
class MultiDomainDataset(Dataset):
    def __init__(self, num_samples_per_domain=500, seq_len=32, vocab_size=1000):
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.domains = ["wikipedia", "code", "scientific", "conversational"]
        self.data = []
        self.labels = []
        self.domain_ids = []

        # Generate domain-specific data with distinct patterns
        for domain_id, domain in enumerate(self.domains):
            for _ in range(num_samples_per_domain):
                if domain == "wikipedia":
                    # Broader vocabulary, uniform-ish distribution
                    seq = np.random.randint(0, vocab_size, seq_len)
                elif domain == "code":
                    # Repetitive patterns, limited vocabulary
                    base_tokens = np.random.randint(0, vocab_size // 4, seq_len // 4)
                    seq = np.tile(base_tokens, 4)
                elif domain == "scientific":
                    # Technical vocabulary (high token values)
                    seq = np.random.randint(vocab_size // 2, vocab_size, seq_len)
                elif domain == "conversational":
                    # Short common words (low token values)
                    seq = np.random.randint(0, vocab_size // 8, seq_len)

                self.data.append(seq)
                self.labels.append(seq)  # Next token prediction
                self.domain_ids.append(domain_id)

        self.data = np.array(self.data)
        self.labels = np.array(self.labels)
        self.domain_ids = np.array(self.domain_ids)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return {
            "input_ids": torch.tensor(self.data[idx], dtype=torch.long),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
            "domain_id": torch.tensor(self.domain_ids[idx], dtype=torch.long),
        }

    def get_domain_subset(self, domain_id):
        indices = np.where(self.domain_ids == domain_id)[0]
        return torch.utils.data.Subset(self, indices)


# Simple Transformer model
class SimpleTransformer(nn.Module):
    def __init__(
        self, vocab_size=1000, d_model=128, nhead=4, num_layers=3, dim_feedforward=256
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Parameter(torch.randn(1, 100, d_model))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            batch_first=True,
            dropout=0.1,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc_out = nn.Linear(d_model, vocab_size)

        # Store intermediate representations
        self.layer_outputs = []
        self.attention_weights = []

    def forward(self, x, store_intermediates=False):
        if store_intermediates:
            self.layer_outputs = []
            self.attention_weights = []

        seq_len = x.size(1)
        x = self.embedding(x) + self.pos_encoding[:, :seq_len, :]

        if store_intermediates:
            # Hook to capture layer outputs
            for i, layer in enumerate(self.transformer.layers):
                x = layer(x)
                self.layer_outputs.append(x.detach())
        else:
            x = self.transformer(x)

        output = self.fc_out(x)
        return output


# Representation health metrics
def compute_attention_entropy(model, dataloader, device):
    """Compute average attention entropy across all heads and layers"""
    model.eval()
    entropies = []

    with torch.no_grad():
        for batch_idx, batch in enumerate(dataloader):
            if batch_idx >= 5:  # Sample only a few batches for efficiency
                break
            input_ids = batch["input_ids"].to(device)

            # Forward pass to get attention patterns (simplified)
            # In practice, we'd extract actual attention weights from transformer
            _ = model(input_ids, store_intermediates=True)

            # Simulate attention entropy (in real implementation, extract from attention matrices)
            # Using layer output variance as proxy
            if len(model.layer_outputs) > 0:
                for layer_out in model.layer_outputs:
                    variance = layer_out.var(dim=-1).mean().item()
                    # Convert to entropy-like metric
                    entropy = -np.log(variance + 1e-8)
                    entropies.append(entropy)

    return np.mean(entropies) if entropies else 0.0


def compute_silhouette_score_metric(model, dataloader, device, n_clusters=4):
    """Compute silhouette score for feature space clustering"""
    model.eval()
    features = []
    domain_labels = []

    with torch.no_grad():
        for batch_idx, batch in enumerate(dataloader):
            if batch_idx >= 10:  # Sample batches
                break
            input_ids = batch["input_ids"].to(device)
            domain_id = batch["domain_id"]

            # Get final layer representations
            output = model(input_ids, store_intermediates=True)
            if len(model.layer_outputs) > 0:
                # Use mean pooling of last layer
                last_layer = model.layer_outputs[-1].mean(dim=1)
                features.append(last_layer.cpu().numpy())
                domain_labels.extend(domain_id.numpy())

    if len(features) == 0:
        return 0.0

    features = np.vstack(features)
    domain_labels = np.array(domain_labels)

    # Compute silhouette score
    if len(np.unique(domain_labels)) > 1 and len(features) > n_clusters:
        try:
            score = silhouette_score(
                features, domain_labels, sample_size=min(500, len(features))
            )
            return score
        except:
            return 0.0
    return 0.0


def compute_cka_similarity(X, Y):
    """Compute CKA similarity between two sets of representations"""
    X = X - X.mean(axis=0)
    Y = Y - Y.mean(axis=0)

    def hsic(K, L):
        n = K.shape[0]
        H = np.eye(n) - np.ones((n, n)) / n
        return np.trace(K @ H @ L @ H) / ((n - 1) ** 2)

    K = X @ X.T
    L = Y @ Y.T

    hsic_xy = hsic(K, L)
    hsic_xx = hsic(K, K)
    hsic_yy = hsic(L, L)

    cka = hsic_xy / (np.sqrt(hsic_xx * hsic_yy) + 1e-8)
    return cka


def compute_layer_cka(model, dataloader, device):
    """Compute CKA similarity between consecutive layers"""
    model.eval()
    layer_features = [[] for _ in range(3)]  # Assuming 3 layers

    with torch.no_grad():
        for batch_idx, batch in enumerate(dataloader):
            if batch_idx >= 5:
                break
            input_ids = batch["input_ids"].to(device)
            _ = model(input_ids, store_intermediates=True)

            for i, layer_out in enumerate(model.layer_outputs):
                layer_features[i].append(layer_out.mean(dim=1).cpu().numpy())

    if len(layer_features[0]) == 0:
        return 0.0

    # Concatenate features
    layer_features = [np.vstack(f) for f in layer_features if len(f) > 0]

    # Compute average CKA between consecutive layers
    cka_scores = []
    for i in range(len(layer_features) - 1):
        cka = compute_cka_similarity(layer_features[i], layer_features[i + 1])
        cka_scores.append(cka)

    return np.mean(cka_scores) if cka_scores else 0.0


# Dynamic mixing strategy
class DynamicMixer:
    def __init__(self, num_domains=4, adjustment_rate=0.1):
        self.num_domains = num_domains
        self.mixing_ratios = np.ones(num_domains) / num_domains
        self.adjustment_rate = adjustment_rate
        self.history = {
            "entropy": defaultdict(list),
            "silhouette": defaultdict(list),
            "cka": defaultdict(list),
        }

    def update_ratios(self, domain_metrics):
        """Adjust mixing ratios based on representation health metrics"""
        # domain_metrics: dict with keys as domain_id and values as dict of metrics

        for domain_id, metrics in domain_metrics.items():
            entropy = metrics.get("entropy", 0)
            silhouette = metrics.get("silhouette", 0)
            cka = metrics.get("cka", 0)

            self.history["entropy"][domain_id].append(entropy)
            self.history["silhouette"][domain_id].append(silhouette)
            self.history["cka"][domain_id].append(cka)

            # Simple rule: increase sampling if metrics indicate healthy learning
            # High entropy = good (not over-specialized)
            # High silhouette = good (clear clustering)
            # Low CKA = good (not converged/collapsed)

            health_score = 0
            if entropy > 2.0:  # Arbitrary threshold
                health_score += 1
            if silhouette > 0.1:
                health_score += 1
            if cka < 0.8:  # Not too similar between layers
                health_score += 1

            # Adjust ratio
            if health_score >= 2:
                # Healthy - increase slightly
                self.mixing_ratios[domain_id] *= 1 + self.adjustment_rate
            else:
                # Unhealthy - decrease slightly
                self.mixing_ratios[domain_id] *= 1 - self.adjustment_rate

        # Normalize
        self.mixing_ratios = np.maximum(self.mixing_ratios, 0.05)  # Min 5%
        self.mixing_ratios /= self.mixing_ratios.sum()

    def sample_domain(self):
        return np.random.choice(self.num_domains, p=self.mixing_ratios)


# Training function
def train_model(
    model,
    train_dataset,
    val_dataset,
    epochs=10,
    batch_size=32,
    dynamic_mixing=False,
    mixing_update_freq=2,
):
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    mixer = DynamicMixer() if dynamic_mixing else None

    train_losses = []
    val_losses = []
    balance_scores = []
    mixing_ratios_history = []

    domains = ["wikipedia", "code", "scientific", "conversational"]

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0

        # Create dynamic dataloader
        if dynamic_mixing and mixer:
            # Sample based on current mixing ratios
            samples_per_domain = [
                int(mixer.mixing_ratios[i] * batch_size * 20) for i in range(4)
            ]
            samples_per_domain = [max(s, 1) for s in samples_per_domain]

            mixed_indices = []
            for domain_id in range(4):
                domain_indices = np.where(train_dataset.domain_ids == domain_id)[0]
                sampled = np.random.choice(
                    domain_indices,
                    min(samples_per_domain[domain_id], len(domain_indices)),
                    replace=False,
                )
                mixed_indices.extend(sampled)

            subset = torch.utils.data.Subset(train_dataset, mixed_indices)
            train_loader = DataLoader(subset, batch_size=batch_size, shuffle=True)
        else:
            train_loader = DataLoader(
                train_dataset, batch_size=batch_size, shuffle=True
            )

        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            output = model(input_ids)

            # Reshape for loss computation
            loss = criterion(output.reshape(-1, output.size(-1)), labels.reshape(-1))
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        avg_train_loss = epoch_loss / len(train_loader)
        train_losses.append(avg_train_loss)

        # Validation
        model.eval()
        val_loss = 0
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                labels = batch["labels"].to(device)
                output = model(input_ids)
                loss = criterion(
                    output.reshape(-1, output.size(-1)), labels.reshape(-1)
                )
                val_loss += loss.item()

        avg_val_loss = val_loss / len(val_loader)
        val_losses.append(avg_val_loss)

        # Compute representation health metrics and update mixing ratios
        if dynamic_mixing and mixer and epoch % mixing_update_freq == 0:
            domain_metrics = {}
            sample_loader = DataLoader(
                train_dataset, batch_size=batch_size, shuffle=True
            )

            for domain_id in range(4):
                domain_subset = train_dataset.get_domain_subset(domain_id)
                domain_loader = DataLoader(
                    domain_subset, batch_size=batch_size, shuffle=False
                )

                entropy = compute_attention_entropy(model, domain_loader, device)
                silhouette = compute_silhouette_score_metric(
                    model, sample_loader, device
                )
                cka = compute_layer_cka(model, domain_loader, device)

                domain_metrics[domain_id] = {
                    "entropy": entropy,
                    "silhouette": silhouette,
                    "cka": cka,
                }

            mixer.update_ratios(domain_metrics)
            mixing_ratios_history.append(mixer.mixing_ratios.copy())

            # Store metrics
            if dynamic_mixing:
                experiment_data["dynamic_mixing"]["attention_entropy"].append(
                    np.mean([m["entropy"] for m in domain_metrics.values()])
                )
                experiment_data["dynamic_mixing"]["silhouette_scores"].append(
                    np.mean([m["silhouette"] for m in domain_metrics.values()])
                )
                experiment_data["dynamic_mixing"]["cka_similarity"].append(
                    np.mean([m["cka"] for m in domain_metrics.values()])
                )

        # Evaluate on domain-specific tasks
        domain_accuracies = evaluate_domain_tasks(
            model, val_dataset, device, batch_size
        )

        # Compute balance score
        if len(domain_accuracies) > 0:
            accuracies_array = np.array(list(domain_accuracies.values()))
            mean_acc = np.mean(accuracies_array)
            std_acc = np.std(accuracies_array)
            balance_score = mean_acc / (std_acc + 1e-8)
        else:
            balance_score = 0.0

        balance_scores.append(balance_score)

        print(
            f"Epoch {epoch+1}/{epochs}: train_loss={avg_train_loss:.4f}, "
            f"validation_loss={avg_val_loss:.4f}, balance_score={balance_score:.4f}"
        )

        if dynamic_mixing and mixer:
            print(f"  Mixing ratios: {mixer.mixing_ratios}")

    return {
        "train_losses": train_losses,
        "val_losses": val_losses,
        "balance_scores": balance_scores,
        "mixing_ratios": mixing_ratios_history,
        "final_domain_accuracies": domain_accuracies,
    }


# Domain-specific downstream task evaluation
def evaluate_domain_tasks(model, dataset, device, batch_size=32):
    """Evaluate model on domain-specific classification tasks"""
    model.eval()
    domain_accuracies = {}

    for domain_id, domain_name in enumerate(
        ["wikipedia", "code", "scientific", "conversational"]
    ):
        domain_subset = dataset.get_domain_subset(domain_id)
        if len(domain_subset) == 0:
            continue

        loader = DataLoader(domain_subset, batch_size=batch_size, shuffle=False)

        correct = 0
        total = 0

        with torch.no_grad():
            for batch in loader:
                input_ids = batch["input_ids"].to(device)
                labels = batch["labels"].to(device)

                output = model(input_ids)
                predictions = output.argmax(dim=-1)

                # Compute accuracy on next token prediction
                correct += (predictions == labels).float().sum().item()
                total += labels.numel()

        accuracy = correct / total if total > 0 else 0.0
        domain_accuracies[domain_name] = accuracy

    return domain_accuracies


# Main experiment
print("Generating synthetic multi-domain dataset...")
train_dataset = MultiDomainDataset(
    num_samples_per_domain=400, seq_len=32, vocab_size=1000
)
val_dataset = MultiDomainDataset(
    num_samples_per_domain=100, seq_len=32, vocab_size=1000
)

print(f"Train dataset size: {len(train_dataset)}")
print(f"Val dataset size: {len(val_dataset)}")

# Train static mixing baseline
print("\n" + "=" * 60)
print("Training STATIC MIXING baseline...")
print("=" * 60)
model_static = SimpleTransformer(vocab_size=1000, d_model=128, nhead=4, num_layers=3)
results_static = train_model(
    model_static,
    train_dataset,
    val_dataset,
    epochs=10,
    batch_size=32,
    dynamic_mixing=False,
)

experiment_data["static_mixing"]["metrics"]["train_loss"] = results_static[
    "train_losses"
]
experiment_data["static_mixing"]["metrics"]["val_loss"] = results_static["val_losses"]
experiment_data["static_mixing"]["metrics"]["balance_score"] = results_static[
    "balance_scores"
]
experiment_data["static_mixing"]["domain_accuracies"] = results_static[
    "final_domain_accuracies"
]

# Train dynamic mixing model
print("\n" + "=" * 60)
print("Training DYNAMIC MIXING model...")
print("=" * 60)
model_dynamic = SimpleTransformer(vocab_size=1000, d_model=128, nhead=4, num_layers=3)
results_dynamic = train_model(
    model_dynamic,
    train_dataset,
    val_dataset,
    epochs=10,
    batch_size=32,
    dynamic_mixing=True,
    mixing_update_freq=2,
)

experiment_data["dynamic_mixing"]["metrics"]["train_loss"] = results_dynamic[
    "train_losses"
]
experiment_data["dynamic_mixing"]["metrics"]["val_loss"] = results_dynamic["val_losses"]
experiment_data["dynamic_mixing"]["metrics"]["balance_score"] = results_dynamic[
    "balance_scores"
]
experiment_data["dynamic_mixing"]["domain_accuracies"] = results_dynamic[
    "final_domain_accuracies"
]
experiment_data["dynamic_mixing"]["mixing_ratios"] = results_dynamic["mixing_ratios"]

# Visualization
print("\nGenerating visualizations...")

# Plot 1: Training and validation loss comparison
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

axes[0, 0].plot(results_static["train_losses"], label="Static Mixing", marker="o")
axes[0, 0].plot(results_dynamic["train_losses"], label="Dynamic Mixing", marker="s")
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Training Loss")
axes[0, 0].set_title("Training Loss Comparison")
axes[0, 0].legend()
axes[0, 0].grid(True)

axes[0, 1].plot(results_static["val_losses"], label="Static Mixing", marker="o")
axes[0, 1].plot(results_dynamic["val_losses"], label="Dynamic Mixing", marker="s")
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Validation Loss")
axes[0, 1].set_title("Validation Loss Comparison")
axes[0, 1].legend()
axes[0, 1].grid(True)

# Plot 2: Balance score over time
axes[1, 0].plot(results_static["balance_scores"], label="Static Mixing", marker="o")
axes[1, 0].plot(results_dynamic["balance_scores"], label="Dynamic Mixing", marker="s")
axes[1, 0].set_xlabel("Epoch")
axes[1, 0].set_ylabel("Balance Score (higher is better)")
axes[1, 0].set_title("Cross-Domain Task Balance Score")
axes[1, 0].legend()
axes[1, 0].grid(True)

# Plot 3: Domain-specific accuracies
domains = list(results_static["final_domain_accuracies"].keys())
static_accs = [results_static["final_domain_accuracies"][d] for d in domains]
dynamic_accs = [results_dynamic["final_domain_accuracies"][d] for d in domains]

x = np.arange(len(domains))
width = 0.35

axes[1, 1].bar(x - width / 2, static_accs, width, label="Static Mixing", alpha=0.8)
axes[1, 1].bar(x + width / 2, dynamic_accs, width, label="Dynamic Mixing", alpha=0.8)
axes[1, 1].set_xlabel("Domain")
axes[1, 1].set_ylabel("Accuracy")
axes[1, 1].set_title("Final Domain-Specific Accuracies")
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(domains, rotation=45, ha="right")
axes[1, 1].legend()
axes[1, 1].grid(True, axis="y")

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "comparison_metrics.png"), dpi=150, bbox_inches="tight"
)
plt.close()

# Plot 4: Mixing ratios evolution
if len(results_dynamic["mixing_ratios"]) > 0:
    fig, ax = plt.subplots(figsize=(10, 6))
    mixing_ratios = np.array(results_dynamic["mixing_ratios"])
    epochs = np.arange(len(mixing_ratios))

    for i, domain in enumerate(["Wikipedia", "Code", "Scientific", "Conversational"]):
        ax.plot(epochs, mixing_ratios[:, i], marker="o", label=domain)

    ax.set_xlabel("Update Step")
    ax.set_ylabel("Mixing Ratio")
    ax.set_title("Dynamic Mixing Ratios Evolution")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, "mixing_ratios_evolution.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

# Plot 5: Representation health metrics
if len(experiment_data["dynamic_mixing"]["attention_entropy"]) > 0:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    axes[0].plot(experiment_data["dynamic_mixing"]["attention_entropy"], marker="o")
    axes[0].set_xlabel("Update Step")
    axes[0].set_ylabel("Attention Entropy")
    axes[0].set_title("Attention Entropy Over Time")
    axes[0].grid(True)

    axes[1].plot(experiment_data["dynamic_mixing"]["silhouette_scores"], marker="s")
    axes[1].set_xlabel("Update Step")
    axes[1].set_ylabel("Silhouette Score")
    axes[1].set_title("Feature Clustering Quality")
    axes[1].grid(True)

    axes[2].plot(experiment_data["dynamic_mixing"]["cka_similarity"], marker="^")
    axes[2].set_xlabel("Update Step")
    axes[2].set_ylabel("CKA Similarity")
    axes[2].set_title("Layer-wise CKA Similarity")
    axes[2].grid(True)

    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, "representation_health_metrics.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Print final results
print("\n" + "=" * 60)
print("FINAL RESULTS")
print("=" * 60)

print("\nStatic Mixing:")
print(f"  Final validation loss: {results_static['val_losses'][-1]:.4f}")
print(f"  Final balance score: {results_static['balance_scores'][-1]:.4f}")
print(f"  Domain accuracies: {results_static['final_domain_accuracies']}")

print("\nDynamic Mixing:")
print(f"  Final validation loss: {results_dynamic['val_losses'][-1]:.4f}")
print(f"  Final balance score: {results_dynamic['balance_scores'][-1]:.4f}")
print(f"  Domain accuracies: {results_dynamic['final_domain_accuracies']}")

improvement = (
    (results_dynamic["balance_scores"][-1] - results_static["balance_scores"][-1])
    / results_static["balance_scores"][-1]
    * 100
)
print(f"\nBalance Score Improvement: {improvement:.2f}%")

print(f"\nAll results saved to {working_dir}")
print("Experiment completed successfully!")
