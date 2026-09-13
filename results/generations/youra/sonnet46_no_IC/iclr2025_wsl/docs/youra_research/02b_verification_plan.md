---
hypothesis_id: H-EquiSSL-v1
workflow: phase2b-planning
date: "2026-08-05"
research_mode: incremental
total_hypothesis_count: 5
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
completedAt: "2026-08-05T08:15:00Z"
---

# Verification Plan: EquiSSL — Scale+Permutation Equivariant SSL for Cross-Architecture Weight Representations

**Date:** 2026-08-05
**Hypothesis ID:** H-EquiSSL-v1
**Confidence:** 0.75
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)

---

## Section 0: Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON — DO NOT RE-VERIFY)

| Claim | Evidence | Status |
|-------|----------|--------|
| Permutation-equivariant layers (NFN, NFT, neural-graphs) outperform non-equivariant baselines for property prediction on same-architecture model zoos | Navon et al. 2023 (NFN, 78 citations), Kofinas et al. 2024 ICLR Oral (neural-graphs R²=0.90 on MLP zoo) | BUILD_ON |
| Scale+permutation equivariant architectures (ScaleGMN) outperform permutation-only methods on property prediction within the same supervised setting | Kalogeropoulos et al. 2024 NeurIPS Oral (ScaleGMN R²=0.91 vs NFN R²=0.84 on MLP zoo) | BUILD_ON |
| SSL on weight populations (SANE, hyper-representations) produces useful property prediction representations from unlabeled model zoos | Schürholt et al. 2021 NeurIPS (R²=0.89 on MNIST zoo), Schürholt et al. 2024 ICML (R²=0.72 on heterogeneous zoo) | BUILD_ON |
| Computational graph representation provides architecture-agnostic node/edge semantics (MLP→CNN zero-shot transfer) | Kofinas et al. 2024 ICLR Oral: zero-shot MLP→CNN transfer R²=0.71 vs baseline 0.59 | BUILD_ON |

### 0.2 PROVE_NEW Claims (Phase 2B Experimental Targets)

| Claim | Status | Phase 2B Target |
|-------|--------|-----------------|
| No existing method combines SSL training objectives with scale+permutation equivariant encoders | PROVE_NEW | H-E1 + H-M1/M2 |
| SSL weight representations generalize to held-out general model architectures (MLPs/CNNs to ViTs) | PROVE_NEW | H-M4 (P1 primary) |

