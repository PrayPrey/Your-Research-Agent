# Config: h-e1-v2
## Scale-Dependent Optimal Curation — Existence Test (Scope-Reduced)

Applied: dataclasses.replace() config-override pattern (EXISTENCE tier)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental from h-e1)
**Status**: Config classes verified from actual base code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dataclass + `dataclasses.replace()` — no subclassing

---

## Inherited Configuration (Base Hypothesis)

All fields below are from the actual `h-e1/code/config.py` implementation:

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    # Factorial design axes
    ppl_thresholds: list = [20, 35, 50]          # UNCHANGED in v2
    dedup_jaccard: list = [0.7, 0.9]              # UNCHANGED in v2
    corpora: list = ["dolma", "fineweb"]          # CHANGED → ["fineweb"]
    scales: list = [70, 160]                      # CHANGED → [14, 31]
    seeds: list = [1, 2, 3]                       # CHANGED → [1, 2]

    # Token budget
    total_tokens: int = 50_000_000_000            # CHANGED → 1_000_000_000
    checkpoint_interval_tokens: int = 5_000_000_000  # CHANGED → 100_000_000
    batch_size_tokens: int = 2_000_000            # UNCHANGED
    train_steps: int = 25_000                     # CHANGED → 500

    # Corpus curation
    gpt2_ppl_model: str = "gpt2"                 # UNCHANGED
    ppl_batch_size: int = 64                      # UNCHANGED
    minhash_length: int = 256                     # UNCHANGED
    char_ngrams: int = 24                         # UNCHANGED
    minhash_seed: int = 42                        # UNCHANGED
    minhash_params: dict = {
        0.7: {"num_buckets": 20, "hashes_per_bucket": 13},
        0.9: {"num_buckets": 8, "hashes_per_bucket": 13},
    }                                             # UNCHANGED

    # Preprocessing
    train_split: float = 0.95                     # UNCHANGED
    val_split: float = 0.025                      # UNCHANGED
    test_split: float = 0.025                     # UNCHANGED

    # Evaluation
    eval_tasks: list = ["mmlu", "hellaswag"]      # CHANGED → ["hellaswag"]
    eval_num_fewshot: int = 4                     # CHANGED → 0
    eval_batch_size: str = "auto"                 # UNCHANGED

    # Statistical analysis
    significance_threshold: float = 0.05         # UNCHANGED
    effect_size_threshold: float = 0.15          # UNCHANGED
    ancova_formula: str = "mmlu_4shot ~ ..."     # UNCHANGED (unused in v2)

    # Paths
    neox_tokenizer: str = "20B_tokenizer.json"   # UNCHANGED
    neox_repo: str = "gpt-neox"                  # UNCHANGED
    corpus_root: str = ".../data/h-e1/corpora"   # CHANGED → h-e1-v2 paths
    checkpoint_root: str = ".../data/h-e1/checkpoints"  # CHANGED
    eval_root: str = ".../data/h-e1/eval"        # CHANGED
    results_csv: str = ".../results/h-e1/results.csv"   # CHANGED
    results_parquet: str = ".../results/h-e1/results.parquet"  # UNCHANGED (not used in v2)
    figures_dir: str = ".../docs/youra_research/h-e1/figures"  # CHANGED

    # Per-scale Pythia configs
    pythia_configs: dict = {
        70: {"num_layers": 6, "hidden_size": 512, "num_attention_heads": 8,
             "seq_length": 2048, "rotary_pct": 0.25, "lr": 1e-3, "min_lr": 1e-4},
        160: {"num_layers": 12, "hidden_size": 768, "num_attention_heads": 12,
              "seq_length": 2048, "rotary_pct": 0.25, "lr": 6e-4, "min_lr": 6e-5},
    }                                             # CHANGED → 14M/31M entries
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

---

## C-1: ExperimentConfig Override for h-e1-v2 [Complexity: 5, Budget: 1 subtask]

Applied: dataclasses.replace() single-instance override

### Configuration (`h-e1-v2/code/config_v2.py`)

```python
import os
import sys
import dataclasses

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from config import ExperimentConfig

BASE_V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_V2: ExperimentConfig = dataclasses.replace(
    ExperimentConfig(),
    # Scales: 14M/31M (was 70M/160M)
    scales=[14, 31],
    pythia_configs={
        14: {
            "num_layers": 6,
            "hidden_size": 128,
            "num_attention_heads": 4,
            "seq_length": 2048,
            "rotary_pct": 0.25,
            "lr": 1e-3,
            "min_lr": 1e-4,
        },
        31: {
            "num_layers": 6,
            "hidden_size": 256,
            "num_attention_heads": 8,
            "seq_length": 2048,
            "rotary_pct": 0.25,
            "lr": 1e-3,
            "min_lr": 1e-4,
        },
    },
    # Token budget: 1B (was 50B)
    total_tokens=1_000_000_000,
    train_steps=500,
    checkpoint_interval_tokens=100_000_000,
    # Seeds: 2 (was 3)
    seeds=[1, 2],
    # Dataset: FineWeb only (was dolma + fineweb)
    corpora=["fineweb"],
    # Evaluation: HellaSwag 0-shot only (was mmlu + hellaswag, 4-shot)
    eval_tasks=["hellaswag"],
    eval_num_fewshot=0,
    # Paths: h-e1-v2
    corpus_root=os.path.join(BASE_V2, "../../data/h-e1-v2/corpora"),
    checkpoint_root=os.path.join(BASE_V2, "../../data/h-e1-v2/checkpoints"),
    eval_root=os.path.join(BASE_V2, "../../data/h-e1-v2/eval"),
    results_csv=os.path.join(BASE_V2, "../../results/h-e1-v2/results.csv"),
    figures_dir=os.path.join(BASE_V2, "figures"),
)
```

