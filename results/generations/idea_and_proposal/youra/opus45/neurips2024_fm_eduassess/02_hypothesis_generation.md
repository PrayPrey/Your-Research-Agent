# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SAEF-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of LLM-based educational assessment with multiple stakeholders, if role-specific explanation templates constrained by educational ontologies (CEFR, Bloom's Taxonomy, Webb's DOK) are applied to SHAP feature attribution outputs, then stakeholder comprehension, trust calibration, and perceived actionability will significantly improve compared to generic XAI visualizations, because the explanations align with stakeholders' distinct mental models of educational assessment.

**Alternative Hypothesis (H0):**
There is no significant difference in comprehension, trust calibration, or actionability ratings between role-adapted explanations (SAEF) and generic explanations (SHAP visualizations, GPT-4 prompt-only, generic text) across different educational stakeholder types.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Stakeholder Type | Independent | Categorical classification: teacher, student, parent, administrator | 4 levels |
| Explanation Format | Independent | Categorical: SAEF (ontology-constrained), GPT-4 prompt-only, generic text, SHAP visualization | 4 conditions |
| Comprehension Score | Dependent | Quiz score measuring understanding of assessment rationale | 0-100% |
| Trust Calibration | Dependent | Confidence-accuracy correlation coefficient (r) | -1.0 to +1.0 |
| Actionability Rating | Dependent | Likert scale rating on perceived usefulness for next steps | 1-7 scale |
| Cognitive Load | Controlled | NASA-TLX subscales, held constant via template design | Fixed baseline |
| Essay Quality Level | Controlled | Pre-categorized essay quality: low/medium/high scoring | 3 levels, balanced |
| Assessment Domain | Controlled | Fixed to English language essay scoring | Constant |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: SHAP Feature Extraction → Educational Ontology Mapping
   ↓
Step 2: Ontology Mapping → Template-Constrained Generation
   ↓
Step 3: Template Generation → Stakeholder Comprehension/Trust/Actionability
   ↓
[OUTCOME]: Improved stakeholder understanding and trust in LLM assessment
```

**Step 1: Feature Extraction → Ontology Mapping**
Technical features from SHAP analysis (e.g., 'coherence_score=0.7') are translated to educational ontology concepts (e.g., 'Learning Objective 2.1: thesis clarity').

**Step 2: Ontology Mapping → Template Generation**
Educational concepts are formatted using role-specific templates matching stakeholder mental models.

**Step 3: Template Generation → Stakeholder Outcomes**
Role-aligned explanations reduce cognitive load and improve understanding because format matches mental model.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | SHAP + CEFR/Bloom's | SHAP values interpretable; CEFR/Bloom's provide standardized vocabulary | Strong |
| Step 2 → Step 3 | Mohammed (2025) | Adaptive XAI: +27% comprehension, +19% trust, +22% accuracy | Strong |
| Step 3 → Outcome | Haas et al. (2024) | Stakeholder-centric XAI increases trust across all types | Medium |

**Key Tension:**
- **Tension:** Mohammed (2025) validates expertise-level adaptation, but educational stakeholders differ by role (categorical). Transfer validity uncertain.
- **Resolution:** This verification plan tests role-based adaptation specifically in educational assessment context.

### 1.4 Key Assumptions

1. **Educational stakeholders have distinct mental models** (Hoffman 2023, Haas 2024)
   - If violated: Role-based adaptation provides no advantage

2. **LLM decisions decompose into interpretable features** (SHAP, IELAT 2025)
   - If violated: Ontology mapping becomes arbitrary

3. **NLG maintains semantic fidelity to XAI** (BERTScore > 0.7)
   - If violated: Explanations mislead stakeholders

4. **Satisfaction correlates with role adaptation** (Mohammed 2025)
   - If violated: Framework complexity not justified

### 1.5 Scope & Boundaries

**Applies to:**
- LLM-based essay/writing assessment with structured rubrics
- Educational contexts with multiple defined stakeholder roles
- Assessment domains with established ontologies

**Does NOT apply to:**
- Unstructured assessment without rubrics
- Non-educational domains
- Real-time feedback during writing
- Pure end-to-end models without feature extraction

**Limitations:**
- Ontology construction requires domain expertise
- Template approach may feel formulaic
- Multi-stakeholder evaluation increases study complexity

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Comprehension Improvement):**
SAEF explanations → comprehension scores significantly higher than GPT-4 prompt-only.

*Measurement:*
- Comprehension > 75% for SAEF
- SAEF > GPT-4 by ≥10 percentage points
- p < 0.05

*Falsification:* Comprehension (SAEF) ≤ Comprehension (SHAP visualization)

**Secondary Predictions:**

**P2 (Trust Calibration):**
Role-adapted explanations → trust calibration improves by >15% (Δr > 0.15)

**P3 (Actionability):**
SAEF → actionability rating > 5.5/7 vs. generic < 4.5/7

**Falsification Criteria:**

1. **Primary Failure:** Comprehension (SAEF) ≤ Comprehension (SHAP)
2. **Mechanism Failure:** BERTScore fidelity < 0.7
3. **Comparative Failure:** No significant difference on any measure

### 1.8 Statistical Verification Design

**Sample Size:**
- Effect size (d): 0.5, Power: 0.8, α: 0.05
- Design: 4×4 mixed (stakeholder × format)
- Required: n ≥ 30/cell = 480 total

**Analysis:**
- 4×4 mixed-design ANOVA
- Post-hoc: Tukey HSD
- Report: Mean ± SD, 95% CI, effect sizes

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does role-adapted explanation generation produce measurably different outputs across stakeholder types?"
- Verification: Empirical content analysis + human evaluation
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the three-component pipeline the actual cause of improved outcomes?"
- Decomposes to: H-M1 (extraction), H-M2 (ontology), H-M3 (templates)
- Verification: Ablation study + fidelity analysis

**SH3 (Comparison):**
"Does SAEF outperform baselines across all outcome measures?"
- Verification: Comparative empirical study

**Total sub-hypotheses:** 5 (1 + 3 + 1)

### Readiness Checklist

- [x] Hypothesis in "If X, then Y because Z" format
- [x] Hypothesis ID: H-SAEF-v1
- [x] Confidence: 0.82
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=3)
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] 3 testable predictions (primary marked)
- [x] Falsification criteria defined
- [x] 4 baselines identified
- [x] SH1/SH2/SH3 ready

### Open Questions

1. **Resources:** Single GPU for SHAP extraction; standard compute for generation
2. **Data:** ASAP dataset (12K+ essays); stakeholder recruitment needed
3. **Ontology Validation:** Expert panel (3-5 educational measurement specialists)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
