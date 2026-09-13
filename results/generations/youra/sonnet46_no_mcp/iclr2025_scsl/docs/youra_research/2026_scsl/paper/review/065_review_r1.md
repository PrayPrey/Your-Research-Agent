# Adversarial Review Report — Round 1

**Date:** 2026-05-04
**Round:** 1 (Three-Persona Adversarial Review)
**Paper:** "Measuring the Spurious-Before-Core Temporal Gap: A Systematic Framework for SGD Feature Learning Dynamics"
**Hypothesis:** H-TemporalGap-v1
**Personas:** Accuracy Checker | Bored Reviewer | Skeptical Expert

---

## Ground Truth Summary

| Metric | Ground Truth Value | Paper Claim | Match? |
|--------|-------------------|-------------|--------|
| delta(t) window fraction | 13.3% (epochs 2-8 of 30) | 13.3% | ✓ |
| delta(t) p-value | 0.0219 | p = 0.022 | ✓ (rounding) |
| t-statistic | 4.619 | 4.619 | ✓ |
| Gap area mean | 0.040 | 0.040 | ✓ |
| Seeds | 3 (seeds 1, 2, 3) | 3 seeds | ✓ |
| GDR | 6.977 | 6.977 | ✓ |
| Spurious gradient norm | ~0.83 | ~0.83 | ✓ |
| Core gradient norm | ~0.118 | ~0.118 | ✓ |
| Wilcoxon p (GDR) | 0.125 | 0.125 | ✓ |
| FFT p-value | 0.033 | not explicitly stated | — |
| Intra-class variance p | 0.027 | not explicitly stated | — |
| Separability AUC p | 0.017 | not explicitly stated | — |
| t* mean | 2.00 epochs | 2.00 epochs | ✓ |
| t* std | 2.00 (sample std, n-1) | 2.00 | ✓ (if sample std) |
| t* 95% CI | [0.00, 2.31] | [0.00, 2.31] | ✓ |
| DFR WGA range | 0.806-0.871 | 0.806-0.871 | ✓ |
| Pearson r (DFR) | -0.8145 | -0.8145 | ✓ |
| Bonferroni threshold (methods) | α = 0.0167 (3 tests) | α = 0.0167 | stated in §3.3 |
| Bonferroni threshold (results) | α = 0.0167 | p < 0.0083 | **FATAL MISMATCH** |
| 10x sample-efficiency claim | N90_spurious=50, N90_core=500 | "10×" | ✓ |
| 598% above threshold | (6.977-1)/1 × 100 = 597.7% | "598%" | ✓ (rounding) |

---

## Executive Summary

This paper presents a measurement framework for SGD temporal feature learning dynamics and reports genuine empirical findings on the Waterbirds/ResNet-50 benchmark. Several numerical results are confirmed correct and the experimental design is reasonable for a proof-of-concept study. However, there is **one FATAL error** and **several MAJOR issues** that require correction before this paper is publishable.

**Issue Counts:**
- FATAL: 2 (one confirmed, one strong candidate)
- MAJOR: 6
- MINOR: 5

**Recommendation: Major Revision Required.** The Bonferroni threshold inconsistency between §3.3 and §5.1 is a fatal internal contradiction that undermines the H-M2 complexity claim. The DFR causal interpretation also requires significant softening. All other issues are addressable without repeating experiments.

---

## PERSONA 1: ACCURACY CHECKER — Findings

### FATAL Issues

**F-AC-1: Bonferroni Threshold Internal Contradiction**

Section 3.3 explicitly states: "Bonferroni correction for 3 simultaneous tests (adjusted α = 0.0167 per metric)."

Section 5.1 states: "All three metrics pass the Bonferroni-corrected threshold (p < 0.0083)."

These two statements are arithmetically incompatible. α=0.05/3=0.0167, not 0.0083. A threshold of p<0.0083 would correspond to 6 simultaneous tests (α=0.05/6), which is not mentioned anywhere. This is not a typo — the two sections report contradictory thresholds.

Furthermore, checking the actual p-values against even the more lenient stated threshold of 0.0167:
- FFT: p=0.033 — FAILS (0.033 > 0.0167)
- Intra-class variance: p=0.027 — FAILS (0.027 > 0.0167)
- Separability AUC: p=0.017 — PASSES (barely, 0.017 ≤ 0.0167)

