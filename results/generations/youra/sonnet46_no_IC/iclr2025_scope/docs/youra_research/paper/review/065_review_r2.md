# Adversarial Review Round 2
**Paper**: Pre-Training Geometry Predicts Optimal LoRA Rank (R1 revised)
**Date**: 2026-08-05
**Round**: R2 — Numerical Verification and Credibility
**Personas**: Accuracy Checker, Skeptical Expert
**Execution Mode**: UNATTENDED

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL    | 0     |
| MAJOR    | 3     |
| MINOR    | 4     |

**Recommendation**: CONDITIONAL_ACCEPT
**New issues since R1**: 7 (3 MAJOR, 4 MINOR)

All four R1 MAJOR issues were fixed in the R1 revision. New numerical verification in R2 reveals one fresh MAJOR issue (erank values cited for oracle FFN layers are from the wrong layer sub-type) and two fresh MAJOR issues (bootstrap CI numerically absent; stable rank never evaluated). Four new MINOR issues also identified.

---

## Numerical Verification Log

| Claim | Paper Value | JSON/File Value | Match | Severity |
|-------|-------------|-----------------|-------|----------|
| Pearson r (BERT erank vs oracle) | 0.984 | 0.9836085 | ✓ correct rounding | OK |
| p-value one-tailed | 0.0013 | 0.001256491 | ✓ correct rounding | OK |
| PR–erank Pearson ρ | 0.968 | 0.96783 | ✓ correct rounding | OK |
| n oracle layers | 5 | 5 | ✓ | OK |
| BERT erank min (LoRA layers) | 543.2 | 543.171 (encoder.layer.0.attention.self.query) | ✓ | OK |
| BERT erank max | 726.6 | 726.557 (encoder.layer.9.output.dense) | ✓ | OK |
| BERT range ratio | 1.34× | 726.6/543.2 = 1.338 | ✓ | OK |
| ViT erank min | 244.4 | 244.4 (from ground_truth.yaml) | ✓ | OK |
| ViT erank max | 727.2 | 727.2 (from ground_truth.yaml) | ✓ | OK |
| ViT range ratio | 2.97× | 727.2/244.4 = 2.975 | ✓ | OK |
| DeBERTa erank min | 536.2 | 536.2 (from ground_truth.yaml) | ✓ | OK |
| DeBERTa erank max | 723.0 | 723.0 (from ground_truth.yaml) | ✓ | OK |
| DeBERTa range ratio | 1.35× | 723.0/536.2 = 1.348 | ✓ | OK |
| Oracle layers count | 5 | 5 (oracle_rank_map has 5 keys) | ✓ | OK |
| Oracle layer: encoder.layer.0.attention.output (rank) | r=4 | 4 | ✓ | OK |
| Oracle layer: encoder.layer.6.attention.output (rank) | r=4 | 4 | ✓ | OK |
| Oracle layer: encoder.layer.3.attention.self.query (rank) | r=4 | 4 | ✓ | OK |
| Oracle layer: encoder.layer.8.intermediate (rank) | r=64 | 64 | ✓ | OK |
| Oracle layer: encoder.layer.10.intermediate (rank) | r=64 | 64 | ✓ | OK |
| FFN intermediate erank "~720" (Abstract, Intro, Conclusion) | ~720 | encoder.layer.8.intermediate=709.5, encoder.layer.10.intermediate=704.4 | ✗ MISMATCH | MAJOR |
| FFN intermediate erank "~704–720" (Section 5.1) | ~704–720 | 709.5 and 704.4 | partial — upper bound ~709 not 720 | MINOR |
| Attention output erank "~557–590" | ~557–590 | encoder.layer.0.attention.output=556.9, encoder.layer.6.attention.output=590.3 | ✓ | OK |
| Query layer erank "~556" | ~556 | encoder.layer.3.attention.self.query=555.7 | ✓ | OK |
| Bootstrap 95% CI (JSON) | stated in paper | ci_low=NaN, ci_high=NaN | ✗ CI FAILED | MAJOR |
| BERT n layers (Table 2) | 72+1 | 73 keys in erank_map JSON | ✓ | OK |
| BERT CV | ~0.04 | (726.6−543.2)/mean≈614≈0.04 | ✓ | OK |
| Pooler.dense exclusion footnote | stated in Table 2 | pooler.dense erank=405.6 in JSON | ✓ (R1 fix applied) | OK |

---

