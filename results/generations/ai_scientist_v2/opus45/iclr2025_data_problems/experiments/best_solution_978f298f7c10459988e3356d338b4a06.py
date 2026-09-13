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
wikitext = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
datasets_info["wikitext"] = [t for t in wikitext["text"] if len(t.strip()) > 50][:6000]
ag_news = load_dataset("ag_news", split="train")
datasets_info["ag_news"] = [t for t in ag_news["text"] if len(t.strip()) > 20][:6000]
imdb = load_dataset("imdb", split="train")
datasets_info["imdb"] = [t[:500] for t in imdb["text"] if len(t.strip()) > 100][:6000]
print(
    f"Loaded: wikitext={len(datasets_info['wikitext'])}, ag_news={len(datasets_info['ag_news'])}, imdb={len(datasets_info['imdb'])}"
)


class TextDataset(Dataset):
    def __init__(self, texts, seq_len=96, vocab_size=256):
        self.seq_len, self.vocab_size = seq_len, vocab_size
        self.data = np.array(
            [
                [ord(c) % vocab_size for c in t[:seq_len]]
                for t in texts
                if len(t) >= seq_len
            ],
            dtype=np.int64,
        )

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return {
            "input_ids": torch.tensor(self.data[idx][:-1]),
            "labels": torch.tensor(self.data[idx][1:]),
        }


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
        x = (
            self.embedding(x) * math.sqrt(self.d_model)
            + self.pos_encoding[:, :seq_len, :]
        )
        mask = nn.Transformer.generate_square_subsequent_mask(seq_len).to(x.device)
        return self.fc_out(self.transformer(x, mask=mask, is_causal=True))


class AdaptivePhaseDetector:
    def __init__(self, window=5):
        self.val_losses, self.window = [], window

    def update(self, val_loss):
        self.val_losses.append(val_loss)

    def get_phase(self):
        if len(self.val_losses) < self.window + 2:
            return "memorization"
        recent = self.val_losses[-self.window :]
        improvements = [recent[i] - recent[i + 1] for i in range(len(recent) - 1)]
        avg_improvement = np.mean(improvements)
        improvement_std = np.std(improvements) + 1e-8
        if avg_improvement > 0.02:
            return "memorization"
        elif avg_improvement > 0.005 or improvement_std > 0.01:
            return "generalization"
        return "refinement"


class ImprovedPADASampler:
    def __init__(self, model, dataset, device):
        self.model, self.dataset, self.device = model, dataset, device
        self.sample_losses = np.ones(len(dataset)) * 10.0
        self.sample_grads = np.ones(len(dataset))
        self.selection_counts = np.zeros(len(dataset))

    def update_scores(self, indices, losses, grads):
        for i, idx in enumerate(indices):
            if i < len(losses) and i < len(grads):
                self.sample_losses[idx] = (
                    0.7 * self.sample_losses[idx] + 0.3 * losses[i]
                )
                self.sample_grads[idx] = 0.7 * self.sample_grads[idx] + 0.3 * grads[i]
                self.selection_counts[idx] += 1

    def select_samples(self, phase, num_samples):
        diversity_bonus = 1.0 / (self.selection_counts + 1)
        if phase == "memorization":
            scores = self.sample_losses * self.sample_grads * diversity_bonus
        elif phase == "generalization":
            median_loss = np.median(self.sample_losses)
            scores = (
                -np.abs(self.sample_losses - median_loss)
                + self.sample_grads * 0.3
                + diversity_bonus * 0.5
            )
        else:
            high_loss_mask = self.sample_losses > np.percentile(self.sample_losses, 60)
            scores = self.sample_losses * high_loss_mask + diversity_bonus * 0.3
        top_k = int(num_samples * 0.7)
        top_indices = np.argsort(scores)[-top_k:]
        remaining = list(set(range(len(self.dataset))) - set(top_indices))
        random_indices = np.random.choice(
            remaining, min(num_samples - top_k, len(remaining)), replace=False
        )
        return list(top_indices) + list(random_indices)


def evaluate(model, dataloader, device):
    model.eval()
    total_loss, total_samples = 0, 0
    with torch.no_grad():
        for batch in dataloader:
            input_ids, labels = batch["input_ids"].to(device), batch["labels"].to(
                device
            )
            output = model(input_ids)
            total_loss += F.cross_entropy(
                output.view(-1, output.size(-1)), labels.view(-1)
            ).item() * input_ids.size(0)
            total_samples += input_ids.size(0)
    return total_loss / total_samples


