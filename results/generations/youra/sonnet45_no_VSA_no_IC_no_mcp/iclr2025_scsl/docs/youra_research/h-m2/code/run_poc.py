import os
import torch
import torch.nn as nn
from torch.optim import SGD
import csv
from data_loader import get_waterbirds_dataloader
from models import create_resnet_bn, create_resnet_cbam, create_vit_small


def set_seed(seed):
    torch.manual_seed(seed)


def evaluate(model, loader, device):
    """Evaluate model on loader, return metrics dict."""
    model.eval()
    all_preds = []
    all_labels = []
    all_groups = []

    with torch.no_grad():
        for batch in loader:
            images, labels, metadata = batch
            images = images.to(device)
            labels = labels.to(device)
            groups = metadata[:, 0].long()

            logits = model(images)
            preds = logits.argmax(dim=1)

            all_preds.append(preds.cpu())
            all_labels.append(labels.cpu())
            all_groups.append(groups.cpu())

    all_preds = torch.cat(all_preds)
    all_labels = torch.cat(all_labels)
    all_groups = torch.cat(all_groups)

    correct = (all_preds == all_labels).float()
    avg_acc = correct.mean().item()

    group_accs = []
    for g in range(4):
        mask = all_groups == g
        if mask.sum() > 0:
            group_accs.append(correct[mask].mean().item())
        else:
            group_accs.append(0.0)

    worst_group_acc = min(group_accs)
    worst_group_gap = avg_acc - worst_group_acc

    return {
        'avg_acc': avg_acc,
        'worst_group_acc': worst_group_acc,
        'worst_group_gap': worst_group_gap,
        'group_0_acc': group_accs[0],
        'group_1_acc': group_accs[1],
        'group_2_acc': group_accs[2],
        'group_3_acc': group_accs[3]
    }


def train_one_epoch(model, loader, optimizer, criterion, device):
    """Train for one epoch, return avg loss."""
    model.train()
    total_loss = 0.0
    count = 0

    for batch in loader:
        images, labels, metadata = batch
        images = images.to(device)
        labels = labels.to(device)

        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        total_loss += loss.item()
        count += 1

    return total_loss / count


def train_one_run(arch_name, seed, num_epochs=10, device='cpu'):
    """Train single run (POC: 10 epochs, 2 seeds)."""
    set_seed(seed)

    if arch_name == 'resnet_bn':
        model = create_resnet_bn()
    elif arch_name == 'resnet_cbam':
        model = create_resnet_cbam()
    elif arch_name == 'vit_small':
        model = create_vit_small()
    else:
        raise ValueError(f"Unknown architecture: {arch_name}")

    model = model.to(device)

    train_loader = get_waterbirds_dataloader('train', batch_size=64, num_workers=0)
    test_loader = get_waterbirds_dataloader('test', batch_size=64, num_workers=0)

    optimizer = SGD(model.parameters(), lr=0.01, momentum=0.9, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    log_path = f'../results/logs/{arch_name}_{seed}.csv'
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    with open(log_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'epoch', 'seed', 'architecture', 'avg_acc', 'worst_group_acc', 'worst_group_gap',
            'train_loss', 'group_0_acc', 'group_1_acc', 'group_2_acc', 'group_3_acc'
        ])
        writer.writeheader()

        for epoch in range(num_epochs):
            train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
            metrics = evaluate(model, test_loader, device)

            row = {
                'epoch': epoch,
                'seed': seed,
                'architecture': arch_name,
                'avg_acc': metrics['avg_acc'],
                'worst_group_acc': metrics['worst_group_acc'],
                'worst_group_gap': metrics['worst_group_gap'],
                'train_loss': train_loss,
                'group_0_acc': metrics['group_0_acc'],
                'group_1_acc': metrics['group_1_acc'],
                'group_2_acc': metrics['group_2_acc'],
                'group_3_acc': metrics['group_3_acc']
            }
            writer.writerow(row)

            print(f"{arch_name} seed={seed} epoch={epoch} avg_acc={metrics['avg_acc']:.4f} gap={metrics['worst_group_gap']:.4f}")

    checkpoint_path = f'../results/checkpoints/{arch_name}_{seed}.pt'
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
    torch.save({'epoch': num_epochs-1, 'model': model.state_dict()}, checkpoint_path)

    print(f"Completed {arch_name} seed={seed}")


if __name__ == '__main__':
    device = 'cpu'
    architectures = ['resnet_bn', 'resnet_cbam', 'vit_small']
    seeds = [0, 1]

    for arch in architectures:
        for seed in seeds:
            train_one_run(arch, seed, num_epochs=10, device=device)

    print("\nAll POC runs complete")
