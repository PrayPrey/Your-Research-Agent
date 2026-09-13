# Adversarial Review Changelog

**Paper:** Ranking Stability Under Distribution Shift  
**Review Period:** 2026-08-29

---

## Summary

| Round | Changes |
|-------|---------|
| R1 | 1 MAJOR fix |
| R2 | 0 changes |

---

## Round 1 Changes

### MAJOR-001: Added V2 Construction Methodology Limitation

**Location:** Section 6 (Discussion), Limitations, "Only One Benchmark Pair Tested"

**Before:**
> Our analysis is limited to ImageNet → ImageNet-V2. Other distribution shifts (ObjectNet, ImageNet-Sketch, ImageNet-R) may show different patterns.

**After:**
> Our analysis is limited to ImageNet → ImageNet-V2. Other distribution shifts (ObjectNet, ImageNet-Sketch, ImageNet-R) may show different patterns. Importantly, ImageNet-V2 was constructed to replicate the original data collection methodology, making it a "near" shift—the observed ranking stability may partially reflect this design choice rather than inherent model robustness.

**Rationale:** Addresses skeptical reviewer concern that V2's construction may preserve ranking by design.

---

## Round 2 Changes

None. All numerical claims verified; no new issues identified.

---

## Not Changed (Human Review)

The following MINOR issues were NOT auto-fixed and are documented in `065_human_review_notes.md`:

1. **MINOR-001:** "96% confidence" wording in Conclusion
2. **MINOR-002:** Section 3/4 redundancy

These require author judgment for resolution.
