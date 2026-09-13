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

# Hyperparameters
learning_rate = 1e-3
batch_size = 64
num_epochs = 20

experiment_data = {
    "random_init": {
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
    },
    "domain_clustered_init": {
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
    },
    "domain_orthogonal_init": {
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


def get_domain_token_mapping():
    """Define which tokens belong to which domain based on dataset generation"""
    domain_ranges = {
        0: (50, 200),  # wikipedia
        1: (200, 300),  # code
        2: (300, 400),  # scientific
        3: (400, 450),  # conversational
        4: (100, 200),  # tinystories
        5: (250, 350),  # openwebtext
    }
    return domain_ranges


def initialize_domain_clustered_embeddings(vocab_size, d_model, num_domains=6):
    """Initialize embeddings with domain-specific clusters"""
    embeddings = torch.randn(vocab_size, d_model) * 0.02
    domain_ranges = get_domain_token_mapping()

    # Create domain-specific centroids
    domain_centroids = torch.randn(num_domains, d_model) * 0.5

    for domain_id, (start_token, end_token) in domain_ranges.items():
        # Tokens in this range are pulled toward domain centroid
        for token_id in range(start_token, min(end_token, vocab_size)):
            # Add domain-specific bias to embeddings
            domain_offset = domain_centroids[domain_id] * 0.3
            embeddings[token_id] = embeddings[token_id] + domain_offset

    return embeddings


def initialize_domain_orthogonal_embeddings(vocab_size, d_model, num_domains=6):
    """Initialize embeddings with maximally separated domain clusters"""
    embeddings = torch.randn(vocab_size, d_model) * 0.02
    domain_ranges = get_domain_token_mapping()

    # Create orthogonal domain subspaces
    domain_subspaces = []
    subspace_dim = d_model // num_domains

    for i in range(num_domains):
        # Create orthogonal basis vectors for each domain
        subspace = torch.zeros(d_model)
        start_idx = i * subspace_dim
        end_idx = min((i + 1) * subspace_dim, d_model)
        subspace[start_idx:end_idx] = 1.0
        domain_subspaces.append(subspace)

    for domain_id, (start_token, end_token) in domain_ranges.items():
        for token_id in range(start_token, min(end_token, vocab_size)):
            # Project embeddings into domain-specific orthogonal subspace
            domain_component = domain_subspaces[domain_id] * 0.5
            embeddings[token_id] = embeddings[token_id] + domain_component

    return embeddings


class SimpleTransformer(nn.Module):
    def __init__(
        self,
        vocab_size=500,
        d_model=128,
        nhead=4,
        num_layers=3,
        dim_feedforward=512,
        init_strategy="random",
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)

        # Apply different initialization strategies
        if init_strategy == "domain_clustered":
            embeddings = initialize_domain_clustered_embeddings(vocab_size, d_model)
            self.embedding.weight.data = embeddings
        elif init_strategy == "domain_orthogonal":
            embeddings = initialize_domain_orthogonal_embeddings(vocab_size, d_model)
            self.embedding.weight.data = embeddings
        # else: use default random initialization

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


class WindowAwareMixer:
    def __init__(self, num_domains=6, critical_window=(5, 10)):
        self.num_domains = num_domains
        self.mixing_ratios = np.ones(num_domains) / num_domains
        self.critical_window = critical_window
        self.baseline_entropy = None
        self.baseline_silhouette = None

    def update(self, metrics, domain_performance, epoch):
        entropy = metrics["attention_entropy"]
        silhouette = metrics["silhouette"]
        cka = metrics["cka"]

        if epoch == 2:
            self.baseline_entropy = entropy
            self.baseline_silhouette = silhouette

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

        in_critical_window = self.critical_window[0] <= epoch <= self.critical_window[1]
        learning_rate = 0.4 if in_critical_window else 0.15

        adjustments = np.zeros(self.num_domains)
        intervention_triggered = False

        # Detect degradation trends
        if self.baseline_entropy is not None and entropy < self.baseline_entropy * 0.9:
            adjustments += (0.6 - perf_array) * 0.35
            intervention_triggered = True

        if (
            self.baseline_silhouette is not None
            and silhouette < self.baseline_silhouette * 0.85
        ):
            adjustments += (0.6 - perf_array) * 0.3
            intervention_triggered = True

        if cka > 0.87:
            weak_domains = perf_array < perf_array.mean()
            adjustments[weak_domains] += 0.2
            intervention_triggered = True

        # Extra intervention during critical window
        if in_critical_window:
            perf_std = perf_array.std()
            if perf_std > 0.15:
                adjustments += (perf_array.mean() - perf_array) * 0.25
                intervention_triggered = True

        new_ratios = self.mixing_ratios + adjustments * learning_rate
        new_ratios = np.maximum(new_ratios, 0.03)
        new_ratios = new_ratios / new_ratios.sum()

        self.mixing_ratios = new_ratios
        return self.mixing_ratios, intervention_triggered


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


def train_model(init_strategy="random"):
    print(f"\n{'='*50}")
    print(f"Training: {init_strategy} initialization")
    print(f"{'='*50}\n")

    torch.manual_seed(42)
    np.random.seed(42)

    train_dataset = MultiDomainDataset(
        num_samples_per_domain=400, seq_len=32, vocab_size=500, split="train"
    )
    test_dataset = MultiDomainDataset(
        num_samples_per_domain=100, seq_len=32, vocab_size=500, split="validation"
    )

    model = SimpleTransformer(
        vocab_size=500, d_model=128, nhead=4, num_layers=3, init_strategy=init_strategy
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=0.01
    )
    criterion = nn.CrossEntropyLoss()

    # Use window-aware mixer for all experiments
    mixer = WindowAwareMixer(num_domains=6)
    mixing_ratios = mixer.mixing_ratios

    exp_key = init_strategy + "_init"
    exp_data = experiment_data[exp_key]

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

        # Update mixing ratios
        if epoch >= 2:
            metrics = {
                "attention_entropy": attention_entropy,
                "silhouette": silhouette,
                "cka": cka,
            }
            mixing_ratios, intervention = mixer.update(
                metrics, exp_data["domain_performance"], epoch
            )
            exp_data["interventions"].append(1 if intervention else 0)

        print(
            f"Epoch {epoch+1}/{num_epochs}: val_loss = {avg_val_loss:.4f}, balance = {balance_score:.4f}, entropy = {attention_entropy:.4f}, silhouette = {silhouette:.4f}"
        )


# Train all models with different initialization strategies
train_model(init_strategy="random")
train_model(init_strategy="domain_clustered")
train_model(init_strategy="domain_orthogonal")

# Visualization
fig = plt.figure(figsize=(20, 15))

strategies = ["random_init", "domain_clustered_init", "domain_orthogonal_init"]
strategy_labels = ["Random Init", "Domain-Clustered Init", "Domain-Orthogonal Init"]

# Plot 1: Balance Score Evolution
ax1 = plt.subplot(3, 3, 1)
for strategy, label in zip(strategies, strategy_labels):
    ax1.plot(
        experiment_data[strategy]["balance_score"],
        label=label,
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

# Plot 2: Attention Entropy
ax2 = plt.subplot(3, 3, 2)
for strategy, label in zip(strategies, strategy_labels):
    ax2.plot(
        experiment_data[strategy]["metrics"]["attention_entropy"],
        label=label,
        linewidth=2,
    )
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Attention Entropy")
ax2.set_title("Attention Entropy Over Training")
ax2.legend()
ax2.grid(True)
ax2.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 3: Silhouette Score
ax3 = plt.subplot(3, 3, 3)
for strategy, label in zip(strategies, strategy_labels):
    ax3.plot(
        experiment_data[strategy]["metrics"]["silhouette"], label=label, linewidth=2
    )
ax3.set_xlabel("Epoch")
ax3.set_ylabel("Silhouette Score")
ax3.set_title("Feature Space Clustering Quality")
ax3.legend()
ax3.grid(True)
ax3.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 4: CKA Similarity
ax4 = plt.subplot(3, 3, 4)
for strategy, label in zip(strategies, strategy_labels):
    ax4.plot(experiment_data[strategy]["metrics"]["cka"], label=label, linewidth=2)
ax4.set_xlabel("Epoch")
ax4.set_ylabel("CKA Similarity")
ax4.set_title("Layer-wise Representation Similarity")
ax4.legend()
ax4.grid(True)
ax4.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 5: Per-Domain Performance Comparison
ax5 = plt.subplot(3, 3, 5)
domains = [
    "wikipedia",
    "code",
    "scientific",
    "conversational",
    "tinystories",
    "openwebtext",
]
x = np.arange(len(domains))
width = 0.25
for i, (strategy, label) in enumerate(zip(strategies, strategy_labels)):
    perf = [experiment_data[strategy]["domain_performance"][d][-1] for d in domains]
    ax5.bar(x + i * width, perf, width, label=label, alpha=0.8)
ax5.set_ylabel("Final Accuracy")
ax5.set_title("Final Per-Domain Performance")
ax5.set_xticks(x + width)
ax5.set_xticklabels(domains, rotation=45, ha="right")
ax5.legend()
ax5.grid(True, axis="y")

# Plot 6: Intervention Tracking
ax6 = plt.subplot(3, 3, 6)
for strategy, label in zip(strategies, strategy_labels):
    if (
        "interventions" in experiment_data[strategy]
        and len(experiment_data[strategy]["interventions"]) > 0
    ):
        cumulative_interventions = np.cumsum(experiment_data[strategy]["interventions"])
        ax6.plot(
            range(len(cumulative_interventions)),
            cumulative_interventions,
            label=label,
            linewidth=2,
            marker="s",
        )
ax6.set_xlabel("Epoch")
ax6.set_ylabel("Cumulative Interventions")
ax6.set_title("Dynamic Mixing Intervention Count")
ax6.legend()
ax6.grid(True)
ax6.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 7: Validation Loss
ax7 = plt.subplot(3, 3, 7)
for strategy, label in zip(strategies, strategy_labels):
    ax7.plot(experiment_data[strategy]["metrics"]["val_loss"], label=label, linewidth=2)
ax7.set_xlabel("Epoch")
ax7.set_ylabel("Validation Loss")
ax7.set_title("Validation Loss Over Training")
ax7.legend()
ax7.grid(True)
ax7.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 8: Domain Performance Std Dev (Balance Measure)
ax8 = plt.subplot(3, 3, 8)
for strategy, label in zip(strategies, strategy_labels):
    perf_std = []
    for epoch in range(len(experiment_data[strategy]["balance_score"])):
        epoch_perf = [
            experiment_data[strategy]["domain_performance"][d][epoch] for d in domains
        ]
        perf_std.append(np.std(epoch_perf))
    ax8.plot(perf_std, label=label, linewidth=2)
ax8.set_xlabel("Epoch")
ax8.set_ylabel("Performance Std Dev")
ax8.set_title("Domain Performance Imbalance (Lower is Better)")
ax8.legend()
ax8.grid(True)
ax8.axvspan(5, 10, alpha=0.2, color="yellow")

# Plot 9: Early Training Dynamics (First 5 Epochs)
ax9 = plt.subplot(3, 3, 9)
for strategy, label in zip(strategies, strategy_labels):
    early_balance = experiment_data[strategy]["balance_score"][:5]
    ax9.plot(
        range(len(early_balance)), early_balance, label=label, linewidth=2, marker="o"
    )
ax9.set_xlabel("Epoch")
ax9.set_ylabel("Balance Score")
ax9.set_title("Early Training Dynamics (Epochs 0-4)")
ax9.legend()
ax9.grid(True)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "embedding_init_ablation_results.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Print final results
print("\n" + "=" * 70)
print("EMBEDDING INITIALIZATION ABLATION RESULTS")
print("=" * 70)

for strategy, label in zip(strategies, strategy_labels):
    print(f"\n{label}:")
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
        f"  Final Silhouette Score: {experiment_data[strategy]['metrics']['silhouette'][-1]:.4f}"
    )
    print(
        f"  Early Training Balance (Epoch 4): {experiment_data[strategy]['balance_score'][4]:.4f}"
    )

    if (
        "interventions" in experiment_data[strategy]
        and len(experiment_data[strategy]["interventions"]) > 0
    ):
        total_interventions = np.sum(experiment_data[strategy]["interventions"])
        window_interventions = (
            np.sum(experiment_data[strategy]["interventions"][5:11])
            if len(experiment_data[strategy]["interventions"]) > 10
            else np.sum(experiment_data[strategy]["interventions"][5:])
        )
        print(f"  Total Interventions: {total_interventions}")
        print(f"  Interventions in Critical Window (5-10): {window_interventions}")

print("\n" + "=" * 70)
print("KEY FINDINGS:")
print("=" * 70)
print("- Random Init: Baseline with no domain structure at initialization")
print("- Domain-Clustered: Tokens from same domain start closer in embedding space")
print(
    "- Domain-Orthogonal: Domain token clusters maximally separated at initialization"
)
print("\nThis tests whether initialization bias helps or hinders the dynamic mixer's")
print("ability to balance multi-domain learning during the critical training window.")

print("\nExperiment complete!")
