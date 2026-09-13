# Adversarial Review — Round 1
**Paper:** SAM during SSL Pretraining Reduces Spurious Correlation Shortcut Learning
**Round:** R1 — Accuracy and Engagement
**Date:** 2026-08-24

---

## Ground Truth Summary

| Metric | Ground Truth Value | Notes |
|--------|-------------------|-------|
| DINO SSL test WGA | 8.57% (0.0857) | |
| DINO SSL test avg acc | 62.10% (0.6210) | |
| Supervised ViT-S test WGA | 81.93% (0.8193) | |
| Supervised ViT-S test avg acc | 94.74% (0.9474) | |
| WGA gap | 73.36 pp | |
| DINO best val WGA | 24.1% at epoch ~17 | stagnates 0–24% throughout |
| Supervised val WGA | >70% by epoch 2; >80% epochs 2–100 | |
| Per-group DINO: waterbird_water | 97.25% | |
| Per-group DINO: waterbird_land | 8.57% | (this is also the WGA) |
| Per-group DINO: landbird_water | 36.54% | |
| Per-group DINO: landbird_land | 81.93% | |
| Per-group Supervised: waterbird_water | 99.82% | |
| Per-group Supervised: waterbird_land | 81.93% | |
| Per-group Supervised: landbird_water | 92.42% | |
| Per-group Supervised: landbird_land | 97.82% | |
| RQ2 anisotropy | PENDING | 200-epoch SimCLR run ongoing |
| RQ3 SAM-SSL | PENDING | |
| ICML page estimate | ~8.5 pp | over 8pp limit |

---

## Executive Summary

| Persona | FATAL | MAJOR | MINOR |
|---------|-------|-------|-------|
| Accuracy Checker | 1 | 3 | 2 |
| Bored Reviewer | 1 | 2 | 1 |
| Skeptical Expert | 1 | 4 | 0 |
| **Total** | **3** | **9** | **3** |

**Overall Recommendation: MAJOR REVISION REQUIRED — NOT READY FOR SUBMISSION**

The paper has one genuinely strong confirmed result (the 73.4 pp WGA gap) but submits to a top venue with two of its three research questions entirely unanswered. The fatal issues are: (1) the title claims SAM reduces shortcut learning but no SAM result exists yet; (2) DINO uses pretrained ImageNet weights while the SimCLR baseline in Table 3 is trained from scratch — a comparison that is potentially misleading and unacknowledged; (3) one citation is internally inconsistent. These must be fixed before submission.

---

## Persona 1: Accuracy Checker Findings

### FATAL Issues

**ACC-FATAL-001: Title is a false claim**
The paper title states "SAM during SSL Pretraining Reduces Spurious Correlation Shortcut Learning." No SAM result exists. RQ3 is explicitly "Planned" and all SAM-SSL numbers are pending. The title asserts a confirmed causal finding that is entirely absent from the paper. A reviewer who reads the title, reads the abstract (which correctly flags pending results), and then reads the title again will note the direct contradiction. The title must change to reflect what is actually confirmed.

Severity: FATAL — the title is verifiably false against the paper's own content.

### MAJOR Issues

**ACC-MAJOR-001: "8.6%" rounding used inconsistently across sections**
The ground truth WGA is 8.57%. The paper uses both "8.57%" (Table 1, Table 2) and "8.6%" (Abstract first sentence, Introduction first sentence, Discussion section 6.1 Finding 2, Conclusion first and third paragraphs) without explanation. This is not a rounding error per se — 8.6% is a valid 1-decimal rounding — but it creates cross-section inconsistency that a careful reviewer will flag. Either round consistently throughout or always state the precise value and note rounding where used.

**ACC-MAJOR-002: "73.4 pp" vs "73.36 pp" inconsistency**
The ground truth WGA gap is 73.36 pp. The abstract, introduction, discussion, and conclusion all state "73.4 pp," while Table 1 states "73.36 pp." This is internally inconsistent. The table is exact; the prose rounds to one decimal. Use consistent rounding or state "73.4 pp (73.36 pp exact)" on first mention.

