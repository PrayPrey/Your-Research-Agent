# Logic Design: H-E1
# BCBHS: Domain-Specific Health Signal Discriminability

**Date:** 2026-05-19
**Hypothesis:** H-E1 (EXISTENCE, LIGHT tier, MUST_WORK gate)
**Phase:** 3 - Logic Design
**Budget:** 8 subtasks

Applied: statistical-pipeline-module-pattern (Archon KB searched; no domain-specific matches — scipy.stats standard patterns applied)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation from scratch

---

## Module: data_pipeline.py

### API Signatures

```python
import pandas as pd
import numpy as np
from typing import Optional

def load_pwc_panel() -> pd.DataFrame:
    """Load PWC leaderboard panel from HuggingFace pwc-archive/evaluation-tables."""
    # Returns: DataFrame[benchmark, domain, model, date, score, quarter]
    # Filter: >=20 submissions, >=2 years history, known domain (cv|nlp), 2018-2025
    ...

def load_openml_panel() -> pd.DataFrame:
    """Load OpenML AMLB + CC18 benchmark panel."""
    # Returns: DataFrame[task_id, benchmark, model, date, score, quarter]
    # benchmark = task_name; domain = "tabular"
    # Filter: >=20 evaluated runs, >=2 years of submissions
    ...

def label_saturation(panel: pd.DataFrame) -> pd.DataFrame:
    """Add label column: saturated|healthy|excluded per (benchmark, quarter)."""
    # Saturated: Kendall tau > 0.90 for >=2 consecutive quarters
    # Healthy:   tau < 0.70
    # Excluded:  0.70 <= tau <= 0.90
    # Returns: panel with added column 'label'
    ...

def get_domain_panels(
    panel: pd.DataFrame,
    domain: str,              # "cv" | "nlp" | "tabular"
    min_saturated: int = 15,
    min_healthy: int = 15,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Filter panel to domain, split by label. Warn if < min thresholds."""
    # Returns: (saturated_df, healthy_df)
    ...
```

### Data Shapes

| Variable | Schema | Note |
|----------|--------|------|
| pwc_panel | `[benchmark, domain, model, date, score, quarter]` | date: datetime, quarter: "2022Q1" |
| openml_panel | `[task_id, benchmark, model, date, score, quarter]` | domain always "tabular" |
| labeled_panel | above + `label: str` | "saturated" \| "healthy" \| "excluded" |
| saturated_df / healthy_df | subset of labeled_panel for domain | row-filtered |

### Subtask: L-A1-1 — Load PWC + OpenML Panels

**Parent Epic**: A-1 (Data Pipeline, complexity 13)

```
load_pwc_panel():
  1. ds = load_dataset("pwc-archive/evaluation-tables", split="train")
  2. df = ds.to_pandas()[["task", "dataset", "metric", "model", "paper_date", "score"]]
  3. rename: dataset -> benchmark, task -> domain_raw, paper_date -> date
  4. map domain_raw -> "cv"|"nlp" using DOMAIN_MAP dict; drop unknowns
  5. filter: count per benchmark >= 20
  6. filter: (max_date - min_date) >= 730 days
  7. filter: date in [2018-01-01, 2025-12-31]
  8. add quarter = pd.PeriodIndex(date, freq="Q").astype(str)
  9. return cleaned DataFrame

load_openml_panel():
  1. suite = openml.study.get_suite("amlb-classification-all")
  2. task_ids = suite.tasks + CC18_TASK_IDS
  3. for task_id in task_ids:
       evals = openml.evaluations.list_evaluations(
           function="predictive_accuracy", tasks=[task_id], output_format="dataframe")
       evals["task_id"] = task_id
       evals["benchmark"] = task_name_map[task_id]
       all_evals.append(evals)
  4. df = pd.concat(all_evals)
  5. rename: setup_name->model, value->score, upload_time->date
  6. filter: count per task >= 20, date range >= 730 days
  7. add quarter; add domain="tabular"
  8. return DataFrame
```

