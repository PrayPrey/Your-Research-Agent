# Hypothesis Inventory
Generated: 2026-08-19
Source: Phase 2B Planning

## Main Hypothesis (h-c1)
**Statement:** LLMs exhibit model-specific behavioral coupling patterns across trustworthiness dimensions, measurable via co-occurrence analysis on existing benchmarks using only API access.

## Sub-Hypotheses

### H-E1: Coupling Exists (EXISTENCE | MUST_WORK)
**Statement:** At least one model exhibits statistically significant coupling (phi ≥ 0.3, p < 0.01) for at least one dimension pair.

**Type:** Foundation existence claim
**Gate:** MUST_WORK
**Prerequisites:** []
**Initial Status:** READY

**Rationale:** Validates basic premise - coupling is detectable. Without this, entire research direction fails.

**Success Criterion:** 
- ≥1 model shows ≥1 dimension pair with phi ≥ 0.3 AND p < 0.01

**Failure Implications:**
- All dimension pairs independent → hypothesis refuted
- Route to Phase 0 (new research direction needed)

---

### H-M1: Difficulty-Independent Coupling (MECHANISM | MUST_WORK)
**Statement:** Observed coupling persists when controlling for instance difficulty (partial phi ≥ 0.25), indicating shared vulnerability mechanisms rather than spurious difficulty correlation.

**Type:** Mechanism validation - distinguishes real coupling from confound
**Gate:** MUST_WORK
**Prerequisites:** [h-e1]
**Initial Status:** NOT_STARTED

**Rationale:** Critical objection from Phase 2A - hard prompts might fail on all dimensions. Difficulty control separates real coupling from spurious correlation.

**Success Criterion:**
- Partial phi ≥ 0.25 for ≥2 dimension pairs after controlling for model confidence scores

**Failure Implications:**
- Coupling disappears with difficulty control → was spurious
- Route to Phase 0 (coupling hypothesis invalid)

---

### H-M2: Multi-Pair Coupling (MECHANISM | SHOULD_WORK)
**Statement:** At least two models show ≥3 dimension pairs with medium-to-strong coupling (phi ≥ 0.3).

**Type:** Generalization across models and dimension pairs
**Gate:** SHOULD_WORK
**Prerequisites:** [h-e1, h-m1]
**Initial Status:** NOT_STARTED

**Rationale:** Strengthens claim beyond single isolated coupling. Demonstrates coupling is not rare edge case.

**Success Criterion:**
- ≥2 models show ≥3 dimension pairs with phi ≥ 0.3, p < 0.01

**Failure Implications:**
- Coupling exists but rare → publishable but weaker contribution
- Does NOT block Phase 5 (SHOULD_WORK gate)

---

### H-C1: Model-Specific Fingerprints (CONDITION | SHOULD_WORK)
**Statement:** Coupling matrices differ across models (Mantel test r < 0.7 for ≥1 model pair), demonstrating model-specific fingerprints.

**Type:** Differentiation claim - coupling as architectural signature
**Gate:** SHOULD_WORK
**Prerequisites:** [h-e1, h-m2]
**Initial Status:** NOT_STARTED

**Rationale:** Reframes universal coupling → model fingerprints. Enables deployment-critical model selection use case.

**Success Criterion:**
- Mantel test r < 0.7 between ≥1 model pair (GPT-4 vs Claude 3, GPT-4 vs Llama 3, or Claude 3 vs Llama 3)

**Failure Implications:**
- Models show identical coupling patterns → universal coupling (different framing, still publishable)
- Does NOT block Phase 5 (SHOULD_WORK gate)

---

## Dependency Graph

```
h-e1 (READY)
  └── h-m1 (depends on h-e1)
        ├── h-m2 (depends on h-e1, h-m1)
        │     └── h-c1 (depends on h-e1, h-m2)
```

## Gate Configuration

| Hypothesis | Gate Type | Effect on Phase 5 |
|------------|-----------|-------------------|
| H-E1       | MUST_WORK | FAIL → Phase 0    |
| H-M1       | MUST_WORK | FAIL → Phase 0    |
| H-M2       | SHOULD_WORK | FAIL → Continue   |
| H-C1       | SHOULD_WORK | FAIL → Continue   |

## Experimental Setup Summary

**Framework:** MMTrustEval
**Models:** GPT-4, Claude 3, Llama 3
**Dimensions:** truthfulness, robustness, fairness, safety, privacy
**Sample Size:** 500 instances per model
**Dimension Pairs:** 10 pairwise combinations

**Statistical Tests:**
- Phi coefficient (effect size)
- Chi-square (significance)
- Partial correlation (difficulty control)
- Mantel test (cross-model comparison)

