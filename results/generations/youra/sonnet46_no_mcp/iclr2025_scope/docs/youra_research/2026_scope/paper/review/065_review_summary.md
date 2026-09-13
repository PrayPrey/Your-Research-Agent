# Adversarial Review Summary (v2.0)

**Paper**: Eviction-Aware LoRA: Training LoRA Adapters Under KV Cache Budget Constraints
**Hypothesis ID**: H-EvictionAwareLoRA-v1
**Review Completed**: 2026-05-04T16:30:00
**Rounds Completed**: 2
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED
**Recommendation**: CONDITIONAL_ACCEPT

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(Accuracy Checker, Bored Reviewer, Skeptical Expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 1     | 1        | 0         |
| MAJOR    | 9     | 9        | 0         |

**MINOR Issues**: 16 collected in `065_human_review_notes.md` (NOT auto-fixed)

**Key outcome**: The single FATAL issue (cosine similarity source document inconsistency) was
resolved by raw data verification — `h-e1/experiment_results.json` confirmed the paper's values
(min=−0.5781, mean=0.05271) are correct. All 9 MAJOR issues were addressed across 2 revision rounds.

---

## Persuasiveness Assessment (v2.0)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Concrete numbers, specific deployment scenario, avoids "X is important" cliché |
| Problem clear by paragraph 2? | PASS | Three-level framing (surface→deeper→gap) is clear |
| Novelty clear by page 1? | PASS | Eviction-Aware LoRA concept introduced clearly with dropout analogy |
| Figure 1 self-explanatory? | PASS | Cosine similarity plot caption is clear; gate threshold line described |
| Hook avoids "X is important"? | PASS | Opens with concrete deployment scenario, not importance claim |
| Would continue reading after abstract? | PASS | Bored Reviewer verdict: yes |
| Attention lost at? | never | Middle sections remain engaging; H-M2 flat-zero results appropriately brief |
| False novelty claims? | 0 | After M-4 fix (LongLoRA contrast added) |
| Unfair baseline comparisons? | 0 | Only sequential baseline; scope justified as mechanistic study |
| Overclaims? | 0 | After M-2 fix ("production-ready" → "validated") |
| Tone overclaiming? | 0 | After R2-M2 fix ("near-orthogonal" qualified with range) |
| Missing limitations? | 0 | All 7 limitations (L1–L7) disclosed in Section 6.2 |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy + Engagement + Skepticism)

**Accuracy Checker Findings**:
| Category | Issues Found | Resolved |
|----------|--------------|---------|
| Cosine similarity source discrepancy | 1 FATAL | Resolved (raw data verification) |
| LoRA alpha documentation inconsistency | 1 MAJOR | Fixed (note added to Section 3.3) |
| H-M1 n=5 basis not in abstract | 1 MAJOR | Fixed (qualifier added) |

**Bored Reviewer Findings**:
| Category | Issues Found | Resolved |
|----------|--------------|---------|
| n=5 omission from abstract | 1 MAJOR | Fixed (shared with AC-3) |
| "Production-ready" overclaim | 1 MAJOR | Fixed (replaced with "validated") |

**Skeptical Expert Findings**:
| Category | Issues Found | Resolved |
|----------|--------------|---------|
| "First systematic study" unverifiable | 1 MAJOR | Fixed (LongLoRA contrast added, hedge strengthened) |
| No random-mask ablation baseline | 1 MAJOR | Fixed (L7 added to Section 6.2) |
| "Production-ready" contradicted by CUDA crash | 1 MAJOR | Fixed (shared with BR-2) |
| Clark et al. BERT→GPT-2 transfer unjustified | 1 MAJOR | Fixed (encoder-only qualifier added) |
| LongLoRA ghost citation | 1 MAJOR (HRN-4) | Fixed (discussed in Section 2.2) |

**Key Issues Addressed in R1**:
1. FATAL AC-1: Cosine similarity discrepancy resolved by raw data audit — paper values confirmed correct
2. MAJOR M-1: Abstract now qualifies attention restructuring claim with "(n=5 synthetic samples, GPT-2 proxy)"
3. MAJOR M-2: "Production-ready" replaced with "validated" throughout abstract, contributions, Section 3.5
4. MAJOR M-4: LongLoRA contrast added to Section 1 and Section 2.2
5. MAJOR M-5: Random-mask ablation absence added as Limitation L7 in Section 6.2
6. MAJOR M-6: Clark et al. encoder-only qualifier added in Sections 2.3 and 6.1

