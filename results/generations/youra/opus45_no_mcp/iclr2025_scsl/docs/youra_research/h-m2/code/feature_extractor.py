import torch
from torch import nn, Tensor
from torch.utils.data import DataLoader

class FeatureExtractor:
    def __init__(self, model: nn.Module, layer_name: str = "avgpool"):
        self.features = None
        self._hook_handle = getattr(model, layer_name).register_forward_hook(self._hook)

    def _hook(self, module, input, output) -> None:
        self.features = output.view(output.size(0), -1).detach()

    def extract_batch(self, model: nn.Module, x: Tensor) -> Tensor:
        with torch.no_grad():
            _ = model(x)
        return self.features

    def extract_dataset(self, model: nn.Module, dataloader: DataLoader, device: str):
        model.eval()
        all_features, all_core, all_spurious = [], [], []
        with torch.no_grad():
            for x, y, metadata in dataloader:
                x = x.to(device)
                _ = model(x)
                all_features.append(self.features.cpu())
                all_core.append(y)
                # group_id % 2: 0,2->0 (land), 1,3->1 (water)
                spurious = (metadata[:, 0] % 2).long()
                all_spurious.append(spurious)
        return torch.cat(all_features), torch.cat(all_core), torch.cat(all_spurious)

    def remove(self) -> None:
        self._hook_handle.remove()
