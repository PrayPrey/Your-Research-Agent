# Configuration: H-E1 — Scale-Dependent Optimal Curation (Existence Test)

Applied: Dataclass configuration pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## 1. Experiment Config (`code/config.py`)

```python
from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    # --- Factorial design axes ---
    ppl_thresholds: list[int] = field(default_factory=lambda: [20, 35, 50])
    dedup_jaccard: list[float] = field(default_factory=lambda: [0.7, 0.9])
    corpora: list[str] = field(default_factory=lambda: ["dolma", "fineweb"])
    scales: list[int] = field(default_factory=lambda: [70, 160])
    seeds: list[int] = field(default_factory=lambda: [1, 2, 3])

    # --- Token budget ---
    total_tokens: int = 50_000_000_000       # 50B tokens per run
    checkpoint_interval_tokens: int = 5_000_000_000  # every 5B → 10 checkpoints
    batch_size_tokens: int = 2_000_000       # 2M tokens per step
    train_steps: int = 25_000               # 50B / 2M

    # --- Corpus curation ---
    gpt2_ppl_model: str = "gpt2"
    ppl_batch_size: int = 64               # GPT-2 scoring batch size
    minhash_length: int = 256
    char_ngrams: int = 24
    minhash_seed: int = 42
    minhash_params: dict = field(default_factory=lambda: {
        0.7: {"num_buckets": 20, "hashes_per_bucket": 13},
        0.9: {"num_buckets": 8,  "hashes_per_bucket": 13},
    })

    # --- Preprocessing ---
    train_split: float = 0.95
    val_split: float = 0.025
    test_split: float = 0.025

    # --- Evaluation ---
    eval_tasks: list[str] = field(default_factory=lambda: ["mmlu", "hellaswag"])
    eval_num_fewshot: int = 4               # lm-eval --num_fewshot; HellaSwag uses 0 via task YAML
    eval_batch_size: str = "auto"

    # --- Statistical analysis ---
    significance_threshold: float = 0.05
    effect_size_threshold: float = 0.15    # partial η² (non-standard: PRD-specified gate)
    ancova_formula: str = "mmlu_4shot ~ C(scale) * C(ppl_threshold) + contamination_rate"

    # --- Paths (set at runtime or override) ---
    neox_tokenizer: str = "20B_tokenizer.json"
    neox_repo: str = "gpt-neox"            # path to cloned EleutherAI/gpt-neox
    corpus_root: str = "data/h-e1/corpora"
    checkpoint_root: str = "data/h-e1/checkpoints"
    eval_root: str = "data/h-e1/eval"
    results_csv: str = "results/h-e1/results.csv"
    results_parquet: str = "results/h-e1/results.parquet"
    figures_dir: str = "docs/youra_research/h-e1/figures"

    # --- Per-scale Pythia configs ---
    pythia_configs: dict = field(default_factory=lambda: {
        70: {
            "num_layers": 6,
            "hidden_size": 512,
            "num_attention_heads": 8,
            "seq_length": 2048,
            "rotary_pct": 0.25,
            "lr": 1e-3,
            "min_lr": 1e-4,
        },
        160: {
            "num_layers": 12,
            "hidden_size": 768,
            "num_attention_heads": 12,
            "seq_length": 2048,
            "rotary_pct": 0.25,
            "lr": 6e-4,
            "min_lr": 6e-5,
        },
    })


CONFIG = ExperimentConfig()
```

---

## 2. GPT-NeoX YAML Config Templates

`build_neox_config()` in `train.py` writes a YAML file by merging these overrides onto a base Pythia config.

### Pythia 70M override template

```yaml
# 70M-specific fields; merged with common block below
num-layers: 6
hidden-size: 512
num-attention-heads: 8
optimizer:
  params:
    lr: 0.001
min-lr: 0.0001
```

### Pythia 160M override template

```yaml
# 160M-specific fields
num-layers: 12
hidden-size: 768
num-attention-heads: 12
optimizer:
  params:
    lr: 0.0006
min-lr: 0.00006
```

### Common block (both scales)

```yaml
seq-length: 2048
max-position-embeddings: 2048
rotary-pct: 0.25
pos-emb: rotary

optimizer:
  type: Adam
  params:
    beta1: 0.9
    beta2: 0.95
    eps: 1.0e-8

lr-decay-style: cosine
warmup: 0.01
weight-decay: 0.1
gradient-clipping: 1.0

fp16:
  enabled: true

zero_optimization:
  stage: 1

train-iters: 25000
global-batch-size: 2048        # 2M tokens / seq_length=2048 = 1024 seqs; adjust per GPU count
checkpoint-factor: 12500       # save every 5B tokens → every 2500 steps (5B/2M)
save-interval: 2500
eval-interval: 2500
```

---

## 3. NeMo-Curator FuzzyDuplicatesConfig

```python
from nemo_curator.modules.fuzzy_dedup import FuzzyDuplicatesConfig

FUZZY_CONFIGS = {
    0.7: FuzzyDuplicatesConfig(
        num_buckets=20,
        hashes_per_bucket=13,
        char_ngrams=24,
        minhash_length=256,
        seed=42,
    ),
    0.9: FuzzyDuplicatesConfig(
        num_buckets=8,
        hashes_per_bucket=13,
        char_ngrams=24,
        minhash_length=256,
        seed=42,
    ),
}
```

---

## 4. Evaluation Config

lm-eval is invoked via subprocess in `evaluate.py`. Effective settings:

```python
LM_EVAL_DEFAULTS = {
    "model": "hf",
    "tasks": ["mmlu", "hellaswag"],
    "num_fewshot": 4,      # HellaSwag task YAML overrides to 0-shot internally
    "batch_size": "auto",
}
```

CLI template:
```bash
lm-eval \
  --model hf \
  --model_args pretrained={model_path} \
  --tasks mmlu,hellaswag \
  --num_fewshot 4 \
  --batch_size auto \
  --output_path {output_path}
```

---

## 5. Statistical Analysis Config

```python
ANALYSIS_CONFIG = {
    "significance_threshold": 0.05,
    "effect_size_threshold": 0.15,   # partial η²; PRD gate criterion
    "ancova_formula": "mmlu_4shot ~ C(scale) * C(ppl_threshold) + contamination_rate",
    "interaction_term": "C(scale):C(ppl_threshold)",
    "secondary_formula": "mmlu_4shot ~ C(scale) * C(dedup_j)",
}
```

---

## 6. Results Schema

```python
# columns in results/h-e1/results.csv
RESULTS_COLUMNS = [
    "scale",             # int: 70 | 160
    "ppl_threshold",     # int: 20 | 35 | 50
    "dedup_j",           # float: 0.7 | 0.9
    "corpus",            # str: "dolma" | "fineweb"
    "seed",              # int: 1 | 2 | 3
    "checkpoint_step",   # int: 2500 | 5000 | ... | 25000
    "mmlu_4shot",        # float: accuracy
    "hellaswag_0shot",   # float: accuracy
    "contamination_rate",# float: CR(condition)
]
```
