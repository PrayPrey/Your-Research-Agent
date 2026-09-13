# Adversarial Review — Round 1
**Paper:** Symmetry Orbits Are Geometrically Large in MLP Weight Spaces: Implications for Weight Space Encoding
**Round:** R1 — Accuracy and Engagement
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert
**Date:** 2026-08-27

---

## Ground Truth Verification Summary

| Claim | Ground Truth | Paper States | Status |
|-------|-------------|--------------|--------|
| Scaling orbit mean cosine dist | 0.3232, CI=[0.3226,0.3238] | 0.32, CI=[0.3226,0.3238] | ⚠ Rounded in abstract (acceptable) |
| Sign-flip mean cosine dist | 1.075, CI=[1.0705,1.0789] | 1.07, CI=[1.0705,1.0789] | ⚠ Rounded in abstract (acceptable) |
| Oracle pairs threshold | 100% of 2,500 pairs | 100% of 2,500 pairs | ✓ |
| NFT scaling gap | +0.0238, CI=[0.0232,0.0245] | +0.024, CI=[0.023,0.024] | ❌ CI upper bound 0.0245→rounds to 0.025, not 0.024 |
| NFT sign-flip gap | -0.0007 | -0.0007 | ✓ |
| 34× ratio | 0.0238/0.0007≈34 | 34× | ✓ |
| PCA EVR improvement | (0.086-0.055)/0.055=0.564 | 56% | ✓ |
| fraction_unique | 72/500=0.144 | 0.144 | ✓ |
| fraction_degenerate | 428/500=0.856 | 85.6% | ✓ |
| mean_tied_neurons | 2.20 | 2.20 | ✓ |
| binomial_prediction | 83% | 83% | ✓ |
| Δρ_D-A (all tasks) | +0.058/+0.053/+0.077 | +0.058/+0.053/+0.077 | ✓ (CIs missing — MAJOR) |

**Verdict:** All substantive numbers check out against ground truth. One CI bound misrepresented (MAJOR). All Δρ values correct but lack bootstrap CIs (MAJOR).

---

## PERSONA 1: Accuracy Checker

### [FATAL-P1-003] Sign-Flip Symmetry Mathematical Justification Is Broken

**Location:** Section 3.2

**Finding:** The stated mathematical justification for sign-flip functional equivalence uses a false identity, then self-corrects with a dangling "actually:" that leads nowhere:
> "for s_i ∈ {-1, +1}. For ReLU activations, f(s_i x) = s_i f(x) when s_i = -1... actually: ReLU(-x) ≠ -ReLU(x)."

If this is the primary mathematical justification for why sign-flip orbits preserve network function, the paper's entire sign-flip section rests on a flawed foundation. The self-correction confirms the identity is wrong but provides no replacement. Expert reviewers will catch this immediately and use it to reject.

**Evidence:** "actually: ReLU(-x) ≠ -ReLU(x)" appearing mid-justification without resolution

