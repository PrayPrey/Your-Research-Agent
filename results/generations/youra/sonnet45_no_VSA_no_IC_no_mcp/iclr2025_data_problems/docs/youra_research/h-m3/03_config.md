# Configuration: h-m3 Embedding-Stage Mismatch

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Tier:** PoC  
**Generated:** 2026-08-24

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New experiment - no base hypothesis  
**Config Files Found:** None (referencing h-m1, h-m2 patterns)  
**Pattern Used:** YAML (follows PRD Section 2.3)

---

## Configuration Schema

Single YAML config file for all experiment parameters. PoC uses fixed defaults from Llama-2 fine-tuning literature.

### experiment_config.yaml

```yaml
# Global experiment configuration
experiment:
  hypothesis_id: h-m3
  name: embedding_stage_mismatch
  tier: PoC
  seed: 42

# Dataset configuration
dataset:
  name: databricks/databricks-dolly-15k
  split: train
  cache_dir: data/dolly_15k
  expected_samples: 15015
  subset_sizes: [2000, 5000, 10000]

# Embedding models (early/mid/late stages)
embedding_models:
  early:
    model_id: sentence-transformers/all-MiniLM-L6-v2
    dimension: 384
    task_instruction: null
  mid:
    model_id: sentence-transformers/all-mpnet-base-v2
    dimension: 768
    task_instruction: null
  late:
    model_id: hkunlp/instructor-large
    dimension: 768
    task_instruction: "Represent the instruction-response pair for diversity-based selection:"

# k-center greedy selection
subset_selection:
  algorithm: k_center_greedy
  distance_metric: cosine
  initialization: random
  seed: 42

# Base model for fine-tuning
base_model:
  model_id: meta-llama/Llama-2-7b-hf
  cache_dir: models/llama2_base
  max_seq_length: 512

# Training hyperparameters (standard Llama-2 instruction tuning)
training:
  num_train_epochs: 3
  per_device_train_batch_size: 8
  gradient_accumulation_steps: 8
  learning_rate: 2.0e-5
  warmup_steps: 100
  lr_scheduler_type: cosine
  optimizer: adamw
  adam_beta1: 0.9
  adam_beta2: 0.999
  adam_epsilon: 1.0e-8
  weight_decay: 0.01
  max_grad_norm: 1.0
  bf16: true
  fp16: false
  seed: 42
  logging_steps: 10
  save_strategy: epoch
  save_total_limit: 1
  output_dir: models/

# Evaluation configuration
evaluation:
  framework: lm-evaluation-harness
  tasks: [mmlu, hellaswag]
  num_fewshot:
    mmlu: 5
    hellaswag: 10
  batch_size: 8
  device: cuda:0

# Output paths
paths:
  data_dir: data/
  embeddings_dir: data/embeddings/
  subsets_dir: data/subsets/
  models_dir: models/
  results_dir: results/
  analysis_dir: results/analysis/
  figures_dir: results/analysis/figures/

# Success criteria (SHOULD_WORK gate)
success_criteria:
  stage_mismatch_penalty_threshold: 0.02  # 2% at k=5000
  speed_advantage_threshold: 3.0  # 3x faster
  quality_bound_threshold: 0.01  # 1% at k=10000
```

---

## Validation Rules

**Dataset constraints:**
- `len(subset_sizes) > 0`
- `all(k <= expected_samples for k in subset_sizes)`
- `expected_samples == 15015` (Dolly-15k)

**Training constraints:**
- `learning_rate > 0`
- `num_train_epochs > 0`
- `per_device_train_batch_size > 0`
- `gradient_accumulation_steps > 0`
- `effective_batch_size = per_device_train_batch_size * gradient_accumulation_steps == 64`

**Embedding constraints:**
- `all(stage in ["early", "mid", "late"] for stage in embedding_models.keys())`
- `embedding_models["late"]["task_instruction"] is not None`

**Evaluation constraints:**
- `all(task in ["mmlu", "hellaswag"] for task in evaluation["tasks"])`
- `all(num_fewshot[task] >= 0 for task in tasks)`

**Success criteria constraints:**
- `0.0 < stage_mismatch_penalty_threshold < 1.0`
- `speed_advantage_threshold >= 1.0`
- `0.0 < quality_bound_threshold < 1.0`

---

## Environment Variables

**Required:**
- `HF_TOKEN` - Hugging Face API token (Llama-2 access)
- `CUDA_VISIBLE_DEVICES` - GPU assignment (default: `0`)

**Optional:**
- `HF_HOME` - Hugging Face cache directory override (default: `~/.cache/huggingface`)
- `TRANSFORMERS_CACHE` - Transformers model cache override

---

## Usage Example

```python
import yaml
from pathlib import Path

# Load config
with open("config/experiment_config.yaml") as f:
    config = yaml.safe_load(f)

# Access parameters
dataset_name = config["dataset"]["name"]
subset_sizes = config["dataset"]["subset_sizes"]
embedding_models = config["embedding_models"]
training_args = config["training"]

# Validation
assert all(k <= config["dataset"]["expected_samples"] for k in subset_sizes)
assert config["training"]["per_device_train_batch_size"] * config["training"]["gradient_accumulation_steps"] == 64
```

---

## Config Files Structure

```
config/
└── experiment_config.yaml      # Single config file (all parameters)

data/
├── dolly_15k/                 # Cached dataset
├── embeddings/                # .npy embedding matrices
│   ├── early_embeddings.npy
│   ├── mid_embeddings.npy
│   └── late_embeddings.npy
└── subsets/                   # Selected indices
    ├── early_k2000_indices.npy
    ├── early_k5000_indices.npy
    ├── early_k10000_indices.npy
    ├── mid_k2000_indices.npy
    ├── mid_k5000_indices.npy
    ├── mid_k10000_indices.npy
    ├── late_k2000_indices.npy
    ├── late_k5000_indices.npy
    └── late_k10000_indices.npy

models/
├── baseline/                  # Full dataset (15,015 samples)
├── early_k2000/               # 9 subset conditions
├── early_k5000/
├── early_k10000/
├── mid_k2000/
├── mid_k5000/
├── mid_k10000/
├── late_k2000/
├── late_k5000/
└── late_k10000/

results/
├── baseline.json              # lm-eval outputs
├── early_k2000.json
├── early_k5000.json
├── early_k10000.json
├── mid_k2000.json
├── mid_k5000.json
├── mid_k10000.json
├── late_k2000.json
├── late_k5000.json
├── late_k10000.json
└── analysis/
    ├── metrics_table.csv
    ├── pareto_frontier.png
    └── convergence_curves.png
```

---

## Reproducibility Notes

**Fixed seeds:**
- `experiment.seed: 42` - Global random seed
- `subset_selection.seed: 42` - k-center greedy initialization
- `training.seed: 42` - Model initialization, data shuffling

**Version pinning (requirements.txt):**
```
torch==2.1.0
transformers==4.36.0
sentence-transformers==2.3.0
datasets==2.16.0
lm-evaluation-harness==0.4.1
numpy==1.24.0
scipy==1.11.0
pyyaml==6.0.1
```

**Deterministic training:**
- `torch.manual_seed(42)`
- `torch.cuda.manual_seed_all(42)`
- `torch.backends.cudnn.deterministic = True`
- `torch.backends.cudnn.benchmark = False`

---

**END OF CONFIGURATION**
