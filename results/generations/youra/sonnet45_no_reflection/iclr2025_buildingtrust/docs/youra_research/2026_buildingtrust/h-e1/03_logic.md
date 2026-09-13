# Logic Specification: h-e1

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-E1 (EXISTENCE)  
**Type:** Proof-of-Concept  
**Budget:** 5 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: Green-field project - designing new APIs  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## A-2: Data Loading [Complexity: 8, Budget: 2]

**Applied**: HuggingFace datasets standard loading pattern

### API Signatures

```python
from datasets import Dataset
from transformers import PreTrainedTokenizer
from typing import Dict, List, Optional

class TrustworthinessDataset:
    def __init__(self, dimension: str, split: str = "validation"):
        """Initialize dataset loader for specific dimension."""
        self.dimension = dimension  # "truthfulness", "fairness", "robustness"
        self.split = split
        self.data: Optional[Dataset] = None
    
    def load_truthfulqa(self) -> Dataset:
        """Load TruthfulQA dataset. Returns HF Dataset with 817 samples."""
        ...
    
    def load_bbq(self) -> Dataset:
        """Load BBQ dataset. Returns HF Dataset with ~58K samples."""
        ...
    
    def load_advglue(self) -> Dataset:
        """Load AdvGLUE dataset. Returns HF Dataset."""
        ...
    
    def __len__(self) -> int:
        """Dataset length."""
        ...
    
    def __getitem__(self, idx: int) -> Dict[str, str]:
        """Get item. Returns: {"question": str, "choices": List[str], "label": int}"""
        ...

class DataCollator:
    def __init__(self, tokenizer: PreTrainedTokenizer, max_length: int = 512):
        """Initialize collator with tokenizer."""
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __call__(self, features: List[Dict]) -> Dict[str, torch.Tensor]:
        """
        Collate batch.
        Input: List of dicts with "question", "choices"
        Output: {"input_ids": [B, L], "attention_mask": [B, L], "labels": [B]}
        """
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Dataset loaders | Implement load_truthfulqa, load_bbq, load_advglue |
| L-2-2 | Data collator | Tokenization with padding/truncation |

---

## A-3: Model Implementation [Complexity: 10, Budget: 2]

**Applied**: HuggingFace PEFT LoRA pattern

### API Signatures

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, PeftModel
import torch
from typing import Dict

class BaselineModel:
    def __init__(self, model_id: str = "meta-llama/Meta-Llama-3-8B"):
        """Initialize baseline model."""
        self.model_id = model_id
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
    
    def load_model(self) -> AutoModelForCausalLM:
        """Load pretrained model with bfloat16."""
        ...
    
    def load_tokenizer(self) -> AutoTokenizer:
        """Load tokenizer with padding setup."""
        ...
    
    def evaluate(self, dataset: Dataset, dimension: str) -> float:
        """
        Evaluate on dataset.
        Returns: accuracy score (float in [0, 1])
        """
        ...

class LoRAInterventionModel:
    def __init__(
        self, 
        base_model: AutoModelForCausalLM, 
        lora_rank: int = 8,
        target_modules: List[str] = ["q_proj", "v_proj"]
    ):
        """Initialize LoRA intervention wrapper."""
        self.base_model = base_model
        self.lora_rank = lora_rank
        self.target_modules = target_modules
        self.peft_model: Optional[PeftModel] = None
    
    def apply_lora(self) -> PeftModel:
        """
        Apply LoRA adapter to base model.
        Config: r=lora_rank, alpha=lora_rank, dropout=0.05
        Returns: PeftModel with trainable adapters
        """
        ...
    
    def get_trainable_params(self) -> Dict[str, int]:
        """Returns: {"trainable": int, "total": int, "percentage": float}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | Tokenized input |
| logits | [B, L, V] | Model output, V=vocab size |
| loss | scalar | Cross-entropy loss |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | BaselineModel | Load Llama-3-8B with bfloat16 |
| L-3-2 | LoRA wrapper | Apply PEFT config with get_peft_model |

---

## A-4: Training Pipeline [Complexity: 9, Budget: 0]

**Note**: Zero budget allocated. Deferred to Phase 4 with inline pseudo-code only.

### API Signatures

```python
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from typing import Dict

