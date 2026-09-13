# Phase 2B: Verification Plan
# H-M1-v2 — Language-Adaptive Perplexity Threshold Equity
# Generated: 2026-07-30

---

## Main Hypothesis

**ID:** H-M1-v2
**Title:** Language-Adaptive Perplexity Threshold Equity

**Statement:**
Under the RedPajama-V2 CommonCrawl quality signal metadata (208,263-document sample,
5 languages: en/de/fr/es/it), if per-language k-th percentile thresholding is applied
to pre-computed ccnet_perplexity scores (instead of global k-th percentile), then
language-group retention disparity (Cramér's V) is reduced by ΔCramér's V ≥ 0.10
for ≥3 of 5 k values ∈ {10, 20, 30, 40, 50}, and max–min per-language retention gap
is reduced by ≥15 percentage points at k=30, because global thresholding introduces
spurious language-retention association due to cross-language scale and shape
heterogeneity in CCNet perplexity distributions.

**Established baseline (h-m1, no re-verification needed):**
- Global threshold: Cramér's V = 0.29–0.41, Holm p ≈ 0 for all 5 τ values
- English retention: 3.7%–36.5% (most excluded); Italian: 18.2%–88.1% (least excluded)
- Dataset: 208,263-row RedPajama-V2 sample, 5 languages

---

## Sub-Hypothesis Inventory

### h-e1 — Existence Baseline (MUST_WORK)
**Status:** READY
**Prerequisites:** none

**Statement:**
Global k-th percentile thresholding on RedPajama-V2 ccnet_perplexity produces
statistically significant language-group retention disparity (Cramér's V = 0.29–0.41,
Holm p ≈ 0 for all 5 k values).

**Rationale:** Already confirmed by h-m1. This sub-hypothesis serves as a data-loading
checkpoint and baseline reconfirmation before running new experimental conditions.

**Success criterion:** Load 208,263-row dataset; reproduce V ∈ [0.29, 0.41] for
k ∈ {10,20,30,40,50} using global percentile threshold.

**Failure criterion (gate violation):** V < 0.10 or data fails to load — indicates
dataset or pipeline regression; block all downstream hypotheses.

---

### h-m1 — Core Mechanism: Per-Language Percentile (MUST_WORK)
**Status:** NOT_STARTED
**Prerequisites:** [h-e1]

**Statement:**
Per-language k-th percentile thresholding reduces language-group retention disparity
(Cramér's V) by ΔV ≥ 0.10 for ≥3 of 5 k values ∈ {10,20,30,40,50}, with bootstrap
95% CI excluding zero, relative to global k-th percentile baseline.

**Rationale:** Primary experiment. Tests P1 prediction. Per-language calibration
compares each document to its within-language distribution, removing the cross-language
scale+shape confound and equalizing selection probability.

**Implementation:**
```python
# Per-language percentile threshold
thresholds = df.groupby('language')['ccnet_perplexity'].quantile(k/100)
retained = df.apply(lambda r: r['ccnet_perplexity'] < thresholds[r['language']], axis=1)
```

**Success criterion (P1):**
- ΔV = V(global_k) - V(per_lang_k) ≥ 0.10 for ≥3/5 k values
- Bootstrap 95% CI lower bound > 0 for those k values
- V(per_lang) ≤ 0.10 for ≥2/5 k values

**Failure criterion:** ΔV < 0.05 across all k values OR CI includes 0 for ≥3/5 k →
threshold calibration is NOT the primary driver; route to Phase 0.

**Statistical validation:**
- Bootstrap: 1000 resamples of 208,263-row DataFrame (document-level)
- Permutation control: 1000 language-label randomizations → V → 0

---

### h-c1 — CCNet Tercile Negative Control (SHOULD_WORK)
**Status:** NOT_STARTED
**Prerequisites:** [h-e1]

**Statement:**
CCNet-consistent per-language tercile thresholding (negative control) yields
Cramér's V < 0.10 on RedPajama-V2 ccnet_perplexity, confirming that the
global-threshold artifact—not upstream LID/dedup pipeline factors—is the primary
source of language-group retention disparity.

**Rationale:** If per-language tercile (the CCNet-original design) yields V ≈ 0,
the global-threshold artifact hypothesis is confirmed. If V > 0.10 under tercile,
upstream factors (LID confidence, dedup asymmetries) co-contribute.

**Implementation:**
```python
# CCNet-consistent per-language tercile (retain bottom third)
thresholds_tercile = df.groupby('language')['ccnet_perplexity'].quantile(1/3)
retained_tercile = df.apply(
    lambda r: r['ccnet_perplexity'] < thresholds_tercile[r['language']], axis=1
)
```

**Success criterion:** V < 0.10 under per-language tercile (artifact confirmed).

**Failure criterion (SHOULD_WORK — non-blocking):** V ≥ 0.10 → upstream factors
co-contribute; document as limitation, do not block Phase 5.

---

### h-m2 — Shape vs. Scale Disambiguation (SHOULD_WORK)
**Status:** NOT_STARTED
**Prerequisites:** [h-m1]

**Statement:**
Per-language percentile calibration reduces Cramér's V more than iso-retention
z-score normalization (|ΔV_percentile - ΔV_zscore| > 0.02 for ≥2 of 5 k values),
confirming that cross-language distributional shape differences—beyond mere scale
differences—contribute to retention disparity.

**Rationale:** Iso-retention z-score retains documents with lowest within-language
standardized perplexity at a rate matching the global-k retention rate. If this
produces similar ΔV as percentile, the bias is purely scale-driven. If percentile
outperforms z-score, shape heterogeneity (skewness, kurtosis) is a distinct confound.

**Implementation:**
```python
# Iso-retention z-score: match global-k retain rate
global_retain_rate = (global_retained.sum()) / len(df)
df['z_score'] = df.groupby('language')['ccnet_perplexity'].transform(
    lambda x: (x - x.mean()) / x.std()
)
z_threshold = df['z_score'].quantile(global_retain_rate)
retained_zscore = df['z_score'] < z_threshold
```

**Pre-registration:** If kurtosis > 10 for any language, flag z-score condition
as potentially unreliable for that language.

**Success criterion (P3):** |ΔV_pct - ΔV_zscore| > 0.02 for ≥2/5 k values.

**Failure criterion (SHOULD_WORK — non-blocking):** |ΔV_pct - ΔV_zscore| ≤ 0.02
across all k → bias is pure scale artifact; update mechanism claim in paper.

---

### h-c2 — Practical Effect at k=30 (MUST_WORK)
**Status:** NOT_STARTED
**Prerequisites:** [h-m1]

**Statement:**
Per-language k-th percentile thresholding at k=30 reduces the max–min per-language
retention gap by ≥15 percentage points relative to global k=30 baseline
(established baseline: English 36.5%, Italian 88.1%, gap ≈ 51.6pp).

**Rationale:** Translates statistical significance (h-m1 Cramér's V) into operational
terms. A ≥15pp gap reduction at k=30 demonstrates the fix is meaningful for
multilingual corpus curation practitioners.

**Implementation:** Derived directly from h-m1 run at k=30.
```python
# At k=30, compute per-language retention rates under per-language percentile
retention_rates_perlang = (
    df[retained_perlang_k30].groupby('language').size() /
    df.groupby('language').size()
)
gap_reduction = (
    (global_k30_rates.max() - global_k30_rates.min()) -
    (retention_rates_perlang.max() - retention_rates_perlang.min())
)
```

**Success criterion (P2):** gap_reduction ≥ 15pp at k=30; English retention rises
from 36.5% baseline toward ≥50%.

**Failure criterion (gate violation):** gap_reduction < 10pp → practical effect
insufficient; blocks contribution framing as "actionable fix".

---

## Dependency Graph (DAG)

```
h-e1 (MUST_WORK, READY)
  ├── h-m1 (MUST_WORK)          ← critical path
  │     ├── h-m2 (SHOULD_WORK)  ← parallel after h-m1
  │     └── h-c2 (MUST_WORK)    ← parallel after h-m1, derived from h-m1 k=30 run
  └── h-c1 (SHOULD_WORK)        ← parallel with h-m1 after h-e1
```

**Critical path:** h-e1 → h-m1 → h-c2

**Parallelism:** h-c1 with h-m1; h-m2 with h-c2 after h-m1.

---

## Risk Register

| Sub-H | Risk | Severity | Mitigation |
|-------|------|----------|------------|
| h-e1 | Dataset cache missing or corrupted | LOW | Re-download from HuggingFace if needed |
| h-m1 | ΔV < 0.05 (null result) | MEDIUM | Pre-registered falsification criteria; route to Phase 0 if fails |
| h-m1 | Bootstrap CI includes 0 for ≥3/5 k | MEDIUM | 208,263 rows = high power; permutation backup |
| h-c1 | V ≥ 0.10 under tercile (upstream confounds) | MEDIUM | SHOULD_WORK gate: non-blocking; document limitation |
| h-m2 | z-score undefined (kurtosis > 10) | MEDIUM | Pre-register check; caveat z-score arm if violated |
| h-m2 | |ΔV_pct - ΔV_zscore| ≤ 0.02 (scale-only) | LOW | Valid negative result; update mechanism claim |
| h-c2 | Gap reduction < 15pp at k=30 | LOW | Statistical significance (h-m1) still publishable |

---

## Experimental Setup

**Dataset:** RedPajama-Data-V2, `togethercomputer/RedPajama-Data-V2`, name=`sample`
- 208,263 documents; 5 languages: en, de, fr, es, it
- Key field: `ccnet_perplexity`, `language`
- Cache: `docs/youra_research/` (existing h-m1 Parquet)

**Compute:** CPU-only, ~150 lines pandas/scipy, <5 min execution

**Dependencies:** pandas, scipy, numpy (all already installed for h-m1)

**Conditions (k ∈ {10, 20, 30, 40, 50}):**
1. `global_percentile`: df['ccnet_perplexity'] < df['ccnet_perplexity'].quantile(k/100)
2. `per_lang_percentile`: groupby language → within-language k-th percentile
3. `iso_retention_zscore`: per-language z-score, threshold matching global retain rate
4. `ccnet_tercile`: per-language 1/3 percentile (negative control)

**Metrics per condition × k:**
- Cramér's V (primary): scipy.stats.contingency.association on 5×2 contingency table
- ΔCramér's V: V(global_k) - V(condition_k), bootstrap 1000 resamples
- Max–min retention gap: max(retention_rate_l) - min(retention_rate_l)
- 90th-pct retained PPL per language (quality proxy)
- Skewness, kurtosis, dip test per language (distributional diagnostics, pre-registered)
- Mantel-Haenszel length-stratified Cramér's V (doc-length confound control)

---

## Success/Failure Summary

| Prediction | Criterion | Gate | Blocks |
|-----------|-----------|------|--------|
| P1 (h-m1) | ΔV ≥ 0.10 for ≥3/5 k, CI_lower > 0 | MUST_WORK | Phase 5 if fails |
| P2 (h-c2) | Gap reduction ≥15pp at k=30 | MUST_WORK | Contribution framing |
| P3 (h-m2) | \|ΔV_pct - ΔV_zscore\| > 0.02 for ≥2/5 k | SHOULD_WORK | Non-blocking |
| NC (h-c1) | V < 0.10 under per-lang tercile | SHOULD_WORK | Non-blocking |
| Quality | 90th-pct PPL increase ≤10% per language | Advisory | Non-blocking |
| Permutation | V → 0 under randomized labels | Validation | Non-blocking |
