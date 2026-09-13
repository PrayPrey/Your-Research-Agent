# Per-Hypothesis Context: H-M1
# Generated JIT by Phase 2C step-01 from 02b_verification_plan.md

## Hypothesis Information

- **ID:** H-M1
- **Type:** MECHANISM
- **Statement:** Under controlled training conditions (DeepSeek-Coder-7B, APPS train split), SFT trained on APPS achieves <60% pass@1 on LiveCodeBench-Hard, confirming that APPS training data creates a signal void (near-zero correct solution coverage) at hard benchmark difficulty levels.
- **Rationale:** Tests the first causal step: whether the "SFT signal void" premise is empirically grounded. If SFT achieves high accuracy on hard benchmarks, the entire mechanistic explanation collapses. Must be confirmed before testing the RLEF advantage mechanism.
- **Gate:** MUST_WORK
- **Prerequisites:** H-E1 (VALIDATED)

## Experimental Setup (from Phase 2A via Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | APPS (codeparrot/apps) | 5000 train split Python problems with unit tests; difficulty stratified (intro/interview/competition); provides both SFT targets and measurable difficulty gradient |
| **Evaluation** | LiveCodeBench (2024-Q4 snapshot) | Hard difficulty tier; contamination-free (post-training-cutoff problems); correctness-only via bigcode-evaluation-harness |
| **Model** | DeepSeek-Coder-7B-base | Public weights; strong code base; not saturated on HumanEval from base; HuggingFace: deepseek-ai/deepseek-coder-7b-base |

## Variables

- **Independent:** Training method (SFT); benchmark difficulty level
- **Dependent:** SFT pass@1 at LiveCodeBench-Hard
- **Controlled:** Same APPS train split as H-E1; DeepSeek-Coder-7B-base; bigcode-harness correctness-only

## Success Criteria (PoC)

- **Primary:** SFT pass@1 on LiveCodeBench-Hard < 60%
- **Secondary:** SFT training loss lower on APPS-Introductory than APPS-Competition (difficulty-graded signal)

## Failure Response

- IF SFT pass@1 ≥ 60%: EXPLORE — APPS covers hard difficulty better than assumed (A1 violated); signal void framing needs revision

## Dependencies & Context

- **H-E1:** VALIDATED (RLEF-Fraction achieves ≥1.5× gap ratio at LiveCodeBench-Medium/Hard vs HumanEval)
- **SFT model reuse:** H-M1 uses the SFT baseline from H-E1 — no additional training required
- **Key Assumption A1:** APPS covers medium difficulty but has sparse fully-correct examples at hard (competition) difficulty

## Baseline Performance Reference (from Phase 2B)

| Method | HumanEval | MBPP | LiveCodeBench-Medium | LiveCodeBench-Hard |
|--------|-----------|------|----------------------|--------------------|
| SFT on APPS (DeepSeek-Coder-7B) | ~40-50% | ~15-25% | ~5-10% | Expected <60% |
