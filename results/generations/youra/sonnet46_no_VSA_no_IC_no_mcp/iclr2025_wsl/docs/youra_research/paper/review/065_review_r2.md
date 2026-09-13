# Adversarial Review — Round 2
**Paper:** Symmetry Orbits Are Geometrically Large in MLP Weight Spaces: Implications for Weight Space Encoding
**Round:** R2 — Numerical Verification and Credibility
**Personas:** Accuracy Checker + Skeptical Expert
**Date:** 2026-08-27
**Input:** 06_paper_r1.md (R1 revised)

---

## Ground Truth Verification Table

| Claim | Paper Value | Ground Truth | Status |
|-------|-------------|--------------|--------|
| Scaling mean cosine distance | 0.3232, CI=[0.3226,0.3238] | 0.3232 | ✓ |
| Sign-flip mean cosine distance | 1.075, CI=[1.0705,1.0789] | 1.075 | ✓ |
| Both fraction_above_threshold | 1.000 | 1.000 | ✓ |
| NFT scaling within-orbit sim | 0.971 | 0.9710 | ✓ |
| NFT scaling cross-orbit sim | 0.995 | 0.9949 | ✓ |
| NFT scaling gap reported value | +0.0238 | +0.0238 (ground truth reported) | ❌ Sign contradiction — see FATAL below |
| NFT scaling CI | [0.0232,0.0245] | [0.0232,0.0245] | ✓ |
| NFT sign-flip gap | -0.0007 | -0.0007 | ✓ |
| 34× ratio | 0.0238/0.0007=34 | 34 | ✓ |
| "24× narrower" CI claim | stated | 0.0238/0.0013=18.3 | ❌ Should be ~18×, not 24× |
| EVR raw k=20 | 0.055 | 0.055 | ✓ |
| EVR canonical k=20 | 0.086 | 0.086 | ✓ |
| 56% relative EVR improvement | 56% | (0.086-0.055)/0.055=0.564 | ✓ |
| Δρ D-A test_acc | +0.058 | 0.136-0.078=0.058 | ✓ |
| Δρ D-A gen_gap | +0.053 | 0.105-0.052=0.053 | ✓ |
| Δρ D-A lr_recovery | +0.077 | 0.121-0.044=0.077 | ✓ |
| fraction_unique | 0.144 (72/500) | 0.144 | ✓ |
| fraction_degenerate | 0.856 (428/500) | 0.856 | ✓ |
| 72+428=500 | 500/500=1.000 | verified | ✓ |
| mean_tied_neurons | 2.20 | 2.20 | ✓ |
| binomial_prediction | 83% | calculated: 83.8% ≈ 83% | ✓ |
| idempotency | 1.000 | 1.000 | ✓ |
| NFT ~3.4M params | 3.4M | ~3.35M from architecture | ✓ |

---

## Mathematical Validity Analysis

### Analysis A: NFT Gap Formula — Sign Impossibility

```
Stated formula:  gap = within_orbit_similarity − cross_orbit_similarity
Reported values: within = 0.9710, cross = 0.9949
Arithmetic:      0.9710 − 0.9949 = −0.0239
Paper reports:   gap = +0.0238  (POSITIVE)
```

The reported value (+0.0238) is arithmetically IMPOSSIBLE under the stated formula.

The computation actually performed must be:
```
gap = cross − within = 0.9949 − 0.9710 = +0.0239 ≈ +0.0238 ✓
```

The formula label is inverted relative to the computation. The numbers, interpretation, and conclusion (NFT is non-invariant to scaling) are all correct. Only the formula text is wrong.

**Severity: FATAL** — any reviewer who checks the arithmetic will find this immediately.

### Analysis B: "24× Narrower" CI Claim

```
CI:       [0.0232, 0.0245]
CI width: 0.0245 − 0.0232 = 0.0013
Gap:      0.0238
Ratio:    0.0238 / 0.0013 = 18.3×
```

The paper claims "24× narrower than the gap itself." Actual ratio is **18.3×**, not 24×. The 24× figure would require CI width = 0.0238/24 = 0.00099 ≈ 0.001. The actual width is 0.0013.

**Severity: MAJOR** — a reviewer can verify this in one calculation.

### Analysis C: Binomial Calculation Verification

```
P(tie per neuron) ≈ sqrt(2/(π·784)) = sqrt(0.000812) = 0.0285 ≈ 2.8%  ✓
P(≥1 tie in 64 neurons) = 1 − 0.972^64 = 1 − e^(−1.817) = 1 − 0.162 = 0.838 ≈ 83%  ✓
```

Paper's 83% figure is accurate.

### Analysis D: Table 5 Δρ Internal Consistency

