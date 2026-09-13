# Phase 2A Extended: Hypothesis Summary for Phase 2B

**Hypothesis ID:** H-IDDC-001
**Title:** Interpretability-Driven Data Curation (IDDC) Framework for Foundation Models
**Confidence:** 0.78 (Medium-High)
**Date:** 2026-02-08

---

## Core Hypothesis

Training foundation models on data curated with **interpretability-inducing structural properties** produces significantly more interpretable models while maintaining performance:

**Three Data Properties:**
1. **Concept Prototype Organization** (silhouette score ≥ 0.65)
2. **Contrastive Structure** (≥30% coverage with annotated differences)
3. **Reasoning Chain Scaffolding** (≥20% coverage with intermediate steps)

**Expected Outcomes:**
- **Interpretability:** Composite score ≥ 0.75 (prototype alignment, linear separability, attention correlation)
- **Human Evaluation:** ≥4.0/5.0 on Likert scale (+60% over random sampling)
- **Performance:** ≤2% accuracy drop vs baseline (maintains task capability)

---

## Causal Mechanism

```
Interpretability-Inducing Data Structure
   ↓ (Training via gradient descent)
Structured Learned Representations
   ↓ (Prototype alignment, linear separability, attention alignment)
Interpretable Model Behavior
```

**Key Evidence:**
- Contrastive learning transfer (SimCLR, CLIP) validates cognitive principle transfer
- Meta's ssl-data-curation demonstrates hierarchical clustering produces structured representations
- Prototype theory (cognitive science) provides theoretical foundation

---

## Sub-Hypotheses (Phase 2B Decomposition)

### SH1: Existence
**Can we construct FM-scale datasets with interpretability-inducing properties?**
- Target: silhouette ≥ 0.65, contrastive ≥ 30%, reasoning ≥ 20%
- Approach: ssl-data-curation + embedding-based pair generation + semi-automated annotation

### SH2: Mechanism
**Do interpretability-inducing properties improve learned representation interpretability?**
- Metrics: Prototype alignment ≥ 0.75, linear separability ≥ 0.80, attention correlation ≥ 0.70
- Test: One-way ANOVA (IDDC vs random sampling vs performance-only), p < 0.01

### SH3: Comparison
**Do IDDC models achieve higher human-evaluated interpretability AND maintain performance?**
- Human eval: ≥4.0/5.0 (crowdsourced, n=100 samples)
- Performance: Within 2% of baseline (TOST equivalence test)
- Validation: Auto metrics correlate with human eval (Spearman ρ > 0.70)

---

## Implementation Plan

**Tools:**
- Meta ssl-data-curation (hierarchical clustering for prototypes)
- NVIDIA NeMo-Curator (pipeline infrastructure)
- HuggingFace datatrove (modular processing)

**Datasets:**
- Vision: ImageNet (1.3M samples)
- Language: C4 (100M+ tokens)

**Validation:**
- **Pilot:** ResNet-50, GPT-2 (2-4 weeks)
- **Full FM:** If pilot succeeds (8-12 weeks)
- **Human Eval:** 100 samples × 3 raters = 300 judgments per condition

**Budget:**
- Reasoning chain annotation: <$10K (crowdsourcing)
- Compute: Standard 1-8 GPU setup (equivalent to baseline FM training)

---

## Falsification Criteria

Hypothesis **FALSIFIED** if:
1. No interpretability improvement (p > 0.05 across all metrics)
2. Performance collapse (>5% accuracy drop)
3. Proxy-human mismatch (correlation r < 0.50)
4. No Pareto solution (zero configs meet both interpretability + performance targets)

---

## Contribution

**Theoretical:** First framework connecting data structure → FM interpretability (fills Gap 2)
**Methodological:** Multi-objective curation with three cognitive science-inspired properties
**Practical:** +60% interpretability improvement while maintaining performance (≤2% drop)

**Novel Synergy:** Combines (1) cognitive principles, (2) multi-objective optimization, (3) production-scale curation—no existing work integrates all three.

---

## Phase 2B Next Steps

1. **Decompose** into SH1 (existence), SH2 (mechanism), SH3 (comparison)
2. **Design experiments** for each sub-hypothesis with statistical power analysis
3. **Define baselines** (random sampling, performance-only curation, model-centric interpretability)
4. **Specify metrics** and validation protocols (human evaluation, inter-rater reliability)
5. **Create verification roadmap** with prioritized experiments and success criteria

---

**Full Document:** `02a_extended_hypothesis_full.md`
**Status:** Ready for Phase 2B Verification Planning
