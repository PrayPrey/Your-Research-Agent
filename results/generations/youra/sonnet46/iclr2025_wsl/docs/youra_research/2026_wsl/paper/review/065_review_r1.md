# Phase 6.5 Adversarial Review — Round 1 (R1)
# Focus: Accuracy and Engagement
# Personas: Accuracy Checker, Bored Reviewer, Skeptical Expert
# Date: 2026-03-16

---

## GROUND TRUTH REFERENCE TABLE

| Claim Type | Paper States | Ground Truth | Match? |
|-----------|-------------|--------------|--------|
| NFT Δρ (h-e1) | 4.09×10⁻⁶ | 4.09×10⁻⁶ | ✓ |
| NFT Δρ (h-m1) | 4.71×10⁻⁷ | 4.71×10⁻⁷ | ✓ |
| flat-MLP Δρ (h-e1) | 0.1595 | 0.1595 | ✓ |
| flat-MLP Δρ (h-m1) | 0.640 | 0.640 | ✓ |
| NFT ρ(s=0) | 0.489 | 0.489 | ✓ |
| flat-MLP ρ(s=0) | 0.303 | 0.303 | ✓ |
| flat-MLP ρ(s=1.0) | −0.337 | −0.337 (h-m1) | ✓ |
| ΔR² | 0.228 | 0.228 (pipeline) | ⚠ ARITHMETIC FLAG |
| NFT params | 75K | 75,000 | ✓ |
| flat-MLP params | 3.04M | 3,040,000 | ✓ |
| params ratio | 40× | 40.5× | ✓ (rounded correctly) |
| Total models | 29,997 | 29,997 | ✓ |
| Train/test split | 23,997 / 6,000 | 23,997 / 6,000 | ✓ |
| Total runs | 21 | 21 (h-e1:2, h-m1:18, h-m2:1) | ✓ |
| Augmentation CV | ≈107% | 1.07 | ✓ |
| Augmentation Δρ range | 0.096–0.317 | 0.096–0.317 | ✓ |

---

## PERSONA 1: ACCURACY CHECKER

*Role: Fact-checker and claim verifier. Cross-references all numerical claims against ground truth.*

### Ground Truth Verification Log

**[CHECK-001] NFT Δρ consistency across h-e1 and h-m1**

- h-e1 (Table 1): NFT Δρ = 4.09×10⁻⁶ ✓
- h-m1 (Table 2): NFT Δρ = 4.71×10⁻⁷ ✓
- Introduction states: "Δρ ≈ 4.7×10⁻⁷" → references h-m1 value ✓
- Abstract states: "near-zero permutation sensitivity" ✓
- Discussion says "Δρ ≈ 4.7×10⁻⁷" (Discussion uses h-m1 value, which is the more rigorous 18-run experiment) ✓
- **ISSUE:** The Introduction (line 45) cites "Δρ ≈ 4.7×10⁻⁷" while Table 1 (h-e1) shows 4.09×10⁻⁶. Introduction uses h-m1 value to summarize contributions, which is fine, BUT the sentence reads as if summarizing the primary result — a reader may wonder why Table 1 shows a different number. This is a **clarity issue** (MINOR), not a factual error.

**[CHECK-002] flat-MLP degradation percentage claim — "52–89%"**

- Paper claims "52–89%" degradation multiple times (abstract, conclusion, discussion)
- h-e1: Δρ/ρ(s=0) = 0.1595/0.3029 = 52.66% ✓
- h-m1: Δρ/ρ(s=0) = 0.640/0.303 = 211%... but paper uses "89%" in conclusion
- Ground truth note: "89%" refers to h-m1 flat-MLP rho going from 0.303 to −0.337, which is a total correlation reversal
- Let's check: actual "89% degradation" in context: Introduction says "loses 89% of its predictive correlation when the target network's neurons are randomly shuffled"
- Calculation: (0.303 − (−0.337)) / 0.303 = 0.640 / 0.303 = 211% — this is **MORE** than 89%, not 89%
- Alternative interpretation: ρ goes from 0.303 to −0.337. If interpreted as |(−0.337)|/0.303 → that's not the standard usage
- Another interpretation: maybe referencing loss of POSITIVE predictive power: from +0.303 to −0.337, the "89%" might be calculated differently
- Actually checking: from initial rho 0.303 at s=0, the final negative rho −0.337 means 100% + 111% = more than 100% degradation
- The paper may be referring to h-e1 for the "52%" and **some other calculation** for "89%"
- But h-m1 flat-MLP at s=0 is 0.303, s=1.0 is −0.337. That's a full sign flip, not 89%
- **HOWEVER:** checking the introduction opening: "loses 89% of its predictive correlation" — let me check if this refers to h-m2:
  - h-m2 flat_mlp_delta_rho = 0.6265, flat_mlp_rho_s0 from verification_state: need to check h-m2 04_validation.md
