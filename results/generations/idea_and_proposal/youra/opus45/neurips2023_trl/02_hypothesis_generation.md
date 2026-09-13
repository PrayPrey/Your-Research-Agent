# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SACTT-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of schema evolution (column additions, deletions, type changes), if table transformer models use prototype-based column encoding with confidence-aware dynamic binding and continual regularization, then they will maintain >90% performance retention while achieving >70% zero-shot accuracy on new columns, because prototype banks provide stable semantic anchors that decouple concept semantics from schema-specific encodings while EWC-style regularization protects important parameters during adaptation.

**Alternative Hypothesis (H0):**
Prototype-based column encoding with continual regularization provides no significant advantage over standard positional encoding approaches for handling schema evolution; performance retention and zero-shot accuracy are primarily determined by model size and training data volume rather than the proposed architectural components.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Prototype Bank Usage | Independent | Binary: prototype-based encoding vs fixed positional embedding | {0: fixed, 1: prototype} |
| Continual Regularization | Independent | Binary: EWC-style regularization vs standard fine-tuning | {0: standard, 1: EWC} |
| Confidence-Aware Binding | Independent | Binary: confidence-based routing vs static column mapping | {0: static, 1: confidence-aware} |
| Performance Retention | Dependent | Accuracy on original schema tasks after schema change (%) | Target: >90% |
| Zero-Shot Accuracy | Dependent | Accuracy on new columns without retraining (%) | Target: >70% |
| Downstream Task Performance | Dependent | Text-to-SQL accuracy on EvoSchema benchmark (%) | Baseline-relative improvement |
| Model Architecture | Controlled | Fixed transformer backbone (e.g., BERT-base) | BERT-base-uncased |
| Training Data Size | Controlled | Fixed corpus (WebTables/GitTables) | ~1M tables |
| Evaluation Benchmark | Controlled | EvoSchema benchmark with 10 perturbation types | 10 perturbation types |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Prototype Bank Learning
    │
    ▼
Step 2: Confidence-Aware Binding
    │
    ▼
Step 3: Continual Regularization
    │
    ▼
