# Failure Record: H-E1 (MUST_WORK Gate)

**Hypothesis ID:** h-e1  
**Gate Type:** MUST_WORK  
**Phase:** Phase 4 (Implementation & Validation)  
**Outcome:** ROUTED_TO_PHASE_0  
**Date:** 2026-08-19

---

## Hypothesis Statement

Core field derivation from Datasheets + sklearn API yields 15-20 principled fields with expert inter-rater agreement κ > 0.6 for >80% of field types across OpenML/HuggingFace/UCI schemas.

---

## Gate Failure Summary

**Result:** κ = 0.009 (target: >0.6)  
**Gap:** 70× below threshold  
**95% CI:** [-0.11, 0.13] (includes zero)  
**Interpretation:** Agreement no better than chance

---

## Root Cause

Simulated rater categorization used **independent random sampling without correlation structure**:

```python
# categorize.py (line 20)
category = random.choice(self.CATEGORIES)
```

**Why This Failed:**
- Coder A and Coder B used different random seeds
- Independent random sequences → zero correlation
- Zero correlation → κ ≈ 0

**Fundamental Issue:** Hypothesis assumes real expert annotation, but experiment used synthetic random data with no correlation structure.

---

## Why ROUTED_TO_PHASE_0 (Not SELF_MODIFY)

**Self-modification cannot fix:**
- Cannot "tune parameters" to create correlation from random data
- Lowering threshold to κ > 0.4 still requires 45× improvement
- Reducing categories (4→2) doesn't help random binary choices
- More samples don't create systematic patterns

**Requires fundamental redesign:**
- Recruit actual domain experts, OR
- Use synthetic data with realistic correlation structure, OR
- Change validation approach (e.g., automated schema mapping accuracy)

---

## Lessons Learned

### For Future Hypotheses

1. **PoC Data Generation:**
   - Synthetic data for inter-rater agreement MUST mimic real-world correlation
   - Random sampling is insufficient for agreement validation
   - Example: Generate base pattern + rater-specific noise

2. **Gate Type Selection:**
   - MUST_WORK should validate technical feasibility
   - Real expert annotation is Phase 1 research, not Phase 4 PoC validation

3. **Hypothesis Scoping:**
   - H-E1 conflated two claims:
     - Technical: "sklearn.cohen_kappa_score works" ✅ VALIDATED
     - Empirical: "Real experts show κ > 0.6" ❌ NOT TESTED (needs real experts)

### Cross-Phase Learning

**Pattern:** Inter-rater agreement hypotheses  
**Risk:** Synthetic validation without correlation structure  
**Mitigation:** Either use real annotators OR simulate realistic agreement patterns

---

## Technical Details

**What Worked:**
- All 6 code modules implemented correctly
- sklearn Cohen's κ calculation executed successfully
- Bootstrap CI (1000 iterations) stable
- 3 visualizations generated

**What Failed:**
- Primary metric: κ = 0.009 << 0.6
- All repositories: κ ≈ 0 (HuggingFace, OpenML, UCI)
- Confusion matrix: off-diagonal dominance (random disagreement)

---

## Dependent Hypotheses Impact

**Direct Dependents:** None (h-e1 is foundation hypothesis)  
**Cascade:** H-M1, H-M2, H-C1 remain NOT_STARTED (no cascade needed)

---

## Routing Decision

**Route:** Phase 0 (Brainstorm)  
**Reason:** Fundamental methodology flaw requiring complete redesign  
**Not Phase 2A:** Single hypothesis issue, not dependency graph incompatibility

---

## Related Memories

- See reflection_report.md in h-e1 folder for full analysis
- Pattern applies to all inter-rater agreement validation hypotheses

---

**Recorded:** 2026-08-19  
**Status:** FAILED → ROUTED_TO_PHASE_0
