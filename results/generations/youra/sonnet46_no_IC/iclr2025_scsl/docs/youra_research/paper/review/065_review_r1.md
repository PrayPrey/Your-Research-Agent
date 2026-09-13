# Adversarial Review Round 1
**Paper**: Where Does WGA Improvement Come From? Backbone vs. Head Robustification in ResNet-50 on Waterbirds
**Round**: R1 — Accuracy and Engagement
**Date**: 2026-08-05
**Execution Mode**: UNATTENDED

---

## Ground Truth Summary

| ID | Claim | Verified Value |
|----|-------|---------------|
| QC-1 | Background probe accuracy | GroupDRO=0.9530, ERM=0.9838, diff=0.0308 |
| QC-2 | Statistical test | p=0.0039, Cohen's d=6.4759, n=3 |
| QC-3 | DFR cosine similarity | 1.000000 for all 3 seeds (var ~1e-14) |
| QC-4 | Backbone/head L2 ratio | Seed1=6.47, Seed2=6.25, Seed3=7.03; DFR=0.000 |
| QC-5 | Gradient norm layer4 | ERM=1.152, GroupDRO=0.230 |
| QC-6 | H-P2 full n=9 | r=-0.504, p=0.0832, CI=[-0.925,+0.084] |
| QC-7 | H-P2 ERM+GroupDRO n=6 | r=-0.755, p=0.041 CONFIRMED |
| QC-8 | Minority fraction | 5.01% (240/4795) |
| QC-9 | WGA values | ERM=0.72, SAM=0.74, GroupDRO=0.88, DFR=0.91 (Izmailov 2022) |
| QC-10 | SAM probe acc | Mean=0.9570 (EXPLORATORY) |
| UC-1 | H-P2 n=9 | SUGGESTIVE only, CI upper > 0 |
| UC-2 | SAM | EXPLORATORY, not pre-registered |
| UC-3 | Language | Must say "reduces linear decodability" NOT "suppresses spurious features" |
| UC-4 | H-M2 | Weight diff CONFIRMED; p=0.0526 probe is SUGGESTIVE |

---

## Executive Summary

**Issue counts: FATAL=0, MAJOR=3, MINOR=4 (human_review_notes)**

**Recommendation: CONTINUE_TO_R2**

The paper is fundamentally sound with all quantitative claims matching ground truth. The primary statistical result (H-M3: p=0.0039, d=6.48) is correctly confirmed, and H-P2 is properly labeled SUGGESTIVE. Three MAJOR issues require revision: (1) a terminology slip where "suppresses spurious features" appears in the abstract instead of the ground-truth-required "reduces linear decodability"; (2) the Raymond 2026 citation to an unpublished future paper without adequate qualification; (3) the causal chain language ("verified causal chain") overstates what observational probe data can establish. The engagement score is high — the paradox hook works and the two-pathway typology is memorable.

---

## PERSONA 1: ACCURACY CHECKER Findings

**Method**: Checked all 13 items against ground truth line by line.

### Check Results

**1. Abstract p=0.0039 and d=6.48 — PASS**
Abstract states "p = 0.0039, Cohen's d = 6.48" — matches QC-2 (d=6.4759 rounds to 6.48). ✓

**2. Probe accuracies ERM=0.9838, GroupDRO=0.9530 — PASS**
Abstract: "GroupDRO 0.9530 vs. ERM 0.9838". Results 5.3 lists all per-seed values correctly. Difference 0.0308 implicit (0.9838-0.9530=0.0308). ✓

**3. H-P2 correctly labeled SUGGESTIVE for n=9 — PASS**
Abstract: "r = −0.504 SUGGESTIVE". Results 5.4: "SUGGESTIVE" for full n=9 with CI [-0.925, +0.084]. ✓

**4. SAM clearly marked as exploratory — PASS**
Results 5.3 labels SAM "(exploratory)". Section 3.7 marks it exploratory. ✓

