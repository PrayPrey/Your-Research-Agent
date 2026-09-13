# Architecture: H-M2
# Depth-Slope Differential Analysis: MOHAWK-SSM vs LAWCAT

**Hypothesis:** H-M2 (MECHANISM — INCREMENTAL on H-E1)
**Date:** 2026-08-03

Applied: Pipeline pattern (sequential stage execution with fallback strategy per stage)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (reads H-E1 output files)
**Status:** H-E1 actual code analyzed — output format verified
**Analyzed Path:** `docs/youra_research/h-e1/code/evaluate.py`
**Findings:** H-E1 per-example JSON schema uses keys `category`, `pred`, `label`, `correct`, `scores` — NOT `domain`/`answer`/`context` as PRD spec assumes. Context field is NOT saved in H-E1 output. Full output file has top-level key `"per_example"` containing the list. LongBench v2 fallback merge (on `_id`) is mandatory, not optional, since context is absent from H-E1 results.

**CRITICAL MISMATCH — PRD vs Actual H-E1 output:**

| PRD Assumption | Actual H-E1 Schema |
|---------------|-------------------|
| `domain` field | `category` field (canonical form e.g. `multi_doc_qa`) |
| `answer` field | `label` field |
| `context` field present | ABSENT — must load from LongBench v2 |
| `_id` field | ABSENT — no example ID saved |
| flat list | nested under `output["per_example"]` |

H-E1 canonical category names for domain filter: `"multi_doc_qa"`, `"long_structured_data"` (from `RETRIEVAL_HEAVY` in config.py).

---

## External Dependencies (H-E1)

### Output File Paths (From Actual Code)

| File | Path | Key Fields |
|------|------|-----------|
| MOHAWK-SSM results | `docs/youra_research/h-e1/code/results/mohawk_longbench.json` | `per_example[].{category,pred,label,correct}` |
| LAWCAT results | `docs/youra_research/h-e1/code/results/lawcat_longbench.json` | `per_example[].{category,pred,label,correct}` |
| Evaluation summary | `docs/youra_research/h-e1/code/results/evaluation_summary.json` | `raw_accuracies`, `delta_norms` |

**Verified from:** `docs/youra_research/h-e1/code/evaluate.py` (actual implementation, lines 230–268)

### LongBench v2 Context Merge (Mandatory — context not in H-E1 output)

H-E1 does not save `context` or `_id`. Strategy: load LongBench v2 from HuggingFace, align by positional index within category (H-E1 iterates dataset in-order without shuffling), then compute depth_percentile from `context` field.

---

## File Structure

```
h-m2/
  code/
    config.py          # paths, thresholds, domain filter constants
    data_loader.py     # load H-E1 JSON + LongBench v2 merge
    depth_computer.py  # depth_percentile computation per example
    regression.py      # rpy2+lme4 primary / statsmodels fallback (strategy pattern)
    gate_evaluator.py  # ratio + CI non-overlap test + PASS/PARTIAL/FAIL
    visualizer.py      # 4 figures
    reporter.py        # JSON results + Markdown summary
    run_analysis.py    # CLI entrypoint: wires all stages end-to-end
  figures/
  h_m2_results.json
  h_m2_summary.md
```

---

## Modules

### Config (`code/config.py`)

**Dependencies:** none

```python
# H-E1 output paths (verified from actual h-e1/code/evaluate.py)
H_E1_RESULTS_DIR = "docs/youra_research/h-e1/code/results"
MOHAWK_RESULTS_JSON = f"{H_E1_RESULTS_DIR}/mohawk_longbench.json"
LAWCAT_RESULTS_JSON  = f"{H_E1_RESULTS_DIR}/lawcat_longbench.json"

# Alternative paths to probe if primary missing
H_E1_ALT_PATHS = [
    "docs/youra_research/h-e1/results",
    "h-e1/code/results",
    "h-e1/outputs",
]

# Domain filter (H-E1 canonical category names from CATEGORY_MAP)
RETRIEVAL_CATEGORIES = {"multi_doc_qa", "long_structured_data"}

# LongBench v2 HuggingFace fallback (for context field)
LONGBENCH_HF_ID = "THUDM/LongBench"
LONGBENCH_HF_CONFIG = "v2"

# Statistical thresholds
GATE_RATIO_THRESHOLD = 2.0
MIN_SAMPLES_PER_MODEL = 100
DEPTH_FALLBACK_VALUE = 0.5
HOLM_N_TESTS = 2

# Output paths
OUTPUT_DIR = "docs/youra_research/h-m2"
FIGURES_DIR = f"{OUTPUT_DIR}/figures"
RESULTS_JSON = f"{OUTPUT_DIR}/h_m2_results.json"
SUMMARY_MD   = f"{OUTPUT_DIR}/h_m2_summary.md"
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies:** config, json, datasets (HuggingFace)

```python
def load_h_e1_results(json_path: str) -> list[dict]:
    """
    Load H-E1 per-example results. Returns list from output["per_example"].
    Each dict: {category, pred, label, correct, scores}.
    Probes H_E1_ALT_PATHS if primary path missing.
    """
    ...

