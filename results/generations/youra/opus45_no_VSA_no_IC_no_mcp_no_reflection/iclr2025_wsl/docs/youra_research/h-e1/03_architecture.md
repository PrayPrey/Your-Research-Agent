# Architecture: H-E1 (EXISTENCE)

**Type**: EXISTENCE (PoC) — minimal structure
**Applied**: measurement-pipeline pattern (no baseline/proposed model split; single pass over pretrained checkpoints)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure

```
h-e1/code/
  config.py
  collect_models.py
  measure.py
  analyze.py
  visualize.py
  run.py
  results.json        (output)
  figures/             (output)
```

---

## Modules

### config.py

**Dependencies**: none

```python
N_MODELS_TARGET: int = 100
N_MODELS_FETCH: int = 150       # buffer for load failures
SEARCH_QUERY: str = "vit"
PIPELINE_TAG: str = "image-classification"
SIGMA_GATE_THRESHOLD: float = 0.5
ATTENTION_NAME_PATTERN: str = "attention|qkv|query|key|value"
RESULTS_PATH: str = "results.json"
FIGURES_DIR: str = "figures/"
```

### collect_models.py

**Dependencies**: config

```python
def fetch_vit_model_ids(n_fetch: int) -> list[str]: ...
```

### measure.py

**Dependencies**: config

```python
def compute_alpha_for_model(model_id: str) -> dict | None:
    """Load model, run WeightWatcher, extract attention-layer alpha stats.
    Returns None on load/analysis failure (caller logs skip)."""
    ...

def run_measurement(model_ids: list[str]) -> list[dict]: ...
```

### analyze.py

**Dependencies**: none (pure numpy/pandas on results)

```python
def aggregate_statistics(results: list[dict]) -> dict:
    """Returns global mean, std (sigma_alpha), median, range, gate_passed,
    and per-family grouping (by model_id prefix)."""
    ...
```

### visualize.py

**Dependencies**: analyze (consumes aggregated dict + raw results)

```python
def plot_gate_bar(sigma_alpha: float, threshold: float, out_dir: str) -> None: ...
def plot_alpha_histogram(results: list[dict], out_dir: str) -> None: ...
def plot_family_boxplot(results: list[dict], out_dir: str) -> None: ...
def plot_alpha_vs_size(results: list[dict], out_dir: str) -> None: ...
```

### run.py

**Dependencies**: collect_models, measure, analyze, visualize, config

```python
def main() -> None:
    """Fetch models -> measure alpha -> aggregate -> save results.json
    -> generate figures -> print gate pass/fail."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Model collection | HF Hub API query for 100+ ViT checkpoints, family filter | 8 | 2+3+2+1 |
| A-2 | Alpha computation | WeightWatcher integration, load model, extract attention-layer alpha | 12 | 3+3+4+2 |
| A-3 | Batch measurement loop | Iterate models, handle failures gracefully, log skips | 7 | 2+2+1+2 |
| A-4 | Statistical aggregation | Compute sigma(alpha), mean, family grouping, gate check | 6 | 2+1+2+1 |
| A-5 | Visualization suite | 4 required figures (gate bar, histogram, boxplot, scatter) | 8 | 3+1+2+2 |
| A-6 | Pipeline orchestration + results output | run.py wiring, results.json save, run within 4hr budget | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2], Low(4-8): [A-1, A-3, A-4, A-5, A-6]

Skipped: ablation modules, config variants, multi-run seeding — EXISTENCE gate needs one deterministic pass. Add if H-E1 passes and downstream hypotheses need parametrization.