def train_epoch_with_stats(
    model, optimizer, dataloader, device, sampler=None, indices=None
):
    model.train()
    total_loss, total_samples = 0, 0
    batch_losses, batch_grads = [], []
    for batch in dataloader:
        input_ids, labels = batch["input_ids"].to(device), batch["labels"].to(device)
        optimizer.zero_grad()
        output = model(input_ids)
        loss = F.cross_entropy(output.view(-1, output.size(-1)), labels.view(-1))
        loss.backward()
        grad_norm = (
            sum(
                p.grad.norm().item() ** 2
                for p in model.parameters()
                if p.grad is not None
            )
            ** 0.5
        )
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss += loss.item() * input_ids.size(0)
        total_samples += input_ids.size(0)
        batch_losses.extend([loss.item()] * input_ids.size(0))
        batch_grads.extend([grad_norm] * input_ids.size(0))
    if sampler and indices:
        sampler.update_scores(
            indices[: len(batch_losses)],
            batch_losses[: len(indices)],
            batch_grads[: len(indices)],
        )
    return total_loss / total_samples, total_samples


experiment_data = {}
num_epochs, batch_size, lr, sample_ratio = 35, 32, 1e-3, 0.6
methods = ["pada", "no_phase", "no_sampler", "random", "full"]

for ds_name, texts in datasets_info.items():
    print(f"\n{'='*50}\nDataset: {ds_name}\n{'='*50}")
    train_texts, val_texts = (
        texts[: int(len(texts) * 0.8)],
        texts[int(len(texts) * 0.8) :],
    )
    train_dataset, val_dataset = TextDataset(train_texts), TextDataset(val_texts)
    if len(train_dataset) < 100:
        continue
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    experiment_data[ds_name] = {
        m: {
            "losses": {"train": [], "val": []},
            "samples_used": [],
            "phases": [],
            "efficiency": [],
        }
        for m in methods
    }

    for method in methods:
        print(f"\n--- {method.upper()} ---")
        torch.manual_seed(42)
        np.random.seed(42)
        model = SmallTransformer().to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        init_val = evaluate(model, val_loader, device)
        total_samples = 0
        phase_detector = (
            AdaptivePhaseDetector() if method in ["pada", "no_sampler"] else None
        )
        sampler = (
            ImprovedPADASampler(model, train_dataset, device)
            if method in ["pada", "no_phase"]
            else None
        )

        for epoch in range(num_epochs):
            if method == "pada":
                phase = phase_detector.get_phase()
                indices = sampler.select_samples(
                    phase, int(len(train_dataset) * sample_ratio)
                )
                train_loader = DataLoader(
                    Subset(train_dataset, indices), batch_size=batch_size, shuffle=True
                )
            elif method == "no_phase":
                phase = "memorization"
                indices = sampler.select_samples(
                    phase, int(len(train_dataset) * sample_ratio)
                )
                train_loader = DataLoader(
                    Subset(train_dataset, indices), batch_size=batch_size, shuffle=True
                )
            elif method == "no_sampler":
                phase = phase_detector.get_phase()
                indices = list(
                    np.random.choice(
                        len(train_dataset),
                        int(len(train_dataset) * sample_ratio),
                        replace=False,
                    )
                )
                train_loader = DataLoader(
                    Subset(train_dataset, indices), batch_size=batch_size, shuffle=True
                )
            elif method == "random":
                phase = None
                indices = list(
                    np.random.choice(
                        len(train_dataset),
                        int(len(train_dataset) * sample_ratio),
                        replace=False,
                    )
                )
                train_loader = DataLoader(
                    Subset(train_dataset, indices), batch_size=batch_size, shuffle=True
                )
            else:
                phase = None
                indices = list(range(len(train_dataset)))
                train_loader = DataLoader(
                    train_dataset, batch_size=batch_size, shuffle=True
                )

            train_loss, samples = train_epoch_with_stats(
                model,
                optimizer,
                train_loader,
                device,
                sampler if method in ["pada", "no_phase"] else None,
                indices if method in ["pada", "no_phase"] else None,
            )
            total_samples += samples
            val_loss = evaluate(model, val_loader, device)
            if phase_detector:
                phase_detector.update(val_loss)
            efficiency = (
                (init_val - val_loss) / total_samples * 1e6 if total_samples > 0 else 0
            )
            experiment_data[ds_name][method]["losses"]["train"].append(train_loss)
            experiment_data[ds_name][method]["losses"]["val"].append(val_loss)
            experiment_data[ds_name][method]["samples_used"].append(total_samples)
            experiment_data[ds_name][method]["efficiency"].append(efficiency)
            if phase:
                experiment_data[ds_name][method]["phases"].append(phase)
            phase_str = f", phase={phase}" if phase else ""
            print(f"Epoch {epoch}: validation_loss = {val_loss:.4f}{phase_str}")

