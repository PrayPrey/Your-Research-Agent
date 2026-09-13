"""Configuration for H-M2 DiD experiment."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    # Model
    model_id: str = "Salesforce/codet5p-220m"

    # Paths to H-E1 checkpoints (PEFT adapters)
    h_e1_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "h-e1")

    # Inference (greedy, K=1 refinement)
    refine_k: int = 1
    max_new_tokens: int = 512
    temperature: float = 0.0

    # DiD conditions
    conditions: tuple = ("actual", "control")
    model_names: tuple = ("RL", "CE")

    # Reproducibility
    seeds: tuple = (42, 43, 44)

    # Statistics
    n_bootstrap: int = 1000
    alpha: float = 0.05

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    @property
    def cache_dir(self) -> Path:
        return self.h_e1_dir / "data_cache"

    @property
    def rl_checkpoint(self) -> Path:
        return self.h_e1_dir / "checkpoints" / "rl_final"

    @property
    def ce_checkpoint(self) -> Path:
        return self.h_e1_dir / "checkpoints" / "ce_final"

    @property
    def figures_dir(self) -> Path:
        return self.base_dir / "figures"

    @property
    def outputs_dir(self) -> Path:
        return self.base_dir / "code" / "outputs"

    def __post_init__(self):
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
