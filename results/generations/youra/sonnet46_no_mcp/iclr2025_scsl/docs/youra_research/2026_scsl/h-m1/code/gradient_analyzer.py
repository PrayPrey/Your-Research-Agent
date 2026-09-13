import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Tuple, Dict, List


class GradientAlignmentAnalyzer:
    def __init__(self, model: nn.Module, device: str) -> None:
        self.model = model
        self.device = device
        self._spurious_norms: List[float] = []
        self._core_norms: List[float] = []
        self._gdr_series: List[float] = []

    def extract_features(
        self,
        loader: DataLoader,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Frozen backbone forward pass. Returns (features [N,2048], core_labels [N,], spurious_labels [N,])."""
        self.model.eval()
        features_list, core_list, spurious_list = [], [], []

        # Register hook on avgpool to capture 2048-dim features
        activations = {}

        def hook_fn(module, input, output):
            activations["avgpool"] = output

        hook = self.model.avgpool.register_forward_hook(hook_fn)

        with torch.no_grad():
            for batch in loader:
                x = batch["image"].to(self.device)
                self.model(x)  # triggers hook
                feat = activations["avgpool"].flatten(1).cpu()  # [B, 2048]
                features_list.append(feat)
                core_list.append(batch["core_label"])
                spurious_list.append(batch["spurious_label"])

        hook.remove()

        features = torch.cat(features_list, dim=0)      # [N, 2048]
        core_labels = torch.cat(core_list, dim=0)        # [N,]
        spurious_labels = torch.cat(spurious_list, dim=0)  # [N,]

        return features, core_labels, spurious_labels

    def compute_label_gradient_norm(
        self,
        features: torch.Tensor,
        label_tensor: torch.Tensor,
        criterion: nn.Module,
    ) -> float:
        """Single fc-only backward pass. Returns L2 grad norm of fc.weight."""
        features_detached = features.detach().to(self.device)
        label_tensor = label_tensor.to(self.device)

        self.model.fc.zero_grad()
        logits = self.model.fc(features_detached)  # [N, 2]
        loss = criterion(logits, label_tensor)
        loss.backward()
        grad_norm = self.model.fc.weight.grad.norm(p=2).item()
        self.model.fc.zero_grad()  # cleanup
        return grad_norm

    def log_epoch_gradients(
        self,
        loader: DataLoader,
        criterion: nn.Module,
    ) -> Dict[str, float]:
        """Extract features, compute GDR, append to history."""
        features, core_labels, spurious_labels = self.extract_features(loader)

        spurious_norm = self.compute_label_gradient_norm(features, spurious_labels, criterion)
        core_norm = self.compute_label_gradient_norm(features, core_labels, criterion)
        gdr = spurious_norm / (core_norm + 1e-8)

        self._spurious_norms.append(spurious_norm)
        self._core_norms.append(core_norm)
        self._gdr_series.append(gdr)

        return {
            "spurious_grad_norm": spurious_norm,
            "core_grad_norm": core_norm,
            "gdr": gdr,
        }

    def get_history(self) -> Dict[str, List[float]]:
        """Returns accumulated history. Keys: spurious_grad_norms, core_grad_norms, gdr_series."""
        return {
            "spurious_grad_norms": list(self._spurious_norms),
            "core_grad_norms": list(self._core_norms),
            "gdr_series": list(self._gdr_series),
        }