### Subtask: L-A1-2 — Saturation Labeling

**Parent Epic**: A-1 (Data Pipeline, complexity 13)

```
label_saturation(panel):
  1. labels = {}
  2. for benchmark in panel["benchmark"].unique():
       bdf = panel[panel.benchmark == benchmark].sort_values("date")
       quarters = bdf["quarter"].unique() sorted chronologically
       tau_series = []
       for i, q in enumerate(quarters):
           models_q = bdf[bdf.quarter == q].set_index("model")["score"]
           if i == 0: prev_q = models_q; continue
           common = models_q.index.intersection(prev_q.index)
           if len(common) < 5: tau_series.append(None); continue
           tau, _ = scipy.stats.kendalltau(prev_q[common], models_q[common])
           tau_series.append((q, tau))
           prev_q = models_q
       # find consecutive runs of tau > 0.90 for >= 2 quarters
       consec = 0
       for q, tau in tau_series:
           if tau is not None and tau > 0.90:
               consec += 1
               if consec >= 2: labels[(benchmark, q)] = "saturated"; continue
           elif tau is not None and tau < 0.70:
               consec = 0; labels[(benchmark, q)] = "healthy"
           else:
               consec = 0; labels[(benchmark, q)] = "excluded"
  3. panel["label"] = panel.apply(
         lambda r: labels.get((r.benchmark, r.quarter), "excluded"), axis=1)
  4. return panel
```

---

## Module: signal_compute.py

### API Signatures

```python
import numpy as np
import pandas as pd
from typing import Optional

def compute_hd_cv(
    benchmark_scores: np.ndarray,    # shape (N_models,) at t-24mo
    held_out_scores: np.ndarray,     # shape (N_models,) on OOD/held-out variants
) -> float:
    """Robustness gap = mean(benchmark - held_out). Falls back to score variance if held_out empty."""
    ...

def compute_hd_nlp(
    benchmark_data: dict,            # {"scores": np.ndarray (N,), "model_ids": list[str]}
    reference_benchmark_data: dict,  # same schema for reference benchmark
) -> Optional[float]:
    """S_index via ConStat. Returns None if ConStat unavailable or data insufficient."""
    ...

def compute_hd_tabular(
    rankings_over_time: np.ndarray,  # shape (T, N_models) ranking matrix
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> float:
    """Block-bootstrapped mean Kendall tau stability. block_size = T // 4."""
    ...

def compute_domain_signals(
    panel: pd.DataFrame,
    domain: str,             # "cv" | "nlp" | "tabular"
    lookback_months: int = 24,
) -> pd.DataFrame:
    """Compute H_d signal per benchmark in panel for given domain."""
    # Returns: DataFrame[benchmark, label, hd_signal, domain]
    ...
```

### Subtask: L-A2-1 — compute_hd_cv with OOD Fallback

**Parent Epic**: A-2 (Signal Computation, complexity 15)

```
compute_hd_cv(benchmark_scores, held_out_scores):
  if held_out_scores is None or len(held_out_scores) == 0:
      # OOD fallback: score variance as CV proxy
      return float(np.var(benchmark_scores))
  common_len = min(len(benchmark_scores), len(held_out_scores))
  gap = benchmark_scores[:common_len] - held_out_scores[:common_len]
  return float(np.mean(gap))
```

### Subtask: L-A2-2 — compute_hd_nlp with ConStat + None Fallback

**Parent Epic**: A-2 (Signal Computation, complexity 15)

