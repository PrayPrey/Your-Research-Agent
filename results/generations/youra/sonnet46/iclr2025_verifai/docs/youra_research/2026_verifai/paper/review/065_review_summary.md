# Adversarial Review Summary (v2.0)

**Paper:** Architecture Determines Calibration Direction: Difficulty-Stratified P(True) Fingerprinting for LLM Code Verifiers
**Hypothesis:** H-CalibDiff-v1
**Review Completed:** 2026-03-23
**Rounds Completed:** 2 (R1: Accuracy and Engagement; R2: Numerical Verification)
**Final Status:** CONVERGED (CONDITIONAL_ACCEPT)
**Persuasiveness Check:** PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (Accuracy Checker, Bored Reviewer, Skeptical Expert) in Round 1 and two-persona analysis (Accuracy Checker, Skeptical Expert) in Round 2 with mandatory Serena MCP numerical verification.

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 0     | 0        | 0         |
| MAJOR    | 5     | 5        | **0**     |

**MINOR Issues:** 6 collected in `065_human_review_notes.md` (NOT auto-fixed)

**Convergence criteria met:**
- ✅ FATAL issues = 0
- ✅ MAJOR issues = 0 (all resolved)
- ✅ Persuasiveness passed (bored reviewer would continue reading)
- ✅ Rounds completed ≥ min_rounds (2 ≥ 2)

---

## Persuasiveness Assessment (v2.0)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✅ PASS | After R1 fix: hook moved to abstract opening |
| Problem clear by paragraph 2? | ✅ PASS | Three-level framing (surface/deeper/gap) is clear |
| Novelty clear by page 1? | ✅ PASS | Architecture-dependent ΔECE stated explicitly in Introduction |
| Figure 1 self-explanatory? | ⚠️ CANNOT ASSESS | No figure caption text in source files (7 figures referenced) |
| Hook avoids "X is important"? | ✅ PASS (after R1) | "When a language model fails..." replaces generic opener |
| Would bored reviewer continue? | ✅ YES | Three-direction finding (+0.298, −0.249, ≈0) is genuinely surprising |
| Attention lost at? | §5.5 (M-stability) | "Exactly stable" without explanation; collected in human_review_notes |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy + Engagement)

**Accuracy Checker Findings:**
| Category | Issues |
|----------|--------|
| Claim-Evidence Mismatch | 0 |
| Numerical Inconsistency | 0 (all ΔECE/ECE/T* values verified correct) |
| Baseline Comparison Fairness | 0 (measurement study, no algorithmic baselines) |

**Bored Reviewer Findings:**
| Category | Issues |
|----------|--------|
| Hook Quality | 1 MAJOR (abstract opening — fixed) |
| Clarity Issues | 3 MINOR (collected in human_review_notes) |
| Engagement Problems | 0 |

**Skeptical Expert Findings:**
| Category | Issues |
|----------|--------|
| Novelty Questions | 0 (novelty is modest but valid measurement study) |
| Methodology Concerns | 1 MAJOR (base model P(True) validity — fixed with L5) |
| Mechanism Overclaim | 1 MAJOR (Contribution 3 reframed to "exploratory hypothesis") |
| Missing Limitations | 0 (L5 now added) |

**R1 Key Issues Addressed:**
1. **MAJOR-001 (Abstract hook):** First sentence now opens with concrete question per narrative blueprint design
2. **MAJOR-002 (Mechanism overclaim):** Contribution 3 reframed as "observations consistent with training-data composition hypothesis" with explicit "(exploratory, N=1 per category)" qualifier
3. **MAJOR-003 (Base model P(True) validity):** Added "Base model applicability" rationale in §3.2 and new L5 limitation in §6.4

### Round 2: Numerical Verification (Serena MCP — MANDATORY)

**Serena MCP searches performed:** 7
**Files accessed:** h-m4/04_validation.md, h-m3/04_validation.md, h-m2/04_validation.md, h-e1/04_validation.md

**Accuracy Checker Findings (Serena Verified):**
| Category | Issues |
|----------|--------|
| Primary ΔECE values | 0 (all verified correct) |
| ECE(hard)/ECE(easy) values | 0 (verified correct) |
| Temperature scaling T* and post-T values | 0 (verified correct) |
| std(c), mean(c) values | 0 (verified correct) |
| Coverage, consensus hard | 0 (verified correct) |
| **Jaccard pair assignments** | **1 MAJOR (swapped — fixed)** |
| **Per-benchmark tier sizes** | **1 MAJOR (wrong values — fixed)** |

