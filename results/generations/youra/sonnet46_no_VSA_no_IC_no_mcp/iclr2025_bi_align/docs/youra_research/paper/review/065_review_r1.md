# Adversarial Review — Round 1

**Date**: 2026-08-26
**Round**: R1 — Accuracy and Engagement
**Paper**: Quantifying Calibration-Alignment Divergence under RLHF Optimization Pressure

---

## Ground Truth Summary

| Claim | Ground Truth | Paper Reports | Match |
|-------|-------------|---------------|-------|
| Coste β | 0.1433 nat⁻¹ | 0.1433 nat⁻¹ | YES |
| Coste R² | 0.9577 | 0.9577 (table); 0.958 (text/abstract) | YES (rounded) |
| Coste p-value | 8.89e-07 | 8.89 × 10⁻⁷ | YES |
| Coste parametric CI | [0.1188, 0.1679] | [0.119, 0.168] | YES (rounded) |
| Coste bootstrap CI | [0.1170, 0.1768] | [0.117, 0.177] | YES (rounded) |
| Gao β | 0.1599 nat⁻¹ | 0.1599 nat⁻¹ | YES |
| Gao R² | 0.7008 | 0.7008 | YES |
| Gao p-value | 2.515e-03 | 0.0025 | YES (rounded) |
| Gao parametric CI | [0.075, 0.245] | [0.075, 0.245] | YES |
| Gao bootstrap CI | [-0.020, 0.236] | [−0.020, 0.236] | YES |
| Cross-dataset slope ratio | 1.116 | 1.116 | YES |
| Gold peak KL | 2.0 nats | ~2.0 nats | YES |
| Gold decline | 40% (0.63→0.38) | 40% (0.63→0.38) | YES |
| Max gap | 0.620 at KL=8.0 | 0.620 at KL=8.0 | YES |
| Spearman ρ(KL,RM) | 1.000 | 1.000 | YES |
| Coste n_observations | 10 | 10 | YES |
| Gao n_observations | 10 (ground truth) | "11 checkpoints" in Section 5.1 body text, but Table 4.1 and Section 5.5 table both say 10 | **DISCREPANCY** |
| Section 5.5 heading | Should be "Step 4" (only 4 steps) | "Step 5" | **ERROR** |

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 3 |

**Human Review Notes Count**: 7 (collected separately — NOT auto-fixed)

**Persuasiveness Assessment**:
- Abstract compelling: YES
- Problem clear in 1 minute: YES
- Novelty clear in 2 minutes: YES
- Figure 1 self-explanatory: YES (dual-axis concept is clearly described in caption reference)
- Would continue reading: YES
- Attention lost at: never (engagement holds through conclusion)

---

## PERSONA 1: Accuracy Checker

### FATAL Issues

None found. All primary numerical claims match ground truth within stated rounding.

### MAJOR Issues

**MAJOR-1: Section 5.1 says "11 checkpoints" for Gao but ground truth says n=10**

Section 5.1 (Step 1: Signal Co-existence) states: "in Gao et al. data, rm_var = 2.42 and gold_var = 0.31 across **11 checkpoints**."

Ground truth (065_ground_truth.yaml, line 102): `gao_n_kl_levels: 11` under `signal_coexistence` (H-E1). But the gao_regression entry (H-M4) states `n_observations: 10`. The datasets table (Section 4.1) lists "10 KL Checkpoints" for Gao. The appendix (Section B) references "11 KL checkpoints." The regression uses n=10.

This is a real inconsistency: H-E1 ground truth says Gao has 11 KL levels for signal coexistence, but H-M4 regression uses 10. The paper has not reconciled or explained this discrepancy. A reviewer will ask: were 1 or 2 checkpoints dropped from Gao for regression, and if so why? This is attackable and must be addressed with an explicit explanation — e.g., the first checkpoint at KL=0 was excluded from regression as a boundary point, reducing from 11 to 10 observations.

**MAJOR-2: Section 5.5 heading says "Step 5" but there are only 4 defined steps**

Section 3.5 (Four-Step Mechanistic Verification) defines exactly four steps: Step 1 (H-E1), Step 2 (H-M1), Step 3 (H-M2), Step 4 (H-M3, H-M4). Section 5.5 heading reads "Step 5: Cross-Dataset Replication (H-M4 — Replication)." There is no Step 5 in the defined framework. H-M4 is listed under Step 4 in Section 3.5.