```
compute_hd_nlp(benchmark_data, reference_benchmark_data):
  try:
      import constat
      scores_b = benchmark_data["scores"]        # (N,)
      scores_r = reference_benchmark_data["scores"]  # (M,)
      if len(scores_b) < 5 or len(scores_r) < 5:
          return None
      s_index = constat.compute_s_index(scores_b, scores_r)
      return float(s_index)
  except ImportError:
      # ConStat not available: fallback to normalized mean difference
      mu_b = np.mean(benchmark_data["scores"])
      mu_r = np.mean(reference_benchmark_data["scores"])
      std_r = np.std(reference_benchmark_data["scores"]) + 1e-9
      return float((mu_b - mu_r) / std_r)
  except Exception:
      return None
```

### Subtask: L-A2-3 — compute_hd_tabular with Block Bootstrap

**Parent Epic**: A-2 (Signal Computation, complexity 15)

```
compute_hd_tabular(rankings_over_time, n_bootstrap=1000, seed=42):
  T, N = rankings_over_time.shape  # (T time steps, N models)
  block_size = max(1, T // 4)
  rng = np.random.default_rng(seed)
  tau_samples = []
  for _ in range(n_bootstrap):
      # Block bootstrap: sample contiguous blocks to preserve autocorrelation
      n_blocks = max(1, T // block_size)
      starts = rng.integers(0, T - block_size + 1, size=n_blocks)
      indices = np.concatenate([np.arange(s, s + block_size) for s in starts])[:T]
      boot = rankings_over_time[indices]  # (T, N)
      # Compute mean Kendall tau across consecutive pairs
      taus = []
      for t in range(len(boot) - 1):
          tau, _ = scipy.stats.kendalltau(boot[t], boot[t+1])
          taus.append(tau)
      tau_samples.append(np.mean(taus) if taus else 0.0)
  return float(np.mean(tau_samples))
```

---

## Module: baseline.py

### API Signatures

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

def extract_naive_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Extract naive features: score_mean, score_std, score_trend, n_models per benchmark."""
    # Returns: DataFrame[benchmark, label, score_mean, score_std, score_trend, n_models]
    ...

def fit_baseline(
    X_train: np.ndarray,    # (N_benchmarks, n_features)
    y_train: np.ndarray,    # (N_benchmarks,) binary: 1=saturated, 0=healthy
) -> LogisticRegression:
    """Fit logistic regression with balanced class weights."""
    ...

def predict_baseline(
    model: LogisticRegression,
    X: np.ndarray,           # (N_benchmarks, n_features)
) -> np.ndarray:             # (N_benchmarks,) probabilities for class=1
    """Return predicted probabilities for saturated class."""
    ...
```

---

## Module: evaluate.py

### API Signatures

```python
import numpy as np
import pandas as pd
from typing import Optional
from scipy import stats

def test_discriminability(
    saturated_signals: np.ndarray,   # (N_sat,) H_d values for saturated benchmarks
    healthy_signals: np.ndarray,     # (N_healthy,) H_d values for healthy benchmarks
) -> dict:
    """Mann-Whitney U test + Cohen's d + AUC. Returns result dict."""
    # Returns: {"u_stat": float, "p_value": float, "cohens_d": float,
    #           "auc": float, "n_sat": int, "n_healthy": int}
    ...

def evaluate_domain(
    domain_signals: pd.DataFrame,    # DataFrame[benchmark, label, hd_signal, domain]
    baseline_probs: np.ndarray,      # (N_benchmarks,) from predict_baseline
    domain: str,                     # "cv" | "nlp" | "tabular"
) -> dict:
    """Full domain evaluation: discriminability + baseline comparison."""
    # Returns: {"domain": str, "discriminability": dict, "baseline_auc": float,
    #           "signal_auc": float, "passes_gate": bool}
    ...

def verify_mechanism_activated(
    domain_results: dict,            # {domain: evaluate_domain result}
) -> tuple[bool, dict]:
    """Check 4 indicators per domain: p<0.05, d>0.5, signal_auc>0.65, n>=15."""
    # Returns: (all_activated: bool, indicators: {domain: {indicator: bool}})
    ...

