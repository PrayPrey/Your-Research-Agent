import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Tuple
import torchvision.models as models


class ResNetExtractor:
    def __init__(self, device: str = "cuda:0"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model = self.build_model()

    def build_model(self) -> nn.Module:
        model = models.resnet50(pretrained=True)
        model.fc = nn.Identity()
        for param in model.parameters():
            param.requires_grad = False
        model.eval()
        model = model.to(self.device)
        return model

    def extract_features(
        self,
        loader: DataLoader,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        all_feats, all_core, all_spurious = [], [], []

        with torch.no_grad():
            for batch in loader:
                if isinstance(batch, dict):
                    images = batch["image"].to(self.device)
                    core_labels = batch.get("core_label", torch.zeros(images.size(0)))
                    spurious_labels = batch.get("spurious_label", torch.zeros(images.size(0)))
                else:
                    images = batch[0].to(self.device)
                    core_labels = batch[1] if len(batch) > 1 else torch.zeros(images.size(0))
                    spurious_labels = torch.zeros(images.size(0))

                feats = self.model(images)
                all_feats.append(feats.cpu().numpy())
                if isinstance(core_labels, torch.Tensor):
                    all_core.append(core_labels.numpy())
                    all_spurious.append(spurious_labels.numpy() if isinstance(spurious_labels, torch.Tensor) else np.zeros(feats.shape[0]))
                else:
                    all_core.append(np.array(core_labels))
                    all_spurious.append(np.zeros(feats.shape[0]))

        features = np.concatenate(all_feats, axis=0)
        core_labels_out = np.concatenate(all_core, axis=0)
        spurious_labels_out = np.concatenate(all_spurious, axis=0)

        assert features.shape[1] == 2048, f"Expected 2048-dim features, got {features.shape[1]}"
        return features, core_labels_out, spurious_labels_out

    def extract_patch_features(self, patches: np.ndarray, batch_size: int = 256) -> np.ndarray:
        """Extract features from raw uint8 patches [N, 64, 64, 3]."""
        import torchvision.transforms as T
        transform = T.Compose([
            T.Resize(256),
            T.CenterCrop(224),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        from PIL import Image
        all_feats = []
        with torch.no_grad():
            for i in range(0, len(patches), batch_size):
                batch = patches[i:i + batch_size]
                tensors = torch.stack([transform(Image.fromarray(p)) for p in batch])
                tensors = tensors.to(self.device)
                feats = self.model(tensors)
                all_feats.append(feats.cpu().numpy())
        return np.concatenate(all_feats, axis=0)

    def extract_split_features(
        self,
        spurious_patches: np.ndarray,
        core_patches: np.ndarray,
        batch_size: int = 256,
    ) -> Tuple[np.ndarray, np.ndarray]:
        spurious_feats = self.extract_patch_features(spurious_patches, batch_size)
        core_feats = self.extract_patch_features(core_patches, batch_size)
        return spurious_feats, core_feats
