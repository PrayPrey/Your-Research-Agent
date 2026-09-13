# Experiment Design: H-M2

**Date:** 2026-05-19
**Author:** Anonymous
**Hypothesis Statement:** Under benchmarks showing score compression (H-M1 confirmed), if compression is present, then domain-specific degradation signals — robustness gap widening (CV), contamination probability increase (NLP), premature rank correlation stabilization (tabular) — will emerge significantly earlier than discriminative collapse, providing measurable t-24 month leading indicators.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 COMPLETED (MUST_WORK PASS — Granger p=1.854e-05 at lag=2; 389 compression events across 145 benchmarks)
**Gate Status:** SHOULD_WORK — fail narrows prospective claim; does not block H-M3

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM (Causal Step 2)
- **Prerequisites:** H-M1 (COMPLETED ✅)

### Gate Condition
**SHOULD_WORK** — Primary: H_d signals emerge ≥12 months before collapse in ≥60% of confirmed compression events. Secondary: H_d magnitude significantly higher in compressed vs. non-compressed benchmarks (Mann-Whitney U p<0.05). **Failure response:** Document as limitation (signals concurrent not leading); retain H-M3/M4 as separate testable claims.

---

## Continuation Context

This is a **continuation experiment** building directly on H-M1 validated infrastructure.

### Previous Hypothesis Results (H-M1)
- **Dataset reused:** Papers With Code Leaderboard Panel (pwc-archive/evaluation-tables HuggingFace)
- **Panel constructed:** 6,938 rows across 466 benchmarks (2018–2025, quarterly)
- **Compression events confirmed:** 389 events across 145 qualifying benchmarks (31.1% compression rate)
- **σ_measurement median:** 0.3323 across 7,592 benchmarks
- **Code location:** `h-m1/code/` — data loading, panel construction, compression detection reused directly
- **Key reuse:** `compression_mask` per benchmark per quarter is the INPUT independent variable for H-M2

**Controlled comparison design:** Same dataset, same panel, only the analysis changes from compression-detection (H-M1) to signal-timing measurement (H-M2).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Temporal onset analysis signal emergence benchmark**
- No domain-specific matches found (Archon KB contains diffusion model content only)
- Consistent with H-E1 and H-M1 findings — novel research topic not yet in KB
- **Implication:** Experiment design relies on Exa/lifelines documentation and direct code reuse from H-M1

**Query 2: Survival analysis event timing lead indicator**
- No domain-specific matches found
- Same novel topic gap

**Query 3: Benchmark saturation degradation signal panel data**
- No domain-specific matches found

**Archon Code Examples**
- No relevant code examples found (all results: diffusion model pipelines)
- **Fallback:** lifelines library documentation + evaleval/benchmark-saturation GitHub repo as primary implementation references

### Exa GitHub Implementations

**Query 1: Temporal signal onset event timing — IoT/time-series anomaly detection**

**Repository 1: dongbeank/TSRBench** (⭐ N/A — specialized)
- **URL:** https://github.com/dongbeank/TSRBench
- **Relevance:** Event-level temporal analysis patterns; onset response time measurement methodology
- **Key Pattern:** Temporal event detection with onset timing metrics using pandas DataFrames
- **Architecture:** `corrupt()` method on pandas DataFrames; onset detection via SPOT algorithm
- **Used for:** Onset timing measurement design; temporal ordering logic

**Repository 2: sintel-dev/Orion** (benchmarking pipeline)
- **URL:** https://github.com/sintel-dev/Orion/blob/master/BENCHMARK.md
- **Relevance:** Pipeline ranking + temporal score tracking per signal/dataset
- **Key Pattern:** `pandas.DataFrame` with `[pipeline, rank, accuracy, elapsed, f1, precision, recall]` per signal
- **Used for:** Result DataFrame schema for temporal signal comparison

**Repository 3: evaleval/benchmark-saturation** (⭐ 2, directly relevant)
- **URL:** https://github.com/evaleval/benchmark-saturation
- **Relevance:** DIRECTLY relevant — benchmark saturation research, same domain
- **Architecture:** Python (81.8%), covers benchmark complexity characterization over time
- **Topics:** ai-evaluation, benchmark-saturation, benchmarking, evaluation-metrics
- **Used for:** Domain-specific signal computation patterns; saturation detection methodology

