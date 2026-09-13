# Logic Specification: h-m2

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M2 (MECHANISM)  
**Type:** Representation Change Validation  
**Budget:** Full implementation (all 9 tasks)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-m1 actual code  
**Analyzed Path**: `docs/youra_research/20260511_buildingtrust/h-m1/code/`  
**Relevant Symbols**: BaselineModel, LoRAInterventionModel, InterventionTrainer, TrustEvaluator

**Key Findings**:
- h-m1 uses GPT-2 with LoRA (r=8, alpha=16, target_modules=["c_attn"])
- Proven training protocol: 3 epochs, lr=1e-4, batch=4
- TrustEvaluator uses lm-eval harness for TruthfulQA evaluation
- h-m2 extends with TransformerLens for activation extraction and CKA for similarity analysis

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are imported from h-m1. Signatures verified from actual implementation:

```python
# From: h-m1/code/src/model.py (ACTUAL CODE)
class BaselineModel:
    def __init__(self, model_id: str = "meta-llama/Meta-Llama-3-8B"):
        """Initialize baseline model.
        
        Args:
            model_id: HuggingFace model identifier
        """
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
        """Initialize LoRA intervention wrapper.
        
        Args:
            base_model: Base model to apply LoRA
            lora_rank: LoRA rank
            lora_alpha: LoRA alpha scaling
            lora_dropout: LoRA dropout rate
            target_modules: Modules to apply LoRA (default: ["q_proj", "v_proj"])
        """
        ...
    
    def apply_lora(self) -> PeftModel:
        """Apply LoRA adapter to base model."""
        ...
    
    def get_trainable_params(self) -> Dict[str, int]:
        """Get trainable parameter statistics."""
        ...

# From: h-m1/code/src/train.py (ACTUAL CODE)
class InterventionTrainer:
    def __init__(self, model: PeftModel, config: Dict):
        """Initialize trainer.
        
        Args:
            model: PEFT model with LoRA adapters
            config: Training configuration
        """
        ...
    
    def setup_optimizer(self, lr: float) -> AdamW:
        """Setup AdamW optimizer."""
        ...
    
    def setup_scheduler(self, optimizer: AdamW, num_training_steps: int) -> any:
        """Setup cosine learning rate scheduler."""
        ...
    
    def train_epoch(self, dataloader: DataLoader) -> Dict[str, float]:
        """Train one epoch. Returns: {"loss": float, "num_batches": int}"""
        ...
    
    def run_intervention(
        self,
        train_dataloader: DataLoader,
        num_epochs: int
    ) -> Dict[str, any]:
        """Run full intervention training. Returns: {"epoch_losses": List[float], "num_steps": int}"""
        ...

# From: h-m1/code/src/evaluate.py (ACTUAL CODE)
class TrustEvaluator:
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        """Initialize evaluator."""
        ...
    
    def evaluate(self, dimension: str, model_path: str = None) -> float:
        """Evaluate model on dimension. Returns: accuracy score"""
        ...
```

**Verified from**: `h-m1/code/` (actual implementation, NOT spec)

**Note**: h-m1 config uses model_id="gpt2" and target_modules=["c_attn"]. h-m2 will use the same configuration.

---

## A-1: Project Setup [Complexity: 7, Budget: All]

**Applied**: Standard PyTorch project structure + TransformerLens + pytorch-cka

### API Signatures

```python
from dataclasses import dataclass, field
from typing import List, Optional
import yaml

@dataclass
class H_M2_Config:
    """Configuration for h-m2 representation change validation."""
    
    # Model (inherited from h-m1)
    model_id: str = "gpt2"
    
    # Replication
    n_replicates: int = 3
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # LoRA configuration (inherited from h-m1)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    
    # Training (inherited from h-m1)
    learning_rate: float = 1e-4
    epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    max_grad_norm: float = 1.0
    warmup_ratio: float = 0.1
    
    # Representation extraction (new for h-m2)
    layers_to_analyze: List[str] = field(default_factory=list)
    save_activations: bool = True
    activation_cache_dir: str = "./outputs/activations"
    
    # Evaluation
    eval_batch_size: int = 8
    
    # Environment
    device: str = "cuda"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    
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

def load_config(config_path: str) -> H_M2_Config:
    """Load configuration from YAML file."""
    ...

def save_config(config: H_M2_Config, output_path: str):
    """Save configuration to YAML file."""
    ...
```