class InterventionTrainer:
    def __init__(
        self, 
        model: PeftModel, 
        config: Dict,
        device: str = "cuda"
    ):
        """Initialize trainer with LoRA model."""
        self.model = model
        self.config = config
        self.device = device
    
    def setup_optimizer(self, lr: float = 5e-5) -> AdamW:
        """Setup AdamW optimizer. Returns: optimizer with weight_decay=0.01"""
        ...
    
    def setup_scheduler(self, optimizer: AdamW, num_steps: int):
        """Setup cosine scheduler with 100 warmup steps."""
        ...
    
    def train_epoch(self, dataloader) -> Dict[str, float]:
        """
        Train single epoch.
        Returns: {"loss": float, "grad_norm": float}
        """
        ...
    
    def run_intervention(self, target_dimension: str) -> Dict[str, float]:
        """
        Run full intervention training.
        Returns: {"final_loss": float, "epochs": int}
        """
        ...

def train_single_replicate(
    base_model: AutoModelForCausalLM,
    target_dimension: str,
    lr: float,
    epochs: int,
    lora_rank: int,
    seed: int
) -> Dict[str, float]:
    """
    Train single replicate with specified hyperparameters.
    Returns: {
        "truthfulness": float,
        "fairness": float, 
        "robustness": float
    }
    """
    ...
```

### Pseudo-code

```
1. Initialize LoRA model with sampled hyperparameters
2. Setup optimizer (AdamW) and scheduler (cosine with warmup)
3. Load target dimension dataset (e.g., TruthfulQA)
4. For each epoch:
   a. Iterate dataloader batches
   b. Forward pass: logits = model(input_ids)
   c. Compute loss: cross_entropy(logits, labels)
   d. Backward pass with gradient accumulation (steps=4)
   e. Optimizer step + scheduler step
5. Evaluate on all 3 dimensions
6. Return delta scores vs baseline
```

---

## A-5: Evaluation System [Complexity: 11, Budget: 1]

**Applied**: Standard evaluation pattern with scipy stats

### API Signatures

```python
from scipy.stats import pearsonr
from typing import Tuple, Dict, List

class TruthfulQAEvaluator:
    def __init__(self, model: AutoModelForCausalLM, tokenizer: AutoTokenizer):
        """Initialize evaluator."""
        self.model = model
        self.tokenizer = tokenizer
    
    def compute_mc1(self, dataset: Dataset) -> float:
        """
        MC1 metric: fraction where best answer has highest probability.
        Returns: accuracy in [0, 1]
        """
        ...
    
    def compute_mc2(self, dataset: Dataset) -> float:
        """
        MC2 metric: normalized probability on true answer set.
        Returns: score in [0, 1]
        """
        ...

class BBQEvaluator:
    def __init__(self, model: AutoModelForCausalLM, tokenizer: AutoTokenizer):
        """Initialize evaluator."""
        self.model = model
        self.tokenizer = tokenizer
    
    def compute_bias_score(self, dataset: Dataset) -> float:
        """
        Bias score: accuracy difference (stereotype-aligned vs conflicting).
        Returns: bias score (lower is better)
        """
        ...
    
    def compute_disambiguation_accuracy(self, dataset: Dataset) -> float:
        """
        Disambiguation accuracy on fully informative contexts.
        Returns: accuracy in [0, 1]
        """
        ...

class AdvGLUEEvaluator:
    def __init__(self, model: AutoModelForCausalLM, tokenizer: AutoTokenizer):
        """Initialize evaluator."""
        self.model = model
        self.tokenizer = tokenizer
    
    def compute_adversarial_accuracy(
        self, 
        dataset: Dataset, 
        task: str = "sst2"
    ) -> float:
        """
        Adversarial accuracy on perturbed examples.
        Returns: accuracy in [0, 1]
        """
        ...

class CorrelationAnalyzer:
    def __init__(self, results: List[Dict[str, float]]):
        """
        Initialize analyzer with replicate results.
        results: List of {"truthfulness": x, "fairness": y, "robustness": z}
        """
        self.results = results
        self.baseline_scores: Optional[Dict] = None
    
    def extract_delta_scores(self, baseline_scores: Dict) -> Dict[str, List[float]]:
        """
        Extract delta scores: Δ = post_intervention - baseline
        Returns: {
            "delta_truthfulness": [float] * N,
            "delta_fairness": [float] * N,
            "delta_robustness": [float] * N
        }
        """
        ...
    
    def compute_pearson_correlation(
        self, 
        dim1: str, 
        dim2: str
    ) -> Tuple[float, float]:
        """
        Compute Pearson correlation between two dimensions.
        Returns: (rho, p_value)
        Example: rho, p = compute_pearson_correlation("truthfulness", "fairness")
        """
        ...
    
    def test_significance(self, rho: float, n: int) -> float:
        """
        Fisher's z-transformation for significance test.
        Returns: p_value
        """
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | CorrelationAnalyzer | Implement extract_delta_scores and compute_pearson_correlation |

