# Architecture: H-M2
# Min vs. Mean Log-Prob Aggregation Sensitivity Across Distribution Types

**Hypothesis:** H-M2 (MECHANISM)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Prerequisite:** H-M1 (COMPLETED, PASSED)

Applied: incremental-extension (reuse H-M1/H-E1 inference pipeline, ablate aggregation function, add TruthfulQA + Spearman ρ analysis)

---

## Codebase Analysis

**Analyzed Path**: `docs/youra_research/h-m1/code/` and `docs/youra_research/h-e1/code/`

**Key findings:**
- H-E1 `run_inference()` returns records with `logprobs: List[float]` and `label: int` — directly reusable
- H-M1 results at `h-m1/results/` contain `.npz` caches with raw records including logprobs — reuse for LLaMA-2-7B TriviaQA/NQ
- H-M2 adds TruthfulQA inference + Mistral-7B-v0.1 on all three datasets
- Core new logic: aggregation function ablation (min/mean/sum) + Spearman ρ with bootstrap CI

---

## File Structure

```
h-m2/
  code/
    config.py          # paths, dataset list, model dict, aggregation methods, stat thresholds
    data_loader.py     # load TriviaQA/NQ/TruthfulQA; binary label generation
    inference.py       # load_model, extract_token_logprobs, run_inference (extends H-E1 pattern)
    aggregation.py     # min_score, mean_score, raw_sum; compute_all_scores
    analysis.py        # compute_spearman_with_ci, compute_auroc, compute_rho_differential, gate_check
    figures.py         # rho_differential_bar (mandatory), scatter, auroc_heatmap, dist_overlay
    run_hm2.py         # orchestration: load/infer → aggregate → analyze → cache → gate → figures
  results/
    logprobs_{model}_{dataset}.npy        # cached token log-prob arrays (N, max_T) with mask
    labels_{model}_{dataset}.npy          # cached binary labels (N,)
    scores_{model}_{dataset}.npz          # aggregated scores: min/mean/sum per sample
    results_summary.json                  # all Spearman ρ, AUROC, CI values
  figures/
    rho_differential_bar.png              # MANDATORY gate figure
    rho_scatter.png
    auroc_heatmap.png
    dist_overlay_{dataset}.png
  03_prd.md
  03_architecture.md   # this file
  03_logic.md
  03_config.md
```

---

## Modules

### Config (`code/config.py`)

**Dependencies**: None (stdlib only)

```python
import os

# Paths
H_M1_RESULTS_DIR: str    # absolute path to h-m1/results/ (log-prob cache source)
H_E1_CODE_DIR: str       # absolute path to h-e1/code/ (inference pipeline)
RESULTS_DIR: str         # h-m2/results/
FIGURES_DIR: str         # h-m2/figures/

# Datasets
DATASETS: list[str] = ["trivia_qa", "nq", "truthful_qa"]
N_SAMPLES: dict[str, int] = {"trivia_qa": 400, "nq": 400, "truthful_qa": 817}
FEW_SHOT_K: dict[str, int] = {"trivia_qa": 4, "nq": 4, "truthful_qa": 0}

# Models
MODELS: dict[str, str] = {
    "llama2": "meta-llama/Llama-2-7b-hf",
    "mistral": "mistralai/Mistral-7B-v0.1",
}
MODELS_TO_RUN: list[str] = ["llama2", "mistral"]

# Inference
MAX_NEW_TOKENS: int = 20
SEED: int = 42

# Aggregation
AGGREGATION_METHODS: list[str] = ["min", "mean", "raw_sum"]

# Statistical analysis
N_RESAMPLES_BOOTSTRAP: int = 1000
CONFIDENCE_LEVEL: float = 0.95
BOOTSTRAP_METHOD: str = "percentile"

# Sanity checks
MIN_GENERATED_TOKENS: int = 2
DEGENERATE_FRACTION_MAX: float = 0.05
```

---

### Data Loader (`code/data_loader.py`)

**Dependencies**: datasets (HuggingFace), numpy

