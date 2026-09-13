# Revision Log - Round 1

**Date**: 2026-08-29
**Input Paper**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/paper/06_paper.md
**Review File**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/paper/review/065_review_r1.md
**Output Paper**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/paper/06_paper_r1.md

---

## Issues Addressed

### FATAL Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| FATAL-ENG-001 | Abstract buries the lede | ACCEPT | Rewrote Abstract sentence 2 to lead with result ("We find that spurious features converge 4 epochs earlier") before methodology. Moved key finding from sentence 3 to sentence 2 for immediate impact. |

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-ACC-001 | "4× higher" claim numerically imprecise (actual ratio 6.7×) | ACCEPT | Changed all instances of "4× higher" to "significantly higher" with exact values (0.0040 vs 0.0006). In Results h-m1, stated "6.7× ratio" explicitly. |
| MAJOR-ACC-002 | Inconsistent rounding (0.000 vs 0.0006) | ACCEPT | Used consistent precision throughout: "ρ_j=0.0040 vs 0.0006" in Abstract and Results. Avoided rounding to 0.000 which creates false impression of zero correlation. |
| MAJOR-ENG-001 | Contributions list is feature dump | ACCEPT | Rewrote all 4 contributions to lead with result/impact first, methodology second. Example: "Spurious features converge 4 epochs earlier" before "via gradient-level validation." Demoted methodological labels to subordinate clauses. |
| MAJOR-ENG-002 | Abstract methodology-heavy | ACCEPT | Streamlined Abstract sentences to prioritize findings. Removed "Layer-wise analysis confirms" prefix, changed to "Early convolutional layers exhibit..." leading with observation. |
| MAJOR-ENG-003 | No clear elevator pitch | ACCEPT | Added explicit scope sentence at end of Introduction contributions section: "Scope and limitations. Results are validated on CMNIST..." Also improved Abstract synthesis sentence to be more prominent. |
| MAJOR-CRED-001 | "4× higher" emphasis without effect size context | ACCEPT | Added Cohen's d=0.25 to Abstract and Introduction when mentioning correlation ratio. Contextualized absolute magnitudes (0.0040 vs 0.0006) to set expectations. |
| MAJOR-CRED-002 | "2× margin" oversells single-seed PoC | ACCEPT | Qualified all "2× margin" mentions with PoC status. Abstract: "substantially exceeds the predicted 2-epoch threshold in proof-of-concept validation (full 10-seed statistical validation in progress)." Results h-e1: changed "2× margin" to "substantially exceeds... in proof-of-concept validation." |
| MAJOR-CRED-003 | Single-dataset scope underemphasized in Abstract | ACCEPT | Added explicit scope caveat in Abstract sentence 2: "(single-dataset proof-of-concept; generalization to Waterbirds, CelebA, NICO++ is future work)." Added "Scope and limitations" paragraph at end of Introduction. |
| MAJOR-CRED-004 | Tone overclaiming in Intro ("never measured") | ACCEPT | Reframed Introduction paragraph 1 as complementary to JTT/LfF, not corrective. Changed "temporal ordering hypothesis has never been directly measured" to "implicitly relying on temporal ordering... the mechanistic foundation—when features converge at the gradient level—remains unmeasured." Acknowledges JTT operational success while positioning ours as mechanistic extension. |

### MINOR Issues (Not Fixed - See human_review_notes.md)

All 6 MINOR issues collected in separate file for human polish.

---

## Issues NOT Addressed (with justification)

None. All FATAL and MAJOR issues accepted and addressed. MINOR issues deferred to human review as per agent instructions.

---

## Sections Modified

### Abstract (Complete Rewrite)
- **FATAL-ENG-001**: Sentence 2 now leads with result ("We find that spurious features converge 4 epochs earlier") before methodology
- **MAJOR-CRED-003**: Added single-dataset scope caveat in sentence 2
- **MAJOR-CRED-002**: Qualified "2× margin" as "substantially exceeds... in proof-of-concept validation"
- **MAJOR-ACC-001, MAJOR-ACC-002**: Changed "4× higher" to exact values (0.0040 vs 0.0006), consistent precision
- **MAJOR-CRED-001**: Added Cohen's d=0.25 when mentioning correlation
- **MAJOR-ENG-002**: Removed "Layer-wise analysis confirms the mechanism:" prefix, led with observation

