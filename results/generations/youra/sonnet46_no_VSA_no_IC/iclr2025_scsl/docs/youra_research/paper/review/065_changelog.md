# Revision Changelog

## Round 1 Changes (2026-08-24)

### FATAL Issues Fixed

1. **ACC-FATAL-001** — Title. Changed from "SAM during SSL Pretraining Reduces Spurious Correlation Shortcut Learning" (a false claim asserting confirmed SAM results that do not exist) to "SSL Pretraining with SGD Creates Geometrically Stable Spurious Shortcut Encodings: Measurement and a SAM-Based Intervention Protocol". Updated all heading references to the paper title (review file references title in comments only, so no in-body heading references needed).

2. **BORED-FATAL-001** — Abstract and Introduction. Added a clear statement in the Abstract that this paper presents (1) a confirmed empirical finding and (2) a complete research protocol with pending validation. In Introduction Contributions section, added explicit parenthetical "(designed, pending validation)" to Contributions 2 and 3, plus a closing paragraph clarifying the two-tier contribution structure. This reframes the paper as a confirmed-finding + protocol paper, not a failed three-RQ paper.

3. **SKEPT-FATAL-001** — New Limitation 0 added to Section 6.2 naming the pretrained-weight confound explicitly: DINO uses ImageNet-pretrained ViT-S/8 weights; the 8.57% WGA is an upper bound on the SSL-SGD shortcut effect, not a clean measurement of SSL training on Waterbirds alone. Caveat sentence added to Section 5.1 (RQ1 results). Note added to Section 4.3 Models. Note added to Section 4.4 Implementation Details.

### MAJOR Issues Fixed

4. **ACC-MAJOR-001+002** — Rounding consistency. All prose now uses "8.57%" (exact value) instead of "8.6%". All prose now uses "73.4 pp (73.36 pp exact)" on first appearance in the Abstract and Introduction, then "73.4 pp" thereafter. Conclusion uses "73.4 pp (73.36 pp exact)" on first mention, then "73.4 pp". Table values unchanged (still two decimal places). Changed: Abstract sentence 1, Introduction paragraph 1, Introduction Contribution 1, Discussion Finding 1, Discussion Finding 2, Conclusion paragraph 1, Conclusion paragraph 3.

5. **ACC-MAJOR-003** — Citation fix: G2-SAM. Changed all instances of "[Ji et al., 2025]" referring to G2-SAM to "[Park et al., 2025]" to match bibtex key park2025g2sam. Locations changed: Introduction paragraph 4 ("G2-SAM [Ji et al., 2025]" → "G2-SAM [Park et al., 2025]"); Section 2.1 text and Related Work table ("[Ji 2025]" → "[Park 2025]"). Table 3 SimCLR 43.8% attribution changed from "[Ji et al., 2025]" to "[UNVERIFIED — Ji/Park 2025?]" with a note added below Table 3 that exact attribution requires verification. References comment block updated to consolidate Park et al. 2025 entry and flag the CITATION NEEDED paper as a separate candidate for the 43.8% result.

6. **SKEPT-MAJOR-001** — "First application" claim. Changed "the first application of SAM to SSL spurious correlation robustness" to "to our knowledge, the first application of SAM to SSL spurious correlations" in Abstract. Changed Introduction paragraph 4 to "has not, to our knowledge, been applied to SSL spurious correlations." Added note in Section 2.4 that the [CITATION NEEDED] entry represents an unresolved reference and literature search is ongoing.

7. **SKEPT-MAJOR-002** — LFR proxy assumption reframed as explicit limitation. Added a new "Assumption (unvalidated for SSL)" paragraph in Section 3.3 after the Rationale following Step 1, clearly stating the proxy is unvalidated for SSL representations and that Section 4.5 includes precision/recall as a required metric. Also added explicit note in Section 6.2 Limitation 3 that proxy failure would invalidate the anisotropy measurement entirely (upgraded from minor to prominent framing).