## PERSONA 1: ACCURACY CHECKER (R2)

### FATAL Issues

None. All primary numerical claims (r, p, ρ, n, erank ranges) are verified against JSON source files.

### MAJOR Issues

**[R2-AC-MAJOR-001] FFN intermediate erank values cited as "~720" but oracle layers measure ~704–710**

- **Location:** Abstract ("FFN intermediate layers (erank ~720)"), Introduction Section 1 contributions ("FFN intermediate matrices (erank ~720)"), Conclusion Section 7 ("FFN intermediate matrices (erank ~720)")
- **Issue:** The paper repeatedly states FFN intermediate oracle layers have "erank ~720." The actual erank values from `erank_map_bert-base-uncased.json` for the two oracle FFN intermediate layers are:
  - `encoder.layer.8.intermediate.dense.weight`: **erank = 709.5**
  - `encoder.layer.10.intermediate.dense.weight`: **erank = 704.4**
  Neither is close to 720. The ~720 values in the erank map come from `output.dense` layers (not `intermediate.dense`), e.g., `encoder.layer.9.output.dense.weight` = 726.5 and `encoder.layer.10.output.dense.weight` = 726.6. The paper has apparently used the max erank for the FFN sub-layer type (output.dense) to characterize the oracle's intermediate.dense layers. This is a concrete numerical inaccuracy for the layers that are actually in the oracle set.
- **Ground truth:**
  - Oracle FFN layers (intermediate.dense): erank ≈ 704–710, not ~720
  - ~720 erank belongs to output.dense layers, which are NOT in the oracle set
  - Section 5.1 uses "erank ~704–720" which is a wider window — partially mitigating but still includes 720 as the upper bound when the actual oracle layer maximum is 709.5
- **Impact:** The abstract and introduction overstate the erank of the oracle FFN layers by ~10–15 units (approximately 1.5–2%). While small in absolute terms, this is a factual misattribution of an erank value to a layer that does not have that value. A reviewer checking the JSON would catch this.
- **Required fix:** Change "erank ~720" to "erank ~704–710" in abstract, introduction, and conclusion. Section 5.1's "~704–720" should be corrected to "~704–710". The value 720 belongs to FFN output.dense layers, not intermediate.dense layers.

**[R2-AC-MAJOR-002] Bootstrap 95% CI computed but values are NaN — paper claims CI confirms results**

- **Location:** Section 5.2 ("Figure 4 (bootstrap CI) confirms the 95% CI for Pearson r excludes zero"), Section 3.3 (methodology describes "Bootstrap 95% CIs via 1000 resamples")
- **Issue:** The `correlation_bert-base-uncased.json` shows:
  ```json
  "ci_low": NaN,
  "ci_high": NaN
  ```
  The bootstrap CI computation failed (returned NaN). Section 5.2 states "Figure 4 (bootstrap CI) confirms the 95% CI for Pearson r excludes zero" — but the underlying JSON has NaN CI values. This means either:
  (a) Figure 4 is fabricated or shows something other than the bootstrap CI from this JSON, or
  (b) The CI was computed separately and the JSON was not updated, or
  (c) The paper's claim that CI excludes zero cannot be verified from available data files.
  The summary.json also shows `"ci_low": NaN, "ci_high": NaN`.
- **Impact:** The claim "95% CI excludes zero" is unverifiable from the source data. At n=5, bootstrap CIs are inherently unreliable (insufficient resamples diversity). With bimodal data (3 vs. 2 split), bootstrap may consistently return r ≈ 0.98 across resamples — but this must be explicitly stated rather than implied by a non-existent or failed CI computation.
- **Required fix:** Either (a) report the actual CI bounds numerically if available, (b) acknowledge that bootstrap CI returned NaN due to the degenerate bimodal structure and remove the claim that Figure 4 confirms CI excludes zero, or (c) replace with an analytical confidence interval appropriate for n=5. The current claim is unsupported by the source JSON.

### MINOR Issues

**[R2-AC-MINOR-001] Abstract/Intro claim "erank ~704–720" in Section 5.1 partially inaccurate**

- **Location:** Section 5.1 body text: "two FFN intermediate layers (encoder.layer.8.intermediate.dense.weight, encoder.layer.10.intermediate.dense.weight; erank ~704–720)"
- **Issue:** The actual values are 709.5 and 704.4. The upper bound "~720" is not supported — the highest oracle FFN intermediate layer is 709.5. Section 5.1 is less wrong than the abstract (uses a range rather than a point ~720) but "~704–720" still implies a value near 720 exists in the oracle set when the actual oracle maximum is 709.5.
- **Required fix:** Change to "erank ~704–710" in Section 5.1.

