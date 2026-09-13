import os
import logging
import torch
import torch.nn as nn
import torchvision.models as tv_models

from config import FEATURE_DIM, CACHE_DIR

_HUB_CACHE = os.path.expanduser('~/.cache/torch/hub')
_MOCO_LOCAL = os.path.join(_HUB_CACHE, 'facebookresearch_moco-v3_main')
_DINO_LOCAL = os.path.join(_HUB_CACHE, 'facebookresearch_dino_main')
_BT_WEIGHTS_URL = 'https://dl.fbaipublicfiles.com/barlowtwins/ljng/resnet50.pth'


def _freeze(model):
    for p in model.parameters():
        p.requires_grad = False
    return model


def _smoke_test(model, device, name):
    with torch.no_grad():
        dummy = torch.randn(2, 3, 224, 224).to(device)
        out = model(dummy)
    assert out.shape == (2, FEATURE_DIM), (
        f"{name}: expected output (2, {FEATURE_DIM}), got {out.shape}"
    )
    logging.info(f"Model {name} smoke test passed: output shape {out.shape}")


def load_erm(device):
    """torchvision resnet50(pretrained=True), fc=Identity, eval, frozen."""
    model = tv_models.resnet50(pretrained=True)
    model.fc = nn.Identity()
    model = _freeze(model).to(device).eval()
    _smoke_test(model, device, 'erm')
    return model


def load_moco(device):
    """MoCo-v3 ResNet-50 backbone via local hub source."""
    model = torch.hub.load(
        _MOCO_LOCAL,
        'resnet50',
        pretrained=True,
        source='local',
        verbose=False,
    )
    # ensure fc is Identity (hubconf.py sets it, but verify)
    if not isinstance(model.fc, nn.Identity):
        model.fc = nn.Identity()
    model = _freeze(model).to(device).eval()
    _smoke_test(model, device, 'moco')
    return model


def load_dino(device):
    """DINO ResNet-50 via local hub source."""
    model = torch.hub.load(
        _DINO_LOCAL,
        'dino_resnet50',
        pretrained=True,
        source='local',
        verbose=False,
    )
    # dino_resnet50 already sets fc=Identity in hubconf
    model = _freeze(model).to(device).eval()
    _smoke_test(model, device, 'dino')
    return model


def load_barlowtwins(device):
    """BarlowTwins ResNet-50: load torchvision backbone + official BarlowTwins weights."""
    model = tv_models.resnet50(pretrained=False)
    model.fc = nn.Identity()
    # Load BarlowTwins pretrained weights
    # Official checkpoint keys: 'model.{resnet_key}' or direct 'backbone.{key}'
    weights_path = os.path.join(_HUB_CACHE, 'checkpoints', 'barlowtwins_resnet50.pth')
    if not os.path.exists(weights_path):
        os.makedirs(os.path.dirname(weights_path), exist_ok=True)
        logging.info(f"Downloading BarlowTwins weights from {_BT_WEIGHTS_URL}")
        state = torch.hub.load_state_dict_from_url(_BT_WEIGHTS_URL, map_location='cpu')
        torch.save(state, weights_path)
    else:
        state = torch.load(weights_path, map_location='cpu')

    # BarlowTwins official checkpoint: dict with 'model' key or direct state_dict
    if isinstance(state, dict) and 'model' in state:
        sd = state['model']
    elif isinstance(state, dict) and 'state_dict' in state:
        sd = state['state_dict']
    else:
        sd = state

    # Strip common prefixes
    cleaned = {}
    for k, v in sd.items():
        for prefix in ('module.backbone.', 'backbone.', 'module.', ''):
            if k.startswith(prefix):
                new_k = k[len(prefix):]
                cleaned[new_k] = v
                break

    msg = model.load_state_dict(cleaned, strict=False)
    logging.info(
        f"BarlowTwins R50 loaded: missing={len(msg.missing_keys)}, unexpected={len(msg.unexpected_keys)}"
    )
    model = _freeze(model).to(device).eval()
    _smoke_test(model, device, 'barlowtwins')
    return model


def extract_features(model, loader, device):
    """
    Returns:
        features:        (N, 2048) float32
        task_labels:     (N,)      int64  — bird species (from y)
        spurious_labels: (N,)      int64  — background (from metadata[:,0])
    """
    feats, task_lbls, spur_lbls = [], [], []
    model.eval()
    with torch.no_grad():
        for batch in loader:
            x, y, metadata = batch
            f = model(x.to(device))
            feats.append(f.cpu())
            task_lbls.append(y.cpu())
            spur_lbls.append(metadata[:, 0].cpu())
    features = torch.cat(feats)
    assert len(features) > 0, "Empty loader — no features extracted"
    assert features.shape[1] == FEATURE_DIM, f"Feature dim mismatch: {features.shape}"
    return features, torch.cat(task_lbls).long(), torch.cat(spur_lbls).long()


def get_or_extract_features(model, loader, device, cache_key, cache_dir=CACHE_DIR):
    """Cache features on disk; reuse across seeds (features are seed-independent)."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"{cache_key}.pt")
    if os.path.exists(path):
        logging.info(f"Loading cached features: {path}")
        feats, task_lbls, spur_lbls = torch.load(path)
        return feats, task_lbls, spur_lbls
    logging.info(f"Extracting features for {cache_key}...")
    feats, task_lbls, spur_lbls = extract_features(model, loader, device)
    torch.save((feats, task_lbls, spur_lbls), path)
    logging.info(f"Cached features saved: {path}")
    return feats, task_lbls, spur_lbls


LOADERS = {
    'erm': load_erm,
    'moco': load_moco,
    'dino': load_dino,
    'barlowtwins': load_barlowtwins,
}
