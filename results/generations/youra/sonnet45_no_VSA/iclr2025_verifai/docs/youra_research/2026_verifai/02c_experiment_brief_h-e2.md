---
hypothesis_id: h-e2
hypothesis_statement: "Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories"
gate_type: MUST_WORK
prerequisites: []
phase: Phase 2C
generated_at: 2026-07-11T06:05:00Z
archon_task_id: 8f52c983-bb92-44c5-b1ae-7376f82c27ea
---

# Experiment Brief: H-E2 Cross-Verifier Semantic Primitives

**Hypothesis ID**: h-e2  
**Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Prerequisites**: None

---

## 1. Executive Summary

This experiment validates whether **common semantic primitives exist across formal verifiers** (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories. This is a foundational hypothesis for cross-verifier portability — without semantic overlap, the normalization layer proposed in H-M3 would be infeasible.

**Core Research Question**: Can ≥80% of error categories from three verifiers (Frama-C WP, Dafny, Why3) be mapped to shared semantic primitives?

**Approach**: Bottom-up taxonomy analysis with empirical validation across real verification benchmarks.

**Success Criteria**:
- ≥80% of error categories map to shared primitives
- Abstraction layer design is implementation-ready (Level 1.5 detail)
- Coverage validated across 3 verifiers on 30+ proof obligations each

**Failure Boundary**:
- <60% semantic overlap → tool-specific semantics dominate
- No viable abstraction layer design emerges
- Critical error categories resist abstraction

---

## 2. Hypothesis Details

### 2.1 Full Statement

**H-E2**: Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories

### 2.2 Research Variables

**Independent Variables**:
- **VerifierTool**: {Frama-C WP, Dafny, Why3}
- **ErrorSource**: Benchmark programs with known verification failures

**Dependent Variables**:
- **SemanticCoverage** (Primary): Percentage of error categories mapping to shared primitives (0-100%)
- **AbstractionViability**: Boolean indicator of whether implementable abstraction layer exists
- **CategoryCount**: Number of shared semantic primitives identified (target: 8-12 categories)

**Controlled Variables**:
- Program domain (C for Frama-C, Dafny for Dafny, Why3ML for Why3)
- Error types analyzed (proof obligation failures only, excluding parse/type errors)
- Benchmark size (30-50 distinct failing proof obligations per verifier)

### 2.3 Success Criteria (Gate Requirements)

**MUST_WORK Gate Passes If**:
1. **≥80% semantic overlap**: 80% of collected error instances map to shared primitives
2. **Abstraction layer design complete**: JSON schema + parser specification exists
3. **Coverage validation**: All 3 verifiers tested on ≥30 failing proof obligations each

**Gate Fails If**:
- <60% semantic overlap (tool-specific semantics dominate)
- No viable abstraction layer design emerges (primitives too heterogeneous)
- Critical categories (e.g., loop invariants, preconditions) resist abstraction

---

## 3. Methodology

### 3.1 Overall Approach

**Type**: Taxonomy Analysis + Empirical Validation  
**Design**: Bottom-up error category extraction with cross-verifier mapping

**Three-Stage Process**:
1. **Stage 1 (Error Collection)**: Extract 30-50 failing proof obligations per verifier from standard benchmarks
2. **Stage 2 (Taxonomy Construction)**: Bottom-up categorization into semantic primitives
3. **Stage 3 (Abstraction Design)**: Design universal abstraction layer with parser specification

### 3.2 Stage 1: Error Collection

#### 3.2.1 Data Sources

**Frama-C WP Errors**:
- **Source**: Frama-C tutorial examples (https://github.com/Frama-C/open-source-case-studies)
- **Tool Version**: Frama-C 29.0 (Copper) with WP plugin
- **Collection Method**: 
  - Run WP on tutorial programs with intentionally incomplete/incorrect ACSL annotations
  - Collect proof obligation failures from WP output
  - Parse error messages from `-wp-msg-key` verbose mode
- **Target**: 40 distinct failing proof obligations
- **Error Types**: 
  - Loop invariant failures (established, preserved)
  - Precondition violations at call sites
  - Postcondition failures
  - Assertion failures
  - Runtime error checks (RTE plugin output)

**Dafny Errors**:
- **Source**: Dafny test suite (dafny-lang/dafny GitHub repository)
- **Tool Version**: Dafny 4.4.0
- **Collection Method**:
  - Extract verification failure examples from test suite
  - Collect error messages with source location context
  - Include quantifier trigger warnings
- **Target**: 40 distinct verification errors
- **Error Types**:
  - Postcondition failures
  - Loop invariant failures
  - Precondition violations
  - Assert failures
  - Quantifier instantiation issues

**Why3 Errors**:
- **Source**: Why3 examples repository + Frama-C WP intermediate output
- **Tool Version**: Why3 1.6.0
- **Collection Method**:
  - Collect Why3 proof obligation failures from standard examples
  - Use Frama-C WP `-wp-print` to generate Why3 intermediate language
  - Extract solver feedback from Alt-Ergo, Z3
- **Target**: 40 distinct proof failures
- **Error Types**:
  - VC (verification condition) failures
  - Contract violations
  - Invariant preservation failures
  - Goal unreachable errors

#### 3.2.2 Error Message Schema

For each error instance, collect:
```json
{
  "error_id": "unique_identifier",
  "verifier": "Frama-C | Dafny | Why3",
  "error_type": "raw_error_category",
  "source_location": "file:line:col",
  "error_message": "full_text_of_error",
  "proof_obligation": "PO_that_failed",
  "context": {
    "function_name": "...",
    "annotation_type": "loop_invariant | precondition | postcondition | assertion",
    "witness_info": "counterexample_if_available"
  }
}
```

**Storage**: JSON Lines format in `errors_collection.jsonl` (one error per line)

### 3.3 Stage 2: Taxonomy Construction

#### 3.3.1 Bottom-Up Categorization

**Process**:
1. **Initial Clustering**: Group errors by surface similarity (textual patterns in error messages)
2. **Semantic Analysis**: For each cluster, identify underlying semantic cause
3. **Cross-Verifier Mapping**: Identify equivalent error semantics across tools
4. **Primitive Extraction**: Abstract common semantic patterns into primitives

**Example Mapping**:
```
Frama-C: "loop invariant 'bounds' not preserved"
Dafny: "invariant might not be maintained by the loop body"
Why3: "cannot prove preservation of invariant inv_bounds"
→ Semantic Primitive: LOOP_INVARIANT_PRESERVATION_FAILURE
```

#### 3.3.2 Candidate Semantic Primitives (Initial Hypothesis)

Based on research synthesis, expected primitives:

1. **MISSING_PRECONDITION**: Required precondition not established at call site
2. **POSTCONDITION_FAILURE**: Function fails to establish postcondition on some path
3. **LOOP_INVARIANT_ESTABLISHMENT**: Invariant false before loop entry
4. **LOOP_INVARIANT_PRESERVATION**: Invariant not maintained through loop iteration
5. **ASSERTION_FAILURE**: Explicit assertion cannot be proved
6. **MEMORY_SAFETY**: Invalid pointer dereference, array bounds violation
7. **ARITHMETIC_OVERFLOW**: Integer overflow/underflow
8. **TERMINATION_FAILURE**: Loop variant not decreasing / recursive call non-terminating
9. **RESOURCE_LEAK**: Memory/resource not released (assigns clause violation)
10. **TYPE_INVARIANT_VIOLATION**: Class/datatype invariant broken
11. **QUANTIFIER_INSTANTIATION**: Universal/existential quantifier cannot be instantiated
12. **WITNESS_UNAVAILABLE**: No concrete counterexample/witness for existential claim

**Validation**: Empirically refine this list based on actual error corpus.

#### 3.3.3 Mapping Metrics

**Coverage Calculation**:
```
SemanticCoverage = (# errors mapped to primitives) / (total # errors) × 100%
```

**Per-Verifier Coverage**:
- Frama-C coverage: % of Frama-C errors mapped
- Dafny coverage: % of Dafny errors mapped
- Why3 coverage: % of Why3 errors mapped

**Cross-Verifier Primitive Support**:
```
Primitive_Support(P) = # verifiers that exhibit primitive P / 3
```
Target: All primitives have support ≥ 2/3 (appear in at least 2 verifiers)

### 3.4 Stage 3: Abstraction Layer Design

#### 3.4.1 Universal Error Schema

**Design Goal**: JSON schema that can represent any proof obligation failure in tool-agnostic form

**Schema Structure** (Level 1.5 detail):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UniversalProofObligationError",
  "type": "object",
  "required": ["error_id", "semantic_primitive", "obligation_type", "source_location"],
  "properties": {
    "error_id": {"type": "string"},
    "semantic_primitive": {
      "type": "string",
      "enum": [
        "MISSING_PRECONDITION", "POSTCONDITION_FAILURE", 
        "LOOP_INVARIANT_ESTABLISHMENT", "LOOP_INVARIANT_PRESERVATION",
        "ASSERTION_FAILURE", "MEMORY_SAFETY", "ARITHMETIC_OVERFLOW",
        "TERMINATION_FAILURE", "RESOURCE_LEAK", "TYPE_INVARIANT_VIOLATION",
        "QUANTIFIER_INSTANTIATION", "WITNESS_UNAVAILABLE"
      ]
    },
    "obligation_type": {
      "type": "string",
      "enum": ["precondition", "postcondition", "loop_invariant", 
               "assertion", "terminates", "assigns", "invariant"]
    },
    "source_location": {
      "type": "object",
      "properties": {
        "file": {"type": "string"},
        "line": {"type": "integer"},
        "column": {"type": "integer"},
        "function": {"type": "string"}
      }
    },
    "witness": {
      "type": "object",
      "description": "Counterexample or concrete values causing failure",
      "properties": {
        "available": {"type": "boolean"},
        "variable_assignments": {"type": "object"}
      }
    },
    "dependency_info": {
      "type": "object",
      "description": "Which other obligations/assumptions this depends on",
      "properties": {
        "required_assumptions": {"type": "array", "items": {"type": "string"}},
        "blocking_obligations": {"type": "array", "items": {"type": "string"}}
      }
    },
    "logical_structure": {
      "type": "object",
      "description": "Formula structure (quantifiers, connectives)",
      "properties": {
        "formula_type": {"type": "string", "enum": ["universal", "existential", "conjunction", "implication"]},
        "subformulas": {"type": "array"}
      }
    }
  }
}
```

#### 3.4.2 Parser Specifications

**Per-Verifier Parser** (pseudo-specification):

**Frama-C WP Parser**:
- Input: WP proof obligation output (text format from `-wp-out`)
- Output: UniversalProofObligationError JSON
- Key Extraction Rules:
  - Parse "Goal" annotations for obligation_type
  - Extract source location from PO metadata
  - Map WP error codes to semantic primitives
  - Extract witness from `-wp-model` counterexample output (if available)

**Dafny Parser**:
- Input: Dafny verification output (error messages + Boogie VC)
- Output: UniversalProofObligationError JSON
- Key Extraction Rules:
  - Parse "Related location" chain to identify root cause
  - Map error message patterns (regex-based) to semantic primitives
  - Extract source location from error output
  - Handle quantifier trigger warnings separately

**Why3 Parser**:
- Input: Why3 proof obligation + solver output
- Output: UniversalProofObligationError JSON
- Key Extraction Rules:
  - Parse Why3 VC structure (WhyML AST if available)
  - Map goal type to obligation_type
  - Extract source location from VC metadata
  - Parse Alt-Ergo/Z3 unsatisfiable core for dependency_info

#### 3.4.3 Abstraction Viability Test

**Test Cases** (Implementation-Ready Validation):
1. Select 5 diverse error instances per verifier (15 total)
2. Manually parse each to UniversalProofObligationError JSON
3. Verify no information loss (can reconstruct original error context)
4. Validate that JSON representation enables:
   - Error categorization for LLM prompts
   - Repair strategy selection (future work)
   - Cross-verifier transfer (can map Why3 error to Dafny repair)

**Success Criteria**: All 15 test cases successfully represented with no ambiguity.

---

## 4. Dataset Specification

### 4.1 Dataset Type & Source

**Dataset Type**: `standard` (publicly available verification benchmarks)

**Sources**:
1. **Frama-C Examples**: https://github.com/Frama-C/open-source-case-studies
   - SSAS parser tutorial
   - Binary search verification examples
   - Memory safety case studies
2. **Dafny Test Suite**: https://github.com/dafny-lang/dafny (tests/LitTests/)
   - Verification failure examples
   - Loop invariant examples
3. **Why3 Examples**: https://why3.lri.fr/examples.html
   - Standard library verification tasks
   - ProofGeneral examples

**Rationale for NO Synthetic Data**:
- Real verifier errors have tool-specific formatting, edge cases, and quirks
- Synthetic errors would miss these implementation details critical for parser design
- Standard benchmarks provide ground truth for taxonomy validation

### 4.2 Data Collection Protocol

**Sample Size**: 120 total proof obligation failures (40 per verifier)

**Sampling Strategy**:
- **Diversity**: Cover all major annotation types (pre/post/invariant/assert)
- **Difficulty**: Mix of simple (missing precondition) and complex (quantifier issues)
- **Realism**: Only failures from real benchmarks, not artificially broken code

**Collection Procedure**:
1. Run verifier on benchmark suite
2. Filter to proof obligation failures only (exclude parse/type errors)
3. For each failure:
   - Capture full error output
   - Record source location and function context
   - Save minimal reproducing example (if <50 LOC)
4. Store in `errors_collection.jsonl`

**Data Format**:
```jsonl
{"error_id": "framac_001", "verifier": "Frama-C", ...}
{"error_id": "framac_002", "verifier": "Frama-C", ...}
```

### 4.3 Dataset Splits

**No train/test split required** (taxonomy analysis, not ML training)

**Usage**:
- **Full Dataset (120 errors)**: Taxonomy construction + coverage calculation
- **Test Subset (15 errors)**: Abstraction viability validation

---

## 5. Baseline & Control Conditions

### 5.1 Baseline Approach

**No baseline comparison needed** (existence proof, not comparative experiment)

**Alternative**: If abstraction layer design fails, fallback is:
- Per-verifier-specific error handling (no normalization)
- Report failure of cross-verifier portability claim

### 5.2 Control Conditions

**Negative Control**: Include 10 intentionally un-categorizable errors
- Verifier-specific warnings (e.g., Dafny's "consider using a trigger")
- Performance hints (e.g., Why3 timeout suggestions)
- **Expected**: These should NOT map to semantic primitives (confirms categorization is not trivial)

**Positive Control**: Include 10 canonical error examples
- Standard loop invariant preservation failures
- Standard precondition violations
- **Expected**: 100% of these should map cleanly to primitives

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics

**1. Semantic Coverage (Primary Success Metric)**:
```
SemanticCoverage = (# errors mapped to primitives) / (total # errors) × 100%
```
- **Target**: ≥80%
- **Measurement**: Manual annotation + automated categorization verification

**2. Abstraction Viability (Boolean Gate)**:
- **Criteria**: JSON schema + parser specs complete AND 15/15 test cases successfully represented
- **Measurement**: Design review + manual validation

**3. Cross-Verifier Primitive Support**:
```
AvgSupport = Σ(Primitive_Support(P)) / (# primitives)
```
- **Target**: ≥0.67 (each primitive appears in ≥2 verifiers on average)
- **Measurement**: Count verifiers exhibiting each primitive

### 6.2 Secondary Metrics

**4. Primitive Count**: Number of distinct semantic primitives identified
- **Target Range**: 8-12 (enough expressiveness, not too fine-grained)

**5. Per-Verifier Coverage**:
- Frama-C_Coverage, Dafny_Coverage, Why3_Coverage
- **Target**: Each ≥75% (no single verifier is an outlier)

**6. Unmapped Error Analysis**:
- For errors that don't map to primitives, categorize reasons:
  - Tool-specific implementation detail
  - Out-of-scope (performance, warnings)
  - Novel category requiring new primitive

### 6.3 Success Thresholds

**Gate PASSES if**:
- SemanticCoverage ≥ 80%
- AbstractionViability = TRUE
- AvgSupport ≥ 0.67

**Gate FAILS if**:
- SemanticCoverage < 60%
- AbstractionViability = FALSE
- AvgSupport < 0.50 (primitives are too tool-specific)

---

## 7. Implementation Plan

### 7.1 Milestones & Timeline

**Total Duration**: 4 weeks (parallel with H-E1 in Wave 1)

| Week | Milestone | Deliverable |
|------|-----------|-------------|
| 1 | Error Collection Complete | `errors_collection.jsonl` with 120+ errors |
| 2 | Taxonomy Construction | Semantic primitive list + mapping table |
| 3 | Abstraction Design | JSON schema + parser specifications |
| 4 | Validation & Report | Coverage metrics + design document |

### 7.2 Detailed Task Breakdown

#### Week 1: Error Collection
**Tasks**:
1. Set up Frama-C 29.0 + WP plugin (Day 1)
2. Run Frama-C on tutorial examples, collect 40 failures (Day 2-3)
3. Set up Dafny 4.4.0, collect 40 failures from test suite (Day 4)
4. Set up Why3 1.6.0, collect 40 failures (Day 5)
5. Validate error collection format, clean data (Day 6-7)

**Compute Requirements**: Standard workstation (CPU-based verification)

#### Week 2: Taxonomy Construction
**Tasks**:
1. Initial clustering by textual similarity (Day 1-2)
2. Manual semantic analysis of clusters (Day 3-4)
3. Cross-verifier mapping (Day 5)
4. Primitive list refinement + coverage calculation (Day 6-7)

**Deliverable**: `taxonomy_mapping.md` with mapping table + coverage stats

#### Week 3: Abstraction Design
**Tasks**:
1. Design UniversalProofObligationError JSON schema (Day 1-2)
2. Write parser specifications for Frama-C, Dafny, Why3 (Day 3-5)
3. Manual parsing of 15 test cases (Day 6-7)

**Deliverable**: `abstraction_design.md` + `universal_error_schema.json`

#### Week 4: Validation & Report
**Tasks**:
1. Calculate all evaluation metrics (Day 1-2)
2. Negative/positive control validation (Day 3)
3. Write experiment report (Day 4-5)
4. Gate decision + archival (Day 6-7)

**Deliverable**: `h-e2_experiment_report.md` + gate decision

### 7.3 Resource Requirements

**Personnel**:
- Formal Methods Expert: 20 hrs/week (verifier setup, error interpretation)
- Research Assistant: 15 hrs/week (data collection, annotation)

**Compute**:
- Standard workstation (8-core CPU, 16GB RAM sufficient)
- No GPU required
- Verifier licenses: All open-source (no cost)

**Tools**:
- Frama-C 29.0 (via opam)
- Dafny 4.4.0 (GitHub releases)
- Why3 1.6.0 (via opam)
- Alt-Ergo, Z3 (automated provers)

**Storage**: ~500MB (error corpus + documentation)

---

## 8. Risk Analysis & Mitigation

### 8.1 Technical Risks

**Risk T1: Verifier version incompatibilities**  
**Probability**: 0.3 | **Impact**: Medium  
**Mitigation**: Pin exact versions (Frama-C 29.0, Dafny 4.4.0, Why3 1.6.0), use Docker containers for reproducibility  
**Contingency**: If version conflicts arise, downgrade to latest stable common versions

**Risk T2: Error message format changes across verifier updates**  
**Probability**: 0.2 | **Impact**: Low  
**Mitigation**: Document exact verifier versions, archive raw outputs  
**Contingency**: Abstraction design should accommodate format variations (parser robustness)

**Risk T3: Insufficient error diversity in benchmarks**  
**Probability**: 0.4 | **Impact**: Medium  
**Mitigation**: Pre-validate benchmark coverage of annotation types before collection  
**Contingency**: Augment with manually introduced errors (e.g., comment out loop invariants)

### 8.2 Methodological Risks

**Risk M1: Subjective categorization bias**  
**Probability**: 0.5 | **Impact**: Medium  
**Mitigation**: 
- Two independent annotators for 20% of corpus (inter-rater reliability check)
- Document categorization decision criteria
- Use positive/negative controls to validate categorization

**Contingency**: If inter-rater agreement <70%, refine categorization guidelines and re-annotate

**Risk M2: Abstraction layer too coarse or too fine**  
**Probability**: 0.4 | **Impact**: High  
**Mitigation**:
- Target 8-12 primitives (empirically validated range from research)
- Design iteratively: start coarse, refine based on test cases
- Validate with LLM prompting test (can LLM interpret primitives?)

**Contingency**: If abstraction fails viability test, iterate on schema design (Week 4 buffer)

### 8.3 Claim Validity Risks

**Risk C1: Semantic overlap <60% (gate failure)**  
**Probability**: 0.3 | **Impact**: High  
**Mitigation**:
- Research synthesis suggests strong semantic overlap for common categories
- Focus on proof obligation failures (exclude tool-specific warnings)
- Pre-registered failure boundary at 60% (not 80%)

**Contingency Plans**:
- **Trigger**: SemanticCoverage < 60%
- **Action 1**: Scope to Frama-C + Why3 only (both use Why3 backend, higher overlap expected)
- **Action 2**: Revise main hypothesis to "partial portability" (tool-specific layers + shared core)
- **Action 3**: Fail gate, report cross-verifier portability as infeasible

**Risk C2: Abstraction layer not implementable**  
**Probability**: 0.2 | **Impact**: Critical  
**Mitigation**:
- Level 1.5 design (detailed enough for implementation)
- Validate with 15 manual parsing test cases
- Consult with Frama-C/Dafny experts on parser feasibility

**Contingency Plans**:
- **Trigger**: Test cases cannot be represented without ambiguity
- **Action**: Revise schema, simplify primitives
- **Escalation**: If still fails after 2 iterations, fail gate

---

## 9. Expected Outcomes

### 9.1 Success Scenario (Gate PASS)

**Deliverables**:
1. **Taxonomy Document**: `taxonomy_mapping.md` with 8-12 semantic primitives
2. **Abstraction Design**: `universal_error_schema.json` + parser specifications
3. **Error Corpus**: `errors_collection.jsonl` with 120+ annotated errors
4. **Coverage Report**: SemanticCoverage ≥80%, AvgSupport ≥0.67
5. **Experiment Report**: `h-e2_experiment_report.md` with gate decision

**Impact**:
- Validates feasibility of cross-verifier normalization (prerequisite for H-M3)
- Provides implementation-ready design for Phase 3
- Demonstrates that verifier feedback CAN be abstracted (key novelty claim)

### 9.2 Partial Success Scenario

**If SemanticCoverage = 70-79%** (below 80% target but above 60% failure boundary):
- **Action**: PASS gate with caveat
- **Scope**: Report as "substantial semantic overlap" (not "universal")
- **Impact**: Proceed to H-M3 but with conservative portability claims

**If AvgSupport = 0.60-0.66** (some primitives tool-specific):
- **Action**: PASS gate, document tool-specific extensions
- **Design**: Core primitives (≥2/3 support) + tool-specific categories
- **Impact**: Hybrid abstraction layer (shared + tool-specific branches)

### 9.3 Failure Scenario (Gate FAIL)

**If SemanticCoverage <60%**:
- **Decision**: FAIL H-E2 gate
- **Impact**: Block H-M3 (cross-verifier transfer hypothesis)
- **Alternative Path**: Scope main hypothesis to single-verifier approach
- **Reporting**: Document tool-specific semantic divergence as key finding

**If Abstraction Viability = FALSE**:
- **Decision**: FAIL H-E2 gate
- **Impact**: Cannot proceed to implementation (no viable design)
- **Alternative Path**: Report theoretical possibility but practical infeasibility
- **Future Work**: Recommend per-verifier-specific feedback approaches

---

## 10. Connection to Main Hypothesis

### 10.1 Role in Overall Research

**Position in Hypothesis DAG**: Foundation Layer (Wave 1, parallel with H-E1)

**Downstream Dependencies**:
- **H-M3** (Semantic Normalization Transfer): DIRECT dependency — cannot test cross-verifier transfer without abstraction layer
- **H-M1** (Information Gradient): INDIRECT — normalization layer enables cross-tool feedback comparisons

**Contribution to Main Hypothesis**:
- Validates **cross-verifier portability** claim (key novelty vs. prior work)
- Demonstrates that verifier feedback is NOT tool-specific gibberish (can be abstracted)
- Provides foundation for "verifier-as-teacher" framework to generalize beyond single tool

### 10.2 Gate Impact

**If H-E2 PASSES**:
- Proceed to H-M3 (semantic normalization transfer experiments)
- Strengthen novelty claim (first cross-verifier specification synthesis)
- Enable Level 1.5 implementation planning in Phase 3

**If H-E2 FAILS**:
- **Scope Reduction**: Main hypothesis becomes "Frama-C-specific verifier-as-teacher"
- **Claim Adjustment**: Remove cross-verifier portability from novelty claims
- **Timeline Impact**: Skip H-M3 (prerequisite not met), focus resources on H-M1, H-C1, H-C2
- **Paper Positioning**: Report semantic divergence as negative result (still publishable)

---

## 11. Documentation & Archival

### 11.1 Experiment Artifacts

**Code & Data**:
```
h-e2_experiment/
├── errors_collection.jsonl          # 120+ annotated errors
├── taxonomy_mapping.md               # Semantic primitive mapping
├── universal_error_schema.json      # JSON schema for abstraction
├── parser_specs/
│   ├── framac_parser_spec.md        # Frama-C WP parser rules
│   ├── dafny_parser_spec.md         # Dafny error parser rules
│   └── why3_parser_spec.md          # Why3 VC parser rules
├── test_cases/                      # 15 manual parsing validation cases
├── scripts/
│   ├── collect_framac_errors.sh     # Frama-C error extraction
│   ├── collect_dafny_errors.sh      # Dafny error extraction
│   └── calculate_coverage.py        # Metric calculation
└── h-e2_experiment_report.md        # Final report + gate decision
```

### 11.2 Reporting Requirements

**Experiment Report Contents**:
1. **Executive Summary**: Gate decision + key findings (1 page)
2. **Methodology**: Data collection + taxonomy construction process (2 pages)
3. **Results**: Coverage metrics + primitive list + example mappings (3 pages)
4. **Abstraction Design**: Schema + parser specs (2 pages)
5. **Discussion**: Implications for H-M3 + limitations (1 page)
6. **Appendices**: Full error corpus + mapping table

**Metrics Summary Table**:
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| SemanticCoverage | ≥80% | TBD | TBD |
| AbstractionViability | TRUE | TBD | TBD |
| AvgSupport | ≥0.67 | TBD | TBD |
| PrimitiveCount | 8-12 | TBD | TBD |

### 11.3 Archon Integration

**Task Update**:
- Update Archon task `8f52c983-bb92-44c5-b1ae-7376f82c27ea` (H-E2) to `doing` at start
- Update to `review` when experiment complete
- Update to `done` after gate decision

**Metadata**:
```yaml
hypothesis: h-e2
phase: Phase 2C → 3 → 4
gate_type: MUST_WORK
experiment_duration: 4 weeks
semantic_coverage: <actual_value>
gate_decision: PASS | FAIL
```

---

## 12. Literature & Prior Work

### 12.1 Related Research

**Cross-Verifier Studies**:
1. **"Static versus Dynamic Verification in Why3, Frama-C and SPARK 2014"** (Signoles et al., 2016)
   - Comparison of specification languages (ACSL, Ada 2012, WhyML)
   - Finding: Semantic overlap exists for basic contracts, divergence in ghost code
   - **Relevance**: Validates hypothesis that shared primitives exist, provides taxonomy starting point

2. **"Research Corner - SPARK 2014 vs Frama-C vs Why3"** (AdaCore blog)
   - Practical comparison of three verifiers on same benchmark
   - Finding: Error messages have tool-specific syntax but shared semantic structure
   - **Relevance**: Confirms abstraction layer is viable approach

**Error Categorization**:
3. **Frama-C WP Manual** (Version 29.0)
   - Documents 12 proof obligation types (loop invariant, ensures, requires, etc.)
   - **Relevance**: Provides Frama-C-specific taxonomy as baseline

4. **Dafny FAQ & Error Documentation** (dafny.org)
   - Categorizes common verification failures (incompleteness, triggers, framing)
   - **Relevance**: Provides Dafny-specific error patterns

### 12.2 Key Findings from Research

**Archon KB Results**:
- Search for "verifier semantic primitives abstraction" returned limited direct matches
- Generic ML normalization papers not directly applicable (verification errors != ML data)

**Exa Web Search Results**:
- Frama-C WP generates 12 distinct VC types (proof obligation categories)
- Dafny errors cluster around: postcondition, invariant, precondition, quantifier issues
- Why3 serves as backend for both Frama-C and SPARK → suggests shared semantic layer exists

**Code Context (Exa)**:
- Frama-C WP API exposes proof obligation types programmatically (good for parser)
- Dafny error messages follow structured "Related location" chain (parseable)
- Why3 VC format is semi-structured (can extract goal type + formula)

**Key Insight**: All three verifiers use weakest-precondition calculus (Frama-C/Why3 explicitly, Dafny via Boogie) → shared logical foundation suggests semantic overlap is plausible.

---

## 13. Anticipated Challenges & Solutions

### 13.1 Technical Challenges

**Challenge 1: Verifier output parsing complexity**  
**Solution**: Focus on structured output modes (Frama-C `-wp-out json`, Dafny `-json`, Why3 API)  
**Fallback**: Regex-based parsing with extensive test cases

**Challenge 2: Counterexample availability varies by verifier**  
**Solution**: Make `witness` field optional in schema, document coverage per verifier  
**Impact**: Witness information is bonus (not required for categorization)

**Challenge 3: Tool-specific idioms (e.g., Dafny triggers)**  
**Solution**: Separate "core primitives" (cross-tool) from "tool-specific extensions"  
**Design**: Hybrid schema with `tool_specific_info` field

### 13.2 Methodological Challenges

**Challenge 4: Inter-rater reliability for categorization**  
**Solution**: 
- Define explicit categorization decision tree (flowchart)
- Pilot annotation on 10 examples to calibrate annotators
- Calculate Cohen's kappa on 20% overlap subset

**Challenge 5: Benchmark errors may not cover all primitives**  
**Solution**: 
- Pre-validate benchmark diversity (check annotation types present)
- Augment with targeted synthetic errors if critical categories missing
- Document primitive coverage per verifier

### 13.3 Timeline Risks

**Challenge 6: Verifier setup delays (dependency hell)**  
**Solution**: 
- Start setup Week 0 (before Phase 2C official start)
- Use Docker containers (pre-built environments)
- Allocate 2-day buffer for troubleshooting

**Challenge 7: Abstraction design iterations exceed Week 3**  
**Solution**: 
- Define "minimum viable schema" (core fields only) as fallback
- Defer optional fields (dependency_info, logical_structure) to Phase 3 if needed
- Week 4 buffer can absorb 3-day overflow

---

## 14. Success Validation Checklist

**Before declaring gate PASS, verify**:

- [ ] Error collection complete: 40+ errors per verifier (120+ total)
- [ ] All errors stored in `errors_collection.jsonl` with required fields
- [ ] Semantic primitive list finalized (8-12 categories)
- [ ] Mapping table complete: each error assigned to primitive or "unmapped"
- [ ] SemanticCoverage calculated: ≥80%
- [ ] Per-verifier coverage calculated: each ≥75%
- [ ] AvgSupport calculated: ≥0.67
- [ ] JSON schema defined with all required fields
- [ ] Parser specifications written for all 3 verifiers
- [ ] 15 test cases manually parsed to JSON with 100% success
- [ ] Abstraction viability validated: no information loss in test cases
- [ ] Negative control passed: unmapped errors are legitimately tool-specific
- [ ] Positive control passed: canonical errors map to primitives
- [ ] Experiment report written with all sections complete
- [ ] Gate decision documented with justification
- [ ] Archon task updated to `done` status
- [ ] Artifacts committed to experiment repository

---

**END OF EXPERIMENT BRIEF: H-E2**
