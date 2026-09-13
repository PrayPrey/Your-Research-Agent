"""H-M5 Configuration: Modality Divergence (Phase Transition Effect)"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExperimentConfig:
    dataset_name: str = "pwc-archive/datasets"
    dataset_split: str = "train"
    date_start: str = "2018-01"
    date_end: str = "2024-12"
    pre_cutoff: str = "2020-01"
    post_cutoff: str = "2021-01"
    modality_keywords: dict = field(default_factory=lambda: {
        "CV": ["image", "vision", "object detection", "segmentation", "visual"],
        "NLP": ["text", "language", "nlp", "translation", "summarization", "question answering"],
        "Audio": ["audio", "speech", "sound", "voice"],
        "Tabular": ["tabular", "structured", "table"],
    })
    default_modality: str = "Other"
    rolling_window: int = 6
    gate_r_pre_min: float = 0.6
    gate_r_post_max: float = 0.4
    gate_p_value_max: float = 0.05
    baseline_r_min: float = 0.5
    min_n_pre: int = 24
    min_n_post: int = 36
    min_time_points: int = 72
    seed: int = 42
    output_dir: str = "figures"
    gate_metrics_path: str = "figures/gate_metrics.png"
    rolling_correlation_path: str = "figures/rolling_correlation.png"
    gini_trajectories_path: str = "figures/gini_trajectories.png"
    correlation_heatmap_path: str = "figures/correlation_heatmap.png"


CONFIG = ExperimentConfig()