The claim "All three metrics pass the Bonferroni-corrected threshold" is therefore **false by two counts**: (a) the threshold stated in results differs from the threshold stated in methods, and (b) two of three p-values fail the correct threshold. The sub-hypothesis H-M2 should be classified as PARTIAL-PASS at best (1/3 metrics pass Bonferroni), not PASS.

**Required fix:** Correct §5.1 to use the threshold from §3.3 (α=0.0167). Report that FFT (p=0.033) and variance (p=0.027) fail Bonferroni correction. Only separability (p=0.017) passes. Update H-M2 gate status to PARTIAL-PASS. Revise any downstream conclusions that cite "complexity hierarchy confirmed by all three metrics."

---

**F-AC-2: t* Standard Deviation — Sample vs Population Ambiguity (Borderline FATAL)**

Per-seed t* values from ground truth: seed1=4 epochs, seed2=2 epochs, seed3=0 epochs.

- Mean = (4+2+0)/3 = 2.00 ✓
- Population std (N denominator): sqrt(((4-2)²+(2-2)²+(0-2)²)/3) = sqrt(8/3) ≈ 1.633
- Sample std (N-1 denominator): sqrt(((4-2)²+(2-2)²+(0-2)²)/2) = sqrt(8/2) = 2.00

The ground truth file records t_star_std: 2.00, and the paper reports std=2.00. These are consistent only if sample standard deviation (N-1 denominator) was used. With n=3, the choice of denominator changes the reported std by approximately 22% (1.633 vs 2.00).

The paper does not state which std formula was used. This matters because:
1. With n=3, the distinction is substantial.
2. The 95% CI [0.00, 2.31] uses the t-distribution — the width depends on which std is used.
3. A reader who computes the population std from the seed values (a natural step) will get 1.633, not 2.00, and conclude the paper is incorrect.

**Classification:** Borderline FATAL. If sample std was intentionally used, this must be explicitly stated. The current omission is likely to generate a rejection-level comment from any reviewer who checks the arithmetic.

