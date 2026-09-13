# Architecture: H-P2
## Spurious Probe Accuracy vs WGA Correlation (Exploratory)

**Generated:** 2026-08-05
**Type:** MECHANISM (Exploratory Correlation) — Incremental extension of H-M3
**Tier:** FULL

Applied: scipy-bootstrap-pearsonr

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m3)
**Status:** Patterns found from base code
**Analyzed Path:** `docs/youra_research/h-m3/code/`
**Findings:** Two files — `config.py` (constants) + `run_experiment.py` (monolithic script with all logic: `load_resnet50`, `get_transform`, `get_loader`, `extract_layer4_features`, `run_probe`, `run_all_probes`, `paired_ttest`, `gate_verdict`, `save_figures`, `save_results`, `main`). All 9 probe accuracies already exist in `h-m3/results.json` (ERM×3, SAM×3, GroupDRO×3). Note: `config.py` has `WGA_BY_METHOD_SEED` with `sam_seed*: 0.78` — differs from Izmailov 2022 Table 1 value of 0.74; H-P2 must use 0.74 per PRD.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| extract_layer4_features | `from h_m3_code.run_experiment import extract_layer4_features` | `h-m3/code/run_experiment.py:58-79` |
| run_probe | `from h_m3_code.run_experiment import run_probe` | `h-m3/code/run_experiment.py:82-96` |
| load_resnet50 | `from h_m3_code.run_experiment import load_resnet50` | `h-m3/code/run_experiment.py` |
| get_transform | `from h_m3_code.run_experiment import get_transform` | `h-m3/code/run_experiment.py` |
| get_loader | `from h_m3_code.run_experiment import get_loader` | `h-m3/code/run_experiment.py` |

**Verified from:** `docs/youra_research/h-m3/code/` (actual implementation)

**Note:** H-M3 is a monolithic script, not a package. H-P2 will use `sys.path` injection or inline copy of key functions rather than package imports. All 9 probe accuracies already exist in `h-m3/results.json` → SAM feature re-extraction is NOT needed.

**Critical config discrepancy:** H-M3 `config.py` uses `sam_seed*: 0.78` for WGA; H-P2 PRD specifies 0.74 from Izmailov 2022 Table 1. H-P2 hardcodes 0.74.

---

## File Structure

```
h-p2/
├── code/
│   ├── config.py          # H-P2 constants (paths, thresholds, WGA values)
│   └── run_correlation.py # Main script: loads H-M3 results → correlation → figures
├── figures/
│   ├── scatter_probe_vs_wga.png
│   ├── bootstrap_distribution.png
│   ├── method_comparison_bar.png
│   └── ablation_sensitivity.png
└── results.json
```

---

## Modules

### Config (`code/config.py`)

**Dependencies:** None (stdlib `os` only)

```python
H_M3_RESULTS_JSON: str  # absolute path to h-m3/results.json
H_M3_CODE_DIR: str      # absolute path to h-m3/code/ (for sys.path if needed)
CHECKPOINT_ARCHIVE: str # same as h-m3 config
WILDS_CACHE: str        # "/home/PrayPrey/.wilds_cache"

BASE_DIR: str           # h-p2/ directory
FIGURES_DIR: str        # h-p2/figures/
RESULTS_JSON: str       # h-p2/results.json
VERIFICATION_STATE: str # docs/youra_research/verification_state.yaml

# WGA ground truth (Izmailov 2022 Table 1 — 0.74 for SAM, not 0.78)
WGA_VALUES: dict        # {"erm_seed1": 0.72, ..., "sam_seed1": 0.74, ..., "groupdro_seed1": 0.88, ...}
METHODS: list           # ["erm", "sam", "groupdro"]
SEEDS: list             # [1, 2, 3]
METHOD_COLORS: dict     # {"erm": "blue", "sam": "orange", "groupdro": "green"}

BOOTSTRAP_N: int        # 1000
BOOTSTRAP_RNG: int      # 42
CI_LEVEL: float         # 0.95

# Verdict thresholds
CONFIRMED_R: float      # -0.5
CONFIRMED_CI_HIGH: float # 0.0
SUGGESTIVE_R: float     # -0.3

# Probe params (for fallback re-extraction only)
PROBE_C: float          # 1e9
PROBE_SOLVER: str       # "lbfgs"
PROBE_MAX_ITER: int     # 1000
PROBE_RANDOM_STATE: int # 42
BATCH_SIZE: int         # 100
```

---

### CorrelationExperiment (`code/run_correlation.py`)

**Dependencies:** config, h-m3/results.json (primary), h-m3/code/run_experiment.py (fallback)

