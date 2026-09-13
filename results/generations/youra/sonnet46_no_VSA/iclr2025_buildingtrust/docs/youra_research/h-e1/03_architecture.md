# Architecture: H-E1 — Transformer Δ*-Vector Fingerprinting

**Hypothesis Type**: EXISTENCE (PoC)
**Date**: 2026-07-29
**Applied**: HuggingFace Trainer + AutoModelForSequenceClassification pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior codebase. Serena skipped per green-field rule.

---

## Module Overview

All modules live under `h-e1/code/`. Each is independently runnable (CLI entry points in `__main__`).

- `data_loader.py` — dataset loading (AdvGLUE, ANLI-R3, CheckList, GLUE clean)
- `fine_tuner.py` — HuggingFace Trainer-based fine-tuning for all model families
- `evaluator.py` — clean + adversarial accuracy evaluation
- `delta_star.py` — Δ* computation, reliability filter, vector construction
- `statistical_analysis.py` — mixed-effects, permutation MANOVA, bootstrap CI, LOMO
- `visualizer.py` — all figure generation
- `run_experiment.py` — orchestration

---

## Module Interfaces

### DataLoader (`h-e1/code/data_loader.py`)

**Dependencies**: `datasets`, `checklist`

```python
GLUE_TASKS = ["sst2", "mnli", "qqp", "qnli", "rte"]

def load_adv_glue() -> dict[str, Dataset]: ...
    # Returns {task: HF Dataset} for all 5 tasks

def load_glue_clean() -> dict[str, Dataset]: ...
    # Returns {task: HF Dataset validation splits}

def load_anli_r3() -> Dataset: ...
    # Returns facebook/anli test_r3 (1200 examples)

def load_checklist_suites() -> list[dict]: ...
    # Returns list of {name, examples, labels} from checklist pip package

def get_num_labels(task: str) -> int: ...
    # sst2->2, mnli->3, qqp->2, qnli->2, rte->2
```

---

### FineTuner (`h-e1/code/fine_tuner.py`)

**Dependencies**: `transformers`, `datasets`, DataLoader

```python
MODEL_CONFIGS = {
    "bert-base-uncased":                  {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "roberta-base":                       {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "google/electra-base-discriminator":  {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "albert-base-v2":                     {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "gpt2":                               {"lr": 5e-5, "batch": 16, "family": "decoder"},
    "facebook/opt-125m":                  {"lr": 5e-5, "batch": 16, "family": "decoder"},
    "facebook/opt-350m":                  {"lr": 5e-5, "batch": 16, "family": "decoder"},
    "t5-base":                            {"lr": 1e-4, "batch": 32, "family": "enc_dec"},
    "facebook/bart-base":                 {"lr": 1e-4, "batch": 32, "family": "enc_dec"},
}

def finetune_model(
    model_id: str,
    task: str,
    train_dataset: Dataset,
    eval_dataset: Dataset,
    output_dir: str,
    seed: int = 42,
) -> tuple[str, float]: ...
    # Returns (checkpoint_path, clean_accuracy)

def finetune_all(
    model_ids: list[str],
    tasks: list[str],
    data: dict,
    checkpoint_dir: str,
    seed: int = 42,
) -> dict[str, dict[str, tuple[str, float]]]: ...
    # Returns {model_id: {task: (ckpt_path, clean_acc)}}

def load_pretrained_glue_checkpoint(model_id: str, task: str) -> str | None: ...
    # Returns HF Hub checkpoint ID if available (BERT/RoBERTa shortcuts), else None
```

---

### Evaluator (`h-e1/code/evaluator.py`)

**Dependencies**: `transformers`, `datasets`, DataLoader

```python
ATTACK_CATEGORIES: list[str]  # C1-C11 + ANLI-R3 + CheckList categories

def evaluate_on_dataset(
    model_path: str,
    tokenizer_id: str,
    dataset: Dataset,
    task: str,
    batch_size: int = 32,
) -> float: ...
    # Returns accuracy

def evaluate_adv_glue(
    model_path: str,
    tokenizer_id: str,
    adv_data: dict[str, Dataset],
) -> dict[str, float]: ...
    # Returns {attack_category: adv_accuracy}

def evaluate_anli_r3(
    model_path: str,
    tokenizer_id: str,
    dataset: Dataset,
) -> float: ...

def evaluate_checklist(
    model_path: str,
    tokenizer_id: str,
    suites: list[dict],
) -> dict[str, float]: ...
    # Returns {suite_name: accuracy}

def run_all_evaluations(
    finetuned: dict[str, dict[str, tuple[str, float]]],
    adv_data: dict,
    anli_data: Dataset,
    checklist_suites: list[dict],
) -> dict: ...
    # Returns {model_id: {attack_category: {clean_acc, adv_acc}}}
```

---

### DeltaStar (`h-e1/code/delta_star.py`)

**Dependencies**: `numpy`, `scipy`, Evaluator output

```python
def compute_delta_star(clean_acc: float, adv_acc: float) -> float: ...
    # (clean - adv) / clean; returns 0.0 if clean == 0

def split_half_reliability(scores_half1: np.ndarray, scores_half2: np.ndarray) -> float: ...
    # Spearman-Brown corrected: (2r) / (1+r)

def filter_reliable_categories(
    results: dict,
    min_r: float = 0.7,
    min_n: int = 50,
) -> list[str]: ...
    # Returns attack categories passing reliability filter

def build_delta_star_vectors(
    results: dict,
    reliable_categories: list[str],
) -> tuple[np.ndarray, list[str], list[str]]: ...
    # Returns (X: [n_models, n_cats], model_ids, family_labels)
```

