from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class H_M4Config:
    # EvalPlus parameters
    dataset: str = "humaneval"
    n_samples: int = 8
    temperature: float = 0.8
    backend: str = "hf"

    # Base model (step_0 frozen baseline)
    baseline_model: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"

    # H-M2 paths
    h_m2_results_dir: str = "docs/youra_research/h-m2/results"
    h_m2_code_dir: str = "docs/youra_research/h-m2/code"

    # Experiment dimensions
    conditions: List[str] = field(default_factory=lambda: ["variance50", "random50", "full374"])
    steps: List[str] = field(default_factory=lambda: ["step_10", "step_20", "step_50"])
    baseline_step: str = "step_0"

    # Gate thresholds
    p1_improvement_pp: float = 0.02
    p1_gap_pp: float = 0.01
    p3_efficiency: float = 0.80

    # Output paths
    results_dir: str = "docs/youra_research/h-m4/results"
    figures_dir: str = "docs/youra_research/h-m4/figures"
    eval_output_root: str = "docs/youra_research/h-m4/eval_cache"

    def checkpoint_path(self, condition: str, step: str) -> str:
        if step == self.baseline_step:
            return self.baseline_model
        step_num = int(step.replace("step_", ""))
        return f"{self.h_m2_results_dir}/{condition}/checkpoint-{step_num}"

    def checkpoint_exists(self, condition: str, step: str) -> bool:
        if step == self.baseline_step:
            return True
        return os.path.isdir(self.checkpoint_path(condition, step))

    def eval_output_dir(self, condition: str, step: str) -> str:
        return f"{self.eval_output_root}/{condition}/{step}"

    def samples_path(self, condition: str, step: str) -> str:
        return f"{self.eval_output_dir(condition, step)}/samples.jsonl"

    def __post_init__(self):
        assert self.n_samples >= 1
        assert 0.0 < self.temperature <= 2.0
        assert self.dataset == "humaneval"
        assert len(self.conditions) > 0
        assert len(self.steps) > 0
        assert 0.0 <= self.p3_efficiency <= 1.0
