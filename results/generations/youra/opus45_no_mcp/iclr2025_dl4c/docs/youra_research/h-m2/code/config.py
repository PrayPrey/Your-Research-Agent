"""Configuration for H-M2 error localization analysis."""
from dataclasses import dataclass, field

SEED = 42

U_LINE_ERRORS = {'SyntaxError', 'IndentationError', 'NameError', 'TypeError',
                  'AttributeError', 'ZeroDivisionError', 'IndexError',
                  'KeyError', 'ValueError'}
U_IGNORE_ERRORS = {'AssertionError', 'RuntimeError', 'TimeoutError',
                    'RecursionError', 'MemoryError'}

TOLERANCE_LINES = 2


@dataclass
class AnalysisConfig:
    n_samples: int = 500
    min_per_category: int = 250
    tolerance_lines: int = TOLERANCE_LINES
    confidence_level: float = 0.95
    significance_threshold: float = 0.05
    spot_check_n: int = 50
    seed: int = SEED


@dataclass
class SamplesConfig:
    reuse_h_m1: bool = True
    h_m1_results_dir: str = "../h-m1/results"


@dataclass
class VizConfig:
    style: str = "seaborn-v0_8-whitegrid"
    dpi: int = 150
    accuracy_bar_path: str = "figures/accuracy_bar.png"
    distance_dist_path: str = "figures/distance_distribution.png"
    exception_breakdown_path: str = "figures/exception_breakdown.png"


@dataclass
class H_M2_Config:
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    samples: SamplesConfig = field(default_factory=SamplesConfig)
    viz: VizConfig = field(default_factory=VizConfig)
    output_dir: str = "results"
    figures_dir: str = "figures"


def get_config():
    return H_M2_Config()
