# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HOSCBM-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under conditions where domain ontologies with hierarchical structure (is-a, part-of relations) are available, if we organize the concept bottleneck layer according to the ontology hierarchy creating multi-resolution concept layers, then the model will achieve higher domain expert-assessed interpretability while maintaining competitive prediction accuracy, because hierarchical concept organization mirrors how scientists cognitively structure domain knowledge and enables coarse-to-fine scientific reasoning.

**Alternative Hypothesis (H0):**
Hierarchical ontology structure in concept bottleneck models provides no interpretability advantage over flat concept sets; domain experts cannot reliably distinguish HOS-CBM explanations from Label-Free CBM explanations, and any apparent improvement is due to increased model complexity rather than meaningful structural alignment with scientific knowledge organization.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Ontology hierarchy structure | Independent | OWL ontology with 3-5 hierarchy levels, parsed using OWL2Vec+ for concept embeddings | Depth: 3-5 levels, Concepts: 100-1000 per domain |
| Bottleneck architecture | Independent | HOS-CBM vs Label-Free CBM vs flat CBM baselines | Categorical: {HOS-CBM, LF-CBM, Flat-CBM} |
| Interpretability score | Dependent | Expert rating (1-5 Likert scale) of concept alignment with domain knowledge + automated concept consistency score | Rating: 1.0-5.0, Consistency: 0.0-1.0 |
| Prediction accuracy | Dependent | F1-score, accuracy on benchmark datasets | Accuracy: 70-95%, F1: 0.65-0.92 |
| Dataset domain | Controlled | Fixed to climate science (ENVO ontology) for primary experiments | ERA5 climate dataset |
| Model capacity | Controlled | ResNet-50 backbone, same hidden dimensions across conditions | Fixed architecture |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Ontology Parsing → Hierarchical Concept Embedding
    ↓
Step 2: Hierarchical Embedding → Multi-Resolution Bottleneck
    ↓
Step 3: Multi-Resolution Bottleneck → Interpretable Predictions
    ↓
[OUTCOME: Higher interpretability + competitive accuracy]
```

**Step 1: Ontology Parsing → Hierarchical Concept Embedding**
- OWL ontology structure is parsed and converted to multi-level concept representations
- OWL2Vec+ generates embeddings preserving taxonomic relations (is-a, part-of)

**Step 2: Hierarchical Embedding → Multi-Resolution Bottleneck**
- Concept embeddings at different hierarchy levels (L1: coarse, L2: medium, L3: fine) are aligned with learned features
- Contrastive loss aligns visual features to concept embeddings at each level

**Step 3: Multi-Resolution Bottleneck → Interpretable Predictions**
- Coarse-to-fine concept activations mirror scientific reasoning patterns
- Ontology consistency loss enforces parent ≥ max(child) constraint

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | OWL2Vec+ (2021) | Ontology embeddings preserve semantic hierarchy | Strong |
| Step2 → Step3 | Label-Free CBM (2023) | Feature-concept alignment via contrastive loss achieves validation | Strong |
| Step3 → Outcome | HINN (2025) | Hierarchical knowledge embedding improves neural network performance | Medium |

**Key Tension:**
- **Tension:** Label-Free CBM uses CLIP's general visual concepts which achieve broad coverage, but HOS-CBM uses domain-specific ontology concepts which may have incomplete coverage
- **Resolution:** Test whether ontology-structured concepts provide superior interpretability even with potentially reduced coverage

### 1.4 Key Assumptions

1. **Domain ontologies capture scientifically meaningful concepts relevant to prediction tasks**
   - Consequence if violated: Ontology concepts will not align with predictive features → HOS-CBM provides no advantage

2. **Ontology concepts can be grounded to learned representations through embedding alignment**
   - Consequence if violated: Multi-resolution bottleneck layers will have random activations → interpretability claims invalid

3. **Hierarchical structure provides useful inductive bias**
   - Consequence if violated: Flat concept bottlenecks will match or exceed HOS-CBM performance

4. **Domain experts can reliably assess scientific validity of concept activations**
   - Consequence if violated: Interpretability measurements will have high variance → inconclusive results

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Domains with formal ontologies: biology (Gene Ontology), chemistry (ChEBI), climate science (ENVO)
- Prediction tasks where domain concepts are visually/semantically groundable

**Where it does NOT apply:**
- Domains without established hierarchical ontologies
- Tasks where concepts are inherently flat

**Known limitations:**
- Ontology completeness for emerging phenomena
- Evaluation subjectivity requires careful protocol design

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Interpretability Improvement)**:
HOS-CBM will achieve significantly higher expert interpretability ratings than Label-Free CBM baseline.

*Measurement*:
- Expert rating (1-5 Likert scale) on concept alignment with domain knowledge
- Target: HOS-CBM rating ≥ 3.5, improvement over baseline with p < 0.05, Cohen's d > 0.5

**Secondary Predictions:**

**P2 (Ontology Consistency)**:
Concept activations will respect taxonomic constraints (parent ≥ max(child)) in ≥ 90% of test samples.

**P3 (Multi-Resolution Utility)**:
Coarse concepts (L1) provide high-level explanations, fine concepts (L3) provide specific details.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Expert interpretability rating for HOS-CBM ≤ baseline with p > 0.05
2. **Mechanism Failure**: Ontology consistency score < 70%
3. **Accuracy Collapse**: HOS-CBM accuracy drops >10% below Label-Free CBM baseline

### 1.7 Statistical Verification Design

**Sample Size:**
- Effect size target: Cohen's d = 0.6
- Power: 0.8, α = 0.05
- Required: n ≥ 30 expert evaluations per condition

**Test Specification:**
- Method: Independent samples t-test
- Report: Mean difference, 95% CI, Cohen's d, p-value
- Experimental runs: 5 random seeds per architecture

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can ontology hierarchy structure be successfully embedded into concept bottleneck architecture?"
- Verification type: Implementation + unit tests
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Does the hierarchical bottleneck structure cause improved interpretability through the proposed 3-step mechanism?"
- Phase 2B decomposes into 3 sub-hypotheses:
  - H-M1: Ontology parsing → embedding preserves hierarchy
  - H-M2: Embedding alignment → multi-resolution bottleneck functions correctly
  - H-M3: Multi-resolution bottleneck → interpretability improvement measurable
- Verification type: Ablation studies + mechanism probing

**SH3 (Comparison):**
"Does HOS-CBM outperform Label-Free CBM baseline on expert interpretability ratings?"
- Verification type: Comparative empirical evaluation
- Critical: Determines practical value

**Total sub-hypotheses:** 5 (SH1: 1, SH2: 3, SH3: 1)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-HOSCBM-v1
- [x] Confidence level: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=3 steps)
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] Testable predictions (P1, P2, P3)
- [x] Falsification criteria (3 conditions)
- [x] Baselines identified (Label-Free CBM, PG-CBM)
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Resource Requirements:** Estimate 1-2 A100 GPUs for 24-48 hours training on ERA5
2. **Data Availability:** Verify ENVO ontology coverage for ERA5 classification task
3. **Expert Availability:** Need 3-5 climate science domain experts for evaluation
4. **Priority Order:** SH1 → SH2-M1 → SH2-M2 → SH2-M3 → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (7 sources with citations)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