def load_longbench_v2() -> dict[str, list[dict]]:
    """
    Load LongBench v2 from HuggingFace. Returns {canonical_category: [examples]}.
    Each example: {context, input, options, answer, ...}.
    Applies same CATEGORY_MAP normalization as H-E1 evaluate.py.
    """
    ...

def merge_context(
    h_e1_records: list[dict],
    longbench_by_category: dict[str, list[dict]],
) -> list[dict]:
    """
    Align H-E1 records with LongBench v2 by positional index within category.
    Adds 'context', 'question', 'answer_text' fields to each record.
    H-E1 iterates dataset in-order — positional alignment is valid.
    Returns merged list with all fields needed for depth computation.
    """
    ...

def filter_retrieval_subset(records: list[dict]) -> list[dict]:
    """Filter to RETRIEVAL_CATEGORIES. Raises ValueError if < MIN_SAMPLES_PER_MODEL."""
    ...

def load_and_prepare(
    mohawk_path: str,
    lawcat_path: str,
) -> tuple[list[dict], list[dict]]:
    """
    Top-level: load both models, merge context, filter retrieval subset.
    Returns (mohawk_records, lawcat_records).
    """
    ...
```

---

### DepthComputer (`code/depth_computer.py`)

**Dependencies:** config, re

```python
def extract_keywords(question: str, answer_text: str, top_n: int = 5) -> list[str]:
    """
    Extract content words (length ≥ 4, non-stopword) from question + answer_text.
    Returns top_n longest distinct tokens.
    """
    ...

def compute_depth_percentile(record: dict) -> float:
    """
    Compute depth_percentile = earliest_keyword_pos / len(context).
    Convention: 0 = answer at end, 1 = answer at beginning.
    Falls back to DEPTH_FALLBACK_VALUE if no keyword found.
    """
    ...

def add_depth_percentiles(records: list[dict]) -> list[dict]:
    """
    Apply compute_depth_percentile to each record. Adds 'depth_percentile' field.
    Validates: nunique > 10, all in [0,1].
    Returns records with depth_percentile added (in-place mutation, also returns list).
    """
    ...

def depth_stats(records: list[dict]) -> dict:
    """Returns {mean, std, min, max, fallback_fraction} of depth_percentile."""
    ...
```

---

### RegressionFitter (`code/regression.py`)

**Dependencies:** config, pandas, numpy, rpy2 (optional), statsmodels

```python
def fit_glmer_rpy2(df: "pd.DataFrame") -> dict:
    """
    Primary: rpy2 + lme4::glmer(correct ~ depth_percentile + (1|task_id), family=binomial).
    Returns {beta, ci_low, ci_high, p_value, method="glmer"}.
    Raises ImportError if rpy2/R unavailable.
    """
    ...

def fit_mixedlm_statsmodels(df: "pd.DataFrame") -> dict:
    """
    Fallback: statsmodels.formula.api.mixedlm (linear approximation for binary outcome).
    Returns {beta, ci_low, ci_high, p_value, method="mixedlm_approx"}.
    Adds warning flag: result["approximation_warning"] = True.
    """
    ...

def fit_model(records: list[dict], model_label: str) -> dict:
    """
    Strategy: try fit_glmer_rpy2 first; on ImportError fall back to fit_mixedlm_statsmodels.
    Constructs DataFrame from records (columns: depth_percentile, correct, task_id).
    task_id = record["category"] (sub_domain if available).
    Returns regression result dict with model_label added.
    """
    ...

def apply_holm_correction(p_values: list[float]) -> list[float]:
    """Holm-Bonferroni correction for HOLM_N_TESTS tests. Returns corrected p-values."""
    ...
```

---

### GateEvaluator (`code/gate_evaluator.py`)

**Dependencies:** config

```python
def compute_ratio(ssm_result: dict, lawcat_result: dict) -> float:
    """abs(beta_SSM) / max(abs(beta_LAWCAT), 1e-9)"""
    ...

def cis_overlap(ssm_result: dict, lawcat_result: dict) -> bool:
    """True if 95% CIs overlap."""
    ...

def evaluate_gate(ssm_result: dict, lawcat_result: dict) -> dict:
    """
    Returns {
        gate_status: "PASS"|"PARTIAL"|"FAIL",
        gate_pass: bool,
        ratio: float,
        cis_overlap: bool,
        rationale: str,
    }.
    PASS: ratio >= 2.0 AND NOT overlap.
    PARTIAL: ratio >= 2.0 OR beta_SSM significantly < 0.
    FAIL: otherwise.
    """
    ...
