# Adversarial Review Round 2

**Paper**: "When Shortcuts Hide in Plain Sight: Feature-Strength Conditionality in Annotation-Free Spurious Direction Recovery"
**Review Date**: 2026-05-20
**Round**: R2 — Verification and Credibility
**Personas**: Accuracy Checker, Skeptical Expert
**Input**: 06_paper_r1.md (after R1 revisions)

---

## R1 Fix Verification

| Issue | Fix Applied | Adequate? | Notes |
|-------|-------------|-----------|-------|
| FATAL-001 (GSB overclaim in abstract) | Abstract revised to: "Our results characterize a detection failure mode that would constitute a silent failure in downstream annotation-free robustification pipelines if propagated — though the downstream mechanism itself is not empirically validated in this work." | YES | Clean fix. No residual GSB overclaim detected anywhere in abstract, body, or conclusion. Section 6.3 L4 also correctly states "was not evaluated because the prerequisite CelebA detection condition was not satisfied." |
| MAJOR-001 (PruSC unverified citation) | Paper now hedges: "reportedly >95% cluster purity" and "(exact configuration unconfirmed, as the paper could not be independently verified at time of writing)" | PARTIAL | Hedge language added appropriately in Introduction and Sections 5.5/6.1. However, the citation [Kim et al., 2024] remains in the reference list without DOI/URL, which leaves the unverified-citation risk intact. C4 contribution still depends on this claim. |
| MAJOR-002 (C3 pre-screen unvalidated) | C3 contribution revised to "motivate a proposed spurious feature salience pre-screen — a lightweight diagnostic... pending empirical validation of the specific threshold." Section 6.2 explicitly adds: "pending empirical calibration" and "Validating this diagnostic... is an important direction for future work." | YES | Appropriately demoted from experimental contribution to proposed diagnostic. No validation experiment was added, but the framing is now correctly scoped. |
| MAJOR-003 ("first systematic characterization" claim) | C1 changed to "to our knowledge, the first systematic characterization." Section 2.4 expanded with 2 sentences noting GEORGE and DFR's limitations. | YES | Adequate softening with appropriate hedging. Related Work now explicitly states what prior work does and does not cover. |
| MAJOR-004 (PruSC comparison framing) | Section 5.5 reframed: "This gap reflects configuration sensitivity rather than a simple discrepancy" and explicitly acknowledges "post-convergence, k>2 conditions that differ substantially from the early-epoch setting." | YES | Internal contradiction resolved. No longer claims "identical experimental configuration" while acknowledging configuration differences. |
| MINOR-001 (YAML frontmatter pipeline metadata) | Not observable in R1 (YAML header retained but no pipeline-internal fields beyond standard paper metadata present) | YES | Standard frontmatter only; internal fields not visible. |
| MINOR-002 (Appendix pipeline metadata) | No Appendix present in R1 | YES | Removed or was never in R1. |
| MINOR-003 ([UNVERIFIED] tags in references) | References do not show [UNVERIFIED] tags in R1 | YES | Cleaned from reference list. |
| MINOR-004 ("gate failure" language in L4) | L4 revised to "was not evaluated because the prerequisite CelebA detection condition was not satisfied" | YES | Pipeline-internal language removed. |
| MINOR-005 (CelebA spurious attribute column) | Table 3.3 now shows "Hair color (texture)" as spurious attribute and "Biological sex" as "Confounding variable" in a separate column | YES | Column structure corrected. |

---

## Round 2 Issues Found

### FATAL Issues

*No new FATAL issues identified.* The FATAL-001 fix is fully adequate. The abstract, introduction, conclusion, and Section 6.3 are mutually consistent: detection results are reported as detection results; downstream consequences are framed as logical inferences explicitly disclaimed from empirical validation. No residual overclaim was found.

---

### MAJOR Issues

#### MAJOR-R2-001: PruSC citation remains structurally unverifiable — C4 credibility gap persists

**Persona**: Skeptical Expert
**Location**: Introduction paragraph 3, Section 5.5, Contribution C4, References [Kim et al., 2024]
**Severity**: MAJOR

**Finding**: The R1 fix added hedge language ("reportedly," "exact configuration unconfirmed, as the paper could not be independently verified at time of writing") but did not resolve the underlying problem: the reference [Kim et al., 2024] still appears in the reference list without DOI, arXiv ID, or venue, making it unlocatable by any reviewer. The ground truth risk flag explicitly notes this paper was not found in Semantic Scholar. C4 ("Identification of configuration-sensitivity in published results") depends entirely on this citation.

**Attack vector**: A reviewer will attempt to locate "Kim et al. 2024 PruSC" and fail. The inline acknowledgment "paper could not be independently verified at time of writing" is unusual and will be flagged as a red flag — it is extremely rare to cite a paper in a submitted venue while disclosing you cannot verify it exists. This signals either a fabricated citation or a misremembered preprint, both of which invite rejection.

