# Adversarial Review Round 1

**Paper**: "When Shortcuts Hide in Plain Sight: Feature-Strength Conditionality in Annotation-Free Spurious Direction Recovery"
**Review Date**: 2026-05-20
**Round**: R1 — Accuracy and Engagement
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Ground Truth Verification Summary

| Claim | Paper Value | Ground Truth | Match | Notes |
|-------|-------------|--------------|-------|-------|
| Waterbirds AMI | 0.762 | 0.7622 | ✓ | Correct 3-dp rounding |
| Waterbirds Purity | 0.892 | 0.8919 | ✓ | Correct 3-dp rounding |
| Waterbirds Random AMI | 0.0001 | 0.0001 | ✓ | Exact match |
| Waterbirds Random Purity | 0.727 | 0.7276 | ✓ | Correct rounding |
| CelebA AMI | 0.258 | 0.2578 | ✓ | Correct 3-dp rounding |
| CelebA Purity | 0.456 | 0.4557 | ✓ | Correct 3-dp rounding |
| CelebA Random AMI | 0.000 | -0.0000 | ✓ | Effectively zero |
| CelebA Random Purity | 0.440 | 0.4395 | ✓ | Correct rounding |
| Waterbirds Train Loss (ep5) | 0.088 | 0.0881 | ✓ | Correct rounding |
| Waterbirds Train Acc (ep5) | 96.66% | 96.66% | ✓ | Exact match |
| CelebA Train Loss (ep5) | 0.124 | 0.1240 | ✓ | Exact match |
| CelebA Train Acc (ep5) | 95.00% | 95.00% | ✓ | Exact match |
| Waterbirds N | 4,795 | 4795 | ✓ | Exact match |
| CelebA N | 162,770 | 162770 | ✓ | Exact match |
| "Threefold" AMI gap | ~3x | 0.762/0.258=2.95x | ✓ | Acceptable approximation |
| DFR worst-group Waterbirds | ~97% | ~97% | ✓ | Verified via Semantic Scholar |
| JTT worst-group Waterbirds | ~82-86% | ~82-86% | ✓ | Verified via Semantic Scholar |
| GroupDRO worst-group Waterbirds | ~90% | ~90% | ✓ | Verified via Semantic Scholar |
| PruSC CelebA purity >95% | >95% | UNVERIFIED | ? | Kim et al. 2024 not found in Semantic Scholar — MEDIUM RISK |
| Optimizer | SGD, momentum=0.9 | SGD, momentum=0.9 | ✓ | Exact match |
| Learning rate | 1e-3 | 0.001 | ✓ | Exact match |
| Weight decay | 1e-3 | 0.001 | ✓ | Exact match |
| Batch size | 32 | 32 | ✓ | Exact match |
| k-means k | 2 | 2 | ✓ | Exact match |
| k-means n_init | 10 | 10 | ✓ | Exact match |
| Seed | 42 | 42 | ✓ | Exact match |
| GSB (H-M4) tested? | Implied in framing | NOT_STARTED in verification_state | RISK | Abstract implies downstream consequence validated; it is not |

---

## Executive Summary

**FATAL issues**: 1
**MAJOR issues**: 4
**MINOR issues**: 8 (collected for human review)
**Recommendation**: CONDITIONAL_ACCEPT

All quantitative claims are numerically verified against ground truth — this paper's empirical core is sound. The core finding (feature-strength conditionality of annotation-free clustering) is genuine, well-characterized, and practically important. However, one FATAL issue exists: the abstract contains a sentence that implies the downstream GSB failure consequence was empirically observed, when GSB (H-M4) was never tested. Four MAJOR issues cover: (1) the PruSC unverified citation on which C4 depends; (2) the C3 pre-screen presented as a contribution without any validation experiment; (3) the "first systematic characterization" claim in C1 asserted without adequate related work justification; (4) the PruSC comparison framing conflating configuration differences with replication failure. All issues are correctable without major restructuring.

