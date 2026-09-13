import os
import pandas as pd
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset
import wilds


def build_mask_index(waterbirds_metadata_csv: str, cub_segmentations_dir: str) -> dict:
    """Maps Waterbirds dataset row index -> CUB segmentation mask file path."""
    df = pd.read_csv(waterbirds_metadata_csv)
    index = {}
    missing = []
    for wilds_idx, row in df.iterrows():
        img_filename = row["img_filename"]
        mask_rel = img_filename.replace(".jpg", ".png")
        mask_abs = os.path.join(cub_segmentations_dir, mask_rel)
        if not os.path.exists(mask_abs):
            missing.append(mask_abs)
        else:
            index[wilds_idx] = mask_abs
    if missing:
        raise FileNotFoundError(
            f"CUB masks missing ({len(missing)} files). First missing: {missing[0]}\n"
            "Download CUB-200-2011 segmentations from http://www.vision.caltech.edu/datasets/cub_200_2011/"
        )
    return index


def load_cub_mask(mask_path: str, target_size: tuple) -> Image.Image:
    """Load and resize CUB segmentation mask. Returns L-mode image (0=bg, 255=bird)."""
    mask = Image.open(mask_path).convert("L")
    if target_size is not None:
        mask = mask.resize(target_size, Image.NEAREST)
    return mask


class WaterbirdsDataset(Dataset):
    """Wrapper around WILDS WaterbirdsDataset that returns (image, bird_label, bg_label, group_id)."""

    def __init__(self, root: str, split: str, transform=None, build_masks: bool = False,
                 cub_segmentations_dir: str = None):
        self.transform = transform
        wilds_dataset = wilds.get_dataset("waterbirds", root_dir=root, download=False)
        self.wilds_subset = wilds_dataset.get_subset(split)
        self.split = split
        self.mask_index = None
        if build_masks and cub_segmentations_dir:
            metadata_csv = os.path.join(root, "waterbirds_v1.0", "metadata.csv")
            self.mask_index = build_mask_index(metadata_csv, cub_segmentations_dir)

    def __len__(self) -> int:
        return len(self.wilds_subset)

    def __getitem__(self, idx: int):
        item = self.wilds_subset[idx]
        image = item[0]
        # WILDS returns tensor for x in some versions; convert to PIL if needed
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image.numpy().astype(np.uint8))
        bird_label = int(item[1])
        metadata = item[2]
        background_label = int(metadata[0])
        group_id = bird_label * 2 + background_label

        if self.transform is not None:
            image = self.transform(image)
        return image, bird_label, background_label, group_id