**Scope Reduction:** 33% (4 BUILD_ON claims accepted as baselines; 2 PROVE_NEW claims are the experimental targets)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the weight-space SSL setting using existing MLP+CNN model zoo checkpoints (SANE MultiZoo), if a scale+permutation equivariant graph encoder (ScaleGMN backbone with hierarchical representation for block-structured architectures) is trained with a contrastive autoencoder objective using scale/permutation augmented positive pairs, then the learned representations will achieve property prediction R² on a held-out ViT Model Zoo (no ViT training data) that is at least 0.10 above SANE baseline trained on the same data, because the computational graph representation eliminates architectural distribution shift while scale equivariance normalizes weight magnitude variation across architectures.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in held-out ViT zoo property prediction R² between EquiSSL (scale+perm equivariant contrastive autoencoder) and SANE (non-equivariant SSL autoencoder) when both are trained on the same MLP+CNN zoo data (delta R² < 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | SANE MultiZoo (training) + ViT Model Zoo (held-out test) (standard) | MultiZoo provides diverse MLP+CNN training distribution; ViT zoo provides architecturally held-out test models with existing accuracy labels. No new benchmarks or annotation required. |
| **Model** | EquiSSL: ScaleGMN Encoder + Graph Decoder + Contrastive Autoencoder | ScaleGMN's monomial group equivariant encoder directly tests the symmetry hypothesis. Graph decoder enables P3 (latent interpolation). Composable from existing codebases. |

**Dataset Details:**
- Source: SANE MultiZoo: github.com/HSG-AIML/MultiZoo-SANE (public). ViT Model Zoo: arXiv 2504.10231 (public).
- Path: Training: HSG-AIML/MultiZoo-SANE dataset (~30k MLP+CNN models). Test: ViT Model Zoo (250 ViT models).

**Model Details:**
- Type: Equivariant graph neural network with contrastive autoencoder training
- Source: ScaleGMN: github.com/jkalogero/scalegmn (public). Neural-graphs (hierarchical ViT formulation): github.com/mkofinas/neural-graphs (public). SANE training framework: github.com/HSG-AIML/SANE (public).

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| SANE (non-equivariant SSL) | R²=0.72 on heterogeneous MLP+CNN zoo; ViT zoo performance unknown (pilot required) | SANE MultiZoo (MLP+CNN, ~30k models) |
| EquiSSL-perm (permutation-only equivariant SSL) | R²=0.71 on supervised MLP→CNN zero-shot (neural-graphs); SSL version untested | MLP zoo + CNN zoo (Kofinas 2024) |
| Hyper-representations (Schürholt et al. 2021 NeurIPS) | R²=0.89 on MNIST zoo (homogeneous); fails across distribution shifts | MNIST MLP zoo (50k models) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Computational graph representation (node=neuron, edge=weight) provides genuinely architecture-agnostic node/edge semantics — ViT attention projections have the same structural role as MLP weight matrices in the graph | Kofinas et al. 2024 ICLR Oral: zero-shot MLP→CNN transfer demonstrates graph schema works across architecture families | Distribution shift elimination mechanism fails; EquiSSL won't generalize to ViTs |
| A2 | Scale equivariance contributes meaningfully beyond permutation equivariance for cross-architecture transfer | Kalogeropoulos et al. 2024: 8-12 R² improvement from scale equivariance in supervised same-architecture setting | Paper's core technical contribution reduced to engineering choice; still publishable as graph+perm finding |
| A3 | ViT Model Zoo (250 models) has sufficient diversity and property labels for valid held-out evaluation | Zoo paper reports ViTs trained on multiple tasks with accuracy labels; 250 models with varying accuracy provides sufficient range for R² | R² estimates have high variance; may need to supplement with HuggingFace ViT checkpoints |
| A4 | SANE MultiZoo training data (MLP+CNN, ~30k models) provides sufficient diversity for SSL pre-training that generalizes to ViT | arXiv 2504.10141: dataset diversity strong predictor of cross-arch performance | EquiSSL also fails to generalize; report as diversity limitation, not method failure |
| A5 | Contrastive autoencoder training with λ=0.1-1.0 converges stably; contrastive and reconstruction objectives do not conflict | Vision SSL analogues (I-JEPA, BEiT) demonstrate stable coexistence; weight-space autoencoders (Schürholt 2022) converge with pure reconstruction | Hybrid architecture collapses; mitigation: λ sweep over 4 values to identify stable regime |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First method combining scale+permutation equivariant encoding with SSL training objectives for weight-space representation learning, demonstrating cross-architecture generalization to architecturally held-out model families (ViT zoo).

**Key Innovation:** EquiSSL unifies two previously separate research tracks: (1) equivariant weight-space architectures (ScaleGMN, NFN, neural-graphs) and (2) SSL on weight populations (SANE, hyper-representations). The computational graph as universal weight-space coordinate system enables this unification.

**Differentiation:**
- vs SANE: Uses computational graph (architecture-agnostic) and monomial-group equivariant encoder (exact invariance by construction) vs flat chunk tokenization (architecture-specific)
- vs ScaleGMN: Trains without labels using SSL objectives, enabling application to unlabeled model zoos
- vs Neural-graphs: Demonstrates cross-architecture SSL transfer (no labels required) vs cross-architecture supervised transfer

---

## 2. Risk Analysis

### 2.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: ViT attention graph semantics mismatch | A1 | H-E1, H-M1, H-M4 | HIGH |
| R2: Insufficient statistical power (250 ViT models) | A3 | H-E1, H-M4 | MEDIUM-HIGH |
| R3: Contrastive + reconstruction objective conflict | A5 | H-M3, H-M4 | MEDIUM |
| R4: Scale equivariance contributes minimally in SSL | A2 | H-M2 | MEDIUM |
| R5: Training zoo diversity insufficient | A4 | H-M4 | LOW-MEDIUM |

### 2.2 Mitigation Strategies

**Risk R1: ViT Attention Graph Semantics Mismatch** (HIGH)

*Source Assumption:* A1 — Computational graph provides architecture-agnostic semantics

*Description:* ViT positional encodings and LayerNorm interactions may break the pure node=neuron, edge=weight schema. Q/K/V projections function through softmax attention scores depending on the full input sequence, not just local edge weights.

*Affected Hypotheses:* H-E1, H-M1, H-M4

*Mitigation Strategy:*
1. **Prevention:** Use Kofinas 2024 hierarchical neural-graphs formulation which handles attention as MLP subgraphs — already validated for ViT representation
2. **Detection:** Run graph construction validation before full training — count non-linear-layer ViT parameters that cannot be embedded in graph schema; target <5% unrepresented parameters
3. **Response:**
   - PIVOT: If positional encodings break schema, represent them as special node features rather than edges
   - SCOPE: Restrict to ViT models without learned positional encodings (many standard ViTs use sinusoidal fixed PE)
   - ABORT: If >20% ViT parameters cannot be graph-embedded, graph representation hypothesis fails; report null result

*Early Warning:* MMD ratio < 1.2 (graph representation barely reduces distribution shift); reconstruction loss on ViT zoo much higher than on MLP+CNN training zoo

---

**Risk R2: Insufficient Statistical Power** (MEDIUM-HIGH)

*Source Assumption:* A3 — ViT zoo (250 models) sufficient for R² evaluation

*Description:* Paired t-test over 5 seeds for p<0.05 requires seed variance dominated by method effect (ΔR²=0.10), not training stochasticity. If SSL training variance (std across 5 seeds) > 0.07, significance testing fails.

*Affected Hypotheses:* H-E1, H-M4

*Mitigation Strategy:*
1. **Prevention:** Run 2 SANE seeds on ViT zoo before full EquiSSL training to estimate baseline variance
2. **Detection:** If SANE ViT R² std > 0.07 across 2 pilot seeds, flag power risk before committing compute
3. **Response:**
   - PIVOT: Increase seed count to 10 for stronger statistical power
   - SCOPE: Supplement ViT zoo with publicly available HuggingFace ViT checkpoints with accuracy labels (target 500+ models total)
   - ABORT: If ViT zoo variance is intrinsically too high (std > 0.15), report as evaluation limitation

*Early Warning:* SANE pilot R² std > 0.07 across 2 seeds

---

**Risk R3: Contrastive + Reconstruction Objective Conflict** (MEDIUM)

*Source Assumption:* A5 — Training objectives do not conflict

*Description:* NT-Xent pushes different networks apart in latent space; MSE reconstruction pulls z toward encoding all weight information. Opposite optimization pressures may destabilize training or produce suboptimal λ sensitivity.

*Affected Hypotheses:* H-M3, H-M4

*Mitigation Strategy:*
1. **Prevention:** λ sweep {0.01, 0.1, 1.0, 10.0} — standard range from vision SSL analogues
2. **Detection:** Monitor training reconstruction loss and contrastive loss jointly; flag if either diverges
3. **Response:**
   - PIVOT: If λ>1.0 always collapses reconstruction, limit P3 evaluation to λ≤1.0 range
   - SCOPE: Report full λ sweep transparently; select λ by validation R² + reconstruction loss jointly

*Early Warning:* Training loss divergence at any λ; reconstruction loss on training zoo much higher than SANE baseline

---

**Risk R4: Scale Equivariance Not Necessary for SSL** (MEDIUM)

*Source Assumption:* A2 — Scale equivariance contributes beyond permutation equivariance

*Description:* Kalogeropoulos 2024 result (8-12 R² improvement) was in supervised same-architecture setting. Cross-architecture SSL may not benefit equivalently.

*Affected Hypotheses:* H-M2

*Mitigation Strategy:*
1. **Prevention:** Include EquiSSL-perm (permutation-only) as explicit ablation baseline — this is the purpose of the ablation ladder
2. **Detection:** If EquiSSL-perm R² ≥ EquiSSL R² on ViT zoo, scale equivariance is not necessary
3. **Response:**
   - ACCEPT: If scale equivariance is not necessary, report as finding: "permutation equivariance + graph representation suffices for cross-architecture SSL transfer" — still a publishable contribution

*Early Warning:* EquiSSL-perm achieves R² within 0.03 of EquiSSL

---

**Risk R5: Training Zoo Diversity Insufficient** (LOW-MEDIUM)

*Source Assumption:* A4 — SANE MultiZoo provides sufficient training diversity

*Description:* MLP+CNN training zoo contains no attention mechanism examples. SSL pre-training may not learn attention-weight statistics generalizable to ViT zoo.

*Affected Hypotheses:* H-M4

*Mitigation Strategy:*
1. **Prevention:** This is a known scope limitation acknowledged in Phase 2A
2. **Detection:** If both EquiSSL and EquiSSL-perm fail to improve over SANE on ViT zoo, diversity is likely the cause
3. **Response:**
   - SCOPE: Report as "MLP+CNN training diversity insufficient for ViT transfer" — supplement zoo with ViT checkpoints in Phase 5

*Early Warning:* Both EquiSSL variants fail to achieve R² > 0.40 on ViT zoo

### 2.3 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Pre-Training Mitigation |
|----|------|--------|----------|----------|------------------------|
| R1 | ViT attention graph semantics mismatch | A1 | HIGH | H-E1, H-M1, H-M4 | Graph construction validation before full training |
| R2 | Insufficient statistical power (250 ViT models) | A3 | MEDIUM-HIGH | H-E1, H-M4 | SANE pilot (2 seeds) to estimate variance |
| R3 | λ objective conflict | A5 | MEDIUM | H-M3, H-M4 | λ sweep {0.01, 0.1, 1.0, 10.0} |
| R4 | Scale equivariance not necessary in SSL | A2 | MEDIUM | H-M2 | Ablation ladder (EquiSSL-perm) |
| R5 | Training zoo diversity insufficient | A4 | LOW-MEDIUM | H-M4 | Acknowledged scope limitation; fallback to HuggingFace ViT |

Critical Risks: 0 | High Risks: 1 | Medium Risks: 3 | Low-Medium Risks: 1

---

## 3. Hierarchical Hypothesis Structure

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | MMD ratio (SANE/EquiSSL) ≥ 2.0 | STOP — graph representation does not reduce distribution shift; reassess hypothesis |
| H-M1 | MUST_WORK | Both EquiSSL variants achieve higher ViT R² than SANE (graph representation mechanism confirmed) | STOP — fundamental mechanism failure; report null result |
| H-M2 | SHOULD_WORK | EquiSSL R² > EquiSSL-perm R² by ≥ 0.05 on ViT zoo | DOCUMENT — scale equivariance not necessary; refined claim (permutation-only suffices) |
| H-M3 | SHOULD_WORK | Latent interpolation accuracy > weight-space averaging (p < 0.05, 100 MLP pairs) | DOCUMENT — contrastive objective does not create functional latent geometry |
| H-M4 | MUST_WORK | R²(EquiSSL, ViT zoo) ≥ R²(SANE, ViT zoo) + 0.10, p < 0.05 | STOP — full causal chain insufficient; report detailed failure analysis |

### 3.3 Timeline Overview

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | Week 1-2 |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | Week 3-7 |

**Total Duration:** 7 weeks (2 + 5)

---

## 4. Sub-Hypothesis Inventory

### 4.1 Hypothesis Inventory Table

| ID | Type | Statement (Brief) | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | EXISTENCE | EquiSSL encoder reduces architectural distribution shift (MMD ratio ≥ 2.0) when applied to held-out ViT zoo | MUST_WORK | None | READY |
| H-M1 | MECHANISM | Computational graph representation eliminates shape mismatch; graph encoder achieves higher ViT R² than flat tokenizer | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | Scale+permutation equivariance (ScaleGMN) improves ViT R² over permutation-only (neural-graphs) by ≥ 0.05 | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | Contrastive autoencoder training creates functional latent geometry: latent interpolation > weight-space averaging | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | Full EquiSSL pipeline achieves ViT zoo R² ≥ SANE + 0.10 (primary prediction P1) | MUST_WORK | H-M3 | NOT_STARTED |

---

### 4.2 Hypothesis Specifications

---
**H-E1: Distribution Shift Reduction (Existence)**

**Statement**: Under the EquiSSL SSL setting, if the ScaleGMN encoder trained on SANE MultiZoo (MLP+CNN) is applied to the ViT Model Zoo (250 models, no ViT training data), then MMD(SANE train→ViT) / MMD(EquiSSL train→ViT) ≥ 2.0 with RBF kernel (σ = median heuristic), because the computational graph representation provides architecture-agnostic node/edge semantics that eliminates the weight tensor shape mismatch between MLP and ViT architectures.

**Rationale**: This is the primary existence test for the distribution shift elimination mechanism. It validates the most fundamental claim — that EquiSSL produces a latent space where MLP+CNN training models and ViT test models are closer together than in SANE's flat tokenizer latent space. A pass here provides mechanistic evidence (P2) independent of the property prediction result (P1).

**Variables (from Phase 2A):**
- Independent: Encoder type (ScaleGMN vs SANE flat tokenizer)
- Dependent: MMD ratio (SANE/EquiSSL) with RBF kernel on latent z
- Controlled: Training data (SANE MultiZoo), test set (ViT zoo 250 models), kernel parameters

**Verification Protocol:**
1. Train EquiSSL and SANE on identical SANE MultiZoo data; extract frozen latent z for all training models
2. Apply frozen encoders to all 250 ViT zoo models; extract latent z for each
3. Compute MMD(train→ViT) for both encoders using RBF kernel, σ = median heuristic on pooled latent codes
4. Report MMD ratio (SANE/EquiSSL); success criterion: ratio ≥ 2.0
5. Visualize with t-SNE: plot MLP+CNN training z and ViT test z for both encoders

**Success Criteria (PoC):**
- Primary: MMD ratio (SANE/EquiSSL) ≥ 2.0
- Secondary: t-SNE visualization shows ViT test points closer to training distribution for EquiSSL than SANE

**Gate:** MUST_WORK — If ratio < 1.5, graph representation does not reduce distribution shift; STOP

**Dependencies:** None (foundation)

**Source:** Phase 2A Section 5 (sh1_existence), Prediction P2

---

**H-M1: Graph Representation Architecture-Agnostic Semantics**

**Statement**: Under the weight-space SSL setting, if directed computational graph encoding (node=neuron, edge=weight) is used for both MLP+CNN training zoo and ViT test zoo, then both EquiSSL and EquiSSL-perm (permutation-only) achieve higher ViT zoo property prediction R² than SANE (flat tokenizer), because the graph schema provides the same node/edge structure regardless of architecture family, eliminating the representational mismatch that prevents flat tokenizers from generalizing to novel architecture shapes.

**Rationale**: This tests the causal step 1 mechanism — that graph representation specifically (not equivariance) is the primary driver of cross-architecture generalization. The comparison is graph-based encoders (both EquiSSL and EquiSSL-perm) vs flat tokenizer (SANE); any advantage shared between both graph encoders vs SANE confirms the graph representation hypothesis independently of the equivariance question.

**Variables:**
- Independent: Representation type (graph-based vs flat tokenizer)
- Dependent: ViT zoo property prediction R² (linear probe, frozen z, 5 seeds)
- Controlled: SSL objective (contrastive autoencoder for both graph encoders), training data (SANE MultiZoo)

**Verification Protocol:**
1. Train three models: SANE (flat tokenizer), EquiSSL-perm (neural-graphs + contrastive), EquiSSL (ScaleGMN + contrastive) on identical SANE MultiZoo data
2. Apply frozen encoders to ViT Model Zoo (250 models); train linear probe (ridge regression) on 80% split
3. Evaluate on 20% test split; report R² ± std over 5 random seeds for all three methods
4. Confirm: R²(EquiSSL-perm) > R²(SANE) AND R²(EquiSSL) > R²(SANE) — both graph encoders beat flat tokenizer
5. Report paired t-test p-value for each comparison vs SANE baseline

**Success Criteria (PoC):**
- Primary: Both EquiSSL-perm and EquiSSL achieve R² > SANE on ViT zoo (p < 0.05)
- Secondary: Effect size R²(graph) - R²(SANE) > 0.05 for at least one graph encoder

**Gate:** MUST_WORK — If neither graph encoder beats SANE, graph representation hypothesis is disconfirmed; STOP

**Dependencies:** H-E1 must pass (existence of distribution shift reduction confirmed)

**Source:** Phase 2A Section 1.3 Causal Step 1, Kofinas 2024 direct evidence

---

**H-M2: Scale Equivariance Contribution Beyond Permutation**

**Statement**: Under the EquiSSL setting with identical contrastive autoencoder training objective, if scale+permutation equivariant message passing (ScaleGMN monomial group) is used instead of permutation-only equivariant message passing (neural-graphs), then EquiSSL achieves ViT zoo property prediction R² ≥ EquiSSL-perm + 0.05, because the monomial group equivariance normalizes weight magnitude variation from neuron rescaling transformations (f(scale(A)) = scale(f(A))) that is present in cross-architecture settings and not captured by permutation equivariance alone.

**Rationale**: This is the scale ablation — the most critical open empirical question identified by Phase 2A (Prof. Rex's objection). It directly tests whether the additional complexity of scale equivariance (monomial group vs symmetric group) is empirically necessary for the cross-architecture transfer claim, or whether permutation equivariance + graph representation already suffices.

**Variables:**
- Independent: Symmetry enforcement level (scale+perm/ScaleGMN vs perm-only/neural-graphs)
- Dependent: ΔR² (EquiSSL − EquiSSL-perm) on ViT zoo
- Controlled: SSL training objective (identical contrastive autoencoder for both), training data, evaluation protocol

**Verification Protocol:**
1. Use EquiSSL and EquiSSL-perm trained in H-M1 (no additional training required)
2. Compare R² ± std over 5 seeds for EquiSSL vs EquiSSL-perm on identical ViT zoo test split
3. Compute ΔR² = R²(EquiSSL) − R²(EquiSSL-perm) and 95% CI
4. Report paired t-test over seeds for significance of ΔR²
5. Visualize latent space geometry for both encoders on ViT zoo (t-SNE/UMAP)

**Success Criteria (PoC):**
- Primary: ΔR² ≥ 0.05 (EquiSSL > EquiSSL-perm), p < 0.10 (directional test)
- Secondary: Scale equivariance improves MMD ratio (EquiSSL MMD ratio > EquiSSL-perm MMD ratio)

**Failure Response:**
- IF fails (ΔR² < 0.05): DOCUMENT as finding — permutation equivariance + graph representation is sufficient; scale equivariance is not causally necessary in SSL setting. Refine thesis claim accordingly. Do NOT stop pipeline.

**Dependencies:** H-M1 must pass (both graph encoders beat SANE)

**Source:** Phase 2A Section 1.3 Causal Step 2, Kalogeropoulos 2024 ablation evidence

---

**H-M3: Contrastive Autoencoder Creates Functional Latent Geometry**

**Statement**: Under the EquiSSL setting trained on SANE MultiZoo, if contrastive autoencoder training (NT-Xent + MSE reconstruction, λ=best validated) is applied, then the resulting latent space enables functional model interpolation: decoded midpoint model (z = (zA + zB)/2, then decode to weights via graph decoder) achieves higher task accuracy than naive weight-space averaging ((θA + θB)/2), averaged over 500+ MLP pairs from the training zoo (p < 0.05, paired t-test), because NT-Xent penalizes distinct networks mapping to similar latent codes while reconstruction ensures z retains sufficient functional weight information.

**Rationale**: This tests the generative quality of the latent space (prediction P3). It is both a scientific contribution (functional latent geometry for model editing) and a validation that the contrastive objective meaningfully shapes the latent space beyond pure reconstruction. A pass here adds the model interpolation use case to the EquiSSL contribution.

**Variables:**
- Independent: Interpolation method (latent-space midpoint decode vs weight-space averaging)
- Dependent: Task accuracy of interpolated model on benchmark tasks
- Controlled: 500+ MLP checkpoint pairs from training zoo (same task), evaluation benchmarks

**Verification Protocol:**
1. Sample 500+ MLP checkpoint pairs from SANE MultiZoo (same task, varying accuracy within pair)
2. For each pair: compute EquiSSL latent midpoint z_mid = (z_A + z_B) / 2; decode z_mid to weights via graph decoder
3. Compute weight-space average: θ_avg = (θ_A + θ_B) / 2
4. Evaluate both interpolated models on same task benchmark; record accuracy difference (latent − weight)
5. Report mean accuracy difference ± std over 500+ pairs; paired t-test for p < 0.05

**Success Criteria (PoC):**
- Primary: Mean accuracy(latent interpolation) > mean accuracy(weight average), p < 0.05 over 500+ pairs
- Secondary: Effect size > 1% accuracy improvement on average

**Failure Response:**
- IF fails: DOCUMENT as scope limitation — contrastive training does not create functional latent geometry for model interpolation; P3 is disconfirmed. Continue to H-M4 (property prediction is independent of interpolation quality).

**Dependencies:** H-M2 evaluation (EquiSSL trained model from H-M1/M2 evaluation)

**Source:** Phase 2A Section 1.6 Prediction P3, Schürholt 2022 (weight-space autoencoder) analogy

---

**H-M4: Full EquiSSL Pipeline — Primary Cross-Architecture Transfer**

**Statement**: Under the weight-space SSL setting, if the full EquiSSL pipeline (computational graph representation + scale+permutation equivariant encoder + contrastive autoencoder training, trained on SANE MultiZoo MLP+CNN data), is applied to the held-out ViT Model Zoo (250+ ViT models, no ViT training data), then property prediction R² for accuracy labels will be ≥ SANE baseline R² + 0.10, with p < 0.05 by paired t-test over 5 random seeds, because the cumulative causal chain (Steps 1-3: graph representation + scale equivariance + contrastive training) collectively enables zero-shot cross-architecture generalization.

**Rationale**: This is the primary prediction (P1) and the central claim of H-EquiSSL-v1. It tests the full causal chain together. This is the gate for Phase 5 (if all H-M hypotheses pass, proceed to baseline comparison; if H-M4 fails despite H-M1 passing, the mechanism exists but effect size is insufficient).

**Variables:**
- Independent: Full pipeline (EquiSSL) vs non-equivariant SSL (SANE)
- Dependent: Property prediction R² on held-out ViT Model Zoo (250 ViT models, accuracy prediction)
- Controlled: Training data (SANE MultiZoo, identical), evaluation protocol (linear probe, same 80/20 split, 5 seeds)

**Verification Protocol:**
1. Apply EquiSSL (best λ from validation) and SANE (trained identically) to all 250+ ViT zoo models; extract frozen z
2. Train ridge regression linear probe on 80% ViT zoo accuracy labels; evaluate on 20% held-out test split
3. Repeat over 5 random seeds; report R² ± std for both EquiSSL and SANE
4. Compute ΔR² = R²(EquiSSL) − R²(SANE); paired t-test over seeds
5. Pre-registered threshold: ΔR² ≥ 0.10, p < 0.05; threshold calibrated against SANE-ViT pilot result

**Success Criteria (PoC: Direction-based with threshold):**
- Primary: ΔR² ≥ 0.10 AND p < 0.05 (paired t-test over seeds)
- Secondary: EquiSSL achieves absolute R² ≥ 0.60 on ViT zoo (demonstrates meaningful cross-architecture transfer, not just beating a weak baseline)

**Gate:** MUST_WORK — If ΔR² < 0.05, full pipeline fails to outperform SANE; investigate failure analysis across H-M1-M3 sub-results

**Dependencies:** H-M1 (graph representation confirmed), H-M2/M3 (ablation results inform interpretation)

**Source:** Phase 2A Section 1.6 Prediction P1 (primary), Section 5 sh2_mechanism

---

## 5. Execution Plan

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 — Root]
    H-E1 (EXISTENCE — no dependencies)
    Gate: MUST_WORK
         │
         ▼
[Level 1 — Core Mechanism]
    H-M1 ← H-E1
    Gate: MUST_WORK
         │
         ▼
[Level 2 — Ablation]
    H-M2 ← H-M1
    Gate: SHOULD_WORK
         │
         ▼
[Level 3 — Latent Quality]
    H-M3 ← H-M2
    Gate: SHOULD_WORK
         │
         ▼
[Level 4 — Primary Prediction]
    H-M4 ← H-M3
    Gate: MUST_WORK

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M4
All MUST_WORK gates must pass for Phase 5 eligibility
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | MUST_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │  W1-2   │  W3-4   │  W5     │  W6     │  W7
─────────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 0: Pre-validation (R1 mitigation)
  Graph validation   │ ██████  │         │         │         │
  SANE-ViT pilot     │ ██████  │         │         │         │
  [Gate 0: Go/No-Go] │      ◆  │         │         │         │
─────────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 1: Foundation
  H-E1 (MMD + train) │         │ ████████│         │         │
  [Gate 1: MUST PASS]│         │      ◆  │         │         │
─────────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 2: Mechanisms
  H-M1 (ablation)    │         │         │ ████████│         │
  H-M2 (scale vs perm│         │         │ ████████│         │
  [Gate 2: H-M1 MUST]│         │         │      ◆  │         │
  H-M3 (interpolation│         │         │         │ ████████│
  H-M4 (primary P1)  │         │         │         │         │ ████████
  [Gate 3: MUST PASS]│         │         │         │         │      ◆
─────────────────────┼─────────┼─────────┼─────────┼─────────┼────────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work │ ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

**Notes:**
- H-M1 and H-M2 share the same training runs (ablation ladder trained simultaneously)
- H-M3 and H-M4 share the same trained EquiSSL model
- Week 1-2 pre-validation (graph construction check + SANE pilot) is critical R1/R2 risk mitigation

### 5.4 Critical Path Analysis

```
Critical Path: Pre-validation (W1-2) → H-E1 (W3-4) → H-M1/M2 (W5) → H-M3 (W6) → H-M4 (W7)
Total Duration: 7 weeks
Slack Available: 0 weeks (fully sequential)

Duration Formula:
  2 (pre-validation + H-E1) + 1 (H-M1/M2 ablation) + 1 (H-M3) + 1 (H-M4) + 2 (training compute)
  = 7 weeks total
```

### 5.5 Resource Summary

```
Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1, H-M2, H-M3, H-M4)
- Condition: 0 (none — no testable conditions in PoC scope)

Verification Phases: 2 (Foundation + Core Mechanisms)
Total Duration: 7 weeks
Critical Path Length: 7 weeks

Compute Resources:
- Pre-validation: ~4h GPU (SANE inference on ViT zoo + graph validation)
- H-E1 training: ~48-72h A100 (EquiSSL, λ sweep 4 values, 5 seeds = 20 runs)
- Ablation: ~48-72h A100 (EquiSSL-perm, 5 seeds) + SANE reuse
- Evaluation: ~4h GPU (linear probe, MMD, interpolation)
```

### 5.6 Execution Order

1. **Step 0 (Pre-gate):** Graph construction validation for ViT zoo models + SANE-ViT pilot (2 seeds)
2. **Gate 0:** R1 validation: ViT graph construction <5% unrepresented parameters → proceed; if R2: SANE std > 0.07 → increase seeds to 10
3. **Step 1:** Train EquiSSL (λ sweep: {0.01, 0.1, 1.0, 10.0}, 5 seeds each) on SANE MultiZoo — 20 training runs
4. **Step 2:** Train EquiSSL-perm (neural-graphs + contrastive, 5 seeds) on same data
5. **Step 3:** Apply all encoders to ViT zoo; compute MMD ratios (H-E1), run ablation comparison (H-M1/M2)
6. **Gate 1:** H-E1 MUST_WORK (MMD ratio ≥ 2.0) → continue; FAIL → STOP
7. **Gate 2:** H-M1 MUST_WORK (graph encoders beat SANE) → continue; FAIL → STOP
8. **Step 4:** Evaluate latent interpolation on 500+ MLP pairs (H-M3)
9. **Step 5:** Full ViT zoo R² evaluation for H-M4 (primary P1)
10. **Gate 3:** H-M4 MUST_WORK (ΔR² ≥ 0.10) → Phase 5 eligibility; FAIL → detailed failure analysis

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** EquiSSL (scale+permutation equivariant SSL) achieves property prediction R² ≥ SANE+0.10 on held-out ViT zoo because: (1) computational graph representation eliminates architectural distribution shift; (2) monomial group equivariance normalizes cross-architecture weight magnitude variation; (3) contrastive autoencoder training creates discriminative functional latent space.

**Supporting Evidence:**
1. Kofinas 2024 ICLR Oral: graph representation enables zero-shot MLP→CNN transfer (R²=0.71 vs 0.59) — direct mechanistic precedent for Step 1
2. Kalogeropoulos 2024 NeurIPS Oral: scale equivariance improves R² by 8-12 points in supervised setting — supporting evidence for Step 2
3. Schürholt 2022 NeurIPS: pure reconstruction on weight zoo enables property prediction — foundation for Step 3's contrastive extension
4. Ballerini 2025: SSL cross-architecture transfer demonstrated for NeRF domain — cross-domain SSL transfer is feasible

**Expected Outcomes:**
- Primary (P1): R²(EquiSSL, ViT zoo) - R²(SANE, ViT zoo) ≥ 0.10
- Secondary (P2): MMD ratio (SANE/EquiSSL) ≥ 2.0
- Tertiary (P3): Latent interpolation accuracy > weight-space averaging (p < 0.05, 500+ pairs)

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in held-out ViT zoo property prediction R² between EquiSSL and SANE (delta R² < 0.05) when both trained on the same MLP+CNN data.

**Counter-Arguments:**
1. ViT attention mechanisms have fundamentally different operational semantics — the Q/K/V projections interact through softmax scores dependent on full input sequence context, not captured by the edge=weight graph schema alone
2. Scale equivariance's proven contribution was in supervised, same-architecture setting — the SSL cross-architecture extension may not benefit from scale normalization when the scaling transformation distribution differs between MLP/CNN and ViT weight statistics
3. SANE MultiZoo contains zero ViT-style attention mechanisms — SSL pre-training on non-attention architectures may not learn attention-weight statistics even with perfect graph representation

**Conditions Under Which H0 Would Be Supported:**
- If MMD ratio < 1.5 (graph representation does not reduce distribution shift) — H-E1 fails
- If both EquiSSL and EquiSSL-perm fail to improve over SANE (graph representation not helpful) — H-M1 fails
- If ΔR²(EquiSSL, ViT zoo) < 0.05 (full causal chain insufficient at specified threshold) — H-M4 fails

### 6.3 Synthesis

**Balanced Assessment:** The thesis has stronger empirical grounding (Kofinas 2024 provides direct evidence for graph schema cross-architecture generalization), while the antithesis correctly identifies three empirically open questions: attention semantic mismatch (R1), scale equivariance necessity in SSL (R4), and training diversity sufficiency (R5). The synthesis is a comparative effectiveness claim under uncertainty.

**Resolution Path:** The verification plan addresses this dialectic through:
1. **Pre-registered pilot (Gate 0):** Graph construction validation + SANE-ViT pilot calibrates threshold before committing compute — preventing post-hoc adjustment
2. **Foundation verification (H-E1):** Establishes distribution shift reduction independently of property prediction — mechanistic evidence (P2) supports or refutes the graph representation claim
3. **Ablation ladder (H-M1 → H-M2):** Tests graph representation vs equivariance contributions separately — produces findings regardless of outcome
4. **Gate conditions:** Allow early detection of H0 support at each step without wasting full compute budget

**Conditions for Thesis Support:**
- H-E1 passes (MMD ratio ≥ 2.0) AND H-M1 passes (graph > flat) AND H-M4 passes (ΔR² ≥ 0.10)

**Conditions for Antithesis Support:**
- H-E1 fails: MMD ratio < 1.5 — graph representation does not eliminate distribution shift
- H-M1 fails despite H-E1 passing: distribution shift reduced but not predictively useful
- H-M4 fails despite H-M1: graph + equivariance + contrastive training → insufficient ΔR²

**Nuanced Outcome Possibilities:**
1. **Full Support:** All MUST_WORK gates pass → Thesis validated; proceed to Phase 5
2. **Partial Support (scale unnecessary):** H-E1/M1/M4 pass, H-M2 fails → Refined thesis: "graph representation + permutation equivariance suffices" — still a publishable contribution
3. **Partial Support (interpolation fails):** H-E1/M1/M4 pass, H-M3 fails → Property prediction works but not generative editing; reduced claim
4. **No Support (mechanism fails):** H-E1 or H-M1 fails → Antithesis supported; root cause analysis and route to Phase 0

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | MMD ratio ≥ 2.0 from graph schema | ViT attention semantics break graph schema | H-E1 test + graph construction validation |
| Mechanism | Causal chain (4 steps) tested | Scale equivariance may not generalize to SSL | H-M1/M2 ablation ladder |
| Generalization | ViT zoo R² ≥ SANE+0.10 | Training diversity insufficient | H-M4 + SANE pilot calibration |
| Latent quality | Functional interpolation from contrastive training | λ conflict collapses reconstruction | H-M3 + λ sweep |

**Overall Robustness Score:** Medium-High (thesis has direct empirical precedents; antithesis raises legitimate but addressable concerns)
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-EquiSSL-v1 — Scale+Permutation Equivariant SSL achieves ViT zoo R² ≥ SANE+0.10 via computational graph representation + monomial group equivariance + contrastive autoencoder training
- ID: H-EquiSSL-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A data loaded, 33% scope reduction applied)
- Sub-Hypotheses: 5 total — H-E1 (1), H-M1-M4 (4), H-C (0)
- Phases: 2 phases (Foundation + Mechanisms) over 7 weeks
- Critical Gates: 3 MUST_WORK gates (H-E1, H-M1, H-M4) + 1 pre-validation gate

**Risk Assessment:** Medium
- Primary concerns: R1 (graph semantics mismatch, HIGH) — mitigated by pre-validation; R2 (statistical power, MEDIUM-HIGH) — mitigated by pilot variance estimation

**Immediate Action:** Execute pre-validation (graph construction check + SANE-ViT pilot, 2 seeds) before committing to full EquiSSL training

### 7.2 Conclusions

**Key Achievements:**
- 5 sub-hypotheses across 2 phases with complete verification protocols
- H0 addressed: "No significant difference between EquiSSL and SANE on ViT zoo (ΔR² < 0.05)"
- Ablation ladder (SANE → EquiSSL-perm → EquiSSL) designed for component-level attribution

**Verification Execution Order:**

**Phase 0: Pre-Validation** (Week 1-2)
- Graph construction validation for ViT zoo models (R1 mitigation)
- SANE-ViT pilot (2 seeds) for variance estimation (R2 mitigation)
- Gate 0: Go/No-Go before committing A100 compute

**Phase 1: Foundation** (Week 3-4)
- H-E1: Train EquiSSL on SANE MultiZoo; evaluate MMD ratio on ViT zoo
- Gate 1: MUST PASS — MMD ratio ≥ 2.0

**Phase 2: Core Mechanisms** (Week 5-7)
- H-M1/M2: Ablation ladder (all three models trained in Week 5, evaluated simultaneously)
- Gate 2: H-M1 MUST PASS — both graph encoders beat SANE
- H-M3: Latent interpolation on 500+ MLP pairs (Week 6)
- H-M4: Full ViT zoo R² evaluation (Week 7)
- Gate 3: MUST PASS — ΔR² ≥ 0.10, p < 0.05

**Critical Decision Points:**
1. **Gate 0:** Graph validation fails → SCOPE (exclude ViT models with problematic PE); variance too high → increase seeds to 10
2. **Gate 1 (Foundation):** H-E1 fails → STOP, reassess graph representation hypothesis
3. **Gate 2 (Mechanism):** H-M1 fails → STOP, report graph representation null result
4. **Gate 3 (Primary):** H-M4 fails → Detailed failure analysis across H-M1-M3; route to Phase 0 or Phase 2A dialogue for hypothesis refinement

**Open Questions (from Phase 2A):**
- What is SANE's actual R² on the ViT zoo? (requires pilot experiment before full training)
- Does λ hyperparameter sensitivity affect ViT generalization quality, or only same-architecture reconstruction?
- Can the hierarchical block-level scale equivariance be formalized mathematically for general attention architectures?
- Does latent interpolation quality (P3) correlate with property prediction R² (P1)?

**Recommendations:**
1. **Immediate Actions:**
   - Start graph construction validation today (no GPU required)
   - Run SANE-ViT pilot (2 seeds, ~4h A100) before any EquiSSL training
   - Pre-register success threshold based on pilot result

2. **Resource Allocation:**
   - Reserve ~100-150h A100 for full training (20 EquiSSL runs + 5 EquiSSL-perm + reuse SANE)
   - Buffer: +2 weeks if variance estimation requires expanding to 10 seeds

3. **Failure Management:**
   - Gate 1 fail: Document graph representation analysis; route to Phase 0 for alternative approach
   - Gate 2 fail: Report null result for graph representation; test flat tokenizer + contrastive training
   - Gate 3 fail: Report ΔR² < 0.10 with detailed ablation; refine threshold or approach in Phase 2A dialogue

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: /home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl/docs/youra_research/03_refinement.yaml (ID: H-EquiSSL-v1)
- Supplementary: 02_synthesis.yaml, 01_round_table/final_opinions.yaml

**B. MCP Tool Usage Summary**
- Total MCP calls: 6
- Tools used: scientificmethod (3x: H-E1, H-M1/M2, H-M3/M4), collaborativereasoning (1x: risk analysis), structuredargumentation (3x: thesis + antithesis + synthesis)
- Mode: Incremental (Phase 2A pre-seeded; 4-6 calls per workflow.md spec — at 6 total, within range)
