# Logic: h-m1 (MECHANISM - Mediation Analysis)

Applied: Sobel Z formula (z = a*b / sqrt(b²*se_a² + a²*se_b²)); percentile bootstrap CI pattern from h-e1
Applied: OpenML groupby(flow_id, setup_id) matched-run pattern (h-e1 collect.py)

Archon KB search ("mediation analysis API design") returned no relevant PyTorch/DL results (corpus is vision/diffusion-focused) — used standard statsmodels/pingouin/scipy patterns instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1, pattern reuse not import)
**Status**: API signatures verified from actual h-e1 code (not spec)
**Analyzed Path**: `docs/youra_research/h-e1/code/{collect,metadata_score,analysis}.py`
**Relevant Symbols**: `collect_datasets`, `get_matched_runs`, `extract_controls`, `compute_metadata_score`, `compute_reproducibility_iqr`, `bootstrap_ci` — signatures below match verified actual code, not `03_architecture.md` prose.

---

## M-2: Data Collection [Complexity 9, Budget 9]

**Applied**: h-e1 `collect_datasets`/`get_matched_runs` pattern, verbatim reuse (new file, same logic).

### API Signatures

```python
def collect_datasets(min_date: str = MIN_DATE) -> pd.DataFrame:
    """OpenML classification datasets uploaded >= min_date. Cols: did,name,upload_date,NumberOfInstances,NumberOfClasses"""

def get_matched_runs(dataset_id: int, min_runs: int = MIN_RUNS_PER_GROUP) -> pd.DataFrame:
    """Runs grouped by (flow_id,setup_id), kept if count>=min_runs. Cols: run_id,data_id,flow_id,setup_id,predictive_accuracy"""

def collect_all_matched_runs(dataset_ids: list[int]) -> pd.DataFrame:
    """Concat get_matched_runs over dataset_ids."""

def extract_controls(dataset_id: int, flow_id: int) -> dict:
    """Returns {stability: float, algo_family: str, sklearn_version: str}. Same logic as h-e1."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-1 | collect_datasets | Copy h-e1 impl verbatim |
| L-M2-2 | get_matched_runs + collect_all_matched_runs | Copy h-e1 impl verbatim |
| L-M2-3 | extract_controls | Copy h-e1 impl verbatim (stability/algo_family/sklearn_version) |
| L-M2-4 | log_popularity control | New: `np.log1p(dataset.qualities.get("NumberOfDownloads", 0))` merged into controls dict in build_analysis_dataset (M-6), not here |

---

## M-3: Flow/Hyperparam Extraction [Complexity 11, Budget 11]

**Applied**: OpenML `flows.get_flow` / `setups.get_setup` component-tree traversal.

### API Signatures

```python
def extract_flow_components(flow_id: int) -> list[str]:
    """Recursively walk flow.components, return list of step class names (e.g. ['StandardScaler','SimpleImputer','RandomForestClassifier'])."""

def extract_hyperparams(setup_id: int) -> dict:
    """openml.setups.get_setup(setup_id).parameters -> {param_name: value_str}. Non-numeric values kept as str."""
```

### Pseudo-code

```
extract_flow_components(flow_id):
    flow = openml.flows.get_flow(flow_id)
    components = []
    def walk(f):
        components.append(f.class_name.split('.')[-1])
        for sub_flow in (f.components or {}).values():
            walk(sub_flow)
    walk(flow)
    return components  # e.g. Pipeline -> [Pipeline, SimpleImputer, StandardScaler, RandomForestClassifier]

extract_hyperparams(setup_id):
    setup = openml.setups.get_setup(setup_id)
    params = {}
    for p in setup.parameters.values():
        params[p.parameter_name] = p.value
    return params
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-1 | extract_flow_components | Recursive flow.components walk, dedupe not required (entropy uses raw list) |
| L-M3-2 | extract_hyperparams | setup.parameters flatten, try/except -> {} on API failure |
| L-M3-3 | Caching layer | `functools.lru_cache(maxsize=None)` on both functions (flow_id/setup_id repeat across matched runs) |

---

## M-5: Entropy Computation [Complexity 10, Budget 10]

**Applied**: `scipy.stats.entropy` (Shannon, base=2) over categorical/binned frequency distribution.

### API Signatures

```python
def compute_preprocessing_entropy(flow_components: list[str]) -> float:
    """Shannon entropy (base 2) of component frequency distribution. Empty list -> 0.0."""

def compute_hyperparameter_entropy(hyperparams: dict) -> float:
    """Discretize each numeric value into 10 bins across the setup's group, then Shannon entropy of the bin-label distribution. Empty dict -> 0.0."""

def bin_continuous(values: list[float], n_bins: int = 10) -> np.ndarray:
    """np.digitize into n_bins equal-width bins. Returns bin index array, shape [len(values)]."""
```

### Pseudo-code

