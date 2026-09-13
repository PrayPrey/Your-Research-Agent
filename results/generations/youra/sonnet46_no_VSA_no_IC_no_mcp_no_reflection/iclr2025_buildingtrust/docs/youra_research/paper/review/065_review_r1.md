# Adversarial Review — Round 1
# Focus: Accuracy and Engagement (Three-Persona)
# Date: 2026-08-31T06:10:00+00:00

---

## Ground Truth Summary

| Metric | Ground Truth Value | Source |
|---|---|---|
| LOO-CV accuracy (k=1) | 83.3% (10/12) | h-e1/04_validation.md |
| Permutation p-value | 0.031 (n=1000, seed=42) | h-e1/04_validation.md |
| TruthfulQA Fisher | 0.8122 | h-m1/04_validation.md |
| WinoGender Fisher | 0.0856 | h-m1/04_validation.md |
| WinoGrande Fisher | 0.0312 | h-m1/04_validation.md |
| BBQ Fisher | 0.0091 | h-m1/04_validation.md |
| TruthfulQA per-pair mean delta | +0.0460 (+4.6pp) | h-m1/04_validation.md |
| BBQ per-pair mean delta | +0.0050 (+0.5pp) | h-m1/04_validation.md |
| BBQ k_positive | 3/6 | h-m1/04_validation.md |
| BBQ p-value | 0.6562 | h-m1/04_validation.md |
| WinoGender k_positive | 4/6 | h-m1/04_validation.md |
| WinoGender p-value | 0.3438 | h-m1/04_validation.md |
| zephyr-7b-alpha alignment | **SFT** | h-e1/04_validation.md, ground_truth |

---

## Executive Summary

| Severity | Count |
|---|---|
| FATAL | 1 |
| MAJOR | 5 |
| MINOR | 2 |

**Recommendation:** REVISE — Fix FATAL-001 (table error) and MAJOR issues before R2.

---

## FATAL Issues

### FATAL-001: Table 1 / Table 5 Alignment Label Contradiction for zephyr-7b-alpha

**Location:** Section 3 (Table 1), Section 5.1 (Table 5)

**Issue:** Table 1 (Model pairs, Section 3) lists the model pair for P1 as:
- SFT column: `Mistral-7B-Instruct-v0.1`
- DPO column: `zephyr-7b-alpha`

However, Table 5 (12×4 benchmark score matrix, Section 5.1) labels `zephyr-7b-alpha` as alignment=**SFT** with SFT group contribution. The ground truth (065_ground_truth.yaml and h-e1/04_validation.md) also confirms: `HuggingFaceH4/zephyr-7b-alpha` → alignment=SFT.

**Impact:** If zephyr-7b-alpha is SFT, then P1 has two SFT models, which means the pair design is wrong. This would reduce the valid DPO/SFT pairs. Alternatively, the Table 5 SFT label for zephyr-alpha is wrong and it should be DPO — but ground truth contradicts this. This must be investigated and corrected.

**Most likely resolution:** zephyr-7b-alpha was trained by HuggingFace as an SFT model (the "alpha" before DPO fine-tuning to get "beta"). The pair P1 may be mislabeled in Table 1, or Table 1 is describing the pair differently than the raw alignment labels. The paper must clarify the pair construction logic explicitly.

**Fix:** Verify actual alignment labels for all 12 models and ensure Table 1 and Table 5 are consistent. Add a note explaining zephyr-alpha/beta training lineage if they are indeed SFT/DPO respectively.

---

## MAJOR Issues

### MAJOR-001: "+4.6pp" not qualified as per-pair mean delta vs group mean

**Location:** Abstract, Introduction, Section 5.2, Section 7

**Issue:** The paper states "DPO models score +4.6pp higher on truthfulness on average." The +4.6pp (+0.046) is the per-pair mean delta from the h-m1 paired analysis. The group mean difference is only +1.1pp (DPO mean 0.534 − SFT mean 0.523 = 0.011). These are different statistics and the paper uses "on average" ambiguously.

