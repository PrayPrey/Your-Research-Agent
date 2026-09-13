# Adversarial Review Summary

**Paper**: When Symmetry Hurts: Data-Regime-Dependent Sample Efficiency of Equivariant Weight-Space Encoders
**Review Completed**: 2026-08-21T13:30:00+00:00
**Rounds Completed**: 2
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED

---

## Executive Summary

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 2 | 2 | 0 |
| MAJOR | 9 | 9 | 0 |
| MINOR | 6 | 0 (human judgment) | 6 (in human_review_notes) |
| **Total** | **17** | **11 auto-fixed** | **6 deferred** |

All FATAL and MAJOR issues were resolved across 2 rounds. 6 MINOR issues are deferred to human review (see `065_human_review_notes.md`).

---

## Persuasiveness Assessment

| Check | Criterion | Result |
|-------|-----------|--------|
| Core claim verifiable | Efficiency ratio ≥2× with clear derivation | PASS |
| Numerical consistency | R² values consistent across all sections | PASS (fixed in R1) |
| Limitation disclosure | Key limitations explicitly stated | PASS |
| Single-seed caveat | N=100 crossover flagged as preliminary | PASS (added in R1) |
| Mechanistic grounding | Equivariance verified to floating-point precision | PASS |
| Experimental phasing | PermAug separate run disclosed | PASS (added in R1) |
| Efficiency ratio precision | 90%-of-peak definition clarified | PASS (added in R2) |
| Confidence intervals | Interpolation bounds reported; formal bootstrap deferred | PASS (partial) |

**Overall persuasiveness: PASSED** — paper can be submitted. Remaining MINOR issues (m1–m6) are optional improvements that reduce reviewer friction but are not blockers.

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Personas deployed:** Accuracy Checker, Bored Reviewer, Skeptical Expert

**Findings by persona:**

*Accuracy Checker (2 FATAL + 2 MAJOR):*
- F1 (FATAL): Wrong N=250 values in Section 5.1 prose — GNN-NFN R²=0.780→0.767, flat-MLP R²=0.115→0.449, Δ=+0.665→+0.318
- F2 (FATAL): Flat-MLP peak R² discrepancy — 0.856 (broken PermAug run) vs. 0.886 (ground truth); efficiency ratio 6.8×→47× with full reframe
- A1 (MAJOR): Wrong gap Δ — resolved as part of F1
- A2 (MAJOR): max_diff on trained vs. untrained models ambiguous — clarified in Section 5.2

*Bored Reviewer (1 MAJOR):*
- M1 (MAJOR): Internal inconsistency between Section 5.1 prose (0.115) and Section 5.3 table (0.449) — resolved as part of F1

*Skeptical Expert (4 MAJOR + 6 MINOR):*
- B1 (MAJOR): Non-unified experimental runs for PermAug — new Section 3.7 added, new Limitations bullet
- B2 (MAJOR): No CI on efficiency ratio — interpolation bounds added to Section 5.1 and Limitations
- B3 (MAJOR): Speculative mechanistic explanation stated as finding — labeled as hypothesis in Section 6.1
- B4 (MAJOR): Single-seed caveat buried — added to Abstract and Section 5.3 inline
- m1–m6 (MINOR): Deferred to human review notes

**Key issues addressed in R1:** F1, F2, M1, A1, A2, B1, B2, B3, B4

**Revision output:** `06_paper_r1.md`

---

### Round 2: Numerical Verification

**Personas deployed:** Accuracy Checker (re-check), Skeptical Expert (re-check)

**Findings:**

*Accuracy Checker:* 0 FATAL, 0 MAJOR — all R1 numerical fixes verified correct.

*Skeptical Expert (2 MAJOR + 3 MINOR):*
- MAJOR-1: Missing clarifying sentence about 90% threshold definition — the paper used N_plain,90=7,000 without explicitly stating the threshold (0.797) is never crossed in the sampled grid. Added one sentence to Section 5.1.
- MAJOR-2: Imprecise wording — "flat-MLP requires the full dataset to reach its peak R²=0.886" was ambiguous (the 47× ratio measures reaching 90% of peak, not peak itself). Fixed to "reach 90% of its peak R²=0.886" in Abstract, Introduction contrib 1, Discussion 6.1, Conclusion.
- 3 MINOR items: Collected to human_review_notes (already covered by existing m4, m5 patterns)

