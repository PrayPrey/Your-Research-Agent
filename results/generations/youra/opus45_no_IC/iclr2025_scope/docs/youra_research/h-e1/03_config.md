# Config: H-E1 (EXISTENCE PoC)

**Applied**: No KB match for KV-cache/gap-statistic config patterns (generic diffusion/inductor/JAX docs only) — standard PoC hardcoded-dict pattern used instead.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dict (single fixed config, no dataclass — EXISTENCE PoC rule)

---

## A-1: Config + Data Loading [Complexity: 8, Budget: 1 subtask]

### Configuration (Hardcoded dict — `code/config.py`)

```python
TASKS = [
    "narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh",
    "hotpotqa", "2wikimqa", "musique", "dureader",
    "gov_report", "qmsum", "multi_news", "vcsum",
    "trec", "triviaqa", "samsum", "lsht",
    "passage_retrieval_en", "passage_count", "passage_retrieval_zh",
    "lcc", "repobench-p",
]  # 21 LongBench tasks

# 6 compression configurations (method, retention, quantization)
COMPRESSION_CONFIGS = [
    {"name": "C1_full",       "method": "full", "retention": 1.0, "quantization": None},
    {"name": "C2_h2o80",      "method": "h2o",  "retention": 0.8, "quantization": None},
    {"name": "C3_h2o40",      "method": "h2o",  "retention": 0.4, "quantization": None},
    {"name": "C4_full_int8",  "method": "full", "retention": 1.0, "quantization": "int8"},
    {"name": "C5_full_int4",  "method": "full", "retention": 1.0, "quantization": "int4"},
    {"name": "C6_h2o60_int8", "method": "h2o",  "retention": 0.6, "quantization": "int8"},
]

MODEL_ID = "meta-llama/Llama-2-7b-hf"
MAX_TOKENS = 4096          # context truncation limit
MAX_NEW_TOKENS = 128       # generation length (LongBench default)
SEED = 42

# Gap statistic clustering params
GAP_STATISTIC = {
    "n_refs": 500,   # bootstrap reference samples
    "max_k": 6,      # test k in range(1, max_k+1)
}

# Output paths (relative to h-e1/)
OUTPUT_DIR = "h-e1"
RESPONSE_MATRIX_PATH = f"{OUTPUT_DIR}/response_matrix.npy"
GAP_RESULTS_PATH = f"{OUTPUT_DIR}/gap_results.json"
CLUSTER_LABELS_PATH = f"{OUTPUT_DIR}/cluster_labels.json"
FIGURES_DIR = f"{OUTPUT_DIR}/figures"
```

**Non-standard**: `MAX_NEW_TOKENS=128` — LongBench standard eval generation length (not tuned).

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Evaluation metrics config | Per-task metric dispatch table (task name -> scorer fn: qa_f1_score / rouge_score / classification_score / retrieval_score / code_sim_score), used by `evaluate.py::score_task` |

```python
TASK_METRIC = {
    "narrativeqa": "qa_f1_score", "qasper": "qa_f1_score",
    "multifieldqa_en": "qa_f1_score", "multifieldqa_zh": "qa_f1_score",
    "hotpotqa": "qa_f1_score", "2wikimqa": "qa_f1_score",
    "musique": "qa_f1_score", "dureader": "qa_f1_score",
    "gov_report": "rouge_score", "qmsum": "rouge_score",
    "multi_news": "rouge_score", "vcsum": "rouge_score",
    "trec": "classification_score", "triviaqa": "qa_f1_score",
    "samsum": "rouge_score", "lsht": "classification_score",
    "passage_retrieval_en": "retrieval_score", "passage_count": "qa_f1_score",
    "passage_retrieval_zh": "retrieval_score",
    "lcc": "code_sim_score", "repobench-p": "code_sim_score",
}
```

---

## No Hyperparameter Sweep (EXISTENCE Rule)

Single fixed config per PRD FR-3 (6 compression configs are the experiment's independent variable, not a tuning grid). No LR/epoch sweep — no training occurs (analysis/clustering only, per experiment brief).
