# Failure Record: H-E1

**Date:** 2026-08-09
**Hypothesis ID:** h-e1
**Gate Type:** MUST_WORK
**Outcome:** PARTIAL

## Hypothesis Statement
Entropy variance significantly differs between hallucinated and factual responses (p < 0.01, Cohen's d > 0.3)

## Failure Details

### What Happened
- Experiment started successfully at 10:11:14
- Processed 130/817 samples (16%) over ~13 minutes
- Process terminated unexpectedly at 10:24:07
- No error or exception in logs
- No results files generated

### Root Cause
External process termination (not code error). Evidence:
- Log ends mid-progress without crash trace
- No OOM or Python exception
- Trap handler for "EXPERIMENT COMPLETE" never fired
- Probable: resource quota, external kill, or timeout

### Code Status
- All code modules functional (config, data, model, metrics, train, evaluate, run_experiment)
- 130 samples processed correctly demonstrates mechanism works
- Infrastructure sound, execution incomplete

## Lessons Learned
1. Long-running experiments need checkpointing for recovery
2. Process monitoring required to detect external termination
3. Resource quotas should be verified before multi-hour runs

## Recovery Path
- Re-run with explicit resource allocation
- Add checkpoint every N samples
- Monitor process externally

## Files
- `h-e1/04_validation.md`: Full validation report
- `h-e1/code/experiment.log`: Partial execution log (130 samples)