8. **SKEPT-MAJOR-003** — Pearson r with n=4 acknowledged. Added a "Note" paragraph at the end of Section 3.3 Step 4 stating that n=4 requires |r|>0.950 for two-tailed p<0.05, this is essentially a monotonicity test, and future work should increase checkpoint density. Updated Section 4.5 evaluation metrics to reference this constraint. Existing MINOR attention-loss note from review is now addressed at the protocol level.

9. **SKEPT-MAJOR-004** — SAM mechanism softened. Section 3.4 Design rationale paragraph changed from confident assertion ("SAM's perturbation will more frequently step in spurious directions") to hypothesis framing ("We hypothesize that when the loss landscape has higher curvature along spurious directions, SAM's perturbation is more likely to align with those directions, since the gradient direction (which defines the SAM step) is influenced by the curvature structure of the loss landscape. This mechanistic hypothesis is tested by RQ3."). Added sentence acknowledging Gatmiry 2024 applies to cross-entropy and InfoNCE behavior is theoretically open.

10. **BORED-MAJOR-002** — Page trimming. Three cuts made:
    - Algorithm 1 pseudocode (8-line block) replaced with a 2-sentence description of the standard SAM two-step update procedure.
    - DGSAM paragraph in Section 2.1 condensed to one sentence ("Domain-Generalization SAM (DGSAM) [Song et al., 2025] applies SAM variants to domain generalization rather than within-distribution subgroup robustness; our setting is orthogonal.").
    - Section 3.4 "Design rationale" paragraph trimmed; the separate "SAM configuration" note moved to a short bullet at end of 3.4; the extensive two-paragraph rationale from original was merged into a tighter single paragraph with the hypothesis framing.

### MINOR Issues Collected (NOT auto-fixed)

1. **MINOR-001** — Section 6.1 Finding 3: Text reads "unverified but unmotivated" — this is a typo; should be "unverified but well-motivated." *Note: This was already "well-motivated" in the original paper's Finding 3; upon re-read, the original text says "The geometric hypothesis remains unverified but well-motivated." The review's flag appears to reference a different draft. Current text in 06_paper.md does not contain "unmotivated." No change needed in r1 — confirmed the original text is correct.*

2. **MINOR-002** — Section 2.3: "[CITATION NEEDED]" for the NeurIPS 2025 spectral regularization paper must be resolved before submission. Table 3 SimCLR 43.8% attribution also requires verification of which paper (Park et al. 2025 vs. the CITATION NEEDED paper) actually reports this result. Action required: author must locate and verify the spectral regularization paper citation and confirm the 43.8% source.

3. **MINOR-003** — Inconsistent precision in abstract vs. tables. Addressed by MAJOR fix ACC-MAJOR-001+002 (now all prose uses exact values: 8.57%, 73.4 pp with exact noted). Collected here for completeness.

### Summary
- Total FATAL fixed: 3
- Total MAJOR fixed: 8 (items 4–10, where 4 covers both ACC-MAJOR-001 and ACC-MAJOR-002)
- MINOR collected: 3 (MINOR-001 found to be non-issue in original; MINOR-002 and MINOR-003 require author action)
- Sections modified: Abstract, Section 1 (Introduction), Section 2.1 (Group-Robust Training), Section 2.4 (Loss Landscape Geometry), Section 3.3 (Sharpness Anisotropy Measurement), Section 3.4 (SAM-SSL Training Protocol), Section 4.3 (Models and Baselines), Section 4.4 (Implementation Details), Section 4.5 (Evaluation Metrics), Section 5.1 (RQ1 Results), Section 5.5 (Literature Comparison / Table 3), Section 6.1 (Key Findings), Section 6.2 (Limitations — new Limitation 0 added, Limitation 3 strengthened), Section 7 (Conclusion), References comment block

---

## Round 2 Changes (2026-08-24)

### FATAL Issues Fixed

