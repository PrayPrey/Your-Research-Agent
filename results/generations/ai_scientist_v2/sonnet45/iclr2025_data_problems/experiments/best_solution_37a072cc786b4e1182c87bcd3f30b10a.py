import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
import warnings
from datasets import load_dataset

warnings.filterwarnings("ignore")

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Hyperparameters - adjusted for better convergence
learning_rates = [5e-4, 1e-3]
batch_sizes = [64, 128]
num_epochs = 15

# Experiment data storage
experiment_data = {}
for lr in learning_rates:
    for bs in batch_sizes:
        key = f"lr_{lr}_bs_{bs}"
        experiment_data[key] = {
            "static_mixing": {
                "metrics": {
                    "train_loss": [],
                    "val_loss": [],
                    "attention_entropy": [],
                    "silhouette": [],
                    "cka": [],
                },
                "domain_performance": {
                    "wikipedia": [],
                    "code": [],
                    "scientific": [],
                    "conversational": [],
                    "tinystories": [],
                    "openwebtext": [],
                },
                "balance_score": [],
                "mixing_ratios": [],
            },
            "dynamic_mixing": {
                "metrics": {
                    "train_loss": [],
                    "val_loss": [],
                    "attention_entropy": [],
                    "silhouette": [],
                    "cka": [],
                },
                "domain_performance": {
                    "wikipedia": [],
                    "code": [],
                    "scientific": [],
                    "conversational": [],
                    "tinystories": [],
                    "openwebtext": [],
                },
                "balance_score": [],
                "mixing_ratios": [],
            },
        }


