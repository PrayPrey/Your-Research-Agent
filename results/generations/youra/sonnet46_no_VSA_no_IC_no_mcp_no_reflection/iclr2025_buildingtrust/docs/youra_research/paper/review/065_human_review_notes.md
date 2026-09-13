# Human Review Notes
# Purpose: Minor issues collected during adversarial review — NOT auto-fixed.
# Date: 2026-08-31T06:30:00+00:00
# Rounds Completed: R1, R2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 1 |
| Formatting | 1 |

---

## Round 1 Issues

### Style

1. **Section 1, paragraph 4**: "Our key insight is that alignment strategy can be treated as a binary classification problem over public benchmark score vectors." The classification framing is the method, not the insight. The actual insight is the truthfulness finding.

   *Suggested revision:* "Our approach treats alignment strategy as a binary classification problem over public benchmark score vectors — a framing that lets us not only test whether fingerprinting is possible, but identify which dimension carries the signal."

### Formatting

1. **Figure Captions — Figure 1**: Caption does not specify which color represents DPO vs SFT. Figure 2 caption correctly says "DPO (blue) and SFT (orange)" but Figure 1 does not.

   *Suggested fix:* Add "(DPO: blue, SFT: orange)" to Figure 1 caption.

---

## Round 2 Issues

### Clarity

1. **Section 5.2, Table 6 caption reference**: The paper refers to "Figure 6 (fig3_fisher_criterion.png)" in Section 5.2, but Figure 6 is the Fisher criterion figure while Fig 3 in the h-e1 figure numbering is the permutation test. The figure filename `fig3_fisher_criterion.png` is inconsistent with the paper's Figure numbering (Figure 6). Human reviewer should verify figure number vs filename consistency across all 7 figures.

### Style

2. **Section 6, Finding 1**: "The fingerprint is sufficiently strong that 10 of 12 models are correctly identified despite subtle differences in absolute scores (0.5–4.6pp range)." The range "0.5–4.6pp" conflates BBQ per-pair delta (0.5pp) with TruthfulQA per-pair delta (4.6pp) — these are per different benchmarks, not a range of the same metric. May confuse readers.

   *Suggested revision:* "despite score differences spanning 0.5pp (BBQ) to 4.6pp (TruthfulQA) across benchmarks."

---

## Recommended Priority

1. **Fix First**: Figure 1 caption color specification (high visibility in venue proceedings)
2. **Fix Second**: Figure numbering consistency check (fig3 vs Figure 6)
3. **Consider**: Introduction "key insight" framing reword (subjective)
4. **Consider**: Section 6 benchmark range clarification

---

*Note: These issues do not block paper acceptance but improve overall quality.*
