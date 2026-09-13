---
name: H-M1 Configuration Design
hypothesis: H-M1
type: configuration
tier: FULL
---

Applied: Statistical-Analysis-Pipeline
Applied: Panel-Regression-FE
Applied: Geometric-Projection-Pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: dataclass (nested, with module-level constants)

---

## Inherited Configuration (Base Hypothesis)

Verified from `/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_bi_align_3/docs/youra_research/20260503_bi_align/h-e1/code/config.py` (actual implementation):

| Field | Actual Name in Code | Actual Default |
|-------|---------------------|----------------|
| Dataset HH-RLHF | `HH_RLHF_DATASET` | `"Anthropic/hh-rlhf"` |
| Dataset WebGPT | `WEBGPT_DATASET` | `"openai/webgpt_comparisons"` |
| Rounds | `N_ROUNDS` | `3` |
| Bootstrap iters | `BOOTSTRAP_ITERS` | `200` (not 1000 — verified from code) |
| Permutation iters | `PERMUTATION_ITERS` | `200` (not 1000 — verified from code) |
| Random seed | `RANDOM_SEED` | `42` |
| Bonferroni K | `BONFERRONI_K` | `3` |
| Alpha corrected | `ALPHA_CORRECTED` | `0.0167` |
| Brier gate | `BRIER_GATE_THRESHOLD` | `0.02` (dataclass) / not set as constant |
| LR params | `LR_PARAMS` | `{"C": 1.0, "max_iter": 1000, "solver": "lbfgs", "class_weight": "balanced", "random_state": 42}` |
| Hedge words | `HEDGE_WORDS` | list of 16 phrases |
| Struct markers | `STRUCT_MARKERS` | list of 13 markers |

**Note**: `BOOTSTRAP_ITERS` and `PERMUTATION_ITERS` are `200` in actual H-E1 code, not 1000. H-M1 raises to `1000` for mechanism-level rigor.

---

## config.py — Complete Content