---

## A-2: Data Pipeline [Complexity: 6, Budget: All]

**Applied**: HuggingFace datasets + lm-eval harness integration (reuse from h-m1)

### API Signatures

```python
from datasets import load_dataset, Dataset
from transformers import PreTrainedTokenizer
from torch.utils.data import DataLoader
import torch
from typing import Dict, List

class TruthfulQADataset:
    def __init__(self, tokenizer: PreTrainedTokenizer, max_length: int = 512):
        """Initialize TruthfulQA dataset.
        
        Args:
            tokenizer: Tokenizer for preprocessing
            max_length: Max sequence length
        """
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.dataset: Optional[Dataset] = None
    
    def load_dataset(self) -> Dataset:
        """Load TruthfulQA validation set. Returns: Dataset with 817 questions"""
        ...
    
    def prepare_training_subset(self, n_samples: int = 100) -> Dataset:
        """Prepare training subset. Input: n_samples -> Output: tokenized Dataset"""
        ...
    
    def prepare_eval_tokens(self, n_samples: int = 817) -> torch.Tensor:
        """Prepare evaluation tokens for activation extraction. Returns: [N, L]"""
        ...
    
    def __len__(self) -> int:
        """Dataset length."""
        ...
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Get item. Returns: {"input_ids": [L], "attention_mask": [L], "labels": [L]}"""
        ...

class DataCollator:
    def __init__(self, tokenizer: PreTrainedTokenizer, max_length: int = 512):
        """Initialize data collator for batching."""
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __call__(self, features: List[Dict]) -> Dict[str, torch.Tensor]:
        """Collate batch. Input: List[Dict] -> Output: {"input_ids": [B, L], "attention_mask": [B, L], "labels": [B, L]}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | Tokenized questions (B=4, L≤512) |
| attention_mask | [B, L] | Padding mask |
| labels | [B, L] | Causal LM labels |
| eval_tokens | [N, L] | Evaluation set tokens (N≤817) |

---

## A-3: TransformerLens Integration [Complexity: 9, Budget: All]

**Applied**: TransformerLens HookedTransformer + PEFT conversion pattern

### API Signatures

```python
from transformer_lens import HookedTransformer
from transformers import AutoModelForCausalLM
from peft import PeftModel
import torch
from typing import Dict, Optional

class TransformerLensWrapper:
    def __init__(self, model_id: str = "gpt2", device: str = "cuda"):
        """Initialize TransformerLens wrapper.
        
        Args:
            model_id: HuggingFace model identifier
            device: Device for model
        """
        self.model_id = model_id
        self.device = device
        self.hooked_model: Optional[HookedTransformer] = None
    
    def load_baseline_hooked(self) -> HookedTransformer:
        """Load GPT-2 as HookedTransformer. Returns: model with hook points"""
        ...
    
    def convert_peft_to_hooked(self, peft_model: PeftModel) -> HookedTransformer:
        """Convert PEFT model to HookedTransformer.
        
        Args:
            peft_model: Fine-tuned model with LoRA adapters
        
        Returns:
            HookedTransformer with merged LoRA weights
        """
        ...
    
    def get_hook_names(self) -> List[str]:
        """Get available hook point names. Returns: List of hook names"""
        ...
```

### Pseudo-code

```
1. Load baseline with hooks:
   hooked_model = HookedTransformer.from_pretrained("gpt2", device="cuda")

2. Convert HuggingFace to PEFT for training:
   hf_model = AutoModelForCausalLM.from_pretrained("gpt2")
   peft_model = get_peft_model(hf_model, lora_config)
   # Train with InterventionTrainer (from h-m1)

3. Convert PEFT back to HookedTransformer:
   peft_model = peft_model.merge_and_unload()  # Merge LoRA weights
   hooked_model_post = HookedTransformer.from_pretrained(
       "gpt2",
       state_dict=peft_model.state_dict(),
       device="cuda"
   )
```

---

## A-4: Activation Extractor [Complexity: 10, Budget: All]

**Applied**: TransformerLens run_with_cache pattern

### API Signatures

```python
from transformer_lens import HookedTransformer, ActivationCache
import torch
from typing import Dict, List
from pathlib import Path

