# Logic: H-E1 — Data Pipeline Validation & FAIL FAST Gate Verification

**Applied**: Standard Python dataclass + statsmodels OLS pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## L1: `compute_partial_r2` [Complexity: 14, Budget: E4/4]

### API Signatures

```python
# code/gates.py
import pandas as pd
import statsmodels.api as sm

def compute_partial_r2(
    predictor: pd.Series,
    controls: pd.DataFrame,
) -> float:
    """OLS residualization: partial_r2 = 1 - rsquared(predictor ~ controls).
    Returns 1.0 if controls is empty (no temporal confounds to remove)."""
```

### Pseudo-code

```
1. if controls is empty or has 0 columns:
       return 1.0  # no temporal variance → full variance is non-temporal

2. X = sm.add_constant(controls.dropna())           # add intercept
3. y = predictor.loc[X.index].dropna()              # align index
4. X = X.loc[y.index]                               # sync after y dropna
5. if len(y) < len(controls.columns) + 2:
       raise ValueError("Insufficient observations for OLS")
6. model = sm.OLS(y, X).fit()
7. return 1.0 - model.rsquared                      # partial_r2
```

**Edge cases:**
- Empty controls → return 1.0 (pass guaranteed; no confounds present)
- Single benchmark (n=1) → raises ValueError before OLS (caught by caller)
- NaN in predictor or controls → align index via dropna before fitting

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L1-1 | OLS residualization | Implement compute_partial_r2 with empty-controls guard |

---

## L2: `GateValidator.g0_coverage` [Complexity: 14, Budget: E4/4]

### API Signatures

```python
# code/gates.py
from dataclasses import dataclass

@dataclass
class GateResult:
    gate: str        # e.g. "G0"
    passed: bool
    value: float
    threshold: float
    message: str

class GateValidator:
    def g0_coverage(
        self,
        n_matched: int,
        n_total: int = 87,
    ) -> GateResult:
        """Coverage gate: passes if n_matched / n_total >= 0.80."""
```

### Pseudo-code

```
1. coverage = n_matched / n_total
2. passed = coverage >= G0_COVERAGE_MIN   # 0.80
3. msg = f"G0 COVERAGE: {coverage:.3f} (threshold={G0_COVERAGE_MIN})"
4. print(msg)
5. return GateResult(
       gate="G0",
       passed=passed,
       value=coverage,
       threshold=G0_COVERAGE_MIN,
       message=msg,
   )
```

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L2-1 | GateResult dataclass | Define GateResult with gate, passed, value, threshold, message |
| L2-2 | g0_coverage | Compute coverage ratio; return GateResult |

---

## L3: `GateValidator.g4_vif` [Complexity: 14, Budget: E4/4]

### API Signatures

```python
# code/gates.py
from statsmodels.stats.outliers_influence import variance_inflation_factor

class VIFChecker:
    COVARIATES: list[str] = [
        "log_unique_paper_count_at_intro_z",
        "paper_diversity_ratio_at_intro_z",
        "task_age",
        "log_publication_volume",
        "benchmark_introduction_year",
    ]

    def compute(self, panel: pd.DataFrame) -> dict[str, float]:
        """Return {covariate: VIF} for all COVARIATES present in panel."""

    def collinearity_failsafe(self, stats_df: pd.DataFrame) -> float:
        """Pearson r between log_unique_paper_count_at_intro_z and
        paper_diversity_ratio_at_intro_z; logs warning if |r| > 0.95."""

class GateValidator:
    def g4_vif(
        self,
        enriched_panel: pd.DataFrame,
    ) -> GateResult:
        """VIF gate: warn if any VIF in [5, 10); fail if any VIF >= 10."""
```

### Pseudo-code

```
VIFChecker.compute(panel):
1. cols = [c for c in COVARIATES if c in panel.columns]
2. X = sm.add_constant(panel[cols].dropna())   # shape: (n, k+1)
3. vif_dict = {}
4. for i, col in enumerate(cols):
       # i+1 because add_constant puts const at col 0
       vif_dict[col] = variance_inflation_factor(X.values, i + 1)
5. return vif_dict

VIFChecker.collinearity_failsafe(stats_df):
1. from scipy.stats import pearsonr
2. r, _ = pearsonr(
       stats_df["log_unique_paper_count_at_intro_z"],
       stats_df["paper_diversity_ratio_at_intro_z"],
   )
3. if abs(r) > COLLINEARITY_R_MAX:   # 0.95
       print(f"WARNING: High collinearity r={r:.3f}; H-M1 should use single predictor")
4. return r

GateValidator.g4_vif(enriched_panel):
1. checker = VIFChecker()
2. vif_dict = checker.compute(enriched_panel)
3. max_vif = max(vif_dict.values())
4. if max_vif >= G4_VIF_MAX:          # 10.0
       passed = False
5. elif max_vif >= G4_VIF_WARN:       # 5.0
       print(f"WARNING: VIF in warn range: {vif_dict}")
       passed = True
6. else:
       passed = True
7. msg = f"G4 VIF: max={max_vif:.2f} (warn={G4_VIF_WARN}, fail>={G4_VIF_MAX})"
8. print(msg)
9. return GateResult(gate="G4", passed=passed, value=max_vif,
                     threshold=G4_VIF_MAX, message=msg)
```