```python
# h-m1/code/config.py
# H-M1: Automation-Bias-Mediated Ambiguity-Modulated AI-Norm Internalization
# Extends H-E1 config — field names verified from h-e1/code/config.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

# ---------------------------------------------------------------------------
# Inherited from H-E1 (verified from h-e1/code/config.py)
# ---------------------------------------------------------------------------

HH_RLHF_DATASET: str = "Anthropic/hh-rlhf"
WEBGPT_DATASET: str = "openai/webgpt_comparisons"
N_ROUNDS: int = 3
BOOTSTRAP_ITERS: int = 1000   # H-M1 raises from H-E1's 200 for mechanism rigor
PERMUTATION_ITERS: int = 1000  # H-M1 raises from H-E1's 200
RANDOM_SEED: int = 42
BONFERRONI_K: int = 3
ALPHA_CORRECTED: float = 0.0167
BRIER_GATE_THRESHOLD: float = 0.02  # verified from h-e1 DataConfig
LR_PARAMS: Dict[str, Any] = {
    "C": 1.0,
    "max_iter": 1000,
    "solver": "lbfgs",
    "class_weight": "balanced",
    "random_state": 42,
}
HEDGE_WORDS: List[str] = [
    "i think", "i believe", "perhaps", "possibly", "might", "may",
    "could", "probably", "seems", "appears", "arguably", "likely",
    "uncertain", "not sure", "unclear", "i'm not certain",
]
STRUCT_MARKERS: List[str] = [
    "\n-", "\n*", "1.", "2.", "3.", "##", "**",
    "first,", "second,", "third,", "finally,",
    "in conclusion,", "to summarize,", "in summary,",
]

# ---------------------------------------------------------------------------
# New for H-M1
# ---------------------------------------------------------------------------

ENCODER_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
ENCODER_BATCH_SIZE: int = 256
EMBED_DIM: int = 384
CUMULATIVE_TOKENS_SCALE: float = 1000.0       # tokens-per-unit for regression
AMBIGUITY_KAPPA_THRESHOLD: float = 0.4        # Fleiss kappa threshold (from H-E1 AnalysisConfig)
EFFECT_SIZE_THRESHOLD: float = 0.1            # SD per 1000 tokens
FIGURES_DIR: str = "../figures"
RESULTS_JSON: str = "../results/results.yaml"
MIN_SESSIONS_PER_WORKER: int = 3
MIN_WORKERS: int = 100
PANEL_COV_TYPE: str = "clustered"             # clustered SE by worker_id
BETA_EXPOSURE_MIN: float = 0.0               # gate: beta must be > 0 (directional)
AMBIGUITY_SCORE_THRESHOLD: float = 0.4       # |score_0 - score_1| split threshold
HH_RLHF_AMBIGUITY_KAPPA: float = 0.4        # Fleiss kappa for HH-RLHF ambiguity split


# ---------------------------------------------------------------------------
# Paths dataclass
# ---------------------------------------------------------------------------

@dataclass
class Paths:
    base_dir: Path
    h_e1_code_dir: Path
    hypothesis_dir: Path
    figures_dir: Path
    results_dir: Path
    code_dir: Path
    tests_dir: Path

    @classmethod
    def from_base(cls, base_dir: Path) -> "Paths":
        base_dir = Path(base_dir)
        hypothesis_dir = base_dir / "docs" / "youra_research" / "20260503_bi_align" / "h-m1"
        return cls(
            base_dir=base_dir,
            h_e1_code_dir=base_dir / "docs" / "youra_research" / "20260503_bi_align" / "h-e1" / "code",
            hypothesis_dir=hypothesis_dir,
            figures_dir=hypothesis_dir / "figures",
            results_dir=hypothesis_dir / "results",
            code_dir=hypothesis_dir / "code",
            tests_dir=hypothesis_dir / "tests",
        )


# ---------------------------------------------------------------------------
# Flat ExperimentConfig dataclass (copy-paste ready for run_experiment.py)
# ---------------------------------------------------------------------------

@dataclass
class ExperimentConfig:
    # Dataset
    hh_rlhf_dataset: str = HH_RLHF_DATASET
    webgpt_dataset: str = WEBGPT_DATASET
    n_rounds: int = N_ROUNDS
    # Encoder
    encoder_model: str = ENCODER_MODEL
    encoder_batch_size: int = ENCODER_BATCH_SIZE
    embed_dim: int = EMBED_DIM
    # Panel regression
    cumulative_tokens_scale: float = CUMULATIVE_TOKENS_SCALE
    min_sessions_per_worker: int = MIN_SESSIONS_PER_WORKER
    min_workers: int = MIN_WORKERS
    panel_cov_type: str = PANEL_COV_TYPE
    # Analysis
    ambiguity_kappa_threshold: float = AMBIGUITY_KAPPA_THRESHOLD
    ambiguity_score_threshold: float = AMBIGUITY_SCORE_THRESHOLD
    effect_size_threshold: float = EFFECT_SIZE_THRESHOLD
    bootstrap_iters: int = BOOTSTRAP_ITERS
    permutation_iters: int = PERMUTATION_ITERS
    random_seed: int = RANDOM_SEED
    # Gate thresholds
    beta_exposure_min: float = BETA_EXPOSURE_MIN
    alpha_significance: float = ALPHA_CORRECTED
    brier_gate_threshold: float = BRIER_GATE_THRESHOLD
    bonferroni_k: int = BONFERRONI_K
    # Output
    figures_dir: str = FIGURES_DIR
    results_file: str = RESULTS_JSON


def load_config(config_path: Optional[str] = None) -> ExperimentConfig:
    if config_path is None:
        return ExperimentConfig()
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)
    cfg = ExperimentConfig()
    for key, val in raw.items():
        if key in ExperimentConfig.__dataclass_fields__:
            setattr(cfg, key, val)
    return cfg
```

---

## YAML Schema (experiment_config.yaml)

```yaml
# experiment_config.yaml — H-M1 experiment configuration
# All values mirror ExperimentConfig dataclass defaults

# Dataset
hh_rlhf_dataset: "Anthropic/hh-rlhf"          # HuggingFace dataset path
webgpt_dataset: "openai/webgpt_comparisons"     # HuggingFace dataset path
n_rounds: 3                                     # Number of HH-RLHF exposure rounds

# Encoder
encoder_model: "sentence-transformers/all-MiniLM-L6-v2"  # Frozen encoder
encoder_batch_size: 256                         # Batch size for SentenceTransformer
embed_dim: 384                                  # Output embedding dimension

# Panel regression
cumulative_tokens_scale: 1000.0                 # Divide raw token count by this (per-1k regression)
min_sessions_per_worker: 3                      # Minimum median sessions for power check
min_workers: 100                                # Minimum unique workers for power check
panel_cov_type: "clustered"                     # Covariance type: "clustered" or "robust"

# Analysis
ambiguity_kappa_threshold: 0.4                  # Fleiss kappa split for HH-RLHF high/low ambiguity
ambiguity_score_threshold: 0.4                  # |score_0 - score_1| threshold for WebGPT ambiguity
effect_size_threshold: 0.1                      # Minimum SD per 1000 tokens to claim practical effect
bootstrap_iters: 1000                           # Bootstrap resampling iterations
permutation_iters: 1000                         # Placebo permutation iterations
random_seed: 42                                 # Global RNG seed

# Gate thresholds
beta_exposure_min: 0.0                          # beta_exposure must exceed this (directional gate)
alpha_significance: 0.0167                      # Bonferroni-corrected significance level
brier_gate_threshold: 0.02                      # Max acceptable Brier score improvement
bonferroni_k: 3                                 # Number of hypotheses for Bonferroni correction

# Output
figures_dir: "../figures"                       # Directory for saved PNG figures
results_file: "../results/results.yaml"         # Path for serialized results
```

