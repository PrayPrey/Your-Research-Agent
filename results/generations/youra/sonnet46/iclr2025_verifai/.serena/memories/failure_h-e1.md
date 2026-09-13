# Failure Record: h-e1 Phase 4 MUST_WORK FAIL

## Hypothesis
h-e1: "LLMs exhibit measurably higher ECE on hard-tier code problems vs. easy-tier using P(True) logprob elicitation"

## Phase
Phase 4 (Experiment Execution)

## Failure Type
MUST_WORK_FAIL → ROUTED_TO_PHASE_0

## Gate Result
FAIL: ΔECE=NaN for all 3 LLM families (llama3-8b, codellama-7b, deepseek-coder)
- n_hard=0, n_easy=0 (all 540 problems assigned "unknown" difficulty)
- p_fdr=1.0 (statistical test not executable without stratification)

## Root Cause
The difficulty tier assignment depends on an external EvalPlus leaderboard CSV (aggregate pass@1 per model per problem). Task T-DATA-1 (download CSV) was listed as "todo" but never executed. The data_loader.py `assign_difficulty_tiers()` function falls back to "unknown" when CSV is absent.

## What Worked
- P(True) logprob elicitation: ACTIVATED (values 0.57-0.91 for all 3 models)
- EvalPlus ground truth evaluation: Working for HumanEval+ (164) + MBPP+ (378) = 542 problems
- Solution generation: Complete for 3 HF models, k=5 solutions each
- ECE_overall: Computed (0.49, 0.52, 0.14 for llama3-8b/codellama-7b/deepseek-coder)
- EvalPlus Python API (check_correctness): Fixed and working after multiple bug fixes

## Bugs Fixed During Phase 4
1. Gated model → switched to NousResearch mirror (non-gated)
2. Python buffering with conda run → use -u flag + PYTHONUNBUFFERED=1
3. evalplus subprocess used wrong Python env → use sys.executable
4. EvalPlus CLI interface mismatch → replaced with Python API (check_correctness)
5. OpenAI API key unavailable → replaced gpt35 with deepseek-coder
6. Solution indentation: strip() removes leading indent → prepend prompt + re-indent body
7. MBPP ground truth pickle cache fails → fallback to trusted_exec directly

## Key Insight for Redesign
The difficulty tier definition method is fragile. Better approach for Phase 0 redesign:
- OPTION A: Bootstrap difficulty from the experiment's own pass@1 data (no external CSV needed)
- OPTION B: Use fixed problem sets with known difficulty (e.g., HumanEval hard subset from literature)
- OPTION C: Define difficulty as model-specific (hard = pass@1 < 0.2 for THAT model)

## Cascade Effect
h-e1 is a foundation hypothesis. Dependents h-m1/h-m2/h-m3/h-m4 all CASCADE_FAILED.

## Routing
ROUTED_TO_PHASE_0 (fundamental redesign of difficulty tier mechanism required)

## Timestamp
2026-03-18T02:00:00+00:00
