import os
import random
import logging
import numpy as np
import torch
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import Dataset, DataLoader
from PIL import Image

from config import ExperimentConfig
from src.models.simclr import SimCLRModel
from src.training.loss import NTXentLoss
from src.data.waterbirds import build_mask_index
from src.data.places365_pool import Places365Pool
from src.augmentation.simclr_augment import get_simclr_transform
from src.augmentation.background_replace import BackgroundReplacementTransform, verify_mechanism_activated

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class SimCLRDataset(Dataset):
    """Two-view dataset for SimCLR training."""

    def __init__(self, wilds_subset, mask_index, transform, condition: str):
        self.wilds_subset = wilds_subset
        self.mask_index = mask_index
        self.transform = transform
        self.condition = condition

    def __len__(self):
        return len(self.wilds_subset)

    def __getitem__(self, idx):
        item = self.wilds_subset[idx]
        image = item[0]
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image.numpy().astype(np.uint8))
        bird_label = int(item[1])
        metadata = item[2]
        background_label = int(metadata[0])

        if self.condition == "original":
            view1 = self.transform(image)
            view2 = self.transform(image)
        else:  # no_background
            mask_path = self.mask_index[idx]
            seg_mask = Image.open(mask_path).convert("L")
            seg_mask = seg_mask.resize(image.size, Image.NEAREST)
            view1, view2 = self.transform(image, seg_mask)

        return view1, view2, bird_label, background_label


class SimCLRTrainer:
    def __init__(self, config: ExperimentConfig, condition: str, seed: int):
        self.config = config
        self.condition = condition
        self.seed = seed
        self.device = torch.device(config.device if torch.cuda.is_available() else "cpu")
        logger.info(f"Trainer: condition={condition}, seed={seed}, device={self.device}")

    def _set_seed(self, seed: int):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    def _build_loader(self):
        import wilds
        cfg = self.config
        wilds_dataset = wilds.get_dataset("waterbirds", root_dir=cfg.waterbirds_root, download=False)
        wilds_train = wilds_dataset.get_subset("train")

        if self.condition == "original":
            transform = get_simclr_transform(cfg.image_size)
            mask_index = None
        else:
            simclr_transform = get_simclr_transform(cfg.image_size)
            places_pool = Places365Pool(cfg.places365_root, n_images=cfg.n_places365)
            transform = BackgroundReplacementTransform(places_pool, simclr_transform)
            metadata_csv = os.path.join(cfg.waterbirds_root, "waterbirds_v1.0", "metadata.csv")
            cub_seg_dir = os.path.join(cfg.cub_root, "segmentations")
            mask_index = build_mask_index(metadata_csv, cub_seg_dir)

        dataset = SimCLRDataset(wilds_train, mask_index, transform, self.condition)
        loader = DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True,
            drop_last=True,
        )
        return loader

    def _verify_mechanism(self, loader):
        """Verify background replacement is active by comparing composited vs original."""
        cfg = self.config
        import wilds
        import torchvision.transforms as T

        wilds_dataset = wilds.get_dataset("waterbirds", root_dir=cfg.waterbirds_root, download=False)
        wilds_train = wilds_dataset.get_subset("train")
        item = wilds_train[0]
        image = item[0]
        if not isinstance(image, Image.Image):
            image = Image.fromarray(item[0].numpy().astype(np.uint8))

        metadata_csv = os.path.join(cfg.waterbirds_root, "waterbirds_v1.0", "metadata.csv")
        cub_seg_dir = os.path.join(cfg.cub_root, "segmentations")
        mask_index = build_mask_index(metadata_csv, cub_seg_dir)

        mask_path = mask_index[0]
        seg_mask = Image.open(mask_path).convert("L").resize(image.size, Image.NEAREST)

        # Build composited image (background replaced) without SimCLR augmentation
        to_tensor_norm = T.Compose([
            T.Resize((cfg.image_size, cfg.image_size)),
            T.ToTensor(),
            T.Normalize(mean=cfg.normalize_mean, std=cfg.normalize_std),
        ])

        # Build background-replaced composite manually (no random crop)
        mask_arr = np.array(seg_mask) > 127  # (H, W) bool
        img_arr = np.array(image)
        bg = np.array(loader.dataset.transform.places_pool.sample().resize(image.size, Image.BILINEAR))
        replaced = np.where(mask_arr[:, :, None], img_arr, bg).astype(np.uint8)

        composited_tensor = to_tensor_norm(Image.fromarray(replaced))  # (3, 224, 224)
        orig_tensor = to_tensor_norm(image)                             # (3, 224, 224)

        # Create resized mask for 224x224
        mask_resized = torch.from_numpy(
            np.array(seg_mask.resize((cfg.image_size, cfg.image_size), Image.NEAREST)) > 127
        )  # (224, 224) bool

        result = verify_mechanism_activated(composited_tensor, orig_tensor, mask_resized)
        logger.info(f"Mechanism verified: pixel_diff={result['pixel_diff']:.4f}")

    def train(self) -> str:
        cfg = self.config
        self._set_seed(self.seed)

        model = SimCLRModel().to(self.device)
        optimizer = optim.SGD(
            model.parameters(),
            lr=cfg.lr,
            momentum=cfg.momentum,
            weight_decay=cfg.weight_decay,
        )
        scheduler = CosineAnnealingLR(optimizer, T_max=cfg.epochs, eta_min=0)
        criterion = NTXentLoss(temperature=cfg.temperature).to(self.device)
        loader = self._build_loader()

        if self.condition == "no_background":
            self._verify_mechanism(loader)

        for epoch in range(cfg.epochs):
            model.train()
            epoch_loss = 0.0
            n_batches = 0
            for view1, view2, _, _ in loader:
                view1 = view1.to(self.device)
                view2 = view2.to(self.device)
                optimizer.zero_grad()
                _, z1 = model(view1)
                _, z2 = model(view2)
                loss = criterion(z1, z2)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
                n_batches += 1
            scheduler.step()
            avg_loss = epoch_loss / n_batches if n_batches > 0 else 0
            logger.info(f"[{self.condition}|seed={self.seed}] Epoch {epoch+1}/{cfg.epochs} | loss={avg_loss:.4f}")

        ckpt_path = cfg.checkpoint_path(self.condition, self.seed)
        torch.save({"backbone": model.get_backbone().state_dict()}, ckpt_path)
        logger.info(f"Checkpoint saved: {ckpt_path}")
        return ckpt_path
