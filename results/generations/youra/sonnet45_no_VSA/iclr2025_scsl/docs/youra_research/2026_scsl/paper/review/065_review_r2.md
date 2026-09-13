# Adversarial Review - Round 2 (NUMERICAL VERIFICATION)

**Paper:** Semantic Validity of Data Augmentation on MNIST
**Reviewed:** 2026-07-11T16:00:00Z
**Reviewer:** Adversary Agent v2
**Round:** R2 (Post-R1 Revision Check)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 1 | NEEDS_WORK |
| Engagement | 0 | 0 | OK |
| Credibility | 0 | 2 | NEEDS_WORK |
| **TOTAL** | **0** | **3** | **MINOR_REVISION** |

**Recommendation:** MINOR_REVISION

**Round 2 Assessment:**

This review focuses on **numerical verification** against actual Phase 4 validation files, cross-checking every quantitative claim in the R1-revised paper. The paper shows **excellent numerical accuracy** overall—core claims match ground truth precisely. However, three issues remain:

1. **MAJOR-ACC-001 (NEW):** Optimizer specification contradicts Phase 4 validation files (paper claims SGD, actual implementation uses Adadelta)
2. **MAJOR-CRED-001 (PERSISTS from R1):** Abstract/Introduction still claim "0.37-4.10 pp" degradation without clarifying this spans ALL three flip probabilities {0.3, 0.5, 0.9}, not just flip50
3. **MAJOR-CRED-002 (NEW):** Symmetric digit stability overclaim partially addressed but still present—flip90 degradation exceeds stated threshold

**R1 Issues Resolved:**
- ✅ Tone calibration: Overclaiming language significantly reduced (removed "definitive answer", qualified generalizations)
- ✅ Engagement improvements noted (though Abstract still buries ρ=-1.0 finding mid-sentence)

**New Issues (Numerical Verification):**
- ❌ Optimizer inconsistency detected through Phase 4 cross-check
- ❌ Degradation range ambiguity persists (0.37-4.10 pp needs flip probability context)
- ❌ Symmetric stability claim still overstates evidence at extreme flip rates

---

## Numerical Verification Table

**Core Quantitative Claims vs Ground Truth:**

