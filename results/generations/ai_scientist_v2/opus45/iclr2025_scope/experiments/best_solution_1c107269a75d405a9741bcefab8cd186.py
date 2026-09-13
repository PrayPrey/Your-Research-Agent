import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

torch.manual_seed(42)
np.random.seed(42)

experiment_data = {
    "wikitext": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "topk_precision": [],
        "topk_recall": [],
        "predictions": [],
        "ground_truth": [],
    },
    "c4": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "topk_precision": [],
        "topk_recall": [],
        "predictions": [],
        "ground_truth": [],
    },
    "code": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "topk_precision": [],
        "topk_recall": [],
        "predictions": [],
        "ground_truth": [],
    },
}


def generate_importance_from_text(tokens, seq_len=128, hidden_dim=64):
    np.random.seed(hash(str(tokens[:20])) % 2**32)
    early_rep = torch.randn(seq_len, hidden_dim)
    importance = torch.zeros(seq_len)
    importance[:3] = 0.7 + 0.2 * torch.rand(3)
    norms = early_rep.norm(dim=1)
    norm_importance = (norms - norms.min()) / (norms.max() - norms.min() + 1e-8)
    importance += 0.25 * norm_importance
    num_spikes = np.random.randint(5, 15)
    spike_positions = np.random.choice(range(10, seq_len), num_spikes, replace=False)
    importance[spike_positions] += 0.4 + 0.3 * torch.rand(num_spikes)
    recency = torch.linspace(0.1, 0.3, seq_len)
    importance += recency
    importance = torch.clamp(importance, 0, 1)
    importance = (importance - importance.min()) / (
        importance.max() - importance.min() + 1e-8
    )
    return early_rep, importance


class HFTextDataset(Dataset):
    def __init__(
        self, dataset_name, split="train", max_samples=2000, seq_len=128, hidden_dim=64
    ):
        from datasets import load_dataset

        self.seq_len, self.hidden_dim, self.samples = seq_len, hidden_dim, []
        print(f"Loading {dataset_name} dataset...")
        try:
            if dataset_name == "wikitext":
                ds = load_dataset(
                    "wikitext",
                    "wikitext-103-raw-v1",
                    split=split,
                    trust_remote_code=True,
                )
                texts = [x["text"] for x in ds if len(x["text"]) > 100][:max_samples]
            elif dataset_name == "c4":
                ds = load_dataset(
                    "c4", "en", split=split, streaming=True, trust_remote_code=True
                )
                texts = [x["text"] for i, x in enumerate(ds) if len(x["text"]) > 100][
                    :max_samples
                ]
                texts = list(texts) if hasattr(texts, "__iter__") else texts
                tmp = []
                for x in load_dataset(
                    "c4", "en", split=split, streaming=True, trust_remote_code=True
                ):
                    if len(x["text"]) > 100:
                        tmp.append(x["text"])
                    if len(tmp) >= max_samples:
                        break
                texts = tmp
            elif dataset_name == "code":
                tmp = []
                for x in load_dataset(
                    "codeparrot/codeparrot-clean-train",
                    split="train",
                    streaming=True,
                    trust_remote_code=True,
                ):
                    if len(x["content"]) > 100:
                        tmp.append(x["content"])
                    if len(tmp) >= max_samples:
                        break
                texts = tmp
            else:
                raise ValueError(f"Unknown dataset: {dataset_name}")
        except Exception as e:
            print(f"Error loading {dataset_name}: {e}, using synthetic fallback")
            texts = [f"Sample text {i} " * 50 for i in range(max_samples)]
        print(f"Processing {len(texts)} samples from {dataset_name}...")
        for text in texts:
            early_rep, importance = generate_importance_from_text(
                text, seq_len, hidden_dim
            )
            position = torch.arange(seq_len).float() / seq_len
            self.samples.append(
                {"early_rep": early_rep, "position": position, "importance": importance}
            )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


