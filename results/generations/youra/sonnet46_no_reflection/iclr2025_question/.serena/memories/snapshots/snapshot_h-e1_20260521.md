# Hypothesis Completion Snapshot: h-e1
**Date:** 2026-05-21T09:05:00
**Hypothesis:** h-e1 (EXISTENCE)
**Statement:** Under Llama-3 base checkpoints on TriviaQA and NQ, SE and KLE show statistically higher AUROC than token-probability at both 8B and 70B scales.
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)

## Results
- Validation: FAIL
- Gate Type: MUST_WORK
- Reflection Outcome: ROUTED_TO_PHASE_0
- 8B/TriviaQA: SE=0.4735 vs TP=0.6835 (FAIL)
- 8B/NQ: SE=0.5524 vs TP=0.6551 (FAIL)
- degenerate_fraction: 0.894 (TriviaQA), 0.848 (NQ)

## Reflection Lessons
- SE/KLE < token_prob for Llama-3-Base on factual QA
- High degenerate_fraction → clustering collapse → SE not discriminative
- Token probability is a strong uncertainty predictor for factual QA
- Recommend: test instruction-tuned models, higher N_samples, or alternative UQ methods

## Cascade
- h-m1, h-m2, h-m3, h-m4: all CASCADE_FAILED

---
*Per-hypothesis snapshot for Phase 2A reference. See also: `mem:phase4_failures/failure_h-e1`*