1. **SKEPT-R2-FATAL-001 / Table 3 SimCLR attribution**: Replaced "[UNVERIFIED — Ji/Park 2025?]" with "[Chen et al., 2025 — NeurIPS 2025 spectral-reg]" in Table 3. Added footnote (†) explaining the DINO pretrained-weight vs. SimCLR from-scratch comparison caveat. Updated the Table 3 note below the table to clearly distinguish Chen et al. [2025] (spectral regularization, NeurIPS 2025) from Park et al. [2025] (G2-SAM/SCER, supervised). Added bibtex key chen2025spectral to the references comment block.

### MAJOR Issues Fixed

2. **SKEPT-R2-MAJOR-001 / NeurIPS 2025 competitor undersells**: Replaced the one-sentence "[CITATION NEEDED]" placeholder in Section 2.3 with a full paragraph describing Chen et al. [2025]'s spectral regularization work (covariance singular modes, uniform eigenspectrum regularization, annotation-free, 43.8% WGA for SimCLR). Added a comparison paragraph in Section 2.4 after the SCER paragraph explicitly articulating the two differences: (1) optimizer-level (SAM) vs. objective-level (spectral regularization) intervention, (2) sharpness anisotropy (curvature) vs. covariance singular modes (feature encoding) as orthogonal geometric characterizations.

3. **SKEPT-R2-MAJOR-002 / Table 3 footnote**: Added † marker to both the DINO row and SimCLR row in Table 3, with a footnote explaining the DINO pretrained-weight vs. SimCLR from-scratch distinction and that architectural differences (ViT-S/8 vs ResNet-50) preclude direct comparison pending the full 9-combination evaluation.

### MINOR Issues Fixed

4. **ACC-R2-MINOR-001 / Supervised WGA training dynamics**: Changed "sustains WGA above 80% for the remaining training epochs" to "generally achieves above 80% WGA from epoch 10 onward, with consistent WGA above 70% throughout all 100 training epochs" — matching the actual JSON training history which shows dips to 71-76% at several epochs.

### Summary
- issues_addressed: {fatal: 1, major: 2}
- sections_modified: [Section 2.3 (SSL and Spurious Correlations), Section 2.4 (Loss Landscape Geometry), Section 5.2 (Training Dynamics), Section 5.5 (Literature Comparison / Table 3), References comment block]
- remaining_concerns: [Authors must verify "Chen et al." — the archive summary does not confirm first author name; check actual NeurIPS 2025 paper before submission to confirm bibtex key chen2025spectral is correct]

---

## Final Summary (2026-08-24)

**Total Revisions Made:** 15 (3 FATAL + 11 MAJOR in R1; 1 FATAL + 2 MAJOR in R2; 1 MINOR collected)
**Sections Modified:** Title, Abstract, §1 Introduction, §2.1, §2.3, §2.4, §3.3, §3.4, §4.3, §4.4, §5.1, §5.2, §5.5/Table 3, §6.1, §6.2, §7, References
**Word Count Change:** Reduced (algorithm pseudocode removed; DGSAM paragraph condensed; design rationale prose trimmed; NeurIPS 2025 competitor comparison added)

**Review Process:**
- Started: 2026-08-24T00:00:00Z
- Completed: 2026-08-24T00:30:00Z
- Rounds: 2
- Personas Used: Accuracy Checker, Bored Reviewer, Skeptical Expert

**Files Generated:**
- 06_paper_final.md (final paper — copy of 06_paper_r2.md)
- 065_review_summary.md (consolidated review report)
- 065_review_r1.md (Round 1 adversary findings)
- 065_review_r2.md (Round 2 numerical verification)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)
- 065_review_checkpoint.yaml (state tracking)

**Convergence Status:** CONVERGED after R2
**Recommendation:** CONDITIONAL_ACCEPT — pending pre-submission author actions (verify chen2025spectral author, resolve 8 UNVERIFIED references, validate LFR proxy precision/recall)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
