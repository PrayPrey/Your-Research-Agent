"""Configuration for H-M1 experiment."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MINEConfig:
    # H-E1 model artifacts (LoRA adapters)
    ce_adapter_path: str = "h-e1/checkpoints/ce_final"
    rl_adapter_path: str = "h-e1/checkpoints/rl_final"
    tokenizer_id: str = "Salesforce/codet5p-220m"

    # Embedding / MINE architecture
    embed_dim: int = 256
    hidden_dim: int = 512

    # Refinement trace extraction
    refine_k: int = 2  # ponytail: reduced test, set to 3 for full run
    seeds: list = field(default_factory=lambda: [42])  # ponytail: single seed for reduced test
    max_new_tokens: int = 512

    # MINE training
    mine_lr: float = 0.001
    mine_batch_size: int = 32
    mine_iters: int = 500  # ponytail: reduced test, set to 5000 for full run
    ema_weight: float = 0.01

    # Statistical testing
    n_permutations: int = 500  # ponytail: reduced test, set to 10000 for full run

    # Subset for faster CPU testing
    max_problems: int = 20  # ponytail: reduced test, set to 164 for full run

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)

    @property
    def h_e1_dir(self) -> Path:
        return self.base_dir / "h-e1"

    @property
    def cache_dir(self) -> Path:
        return self.h_e1_dir / "data_cache"

    @property
    def ce_path(self) -> Path:
        return self.base_dir / self.ce_adapter_path

    @property
    def rl_path(self) -> Path:
        return self.base_dir / self.rl_adapter_path

    @property
    def output_dir(self) -> Path:
        return self.base_dir / "h-m1"

    @property
    def figures_dir(self) -> Path:
        return self.output_dir / "figures"

    def __post_init__(self):
        self.figures_dir.mkdir(parents=True, exist_ok=True)
