# Configuration: H-M4 (Bidirectional Tasks Show Miscalibrated Confidence)

**Format:** Python Dataclass (single file, `code/config.py`)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** Config verified from architecture's Codebase Analysis section (H-E1 `results.json` schema confirmed: `per_task` has `task_id, correct_logprob_norm, max_wrong_logprob_norm, inversion_score, is_inverted, cluster_label`; no `task_metadata` key — task text must be rejoined via `h-e1/code/data.py` loaders).
**Config Files Found:** `h-e1/code/config.py` (referenced for loader signatures only; no shared dataclass fields to inherit — H-M4 is a standalone analysis config).
**Pattern Used:** dataclass

Applied: analysis-pipeline config pattern (single dataclass, no training hyperparams)

---

## Config (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class H_M4_Config:
    # Paths
    e1_results_path: str = "../h-e1/code/outputs/results.json"
    output_dir: str = "outputs"
    results_path: str = "outputs/results.json"
    figures_dir: str = "../figures"

    # Feature keyword lists (FR-2)
    belief_markers: tuple = (
        "you think", "you believe", "your view", "your opinion",
        "you feel", "you assume", "you expect"
    )
    context_markers: tuple = (
        "in this context", "given that", "assuming",
        "depending on", "it depends", "situation"
    )
    hedge_markers: tuple = (
        "might be", "could be", "possibly", "sometimes",
        "it varies", "not always", "generally"
    )

    # Gate thresholds (from PRD/brief)
    r_threshold: float = 0.4      # point_biserial_r > 0.4 (primary)
    d_threshold: float = 0.3      # cohens_d > 0.3 (secondary, AND)
    partial_r_threshold: float = 0.3  # partial_r > 0.3 (secondary, AND)

    # Confound extraction (FR-3)
    # topic: one-hot over source datasets actually used in H-E1 (verified, not PRD names)
    topic_categories: tuple = ("tqa", "mmlu", "hh")
    format_categories: tuple = ("multiple_choice", "open_ended")

    # Cross-model (FR-5) — best-effort per architecture note (no per-model
    # cluster data in results.json; uses aggregate `models_evaluated` list)
    models: tuple = ("Llama-2-7B", "Llama-2-13B", "Mistral-7B")

    seed: int = 42
```

**Non-standard:** `topic_categories` uses `("tqa", "mmlu", "hh")` not PRD's stated `TruthfulQA/ETHICS/HHH` — architecture verified actual H-E1 datasets are TruthfulQA, MMLU moral_scenarios, Anthropic HH-RLHF.

---

## YAML Schema (optional override file, `code/config.yaml`)

```yaml
e1_results_path: "../h-e1/code/outputs/results.json"
output_dir: "outputs"
results_path: "outputs/results.json"
figures_dir: "../figures"

thresholds:
  r_threshold: 0.4
  d_threshold: 0.3
  partial_r_threshold: 0.3

topic_categories: ["tqa", "mmlu", "hh"]
format_categories: ["multiple_choice", "open_ended"]
models: ["Llama-2-7B", "Llama-2-13B", "Mistral-7B"]

seed: 42
```

Loaded via `yaml.safe_load` → merged into `H_M4_Config(**overrides)` if present; otherwise dataclass defaults apply (YAML is optional, not required for PoC run).

---

## Output File Format (`outputs/results.json`)

```json
{
  "metrics": {
    "point_biserial_r": 0.0,
    "point_biserial_p": 0.0,
    "cohens_d": 0.0,
    "partial_r": 0.0,
    "partial_p": 0.0
  },
  "gate_pass": false,
  "cross_model": {"Llama-2-7B": {}, "Llama-2-13B": {}, "Mistral-7B": {}},
  "n_tasks": 2212,
  "feature_prevalence_by_cluster": {},
  "seed": 42
}
```

---

## A-1 to A-9: Task-Level Config Notes

No per-task config variation needed — all 9 architecture tasks (A-1..A-9) consume the single `H_M4_Config` above. No hyperparameter sweep, no ablation configs (this is a MECHANISM/FULL-tier analysis experiment with fixed thresholds from PRD, not a PoC grid search).

| Task | Config fields used |
|------|--------------------|
| A-1 Data loading | `e1_results_path` |
| A-2 Feature scoring | `belief_markers`, `context_markers`, `hedge_markers` |
| A-3 Confound extraction | `topic_categories`, `format_categories` |
| A-4 Correlation analysis | (none — pure computation) |
| A-5 Gate check | `r_threshold`, `d_threshold`, `partial_r_threshold` |
| A-6 Cross-model | `models` |
| A-7/A-8 Visualization | `figures_dir` |
| A-9 Serialization | `results_path`, `seed` |
