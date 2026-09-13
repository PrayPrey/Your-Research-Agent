# Phase 6.5 Adversarial Review — Round 1
**Paper:** Gradient Norms as Label-Free Minority Proxies: Confirming the Prediction-Residual Signal for Spurious Correlation Robustness
**Date:** 2026-03-16
**Round:** R1 — Accuracy and Engagement
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Executive Summary

| Category | Count |
|----------|-------|
| FATAL issues | 2 |
| MAJOR issues | 6 |
| MINOR issues (human review) | 7 |
| Persuasiveness passed | false |
| Would continue reading | true (conditionally) |
| Attention lost at | Section 6.1 / Discussion |

**Overall Recommendation:** MAJOR_REVISION

The paper presents real, internally consistent experimental results with a genuinely interesting signal (AUC=0.914). However, it contains two FATAL accuracy violations: (1) it claims temporal persistence "ratio 6.5x–8.8x" in the abstract/intro contributions, but Table 2 shows epoch 1 ratio=6.513 and epoch 10=8.509 — both correct individually — yet the contribution statement implies a continuous range that mildly misrepresents the trajectory; more critically (2) the paper as a whole has a fundamental scope mismatch: it proposes "GNR-LLR" as a two-stage method in the title and introduction but only executes Stage 1, and then frames incomplete execution as a deliberate preliminary study rather than a limitation of equal standing with the contribution claims. The DFR analogy in particular (Section 2.2, Section 3.4) creates a strong implied claim about WGA that is not and cannot be substantiated by the data presented. The paper also cites NHT [Khanh & Hoa, 2026] as a theoretical grounding while acknowledging it is UNVERIFIED — this is a critical credibility risk.

---

## Ground Truth Verification Log

| Claim in Paper | Location | Ground Truth | Match? | Severity |
|---------------|----------|--------------|--------|----------|
| AUC = 0.914 at T_id=5 | Abstract, Intro, Results | AUC = 0.914 — PASS | MATCH | OK |
| ratio = 8.805 at T_id=5 | Table main results | ratio = 8.805 — PASS | MATCH | OK |
| ratio = 8.509 at T_id=10 | Table 2 | ratio = 8.509 — PASS | MATCH | OK |
| ratio ≥ 1.2x at T_id=10 (target) | Section 4.3 | Verified pass | MATCH | OK |
| h_norm_std_ratio ≈ 0.10 | Abstract, Table 3 | ≈ 0.10 — PASS | MATCH | OK |
| balance_deviation = 0.379 vs ≤0.10 target | Table main results | 0.379 — FAIL (by design) | MATCH | OK (disclosed) |
| Stage 2 LLR executed | Section 3.4, implied throughout | NOT EXECUTED | MISMATCH | FATAL |
| DFR achieves 92.9% WGA | Section 2.2, 6.2 | UNVERIFIED external claim | UNVERIFIED | MAJOR |
| JTT +21pp WGA on Waterbirds | Section 2.2 | UNVERIFIED external claim | UNVERIFIED | MAJOR |
| JTT "estimated AUC ≈ 0.70–0.80" | Section 5.1, Key Obs. 1 | No citation, estimative only | UNSUPPORTED | MAJOR |
| NHT [Khanh & Hoa, 2026] as theory grounding | Sections 2.3, 3.5, 6.1, 6.3 | UNVERIFIED — paper may not exist | UNVERIFIED | FATAL |
| GEORGE [Zhang et al., 2022] | Section 2.3 | UNVERIFIED | UNVERIFIED | MAJOR |
| Rosenfeld & Risteski 2023 | References | UNVERIFIED (wrong title possible) | UNVERIFIED | MINOR |
| Ghaznavi et al. 2023 | References | UNVERIFIED | UNVERIFIED | MINOR |
| Nam et al. 2020 LfF | Section 2.2 | UNVERIFIED | UNVERIFIED | MAJOR |
| Ratio range "6.5x–8.8x" in contributions | Section 1 Contribution 1 | epoch 1=6.513, epoch 5=8.805, epoch 10=8.509; range is accurate | MATCH | OK |
| "5 seeds" or multi-seed results | Nowhere claimed | Only seed=42 used | N/A (not claimed) | OK |
| Phase 5 baseline comparison done | Nowhere claimed | Skipped by config | N/A (not claimed) | OK |
| GNR-LLR framed as complete method | Title, Abstract, Section 3.4 | Only Stage 1 executed | MISMATCH (framing) | FATAL |

---

