import numpy as np
import torch
from PIL import Image
from src.data.places365_pool import Places365Pool


class BackgroundReplacementTransform:
    """
    Replaces background pixels with random Places365 images.
    Each call samples two independent backgrounds for view1 and view2.
    """

    def __init__(self, places_pool: Places365Pool, simclr_transform):
        self.places_pool = places_pool
        self.simclr_transform = simclr_transform

    def __call__(self, image: Image.Image, seg_mask: Image.Image):
        """
        Args:
            image: PIL RGB image (H, W, 3)
            seg_mask: PIL L-mode mask (H, W), values ~255=bird, ~0=background
        Returns:
            (view1, view2): each (3, 224, 224) normalized tensors
        """
        # Align mask to image size
        if seg_mask.size != image.size:
            seg_mask = seg_mask.resize(image.size, Image.NEAREST)

        img_arr = np.array(image)                      # (H, W, 3) uint8
        mask_bool = np.array(seg_mask) > 127           # (H, W) bool; True=bird

        # Each view gets an independent background
        bg1 = np.array(self.places_pool.sample().resize(image.size, Image.BILINEAR))
        bg2 = np.array(self.places_pool.sample().resize(image.size, Image.BILINEAR))

        replaced1 = np.where(mask_bool[:, :, None], img_arr, bg1).astype(np.uint8)
        replaced2 = np.where(mask_bool[:, :, None], img_arr, bg2).astype(np.uint8)

        view1 = self.simclr_transform(Image.fromarray(replaced1))
        view2 = self.simclr_transform(Image.fromarray(replaced2))
        return view1, view2


def verify_mechanism_activated(
    augmented_view: torch.Tensor,
    original_image: torch.Tensor,
    seg_mask: torch.Tensor,
    threshold: float = 0.05,
) -> dict:
    """
    Verifies background pixels changed after replacement.
    augmented_view, original_image: (3, H, W) tensors (same normalization)
    seg_mask: (H, W) bool tensor, True=bird foreground
    """
    bg_mask = ~seg_mask                                   # (H, W) True=background
    bg_pixels_view = augmented_view[:, bg_mask]           # (3, N_bg)
    bg_pixels_orig = original_image[:, bg_mask]           # (3, N_bg)

    pixel_diff = (bg_pixels_view - bg_pixels_orig).abs().mean().item()

    result = {
        "background_changed": pixel_diff > threshold,
        "pixel_diff": pixel_diff,
        "mechanism_active": pixel_diff > threshold,
    }
    assert result["mechanism_active"], (
        f"FAIL: Background replacement not active — pixel_diff={pixel_diff:.4f} "
        f"(threshold={threshold}). Check CUB mask loading and Places365 pool."
    )
    return result