```
compute_preprocessing_entropy(flow_components):
    if not flow_components: return 0.0
    counts = Counter(flow_components)
    probs = np.array(list(counts.values())) / len(flow_components)
    return float(scipy.stats.entropy(probs, base=2))

compute_hyperparameter_entropy(hyperparams):
    # hyperparams: dict of {param_name: value} for ONE setup;
    # entropy computed per-dataset-group over all setups' values for that param, then averaged
    if not hyperparams: return 0.0
    numeric_vals = [float(v) for v in hyperparams.values() if is_numeric(v)]
    if not numeric_vals: return 0.0
    bins = bin_continuous(numeric_vals, n_bins=10)
    counts = np.bincount(bins)
    probs = counts[counts > 0] / len(bins)
    return float(scipy.stats.entropy(probs, base=2))
```

### Tensor/Shape Notes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| flow_components | list[str] | length = pipeline steps |
| bin indices | np.ndarray[int], [N] | N = numeric hyperparam count |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M5-1 | compute_preprocessing_entropy | Counter + scipy.stats.entropy, edge case empty->0 |
| L-M5-2 | bin_continuous | np.digitize equal-width binning |
| L-M5-3 | compute_hyperparameter_entropy | numeric filter + bin + entropy |
| L-M5-4 | NaN/Inf guard | Wrap both entropy fns: `if not np.isfinite(result): return 0.0` |

---

## M-6: Analysis Dataset Build [Complexity 8, Budget 8]

**Applied**: h-e1 `compute_reproducibility_iqr` groupby pattern (verified, reused verbatim).

### API Signatures

```python
def compute_reproducibility_iqr(runs_df: pd.DataFrame) -> pd.DataFrame:
    """groupby(data_id,flow_id,setup_id)[predictive_accuracy].agg(iqr,mean,std,count). Verbatim from h-e1."""

def build_analysis_dataset(
    matched_runs: pd.DataFrame,
    metadata_scores: pd.DataFrame,
    controls: pd.DataFrame,
    flow_components: dict[int, list[str]],
    hyperparams: dict[int, dict],
) -> pd.DataFrame:
    """Merge all sources on data_id/flow_id/setup_id. Adds: prep_entropy, hyp_entropy, metadata_quartile (pd.qcut q=4, labels=1..4)."""
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M6-1 | compute_reproducibility_iqr | Copy h-e1 verbatim |
| L-M6-2 | build_analysis_dataset merge | pd.merge chain on data_id/flow_id/setup_id + entropy column mapping |
| L-M6-3 | metadata_quartile | `pd.qcut(df.metadata_score, 4, labels=[1,2,3,4], duplicates='drop')` |

---

## M-7: Mediation Analysis [Complexity 13, Budget 13]

**Applied**: pingouin `mediation_analysis` (Baron & Kenny + bootstrap) + manual Sobel Z as corroborating stat.

### API Signatures

```python
def run_mediation_analysis(df: pd.DataFrame) -> dict:
    """
    pingouin.mediation_analysis(data=df, x='metadata_score', m='prep_entropy', y='iqr',
        covar=['stability','log_popularity','algo_family'], n_boot=1000, seed=42, alpha=0.05)
    Returns dict: {indirect_effect, indirect_se, indirect_ci_lower, indirect_ci_upper,
                   total_effect, direct_effect, proportion_mediated, p_value,
                   sobel_z, sobel_p, path_a, path_a_se, path_b, path_b_se, boot_estimates: list[float]}
    """

def compute_sobel_z(coef_a: float, se_a: float, coef_b: float, se_b: float) -> tuple[float, float]:
    """Sobel test: z = a*b / sqrt(b^2*se_a^2 + a^2*se_b^2); p = 2*(1-norm.cdf(|z|)). Returns (z, p)."""

def save_mediation_results(result: dict, path: str) -> None:
    """json.dump result (boot_estimates truncated/excluded) to path."""
```

### Pseudo-code

```
run_mediation_analysis(df):
    med = pingouin.mediation_analysis(
        data=df, x='metadata_score', m='prep_entropy', y='iqr',
        covar=['stability','log_popularity','algo_family'],
        n_boot=N_BOOTSTRAP, seed=RANDOM_SEED, alpha=0.05)
    # med is a DataFrame with rows: Path 'X -> M', 'M -> Y', 'X -> Y', 'X -> Y (Direct)', 'X -> Y (Total)', 'Indirect'
    a_row = med[med.path == 'X -> M']       # path_a, se
    b_row = med[med.path == 'M -> Y']       # path_b, se
    indirect_row = med[med.path == 'Indirect']
    total_row = med[med.path == 'X -> Y (Total)']

    sobel_z, sobel_p = compute_sobel_z(a_row.coef, a_row.se, b_row.coef, b_row.se)
    proportion_mediated = indirect_row.coef / total_row.coef

    return {
        'indirect_effect': indirect_row.coef, 'indirect_se': indirect_row.se,
        'indirect_ci_lower': indirect_row['CI[2.5%]'], 'indirect_ci_upper': indirect_row['CI[97.5%]'],
        'total_effect': total_row.coef, 'direct_effect': med[med.path=='X -> Y (Direct)'].coef,
        'proportion_mediated': proportion_mediated, 'p_value': indirect_row.pval,
        'sobel_z': sobel_z, 'sobel_p': sobel_p,
        'path_a': a_row.coef, 'path_a_se': a_row.se, 'path_b': b_row.coef, 'path_b_se': b_row.se,
    }

