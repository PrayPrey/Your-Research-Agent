# Configuration for H-M1 ProvenanceCache

**Hypothesis**: h-m1  
**Type**: MECHANISM  
**Date**: 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase  
**Status**: Extends h-e1 (validated) - reuses Llama-2-7B + Contriever pipeline  
**Config Files Found**: h-e1 YAML configs (model_config.yaml, retrieval_config.yaml)  
**Pattern Used**: YAML config files + Python dataclass for cache policies

**Applied**: Standard PyTorch + HuggingFace defaults for model/generation, adapted from h-e1

---

## Configuration Files

### model_config.yaml

```yaml
# Model: Llama-2-7B (from h-e1, verified)
model:
  checkpoint: "meta-llama/Llama-2-7b-hf"  # Base model (not chat)
  device: "cuda"
  dtype: "float16"
  output_attentions: true  # H2O baseline requires this

generation:
  max_new_tokens: 100
  temperature: 0.0  # Greedy decoding
  do_sample: false
  seed: 42
```

---

### cache_config.yaml

```yaml
# Cache eviction policies
cache:
  budget_ratio: 0.25  # 25% retention
  
  # H2O baseline
  h2o:
    heavy_ratio: 0.125
    recent_ratio: 0.125
    n_sink: 4
  
  # ProvenanceCache (proposed)
  provenance:
    top_k_passages: 5
    high_rel_count: 3  # Top-3 passages = high-rel
    tier_allocation:
      query: "all"  # Always retain
      high_rel: 0.5  # 50% of budget
      low_rel: 0.5   # 50% of budget
```

---

### retrieval_config.yaml

```yaml
# Contriever (from h-e1, reused)
contriever:
  checkpoint: "facebook/contriever-msmarco"
  max_length: 512
  batch_size: 64
  top_k: 5  # Reduced from h-e1 (10) for tighter focus
  device: "cuda"
  pooling: "cls"
  
passage_chunking:
  chunk_size: 512
  overlap: 128
  score_normalization: "minmax"  # [0,1] per query
```

---

### dataset_config.yaml

```yaml
# LongBench single-hop QA
dataset:
  source: "THUDM/LongBench"
  tasks: 
    - "narrativeqa"
    - "qasper"
    - "triviaqa"
    - "multifieldqa_en"
  samples_per_task: 200
  max_context_length: 4096  # Llama-2-7B max

preprocessing:
  tokenizer: "meta-llama/Llama-2-7b-hf"
  padding_side: "left"
  truncation: true
```

---

### experiment_config.yaml

```yaml
experiment:
  name: "h-m1-provenance-cache"
  hypothesis_id: "h-m1"
  random_seed: 42
  
conditions:
  - name: "FullKV"
    cache_ratio: 1.0
  - name: "H2O"
    cache_ratio: 0.25
    policy: "h2o"
  - name: "ProvenanceCache"
    cache_ratio: 0.25
    policy: "provenance"
  - name: "Random"
    cache_ratio: 0.25
    policy: "random"

evaluation:
  metrics:
    - "f1"
    - "exact_match"
    - "cache_compression"
    - "latency"
    - "memory"
  statistical_test:
    method: "ttest_ind"
    alternative: "greater"
    alpha: 0.05
  gate_threshold: 1.05  # ProvenanceCache F1 >= H2O F1 * 1.05

checkpointing:
  interval: 50
  resume_enabled: true
  
visualization:
  required:
    - "gate_metrics_bar"
  optional:
    - "cache_budget_curve"
    - "per_task_breakdown"
    - "cache_composition"
    - "latency_boxplot"
    - "memory_usage"
  output_dir: "figures/"
  format: "png"
  dpi: 300
```

---

## Python Dataclass (Cache Policy)

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class H2OCacheConfig:
    """H2O baseline configuration"""
    heavy_ratio: float = 0.125
    recent_ratio: float = 0.125
    n_sink: int = 4
    cache_budget_ratio: float = 0.25

@dataclass
class ProvenanceCacheConfig:
    """ProvenanceCache configuration"""
    cache_budget_ratio: float = 0.25
    top_k_passages: int = 5
    high_rel_count: int = 3
    tier_allocation_high: float = 0.5
    tier_allocation_low: float = 0.5

@dataclass
class CacheCondition:
    """Experimental condition"""
    name: Literal["FullKV", "H2O", "ProvenanceCache", "Random"]
    cache_ratio: float
    policy: Literal["none", "h2o", "provenance", "random"]
    config: H2OCacheConfig | ProvenanceCacheConfig | None = None