### Subtasks [3/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L3-1 | VIFChecker.compute | variance_inflation_factor loop over COVARIATES |
| L3-2 | VIFChecker.collinearity_failsafe | Pearson r with warning log |
| L3-3 | g4_vif | Orchestrate VIF check with warn/fail thresholds |

---

## L4: `GateValidator.run_all` [Complexity: 14, Budget: E4/4]

### API Signatures

```python
class GateValidator:
    def g1_log_count_time_independence(
        self,
        stats_df: pd.DataFrame,
        panel: pd.DataFrame,
    ) -> GateResult:
        """partial_r2 of log_unique_paper_count_at_intro_z ~ [task_age, intro_year]."""

    def g2_diversity_ratio_time_independence(
        self,
        stats_df: pd.DataFrame,
        panel: pd.DataFrame,
    ) -> GateResult:
        """partial_r2 of paper_diversity_ratio_at_intro_z ~ [task_age, intro_year]."""

    def g3_diversity_variance(
        self,
        stats_df: pd.DataFrame,
    ) -> GateResult:
        """std(paper_diversity_ratio_at_intro) > 0.10."""

    def run_all(
        self,
        stats_df: pd.DataFrame,
        panel: pd.DataFrame,
        n_matched: int,
    ) -> list[GateResult]:
        """Run G0->G4 sequentially; SystemExit(1) on first failure."""
```

### Pseudo-code

```
g1_log_count_time_independence(stats_df, panel):
1. merged = stats_df.merge(panel[["task_path", "task_age",
       "benchmark_introduction_year"]], on="task_path", how="left")
2. predictor = merged["log_unique_paper_count_at_intro_z"]
3. controls = merged[["task_age", "benchmark_introduction_year"]]
4. pr2 = compute_partial_r2(predictor, controls)
5. passed = pr2 > G1_PARTIAL_R2_MIN   # 0.01
6. msg = f"G1 LOG-COUNT TIME-INDEP: partial_r2={pr2:.4f} (threshold>{G1_PARTIAL_R2_MIN})"
7. print(msg)
8. return GateResult(gate="G1", passed=passed, value=pr2,
                     threshold=G1_PARTIAL_R2_MIN, message=msg)

g2_diversity_ratio_time_independence(stats_df, panel):
# same pattern as g1, using "paper_diversity_ratio_at_intro_z"
1. merged = stats_df.merge(panel[["task_path", "task_age",
       "benchmark_introduction_year"]], on="task_path", how="left")
2. predictor = merged["paper_diversity_ratio_at_intro_z"]
3. controls = merged[["task_age", "benchmark_introduction_year"]]
4. pr2 = compute_partial_r2(predictor, controls)
5. passed = pr2 > G2_PARTIAL_R2_MIN   # 0.01
6. msg = f"G2 DIV-RATIO TIME-INDEP: partial_r2={pr2:.4f} (threshold>{G2_PARTIAL_R2_MIN})"
7. print(msg)
8. return GateResult(gate="G2", passed=passed, value=pr2,
                     threshold=G2_PARTIAL_R2_MIN, message=msg)

g3_diversity_variance(stats_df):
1. std_val = stats_df["paper_diversity_ratio_at_intro"].std()
2. passed = std_val > G3_STD_MIN   # 0.10
3. msg = f"G3 DIV-VARIANCE: std={std_val:.4f} (threshold>{G3_STD_MIN})"
4. print(msg)
5. return GateResult(gate="G3", passed=passed, value=std_val,
                     threshold=G3_STD_MIN, message=msg)

run_all(stats_df, panel, n_matched):
1. gates_fn = [
       lambda: self.g0_coverage(n_matched),
       lambda: self.g1_log_count_time_independence(stats_df, panel),
       lambda: self.g2_diversity_ratio_time_independence(stats_df, panel),
       lambda: self.g3_diversity_variance(stats_df),
       lambda: self.g4_vif(panel.merge(stats_df, on="task_path", how="left")),
   ]
2. results: list[GateResult] = []
3. for fn in gates_fn:
       result = fn()
       results.append(result)
       if not result.passed:
           print(f"FAIL FAST: {result.message}")
           raise SystemExit(1)
4. return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L4-1 | g1_log_count_time_independence | Merge panel, call compute_partial_r2, return GateResult |
| L4-2 | g2_diversity_ratio_time_independence | Same pattern for diversity_ratio_z |
| L4-3 | g3_diversity_variance | std check on paper_diversity_ratio_at_intro |
| L4-4 | run_all | Sequential gate loop with SystemExit(1) on first failure |

---

## L5: `FuzzyJoiner.join` [Complexity: 13, Budget: E3/2]

### API Signatures

```python
# code/pipeline.py
from rapidfuzz import fuzz, process as rfuzz_process

