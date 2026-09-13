"""H_M4_Config: RLEF-Fraction Monotonic Difficulty Scaling + 1.3B Scale Sanity Check."""
import sys
from dataclasses import dataclass, field
from pathlib import Path

_THIS = Path(__file__).resolve()
H_M4_ROOT = _THIS.parents[1]          # docs/youra_research/h-m4
RESEARCH_ROOT = _THIS.parents[2]      # docs/youra_research
H_E1_CODE = RESEARCH_ROOT / "h-e1" / "code"

if str(H_E1_CODE) not in sys.path:
    sys.path.insert(0, str(H_E1_CODE))


BENCHMARK_ORDER = ["humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"]
PROBLEM_COUNTS = {
    "humaneval": 164,
    "mbpp": 374,
    "lcb_easy": 250,
    "lcb_medium": 250,
    "lcb_hard": 150,
}
SFT_PASS_RATES = {
    "humaneval": 0.45,
    "mbpp": 0.40,
    "lcb_easy": 0.30,
    "lcb_medium": 0.18,
    "lcb_hard": 0.10,
}


@dataclass
class SFT1B3Config:
    model_name: str = "deepseek-ai/deepseek-coder-1.3b-base"
    lr: float = 2e-5
    batch_size: int = 8
    grad_accum: int = 4
    epochs: int = 3
    max_length: int = 2048
    max_new_tokens: int = 512
    seed: int = 1
    precision: str = "bfloat16"
    warmup_ratio: float = 0.1
    lr_schedule: str = "cosine"
    grad_clip: float = 1.0
    num_generations: int = 8
    beta: float = 0.04
    temperature_rollout: float = 0.8


@dataclass
class JTTestConfig:
    alpha: float = 0.05
    alternative: str = "increasing"
    n_boot: int = 1000
    seed: int = 42


@dataclass
class GateConfig:
    jt_p_threshold: float = 0.05
    jt_z_min: float = 0.0
    delta_ratio_min: float = 1.0
    null_result_action: str = "EXPLORE"


@dataclass
class PathsConfig:
    he1_results_json: str = str(H_E1_CODE / "results" / "h-e1" / "experiment_results.json")
    he1_validation_md: str = str(H_M4_ROOT.parents[0] / "h-e1" / "04_validation.md")
    sft_1_3b_dir: str = str(H_M4_ROOT / "code" / "checkpoints" / "sft_1_3b")
    rlef_1_3b_dir: str = str(H_M4_ROOT / "code" / "checkpoints" / "rlef_fraction_1_3b")
    results_dir: str = str(H_M4_ROOT / "results")
    figures_dir: str = str(H_M4_ROOT / "figures")
    logs_dir: str = str(H_M4_ROOT / "code" / "logs")


@dataclass
class FigureConfig:
    dpi: int = 150
    fig_width: float = 8.0
    fig_height: float = 5.0
    output_dir: str = str(H_M4_ROOT / "figures")
    output_format: str = "png"
    color_7b: str = "#2196F3"
    color_1b3: str = "#FF5722"
    color_trend: str = "#4CAF50"
    fig1_name: str = "fig1_7b_delta_by_difficulty.png"
    fig2_name: str = "fig2_jt_test_result.png"
    fig3_name: str = "fig3_1b3_delta_by_difficulty.png"
    fig4_name: str = "fig4_delta_ratio_gate.png"


@dataclass
class H_M4_Config:
    sft_1b3: SFT1B3Config = field(default_factory=SFT1B3Config)
    jt: JTTestConfig = field(default_factory=JTTestConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    figure: FigureConfig = field(default_factory=FigureConfig)
    benchmarks_ordered: tuple = tuple(BENCHMARK_ORDER)
    n_bootstrap: int = 5000
    bootstrap_seed: int = 1
    n_samples: int = 20
    temperature: float = 0.2
    lcb_release: str = "release_v4"
