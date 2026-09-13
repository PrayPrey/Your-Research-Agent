import os
import sys

# Fix for isatty issue with redirected stdout
if not hasattr(sys.stdout, "isatty"):
    sys.stdout.isatty = lambda: False
if not hasattr(sys.stderr, "isatty"):
    sys.stderr.isatty = lambda: False

os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel, logging
from datasets import load_dataset
from scipy.stats import spearmanr
import warnings

warnings.filterwarnings("ignore")
logging.set_verbosity_error()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

experiment_data = {
    "wikitext": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "spearman": [],
    },
    "ag_news": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "spearman": [],
    },
    "code": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "spearman": [],
    },
    "cdcs_history": [],
    "epoch_losses": {"train": [], "val": []},
}

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
base_model = AutoModel.from_pretrained(
    "distilbert-base-uncased", output_attentions=True
)
base_model = base_model.to(device)
base_model.eval()


def compute_importance_scores(attention_weights, seq_len):
    all_attn = torch.stack(attention_weights, dim=0)
    avg_attn = all_attn.mean(dim=(0, 2))
    importance = avg_attn.sum(dim=1)
    importance = importance / (importance.max(dim=-1, keepdim=True)[0] + 1e-8)
    return importance


class ImportanceDataset(Dataset):
    def __init__(self, texts, tokenizer, base_model, max_len=128, device="cpu"):
        self.features, self.importance_scores = [], []
        base_model.eval()
        with torch.no_grad():
            for text in texts:
                if len(text.strip()) < 10:
                    continue
                encoded = tokenizer(
                    text,
                    truncation=True,
                    max_length=max_len,
                    padding="max_length",
                    return_tensors="pt",
                )
                input_ids = encoded["input_ids"].to(device)
                attention_mask = encoded["attention_mask"].to(device)
                outputs = base_model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_attentions=True,
                    output_hidden_states=True,
                )
                hidden = outputs.hidden_states[1][0].cpu()
                importance = compute_importance_scores(outputs.attentions, max_len)[
                    0
                ].cpu()
                self.features.append(hidden)
                self.importance_scores.append(importance)
                if len(self.features) >= 500:
                    break

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.importance_scores[idx]


