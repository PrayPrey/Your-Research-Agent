# Adversarial Review — Round 1
**Paper**: Permutation-Equivariant Inductive Bias Advantage in Weight-Space Accuracy Prediction: A Controlled Δρ Benchmark
**Round**: R1 — Accuracy and Engagement
**Date**: 2026-05-05
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Ground Truth Summary

| Metric | Ground Truth Value | Paper Claim | Match |
|--------|-------------------|-------------|-------|
| Δρ (NFN − flat MLP) | 0.5119 | Abstract: "0.51", Intro Contribution 1: "0.512", Results: "0.5119", Conclusion: "0.51" / "0.512" | Ambiguous (rounding inconsistency) |
| 95% CI for Δρ | [0.3814, 0.6382] | Abstract: "[0.38, 0.64]", Intro: "[0.381, 0.638]", Results: "[0.381, 0.638]" | OK |
| Flat MLP ρ (H-M3, untrained) | 0.1688 | Abstract: "0.17", Results Table 2: "0.1688" | OK |
| Deep Sets ρ | 0.4466 | Abstract: "0.45", Results Table 2: "0.4466" | OK |
| NFN ρ | 0.6806 | Abstract: "0.68", Results Table 2: "0.6806" | OK |
| Flat MLP sensitivity score | 0.6490 | Abstract: "0.649", Results: "0.649" | OK |
| NFN sensitivity score | 7.34e-07 | Abstract/Results: "7.34 × 10⁻⁷" | OK |
| 885,000× reduction | Confirmed | Claimed throughout | OK |
| Low-tier NFN ρ | 0.8559 | "0.856" | OK (rounding) |
| Mid-tier NFN ρ | 0.3169 | "0.317" | OK (rounding) |
| High-tier NFN ρ | −0.3135 | "−0.314" | OK (rounding) |
| Flat MLP params (H-M1, trained) | 500,577 | Section 3.2 and Table 1: "500,577" | OK |
| Flat MLP params (H-M3, untrained) | 500,706 | Results Table 2: "500,706" | OK — but differs from Table 1 claim of 500,577 |
| NFN params | 521,953 | "521,953" | OK |
| Deep Sets params | 471,936 | "471,936" | OK |
| FlatMLP evaluated UNTRAINED in H-M3 | Confirmed (checkpoint not found) | Section 6.3 L2 "implicit"; Table 2 label "Flat MLP (untrained)" | Partially disclosed |
| CIFAR-10 tested | NOT TESTED | Section 6.3 L1 discloses | OK |
| Orbit proportion | 1.000 | "1.000" | OK |
| H-E1 dataset size | 976 checkpoints (seed-only) | Section 4.2 states "2,249 checkpoints" | MISMATCH — see ACC-FATAL-01 |

---

## Executive Summary

**Issue counts: FATAL=2, MAJOR=3, MINOR=6 (collected separately)**
**Recommendation: MAJOR_REVISION**

The paper presents a legitimate and interesting controlled benchmark with strong mechanism evidence. All core numerical claims check out against ground truth. However, two critical issues require mandatory fixing before acceptance: (1) a dataset size discrepancy where the paper describes a 2,249-checkpoint zoo for Section 4.2 yet H-E1 actually used a 976-checkpoint seed-only subset — the paper's methodology description is inconsistent with the actual experiment; and (2) the FlatMLP in H-M3 was evaluated UNTRAINED (checkpoint not found), which means Δρ=0.51 is explicitly an upper bound on the true gap — yet the paper never uses the word "upper bound" and presents this as the primary result without adequate emphasis. Three major issues are also identified. The paper is broadly compelling for a motivated reader, but the Bored Reviewer would abandon at the Results section upon discovering the untrained flat MLP caveat buried in a table header.

---

## PERSONA 1: Accuracy Checker Findings

### FATAL Issues (ACC)

---

**ACC-FATAL-01: Dataset size inconsistency — H-E1 used 976 checkpoints, paper claims 2,249**

