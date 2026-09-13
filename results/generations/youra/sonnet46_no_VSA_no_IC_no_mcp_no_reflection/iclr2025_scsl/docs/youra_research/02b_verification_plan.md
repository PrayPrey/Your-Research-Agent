---
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
status: complete
hypothesis_id: H-GAD-v1
generated_at: "2026-08-31"
completedAt: "2026-08-31"
---

# Verification Plan: Gradient Alignment Debiasing (GAD)

**Date:** 2026-08-31
**Hypothesis ID:** H-GAD-v1
**Confidence:** 0.72
**Total Hypotheses:** 6

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard ERM training on spurious correlation benchmarks (Waterbirds, CelebA, MultiNLI) with random mini-batch sampling, if we compute the cosine similarity between per-sample last-layer gradients and the batch-mean gradient at each training step and use the EMA-smoothed inverse alignment score as an online importance weight, then the trained model will achieve better worst-group accuracy than JTT and LfF baselines, because gradient alignment direction specifically captures spurious-minority membership (conflicting gradient direction with majority batch) in a way that magnitude-based proxies cannot distinguish from hard-but-spurious-majority samples.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in worst-group accuracy on Waterbirds and CelebA between ERM training with gradient-alignment-based online upweighting and JTT baseline training (two-sided test, significance level α = 0.05 across 3 random seeds).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds + CelebA (primary); MultiNLI (secondary) — standard | Canonical spurious correlation benchmarks with existing group annotations enabling annotation-free training and annotation-based evaluation; all comparison methods report on these. |
| **Model** | ResNet-50 (vision); BERT-base (NLI) | Standard backbone for Waterbirds/CelebA; last-layer (2048×2) gradient computation feasible with torch.func.vmap at batch_size=32. |

**Dataset Details:**
- Source: Sagawa et al. 2020 Group DRO paper; Koh et al. 2021 WILDS
- Path: Available via kohpangwei/group_DRO repository (standard download scripts)

**Model Details:**
- Type: Standard pretrained classifier
- Source: torchvision.models.resnet50(pretrained=True); huggingface/bert-base-uncased

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| ERM (ResNet-50) | 72.6% worst-group accuracy | Waterbirds |
| JTT (Liu et al. 2021) | 86.7% worst-group accuracy | Waterbirds |
| LfF (Nam et al. 2020) | 78.0% worst-group accuracy | Waterbirds |
| DFR (Kirichenko et al. 2022) | 91.8% worst-group accuracy (requires labels — ceiling) | Waterbirds |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Spurious-minority samples are statistical minority in random mini-batches (Waterbirds 18%, CelebA ~6%) | Sagawa et al. 2020 group statistics; standard random sampling maintains ratios | Alignment signal loses specificity; method breaks for balanced batching |
| A2 | Last/penultimate-layer gradient alignment feasible with vmap on ResNet-50, batch≤32 | Last layer: 2048×2=4096 params; 32×4096=131K floats; vmap supports linear layers | OOM on penultimate layer; must use gradient checkpointing or last-layer only |
| A3 | EMA β=0.9 provides stable smoothing without excessive lag | Standard for importance weight smoothing; effective window ≈10 steps | β too high: intervention too late; β too low: training instability |
| A4 | Per-sample last-layer gradient computable without group labels | Cross-entropy gradient requires only network prediction + true class label | Method not truly annotation-free; Experiment 1 validates this |
| A5 | Worst-group accuracy on standard test splits is valid and sufficient evaluation criterion | Standard from Sagawa et al. 2020; used by all comparison methods | Improvement attributable to regularization not alignment mechanism |

### 1.6 Research Gap & Novelty

**Gap:** No existing annotation-free debiasing method uses gradient cosine similarity (directional information) as a training-time proxy for spurious-minority membership. JTT and LfF use magnitude-based signals (misclassification, high relative loss), which conflate hard-but-spurious-majority samples with spurious-minority samples.

**Innovation:** Gradient Alignment Debiasing (GAD): online importance weighting based on per-sample last-layer gradient cosine similarity with batch mean. Single-training-run (online), no second stage. Directional signal correctly distinguishes hard-but-spurious-majority (aligned gradients) from spurious-minority (conflicting gradients).

**Scope Reduction:** 67% of claims are BUILD_ON (established by prior work). Only 2 PROVE_NEW claims require experimental verification: (1) alignment ROC-AUC > loss ROC-AUC, (2) online GAD improves worst-group accuracy over JTT.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |
| H-C1 | CONDITION | SHOULD_WORK | H-M4 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Gradient Alignment Signal Predicts Spurious-Minority Membership**

