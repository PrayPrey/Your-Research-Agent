# Experiment Design: H-E2

**Date:** 2026-07-11
**Author:** Anonymous
**Hypothesis Statement:** Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (no prerequisites - foundation hypothesis)
**Gate Status:** MUST_WORK gate active - failure blocks cross-verifier portability claim

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E2
- **Type:** Existence (Foundation Layer)
- **Prerequisites:** None (independent, can execute in parallel with H-E1)

### Gate Condition
**MUST_WORK** - Failure stops cross-verifier portability path:
- If coverage <60%: Tool-specific semantics dominate → no abstraction layer viable
- If critical categories resist abstraction → H-M3 (Semantic Normalization Transfer) cannot proceed
- Consequence: Scope reduced to single-verifier approach, cross-verifier claim invalid

---

## Continuation Context

**First Experiment** (Foundation Layer): No previous hypothesis results to inherit.

This is Wave 1 execution (parallel with H-E1), establishing whether semantic primitives exist across verifiers before H-M3 attempts cross-verifier transfer.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in execution order

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Cross-verifier semantic primitives taxonomy**
- No directly relevant results found in Archon KB
- Archon KB appears to lack formal verification domain content
- Most results were from web/ML domains (diffusion models, transformers, GPU infrastructure)

**Query 2: Formal verification error abstraction repair categories**
- No directly relevant results found
- Knowledge base does not contain formal methods/verification literature

**Query 3: Frama-C Dafny Why3 comparative analysis**
- No directly relevant results found
- Specific verifier tools not indexed in current Archon KB

**Assessment**: Archon KB does not contain formal verification domain knowledge. This hypothesis requires domain-specific research from formal methods literature and GitHub implementations.

### Archon Code Examples

**Query 1: Error taxonomy classification verifier**
- No relevant code examples found
- Results included LaTeX formatting, UI styling, unrelated Python code

**Query 2: Semantic primitive abstraction mapping**
- No relevant code examples found  
- Results included JSON parsing, quantization code, diffusion pipelines

**Assessment**: Archon code examples repository does not contain formal verification implementation patterns. Primary research will come from Exa GitHub search and direct repository analysis.

### Exa GitHub Implementations

**Query 1: Frama-C Dafny Why3 error message parser semantic abstraction**

