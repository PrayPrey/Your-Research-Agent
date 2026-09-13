# Logic: H-M3
# Transition Epoch t* Reproducibility Analysis

**Hypothesis ID:** H-M3
**Type:** MECHANISM (Post-hoc Statistical Analysis)
**Date:** 2026-05-04

Applied: threshold-based-transition-detection (H-E1 analyze.py find_t_star pattern)
Applied: bootstrap-CI-resampling (numpy random resampling pattern)
Applied: dataclass-config (H-E1 config.py pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/20260504_scsl/h-e1/code/`
**Relevant Symbols**:
- `find_t_star(delta_mean, epochs, threshold=0.02, consecutive=3) -> int` — h-e1/code/analyze.py:67
- `evaluate_gate(window_fraction, p_value, cfg) -> dict` — h-e1/code/analyze.py:81
- `run_analysis(results_df, cfg) -> dict` — h-e1/code/analyze.py:104, saves to `h-e1_results.json`
- JSON schema: `output["per_seed"][i]` has keys `seed`, `delta_curve`, `epochs`, `gap_area`, `t_star`
- `ExperimentConfig` has nested `train`, `probe`, `gate`, `paths` — h-e1/code/config.py:59

**Key difference**: H-E1 `find_t_star` returns `int(epochs[-1])` (never None). H-M3 reimplements returning `Optional[int]` with adaptive fallback.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/analyze.py (ACTUAL CODE)
# H-E1 JSON output schema (read by DeltaCurveLoader._load_from_json):
# {
#   "per_seed": [
#     {
#       "seed": int,
#       "delta_curve": List[float],   # length = n_checkpoints
#       "epochs": List[int],          # checkpoint epoch numbers
#       "gap_area": float,
#       "t_star": int
#     }, ...
#   ]
# }
# File: cfg.results_dir + "/h-e1_results.json"  (e.g. "./results/h-e1/h-e1_results.json")

# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class GateConfig:
    t_star_delta_threshold: float = 0.02   # ← actual field name
    t_star_consecutive: int = 3             # ← actual field name
```

---

## A-2: DeltaCurveLoader [Complexity: 14, Budget: 4]

### API Signatures

```python
class DeltaCurveLoader:
    def __init__(self, cfg: ExperimentConfig):
        """Initialize with config; resolve h-e1 paths."""
        self.cfg = cfg
        self.results_dir: str = cfg.paths.h_e1_results_dir
        self.checkpoint_dir: str = cfg.paths.h_e1_checkpoint_dir

    def load(self) -> Dict[int, np.ndarray]:
        """Load delta(t) arrays for all seeds.
        Returns: {seed_int: array[n_checkpoints]} — float32, values in [-1, 1]
        Priority: JSON > per-seed .npy > checkpoint regeneration
        """

    def _load_from_json(self) -> Optional[Dict[int, np.ndarray]]:
        """Parse h-e1_results.json per_seed[i].delta_curve.
        Returns: {seed: np.ndarray[n_checkpoints]} or None if file missing/malformed
        """

    def _load_from_npy(self, seed: int) -> Optional[np.ndarray]:
        """Load results_dir/delta_t_seed{seed}.npy.
        Returns: np.ndarray[n_checkpoints] or None if not found
        """

    def _regenerate_from_checkpoints(self, seed: int) -> np.ndarray:
        """Fallback: load ResNet-50 checkpoints, run probe, compute delta(t).
        Returns: np.ndarray[n_checkpoints] — length = n_epochs // checkpoint_interval
        """

    def validate(self, curves: Dict[int, np.ndarray]) -> None:
        """Assert len(curves) >= 3, each array len >= 15. Log shapes. Raise ValueError."""
```

### Pseudo-code: `load()`

```
seeds = cfg.analysis.seeds

# Attempt 1: JSON
result = _load_from_json()
if result and all seeds present: return result

# Attempt 2: per-seed .npy
curves = {}
for seed in seeds:
    arr = _load_from_npy(seed)
    if arr: curves[seed] = arr
if len(curves) == len(seeds): return curves

# Attempt 3: checkpoint regeneration for missing seeds
for seed in seeds not in curves:
    curves[seed] = _regenerate_from_checkpoints(seed)

validate(curves)
return curves
```

### Pseudo-code: `_regenerate_from_checkpoints(seed)`

```
checkpoints = sorted glob(checkpoint_dir/seed_{seed}/epoch_*.pt)
delta_list = []
for ckpt in checkpoints:
    model = load ResNet-50 backbone from ckpt
    features_train = extract_features(model, train_loader)   # [N, 2048]
    features_val   = extract_features(model, val_loader)     # [M, 2048]
    probe = LogisticRegression(C=1.0).fit(features_train, spurious_labels_train)
    spurious_acc = probe.score(features_val, spurious_labels_val)
    probe2 = LogisticRegression(C=1.0).fit(features_train, core_labels_train)
    core_acc = probe2.score(features_val, core_labels_val)
    delta_list.append(spurious_acc - core_acc)
return np.array(delta_list, dtype=np.float32)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | json_loader | `_load_from_json`: open h-e1_results.json, parse per_seed[i].delta_curve |
| L-2-2 | npy_loader | `_load_from_npy`: glob delta_t_seed{N}.npy, load with np.load |
| L-2-3 | checkpoint_regen | `_regenerate_from_checkpoints`: ResNet-50 feature extract + probe fit |
| L-2-4 | validate_and_load | `load()` orchestration + `validate()` shape/count assertions |

---

## A-3: TransitionEpochAnalyzer [Complexity: 12, Budget: 2]

### API Signatures

```python
class TransitionEpochAnalyzer:
    def __init__(self, cfg: ExperimentConfig):
        """Read threshold and n_consecutive from cfg.analysis."""
        self.threshold: float = cfg.analysis.threshold        # 0.02
        self.n_consecutive: int = cfg.analysis.n_consecutive  # 3
        self.checkpoint_interval: int = cfg.analysis.checkpoint_interval  # 2

    def find_t_star(
        self,
        delta_curve: np.ndarray,       # [n_checkpoints]
        threshold: Optional[float] = None,
        n_consecutive: Optional[int] = None,
    ) -> Optional[int]:
        """Return epoch of first transition (delta < threshold for n_consecutive steps).
        epoch = checkpoint_index * checkpoint_interval
        Returns None if transition not found.
        """

    def find_t_star_adaptive(self, delta_curve: np.ndarray) -> Optional[int]:
        """Try find_t_star with default threshold; if None retry with 0.5 * min(delta_curve).
        Returns Optional[int] epoch number.
        """

    def compute_gap_area(self, delta_curve: np.ndarray) -> float:
        """Return sum(max(delta(t), 0)) across all checkpoints. Scalar."""

    def analyze_across_seeds(self, delta_curves: Dict[int, np.ndarray]) -> dict:
        """Run find_t_star_adaptive + compute_gap_area per seed.
        Returns dict with keys:
          t_star_per_seed: Dict[int, Optional[int]]
          mean_t_star: float  (over valid seeds only)
          std_t_star: float
          gap_areas: Dict[int, float]
          mean_gap_area: float
          valid_seed_count: int
          used_adaptive_threshold: Dict[int, bool]
        """
```

### Pseudo-code: `find_t_star()`

```
# Mirror H-E1 analyze.py:67 but return None instead of epochs[-1]
threshold = threshold or self.threshold
n_consecutive = n_consecutive or self.n_consecutive
count = 0
for i, d in enumerate(delta_curve):
    if d < threshold:
        count += 1
        if count >= n_consecutive:
            start_idx = i - n_consecutive + 1
            return start_idx * self.checkpoint_interval
    else:
        count = 0
return None
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | find_t_star_impl | `find_t_star` + `find_t_star_adaptive` with adaptive retry |
| L-3-2 | aggregate | `compute_gap_area` + `analyze_across_seeds` aggregation logic |

---

## A-4: StatisticalValidator [Complexity: 14, Budget: 2]

### API Signatures

```python
class StatisticalValidator:
    def __init__(self, cfg: ExperimentConfig):
        """Read gate thresholds and bootstrap params from cfg.analysis."""
        self.n_bootstrap: int = cfg.analysis.n_bootstrap          # 10000
        self.bootstrap_seed: int = cfg.analysis.bootstrap_seed    # 42
        self.std_gate_threshold: float = cfg.analysis.std_gate_threshold  # 10.0

    def bootstrap_std_ci(
        self,
        t_star_values: List[float],
        n_resamples: int = 10000,
    ) -> Tuple[float, float]:
        """95% bootstrap CI for std(t*). Returns (ci_low, ci_high)."""

    def bootstrap_mean_ci(
        self,
        values: List[float],
        n_resamples: int = 10000,
    ) -> Tuple[float, float]:
        """95% bootstrap CI for mean(values). Returns (ci_low, ci_high)."""

    def evaluate_gate(self, analysis_results: dict) -> dict:
        """MUST_WORK gate: std(t*) < std_gate_threshold over >= 3 valid seeds.
        Returns dict: {gate_passed, decision, std_t_star, ci_95_std: (lo, hi),
                       partial_pass, insufficient_data, criteria}
        """

    def verify_mechanism_activated(self, results: dict) -> Tuple[bool, dict]:
        """4 indicators: all_seeds_found_t_star, std_below_threshold,
        gap_area_positive, curves_loaded.
        Returns (all_pass: bool, indicators: dict)
        """

    def run_full_validation(self, analysis_results: dict) -> dict:
        """Combine gate + mechanism + CI. Returns unified validation dict."""
```

### Pseudo-code: `bootstrap_std_ci()`

```
rng = np.random.default_rng(self.bootstrap_seed)
vals = np.array(t_star_values)
boot_stds = []
for _ in range(n_resamples):
    sample = rng.choice(vals, size=len(vals), replace=True)
    boot_stds.append(np.std(sample, ddof=1))
ci_low  = np.percentile(boot_stds, 2.5)
ci_high = np.percentile(boot_stds, 97.5)
return (float(ci_low), float(ci_high))
```

### Pseudo-code: `evaluate_gate()`

```
t_star_per_seed = analysis_results["t_star_per_seed"]
valid = [v for v in t_star_per_seed.values() if v is not None]
if len(valid) < 3:
    return {gate_passed: False, insufficient_data: True, decision: "FAIL", ...}
std_val = np.std(valid, ddof=1)
ci = bootstrap_std_ci(valid)
gate_passed = std_val < self.std_gate_threshold
partial = (not gate_passed) and std_val < 2 * self.std_gate_threshold
return {
    gate_passed: gate_passed,
    decision: "PASS" if gate_passed else ("PARTIAL-PASS" if partial else "FAIL"),
    std_t_star: std_val,
    ci_95_std: ci,
    partial_pass: partial,
    insufficient_data: False,
    criteria: {std_gate_threshold: self.std_gate_threshold, min_seeds: 3}
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | bootstrap_ci | `bootstrap_std_ci` + `bootstrap_mean_ci` with rng seeding |
| L-4-2 | gate_and_verify | `evaluate_gate` + `verify_mechanism_activated` + `run_full_validation` |

---

## A-8: Integration Test [Complexity: 9, Budget: 0]

No subtask budget allocated. Implementation: single test script that runs `main("configs/waterbirds.yaml")` against H-E1 JSON output and asserts `validation_results["gate_passed"] == True`.

---

*Logic for H-M3 — post-hoc statistical analysis, no new model training*
*Generated: 2026-05-04*
