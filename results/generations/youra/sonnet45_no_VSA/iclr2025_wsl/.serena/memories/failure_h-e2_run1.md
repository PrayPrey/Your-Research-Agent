# Phase 4 Failure Record: h-e2 (Run 1)

**Date:** 2026-07-11T14:51:00Z
**Hypothesis:** h-e2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** FUNDAMENTAL_API_MISMATCH

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Functional Equivalence Tests Passed | 0/10 | N/A | N/A |
| Max Deviation | 2.67e+02 | 1.0e-6 (threshold) | 267,000× over threshold |

## Root Cause Analysis

- **NFN Library Design Mismatch**: The NFN library's `network_spec_from_wsfeat()` function is designed for **weight-space learning** (meta-learning where neural network weights are INPUT data to models), NOT for extracting permutation groups from single pre-trained models
- **API Incompatibility**: The function expects weights in shape `[BatchSize, Channels, ...]` where BatchSize represents a batch of DIFFERENT neural networks. ResNet-18 state_dict has weights in shape `[C_out, C_in, H, W]` for a SINGLE network
- **Fundamental Misunderstanding**: The hypothesis incorrectly assumed NFN library extracts symmetries from single models; the library actually trains models that PROCESS network weights as data
- **Manual Fallback Also Failed**: Even manual permutation extraction failed functional equivalence testing (0/10 tests passed, all deviations 99.6 to 267 vs threshold 1e-6), suggesting deeper architectural incompatibility beyond just NFN API design

## Lessons Learned

1. **Verify Library Purpose Before Implementation**: Always check if a library's design aligns with research goals. NFN is for meta-learning, not checkpoint analysis
2. **API Design Matters**: Libraries designed for batch processing of networks cannot be repurposed for single-model symmetry extraction without fundamental redesign
3. **Test Assumptions Early**: The hypothesis assumed NFN could extract permutation groups from pre-trained models, but this was never the library's intended use case
4. **Manual Fallback Validation**: Even when the primary approach fails, testing the underlying concept (permutation invariance) revealed the approach may be fundamentally flawed for ResNet-18
5. **Research Direction Incompatibility**: NFN's weight-space learning paradigm is orthogonal to the goal of analyzing pre-trained model symmetries

## Feedback for Next Phase

### Suggested Modifications
- Consider alternative equivariance libraries designed for single-model analysis (e.g., e2cnn, escnn)
- Explore manual permutation specification approaches (validated in fallback, but needs better permutation design)
- Investigate whether ResNet-18's architecture actually supports the assumed permutation symmetries
- Research libraries specifically designed for neural network symmetry analysis, not meta-learning

### What NOT To Do
- Do NOT attempt to adapt NFN library for single-model checkpoint analysis
- Do NOT assume weight-space learning tools can be repurposed for pre-trained model analysis
- Do NOT rely on libraries without verifying their intended use case matches research goals
- Do NOT proceed with permutation-based approaches without first validating functional equivalence

### What Showed Promise
- Manual permutation group specification worked (implementation-wise), though functional equivalence failed
- The validation framework (checkpoint loading, permutation generation, functional testing) is sound
- The experimental design correctly identified the API mismatch early

---

## Impact Assessment

**Blocking Effect**: This hypothesis (h-e2) is a **foundation hypothesis** with MUST_WORK gate.

**Downstream Impact**:
- ❌ Cannot proceed to h-m1 (NFN encoder integration) - blocked by h-e2 failure
- ❌ Cannot proceed to h-m2 (pipeline integration) - blocked by h-e2 failure  
- ❌ Main hypothesis H-PracPrec-v1 cannot be validated using NFN library approach

**Recommended Routing**: **Phase 0** - Re-brainstorm hypothesis with compatible methodologies

---

*For cross-phase reference*
*Written at: 2026-07-11T14:51:00Z*