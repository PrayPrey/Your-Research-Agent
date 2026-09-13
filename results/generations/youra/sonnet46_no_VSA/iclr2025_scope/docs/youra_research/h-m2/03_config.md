# Config: H-M2
# Depth-Slope Differential Analysis: MOHAWK-SSM vs LAWCAT

**Hypothesis:** H-M2 (MECHANISM — INCREMENTAL on H-E1)
**Date:** 2026-08-03

Applied: No domain-relevant KB patterns found (similarity < 0.50); using standard Python dataclass defaults.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (reads H-E1 output files)
**Status**: H-E1 actual code verified — `docs/youra_research/h-e1/code/config.py` read directly
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: module-level constants (H-E1 style) + dataclass for H-M2 analysis config

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual H-E1 Code)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE — verified)

# H-E1 paths (Path objects resolved from __file__)
RESULTS_DIR = HYPOTHESIS_DIR / "results"   # → docs/youra_research/h-e1/results/
FIGURES_DIR  = HYPOTHESIS_DIR / "figures"  # → docs/youra_research/h-e1/figures/

# Canonical category names used in H-E1 per-example JSON
RETRIEVAL_HEAVY = {"multi_doc_qa", "long_structured_data"}  # ← used as H-M2 domain filter

# LongBench v2 dataset identifier (same dataset H-M2 needs for context merge)
LONGBENCH_DATASET = ("THUDM/LongBench", "v2")
```

**Critical verified finding:** H-E1 `evaluate.py` saves results to
`HYPOTHESIS_DIR/results/mohawk_longbench.json` and `lawcat_longbench.json`
under key `"per_example"`. The `category` field uses snake_case canonical names
matching `RETRIEVAL_HEAVY` above. There is no `context` or `_id` field —
LongBench v2 context merge is mandatory, not optional.

---

## A-7: Visualizer — 4 Figures [Complexity: 10, Budget: 2 subtasks]

### C-7-1: Visualization Config Dataclass

```python
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class VizConfig:
    # Figure dimensions
    figure_size: Tuple[float, float] = (8.0, 6.0)
    figure_size_wide: Tuple[float, float] = (10.0, 6.0)   # scatter + quartile plots
    dpi: int = 150

    # Model colors (MOHAWK=red, LAWCAT=blue — fixed per architecture identity)
    color_mohawk: str = "#D62728"   # matplotlib tab:red
    color_lawcat: str = "#1F77B4"   # matplotlib tab:blue
    color_reference_line: str = "#2CA02C"  # green for 2x reference line

    # Scatter jitter
    jitter_amplitude: float = 0.05  # ±0.05 vertical jitter on binary correct axis

    # Depth quartile bin edges (equal-width [0,1] split into Q1..Q4)
    quartile_edges: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.50, 0.75, 1.0])
    quartile_labels: List[str] = field(default_factory=lambda: ["Q1\n0-25%", "Q2\n25-50%", "Q3\n50-75%", "Q4\n75-100%"])

    # Typography
    font_size_title: int = 13
    font_size_axis: int = 11
    font_size_tick: int = 10
    font_size_legend: int = 10
    font_size_annotation: int = 9

    # Legend placement
    legend_loc: str = "best"   # matplotlib auto; override per plot if needed

    # Error bar style (CI bars on beta estimates)
    capsize: int = 5
    linewidth_ci: float = 2.0
```

**YAML schema:**
```yaml
viz:
  figure_size: [8.0, 6.0]
  figure_size_wide: [10.0, 6.0]
  dpi: 150
  color_mohawk: "#D62728"
  color_lawcat: "#1F77B4"
  color_reference_line: "#2CA02C"
  jitter_amplitude: 0.05
  quartile_edges: [0.0, 0.25, 0.50, 0.75, 1.0]
  quartile_labels: ["Q1\n0-25%", "Q2\n25-50%", "Q3\n50-75%", "Q4\n75-100%"]
  font_size_title: 13
  font_size_axis: 11
  font_size_tick: 10
  font_size_legend: 10
  font_size_annotation: 9
  legend_loc: "best"
  capsize: 5
  linewidth_ci: 2.0
```

**Calibration notes:**
- `jitter_amplitude`: 0.05 is standard for binary scatter; increase to 0.08 if points overlap heavily with N > 200.
- `dpi`: 150 is sufficient for paper-quality PNG; raise to 300 for publication PDF.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | VizConfig dataclass | Figure size, DPI, colors, jitter, quartile edges, fonts, legend, CI bar style |
| C-7-2 | Figure output path config | Per-figure filename constants, FIGURES_DIR, PNG/PDF toggle |

---

### C-7-2: Figure Output Path Config

```python
from dataclasses import dataclass