def check_gate_condition(
    domain_results: dict,            # {domain: evaluate_domain result}
) -> tuple[bool, dict]:
    """PASS if Mann-Whitney p<0.05 AND Cohen's d>0.5 in >=2 of 3 domains."""
    # Returns: (passed: bool, gate_details: {domain: {"p_value", "cohens_d", "passes"}})
    ...

def run_temporal_test(
    panel: pd.DataFrame,
    domain: str,
    lookbacks: list[int],            # e.g. [6, 12, 18, 24] months
) -> dict:
    """Test discriminability at multiple lookback horizons."""
    # Returns: {lookback: test_discriminability result}
    ...

def save_results(
    results: dict,
    output_path: str,
) -> None:
    """Save results dict as JSON to output_path."""
    ...
```

### Subtask: L-A4-1 — test_discriminability (Mann-Whitney U, AUC, Cohen's d)

**Parent Epic**: A-4 (Evaluation + Gate, complexity 14)

```
test_discriminability(saturated_signals, healthy_signals):
  n_sat = len(saturated_signals)
  n_healthy = len(healthy_signals)

  # Mann-Whitney U
  u_stat, p_value = scipy.stats.mannwhitneyu(
      saturated_signals, healthy_signals, alternative="two-sided")

  # AUC from U statistic: AUC = U / (n_sat * n_healthy)
  auc = u_stat / (n_sat * n_healthy)

  # Cohen's d with pooled standard deviation
  mean_diff = np.mean(saturated_signals) - np.mean(healthy_signals)
  pooled_std = np.sqrt(
      ((n_sat - 1) * np.var(saturated_signals, ddof=1) +
       (n_healthy - 1) * np.var(healthy_signals, ddof=1))
      / (n_sat + n_healthy - 2)
  )
  cohens_d = mean_diff / (pooled_std + 1e-9)

  return {
      "u_stat": float(u_stat), "p_value": float(p_value),
      "cohens_d": float(cohens_d), "auc": float(auc),
      "n_sat": n_sat, "n_healthy": n_healthy
  }
```

### Subtask: L-A4-2 — verify_mechanism_activated (4 indicators per domain)

**Parent Epic**: A-4 (Evaluation + Gate, complexity 14)

```
verify_mechanism_activated(domain_results):
  indicators = {}
  all_activated = True
  for domain, res in domain_results.items():
      disc = res["discriminability"]
      ind = {
          "p_lt_005":     disc["p_value"] < 0.05,
          "d_gt_05":      abs(disc["cohens_d"]) > 0.5,
          "auc_gt_065":   disc["auc"] > 0.65,
          "n_sufficient": disc["n_sat"] >= 15 and disc["n_healthy"] >= 15,
      }
      indicators[domain] = ind
      if not all(ind.values()):
          all_activated = False
  return (all_activated, indicators)
```

### Subtask: L-A4-3 — check_gate_condition (>=2/3 domains pass)

**Parent Epic**: A-4 (Evaluation + Gate, complexity 14)

```
check_gate_condition(domain_results):
  gate_details = {}
  n_passing = 0
  for domain, res in domain_results.items():
      disc = res["discriminability"]
      passes = disc["p_value"] < 0.05 and abs(disc["cohens_d"]) > 0.5
      gate_details[domain] = {
          "p_value":  disc["p_value"],
          "cohens_d": disc["cohens_d"],
          "passes":   passes,
      }
      if passes:
          n_passing += 1
  passed = n_passing >= 2
  gate_details["summary"] = {"n_passing": n_passing, "threshold": 2, "passed": passed}
  return (passed, gate_details)
```

---

## Module: visualize.py

### API Signatures

```python
import matplotlib.pyplot as plt
from typing import dict as Dict

def plot_gate_metrics(
    domain_results: dict,     # {domain: evaluate_domain result}
    output_dir: str,
) -> None:
    """Bar chart: p-value and Cohen's d per domain with gate threshold lines."""
    ...

