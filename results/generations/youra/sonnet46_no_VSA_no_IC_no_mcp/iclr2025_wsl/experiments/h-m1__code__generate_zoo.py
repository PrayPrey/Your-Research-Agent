"""
Generate a synthetic MNIST MLP zoo for NFT training.
Trains N_MODELS small 784→64→10 MLPs on real MNIST data with diverse hyperparameters.
This is the SELF_MODIFY fallback when the Schürholt zoo is unavailable at full scale.
"""
import os
import sys
import random
import torch
import torch.nn as nn
from torch.optim import Adam, SGD
from torchvision import datasets, transforms
from pathlib import Path

N_MODELS = 1000    # enough for NFT training
N_EPOCHS_PER_MODEL = 5
BATCH_SIZE = 256
SAVE_PATH = Path(__file__).parent / "data/synthetic_mnist_zoo.pt"


class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 64)
        self.fc2 = nn.Linear(64, 10)

    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x.view(-1, 784))))


def state_dict_to_flat(sd) -> torch.Tensor:
    return torch.cat([p.float().flatten() for p in sd.values()])


def generate_zoo(n_models=N_MODELS, device="cuda"):
    print(f"Generating synthetic MNIST zoo ({n_models} models)...")
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    train_ds = datasets.MNIST("/tmp/mnist_data", train=True,  download=True, transform=transform)
    test_ds  = datasets.MNIST("/tmp/mnist_data", train=False, download=True, transform=transform)
    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    test_loader  = torch.utils.data.DataLoader(test_ds,  batch_size=512, shuffle=False)

    # Property ranges for diversity
    lrs = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
    epochs_list = [1, 2, 3, 5, 8]
    wd_list = [0.0, 1e-4, 1e-3]

    weights_list = []
    labels_list  = []
    criterion = nn.CrossEntropyLoss()

    rng = random.Random(42)
    for i in range(n_models):
        lr  = rng.choice(lrs)
        ep  = rng.choice(epochs_list)
        wd  = rng.choice(wd_list)

        model = MLP().to(device)
        opt   = Adam(model.parameters(), lr=lr, weight_decay=wd)

        model.train()
        for e in range(ep):
            for xb, yb in train_loader:
                xb, yb = xb.to(device), yb.to(device)
                opt.zero_grad()
                criterion(model(xb), yb).backward()
                opt.step()

        # Test accuracy
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for xb, yb in test_loader:
                xb, yb = xb.to(device), yb.to(device)
                pred = model(xb).argmax(dim=1)
                correct += (pred == yb).sum().item()
                total += len(yb)
        test_acc = correct / total

        # Generalization gap (train - test acc)
        model.eval()
        correct_tr = total_tr = 0
        with torch.no_grad():
            for xb, yb in list(train_loader)[:10]:  # sample
                xb, yb = xb.to(device), yb.to(device)
                pred = model(xb).argmax(dim=1)
                correct_tr += (pred == yb).sum().item()
                total_tr += len(yb)
        train_acc = correct_tr / total_tr
        gen_gap = train_acc - test_acc

        sd_cpu = {k: v.cpu() for k, v in model.state_dict().items()}
        weights_list.append(sd_cpu)
        labels_list.append({
            "test_accuracy": test_acc,
            "generalization_gap": gen_gap,
            "learning_rate": lr,
            "dataset_name": "mnist",
        })

        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{n_models} models generated. Last: acc={test_acc:.3f} lr={lr}")

    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"weights": weights_list, "labels": labels_list}, str(SAVE_PATH))
    print(f"Zoo saved: {SAVE_PATH} ({n_models} models)")
    return str(SAVE_PATH)


if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    generate_zoo(N_MODELS, device=device)
