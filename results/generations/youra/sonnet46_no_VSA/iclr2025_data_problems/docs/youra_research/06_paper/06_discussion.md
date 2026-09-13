# Discussion

## 6.1 Mechanism Interpretation

The retention ordering es > fr > it > en > de — perfectly consistent across all five tested threshold levels — aligns with a specific structural prediction from the CCNet design. CCNet \cite{Wenzek2020} trains one KenLM language model per language using that language's Wikipedia as reference text. English Wikipedia contains approximately 6.7 million articles; German Wikipedia, approximately 2.8 million; French, 2.5 million; Spanish, 1.9 million; Italian, 1.7 million.

We hypothesize that the *relative* perplexity scale is inverted between web text and Wikipedia text in a language-family-dependent way. English and German Wikipedia are large, diverse, and formally structured, producing KenLM models that assign relatively *low* perplexity to matching-register web text. Equivalently, English and German CommonCrawl web text that is high-quality but informal may receive higher perplexity from models trained on formal Wikipedia prose. Spanish, French, and Italian Wikipedias are smaller and potentially less domain-diverse, producing KenLM models that assign higher perplexity to a broader range of web text — including both high-quality and colloquial documents.

This hypothesis is *consistent with* the observed retention ordering and the KDE distributions (Figure 4), but the causal mechanism has not been directly tested. The planned follow-up experiments (h-m1: per-language percentile calibration; h-c1: CCNet-consistent tercile negative control) would provide stronger mechanistic evidence by testing whether recalibration removes the disparity and whether the disparity is specific to global threshold calibration rather than upstream pipeline factors.

## 6.2 Prior Estimate Recalibration

Our empirical measurement (V = 0.40–0.57) is 25–40% larger than the prior literature-based estimate (V = 0.29–0.41). This gap has a practical implication: researchers who size their correction experiments based on estimates from CCNet paper descriptions will systematically underestimate the required effect size.

The iterative gate calibration in this study (h-e1 → h-e1-v3 → h-e1-v3-v4) provides a documented trajectory of this estimation error. The initial gate range [0.29, 0.41] — derived from Phase 2B prior estimates based on CCNet paper descriptions and multilingual quality filtering literature — was too narrow to capture the actual effect. All three experimental runs produced identical V values (0.4021–0.5696); only the gate range changed between iterations. This is not a failure of the experimental protocol but rather a finding: prior estimates from CCNet descriptions underestimate the actual disparity on this specific dataset.

We report this recalibration transparently as a secondary contribution. Future researchers estimating whether their correction strategy achieves "sufficient" disparity reduction should use the empirical baseline V = 0.40–0.57 rather than paper-description estimates.

## 6.3 The Saturation Regime

The Spanish saturation phenomenon (retention = 100% at k ≥ 40) is a qualitatively distinct finding beyond the main disparity measurement. At threshold levels k = 40 and k = 50, the global threshold has been set so permissively — driven by the Germanic language mass at the lower end of the perplexity distribution — that it falls below every Spanish document's perplexity score. This means:

1. **No Spanish-specific correction is possible at k ≥ 40.** Any per-language calibration strategy must either accept 100% Spanish retention (if calibrated to keep k% of each language) or use a different target that imposes a lower ceiling on Spanish.

2. **The correction problem becomes asymmetric.** A per-language percentile threshold at k=40 would keep 40% of each language, dramatically *reducing* Spanish retention from 100% to 40% while *increasing* German retention from 20.7% to 40%. The correction is not just reduction of V; it involves substantial reconfiguration of which documents are retained from each language.

3. **Practitioners using k=40–50 may be unaware of the saturation.** A practitioner who looks only at overall corpus statistics — overall retention rate is exactly k% by construction of any percentile threshold — would not notice that all Spanish documents and virtually all French documents are retained, while most German and English documents are removed.

## 6.4 Limitations

**L1: Existence-only scope.** This paper establishes that the disparity exists and characterizes its magnitude and structure. The proposed correction mechanism — per-language percentile calibration — was not experimentally tested. The claims about V = 0.40–0.57 are well-supported; claims about the correction are explicitly framed as future work.

**L2: Sample scope.** Our analysis uses 208,262 documents from the head+middle partition, approximately 0.0002% of the full 113.3B document corpus. The effect magnitude could differ at scale if the tail partition has different per-language perplexity characteristics. However, three-run consistency on the same sample and the structural nature of the mechanism (driven by KenLM training corpus differences, not sampling) make generalization plausible. High statistical power (Holm p ≈ 0, chi² = 33k–68k) confirms the finding is not sampling noise.

**L3: Document-length confound.** Longer documents tend to have lower perplexity. If language groups differ in average document length, part of the retention gap may reflect length rather than language-family perplexity structure. We did not apply length stratification (Mantel-Haenszel CMH test was planned but not implemented). We note that a 72.7pp retention gap at k=30 substantially exceeds what plausible length differences can account for, and the KDE distributions (Figure 4) confirm structurally different per-language perplexity shapes independent of length effects. Length stratification is recommended as a robustness check.

**L4: Single dataset.** Results are specific to RedPajama-V2 with CCNet perplexity signals. Whether the same disparity magnitude occurs on other corpora (C4, OSCAR, Dolma) or with other quality signals (duplicate ratio, punctuation fraction, neural LM perplexity) is not tested.
