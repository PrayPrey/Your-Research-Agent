# Logic: H-M3 — Second Derivative Crystallization Detection

Applied: signal-detection-pipeline (rolling-smooth -> differentiate -> peak-find -> aggregate)
Applied: multi-seed-statistical-validation (detection-rate + variance across seeds/benchmarks)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2) + upstream (H-E1)
**Status**: API verified from actual code (direct file read; Serena MCP unavailable in this environment)
**Analyzed Path**: `h-e1/code/detector.py`, `h-m2/code/config.py`
**Relevant Symbols**: `CrystallizationDetector.compute_second_derivative`, `CrystallizationDetector.detect_crystallization_peak` (h-e1/code/detector.py) — reference pattern only, not imported. `DetectionConfig`-style dataclass pattern (h-m2/code/config.py) — style reused, not imported.

No importable H-M2/H-E1 module is called directly by H-M3; H-M3 reimplements detection with `scipy.signal.find_peaks` per FR-4 instead of H-E1's `argmin`-only approach.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/detector.py (ACTUAL CODE, reference pattern only — not imported)
class CrystallizationDetector:
    def __init__(self, smoothing_window: int = 5): ...
    def compute_second_derivative(self) -> np.ndarray:
        """uniform_filter1d(wga, size=window) -> gradient -> gradient. Returns d2: [T]"""
    def detect_crystallization_peak(self, threshold: float = -0.01) -> tuple[int, float, bool]:
        """argmin over first half of d2. Returns (peak_idx, peak_value, is_significant)"""
```

**Verified from**: `h-e1/code/detector.py`. H-M3's `detector.py` upgrades this pattern: `find_peaks` w/ prominence instead of `argmin`, full-curve search instead of midpoint truncation, adds SNR.

Checkpoint access: `torch.load(path)` on `h-e1/code/checkpoints/waterbirds_epoch{N}.pt` — inspect dict keys at runtime (no fixed schema observed beyond epoch-indexed files); extract WGA scalar if key present, else return `None` and fall back to synthesis.

---

## A-1: Config module [Complexity: 5]

**Applied**: dataclass config pattern (from h-m2/code/config.py)

```python
# config.py
from dataclasses import dataclass, field

@dataclass
class DetectionConfig:
    benchmarks: list[str] = field(default_factory=lambda: ["waterbirds", "celeba", "coloredmnist"])
    n_seeds: int = 5
    epochs_by_benchmark: dict[str, int] = field(default_factory=lambda: {
        "waterbirds": 100, "celeba": 50, "coloredmnist": 30})
    smoothing_windows: list[int] = field(default_factory=lambda: [3, 5, 7])
    primary_window: int = 5
    prominence_threshold: float = 0.005
    h_e1_checkpoint_dir: str = "../../h-e1/code/checkpoints"
    detection_rate_target: float = 0.8
    variance_target_epochs: float = 5.0
    snr_target: float = 2.0
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"

CONFIG = DetectionConfig()
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Dataclass fields | benchmark/seed/window/epoch params |
| L-1-2 | Gate targets | detection_rate, variance, snr thresholds |
| L-1-3 | Path fields | checkpoint_dir, output_dir, figures_dir |
| L-1-4 | Module CONFIG instance | Singleton default |

---

## A-2: Real curve loader [Complexity: 9]

```python
# data.py
def load_wga_from_checkpoint(pt_path: str) -> float | None:
    """Load one checkpoint, extract WGA scalar. None if key missing/file absent."""
    ...

def load_real_curve(benchmark: str, checkpoint_dir: str, n_epochs: int) -> np.ndarray | None:
    """Iterate epoch files 1..n_epochs, call load_wga_from_checkpoint per epoch.
    Returns [n_epochs] array, or None if <50% epochs found (insufficient real data)."""
    ...
```

### Tensor Shapes
| Variable | Shape | Note |
|----------|-------|------|
| wga (per-epoch) | scalar float | Worst-group accuracy at one epoch |
| curve | [n_epochs] | Full trajectory, np.float64 |

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | `load_wga_from_checkpoint` | torch.load, key inspection, try/except -> None |
| L-2-2 | `load_real_curve` epoch loop | Build filename `{benchmark}_epoch{N}.pt`, collect |
| L-2-3 | Missing-data handling | Threshold check, return None to trigger fallback |
| L-2-4 | Logging | Warn on partial/missing coverage |

---

## A-3: Synthetic curve generator [Complexity: 8]

```python
def synthesize_curve(benchmark: str, seed: int, n_epochs: int, crystallization_epoch: int) -> np.ndarray:
    """Seeded sigmoid-with-dip WGA curve. Returns [n_epochs] float64 in [0,1]."""
    ...
```

### Pseudo-code
```
1. rng = np.random.default_rng(seed)
2. t = np.arange(n_epochs)
3. baseline = sigmoid rise from ~0.5 -> ~0.85 over training  # smooth learning curve
4. dip = gaussian_bump(center=crystallization_epoch, width=~3-5 epochs, depth=~0.1-0.2)
5. curve = baseline - dip + rng.normal(0, noise_std, n_epochs)
6. clip to [0, 1]
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Seeded RNG setup | `np.random.default_rng(seed)` |
| L-3-2 | Baseline sigmoid | Rising accuracy trend |
| L-3-3 | Crystallization dip | Gaussian bump subtracted at target epoch |
| L-3-4 | Noise + clip | Add noise, clip [0,1] |

---

## A-4: Smoothing + 2nd derivative [Complexity: 6]

```python
# detector.py
def smooth_curve(wga: np.ndarray, window_size: int) -> np.ndarray:
    """uniform_filter1d(wga, size=window_size, mode='nearest'). Returns [T]."""
    ...