A reviewer who computes the group mean difference from Table 5 will get +1.1pp, not +4.6pp, and conclude the paper has an error. The paired mean is more appropriate for the paired design, but it must be labeled as such.

**Fix:** Change "DPO models score +4.6pp higher on truthfulness on average" to "DPO models score +4.6pp higher on truthfulness on average across matched pairs (per-pair mean delta)."

---

### MAJOR-002: BBQ group mean discrepancy not acknowledged

**Location:** Section 5.2, Table 7

**Issue:** Table 5 shows DPO BBQ mean=0.460, SFT BBQ mean=0.422, difference=+3.8pp. Yet Table 7 reports mean_BBQ_delta=+0.005 (per-pair). This discrepancy (+3.8pp group mean vs +0.5pp per-pair) is large and unexplained. A skeptical reviewer will notice that the "null result" on BBQ is contradicted by the group means in Table 5.

The explanation is that the paired structure matters — when you pair models, the BBQ advantage collapses. But this is never explained in the paper. The discrepancy implies the group mean difference is driven by confounding (different base models, model quality differences across DPO/SFT pool), not alignment strategy. This actually strengthens the paper's argument if explained properly.

**Fix:** Add a sentence in Section 5.2 explaining: "Although DPO models have higher mean BBQ score (+3.8pp group mean; Table 5), the paired comparison reveals this is driven by model quality confounds rather than alignment strategy: per-pair delta = +0.005pp (k=3/6, p=0.66), indicating no systematic DPO advantage once base model is controlled."

---

### MAJOR-003: C4 "first" claim lacks epistemic hedge

**Location:** Introduction, Contribution C4

**Issue:** C4 states "our results — the first paired DPO/SFT comparison on a unified fairness-inclusive trustworthiness suite." The word "first" is a strong absolute claim. Without exhaustive literature review, this cannot be guaranteed. Should be hedged.

**Fix:** Add "to our knowledge" — "our results — to our knowledge, the first paired DPO/SFT comparison..."

---

### MAJOR-004: P4 RLHF model in mechanism analysis — no sensitivity analysis

**Location:** Section 5.2, Table 7 (h-m1 results)

**Issue:** Pair P4 pairs `Llama-2-7b-chat (RLHF)` as the SFT member vs `neural-chat-7b-v3-1` as the DPO member. Llama-2-chat is RLHF-trained, which the paper acknowledges makes it "an outlier among SFT models" (Section 5.1). Using an RLHF model as the SFT baseline in the mechanism analysis may distort the per-pair deltas.

P4 contributes: BBQ Δ=+0.05, WinoGender Δ=+0.01, WinoGrande Δ=+0.06, TruthfulQA Δ=+0.097 (DPO higher). Removing P4 would change k_TruthfulQA from 4/6 to 3/5 and mean TruthfulQA delta from +0.046 to ~+0.038. The qualitative conclusion holds, but the paper should report this sensitivity check.

**Fix:** Add a sensitivity analysis in Section 5.2 or Section 6 (Limitations): "Excluding P4 (RLHF model) from the paired mechanism analysis yields k_TruthfulQA=3/5 pairs with DPO higher, mean delta=+X.Xpp — the qualitative conclusions are unchanged."

---

### MAJOR-005: Abstract "establishes" overclaims for n=12

**Location:** Abstract, final sentence of first paragraph

**Issue:** "These results establish practical alignment auditing from public leaderboard data while challenging..." The word "establishes" implies definitive proof. With n=12 models and p=0.031 (close to α=0.05), this is pilot-scale evidence. The paper itself acknowledges this in L2 (Section 6).

**Fix:** Replace "establish" with "demonstrate the feasibility of" — "These results demonstrate the feasibility of practical alignment auditing from public leaderboard data while..."

---

## MINOR Issues (Collected for Human Review)

### MINOR-001: Figure 1 caption lacks color specification

**Location:** Figure Captions section

**Issue:** Figure 1 caption does not specify which color represents DPO vs SFT. Figure 2 caption correctly says "DPO (blue) and SFT (orange)" but Figure 1 does not.

