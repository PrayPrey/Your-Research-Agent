import os
import numpy as np
import torch
import torch.nn as nn
from config import BATCH_SIZE, FEATURE_DIM


def _get_device():
    return 'cuda' if torch.cuda.is_available() else 'cpu'


def load_erm_backbone(device=None):
    if device is None:
        device = _get_device()
    import torchvision.models as tvm
    model = tvm.resnet50(pretrained=True)
    model.fc = nn.Identity()
    model.eval()
    model.to(device)
    return model


def load_moco_backbone(device=None):
    if device is None:
        device = _get_device()
    try:
        model = torch.hub.load('facebookresearch/moco-v3:main', 'resnet50',
                               force_reload=False)
    except Exception:
        model = torch.hub.load('facebookresearch/moco-v3:main', 'resnet50',
                               force_reload=True)
    # MoCo-v3 hub model returns full ResNet; replace fc
    if not isinstance(model.fc, nn.Identity):
        model.fc = nn.Identity()
    model.eval()
    model.to(device)
    return model


def extract_features(model, dataloader, device=None):
    if device is None:
        device = _get_device()
    all_feats = []
    with torch.no_grad():
        for batch in dataloader:
            # WILDS returns (x, y, metadata) — torchvision Subset returns (x, y)
            if isinstance(batch, (list, tuple)):
                images = batch[0]
            else:
                images = batch
            images = images.to(device)
            feats = model(images)
            all_feats.append(feats.cpu().numpy())
    return np.concatenate(all_feats, axis=0).astype(np.float32)


def extract_and_save_celeba_features(paradigm, dataloader, save_path, device=None,
                                     force_recompute=False):
    if os.path.exists(save_path) and not force_recompute:
        print(f"[cache] Loading {paradigm} features from {save_path}")
        return torch.load(save_path, weights_only=True).numpy()

    if device is None:
        device = _get_device()
    loader_fn = load_erm_backbone if paradigm == 'erm' else load_moco_backbone
    print(f"[extract] Loading {paradigm} backbone...")
    model = loader_fn(device)
    print(f"[extract] Extracting {paradigm} features...")
    features = extract_features(model, dataloader, device)
    torch.save(torch.tensor(features), save_path)
    print(f"[extract] Saved {paradigm} features: {features.shape} → {save_path}")
    return features