**[R2-AC-MINOR-002] BERT erank min (543.2) attributed to wrong layer type in paper prose**

- **Location:** Abstract, Section 5.4
- **Issue:** The paper states "attention Q/K/V/O layers (erank ~530–611)" (Section 5.4). The actual minimum erank in the LoRA-targetable layer set is `encoder.layer.0.attention.self.query.weight` = 543.2. However, `encoder.layer.2.attention.self.key.weight` = 518.3 is the actual minimum if pooler.dense is excluded. The paper's Table 2 claims BERT erank min = 543.2, but the JSON shows 518.3 for `encoder.layer.2.attention.self.key.weight`. The ground_truth.yaml states `min_erank_excluding_pooler: 518.3` and `claimed_range_min: 543.2`, noting the paper uses a non-pooler range starting at 543.2. The ground_truth notes this as correct — but the footnote to Table 2 only mentions excluding `pooler.dense`, not also excluding other low-erank layers like key.weight at 518.3.
- **Detail:** From erank_map JSON: the minimum non-pooler erank is `encoder.layer.2.attention.self.key.weight` = 518.267, not 543.2. The 543.2 value is `encoder.layer.0.attention.self.query.weight`. So the paper's claimed range min of 543.2 is not the minimum of the LoRA-targetable layers — it's the minimum of the query weights in layer 0. The actual minimum (excluding pooler) is 518.3. This contradicts the footnote which says "range excludes pooler.dense" implying pooler is the only exclusion.
- **Severity:** This may indicate the BERT erank range 543.2–726.6 is computed over a subset of layers (e.g., only certain layer types), not all LoRA-targetable layers. The ground_truth.yaml marks this as "match: true" but the explanation is inconsistent. This needs clarification.
- **Required fix:** The Table 2 footnote should clarify exactly which layers are included in the range computation. If 543.2 is the min for query layers only, that should be stated. If the range is meant to cover all LoRA-targetable layers excluding pooler, the min should be 518.3.

---

## PERSONA 2: SKEPTICAL EXPERT (R2)

### FATAL Issues

None. The core claim is factually accurate and the revised paper is appropriately hedged.

### MAJOR Issues

**[R2-SE-MAJOR-001] Stable rank: listed as baseline, never evaluated — creates a misleading comparison frame**

