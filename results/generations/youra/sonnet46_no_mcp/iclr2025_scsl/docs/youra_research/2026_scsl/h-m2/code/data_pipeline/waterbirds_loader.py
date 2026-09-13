import os
import numpy as np
import pandas as pd
from PIL import Image
from typing import Dict, Any, Optional
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T

from data_pipeline.patch_extractor import PatchExtractor


class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: str = "train", transform=None):
        self.root = root
        self.transform = transform

        meta_path = os.path.join(root, "metadata.csv")
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"metadata.csv not found at {meta_path}")

        df = pd.read_csv(meta_path)
        split_map = {"train": 0, "val": 1, "test": 2}
        split_id = split_map.get(split, 0)
        self.df = df[df["split"] == split_id].reset_index(drop=True)

        self.mask_dir = os.path.join(root, "segmentation_masks")

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        row = self.df.iloc[idx]
        img_filename = row["img_filename"]
        img_path = os.path.join(self.root, img_filename)

        img = Image.open(img_path).convert("RGB")

        # Resolve mask path
        base = os.path.splitext(os.path.basename(img_filename))[0]
        mask_path = os.path.join(self.mask_dir, base + ".png")
        if not os.path.exists(mask_path):
            # Try with full subpath
            mask_path = os.path.join(self.mask_dir, img_filename.replace(".jpg", ".png").replace(".jpeg", ".png"))
        if not os.path.exists(mask_path):
            mask_path = ""

        if self.transform is not None:
            img = self.transform(img)

        return {
            "image": img,
            "core_label": int(row["y"]),
            "spurious_label": int(row["place"]),
            "mask_path": mask_path,
            "img_path": img_path,
        }


def extract_waterbirds_patches(
    root: str,
    extractor: PatchExtractor,
    split: str = "train",
    use_masks: bool = True,
) -> Dict[str, np.ndarray]:
    dataset = WaterbirdsDataset(root, split=split, transform=None)

    spurious_list, core_list = [], []
    spurious_labels, core_labels = [], []
    fallback_count = 0
    mask_success_count = 0

    for item in dataset:
        img = item["image"]
        if not isinstance(img, np.ndarray):
            img = np.array(img)

        mask_path = item["mask_path"]
        used_mask = False

        if use_masks and mask_path:
            try:
                mask_img = Image.open(mask_path).convert("L")
                mask = np.array(mask_img)
                mask_bool = mask > 127
                fg_frac = mask_bool.sum() / mask_bool.size
                if 0.01 < fg_frac < 0.99:
                    sp_patch, co_patch = extractor.extract_from_mask(img, mask_bool.astype(np.uint8) * 255)
                    used_mask = True
                    mask_success_count += 1
            except Exception:
                pass

        if not used_mask:
            sp_patch, co_patch = extractor.extract_quadrant(img)
            fallback_count += 1

        spurious_list.append(sp_patch)
        core_list.append(co_patch)
        spurious_labels.append(item["spurious_label"])
        core_labels.append(item["core_label"])

    N = len(spurious_list)
    print(f"Waterbirds: {N} patches extracted, {mask_success_count} mask-based, {fallback_count} quadrant fallbacks")

    if N < 100:
        raise ValueError(f"Extracted only {N} patches, need >= 100")

    return {
        "spurious_patches": np.stack(spurious_list, axis=0),
        "core_patches": np.stack(core_list, axis=0),
        "spurious_labels": np.array(spurious_labels, dtype=np.int64),
        "core_labels": np.array(core_labels, dtype=np.int64),
    }


def get_waterbirds_feature_loader(
    root: str,
    split: str = "train",
    batch_size: int = 256,
    num_workers: int = 4,
) -> DataLoader:
    transform = T.Compose([
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    dataset = WaterbirdsDataset(root, split=split, transform=transform)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )
