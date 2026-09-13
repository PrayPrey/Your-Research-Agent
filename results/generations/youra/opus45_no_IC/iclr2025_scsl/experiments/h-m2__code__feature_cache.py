"""Feature extraction and caching."""
import os
import numpy as np
import torch
import torch.nn as nn
from tqdm import tqdm
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'h-e1', 'code'))

def load_frozen_backbone(checkpoint_path, num_classes=2, pretrained=True):
    """Load model, freeze, remove fc for feature extraction."""
    from model import build_resnet18
    model = build_resnet18(num_classes=num_classes, pretrained=pretrained)
    model.load_state_dict(torch.load(checkpoint_path, map_location='cpu'))
    model.fc = nn.Identity()
    model.eval()
    model.requires_grad_(False)
    return model

def extract_epoch_features(backbone, loader, device, cache_path):
    """Extract features, cache to disk."""
    if os.path.exists(cache_path):
        data = np.load(cache_path)
        return data["features"], data["bird_labels"], data["bg_labels"]

    backbone = backbone.to(device)
    feats_list, y_list, place_list = [], [], []

    with torch.no_grad():
        for imgs, y, place, idx in tqdm(loader, desc="Extracting", leave=False):
            f = backbone(imgs.to(device))
            feats_list.append(f.cpu().numpy())
            y_list.append(y.numpy())
            place_list.append(place.numpy())

    features = np.concatenate(feats_list)
    bird_labels = np.concatenate(y_list)
    bg_labels = np.concatenate(place_list)

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    np.savez(cache_path, features=features, bird_labels=bird_labels, bg_labels=bg_labels)
    return features, bird_labels, bg_labels
