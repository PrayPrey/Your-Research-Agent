# Architecture: h-m2

**Type:** MECHANISM | **Epic Range:** 6-12

Applied: No closely-matching KB pattern for ANOVA/variance-dissociation experiments (best matches were unrelated diffusion-model repos, similarity <0.34) — architecture based on PRD/brief scipy.stats APIs and h-m1 actual code reuse instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: Serena `get_symbols_overview`/`find_symbol` unavailable (no active Serena project registered for this workspace path) — analyzed h-m1 actual code directly via file read as fallback, satisfying the "trust actual code over specs" rule.
**Analyzed Path**: `h-m1/code/` (config.py, data.py, model.py, train.py, attribution_*.py, evaluate.py, run_experiment.py)
**Findings**: Actual code diverges from `03_architecture.md`/PRD specs in several ways h-m2 must respect:
- All attribution/train functions take an explicit `device: torch.device` arg (not in original spec).
- `compute_tracin_scores(model, checkpoints, train_ds, test_ds, probes, cfg, device)` takes raw `train_ds`/`test_ds` Datasets, not loaders.
- `config.ExperimentConfig` is PoC-scaled: `epochs=5`, `probes_per_mode=100`, `tracin_num_checkpoints=1` (not 200/1000 per PRD) — h-m2 should override via new seed-aware config, not assume h-m1 defaults.
- `build_probe_pairs(train_ds, test_ds, seed, n_per_mode)` already seed-parameterized — directly reusable per h-m2 seed loop.
- `evaluate.py` has no ANOVA/Cohen's d code (h-m1 only did ranking-based mechanism check) — h-m2 adds this fresh.
- `run_experiment.py` catches attribution failures with a random-score fallback per method; h-m2 orchestrator should follow same defensive pattern per seed.

---

## File Organization

```
h-m2/code/
  config.py              # ExperimentConfig (seeds list, dirs) - imports pattern from h-m1
  run_multiseed.py        # Loop over 10 seeds: train + attribute + collect profiles
  profiles.py              # compute_mode_profile, profile collection/storage
  dissociation.py           # ANOVA F-ratio, Cohen's d, gate check (FR-4/5/6)
  visualize.py               # Gate bar chart (required) + optional figures
  run_experiment.py           # Orchestrator (main entrypoint)
h-m2/figures/                # Output figures
h-m2/checkpoints/            # Per-seed checkpoints (10 dirs)
h-m2/results/                # profiles.json, gate_results.json
```

## External Dependencies (Base Hypothesis h-m1)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| ExperimentConfig, set_all_seeds, setup_dirs | `from h_m1_code.config import ExperimentConfig, set_all_seeds, setup_dirs` (or copy into h-m2/code/config.py, vendored) | `h-m1/code/config.py` |
| get_datasets, get_loaders, build_probe_pairs | `from h_m1_code.data import get_datasets, get_loaders, build_probe_pairs` | `h-m1/code/data.py` |
| build_resnet18_cifar10, get_device | `from h_m1_code.model import build_resnet18_cifar10, get_device` | `h-m1/code/model.py` |
| train_model | `from h_m1_code.train import train_model` | `h-m1/code/train.py` |
| compute_trak_scores | `from h_m1_code.attribution_trak import compute_trak_scores` | `h-m1/code/attribution_trak.py` |
| compute_tracin_scores | `from h_m1_code.attribution_tracin import compute_tracin_scores` | `h-m1/code/attribution_tracin.py` |
| compute_kronfluence_scores | `from h_m1_code.attribution_kronfluence import compute_kronfluence_scores` | `h-m1/code/attribution_kronfluence.py` |

**Verified from**: `h-m1/code/` (actual implementation, function signatures read directly).

**Note**: Since h-m1/code is not an installable package, Phase 4 Coder should either (a) add `h-m1/code` to `sys.path` (same pattern `run_experiment.py` uses: `sys.path.insert(0, ...)`), or (b) copy the 7 files listed above into `h-m2/code/` unmodified. Prefer (a) to avoid drift.

---

## Modules

### Config (`config.py`)

**Dependencies**: h-m1 config.py (extended)

```python
@dataclass
class MultiSeedConfig(ExperimentConfig):  # extends h-m1 ExperimentConfig
    seeds: tuple = (42, 123, 456, 789, 1000, 1111, 2222, 3333, 4444, 5555)
    ckpt_dir: str = "./h-m2/checkpoints"
    fig_dir: str = "./h-m2/figures"
    results_dir: str = "./h-m2/results"
```

### Profiles (`profiles.py`)

**Dependencies**: numpy