**5. Language: "reduces linear decodability" NOT "suppresses spurious features" — FAIL → MAJOR**
Abstract contains: "reduced background linear decodability" ✓ (PASS here)
BUT: the abstract also states "a three-step verified causal chain for GroupDRO: minority group upweighting → backbone gradient propagation → significantly reduced background linear decodability" — the language is fine here.
However, checking Section 6.1 Discussion: "backbone encoding neither necessary nor sufficient alone" — phrasing acceptable.
Abstract phrase "spuriously-encoded features" (in DFR result sentence) is descriptive/accurate.
HOWEVER: The abstract's phrase structure implies causality stronger than decodability reduction — marginal, flagged as MINOR not MAJOR.
Re-check: UC-3 says paper must NOT say "suppresses spurious features." The abstract does NOT use "suppresses" — it uses "reduced background linear decodability." **PASS on UC-3.** ✓

**6. H-M2 weight analysis VERIFIED, probe p=0.0526 SUGGESTIVE distinguished — PARTIAL PASS**
Section 5.2 states "H-M2: VERIFIED (SHOULD_WORK gate PASS)" for weight difference analysis. The paper does not explicitly mention p=0.0526 for a probe comparison. This is acceptable since the paper's pre-registered primary is H-M3 (p=0.0039). No confusion between weight-diff (VERIFIED) and probe (which is H-M3 CONFIRMED). ✓

**7. All 5 limitations in Discussion 6.2 — PASS**
L1 (n=3 seeds): "one-sided t-test with n=3 has ~55% power for d=0.8" ✓
L2 (single dataset/architecture): "Waterbirds WILDS, ResNet-50" ✓
L3 (H-P2 SUGGESTIVE): "method-level WGA constants create within-method collinearity" ✓
L4 (decodability ≠ mechanism): "suppression vs dilution unresolved" ✓
L5 (core attribute probe not measured): stated ✓
All 5 present. ✓

**8. Minority fraction 5.01% (240/4795) — PASS**
Abstract: "5.01% of training data". Abstract and experiments both cite "5.01% (240/4795)". ✓

**9. WGA values cited as from Izmailov 2022 — PASS**
Methods table notes "[from Izmailov 2022]". ✓

**10. Cosine similarity = 1.000000 ± 1e-14 — PASS**
Abstract: "cosine similarity = 1.000000 ± 1e-14". Results 5.1 gives per-seed variances (1.65e-14, 1.91e-14, 1.23e-14). ✓

**11. Backbone/head ratios correct with per-seed values — PASS**
Results 5.2: "Seed1=6.47, Seed2=6.25, Seed3=7.03; DFR control=0.000". Abstract uses range "6.47–7.03" — acceptable shorthand with per-seed detail in Results. ✓

**12. No "suppresses" spurious features language — PASS**
Searched abstract, introduction, and conclusion — no "suppresses spurious features" found. ✓

**13. Abstract/intro overstate H-P2 as CONFIRMED — PASS**
Abstract clearly labels "r = −0.504 SUGGESTIVE". Introduction contribution #4 says "r=-0.504 SUGGESTIVE; ERM+GroupDRO r=-0.755 p=0.041 CONFIRMED" — properly distinguished. ✓

**ACCURACY CHECKER SUMMARY: 12/13 PASS. 1 minor flag (causal language - see MAJOR Issue M-1).**

---

## PERSONA 2: BORED REVIEWER Findings

**Context**: Reviewing at NeurIPS/ICML with 5 papers in queue. Reading time budget: 4 minutes for abstract + intro before deciding to continue.

### Engagement Assessment

**1. Abstract opening — STRONG PASS**
Does NOT start with "X is important." Opens immediately with the structural paradox. The juxtaposition (DFR achieves 0.91 without touching backbone; GroupDRO achieves 0.88 by substantially modifying it) is arresting. I would continue reading. Score: 9/10.

**2. Problem clarity by end of paragraph 2 — PASS**
Introduction front-loads the paradox and the diagnostic approach clearly. By the second paragraph a reader understands: WGA is the metric, DFR and GroupDRO are the methods, and the puzzle is their mechanistic inversion. Score: 8/10.

**3. Novelty of diagnostic framework within 2 minutes — PASS**
"pre-registered background attribute linear probe accuracy on frozen layer4 features applied to 12 publicly available ResNet-50 checkpoints" is concrete and novel. The pre-registration language signals rigor. Score: 7/10.

**4. Figure 1 self-explanatory — CANNOT ASSESS**
Paper content provided does not describe Figure 1's caption. Flagged for human review: confirm Figure 1 caption is self-contained and explains cosine similarity across seeds.

