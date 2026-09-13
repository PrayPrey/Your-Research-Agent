# Configuration Design: H-M3 — Parameter Extraction & Plausibility Validation

**Applied:** Inline constants pattern (scipy statistical extraction — no ML training loop)
**Applied:** Dataclass config pattern with YAML-serializable defaults

---

## Inherited Configuration

From `/docs/youra_research/h-m2/code/run.py` (verified from actual code):

| Config Key | H-M2 Value (actual) | H-M3 Status |
|-----------|---------------------|-------------|
| `p0` | `[0.9, 0.5, median(t)*0.3]` | Reused verbatim |
| `bounds.K` | `[0.8, 1.05]` | Reused verbatim |
| `bounds.r` | `[0.01, 5.0]` | Reused verbatim |
| `bounds.t0` | `[-20, 60]` | Reused verbatim |
| `maxfev` | `10000` | Reused verbatim |
| CI formula | `1.96 * sqrt(diag(pcov))` | Reused verbatim |

**Note:** H-M2 uses `p0 = [0.9, 0.5, np.median(t) * 0.3]` (data-dependent init). H-M3 inherits this exactly — no override.

---

## Configuration Schema

### YAML Config File (`h-m3/config.yaml`)

```yaml
# H-M3 Configuration
hypothesis_id: "H-M3"

# --- Logistic Fit Config (inherited from H-M2 actual code) ---
logistic_fit:
  p0: null                  # null = use H-M2 formula: [0.9, 0.5, median(t)*0.3]
  bounds:
    lower: [0.8, 0.01, -20.0]
    upper: [1.05, 5.0, 60.0]
  maxfev: 10000

# --- Plausibility Gate Thresholds (H-M3 new) ---
plausibility_gates:
  K:
    min: 0.85
    max: 1.0
  r:
    min: 0.0              # strict: r > 0 (not >=)
  t0_absolute:
    min: 6.0              # months since benchmark release
    max: 48.0
    relaxed_min: 0.0      # fallback if border case — must document justification
  ci_t0_width_max: 12.0   # 2 * 1.96 * perr[2] < 12.0

# --- Bootstrap CI Fallback (H-M3 new) ---
bootstrap:
  n_resamples: 500
  confidence: 0.95
  random_seed: 42         # deterministic fallback

# --- Benchmark Reference Config (H-M3 new) ---
benchmarks:
  glue:
    benchmark_id: "glue"
    release_offset: 0.0   # t=0 IS benchmark release in H-M2 data pipeline
  superglue:
    benchmark_id: "superglue"
    release_offset: 0.0

# --- Paths ---
paths:
  h_m2_code: "../h-m2/code"
  h_m2_results: "../h-m2/results.json"
  output_results: "h-m3/results.json"
  figures_dir: "h-m3/figures/"
```

---

## Python Dataclass Equivalents

```python
from dataclasses import dataclass, field
from typing import Optional, Tuple
from pathlib import Path


@dataclass
class LogisticFitConfig:
    """Inherited from H-M2 actual code — do not change without re-validating H-M2."""
    p0: Optional[list] = None        # None = use data-dependent formula
    bounds_lower: Tuple = (0.8, 0.01, -20.0)
    bounds_upper: Tuple = (1.05, 5.0, 60.0)
    maxfev: int = 10000


@dataclass
class PlausibilityGateConfig:
    K_min: float = 0.85
    K_max: float = 1.0
    r_min: float = 0.0             # strict: r > r_min (not >=)
    t0_abs_min: float = 6.0        # months since benchmark release
    t0_abs_max: float = 48.0
    t0_abs_relaxed_min: float = 0.0  # border case fallback
    ci_t0_width_max: float = 12.0   # months (2 * 1.96 * perr[2])


@dataclass
class BootstrapConfig:
    n_resamples: int = 500
    confidence: float = 0.95
    random_seed: int = 42


@dataclass
class BenchmarkRefConfig:
    benchmark_id: str
    release_offset: float = 0.0    # = 0: t=0 IS release in H-M2 data


@dataclass
class H_M3Config:
    logistic_fit: LogisticFitConfig = field(default_factory=LogisticFitConfig)
    plausibility: PlausibilityGateConfig = field(default_factory=PlausibilityGateConfig)
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    glue: BenchmarkRefConfig = field(
        default_factory=lambda: BenchmarkRefConfig(benchmark_id="glue", release_offset=0.0)
    )
    superglue: BenchmarkRefConfig = field(
        default_factory=lambda: BenchmarkRefConfig(benchmark_id="superglue", release_offset=0.0)
    )
    h_m2_code_path: Path = Path("../h-m2/code")
    h_m2_results_path: Path = Path("../h-m2/results.json")
    results_path: Path = Path("h-m3/results.json")
    figures_dir: Path = Path("h-m3/figures")
```

---

## Configuration Usage in run.py

```python
# Instantiate with defaults (no config file required for PoC)
cfg = H_M3Config()

# Plausibility check using config
flags = PlausibilityFlags(
    K_in_range=cfg.plausibility.K_min <= K <= cfg.plausibility.K_max,
    r_positive=r > cfg.plausibility.r_min,
    t0_in_range=cfg.plausibility.t0_abs_min <= t0_absolute <= cfg.plausibility.t0_abs_max,
    ci_t0_narrow=2 * ci_95[2] < cfg.plausibility.ci_t0_width_max,
)

# Bootstrap trigger
if not check_pcov_validity(pcov):
    ci_bounds = bootstrap_ci(t, y,
                             n_resamples=cfg.bootstrap.n_resamples,
                             confidence=cfg.bootstrap.confidence,
                             random_seed=cfg.bootstrap.random_seed)
```

---

## Config Decisions: New vs. Inherited

| Config | New / Inherited | Rationale |
|--------|----------------|-----------|
| logistic bounds, p0, maxfev | Inherited (H-M2 actual code) | Proven to converge (R²>0.99) |
| K gate [0.85, 1.0] | New (H-M3) | From Phase 2B spec |
| r gate (>0) | New (H-M3) | From Phase 2B spec |
| t0_absolute gate [6, 48] | New (H-M3) | From Phase 2B spec |
| CI width gate (<12 months) | New (H-M3) | From Phase 2B spec |
| release_offset=0 | New (H-M3) | Derived from H-M2 data pipeline analysis |
| bootstrap n=500, seed=42 | New (H-M3) | Standard practice, deterministic |

---

## Notes on release_offset

The `release_offset=0.0` is a critical H-M3 finding: in H-M2's data pipeline, `t=0` is already set to the benchmark release month (GLUE: April 2018, SuperGLUE: May 2019). Therefore `t0_absolute = t0_relative + 0 = t0_relative`. The negative t0 values from H-M2 (GLUE: −6.77, SuperGLUE: −2.85) mean the inflection point occurred **before** the first recorded leaderboard entry, which is physically plausible — benchmarks were already in rapid-growth phase when tracking began.

This is the key insight Phase 4 must verify: `t0_absolute < 6` may trigger the relaxed threshold path.
