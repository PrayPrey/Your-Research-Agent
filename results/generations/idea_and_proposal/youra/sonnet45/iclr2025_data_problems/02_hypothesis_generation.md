# Phase 2A Extended: Hypothesis Summary for Phase 2B

**Date:** 2026-02-06
**Author:** Pray
**Hypothesis ID:** H-ICLR2025-CONTAM-001
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Research Question:** How can we detect cross-lingual benchmark contamination in multilingual foundation models when traditional text-overlap methods fail?

**Main Hypothesis:**
Multi-channel behavioral side-channel analysis—combining confidence divergence testing, output consistency analysis, and semantic perturbation measurement with typology-aware adaptive thresholding—achieves superior contamination detection accuracy (TPR ≥ 0.85, FPR ≤ 0.10) compared to single-method baselines.

**Confidence Level:** 0.82 (HIGH)

**Target Gap:** Gap 2 (Cross-Lingual Contamination at Scale) - Existing methods fail to detect contamination that propagates across languages via multilingual representations (Yao et al., 2024).

---

## Core Innovation

### Theoretical Contribution
**Contamination as Information Leakage:** First framework conceptualizing benchmark contamination as a side-channel information leakage phenomenon (analogous to cryptographic side-channel attacks), detectable through multi-channel behavioral signatures rather than direct text overlap.

### Methodological Contribution
**3-Channel Behavioral Detection Framework:**

1. **Channel 1 - Confidence Divergence:** Paired t-tests on confidence scores across language pairs (adapted from PaCoST)
2. **Channel 2 - Output Consistency:** Cross-lingual answer correlation analysis
3. **Channel 3 - Perturbation Response:** Semantic perturbation brittleness testing (adapted from Yao et al.)
4. **Adaptive Fusion:** WALS typology-aware threshold calibration + ensemble voting

**Key Innovation:** First multi-channel ensemble for contamination detection with linguistic typology integration.

### Practical Contribution
- **Output-only detection** (no training data access required) → works with closed-source models (GPT-4, Claude)
- **Scalable:** O(n) complexity per language pair
- **Cost-efficient:** ~$500 automated detection vs. ~$50K manual auditing per benchmark
- **Target users:** Benchmark maintainers, model developers, academic researchers

---

## Testable Predictions

**Primary (P1):** Multi-channel detection achieves TPR ≥ 0.85, FPR ≤ 0.10 on cross-lingual contamination (≥15 F1-points improvement vs. best single-method baseline)

**Secondary:**
- **P2:** Confidence divergence ≥20 percentage points between contaminated vs. clean pairs (p < 0.01)
- **P3:** Output consistency ≥0.80 (contaminated) vs. ≤0.50 (clean), p < 0.001
- **P4:** Perturbation retention ≤30% (contaminated) vs. ≥70% (clean), p < 0.01
- **P5:** Adaptive typology thresholding reduces accuracy gap across language pairs by ≥50%
- **P6:** Ensemble outperforms best single-channel by ≥15 F1-points

**Falsification Criteria:**
- TPR < 0.75 OR FPR > 0.20
- Ensemble F1 ≤ best single-channel F1 + 0.05
- Typology adaptation performs worse than fixed thresholds
- Any prediction (P2-P6) fails with p > 0.05

---

## Experimental Design

**Models:** mBERT-base, XLM-R-large, mT5-base (3 families)
**Benchmarks:** MMLU-multilingual, XQuAD, TyDiQA
**Contamination Levels:** 0%, 25%, 50%, 75%, 100%
**Language Pairs:** EN-ZH (distant), EN-AR (distant), EN-ES (close), EN-FI (medium)

**Baselines:**
1. Yao et al. (2024) - Cross-lingual generalization testing
2. Zhang et al. (2024) - PaCoST confidence testing
3. Xu et al. (2024) - Text-overlap detection

**Statistical Tests:**
- McNemar's test for paired detection accuracy
- Paired t-tests for TPR/FPR differences (Bonferroni corrected)
- Power = 0.80, minimum detectable effect = 0.10 TPR difference

**Metrics:** TPR, FPR, F1-score, AUC-ROC, detection latency, computational cost

---

## Phase 2B Sub-Hypothesis Decomposition

### SH1: Channel Validity (Existence)
**Statement:** Each behavioral channel independently correlates with contamination (AUC > 0.70, p < 0.01) with typology-modulated strength.

**Validation:** Single-channel ablation experiments + typology sensitivity analysis

---

### SH2: Typology Moderation (Mechanism)
**Statement:** WALS-based adaptive thresholding improves F1-score by ≥0.05 on typologically distant language pairs.

**Validation:** Compare fixed vs. adaptive thresholds across 4 language pairs + regression analysis (typology distance vs. accuracy)

---

### SH3: Ensemble Superiority (Comparison)
**Statement:** Multi-channel ensemble outperforms single-method baselines by ≥0.10 F1-score, with highest gains on cross-lingual scenarios.