**Required fix:** State explicitly in §5.4 that sample standard deviation (Bessel's correction, n-1 denominator) is used throughout. Verify the CI calculation uses the t-distribution with n=3 (df=2), t=4.303 at 95%. Confirm the CI [0.00, 2.31] is consistent with the stated mean and std.

---

### MAJOR Issues

**M-AC-1: GDR Statistical Significance Not Formally Established**

The paper reports GDR=6.977 and describes this as "approximately 7× higher gradient signal." However, the Wilcoxon signed-rank test (the only formal significance test reported for GDR) yields p=0.125. The paper acknowledges this is "underpowered at n=3" in the limitations section, but the abstract and results sections describe the GDR finding in confident language without qualification.

Abstract: "approximately 7× higher gradient signal in early training (GDR = 6.977)"

This sentence in the abstract contains no indication that the between-seed comparison is not statistically significant. A reader who reads only the abstract will believe the 7× figure is a statistically robust finding. It is a consistent point estimate from a severely underpowered test.

**Required fix:** Add a parenthetical qualifier in the abstract, e.g., "(p=0.125, underpowered at n=3; see §6)." Soften results language in §5.2 to distinguish between the magnitude of the point estimate and the lack of formal statistical confirmation.

**M-AC-2: Abstract "p = 0.022" and the Bonferroni Cascade**

The abstract states "statistically significant temporal gap (p = 0.022)." This refers to the H-E1 delta(t) result and is numerically correct (p=0.0219, rounded). However, the abstract does not contextualize this finding relative to the failed Bonferroni tests in H-M2. A reader evaluating the abstract's claim that the "causal chain" is confirmed will expect all links to be statistically solid. The broken Bonferroni link in H-M2 (see F-AC-1) weakens this framing but is not acknowledged in the abstract.

**Required fix:** After fixing F-AC-1, revise the abstract to accurately represent the H-M2 status as partial rather than fully confirmed.

**M-AC-3: "598% above threshold" Claim Lacks Threshold Definition**

The paper states the GDR is "598% above threshold." The threshold here is implicitly GDR=1.0 (parity). The calculation (6.977-1)/1 × 100 = 597.7% ≈ 598% is arithmetically correct. However, the "threshold" of GDR=1.0 is never formally defined as such in the methodology. A reader cannot verify what the threshold is or why it is 1.0 without inference. This percentage framing also exaggerates rhetorical impact without additional interpretive value.

**Required fix:** Either define the threshold explicitly in §3 (e.g., "GDR > 1.0 indicates spurious gradient dominance") or remove the percentage framing in favor of the raw ratio.

---

### MINOR Issues (for human review)

- **MN-AC-1:** Abstract says "p = 0.022" — this is rounded from 0.0219. Acceptable rounding but consider reporting as "p = 0.0219" for precision consistency.
- **MN-AC-2:** Figure references in §5.1 mention "Figure 6 shows...Figure 7..." — verify these figure numbers are correct in final layout.
- **MN-AC-3:** The abbreviation "GDR" is introduced in the abstract but defined formally only in §3. Consider a brief parenthetical in the abstract.

---

## PERSONA 2: BORED REVIEWER — Findings

### FATAL Issues

*None from readability/engagement perspective that rise to fatal level.*

### MAJOR Issues

**M-BR-1: Abstract Buries the Lead — Counterintuitive Finding Not Front-Loaded**

The abstract opens with methodology framing ("We propose a measurement framework") rather than with the finding that would make a reader stop scrolling. The genuinely surprising result — that DFR achieves near-ceiling worst-group accuracy from epoch 1 onward, suggesting ImageNet pretraining matters more than training dynamics — is buried in the fifth sentence of the abstract.

For a competitive venue (NeurIPS, ICML), the opening sentence should announce the surprising finding, not the proposed tool. The current opening reads like a methods paper rather than a discovery paper.

**Required fix:** Restructure abstract to lead with the counterintuitive DFR finding or the unexpected universality of t* stability. Move the "measurement framework" framing to sentence 2.

**M-BR-2: Novelty Claim Clarity is Insufficient by Page 1**

A bored reviewer spending 2 minutes on this paper will encounter the phrase "first systematic, reproducible protocol for measuring δ(t)" in the introduction, but will not understand what was done before (qualitative observation only, per Mangalam & Girshick 2021) versus what this paper adds (quantitative, multi-metric, reproducible measurement). The gap is stated but not dramatized.

The paper needs a single crisp sentence early in the introduction that says something like: "Prior work has observed that shortcuts emerge early (Mangalam & Girshick 2021) but has not measured when, how fast, or how consistently this occurs. We provide the first measurements."

**Required fix:** Add a one-sentence prior-art gap statement to the introduction's second paragraph. This is a presentation issue, not a scientific one, but it affects reviewer reception significantly.

**M-BR-3: Engagement Drop in Section 4 (Experimental Setup)**

The experimental setup section reads as a list of hyperparameters without motivating the choices. A bored reviewer will skim Section 4 and be unable to reconstruct why 30 epochs (not 100 or 300) was chosen, why layer4 was used for GDR (not earlier layers), and why quadrant-based patch extraction is adequate for complexity measurement. These are addressed partially in the limitations but should be motivated in the setup section.

**Required fix:** Add 1-2 sentences of motivation for each non-obvious design choice in §4. Specifically: (a) why 30 epochs (PoC scope, explicitly), (b) why layer4 (final conv layer captures highest-level feature selectivity), (c) why quadrant-based (no segmentation masks available; see also Limitation L5).

---

### MINOR Issues (for human review)

- **MN-BR-1:** Introduction opening "learns the wrong answer first" is compelling colloquially but may read as imprecise to some reviewers. Consider "encodes spurious correlations preferentially in early training."
- **MN-BR-2:** The paper ends Section 5 with the DFR finding (§5.5) which contains the most surprising result, but the conclusion section does not adequately revisit why this reframes the contribution. The conclusion should emphasize the DFR finding more prominently.

---

## PERSONA 3: SKEPTICAL EXPERT — Findings

### FATAL Issues

**F-SE-1: (Reinforcing F-AC-1) H-M2 Bonferroni Failure Undermines the Causal Chain Narrative**

The paper's central contribution is described as "empirical confirmation of the causal chain: complexity → gradient → temporal gap." H-M2 (complexity hierarchy) is the first link in this chain. If only 1 of 3 complexity metrics passes Bonferroni correction (as the correct analysis shows), the complexity link is at best weakly supported.

The paper cannot claim "empirical confirmation of the causal chain" with 3/3 metrics if the correct Bonferroni-adjusted analysis shows 1/3 pass. This is not a minor labeling issue — it goes to the core contribution claim. If the causal chain's first link is PARTIAL-PASS, the paper's framing as a "confirmed" framework becomes an overclaim.

**Required fix:** Revise the causal chain claim to accurately reflect the partial evidence for complexity hierarchy. Alternatively, conduct additional experiments (more seeds, supplementary datasets) to achieve statistical power for the complexity metrics, or argue explicitly that Bonferroni is too conservative for this multi-metric design and propose an alternative correction.

---

### MAJOR Issues

**M-SE-1: DFR Causal Claim is an Unsupported Inference**

The abstract states: "ImageNet pretraining — not post-t* feature encoding — as the dominant driver of its robustness."

This is a causal claim derived from a correlational observation (DFR WGA is high even at epoch 1). The data shows that DFR WGA does not vary substantially across training depths (0.806-0.871), and that the Pearson correlation between training depth and DFR improvement is negative (r=-0.8145). These observations are consistent with ImageNet pretraining being important, but they do not rule out alternative explanations:

1. The DFR linear probe itself at epoch 1 is extracting features from ImageNet-pretrained weights, but "post-t* encoding" could still matter for non-DFR interventions.
2. The range 0.806-0.871 shows a positive trend (deeper training correlates with slightly higher WGA). Calling pretraining the "dominant" driver while acknowledging this trend requires formal decomposition (e.g., ablating ImageNet initialization) that the paper does not perform.
3. Negative r=-0.8145 with DFR improvement vs epochs-past-t* may indicate that training past t* helps somewhat, which would be the opposite direction from the "pretraining dominant" narrative.

The paper correctly classifies H-M4 as LIMITATION in the ground truth, but the abstract language does not reflect this nuance. The abstract's causal framing ("dominant driver") overstates what the correlational data supports.

**Required fix:** Soften the abstract claim to: "DFR achieves high worst-group accuracy even from epoch 1 (WGA 0.806), suggesting ImageNet pretraining may be a more important driver than post-t* feature encoding — though controlled ablation would be required to confirm this." Remove the word "dominant."

**M-SE-2: "Systematic Framework" Claim with Single Dataset**

The paper's title and introduction claim to provide "A Systematic Framework for SGD Feature Learning Dynamics." Section 6 acknowledges "Single architecture (ResNet-50 + ImageNet only)" as Limitation L6. However, the paper does not adequately justify calling the result a "systematic framework" when validated on a single dataset (Waterbirds) with a single architecture (ResNet-50) over 30 epochs.

A "framework" implies generalizability beyond the validation context. The paper's own limitations undermine this framing: CelebA was not replicated (L2), 300-epoch training was not performed (L1), and only ResNet-50 was tested (L6). The correct framing is "a proof-of-concept measurement protocol" or "a validated measurement approach for Waterbirds/ResNet-50."

**Required fix:** Qualify "systematic framework" throughout to "proof-of-concept framework" or add a statement in the abstract and introduction that the framework's generality is to be demonstrated in future work. The title itself may need revision.

**M-SE-3: Wilcoxon p=0.125 Cited as Evidence for MUST_WORK Criterion**

The ground truth marks H-M1 (GDR) as PARTIAL-PASS, with the paper noting "MUST_WORK satisfied." The Wilcoxon p=0.125 is cited as the significance test. A p=0.125 does not satisfy conventional significance thresholds (α=0.05) and would not be accepted as a passing statistical test by reviewers at major ML venues.

The paper correctly identifies this as underpowered (Limitation L3), but the classification of H-M1 as meeting a "MUST_WORK" criterion while the only formal test has p=0.125 is internally inconsistent. Either the criterion should be revised to not require formal significance (in which case what does it require?), or the test should be acknowledged as failing to establish significance.

**Required fix:** In §5.2, change the language from implying statistical confirmation to: "GDR=6.977 provides a strong point estimate of gradient dominance, though the Wilcoxon test (p=0.125) cannot confirm this due to insufficient power at n=3. Formal confirmation requires additional seeds."

**M-SE-4: t* CI [0.00, 2.31] Lower Bound at Zero Raises Questions**

The 95% CI for t* is [0.00, 2.31]. A lower bound of 0.00 means the CI is consistent with spurious features never appearing first (t*=0 means no gap). This is a remarkably wide CI given the paper's claim that t* is a "structural SGD property." The paper does not comment on the lower bound reaching zero.

For a claim of "structural property," a CI that includes zero should be explicitly addressed. The correct interpretation is: "we cannot rule out that in some seeds/runs, spurious features do not emerge first" — which would directly undermine the universality claim for t*.

**Required fix:** Add a sentence in §5.4 acknowledging that the CI lower bound of 0.00 is consistent with no gap in some cases, and discuss what this means for the structural property claim. This may require softening "structural SGD property" to "consistently observed but variable property."

**M-SE-5: Novelty Claim Defensibility Against Mangalam & Girshick [2021]**

The paper claims to be "the first to systematically measure δ(t)." Mangalam & Girshick [2021] is cited as observing shortcuts in early training qualitatively. However, the paper does not explain precisely what quantitative measurements Mangalam & Girshick did or did not perform. A skeptical reviewer familiar with that work could challenge the "first" claim if Mangalam & Girshick performed any form of checkpoint analysis.

The novelty claim would be strengthened by a brief explicit statement: "Mangalam & Girshick [2021] observed [specific qualitative claim] but did not quantify [specific measurement this paper introduces]." This specificity makes the novelty defensible.

**Required fix:** In the related work section, add explicit contrast: what M&G measured vs. what this paper measures. "First systematic" is defensible if framed precisely.

---

### MINOR Issues (for human review)

- **MN-SE-1:** The paper refers to "layer4" of ResNet-50 for GDR calculation. This is the last residual block before global average pooling. The paper should clarify whether gradients are taken with respect to the layer4 feature maps or the layer4 parameters, as these would give different norms.
- **MN-SE-2:** Quadrant-based patch extraction (top 40% = spurious, center 60% = core) is described in Limitation L5 as potentially inaccurate. However, no sensitivity analysis is reported. At minimum, a brief note on whether the 40%/60% split was validated against any ground-truth annotation would strengthen this.
- **MN-SE-3:** The paper describes a 30-epoch PoC but Waterbirds training in the literature typically uses 50-300 epochs. Some reviewers will question whether the temporal dynamics observed at 30 epochs are representative of full training. This should be addressed more directly in §4 or §6.

---

## Consolidated Issue List (Deduplicated, Prioritized)

| Priority | ID | Issue | Personas | Severity |
|----------|----|-------|----------|----------|
| 1 | FATAL-1 | Bonferroni threshold inconsistency: §3.3 says α=0.0167, §5.1 says p<0.0083; 2/3 metrics fail correct threshold; H-M2 must be PARTIAL-PASS | P1, P3 | FATAL |
| 2 | FATAL-2 | t* std denominator (sample vs population) not stated; ambiguity makes paper's reported std=2.00 unverifiable without hidden assumptions | P1 | FATAL (borderline) |
| 3 | MAJOR-1 | DFR causal claim ("ImageNet pretraining as dominant driver") is unsupported inference from correlation data | P3 | MAJOR |
| 4 | MAJOR-2 | GDR p=0.125 not statistically significant; abstract presents 7× finding without qualification | P1, P3 | MAJOR |
| 5 | MAJOR-3 | "Systematic framework" overstated for single-dataset, single-architecture, 30-epoch proof-of-concept | P3 | MAJOR |
| 6 | MAJOR-4 | t* CI [0.00, 2.31] lower bound at zero not addressed; inconsistent with "structural property" claim | P3 | MAJOR |
| 7 | MAJOR-5 | Abstract buries counterintuitive DFR finding; novelty framing insufficient for competitive venue | P2 | MAJOR |
| 8 | MAJOR-6 | Novelty claim against Mangalam & Girshick [2021] needs explicit quantitative contrast | P3 | MAJOR |
| 9 | MINOR-1 | Experimental setup lacks motivation for 30-epoch scope, layer4 choice, quadrant extraction | P2 | MINOR |
| 10 | MINOR-2 | "598% above threshold" framing — threshold (GDR=1.0) never formally defined | P1 | MINOR |
| 11 | MINOR-3 | layer4 gradient norm: clarify feature map vs parameter gradients | P3 | MINOR |
| 12 | MINOR-4 | Quadrant split (40%/60%) lacks sensitivity analysis | P3 | MINOR |
| 13 | MINOR-5 | Conclusion undersells DFR finding; should close on the most surprising result | P2 | MINOR |

---

## Persuasiveness Assessment

| Check | Assessment |
|-------|-----------|
| Core finding is real and replicable | YES — delta(t) window and t* are confirmed across 3 seeds |
| Statistical tests are appropriate (where used) | PARTIAL — Bonferroni correctly chosen but incorrectly applied; Wilcoxon underpowered |
| Numerical claims verified against ground truth | PARTIAL — most match; Bonferroni threshold in §5.1 is wrong |
| Causal chain narrative is supported | PARTIAL — H-E1 strong, H-M1 underpowered, H-M2 overstated, H-M4 LIMITATION |
| Abstract accurately represents findings | NO — DFR causal claim overclaims; Bonferroni issue concealed |
| Limitations are complete | MOSTLY — L4 (H-M4 confound) and L3 (underpowered) present, but t* CI zero-bound not addressed |
| Novelty is defensible | YES with qualification — "first systematic measurement" defensible if contrast with M&G 2021 sharpened |
| Paper is engaging/readable | PARTIAL — strong findings, but abstract buries the lead |

**Overall persuasiveness:** The paper has a genuine empirical core. The main risk is reviewer rejection on the Bonferroni issue, which is easy to catch and will appear as scientific dishonesty even if unintentional. The DFR overclaim is the second major credibility risk.

---

## Summary for Revision Agent

**MUST FIX BEFORE SUBMISSION (will cause rejection if not fixed):**

1. **[FATAL-1] Bonferroni correction error in §5.1:**
   - Change threshold from "p < 0.0083" to "p < 0.0167" (consistent with §3.3)
   - Report: FFT (p=0.033) FAILS, variance (p=0.027) FAILS, separability (p=0.017) PASSES
   - Update H-M2 classification to PARTIAL-PASS
   - Revise any sentence claiming "all three metrics confirm the complexity hierarchy"
   - Soften the causal chain claim to acknowledge partial complexity evidence

2. **[FATAL-2] t* std denominator disclosure in §5.4:**
   - Add explicit statement: "Standard deviation uses Bessel's correction (sample std, n-1 denominator)"
   - Verify CI [0.00, 2.31] is computed with t-distribution (df=2, t=4.303)
   - Note that population std would be 1.633; the sample std of 2.00 is used throughout

**SHOULD FIX (will attract major revision requests):**

3. **[MAJOR-1] DFR causal language in abstract and §5.5:**
   - Replace "dominant driver" with "potentially more important driver (requiring controlled ablation to confirm)"

4. **[MAJOR-2] GDR statistical qualification in abstract:**
   - Add "(Wilcoxon p=0.125, underpowered at n=3)" after the 7× claim

5. **[MAJOR-3] Title and framing of "systematic framework":**
   - Add "proof-of-concept" qualifier or "initial validation on Waterbirds/ResNet-50"

6. **[MAJOR-4] t* CI lower bound discussion in §5.4:**
   - Add one sentence acknowledging CI includes 0.00 and what this means for universality claims

7. **[MAJOR-5] Abstract restructuring:**
   - Lead with the counterintuitive DFR finding or t* stability result
   - Move framework framing to second sentence

8. **[MAJOR-6] Explicit novelty contrast with Mangalam & Girshick [2021]:**
   - Add: what they measured (qualitative), what this paper adds (quantitative: δ(t), gap area, t*)

**COLLECT FOR HUMAN REVIEW (minor issues, do not auto-fix):**
- MN-AC-1: p-value rounding (0.022 vs 0.0219)
- MN-AC-2: Figure number consistency check
- MN-AC-3: GDR acronym definition in abstract
- MN-BR-1: "learns the wrong answer first" phrasing precision
- MN-BR-2: Conclusion emphasis on DFR finding
- MN-SE-1: layer4 gradient clarification (feature map vs parameters)
- MN-SE-2: Quadrant split sensitivity note
- MN-SE-3: 30-epoch scope vs literature norms