**ACC-MAJOR-003: Citation inconsistency — G2-SAM attribution**
Introduction paragraph 4 cites "G2-SAM [Ji et al., 2025]." Related Work Table (Section 2) also cites "[Ji 2025]." But ground truth flags that the bibtex key is "park2025g2sam" and Table 3 attributes "SimCLR 43.8%" to "[Ji et al., 2025]." If the bibtex key is park2025g2sam, the author name should be Park et al., not Ji et al. This is an unresolved citation inconsistency. Additionally, Table 3 attributes the SimCLR 43.8% WGA number to "[NeurIPS 2025]" in text but the ground truth flags it as possibly wrongly attributed to Ji/Park 2025. This must be resolved — verify which paper actually reports the 43.8% SimCLR result and correct the attribution.

### Verification Log

- Abstract: "73.4 pp" gap, "8.6%", "81.9%" — 8.6% rounds correctly from 8.57%; 81.9% rounds correctly from 81.93%; 73.4 pp rounds correctly from 73.36 pp. Values are correct but inconsistently precise vs. tables.
- Table 1: WGA 8.57%, 81.93%, gap 73.36 pp — matches ground truth exactly. PASS.
- Table 2 per-group DINO: 97.25% / 8.57% / 36.54% / 81.93% — matches ground truth exactly. PASS.
- Table 2 per-group Supervised: 99.82% / 81.93% / 92.42% / 97.82% — matches ground truth exactly. PASS.
- Training dynamics (Section 5.2): Best val WGA "24.1% at epoch 17" — matches ground truth (24.1%, epoch ~17). PASS.
- Supervised val WGA: ">70% by epoch 2, >80% for remaining epochs" — matches ground truth. PASS.
- RQ2 language: Clearly labeled "Pending" in Section 5.3, Table title, Discussion Finding 3. PASS — not overclaimed.
- RQ3 language: Clearly labeled "Planned" in Section 5.4. PASS — not overclaimed.
- Abstract last paragraph: Correctly states anisotropy and SAM results are pending. PASS.
- Conclusion: Clearly states mechanistic test is "ongoing." PASS.

---

## Persona 2: Bored Reviewer Findings

### Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Would I continue after the abstract? | CONCERN | Abstract is clear but the "pending" disclosure in the last sentence is deflating. A top-venue reviewer reads "pending experimental runs" and wonders why this was submitted. |
| Problem clear in first 2 paragraphs? | PASS | The 8.6% / 62% / 73 pp framing is vivid and grounded. |
| Novelty clear within first page? | PASS | The geometric reframing and SAM-during-SSL proposal are stated early and clearly. |
| Figure 1 understandable without text? | CONCERN | Figures are referenced as "[Figure N] placeholders." Cannot assess. Assumed not yet designed. |
| Attention loss point identified? | YES — see below | Attention drops at Section 5.3, the first "PENDING" result section. |
| Abstract makes compelling case? | PARTIAL | The confirmed finding is compelling; the pending disclosure undercuts it. |
| "Pending" result framing handled well? | FAIL | See BORED-FATAL-001. |
| Genuinely novel to top-venue ML? | CONCERN | See BORED-MAJOR-001. |

### FATAL Issues

**BORED-FATAL-001: Submitting an incomplete paper to a top venue is a structural rejection risk**
Sections 5.3 (RQ2) and 5.4 (RQ3) contain no results — they explicitly state "PENDING" and "Planned." For ICML/NeurIPS, this is a near-certain desk rejection or a "reject — incomplete work" from reviewers. A reviewer with 5 papers to review sees: Abstract says results are pending → sections confirm this → immediate reject. The paper as currently structured is a proposal, not a paper. Either (a) wait for the 200-epoch results before submitting, or (b) completely reframe as a position/proposal paper if the venue allows it, with the WGA gap as the primary contribution. The current framing attempts to straddle both and satisfies neither.

Severity: FATAL for submission viability. Not a content error but a fatal strategic error.

### MAJOR Issues

