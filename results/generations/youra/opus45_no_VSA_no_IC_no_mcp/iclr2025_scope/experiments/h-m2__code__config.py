from dataclasses import dataclass, field
from typing import Literal


@dataclass
class TCSSMConfig:
    d_model: int = 1024
    d_state: int = 16
    d_conv: int = 4
    expand: int = 2
    task_emb_dim: int = 128
    rank: int = 32
    modulation_target: Literal["delta_only", "all_matrices"] = "all_matrices"


@dataclass
class ExperimentConfig:
    tasks: list[str] = field(default_factory=lambda: ["boolq", "rte", "wic"])
    samples_per_task: int = 500
    warmup_iters: int = 10
    measure_iters: int = 100
    seed: int = 42


@dataclass
class MeasurementConfig:
    device: str = "cuda"
    significance_level: float = 0.05
    overhead_threshold: float = 2.0


@dataclass
class AblationConfig:
    ranks: list[int] = field(default_factory=lambda: [16, 32, 64])
    modulation_targets: list[str] = field(
        default_factory=lambda: ["delta_only", "all_matrices"]
    )
