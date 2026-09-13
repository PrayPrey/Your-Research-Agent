# Logic: H-E1
# AIFS Conditional Preference Shift Detection in HH-RLHF

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Type:** Statistical analysis pipeline — no neural network training
**Date:** 2026-05-12
**Gate:** β₄ > 0, OR ≥ 1.10, p < 0.01, CI_lo > 1.0

Applied: modular-pipeline pattern (single-responsibility modules with explicit data contracts)
Applied: Standard Python statistical pipeline (no DL-specific KB patterns matched; similarity < 0.47)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A (Serena reports no active project at working directory; project is new)
**Relevant Symbols**: None — new implementation from scratch per PRD specifications

---

## Subtask Breakdown [5/5 used]

| ID | Module | Subtask | Description |
|----|--------|---------|-------------|
| L-3-1 | experiment.py | ConditionalLogit model fitting | Implement baseline + proposed + extended + perplexity models via statsmodels ConditionalLogit with groups=cluster_id |
| L-3-2 | experiment.py | Mechanism verification (5 indicators) | verify_mechanism_activated(): check beta4 fitted, data variance, split balance, cluster validity, effect nonzero |
| L-2-1 | data_prep.py | AIFS regex scoring + pair construction | compute_aifs_score() 4-pattern regex, build_pairs_df() with delta_aifs_x_split interaction column |
| L-2-2 | data_prep.py | Semantic clustering + validation | cluster_prompts() via sentence-transformers cosine threshold, validate_clusters() abort guard |
| L-4-1 | evaluate.py | Metrics extraction + LRT + gate check | compute_metrics() extracting OR/CI/LRT from ModelResult, check_gate() logic |

---

## Module: data_prep.py

### Constants

```python
import re
import numpy as np
import pandas as pd

AIFS_PATTERNS: dict[str, re.Pattern] = {
    "structured_list": re.compile(r"^\s*(\d+\.|[-*])\s", re.MULTILINE),
    "safety_preface":  re.compile(r"\b(I (cannot|must note|should mention)|Note that|Important:)\b", re.IGNORECASE),
    "cot_marker":      re.compile(r"\b(Let me (think|consider|break)|Step \d+:|First,|Therefore,)\b", re.IGNORECASE),
    "hedging":         re.compile(r"\b(however|that said|on the other hand|it depends)\b", re.IGNORECASE),
}
COSINE_THRESHOLD: float = 0.85
MIN_TOKEN_COUNT: int = 20
BATCH_SIZE: int = 512
RANDOM_SEED: int = 1
```

### API Signatures