@dataclass
class FigurePathConfig:
    figures_dir: str = "docs/youra_research/h-m2/figures"

    # Per-figure filename stems (extension controlled by output_format)
    gate_metrics_stem: str = "gate_metrics"
    depth_scatter_stem: str = "depth_accuracy_scatter"
    depth_quartile_stem: str = "depth_quartile_accuracy"
    beta_forest_stem: str = "beta_forest_plot"

    # Output format toggle: "png" for quick PoC, "pdf" for publication
    output_format: str = "png"   # calibration: switch to "pdf" for paper submission

    def path(self, stem: str) -> str:
        return f"{self.figures_dir}/{stem}.{self.output_format}"

    @property
    def gate_metrics(self) -> str:
        return self.path(self.gate_metrics_stem)

    @property
    def depth_scatter(self) -> str:
        return self.path(self.depth_scatter_stem)

    @property
    def depth_quartile(self) -> str:
        return self.path(self.depth_quartile_stem)

    @property
    def beta_forest(self) -> str:
        return self.path(self.beta_forest_stem)
```

**YAML schema:**
```yaml
figure_paths:
  figures_dir: "docs/youra_research/h-m2/figures"
  gate_metrics_stem: "gate_metrics"
  depth_scatter_stem: "depth_accuracy_scatter"
  depth_quartile_stem: "depth_quartile_accuracy"
  beta_forest_stem: "beta_forest_plot"
  output_format: "png"   # "png" or "pdf"
```

**Calibration notes:**
- `figures_dir`: environment-specific if running outside repo root; pass `--figures-dir` via CLI.
- `output_format`: `"png"` for PoC; `"pdf"` for Matplotlib vector output for papers.

---

## A-9: RunAnalysis / Integration Config [Complexity: 9, Budget: 2 subtasks]

### C-9-1: H-M2AnalysisConfig Dataclass

```python
from dataclasses import dataclass, field
from typing import List, Set


@dataclass
class H_M2AnalysisConfig:
    # --- H-E1 input paths (verified from h-e1/code/evaluate.py output logic) ---
    # calibration: these paths are environment-specific; pass via CLI --mohawk / --lawcat
    mohawk_results_json: str = "docs/youra_research/h-e1/code/results/mohawk_longbench.json"
    lawcat_results_json: str  = "docs/youra_research/h-e1/code/results/lawcat_longbench.json"

    # Ordered alt-path prefixes probed if primary file is missing
    h_e1_alt_path_prefixes: List[str] = field(default_factory=lambda: [
        "docs/youra_research/h-e1/results",
        "h-e1/code/results",
        "h-e1/outputs",
    ])

    # --- Domain filter (H-E1 canonical category names from RETRIEVAL_HEAVY) ---
    retrieval_categories: Set[str] = field(
        default_factory=lambda: {"multi_doc_qa", "long_structured_data"}
    )

    # --- LongBench v2 context merge (mandatory — H-E1 does not save context) ---
    longbench_hf_id: str = "THUDM/LongBench"
    longbench_hf_config: str = "v2"

    # --- Statistical thresholds ---
    gate_ratio_threshold: float = 2.0      # |beta_SSM| / |beta_LAWCAT| >= 2.0 for PASS
    min_samples_per_model: int = 100       # minimum retrieval-subset examples per model
    depth_fallback_value: float = 0.5      # used when no keyword found in context
    holm_n_tests: int = 2                  # number of tests for Holm-Bonferroni correction
    keyword_top_n: int = 5                 # top-N keywords extracted per example
    bm25_fallback_threshold: float = 0.5   # switch to BM25 if fallback fraction exceeds this

    # --- Output paths ---
    output_dir: str = "docs/youra_research/h-m2"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    results_json: str = "docs/youra_research/h-m2/h_m2_results.json"
    summary_md: str   = "docs/youra_research/h-m2/h_m2_summary.md"

    # --- Sub-configs ---
    viz: VizConfig = field(default_factory=VizConfig)
    figure_paths: FigurePathConfig = field(default_factory=FigurePathConfig)
```

**YAML schema:**
```yaml
h_m2:
  mohawk_results_json: "docs/youra_research/h-e1/code/results/mohawk_longbench.json"
  lawcat_results_json:  "docs/youra_research/h-e1/code/results/lawcat_longbench.json"

  h_e1_alt_path_prefixes:
    - "docs/youra_research/h-e1/results"
    - "h-e1/code/results"
    - "h-e1/outputs"

  retrieval_categories:
    - "multi_doc_qa"
    - "long_structured_data"

  longbench_hf_id: "THUDM/LongBench"
  longbench_hf_config: "v2"

  gate_ratio_threshold: 2.0
  min_samples_per_model: 100
  depth_fallback_value: 0.5
  holm_n_tests: 2
  keyword_top_n: 5
  bm25_fallback_threshold: 0.5

  output_dir: "docs/youra_research/h-m2"
  figures_dir: "docs/youra_research/h-m2/figures"
  results_json: "docs/youra_research/h-m2/h_m2_results.json"
  summary_md:   "docs/youra_research/h-m2/h_m2_summary.md"

  viz:
    # ... (VizConfig fields above)
  figure_paths:
    # ... (FigurePathConfig fields above)