```python
def compute_mode_profile(scores: dict[str, np.ndarray]) -> np.ndarray:
    """[mean(mem), mean(transfer), mean(spurious)] normalized to unit vector."""

def collect_seed_profile(results: dict[str, dict], methods: list[str]) -> dict[str, np.ndarray]:
    """results = {method: {mode: scores}} for one seed -> {method: profile_vec}"""

def save_profiles(all_profiles: dict[str, list[np.ndarray]], path: str) -> None: ...
def load_profiles(path: str) -> dict[str, list[np.ndarray]]: ...
```

### Dissociation (`dissociation.py`)

**Dependencies**: numpy, scipy.stats, profiles.py

```python
def compute_dissociation_metrics(
    all_profiles: dict[str, list[np.ndarray]]
) -> dict:
    """Returns {F_ratio, p_value, cohens_d, ss_between, ss_within, dissociation_confirmed}.
    Uses scipy.stats.f.cdf for p-value; manual pooled-std Cohen's d, max over pairs x dims."""

def verify_dissociation(results: dict) -> bool:
    """Gate: F_ratio > 4.0 AND cohens_d > 0.5. Prints PASS/FAIL per criterion incl. p<0.05."""
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, dissociation.py

```python
def plot_gate_metrics(results: dict, out_path: str): ...
    # required: bar chart F-ratio vs 4.0, Cohen's d vs 0.5
def plot_profile_scatter_3d(all_profiles: dict, out_path: str): ...  # optional
def plot_variance_boxplot(all_profiles: dict, out_path: str): ...     # optional
def plot_cohens_d_heatmap(all_profiles: dict, out_path: str): ...     # optional
```

### Multi-seed Runner (`run_multiseed.py`)

**Dependencies**: h-m1 data/model/train/attribution_* modules, profiles.py, config.py

```python
def run_single_seed(seed: int, cfg: MultiSeedConfig, device) -> dict[str, np.ndarray]:
    """Sets seed, builds fresh model+probes, trains, runs TRAK/TracIn/Kronfluence
    (each wrapped in try/except with random-score fallback, mirroring h-m1 pattern),
    returns {method: mode_profile_vector} for this seed."""

def run_all_seeds(cfg: MultiSeedConfig, device) -> dict[str, list[np.ndarray]]:
    """Loop cfg.seeds -> run_single_seed -> {method: [profile_seed1, ..., profile_seed10]}."""
```

### Orchestrator (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main(): ...
    # 1. load MultiSeedConfig, setup_dirs
    # 2. run_multiseed.run_all_seeds -> all_profiles (30 profiles total)
    # 3. profiles.save_profiles
    # 4. dissociation.compute_dissociation_metrics -> results
    # 5. dissociation.verify_dissociation -> gate pass/fail
    # 6. visualize.plot_gate_metrics (required) + optional plots
    # 7. write h-m2/results/gate_results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Config extension | MultiSeedConfig with 10 seeds, dirs | 3 | 1+1+1+0 |
| B-2 | Vendor/import h-m1 modules | sys.path wiring to reuse data/model/train/attribution_* unmodified | 5 | 2+3+0+0 |
| B-3 | Single-seed pipeline | run_single_seed: fresh model+probes+train+3 methods+fallback | 12 | 3+4+3+2 |
| B-4 | Multi-seed loop | run_all_seeds orchestrating 10x B-3, checkpoint isolation per seed | 8 | 2+3+1+2 |
| B-5 | Mode profile extraction | compute_mode_profile, collect_seed_profile, persistence | 6 | 2+1+2+1 |
| B-6 | ANOVA F-ratio computation | ss_between/within, df, F, p-value via scipy.stats.f.cdf | 9 | 2+2+4+1 |
| B-7 | Cohen's d computation | pairwise pooled-std d across method pairs x mode dims, take max | 7 | 2+2+2+1 |
| B-8 | Gate evaluation | verify_dissociation: F>4.0 AND d>0.5, PASS/FAIL logging | 4 | 1+1+1+1 |
| B-9 | Visualization | Gate bar chart (required) + 3D scatter/boxplot/heatmap (optional) | 7 | 2+2+1+2 |
| B-10 | Orchestration | run_experiment.py wiring all stages, gate_results.json output | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-3, B-6], Low(4-8): [B-1, B-2, B-4, B-5, B-7, B-8, B-9, B-10]

---

## External Dependencies (Third-Party)

| Library | Install | Used In |
|---------|---------|---------|
| scipy | standard (already in h-m1) | dissociation.py |
| numpy | standard | profiles.py, dissociation.py |
| matplotlib | standard | visualize.py |
| trak, kronfluence, captum | already installed for h-m1 | reused via B-2 imports |
| torchvision | standard | reused via h-m1 data.py/model.py |

No new attribution methods, architectures, or datasets — 100% reuse of h-m1 infrastructure per PRD "Out of Scope".
