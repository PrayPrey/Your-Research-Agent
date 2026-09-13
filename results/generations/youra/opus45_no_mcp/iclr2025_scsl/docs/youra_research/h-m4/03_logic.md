# Logic: H-M4 — Benchmark-Relative Crystallization Timing Validation

Applied: multi-benchmark-normalization (reuse H-M3 detection, add timing % layer)
Applied: cross-benchmark-statistical-validation (compliance + variance gate)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3)
**Status**: API verified from actual code (direct file read; Serena MCP unavailable in this environment)
**Analyzed Path**: `h-m3/code/detector.py`, `h-m3/code/config.py`, `h-m3/code/data.py`
**Relevant Symbols**: `smooth_curve`, `second_derivative`, `detect_peak` (h-m3/code/detector.py) — imported directly, unmodified per FR-2. `DetectionConfig` (h-m3/code/config.py) — style reused for `BenchmarkConfig`. `load_all_curves`, `synthesize_curve`, `load_real_curve` (h-m3/code/data.py) — reused for curve acquisition.

**Critical API note**: H-M3's actual `detect_peak(d2_wga, prominence=0.005) -> dict` (not `detect_crystallization_peak` as named in 02c brief/PRD pseudo-code — that name is from H-E1's superseded reference pattern). H-M4 code MUST call `detect_peak`, `smooth_curve`, `second_derivative` exactly as defined in h-m3/code/detector.py.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m3/code/detector.py (ACTUAL CODE)
def smooth_curve(wga: np.ndarray, window_size: int) -> np.ndarray:
    """uniform_filter1d(wga, size=window_size, mode='nearest'). Returns [T]."""

def second_derivative(smoothed: np.ndarray) -> np.ndarray:
    """np.gradient applied twice. Returns [T], same length as input."""

def detect_peak(d2_wga: np.ndarray, prominence: float = 0.005) -> dict:
    """find_peaks(-d2_wga, prominence=prominence); pick max-prominence peak.
    Returns {'detected': bool, 'epoch': int|None, 'prominence': float|None, 'snr': float|None}"""

# From: h-m3/code/data.py (ACTUAL CODE)
def load_all_curves(config: "DetectionConfig") -> dict[str, dict[int, np.ndarray]]:
    """Returns {benchmark: {seed_id: wga_array[n_epochs]}}. Real checkpoint or synthetic fallback."""
```

**Verified from**: `h-m3/code/detector.py`, `h-m3/code/data.py`. H-M4 does NOT reimplement detection — imports these three functions directly (`from detector import smooth_curve, second_derivative, detect_peak` via sys.path append to `../../h-m3/code`, or vendored copy if cross-hypothesis import unsupported by harness).

---

## A-1: Config module [Complexity: 4]

**Applied**: dataclass config pattern (from h-m3/code/config.py)

```python
# config.py
from dataclasses import dataclass, field

@dataclass
class BenchmarkConfig:
    name: str
    total_epochs: int
    expected_range: tuple[float, float] = (20.0, 40.0)

@dataclass
class TimingConfig:
    benchmarks: dict[str, BenchmarkConfig] = field(default_factory=lambda: {
        "waterbirds": BenchmarkConfig("Waterbirds", 100, (20.0, 40.0)),
        "celeba": BenchmarkConfig("CelebA", 50, (20.0, 40.0)),
        "coloredmnist": BenchmarkConfig("ColoredMNIST", 30, (20.0, 40.0)),
    })
    n_seeds: int = 5
    smoothing_window: int = 5
    prominence_threshold: float = 0.005
    h_m3_code_dir: str = "../../h-m3/code"
    h_m3_checkpoint_dir: str = "../../h-e1/code/checkpoints"
    variance_target_percent: float = 10.0
    detection_rate_target: float = 0.8
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"

CONFIG = TimingConfig()
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | `BenchmarkConfig` dataclass | name, total_epochs, expected_range |
| L-1-2 | `TimingConfig` dataclass | benchmarks dict, seeds, window, prominence |
| L-1-3 | Gate target fields | variance_target_percent, detection_rate_target |
| L-1-4 | Module CONFIG instance + sys.path hook for h-m3 import | Singleton default |

---

## A-2: Timing normalization [Complexity: 3]

```python
# timing.py
def normalize_peak_timing(peak_epoch: int, total_epochs: int) -> float:
    """(peak_epoch / total_epochs) * 100.0. Returns percent in [0, 100]."""
    ...

def range_compliant(normalized_timing: float | None, expected_range: tuple[float, float]) -> bool:
    """expected_range[0] <= normalized_timing <= expected_range[1]. False if None."""
    ...
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | `normalize_peak_timing` | Division + scale to percent |
| L-2-2 | `range_compliant` | Bounds check with None guard |

---

## A-3: Per-run analysis (H-M3 integration) [Complexity: 9]

```python
# analyzer.py
from detector import smooth_curve, second_derivative, detect_peak  # h-m3, unmodified
from timing import normalize_peak_timing, range_compliant

def analyze_single_run(benchmark: str, seed: int, wga: np.ndarray,
                        bench_config: "BenchmarkConfig",
                        window: int = 5, prominence: float = 0.005) -> dict:
    """Full H-M3 detection pipeline + normalization for one (benchmark, seed) curve.
    wga: [n_epochs]. Returns single-run result dict (see Tensor Shapes)."""
    ...

def analyze_benchmark_timing(wga_curves: dict[str, dict[int, np.ndarray]],
                              configs: dict[str, "BenchmarkConfig"]) -> dict:
    """Iterate all benchmarks x seeds, call analyze_single_run.
    Returns {benchmark: {'runs': [dict,...], 'per_benchmark_summary': dict}}."""
    ...
