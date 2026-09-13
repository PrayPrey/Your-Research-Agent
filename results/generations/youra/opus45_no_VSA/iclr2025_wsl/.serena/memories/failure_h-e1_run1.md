# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-10T06:00:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** IMPLEMENTATION_PROXY_MISMATCH

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| R² | -2.9546 | 0.0142 | -2.9688 (-20893%) |

## Root Cause Analysis

- Used random projection proxy instead of pretrained SANE encoder
- HSG-AIML/SANE checkpoint not available/loaded
- Random projection provides no learned weight-space structure
- Result reflects failure of random projections, not learned embeddings

## Lessons Learned

1. SANE requires actual pretrained checkpoint — random projection is not a valid proxy
2. Cross-architecture transfer (ConvNet→ViT) is challenging even for baseline
3. Baseline R²=0.0142 shows some signal transfers; learned approach needs proper implementation
4. Before abandoning learned embeddings approach, obtain actual SANE checkpoint

## Feedback for Next Phase

### Suggested Modifications
- Download actual SANE checkpoint from HSG-AIML/SANE repository
- Use official SANE tokenization (not ad-hoc chunking)
- Consider training minimal SANE-like encoder if checkpoint unavailable

### What NOT To Do
- Do not use random projection as proxy for learned embeddings
- Do not conclude learned embeddings fail based on random projection results

### What Showed Promise
- Mechanism verification passed (output shape, variance, decorrelation)
- Baseline shows positive R² — some cross-architecture signal exists
- Infrastructure for comparison is working correctly

---
*For cross-phase reference*
*Written at: 2026-08-10T06:00:00Z*
