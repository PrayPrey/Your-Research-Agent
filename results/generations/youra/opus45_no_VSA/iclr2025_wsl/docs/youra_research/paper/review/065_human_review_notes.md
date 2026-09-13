# Human Review Notes

Collected from adversarial review rounds. These MINOR issues are NOT auto-fixed.

---

## From Round 1

### MINOR-001: Vague Accuracy Range
- **Location**: Section 4, Table
- **Issue**: "~72% - ~88%" is vague
- **Suggestion**: Use exact values or cite timm metadata

### MINOR-002: SVD Implementation Terminology
- **Location**: Section 3
- **Issue**: "torch.linalg.svd with QR-based random projection" mixes terminology
- **Suggestion**: Clarify that randomized SVD uses random projection matrix; QR is for orthonormalization step

### MINOR-003: Related Work Density
- **Location**: Section 2
- **Issue**: Could be 10-15% shorter without losing positioning
- **Suggestion**: Tighten paragraph structure, reduce redundant positioning

---

## Summary

| Round | Type | Count |
|-------|------|-------|
| R1 | typo | 0 |
| R1 | grammar | 0 |
| R1 | style | 1 |
| R1 | clarity | 2 |
| R1 | formatting | 0 |
| **Total** | | **3** |
