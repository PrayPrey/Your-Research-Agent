---
hypothesis_id: h-m1
generated_by: Phase 2C step-01 JIT generation
source: 02b_verification_plan.md
date: "2026-08-05"
---

# H-M1 Context: Graph Representation Architecture-Agnostic Semantics

## Hypothesis Info

**ID:** H-M1
**Type:** MECHANISM
**Gate:** MUST_WORK

**Statement:** Under the weight-space SSL setting, if directed computational graph encoding (node=neuron, edge=weight) is used for both MLP+CNN training zoo and ViT test zoo, then both EquiSSL and EquiSSL-perm (permutation-only) achieve higher ViT zoo property prediction R² than SANE (flat tokenizer), because the graph schema provides the same node/edge structure regardless of architecture family, eliminating the representational mismatch that prevents flat tokenizers from generalizing to novel architecture shapes.

**Rationale:** Tests causal step 1 — graph representation (not equivariance) as primary driver of cross-architecture generalization. Any advantage shared between BOTH graph encoders vs SANE confirms the graph representation hypothesis independently of equivariance.

## Experimental Setup (from Phase 2A/2B)

**Dataset:**
- Training: SANE MultiZoo (MLP+CNN, ~30k models) — github.com/HSG-AIML/MultiZoo-SANE
- Test: ViT Model Zoo (250 models, arXiv 2504.10231) — github.com/ModelZoos/ViTModelZoo
- Type: standard (real, public)

**Model:**
- SANE (flat tokenizer baseline): github.com/HSG-AIML/SANE
- EquiSSL-perm (neural-graphs + contrastive autoencoder): github.com/mkofinas/neural-graphs
- EquiSSL (ScaleGMN + contrastive autoencoder): github.com/jkalogero/scalegmn

**Variables:**
- Independent: Representation type (graph-based vs flat tokenizer)
- Dependent: ViT zoo property prediction R² (linear probe, frozen z, 5 seeds)
- Controlled: SSL objective (contrastive autoencoder for both graph encoders), training data (SANE MultiZoo)

## Verification Protocol (from Phase 2B)

1. Train three models: SANE, EquiSSL-perm (neural-graphs + contrastive), EquiSSL (ScaleGMN + contrastive) on identical SANE MultiZoo data
2. Apply frozen encoders to ViT Model Zoo (250 models); train linear probe (ridge regression) on 80% split
3. Evaluate on 20% test split; report R² ± std over 5 random seeds for all three methods
4. Confirm: R²(EquiSSL-perm) > R²(SANE) AND R²(EquiSSL) > R²(SANE)
5. Report paired t-test p-value for each comparison vs SANE baseline

## Success Criteria

- **Primary:** Both EquiSSL-perm and EquiSSL achieve R² > SANE on ViT zoo (p < 0.05)
- **Secondary:** Effect size R²(graph) - R²(SANE) > 0.05 for at least one graph encoder

## Gate Condition

**MUST_WORK** — If neither graph encoder beats SANE, graph representation hypothesis disconfirmed; STOP pipeline.

## Prerequisites

- H-E1: COMPLETED (PASS) — MMD ratio = 2.575 ± 0.070 (threshold ≥ 2.0 satisfied)

## Dependencies

- H-E1 must pass → CONFIRMED
- Shares trained models from H-E1 (EquiSSL encoder checkpoint from best λ=0.1 run)
- EquiSSL-perm requires additional training (5 seeds, same contrastive autoencoder objective)

## Baseline & Comparison Targets

| Method | Role | Source |
|--------|------|--------|
| SANE (flat tokenizer) | Baseline | github.com/HSG-AIML/SANE |
| EquiSSL-perm (neural-graphs) | Ablation (graph-only, perm equivariant) | github.com/mkofinas/neural-graphs |
| EquiSSL (ScaleGMN) | Proposed (graph + scale+perm equivariant) | github.com/jkalogero/scalegmn |

## Key Risk

**R1 (HIGH):** ViT attention graph semantics mismatch — Q/K/V projections have different operational semantics than MLP weight matrices.

**Mitigation:** Use neural-graphs hierarchical formulation which handles attention as MLP subgraphs (validated for ViT); Graph Metanetworks (GMN) paper shows explicit multi-head attention layer handling in parameter graphs.

## Lessons Learned from H-E1

- ScaleGMN with λ=0.1 best across all seeds; converges in ~50 epochs
- SANE baseline degenerates on scale-normalized weights (maps each arch to distinct constant)
- Test data was synthetic ViT-like zoo in H-E1; H-M1 uses real ViT zoo (critical difference)
- sklearn TSNE: use `max_iter` not deprecated `n_iter`
- MMD nan bandwidth issue: clamp σ > 1e-8 before division