**Why R1 fix is insufficient**: Hedge language mitigates but does not eliminate the risk. A reviewer who cannot find the paper will not be satisfied by a hedge — they will recommend rejection pending citation clarification.

**Required Fix**:
- Option A (preferred): Identify the correct citation (correct authors/year/title) or find the arXiv preprint. Replace [Kim et al., 2024] with the verified reference.
- Option B: Remove the PruSC-specific citation entirely. Replace C4 framing with a configuration-sensitivity argument that does not depend on a specific unverified claim: "Published annotation-free clustering results are consistently reported at or near training convergence with k matching the number of known groups; none report early-epoch, k=2 results, creating an undisclosed configuration gap that makes published results appear more broadly applicable than they are." This is supportable from the Waterbirds/CelebA GEORGE and PruSC framing in the literature without requiring an unverified specific number.

---

#### MAJOR-R2-002: k=2 choice inadequately justified for CelebA's 4-group structure in main text

**Persona**: Skeptical Expert
**Location**: Section 3.2 (Step 3), Section 6.3 (L2), Section 3.4
**Severity**: MAJOR

**Finding**: The paper uses k=2 for CelebA, which has a 4-group spurious structure (binary label × binary spurious attribute). The paper acknowledges this in Limitation L2 ("CelebA has 4-group spurious structure (binary class × binary spurious attribute). k=2 collapses this, particularly harming the minority group (blonde male, ~1%)."). However, the main text methodology (Section 3.2) justifies k=2 only as: "k=2 matches the binary spurious attribute structure and follows published methodology (GEORGE, PruSC) for a fair comparison."

**Attack vector**: A reviewer will point out that the spurious attribute structure is binary (blonde/non-blonde) but the spurious *group* structure is 4-way. The k=2 choice may be inappropriate for detecting spurious *groups* (which is the task). Worse, the paper's core claim is that CelebA fails because of pretrained representation insufficiency — but it could alternatively fail because k=2 is simply the wrong choice for a 4-group dataset. The paper does not run k=4 to distinguish between these explanations.

**Why this is MAJOR**: The alternative explanation (k=2 is wrong for CelebA, not pretraining alignment) undermines the causal attribution of the failure to pretrained prior quality rather than clustering configuration. Limitation L2 names this issue but does not address whether the conclusion holds under k=4. This creates a confound that a thorough reviewer will exploit.

**Required Fix**: Add one or two sentences in Section 6.1 (Finding 1) or Section 6.3 (L2) explicitly acknowledging that the k=2 configuration may jointly contribute to CelebA's failure alongside pretraining alignment, and that a k=4 experiment would be needed to decouple these factors. The paper should not claim that pretraining alignment is the *sole* explanation without ruling out k=2 as a co-factor. The current limitation L2 is too brief and buried — it should be surfaced in the main findings discussion.

---

#### MAJOR-R2-003: Single-seed limitation scope is understated relative to claims made

**Persona**: Skeptical Expert
**Location**: Section 6.3 (L1), Abstract, Section 5.1
**Severity**: MAJOR

**Finding**: L1 ("Single random seed. Experiments use one seed (PoC mode). The Waterbirds gap above threshold (AMI +0.262) is large enough to likely be stable, but formal seed characterization (≥5 seeds) is absent.") acknowledges the limitation. However, the paper makes probabilistic stability claims — "large enough to *likely* be stable" — without any supporting analysis (e.g., sensitivity analysis to k-means initialization, t-SNE stability).

**Attack vector**: The paper reports k-means results with n_init=10, meaning the k-means objective is averaged over 10 initializations, providing some initialization robustness. However, the ERM training seed (weight initialization, data ordering) is a separate source of variance. A reviewer may ask: does epoch-5 ERM training on CelebA with different random seeds always produce low-AMI embeddings? Given CelebA's 162,770 training samples and only 5 epochs, representations may be stable — but this is not demonstrated. The claim "likely stable" is not scientifically rigorous and does not constitute validation.

**Why this is MAJOR**: The single-seed limitation is a standard weakness reviewers probe. The paper's core contribution (characterizing feature-strength conditionality) rests on two data points — one seed on each dataset. If CelebA AMI has high variance across seeds (possible given only 5 epochs and 162K samples), the characterization could be confounded.

**Required Fix**: Strengthen L1 to be specific about which aspects of the single-seed limitation are of concern (ERM training seed vs. k-means initialization seed vs. t-SNE seed). Note that k-means uses n_init=10 (providing initialization robustness) but ERM training seed is uncharacterized. Consider adding: "The k-means initialization variance is mitigated by n_init=10, but ERM training seed variance is uncharacterized. Given the magnitude of the Waterbirds gap, reversal is unlikely but not ruled out for CelebA, where the AMI (0.258) may have wider variance given the large dataset and short training horizon." This is more honest than "likely stable."

---

