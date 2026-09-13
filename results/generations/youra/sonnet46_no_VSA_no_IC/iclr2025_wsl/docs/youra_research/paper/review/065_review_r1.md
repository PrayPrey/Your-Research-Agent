# Adversarial Review Report — Round 1

**Paper:** "When Symmetry Hurts: Data-Regime-Dependent Sample Efficiency of Equivariant Weight-Space Encoders"  
**Reviewer pipeline:** YouRA Phase 6.5 Adversarial Review  
**Date:** 2026-08-21

---

## Ground Truth Summary

| Metric | Ground Truth Value | Source |
|--------|--------------------|--------|
| Efficiency Ratio | 6.804× | 065_ground_truth.yaml |
| N_equiv_90 | ~147 (interpolated) | 065_ground_truth.yaml |
| N_plain_90 | 1000 | 065_ground_truth.yaml |
| GNN-NFN R² N=100 | -0.016 | ground truth + h-m2 |
| GNN-NFN R² N=250 | 0.767 | ground truth + h-m2/h-m3 |
| GNN-NFN R² N=500 | 0.847 | ground truth |
| GNN-NFN R² N=1000 | 0.864 | ground truth |
| GNN-NFN R² N=full | 0.894 | ground truth |
| Flat-MLP R² N=100 | -0.141 | ground truth |
| Flat-MLP R² N=250 | 0.449 | ground truth |
| Flat-MLP R² N=500 | 0.687 | ground truth |
| Flat-MLP R² N=1000 | 0.740 | ground truth |
| Flat-MLP R² N=full | 0.886 | ground truth |
| PermAug R² N=100 | 0.138 | ground truth + h-m3 |
| PermAug R² N=250 | 0.532 | ground truth |
| PermAug R² N=500 | 0.768 | ground truth |
| PermAug R² N=1000 | 0.842 | ground truth |
| GNN-NFN max_diff | 1.80×10⁻⁶ (10,000 checks) | ground truth |
| DWSNets max_diff | 7.45×10⁻⁹ (1,000 checks) | ground truth |
| Flat-MLP max_diff | 5.59×10⁻² | ground truth |
| Full-data gap | 0.008 | ground truth |

---

## Executive Summary

- **Fatal issues: 2**
- **Major issues: 5**
- **Minor issues (for human review): 6**
- **Persuasiveness: PASS** (title, hook, and crossover finding are strong)
- **Recommendation: MAJOR_REVISION**

The paper has a compelling core finding and a strong hook. However, two fatal numerical errors — one in abstract-facing prose (wrong GNN-NFN R² at N=250) and one undermining the flat-MLP baseline computation (wrong peak R²) — must be corrected. Additionally, a structural methodological flaw exists: PermAug and Flat-MLP results come from different experimental runs (h-m2 vs. h-m3) with different seeds, which undermines the "shared-split" claim. The single-seed limitation is acknowledged but insufficiently prominently disclosed for a crossover finding presented as novel.

---

## Persona 1: Accuracy Checker

### FATAL Issues

**F1** | Location: Section 5.1, paragraph 2  
**Claim:** "GNN-NFN achieves R²=0.780 compared to flat-MLP's R²=0.115 (Δ=+0.665)"  
**Ground Truth:** GNN-NFN N=250 R² = 0.767 (not 0.780); Flat-MLP N=250 R² = 0.449 (not 0.115)  
**Discrepancy:** GNN-NFN value is wrong by 0.013; Flat-MLP value is catastrophically wrong (0.449 vs 0.115, Δ=0.334). The gap Δ=+0.665 cannot be correct under either value.  
**Correct statement:** "At N=250: GNN-NFN achieves R²=0.767 compared to flat-MLP's R²=0.449 (Δ=+0.318)"  
**Severity: FATAL** — the "largest gap" claim at N=250 is stated with entirely wrong numbers. The table in Section 5.3 correctly shows 0.449 for flat-MLP at N=250, making the prose in 5.1 internally inconsistent with the paper's own table.

