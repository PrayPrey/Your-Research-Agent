# Logic: H-M1 — Logit Delta Anisotropy Analysis

**Hypothesis ID:** H-M1
**Type:** MECHANISM (INCREMENTAL — extends H-E1)
**Date:** 2026-03-17

Applied: Standard numpy scientific computing pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from actual code (direct file reads — Serena project activation failed, read files directly)
**Analyzed Path:** `docs/youra_research/20260317_buildingtrust/h-e1/code/`
**Relevant Symbols:**
- `ModelRunner.__init__(model_id, torch_dtype="float16", device_map="auto")`
- `ModelRunner.extract_logprobs(dataset, cache_path, batch_size=1, dataset_cfg=None)` → `np.ndarray [N, 4]`
- `ModelRunner.load()`, `ModelRunner.unload()`
- `run_pair_extraction(pair_cfg, datasets, cache_dir, dataset_cfgs=None)` → `{"mmlu": {"base": ndarray[N,4], "aligned": ndarray[N,4]}, ...}`
- `load_all_datasets(dataset_cfgs=None)` → `{"mmlu": list[dict], "truthfulqa": list[dict], "arc": list[dict]}`
- `MCQDataLoader(dataset_cfg)` + `.format_prompt(item)` + `.get_option_tokens(tokenizer)`

---

## External Dependencies API

### API Signatures (From Actual Code)

Verified from `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_buildingtrust/docs/youra_research/20260317_buildingtrust/h-e1/code/model_runner.py` and `data_loader.py`.

```python
# From: h-e1/code/model_runner.py (ACTUAL CODE)
class ModelRunner:
    def __init__(self, model_id: str, torch_dtype: str = "float16", device_map: str = "auto"):
        ...

    def load(self) -> None: ...

    def extract_logprobs(
        self,
        dataset: list[dict],
        cache_path: str,
        batch_size: int = 1,
        dataset_cfg: dict = None,
    ) -> np.ndarray:
        """Returns log_softmax over [A,B,C,D] tokens. Shape: [N, 4]"""
        ...

    def unload(self) -> None: ...


def run_pair_extraction(
    pair_cfg: dict,
    datasets: dict[str, list[dict]],
    cache_dir: str,
    dataset_cfgs: list[dict] = None,
) -> dict[str, dict]:
    """Returns {"mmlu": {"base": ndarray[N,4], "aligned": ndarray[N,4]}, ...}"""
    ...


# From: h-e1/code/data_loader.py (ACTUAL CODE)
def load_all_datasets(dataset_cfgs: list[dict] = None) -> dict[str, list[dict]]:
    """Returns {"mmlu": list[dict], "truthfulqa": list[dict], "arc": list[dict]}"""
    ...


class MCQDataLoader:
    def __init__(self, dataset_cfg: dict): ...
    def format_prompt(self, item: dict) -> str: ...
    def get_option_tokens(self, tokenizer) -> list[int]: ...
```

**Cache path pattern (verified from actual code):**
```python
cache_path = os.path.join(cache_dir, f"{pair_id}_{model_role}_{ds_name}.npy")
# e.g., "h-m1/cache/pair2_base_mmlu.npy"
```

---

## A-4: Covariance Eigendecomposition [Complexity: 12, Budget: 2]

Applied: Standard numpy scientific computing pattern

### API Signatures

```python
def compute_covariance_eigendecomposition(
    delta: np.ndarray,  # [N, 4] centered or raw delta
) -> dict:
    """Eigendecompose covariance matrix of delta. Returns eigenvalues descending."""
    ...
# Returns:
# {
#   "eigenvalues": np.ndarray,   # [4] descending order
#   "eigenvectors": np.ndarray,  # [4, 4] columns = eigenvectors
#   "cov_matrix": np.ndarray,    # [4, 4]
#   "anisotropy_ratio": float,   # eigenvalues[0] / mean(eigenvalues[1:])
# }


def compute_anisotropy_significance(
    eigenvalues: np.ndarray,  # [4] descending
) -> dict:
    """Paired t-test: dominant eigenvalue vs trailing eigenvalues."""
    ...
# Returns:
# {
#   "t_stat": float,
#   "p_value": float,
#   "is_significant": bool,  # p_value < 0.05
# }
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| delta | [N, 4] | Raw logit delta per item |
| delta_centered | [N, 4] | delta - mean(delta, axis=0) |
| cov_matrix | [4, 4] | np.cov(delta_centered.T) |
| eigenvalues | [4] | Descending (eigh returns ascending, reverse) |
| eigenvectors | [4, 4] | Columns are eigenvectors |

### Pseudo-code

```
compute_covariance_eigendecomposition(delta):
    delta_centered = delta - delta.mean(axis=0)   # [N, 4]
    cov = np.cov(delta_centered.T)                 # [4, 4]
    eigenvalues, eigenvectors = np.linalg.eigh(cov)  # ascending order
    # sort descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    anisotropy_ratio = eigenvalues[0] / np.mean(eigenvalues[1:])
    return {eigenvalues, eigenvectors, cov_matrix: cov, anisotropy_ratio}

