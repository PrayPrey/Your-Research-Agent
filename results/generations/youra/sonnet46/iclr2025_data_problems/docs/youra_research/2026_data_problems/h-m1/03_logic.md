# H-M1 Logic: Conditional Log-Odds Demographic-Occupation Analysis

**Hypothesis:** H-M1 (MECHANISM — Corpus → Log-Odds)
**Base Hypothesis:** H-E1 (COMPLETED, PASS)
**Generated:** 2026-03-14

Applied: corpus-statistical-analysis-pipeline
Applied: spearman-gate-evaluation-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 code analyzed)
**Status**: API signatures verified from base code
**Analyzed Path**: `h-e1/code/`
**Relevant Symbols**:
- `CorpusFilter.__init__(fasttext_model_path: str, seed: int = 42)`
- `CorpusFilter.load_corpus(config_id: str, data_dir: str) -> List[dict]`
- `CorpusFilter.build_all_corpora(data_dir, dataset_id, n_docs, configurations) -> Dict[str, str]`
- `EntropyMeasure.__init__(occ_lexicon, demo_lexicon, window_size=10)`
- `EntropyMeasure._tokenize(text: str) -> List[str]` — `re.findall(r"[a-zA-Z']+", text.lower())`
- `EntropyMeasure.compute_joint_counts(docs) -> Dict[Tuple[str,str], int]` — keys are `(occ_token, demo_token)` order
- H-E1 CONFIG `window_size=10` (not 5; trust actual code)
- H-E1 CONFIG `occupation_lexicon` (60 tokens), `demographic_lexicon` (30 tokens)

---

## External Dependencies API

### Verified Signatures from h-e1 Actual Code

```python
# From: h-e1/code/corpus_filter.py
class CorpusFilter:
    def __init__(self, fasttext_model_path: str, seed: int = 42): ...
    def load_corpus(self, config_id: str, data_dir: str) -> List[dict]: ...
    def build_all_corpora(
        self,
        data_dir: str,
        dataset_id: str = "mlfoundations/dclm-baseline-1.0",
        n_docs: int = 10_000_000,
        configurations: Optional[list] = None,
    ) -> Dict[str, str]: ...

# From: h-e1/code/entropy_measure.py
class EntropyMeasure:
    def __init__(self, occ_lexicon: List[str], demo_lexicon: List[str], window_size: int = 10): ...
    def _tokenize(self, text: str) -> List[str]:
        # re.findall(r"[a-zA-Z']+", text.lower())
        ...
    def compute_joint_counts(self, docs: List[dict]) -> Dict[Tuple[str, str], int]:
        # Keys: (occ_token, demo_token) — NOTE: occ is index 0, demo is index 1
        ...

# From: h-e1/code/config.py
CONFIG = {
    "window_size": 10,         # VERIFIED: 10, not 5
    "occupation_lexicon": [...],  # 60 WinoBias tokens
    "demographic_lexicon": [...], # 30 tokens
    "configurations": [           # C0-C6
        {"id": "C1", "filter_type": "fasttext", "percentile": 10}, ...
    ],
    "data_dir": "/home/anonymous/.../h-e1/data",
    "fasttext_model_path": "/home/anonymous/.../h-e1/data/models/openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin",
}
```

**Verified from**: `h-e1/code/` (actual implementation)

**Critical Note on joint_counts key order**: `EntropyMeasure.compute_joint_counts` stores `(occ_token, demo_token)` — the outer loop iterates over occ tokens and inner over demo tokens within the window. H-M1's `LogOddsComputer.compute_cooccurrence_counts` should use `(demo_token, occ_token)` order for clarity and must document this explicitly.

---

## A-3: Co-occurrence Counting [Complexity: 12, Budget: 2 subtasks]

Applied: sliding-window-cooccurrence-pattern

### API Signatures

```python
class LogOddsComputer:
    def __init__(
        self,
        occ_lexicon: List[str],
        demo_lexicon: List[str],
        window_size: int = 10,   # matches h-e1 actual value
        alpha: float = 0.5,
    ) -> None:
        """Initialize with lexicons and smoothing params."""

    def _tokenize(self, text: str) -> List[str]:
        """Identical to EntropyMeasure._tokenize: re.findall(r\"[a-zA-Z']+\", text.lower())"""

    def compute_cooccurrence_counts(
        self,
        docs: List[dict],
    ) -> Tuple[
        Dict[Tuple[str, str], int],  # cooc_demo_occ: {(demo, occ): count}
        Dict[str, int],              # count_demo: {demo_token: window_count}
        Dict[str, int],              # count_occ: {occ_token: window_count}
        int,                         # total_windows: N
    ]:
        """Sliding-window co-occurrence. Window of ±window_size tokens around each occ token.
        Key order: (demo_token, occ_token).
        count_demo[d] = # windows containing demo token d.
        count_occ[o] = # windows containing occ token o.
        total_windows = total # of occ-anchor windows scanned.
        """
```

