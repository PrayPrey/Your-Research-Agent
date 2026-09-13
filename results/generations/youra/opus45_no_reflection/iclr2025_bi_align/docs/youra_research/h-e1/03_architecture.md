# Architecture: H-E1 (EXISTENCE / PoC)

**Hypothesis:** Collaboration score extracts agency signals orthogonal to preference labels (correlation < 0.7)
**Type:** EXISTENCE - statistical analysis, no training

Applied: No directly relevant KB pattern found (searched "statistical analysis correlation architecture"); standard scipy-based analysis pipeline used instead.

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis, no existing codebase.

---

## File Structure

- `data.py` - dataset loading + response extraction
- `collab_score.py` - collab_score_v2 signal computation
- `analysis.py` - correlation + distribution stats
- `visualize.py` - figure generation (bar/hist/scatter/box)
- `run_experiment.py` - orchestration entrypoint
- `config.py` - fixed config (seed, sample size, paths)

---

## Module Interfaces

### config.py

```python
SEED: int = 42
SAMPLE_SIZE: int = 1000
DATASET_NAME: str = "Anthropic/hh-rlhf"
DATASET_SUBSET: str = "helpful-base"
FIGURES_DIR: str = "figures/"
```

### data.py

**Dependencies**: config

```python
def load_hh_rlhf_sample(seed: int, n: int) -> Dataset: ...
def extract_assistant_response(conversation: str) -> str: ...
```

### collab_score.py

**Dependencies**: None (re, numpy)

```python
def compute_collab_score_v2(response: str) -> float: ...
```

### analysis.py

**Dependencies**: collab_score, data

```python
def compute_correlation(dataset, n_samples: int) -> dict:
    """Returns: correlation, p_value, chosen_mean/std, rejected_mean/std, gate_passed"""
    ...
```

### visualize.py

**Dependencies**: analysis (result dict)

```python
def plot_gate_bar_chart(correlation: float, threshold: float, out_path: str) -> None: ...
def plot_score_histogram(chosen: list, rejected: list, out_path: str) -> None: ...
def plot_scatter_regression(scores: list, labels: list, out_path: str) -> None: ...
def plot_boxplot(chosen: list, rejected: list, out_path: str) -> None: ...
```

### run_experiment.py

**Dependencies**: config, data, analysis, visualize

```python
def main() -> None:
    """Load data -> compute scores -> correlation -> save figures + results.json"""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup config & project structure | config.py, dirs | 3 | 1+1+1+0 |
| A-2 | Data loading module | load HH-RLHF, shuffle, extract response | 6 | 2+2+1+1 |
| A-3 | Implement collab_score_v2 | regex signal extraction + normalization | 7 | 2+1+3+1 |
| A-4 | Correlation analysis module | pearsonr, means/stds, gate check | 6 | 2+2+2+0 |
| A-5 | Visualization suite | 4 required figures | 6 | 2+1+1+2 |
| A-6 | Run experiment end-to-end | orchestrate + save results.json | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6]

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Module sections = interface code only
- [x] 6 Epic tasks with complexity (within 4-8 range)
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included (green-field)