```python
def load_dataset_samples(dataset_name: str, n_samples: int, seed: int) -> List[Dict]:
    """Load and subsample TriviaQA/NQ/TruthfulQA. Returns records with question + reference_answers."""

def score_triviaqa_nq(generated: str, reference_answers: List[str]) -> int:
    """Exact-match after normalization (lowercase, strip punct/articles). Returns 0 or 1."""

def score_truthfulqa(generated: str, best_answer: str) -> int:
    """Binary: ROUGE-L or substring match against best_answer field. Returns 0 or 1."""

def assign_labels(records: List[Dict], dataset_name: str) -> List[Dict]:
    """Attach label field to each record based on dataset-appropriate scoring."""
```

---

### Inference (`code/inference.py`)

**Dependencies**: transformers, torch, numpy

```python
def load_model(model_id: str) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load frozen fp16 model via device_map='auto'. Sets eval mode."""

def extract_token_logprobs(
    model, tokenizer, prompt: str, max_new_tokens: int = 20
) -> np.ndarray:
    """Single greedy forward pass. Returns shape (T,) log-probs; T = generated tokens."""

def run_inference(
    samples: List[Dict], model, tokenizer,
    few_shot_k: int, max_new_tokens: int, dataset_name: str
) -> List[Dict]:
    """Run inference over all samples. Returns records with logprobs + generated_text."""

def load_or_run_inference(
    dataset_name: str, model_key: str, config
) -> Tuple[List[np.ndarray], List[int]]:
    """Cache-first: try H-M1/H-E1 .npy cache, then re-run. Returns (logprob_arrays, labels)."""
```

---

### Aggregation (`code/aggregation.py`)

**Dependencies**: numpy

```python
def min_score(lp: np.ndarray) -> float:      # np.min(lp)
def mean_score(lp: np.ndarray) -> float:     # np.mean(lp)
def raw_sum(lp: np.ndarray) -> float:        # np.sum(lp)

def compute_all_scores(
    logprob_arrays: List[np.ndarray]
) -> Dict[str, np.ndarray]:
    """Returns {"min": (N,), "mean": (N,), "raw_sum": (N,)} arrays."""
```

---

### Analysis (`code/analysis.py`)

**Dependencies**: scipy, sklearn, numpy

```python
def compute_spearman_with_ci(
    scores: np.ndarray, labels: np.ndarray,
    n_resamples: int = 1000, ci: float = 0.95
) -> Tuple[float, float, ConfidenceInterval]:
    """Returns (rho, p_value, bootstrap_ci)."""

def compute_auroc(scores: np.ndarray, labels: np.ndarray) -> float:
    """roc_auc_score(labels, -scores); negated since lower score = more hallucinated."""

def compute_rho_differential(
    scores_min: np.ndarray, scores_mean: np.ndarray, labels: np.ndarray,
    n_resamples: int = 1000
) -> Dict:
    """Returns {diff, ci_low, ci_high} for rho(min) - rho(mean)."""

def gate_check(results: Dict) -> Dict:
    """
    P1: rho(min, triviaqa/nq) > rho(mean, triviaqa/nq) for >=1 model
    P2: rho(mean, truthfulqa) > rho(min, truthfulqa) for >=1 model
    Returns {gate: PASS/PARTIAL_PASS/FAIL, p1_met: bool, p2_met: bool}
    """
```

---

### Figures (`code/figures.py`)

**Dependencies**: matplotlib, numpy, analysis

```python
def plot_rho_differential_bar(results: Dict, save_path: str) -> None:
    """MANDATORY. Bar chart: rho(min)-rho(mean) per (model, dataset), 95% CI error bars."""

def plot_rho_scatter(results: Dict, save_path: str) -> None:
    """Scatter: rho(min) vs rho(mean) per dataset/model; peaked vs flat benchmark clusters."""

def plot_auroc_heatmap(results: Dict, save_path: str) -> None:
    """Heatmap: 3 aggregations x 3 datasets x 2 models AUROC values."""

def plot_dist_overlay(logprob_arrays, labels, dataset_name: str, save_path: str) -> None:
    """Token log-prob distribution histograms: hallucinated vs correct per dataset."""

def save_all_figures(results: Dict, logprob_cache: Dict, figures_dir: str) -> None:
    """Generate and save all figures. Bar chart always runs; others best-effort."""
```

---

### Run Experiment (`code/run_hm2.py`)

**Dependencies**: all modules above

