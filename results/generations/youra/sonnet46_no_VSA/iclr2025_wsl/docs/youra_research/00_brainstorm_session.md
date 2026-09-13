---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Weight Space Learning — Architecturally Invariant Encoders for Model Zoo Performance Prediction"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-03
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Neural network weights as a new data modality — designing architecturally permutation-invariant weight encoders (DeepSets / Neural Functional Networks) to eliminate within-orbit variance at the encoder level, replacing failed post-hoc alignment approaches, and testing whether invariant encoding improves downstream model performance prediction on existing model zoo benchmarks.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — 3rd attempt, learning from h-m1 + sh1 + sh2)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

The recent surge in publicly available neural network models (exceeding 1 million on Hugging Face) calls for treating neural network weights as a first-class data modality. Key research dimensions include: weight space properties (symmetries, permutations, scaling), weight space learning paradigms (supervised: weight embeddings, meta-learning, hyper-networks; unsupervised: autoencoders, hyper-representations), theoretical foundations (expressivity, generalization bounds), model/weight analysis (inferring properties, interpretability), model/weight synthesis (generation, model merging, task arithmetic), and applications (NeRFs/INRs, physics modeling, backdoor detection).

Source Type: Workshop CFP / Structured Input (ICLR 2025 Workshop on Neural Network Weights as a New Data Modality)

**ROUTE_TO_0 Context:** Three experiments completed. sh1 PASS (CISE PE is NOT invariant, OrbitVar > 0.01 confirmed). h-m1 FAIL (quantile encoders are mathematically invariant — aliasing impossible). sh2 FAIL (Hungarian LAP alignment is cross-model, cannot reduce within-orbit OrbitVar). New direction: achieve permutation-invariance architecturally inside the encoder (not post-hoc), then validate downstream utility.

---

## Lessons from Previous Attempts

### What Was Tried (Three Runs)

**h-m1 (FAIL — MATHEMATICAL_INVARIANCE):**
Hypothesis: Per-layer quantile features exhibit permutation aliasing (OrbitVar > threshold) under S_16³ channel permutations.
Result: OrbitVar = 1.24e-33 (machine epsilon). Quantile encoders are order statistics — provably permutation-invariant by construction. Aliasing is mathematically impossible.

**sh1 (PASS — MUST_WORK):**
Hypothesis: CISE encoder with sinusoidal positional encoding exhibits non-zero within-orbit variance (OrbitVar > 0.01) under S_16³ channel permutations.
Result: mean OrbitVar(CISE) = 0.010333 ✓. Sinusoidal PE formula sin(cπ/C), cos(cπ/C) breaks permutation symmetry — the CISE encoder IS sensitive to channel order. This is the baseline: an encoder that has measurable aliasing.

**sh2 (FAIL — MUST_WORK_FAIL):**
Hypothesis: Hungarian LAP alignment (scipy.optimize.linear_sum_assignment) reduces OrbitVar(CISE) by ≥100× (from >0.01 to <0.0001).
Result: mean OrbitVar(CISE_aligned) = 0.010325. Reduction ratio: 1.0×. Root cause: OrbitVar measures **within-model** orbit variance; Hungarian alignment is a **cross-model** operation. They are orthogonal — alignment cannot reduce within-orbit variance by construction.

### How This New Direction Avoids Those Pitfalls

1. **No post-hoc alignment:** sh2 definitively proved post-hoc cross-model alignment (LAP/Hungarian) cannot reduce within-orbit OrbitVar. This class of approaches is ruled out.
2. **No order-statistic encoders:** h-m1 definitively proved quantile/sorted-feature encoders are permutation-invariant. This class is ruled out for aliasing experiments.
3. **Encoder-level architectural invariance instead:** Use architecturally permutation-invariant encoders (DeepSets-style sum/mean pooling across channels, Neural Functional Networks) that achieve OrbitVar ≈ 0 by design. Verify architecturally before running experiments.
4. **Reuse working infrastructure:** sh1's ModelZooDataset CIFAR10-GS pipeline, OrbitVar metric, and LightGBM HP framework are all validated and reusable.
5. **Correct comparison frame:** The question is now: does replacing the non-invariant CISE encoder (OrbitVar = 0.01) with an architecturally invariant encoder (OrbitVar ≈ 0) improve downstream model performance prediction (R²)? This is a clean, testable, binary comparison.

---

## Session Plan

ROUTE_TO_0 auto-extraction from three failure/completion records (Serena Memory: failure_h-m1_run1, failure_sh2_run1, snapshot_sh1_2026-08-03) merged with current ICLR 2025 WSL workshop CFP input. Research question redesigned to target encoder-level architectural invariance, avoiding both (a) order-statistic invariance traps and (b) post-hoc alignment orthogonality traps.

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions. Three failure/completion records applied to redesign hypothesis direction. Key inference: both known approaches to "removing" permutation sensitivity (order statistics = trivially invariant; post-hoc alignment = orthogonal to OrbitVar) have failed. The remaining valid approach is architectural permutation-invariance inside the encoder.

---

