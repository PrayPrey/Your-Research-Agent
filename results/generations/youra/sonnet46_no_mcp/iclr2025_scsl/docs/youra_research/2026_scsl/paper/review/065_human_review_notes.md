# Human Review Notes — Phase 6.5 Adversarial Review

> Minor issues collected for human review. NOT auto-fixed.
> Generated: 2026-05-04
> Round: 1

---

## Summary

| Category | Count |
|----------|-------|
| Precision / Rounding | 1 |
| Formatting / Layout | 1 |
| Terminology / Acronym | 1 |
| Style / Phrasing | 2 |
| Methodology Clarification | 3 |

**Total minor issues (R1): 8 | Total minor issues (R2): 3 | Grand total: 11**

---

## Round 1 Issues

### Precision / Rounding

**MN-AC-1** — §5.3, Abstract: p-value rounding
- Current text reports "p = 0.022" (abstract and results table)
- Ground truth value is p = 0.0219
- Rounding to 0.022 is acceptable but inconsistent with the precision used for other reported p-values (e.g., FFT p=0.033, separability p=0.017)
- Recommendation: Consider reporting "p = 0.0219" for consistency, or establish a uniform rounding policy across all p-values.
- Source: MN-AC-1 (Accuracy Checker)

---

### Formatting / Layout

**MN-AC-2** — §5.1, §5.3, §5.4, §5.5: Figure number consistency
- The paper references Figures 1–12 throughout Section 5
- These figure numbers cannot be verified without the actual figures/layout file
- Recommendation: Before final submission, verify all figure numbers match the actual figure ordering in the compiled document (especially Figures 6, 7, 8, 9, 11, 12 referenced in §5.1–5.5).
- Source: MN-AC-2 (Accuracy Checker)

---

### Terminology / Acronym

**MN-AC-3** — Abstract: GDR acronym definition
- "GDR" is used in the abstract ("GDR = 6.977") but the acronym is first formally defined in §3.2
- A reader who reads only the abstract will encounter an undefined acronym
- Recommendation: Add a brief parenthetical in the abstract, e.g., "(Gradient Dominance Ratio, GDR = 6.977)" or expand on first use.
- Source: MN-AC-3 (Accuracy Checker)

---

### Style / Phrasing

**MN-BR-1** — Introduction §1, opening sentence: Colloquial phrasing
- Current: "it learns the wrong answer first"
- This is engaging colloquially but may read as imprecise to some reviewers who expect formal language
- Alternative: "it encodes spurious correlations preferentially in early training" or "it acquires shortcut features before core features"
- Recommendation: Author's call — the colloquial opening is a deliberate rhetorical choice; flag for human judgment.
- Source: MN-BR-1 (Bored Reviewer)

**MN-BR-2** — §7 Conclusion: DFR finding emphasis
- The conclusion's final paragraph briefly mentions the DFR epoch-1 finding but does not emphasize it as the most surprising result of the paper
- The DFR finding (WGA = 0.806 at epoch 1, suggesting ImageNet pretraining may matter more than training dynamics) is arguably more novel and surprising than the t* stability result
- Recommendation: Consider restructuring the conclusion to close on the DFR finding rather than the future work list, to leave a stronger impression.
- Source: MN-BR-2 (Bored Reviewer)

---

### Methodology Clarification

**MN-SE-1** — §3.2, §4.7: layer4 gradient norm ambiguity
- The paper states gradient instrumentation hooks are registered on "ResNet-50 layer4 parameters"
- It is ambiguous whether GDR is computed from gradients w.r.t. layer4 *feature maps* (activations) or layer4 *parameters* (weights)
- These give different norm values and different interpretations
- Recommendation: Add one clarifying sentence: "Gradient norms are computed with respect to layer4 weight parameters (not feature maps), averaged over the batch."
- Source: MN-SE-1 (Skeptical Expert)

**MN-SE-2** — §3.3, §6.2 L5: Quadrant patch split sensitivity
- The paper uses top 40% of image height for spurious patches and center 60% for core patches
- No validation is reported showing these splits capture the intended content (background vs. bird)
- Recommendation: Add a brief note on whether this split was spot-checked against any ground-truth annotation (e.g., a random sample of 20 images visually inspected), or report patch purity qualitatively. Even an informal validation statement would strengthen credibility.
- Source: MN-SE-2 (Skeptical Expert)

**MN-SE-3** — §4.4, §6.2 L1: 30-epoch scope vs. literature norms
- Waterbirds training in published DFR and GroupDRO work typically uses 50–300 epochs
- The paper addresses this in Limitation L1, but §4.4 does not explain why 30 epochs was chosen
- Recommendation: Add 1–2 sentences in §4.4 motivating the 30-epoch choice explicitly as a proof-of-concept scope decision (not a claim that full-scale dynamics are captured), with a forward reference to L1.
- Source: MN-SE-3 (Skeptical Expert)

---

## Round 2 Issues

### Precision / Consistency

**MN-R2-1** — §5.3: Window epoch range vs. fraction reconciliation
- The paper states "δ(t) > 0 for a contiguous window covering epochs 2–8" but 13.3% of 30 epochs = 4 epochs, not 6 (2–8 spans 6 epochs at face value)
- The 13.3% figure = 2 checkpoints × 2 epochs/checkpoint / 30 epochs = 4/30 = 0.133. This is internally consistent only if the contiguous window covers 2 checkpoints (epochs 2 and 4), not all of epochs 2–8.
- Recommendation: Clarify in §5.3 that "window_epochs: 2-8" refers to the observation range while "13.3%" refers to the fraction of checkpoint epochs with δ(t)>0 within that range, or correct the epoch range description to match the 4-epoch (2 checkpoint) calculation.
- Source: MN-R2-1 (Accuracy Checker, Round 2)

**MN-R2-2** — §5.2: Core gradient norm precision
- Paper uses "~0.12" as the core gradient norm; ground truth value is 0.118
- Recommendation: Use "~0.118" or "~0.12" consistently throughout; currently mixed precision in different sections.
- Source: MN-R2-2 (Accuracy Checker, Round 2)

**MN-R2-3** — Abstract and §5.3: p-value inconsistency (pre-existing, carried forward)
- Abstract reports "p = 0.022"; §5.3 table reports "0.0219"; ground truth is 0.0219
- Recommendation: Unify to "p = 0.0219" throughout for precision, or explicitly note "rounded to p = 0.022 in abstract for readability."
- Source: MN-R2-3 (Accuracy Checker, Round 2; pre-existing MN-AC-1 from Round 1)
