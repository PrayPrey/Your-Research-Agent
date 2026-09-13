# Architecture: H-M3 — Unreliable Localization Causes Gradient Noise

**Type:** MECHANISM | **Prerequisites:** H-M1 (VALIDATED), H-M2 (VALIDATED)

Applied: gradient-concentration-metric-pattern (reuse H-M1 policy-gradient token attribution)
Applied: ast-heuristic-ground-truth-pattern (reuse H-M2 error-type-dispatch localization)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (dual: H-M1 + H-M2)
**Status**: patterns found from base code
**Analyzed Path**: `h-m1/code/`, `h-m2/code/`
**Findings**:
- H-M1 `gradient_analysis.py` computes gradients via **policy-gradient approximation** (`extract_token_gradients(model, input_ids, decoder_ids, rewards)`), NOT `loss.backward()` as the PRD/brief pseudocode suggests. Reuse must follow this actual signature — rewards tensor encodes penalty at target line (`-1.0` at target, `-0.1` elsewhere).
- H-M1 has no `ground_truth.py` — PRD's reuse table is aspirational; ground truth comes only from H-M2.
- H-M2 `ground_truth.py::find_bug_line_ast(code, error_type, traceback_str)` returns `actual_bug_line` per sample; dispatches on error_type via AST heuristics.
- Both H-M1 and H-M2 duplicate `parse_traceback_line`/`classify_error` — H-M3 imports from H-M1 (canonical per PRD FR-1).
- Config `U_LINE_ERRORS`/`U_IGNORE_ERRORS` sets differ slightly between H-M1 and H-M2 (H-M1 has `IndexError`/`KeyError` in U_LINE, H-M2 also does — consistent). H-M3 imports from H-M2's `config.py` per PRD.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| tokenize_with_lines | `from gradient_analysis import tokenize_with_lines` | `h-m1/code/gradient_analysis.py` |
| extract_token_gradients | `from gradient_analysis import extract_token_gradients` | `h-m1/code/gradient_analysis.py` |
| aggregate_gradients_by_line | `from gradient_analysis import aggregate_gradients_by_line` | `h-m1/code/gradient_analysis.py` |
| classify_error, parse_traceback_line | `from sample_collector import classify_error, parse_traceback_line` | `h-m1/code/sample_collector.py` |
| execute_code_safely | `from sample_collector import execute_code_safely` | `h-m1/code/sample_collector.py` |
| generate_synthetic_samples | `from sample_collector import generate_synthetic_samples` | `h-m1/code/sample_collector.py` |
| find_bug_line_ast, annotate_ground_truth | `from ground_truth import find_bug_line_ast, annotate_ground_truth` | `h-m2/code/ground_truth.py` |
| U_LINE_ERRORS, U_IGNORE_ERRORS | `from config import U_LINE_ERRORS, U_IGNORE_ERRORS` | `h-m2/code/config.py` |

**Verified from**: `h-m1/code/` and `h-m2/code/` (actual implementation, not specs). Both use `sys.path.insert(0, '../h-e1/code')` idiom — H-M3 code must sit adjacent (`h-m3/code/`) and add `../h-m1/code` and `../h-m2/code` to `sys.path`.

**Deviation note**: PRD implies `loss.backward()` on total_loss with an added "penalty" term. Actual H-M1 mechanism is a policy-gradient reward vector fed into `extract_token_gradients`. H-M3's `noise_analysis.py` reuses this exact function — target line gets reward `-1.0` (penalty), matching H-M1's proven pattern instead of inventing a new one.

---

## Module Structure

### noise_analysis.py (`h-m3/code/noise_analysis.py`)

**Dependencies**: gradient_analysis (H-M1), ground_truth (H-M2), config