```python
def load_hh_rlhf() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load Anthropic/hh-rlhf helpful-base and helpful-online splits.
    Returns (df_base, df_online) each with columns: [chosen, rejected].
    """
    ...

def extract_dialogue(example: dict) -> dict:
    """TRL common-prefix pattern: strip shared prefix to get {prompt, chosen, rejected}."""
    # 1. Find longest common prefix of example["chosen"] and example["rejected"]
    # 2. chosen_text = example["chosen"][len(prefix):]
    # 3. rejected_text = example["rejected"][len(prefix):]
    # 4. Return {"prompt": prefix, "chosen": chosen_text, "rejected": rejected_text}
    ...

def filter_pairs(df: pd.DataFrame, min_tokens: int = MIN_TOKEN_COUNT) -> pd.DataFrame:
    """Keep rows where both chosen and rejected have >= min_tokens whitespace-split tokens."""
    # mask = (df["chosen"].str.split().str.len() >= min_tokens) &
    #        (df["rejected"].str.split().str.len() >= min_tokens)
    # return df[mask].reset_index(drop=True)
    ...

def compute_aifs_score(text: str) -> float:
    """AIFS density: total pattern matches / (token_count / 100). Returns float >= 0."""
    # token_count = max(1, len(text.split()))
    # hits = sum(len(p.findall(text)) for p in AIFS_PATTERNS.values())
    # return hits / (token_count / 100)
    ...

def cluster_prompts(
    prompts: list[str],
    threshold: float = COSINE_THRESHOLD,
    batch_size: int = BATCH_SIZE,
) -> np.ndarray:
    """Greedy cosine-threshold clustering of prompts via all-MiniLM-L6-v2.
    Returns cluster_id array of shape [len(prompts),] with int cluster IDs.
    """
    # 1. encode prompts in batches -> embeddings [N, 384]
    # 2. Greedy assignment: for each prompt i, find first centroid j with cosine_sim(i,j) >= threshold
    # 3. If no centroid qualifies, create new cluster centroid = embedding[i]
    # 4. Return integer cluster_id array
    ...

def build_pairs_df(
    df_base: pd.DataFrame,
    df_online: pd.DataFrame,
    cluster_ids: np.ndarray,
) -> pd.DataFrame:
    """Construct analysis-ready pairs DataFrame.
    Returns DataFrame with columns:
      chosen          int       {0, 1}  (1 = chosen response selected)
      delta_aifs      float     aifs(chosen) - aifs(rejected)
      delta_length    float     len(chosen) - len(rejected)  [token count diff]
      delta_aifs_x_split float  delta_aifs * split  [interaction term]
      split           int       {0=base, 1=online}
      cluster_id      int       semantic cluster assignment
    """
    # 1. Compute aifs scores for chosen and rejected in df_base and df_online
    # 2. For each row create two observations (long format):
    #    obs_chosen:   chosen=1, delta_aifs=aifs_c-aifs_r, delta_length=len_c-len_r
    #    obs_rejected: chosen=0, delta_aifs=aifs_r-aifs_c, delta_length=len_r-len_c
    #    (conditional logit requires one row per alternative, paired by cluster_id)
    # 3. Assign split=0 for df_base rows, split=1 for df_online rows
    # 4. delta_aifs_x_split = delta_aifs * split
    # 5. Assign cluster_id from cluster_ids array (indexed by prompt position)
    ...

def validate_clusters(df_pairs: pd.DataFrame) -> None:
    """Abort if fewer than 100 clusters contain >= 2 pairs. Raises ValueError."""
    # counts = df_pairs.groupby("cluster_id").size()
    # valid = (counts >= 2).sum()
    # if valid < 100: raise ValueError(f"Only {valid} valid clusters; need >= 100")
    ...
```

---

## Module: experiment.py

### Type Alias

```python
import statsmodels.discrete.conditional_models as cm
ModelResult = cm.ConditionalLogitResults
```

### API Signatures

```python
def fit_baseline_model(df_pairs: pd.DataFrame) -> ModelResult:
    """Fit ConditionalLogit: chosen ~ delta_aifs + delta_length, groups=cluster_id."""
    ...

def fit_proposed_model(df_pairs: pd.DataFrame) -> ModelResult:
    """Fit ConditionalLogit: chosen ~ delta_aifs + delta_length + delta_aifs_x_split, groups=cluster_id."""
    ...

def fit_extended_model(df_pairs: pd.DataFrame) -> ModelResult:
    """Fit proposed model + supply_prop covariate (supply-side control)."""
    ...

def fit_perplexity_model(df_pairs: pd.DataFrame) -> ModelResult:
    """Fit proposed model + delta_perplexity covariate (token length proxy)."""
    ...

def compute_supply_prop(df_pairs: pd.DataFrame) -> pd.DataFrame:
    """Add supply_prop column: fraction of online pairs within each cluster_id.
    Returns df_pairs with new column supply_prop (float, per-cluster scalar broadcast).
    """
    # supply_prop[cluster] = online_count[cluster] / total_count[cluster]
    ...

def verify_mechanism_activated(
    result: ModelResult,
    df_pairs: pd.DataFrame,
) -> tuple[bool, dict]:
    """Check 5 mechanism indicators. Raises RuntimeError if any is False.
    Returns (all_ok: bool, indicators: dict[str, bool]).
    Indicators:
      beta4_fitted    : result.params["delta_aifs_x_split"] exists (not NaN)
      data_variance   : df_pairs["delta_aifs"].std() > 0
      split_balanced  : both split values present with > 5% share each
      clusters_valid  : validate_clusters passes (>= 100 clusters with >= 2 pairs)
      effect_nonzero  : abs(result.params["delta_aifs_x_split"]) > 1e-6
    """
    ...
```

### Pseudo-code: fit_proposed_model (representative for all fit_* functions)

