# Product Requirements Document: Cross-Verifier Transfer System (h-m3)

**Hypothesis**: h-m3  
**Version**: 1.0  
**Date**: 2026-07-11  
**Status**: Draft

---

## Executive Summary

### Purpose
Implement and validate a semantic normalization layer that enables cross-verifier transfer learning, allowing feedback→repair models trained on one formal verification tool (Frama-C) to transfer to other tools (Dafny, Why3) with ≤20% performance degradation.

### Success Criteria
- **Primary**: Cross-verifier proof discharge rate degradation ≤20% across all 6 transfer pairs
- **Secondary**: Bidirectional transfer works symmetrically (A→B ≈ B→A performance)
- **Tertiary**: Semantic normalization achieves ≥80% error category coverage

### Gate Type
**MUST_WORK** - This is a critical validation of the cross-verifier portability claim.

---

## Problem Statement

### Research Question
Can semantic abstraction preserve enough structure to enable cross-verifier transfer, or do tool-specific idioms fundamentally prevent portability?

### Current Limitations
- Existing feedback→repair systems are tool-specific (h-m1 demonstrates effectiveness for single verifier)
- No existing approach validates cross-tool transfer learning for formal verification
- Unknown whether semantic normalization layer (h-e2) is sufficient for transfer

### Target Users
- Researchers validating cross-verifier portability hypothesis
- Future developers building verifier-agnostic repair tools

---

## Functional Requirements

### FR1: Semantic Normalization Layer Integration
**Priority**: P0 (Critical)  
**Dependencies**: h-e2 (semantic primitive taxonomy)

**Requirements**:
- Load h-e2 taxonomy mapping: `{ToolError} → {UniversalPrimitive}`
- Parse raw verifier output (Frama-C, Dafny, Why3 formats)
- Map tool-specific errors to 8-category universal primitive space
- Validate ≥80% error coverage per verifier
- Output normalized feedback representation for downstream pipeline

**Acceptance Criteria**:
- Parser handles all three verifier output formats
- Normalization achieves ≥80% coverage on test set
- Universal primitives preserve semantic meaning (manual validation on 30 samples)

### FR2: Cross-Verifier Training Pipeline
**Priority**: P0 (Critical)  
**Dependencies**: h-m1 (feedback→repair pipeline), FR1

**Requirements**:
- Train feedback→repair model on Source Verifier (40 programs)
- Use FullStructured feedback condition (best performer from h-m1)
- 10-iteration refinement budget per program
- Record learned mappings: (NormalizedFeedback → RepairAction → Outcome)
- Validate same-tool baseline performance on 10 held-out programs

**Acceptance Criteria**:
- Same-tool baseline achieves 60-80% proof discharge rate
- Training pipeline handles all 3 source verifiers (Frama-C, Dafny, Why3)
- Learned mappings stored in universal primitive space (not tool-specific)

### FR3: Cross-Verifier Transfer Evaluation
**Priority**: P0 (Critical)  
**Dependencies**: FR1, FR2

**Requirements**:
- Evaluate 6 directional transfer pairs:
  - Frama-C → Dafny, Frama-C → Why3
  - Dafny → Frama-C, Dafny → Why3
  - Why3 → Frama-C, Why3 → Dafny
- Apply learned mappings (from source) to target verifier feedback
- Generate target-specific specification syntax from repair actions
- Measure proof discharge rate on 10 test programs per target
- Calculate degradation: `(Baseline - Transfer) / Baseline × 100%`

**Acceptance Criteria**:
- All 6 transfer pairs evaluated
- Degradation metric computed for each pair
- Target syntax generation produces valid specifications (parser validation)

### FR4: Control Experiments
**Priority**: P0 (Critical)  
**Dependencies**: FR2

**Requirements**:
- **Baseline 1 (Same-Tool)**: Train on Verifier A, test on held-out A programs
- **Baseline 2 (Raw Transfer)**: Train on raw Frama-C output, test on raw Dafny (no normalization)
- **Baseline 3 (Manual Porting)**: Expert-written specifications for subset (optional)

**Acceptance Criteria**:
- Same-tool baseline establishes performance ceiling (60-80%)
- Raw transfer baseline shows poor performance (~30-40%, confirming normalization necessity)
- If manual baseline available: provides upper bound reference (80-90%)

### FR5: Dataset Collection and Preparation
**Priority**: P0 (Critical)  
**Dependencies**: None

**Requirements**:
- Collect 50 verified programs per verifier (150 total):
  - Frama-C: Tutorial examples + ACSL benchmark
  - Dafny: dafny-lang/dafny examples
  - Why3: VSTTE benchmark suite
- Annotate each program with:
  - Verification tool and version
  - Gold standard specifications
  - Proof obligations (extracted from verifier)
  - Error categories (mapped to universal primitives)
- 80/20 tool-stratified split (40 train, 10 test per verifier)

**Acceptance Criteria**:
- All programs verify successfully under native verifier
- Manual validation confirms semantic equivalence for subset
- Dataset size: 150 programs (50 per verifier)

### FR6: Target Syntax Generation Templates
**Priority**: P1 (High)  
**Dependencies**: FR1, FR3

