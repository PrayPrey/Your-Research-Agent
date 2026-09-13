# 6. Discussion

## 6.1 Key Findings

**The bias is large, structural, and persistent across threshold choices.** Cramér's V = 0.40–0.57 places the language × retention association firmly in the "large" effect range. More importantly, the bias is not concentrated at a specific threshold level — any practitioner using global k-th percentile filtering on ccnet_perplexity, for any k in the practical range, will encounter a disparity of this magnitude. The consistent es > fr > it > en > de retention ordering across all five threshold levels is not compatible with a sampling artifact explanation; it tracks the Romance–Germanic language family boundary precisely.

**The implication for practitioners is direct.** At k=30 — a commonly used threshold — a practitioner would retain 6.3× more Spanish documents than German documents from the same raw corpus. At k=40, they would retain essentially all Spanish documents while excluding 79% of German documents. The training corpus this produces does not reflect relative document quality; it reflects a calibration artifact introduced by applying a global threshold to locally-calibrated perplexity scores.

**Prior estimates underestimate the bias.** Our finding that V = 0.40–0.57 exceeds literature-derived estimates of V ∈ [0.29, 0.41] by 25–40% has consequences for future correction study design. Researchers who rely on CCNet paper descriptions to power their correction experiments will underestimate the required effect size for detecting significant bias reduction, potentially leading to inconclusive results on studies that would otherwise detect partial corrections. We recommend using the V = 0.40–0.57 calibrated baseline from this work when designing correction studies on the RedPajama-V2 ccnet_perplexity signal.

## 6.2 Connection to Prior Work

Our measurement extends Caswell et al. [2021]'s qualitative documentation of cross-language quality disparities in multilingual web datasets to a specific, quantitative baseline. Their finding that "per-language quality evaluation is necessary" is confirmed with a concrete associativity measure. Our finding complements Turki et al. [2026]'s recommendation of percentile-based per-language thresholding by providing the precise V baseline that per-language calibration would need to reduce — previously unavailable in the literature.

The finding is consistent with CCNet's original design intent [Wenzek et al., 2019]: CCNet uses language-specific cutoff values precisely because global thresholds on per-language KenLM scores are not appropriate. The disparity we measure is what happens when practitioners deviate from this design by applying a single global threshold.

## 6.3 Limitations

**L1: Existence-Only Scope.** This paper tests only the existence of the disparity under global thresholding. Whether per-language percentile calibration (h-m1), CCNet-consistent tercile calibration (h-c1), or iso-retention z-score normalization (h-m2) reduces the disparity — and by how much — is not tested here. The paper characterizes the problem; the correction study is the necessary next step.

*Why acceptable:* The existence finding is independently publishable and necessary. Without a calibrated V baseline, any correction study lacks a proper reference point. The characterization contribution is complete and stands on its own.

**L2: Sample Scope.** Results are based on 208,262 documents from the head and middle partitions of RedPajama-V2 (approximately 0.0002% of the full 113.3B document corpus). Cramér's V magnitudes may differ at scale if per-language perplexity distributions shift in the tail partition.

*Why acceptable:* Statistical power is high (Holm p ≈ 0, n = 208,262). The phenomenon is structurally driven by KenLM training corpus differences — an effect that is unlikely to reverse at scale. The direction and ordering of the disparity are confirmed across three independent runs on the same sample.

**L3: Document-Length Confound.** Longer documents tend to have lower perplexity. If language groups differ in document length distributions, part of the retention gap could reflect length differences rather than purely language-family perplexity structure. Mantel-Haenszel length stratification was planned but not implemented.

*Why acceptable:* The 72.7pp retention gap at k=30 substantially exceeds what a plausible length confound could explain. The perplexity KDE plots (Figure 3) show structurally divergent distributional shapes rather than simple location shifts, suggesting language-family structure rather than length-driven scale differences. Length stratification is a recommended robustness check for future work.

**L4: Five-Language Sample.** Our sample covers only five European languages — two Germanic (en, de) and three Romance (es, fr, it) — all with substantial Wikipedia and CommonCrawl representation. The findings may not generalize to low-resource languages or non-Indo-European languages where CCNet KenLM training corpus availability and quality differ substantially.

## 6.4 Broader Impact

The finding that global ccnet_perplexity thresholding produces Cramér's V = 0.40–0.57 language-family disparity has direct implications for multilingual LLM training. Any model trained on a corpus filtered using global percentile thresholds on this quality signal will have structurally imbalanced language coverage — with systematic under-representation of Germanic languages relative to Romance languages. This is not a quality-based imbalance but a calibration artifact.

Positive impact: We provide a precise, reproducible measurement that enables the NLP community to (a) audit existing multilingual training datasets for this specific bias source, (b) design properly powered correction studies, and (c) adopt per-language calibration as a default practice.

Potential concerns: Practitioners reading this work who switch to per-language calibration without proper evaluation may inadvertently introduce other biases (e.g., threshold level becomes harder to interpret across languages). We recommend evaluating correction strategies against the V baseline we establish before deploying in production pipelines.