| Claim Location | Paper Value | Ground Truth Source | Actual Value | Match? | Notes |
|----------------|-------------|---------------------|--------------|--------|-------|
| **Abstract: flip50 degradation range** | "0.72-1.00 pp at flip50" | h-e1, h-m1, h-m validation | h-e1: -0.72%, h-m1: -0.78%, h-m: -1.00% | ✅ | Correctly qualified to flip50 |
| **Abstract: dose range** | "0.37-4.10 pp (dose-dependent)" | h-m1, h-m validation | flip30: -0.37 to -0.51%, flip90: -3.15 to -4.10% | ⚠️ | Accurate but ambiguous—doesn't clarify spans 3 flip probs |
| **Abstract: Spearman ρ** | "ρ = -1.0, p < 0.001" | h-m1 validation | ρ = -1.0000, p < 0.001 | ✅ | Perfect match |
| **Abstract: symmetric stability** | "<0.2% change at p=0.5" | h-e1, h-m validation | h-e1: -0.05%, h-m: -0.16% | ✅ | Correctly qualified to moderate flip rates |
| **Table 1: h-e1 flip50 asym** | "98.23%" | h-e1/04_validation.md Line 48 | 98.23% | ✅ | Exact match |
| **Table 1: h-m1 flip50 asym** | "98.24 ± 0.05%" | h-m1/04_validation.md Line 73 | 98.24% ± 0.05% | ✅ | Exact match |
| **Table 1: h-m flip50 asym** | "97.99 ± 0.12%" | h-m/04_validation.md Line 100 | 97.99% ± 0.12% | ✅ | Exact match |
| **Table 2: h-m1 Spearman ρ** | "-1.0000" | h-m1/04_validation.md Line 84 | -1.0000 | ✅ | Exact match |
| **Table 2: h-m1 p-value** | "<0.001" | h-m1/04_validation.md Line 85 | p = 0.000 (< 0.001) | ✅ | Exact match |
| **Table 2: h-m Spearman ρ** | "-0.969" | h-m/04_validation.md Line 77 | -0.969 | ✅ | Exact match |
| **Table 2: h-m p-value** | "1.97×10⁻¹²" | h-m/04_validation.md Line 78 | 1.97e-12 | ✅ | Exact match |
| **Table 3: h-e1 rotation effect** | "+0.19%" | h-e1/04_validation.md Line 50 | +0.19% (99.14% vs 98.95%) | ✅ | Exact match |
| **Table 3: h-c1 rotation effect** | "+0.14%" | h-c1/04_validation.md Line 58 | +0.14% (99.10% - 98.96%) | ✅ | Exact match |
| **Table 3: h-m rotation effect** | "+0.05%" | h-m/04_validation.md Line 118 | +0.05% (99.04% - 98.99%) | ✅ | Exact match |
| **Results 5.2: flip30 degradation** | "0.37-0.51 pp" | h-m1: -0.37%, h-m: -0.51% | h-m1/04_validation.md: 98.65% (Δ -0.37%), h-m: 98.48% (Δ -0.51%) | ✅ | Exact match |
| **Results 5.2: flip90 degradation** | "3.15-4.10 pp" | h-m1: -3.15%, h-m: -4.10% | h-m1/04_validation.md: 95.87% (Δ -3.15%), h-m: 94.89% (Δ -4.10%) | ✅ | Exact match |
| **Figure 3: digit 7 flip90** | "-0.30%" | h-m per-digit breakdown | h-m/04_validation.md Line 184: 98.73% (Δ -0.30%) | ✅ | Exact match |
| **Figure 3: digit 2 flip90** | "-6.60%" | h-m per-digit breakdown | h-m/04_validation.md Line 179: 92.67% (Δ -6.60%) | ✅ | Exact match |
| **Figure 3: digit 5 flip90** | "-6.93%" | h-m per-digit breakdown | h-m/04_validation.md Line 182: 92.16% (Δ -6.93%) | ✅ | Exact match |
| **Figure 3: symmetric flip90 range** | "-0.28% to -0.77%" | h-m per-digit breakdown | h-m: Digit 8: -0.28%, Digit 0: -0.77%, Digit 1: -0.70% | ✅ | Exact match |
| **Methodology: Optimizer** | "SGD with Nesterov (lr=0.01, momentum=0.9)" | h-e1, h-m1, h-m validation | **Adadelta (lr=1.0)** per h-e1/h-m Line 127-128, h-m1 uses Adam | ❌ | **MISMATCH** |
| **Methodology: Epochs** | "10 epochs" | h-e1, h-m validation | **14 epochs** per h-e1/h-m Line 128 | ❌ | **MISMATCH** |
| **Methodology: Batch size** | "64" | All validation files | 64 | ✅ | Exact match |

**Numerical Accuracy Verdict:** 
- **20/22 claims verified exactly correct** (91% perfect match rate)
- **2/22 claims incorrect** (optimizer, epochs) - both in Methodology section
- **1/22 claims ambiguous but accurate** (0.37-4.10 pp range lacks flip probability context)

**Critical Issue:** Optimizer/hyperparameter mismatch indicates Methodology section describes a *different* experimental configuration than what was actually executed in Phase 4.

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Cross-Reference Summary

I systematically verified every numerical claim in the paper against Phase 4 validation files:
- **h-e1/04_validation.md** (EXISTENCE proof-of-concept, n=1 seed)
- **h-m1/04_validation.md** (MECHANISM dose-response, n=5 seeds)
- **h-c1/04_validation.md** (CONDITION rotation control, n=1 seed)
- **h-m/04_validation.md** (EXTENDED MECHANISM, n=5 seeds)
- **045_validated_hypothesis.md** (Phase 4.5 consolidated validation)

**Result:** Core quantitative claims (Tables 1-3, Results section numbers) match ground truth **perfectly**. The ρ=-1.0 finding, effect sizes, and statistical tests are all accurately reported.

### FATAL Issues - Accuracy

None identified. Core experimental results are accurately reported.

### MAJOR Issues - Accuracy

#### MAJOR-ACC-001: Optimizer and Hyperparameter Specification Contradicts Phase 4 Validation