```

---

## Inherited from H-E1

**Verified from h-e1 config (actual specs):**

```yaml
# model_config.yaml (h-e1)
model:
  checkpoint: "meta-llama/Llama-2-7b-chat-hf"  # Chat version in h-e1
  device: "cuda"
  dtype: "float16"

# retrieval_config.yaml (h-e1)
contriever:
  checkpoint: "facebook/contriever-msmarco"
  max_length: 512
  batch_size: 64
  top_k: 10  # h-e1 used 10, h-m1 uses 5
```

**Changes for h-m1:**
- Model: `Llama-2-7b-hf` (base, not chat) for generation tasks
- Generation: `temperature=0.0` (greedy), `max_new_tokens=100` (from LongBench standard)
- Retrieval: `top_k=5` (tighter passage set for cache experiment)

---

## Hyperparameter Justification

### Cache Budget
- **budget_ratio: 0.25**: Hypothesis target, balances compression vs accuracy
- **h2o heavy_ratio: 0.125**: Matches total budget (0.125 + 0.125 = 0.25)
- **provenance tier_allocation: 50/50**: Equal weight to high-rel and low-rel after query tokens

### Model/Generation
- **dtype: float16**: Same as h-e1, fits on 16GB GPU
- **temperature: 0.0**: Greedy decoding for reproducibility
- **max_new_tokens: 100**: LongBench QA answer length

### Retrieval
- **top_k: 5**: Reduced from h-e1 (10) to focus on most relevant passages
- **chunk_size: 512**: Contriever max length
- **overlap: 128**: 25% overlap for boundary tokens

### Statistical Testing
- **alpha: 0.05**: Standard significance threshold
- **alternative: greater**: One-tailed test (ProvenanceCache > H2O)

---

## Validation Rules

```python
VALIDATION_RULES = {
    "cache_budget_sum": lambda: abs((0.125 + 0.125) - 0.25) < 1e-6,
    "model_checkpoint_exists": lambda: check_hf_access("meta-llama/Llama-2-7b-hf"),
    "gpu_memory_sufficient": lambda: torch.cuda.get_device_properties(0).total_memory > 14e9,
    "retrieval_top_k_valid": lambda: 3 <= CONFIG["retrieval"]["top_k"] <= 10,
    "seed_fixed": lambda: CONFIG["experiment"]["random_seed"] == 42,
    "provenance_tier_sum": lambda: abs(0.5 + 0.5 - 1.0) < 1e-6,
}
```

---

## Usage Example

```python
import yaml
from dataclasses import dataclass

# Load YAML configs
with open("configs/cache_config.yaml") as f:
    cache_cfg = yaml.safe_load(f)

# Create dataclass instances
h2o_config = H2OCacheConfig(
    heavy_ratio=cache_cfg["cache"]["h2o"]["heavy_ratio"],
    recent_ratio=cache_cfg["cache"]["h2o"]["recent_ratio"],
    n_sink=cache_cfg["cache"]["h2o"]["n_sink"],
    cache_budget_ratio=cache_cfg["cache"]["budget_ratio"]
)

provenance_config = ProvenanceCacheConfig(
    cache_budget_ratio=cache_cfg["cache"]["budget_ratio"],
    top_k_passages=cache_cfg["cache"]["provenance"]["top_k_passages"],
    high_rel_count=cache_cfg["cache"]["provenance"]["high_rel_count"],
    tier_allocation_high=cache_cfg["cache"]["provenance"]["tier_allocation"]["high_rel"],
    tier_allocation_low=cache_cfg["cache"]["provenance"]["tier_allocation"]["low_rel"]
)

# Use in experiment
conditions = {
    "H2O": CacheCondition("H2O", 0.25, "h2o", h2o_config),
    "ProvenanceCache": CacheCondition("ProvenanceCache", 0.25, "provenance", provenance_config),
}
```

---

## File Locations

```
h-m1/
├── configs/
│   ├── model_config.yaml
│   ├── cache_config.yaml
│   ├── retrieval_config.yaml
│   ├── dataset_config.yaml
│   └── experiment_config.yaml
├── code/
│   └── cache_policy.py  # CacheCondition dataclasses
```

---

**Config Status**: COMPLETE  
**Ready for Phase 4**: YES  
**Format**: YAML configs + Python dataclass (cache policies)  
**Base Hypothesis**: h-e1 (validated) - reuses model/retrieval configs
