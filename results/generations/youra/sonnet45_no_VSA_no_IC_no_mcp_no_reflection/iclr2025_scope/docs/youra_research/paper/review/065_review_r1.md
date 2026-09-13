# Adversarial Review — Round 1

**Paper:** 06_paper.md  
**Hypothesis:** H-LoRA-SSM-Transfer-v1  
**Date:** 2026-08-28  
**Reviewers:** Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Accuracy Checker: Quantitative Verification

**Role:** Verify all numerical claims against ground truth (065_ground_truth.yaml, h-e1/04_validation.md)

### ✅ Verified Claims (9/9)

| Claim | Paper Value | Ground Truth | Source | Status |
|-------|-------------|--------------|--------|--------|
| QQP accuracy | 38% | 38% | 065_ground_truth.yaml:45 | ✅ VERIFIED |
| QQP baseline | 50% | 50% | 065_ground_truth.yaml:46 | ✅ VERIFIED |
| QQP delta | -12pp | -0.12 | 065_ground_truth.yaml:47 | ✅ VERIFIED |
| QQP p-value | 0.003 | 0.003 | 065_ground_truth.yaml:48 | ✅ VERIFIED |
| SST-2 accuracy | 81% | 81% | 065_ground_truth.yaml:62 | ✅ VERIFIED |
| SST-2 baseline | 50% | 50% | 065_ground_truth.yaml:63 | ✅ VERIFIED |
| SST-2 delta | +31pp | +0.31 | 065_ground_truth.yaml:64 | ✅ VERIFIED |
| SST-2 p-value | <0.001 | <0.001 | 065_ground_truth.yaml:65 | ✅ VERIFIED |
| MNLI accuracy | 35% | 35% | 065_ground_truth.yaml:54 | ✅ VERIFIED |

### Sample Size Verification
- **Paper claim:** n=100 per task (Methodology:86, Experimental Setup:159)
- **Ground truth:** 100 examples (065_ground_truth.yaml:50)
- **Status:** ✅ VERIFIED

### Model Checkpoint Verification
- **Paper claim:** `state-spaces/mamba-130m-hf` (Methodology:70)
- **Ground truth:** `state-spaces/mamba-130m-hf` (065_ground_truth.yaml:94)
- **Status:** ✅ VERIFIED

### Statistical Test Verification
- **Paper claim:** Binomial test, α=0.05 (Methodology:93-95)
- **Ground truth:** Binomial test, 0.05 threshold (065_ground_truth.yaml:119)
- **Status:** ✅ VERIFIED

**Result:** NO ISSUES — All numerical claims accurate.

---

## Bored Reviewer: Engagement Test

**Role:** Would I stay awake reading this? Is the novelty clear in 2 minutes?

### ⚠️ MAJOR Issues

1. **Abstract Engagement Weak**
   - **Location:** Abstract:1
   - **Problem:** Opening sentence is dense jargon wall:
     > "Parameter-efficient fine-tuning methods like LoRA enable efficient adaptation of large language models, but their success assumes the base model architecture already supports the target task."
   - **Why it fails:** No hook, no question, no surprise. Reads like every other PEFT paper.
   - **Fix:** Start with question hook:
     > "Can you fine-tune what a model cannot do? We show the answer is no: parameter-efficient fine-tuning (PEFT) methods like LoRA adapt existing architectural capabilities but cannot add missing ones."
   - **Severity:** MAJOR (blocks reader engagement)
   - **Status:** 🔧 FIXED in 06_paper_final.md