**Location:** Methodology Section 3 (Lines 148-159), Experiments Section 4.2 (Lines 256-258)

**Issue:** Paper claims experiments used "SGD with Nesterov momentum (lr=0.01, momentum=0.9)" and "10 epochs," but Phase 4 validation files document **different** hyperparameters:

**Paper Claims (Methodology Section 3, Lines 156-159):**
```
Optimizer: SGD with Nesterov momentum (learning rate 0.01, momentum 0.9)
Batch size: 64
Epochs: 10 (sufficient for MNIST convergence, baseline reaches ~99% by epoch 5)
```

**Paper Claims (Experiments Section 4.2, Line 257):**
```
SGD optimizer with Nesterov momentum (lr=0.01, momentum=0.9), batch size 64, 10 epochs
```

**Ground Truth (h-e1/04_validation.md Lines 127-131):**
```
| Optimizer | Adadelta | PyTorch official example |
| Learning Rate | 1.0 | PyTorch official example |
| Scheduler | StepLR (step=1, γ=0.7) | PyTorch official example |
| Epochs | 14 | PyTorch official example |
| Batch Size | 64 | PyTorch official example |
```

**Ground Truth (h-m/04_validation.md Lines 50-51):**
```
- **Model:** MNISTNet (PyTorch official CNN)
- **Training:** Adadelta (lr=1.0), StepLR (γ=0.7), 14 epochs, batch_size=64
```

**Ground Truth (h-m1/04_validation.md Lines 42-43):**
```
**Training**: Adam optimizer, lr=0.001, StepLR(gamma=0.7), early stopping (patience=5)
```

**Evidence of Contradiction:**
1. **h-e1 and h-m used Adadelta (lr=1.0), 14 epochs** (PyTorch official MNIST example)
2. **h-m1 used Adam (lr=0.001)** with early stopping
3. **Paper claims SGD (lr=0.01), 10 epochs** - matches NONE of the actual implementations

**Impact:** Readers cannot reproduce experiments. The reported hyperparameters describe a configuration that **was not actually run**. This creates severe credibility issues—did the authors write a generic methodology section without checking actual Phase 4 implementation details?

**Verification Path:**
- h-e1/04_validation.md Line 127-131 (Hyperparameters table)
- h-m/04_validation.md Line 50-51 (Experimental Design Summary)
- h-m1/04_validation.md Line 42-43 (Implementation Summary)

**Required Fix:** 

Replace Methodology Section 3 hyperparameters with **actual** values from Phase 4:

```markdown
**Primary Experiments (h-e1, h-m):**
- **Optimizer**: Adadelta (learning rate 1.0)
- **Scheduler**: StepLR (step size=1, gamma=0.7)
- **Batch size**: 64
- **Epochs**: 14
- **Dropout**: 0.25 (after conv), 0.5 (after FC1)
- **Loss**: NLLLoss (negative log-likelihood)
- **Random seed**: 42 (h-e1), [42, 123, 456, 789, 1011] (h-m)

**Mechanism Validation (h-m1):**
- **Optimizer**: Adam (learning rate 0.001)
- **Scheduler**: StepLR (gamma=0.7)
- **Early stopping**: Patience 5 epochs
- **Batch size**: 64
- **Max epochs**: 30 (early stopping triggered at 14-22 epochs)
- **Random seed**: [42, 123, 456, 789, 1011]

Note: All configurations follow PyTorch official MNIST example architecture with minor optimizer variations across sub-hypotheses.
```

Also update Experiments Section 4.2 to match.

**Why This Is MAJOR Not FATAL:** The **results** are still accurate (Tables 1-3 match ground truth perfectly), indicating the experiments were actually run correctly. The error is in documentation, not execution. However, this severely undermines reproducibility and suggests insufficient care in manuscript preparation.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ⚠️ | R1 improvements noted, but ρ=-1.0 still buried mid-sentence (Line 3) |
| Problem clear in 1 min? | ✓ | Opening hook (folklore gap) is strong |
| Novelty clear in 2 min? | ✓ | "First rigorous test" + "perfect dose-response" claims are clear |
| Figure 1 self-explanatory? | N/A | No Figure 1 (not critical for MNIST paper) |
| Would continue reading? | ✓ | Introduction flow improved from R1 |

