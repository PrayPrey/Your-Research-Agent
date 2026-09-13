# Logic: h-m2 (Cross-Model Probe Transfer)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code (read directly; Serena project not registered for this path, used file tool fallback)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `SemanticEntropyProbe.__init__/extract_hidden_state/fit/predict_proba` (sep.py), `ModelWrapper.load/generate` (models.py), `MODELS/SEED/LAYER_FRACTION` (config.py), `load_truthfulqa/split_train_val` (data.py)

Applied: no direct Archon KB match for cross-model probe transfer (searched "cross-model representation transfer API patterns" — irrelevant hits); used least-squares affine-mapping-transfer pattern per architecture spec (Chen et al. 2025 model stitching).

---

## A-6: AffineAligner [Complexity: 8, Budget: 1]

**Applied**: least-squares affine mapping (source ≈ target @ W + b), standard numpy lstsq.

### API Signatures

```python
class AffineAligner:
    def __init__(self):
        self.W: np.ndarray | None = None  # [target_dim, source_dim]
        self.b: np.ndarray | None = None  # [source_dim]

    def fit(self, source_hidden: np.ndarray, target_hidden: np.ndarray) -> None:
        """Paired samples (same questions). source ~= target @ W + b."""

    def transform(self, target_hidden: np.ndarray) -> np.ndarray:
        """[N, target_dim] -> [N, source_dim]. No-op (return input) if unfit."""
```

### Pseudo-code

```
fit(source_hidden, target_hidden):        # source: [N, D_s], target: [N, D_t]
  X = hstack([target_hidden, ones([N, 1])])       # [N, D_t+1]
  Wb, *_ = np.linalg.lstsq(X, source_hidden, rcond=None)  # [D_t+1, D_s]
  self.W = Wb[:-1, :]                     # [D_t, D_s]
  self.b = Wb[-1, :]                      # [D_s]

transform(target_hidden):                 # [M, D_t]
  if self.W is None: return target_hidden
  return target_hidden @ self.W + self.b  # [M, D_s]
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| source_hidden (fit) | [N_train, D_s] | paired train split, source model dim |
| target_hidden (fit) | [N_train, D_t] | paired train split, target model dim (may differ, e.g. 3584 vs 4096) |
| target_hidden (transform) | [M, D_t] | val split |
| output | [M, D_s] | aligned to source space |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | AffineAligner fit/transform | lstsq fit on paired train hidden states; transform applies W,b; no-op fallback if unfit |

---

## A-8: build_transfer_matrix + compute_gap_stats [Complexity: 8, Budget: 1]

**Applied**: standard pairwise evaluation loop (no KB pattern; direct-then-aligned-fallback per PRD FR-4).

### API Signatures

```python
def build_transfer_matrix(
    probes: dict[str, "SemanticEntropyProbe"],
    hidden_val: dict[str, np.ndarray],
    labels_val: dict[str, np.ndarray],
    aligners: dict[tuple[str, str], "AffineAligner"],
) -> np.ndarray:
    """3x3 AUROC matrix. matrix[i][j] = probe_i evaluated on model_j's hidden states."""

def compute_gap_stats(matrix: np.ndarray, model_keys: list[str]) -> dict:
    """Returns {"mean_gap": float, "max_gap": float, "per_pair_gaps": dict[str, float]}."""
```

### Pseudo-code

```
build_transfer_matrix(probes, hidden_val, labels_val, aligners):
  keys = list(probes.keys())                       # 3 model keys
  matrix = zeros([3, 3])
  for i, src in enumerate(keys):
    for j, tgt in enumerate(keys):
      target_hidden = hidden_val[tgt]               # [n_val, D_tgt]
      if src == tgt:
        proba = probes[src].predict_proba(target_hidden)[:, 1]
      else:
        proba_direct = probes[src].predict_proba_safe(target_hidden)  # handles dim mismatch -> None
        gap_direct = None if proba_direct is None else abs(auroc(labels_val[tgt], proba_direct) - matrix[i][i])
        if proba_direct is not None and gap_direct <= 0.10:
          proba = proba_direct
        else:
          aligned = aligners[(src, tgt)].transform(target_hidden)  # [n_val, D_src]
          proba = probes[src].predict_proba(aligned)[:, 1]
      matrix[i][j] = roc_auc_score(labels_val[tgt], proba)
  return matrix                                     # [3, 3]

compute_gap_stats(matrix, model_keys):
  diag = diagonal(matrix)                           # [3] baselines
  pair_gaps = {}
  for i, src in enumerate(model_keys):
    for j, tgt in enumerate(model_keys):
      if i != j:
        pair_gaps[f"{src}->{tgt}"] = abs(matrix[i][j] - diag[i])
  gaps = list(pair_gaps.values())                   # len=6
  return {"mean_gap": mean(gaps), "max_gap": max(gaps), "per_pair_gaps": pair_gaps}
```

Note: `predict_proba_safe` raises/returns None when `target_hidden.shape[1] != probe.n_features_in_` (dim mismatch, e.g. Qwen 3584 vs Llama/Mistral 4096) — forces aligned path per PRD FR-4 ("required for Qwen pairs").

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| hidden_val[model] | [n_val, D_model] | D: 4096 (llama/mistral) or 3584 (qwen) |
| matrix | [3, 3] | rows=train model, cols=eval model, diagonal=baseline |
| pair_gaps values | len=6 | off-diagonal only |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Transfer matrix + gap stats | 9-cell AUROC matrix with direct/aligned fallback (gap>0.10 or dim mismatch triggers alignment); mean/max/per-pair gap aggregation |

---

## External Dependencies API (Base Hypothesis)

Verified from `docs/youra_research/h-e1/code/` (actual implementation):

```python
# From: h-e1/code/models.py
class ModelWrapper:
    def __init__(self, model_id: str): ...
    def load(self) -> None: ...
    def generate(self, question: str, n_samples: int, temperature: float = 1.0) -> list[str]: ...
    def get_hidden_states(self, question: str, layer_idx: int, token_position: str = "last") -> np.ndarray: ...

# From: h-e1/code/sep.py
class SemanticEntropyProbe:
    def __init__(self, layer_idx: int, token_position: str = "last"): ...
    def extract_hidden_state(self, model: ModelWrapper, question: str) -> np.ndarray: ...  # [hidden_dim]
    def fit(self, hidden_states: np.ndarray, labels: list[int]) -> None: ...               # hidden_states: [N, hidden_dim]
    def predict_proba(self, hidden_states: np.ndarray) -> np.ndarray: ...                  # -> [N, 2]

# From: h-e1/code/config.py
MODELS: dict        # {"llama3": {"id": ..., "n_layers": 32}, "mistral": {...}, "qwen2": {...}}
SEED: int = 42
LAYER_FRACTION: float = 2/3

# From: h-e1/code/data.py
def load_truthfulqa() -> "Dataset": ...
def split_train_val(data: "Dataset", train_frac: float, seed: int) -> tuple["Dataset", "Dataset"]: ...
```

h-m2 vendors these 4 files unchanged into `h-m2/code/` (per architecture File Organization).

---

## Total Subtasks: 2/2 used (budget exhausted: L-6-1, L-8-1)
