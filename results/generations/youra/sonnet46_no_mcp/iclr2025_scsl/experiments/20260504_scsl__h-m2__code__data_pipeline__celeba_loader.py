import os
import numpy as np
from PIL import Image
from typing import Dict
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision
import torchvision.transforms as T

from data_pipeline.patch_extractor import PatchExtractor


class CelebAFeatureDataset(Dataset):
    def __init__(self, root: str, indices: np.ndarray, attrs: torch.Tensor,
                 blond_col: int = 9, gender_col: int = 20, transform=None):
        self.root = root
        self.indices = indices
        self.attrs = attrs
        self.blond_col = blond_col
        self.gender_col = gender_col
        self.transform = transform
        self._ds = torchvision.datasets.CelebA(
            root=root, split="train", target_type="attr", download=False
        )

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, i: int):
        idx = int(self.indices[i])
        img, _ = self._ds[idx]
        if self.transform:
            img = self.transform(img)
        return {
            "image": img,
            "spurious_label": int(self.attrs[idx, self.blond_col]),
            "core_label": int(self.attrs[idx, self.gender_col]),
        }


def extract_celeba_patches(
    root: str,
    extractor: PatchExtractor,
    samples_per_group: int = 5000,
    split: str = "train",
) -> Dict[str, np.ndarray]:
    ds = torchvision.datasets.CelebA(
        root=root, split=split, target_type="attr", download=False
    )
    attrs = ds.attr  # [N, 40]
    blond_col, gender_col = 9, 20

    groups = [(0, 0), (0, 1), (1, 0), (1, 1)]
    rng = np.random.RandomState(42)

    all_spurious, all_core = [], []
    all_sl, all_cl = [], []

    for (b, g) in groups:
        mask = (attrs[:, blond_col] == b) & (attrs[:, gender_col] == g)
        indices = np.where(mask.numpy())[0]
        n_take = min(samples_per_group, len(indices))
        if n_take == 0:
            print(f"  Warning: group (blond={b}, gender={g}) has 0 samples")
            continue
        chosen = rng.choice(indices, size=n_take, replace=False)
        print(f"  Group (blond={b}, gender={g}): {n_take} samples")

        for idx in chosen:
            img_pil, _ = ds[int(idx)]
            img_arr = np.array(img_pil)
            sp_patch, co_patch = extractor.extract_celeba_patches(img_arr)
            all_spurious.append(sp_patch)
            all_core.append(co_patch)
            all_sl.append(b)
            all_cl.append(g)

    N = len(all_spurious)
    print(f"CelebA: {N} patches extracted across {len(groups)} groups")

    return {
        "spurious_patches": np.stack(all_spurious, axis=0),
        "core_patches": np.stack(all_core, axis=0),
        "spurious_labels": np.array(all_sl, dtype=np.int64),
        "core_labels": np.array(all_cl, dtype=np.int64),
    }


def get_celeba_feature_loader(
    root: str,
    samples_per_group: int = 5000,
    batch_size: int = 256,
    num_workers: int = 4,
) -> DataLoader:
    transform = T.Compose([
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    ds_raw = torchvision.datasets.CelebA(
        root=root, split="train", target_type="attr", download=False
    )
    attrs = ds_raw.attr
    blond_col, gender_col = 9, 20
    groups = [(0, 0), (0, 1), (1, 0), (1, 1)]
    rng = np.random.RandomState(42)
    all_indices = []
    for (b, g) in groups:
        mask = (attrs[:, blond_col] == b) & (attrs[:, gender_col] == g)
        indices = np.where(mask.numpy())[0]
        n_take = min(samples_per_group, len(indices))
        chosen = rng.choice(indices, size=n_take, replace=False)
        all_indices.extend(chosen.tolist())

    all_indices = np.array(all_indices)
    dataset = CelebAFeatureDataset(root, all_indices, attrs, blond_col, gender_col, transform)
    return DataLoader(dataset, batch_size=batch_size, shuffle=False,
                      num_workers=num_workers, pin_memory=True)
