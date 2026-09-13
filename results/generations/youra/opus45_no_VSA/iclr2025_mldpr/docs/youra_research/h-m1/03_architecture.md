# Architecture: h-m1 (MECHANISM - Mediation Analysis)

Applied: Sobel/bootstrap mediation pattern (indirect = a*b; SE via variance formula; percentile bootstrap CI)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1 VALIDATED, conceptually prior but not directly extended as code)
**Status**: Existing patterns found from h-e1 code — reusable for data collection layer
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: h-e1 provides `collect.py` (OpenML dataset/run collection), `metadata_score.py` (5-field scorer), `config.py` (paths/thresholds), `analysis.py` (IQR + mixed model). h-m1 reuses collection/metadata pattern but adds new entropy + mediation modules; does not import h-e1 code directly (separate hypothesis folder, PRD requires standalone reproducibility) — instead **replicates the pattern** with new files under `h-m1/code/`.

## Module Structure

### config.py (`h-m1/code/config.py`)

```python
MIN_DATE: str
MAX_DATE: str
MIN_RUNS_PER_GROUP: int
N_BOOTSTRAP: int  # 1000
RANDOM_SEED: int  # 42
MIN_DATASETS: int  # 200
PATHS: dict[str, str]
SUCCESS_CRITERIA: dict[str, float]  # proportion_mediated_min=0.30, p_value_max=0.05, sobel_z_min=1.96
```

### collect.py (`h-m1/code/collect.py`)

**Dependencies**: config

```python
def collect_datasets(min_date: str) -> pd.DataFrame: ...
def get_matched_runs(dataset_id: int, min_runs: int) -> pd.DataFrame: ...
def collect_all_matched_runs(dataset_ids: list) -> pd.DataFrame: ...
def extract_controls(dataset_id: int, flow_id: int) -> dict: ...
def extract_flow_components(flow_id: int) -> list[str]: ...  # NEW: parse flow.name/components for preprocessing steps
def extract_hyperparams(setup_id: int) -> dict: ...  # NEW: openml.setups.get_setup(setup_id).parameters
```

### metadata_score.py (`h-m1/code/metadata_score.py`)

**Dependencies**: config

```python
def compute_metadata_score(dataset) -> int: ...
def score_all_datasets(dataset_ids: list) -> pd.DataFrame: ...
```

### entropy.py (`h-m1/code/entropy.py`)

**Dependencies**: none (scipy.stats.entropy)

```python
def compute_preprocessing_entropy(flow_components: list[str]) -> float: ...
def compute_hyperparameter_entropy(hyperparams: dict) -> float: ...  # discretize continuous -> bins, then Shannon
def bin_continuous(values: list[float], n_bins: int = 10) -> np.ndarray: ...
```

### analysis.py (`h-m1/code/analysis.py`)

**Dependencies**: config, entropy

```python
def compute_reproducibility_iqr(runs_df: pd.DataFrame) -> pd.DataFrame: ...
def build_analysis_dataset(matched_runs, metadata_scores, controls, flow_components, hyperparams) -> pd.DataFrame: ...
    # adds columns: prep_entropy, hyp_entropy, metadata_quartile
```

### mediation.py (`h-m1/code/mediation.py`)

**Dependencies**: config, analysis

```python
def run_mediation_analysis(df: pd.DataFrame) -> dict: ...
    # pingouin.mediation_analysis(x='metadata_score', m='prep_entropy', y='iqr',
    #   covar=['stability','log_popularity','algo_family'], n_boot=1000, seed=42)
    # returns indirect_effect, total_effect, proportion_mediated, p_value, ci_lower, ci_upper
def compute_sobel_z(coef_a, se_a, coef_b, se_b) -> tuple[float, float]: ...  # (z, p)
def save_mediation_results(result: dict, path: str) -> None: ...
```

### subpredictions.py (`h-m1/code/subpredictions.py`)

**Dependencies**: analysis

```python
def quartile_split(df: pd.DataFrame, col: str = "metadata_score") -> tuple[pd.DataFrame, pd.DataFrame]: ...  # Q1, Q4
def test_p2a(df: pd.DataFrame) -> dict: ...  # t-test H_prep Q4 vs Q1
def test_p2b(df: pd.DataFrame) -> dict: ...  # t-test H_hyp Q4 vs Q1
```

### visualize.py (`h-m1/code/visualize.py`)

**Dependencies**: matplotlib

```python
def plot_mediation_path(result: dict, out_path: str) -> None: ...
def plot_entropy_boxplot(df: pd.DataFrame, col: str, out_path: str) -> None: ...  # reused for H_prep and H_hyp
def plot_bootstrap_distribution(boot_estimates: list[float], out_path: str) -> None: ...
def plot_mediation_proportion(result: dict, out_path: str) -> None: ...
```

### run.py (`h-m1/code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # orchestrates: collect -> score -> entropy -> build_analysis_dataset ->
    # run_mediation_analysis -> subprediction tests -> visualize -> save results
```

## External Dependencies (Base Hypothesis)

**Not directly imported** — h-m1 is a standalone folder per Phase 2C spec. Pattern reuse only (no cross-folder import).

| Reused Pattern | h-e1 Source | h-m1 Reimplementation |
|-----------------|-------------|------------------------|
| Dataset/run collection | `h-e1/code/collect.py` | `h-m1/code/collect.py` (extended with flow components + hyperparams) |
| Metadata scoring | `h-e1/code/metadata_score.py` | `h-m1/code/metadata_score.py` (unchanged logic) |
| Config/paths pattern | `h-e1/code/config.py` | `h-m1/code/config.py` (new thresholds for mediation) |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, not specs)

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Config setup | Paths, thresholds, seeds | 4 | 1+1+1+1 |
| M-2 | Data collection | OpenML datasets/runs (adapt h-e1 pattern) | 9 | 2+3+2+2 |
| M-3 | Flow/hyperparam extraction | Parse preprocessing components + hyperparams per setup | 11 | 3+3+3+2 |
| M-4 | Metadata scoring | 5-field checklist (reuse h-e1 logic) | 4 | 1+1+1+1 |
| M-5 | Entropy computation | Shannon entropy for H_prep, H_hyp incl. binning | 10 | 3+2+4+1 |
| M-6 | Analysis dataset build | Merge all sources, compute IQR, quartiles | 8 | 2+3+2+1 |
| M-7 | Mediation analysis | pingouin mediation + Sobel Z + bootstrap CI | 13 | 3+4+4+2 |
| M-8 | Sub-prediction tests | P2a/P2b t-tests across quartiles | 6 | 1+2+2+1 |
| M-9 | Visualization | 4 required figures | 7 | 2+2+1+2 |
| M-10 | Orchestration + validation | run.py end-to-end, acceptance checks | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-2,M-3,M-5,M-6,M-7], Low(4-8): [M-1,M-4,M-8,M-9,M-10]