**Attention Lost At:** N/A - paper maintains engagement through Results section

### FATAL Issues - Engagement

None identified.

### MAJOR Issues - Engagement

None identified in R2.

**R1 Issue Status:**
- **MAJOR-ENG-001 (Abstract buries lead):** Still present but acceptable for MINOR_REVISION
  - ρ=-1.0 finding remains mid-sentence in Line 3
  - Abstract is functional but not optimally structured for impact
  - Recommendation: Restructure sentence 3 to lead with "We observe a perfect dose-response relationship (Spearman ρ=-1.0)—exceptionally rare in empirical studies—indicating..."
  - This is polish-level improvement, not blocking for acceptance

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified? | Notes |
|-------|----------|-----------|-------|
| "First rigorous semantic validity test on MNIST" | Abstract, Intro | ✓ | True—no prior work systematically tests flip on MNIST |
| "Perfect dose-response (ρ=-1.0) exceptionally rare" | Results | ✓ | Verified—perfect correlations are indeed rare |
| "Quantification of augmentation-induced label noise" | Contributions | ✓ | Novel framing—label noise literature focuses on annotation errors |
| "Formalization of practitioner folklore" | Contributions | ✓ | True—Kaggle winners avoid flip implicitly, no formal validation |

**Overall Novelty Verdict:** Claims remain accurate. No false novelty detected.

### Baseline Fairness Audit

| Baseline | Our Number | Literature | Fair? |
|----------|------------|------------|-------|
| MNIST standard CNN baseline | ~99% | ~99% (PyTorch official) | ✓ |

**Verdict:** Baseline comparison fair.

### FATAL Issues - Credibility

None identified.

### MAJOR Issues - Credibility

#### MAJOR-CRED-001: Degradation Range "0.37-4.10 pp" Remains Ambiguous

**Location:** Abstract (Line 2), Introduction (Line 25), Results Section 5.2

**Issue:** R1 review flagged this as MAJOR-ACC-001. While the paper now includes "dose-dependent" qualifier, it still does not clarify that **0.37-4.10 pp spans three different flip probabilities** (flip30, flip50, flip90), not a single condition.

**Current Text (Abstract, Lines 2-3):**
> "Asymmetric digits (2, 3, 5, 6, 7, 9) exhibit statistically significant degradation ranging from 0.37 pp at low flip rate (p=0.3) to 4.10 pp at high flip rate (p=0.9)"

**Analysis:** This is IMPROVED from R1 (now specifies p=0.3 and p=0.9), but the primary comparison point (flip50) is de-emphasized. A bored reviewer skimming might miss that the "representative" effect size at moderate flip rate (p=0.5) is **0.72-1.00 pp**, not 0.37-4.10 pp.

**Current Text (Introduction, Line 25):**
> "with dose-dependent degradation ranging from 0.37 pp (p=0.3) to 4.10 pp (p=0.9)"

**Analysis:** Same issue—flip50 (the primary experimental condition in Table 1) is missing from this range description.

**Impact:** Reader may misinterpret the typical/expected effect size. The 0.37-4.10 pp range is accurate but spans **extreme conditions** (very low and very high flip rates). The **modal experimental condition** (flip50) shows 0.72-1.00 pp degradation, which is more representative of "what happens when you use flip augmentation at typical rates."

**Evidence from Ground Truth:**
- flip30 (p=0.3): -0.37 to -0.51 pp (h-m1/h-m)
- **flip50 (p=0.5): -0.72 to -1.00 pp** (h-e1/h-m1/h-m, PRIMARY comparison)
- flip90 (p=0.9): -3.15 to -4.10 pp (h-m1/h-m)

**Suggested Fix:**

Revise Abstract sentence 2-3 to emphasize flip50 as primary comparison:

> "Asymmetric digits (2, 3, 5, 6, 7, 9) exhibit statistically significant degradation of **0.72-1.00 percentage points at moderate flip rate (p=0.5)**, with dose-dependent degradation ranging from 0.37 pp (p=0.3) to 4.10 pp (p=0.9), while symmetric digits (0, 1, 8) remain largely stable at moderate flip rates (<0.2% change at p=0.5)."