## PERSONA 1: ACCURACY CHECKER FINDINGS

### FATAL-1: Stage 2 Not Executed — Method Framed as Complete

**Location:** Title ("Gradient Norms as Label-Free Minority Proxies"), Abstract (last sentence: "providing a strong foundation for gradient-norm-informed last-layer retraining toward group-robust models"), Section 1 ("we propose GNR-LLR... which uses the normalized per-sample gradient norm... for constructing a pseudo-balanced subset. GNR-LLR consists of two stages"), Section 3.4 (full Stage 2 specification), Section 3.5 (connection to NHT), Section 6.2 Limitation 1.

**Ground Truth:** Stage 2 (LLR) was NOT EXECUTED. No WGA measurements exist.

**The problem:** The paper proposes "GNR-LLR" as the full method (Title, Introduction), specifies Stage 2 in detail (Section 3.4: "Freeze feature extractor; retrain model.fc on S, SGD lr=0.01, 100 epochs → Evaluate WGA"), then discloses in Limitation 1 that Stage 2 was not run. This structure — naming a two-stage method after both stages, specifying Stage 2 hyperparameters, drawing DFR analogies implying WGA competitiveness, then footnoting non-execution — constitutes a fundamental framing mismatch. A reviewer reading the title and abstract would reasonably expect WGA results.

**Required Fix:** Either (a) rename the paper to focus on the proxy signal only (e.g., "Gradient Norms as Label-Free Minority Proxies: A Mechanistic Study"), strip all GNR-LLR two-stage framing from abstract and introduction, and re-scope contributions as a proxy-signal study; or (b) execute Stage 2 and report WGA before submission.

**Severity:** FATAL — the paper's title, abstract, and introduction systematically overpromise relative to the results.

---

### FATAL-2: NHT [Khanh & Hoa, 2026] Used as Theoretical Grounding — Unverified Citation

**Location:** Section 2.3 ("Norm Hierarchy Theory (NHT) [Khanh & Hoa, 2026] predicts that minority samples resist the shortcut attractor basin..."), Section 3.5 ("g̃ᵢ directly captures the prediction-residual that NHT [Khanh & Hoa, 2026] predicts will remain elevated"), Section 6.1 Finding 3 ("qualitatively consistent with NHT predictions"), References ([UNVERIFIED — preprint cited in Phase 2A/2B]).

**Ground Truth:** NHT [Khanh & Hoa, 2026] is explicitly marked UNVERIFIED in both 065_ground_truth.yaml and in the paper's own reference list. It is cited as a 2026 preprint. The paper cannot verify the citation, the title, or whether the paper exists.

**The problem:** The paper uses NHT as its primary theoretical support in four locations, framing empirical results as "consistent with NHT predictions." If NHT does not exist or has different content, this invalidates all claims of theoretical grounding. At minimum, a reviewer will check this citation. An [UNVERIFIED] tag appearing in the paper's own reference list is an extraordinary and disqualifying editorial error.

**Required Fix:** Remove ALL citations to NHT [Khanh & Hoa, 2026] from the manuscript body. The [UNVERIFIED] tag must never appear in a submitted reference list. If the theoretical prediction is independently derivable from the outer-product decomposition + ERM dynamics, present it as the paper's own analysis, not as external citation support. References marked [UNVERIFIED] in the reference list (Nam, GEORGE, Rosenfeld & Risteski, Ghaznavi et al.) must all be verified or removed before submission.

**Severity:** FATAL — submitting a paper with [UNVERIFIED] in the reference list is an immediate desk-reject trigger.

---

### MAJOR-1: JTT AUC Comparison Without Citation or Methodology

**Location:** Section 5.1, Key Observation 1: "This substantially exceeds both the 0.70 threshold and the estimated AUC ≈ 0.70–0.80 of JTT's binary misclassification signal on Waterbirds."

**Ground Truth:** No source for "estimated AUC ≈ 0.70–0.80" of JTT exists in the verified results. This is an estimative claim made without any citation, experimental measurement, or stated basis.

**The problem:** The paper's headline comparison ("substantially exceeds... JTT's binary misclassification signal") is unsubstantiated. JTT uses a binary signal — AUC of a binary classifier is not directly reported in the JTT paper. This comparison may be computed from first principles (a binary signal has AUC = its accuracy on balanced classes), but no derivation or citation is given. A reviewer will immediately ask: where does "estimated AUC ≈ 0.70–0.80" come from?