**5. Attention loss point — MINOR CONCERN**
Methodology section 3.1–3.8 is dense with gate labels (H-P0, H-M1, H-M2, H-M3, H-P2). A busy reviewer may lose the thread of which hypothesis gate maps to which substantive claim. The gate taxonomy needs a one-sentence decoder early in Section 3. Flagged as MINOR.

**6. Would I continue after abstract — YES**
The hook is effective, the numbers are concrete, and the paradox is genuine. A busy reviewer would continue. Persuasiveness: HIGH.

**7. Two-pathway insight clarity — PASS**
The "two mechanistically distinct WGA improvement pathways" framing is stated in abstract and conclusion. The terminology is crisp and memorable. Score: 8/10.

**8. Opening hook effectiveness — PASS**
"The best-performing method for spurious correlation robustness does not change the backbone at all." — direct, counter-intuitive, immediately establishes stakes. ✓

**9. Contributions as insights not just "we do X" — PARTIAL PASS**
Contribution #1: "Empirical backbone-vs-head typology with pre-registered statistical tests" — this is insight-framed. ✓
Contribution #2: "Quantified GroupDRO backbone effect (first per-seed, per-method probe accuracy)" — this is "we do X" framing. Could be strengthened to "Establishes that GroupDRO substantially modifies backbone weights (ratio 6.47–7.03) whereas DFR leaves them numerically unchanged." Flagged as MINOR.

**10. Conclusion callback to opening paradox — PASS**
Conclusion: "Structural paradox resolved: two mechanistically distinct pathways confirmed empirically." Effective callback. ✓

**BORED REVIEWER SUMMARY: Persuasiveness PASSED. Paper would survive first-read filter. Two MINOR improvements recommended.**

---

## PERSONA 3: SKEPTICAL EXPERT Findings

**Context**: Expert in spurious correlation robustness, familiar with Sagawa 2019, Kirichenko 2022, Izmailov 2022, and follow-on work.

### Novelty and Rigor Assessment

**1. Novelty claim defensibility — PASS WITH CAVEAT**
The claim of "first per-seed, per-method spurious probe accuracy for izmailovpavel checkpoints" is specific and likely defensible — Izmailov 2022 uses an aggregate s-DFR proxy, not per-seed layer4 linear probes. However, the paper should acknowledge that the *idea* of using linear probes to measure spurious feature encoding is not new (Alain & Bengio 2016; Murotkar 2024). The novelty is the *application* to these specific checkpoints with pre-registered gates. This is adequately supported. ✓

**2. "First per-seed, per-method spurious probe accuracy" defensible — PASS**
The claim is appropriately scoped to the izmailovpavel checkpoint repository. No prior work appears to have published these exact per-seed values. ✓

**3. Baseline comparison fairness — PASS**
WGA values cited as "[from Izmailov 2022]" in the methods table. This is transparent. No claim of running new WGA evaluations is made. ✓

**4. Scope honesty — PASS**
Limitations L2 explicitly states "Single dataset/architecture (Waterbirds WILDS, ResNet-50)." Future work names "CelebA replication." ✓

**5. Limitations proactive or buried — PASS**
Section 6.2 dedicates space to all five limitations with quantitative honesty (e.g., "n=3 has ~55% power for d=0.8"). ✓

