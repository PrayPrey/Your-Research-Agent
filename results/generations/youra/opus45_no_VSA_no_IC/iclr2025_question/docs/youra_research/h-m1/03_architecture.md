# Architecture: h-m1 (MECHANISM)

**Hypothesis:** Probe trained on TriviaQA (~11K) achieves AUROC >0.70 on TruthfulQA (cross-dataset transfer)

Applied: linear-probe-on-frozen-hidden-states pattern (reused from h-e1; Archon KB search "cross-dataset transfer learning probes" returned only unrelated diffusers training-loop pages, no applicable pattern).

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Serena had no active project registered for this session (`youra_research` project not selected); base code was inspected directly via file Read instead of Serena tools, satisfying the same requirement (actual implementation verified, not just specs).
**Analyzed Path:** `h-e1/code/` (config.py, models.py, sep.py, data.py, evaluate.py)
**Findings:** h-e1 code differs slightly from its own 03_architecture.md: `NLI_MODEL_ID` uses `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` (not `microsoft/deberta-v3-large-mnli`), `ModelWrapper.generate` hardcodes `max_new_tokens=100`, `SemanticEntropyProbe.extract_hidden_state` takes `(model, input_ids, attention_mask)` not raw hidden states, and `evaluate.py` has no `plot`/multi-family logic beyond gap check. h-m1 reuses `ModelWrapper` and `SemanticEntropyProbe` as-is; reimplements data loading (TriviaQA + TruthfulQA vs. TruthfulQA-only) and evaluation (raw AUROC vs. gap-based).

---

## File Structure

- `h-m1/code/config.py` — fixed config (model, datasets, seed, layer, paths)
- `h-m1/code/data.py` — TriviaQA (train) + TruthfulQA (eval) loading
- `h-m1/code/semantic_entropy.py` — SE label generation (reused logic from h-e1)
- `h-m1/code/train.py` — orchestration: extract features, train probe, evaluate, visualize
- `h-m1/code/evaluate.py` — AUROC + gate check (>0.70 pass, <0.60 fail)
- `h-m1/code/visualize.py` — ROC curve, layer analysis, calibration, distribution plots
- `h-m1/figures/` — output figures
- `h-m1/results/` — metrics JSON output

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
SEED = 42
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
N_LAYERS = 32
HIDDEN_DIM = 4096
TRAIN_DATASET = "trivia_qa"   # rc.nocontext, train[:11000]
EVAL_DATASET = "truthful_qa"  # generation, validation (817)
NLI_MODEL_ID = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"  # match h-e1 actual code
N_SAMPLES = 5
TEMPERATURE = 1.0
LAYER_IDX = -1  # default last layer; ablation sweeps [20..31]
TORCH_DTYPE = "float16"
DEVICE_MAP = "auto"
RESULTS_DIR = "h-m1/results"
FIGURES_DIR = "h-m1/figures"
```

### Data (`data.py`)

**Dependencies**: config

```python
def load_triviaqa(n_samples: int = 11000) -> "datasets.Dataset":
    """trivia_qa rc.nocontext train[:n_samples]."""
def load_truthfulqa() -> "datasets.Dataset":
    """truthful_qa generation validation split (817)."""
```

### SemanticEntropyLabels (`semantic_entropy.py`)

**Dependencies**: models.ModelWrapper (external, h-e1), config

```python
class SemanticEntropyLabels:
    def __init__(self, nli_model_id: str): ...
    def cluster_responses(self, responses: list[str]) -> list[int]: ...
    def compute_entropy(self, cluster_ids: list[int]) -> float: ...
    def compute_se_scores(self, model, questions: list[str]) -> list[float]:
        """generate(n_samples, temperature) -> cluster -> entropy, per question."""
    def binarize(self, se_scores: list[float]) -> list[int]:
        """Threshold at median (computed per-dataset)."""
    def correctness_labels(self, model, questions, references) -> list[int]:
        """Greedy-decode answer vs reference match -> binary correctness (for AUROC ground truth)."""
```

### Evaluate (`evaluate.py`)

**Dependencies**: sklearn.metrics

```python
def compute_auroc(y_true: list[int], y_pred_proba: "np.ndarray") -> float: ...
def check_gate(auroc: float) -> dict:
    """pass if auroc>0.70, fail if auroc<0.60, else inconclusive."""