- The ground truth file clarifies: "52% on primary (h-e1, 50 epochs); 89% collapse in h-m1 ablation (Δρ=0.640 on 0.303 baseline)"
  - 89% = (0.640 / 0.303) × (1/something)? No...
  - Actually: from rho_s0=0.303 to rho_s10=−0.337: the range is 0 to 0.303 (positive predictive power), and −0.337 is entirely below zero. But this seems like a **MAJOR ARITHMETIC ERROR** in how 89% is derived.
- **SEVERITY ASSESSMENT:** The "89%" figure appears in Introduction, Discussion, and Conclusion. If the calculation is wrong, this is a MAJOR credibility issue. Let me flag for R2 Serena verification.

**ISSUE R1-ACCURACY-001 [MAJOR]:** "89% degradation" figure not arithmetically derivable from reported values. h-m1 shows flat-MLP goes from ρ=0.303 to ρ=−0.337 (Δρ=0.640). This is 211% degradation by the paper's own formula (Δρ/ρ(s=0) = 0.640/0.303). The "89%" figure is unexplained. Must either: (a) provide the arithmetic derivation, or (b) replace with the verifiable "211% relative degradation" or "rho sign-flip from +0.303 to −0.337."

**[CHECK-003] "62% relative improvement" — NFT vs flat-MLP baseline**

- NFT ρ = 0.489, flat-MLP ρ = 0.303
- (0.489 − 0.303) / 0.303 = 0.186 / 0.303 = 61.4% ✓
- Paper rounds to "62%" — acceptable ✓

**[CHECK-004] ΔR² = 0.228 arithmetic check**

- Paper states: ΔR² = R²(NFT-base) − R²(flat-MLP+aug) = 0.239 − 0.056 = **0.228** (Results section, line 75)
- ARITHMETIC: 0.239 − 0.056 = **0.183**, NOT 0.228
- Ground truth file flags this: "0.239 − 0.056 = 0.183... wait — check"
- verification_state confirms delta_r2: 0.2280 (from h-m1 key_findings)
- **Two possibilities:** (a) R² values in Table 2 (0.239, 0.056) are rounded, and actual unrounded values give 0.228; OR (b) There is a genuine arithmetic error
- The verification_state key_findings show: nft_delta_rho: 4.71e-07, delta_r2: 0.2280, flat_mlp_aug_delta_rho: 0.2239
- R²(NFT-base) = 0.239 (displayed in Table 2, rounded from perhaps 0.2390 or slightly different)
- R²(flat-MLP+aug) = 0.056 (displayed in Table 2)
- If actual R²(NFT-base) = 0.2840 and R²(aug) = 0.056 → ΔR² = 0.228 ← POSSIBLE
- OR: R²(NFT-base) = 0.239, R²(aug) = 0.011 → ΔR² = 0.228 ← unlikely
- OR: Table 2 values are means rounded to 3dp, real values give 0.228
- The discrepancy 0.239 − 0.056 = 0.183 ≠ 0.228 shown in the **same sentence** is a FATAL PRESENTATION ERROR, regardless of what the actual values are.

**ISSUE R1-ACCURACY-002 [FATAL]:** Mathematical impossibility in Results. Line: "ΔR² = R²(NFT-base) − R²(flat-MLP+aug) = 0.239 − 0.056 = **0.228**" — but 0.239 − 0.056 = 0.183, not 0.228. Either the table values are wrong, the ΔR² is wrong, or the computation shown is incorrect. This MUST be corrected. If actual R² values differ from Table 2, the table must be updated. If ΔR² = 0.228 is correct, the R² values shown must be corrected to be consistent.

**[CHECK-005] "40,000× below threshold" claim (Figure 2 caption)**

