# Phase 4 Failure Record: h-e1 (Run 3)

**Date:** 2026-07-10T19:47:00Z
**Hypothesis:** h-e1
**Run:** 3
**Final Status:** FAIL
**Failure Type:** INCOMPLETE_EXECUTION

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Best Metric | N/A (incomplete) | 93.85% (ERM, n=2) | N/A |

**Note:** Only 2/15 experiments completed (ERM baseline only). Cannot compute Joint SAM+SWA vs baseline comparison.

## Root Cause Analysis

- **Sequential Execution Bottleneck**: Implementation uses sequential experiment execution instead of parallel processing, resulting in 72-minute total runtime (15 experiments × 4.8 min/experiment) vs expected 18-20 minutes with parallelization
- **Missing Parallelization**: Despite 4 CPU cores available, `run_experiments.py` executes experiments in serial `for` loops without multiprocessing/joblib
- **CelebA Not Implemented**: Hypothesis requires "BOTH ColoredMNIST AND CelebA" cross-dataset validation, but CelebA experiments were not configured or launched
- **Time Estimation Error**: Underestimated experiment duration by 12× (expected 5 min total → actual 60+ min for ColoredMNIST only)

## Lessons Learned

1. **Always Profile Before Scale**: Single experiment took 4-5 minutes, not the assumed 20 seconds. Profiling one full run before launching 15× would have revealed the bottleneck early.
2. **Parallel-by-Default for Independent Experiments**: 15 independent experiments with no cross-dependencies should default to parallel execution (`joblib.Parallel` or `multiprocessing.Pool`), not sequential loops.
3. **Validate Dataset Availability Before Launch**: Hypothesis explicitly requires CelebA, but no CelebA data loading or training code exists in the implementation. Should have verified dataset setup before claiming "ready for experiments."
4. **Realistic Time Budgets**: 100-epoch ResNet-18 training (even on MNIST) requires ~5 minutes with modern hardware. Future estimates should benchmark 1 seed first, then scale linearly with safety margin (1.5-2×).
5. **Synchronous Validation Window**: Unattended pipeline cannot wait 60+ minutes for experiments. Need either (a) parallel execution to fit within ~15-20 min window, or (b) asynchronous validation mode where experiments complete in background and pipeline resumes later.

## Feedback for Next Phase

### Suggested Modifications

- **Narrow Hypothesis Scope**: Split H-E1 into H-E1-R1 (ColoredMNIST only, single-dataset PoC) and H-E1-R2 (CelebA extension after ColoredMNIST success)
- **Add Parallel Execution**: Implement `joblib.Parallel(n_jobs=4)` wrapper around experiment loop
- **Validate Datasets Upfront**: Before claiming implementation complete, run smoke test for ALL required datasets (ColoredMNIST + CelebA)
- **Asynchronous Validation Option**: Consider allowing experiments to run in background with auto-completion (scripts already implemented: `complete_phase4_validation.py` exists)

### What NOT To Do

- **Do NOT add more sequential experiments**: Current architecture cannot scale beyond 15 experiments without exceeding time budget
- **Do NOT implement CelebA without parallelization**: Adding 15 more sequential experiments (CelebA) would push total time to 2.5+ hours
- **Do NOT skip dataset smoke tests**: Assuming datasets "just work" led to discovering CelebA missing at experiment launch time

### What Showed Promise

- **Implementation Quality**: ERM baseline experiments ran successfully with correct metrics (worst-group accuracy computed properly, validation curves show learning)
- **Auto-Completion Infrastructure**: Background scripts (`complete_phase4_validation.py`, `wait_and_generate_validation.py`) successfully monitor experiment PID and will auto-generate validation when complete
- **Config-Driven Architecture**: Clean separation of experiment logic, configuration, and training code makes it easy to add parallel execution wrapper

## Execution Context

### Completed Experiments (2/15)
1. ERM/ColoredMNIST/seed=42: Test WG Acc = 93.80%
2. ERM/ColoredMNIST/seed=123: Test WG Acc = 94.91%

### In Progress (1/15)
- ERM/ColoredMNIST/seed=456: Epoch 75/100 at validation time

### Not Started (12/15)
- SAM-only: 0/3 seeds
- SWA-only: 0/3 seeds
- Joint SAM+SWA: 0/3 seeds (**primary hypothesis**)
- Sequential SAM→SWA: 0/3 seeds
- CelebA: 0/15 experiments (not implemented)

### Active Processes
- Main experiment: PID 3146982 (147% CPU, expected completion 2026-07-10T20:45:00Z)
- Auto-completion: PID 3154235 (waiting for main experiment)

---

## Recommendation

**Route to Phase 2A** for hypothesis refinement:
1. Narrow scope to single-dataset PoC (ColoredMNIST only)
2. Add parallel execution architecture
3. Validate CelebA dataset availability before re-attempt

**Alternative**: Wait for auto-completion (~60 min) to get ColoredMNIST results, then assess if single-dataset evidence is sufficient for gate decision (though hypothesis explicitly requires "BOTH datasets").

---
*For cross-phase reference*
*Written at: 2026-07-10T19:47:00Z*
