# Human Review Notes
# Phase 6.5 Adversarial Review — Minor Issues for Human Review
# Date: 2026-08-26
# Rounds Completed: 2

> **Purpose:** Minor issues collected during adversarial review for human editorial attention.
> These issues do NOT block paper acceptance. They are collected here rather than auto-fixed
> to preserve authorial voice and avoid unintended changes.

---

## Summary by Category

| Category | Count |
|----------|-------|
| Grammar / Style | 3 |
| Notation consistency | 2 |
| Attribution clarity | 2 |
| Formatting | 1 |
| **Total** | **8** |

---

## Round 1 Issues

### Notation Consistency

1. **§3.3 — Hyperparameter notation**: Learning rates written as `lr=2e-5` and `lr=1e-6` (scientific inline). R2 version already corrected to `lr=2×10⁻⁵` and `lr=1×10⁻⁶`. If authors prefer inline `2e-5` form, apply consistently throughout §3.3 and §4.3. Both are acceptable; pick one.

2. **Table 1 Note — Tilde usage**: Original paper had "~0.52–0.58" (tilde before range). Fixed in R1. If any other occurrences of `~` before ranges appear in final, remove tilde (redundant with range notation).

### Style / Brevity

3. **§6.3 "Potential concerns"**: The sentence "Improved code generation capability could accelerate automated code production without sufficient quality control" is a generic broader-impact boilerplate statement present in many code LLM papers. Consider replacing with a concern specific to this work (e.g., the risk that practitioners over-generalize from smoke-scale proxy results to production decisions). *Subjective — keep if ICML broader-impact convention favors it.*

4. **§7 Future Directions**: Lists 4 items. Consider trimming to 2 most impactful (mechanism verification + full-scale evaluation) for tighter conclusion. The medium-term items (VeRPO formulation, model scale) could be moved to §6.1 or omitted.

### Attribution Clarity

5. **§2.1 — CodeRL +4.3% claim**: The sentence "demonstrating consistent improvements over SFT on APPS and HumanEval (+4.3%)" — add "(pass@1)" after "+4.3%" to clarify metric. Reviewers may ask which metric.

6. **§2.2 — 97% attribution**: "arXiv:2605.02944 finds that 97% of APPS problems..." — attribution is now in place (fixed in R1). Consider adding "(at GRPO convergence)" after "97% of APPS problems" to match the paper's actual condition more precisely.

---

## Round 2 Issues

### Formatting

7. **Table 2 column width**: Table 2 now has 5 columns (Benchmark, Difficulty, SFT pass@1, RLEF pass@1, Δ). In a PDF rendering at ICML column width, 5 columns may be tight. Consider abbreviating "Difficulty" to "Diff." or collapsing SFT/RLEF columns with a footnote if space is an issue. Not a correctness issue.

### Grammar

8. **§5.4 "Higher loss = less certain next-token prediction at training time"**: The dash formulation is colloquial. Consider: "Higher loss reflects less certain next-token prediction at training time" for more formal register.

---

## Recommended Priority

1. **Fix First (High Visibility)**: Attribution qualifiers (items 5, 6) — reviewers check these.
2. **Fix Second**: Notation consistency (items 1, 2) — copy-editor will catch these.
3. **Consider**: Style improvements (items 3, 4, 8) — subjective, author preference.
4. **Optional**: Table formatting (item 7) — depends on final PDF layout.

---

*None of these issues block paper submission. All FATAL and MAJOR issues have been resolved in the adversarial review process.*
