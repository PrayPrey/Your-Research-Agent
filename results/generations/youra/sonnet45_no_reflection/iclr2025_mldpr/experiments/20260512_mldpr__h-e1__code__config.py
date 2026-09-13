from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ExperimentConfig:
    # Data settings
    data_root: str = "./data"
    output_dir: str = "./output"

    # Device settings
    device: str = "cuda"
    batch_size: int = 256

    # Drift detection settings
    n_pca_components: int = 2
    mmd_permutations: int = 1000

    # Cold-start thresholds (from hypothesis)
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        'MAJOR': 0.07,
        'MINOR': 0.02,
        'PATCH': 0.005
    })

    # Reproducibility
    seed: int = 42

    # Feature extraction
    vision_model: str = "resnet50"
    nlp_model: str = "bert-base-uncased"
    max_seq_length: int = 512

    # Visualization
    figures_dir: str = "./figures"
    dpi: int = 300

    # Evaluation targets
    target_precision: float = 0.70
    target_recall: float = 0.85
    target_accuracy: float = 0.85


def get_default_config() -> ExperimentConfig:
    return ExperimentConfig()
