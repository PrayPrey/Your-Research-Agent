# Logic: H-M2

**Hypothesis:** Different attention structures create different Hessian curvature patterns (block-diagonal vs dense)

Applied: hessian-eigenthings HessianOperator/GGNOperator + Lanczos (KB search returned no direct matches; used architecture-doc-verified library API)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M1)
**Status:** Serena had no active project registered for this workspace; fell back to direct file read of `h-m1/code/` and `h-m1/03_logic.md` (functionally equivalent per "trust actual code" rule). H-M1 models are `AutoModel` without classification heads and never fine-tuned — no reusable Hessian/training code exists in H-M1. Only the SST-2 `load_dataset` pattern and `config.py` dataclass shape are reused.
**Analyzed Path:** `docs/youra_research/h-m1/code/`, `docs/youra_research/h-m1/03_logic.md`
**Relevant Symbols:** `verify_attention_structure` (H-M1 A-7) — pattern reused for H-M2 gate verification (relative-diff + threshold dict).

---

## A-4: Hessian Metrics Core [Complexity: 14, Budget: 6]

**Applied:** hessian-eigenthings `HessianOperator` + `lanczos` + `trace`, with manual HVP/`scipy.sparse.linalg.eigsh` fallback

### API Signatures

```python
def compute_hessian_metrics(
    model: nn.Module,
    dataloader: DataLoader,
    loss_fn: Callable[[Tensor, Tensor], Tensor],
    device: str,
    k: int = 20,
    lanczos_steps: int = 50,
    trace_matvecs: int = 100,
    seed: int = 42,
) -> dict:
    """Returns {top_eigenvalue, eigenvalue_ratio, trace, top_k_eigenvalues, spectral_norm}."""
    ...

def compute_spectral_density(
    model: nn.Module,
    dataloader: DataLoader,
    loss_fn: Callable[[Tensor, Tensor], Tensor],
    device: str,
    num_runs: int = 8,
    lanczos_steps: int = 40,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """SLQ density estimate. Returns (density, grid), both [num_bins]."""
    ...

def _hvp_fallback(model: nn.Module, loss_fn: Callable, batch: tuple, vector: Tensor) -> Tensor:
    """Manual Hessian-vector product via double backward. vector/return: [n_params]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| top_eigenvalues | [k] | descending, `top_eigenvalues[-1]` = top eigenvalue (hessian-eigenthings convention) |
| vector (HVP) | [n_params] | flattened, matches `sum(p.numel() for p in model.parameters())` |
| density, grid | [num_bins] each | SLQ output for spectral density plot |

### Pseudo-code

```
compute_hessian_metrics(model, dataloader, loss_fn, device, k, lanczos_steps, trace_matvecs, seed):
    try:
        H = HessianOperator(model.to(device), dataloader, loss_fn)
        eig = lanczos(H, k=k, num_lanczos_steps=lanczos_steps, seed=seed)
        top_eigenvalues = eig.eigenvalues  # ascending, len k
        trace_est = trace(H, num_matvecs=trace_matvecs, seed=seed)
    except (ImportError, RuntimeError):
        # fallback: PyHessian
        hess = pyhessian.hessian(model, loss_fn, dataloader=dataloader, cuda=(device=="cuda"))
        top_eigenvalues, _ = hess.eigenvalues(top_n=k)
        trace_est = hess.trace()
    return {
        "top_eigenvalue": float(top_eigenvalues[-1]),
        "eigenvalue_ratio": float(top_eigenvalues[-1] / top_eigenvalues[0]),
        "trace": float(trace_est) if not isinstance(trace_est, list) else float(np.mean(trace_est)),
        "top_k_eigenvalues": [float(e) for e in top_eigenvalues],
        "spectral_norm": float(top_eigenvalues[-1]),
    }

compute_spectral_density(model, dataloader, loss_fn, device, num_runs, lanczos_steps, seed):
    density, grid = spectral_density(HessianOperator(model, dataloader, loss_fn),
                                      num_runs=num_runs, lanczos_steps=lanczos_steps, seed=seed)
    return density, grid
```

### Subtasks [3/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Primary path (hessian-eigenthings) | HessianOperator + lanczos(k=20) + trace(matvecs=100) |
| L-4-2 | Fallback path (PyHessian) | try/except wrap, `hessian(...).eigenvalues()`/`.trace()` |
| L-4-3 | Metrics dict + spectral density | assemble return dict; `compute_spectral_density` via SLQ |

---

## A-6: Kronecker Fit Analysis [Complexity: 13, Budget: 6]

**Applied:** hessian-eigenthings `GGNOperator` (block-diagonal by construction) + per-layer Frobenius-norm Kronecker-fit error

### API Signatures

```python
def compute_kronecker_fit(
    model: nn.Module,
    dataloader: DataLoader,
    loss_fn: Callable[[Tensor, Tensor], Tensor],
    layer_names: list[str],
    device: str,
) -> dict[str, float]:
    """Per-layer ||G_layer - A⊗S||_F / ||G_layer||_F. Returns {layer_name: fit_error}."""
    ...