**Fix:** Add "(DPO: blue, SFT: orange)" to Figure 1 caption.

---

### MINOR-002: Introduction frames classification as "key insight"

**Location:** Section 1, paragraph 4

**Issue:** "Our key insight is that alignment strategy can be treated as a binary classification problem over public benchmark score vectors." The classification framing is the method, not the insight. The actual insight is the truthfulness finding. This framing may mislead readers about the paper's contribution.

**Suggested revision:** "Our approach treats alignment strategy as a binary classification problem over public benchmark score vectors — a framing that lets us not only test whether fingerprinting is possible, but identify which dimension carries the signal."

---

## Persuasiveness Assessment

| Check | Result | Notes |
|---|---|---|
| Abstract compelling? | PASS | Two-beat hook, concrete numbers, surprising finding |
| Problem clear in 1 minute? | PASS | Direct statement in first paragraph |
| Novelty clear in 2 minutes? | PASS | C1-C4 contributions bold-labeled |
| Figure 1 self-explanatory? | PARTIAL | Caption lacks color specification (MINOR-001) |
| Would continue reading? | YES | |
| Attention lost at? | Never | |
| False novelty claims? | 1 (MAJOR-003) | "first" without hedge |
| Unfair baseline comparisons? | 0 | Permutation test is correct baseline |
| Overclaims? | 1 (MAJOR-005) | "establishes" in abstract |
| Tone overclaiming? | 0 | Generally appropriate hedging |
| Missing limitations? | 1 (MAJOR-004) | P4 RLHF sensitivity analysis missing |

**Persuasiveness verdict: CONDITIONAL PASS** — passes on engagement but has addressable credibility issues (MAJOR-003, MAJOR-005) that would attract reviewer criticism.

---

## Ground Truth Verification Log

| Claim | Paper Value | Ground Truth | Status |
|---|---|---|---|
| LOO-CV accuracy | 83.3% (10/12) | 83.3% (10/12) | ✅ MATCH |
| Permutation p-value | 0.031 | 0.031 | ✅ MATCH |
| TruthfulQA Fisher | 0.8122 | 0.8122 | ✅ MATCH |
| WinoGender Fisher | 0.0856 | 0.0856 | ✅ MATCH |
| BBQ Fisher | 0.0091 | 0.0091 | ✅ MATCH |
| TruthfulQA mean delta | +4.6pp | +0.0460 | ✅ MATCH |
| BBQ k, p | 3/6, 0.66 | 3/6, 0.6562 | ✅ MATCH |
| WinoGender k, p | 4/6, 0.34 | 4/6, 0.3438 | ✅ MATCH |
| k=3 sensitivity | 75.0% | 0.750 | ✅ MATCH |
| k=5 sensitivity | 66.7% | 0.667 | ✅ MATCH |
| zephyr-7b-alpha label in Table 5 | SFT | SFT | ✅ MATCH |
| zephyr-7b-alpha label in Table 1 | DPO (WRONG) | SFT | ❌ MISMATCH → FATAL-001 |

---

## Summary for Revision Agent

**Priority 1 (FATAL — must fix):**
1. FATAL-001: Fix Table 1 / Table 5 alignment label contradiction for zephyr-7b-alpha. Determine true alignment labels for all 12 models and make tables consistent.

**Priority 2 (MAJOR — must fix):**
2. MAJOR-001: Qualify "+4.6pp" as "per-pair mean delta" throughout.
3. MAJOR-002: Explain BBQ group mean (+3.8pp) vs per-pair delta (+0.5pp) discrepancy in Section 5.2.
4. MAJOR-003: Add "to our knowledge" to C4 "first" claim.
5. MAJOR-004: Add P4 RLHF sensitivity analysis to Section 5.2 or Section 6.
6. MAJOR-005: Change "establishes" to "demonstrates the feasibility of" in abstract.

**Priority 3 (MINOR — collect for human review):**
7. MINOR-001: Figure 1 caption color specification.
8. MINOR-002: Introduction "key insight" framing reword.