**F2** | Location: Section 5.1, bullet "Flat-MLP: peak R²=0.856"  
**Claim:** flat-MLP peak R² = 0.856  
**Ground Truth:** flat_mlp N=full R² = 0.886 (from 065_ground_truth.yaml)  
**Discrepancy:** 0.030 difference. The value 0.856 appears in h-m2/04_validation.md, which explicitly notes flat_mlp_perm_aug was a broken duplicate of flat_mlp. The ground truth flat_mlp N=full = 0.886 is the authoritative value. If flat-MLP peak = 0.856, the 90% threshold = 0.770 is correct relative to 0.856 but wrong relative to the true peak 0.886 (correct threshold would be 0.797). This shifts N_plain_90 and potentially changes the efficiency ratio.  
**Impact on efficiency ratio:** If N_plain,90 uses threshold 0.797 from true peak 0.886, and flat-MLP first reaches 0.797 at N=full (it reaches only 0.740 at N=1000), then N_plain_90 = "full" (~7000), not 1000. This would make the efficiency ratio ~47×, not 6.8×. Alternatively if the paper uses the 0.856 peak from a broken experimental run (h-m2 bug: perm_aug identical to flat_mlp), the reported efficiency ratio 6.804× rests on an artifact.  
**Severity: FATAL** — either the flat-MLP peak is wrong (using a buggy h-m2 run value instead of the true value), or the ground truth is inconsistent. This must be resolved before publication.

### MAJOR Issues (Accuracy)

**A1** | Location: Section 5.1 paragraph 2 (partially covered in F1)  
**Claim:** "The gap is largest at N=250"  
**Issue:** With correct values (GNN-NFN 0.767, flat-MLP 0.449, Δ=0.318), the claim of "largest gap at N=250" should be verified against all N points. At N=500: Δ=0.847-0.687=0.160; at N=1000: Δ=0.864-0.740=0.124. At N=250 Δ=0.318 is indeed largest. So the directional claim holds, but only the Δ value needs correction (0.318, not 0.665).  
**Suggested fix:** Correct Δ to 0.318 in the prose.

**A2** | Location: Abstract, "GNN-NFN R²=−0.016" and Section 5.1  
**Issue:** The GNN-NFN equivariance max_diff reported in h-m2/04_validation.md is 2.98×10⁻⁸ (on randomly initialized model), while the paper reports 1.80×10⁻⁶ (on trained model, 10,000 checks). These are compatible if the trained-model test is more permissive, but the methodology section does not clarify that equivariance was tested on TRAINED models. If max_diff=1.80×10⁻⁶ comes from a different experiment than h-m2's 2.98×10⁻⁸, both should be explained.  
**Suggested fix:** Clarify in Section 5.2 that equivariance was verified on trained models post-training, and report both the pre-training and post-training verification results.

---

## Persona 2: Bored Reviewer

### Engagement Assessment

1. **Would I continue reading after the abstract?** YES. The abstract opens with a precise quantitative claim (6.8×), identifies a counterintuitive finding (equivariant encoder fails where it should excel), and gives a clear practical upshot (150–250 model threshold). Hooks a reviewer.

2. **Is the problem clear in first 1 minute?** YES. The Introduction paragraph 1 poses the question ("why does a symmetry-enforcing architecture fail at the scale where it should matter most?") immediately and concretely. Problem is clear.

3. **Is the novelty clear in 2 minutes?** PARTIAL. Section 2.4 "Positioning" states 4 novelty claims clearly. However, the gap between "no controlled shared-split comparison exists" and "we filled it" needs a stronger statement of WHY this gap matters to the field. Currently reads as filling a methodological hole; the practical impact of the crossover finding should lead novelty positioning.

4. **Can I understand Figure 1 without reading text?** CANNOT ASSESS (figures are referenced as [figures/...png] but not embedded/described with sufficient caption detail to evaluate). The caption "Shaded bands show bootstrap 95% CI. Log-x scale." is minimal. A standalone figure should label the crossover point and the efficiency ratio directly on the figure.

5. **At what point did I lose attention?** Section 3 (Methodology) is dense with design rationale prose. The sentence "Our experimental design is constructed to make the crossover visible" is helpful, but the subsection structure (3.1–3.6) is standard and dry. Attention is regained at Section 5.

6. **Is the hook strong?** YES. The opening paragraph of Section 1 is excellent: "A simple trick — randomly shuffling neurons before each training step — outperforms a mathematically guaranteed equivariant architecture when only 100 models are available." This is specific, surprising, and provocative without using "X is important."

### Issues Found

**M1 (MAJOR)** | Location: Section 5.1  
**Issue:** The prose states a flat-MLP R² of 0.115 at N=250, which contradicts the table in Section 5.3 (0.449) and ground truth. A bored reviewer scanning the results section will catch this inconsistency immediately and lose confidence in the paper's correctness.