- Figure 2 caption: "NFT is 40,000× below threshold"
- NFT Δρ (h-e1) = 4.09×10⁻⁶; threshold = 0.02
- 0.02 / 4.09×10⁻⁶ = 4,890× — NOT 40,000×
- NFT Δρ (h-m1) = 4.71×10⁻⁷; 0.02 / 4.71×10⁻⁷ = 42,462× ≈ 40,000× ✓
- Figure 2 is from h-e1 (primary robustness comparison), so the 40,000× figure refers to h-m1, not h-e1
- The Figure 2 caption should use h-e1 value → "3,700× below threshold" (as correctly stated in Observation 1 in Results)
- Actually Observation 1 correctly says "3,700× below our pre-specified 0.02 robustness threshold" for h-e1 ✓
- But Figure 2 caption says "40,000×" which is inconsistent with h-e1 data

**ISSUE R1-ACCURACY-003 [MAJOR]:** Figure 2 caption states "NFT is 40,000× below threshold" but Figure 2 shows h-e1 data where NFT Δρ = 4.09×10⁻⁶ → 0.02/4.09×10⁻⁶ = 4,890×, not 40,000×. The 40,000× figure corresponds to h-m1 (Δρ = 4.71×10⁻⁷). Fix: Change caption to "NFT is ~4,900× below threshold" (consistent with h-e1), or clarify this references h-m1.

**[CHECK-006] "3,700×" in Observation 1**

- NFT Δρ (h-e1) = 4.09×10⁻⁶; 0.02/4.09×10⁻⁶ = 4,890×
- Paper states "3,700× below our pre-specified 0.02 robustness threshold"
- 4,890 ≠ 3,700 — this is also incorrect

**ISSUE R1-ACCURACY-004 [MAJOR]:** Observation 1 states "3,700× below our pre-specified 0.02 robustness threshold" — calculation: 0.02/4.09×10⁻⁶ = 4,890×, not 3,700×. Fix: Change to "~4,900×" or "over 4,800×."

**[CHECK-007] Training epochs consistency**

- h-e1: 50 epochs (paper Table 1 caption: "50 training epochs") ✓
- h-m1: 100 epochs (paper Table 2 caption, Methodology section) ✓
- Experiments section: "100 epochs" listed in general protocol ✓
- But Section 4 also says "h-e1: 2 runs" for RQ1 initial, "h-m1: 18 runs" for mechanism — this is correctly explained ✓

**[CHECK-008] Epoch count for h-e1 in Methodology**

- Methodology says "100 epochs" for all encoders
- But h-e1 used 50 epochs (ground truth: epochs_h_e1: 50)
- Table 1 caption correctly says "(h-e1, 50 training epochs)" ✓
- Methodology section does not specify different epochs for h-e1 vs h-m1 — could confuse reader

**ISSUE R1-ACCURACY-005 [MINOR — human review note]:** Methodology section states "100 epochs" in training protocol as if universal, but h-e1 used 50 epochs. Table 1 caption correctly says "50 training epochs." Add a clarification that h-e1 used 50 epochs and h-m1 used 100 epochs.

**[CHECK-009] Introduction opening "89% loss"**

- "A neural network trained to predict how well another network generalizes loses 89% of its predictive correlation when the target network's neurons are randomly shuffled"
- This opening hook claims "89%" — not derivable from the paper's own formula
- As noted in CHECK-002, this appears in h-m1 context: flat-MLP goes from 0.303 to −0.337
- The "89%" may be an artifact of a different calculation method not disclosed.

**ACCURACY CHECKER SUMMARY:**
- FATAL: 1 (ΔR² arithmetic inconsistency)
- MAJOR: 3 (89% figure underivable; Fig 2 caption 40,000× wrong; Observation 1 3,700× wrong)
- MINOR: 1 (epoch clarification)

---

## PERSONA 2: BORED REVIEWER

*Role: Busy NeurIPS reviewer with 5 papers to read. Checks engagement and clarity.*

### Persuasiveness Assessment

**[ENGAGE-001] Abstract — would I continue reading?**

"Neural network weights are predictive of generalization — but standard weight-space encoders treat neuron position as meaningful signal, creating representations that collapse when neurons are arbitrarily reordered at test time."

Assessment: **YES**, I would continue reading. The opening sentence is clean and sets up the problem efficiently. The abstract delivers concrete numbers ("40 times fewer parameters," "near-zero permutation sensitivity") and ends with a clear takeaway. No jargon overload. The abstract is well-written and compelling.

**abstract_compelling: TRUE**

**[ENGAGE-002] Problem clear in 1 minute?**

Reading through page 1 (Introduction): Yes. The problem is stated clearly in the second paragraph. The permutation argument is explained intuitively ("any permutation of neurons in a fully-connected network yields a functionally identical network"). I understand the problem within 1 minute.

**problem_clear_in_1_minute: TRUE**