- **ID**: ACC-FATAL-01
- **Location**: Section 4.2 (Dataset), Section 5.1 (Results — Orbit Existence)
- **Claim in paper**: Section 4.2 states "The Schurholt et al. MNIST-CNN model zoo (hyp_rand variant): 2,249 checkpoints of a BN-free CNN on MNIST, split 1,589 / 322 / 338 (train/val/test) following the standard Schurholt et al. protocol." Section 5.1 states "We sample 500 model pairs stratified across 10 accuracy deciles (50 pairs per decile) from the seed-only subset (976 checkpoints)."
- **Ground Truth**: H-E1/04_validation.md is explicit: "Zoo Size (final epoch): 976 checkpoints | Filtered to `training_iteration=50` from 50,860 total records." The dataset used was `dataset_mnist_seed.pt` (seed-only, ~976 final-epoch checkpoints), not the `hyp_rand` variant (2,249 checkpoints). Furthermore the H-E1 report notes: "The `dataset_mnist_seed.pt` uses a smaller architecture (Conv(8) channels) vs the full zoo's Conv(32)-Conv(64)-FC(128)-FC(10). H-M1/M2/M3 may need the `hyp_rand` or `hyp_fix` datasets for the full architecture."
- **Evidence**: H-E1/04_validation.md Section "Data Setup" table; also the results file YAML shows `n_checkpoints: 976`. The hyp_rand 2,249-checkpoint figure appears only for H-M1/M2/M3. The 5.1 section in the paper self-contradicts: it says "seed-only subset (976 checkpoints)" inline, but Section 4.2 presents the dataset as the hyp_rand 2,249-checkpoint zoo uniformly.
- **Required Fix**: Separate the dataset descriptions. Section 4.2 must clarify that H-E1 used the `dataset_mnist_seed.pt` (976 final-epoch checkpoints from the seed-only variant) for orbit existence probing, while H-M1/M2/M3 used `dataset_mnist_hyp_rand.pt` (2,249 checkpoints). Table 2 must clearly note which dataset was used for each encoder's ρ measurement. If all encoder training used hyp_rand, the orbit existence result (H-E1) was obtained on a smaller, differently-structured zoo — this should be stated as a limitation, because the architecture used in H-E1 (Conv(8)) differs from H-M1/M2/M3 (Conv(32)-Conv(64)-FC(128)-FC(10)).

---

**ACC-FATAL-02: Δρ=0.51 presented as primary result without stating it is an UPPER BOUND due to untrained flat MLP**

- **ID**: ACC-FATAL-02
- **Location**: Abstract, Introduction Contribution 1, Results Section 5.4, Conclusion, all tables
- **Claim in paper**: The abstract states "yielding Δρ = 0.51 [95% CI: 0.38, 0.64]" with no qualification. Contribution 1 states "We find Δρ(NFN − flat MLP) = 0.512 [95% CI: 0.381, 0.638]" with no qualification. Results Table 2 labels the baseline as "Flat MLP (untrained)" — the only disclosure. Conclusion states "Δρ = 0.512 [95% CI: 0.381, 0.638]" without qualification.
- **Ground Truth**: H-M3/04_validation.md states explicitly: "The h-m1 checkpoint `best_flat_mlp_encoder.pt` was not found at the expected path. The FlatMLP was evaluated as an **untrained model** (random weights). This explains its low rho=0.1688 and is a conservative lower-bound on FlatMLP performance. The Δρ result is therefore a lower-bound estimate of the true gap." Also: "h-m3/04_validation.md: Δρ(NFN − flat MLP) = 0.5119 — Note on FlatMLP: evaluated as untrained model (random weights) — Δρ is upper bound on true gap between trained models."
- **Evidence**: The trained flat MLP (H-M1) achieved ρ = 0.1041, while the untrained flat MLP used in H-M3 achieved ρ = 0.1688. Paradoxically, the untrained model scores higher. This means: (a) the reported Δρ = 0.512 is computed against a baseline that performed better than the trained version — making Δρ = 0.512 a LOWER bound relative to the trained baseline (NFN 0.6806 minus trained flat MLP 0.1041 = 0.5765), OR (b) relative to a properly-trained flat MLP that might reach literature-reported ρ ≈ 0.5–0.7, Δρ could be near zero. The paper does not reconcile this. More critically, the abstract and all contribution statements present Δρ = 0.51 as "the" result without the qualifier "upper bound" or even the minimal qualifier "(untrained baseline)" that appears only in Table 2. A reviewer reading the abstract, introduction, or conclusion alone will not know the flat MLP was untrained.
- **Required Fix**: Every appearance of Δρ = 0.51/0.512 in the abstract, contributions list, and conclusion MUST include a parenthetical qualifier: "(untrained flat MLP baseline; trained flat MLP ρ = 0.104)". The paper should explicitly acknowledge that the gap against a well-tuned multi-layer flat MLP is unknown and could be substantially smaller, and this should appear in the abstract or at minimum in the first contribution statement, not only in the Limitations section. The word "upper bound" (on the gap against a trained, well-tuned flat MLP) should be used at least once in the Results section.

