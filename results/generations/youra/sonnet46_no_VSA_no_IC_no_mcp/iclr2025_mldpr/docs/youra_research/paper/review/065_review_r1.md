# Adversarial Review — Round 1
**Paper**: When Did GLUE Go Stale? Automated Benchmark Saturation Detection via Logistic Growth Model Fitting  
**Round**: R1 — Accuracy and Engagement  
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert  
**Date**: 2026-08-25T20:00:00+00:00  

---

## Ground Truth Verification Summary

All 20 quantitative metrics in 065_ground_truth.yaml verified against paper claims.  
**Result: 0 numerical discrepancies.** Every reported value (R², ΔAIC, K, r, t₀, saturation dates, H-C1 metrics) matches ground truth exactly.

---

## Executive Summary

| Severity | Found | Source |
|----------|-------|--------|
| FATAL | 0 | — |
| MAJOR | 4 | See below |
| MINOR | 7 | Collected in human_review_notes |

**Persuasiveness**: PASSED  
- Abstract compelling: YES  
- Problem clear in 1 minute: YES  
- Novelty clear in 2 minutes: YES  
- Would continue reading: YES  
- Attention lost at: briefly in Section 2.2, recovered by positioning paragraph  

**Overall recommendation**: REVISE — fix 4 MAJOR issues, then strong candidate.

---

## FATAL Issues

*None.*

---

## MAJOR Issues

### MAJ-001 — Abstract ΔAIC Range Conflates Linear and Power-Law Comparisons
**Persona**: Accuracy Checker  
**Location**: Abstract, sentence beginning "ΔAIC ≈ −194 to −357 versus linear"  
**Issue**: The range "−194 to −357" is presented as "versus linear" but the values span both linear and power-law comparisons:
- vs linear: −194.37 (SuperGLUE) to −250.50 (GLUE) → range is −194 to −250
- vs power-law: −112.72 (SuperGLUE) to −357.09 (GLUE)

The claim "−194 to −357 versus linear" is factually incorrect. The value −357.09 is vs power-law, not vs linear. A reviewer checking the numbers will immediately flag this.

**Required fix**: Either (a) scope to linear only: "ΔAIC ≈ −194 to −250 versus linear, −113 to −357 versus power-law", or (b) write "ΔAIC ≈ −113 to −357 versus alternative models" with "versus linear" removed, or (c) add a parenthetical "(vs. linear) and −113 to −357 (vs. power-law)".

**Evidence**: Ground truth: ΔAIC_lin_GLUE=−250.50, ΔAIC_lin_SuperGLUE=−194.37, ΔAIC_pl_GLUE=−357.09, ΔAIC_pl_SuperGLUE=−112.72.

---

### MAJ-002 — Uncaveated "First" Novelty Claim
**Persona**: Bored Reviewer  
**Location**: Introduction, Contribution 1: "First automated benchmark saturation detection pipeline"  
**Issue**: The paper acknowledges in Section 2.3: "We are not aware of prior work applying logistic growth models to benchmark leaderboard timeseries." The phrase "not aware of" is scientific hedging language that belongs in the contribution list as well. As written, Contribution 1 is an absolute "first" claim that a reviewer can attack by finding any prior automated approach (even tangentially related). Strong claims need strong evidence; "first" in a title contribution requires a systematic literature search or an explicit hedge.

**Required fix**: Change "First automated benchmark saturation detection pipeline" to "To our knowledge, the first automated benchmark saturation detection pipeline". Apply the same hedge in the Abstract and Conclusion where the "first" claim recurs.

**Note**: This is a pattern issue — fix consistently in Abstract, Intro (Contribution 1), and Conclusion.

---

