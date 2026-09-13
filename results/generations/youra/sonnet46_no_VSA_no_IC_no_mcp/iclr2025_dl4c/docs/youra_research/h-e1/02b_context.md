# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Prerequisites:** None

## Hypothesis Statement

Under controlled conditions (DeepSeek-Coder-7B, APPS training, bigcode-harness correctness-only evaluation), RLEF using fraction-of-tests reward achieves Δ(RLEF-Fraction, SFT) at LiveCodeBench-Medium/Hard ≥ 1.5× Δ at HumanEval (p < 0.05, bootstrap), confirming the difficulty-scaling phenomenon exists.

## Rationale

Existence hypothesis — verifies the central difficulty-scaling phenomenon before testing mechanism. Without confirming the phenomenon, mechanism testing is premature.

## Experimental Setup

**Dataset:**
- Name: APPS (Automated Programming Progress Standard)
- Type: standard
- Source: Hendrycks et al., 2021
- Path: codeparrot/apps (HuggingFace)
- HF identifier: "codeparrot/apps"
- Hypothesis Fit: 5000 Python problems spanning easy-to-competition difficulty; provides SFT targets (correct solutions) and RLEF execution signals (test pass/fail); natural difficulty gradient (intro/interview/competition)

**Evaluation Benchmarks:**
- HumanEval: 164 problems (easy)
- MBPP: 374 problems (medium-easy)
- LiveCodeBench 2024-Q4 snapshot: Easy/Medium/Hard splits (~400+ problems each)
- Evaluation harness: bigcode-evaluation-harness (pin commit), correctness-only mode

**Model:**
- Name: DeepSeek-Coder-7B-base
- Type: decoder-only transformer, code-specialized
- Source: deepseek-ai/deepseek-coder-7b-base (HuggingFace)
- HF identifier: "deepseek-ai/deepseek-coder-7b-base"
- Hypothesis Fit: Public weights, strong code generation, not saturated at HumanEval from base weights; 7B scale allows partial solutions on hard APPS problems

## Variables

- **Independent:** Training method (SFT vs RLEF-Fraction) × Benchmark difficulty level
- **Dependent:** Δ pass@1 (RLEF-Fraction − SFT) at each benchmark
- **Controlled:** DeepSeek-Coder-7B base, APPS train split, matched gradient steps, bigcode-harness correctness-only, LiveCodeBench 2024-Q4

## Baselines

| Method | Expected Performance |
|--------|---------------------|
| SFT on APPS (DeepSeek-Coder-7B) | ~40-50% HumanEval; ~15-25% MBPP; ~5-10% LiveCodeBench-Medium |
| RLEF-Binary on APPS | +5-10% over SFT at HumanEval |
| CodeRL (Le et al., 2022) | +4.3% pass@1 HumanEval vs SFT |

## Success Criteria (PoC)

- Primary: Δ_LiveCodeBench / Δ_HumanEval ≥ 1.5 with p < 0.05 (bootstrap)
- Secondary: Both Δ values positive (RLEF-Fraction > SFT at all difficulty levels)

## Failure Response

IF Δ ratio < 1.5: STOP — phenomenon not demonstrated; reassess hypothesis.

## Phase 2B Gate Validation

- Dataset tests IV manipulation: ✅ (SFT vs RLEF-Fraction on same APPS data)
- Dataset measures DV: ✅ (bigcode-harness pass@1 on HumanEval + LiveCodeBench)
- Model within scope: ✅ (7B base, not instruct; available open-source)
- No critical issues: ✅ (SFT ceiling check built into verification protocol)
