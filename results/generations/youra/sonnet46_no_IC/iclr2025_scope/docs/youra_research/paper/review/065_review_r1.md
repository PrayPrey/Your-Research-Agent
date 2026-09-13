# Adversarial Review Round 1
**Paper**: Pre-Training Geometry Predicts Optimal LoRA Rank
**Date**: 2026-08-05
**Round**: R1 — Accuracy and Engagement
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert
**Execution Mode**: UNATTENDED

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL    | 0     |
| MAJOR    | 4     |
| MINOR    | 6     |

**Recommendation**: MAJOR_REVISION
**Persuasiveness**: PASS (but fragile — bored reviewer stays engaged, barely)

---

## Ground Truth Verification

| Claim | Paper Value | Ground Truth | Match | Notes |
|-------|------------|--------------|-------|-------|
| Pearson r (BERT) | 0.984 | 0.9836085 | ✓ | Correct rounding |
| p-value (one-tailed) | 0.0013 | 0.001256 | ✓ | Correct rounding |
| PR–erank ρ | 0.968 | 0.96783 | ✓ | Correct rounding |
| n oracle layers | 5 | 5 | ✓ | |
| BERT erank range | 543.2–726.6 | 543.2–726.6 | ✓ | Excludes pooler.dense outlier (405.6) |
| DeBERTa erank range | 536.2–723.0 | 536.2–723.0 | ✓ | |
| ViT erank range | 244.4–727.2 | 244.4–727.2 | ✓ | |
| ViT range ratio | 2.97× | 2.975× | ✓ | |
| Oracle rank set | {4,8,16,32,64} | {4,8,16,32,64} | ✓ | |
| Baseline rank | r=8 | 8 | ✓ | |
| erank formula | Roy & Vetterli 2007 | Confirmed | ✓ | |
| FFN intermediate → r=64 | stated | confirmed | ✓ | |
| "attention output → r=4" | stated | PARTIAL | ⚠ | One r=4 layer is attention.self.query, not attention.output |
| Multi-family gate | PENDING | 1/3 families | ✓ | Paper correctly marks as pending |
| CV for BERT/DeBERTa | ~0.04 | ~0.04 | ✓ | Below A1 threshold of 0.05 |

**Critical finding:** The 5 oracle layers include `encoder.layer.3.attention.self.query.weight` (oracle rank 4, erank ~555.7). The paper conflates this with "attention output" layers in the abstract and introduction, and then — more severely — groups it with "three FFN intermediate layers" in Section 5.1 (sections file). This is a factual mislabeling.

---

## PERSONA 1: ACCURACY CHECKER

### FATAL Issues

None. All numerical claims match ground truth. The correlation, p-value, PR agreement, and erank ranges are all correctly stated or correctly rounded.

### MAJOR Issues

**[MAJOR-AC-01] Layer mislabeling: attention.self.query grouped with FFN layers (Section 5.1, sections file)**

- **Location:** `sections/05_results.md`, Section 5.1, paragraph 1; also `06_paper.md` Section 5.1
- **Issue:** `encoder.layer.3.attention.self.query.weight` receives oracle rank 4 and has erank ~555.7. In `sections/05_results.md`, this layer is listed parenthetically as one of "three FFN intermediate layers" — a clear mislabeling. It is an attention.self (query projection) layer, not an FFN layer.
- **Detail from sections/05_results.md:** "three FFN intermediate layers (encoder.layer.3.attention.self.query, encoder.layer.8.intermediate.dense, encoder.layer.10.intermediate.dense) receive oracle rank r* = 4–64"
- **Why matters:** This makes the "three FFN intermediate" count wrong (should be two FFN intermediate layers), miscategorizes a layer type, and misrepresents the oracle rank distribution. The query layer receives r*=4, not r*=4–64.
- **Ground truth:** oracle_layers_used lists 2 attention.output, 1 attention.self.query, 2 intermediate.dense. The claim "FFN intermediate → r=64, attention output → r=4" oversimplifies — the query layer also receives r=4 but is not an output layer.
- **Correct framing:** Two attention.output layers (r*=4), one attention.self.query layer (r*=4), two FFN intermediate layers (r*=64). Or: three attention-mechanism-adjacent layers receive r*=4; two FFN intermediate layers receive r*=64.
- **Required fix:** Correct the layer categorization in sections/05_results.md Section 5.1. Propagate to abstract and introduction where "two attention output layers" is stated. The abstract says "FFN intermediate layers (erank ~720) receive oracle rank 64 while attention output layers (erank ~557) receive oracle rank 4" — the directional claim holds but "attention output" should be "attention layers" to include the query layer.

