# Adversarial Review Summary (v2.0)

**Paper**: Alignment Changes Answers, Not Just Confidence: Mechanistic Discrimination of RLHF Miscalibration
**Review Completed**: 2026-03-15T09:30:00Z
**Rounds Completed**: 2 (R1 + R2)
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED
**Recommendation**: CONDITIONAL_ACCEPT (pending human review of minor notes)

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(accuracy_checker, bored_reviewer, skeptical_expert). All blocking issues were resolved.

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 2     | 2        | 0         |
| MAJOR    | 9     | 9        | 0         |

**MINOR Issues**: 26 items collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment (v2.0)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Opens with specific striking statistic (99.7%, ρ = −0.324); immediately answers "so what" |
| Problem clear by paragraph 2? | PASS | H1/H2/H3 framing makes the problem concrete and discriminable |
| Novelty clear by page 1? | PASS | Pre-registered mechanistic discrimination framed as the novel contribution; well positioned vs. Xie et al. 2024 |
| Figure 1 self-explanatory? | N/A | No visual Figure 1 in the paper (figures are referenced as .png files); first figure is Figure 1: ΔBrier Reliability bar chart — caption is clear |
| Hook avoids "X is important"? | PASS | Opening sentence is concrete and counterintuitive, not generic |
| Would bored reviewer continue reading? | PASS | Abstract + Introduction are genuinely engaging; attention was temporarily lost at Table 2 (now fixed) |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review
**Focus**: Accuracy and Engagement

**Accuracy Checker Findings** (Persona 1):
| Category | Issues Found | Issues Resolved |
|----------|-------------|----------------|
| Table completeness (missing SFT rows) | 1 MAJOR | 1 resolved |
| Metric conflation (ΔECE vs ΔBrier Reliability) | 1 MAJOR | 1 resolved (partial — structural fix applied) |
| Pre-registration failure labeling | 1 MAJOR | 1 resolved |

**Bored Reviewer Findings** (Persona 2):
| Category | Issues Found | Issues Resolved |
|----------|-------------|----------------|
| Table 2 credibility at first-results moment | 1 MAJOR | 1 resolved |

**Skeptical Expert Findings** (Persona 3):
| Category | Issues Found | Issues Resolved |
|----------|-------------|----------------|
| "Definitively" overclaiming for single-family study | 1 MAJOR | 1 resolved |
| DPO ≥ PPO contribution framing vs. fallback checkpoints | 1 MAJOR | 1 resolved |
| H-M2/H-M3 evidence non-independence | 1 MAJOR | 1 resolved |

**Key R1 Fixes Applied**:
1. Added SFT rows to Table 2; separated ΔECE and ΔBrier Reliability columns
2. Replaced "definitively refuted/excluded" with "in the Pythia family, we find..." scoped language throughout
3. Pre-registration prediction (PPO ≥ DPO) explicitly labeled as falsified
4. DPO ≥ PPO finding reframed as "exploratory observation" with checkpoint caveat elevated
5. Added clarifying note on H-M2/H-M3 non-independence in Section 3.5

---

### Round 2: Numerical Verification (Serena MCP)
**Focus**: Mathematical validity and baseline fairness

**Serena MCP Verification**: 10 searches performed across h-e1, h-m1, h-m2, h-m3 validation files.

**Accuracy Checker Findings** (Persona 1):
| Category | Issues Found | Issues Resolved |
|----------|-------------|----------------|
| Incorrect Spearman ρ values in Table 3 (6 of 9 wrong vs. experiment_results.json) | 1 FATAL | 1 resolved |
| Table 2 ECE_aligned values do not match h-e1 actual data | 1 FATAL | 1 resolved |

**Key R2 Fact**: Despite incorrect specific ρ values in the original paper, the **core H2 conclusion is preserved** with the corrected values — all 9 pairs still fall below 0.90, and 8/9 still fall below 0.85. The scientific finding is robust.

**Skeptical Expert Findings** (Persona 2):
| Category | Issues Found | Issues Resolved |
|----------|-------------|----------------|
| DPO > PPO at 2.8B not statistically distinguishable (overlapping CIs) | 1 MAJOR | 1 resolved |
| Approximate argmax rates (~%) inconsistent with exact partition counts | 1 MAJOR | 1 resolved |

**Key R2 Fixes Applied**:
1. Table 3: 6 incorrect Spearman ρ values corrected to experiment_results.json authoritative values
2. Table 3: Approximate argmax change rates replaced with exact counts from h-m3/04_validation.md
3. Table 2: ECE_aligned and ΔECE values corrected to match h-e1/04_validation.md actuals
4. Added statistical qualification: "2.8B DPO/PPO difference not statistically distinguishable (overlapping 95% CIs)"
5. Added shot-count asymmetry caveat for H3 diagnostic (MMLU 4-shot vs TruthfulQA 0-shot)

