import os
import torch
from torch import nn
from torch.optim.lr_scheduler import MultiStepLR
from tqdm import tqdm

from model import build_resnet50
from data import get_loaders
from evaluate import evaluate_epoch
from detector import CrystallizationDetector
from gradient_tracker import GradientTracker
from config import Config

def train_one_epoch_tracked(
    model, loader, optimizer, criterion, device, tracker: GradientTracker
) -> tuple:
    model.train()
    total_loss = 0.0
    n_batches = 0
    epoch_ratios = []
    epoch_group_norms = {}
    for x, y, metadata in loader:
        x, y = x.to(device), y.to(device)
        groups = metadata[:, 0].to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        ratio, group_norms = tracker.compute_group_gradient_ratio(groups)
        if ratio is not None:
            epoch_ratios.append(ratio)
            for g, norm in group_norms.items():
                epoch_group_norms.setdefault(g, []).append(norm)
        optimizer.step()
        total_loss += loss.item()
        n_batches += 1
    avg_loss = total_loss / max(n_batches, 1)
    avg_ratio = sum(epoch_ratios) / len(epoch_ratios) if epoch_ratios else 0.0
    avg_group_norms = {g: sum(norms)/len(norms) for g, norms in epoch_group_norms.items()}
    return avg_loss, avg_ratio, avg_group_norms

def train(dataset_name: str, cfg: Config) -> dict:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(cfg.seed)

    model = build_resnet50(num_classes=2, pretrained=True).to(device)
    optimizer = torch.optim.SGD(
        model.parameters(), lr=cfg.lr, momentum=cfg.momentum, weight_decay=cfg.weight_decay
    )
    scheduler = MultiStepLR(optimizer, milestones=cfg.lr_milestones, gamma=cfg.lr_gamma)
    criterion = nn.CrossEntropyLoss()
    loaders = get_loaders(dataset_name, cfg.batch_size, cfg.data_root)

    n_epochs = cfg.epochs_waterbirds if dataset_name == "waterbirds" else cfg.epochs_celeba
    detector = CrystallizationDetector(cfg.smoothing_window)
    tracker = GradientTracker(model, cfg.majority_group_id, cfg.minority_group_id)

    wga_history = []
    group_acc_history = []

    os.makedirs(cfg.checkpoint_dir, exist_ok=True)

    for epoch in tqdm(range(n_epochs), desc=f"Training {dataset_name}"):
        _, avg_ratio, avg_group_norms = train_one_epoch_tracked(
            model, loaders["train"], optimizer, criterion, device, tracker
        )
        tracker.log_epoch_gradients(epoch, avg_ratio, avg_group_norms)
        scheduler.step()
        wga, group_acc = evaluate_epoch(model, loaders["val"], device)
        wga_history.append(wga)
        group_acc_history.append(group_acc)
        detector.log_epoch(wga)

        if (epoch + 1) % cfg.checkpoint_every == 0:
            ckpt_path = os.path.join(cfg.checkpoint_dir, f"{dataset_name}_epoch{epoch}.pt")
            torch.save(model.state_dict(), ckpt_path)

    tracker.remove()

    return {
        "wga_history": wga_history,
        "group_acc_history": group_acc_history,
        "detector": detector,
        "gradient_history": tracker.gradient_history,
        "gradient_ratio_history": tracker.get_ratio_history(),
        "group_norm_history": tracker.get_group_norm_history(),
        "n_epochs": n_epochs
    }
