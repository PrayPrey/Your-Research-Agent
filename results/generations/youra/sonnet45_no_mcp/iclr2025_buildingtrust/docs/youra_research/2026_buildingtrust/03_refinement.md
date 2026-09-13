# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-04-14T10:35:14.581282Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: GAP-001
- **Gap Title**: Interpretable Error Taxonomy for LLM Benchmark Failures
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All convergence criteria met - specific claim with quantitative thresholds, 4-step causal mechanism explained, four testable predictions with falsification criteria, novelty articulated (diagnostic framing + temporal dimension), feasibility validated (all data available, no API dependency), major objections addressed (expert recruitment budget, granularity gap mitigation, baseline comparisons defined)

### Key Insights

1. **Diagnostic Pivot**: Exchange 7 breakthrough - Dr. Nova's pivot from prediction to diagnostic framing resolved feasibility concerns and clarified success criteria
2. **Expert Validation Framework**: Exchange 8 - Prof. Vera established rigorous Cohen's kappa framework as interpretability gold standard
3. **Temporal Dimension**: Exchanges 13-14 scoped temporal analysis to feasible two-timepoint comparison (baseline vs current models)
4. **API Elimination**: Throughout discussion, emphasis on using ONLY published results avoids h-e1 failure mode

### Breakthrough Moments

- **Exchange 1**: Dr. Nova reframed published results as rich dataset rather than limitation
- **Exchange 7**: Pivot from prediction accuracy to pattern discovery validated by expert agreement
- **Exchange 8**: Cohen's kappa established as quantitative interpretability measure
- **Exchange 11**: Dr. Ally synthesized converged hypothesis with all concerns addressed

---

## Final Hypothesis

### Title
Interpretable Error Taxonomy for LLM Benchmarks via Published Results Analysis

### Core Claim
Under the scope of existing LLM benchmarks with published results (TruthfulQA, MMLU), if we extract interpretable features from question metadata and analyze category-level error patterns across multiple models, then we can generate an error taxonomy achieving ≥0.7 Cohen's kappa agreement with human expert categorization, because systematic failure patterns exist in question characteristics that transcend individual model implementations.

### Mechanism

**4-Step Causal Chain:**

1. **Metadata→Difficulty Correlation**: Question metadata features (type, topic, complexity) correlate with error patterns across models because they capture intrinsic difficulty characteristics independent of model implementations (Evidence: Item Response Theory from educational testing)

2. **Category-Level→Item Clustering**: Category-level error rates from published results provide signal for item-level clustering via shared metadata features (Evidence: Weak supervision paradigm)

3. **Clustering→Interpretability**: Clustered errors are interpretable because human experts can recognize patterns in grouped characteristics (Evidence: Expert agreement measured via IRR)

4. **Cross-Benchmark Generalization**: Taxonomy generalizes across benchmarks because patterns reflect fundamental LLM limitations not benchmark artifacts (Evidence: TruthfulQA→MMLU transfer)

---

## Predictions

### P1 (Primary): Same-Benchmark Validation
**Statement**: Human experts independently categorizing TruthfulQA error modes will agree with taxonomy at ≥0.7 Cohen's kappa

**Test Method**: 100 sampled questions, 3 independent experts, standardized annotation protocol

**Success Criterion**: Kappa ≥0.7 AND expert IRR ≥0.6

**Falsification**: Kappa ≤0.5 indicates taxonomy lacks interpretability

### P2: Cross-Benchmark Transfer
**Statement**: Taxonomy applied to MMLU achieves ≥0.6 Cohen's kappa agreement

**Test Method**: 100 MMLU questions, same expert protocol

**Success Criterion**: Kappa ≥0.6 (moderate agreement)

**Falsification**: Kappa <0.4 indicates TruthfulQA-specific artifacts

### P3: Feature Interpretability
**Statement**: Top-3 features per category are human-interpretable

**Test Method**: Feature importance analysis + expert survey

**Success Criterion**: ≥80% rated interpretable by majority

**Falsification**: Opaque features (e.g., PCA components)

### P4: Temporal Improvement
**Statement**: ≥30% categories show ≥15pp error rate improvement baseline→current

**Test Method**: Two-timepoint comparison (GPT-3.5/Claude-2/Llama-2 vs GPT-4/Claude-3/Llama-3)

**Success Criterion**: 30% categories improve >15 percentage points

**Falsification**: <20% improve indicates persistent fundamental limitations

---

## Novelty

### What's New
First systematic error taxonomy for LLM benchmarks validated against expert judgment using ONLY published results

### Key Innovation
Diagnostic framing (pattern discovery validated by expert agreement) rather than predictive accuracy, enabling interpretability-first design

### Differentiation from Prior Work
- **vs Manual Error Analysis**: Automated systematic framework (scalable to new benchmarks)
- **vs Unsupervised Clustering (h-e1)**: Supervised with expert validation, eliminates API dependency
- **vs Aggregate Scoring**: Fine-grained interpretable categories with cross-benchmark generalization
- **vs IRT**: Adaptation to LLM evaluation with category-level weak supervision

---

## Experimental Design

### Datasets
- **TruthfulQA**: 817 items, 38 categories, factual accuracy focus
- **MMLU**: 14,042 items, 57 subjects, knowledge evaluation

### Models
- **Current**: GPT-4, Claude-3, Llama-3
- **Baseline**: GPT-3.5, Claude-2, Llama-2

### Baselines
1. Random category assignment (expect kappa ~0)
2. Category mean baseline (no metadata features)
3. Single-feature baseline (question length only)

### Timeline
**3 months total**
- Weeks 1-2: Data extraction and preprocessing
- Weeks 3-4: Feature engineering and clustering
- Weeks 5-6: Taxonomy generation
- Weeks 7-8: Expert validation (TruthfulQA)
- Weeks 9-10: Cross-benchmark transfer (MMLU)
- Weeks 11-12: Analysis and write-up

---

## Limitations

1. **Category-level supervision** provides coarse signal for item-level validation (mitigated via expert validation)
2. **Expert recruitment** requires $3000 budget and careful sourcing
3. **Temporal analysis** limited to 2 timepoints due to historical data availability
4. **Cross-benchmark testing** validated on one pair (TruthfulQA→MMLU)
5. **Feature engineering** limited to metadata (no semantic analysis to avoid API dependency)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas consensus |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |
| **Confidence Level** | 0.8 |
| **Phase 2B Readiness** | READY |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
