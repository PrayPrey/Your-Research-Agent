# Config: H-E1 — Token-Level Log-Probability Aggregation Ablation

**Date:** 2026-08-21
**Hypothesis:** H-E1 (EXISTENCE / LIGHT)
**Applied:** frozen dataclass single-config pattern (green-field)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design, no existing codebase to analyze
**Config Files Found**: None — new config
**Pattern Used**: frozen dataclass

---

## E-4: Orchestration + Persistence [Complexity: 9, Budget: 1 subtask]

**Applied**: Standard frozen dataclass pattern (no KB match — literature default)

### C-4-1: Experiment Config Dataclass + Output Schemas

#### `code/config.py`

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExperimentConfig:
    model_ids: dict[str, str] = field(default_factory=lambda: {
        "llama2": "meta-llama/Llama-2-7b-hf",
        "mistral": "mistralai/Mistral-7B-v0.1",
    })
    datasets: tuple[str, ...] = ("trivia_qa", "nq", "truthful_qa")
    aggregation_methods: tuple[str, ...] = ("min", "mean", "sum")
    seed: int = 42
    max_new_tokens: int = 50
    bootstrap_n_resamples: int = 1000
    ece_n_bins: int = 15
    length_stratification_threshold: int = 5
    results_dir: str = "docs/youra_research/h-e1/results"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    farquhar_data_dir: str = "data/semantic_uncertainty"
    truthful_qa_rouge_threshold: float = 0.3
    gate_auroc_diff_threshold: float = 0.02
    torch_dtype: str = "float16"
    attn_implementation: str = "flash_attention_2"


# Singleton used by all modules
CFG = ExperimentConfig()
```

> Non-standard: `datasets` and `aggregation_methods` use `tuple` instead of `list` to satisfy `frozen=True` (lists are mutable and disallowed in frozen dataclasses). Callers iterate normally.

---

#### `config.yaml` (YAML equivalent for reference/CLI use)

```yaml
model_ids:
  llama2: "meta-llama/Llama-2-7b-hf"
  mistral: "mistralai/Mistral-7B-v0.1"

datasets:
  - trivia_qa
  - nq
  - truthful_qa

aggregation_methods:
  - min
  - mean
  - sum

seed: 42
max_new_tokens: 50
bootstrap_n_resamples: 1000
ece_n_bins: 15
length_stratification_threshold: 5

results_dir: "docs/youra_research/h-e1/results"
figures_dir: "docs/youra_research/h-e1/figures"
farquhar_data_dir: "data/semantic_uncertainty"

truthful_qa_rouge_threshold: 0.3
gate_auroc_diff_threshold: 0.02
torch_dtype: "float16"
attn_implementation: "flash_attention_2"
```

---

### Output File Schemas

#### `results/auroc_table.csv`

| Column | dtype | Description |
|--------|-------|-------------|
| `model` | str | Short model key (`llama2`, `mistral`) |
| `dataset` | str | Dataset name (`trivia_qa`, `nq`, `truthful_qa`) |
| `aggregation` | str | Method (`min`, `mean`, `sum`) |
| `auroc` | float64 | AUROC score |
| `auprc` | float64 | AUPRC score |
| `ece` | float64 | ECE (15-bin) |
| `n_samples` | int64 | Number of samples in cell |

18 rows (2 models × 3 datasets × 3 aggregations).

---

#### `results/bootstrap_ci_table.csv`

| Column | dtype | Description |
|--------|-------|-------------|
| `model` | str | Short model key |
| `dataset` | str | Dataset name |
| `pair` | str | Pairwise comparison label e.g. `min_vs_mean` |
| `auroc_diff` | float64 | Point estimate: AUROC(a) − AUROC(b) |
| `ci_lower` | float64 | 95% CI lower bound (percentile bootstrap) |
| `ci_upper` | float64 | 95% CI upper bound |
| `n_resamples` | int64 | Bootstrap resamples used (1000) |

18 rows (2 models × 3 datasets × 3 pairs).

---

#### `results/scores_{model}_{dataset}.npz` — Array Schema

```
scores_{model}_{dataset}.npz
├── labels        shape: (N,)   dtype: int32    # binary: 1=correct, 0=hallucinated
├── scores_min    shape: (N,)   dtype: float32  # negated min log-prob
├── scores_mean   shape: (N,)   dtype: float32  # negated mean log-prob
├── scores_sum    shape: (N,)   dtype: float32  # negated sum log-prob
└── n_tokens      shape: (N,)   dtype: int32    # generated token count per sample
```

N varies by dataset: ~7000 (trivia_qa), ~3600 (nq), ~817 (truthful_qa).
File naming examples: `scores_llama2_trivia_qa.npz`, `scores_mistral_nq.npz`.

---

#### `results/gate_decision_h-e1.md` — Template

```markdown
# Gate Decision: H-E1

**Date:** {YYYY-MM-DD}
**Status:** PASS | FAIL

## Gate Criterion

Any pairwise AUROC diff >= 0.02 with bootstrap 95% CI lower bound > 0.

## Result Summary

| Model | Dataset | Pair | AUROC Diff | CI Lower | CI Upper | Passes Gate |
|-------|---------|------|-----------|---------|---------|------------|
| ...   | ...     | ...  | ...       | ...     | ...     | Yes / No   |

## Decision

**PASS** — {best_pair} on {model}/{dataset}: diff={val:.4f}, CI=[{lo:.4f}, {hi:.4f}]
OR
**FAIL** — No pairwise difference meets criterion. Next step: 10-sample dry run, route to Phase 2A.

## Notes

- Seed: 42
- Bootstrap n_resamples: 1000
- Models: llama2 (meta-llama/Llama-2-7b-hf), mistral (mistralai/Mistral-7B-v0.1)
- Datasets: trivia_qa, nq, truthful_qa
```

---

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Experiment Config Dataclass + Output Schemas | Frozen `ExperimentConfig` dataclass, YAML equivalent, CSV/NPZ/MD output schemas |