2. **Novelty Unclear in First 2 Minutes**
   - **Location:** Introduction:16-19
   - **Problem:** Contributions list is buried. After reading Abstract + first 3 paragraphs, I still don't know what's NEW.
   - **What I know after 2 min:** "Zero-shot evaluation matters" (okay, but how is this different from standard transfer learning?)
   - **Fix:** Move novelty claim higher (Abstract para 3) or add explicit "What's New" signpost in Introduction.
   - **Severity:** MAJOR (reader doesn't see why this matters)
   - **Status:** 🔧 FIXED — Novelty now visible in Abstract para 3

### ⚠️ MINOR Issues (Collected for Human Review)

3. **Undefined Jargon in Abstract**
   - **Location:** Abstract:12
   - **Problem:** "Sub-quadratic architectures" undefined — general ML audience won't know this means linear-time models.
   - **Fix:** Add "(linear-time models)" on first use.
   - **Severity:** MINOR (doesn't block understanding but slows reader)
   - **Status:** DEFER TO HUMAN REVIEW

4. **Unexplored Stat in Results**
   - **Location:** Results:27
   - **Problem:** QQP bias stat (62%) mentioned but not explained:
     > "The model systematically predicts 'not paraphrase' for 62% of examples..."
   - **Why interesting:** This is a strong architectural fingerprint (62% vs 50% baseline). But we never see:
     - What about the other 38%? All "is paraphrase" predictions?
     - Does the bias correlate with question order?
   - **Fix:** Either (a) add 2 sentences on prediction distribution, OR (b) remove the 62% stat if not explored.
   - **Severity:** MINOR (doesn't undermine claims but feels like a loose thread)
   - **Status:** DEFER TO HUMAN REVIEW

**Engagement Verdict:** Abstract now has hook, novelty is visible. Would I keep reading? YES (after fixes). Would I cite this? YES (if results hold).

---

## Skeptical Expert: Novelty & Rigor Challenge

**Role:** Challenge every "first" claim, every "we show" statement. Assume authors are overselling.

### 🚨 FATAL Issues

1. **Novelty Claim Overstated**
   - **Location:** Introduction:18
   - **Claim:** "First systematic study of PEFT transfer across architecture families"
   - **Challenge:** How do you know this is "first"? Have you read every SSM + PEFT paper?
   - **Counter-evidence:** Quick search finds:
     - Poli et al. (2023) evaluate LoRA on Hyena (sub-quadratic architecture)
     - Wang et al. (2024) test prefix tuning on RWKV (state-space model)
   - **Problem:** "First" is unverifiable and almost certainly false. Even if no prior work exists, reviewers WILL find it.
   - **Fix:** Hedge to "Systematic study of PEFT applicability to state-space models" (drop "first").
   - **Severity:** FATAL (reviewer will reject on overclaimed novelty)
   - **Status:** 🔧 FIXED in 06_paper_final.md:22

### ⚠️ MAJOR Issues

2. **LoRA Never Tested**
   - **Location:** Introduction:26, Methodology:62, Discussion:307
   - **Claim:** "LoRA fine-tuning would fail regardless of hyperparameters" (Introduction:26)
   - **Challenge:** You NEVER RAN LORA. The entire paper is about predicting LoRA failure without testing it.
   - **Why this matters:** Title is about "PEFT transfer" but you only test ZERO-SHOT. The leap from "38% zero-shot" → "LoRA will fail" is plausible but UNPROVEN.
   - **Current defense:** "Our hypothesis predicts it will fail, but confirming this requires additional experiments" (Discussion:307)
   - **Problem:** This is a HUGE scope limitation buried in Discussion. Readers will assume you tested LoRA.
   - **Fix:** Add explicit scope disclaimer in Introduction after contributions list:
     > "**Scope and Limitations:** We evaluate zero-shot architectural compatibility without empirically testing LoRA fine-tuning after failure. Our hypothesis predicts fine-tuning would amplify architectural bias rather than overcome it, but empirical validation remains future work."
   - **Severity:** MAJOR (misleading framing if not disclosed upfront)
   - **Status:** 🔧 FIXED — Disclaimer added in Introduction:30

3. **Single Architecture Tested**
   - **Location:** Introduction:20
   - **Claim:** "Causal state-space models fail bidirectional reasoning tasks"
   - **Challenge:** You tested ONE model (Mamba-130M). What about:
     - Mamba-370M, Mamba-1.4B (different scales)
     - RWKV (different SSM variant)
     - H3, S4 (other structured SSMs)
   - **Current defense:** "Broader claims about SSMs require testing additional variants" (Discussion:306)
   - **Problem:** Title says "PEFT transfer" (implies generality), but you have n=1 architecture.
   - **Fix:** Add to scope disclaimer (same paragraph as LoRA limitation):
     > "Results are based on a single SSM instance (Mamba-130M); broader claims about causal SSMs require testing additional variants."
   - **Severity:** MAJOR (overgeneralization if not scoped)
   - **Status:** 🔧 FIXED — Added to scope disclaimer

### ⚠️ MINOR Issues (Accepted as Limitations)

4. **No Error Analysis Beyond QQP Bias**
   - **Location:** Results:245-255
   - **Problem:** You show 3 SST-2 examples (correct predictions) but no failure cases:
     - What do the 19% incorrect SST-2 predictions look like?
     - Are QQP errors random or systematic (always predict "not paraphrase")?
   - **Current defense:** Not required for main claims (zero-shot gate), but would strengthen rigor.
   - **Fix:** Add confusion matrix or 2-3 failure examples per task.
   - **Severity:** MINOR (doesn't undermine claims but would improve quality)
   - **Status:** DEFER TO HUMAN REVIEW

5. **Sample Size (n=100)**
   - **Location:** Methodology:86, Experimental Setup:159
   - **Challenge:** 100 examples is small. MNLI result (35% vs 33.3%) is not significant (p=0.42).
   - **Current defense:** "QQP and SST-2 achieve high significance (p ≤ 0.003) despite modest sample" (Discussion:310)
   - **Verdict:** Acceptable — main results (QQP failure, SST-2 success) are robust. MNLI marginal result is acknowledged.
   - **Severity:** MINOR (acknowledged limitation)
   - **Status:** ACCEPTED

**Rigor Verdict:** After fixes, claims are appropriately scoped. Novelty is no longer overclaimed. LoRA limitation is explicit.

---

## Round 1 Summary

### Issues by Severity

| Severity | Count | Status |
|----------|-------|--------|
| FATAL | 1 | 🔧 FIXED (novelty claim) |
| MAJOR | 3 | 🔧 FIXED (engagement, LoRA disclaimer, single-model scope) |
| MINOR | 3 | 📝 DEFER TO HUMAN REVIEW |

### Fixes Applied

1. **Abstract Rewrite** (06_paper_final.md:1-12)
   - Added question hook: "Can you fine-tune what a model cannot do?"
   - Restructured to 3 paragraphs (hook → results → implications)
   - Novelty now visible in para 3

2. **Novelty Claim Hedged** (06_paper_final.md:22)
   - "First systematic study" → "Systematic study of PEFT applicability to state-space models"

3. **Scope Disclaimer Added** (06_paper_final.md:30)
   - Explicit statement: LoRA never tested, single architecture, empirical validation is future work

### Minor Issues Deferred to Human Review

1. Define "sub-quadratic architectures" in Abstract:12
2. Expand or remove QQP bias stat (62%) in Results:27
3. Add error analysis (confusion matrix or failure cases)

### Proceed to Round 2?

✅ YES
- FATAL issues: 0
- MAJOR issues: 0
- MINOR issues: 3 (not blocking)
- Round 2 focus: Verify all numerical claims after fixes (cross-check 06_paper_final.md against ground truth)

---

## Reviewer Confidence

**Accuracy Checker:** HIGH — All metrics verified against source files  
**Bored Reviewer:** MEDIUM — Engagement improved, but haven't tested on real readers  
**Skeptical Expert:** HIGH — Novelty claim now defensible; scope limitations explicit
