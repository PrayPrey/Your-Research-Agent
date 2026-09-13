# Human Review Notes - Phase 6.5 Adversarial Review
# Minor issues collected for human review (NOT auto-fixed)

## Round 1 Minor Issues

### Consistency
1. **Table 5.2 rounding**: Shows "d=1.33" while text uses "1.325" — minor rounding inconsistency
2. **Abstract rounding**: Uses "0.82" while body reports "0.8245" — acceptable but inconsistent
3. **Terminology**: Section 5.1 says "6× difference" for JS-divergence ratio, but "7× gap" used elsewhere for transfer degradation — potentially confusing different metrics

### Style
- None flagged

### Typos
- None flagged

### Grammar
- None flagged

### Formatting
- Section 5.6 summary table may feel redundant after 5.1-5.5 narrative

---

## Round 2 Minor Issues

### Methodology
1. **Within-cluster JS approximation**: Section 5.1 states "0.08" but source shows 0.056 (C1) and 0.108 (C2), mean ~0.082
2. **Temperature inconsistency**: Paper states T=0.7 throughout, but H-M3 used T=1.0

---

## Summary
- Total MINOR issues: 6
- Typo: 0
- Grammar: 0
- Style: 0
- Clarity: 1
- Formatting: 1
- Consistency: 3
- Methodology: 2
