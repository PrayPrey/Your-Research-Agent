# Configuration: h-m2 Transfer Stability Categorization

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Generated:** 2026-08-24

---

## Codebase Analysis

**Project Type:** green-field  
**Status:** New configuration design (PoC)  
**Config Files Found:** None - new config  
**Pattern Used:** YAML (data config) + Python dict (training config)

---

## 1. C4 Thresholds (Extracted from Documentation)

**File:** `config/c4_thresholds.yaml`

```yaml
# Filtering thresholds from C4 dataset documentation
# Source: https://huggingface.co/datasets/c4

deduplication:
  n_gram_size: 13
  similarity_threshold: 0.8

perplexity:
  cutoff: 1000
  reference_model: "gpt2"

domain_mixing:
  web: 0.6
  news: 0.2
  forums: 0.2
```

**Notes:**
- `n_gram_size: 13` - Standard MinHash LSH parameter
- `similarity_threshold: 0.8` - Jaccard similarity for near-duplicate detection
- `perplexity cutoff: 1000` - Removes outliers (GPT-2 reference)

---

## 2. Training Configuration (Fixed Across All Conditions)

**File:** `config/train_config.yaml`

```yaml
# Fixed training configuration for all 5 dataset conditions
# Ensures curation is the only variable

model:
  name: "meta-llama/Llama-2-7b-hf"
  max_seq_length: 512

training:
  epochs: 3
  batch_size: 8
  gradient_accumulation_steps: 8  # Effective batch = 64
  learning_rate: 2.0e-5
  warmup_steps: 100
  lr_scheduler: "cosine"
  optimizer: "adamw"
  adam_beta1: 0.9
  adam_beta2: 0.999
  adam_epsilon: 1.0e-8
  weight_decay: 0.01
  max_grad_norm: 1.0
  seed: 42
  fp16: true
  logging_steps: 50
  save_strategy: "epoch"
  save_total_limit: 1
  output_dir: "models/{condition}/"
```

**Python dict equivalent** (for direct import):

```python
TRAIN_CONFIG = {
    "model": {
        "name": "meta-llama/Llama-2-7b-hf",
        "max_seq_length": 512,
    },
    "training": {
        "epochs": 3,
        "batch_size": 8,
        "gradient_accumulation_steps": 8,
        "learning_rate": 2e-5,
        "warmup_steps": 100,
        "lr_scheduler": "cosine",
        "optimizer": "adamw",
        "adam_beta1": 0.9,
        "adam_beta2": 0.999,
        "adam_epsilon": 1e-8,
        "weight_decay": 0.01,
        "max_grad_norm": 1.0,
        "seed": 42,
        "fp16": True,
        "logging_steps": 50,
        "save_strategy": "epoch",
        "save_total_limit": 1,
        "output_dir": "models/{condition}/",
    }
}
```

---

## 3. Filter Tuning Configuration (Grid Search)

**File:** `config/filter_tuning.yaml`

```yaml
# Hyperparameter grid for stage-tuning filters
# Used only for Tuned-Indep and Tuned-Dep conditions

objective_independent:
  deduplication:
    similarity_threshold: [0.7, 0.8, 0.9, 0.95]
  perplexity:
    cutoff: [500, 1000, 1500, 2000]
  validation_metric: "val_perplexity"
  selection_strategy: "best_val_performance"

objective_dependent:
  domain_mixing:
    web_ratio: [0.5, 0.6, 0.7]  # If multi-source available
  quality_filters:
    min_prompt_diversity: [0.3, 0.5, 0.7]
    min_response_length: [20, 50, 100]
  validation_metric: "instruction_quality_score"
  selection_strategy: "best_val_performance"

validation_split: 0.1  # 10% of Dolly train set
```

---

## 4. Evaluation Configuration

**File:** `config/eval_config.yaml`

```yaml
# lm-evaluation-harness configuration
# Benchmarks: MMLU, HellaSwag

tasks:
  - mmlu
  - hellaswag

num_fewshot: 5
batch_size: 16
device: "cuda"
output_dir: "results/"
log_samples: false
```

**Python dict equivalent**:

```python
EVAL_CONFIG = {
    "tasks": ["mmlu", "hellaswag"],
    "num_fewshot": 5,
    "batch_size": 16,
    "device": "cuda",
    "output_dir": "results/",
    "log_samples": False,
}
```

---

## 5. Statistical Analysis Configuration

**File:** `config/statistical_config.yaml`

```yaml
# Bootstrap and hypothesis testing parameters

bootstrap:
  n_resamples: 10000
  confidence_level: 0.95
  random_seed: 42

tests:
  - name: "welch_t_test"
    alpha: 0.05
  - name: "cohens_d"
    interpretation:
      small: 0.2
      medium: 0.5
      large: 0.8
```

---

## 6. Gate Criteria Configuration

**File:** `config/gate_criteria.yaml`

```yaml
# SHOULD_WORK gate pass/fail thresholds

should_work:
  primary:
    objective_independent_delta_max: 1.0  # ≤1% transfer delta
    objective_dependent_delta_min: 5.0    # >5% transfer delta
  
  secondary:
    ci_overlap_allowed: false  # 95% CIs must not overlap
    min_curation_benefit: 2.0  # Tuned > Baseline by ≥2%
  
  statistical:
    min_significance: 0.05  # p < 0.05
    min_effect_size: 0.8    # Cohen's d > 0.8 (P2 criterion)
```

---

## 7. Dataset Conditions Table

