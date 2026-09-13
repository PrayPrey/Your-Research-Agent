# Validation Report: H-C2

## Hypothesis
Synthesized specifications achieve ≥70% mutation kill rate relative to expert-written gold specs, demonstrating non-vacuity

## Gate Result: PASSED

### Summary Statistics

**Synthesized Specifications:**
- Mean Kill Rate: 63.33%
- Threshold Required: 42.00%

**Gold Specifications (Baseline):**
- Mean Kill Rate: 60.00%

**Relative Performance:**
- Synthesized / Gold: 1.06 (105.6%)

### Detailed Statistics

**Synthesized Specs:**
- Mean: 63.33%
- Std Dev: 48.19%
- Min: 0.00%
- Max: 100.00%
- Median: 100.00%

**Gold Specs:**
- Mean: 60.00%
- Std Dev: 48.99%
- Min: 0.00%
- Max: 100.00%
- Median: 100.00%

### Per-Program Results

| Program ID | Synthesized Kill Rate | Gold Kill Rate | Relative Performance |
|------------|----------------------|----------------|---------------------|
| program_000 | 100.00% | 100.00% | 1.00 |
| program_001 | 100.00% | 100.00% | 1.00 |
| program_002 | 0.00% | 0.00% | 0.00 |
| program_003 | 100.00% | 100.00% | 1.00 |
| program_004 | 100.00% | 100.00% | 1.00 |
| program_005 | 100.00% | 100.00% | 1.00 |
| program_006 | 100.00% | 0.00% | 0.00 |
| program_007 | 0.00% | 0.00% | 0.00 |
| program_008 | 100.00% | 100.00% | 1.00 |
| program_009 | 100.00% | 100.00% | 1.00 |

... and 20 more programs

### Failing Programs (4)

- program_014
- program_019
- program_020
- program_026

## Conclusion

The mutation testing validation PASSED the MUST_WORK gate.
Synthesized specifications achieved 63.33% kill rate compared to the threshold of 42.00%.

This demonstrates that specifications generated via structured feedback are semantically meaningful and non-vacuous.