- **Location:** Section 4.3 ("Stable rank: SRLoRA baseline from prior work"), Results (never mentioned again)
- **Issue:** Section 4.3 lists stable rank (`‖W₀‖_F²/‖W₀‖_2²`) as a "baseline." In Results (Sections 5.1–5.4), stable rank is never mentioned, compared to erank, or evaluated. The paper has no stable rank vs. erank correlation number, no stable rank vs. oracle rank correlation, and no discussion of whether stable rank would have produced a different result. Yet listing it as a "baseline" in Section 4.3 implies a comparison that never happens.
- **Impact:** A skeptical reviewer will immediately ask: "If stable rank is a baseline, what does it give? r=0.5? r=0.1? Why show erank is better without showing what stable rank gives?" The paper cannot claim erank is superior to stable rank without data. R1 review flagged this as MINOR-SE-02, but the R1 revision did not fix it — the R1 paper still lists stable rank in Section 4.3 with no result.
- **Required fix:** Either (a) compute and report stable rank vs. oracle rank correlation (r=? for BERT's 5 oracle layers) and include in Table 1 or a brief parenthetical, or (b) remove stable rank from Section 4.3 and do not describe it as a "baseline." The current state — listing it as a baseline with zero result — is the worst option.

### MINOR Issues

**[R2-SE-MINOR-001] "zero-cost" claim is framed correctly but SVD computation cost is underacknowledged**

- **Location:** Abstract ("zero-cost, zero-data LoRA rank allocation"), Introduction Section 1 ("zero-cost rank allocation strategy"), Section 2.5 ("zero-cost, zero-data rank predictor"), Conclusion
- **Issue:** "Zero-cost" is used in the specific sense of "zero training cost / no calibration data required." The SVD computation of W₀ is not literally zero-cost — for large models, it is O(d²k) per matrix. For BERT-base-uncased (768×3072 matrices), SVD is fast, but for LLaMA-70B (8192×28672), SVD becomes non-trivial. The paper's zero-cost claim is accurate within the paper's experimental scope (encoder-only models) but the framing does not acknowledge that "zero-cost" means "zero fine-tuning cost" rather than "zero compute."
- **Assessment:** This is a MINOR issue because (a) the paper's Section 2.5 already says "a single SVD pass from W₀ alone" which acknowledges some compute, (b) Limitation L3 covers the scope to encoder-only models, and (c) the field convention for "zero-cost" in this context is widely understood as "no training data or gradient computation." However, one sentence clarifying "zero-cost relative to training" would strengthen the framing.
- **Required fix:** In abstract or Section 2.5, clarify: "zero-cost (relative to fine-tuning: no training runs, gradient computation, or calibration data required; computation reduces to a single SVD pass over W₀)."

**[R2-SE-MINOR-002] ViT erank range ratio (2.97×) used as motivation for future work — possible overclaim**

- **Location:** Section 5.3 ("ViT exhibiting the largest within-model variation (erank range ratio 2.97×)"), Discussion 6.2 ("ViT's 2.97× erank range ratio, suggests strong prospects for cross-family confirmation")
- **Issue:** The paper argues ViT's larger erank range ratio implies "stronger discriminative power if oracle ranks are available" and "strong prospects for cross-family confirmation." This is used in Discussion 6.2 to suggest that ViT oracle results, when obtained, will likely show an even stronger correlation than BERT. This is speculative: a larger erank range does not guarantee a stronger oracle correlation — if ViT oracle ranks are also bimodal (or worse, uniform), the correlation may be lower regardless of erank range.
- **Assessment:** The R1 revision already converted the original "Implication" paragraph to a conditional ("if oracle ranks are available") framing per MAJOR-BR-02. The residual language in Discussion 6.2 ("suggests strong prospects") still slightly overclaims. However, it is marked clearly as a future direction in the same paragraph.
- **Required fix:** Change "suggests strong prospects for cross-family confirmation" to "motivates cross-family oracle sweeps, though the direction and magnitude of correlation cannot be predicted from erank variation alone." This removes the implicit prediction while retaining the motivational value.

**[R2-SE-MINOR-003] Overclaim language persists: "remarkably well" in Conclusion**

- **Location:** Conclusion Section 7, paragraph 1: "For BERT-base-uncased, it does — remarkably well."
- **Issue:** R1 MAJOR-003 (originally MINOR-BR-02) required removing "remarkably accurate" from the abstract. The Abstract was fixed (Abstract now says "remarkable accuracy" but qualifies it immediately with the bimodal structure caveat). However, the Conclusion still contains "remarkably well" without an accompanying caveat about n=5 bimodal structure. The editorial intensifier in the conclusion is not dangerous but is inconsistent with the hedging elsewhere.
- **Required fix:** Change to "For BERT-base-uncased, it does — with strong predictive discrimination (r = 0.984, n=5, bimodal oracle structure)." This keeps the positive result while being precise.

---

## Combined New Issues (Not in R1)

### FATAL

None.

### MAJOR

| ID | Persona | Location | Issue |
|----|---------|----------|-------|
| R2-MAJOR-001 | AC | Abstract, Intro, Conclusion | Oracle FFN intermediate layers cited as "erank ~720" but JSON shows 704.4 and 709.5; ~720 belongs to output.dense layers not in oracle set |
| R2-MAJOR-002 | AC | Section 5.2, 3.3 | Bootstrap CI in source JSON is NaN (failed); paper claims CI confirms result excludes zero — unverifiable |
| R2-MAJOR-003 | SE | Section 4.3, Results | Stable rank listed as baseline but never evaluated — cannot claim erank is superior without comparison data |

### MINOR

| ID | Persona | Location | Issue |
|----|---------|----------|-------|
| R2-MINOR-001 | AC | Section 5.1 | "erank ~704–720" for FFN oracle layers — upper bound 720 not supported; actual max is 709.5 |
| R2-MINOR-002 | AC | Table 2 footnote | BERT erank min 543.2 is not the true minimum of LoRA-targetable layers; actual min (excl. pooler) is 518.3; footnote scope unclear |
| R2-MINOR-003 | SE | Abstract, Intro, Conclusion | "zero-cost" framing does not acknowledge SVD compute cost; accurate within scope but could be clarified |
| R2-MINOR-004 | SE | Discussion 6.2, Conclusion | "remarkably well" (Conclusion) and "suggests strong prospects" (Discussion 6.2) are mild overclaim language |

---

## R1 Issues Verification

Confirmed that R1 MAJOR-001 through MAJOR-004 were addressed in the revised paper:

| R1 Issue | Fix Required | Status in R1-revised paper | Verdict |
|----------|-------------|---------------------------|---------|
| MAJOR-001: Layer mislabeling (attention.self.query called FFN) | Fix in Section 5.1; propagate "attention output" → "attention layers" | Section 5.1 now says "two attention output layers... and one attention query layer"; abstract/intro use "attention layers including query and output projections"; conclusion uses "attention layers — including both output projections and query projections" | ✓ FIXED |
| MAJOR-002: n=5 not disclosed in abstract; bimodal structure not stated | Add n=5 to abstract; add bimodal caveat | Abstract now contains "Pearson r = 0.984 (p = 0.0013, n=5 oracle layers)" and "The near-perfect correlation reflects binary discrimination between two structural tiers (erank < 600 → r*=4; erank > 700 → r*=64) rather than a smooth graded relationship" | ✓ FIXED |
| MAJOR-003: CV threshold (A1) unaddressed for BERT/DeBERTa | Add Limitation L5 | Discussion 6.3 now has Limitation L5 explicitly noting BERT/DeBERTa CV ~0.04 < 0.05, with explanation of why bimodal oracle compensates | ✓ FIXED |
| MAJOR-004: Depth confound with layer type unaddressed | Add depth confound to Discussion 6.3 | Discussion 6.3 now has Limitation L6 noting that attention layers span depths 0,3,6 and FFN layers span depths 8,10, with partial correlation noted as future work | ✓ FIXED |

Additional R1 MINOR fixes:
- MINOR-001 (stable rank formula typo): Section 4.3 now shows correct formula `$\|W_0\|_F^2 / \|W_0\|_2^2$` — ✓ FIXED
- MINOR-006 (Table 2 pooler footnote): Table 2 now has footnote "†BERT erank range excludes pooler.dense (erank=405.6), which is not a LoRA adaptation target and is an architectural outlier" — ✓ FIXED
- MINOR-004 (Section 5.3 speculative ViT paragraph): Section 5.3 reframed as conditional/motivational — ✓ FIXED
- MINOR-002 (editorial "remarkably accurate" in abstract): Abstract text is qualified by bimodal caveat — ✓ PARTIALLY FIXED (Conclusion still has "remarkably well" without full caveat — flagged as R2-MINOR-004)
- MINOR-005 (stable rank never evaluated): NOT FIXED in R1 revision — escalated to R2-MAJOR-003

---

## Summary for Revision Agent

**Priority fixes for R2:**

1. **[R2-MAJOR-001] CRITICAL NUMERICAL FIX:** Change "erank ~720" to "erank ~704–710" throughout abstract, introduction, and conclusion. The oracle FFN intermediate layers (encoder.layer.8 and encoder.layer.10 intermediate.dense) have erank 709.5 and 704.4 respectively. The value ~720 applies to output.dense layers not in the oracle set. This is the most important fix — a reviewer checking the JSON will catch this.

2. **[R2-MAJOR-002] BOOTSTRAP CI FIX:** The source JSON shows `ci_low: NaN, ci_high: NaN`. Section 5.2 should not claim CI "confirms" the result. Options: (a) acknowledge NaN and state CI is not computable from this JSON, (b) compute CI separately and report numerically, or (c) replace Section 5.2 CI claim with an analytical statement. Do not leave the current language that implies CI was successfully computed.

3. **[R2-MAJOR-003] STABLE RANK BASELINE:** Either add a stable rank correlation result (trivial to compute from pr_map and oracle_rank_map: compute stable rank values for the 5 oracle layers and correlate with oracle ranks), or remove stable rank from Section 4.3's baseline list. The current state of "baseline listed but never evaluated" is untenable for peer review.

4. **[R2-MINOR-001]:** Sync Section 5.1 "erank ~704–720" to "erank ~704–710".

5. **[R2-MINOR-002]:** Clarify Table 2 footnote — if BERT min of 543.2 excludes key.weight (518.3) in addition to pooler.dense, say so explicitly. Otherwise correct to 518.3.

6. **[R2-MINOR-003/004]:** Minor language polish: "zero-cost" clarification, "remarkably well" → precise language in conclusion.
