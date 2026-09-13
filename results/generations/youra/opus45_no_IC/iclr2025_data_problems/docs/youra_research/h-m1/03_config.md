# Config: H-M1 (MECHANISM/PoC)

**Applied**: No matching KB pattern found (searched "experiment configuration patterns" — only unrelated PyTorch inductor / LaTeX / diffuser results); used standard PoC hardcoded-dict pattern (single fixed config, no tuning, no ablations, per EXISTENCE rules).

## Codebase Analysis (Serena)

**Project Type**: green-field (h-e1 reference exists but implements an unrelated pipeline and defines no reusable config symbols — confirmed in architecture doc)
**Status**: green-field — new config design
**Config Files Found**: None
**Pattern Used**: Hardcoded dict

---

## Config (`code/config.py`)

PoC config — single fixed run, no hyperparameter search, subtasks folded into A-1.

```python
CONFIG = {
    # N-gram
    "ngram_size": 13,  # GPT-3 / lm-eval-harness standard

    # Pile
    "pile_dataset": "EleutherAI/pile",  # HF id; fallback: local jsonl.zst path
    "pile_subset_docs": 200_000,  # representative subset (full 825GB out of scope per PRD)

    # Benchmarks: name -> (hf_id, subset, split)
    "benchmarks": {
        "mmlu": ("cais/mmlu", "all", "test"),
        "arc_challenge": ("allenai/ai2_arc", "ARC-Challenge", "test"),
        "hellaswag": ("Rowan/hellaswag", None, "validation"),
        "winogrande": ("allenai/winogrande", "winogrande_xl", "validation"),
    },

    # Gate
    "overlap_threshold": 0.01,  # 1% gate condition (PRD success criteria)

    # Repro
    "seed": 1,

    # Paths
    "output_dir": "results/",
    "index_path": "results/pile_index.pkl",
    "results_json": "results/overlap_results.json",
    "figures_dir": "figures/",
}
```

## YAML Schema

```yaml
ngram_size: 13
pile_dataset: "EleutherAI/pile"
pile_subset_docs: 200000
benchmarks:
  mmlu: {hf_id: "cais/mmlu", subset: "all", split: "test"}
  arc_challenge: {hf_id: "allenai/ai2_arc", subset: "ARC-Challenge", split: "test"}
  hellaswag: {hf_id: "Rowan/hellaswag", subset: null, split: "validation"}
  winogrande: {hf_id: "allenai/winogrande", subset: "winogrande_xl", split: "validation"}
overlap_threshold: 0.01
seed: 1
output_dir: "results/"
index_path: "results/pile_index.pkl"
results_json: "results/overlap_results.json"
figures_dir: "figures/"
```

## Default Values Rationale

| Field | Value | Rationale |
|-------|-------|-----------|
| `ngram_size` | 13 | GPT-3 contamination-detection standard, matches h-e1's `compute_ngram_overlap(n=13)` convention |
| `pile_subset_docs` | 200,000 | PRD explicitly scopes out full-825GB indexing; subset large enough to be "representative" per FR-2 |
| `overlap_threshold` | 0.01 | PRD success criteria: >1% overlap = gate pass |
| `seed` | 1 | Single fixed seed — PoC, no variance study needed |
| tokenization | lowercase + whitespace split | PRD FR-1 explicit requirement |

## Subtasks

None — config is a single file created as part of A-1 (Epic Task A-1: Config setup, budget 3, no further breakdown per 0-subtask allocation for this task).
