# Configuration: h-m3 (MECHANISM)

**Type**: MECHANISM — new `ExperimentConfig`/`ExperimentResult` dataclasses (architecture.md config.py spec used as-is); models/loaders reused unchanged from h-m1.

Applied: factorial-sweep-config-pattern (single dataclass drives 2 tasks x 3 archs x 3 seeds sweep, no per-run config variants)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: h-m1 config classes read directly (Serena MCP unavailable; base code + h-m1/03_config.md read manually per fallback, consistent with h-m3/03_architecture.md's own fallback note)
**Config Files Found**: `docs/youra_research/h-m1/03_config.md` (extends `h-e1/code/config.py` `Config`); h-m1 itself has no separate `config.py` file on disk yet (defined only in its 03_config.md spec)
**Pattern Used**: dataclass

**Decision**: h-m3 does **not** inherit h-m1's `Config` class. h-m1's `Config` is training-dynamics-tracking specific (gradient/attention tracking fields — `track_every`, `wasserstein_threshold`, etc.) which h-m3 does not use (architecture.md confirms h-m3 reuses only `models.py` + `normalize_weights`/`collate_fn` from h-m1, not its config or tracker). h-m3 defines a fresh, smaller `ExperimentConfig` per `03_architecture.md`'s own config.py spec, matching PRD FR-4 training protocol values (lr=1e-4, batch_size=32, epochs=100, seeds=[42,123,456]) exactly.

---

## Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    tasks: list = field(default_factory=lambda: ["backdoor", "accuracy"])
    architectures: list = field(default_factory=lambda: ["mlp", "dws", "nft"])
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    n_train: int = 600
    n_test: int = 200
    epochs: int = 100
    lr: float = 1e-4
    batch_size: int = 32
    hidden_dim: int = 128
    weight_shapes: list = None        # set at runtime via synth_data.default_weight_shapes
    param_count_tolerance: float = 0.10   # FR-3: match param counts within 10%
    anova_alpha: float = 0.05             # FR-6: significance threshold
    device: str = "cuda"
    results_path: str = "docs/youra_research/h-m3/code/outputs/results.json"
    fig_dir: str = "docs/youra_research/h-m3/figures"

@dataclass
class ExperimentResult:
    task: str
    architecture: str
    seed: int
    metric_value: float             # AUC (backdoor) or RMSE (accuracy)
    secondary_metric: float = None  # R2 (accuracy only)
    train_time: float = 0.0
```

No YAML/CLI — hardcode `ExperimentConfig()` in `main.py`. `weight_shapes` populated once at startup via `default_weight_shapes(hidden_dim)` and shared across all 18 runs so param-count matching (M-7 pre-check) is comparable.

---

## Subtasks [2/2 used]

Config work is folded into architecture's M-2 (Complexity 6); allocating both budgeted subtasks there per task allocation.

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Dataclass definitions | `ExperimentConfig`, `ExperimentResult` in `config.py` per schema above |
| C-2-2 | Weight-shape + param-count helpers | `default_weight_shapes(hidden_dim, n_layers=4)`; verify `build_model` output stays within `param_count_tolerance` across mlp/dws/nft |

---

## Remaining Tasks (M-1, M-3–M-9)

No additional config fields — all consume `ExperimentConfig` fields above (`lr`, `batch_size`, `epochs`, `seeds`, `n_train`, `n_test`, `anova_alpha`, `fig_dir`, `results_path`) as specified in `03_architecture.md` module signatures. AdamW + CosineAnnealingLR (T_max=`epochs`), `BCEWithLogitsLoss` (backdoor) / `MSELoss` (accuracy) injected per-task into shared `train_task`, matplotlib `dpi=150` for all 4 figures (h-e1/h-m1 convention, reused as-is).