```python
def run_model_dataset(
    model_key: str, dataset_name: str, config
) -> Dict:
    """Full pipeline for one (model, dataset) pair. Returns analysis results dict."""

def main() -> None:
    """Outer loop: for each (model, dataset) → infer → aggregate → analyze → cache → gate → figures."""

if __name__ == "__main__":
    main()
```

---

## Data Flow

```
HuggingFace datasets
    ↓ data_loader.load_dataset_samples()
List[Dict] (question, reference_answers)
    ↓ inference.load_or_run_inference()
       ├─ Path A: load h-m1/results/logprobs_{model}_{dataset}.npy  [LLaMA-2-7B TriviaQA/NQ]
       └─ Path B: run_inference() → extract_token_logprobs() per sample
List[np.ndarray] shape (T_i,) per sample  +  labels (N,)
    ↓ aggregation.compute_all_scores()
{"min": (N,), "mean": (N,), "raw_sum": (N,)}  per (model, dataset)
    ↓ analysis.compute_spearman_with_ci() + compute_auroc() + compute_rho_differential()
results_summary.json  +  scores_{model}_{dataset}.npz
    ↓ analysis.gate_check()
{gate: PASS/PARTIAL_PASS/FAIL, p1_met, p2_met}
    ↓ figures.save_all_figures()
h-m2/figures/*.png
```

---

## Tensor Shapes

| Variable | Shape | Dtype | Notes |
|----------|-------|-------|-------|
| `token_logprobs` per sample | `(T_i,)` | float32 | T_i = generated tokens for sample i; all ≤ 0.0 |
| `logprob_arrays` | `List[(T_i,)]` | float32 | Variable length per sample |
| `scores["min"]` | `(N,)` | float64 | N = samples in dataset split |
| `scores["mean"]` | `(N,)` | float64 | Same |
| `scores["raw_sum"]` | `(N,)` | float64 | Same |
| `labels` | `(N,)` | int | 0=hallucinated, 1=correct |
| Spearman ρ | scalar | float | range [-1, 1] |
| Bootstrap CI | `(2,)` | float | (low, high) |

---

## H-M1 Cache Reuse Interface

```python
# Load cached LLaMA-2-7B log-probs from H-M1 results
import numpy as np

cache_path = f"{H_M1_RESULTS_DIR}/logprobs_llama2_{dataset}.npy"
if os.path.exists(cache_path):
    logprob_arrays = list(np.load(cache_path, allow_pickle=True))
    labels = np.load(f"{H_M1_RESULTS_DIR}/labels_llama2_{dataset}.npy")
else:
    # fallback: re-run inference
```

---

## Gate Check Logic

```python
def gate_check(results):
    p1_met = any(
        results[model]["trivia_qa"]["rho_min"] > results[model]["trivia_qa"]["rho_mean"]
        for model in results
    ) or any(
        results[model]["nq"]["rho_min"] > results[model]["nq"]["rho_mean"]
        for model in results
    )
    p2_met = any(
        results[model]["truthful_qa"]["rho_mean"] > results[model]["truthful_qa"]["rho_min"]
        for model in results
    )
    if p1_met and p2_met:
        return {"gate": "PASS"}
    elif p1_met or p2_met:
        return {"gate": "PARTIAL_PASS", "p1_met": p1_met, "p2_met": p2_met}
    else:
        return {"gate": "FAIL"}
```

---

## Epic Tasks

| ID | Task | Description | Complexity |
|----|------|-------------|------------|
| A-1 | Setup & Config | config.py + directory init | 3 |
| A-2 | Data Loader | load TriviaQA/NQ/TruthfulQA, label assignment | 6 |
| A-3 | Inference Pipeline | load_model, extract_token_logprobs, run_inference | 8 |
| A-4 | Cache Load/Save | load_or_run_inference: H-M1 cache → H-E1 fallback → re-run | 6 |
| A-5 | Aggregation Module | min/mean/raw_sum; compute_all_scores | 3 |
| A-6 | Statistical Analysis | Spearman ρ + bootstrap CI + AUROC + rho differential | 7 |
| A-7 | Gate Evaluation | gate_check logic + results_summary.json | 4 |
| A-8 | Figures | rho_bar (mandatory), scatter, AUROC heatmap, dist overlays | 8 |
| A-9 | Orchestration | run_model_dataset + main loop | 5 |