print("\n" + "=" * 60 + "\nFINAL RESULTS & COMPONENT ABLATION\n" + "=" * 60)
ablation_results = {}
for ds_name in experiment_data:
    print(f"\n{ds_name}:")
    ablation_results[ds_name] = {}
    pada_eff = experiment_data[ds_name]["pada"]["efficiency"][-1]
    for method in methods:
        d = experiment_data[ds_name][method]
        print(
            f"  {method}: val_loss={d['losses']['val'][-1]:.4f}, samples={d['samples_used'][-1]}, efficiency={d['efficiency'][-1]:.4f}"
        )

    no_phase_eff = experiment_data[ds_name]["no_phase"]["efficiency"][-1]
    no_sampler_eff = experiment_data[ds_name]["no_sampler"]["efficiency"][-1]
    phase_delta = ((pada_eff - no_phase_eff) / (pada_eff + 1e-10)) * 100
    sampler_delta = ((pada_eff - no_sampler_eff) / (pada_eff + 1e-10)) * 100
    ablation_results[ds_name]["phase_detector_delta"] = phase_delta
    ablation_results[ds_name]["sampler_delta"] = sampler_delta
    print(
        f"  *** Phase Detector Contribution (component_ablation_delta): {phase_delta:.2f}% ***"
    )
    print(
        f"  *** Sampler Contribution (component_ablation_delta): {sampler_delta:.2f}% ***"
    )

experiment_data["ablation_results"] = ablation_results

fig, axes = plt.subplots(
    len([d for d in experiment_data if d != "ablation_results"]),
    3,
    figsize=(15, 4 * len([d for d in experiment_data if d != "ablation_results"])),
)
if sum(1 for d in experiment_data if d != "ablation_results") == 1:
    axes = axes.reshape(1, -1)
colors = {
    "pada": "blue",
    "no_phase": "red",
    "no_sampler": "cyan",
    "random": "orange",
    "full": "green",
}
for i, ds_name in enumerate([d for d in experiment_data if d != "ablation_results"]):
    for method, color in colors.items():
        d = experiment_data[ds_name][method]
        axes[i, 0].plot(d["losses"]["val"], label=method, color=color)
        axes[i, 1].plot(
            d["samples_used"], d["losses"]["val"], label=method, color=color
        )
        axes[i, 2].plot(d["efficiency"], label=method, color=color)
    for j, title in enumerate(
        ["Val Loss vs Epoch", "Val Loss vs Samples", "Efficiency"]
    ):
        axes[i, j].set_title(f"{ds_name}: {title}")
        axes[i, j].legend()
        axes[i, j].grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_component_analysis.png"), dpi=150)
plt.close()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
ds_names = [d for d in experiment_data if d != "ablation_results"]
x = np.arange(len(ds_names))
width = 0.15
for idx, method in enumerate(methods):
    final_losses = [experiment_data[ds][method]["losses"]["val"][-1] for ds in ds_names]
    final_effs = [experiment_data[ds][method]["efficiency"][-1] for ds in ds_names]
    axes[0].bar(
        x + idx * width, final_losses, width, label=method, color=colors[method]
    )
    axes[1].bar(x + idx * width, final_effs, width, label=method, color=colors[method])
axes[0].set_xticks(x + 2 * width)
axes[0].set_xticklabels(ds_names)
axes[0].set_ylabel("Final Val Loss")
axes[0].set_title("Final Validation Loss Comparison")
axes[0].legend()
axes[1].set_xticks(x + 2 * width)
axes[1].set_xticklabels(ds_names)
axes[1].set_ylabel("Efficiency")
axes[1].set_title("Sample Efficiency Comparison")
axes[1].legend()

phase_deltas = [ablation_results[ds]["phase_detector_delta"] for ds in ds_names]
sampler_deltas = [ablation_results[ds]["sampler_delta"] for ds in ds_names]
x2 = np.arange(len(ds_names))
axes[2].bar(x2 - 0.2, phase_deltas, 0.4, label="Phase Detector", color="purple")
axes[2].bar(x2 + 0.2, sampler_deltas, 0.4, label="Sampler", color="teal")
axes[2].set_xticks(x2)
axes[2].set_xticklabels(ds_names)
axes[2].set_ylabel("Contribution (%)")
axes[2].set_title("Component Ablation Delta")
axes[2].legend()
axes[2].axhline(y=0, color="black", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_summary.png"), dpi=150)
plt.close()

np.save(
    os.path.join(working_dir, "experiment_data.npy"), experiment_data, allow_pickle=True
)
print(f"\nResults saved to {working_dir}")