**R2 Key Issues Addressed:**
1. **MAJOR-R2-001 (Jaccard table):** Llama3∩CodeLlama (0.456→0.546) and CodeLlama∩DeepSeek (0.546→0.456) corrected; Serena-verified against h-m2/04_validation.md
2. **MAJOR-R2-002 (Tier sizes Table 5.1.1):** All 12 per-benchmark values corrected to h-e1 actual data; combined totals in main Table 1 remain correct

---

## Sections Modified

| Section | Round | Modifications |
|---------|-------|---------------|
| Abstract | R1 | Opening sentence rewritten with concrete question hook |
| Introduction (Contribution 3) | R1 | "Evidence that..." → "Observations consistent with...hypothesis" + exploratory qualifier |
| §3.2 Methodology | R1 | Added "Base model applicability" paragraph |
| §5.1.1 Results (Table) | R2 | Per-benchmark tier sizes corrected to h-e1 actual values |
| §5.1.3 Results (Table) | R2 | Jaccard pair assignments corrected (swapped values fixed) |
| §6.4 Limitations | R1 | Added L5: Base model P(True) validity limitation |
| Conclusion (item 3) | R1 | Reframed mechanism claim to "observations consistent with hypothesis" |

---

## Quality Improvements

- **Logical Consistency:** Improved (mechanism claim now matches Discussion's hedged framing)
- **Numerical Accuracy:** Improved (Jaccard pair assignments and per-benchmark tier sizes corrected)
- **Novelty Claims:** Unchanged (already modestly stated; confirmed valid measurement study)
- **Baseline Comparison:** Unchanged (measurement study with appropriate null/temperature baselines)
- **Persuasiveness:** Improved (concrete hook now leads Abstract)
- **Methodological Transparency:** Improved (base model P(True) validity explicitly addressed)

---

## Reviewer Preparation Notes

Potential attack surfaces for real reviewers and prepared responses:

1. **"Why use base models for P(True)? Kadavath et al. used instruction-tuned models."**
   → Addressed in L5: deliberate choice to isolate pre-training calibration; weak-but-significant correlation (r=0.14–0.20, p<10⁻¹⁰) confirms non-trivial signal in base models; future work with instruction-tuned variants explicitly planned.

2. **"Only 3 models, one per category — how do you know this generalizes?"**
   → Addressed in L3: explicitly framed as exploratory (N=1 per category); future work section recommends N≥2 per category (Mistral-7B, WizardCoder-7B, DeepSeek-33B). Results are directional signals, not confirmatory.

3. **"CodeLlama easy tier n=37 is very small for M=15 ECE bins."**
   → Addressed in L2: effect size (−0.249) is large; CI entirely negative; direction robust. Magnitude confirmation requires larger k. The paper explicitly acknowledges this.

4. **"The mechanism (training data composition) is not proven — you're speculating."**
   → After R1 fix: Contribution 3 now explicitly says "observations consistent with hypothesis" and "exploratory." Discussion §6.2 already hedged appropriately. The speculation is acknowledged.

5. **"Global temperature scaling analysis — you're using the same data for fitting and reporting."**
   → §3.3 explicitly states: "T* fitted on 20% holdout, recomputed on remaining 80%." Proper train/test split for temperature scaling. ✅

---

## Final Output Files

| File | Path | Description |
|------|------|-------------|
| Final Paper | `paper/06_paper_final.md` | R2-revised and reviewed paper |
| Review Summary | `paper/review/065_review_summary.md` | This file |
| Human Review Notes | `paper/review/065_human_review_notes.md` | 6 MINOR issues for human review |
| Changelog | `paper/review/065_changelog.md` | Detailed change history (R1 + R2) |
| R1 Review | `paper/review/065_review_r1.md` | Round 1 adversarial review |
| R2 Review | `paper/review/065_review_r2.md` | Round 2 adversarial review (Serena verified) |
| Checkpoint | `paper/review/065_review_checkpoint.yaml` | Final state |

---

*Phase 6.5 Adversarial Review v2.0 — COMPLETE*
*Next Phase: Phase 6.5.1 (Overleaf LaTeX/PDF generation)*