### Round 2: Numerical Verification and Credibility

All R1 fixes verified as correctly applied. Two new MAJOR issues identified:

**New R2 Issues**:
| ID | Description | Resolved |
|----|-------------|---------|
| R2-M1 | Section 5.2 falsely claimed evaluation on "full KV cache"; H-M1 used H2O masks active | Fixed (evaluation condition corrected) |
| R2-M2 | "Near-orthogonal" overstated distribution uniformity (range [−0.578, +0.469]) | Fixed (qualified with range throughout) |

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Abstract | Added n=5 qualifier; replaced "production-ready"; qualified "near-orthogonal" with range | Added range [−0.578, +0.469] |
| Section 1 (Contributions) | LongLoRA contrast; n=5 in #3; "validated" in #4 | Qualified "near-orthogonal" in #2 |
| Section 2.2 | New LongLoRA paragraph | None |
| Section 2.3 | Clark et al. encoder-only qualifier | None |
| Section 3.3 | Alpha discrepancy note | None |
| Section 3.4 | Added 4th dropout difference (input-dependent masks) | None |
| Section 4.2 | Clarified synthetic sample context | None |
| Section 4.3 | Random-mask ablation absence noted | None |
| Section 5.1 | Tone adjustment on "striking" | Range added to distribution description |
| Section 5.2 | n=5 caveat added | Evaluation condition corrected (H2O masks active) |
| Section 6.1 | Clark et al. qualifier | "Near-orthogonal" qualified with mean-near-zero note |
| Section 6.2 | New L7 (random-mask ablation) | None |
| Section 7 | Infrastructure language; Interpretation A/B link | "Near-orthogonal" qualified in contributions list |

---

## Quality Improvements

- **Logical Consistency**: Improved — evaluation condition in Section 5.2 corrected
- **Numerical Accuracy**: Confirmed — all numbers match raw experiment_results.json
- **Novelty Claims**: Refined — LongLoRA contrast; "first systematic study" hedge strengthened
- **Baseline Comparison**: Contextualized — random-mask ablation absence acknowledged as L7
- **Persuasiveness**: Maintained — n=5 qualification improves credibility without killing engagement
- **Terminology**: Improved — "near-orthogonal" qualified; "production-ready" → "validated"

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **n=5 H-M1 sample size**: Now disclosed in abstract. Prepared response: "H-M1 is a mechanistic proxy validation — 5 samples establish the mechanism exists; Section 4.2 and L3 acknowledge full-scale replication is needed."

2. **H-M3 not executed**: Disclosed as L1 (Critical). Prepared response: "This is explicitly a mechanistic study; P1 accuracy claim is future work estimated at ~24 GPU-hours on A100."

3. **GPT-2 proxy validity**: Disclosed as L3. Prepared response: "H2O mask injection is architecture-agnostic (hook-based); gradient divergence is a general mechanism. Section 3.2.2 explains hook compatibility with LLaMA/Mistral."

4. **Single eviction policy**: Disclosed as L5. Prepared response: "H2O was chosen as the most studied eviction policy with clear heavy-hitter persistence properties. SnapKV and StreamingLLM generalization is future work."

5. **No random-mask ablation**: Now disclosed as L7. Prepared response: "Random-mask ablation is a natural next experiment to isolate H2O policy specificity; we acknowledge this gap explicitly."

---

## Files Generated

| File | Description |
|------|-------------|
| `paper/06_paper_final.md` | Final reviewed paper (R2 revision + review metadata) |
| `paper/review/065_review_r1.md` | Round 1 adversarial review (3-persona) |
| `paper/review/065_review_r2.md` | Round 2 numerical verification review |
| `paper/review/065_review_summary.md` | This consolidated summary |
| `paper/review/065_human_review_notes.md` | 16 MINOR issues for human review |
| `paper/review/065_changelog.md` | Complete change history |
| `paper/review/065_review_checkpoint.yaml` | Review state tracking |
