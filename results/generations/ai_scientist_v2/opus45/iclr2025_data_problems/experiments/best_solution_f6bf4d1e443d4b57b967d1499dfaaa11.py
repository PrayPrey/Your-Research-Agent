import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, Subset
import math
import matplotlib.pyplot as plt

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

torch.manual_seed(42)
np.random.seed(42)

from datasets import load_dataset

print("Loading HuggingFace datasets...")
datasets_info = {}

# Dataset 1: WikiText-2
wikitext = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
datasets_info["wikitext"] = [t for t in wikitext["text"] if len(t.strip()) > 50][:5000]

# Dataset 2: AG News
ag_news = load_dataset("ag_news", split="train")
datasets_info["ag_news"] = [t for t in ag_news["text"] if len(t.strip()) > 20][:5000]

# Dataset 3: IMDB (replacing tiny_shakespeare)
imdb = load_dataset("imdb", split="train")
datasets_info["imdb"] = [t[:500] for t in imdb["text"] if len(t.strip()) > 100][:5000]

print(
    f"Loaded: wikitext={len(datasets_info['wikitext'])}, ag_news={len(datasets_info['ag_news'])}, imdb={len(datasets_info['imdb'])}"
)


class TextDataset(Dataset):
    def __init__(self, texts, seq_len=96, vocab_size=256):
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.data = []
        for text in texts:
            encoded = [ord(c) % vocab_size for c in text]
            if len(encoded) >= seq_len:
                self.data.append(encoded[:seq_len])
        self.data = np.array(self.data, dtype=np.int64)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        seq = self.data[idx]
        return {"input_ids": torch.tensor(seq[:-1]), "labels": torch.tensor(seq[1:])}


