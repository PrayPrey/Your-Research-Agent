# Architecture: h-m2 (Cross-Model Probe Transfer)

Applied: affine-mapping-transfer-pattern (least-squares W,b alignment between representation spaces)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Actual implementation found and read directly (Serena project not registered for this path; read via file tool instead, per fallback)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: h-e1 provides `ModelWrapper` (models.py: load/generate/get_hidden_states), `SemanticEntropyProbe` (sep.py: extract_hidden_state/fit/predict_proba using sklearn LogisticRegression), `config.py` (MODELS dict, SEED=42, LAYER_FRACTION=2/3), `data.py` (load_truthfulqa/split_train_val). h-m2 reuses all four modules unchanged and adds transfer-specific logic (caching, affine alignment, transfer matrix).

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| ModelWrapper | `from base.models import ModelWrapper` | `h-e1/code/models.py` |
| SemanticEntropyProbe | `from base.sep import SemanticEntropyProbe` | `h-e1/code/sep.py` |
| MODELS, SEED, LAYER_FRACTION | `from base.config import MODELS, SEED, LAYER_FRACTION` | `h-e1/code/config.py` |
| load_truthfulqa, split_train_val | `from base.data import load_truthfulqa, split_train_val` | `h-e1/code/data.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, read directly)

Note: h-m2 code dir will vendor/copy these 4 files (`models.py`, `sep.py`, `config.py`, `data.py`) rather than cross-package import, consistent with sibling-hypothesis folder isolation.

---

## File Organization

- `code/config.py` — models, seed, paths (extends h-e1 config)
- `code/data.py` — reused from h-e1 (unchanged)
- `code/models.py` — reused from h-e1 (unchanged)
- `code/sep.py` — reused from h-e1 (unchanged)
- `code/cache.py` — hidden-state disk caching (NEW)
- `code/extract.py` — per-model hidden state extraction loop (NEW)
- `code/transfer.py` — affine alignment + transfer evaluation (NEW)
- `code/evaluate.py` — transfer matrix computation, gap stats (NEW)
- `code/visualize.py` — heatmap + gap bar chart (NEW)
- `code/train.py` — orchestrates full pipeline (NEW)
- `results/transfer_matrix.json`, `results/results.json`
- `figures/transfer_heatmap.png`, `figures/transfer_gap_bar.png`

---

## Modules

### HiddenStateCache (`code/cache.py`)

**Dependencies**: numpy, os

```python
class HiddenStateCache:
    def __init__(self, cache_dir: str): ...
    def path(self, model_key: str, split: str) -> str: ...
    def save(self, model_key: str, split: str, hidden: np.ndarray) -> None: ...
    def load(self, model_key: str, split: str) -> np.ndarray | None: ...
    def exists(self, model_key: str, split: str) -> bool: ...
```

### extract.py (functions)

**Dependencies**: ModelWrapper, SemanticEntropyProbe, HiddenStateCache, config.MODELS

```python
def get_layer_idx(n_layers: int, frac: float) -> int: ...

def extract_for_model(
    model_key: str, questions: list[str], split: str, cache: HiddenStateCache
) -> np.ndarray:
    """Load model, extract hidden states at 2/3 depth, cache to disk, unload model."""
```

### AffineAligner (`code/transfer.py`)

**Dependencies**: numpy

```python
class AffineAligner:
    def __init__(self): ...
    def fit(self, source_hidden: np.ndarray, target_hidden: np.ndarray) -> None:
        """Least-squares: source ~= target @ W + b (paired samples)."""
    def transform(self, target_hidden: np.ndarray) -> np.ndarray: ...
```

### TransferEvaluator (`code/transfer.py`)

**Dependencies**: SemanticEntropyProbe, AffineAligner, sklearn.roc_auc_score

```python
class TransferEvaluator:
    def __init__(self, probe: SemanticEntropyProbe): ...
    def evaluate_direct(self, target_hidden: np.ndarray, labels: list) -> float: ...
    def evaluate_aligned(
        self, target_hidden: np.ndarray, labels: list, aligner: AffineAligner
    ) -> float: ...
```

### evaluate.py (functions)

**Dependencies**: TransferEvaluator, numpy

```python
def build_transfer_matrix(
    probes: dict[str, SemanticEntropyProbe],
    hidden_val: dict[str, np.ndarray],
    labels_val: np.ndarray,
    aligners: dict[tuple[str, str], AffineAligner],
) -> np.ndarray:
    """3x3 AUROC matrix; diagonal = baseline, off-diag = transfer (aligned when dims mismatch)."""

def compute_gap_stats(matrix: np.ndarray) -> dict:
    """mean_gap, max_gap, per_pair_gaps."""
```

### visualize.py (functions)

**Dependencies**: matplotlib, evaluate.build_transfer_matrix

```python
def plot_transfer_heatmap(matrix: np.ndarray, model_names: list[str], out_path: str) -> None: ...
def plot_gap_bar(gap_stats: dict, out_path: str) -> None: ...
```

### train.py (orchestration)

**Dependencies**: all above + base.data, base.config

```python
def main() -> None:
    """
    1. Load TruthfulQA, split train/val (seed=42, reuse base.data)
    2. Binarize SE labels at median (reuse h-e1 SE computation via base module)
    3. For each of 3 models: extract+cache train/val hidden states (extract.py)
    4. Train 3 SEP probes on respective train hidden states (base.sep)
    5. For mismatched-dim pairs (Qwen<->Llama/Mistral): fit AffineAligner on train split
    6. Build 3x3 transfer matrix (direct; aligned fallback if gap>0.10)
    7. Compute gap stats, save results.json
    8. Generate heatmap + bar chart
    """
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + vendoring | Copy/adapt config.py, data.py, models.py, sep.py from h-e1 | 5 | 1+1+1+2 |
| A-2 | Hidden state cache | Implement HiddenStateCache (save/load NPY) | 5 | 2+1+1+1 |
| A-3 | SE label computation | Reuse h-e1 semantic_entropy.py to binarize labels at median | 6 | 2+2+1+1 |
| A-4 | Hidden state extraction | extract.py: per-model layer selection + extraction loop with sequential load/unload | 9 | 3+2+2+2 |
| A-5 | Per-model SEP training | Train 3 probes on cached train hidden states | 4 | 1+2+1+1 |
| A-6 | Affine aligner | Implement AffineAligner least-squares fit/transform | 8 | 3+1+3+1 |
| A-7 | Transfer evaluator | TransferEvaluator direct + aligned AUROC eval | 7 | 2+2+2+1 |
| A-8 | Transfer matrix + gap stats | build_transfer_matrix + compute_gap_stats over 9 evaluations | 8 | 2+3+2+1 |
| A-9 | Visualization | Heatmap + gap bar chart | 5 | 2+1+1+1 |
| A-10 | Pipeline orchestration | train.py end-to-end wiring, results.json output | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-6, A-8], Low(4-8): [A-1, A-2, A-3, A-5, A-7, A-9, A-10]
