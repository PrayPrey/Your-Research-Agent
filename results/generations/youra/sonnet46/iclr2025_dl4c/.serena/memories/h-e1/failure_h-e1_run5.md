# Phase 4 Failure Record: h-e1 (Run 5)

**Date:** 2026-03-15T15:30:00Z
**Hypothesis:** h-e1
**Run:** 5
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| ZRF (binary) | 1.0 | N/A (target<0.8) | FAIL |
| ZRF (ratio) | 1.0 | N/A (target<0.8) | FAIL |
| ZRF Reduction | 0.0% | N/A (required≥20%) | FAIL |
| SNR Ratio | 1.0x | N/A (required≥1.5x) | FAIL |

## Root Cause Analysis

- S_term threshold=0.85 selects competition/interview problems (~2361/5000) that are inherently too hard for Qwen2.5-Coder-7B-Instruct → reward=0 on all rollouts
- max_completion_length=512 truncates nearly all solutions (clipped_ratio=0.875–1.0) — competition-level programming requires 100–400+ lines
- Degenerate GRPO: all advantages=0, all gradient signals=0
- Design mismatch: h-e1 EXISTENCE hypothesis was about prescreening (direct inference), but Phase 4 experiment ran GRPO training with ZRF/SNR gates

## Lessons Learned

1. Prescreening (EXISTENCE) and GRPO training (MECHANISM) gates must be evaluated separately — using GRPO ZRF gates on an inference prescreening hypothesis is a category error
2. S_term threshold must be empirically calibrated via inference, not problem category labels (competition=0.95, interview=0.75, introductory=0.25)
3. For Qwen2.5-Coder-7B, partial tractability zone is S_term ∈ [0.3, 0.6] on introductory problems (APPS difficulty=0), NOT competition/interview level
4. max_completion_length≥1024 required for programming tasks (512 is insufficient)
5. ZRF=1.0 across all 27 steps and 6 runs (2 conditions × 3 seeds) — no partial success to build on

## Routing Decision

- **reflection_outcome**: ROUTED_TO_PHASE_0
- **Route**: Phase 0 (hypothesis redesign)
- **Reason**: Complete failure with zero reward across all conditions. No parameter adjustment can recover meaningful gradient signal. Fundamental redesign required.

## Proven Infrastructure (Reusable)

- TRL v0.29.0 GRPO API: `args=grpo_config`, `beta=kl_coef` — correct
- APPS dataset loading (codeparrot/apps HuggingFace cache at `~/.cache/huggingface/datasets/codeparrot___apps`)
- `s_term_labels.json` precomputed for 5000 train problems
- `PYTHONUNBUFFERED=1` required to prevent conda pipe buffer deadlock
- `device_map="cuda:0"` with `CUDA_VISIBLE_DEVICES=N` for single GPU isolation
- SFT checkpoint: `h-e1/code/sft_checkpoint/` available and verified

## Recommendations for Phase 0 Redesign

1. Calibrate S_term empirically via inference-only prescreening on APPS introductory split
2. Target S_term ∈ [0.3, 0.6] for 7B model (introductory/easy problems)
3. Increase max_completion_length to ≥1024 or 2048
4. Decouple EXISTENCE gate (prescreening.py) from MECHANISM gate (train_grpo.py)
5. Lower success threshold: fraction(k_pass≥2)≥10% may be more achievable than 20%

---
*For cross-phase reference*
*Written at: 2026-03-15T15:30:00Z*