### MAJ-003 — No Detection Accuracy Baseline
**Persona**: Skeptical Expert  
**Location**: Section 5.4 (RQ4), Table 4  
**Issue**: The dual-criterion detector achieves 3-month and 5-month accuracy. This is reported without any baseline comparison for the detection task itself. A reviewer will ask: "Is 3 months good? How does this compare to a naive detector?" Without a baseline, the absolute accuracy numbers are unanchored. Plausible naive baselines include: (a) threshold on raw score (detect when top-3 mean ≥ 0.99), (b) moving-average crossing, (c) community consensus date directly. The paper argues the method is necessary precisely because no automated baseline exists — but that makes it even more important to show what ad-hoc methods would yield.

**Required fix**: Add a brief comparison (even just 1–2 rows in Table 4) showing what a naive detector (e.g., simple score threshold without rate criterion) achieves on the same data. This anchors the 3m/5m result. If naive methods achieve similar accuracy, the dual-criterion's value needs different justification; if they perform worse, this strengthens the paper.

---

### MAJ-004 — Ground Truth Circularity Not Acknowledged
**Persona**: Skeptical Expert  
**Location**: Section 6.2 Limitations  
**Issue**: The "ground truth" saturation dates (Sept 2019 for GLUE, Jun 2021 for SuperGLUE) are sourced from published community papers — the SuperGLUE paper and BIG-bench paper respectively. These dates are community judgment calls retroactively documented, not independently measured saturation timestamps. There is a circularity risk: the paper validates against community consensus, while the motivation claims the pipeline is needed because community consensus is unreliable/delayed. A skeptical reviewer will ask: "How do you validate a method meant to replace community consensus by comparing to community consensus?"

This is a genuine epistemic limitation that the paper should acknowledge explicitly in L2 or as a new L6. The existing L5 (negative t₀ interpretation) covers a different issue.

**Required fix**: Add a limitation (L6 or extend L2): "The ground truth saturation dates used for validation are themselves community-documented events from published papers, not independently measured saturation timestamps. This creates an evaluation circularity: our detector is validated against the same community judgment it aims to systematize. An ideal validation would use blind annotation of saturation dates from annotators who had not observed community responses, or prospective prediction prior to community action."

---

## MINOR Issues (Collected for Human Review — NOT auto-fixed)

MIN-001: Section 5.2 — "ΔAIC values are 19–36× larger than decisive threshold" — the 11.3× value (SuperGLUE vs power-law) is excluded from this range. If all four ΔAICs are meant, write "11–36×". If scoped to vs-linear only, scope the sentence explicitly.

MIN-002: Section 5.3 — "K ≈ 0.89 aligns precisely with human parity (~89.8%)" — the 89.8% human parity figure needs a specific citation (likely the original GLUE paper, Wang et al. 2018, which reports 87.1% average human performance; the 89.8% should be verified against its actual source).

MIN-003: Appendix B — the H-C1 bounds (`bounds_lower_c1 = [0.8, 0.1, 6]`) differ from main pipeline bounds (t₀ lower = −24). Add a comment clarifying these are H-C1-specific bounds for benchmarks with sufficient early-phase data, not the general pipeline defaults.

MIN-004: Introduction paragraph 1 — "no automated system" appears in both the first sentence ("no automated system detects when this saturation occurs") and implicitly in the hook. In Section 2.3, "We are not aware of prior work" also signals the same. Minor redundancy; consider collapsing.

MIN-005: Section 5.5 (RQ5) — The K-boundary hit rate detail (25% → 50% when bounds removed) is mechanistically important but detailed for main results. Consider moving to Appendix C with a forward pointer.

MIN-006: Section 5.2 / Discussion — The SuperGLUE power-law AIC (−372.71) is more negative than linear (−291.06), meaning power-law beats linear for SuperGLUE. The logistic still beats both, but the paper doesn't discuss why power-law better describes SuperGLUE than GLUE. A sentence noting this asymmetry (e.g., SuperGLUE's trajectory may have a longer growth phase visible in the data) would preempt reviewer questions.

