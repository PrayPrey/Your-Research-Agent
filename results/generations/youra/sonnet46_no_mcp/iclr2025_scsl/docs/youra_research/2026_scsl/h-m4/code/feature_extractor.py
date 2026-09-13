import numpy as np
import torch
import torch.nn as nn
from typing import Tuple
from torchvision import models

from config import ExperimentConfig
from data.waterbirds import get_waterbirds_loader


class FeatureExtractor:
    def __init__(self, device: str):
        self.device = device

    def load_backbone(self, checkpoint_path: str) -> nn.Module:
        # Build model with 2-class fc to match checkpoint shape, load state_dict, then replace fc
        model = models.resnet50(pretrained=False)
        model.fc = nn.Linear(2048, 2)
        state_dict = torch.load(checkpoint_path, map_location=self.device, weights_only=True)
        model.load_state_dict(state_dict)
        # Replace fc with Identity AFTER loading to get 2048-dim features
        model.fc = nn.Identity()
        model.eval()
        for param in model.parameters():
            param.requires_grad = False
        model = model.to(self.device)
        return model

    def extract(
        self,
        backbone: nn.Module,
        loader,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        all_feats = []
        all_labels = []
        all_groups = []

        with torch.no_grad():
            for batch in loader:
                imgs = batch["image"].to(self.device)
                feats = backbone(imgs).cpu().numpy()  # [B, 2048]
                all_feats.append(feats)
                all_labels.append(batch["core_label"].numpy())
                all_groups.append(batch["group_id"].numpy())

        features = np.concatenate(all_feats, axis=0)   # [N, 2048]
        labels = np.concatenate(all_labels, axis=0)    # [N]
        group_ids = np.concatenate(all_groups, axis=0) # [N]

        assert features.shape[1] == 2048, f"Expected 2048-dim features, got {features.shape[1]}"
        return features, labels, group_ids

    def extract_split(
        self,
        root: str,
        split: str,
        cfg: ExperimentConfig,
        checkpoint_path: str,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        loader = get_waterbirds_loader(
            root=root,
            split=split,
            batch_size=cfg.train.batch_size,
            num_workers=cfg.train.num_workers,
            augment=False,
        )
        backbone = self.load_backbone(checkpoint_path)
        return self.extract(backbone, loader)
