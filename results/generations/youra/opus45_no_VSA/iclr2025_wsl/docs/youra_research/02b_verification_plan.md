# Phase 2B Verification Plan
## H-CVPR-v1: CV of Participation Ratio as Model Quality Signal

Generated: 2026-08-10
Archon Project ID: afad20c1-f52e-4ead-b527-3c35cf4511e8

---

## Main Hypothesis

**Statement**: Under pretrained image classification models from timm (n >= 100), if we compute the coefficient of variation (CV) of participation ratio across 20 randomized SVD seeds and aggregate layer-wise metrics via mean, then CV_PR correlates negatively with model accuracy (r < -0.3, p < 0.05), because CV reflects spectral shape — flatter decay enables better generalization.

**H0**: No significant negative correlation between CV_PR and model accuracy (r >= 0 or p >= 0.05).

---

## Sub-Hypotheses

### H-E1: CV-PR Extraction Feasibility
- **Type**: EXISTENCE
- **Gate**: MUST_WORK
- **Statement**: CV_PR can be reliably extracted from 100+ timm models using randomized SVD with 20 seeds
- **Success**: Extraction completes for all models with consistent methodology
- **Archon Task**: 0adc27b2-b921-4fd9-b7f3-655863f24553

### H-E2: P1 Core Correlation (PRIMARY)
- **Type**: EXISTENCE  
- **Gate**: MUST_WORK
- **Statement**: CV_PR correlates negatively with ImageNet accuracy (r < -0.3, p < 0.05)
- **Success**: Pearson r < -0.3 with p < 0.05
- **Falsification**: r >= 0 or p >= 0.05
- **Archon Task**: 6c7eed7e-4e6f-4f92-b4dc-c7c6a13c32d7
- **Prerequisites**: H-E1

### H-M1: P2 Mechanism Specificity
- **Type**: MECHANISM
- **Gate**: SHOULD_WORK
- **Statement**: Partial correlation CV_PR-accuracy remains significant after controlling for condition number
- **Success**: Partial r significant at p < 0.05, |r| > 0.1
- **Falsification**: Partial r non-significant or |r| < 0.1
- **Archon Task**: cdbcbc20-e099-4665-976c-5712643897ca
- **Prerequisites**: H-E2

### H-M2: P3 Architecture-Aware Correlation
- **Type**: MECHANISM
- **Gate**: SHOULD_WORK
- **Statement**: Within ResNet family, correlation is stronger than cross-family pooled
- **Success**: |r_within_ResNet| > |r_cross_family|
- **Falsification**: Within-family correlation weaker or equal
- **Archon Task**: 11888c54-3f42-49bd-8151-d17b4a866be3
- **Prerequisites**: H-E2

---

## Dependency Graph (DAG)

```
H-E1 (Extraction Feasibility)
  │
  └──► H-E2 (P1 Core Correlation) [MUST_WORK]
         │
         ├──► H-M1 (P2 Mechanism Specificity) [SHOULD_WORK]
         │
         └──► H-M2 (P3 Architecture-Aware) [SHOULD_WORK]
```

**Execution Order**: H-E1 → H-E2 → (H-M1 || H-M2)

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Effect size too weak (r ~ -0.2) | Medium | High | Pre-register -0.3 threshold; report actual r |
| Confound: parameter count | Medium | Medium | Control via partial correlation |
| timm accuracy metadata incomplete | Low | Medium | Verify metadata availability first |
| SVD convergence issues on large weights | Low | Low | Set max matrix dimension |

---

## Timeline (Gantt)

```
Week 1: H-E1 (Extraction pipeline)
  ├── Phase 2C: Experiment design
  ├── Phase 3: Implementation planning  
  └── Phase 4: Validation

Week 2: H-E2 (Core correlation test)
  ├── Phase 2C: Statistical analysis design
  ├── Phase 3: Analysis pipeline
  └── Phase 4: Correlation validation

Week 3: H-M1 + H-M2 (Mechanism tests) [PARALLEL]
  ├── Partial correlation analysis
  └── Within-family stratification
```

---

## Dialectical Analysis

### Thesis
CV of participation ratio captures spectral shape information that correlates with model generalization quality. Low CV indicates flatter spectral decay and better-conditioned weights.

### Antithesis
- CV may just measure numerical noise, not spectral properties
- Effect size may be too weak for practical utility (r ~ -0.3 = 9% variance)
- Aggregation scheme (mean across layers) may lose signal

### Synthesis
The hypothesis is testable with clear falsification criteria. P1 is the primary gate with quantitative threshold. P2 tests mechanism specificity. Even if r = -0.3, the contribution is novel (first use of estimator variance as quality signal). Aggregation ablation should be included in Phase 4.

---

## Controlled Variables

- **Dataset**: ImageNet-1K pretrained models only
- **SVD Seeds**: 20 per layer (fixed across all models)
- **Layer Types**: conv2d, linear only
- **Architecture Families**: ResNet, ViT, EfficientNet, ConvNeXt

---

## Phase 5 Gate

**Type**: DETERMINES_SUCCESS
**Baseline**: Unterthiner et al. 2020 features (R² > 0.98 cross-architecture)
**Our Target**: Demonstrate within-family improvement or complementary signal
