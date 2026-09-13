"""Configuration for H-M3 Experiment - Multi-Dimensional Correlation Analysis"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class H_M3_Config:
    """Complete configuration for H-M3 MECHANISM hypothesis.
    Extends h-m2 with multi-dimensional evaluation and cross-dimensional correlation."""
    
    # Project
    project_name: str = "h-m3-cross-dimensional-correlation"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    activation_cache_dir: str = "./outputs/activations"
    
    # Model (inherited from h-m2)
    model_id: str = "gpt2"
    device: str = "cuda"
    
    # LoRA (inherited from h-m2 - proven values)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    lora_bias: str = "none"
    task_type: str = "CAUSAL_LM"
    
    # Training (inherited from h-m2, increased sample size)
    learning_rate: float = 5e-5
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    training_samples: int = 500  # Increased from h-m2's 100
    
    # Data (tokenization settings inherited from h-m2)
    max_length: int = 512
    cache_dir: Optional[str] = None
    
    # Experiment (inherited from h-m2)
    num_replicates: int = 3
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # Evaluation (inherited from h-m2)
    eval_batch_size: int = 8
    
    # Representation Extraction (inherited from h-m2)
    n_layers: int = 12
    layers_to_analyze: List[str] = field(default_factory=list)
    save_activations: bool = True
    activation_format: str = "pt"
    
    # CKA Analysis (inherited from h-m2)
    use_pytorch_cka: bool = True
    kernel_type: str = "linear"
    center_kernel: bool = True
    save_cka_scores: bool = True
    
    # Multi-Dimensional Evaluation (NEW for h-m3)
    dimensions: List[str] = field(default_factory=lambda: ["truthfulness", "fairness", "robustness"])
    eval_limit: Dict[str, Optional[int]] = field(default_factory=lambda: {
        "truthfulness": None,  # Full TruthfulQA validation set (817)
        "fairness": None,      # Full BBQ test split (500+)
        "robustness": None     # Full AdvGLUE standard splits
    })
    
    # Dataset Sources (NEW for h-m3)
    truthfulqa_dataset: str = "truthfulqa/truthful_qa"
    truthfulqa_split: str = "validation"
    truthfulqa_task: str = "generation"
    bbq_dataset: str = "lighteval/bbq_helm"
    bbq_split: str = "test"
    bbq_subset: str = "all"
    advglue_path: Optional[str] = None
    
    # Cross-Dimensional Correlation (NEW for h-m3)
    correlation_method: str = "pearson"
    significance_threshold: float = 0.05
    permutation_iterations: int = 1000
    
    # Statistical Analysis (inherited from h-m2)
    min_layers_with_change: int = 12
    
    # Visualization (inherited from h-m2)
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"
    
    def __post_init__(self):
        """Generate layer names for GPT-2 (12 layers) if not provided."""
        if not self.layers_to_analyze:
            self.layers_to_analyze = []
            for i in range(12):
                self.layers_to_analyze.append(f"blocks.{i}.attn.hook_pattern")
            for i in range(12):
                self.layers_to_analyze.append(f"blocks.{i}.hook_resid_post")

def get_default_config() -> H_M3_Config:
    """Get default h-m3 configuration"""
    return H_M3_Config()

def get_default_dimensions() -> List[str]:
    """Get default trustworthiness dimensions"""
    return ["truthfulness", "fairness", "robustness"]
