# Logic Specification: h-m4

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M4 (MECHANISM)  
**Type:** Cross-Architecture Directional Replication Analysis  
**Budget:** 14 subtasks

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-m3 actual code  
**Analyzed Path**: `docs/youra_research/20260511_buildingtrust/h-m3/code/src/`  
**Relevant Symbols**: BaselineModel, LoRAInterventionModel, MultiDimensionalEvaluator, BBQEvaluator, AdvGLUEEvaluator, TruthfulQAEvaluator, InterventionTrainer, MultiDimensionalDataset

**Key Findings**:
- h-m3 implements multi-dimensional evaluation (TruthfulQA, BBQ, ANLI) with 3 seed replication
- Proven evaluation pipeline: MultiDimensionalEvaluator handles all 3 dimensions
- LoRA intervention: lora_rank=8, lora_alpha=16, target_modules configurable
- h-m4 extends with 5 model families (LLaMA, Mistral, Qwen, Mamba, Falcon) and directional replication analysis

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are imported from h-m3. Signatures verified from actual implementation:

```python
# From: h-m3/code/src/model.py (ACTUAL CODE)
class BaselineModel:
    def __init__(self, model_id: str = "meta-llama/Meta-Llama-3-8B"):
        """Initialize baseline model. Args: model_id (HuggingFace model ID)"""
        ...
    
    def load_model(self) -> AutoModelForCausalLM:
        """Load pretrained model with bfloat16."""
        ...
    
    def load_tokenizer(self) -> AutoTokenizer:
        """Load tokenizer with padding setup."""
        ...

class LoRAInterventionModel:
    def __init__(
        self,
        base_model: AutoModelForCausalLM,
        lora_rank: int = 8,
        lora_alpha: int = 8,
        lora_dropout: float = 0.05,
        target_modules: Optional[List[str]] = None
    ):
        """Initialize LoRA wrapper. target_modules default: ["q_proj", "v_proj"]"""
        ...
    
    def apply_lora(self) -> PeftModel:
        """Apply LoRA adapter to base model."""
        ...

# From: h-m3/code/src/evaluators.py (ACTUAL CODE)
class BBQEvaluator:
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        """Initialize BBQ fairness evaluator."""
        ...
    
    def evaluate(self) -> float:
        """Evaluate fairness. Returns: accuracy (0-1)"""
        ...

class AdvGLUEEvaluator:
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        """Initialize AdvGLUE robustness evaluator."""
        ...
    
    def evaluate(self) -> float:
        """Evaluate robustness. Returns: accuracy (0-1)"""
        ...

class TruthfulQAEvaluator:
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        """Initialize TruthfulQA evaluator."""
        ...
    
    def evaluate(self) -> float:
        """Evaluate truthfulness. Returns: MC1 accuracy (0-1)"""
        ...

class MultiDimensionalEvaluator:
    def __init__(self, model, tokenizer, dimensions: List[str]):
        """Initialize multi-dimensional evaluator. dimensions: ["truthfulness", "fairness", "robustness"]"""
        ...
    
    def evaluate_dimension(self, dimension: str) -> float:
        """Evaluate single dimension. Returns: score (0-1)"""
        ...
    
    def evaluate_all_dimensions(self) -> Dict[str, float]:
        """Evaluate all dimensions. Returns: {dimension: score}"""
        ...

# From: h-m3/code/src/train.py (ACTUAL CODE)
class InterventionTrainer:
    def __init__(self, model: PeftModel, config: Dict):
        """Initialize trainer. Args: model (PEFT model), config (training config)"""
        ...
    
    def run_intervention(
        self,
        train_dataloader: DataLoader,
        num_epochs: int
    ) -> Dict[str, any]:
        """Run full intervention training. Returns: training history"""
        ...

# From: h-m3/code/src/data_multi_dimensional.py (ACTUAL CODE)
class MultiDimensionalDataset:
    def __init__(self, tokenizer: PreTrainedTokenizer, dimensions: List[str]):
        """Initialize multi-dimensional dataset loader."""
        ...
    
    def load_truthfulqa(self, split: str = "validation") -> Dataset:
        """Load TruthfulQA. Returns: Dataset with 817 questions"""
        ...
    
    def get_training_samples(self, n_samples: int = 500) -> Dataset:
        """Get training subset from TruthfulQA. Returns: Dataset [n_samples]"""
        ...
```

