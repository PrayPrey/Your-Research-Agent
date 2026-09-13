# Phase 2B: Verification Plan
## Benchmark Fingerprint Hypothesis

**Generated:** 2026-08-24  
**Main Hypothesis ID:** H-BenchmarkFingerprint-v1  
**Archon Project ID:** 6c932663-c983-48db-9ef4-e4048b949e72

---

## Main Hypothesis

**Statement:** Under fine-tuning scenarios on image classification tasks, if a model is fine-tuned on a single popular benchmark, then it will exhibit: (a) a detectable benchmark fingerprint in its representations, and (b) larger performance degradation on alternative same-domain datasets, because fine-tuning on narrow benchmark distributions causes models to encode benchmark-specific spurious features rather than task-general visual concepts.

**Null Hypothesis (H0):** There is no significant difference in cross-dataset generalization gap between models fine-tuned on single benchmarks versus mixed benchmarks, and benchmark fingerprint strength does not correlate with performance degradation.

---

## Sub-Hypotheses

### H-E1: Fingerprint Detectability (MUST_WORK)

| Field | Value |
|-------|-------|
| Type | EXISTENCE |
| Statement | A linear classifier trained on penultimate layer representations can predict which fine-tuning benchmark was used with >60% accuracy (chance=20% for 5 benchmarks) |
| Gate | MUST_WORK |
| Prerequisites | None |
| Status | READY |
| Success Criterion | Classification accuracy > 60% |
| Falsification | Accuracy ≤ 25% (near chance level) |
| Archon Task ID | a21a11ca-9304-419d-992a-4ab2c434a7b5 |

### H-M1: Gap Correlation (SHOULD_WORK)

| Field | Value |
|-------|-------|
| Type | MECHANISM |
| Statement | Benchmark Fingerprint Score (classifier confidence for true benchmark) correlates positively with cross-dataset performance gap (r>0.3, p<0.05) |
| Gate | SHOULD_WORK |
| Prerequisites | H-E1 |
| Status | NOT_STARTED |
| Success Criterion | r > 0.3, p < 0.05 |
| Falsification | r ≤ 0 or p > 0.1 |
| Archon Task ID | d649e6b1-e3a6-418c-9c3a-46c1d7d81929 |

### H-M2: Training Regime Effect (SHOULD_WORK)

| Field | Value |
|-------|-------|
| Type | MECHANISM |
| Statement | Models fine-tuned on a single benchmark show larger cross-dataset gap than models fine-tuned on a mix of 3+ benchmarks (>5 percentage points difference) |
| Gate | SHOULD_WORK |
| Prerequisites | H-E1 |
| Status | NOT_STARTED |
| Success Criterion | Single-benchmark gap > multi-benchmark gap + 5pp |
| Falsification | Multi-benchmark gap ≥ single-benchmark gap |
| Archon Task ID | 88cd81c2-dc8d-4b4b-abf7-8371f1436bc3 |

---

## Dependency Graph

```
H-E1 (MUST_WORK) ─┬─> H-M1 (SHOULD_WORK)
                  └─> H-M2 (SHOULD_WORK)
```

- H-E1 must pass before H-M1 and H-M2 can proceed
- H-M1 and H-M2 are independent of each other (can run in parallel)

---

## Risk Analysis

| Hypothesis | Risk Level | Risk Factors | Mitigation |
|------------|------------|--------------|------------|
| H-E1 | Low | Standard linear probing technique | Well-established methodology |
| H-M1 | Medium | Correlation may be weak; requires sufficient sample size | Use 3 seeds × 5 benchmarks = 15 models minimum |
| H-M2 | Medium | 5pp threshold may be aggressive | Report effect size with confidence intervals |

---

## Timeline

| Week | Activities |
|------|------------|
| Week 1 | Data preparation, fine-tune ResNet-50 on 5 benchmarks (3 seeds each) |
| Week 2 | H-E1: Extract features, train fingerprint classifier, evaluate |
| Week 2-3 | H-M1/H-M2: Cross-dataset evaluation, correlation analysis (parallel) |

**Estimated GPU Hours:** ~10 hours (fine-tuning) + ~2 hours (evaluation)

---

## Controlled Variables

| Variable | Value |
|----------|-------|
| Model Architecture | ResNet-50 |
| Pre-training | ImageNet-1K (torchvision) |
| Fine-tuning Epochs | 30 |
| Learning Rate | 0.01 with cosine annealing |
| Optimizer | SGD with momentum 0.9 |
| Seeds | 3 per condition |

---

## Datasets

| Dataset | Classes | Images | Role |
|---------|---------|--------|------|
| CUB-200-2011 | 200 | 11,788 | Fine-tuning benchmark |
| Stanford Dogs | 120 | 20,580 | Fine-tuning benchmark |
| Oxford Flowers 102 | 102 | 8,189 | Fine-tuning benchmark |
| Stanford Cars | 196 | 16,185 | Fine-tuning benchmark |
| FGVC Aircraft | 100 | 10,000 | Fine-tuning benchmark |
| NABirds | 555 | 48,562 | Validation (cross-dataset) |

---

## Dialectical Analysis

**Thesis:** Fine-tuning on single benchmarks creates detectable fingerprints that explain cross-dataset generalization gaps.

**Antithesis:** Cross-dataset gaps reflect inherent task differences (different label spaces, image distributions), not benchmark-specific encoding. Linear classifier may detect task features rather than spurious benchmark features.

**Synthesis:** By comparing within the fine-grained classification domain (all datasets share similar task structure), we control for task differences. The correlation analysis (H-M1) tests whether fingerprint strength predicts gap magnitude beyond what task similarity would explain. Multi-benchmark training (H-M2) provides a counterfactual: if gaps were purely task-based, mixed training would show similar gaps.

---

## Next Steps

1. **Phase 2C:** Generate detailed experiment design for H-E1
2. **Phase 3:** Implementation planning (PRD, Architecture, PRP)
3. **Phase 4:** Code generation and PoC validation
4. **Phase 5:** Baseline comparison (DETERMINES_SUCCESS gate)
