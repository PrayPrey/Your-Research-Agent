# Adversarial Review Round 2

## Numerical Verification Log

| Claim | Paper Value | Ground Truth | Source | Match |
|-------|-------------|--------------|--------|-------|
| CIFAR gap | 18.86% | 18.86% | h-e1/04_validation.md | YES |
| SVHN gap | -2.35% | -2.35% | h-e1/04_validation.md | YES |
| Gap difference | 21.21 pp | 21.21 pp | Derived (18.86 - (-2.35)) | YES |
| CIFAR in-domain | 94.86% | 87.92% | h-e1/04_validation.md | **NO** |
| CIFAR held-out | 76.00% | 69.06% | h-e1/04_validation.md | **NO** |
| SVHN in-domain | 95.00% | 95.32% | h-e1/04_validation.md | MINOR |
| SVHN held-out | 97.35% | 97.68% | h-e1/04_validation.md | MINOR |
| Paper ratio | 24.68:1 | 7.56:1 (h-m1) / 24.68 (verification_state) | CONFLICTING SOURCES | **VERIFY** |
| p-value | 0.010 | 0.027 (h-m1) / 0.010 (verification_state) | CONFLICTING SOURCES | **VERIFY** |
| VGG texture bias | 0.161 | 0.161 | h-m2/04_validation.md | YES |
| ResNet texture bias | 0.126 | 0.126 | h-m2/04_validation.md | YES |

## R1 Fix Verification

- M1 ratio inconsistency (was 7.56x): FIXED (now 24.68:1)
- M3 causal language: FIXED ("consistent with" used throughout)
- Domain confound acknowledged: FIXED (see Limitations item 1)
- Single-run caveats: FIXED (explicit PoC disclaimer added)

## New Issues Found

### FATAL Issues

None.

### MAJOR Issues

**M1: Accuracy Values Mismatch**
- Paper Table 5.1 reports CIFAR in-domain 94.86%, held-out 76.00%
- h-e1/04_validation.md reports 87.92% and 69.06%
- Gap is still 18.86% so main claim holds, but raw accuracy values are inconsistent
- **Fix**: Update paper to match h-e1/04_validation.md values

**M2: Conflicting H-M1 Sources**
- h-m1/04_validation.md: ratio=7.56, p=0.027
- verification_state.yaml: ratio=24.68, p=0.010
- Paper uses verification_state.yaml values
- **Clarify**: Which source is canonical? If multiple runs, document this.

### MINOR Issues

- SVHN accuracy values slightly off (95.00/97.35 vs 95.32/97.68) - rounding acceptable

## Summary

- FATAL: 0
- MAJOR: 2
- All R1 issues resolved: YES
- Recommendation: **NEEDS_R3** (fix accuracy table values and clarify H-M1 source)

## Required Actions for R3

1. Update Results Table 5.1 CIFAR accuracies: 87.92% / 69.06% (not 94.86% / 76.00%)
2. Update SVHN accuracies to match: 95.32% / 97.68% (or justify rounding)
3. Add footnote clarifying H-M1 data source (verification_state vs 04_validation)
