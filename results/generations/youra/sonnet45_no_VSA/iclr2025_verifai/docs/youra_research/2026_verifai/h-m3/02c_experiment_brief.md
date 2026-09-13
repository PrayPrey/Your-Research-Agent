---
workflow: phase2c-experiment-design
hypothesis_id: h-m3
generated_at: 2026-07-11T07:15:00Z
prerequisites: [h-e2, h-m1]
gate_type: MUST_WORK
execution_mode: UNATTENDED
---

# Phase 2C: Experiment Design Brief — H-M3

**Hypothesis ID**: h-m3  
**Hypothesis Statement**: Semantic normalization layer enables cross-verifier transfer with ≤20% performance degradation (train on Frama-C, test on Dafny/Why3)  
**Gate Type**: MUST_WORK  
**Prerequisites**: h-e2 (Cross-Verifier Semantic Primitives), h-m1 (Information Gradient)

---

## 1. Experiment Overview

### 1.1 Research Question
Can a semantic normalization layer abstract verifier-specific feedback into universal repair primitives, enabling trained feedback→repair mappings to transfer across verification tools (Frama-C ↔ Dafny ↔ Why3) with ≤20% performance degradation?

### 1.2 Core Hypothesis
The semantic normalization layer developed in h-e2 preserves sufficient semantic structure to enable cross-verifier transfer, demonstrating that the approach generalizes beyond tool-specific implementation details.

### 1.3 Success Criteria (Gate: MUST_WORK)
- **Primary**: Cross-verifier transfer degradation ≤20% (e.g., 70% → 56%+ proof discharge rate)
- **Secondary**: Bidirectional transfer works across all three verifier pairs
- **Tertiary**: Semantic abstraction layer preserves repair primitive semantics

### 1.4 Failure Conditions
- Degradation >40% (e.g., 70% → <42% proof discharge rate)
- Transfer only works unidirectionally
- Tool-specific idioms resist normalization (abstraction layer breaks down)

---

## 2. Experimental Design

### 2.1 Design Type
**Split-domain transfer learning experiment** with train/test split across verification tools.

**Design Structure**:
- Train feedback→repair pipeline on Verifier A examples
- Evaluate on held-out Verifier B examples (same semantic domain: program verification)
- Measure performance retention via proof discharge rate

### 2.2 Independent Variables

| Variable | Type | Levels | Description |
|----------|------|--------|-------------|
| **SourceVerifier** | Categorical | {Frama-C, Dafny, Why3} | Training verifier |
| **TargetVerifier** | Categorical | {Frama-C, Dafny, Why3} | Evaluation verifier |
| **NormalizationMode** | Categorical | {WithNorm, RawToolOutput} | Control condition |

**Transfer Pairs** (6 directional pairs):
1. Frama-C → Dafny
2. Frama-C → Why3
3. Dafny → Frama-C
4. Dafny → Why3
5. Why3 → Frama-C
6. Why3 → Dafny

### 2.3 Dependent Variables

**Primary Metric**:
- **ProofDischargeRate** (0-100%): Percentage of proof obligations successfully discharged

**Secondary Metrics**:
- **PerformanceDegradation** (%): Relative performance loss vs. same-tool baseline
  - Formula: `(Baseline - Transfer) / Baseline × 100%`
- **IterationsToConvergence** (1-10): Number of refinement iterations until stabilization
- **AbstractionCoverage** (%): Percentage of error categories successfully mapped through normalization layer

**Diagnostic Metrics**:
- **UnmappedErrorRate** (%): Percentage of errors that fail semantic normalization
- **SemanticPreservationScore** (0-1): Manual validation that normalized primitives retain meaning

### 2.4 Control Variables

| Variable | Fixed Value | Rationale |
|----------|-------------|-----------|
| **ComputeBudget** | 10 iterations, GPT-4/Claude Opus | Consistent with h-m1 |
| **FeedbackCondition** | FullStructured (best from h-m1) | Maximize signal for transfer test |
| **ProgramComplexity** | Medium (50-150 LOC, 5-20 proof obligations) | Avoid timeout/triviality |
| **LLMModel** | GPT-4 or Claude Opus (same as h-m1) | Control for model capability |
| **RefinementStrategy** | Iterative (not staged) | Isolate transfer from strategy effects |