---

## Sections Modified (All Rounds)

| Section | Modifications |
|---------|---------------|
| Abstract | Scoped "definitively" language; Spearman ρ claim preserved (all 9 < 0.90) |
| Section 1 (Introduction) | Contribution 2 reframed as observation; pre-registration failure labeled |
| Section 3.4 | Explicit ΔECE vs. ΔBrier Reliability distinction added |
| Section 3.5 | H-M2/H-M3 non-independence clarified; MMLU/TruthfulQA shot asymmetry noted |
| Section 3.6 | H-M3 gate marked FAILED (H1 not confirmed — scientifically desired) |
| Section 4.3 | "Theoretical" pressure gradient hedged |
| Section 5.1 / Table 2 | SFT rows added; ECE_aligned corrected; ΔECE and ΔBrier Reliability properly separated |
| Section 5.2 | Pre-registration falsification explicit; 2.8B CI overlap qualified; DPO ordering labeled exploratory |
| Section 5.3 / Table 3 | All 6 incorrect ρ values corrected; argmax rates updated to exact counts |
| Section 5.4 | "Definitively excluded" scoped to softmax-ECE setting |
| Section 6.1 | All three findings properly scoped to Pythia family |
| Section 7 (Conclusion) | Pre-reg failure explicit; 2.8B qualification added |

---

## Quality Improvements

- **Logical Consistency**: Significantly improved (pre-registration failure disclosed, SFT rows added)
- **Numerical Accuracy**: Significantly improved (6 ρ values corrected, ECE values corrected)
- **Novelty Claims**: Refined (scoped to Pythia family, "definitively" removed)
- **Baseline Comparison**: N/A (within-family paired design; no external baseline comparison issues)
- **Persuasiveness**: Improved (Table 2 now complete and credible at first-results moment)
- **Statistical Rigor**: Improved (2.8B DPO/PPO CI overlap now disclosed)

---

## Remaining Attack Surfaces for Real Reviewers

The following are acknowledged limitations that may draw reviewer questions:

1. **Single model family (Pythia 1.4B–6.9B)**: Cannot generalize H2 dominance to LLaMA-2, Mistral, Falcon.
   - *Prepared response*: Pythia provides the only clean controlled experiment (identical pretraining); the framework is explicitly designed to be reusable on any family via lm-eval. 6.9B-DPO near-threshold behavior motivates cross-family replication.

2. **Fallback checkpoints (Risk R1)**: Primary RLHFlow checkpoints unavailable.
   - *Prepared response*: H2 finding (0/9 ρ ≥ 0.90) would require implausibly consistent misconfiguration across all 9 pairs to overturn. DPO ≥ PPO ordering is explicitly labeled as checkpoint-level observation.

3. **H-M4 not executed**: ATS correctability for H2 remains untested.
   - *Prepared response*: Explicitly noted in Limitations (Section 6.4); framed as motivated future work. ATS interpretation in Section 6.2 is clearly labeled as untested mechanistic interpretation.

4. **Spearman ρ on n=4 vectors**: Low per-item statistical power.
   - *Prepared response*: Per-item ρ on n=4 has limited power individually; the aggregation over 14,042 items provides robust estimates. This is noted in human_review_notes for potential addition to methodology.

5. **MMLU 4-shot vs TruthfulQA 0-shot asymmetry**: H3 diagnostic comparison is not perfectly controlled for shot count.
   - *Prepared response*: Added caveat in Section 3.5 acknowledging this; H3 remains falsified (all ratios < 1.0) even with shot-count confound, since the confound would predict TruthfulQA doing relatively better (0-shot harder), strengthening H3 falsification.

---

## Final Verdict

**CONVERGED** after 2 rounds. The paper's core scientific contribution — pre-registered mechanistic discrimination identifying H2 (decision-boundary restructuring) as the dominant mechanism of RLHF-induced miscalibration in Pythia 1.4B–6.9B — is:

- **Numerically accurate** after corrections (verified against actual experiment files)
- **Appropriately scoped** (single-family claims, fallback checkpoint caveats)
- **Engaging** (concrete hook, clear novelty positioning, compelling statistical result)
- **Honest about limitations** (4 explicit limitations in Section 6.4)

Minor issues (26 items) are collected in `065_human_review_notes.md` for human final polish.
