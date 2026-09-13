# Results

## Experiment Outcome: Incomplete

**Status**: FAILED (infrastructure crash at 53% completion)

The experiment did not complete. The pipeline crashed during the EVAF gating phase after processing 87 of 164 HumanEval problems (53%). No aggregate metrics could be computed.

## Execution Timeline

| Stage | Status | Progress |
|-------|--------|----------|
| Baseline generation | COMPLETE | 164/164 problems |
| Failure filtering | COMPLETE | Identified failing problems |
| EVAF gating | FAILED | 87/164 (~53%) |
| Metrics computation | NOT REACHED | — |
| Visualization | NOT REACHED | — |

**Start time**: 2026-08-18T13:59:28Z  
**Termination**: 2026-08-18T14:31:19Z (stalled/crashed)  
**Duration before failure**: ~32 minutes

## Failure Analysis

The experiment process stalled during EVAF gating at iteration 87. No error message was captured in the log—the process simply stopped producing output.

**Hypothesized Root Causes** (ordered by likelihood):

1. **GPU Memory Exhaustion (HIGH)**: CodeLlama-7b-Instruct inference on longer problems may have exceeded available GPU memory. The 7B parameter model in float16 requires ~14GB; combined with CodeT5-770M and problem context, complex problems could trigger OOM.

2. **Subprocess Timeout Escalation (MEDIUM)**: Generated code containing infinite loops or resource-intensive operations may have caused subprocess timeouts to cascade, eventually stalling the main process.

3. **System-Level Kill (MEDIUM)**: External OOM killer or resource limits may have terminated the process without generating an error log.

**Evidence**: No error trace captured, process simply stopped. This pattern is consistent with GPU OOM (which often hangs rather than crashes cleanly) or system-level termination.

## What We Observed Before Failure

During the successful portion (problems 1-87):

- Baseline generation completed for all 164 problems
- CodeT5-770M inference ran without issues
- CodeLlama-7b-Instruct generated critiques for 87 problems
- Execution gating ran subprocess tests for 87 problems

We cannot report accept rates or rejection breakdowns because the experiment did not complete and no intermediate results were saved. The implementation lacked checkpointing.

## Artifacts Generated

Despite the incomplete experiment, all implementation artifacts were created:

| File | Purpose | Status |
|------|---------|--------|
| config.py | Configuration constants | Complete |
| data.py | HumanEval data loading | Complete |
| model.py | BaselineModel + FeedbackModel | Complete |
| gating.py | Code extraction + test execution | Complete |
| metrics.py | Accept rate computation | Complete |
| visualize.py | Figure generation | Complete |
| train.py | Pipeline orchestration | Complete |
| experiment.log | Execution log | Partial (87 iterations) |

**Missing Artifacts**:
- results.json (per-problem results)
- metrics.json (aggregate metrics)
- Figures (gate metrics, accept distribution, rejection breakdown)

## Gate Verdict

**Gate Type**: MUST_WORK  
**Status**: FAILED (not satisfied)

The MUST_WORK gate requires accept rate measurement between 20-60%. With no metrics available, the gate cannot be evaluated. The experiment must be re-run with infrastructure fixes before proceeding to comparative evaluation.

## Comparison to Expectations

| Expected | Actual |
|----------|--------|
| Accept rate 20-60% | Not measured |
| Coverage >80% | Not measured |
| Complete execution | Crashed at 53% |
| Metrics JSON output | Not generated |
| 3 visualization figures | Not generated |

## Reproducibility Note

The implementation code is complete and passes unit tests. The failure occurred at runtime scale, not in the implementation logic. Future attempts should:

1. Add checkpointing to EVAF gating loop (save results every N iterations)
2. Profile GPU memory usage during CodeLlama inference
3. Consider model quantization (4-bit) to reduce memory footprint
4. Add explicit error handling and logging for GPU OOM conditions
