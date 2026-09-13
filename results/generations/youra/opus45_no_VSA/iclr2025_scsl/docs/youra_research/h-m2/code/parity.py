import torch
import torch.nn as nn
from data import WaterbirdDataset, get_group_batch


class UpdateNormParityTrainer:
    def __init__(self, model: nn.Module, num_groups: int = 4, scale: float = 1.0):
        self.model = model
        self.num_groups = num_groups
        self.scale = scale

    def compute_group_grad_norms(
        self,
        dataset: WaterbirdDataset,
        group_ids: tuple,
        batch_size: int,
        criterion: nn.Module,
        device: torch.device
    ) -> dict:
        norms = {}
        for g in group_ids:
            x, y, _ = get_group_batch(dataset, g, batch_size, device)
            if x is None:
                continue
            self.model.zero_grad()
            loss = criterion(self.model(x.double()), y)
            loss.backward()
            flat = torch.cat([p.grad.reshape(-1) for p in self.model.parameters() if p.grad is not None])
            norms[g] = flat.norm().item()
        self.model.zero_grad()
        return norms

    def apply_parity_scaling(self, group_norms: dict, target_group: int) -> dict:
        if self.scale == 0.0 or len(group_norms) == 0:
            return {"group": target_group, "orig_norm": 0, "scaled_norm": 0, "target_norm": 0}

        mean_norm = sum(group_norms.values()) / len(group_norms)
        orig = group_norms.get(target_group, mean_norm)
        target_norm = orig + self.scale * (mean_norm - orig)
        factor = target_norm / (orig + 1e-12)

        for p in self.model.parameters():
            if p.grad is not None:
                p.grad.mul_(factor)

        return {"group": target_group, "orig_norm": orig, "scaled_norm": target_norm, "target_norm": mean_norm}