**Requirements**:
- Implement syntax generation for each target verifier:
  - Frama-C: ACSL annotation templates
  - Dafny: pre/post/invariant templates
  - Why3: WhyML specification templates
- Few-shot prompting with tool-specific examples
- Parser validation for generated specifications

**Acceptance Criteria**:
- Generated specifications parse successfully (syntax validation)
- Templates cover all 8 universal repair primitives
- Few-shot examples minimize invalid syntax generation

### FR7: Automated Evaluation Harness
**Priority**: P1 (High)  
**Dependencies**: FR2, FR3

**Requirements**:
- Batch processing for 150 programs × 10 iterations = 1500 runs
- Automated verifier integration (Frama-C WP, Dafny, Why3)
- 10s timeout per verification attempt
- Collect metrics per (source, target, program, iteration):
  - Proof discharge rate
  - Iterations to convergence
  - Unmapped error rate
  - Syntax validity

**Acceptance Criteria**:
- Harness runs unattended for full experiment (12.5 CPU-hours)
- Results saved to structured CSV format
- Timeout handling prevents hung processes

### FR8: Statistical Analysis and Visualization
**Priority**: P1 (High)  
**Dependencies**: FR7

**Requirements**:
- **Primary Analysis**: Paired t-test for degradation ≤20% threshold (α=0.05)
- **Secondary Analyses**:
  - Bidirectionality: Compare Degradation(A→B) vs Degradation(B→A)
  - Normalization coverage: % errors successfully mapped
  - Semantic preservation: Manual validation on 30 samples
- **Visualizations**:
  - Figure 1: Transfer performance heatmap (3×3 verifier pairs)
  - Figure 2: Degradation bar chart with 20% threshold line
  - Figure 3: Iteration convergence curves (same-tool vs cross-tool)

