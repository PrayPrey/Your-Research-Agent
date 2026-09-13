# Logic: H-E1 (EXISTENCE / PoC)

Applied: randomized SVD (Halko algorithm) numerical pattern — standard PyTorch linalg, no KB code example needed.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - designing new APIs, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Core SVD+PR mechanism [Complexity: 12, Budget: 1 subtask]

**Applied**: Halko randomized SVD (standard numerical recipe)

### API Signatures

```python
def randomized_svd(A: torch.Tensor, rank: int, seed: int) -> torch.Tensor:
    """Randomized SVD via random projection. A: [M, N] -> singular values [rank]"""
    ...

def participation_ratio(eigenvalues: torch.Tensor) -> float:
    """PR = (sum(eig))^2 / sum(eig^2). eigenvalues: [rank] -> scalar"""
    ...

def compute_cv_pr(weight: torch.Tensor, n_seeds: int = 20, rank: int = 50) -> dict:
    """weight: [out, in] -> {"cv_pr": float, "mean_pr": float, "std_pr": float}"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| A | [M, N] | 2D weight matrix |
| Omega | [N, rank] | random projection, `torch.manual_seed(seed)` |
| Y | [M, rank] | A @ Omega |
| S | [rank] | singular values from `torch.linalg.svd(Y, ...)` |
| eigenvalues | [rank] | S ** 2 |

### Pseudo-code

```
randomized_svd(A, rank, seed):
    torch.manual_seed(seed)
    Omega = torch.randn(A.shape[1], rank)
    Y = A @ Omega                          # [M, rank]
    Q, _ = torch.linalg.qr(Y)              # [M, rank]
    B = Q.T @ A                            # [rank, N]
    _, S, _ = torch.linalg.svd(B, full_matrices=False)
    return S                               # [rank]

participation_ratio(eigenvalues):
    eig = eigenvalues.clamp(min=1e-12)     # numerical stability, avoid div-by-zero
    return (eig.sum() ** 2 / (eig ** 2).sum()).item()

compute_cv_pr(weight, n_seeds=20, rank=50):
    prs = []
    for seed in range(n_seeds):
        S = randomized_svd(weight, rank, seed)
        prs.append(participation_ratio(S ** 2))
    prs = torch.tensor(prs)
    mean, std = prs.mean().item(), prs.std().item()
    cv = std / mean if mean > 0 else float("nan")
    return {"cv_pr": cv, "mean_pr": mean, "std_pr": std}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | randomized_svd | QR-based random projection SVD, seeded |
| L-A2-2 | participation_ratio | PR formula with eps clamp |
| L-A2-3 | compute_cv_pr loop | 20-seed loop, mean/std/cv aggregation |
| L-A2-4 | edge-case guards | rank > min(M,N) clamp; mean==0 -> nan |

---

## A-4: Model loop + error handling [Complexity: 10, Budget: 1 subtask]

**Applied**: Standard PyTorch — try/except per-model isolation

### API Signatures

```python
def get_target_layers(model: torch.nn.Module) -> list[tuple[str, torch.Tensor]]:
    """Yields (name, weight) for Conv2d/Linear. 4D weight [O,C,H,W] -> reshaped [O, C*H*W]"""
    ...

def process_model(model_name: str, cfg: dict) -> dict | None:
    """Loads model via timm, runs compute_cv_pr per layer. Returns None on failure."""
    ...

def run_extraction(cfg: dict) -> list[dict]:
    """Iterates timm.list_models(pretrained=True)[:cfg['n_models']]. Returns list of per-model dicts."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weight (Linear) | [out, in] | used as-is |
| weight (Conv2d) | [O, C, H, W] | reshape to [O, C*H*W] before compute_cv_pr |

### Pseudo-code

```
get_target_layers(model):
    for name, module in model.named_modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            w = module.weight.data
            if w.dim() == 4:
                w = w.reshape(w.shape[0], -1)   # [O, C*H*W]
            yield (name, w)

process_model(model_name, cfg):
    try:
        model = timm.create_model(model_name, pretrained=True)
        model.eval()
        layer_results = []
        for name, w in get_target_layers(model):
            try:
                r = compute_cv_pr(w, cfg["n_seeds"], cfg["rank"])
                layer_results.append({"layer": name, **r})
            except Exception:
                continue                        # skip bad layer, keep going
        if not layer_results:
            return None
        model_cv_pr = mean(r["cv_pr"] for r in layer_results if isfinite(r["cv_pr"]))
        return {"model": model_name, "model_cv_pr": model_cv_pr, "layers": layer_results}
    except Exception as e:
        log.warning(f"skip {model_name}: {e}")
        return None

run_extraction(cfg):
    names = timm.list_models(pretrained=True)[:cfg["n_models"]]
    results = []
    for i, name in enumerate(names):
        r = process_model(name, cfg)
        if r is not None:
            results.append(r)
        log.info(f"[{i+1}/{len(names)}] {name}: {'ok' if r else 'skipped'}")
    return results
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | get_target_layers | named_modules filter + 4D->2D reshape |
| L-A4-2 | process_model | timm load, per-layer try/except, model-level aggregation |
| L-A4-3 | run_extraction | list_models loop, progress logging, skip-on-None |

---

## A-7: End-to-end run + verification [Complexity: 9, Budget: 1 subtask]

**Applied**: Standard PyTorch — script orchestration, no new pattern

### API Signatures

```python
def main() -> None:
    """Runs run_extraction(CONFIG) -> aggregate_results -> check_success_criteria -> save_results -> plots."""
    ...

def verify_cv_pr_mechanism(results: list[dict]) -> bool:
    """Sanity check: cv_pr finite in (0,10) for all models, completion_rate >= 0.95."""
    ...
```

### Pseudo-code

```
main():
    results = run_extraction(CONFIG)
    summary = aggregate_results(results)
    ok = check_success_criteria(summary)
    save_results(results, summary, CONFIG["output_dir"])
    plot_success_rate(summary, ...)
    plot_cv_pr_distribution(results, ...)
    assert verify_cv_pr_mechanism(results) == ok
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A7-1 | main orchestration | wire extraction -> aggregate -> save -> plots |
| L-A7-2 | verify_cv_pr_mechanism | reuse check_success_criteria for final assertion |

---

## Self-Validation

- No ASCII diagrams
- Docstrings <= 2 lines
- Tensor shapes in comments/tables
- Subtask counts within per-task budgets from architecture
- Green-field: Serena skipped, noted above
</content>