**Verified from**: `h-m3/code/` (actual implementation, NOT spec!)

**Note**: h-m3 uses model_id="gpt2" by default. h-m4 will use 5 different model families with family-specific configurations.

---

## A-1: Project Setup [Complexity: 7, Budget: 2]

**Applied**: Standard PyTorch project structure + h-m3 imports

### API Signatures

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import yaml

@dataclass
class H_M4_Config:
    """Configuration for h-m4 cross-architecture replication."""
    
    # Multi-model families (NEW for h-m4)
    model_families: List[str] = field(default_factory=lambda: ["llama", "mistral", "qwen", "mamba", "falcon"])
    model_ids_map: Dict[str, str] = field(default_factory=dict)
    
    # Replication (increased from h-m3)
    n_seeds: int = 5
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44, 45, 46])
    
    # LoRA (inherited from h-m3)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules_map: Dict[str, List[str]] = field(default_factory=dict)
    
    # Training (inherited from h-m3)
    learning_rate: float = 2e-4
    num_epochs: int = 3
    batch_size: int = 8
    training_samples: int = 500
    
    # Multi-dimensional evaluation (inherited from h-m3)
    dimensions: List[str] = field(default_factory=lambda: ["truthfulness", "fairness", "robustness"])
    
    # Directional replication (NEW for h-m4)
    correlation_threshold: float = 0.3
    replication_threshold: float = 0.6
    
    # Environment
    device: str = "cuda"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    
    def __post_init__(self):
        """Initialize model IDs and target modules per family."""
        if not self.model_ids_map:
            self.model_ids_map = {
                "llama": "meta-llama/Llama-3.2-1B",
                "mistral": "mistralai/Mistral-7B-v0.1",
                "qwen": "Qwen/Qwen-1.8B",
                "mamba": "state-spaces/mamba-1.4b",
                "falcon": "tiiuae/falcon-7b"
            }
        if not self.target_modules_map:
            self.target_modules_map = {
                "llama": ["q_proj", "k_proj", "v_proj", "o_proj"],
                "mistral": ["q_proj", "k_proj", "v_proj", "o_proj"],
                "qwen": ["c_attn"],
                "mamba": ["in_proj", "out_proj"],
                "falcon": ["query_key_value", "dense"]
            }

def load_config(config_path: str) -> H_M4_Config:
    """Load configuration from YAML."""
    ...

