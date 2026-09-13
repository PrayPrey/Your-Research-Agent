# Phase 4.5 Synthesis: H-CalibDiff-v1 (LLM Calibration Code Verifier)

**Date:** 2026-03-23
**Archive Path:** docs/youra_research/20260316_verifia/_archive/20260318T120129_routing_recovery/
**Output:** 045_validated_hypothesis.md (v2.0)

## Key Outcomes

- Predictions supported: 0/3 (P1, P2, P3 all REFUTED as universal claims)
- Sub-hypotheses PASS: 4/5 (h-e1, h-m1, h-m2, h-m3 PASS; h-m4 MUST_WORK FAIL)
- Routing: Phase 0 (MUST_WORK FAIL on h-m4)

## Refined Core Statement

ΔECE architecture-dependent:
- DeepSeek-Coder-6.7B: ΔECE=+0.298 (CI=[0.285, 0.312]) ✅ POSITIVE
- Llama3-8B: ΔECE=+0.003 (CI includes 0, p=0.256) ⚪ NEAR-ZERO
- CodeLlama-7B: ΔECE=−0.249 (CI entirely negative) ❌ INVERTED

## Main Theoretical Contribution

Architecture-stratified analysis of P(True) calibration under difficulty stratification.
Key finding: code-adapted fine-tuning (CodeLlama) INVERTS calibration direction on easy MBPP-style problems.
Code-specialized training (DeepSeek) shows expected positive ΔECE.

## Infrastructure Reusable

- k=5 tier stratification (Jaccard 0.45-0.55 validated)
- P(True) logprob extraction (non-degenerate for all 3 models)
- ECE computation with bootstrap CI and temperature scaling
- All components in archive folders h-e1..h-m4/code/

## Lessons for Future Pipelines

- Architecture identity (not just capability) determines calibration direction; test multiple architectures per category
- CodeLlama-type models (code-adapted from general base) may show calibration inversion on easy domain tasks
- k=5 degenerate easy tier for weak models (CodeLlama HumanEval n_easy=0); use larger k or focus on MBPP
- T*=3.95 extreme scaling is a red flag for systematic overconfidence; investigate before architecture comparison