**Statement:** Under standard ERM training on Waterbirds and CelebA with random mini-batch sampling, if we compute per-sample last-layer gradient cosine similarity with the batch-mean gradient at epochs {1, 5, 10, 25, 50}, then gradient alignment ROC-AUC for predicting spurious-minority group membership exceeds per-sample loss ROC-AUC at ≥1 epoch on BOTH datasets, because spurious-minority samples cannot be classified via the spurious feature and thus produce gradients conflicting with the majority batch direction.

**Rationale:** This is the foundational existence test — it validates the core PROVE_NEW claim (claim 5) that the alignment signal is a meaningful proxy. Without this, the intervention hypothesis (H-M3) has no mechanistic basis. If P1 fails, the method is not a mechanistic advance.

**Variables:**
- Independent: Training epoch (1, 5, 10, 25, 50) as time axis
- Dependent: ROC-AUC of alignment score and loss score for predicting spurious-minority membership
- Controlled: ResNet-50 pretrained, standard ERM training, batch_size=32, 3 seeds

**Verification Protocol:**
1. Train ERM ResNet-50 on Waterbirds and CelebA with kohpangwei/group_DRO standard settings.
2. At epochs {1, 5, 10, 25, 50}, compute per-sample last-layer cosine similarity with batch mean and per-sample loss for all training samples.
3. Use existing group annotations to label each sample as spurious-minority (1) or not (0).
4. Compute ROC-AUC of alignment score and loss score for each epoch on both datasets.
5. Compare ROC-AUC curves; success if alignment > loss at ≥1 epoch on both Waterbirds and CelebA.

**Success Criteria (PoC):**
- Primary: Alignment ROC-AUC > loss ROC-AUC at ≥1 epoch on BOTH Waterbirds AND CelebA
- Secondary: ROC-AUC > 0.6 threshold indicates meaningful predictive power

**Failure Response:**
- IF fails: PIVOT — restate novelty claim; GAD may still be useful as regularization variant but mechanistic advance claim fails

**Dependencies:** None (foundation)

**Source:** Phase 2A PROVE_NEW claim 5; Prediction P1; sh1_existence

---

**H-M1: Spurious-Majority Batch Domination Produces Alignment-Predictive Signal**

**Statement:** Under standard ERM training on Waterbirds (82% majority) with random batches, if we track per-sample last-layer gradient contribution and batch-mean gradient direction in early training epochs (1-10), then spurious-majority sample gradients align with the batch mean while spurious-minority sample gradients conflict with it (cosine similarity distribution separation between groups), because batch-mean gradient encodes the spurious feature direction when majority dominates.

**Rationale:** This tests causal step 1 of the mechanism: that batch domination by spurious-majority samples creates the alignment signal. H-E1 establishes the signal exists; H-M1 validates the mechanistic reason. It is MUST_WORK because the causal chain collapses without this step.

**Variables:**
- Independent: Sample group membership (spurious-majority vs spurious-minority)
- Dependent: Distribution of cosine similarity scores between per-sample gradient and batch-mean gradient
- Controlled: Early training epochs only (1-10); ResNet-50; standard batch_size=32

