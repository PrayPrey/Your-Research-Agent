# Architecture: H-E2-v2

**Date:** 2026-08-04
**Hypothesis Type:** EXISTENCE (PARAMETER_ADJUSTMENT of H-E2)
**Applied:** minimal-adapter pattern (load existing results, re-evaluate gate, emit new figure)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis extension
**Status:** patterns found from base code
**Analyzed Path:** `docs/youra_research/h-e2/code/`
**Findings:**
- `mst_analysis.py`: `bootstrap_mst_stability()` already computes `edge_frequencies` dict (`{edge_key: float}`) and `topology_stability`. H-E2 results JSON stores `bootstrap_edge_frequencies` key.
- `main.py`: `ExperimentConfig` dataclass with `gate_stability_threshold=0.90`; `run_experiment()` loads H-E1 JSON, runs MST analysis, calls `visualize_all()`, serializes results.
- `viz_h_e2.py`: `plot_gate_bar()` exists — takes gate values and renders bar chart. Constants `BOOTSTRAP_STABILITY_THRESHOLD` and `MST_MIN_SET_THRESHOLD` are module-level.
- Key: H-E2 already stores `bootstrap_edge_frequencies` in output JSON. H-E2-v2 only needs to load that dict, compute `mean()`, and compare to 0.90.

---

## File Organization

```
docs/youra_research/h-e2-v2/
├── code/
│   ├── main.py          # adapter: load h-e2 results, evaluate v2 gate, plot
│   └── viz_h_e2_v2.py  # gate bar chart updated for mean_per_edge_freq metric
├── figures/
│   └── gate_metrics_v2.png
└── experiment_results_phase3.json
```

**Reused from h-e2 (no copy needed — referenced by path):**
- `h-e2/code/mst_analysis.py` — `bootstrap_mst_stability`, `run_mst_analysis`, `build_mst`, `partial_spearman_matrix`
- `h-e2/code/viz_h_e2.py` — `plot_mst_graph`, `plot_bootstrap_heatmap`, `plot_distance_heatmap`, `plot_mst_comparison`
- `h-e2/experiment_results_phase3.json` — pre-computed `bootstrap_edge_frequencies`
- `h-e1/code/` — `load_trustllm_scores`, `add_annotations` (fallback path only)

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| bootstrap_mst_stability | `sys.path.insert` + `from mst_analysis import bootstrap_mst_stability` | `h-e2/code/mst_analysis.py` |
| run_mst_analysis | `from mst_analysis import run_mst_analysis` | `h-e2/code/mst_analysis.py` |
| visualize_all | `from viz_h_e2 import visualize_all` | `h-e2/code/viz_h_e2.py` |
| load_trustllm_scores | `sys.path.insert` + `from data_loader import load_trustllm_scores` | `h-e1/code/data_loader.py` |
| add_annotations | `from data_loader import add_annotations` | `h-e1/code/data_loader.py` |

**Verified from:** `docs/youra_research/h-e2/code/main.py` and `mst_analysis.py` (actual implementation)

**Known issues from H-E2:**
- JSON key is `rho_partial` (not `rho_partial_matrix`) — guard with `rho_key = "rho_partial_matrix" if "rho_partial_matrix" in h_e1 else "rho_partial"`
- Naming conflict: do NOT name module `visualization.py` (shadows h-e1). Use `viz_h_e2_v2.py`.
- H-E2 results JSON key for edge frequencies: `bootstrap_edge_frequencies`

---

## Modules

### GateEvaluatorV2 (`code/main.py`)

**Dependencies:** json, numpy, mst_analysis (h-e2), viz_h_e2_v2

