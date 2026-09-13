# Architecture: H-E1 — Token-Level Log-Probability Aggregation Ablation

**Date:** 2026-08-21
**Hypothesis:** H-E1 (EXISTENCE / LIGHT)
**Applied:** single-file flat script pattern (no abstraction layers, direct sklearn/scipy calls)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing codebase to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. No prior code to reuse or align with.

---

## File Organization

```
docs/youra_research/h-e1/
    code/
        data_loader.py       # dataset loading + label extraction
        inference.py         # model loading + greedy forward pass + log-prob extraction
        aggregation.py       # min / mean / sum aggregation functions
        evaluation.py        # AUROC, AUPRC, ECE, bootstrap CI
        visualization.py     # ROC curves, score histograms
        run_experiment.py    # top-level orchestration
        config.py            # single fixed config (paths, model IDs, seeds)
    results/
        scores_{model}_{dataset}.npz
        auroc_table.csv
        bootstrap_ci_table.csv
        gate_decision_h-e1.md
    figures/
        roc_{model}_{dataset}.png
        hist_{model}_{dataset}_{method}.png
```

---

## Modules

### Config (`code/config.py`)

**Dependencies:** none

```python
MODELS = {
    "llama2": "meta-llama/Llama-2-7b-hf",
    "mistral": "mistralai/Mistral-7B-v0.1",
}
DATASETS = ["trivia_qa", "nq", "truthful_qa"]
AGGREGATIONS = ["min", "mean", "sum"]
SEED = 42
MAX_NEW_TOKENS = 50
BOOTSTRAP_N = 1000
RESULTS_DIR = "docs/youra_research/h-e1/results"
FIGURES_DIR = "docs/youra_research/h-e1/figures"
FARQUHAR_DATA_DIR = "data/semantic_uncertainty"  # cloned jlko/semantic_uncertainty
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies:** config, datasets, rouge-score, json

```python
def load_trivia_qa(farquhar_data_dir: str) -> list[dict]:
    """Returns list of {question, reference_answers, label} from trivia_qa_val.jsonl."""
    ...

def load_nq(farquhar_data_dir: str) -> list[dict]:
    """Returns list of {question, reference_answers, label} from nq_open_val.jsonl."""
    ...

def load_truthful_qa() -> list[dict]:
    """Returns list of {question, best_answer, label} using ROUGE-L >= 0.3 threshold."""
    ...

def get_dataset(name: str, farquhar_data_dir: str) -> list[dict]:
    """Dispatcher: name in {'trivia_qa', 'nq', 'truthful_qa'}."""
    ...
```

Each returned dict schema: `{"question": str, "label": int, "reference_answers": list[str]}`

---

### Inference (`code/inference.py`)

**Dependencies:** config, transformers, torch

```python
def load_model(model_key: str) -> tuple:
    """Load frozen fp16 model + tokenizer. Returns (model, tokenizer)."""
    ...

def extract_token_logprobs(
    model, tokenizer, prompt: str, max_new_tokens: int = 50
) -> list[float]:
    """Single greedy forward pass. Returns per-token log-probs for generated tokens only.
    Returns [] if no tokens generated (empty answer filtered upstream)."""
    ...

def run_inference(
    samples: list[dict], model, tokenizer
) -> list[dict]:
    """For each sample: extract log-probs, attach to record.
    Filters empty generations. Returns list of {question, label, logprobs}."""
    ...
```

---

### Aggregation (`code/aggregation.py`)

**Dependencies:** numpy

```python
def aggregate(logprobs: list[float], method: str) -> float:
    """method in {'min', 'mean', 'sum'}. Returns scalar confidence score (not negated)."""
    ...

