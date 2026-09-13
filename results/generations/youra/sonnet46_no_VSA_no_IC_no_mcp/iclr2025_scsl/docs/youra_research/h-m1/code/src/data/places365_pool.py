import os
import random
from PIL import Image


class Places365Pool:
    """Pre-loaded pool of Places365 images for background replacement sampling."""

    def __init__(self, root: str, n_images: int = 10000):
        val_dir = os.path.join(root, "val_256")
        if not os.path.isdir(val_dir):
            raise FileNotFoundError(f"Places365 val_256 not found at {val_dir}")

        all_files = sorted([
            os.path.join(val_dir, f)
            for f in os.listdir(val_dir)
            if f.endswith(".jpg") or f.endswith(".png")
        ])
        if len(all_files) == 0:
            raise FileNotFoundError(f"No images found in {val_dir}")

        # Sample n_images from available files
        n = min(n_images, len(all_files))
        random.shuffle(all_files)
        self.image_paths = all_files[:n]
        self._pool = []
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            print(f"Loading {len(self.image_paths)} Places365 images into pool...")
            for p in self.image_paths:
                try:
                    img = Image.open(p).convert("RGB")
                    self._pool.append(img.copy())
                except Exception:
                    pass
            self._loaded = True
            print(f"Places365 pool ready: {len(self._pool)} images")

    def sample(self) -> Image.Image:
        self._ensure_loaded()
        return random.choice(self._pool)
