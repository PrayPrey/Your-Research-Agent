"""Full checkpointed training - save model every epoch."""
import os
import torch
import torch.nn as nn
from tqdm import tqdm

def train_with_full_checkpoints(model, loaders, n_epochs, lr, momentum, weight_decay, device, ckpt_dir):
    """ERM training with checkpoint every epoch."""
    os.makedirs(ckpt_dir, exist_ok=True)
    model = model.to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss()
    ckpt_paths = {}

    for epoch in range(1, n_epochs + 1):
        model.train()
        total_loss = 0
        correct = 0
        total = 0

        for imgs, y, place, idx in tqdm(loaders["train"], desc=f"Epoch {epoch}/{n_epochs}", leave=False):
            imgs, y = imgs.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(imgs)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * imgs.size(0)
            _, pred = logits.max(1)
            correct += pred.eq(y).sum().item()
            total += imgs.size(0)

        path = os.path.join(ckpt_dir, f"epoch_{epoch:03d}.pt")
        torch.save(model.state_dict(), path)
        ckpt_paths[epoch] = path

        print(f"Epoch {epoch}: loss={total_loss/total:.4f}, acc={correct/total:.4f}")

    return ckpt_paths