```

---

### Visualizer (`code/visualizer.py`)

**Dependencies:** config, matplotlib, seaborn, numpy

```python
def plot_gate_metrics_bar(
    ssm_result: dict, lawcat_result: dict, gate: dict, output_path: str
) -> None:
    """FR-5.1: Bar chart |beta| with CI error bars + 2x reference line."""
    ...

def plot_depth_accuracy_scatter(
    mohawk_records: list[dict], lawcat_records: list[dict], output_path: str
) -> None:
    """FR-5.2: Scatter depth_percentile vs correct (jittered), logistic fit curves."""
    ...

def plot_depth_quartile_accuracy(
    mohawk_records: list[dict], lawcat_records: list[dict], output_path: str
) -> None:
    """FR-5.3: Accuracy by depth quartile [Q1..Q4] for both models."""
    ...

def plot_beta_forest(
    ssm_result: dict, lawcat_result: dict, gate: dict, output_path: str
) -> None:
    """FR-5.4: Forest plot beta_depth + 95% CIs, ratio annotation."""
    ...

def generate_all_figures(
    mohawk_records: list[dict],
    lawcat_records: list[dict],
    ssm_result: dict,
    lawcat_result: dict,
    gate: dict,
    figures_dir: str,
) -> None:
    """Generate all 4 figures. Creates figures_dir if needed."""
    ...
```

---

### Reporter (`code/reporter.py`)

**Dependencies:** config, json

```python
def build_results_dict(
    ssm_result: dict,
    lawcat_result: dict,
    gate: dict,
    ssm_holm_p: float,
    lawcat_holm_p: float,
    ssm_records: list[dict],
    lawcat_records: list[dict],
) -> dict:
    """
    Builds full results dict matching FR-6.1 JSON schema:
    {gate_pass, ratio, mohawk_ssm, lawcat, sample_sizes,
     holm_corrected_p_values, depth_percentile_stats}.
    """
    ...

def save_json(results: dict, output_path: str) -> None: ...

def save_markdown(results: dict, gate: dict, output_path: str) -> None:
    """FR-6.2: Regression table + gate verdict + figure references."""
    ...
```

---

### RunAnalysis (`code/run_analysis.py`)

**Dependencies:** all modules above

```python
def run(
    mohawk_path: str = MOHAWK_RESULTS_JSON,
    lawcat_path: str  = LAWCAT_RESULTS_JSON,
    figures_dir: str  = FIGURES_DIR,
    results_json: str = RESULTS_JSON,
    summary_md: str   = SUMMARY_MD,
) -> dict:
    """
    End-to-end pipeline:
    1. load_and_prepare(mohawk_path, lawcat_path)
    2. add_depth_percentiles for each model
    3. fit_model for each model
    4. apply_holm_correction
    5. evaluate_gate
    6. generate_all_figures
    7. save_json + save_markdown
    Returns full results dict.
    """
    ...

if __name__ == "__main__":
    # argparse: --mohawk, --lawcat, --figures-dir, --output-dir
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & Project Setup | Write config.py, create directory structure, define H-E1 output path probing logic, pin dependencies in requirements.txt | 5 | 1+1+1+2 |
| A-2 | DataLoader — H-E1 JSON Loading | Implement load_h_e1_results with alt-path probing; validate schema keys (category/pred/label/correct); handle nested per_example key | 8 | 2+2+2+2 |
| A-3 | DataLoader — LongBench v2 Context Merge | Load LongBench v2 from HuggingFace; align by positional index within category (same traversal order as H-E1); add context/question fields | 11 | 3+2+3+3 |
| A-4 | DepthComputer | Keyword extraction, depth_percentile = earliest_pos / len(context), fallback, validation asserts, depth_stats | 8 | 2+1+3+2 |
| A-5 | RegressionFitter | rpy2+lme4::glmer primary; statsmodels.mixedlm fallback; strategy dispatch; DataFrame construction; Holm correction | 14 | 3+3+4+4 |
| A-6 | GateEvaluator | Ratio computation, CI overlap test, PASS/PARTIAL/FAIL classification | 5 | 1+1+2+1 |
| A-7 | Visualizer — 4 Figures | Bar chart (gate metrics), scatter+logistic fit, quartile bar chart, forest plot | 10 | 2+2+3+3 |
| A-8 | Reporter — JSON + Markdown | Build results dict matching FR-6.1 schema, save JSON, generate Markdown table with gate verdict | 6 | 1+1+2+2 |
| A-9 | RunAnalysis Entrypoint + Integration Test | Wire pipeline stages in run_analysis.py; argparse CLI; end-to-end test with synthetic fixture data verifying ratio ≥ 2 detection | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-3, A-7, A-9], Low(4-8): [A-1, A-2, A-4, A-6, A-8]
