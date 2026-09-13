# Architecture: H-M4 (Probe vs Output-Level Baselines)

Applied: single-pass uncertainty baselines (entropy/NLL) computed from generate() output_scores, no external UQ dependency needed

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3)
**Status**: Actual code inspected at `h-m3/code/` (specs in `03_architecture.md` were close but not exact)
**Analyzed Path**: `docs/youra_research/h-m3/code/`
**Findings**:
- H-M3 does **not** persist a probe checkpoint (no `joblib.dump`/pickle) — probe trained in-memory in `train.py::main()` and discarded after run. H-M4 must **retrain the identical probe** (same seed=42, C=1e-3, StandardScaler) rather than "load checkpoint from disk" as PRD FR-3 assumes.
- H-M1 cache path actually used: `h-m3/code/config.py::h_m1_cache_folder = "../h-m1/code/cache"`, files `train_hidden_states.pt` / `val_hidden_states.pt` (dict with `hidden_states`, `labels` keys). Shapes: train (9500,4096), val (1700,4096).
- `LinearCorrectnessProbe` (`h-m3/code/probe.py`) and `StandardScaler` logic (`h-m3/code/data.py::scale_features`) are directly reusable via import (same directory added to `sys.path`) or copy-in.
- No cached generation logits/entropy anywhere — token entropy & seq NLL must be computed fresh via live `model.generate()` on the val question set.

---

## File Organization

- `code/reuse_probe.py` - retrain H-M3 probe in-process (imports from h-m3/code) + reload val labels/hidden states
- `code/baselines.py` - token entropy + sequence NLL computation from generation
- `code/generate.py` - Llama-3-8B-Instruct generation loop over val questions, produces entropy/NLL arrays
- `code/evaluate.py` - AUROC per method, deltas, gate check
- `code/visualize.py` - gate bar chart, ROC overlay, distributions, scatter
- `code/run.py` - orchestration entrypoint
- `config.py` - hyperparameters/paths

---

## Modules

### ProbeReuse (`code/reuse_probe.py`)

**Dependencies**: h-m3/code (`probe.py`, `data.py`), numpy

```python
import sys
sys.path.insert(0, "../h-m3/code")
from probe import LinearCorrectnessProbe
from data import load_hidden_states, scale_features

def get_probe_scores(h_m1_cache_folder: str, seed: int = 42) -> tuple[np.ndarray, np.ndarray]: ...
    # returns (probe_val_scores, y_val); retrains probe identically to H-M3
```

### GenerationRunner (`code/generate.py`)

**Dependencies**: transformers, torch, datasets

```python
def load_model(model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct") -> tuple: ...  # (model, tokenizer)
def generate_with_scores(model, tokenizer, prompt: str, max_new_tokens: int = 50) -> dict: ...
    # returns {"text": str, "scores": Tensor[gen_len, vocab]}
def run_generation_batch(model, tokenizer, questions: list[dict], max_new_tokens: int = 50) -> list[dict]: ...
    # per-example: {"id", "scores", "generated_ids"}
```

### BaselineMetrics (`code/baselines.py`)

**Dependencies**: torch.nn.functional

```python
def compute_token_entropy(logits: torch.Tensor) -> float: ...   # mean per-token entropy
def compute_sequence_nll(logits: torch.Tensor, token_ids: torch.Tensor) -> float: ...  # avg NLL
def compute_all_baselines(gen_outputs: list[dict]) -> dict: ...
    # returns {"entropy_scores": np.ndarray, "nll_scores": np.ndarray} (both negated -> higher=more confident)
```

### Evaluator (`code/evaluate.py`)

**Dependencies**: sklearn.metrics.roc_auc_score, roc_curve

```python
def compute_auroc_all(probe_scores, entropy_scores, nll_scores, labels) -> dict: ...
    # {"probe_auroc","entropy_auroc","nll_auroc"}
def compute_deltas(aurocs: dict) -> dict: ...
    # {"delta_entropy","delta_nll"}
def check_gate(deltas: dict, threshold: float = 0.05) -> dict: ...
```

### Visualizer (`code/visualize.py`)

**Dependencies**: matplotlib, sklearn.metrics.roc_curve

```python
def plot_gate_comparison(aurocs: dict, threshold: float, out_path: str) -> None: ...
def plot_roc_overlay(labels, probe_scores, entropy_scores, nll_scores, out_path: str) -> None: ...
def plot_confidence_distributions(labels, probe_scores, entropy_scores, out_path: str) -> None: ...
def plot_score_scatter(probe_scores, entropy_scores, labels, out_path: str) -> None: ...
```

### Orchestrator (`code/run.py`)

**Dependencies**: all modules above

```python
def main(hypothesis_folder: str) -> dict: ...  # returns results dict, writes results.json + figures/
```

### Config (`config.py`)

```python
SEED = 42
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
H_M1_CACHE_FOLDER = "../h-m3/../h-m1/code/cache"  # verified from h-m3/code/config.py
H_M3_CODE_PATH = "../h-m3/code"
N_VAL = 1700
MAX_NEW_TOKENS = 50
DELTA_GATE = 0.05
PROBE_AUROC_MIN = 0.88
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| LinearCorrectnessProbe | `from probe import LinearCorrectnessProbe` (after `sys.path.insert(0, "../h-m3/code")`) | `h-m3/code/probe.py` |
| DataModule | `from data import load_hidden_states, scale_features` | `h-m3/code/data.py` |
| H-M1 cache | N/A (data, not code) | `h-m1/code/cache/{train,val}_hidden_states.pt` |

**Verified from**: `docs/youra_research/h-m3/code/` (actual implementation, not `03_architecture.md` spec — spec's `code/train.py` path for cache was confirmed correct: `h_m1_cache_folder: str = "../h-m1/code/cache"`)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Reuse H-M3 probe | Import probe.py/data.py, retrain identically, get val scores+labels | 8 | 2+3+2+1 |
| B-2 | Model loading | Load Llama-3-8B-Instruct + tokenizer | 5 | 2+2+1+0 |
| B-3 | Generation loop | Batch generate over 1700 val questions with output_scores | 10 | 3+2+3+2 |
| B-4 | Token entropy computation | Softmax/log_softmax entropy per token, mean over sequence | 6 | 1+1+3+1 |
| B-5 | Sequence NLL computation | Gather log-probs of generated tokens, average, negate | 6 | 1+1+3+1 |
| B-6 | Correctness labeling | Exact-match scoring of generated text vs gold answers | 6 | 2+1+2+1 |
| B-7 | AUROC + delta computation | roc_auc_score per method, deltas, gate check | 5 | 1+2+1+1 |
| B-8 | Visualization suite | Gate bar chart, ROC overlay, distributions, scatter | 7 | 2+2+1+2 |
| B-9 | End-to-end orchestration | Wire run.py, save results.json + figures | 6 | 1+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-1,B-3], Low(4-8): [B-2,B-4,B-5,B-6,B-7,B-8,B-9]

---

## Notes

- Generation is the dominant cost (B-3): 1700 forward-generate passes on 8B model, no batching assumption relaxed (NFR-1 caps at 30 min single-GPU — batch generation strongly recommended in implementation, not architecturally mandated here).
- Correctness labels: PRD assumes reuse of H-M1/H-M3 labels, but those labels were computed against a *previously cached* generation (different run). B-6 explicitly recomputes exact-match against the *current* live generation to keep labels consistent with entropy/NLL scores (avoids label/score mismatch bug).
