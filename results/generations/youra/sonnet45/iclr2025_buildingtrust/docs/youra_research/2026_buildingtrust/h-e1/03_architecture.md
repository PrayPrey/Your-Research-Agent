# Architecture: H-E1 — Confidence Margin Predicts Argmax Flip (EXISTENCE PoC)

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-17

Applied: inference-pipeline pattern (green-field; Archon KB domain mismatch — diffusion models only, similarity < 0.42)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Foundation hypothesis with no prerequisites.

---

## Overview

Pure inference + statistical analysis pipeline. No model training. Minimal EXISTENCE PoC structure.

**Research claim**: Pre-alignment confidence margin (top-1 minus top-2 log-prob, z-scored) predicts post-alignment argmax flip probability. Gate: β₁ < 0, p < 0.005, AUROC ≥ 0.75 cross-benchmark.

---

## File Structure

- `h-e1/code/config.py` — model pairs, dataset IDs, paths, seeds, thresholds
- `h-e1/code/data_loader.py` — HuggingFace dataset loading + MCQ prompt formatting
- `h-e1/code/model_runner.py` — logit extraction from AutoModelForCausalLM
- `h-e1/code/analysis_pipeline.py` — margin, flip, KL, logistic regression, AUROC
- `h-e1/code/visualization.py` — figures 1-4 saved to `h-e1/figures/`
- `h-e1/code/main.py` — orchestrator: run all steps, save results, verify gate
- `h-e1/cache/` — `.npy` files for extracted logprobs per model
- `h-e1/figures/` — output `.pdf` and `.png` figures
- `h-e1/results/` — `results.yaml` with β₁, p-value, AUROC per model pair

---

## Module Definitions

### Config (`h-e1/code/config.py`)

**Dependencies**: none

```python
MODEL_PAIRS: list[dict] = [
    {"pair_id": "pair1", "base": "allenai/tulu-2-7b",     "aligned": "allenai/tulu-2-ppo-7b", "method": "PPO"},
    {"pair_id": "pair2", "base": "allenai/tulu-2-7b",     "aligned": "allenai/tulu-2-dpo-7b", "method": "DPO"},
    {"pair_id": "pair3", "base": "EleutherAI/pythia-1.4b", "aligned": "...",                   "method": "PPO"},
    {"pair_id": "pair4", "base": "EleutherAI/pythia-6.9b", "aligned": "...",                   "method": "PPO"},
]

DATASETS: list[dict] = [
    {"name": "mmlu",       "hf_id": "cais/mmlu",          "config": "all",            "split": "test"},
    {"name": "truthfulqa", "hf_id": "truthful_qa",         "config": "multiple_choice","split": "validation"},
    {"name": "arc",        "hf_id": "allenai/ai2_arc",     "config": "ARC-Challenge",  "split": "test"},
]

CACHE_DIR: str = "h-e1/cache"
FIGURES_DIR: str = "h-e1/figures"
RESULTS_DIR: str = "h-e1/results"
SEED: int = 42

GATE_THRESHOLDS: dict = {
    "beta1_max": 0.0,        # β₁ must be < 0
    "pvalue_max": 0.005,
    "auroc_min": 0.75,
    "partial_eta2_min": 0.06,
}

TORCH_DTYPE: str = "float16"
DEVICE_MAP: str = "auto"
```

---

### DataLoader (`h-e1/code/data_loader.py`)

**Dependencies**: config

```python
class MCQDataLoader:
    def __init__(self, dataset_cfg: dict): ...

    def load(self) -> list[dict]: ...
    # Returns list of items with keys: question, choices, answer_idx

    def format_prompt(self, item: dict) -> str: ...
    # Returns: "Question: {q}\nA: {a}\nB: {b}\nC: {c}\nD: {d}\nAnswer:"

    def get_option_tokens(self, tokenizer) -> list[int]: ...
    # Returns token IDs for [" A", " B", " C", " D"]


def load_all_datasets(dataset_cfgs: list[dict]) -> dict[str, list[dict]]: ...
# Returns: {"mmlu": [...], "truthfulqa": [...], "arc": [...]}
```

