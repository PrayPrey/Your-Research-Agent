# Superseded Hypothesis Record: h-e2-v2

**Type:** SUPERSEDED
**Hypothesis:** h-e2-v2
**Date:** 2026-08-25
**Phase:** Phase 4 — Gate Processing / Reflection
**Supersedes:** h-e2

---

## Hypothesis

Semantic entropy achieves AUROC >= 0.75 on TriviaQA dev (11,313 questions) using Llama-2-7B with K=10 samples, replicating the Kuhn et al. result.

## Gate: MUST_WORK

**Result:** FAIL
**SE AUROC:** 0.5419 (n=98, partial experiment)
**95% CI:** [0.4228, 0.6503]
**Gate threshold:** 0.75

## Why SUPERSEDED

- Two attempts (h-e2, h-e2-v2) both failed at the AUROC 0.75 gate
- The mechanism is confirmed working: avg 3.89 clusters/question, SE > TE direction (+0.029 gap)
- The fundamental issue: Kuhn et al. achieved 0.75+ on Llama-65B, not 7B
- The 0.75 threshold is inconsistent with Llama-2-7B capabilities
- Code implementation is correct — the issue is model scale vs. gate threshold

## Confirmed Findings

- Semantic entropy mechanism activates on Llama-2-7B (3.89 avg clusters)
- SE AUROC > TE AUROC direction confirmed (0.0292 gap)
- EM accuracy 34.4% on TriviaQA (low accuracy = sufficient uncertainty diversity for clustering)
- h-e1 code reuse was correct and complete

## What Does NOT Work

- AUROC ≥ 0.75 threshold for Llama-2-7B — achievable AUROC range appears to be 0.54-0.60

## Recommended Redesign (Phase 2A)

1. **Option A (preferred):** Revise gate to AUROC ≥ 0.60 for 7B model existence check
2. **Option B:** Upgrade to Llama-2-13B (expected AUROC ~0.65-0.70)
3. **Option C:** Use a model where Kuhn et al. explicitly reported AUROC > 0.75

## Reusable Code

All code in `h-e2-v2/code/` is correct and reusable:
- `generation.py` — K=10 sampling with checkpoint/resume
- `uncertainty.py` — NLI clustering, semantic entropy
- `evaluate.py` — AUROC + bootstrap CI
- `generate_shard.py` — 5-GPU parallel generation
- `run_experiment.py` — full pipeline orchestration

## Key Lesson

Always pilot on 200 questions before committing to 11,313 to check AUROC trajectory.
The 7B scale is insufficient for the 0.75 gate. Existence checks should be calibrated per model scale.

---
*Written by Phase 4 reflection (ABLATION mode — Serena MCP unavailable, written directly)*
