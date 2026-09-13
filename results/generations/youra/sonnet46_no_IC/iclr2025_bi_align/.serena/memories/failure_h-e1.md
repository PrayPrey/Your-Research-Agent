# Failure Record: h-e1 — Phase 4 MUST_WORK Gate FAIL

**Date:** 2026-08-04
**Phase:** 4 (PoC Implementation & Validation)
**Gate:** MUST_WORK → FAIL
**Outcome:** ROUTED_TO_PHASE_0

## Hypothesis

h-e1 (EXISTENCE): Verify HumaneEval v1 sub-dimension columns accessible AND AlpacaEval 2.0 covers >= 12 of 15 HumaneEval v1 frontier LLMs (N >= 12 intersection, fuzz.ratio > 85).

## Gate Checks

| Check | Result |
|-------|--------|
| A1: Sub-dimension cols >= 3 | PASS (24 cols found) |
| A2: N_intersection >= 12 | FAIL (N=0) |
| **Overall** | **FAIL** |

## Root Cause

AlpacaEval 2.0 leaderboard covers **2023-2024 era models** (Claude 3.5 Sonnet, GPT-4 Turbo, Gemini Pro). HumaneEval v1 evaluates **2025/2026 frontier models** (gpt-5, grok-4, claude-opus-4.1, gemini-2.5-pro, llama-4-maverick). Non-overlapping model generations → N_intersection = 0.

Best fuzz score: llama-3.1-405b-instruct vs "Llama 3.1 405B Instruct" = 73.9 (below threshold 85).

## Key Discoveries

1. HumaneEval v1 `baseline_scores.csv` lives in **repo root** (not `tables/`). Direct raw URL returns 404. Git clone fallback works.
2. Column names use hyphen format (`respect-user-attention`, not `autonomy-preservation`). A1 confirmed with 8 principle cols + CI bounds = 24 total.
3. AlpacaEval 2.0 has 211 models, none from 2025/2026 era.

## Recommendation for Redesign

Replace AlpacaEval 2.0 with a benchmark covering 2025/2026 frontier models:
- **Chatbot Arena ELO** (lmarena.ai) — continuously updated, covers frontier models
- All code in `h-e1/code/` reusable; only `ALPACA_CSV_URL` in `config.py` needs to change
- Runtime: ~5 min, CPU only, no API keys needed

## Artifacts

- `h-e1/results/gate_result.json`
- `h-e1/04_validation.md`
- `h-e1/reflection_report.md`
- `h-e1/code/` (6 Python modules, fully validated)
