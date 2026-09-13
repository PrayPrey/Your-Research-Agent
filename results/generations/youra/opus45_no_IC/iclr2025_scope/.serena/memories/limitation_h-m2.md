# H-M2 Limitation Record

## Hypothesis
**H-M2**: High-entropy tasks tolerate eviction better - stratified by entropy, high-entropy group shows higher accuracy retention under eviction.

## Gate Type
SHOULD_WORK (optional validation)

## Status
**FAILED** - Documented as limitation, pipeline continues.

## Failure Details

### Root Cause
Accuracy measurement inadequate for LongBench-v2 answer formats:
- Simple string matching failed to capture correct answers
- Baseline accuracy = 0% for all 30 samples
- Retention metric undefined (division by zero)

### Technical Details
- Dataset: LongBench-v2 (THUDM/LongBench-v2)
- Model: Llama-2-7b-hf
- Samples: 30 (5 per domain, PoC mode)
- Eviction ratios tested: 1.0, 0.4

### Why Accuracy Failed
LongBench-v2 answers are:
- Multi-sentence paragraphs
- JSON structures
- Multiple valid phrasings
- Require semantic matching, not substring

## Impact
- H-M2 mechanism remains **theoretically plausible** (H-M1 proved entropy variance exists)
- Cannot empirically validate eviction tolerance claim with current metrics
- Does not block H-M3/H-M4 (SHOULD_WORK gate)

## Recommendations for Future Work
1. Implement LLM-as-judge scoring
2. Use ROUGE/BERTScore for semantic similarity
3. Or switch to dataset with exact-match answers

## Related
- `mem:h-m1` - Entropy variance confirmed (F=38.05, p<0.001)
- `mem:h-e1` - Cluster existence confirmed (k*=3)

---
*Recorded: 2026-08-11*
*Phase 4 Validation*
