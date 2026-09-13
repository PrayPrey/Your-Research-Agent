# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review. These are NOT auto-fixed — they require human judgment.

**Date:** 2026-08-31  
**Rounds Completed:** R1, R2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 1 |
| Grammar | 1 |
| Style/Clarity | 4 |
| Formatting | 0 |
| **Total** | **8** |

---

## Round 1 Issues

### Style / Clarity

1. **§3.5 Table caption missing.** The Training Configuration table has no caption. Suggest adding: "Table 3: Training configuration for h-e1 and h-m1 experiments." *(Subjective — standard for ML papers)*

2. **§4.4 GPU indexing ambiguous.** "binary: GPU 3; ratio: GPU 4" — not clear whether these are absolute GPU indices or CUDA device indices. Clarify to: "CUDA device 3 (binary condition) and CUDA device 4 (ratio condition)."

3. **§3.4 gate criterion unlabeled.** "Ratio HumanEval pass@1 − binary ≥ 0.03 with 95% bootstrap CI excluding 0" should be explicitly labeled as the h-m1 gate, not h-e1. Add: "**h-m1 gate criterion:**" prefix to the sentence.

4. **§2 Related Work missing APPS filter.** The Related Work section mentions "APPS dataset" without specifying that the h-e1 filter (≥5 test cases, n=1,789) differs from the h-m1 filter (≥1 test case). Consider adding a brief note in §2 or a forward reference to §3.5 for clarity.

### Grammar

5. **§5.4 "mean = +0.000730"** — the "+" prefix before a positive mean value is non-standard in formal writing. Typically reported as "0.000730" without the sign, unless contrasting with a negative value. *(Minor — some venues prefer explicit sign for contrast)*

### Typo

6. **§5.4 last sentence of gate verdict:** "...making both rewards mathematically equivalent (both = 0 for all completions in all groups). GRPO produces zero gradient..." — consider combining into one sentence for flow: "...making both rewards mathematically equivalent (both = 0 for all completions), and GRPO produces zero gradient contribution from every group for both conditions."

---

## Round 2 Issues

### Style / Clarity

7. **§5.1 Table 1 bold markdown:** "Group mean" and "Advantage variance" rows use markdown bold (`**`). Check that conference submission system (e.g., ICML LaTeX template) renders this correctly — if converting from markdown to LaTeX, bold in table cells may require manual conversion.

8. **§3.2 dead zone condition nuance:** The paper describes the dead zone as "all k_i ∈ {0, n}" in §3.2 but in practice refers to the all-fail case (k_i=0 for all i) throughout the intro and abstract. A parenthetical clarification would help: after "all k_i ∈ {0, n}", add "(which in early training is dominated by the all-zero case, k_i=0 for all i)."

---

## Recommended Priority

1. **Fix First:** Item 3 (h-m1 gate label) — prevents reader confusion about which hypothesis the criterion belongs to
2. **Fix Second:** Item 2 (GPU index clarity) — affects reproducibility
3. **Consider:** Items 1 and 4 (captions and cross-references) — improve navigability
4. **Optional:** Items 5 and 6 (grammar/typo) — purely stylistic

---

*Note: These issues do not block paper acceptance but improve overall quality.*