**Required Fix:** Either (a) provide explicit derivation: "JTT's binary misclassification proxy has AUC bounded by its classification accuracy; on Waterbirds with [X]% minority fraction, a [Y]% error rate yields AUC ≤ Z" — cite Liu et al. for specific numbers; or (b) remove the JTT AUC comparison entirely and only compare on WGA (which requires executing Stage 2). Do not present an unsubstantiated numerical estimate as a comparison point.

**Severity:** MAJOR — this is the paper's primary performance comparison claim.

---

### MAJOR-2: DFR WGA Comparison Without Stage 2 Results

**Location:** Section 2.2 ("DFR... achieving 92.9% WGA on Waterbirds"), Section 3.4 ("analogous to DFR... but without requiring group annotations"), Section 6.2 ("DFR demonstrates that oracle balanced subsets achieve 92.9% WGA on Waterbirds; our signal quality motivates the expectation of competitive WGA").

**Ground Truth:** Stage 2 was NOT executed. The paper has no WGA results. "Expectation of competitive WGA" is not a result.

**The problem:** Repeatedly invoking DFR's 92.9% WGA while having no WGA measurement creates a false equivalence impression. The phrase "motivates the expectation" is an opinion, not evidence. A reviewer who reads "analogous to DFR" will expect WGA results. Additionally, the DFR 92.9% figure is UNVERIFIED — it is a cited external claim not confirmed in this pipeline.

**Required Fix:** Remove all DFR WGA comparisons from the paper body. If the DFR analogy is retained for motivation, explicitly flag that no WGA comparison is made in this paper.

**Severity:** MAJOR — creates overclaim impression without supporting data.

---

### MAJOR-3: Multiple Unverified Citations Used as Evidence

**Location:** Section 2.2 (JTT "+21pp WGA"), Section 2.2 (DFR "92.9% WGA"), Section 2.2 (LfF [Nam et al., 2020] [UNVERIFIED]), Section 2.3 (GEORGE [Zhang et al., 2022] [UNVERIFIED]).

**Ground Truth:** All four of these citations are flagged as UNVERIFIED in ground truth. The [UNVERIFIED] flag appears in the reference list itself for Nam et al. and GEORGE.

**Required Fix:** Verify all cited numerical results (JTT +21pp, DFR 92.9%) against actual published papers before submission. Remove [UNVERIFIED] tags from references entirely — verify or delete. LfF, GEORGE, Rosenfeld & Risteski, Ghaznavi et al. must be confirmed to exist with the stated titles and results.

**Severity:** MAJOR — a submitted paper cannot have unverified citations. This is a pre-submission task, not a revision request.

---

### MAJOR-4: h-e1-v2 "Direct Minority Recall" Deferred Without Acknowledgment of Current Gap

**Location:** Section 5.2 ("Direct minority recall measurement is addressed in h-e1-v2"), Section 6.2 Limitation 3 ("Direct recall measurement is pending (h-e1-v2)"), Section 7 ("h-e1-v2 with minority recall criterion").

**Ground Truth:** Minority recall of the top-25% subset was not directly measured. The paper acknowledges this but frames it as a deliberate next step while simultaneously claiming the top-25% is "strongly minority-enriched" (Section 5.2, Figure 4 claim).

**The problem:** The paper makes a direct claim about subset quality ("strongly minority-enriched", "G1 and G2 are substantially overrepresented") without quantifying it. The visual Figure 4 claim is presented as confirmed, but the actual minority recall (what fraction of the 240 minority samples appear in the top-1199?) is not stated. This is a measurable quantity from existing data — it is not pending future experiments.

**Required Fix:** Compute and report minority recall of the top-25% subset from existing epoch-5 gradient norm data. This is a single line of code from already-computed results. The claim "strongly minority-enriched" must be backed by a number (e.g., "minority recall = X.XX in top-25% subset vs. 5% baseline").

**Severity:** MAJOR — the paper's central application claim (subset enrichment) is stated without the key quantitative metric that would confirm it.

---

## PERSONA 2: BORED REVIEWER FINDINGS

### Overall Engagement Assessment

**Would I continue reading after the abstract?** Yes — barely. The AUC=0.914 number is arresting, and the outer-product decomposition story is legitimately elegant. However, the abstract ends with a hedged forward-looking sentence ("providing a strong foundation for... toward group-robust models without annotation costs") that signals the paper does not close the loop. A NeurIPS reviewer with limited time will immediately sense the paper is proposing without delivering.

