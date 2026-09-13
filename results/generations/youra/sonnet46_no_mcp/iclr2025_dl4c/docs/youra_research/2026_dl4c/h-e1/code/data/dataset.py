"""Dataset classes for 4-condition GRPO training experiment."""

import torch
from torch.utils.data import Dataset
import datasets as hf_datasets


class CurriculumDataset(Dataset):
    """Phase 0-2499: easy_data; phase 2500+: hard_data."""

    def __init__(
        self,
        easy_data: hf_datasets.Dataset,
        hard_data: hf_datasets.Dataset,
        curriculum_step: int = 2500,
    ) -> None:
        self.easy_data = easy_data
        self.hard_data = hard_data
        self.curriculum_step = curriculum_step
        self.active_data = easy_data

    def set_step(self, step: int) -> None:
        """Switch active_data when step >= curriculum_step."""
        if step >= self.curriculum_step and self.active_data is self.easy_data:
            self.active_data = self.hard_data
            print(f"Curriculum phase: switching to hard_data at step {step}")

    def __len__(self) -> int:
        return len(self.active_data)

    def __getitem__(self, idx: int) -> dict:
        """Returns tokenized example dict from active_data."""
        return self.active_data[idx % len(self.active_data)]


class UniformDataset(Dataset):
    """Full pool with uniform random sampling."""

    def __init__(self, full_data: hf_datasets.Dataset) -> None:
        self.full_data = full_data

    def __len__(self) -> int:
        return len(self.full_data)

    def __getitem__(self, idx: int) -> dict:
        return self.full_data[idx % len(self.full_data)]


class EasyOnlyDataset(Dataset):
    """Only easy pool throughout training."""

    def __init__(self, easy_data: hf_datasets.Dataset) -> None:
        self.easy_data = easy_data

    def __len__(self) -> int:
        return len(self.easy_data)

    def __getitem__(self, idx: int) -> dict:
        return self.easy_data[idx % len(self.easy_data)]


class HardOnlyDataset(Dataset):
    """Only hard pool throughout training."""

    def __init__(self, hard_data: hf_datasets.Dataset) -> None:
        self.hard_data = hard_data

    def __len__(self) -> int:
        return len(self.hard_data)

    def __getitem__(self, idx: int) -> dict:
        return self.hard_data[idx % len(self.hard_data)]


def get_dataset(
    condition: str,
    easy_data: hf_datasets.Dataset,
    hard_data: hf_datasets.Dataset,
    full_data: hf_datasets.Dataset,
    curriculum_step: int = 2500,
) -> Dataset:
    """Factory: condition in {'curriculum','uniform','easy_only','hard_only'}."""
    if condition == "curriculum":
        return CurriculumDataset(easy_data, hard_data, curriculum_step)
    elif condition == "uniform":
        return UniformDataset(full_data)
    elif condition == "easy_only":
        return EasyOnlyDataset(easy_data)
    elif condition == "hard_only":
        return HardOnlyDataset(hard_data)
    else:
        raise ValueError(f"Unknown condition: {condition}. Must be one of {['curriculum','uniform','easy_only','hard_only']}")