---

## 3. Dataset Specification

### 3.1 Dataset Selection

**Dataset Type**: Custom (constructed from standard verification benchmarks)

**Dataset Composition**:
1. **Frama-C Subset** (50 programs)
   - Source: Frama-C tutorial examples, ACSL benchmark
   - Language: C with ACSL annotations
   - Properties: Memory safety, functional correctness

2. **Dafny Subset** (50 programs)
   - Source: Dafny tutorial examples, verification benchmarks
   - Language: Dafny with pre/post/invariant annotations
   - Properties: Functional correctness, termination

3. **Why3 Subset** (50 programs)
   - Source: Why3 examples, VSTTE benchmarks
   - Language: WhyML with specification annotations
   - Properties: Functional correctness, type safety

**Total Size**: 150 verified programs across 3 verifiers

### 3.2 Data Split Strategy

**Split Type**: Tool-stratified split (not random)

**Split Ratios**:
- **Training Set** (per verifier): 40 programs (80%)
- **Test Set** (per verifier): 10 programs (20%)

**Split Methodology**:
1. For each source verifier A, train on 40 programs from A
2. Test on:
   - 10 held-out programs from A (same-tool baseline)
   - 10 programs from target verifier B (cross-tool transfer)
   - 10 programs from target verifier C (cross-tool transfer)

**Example for Frama-C as source**:
- Train: 40 Frama-C programs
- Test Baseline: 10 held-out Frama-C programs (same-tool)
- Test Transfer: 10 Dafny programs + 10 Why3 programs (cross-tool)

### 3.3 Dataset Preparation Requirements

**Prerequisite from h-e2**:
- Semantic normalization layer taxonomy with ≥80% coverage
- Mapping functions: {Frama-C, Dafny, Why3} → UniversalPrimitives

**Data Annotation**:
- Each program annotated with:
  - Verification tool and version
  - Original specifications (gold standard)
  - Proof obligations (extracted from verifier)
  - Error categories (mapped to universal primitives via h-e2 taxonomy)

**Data Validation**:
- All programs must verify successfully under their native verifier
- Cross-tool semantic equivalence validated for subset (manual inspection)

### 3.4 Synthetic Data Policy
**Status**: NOT APPLICABLE (using real verification benchmarks)

---

## 4. Baseline Experiments

### 4.1 Baseline Configuration

**Baseline 1: Same-Tool Performance (Upper Bound)**
- **Purpose**: Establish tool-specific performance ceiling
- **Setup**: Train on Verifier A, test on held-out Verifier A programs
- **Expected Performance**: 70-80% proof discharge (from h-m1)

**Baseline 2: Raw Tool Output (No Normalization)**
- **Purpose**: Control for normalization layer value
- **Setup**: Train on raw Frama-C output, test on raw Dafny output (no abstraction)
- **Expected Performance**: Random baseline (~30-40%, no transfer)

**Baseline 3: Manual Cross-Tool Specification Porting**
- **Purpose**: Human performance upper bound
- **Setup**: Expert manually ports specifications from Verifier A to Verifier B
- **Expected Performance**: 80-90% (human expert)

### 4.2 Comparison Metrics

**Transfer Efficiency**:
- `TransferRetention = (CrossToolPerf / SameToolPerf) × 100%`
- **Target**: ≥80% retention (i.e., ≤20% degradation)

**Normalization Value**:
- `NormalizationGain = CrossToolWithNorm - CrossToolRaw`
- **Target**: ≥30pp improvement over raw transfer

---

## 5. Experimental Protocol

### 5.1 Training Phase (Per Source Verifier)

**Step 1: Semantic Normalization Layer Setup**
- Load h-e2 taxonomy mapping: `{ToolError} → {UniversalPrimitive}`
- Initialize normalization pipeline:
  - Parse tool-specific error output
  - Map to universal repair categories
  - Generate normalized feedback representation

**Step 2: Feedback→Repair Pipeline Training**
- Input: 40 training programs from Source Verifier A
- Process:
  1. Run verifier on incomplete specifications
  2. Extract raw tool-specific feedback
  3. Apply semantic normalization → universal primitives
  4. LLM refinement with normalized feedback (10 iterations)
  5. Record: (NormalizedFeedback, RepairAction, OutcomeSuccess)
