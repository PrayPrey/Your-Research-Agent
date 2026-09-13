"""H-M4 fixed experiment constants."""
from dataclasses import dataclass, field

CATEGORIES = ['execution', 'static', 'type', 'smt']
MAX_ITERS = 3
SMT_TIMEOUT = 30.0
EXEC_TIMEOUT = 10.0
GENERATION_TEMP = 0.2
REPAIR_TEMP = 0.0
MAX_TOKENS = 1024
N_BOOTSTRAP = 10000
SEED = 1

import pathlib as _pl
_HM4_DIR = _pl.Path(__file__).parent.parent  # h-m4/
FIGURES_DIR = str(_HM4_DIR / "figures")
RESULTS_PATH = str(_HM4_DIR / "results.json")
SUMMARY_PATH = str(_HM4_DIR / "summary.json")
CHECKPOINT_PATH = str(_HM4_DIR / "checkpoint.json")


@dataclass
class DatasetConfig:
    humaneval_hf_id: str = "openai/openai_humaneval"
    humaneval_split: str = "test"
    humaneval_n: int = 164
    mbpp_hf_id: str = "google-research-datasets/mbpp"
    mbpp_config: str = "sanitized"
    mbpp_split: str = "test"
    mbpp_n: int = 374
    total_problems: int = 538
    baseline_pass_path: str | None = None


@dataclass
class PyrightConfig:
    command: list = field(default_factory=lambda: ["pyright", "--outputjson"])
    tmpfile_prefix: str = "h_m4_pyright_"
    per_file_timeout: float = 30.0


CATEGORY_COLORS = {
    "execution": "#0072B2",
    "static":    "#E69F00",
    "type":      "#009E73",
    "smt":       "#D55E00",
}


@dataclass
class FigureConfig:
    output_dir: str = "docs/youra_research/h-m4/figures"
    dpi: int = 300
    fig_size_bar: tuple = (8.0, 5.0)
    fig_size_boxplot: tuple = (10.0, 6.0)
    fig_size_violin: tuple = (10.0, 6.0)
    fig_size_scatter: tuple = (7.0, 7.0)
    fig_size_heatmap: tuple = (14.0, 8.0)
    color_palette: dict = field(default_factory=lambda: CATEGORY_COLORS)
    font_size_title: int = 14
    font_size_label: int = 12
    font_size_tick: int = 10


@dataclass
class LogScaleConfig:
    log_transform_threshold: float = 1e-3
    log_base: int = 10
    tick_positions: list = field(default_factory=lambda: [1e-3, 1e-2, 1e-1, 1.0, 10.0, 30.0])
    tick_labels: list = field(default_factory=lambda: ["1ms", "10ms", "100ms", "1s", "10s", "30s"])
    heatmap_vmin: float = 1e-3
    heatmap_vmax: float = 30.0