def plot_signal_boxplots(
    domain_signals: dict,     # {domain: DataFrame[benchmark, label, hd_signal]}
    output_dir: str,
) -> None:
    """Box plots: H_d signal distributions for saturated vs. healthy per domain."""
    ...

def plot_roc_curves(
    domain_results: dict,     # {domain: evaluate_domain result with roc data}
    output_dir: str,
) -> None:
    """ROC curves for signal vs. baseline per domain."""
    ...

def plot_temporal_separation(
    temporal_results: dict,   # {domain: {lookback: test_discriminability result}}
    output_dir: str,
) -> None:
    """Line plot: AUC / Cohen's d vs. lookback horizon per domain."""
    ...

def plot_scatter_saturation(
    domain_signals: dict,     # {domain: DataFrame[benchmark, label, hd_signal]}
    output_dir: str,
) -> None:
    """Scatter: H_d signal vs. Kendall tau, colored by label."""
    ...

def generate_all_figures(
    domain_results: dict,
    domain_signals: dict,
    temporal_results: dict,
    output_dir: str,
) -> None:
    """Call all plot_* functions. Save PNGs to output_dir."""
    ...
```

---

## Module: run_experiment.py

### API Signatures

```python
import argparse
from typing import Optional

CONFIG = {
    "lookback_months": 24,
    "min_saturated": 15,
    "min_healthy": 15,
    "n_bootstrap": 1000,
    "bootstrap_seed": 42,
    "tau_saturated_threshold": 0.90,
    "tau_healthy_threshold": 0.70,
    "consecutive_quarters": 2,
    "gate_p_threshold": 0.05,
    "gate_d_threshold": 0.5,
    "gate_min_domains": 2,
    "temporal_lookbacks": [6, 12, 18, 24],
    "domains": ["cv", "nlp", "tabular"],
    "output_dir": "results/h-e1/",
}

def main(args: Optional[list[str]] = None) -> None:
    """Orchestrate full H-E1 experiment pipeline."""
    # 1. parse args (override CONFIG via CLI)
    # 2. load_pwc_panel() + load_openml_panel()
    # 3. label_saturation(panel) for each source
    # 4. for each domain: compute_domain_signals()
    # 5. fit_baseline + predict_baseline per domain
    # 6. evaluate_domain() per domain
    # 7. run_temporal_test() per domain
    # 8. verify_mechanism_activated(domain_results)
    # 9. check_gate_condition(domain_results)
    # 10. generate_all_figures()
    # 11. save_results(results, CONFIG["output_dir"] + "results.json")
    # 12. print gate verdict: PASS / FAIL
    ...
```

---

## Subtask Summary

| ID | Title | Parent Epic | Complexity |
|----|-------|-------------|------------|
| L-A1-1 | Load PWC + OpenML Panels with filtering | A-1 (Data Pipeline, 13) | Medium |
| L-A1-2 | Saturation labeling via Kendall tau consecutive quarters | A-1 (Data Pipeline, 13) | Medium |
| L-A2-1 | compute_hd_cv with OOD fallback to score variance proxy | A-2 (Signal Computation, 15) | Medium |
| L-A2-2 | compute_hd_nlp with ConStat integration + None fallback | A-2 (Signal Computation, 15) | High |
| L-A2-3 | compute_hd_tabular with block bootstrap (block_size=T//4) | A-2 (Signal Computation, 15) | High |
| L-A4-1 | test_discriminability: Mann-Whitney U, AUC=U/(n*m), Cohen's d pooled | A-4 (Evaluation+Gate, 14) | Medium |
| L-A4-2 | verify_mechanism_activated: 4 indicators per domain | A-4 (Evaluation+Gate, 14) | Low |
| L-A4-3 | check_gate_condition: p<0.05 AND d>0.5 in >=2/3 domains | A-4 (Evaluation+Gate, 14) | Low |

**Total: 8 subtasks [8/8 budget used]**