**BORED-MAJOR-001: Novelty undercut by the pending results being the entire novel contribution**
The abstract describes three contributions: (1) WGA gap measurement (confirmed), (2) anisotropy measurement protocol (designed but unmeasured), (3) SAM-SSL intervention (proposed but untested). Contribution 1 is confirmatory/empirical — valuable but not a methodological novelty. Contributions 2 and 3 are the actual novel contributions, and both are unverified. A bored reviewer at a top venue will correctly observe that the paper's novelty is pending.

**BORED-MAJOR-002: Page limit violation (estimated 8.5 pp vs. 8 pp ICML limit)**
Ground truth flags ~8.5 pp estimate against the ICML 8pp limit. The paper needs trimming. The methodology section (Section 3) is the most verbose — the algorithm pseudocode and the extensive design rationale paragraphs could be condensed. Related work is comprehensive but could lose the DGSAM paragraph (one sentence suffices).

### Attention Loss Points

- **Section 5.3** (page ~6): "PENDING" in bold in a results section. This is where a bored reviewer skims to the conclusion.
- **Section 2 Related Work**: The 4-subsection structure is thorough but slows the paper's momentum. A reviewer wanting to reach the experimental results will skim this.
- **Section 3.3 Step 4**: The Pearson r correlation with only 4 checkpoints (epochs 50/100/150/200) will raise eyebrows — 4 data points for a "significant" correlation (p < 0.05) requires r > 0.95, which is an extremely tight bar.

---

## Persona 3: Skeptical Expert Findings

### FATAL Issues

**SKEPT-FATAL-001: DINO uses pretrained ImageNet weights; Table 3 SimCLR is trained from scratch — the comparison is fundamentally unfair and unacknowledged in Results**
Section 4.4 states: "DINO uses ViT-S/8 with pre-trained weights from the official DINO repository." This means the DINO model was not trained from scratch on Waterbirds — it used weights pretrained on ImageNet (or a large dataset), then fine-tuned or linearly probed on Waterbirds. The SimCLR baseline in Table 3 (43.8% WGA) appears to be trained from scratch on Waterbirds. The paper's Section 5.5 briefly mentions "the use of pretrained DINO weights, which may have encoded stronger background biases from pretraining" as one possible explanation for the 8.57% vs. 43.8% discrepancy — but frames this as a footnote, not a fundamental confound.

This is a fatal methodological problem: if the 73.4 pp WGA gap is partly explained by DINO importing ImageNet background biases rather than learning them on Waterbirds, then the claim that "SSL-SGD training on spurious correlation benchmarks causes severe WGA degradation" is not fully supported by the data. The WGA degradation may be partly attributable to the pretrained weights, not to SSL-SGD on the spurious benchmark. The paper needs to either: (a) run SimCLR from scratch on Waterbirds and measure the gap, (b) run DINO from scratch, or (c) explicitly frame the pretrained-weight confound as a major limitation and caveat all claims accordingly.

Note: The Discussion (Section 6.2 Limitation 2) mentions scope limitations but does not flag the pretrained-weight confound as a limitation — it is buried in a brief phrase in Section 5.5.

### MAJOR Issues

**SKEPT-MAJOR-001: "First application of SAM to SSL spurious correlation robustness" — unverified claim**
The paper claims this is "the first application of SAM to SSL spurious correlations." Given the listed unverified references (ghaznavi2023lfr, ghaznavi2024evals, gatmiry2024sam, izmailov2022spurious, zhang2022re, yadav2026crossvariant, ji2025scer, park2025g2sam) and the existence of a "[CITATION NEEDED]" NeurIPS 2025 spectral regularization paper in Section 2.3, the novelty claim cannot be confirmed. A reviewer in this domain will have access to recent preprints. The "first" claim is only defensible if a thorough literature search has been completed — and the [CITATION NEEDED] in Related Work signals it has not been.

