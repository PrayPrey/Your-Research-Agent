import torch
from torch import nn, Tensor
import torch.nn.functional as F

class LinearProbe(nn.Module):
    def __init__(self, input_dim: int = 2048, num_classes: int = 2):
        super().__init__()
        self.fc = nn.Linear(input_dim, num_classes)

    def forward(self, x: Tensor) -> Tensor:
        return self.fc(x)

def train_probe(probe: LinearProbe, features: Tensor, labels: Tensor,
                lr: float = 0.01, iterations: int = 100, device: str = "cuda") -> LinearProbe:
    probe.train()
    probe.to(device)
    features, labels = features.to(device), labels.to(device)
    optimizer = torch.optim.SGD(probe.parameters(), lr=lr)
    for _ in range(iterations):
        logits = probe(features)
        loss = F.cross_entropy(logits, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    return probe

def evaluate_probe(probe: LinearProbe, features: Tensor, labels: Tensor,
                   device: str = "cuda") -> float:
    probe.eval()
    with torch.no_grad():
        logits = probe(features.to(device))
        preds = logits.argmax(dim=1)
        acc = (preds == labels.to(device)).float().mean()
    return acc.item()
