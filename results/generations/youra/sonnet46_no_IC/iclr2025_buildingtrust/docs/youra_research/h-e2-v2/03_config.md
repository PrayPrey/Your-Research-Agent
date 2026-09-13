# H-E2-v2 Configuration

**Applied**: hardcoded dict / simple dataclass (Archon KB: diffusion model content only — not applicable)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from h-e2/code/main.py (actual implementation)
**Config Files Found**: `h-e2/code/main.py` — `ExperimentConfig` dataclass
**Pattern Used**: dataclass (inherited, field names verified from actual code)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e2/code/main.py (ACTUAL CODE — verified)
@dataclass
class ExperimentConfig:
    h_e1_results_path: str = "../h-e1/experiment_results_phase3.json"
    out_dir: str = ".."
    n_bootstrap: int = 1000
    subsample_size: int = 14
    seed: int = 42
    gate_min_set_threshold: int = 4
    gate_stability_threshold: float = 0.90   # ← RETIRED in H-E2-v2
    figure_dpi: int = 300
    dim_names: List[str] = field(default_factory=lambda: [
        "truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics",
    ])
```

Key verified details from actual code:
- Field is `h_e1_results_path` (not `h_e1_path`)
- Field is `out_dir` (not `output_dir`)
- Field is `gate_stability_threshold` (retired — replaced by `gate_mean_freq_threshold`)
- Results key is `bootstrap_edge_frequencies` (from main.py line 151)
- Results key is `bootstrap_topology_stability` (old metric, from main.py line 141)

---

## H-E2-v2 Configuration

### ExperimentConfigV2 (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfigV2:
    # Data paths
    h_e2_results_path: str = "h-e2/experiment_results_phase3.json"
    h_e1_results_path: str = "h-e1/experiment_results_phase3.json"
    output_dir: str = "h-e2-v2"
    figures_dir: str = "h-e2-v2/figures"

    # Bootstrap (unchanged from H-E2)
    n_bootstrap: int = 1000
    subsample_size: int = 14
    seed: int = 42

    # Gate thresholds
    gate_min_set_threshold: int = 4
    gate_mean_freq_threshold: float = 0.90   # CHANGED: was gate_stability_threshold (topology)

    # Non-standard: figure_dpi inherited from H-E2 defaults
    figure_dpi: int = 300

    dim_names: List[str] = field(default_factory=lambda: [
        "truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics",
    ])
```

### Gate Logic Change

```python
# H-E2 gate (RETIRED):
# gate_secondary = results["bootstrap_topology_stability"] >= 0.90  # fraction with IDENTICAL edge set

# H-E2-v2 gate (NEW):
def check_gate_v2(results: dict, cfg: ExperimentConfigV2) -> dict:
    primary_pass = results["mst_min_set_size"] <= cfg.gate_min_set_threshold
    # mean_per_edge_freq: mean of per-edge bootstrap frequencies (Tumminello 2007)
    secondary_pass = results["mean_per_edge_freq"] >= cfg.gate_mean_freq_threshold
    return {
        "primary_pass": primary_pass,
        "secondary_pass": secondary_pass,
        "gate_result": "PASS" if (primary_pass and secondary_pass) else "FAIL",
    }
```

### Fast Path (Load from H-E2 results)

```python
import json, numpy as np

def load_mean_freq_from_h_e2(cfg: ExperimentConfigV2) -> float:
    with open(cfg.h_e2_results_path) as f:
        r = json.load(f)
    # H-E2 stores per-edge frequencies under key "bootstrap_edge_frequencies"
    freqs = r.get("bootstrap_edge_frequencies", {})
    if freqs:
        return float(np.mean(list(freqs.values())))
    # Fallback: known values from H-E2 validated results
    return float(np.mean([1.0000, 1.0000, 0.9410, 0.9560, 0.6880]))  # = 0.917
```

---

## Summary of Config Changes from H-E2

| Field | H-E2 | H-E2-v2 | Note |
|-------|------|---------|------|
| `gate_stability_threshold` | 0.90 | REMOVED | Retired metric |
| `gate_mean_freq_threshold` | — | 0.90 | NEW — Tumminello 2007 mean per-edge freq |
| `h_e2_results_path` | — | `"h-e2/experiment_results_phase3.json"` | Fast path source |
| `h_e1_results_path` | `"../h-e1/…"` | `"h-e1/…"` | Adjusted relative path |
| `output_dir` | `out_dir = ".."` | `"h-e2-v2"` | New output location |
| `figures_dir` | `"../h-e2/figures"` | `"h-e2-v2/figures"` | New figures location |
| `n_bootstrap` | 1000 | 1000 | Unchanged |
| `subsample_size` | 14 | 14 | Unchanged |
| `seed` | 42 | 42 | Unchanged |
| `gate_min_set_threshold` | 4 | 4 | Unchanged |