---

### MAJOR Issues (ACC)

---

**ACC-MAJOR-01: Flat MLP parameter count inconsistency between Table 1 and Table 2**

- **ID**: ACC-MAJOR-01
- **Location**: Table 1 (Section 3.2) vs. Table 2 (Section 5.4)
- **Claim**: Table 1 lists Flat MLP parameter count as 500,577. Table 2 lists Flat MLP (untrained) parameter count as 500,706. These are different architectures: H-M1 trained the flat MLP (500,577 params); H-M3 evaluated an untrained flat MLP that apparently has 500,706 params — a different model instance.
- **Ground Truth**: ground truth YAML lists "Flat MLP (untrained, H-M3): param_count: 500706" and "Flat MLP (trained, H-M1): param_count: 500577". This discrepancy is real.
- **Evidence**: The paper never explains why two different flat MLP instances exist. A reader comparing Table 1 and Table 2 will see different parameter counts for nominally the same architecture and conclude an error exists.
- **Required Fix**: Explicitly state in Section 4.5 or the Table 2 footnote that the flat MLP in Table 2 is an untrained instance (random weights) with 500,706 params, distinct from the trained flat MLP in H-M1 (500,577 params). The discrepancy in parameter counts should be explained (likely a minor initialization difference or slightly different architecture variant). If they are truly different architectures, this must be disclosed.

---

**ACC-MAJOR-02: Rounding inconsistency of Δρ across sections creates credibility risk**

- **ID**: ACC-MAJOR-02
- **Location**: Abstract ("0.51"), Introduction Contribution 1 ("0.512"), Results ("0.5119"), Conclusion ("0.51" and "0.512")
- **Claim**: The paper uses three distinct precision levels for the same primary metric in different sections.
- **Ground Truth**: The true value is 0.5119 (H-M3/04_validation.md).
- **Evidence**: Abstract says "Δρ = 0.51"; Contribution 1 says "Δρ(NFN − flat MLP) = 0.512"; Results Table 2 says "Δρ(NFN − flat MLP) = 0.5119"; Conclusion paragraph 1 says "Δρ = 0.51" and paragraph 2 says "Δρ = 0.512". This is not a FATAL error (all are correct roundings) but it is a MAJOR credibility risk: ICML reviewers routinely check number consistency across sections, and inconsistency at the primary result invites scrutiny of everything else.
- **Required Fix**: Standardize to one precision level throughout: "0.512" (3 significant figures) is recommended. The abstract can round to "0.51" for brevity, but every other mention should be "0.512". Explicitly note in the Results: "Δρ = 0.512 (rounded to 0.51 in Abstract for brevity)."

---

**ACC-MAJOR-03: H-E1 sensitivity score result uses different dataset architecture than H-M1/M2/M3 — this architectural mismatch is not disclosed**