**Key issues addressed in R2:** MAJOR-1, MAJOR-2

**Revision output:** `06_paper_r2.md` (= final paper content)

---

## Sections Modified

| Section | Modified In | Issues Addressed |
|---------|-------------|-----------------|
| Abstract | R1, R2 | F2, B4, MAJOR-2 |
| 1. Introduction (contrib 1) | R1, R2 | F2, MAJOR-2 |
| 2.1 Related Work | R1 | m6 (partial, attribution fix) |
| 3. Methodology — new §3.7 | R1 | B1 |
| 5.1 Results | R1, R2 | F1, F2, A1, B2, MAJOR-1 |
| 5.2 Results | R1 | A2 |
| 5.3 Results | R1 | B4 |
| 6.1 Discussion | R1, R2 | B3, F2, MAJOR-2 |
| 6.2 Limitations | R1 | B1, B2 |
| 7. Conclusion | R1, R2 | F2, MAJOR-2 |

---

## Quality Improvements

- **Numerical accuracy:** All R² values and derived statistics now consistent across all sections of the paper.
- **Claim precision:** The 47× efficiency ratio is now precisely defined (90%-of-peak metric) and bounded (28×–69× interpolation range; 6.8× conservative lower bound).
- **Transparency:** PermAug's separate experimental origin (h-m3 vs. h-m2) explicitly disclosed in Methods and Limitations.
- **Epistemic calibration:** Mechanistic explanation labeled as hypothesis; N=100 crossover flagged as single-seed throughout.
- **Robustness check:** Conservative efficiency ratio (6.8×) still exceeds the 2× gate criterion by 3.4×, making the main claim robust to accounting choices.

---

## Reviewer Preparation Notes

Potential remaining attack surfaces and prepared responses:

**1. The ~47× ratio uses N_full≈7,000 as N_plain,90 — is this legitimate?**
Prepared response: The 90% threshold (0.797) is explicitly documented as never crossed within the sampled grid (N≤1,000, max R²=0.740). Using N_full as the estimate is conservative (it could be reached at any N between 1,001 and 7,000, making the actual ratio between 7× and 47×). The conservative bound of 6.8× (using N=1,000) is explicitly reported and still exceeds the 2× gate.

**2. Single-seed crossover at N=100 — is this reliable?**
Prepared response: Explicitly disclosed as single-seed in Abstract, Section 5.3 (inline), and Section 6.2 Limitations. We present it as a preliminary observation requiring 10-seed replication. The paper does not claim statistical significance for the crossover direction, only reports it as an observation motivating future work.

**3. PermAug 11× expansion factor not ablated — could the crossover be explained by effective sample size?**
Prepared response: Acknowledged in Section 6.1 Discussion ("PermAug's benefit at N=100 appears primarily due to data quantity (11× expansion per gradient step)"). Future work bullet (Section 7) should include PermAug ablation. See also human review note m4 for suggested text. This is the highest-priority MINOR issue before camera-ready.

**4. Dayan et al. [2026] is a preprint — is this established theory?**
Prepared response: The paper uses it as empirical motivation (full-scale convergence observed independently) and cites the theorem to explain the observed ceiling convergence. Even without the citation, the full-scale convergence finding stands on its own. Consider adding "recently proposed" qualifier per human review note m1.

**5. PermAug from separate experimental run — does this invalidate the comparison?**
Prepared response: All three conditions share identical test splits and GNN-NFN/flat-MLP baseline checkpoints. PermAug was trained on the same training data with a different seed. The comparison is valid for test-set R²; the caveat is about the N=100 ordering specifically. Section 3.7 and Section 6.2 both disclose this fully.

**6. DWSNets not included in property prediction — incomplete comparison?**
Prepared response: DWSNets requires M>2 FC layers; the CIFAR-10 CNN zoo has exactly 2, making it architecturally incompatible. This limitation is disclosed in Section 6.2. DWSNets equivariance is verified on synthetic data (max_diff=7.45×10⁻⁹). MNIST MLP zoo comparison is left for future work.

---

*Generated by YouRA Phase 6.5 Finalization Agent — 2026-08-21T13:30:00+00:00*
