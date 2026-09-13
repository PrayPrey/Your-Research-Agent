"""Tests for ERMModel."""
import os
import sys
import pytest
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_erm_model_import():
    from models.resnet import ERMModel
    assert ERMModel is not None


def test_erm_model_forward():
    from models.resnet import ERMModel
    model = ERMModel(num_classes=2, pretrained=False)
    x = torch.randn(2, 3, 224, 224)
    logits = model(x)
    assert logits.shape == (2, 2)


def test_feature_extractor_shape():
    from models.resnet import ERMModel
    model = ERMModel(num_classes=2, pretrained=False)
    fe = model.get_feature_extractor()
    x = torch.randn(2, 3, 224, 224)
    feat = fe(x).squeeze(-1).squeeze(-1)
    assert feat.shape == (2, 2048)


def test_save_load_checkpoint(tmp_path):
    from models.resnet import ERMModel, save_checkpoint, load_checkpoint
    model = ERMModel(num_classes=2, pretrained=False)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.001)
    ckpt_path = str(tmp_path / 'test_ckpt.pt')
    save_checkpoint(model, optimizer, epoch=5, path=ckpt_path)
    model2 = ERMModel(num_classes=2, pretrained=False)
    epoch = load_checkpoint(model2, ckpt_path, torch.device('cpu'))
    assert epoch == 5