| Condition | Dedup | Perplexity | Domain Mix | Task Filter | Config File |
|-----------|-------|------------|------------|-------------|-------------|
| Baseline | No | No | No | No | None |
| Transferred-Indep | C4 (0.8, 13-gram) | C4 (1000) | No | No | `c4_thresholds.yaml` |
| Tuned-Indep | Optimized | Optimized | No | No | `filter_tuning.yaml` (indep) |
| Transferred-Dep | No | No | C4 ratios | C4 filters | `c4_thresholds.yaml` |
| Tuned-Dep | No | No | Optimized | Optimized | `filter_tuning.yaml` (dep) |

**Expected sample counts** (Dolly-15k baseline):
- Baseline: 13,513 train samples (90% of 15,015)
- Transferred-Indep: ~13,000 (minimal removal)
- Tuned-Indep: 10,000-13,000 (depends on tuned thresholds)
- Transferred-Dep: Varies by domain mix
- Tuned-Dep: Varies by quality filters

---

## 8. Environment Setup

**File:** `requirements.txt`

```
python>=3.9
torch>=2.0.0
transformers>=4.30.0
datasets>=2.12.0
accelerate>=0.20.0
deepspeed>=0.9.0
lm-evaluation-harness>=0.3.0
scipy>=1.10.0
numpy>=1.24.0
pyyaml>=6.0
tqdm>=4.65.0
```

**Hardware requirements:**

```yaml
gpu:
  model: "NVIDIA A100"
  memory: "40GB"
  count: 1

storage:
  total: "70GB"
  breakdown:
    datasets: "500MB"
    models: "65GB"  # 5 checkpoints × 13GB
    results: "1GB"

ram: "64GB"
```

**Installation:**

```bash
pip install -r requirements.txt
pip install git+https://github.com/EleutherAI/lm-evaluation-harness.git
```

---

## 9. Hyperparameter Rationale

### Training Hyperparameters (Fixed)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Learning rate | 2e-5 | Standard for LLaMA instruction tuning |
| Epochs | 3 | Standard instruction tuning duration |
| Batch size | 8 × 8 = 64 | Memory-feasible effective batch |
| Warmup steps | 100 | ~1% of total steps (13,513 samples / 64 batch) |
| LR scheduler | cosine | Standard for transformer fine-tuning |
| Weight decay | 0.01 | AdamW default |
| Max grad norm | 1.0 | Stability for FP16 training |
| Seed | 42 | Reproducibility |

### Filter Tuning Grids

**Objective-independent** (similarity_threshold):
- Range: [0.7, 0.8, 0.9, 0.95]
- Rationale: 0.8 is C4 baseline; test stricter (0.9, 0.95) and looser (0.7)

**Objective-independent** (perplexity cutoff):
- Range: [500, 1000, 1500, 2000]
- Rationale: 1000 is C4 baseline; test stricter (500) and looser (1500, 2000)

**Objective-dependent** (min_response_length):
- Range: [20, 50, 100]
- Rationale: Instruction responses vary; test minimal (20), moderate (50), strict (100)

---

## 10. Success Criteria Summary

**Gate passes (SHOULD_WORK) when:**

1. **Primary metrics:**
   - Objective-independent delta ≤ 1.0% (both MMLU and HellaSwag)
   - Objective-dependent delta > 5.0% (both MMLU and HellaSwag)

2. **Secondary metrics:**
   - 95% confidence intervals do not overlap between categories
   - Tuned-Indep > Baseline by ≥2% (validates curation utility)
   - Tuned-Dep > Baseline by ≥2%

3. **Statistical significance:**
   - Welch's t-test: p < 0.05 (category separation)
   - Cohen's d > 0.8 (large effect size, P2 criterion)

**Gate fails when:**
- Deltas overlap or reverse (independent > dependent)
- Insufficient statistical separation (p > 0.05)
- Both categories show <1% or >5% deltas (categorical distinction invalid)

---

## 11. Configuration File Locations

```
config/
├── c4_thresholds.yaml           # Extracted C4 filtering thresholds
├── train_config.yaml             # Fixed training hyperparameters
├── filter_tuning.yaml            # Grid search parameters
├── eval_config.yaml              # lm-evaluation-harness settings
├── statistical_config.yaml       # Bootstrap and hypothesis tests
└── gate_criteria.yaml            # SHOULD_WORK pass/fail thresholds

dolly_splits/
├── train.jsonl                   # 13,513 samples (90%)
└── val.jsonl                     # 1,502 samples (10%)

dolly_variants/
├── baseline/train.jsonl          # No filtering
├── transferred_indep/train.jsonl # C4 dedup + perplexity
├── tuned_indep/train.jsonl       # Optimized dedup + perplexity
├── transferred_dep/train.jsonl   # C4 domain mix + filters
└── tuned_dep/train.jsonl         # Optimized domain mix + filters

models/
├── baseline/                     # 13GB checkpoint
├── transferred_indep/
├── tuned_indep/
├── transferred_dep/
└── tuned_dep/

results/
├── mmlu_scores.csv
├── hellaswag_scores.csv
├── transfer_deltas.csv
├── statistical_analysis.yaml
└── gate_check.yaml
```

---

## 12. Quick Reference: Config Loading

**Python script example:**

```python
import yaml

# Load C4 thresholds
with open("config/c4_thresholds.yaml") as f:
    c4_config = yaml.safe_load(f)

# Load training config
with open("config/train_config.yaml") as f:
    train_config = yaml.safe_load(f)

# Load gate criteria
with open("config/gate_criteria.yaml") as f:
    gate_config = yaml.safe_load(f)

# Access values
dedup_threshold = c4_config["deduplication"]["similarity_threshold"]  # 0.8
learning_rate = train_config["training"]["learning_rate"]  # 2e-5
delta_max = gate_config["should_work"]["primary"]["objective_independent_delta_max"]  # 1.0
```

---

**Document Version:** 1.0  
**Status:** Phase 3 - Configuration Complete  
**Next Phase:** Phase 4 - Implementation