**SKEPT-MAJOR-002: LFR proxy transfer to SSL representations is an unsupported assumption**
The entire annotation-free measurement protocol (Section 3.3) relies on the LFR assumption: that top-25% high-loss linear probe samples are a reliable proxy for spurious/minority group members. LFR [Ghaznavi 2023] validated this proxy for supervised ERM representations. The paper acknowledges in Limitation 3 (Section 6.2) that this transfer to SSL representations is unvalidated. However, this is not a minor limitation — it is a load-bearing assumption of the entire measurement protocol. If the proxy fails to identify spurious-direction samples in SSL representations (e.g., because SSL representations have different loss distributions), the anisotropy ratio measures nothing meaningful. This needs to be validated before the measurement protocol is published as a contribution.

**SKEPT-MAJOR-003: Pearson r with 4 data points — statistical validity concern**
Section 3.3 Step 4 and Section 4.5 propose computing Pearson correlation between AR and WGA at 4 checkpoints (epochs 50, 100, 150, 200) and setting a significance threshold of p < 0.05. With n=4 data points, a p < 0.05 threshold for Pearson r requires |r| > 0.950 (two-tailed). This is an extremely conservative bar that leaves almost no room for any noise. The paper should either increase the number of checkpoints (e.g., every 25 epochs = 8 checkpoints, or every 10 = 20 checkpoints), or use a less stringent correlation threshold, or acknowledge this as a limitation of the planned analysis.

**SKEPT-MAJOR-004: The geometric hypothesis mechanism is hand-wavy — the SAM-to-anisotropy causal chain is speculative**
Section 3.4 states: "When the loss landscape has higher curvature along spurious directions, SAM's perturbation will more frequently step in spurious directions to find the worst-case loss." This is the key mechanistic claim, but it is stated as an intuition, not derived from theory. SAM's perturbation is $\rho \cdot \nabla_\theta \mathcal{L}(B, \theta) / \|\nabla_\theta \mathcal{L}(B, \theta)\|$ — it steps in the gradient direction of the full batch, not specifically in spurious-feature directions. Whether this gradient direction aligns with spurious-feature Hessian eigenvectors depends on the loss landscape and the batch composition. The paper acknowledges Gatmiry 2024 as theoretical motivation but also notes it applies to supervised cross-entropy, not InfoNCE. The mechanism connecting "SAM perturbation" to "preferential flattening of spurious directions" in InfoNCE is unproven and requires either theoretical derivation or empirical demonstration (which is pending). The discussion in Section 6.3 correctly identifies this tension, but Section 3.4 states the mechanism too confidently.

### Missing Limitations

1. **Pretrained-weight confound**: DINO's WGA of 8.57% may reflect ImageNet pretraining background biases, not only SSL training on Waterbirds. This is mentioned in passing but not listed as a named limitation.

2. **Single random seed**: Section 4.4 notes "Seed 1 for initial PoC run." With only one random seed, the WGA numbers could be seed-sensitive. WGA is a minimum across groups — particularly susceptible to variance. No error bars or seed ablation is planned.

3. **4 data points for Pearson correlation**: n=4 is not noted as a statistical limitation.

4. **ViT vs. ResNet-50 architecture mismatch**: DINO uses ViT-S/8 (384-dim); SimCLR and MoCo-v2 use ResNet-50 (2048-dim). Comparing these models' WGA is conflating architecture effects with SSL objective effects.

5. **No ablation of SAM radius ρ**: The paper uses ρ=0.05 with ASAM as a secondary variant, but does not plan a sensitivity analysis for ρ. SAM's behavior is known to be sensitive to ρ.

---

## MINOR Issues (for Human Review)

**MINOR-001: "unmotivated" should be "unverified" in Discussion Section 6.1 Finding 3**
Text reads: "The geometric hypothesis remains unverified but unmotivated." This is presumably a typo for "unverified but well-motivated" or "unverified but not unmotivated" — the paper extensively motivates the hypothesis. As written it contradicts the entire preceding argument.

**MINOR-002: "[CITATION NEEDED]" in Section 2.3 must be resolved before submission**
"A recent NeurIPS 2025 paper applies spectral regularization to SSL to reduce shortcut reliance [CITATION NEEDED]." The 43.8% SimCLR result in Table 3 is attributed to this paper. If the citation is unresolved, Table 3's attribution is unverifiable. This is simultaneously a citation gap and a numerical attribution issue.

