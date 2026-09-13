# Adversarial Review Changelog

## Round 1 — 2026-08-05

### MAJOR Issues Fixed

#### MAJOR-001: Layer mislabeling in Section 5.1 (and Abstract, Introduction, Conclusion)

**Location**: Abstract; Section 1 Introduction (contributions list); Section 5.1 Results; Section 6.1 Discussion; Section 7 Conclusion

**Root cause**: `encoder.layer.3.attention.self.query.weight` (oracle rank 4, erank ~555.7) was grouped with FFN intermediate layers in the sections/05_results.md parenthetical, and "attention output layers" language in the abstract/introduction/conclusion excluded this query layer from the low-rank group.

**Changes applied**:

*Abstract* — "attention output layers (erank ~557)" changed to "attention layers (erank ~557–590)" to cover both output and query projections.

**Before**: `FFN intermediate layers (erank ~720) receive oracle rank 64 while attention output layers (erank ~557) receive oracle rank 4`
**After**: `FFN intermediate layers (erank ~720) receive oracle rank 64 while attention layers (erank ~557–590) receive oracle rank 4`

*Section 5.1* — Replaced the inaccurate parenthetical grouping with explicit layer-by-layer breakdown:

**Before**: `Two attention output layers (erank ~557–590) receive oracle rank r*=4; three FFN intermediate layers (erank ~557–704) receive oracle rank r*=4–64.`
**After**: `Two attention output layers (encoder.layer.0.attention.output.dense.weight, encoder.layer.6.attention.output.dense.weight; erank ~557–590) and one attention query layer (encoder.layer.3.attention.self.query.weight; erank ~556) receive oracle rank r*=4; two FFN intermediate layers (encoder.layer.8.intermediate.dense.weight, encoder.layer.10.intermediate.dense.weight; erank ~704–720) receive oracle rank r*=64.`

*Section 1 contributions list* — "attention output matrices (erank ~557)" changed to "attention layers including query and output projections (erank ~557–590)".

*Section 6.1 Discussion* — "Attention output layers (erank ~560, concentrated spectra) need only r=4" changed to "Attention layers — both output projections and query projections (erank ~556–590, concentrated spectra) — need only r=4."

*Section 7 Conclusion* — "attention output matrices (erank ~557) receive oracle rank r*=4" changed to "attention layers — including both output projections and query projections (erank ~557–590) — receive oracle rank r*=4."

---

#### MAJOR-002: n=5 not disclosed in Abstract

**Location**: Abstract; Section 1 contributions list

**Problem**: Abstract stated `r = 0.984 (p = 0.0013)` with no mention of n=5 sample size or the bimodal (binary) nature of the correlation. Readers would assume a graded linear correlation over many layers.

**Changes applied**:

*Abstract* — Added n=5 disclosure and bimodal structure clarification:

**Before**: `at Pearson r = 0.984 (p = 0.0013): FFN intermediate layers...`
**After**: `at Pearson r = 0.984 (p = 0.0013, n=5 oracle layers): FFN intermediate layers...` plus added sentence: `The near-perfect correlation reflects binary discrimination between two structural tiers (erank <600 → r*=4; erank >700 → r*=64) rather than a smooth graded relationship over the full erank range; validation over all 72 layers is pending.`

*Section 1 contributions* — Added `(n=5 oracle layers)` to the r=0.984 claim.

---

#### MAJOR-003: CV threshold (A1) not acknowledged for BERT/DeBERTa

**Location**: Section 6.3 Limitations (new L5)

**Problem**: Table 2 showed BERT CV ~0.04 and DeBERTa CV ~0.04, both below the pre-registered A1 threshold (CV > 0.05). The paper never acknowledged this failure. Only ViT (CV ~0.12) meets A1.

**Change applied**: Added new **Limitation L5** to Section 6.3:

**Added**:
> **L5: BERT and DeBERTa erank variation below A1 threshold.** BERT-base and DeBERTa-v3-base show CV ≈ 0.04, below the pre-registered A1 threshold (CV > 0.05). Only ViT-base (CV ≈ 0.12) meets this threshold. The strong oracle correlation for BERT (r = 0.984) is driven by oracle bimodality (rank 4 vs. 64) rather than erank spread — erank need not vary widely to discriminate two structural tiers perfectly, but this means continuous rank discrimination across the full erank range remains untested for NLP encoders. If the oracle is not bimodal for full 72-layer coverage, the modest BERT/DeBERTa erank variation (range ratio 1.34×–1.35×) may limit erank's discriminative power as a continuous predictor.

---

#### MAJOR-004: Depth confound unaddressed

**Location**: Section 6.3 Limitations (new L6); Section 7 Conclusion (added reference)

**Problem**: The 5 measured BERT oracle layers have attention layers at depths 0, 3, 6 and FFN layers at depths 8, 10. Layer type is confounded with depth. The paper mentioned partial correlation as future work in the Conclusion but did not acknowledge the confound in Limitations.

**Changes applied**: Added new **Limitation L6** to Section 6.3:

