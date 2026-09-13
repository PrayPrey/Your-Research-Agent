"""H-M3 Configuration: Second Derivative Crystallization Detection"""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DetectionConfig:
    # Only waterbirds has H-E1 checkpoints available
    benchmarks: list = field(default_factory=lambda: ["waterbirds"])
    n_seeds: int = 5
    epochs_by_benchmark: dict = field(default_factory=lambda: {
        "waterbirds": 100, "celeba": 50, "coloredmnist": 30
    })
    smoothing_windows: list = field(default_factory=lambda: [3, 5, 7])
    primary_window: int = 5
    prominence_threshold: float = 0.005
    window_robustness_tolerance_epochs: int = 3
    h_e1_checkpoint_dir: str = str(Path(__file__).parent.parent.parent / "h-e1/code/checkpoints")
    checkpoint_pattern: str = "waterbirds_epoch{epoch}.pt"
    detection_rate_target: float = 0.8
    variance_target_epochs: float = 5.0
    snr_target: float = 2.0
    window_robustness_target: float = 0.7
    cross_benchmark_correlation_target: float = 0.6
    synthesis_seed_base: int = 42
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"
    results_file: str = "detection_results.json"
    metrics_file: str = "aggregated_metrics.yaml"

    def get_checkpoint_path(self, epoch: int) -> str:
        return str(Path(self.h_e1_checkpoint_dir) / self.checkpoint_pattern.format(epoch=epoch))

    def get_n_epochs(self, benchmark: str) -> int:
        return self.epochs_by_benchmark[benchmark]


CONFIG = DetectionConfig()