---

### ModelRunner (`h-e1/code/model_runner.py`)

**Dependencies**: config, data_loader

```python
class ModelRunner:
    def __init__(self, model_id: str, torch_dtype: str = "float16", device_map: str = "auto"): ...

    def load(self) -> None: ...
    # Loads AutoModelForCausalLM + AutoTokenizer

    def extract_logprobs(
        self,
        dataset: list[dict],
        cache_path: str,
        batch_size: int = 1,
    ) -> np.ndarray: ...
    # Returns: (n_items, 4) array of log_softmax over option tokens
    # Saves to cache_path as .npy; loads from cache if exists

    def unload(self) -> None: ...
    # Deletes model from GPU memory


def run_pair_extraction(
    pair_cfg: dict,
    datasets: dict[str, list[dict]],
    cache_dir: str,
) -> dict[str, dict]:  ...
# Returns: {"mmlu": {"base": ndarray, "aligned": ndarray}, "truthfulqa": {...}, "arc": {...}}
```

---

### AnalysisPipeline (`h-e1/code/analysis_pipeline.py`)

**Dependencies**: config

```python
def compute_margin_and_flip(
    base_logprobs: np.ndarray,    # (n, 4)
    aligned_logprobs: np.ndarray, # (n, 4)
) -> tuple[np.ndarray, np.ndarray]:  ...
# Returns: (margin_z, flip) — both (n,)
# margin_z = zscore(top1 - top2 of base); flip = int(argmax_base != argmax_aligned)

def compute_kl_divergence(
    base_logprobs: np.ndarray,    # (n, 4)
    aligned_logprobs: np.ndarray, # (n, 4)
) -> np.ndarray: ...
# Returns: (n,) KL(base || aligned) over 4-option softmax distributions

def fit_logistic_regression(
    margin_z: np.ndarray,  # (n,)
    kl_div: np.ndarray,    # (n,)
    flip: np.ndarray,      # (n,)
) -> dict: ...
# Returns: {"beta1": float, "beta0": float, "pvalue_beta1": float,
#           "auroc": float, "partial_eta2": float, "lr_model": LogisticRegression}

def evaluate_cross_benchmark(
    lr_model,
    datasets_logprobs: dict[str, dict],
    train_dataset: str = "mmlu",
) -> dict[str, float]: ...
# Returns: {"truthfulqa": auroc, "arc": auroc}

def verify_pipeline_activated(
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
    margin_z: np.ndarray,
    flip: np.ndarray,
    beta1: float,
    auroc: float,
) -> tuple[bool, dict[str, bool]]: ...
# Returns: (all_pass, {indicator_name: bool})

def run_full_analysis(
    pair_cfg: dict,
    datasets_logprobs: dict[str, dict],
) -> dict: ...
# Returns full results dict for one model pair
```

---

### Visualization (`h-e1/code/visualization.py`)

**Dependencies**: config, analysis_pipeline

```python
def plot_gate_metrics(results_all_pairs: list[dict], save_dir: str) -> None: ...
# Figure 1: bar chart β₁ value, AUROC target vs actual, p-value marker

def plot_quintile_flip_rates(
    margin_z: np.ndarray,
    flip: np.ndarray,
    pair_id: str,
    save_dir: str,
) -> None: ...
# Figure 2: 5-bin bar chart P(flip | margin quintile)

def plot_roc_curves(
    results_all_pairs: list[dict],
    cross_benchmark_results: dict,
    save_dir: str,
) -> None: ...
# Figure 3: per model pair + cross-benchmark ROC curves

def plot_margin_distribution(
    margin_z: np.ndarray,
    flip: np.ndarray,
    pair_id: str,
    save_dir: str,
) -> None: ...
# Figure 4: box plots margin distribution for flipped vs non-flipped


def save_all_figures(
    results_all_pairs: list[dict],
    figures_dir: str,
) -> None: ...
# Calls all plot functions; saves .pdf + .png for each
```