A careful reviewer will see this immediately and conclude the paper is either internally inconsistent or the section numbering is an uncorrected draft artifact. This undermines precision credibility.

**MAJOR-3: The "first quantitative characterization" claim is potentially overclaimed without caveat**

The abstract states "the first quantitative, replicated regression characterization." This claim depends entirely on the premise that Coste et al. [2023] and Gao et al. [2023] — the very papers being analyzed — do not themselves present regression slopes. Section 2.1 asserts "Both papers describe the divergence qualitatively — RM rises while gold reverses — but stop short of fitting a regression model." If this is incorrect (e.g., if Gao et al. present any regression characterization of overoptimization), the central novelty claim collapses.

The paper never directly quotes or cites a passage from either source paper confirming the absence of regression analysis. Gao et al. [2023] is titled "Scaling Laws for Reward Model Overoptimization" — papers about scaling laws frequently include regression analysis. A skeptical reviewer will check Gao et al. and flag this if any regression slope appears there. The paper should either (a) directly quote the specific absence from both source papers, or (b) qualify the claim more narrowly (e.g., "no prior work regresses the normalized divergence gap on KL budget and reports cross-dataset slope comparison").

### Ground Truth Verification Log

- All CI bounds checked: reported values in Section 5.5 table are correct and consistent with ground truth (rounded).
- β values in abstract, introduction, and results tables: all consistent.
- Cross-dataset ratio 1.116 = 0.1599/0.1433: verified (0.1599/0.1433 = 1.1157... rounds to 1.116). Correct.
- Coste parametric CI reported in Section 5.4 table as [0.119, 0.168] vs ground truth [0.1188, 0.1679]: correct rounding.
- Gao bootstrap CI [-0.020, 0.236] disclosed in Section 5.5 table: correct, caveat present.
- Spearman ρ = 1.000 disclosed with caveat in Section 5.2: correct.
- Gap table (Section 5.3): values at KL=4,5,6,7,8 match ground truth exactly.
- N=10 claim: correct for regression; see MAJOR-1 for Gao H-E1 vs H-M4 discrepancy.
- Section numbering error (Step 5 vs Step 4): confirmed as numbering error (MAJOR-2).

---

## PERSONA 2: Bored Reviewer

### FATAL Issues

None. The paper does not fail catastrophically on engagement.

### MAJOR Issues

None that are purely engagement-driven beyond those already identified above.

### Engagement Assessment

**Opening paragraph (Introduction):** The hook works. The specific number (0.143), the counterintuitive framing ("more RLHF = worse alignment"), and the replication claim (12% slope agreement) appear in the first sentence. This is exactly the "surprising quantitative claim" strategy from the narrative blueprint. I kept reading.

**Abstract:** Compact and specific. β values, R², p-value, slope ratio, and the framing ("first quantitative, replicated regression characterization") are all present. At ~150 words, it is appropriately dense. The abstract earns a yes on "compelling."

**Problem clarity:** The surface/deeper/gap structure in the Introduction (bold headers) is clear and navigable. A busy reviewer can scan these three paragraphs and understand the position in under 60 seconds.

**Novelty positioning:** Section 2 (Related Work) positions the contribution clearly against Coste et al. and Gao et al. The argument — "they described it qualitatively; we fit a regression" — is simple and legible. Novelty is clear within 2 minutes.

**Figure 1 reference:** The paper references "Figure 1 (trajectory_dual_axis.png)" but the figures are not embedded in the markdown source. A reviewer reading the compiled PDF should see the figure inline; the caption reference is clear enough that a reviewer who sees only the figure can infer it shows RM monotone rise vs. gold preference peak-then-decline. The dual-axis concept is described adequately in the text.

**Attention risk:** Section 4 (Experimental Setup) is thin. The RQ list and dataset/metric tables are useful but the "Implementation Details" paragraph (Section 4.3) reads like boilerplate — Python, dataclass, flat src/ layout. A reviewer skimming this section will wonder if it's padding. This is a minor engagement drag, not fatal.

**Pacing:** The five-step results structure (5.1–5.6) works well; each section has a clear "What this means" conclusion that prevents the reviewer from getting lost in numbers.