---

## A-6: Experiment Orchestration [Complexity: 7, Budget: 0]

**Note**: Zero budget allocated. Entry point logic follows standard workflow.

### API Signatures

```python
def evaluate_baseline(
    model: BaselineModel, 
    config: Dict
) -> Dict[str, float]:
    """
    Evaluate baseline on all 3 dimensions.
    Returns: {
        "truthfulness": float,
        "fairness": float,
        "robustness": float
    }
    """
    ...

def run_experiment(config_path: str = "config.yaml") -> Dict:
    """
    Main experiment orchestrator.
    
    Workflow:
    1. Load config and setup seed/GPU
    2. Load baseline model
    3. Measure baseline scores on 3 benchmarks
    4. Run N replicates (N=3 for PoC):
       - Sample hyperparameters (lr, epochs, lora_rank)
       - Train with LoRA on target dimension
       - Evaluate on all 3 dimensions
       - Store delta scores
    5. Compute cross-dimensional correlations
    6. Generate visualizations
    7. Save results
    
    Returns: {
        "correlations": Dict[Tuple[str, str], Tuple[float, float]],
        "baseline_scores": Dict[str, float],
        "replicate_results": List[Dict]
    }
    """
    ...
```

---

## A-7: Visualization [Complexity: 6, Budget: 0]

**Note**: Zero budget allocated. Standard matplotlib/seaborn patterns.

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict

class FigureGenerator:
    def __init__(self, results: Dict, output_dir: str = "./figures"):
        """Initialize figure generator."""
        self.results = results
        self.output_dir = output_dir
    
    def plot_correlation_heatmap(self, correlation_matrix: Dict) -> plt.Figure:
        """
        Plot 3×3 correlation heatmap.
        Input: {"(truth, fair)": (rho, p), ...}
        Returns: matplotlib Figure
        """
        ...
    
    def plot_scatter_grid(self, deltas: Dict[str, List[float]]) -> plt.Figure:
        """
        Plot scatter grid for dimension pairs.
        Shows: (Δtruth, Δfair), (Δtruth, Δrobust), (Δfair, Δrobust)
        Returns: matplotlib Figure with 3 subplots
        """
        ...
    
    def plot_delta_distributions(self, deltas: Dict) -> plt.Figure:
        """
        Plot histograms of delta scores per dimension.
        Returns: matplotlib Figure with 3 subplots
        """
        ...
    
    def plot_intervention_effects(self, mean_deltas: Dict[str, float]) -> plt.Figure:
        """
        Bar chart of mean intervention effects.
        Returns: matplotlib Figure
        """
        ...
    
    def plot_significance_map(self, p_values: Dict) -> plt.Figure:
        """
        Binary heatmap for p<0.01 significance.
        Returns: matplotlib Figure
        """
        ...
    
    def save_all_figures(self):
        """Generate and save all 5 required figures."""
        ...
```

---

## Configuration & Utils

### Config Module

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    """Experiment configuration."""
    model_id: str = "meta-llama/Meta-Llama-3-8B"
    target_dimension: str = "truthfulness"
    n_replicates: int = 3
    lora_ranks: List[int] = field(default_factory=lambda: [8, 16, 32])
    learning_rates: List[float] = field(default_factory=lambda: [1e-5, 5e-5, 1e-4])
    epochs_list: List[int] = field(default_factory=lambda: [1, 3, 5])
    seed: int = 1
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    device: str = "cuda"
    output_dir: str = "./results"

def load_config(config_path: str) -> ExperimentConfig:
    """Load config from YAML."""
    ...

def save_config(config: ExperimentConfig, path: str):
    """Save config to YAML."""
    ...
```

### Utils Module

