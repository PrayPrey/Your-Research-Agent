"""H-M4 Config: Benchmark-relative timing validation"""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BenchmarkConfig:
    name: str
    total_epochs: int
    lr: float
    num_classes: int
    image_size: int
    expected_range: tuple = (20.0, 40.0)


@dataclass
class TimingConfig:
    benchmarks: dict = field(default_factory=lambda: {
        "waterbirds": BenchmarkConfig("Waterbirds", 30, 1e-3, 2, 224),
        "coloredmnist": BenchmarkConfig("ColoredMNIST", 20, 1e-3, 10, 32),
    })
    seeds: list = field(default_factory=lambda: [0, 1, 2])
    batch_size: int = 128
    momentum: float = 0.9
    smoothing_window: int = 5
    prominence_threshold: float = 0.005
    expected_range: tuple = (20.0, 40.0)
    variance_target: float = 10.0
    detection_rate_target: float = 0.8
    data_root: str = str(Path(__file__).parent.parent.parent / "h-e1/code/data")
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"
    h_m3_code_dir: str = str(Path(__file__).parent.parent.parent / "h-m3/code")
    h_e1_checkpoint_dir: str = str(Path(__file__).parent.parent.parent / "h-e1/code/checkpoints")

    def get_n_epochs(self, benchmark: str) -> int:
        return self.benchmarks[benchmark].total_epochs


CONFIG = TimingConfig()