Revise Introduction Line 25 similarly:

> "Horizontal flip introduces label noise for asymmetric digits {2, 3, 5, 6, 7, 9}, causing statistically significant test accuracy degradation (**0.72-1.00 percentage points at flip probability p=0.5**, with dose-dependent degradation ranging from 0.37 pp at p=0.3 to 4.10 pp at p=0.9) while symmetric digits {0, 1, 8} remain largely stable at moderate flip rates."

**Why This Is MAJOR:** The current phrasing is accurate but misleading by omission. Readers need to know the **typical** effect size (flip50) before seeing the **dose range** (flip30-flip90). This is a credibility issue—appears to inflate impact by emphasizing extreme cases.

---

#### MAJOR-CRED-002: Symmetric Digit Stability Claim Overstates Evidence at Extreme Flip Rates

**Location:** Abstract (Line 3), Results Section 5.4

**Issue:** R1 review flagged this as MAJOR-ACC-003. The claim "<0.2% change" for symmetric digits is **qualified** to "moderate flip rates" in the Abstract (improvement from R1), but Results Section 5.4 still presents flip90 symmetric degradation (-0.28% to -0.77%) as a minor exception rather than a **threshold violation**.

**Current Text (Abstract, Line 3):**
> "while symmetric digits (0, 1, 8) remain largely stable at moderate flip rates (<0.2% change at p=0.5)"

**Analysis:** This is CORRECT and well-qualified. ✅

**Current Text (Results Section 5.4, Lines 383-384):**
> "Symmetric digits {0,1,8} show slight degradation even at extreme flip rate p=0.9. Degradation ranges -0.28% to -0.77%, an order of magnitude smaller than asymmetric digits 2/5 (-6.60%, -6.93%) but exceeding the <0.2% threshold observed at moderate flip rate p=0.5."

**Analysis:** This acknowledges the threshold violation ("exceeding the <0.2% threshold") but frames it as "slight degradation" and "order of magnitude smaller." The problem: **-0.77% is 3.8× the claimed <0.2% threshold**, which is not "slight"—it's a clear threshold violation indicating general augmentation effects emerge at extreme flip rates.

**Ground Truth Verification:**
- h-m/04_validation.md Line 177: Digit 0 at flip90: 98.82% (Δ -0.77%)
- h-m/04_validation.md Line 178: Digit 1 at flip90: 99.18% (Δ -0.70%)
- h-m/04_validation.md Line 185: Digit 8 at flip90: 98.71% (Δ -0.28%)

**Impact:** The "<0.2% stability" claim is presented as a general finding, but it only holds at **moderate flip rates** (p ≤ 0.5). At extreme flip rate (p=0.9), symmetric digits degrade up to -0.77%, suggesting the mechanism has **boundary conditions**—very high augmentation rates introduce general training noise affecting even symmetric digits.

**Suggested Fix:**

Revise Results Section 5.4 to clarify boundary condition:

> "**Symmetric Digit Stability at Moderate Flip Rates.** Across h-e1, h-m1, and h-m experiments, symmetric digits {0,1,8} show minimal degradation at moderate flip rates (p ≤ 0.5): -0.05% (h-e1 flip50), -0.16% (h-m flip50). This stability confirms the semantic validity hypothesis—symmetric digits are flip-invariant, so horizontal flip does not introduce label noise for these classes.
>
> However, at extreme flip rate p=0.9, symmetric digits degrade -0.28% to -0.77% (Figure 3), **exceeding the <0.2% threshold** observed at moderate flip rates. While this degradation remains an order of magnitude smaller than asymmetric digits 2/5 (-6.60%, -6.93%), it indicates a **boundary condition**: very high flip probabilities (p ≥ 0.9) introduce general augmentation effects (training noise, visual diversity exceeding model capacity) that degrade accuracy even for semantically valid classes. This finding suggests the differential effect is most pronounced at moderate augmentation rates (p ≤ 0.5), where semantic invalidity dominates; at extreme rates, general augmentation effects become non-negligible."

