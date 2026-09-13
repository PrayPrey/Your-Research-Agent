# H-M1 Architecture: AI-Typicality Geometric Projection + WebGPT Panel Regression

**Date:** 2026-05-03
**Hypothesis:** H-M1 (MECHANISM)
**Base:** H-E1 (INCREMENTAL extension)

Applied: Statistical-Analysis-Pipeline
Applied: Panel-Regression-FE
Applied: Geometric-Projection-Pattern
Applied: Pipeline-Module-Separation

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `h-e1/code/`
**Findings**: H-E1 uses flat module layout (config.py, data_loader.py, features.py, q_early.py, analysis.py, visualize.py, run_experiment.py). Import style is direct (`from config import ...`, `from features import ...`). All modules use `logging.getLogger(__name__)`. `QEarlyModel` is a class in q_early.py; analysis functions are module-level; `load_hh_rlhf` and `load_webgpt` are separate top-level functions in data_loader.py. H-E1 `webgpt_dose_response` in analysis.py is a stub (no PanelOLS) — H-M1 replaces with real panel regression.

---

## File Structure

```
h-m1/code/
├── config.py
├── data_loader_webgpt.py
├── encoder.py
├── projection.py
├── panel_regression.py
├── interaction_test.py
├── visualize.py
└── run_experiment.py
```

**Reused from H-E1 (no copy — import directly):**
- `h-e1/code/data_loader.py` — `load_hh_rlhf`, `stratify_rounds`, `validate_round_coverage`
- `h-e1/code/features.py` — `build_feature_matrix`, `partition_by_ambiguity`
- `h-e1/code/q_early.py` — `QEarlyModel`
- `h-e1/code/analysis.py` — `bootstrap_coefficient_ci`, `placebo_permutation_test`, `apply_bonferroni`

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_hh_rlhf | `sys.path.insert(0, he1_code_dir); from data_loader import load_hh_rlhf` | `h-e1/code/data_loader.py` |
| stratify_rounds | `from data_loader import stratify_rounds` | `h-e1/code/data_loader.py` |
| validate_round_coverage | `from data_loader import validate_round_coverage` | `h-e1/code/data_loader.py` |
| build_feature_matrix | `from features import build_feature_matrix` | `h-e1/code/features.py` |
| partition_by_ambiguity | `from features import partition_by_ambiguity` | `h-e1/code/features.py` |
| QEarlyModel | `from q_early import QEarlyModel` | `h-e1/code/q_early.py` |
| bootstrap_coefficient_ci | `from analysis import bootstrap_coefficient_ci` | `h-e1/code/analysis.py` |
| placebo_permutation_test | `from analysis import placebo_permutation_test` | `h-e1/code/analysis.py` |
| apply_bonferroni | `from analysis import apply_bonferroni` | `h-e1/code/analysis.py` |

**Verified from**: `h-e1/code/` (actual implementation — `run_experiment.py` imports confirm flat module layout)

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: none

```python
# H-E1 inherited
HH_RLHF_DATASET: str = "Anthropic/hh-rlhf"
WEBGPT_DATASET: str = "openai/webgpt_comparisons"
N_ROUNDS: int = 3
BOOTSTRAP_ITERS: int = 1000
PERMUTATION_ITERS: int = 1000
RANDOM_SEED: int = 42
BONFERRONI_K: int = 3
ALPHA_CORRECTED: float = 0.0167
LR_PARAMS: dict = {"C": 1.0, "max_iter": 1000, "solver": "lbfgs", "random_state": 42}
BRIER_GATE_THRESHOLD: float = 0.05
HEDGE_WORDS: list
STRUCT_MARKERS: list

# H-M1 new
ENCODER_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
ENCODER_BATCH_SIZE: int = 256
EMBED_DIM: int = 384
CUMULATIVE_TOKENS_SCALE: float = 1000.0  # tokens per unit for regression
AMBIGUITY_KAPPA_THRESHOLD: float = 0.4
EFFECT_SIZE_THRESHOLD: float = 0.1  # SD per 1000 tokens
FIGURES_DIR: str = "../figures"
RESULTS_JSON: str = "../experiment_results.json"
MIN_SESSIONS_PER_WORKER: int = 3
MIN_WORKERS: int = 100
```

---

