import clip
import torch
import numpy as np
from torch.utils.data import DataLoader
from tqdm import tqdm


def load_clip_model(device: str) -> tuple:
    model, preprocess = clip.load("ViT-B/16", device=device)
    model.eval()
    return model, preprocess


def extract_features(dataset, model, device: str, batch_size: int = 100) -> tuple:
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=4)

    all_features = []
    all_y = []
    all_place = []

    with torch.no_grad():
        for images, y, place in tqdm(loader, desc="Extracting features"):
            features = model.encode_image(images.to(device))
            features = features / features.norm(dim=-1, keepdim=True)
            all_features.append(features.cpu().numpy())
            all_y.append(y.numpy())
            all_place.append(place.numpy())

    features = np.concatenate(all_features, axis=0)
    y = np.concatenate(all_y, axis=0)
    place = np.concatenate(all_place, axis=0)

    return features, y, place


def cache_features(path: str, features: np.ndarray, y: np.ndarray, place: np.ndarray) -> None:
    np.savez(path, features=features, y=y, place=place)


def load_cached_features(path: str) -> tuple:
    data = np.load(path)
    return data["features"], data["y"], data["place"]