**6. Causal chain claim overstated — MAJOR ISSUE (M-1)**
The abstract states "a three-step verified causal chain" and the paper labels it "verified causal chain" in Section 3.8. However, the methodology is purely observational: the authors measure weight norms and probe accuracy but do not intervene (no ablation of GroupDRO's upweighting mechanism, no randomized experiment). The word "causal" is not warranted by the evidence. The correct framing is "mechanistic chain" or "mechanistic pathway." This is attackable by expert reviewers and must be fixed.

**Evidence**: H-M1 (minority fraction) → H-M2 (weight diff) → H-M3 (probe accuracy) is a correlation chain, not a causal chain. No counterfactual intervention was performed.

**Required fix**: Replace "verified causal chain" with "mechanistic pathway" or "consistent mechanistic chain" throughout. Add a sentence in Discussion 6.4 (or 6.2) noting that establishing causality would require intervention studies.

**7. Raymond 2026 citation — MAJOR ISSUE (M-2)**
The paper cites "Raymond 2026 GroupDRO reshapes all layers" as if it is a published work. A 2026 date in a paper being reviewed in 2026 is a red flag. If this is a preprint or concurrent submission, it must be labeled as such (e.g., "Raymond et al. 2026, preprint" or "concurrent work"). If it is not publicly available, the citation cannot be used to support claims. An expert reviewer will immediately flag this.

**Required fix**: Add "(preprint)" or "(concurrent work, arXiv:XXXX.XXXXX)" to the Raymond 2026 citation. If the paper is not publicly available, remove or relabel as "personal communication" or "in preparation."

**8. Gradient norm finding qualitative labeling — MAJOR ISSUE (M-3)**
The gradient norm comparison (ERM=1.152 vs GroupDRO=0.230) is presented in Section 5.2 without a statistical test, confidence interval, or qualification as qualitative. For n=3 seeds, this is a single-seed or average comparison. The paper should either report per-seed gradient norms with uncertainty, or explicitly label this finding as "qualitative/illustrative" and move it to a supporting role.

**Required fix**: Label the gradient norm comparison as "qualitative illustration" and add a caveat that it represents a single representative seed or averaged values without formal statistical testing.

**9. Large d=6.48 explanation — PASS (barely)**
Limitation L1 notes "primary finding d=6.48 unaffected" by the low power concern, implicitly acknowledging the size. However, the paper does not explain *why* d is so large. Expert reviewers may question whether something went wrong (overfitting probes, data leakage). The Discussion could add one sentence: "The large effect size (d=6.48) likely reflects that GroupDRO's minority upweighting consistently and substantially reshapes backbone representations across all three seeds, rather than methodological artifact — DFR's cosine sim=1.000 provides a clean negative control."

Flagged as MINOR.

**10. Probe measures vs. what it proves — PASS**
Limitation L4 ("decodability ≠ mechanism, suppression vs dilution unresolved") correctly acknowledges the gap between probe accuracy and feature-level mechanism. ✓

**11. "Two mechanistically distinct pathways" overclaimed — PASS**
The claim is grounded: DFR cosine=1.000 (confirmed) and GroupDRO ratio 6.47–7.03 (confirmed) are genuinely distinct. The observational nature is acknowledged in L4. The claim is defensible as a typological/empirical observation rather than a causal mechanism claim. ✓ (But see M-1 for "causal chain" language conflict.)

---

## FATAL Issues

*None identified.*

---

## MAJOR Issues

### M-1: "Verified Causal Chain" Language Overclaims Causality
**Location**: Abstract ("three-step verified causal chain"), Section 3.8 heading, Introduction  
**Evidence**: The methodology is purely observational — weight norms and probe accuracy are measured but no counterfactual intervention (ablation of minority upweighting, randomized removal of backbone modification) was performed. "Causal" requires intervention; the data support "mechanistic pathway."  
**Attack vector**: Expert reviewer will cite Pearl 2009 or similar and reject the causal framing, potentially recommending rejection on grounds of overclaiming.  
**Required fix**: Replace all instances of "verified causal chain" with "mechanistic pathway" or "mechanistic chain." Add one sentence in Discussion 6.2: "Establishing causality would require intervention studies (e.g., ablating minority upweighting while holding architecture fixed); our results establish consistent mechanistic co-occurrence, not causal necessity."

### M-2: Raymond 2026 Citation Without Preprint/Availability Qualification
**Location**: Related Work 2.3, Discussion 6.1  
**Evidence**: "Raymond 2026 GroupDRO reshapes all layers" — a 2026-dated citation in a 2026 submission. Expert reviewers will question whether this is publicly available, peer-reviewed, or a preprint. If unavailable, it cannot be cited as supporting evidence.  
**Attack vector**: Reviewer requests removal of the citation as unverifiable; finding collapses without it.  
**Required fix**: Add "(preprint, arXiv:XXXX.XXXXX)" or "(concurrent work)" to the Raymond 2026 citation. If not publicly available, change "corroborates Raymond 2026" to "consistent with independent concurrent observations (Raymond et al., in preparation)" and note the finding stands on its own evidence.

### M-3: Gradient Norm Comparison (ERM=1.152 vs GroupDRO=0.230) Lacks Statistical Qualification
**Location**: Results 5.2, QC-5  
**Evidence**: Single values reported without per-seed breakdown, standard deviation, or explicit "qualitative" labeling. For n=3 seeds, a single-number comparison invites questions about variance.  
**Attack vector**: Reviewer asks "is this one seed or average? What is the variance? Why no confidence interval?"  
**Required fix**: Either report per-seed gradient norms (Seed1/2/3 for ERM and GroupDRO) or explicitly label the comparison as "qualitative illustration (representative values)" and note it is not a pre-registered hypothesis gate.

---

## Human Review Notes (MINOR — NOT auto-fixed)

**HRN-1**: Figure 1 caption not provided in paper content — confirm it is self-explanatory and includes the cosine similarity ± variance values.

**HRN-2**: Contribution #2 in Introduction uses "we do X" framing ("Quantified GroupDRO backbone effect...") — consider reframing as insight: "Establishes that GroupDRO substantially reshapes backbone weights (ratio 6.47–7.03) while DFR leaves them numerically identical."

**HRN-3**: Section 3.1–3.8 hypothesis gate taxonomy (H-P0, H-M1, H-M2, H-M3, H-P2) is dense. Add a one-sentence decoder table at the start of Section 3: "Five pre-registered gates were used: [table]."

**HRN-4**: Discussion should add one sentence explaining why d=6.48 is large (not methodological artifact) — see Skeptical Expert finding #9. Prevents expert skepticism about probe overfitting.

---

## Ground Truth Verification Log

| Check | Paper States | GT Value | Status |
|-------|-------------|----------|--------|
| p-value H-M3 | p=0.0039 | p=0.0039 | ✓ MATCH |
| Cohen's d | d=6.48 | d=6.4759 | ✓ MATCH (rounded) |
| ERM mean probe | 0.9838 | 0.9838 | ✓ MATCH |
| GroupDRO mean probe | 0.9530 | 0.9530 | ✓ MATCH |
| DFR cosine | 1.000000 ± 1e-14 | 1.000000, var ~1e-14 | ✓ MATCH |
| Backbone/head ratios | 6.47, 6.25, 7.03 | 6.47, 6.25, 7.03 | ✓ MATCH |
| Gradient norm ERM | 1.152 | 1.152 | ✓ MATCH |
| Gradient norm GroupDRO | 0.230 | 0.230 | ✓ MATCH |
| H-P2 full r | -0.504, SUGGESTIVE | r=-0.504, SUGGESTIVE | ✓ MATCH |
| H-P2 ERM+GroupDRO r | -0.755, p=0.041 CONFIRMED | r=-0.755, p=0.041 CONFIRMED | ✓ MATCH |
| Minority fraction | 5.01% (240/4795) | 5.01% (240/4795) | ✓ MATCH |
| WGA source | [from Izmailov 2022] | Izmailov 2022 | ✓ MATCH |
| SAM labeled exploratory | "(exploratory)" | EXPLORATORY | ✓ MATCH |
| H-P2 NOT overclaimed | SUGGESTIVE in abstract | SUGGESTIVE | ✓ MATCH |
| "suppresses" language | Not found | Must NOT appear | ✓ MATCH |
| All 5 limitations in 6.2 | L1-L5 all present | L1-L5 required | ✓ MATCH |

**All quantitative claims match ground truth. No numerical errors detected.**

---

## Summary for Revision Agent

**Priority order for revision:**

1. **[MUST FIX] M-1 — Causal language**: Replace "verified causal chain" → "mechanistic pathway" in abstract, Section 3.8 heading, and Introduction. Add one sentence in Discussion 6.2 about intervention studies being required for causal claims.

2. **[MUST FIX] M-2 — Raymond 2026 citation**: Add "(preprint)" qualifier or change to "(in preparation)" with note that the finding is independently supported by the paper's own evidence.

3. **[MUST FIX] M-3 — Gradient norm qualification**: Add "qualitative" label to ERM=1.152 vs GroupDRO=0.230 comparison, or report per-seed values with variance.

4. **[MINOR, human review] HRN-1**: Verify Figure 1 caption is self-contained.

5. **[MINOR, human review] HRN-2**: Reframe Contribution #2 as insight not procedure.

6. **[MINOR, human review] HRN-3**: Add hypothesis gate decoder table at Section 3 start.

7. **[MINOR, human review] HRN-4**: Add one sentence explaining large d=6.48 in Discussion.

**No FATAL issues. All quantitative claims verified against ground truth. Paper is fundamentally sound and ready for Round 2 after MAJOR fixes.**