**MINOR-003: Inconsistent precision in abstract vs. tables**
Abstract uses "8.6%", "81.9%", "73.4 pp"; Table 1 uses "8.57%", "81.93%", "73.36 pp". Choose one precision level and apply consistently, or add a note "(rounded to 1 decimal)" in prose sections.

---

## Summary for Revision Agent

### MUST FIX (FATAL)

1. **ACC-FATAL-001 / Title**: Change the title to not claim SAM results that do not exist. Suggested: "SSL Pretraining with SGD Creates Geometrically Stable Spurious Shortcut Encodings: Toward SAM as a Training-Time Intervention" or submit only after SAM results are available.

2. **BORED-FATAL-001 / Incomplete paper**: Do not submit until RQ2 and RQ3 have results, OR reframe as a "position/findings" paper with the WGA gap and geometric protocol as the contribution (if venue format allows). Current framing is not submission-ready.

3. **SKEPT-FATAL-001 / Pretrained-weight confound**: Add a dedicated named limitation (Limitation 0 or prominent in Limitation 2) that the DINO baseline uses ImageNet-pretrained weights, which may pre-encode background biases independent of Waterbirds SSL training. All WGA gap claims must be caveated accordingly. Consider adding a from-scratch SimCLR result as a cleaner baseline for RQ1.

### MUST FIX (MAJOR)

4. **ACC-MAJOR-003 / Citation inconsistency**: Resolve "Ji et al., 2025" vs. "park2025g2sam" — determine correct first author. Resolve Table 3's 43.8% SimCLR attribution (is it Ji/Park 2025 or the [CITATION NEEDED] NeurIPS 2025 paper?). These are different issues that may be conflated.

5. **ACC-MAJOR-001+002 / Rounding consistency**: Standardize all WGA percentages and pp gaps to consistent precision throughout the document (recommend 2 decimal places matching the tables).

6. **SKEPT-MAJOR-001 / "First application" claim**: Add qualifier: "to our knowledge" and note that the literature search is ongoing (the [CITATION NEEDED] entry demonstrates incompleteness).

7. **SKEPT-MAJOR-002 / LFR proxy assumption**: Add validation of the LFR proxy precision/recall against Waterbirds group labels as a required (not optional) result before the measurement protocol is presented as a contribution.

8. **SKEPT-MAJOR-003 / Pearson r with n=4**: Either increase checkpoint frequency or explicitly acknowledge that n=4 requires |r|>0.95 for p<0.05, and consider alternative statistical approaches (e.g., monotonic trend test, Spearman rank correlation with explicit acknowledgment of n=4 limitation).

9. **SKEPT-MAJOR-004 / SAM mechanism**: Soften Section 3.4 mechanism language from confident assertion to hypothesis framing. Use "we hypothesize that SAM's perturbation will more frequently align with spurious directions" rather than stating the mechanism as established.

10. **BORED-MAJOR-002 / Page limit**: Target 8.0 pp for ICML. Cut: (a) the algorithm pseudocode (can be a 2-line description), (b) DGSAM paragraph in Related Work (one sentence), (c) "Design rationale" paragraphs in Section 3.3/3.4 (move to appendix).

11. **MINOR-001**: Fix "unverified but unmotivated" to "unverified but well-motivated" in Section 6.1 Finding 3.

12. **MINOR-002**: Resolve [CITATION NEEDED] before submission.

### Persuasiveness Status

| Check | Status |
|-------|--------|
| Problem clear in first 2 paragraphs | PASS |
| Novelty clear within first page | PASS |
| Abstract compelling | PARTIAL — pending disclosure deflates it |
| Pending result framing | FAIL — two of three RQs are unanswered |
| Novelty defensible at top venue | CONCERN — pending results are the novelty |
| Page limit compliant | FAIL — ~8.5 pp vs. 8 pp limit |