**m1 (MINOR)** | Location: Abstract  
**Issue:** "consistent with expressivity equivalence theory" — the reference is to Dayan et al. [2026], a 2026 preprint. Worth noting the paper is citing work from the same year, which may raise peer review questions about timing.

**m2 (MINOR)** | Location: Section 4.3  
**Issue:** "All experiments run on NVIDIA H100 NVL GPUs (5× 95,830 MiB)" — this level of hardware detail is unusual and slightly distracting. Standard practice is "NVIDIA H100 GPU."

**m3 (MINOR)** | Location: Section 5.1  
**Issue:** The phrase "reducing zoo collection burden by ~7×" conflates efficiency ratio (6.8×) with a practical burden claim. Zoo collection is not purely linear in models (curation, training time, storage scale differently). The ~7× framing is sloppy.

---

## Persona 3: Skeptical Expert

### Novelty Assessment

**Is this really novel?** The learning curve / data-regime comparison approach is standard in ML (c.f., any sample efficiency paper). The specific application to weight-space encoders is genuinely new as no prior work reports this comparison on shared splits. The crossover finding (PermAug > structural equivariance at very low N) is a real empirical contribution. However:

- The 6.8× ratio is computed from a 4-point interpolated learning curve (N=100, 250, 500, 1000). The interpolation between N=100 (R²=−0.016) and N=250 (R²=0.767) is extremely coarse — N_equiv_90≈147 could be anywhere from 101 to 249. The confidence interval on the efficiency ratio is therefore enormous and is NOT reported.
- The expressivity equivalence theorem (Dayan et al., 2026) is a 2026 preprint cited as established theory. This may not be peer-reviewed at time of submission.

### Baseline Fairness Assessment

**MAJOR methodological concern (see B1 below):** The Flat-MLP and PermAug results come from different experimental runs:
- h-m2 (primary experiment): PermAug was broken — identical to Flat-MLP (same seeds). h-m2 explicitly notes: "FlatMLP vs FlatMLP+PermAug identical: H-E1 stored same results for both."
- h-m3 (follow-up): PermAug was re-implemented correctly and produces different results.
- GNN-NFN results come from h-m2, not re-run alongside h-m3.

This means the three conditions were NOT run in a single shared experiment: Flat-MLP from h-m2/h-e1, PermAug from h-m3 (different seeds, different training run), GNN-NFN from h-m2. The paper claims a "controlled, shared-split study" but the conditions were run in two separate phases with potential seed leakage between the Flat-MLP baseline used in h-m3 (loaded from h-m2) and the PermAug results generated in h-m3. This is a material confound for the crossover finding.

### Missing Limitations

The paper acknowledges several limitations (Section 6.2) but misses:

1. **No confidence intervals on the efficiency ratio itself.** The 6.804× ratio has no uncertainty quantification. Given that N_equiv_90 is interpolated from two points spanning a dramatic range (−0.016 to 0.767), the CI on 147 is very wide.

2. **PermAug and GNN-NFN not co-trained in shared experiment.** The crossover finding (central claim) rests on results from two separate experimental phases. This should be in limitations.

3. **Hyperparameter fairness for GNN-NFN at N=100.** The paper mentions this in 6.2 but does not quantify the potential confound. GNN-NFN's negative R² at N=100 could be an Adam LR issue rather than a structural threshold effect. This is the most exciting finding and needs the most robustness.

4. **No ablation on PermAug expansion factor.** The 11× expansion is stated but not ablated. A reviewer will ask: what if 5× or 20× were used? Is the crossover driven by the expansion factor, not the augmentation strategy?

### Issues Found

**B1 (MAJOR)** | Location: Section 3, Abstract  
**Issue:** The paper claims "controlled, shared-split study" but PermAug results (from h-m3) and GNN-NFN results (from h-m2) were generated in separate experimental runs with different seeds. The Flat-MLP baseline in h-m3 was loaded from h-m2, creating a hybrid comparison. This is the single largest methodological weakness and will be caught by any careful reviewer.  
**Suggested fix:** Explicitly state in Methodology that PermAug was run in a follow-up experiment (h-m3) sharing the Flat-MLP and GNN-NFN baselines from h-m2 but using different seeds for PermAug training. Alternatively, rerun all three conditions in a single controlled experiment.