[Outcome: Schema-Adaptive Representations]
```

**Step 1 (Prototype Bank Learning):**
Clustering column representations from large table corpus → Discover natural semantic concepts (~100-500 prototypes) → Provides stable semantic anchors independent of any specific schema structure.

**Step 2 (Confidence-Aware Binding):**
New column metadata (name, type, sample values) → Attention-based prototype matching with confidence score → High confidence: route to closest prototype; Low confidence: trigger few-shot learning for novel concepts.

**Step 3 (Continual Regularization):**
Schema change event → EWC identifies important parameters via Fisher Information Matrix → Protects prototype embeddings while allowing binding layer adaptation → Outcome: Retained past performance + adapted representations for new schema.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Relational Transformer (2025) | Cell-level tokenization achieves 94% zero-shot accuracy | Strong |
| Step2 → Step3 | CEL with EWC (2024) | EWC reduces forgetting by 65% in continual learning settings | Strong |
| Step3 → Outcome | KG-EWC (2025) | EWC reduces catastrophic forgetting by 45.7% in knowledge graphs | Medium |

**Key Tension:**
EvoSchema (2025) shows table-level perturbations have significantly greater impact than column-level changes, but SACTT's prototype-based approach primarily addresses column-level semantics. This verification plan tests whether prototype binding can generalize to table-level schema changes through hierarchical prototype organization.

### 1.4 Key Assumptions

1. **Semantic concept finiteness:** Semantic column concepts are finite and clusterable (~100-500 prototypes)
   - Evidence: WebTables/GitTables contain millions of tables but limited unique semantic column types
   - Consequence if violated: Prototype bank would require exponential growth, negating efficiency benefits

2. **Metadata sufficiency:** Column metadata (name, type, sample values) provides sufficient signal for prototype binding
   - Evidence: Relational Transformer achieves 94% zero-shot using cell-level tokenization
   - Consequence if violated: Would require additional context (e.g., full table structure, documentation) increasing complexity

3. **EWC transferability:** EWC-style regularization transfers from vision/NLP to tabular domain
   - Evidence: CEL (2024) applies EWC to time-series; KG-EWC (2025) applies to knowledge graphs
   - Consequence if violated: Need domain-specific regularization methods; EWC hyperparameters may require extensive tuning

### 1.5 Scope & Boundaries

**Applies to:**
- Relational tables with schema metadata (column names, types)
- Text-to-SQL and table QA downstream tasks
- Tables with evolving schemas (production databases, data lakes)

**Does NOT apply to:**
- Completely unstructured data without column identifiers
- Tables with purely numeric column names (col1, col2) without any semantic signal
- Real-time schema changes requiring sub-second adaptation

**Known Limitations:**
- May require few-shot examples for highly domain-specific concepts (e.g., specialized medical terminology)
- Initial prototype pre-training requires substantial compute (~100 GPU-hours estimated)
- Confidence threshold requires validation-set tuning per domain

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Performance Retention Target):**
SACTT will achieve performance retention >90% on original schema tasks after schema evolution events (column additions, deletions, renames).

*Measurement*:
- Retention rate = (Accuracy_after_change / Accuracy_before_change) × 100%
- Statistical test: One-sample t-test against 90% threshold, n ≥ 20 runs, p < 0.05

*Basis*:
Domain standard for continual learning is 85-95% retention. CEL achieves 65% forgetting reduction; we target top of range.

*Success Criteria for Phase 2B*:
- Primary: Retention rate > 90% (p < 0.05)
- Falsification: Retention rate ≤ 75% triggers rejection (>25% below target)

**Secondary Predictions:**

**P2 (Zero-Shot Generalization):**
Novel columns mapped to known prototypes with high confidence (>0.8) will achieve >70% zero-shot accuracy on downstream tasks without any fine-tuning.

**P3 (Prototype Stability):**
If prototype bank grows incrementally via few-shot learning for novel concepts, then no catastrophic forgetting on previously learned concepts (retention >95% on original prototypes).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: Performance retention ≤ 75% (>25% below 90% target)
2. **Mechanism Failure**: Zero-shot accuracy on high-confidence bindings ≤ 50% (no better than random)
3. **Baseline Failure**: No statistically significant improvement over TAPAS/TaBERT fine-tuning baseline

### 1.7 SOTA Baseline (Optional)

*Not applicable - Absolute Performance Mode selected*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large effect expected)
- Required runs: n ≥ 20 per condition
- Statistical power: 0.8

**Test Specification:**
- Method: Independent samples t-test (SACTT vs baselines)
- Additional: Paired t-test for before/after schema change
- Significance level: α = 0.05 (two-tailed)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does prototype-based column encoding with confidence-aware binding enable table transformers to maintain functionality after schema evolution events?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the three-component mechanism (prototype learning → confidence binding → continual regularization) the actual cause of schema adaptation capability?"
- Maps to: Causal mechanism (N=3 causal links)
- Phase 2B will decompose into:
  - H-M1: Prototype bank provides semantic anchoring
  - H-M2: Confidence-aware binding correctly routes columns
  - H-M3: EWC regularization prevents catastrophic forgetting
- Verification type: Causal analysis (ablation studies)
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does SACTT outperform baseline approaches (TAPAS, TaBERT, column-name embedding) on schema evolution robustness?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-SACTT-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table provided)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 provided, primary marked)
- [x] Falsification criteria are defined (3 failure conditions)
- [x] Baselines are identified for comparison (TAPAS, TaBERT, column-name)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What is the compute budget for prototype pre-training? (Estimated: ~100 GPU-hours on A100)
2. **Data Availability:** Can we access EvoSchema benchmark data directly, or need to generate perturbations ourselves?
3. **Priority Verification Order:** Should we validate SH1 (existence) first before investing in full mechanism testing (SH2)?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