**Query 2: Survival analysis + lifelines for temporal event ordering**

**Repository 4: lifelines v0.30.3 (official)**
- **URL:** https://lifelines.readthedocs.io/en/stable/
- **Relevance:** PRIMARY — KaplanMeierFitter for lead time distribution; datetimes_to_durations for temporal alignment
- **Key Code:**
  ```python
  from lifelines import KaplanMeierFitter
  from lifelines.utils import datetimes_to_durations
  
  T, E = datetimes_to_durations(signal_onset_dates, collapse_dates, freq='M')
  kmf = KaplanMeierFitter()
  kmf.fit(T, event_observed=E)
  # median_lead_time = kmf.median_survival_time_
  ```
- **Training Config:** N/A (statistical analysis, not ML training)
- **Used for:** Lead time distribution; survival-style event timing analysis

**Query 3: PWC archive + benchmark saturation data**

**Repository 5: evaleval/benchmark-saturation** (confirmed above)
- **Additional reference:** Polo et al. arXiv:2602.16763 — S_index and benchmark plateau analysis
- **Repository 6: paperswithcode/paperswithcode-data**
  - **URL:** https://github.com/paperswithcode/paperswithcode-data
  - **Loading:** `load_dataset("pwc-archive/evaluation-tables")` (HuggingFace parquet)
  - **Used for:** Data loading — reuse from H-M1

**Serena Analysis Needed:** false

### 🎯 Implementation Priority Assessment

This is **NOT a paper reproduction experiment** — it is an original statistical analysis pipeline. No single "official implementation" to reproduce.

**Recommended Implementation Path:**
- Primary: Direct reuse of `h-m1/code/` data pipeline + new temporal onset analysis module
- Fallback: lifelines `datetimes_to_durations` + `KaplanMeierFitter` for event timing
- Justification: H-M1 panel construction code is already validated; H-M2 adds temporal ordering analysis layer on top of existing `compression_mask` outputs

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear; h-m1/code/ provides reusable data loading pipeline. The statistical analysis (pandas temporal joins, scipy Mann-Whitney U, lifelines KM) requires no semantic code analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset: Papers With Code Leaderboard Panel (Continuation from H-M1)**
- **Name:** Papers With Code Leaderboard Panel + OpenML Benchmark Panel
- **Type:** programmatic-api (real leaderboard data via HuggingFace archive)
- **Source:** `pwc-archive/evaluation-tables` (HuggingFace); OpenML Python client
- **Version:** Archive snapshot (last push: 2025-09-08)
- **Scope:** CV + NLP benchmarks (Papers With Code), tabular benchmarks (OpenML)
- **Time coverage:** 2018–2025 (quarterly panel)
- **Pre-filtered from H-M1:** 145 benchmarks with confirmed score compression events (389 events)
- **Additional filtering for H-M2:** Benchmarks must have documented collapse events (Kendall τ > 0.90) for temporal comparison — estimated 40–60 confirmed events from MMLU, SQuAD, CIFAR-10, GLUE subtasks, ImageNet

**Statistics (from H-M1 panel):**
- Total panel rows: 6,938 (benchmark × quarter)
- Total benchmarks with compression: 145
- Collapse events required: ≥20 (A1 risk threshold); target: 40–60
- Domain breakdown: CV (robustness gap signal), NLP (contamination probability via ConStat), Tabular (block-bootstrapped Kendall τ)

**H_d Signal Definitions (per domain):**
- **CV:** Robustness gap = mean score(top-k, corrupted set) − mean score(top-k, clean set) [widening = degradation]
- **NLP:** Contamination probability increase = ConStat estimated P(contamination) at quarter t vs. baseline t₀
- **Tabular:** Block-bootstrapped Kendall τ premature stabilization = τ exceeds 0.90 threshold before collapse event

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets (reuse from H-M1)
- Identifier: `"pwc-archive/evaluation-tables"`
- Code:
  ```python
  from datasets import load_dataset
  ds = load_dataset("pwc-archive/evaluation-tables")
  # Then apply H-M1 panel construction from h-m1/code/build_panel.py
  # Filter: compression_events_df = panel[panel['compression_flag'] == True]
  ```