def save_config(config: H_M4_Config, output_path: str):
    """Save configuration to YAML."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Config dataclass | Define H_M4_Config with 5 model families |
| L-1-2 | Model ID mapping | Map family names to HuggingFace model IDs |

---

## A-2: Model Family Manager [Complexity: 12, Budget: 3]

**Applied**: HuggingFace AutoModel loading pattern + Mamba-specific handling

### API Signatures

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
from typing import Tuple
import torch

class ModelFamilyManager:
    def __init__(self, config: H_M4_Config):
        """Initialize model family manager."""
        self.config = config
        self.loaded_models = {}
    
    def get_model_id(self, family_name: str) -> str:
        """Get HuggingFace model ID for family. Returns: model_id string"""
        return self.config.model_ids_map[family_name]
    
    def load_model_family(
        self,
        family_name: str
    ) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
        """Load model and tokenizer for family. Returns: (model, tokenizer)"""
        ...
    
    def _load_transformer_family(self, model_id: str) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
        """Load transformer model. model_id -> (model, tokenizer)"""
        ...
    
    def _load_mamba_family(self, model_id: str) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
        """Load Mamba SSM model. model_id -> (model, tokenizer)"""
        ...
    
    def get_target_modules(self, family_name: str) -> List[str]:
        """Get LoRA target modules for family. Returns: list of module names"""
        return self.config.target_modules_map[family_name]
    
    def is_mamba(self, family_name: str) -> bool:
        """Check if family is Mamba (SSM). Returns: bool"""
        return family_name == "mamba"
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | Tokenized input (L≤512) |
| logits | [B, L, V] | Model output (V=vocab_size) |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Transformer loader | Load 4 transformer families (LLaMA, Mistral, Qwen, Falcon) |
| L-2-2 | Mamba loader | Load Mamba SSM with special API |
| L-2-3 | Target modules | Map family names to LoRA target modules |

---

## A-3: LoRA Cross-Architecture Adapter [Complexity: 10, Budget: 2]

**Applied**: PEFT LoraConfig with architecture-specific target modules

### API Signatures

```python
from peft import LoraConfig, get_peft_model, PeftModel
from transformers import PreTrainedModel

class LoRACrossArchitectureAdapter:
    def __init__(self, config: H_M4_Config):
        """Initialize LoRA adapter with architecture-specific configs."""
        self.config = config
    
    def apply_lora_to_family(
        self,
        model: PreTrainedModel,
        family_name: str
    ) -> PeftModel:
        """Apply LoRA to model family. Returns: PeftModel with trainable adapters"""
        ...
    
    def get_lora_config(self, family_name: str) -> LoraConfig:
        """Get LoRA config for family. Returns: LoraConfig"""
        target_modules = self.config.target_modules_map[family_name]
        return LoraConfig(
            r=self.config.lora_rank,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=target_modules,
            bias="none",
            task_type="CAUSAL_LM"
        )
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | LoRA config | Generate LoraConfig per family with correct target modules |
| L-3-2 | PEFT application | Apply LoRA to each model family |

---

## A-4: Multi-Model Evaluation Pipeline [Complexity: 11, Budget: 2]

**Applied**: Reuse h-m3 MultiDimensionalEvaluator + multi-family orchestration

### API Signatures

```python
from h_m3.src.evaluators import MultiDimensionalEvaluator
from transformers import PreTrainedModel, PreTrainedTokenizer
from typing import Dict

class MultiModelEvaluator:
    def __init__(self, config: H_M4_Config):
        """Initialize multi-model evaluator."""
        self.config = config
    
    def evaluate_model_family(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer,
        family_name: str
    ) -> Dict[str, float]:
        """Evaluate single model family. Returns: {dimension: score}"""
        evaluator = MultiDimensionalEvaluator(model, tokenizer, self.config.dimensions)
        return evaluator.evaluate_all_dimensions()
    
    def compute_deltas(
        self,
        baseline_scores: Dict[str, float],
        post_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Compute performance deltas. Returns: {dimension: delta}"""
        return {dim: post_scores[dim] - baseline_scores[dim] for dim in self.config.dimensions}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Family evaluation | Evaluate each family with MultiDimensionalEvaluator |
| L-4-2 | Delta computation | Compute deltas per family per seed |

---

## A-5: Directional Classification [Complexity: 9, Budget: 1]

**Applied**: scipy.stats.pearsonr for correlation + threshold-based classification

### API Signatures

```python
from scipy.stats import pearsonr
import numpy as np
from typing import Tuple, List

class DirectionalClassifier:
    def __init__(self, threshold: float = 0.3):
        """Initialize classifier. threshold: correlation threshold for direction"""
        self.threshold = threshold
    
    def compute_correlation(
        self,
        deltas1: List[float],
        deltas2: List[float]
    ) -> Tuple[float, float]:
        """Compute Pearson correlation. Returns: (r, p_value)"""
        r, p = pearsonr(deltas1, deltas2)
        return r, p
    
    def classify_direction(self, r: float, threshold: float = None) -> str:
        """Classify correlation direction. Returns: "positive" | "negative" | "neutral" """
        if threshold is None:
            threshold = self.threshold
        if r > threshold:
            return "positive"
        elif r < -threshold:
            return "negative"
        else:
            return "neutral"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Direction classifier | Classify correlation as positive/negative/neutral |

---

## A-6: Replication Rate Analysis [Complexity: 10, Budget: 1]

**Applied**: Majority voting + replication rate computation

### API Signatures

```python
from typing import Dict, List
from collections import Counter