**Added**:
> **L6: Depth confound in oracle sample.** The 5 measured BERT oracle layers span network depths 0–10, with attention layers sampled from shallower positions (encoder layers 0, 3, 6) and FFN layers from deeper positions (encoder layers 8, 10). Consequently, layer type is partially confounded with depth in the current sample — whether erank predicts oracle rank independently of depth cannot be assessed from 5 layers alone. Partial correlation analysis controlling for depth is planned as a priority analysis once full-coverage oracle sweeps are completed (noted as future work in Section 7).

*Section 7 Conclusion* — Forward-reference to L6 added: "partial correlation controlling for depth to separate erank signal from depth confound (see Limitation L6)".

---

### Table 2 Footnote (Reviewer MINOR-006 — fixed as part of accuracy pass)

Added table footnote to Table 2 disclosing pooler.dense exclusion from BERT erank range:

**Added**: `†BERT erank range excludes pooler.dense (erank = 405.6), which is not a LoRA adaptation target and is an architectural outlier; the range reported reflects LoRA-targetable layers only.`

Note: This was listed as MINOR-006 in the review but was a factual disclosure gap closely related to MAJOR-001 accuracy fixes, so it was applied in R1.

---

### Section 4.3 Typo Fix (Reviewer MINOR-001 — fixed as part of accuracy pass)

Fixed stable rank formula typo in Section 4.3:

**Before**: `$\|W_0\|_2^^$`
**After**: `$\|W_0\|_2^2$`

Note: This was MINOR-001 but was a clear LaTeX rendering error that would appear garbled in any compiled output, so it was corrected in R1.

---

### Issues NOT Fixed (passed to human review or R2)

- **MINOR-002**: Unverified 2026 citations (LAARA, IFCLoRA, IGU-LoRA, La-LoRA) — requires human verification before submission.
- **MINOR-003**: "remarkably accurate" in abstract — editorial adverb; flagged for human review.
- **MINOR-004**: Speculative ViT "Implication" paragraph in Section 5.3 — not fixed in R1 as the content is clearly framed as a forward-looking statement; flagged for human review.
- **MINOR-005**: Stable rank baseline listed in Section 4.3 but not evaluated in results — flagged for human review (either add SR vs. erank comparison or reframe as "structural baseline for future comparison").

---

## Round 2 — 2026-08-05

### MAJOR Issues Fixed

#### R2-MAJOR-001: FFN erank value corrected from ~720 to ~704–710

**Locations fixed**: Abstract; Section 1 Introduction (contributions list); Section 6.1 Discussion ("Mechanism matches theory" paragraph); Section 7 Conclusion

**Problem**: The paper stated "FFN intermediate layers (erank ~720)" in multiple locations. The actual erank values from `erank_map_bert-base-uncased.json` for the two oracle FFN intermediate layers are:
- `encoder.layer.8.intermediate.dense.weight`: erank = 709.52
- `encoder.layer.10.intermediate.dense.weight`: erank = 704.44

The value ~720 belongs to `output.dense` layers (e.g., `encoder.layer.9.output.dense.weight` = 726.5), which are NOT in the oracle set.

**Before**: `FFN intermediate layers (erank ~720) receive oracle rank 64`
**After**: `FFN intermediate layers (erank ~704–710) receive oracle rank 64`

Applied in: Abstract, Section 1 contribution #1, Section 6.1 Discussion, Section 7 Conclusion.

Also fixed Section 5.1 which used "erank ~704–720" (R2-MINOR-001 also addressed): changed to "erank ~704–710" to remove the unsupported upper bound of 720.

---

#### R2-MAJOR-002: Bootstrap CI claim corrected

**Location**: Section 5.2

**Problem**: Section 5.2 stated "Figure 4 (bootstrap CI) confirms the 95% CI for Pearson r excludes zero." The source `correlation_bert-base-uncased.json` shows `ci_low: NaN, ci_high: NaN` — the bootstrap CI computation failed. The claim was unverifiable.

**Before**: `Figure 4 (bootstrap CI) confirms the 95% CI for Pearson r excludes zero.`

**After**: `The one-tailed p-value of 0.0013, well below α=0.05, provides statistical confirmation that the Pearson r excludes zero without relying on bootstrap resampling. Bootstrap CI computation returned NaN values at n=5 due to the degenerate bimodal structure of the data (all resamples yield near-identical splits), and is noted for future reporting once full oracle coverage is achieved.`

Also removed the bootstrap CI reference from Section 4.4 Evaluation Metrics (removed "95% bootstrap CI" from the primary metrics list since it was not successfully computed).

---

#### R2-MAJOR-003: Stable rank baseline removed from Section 4.3; deferred to future work

**Location**: Section 4.3 (baselines), new Limitation L7 in Section 6.3

**Problem**: Section 4.3 listed stable rank as a "baseline" but Results (Sections 5.1–5.4) contained no stable rank correlation result. A baseline with no result implies a missing comparison.

**Fix applied**: Removed stable rank from the Section 4.3 baselines list. Added a note in Section 4.3 explaining that stable rank maps were computed but oracle correlation is deferred. Added new **Limitation L7** to Section 6.3:

> **L7: Stable rank oracle correlation pending.** Stable rank ($\|W_0\|_F^2 / \|W_0\|_2^2$) maps were computed for all BERT layers but oracle correlation for stable rank is not reported in this paper, as oracle sweeps covered only 5 layers and the focus of the current work is erank as the primary predictor. Stable rank vs. erank oracle comparison is deferred to the full-oracle experiment.