### Models

#### Baseline Model

**Statistical Baseline: Concurrent Signal Descriptor (null model)**
- **Architecture:** Direct correlation of H_d signal magnitude with collapse label at same time point t (no lead time)
- **Purpose:** Tests whether signals are merely concurrent with collapse rather than leading it
- **Operationalization:** AUC of H_d(B, t) predicting collapse at time t (concurrent measurement)
- **Loading:** Pure scipy/pandas — no pretrained model

**Loading Information** (for Phase 4):
- Method: scipy.stats + pandas
- Identifier: N/A (custom statistical computation)
- Code:
  ```python
  from scipy.stats import mannwhitneyu
  from sklearn.metrics import roc_auc_score
  # Baseline: AUC of H_d at time t (concurrent)
  auc_concurrent = roc_auc_score(collapse_labels, hd_signals_at_t)
  ```

#### Proposed Model

**Architecture:** Temporal Lead Analysis — H_d(B, t-24mo) predicting collapse at t

**Core Mechanism Implementation:**

```python
# Core Mechanism: Domain-Specific Degradation Signal Lead Time Analysis
# Based on: H-M1 compression_mask output + lifelines datetimes_to_durations
# Source: h-m1/code/build_panel.py (data) + lifelines v0.30.3 (timing)

def compute_signal_onset_times(panel_df, domain, compression_mask):
    """
    For each compressed benchmark, find first quarter when H_d signal
    exceeds domain-specific threshold (signal_onset).
    Args:
        panel_df: (N_benchmarks × N_quarters) with H_d values per domain
        domain: 'cv' | 'nlp' | 'tabular'
        compression_mask: boolean Series (from H-M1) per benchmark
    Returns:
        onset_df: DataFrame with [benchmark_id, signal_onset_quarter, collapse_quarter]
    """
    compressed = panel_df[compression_mask]
    onset_records = []
    for bm_id, bm_data in compressed.groupby('benchmark_id'):
        hd_series = bm_data[f'hd_{domain}'].sort_values('quarter')
        collapse_q = bm_data[bm_data['collapse_flag']]['quarter'].min()
        if pd.isna(collapse_q):
            continue  # no collapse observed — censored
        # Signal onset: first quarter H_d exceeds domain threshold
        threshold = DOMAIN_THRESHOLDS[domain]  # pre-specified from H-E1
        onset_q = hd_series[hd_series > threshold].index.min()
        lead_months = (collapse_q - onset_q).days / 30 if not pd.isna(onset_q) else None
        onset_records.append({'benchmark_id': bm_id, 'lead_months': lead_months,
                               'onset_observed': not pd.isna(onset_q)})
    return pd.DataFrame(onset_records)

def run_temporal_ordering_test(onset_df, min_lead_months=12):
    """
    Primary test: what fraction of benchmarks show H_d onset ≥12mo before collapse?
    Returns fraction_leading and KM lead time distribution.
    """
    from lifelines import KaplanMeierFitter
    from lifelines.utils import datetimes_to_durations
    T = onset_df['lead_months'].fillna(0)
    E = onset_df['onset_observed'].astype(int)
    kmf = KaplanMeierFitter()
    kmf.fit(T, event_observed=E)
    fraction_leading = (onset_df['lead_months'] >= min_lead_months).mean()
    return fraction_leading, kmf
```

### Training Protocol

**Note:** This is a statistical analysis pipeline — no ML training. "Protocol" = data processing + statistical test sequence.

**From H-M1 (reused for controlled comparison):**
- **Panel construction:** Reuse `h-m1/code/build_panel.py` — benchmark × quarter panel, 2018–2025
- **Compression mask:** Reuse `h-m1/code/detect_compression.py` output — 145 benchmarks, 389 events

**H-M2 Specific Protocol:**
- **Step 1:** Filter panel to benchmarks with confirmed compression (H-M1 output)
- **Step 2:** Compute H_d signals at t-24mo, t-12mo, and t for each domain
  - CV: robustness gap (score on corrupted test − score on clean test, rolling 4-quarter window)
  - NLP: ConStat contamination probability (existing ConStat API call; validated in H-E1)
  - Tabular: Block-bootstrapped Kendall τ (reuse H-E1 implementation)