```python
# --- Data assembly ---
def load_probe_accs_from_hm3(results_path: str) -> dict[str, float]:
    """Load all_probe_results from h-m3/results.json. Returns {key: acc}."""
    ...

def extract_sam_probes_fallback(device: str) -> dict[str, float]:
    """Fallback: re-extract SAM×3 features + fit probe. Uses h-m3 functions via sys.path."""
    ...

def assemble_dataset() -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Returns:
        probe_accs: shape (9,)
        wga_values: shape (9,)
        labels: list of 9 checkpoint keys (e.g., ["erm_seed1", ...])
    """
    ...

# --- Statistics ---
def compute_pearsonr(probe_accs: np.ndarray, wga_values: np.ndarray) -> tuple[float, float]:
    """One-sided Pearson r test (alternative='less'). Returns (r, p_value)."""
    ...

def compute_bootstrap_ci(
    probe_accs: np.ndarray, wga_values: np.ndarray
) -> tuple[float, float, str]:
    """BCa bootstrap with percentile fallback. Returns (ci_low, ci_high, method_used)."""
    ...

def classify_verdict(r: float, p: float, ci_low: float, ci_high: float) -> str:
    """Returns 'CONFIRMED' | 'SUGGESTIVE' | 'REJECTED'."""
    ...

# --- Ablations ---
def run_ablation_variants(
    probe_accs: np.ndarray, wga_values: np.ndarray, labels: list[str]
) -> dict:
    """
    Runs 3 variants:
      - full_n9: all 9 checkpoints
      - erm_groupdro_n6: exclude SAM
      - method_means_n3: per-method mean (3 points)
    Returns dict with r, p, ci_low, ci_high, verdict per variant.
    """
    ...

# --- Figures ---
def plot_scatter(probe_accs, wga_values, labels, r, p, out_path: str) -> None:
    """Scatter probe_acc vs WGA, color by method, regression line, r+p annotated."""
    ...

def plot_bootstrap_dist(probe_accs, wga_values, ci_low, ci_high, out_path: str) -> None:
    """Histogram of 1000 bootstrap r values with CI bounds marked."""
    ...

def plot_method_comparison(probe_accs, wga_values, labels, out_path: str) -> None:
    """Bar chart: mean probe_acc and WGA per method with seed error bars."""
    ...

def plot_ablation_sensitivity(ablation_results: dict, out_path: str) -> None:
    """Bar chart: Pearson r for full-9, ERM+GroupDRO-6, method-means-3."""
    ...

def save_figures(probe_accs, wga_values, labels, stats, ablation_results) -> None:
    """Generates and saves all 4 required figures to config.FIGURES_DIR."""
    ...

# --- I/O ---
def save_results(probe_accs, wga_values, labels, stats, ablation_results) -> None:
    """Writes h-p2/results.json per PRD schema."""
    ...

def update_verification_state(verdict: str, stats: dict) -> None:
    """Appends H-P2 gate result to verification_state.yaml."""
    ...

def main() -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup project structure | Create h-p2/code/, h-p2/figures/, config.py with correct WGA values (SAM=0.74 not 0.78) | 5 | 1+1+1+2 |
| A-2 | Load H-M3 probe results | Read h-m3/results.json, extract all 9 probe accs, validate completeness | 5 | 1+2+1+1 |
| A-3 | Assemble 9-point dataset | Pair probe_accs with WGA ground truth, build ordered arrays; include fallback path for missing SAM data | 7 | 2+2+2+1 |
| A-4 | Pearson r + one-sided p-value | scipy.stats.pearsonr with alternative='less'; classify verdict | 6 | 1+2+2+1 |
| A-5 | Bootstrap CI (BCa + fallback) | scipy.stats.bootstrap paired=True, BCa→percentile fallback for n=9 degeneracy | 9 | 2+2+3+2 |
| A-6 | Ablation variants | Run correlation for n=9 (full), n=6 (ERM+GroupDRO), n=3 (method means) | 7 | 2+2+2+1 |
| A-7 | Figure 1: scatter + regression | probe_acc vs WGA, color by method, regression line, r+p annotation | 8 | 2+2+2+2 |
| A-8 | Figure 2: bootstrap distribution | Histogram of 1000 bootstrap r values with 95% CI bounds | 7 | 2+1+2+2 |
| A-9 | Figures 3+4: method comparison + ablation | Bar charts for method-level means and ablation r values | 7 | 2+1+2+2 |
| A-10 | Results serialization | Save h-p2/results.json per PRD schema + update verification_state.yaml | 6 | 1+2+1+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5], Low(4-8): [A-1, A-2, A-3, A-4, A-6, A-7, A-8, A-9, A-10]

---

## Implementation Notes

1. All 9 probe accuracies exist in `h-m3/results.json` under `all_probe_results`. SAM fallback path (`extract_sam_probes_fallback`) is defensive only.
2. `run_probe` in H-M3 scores on train features (not test). PRD requires test set scoring. Verify with actual code before reusing; may need test features passed separately.
3. WGA discrepancy: H-M3 config uses SAM=0.78; PRD/Izmailov 2022 says 0.74. H-P2 hardcodes 0.74 and reports note in results.json.
4. Bootstrap at n=9 is borderline — log which CI method was used (`ci_method` field in results.json).
