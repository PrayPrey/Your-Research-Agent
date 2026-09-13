# Phase 6.5 Adversarial Review Changelog

**Paper:** 06_paper.md → 06_paper_final.md  
**Hypothesis:** H-LoRA-SSM-Transfer-v1  
**Date:** 2026-08-28

---

## Round 1 Fixes

### FATAL Issues (Blocking Publication)

1. **Novelty Claim Overstated** (Introduction:15)
   - **Before:** "First systematic study of PEFT transfer across architecture families"
   - **After:** "Systematic study of PEFT applicability to state-space models"
   - **Reason:** Other SSM PEFT papers exist; claim not verifiable as "first"

### MAJOR Issues (Severe Quality Problems)

1. **Abstract Engagement** (Abstract:1-12)
   - **Before:** Dense opening sentence with jargon ("parameter-efficient fine-tuning methods like LoRA enable efficient adaptation...")
   - **After:** Question hook ("Can you fine-tune what a model cannot do? We show the answer is no...")
   - **Reason:** Bored reviewer test failed — novelty unclear in first 2 minutes

2. **LoRA Untested** (Introduction:24-26, new paragraph)
   - **Before:** Implicit assumption that LoRA would fail (no explicit disclaimer)
   - **After:** Added "Scope and Limitations" paragraph acknowledging LoRA never empirically tested
   - **Reason:** Skeptical expert flagged gap between claims and evidence

3. **Abstract Restructure** (Abstract:1-12)
   - **Before:** 197-word single paragraph
   - **After:** 3-paragraph structure (hook → results → implications)
   - **Reason:** Improved scannability and engagement

### MINOR Issues (Not Auto-Fixed)

1. "Sub-quadratic architectures" undefined (Abstract:12)
   - **Action:** Noted in human_review_notes.md
   - **Fix:** Add "(linear-time models)" on first use

2. QQP bias stat (62%) unexplored (Results:27)
   - **Action:** Noted in human_review_notes.md
   - **Fix:** Add 2 sentences on prediction distribution OR remove stat

3. Passive voice in limitations (Discussion:306-314)
   - **Action:** Noted in human_review_notes.md
   - **Fix:** Convert to active voice

---

## Round 2 Fixes

**No changes made** — numerical verification found zero discrepancies.

---

## Summary Statistics

**Total edits:** 4 (1 FATAL, 3 MAJOR)  
**Lines changed:** 28  
**Sections modified:** Abstract (12 lines), Introduction (3 lines)  
**Convergence:** Round 2 (minimum required)

---

## Verification Audit

**Metrics Verified Against Ground Truth:**
1. QQP accuracy: 38% ✅
2. QQP baseline: 50% ✅
3. QQP delta: -12pp ✅
4. QQP p-value: 0.003 ✅
5. SST-2 accuracy: 81% ✅
6. SST-2 baseline: 50% ✅
7. SST-2 delta: +31pp ✅
8. SST-2 p-value: <0.001 ✅
9. MNLI accuracy: 35% ✅

**Source files checked:**
- h-e1/04_validation.md
- 045_validated_hypothesis.md
- 065_ground_truth.yaml

---

## Next Steps

1. Human review of MINOR issues (065_human_review_notes.md)
2. Phase 6.51 (Overleaf upload) if human approves
3. No further adversarial rounds needed
