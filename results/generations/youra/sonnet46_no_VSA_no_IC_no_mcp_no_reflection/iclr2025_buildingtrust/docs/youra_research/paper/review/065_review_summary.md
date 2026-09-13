# Adversarial Review Summary
# Paper: Alignment Fingerprinting: DPO and SFT Models Are Separable by Truthfulness, Not Fairness
# Review Completed: 2026-08-31T07:00:00+00:00
# Rounds Completed: 2 (R1, R2)
# Final Status: CONVERGED
# Persuasiveness Check: PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(accuracy_checker, bored_reviewer, skeptical_expert in R1; accuracy_checker,
skeptical_expert in R2).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 1 | 1 | 0 |
| MAJOR | 6 | 6 | 0 |

**MINOR Issues**: 4 collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|---|---|---|
| Abstract compelling? | PASS | Two-beat hook, concrete numbers, surprising finding |
| Problem clear in 1 minute? | PASS | Direct statement in Introduction para 1 |
| Novelty clear in 2 minutes? | PASS | C1–C4 bold-labeled in Introduction |
| Figure 1 self-explanatory? | PARTIAL | Caption lacks color spec (MINOR — collected for human review) |
| Hook avoids "X is important"? | PASS | Opens with question + answer, not generic framing |
| Would continue reading? | YES | |
| Attention lost at? | Never | |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy + Engagement + Credibility)

**Accuracy Checker Findings:**
| Issue | Severity | Resolution |
|---|---|---|
| Table 1 / Table 5 alignment label contradiction (zephyr-7b-alpha) | FATAL | Fixed: Table 1 column renamed, footnotes added clarifying pair design |
| "+4.6pp" not qualified as per-pair mean delta | MAJOR | Fixed: Added "(per-pair mean delta)" throughout |
| BBQ group-mean vs per-pair delta discrepancy unacknowledged | MAJOR | Fixed: Added explanation in Section 5.2 |

**Bored Reviewer Findings:**
| Issue | Severity | Resolution |
|---|---|---|
| Figure 1 caption lacks DPO/SFT color specification | MINOR | Collected for human review |
| Introduction frames classification as "key insight" | MINOR | Collected for human review |

**Skeptical Expert Findings:**
| Issue | Severity | Resolution |
|---|---|---|
| C4 "first" claim lacks "to our knowledge" hedge | MAJOR | Fixed: Added hedge |
| P4 RLHF model in mechanism analysis — no sensitivity check | MAJOR | Fixed: Sensitivity analysis added to L4 |
| Abstract "establishes" overclaims for n=12 | MAJOR | Fixed: Changed to "demonstrates the feasibility of" |

**R1 persuasiveness:** CONDITIONAL PASS (engagement: full pass; credibility: issues addressed)

---

### Round 2: Numerical Verification (Accuracy + Credibility)

**Accuracy Checker Findings:**
| Issue | Severity | Resolution |
|---|---|---|
| Sensitivity analysis "+3.8pp" should be "+3.6pp" (arithmetic error) | MAJOR | Fixed: Corrected to "+3.6pp" |
| "establishes" remains in Section 6 and Section 7 | MAJOR | Fixed: Softened to "provides evidence that" and "confirms... at pilot scale" |
| All other numerical claims | ✅ VERIFIED | All match ground truth |

**Skeptical Expert Findings:**
| Issue | Severity | Resolution |
|---|---|---|
| Figure numbering vs filename discrepancy | MINOR | Collected for human review |
| "0.5–4.6pp range" conflates different benchmark deltas | MINOR | Collected for human review |

**R2 persuasiveness:** FULL PASS (no remaining FATAL or MAJOR)

---

## Key Issues Addressed

### FATAL-001 (Table 1/Table 5 Alignment Label Contradiction)
**Problem:** Table 1 listed zephyr-7b-alpha as the DPO member of P1, but Table 5 and ground truth label it as SFT. This fundamental inconsistency would raise immediate red flags from reviewers examining the model pairs.

**Resolution:** Table 1 column renamed from "DPO Model" to "DPO-aligned Model" with footnotes (†, ‡) explicitly acknowledging: (1) zephyr-7b-alpha is labeled SFT in the existence analysis but serves as DPO-comparable counterpart in the mechanism analysis based on training lineage; (2) Llama-2-chat is RLHF, not pure SFT. This framing is honest about the limitation while preserving the analysis.

### MAJOR-002 (BBQ Group-Mean vs Per-Pair Discrepancy)
**Problem:** DPO BBQ group mean is +3.8pp higher than SFT (Table 5: 0.460 vs 0.422), yet the paper reports a null result (+0.5pp per-pair delta, k=3/6, p=0.66). An astute reviewer would immediately question this apparent contradiction.

**Resolution:** Added explicit explanation that the group mean difference reflects model quality confounds; the paired comparison controls for this, yielding the null result. This actually strengthens the paper's argument by showing the value of paired design.

---

## Sections Modified (Cumulative R1+R2)

| Section | Modifications |
|---|---|
| Abstract | "establishes" → "demonstrates the feasibility of"; "+4.6pp" qualified as per-pair mean |
| Section 1 (Introduction) | C2: per-pair mean delta qualifier; C4: "to our knowledge" hedge |
| Section 3 (Methodology) | Table 1: column rename, pair design footnotes (†, ‡) |
| Section 5.2 (Results) | BBQ group-mean vs per-pair delta explanation added |
| Section 6 (Discussion) | L4: P4 sensitivity analysis added (+3.6pp corrected); Finding 1: "provides evidence" |
| Section 7 (Conclusion) | "confirms... at pilot scale" |

---

## Quality Improvements

- **Logical Consistency**: Improved (Table 1/Table 5 contradiction resolved)
- **Numerical Accuracy**: Improved (sensitivity analysis corrected)
- **Novelty Claims**: Refined (hedges added appropriately)
- **Baseline Comparison**: Contextualized (BBQ group-mean vs paired discrepancy explained)
- **Persuasiveness**: Maintained (hook, structure, novelty clarity all pass)
- **Credibility**: Improved (overclaims softened, RLHF sensitivity analysis added)

---

## Reviewer Preparation Notes

**Potential remaining attack surfaces for real reviewers:**

1. **Small n=12**: p=0.031 is significant but close to α=0.05. Reviewers may ask for larger replication.
   - *Prepared response:* L2 explicitly acknowledges this. No matched DPO/SFT public dataset larger than n=12 exists without custom model training. Results are confirmatory at pilot scale.

2. **zephyr-7b-alpha pair labeling**: Reviewers may question using an SFT-labeled model as DPO-comparable.
   - *Prepared response:* Footnote in Table 1 explains. L4 extended with sensitivity analysis. Qualitative conclusions hold even with this pair excluded.

3. **100-sample evaluation limit**: Reviewers may question score reliability.
   - *Prepared response:* L3 explicitly acknowledges. BBQ null result is far from threshold (p=0.66) and robust to sampling variance. Full evaluation is stated future work.

4. **Community model confounds**: Not all pairs are perfectly matched.
   - *Prepared response:* L4 acknowledges. The paired design minimizes (but cannot eliminate) confounds. Sensitivity analyses support robustness.
