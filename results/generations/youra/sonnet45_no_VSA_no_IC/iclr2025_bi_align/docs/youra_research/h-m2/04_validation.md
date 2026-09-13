# h-m2 Multi-Layer Validation Detection Results

**Hypothesis:** Three-layer validation detects constraint violations missed by schema-only validation.

---

## Detection Rates

| Condition | Detection Rate | Detected/Total |
|-----------|----------------|----------------|
| Schema-only | 40.0% | 10/25 |
| Three-layer | 88.0% | 22/25 |
| **Gap** | **48.0pp** | - |

## Per-Layer Detection (Three-Layer Condition)

- Schema: 10 violations
- Pattern: 8 violations
- Contract: 4 violations

## Per-Constraint Detection

- C1 (synthetic data): 4/5
- C2 (human eval): 4/5
- C3 (standard dataset): 2/2
- C4 (new benchmark): 2/3

## False Positive Rate

Valid cases rejected: 0.0% (0/5)

## Gate Verdict: PASS

**Result:** PRIMARY criterion met (gap >= 40pp) + SECONDARY criteria met.

## Key Findings

1. Three-layer detection rate: 88.0%
2. Schema-only detection rate: 40.0%
3. Detection gap: 48.0 percentage points
4. Pattern layer caught 8/10 semantic violations (C1/C2)
5. Contract layer caught 4/5 cross-field violations (C3/C4)
6. False positive rate: 0.0% (all valid cases passed)