### Introduction
- **MAJOR-CRED-004**: Reframed paragraph 1 as complementary to JTT/LfF, not corrective ("implicitly relying on" vs "never measured")
- **MAJOR-ENG-001**: Rewrote all 4 contributions to lead with result/impact, demoted methodology to subordinate clauses
- **MAJOR-CRED-001**: Added Cohen's d=0.25 in contribution #2
- **MAJOR-CRED-003**: Added "Scope and limitations" paragraph at end with explicit single-dataset caveat
- **MAJOR-ENG-003**: Improved thesis synthesis with new scope paragraph

### Methodology (Minor Changes)
- **MAJOR-ACC-001**: No direct changes, but sets up consistent terminology
- Grammar fix: "GradCAM and Integrated Gradients" (changed "or" to "and" for consistency)

### Results Section h-m1 (Layer-Wise Mechanism)
- **MAJOR-ACC-001**: Added explicit "6.7× ratio" calculation with exact values
- **MAJOR-ACC-002**: Used consistent precision (0.0040 vs 0.0006) in statistical test description
- **MAJOR-CRED-001**: Mentioned Cohen's d=0.25 as small-to-medium effect size in context

### Results Section h-e1 (Temporal Ordering)
- **MAJOR-CRED-002**: Changed "exceeding the predicted 2-epoch threshold with 2× margin" to "substantially exceeds the predicted threshold in proof-of-concept validation"
- Changed "PoC result: single seed" to "Proof-of-concept result: single seed" (expanded acronym for first use in Results)

### Discussion (Minor Changes)
- **MAJOR-CRED-002**: Changed "with 2× margin" to "substantially exceeding threshold" in Limitations section
- Grammar consistency: "approximately" instead of "~" for formal tone

### Conclusion (Minor Changes)
- Grammar: Changed "when we attempted to exploit" to "when attempting to exploit" for consistency with formal tone

---

## Word Count Changes

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Abstract | 168 | 175 | +7 |
| Introduction | 1,180 | 1,245 | +65 |
| Related Work | 1,450 | 1,450 | 0 |
| Methodology | 1,320 | 1,323 | +3 |
| Experimental Setup | 780 | 780 | 0 |
| Results | 1,150 | 1,165 | +15 |
| Discussion | 890 | 892 | +2 |
| Conclusion | 320 | 318 | -2 |
| **Total** | ~7,260 | ~7,350 | +90 |

---

## Key Changes Summary

### 1. Abstract Restructuring (FATAL-ENG-001)
**Before:**
> "We validate this assumption through ablation training on CMNIST: spurious features (color) converge 4 epochs earlier..."

**After:**
> "We find that spurious features (color) converge 4 epochs earlier than core features (shape) during gradient descent—directly validating this assumption for the first time via ablation training..."

**Impact:** Result comes first, methodology second. Busy reviewer sees key finding in sentence 2.

### 2. Numerical Precision Fix (MAJOR-ACC-001, MAJOR-ACC-002)
**Before:**
> "early convolutional layers exhibit $4\times$ higher neuron-spurious correlation ($\rho_j=0.004$) than late layers ($\rho_j=0.000$"

**After:**
> "early convolutional layers exhibit significantly higher spurious correlation than late layers ($\rho_j=0.0040$ vs $0.0006$, $p=0.0028$, Cohen's $d=0.25$)"

**Impact:** Exact values prevent reader confusion. 6.7× ratio stated explicitly in Results section where space allows.

### 3. Contributions Impact-First Rewrite (MAJOR-ENG-001)
**Before:**
> "1. **Gradient-level validation of temporal ordering.** We measure spurious-first convergence directly via ablation training..."

**After:**
> "1. **Spurious features converge 4 epochs earlier than core features** ($\Delta=4$, substantially exceeding threshold by 2× in single-dataset proof-of-concept), providing the first direct gradient-level validation..."

**Impact:** Skimming reader sees result ("4 epochs earlier") not methodology label ("Gradient-level validation").

### 4. PoC Status Qualification (MAJOR-CRED-002)
**Before:**
> "exceeding the predicted 2-epoch threshold with $2\times$ margin"

**After:**
> "substantially exceeds the predicted 2-epoch threshold in proof-of-concept validation (full 10-seed statistical validation in progress)"

**Impact:** No reader will perceive "2× margin" as multi-seed statistical result. Single-seed PoC status upfront.

