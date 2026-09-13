# Architecture: H-M1 (MECHANISM)

**Hypothesis:** LLMs produce category-specific confidence distributions on TruthfulQA
**Type:** MECHANISM — tests causal mechanism (distribution divergence) underlying h-e1's ECE variation

Applied: no matching KB pattern (search returned unrelated diffusion-model results); used scipy.stats standard KS test implementation per experiment brief.

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e1)
**Status:** Actual h-e1 code inspected; matches 03_architecture.md spec closely. Reusing as-is via import.
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** `data.py` exposes `load_truthfulqa_mc`, `assign_clusters`, `validate_cluster_sizes`. `model.py` exposes `load_model_and_tokenizer`, `score_choices`, `predict`. `config.py` exposes `CATEGORY_TO_CLUSTER`, `CLUSTER_NAMES`, `MODEL_ID`, `SEED`, etc. All directly reusable — no reimplementation needed.

---

## File Structure

```
docs/youra_research/h-m1/code/
├── config.py       # local overrides (ALPHA, N_CLUSTERS) + import h-e1 config
├── ks_analysis.py  # pairwise KS test logic (new mechanism module)
├── train.py        # entry point: run inference + KS tests + figures
└── figures/
```

No local `data.py`/`model.py` — imported directly from h-e1 (see External Dependencies).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_truthfulqa_mc | `from h_e1.code.data import load_truthfulqa_mc` | `docs/youra_research/h-e1/code/data.py` |
| assign_clusters | `from h_e1.code.data import assign_clusters` | `docs/youra_research/h-e1/code/data.py` |
| load_model_and_tokenizer | `from h_e1.code.model import load_model_and_tokenizer` | `docs/youra_research/h-e1/code/model.py` |
| predict | `from h_e1.code.model import predict` | `docs/youra_research/h-e1/code/model.py` |
| CATEGORY_TO_CLUSTER, CLUSTER_NAMES, MODEL_ID, SEED | `from h_e1.code.config import *` | `docs/youra_research/h-e1/code/config.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, confirmed via Serena symbol overview)

**Note:** If cross-hypothesis package imports are not resolvable at runtime, Phase 4 Coder should copy h-e1's `data.py`, `model.py`, `config.py` into `h-m1/code/` unchanged rather than reimplementing.

---

## Modules

### config.py

**Dependencies**: h-e1 config (imported)

```python
from h_e1.code.config import *  # SEED, MODEL_ID, CATEGORY_TO_CLUSTER, CLUSTER_NAMES, ...
ALPHA = 0.05
N_CLUSTERS = 7
MIN_CLUSTER_SIZE = 100
RESULTS_JSON = "results.json"
VALIDATION_MD = "../04_validation.md"
FIGURES_DIR = "figures/"
```

### ks_analysis.py

**Dependencies**: config, scipy.stats, itertools

```python
def extract_cluster_confidences(records: list[dict]) -> dict[int, "np.ndarray"]:
    """Group per-question confidence by cluster_id from predict() records."""
def pairwise_ks_tests(cluster_confidences: dict[int, "np.ndarray"]) -> dict[tuple[int,int], dict]:
    """ks_2samp for all C(7,2)=21 pairs. Returns {(c1,c2): {statistic, pvalue}}."""
def evaluate_gate_condition(ks_results: dict) -> tuple[bool, int, int]:
    """Returns (gate_passed, significant_count, total_pairs=21). Pass if >=11/21 p<0.05."""
def cluster_mean_std(cluster_confidences: dict[int, "np.ndarray"]) -> dict[int, dict]:
    """Returns {cluster_id: {mean, std}} and confidence range across clusters."""
```

### train.py (entry point)

**Dependencies**: config, h-e1.data, h-e1.model, ks_analysis, matplotlib

```python
def run_inference(dataset, model, tokenizer, device) -> list[dict]:
    """Reuse h-e1 predict() per question; collect {confidence, cluster_id} records."""
def plot_ks_heatmap(ks_results: dict, cluster_ids: list[int], path): ...
def plot_confidence_histograms(cluster_confidences: dict, path): ...
def plot_confidence_boxplot(cluster_confidences: dict, path): ...
def plot_cdf_comparison(cluster_confidences: dict, path): ...
def save_results_json(results: dict, path): ...
def save_validation_md(gate_pass: bool, results: dict, path): ...
def main(): ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Wire h-e1 reuse | Import/copy h-e1 data.py, model.py, config.py; verify functions callable | 5 | 1+2+1+1 |
| M-2 | Dataset + cluster prep | Load TruthfulQA MC, assign clusters, validate >=100/cluster | 6 | 2+2+1+1 |
| M-3 | Model inference | Load Llama-2-7B fp16, run predict() over all questions, collect confidence records | 10 | 2+3+2+3 |
| M-4 | KS test module | Implement extract_cluster_confidences, pairwise_ks_tests (21 pairs), gate evaluation | 8 | 2+1+3+2 |
| M-5 | Descriptive stats | Per-cluster mean/std confidence, range check (>0.1) | 4 | 1+1+1+1 |
| M-6 | Required visualization | KS p-value heatmap (21 pairs, significance highlighted) | 5 | 1+1+1+2 |
| M-7 | Optional visualizations | Confidence histograms, box plot, CDF comparison per cluster | 6 | 2+1+1+2 |
| M-8 | Results & gate report | Write results.json and 04_validation.md with gate decision, stats, figures | 5 | 1+1+1+2 |
| M-9 | End-to-end run & validation | Wire train.py main(), execute pipeline, verify <30min/<24GB | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-3, M-4], Low(4-8): [M-1, M-2, M-5, M-6, M-7, M-8, M-9]

---

## Self-Check
- Base hypothesis (h-e1) exists -> Serena MUST be called -> done, actual code inspected.
- External Dependencies section included with verified import paths.
- 9 Epic tasks (within 6-12 range for MECHANISM).
- No new model/training code — reuses h-e1 inference infra, adds only KS analysis layer.
