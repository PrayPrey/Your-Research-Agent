import numpy as np
from PIL import Image
from typing import Tuple
import torch
import torchvision.transforms as T


class PatchExtractor:
    def __init__(self, patch_size: int = 64):
        self.patch_size = patch_size
        self._imagenet_transform = T.Compose([
            T.Resize(256),
            T.CenterCrop(224),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def _resize(self, crop: np.ndarray) -> np.ndarray:
        pil = Image.fromarray(crop.astype(np.uint8))
        pil = pil.resize((self.patch_size, self.patch_size), Image.BILINEAR)
        return np.array(pil, dtype=np.uint8)

    def _bounding_box(self, binary: np.ndarray) -> Tuple[int, int, int, int]:
        rows = np.any(binary, axis=1)
        cols = np.any(binary, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        return int(rmin), int(rmax) + 1, int(cmin), int(cmax) + 1

    def extract_from_mask(
        self,
        image: np.ndarray,
        mask: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        H, W = image.shape[:2]
        mask_bool = mask.astype(bool)

        fg_frac = mask_bool.sum() / (H * W)
        if fg_frac < 0.01 or fg_frac > 0.99:
            return self.extract_quadrant(image)

        bg_bool = ~mask_bool
        if not bg_bool.any() or not mask_bool.any():
            return self.extract_quadrant(image)

        try:
            r0, r1, c0, c1 = self._bounding_box(bg_bool)
            if (r1 - r0) < 4 or (c1 - c0) < 4:
                raise ValueError("bg bbox too small")
            spurious_crop = image[r0:r1, c0:c1]

            r0, r1, c0, c1 = self._bounding_box(mask_bool)
            if (r1 - r0) < 4 or (c1 - c0) < 4:
                raise ValueError("fg bbox too small")
            core_crop = image[r0:r1, c0:c1]
        except (ValueError, IndexError):
            return self.extract_quadrant(image)

        return self._resize(spurious_crop), self._resize(core_crop)

    def extract_quadrant(
        self,
        image: np.ndarray,
        spurious_top_frac: float = 0.4,
    ) -> Tuple[np.ndarray, np.ndarray]:
        H, W = image.shape[:2]
        top_h = max(4, int(H * spurious_top_frac))
        spurious_crop = image[:top_h, :, :]

        center_size = min(H, W) // 2
        center_size = max(4, center_size)
        r_start = (H - center_size) // 2
        c_start = (W - center_size) // 2
        core_crop = image[r_start:r_start + center_size, c_start:c_start + center_size, :]

        return self._resize(spurious_crop), self._resize(core_crop)

    def extract_celeba_patches(
        self,
        image: np.ndarray,
        hair_top_frac: float = 0.25,
        face_crop_size: int = 112,
    ) -> Tuple[np.ndarray, np.ndarray]:
        H, W = image.shape[:2]
        top_h = max(4, int(H * hair_top_frac))
        spurious_crop = image[:top_h, :, :]

        r_start = max(0, (H - face_crop_size) // 2)
        c_start = max(0, (W - face_crop_size) // 2)
        r_end = min(H, r_start + face_crop_size)
        c_end = min(W, c_start + face_crop_size)
        core_crop = image[r_start:r_end, c_start:c_end, :]

        return self._resize(spurious_crop), self._resize(core_crop)

    def to_imagenet_tensor(self, patch_uint8: np.ndarray) -> torch.Tensor:
        pil = Image.fromarray(patch_uint8.astype(np.uint8))
        return self._imagenet_transform(pil)