### DataLoaderWebGPT (`data_loader_webgpt.py`)

**Dependencies**: config.py

```python
import pandas as pd

def load_webgpt_with_sessions() -> pd.DataFrame:
    """Load WebGPT comparisons; normalize columns; validate worker_id/created_at presence.
    Returns df with columns: question, answer_0, answer_1, score_0, score_1,
    preferred, worker_id, created_at.
    Raises DataError if worker_id unavailable and fallback not possible."""
    ...

def build_session_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by (worker_id, created_at); assign session_order per worker;
    compute cumulative_tokens_viewed as cumsum of token counts per worker.
    Returns df with added columns: session_order, cumulative_tokens_viewed,
    cumulative_tokens_k (= cumulative_tokens_viewed / 1000).
    Falls back to row-index ordering if created_at is NaT."""
    ...

def validate_panel_power(panel_df: pd.DataFrame) -> bool:
    """Check median sessions per worker >= MIN_SESSIONS_PER_WORKER;
    check unique worker count >= MIN_WORKERS.
    Logs warnings on failure; returns False (non-fatal for gate)."""
    ...

def build_webgpt_chosen_rejected(df: pd.DataFrame) -> pd.DataFrame:
    """Construct chosen/rejected columns from answer_0/answer_1 + preferred.
    Required for reuse of H-E1 build_feature_matrix and encoder text lists."""
    ...
```

---

### Encoder (`encoder.py`)

**Dependencies**: config.py

```python
import numpy as np
from sentence_transformers import SentenceTransformer

class FrozenEncoder:
    """Wrapper for all-MiniLM-L6-v2 in frozen eval mode."""

    def __init__(self, model_name: str = ENCODER_MODEL) -> None: ...

    def encode_batch(self, texts: list[str], normalize: bool = True) -> np.ndarray:
        """Encode texts; returns (N, 384) float32 array.
        normalize=True applies L2 normalization per embedding."""
        ...

    @property
    def embed_dim(self) -> int: ...
```

---

### Projection (`projection.py`)

**Dependencies**: encoder.py, config.py; reuses QEarlyModel from h-e1

```python
import numpy as np

def build_ai_typicality_vector(
    encoder,
    ai_texts: list[str],
    human_texts: list[str],
) -> np.ndarray:
    """Centroid difference: mean(ai_embs) - mean(human_embs), L2-normalized.
    Returns unit vector (384,)."""
    ...

def compute_raw_projection(
    embeddings: np.ndarray,
    ai_typicality_vec: np.ndarray,
) -> np.ndarray:
    """Dot product of each embedding row with unit ai_typicality_vec.
    Input: (N, 384), (384,) -> Output: (N,) scalar scores."""
    ...

def partial_out_q_early(
    raw_proj: np.ndarray,
    q_early_scores: np.ndarray,
) -> np.ndarray:
    """Regress raw_proj on q_early_scores (OLS); return residuals.
    Removes quality-correlated variance from projection scores."""
    ...

def zscore_projection(residuals: np.ndarray) -> np.ndarray:
    """Standardize residuals to z-scores (mean=0, std=1).
    Returns (N,) float64."""
    ...

def build_topic_axis_vector(
    encoder,
    prompt_texts: list[str],
    n_components: int = 1,
) -> np.ndarray:
    """PCA first component of prompt embeddings as topic-axis direction.
    Used for discriminant validity control. Returns unit vector (384,)."""
    ...

def placebo_permute_vector(
    encoder,
    ai_texts: list[str],
    human_texts: list[str],
    n_permutations: int = 1000,
    seed: int = 42,
) -> np.ndarray:
    """Permute AI/human labels; compute centroid difference for each permutation.
    Returns (n_permutations, 384) array of null vectors."""
    ...
```

---

### PanelRegression (`panel_regression.py`)

**Dependencies**: config.py

