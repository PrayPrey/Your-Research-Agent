# Configuration for H-E1 Attention-Retrieval Correlation

**Hypothesis**: h-e1  
**Type**: EXISTENCE (PoC)  
**Date**: 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New experiment - no base config to inherit  
**Config Files Found**: None - new config design  
**Pattern Used**: YAML config files (standard research experiment format)

---

## Configuration Files

### model_config.yaml

**Applied**: Standard HuggingFace Transformers defaults

```yaml
# Model: Llama-2-7B-Chat
model:
  checkpoint: "meta-llama/Llama-2-7b-chat-hf"
  device: "cuda"
  dtype: "float16"
  max_memory: {0: "38GB"}  # A100 40GB with 2GB headroom

generation:
  max_new_tokens: 128
  temperature: 0.7
  top_p: 0.9
  do_sample: false  # Greedy for reproducibility
  output_attentions: true  # CRITICAL

attention_extraction:
  target_layer: -1  # Last decoder layer
  aggregation_method: "mean_heads_sum_tokens"
```

---

### retrieval_config.yaml

**Applied**: BM25/Contriever paper defaults

```yaml
# BM25 (Lexical)
bm25:
  k1: 1.5  # Term frequency saturation
  b: 0.75  # Length normalization
  top_k: 10
  tokenizer: "nltk_word_tokenize"

# Contriever (Semantic)
contriever:
  checkpoint: "facebook/contriever-msmarco"
  max_length: 512
  batch_size: 64
  top_k: 10
  device: "cuda"
  pooling: "cls"  # CLS token embedding
```

---

### experiment_config.yaml

**Applied**: Standard correlation study design

```yaml
experiment:
  name: "h-e1-attention-correlation"
  hypothesis_id: "h-e1"
  random_seed: 42
  
dataset:
  source: "THUDM/LongBench"
  tasks: ["hotpotqa", "2wikimqa", "musique"]
  samples_per_task: 200
  total_samples: 600

query_complexity:
  simple:
    word_count_max: 10
    entity_density_max: 0.3
  complex:
    word_count_min: 10  # OR condition
    entity_density_min: 0.3
  ner_model: "en_core_web_sm"  # spaCy

checkpointing:
  interval: 100  # Save every 100 questions
  resume_enabled: true

evaluation:
  correlation_method: "spearman"
  confidence_interval: 0.95
  bootstrap_samples: 1000
  
answer_correctness:
  exact_match: true
  f1_threshold: 0.5  # OR condition with exact_match
```

---

### paths_config.yaml

**Applied**: Standard research repo structure

```yaml
paths:
  # Data
  data_root: "data/"
  raw: "data/longbench_raw/"
  preprocessed: "data/preprocessed/"
  retrieval: "data/retrieval/"
  cache: "data/cache/"
  
  # Outputs
  outputs_root: "outputs/"
  attentions: "outputs/attentions/"
  answers: "outputs/answers/"
  results: "outputs/results/"
  plots: "outputs/plots/"
  
  # Checkpoints
  checkpoints: "outputs/checkpoints/"
  
files:
  preprocessed_dataset: "preprocessed_longbench_h-e1.pkl"
  bm25_scores: "bm25_retrieval_scores.pkl"
  contriever_scores: "contriever_retrieval_scores.pkl"
  complexity_labels: "query_complexity_labels.pkl"
  correctness_labels: "answer_correctness_labels.pkl"
```

---

## Hyperparameter Justification

### Model Configuration

- **dtype: float16**: Llama-2-7B is 14GB in FP16, fits A100 40GB with 26GB headroom for activations
- **do_sample: false**: Greedy decoding for reproducibility (removes temperature randomness)
- **target_layer: -1**: Last layer attention most predictive per prior research

### Retrieval Configuration

- **BM25 k1=1.5, b=0.75**: Standard Okapi BM25 parameters from Robertson et al.
- **top_k: 10**: Balances coverage vs noise (LongBench contexts have 10-30 passages)

### Experiment Configuration

- **samples: 600**: Statistical power for correlation analysis at 95% CI
- **checkpoint_interval: 100**: Balance between resume granularity and I/O overhead
- **f1_threshold: 0.5**: Standard QA evaluation threshold (partial credit for incomplete answers)

---

## Validation Rules

```python
# Auto-validation (run before experiment)
VALIDATION_RULES = {
    "model_checkpoint_exists": lambda: check_hf_access("meta-llama/Llama-2-7b-chat-hf"),
    "gpu_memory_sufficient": lambda: torch.cuda.get_device_properties(0).total_memory > 38e9,
    "retrieval_top_k_valid": lambda: 5 <= CONFIG["retrieval"]["top_k"] <= 20,
    "sample_count_valid": lambda: CONFIG["experiment"]["total_samples"] == 600,
    "seed_fixed": lambda: CONFIG["experiment"]["random_seed"] is not None,
}
```

---

## Usage Example

```python
import yaml

# Load configs
with open("configs/model_config.yaml") as f:
    model_cfg = yaml.safe_load(f)
with open("configs/retrieval_config.yaml") as f:
    retrieval_cfg = yaml.safe_load(f)
with open("configs/experiment_config.yaml") as f:
    exp_cfg = yaml.safe_load(f)
with open("configs/paths_config.yaml") as f:
    paths_cfg = yaml.safe_load(f)

# Access values
checkpoint = model_cfg["model"]["checkpoint"]
bm25_k1 = retrieval_cfg["bm25"]["k1"]
seed = exp_cfg["experiment"]["random_seed"]
output_dir = paths_cfg["paths"]["outputs_root"]
```

---

## File Locations

Create these files in experiment repo:

```
h-e1-attention-correlation/
├── configs/
│   ├── model_config.yaml
│   ├── retrieval_config.yaml
│   ├── experiment_config.yaml
│   └── paths_config.yaml
```

---

**Config Status**: COMPLETE  
**Ready for Phase 4**: YES  
**Format**: YAML config files (standard research pattern)