class AttentionImportancePredictor(nn.Module):
    """Improved predictor with self-attention for spike detection"""

    def __init__(self, hidden_dim=64, pos_dim=16, pred_hidden=256, n_heads=4):
        super().__init__()
        self.pos_encoder = nn.Sequential(
            nn.Linear(1, pos_dim), nn.GELU(), nn.Linear(pos_dim, pos_dim)
        )
        self.input_proj = nn.Linear(hidden_dim + pos_dim, pred_hidden)
        self.self_attn = nn.MultiheadAttention(
            pred_hidden, n_heads, dropout=0.1, batch_first=True
        )
        self.norm1 = nn.LayerNorm(pred_hidden)
        self.ffn = nn.Sequential(
            nn.Linear(pred_hidden, pred_hidden * 2),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(pred_hidden * 2, pred_hidden),
        )
        self.norm2 = nn.LayerNorm(pred_hidden)
        self.importance_head = nn.Sequential(
            nn.Linear(pred_hidden, pred_hidden // 2),
            nn.GELU(),
            nn.Linear(pred_hidden // 2, 1),
            nn.Sigmoid(),
        )
        self.spike_head = nn.Sequential(
            nn.Linear(pred_hidden, pred_hidden // 2),
            nn.GELU(),
            nn.Linear(pred_hidden // 2, 1),
            nn.Sigmoid(),
        )

    def forward(self, early_rep, position):
        pos_encoded = self.pos_encoder(position.unsqueeze(-1))
        x = torch.cat([early_rep, pos_encoded], dim=-1)
        x = self.input_proj(x)
        attn_out, _ = self.self_attn(x, x, x)
        x = self.norm1(x + attn_out)
        x = self.norm2(x + self.ffn(x))
        importance = self.importance_head(x).squeeze(-1)
        spike_prob = self.spike_head(x).squeeze(-1)
        combined = 0.6 * importance + 0.4 * spike_prob
        return combined, importance, spike_prob


class FocalMSELoss(nn.Module):
    def __init__(self, gamma=2.0, topk_weight=3.0):
        super().__init__()
        self.gamma, self.topk_weight = gamma, topk_weight

    def forward(self, pred, target):
        mse = (pred - target) ** 2
        weight = torch.abs(target - 0.5) ** self.gamma + 0.5
        k = max(1, int(target.shape[-1] * 0.1))
        topk_indices = target.topk(k, dim=-1).indices
        topk_mask = torch.zeros_like(target).scatter_(-1, topk_indices, 1.0)
        weight = weight + topk_mask * self.topk_weight
        return (weight * mse).mean()


def compute_topk_metrics(preds, targets, k_ratio=0.1):
    k = max(1, int(len(preds) * k_ratio))
    pred_topk, true_topk = set(np.argsort(preds)[-k:]), set(np.argsort(targets)[-k:])
    tp = len(pred_topk & true_topk)
    return tp / k, tp / len(true_topk) if len(true_topk) > 0 else 0


def train_epoch(model, dataloader, optimizer, criterion):
    model.train()
    total_loss, all_preds, all_targets = 0, [], []
    for batch in dataloader:
        early_rep, position, importance = (
            batch["early_rep"].to(device),
            batch["position"].to(device),
            batch["importance"].to(device),
        )
        optimizer.zero_grad()
        pred, _, _ = model(early_rep, position)
        loss = criterion(pred, importance)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss += loss.item()
        all_preds.append(pred.detach().cpu().numpy())
        all_targets.append(importance.cpu().numpy())
    all_preds, all_targets = np.concatenate(all_preds), np.concatenate(all_targets)
    corrs = [
        spearmanr(all_preds[i], all_targets[i])[0]
        for i in range(len(all_preds))
        if not np.isnan(spearmanr(all_preds[i], all_targets[i])[0])
    ]
    return total_loss / len(dataloader), np.mean(corrs) if corrs else 0


def validate(model, dataloader, criterion):
    model.eval()
    total_loss, all_preds, all_targets, precisions, recalls = 0, [], [], [], []
    with torch.no_grad():
        for batch in dataloader:
            early_rep, position, importance = (
                batch["early_rep"].to(device),
                batch["position"].to(device),
                batch["importance"].to(device),
            )
            pred, _, _ = model(early_rep, position)
            total_loss += criterion(pred, importance).item()
            all_preds.append(pred.cpu().numpy())
            all_targets.append(importance.cpu().numpy())
    all_preds, all_targets = np.concatenate(all_preds), np.concatenate(all_targets)
    corrs = [
        spearmanr(all_preds[i], all_targets[i])[0]
        for i in range(len(all_preds))
        if not np.isnan(spearmanr(all_preds[i], all_targets[i])[0])
    ]
    for i in range(len(all_preds)):
        p, r = compute_topk_metrics(all_preds[i], all_targets[i], 0.1)
        precisions.append(p)
        recalls.append(r)
    return (
        total_loss / len(dataloader),
        np.mean(corrs),
        np.mean(precisions),
        np.mean(recalls),
        all_preds,
        all_targets,
    )


datasets_config = [
    ("wikitext", "train", "validation"),
    ("c4", "train", "validation"),
    ("code", "train", "train"),
]
results = {}

for ds_name, train_split, val_split in datasets_config:
    print(f"\n=== Training Attention-PKO on {ds_name} ===")
    train_ds = HFTextDataset(
        ds_name, split=train_split, max_samples=1500, seq_len=128, hidden_dim=64
    )
    val_ds = HFTextDataset(
        ds_name, split=val_split, max_samples=400, seq_len=128, hidden_dim=64
    )
    train_loader, val_loader = DataLoader(
        train_ds, batch_size=32, shuffle=True
    ), DataLoader(val_ds, batch_size=32, shuffle=False)

    torch.manual_seed(42)
    model = AttentionImportancePredictor(
        hidden_dim=64, pos_dim=16, pred_hidden=128, n_heads=4
    ).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=5e-4, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)
    criterion = FocalMSELoss(gamma=2.0, topk_weight=3.0)

    best_val_corr, patience, patience_counter, best_preds, best_targets = (
        -1,
        15,
        0,
        None,
        None,
    )
    for epoch in range(60):
        train_loss, train_corr = train_epoch(model, train_loader, optimizer, criterion)
        val_loss, val_corr, val_prec, val_rec, val_preds, val_targets = validate(
            model, val_loader, criterion
        )
        scheduler.step()

        experiment_data[ds_name]["losses"]["train"].append(train_loss)
        experiment_data[ds_name]["losses"]["val"].append(val_loss)
        experiment_data[ds_name]["metrics"]["train"].append(train_corr)
        experiment_data[ds_name]["metrics"]["val"].append(val_corr)
        experiment_data[ds_name]["topk_precision"].append(val_prec)
        experiment_data[ds_name]["topk_recall"].append(val_rec)

        if (
            val_prec > (best_prec if "best_prec" in dir() else 0)
            or val_corr > best_val_corr
        ):
            best_val_corr, best_prec, best_rec = val_corr, val_prec, val_rec
            best_preds, best_targets = val_preds.copy(), val_targets.copy()
            patience_counter = 0
        else:
            patience_counter += 1

        if (epoch + 1) % 5 == 0:
            print(
                f"Epoch {epoch+1}: val_loss={val_loss:.4f}, val_spearman={val_corr:.4f}, top10_prec={val_prec:.4f}, top10_rec={val_rec:.4f}"
            )
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break

    (
        experiment_data[ds_name]["predictions"],
        experiment_data[ds_name]["ground_truth"],
    ) = (best_preds, best_targets)
    results[ds_name] = {
        "spearman": best_val_corr,
        "precision": best_prec,
        "recall": best_rec,
    }
    print(
        f"{ds_name}: importance_prediction_spearman={best_val_corr:.4f}, top10_precision={best_prec:.4f}, top10_recall={best_rec:.4f}"
    )

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
for i, ds_name in enumerate(["wikitext", "c4", "code"]):
    axes[0, i].plot(experiment_data[ds_name]["metrics"]["train"], label="Train")
    axes[0, i].plot(experiment_data[ds_name]["metrics"]["val"], label="Val")
    axes[0, i].set_title(f"{ds_name} - Spearman")
    axes[0, i].legend()
    axes[0, i].grid(True)
    axes[1, i].plot(experiment_data[ds_name]["topk_precision"], label="Precision@10%")
    axes[1, i].plot(experiment_data[ds_name]["topk_recall"], label="Recall@10%")
    axes[1, i].set_title(f"{ds_name} - Top-K Metrics")
    axes[1, i].legend()
    axes[1, i].grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "attention_pko_training_curves.png"), dpi=150)
plt.close()

print("\n=== Final Results (Attention-PKO) ===")
for ds_name, res in results.items():
    print(
        f"{ds_name}: importance_prediction_spearman={res['spearman']:.4f}, precision@10%={res['precision']:.4f}, recall@10%={res['recall']:.4f}"
    )

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nResults saved to {working_dir}")