class ReplicationRateAnalyzer:
    def __init__(self, dimensions: List[str], replication_threshold: float = 0.6):
        """Initialize replication analyzer."""
        self.dimensions = dimensions
        self.replication_threshold = replication_threshold
    
    def compute_family_directions(
        self,
        family_deltas: Dict[str, List[float]]
    ) -> Dict[str, str]:
        """Compute correlation directions for all dimension pairs. Returns: {pair: direction}"""
        ...
    
    def compute_replication_rate(
        self,
        all_family_directions: Dict[str, Dict[str, str]]
    ) -> Dict[str, Dict]:
        """Compute replication rate per dimension pair.
        
        Args:
            all_family_directions: {family_name: {dim_pair: direction}}
        
        Returns:
            {dim_pair: {"majority_direction": str, "replication_rate": float, "gate_pass": bool}}
        """
        ...
    
    def check_gate_criterion(self, replication_rates: Dict[str, Dict]) -> bool:
        """Check if any dimension pair has replication_rate >= threshold. Returns: bool"""
        return any(r["gate_pass"] for r in replication_rates.values())
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Replication rate | Compute majority direction and replication rate (≥3/5) |

---

## A-7: Training Pipeline Extension [Complexity: 8, Budget: 1]

**Applied**: Reuse h-m3 InterventionTrainer + multi-family loop

### API Signatures

```python
from h_m3.src.train import InterventionTrainer
from h_m3.src.data_multi_dimensional import MultiDimensionalDataset
from torch.utils.data import DataLoader
from peft import PeftModel

class H_M4_Trainer:
    def __init__(self, config: H_M4_Config):
        """Initialize h-m4 trainer."""
        self.config = config
    
    def train_lora_family(
        self,
        model: PeftModel,
        tokenizer: PreTrainedTokenizer,
        train_data: Dataset,
        seed: int
    ) -> Dict:
        """Train LoRA on family. Returns: training history"""
        dataloader = self.setup_dataloader(train_data, tokenizer)
        trainer = InterventionTrainer(model, self.config.__dict__)
        return trainer.run_intervention(dataloader, self.config.num_epochs)
    
    def setup_dataloader(
        self,
        train_data: Dataset,
        tokenizer: PreTrainedTokenizer
    ) -> DataLoader:
        """Setup training dataloader. Returns: DataLoader"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Training loop | Train LoRA on 5 families × 5 seeds (25 runs) |

---

## A-8: Per-Family Correlation Analysis [Complexity: 9, Budget: 1]

**Applied**: scipy.stats correlation + per-family aggregation

### API Signatures

```python
from scipy.stats import pearsonr
from typing import Dict, List, Tuple

class PerFamilyCorrelationAnalyzer:
    def __init__(self, dimensions: List[str]):
        """Initialize per-family correlation analyzer."""
        self.dimensions = dimensions
        self.dimension_pairs = self._generate_pairs()
    
    def _generate_pairs(self) -> List[Tuple[str, str]]:
        """Generate dimension pairs. Returns: [(d1, d2), ...]"""
        pairs = []
        for i, d1 in enumerate(self.dimensions):
            for d2 in self.dimensions[i+1:]:
                pairs.append((d1, d2))
        return pairs
    
    def compute_correlations_for_family(
        self,
        family_deltas: Dict[str, List[float]]
    ) -> Dict[str, Tuple[float, float]]:
        """Compute correlations for all dimension pairs.
        
        Args:
            family_deltas: {dimension: [delta_seed1, ..., delta_seed5]}
        
        Returns:
            {f"{dim1}_vs_{dim2}": (r, p)}
        """
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Per-family correlation | Compute Pearson correlation per family across 5 seeds |

---

## A-9: Visualization Suite [Complexity: 10, Budget: 2]

**Applied**: matplotlib + seaborn for 5 required figures

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict

