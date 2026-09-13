# Superseded Hypothesis Record

**Date:** 2026-07-30T04:00:00+00:00
**Hypothesis:** h-m1
**Superseded By:** h-m1-v2 (via phase2a-dialogue)
**Status:** SUPERSEDED

## Supersede Reason

Hypothesis direction was fundamentally inverted. h-m1 predicted low-resource language groups would show lower retention under global perplexity thresholds, but experimental results (208,263 rows, RedPajama-V2) showed the opposite: English is most excluded (retention 3.7%–36.5% at τ = 10th–50th percentile), while low-resource Italian retains 18.2%–88.1%. The lr_gap_pp metric was negative at all 5 τ values (-14.45pp to -51.67pp), directly contradicting the hypothesis direction. The mechanism (disparity) was confirmed (Cramér's V = 0.29–0.41, all Holm p = 0), but the direction requires redesign.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | 0.2 |
| Recommendation | SUPERSEDE |
| Reasoning | Core directional claim refuted. English has higher perplexity distribution than low-resource languages in this corpus, causing global thresholds to disproportionately exclude English, not low-resource groups. Fundamental redesign needed... |

## Key Experimental Findings (Preserved)

- Pipeline ran end-to-end successfully (208,263 rows, 5 modules, 27/27 tests pass)
- Disparity mechanism IS real: Cramér's V = 0.29–0.41 at all 5 τ
- All Holm-corrected p-values = 0 (strong statistical signal)
- English retention: 3.7% (τ=10th) to 36.5% (τ=50th) — most excluded
- Italian (low-resource proxy) retention: 18.2% (τ=10th) to 88.1% (τ=50th) — least excluded
- lr_gap_pp range: -51.67pp to -14.45pp (all negative — direction inverted)
- 6 figures generated at 300 DPI

## Insight for h-m1-v2

The disparity mechanism is real and strong, but the direction is: global perplexity thresholds disproportionately EXCLUDE high-perplexity languages (English in CommonCrawl web text). Low-resource languages with simpler/shorter text have lower perplexity and thus higher retention. A reformulated hypothesis should address this inverted disparity or examine language-adaptive thresholds that correct for per-language perplexity distributions.

## Timeline

1. Original hypothesis: h-m1 (low-resource excluded more)
2. FAIL gate — direction inverted, not magnitude issue
3. Cramér's V confirmed strong disparity (just wrong direction)
4. Decision: SUPERSEDE → route to phase2a-dialogue for h-m1-v2
5. New direction: h-m1-v2 (reformulated directional claim)

---
*Superseded at: 2026-07-30T04:00:00+00:00*