**[ENGAGE-003] Novelty clear in 2 minutes?**

Contributions (1)-(4) are stated explicitly in Introduction. The claim of "first controlled comparison" is prominent. Within 2 minutes, the novelty is clear.

**novelty_clear_in_2_minutes: TRUE**

**[ENGAGE-004] Figure 1 self-explanatory?**

Figure 1: "Spearman ρ vs. permutation severity for NFT-base and flat-MLP" — the caption describes what to look for (flat line vs declining line, specific values). Without reading the text, I can understand that one line is flat and one declines, and that the flat one (NFT) is better. **Reasonably self-explanatory** — the Y-axis label "Spearman ρ" may not be immediately clear to all readers but is standard in ML.

**figure_1_self_explanatory: TRUE** (marginal — could benefit from a one-line "higher = better" note in caption)

**[ENGAGE-005] At what point did I lose attention?**

The paper maintains attention throughout Introduction and Results. **Attention slightly dropped** entering Section 3 (Methodology — Encoder Suite descriptions of E1 through E6 are dense and technical). The mediation analysis section is thorough but somewhat dry. The Results section re-engages with concrete numbers.

**attention_lost_at: "Section 3 encoder descriptions (E1-E6) — dense technical detail"**

**[ENGAGE-006] Would I continue reading?**

Yes. The paper is well-structured, delivers on its abstract promises, and the negative result (L2 canonicalization failure) is genuinely interesting. The writing is clear.

**would_continue_reading: TRUE**

### Engagement Issues

**[ENGAGE-007] The "89%" hook — opening sentence**

The paper opens with "loses 89% of its predictive correlation." This is an attention-grabbing hook. However, I cannot find where 89% is derived from the paper's data. If I look at Table 2, flat-MLP goes from 0.303 to −0.337 — this is a sign flip (more than 100% degradation). The "89%" is mysteriously absent from the numerical results section. As a bored reviewer, this inconsistency would make me suspicious.

**ISSUE R1-ENGAGE-001 [MAJOR — overlaps with ACCURACY-001]:** The opening hook uses "89%" which cannot be verified from any table in the paper. This is both an accuracy issue and an engagement issue: a suspicious reviewer stops reading to hunt for the source of "89%" and cannot find it. The hook would be MORE compelling and more honest using the actual numbers: "from ρ = +0.303 to ρ = −0.337 — a complete sign reversal in predictive correlation."

**[ENGAGE-008] "Catastrophically wrong" language**

The paper uses "catastrophically wrong" for L2 canonicalization (Discussion, RQ3). This is vivid language appropriate to the finding. The result (output std = 0 across all 3 seeds) truly is catastrophic. This is NOT overclaiming — the result supports the language. ✓

**[ENGAGE-009] "First controlled comparison" claim**

The abstract claims "first controlled comparison" between NFT and flat-MLP for model zoo property prediction. The Related Work section supports this: "Our work provides the first empirical test of NFT on the latter problem class." This is a verifiable claim (NFT paper evaluated on INR tasks, not zoo property prediction) that is supported by the literature review. ✓

**false_novelty_claims_found: 0**

**BORED REVIEWER SUMMARY:**
- Engagement: HIGH — would continue reading
- Persuasiveness: PASSED (all 5 key checks pass)
- Primary concern: "89%" hook cannot be verified from paper data — erodes credibility
- Attention drop: Methodology section E1-E6 descriptions (minor; acceptable in technical paper)

---

## PERSONA 3: SKEPTICAL EXPERT

*Role: Domain expert looking for holes in claims.*

### Novelty Challenge

**[SKEPTIC-001] "First controlled comparison" — is this truly novel?**

The claim is that no prior work has (a) applied NFT to model zoo property prediction and (b) compared it to flat-MLP under permutation stress. Checking the related work:
- Zhou et al. [2023] evaluated NFT on INR classification — correct, not zoo property prediction ✓
- Unterthiner et al. [2020] used flat-MLP but no equivariant comparison ✓
- Schürholt et al. [2021] augmentation work doesn't compare to NFT ✓

The "first controlled comparison" claim is defensible. The novelty is incremental (applying existing NFT to existing zoo benchmark) but the combination and the systematic ablation design are original contributions. A skeptical reviewer would rate this as "A solid empirical contribution bridging two existing lines of work" — not revolutionary, but legitimate. **No false novelty claim.**

**[SKEPTIC-002] Baseline fairness — is the comparison fair?**