**Required Fix:** Replace with the correct two-layer sign-propagation argument: For each hidden neuron i, simultaneously negating both the incoming weights W₁[:,i] → -W₁[:,i] and outgoing weights W₂[i,:] → -W₂[i,:] preserves the network function because the negations cancel through the neuron's linear output: (-W₂[i,:]) · ReLU(-W₁[:,i] · x) produces the same post-activation contribution as W₂[i,:] · ReLU(W₁[:,i] · x) only if ReLU is positive-homogeneous — which it is for positive inputs, but not via the erroneous identity. The correct argument is: the hidden pre-activation for neuron i is h_i = W₁[:,i]·x. After sign-flip, h_i' = -W₁[:,i]·x = -h_i. ReLU(h_i') = ReLU(-h_i) = 0 when h_i > 0. This does NOT equal -ReLU(h_i) = -h_i. Therefore sign-flip symmetry requires a different justification — specifically, the functional equivalence holds only when the network function is homogeneous of degree 0 in each neuron's scale, which is NOT generally true for sign flips with ReLU. The paper must either (a) provide the correct conditions under which sign-flip symmetry holds (if it does), or (b) acknowledge this is an approximate or conditional symmetry.

**Severity:** FATAL — the mathematical foundation of the sign-flip experiments is undefended.

---

### [MAJOR-P1-001] NFT Scaling CI Upper Bound Misrepresented

**Location:** Abstract, Introduction, Table 2

**Finding:** Abstract and Introduction state CI=[0.023,0.024] for the NFT scaling gap. Ground truth and Table 2 show CI=[0.0232,0.0245]. The upper bound 0.0245 rounds to 0.025, not 0.024. Reporting [0.023,0.024] makes the interval appear narrower than it is.

**Evidence:** Abstract: "CI=[0.023,0.024]" vs Table 2: CI=[0.0232,0.0245]

**Required Fix:** Report CI=[0.023,0.025] in abstract/introduction (correct rounding of 0.0245), or use full 4-decimal CI=[0.0232,0.0245] consistently throughout.

---

### [MAJOR-P1-002] N=2,500 vs. N=500 Ambiguity

**Location:** Introduction vs. Section 3.2

**Finding:** Introduction and Abstract state "2,500 oracle-constructed pairs." Section 3.2 states "N=500 pairs for each symmetry type." These are consistent only if 2,500 = 5 conditions × 500 pairs, but this arithmetic is never made explicit. A reviewer reads both numbers and flags inconsistency.

**Evidence:** Abstract: "2,500 oracle-constructed pairs"; Methods 3.2: "N=500 pairs for each symmetry type"

**Required Fix:** Add one sentence in Section 3.2: "We construct N=500 pairs per condition across 5 conditions (A–E), yielding 2,500 total orbit pairs referenced in the abstract."

---

### [MAJOR-P1-004] Δρ Downstream Values Missing Bootstrap CIs

**Location:** Results Section 5.5, Table 5

**Finding:** The paper reports Δρ_D-A: test_acc=+0.058, gen_gap=+0.053, lr=+0.077 without confidence intervals. At n=50 test samples with CI width ≈0.6 for Spearman ρ, these point estimates could easily include zero. The paper acknowledges this elsewhere but does not report the actual CIs for these specific differences.

**Evidence:** Δρ values reported without CIs; paper separately notes "all CIs include zero"

**Required Fix:** Add bootstrap 95% CIs for all Δρ values in Table 5. The paper should show explicitly that CIs are [−X, +X] spanning zero, making the "statistically non-significant" claim concrete rather than stated.

---

## PERSONA 2: Bored Reviewer

**Would I continue reading?** Yes — abstract hook works; attention at risk in Section 3.2.

**Abstract compelling?** YES. The 1.07 cosine distance hook earns continued reading. The asymmetry finding (NFT invariant to sign-flip but not scaling) is the most interesting claim and is clearly stated.

**Problem clear in first paragraph?** YES. Weight space learning + symmetry orbits = wasted capacity. No prior knowledge of NFT or DWSNets required.

**Novelty clear in 2 minutes?** MOSTLY. The 4-contribution structure is signposted. Contributions 2 and 3 (NFT invariance probe vs. geometric concentration) are adjacent enough that a skimming reviewer may merge them.

**Attention loss point:** Section 3.2, sign-flip mathematical derivation. The dangling "actually:" is a hard stop — a bored reviewer who sees this will immediately distrust the paper. This is where FATAL-P1-003 becomes a persuasion failure, not merely a technical one.

**Figure 1 self-explanatory?** Cannot confirm without seeing figure content; described as bar chart (fig_gate_metrics.png) of mean distances vs threshold. This should work if axes are clearly labeled.

**Persuasiveness:** CONDITIONAL PASS — passes if and only if FATAL-P1-003 is fixed.

---

## PERSONA 3: Skeptical Expert

### [MAJOR-P3-001] "First Empirical Characterization" Overclaimed

**Location:** Abstract, Introduction

**Finding:** "First empirical characterization of scaling and sign-flip symmetry orbit diameters" needs defense. Entezari et al. (2022), Ainsworth et al. (2022), and Schürholt et al. (2022) all characterize weight space geometry empirically. The specific claim (cosine distance as orbit diameter metric) may be novel, but the paper does not distinguish its measurement approach from prior empirical work.

**Evidence:** "We provide the first empirical characterization of scaling and sign-flip symmetry orbit diameters"

**Required Fix:** Narrow to "first empirical quantification of orbit diameters as cosine distances in a real model zoo" and add a footnote contrasting with Entezari/Ainsworth (who measure permutation, not scaling/sign-flip orbit geometry).

---

### [MAJOR-P3-002] NFT ρ≈0.11 vs. Layer Statistics ρ≈0.9 — Gap Undercontextualized

**Location:** Related Work, Results

**Finding:** NFT achieving ρ≈0.11 while layer statistics achieves ρ≈0.9 is an extraordinary gap. This either means (a) NFT is misconfigured/undertrained, (b) the comparison is unfair, or (c) equivariant encoders fundamentally underperform on this zoo without canonicalization. None of these is explained. Reviewers will ask: if NFT barely outperforms random (ρ≈0.11 vs. chance), why is NFT the anchor encoder for this study?

**Evidence:** ρ≈0.11 (NFT) vs. ρ≈0.9 (layer statistics) stated without analysis

**Required Fix:** Add subsection or prominent paragraph explaining: "NFT's ρ≈0.11 on the Schürholt zoo reflects training at N=400 — severely underpowered. This poor performance is itself evidence of the invariance problem: NFT wastes capacity on symmetry-induced variation. Layer statistics, being permutation-agnostic, bypass this problem. Our canonicalization is designed to close this gap at adequate N."

---

### [MAJOR-P3-003] E>D Finding Not Framed as Cautionary Negative Result

**Location:** Results Section 5.5, Discussion

**Finding:** Condition E (random normalization) outperforming Condition D (full canonicalization) undermines the paper's practical recommendation. The paper recommends canonicalization but its own results show a random baseline beats the systematic approach. This is framed as a secondary result attributable to the H-C1 non-uniqueness finding, but the causal chain is speculative.

**Evidence:** E>D ordering in property prediction results; recommendation of canonicalization despite this

**Required Fix:** Add explicit cautionary statement: "We caution that full canonicalization (Condition D) did not outperform random normalization (Condition E) at N=500. We attribute this to the non-unique sign-flip canonicalization (Section 5.4), but this attribution is post-hoc. Until confirmed at N≥5,000, practitioners should prefer scaling-only canonicalization (Condition B) over full canonicalization."

---

### [MAJOR-P3-004] Single Zoo / Single Architecture Scope Not Prominent Enough

**Location:** Limitations (Discussion)

**Finding:** All experiments use a single model zoo (MNIST-based), single architecture (784→64→10), single dataset. The paper frames findings as a general "measurement-grounded framework" but provides no evidence of cross-architecture validity.

**Evidence:** Methodology section — single zoo, single architecture throughout

**Required Fix:** Add to limitations: "All findings are derived from a single architecture (784→64→10 MLP) and dataset (MNIST). Orbit geometry for deeper networks, convolutional architectures, or non-ReLU activations may differ substantially. The orbit characterization methodology generalizes; the specific numerical findings (0.32, 1.07 orbit diameters) are architecture-specific."

---

## MINOR Issues — Human Review Notes

Collected for human review only. Do NOT auto-fix.

1. **MINOR-001** [style] Abstract sentence 2 is a run-on; consider splitting at "— a geometric reality with concrete consequences."
2. **MINOR-002** [style] "sign-flip orbits by construction — an emergent consequence" — dash weakens causal claim; consider "which is an emergent consequence."
3. **MINOR-003** [style] "transforms the argument for symmetry canonicalization from a theoretical expectation into a measurement-grounded framework" — mixed metaphor (transforms argument into framework).
4. **MINOR-004** [style] "Together, these findings transform..." — weak connector for 4-claim summary; consider restructuring.
5. **MINOR-005** [clarity] Verify 428+72=500 explicitly in paper for reproducibility.
6. **MINOR-006** [clarity] "mean_tied_neurons: 2.20, binomial_prediction: 83%" — connection between numbers not explained inline.
7. **MINOR-007** [formatting] Kofinas 2024 citation — verify publication year and venue; may be a preprint.
8. **MINOR-008** [clarity] Table 2 caption should explicitly note CIs are at 95% confidence.
9. **MINOR-009** [clarity] Contributions 2 and 3 (NFT invariance probe vs. geometric concentration) are easy to confuse — consider adding a brief transition sentence distinguishing them.
10. **MINOR-010** [grammar] Check consistent use of "canonicalization" spelling throughout.

---

## Summary for Revision Agent — Prioritized Fix List

### FATAL (Fix First — Paper Cannot Proceed Without This):

1. **FATAL-P1-003**: Replace broken sign-flip ReLU derivation in Section 3.2. The "actually: ReLU(-x) ≠ -ReLU(x)" dangling self-correction must be replaced with the correct mathematical argument for why simultaneous two-layer weight negation preserves network function. If functional equivalence requires conditions beyond basic ReLU, state them explicitly.

### HIGH PRIORITY MAJORS (Fix in Revision):

2. **MAJOR-P1-001**: Fix CI upper bound: [0.023,0.024] → [0.023,0.025] in abstract/introduction.
3. **MAJOR-P1-002**: Clarify N=2,500 = 5 conditions × 500 pairs in Section 3.2.
4. **MAJOR-P1-004**: Add bootstrap CIs for all Δρ values in Table 5.
5. **MAJOR-P3-001**: Narrow "first empirical characterization" claim with qualifying clause.
6. **MAJOR-P3-002**: Contextualize NFT ρ≈0.11 vs. layer statistics ρ≈0.9 gap.
7. **MAJOR-P3-003**: Frame E>D as explicit cautionary finding.
8. **MAJOR-P3-004**: Add single-zoo/single-architecture limitation prominently.

### DEFER TO HUMAN (MINOR):

9. MINOR-001 through MINOR-010 — style, grammar, clarity, formatting.

---

```yaml
agent: adversary
round: R1
status: COMPLETED
fatal_count: 1
major_count: 7
minor_count_for_human_review: 10
persuasiveness_passed: false
would_continue_reading: true
attention_lost_at: "Section 3.2 (sign-flip derivation)"
false_novelty_claims: 1
missing_limitations: true
recommendation: MAJOR_REVISION
```