```python
import pandas as pd
from dataclasses import dataclass

@dataclass
class PanelResult:
    beta_exposure: float
    p_value: float
    ci_lower: float
    ci_upper: float
    effect_size_per_1k: float
    n_workers: int
    n_obs: int
    model_type: str  # "PanelOLS" | "LSDV"
    summary: object  # linearmodels/statsmodels result object

def run_panel_ols(
    panel_df: pd.DataFrame,
    outcome_col: str = "proj_score_z",
    exposure_col: str = "cumulative_tokens_k",
    entity_col: str = "worker_id",
    time_col: str = "session_order",
) -> PanelResult:
    """PanelOLS with EntityEffects and clustered SE by worker.
    panel_df must have MultiIndex (worker_id, session_order).
    Falls back to LSDV if linearmodels raises."""
    ...

def run_lsdv_fallback(
    panel_df: pd.DataFrame,
    outcome_col: str,
    exposure_col: str,
    entity_col: str,
) -> PanelResult:
    """Least Squares Dummy Variables via statsmodels OLS.
    Worker dummies absorbed via C(worker_id) formula term."""
    ...

def between_worker_tercile_comparison(
    panel_df: pd.DataFrame,
    outcome_col: str = "proj_score_z",
    exposure_col: str = "cumulative_tokens_k",
) -> dict:
    """Fallback: split workers into terciles by total cumulative_tokens;
    compare mean projection score across terciles (low/mid/high).
    Returns dict with tercile means, F-stat, p-value."""
    ...

def bootstrap_beta_ci(
    panel_df: pd.DataFrame,
    n_iter: int = 1000,
    seed: int = 42,
) -> tuple[float, float]:
    """Bootstrap 95% CI on beta_exposure by resampling workers with replacement.
    Returns (ci_lower, ci_upper)."""
    ...
```

---

### InteractionTest (`interaction_test.py`)

**Dependencies**: config.py; reuses partition_by_ambiguity from h-e1/features.py

```python
import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class InteractionResult:
    interaction_coef: float
    interaction_p: float
    high_ambiguity_beta: float
    low_ambiguity_beta: float
    discriminant_valid: bool  # stylistic_beta > topic_beta
    placebo_p: float
    summary: object

def run_ambiguity_modulation_test(
    hh_df: pd.DataFrame,
    proj_scores_z: np.ndarray,
    q_early_model,
    feature_matrix_fn,
) -> InteractionResult:
    """Statsmodels Logit with round x high_ambiguity interaction.
    proj_score_z ~ C(round) + high_ambiguity + C(round):high_ambiguity + Q_early.
    Returns interaction coefficient and p-value."""
    ...

def run_discriminant_validity(
    stylistic_panel_result,
    topic_panel_result,
) -> bool:
    """Returns True if stylistic beta_exposure > topic beta_exposure."""
    ...

def run_projection_placebo(
    null_vectors: np.ndarray,
    embeddings: np.ndarray,
    observed_proj_scores: np.ndarray,
) -> float:
    """For each null vector, compute projection scores;
    compare distribution to observed scores.
    Returns empirical p-value (proportion of null means >= observed mean)."""
    ...

def check_monotonicity_hh(
    round_proj_means: dict,
) -> bool:
    """Check round-1 < round-2 < round-3 mean projection scores (HH-RLHF)."""
    ...
```

---

### Visualize (`visualize.py`)

**Dependencies**: config.py; extends H-E1 visualize.py (H-M1 adds 6 new figures)