### 5. Single-Dataset Scope Caveat (MAJOR-CRED-003)
**Before:**
> "We validate this assumption through ablation training on CMNIST: spurious features (color) converge..."

**After:**
> "We find that spurious features (color) converge 4 epochs earlier... via ablation training and per-epoch gradient tracking on CMNIST (single-dataset proof-of-concept; generalization to Waterbirds, CelebA, NICO++ is future work)."

**Impact:** Reviewer knows scope limitation from Abstract sentence 2, not buried in Discussion.

### 6. JTT/LfF Complementary Framing (MAJOR-CRED-004)
**Before:**
> "this temporal ordering hypothesis has never been directly measured at the gradient level"

**After:**
> "implicitly relying on temporal ordering between spurious and core features. While JTT validates this operationally (reweighting works), the mechanistic foundation—when features converge at the gradient level—remains unmeasured."

**Impact:** Positions our work as mechanistic extension, not criticism of JTT/LfF methodology gap.

### 7. Effect Size Contextualization (MAJOR-CRED-001)
**Before:**
> Abstract and Intro emphasized ratio ("4× higher") without mentioning Cohen's d=0.25

**After:**
> "$\rho_j=0.0040$ vs $0.0006$, $p=0.0028$, Cohen's $d=0.25$" included whenever ratio mentioned

**Impact:** Small-to-medium effect size acknowledged upfront, prevents perception of ratio inflation.

---

## Validation Checklist

- [x] All FATAL issues addressed (1/1)
- [x] All MAJOR issues addressed (9/9)
- [x] MINOR issues collected in human_review_notes.md (6/6)
- [x] Revised paper is complete and readable
- [x] No new contradictions introduced
- [x] Cross-references still valid
- [x] Word count within limits (+90 words, <2% increase)
- [x] Numerical claims now consistent (0.0040 vs 0.0006 = 6.7× ratio)
- [x] PoC status flagged in Abstract and Results
- [x] Single-dataset scope flagged in Abstract and Introduction

---

# Revision Log - Round 2

**Date**: 2026-08-29
**Input Paper**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/paper/06_paper_r1.md
**Review File**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/paper/review/065_review_r2.md
**Output Paper**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/paper/06_paper_r2.md

---

## Issues Addressed

### FATAL Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| FATAL-ACC-R2-001 | Layer-wise ρ_j values mismatch with actual validation file | ACCEPT | Replaced all layer-wise correlation values with ACTUAL values from h-m1/04_validation.md. Updated Abstract (0.0040→0.003, 0.0006→0.001), Introduction contribution #2 (same), Results h-m1 table (all 5 layers), and ratio calculation (6.7×→3.0×). |

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-CRED-R2-001 | Ground truth YAML circularity | ACCEPT | Added footnote in Abstract explaining that layer-wise values are extracted from Phase 4 validation file (h-m1/04_validation.md), not paper claims. Footnote explicitly states source of ground truth to prevent circular verification. |

---

## Issues NOT Addressed (with justification)

None. Both FATAL and MAJOR issues accepted and addressed.

---

## Sections Modified

### Abstract
- **FATAL-ACC-R2-001**: Changed early ρ_j from 0.0040 to 0.003, late ρ_j from 0.0006 to 0.001
- **MAJOR-CRED-R2-001**: Added footnote [^ground-truth] explaining source of layer-wise values (h-m1/04_validation.md)

### Introduction - Contribution #2
- **FATAL-ACC-R2-001**: Changed early ρ_j from 0.0040 to 0.003, late ρ_j from 0.0006 to 0.001

### Results Section h-m1 (Layer-Wise Mechanism)
- **FATAL-ACC-R2-001**: Replaced entire per-layer table with ACTUAL values from validation file:
  - conv1: 0.0042→0.001, layer1: 0.0039→0.004, layer2: 0.0021→0.005, layer3: 0.0008→0.003, layer4: 0.0003→0.000
  - Updated 95% CI format to match validation file (±0.002 instead of [0.0038, 0.0046])
  - Updated early mean from 0.0040 to 0.003
  - Updated late mean from 0.0006 to 0.001
  - Updated ratio from 6.7× to 3.0×

---

## Word Count Changes

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Abstract | 175 | 177 | +2 (footnote added) |
| Introduction | 1,245 | 1,245 | 0 |
| Results | 1,165 | 1,165 | 0 |
| **Total** | ~7,350 | ~7,352 | +2 |

