import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from evaluate import evaluate_accuracy, measure_delta_acc


class TinyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(4, 2)

    def forward(self, x):
        return self.fc(x)


def make_loader(n=64, d=4, n_classes=2):
    x = torch.randn(n, d)
    y = torch.randint(0, n_classes, (n,))
    return DataLoader(TensorDataset(x, y), batch_size=32)


def test_evaluate_accuracy_returns_float():
    model = TinyModel()
    loader = make_loader()
    device = torch.device("cpu")
    acc = evaluate_accuracy(model, loader, device)
    assert isinstance(acc, float)
    assert 0.0 <= acc <= 1.0


def test_measure_delta_acc_returns_tuple():
    model = TinyModel()
    device = torch.device("cpu")
    sd_orig = {k: v.clone() for k, v in model.state_dict().items()}
    sd_perm = {k: v + 0.01 for k, v in sd_orig.items()}
    loader = make_loader()
    acc_before, acc_after, delta = measure_delta_acc(model, sd_orig, sd_perm, loader, device)
    assert isinstance(acc_before, float)
    assert isinstance(acc_after, float)
    assert isinstance(delta, float)
    assert delta >= 0.0