```python
from pathlib import Path
import numpy as np
import pandas as pd

# H-M1-specific figures (new)
def plot_dose_response(
    panel_df: pd.DataFrame,
    panel_result,
    figures_dir: Path,
) -> None:
    """Scatter: projection score vs cumulative_tokens_k per worker;
    worker-level means overlaid; fitted regression line."""
    ...

def plot_ambiguity_modulation(
    high_proj_by_round: dict,
    low_proj_by_round: dict,
    figures_dir: Path,
) -> None:
    """Side-by-side projection score distributions for high/low ambiguity
    strata across rounds 1-3 (HH-RLHF)."""
    ...

def plot_ai_typicality_placebo(
    null_proj_means: np.ndarray,
    observed_proj_mean: float,
    figures_dir: Path,
) -> None:
    """Histogram of null projection means under label permutation;
    vertical line at observed mean."""
    ...

def plot_worker_fe_distribution(
    worker_intercepts: np.ndarray,
    figures_dir: Path,
) -> None:
    """Distribution of worker-level fixed effects from panel regression."""
    ...

def plot_discriminant_validity(
    stylistic_beta: float,
    topic_beta: float,
    stylistic_ci: tuple,
    topic_ci: tuple,
    figures_dir: Path,
) -> None:
    """Side-by-side bar chart: beta_exposure for stylistic vs topic projection."""
    ...

def plot_gate_metrics_hm1(
    beta_exposure: float,
    p_value: float,
    effect_size: float,
    figures_dir: Path,
) -> None:
    """Bar chart: beta_exposure vs threshold 0; p-value vs 0.05;
    effect_size vs 0.1 SD."""
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: all H-M1 modules + H-E1 imports via sys.path

```python
def main() -> dict:
    """Full H-M1 pipeline:
    1. Load HH-RLHF (H-E1); stratify rounds
    2. Load WebGPT with sessions; build panel; validate power
    3. Build feature matrices; VIF check (H-E1 features.py)
    4. Train/calibrate QEarlyModel (H-E1 q_early.py)
    5. Encode texts; build AI-typicality vector
    6. Compute projection scores; partial out Q_early; z-score
    7. Build WebGPT panel df; run PanelOLS (+ LSDV fallback)
    8. Bootstrap beta_exposure CI
    9. Ambiguity-modulation interaction test (HH-RLHF)
    10. Discriminant validity: topic-axis projection regression
    11. Placebo permutation test on AI-typicality vector
    12. HH-RLHF monotonicity check
    13. Gate evaluation (MUST_WORK)
    14. Generate 6 H-M1 figures + gate_metrics figure
    15. Serialize results JSON
    Returns: results dict with gate_passed, beta_exposure, p_value, effect_size
    """
    ...

if __name__ == "__main__":
    results = main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | config.py, directory layout, sys.path H-E1 bridge, requirements.txt | 6 | 2+1+1+2 |
| A-2 | WebGPT Data Loader | data_loader_webgpt.py: load, normalize columns, session panel construction, cumulative tokens, power validation | 13 | 3+2+4+4 |
| A-3 | Frozen Encoder | encoder.py: FrozenEncoder wrapper, batch encode, L2 normalize, eval mode | 8 | 2+2+2+2 |
| A-4 | AI-Typicality Projection | projection.py: centroid-difference vector, raw projection, Q_early partialing, z-score, topic-axis PCA vector, placebo permute | 16 | 4+3+5+4 |
| A-5 | Panel Regression | panel_regression.py: PanelOLS + LSDV fallback + between-worker tercile + bootstrap CI | 17 | 4+3+5+5 |
| A-6 | Interaction & Validity Tests | interaction_test.py: ambiguity-modulation logit, discriminant validity, projection placebo, monotonicity check | 15 | 3+3+5+4 |
| A-7 | Visualization Suite | visualize.py: 6 H-M1 figures (dose-response, ambiguity-modulation, placebo, worker FE, discriminant validity, gate metrics) | 12 | 2+2+3+5 |
| A-8 | Run Experiment Integration | run_experiment.py: 15-step pipeline, gate evaluation, results JSON serialization | 14 | 3+4+3+4 |
| A-9 | End-to-End Validation | Smoke test with subsample; verify encoder output shape (N,384); panel df multiindex; projection z-score distribution; gate log message format | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4, A-5, A-6, A-8], Medium(9-13): [A-2, A-3, A-7, A-9], Low(4-8): [A-1]

---

## Data Flow

- `data_loader_webgpt.py` → `pd.DataFrame` (WebGPT, session panel, cumulative_tokens_k)
- H-E1 `data_loader.py` → `pd.DataFrame` (HH-RLHF, round-stratified)
- `encoder.py` → `np.ndarray` (N, 384) embeddings
- `projection.py` → `np.ndarray` (N,) proj_score_z; `np.ndarray` (384,) ai_typicality_vec
- `panel_regression.py` → `PanelResult` (beta_exposure, p_value, CI)
- `interaction_test.py` → `InteractionResult` (interaction_coef, placebo_p, discriminant_valid)
- `visualize.py` → PNG files in `h-m1/figures/`
- `run_experiment.py` → `experiment_results.json`

## Gate Logic

```python
gate_passed = True  # MUST_WORK: code executed end-to-end
hypothesis_supported = (
    panel_result.beta_exposure > 0
    and panel_result.p_value < 0.05
    and panel_result.effect_size_per_1k >= EFFECT_SIZE_THRESHOLD
)
```
