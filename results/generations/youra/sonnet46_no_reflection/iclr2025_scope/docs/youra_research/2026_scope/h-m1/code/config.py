"""
H-M1 ExperimentConfig: JointLoRA-KV Task CE Loss Joint Training
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "1")

BASE_DIR = Path(__file__).parent


@dataclass
class ExperimentConfig:
    # Model
    base_model_name: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    locret_checkpoint: str = "hyx21/Locret-llama-3.1-8B-instruct"
    attn_implementation: str = "eager"

    # LoRA
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj"])

    # KV budget
    kv_budget_ratio: float = 0.5
    kv_budget_ratios_sweep: List[float] = field(default_factory=lambda: [0.3, 0.5, 0.7])

    # Locret / GQA architecture (LLaMA-3.1-8B)
    num_layers: int = 32
    num_kv_heads: int = 8
    num_query_heads: int = 32
    kv_repeat: int = 4          # num_query_heads // num_kv_heads
    head_dim: int = 128
    hidden_size: int = 4096
    locret_hidden: int = 1024   # dR
    # CIS input dim: q_proj_out(4096) + k_proj_out(1024) + v_proj_out(1024) = 6144
    cis_input_dim: int = 6144

    # Training
    lora_lr: float = 1e-4
    locret_lr: float = 5e-4
    weight_decay: float = 0.01
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999
    adam_eps: float = 1e-8
    grad_clip: float = 1.0
    warmup_ratio: float = 0.06
    per_device_batch_size: int = 4
    grad_accum_steps: int = 8   # effective batch = 32
    max_seq_length: int = 512
    longbench_max_length: int = 4096

    # Seeds
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])

    # GLUE tasks and epochs
    glue_tasks: List[str] = field(default_factory=lambda: ["mnli", "sst2", "qnli"])
    task_epochs: dict = field(default_factory=lambda: {"mnli": 3, "sst2": 5, "qnli": 5})

    # LongBench tasks
    longbench_tasks: List[str] = field(default_factory=lambda: [
        "narrativeqa", "qasper", "multifieldqa_en"
    ])
    longbench_max_new_tokens: int = 50

    # Paths
    code_dir: Path = BASE_DIR
    results_dir: Path = BASE_DIR / "results"
    outputs_dir: Path = BASE_DIR / "outputs"
    logs_dir: Path = BASE_DIR / "logs"
    figures_dir: Path = BASE_DIR.parent / "figures"

    # PoC subset limits (keeps full train feasible in <4h)
    max_train_samples: int = 2000   # cap per task for PoC
    max_val_samples: int = 500

    # Gate threshold
    gate_threshold_pp: float = 2.0   # percentage points

    def get_epochs(self, task: str) -> int:
        return self.task_epochs.get(task, 3)

    def get_results_path(self, tag: str) -> Path:
        self.results_dir.mkdir(parents=True, exist_ok=True)
        return self.results_dir / f"{tag}.json"

    def get_figures_dir(self) -> Path:
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        return self.figures_dir

    def get_log_path(self, tag: str) -> Path:
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        return self.logs_dir / f"training_{tag}.log"