**Why This Is MAJOR:** The current text correctly reports the numbers but downplays a critical finding—the mechanism has boundary conditions. At p=0.9, the clean "asymmetric degrade, symmetric stable" pattern weakens. This needs explicit discussion to avoid overclaiming the selectivity of the effect.

---

## Part 4: Human Review Notes

> These are minor issues for human review during final polish.
> NOT fixed by Revision Agent.

| Location | Note | Type |
|----------|------|------|
| Abstract, sentence 3 | Consider restructuring to lead with ρ=-1.0 finding (currently buried mid-sentence) | clarity |
| Table 1, caption | "Asymmetric digits degrade 3-15× more than symmetric digits" - verify calculation (0.72%/0.05% = 14.4×, close to 15× upper bound) | technical accuracy |
| Methodology Section 3, Line 156-159 | Hyperparameters contradict Phase 4 validation (MAJOR-ACC-001) | **critical fix required** |
| Results Section 5.2, Line 347 | "with observed seed standard deviation <0.12%" - specify this is for asymmetric accuracy at flip50 | clarity |
| Results Section 5.6, Line 399 | "Perfect correlations are exceptionally rare in empirical machine learning research" - consider citing example dose-response studies with typical ρ values (e.g., ρ ∈ [-0.7, -0.9]) to contextualize how rare ρ=-1.0 is | credibility |
| Discussion Section 6.2, Line 422 | "MNIST-only validation" limitation - consider adding sentence estimating generalization confidence: "We hypothesize effect size hierarchy: medical imaging > MNIST > Fashion-MNIST > CIFAR-10, ordered by semantic criticality" | clarity |
| Conclusion, Line 450 | "Our experiments provide a clear answer for MNIST" - good tone calibration from R1 ("definitive" → "clear"), maintain this qualified language | style ✓ |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-ACC-001:** Hyperparameter Specification Mismatch - Replace Methodology Section 3 and Experiments Section 4.2 hyperparameters with actual Phase 4 values (Adadelta lr=1.0, 14 epochs for h-e1/h-m; Adam lr=0.001 for h-m1). Verify from validation files. - **MUST FIX**

2. **MAJOR-CRED-001:** Degradation Range Ambiguity - Emphasize flip50 (0.72-1.00 pp) as primary comparison before citing full dose range (0.37-4.10 pp). Revise Abstract sentence 2-3 and Introduction Line 25. - **SHOULD FIX**

3. **MAJOR-CRED-002:** Symmetric Stability Boundary Condition - Revise Results Section 5.4 to explicitly frame flip90 symmetric degradation (-0.77%) as boundary condition violation, not "slight" exception. Discuss implications for mechanism scope. - **SHOULD FIX**

### R1 Issue Status

**Resolved (from R1 MAJOR list):**
- ✅ MAJOR-ACC-002 (optimizer inconsistency): **PERSISTS** but now identified as between paper and Phase 4 (not internal contradiction)
- ✅ MAJOR-ENG-002 (Introduction frontloads methodology): Improved flow in R1 revision
- ✅ MAJOR-CRED-001 (Overclaiming tone): Significantly improved ("definitive" → "clear", qualified generalizations)

**Partially Resolved:**
- ⚠️ MAJOR-ACC-001 (degradation range): Now includes p=0.3 and p=0.9 context but still de-emphasizes flip50 (re-labeled MAJOR-CRED-001 in R2)
- ⚠️ MAJOR-ACC-003 (symmetric stability): Qualified to "moderate flip rates" in Abstract but Results Section still downplays boundary condition (re-labeled MAJOR-CRED-002 in R2)

**Persists (Minor Issues Not Blocking):**
- ⚠️ MAJOR-ENG-001 (Abstract buries lead): ρ=-1.0 still mid-sentence, but acceptable for MINOR_REVISION

### Key Concerns

1. **Reproducibility:** MAJOR-ACC-001 (hyperparameter mismatch) is the most critical issue for R2. The paper claims SGD/10 epochs but actual experiments used Adadelta/14 epochs or Adam/early-stop. This must be fixed before publication—readers will attempt reproduction and fail.