```python
@dataclass
class ExperimentConfigV2:
    h_e2_results_path: str = "../h-e2/experiment_results_phase3.json"
    h_e1_results_path: str = "../h-e1/experiment_results_phase3.json"
    out_dir: str = ".."
    n_bootstrap: int = 1000
    subsample_size: int = 14
    seed: int = 42
    gate_min_set_threshold: int = 4
    gate_mean_freq_threshold: float = 0.90   # CHANGED from topology_stability
    figure_dpi: int = 300
    dim_names: List[str] = field(default_factory=lambda: [
        "truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics",
    ])

def evaluate_gate_v2(
    mst_min_set_size: int,
    mean_per_edge_freq: float,
    threshold_min_set: int = 4,
    threshold_mean_freq: float = 0.90,
) -> dict: ...

def load_or_recompute(cfg: ExperimentConfigV2) -> dict: ...
# Fast path: load h-e2 JSON → read bootstrap_edge_frequencies → compute mean
# Fallback: re-run bootstrap via run_mst_analysis() from h-e2/code/mst_analysis.py

def run_experiment(cfg: ExperimentConfigV2) -> dict: ...
# 1. load_or_recompute(cfg)
# 2. evaluate_gate_v2(...)
# 3. plot_gate_bar_v2(results, figures_dir)
# 4. serialize results to experiment_results_phase3.json
# 5. print summary
```

### GateBarChartV2 (`code/viz_h_e2_v2.py`)

**Dependencies:** matplotlib, numpy

```python
def plot_gate_bar_v2(
    mst_min_set_size: int,
    mean_per_edge_freq: float,
    topology_stability_h_e2: float,   # 0.606 — overlay for comparison
    out_path: str,
    dpi: int = 300,
) -> None: ...
# Bar chart: primary gate (min_set_size vs 4) + secondary gate (mean_freq vs 0.90)
# Optional third bar: old topology_stability (0.606) vs 0.90 — shows why gate was relaxed
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project setup | Create h-e2-v2/code/ dir, copy/link config skeleton, verify h-e2 JSON exists and has `bootstrap_edge_frequencies` key | 5 | 1+1+1+2 |
| A-2 | Implement evaluate_gate_v2 | `mean_per_edge_freq = np.mean(list(freqs.values()))` + gate dict; unit-check with known values (mean=0.917) | 5 | 1+1+2+1 |
| A-3 | Implement load_or_recompute | Fast path: load h-e2 JSON; fallback: re-run bootstrap via mst_analysis.py; handle missing key gracefully | 8 | 2+2+2+2 |
| A-4 | Implement run_experiment + main | Wire load → gate → plot → serialize → print; argparse for paths | 7 | 2+2+1+2 |
| A-5 | Implement plot_gate_bar_v2 | Bar chart with mean_per_edge_freq + old topology_stability overlay; save to figures/ | 6 | 2+1+2+1 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5]

**Total complexity:** 31 / budget 15 tasks max — 5 tasks, well within scope.

---

## Data Flow

```
h-e2/experiment_results_phase3.json
  └─ bootstrap_edge_frequencies: {edge_key: float}  (fast path)
       └─ np.mean(values) → mean_per_edge_freq=0.917
            └─ evaluate_gate_v2(min_set=3, mean_freq=0.917) → PASS
                 └─ plot_gate_bar_v2() → figures/gate_metrics_v2.png
                      └─ serialize → h-e2-v2/experiment_results_phase3.json

Fallback (if key missing):
h-e1/experiment_results_phase3.json + TrustLLM scores
  └─ run_mst_analysis() [from h-e2/code/mst_analysis.py]
       └─ bootstrap_mst_stability() → edge_frequencies → mean → gate
```

---

## Output JSON Schema (experiment_results_phase3.json)

```json
{
  "hypothesis": "h-e2-v2",
  "gate_metric": "mean_per_edge_bootstrap_frequency",
  "mst_min_set_size": 3,
  "mst_min_set": ["truthfulness", "fairness", "privacy"],
  "mean_per_edge_bootstrap_frequency": 0.917,
  "per_edge_frequencies": {
    "privacy--safety": 1.0,
    "fairness--truthfulness": 1.0,
    "robustness--truthfulness": 0.941,
    "fairness--privacy": 0.956,
    "machine_ethics--privacy": 0.688
  },
  "topology_stability_h_e2": 0.606,
  "gate_primary_passed": true,
  "gate_secondary_passed": true,
  "gate_result": "PASS"
}
```