- **ID**: ACC-MAJOR-03
- **Location**: Section 5.1, Section 4.2, cross-reference with H-E1/04_validation.md
- **Claim**: The paper presents H-E1 (orbit existence) and H-M1/M2/M3 (mechanism and performance) as a coherent causal chain on the same zoo.
- **Ground Truth**: H-E1 used `dataset_mnist_seed.pt` with a Conv(8)-Conv(8)-Conv(8)-FC-FC architecture (976 checkpoints). H-M1/M2/M3 used `dataset_mnist_hyp_rand.pt` with Conv(32)-Conv(64)-FC(128)-FC(10) architecture (2,249 checkpoints). These are architecturally distinct model families.
- **Evidence**: H-E1/04_validation.md explicitly warns: "The `dataset_mnist_seed.pt` uses a smaller architecture (Conv(8) channels) vs the full zoo's Conv(32)-Conv(64)-FC(128)-FC(10). H-M1/M2/M3 may need the `hyp_rand` or `hyp_fix` datasets for the full architecture." The paper presents the orbit existence result (orbit_proportion=1.0, mean cosine distance=0.768) as if it characterizes the same zoo that encoders were trained on — but it does not.
- **Required Fix**: Clearly disclose in Section 4.2 and 5.1 that H-E1 used the seed-only zoo variant (976 checkpoints, Conv(8) architecture) while H-M1/M2/M3 used the hyp_rand variant (2,249 checkpoints, Conv(32)-Conv(64)-FC(128)-FC(10)). Acknowledge that the orbit existence result technically characterizes a different (smaller, differently-structured) zoo. The causal chain argument (orbit existence → capacity waste → performance gap) bridges two different datasets, which weakens it. This should be prominently disclosed as a limitation.

---

### Minor Notes (ACC) — For Human Review

1. Section 5.2: "Spearman ρ on test: 0.1041" refers to the trained flat MLP (H-M1), but Table 2 shows the untrained flat MLP with ρ = 0.1688. This dual-ρ presentation is confusing — readers may conflate the two. A sentence explicitly reconciling these two numbers would help.
2. Section 3.5 mentions "Bootstrap CI uses 1,000 resamples" but does not specify whether the bootstrap is paired (it is paired per H-M3/04_validation.md). Paired bootstrap should be stated explicitly.
3. CI bounds: Abstract rounds CI to "[0.38, 0.64]" while ground truth is [0.3814, 0.6382]. The lower bound 0.38 rounds correctly; the upper bound 0.64 is slightly off (0.6382 rounds to 0.64). This is acceptable but worth verifying.
4. Section 6.3 L3 says "Single training seed [LOW]" but the limitation description says "A 5-seed ensemble would strengthen statistical rigor." Severity should perhaps be MEDIUM given the NFN ρ variance is unknown.

---

## PERSONA 2: Bored Reviewer Assessment

### Persuasiveness Checks

- **abstract_compelling**: true — The abstract leads with a concrete problem (capacity-confounded comparisons), states the specific mechanism result (885,000× sensitivity reduction), and gives the primary result (Δρ = 0.51, ten times threshold). The hook works. However, "ten times the minimum meaningful threshold" is jargon that requires the reader to already know what the threshold is.

- **problem_clear_in_1_minute**: true — The first paragraph of the Introduction clearly states the permutation orbit problem and why it matters. The factorial orbit size example (>10⁸³ configurations) is effective. The problem framing is tight.

- **novelty_clear_in_2_minutes**: true — By the end of the Introduction (Contributions list), it is clear that matched-capacity comparison with bootstrap CIs and a Deep Sets intermediate baseline are the three novel elements. The framing is crisp.

- **figure_1_self_explanatory**: false — Figure 1 caption reads: "Spearman ρ by accuracy decile for all three encoders (flat MLP, Deep Sets, NFN) at matched ~500K parameters. NFN shows strong performance in low-to-mid accuracy deciles, with a notable decline in the highest accuracy decile." This caption tells readers what to look for but does not describe what the figure actually shows (e.g., axis labels, whether lines or bars are used, what the x-axis deciles represent). A reviewer looking at the caption alone cannot determine the key finding (the high-accuracy tier inversion, or the NFN vs. Deep Sets gap). The caption should be extended to state the numerical takeaway.

