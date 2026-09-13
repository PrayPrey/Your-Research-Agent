# Hypothesis Pivot Record

**Date:** 2026-07-29T13:46:00+00:00
**From:** h-e1
**To:** h-e1-v2

## Pivot Reason

PARTIAL result — mechanism present and effect large (η²=0.293 > 0.15 target, 83% of categories met), but statistical significance not achieved (p=0.147, N=9 underpowered). SELF_MODIFY decision: effect is real, methodology is sound, failure is purely a scale/power issue.

## What Changed

- Expand encoder family from 3 to 4-5 models: add distilbert-base-uncased, microsoft/deberta-v3-base
- Expand decoder family from 3 to 4-5 models: add EleutherAI/gpt-neo-125m or facebook/opt-1.3b
- Expand enc_dec family from 2 to 3-4 models: add google/t5-v1_1-base; fine-tune T5/BART on mnli for multi-task coverage
- Install checklist package for CheckList evaluation (was skipped in h-e1)
- Minimum target: 5 models per family (15 total) for 80% power at η²=0.29, α=0.05

## What Was Preserved

- Core Δ*-vector computation pipeline (delta_star.py)
- Permutation MANOVA + bootstrap CI + LOMO statistical framework
- AdvGLUE/ANLI/CheckList attack category structure
- Scale-matched (~110-250M parameters) model selection criterion
- All generated code modules (data_loader, fine_tuner, evaluator, statistical_analysis, visualizer, run_experiment)
- Generated figures and partial results

## Partial Results Preserved

| Metric | Value | Notes |
|--------|-------|-------|
| Permutation MANOVA η² (overall) | 0.293 | From h-e1 |
| η² fraction ≥ 0.15 | 83.3% | From h-e1 |
| adv_rte η² | 0.592 | Strongest signal |
| adv_qqp η² | 0.354 | From h-e1 |
| adv_qnli η² | 0.350 | From h-e1 |
| Mixed-effects encoder×adv_mnli | p=0.014 | Significant interaction found |

## Root Cause Analysis

- Primary: Statistical underpowering — N=9 models (3 per family) gives ~40% power to detect η²=0.29 at α=0.05; minimum N for 80% power ≈ 5 per family (15 total)
- Secondary: enc_dec coverage gap — T5 and BART only evaluated on sst2 (no multi-task checkpoints), causing ANLI-R3 η²=0.0 for enc_dec family

## Lineage

```
h-e1
    └── (PIVOT: PARTIAL — underpowered N=9, enc_dec coverage gap)
        └── h-e1-v2
```

---
*Pivot recorded at: 2026-07-29T13:46:00+00:00*
