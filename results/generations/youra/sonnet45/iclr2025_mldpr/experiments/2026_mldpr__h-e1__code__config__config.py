"""
Configuration for H-E1 Experiment
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class DataCollectionConfig:
    """Data collection configuration"""
    n_huggingface: int = 150
    n_openml: int = 100
    n_uci: int = 50
    n_total_samples: int = 300
    random_seed: int = 42
    scaffold_ratio: float = 0.5  # 50% scaffolded samples


@dataclass
class AnnotationConfig:
    """Annotation protocol configuration"""
    dts_sections: List[str] = field(default_factory=lambda: [
        "Dataset_Description",
        "Task_Description",
        "Source_Attribution",
        "Data_Collection_Method",
        "Known_Limitations",
        "Ethical_Considerations"
    ])


@dataclass
class StatisticalConfig:
    """Statistical analysis configuration"""
    bootstrap_iterations: int = 1000
    confidence_level: float = 0.95
    random_seed: int = 42


@dataclass
class GateConfig:
    """Gate validation configuration"""
    gate_type: str = "MUST_WORK"
    kappa_threshold: float = 0.60
    probe_threshold: float = 0.75
    min_sections_pass: int = 5  # At least 5 of 6 sections must pass


@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    dpi: int = 300
    figure_format: str = "png"
    color_pass: str = "green"
    color_fail: str = "red"


@dataclass
class ExperimentConfig:
    """Main experiment configuration"""
    experiment_id: str = "h-e1"
    hypothesis_type: str = "EXISTENCE"

    # Sub-configurations
    data_collection: DataCollectionConfig = field(default_factory=DataCollectionConfig)
    annotation: AnnotationConfig = field(default_factory=AnnotationConfig)
    statistical: StatisticalConfig = field(default_factory=StatisticalConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)

    @property
    def n_total_samples(self) -> int:
        return self.data_collection.n_total_samples
