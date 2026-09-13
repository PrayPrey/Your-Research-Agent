# Phase 2B Context: H-E1

**Generated:** 2026-07-10  
**Source:** 02b_verification_plan.md  
**Hypothesis ID:** h-e1  
**Context Type:** Per-Hypothesis JIT Generated

---

## Hypothesis Information

### Statement
Temperature scaling produces calibrated confidence scores that reduce Expected Calibration Error (ECE) by ≥30% compared to uncalibrated logits

### Type
EXISTENCE

### Gate Type
MUST_WORK

### Prerequisites
None (foundation hypothesis)

### Status
READY

---

## Rationale

- Validates that the calibration mechanism itself works
- Establishes baseline calibration quality before testing behavioral relevance
- Directly tests the first component of the causal chain

---

## Key Metrics

- **Expected Calibration Error (ECE)** - Primary metric
- **Reliability diagram alignment** - Visual validation
- **Calibration curve visualization** - Monotonicity check

---

## Success Criteria

- ECE reduction ≥ 30% compared to uncalibrated logits
- Reliability diagram shows improved diagonal alignment
- Calibration curves demonstrate monotonic confidence-accuracy relationship

---

## Risk Assessment

**Risk Level:** LOW  
**Estimated Effort:** 2-3 days

**Technical Risks:**
- Temperature scaling doesn't reduce ECE (LOW likelihood)
  - Mitigation: Use established methods (UniCR, QaTS)

**Methodological Risks:**
- Dataset size insufficient for robust calibration (LOW likelihood)
  - Mitigation: Use MBPP (974 problems), pool rounds if needed

---

## Controlled Variables (From Phase 2B)

### Datasets
- **Primary:** MBPP (974 problems)
  - Train: 60% (584 problems)
  - Calibration: 20% (195 problems)
  - Validation: 20% (195 problems)
- **Generalization Test:** HumanEval (164 problems, held-out)

### Models
- Code Llama (open-weight, logit access)
- StarCoder2 (open-weight, logit access)
- DeepSeek-Coder (open-weight, logit access)

### Calibration Method
- Temperature scaling (learned on calibration split)
- Conformal quantiles: α=0.05, β=0.20

---

## Gate Decision Rules

### H-E1 MUST_WORK Gate
- **PASS:** ECE reduction ≥ 30% → Proceed to H-M1
- **PARTIAL:** 15-30% ECE reduction → Modify (improve calibration method), max 1 attempt
- **FAIL:** < 15% ECE reduction → Route to Phase 0 (calibration doesn't work)

---

## Dependencies

### Downstream Hypotheses (Blocked if H-E1 fails)
- **H-M1:** Confidence-Correctness Monotonicity (requires calibrated confidence)
- **H-M2:** Marginal Benefit Regression (requires H-M1)
- **H-C1:** Gated Execution Reduction (requires H-M2)

### Upstream Hypotheses
None - This is the foundation hypothesis

---

## Archon Task ID
e372e957-4213-4e57-b682-229fc1a2d4cc

---

## Pipeline Context

**Pipeline Project ID:** 01ed3ac8-ad89-4e0a-8121-d72f11f7b9a7  
**Main Hypothesis:** h-c1 (Confidence-Calibrated Iteration Control)  
**Position in DAG:** Root node (first in sequential chain)
