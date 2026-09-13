# Methodology

We present a three-layer contract-based validation architecture for research pipeline phase transitions. The methodology follows directly from our key insight: feasibility constraints are semantic and compositional, requiring explicit checking beyond what schema validation can express. We first describe the constraint types our system targets (Section 3.1), then present the three validation layers and their complementary roles (Section 3.2), and conclude with design rationale for key architectural decisions (Section 3.3).

## 3.1 Constraint Types and Formalization

Research workflows with feasibility constraints require enforcement of four distinct constraint classes:

**C1 (Keyword Pattern Constraint):** No synthetic data generation allowed. Formally: `∀ dataset_name, "synthetic" ∉ dataset_name.lower() ∧ "generated" ∉ dataset_name.lower()`. This constraint restricts dataset names to exclude forbidden keywords indicating data synthesis.

**C2 (Keyword Blacklist Constraint):** No human evaluation methods allowed. Formally: `∀ evaluation_method, {"human", "manual", "annotator"} ∩ evaluation_method.lower().split() = ∅`. This constraint prohibits evaluation approaches requiring human judgment.

**C3 (Cross-Field Logic Constraint):** Standard dataset membership validation. Formally: `dataset_type = "standard" → dataset_name ∈ STANDARD_DATASETS`. This constraint enforces conditional membership — when a hypothesis declares it uses standard datasets, the named dataset must exist in the approved standard dataset registry.

**C4 (State-Based Constraint):** No new benchmark creation. Formally: `evaluation_method.contains("benchmark") → ∃b ∈ EXISTING_BENCHMARKS : b ∈ evaluation_method`. This constraint requires that any mentioned benchmark exists in the external benchmark registry.

These constraint types represent distinct validation challenges: C1 and C2 require semantic content analysis (keyword detection), C3 requires cross-field conditional logic, and C4 requires access to external state (benchmark registry). Schema validation alone cannot express any of these constraints.

## 3.2 Three-Layer Validation Architecture

Our validation architecture consists of three complementary layers, each targeting violations the previous layer cannot detect:

### Layer 1: Schema Validation (Structural)

The schema layer validates structural properties using Pydantic BaseModel with typed fields:

```python
class Phase2AOutput(BaseModel):
    research_question: str
    dataset_name: str
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    evaluation_method: str
    hypotheses: List[str] = Field(..., min_length=1)
```

This layer catches type errors (wrong field types), missing required fields, and simple field constraints (minimum list length). It cannot detect semantic violations (keywords in string fields) or compositional failures (cross-field dependencies).

**Coverage:** C1: ✗, C2: ✗, C3: ✗, C4: ✗ (0% constraint coverage)

### Layer 2: Pattern Validation (Semantic)

The pattern layer adds field validators that check semantic content using keyword matching:

```python
@field_validator("dataset_name")
@classmethod
def validate_no_synthetic(cls, v: str):
    forbidden = ["synthetic", "simulated", "generated"]
    if any(kw in v.lower() for kw in forbidden):
        raise ValueError("C1 violation: synthetic data forbidden")
    return v

@field_validator("evaluation_method")
@classmethod
def validate_no_human_eval(cls, v: str):
    forbidden = ["human", "manual", "annotator"]
    if any(kw in v.lower() for kw in forbidden):
        raise ValueError("C2 violation: human evaluation forbidden")
    return v
```

This layer extends schema validation with semantic checks on field content. It handles C1 and C2 (keyword patterns) but cannot express C3 (cross-field logic requires access to multiple fields simultaneously) or C4 (state-based validation requires external data).

**Coverage:** C1: ✓, C2: ✓, C3: ✗, C4: ✗ (50% constraint coverage)

### Layer 3: Compositional Contracts (Cross-Field and State-Based)

The contract layer adds postconditions using icontract decorators for constraints requiring cross-field logic or external state:

```python
@ensure(
    lambda self: self.dataset_type != "standard" or 
                 self.dataset_name in STANDARD_DATASETS,
    "C3 violation: unknown standard dataset"
)
def validate_cross_field(self):
    return self

def _validate_no_new_benchmarks(self):
    if "benchmark" in self.evaluation_method.lower():
        benchmark_mentioned = any(
            b.lower() in self.evaluation_method.lower()
            for b in EXISTING_BENCHMARKS
        )
        if not benchmark_mentioned:
            raise ViolationError("C4 violation: new benchmark")
```

The contract layer enforces compositional constraints that pattern validators cannot express. The `@ensure` decorator executes after object construction, checking postconditions over the complete validated object. This enables cross-field logic (C3: IF-THEN rule) and state-based validation (C4: membership in external registry).

**Coverage:** C1: ✓ (inherited), C2: ✓ (inherited), C3: ✓, C4: ✓ (100% constraint coverage)

### Layer Complementarity

The three layers are complementary, not redundant. Each layer catches violations the previous layer misses:

- Schema catches structural errors (wrong types, missing fields)
- Pattern catches semantic errors schema cannot detect (forbidden keywords)
- Contract catches compositional errors pattern cannot express (cross-field rules, state dependencies)

This complementarity is critical: removing any layer reduces constraint coverage and allows violations to propagate to downstream phases.

## 3.3 Design Rationale

**Why three layers rather than two?** We considered a two-layer architecture (schema + contract) that encodes all validation in contracts. However, this design duplicates pattern matching logic in contract specifications, increasing specification burden. The three-layer architecture isolates concerns: schemas validate structure, patterns validate keywords, contracts validate composition. This separation reduces per-constraint specification cost (7 LOC average vs 15 LOC for contract-only).

**Why icontract rather than Pydantic validators?** We chose icontract for the contract layer because Design-by-Contract semantics (preconditions, postconditions, invariants) map naturally to phase transitions. Pydantic's `@model_validator` could encode contracts but lacks the explicit precondition/postcondition framing that makes contract specifications self-documenting. The icontract `@ensure` decorator executes after object construction, checking postconditions over the complete validated object.

**Why fail-fast at boundaries?** Research pipelines have sequential phase dependencies — Phase N+1 requires Phase N output. Early boundary validation halts the pipeline immediately on violation, preventing infeasible hypotheses from consuming compute resources in downstream implementation phases. Alternative approaches (collect violations, generate report, continue) allow constraint violations to propagate, defeating the purpose of boundary validation.

**Why layer execution order matters?** Layers execute schema → pattern → contract, ordered by increasing expressiveness and decreasing performance cost. Schema validation runs first (fastest), catching structural errors before pattern matching. Pattern validation runs second, catching keyword violations before expensive cross-field checks. Contract validation runs last, catching compositional failures only if previous layers pass. This ordering minimizes wasted computation on obviously invalid inputs.

The methodology implements a simple principle: validate constraints at the earliest point where they can be detected, using the layer with sufficient expressiveness to encode the constraint. The result is a multi-layer boundary validation system that forces explicit checking of semantic and compositional constraints schema-only validation leaves implicit.