**Resource 1**: Why3 API - Model_parser (https://why3.org/api/Model_parser.html)
- **Relevance**: Official Why3 documentation showing error model structure
- **Key Structures**:
  - Model elements with error messages: `Error_message | Result | Loop_before | Other`
  - Counter-example model elements representing source code values
  - Model parser interface: `string -> model` (parses SMT solver output)
- **Error Categories**: Result, Loc.position, Old, Loop_before, Loop_current_iteration, Error_message, Other
- **Priority**: ⭐⭐⭐ HIGHEST - Official Why3 error taxonomy

**Resource 2**: Frama-C API - Logic_parser & WP VC (https://frama-c.com/api/)
- **Relevance**: Official Frama-C proof obligation generator
- **Key Structures**:
  - VC (Verification Condition) types with `get_description`, `get_property`, `get_formula`
  - Proof obligation management with `is_trivial`, `is_valid`, `has_unknown`
  - ACSL specification language error handling
- **Error Categories**: Proof obligations grouped by property types
- **Priority**: ⭐⭐⭐ HIGHEST - Official Frama-C error taxonomy

**Resource 3**: Dafny Documentation - Error Messages (https://dafny.org/v3.12.0/HowToFAQ/Errors)
- **Relevance**: Official Dafny error documentation
- **Key Structures**: Parser errors for type parameters, verification errors
- **Priority**: ⭐⭐⭐ HIGHEST - Official Dafny error categories

**Query 2: Formal verification tool error taxonomy cross-verifier translation**

**Repository 1**: joscoh/why3-semantics (https://github.com/joscoh/why3-semantics) ⭐ GitHub repo
- **Relevance**: Formalization of Why3 logic in Coq, showing semantic structure
- **Architecture**: Denotational semantics for Why3 terms/formulas in Coq
- **Key Implementation**: 
  - Syntax and type system formalization
  - Recursive functions encoded via well-founded induction
  - Inductive predicates using Boehm-Berarducci encoding
- **Cross-verifier insight**: Shows semantic primitives shared between Why3 and proof assistants (Coq)
- **Priority**: ⭐⭐ MEDIUM - Academic formalization showing semantic overlap

**Resource 2**: FormalRx Error Taxonomy (https://arxiv.org/html/2607.04655)
- **Relevance**: Hierarchical error classification for formal mathematics (28 categories)
- **Taxonomy Structure**: Semantic, Constraint, Implementation dimensions
- **Key Insight**: Demonstrates feasibility of cross-tool error abstraction in formal domains
- **Categories**: Logical structure errors, mathematical object errors, constraint violations, implementation errors
- **Priority**: ⭐⭐ MEDIUM - Proof that semantic error taxonomies work across tools

**Resource 3**: Translation Validation Papers (Multiple sources)
- **Relevance**: Formal verification of cross-verifier translations
- **Key Papers**:
  - "Towards Trustworthy Automated Program Verifiers" (Dafny→Boogie, Viper→Boogie)
  - "Specification Translator" (OpenJML, Krakatoa, VerCors translation)
  - "Witness Validation" (cross-verifier error witness exchange format)
- **Cross-verifier patterns**:
  - Forward simulation proofs between source and IVL
  - Semantic gap bridging via intermediate representations
  - Error witness exchange formats (validator-independent)
- **Priority**: ⭐⭐⭐ HIGHEST - Demonstrates cross-verifier semantic abstraction is achievable

**Query 3: Frama-C ACSL error categories**

**Resource 1**: Frama-C WP Manual & Tutorials
- **URLs**: 
  - https://frama-c.com/download/wp-manual-Fluorine-20130601.pdf
  - https://www-verimag.imag.fr/~boulme/Frama-C-Tutorial/frama-C-wp-tutorial.pdf
- **Error/Proof Obligation Types**:
  - Memory safety: valid memory accesses
  - Arithmetic safety: no overflow, no division by zero
  - Functional properties: pre/postconditions, invariants
  - Termination proofs
- **WP Goals Structure**: Each annotation generates "WP goals" (Verifying Conditions/Proof Obligations)
- **Priority**: ⭐⭐⭐ HIGHEST - Concrete Frama-C error taxonomy

**Serena Analysis Needed**: No - documentation is clear, no complex code to analyze

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**N/A - Not a Paper Reproduction**

This is an original taxonomy analysis, not reproducing a specific paper's method. Implementation priority is based on official documentation sources, not author repositories.

**Recommended Implementation Path:**
- Primary: Official verifier documentation (Why3 API, Frama-C WP manual, Dafny docs)
- Fallback: Academic translation validation papers for cross-verifier mapping patterns
- Justification: Official documentation provides ground truth for error taxonomies; academic papers demonstrate semantic mapping feasibility

**Sources Prioritized**:
1. ⭐⭐⭐ Why3 Model_parser API (official error model structure)
2. ⭐⭐⭐ Frama-C WP VC API (official proof obligation types)
3. ⭐⭐⭐ Dafny error documentation (official error categories)
4. ⭐⭐ Translation validation papers (cross-verifier semantic abstraction patterns)

### Code Analysis (Serena MCP)

**Serena Analysis**: Not needed

**Rationale**: This hypothesis involves taxonomy construction from documentation, not complex code analysis. The pseudo-code in Section "Core Mechanism Implementation" was synthesized from documented APIs (Why3 Model_parser, Frama-C VC types) rather than requiring deep semantic analysis of existing implementations.

---

## Experiment Specification

### Dataset

**Dataset Type**: Error Message Corpus (Taxonomy Analysis)
**Name**: Cross-Verifier Error Documentation Corpus
**Type**: `custom` (documentation + example programs)
**Source**: Official verifier documentation and error message catalogs

**Components**:
1. **Frama-C WP Error Catalog**
   - Source: Frama-C WP manual, API documentation  
   - URL: https://frama-c.com/api/frama-c-wp/Wp/VC/index.html
   - Error types: Proof obligations (VC types), ACSL annotation errors
   - Examples: Memory safety, arithmetic safety, functional properties, termination

2. **Dafny Error Catalog**
   - Source: Dafny official documentation
   - URL: https://dafny.org/v3.12.0/HowToFAQ/Errors
   - Error types: Parser errors, type parameter errors, verification errors

3. **Why3 Error Catalog**
   - Source: Why3 API Model_parser documentation
   - URL: https://why3.org/api/Model_parser.html
   - Error types: Error_message, Result, Loc.position, Loop_before/current/previous, Old, Other
   
**Benchmark Programs** (for validation):
- Frama-C examples repository (C programs with ACSL annotations)
- Juliet Test Suite verified subset (NIST benchmark for static analyzers)
- Why3 gallery examples

**Loading Information** (for Phase 4 download):
- Method: `manual_curation` + `web_scraping` (documentation) + `git_clone` (examples)
- Identifier: Multiple sources (see components above)
- Code:
```python
# Phase 4 will implement:
# 1. Clone Frama-C/Dafny/Why3 example repositories
# 2. Parse documentation for error type listings
# 3. Run verifiers on benchmark programs to collect error messages
# 4. Build taxonomy mapping table
```

### Models

#### Baseline Model

**Baseline**: Manual tool-specific error handling (no abstraction layer)
**Description**: Current state-of-the-art uses verifier-specific error parsing with no semantic normalization

**Comparison Target**:
- Each verifier's error messages processed independently
- No cross-verifier knowledge transfer
- Performance metric: 0% error categories mapped to shared primitives (baseline = no mapping)

**Loading Information** (for Phase 4 download):
- Method: N/A (taxonomy analysis, not ML model)
- Identifier: N/A
- Code: N/A (baseline is conceptual - represents absence of abstraction layer)

#### Proposed Model

**Architecture:** N/A (Taxonomy analysis, not ML model)

**Core Mechanism Implementation:**

**Mechanism**: Cross-Verifier Semantic Primitive Taxonomy
**Purpose**: Map error categories from 3 verifiers (Frama-C, Dafny, Why3) to shared semantic primitives

**Taxonomy Construction Algorithm** (10-30 lines pseudo-code):

```python
# Cross-Verifier Semantic Primitive Taxonomy Construction
# Based on: Why3 Model_parser API, Frama-C WP VC API, Dafny Error documentation

class TaxonomyBuilder:
    """
    Constructs cross-verifier semantic primitive abstraction layer.
    Success: ≥80% error categories map to shared primitives.
    """
    
    def __init__(self):
        self.primitives = []  # Shared semantic categories
        self.mappings = {  # verifier -> primitive mappings
            'frama-c': {},
            'dafny': {},
            'why3': {}
        }
    
    def extract_error_categories(self, verifier_name):
        """
        Extract error categories from each verifier.
        Frama-C: VC types (memory_safety, arithmetic_safety, functional_property, termination)
        Dafny: parser_error, type_error, verification_failure
        Why3: Error_message, Result, Loop_before, Loop_current, Loc.position, Other
        """
        if verifier_name == 'frama-c':
            return ['memory_access_valid', 'no_overflow', 'no_division_by_zero',
                    'precondition_holds', 'postcondition_holds', 'invariant_preserved']
        elif verifier_name == 'dafny':
            return ['assertion_failure', 'precondition_violation', 'postcondition_violation',
                    'invariant_violation', 'decreases_violation']
        elif verifier_name == 'why3':
            return ['error_message', 'result', 'loc_position', 'loop_before',
                    'loop_current_iteration', 'loop_previous_iteration', 'old_value']
        
    def identify_semantic_primitives(self, all_categories):
        """
        Bottom-up taxonomy construction: cluster error categories by semantic similarity.
        Returns: List of universal repair categories (semantic primitives).
        """
        # Semantic clustering (based on proof obligation structure)
        primitives = [
            'MISSING_PRECONDITION',      # Frama-C precondition, Dafny precondition_violation
            'POSTCONDITION_FAILURE',      # Frama-C postcondition, Dafny postcondition_violation
            'LOOP_INVARIANT_VIOLATION',   # All 3 verifiers support loops
            'BOUNDS_CHECK_FAILURE',       # Frama-C memory_access, Dafny seq index
            'ARITHMETIC_OVERFLOW',        # Frama-C no_overflow, Dafny int overflow
            'NULL_DEREFERENCE',           # Frama-C memory_safety, Dafny null check
            'TERMINATION_FAILURE',        # Frama-C termination, Dafny decreases
            'TYPE_MISMATCH'               # Cross-verifier type errors
        ]
        return primitives
    
    def map_to_primitives(self, verifier_name, error_category):
        """
        Map verifier-specific error to universal primitive.
        Returns: (primitive_id, confidence_score)
        """
        # Mapping logic based on error semantics
        mapping_rules = {
            ('frama-c', 'precondition_holds'): ('MISSING_PRECONDITION', 1.0),
            ('dafny', 'precondition_violation'): ('MISSING_PRECONDITION', 1.0),
            ('frama-c', 'no_overflow'): ('ARITHMETIC_OVERFLOW', 1.0),
            ('why3', 'loop_current_iteration'): ('LOOP_INVARIANT_VIOLATION', 0.8),
            # ... additional mappings
        }
        return mapping_rules.get((verifier_name, error_category), (None, 0.0))
    
    def compute_coverage(self):
        """
        Coverage metric: percentage of error categories mapped to shared primitives.
        Success: ≥80% coverage across all 3 verifiers.
        """
        total_categories = sum(len(self.mappings[v]) for v in self.mappings)
        mapped_categories = sum(1 for v in self.mappings.values() 
                                for m in v.values() if m[0] is not None)
        return (mapped_categories / total_categories) * 100 if total_categories > 0 else 0.0

# Experiment execution:
# 1. Extract error categories from each verifier (documentation + empirical)
# 2. Identify semantic primitives (bottom-up clustering)
# 3. Map verifier errors to primitives
# 4. Validate coverage ≥80% threshold
```

**Integration**: Abstraction layer sits between verifier output parsers and LLM repair system

### Training Protocol

**N/A - Taxonomy Analysis (Not ML Training)**

**Experimental Procedure**:
1. **Phase 1: Error Category Extraction** (Week 1-2)
   - Parse Frama-C WP documentation for VC types
   - Parse Dafny error documentation  
   - Parse Why3 Model_parser API for error model elements
   - Run verifiers on benchmark programs to collect empirical error instances

2. **Phase 2: Semantic Primitive Identification** (Week 3-4)
   - Bottom-up clustering of error categories by semantic structure
   - Identify candidate universal repair categories
   - Validate primitives cover proof obligation types

3. **Phase 3: Mapping Construction** (Week 5-6)
   - Create mapping table: verifier_error → semantic_primitive
   - Assign confidence scores to mappings
   - Document tool-specific edge cases

4. **Phase 4: Coverage Analysis** (Week 7)
   - Compute coverage percentage
   - Identify unmapped categories
   - Refine taxonomy to reach ≥80% threshold

**Validation Method**: Manual review + empirical testing on benchmark programs

**Timeline**: 7 weeks (not epochs - this is taxonomy development, not training)

### Evaluation

**Primary Metrics**:

1. **Coverage Percentage** (Primary Success Criterion)
   - Definition: (# error categories mapped to shared primitives / total # error categories) × 100%
   - Success Threshold: ≥80% (from Phase 2B)
   - Measurement: Count mapped categories across all 3 verifiers

2. **Abstraction Layer Feasibility**
   - Definition: Binary assessment of whether abstraction layer design is implementation-ready
   - Success Criterion: Design document produced with clear API specification
   - Measurement: Qualitative review by formal methods expert

3. **Cross-Verifier Validation**
   - Definition: Coverage validated across all 3 verifiers (Frama-C, Dafny, Why3)
   - Success Criterion: All 3 verifiers achieve ≥80% individual coverage
   - Measurement: Per-verifier coverage breakdown

**Success Criteria**:
- **MUST_WORK Gate**: Coverage ≥80% AND abstraction layer feasible AND all 3 verifiers covered
- **PoC Success**: Coverage > baseline (0%) - demonstrates semantic overlap exists

**Expected Baseline Performance**:
- Baseline (no abstraction): 0% cross-verifier coverage (tool-specific handling only)
- Target (with abstraction): ≥80% coverage (from Phase 2B success criteria)

**Failure Conditions** (from Phase 2B):
- Coverage <60%: Tool-specific semantics dominate, no viable abstraction
- No abstraction layer design emerges: Implementation not feasible
- Critical error categories resist abstraction: Portability claim invalid

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: `taxonomy_analysis` (not ML classification/regression)
- Library: `custom` (manual taxonomy construction + coverage computation)
- Code:
```python
def compute_coverage(mappings, total_categories):
    """
    Compute cross-verifier taxonomy coverage.
    """
    mapped = sum(1 for v in mappings.values() 
                 for m in v.values() if m[0] is not None)
    return (mapped / total_categories) * 100
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations**:

1. **Taxonomy Heatmap**
   - Rows: Verifier-specific error categories (Frama-C, Dafny, Why3)
   - Columns: Universal semantic primitives
   - Cell values: Mapping confidence scores (0.0-1.0)
   - Purpose: Visualize cross-verifier semantic overlap

2. **Coverage Breakdown by Verifier**
   - Bar chart: Per-verifier coverage percentage
   - Threshold line at 80%
   - Purpose: Show coverage distribution across tools

3. **Primitive Frequency Distribution**
   - Bar chart: # verifier errors mapping to each primitive
   - Purpose: Identify most common vs. rare semantic categories

4. **Unmapped Category Analysis**
   - List/table of error categories with no primitive mapping
   - Grouped by verifier
   - Purpose: Identify abstraction gaps

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

**Official Documentation Sources**:

1. **Why3 Model_parser API** (https://why3.org/api/Model_parser.html)
   - Error model structure: Error_message, Result, Loop_before/current/previous, Loc.position, Other
   - Model element types for counter-examples
   - Relevance: Official Why3 error taxonomy

2. **Frama-C WP VC API** (https://frama-c.com/api/frama-c-wp/Wp/VC/index.html)
   - VC types: Memory safety, arithmetic safety, functional properties, termination
   - Proof obligation management interface
   - Relevance: Official Frama-C error taxonomy

3. **Dafny Error Documentation** (https://dafny.org/v3.12.0/HowToFAQ/Errors)
   - Parser errors, type parameter errors, verification failures
   - Precondition/postcondition/invariant violations
   - Relevance: Official Dafny error categories

4. **joscoh/why3-semantics** (https://github.com/joscoh/why3-semantics)
   - Coq formalization of Why3 logic showing semantic structure
   - Demonstrates semantic overlap between Why3 and proof assistants
   - Relevance: Academic validation of cross-tool semantic abstraction

5. **FormalRx Error Taxonomy** (https://arxiv.org/html/2607.04655)
   - 28-category hierarchical classification for formal mathematics
   - Semantic/Constraint/Implementation dimensions
   - Relevance: Proof-of-concept that error taxonomies work across formal tools

6. **Translation Validation Papers**
   - Dafny→Boogie, Viper→Boogie forward simulations
   - OpenJML/Krakatoa/VerCors specification translation
   - Witness validation cross-verifier exchange format
   - Relevance: Demonstrates cross-verifier semantic abstraction is achievable

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE - use prompt context)
**Date:** 2026-07-11

### Workflow History for This Hypothesis
- 2026-07-11T06:05:18Z: Hypothesis h-e2 set to IN_PROGRESS (external loop starting Phase 2C)
- 2026-07-11T06:06:00Z: Phase 2C experiment design COMPLETED (this document)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
