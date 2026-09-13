# Results

## Proxy Extraction (H-E1)

Agency proxies achieve substantially above-target extraction performance. Table 1 reports AUROC for each proxy classifier on the held-out test set.

| Proxy Type | AUROC | Status |
|------------|-------|--------|
| Clarifying Question | 0.9949 | PASS |
| Option Enumeration | 0.9840 | PASS |
| Epistemic Hedging | 0.9880 | PASS |
| Explicit Deferral | 0.9676 | PASS |
| **Mean** | **0.9836** | **PASS** |

All four proxies exceed the 0.8 target threshold, with a mean AUROC of 0.9836. Figure \ref{fig:auroc_bar} visualizes these results. The high performance confirms that agency-related linguistic patterns exist in preference data and are reliably detectable with simple classifiers.

Proxy prevalence varies considerably: epistemic hedging appears in 11.7% of responses, while explicit deferral appears in only 0.3%. This skewed distribution suggests most preference data responses do not exhibit strong agency-preserving behaviors — a finding relevant to later interpretation.

**H-E1 Gate: PASS.** Proceed to representational independence testing.

## Representational Independence (H-M1)

Adversarial probing confirms that BAI occupies an independent representational subspace. Table 2 reports results across three random seeds.

| Seed | BAI AUROC | Reward R² (Baseline) | Reward R² (GRL) | R² Degradation |
|------|-----------|----------------------|-----------------|----------------|
| 42 | 0.9881 | 0.4880 | 0.4973 | -0.93% |
| 123 | 0.9857 | 0.4944 | 0.4854 | 0.90% |
| 456 | 0.9855 | 0.4879 | 0.4955 | -0.76% |
| **Mean** | **0.9864** | — | — | **-0.27%** |

The BAI probe maintains AUROC 0.9864 (± 0.0011) even after gradient reversal actively suppresses reward-predictive variance. Meanwhile, reward probe R² shows negligible change (-0.27% mean), indicating successful disentanglement without destroying reward information.

These results far exceed our targets (BAI AUROC ≥ 0.7, R² degradation < 2%). The BAI signal is not merely a stylistic subcomponent of reward — it occupies genuinely orthogonal representational space.

**H-M1 Gate: PASS.** Representational independence validated.

## Disagreement Analysis (H-M2)

BAI and reward scores show systematic but moderate disagreement. After z-score standardization, 11.77% of responses fall in disagreement quadrants.

| Quadrant | Count | Interpretation |
|----------|-------|----------------|
| HH (high BAI, high reward) | 2,319 | Agreement: agentic → high reward |
| HL (high BAI, low reward) | 3,063 | **Disagreement** |
| LH (low BAI, high reward) | 1,869 | **Disagreement** |
| LL (low BAI, low reward) | 2,847 | Agreement: non-agentic → low reward |

**Disagreement Rate:** (3,063 + 1,869) / 41,896 = **11.77%**

This rate exceeds the PARTIAL threshold (10%) but falls below the PASS threshold (20%). Notably, the HL quadrant (high-BAI, low-reward) substantially exceeds LH (low-BAI, high-reward): 3,063 vs. 1,869 responses. This asymmetry suggests responses exhibiting agency proxies tend to receive lower reward scores more often than vice versa.

Correlation analysis supports partial orthogonality: Pearson r = -0.11 (p < 10⁻¹¹⁰), indicating a weak negative relationship. The correlation is statistically significant but small, consistent with substantial independence rather than opposition.

Figure \ref{fig:scatter_quadrants} visualizes the BAI-reward relationship with quadrant boundaries.

**H-M2 Gate: PARTIAL.** Mechanism exists but is weaker than hypothesized.

## Semantic Coherence (H-C1)

Semantic validation reveals that high-BAI responses do not cluster into interpretable agency patterns. BERTopic discovered 3 topics with 98.05% coverage, but none matched agency vocabulary.

| Topic | Top Keywords |
|-------|--------------|
| 0 | the, you, to, and, of, that, it, in, is, are |
| 1 | welcome, re, you |
| 2 | welcome, re, you, very, thanks, congratulations, thank, learning, okay, happy |

**Agency Pattern Rate:** 0 / 3 = **0%**

The dominant keywords are stopwords and generic conversational markers. The agency vocabulary (clarify, prefer, might, option, perhaps, consider, alternatively, uncertain) does not appear in top-10 keywords for any topic.

This result indicates that BAI, while extractable and representationally independent, does not capture semantically coherent agency-preserving content. The proxy detectors likely identify surface features (length, politeness markers) rather than functional agency preservation.

**H-C1 Gate: FAIL.** Semantic coherence not validated.

## Summary

| Hypothesis | Gate Type | Target | Result | Status |
|------------|-----------|--------|--------|--------|
| H-E1 | MUST_WORK | AUROC ≥ 0.8 | 0.9836 | **PASS** |
| H-M1 | MUST_WORK | BAI AUROC ≥ 0.7, R² deg < 2% | 0.9864, -0.27% | **PASS** |
| H-M2 | SHOULD_WORK | Disagreement ≥ 20% | 11.77% | **PARTIAL** |
| H-C1 | SHOULD_WORK | Agency rate ≥ 50% | 0% | **FAIL** |

Overall: 2 PASS, 1 PARTIAL, 1 FAIL. The core methodological claims (extraction, independence) are validated. The semantic interpretation claim is not supported.