---

### Main Orchestrator (`h-e1/code/main.py`)

**Dependencies**: config, data_loader, model_runner, analysis_pipeline, visualization

```python
def main() -> None: ...
# Full pipeline:
# 1. Load all datasets (MMLU, TruthfulQA, ARC)
# 2. For each model pair:
#    a. Extract logprobs (base + aligned) for all 3 benchmarks — use cache if present
#    b. Run full analysis (margin, flip, KL, logistic regression, AUROC)
#    c. Verify pipeline activated
#    d. Run cross-benchmark evaluation
# 3. Aggregate results across all pairs
# 4. Generate and save all figures
# 5. Save results.yaml
# 6. Print gate check: PASS / FAIL with threshold values

def save_results(results: dict, results_dir: str) -> None: ...
# Serializes results dict to results.yaml

def print_gate_summary(results: dict, thresholds: dict) -> None: ...
# Prints β₁, p-value, AUROC per pair; PASS/FAIL for each gate criterion


if __name__ == "__main__":
    main()
```

---

## Data Flow

- `main.py` calls `load_all_datasets()` → list of items per benchmark
- `main.py` calls `run_pair_extraction()` for each model pair → logprob `.npy` cache
- `main.py` calls `run_full_analysis()` → β₁, p-value, AUROC, partial η²
- `main.py` calls `save_all_figures()` → `h-e1/figures/*.pdf`, `*.png`
- `main.py` calls `save_results()` → `h-e1/results/results.yaml`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown (M+D+A+I) |
|----|------|-------------|------------|----------------------|
| A-1 | Project Setup + Data Loading | Create file structure, config, implement DataLoader with MCQ prompt formatting for MMLU/TruthfulQA/ARC | 8 | 2+1+2+3 |
| A-2 | Model Inference + Logprob Extraction | Implement ModelRunner with float16 logit extraction, option token ID lookup, .npy caching | 12 | 3+2+3+4 |
| A-3 | Statistical Analysis Pipeline | Implement margin/flip/KL computation, logistic regression, AUROC, cross-benchmark eval, verify_pipeline_activated | 14 | 3+2+5+4 |
| A-4 | Visualization | Implement 4 required figures (gate metrics, quintile flip rate, ROC curves, margin distribution), save .pdf/.png | 9 | 2+2+2+3 |
| A-5 | Main Orchestrator + Gate Check | Wire full pipeline in main.py, result serialization to YAML, gate summary print | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-2, A-4], Low(4-8): [A-1, A-5]

---

## External Libraries

| Library | Version | Usage |
|---------|---------|-------|
| `torch` | >=2.0.0 | Tensor operations, float16 inference |
| `transformers` | >=4.35.0 | AutoModelForCausalLM, AutoTokenizer |
| `datasets` | >=2.14.0 | load_dataset for MMLU/TruthfulQA/ARC |
| `scikit-learn` | >=1.3.0 | LogisticRegression, roc_auc_score |
| `scipy` | >=1.11.0 | zscore, Wald test p-value |
| `numpy` | >=1.24.0 | Array operations, .npy I/O |
| `matplotlib` | >=3.7.0 | Figure generation |
| `seaborn` | >=0.12.0 | Box plots, bar charts |
| `statsmodels` | >=0.14.0 | Wald test for β₁ p-value |
| `pyyaml` | >=6.0 | results.yaml serialization |
| `tqdm` | >=4.65.0 | Progress bars during inference |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Module sections = interface code only
- [x] 5 Epic tasks with complexity scores (EXISTENCE PoC: 4-6 tasks)
- [x] Total length < 500 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field: Serena skip noted in Codebase Analysis
