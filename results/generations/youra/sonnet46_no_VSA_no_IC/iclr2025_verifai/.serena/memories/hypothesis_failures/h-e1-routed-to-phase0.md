# Hypothesis h-e1: ROUTED_TO_PHASE_0

**Date:** 2026-08-22
**Hypothesis:** h-e1
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Claim
ruff and mypy flag ≥70% of failed HumanEval+MBPP round-0 problems with ≥1 actionable error.

## Why FAIL
GATE_MIN_SCALES=2 not met: only 1 of 2 required model scales ran (llama-3.1-8b-instruct debug n=10). codellama-7b-instruct experiment did not complete. Full dataset (n=538) not evaluated.

## Partial Evidence
- llama-3.1-8b-instruct (n=10): SA fire rate on failed problems = 88.9% (exceeds 70% threshold)
- False positive rate = 0%
- McNemar p=0.0 — individual model gate PASS
- SA oracle (ruff+mypy subprocess) confirmed functional

## Root Causes
1. Experiment runner did not execute second model scale
2. Only debug run (n=10) completed instead of full n=538
3. GATE_MIN_SCALES=2 is hard gate requirement — partial single-model evidence insufficient

## Lessons Learned
- Validate GATE_MIN_SCALES completion before gate evaluation
- Debug runs must not substitute for full-scale experiments in gate decisions
- SA oracle approach is promising — infrastructure failure, not conceptual failure

## Next Action
Route to /phase0-brainstorm for hypothesis redesign or experiment infrastructure repair.
