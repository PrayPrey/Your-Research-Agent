from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import torch


def _check_torch_version() -> None:
    major, minor = (int(x) for x in torch.__version__.split(".")[:2])
    assert (major, minor) >= (2, 0), (
        f"torch>=2.0.0 required for torch.func.vmap; got {torch.__version__}"
    )


@dataclass
class DatasetConfig:
    name: str                                  # "waterbirds" | "celeba"
    root_dir: str
    target_name: str
    confounder_names: List[str]
    n_classes: int
    lr: float
    n_epochs: int
    batch_size: int = 32
    seed: int = 42
    checkpoint_epochs: tuple = (1, 5, 10, 25, 50)
    minority_group_ids: frozenset = field(default_factory=frozenset)
    max_train_samples: int = -1  # -1 = use full set; >0 = subsample (stratified by group)


WATERBIRDS_CONFIG = DatasetConfig(
    name="waterbirds",
    root_dir="./data/waterbirds",
    target_name="y",
    confounder_names=["place"],
    n_classes=2,
    lr=0.001,
    n_epochs=300,
    batch_size=32,
    seed=42,
    checkpoint_epochs=(1, 5, 10, 25, 50),
    minority_group_ids=frozenset({1, 2}),
)

CELEBA_CONFIG = DatasetConfig(
    name="celeba",
    root_dir="./data/celeba",
    target_name="Blond_Hair",
    confounder_names=["Male"],
    n_classes=2,
    lr=0.0001,
    n_epochs=50,
    batch_size=32,
    seed=42,
    checkpoint_epochs=(1, 5, 10, 25, 50),
    minority_group_ids=frozenset({3}),  # blond+male = group 3 (y=1, confounder=1 → 1*2+1=3)
    max_train_samples=16000,  # ponytail: 10% subsample; upgrade to full 162K if signal is noisy
)


_check_torch_version()