compute_sobel_z(coef_a, se_a, coef_b, se_b):
    se_indirect = sqrt(coef_b**2 * se_a**2 + coef_a**2 * se_b**2)
    z = (coef_a * coef_b) / se_indirect
    p = 2 * (1 - scipy.stats.norm.cdf(abs(z)))
    return z, p
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M7-1 | run_mediation_analysis wrapper | Call pingouin, extract path rows into dict |
| L-M7-2 | proportion_mediated + gate check | indirect/total ratio, compare to SUCCESS_CRITERIA thresholds |
| L-M7-3 | compute_sobel_z | Manual formula, scipy.stats.norm for p-value |
| L-M7-4 | save_mediation_results | JSON serialize (drop non-serializable boot arrays, keep summary stats) |

---

## M-8: Sub-prediction Tests [Complexity 6, Budget 6]

**Applied**: Independent-samples t-test (Welch), reused from h-e1 style stats.

### API Signatures

```python
def quartile_split(df: pd.DataFrame, col: str = "metadata_score") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (Q1_df, Q4_df) via df.metadata_quartile == 1 / == 4."""

def test_p2a(df: pd.DataFrame) -> dict:
    """t-test prep_entropy: Q4 vs Q1. scipy.stats.ttest_ind(q4.prep_entropy, q1.prep_entropy, equal_var=False). Returns {t_stat, p_value, mean_q1, mean_q4, pct_reduction}."""

def test_p2b(df: pd.DataFrame) -> dict:
    """Same as test_p2a but on hyp_entropy column; expects p>0.10 (non-significant)."""
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M8-1 | quartile_split + test_p2a | Q1/Q4 filter, Welch t-test on prep_entropy |
| L-M8-2 | test_p2b | Same fn body param'd on hyp_entropy (shared helper `_ttest_quartiles(df, col)`) |

---

## Standard Modules (No New Subtask Budget)

### config.py — M-1

Constants only: `MIN_DATE, MAX_DATE, MIN_RUNS_PER_GROUP, N_BOOTSTRAP=1000, RANDOM_SEED=42, MIN_DATASETS=200, PATHS: dict, SUCCESS_CRITERIA: dict` (proportion_mediated_min=0.30, p_value_max=0.05, sobel_z_min=1.96).

### metadata_score.py — M-4

`compute_metadata_score(dataset) -> int` and `score_all_datasets(dataset_ids: list) -> pd.DataFrame` — copy h-e1 verbatim (5-field checklist logic, verified above), no changes.

### visualize.py — M-9

```python
def plot_mediation_path(result: dict, out_path: str) -> None: ...  # matplotlib annotate diagram: X->M->Y with coefs
def plot_entropy_boxplot(df: pd.DataFrame, col: str, out_path: str) -> None: ...  # sns.boxplot(x='metadata_quartile', y=col)
def plot_bootstrap_distribution(boot_estimates: list[float], out_path: str) -> None: ...  # plt.hist
def plot_mediation_proportion(result: dict, out_path: str) -> None: ...  # bar: direct vs indirect effect
```

### run.py — M-10

```python
def main() -> None: ...
    # 1. datasets = collect_datasets(); score_all_datasets(datasets.did)
    # 2. matched = collect_all_matched_runs(datasets.did); iqr_df = compute_reproducibility_iqr(matched)
    # 3. per (flow_id,setup_id): extract_flow_components, extract_hyperparams, extract_controls
    # 4. entropy per group: compute_preprocessing_entropy, compute_hyperparameter_entropy
    # 5. df = build_analysis_dataset(...)
    # 6. result = run_mediation_analysis(df); save_mediation_results(result, PATHS['results'])
    # 7. p2a = test_p2a(df); p2b = test_p2b(df)
    # 8. visualize.* calls; assert result against SUCCESS_CRITERIA
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code — verified via Serena)

```python
# From: docs/youra_research/h-e1/code/collect.py (ACTUAL CODE)
def collect_datasets(min_date: str = MIN_DATE) -> pd.DataFrame: ...
def get_matched_runs(dataset_id: int, min_runs: int = MIN_RUNS_PER_GROUP) -> pd.DataFrame: ...
def extract_controls(dataset_id: int, flow_id: int) -> dict: ...
    # Returns: {"stability": float, "algo_family": str, "sklearn_version": str}

# From: docs/youra_research/h-e1/code/metadata_score.py (ACTUAL CODE)
def compute_metadata_score(dataset) -> int: ...  # 0-5 int score, verified 5-field logic above

# From: docs/youra_research/h-e1/code/analysis.py (ACTUAL CODE)
def compute_reproducibility_iqr(runs_df: pd.DataFrame) -> pd.DataFrame: ...
    # groupby(data_id,flow_id,setup_id) -> cols: iqr, mean, std, count
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, not spec). No naming discrepancies found between h-e1 `03_logic.md` (n/a — not read, code read directly) and code; h-m1 replicates these functions verbatim into its own folder (no cross-import, per PRD standalone-reproducibility requirement).
