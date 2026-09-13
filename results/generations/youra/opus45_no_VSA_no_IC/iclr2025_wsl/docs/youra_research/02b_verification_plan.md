# Phase 2B Verification Plan
## H-EquivariantDataEfficiency-v1

**Generated**: 2026-08-24T09:28:30Z  
**Archon Project ID**: `2ecbc2dd-b2cc-459b-b1b8-6ff3e20e6b2e`

---

## Main Hypothesis

**Statement**: Under fixed-architecture homogeneous model zoos (ResNet-20/CIFAR-10), permutation-equivariant architectures (NFN) achieve equivalent accuracy prediction R² with ≤50% of training samples compared to MLP baselines, because equivariance eliminates the need to learn permutation invariance from data.

**Predictions**:
- P1: NFN R² > MLP R² + 0.1 at N=500 (p < 0.05)
- P2: All methods within R² ±0.03 at N=5000
- P3: Crossing point N* < 2500 where NFN matches Statistics

---

## Sub-Hypotheses

| ID | Type | Statement | Gate | Prerequisites | Status |
|----|------|-----------|------|---------------|--------|
| H-E1 | EXISTENCE | Model Zoo ResNet-20/CIFAR-10 weights have learnable accuracy-correlated features; Statistics baseline achieves R² > 0.85 | MUST_WORK | None | READY |
| H-M1 | MECHANISM | NFN equivariant layers extract permutation-invariant features architecturally without data augmentation | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | At N=500 training models, NFN R² exceeds MLP R² by at least 0.1 (p < 0.05) | MUST_WORK | H-M1 | NOT_STARTED |
| H-C1 | CONDITION | At N=5000, all three methods achieve R² within ±0.03 | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-C2 | CONDITION | Crossing point N* where NFN matches Statistics R² exists at N* < 2500 | SHOULD_WORK | H-M2 | NOT_STARTED |

---

## Dependency DAG

```
H-E1 (Foundation)
  └─→ H-M1 (NFN Validation)
        └─→ H-M2 (Data Efficiency - P1)
              ├─→ H-C1 (Convergence - P2)
              └─→ H-C2 (Crossing Point - P3)
```

---

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| A3: NFN implementation correctness | Use official `nfn` library (pip installable, NeurIPS 2023) |
| Low accuracy diversity in model zoo | Verified: Model Zoo paper shows 70-95% accuracy range |
| R² ceiling effect at large N | Focus analysis on small-N regime (N ≤ 1000) |
| Statistical power | 10 seeds per condition with confidence intervals |

---

## Timeline Estimate

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C | All (parallel start, H-E1 first) | ~2 days |
| Phase 3 | Per hypothesis | ~2 days each |
| Phase 4 | Per hypothesis | ~3 days each |
| Phase 5 | Baseline comparison | ~2 days |

---

## Archon Task Mapping

| Hypothesis | Task ID |
|------------|---------|
| H-E1 | `76c55ce8-02b3-4d70-b1d5-b539882293b9` |
| H-M1 | `c0f58027-a062-461f-85b4-edf3f87709f9` |
| H-M2 | `e978bdf0-178e-4904-8249-3e6bad2a2eeb` |
| H-C1 | `8d4d3945-8890-49e7-8cc6-9b702e71f66d` |
| H-C2 | `62c23330-7d3a-4069-bfa1-e441987059f6` |

---

## Controlled Variables

- **Dataset**: CIFAR-10
- **Architecture**: ResNet-20 (homogeneous model zoo)
- **Training sizes**: N ∈ {100, 250, 500, 1000, 2500, 5000}
- **Test size**: 500 held-out models (fixed)
- **Seeds**: 10 per (N, method) pair

---

## Next Action

Begin Phase 2C with H-E1 (status: READY).