**Verification Protocol:**
1. From H-E1 training runs, extract per-sample cosine similarity scores at epochs 1 and 5.
2. Separate scores by group membership (spurious-majority vs spurious-minority) using group annotations.
3. Compute distribution statistics (mean, std) and effect size (Cohen's d) for the two groups.
4. Test that spurious-minority group has significantly lower mean cosine similarity (one-sided t-test, α=0.05).
5. Visualize score distributions to confirm separation rather than just mean difference.

**Success Criteria (PoC):**
- Primary: Spurious-minority mean cosine similarity < spurious-majority mean (statistically significant, p<0.05)
- Secondary: Cohen's d > 0.5 (medium effect size minimum)

**Failure Response:**
- IF fails: PIVOT — step 1 mechanism fails; alignment signal is not caused by batch domination

**Dependencies:** H-E1

**Source:** Phase 2A causal step 1; Section 1.3

---

**H-M2: Spurious-Minority Gradient Conflict Produces Low Cosine Similarity**

**Statement:** Under standard ERM training on Waterbirds and CelebA, if spurious-minority samples (e.g., landbirds on water) cannot be classified via the spurious feature (background), then their per-sample last-layer gradient direction at early training epochs conflicts with the batch-mean gradient (low cosine similarity), because their classification requires encoding the core feature which is opposite to the dominant spurious direction.

**Rationale:** This validates causal step 2 — the mechanistic reason why the signal is directional rather than magnitude-based. It explains why JTT's loss-based signal conflates hard-spurious-majority with spurious-minority (both have high loss) while alignment does not (hard-spurious-majority has high loss AND high alignment).

**Variables:**
- Independent: Sample type (spurious-minority vs hard-spurious-majority vs easy-majority)
- Dependent: Cosine similarity value; per-sample loss value
- Controlled: ResNet-50; epochs 1-10; Waterbirds + CelebA

**Verification Protocol:**
1. Segment training samples into: spurious-minority, hard-spurious-majority (misclassified majority), easy-majority.
2. For each segment, compute mean cosine similarity and mean loss at epochs 1, 5, 10.
3. Verify: spurious-minority has LOW alignment AND HIGH loss; hard-spurious-majority has HIGH alignment AND HIGH loss.
4. This 2×2 pattern (alignment × loss) demonstrates the directional signal discriminates where magnitude cannot.
5. Report confusion matrix comparing alignment-based vs loss-based segmentation accuracy against group annotations.

**Success Criteria (PoC):**
- Primary: Spurious-minority and hard-spurious-majority have similar loss but different alignment (alignment separates them; loss does not)
- Secondary: Alignment-based classification of spurious-minority has higher F1 than loss-based classification

**Failure Response:**
- IF fails: EXPLORE — alignment may still be useful even if exact mechanism differs; document finding

**Dependencies:** H-M1

**Source:** Phase 2A causal step 2; DFR finding (Kirichenko 2022) cited in evidence

---

**H-M3: EMA-Smoothed Inverse Alignment Upweighting Shifts Training Distribution**

**Statement:** Under standard ERM training on Waterbirds and CelebA, if we apply EMA-smoothed (β=0.9) inverse alignment score as online importance weights (clip max 5×), then the effective training distribution shifts toward the spurious-minority group as measured by the weighted group proportions during training, because samples with low alignment (spurious-minority) receive higher weights continuously throughout training.

**Rationale:** This validates causal step 3 — that the online upweighting actually changes the training dynamics. The DFR finding (Kirichenko 2022) shows last-layer reweighting toward minority restores worst-group accuracy; H-M3 tests whether online EMA-based reweighting produces this shift without access to group labels.

**Variables:**
- Independent: Training step; presence/absence of EMA upweighting
- Dependent: Effective weighted proportion of spurious-minority samples per batch; Hessian dominant eigenvectors (optional)
- Controlled: β=0.9; clip_max=5.0; ResNet-50; same data order

**Verification Protocol:**
1. Train GAD (ERM + online alignment upweighting) and record the effective importance weights for each sample per epoch.
2. Compute effective group proportions: sum(weights × group_indicator) / sum(weights) per training step.
3. Compare effective minority proportion under GAD vs uniform (ERM) — GAD should increase minority proportion.
4. Track whether the shift is early (epochs 1-10) vs late — earlier shift should predict better worst-group accuracy.
5. Compare GAD vs ERM+L2 effective distributions to rule out regularization confound.

**Success Criteria (PoC):**
- Primary: Effective spurious-minority proportion under GAD weights > ERM (uniform weights) at epochs 1-10
- Secondary: Shift is larger in early training than late training (consistent with online mechanism)

**Failure Response:**
- IF fails: EXPLORE — intervention may work through different mechanism; document and continue to H-M4

**Dependencies:** H-M2

**Source:** Phase 2A causal step 3; A3 (EMA stability assumption)

---

**H-M4: Online Single-Pass GAD Achieves ≥ JTT Worst-Group Accuracy**

**Statement:** Under standard ERM training on Waterbirds and CelebA with random mini-batch sampling, if we train a single GAD run (ERM + online EMA-smoothed inverse alignment upweighting, β=0.9, clip_max=5.0) and compare against JTT (two-stage, T_1=60, λ=100), then GAD achieves worst-group accuracy ≥ JTT on BOTH datasets averaged across 3 random seeds, because online continuous upweighting with directional signal occurs earlier and more precisely than JTT's binary two-stage misclassification signal.

**Rationale:** This is the core PROVE_NEW claim 6 — the intervention hypothesis. H-E1 through H-M3 build the mechanistic case; H-M4 tests whether the mechanism produces the claimed performance benefit. This is the direct falsification of H0.

**Variables:**
- Independent: Training method (GAD-last, JTT, LfF, ERM, ERM+L2)
- Dependent: Worst-group accuracy on standard test splits (mean ± std, 3 seeds)
- Controlled: ResNet-50 ImageNet pretrained; same LR schedule as JTT baseline; batch_size=32; same datasets

**Verification Protocol:**
1. Train GAD (single run: ERM + online alignment upweighting) on Waterbirds and CelebA, 3 seeds.
2. Train JTT baseline (from anniesch/jtt) on same datasets with standard hyperparameters (T_1=60, λ=100), 3 seeds.
3. Train LfF and ERM baselines for full comparison table.
4. Report worst-group accuracy on standard test splits (mean ± std across 3 seeds) for all methods.
5. Test H0 rejection: two-sided t-test (GAD vs JTT, α=0.05) on 3-seed worst-group accuracy.

**Success Criteria (PoC):**
- Primary: GAD worst-group accuracy ≥ JTT on BOTH Waterbirds AND CelebA (within or outside error bars)
- Secondary: GAD > LfF (stronger comparison since LfF < JTT on Waterbirds)

**Failure Response:**
- IF fails: PIVOT — if H-E1 held but H-M4 fails, GAD exists mechanistically but doesn't translate to performance; explore hyperparameter sensitivity (β, clip_max)

**Dependencies:** H-M3

**Source:** Phase 2A PROVE_NEW claim 6; Prediction P2; sh2_mechanism

---

**H-C1: GAD Alignment Signal Degrades Under Class-Balanced Batching**

**Statement:** Under modified ERM training on Waterbirds with class-balanced mini-batch sampling (equal class proportions per batch), if we compute the same GAD alignment signal, then gradient alignment ROC-AUC for predicting spurious-minority membership drops significantly (≤0.55) compared to random sampling (>0.6), because class-balanced batching equalizes the batch-mean gradient direction, eliminating the spurious-majority dominance that creates the alignment signal.

**Rationale:** This boundary condition test (optional but informative) validates scope claim in A1 — the method is specifically designed for random sampling. Confirming this boundary sharpens the paper's scope claims and validates the mechanistic explanation (if balanced batching eliminates the signal, it confirms the mechanism is batch-majority-driven).

**Variables:**
- Independent: Mini-batch sampling strategy (random vs class-balanced)
- Dependent: Gradient alignment ROC-AUC for spurious-minority prediction
- Controlled: ResNet-50; Waterbirds; epochs {1, 5, 10}; same model initialization

**Verification Protocol:**
1. Train ERM ResNet-50 on Waterbirds with class-balanced sampling (equal class batches); track alignment signal.
2. At epochs {1, 5, 10}, compute alignment ROC-AUC using same procedure as H-E1.
3. Compare ROC-AUC: random-sampling (from H-E1) vs class-balanced — expect significant drop.
4. Quantify the boundary: at what minority proportion does signal degrade (optional sweep)?
5. Document as scope limitation with specific ROC-AUC values.

**Success Criteria (PoC):**
- Primary: Class-balanced alignment ROC-AUC ≤ 0.55 at all epochs (vs random-sampling ≥ 0.6 from H-E1)
- Secondary: Absolute drop > 0.1 ROC-AUC points between random and balanced sampling

**Failure Response:**
- IF fails: EXPLORE — if signal persists under balanced batching, mechanism is more robust than claimed; document as positive finding

**Dependencies:** H-M4

**Source:** Phase 2A scope.does_not_apply_to (class-balanced batching); A1 violation scenario

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Alignment ROC-AUC > loss ROC-AUC at ≥1 epoch on both datasets | STOP — mechanistic novelty claim fails |
| H-M1 | MUST_WORK | Spurious-minority mean cosine similarity < majority (p<0.05) | PIVOT — causal step 1 mechanism fails |
| H-M2 | SHOULD_WORK | Alignment separates spurious-minority from hard-majority; loss does not | EXPLORE — document mechanistic finding |
| H-M3 | SHOULD_WORK | Effective minority proportion under GAD weights > ERM | EXPLORE — alternative mechanism possible |
| H-M4 | SHOULD_WORK | GAD worst-group ≥ JTT on both Waterbirds and CelebA | PIVOT — tune hyperparameters (β, clip_max) |
| H-C1 | SHOULD_WORK | Balanced-batch alignment ROC-AUC ≤ 0.55 | EXPLORE — stronger robustness than claimed |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks (1+1+1+2) |
| Phase 2.5: Conditions | H-C1 | 1 week |

**Total Duration:** 8 weeks

---

## 4. Risk Analysis

### 4.1 Risk Identification

**R1 (from A1): Batch Composition Signal Loss**
- Source: A1 — spurious-minority must be statistical minority in batches
- Description: If class-balanced batching used, or if minority proportion is higher than expected, alignment signal loses specificity
- Severity: High
- Likelihood: Low (standard random sampling used on canonical benchmarks)
- Affected Hypotheses: H-E1, H-M1

**R2 (from A2): GPU Memory / vmap OOM**
- Source: A2 — vmap feasibility at batch_size≤32
- Description: torch.func.vmap may OOM on penultimate layer (2048-dim activations × batch_size=32)
- Severity: Medium
- Likelihood: Medium (penultimate layer is memory-intensive)
- Affected Hypotheses: H-M2 (penultimate layer tracking)

**R3 (from A3): EMA Instability**
- Source: A3 — β=0.9 provides stable smoothing
- Description: β=0.9 may introduce either too much lag or too much noise for specific training dynamics
- Severity: Medium
- Likelihood: Low-Medium (β=0.9 is standard; mitigated by grid search)
- Affected Hypotheses: H-M3, H-M4

**R4 (from A4): Annotation Dependency Revealed**
- Source: A4 — gradient computable without group labels
- Description: If alignment sign is ambiguous without knowing majority/minority a priori, method requires implicit annotation knowledge
- Severity: High
- Likelihood: Low (gradient computed from cross-entropy loss + true class label only)
- Affected Hypotheses: H-E1 (annotation-free claim)

**R5 (from A5): Regularization Confound**
- Source: A5 — worst-group accuracy improvement must be attributable to alignment mechanism
- Description: GAD improvement may be caused by implicit regularization from reweighting rather than alignment mechanism specifically
- Severity: Medium
- Likelihood: Medium (importance weighting always has regularization effect)
- Affected Hypotheses: H-M3, H-M4

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Batch composition | A1 | H-E1, H-M1 | High |
| R2: vmap OOM | A2 | H-M2 | Medium |
| R3: EMA instability | A3 | H-M3, H-M4 | Medium |
| R4: Annotation dependency | A4 | H-E1 | High |
| R5: Regularization confound | A5 | H-M3, H-M4 | Medium |

### 4.3 Mitigation Strategies

**R1 — Batch Composition Signal Loss:**
- Prevention: Use standard random sampling (documented as scope requirement); verify dataset statistics match expected majority proportions before training
- Detection: Monitor group proportion in each mini-batch during first epoch; alert if minority proportion > 30%
- Response: SCOPE — document as boundary condition (H-C1 tests this explicitly); restrict claims to random-sampling regime

**R2 — GPU Memory / vmap OOM:**
- Prevention: Pre-test vmap on penultimate layer at batch_size=32 before full training run
- Detection: Memory monitoring in first training step; OOM caught immediately
- Response: PIVOT — use gradient checkpointing for penultimate layer; or restrict to last-layer only and document P3 as inconclusive

**R3 — EMA Instability:**
- Prevention: Ablation over β ∈ {0.5, 0.9, 0.99} and clip_max ∈ {2, 5, 10} as planned in measurement plan
- Detection: Monitor training loss and worst-group accuracy on validation set per epoch; instability shows as oscillating loss
- Response: SCOPE — report best β from grid search; narrow claim to optimal hyperparameter setting

**R4 — Annotation Dependency Revealed:**
- Prevention: Implement gradient computation from cross-entropy(logits, y_pred_label) not y_true_group; verify no group annotation accessed during training
- Detection: Code audit: grep for group annotation access in training loop
- Response: ABORT annotation-free claim; reframe as weakly-supervised or evaluation-time annotation method

**R5 — Regularization Confound:**
- Prevention: Include ERM+L2 baseline (λ ∈ {0.01, 0.1, 1.0}) in experiment plan
- Detection: If GAD ≈ ERM+L2 best in worst-group accuracy, confound likely
- Response: EXPLORE — investigate Hessian structure; if alignment mechanism is real (H-M1-2 pass) but ERM+L2 matches, document as "importance weighting via alignment is equivalent to adaptive regularization"

### 4.4 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Batch composition | A1 | High | H-E1, H-M1 | Random sampling + H-C1 boundary test |
| R2 | vmap OOM | A2 | Medium | H-M2 | Gradient checkpointing fallback |
| R3 | EMA instability | A3 | Medium | H-M3, H-M4 | β grid search ablation |
| R4 | Annotation dependency | A4 | High | H-E1 | Code audit + annotation-free implementation |
| R5 | Regularization confound | A5 | Medium | H-M3, H-M4 | ERM+L2 ablation baseline |

Critical Risks: 0 | High: 2 (R1, R4) | Medium: 3 (R2, R3, R5) | Low: 0

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 6 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1 (EXISTENCE — no dependencies)
    [MUST_WORK gate]
         │
         ▼
[Level 1 - Core Mechanism Step 1]
    H-M1 ← H-E1
    [MUST_WORK gate]
         │
         ▼
[Level 2 - Core Mechanism Step 2]
    H-M2 ← H-M1
    [SHOULD_WORK gate]
         │
         ▼
[Level 3 - Core Mechanism Step 3]
    H-M3 ← H-M2
    [SHOULD_WORK gate]
         │
         ▼
[Level 4 - Core Mechanism Step 4: Intervention]
    H-M4 ← H-M3
    [SHOULD_WORK gate]
         │
         ▼
[Level 5 - Boundary Condition]
    H-C1 ← H-M4
    [SHOULD_WORK gate]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |
| 5 | H-C1 | H-M4 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 6 Hypotheses
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis  │  W1-2  │  W3-4  │  W5  │  W6  │  W7  │  W8  │  W9
──────────────────┼────────┼────────┼──────┼──────┼──────┼──────┼──────
PHASE 1: Foundation
  H-E1            │ ██████ │        │      │      │      │      │
  [Gate 1]        │        │  ◆     │      │      │      │      │
──────────────────┼────────┼────────┼──────┼──────┼──────┼──────┼──────
PHASE 2: Core Mechanisms
  H-M1            │        │ ██████ │      │      │      │      │
  H-M2            │        │        │ ████ │      │      │      │
  H-M3            │        │        │      │ ████ │      │      │
  H-M4            │        │        │      │      │ ████ │ ████ │
  [Gate 2]        │        │        │      │      │      │      │ ◆
──────────────────┼────────┼────────┼──────┼──────┼──────┼──────┼──────
PHASE 2.5: Conditions
  H-C1            │        │        │      │      │      │      │ ████
  [Gate 2.5]      │        │        │      │      │      │      │     ◆
──────────────────┴────────┴────────┴──────┴──────┴──────┴──────┴──────
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 8 weeks
═══════════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1

Total Duration: 8 weeks
  Formula: 2 (H-E1) + 4 (H-M, W3-4 then W5,6,7-8) + 1 (H-C) = 8 weeks

Slack Available: 0 weeks (all sequential)

Note: H-M2/H-M3 can leverage cached gradient data from H-E1/H-M1
      experiments, reducing compute overhead.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 6
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 1 (H-C1)

Verification Phases: 3
1. Foundation (H-E1) — 2 weeks
2. Mechanisms (H-M1–H-M4) — 5 weeks
3. Conditions (H-C1) — 1 week

Estimated GPU compute: ~30 GPU-hours total
- H-E1: ~5 GPU-hours (diagnostic, multiple epochs)
- H-M1/M2: ~2 GPU-hours (analysis of H-E1 data, minimal additional compute)
- H-M3/M4: ~18 GPU-hours (GAD training + baselines, 3 seeds each)
- H-C1: ~5 GPU-hours (balanced-batch training, 3 seeds)

Total Duration: 8 weeks
Critical Path Length: 8 weeks
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1**: Execute H-E1 (Foundation) — Week 1-2
**Step 2**: Evaluate Gate 1 — If MUST_WORK fails, STOP entire pipeline
**Step 3**: Execute H-M1 (Batch domination → alignment signal cause) — Week 3-4
**Step 4**: Evaluate Gate 1b — If MUST_WORK fails, PIVOT on mechanism claim
**Step 5**: Execute H-M2 (Directional vs magnitude discrimination) — Week 5
**Step 6**: Execute H-M3 (EMA upweighting shifts training distribution) — Week 6
**Step 7**: Execute H-M4 (GAD achieves ≥ JTT worst-group accuracy) — Week 7-8
**Step 8**: Evaluate Gate 2 — Document all SHOULD_WORK outcomes
**Step 9**: Execute H-C1 (Balanced-batch boundary condition) — Week 9
**Final**: Verify complete, proceed to Phase 5 (skip_baseline_comparison=true per module.yaml → proceed to Phase 4.5)

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Per-sample last-layer gradient cosine similarity with the batch-mean gradient (EMA-smoothed inverse = online importance weight) is a reliable, annotation-free proxy for spurious-minority membership that, when used for online upweighting in a single ERM training run, achieves better worst-group accuracy than JTT and LfF.

**Supporting Evidence:**
1. Batch domination by spurious-majority (82% on Waterbirds) creates directional gradient signal (Shah 2020, Sagawa 2020, Arpit 2017)
2. Spurious-minority samples cannot classify via spurious feature → gradient conflicts with batch mean → logical consequence of simplicity bias
3. DFR (Kirichenko 2022) shows last-layer reweighting toward minority restores worst-group accuracy; GAD does this online without annotations

**Strengths:**
- Clear causal mechanism with 4 steps, each independently falsifiable
- Directional vs magnitude signal distinction addresses JTT's hard-example conflation problem specifically
- Online single-pass eliminates JTT's 2× compute overhead
- 67% of foundational claims already established by prior work (BUILD_ON)

**Expected Outcomes:**
- P1: Alignment ROC-AUC > loss ROC-AUC at ≥1 epoch on both Waterbirds and CelebA
- P2: GAD worst-group ≥ JTT on both datasets (3 seeds)
- P3: Penultimate-layer alignment predictive at earlier epoch than last-layer

### 6.2 Antithesis

**Null Hypothesis (H0):** No significant difference in worst-group accuracy between GAD and JTT (α=0.05, 3 seeds, Waterbirds and CelebA).

**Counter-Arguments:**
1. Mechanism conflates "statistical minority in batch" with "spurious-minority" — Prof. Rex's precision caveat: on datasets where these coincide (Waterbirds, CelebA), the claim holds empirically but lacks general mechanistic validity
2. EMA importance weighting is a known regularization technique; GAD improvement may be regularization artifact (A5), not alignment-specific — ERM+L2 might match performance
3. JTT already achieves 86.7% on Waterbirds (annotation-free); the marginal gain of GAD over JTT may not be statistically significant across 3 seeds

**Potential Failure Points:**
- R4: Gradient computation implicitly requires knowing which class is majority (sign ambiguity)
- R1: If random batch composition happens to equalize groups in practice, signal weakens
- R5: ERM+L2 achieves same worst-group accuracy as GAD → regularization confound confirmed

**Conditions Under Which H0 Would Be Supported:**
- If alignment ROC-AUC ≤ loss ROC-AUC at all epochs on either dataset (P1 falsification)
- If GAD worst-group accuracy < JTT outside error bars on either dataset (P2 falsification)
- If ERM+L2 matches GAD worst-group accuracy (R5 materialized)

### 6.3 Synthesis

The hypothesis H-GAD-v1 presents a well-grounded mechanistic claim that builds on 4 established facts and targets 2 novel empirical demonstrations. The antithesis raises valid precision concerns (mechanism = statistical minority detection, not spurious feature direction detection) and a legitimate confound (importance weighting as regularization). The verification plan resolves this dialectic through:

1. **Foundation first (H-E1):** Establishes signal existence before intervention — if P1 fails, the method is not mechanistically novel regardless of intervention performance
2. **Granular mechanism testing (H-M1–H-M3):** Causal step isolation allows attribution of any performance gain to the specific mechanism vs generic regularization
3. **Explicit confound control (ERM+L2 ablation in H-M4):** Directly tests the antithesis's strongest challenge

**Conditions for Thesis Support:**
- H-E1 MUST_WORK gate passes (alignment > loss ROC-AUC)
- H-M1 MUST_WORK gate passes (batch domination → directional signal)
- H-M4 achieves GAD ≥ JTT AND GAD ≠ ERM+L2 (mechanistic, not just regularization)

**Conditions for Antithesis Support:**
- H-E1 fails (alignment ROC-AUC ≤ loss; directional signal is not distinctive)
- H-M4: GAD < JTT (single-pass does not match two-stage binary signal)
- H-M4: GAD ≈ ERM+L2 (regularization confound confirmed)

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 passes + H-M4 beats JTT + not explainable by L2 → Full thesis validated
2. **Partial Support (Mechanism Valid, Performance Marginal):** H-E1, H-M1-2 pass but H-M4 ties JTT within error bars → Mechanistic contribution stands; performance advantage narrow → paper contribution is diagnostic (P1, P3) not intervention
3. **Antithesis Supported:** H-E1 fails → alignment signal is not directionally distinctive → full pivot needed

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Alignment ROC-AUC > loss at ≥1 epoch | May be coincidence or artifact | H-E1 test with 5 epoch checkpoints |
| Mechanism | 4-step causal chain from batch domination | Mechanism = statistical minority, not spurious feature | H-M1/M2 isolation tests + Prof. Rex caveat documented |
| Intervention | Online GAD ≥ JTT worst-group accuracy | Regularization confound; marginal gain | H-M4 with ERM+L2 ablation |
| Scope | Applies to random-sampling training | Breaks under balanced batching | H-C1 boundary condition test |

**Overall Robustness Score:** Medium-High
**Confidence in Verification Plan:** 0.72 (from Phase 2A)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-GAD-v1 — Online EMA-smoothed inverse gradient alignment upweighting achieves better worst-group accuracy than JTT/LfF without group annotations in a single training run.
- Confidence: 0.72; Mode: Incremental (67% scope reduction)

**Verification Structure:**
- Sub-Hypotheses: 6 total — H-E: 1, H-M: 4, H-C: 1
- Phases: 3 phases over 8 weeks
- Critical Gates: 2 MUST_WORK (H-E1, H-M1); 4 SHOULD_WORK (H-M2/3/4, H-C1)

**Risk Assessment:** Medium
- Primary concerns: R1 (batch composition, High) and R4 (annotation-free claim, High)
- Both mitigated by design: H-C1 boundary test and code-level annotation audit

**Immediate Action:** Begin Phase 1 with H-E1 — diagnostic ROC-AUC comparison experiment

### 7.2 Conclusions

**Key Achievements:**
- 6 hypotheses across 3 phases; all grounded in Phase 2A causal chain
- H0 addressed: null hypothesis directly falsified by H-M4 test (two-sided t-test, α=0.05)
- Prof. Rex precision caveat incorporated as scope boundary (H-C1)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Gradient alignment ROC-AUC > loss ROC-AUC on Waterbirds + CelebA
- Gate 1: MUST PASS — pipeline stops if H-E1 fails

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Batch domination → alignment signal mechanistic validation (W3-4)
- H-M2: Directional vs magnitude discrimination (W5)
- H-M3: EMA upweighting distribution shift (W6)
- H-M4: GAD ≥ JTT worst-group accuracy, 3 seeds (W7-8)
- Gate 2: H-M1 MUST PASS; H-M2/3/4 document outcomes

**Phase 2.5: Conditions** (1 week)
- H-C1: Balanced-batch boundary condition validation (W9)
- Gate 2.5: SHOULD PASS — narrows scope, does not invalidate

**Critical Decision Points:**

1. **Gate 1 (H-E1 Foundation):** MUST_WORK
   - FAIL → STOP full pipeline; novelty claim cannot be supported
   - PASS → Proceed to Phase 2

2. **Gate 1b (H-M1 Mechanism):** MUST_WORK
   - FAIL → PIVOT on mechanism claim; continue H-M4 to check if intervention still works empirically
   - PASS → Proceed through mechanism chain

3. **Gate 2 (H-M4 Intervention):** SHOULD_WORK
   - FAIL → PIVOT — tune β, clip_max; if still fails, document as null result

**Open Questions:**
- "Does penultimate-layer alignment provide strictly earlier signal than last-layer? (P3)"
- "Is the alignment signal robust to class-balanced batching, or does it break? (A1 → H-C1)"
- "Can the method scale to ViT-B with gradient checkpointing? (A2)"
- "Does GAD with EMA β=0.9 achieve ≥ JTT on CelebA in addition to Waterbirds? (P2)"

**Recommendations:**

1. **Immediate Actions:**
   - Start H-E1: set up gradient tracking in ERM training loop using torch.func.vmap
   - Download Waterbirds + CelebA via kohpangwei/group_DRO scripts
   - Implement alignment score logging at epoch checkpoints {1, 5, 10, 25, 50}

2. **Resource Allocation:**
   - Allocate 8 weeks for full critical path; H-M1/M2 reuse H-E1 data (minimal extra compute)
   - ~30 GPU-hours total; reserve buffer for hyperparameter ablations

3. **Failure Management:**
   - Gate 1 failure: full stop; route to Phase 0 for new hypothesis direction
   - Gate 1b failure: continue to H-M4 (empirical test) with documented mechanism caveat
   - H-M4 failure: execute β/clip_max grid search as first PIVOT attempt

### 7.3 Appendices

**A. Phase 2A Reference:**
- Source: docs/youra_research/03_refinement.yaml (ID: H-GAD-v1)
- Generated: 2026-08-31; Convergence at Exchange 10-11; 6 agents; 8 citations

**B. MCP Tool Usage Summary:**
- Total MCP calls: 0 (ABLATION MODE — ClearThought MCP not available)
- Note: Sub-hypotheses generated via direct Phase 2A causal chain decomposition (4 steps → H-M1–H-M4); scientific method reasoning applied without external MCP tool call

**C. Scope Reduction Applied:**
- 4 of 6 claims are BUILD_ON (67% reduction); only claims 5-6 require experimental verification
- Experiments focus exclusively on: (1) alignment ROC-AUC diagnostic, (2) GAD intervention worst-group accuracy

---

*Step 00-09 saved.*