---

## FATAL Issues

### FATAL-001: Abstract implies GSB downstream mechanism is empirically validated

**Location**: Abstract, final sentence: "Our results reveal a silent failure mode in downstream robustification pipelines"

**Evidence**: The verification_state.yaml shows H-M4 (GSB intervention) status = NOT_STARTED. Section 6.3 Limitation L4 states explicitly: "The Gradient SNR Balancing (GSB) intervention — equalizing gradient SNR along cluster-discovered directions to improve worst-group accuracy — was blocked by the CelebA gate failure. The mechanistic chain (H-M1 through H-M4) is theoretically motivated but not empirically validated."

**Problem**: The abstract sentence "Our results reveal a silent failure mode in downstream robustification pipelines" is placed after reporting the detection experiment results, causing a reader to infer that the downstream failure mode was empirically demonstrated. It was not. Only the detection step (H-E1) was tested. The downstream consequence is a logical inference, not an experimental finding.

**Required Fix**: Revise the abstract sentence to make the logical/inferential status explicit:

> "Our results characterize a detection failure mode that would constitute a silent failure in downstream annotation-free robustification pipelines if propagated — though the downstream consequence is not empirically validated in this work."

Additionally, ensure no other language in the abstract or introduction conflates the detection finding with a downstream validated effect.

---

## MAJOR Issues

### MAJOR-001: C4 contribution depends on unverified PruSC citation

**Location**: Introduction paragraph 3, Section 5.5, Contribution C4, References

**Evidence**: The paper states "The PruSC paper [Kim et al., 2024] reports >95% cluster purity on CelebA; our identical experimental configuration yields purity=0.456." This comparison anchors Contribution C4 ("Identification of configuration-sensitivity in published results"). The ground truth risk flags note: "Kim et al. 2024 PruSC paper not found in Semantic Scholar. MEDIUM RISK — if PruSC paper doesn't exist or doesn't claim 95%, the comparison is invalid." The reference entry already carries an [UNVERIFIED] tag.

**Problem**: C4 is one of four stated contributions. If the citation is wrong (incorrect year, authors, non-existent paper, or misremembered result), the contribution collapses and the paper faces a fabrication accusation from reviewers who cannot locate the source.

**Required Fix**:
- Option A (preferred): Independently verify Kim et al. 2024 PruSC and provide DOI/arxiv URL in the reference entry. Remove [UNVERIFIED] tag.
- Option B (if unverifiable): Remove the PruSC-specific comparison. Replace C4 with: "We identify that published annotation-free clustering results are configuration-sensitive: results obtained at training convergence with k>2 do not transfer to the early-epoch, k=2 configurations required by intervention methods, a gap not disclosed in existing reporting."

### MAJOR-002: C3 (pretrained linear probe pre-screen) listed as contribution without validation

**Location**: Contribution list C3 (Section 1), Section 6.2

**Evidence**: The ground truth notes C3 is "Proposed but not experimentally validated in this paper — framed as proposal." Section 6.2 proposes a linear probe with a specific threshold (~70% accuracy) but reports no experiment. No table or figure in the paper validates this threshold. Yet C3 in the contributions section says "We explain the conditionality through ImageNet pretraining alignment and propose a spurious feature salience pre-screen — a lightweight diagnostic that practitioners can use before trusting annotation-free cluster-based spurious direction estimates."

**Problem**: A reviewer will note the absence of any linear probe experiment validating the ~70% threshold and call out that an untested proposal does not constitute an experimental contribution. The framing as a contribution (not as future work) invites this criticism.

**Required Fix**:
- Option A (preferred): Add a simple experiment — train a linear probe on pretrained (pre-fine-tuning) ResNet-50 embeddings for the spurious attribute on Waterbirds and CelebA. Report probe accuracy. This would also mechanistically support Finding 1. One table suffices.
- Option B: Move the linear probe proposal from the contribution list to Section 6.2 Discussion, explicitly labeled as "unvalidated proposed diagnostic." Change "propose a spurious feature salience pre-screen" in C3 to "explain the mechanism and motivate a proposed future diagnostic."