- **would_continue_reading**: true — The abstract and introduction are well-written. The hook is not the generic "X is important because X is important" formulation; it leads with the empirical result.

- **attention_lost_at**: Results Section 5.4 — Upon reading Table 2 and seeing "Flat MLP (untrained)" in the baseline row, a bored reviewer will pause. An untrained model as the primary comparison baseline is deeply unusual. The paper explains this in Section 6.3 L2, but by then attention may be lost. There is no prominent warning when the table is first presented that the flat MLP baseline is untrained.

### FATAL Issues (BORED)

None — the paper is readable enough that no engagement failure rises to FATAL level. The attention loss at Table 2 is a major issue but not fatal.

### MAJOR Issues (BORED)

**BORED-MAJOR-01: Untrained flat MLP baseline disclosed only in table header — this will stop a reviewer cold**

- **ID**: BORED-MAJOR-01
- **Location**: Results Section 5.4, Table 2
- **Issue**: A reviewer spending 5 minutes on the paper will hit Table 2 and see "Flat MLP (untrained)" as the primary comparison baseline. There is no sentence in Section 5.4 that says "Note: the flat MLP in this comparison is evaluated at random weights because the trained checkpoint was unavailable." The parenthetical in the table label is the only disclosure at this point. A reviewer will immediately ask: "Why is an untrained model the baseline?" and may abandon the paper or give it a low score on methodology.
- **Required Fix**: Add an explicit sentence at the start of Section 5.4: "Important: the flat MLP encoder in Table 2 is evaluated with random (untrained) weights. The trained flat MLP from H-M1 (ρ = 0.1041) was unavailable due to checkpoint loading failure; both trained and untrained flat MLPs achieve similarly poor ρ in the 0.10–0.17 range (see Section 6.3), confirming the capacity waste mechanism is not training-dependent." This sentence should appear before the table, not after.

### Minor Notes (BORED) — For Human Review

1. The introduction's "more than atoms in the observable universe" analogy for 10⁸³ permutations is vivid but scientifically imprecise as a motivator (orbit size does not scale this way for the actual zoo models). Consider replacing with "an astronomically large search space."
2. Section 2.4 (Related Work) ends abruptly with a list of three differentiators — the transition to Section 3 would benefit from a bridging sentence.
3. The paper has no explicit "Paper Organization" sentence at the end of the Introduction contributions list — there is a brief "We organize the paper as follows" paragraph, which is good. Minor readability note: the section reference list is slightly mechanical.

---

## PERSONA 3: Skeptical Expert Findings

### FATAL Issues (SKEPT)

None — the core mechanism claim is real and the data support it. No genuinely impossible or fundamentally contradicted claim exists once the upper-bound nature of Δρ is disclosed.

### MAJOR Issues (SKEPT)

**SKEPT-MAJOR-01: "First matched-capacity controlled Δρ benchmark" — novelty claim may be overclaimed**

- **ID**: SKEPT-MAJOR-01
- **Location**: Introduction Contribution 1: "First matched-capacity controlled Δρ benchmark"
- **Issue**: The paper claims this is the "first" such benchmark. This is a strong claim that requires negative evidence: a literature search showing no prior work matched capacity. The Related Work (Section 2.3) cites Schurholt et al. [2023] as comparing "multiple encoder architectures on their zoo without capacity matching, bootstrap CIs, or a Deep Sets baseline" — this is the only direct competitor mentioned. However, the claim of "first" for a benchmark methodology requires a more comprehensive literature sweep. Additionally, the Deep Sets intermediate baseline on model zoo accuracy prediction is also claimed as novel (no prior benchmarking) — but Deep Sets has been applied to many set-based learning tasks; the claim should be more precise ("first on model zoo accuracy prediction" rather than implying Deep Sets has never been benchmarked in weight-space contexts).
- **Required Fix**: Add a paragraph in Related Work explicitly justifying the "first" claim by stating which specific papers were checked and why they do not qualify as capacity-matched comparisons. If the claim cannot be fully substantiated, downgrade from "first" to "first systematic" or "first with bootstrap CI validation and ±5% capacity matching."