### Persuasiveness Check (R2)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract still compelling after R1 revisions? | PASS | The revised abstract maintains the core hook (AMI contrast) while correctly hedging the downstream inference. The added qualifier is slightly verbose but does not undercut the paper's appeal. |
| FATAL-001 fix weakens narrative? | NO | The revised sentence is scientifically more honest and does not significantly weaken the narrative; the finding (detection failure) is still clearly important without overclaiming downstream consequences. |
| C3 demotion weakens contributions? | MINOR | Moving from "contribution" to "proposed diagnostic" reduces the apparent contribution count but is more honest and less reviewer-attackable. The paper's empirical core (C1, C2, C4) remains intact. |
| "to our knowledge" hedging on C1 — adequate? | YES | Standard academic hedging. Does not undermine novelty claim; makes it defensible. |
| PruSC framing (MAJOR-R2-001) — does it damage persuasiveness? | YES | The inline disclosure "paper could not be independently verified at time of writing" is the single biggest persuasiveness risk remaining. A reader who notices this will question the paper's other citation practices. |
| Overall persuasiveness maintained? | PASS (conditional) | Core empirical story is intact and compelling. Conditional on resolving MAJOR-R2-001. |

---

### MINOR Issues (For Human Review)

**MINOR-R2-001**: Section 1 contributions list still reads "C3 — Mechanistic explanation and proposed diagnostic" but the content of C3 now describes "motivate a proposed spurious feature salience pre-screen... pending empirical validation." The contribution heading label "Mechanistic explanation and proposed diagnostic" is accurate, but the heading might be refined to "Mechanistic explanation and motivating diagnostic proposal" to signal the non-experimental status upfront without reading the full bullet.

**MINOR-R2-002**: Section 3.3 dataset table lists "High" vs. "Low" for ImageNet alignment without operationalizing what these categories mean quantitatively. A reviewer may ask what defines "high" vs. "low" alignment. Even a parenthetical "(no dedicated ImageNet category)" vs. "(dedicated scene-level category)" would improve precision.

**MINOR-R2-003**: Section 7 (Conclusion) mentions "Waterbirds-restricted validation of the downstream GSB mechanism where detection is confirmed reliable (addressing L4)" as a future direction. This is appropriate, but the mention of "GSB" without prior introduction in the main conclusion section may confuse readers who did not trace this back to Limitation L4. A brief parenthetical "(gradient-based shortcut balancing intervention)" would aid standalone readability.

**MINOR-R2-004**: The "threefold gap" phrasing appears in the Abstract ("a threefold gap") and Introduction ("a threefold gap"). Ground truth confirms 0.762/0.258 = 2.95x. The R1 paper is consistent in using "threefold" throughout. This is borderline — 2.95x does round to 3x, and "approximately threefold" would be more precise, but "threefold" is within standard approximation norms and is consistently stated across sections.

**MINOR-R2-005**: Section 5.3 describes Waterbirds cluster composition as "cluster 0 is ~89% water-background samples and cluster 1 is ~89% land-background samples." The ~89% figure corresponds to purity=0.892 (ground truth 0.8919). The per-cluster composition numbers are plausible but not explicitly tabulated — they are stated in prose. If the figures (Figure 5) are not embedded and reviewers cannot see them, this claim is unverifiable from the text alone. Consider adding a small composition table or at minimum reporting exact percentages.

---

## Convergence Assessment

- **FATAL remaining**: 0
- **MAJOR remaining**: 3 (MAJOR-R2-001: PruSC citation unresolvable; MAJOR-R2-002: k=2 causal confound; MAJOR-R2-003: single-seed scope understated)
- **Persuasiveness**: PASS (conditional on MAJOR-R2-001 resolution)
- **Recommendation**: CONTINUE_R3

### Rationale for CONTINUE_R3

The R1 fixes were well-executed and resolved all R1 FATAL and MAJOR issues adequately. No residual FATAL issues remain. However, three new MAJOR issues are identified:

1. MAJOR-R2-001 is the most critical: an unverifiable citation that the paper itself discloses it cannot confirm will attract negative reviewer attention regardless of the hedge language. This needs to be resolved by either verifying the citation or restructuring C4.

2. MAJOR-R2-002 (k=2 confound) is a genuine methodological weakness: the paper claims pretraining alignment is the key determinant of failure, but k=2 is a co-candidate explanation for CelebA failure that is not ruled out. The paper's causal claim is somewhat stronger than its evidence allows.

3. MAJOR-R2-003 (single-seed scope) is addressable with more precise limitation language rather than a new experiment.

These three MAJORs are all correctable without structural rewrites. A focused R3 revision addressing them — particularly MAJOR-R2-001 (resolve or restructure the PruSC citation) and MAJOR-R2-002 (add explicit confound acknowledgment in the findings) — should allow convergence at R3.

---

*Review completed: 2026-05-20 | Adversary Agent | Round 2*