**[MAJOR-AC-02] Abstract inconsistency: layer count mismatch**

- **Location:** Abstract (main paper), Introduction (Section 1, contributions list)
- **Issue:** Abstract states "FFN intermediate layers (erank ~720) receive oracle rank 64 while attention output layers (erank ~557) receive oracle rank 4." This implies a clean 2-tier split: FFN=high, attention-output=low. But the actual split is: 2 attention.output (r=4) + 1 attention.self.query (r=4) + 2 FFN.intermediate (r=64). The query layer has moderate erank (~555) which supports the correlation directionally, but calling all low-rank layers "attention output" is inaccurate.
- **Required fix:** Change "attention output layers" to "attention layers" (or "attention Q/O layers") throughout abstract and introduction to cover query.weight.

**[MAJOR-AC-03] Pooler.dense omitted from Table 2 erank range without disclosure**

- **Location:** Table 2 (Section 5.3), both in main paper and sections file
- **Issue:** Ground truth shows BERT has 73 layers including pooler.dense, with min erank 405.6 for pooler.dense. The paper claims erank min = 543.2 (the non-pooler minimum). Table 2 notes "72+1" in sections file but the main paper Table 2 uses "73" layers yet claims min = 543.2. The pooler is excluded from the range without explicit disclosure in the table itself.
- **Severity:** The range ratio 1.34× would be very different if pooler.dense (erank 405.6) were included (726.6/405.6 = 1.79×). The exclusion is reasonable (pooler is not a LoRA target) but needs a table footnote.
- **Required fix:** Add a table footnote: "erank range excludes pooler.dense (erank=405.6), which is not a LoRA adaptation target."

### MINOR Issues (collected, not auto-fixed)

- **[MINOR-AC-01]** Section 4.3 has a typo: `$\|W_0\|_2^^$` — double caret is a formatting error for the stable rank formula. Should be `$\|W_0\|_2^2$`.
- **[MINOR-AC-02]** Citation for LAARA [Tripathi et al., 2026] — paper notes 4 unverified citations (67% verification rate). LAARA (arXiv:2607.19391) and IFCLoRA (arXiv:2607.22251) and IGU-LoRA (arXiv:2603.13792) are 2026 preprints with no verification status confirmed. Flag for human review.
- **[MINOR-AC-03]** The paper mentions "participation ratio" in two different formulations without clarifying that PR and erank are related (both derived from singular values) but distinct — a one-sentence clarification in Section 3.1 or 3.3 would help.

---

## PERSONA 2: BORED REVIEWER

*Setting: 5 papers queued, 20 minutes per paper, NeurIPS area chair track.*

### Persuasiveness Checks

| Check | Result | Notes |
|-------|--------|-------|
| abstract_compelling | PASS | r=0.984 is a strong hook number; "zero-shot" framing is clean |
| problem_clear_in_1_minute | PASS | Intro paragraph 1 sets up the contrast well |
| novelty_clear_in_2_minutes | PASS | Section 2.5 position statement is clear and direct |
| figure_1_self_explanatory | N/A | Figures described but not included in text files; described well enough in prose |
| would_continue_reading | YES | Barely — the n=5 caveat in Table 1 raised a red flag at minute 2 |
| attention_lost_at | Section 5.3 | erank maps without oracle data feel like filler; the ViT "implications" paragraph promises results that aren't there |
| hook_works | PASS | Counterintuitive contrast ("weights already know") is effective |
| honest_about_n5 | PASS | Table 1 marks "5 layers" as ⚠ PARTIAL; Discussion 6.1 addresses it; but the abstract buries the caveat |

