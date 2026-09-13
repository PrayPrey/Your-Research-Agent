# Adversarial Review Summary

**Paper:** MMLU Scale Confounding in Alignment Benchmark Correlations: A Partial Spearman Diagnostic  
**Review Completed:** 2026-07-30  
**Rounds Completed:** 2 (R1, R2)  
**Final Status:** CONVERGED  
**Persuasiveness Check:** PASSED  

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 0 | 0 | 0 |
| MAJOR | 4 | 4 | 0 |

**MINOR Issues:** Collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Concrete hook: "80% MMLU...alignment coherence disappears by more than half" |
| Problem clear in 1 minute? | PASS | First paragraph states problem, method, result, implication |
| Novelty clear within 2 minutes? | PASS | Contribution (2) explicitly names the Fisher z application |
| Figure 1 self-explanatory? | PARTIAL | Description minimal in compiled paper; acceptable for blind review if figure included |
| Would continue reading? | YES | Strong engagement throughout |
| Attention lost? | Never | Paper maintains reader engagement |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy + Engagement + Credibility)

**R1 Adversary findings:**

**Accuracy Checker:**
| Category | Issues Found |
|----------|--------------|
| N=299 stale value in section file | 1 MAJOR |
| Fisher z formula notation | 1 MAJOR |

**Bored Reviewer:**
| Category | Issues Found |
|----------|--------------|
| Hook quality | 0 (PASS — strong concrete hook) |
| Engagement | 0 (PASS) |
| Contribution clarity | 0 (PASS) |

**Skeptical Expert:**
| Category | Issues Found |
|----------|--------------|
| "First" claim lacks hedge in Conclusion | 1 MAJOR |
| False novelty claims | 0 |
| Unfair baseline comparisons | 0 |
| Missing limitations | 0 (all 5 present) |

**R1 Key Issues Addressed:**
1. **ACC-MAJOR-001** (N=299 → N=297 in section file): Fixed in `sections/04_experiments.md`
2. **ACC-MAJOR-002** (Fisher z formula notation): Added formula clarification in Section 3.1
3. **CRED-MAJOR-001** ("first" claim missing hedge): Added "to our knowledge" to Conclusion Section 7

### Round 2: Numerical Verification (Accuracy Checker + Serena MCP)

R2 verified all 24 primary numerical claims against Phase 4 result JSON files (h_m1_results.json, h_m2_results.json, h_m3_results.json, h-e1/experiment_results.json).

| Claim | Verified? |
|-------|-----------|
| N=296, N=297 | ✓ |
| raw_rho=0.7322, partial_rho=0.3432 | ✓ |
| Fisher z=6.9679, p=3.22×10⁻¹² | ✓ |
| reduction_pct=53.1% | ✓ |
| R²(MMLU×TruthfulQA)=0.4927, R²(MMLU×BBQ)=0.7634 | ✓ |
| CI non-overlap (0.492 < 0.670) | ✓ |
| Sign test k=146/300, p=0.686 | ✓ |
| AMBIGUOUS scenario (robustness ablations) | ✓ |

**R2 Issue Found:**

4. **MATH-MAJOR-001** (Fisher z formula mismatch): R1 revision introduced `√(1/(N−3)+1/(N−4))` (independent-samples) but code uses `√(2/(N−3))` (same-sample). Numerically: paper formula gives z=6.9619 vs reported z=6.9679 from code. Fixed to same-sample formula with Steiger (1980) citation.

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Section 3.1 | Fisher z formula corrected twice: first to add denominators (R1), then to correct to same-sample form √(2/(N−3)) with Steiger 1980 citation (R2) |
| Section 7 (Conclusion) | Added "to our knowledge" hedge to first-application claim |
| References | Steiger (1980) added alphabetically |
| sections/04_experiments.md | N=299 corrected to N=297 |
| sections/07_conclusion.md | Hedge added (parallel to compiled paper fix) |

---

## Quality Improvements

- **Logical Consistency:** Improved — Conclusion now consistently hedges novelty claim as "to our knowledge"
- **Numerical Accuracy:** Improved — Fisher z formula now matches code implementation exactly
- **Novelty Claims:** Refined — "first" claim appropriately hedged in all locations
- **Baseline Comparison:** N/A (observational study)
- **Persuasiveness:** Unchanged (already strong)
- **BBQ Proxy Handling:** Unchanged (already exemplary)

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **BBQ proxy is ARC Challenge, not genuine BBQ** — paper acknowledges this explicitly in abstract, methodology, limitations, discussion. Prepared response: "We agree this is the principal limitation; we disclose it at every relevant point and qualify all bias-avoidance claims accordingly. Replication with HELM Lite BBQ is our top next step."

2. **N=296 is insufficient to resolve scenario classification** — paper pre-registers AMBIGUOUS as valid. Prepared response: "AMBIGUOUS is a pre-registered, scientifically informative outcome. We report it honestly and provide power analysis: N≥400–600 required. LLM LB v2 (N>1000) would resolve it."

3. **RLHF sign test is underpowered for the proxy** — acknowledged in L4. Prepared response: "The null result (p=0.686) may reflect proxy inadequacy; we frame it as hypothesis-generating."

4. **Single dataset (LLM LB v1)** — acknowledged in L5. Prepared response: "Observational cross-sectional study by design; replication with LLM LB v2 is the obvious extension."

5. **Same-sample Fisher z formula** — now correctly documented with Steiger (1980). Prepared response: "Both raw and partial correlations are estimated from the same N=296 observations; the same-sample formula is theoretically appropriate and numerically matches our implementation (z=6.9679)."

---

## Final Recommendation: CONDITIONAL ACCEPT

Paper is methodologically sound, numerically verified, and honestly reported. All FATAL and MAJOR issues resolved. Minor polish items remain in human_review_notes.md.
