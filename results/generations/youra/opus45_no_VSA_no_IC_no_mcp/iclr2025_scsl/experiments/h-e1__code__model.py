import torch
import torch.nn as nn
import torchvision.models as models
import numpy as np
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget


def build_resnet50(num_classes: int = 2) -> nn.Module:
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(2048, num_classes)
    return model


class AttributionTracker:
    def __init__(self, model: nn.Module, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.cam = None
        self.epoch_ratios = []

    def _ensure_cam(self):
        if self.cam is None:
            self.cam = GradCAM(model=self.model, target_layers=[self.target_layer])

    def compute_attribution_ratio(self, dataloader, device) -> float:
        self._ensure_cam()
        self.model.eval()
        ratios = []

        for batch in dataloader:
            images, labels, spurious_masks, core_masks = batch
            images = images.to(device)

            grayscale_cams = self.cam(input_tensor=images, targets=None)

            spurious_masks_np = spurious_masks.numpy()
            core_masks_np = core_masks.numpy()

            for i in range(len(images)):
                cam = grayscale_cams[i]
                spurious_attr = (cam * spurious_masks_np[i]).sum()
                core_attr = (cam * core_masks_np[i]).sum() + 1e-8
                ratio = spurious_attr / core_attr
                ratios.append(ratio)

        return float(np.mean(ratios))

    def log_epoch(self, epoch: int, dataloader, device) -> float:
        ratio = self.compute_attribution_ratio(dataloader, device)
        self.epoch_ratios.append((epoch, ratio))
        print(f"Epoch {epoch}: Spurious/Core ratio = {ratio:.4f}")
        return ratio