Critical concern: **NFT (75K params) vs. flat-MLP (3.04M params)** — these are NOT matched architectures. NFT uses fewer parameters and achieves higher ρ. Is this because of equivariance, or simply because NFT is a better-designed architecture regardless of equivariance?

The paper addresses this partially in Section 6: "We cannot definitively rule out the alternative explanation that flat-MLP is over-parameterized..." This is honest. But the conclusion says "architectural equivariance is the correct inductive bias" — this is overclaiming if parameter count is not controlled.

**ISSUE R1-SKEPTIC-001 [MAJOR]:** The performance comparison (NFT ρ=0.489 vs. flat-MLP ρ=0.303) confounds two variables: (1) equivariance, and (2) parameter count/architecture design. The paper's conclusion that equivariance is the key factor is supported by the mediation analysis (ΔR²=0.228) but NOT by a matched-parameter comparison. The Discussion section acknowledges this limitation but the contribution claim in the Introduction frames it as a clean "equivariance advantage" without sufficient hedging. Recommendation: Add a hedged statement in contributions claim (2) or (4) that the parameter efficiency and baseline advantage are correlated but causality requires matched-parameter experiments.

**[SKEPTIC-003] Overclaiming "Architectural equivariance as the correct inductive bias"**

The paper's title and conclusion claim: "Structural Equivariance as a Necessary Inductive Bias." "Necessary" is a strong word — it implies no other approach can work. Yet:
- Oracle canonicalization achieves Δρ=0.000 ✓ (but requires oracle access)
- The paper tests ONLY L2 canonicalization (which fails), not Hungarian alignment, sort-by-magnitude, etc.
- The paper acknowledges this in Limitation 3 ✓

The word "Necessary" in the title is technically defensible because (a) the paper tests all practical alternatives (aug fails, L2-canon fails), (b) oracle-canon needs oracle access (impractical), and (c) NFT achieves oracle performance without oracle access. A reviewer could challenge this, but the paper has a good counter-argument in the limitations section. The claim is at the edge of what the data supports — **borderline overclaim but defensible with the oracle comparison**.

**ISSUE R1-SKEPTIC-002 [MINOR — human review note]:** The word "Necessary" in the title ("Necessary Inductive Bias") is a strong claim. Since the paper acknowledges in Limitation 3 that stronger canonicalization (Hungarian alignment) is untested, consider hedging to "An Effective" or "The Correct" instead of "Necessary" — unless authors want to defend this position in rebuttal.

**[SKEPTIC-004] Missing limitations — any important ones not disclosed?**

Checking against ground truth limitations (L1-L4):
- L1: CNN zoo used instead of FC-MLP zoo — DISCLOSED in Discussion ✓
- L2: Cross-pipeline transfer not validated — DISCLOSED ✓
- L3: Only L2 canonicalization tested — DISCLOSED ✓
- L4: Augmentation analysis only 3 seeds — DISCLOSED ✓

**Additional missing limitation not in ground truth:**
- The paper uses Unterthiner "MNIST zoo (CNN, adapted to FC-MLP format)" — but the generalization gap values come from training CNN classifiers on MNIST, not actual FC-MLP networks. The claim that "generalization gap signal is encoded in neuron influence concentration" may be specific to CNNs. This is a subtle gap: CNN neurons have spatial structure (filters) while FC-MLP neurons do not. The per-neuron tokenization abstracts over this, but the predictive signal may differ.
- This is partially covered by Limitation 1, but the specific point about CNN vs. FC-MLP signal structure is not made explicit.

**ISSUE R1-SKEPTIC-003 [MINOR — human review note]:** Limitation 1 could be strengthened to explicitly note that generalization gap prediction signal for CNN weights (which have spatial filter structure) may differ from FC-MLP weights (fully dense). The current limitation mentions "absolute Δρ values may differ" but doesn't explain why (the structural difference in what "neuron influence concentration" means for CNNs vs. MLPs).

**[SKEPTIC-005] Would I accept this paper?**

Conditional accept. The paper delivers on its core claims (NFT robustness, mediation analysis, L2-canon failure). The main weaknesses are:
1. The "89%" opening number is unverifiable from paper data (erodes trust)
2. The ΔR² arithmetic error (0.239 − 0.056 ≠ 0.228) would get flagged by any careful reviewer
3. The confound between equivariance and parameter count is acknowledged but the contribution framing is slightly overclaimed
4. Two figure captions have wrong multiplier values (3,700× and 40,000× should be ~4,900×)

If these are fixed, this is a solid ICML paper with genuine empirical contribution.

