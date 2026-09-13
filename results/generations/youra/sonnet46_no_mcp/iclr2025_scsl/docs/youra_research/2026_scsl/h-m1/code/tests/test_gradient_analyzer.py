import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
from unittest.mock import MagicMock
from gradient_analyzer import GradientAlignmentAnalyzer
from train import build_model


def make_loader(n=32, batch_size=16):
    images = torch.randn(n, 3, 224, 224)
    core = torch.randint(0, 2, (n,))
    spurious = torch.randint(0, 2, (n,))
    dataset = [{"image": images[i], "core_label": core[i].item(), "spurious_label": spurious[i].item()} for i in range(n)]

    def collate(batch):
        return {
            "image": torch.stack([b["image"] for b in batch]),
            "core_label": torch.tensor([b["core_label"] for b in batch]),
            "spurious_label": torch.tensor([b["spurious_label"] for b in batch]),
        }

    return torch.utils.data.DataLoader(dataset, batch_size=batch_size, collate_fn=collate)


def test_extract_features_shapes():
    device = "cpu"
    model = build_model(pretrained=False).to(device)
    analyzer = GradientAlignmentAnalyzer(model, device)
    loader = make_loader(n=32, batch_size=16)
    features, core_labels, spurious_labels = analyzer.extract_features(loader)
    assert features.shape == (32, 2048)
    assert core_labels.shape == (32,)
    assert spurious_labels.shape == (32,)


def test_compute_label_gradient_norm_positive():
    device = "cpu"
    model = build_model(pretrained=False).to(device)
    analyzer = GradientAlignmentAnalyzer(model, device)
    loader = make_loader(n=32, batch_size=16)
    features, core_labels, _ = analyzer.extract_features(loader)
    criterion = nn.CrossEntropyLoss()
    norm = analyzer.compute_label_gradient_norm(features, core_labels, criterion)
    assert isinstance(norm, float)
    assert norm > 0


def test_log_epoch_gradients_keys():
    device = "cpu"
    model = build_model(pretrained=False).to(device)
    analyzer = GradientAlignmentAnalyzer(model, device)
    loader = make_loader(n=32, batch_size=16)
    criterion = nn.CrossEntropyLoss()
    result = analyzer.log_epoch_gradients(loader, criterion)
    assert "spurious_grad_norm" in result
    assert "core_grad_norm" in result
    assert "gdr" in result


def test_get_history_length():
    device = "cpu"
    model = build_model(pretrained=False).to(device)
    analyzer = GradientAlignmentAnalyzer(model, device)
    loader = make_loader(n=32, batch_size=16)
    criterion = nn.CrossEntropyLoss()
    for _ in range(15):
        analyzer.log_epoch_gradients(loader, criterion)
    history = analyzer.get_history()
    assert len(history["gdr_series"]) == 15
    assert len(history["spurious_grad_norms"]) == 15
    assert len(history["core_grad_norms"]) == 15