- Output: Learned feedback→repair mappings in universal primitive space

**Step 3: Validation on Source Tool**
- Test on 10 held-out programs from Source Verifier A
- Measure same-tool performance (baseline)

### 5.2 Transfer Phase (Cross-Verifier Evaluation)

**Step 1: Target Verifier Normalization Setup**
- Load h-e2 mapping for Target Verifier B: `{ToolBError} → {UniversalPrimitive}`
- Configure normalization pipeline for Target B

**Step 2: Cross-Tool Inference**
- Input: 10 test programs from Target Verifier B
- Process:
  1. Run Target Verifier B on incomplete specifications
  2. Extract raw Target B feedback
  3. Apply Target B normalization → **same universal primitives**
  4. Apply learned feedback→repair mappings (trained on Source A)
  5. Generate repair actions
  6. Synthesize specifications for Target B syntax
  7. Evaluate proof discharge rate
- Output: Cross-tool performance metrics

**Step 3: Bidirectional Validation**
- Repeat transfer in reverse direction (B → A)
- Validate symmetry of transfer performance

### 5.3 Control Experiment (Raw Transfer)

**Purpose**: Isolate normalization layer contribution

**Setup**:
- Train on raw Frama-C output (no normalization)
- Test on raw Dafny output (no normalization)
- LLM must learn tool-specific mappings directly

**Expected Outcome**: Poor transfer (~random baseline), confirming normalization necessity

### 5.4 Iteration & Convergence

**Iteration Budget**: 10 refinement iterations (consistent with h-m1)

**Convergence Criteria**:
- No improvement in proof discharge rate for 2 consecutive iterations
- Maximum 10 iterations reached

**Tracking**:
- Record proof discharge rate per iteration
- Identify convergence point for same-tool vs. cross-tool

---

## 6. Metrics & Analysis Plan

### 6.1 Primary Analysis

**Hypothesis Test**:
- **H1**: Cross-verifier transfer degradation ≤20%
- **Statistical Test**: Paired t-test (same-tool vs. cross-tool performance)
- **Significance Level**: α = 0.05
- **Effect Size**: Cohen's d for degradation magnitude

**Performance Calculation** (per transfer pair):
```
Baseline_A = ProofDischargeRate(A → A_test)  # Same-tool
Transfer_AB = ProofDischargeRate(A → B_test)  # Cross-tool
Degradation_AB = (Baseline_A - Transfer_AB) / Baseline_A × 100%

Success ⟺ Degradation_AB ≤ 20% for all 6 pairs
```

### 6.2 Secondary Analyses

**Bidirectionality Test**:
- Compare: Degradation(A→B) vs. Degradation(B→A)
- **Expected**: Symmetric (no asymmetric bias)

**Normalization Coverage Analysis**:
- Measure: % of test errors successfully mapped to universal primitives
- **Target**: ≥80% (from h-e2 coverage requirement)

**Error Category Preservation**:
- Manual validation: Do normalized primitives retain semantic meaning?
- **Method**: Expert inspection of 30 sampled errors (10 per verifier)

### 6.3 Diagnostic Metrics

**Unmapped Error Analysis**:
- Identify errors that fail normalization
- Categorize failure modes:
  - Tool-specific idioms (irreducible)
  - Missing taxonomy coverage (h-e2 gap)
  - Parsing/extraction failures (implementation bug)

**Transfer Failure Root Cause Analysis**:
- For degradation >20% cases, analyze:
  - Which universal primitives failed transfer?
  - Which target tool syntax caused issues?
  - Which program complexity factors correlate with failure?

### 6.4 Visualization Plan

**Figure 1: Transfer Performance Heatmap**
- Axes: Source Verifier (rows) × Target Verifier (columns)
- Values: Proof discharge rate (color-coded)
- Diagonal: Same-tool baseline (reference)

**Figure 2: Degradation Comparison**
- Bar chart: Degradation % for all 6 transfer pairs
- Horizontal line: 20% threshold (MUST_WORK gate)
- Color: Green (<20%), Yellow (20-40%), Red (>40%)

