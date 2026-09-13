# Adversarial Review Round 2

## Numerical Verification

| Claim (Paper) | Ground Truth | Status |
|---------------|--------------|--------|
| CAB drift slope: 0.00090506 | 9.051e-04 | MATCH |
| MOHAWK drift slope: 0.00452495 | 4.525e-03 | MATCH |
| Slope ratio: 5.0x | 5.0x | MATCH |
| CAB drift ratio: 1.34 | 1.34 | MATCH |
| MOHAWK drift ratio: 2.02 (13.79/6.84) | 13.79/6.84 = 2.015... | MATCH |
| CAB drift 512: 4.08 | 4.08 | MATCH |
| CAB drift 2048: 5.47 | 5.47 | MATCH |
| MOHAWK drift 512: 6.84 | 6.84 | MATCH |
| MOHAWK drift 2048: 13.79 | 13.79 | MATCH |
| Cosine MOHAWK 512: 0.994 | 0.994 | MATCH |
| Cosine MOHAWK 2048: 0.978 | 0.978 | MATCH |
| Cosine CAB 512: 0.998 | 0.998 | MATCH |
| Cosine CAB 2048: 0.996 | 0.996 | MATCH |
| H-M3 p-value: 0.881 | 0.881 | MATCH |

## Mathematical Validity Check

- Slope ratio calculation: 0.00452495 / 0.00090506 = 5.0 (correct)
- Drift ratio calculation for MOHAWK: 13.79/6.84 = 2.016 (paper says 2.02, acceptable rounding)
- Drift ratio calculation for CAB: 5.47/4.08 = 1.34 (correct)

No calculation errors found.

## Baseline Fairness Check

Paper states (Section 3.2): "Same training data: C4 dataset (streaming), Phi tokenizer" and "The framework supports switching between MOHAWK Stage 1-3 losses and CAB bridge alignment via configuration."

Ground truth confirms: Both use C4 validation (500 documents), same teacher (Phi-1.5), same sequence lengths (512-2048), same layers analyzed (8, 12, 16).

**However**: Section 6.2 discloses "Simulated student approximation" - this is consistent with ground truth noting "simulated student models were used." The comparison is fair within methodology, but methodology is a proxy (not real trained checkpoints).

Status: FAIR (limitation disclosed)

## Signal-Performance Gap Check

Paper Section 6.2 states:
- "PoC training only... downstream task performance (F1 on LongBench) cannot be verified"
- "The 5× slope ratio is directionally robust but exact magnitudes may vary with real checkpoints"

H-M3 failure (p=0.881) is disclosed in Section 5.4 with explicit "FAIL" label.

Paper correctly distinguishes drift stability (measured) from task performance (not measured).

Status: CLEAR

## Issues Found

### FATAL
None.

### MAJOR
None.

### MINOR

1. **Line 219**: Paper says "middle layers (12, 16) exhibit greatest divergence" but ground truth shows identical values across layers 8, 12, 16. This statement cannot be verified from provided data - appears to be speculation not supported by per-layer results.

2. **Abstract/Conclusion phrasing**: "token-level distillation produces representations with 5× lower drift" - strictly speaking, this was measured on simulated students, not actual distilled models. The limitation is buried in Section 6.2. Consider adding "in PoC simulations" qualifier to abstract.

## Summary

| Severity | Count |
|----------|-------|
| FATAL    | 0     |
| MAJOR    | 0     |
| MINOR    | 2     |

R1 revisions successfully addressed all prior issues. Numerical claims now match ground truth exactly. Limitations are properly disclosed. The paper is ready for final polish addressing the two minor issues (per-layer divergence claim unsupported by data; consider clarifying simulation context in abstract).