```

**Calibration notes:**
- `mohawk_results_json` / `lawcat_results_json`: environment-specific — always override via `--mohawk` / `--lawcat` CLI args or environment variable if paths differ.
- `gate_ratio_threshold`: fixed at 2.0 per H-M2 hypothesis definition — do not tune.
- `bm25_fallback_threshold`: 0.5 means "if > 50% examples fall back to depth=0.5, use BM25". Empirical; calibrate after first data load.
- `keyword_top_n`: 5 is a reasonable default; increase if fallback fraction is high.

---

### C-9-2: Integration Test Fixture Config

```python
from dataclasses import dataclass, field
from typing import List
import random


@dataclass
class FixtureConfig:
    """
    Synthetic data spec for integration test.
    Produces two model record-sets where MOHAWK has steep depth slope (beta ~ -2.0)
    and LAWCAT has flat slope (beta ~ -0.5), ensuring ratio >= 2 detection.
    """
    seed: int = 42
    n_examples: int = 50                            # per model
    n_categories: int = 2                           # "multi_doc_qa", "long_structured_data"
    categories: List[str] = field(
        default_factory=lambda: ["multi_doc_qa", "long_structured_data"]
    )

    # Depth percentile distribution: uniform [0.1, 0.9] to avoid boundary effects
    depth_low: float = 0.1
    depth_high: float = 0.9

    # MOHAWK: steep negative slope — P(correct) decreases sharply as depth decreases
    # logistic: P = sigmoid(intercept + slope * depth_percentile)
    mohawk_intercept: float = 1.5    # high accuracy at depth=1.0
    mohawk_slope: float = -3.0       # sharp drop toward depth=0.0 (far from surface)

    # LAWCAT: flat slope — weakly affected by depth
    lawcat_intercept: float = 0.5
    lawcat_slope: float = -0.8       # shallow drop

    # Expected gate outcome from this fixture
    expected_gate_status: str = "PASS"
    expected_ratio_min: float = 2.0  # fixture must produce ratio >= 2.0

    # Validation assertions for integration test
    assert_gate_pass: bool = True
    assert_ratio_ge: float = 2.0
    assert_mohawk_beta_lt: float = 0.0   # beta_SSM must be negative
    assert_lawcat_beta_gt: float = -2.0  # beta_LAWCAT must be less steep than SSM


def make_fixture_records(cfg: FixtureConfig, model_label: str) -> List[dict]:
    """
    Generate synthetic records matching H-E1 merged-record schema.
    Each record: {category, pred, label, correct, depth_percentile, task_id}
    """
    import math
    rng = random.Random(cfg.seed)
    if model_label == "mohawk":
        intercept, slope = cfg.mohawk_intercept, cfg.mohawk_slope
    else:
        intercept, slope = cfg.lawcat_intercept, cfg.lawcat_slope

    records = []
    for i in range(cfg.n_examples):
        depth = rng.uniform(cfg.depth_low, cfg.depth_high)
        logit = intercept + slope * depth
        p_correct = 1.0 / (1.0 + math.exp(-logit))
        correct = 1 if rng.random() < p_correct else 0
        cat = cfg.categories[i % cfg.n_categories]
        records.append({
            "category": cat,
            "depth_percentile": depth,
            "correct": correct,
            "task_id": cat,
            "pred": "A" if correct else "B",
            "label": "A",
        })
    return records
```

**YAML schema (fixture section):**
```yaml
fixture:
  seed: 42
  n_examples: 50
  n_categories: 2
  categories: ["multi_doc_qa", "long_structured_data"]
  depth_low: 0.1
  depth_high: 0.9
  mohawk_intercept: 1.5
  mohawk_slope: -3.0
  lawcat_intercept: 0.5
  lawcat_slope: -0.8
  expected_gate_status: "PASS"
  expected_ratio_min: 2.0
  assert_gate_pass: true
  assert_ratio_ge: 2.0
  assert_mohawk_beta_lt: 0.0
  assert_lawcat_beta_gt: -2.0
```

**Calibration notes:**
- `mohawk_slope = -3.0` / `lawcat_slope = -0.8`: ratio of |slopes| = 3.75 > 2.0, ensuring the fixture reliably triggers PASS with N=50. If statsmodels CI is wide at N=50 and CIs overlap, increase `n_examples` to 100.
- `seed = 42`: fixed for deterministic test. Do not randomize in CI.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | H_M2AnalysisConfig dataclass | Top-level config: gate threshold, min samples, Holm N, depth fallback, H-E1 paths + alt-paths, output paths, sub-configs |
| C-9-2 | Integration test fixture config | FixtureConfig + make_fixture_records: N=50, 2 categories, controlled logistic slopes producing ratio >= 2 PASS |