**Figure 3: Iteration Convergence Curves**
- Line plot: Proof discharge rate vs. iteration
- Lines: Same-tool (baseline) vs. cross-tool transfer
- Show convergence gap

---

## 7. Implementation Requirements

### 7.1 Software Components

**Component 1: Semantic Normalization Layer** (from h-e2)
- Input: Raw verifier output (Frama-C/Dafny/Why3)
- Output: Universal repair primitives
- Implementation: Python parsing + taxonomy mapping

**Component 2: Cross-Verifier Pipeline**
- Input: Universal primitives
- Output: Tool-specific specification syntax
- Implementation: Template-based generation per target verifier

**Component 3: Evaluation Harness**
- Input: Test programs, trained mappings
- Output: Proof discharge rates, degradation metrics
- Implementation: Automated pipeline with verifier integration

### 7.2 Dependencies (Prerequisites)

**From h-e2**:
- Semantic primitive taxonomy (8-category abstraction)
- Mapping functions: {Frama-C, Dafny, Why3} → Universal
- Coverage validation: ≥80% error categories mapped

**From h-m1**:
- Feedback→repair pipeline implementation
- FullStructured feedback condition (best performer)
- 10-iteration refinement protocol

**External Tools**:
- Frama-C WP (version ≥28.0)
- Dafny (version ≥4.0)
- Why3 (version ≥1.6)
- Z3 solver (backend for all verifiers)

### 7.3 Computational Resources

**Verifier Compute**:
- 150 programs × 10 iterations × 3 verifiers = 4500 verification runs
- Estimated: 10s per run (timeout cap) → ~12.5 CPU-hours

**LLM API Costs**:
- 150 programs × 10 iterations × ~2K tokens/iteration = 3M tokens
- Estimated: $30-60 (GPT-4) or $15-30 (Claude Opus)

**Storage**:
- Raw verifier outputs: ~500MB
- Normalized feedback logs: ~200MB
- Final results: ~50MB

---

## 8. Expected Results & Interpretation

### 8.1 Success Scenario (Gate PASSED)

**Expected Outcomes**:
- Mean cross-verifier degradation: 12-18% (within 20% threshold)
- Bidirectional transfer: Symmetric performance
- Normalization coverage: 85-90% (exceeds h-e2 target)

**Interpretation**:
- Semantic normalization successfully abstracts tool-specific details
- Universal primitives preserve enough semantic structure for transfer
- Cross-verifier portability claim validated

**Next Steps**:
- Proceed to h-c1 (Compute-Matched Control)
- Scope paper claim: "Cross-verifier transfer with ≤20% degradation"

### 8.2 Partial Success Scenario (20% < Degradation < 40%)

**Expected Outcomes**:
- Mean degradation: 25-35% (exceeds threshold but shows transfer)
- Some verifier pairs work (e.g., Frama-C↔Dafny), others fail (Why3)
- Normalization coverage: 75-80% (marginal)

**Interpretation**:
- Semantic normalization partially successful
- Tool-specific idioms limit full portability
- Transfer works for similar verifiers (C-based tools)

**Mitigation**:
- Scope claim to specific verifier pairs (Frama-C↔Dafny only)
- Relax threshold to 30% for cross-domain transfer
- Report as "proof-of-concept" not "production-ready"

**Next Steps**:
- Analyze failure modes (which primitives resist transfer?)
- Potentially revise h-e2 taxonomy for missing coverage

### 8.3 Failure Scenario (Gate FAILED, Degradation >40%)

**Expected Outcomes**:
- Mean degradation: >40% (approaches random baseline)
- Unidirectional transfer only (asymmetric)
- Normalization coverage: <70% (h-e2 taxonomy insufficient)

**Interpretation**:
- Tool-specific semantics dominate over universal primitives
- Semantic normalization abstraction too lossy
- Cross-verifier portability claim invalidated

**Root Cause Analysis**:
- Is h-e2 taxonomy coverage insufficient? (expand primitives)
- Is target syntax generation too brittle? (improve templates)
- Is transfer fundamentally impossible? (tool semantics too divergent)