MIN-007: Abstract, final sentence — "transforming what has been a community judgment call into a principled, data-driven measurement" — this is strong language for a two-benchmark retrospective study. Softer: "establishing a principled, data-driven foundation for automated benchmark saturation monitoring."

---

## Ground Truth Verification Log

| Claim | Paper | Ground Truth | Match |
|-------|-------|-------------|-------|
| R² GLUE | 0.9959 | 0.9959 | ✓ |
| R² SuperGLUE | 0.9936 | 0.9936 | ✓ |
| ρ_monotonic GLUE | 0.993 | 0.993 | ✓ |
| ρ_monotonic SuperGLUE | 0.999 | 0.999 | ✓ |
| ρ_decel GLUE | −0.908 | −0.908 | ✓ |
| ρ_decel SuperGLUE | −0.982 | −0.982 | ✓ |
| γ GLUE | 29× | 29× | ✓ |
| γ SuperGLUE | 15× | 15× | ✓ |
| AIC_log GLUE | −590.95 | −590.95 | ✓ |
| AIC_lin GLUE | −340.45 | −340.45 | ✓ |
| AIC_pl GLUE | −233.86 | −233.86 | ✓ |
| ΔAIC_lin GLUE | −250.50 | −250.50 | ✓ |
| ΔAIC_pl GLUE | −357.09 | −357.09 | ✓ |
| AIC_log SuperGLUE | −485.43 | −485.43 | ✓ |
| AIC_lin SuperGLUE | −291.06 | −291.06 | ✓ |
| AIC_pl SuperGLUE | −372.71 | −372.71 | ✓ |
| ΔAIC_lin SuperGLUE | −194.37 | −194.37 | ✓ |
| ΔAIC_pl SuperGLUE | −112.72 | −112.72 | ✓ |
| K GLUE | 0.8955 [0.882, 0.909] | 0.8955 [0.882, 0.909] | ✓ |
| K SuperGLUE | 0.8858 [0.870, 0.902] | 0.8858 [0.870, 0.902] | ✓ |
| r GLUE | 0.2017 [0.181, 0.222] | 0.2017 [0.181, 0.222] | ✓ |
| r SuperGLUE | 0.1578 [0.134, 0.182] | 0.1578 [0.134, 0.182] | ✓ |
| t₀ GLUE | −6.77 | −6.77 | ✓ |
| t₀ SuperGLUE | −2.85 | −2.85 | ✓ |
| Saturation GLUE | Dec 2019, 3m | Dec 2019, 3m | ✓ |
| Saturation SuperGLUE | Nov 2021, 5m | Nov 2021, 5m | ✓ |
| H-C1 mean R² | 0.913 | 0.913 | ✓ |
| H-C1 convergence | 100% | 100% | ✓ |
| H-C1 n_benchmarks | 20 | 20 | ✓ |

**Total discrepancies: 0**

---

## Summary for Revision Agent

**Priority 1 (FATAL):** None.

**Priority 2 (MAJOR — ALL must be fixed):**
1. MAJ-001: Fix "ΔAIC ≈ −194 to −357 versus linear" in Abstract — split linear vs power-law ranges
2. MAJ-002: Add "To our knowledge" hedge to all "first" claims (Abstract, Intro Contribution 1, Conclusion)
3. MAJ-003: Add naive detection baseline to Table 4 in Section 5.4 (e.g., asymptote-only criterion without rate criterion — this is already partially done with θ_K=0.99/θ_r=0.02 in sensitivity table; link to it explicitly as a baseline)
4. MAJ-004: Add L6 limitation in Section 6.2 acknowledging ground truth circularity

**Priority 3 (MINOR — collect in human_review_notes, do NOT auto-fix):**
MIN-001 through MIN-007 as documented above.

**Agent return summary:**
- fatal_count: 0
- major_count: 4
- minor_count: 7
- ground_truth_discrepancies: 0
- persuasiveness_passed: true
- recommendation: REVISE (fix 4 MAJOR, then strong candidate)