**Is the problem clear in 1 minute?** Yes. The minority group / spurious correlation problem is efficiently set up. The gradient norm idea is stated clearly. The paper is well-written in its problem framing.

**Is the novelty clear in 2 minutes?** Partially. The outer-product decomposition story is clear and novel. But the reader will ask: "So what's the WGA?" — and the paper never answers this. By the time this becomes apparent (end of abstract or Section 3.4), engagement drops.

**Can you understand Figure 1 from the description alone?** Yes — the description in Appendix A.Figure 1 is clear: three bars against three targets. The balance deviation bar failing is clearly labeled as a design mismatch. This is well-handled.

**At what point did I lose attention?** At Section 6.1 / Discussion. The "Finding 1" repeats what was already in Section 5. "Finding 2" (balance criterion was wrong) is fine but reads defensively — "the criterion was wrong" feels like post-hoc rationalization even if technically correct. By Section 6.3, the paper is adding general comments about broader impact that feel aspirational rather than grounded.

**Persuasiveness of the core claim:** The AUC=0.914 result is genuinely strong. The outer-product decomposition is theoretically clean. If the paper were scoped as "we confirm gradient norms are an excellent minority proxy signal and here is why mechanistically," it would be a solid short paper. The problem is the paper keeps hinting at WGA implications it cannot deliver.

**Does the paper oversell incomplete results?** Yes, in three places:
1. The title includes "GNR-LLR" which implies a complete retraining method.
2. Key Observation 1 compares against JTT AUC without a citation or derivation.
3. Section 6.2 Limitation 1 "motivates the expectation of competitive WGA" is opinion dressed as conclusion.

**Structural clarity:** The paper is well-structured. The RQ framework (RQ1–RQ4) maps cleanly to results. Tables 1–3 are readable. The limitation section is unusually transparent for a submitted paper (this is a positive signal).

**Attention loss timeline:**
- Abstract: Engaged (strong number, clear signal)
- Introduction: Engaged (decomposition story is clean)
- Related Work: Engaged but skeptical (NHT citation from 2026 feels self-referential)
- Methodology: Engaged (Algorithm 1 is clean)
- Results: Engaged (Table 2 is informative; Section 5.2 handles the failure gracefully)
- Discussion: Losing interest (repetitive, aspirational)
- Conclusion: Disengaged (adds nothing new)

---

## PERSONA 3: SKEPTICAL EXPERT FINDINGS

### 3.1 Novelty Assessment: "First to Use Gradient Norms as Minority Proxy"

**Claim:** "No existing work in this paradigm uses per-sample gradient norms as the minority identification signal." (Section 2.2)

**Analysis:** This claim requires a thorough literature search that the paper has not documented. Several adjacent works are relevant:

- **Loss-based signals** (JTT, LfF, DFR) all use per-sample scalar quantities from training dynamics. The step from "loss value" to "gradient norm" is conceptually small — the loss IS the gradient norm's numerator when the denominator (feature norm) is constant. The paper's contribution is the normalization step + mechanistic decomposition, not the general idea of using training dynamics.
- **Influence functions** [Koh & Liang, 2017] use gradient inner products as per-sample signals. While not specifically for minority proxy identification, gradient-norm-adjacent signals have been used for data attribution.
- **EL2N score** [Paul et al., 2021] uses the expected L2-norm of error vectors (which is essentially ‖pᵢ − yᵢ‖) for data pruning — directly related to g̃ᵢ. The paper does not cite or discuss EL2N.
- **Forgetting events** [Toneva et al., 2019] track per-sample training dynamics. Not cited.

**Assessment:** The specific claim of gradient NORM (normalized by feature norm) for minority proxy identification at a specific training checkpoint may be novel. But the paper should cite EL2N and data pruning work using gradient-adjacent signals, and explicitly distinguish g̃ from these. The current related work section is incomplete. A reviewer familiar with data-centric AI will immediately raise EL2N.

**Recommendation:** Add a subsection on data-centric methods (EL2N, forgetting events, influence functions) and explicitly compare g̃ to EL2N = ‖pᵢ − yᵢ‖ (same quantity, different use case).

**Severity:** MAJOR — novelty claim may not survive reviewer scrutiny without this discussion.

---

### 3.2 Baseline Fairness

**JTT Comparison:** The comparison to JTT is unfair in its current form. JTT's "binary misclassification signal" has known limitations but achieves +21pp WGA — a concrete downstream result. This paper achieves AUC=0.914 as a proxy quality metric — a different level of the pipeline. Comparing AUC of g̃ against "estimated AUC of JTT" is an apples-to-oranges comparison. The fair comparison would be WGA(GNR-LLR) vs. WGA(JTT).