- **Step 3:** Identify collapse events (Kendall τ > 0.90 for ≥2 consecutive quarters)
- **Step 4:** For each benchmark × domain, compute lead time = collapse_quarter − signal_onset_quarter
- **Step 5:** Primary statistical tests (see Evaluation below)
- **Seeds:** 1 (fixed; block-bootstrap uses seed=42)
- **Statistical significance:** α = 0.05 (pre-registered)

**Dependencies:**
```
lifelines==0.30.x        # Kaplan-Meier, datetimes_to_durations
scipy>=1.10              # mannwhitneyu, spearmanr
pandas>=2.0              # temporal joins, groupby
numpy>=1.24              # array ops
datasets>=2.0            # HuggingFace data loading (reuse H-M1)
```

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold | Gate |
|--------|-----------|-------------------|------|
| `fraction_leading` | % benchmarks where H_d onset ≥12mo before collapse | ≥ 0.60 | Primary SHOULD_WORK |
| `mw_p_value` | Mann-Whitney U p-value: H_d magnitude in compressed vs. non-compressed | < 0.05 | Secondary |
| `auc_lead` | AUC of H_d(B, t-24mo) predicting collapse label | > 0.65 | Supporting |
| `auc_concurrent` | AUC of H_d(B, t) predicting collapse label | Baseline comparison | Context |

**Success Criteria:**
```
PRIMARY (SHOULD_WORK gate):
  fraction_leading >= 0.60 in at least 2 of 3 domains
  → H_d signals are LEADING indicators (not concurrent)

SECONDARY:
  mw_p_value < 0.05 (H_d magnitude higher in compressed benchmarks)
  auc_lead > auc_concurrent (leading signals more discriminable than concurrent)

FAILURE RESPONSE (if primary fails):
  Document lead time distribution (median, IQR) as honest finding
  Frame as "concurrent health monitor" not "prospective predictor"
  Retain mechanistic findings; proceed to H-M3
```

**Expected Performance (from research):**
- R3 risk (critical): signals may be concurrent — tested explicitly here
- Prior literature: H-E1 showed AUC >0.70 at t-24mo → suggests leading signal exists
- H-M1 Granger causality (p=1.854e-05 at lag=2) provides causal grounding for H_d emergence