```
1. endog = df_pairs["chosen"].values
2. exog  = df_pairs[["delta_aifs", "delta_length", "delta_aifs_x_split"]].values
3. groups = df_pairs["cluster_id"].values
4. model = ConditionalLogit(endog, exog, groups=groups)
5. result = model.fit(method="bfgs", disp=False)
6. return result
```

---

## Module: evaluate.py

### Constants

```python
GATE_BETA4_MIN: float = 0.0
GATE_OR_MIN: float = 1.10
GATE_PVAL_MAX: float = 0.01
GATE_CI_LO_MIN: float = 1.0
RESULTS_DIR: str = "h-e1/results"
```

### API Signatures

```python
def compute_metrics(
    result_baseline: ModelResult,
    result_proposed: ModelResult,
) -> dict:
    """Extract gate-relevant metrics from fitted models.
    Returns dict with keys:
      beta4              float   coefficient of delta_aifs_x_split
      OR                 float   exp(beta4)
      CI_lo              float   exp(lower 95% CI of beta4)
      CI_hi              float   exp(upper 95% CI of beta4)
      pval               float   p-value of beta4 coefficient
      mcfadden_r2_baseline float  1 - llf_baseline / llnull_baseline
      mcfadden_r2_proposed float  1 - llf_proposed / llnull_proposed
      lrt_stat           float   2 * (llf_proposed - llf_baseline)
      lrt_pval           float   chi2 p-value for lrt_stat with df=1
    """
    # beta4 = result_proposed.params["delta_aifs_x_split"]
    # conf = result_proposed.conf_int()  # DataFrame [lo, hi]
    # CI_lo, CI_hi = exp(conf.loc["delta_aifs_x_split"])
    # pval = result_proposed.pvalues["delta_aifs_x_split"]
    # lrt_stat = 2 * (result_proposed.llf - result_baseline.llf)
    # lrt_pval = scipy.stats.chi2.sf(lrt_stat, df=1)
    ...

def check_gate(metrics: dict) -> bool:
    """Return True iff β₄>0 AND OR>=1.10 AND pval<0.01 AND CI_lo>1.0."""
    return (
        metrics["beta4"] > GATE_BETA4_MIN
        and metrics["OR"] >= GATE_OR_MIN
        and metrics["pval"] < GATE_PVAL_MAX
        and metrics["CI_lo"] > GATE_CI_LO_MIN
    )

def save_metrics(metrics: dict, gate_passed: bool) -> None:
    """Write metrics + gate_passed to h-e1/results/metrics.json."""
    ...

def save_model_summary(result_proposed: ModelResult) -> None:
    """Write result_proposed.summary().as_text() to h-e1/results/model_summary.txt."""
    ...

def save_pairs_df(df_pairs: pd.DataFrame) -> None:
    """Write df_pairs to h-e1/results/pairs_df.parquet."""
    ...
```

---

## Module: visualize.py

### Constants

```python
FIGURES_DIR: str = "h-e1/figures"
SENSITIVITY_THRESHOLDS: list[float] = [0.75, 0.80, 0.85, 0.90]
```

### API Signatures

```python
def plot_or_comparison(metrics: dict) -> None:
    """Fig 1: Bar chart OR (proposed) vs null OR=1.0 with 95% CI error bars.
    Saves: h-e1/figures/fig1_or_comparison.png
    """
    # xerr = [[OR - CI_lo], [CI_hi - OR]]
    ...

def plot_forest(results: dict[str, ModelResult]) -> None:
    """Fig 2: Forest plot of β₄ across model specs with 95% CI.
    Keys expected: "baseline", "proposed", "extended", "perplexity"
    Saves: h-e1/figures/fig2_forest_plot.png
    """
    ...

def plot_aifs_distribution(df_pairs: pd.DataFrame) -> None:
    """Fig 3: Violin plot of AIFS scores (chosen vs rejected) faceted by split.
    Uses columns: delta_aifs, split. Saves: h-e1/figures/fig3_aifs_distribution.png
    """
    ...

def plot_cluster_histogram(df_pairs: pd.DataFrame) -> None:
    """Fig 4: Histogram of semantic cluster sizes (pairs per cluster_id).
    Saves: h-e1/figures/fig4_cluster_histogram.png
    """
    ...

def plot_or_sensitivity(
    df_base: pd.DataFrame,
    df_online: pd.DataFrame,
    thresholds: list[float] = SENSITIVITY_THRESHOLDS,
) -> None:
    """Fig 5: OR estimates across cosine thresholds [0.75, 0.80, 0.85, 0.90].
    For each threshold: re-cluster -> build_pairs_df -> fit_proposed_model -> extract OR.
    Saves: h-e1/figures/fig5_or_sensitivity.png
    """
    ...
```