**Overall verdict:** A bored NeurIPS reviewer would continue reading. The hook lands, the problem is clear, the numbers are specific and not generic. The only engagement risk is the Step 5 numbering error (MAJOR-2), which triggers a precision alarm in a careful reader.

---

## PERSONA 3: Skeptical Expert

### FATAL Issues

None found that are scientifically impossible or self-contradicting.

### MAJOR Issues

**MAJOR-3 (repeated from Persona 1):** The "first quantitative characterization" claim is vulnerable to challenge from Gao et al. [2023] specifically. Gao et al. study scaling laws for reward model overoptimization — the paper's title and the ICML venue both imply regression-based characterization. The skeptical expert will pull Gao et al. and check for any slope quantification. If Gao et al. include log-linear or power-law fits of their overoptimization curves, the novelty claim as stated fails.

The safe fix is to narrow the claim: instead of "the first quantitative regression characterization," write "the first regression characterization of the *normalized divergence gap* (RM_norm − gold_preference) as a function of KL budget, enabling cross-dataset slope comparison." This remains defensible because the normalization methodology and cross-dataset comparison are unambiguously new contributions, regardless of what Gao et al. fitted internally.

### Novelty and Credibility Assessment

**Is the phenomenon novel?** No — Coste et al. and Gao et al. already showed reward hacking qualitatively. The paper correctly acknowledges this and positions novelty in the *quantification and cross-dataset comparison* layer. This positioning is credible.