class SmallTransformer(nn.Module):
    def __init__(self, vocab_size=256, d_model=192, nhead=6, num_layers=4, dim_ff=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Parameter(torch.randn(1, 256, d_model) * 0.02)
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


class ImprovedPhaseDetector:
    def __init__(self, total_epochs):
        self.val_losses = []
        self.total_epochs = total_epochs

    def update(self, val_loss):
        self.val_losses.append(val_loss)

    def get_phase(self, current_epoch):
        progress = current_epoch / self.total_epochs
        if progress < 0.33:
            return "memorization"
        elif progress < 0.66:
            return "generalization"
        else:
            return "refinement"


class PADASampler:
    def __init__(self, model, dataset, device):
        self.model = model
        self.dataset = dataset
        self.device = device
        self.gradient_cache = {}
        self.loss_cache = {}

    def compute_sample_scores(self, indices, phase):
        scores = []
        self.model.eval()
        sample_indices = np.random.choice(
            indices, min(500, len(indices)), replace=False
        )

        for idx in sample_indices:
            batch = self.dataset[idx]
            input_ids = batch["input_ids"].unsqueeze(0).to(self.device)
            labels = batch["labels"].unsqueeze(0).to(self.device)

            self.model.zero_grad()
            output = self.model(input_ids)
            loss = F.cross_entropy(output.view(-1, output.size(-1)), labels.view(-1))
            loss.backward()

            grad_norm = (
                sum(
                    p.grad.norm().item() ** 2
                    for p in self.model.parameters()
                    if p.grad is not None
                )
                ** 0.5
            )

            with torch.no_grad():
                probs = F.softmax(output, dim=-1)
                entropy = -(probs * torch.log(probs + 1e-10)).sum(dim=-1).mean().item()

            self.gradient_cache[idx] = grad_norm
            self.loss_cache[idx] = loss.item()

            if phase == "memorization":
                score = grad_norm * (1 + 0.1 * np.random.randn())
            elif phase == "generalization":
                median_grad = (
                    np.median(list(self.gradient_cache.values()))
                    if self.gradient_cache
                    else grad_norm
                )
                score = -abs(grad_norm - median_grad) + entropy
            else:
                score = entropy + 0.5 * loss.item()
            scores.append((idx, score))

        self.model.train()
        return scores

    def select_samples(self, phase, num_samples, all_indices):
        scored = self.compute_sample_scores(all_indices, phase)
        scored.sort(key=lambda x: x[1], reverse=True)
        selected = [idx for idx, _ in scored[: int(num_samples * 0.8)]]
        remaining = list(set(all_indices) - set(selected))
        if remaining:
            extra = np.random.choice(
                remaining, min(int(num_samples * 0.2), len(remaining)), replace=False
            )
            selected.extend(extra)
        return selected[:num_samples]


def evaluate(model, dataloader, device):
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
    return total_loss / total_samples


def train_epoch(model, optimizer, dataloader, device):
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
    return total_loss / total_samples, total_samples


experiment_data = {}
num_epochs = 30
batch_size = 32
lr = 1e-3
sample_ratio = 0.6

for ds_name, texts in datasets_info.items():
    print(f"\n{'='*50}\nDataset: {ds_name}\n{'='*50}")
    train_texts = texts[: int(len(texts) * 0.8)]
    val_texts = texts[int(len(texts) * 0.8) :]
    train_dataset = TextDataset(train_texts)
    val_dataset = TextDataset(val_texts)

    if len(train_dataset) < 100 or len(val_dataset) < 20:
        print(f"Skipping {ds_name}: insufficient data")
        continue

    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    experiment_data[ds_name] = {
        "pada": {
            "losses": {"train": [], "val": []},
            "samples_used": [],
            "phases": [],
            "efficiency": [],
        },
        "random": {
            "losses": {"train": [], "val": []},
            "samples_used": [],
            "efficiency": [],
        },
        "full": {
            "losses": {"train": [], "val": []},
            "samples_used": [],
            "efficiency": [],
        },
    }

    for method in ["pada", "random", "full"]:
        print(f"\n--- {method.upper()} on {ds_name} ---")
        model = SmallTransformer().to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        init_val = evaluate(model, val_loader, device)
        total_samples = 0
        phase_detector = ImprovedPhaseDetector(num_epochs) if method == "pada" else None
        pada_sampler = (
            PADASampler(model, train_dataset, device) if method == "pada" else None
        )

        for epoch in range(num_epochs):
            if method == "pada":
                phase = phase_detector.get_phase(epoch)
                selected = pada_sampler.select_samples(
                    phase,
                    int(len(train_dataset) * sample_ratio),
                    list(range(len(train_dataset))),
                )
                train_loader = DataLoader(
                    Subset(train_dataset, selected), batch_size=batch_size, shuffle=True
                )
                experiment_data[ds_name]["pada"]["phases"].append(phase)
            elif method == "random":
                selected = np.random.choice(
                    len(train_dataset),
                    int(len(train_dataset) * sample_ratio),
                    replace=False,
                )
                train_loader = DataLoader(
                    Subset(train_dataset, selected), batch_size=batch_size, shuffle=True
                )
            else:
                train_loader = DataLoader(
                    train_dataset, batch_size=batch_size, shuffle=True
                )

            train_loss, samples = train_epoch(model, optimizer, train_loader, device)
            total_samples += samples
            val_loss = evaluate(model, val_loader, device)
            efficiency = (
                (init_val - val_loss) / total_samples if total_samples > 0 else 0
            )

            experiment_data[ds_name][method]["losses"]["train"].append(train_loss)
            experiment_data[ds_name][method]["losses"]["val"].append(val_loss)
            experiment_data[ds_name][method]["samples_used"].append(total_samples)
            experiment_data[ds_name][method]["efficiency"].append(efficiency)

            if method == "pada":
                phase_detector.update(val_loss)
                print(
                    f"Epoch {epoch}: validation_loss = {val_loss:.4f}, phase = {phase}"
                )
            else:
                print(f"Epoch {epoch}: validation_loss = {val_loss:.4f}")

print("\n" + "=" * 60 + "\nFINAL RESULTS\n" + "=" * 60)
for ds_name in experiment_data:
    print(f"\n{ds_name}:")
    for method in ["pada", "random", "full"]:
        final_loss = experiment_data[ds_name][method]["losses"]["val"][-1]
        final_samples = experiment_data[ds_name][method]["samples_used"][-1]
        final_eff = experiment_data[ds_name][method]["efficiency"][-1]
        print(
            f"  {method}: val_loss={final_loss:.4f}, samples={final_samples}, efficiency={final_eff:.8f}"
        )
    pada_eff = experiment_data[ds_name]["pada"]["efficiency"][-1]
    random_eff = experiment_data[ds_name]["random"]["efficiency"][-1]
    ratio = pada_eff / random_eff if random_eff != 0 else 0
    print(f"  *** Phase-Specific Sample Efficiency Ratio: {ratio:.4f} ***")

fig, axes = plt.subplots(
    len(experiment_data), 3, figsize=(15, 4 * len(experiment_data))
)
if len(experiment_data) == 1:
    axes = axes.reshape(1, -1)

for i, ds_name in enumerate(experiment_data):
    for method, color in [("pada", "blue"), ("random", "orange"), ("full", "green")]:
        axes[i, 0].plot(
            experiment_data[ds_name][method]["losses"]["val"], label=method, color=color
        )
        axes[i, 1].plot(
            experiment_data[ds_name][method]["samples_used"],
            experiment_data[ds_name][method]["losses"]["val"],
            label=method,
            color=color,
        )
        axes[i, 2].plot(
            experiment_data[ds_name][method]["efficiency"], label=method, color=color
        )
    axes[i, 0].set_title(f"{ds_name}: Val Loss vs Epoch")
    axes[i, 0].legend()
    axes[i, 1].set_title(f"{ds_name}: Val Loss vs Samples")
    axes[i, 1].legend()
    axes[i, 2].set_title(f"{ds_name}: Efficiency")
    axes[i, 2].legend()

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pada_three_datasets.png"), dpi=150)
plt.close()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nResults saved to {working_dir}")