```python
import torch
import random
import numpy as np
import json

def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def save_results(results: Dict, path: str):
    """Save results to JSON."""
    with open(path, 'w') as f:
        json.dump(results, f, indent=2)

def load_results(path: str) -> Dict:
    """Load results from JSON."""
    with open(path, 'r') as f:
        return json.load(f)

def setup_gpu(device_id: int = 0):
    """Setup single GPU."""
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = str(device_id)

def get_parameter_count(model) -> int:
    """Count total model parameters."""
    return sum(p.numel() for p in model.parameters())

def format_metrics(metrics: Dict) -> str:
    """Format metrics for logging."""
    return " | ".join([f"{k}: {v:.4f}" for k, v in metrics.items()])
```

---

## Entry Point

```python
# main.py
from src.config import load_config
from src.utils import set_seed, setup_gpu, save_results
from src.model import BaselineModel, LoRAInterventionModel
from src.train import train_single_replicate
from src.evaluate import CorrelationAnalyzer
from src.visualize import FigureGenerator

def main():
    """Main experiment entry point."""
    # 1. Setup
    config = load_config("config.yaml")
    set_seed(config.seed)
    setup_gpu(0)
    
    # 2. Load baseline model
    baseline = BaselineModel(config.model_id)
    baseline.load_model()
    baseline.load_tokenizer()
    
    # 3. Measure baseline scores
    baseline_scores = evaluate_baseline(baseline, config)
    save_results(baseline_scores, f"{config.output_dir}/baseline_scores.json")
    
    # 4. Run intervention replicates
    results = []
    for i in range(config.n_replicates):
        print(f"Running replicate {i+1}/{config.n_replicates}")
        replicate_scores = train_single_replicate(
            base_model=baseline.model,
            target_dimension=config.target_dimension,
            lr=config.learning_rates[i],
            epochs=config.epochs_list[i],
            lora_rank=config.lora_ranks[i],
            seed=config.seed + i
        )
        results.append(replicate_scores)
    
    save_results(results, f"{config.output_dir}/intervention_results.json")
    
    # 5. Compute cross-dimensional correlations
    analyzer = CorrelationAnalyzer(results)
    deltas = analyzer.extract_delta_scores(baseline_scores)
    
    correlations = {}
    for dim1, dim2 in [("truthfulness", "fairness"), 
                       ("truthfulness", "robustness"),
                       ("fairness", "robustness")]:
        rho, p_value = analyzer.compute_pearson_correlation(dim1, dim2)
        correlations[(dim1, dim2)] = (rho, p_value)
        print(f"ρ({dim1}, {dim2}) = {rho:.3f}, p = {p_value:.3e}")
    
    save_results(correlations, f"{config.output_dir}/correlation_analysis.json")
    
    # 6. Generate visualizations
    visualizer = FigureGenerator(
        results={"deltas": deltas, "correlations": correlations},
        output_dir=f"{config.output_dir}/../figures"
    )
    visualizer.save_all_figures()
    
    print("Experiment completed successfully!")

if __name__ == "__main__":
    main()
```

---

## Budget Summary

| Task | Complexity | Budget Allocated | Budget Used |
|------|------------|-----------------|-------------|
| A-2 | 8 | 2 | 2 |
| A-3 | 10 | 2 | 2 |
| A-4 | 9 | 0 | 0 |
| A-5 | 11 | 1 | 1 |
| A-6 | 7 | 0 | 0 |
| A-7 | 6 | 0 | 0 |
| **Total** | **56** | **5** | **5** |

**Note**: Tasks with zero budget (A-4, A-6, A-7) receive API signatures and pseudo-code only. Implementation details deferred to Phase 4 coder with inline documentation.

---

## Validation Checklist

- [x] All function signatures include type hints
- [x] Tensor shapes documented in code comments
- [x] External dependencies specified (torch, transformers, peft, datasets, scipy)
- [x] EXISTENCE hypothesis constraint: Single model (Llama-3-8B), 3 replicates
- [x] Entry point workflow matches experiment requirements
- [x] Budget allocation: 5 subtasks distributed across high-complexity tasks
- [x] Green-field project: No base hypothesis dependencies
- [x] Codebase Analysis (Serena) section included
- [x] Applied patterns documented for each task

---

*Generated by Phase 3 Logic Agent*  
*Patterns Applied: HuggingFace PEFT LoRA, PyTorch standard modules, scipy statistical analysis*  
*EXISTENCE hypothesis - minimal API design for proof-of-concept validation*
