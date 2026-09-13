from dataclasses import dataclass, field
from typing import List


@dataclass
class H_M2Config:
    # Inputs from H-E1/H-M1
    profiling_json: str = "docs/youra_research/h-e1/results/mbpp_variance_profile.json"

    # Model
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"

    # Dataset
    mbpp_dataset_id: str = "google-research-datasets/mbpp"
    mbpp_subset: str = "full"
    mbpp_split: str = "train"
    k: int = 50
    seed: int = 42

    # GRPO Training
    learning_rate: float = 5e-7
    num_generations: int = 4
    generation_batch_size: int = 4
    max_steps: int = 50
    beta: float = 0.0       # avoids spurious KL grads on zero-std groups (TRL #5588)
    logging_steps: int = 1
    use_vllm: bool = False
    save_steps: List[int] = field(default_factory=lambda: [10, 20, 50])
    max_new_tokens: int = 512
    exec_timeout: float = 5.0

    # Gate evaluation
    gate_checkpoints: List[int] = field(default_factory=lambda: [10, 20, 50])
    gap_threshold_pp: float = 0.05

    # Output
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"

    min_trl_version: str = "0.15.0"

    def __post_init__(self):
        assert self.k == 50
        assert self.num_generations == self.generation_batch_size == 4
        assert self.logging_steps == 1
        assert self.beta == 0.0
        assert len(self.save_steps) > 0