## Research Question Development

### Initial Question

Does replacing the non-invariant CISE sinusoidal PE encoder (OrbitVar = 0.010333) with an architecturally permutation-invariant encoder (DeepSets-style or NFN-style) reduce within-orbit variance to OrbitVar < 0.001, and does this invariant encoding improve model performance prediction accuracy on existing model zoo benchmarks?

### Refined Question

Can an **architecturally permutation-invariant weight encoder** (e.g., DeepSets-style channel-wise pooling or Neural Functional Network layer) achieve OrbitVar < 0.001 on ModelZooDataset CIFAR10-GS under S_16³ channel permutations — and does this invariant encoding produce higher LightGBM prediction R² for model test accuracy compared to the non-invariant CISE baseline (OrbitVar = 0.010333), using only existing datasets and benchmarks?

### Detailed Sub-Questions

1. Does a DeepSets-style encoder (per-channel statistics → sum/mean pool across channels) achieve OrbitVar < 0.001 under S_16³ channel permutations on ModelZooDataset CIFAR10-GS, confirming architectural permutation-invariance?
2. Does this invariant encoder produce LightGBM model performance prediction R² that is statistically higher than the CISE encoder baseline (R² from sh1 experimental infrastructure) on held-out test accuracy labels?
3. Is the improvement in R² attributable to variance reduction: does the invariant encoder's lower within-orbit variance (OrbitVar) correlate with reduced prediction variance across permuted representations of the same model?
4. Does a more expressive invariant encoder (e.g., Neural Functional Network / neural functional layer operating on weight matrices directly) achieve both lower OrbitVar and higher prediction R² than the simpler DeepSets pooling baseline?
5. Is the invariance-utility trade-off monotone: does reducing OrbitVar (via architectural choices) monotonically improve prediction R², or is there an optimal operating point where some sensitivity to weight structure improves prediction?

---

## Reference Papers

Not provided — will discover in Phase 1

Key search targets:
- DeepSets (Zaheer et al. 2017) — permutation-invariant set functions via sum/mean pooling
- Neural Functional Networks / NFN (Zhou et al. 2023) — equivariant/invariant architectures for weight spaces
- DWSNet / Deep Weight Space Networks (Navon et al. 2023) — graph-based permutation-equivariant weight encoders
- ModelZooDataset (Unterthiner et al. 2020) — model zoo with accuracy labels (used in h-m1/sh1)
- Hyper-representations (Schürholt et al. 2022) — weight space autoencoders
- Model performance prediction from weights survey (Eilertsen et al. 2020)
- CISE encoder reference (from sh1 experimental code)
- OrbitVar metric: within-orbit variance for symmetry quantification

---

## Validation Results

### So What Test

Permutation symmetry in weight spaces is a fundamental obstacle to reliable model analysis: functionally identical networks (related by channel permutations) have different weight representations, causing distance metrics and downstream ML models to see artificial variance. Two prior experiments confirmed:
- The CISE encoder has measurable aliasing (OrbitVar = 0.010333) — this is the problem
- Post-hoc alignment cannot fix within-orbit aliasing — the community needs encoder-level solutions

Demonstrating that an architecturally invariant encoder (a) eliminates within-orbit aliasing and (b) improves prediction accuracy provides:
- Concrete empirical evidence for the practical benefit of architectural invariance in weight space learning
- A clear recommendation for practitioners: use invariant architectures (DeepSets/NFN), not post-hoc alignment
- A reusable OrbitVar benchmark protocol for comparing encoder designs — directly relevant to ICLR WSL community

### Feasibility Check

✅ FEASIBLE under mandatory constraints:

- **Existing datasets:** ModelZooDataset CIFAR10-GS (validated in h-m1/sh1/sh2 — data pipeline confirmed working, record 6620869, file `dataset_cifar_small_hyp_rand.pt`), Unterthiner et al. 2020 (publicly available)
- **Existing benchmarks:** Standard test accuracy prediction (R²) — same metric used in all previous runs, no new benchmark
- **Encoder validity:** DeepSets sum/mean pooling is provably permutation-invariant (mathematical guarantee: pool(permute(x)) = pool(x) for symmetric aggregation). NFN layers maintain equivariance by construction (Zhou et al. 2023). Both can be verified analytically before running.
- **Baseline comparison:** sh1 established CISE OrbitVar = 0.010333 and ran LightGBM on same dataset — provides direct baseline R² for comparison without additional experiments
- **OrbitVar metric:** Correctly implemented and validated in sh1/sh2 (not the source of failures)
- **LightGBM pipeline:** Reusable from h-m1/sh1 (HP search framework confirmed working)
- **No human evaluation:** Fully automated (prediction vs. ground-truth test accuracy)
- **No synthetic data:** All weights from real trained models in ModelZooDataset
- **No new benchmarks:** Uses pre-existing accuracy labels from model zoo datasets
- **No new rubrics:** OrbitVar threshold (< 0.001) derived from sh1 baseline (0.010333) — 10× reduction target

