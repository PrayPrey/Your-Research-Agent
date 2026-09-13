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

learning_rate = 1e-3
batch_size = 64
num_epochs = 20

experiment_data = {
    "static": {
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
    "smart_sparse": {
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
        "interventions": [],
        "gradient_norms": [],
    },
}


class MultiDomainDataset(Dataset):
    def __init__(
        self, num_samples_per_domain=400, seq_len=32, vocab_size=500, split="train"
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
        self.data = []
        self.labels = []
        self.domain_ids = []

        try:
            tinystories_data = load_dataset(
                "roneneldan/TinyStories", split=f"{split}[:500]", trust_remote_code=True
            )
            openwebtext_data = load_dataset(
                "Skylion007/openwebtext", split=f"train[:500]", trust_remote_code=True
            )
        except:
            tinystories_data = None
            openwebtext_data = None

        for domain_id, domain in enumerate(self.domains):
            for i in range(num_samples_per_domain):
                if domain == "wikipedia":
                    sample = np.random.randint(50, 200, seq_len)
                elif domain == "code":
                    base = np.random.randint(200, 300, seq_len // 4)
                    sample = np.tile(base, 4)[:seq_len]
                elif domain == "scientific":
                    sample = np.concatenate(
                        [
                            np.random.randint(300, 350, seq_len // 2),
                            np.random.randint(350, 400, seq_len // 2),
                        ]
                    )
                elif domain == "conversational":
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
                else:
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


class SmartSparseMixer:
    def __init__(self, num_domains=6):
        self.num_domains = num_domains
        self.mixing_ratios = np.ones(num_domains) / num_domains
        self.baseline_metrics = None
        self.metric_history = {"entropy": [], "silhouette": [], "cka": []}
        self.gradient_history = []
        self.intervention_cooldown = 0

    def update(self, metrics, domain_performance, epoch, domain_gradients):
        entropy = metrics["attention_entropy"]
        silhouette = metrics["silhouette"]
        cka = metrics["cka"]

        self.metric_history["entropy"].append(entropy)
        self.metric_history["silhouette"].append(silhouette)
        self.metric_history["cka"].append(cka)
        self.gradient_history.append(domain_gradients.copy())

        # Establish baseline in first 3 epochs
        if epoch <= 2:
            if self.baseline_metrics is None:
                self.baseline_metrics = {
                    "entropy": entropy,
                    "silhouette": silhouette,
                    "cka": cka,
                }
            else:
                self.baseline_metrics["entropy"] = (
                    0.7 * self.baseline_metrics["entropy"] + 0.3 * entropy
                )
                self.baseline_metrics["silhouette"] = (
                    0.7 * self.baseline_metrics["silhouette"] + 0.3 * silhouette
                )
                self.baseline_metrics["cka"] = (
                    0.7 * self.baseline_metrics["cka"] + 0.3 * cka
                )
            return self.mixing_ratios, False

        # Cooldown check - don't intervene every epoch
        if self.intervention_cooldown > 0:
            self.intervention_cooldown -= 1
            return self.mixing_ratios, False

        # Multi-signal health degradation detector with strict thresholds
        health_signals = []

        # Signal 1: Significant entropy drop (>20% below baseline)
        if entropy < self.baseline_metrics["entropy"] * 0.8:
            health_signals.append("entropy_drop")

        # Signal 2: Persistent silhouette decline (check 3-epoch trend)
        if len(self.metric_history["silhouette"]) >= 3:
            recent_sil = self.metric_history["silhouette"][-3:]
            if all(s < self.baseline_metrics["silhouette"] * 0.85 for s in recent_sil):
                health_signals.append("silhouette_decline")

        # Signal 3: High CKA indicating convergence
        if cka > 0.90:
            health_signals.append("high_cka")

        # Signal 4: Gradient imbalance across domains
        grad_std = domain_gradients.std()
        grad_mean = domain_gradients.mean()
        if grad_std / (grad_mean + 1e-9) > 0.5:
            health_signals.append("gradient_imbalance")

        # Require at least 2 concurrent signals to trigger intervention
        if len(health_signals) < 2:
            return self.mixing_ratios, False

        # Intervention triggered - compute smart adjustments
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

        # Identify struggling domains using both performance and gradients
        perf_threshold = perf_array.mean() - 0.1 * perf_array.std()
        grad_threshold = domain_gradients.mean() + 0.5 * domain_gradients.std()

        struggling_domains = (perf_array < perf_threshold) | (
            domain_gradients > grad_threshold
        )

        # Compute targeted adjustments
        adjustments = np.zeros(self.num_domains)

        if "entropy_drop" in health_signals or "silhouette_decline" in health_signals:
            # Boost struggling domains
            adjustments[struggling_domains] += 0.15
            # Reduce well-performing domains slightly
            adjustments[~struggling_domains] -= 0.05

        if "gradient_imbalance" in health_signals:
            # Balance by gradient magnitude
            grad_normalized = (domain_gradients - domain_gradients.min()) / (
                domain_gradients.max() - domain_gradients.min() + 1e-9
            )
            adjustments += 0.1 * (grad_normalized - 0.5)

        # Apply adjustments with adaptive learning rate
        in_critical_window = 5 <= epoch <= 10
        learning_rate = 0.35 if in_critical_window else 0.20

        new_ratios = self.mixing_ratios + adjustments * learning_rate
        new_ratios = np.maximum(new_ratios, 0.05)
        new_ratios = new_ratios / new_ratios.sum()

        self.mixing_ratios = new_ratios
        self.intervention_cooldown = 1  # Wait 1 epoch before next intervention

        return self.mixing_ratios, True


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


def compute_domain_gradients(model, dataset, batch_size=32):
    model.eval()
    domain_grad_norms = np.zeros(6)
    domain_counts = np.zeros(6)

    sampler_indices = list(range(min(200, len(dataset))))
    np.random.shuffle(sampler_indices)

    for idx in sampler_indices[:batch_size]:
        sample = dataset[idx]
        input_ids = sample["input_ids"].unsqueeze(0).to(device)
        labels = sample["labels"].unsqueeze(0).to(device)
        domain_id = sample["domain_id"].item()

        model.zero_grad()
        outputs = model(input_ids)
        loss = F.cross_entropy(outputs.view(-1, 500), labels.view(-1))
        loss.backward()

        grad_norm = sum(
            p.grad.norm().item() for p in model.parameters() if p.grad is not None
        )
        domain_grad_norms[domain_id] += grad_norm
        domain_counts[domain_id] += 1

        model.zero_grad()

    domain_counts = np.maximum(domain_counts, 1)
    return domain_grad_norms / domain_counts


def train_model(mixing_strategy="static"):
    print(f"\n{'='*50}")
    print(f"Training: {mixing_strategy} mixing")
    print(f"{'='*50}\n")

    torch.manual_seed(42)
    np.random.seed(42)

    train_dataset = MultiDomainDataset(
        num_samples_per_domain=400, seq_len=32, vocab_size=500, split="train"
    )
    test_dataset = MultiDomainDataset(
        num_samples_per_domain=100, seq_len=32, vocab_size=500, split="validation"
    )

    model = SimpleTransformer(vocab_size=500, d_model=128, nhead=4, num_layers=3).to(
        device
    )
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=0.01
    )
    criterion = nn.CrossEntropyLoss()

    if mixing_strategy == "smart_sparse":
        mixer = SmartSparseMixer(num_domains=6)
        mixing_ratios = mixer.mixing_ratios
    else:
        mixing_ratios = np.ones(6) / 6

    exp_data = experiment_data[mixing_strategy]

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

        # Compute domain gradients for smart mixing
        domain_gradients = compute_domain_gradients(model, train_dataset, batch_size=32)

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

        if mixing_strategy == "smart_sparse":
            exp_data["gradient_norms"].append(domain_gradients.copy())

        # Update mixing ratios
        if mixing_strategy == "smart_sparse" and epoch >= 2:
            metrics = {
                "attention_entropy": attention_entropy,
                "silhouette": silhouette,
                "cka": cka,
            }
            mixing_ratios, intervention = mixer.update(
                metrics, exp_data["domain_performance"], epoch, domain_gradients
            )
            exp_data["interventions"].append(1 if intervention else 0)

        print(
            f"Epoch {epoch+1}/{num_epochs}: validation_loss = {avg_val_loss:.4f}, balance_score = {balance_score:.4f}, entropy = {attention_entropy:.4f}"
        )


# Train all models
train_model(mixing_strategy="static")
train_model(mixing_strategy="smart_sparse")

# Visualization
fig = plt.figure(figsize=(20, 12))

domains = [
    "wikipedia",
    "code",
    "scientific",
    "conversational",
    "tinystories",
    "openwebtext",
]

# Plot 1: Balance Score Evolution
ax1 = plt.subplot(3, 3, 1)
for strategy in ["static", "smart_sparse"]:
    ax1.plot(
        experiment_data[strategy]["balance_score"],
        label=strategy,
        linewidth=2,
        marker="o",
        markersize=4,
    )
ax1.set_xlabel("Epoch")
ax1.set_ylabel("Balance Score")
ax1.set_title("Cross-Domain Balance Score Evolution")
ax1.legend()
ax1.grid(True)
ax1.axvspan(5, 10, alpha=0.2, color="yellow", label="Critical Window")

# Plot 2: Validation Loss
ax2 = plt.subplot(3, 3, 2)
for strategy in ["static", "smart_sparse"]:
    ax2.plot(
        experiment_data[strategy]["metrics"]["val_loss"], label=strategy, linewidth=2
    )
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Validation Loss")
ax2.set_title("Validation Loss Over Training")
ax2.legend()
ax2.grid(True)
ax2.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 3: Attention Entropy
ax3 = plt.subplot(3, 3, 3)
for strategy in ["static", "smart_sparse"]:
    ax3.plot(
        experiment_data[strategy]["metrics"]["attention_entropy"],
        label=strategy,
        linewidth=2,
    )
ax3.set_xlabel("Epoch")
ax3.set_ylabel("Attention Entropy")
ax3.set_title("Attention Entropy Over Training")
ax3.legend()
ax3.grid(True)
ax3.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 4: Silhouette Score
ax4 = plt.subplot(3, 3, 4)
for strategy in ["static", "smart_sparse"]:
    ax4.plot(
        experiment_data[strategy]["metrics"]["silhouette"], label=strategy, linewidth=2
    )
ax4.set_xlabel("Epoch")
ax4.set_ylabel("Silhouette Score")
ax4.set_title("Feature Space Clustering Quality")
ax4.legend()
ax4.grid(True)
ax4.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 5: CKA Similarity
ax5 = plt.subplot(3, 3, 5)
for strategy in ["static", "smart_sparse"]:
    ax5.plot(experiment_data[strategy]["metrics"]["cka"], label=strategy, linewidth=2)
ax5.set_xlabel("Epoch")
ax5.set_ylabel("CKA Similarity")
ax5.set_title("Layer-wise Representation Similarity")
ax5.legend()
ax5.grid(True)
ax5.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 6: Intervention Tracking
ax6 = plt.subplot(3, 3, 6)
if "interventions" in experiment_data["smart_sparse"]:
    cumulative_interventions = np.cumsum(
        experiment_data["smart_sparse"]["interventions"]
    )
    ax6.plot(
        range(len(cumulative_interventions)),
        cumulative_interventions,
        label="smart_sparse",
        linewidth=2,
        marker="s",
        color="green",
    )
ax6.set_xlabel("Epoch")
ax6.set_ylabel("Cumulative Interventions")
ax6.set_title("Smart Sparse Intervention Count")
ax6.legend()
ax6.grid(True)
ax6.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 7: Domain Performance Std Dev
ax7 = plt.subplot(3, 3, 7)
for strategy in ["static", "smart_sparse"]:
    perf_std = []
    for epoch in range(len(experiment_data[strategy]["balance_score"])):
        epoch_perf = [
            experiment_data[strategy]["domain_performance"][d][epoch] for d in domains
        ]
        perf_std.append(np.std(epoch_perf))
    ax7.plot(perf_std, label=strategy, linewidth=2)
ax7.set_xlabel("Epoch")
ax7.set_ylabel("Performance Std Dev")
ax7.set_title("Domain Performance Imbalance (Lower is Better)")
ax7.legend()
ax7.grid(True)
ax7.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 8: Final Per-Domain Performance
ax8 = plt.subplot(3, 3, 8)
x = np.arange(len(domains))
width = 0.35
for i, strategy in enumerate(["static", "smart_sparse"]):
    perf = [experiment_data[strategy]["domain_performance"][d][-1] for d in domains]
    ax8.bar(x + i * width, perf, width, label=strategy, alpha=0.8)
ax8.set_ylabel("Final Accuracy")
ax8.set_title("Final Per-Domain Performance")
ax8.set_xticks(x + width / 2)
ax8.set_xticklabels(domains, rotation=45, ha="right")
ax8.legend()
ax8.grid(True, axis="y")

# Plot 9: Gradient Norms Evolution
ax9 = plt.subplot(3, 3, 9)
if "gradient_norms" in experiment_data["smart_sparse"]:
    grad_history = np.array(experiment_data["smart_sparse"]["gradient_norms"])
    for i, domain in enumerate(domains):
        ax9.plot(grad_history[:, i], label=domain, linewidth=1.5, alpha=0.8)
ax9.set_xlabel("Epoch")
ax9.set_ylabel("Gradient Norm")
ax9.set_title("Per-Domain Gradient Norms")
ax9.legend(loc="best", fontsize=7)
ax9.grid(True)
ax9.axvspan(5, 10, alpha=0.2, color="yellow")

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "smart_sparse_results.png"), dpi=300, bbox_inches="tight"
)
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Print final results
print("\n" + "=" * 70)
print("SMART SPARSE INTERVENTION RESULTS")
print("=" * 70)

for strategy in ["static", "smart_sparse"]:
    print(f"\n{strategy.upper()}:")
    print(
        f"  Final Balance Score: {experiment_data[strategy]['balance_score'][-1]:.4f}"
    )
    print(
        f"  Final Validation Loss: {experiment_data[strategy]['metrics']['val_loss'][-1]:.4f}"
    )
    print(
        f"  Avg Balance Score: {np.mean(experiment_data[strategy]['balance_score']):.4f}"
    )
    print(
        f"  Avg Validation Loss: {np.mean(experiment_data[strategy]['metrics']['val_loss']):.4f}"
    )

    if "interventions" in experiment_data[strategy]:
        total_interventions = np.sum(experiment_data[strategy]["interventions"])
        window_interventions = np.sum(experiment_data[strategy]["interventions"][5:11])
        print(f"  Total Interventions: {total_interventions}")
        print(f"  Interventions in Critical Window (5-10): {window_interventions}")
        print(
            f"  Intervention Epochs: {[i+1 for i, x in enumerate(experiment_data[strategy]['interventions']) if x == 1]}"
        )

print("\nExperiment complete!")