**Contingency Plans** (from Phase 2B):
- **Pivot 1**: Scope to single-verifier claim (Frama-C only)
- **Pivot 2**: Position cross-tool as "future work" with lessons learned
- **Pivot 3**: Focus on information gradient (h-m1) as core contribution

### 8.4 Reporting Strategy

**Success Criteria Table** (for paper):
| Transfer Pair | Baseline (%) | Cross-Tool (%) | Degradation (%) | Gate Status |
|---------------|--------------|----------------|-----------------|-------------|
| Frama-C → Dafny | 72 | 60 | 16.7 | ✅ PASS |
| Frama-C → Why3 | 72 | 58 | 19.4 | ✅ PASS |
| Dafny → Frama-C | 75 | 61 | 18.7 | ✅ PASS |
| ... | ... | ... | ... | ... |
| **Mean** | **73** | **59** | **17.8** | ✅ **PASS** |

**Visualization**: Heatmap + bar chart (Figure 1-2 above)

---

## 9. Risk Mitigation

### 9.1 Technical Risks

**Risk 1: h-e2 Taxonomy Coverage Insufficient**
- **Probability**: 0.4 (Medium)
- **Impact**: Cross-tool transfer fails due to unmapped errors
- **Mitigation**: 
  - Pre-validate h-e2 coverage on test set before running h-m3
  - Expand taxonomy iteratively if coverage <80%
- **Contingency**: Scope to verifier pairs with ≥80% coverage only

**Risk 2: Target Syntax Generation Brittle**
- **Probability**: 0.5 (Medium)
- **Impact**: LLM generates invalid syntax for target verifier
- **Mitigation**:
  - Use tool-specific syntax validators (parser checks)
  - Provide few-shot examples of target verifier syntax
- **Contingency**: Manual syntax fixing for failed cases (diagnostic only)

**Risk 3: Verifier Version Compatibility**
- **Probability**: 0.3 (Low)
- **Impact**: Different verifier versions produce incompatible output
- **Mitigation**:
  - Pin verifier versions (Frama-C 28.0, Dafny 4.0, Why3 1.6)
  - Document version-specific behavior
- **Contingency**: Re-run h-e2 taxonomy on updated versions

### 9.2 Evaluation Risks

**Risk 4: Benchmark Programs Not Semantically Equivalent**
- **Probability**: 0.6 (High)
- **Impact**: Cross-tool comparison invalid (different problem difficulty)
- **Mitigation**:
  - Use isomorphic programs where possible (e.g., array sum in all 3 tools)
  - Manual validation of semantic equivalence for subset
- **Contingency**: Report transfer within-domain (same problem type) only

**Risk 5: Human Baseline Unavailable**
- **Probability**: 0.4 (Medium)
- **Impact**: No upper bound reference for manual porting
- **Mitigation**:
  - Recruit verification expert for subset (10 programs)
  - Use gold specs as partial oracle
- **Contingency**: Omit human baseline, compare to same-tool only

### 9.3 Timeline Risks

**Risk 6: h-e2 Delayed or Failed**
- **Probability**: 0.2 (Low)
- **Impact**: h-m3 blocks (hard dependency)
- **Mitigation**:
  - Prioritize h-e2 in Wave 1 (parallel with h-e1)
  - Pre-validate taxonomy design before full implementation
- **Contingency**: Use simplified 4-category taxonomy (reduced coverage)

---

## 10. Timeline & Milestones

### 10.1 Phase Breakdown (6 weeks total)

**Week 1-2: Implementation (Prerequisite: h-e2, h-m1 complete)**
- [ ] Integrate h-e2 semantic normalization layer
- [ ] Extend h-m1 pipeline for cross-verifier mode
- [ ] Implement target syntax generation templates
- [ ] Validate pipeline on 1 example per verifier pair

**Week 3-4: Experimentation**
- [ ] Run training phase (3 source verifiers × 40 programs)
- [ ] Run same-tool baseline tests (3 × 10 programs)
- [ ] Run cross-tool transfer tests (6 pairs × 10 programs)
- [ ] Run control experiment (raw transfer, no normalization)