class FuzzyJoiner:
    def join(
        self,
        eval_df: pd.DataFrame,
        panel: pd.DataFrame,
        threshold: int = 85,
    ) -> pd.DataFrame:
        """Map eval_df.task_path to panel slugs via token_sort_ratio.
        Returns eval_df with 'matched_task' column (None if score < threshold)."""

    def coverage_count(self, joined: pd.DataFrame) -> int:
        """Count panel benchmarks with >=1 non-null paper_url after join."""
```

### Pseudo-code

```
join(eval_df, panel, threshold=85):
1. h_e2_slugs = panel["task_path"].unique().tolist()
2. def match_one(slug: str) -> str | None:
       result = rfuzz_process.extractOne(
           slug,
           h_e2_slugs,
           scorer=fuzz.token_sort_ratio,
       )
       if result is None or result[1] < threshold:
           return None
       return result[0]   # matched slug string
3. eval_df = eval_df.copy()
4. eval_df["matched_task"] = eval_df["task_path"].map(match_one)
5. return eval_df

coverage_count(joined):
1. matched = joined[joined["matched_task"].notna()]
2. # count distinct panel benchmarks that have >=1 paper_url
3. covered = (
       matched[matched["paper_url"].notna()]
       .groupby("matched_task")["paper_url"]
       .count()
   )
4. return len(covered)   # number of panel benchmarks with >=1 paper
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L5-1 | FuzzyJoiner.join + coverage_count | rapidfuzz token_sort_ratio loop; coverage count |

---

## L6: `DiversityAggregator.aggregate` [Complexity: 13, Budget: E3/2]

### API Signatures

```python
# code/pipeline.py
import numpy as np

class DiversityAggregator:
    def filter_temporal(
        self,
        joined: pd.DataFrame,
        panel: pd.DataFrame,
    ) -> pd.DataFrame:
        """Retain rows where pub_year <= intro_year; fallback to all rows if unavailable."""

    def aggregate(
        self,
        filtered_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Per matched_task: unique_count, total_rows, diversity_ratio, log_unique_count."""

    def z_standardize(
        self,
        stats_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Add _z columns for log_unique_count and diversity_ratio."""
```

### Pseudo-code

```
filter_temporal(joined, panel):
1. if "pub_year" not in joined.columns:
       return joined   # fallback: use all rows
2. intro_map = panel.set_index("task_path")["benchmark_introduction_year"].to_dict()
3. joined = joined.copy()
4. joined["intro_year"] = joined["matched_task"].map(intro_map)
5. mask = (
       joined["pub_year"].isna() |          # keep if pub_year unknown
       joined["intro_year"].isna() |        # keep if intro_year unknown
       (joined["pub_year"] <= joined["intro_year"])
   )
6. return joined[mask]

aggregate(filtered_df):
1. stats = (
       filtered_df[filtered_df["matched_task"].notna()]
       .groupby("matched_task")
       .agg(
           unique_count=("paper_url", "nunique"),
           total_rows=("paper_url", "count"),
       )
       .reset_index()
   )
2. stats["diversity_ratio"] = stats["unique_count"] / stats["total_rows"].clip(lower=1)
3. stats["log_unique_count"] = np.log1p(stats["unique_count"])
4. # rename to final column names
5. stats = stats.rename(columns={
       "matched_task": "task_path",
       "log_unique_count": "log_unique_paper_count_at_intro",
       "diversity_ratio": "paper_diversity_ratio_at_intro",
   })
6. return stats   # columns: task_path, unique_count, total_rows,
                  #          paper_diversity_ratio_at_intro,
                  #          log_unique_paper_count_at_intro

z_standardize(stats_df):
1. stats_df = stats_df.copy()
2. for col, z_col in [
       ("log_unique_paper_count_at_intro", "log_unique_paper_count_at_intro_z"),
       ("paper_diversity_ratio_at_intro",  "paper_diversity_ratio_at_intro_z"),
   ]:
       mean_ = stats_df[col].mean()
       std_  = stats_df[col].std()
       stats_df[z_col] = (stats_df[col] - mean_) / std_
3. return stats_df
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L6-1 | DiversityAggregator.filter_temporal | pub_year <= intro_year filter with fallback |
| L6-2 | DiversityAggregator.aggregate + z_standardize | groupby agg, log1p, z-score two columns |

---

## Subtask Summary (6/6 used)

| ID | Epic | Subtask | Key Function |
|----|------|---------|--------------|
| L1-1 | E4 | OLS residualization | compute_partial_r2 |
| L2-1/2 | E4 | GateResult + G0 | g0_coverage |
| L3-1/2/3 | E4 | VIF compute + g4_vif | VIFChecker.compute, g4_vif |
| L4-1/2/3/4 | E4 | G1/G2/G3 + run_all | g1, g2, g3, run_all |
| L5-1 | E3 | Fuzzy join + coverage | FuzzyJoiner.join |
| L6-1/2 | E3 | Temporal filter + agg + z | DiversityAggregator |