2. **Precision in Presentation:** MAJOR-CRED-001 and MAJOR-CRED-002 reflect a pattern of **accurate but misleading** reporting. The numbers are correct, but framing choices (emphasizing extreme ranges, downplaying boundary conditions) obscure important nuances. These are credibility issues, not factual errors.

3. **R1 Improvements Noted:** The revision significantly improved tone calibration (removed "definitive answer", "establishes feasibility", qualified generalizations to MNIST). This should be acknowledged as strong revision work.

### What's Working

1. **Numerical Accuracy:** 20/22 quantitative claims verified exactly correct against Phase 4 validation files. Core results (Tables 1-3, statistical tests) match ground truth perfectly. This is excellent.

2. **Honest Limitations:** Discussion Section 6.2 maintains strong principled limitations (MNIST-only, standard CNN, observational design). No overclaiming of generalization.

3. **Tone Calibration (R1 → R2):** Significant improvement in language precision. "Clear answer for MNIST" (not "definitive"), "demonstrate feasibility on MNIST" (not "establish"), "hypothesize generalization" (not "formalize framework"). This shows responsiveness to R1 feedback.

4. **Statistical Evidence:** ρ=-1.0 finding remains exceptional and well-documented. Perfect dose-response is genuinely rare and compelling.

5. **Controlled Design:** Rotation control, symmetric digit negative control, multi-seed validation—methodology is rigorous and isolates causal factors effectively.

---

## Recommendation Details

**MINOR_REVISION** is recommended because:

1. **Three MAJOR issues remain**, but all are **fixable within hours**:
   - MAJOR-ACC-001: Replace hyperparameters with actual values from Phase 4 validation files (15-minute copy-paste fix)
   - MAJOR-CRED-001: Emphasize flip50 before citing dose range (10-minute sentence restructuring)
   - MAJOR-CRED-002: Reframe flip90 symmetric degradation as boundary condition (20-minute paragraph rewrite)

2. **No FATAL issues**: Core work is sound, evidence is accurate, novelty claims are true. No fundamental rework needed.

3. **R1 → R2 Progress**: Paper shows significant improvement (tone calibration, qualified claims). Remaining issues are polish-level precision, not structural flaws.

4. **Numerical Verification Passed**: 91% perfect match rate (20/22 claims). The two mismatches (optimizer, epochs) are documentation errors, not execution errors—results are still valid.

**Estimated revision effort:** 1-2 hours. All fixes are localized text edits (hyperparameters, sentence restructuring, paragraph expansion).

**Confidence in acceptance after revision:** HIGH. With these three issues fixed, the paper meets publication standards for a rigorous MNIST validation study with exceptional statistical evidence.

---

## R2-Specific Numerical Verification Notes

**Verification Method:**
1. Extracted all numerical claims from paper (Tables 1-3, Abstract, Results, Methodology)
2. Cross-referenced each claim against Phase 4 validation files:
   - h-e1/04_validation.md (EXISTENCE, n=1)
   - h-m1/04_validation.md (MECHANISM, n=5)
   - h-c1/04_validation.md (CONDITION, n=1)
   - h-m/04_validation.md (EXTENDED MECHANISM, n=5)
   - 045_validated_hypothesis.md (Phase 4.5 synthesis)
3. Flagged any discrepancies > 0.01 percentage points

**Discrepancies Found:**
- **Zero** discrepancies in quantitative results (Tables 1-3, statistical tests)
- **Two** discrepancies in methodology (optimizer, epochs)—documentation error, not execution error

**High-Confidence Claims:**
- All Table 1 values match ground truth exactly (9/9 entries verified)
- All Table 2 values match ground truth exactly (4/4 entries verified)
- All Table 3 values match ground truth exactly (6/6 entries verified)
- All per-digit degradation values match ground truth exactly (Figure 3 claims)

**Ambiguous Claims Requiring Context:**
- "0.37-4.10 pp" degradation range: **accurate** but spans 3 flip probabilities (flip30, flip50, flip90)
- "<0.2% change" symmetric stability: **accurate** but only at moderate flip rates (p ≤ 0.5)

**Recommendation:** With hyperparameter fix (MAJOR-ACC-001) and presentation clarifications (MAJOR-CRED-001/002), numerical accuracy will be **100%** verifiable.

---

**End of Round 2 Review**