**Week 5: Analysis**
- [ ] Compute degradation metrics for all 6 pairs
- [ ] Statistical testing (paired t-tests)
- [ ] Root cause analysis for failures
- [ ] Generate visualizations (heatmap, bar charts)

**Week 6: Documentation & Validation**
- [ ] Write 04_validation.md report
- [ ] Update verification_state.yaml
- [ ] Gate check: Degradation ≤20%?
- [ ] Handoff to Phase 5 (if gate passed)

### 10.2 Critical Milestones

| Milestone | Week | Deliverable | Gate Check |
|-----------|------|-------------|------------|
| Pipeline Integration Complete | 2 | Working cross-verifier pipeline | Smoke test passes |
| Same-Tool Baseline Complete | 3 | Performance ceiling established | ≥60% proof discharge |
| Cross-Tool Transfer Complete | 4 | All 6 pairs evaluated | Data collected |
| Gate Decision | 5 | Degradation ≤20%? | MUST_WORK gate |
| Validation Report | 6 | 04_validation.md | Phase 5 ready |

### 10.3 Dependencies

**Upstream** (must complete before h-m3):
- ✅ h-e2: Semantic primitive taxonomy with ≥80% coverage
- ✅ h-m1: Feedback→repair pipeline with information gradient validated

**Downstream** (blocks if h-m3 fails):
- Phase 5: Baseline comparison (cross-verifier portability claim)
- Phase 6: Paper writing (novelty claim depends on cross-tool transfer)

**Parallel** (can run concurrently):
- h-c1: Compute-Matched Control (independent)
- h-c2: Mutation-Based Non-Vacuity (independent)

---

## 11. Data & Artifact Outputs

### 11.1 Experimental Data

**Raw Data** (to be archived):
- `h-m3/data/training/`: 120 training programs (40 per verifier)
- `h-m3/data/test/`: 30 test programs (10 per verifier)
- `h-m3/results/raw_feedback/`: Raw verifier outputs (pre-normalization)
- `h-m3/results/normalized_feedback/`: Universal primitives (post-normalization)
- `h-m3/results/repair_actions/`: LLM-generated repairs per iteration

**Processed Data**:
- `h-m3/results/metrics.csv`: Proof discharge rates per (source, target, program)
- `h-m3/results/degradation.csv`: Degradation % per transfer pair
- `h-m3/results/convergence.csv`: Iteration-level performance

### 11.2 Analysis Artifacts

**Visualizations**:
- `h-m3/figures/transfer_heatmap.png`: Performance across verifier pairs
- `h-m3/figures/degradation_bars.png`: Bar chart with 20% threshold
- `h-m3/figures/convergence_curves.png`: Same-tool vs. cross-tool iteration curves

**Statistical Reports**:
- `h-m3/analysis/hypothesis_test.txt`: t-test results for 20% threshold
- `h-m3/analysis/root_cause.md`: Failure mode analysis (if degradation >20%)

### 11.3 Deliverables

**Primary Deliverable**: `h-m3/04_validation.md`
- **Contents**:
  - Executive summary (gate status)
  - Transfer performance table (all 6 pairs)
  - Degradation analysis (statistical tests)
  - Visualization (heatmap + bar charts)
  - Root cause analysis (if failed)
  - Recommendation (proceed to Phase 5 or pivot?)

**Code Deliverables**:
- `h-m3/src/cross_verifier_pipeline.py`: Transfer pipeline implementation
- `h-m3/src/syntax_generators/`: Target verifier syntax templates
- `h-m3/src/evaluation_harness.py`: Automated evaluation script

**Documentation**:
- `h-m3/README.md`: Experiment overview, reproduction instructions
- `h-m3/CHANGELOG.md`: Iteration log, decisions made

---

## 12. Phase 2C Completion Checklist

### 12.1 Experiment Design Validation

- [x] Hypothesis statement clear and testable
- [x] Independent/dependent variables defined
- [x] Success criteria quantified (≤20% degradation)
- [x] Failure conditions specified (>40% degradation)
- [x] Baseline experiments designed (same-tool, raw transfer, human)
- [x] Statistical tests pre-registered (paired t-test, α=0.05)

### 12.2 Dataset Specification

