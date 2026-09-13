"""H-M3 configuration dataclasses for Sparsity-Rank Sensitivity Correlation experiment."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import yaml


@dataclass
class ExperimentConfig:
    """H-M3: Sparsity-Rank Sensitivity Correlation experiment config."""

    # Model settings
    model_name: str = "meta-llama/Llama-3.1-8B"
    n_layers: int = 32
    torch_dtype: str = "bfloat16"
    local_files_only: bool = True
    device_map: str = "auto"
    max_length: int = 512

    # LoRA training (uniform reference)
    lora_r: int = 16
    lora_alpha: int = 16
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])
    lora_dropout: float = 0.0

    # Optimizer
    lr: float = 2e-4
    weight_decay: float = 0.01
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999

    # Schedule
    warmup_ratio: float = 0.03

    # Training loop
    batch_size: int = 16
    num_epochs: int = 3
    gradient_accumulation_steps: int = 1
    gradient_checkpointing: bool = False

    # Seeds
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44, 45, 46])

    # Sensitivity sweep
    delta_r: int = 2
    delta_r_fallback: int = 4
    sensitive_drop_threshold: float = 0.005

    # Tasks
    tasks: List[str] = field(default_factory=lambda: ["sst2", "mnli"])

    # AdaLoRA
    adalora_target_r: int = 9
    adalora_init_r: int = 16
    adalora_tinit: int = 100
    adalora_tfinal: int = 1500
    adalora_deltaT: int = 10
    adalora_beta1: float = 0.85
    adalora_beta2: float = 0.85
    adalora_orth_reg_weight: float = 0.5

    # Spectral
    top_k_svs: int = 4

    # Gate thresholds
    pearson_r_threshold: float = -0.4
    kendall_tau_threshold: float = 0.4
    unique_var_threshold: float = 0.20
    p_value_threshold: float = 0.05
    r6_min_sensitive_layers: int = 5

    # Paths
    h_m2_results_path: str = "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m2/experiment_results.json"
    figures_dir: str = "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m3/figures/"
    results_path: str = "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m3/experiment_results.json"
    validation_report_path: str = "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m3/04_validation.md"

    def __post_init__(self):
        assert self.n_layers == 32, "LLaMA-3.1-8B must have 32 layers"
        assert self.torch_dtype in ("float16", "bfloat16", "float32")
        assert self.delta_r in (2, 4), "delta_r must be 2 or 4"
        assert self.delta_r_fallback in (2, 4), "delta_r_fallback must be 2 or 4"
        assert len(self.seeds) >= 1

    def to_yaml(self, path: str) -> None:
        import dataclasses
        d = dataclasses.asdict(self)
        with open(path, "w") as f:
            yaml.dump(d, f, default_flow_style=False)

    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig":
        with open(path) as f:
            d = yaml.safe_load(f)
        return cls(**d)


@dataclass
class AdaLoRAConfig:
    """AdaLoRA hyperparameters for H-M3 reference run (60% budget)."""

    target_r: int = 9
    init_r: int = 16
    tinit: int = 100
    tfinal: int = 1500
    deltaT: int = 10
    beta1: float = 0.85
    beta2: float = 0.85
    orth_reg_weight: float = 0.5
    total_budget_pct: float = 0.60

    def __post_init__(self):
        assert self.target_r == int(self.total_budget_pct * 16), (
            f"target_r={self.target_r} must equal floor(total_budget_pct * 16)"
        )
        assert 0 < self.beta1 < 1 and 0 < self.beta2 < 1
        assert self.tinit < self.tfinal


@dataclass
class GateConfig:
    """Gate evaluation thresholds for H-M3 MUST_WORK criteria."""

    pearson_r_threshold: float = -0.4
    kendall_tau_threshold: float = 0.4
    unique_var_threshold: float = 0.20
    p_value_threshold: float = 0.05
    sensitive_drop_threshold: float = 0.005
    r6_min_sensitive_layers: int = 5

    def gate_pass(
        self,
        pearson_r_sst2: float,
        pearson_r_mnli: float,
        kendall_tau_sst2: float,
        kendall_tau_mnli: float,
        unique_var_sparsity: float,
        p_value_sparsity: float,
        n_sensitive_sst2: int,
    ) -> bool:
        r6_fallback = n_sensitive_sst2 < self.r6_min_sensitive_layers
        if r6_fallback:
            gate_pearson = pearson_r_mnli <= self.pearson_r_threshold
            gate_tau = kendall_tau_mnli >= self.kendall_tau_threshold
        else:
            import math
            p_sst2 = pearson_r_sst2 if not math.isnan(pearson_r_sst2) else 0.0
            p_mnli = pearson_r_mnli if not math.isnan(pearson_r_mnli) else 0.0
            gate_pearson = (p_sst2 <= self.pearson_r_threshold and
                            p_mnli <= self.pearson_r_threshold)
            gate_tau = (kendall_tau_sst2 >= self.kendall_tau_threshold and
                        kendall_tau_mnli >= self.kendall_tau_threshold)
        gate_spectral = (unique_var_sparsity >= self.unique_var_threshold and
                         p_value_sparsity < self.p_value_threshold)
        return gate_pearson and gate_tau and gate_spectral


@dataclass
class PathConfig:
    """Path management for H-M3."""

    BASE: str = "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope"

    h_m2_results_path: str = field(init=False)
    model_cache_path: str = "~/.cache/huggingface/hub/models--meta-llama--Llama-3.1-8B"
    figures_dir: str = field(init=False)
    results_path: str = field(init=False)
    validation_report_path: str = field(init=False)
    tasks: List[str] = field(default_factory=lambda: ["sst2", "mnli"])

    def __post_init__(self):
        self.h_m2_results_path = f"{self.BASE}/h-m2/experiment_results.json"
        self.figures_dir = f"{self.BASE}/h-m3/figures/"
        self.results_path = f"{self.BASE}/h-m3/experiment_results.json"
        self.validation_report_path = f"{self.BASE}/h-m3/04_validation.md"
