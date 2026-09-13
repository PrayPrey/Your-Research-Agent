# Hypothesis h-e1: BN-LN Worst-Group Gap Difference

**ID**: h-e1  
**Type**: EXISTENCE  
**Gate**: MUST_WORK (foundation hypothesis)  
**Status**: Experiment design complete, ready for Phase 3  
**Archon Task ID**: c4f70e7d-cb8d-476c-9f74-91c168c072b0

---

## Statement

ResNet-BN shows ≥5 percentage point higher worst-group accuracy gap than ResNet-LN when both reach 90% average accuracy on Waterbirds dataset.

---

## Motivation

Foundation hypothesis testing whether Batch Normalization amplifies spurious correlation learning compared to Layer Normalization. If confirmed, establishes architectural signature basis for mechanism hypotheses (h-m1, h-m2, h-c1).

---

## Prerequisites

None — ready for immediate execution.

---

## Dependencies

Blocks execution of:
- h-m1 (BN amplification mechanism)
- h-m2 (attention correction mechanism)  
- h-c1 (signature consistency condition)

All dependent hypotheses wait for h-e1 validation before starting Phase 2C.

---

## Success Criterion

- Mean gap difference (BN - LN) ≥ 5 percentage points AND
- Paired t-test p < 0.05 AND
- Cohen's d ≥ 0.8 (large effect size)

Statistical power: 10 seeds provide 80% power to detect 2pp effect.

---

## Falsification Criterion

- p > 0.05 OR
- Mean gap difference < 3 percentage points OR
- Cohen's d < 0.5 (medium effect)

If falsified → ROUTE to Phase 0 (fundamental flaw in main hypothesis).

---

## Key Design Decisions

1. **Accuracy-matched comparison**: Eliminates learning rate schedule confound
2. **Constant LR=0.01**: Isolates architectural effects from optimization dynamics
3. **No data augmentation**: Removes augmentation-normalization interaction
4. **10 seeds**: Statistical power for small effects (2pp detectable)
5. **Real dataset (Waterbirds)**: Standard spurious correlation benchmark, not synthetic

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| 90% accuracy never reached | Fallback: measure gap at epoch 80 or best accuracy |
| Training speed confound | Accuracy-matched comparison eliminates confound |
| LN convergence instability | Monitor loss curves, gradient clipping if needed |

---

## Next Phase Actions

**Phase 3 (Implementation Planning)**:
1. Generate PRD with acceptance criteria
2. Design architecture (4 modules: data, model, train, eval)
3. Break into Epic-level Archon tasks
4. Estimate implementation budget

**Phase 4 (PoC Validation)**:
1. Implement via Coder-Validator loop
2. Run 10-seed experiment
3. Validate statistical test results
4. Generate 04_validation.md report

---

**Phase 2C Status**: COMPLETED  
**Blocking Issues**: NONE  
**Ready for Phase 3**: YES
