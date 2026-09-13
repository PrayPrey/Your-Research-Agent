# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T00:00:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap_1
- **Gap Title**: Comparative Expressivity Analysis of Weight-Processing Backbones
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All convergence criteria met after 7 exchanges: specific claim, mechanism, predictions, novelty, feasibility, and objections addressed

### Key Insights

1. **Paradigm Reframe**: Shifted from empirical "which backbone wins?" to principled "what does each capture?" characterization framework
2. **Theory-Grounded Taxonomy**: Avoided circular reasoning by anchoring property dimensions (permutation, locality/globality, frequency) in established mathematical theory
3. **Failure-Mode Complementarity**: Focused on detecting anomalies individual backbones miss (>10% backdoor detection gain) rather than marginal average accuracy improvements
4. **Dimensionality Solution**: Layer-wise processing resolves scalability constraints while preserving layer-local structural properties validated by model stitching literature

### Breakthrough Moments

1. **Exchange 1**: Dr. Nova reframed comparison paradigm from horse-race to complementarity characterization
2. **Exchange 6**: Prof. Rex's circularity challenge led to theory-grounded taxonomy design
3. **Exchange 7**: Dr. Nova's backdoor detection application simultaneously satisfied feasibility (Prof. Pax), testability (Prof. Vera), and significance (Dr. Sage) concerns

---

## Final Hypothesis

### Title
Orthogonal Expressivity of Weight-Processing Backbones

### Core Claim
Under the domain of neural network weight-space learning, if we process weights with multiple backbone architectures (transformer, equivariant GNN, MLP) that target orthogonal structural properties (global dependencies, permutation symmetry, local patterns), then combining their learned representations will significantly outperform individual backbones on weight-to-property prediction and anomaly detection tasks (>5% on property prediction, >10% on backdoor detection), because each architecture captures complementary aspects of weight structure that individual backbones miss.

### Mechanism
Each architecture's inductive biases align with specific weight-space properties:
1. **Step 1**: Architectural priors determine property alignment (Transformers → global dependencies, GNNs → locality + permutation symmetry, MLPs → local patterns)
2. **Step 2**: During embedding learning, each backbone preferentially captures its aligned property while underperforming on others
3. **Step 3**: Captured properties are orthogonal, leading to low reconstruction error correlation (<0.7)
4. **Step 4**: Concatenating orthogonal embeddings provides complementary information, improving downstream task performance

---

## Predictions

**P1 (Primary)**: Concatenated Transformer+GNN embeddings achieve >5% accuracy improvement over best single backbone on model property prediction task
- **Test Method**: Train three systems (Transformer-only, GNN-only, concatenated), measure accuracy on held-out model zoo
- **Success Criterion**: Concatenated accuracy > max(single backbone) + 5 percentage points
- **Falsification**: If improvement <5%, orthogonality claim is FALSE

**P2**: Equivariant GNN shows symmetry differential >30% (within-layer vs across-layer permutations); Transformer <10%
- **Test Method**: Apply within-layer and across-layer weight permutations, measure prediction accuracy degradation
- **Success Criterion**: GNN differential >30%, Transformer differential <10%
- **Falsification**: If GNN <30% OR Transformer >10%, equivariance claim is FALSE

**P3**: Reconstruction error correlation between Transformer and GNN <0.7, indicating orthogonal failure modes
- **Test Method**: Train autoencoders for each backbone, compute reconstruction errors, calculate Pearson correlation
- **Success Criterion**: Correlation <0.7 across test set
- **Falsification**: If correlation >0.7, embeddings are not orthogonal

---

## Novelty

**Key Innovation**: Reframes backbone comparison from empirical performance comparison to systematic characterization of structural property capture, grounding taxonomy in mathematical theory rather than post-hoc observation

**Differentiation from Prior Work**:
- Prior: Empirical architecture comparison on single tasks
- This work: Characterizes HOW backbones differ via theoretical property taxonomy, predicts when each excels, demonstrates complementarity
- Prior: Ad-hoc weight representations in model merging/task arithmetic
- This work: Principled architecture selection based on task-relevant weight-space properties
- Prior: Single-architecture backdoor detection
- This work: Orthogonal failure modes enable ensemble robustness (local + global anomaly detection)

---

## Experimental Design

**Datasets**: 
- timm model zoo (pre-trained ImageNet models: ResNet, EfficientNet, ViT)
- Existing backdoor detection datasets
- Synthetic networks with planted symmetries (Stage 1 validation)

**Models**:
- Transformer-based weight embedder (global dependencies)
- Equivariant GNN weight processor (permutation + locality)
- MLP baseline (local patterns only)
- Concatenated Transformer+GNN system

**Baselines**:
- Single-backbone systems (Transformer-only, GNN-only, MLP-only)
- Simple ensemble (majority voting / averaging)
- Random concatenation (null hypothesis check)

**Two-Stage Validation**:
1. **Stage 1**: Synthetic networks with known ground truth structure (proof of concept)
2. **Stage 2**: Real pre-trained models from timm (generalization validation)

---

## Limitations

1. **Layer-wise Processing**: Loses some cross-layer dependencies, but validated by model stitching literature showing most properties are layer-local
2. **Taxonomy Completeness**: Three properties (permutation, locality/globality, frequency) well-grounded but may not exhaust relevant weight-space structure
3. **Scalability Demonstrated on Mid-Size Models**: ResNet50-scale validation, not billion-parameter LLMs
4. **Application Specificity**: Backdoor detection as primary application; other anomaly types require additional validation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All convergence criteria met after 7 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (concerns identified with mitigation strategies) |

---

## Phase 2B Readiness

**Status**: READY

**SH1 (Existence)**: Verify that (1) layer-wise weight tokenization preserves structural signal, (2) backbone capacity matching isolates structural effects, (3) property taxonomy is complete enough

**SH2 (Mechanism)**: Test four-step causal chain via symmetry differential (P2), reconstruction correlation (P3), complementarity gain (P1)

**SH3 (Comparison)**: Compare concatenated multi-backbone system against single-backbone baselines and simple ensemble (deferred baseline repository comparison to Phase 5)

**Open Questions**:
- Are three properties exhaustive, or are additional dimensions needed?
- Does layer-wise processing lose critical cross-layer signals?
- Do capacity-matched architectures still differ in expressivity ceilings?
- Does backdoor detection complementarity generalize to other anomaly types?

---

*Phase 2A Complete - Ready for Phase 2B Research Planning*