class MultiDomainDataset(Dataset):
    def __init__(
        self, num_samples_per_domain=500, seq_len=32, vocab_size=500, split="train"
    ):
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.domains = [
            "wikipedia",
            "code",
            "scientific",
            "conversational",
            "tinystories",
            "openwebtext",
        ]
        self.num_domains = len(self.domains)

        self.data = []
        self.labels = []
        self.domain_ids = []

        # Load HuggingFace datasets with smaller samples
        try:
            tinystories_data = load_dataset(
                "roneneldan/TinyStories", split=f"{split}[:500]", trust_remote_code=True
            )
            openwebtext_data = load_dataset(
                "Skylion007/openwebtext", split=f"train[:500]", trust_remote_code=True
            )
        except:
            print("Failed to load HuggingFace datasets, using synthetic data")
            tinystories_data = None
            openwebtext_data = None

        for domain_id, domain in enumerate(self.domains):
            for i in range(num_samples_per_domain):
                if domain == "wikipedia":
                    # More structured patterns
                    sample = np.random.randint(50, 200, seq_len)
                elif domain == "code":
                    # Code-like patterns with repeating tokens
                    base = np.random.randint(200, 300, seq_len // 4)
                    sample = np.tile(base, 4)[:seq_len]
                elif domain == "scientific":
                    # Scientific patterns with specific vocabulary ranges
                    sample = np.concatenate(
                        [
                            np.random.randint(300, 350, seq_len // 2),
                            np.random.randint(350, 400, seq_len // 2),
                        ]
                    )
                elif domain == "conversational":
                    # Conversational patterns
                    sample = np.random.randint(400, 450, seq_len)
                elif domain == "tinystories":
                    if tinystories_data is not None and i < len(tinystories_data):
                        text = tinystories_data[i]["text"][:seq_len]
                        sample = np.array([ord(c) % vocab_size for c in text])
                        if len(sample) < seq_len:
                            sample = np.pad(
                                sample, (0, seq_len - len(sample)), constant_values=0
                            )
                        sample = np.clip(sample, 0, vocab_size - 1)
                    else:
                        sample = np.random.randint(100, 200, seq_len)
                else:  # openwebtext
                    if openwebtext_data is not None and i < len(openwebtext_data):
                        text = openwebtext_data[i]["text"][:seq_len]
                        sample = np.array([ord(c) % vocab_size for c in text])
                        if len(sample) < seq_len:
                            sample = np.pad(
                                sample, (0, seq_len - len(sample)), constant_values=0
                            )
                        sample = np.clip(sample, 0, vocab_size - 1)
                    else:
                        sample = np.random.randint(250, 350, seq_len)

                self.data.append(sample)
                self.labels.append(np.roll(sample, -1))
                self.domain_ids.append(domain_id)

        self.data = torch.LongTensor(self.data)
        self.labels = torch.LongTensor(self.labels)
        self.domain_ids = torch.LongTensor(self.domain_ids)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return {
            "input_ids": self.data[idx],
            "labels": self.labels[idx],
            "domain_id": self.domain_ids[idx],
        }


class SimpleTransformer(nn.Module):
    def __init__(
        self, vocab_size=500, d_model=128, nhead=4, num_layers=3, dim_feedforward=512
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Parameter(torch.randn(1, 512, d_model) * 0.02)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            batch_first=True,
            dropout=0.1,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output_proj = nn.Linear(d_model, vocab_size)
        self.d_model = d_model
        self.num_layers = num_layers

    def forward(self, x, return_attention=False, return_hidden=False):
        seq_len = x.size(1)
        x = self.embedding(x) * np.sqrt(self.d_model)
        x = x + self.pos_embedding[:, :seq_len, :]

        if return_hidden:
            hidden_states = [x]

        if return_attention:
            attentions = []
            for layer in self.transformer.layers:
                attn_output, attn_weights = layer.self_attn(
                    x, x, x, need_weights=True, average_attn_weights=True
                )
                attentions.append(attn_weights)
                x = layer(x)
                if return_hidden:
                    hidden_states.append(x)
            output = self.output_proj(x)
            if return_hidden:
                return output, attentions, hidden_states
            return output, attentions
        else:
            x = self.transformer(x)
            output = self.output_proj(x)
            return output


def compute_attention_entropy(attention_weights):
    entropies = []
    for attn in attention_weights:
        attn_probs = attn.detach().cpu().numpy()
        entropy = -np.sum(attn_probs * np.log(attn_probs + 1e-9), axis=-1)
        entropies.append(np.mean(entropy))
    return np.mean(entropies)


def compute_silhouette_score(hidden_states, domain_ids, max_samples=500):
    features = hidden_states[-1].detach().cpu().numpy()
    features = features.mean(axis=1)
    domain_ids = domain_ids.detach().cpu().numpy()

    if len(features) > max_samples:
        indices = np.random.choice(len(features), max_samples, replace=False)
        features = features[indices]
        domain_ids = domain_ids[indices]

    if len(np.unique(domain_ids)) < 2:
        return 0.0

    try:
        score = silhouette_score(features, domain_ids)
    except:
        score = 0.0
    return score


def compute_cka_similarity(X, Y):
    X = X - X.mean(axis=0, keepdims=True)
    Y = Y - Y.mean(axis=0, keepdims=True)

    X_gram = X @ X.T
    Y_gram = Y @ Y.T

    numerator = np.linalg.norm(X_gram @ Y_gram, "fro") ** 2
    denominator = np.linalg.norm(X_gram, "fro") * np.linalg.norm(Y_gram, "fro")

    if denominator == 0:
        return 0.0
    return numerator / denominator


def compute_layer_cka(hidden_states):
    if len(hidden_states) < 2:
        return 0.0
    cka_scores = []
    for i in range(len(hidden_states) - 1):
        h1 = (
            hidden_states[i]
            .detach()
            .cpu()
            .numpy()
            .reshape(hidden_states[i].size(0), -1)
        )
        h2 = (
            hidden_states[i + 1]
            .detach()
            .cpu()
            .numpy()
            .reshape(hidden_states[i + 1].size(0), -1)
        )
        cka = compute_cka_similarity(h1, h2)
        cka_scores.append(cka)
    return np.mean(cka_scores)


class DynamicMixer:
    def __init__(self, num_domains=6, smoothing=0.9):
        self.num_domains = num_domains
        self.mixing_ratios = np.ones(num_domains) / num_domains
        self.smoothing = smoothing

    def update(self, metrics, domain_performance):
        entropy = metrics["attention_entropy"]
        silhouette = metrics["silhouette"]
        cka = metrics["cka"]

        adjustments = np.zeros(self.num_domains)

        if entropy < 2.5:
            perf_array = np.array(
                [
                    domain_performance[d][-1] if len(domain_performance[d]) > 0 else 0.5
                    for d in [
                        "wikipedia",
                        "code",
                        "scientific",
                        "conversational",
                        "tinystories",
                        "openwebtext",
                    ]
                ]
            )
            adjustments += (1.0 - perf_array) * 0.1

        if silhouette < 0.2:
            perf_array = np.array(
                [
                    domain_performance[d][-1] if len(domain_performance[d]) > 0 else 0.5
                    for d in [
                        "wikipedia",
                        "code",
                        "scientific",
                        "conversational",
                        "tinystories",
                        "openwebtext",
                    ]
                ]
            )
            adjustments += (1.0 - perf_array) * 0.05

        if cka > 0.9:
            adjustments += 0.05

        new_ratios = self.mixing_ratios + adjustments
        new_ratios = np.maximum(new_ratios, 0.05)
        new_ratios = new_ratios / new_ratios.sum()

        self.mixing_ratios = (
            self.smoothing * self.mixing_ratios + (1 - self.smoothing) * new_ratios
        )
        self.mixing_ratios = self.mixing_ratios / self.mixing_ratios.sum()

        return self.mixing_ratios


class DomainSampler:
    def __init__(self, dataset, mixing_ratios):
        self.dataset = dataset
        self.mixing_ratios = mixing_ratios
        self.domain_indices = [[] for _ in range(6)]

        for idx in range(len(dataset)):
            domain_id = dataset.domain_ids[idx].item()
            self.domain_indices[domain_id].append(idx)

    def sample_batch(self, batch_size):
        batch_indices = []
        samples_per_domain = (batch_size * self.mixing_ratios).astype(int)
        samples_per_domain[-1] = batch_size - samples_per_domain[:-1].sum()

        for domain_id, n_samples in enumerate(samples_per_domain):
            if n_samples > 0 and len(self.domain_indices[domain_id]) > 0:
                indices = np.random.choice(
                    self.domain_indices[domain_id], n_samples, replace=True
                )
                batch_indices.extend(indices)

        np.random.shuffle(batch_indices)
        return batch_indices


def evaluate_downstream_tasks(model, test_dataset):
    model.eval()
    domain_correct = {i: 0 for i in range(6)}
    domain_total = {i: 0 for i in range(6)}

    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            domain_ids = batch["domain_id"]

            outputs = model(input_ids)
            predictions = outputs.argmax(dim=-1)

            for i in range(len(domain_ids)):
                domain_id = domain_ids[i].item()
                correct = (predictions[i] == labels[i]).float().mean().item()
                domain_correct[domain_id] += correct
                domain_total[domain_id] += 1

    domain_names = [
        "wikipedia",
        "code",
        "scientific",
        "conversational",
        "tinystories",
        "openwebtext",
    ]
    domain_performance = {}
    for domain_id, domain_name in enumerate(domain_names):
        if domain_total[domain_id] > 0:
            domain_performance[domain_name] = (
                domain_correct[domain_id] / domain_total[domain_id]
            )
        else:
            domain_performance[domain_name] = 0.0

    return domain_performance


def compute_balance_score(domain_performance):
    scores = np.array(list(domain_performance.values()))
    if len(scores) == 0 or scores.mean() < 1e-6:
        return 0.0
    cv = scores.std() / (scores.mean() + 1e-9)
    balance_score = 1.0 / (1.0 + cv)
    return max(0.0, min(1.0, balance_score))


def train_model(mixing_strategy="static", learning_rate=1e-3, batch_size=64):
    print(f"\n{'='*50}")
    print(f"Training: {mixing_strategy} mixing, LR={learning_rate}, BS={batch_size}")
    print(f"{'='*50}\n")

    torch.manual_seed(42)
    np.random.seed(42)

    train_dataset = MultiDomainDataset(
        num_samples_per_domain=300, seq_len=32, vocab_size=500, split="train"
    )
    test_dataset = MultiDomainDataset(
        num_samples_per_domain=80, seq_len=32, vocab_size=500, split="validation"
    )

    model = SimpleTransformer(vocab_size=500, d_model=128, nhead=4, num_layers=3).to(
        device
    )
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=0.01
    )
    criterion = nn.CrossEntropyLoss()

    if mixing_strategy == "dynamic":
        mixer = DynamicMixer(num_domains=6)
        mixing_ratios = mixer.mixing_ratios
    else:
        mixing_ratios = np.ones(6) / 6

    key = f"lr_{learning_rate}_bs_{batch_size}"
    exp_data = experiment_data[key][f"{mixing_strategy}_mixing"]

    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0.0
        num_batches = 0

        sampler = DomainSampler(train_dataset, mixing_ratios)

        for _ in range(len(train_dataset) // batch_size):
            batch_indices = sampler.sample_batch(batch_size)

            batch_data = [train_dataset[i] for i in batch_indices]
            input_ids = torch.stack([b["input_ids"] for b in batch_data]).to(device)
            labels = torch.stack([b["labels"] for b in batch_data]).to(device)

            optimizer.zero_grad()
            outputs = model(input_ids)

            loss = criterion(outputs.view(-1, 500), labels.view(-1))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            epoch_loss += loss.item()
            num_batches += 1

        avg_train_loss = epoch_loss / num_batches

        # Validation
        model.eval()
        val_loss = 0.0
        val_batches = 0

        all_attentions = []
        all_hidden_states = []
        all_domain_ids = []

        val_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                labels = batch["labels"].to(device)
                domain_ids = batch["domain_id"].to(device)

                outputs, attentions, hidden_states = model(
                    input_ids, return_attention=True, return_hidden=True
                )
                loss = criterion(outputs.view(-1, 500), labels.view(-1))

                val_loss += loss.item()
                val_batches += 1

                if len(all_attentions) < 5:
                    all_attentions.extend(attentions)
                all_hidden_states.append(hidden_states[-1])
                all_domain_ids.append(domain_ids)

        avg_val_loss = val_loss / val_batches

        # Compute metrics
        attention_entropy = compute_attention_entropy(all_attentions[:10])

        combined_hidden = torch.cat(all_hidden_states, dim=0)
        combined_domains = torch.cat(all_domain_ids, dim=0)
        silhouette = compute_silhouette_score([None, combined_hidden], combined_domains)

        sample_batch = next(iter(val_loader))
        sample_input = sample_batch["input_ids"].to(device)
        with torch.no_grad():
            _, _, sample_hidden = model(
                sample_input, return_attention=True, return_hidden=True
            )
        cka = compute_layer_cka(sample_hidden)

        domain_performance = evaluate_downstream_tasks(model, test_dataset)
        balance_score = compute_balance_score(domain_performance)

        # Store metrics
        exp_data["metrics"]["train_loss"].append(avg_train_loss)
        exp_data["metrics"]["val_loss"].append(avg_val_loss)
        exp_data["metrics"]["attention_entropy"].append(attention_entropy)
        exp_data["metrics"]["silhouette"].append(silhouette)
        exp_data["metrics"]["cka"].append(cka)

        for domain in [
            "wikipedia",
            "code",
            "scientific",
            "conversational",
            "tinystories",
            "openwebtext",
        ]:
            exp_data["domain_performance"][domain].append(domain_performance[domain])

        exp_data["balance_score"].append(balance_score)
        exp_data["mixing_ratios"].append(mixing_ratios.copy())

        if mixing_strategy == "dynamic" and epoch > 2:
            metrics = {
                "attention_entropy": attention_entropy,
                "silhouette": silhouette,
                "cka": cka,
            }
            mixing_ratios = mixer.update(metrics, exp_data["domain_performance"])

        print(
            f"Epoch {epoch+1}/{num_epochs}: validation_loss = {avg_val_loss:.4f}, balance_score = {balance_score:.4f}"
        )


# Train models with different hyperparameters
for lr in learning_rates:
    for bs in batch_sizes:
        train_model(mixing_strategy="static", learning_rate=lr, batch_size=bs)
        train_model(mixing_strategy="dynamic", learning_rate=lr, batch_size=bs)

# Visualization
fig = plt.figure(figsize=(20, 12))

# Plot 1: Balance Score Comparison
ax1 = plt.subplot(2, 3, 1)
config_labels = []
static_scores = []
dynamic_scores = []
for lr in learning_rates:
    for bs in batch_sizes:
        key = f"lr_{lr}_bs_{bs}"
        config_labels.append(f"{lr:.0e}\n{bs}")
        static_scores.append(experiment_data[key]["static_mixing"]["balance_score"][-1])
        dynamic_scores.append(
            experiment_data[key]["dynamic_mixing"]["balance_score"][-1]
        )

x = np.arange(len(config_labels))
width = 0.35
ax1.bar(x - width / 2, static_scores, width, label="Static", alpha=0.8)
ax1.bar(x + width / 2, dynamic_scores, width, label="Dynamic", alpha=0.8)
ax1.set_xlabel("LR / BS")
ax1.set_ylabel("Balance Score")
ax1.set_title("Cross-Domain Performance Balance Score")
ax1.set_xticks(x)
ax1.set_xticklabels(config_labels)
ax1.legend()
ax1.grid(True, axis="y")

# Plot 2: Training Loss
ax2 = plt.subplot(2, 3, 2)
best_idx = np.argmax(dynamic_scores)
best_key = list(experiment_data.keys())[best_idx]
train_loss_static = experiment_data[best_key]["static_mixing"]["metrics"]["train_loss"]
train_loss_dynamic = experiment_data[best_key]["dynamic_mixing"]["metrics"][
    "train_loss"
]
ax2.plot(train_loss_static, label="Static", linewidth=2)
ax2.plot(train_loss_dynamic, label="Dynamic", linewidth=2)
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Training Loss")
ax2.set_title(f"Training Loss (Best Config: {best_key})")
ax2.legend()
ax2.grid(True)

# Plot 3: Validation Loss
ax3 = plt.subplot(2, 3, 3)
val_loss_static = experiment_data[best_key]["static_mixing"]["metrics"]["val_loss"]
val_loss_dynamic = experiment_data[best_key]["dynamic_mixing"]["metrics"]["val_loss"]
ax3.plot(val_loss_static, label="Static", linewidth=2)
ax3.plot(val_loss_dynamic, label="Dynamic", linewidth=2)
ax3.set_xlabel("Epoch")
ax3.set_ylabel("Validation Loss")
ax3.set_title(f"Validation Loss (Best Config: {best_key})")
ax3.legend()
ax3.grid(True)

# Plot 4: Per-Domain Performance (Static)
ax4 = plt.subplot(2, 3, 4)
domains = [
    "wikipedia",
    "code",
    "scientific",
    "conversational",
    "tinystories",
    "openwebtext",
]
domain_perf_static = [
    experiment_data[best_key]["static_mixing"]["domain_performance"][d][-1]
    for d in domains
]
ax4.bar(range(len(domains)), domain_perf_static, alpha=0.8, color="tab:blue")
ax4.set_ylabel("Accuracy")
ax4.set_title("Per-Domain Performance - Static")
ax4.set_xticks(range(len(domains)))
ax4.set_xticklabels(domains, rotation=45, ha="right")
ax4.grid(True, axis="y")

# Plot 5: Per-Domain Performance (Dynamic)
ax5 = plt.subplot(2, 3, 5)
domain_perf_dynamic = [
    experiment_data[best_key]["dynamic_mixing"]["domain_performance"][d][-1]
    for d in domains
]
ax5.bar(range(len(domains)), domain_perf_dynamic, alpha=0.8, color="tab:orange")
ax5.set_ylabel("Accuracy")
ax5.set_title("Per-Domain Performance - Dynamic")
ax5.set_xticks(range(len(domains)))
ax5.set_xticklabels(domains, rotation=45, ha="right")
ax5.grid(True, axis="y")

# Plot 6: Balance Score Evolution
ax6 = plt.subplot(2, 3, 6)
balance_static = experiment_data[best_key]["static_mixing"]["balance_score"]
balance_dynamic = experiment_data[best_key]["dynamic_mixing"]["balance_score"]
ax6.plot(balance_static, marker="o", label="Static", linewidth=2)
ax6.plot(balance_dynamic, marker="s", label="Dynamic", linewidth=2)
ax6.set_xlabel("Epoch")
ax6.set_ylabel("Balance Score")
ax6.set_title("Balance Score Evolution")
ax6.legend()
ax6.grid(True)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "baseline_tuning_results.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Print results
print("\n" + "=" * 70)
print("BASELINE TUNING RESULTS")
print("=" * 70)

for key in experiment_data.keys():
    print(f"\n{key}:")
    static_balance = experiment_data[key]["static_mixing"]["balance_score"][-1]
    dynamic_balance = experiment_data[key]["dynamic_mixing"]["balance_score"][-1]
    print(f"  Static Balance Score: {static_balance:.4f}")
    print(f"  Dynamic Balance Score: {dynamic_balance:.4f}")

best_static_idx = np.argmax(static_scores)
best_dynamic_idx = np.argmax(dynamic_scores)
print(f"\nBest Static Config: {list(experiment_data.keys())[best_static_idx]}")
print(f"  Balance Score: {static_scores[best_static_idx]:.4f}")
print(f"\nBest Dynamic Config: {list(experiment_data.keys())[best_dynamic_idx]}")
print(f"  Balance Score: {dynamic_scores[best_dynamic_idx]:.4f}")

print("\nExperiment complete!")