def per_layer_auroc(probe_cls, hidden_states_by_layer: dict[int, "np.ndarray"],
                     train_labels, test_labels, test_layer_states) -> dict[int, float]:
    """Ablation: AUROC per layer for layer-analysis figure."""
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, sklearn.metrics.roc_curve, evaluate results

```python
def plot_gate_metric(auroc: float, threshold: float, out_path: str) -> None:
    """Mandatory: bar chart AUROC vs 0.70 threshold."""
def plot_roc_curve(y_true, y_pred_proba, out_path: str) -> None: ...
def plot_layer_analysis(layer_aurocs: dict[int, float], out_path: str) -> None: ...
def plot_calibration(y_true, y_pred_proba, out_path: str) -> None: ...
def plot_distribution_comparison(train_proba, eval_proba, out_path: str) -> None: ...
```

### Train / Orchestration (`train.py`)

**Dependencies**: data, semantic_entropy, evaluate, visualize, external ModelWrapper + SemanticEntropyProbe

```python
def main() -> None:
    """
    1. Load ModelWrapper(MODEL_ID), load TriviaQA(11k) + TruthfulQA(817).
    2. Compute SE labels + binarize on TriviaQA (train).
    3. Compute correctness labels on TruthfulQA (eval ground truth).
    4. Extract hidden states (LAYER_IDX, 'last') for train + eval via SEP.extract_hidden_state.
    5. probe = SemanticEntropyProbe(LAYER_IDX); probe.fit(train_hidden, train_se_binary).
    6. eval_proba = probe.predict_proba(eval_hidden)[:, 1].
    7. auroc = evaluate.compute_auroc(eval_correctness, eval_proba); gate = check_gate(auroc).
    8. Optional: per_layer_auroc ablation sweep for layer-analysis figure.
    9. Save results JSON, call all visualize.plot_* functions.
    """
```

---

## External Dependencies (Base Hypothesis: h-e1)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| ModelWrapper | `from h_e1.code.models import ModelWrapper` (or copy into `h-m1/code/models.py` if cross-hypothesis import unsupported) | `h-e1/code/models.py` |
| SemanticEntropyProbe | `from h_e1.code.sep import SemanticEntropyProbe` (or copy into `h-m1/code/sep.py`) | `h-e1/code/sep.py` |

**Verified from**: `h-e1/code/models.py`, `h-e1/code/sep.py` (actual implementation, read directly).

**Note**: `ModelWrapper.generate(prompt, n_samples, temperature)` hardcodes `max_new_tokens=100`; `SemanticEntropyProbe.extract_hidden_state(model, input_ids, attention_mask)` requires a `ModelWrapper` instance with `.get_hidden_states`, not raw tensors. `SemanticEntropyProbe.predict_proba` returns full `(N,2)` proba array — h-m1 must index `[:, 1]`.

If cross-hypothesis Python imports are not wired in the project (no shared package), Phase 4 Coder should copy `models.py` and `sep.py` verbatim into `h-m1/code/`.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup + config | config.py, copy/import ModelWrapper + SemanticEntropyProbe from h-e1 | 5 | 1+2+1+1 |
| M-2 | Data pipeline | data.py: TriviaQA (11k) + TruthfulQA (817) loading | 6 | 2+2+1+1 |
| M-3 | SE label generation | semantic_entropy.py: generate 5 samples/question, NLI cluster, entropy, binarize, correctness labels | 13 | 3+3+4+3 |
| M-4 | Hidden state extraction (train+eval) | Run SEP.extract_hidden_state over TriviaQA + TruthfulQA at LAYER_IDX | 9 | 2+3+2+2 |
| M-5 | Probe training + cross-dataset eval | Fit probe on TriviaQA, predict on TruthfulQA, compute AUROC | 8 | 2+2+2+2 |
| M-6 | Gate check + evaluate.py | check_gate logic, JSON results output | 4 | 1+1+1+1 |
| M-7 | Layer ablation | per_layer_auroc sweep across candidate layers | 10 | 2+2+3+3 |
| M-8 | Visualization suite | gate bar chart, ROC curve, layer analysis, calibration, distribution plots | 9 | 3+2+2+2 |
| M-9 | Orchestration + integration | train.py main(): wire all modules end-to-end, run full pipeline | 12 | 3+4+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-3, M-4, M-7, M-8, M-9], Low(4-8): [M-1, M-2, M-5, M-6]