### Pseudo-code

```
for doc in docs:
    tokens = _tokenize(doc["text"])
    for i, tok in enumerate(tokens):
        if tok in occ_lexicon:
            window = tokens[max(0,i-W) : i+W+1] excluding position i
            count_occ[tok] += 1
            total_windows += 1
            for w in window:
                if w in demo_lexicon:
                    cooc_demo_occ[(w, tok)] += 1
                    count_demo[w] += 1  # per-occ-window occurrence
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Sliding Window Scan | Implement `compute_cooccurrence_counts` with ±window_size around each occ token |
| L-3-2 | Tokenizer Parity | `_tokenize` must exactly match H-E1 `EntropyMeasure._tokenize` regex |

---

## A-4: Log-Odds Matrix [Complexity: 14, Budget: 4 subtasks]

Applied: laplace-smoothed-log-odds-contingency-table

### API Signatures

```python
    def compute_log_odds_pair(
        self,
        n_demo_occ: int,
        n_demo_not_occ: int,
        n_not_demo_occ: int,
        n_not_demo_not_occ: int,
    ) -> Tuple[float, float, float]:
        """2x2 contingency table log-odds via statsmodels Table2x2.
        Laplace smoothing alpha=0.5 applied before Table2x2.
        Returns: (log_odds, ci_low, ci_high)
        """

    def compute_log_odds_matrix(
        self,
        docs: List[dict],
        config_id: str,
    ) -> pd.DataFrame:
        """Compute (demo × occ) log-odds for one corpus config.
        Returns DataFrame columns: [demographic, occupation, log_odds, ci_low, ci_high, config_id]
        Row count: N_demo * N_occ (all pairs, including zero-count pairs)
        """

    def compute_all_configs(
        self,
        corpora: Dict[str, List[dict]],
    ) -> pd.DataFrame:
        """Iterate over all configs, call compute_log_odds_matrix, concat.
        Returns shape: (N_demo * N_occ * N_configs, 6)
        """

    def aggregate_mean_log_odds(
        self,
        log_odds_df: pd.DataFrame,
    ) -> Dict[str, float]:
        """Group by config_id, return mean log_odds per config.
        Returns: {"C1": float, ..., "C6": float}
        """

    def save_log_odds_matrix(
        self,
        log_odds_df: pd.DataFrame,
        output_path: str,
    ) -> None:
        """Pivot to wide format: index=(demographic, occupation), columns=config_ids.
        Saves to output_path as CSV for H-M2 downstream use.
        Wide shape: (N_demo * N_occ, N_configs + 2)
        """
```

### Tensor Shapes

| Variable | Shape/Type | Note |
|----------|------------|------|
| cooc_demo_occ | Dict[(demo,occ), int] | sparse; missing pairs = 0 before alpha |
| log_odds_df | DataFrame (N_demo*N_occ*N_configs, 6) | long format |
| log_odds_matrix (wide) | DataFrame (N_demo*N_occ, N_configs) | pivoted, saved as CSV |
| mean_log_odds_per_config | Dict[str, float] | one scalar per config |

### Pseudo-code (compute_log_odds_matrix)

```
cooc, count_demo, count_occ, N = compute_cooccurrence_counts(docs)
rows = []
for demo in demo_lexicon:
    for occ in occ_lexicon:
        a = cooc.get((demo, occ), 0) + alpha          # demo AND occ
        b = count_demo.get(demo, 0) - cooc.get((demo,occ),0) + alpha  # demo AND NOT occ
        c = count_occ.get(occ, 0) - cooc.get((demo,occ),0) + alpha    # NOT demo AND occ
        d = N - count_demo.get(demo,0) - count_occ.get(occ,0) + cooc.get((demo,occ),0) + alpha
        lo, ci_lo, ci_hi = compute_log_odds_pair(a, b, c, d)
        rows.append((demo, occ, lo, ci_lo, ci_hi, config_id))