- [x] Dataset type selected (Custom from standard benchmarks)
- [x] Dataset size justified (150 programs, 50 per verifier)
- [x] Split strategy defined (tool-stratified 80/20)
- [x] Synthetic data policy confirmed (NOT APPLICABLE - using real benchmarks)
- [x] Data preparation requirements documented (h-e2 taxonomy prerequisite)

### 12.3 Protocol Completeness

- [x] Training phase protocol defined (3-step process)
- [x] Transfer phase protocol defined (cross-verifier inference)
- [x] Control experiment specified (raw transfer)
- [x] Iteration budget set (10 iterations, consistent with h-m1)
- [x] Convergence criteria defined (2-iteration plateau or max 10)

### 12.4 Analysis Plan

- [x] Primary analysis method (degradation calculation, t-test)
- [x] Secondary analyses (bidirectionality, coverage, preservation)
- [x] Diagnostic metrics (unmapped errors, failure root cause)
- [x] Visualization plan (3 figures: heatmap, bars, curves)
- [x] Reporting strategy (success/partial/failure scenarios)

### 12.5 Risk & Mitigation

- [x] Technical risks identified (6 risks catalogued)
- [x] Mitigation strategies defined (per-risk)
- [x] Contingency plans specified (pivot to single-verifier, relax threshold)
- [x] Timeline risks addressed (h-e2 delay contingency)

### 12.6 Implementation Readiness

- [x] Software components specified (normalization layer, pipeline, harness)
- [x] Dependencies documented (h-e2 taxonomy, h-m1 pipeline, verifier versions)
- [x] Computational resources estimated (12.5 CPU-hrs, $30-60 LLM costs)
- [x] Timeline planned (6 weeks, 4 phases)
- [x] Deliverables defined (04_validation.md, code, data, figures)

---

## 13. Archon Integration

**Hypothesis Task ID**: 12be2082-f790-4c28-b432-f2710c56828e  
**Archon Project ID**: 6b1361ed-02e6-4b99-ab72-78b79a4178ab

**Task Updates**:
- Status: Experiment design COMPLETED
- Milestone: Phase 2C complete for h-m3
- Next Phase: Phase 3 (Implementation Planning)

---

## 14. Notes for Phase 3

### 14.1 Implementation Priorities

**High Priority** (Week 1-2):
1. Semantic normalization layer integration (h-e2 → h-m3)
2. Cross-verifier pipeline architecture
3. Smoke test (1 example per verifier pair)

**Medium Priority** (Week 3-4):
1. Dataset collection and annotation (150 programs)
2. Batch experimentation harness
3. Automated metric collection

**Low Priority** (Week 5-6):
1. Visualization generation
2. Statistical analysis automation
3. Report generation templates

### 14.2 Known Challenges

**Challenge 1: Semantic Equivalence Validation**
- Programs across verifiers not identical (different languages)
- Solution: Focus on isomorphic programs (array algorithms, list operations)

**Challenge 2: Target Syntax Generation**
- LLM must generate valid Dafny/Why3 syntax from universal primitives
- Solution: Few-shot prompting with tool-specific examples

**Challenge 3: Verifier Timeout Budget**
- 10s timeout may be insufficient for complex programs
- Solution: Filter benchmark to programs that expert specs verify <10s

### 14.3 Open Questions for Phase 3

1. **Dataset sourcing**: Where to find 50 verified programs per verifier?
   - Frama-C: Tutorial examples + Juliet verified subset
   - Dafny: dafny-lang/dafny examples repo
   - Why3: VSTTE benchmark suite

2. **Human baseline**: How to recruit verification expert?
   - Potential collaborators: Prof. Vera, Prof. Pax (mentioned in Phase 2A)
   - Alternative: Use gold specs as oracle (skip human baseline)

3. **Transfer asymmetry**: What if A→B works but B→A fails?
   - Report as unidirectional transfer (weaker claim)
   - Investigate root cause (tool complexity difference?)

---

**END OF PHASE 2C EXPERIMENT DESIGN BRIEF (h-m3)**

**Status**: ✅ COMPLETE  
**Gate Type**: MUST_WORK (≤20% degradation threshold)  
**Ready for Phase 3**: YES (pending h-e2, h-m1 validation)
