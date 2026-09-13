# Phase 6.5 Changelog

## Round 1 Revisions (06_paper.md → 06_paper_r1.md)

### MAJOR-1: MOHAWK Drift Ratio Clarification
**Location**: Section 5.3, Table in Section 5.1
**Before**: ">2.0"
**After**: "2.02 (computed as 13.79/6.84 from raw drift values)"
**Reason**: Vague quantification flagged as hiding unfavorable precision

### MAJOR-2: H-M3 Failure Reframing
**Location**: Section 5.4
**Before**: "H-M3 failure is attributed to PoC mode"
**After**: "H-M3 was **not supported** (p=0.881 indicates no detectable interaction effect)"
**Reason**: Original framing was defensive/excuse-making

### MAJOR-3: Mechanism Claim Softening
**Location**: Section 6.1
**Before**: "Token-level objectives are position-agnostic: Aligning individual Q/K projections..."
**After**: "**We hypothesize that** token-level objectives are position-agnostic... This would create supervision..."
**Reason**: Mechanism was stated as finding without direct evidence

## Round 2 Revisions

No revisions needed. All R2 findings were MINOR and collected in human_review_notes.md.

## Files Modified

| Original | Revised | Status |
|----------|---------|--------|
| 06_paper.md | 06_paper_r1.md | R1 revisions applied |
| 06_paper_r1.md | 06_paper_final.md | Copied (no R2 changes needed) |

## Deferred to Human Review

See `065_human_review_notes.md` for 7 minor issues:
- Consistency (5x vs 5.0x)
- Missing source data for CI brackets
- Table design (MUST_WORK gate with FAIL result)
- p-value interpretation clarity
- Sample size confirmation
- Per-layer divergence unsupported claim
- References expansion needed