### MAJOR-003: "First systematic characterization" novelty claim inadequately supported

**Location**: Contribution C1 (Section 1), Section 2.4

**Evidence**: C1 states "We provide the first systematic characterization of when annotation-free clustering-based spurious direction discovery succeeds and fails." Section 2.4 asserts the gap exists ("none of these methods characterize the conditions under which the clustering step succeeds") without demonstrating that no prior work addresses this. The related work survey is thin (~150 words in Section 2.4) and does not engage with: (a) the DFR paper's implicit analysis of when ERM representations encode spurious features; (b) GEORGE's own discussion of clustering quality; (c) any representational geometry literature.

**Problem**: "First" is the strongest novelty claim. A skeptical reviewer familiar with the representation learning / shortcut literature can find reasons to challenge this claim. The paper does not demonstrate the gap — it asserts it. This weakens C1 credibility.

**Required Fix**: In C1 and Section 2.4, change "the first systematic characterization" to "to our knowledge, the first systematic characterization." Add 2-3 sentences to Section 2.4 explicitly noting what the closest prior works say about clustering failure conditions and why they fall short: e.g., GEORGE notes cluster quality depends on representation quality but does not study the pretraining alignment determinant; DFR shows ERM encodes invariant features but does not study the clustering step reliability.

### MAJOR-004: PruSC comparison framing conflates configuration difference with replication failure

**Location**: Section 5.5, Introduction paragraph 3

**Evidence**: Section 5.5 states "The PruSC paper [Kim et al., 2024] reports >95% cluster purity on CelebA using a related approach; our identical experimental configuration yields purity=0.456." The phrase "identical experimental configuration" is immediately followed by acknowledging "different configuration (post-convergence embeddings, k>2, different preprocessing)" — an internal contradiction. The comparison is between different methods and configurations, not a replication.

**Problem**: Presenting this as a near-replication failure ("our identical experimental configuration") while acknowledging the configurations differ is misleading. A reviewer will note this inconsistency and question the C4 framing. If the configurations differ, the comparison demonstrates configuration sensitivity, not a discrepancy with PruSC specifically.

**Required Fix**: Reframe Section 5.5 to explicitly acknowledge the comparison is cross-configuration. Suggested revision: "PruSC [Kim et al., 2024] reports >95% cluster purity on CelebA; our early-epoch (epoch-5), k=2 configuration yields purity=0.456. This gap reflects configuration sensitivity: the PruSC result is likely obtained under post-convergence, k>2 conditions. Published results at convergence should not be cited as evidence that early-epoch annotation-free detection is reliable on CelebA."

---

## Persuasiveness Assessment (Bored Reviewer)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Opens with concrete AMI contrast (0.762 vs 0.258), explains the mechanism, names a practical takeaway. No boilerplate motivation. |
| Problem clear in 1 min? | PASS | First paragraph of introduction re-states the contrast with enough context ("same algorithm, same model, same hyperparameters, no bug"). Second paragraph correctly escalates to practical stakes (silent failure). |
| Novelty clear in 2 min? | PARTIAL | "Feature-strength conditionality" is stated clearly by end of introduction. However, C1's "first" claim will make a reviewer pause — novelty is asserted, not demonstrated. A reviewer who knows GEORGE or DFR will mentally flag this. |
| Figure 1 self-explanatory? | PASS (conditional) | Described as bar chart with threshold lines and random baselines — appropriate and self-explanatory. However, figures are referenced as placeholder paths (not embedded), which will fail in actual submission rendering. |
| Would continue reading? | YES | The hook is effective and the empirical gap is genuine. Writing is economical and does not meander. |
| Attention lost at? | Section 5.5 / Contribution C3 | Section 5.5 introduces an unverified citation prominently. A reviewer who tries to locate the PruSC paper and fails will lose confidence. C3 in the contributions also raises an eyebrow — "diagnostic framework" for an unvalidated heuristic. |