### YAML Equivalent (human-readable reference)

```yaml
# h-e1-v2 overrides (fields not listed are inherited from h-e1)
scales: [14, 31]
total_tokens: 1_000_000_000
train_steps: 500
checkpoint_interval_tokens: 100_000_000
seeds: [1, 2]
corpora: ["fineweb"]
eval_tasks: ["hellaswag"]
eval_num_fewshot: 0

pythia_configs:
  14:
    num_layers: 6
    hidden_size: 128
    num_attention_heads: 4
    seq_length: 2048
    rotary_pct: 0.25
    lr: 1.0e-3
    min_lr: 1.0e-4
  31:
    num_layers: 6
    hidden_size: 256
    num_attention_heads: 8
    seq_length: 2048
    rotary_pct: 0.25
    lr: 1.0e-3
    min_lr: 1.0e-4

paths:
  corpus_root: data/h-e1-v2/corpora
  checkpoint_root: data/h-e1-v2/checkpoints
  eval_root: data/h-e1-v2/eval
  results_csv: results/h-e1-v2/results.csv
  figures_dir: docs/youra_research/h-e1-v2/figures
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Write config_v2.py | Create `h-e1-v2/code/config_v2.py` with CONFIG_V2 using dataclasses.replace() |

---

## C-2: Curation Condition Configs [Complexity: 5, Budget: 1 subtask]

Applied: hardcoded dict — 6 fixed conditions, no tuning needed

### 6 Curation Conditions

Factorial: PPL threshold τ ∈ {20, 35, 50} × Jaccard J ∈ {0.7, 0.9} = 6 conditions.

```python
# All 6 curation conditions for h-e1-v2
# NeMo-Curator params differ from h-e1 minhash_params (which used num_buckets/hashes_per_bucket).
# FuzzyDeduplicationWorkflow uses num_bands/minhashes_per_band naming.
CURATION_CONDITIONS = [
    {
        "condition_id": "ppl20_j07",
        "ppl_threshold": 20,
        "jaccard_threshold": 0.7,
        # GPT-2 PPL filter: keep documents with perplexity <= threshold
        "ppl_filter": {"model": "gpt2", "max_ppl": 20, "batch_size": 64},
        # NeMo-Curator FuzzyDeduplicationWorkflow params for J=0.7
        "dedup": {"num_bands": 25, "minhashes_per_band": 10},
        # Expected token retention after filtering (from PRD FR-1)
        "expected_retention_pct": 10,  # ~10% of raw FineWeb
    },
    {
        "condition_id": "ppl20_j09",
        "ppl_threshold": 20,
        "jaccard_threshold": 0.9,
        "ppl_filter": {"model": "gpt2", "max_ppl": 20, "batch_size": 64},
        # NeMo-Curator FuzzyDeduplicationWorkflow params for J=0.9
        "dedup": {"num_bands": 15, "minhashes_per_band": 15},
        "expected_retention_pct": 12,
    },
    {
        "condition_id": "ppl35_j07",
        "ppl_threshold": 35,
        "jaccard_threshold": 0.7,
        "ppl_filter": {"model": "gpt2", "max_ppl": 35, "batch_size": 64},
        "dedup": {"num_bands": 25, "minhashes_per_band": 10},
        "expected_retention_pct": 35,
    },
    {
        "condition_id": "ppl35_j09",
        "ppl_threshold": 35,
        "jaccard_threshold": 0.9,
        "ppl_filter": {"model": "gpt2", "max_ppl": 35, "batch_size": 64},
        "dedup": {"num_bands": 15, "minhashes_per_band": 15},
        "expected_retention_pct": 40,
    },
    {
        "condition_id": "ppl50_j07",
        "ppl_threshold": 50,
        "jaccard_threshold": 0.7,
        "ppl_filter": {"model": "gpt2", "max_ppl": 50, "batch_size": 64},
        "dedup": {"num_bands": 25, "minhashes_per_band": 10},
        "expected_retention_pct": 60,
    },
    {
        "condition_id": "ppl50_j09",
        "ppl_threshold": 50,
        "jaccard_threshold": 0.9,
        "ppl_filter": {"model": "gpt2", "max_ppl": 50, "batch_size": 64},
        "dedup": {"num_bands": 15, "minhashes_per_band": 15},
        "expected_retention_pct": 65,
    },
]

# Index by condition_id for O(1) lookup
CURATION_CONDITIONS_BY_ID = {c["condition_id"]: c for c in CURATION_CONDITIONS}
```

### NeMo-Curator Dedup Params Rationale

| Jaccard J | num_bands | minhashes_per_band | Total minhashes | LSH recall target |
|-----------|-----------|-------------------|-----------------|-------------------|
| 0.7 | 25 | 10 | 250 | ~0.99 at J=0.7 |
| 0.9 | 15 | 15 | 225 | ~0.99 at J=0.9 |

These params are non-standard (not PyTorch defaults) — chosen to match LSH probability curve for each threshold.

### Per-Condition YAML Schema

```yaml
# Template: one entry per condition (6 total)
condition_id: ppl35_j07
ppl_filter:
  model: gpt2
  max_ppl: 35
  batch_size: 64
dedup:
  num_bands: 25
  minhashes_per_band: 10
expected_retention_pct: 35
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Write CURATION_CONDITIONS | Add `CURATION_CONDITIONS` list to `config_v2.py` alongside CONFIG_V2 |