return pd.DataFrame(rows, columns=[...])
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Contingency Table | Implement `compute_log_odds_pair` with alpha=0.5 smoothing + `Table2x2` |
| L-4-2 | Matrix Computation | Implement `compute_log_odds_matrix` per-config nested loop |
| L-4-3 | All-Config Aggregation | Implement `compute_all_configs` + `aggregate_mean_log_odds` |
| L-4-4 | CSV Persistence | Implement `save_log_odds_matrix` wide pivot + CSV save |

---

## A-5: Spearman Gate [Complexity: 11, Budget: 2 subtasks]

Applied: spearman-gate-evaluation-pattern

### API Signatures

```python
class StatisticalTests:
    def __init__(self, n_bootstrap: int = 1000, seed: int = 42) -> None:
        """Initialize with bootstrap params."""

    def spearman_correlation(
        self,
        filtering_intensities: List[int],   # [10, 30, 50, 70, 90] for C1-C5
        mean_log_odds: List[float],          # parallel list for C1-C5
    ) -> Dict[str, float]:
        """scipy.stats.spearmanr over C1-C5 only. Returns: {rho, pvalue}"""

    def bootstrap_spearman_ci(
        self,
        filtering_intensities: List[int],
        mean_log_odds: List[float],
    ) -> Tuple[float, float]:
        """scipy.stats.bootstrap with n_resamples=1000, random_state=seed.
        Returns: (ci_low, ci_high)
        """

    def evaluate_gate(
        self,
        spearman_result: Dict[str, float],
        bootstrap_ci: Tuple[float, float],
    ) -> Dict[str, Any]:
        """Gate: abs(rho) > 0 AND pvalue < 0.05.
        Returns: {gate_passed: bool, rho, pvalue, bootstrap_ci_low, bootstrap_ci_high}
        """
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Spearman + Bootstrap | Implement `spearman_correlation` + `bootstrap_spearman_ci` (C1-C5 only) |
| L-5-2 | Gate Logic | Implement `evaluate_gate`; gate condition: `abs(rho) > 0 AND pvalue < 0.05` |

---

## A-6: Secondary Stats [Complexity: 12, Budget: 2 subtasks]

Applied: standard-scipy-statsmodels-pattern

### API Signatures

```python
    def ols_regression(
        self,
        filtering_intensities: List[int],   # [10, 30, 50, 70, 90]
        mean_log_odds: List[float],
    ) -> Dict[str, Any]:
        """statsmodels OLS: log_odds ~ percentile_cutoff.
        Returns: {coef, intercept, r_squared, pvalue}
        """

    def mann_whitney_u(
        self,
        log_odds_c5: np.ndarray,  # per-pair log_odds values for C5
        log_odds_c6: np.ndarray,  # per-pair log_odds values for C6
    ) -> Dict[str, float]:
        """scipy.stats.mannwhitneyu(alternative='two-sided').
        Returns: {statistic, pvalue}
        """

    def ks_test(
        self,
        log_odds_c1: np.ndarray,
        log_odds_c5: np.ndarray,
    ) -> Dict[str, float]:
        """scipy.stats.ks_2samp. Returns: {statistic, pvalue}"""

    def per_pair_spearman(
        self,
        log_odds_df: pd.DataFrame,
        filtering_intensities: List[int],   # [10, 30, 50, 70, 90]
    ) -> pd.DataFrame:
        """Per-(demographic, occupation) Spearman ρ across C1-C5.
        Groups log_odds_df by (demographic, occupation), filters to C1-C5.
        Returns DataFrame columns: [demographic, occupation, rho, pvalue]
        Shape: (N_demo * N_occ, 4)
        """

    def run_all_tests(
        self,
        log_odds_df: pd.DataFrame,
        mean_log_odds_per_config: Dict[str, float],
        filtering_intensities: List[int],
    ) -> Dict[str, Any]:
        """Orchestrate all tests. Returns unified results dict with keys:
        spearman, bootstrap_ci, ols, mann_whitney, ks, per_pair_spearman, gate
        """
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | OLS + Distribution Tests | Implement `ols_regression`, `mann_whitney_u`, `ks_test` |
| L-6-2 | Per-Pair Spearman + Orchestration | Implement `per_pair_spearman` + `run_all_tests` |

---

## A-8: Pipeline Orchestration [Complexity: 13, Budget: 2 subtasks]

