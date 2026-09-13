# Hypothesis Context: H-M4

**Generated:** 2026-04-24
**Source:** 02b_verification_plan.md

---

## Hypothesis Information

**ID:** H-M4
**Type:** MECHANISM (Step 4 of 4)
**Prerequisites:** H-M3 (SGD flow dynamics established)
**Gate:** SHOULD_WORK

**Statement:** At convergence, if solutions have lower minority-gradient alignment A(w) (from H-M3 SGD flow), then they will exhibit better worst-group accuracy, because functional coupling between geometry and phenotype within mode-connected manifolds means geometric regions determine robustness outcomes.

**Rationale:**
Final causal link: validates functional coupling—geometry (A(w)) predicts phenotype (worst-group accuracy), not just correlation but causal relationship via FGE sampling.

---

## Experimental Setup

**Dataset:** Waterbirds (primary), CelebA + Colored MNIST (cross-validation)
- Source: group_DRO repository (https://github.com/kohpangwei/group_DRO)
- Path: Downloaded via group_DRO scripts
- Type: Standard dataset with ground-truth spurious labels

**Model:** ResNet-50
- Type: Standard CNN with skip connections
- Source: torchvision.models
- Justification: Li et al. show ResNets produce analyzable loss landscapes with skip connections

**Controlled Variables:**
- Batch sizes: [32, 128, 512]
- Random seeds: 20 runs
- Architecture: ResNet-50

---

## Variables

**Independent:** Curvature alignment A(w)
**Dependent:** Worst-group accuracy (WGA)
**Controlled:** Architecture, dataset, connectivity path (FGE vs linear)

---

## Verification Protocol

1. Sample solutions along FGE-optimized paths (M=20 checkpoints between ERM and DRO)
2. For each checkpoint, compute A(w) and measure worst-group accuracy
3. Calculate Spearman correlation ρ(A(w), WGA) to test monotonic coupling
4. Validate via linear interpolation (simpler path, no optimization)
5. Test robustness to 10% minority label noise

---

## Success Criteria (PoC: Direction-based)

**Primary:** FGE shows strong coupling ρ(A(w), WGA) > 0.6, p<0.01
**Secondary:** Linear interpolation shows monotonic coupling ρ>0.7

---

## Failure Response

IF fails: Document as geometry variation without phenotype variation (falsifies A5)

---

## Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Standard ERM | 85-90% average, 60-75% worst-group | Waterbirds, CelebA |
| Group-DRO | 75-80% worst-group (requires group labels) | Waterbirds, CelebA |
| Fast Geometric Ensembling (FGE) | Cyclical learning rate sampling | Waterbirds |

---

## Dependencies

**Prerequisite Results (from H-M3):**
- SGD trajectory shows directional bias: 0.15
- Bulk alignment (0.62) > Outlier alignment (0.47)
- Statistical significance: p=0.023
- Mechanism validated - SGD prefers flat directions over sharp directions

**Chain Context:**
- H-E1: ERM alignment (0.7234) > DRO alignment (0.3156), p=0.0023
- H-M1: ERM exhibits 23 outlier eigenvalues vs 15 for DRO
- H-M2: Minority alignment (0.844) > majority alignment (0.155)
- H-M3: SGD directional bias toward flat directions confirmed

---

*This context file enables Phase 2C to design experiments without loading full roadmap*
