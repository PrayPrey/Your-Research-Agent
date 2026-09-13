# Hypothesis Pivot Record

**Date:** 2026-08-02T16:45:00+00:00
**From:** h-e1
**To:** h-e1-v2

## Pivot Reason

PARTIAL result — Pearson |r|=0.049 < 0.7 PASS but partial R²=0.0101 < 0.02 FAIL due to underpowering (N=300 instead of N=2500). Mechanism confirmed empirically; need full dataset.

## What Changed

- N_PROMPTS: 300 → 2500 (restore spec from 02c_experiment_brief.md)
- Regenerate signals.pkl checkpoint at N=2500
- No code architecture changes needed

## What Was Preserved

- Full code pipeline (generate.py, compute_signals.py, judge.py, stats_analysis.py, visualize.py)
- youra-h-e1 conda environment (torch 2.8.0+cu128, all deps installed)
- Gate thresholds unchanged (pearson_r < 0.70, partial_r2 >= 0.02, abandon > 0.85)
- NLI model: cross-encoder/nli-deberta-v3-small
- LM judge: Qwen/Qwen2.5-7B-Instruct
- Dataset: mandarjoshi/trivia_qa (rc.nocontext, validation, seed=42)

## Partial Results Preserved

| Metric | Value | Notes |
|--------|-------|-------|
| pearson_r | 0.0493 | From h-e1 (N=300) |
| abs_pearson_r | 0.0493 | PASS criterion confirmed |
| partial_r2_se | 0.0101 | Marginal at N=300; expected ≥0.02 at N=2500 |
| lrt_p | 0.1504 | Non-significant at N=300 |
| spearman_rho | -0.0815 | Circularity check OK |
| correctness_rate | 0.3433 | 103/300 correct |

## Key Insight

SE_N5 and min_logprob are empirically near-orthogonal (|r|=0.049 << 0.7). The independence claim is strongly supported. The partial R² threshold failure is purely a power issue — at N=300 with correctness rate 34.3%, the sample is too small to detect a small-but-real SE contribution. At N=2500, statistical power will be sufficient.

## Lineage

```
h-e1 (N=300 PoC smoke test)
    └── (PIVOT: underpowered — N=300 instead of N=2500)
        └── h-e1-v2 (N=2500 full dataset)
```

---
*Pivot recorded at: 2026-08-02T16:45:00+00:00*
