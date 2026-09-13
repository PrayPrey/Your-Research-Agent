# Phase 2B Context: h-m3

**Generated**: 2026-08-28 (Synthesized from pipeline state)

## Hypothesis

**ID**: h-m3  
**Type**: MECHANISM  
**Statement**: Citation velocity correlation with saturation detection yields >80% precision (detected saturation → actual paradigm shift) and >70% recall (actual shifts → detection within 6mo prior) on 15-20 benchmark cases

**Gate**: MUST_WORK  
**Prerequisites**: h-m1, h-m2  
**Status**: PLANNING

## Verification Protocol

### Success Criteria

1. **Precision**: >80% (detected saturation events → actual paradigm shifts within dataset)
2. **Recall**: >70% (actual paradigm shifts → saturation detected within 6mo prior)
3. **Sample Size**: 15-20 benchmark cases (minimum statistical validity)

### Measurement Protocol

- **Saturation Detection**: Apply h-m1 dual-metric detector (score convergence + velocity decay)
- **Citation Velocity Analysis**: Track citation accumulation rate before/after paradigm shift events
- **Correlation Test**: Measure temporal alignment between saturation detection and shift adoption
- **Validation**: Use known paradigm shift dates (GPT-3 2020, ViT 2021, LLaMA 2023) as ground truth

### Expected Baseline

- Random detector: ~33% precision/recall (chance)
- Single-metric detector: ~50-60% (from h-m1 validation)
- Dual-metric + citation: target >80% precision, >70% recall

### Data Requirements

- **Benchmark leaderboards**: 15-20 cases with sufficient history (2015-2024)
- **Citation data**: Per-benchmark paper citation counts with monthly resolution
- **Ground truth**: Documented paradigm shift adoption dates

## Dependency Chain

```
h-e1 (leaderboard data) → h-m1 (saturation detector) → h-m2 (temporal validation) → h-m3 (citation correlation)
```

h-m3 validates whether citation velocity adds predictive power beyond saturation detection alone.

## Notes

- Phase 2B verification plan was not generated (status=PLANNING)
- This context synthesized from pipeline state for Phase 2C workflow continuity
- Full 02b_verification_plan.md should be generated via `/phase2b-planning h-m3` for complete research lineage