def compute_all_scores(
    records: list[dict]
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Returns {method: (scores_array, labels_array)} for all three methods.
    Scores are negated (higher = more uncertain = predicted hallucinated)."""
    ...
```

---

### Evaluation (`code/evaluation.py`)

**Dependencies:** numpy, scikit-learn, scipy

```python
def compute_auroc(labels: np.ndarray, scores: np.ndarray) -> float: ...

def compute_auprc(labels: np.ndarray, scores: np.ndarray) -> float: ...

def compute_ece(labels: np.ndarray, scores: np.ndarray, n_bins: int = 15) -> float: ...

def bootstrap_auroc_diff(
    scores_a: np.ndarray, scores_b: np.ndarray, labels: np.ndarray,
    n_resamples: int = 1000
) -> tuple[float, float]:
    """Returns (ci_lower, ci_upper) for AUROC(a) - AUROC(b), percentile bootstrap."""
    ...

def evaluate_cell(
    labels: np.ndarray, scores: np.ndarray
) -> dict:
    """Returns {auroc, auprc, ece} for one (model x dataset x aggregation) cell."""
    ...

def compute_all_pairwise_ci(
    method_scores: dict[str, np.ndarray], labels: np.ndarray, n_resamples: int = 1000
) -> dict[str, tuple[float, float]]:
    """Returns {pair_key: (ci_lower, ci_upper)} for all 3 pairwise combos."""
    ...

def length_stratified_auroc(
    records: list[dict], method: str, threshold: int = 5
) -> dict:
    """Returns {short: auroc, long: auroc} split by answer token count."""
    ...

def check_gate(ci_table: dict) -> bool:
    """H-E1 pass: any pairwise diff >= 0.02 with CI lower bound > 0."""
    ...
```

---

### Visualization (`code/visualization.py`)

**Dependencies:** matplotlib, scikit-learn, numpy

```python
def plot_roc_curves(
    method_scores: dict[str, np.ndarray], labels: np.ndarray,
    model_key: str, dataset_name: str, out_dir: str
) -> None:
    """ROC curves for all 3 aggregation methods overlaid. Saved to out_dir."""
    ...

def plot_score_histograms(
    scores: np.ndarray, labels: np.ndarray,
    model_key: str, dataset_name: str, method: str, out_dir: str
) -> None:
    """Score histogram split by correct/hallucinated. Saved to out_dir."""
    ...
```

---

### Run Experiment (`code/run_experiment.py`)

**Dependencies:** all modules above, numpy, pandas, os

```python
def main() -> None:
    """
    Orchestrates full pipeline:
    1. For each model:
       a. load_model()
       b. For each dataset: load_dataset -> run_inference -> save scores .npz
    2. Compute metrics for all 18 cells -> auroc_table.csv
    3. Compute bootstrap CI for all pairwise diffs -> bootstrap_ci_table.csv
    4. Run length stratification ablation
    5. Generate ROC curves and histograms
    6. check_gate() -> write gate_decision_h-e1.md
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data Setup | Implement data_loader.py: load TriviaQA/NQ from Farquhar JSONL, TruthfulQA from HF hub; binary label extraction (exact-match + ROUGE-L) | 9 | 2+2+3+2 |
| E-2 | Inference Pipeline | Implement inference.py: fp16 model loading, greedy forward pass, log-prob extraction from output_scores; empty-generation filter | 11 | 3+2+4+2 |
| E-3 | Aggregation + Evaluation | Implement aggregation.py (min/mean/sum) + evaluation.py (AUROC/AUPRC/ECE, bootstrap CI, length stratification, gate check) | 10 | 2+2+4+2 |
| E-4 | Orchestration + Persistence | Implement run_experiment.py: full pipeline loop over 2 models × 3 datasets; save .npz scores, auroc_table.csv, bootstrap_ci_table.csv, gate_decision.md | 9 | 2+3+2+2 |
| E-5 | Visualization | Implement visualization.py: ROC curves (3 methods overlaid), score histograms split by label; save to figures/ | 6 | 2+1+2+1 |

**Distribution:** High(10-13): [E-2, E-3], Medium(7-9): [E-1, E-4], Low(4-6): [E-5]

---

## Module Dependency Graph

- `run_experiment.py` imports: config, data_loader, inference, aggregation, evaluation, visualization
- `evaluation.py` imports: numpy, scikit-learn, scipy
- `aggregation.py` imports: numpy
- `inference.py` imports: config, transformers, torch
- `data_loader.py` imports: config, datasets, rouge-score, json
- `visualization.py` imports: matplotlib, scikit-learn, numpy

---

## External Dependencies (Python Packages)

| Package | Version | Usage |
|---------|---------|-------|
| transformers | >=4.40.0 | Model loading, generation |
| datasets | >=2.18.0 | TruthfulQA loading |
| torch | >=2.2.0 | fp16 inference, no_grad |
| scikit-learn | >=1.4.0 | AUROC, AUPRC, calibration |
| scipy | >=1.11.0 | bootstrap CI |
| numpy | >=1.26.0 | array ops |
| rouge-score | >=0.1.2 | TruthfulQA label extraction |
| matplotlib | >=3.8.0 | plots |
| accelerate | >=0.29.0 | device_map for model loading |

External data: `git clone https://github.com/jlko/semantic_uncertainty` into `FARQUHAR_DATA_DIR`.
