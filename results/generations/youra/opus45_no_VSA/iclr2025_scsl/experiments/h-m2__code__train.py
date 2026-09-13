import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from collections import Counter

from config import CONFIG
from data import WaterbirdDataset, get_train_loader
from model import create_pretrained_model
from parity import UpdateNormParityTrainer
from sharpness import compute_sharpness_ratio
from metrics import per_group_accuracy, worst_group_accuracy


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> tuple:
    model.eval()
    y_true, y_pred, groups = [], [], []
    with torch.no_grad():
        for x, y, g in loader:
            x = x.double().to(device)
            logits = model(x)
            preds = logits.argmax(dim=1).cpu().tolist()
            y_true.extend(y.tolist())
            y_pred.extend(preds)
            groups.extend(g.tolist())
    model.train()
    return y_true, y_pred, groups


def train_one_variant(variant: str, seed: int, cfg, device: torch.device) -> dict:
    print(f"\n=== Training {variant} seed={seed} ===")

    model = create_pretrained_model(seed).to(device)
    train_dataset = WaterbirdDataset(cfg.data_root, "train")
    val_dataset = WaterbirdDataset(cfg.data_root, "val")

    train_loader = get_train_loader(train_dataset, cfg.batch_size)
    val_loader = DataLoader(val_dataset, batch_size=cfg.batch_size, shuffle=False, num_workers=2)

    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=cfg.lr,
        momentum=cfg.momentum,
        weight_decay=cfg.weight_decay
    )
    criterion = nn.CrossEntropyLoss()

    scale_map = {"baseline": 0.0, "full_parity": cfg.full_scale, "partial_parity": cfg.partial_scale}
    scale = scale_map[variant]
    trainer = UpdateNormParityTrainer(model, cfg.num_groups, scale) if scale > 0 else None

    best_wga = -float('inf')
    patience_ctr = 0
    sr_value = None
    update_norms = []

    all_groups = cfg.minority_groups + cfg.majority_groups

    for epoch in range(cfg.epochs):
        model.train()
        epoch_loss = 0.0

        for batch_idx, (x, y, g) in enumerate(train_loader):
            x = x.double().to(device)
            y = y.to(device)
            g = g.to(device)

            if trainer is not None and scale > 0:
                group_norms = trainer.compute_group_grad_norms(
                    train_dataset, all_groups, min(cfg.batch_size, 64), criterion, device
                )
                optimizer.zero_grad()
                loss = criterion(model(x), y)
                loss.backward()
                target_group = Counter(g.tolist()).most_common(1)[0][0]
                log = trainer.apply_parity_scaling(group_norms, target_group)
                if batch_idx % 50 == 0:
                    update_norms.append(log)
            else:
                optimizer.zero_grad()
                loss = criterion(model(x), y)
                loss.backward()

            optimizer.step()
            epoch_loss += loss.item()

        y_t, y_p, grp = evaluate(model, val_loader, device)
        wga = worst_group_accuracy(y_t, y_p, grp)
        avg_acc = sum(1 for a, b in zip(y_t, y_p) if a == b) / len(y_t)

        print(f"  Epoch {epoch+1}: loss={epoch_loss/len(train_loader):.4f}, WGA={wga:.4f}, Avg={avg_acc:.4f}")

        if epoch + 1 == cfg.sr_eval_epoch:
            print(f"  Computing SR at epoch {cfg.sr_eval_epoch}...")
            sr_value = compute_sharpness_ratio(model, train_dataset)
            print(f"  SR = {sr_value:.4f}")

        if wga > best_wga:
            best_wga = wga
            patience_ctr = 0
        else:
            patience_ctr += 1

        if patience_ctr >= cfg.early_stop_patience:
            print(f"  Early stop at epoch {epoch+1}")
            break

    if sr_value is None:
        print("  Computing final SR...")
        sr_value = compute_sharpness_ratio(model, train_dataset)
        print(f"  SR = {sr_value:.4f}")

    y_t, y_p, grp = evaluate(model, val_loader, device)
    final_wga = worst_group_accuracy(y_t, y_p, grp)
    final_per_group = per_group_accuracy(y_t, y_p, grp)

    return {
        "variant": variant,
        "seed": seed,
        "sr": sr_value,
        "wga": final_wga,
        "per_group_acc": final_per_group,
        "update_norms": update_norms,
    }
