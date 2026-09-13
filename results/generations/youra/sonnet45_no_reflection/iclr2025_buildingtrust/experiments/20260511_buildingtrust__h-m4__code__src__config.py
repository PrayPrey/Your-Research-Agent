"""Configuration for H-M2 Experiment"""
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

@dataclass
class H_M2_Config:
    """
    Complete configuration for H-M2 MECHANISM hypothesis.
    Extends h-m1 with representation extraction and CKA analysis.
    """

    # Project
    project_name: str = "h-m2-representation-change"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    activation_cache_dir: str = "./outputs/activations"

    # Model (inherited from h-m1)
    model_id: str = "gpt2"
    device: str = "cuda"

    # LoRA (inherited from h-m1, verified values)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    lora_bias: str = "none"
    task_type: str = "CAUSAL_LM"

    # Training (inherited from h-m1)
    learning_rate: float = 1e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0

    # Data (TruthfulQA only, inherited from h-m1)
    max_length: int = 512
    truthfulqa_task: str = "truthfulqa_mc2"
    training_samples: int = 100
    cache_dir: Optional[str] = None

    # Experiment
    num_replicates: int = 3
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])

    # Evaluation (inherited from h-m1)
    eval_batch_size: int = 8

    # Representation Extraction (new for h-m2)
    n_layers: int = 12
    layers_to_analyze: List[str] = field(default_factory=list)
    save_activations: bool = True
    activation_format: str = "pt"

    # CKA Analysis (new for h-m2)
    use_pytorch_cka: bool = True
    kernel_type: str = "linear"
    center_kernel: bool = True
    save_cka_scores: bool = True

    # Statistical Analysis (new for h-m2)
    correlation_method: str = "pearson"
    significance_threshold: float = 0.05
    h_m1_performance_delta: float = 0.0232
    min_layers_with_change: int = 12

    # Visualization (new for h-m2)
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"

    def __post_init__(self):
        """Generate layer names for GPT-2 (12 layers)."""
        if not self.layers_to_analyze:
            self.layers_to_analyze = []
            # Attention patterns: blocks.{i}.attn.hook_pattern
            for i in range(12):
                self.layers_to_analyze.append(f"blocks.{i}.attn.hook_pattern")
            # Hidden states: blocks.{i}.hook_resid_post
            for i in range(12):
                self.layers_to_analyze.append(f"blocks.{i}.hook_resid_post")

def get_default_config() -> H_M2_Config:
    """Get default h-m2 configuration"""
    return H_M2_Config()