---

### StatisticalAnalysis (`h-e1/code/statistical_analysis.py`)

**Dependencies**: `statsmodels`, `scipy`, `sklearn`, `numpy`, DeltaStar output

```python
def run_mixed_effects(
    df: pd.DataFrame,
    formula: str = "delta_star ~ arch_family * attack_type + objective + tokenizer + clean_acc",
    group_var: str = "model_id",
) -> dict: ...
    # Returns {coef, pvalues, aic}

def bootstrap_interaction_ci(
    df: pd.DataFrame,
    n_iter: int = 1000,
    seed: int = 42,
) -> dict[str, tuple[float, float]]: ...
    # Returns {term: (ci_low, ci_high)}

def permutation_manova(
    X: np.ndarray,
    y: np.ndarray,
    n_permutations: int = 1000,
    seed: int = 42,
) -> dict[str, float]: ...
    # Returns {eta_squared, p_value}

def lomo_classify(
    X: np.ndarray,
    family_labels: list[str],
) -> tuple[float, np.ndarray]: ...
    # Returns (accuracy, confusion_matrix) — cosine KNN k=1 LOMO

def run_all_analyses(
    X: np.ndarray,
    model_ids: list[str],
    family_labels: list[str],
    reliable_categories: list[str],
    results_raw: dict,
) -> dict: ...
    # Returns full results dict saved to h-e1/results/
```

---

### Visualizer (`h-e1/code/visualizer.py`)

**Dependencies**: `matplotlib`, `seaborn`, `numpy`, StatisticalAnalysis output

```python
def plot_delta_star_heatmap(
    X: np.ndarray,
    model_ids: list[str],
    category_labels: list[str],
    out_path: str,
) -> None: ...

def plot_reliability_scatter(
    reliability_scores: dict[str, float],
    threshold: float = 0.7,
    out_path: str = "h-e1/figures/reliability_scatter.png",
) -> None: ...

def plot_manova_eta(
    eta_per_category: dict[str, float],
    threshold: float = 0.15,
    out_path: str = "h-e1/figures/manova_eta.png",
) -> None: ...

def plot_lomo_confusion(
    confusion_matrix: np.ndarray,
    class_names: list[str],
    out_path: str = "h-e1/figures/lomo_confusion.png",
) -> None: ...

def plot_family_profiles(
    X: np.ndarray,
    family_labels: list[str],
    category_labels: list[str],
    out_path: str = "h-e1/figures/family_profiles.png",
) -> None: ...
```

---

### RunExperiment (`h-e1/code/run_experiment.py`)

**Dependencies**: All modules above

```python
def main(
    model_ids: list[str] = list(MODEL_CONFIGS.keys()),
    tasks: list[str] = GLUE_TASKS,
    checkpoint_dir: str = "h-e1/checkpoints",
    results_dir: str = "h-e1/results",
    figures_dir: str = "h-e1/figures",
    seed: int = 42,
    skip_finetuning: bool = False,  # use pre-trained HF Hub checkpoints
) -> None: ...
```

---

## File Structure

```
h-e1/
├── code/
│   ├── data_loader.py
│   ├── fine_tuner.py
│   ├── evaluator.py
│   ├── delta_star.py
│   ├── statistical_analysis.py
│   ├── visualizer.py
│   └── run_experiment.py
├── checkpoints/          # fine-tuned model checkpoints
├── results/              # JSON result files
└── figures/              # output visualizations
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | Implement data_loader.py + verify all 4 datasets load correctly | 8 | 2+2+1+3 |
| A-2 | Fine-tuning Pipeline | Implement fine_tuner.py for 8-9 models × 5 tasks; handle decoder/enc-dec edge cases | 16 | 4+3+4+5 |
| A-3 | Adversarial Evaluation | Implement evaluator.py; map AdvGLUE attack categories; CheckList integration | 14 | 3+4+4+3 |
| A-4 | Delta* + Reliability | Implement delta_star.py: Δ* formula, split-half reliability filter, vector builder | 10 | 2+2+4+2 |
| A-5 | Statistical Analysis | Implement statistical_analysis.py: mixed-effects, bootstrap CI, permutation MANOVA, LOMO | 17 | 3+3+5+4 (ponytail: bootstrap 1k iters is slow; reduce to 200 for PoC) |
| A-6 | Visualization + Orchestration | Implement visualizer.py (5 figures) + run_experiment.py end-to-end | 11 | 2+2+3+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-3, A-5], Medium(9-13): [A-4, A-6], Low(4-8): [A-1]

---

## Dependencies Between Modules

```
DataLoader
    └── FineTuner  →  Evaluator  →  DeltaStar  →  StatisticalAnalysis  →  Visualizer
                                                                              ↑
                                                              RunExperiment calls all
```

## Notes

- `skip_finetuning=True` in `run_experiment.py` loads pre-trained BERT/RoBERTa/ALBERT/ELECTRA from HuggingFace Hub — use for fast PoC iteration
- Seed=42 fixed throughout; single-run PoC
- Results persisted as JSON to `h-e1/results/` after each stage so pipeline is resumable
- ponytail: bootstrap at n=1000 may take 10-30 min; add `--n_bootstrap` CLI flag, default 200 for PoC, 1000 for gate condition check