**Metrics Loading Information** (for Phase 4):
- Task Type: temporal ordering / survival analysis (not classification)
- Library: scipy.stats + lifelines + sklearn.metrics
- Code:
  ```python
  from scipy.stats import mannwhitneyu
  from lifelines import KaplanMeierFitter
  from sklearn.metrics import roc_auc_score
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart of `fraction_leading` per domain vs. 0.60 threshold

#### Additional Figures (LLM Autonomous)
The Phase 4 Coder should autonomously decide which of the following are most informative:
1. **Kaplan-Meier lead time curves** per domain (CV, NLP, Tabular) — shows distribution of H_d onset-to-collapse lead times
2. **Signal emergence timeline plot** — aligned time series showing H_d signal and collapse event timing for representative benchmarks (e.g., MMLU, CIFAR-10, SQuAD)
3. **AUC comparison bar chart** — H_d(t-24mo) vs. H_d(t-12mo) vs. H_d(t) AUC per domain (tests temporal specificity)
4. **Mann-Whitney comparison boxplot** — H_d magnitude in compressed vs. non-compressed benchmarks per domain

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H_d signals are computable for all 3 domains on H-M1 panel | TRUE — H-E1 validated signal computability; H-M1 panel already built |
| Mechanism Isolatable | Lead time analysis can be enabled/disabled via temporal offset parameter | TRUE — offset `delta_months` parameter controls t-24mo vs. t measurement |
| Baseline Measurable | Concurrent signal (H_d at t) can be measured as comparison | TRUE — same computation at t instead of t-24mo |

### Architecture Compatibility Check

**This is a statistical pipeline, not a neural architecture.** Compatibility check = data schema validation.

**Required data fields:**
- `benchmark_id` (str): unique benchmark identifier
- `quarter` (datetime): observation quarter
- `hd_cv` (float): robustness gap signal for CV benchmarks
- `hd_nlp` (float): contamination probability for NLP benchmarks
- `hd_tabular` (float): Kendall τ for tabular benchmarks
- `compression_flag` (bool): from H-M1 output
- `collapse_flag` (bool): Kendall τ > 0.90 for ≥2 consecutive quarters

**Incompatible scenarios:**
- Benchmarks with < 8 quarters of history (insufficient for t-24mo lead time analysis)
- Benchmarks without collapse events (censored — handled by KM estimator)

> ⚠️ If collapse_event_count < 20 after filtering, Phase 4 MUST trigger R1 mitigation: use τ>0.85 threshold and report as preliminary study.

---

### Mechanism Activation Indicators

**How to detect if temporal ordering mechanism is actually being measured:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Computing H_d signals at t-24mo offset for N benchmarks"` | `temporal_analysis.py:compute_signal_onset_times()` |
| Data Shape | `onset_df` shape: (N_compressed_benchmarks, 4) with columns `[benchmark_id, lead_months, onset_observed, domain]` | `temporal_analysis.py:compute_signal_onset_times()` return |
| Metric Delta | `fraction_leading` ∈ [0, 1]; KM median lead time reported in months | `evaluate.py:run_temporal_ordering_test()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(onset_df, km_results, results):
    indicators = {
        "onset_df_populated": len(onset_df) > 0,
        "collapse_events_found": onset_df['onset_observed'].sum() >= 20,
        "lead_time_computed": 'lead_months' in onset_df.columns,
        "km_fitted": km_results is not None,
        "fraction_computed": 'fraction_leading' in results
    }
    all_activated = all(indicators.values())
    return all_activated, indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No collapse events found | `onset_df['onset_observed'].sum() < 20` | Apply R1 mitigation: lower τ threshold to 0.85 |
| All lead times negative (signals AFTER collapse) | `onset_df['lead_months'].median() < 0` | SHOULD_WORK FAIL — document as concurrent signal |
| H_d signals not available for domain | `hd_{domain}` column all NaN | Skip domain, report as missing data limitation |
| Compression mask empty | `compression_mask.sum() == 0` | Critical error — H-M1 output corrupted |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (all 5 indicators) | `verify_mechanism_activated()` returns True |
| Lead Effect Measurable | `onset_df['lead_months'].median() > 0` | Positive median lead time |
| Hypothesis Supported | `fraction_leading >= 0.60` in ≥2 domains | `run_temporal_ordering_test()` output |

---

## Ablation Study Design

> **MECHANISM hypothesis** — ablation required to isolate temporal ordering effect.

### Ablation Variants

| Variant | Description | What It Measures |
|---------|-------------|-----------------|
| A1: t-24mo offset | H_d(B, t-24mo) predicting collapse | PROPOSED — 24-month lead window |
| A2: t-12mo offset | H_d(B, t-12mo) predicting collapse | 12-month lead window (shorter) |
| A3: t offset (concurrent) | H_d(B, t) predicting collapse | BASELINE — concurrent descriptor |
| A4: Compression-filtered only | Analysis restricted to H-M1 confirmed compression benchmarks | Tests whether compression is necessary condition |
| A5: All benchmarks (no compression filter) | H_d signals on ALL benchmarks | Tests whether compression filter adds specificity |

**Key ablation question:** Does filtering to H-M1 compression benchmarks (A4 vs A5) increase fraction_leading? If yes, compression is a necessary precondition for domain-specific signal emergence.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB**: No domain-specific matches found across 5 queries.
- This is consistent with H-E1 and H-M1 findings
- Novel research topic (benchmark health scoring via temporal survival analysis) not yet in Archon KB
- All Archon results returned diffusion model content (unrelated)

### B. GitHub Implementations (Exa)

**Repository 1: lifelines v0.30.3 (official documentation)**
- **URL:** https://lifelines.readthedocs.io/en/stable/
- **Query Used:** "survival analysis event timing lead time scipy lifelines Mann-Whitney temporal ordering panel data Python"
- **Relevance:** PRIMARY — complete survival analysis library for Kaplan-Meier lead time distribution
- **Key Code (annotated):**
  ```python
  from lifelines import KaplanMeierFitter
  from lifelines.utils import datetimes_to_durations
  
  # Convert calendar dates to durations (months) for survival analysis
  T, E = datetimes_to_durations(signal_onset_dates, collapse_dates, freq='M')
  # T = lead time in months; E = whether collapse was observed (1) or censored (0)
  
  kmf = KaplanMeierFitter()
  kmf.fit(T, event_observed=E)
  median_lead_time = kmf.median_survival_time_  # median lead time in months
  ```
- **Configuration Extracted:** `freq='M'` for monthly lead times; `event_observed` handles right-censoring
- **Used For:** Lead time distribution computation (Step 5 in verification protocol)

**Repository 2: evaleval/benchmark-saturation**
- **URL:** https://github.com/evaleval/benchmark-saturation
- **Query Used:** "Papers With Code benchmark saturation temporal signal emergence score compression leading indicator GitHub Python"
- **Relevance:** DIRECTLY relevant — same research domain (benchmark saturation characterization)
- **Architecture:** Python (81.8%), benchmark complexity characterization over time
- **Used For:** Domain understanding; signal computation patterns; saturation detection methodology reference

**Repository 3: paperswithcode/paperswithcode-data**
- **URL:** https://github.com/paperswithcode/paperswithcode-data
- **Relevance:** Data source documentation; loading methodology
- **Key Code:**
  ```python
  from datasets import load_dataset
  # Load evaluation tables from HuggingFace archive (REST API shut down July 2025)
  ds = load_dataset("pwc-archive/evaluation-tables")
  ```
- **Used For:** Data loading (reuse from H-M1 — already validated)

**Repository 4: TSRBench / Orion (temporal event patterns)**
- **URL:** https://github.com/dongbeank/TSRBench; https://github.com/sintel-dev/Orion
- **Relevance:** INDIRECT — onset response timing measurement patterns
- **Used For:** Onset detection design; temporal result DataFrame schema

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. The h-m1/code/ pipeline provides direct reuse, and lifelines docs provide complete API reference for survival-style event timing.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M1 (`h-m1/04_validation.md`)
- **Reused Components:**
  - Dataset: Papers With Code Leaderboard Panel — proven stable (6,938 rows, 466 benchmarks)
  - Panel construction: `h-m1/code/build_panel.py` — validated quarterly aggregation
  - Compression detection: `h-m1/code/detect_compression.py` — outputs `compression_mask` (145 benchmarks, 389 events)
  - σ_measurement: 0.3323 median — reused as compression threshold denominator
- **Why Reused:** Enables controlled experiment — only analysis layer changes (temporal ordering vs. Granger causality)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A/2B + H-M1 reuse | Section 1.3 (02b_verification_plan.md); h-m1/04_validation.md |
| Data loading code | GitHub | paperswithcode/paperswithcode-data (Exa B.3) |
| H_d signal computation | Phase 2B protocol | 02b_verification_plan.md Section 2.2 H-M2; H-E1 validated |
| Lead time computation | lifelines docs | Exa B.1 (datetimes_to_durations, KaplanMeierFitter) |
| Mann-Whitney U test | scipy docs | Standard library; confirmed working in H-E1 |
| Temporal ordering design | Phase 2B H-M2 protocol | 02b_verification_plan.md steps 1–5 |
| Ablation variants | Phase 2B + R3 risk analysis | 02b_verification_plan.md Section 4.1 Risk R3 |
| Success criteria thresholds | Phase 2B gate definition | 02b_verification_plan.md Section 3.2 (≥60% in ≥2 domains) |
| Compression filter input | H-M1 output | h-m1/04_validation.md; compression_events_df |
| Mechanism verification code | Original design | Based on lifelines API (Exa B.1) + H-M1 patterns |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-19T08:35:00Z

### Workflow History for This Hypothesis
- 2026-05-19T08:30:06Z: H-M2 set to IN_PROGRESS (Hypothesis Loop started Phase 2C → 3 → 4)
- 2026-05-19T08:35:00Z: Phase 2C experiment design started (IN_PROGRESS)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — no domain matches), Exa (GitHub — 4 repositories), Serena (skipped — code clear)*
*All specifications grounded in Phase 2B protocol + H-M1 validated infrastructure + lifelines documentation*
*Next Phase: Phase 3 - Implementation Planning*
