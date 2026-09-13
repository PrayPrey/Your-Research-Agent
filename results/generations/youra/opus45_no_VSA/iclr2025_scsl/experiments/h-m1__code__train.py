import os
import json
import torch
from torch import nn
from torch.optim import SGD
from torch.optim.lr_scheduler import StepLR
import numpy as np
from tqdm import tqdm

from config import Config, SEEDS, set_seed
from data import load_waterbirds, get_dataloader, get_group_indices
from model import build_resnet50

def compute_batch_gradient_ratio(model, data_loader, loss_fn, majority_groups, device):
    model.train()
    maj_norms, min_norms = [], []
    for batch in data_loader:
        images, labels, groups = batch
        images, labels, groups = images.to(device), labels.to(device), groups
        model.zero_grad()
        outputs = model(images)
        loss = loss_fn(outputs, labels)
        loss.backward()
        grad_norm = sum(p.grad.norm().item()**2 for p in model.parameters() if p.grad is not None)**0.5
        maj_mask = torch.tensor([g.item() in majority_groups for g in groups])
        min_mask = ~maj_mask
        if maj_mask.any():
            maj_norms.append(grad_norm * maj_mask.sum().item() / len(groups))
        if min_mask.any():
            min_norms.append(grad_norm * min_mask.sum().item() / len(groups))
    if not maj_norms or not min_norms:
        return 1.0
    return np.mean(maj_norms) / np.mean(min_norms)

def compute_sharpness_ratio_approx(model, minority_loader, majority_loader, loss_fn, device):
    def get_loss_curvature(loader):
        model.eval()
        total_loss = 0.0
        count = 0
        for batch in loader:
            images, labels = batch[0].to(device), batch[1].to(device)
            with torch.no_grad():
                outputs = model(images)
                total_loss += loss_fn(outputs, labels).item() * len(labels)
                count += len(labels)
        return total_loss / max(count, 1)
    loss_min = get_loss_curvature(minority_loader)
    loss_maj = get_loss_curvature(majority_loader)
    if loss_maj == 0:
        return 1.0
    return (loss_min + 0.01) / (loss_maj + 0.01)

def train_one_seed(cfg: Config, seed: int) -> dict:
    set_seed(seed)
    device = cfg.device
    train_dataset = load_waterbirds(cfg.data_root, "train", cfg.image_size)
    train_loader = get_dataloader(train_dataset, cfg.batch_size, shuffle=True, num_workers=cfg.num_workers)
    all_groups = get_group_indices(train_dataset)
    minority_indices = [i for i, g in enumerate(all_groups) if g.item() in cfg.minority_groups]
    majority_indices = [i for i, g in enumerate(all_groups) if g.item() in cfg.majority_groups]
    from torch.utils.data import Subset
    minority_loader = get_dataloader(Subset(train_dataset, minority_indices), cfg.batch_size, shuffle=False, num_workers=cfg.num_workers)
    majority_loader = get_dataloader(Subset(train_dataset, majority_indices), cfg.batch_size, shuffle=False, num_workers=cfg.num_workers)
    model = build_resnet50(cfg.num_classes).to(device)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum, weight_decay=cfg.weight_decay)
    scheduler = StepLR(optimizer, step_size=cfg.step_size, gamma=cfg.gamma)
    r_series = []
    sr_series = []
    for epoch in range(cfg.epochs):
        model.train()
        for batch in tqdm(train_loader, desc=f"Seed {seed} Epoch {epoch+1}/{cfg.epochs}", leave=False):
            images, labels, groups = batch
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = loss_fn(outputs, labels)
            loss.backward()
            optimizer.step()
        r_t = compute_batch_gradient_ratio(model, train_loader, loss_fn, cfg.majority_groups, device)
        r_series.append(r_t)
        sr_t = compute_sharpness_ratio_approx(model, minority_loader, majority_loader, loss_fn, device)
        sr_series.append(sr_t)
        scheduler.step()
        print(f"Seed {seed} Epoch {epoch+1}: r_t={r_t:.4f}, SR_t={sr_t:.4f}")
    return {"r_series": np.array(r_series), "sr_series": np.array(sr_series), "seed": seed}

def main():
    cfg = Config()
    os.makedirs(cfg.results_dir, exist_ok=True)
    all_results = []
    for seed in SEEDS:
        result = train_one_seed(cfg, seed)
        all_results.append(result)
        with open(os.path.join(cfg.results_dir, f"seed_{seed}.json"), "w") as f:
            json.dump({"r_series": result["r_series"].tolist(), "sr_series": result["sr_series"].tolist()}, f)
    with open(os.path.join(cfg.results_dir, "all_seeds.json"), "w") as f:
        json.dump([{"seed": r["seed"], "r_series": r["r_series"].tolist(), "sr_series": r["sr_series"].tolist()} for r in all_results], f)
    print(f"Training complete. Results saved to {cfg.results_dir}")

if __name__ == "__main__":
    main()