**unfair_baseline_comparisons: 1** (parameter count confound — partially acknowledged)
**overclaims_found: 0** (title "necessary" is borderline but defensible)
**missing_limitations: FALSE** (all key limitations disclosed)

---

## ROUND 1 SUMMARY

### FATAL Issues (blocks convergence)

| ID | Description | Location | Severity |
|----|-------------|----------|---------|
| R1-ACCURACY-002 | ΔR² arithmetic impossibility: "0.239 − 0.056 = 0.228" but 0.239 − 0.056 = 0.183 | Results §5.2, same sentence | FATAL |

### MAJOR Issues (must fix)

| ID | Description | Location | Evidence |
|----|-------------|----------|---------|
| R1-ACCURACY-001 | "89%" degradation not arithmetically derivable. h-m1: Δρ/ρ(s=0) = 0.640/0.303 = 211%; h-e1 gives 52.7% | Introduction, Discussion, Conclusion | Ground truth: h-m1 flat_mlp rho 0.303→−0.337 |
| R1-ACCURACY-003 | Figure 2 caption "40,000× below threshold" wrong for h-e1 data (should be ~4,900×) | Figure 2 caption | h-e1 Δρ=4.09e-6; 0.02/4.09e-6=4,890× |
| R1-ACCURACY-004 | Observation 1 "3,700×" wrong (should be ~4,900×) | Results §5.1 Observation 1 | Same calculation |
| R1-ENGAGE-001 | Opening hook "89%" coincides with unverifiable number, erodes credibility (overlaps ACCURACY-001) | Introduction line 1, Conclusion | No table contains the source |
| R1-SKEPTIC-001 | Contribution framing conflates equivariance advantage with parameter efficiency advantage without sufficient hedging | Introduction contributions (4) | NFT 75K vs flat-MLP 3.04M confound |

### MINOR Issues → Human Review Notes

| ID | Description | Category |
|----|-------------|---------|
| R1-ACCURACY-005 | Methodology says "100 epochs" universally but h-e1 used 50 epochs | clarity |
| R1-SKEPTIC-002 | Title "Necessary" is a strong claim given untested canonicalization alternatives | style |
| R1-SKEPTIC-003 | Limitation 1 could explicitly note CNN vs FC-MLP signal structure difference | clarity |
| R1-ENGAGE-001b | Figure 1 caption could benefit from "higher = better" note | formatting |

### Persuasiveness Assessment

| Check | Result |
|-------|--------|
| abstract_compelling | TRUE |
| problem_clear_in_1_minute | TRUE |
| novelty_clear_in_2_minutes | TRUE |
| figure_1_self_explanatory | TRUE (marginal) |
| would_continue_reading | TRUE |
| attention_lost_at | Section 3 encoder descriptions (minor) |
| false_novelty_claims_found | 0 |
| unfair_baseline_comparisons | 1 (parameter confound, partially acknowledged) |
| overclaims_found | 0 |
| missing_limitations | FALSE |

**Persuasiveness PASSED** (all key engagement checks pass; major issues are factual/numerical, not structural)

### R1 Issue Counts

| Persona | FATAL | MAJOR | Human Review Notes |
|---------|-------|-------|-------------------|
| Accuracy Checker | 1 | 3 | 1 |
| Bored Reviewer | 0 | 1 | 1 |
| Skeptical Expert | 0 | 1 | 2 |
| **TOTAL (deduplicated)** | **1** | **5** | **4** |

Note: R1-ENGAGE-001 and R1-ACCURACY-001 are the same underlying issue ("89%" figure) — counted once in MAJOR.

**Deduplicated FATAL: 1, MAJOR: 4, Human Review Notes: 4**

### Revision Agent Summary

**Priority 1 (FATAL — fix immediately):**
- Fix ΔR² presentation: "0.239 − 0.056 = 0.228" is arithmetically wrong. Investigate actual R² values and correct table or formula.

**Priority 2 (MAJOR — fix before convergence):**
- Fix "89%" figure: replace with derivable percentage or provide explicit calculation
- Fix Figure 2 caption "40,000×" → use h-e1 consistent value
- Fix Observation 1 "3,700×" → correct calculation from h-e1 data
- Add hedging language on parameter efficiency vs. equivariance in contribution (4)

**Priority 3 (Human Review Notes — do NOT auto-fix):**
- Epoch clarification in Methodology
- "Necessary" in title
- Limitation 1 CNN/FC-MLP signal difference
- Figure 1 caption "higher = better"