**Critical pre-experiment gate (avoids sh2 failure mode):**
Before running full experiment, verify: for a single sample model, `encoder(permute(W)) == encoder(W)` (within numerical tolerance) for the proposed invariant encoder. This unit test must pass before Phase 2A hypothesis generation.

**Critical pre-experiment gate (avoids h-m1 failure mode):**
Confirm the proposed encoder is NOT trivially invariant for the WRONG reason (e.g., it should not reduce to order statistics). Verify: `encoder(W)` uses symmetric pooling over channels — not sorting.

---

## Phase 1 Input Package

<phase1-input>

### research_question
Does an architecturally permutation-invariant weight encoder (DeepSets-style channel pooling or Neural Functional Network layer) achieve OrbitVar < 0.001 under S_16³ channel permutations on ModelZooDataset CIFAR10-GS — and does this invariant encoding improve LightGBM model performance prediction R² compared to the non-invariant CISE encoder baseline (OrbitVar = 0.010333), using only existing datasets and benchmarks?

### detailed_question
1. Does a DeepSets-style encoder (per-channel statistics aggregated via sum/mean pooling) achieve OrbitVar < 0.001 under S_16³ channel permutations on ModelZooDataset CIFAR10-GS, confirming architectural permutation-invariance?
2. Does this invariant encoder produce LightGBM prediction R² statistically higher than the CISE encoder baseline on held-out model test accuracy labels from the same dataset?
3. Is reduced prediction variance (across permuted representations of the same model) the mechanistic driver of improved R²?
4. Does a more expressive NFN-style invariant encoder achieve both lower OrbitVar and higher R² than the simpler DeepSets baseline?
5. Is the invariance-utility trade-off monotone, or is there an optimal OrbitVar operating point that balances invariance and expressivity for prediction accuracy?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Three experiments have systematically eliminated two major classes of approaches: (1) order-statistic encoders (trivially invariant, no aliasing possible) and (2) post-hoc cross-model alignment (orthogonal to within-orbit OrbitVar)
- The remaining valid approach space is: encoder-level architectural invariance (DeepSets, NFN, equivariant architectures)
- sh1's CISE result (OrbitVar = 0.010333) provides the concrete baseline to beat — new encoder must achieve < 0.001
- sh1's LightGBM R² provides the downstream accuracy baseline — new encoder must improve it
- The entire data pipeline (ModelZooDataset CIFAR10-GS), metric (OrbitVar), and downstream model (LightGBM HP search) are validated and reusable
- The key architectural insight from the literature (DeepSets, NFN) is that permutation-invariance requires symmetric aggregation inside the encoder, not external post-processing

### Techniques Used

ROUTE_TO_0 Mode (multi-failure context analysis + structured input extraction):
- Failure root-cause analysis: failure_h-m1_run1 (mathematical invariance), failure_sh2_run1 (orthogonality trap)
- Completion snapshot analysis: snapshot_sh1_2026-08-03 (baseline values, reusable code)
- Previous brainstorm review: archived 00_brainstorm_session.md (20260803T164022)
- Current input extraction: ICLR 2025 WSL workshop CFP
- Merge strategy: eliminate ruled-out approaches → narrow to architecturally invariant encoders → frame as clean A/B comparison against sh1 baseline

### Areas for Further Exploration

- NFN expressivity theorem: theoretical bounds on what invariant weight encoders can represent vs. non-invariant ones
- Layer-permutation aliasing: quantile encoders ARE sensitive to layer reordering — valid orthogonal direction
- Model merging in weight space: how does encoder invariance affect merge quality (task arithmetic)?
- Weight space augmentation: random permutations as augmentation during training of downstream models
- Scaling: does the invariance-utility trade-off change with model zoo size (number of models) or model size (number of parameters)?
- Backdoor detection: does permutation-invariant encoding change backdoor detection accuracy?

---

## Next Steps

Proceed to Phase 1 - Targeted Research: `/phase1-targeted`

**Priority search targets for Phase 1:**
1. DeepSets (Zaheer et al. 2017) — theoretical foundation for permutation-invariant encoders
2. Neural Functional Networks (Zhou et al. 2023) — state-of-the-art invariant/equivariant weight encoders
3. DWSNet (Navon et al. 2023) — graph-based equivariant weight space networks
4. ModelZooDataset benchmark papers (Unterthiner et al. 2020; Eilertsen et al. 2020) — confirm available accuracy labels and dataset access
5. Hyper-representations (Schürholt et al. 2022) — weight space autoencoders: check invariance properties
6. Any existing comparison of invariant vs. non-invariant weight encoders on performance prediction

**Mandatory pre-Phase-2A gates (from accumulated failure lessons):**
1. **Anti-sh2 gate:** Confirm proposed encoder achieves `encoder(permute(W)) == encoder(W)` (within tolerance) for a single test case before full experiment
2. **Anti-h-m1 gate:** Confirm encoder does NOT reduce to order statistics (verify pooling is symmetric, not sorting-based)
3. **Baseline R² recorded:** Record sh1 LightGBM R² from experimental logs before Phase 2A — this is the comparison target

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
