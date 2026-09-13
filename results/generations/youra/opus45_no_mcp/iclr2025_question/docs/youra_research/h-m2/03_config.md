# Configuration: H-M2 (Semantic Consistency as Hallucination Predictor)

**Applied**: Hardcoded module-level config (dict-of-constants pattern), copied from H-M1 for cross-hypothesis consistency, extended with embedding + gate params.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config fields verified directly from `03_architecture.md` (Codebase Analysis section already cross-checked `h-m1/code/config.py`, `results/h-m1_results.json`, `results/checkpoint.json` — architecture doc confirms exact field names/values). Direct glob for `h-m1/code/config*.py` in this session found no file (path likely not materialized as actual code yet — h-m1 is spec-level in this pass), so values below are taken verbatim from the architecture doc's verified config listing.
**Config Files Found**: `h-m1/code/config.py` (referenced, module-level constants — NOT a dataclass)
**Pattern Used**: Hardcoded constants (module-level), matching H-M1 exactly

---

## Config (`h-m2/code/config.py`)

```python
# Generation (copied from h-m1)
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
NUM_RESPONSES = 10
TEMPERATURE = 0.7
TOP_P = 0.9
MAX_NEW_TOKENS = 128
SEED = 42
N_QUESTIONS = 100

# Embedding (new)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Gate thresholds (new)
AUROC_TARGET = 0.55
P_VALUE_TARGET = 0.05

# Checkpoint / IO (copied from h-m1)
CHECKPOINT_PATH = "results/checkpoint.json"
CHECKPOINT_EVERY = 50
OUTPUT_PATH = "results/h-m2_results.json"
FIGURES_DIR = "figures/"
```

**Non-standard**: `MAX_NEW_TOKENS=128` (PRD FR-1 says 100) — kept at 128 to match H-M1's actual verified code exactly, since generation must be identical between hypotheses for a controlled comparison. PRD's "100" is stale; architecture doc's verified value wins.

---

## A-1: Config + Copy Base Modules [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch/HF defaults, copy-verbatim strategy for sibling-folder reuse (no cross-package import).

Copy unchanged from `h-m1/code/`: `config.py` (extend as above), `load_data.py`, `generate.py`, `entropy.py`, `correctness.py`, `checkpoint.py`.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Write config.py | Constants above |
| C-1-2 | Copy load_data.py + generate.py | Verbatim copy, no edits |
| C-1-3 | Copy entropy.py | Verbatim copy |
| C-1-4 | Copy correctness.py + checkpoint.py | Verbatim copy |

---

## A-2: SemanticConsistencyScorer [Complexity: 8, Budget: 8]

**Applied**: SelfCheckGPT-style pairwise embedding similarity (sentence-transformers).

```python
@dataclass
class ConsistencyConfig:
    embedding_model: str = EMBEDDING_MODEL  # "all-MiniLM-L6-v2"
    batch_size: int = 32
```

`SemanticConsistencyScorer.compute_consistency(responses: list[str]) -> float`: encode N=10 responses -> (10,384), mean of 45 pairwise cosine sims.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | Load embedding model | Cache SentenceTransformer(EMBEDDING_MODEL) at module init |
| C-2-2 | Batch encode responses | `.encode(responses, batch_size=32)` |
| C-2-3 | Pairwise cosine sim | sklearn `cosine_similarity`, upper-triangle mean |
| C-2-4 | Unit sanity check | assert identical responses -> consistency ~= 1.0 |

---

## A-3: Consistency Stats Analyzer [Complexity: 7, Budget: 7]

**Applied**: Independent samples t-test (one-sided) + AUROC + Cohen's d, same pattern as H-M1's entropy stats module.