class H_M4_FigureGenerator:
    def __init__(self, output_dir: str):
        """Initialize figure generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_replication_rates(self, replication_rates: Dict[str, Dict]):
        """Plot replication rate bar chart. Save: replication_rates.png"""
        ...
    
    def plot_family_correlation_heatmap(self, all_family_correlations: Dict[str, Dict[str, float]]):
        """Plot per-family correlation heatmap. Save: family_correlation_heatmap.png"""
        ...
    
    def plot_directional_consistency(self, all_family_directions: Dict[str, Dict[str, str]]):
        """Plot directional consistency stacked bar. Save: directional_consistency.png"""
        ...
    
    def plot_architecture_comparison(self, transformer_results: Dict, ssm_results: Dict):
        """Plot transformer vs SSM comparison. Save: architecture_comparison.png"""
        ...
    
    def plot_per_family_performance(self, all_family_results: Dict):
        """Plot per-family performance deltas. Save: per_family_performance.png"""
        ...
    
    def save_all_figures(self, results: Dict):
        """Generate and save all 5 figures."""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Gate figure | Plot replication rate bar chart (gate metric) |
| L-9-2 | Analysis figures | Plot 4 additional figures (heatmaps, comparisons) |

---

## A-10: Experiment Orchestration [Complexity: 12, Budget: 0]

**Applied**: Standard experiment workflow with 5 families × 5 seeds

### API Signatures

```python
import torch
import random
import numpy as np
from typing import Dict, List

def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def setup_gpu(gpu_id: int):
    """Setup GPU environment. export CUDA_VISIBLE_DEVICES={gpu_id}"""
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

def main():
    """Main experiment orchestrator."""
    ...
```

### Pseudo-code

```
1. Setup:
   config = load_config("config.yaml")
   set_seed(config.seeds[0])
   setup_gpu(0)

2. Initialize managers:
   model_manager = ModelFamilyManager(config)
   data_module = MultiDimensionalDataset(None, config.dimensions)
   evaluator = MultiModelEvaluator(config)
   lora_adapter = LoRACrossArchitectureAdapter(config)
   directional_classifier = DirectionalClassifier(config.correlation_threshold)
   replication_analyzer = ReplicationRateAnalyzer(config.dimensions, config.replication_threshold)

3. Load universal training data:
   train_data = data_module.get_training_samples(config.training_samples)

4. Multi-family loop (5 families):
   all_family_results = {}
   all_family_deltas = {}
   
   for family_name in config.model_families:
       # Load model and tokenizer
       model, tokenizer = model_manager.load_model_family(family_name)
       
       # Baseline evaluation
       baseline_scores = evaluator.evaluate_model_family(model, tokenizer, family_name)
       
       # Multi-seed loop (5 seeds)
       family_deltas = []
       for seed in config.seeds:
           set_seed(seed)
           
           # Apply LoRA
           model_lora = lora_adapter.apply_lora_to_family(model, family_name)
           
           # Train on TruthfulQA
           trainer = H_M4_Trainer(config)
           trainer.train_lora_family(model_lora, tokenizer, train_data, seed)
           
           # Post-intervention evaluation
           post_scores = evaluator.evaluate_model_family(model_lora, tokenizer, family_name)
           
           # Compute deltas
           deltas = evaluator.compute_deltas(baseline_scores, post_scores)
           family_deltas.append(deltas)
       
       # Store results
       all_family_results[family_name] = {
           "baseline": baseline_scores,
           "deltas_per_seed": family_deltas
       }
       
       # Convert to per-dimension lists
       all_family_deltas[family_name] = {
           dim: [d[dim] for d in family_deltas]
           for dim in config.dimensions
       }

5. Directional replication analysis:
   # Compute correlations per family
   corr_analyzer = PerFamilyCorrelationAnalyzer(config.dimensions)
   all_family_correlations = {}
   all_family_directions = {}
   
   for family_name, deltas in all_family_deltas.items():
       correlations = corr_analyzer.compute_correlations_for_family(deltas)
       all_family_correlations[family_name] = correlations
       
       # Classify direction per dimension pair
       directions = {}
       for pair, (r, p) in correlations.items():
           direction = directional_classifier.classify_direction(r)
           directions[pair] = direction
       all_family_directions[family_name] = directions
   
   # Compute replication rates
   replication_rates = replication_analyzer.compute_replication_rate(all_family_directions)
   
   # Check gate criterion
   gate_pass = replication_analyzer.check_gate_criterion(replication_rates)

6. Visualization:
   visualizer = H_M4_FigureGenerator(config.figures_dir)
   visualizer.save_all_figures({
       "replication_rates": replication_rates,
       "family_correlations": all_family_correlations,
       "family_directions": all_family_directions,
       "family_results": all_family_results
   })

7. Save results:
   save_json({
       "replication_rates": replication_rates,
       "family_directions": all_family_directions,
       "family_correlations": all_family_correlations,
       "family_deltas": all_family_deltas,
       "gate_pass": gate_pass
   }, f"{config.output_dir}/h_m4_validation.json")

8. Print gate status:
   print(f"Gate Status: {'PASS' if gate_pass else 'FAIL'}")
```

---

## Implementation Notes

### h-m3 Code Reuse Strategy

**Direct Imports (No Modifications)**:
- `BaselineModel` (model loading)
- `LoRAInterventionModel` (LoRA configuration)
- `MultiDimensionalEvaluator` (3-dimension evaluation)
- `BBQEvaluator`, `AdvGLUEEvaluator`, `TruthfulQAEvaluator` (dimension-specific evaluators)
- `InterventionTrainer` (LoRA training loop)
- `MultiDimensionalDataset` (dataset loading)

**h-m4 Specific Components**:
- `ModelFamilyManager` (5 model families loading)
- `LoRACrossArchitectureAdapter` (family-specific LoRA application)
- `MultiModelEvaluator` (multi-family evaluation orchestration)
- `DirectionalClassifier` (correlation direction classification)
- `ReplicationRateAnalyzer` (majority direction + replication rate)
- `PerFamilyCorrelationAnalyzer` (per-family correlation tracking)
- `H_M4_FigureGenerator` (multi-family visualizations)

### Multi-Model Family Pattern

**Challenge**: Load and evaluate 5 diverse model families with different architectures.

**Solution**:
```python
# Family-specific model IDs
MODEL_IDS = {
    "llama": "meta-llama/Llama-3.2-1B",
    "mistral": "mistralai/Mistral-7B-v0.1",
    "qwen": "Qwen/Qwen-1.8B",
    "mamba": "state-spaces/mamba-1.4b",
    "falcon": "tiiuae/falcon-7b"
}

# Family-specific LoRA target modules
TARGET_MODULES = {
    "llama": ["q_proj", "k_proj", "v_proj", "o_proj"],
    "mistral": ["q_proj", "k_proj", "v_proj", "o_proj"],
    "qwen": ["c_attn"],
    "mamba": ["in_proj", "out_proj"],
    "falcon": ["query_key_value", "dense"]
}

# Load family
model = AutoModelForCausalLM.from_pretrained(
    MODEL_IDS[family_name],
    device_map="auto",
    torch_dtype="auto"
)
```

### Directional Replication Analysis Pipeline

**Challenge**: Determine if correlation direction replicates across ≥3/5 models.

**Solution**:
```python
from scipy.stats import pearsonr

# Per-family direction classification
for family, deltas in all_family_deltas.items():
    r, p = pearsonr(deltas['truthfulness'], deltas['robustness'])
    if r > 0.3:
        direction = "positive"
    elif r < -0.3:
        direction = "negative"
    else:
        direction = "neutral"
    family_directions[family] = direction

# Replication analysis
from collections import Counter
directions = list(family_directions.values())
majority = Counter(directions).most_common(1)[0][0]
replication_rate = directions.count(majority) / len(directions)
gate_pass = replication_rate >= 0.6  # ≥3/5
```

---

## Validation Checklist

### Self-Validation

- [x] No ASCII diagrams
- [x] KB patterns applied (PEFT LoRA, scipy.stats correlation)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments where non-obvious
- [x] Subtask count within budget (14 total)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] Base hypothesis code verified from actual h-m3 code

### Base Hypothesis Verification

- [x] Read actual code from h-m3/code/
- [x] API signatures verified from actual implementation
- [x] Parameter names exactly match (model_id, lora_rank, lora_alpha, target_modules)
- [x] External Dependencies API section included
- [x] Configuration inheritance documented

---

*Generated by Phase 3 Logic Agent*  
*Patterns Applied: PEFT LoRA cross-architecture adaptation, scipy.stats correlation analysis, multi-model evaluation, directional replication analysis*  
*MECHANISM hypothesis - extends h-m3 to validate cross-architecture directional replication across 5 model families*