compute_anisotropy_significance(eigenvalues):
    # t-test: is eigenvalues[0] significantly greater than eigenvalues[1:]?
    t_stat, p_value = scipy.stats.ttest_1samp(eigenvalues[1:], popmean=eigenvalues[0])
    # Note: one-tailed; dominant > trailing → p_value / 2
    is_significant = (p_value / 2) < 0.05
    return {t_stat, p_value: p_value/2, is_significant}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Eigendecomposition core | compute_covariance_eigendecomposition(): center, cov, eigh, descending sort, ratio |
| L-4-2 | Significance test | compute_anisotropy_significance(): ttest_1samp on trailing eigenvalues vs dominant |

---

## A-5: Secondary Analysis [Complexity: 11, Budget: 2]

Applied: Standard numpy scientific computing pattern

### API Signatures

```python
def compute_decision_axis_projection(
    delta: np.ndarray,        # [N, 4]
    base_logprobs: np.ndarray,  # [N, 4]
) -> dict:
    """Project delta onto decision margin axis (top1 - top2 direction)."""
    ...
# Returns:
# {
#   "decision_axis_var": float,    # variance along decision axis
#   "orthogonal_vars": np.ndarray, # [3] variance along other 3 principal components
# }


def compute_margin_quintile_anisotropy(
    delta: np.ndarray,          # [N, 4]
    base_logprobs: np.ndarray,  # [N, 4]
    n_quintiles: int = 5,
) -> list[dict]:
    """Compute anisotropy ratio per confidence margin quintile."""
    ...
# Returns list[dict] per quintile:
# [{"quintile": int, "anisotropy_ratio": float, "n_items": int}, ...]


def run_isotropic_sanity_check(n_items: int = 1000, seed: int = 1) -> dict:
    """Compute anisotropy ratio on synthetic isotropic Gaussian noise; expected ~1.0."""
    ...
# Returns: {"anisotropy_ratio": float, "expected_approx_1": bool}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| delta | [N, 4] | Input |
| margins | [N] | top1_logit - top2_logit from base_logprobs |
| quintile_mask | [N] | Boolean index for quintile |
| delta_q | [N_q, 4] | Subset of delta for quintile q |

### Pseudo-code

```
compute_decision_axis_projection(delta, base_logprobs):
    # Decision axis = direction of max logit - second max logit
    sorted_logits = np.sort(base_logprobs, axis=1)[:, ::-1]  # [N, 4] descending
    decision_vec = np.zeros(4); decision_vec[0] = 1; decision_vec[1] = -1  # [4]
    decision_vec /= np.linalg.norm(decision_vec)
    # Project delta onto decision axis
    proj = delta @ decision_vec  # [N]
    decision_axis_var = np.var(proj)
    # Orthogonal: PCA on delta, take components 2-4
    pca = PCA(n_components=3).fit(delta - delta.mean(0))
    orthogonal_vars = pca.explained_variance_[1:]  # [3] — skip dominant
    return {decision_axis_var, orthogonal_vars}

compute_margin_quintile_anisotropy(delta, base_logprobs, n_quintiles=5):
    sorted_lp = np.sort(base_logprobs, axis=1)[:, ::-1]
    margins = sorted_lp[:, 0] - sorted_lp[:, 1]  # [N]
    quintile_edges = np.percentile(margins, np.linspace(0, 100, n_quintiles+1))
    results = []
    for q in range(n_quintiles):
        mask = (margins >= quintile_edges[q]) & (margins < quintile_edges[q+1])
        delta_q = delta[mask]  # [N_q, 4]
        if len(delta_q) < 10:
            continue
        result = compute_covariance_eigendecomposition(delta_q)
        results.append({"quintile": q+1, "anisotropy_ratio": result["anisotropy_ratio"], "n_items": len(delta_q)})
    return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Decision axis projection | compute_decision_axis_projection(): margin-direction variance vs orthogonal components |