**SKEPT-MAJOR-02: Flat MLP bottleneck — single narrow hidden layer at 500K may make Δρ=0.51 uninformative as an architectural comparison**

- **ID**: SKEPT-MAJOR-02
- **Location**: Section 3.2 (Flat MLP architecture), Section 6.3 (L2 limitation), Results 5.2
- **Issue**: The capacity-matched flat MLP uses hidden_dims=[193] for a 2,464-dimensional input. This is a single hidden layer of width 193, producing a severe information bottleneck. The architecture is arguably not a "fair" flat MLP baseline — it is a maximally constrained flat MLP forced into a single narrow layer by the parameter budget. A 500K-parameter budget with input_dim=2,464 could support [512, 256] or [512, 128] multi-layer architectures that would provide substantially stronger baselines. The paper acknowledges this in L2 but characterizes it as: "Both trained (ρ = 0.1041) and untrained (ρ = 0.1688) flat MLPs yield similarly poor predictions, but this near-equality itself suggests the bottleneck dominates over training." This argument is circular: the bottleneck may be why training has no effect, not evidence that a well-designed flat MLP would also fail.
- **Evidence**: Literature (Unterthiner et al. 2020) reports flat MLP achieving ρ ≈ 0.5–0.7, dramatically better than the 0.104 achieved here. The discrepancy is attributed to the bottleneck — but this means the reported Δρ = 0.51 may largely measure the cost of architectural constraints on the flat MLP, not the fundamental inductive bias advantage of equivariance.
- **Required Fix**: This is a known limitation (L2) and is disclosed, but its severity is understated. The paper should add: (a) an explicit estimate of what a [512, 256]-layer flat MLP might achieve at 500K params (even a theoretical calculation), and (b) a stronger caveat in the abstract or contributions stating "Δρ = 0.51 against a single-layer bottleneck flat MLP; advantage against a well-tuned multi-layer flat MLP may be smaller." Without this, reviewers will legitimately challenge the Δρ as reflecting flat MLP undertuning rather than equivariance advantage.

**SKEPT-MAJOR-03: Negative NFN ρ = −0.314 in high-accuracy tier is unexplained and potentially undermines the paper's utility claim**

- **ID**: SKEPT-MAJOR-03
- **Location**: Results Section 5.5, Table 3, Discussion Section 6.2
- **Issue**: NFN achieving ρ = −0.314 for the high-accuracy tier means it is actively anti-correlated with accuracy for the top third of models. The paper's explanation ("capacity-regime mismatch — 500K parameters may be insufficient") is speculative and not supported by additional experiments. A skeptical reviewer will note: if NFN anti-correlates for high-accuracy models in the primary zoo, its practical utility for model selection on competitive model zoos (where distinguishing well-trained models matters) is questionable. The paper frames this as an "unexpected finding" that "opens a new research direction" — but it could equally be framed as a failure mode of the proposed encoder that limits real-world applicability.
- **Required Fix**: The discussion of the negative ρ should be strengthened with at least: (a) an analysis of whether the anti-correlation is statistically significant (bootstrap CI for the tier-level ρ values are not reported), and (b) an honest statement that the practical utility of NFN for model selection among high-performing models remains undemonstrated. The implication that NFN is ready for "zero-shot model selection" (Introduction paragraph 2) should be qualified given the high-accuracy tier failure.

### Minor Notes (SKEPT) — For Human Review