---

## requirements.txt

```
# H-M1 requirements
# Inherited from H-E1
numpy>=1.24.0
scipy>=1.10.0
pandas>=2.0.0
scikit-learn>=1.3.0
statsmodels>=0.14.0
matplotlib>=3.7.0
seaborn>=0.12.0
pytest>=7.4.0
pyyaml>=6.0
tqdm>=4.65.0

# New for H-M1
sentence-transformers>=2.2.2
linearmodels>=4.28
datasets>=2.14.0
```

---

## Subtasks

### A-2: WebGPT Data Loader [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A-2-1 | WebGPT column config | `load_webgpt_with_sessions` uses `WEBGPT_DATASET`; expects columns `question`, `answer_0`, `answer_1`, `score_0`, `score_1`; `worker_id` fallback: if absent, use row-index as surrogate (log warning); `created_at` fallback: if NaT, fall back to row-index ordering; `cumulative_tokens_viewed` = cumsum of `len(answer_0.split()) + len(answer_1.split())` per worker; `cumulative_tokens_k = cumulative_tokens_viewed / CUMULATIVE_TOKENS_SCALE` |
| C-A-2-2 | Panel power thresholds | `validate_panel_power` checks: `median(sessions_per_worker) >= MIN_SESSIONS_PER_WORKER` (3) and `n_unique_workers >= MIN_WORKERS` (100); rationale: 100 workers x 3 sessions = 300 obs minimum for clustered SE convergence; non-fatal — logs warning and returns `False`; gate does not block on this check |

---

### A-7: Visualization [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A-7-1 | Figure output config | All figures saved to `FIGURES_DIR` (`../figures`); DPI=150; figure sizes: dose-response (10,6), ambiguity-modulation (12,5), placebo histogram (8,5), worker-FE distribution (8,5), discriminant-validity bar (8,6), gate-metrics bar (8,5); color palette: `{"high_ambiguity": "#E74C3C", "low_ambiguity": "#3498DB", "observed": "#2ECC71", "null": "#95A7AA", "stylistic": "#8E44AD", "topic": "#F39C12"}`; all figures use `tight_layout()`; filenames: `dose_response.png`, `ambiguity_modulation.png`, `placebo_permutation.png`, `worker_fe_distribution.png`, `discriminant_validity.png`, `gate_metrics_hm1.png` |

---

### A-9: Validation [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A-9-1 | Smoke test config | Subsample sizes: HH-RLHF `n=500` rows, WebGPT `n=200` rows; encoder shape assertion: `embeddings.shape == (n, 384)`; panel df assertion: `isinstance(panel_df.index, pd.MultiIndex)`; projection z-score assertion: `abs(proj_scores_z.mean()) < 0.1` and `0.8 < proj_scores_z.std() < 1.2`; gate log assertion: results dict contains keys `["gate_passed", "beta_exposure", "p_value", "effect_size_per_1k"]`; smoke test uses `random_seed=42`, `bootstrap_iters=10`, `permutation_iters=10` to run fast |

---

### ENV-1: Environment Setup [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-ENV-1 | Environment setup | Create venv: `python -m venv .venv && source .venv/bin/activate`; install: `pip install -r h-m1/code/requirements.txt`; check GPU: `nvidia-smi` then `export CUDA_VISIBLE_DEVICES=<empty_gpu_id>`; verify: `python -c "from sentence_transformers import SentenceTransformer; print('ok')"` and `python -c "from linearmodels.panel import PanelOLS; print('ok')"`; `sentence-transformers` will auto-download `all-MiniLM-L6-v2` (~80MB) on first `FrozenEncoder` instantiation; no CUDA required — encoder runs on CPU by default |