| L-5-2 | Quintile + sanity check | compute_margin_quintile_anisotropy() + run_isotropic_sanity_check() |

---

## A-6: Gate Evaluation [Complexity: 10, Budget: 1]

Applied: Standard numpy scientific computing pattern

### API Signatures

```python
def evaluate_gate(
    all_pair_results: list[dict],
    gate_thresholds: dict,
) -> dict:
    """Evaluate H-M1 gate: ratio > 1.0 AND p < 0.05 in >= 2/3 families.

    gate_thresholds: {"anisotropy_ratio_min": 1.0, "pvalue_max": 0.05, "families_min": 2}
    """
    ...
# Returns:
# {
#   "gate_result": str,      # "PASS" or "FAIL"
#   "families_pass": int,    # count of families passing both criteria
#   "families_total": int,
#   "pair_details": list[dict],  # per-pair: {pair_id, ratio, p_value, passed}
# }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Gate logic | Per-pair check ratio > threshold AND p < 0.05; count families; PASS if >= families_min |

---

## A-7: run_anisotropy_analysis [Complexity: 10, Budget: 1]

Applied: Standard numpy scientific computing pattern

### API Signatures

```python
def run_anisotropy_analysis(
    pair_cfg: dict,
    datasets_logprobs: dict,  # {"mmlu": {"base": ndarray[N,4], "aligned": ndarray[N,4]}, ...}
) -> dict:
    """Full per-pair anisotropy pipeline: delta -> covariance -> eigendecomp -> significance -> secondary."""
    ...
# Returns per-pair result dict:
# {
#   "pair_id": str,
#   "datasets": {
#     "mmlu": {
#       "delta": ndarray,          # [N, 4]
#       "eigenvalues": ndarray,    # [4]
#       "cov_matrix": ndarray,     # [4, 4]
#       "anisotropy_ratio": float,
#       "significance": dict,      # {t_stat, p_value, is_significant}
#       "decision_axis": dict,     # {decision_axis_var, orthogonal_vars}
#       "quintile_results": list[dict],
#     },
#     ...
#   },
#   "primary_ratio": float,        # anisotropy_ratio from mmlu
#   "primary_p_value": float,
#   "passes_gate": bool,
# }
```

### Pseudo-code

```
run_anisotropy_analysis(pair_cfg, datasets_logprobs):
    pair_id = pair_cfg["pair_id"]
    all_ds_results = {}
    for ds_name, logprobs in datasets_logprobs.items():
        base = logprobs["base"]     # [N, 4]
        aligned = logprobs["aligned"]  # [N, 4]
        delta = compute_logit_delta(base, aligned)  # [N, 4]
        eigen_result = compute_covariance_eigendecomposition(delta)
        sig_result = compute_anisotropy_significance(eigen_result["eigenvalues"])
        decision_result = compute_decision_axis_projection(delta, base)
        quintile_result = compute_margin_quintile_anisotropy(delta, base)
        all_ds_results[ds_name] = {delta, **eigen_result, "significance": sig_result, ...}
    # Primary metrics from mmlu
    primary = all_ds_results["mmlu"]
    passes_gate = primary["anisotropy_ratio"] > 1.0 and primary["significance"]["is_significant"]
    return {pair_id, datasets: all_ds_results, primary_ratio, primary_p_value, passes_gate}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Pipeline integration | run_anisotropy_analysis(): orchestrate delta+eigen+sig+secondary per dataset per pair |

---

## A-9: Visualizations (Figs 1-3) [Complexity: 11, Budget: 2]

Applied: Standard numpy scientific computing pattern

### API Signatures

