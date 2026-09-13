# Human Review Notes — Phase 6.5 Adversarial Review

**Date**: 2026-08-05
**Rounds**: R1 (R2 to be appended)

---

## Summary

| Category | Count |
|----------|-------|
| Typo | 1 |
| Grammar | 0 |
| Style | 1 |
| Clarity | 2 |
| Formatting | 1 |
| Verification required | 1 |

**Total**: 6

---

## Round 1 Issues

### Typos

- **MINOR-001** — Section 4.3, Baselines: Stable rank formula has double-caret typo: `$\|W_0\|_2^^$` should be `$\|W_0\|_2^2$`. *Note: Fixed in R1 paper (06_paper_r1.md) as it causes garbled LaTeX output.*

### Grammar

None identified.

### Style

- **MINOR-003** — Abstract: "remarkably accurate" is an editorial adverb. The r=0.984 figure speaks for itself; the adverb weakens rather than strengthens the claim. Recommend deleting "with remarkable accuracy" from the sentence "...predicts per-layer optimal LoRA rank with remarkable accuracy."

### Clarity

- **MINOR-004** — Section 5.3, final paragraph: The "Implication: If ViT's larger erank range translates..." paragraph presents speculation as an implication. No oracle data for ViT is available in the current paper. Recommend reframing as "Research hypothesis" or "Motivating observation" rather than "Implication" to avoid reviewer pushback on presenting predictions as conclusions.

- **MINOR-005** — Section 4.3 / Results: Stable rank is listed in Section 4.3 as a baseline ("SRLoRA baseline from prior work") but no stable rank vs. erank comparison appears anywhere in the Results or Discussion. Either (a) add a one-line SR vs. erank Pearson correlation result to Table 1 or Section 5.2, or (b) reframe stable rank in Section 4.3 as "structural baseline for future comparison" to avoid implying results that are not reported.

### Formatting

- **MINOR-006** — Table 2: BERT erank min (543.2) excludes pooler.dense (erank=405.6) but the original paper had no footnote disclosing this exclusion. *Note: Footnote added in R1 paper (06_paper_r1.md).*

### Verification Required

- **MINOR-002** — References: Four 2026 preprint citations have unverified status in the paper pipeline (verification rate 67%). Requires manual verification before submission:
  - LAARA [Tripathi et al., 2026] — arXiv:2607.19391
  - IFCLoRA [Zhang et al., 2026] — arXiv:2607.22251
  - IGU-LoRA [Jiang et al., 2026] — arXiv:2603.13792
  - La-LoRA [Chen et al., 2025] — no arXiv ID listed in paper
  
  Action: Confirm arXiv IDs exist and author lists match. La-LoRA citation is missing an arXiv ID entirely.

---

## Round 2 Issues

**Date**: 2026-08-05

### Numerical Accuracy

- **R2-MINOR-001** — Section 5.1: "erank ~704–720" for the two FFN oracle intermediate layers — upper bound of 720 not supported by the JSON. Actual values are 709.5 and 704.4. *Note: Fixed in R2 paper (06_paper_r2.md) as part of R2-MAJOR-001 fix.*

- **R2-MINOR-002** — Table 2 footnote: BERT erank min reported as 543.2, but the actual minimum of all LoRA-targetable layers excluding pooler.dense is `encoder.layer.2.attention.self.key.weight` = 518.3. The footnote only disclaims exclusion of pooler.dense, leaving the impression that 543.2 is the true LoRA-layer minimum. Action: Clarify which layers are included in the range computation — if 543.2 is the min across query weights only (or based on a specific subset), the footnote should state that explicitly; otherwise correct min to 518.3.

### Framing / Language

- **R2-MINOR-003** — Abstract, Introduction, Conclusion: "zero-cost" framing does not acknowledge that SVD computation of W₀ has real compute cost (O(d²k) per matrix), which becomes non-trivial for large models. The usage is accurate within the paper's scope (encoder-only models, no training cost) but one clarifying phrase such as "zero-cost relative to fine-tuning" would preempt reviewer objections.

- **R2-MINOR-004** — Conclusion Section 7 ("remarkably well") and Discussion 6.2 ("suggests strong prospects"): mild overclaim language. "Remarkably well" in the Conclusion lacks the bimodal caveat present in the Abstract. "Suggests strong prospects for cross-family confirmation" in Discussion 6.2 implies a prediction from erank variation alone that is not warranted. *Note: "remarkably well" changed to precise language in R2 paper. "Suggests strong prospects" changed to more hedged language in R2 paper.*