**Validation:** Direct comparison experiments + McNemar's test + subgroup analysis (monolingual vs. cross-lingual)

---

## Key Assumptions

1. **Access:** Model outputs (logits, confidence) accessible for multiple languages
2. **Translations:** High-quality benchmark translations available (XNLI, MMLU-multi, XQuAD)
3. **Behavioral Consistency:** Contamination signatures stable within language families
4. **Typology Database:** WALS provides sufficient features (192 features, 2,679 languages)
5. **Clean Baselines:** Cross-contamination validation establishes known-clean references
6. **Channel Independence:** Three channels provide non-redundant information (testable)
7. **Calibration:** Validation sets with known contamination levels available

---

## Scope & Limitations

**Applies To:**
- Multilingual models with shared representations (mBERT, XLM-R, mT5, GPT-4-multi)
- Translated benchmark contamination (MMLU-Chinese → MMLU-English)
- Languages with WALS typology data (2,679 languages)
- Post-deployment contamination detection (no training data access)

**Does NOT Apply To:**
- Monolingual models without cross-lingual transfer
- Data augmentation contamination (non-benchmark paraphrases)
- Adversarial contamination (intentional evasion)
- Real-time training contamination detection
- Languages without typology data or translations

**Limitations:**
- Computational cost: 3-5x slower than single-method (still practical at O(n))
- Typology dependency: Performance degrades for under-documented languages
- False positives: Code-switching effects may trigger false alarms if not calibrated
- Adversarial vulnerability: Public method may enable evasion (future arms race)

---

## Related Work Foundation

**Core Papers:**
1. **Yao et al. (2024)** - "Data Contamination Can Cross Language Barriers" (Foundation: defines problem)
2. **Zhang et al. (2024)** - "PaCoST" (Methodology: confidence testing framework)
3. **Xu et al. (2024)** - "Benchmarking Benchmark Leakage" (Baseline: text-overlap detection)

**Cross-Domain Inspiration:**
4. **Hamoudi et al. (2021)** - Cryptographic side-channel analysis (multi-channel correlation)
5. **Chen & Farrús (2022)** - Cross-lingual neural patterns (typology motivation)

**Gaps Addressed:**
- Single-method limitations (Yao/PaCoST/Xu each use one channel only)
- Cross-lingual typology ignored (fixed thresholds across all language pairs)
- No cross-domain transfer (isolation from cryptography/linguistics)
- Closed-source model coverage (most methods require training data)

---

## Open Questions for Phase 2B

**HIGH Priority:**
1. Which WALS features optimal for typology distance? (word order? morphology? combination?)
2. Cross-contamination validation protocol design? (avoid circular validation)

**MEDIUM Priority:**
3. Channel correlation analysis? (test independence assumption)
4. Low-resource language fallback strategies? (no WALS data)
5. Multi-benchmark testing scope? (MMLU + XQuAD + TyDiQA vs. focus on one)

**LOW Priority (Future Work):**
6. Adversarial robustness investigation? (out of scope for v1)
7. Computational optimization? (early stopping, channel prioritization)

---

## Success Criteria

**Minimum Viable:** TPR ≥ 0.80, FPR ≤ 0.15 (match SOTA)
**Strong Success:** TPR ≥ 0.85, FPR ≤ 0.10 (significant improvement)
**Exceptional:** TPR ≥ 0.90, FPR ≤ 0.05 (transformative accuracy)

**Phase 2B Readiness Checklist:**
- [x] Hypothesis falsifiable with clear criteria
- [x] Variables operationalized (IV/DV/CV defined)
- [x] Causal mechanism explicit (4-step chain with evidence)
- [x] Statistical design complete (tests, power analysis, metrics)
- [x] Baselines identified (3 single-method comparisons)
- [x] Sub-hypotheses decomposed (SH1-SH3)
- [x] Scope boundaries clear (in/out of scope specified)

**Overall Status:** ✅ **READY FOR PHASE 2B VERIFICATION PLANNING**

---

## Next Steps

1. **Phase 2B:** Decompose into detailed sub-hypotheses + verification roadmap
2. **Phase 2C:** Design experiments for each sub-hypothesis (SH1-SH3)
3. **Phase 3:** Implementation planning (PRD, Architecture, Archon tasks)
4. **Phase 4:** Code + validate hypothesis
5. **Phase 5:** Write paper (target: ICLR 2026 DATA-FM workshop)

---

**Full Technical Details:** See `02a_extended_hypothesis_full.md`

**Cross-Reference:**
- Phase 0: `00_brainstorm_session.md`
- Phase 1: `01_targeted_research.md`
- Phase 2A: `02a_validated_hypotheses.md`, `02a_round_1_discussion.md`

---

*Generated using YouRA Phase 2A Extended Workflow*
*Execution Mode: YOLO (Fully Automated)*
*Date: 2026-02-06*
*Ready for: Phase 2B Verification Planning*
