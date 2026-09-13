"""Configuration for H-M1 gradient concentration analysis."""
from dataclasses import dataclass, field

SEED = 42
MODEL_NAME = "Salesforce/codet5-small"  # ponytail: small for PoC, codet5-large for full
MAX_INPUT_LEN = 512
MAX_OUTPUT_LEN = 256

U_LINE_ERRORS = {'SyntaxError', 'IndentationError', 'NameError',
                 'TypeError', 'AttributeError', 'KeyError', 'IndexError'}
U_IGNORE_ERRORS = {'RuntimeError', 'RecursionError', 'MemoryError',
                   'TimeoutError', 'AssertionError'}


@dataclass
class AnalysisConfig:
    n_samples: int = 500
    concentration_threshold: float = 1.0
    within_lines_threshold: float = 0.80
    within_lines_window: int = 2
    p_value_threshold: float = 0.05
    random_baseline_seed: int = 42


@dataclass
class GradientConfig:
    gradient_source: str = "embedding"
    normalize_by_line_length: bool = True
    eps: float = 1e-8


@dataclass
class H_M1_Config:
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    gradient: GradientConfig = field(default_factory=GradientConfig)
    output_dir: str = "h-m1/results"
    figures_dir: str = "h-m1/figures"


def get_config():
    return H_M1_Config()