```python
STATS_CONFIG = {
    "alternative": "greater",   # correct > incorrect
    "auroc_target": AUROC_TARGET,
    "p_value_target": P_VALUE_TARGET,
}
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | t-test | `scipy.stats.ttest_ind(alternative="greater")` |
| C-3-2 | AUROC | `sklearn.metrics.roc_auc_score(correct, consistency)` |
| C-3-3 | Cohen's d | pooled-std effect size |
| C-3-4 | Assemble result dict | `{t_stat, p_value, auroc, cohens_d, mean_correct, mean_incorrect, n_correct, n_incorrect}` |

---

## A-4: Entropy-Consistency Correlation [Complexity: 4, Budget: 4]

**Applied**: Standard Pearson correlation (scipy), H-M3 preview only.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | Pearson r | `scipy.stats.pearsonr(entropies, consistencies)[0]` |
| C-4-2 | Guard n<2 | return None if fewer than 2 points |
| C-4-3 | Add to results dict | key `pearson_r_entropy_consistency` |
| C-4-4 | Smoke test | check r in [-1, 1] |

---

## A-5: Visualizer [Complexity: 8, Budget: 8]

**Applied**: matplotlib + sklearn roc_curve pattern (extends H-M1's gate-bar plot).

```python
VIS_CONFIG = {
    "figsize_default": (6, 4),
    "dpi": 150,
    "figures_dir": FIGURES_DIR,
}
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | Gate bar plot | AUROC vs target, p-value vs target |
| C-5-2 | Consistency histograms | overlaid correct/incorrect distributions |
| C-5-3 | ROC curve | sklearn `roc_curve` + AUC annotation |
| C-5-4 | Entropy-vs-consistency scatter | colored by correctness, for H-M3 preview |

---

## A-6: Pipeline Integration [Complexity: 11, Budget: 11]

**Applied**: Sequential orchestration + checkpoint resume, matching H-M1's `run_pipeline.py` structure.

```python
PIPELINE_CONFIG = {
    "limit": N_QUESTIONS,      # 100
    "resume": True,
    "checkpoint_every": CHECKPOINT_EVERY,  # 50
}
```

### Subtasks [8/8 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | Load data + model | `load_triviaqa_val`, `load_model` |
| C-6-2 | Per-question loop | generate 10 responses, checkpoint resume check |
| C-6-3 | Compute entropy | mean token entropy across 10 responses |
| C-6-4 | Compute consistency | `SemanticConsistencyScorer.compute_consistency` |
| C-6-5 | Compute correctness | majority answer + exact-match |
| C-6-6 | Save checkpoint | every 50 questions |
| C-6-7 | Aggregate stats | call stats.py functions on full result set |
| C-6-8 | Write output + figures | `results/h-m2_results.json`, call visualize.py |

---

## A-7: Full-Run Validation [Complexity: 9, Budget: 9]

**Applied**: End-to-end gate check against PRD success criteria (SHOULD_WORK gate — no hard block).

```python
GATE_CONFIG = {
    "p_value_threshold": P_VALUE_TARGET,   # < 0.05
    "auroc_threshold": AUROC_TARGET,        # > 0.55
    "direction_check": "mean_correct > mean_incorrect",
}
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-7-1 | Run full 100-question pipeline | `run(limit=100, resume=True)` |
| C-7-2 | Verify no errors / output written | check `results/h-m2_results.json` exists and parses |
| C-7-3 | Check gate criteria | p<0.05, AUROC>0.55, direction correct |
| C-7-4 | Document result | pass/fail note in `04_validation.md` (SHOULD_WORK: continue regardless) |

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/code/config.py (verified via architecture.md Codebase Analysis)
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
NUM_RESPONSES = 10
TEMPERATURE = 0.7
TOP_P = 0.9
MAX_NEW_TOKENS = 128
SEED = 42
N_QUESTIONS = 100
CHECKPOINT_PATH = "results/checkpoint.json"
CHECKPOINT_EVERY = 50
```

H-M2 extends with: `EMBEDDING_MODEL`, `AUROC_TARGET`, `P_VALUE_TARGET`, `OUTPUT_PATH` (repointed to `h-m2_results.json`), `FIGURES_DIR`.

**Verified from**: `h-m1/code/config.py` field listing in `h-m2/03_architecture.md` (Codebase Analysis section, cross-checked against `h-m1/results/h-m1_results.json` and `checkpoint.json`).

**Note**: H-M1's `generate_responses()` raw texts were not persisted (only truncated `majority_answer`), so H-M2 must regenerate all responses with identical config — it cannot load H-M1's raw outputs directly.