def second_derivative(smoothed: np.ndarray) -> np.ndarray:
    """np.gradient applied twice. Returns [T], same length as input."""
    ...
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | `smooth_curve` | uniform_filter1d, mode='nearest' |
| L-4-2 | `second_derivative` | double np.gradient |
| L-4-3 | Edge-case guard | len(wga) < window -> return zeros_like |
| L-4-4 | Unit test | Known-shape curve -> expected peak location |

---

## A-5: Peak detection [Complexity: 8]

```python
def detect_peak(d2_wga: np.ndarray, prominence: float = 0.005) -> dict:
    """find_peaks(-d2_wga, prominence=prominence); pick max-prominence peak.
    Returns {'detected': bool, 'epoch': int|None, 'prominence': float|None, 'snr': float|None}"""
    ...
```

### Pseudo-code
```
1. peaks, props = find_peaks(-d2_wga, prominence=prominence)
2. if len(peaks) == 0: return {detected: False, epoch: None, prominence: None, snr: None}
3. best = argmax(props['prominences'])
4. snr = props['prominences'][best] / std(d2_wga)
5. return {detected: True, epoch: int(peaks[best]), prominence: float(props['prominences'][best]), snr: float(snr)}
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | find_peaks call | Negated d2, prominence kwarg |
| L-5-2 | Strongest-peak selection | argmax over prominences |
| L-5-3 | SNR calc | prominence / std(d2) |
| L-5-4 | No-peak-found path | Return detected=False dict |

---

## A-6: Sensitivity + aggregation [Complexity: 11]

```python
def run_sensitivity_analysis(wga: np.ndarray, windows: list[int] = [3, 5, 7],
                              prominence: float = 0.005) -> dict[str, dict]:
    """Per-window detect_peak. Returns {str(window): detect_peak_result}."""
    ...

# analyzer.py
def analyze_curve(benchmark: str, seed: int, wga: np.ndarray, config: "DetectionConfig") -> dict:
    """smooth+d2+detect at config.primary_window, plus run_sensitivity_analysis.
    Returns {'benchmark', 'seed', **primary_detect_peak_result, 'sensitivity': dict}"""
    ...

def aggregate_seed_results(results: list[dict]) -> dict:
    """Group by benchmark. Returns {benchmark: {'detection_rate': float,
    'timing_variance': float, 'mean_snr': float}}"""
    ...

def compute_window_robustness(sensitivity_results: dict, tolerance_epochs: int = 3) -> float:
    """% windows whose detected epoch is within tolerance of primary-window epoch."""
    ...

def compute_cross_benchmark_correlation(aggregated: dict[str, dict]) -> float:
    """Correlation of normalized (epoch / n_epochs) detection timing across benchmarks."""
    ...

def evaluate_gate(aggregated: dict[str, dict]) -> dict:
    """Checks detection_rate>0.8, variance<5, snr>2.0 per benchmark (or overall).
    Returns {'passed': bool, 'metrics': dict}"""
    ...
```

### Pseudo-code (aggregate_seed_results)
```
1. group results by benchmark
2. detected = [r for r in group if r['detected']]
3. detection_rate = len(detected) / len(group)
4. timing_variance = std([r['epoch'] for r in detected]) if detected else inf
5. mean_snr = mean([r['snr'] for r in detected]) if detected else 0.0
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | `run_sensitivity_analysis` + `analyze_curve` | Multi-window loop, primary+sensitivity merge |
| L-6-2 | `aggregate_seed_results` | Per-benchmark detection_rate/variance/snr |
| L-6-3 | `compute_window_robustness` + cross-benchmark corr | Tolerance-based agreement, np.corrcoef |
| L-6-4 | `evaluate_gate` | Threshold checks vs config targets |

---

## A-7: Visualization suite [Complexity: 9]

```python
# visualize.py
def plot_gate_metrics(gate_result: dict, save_path: str) -> None: ...
def plot_wga_with_derivatives(wga: np.ndarray, smoothed: np.ndarray, d2: np.ndarray,
                               peak_epoch: int | None, save_path: str) -> None: ...
def plot_window_comparison(sensitivity_results: dict, save_path: str) -> None: ...
def plot_detection_heatmap(all_results: dict, save_path: str) -> None: ...
def plot_snr_distribution(all_results: dict, save_path: str) -> None: ...
def plot_timing_variance(aggregated: dict, save_path: str) -> None: ...
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | `plot_gate_metrics` + `plot_wga_with_derivatives` | Bar chart; 3-panel raw/smoothed/d2 |
| L-7-2 | `plot_window_comparison` | Overlay d2 for [3,5,7] |
| L-7-3 | `plot_detection_heatmap` + `plot_snr_distribution` | Seeds x benchmarks matrix; boxplot |
| L-7-4 | `plot_timing_variance` | Bar chart per benchmark |

---

## A-8: run.py integration [Complexity: 7]

```python
# run.py
def main() -> None:
    """load_all_curves -> analyze_curve per (benchmark,seed) -> aggregate_seed_results ->
    evaluate_gate -> write outputs/detection_results.json, outputs/aggregated_metrics.yaml ->
    call all visualize.* functions."""
    ...
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Load + analyze loop | `load_all_curves`, iterate benchmark/seed |
| L-8-2 | Aggregate + gate | Call aggregate_seed_results, evaluate_gate |
| L-8-3 | JSON/YAML output | Write detection_results.json, aggregated_metrics.yaml |
| L-8-4 | Figure generation | Call visualize.py functions with results |

`load_all_curves(config: "DetectionConfig") -> dict[str, dict[int, np.ndarray]]` (data.py, orchestration entrypoint): tries `load_real_curve` per benchmark/seed, falls back to `synthesize_curve` when `None`. Returns `{benchmark: {seed_id: wga_array[n_epochs]}}`.