Applied: standard-experiment-pipeline-pattern

### API Signatures

```python
def setup_h1_imports(he1_code_dir: str) -> None:
    """sys.path.insert(0, he1_code_dir) for CorpusFilter and config imports."""

def load_corpora(config: "HM1Config") -> Dict[str, List[dict]]:
    """Load C1-C6 from h-e1/data/corpora/*.jsonl via CorpusFilter.load_corpus().
    Falls back to CorpusFilter.build_all_corpora() if any subset missing.
    Returns: {"C1": [...], ..., "C6": [...]}
    """

def verify_mechanism_activated(
    log_odds_df: pd.DataFrame,
    stats_results: Dict[str, Any],
) -> Dict[str, Any]:
    """Returns: {log_odds_computed, shape_valid, variation_exists, spearman_computed, mechanism_activated}
    log_odds_computed: len(log_odds_df) > 0
    shape_valid: log_odds_df['config_id'].nunique() == 6
    variation_exists: log_odds_df['log_odds'].std() > 0
    spearman_computed: 'spearman' in stats_results
    mechanism_activated: all of above
    """

def write_results_json(results: Dict[str, Any], path: str) -> None: ...

def write_validation_md(
    results: Dict[str, Any],
    mechanism_check: Dict[str, Any],
    path: str,
) -> None: ...

def main() -> None:
    """
    1. parse_args() — --quick, --output-dir, --config
    2. load_config() → HM1Config
    3. setup_h1_imports(config.he1_code_dir)
    4. mkdir data_dir, figures_dir
    5. load_corpora(config) → Dict[str, List[dict]]
    6. get_he1_lexicons() → {occupation_lexicon, demographic_lexicon}
    7. LogOddsComputer(occ_lexicon, demo_lexicon, window_size=10, alpha=0.5)
    8. log_odds_df = computer.compute_all_configs(corpora)
    9. mean_log_odds = computer.aggregate_mean_log_odds(log_odds_df)
    10. stats = StatisticalTests(n_bootstrap=1000, seed=42).run_all_tests(
            log_odds_df, mean_log_odds, config.filtering_intensities)
    11. Visualizer(config.figures_dir).generate_all(log_odds_df, mean_log_odds, stats)
    12. mechanism_check = verify_mechanism_activated(log_odds_df, stats)
    13. computer.save_log_odds_matrix(log_odds_df, config.log_odds_matrix_path)
    14. write_results_json(results, config.results_path)
    15. write_validation_md(results, mechanism_check, config.validation_path)
    """
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Corpus Loading + Import Wiring | Implement `setup_h1_imports`, `load_corpora` with fallback to `build_all_corpora` |
| L-8-2 | main() Pipeline | Implement full 15-step main(), `verify_mechanism_activated`, `write_results_json`, `write_validation_md` |

---

## Subtask Budget Summary

| Epic | Task | Subtasks Used | Budget |
|------|------|--------------|--------|
| A-3 | Co-occurrence Counting | 2 | 2 |
| A-4 | Log-Odds Matrix | 4 | 4 |
| A-5 | Spearman Gate | 2 | 2 |
| A-6 | Secondary Stats | 2 | 2 |
| A-8 | Pipeline Orchestration | 2 | 2 |
| **Total** | | **12** | **12** |

---

## Key Implementation Notes for Phase 4

1. **window_size=10** — from h-e1/code/config.py actual code; PRD says 5 but trust actual code.
2. **Contingency table cell b**: `count_demo[demo] - cooc[(demo,occ)]` counts windows where demo appears but occ is the anchor (not a direct "demo AND NOT occ" global count). This is the correct approximation for window-based statistics.
3. **C6 exclusion from Spearman**: pass `filtering_intensities=[10,30,50,70,90]` and `mean_log_odds=[C1..C5 values]` to `spearman_correlation`. C6 only used in `mann_whitney_u`.
4. **Table2x2 usage**: `from statsmodels.stats.contingency_tables import Table2x2; t = Table2x2([[a,b],[c,d]]); lo = t.log_oddsratio; ci = t.log_oddsratio_confint()`.
5. **get_he1_lexicons()** in config.py: `sys.path.insert(0, HE1_CODE_DIR)` then `from config import CONFIG; return {"occupation_lexicon": CONFIG["occupation_lexicon"], "demographic_lexicon": CONFIG["demographic_lexicon"]}`.
