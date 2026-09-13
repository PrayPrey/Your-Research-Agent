# Config: H-M2 (Deduplication Stringency Dose-Response)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass

Applied: data-pipeline-sweep pattern (config-varied dataset generation, dataclass schema)
Applied: from-scratch-LM-training pattern (GPT-2 hyperparameter defaults)

---

## A-2: Dedup Module [Complexity: 10, Budget: 3 subtasks]

**Applied**: data-pipeline-sweep pattern (5 discrete levels, ordered stringency)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class DeduplicationConfig:
    level: str                    # "none" | "fuzzy_0.7" | "fuzzy_0.85" | "exact" | "exact_plus_fuzzy"
    jaccard_threshold: float       # MinHash LSH threshold; 1.0 = disabled
    include_exact: bool            # apply exact string-match dedup

DEDUP_LEVELS: list[DeduplicationConfig] = [
    DeduplicationConfig("none",              jaccard_threshold=1.0,  include_exact=False),
    DeduplicationConfig("fuzzy_0.7",         jaccard_threshold=0.7,  include_exact=False),
    DeduplicationConfig("fuzzy_0.85",        jaccard_threshold=0.85, include_exact=False),
    DeduplicationConfig("exact",             jaccard_threshold=1.0,  include_exact=True),
    DeduplicationConfig("exact_plus_fuzzy",  jaccard_threshold=0.85, include_exact=True),
]

# text-dedup MinHash params (fixed, not swept)
MINHASH_NUM_PERM: int = 128
MINHASH_NGRAM_SIZE: int = 5
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | MinHash LSH dedup | `apply_deduplication()` using text-dedup MinHash for fuzzy levels |
| C-2-2 | Exact dedup | Exact string-match pass, combinable with fuzzy (exact_plus_fuzzy) |
| C-2-3 | Verification + stats | `verify_deduplication_applied()`, `log_dedup_stats()` — removal count/pct |

---

## A-6: Evaluation Module [Complexity: 9, Budget: 3 subtasks]

**Applied**: dose-response evaluation pattern (ensemble PC1 metric across ordered levels)

### Configuration (Python Dataclass)

```python
@dataclass
class EvalConfig:
    tasks: tuple[str, ...] = ("hellaswag", "arc_easy", "piqa", "winogrande")
    batch_size: int = 32
    num_fewshot: int = 0
    device: str = "cuda"
    limit: int | None = None   # None = full eval set
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | lm-eval-harness runner | `run_benchmarks(checkpoint_path, tasks)` -> per-task accuracy dict |
| C-6-2 | PC1 ensemble | `compute_pc1_ensemble(scores)` — PCA across 4 benchmarks x 3 seeds, project PC1 |
| C-6-3 | Result serialization | Write per-checkpoint benchmark JSON to `results/{level}/{seed}/eval.json` |

---

## TrainConfig (GPT-2 125M, Reference Only — A-4/A-5, out of allocated budget)

```python
@dataclass
class TrainConfig:
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
    total_tokens: int = 10_000_000_000
    seq_len: int = 1024
    batch_size: int = 512
    lr: float = 6e-4
    warmup_steps: int = 2000
    beta1: float = 0.9
    beta2: float = 0.95
    weight_decay: float = 0.1
    checkpoint_every_tokens: int = 1_000_000_000
    seeds: tuple[int, int, int] = (0, 1, 2)
```

Sources: FR-2 (PRD), GPT-2 small standard architecture, AdamW/cosine schedule as specified in PRD.

---

## YAML Schema: Experiment Sweep

```yaml
sweep:
  dedup_levels: [none, fuzzy_0.7, fuzzy_0.85, exact, exact_plus_fuzzy]
  seeds: [0, 1, 2]
  train:
    n_layer: 12
    n_head: 12
    n_embd: 768
    total_tokens: 10_000_000_000
    batch_size: 512
    lr: 6e-4
    warmup_steps: 2000
  eval:
    tasks: [hellaswag, arc_easy, piqa, winogrande]
    num_fewshot: 0
  output:
    checkpoint_dir: checkpoints/{level}/{seed}/
    results_dir: results/{level}/{seed}/eval.json
```

15 total runs = 5 dedup_levels x 3 seeds.

---

## Default Hyperparameter Values with Sources

| Param | Value | Source |
|-------|-------|--------|
| jaccard_threshold (fuzzy_0.7) | 0.7 | PRD FR-5 |
| jaccard_threshold (fuzzy_0.85) | 0.85 | PRD FR-5 |
| minhash_num_perm | 128 | text-dedup default |
| minhash_ngram_size | 5 | text-dedup default (word n-grams) |
| n_layer/n_head/n_embd | 12/12/768 | PRD FR-2, GPT-2 small |
| total_tokens | 10e9 | PRD FR-2 |
| lr | 6e-4 | PRD FR-2 |
| warmup_steps | 2000 | PRD FR-2 |
| beta1/beta2/wd | 0.9/0.95/0.1 | PRD FR-2 |
| eval tasks | hellaswag, arc_easy, piqa, winogrande | PRD FR-3 |
| num_fewshot | 0 | lm-eval-harness standard zero-shot |
| checkpoint interval | 1B tokens | PRD NFR-2 |