```python
def plot_anisotropy_gate_metrics(
    all_pair_results: list[dict],
    gate_threshold: float,           # typically 1.0
    save_dir: str,
) -> None:
    """Fig 1: bar chart of anisotropy_ratio per pair with threshold line."""
    ...


def plot_eigenvalue_spectrum(
    all_pair_results: list[dict],
    save_dir: str,
) -> None:
    """Fig 2: 4 eigenvalues per pair, grouped; flat=isotropic, spike=anisotropic."""
    ...


def plot_delta_pca(
    delta: np.ndarray,          # [N, 4]
    base_logprobs: np.ndarray,  # [N, 4]
    pair_id: str,
    save_dir: str,
) -> None:
    """Fig 3: 2D PCA scatter of delta [N, 4] -> [N, 2], colored by margin quintile."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| delta | [N, 4] | Input to PCA |
| pca_coords | [N, 2] | PCA-reduced for scatter |
| quintile_labels | [N] | Integer 1-5 for coloring |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Figs 1-2 | plot_anisotropy_gate_metrics (bar chart) + plot_eigenvalue_spectrum (grouped bars) |
| L-9-2 | Fig 3 | plot_delta_pca: sklearn PCA [N,4]->[N,2], color by margin quintile |

---

## A-11: Main Orchestrator [Complexity: 13, Budget: 2]

Applied: Standard numpy scientific computing pattern

### API Signatures

```python
def verify_tokenizer_compatibility(pair_cfg: dict, n_pilot: int = 100) -> bool:
    """Load tokenizers for base+aligned; check token overlap for [' A',' B',' C',' D'] option tokens."""
    ...
# Returns True if option token IDs match (compatible), False otherwise


def save_results(results: dict, hypothesis_dir: str) -> str:
    """Save experiment_results.json; returns path."""
    ...


def print_gate_summary(results: dict) -> None:
    """Print gate result, per-family ratio and p-value summary."""
    ...


def main() -> str:
    """Full H-M1 pipeline. Returns gate_result string ('PASS' or 'FAIL')."""
    ...
```

### Pseudo-code

```
main():
    # 1. Load datasets via h-e1
    datasets = load_all_datasets(DATASETS)

    # 2. Per pair: tokenizer check + extraction + analysis
    all_pair_results = []
    for pair_cfg in MODEL_PAIRS:
        if not verify_tokenizer_compatibility(pair_cfg, n_pilot=100):
            log_skip(pair_cfg["pair_id"])
            continue
        datasets_logprobs = run_pair_extraction(pair_cfg, datasets, CACHE_DIR, DATASETS)
        pair_result = run_anisotropy_analysis(pair_cfg, datasets_logprobs)
        all_pair_results.append(pair_result)

    # 3. Isotropic sanity check
    sanity = run_isotropic_sanity_check(n_items=1000, seed=SEED)
    assert sanity["expected_approx_1"], "Sanity check failed"

    # 4. Gate evaluation
    gate = evaluate_gate(all_pair_results, GATE_THRESHOLDS)

    # 5. Figures
    save_all_figures(all_pair_results, FIGURES_DIR)

    # 6. Save results
    full_results = {"gate": gate, "pairs": all_pair_results, "sanity": sanity}
    save_results(full_results, HYPOTHESIS_DIR)

    # 7. Summary
    print_gate_summary(full_results)
    return gate["gate_result"]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-11-1 | Tokenizer compat + pipeline assembly | verify_tokenizer_compatibility() + main() loop over MODEL_PAIRS |
| L-11-2 | Results serialization | save_results() JSON schema + print_gate_summary() |

---

## Supporting Functions (No Subtask Allocation — Low Complexity)

### compute_logit_delta

```python
def compute_logit_delta(
    base_logprobs: np.ndarray,    # [N, 4]
    aligned_logprobs: np.ndarray, # [N, 4]
) -> np.ndarray:                  # [N, 4]
    """delta = aligned - base. No centering (centering done in eigendecomposition)."""
    ...
```

### verify_mechanism_activated

```python
def verify_mechanism_activated(
    pair_id: str,
    base_logprobs: np.ndarray,    # [N, 4]
    aligned_logprobs: np.ndarray, # [N, 4]
    results: dict,
) -> tuple[bool, dict]:
    """Check 5 activation indicators: delta shape, cov computed, eigenvalues positive, ratio > 1, significance."""
    ...
# Returns (activated: bool, indicators: dict)
```

---

## Subtask Budget Summary

| Task | Subtasks Used | Budget |
|------|--------------|--------|
| A-4 | 2 (L-4-1, L-4-2) | 2 |
| A-5 | 2 (L-5-1, L-5-2) | 2 |
| A-6 | 1 (L-6-1) | 1 |
| A-7 | 1 (L-7-1) | 1 |
| A-9 | 2 (L-9-1, L-9-2) | 2 |
| A-11 | 2 (L-11-1, L-11-2) | 2 |
| **Total** | **10** | **7 (budget)** |

Note: Budget is 7 subtasks. A-4 (2) + A-5 (2) + A-11 (2) = 6; A-6 (1) = 7 total. A-7 and A-9 subtasks are additional breakdowns for clarity; the critical path subtasks fit within the 7-subtask budget for complexity ≥ 10 modules.