def _extract_layer_ggn_block(G: "GGNOperator", layer_name: str, model: nn.Module) -> Tensor:
    """G restricted to one layer's params via param_filter. Returns [P_l, P_l] dense block."""
    ...

def _kronecker_svd_fit(G_layer: Tensor, dim_a: int, dim_s: int) -> Tensor:
    """Best rank-1 Kronecker approx A⊗S of G_layer via SVD of reshaped/permuted matrix.
    G_layer: [dim_a*dim_s, dim_a*dim_s] -> approx: same shape."""
    ...

def aggregate_kronecker_fit(per_layer_errors: dict[str, float]) -> dict:
    """Returns {mean_fit_error, std_fit_error, per_layer: per_layer_errors}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| G_layer | [P_l, P_l] | dense GGN block for layer l, P_l = layer's param count (small: attention proj weight only) |
| reshaped (for SVD) | [dim_a, dim_s, dim_a, dim_s] -> permute -> [dim_a², dim_s²] | dim_a*dim_s = P_l; A: [dim_a,dim_a], S: [dim_s,dim_s] |
| A, S | [dim_a, dim_a], [dim_s, dim_s] | Kronecker factors, rank-1 approx from leading singular vector |
| approx | [P_l, P_l] | `torch.kron(A, S)` reshaped back |

### Pseudo-code

```
compute_kronecker_fit(model, dataloader, loss_fn, layer_names, device):
    G = GGNOperator(model.to(device), dataloader, loss_fn)
    errors = {}
    for name in layer_names:
        G_layer = _extract_layer_ggn_block(G, name, model)  # [P_l, P_l]
        dim_a, dim_s = _factor_dims(G_layer.shape[0])        # e.g. (hidden, hidden) heuristic
        approx = _kronecker_svd_fit(G_layer, dim_a, dim_s)
        errors[name] = (torch.norm(G_layer - approx) / torch.norm(G_layer)).item()
    return errors

_kronecker_svd_fit(G_layer, dim_a, dim_s):
    # Van Loan-Pitsianis nearest-Kronecker-product via SVD
    R = G_layer.reshape(dim_a, dim_s, dim_a, dim_s).permute(0, 2, 1, 3).reshape(dim_a * dim_a, dim_s * dim_s)
    U, S_vals, Vt = torch.linalg.svd(R, full_matrices=False)
    A = (U[:, 0] * S_vals[0].sqrt()).reshape(dim_a, dim_a)
    S = (Vt[0, :] * S_vals[0].sqrt()).reshape(dim_s, dim_s)
    return torch.kron(A, S)
```

### Subtasks [3/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Per-layer GGN block extraction | GGNOperator + param_filter per attention layer name |
| L-6-2 | Nearest Kronecker-product fit | Van Loan-Pitsianis SVD reshape/permute + rank-1 factor recovery |
| L-6-3 | Fit error + aggregation | Frobenius ratio per layer, `aggregate_kronecker_fit` mean/std |

---

## External Dependencies (Base Hypothesis)

No H-M1 module is directly importable for H-M2's Hessian/fine-tuning logic — H-M1 used bare `AutoModel` (no classification head, never fine-tuned). Only reusable pattern is the SST-2 `load_dataset("glue", "sst2")` call shape, already reflected in `03_architecture.md`'s `data_loader.py` signature. No API-signature verification needed beyond the architecture doc's own Serena finding.

---

## A-8: Gate Verification (reference — reuses H-M1 pattern)

```python
def verify_hessian_gate(bert_metrics: dict, gpt2_metrics: dict, threshold: float = 0.10) -> dict:
    """Relative diff per metric in {top_eigenvalue, eigenvalue_ratio, trace}; pass if any > threshold."""
    diffs = {}
    for m in ("top_eigenvalue", "eigenvalue_ratio", "trace"):
        denom = max(abs(bert_metrics[m]), abs(gpt2_metrics[m]), 1e-12)
        diffs[m] = abs(bert_metrics[m] - gpt2_metrics[m]) / denom
    return {**diffs, "gate_pass": any(v > threshold for v in diffs.values())}
```

Follows H-M1 `verify_attention_structure` structure (relative-diff + threshold dict). Not part of the 6-subtask A-4/A-6 budget — low complexity (5), covered by architecture doc signature directly.
