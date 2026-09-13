# Product Requirements Document: H-E1
# BCBHS: Domain-Specific Health Signal Discriminability (EXISTENCE PoC)

**Hypothesis ID:** H-E1
**Date:** 2026-05-19
**Author:** Anonymous
**Phase:** 3 - Implementation Planning
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)

---

## 1. Executive Summary

This experiment validates the existence of domain-specific benchmark health signals that can discriminate saturated vs. healthy ML benchmarks. For CV (robustness gap), NLP (contamination-adjusted S_index via ConStat), and tabular (block-bootstrapped Kendall τ), we test whether these signals show statistically significant differences (Mann-Whitney U p<0.05, Cohen's d>0.5) between confirmed-saturated and healthy benchmarks. This is the MUST_WORK foundation hypothesis — failure blocks the entire BCBHS pipeline (H-M1 through H-M4).

---

## 2. Problem Statement

Benchmark saturation is currently detected reactively — after community consensus forms. The BCBHS project needs domain-specific leading indicators computable from leaderboard panel data. This PoC answers: **do these signals exist and discriminate saturated from healthy benchmarks at t-24 months?**

### 2.1 Success Criteria (Gate Condition)

**PASS:** Mann-Whitney U p<0.05 AND Cohen's d>0.5 in ≥2 of 3 domains (CV, NLP, tabular)
**FAIL:** Fewer than 2 domains meet criteria → H-E1 rejected → block H-M1 through H-M4

---

## 3. Functional Requirements

### FR-1: Data Pipeline — PWC Leaderboard Panel Construction

**Source:** `pwc-archive/evaluation-tables` (HuggingFace) — PWC REST API shut down July 2025
**Filter criteria:**
- ≥20 submissions per benchmark
- ≥2 years submission history
- Known domain (CV or NLP)
- Time range: 2018–2025

**Implementation:**
```python
from datasets import load_dataset
pwc_eval = load_dataset("pwc-archive/evaluation-tables", split="train")
# Fields: task, dataset, metric, model, paper_date, score, evaluated_on
```

### FR-2: Data Pipeline — OpenML Benchmark Panel Construction

**Source:** OpenML API (`openml.study.get_suite("amlb-classification-all")` + CC18)
**Filter criteria:**
- ≥20 evaluated runs per task
- ≥2 years of submissions

**Implementation:**
```python
import openml
suite = openml.study.get_suite("amlb-classification-all")
for task_id in suite.tasks:
    evaluations = openml.evaluations.list_evaluations(
        function="predictive_accuracy", tasks=[task_id], output_format="dataframe")
```

### FR-3: Saturation Labeling

**Saturated (positive):** Kendall τ(ranking_{t-1}, ranking_t) > 0.90 for ≥2 consecutive quarters
**Healthy (negative):** Kendall τ < 0.70 at same time point t
**Excluded (ambiguous):** τ between 0.70–0.90
**Expected:** 40–60 confirmed saturation events (MMLU, SQuAD, CIFAR-10, GLUE subtasks, OpenML classic datasets)
**Minimum:** ≥50 saturated events total; ≥15 saturated + ≥15 healthy per domain

### FR-4: CV Domain Signal — Robustness Gap

Compute `H_d_cv = mean(benchmark_scores_t-24mo - held_out_scores)` per benchmark

```python
def compute_hd_cv(benchmark_scores, held_out_scores):
    return np.mean(benchmark_scores - held_out_scores)
```

**Fallback:** If OOD test variants unavailable, use score variance as CV proxy.

### FR-5: NLP Domain Signal — Contamination-Adjusted S_index

Use `eth-sri/ConStat` library:
```python
from constat import ConStat
constat = ConStat(benchmark_data, reference_benchmark_data)
result = constat.test()  # p_value, s_index
s_index = -np.log(result.p_value + 1e-10)
```

**Fallback:** If no reference benchmark, mark NLP S_index as missing for that benchmark.

### FR-6: Tabular Domain Signal — Block-Bootstrapped Kendall τ

```python
def compute_hd_tabular(rankings_over_time, n_bootstrap=1000):
    T = rankings_over_time.shape[0]
    block_size = max(1, T // 4)
    tau_samples = []
    for _ in range(n_bootstrap):
        t1 = np.random.randint(0, T - block_size)
        t2 = np.random.randint(0, T - block_size)
        tau, _ = stats.kendalltau(
            rankings_over_time[t1:t1+block_size].mean(0),
            rankings_over_time[t2:t2+block_size].mean(0))
        tau_samples.append(tau)
    return np.mean(tau_samples)
```

### FR-7: Baseline Model

**Type:** Logistic Regression on naive derived features (no domain-specific signals)
**Features:**
- `score_variance_last_4q`: Variance of scores in top-10 models over last 4 quarters
- `improvement_slope`: Linear trend of best score over time
- `benchmark_age_months`: Time since first submission

```python
from sklearn.linear_model import LogisticRegression
baseline = LogisticRegression()
baseline.fit(X_train_baseline, y_train)
```

### FR-8: Statistical Testing (Per Domain)

```python
from scipy.stats import mannwhitneyu
from sklearn.metrics import roc_auc_score

stat, p = mannwhitneyu(saturated_signals, healthy_signals, alternative='two-sided')
auc = stat / (len(saturated_signals) * len(healthy_signals))
pooled_std = np.sqrt((np.var(saturated_signals) + np.var(healthy_signals)) / 2)
cohens_d = abs(np.mean(saturated_signals) - np.mean(healthy_signals)) / pooled_std
```

### FR-9: Mechanism Activation Verification

```python
def verify_mechanism_activated(domain_results):
    indicators = {}
    for domain in ["cv", "nlp", "tabular"]:
        r = domain_results[domain]
        indicators[domain] = {
            "signals_computed": r["n_benchmarks"] >= 15,
            "groups_defined": r["n_saturated"] >= 10 and r["n_healthy"] >= 10,
            "effect_measurable": abs(r["cohens_d"]) > 0.0,
            "better_than_baseline": r["auc_hd"] > r["auc_baseline"]
        }
    return all(all(v.values()) for v in indicators.values()), indicators
```

### FR-10: Visualization

**Required (mandatory):**
- Gate Metrics Comparison: bar chart of p-value, Cohen's d, AUC per domain (target vs. actual)

**Additional (autonomous):**
- Box plots of H_d signal distributions (saturated vs. healthy) per domain
- ROC curves per domain: H_d signal vs. naive baseline
- Temporal separation plot: Cohen's d at t-6mo, t-12mo, t-18mo, t-24mo
- Scatter plot: saturation labels vs. H_d signal values per domain

**Output directory:** `h-e1/figures/`

### FR-11: Temporal Ordering Test (Secondary)

Compare signal discriminability (Cohen's d) at:
- t-24mo, t-18mo, t-12mo, t-6mo before confirmed saturation
Expected: t-24mo shows strong separation (leading indicator property)

---

## 4. Data Specification

### 4.1 Primary Datasets

| Dataset | Source | Method | Domain |
|---------|--------|--------|--------|
| PWC Evaluation Tables | `pwc-archive/evaluation-tables` (HuggingFace) | `load_dataset()` | CV + NLP |
| OpenML Benchmark Panel | OpenML API | `openml.study.get_suite()` | Tabular |

### 4.2 Minimum Sample Requirements

- Total: ≥500 benchmark-time-point observations
- Saturated events: ≥50 total; ≥15 per domain
- Healthy benchmarks: ≥15 per domain
- Filter: benchmarks with <10 unique model submissions → excluded

### 4.3 Saturation Labels

- **Source:** Kendall τ of ranking sequences (computed from panel data)
- **Positive (saturated):** τ > 0.90 for ≥2 consecutive quarters
- **Negative (healthy):** τ < 0.70
- **Excluded:** τ 0.70–0.90

### 4.4 Time Split

- **Training labels:** 2018–2022 (for baseline model fitting)
- **Test period:** 2023–2025 (prospective evaluation)

---

## 5. Non-Functional Requirements

### 5.1 Performance

- **Expected runtime:** 15–45 minutes (API data loading is bottleneck)
- **Bootstrap iterations:** 1000 (fixed, `np.random.seed(42)`)
- No GPU required — pure statistical analysis

### 5.2 Reproducibility

- Fixed seed: `np.random.seed(42)`
- All data loaded via versioned APIs/archives
- Results logged to CSV for reproducibility

### 5.3 Infrastructure (LIGHT tier — minimal)

- Config: hardcoded / argparse
- Logging: print statements + CSV output
- Testing: smoke test (run completes without error)
- No WandB, no YAML config system required

---

## 6. Success Criteria

### 6.1 MUST_WORK Gate (Primary)

| Criterion | Threshold | Domain |
|-----------|-----------|--------|
| Mann-Whitney U | p < 0.05 | ≥2/3 domains |
| Cohen's d | d > 0.5 | ≥2/3 domains |
| AUC (H_d vs baseline) | AUC > 0.70 | ≥2/3 domains |

### 6.2 Mechanism Activation (Prerequisite)

- ≥15 benchmarks per domain with H_d computed
- ≥10 saturated + ≥10 healthy per domain
- H_d AUC > baseline AUC in ≥2 domains

### 6.3 PoC Pass Condition

1. Code runs without error
2. H_d signals show p<0.05 AND Cohen's d>0.5 in ≥2 of 3 domains
3. Naive baseline does NOT meet these thresholds in ≥2 domains

---

## 7. Dependencies

### 7.1 Python Packages

```
datasets>=2.0.0          # HuggingFace datasets (PWC archive)
openml>=0.14.0           # OpenML Python API
scipy>=1.9.0             # mannwhitneyu, kendalltau
scikit-learn>=1.0.0      # LogisticRegression, roc_auc_score
numpy>=1.21.0            # Array operations
pandas>=1.3.0            # Dataframe handling
matplotlib>=3.4.0        # Visualization
seaborn>=0.11.0          # Visualization
constat                  # eth-sri/ConStat (pip install -e from GitHub)
```

### 7.2 External Repositories

| Repository | URL | Purpose |
|------------|-----|---------|
| eth-sri/ConStat | https://github.com/eth-sri/ConStat | NLP contamination-adjusted S_index |
| pwc-archive/evaluation-tables | HuggingFace dataset | PWC leaderboard panel data |
| openml/openml-python | https://github.com/openml/openml-python | OpenML tabular benchmark data |

### 7.3 Install Notes

- ConStat: `conda create -n constat python=3.10 && pip install -e . && pip install -r requirements.txt`
- No GPU required
- Single CPU sufficient

---

## 8. File Structure

```
h-e1/
├── 02c_experiment_brief.md       # Phase 2C input
├── 03_prd.md                     # This document
├── 03_architecture.md            # Phase 3 Architecture
├── 03_logic.md                   # Phase 3 Logic
├── 03_config.md                  # Phase 3 Config
├── 03_tasks.yaml                 # Phase 4 task list
├── code/
│   ├── data_pipeline.py          # FR-1, FR-2, FR-3
│   ├── signal_compute.py         # FR-4, FR-5, FR-6
│   ├── baseline.py               # FR-7
│   ├── evaluate.py               # FR-8, FR-9
│   ├── visualize.py              # FR-10
│   └── run_experiment.py         # Entry point
└── figures/
    ├── gate_metrics.png
    ├── boxplots_domain.png
    ├── roc_curves.png
    ├── temporal_separation.png
    └── scatter_saturation.png
```

---

## 9. Out of Scope

- Cox proportional hazards modeling (H-M3 scope)
- Multi-domain calibration (H-M3/H-M4 scope)
- Lead time prediction beyond signal discrimination (H-M4 scope)
- Any neural network training
- Real-time/streaming benchmark monitoring

---

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| PWC API offline (July 2025) | Use HuggingFace archive `pwc-archive/evaluation-tables` |
| Insufficient saturated benchmarks per domain (<15) | Report as low-power warning; treat as preliminary |
| ConStat reference benchmark unavailable for NLP | Mark S_index as missing; exclude that NLP benchmark |
| CV benchmarks without OOD variants | Use score variance as CV H_d proxy |
| OpenML API rate limits | Cache responses; use `output_format="dataframe"` |

---

*Generated by Phase 3 Implementation Planning (BMAD BMM unavailable — direct generation from Phase 2C brief)*
*stepsCompleted: [prd]*