---

## Module: run_experiment.py

### API Signatures

```python
def parse_args() -> argparse.Namespace:
    """Parse CLI args. Flags: --smoke-test (bool), --log-path (str)."""
    ...

def setup_logging(log_path: str = "h-e1/results/experiment.log") -> None:
    """Configure root logger: console + rotating file handler, format with timestamps."""
    ...

def smoke_test(df_pairs: pd.DataFrame) -> None:
    """Run pipeline on first 1000 rows of df_pairs. Asserts metrics dict non-null.
    Raises AssertionError on failure.
    """
    ...

def main() -> None:
    """Full pipeline orchestration.
    Steps:
      1.  parse_args() + setup_logging()
      2.  load_hh_rlhf() -> df_base_raw, df_online_raw
      3.  extract_dialogue() applied to each row
      4.  filter_pairs(df_base), filter_pairs(df_online)
      5.  cluster_prompts(all_prompts) -> cluster_ids
      6.  build_pairs_df(df_base, df_online, cluster_ids)
      7.  validate_clusters(df_pairs)
      8.  if args.smoke_test: smoke_test(df_pairs); return
      9.  compute_supply_prop(df_pairs)
      10. fit_baseline_model + fit_proposed_model + fit_extended_model + fit_perplexity_model
      11. verify_mechanism_activated(result_proposed, df_pairs)
      12. compute_metrics(result_baseline, result_proposed)
      13. check_gate(metrics) -> gate_passed
      14. save_metrics(metrics, gate_passed) + save_model_summary + save_pairs_df
      15. plot_or_comparison + plot_forest + plot_aifs_distribution
          + plot_cluster_histogram + plot_or_sensitivity
    """
    ...
```

---

## Data Contracts

### df_base / df_online (raw, after load_hh_rlhf)

| Column   | Type   | Note                        |
|----------|--------|-----------------------------|
| chosen   | str    | Full chosen response text   |
| rejected | str    | Full rejected response text |

### df_base / df_online (after extract_dialogue + filter_pairs)

| Column   | Type   | Note                         |
|----------|--------|------------------------------|
| prompt   | str    | Common prefix (shared query) |
| chosen   | str    | Chosen response only         |
| rejected | str    | Rejected response only       |

### df_pairs (analysis-ready, output of build_pairs_df)

| Column             | Type    | Values / Range         | Note                                 |
|--------------------|---------|------------------------|--------------------------------------|
| chosen             | int     | {0, 1}                 | 1 = this alternative was chosen      |
| delta_aifs         | float   | R                      | aifs(chosen) - aifs(rejected)        |
| delta_length       | float   | R (token count diff)   | len(chosen) - len(rejected)          |
| delta_aifs_x_split | float   | R                      | delta_aifs * split (interaction)     |
| split              | int     | {0, 1}                 | 0=helpful-base, 1=helpful-online     |
| cluster_id         | int     | >= 0                   | Semantic cluster assignment          |
| supply_prop        | float   | [0, 1]  (optional col) | Fraction online pairs in cluster     |
| delta_perplexity   | float   | R       (optional col) | Token length proxy for perplexity    |

### metrics dict (output of compute_metrics)

| Key                   | Type  | Gate Condition   |
|-----------------------|-------|------------------|
| beta4                 | float | > 0              |
| OR                    | float | >= 1.10          |
| CI_lo                 | float | > 1.0            |
| CI_hi                 | float | —                |
| pval                  | float | < 0.01           |
| mcfadden_r2_baseline  | float | —                |
| mcfadden_r2_proposed  | float | —                |
| lrt_stat              | float | —                |
| lrt_pval              | float | —                |
| gate_passed           | bool  | written by save_metrics |

---

*Generated by Logic Agent — H-E1 | EXISTENCE | Phase 3*
*Archon KB: no domain-specific content matched (similarity < 0.47 for all queries)*
*Serena: green-field project — no existing codebase to analyze*