class PKOPredictor(nn.Module):
    def __init__(self, hidden_dim=768, num_domains=3):
        super().__init__()
        self.local_conv = nn.Conv1d(hidden_dim, 128, kernel_size=3, padding=1)
        self.attention = nn.MultiheadAttention(
            hidden_dim, num_heads=4, batch_first=True
        )
        self.layer_norm = nn.LayerNorm(hidden_dim)
        self.domain_bns = nn.ModuleList(
            [nn.BatchNorm1d(hidden_dim) for _ in range(num_domains)]
        )
        self.predictor = nn.Sequential(
            nn.Linear(hidden_dim + 128, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )
        self.pos_encoding = nn.Parameter(torch.randn(1, 512, hidden_dim) * 0.02)

    def forward(self, x, domain_id=0):
        batch_size, seq_len, _ = x.shape
        x = x + self.pos_encoding[:, :seq_len, :]
        attn_out, _ = self.attention(x, x, x)
        x = self.layer_norm(x + attn_out)
        x_permuted = x.permute(0, 2, 1)
        if domain_id < len(self.domain_bns):
            x_permuted = self.domain_bns[domain_id](x_permuted)
        x = x_permuted.permute(0, 2, 1)
        local_feat = F.relu(self.local_conv(x.permute(0, 2, 1))).permute(0, 2, 1)
        combined = torch.cat([x, local_feat], dim=-1)
        return torch.sigmoid(self.predictor(combined).squeeze(-1))


def ranking_loss(pred, target, margin=0.1):
    batch_size, seq_len = pred.shape
    n_pairs = min(100, seq_len * (seq_len - 1) // 2)
    idx1 = torch.randint(0, seq_len, (batch_size, n_pairs), device=pred.device)
    idx2 = torch.randint(0, seq_len, (batch_size, n_pairs), device=pred.device)
    pred1, pred2 = torch.gather(pred, 1, idx1), torch.gather(pred, 1, idx2)
    target1, target2 = torch.gather(target, 1, idx1), torch.gather(target, 1, idx2)
    return F.relu(margin - (pred1 - pred2) * torch.sign(target1 - target2)).mean()


def combined_loss(pred, target, alpha=0.5):
    return F.mse_loss(pred, target) + alpha * ranking_loss(pred, target)


def compute_metrics(pred, target):
    pred_np, target_np = (
        pred.detach().cpu().numpy().flatten(),
        target.detach().cpu().numpy().flatten(),
    )
    mask = target_np > 0.01
    if mask.sum() < 10:
        return 0.0, 0.0, 0.0
    pred_np, target_np = pred_np[mask], target_np[mask]
    spearman, _ = spearmanr(pred_np, target_np)
    spearman = 0.0 if np.isnan(spearman) else spearman
    k = max(1, len(target_np) // 10)
    top_k_pred, top_k_target = set(np.argsort(pred_np)[-k:]), set(
        np.argsort(target_np)[-k:]
    )
    precision = len(top_k_pred & top_k_target) / k
    recall = len(top_k_pred & top_k_target) / len(top_k_target) if top_k_target else 0
    return spearman, precision, recall


def compute_cdcs(spearman_scores):
    scores = np.array([s for s in spearman_scores if s > 0])
    if len(scores) == 0:
        return 0.0
    harmonic_mean = len(scores) / np.sum(1.0 / (scores + 1e-8))
    cv = min(np.std(scores) / (np.mean(scores) + 1e-8), 1.0)
    return harmonic_mean * (1 - cv)


print("Loading datasets...")
wikitext_texts = [
    t
    for t in load_dataset("wikitext", "wikitext-2-raw-v1", split="train")["text"]
    if len(t.strip()) > 50
][:1000]
ag_news_texts = [
    t for t in load_dataset("ag_news", split="train")["text"] if len(t.strip()) > 50
][:1000]
code_texts = [
    t
    for t in load_dataset("code_search_net", "python", split="train")[
        "whole_func_string"
    ]
    if t and len(t.strip()) > 50
][:1000]

print("Extracting features...")
datasets = {
    "wikitext": ImportanceDataset(wikitext_texts, tokenizer, base_model, device=device),
    "ag_news": ImportanceDataset(ag_news_texts, tokenizer, base_model, device=device),
    "code": ImportanceDataset(code_texts, tokenizer, base_model, device=device),
}

train_loaders, val_loaders = {}, {}
for name, ds in datasets.items():
    n, train_size = len(ds), int(len(ds) * 0.8)
    train_ds, val_ds = torch.utils.data.random_split(ds, [train_size, n - train_size])
    train_loaders[name] = DataLoader(train_ds, batch_size=16, shuffle=True)
    val_loaders[name] = DataLoader(val_ds, batch_size=16)

domain_to_id = {"wikitext": 0, "ag_news": 1, "code": 2}
model = PKOPredictor(hidden_dim=768, num_domains=3).to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=20)

for epoch in range(20):
    model.train()
    total_train_loss, train_batches = 0, 0
    domain_iters = {d: iter(loader) for d, loader in train_loaders.items()}
    active_domains = set(domain_iters.keys())
    while active_domains:
        for domain in list(active_domains):
            try:
                features, importance = next(domain_iters[domain])
            except StopIteration:
                active_domains.discard(domain)
                continue
            features, importance = features.to(device), importance.to(device)
            optimizer.zero_grad()
            loss = combined_loss(
                model(features, domain_to_id[domain]), importance, alpha=0.3
            )
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_train_loss += loss.item()
            train_batches += 1
    scheduler.step()
    experiment_data["epoch_losses"]["train"].append(
        total_train_loss / max(train_batches, 1)
    )

    model.eval()
    total_val_loss, val_batches, domain_spearman, domain_precision = 0, 0, {}, {}
    with torch.no_grad():
        for domain, loader in val_loaders.items():
            preds, targets, domain_loss = [], [], 0
            for features, importance in loader:
                features, importance = features.to(device), importance.to(device)
                pred = model(features, domain_to_id[domain])
                domain_loss += combined_loss(pred, importance, alpha=0.3).item()
                preds.append(pred)
                targets.append(importance)
                val_batches += 1
            if preds:
                all_preds, all_targets = torch.cat(preds), torch.cat(targets)
                spearman, precision, recall = compute_metrics(all_preds, all_targets)
                domain_spearman[domain], domain_precision[domain] = spearman, precision
                experiment_data[domain]["spearman"].append(spearman)
                total_val_loss += domain_loss

    avg_val_loss = total_val_loss / max(val_batches, 1)
    experiment_data["epoch_losses"]["val"].append(avg_val_loss)
    cdcs = compute_cdcs(
        [domain_spearman.get(d, 0) for d in ["wikitext", "ag_news", "code"]]
    )
    experiment_data["cdcs_history"].append(cdcs)
    print(
        f"Epoch {epoch+1}/20: validation_loss = {avg_val_loss:.4f}, CDCS = {cdcs:.4f}"
    )
    print(f"  Spearman: {domain_spearman}")

final_spearman, final_precision, final_recall = {}, {}, {}
model.eval()
with torch.no_grad():
    for domain, loader in val_loaders.items():
        preds, targets = [], []
        for features, importance in loader:
            preds.append(model(features.to(device), domain_to_id[domain]))
            targets.append(importance.to(device))
        if preds:
            all_preds, all_targets = torch.cat(preds), torch.cat(targets)
            final_spearman[domain], final_precision[domain], final_recall[domain] = (
                compute_metrics(all_preds, all_targets)
            )
            experiment_data[domain]["predictions"] = all_preds.cpu().numpy()
            experiment_data[domain]["ground_truth"] = all_targets.cpu().numpy()

final_cdcs = compute_cdcs(
    [final_spearman.get(d, 0) for d in ["wikitext", "ag_news", "code"]]
)
print(f"\nFINAL CDCS: {final_cdcs:.4f}")
print(f"Final Spearman: {final_spearman}")

experiment_data["final_results"] = {
    "spearman": final_spearman,
    "precision": final_precision,
    "recall": final_recall,
    "cdcs": final_cdcs,
}
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes[0, 0].plot(experiment_data["epoch_losses"]["train"], label="Train")
axes[0, 0].plot(experiment_data["epoch_losses"]["val"], label="Val")
axes[0, 0].legend()
axes[0, 0].set_title("Loss")
for domain in ["wikitext", "ag_news", "code"]:
    axes[0, 1].plot(experiment_data[domain]["spearman"], label=domain)
axes[0, 1].legend()
axes[0, 1].set_title("Spearman")
axes[1, 0].plot(experiment_data["cdcs_history"])
axes[1, 0].set_title("CDCS")
x = np.arange(3)
axes[1, 1].bar(x, [final_spearman.get(d, 0) for d in ["wikitext", "ag_news", "code"]])
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(["wikitext", "ag_news", "code"])
axes[1, 1].set_title(f"Final (CDCS={final_cdcs:.4f})")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pko_results.png"), dpi=150)
plt.close()
print("Done!")