1. The paper claims "ten times the minimum meaningful threshold" (for Δρ exceeding 0.05). The threshold of 0.05 is not justified in the methodology — it appears to be a pre-registered gate criterion, but its origin and justification (why 0.05 and not 0.1?) should be briefly stated in the paper.
2. Citations described in ground truth as "INFERRED" (not verified against Semantic Scholar) include Kofinas et al. (2023/2024) — the paper's reference list cites this as "ICLR 2024" but the text says "Kofinas et al., 2023." The year inconsistency should be resolved.
3. The NFN ρ = 0.68 is below the reported Navon et al. (2023) result of ρ ≈ 0.73. The paper attributes this to capacity control but does not provide a detailed comparison of the two experimental setups (Navon et al.'s dataset size, train/test split, zoo type). A table or footnote comparing the setups would strengthen the claim that the difference is due to capacity matching.
4. "Ten times the minimum meaningful threshold" is marketing language. "Exceeding the minimum threshold by a factor of 10" is more precise and appropriate for an ICML submission.

---

## Ground Truth Verification Log

| Claim | Paper Value | Ground Truth | Match |
|-------|-------------|--------------|-------|
| Δρ primary | "0.51" (abstract), "0.512" (intro), "0.5119" (results), "0.512" (conclusion) | 0.5119 | OK (rounding) |
| Δρ 95% CI lower | "0.381" | 0.3814 | OK |
| Δρ 95% CI upper | "0.638" | 0.6382 | OK |
| Abstract CI: "[0.38, 0.64]" | "[0.38, 0.64]" | [0.3814, 0.6382] | OK (rounded) |
| Flat MLP ρ (abstract, intro) | "0.17" | 0.1688 | OK |
| Flat MLP ρ (results table) | 0.1688 | 0.1688 | EXACT |
| Deep Sets ρ (abstract) | "0.45" | 0.4466 | OK |
| Deep Sets ρ (results table) | 0.4466 | 0.4466 | EXACT |
| NFN ρ (abstract) | "0.68" | 0.6806 | OK |
| NFN ρ (results table) | 0.6806 | 0.6806 | EXACT |
| Flat MLP sensitivity | 0.649 | 0.6490 | OK |
| NFN sensitivity | 7.34 × 10⁻⁷ | 7.34e-07 | EXACT |
| 885,000× reduction | "885,000×" | 885,000× | EXACT |
| Low-tier ρ | 0.856 | 0.8559 | OK (rounding) |
| Mid-tier ρ | 0.317 | 0.3169 | OK (rounding) |
| High-tier ρ | −0.314 | −0.3135 | OK (rounding) |
| Flat MLP params (Table 1) | 500,577 | 500,577 (H-M1) | EXACT |
| Flat MLP params (Table 2) | 500,706 | 500,706 (H-M3, untrained) | EXACT but inconsistent with Table 1 |
| NFN params | 521,953 | 521,953 | EXACT |
| Deep Sets params | 471,936 | 471,936 | EXACT |
| Test set n | 338 | 338 | EXACT |
| Bootstrap resamples | 1,000 | 1,000 | EXACT |
| orbit_proportion | 1.000 | 1.000 | EXACT |
| mean cosine distance | 0.768 | 0.768 (0.7677) | OK |
| H-E1 n_checkpoints | "2,249" (Section 4.2 claim) | 976 (H-E1 actual) | MISMATCH — FATAL |
| FlatMLP trained or untrained in H-M3 | "Flat MLP (untrained)" (Table 2 only) | Untrained (checkpoint not found) | Partially disclosed — FATAL |
| CIFAR-10 status | "Not executed (download failure)" | Not tested | OK |
| Sensitivity score threshold | "> 0.3 (exceeded 2.2×)" | threshold=0.3, 0.649/0.3=2.16× | OK |
| CI lower bound vs threshold | "7.6× the minimum threshold (0.05)" | 0.3814/0.05 = 7.63× | OK |
| Introduction sensitivity score | "0.649" | 0.6490 | OK |
| Deep Sets val loss | "0.0203" | 0.0203 | EXACT |
| NFN best checkpoint epoch | "epoch 114" | epoch 114 | EXACT |
| Deep Sets best epoch | "epoch 39" | epoch 39 | EXACT |

---

## Summary for Revision Agent

### Issues Requiring Immediate Fix (FATAL)

1. **ACC-FATAL-01**: Dataset size inconsistency — Section 4.2 claims 2,249-checkpoint hyp_rand zoo but H-E1 used 976-checkpoint seed-only zoo with different model architecture (Conv(8) vs Conv(32)-Conv(64)-FC(128)-FC(10)). **Required action**: Rewrite Section 4.2 to distinguish the two datasets used across the four sub-experiments. Add a paragraph or table mapping each hypothesis (H-E1, H-M1, H-M2, H-M3) to the dataset it actually used. Add an explicit limitation noting that orbit existence (H-E1) was measured on a smaller, architecturally different zoo than the one used for encoder training.

2. **ACC-FATAL-02**: Primary result Δρ=0.51 presented without "upper bound" qualifier in abstract, contributions, and conclusion despite being computed against an untrained flat MLP. **Required action**: Add "(untrained flat MLP baseline; see Section 6.3)" immediately after every abstract/contribution/conclusion statement of Δρ=0.51. Add one sentence in the abstract stating the upper bound nature. Add a prominent warning sentence at the start of Results Section 5.4 before Table 2 is presented.

### Issues Requiring Fix (MAJOR)

1. **ACC-MAJOR-01**: Flat MLP parameter count differs between Table 1 (500,577) and Table 2 (500,706) with no explanation. **Required action**: Add a footnote to Table 2 explaining that the untrained flat MLP (500,706) is a distinct instance from the trained H-M1 model (500,577), and explain the minor parameter count difference.

2. **ACC-MAJOR-02**: Δρ value reported at three different precision levels (0.51, 0.512, 0.5119) across sections. **Required action**: Standardize to 0.512 everywhere except abstract (where 0.51 is acceptable for space); add a parenthetical in Results noting the abstract rounding.

3. **ACC-MAJOR-03**: H-E1 used architecturally different zoo (Conv(8), 976 checkpoints) from H-M1/M2/M3 (Conv(32)-Conv(64), 2,249 checkpoints) — not disclosed. **Required action**: Disclose this as an explicit limitation in Section 5.1 and Section 6.3. The causal chain argument relies on orbit existence in the same zoo the encoders are trained on; this cross-zoo gap must be acknowledged.

4. **BORED-MAJOR-01**: Untrained baseline not disclosed until the table header in Section 5.4. **Required action**: Add an explicit warning sentence at the beginning of Section 5.4 Results before Table 2.

5. **SKEPT-MAJOR-01**: "First" novelty claim insufficiently justified in Related Work. **Required action**: Add explicit negative evidence showing no prior capacity-matched comparisons exist.

6. **SKEPT-MAJOR-02**: Single-layer bottleneck flat MLP severely limits the validity of Δρ as an architectural comparison. **Required action**: Strengthen L2 limitation disclosure; add qualifier to abstract contributions.

7. **SKEPT-MAJOR-03**: Bootstrap CIs not reported for tier-level ρ values; high-accuracy anti-correlation (ρ = −0.314) is under-analyzed. **Required action**: Compute and report bootstrap CIs for Table 3 tier ρ values. Add sentence qualifying practical utility of NFN for high-accuracy model selection.

### Minor Notes to Collect (not blocking)

1. The threshold of 0.05 for Δρ is not justified in the paper — add one sentence citing its origin.
2. Kofinas et al. year inconsistency: text says "2023" but reference list says "ICLR 2024." Resolve.
3. "Ten times the minimum meaningful threshold" should be replaced with "exceeds the minimum threshold by a factor of 10."
4. Bootstrap should be specified as "paired bootstrap" (consistent with H-M3/04_validation.md).
5. Tier-level ρ values in Table 3 lack confidence intervals — notable for a paper that emphasizes bootstrap CI rigor.
6. Figure 1 caption is insufficiently self-explanatory — add numerical takeaway to the caption.

### Issue Counts
- **fatal_count**: 2
- **major_count**: 6 (including BORED-MAJOR-01 and SKEPT-MAJOR-01/02/03)
- **minor_count**: 6 (for human review, not blocking)
- **ground_truth_discrepancies**: 2 (dataset size mismatch ACC-FATAL-01; parameter count inconsistency ACC-MAJOR-01)
- **persuasiveness_passed**: true (abstract is compelling; attention loss occurs only at Table 2 upon discovering untrained baseline)
