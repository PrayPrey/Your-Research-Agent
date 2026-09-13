# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-07-30T07:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1
- **Gap Title**: No Prior Direct Comparison of Global vs. Per-Language Percentile Perplexity Thresholds on Cramér's V Retention Equity
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS addressed. Pre-registered hypothesis with 4-condition experimental design, practical effect size criterion, and permutation/bootstrap validation framework.

### Key Insights

1. **The h-m1 direction inversion is mechanistically explained**: English web text has higher mean perplexity than romance language web text relative to Wikipedia-trained KenLM — not because English is lower quality, but because English web text is more domain-diverse and noisier (informal registers, code-switching) relative to what Wikipedia training examples. Global percentile threshold treats the cross-language mixture distribution as a single pool, over-excluding the high-perplexity tail (English) and under-excluding the low-perplexity range (Italian).

2. **CCNet's original design was correct**: CCNet uses per-language tercile boundaries (cutoff.csv, one row per language). The bug is in practitioner reuse of exported ccnet_perplexity scores from RedPajama-V2 Parquet with a global threshold. The h-m1 implementation did this — making it a valid baseline for our comparison.

3. **Iso-retention z-score arm enables mechanistic diagnosis**: By making the z-score condition iso-retention (same total retain rate as global k-th percentile), we can directly compare ΔV under percentile vs. z-score. If |ΔV_pct - ΔV_zscore| > 0.02, shape differences (skew/kurtosis) across language perplexity distributions are confirmed.

4. **"Distributional parity of selection" is the correct framing**: Without GPU, we cannot claim fairness of usable training signal — only that the selection process is equitable in distributional terms. This is strictly defensible.

### Breakthrough Moments

- **Exchange 4** (Prof. Rex): Resolved the strawman concern — h-m1's global threshold on exported Parquet scores IS the practitioner-reuse scenario. Comparison is valid.
- **Exchange 9** (Prof. Rex): Iso-retention z-score formulation — enables scale vs. shape disambiguation within a single experiment.
- **Exchange 12** (Prof. Rex): Practical effect size criterion (≥15pp retention gap reduction at k=30) — elevates from statistical to operational claim.
- **Exchange 14** (Prof. Vera): Length-stratified Cramér's V via Mantel-Haenszel — closes doc-length confound.

---

## Final Hypothesis

### Title
Language-Adaptive Perplexity Threshold Equity (h-m1-v2)

### Core Claim

Under the RedPajama-V2 CommonCrawl quality signal metadata (208,263-document sample, 5 languages: en/de/fr/es/it), if per-language k-th percentile thresholding is applied to pre-computed ccnet_perplexity scores (instead of global k-th percentile), then language-group retention disparity (Cramér's V) is reduced by ΔCramér's V ≥ 0.10 for ≥3 of 5 k values ∈ {10, 20, 30, 40, 50}, and max–min per-language retention gap is reduced by ≥15 percentage points at k=30, because global thresholding introduces spurious language-retention association due to cross-language scale and shape heterogeneity in CCNet perplexity distributions.

### Mechanism

Cross-language heterogeneity in ccnet_perplexity distributions — different scale AND shape, due to per-language KenLM training on Wikipedia and language-specific SentencePiece tokenization — causes global percentile thresholds to systematically over-exclude high-perplexity languages (English: 3.7%–36.5% retention) and under-exclude low-perplexity languages (Italian: 18.2%–88.1% retention). Per-language percentile calibration compares each document to its within-language distribution, removing the scale+shape confound and equalizing selection probability.

**Four-condition design:**
1. **Global k-th percentile** [baseline — h-m1 implementation, Cramér's V = 0.29–0.41]
2. **Per-language k-th percentile** [primary intervention — `df.groupby('language')['ccnet_perplexity'].transform('quantile', k/100)`]
3. **Iso-retention per-language z-score** [scale vs. shape disambiguation — retain z_l ≤ z* where z* = global k retain rate]
4. **CCNet-consistent per-language tercile** [negative control — expect V ≈ 0]

---

## Predictions

### P1 (Primary)
**Statement**: Per-language k-th percentile thresholding reduces Cramér's V by ΔV ≥ 0.10 for ≥3/5 k values, bootstrap 95% CI excluding zero.  
**Success criterion**: ΔV ≥ 0.10 AND CI_lower > 0 for ≥3/5 k; V(per_lang) ≤ 0.10 for ≥2/5 k  
**Falsification**: ΔV < 0.05 across all k, OR CI includes 0 for ≥3/5 k

### P2
**Statement**: Max–min per-language retention gap reduced by ≥15pp at k=30; English retention rises from 36.5% baseline.  
**Falsification**: Gap reduction < 10pp at k=30

### P3
**Statement**: |ΔV_percentile - ΔV_zscore| > 0.02 for ≥2/5 k values (shape effect confirmed).  
**Falsification**: |ΔV_pct - ΔV_zscore| ≤ 0.02 across all k (bias is pure scale artifact)

---

## Novelty

**What's new**: First direct measurement of language-group retention disparity (Cramér's V) when practitioners reuse CCNet-derived perplexity scores from RedPajama-V2 with global threshold; first comparison of global vs. per-language percentile thresholding for multilingual corpus equity; first mechanistic disambiguation via iso-retention z-score condition.

**Closest prior work**: Turki et al. [2026] (classifier-based retention rate tuning at DATA-FM/ICLR 2026) — our work is the perplexity-based analogue, simpler and more widely deployed.

**Generalizable principle**: Language-aware quality scores + language-agnostic thresholds → retention disparity. Extends to classifier logits, toxicity scores, or any language-specific quality metric.

---

## Experimental Design

**Dataset**: RedPajama-V2 CommonCrawl quality signals (208,263-document sample, 5 languages, Parquet)  
**Implementation**: pandas groupby + scipy.stats + custom bootstrap CI (~150 lines Python)  
**Compute**: CPU-only, static Parquet files, ~60 seconds per condition  

**Validation controls**:
- Permutation: randomize language labels → V → 0 for all methods
- CCNet-tercile: per-language tercile → V ≈ 0 (negative control)
- Distributional diagnostics: skewness, kurtosis, Hartigan's dip test per language (pre-registered)
- Length stratification: Mantel-Haenszel Cramér's V by document length decile
- Quality proxy: 90th-percentile retained PPL per language (increase ≤10% = quality preserved)

---

## Limitations

1. **Sample scope**: 208,263-document sample vs. 113.3B full RedPajama-V2 corpus — all claims scoped to sample only
2. **No downstream evaluation**: CPU constraint prevents LLM training/evaluation — testing distributional parity of selection, not quality of selected training signal
3. **Z-score breakdown**: Iso-retention z-score condition assumes finite variance; pre-register kurtosis > 10 as heavy-tail caveat condition
4. **Length confound**: Mantel-Haenszel stratification mitigates but does not fully eliminate doc-length-to-PPL correlation
5. **5 languages only**: Results may differ for languages outside en/de/fr/es/it (especially very low-resource languages not in RedPajama-V2)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | CONVERGED at exchange 15 of 15 |
| **Clarity Verified** | Yes |
| **Hypothesis ID** | H-M1-v2 |
| **Remaining Objections** | 3 documented (scope, length confound, z-score heavy tail) — all Phase 6 limitations |

---

*Phase 2A Complete — Outputs ready for Phase 2B planning*