```python
@dataclass
class NoiseSample:
    code: str
    traceback: str
    error_type: str          # "U_line" | "U_ignore"
    traceback_line: int
    ground_truth_line: int

def build_reward_vector(line_numbers: List[int], target_line: int) -> torch.Tensor: ...

def measure_sample_noise(
    model, tokenizer, sample: NoiseSample
) -> Optional[Dict[str, float]]:
    """Returns gt_grad, tb_grad, other_grad, gt_concentration, noise_ratio, traceback_matches_gt."""
    ...

def run_noise_analysis(
    model, tokenizer, samples: List[NoiseSample]
) -> Dict[str, List[Dict]]:
    """Stratified by error_type -> {"u_line": [...], "u_ignore": [...]}"""
    ...
```

### sample_builder.py (`h-m3/code/sample_builder.py`)

**Dependencies**: sample_collector (H-M1), ground_truth (H-M2), config

```python
def load_apps_dataset(split: str = "train"): ...

def collect_stratified_samples(
    model, tokenizer, dataset,
    n_per_category: int = 500, seed: int = 42,
) -> List[NoiseSample]:
    """Reuses H-M1 execute_code_safely + classify_error; annotates
    ground_truth via H-M2 find_bug_line_ast; balances U_line/U_ignore."""
    ...

def collect_synthetic_samples(n_per_category: int = 500, seed: int = 42) -> List[NoiseSample]:
    """Fallback: extend H-M1 generate_synthetic_samples with ground_truth_line."""
    ...
```

### stats_tests.py (`h-m3/code/stats_tests.py`)

**Dependencies**: scipy.stats, numpy

```python
def compare_concentration(u_line: List[float], u_ignore: List[float]) -> Dict[str, float]:
    """t-test, Mann-Whitney U, Cohen's d, bootstrap 95% CI."""
    ...

def summarize_noise_ratio(u_ignore_noise_ratios: List[float]) -> Dict[str, float]: ...
```

### visualization.py (`h-m3/code/visualization.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
def plot_concentration_boxplot(u_line: List[float], u_ignore: List[float], path: str) -> None: ...
def plot_noise_ratio_histogram(u_ignore_noise: List[float], path: str) -> None: ...
def plot_gradient_heatmap(sample_u_line: dict, sample_u_ignore: dict, path: str) -> None: ...
def plot_concentration_vs_noise_scatter(results: Dict[str, List[Dict]], path: str) -> None: ...
```

### config.py (`h-m3/code/config.py`)

```python
SEED = 42
MODEL_NAME = "Salesforce/codet5-small"
N_PER_CATEGORY = 500

@dataclass
class H_M3_Config:
    seed: int = SEED
    n_per_category: int = N_PER_CATEGORY
    output_dir: str = "results"
    figures_dir: str = "figures"
```

### run_analysis.py (`h-m3/code/run_analysis.py`)

**Dependencies**: all above modules

```python
def main() -> None:
    """Load model -> collect samples -> run_noise_analysis ->
    compare_concentration -> generate figures -> dump results/metrics.json."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | h-m3 config.py, sys.path wiring to h-m1/h-m2 | 4 | 1+2+1+0 |
| A-2 | Sample builder (real) | collect_stratified_samples: APPS load + H-M1 execute + H-M2 ground truth annotation, balance 500/500 | 15 | 4+4+4+3 |
| A-3 | Sample builder (synthetic fallback) | extend H-M1 synthetic templates with ground_truth_line | 6 | 2+2+1+1 |
| A-4 | Noise analysis core | build_reward_vector + measure_sample_noise using H-M1's extract_token_gradients | 13 | 3+4+4+2 |
| A-5 | Stratified runner | run_noise_analysis aggregating u_line/u_ignore result lists | 6 | 2+2+1+1 |
| A-6 | Statistical tests | t-test, Mann-Whitney, Cohen's d, bootstrap CI | 8 | 2+1+4+1 |
| A-7 | Visualization suite | 4 required figures (boxplot, histogram, heatmap, scatter) | 10 | 3+1+3+3 |
| A-8 | End-to-end pipeline | run_analysis.py orchestration, results/metrics.json dump | 7 | 2+3+1+1 |
| A-9 | Validation run | execute full pipeline on 1000 samples, verify PoC success criteria | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-4, A-7], Low(4-8): [A-1, A-3, A-5, A-6, A-8, A-9]