---

## MINOR Issues (For Human Review)

**MINOR-001**: YAML frontmatter contains `hypothesis_id: "H-GSB-v1 (H-E1 sub-hypothesis)"` and `generated_by: "Anonymous Research Pipeline v2.0"` — internal pipeline metadata that must be removed before submission. (YAML frontmatter)

**MINOR-002**: The Appendix "Paper Statistics" block contains pipeline-internal metadata (word counts by section, `narrative_coherence` flags, pipeline_version). This entire appendix must be removed before submission. (Appendix)

**MINOR-003**: References section contains three explicit [UNVERIFIED] tags (Kim et al. 2024, Ghaznavi et al. 2023, Robinson et al. 2023). These internal metadata tags must be removed from the reference list before submission. (References)

**MINOR-004**: Section 6.3 Limitation L4 uses the phrase "was blocked by the CelebA gate failure" — pipeline-internal language opaque to readers. Rephrase to: "was not evaluated because the prerequisite CelebA detection condition was not satisfied." (Section 6.3)

**MINOR-005**: Section 3.3 table labels "Spurious attribute" for CelebA as "Biological sex" — this is the confounding variable, not the spurious attribute. The spurious attribute is hair color; biological sex is the spurious correlate. Table column value should be "Hair color (texture)" with a separate column or note for the confounding variable. (Section 3.3)

**MINOR-006**: Section 5.1 states "CelebA purity (0.456) is only 0.016 above the random baseline (0.440)." The actual values are 0.4557 and 0.4395, giving a gap of 0.0162. The text rounds both to 3dp but computes the difference from rounded values (0.456-0.440=0.016 vs actual 0.0162). Numerically inconsequential but technically should reference the unrounded gap or use consistent precision. (Section 5.1)

**MINOR-007**: Section 2.2 describes LFR as "Last-Layer Feature Reweighting" and Section 2.1 describes DFR as retraining "only the last linear layer." The method names are similar and may confuse readers unfamiliar with both. Adding a one-sentence distinguishing note (e.g., "unlike DFR which uses labeled group-balanced data, LFR...") would improve clarity. (Sections 2.1/2.2)

**MINOR-008**: The contribution list introduces C1-C4 in a specific order, but the contributions are not clearly mapped to sections in the body of the paper. Adding "(see Section X)" cross-references to each contribution bullet would improve navigability for a reviewer scanning the paper. (Section 1, contributions)

---

## Summary for Revision Agent

Priority fixes needed:

1. **[FATAL-001]** Revise the abstract sentence "Our results reveal a silent failure mode in downstream robustification pipelines" to clarify this is an inferred potential consequence, not an empirically validated result. GSB/H-M4 was never tested.

2. **[MAJOR-001]** Verify or remove the PruSC [Kim et al., 2024] citation. Provide DOI/URL if verified; soften C4 if not verifiable. Remove [UNVERIFIED] tag from reference once resolved.

3. **[MAJOR-002]** Either add a pretrained linear probe validation experiment (one small table) to support C3, or demote the pre-screen from the contribution list to Discussion as a proposed future diagnostic with explicit "unvalidated" labeling.

4. **[MAJOR-003]** Soften C1 to "to our knowledge, the first systematic characterization" and add 2-3 sentences to Section 2.4 explaining why prior work (GEORGE, DFR) does not fully address the clustering failure condition question.

5. **[MAJOR-004]** Reframe Section 5.5 to acknowledge the PruSC comparison is cross-configuration, not a direct replication. Remove the contradictory phrase "identical experimental configuration" from this context.

6. **[MINOR-001/002/003/004]** Strip all pipeline-internal metadata: YAML frontmatter fields, Appendix statistics block, [UNVERIFIED] tags in references, "gate failure" language in L4.

---

*Review completed: 2026-05-20 | Adversary Agent | Round 1*
