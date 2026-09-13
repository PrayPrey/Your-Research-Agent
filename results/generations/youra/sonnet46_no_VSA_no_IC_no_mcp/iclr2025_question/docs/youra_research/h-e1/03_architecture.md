---
hypothesis_id: H-E1
phase: Phase 3
generated: 2026-08-25
author: yoon303@ust.ac.kr
---

# Architecture: H-E1 — SE vs TE AUROC Comparison

Applied: Kuhn et al. 2023 SE clustering pattern (bidirectional NLI entailment, logsumexp aggregation)
Applied: Bootstrap AUROC evaluation pattern (stratified resampling, 95% CI)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. h-e2-v2 samples reused as data inputs only; no h-e2-v2 code directory to analyze.

---

## File Organization

```
docs/youra_research/h-e1/
    code/
        run.py          # orchestrator + argparse CLI
        data.py         # data loading + h-e2-v2 sample loading
        compute_te.py   # token entropy computation
        compute_se.py   # semantic entropy computation (NLI clustering)
        evaluate.py     # AUROC, bootstrap, EM correctness, figures
    figures/            # output figures (auto-created)
    results/            # results.json, *.npy outputs (auto-created)
```

---

## Module Definitions

### DataLoader (`code/data.py`)

**Dependencies**: datasets, numpy, json

```python
def load_triviaqa(n: int = 98, seed: int = 42) -> list[dict]: ...
    # Returns list of {question_id, question, answers: list[str]}

def load_h_e2v2_samples(samples_path: str) -> dict[str, dict]: ...
    # Returns {question_id: {samples: list[str], log_probs: list[float]}}
    # Falls back to regeneration if path missing

def get_pilot_indices(dataset, n: int = 98, seed: int = 42) -> list[int]: ...
```

### TokenEntropy (`code/compute_te.py`)

**Dependencies**: torch, transformers, DataLoader

```python
def load_llama(model_id: str = "meta-llama/Llama-2-7b-hf") -> tuple: ...
    # Returns (model, tokenizer) in float16 with device_map="auto"

def compute_te_scores(
    questions: list[dict],
    model,
    tokenizer,
    device: str = "cuda"
) -> list[float]: ...
    # Greedy decode, extract logits, mean per-token Shannon entropy
    # TE = mean(-sum(p * log(p+1e-9), dim=-1)) over output tokens
```

### SemanticEntropy (`code/compute_se.py`)

**Dependencies**: transformers, numpy, DataLoader

```python
def load_nli_model(model_id: str = "cross-encoder/nli-deberta-v3-large"): ...
    # Returns HuggingFace pipeline("zero-shot-classification", device=0)

def get_semantic_ids(strings_list: list[str], nli_pipeline) -> list[int]: ...
    # Bidirectional entailment clustering (Kuhn et al. 2023)
    # Returns cluster assignment per sample

def compute_se_scores(
    questions: list[dict],
    samples_map: dict[str, dict],
    nli_pipeline,
) -> tuple[list[float], float]: ...
    # Returns (se_scores, avg_clusters)
    # logsumexp aggregation per cluster → Shannon entropy
```

### Evaluator (`code/evaluate.py`)

**Dependencies**: sklearn, numpy, matplotlib, seaborn, scipy

```python
def normalize_answer(s: str) -> str: ...
    # Lowercase, strip articles/punctuation (TriviaQA standard)

def em_correctness(
    predictions: list[str],
    references: list[list[str]]
) -> list[int]: ...

def bootstrap_auroc(
    y_true: np.ndarray,
    y_score: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42
) -> tuple[float, np.ndarray]: ...
    # Returns (mean_auroc, [ci_low, ci_high])

def verify_mechanism(
    te_scores: list[float],
    se_scores: list[float],
    correctness: list[int],
    avg_clusters: float
) -> tuple[bool, dict]: ...
    # Asserts avg_clusters > 1.5, mean(te) > 0, both classes present, |gap| < 0.30

def save_results(
    te_scores, se_scores, correctness,
    auroc_te, auroc_se,
    te_ci, se_ci,
    avg_clusters,
    out_dir: str
) -> None: ...
    # Writes results.json, te_scores.npy, se_scores.npy, correctness.npy

def plot_figures(
    te_scores, se_scores, correctness,
    auroc_te, auroc_se, te_ci, se_ci,
    bootstrap_te, bootstrap_se,
    figures_dir: str
) -> None: ...
    # Fig1: bar chart w/ CI; Fig2: ROC curves; Fig3: violin distributions; Fig4: bootstrap hist
```

### Orchestrator (`code/run.py`)

**Dependencies**: argparse, all modules above

```python
def parse_args() -> argparse.Namespace: ...
    # --samples-path, --n, --out-dir, --smoke-test (N=5), --seed, --skip-te

def smoke_test(args) -> None: ...
    # Runs N=5 questions end-to-end; asserts no crash

def main() -> None: ...
    # 1. Load data + h-e2-v2 samples
    # 2. Compute TE (load_llama → compute_te_scores)
    # 3. Compute SE (load_nli_model → compute_se_scores)
    # 4. EM correctness labels
    # 5. Bootstrap AUROC for TE and SE
    # 6. verify_mechanism assertions
    # 7. Print gap; trigger extension protocol if gap in [0.03, 0.05]
    # 8. save_results + plot_figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Data | Project structure, TriviaQA loading, h-e2-v2 sample loading with fallback | 7 | Module_Size:2 + Dependencies:2 + Algorithm:1 + Integration:2 |
| A-2 | Token Entropy | Load Llama-2-7B float16, greedy decode, logit extraction, mean per-token Shannon entropy | 14 | Module_Size:3 + Dependencies:4 + Algorithm:4 + Integration:3 |
| A-3 | Semantic Entropy | NLI pipeline, bidirectional entailment clustering, logsumexp aggregation, cluster entropy | 16 | Module_Size:4 + Dependencies:3 + Algorithm:5 + Integration:4 |
| A-4 | Evaluation & Metrics | EM correctness, bootstrap AUROC, mechanism verification, extension protocol logic | 12 | Module_Size:3 + Dependencies:3 + Algorithm:4 + Integration:2 |
| A-5 | Results & Figures | Save JSON/npy, 4 matplotlib figures (bar, ROC, violin, bootstrap hist) | 9 | Module_Size:3 + Dependencies:2 + Algorithm:1 + Integration:3 |
| A-6 | Orchestrator & CLI | run.py argparse CLI, smoke test mode, end-to-end wiring | 8 | Module_Size:2 + Dependencies:2 + Algorithm:1 + Integration:3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-3], Medium(9-13): [A-4, A-5], Low(4-8): [A-1, A-6]

**Total complexity**: 66 | **Task count**: 6 (within LIGHT tier 4-8 budget)

---

## Data Flow

- `data.py` → questions + samples_map
- `compute_te.py` ← questions → `te_scores`
- `compute_se.py` ← questions + samples_map → `(se_scores, avg_clusters)`
- `evaluate.py` ← te_scores + se_scores + correctness → auroc, CI, figures, results
- `run.py` orchestrates all; `--smoke-test` short-circuits to N=5

## Extension Protocol

If `gap in [0.03, 0.05]` after N=98: `run.py` auto-samples N=500 (seed=42, non-overlapping), regenerates K=10 samples for new questions, recomputes SE+TE, re-reports gap. Controlled by `--n 500` re-invocation or inline in `main()`.