```
D−A (test_acc):   0.136 − 0.078 = 0.058 ✓
D−A (gen_gap):    0.105 − 0.052 = 0.053 ✓
D−A (lr_recov):   0.121 − 0.044 = 0.077 ✓
E−D margins:      0.016, 0.013, 0.027 (all within noise at CI width ≈0.6) ✓
```

All Δρ values correct.

### Analysis E: EVR Relative Improvement

```
(0.086 − 0.055) / 0.055 = 0.031 / 0.055 = 0.564 ≈ 56%  ✓
```

### Analysis F: NFT Parameter Count

Architecture: d_model=256, 4 layers, 8 heads, FFN 4×
- Per layer: attention (4×256²=262K) + FFN (2×256×1024=524K) + norms = ~787K
- 4 layers: ~3.15M
- Embedding/head: ~200K
- Total: ~3.35M ≈ 3.4M  ✓

### Analysis G: Baseline Fairness

All conditions (A–E) use identical split (400/50/50), identical NFT architecture, identical training protocol, identical evaluation. **Fair comparison.**

Layer statistics (ρ≈0.9) reported as context from literature, not as a controlled head-to-head. Paper explicitly acknowledges this. **Fair framing.**

---

## FATAL Issues

```
[FATAL-ACCURACY-R2-001] NFT Gap Formula Inverted — Arithmetic Impossibility
Location: Section 3.3 (formula definition), Table 2, prose throughout Results §5.2
Finding: Paper defines "gap = within_orbit_similarity − cross_orbit_similarity" and 
reports gap = +0.0238. But within=0.9710 and cross=0.9949, so 0.9710−0.9949=−0.0239,
which is NEGATIVE, not +0.0238. The formula as written produces the wrong sign.
The actual computation must be gap = cross − within = 0.9949 − 0.9710 = +0.0239.
Evidence: Table 2: within=0.9710, cross=0.9949, gap=+0.0238. Calculation: 0.9710−0.9949=−0.0239≠+0.0238.
Required Fix: Change formula to "gap = cross_orbit_similarity − within_orbit_similarity".
Update interpretation: "A positive gap indicates cross-orbit similarity exceeds 
within-orbit similarity — the encoder does NOT treat symmetry-related models as 
more similar than property-matched unrelated models, indicating non-invariance."
Numbers and conclusions are correct; only the formula text needs inversion.
```

---

## MAJOR Issues

```
[MAJOR-ACCURACY-R2-002] "24× Narrower" CI Claim Arithmetically Incorrect
Location: Section 5.2 prose ("24× narrower than the gap itself")
Finding: CI=[0.0232,0.0245] has width 0.0013. Gap=0.0238. 
Actual ratio: 0.0238/0.0013 = 18.3×, not 24×.
The 24× figure requires CI width ≈0.001, but actual width is 0.0013.
Evidence: 0.0245−0.0232=0.0013; 0.0238/0.0013=18.3≠24
Required Fix: Replace "24× narrower than the gap itself" with "~18× narrower" 
(or state "CI width is ~5.5% of the gap magnitude" — more defensible).
```

---

## Items Confirmed Correct — No Changes Needed

- All orbit diameter values (0.3232, 1.075, both CIs)
- Both fraction_above_threshold = 1.000
- All three Δρ D−A values (0.058, 0.053, 0.077)
- 34× ratio (sign-flip/scaling NFT gaps)
- 56% EVR relative improvement
- Binomial 83% prediction
- NFT ~3.4M parameter count
- Sign-flip degeneracy statistics (72/500, 428/500, mean 2.20)
- Idempotency = 1.000
- R1 fixes confirmed preserved: CI=[0.023,0.025] in abstract, N=2,500 clarified, sign-flip approximate symmetry stated
- E>D cautionary framing appropriate given CI width ≈0.6
- Single-zoo limitation (Limitation 4) present

---

## Summary for Revision Agent — Prioritized Fixes

### FATAL (fix first):
1. **FATAL-ACCURACY-R2-001**: Invert the gap formula definition everywhere: `gap = cross − within` (not `within − cross`). Update interpretation text accordingly. Numbers unchanged.

### MAJOR (fix in same revision):
2. **MAJOR-ACCURACY-R2-002**: Replace "24× narrower" with "~18× narrower" in Section 5.2.

### No other issues found.

---

```yaml
agent: adversary
round: R2
status: COMPLETED
serena_searches_performed: 0
numerical_discrepancies_found: 2
mathematical_impossibilities: 1
baseline_fairness_issues: 0
summary:
  fatal_count: 1
  major_count: 1
  minor_count_for_human_review: 0
```