### FATAL Issues

None from the engagement perspective.

### MAJOR Issues

**[MAJOR-BR-01] Abstract does not disclose n=5 limitation — creates misleading first impression**

- **Location:** Abstract
- **Issue:** Abstract presents r=0.984 (p=0.0013) without mentioning n=5. A reviewer reading the abstract would assume this is a reasonably powered statistical test. The n=5 caveat only appears in Table 1 (Section 5). For a bored reviewer who reads only the abstract, the impression is that this is a robust correlation result — which it arguably is not, at n=5 with a bimodal distribution (it's really a binary classification with 5 data points, not a standard Pearson correlation).
- **Required fix:** Add "over 5 oracle-measured layers" (or similar) to the abstract. Example: "...at Pearson r = 0.984 (p = 0.0013, n=5 oracle measurements)"

**[MAJOR-BR-02] Section 5.3 (erank maps) presents hypothesis/speculation as implication without data**

- **Location:** Section 5.3, final paragraph ("Implication: If ViT's larger erank range translates...")
- **Issue:** This paragraph speculates that ViT oracle results will be stronger than BERT. Without oracle data, this is pure conjecture dressed as an implication. A busy reviewer will note that Section 5.3 adds no evidence to the central claim — only motivation for future experiments that aren't in this paper.
- **Required fix:** Reframe as a research hypothesis or motivating observation, not an "implication." Or remove the speculative paragraph and replace with a factual statement about what the erank variation means for discriminative power without making predictions.

### MINOR Issues

- **[MINOR-BR-01]** Section 5.1 in the main paper refers to "Figure 1 (scatter plot)" and "Figure 4 (bootstrap CI)" without the figures being available in the submitted text. This is expected for a draft, but figure captions should be included in the sections to allow evaluation.
- **[MINOR-BR-02]** The phrase "remarkably accurate" in the abstract is editorial. The correlation is excellent — the number speaks for itself. Remove the adverb.
- **[MINOR-BR-03]** Conclusion paragraph 2 states "FFN intermediate matrices (erank ~720) receive oracle rank r*=64; attention output matrices (erank ~557) receive oracle rank r*=4." Same mislabeling issue as abstract — query.weight is missing from this accounting.

---

## PERSONA 3: SKEPTICAL EXPERT

*Setting: LoRA/PEFT expert who has reviewed 3 AdaLoRA papers and is tired of overclaims.*

### FATAL Issues

None. The core claim (erank correlates with PARA oracle ranks at r=0.984, n=5, BERT only) is factually accurate and properly hedged in the discussion.

### MAJOR Issues

**[MAJOR-SE-01] n=5 bimodal oracle: the statistical claim is structurally misleading**

- **Location:** Abstract, Section 5.1, Discussion 6.1
- **Issue:** With n=5 data points where oracle ranks are bimodal (exclusively 4 or 64), Pearson r=0.984 with p=0.0013 is computing a point-biserial correlation, not a standard linear correlation. The p=0.0013 is driven by perfect binary separation (3 vs. 2 split), not by evidence of a graded linear relationship between erank and rank. Calling this "remarkable accuracy" or even "correlation" implies a graded relationship that the data do not demonstrate.
- **The actual statistical situation:** We have 5 points in 2 clusters. Any continuous predictor that separates the clusters perfectly (even slightly different threshold values) would also yield r ≈ 0.98. The p-value reflects perfect binary classification, not a general monotone relationship over the erank range.
- **Missing in Discussion:** The paper acknowledges bimodality in 6.1 ("correlation is not a smooth linear relationship but a near-perfect tier classification") — this is honest, but the abstract and introduction still use standard "Pearson r = 0.984" language that implies a graded relationship. The paper needs to be more explicit in its framing: this is a binary structural discrimination result, not a general rank prediction correlation.
- **Required fix:** Add a sentence to the abstract: "The near-perfect correlation reflects binary discrimination between two structural tiers (erank separating oracle ranks 4 vs. 64), rather than a smooth graded relationship; full-range validation over all 72 layers is pending." The contribution framing must be honest about what r=0.984 with n=5 bimodal data actually demonstrates.

**[MAJOR-SE-02] CV threshold not met for BERT/DeBERTa — A1 assumption unaddressed**

- **Location:** Table 2 (Section 5.3), Discussion
- **Issue:** Ground truth confirms BERT CV ~0.04 and DeBERTa CV ~0.04, both below the pre-registered A1 threshold (CV > 0.05). Only ViT (CV ~0.12) meets this threshold. The paper shows CV values in Table 2 but does not discuss what this means for the A1 assumption validity for BERT/DeBERTa. The claim that erank "discriminates" BERT layers implicitly assumes sufficient variation — but the BERT oracle correlation was achieved despite CV < 0.05 because of bimodal oracle structure compensating for modest erank spread.
- **Why this matters:** A reviewer can legitimately argue that BERT's erank variation (543–727, ratio 1.34×) is too modest for erank to function as a reliable continuous predictor. The bimodal result gets around this, but if the oracle is not bimodal (e.g., for full 72-layer coverage), the modest CV may mean erank has insufficient discriminative power.
- **Required fix:** Add a Limitation L5: "BERT and DeBERTa erank variation (CV ~0.04) falls below the pre-registered A1 threshold (CV > 0.05), suggesting modest discriminative power for these NLP encoders. The observed correlation is valid because the oracle rank structure is bimodal; continuous rank discrimination across the full erank range remains to be tested."

**[MAJOR-SE-03] Depth confound not addressed**

- **Location:** Discussion 6.3, Conclusion
- **Issue:** The paper mentions in the Conclusion "partial correlation controlling for depth" as a future direction, but does not address whether the observed erank-oracle correlation is confounded by layer depth. In transformer encoders, FFN layers (higher erank in this data) and attention layers (lower erank) are structurally alternating — but within layer types, deeper layers often have different erank than shallower ones. The 5 sampled layers span layers 0, 3, 6, 8, 10 of a 12-layer encoder. The query layer (layer 3, erank ~555) vs. the FFN layers (layers 8, 10, erank ~705–720) — is the erank difference due to layer type or layer depth?
- **Ground truth shows:** encoder.layer.0.attention.output (r=4), encoder.layer.6.attention.output (r=4), encoder.layer.3.attention.self.query (r=4) vs. encoder.layer.8.intermediate (r=64), encoder.layer.10.intermediate (r=64). All attention layers are in earlier/middle layers; FFN layers in later layers. This is a confound with depth that cannot be disentangled from the current 5-layer sample.
- **Required fix:** Add as Limitation L5 (or rename existing L1-L4 to accommodate): "The 5 measured oracle layers include attention layers from depths 0, 3, 6 and FFN layers from depths 8, 10. Depth is confounded with layer type in this sample; whether erank predicts oracle rank independently of depth cannot be assessed until full-coverage oracle sweeps are completed."

### MINOR Issues

- **[MINOR-SE-01]** The novelty claim "first to test erank(W₀) as rank predictor" (Section 2.5) is defensible based on Phase 1 research, but the paper should more explicitly compare to IFCLoRA's calibration-based approach — one sentence noting that IFCLoRA also uses pre-fine-tuning signals but requires a forward pass would sharpen the distinction and preempt reviewer challenges.
- **[MINOR-SE-02]** The stable rank baseline (Section 4.3) is mentioned as "SRLoRA baseline from prior work" but no result is reported comparing it to erank. Either include a SR vs. erank correlation comparison or remove the claim that stable rank is a baseline (it's listed in setup but never evaluated in results).
- **[MINOR-SE-03]** The PARA oracle assigns rank per layer with all others frozen at r=8. This means the oracle rank for layer A depends on all other layers being set to r=8 — a marginal, not joint, oracle. The paper acknowledges this (L2) but understates the potential impact: if other layers should be at r=64, layer A's "optimal" rank at r_others=8 may not be its optimal rank in a joint allocation. This limitation deserves more prominence given the paper's claim of identifying "optimal" per-layer rank.

---

## Combined Issue List (Deduplicated)

### FATAL Issues

None.

### MAJOR Issues

| ID | Source | Location | Issue |
|----|--------|----------|-------|
| MAJOR-001 | AC-01 + BR (Conclusion) | Section 5.1 (sections file), Abstract, Introduction, Conclusion | `encoder.layer.3.attention.self.query.weight` mislabeled as FFN layer; "attention output layers" framing excludes the query layer that also receives r=4 |
| MAJOR-002 | BR-01 + SE-01 | Abstract | n=5 not disclosed in abstract; r=0.984 with bimodal n=5 implies a graded linear correlation that the data do not demonstrate |
| MAJOR-003 | SE-02 | Table 2, Discussion | CV threshold A1 not met for BERT/DeBERTa (CV ~0.04 < 0.05); limitation not acknowledged |
| MAJOR-004 | SE-03 | Discussion 6.3, Conclusion | Depth confound with layer type unaddressed in the 5-layer sample (attention layers at depths 0,3,6; FFN layers at depths 8,10) |

### MINOR Issues for Human Review

| ID | Location | Issue |
|----|----------|-------|
| MINOR-001 | Section 4.3 | Typo: `$\|W_0\|_2^^$` should be `$\|W_0\|_2^2$` |
| MINOR-002 | References | 4 unverified 2026 citations (LAARA, IFCLoRA, IGU-LoRA, La-LoRA) — verify before submission |
| MINOR-003 | Abstract | "remarkably accurate" — remove editorial adverb; r=0.984 speaks for itself |
| MINOR-004 | Section 5.3 | Speculative "Implication" paragraph (ViT oracle will be stronger) — reframe as hypothesis |
| MINOR-005 | Section 4.3, Results | Stable rank listed as baseline but never evaluated in results section |
| MINOR-006 | Table 2 | No footnote disclosing pooler.dense exclusion (erank=405.6) from BERT range |

---

## Summary for Revision Agent

Priority fixes needed:

1. **[MAJOR-001]**: Correct layer mislabeling throughout. `encoder.layer.3.attention.self.query.weight` is an attention layer (oracle rank 4, erank ~555.7), not an FFN layer. Fix in sections/05_results.md Section 5.1 (parenthetical list), and propagate "attention output" → "attention layers" in abstract, introduction, and conclusion. The correct layer breakdown: 2 attention.output (r=4), 1 attention.self.query (r=4), 2 FFN.intermediate (r=64).

2. **[MAJOR-002]**: Add n=5 disclosure to abstract. Add a clause acknowledging bimodal structure in abstract: e.g., "...Pearson r = 0.984 (p = 0.0013, n=5 oracle measurements); the near-perfect correlation reflects binary discrimination between two structural tiers (erank < 600 → r=4; erank > 700 → r=64) rather than a smooth graded relationship." This preempts the most obvious reviewer attack.

3. **[MAJOR-003]**: Add a Limitation (L5) explicitly noting BERT/DeBERTa CV ~0.04 falls below the A1 threshold (CV > 0.05), and explaining why the BERT oracle correlation is valid despite this (bimodal oracle structure provides natural discrimination even with modest erank variation).

4. **[MAJOR-004]**: Add depth confound to Discussion 6.3 limitations. One sentence: "The 5 sampled layers confound layer type with depth (attention at layers 0,3,6; FFN at layers 8,10); partial correlation controlling for depth is needed to isolate the erank signal." The Conclusion already mentions this as a future direction — bring the acknowledgment forward to the Discussion.

5. **[MINOR-001]**: Fix stable rank formula typo in Section 4.3.

6. **[MINOR-006]**: Add footnote to Table 2 about pooler.dense exclusion.
