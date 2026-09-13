# Architecture: H-E1 (EXISTENCE / PoC)

**Hypothesis**: CV_PR can be reliably extracted from 100+ timm models using randomized SVD with 20 seeds
**Type**: EXISTENCE — minimal architecture (4-8 tasks, no ablation modules)

Applied: low-rank weight matrix analysis pattern (PEFT/LoRA-adjacent, from Archon KB)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis, no existing repo.

---

## File Structure

```
h-e1/code/
  model.py       # randomized SVD + participation ratio + CV_PR core functions
  extract.py      # model loading loop (timm), layer iteration, orchestration
  config.py       # fixed config (n_seeds, rank, model list, output paths)
  evaluate.py      # aggregate results, success-rate check, summary stats
  visualize.py     # required figures (success rate bar, CV_PR histogram) + optional figs
```

## Modules

### model.py

**Dependencies**: torch, numpy

```python
def randomized_svd(A: torch.Tensor, rank: int, seed: int) -> torch.Tensor: ...
def participation_ratio(eigenvalues: torch.Tensor) -> float: ...
def compute_cv_pr(weight: torch.Tensor, n_seeds: int = 20, rank: int = 50) -> dict: ...
```

### extract.py

**Dependencies**: model.py, config.py, timm

```python
def get_target_layers(model: torch.nn.Module) -> list[tuple[str, torch.Tensor]]: ...
    # yields (layer_name, weight) for conv2d/linear, reshape 4D->2D
def process_model(model_name: str, cfg: dict) -> dict | None: ...
    # loads model, runs compute_cv_pr per layer, aggregates to model-level, catches errors
def run_extraction(cfg: dict) -> list[dict]: ...
    # iterates timm.list_models(pretrained=True)[:cfg.n_models], calls process_model, logs progress
```

### config.py

**Dependencies**: none

```python
CONFIG = {
    "n_seeds": 20,
    "rank": 50,
    "n_models": 100,
    "seed_base": 0,
    "output_dir": "h-e1/results",
    "figures_dir": "h-e1/figures",
}
```

### evaluate.py

**Dependencies**: numpy, config.py

```python
def aggregate_results(results: list[dict]) -> dict: ...
    # completion_rate, mean/std cv_pr across models, per-family breakdown
def check_success_criteria(summary: dict) -> bool: ...
    # completion_rate >= 0.95, all cv_pr finite in (0,10)
def save_results(results: list[dict], summary: dict, out_dir: str) -> None: ...
    # writes CSV/JSON per PRD FR-6
```

### visualize.py

**Dependencies**: matplotlib, evaluate.py

```python
def plot_success_rate(summary: dict, out_path: str) -> None: ...
def plot_cv_pr_distribution(results: list[dict], out_path: str) -> None: ...
def plot_cv_pr_by_family(results: list[dict], out_path: str) -> None: ...   # optional
def plot_cv_pr_vs_size(results: list[dict], out_path: str) -> None: ...     # optional
def plot_processing_time(results: list[dict], out_path: str) -> None: ...   # optional
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | Define fixed config dict (seeds, rank, model count, paths) | 4 | 1+1+1+1 |
| A-2 | Core SVD+PR mechanism | Implement randomized_svd, participation_ratio, compute_cv_pr in model.py | 12 | 3+2+5+2 |
| A-3 | Layer extraction | get_target_layers: iterate named_modules, filter conv2d/linear, reshape 4D weights | 8 | 2+2+2+2 |
| A-4 | Model loop + error handling | process_model + run_extraction: timm loading, per-model try/except, progress logging | 10 | 3+3+2+2 |
| A-5 | Aggregation + success check | evaluate.py: aggregate stats, threshold checks, CSV/JSON save | 7 | 2+2+2+1 |
| A-6 | Visualization | Required figures (success rate, CV_PR histogram) + 3 optional figs | 6 | 2+1+1+2 |
| A-7 | End-to-end run + verification | Run full 100+ model extraction, verify mechanism per brief's verify_cv_pr_mechanism | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-7], Low(4-8): [A-1, A-3, A-5, A-6]

---

## Notes

- No ablation/baseline model modules — EXISTENCE type has no comparison model (extraction pipeline only).
- Reproducibility: seed = 0..19 fixed per layer (FR-NFR-3), `torch.manual_seed(seed)` inside `randomized_svd`.
- Error handling: `process_model` wraps model load + layer loop in try/except, returns `None` on failure; `run_extraction` skips and logs.
</content>