**DFR Comparison:** Similarly, invoking DFR's 92.9% WGA while having no WGA number is not a comparison — it is an aspiration. The paper partially acknowledges this (Limitation 1) but continues to invoke the DFR analogy throughout.

**What the paper COULD do:** Report AUC(g̃) vs. AUC(misclassification flag from JTT's error set E). This is a fair apples-to-apples proxy quality comparison that could be computed from existing data without Stage 2.

---

### 3.3 Overclaims

1. **Title overclaim:** "GNR-LLR" implies a complete two-stage method. Stage 2 was not run. The title should reflect what was done: signal measurement and mechanistic validation.

2. **Abstract last sentence:** "providing a strong foundation for gradient-norm-informed last-layer retraining toward group-robust models without annotation costs" — this is a forward-looking claim dressed as a result. A submitted paper's abstract should state what was achieved, not what might be achieved.

3. **Section 3.4 Stage 2 specification:** Providing full hyperparameters (SGD, lr=0.01, 100 epochs) for an experiment that was not run creates a false impression of completeness. These parameters are not validated; they are aspirational.

4. **"First experimental confirmation"** (Conclusion): The paper claims this is "first experimental confirmation of gradient norms as a minority proxy signal." This needs support — specifically, confirmation that EL2N and other gradient-adjacent proxy work does not accomplish the same thing.

---

### 3.4 Missing Limitations

The limitation section is unusually honest but still missing:

1. **Single architecture:** Only ResNet-50 with BatchNorm. The whole normalization argument depends on BatchNorm feature equalization. For architectures without BatchNorm (e.g., ViT with LayerNorm, or early convolutional networks), the normalization step may not be valid. This is not mentioned.

2. **ERM training instability:** With only seed=42, there is no evidence that the AUC=0.914 result is not a lucky seed. The paper should acknowledge that multi-seed validation is needed (h-m4 was not run per ground truth).

3. **k=0.25 sensitivity:** The paper states k=0.25 is the "primary configuration" but Table 2 shows only epoch sensitivity, not k sensitivity. How sensitive are results to k?

4. **NHT theoretical grounding:** The entire theoretical framing depends on NHT [Khanh & Hoa, 2026] — an unverified, self-cited 2026 preprint. If NHT is the paper's own prior work, this needs to be disclosed. If it does not exist, the theoretical section collapses.

5. **g̃ ≡ EL2N:** The paper does not acknowledge that g̃ᵢ = ‖pᵢ − yᵢ‖ is identical to the EL2N score (Paul et al., 2021, "Deep Learning on a Data Diet"). If EL2N has already been applied to minority identification in any published work, the novelty claim is undermined.

---

### 3.5 The "Criterion Design Lesson" Presentation

Section 5.2 and Finding 2 present the balance_deviation failure as a "criterion design insight." This framing is appropriate — the mathematical argument is correct (50% class balance is impossible given 5% minority prevalence). However:

- The paper presents this as a "lesson" discovered during the study. A skeptical reviewer will note this looks like post-hoc rationalization of a failed criterion.
- The correct presentation is: "we initially used balance_deviation as a success criterion, discovered it was inapplicable, and replaced it with AUC and ratio metrics. The AUC=0.914 and ratio=8.8x results use the corrected metrics." This is more transparent.
- The paper should explicitly state what the minority recall of the top-25% is (see MAJOR-4) to substantiate the claim that the criterion change was justified, not just convenient.

---

### 3.6 Accept/Reject Recommendation

**Current state:** REJECT (with invitation to revise)

**Rationale:** The paper has genuinely interesting results (AUC=0.914, clear mechanistic story) but cannot be submitted in current form due to (1) FATAL framing mismatch between two-stage method proposal and single-stage execution, (2) FATAL unverified citation appearing in the reference list, (3) incomplete related work missing EL2N and data-centric AI literature. With these issues addressed, the core contribution is publishable as a workshop paper or short paper focusing on the proxy signal quality result.

---

## MINOR Issues (Human Review Notes)

Do NOT auto-fix these. Collect for human review only.

1. **MINOR-1 (Grammar/Style):** Section 1 contribution 1: "ratio 6.5x–8.8x" — inconsistent with Table 2 which shows epoch-1 as 6.513 and epoch-5 as 8.805. The range notation implies monotone increase; should clarify epoch 10 = 8.509 is also within range but slightly below peak.

2. **MINOR-2 (Formatting):** Reference for Kirichenko et al. [2022] lists venue as "ICLR 2023" but is cited as "[Kirichenko et al., 2022]." The year in the citation key should match either the preprint year or publication year consistently.

3. **MINOR-3 (Clarity):** Section 3.3 calls the subset "pseudo-balanced" but immediately acknowledges it is not balanced. "Minority-enriched subset" or "pseudo-minority-enriched subset" would be more accurate.

4. **MINOR-4 (Style):** "The signal was always there — in the gradient norms of every training run" (Conclusion) — this is colloquial for an academic paper. May be appropriate for a blog post but flags as informal to some reviewers.

5. **MINOR-5 (Terminology):** "criterion design flaw" in Contribution 4 and "criterion design lesson" in Section 6.2 use different labels for the same concept. Standardize to one term.

6. **MINOR-6 (Appendix):** Appendix C lists "PyTorch 2.10+cu128" — this appears to be a future PyTorch version (current as of 2026-03-16 may differ). Verify the actual version used.

7. **MINOR-7 (Meta):** The paper's YAML header contains `generated_by: "Anonymous Research Pipeline v2.0 — Phase 6"` and the footer reads `Generated by Anonymous Research Pipeline v2.0`. These pipeline attribution markers must be removed before submission to any venue.

---

## Summary for Revision Agent

**PRIORITIZED FIX LIST — execute FATAL first, then MAJOR**

### FATAL Fixes (Block submission until resolved)

**[FATAL-1] Rescope paper away from two-stage method framing**
- Change title: remove "GNR-LLR" or subtitle to "Confirming the Proxy Signal"
- Rewrite abstract: remove all Stage 2 / WGA implication language
- Rewrite Introduction contributions: replace "we propose GNR-LLR (two stages)" with "we confirm the Stage 1 proxy signal; Stage 2 execution is future work"
- Section 3.4: demote to "Proposed Pipeline (Not Evaluated)" or move to Discussion as future work
- Section 6.2 Limitation 1: make this limitation as prominent as the contributions, not a footnote

**[FATAL-2] Remove all unverified citations from the manuscript**
- Remove NHT [Khanh & Hoa, 2026] from ALL locations in manuscript body (Sections 2.3, 3.5, 6.1, 6.3)
- Remove [UNVERIFIED] tags from reference list — either verify the citation or delete it entirely
- Verify Nam et al. 2020, GEORGE Zhang et al. 2022, Rosenfeld & Risteski 2023, Ghaznavi et al. 2023 via Semantic Scholar before re-adding
- Replace NHT theoretical grounding with self-contained analysis based on outer-product decomposition + ERM dynamics

### MAJOR Fixes (Required before submission)

**[MAJOR-1] Fix or remove JTT AUC comparison**
- Either derive AUC(JTT misclassification) formally with citation, or remove comparison
- Alternative: compute AUC(top-k% by ERM misclassification) from existing data and compare directly

**[MAJOR-2] Remove DFR WGA comparisons**
- Delete "our signal quality motivates the expectation of competitive WGA"
- Retain DFR as motivation for Stage 2 design, but remove all implied WGA equivalence

**[MAJOR-3] Verify all cited numerical results**
- Confirm DFR 92.9% WGA and JTT +21pp WGA against actual published papers
- Confirm LfF, GEORGE descriptions are accurate

**[MAJOR-4] Add direct minority recall measurement**
- From existing epoch-5 g̃ data, compute: |{top-25%} ∩ {G1 ∪ G2}| / |G1 ∪ G2|
- Report as a new metric in Table main results
- This is a single computation from existing data

**[MAJOR-5] Add EL2N and data-centric AI related work**
- Add Section 2.X: "Data-Centric Training Signals"
- Compare g̃ = ‖pᵢ − yᵢ‖ explicitly to EL2N score (Paul et al., 2021)
- Distinguish: EL2N is used for data pruning/coreset selection; g̃ is used for minority group identification — different downstream use, potentially different distribution properties

**[MAJOR-6] Add single-seed limitation**
- Explicitly state: "All results use a single random seed (42). Multi-seed validation is future work (h-m4)."
- Add to Appendix C reproducibility checklist: "Note: single seed only; multi-seed replication pending"

---

*Review generated by Adversarial Agent — Phase 6.5 Round 1*
*Paper: 06_paper.md | Date: 2026-03-16*