```

### Pseudo-code (analyze_single_run)
```
1. smoothed = smooth_curve(wga, window)              # [n_epochs]
2. d2 = second_derivative(smoothed)                    # [n_epochs]
3. peak_info = detect_peak(d2, prominence)              # H-M3 unmodified call
4. if peak_info['detected']:
       norm_timing = normalize_peak_timing(peak_info['epoch'], bench_config.total_epochs)
       in_range = range_compliant(norm_timing, bench_config.expected_range)
   else:
       norm_timing, in_range = None, False
5. return {benchmark, seed, peak_epoch: peak_info['epoch'], total_epochs: bench_config.total_epochs,
           normalized_timing_percent: norm_timing, in_expected_range: in_range,
           expected_range: bench_config.expected_range, snr: peak_info['snr'],
           detected: peak_info['detected']}
```

### Tensor Shapes
| Variable | Shape | Note |
|----------|-------|------|
| wga | [n_epochs] | Per-benchmark, varies (30/50/100) |
| smoothed, d2 | [n_epochs] | Same length as wga |
| normalized_timing_percent | scalar float or None | 0-100 range |

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | `analyze_single_run` | Calls H-M3 detector fns + normalize/range_compliant |
| L-3-2 | `analyze_benchmark_timing` outer loop | benchmark x seed iteration |
| L-3-3 | `per_benchmark_summary` assembly | Mean/detected-count per benchmark within this fn |
| L-3-4 | Missing-curve guard | Skip seed if curve is None/empty |

---

## A-4: Cross-benchmark statistics + gate [Complexity: 8]

```python
# stats.py
def compute_timing_statistics(results: dict) -> dict:
    """Aggregate normalized timings across ALL detected runs (all benchmarks, all seeds).
    Returns {'success': bool, 'mean_normalized_timing': float, 'timing_variance_percent': float,
    'all_in_20_40_range': bool, 'benchmarks_in_range': int, 'total_benchmarks': int, 'gate_pass': bool}"""
    ...

def evaluate_range_compliance(results: dict, expected_range: tuple[float, float] = (20.0, 40.0)) -> dict:
    """Per-benchmark compliance rate across seeds.
    Returns {benchmark: {'compliance_rate': float, 'n_in_range': int, 'n_detected': int}}"""
    ...

def compute_seed_consistency(runs: list[dict]) -> dict:
    """Within-benchmark cross-seed variance. Returns {'mean': float, 'std': float, 'outlier_seeds': list[int]}."""
    ...

def evaluate_gate(stats: dict, compliance: dict, detection_rate: float,
                   config: "TimingConfig") -> dict:
    """PASS: all_in_range AND variance<target AND detection_rate>=target.
    CONDITIONAL: outside range but consistent (variance<15%). FAIL: otherwise.
    Returns {'status': 'PASS'|'CONDITIONAL'|'FAIL', 'metrics': dict}"""
    ...
```

### Pseudo-code (compute_timing_statistics)
```
1. valid = [r for benchmark_result in results.values() for r in benchmark_result['runs'] if r['detected']]
2. if len(valid) == 0: return {success: False, reason: 'No peaks detected'}
3. timings = [r['normalized_timing_percent'] for r in valid]
4. mean_timing, timing_variance = np.mean(timings), np.std(timings)
5. all_in_range = all(r['in_expected_range'] for r in valid)
6. benchmarks_in_range = count of benchmarks where >=1 seed in range (or majority-seed rule)
7. gate_pass = all_in_range and timing_variance < 10.0
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | `compute_timing_statistics` | Flatten all runs, mean/std, gate_pass bool |
| L-4-2 | `evaluate_range_compliance` | Per-benchmark % in range across seeds |
| L-4-3 | `compute_seed_consistency` | Per-benchmark seed std, >2std outlier flag |
| L-4-4 | `evaluate_gate` | 3-tier PASS/CONDITIONAL/FAIL per FR-7 |

---

## A-5: Visualization suite [Complexity: 9]

```python
# visualize.py
def plot_gate_metrics(gate_result: dict, save_path: str) -> None: ...
def plot_normalized_timing_bars(results: dict, expected_range: tuple, save_path: str) -> None: ...
def plot_wga_curves_overlay(wga_curves: dict, configs: dict, save_path: str) -> None: ...
def plot_timing_distribution(results: dict, save_path: str) -> None: ...
def plot_cross_benchmark_regression(results: dict, save_path: str) -> None: ...
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | `plot_gate_metrics` | Target vs actual bars (compliance, variance) |
| L-5-2 | `plot_normalized_timing_bars` | Per-benchmark % with 20-40% shaded band |
| L-5-3 | `plot_wga_curves_overlay` + `plot_timing_distribution` | 3-panel normalized-x curves; boxplot per benchmark |
| L-5-4 | `plot_cross_benchmark_regression` | epoch vs total_epochs scatter + fit line |

---

## A-6: run.py integration [Complexity: 7]

```python
# run.py
def main() -> None:
    """load_all_curves(config) [from h-m3/data.py, per benchmark/seed] ->
    analyze_benchmark_timing -> compute_timing_statistics -> evaluate_range_compliance ->
    compute_seed_consistency per benchmark -> evaluate_gate ->
    write outputs/timing_results.json, outputs/aggregated_metrics.yaml ->
    call all visualize.* functions."""
    ...
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Curve loading | `load_all_curves(CONFIG)` reused from h-m3/data.py |
| L-6-2 | Analysis + stats pipeline | analyze_benchmark_timing -> compute_timing_statistics -> evaluate_range_compliance |
| L-6-3 | Gate + output | evaluate_gate, write timing_results.json / aggregated_metrics.yaml |
| L-6-4 | Figure generation | Call all visualize.py functions with results |