**B2 (MAJOR)** | Location: Section 5.1, footnote area  
**Issue:** No confidence interval is reported on the 6.804× efficiency ratio. The interpolation between N=100 and N=250 means N_equiv_90 could range from 101 to 249, giving efficiency ratios from ~4× to ~9.9×. The headline number 6.804× implies false precision.  
**Suggested fix:** Report a bootstrap CI on the efficiency ratio, or at minimum state the interpolation bounds: "6.804× [CI: 4.0×–9.9×]."

**B3 (MAJOR)** | Location: Section 5.3, Discussion  
**Issue:** The crossover finding (PermAug > GNN-NFN at N=100) is presented as a "novel finding" requiring only multi-seed replication as follow-up. However, the explanation ("GNN-NFN graph encoder lacks sufficient topological diversity") is speculative and not tested. Alternative explanations (LR miscalibration at N=100, PermAug's 11× data expansion is a trivially larger effective dataset) are mentioned but not ruled out. The paper should more clearly distinguish observed finding from mechanistic interpretation.  
**Suggested fix:** Qualify the mechanistic explanation as a hypothesis and add "Ruling out the LR confound (ablation at N=100) is the highest-priority follow-up."

**B4 (MAJOR)** | Location: Section 6.2  
**Issue:** The single-seed limitation for PermAug is acknowledged, but with insufficient weight for the crossover finding. The statement "presented as a preliminary observation requiring 10-seed replication" should appear in the Abstract and Results, not only in Limitations, given this is the paper's most novel claim.  
**Suggested fix:** Add "(single-seed; requires replication)" inline in the Abstract and at first mention of the crossover in Section 5.3.

### Accept/Reject Decision

**REJECT at current state; ACCEPT WITH REVISIONS after:**
1. Correcting F1 (wrong Flat-MLP N=250 value and gap claim)
2. Resolving F2 (flat-MLP peak R² discrepancy and its effect on efficiency ratio)
3. Disclosing B1 (non-unified experimental runs) clearly
4. Adding CI on efficiency ratio (B2)
5. Prominent single-seed caveat on crossover (B4)

---

## Consolidated Issue List

| ID | Severity | Persona | Location | Issue Summary |
|----|----------|---------|----------|---------------|
| F1 | FATAL | Accuracy | Sec 5.1 prose | GNN-NFN R²=0.780 (wrong, GT=0.767); flat-MLP R²=0.115 at N=250 (wrong, GT=0.449); gap Δ=0.665 (wrong, correct=0.318) |
| F2 | FATAL | Accuracy | Sec 5.1 bullets | flat-MLP peak R²=0.856 inconsistent with ground truth flat_mlp N=full=0.886; efficiency ratio validity depends on resolution |
| B1 | MAJOR | Expert | Sec 3, Abstract | PermAug and GNN-NFN from separate experimental runs, not fully shared controlled experiment |
| B2 | MAJOR | Expert | Sec 5.1 | No CI on 6.804× efficiency ratio; interpolation has wide bounds (~4×–10×) |
| B3 | MAJOR | Expert | Sec 5.3 | Mechanistic crossover explanation is speculative, not distinguished from observation |
| B4 | MAJOR | Expert | Sec 6.2 | Single-seed crossover caveat buried in Limitations; should appear in Abstract and Results |
| M1 | MAJOR | Reviewer | Sec 5.1 | Flat-MLP R²=0.115 at N=250 in prose contradicts own table (0.449) — internal inconsistency |
| A1 | MAJOR | Accuracy | Sec 5.1 | Gap Δ=+0.665 is wrong (correct=+0.318); affects "largest gap at N=250" framing |
| A2 | MAJOR | Accuracy | Sec 5.2 | GNN-NFN max_diff discrepancy between h-m2 (2.98×10⁻⁸) and paper (1.80×10⁻⁶); methodology not clarified |
| m1 | MINOR | Reviewer | Abstract | Citation of 2026 preprint as established theory; may raise review timing questions |
| m2 | MINOR | Reviewer | Sec 4.3 | Overly specific GPU memory spec (95,830 MiB) |
| m3 | MINOR | Reviewer | Sec 5.1 | "reducing zoo collection burden by ~7×" conflates efficiency ratio with collection effort |
| m4 | MINOR | Expert | Sec 5.3 | PermAug 11× expansion factor not ablated; critical for interpreting crossover |
| m5 | MINOR | Expert | Sec 6.2 | Missing: no CI on efficiency ratio in limitations list |
| m6 | MINOR | Accuracy | Sec 2.1 | DWSNets cited as "R²≈0.89 for accuracy prediction on a private MNIST model zoo" — value not verifiable from ground truth |

---

## Minor Issues (for human_review_notes — NOT to be auto-fixed)

- **m1**: Abstract cites Dayan et al. [2026] preprint as supporting theory. If submission is to ICML 2025/2026, reviewers may question whether an unpublished 2026 paper constitutes established theory. Consider adding "recently proposed" qualifier.
- **m2**: Section 4.3 hardware spec "5× 95,830 MiB" is unconventional. Standard: "5× NVIDIA H100 NVL GPUs."
- **m3**: Section 5.1 "reducing zoo collection burden by ~7×" — zoo collection burden is not purely proportional to model count. More careful: "reducing the minimum zoo size requirement by ~7×."
- **m4**: Section 5.3 and Discussion: The PermAug 11× expansion factor is fixed without ablation. Reviewers will ask whether a 2× or 5× expansion changes the crossover. Add to future work or ablation.
- **m5**: Section 6.2 limitations should include: "The efficiency ratio (6.804×) has no formal confidence interval; the interpolated N_equiv_90≈147 spans a range that produces ratios from ~4× to ~10×."
- **m6**: Section 2.1 DWSNets description claims R²≈0.89 "on a private MNIST model zoo" — this value is from the original paper and not verifiable from current experiments. Mark as "reported by Navon et al." more explicitly.

---

## Summary for Revision Agent

### Priority 1 — FATAL (must fix before any other work)

1. **F1**: Correct Section 5.1 paragraph 2. Replace "GNN-NFN achieves R²=0.780 compared to flat-MLP's R²=0.115 (Δ=+0.665)" with correct values: GNN-NFN R²=0.767, flat-MLP R²=0.449, Δ=+0.318. Verify internally consistent with Table in Section 5.3.

2. **F2**: Resolve flat-MLP peak R² discrepancy. The ground truth has flat_mlp N=full=0.886; h-m2 validation has 0.856 (from a buggy run where PermAug=FlatMLP). Determine which is authoritative. If 0.886 is the true flat-MLP full-data R², then:
   - N_plain,90 threshold = 0.797; flat-MLP never reaches 0.797 at N≤1000 (max=0.740), so N_plain_90 > 1000
   - Efficiency ratio would exceed 6.8× substantially, OR the full-data R² needs to be reconciled with the experimental record
   - Update Section 5.1 bullet points accordingly and recompute/verify efficiency ratio

### Priority 2 — MAJOR (must fix for acceptance)

3. **B1**: Add clear disclosure in Section 3 (Methodology) that PermAug results come from a separate experimental run (h-m3) that loaded Flat-MLP and GNN-NFN baselines from h-m2. State this is a design limitation and that the shared test split and loaded baselines provide partial control.

4. **B2**: Add a confidence interval or interpolation bound statement on the 6.804× efficiency ratio in Section 5.1 and Abstract. Minimum: "The interpolated N_equiv_90≈147 yields a ratio of 6.804×; due to the 4-point grid, this estimate spans [4.0×, 9.9×] depending on the true crossover location."

5. **B4**: Move the single-seed caveat for PermAug crossover from Limitations to Abstract and inline with first crossover result in Section 5.3. Add "(single-seed PoC; multi-seed replication required)" to the N=100 crossover claim.

6. **A2**: Clarify Section 5.2 that GNN-NFN max_diff=1.80×10⁻⁶ is measured on trained models across 10,000 checks, which may differ from initialization-time equivariance checks (h-m2 reports 2.98×10⁻⁸ on random init). Both are valid equivariance measures; both should be reported with context.

7. **B3**: In Section 6.1 crossover interpretation, explicitly label the "topological diversity" explanation as a hypothesis, not a finding: "We hypothesize that GNN-NFN's below-chance performance at N=100 reflects insufficient diversity of weight-graph topologies, but do not rule out LR miscalibration. An LR sweep at N=100 is the priority follow-up to distinguish these explanations."
```

---

*Generated by YouRA Phase 6.5 Adversarial Review Agent*  
*Round: R1 | Model: claude-sonnet-4-6*