**Acceptance Criteria**:
- Statistical tests compute p-values and effect sizes (Cohen's d)
- Visualizations saved as publication-ready figures (PNG, 300dpi)
- Analysis script automated (no manual computation)

### FR9: Root Cause Analysis (Diagnostic)
**Priority**: P2 (Medium)  
**Dependencies**: FR7, FR8

**Requirements**:
- **If degradation >20%**: Identify failure modes
  - Which universal primitives failed transfer?
  - Which target verifier syntax caused errors?
  - Which program complexity factors correlated with failure?
- **Unmapped Error Analysis**:
  - Categorize normalization failures (tool-specific idioms, taxonomy gaps, bugs)
  - Report % unmapped errors per verifier

**Acceptance Criteria**:
- Failure modes categorized and quantified
- Root cause analysis included in 04_validation.md
- Recommendations for h-e2 taxonomy extension (if coverage <80%)

---

## Non-Functional Requirements

### NFR1: Computational Resources
- **Verifier Compute**: ~12.5 CPU-hours (4500 verification runs × 10s timeout)
- **LLM API Budget**: $30-60 (GPT-4) or $15-30 (Claude Opus) for ~3M tokens
- **Storage**: ~750MB (500MB raw outputs, 200MB normalized logs, 50MB results)

### NFR2: Reproducibility
- Pin verifier versions: Frama-C ≥28.0, Dafny ≥4.0, Why3 ≥1.6
- Pin Z3 solver version (backend for all verifiers)
- Document LLM model and version (GPT-4 or Claude Opus)
- Seed random number generators for dataset splits

### NFR3: Performance
- Verification timeout: 10s per program (prevent hung processes)
- Batch processing: Support parallel execution (GPU not required)
- API rate limiting: Respect LLM provider limits (1000 req/min for GPT-4)

### NFR4: Maintainability
- Modular architecture: Separate normalization, training, evaluation components
- Configuration-driven: Verifier selection, dataset paths, hyperparameters in YAML
- Logging: Structured logs for debugging (WandB optional)

---

## Data Requirements

### Input Data
- **Verification Programs**: 150 programs (50 per verifier) with gold specifications
- **h-e2 Taxonomy**: 8-category universal primitive mapping
- **h-m1 Pipeline**: Feedback→repair model implementation

### Output Data
- **Raw Verifier Outputs**: Text logs from Frama-C/Dafny/Why3 (500MB)
- **Normalized Feedback**: Universal primitive representations (200MB)
- **Metrics CSV**: Proof discharge rates per (source, target, program, iteration)
- **Degradation CSV**: Summary statistics per transfer pair
- **Visualizations**: 3 publication-ready figures (PNG)

### Data Validation
- All programs verify under native verifier (correctness check)
- Semantic equivalence validated for subset (manual inspection)
- No synthetic data (using real verification benchmarks only)

---

## Dependencies

### Upstream (Prerequisites)
- **h-e2**: Semantic primitive taxonomy with ≥80% coverage (COMPLETED)
- **h-m1**: Feedback→repair pipeline with FullStructured feedback (COMPLETED)

### External Tools
- Frama-C WP (version ≥28.0)
- Dafny (version ≥4.0)
- Why3 (version ≥1.6)
- Z3 solver (backend for all verifiers)
- LLM API (GPT-4 or Claude Opus)

### Downstream (Consumers)
- Phase 5: Baseline Repository Comparison
- Phase 6: Paper Writing (cross-verifier portability claim)

---

## Success Metrics

### Gate Criteria (MUST_WORK)
| Metric | Target | Measurement |
|--------|--------|-------------|
| **Cross-Verifier Degradation** | ≤20% | Mean degradation across 6 transfer pairs |
| **Bidirectionality** | Symmetric | Degradation(A→B) ≈ Degradation(B→A) within 5pp |
| **Normalization Coverage** | ≥80% | % errors successfully mapped to primitives |

### Performance Metrics
| Metric | Target | Context |
|--------|--------|---------|
| **Same-Tool Baseline** | 60-80% | Proof discharge rate (upper bound) |
| **Raw Transfer Baseline** | 30-40% | No normalization (lower bound) |
| **Cross-Tool with Normalization** | ≥48% | Retains ≥80% of same-tool performance |

### Diagnostic Metrics
- **Unmapped Error Rate**: <20% (validates h-e2 taxonomy sufficiency)
- **Syntax Validity**: >90% (target syntax generation robustness)
- **Convergence Iterations**: ≤10 (consistent with h-m1 budget)

---

## Risk Mitigation

### High-Priority Risks
1. **h-e2 Taxonomy Coverage Insufficient** (Probability: 0.4)
   - Mitigation: Pre-validate coverage on test set before h-m3
   - Contingency: Expand taxonomy iteratively if <80%

2. **Benchmark Programs Not Semantically Equivalent** (Probability: 0.6)
   - Mitigation: Focus on isomorphic programs (array algorithms)
   - Contingency: Report transfer within-domain only

3. **Target Syntax Generation Brittle** (Probability: 0.5)
   - Mitigation: Few-shot prompting, parser validation
   - Contingency: Manual syntax fixing for diagnostic analysis

### Medium-Priority Risks
4. **Human Baseline Unavailable** (Probability: 0.4)
   - Mitigation: Recruit verification expert for subset
   - Contingency: Omit human baseline, use gold specs as oracle

5. **Verifier Version Compatibility** (Probability: 0.3)
   - Mitigation: Pin versions explicitly
   - Contingency: Re-run h-e2 taxonomy on updated versions

---

## Timeline

### Phase Breakdown (6 weeks)
- **Week 1-2**: Implementation (normalization integration, pipeline extension)
- **Week 3-4**: Experimentation (training, same-tool baseline, cross-tool transfer)
- **Week 5**: Analysis (statistics, visualizations, root cause)
- **Week 6**: Validation report (04_validation.md, gate decision)

### Critical Milestones
| Milestone | Week | Deliverable | Gate Check |
|-----------|------|-------------|------------|
| Pipeline Integration | 2 | Working cross-verifier pipeline | Smoke test passes |
| Same-Tool Baseline | 3 | Performance ceiling established | ≥60% discharge |
| Cross-Tool Transfer | 4 | All 6 pairs evaluated | Data collected |
| Gate Decision | 5 | Degradation ≤20%? | MUST_WORK gate |
| Validation Report | 6 | 04_validation.md | Phase 5 ready |

---

## Deliverables

### Primary Deliverable
- **04_validation.md**: Gate decision, transfer performance table, degradation analysis, visualizations, recommendations

### Code Deliverables
- `src/cross_verifier_pipeline.py`: Transfer pipeline implementation
- `src/syntax_generators/`: Target verifier syntax templates (Frama-C, Dafny, Why3)
- `src/evaluation_harness.py`: Automated batch evaluation script

### Data Deliverables
- `data/training/`: 120 training programs (40 per verifier)
- `data/test/`: 30 test programs (10 per verifier)
- `results/metrics.csv`: Proof discharge rates
- `results/degradation.csv`: Summary statistics
- `figures/`: 3 publication-ready visualizations

### Documentation
- `README.md`: Experiment overview, reproduction instructions
- `CHANGELOG.md`: Iteration log, design decisions

---

## Appendix: Phase 2C Traceability

### Dataset Coverage
- ✅ Frama-C Subset: 50 programs (ACSL benchmark)
- ✅ Dafny Subset: 50 programs (dafny-lang/dafny examples)
- ✅ Why3 Subset: 50 programs (VSTTE benchmarks)

### Baseline Models Coverage
- ✅ Baseline 1: Same-Tool (FR4, FR2)
- ✅ Baseline 2: Raw Transfer (FR4)
- ✅ Baseline 3: Manual Porting (FR4, optional)

### Evaluation Metrics Coverage
- ✅ ProofDischargeRate: FR3, FR7
- ✅ PerformanceDegradation: FR3, FR8
- ✅ IterationsToConvergence: FR7
- ✅ AbstractionCoverage: FR1, FR8
- ✅ UnmappedErrorRate: FR9
- ✅ SemanticPreservationScore: FR1, FR8

### Ablation/Control Coverage
- ✅ Raw Transfer Control: FR4 (Baseline 2)

**Phase 2C Completeness**: 100% (all items from experiment brief mapped to FRs)

---

**END OF PRD**