**Is the normalization methodology genuinely new?** Yes, within the scope of these two papers. The specific construct of min-max normalizing RM scores and computing RM_norm − gold_preference as a regression target is not described in either source paper (as far as can be determined from their abstracts and the paper's characterization of them).

**Spearman ρ = 1.000 — is this suspicious?** Yes. The paper addresses this in Section 5.2 caveat and Section 6.3 (L1), attributing it to digitization idealization. This is the correct and honest response. A skeptical expert will appreciate the disclosure. However, the caveat in Section 5.2 is brief and partially buried: "ρ = 1.000 is unexpectedly perfect for real experimental data; we attribute this likely to digitization idealization." This should be more prominent — perhaps a single sentence acknowledging it at first mention in the abstract or introduction would pre-empt reviewer attack.

**Bootstrap CI for Gao overlapping zero — is this adequately disclosed?** Yes. Table in Section 5.5 shows [-0.020, 0.236] explicitly, and the caveat paragraph explains the pre-registered criterion (parametric CI) and the mechanistic reason (non-monotone gap at low KL). The disclosure is adequate and honest.

**Data provenance — is digitization acknowledged clearly enough?** Mostly yes. Section 3.2 explicitly states "Data values are constructed consistent with qualitative descriptions in published figures using standard figure digitization methodology. This introduces an estimated ±2–5% digitization uncertainty per data point." Section 6.3 (L1) repeats this as a named limitation. The language "constructed consistent with qualitative descriptions" is appropriately cautious without being alarming. One concern: a reviewer may argue that "constructed consistent with qualitative descriptions" is not the same as "digitized from published figures using digitization software" — the former implies more manual construction than the latter. If the data was literally hand-constructed (not software-digitized), the honest description is accurate but may invite scrutiny about whether the data can be independently verified.

**Cross-dataset slope ratio 1.116 — overinterpreted?** The paper calls slopes "within 12%" a sign that "the divergence curve reflects a property of the RLHF optimization process itself" (Section 6.1, Finding 2). A skeptical expert will note that n=2 datasets is too small to establish "model-family-independent mechanism" — this is consistent with that mechanism but not confirming evidence. The language in Section 6.1 is appropriately hedged ("suggest" is used), but the Introduction is slightly stronger: "strong evidence this is not a model-family artifact" (Section 1, Contribution 3). "Strong evidence" from two datasets (both digitization-derived) is an overclaim in the introduction, even if the hedging in Discussion is correct.

**Limitations section — anything missing?** Four limitations (L1–L4) are identified. One missing limitation worth naming: the two datasets are not fully independent — they share the same general RLHF setup (PPO-based fine-tuning from human preference annotations) and the Gao paper was published contemporaneously and may have been influenced by similar experimental design choices. True independence requires different experimental paradigms (e.g., DPO vs. PPO, constitutional AI). The paper does not overstate independence, but it also does not explicitly limit the replication's scope.

---

## Human Review Notes (MINOR — for human review, NOT auto-fixed)

### Typos
- None identified.

### Grammar
- Section 5.2: "ρ = 1.000 is unexpectedly perfect for real experimental data; we attribute this likely to digitization idealization." — awkward: "we attribute this likely to" should be "we attribute this most likely to" or "this is likely attributable to."

### Style
- Introduction bold headers ("The surface problem," "The deeper problem," "The gap we address") are effective but atypical for ICML format. Verify this is style-guide compliant.
- Section 4.3 "Implementation Details" mentions "dataclass configuration, flat `src/` layout, and `sys.exit(0/1) gate result`" — implementation-speak that is meaningless to a paper reviewer and reads as padding. Trim or remove.

### Clarity
- Section 3.5: The four-step list labels steps "Step 1" through "Step 4" but does not number them explicitly (uses bullet points). This makes the mismatch with Section 5.5 heading "Step 5" harder to notice during proofreading. Convert the bullet list to a numbered list to make the count unambiguous.
- Section 6.1, Finding 2: "suggest a model-family-independent mechanism" — add parenthetical "(n=2 datasets; further replication required to establish universality)" to pre-empt reviewer objection.
- Appendix B mentions Gao data "across 11 KL checkpoints" — reconcile with the n=10 used in regression (see MAJOR-1). A footnote explaining why 11 levels appear in H-E1 but 10 in regression would resolve this.

### Formatting
- Section 5.5 table: Bootstrap CI column shows "−0.020" with en-dash typeset as minus — verify this renders correctly in LaTeX as a proper negative sign (use `$-0.020$` in math mode).
- References section uses inconsistent venue formatting: some entries have venue in italics (*NeurIPS 2022*), some in standard text. Standardize.

### Minor factual note (not an error but worth noting)
- The paper references ICLR 2025 Workshop as authority for the "400 papers" finding and "systematic measurement asymmetry" claim (P3). Since P3 was not independently verified (acknowledged as L3), the paper correctly attributes this claim to the survey — but should add "(qualitative finding, not independently verified in this work)" at first mention in Introduction (Section 1) to pre-empt a reviewer who might interpret it as a result of this paper.

---

## Summary for Revision Agent

**FATAL issues to fix (priority 1)**:
None.

**MAJOR issues to fix (priority 2)**:

1. **MAJOR-1: Gao checkpoint count inconsistency.** Section 5.1 says "11 checkpoints" for Gao; datasets table and regression use n=10. Add a footnote or parenthetical in Section 5.1 and Appendix B explaining that H-E1 plots 11 KL levels but H-M4 regression uses 10 (explain which checkpoint was excluded and why — e.g., KL=0 boundary excluded from regression). Reconcile the count in the datasets table (Section 4.1) if 11 is correct for H-E1.

2. **MAJOR-2: Section 5.5 heading says "Step 5" — fix to "Step 4."** The four-step framework defines exactly 4 steps; H-M4 is part of Step 4. Change heading to "Step 4: Cross-Dataset Replication (H-M4 — Replication)" and verify Section 3.5 bullet list is numbered explicitly so this stays consistent.

3. **MAJOR-3: Narrow the "first quantitative characterization" novelty claim.** Replace "first quantitative, replicated regression characterization" with "first regression characterization of the normalized divergence gap (RM_norm − gold_preference) as a function of KL budget, with cross-dataset slope comparison" — this is unambiguously defensible even if Gao et al. internally present regression fits of their own overoptimization curves. Also soften "strong evidence" in Introduction Contribution 3 to "consistent evidence" or "suggestive evidence (n=2 datasets)."

**Human Review Notes** (collected — human fixes later): 7 items
- Grammar fix in Section 5.2 ("we attribute this likely to")
- Style: verify ICML compliance for bold-header pattern in Introduction
- Style: trim Section 4.3 implementation boilerplate
- Clarity: convert Section 3.5 bullet list to numbered list
- Clarity: add n=2 caveat parenthetical in Section 6.1 Finding 2
- Clarity: add "(qualitative finding, not independently verified)" for P3/ICLR 2025 survey claim in Introduction
- Formatting: verify negative sign in Gao bootstrap CI renders correctly in LaTeX; standardize reference venue formatting