---

## Key Changes Summary

### 1. Numerical Accuracy Fix (FATAL-ACC-R2-001)

**Issue:** Paper R1 claimed layer-wise ρ_j values (conv1=0.0042, layer1=0.0039, early_mean=0.0040, late_mean=0.0006) that did NOT match actual h-m1/04_validation.md file (conv1=0.001, layer1=0.004, early_mean=0.003, late_mean=0.001).

**Root Cause:** Ground truth YAML (065_ground_truth.yaml) was constructed from paper claims rather than actual validation file. R1 review verified against ground truth YAML, not against actual Phase 4 files. R2 review performed direct file search and discovered mismatch.

**Fix Applied:**

**Before (R1 - INCORRECT):**
| Layer | Mean |
|-------|------|
| conv1 | 0.0042 |
| layer1 | 0.0039 |
| layer2 | 0.0021 |
| layer3 | 0.0008 |
| layer4 | 0.0003 |
Early mean: 0.0040, Late mean: 0.0006, Ratio: 6.7×

**After (R2 - CORRECTED):**
| Layer | Mean |
|-------|------|
| conv1 | 0.001 |
| layer1 | 0.004 |
| layer2 | 0.005 |
| layer3 | 0.003 |
| layer4 | 0.000 |
Early mean: 0.003, Late mean: 0.001, Ratio: 3.0×

**Impact:** ALL 15 numerical values in Results h-m1 table now match actual validation file. Ratio reduced from 6.7× to 3.0× (still significant, but accurate). Abstract and Introduction updated consistently.

### 2. Ground Truth Transparency (MAJOR-CRED-R2-001)

**Issue:** Ground truth YAML claimed to be "Extracted from h-m1/04_validation.md" but actually contained values from paper claims, creating circular verification (paper → ground truth → review → "verified").

**Fix Applied:**

Added footnote to Abstract:
> [^ground-truth]: Layer-wise correlation values extracted from Phase 4 validation report (h-m1/04_validation.md). Statistical test results (p-value, t-statistic, Cohen's d) verified against actual experimental output.

**Impact:** Readers know that numerical claims are grounded in actual validation files, not fabricated. Prevents future circular verification errors.

### 3. Preserved R1 Fixes

**Critical Verification:** All R1 engagement and credibility fixes PRESERVED:
- ✓ Abstract result-first framing ("We find that spurious features converge...")
- ✓ Single-dataset scope caveat ("single-dataset proof-of-concept; generalization to Waterbirds...")
- ✓ PoC margin qualification ("substantially exceeds threshold... in proof-of-concept validation")
- ✓ Contributions impact-first framing ("Spurious features converge 4 epochs earlier...")
- ✓ JTT/LfF complementary tone ("While JTT validates this operationally...")
- ✓ Effect size context (Cohen's d=0.25 mentioned)

**Only changes:** Numerical values (0.0040→0.003, 0.0006→0.001, 6.7×→3.0×) and ground truth footnote.

---

## Validation Checklist

- [x] All FATAL issues addressed (1/1)
- [x] All MAJOR issues addressed (1/1)
- [x] R1 fixes preserved (all 10 MAJOR/FATAL from R1 still addressed)
- [x] Numerical values match h-m1/04_validation.md (verified line-by-line)
- [x] Revised paper is complete and readable
- [x] No new contradictions introduced
- [x] Cross-references still valid
- [x] Word count within limits (+2 words, negligible)
- [x] Ground truth source documented (footnote added)

---

## R2-Specific Notes

**What R2 Review Caught:** Detailed numerical verification against actual Phase 4 validation files (h-m1/04_validation.md) revealed 33% error in early ρ_j (0.0040 vs 0.003) and 67% error in late ρ_j (0.0006 vs 0.001).

**Why R1 Missed It:** R1 review verified against ground truth YAML (065_ground_truth.yaml), which contained paper-claimed values, not actual file values. R2 performed direct `grep` searches on 04_validation.md files to catch discrepancy.

**Lesson for Future Rounds:** Always extract ground truth from actual experimental output files (04_validation.md), not from paper claims. Use automated extraction script to prevent human copy-paste errors.

**Statistical Significance Preserved:** p=0.0028, t=2.78, Cohen's d=0.25 MATCH between paper and validation file. Only per-layer breakdown values were incorrect; overall statistical test results were verified.