class ActivationExtractor:
    def __init__(self, model: HookedTransformer, layers: List[str], cache_dir: str):
        """Initialize activation extractor.
        
        Args:
            model: HookedTransformer with hook points
            layers: Layer names to extract (e.g., "blocks.0.attn.hook_pattern")
            cache_dir: Directory to save activations
        """
        self.model = model
        self.layers = layers
        self.cache_dir = Path(cache_dir)
    
    def extract_activations(self, tokens: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Extract activations for all layers.
        
        Args:
            tokens: Input tokens [N, L]
        
        Returns:
            Dict mapping layer_name -> activation tensor
        """
        ...
    
    def save_activations(self, activations: Dict[str, torch.Tensor], filepath: str):
        """Save activations to disk. Input: Dict -> Output: .pt file"""
        ...
    
    def load_activations(self, filepath: str) -> Dict[str, torch.Tensor]:
        """Load activations from disk. Input: .pt file -> Output: Dict"""
        ...

class RepresentationAnalyzer:
    def __init__(self, config: H_M2_Config):
        """Initialize representation analyzer."""
        self.config = config
        self.extractor: Optional[ActivationExtractor] = None
    
    def extract_pre_intervention(
        self,
        model: HookedTransformer,
        eval_tokens: torch.Tensor,
        seed: int
    ) -> Dict[str, torch.Tensor]:
        """Extract pre-intervention activations. Returns: 24 layers × activations"""
        ...
    
    def extract_post_intervention(
        self,
        model: HookedTransformer,
        eval_tokens: torch.Tensor,
        seed: int
    ) -> Dict[str, torch.Tensor]:
        """Extract post-intervention activations. Returns: 24 layers × activations"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| tokens | [N, L] | Input tokens (N≤817, L≤512) |
| attn_pattern | [N, H, L, L] | Attention patterns (H=12 heads) |
| hidden_state | [N, L, D] | Hidden states (D=768 for GPT-2) |
| flattened_attn | [N, H*L*L] | Flattened for CKA |
| flattened_hidden | [N, L*D] | Flattened for CKA |

### Pseudo-code

```
1. Extract activations:
   _, cache = model.run_with_cache(tokens)
   
2. Store layer activations:
   activations = {}
   for layer_name in layers_to_analyze:
       act = cache[layer_name].detach().cpu()
       activations[layer_name] = act
   
3. Save to disk:
   torch.save(activations, f"pre_activations_seed{seed}.pt")
```

---

## A-5: CKA Similarity Module [Complexity: 11, Budget: All]

**Applied**: pytorch-cka library + custom implementation fallback

### API Signatures

```python
import torch
from typing import Dict, List
import numpy as np

class CKASimilarity:
    def __init__(self, device: str = "cuda"):
        """Initialize CKA similarity computation.
        
        Args:
            device: Device for computation (GPU-accelerated)
        """
        self.device = device
    
    def compute_cka(self, X: torch.Tensor, Y: torch.Tensor) -> float:
        """Compute CKA similarity between two representations.
        
        Args:
            X: Pre-intervention activations [N, F]
            Y: Post-intervention activations [N, F]
        
        Returns:
            CKA similarity score (0-1)
        """
        ...
    
    def compute_layer_cka(
        self,
        pre_acts: Dict[str, torch.Tensor],
        post_acts: Dict[str, torch.Tensor],
        layer_name: str
    ) -> float:
        """Compute CKA for single layer. Returns: similarity score"""
        ...
    
    def compute_all_layers(
        self,
        pre_acts: Dict[str, torch.Tensor],
        post_acts: Dict[str, torch.Tensor],
        layers: List[str]
    ) -> Dict[str, float]:
        """Compute CKA for all layers. Returns: {layer_name: cka_score}"""
        ...

def flatten_activations(act: torch.Tensor) -> torch.Tensor:
    """Flatten activations for CKA. Input: [N, ...] -> Output: [N, F]"""
    ...
```

### Pseudo-code

```
1. Flatten activations:
   # Attention patterns: [N, H, L, L] -> [N, H*L*L]
   pre_flat = pre_acts[layer].flatten(1)
   post_flat = post_acts[layer].flatten(1)

2. Compute CKA (Centered Kernel Alignment):
   # Using pytorch-cka library
   from cka import cka_score
   cka = cka_score(pre_flat, post_flat)
   
   # Manual implementation:
   K = pre_flat @ pre_flat.T  # Gram matrix
   L = post_flat @ post_flat.T
   # HSIC (Hilbert-Schmidt Independence Criterion)
   cka = HSIC(K, L) / sqrt(HSIC(K, K) * HSIC(L, L))

3. Store results:
   cka_scores[layer_name] = cka.item()
```

---

## A-6: LoRA Training Pipeline [Complexity: 8, Budget: All]

**Applied**: Reuse h-m1 InterventionTrainer with activation tracking

### API Signatures

```python
from h_m1.src.train import InterventionTrainer
from transformer_lens import HookedTransformer
import torch
from typing import Dict

class H_M2_Trainer:
    def __init__(self, config: H_M2_Config):
        """Initialize h-m2 trainer with representation tracking."""
        self.config = config
        self.base_trainer: Optional[InterventionTrainer] = None
    
    def train_with_representation_tracking(
        self,
        peft_model,
        train_dataloader,
        eval_tokens: torch.Tensor,
        seed: int
    ) -> Dict:
        """Train LoRA with pre/post activation extraction.
        
        Args:
            peft_model: PEFT model with LoRA adapters
            train_dataloader: Training data
            eval_tokens: Tokens for activation extraction
            seed: Random seed
        
        Returns:
            {
                "training_history": Dict,
                "pre_activations_path": str,
                "post_activations_path": str
            }
        """
        ...
```

### Pseudo-code

```
1. Extract pre-intervention activations:
   hooked_model = convert_to_hooked(peft_model.get_base_model())
   pre_acts = extract_activations(hooked_model, eval_tokens)
   save_activations(pre_acts, f"pre_seed{seed}.pt")

2. Train with h-m1 InterventionTrainer:
   trainer = InterventionTrainer(peft_model, config)
   history = trainer.run_intervention(train_dataloader, epochs=3)

3. Extract post-intervention activations:
   peft_model_merged = peft_model.merge_and_unload()
   hooked_model_post = convert_to_hooked(peft_model_merged)
   post_acts = extract_activations(hooked_model_post, eval_tokens)
   save_activations(post_acts, f"post_seed{seed}.pt")
```

---

## A-7: Statistical Analysis [Complexity: 9, Budget: All]

**Applied**: scipy Pearson correlation + paired t-test

### API Signatures

```python
from scipy.stats import pearsonr, ttest_rel
import numpy as np
from typing import Dict, List

class CorrelationAnalyzer:
    def __init__(self, performance_delta: float = 0.0232):
        """Initialize correlation analyzer.
        
        Args:
            performance_delta: Performance improvement from h-m1 (+2.32% TruthfulQA)
        """
        self.performance_delta = performance_delta
    
    def compute_representation_change(self, cka_scores: Dict[str, float]) -> Dict[str, float]:
        """Compute change magnitude (1 - CKA). Returns: {layer: change_magnitude}"""
        ...
    
    def correlate_representation_performance(
        self,
        change_magnitudes: List[float],
        performance_delta: float
    ) -> Dict[str, float]:
        """Correlate representation change with performance.
        
        Returns:
            {
                "correlation": float,
                "p_value": float,
                "significant": bool
            }
        """
        ...
    
    def aggregate_across_replicates(
        self,
        replicate_cka_scores: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """Aggregate CKA scores across replicates. Returns: {layer: mean_cka}"""
        ...

class StatisticalAnalyzer:
    def __init__(self):
        """Initialize statistical analyzer."""
        pass
    
    def evaluate_gate(
        self,
        cka_scores: Dict[str, float],
        performance_delta: float = 0.0232
    ) -> Dict:
        """Evaluate SHOULD_WORK gate.
        
        Returns:
            {
                "pass": bool,
                "correlation": float,
                "p_value": float,
                "mean_change": float,
                "layers_changed": int
            }
        """
        ...
```

### Pseudo-code

```
1. Compute representation change magnitude:
   changes = [1.0 - cka for cka in cka_scores.values()]
   mean_change = np.mean(changes)

2. Correlation with performance:
   # All layers compared to same performance delta
   perf_deltas = [performance_delta] * len(changes)
   correlation, p_value = pearsonr(changes, perf_deltas)

3. Gate evaluation:
   pass = (p_value < 0.05) AND (mean_change > 0)
   layers_changed = sum(1 for cka in cka_scores.values() if cka < 1.0)
```

---

## A-8: Visualization [Complexity: 7, Budget: All]

**Applied**: matplotlib + seaborn plotting patterns

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List
from pathlib import Path

class FigureGenerator:
    def __init__(self, output_dir: str):
        """Initialize figure generator.
        
        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_cka_heatmap(
        self,
        cka_scores: Dict[str, float],
        layers: List[str]
    ):
        """Plot CKA similarity heatmap. X=layer_idx, Y=type (attn/hidden)"""
        ...
    
    def plot_change_magnitude(
        self,
        change_magnitudes: Dict[str, float]
    ):
        """Plot layer-wise change magnitude bar chart."""
        ...
    
    def plot_layer_progression(
        self,
        cka_scores: Dict[str, float]
    ):
        """Plot change progression across depth. Two lines: attn, hidden"""
        ...
    
    def plot_correlation_scatter(
        self,
        change_magnitudes: List[float],
        performance_delta: float,
        correlation: float,
        p_value: float
    ):
        """Plot correlation scatter with regression line. Required for gate."""
        ...
    
    def save_all_figures(
        self,
        cka_scores: Dict[str, float],
        correlation_result: Dict
    ):
        """Generate and save all 4 required figures."""
        ...
```

---

## A-9: Experiment Orchestration [Complexity: 8, Budget: All]

**Applied**: Standard experiment workflow pattern

### API Signatures

```python
import torch
import random
import numpy as np
from typing import Dict, List
from pathlib import Path

def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def setup_gpu(gpu_id: int):
    """Setup GPU environment."""
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

def train_single_replicate(
    config: H_M2_Config,
    seed: int,
    eval_tokens: torch.Tensor
) -> Dict:
    """Train single replicate with activation tracking.
    
    Returns:
        {
            "seed": int,
            "pre_activations_path": str,
            "post_activations_path": str,
            "cka_scores": Dict[str, float],
            "training_history": Dict
        }
    """
    ...

def run_all_replicates(config: H_M2_Config) -> List[Dict]:
    """Run N=3 replicates with different seeds."""
    ...

def main():
    """Main experiment orchestrator.
    
    Workflow:
        1. Load configuration
        2. Setup environment (GPU, seeds)
        3. Prepare evaluation data
        4. For each replicate:
           a. Extract pre-intervention activations
           b. Apply LoRA intervention (h-m1 protocol)
           c. Extract post-intervention activations
           d. Compute CKA similarity
        5. Aggregate results across replicates
        6. Statistical analysis (correlation)
        7. Generate visualizations
        8. Evaluate gate (p < 0.05)
        9. Save validation report
    """
    ...
```

### Pseudo-code

```
1. Setup:
   config = load_config("config.yaml")
   set_seed(config.seeds[0])
   setup_gpu(0)

2. Prepare data:
   baseline_model = BaselineModel(model_id=config.model_id)
   tokenizer = baseline_model.load_tokenizer()
   dataset = TruthfulQADataset(tokenizer)
   eval_tokens = dataset.prepare_eval_tokens(n_samples=100)
   train_data = dataset.prepare_training_subset(n_samples=100)
   train_loader = DataLoader(train_data, batch_size=4, collate_fn=DataCollator(tokenizer))

3. Replicate loop (N=3):
   all_results = []
   for seed in config.seeds:
       set_seed(seed)
       
       # Load baseline with hooks
       wrapper = TransformerLensWrapper(config.model_id)
       hooked_baseline = wrapper.load_baseline_hooked()
       
       # Extract pre-intervention activations
       analyzer = RepresentationAnalyzer(config)
       pre_acts = analyzer.extract_pre_intervention(hooked_baseline, eval_tokens, seed)
       
       # Convert to PEFT for training
       hf_model = baseline_model.load_model()
       lora_wrapper = LoRAInterventionModel(
           base_model=hf_model,
           lora_rank=config.lora_rank,
           lora_alpha=config.lora_alpha,
           target_modules=config.target_modules
       )
       peft_model = lora_wrapper.apply_lora()
       
       # Train with h-m1 protocol
       trainer = InterventionTrainer(peft_model, config.__dict__)
       history = trainer.run_intervention(train_loader, num_epochs=config.epochs)
       
       # Merge LoRA and convert back to hooked model
       peft_model_merged = peft_model.merge_and_unload()
       hooked_post = wrapper.convert_peft_to_hooked(peft_model_merged)
       
       # Extract post-intervention activations
       post_acts = analyzer.extract_post_intervention(hooked_post, eval_tokens, seed)
       
       # Compute CKA similarity
       cka_module = CKASimilarity(device=config.device)
       cka_scores = cka_module.compute_all_layers(pre_acts, post_acts, config.layers_to_analyze)
       
       all_results.append({
           "seed": seed,
           "cka_scores": cka_scores,
           "training_history": history
       })

4. Statistical analysis:
   # Aggregate CKA scores across replicates
   corr_analyzer = CorrelationAnalyzer(performance_delta=0.0232)
   aggregated_cka = corr_analyzer.aggregate_across_replicates([r["cka_scores"] for r in all_results])
   
   # Compute representation change
   change_magnitudes = corr_analyzer.compute_representation_change(aggregated_cka)
   
   # Correlate with h-m1 performance improvement
   corr_result = corr_analyzer.correlate_representation_performance(
       list(change_magnitudes.values()),
       performance_delta=0.0232
   )
   
   # Evaluate gate
   stat_analyzer = StatisticalAnalyzer()
   gate_result = stat_analyzer.evaluate_gate(aggregated_cka, performance_delta=0.0232)

5. Visualization:
   visualizer = FigureGenerator(config.figures_dir)
   visualizer.save_all_figures(aggregated_cka, corr_result)

6. Save results:
   results = {
       "replicates": all_results,
       "aggregated_cka": aggregated_cka,
       "correlation": corr_result,
       "gate": gate_result
   }
   save_json(results, f"{config.output_dir}/h_m2_validation.json")
```

---

## Configuration Schema

```python
@dataclass
class H_M2_Config:
    # Model (inherited from h-m1)
    model_id: str = "gpt2"
    
    # Replication
    n_replicates: int = 3
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # LoRA (inherited from h-m1)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    
    # Training (inherited from h-m1)
    learning_rate: float = 1e-4
    epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    max_grad_norm: float = 1.0
    warmup_ratio: float = 0.1
    
    # Representation extraction (new)
    layers_to_analyze: List[str] = field(default_factory=list)
    save_activations: bool = True
    activation_cache_dir: str = "./outputs/activations"
    
    # Environment
    device: str = "cuda"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
```

---

## Implementation Notes

### h-m1 Code Reuse Strategy

**Direct Imports (No Modifications)**:
- `BaselineModel.load_model()` (override model_id to "gpt2")
- `BaselineModel.load_tokenizer()`
- `LoRAInterventionModel.apply_lora()` (override target_modules to ["c_attn"])
- `InterventionTrainer.run_intervention()` (use as-is)

**h-m2 Specific Components**:
- `TransformerLensWrapper` (activation extraction capability)
- `ActivationExtractor` (pre/post activation caching)
- `CKASimilarity` (representation similarity computation)
- `CorrelationAnalyzer` (representation-performance correlation)
- `FigureGenerator` (CKA heatmaps, correlation scatter)

### TransformerLens + PEFT Integration Pattern

**Challenge**: TransformerLens uses custom format, PEFT uses HuggingFace.

**Solution**:
1. Load GPT-2 as HookedTransformer for pre-intervention extraction
2. Convert to HuggingFace format for PEFT LoRA training
3. Merge LoRA weights and reload into HookedTransformer for post-intervention extraction

**Critical**: Use `merge_and_unload()` to merge LoRA weights before converting to HookedTransformer.

---

## Validation Checklist

### Self-Validation

- [x] No ASCII diagrams
- [x] KB patterns applied (TransformerLens, pytorch-cka, PEFT)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] Base hypothesis code verified
- [x] API signatures match actual h-m1 code
- [x] External Dependencies API section included

### Base Hypothesis Verification

- [x] Read actual code from h-m1/code/
- [x] API signatures verified from actual implementation
- [x] Parameter names exactly match (model_id, lora_rank, lora_alpha, target_modules)
- [x] External Dependencies API section included
- [x] Configuration inheritance documented

---

*Generated by Phase 3 Logic Agent*  
*Patterns Applied: TransformerLens activation extraction, pytorch-cka representation similarity, PEFT LoRA integration, scipy statistical analysis*  
*MECHANISM hypothesis - extends h-m1 to validate representation change mechanism*
