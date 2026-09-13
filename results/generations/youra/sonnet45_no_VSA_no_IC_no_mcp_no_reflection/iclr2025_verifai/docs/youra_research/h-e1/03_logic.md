# Logic Specification: h-e1 SMT Constraint Extraction

**Date:** 2026-08-28
**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)
**Author:** Phase 3 Logic Agent

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Dataset Preparation [Complexity: 8, Budget: 8]

**Applied**: HuggingFace datasets + template string formatting

### API Signatures

```python
def extend_humaneval_prompt(problem: dict) -> dict:
    """Add Pydantic annotations to HumanEval prompt.
    problem: {"prompt": str, "entry_point": str, ...}
    Returns: {"prompt": str (extended), "entry_point": str, ...}
    """
    ...

def prepare_dataset(output_dir: str, n_problems: int = 100) -> List[dict]:
    """Load HumanEval, extend first n_problems with Pydantic.
    Returns: List[dict] of extended problems
    """
    ...
```

### Pseudo-code

```
1. Load dataset("openai_humaneval")
2. Take first 100 problems
3. For each:
   - Parse function signature
   - Generate Pydantic BaseModel template
   - Prepend to original prompt
   - Save to output_dir/{id}.json
4. Return list of extended problems
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-1-1 | Load dataset | datasets.load_dataset |
| A-1-2 | Slice subset | problems[:100] |
| A-1-3 | Parse signature | Extract types from prompt |
| A-1-4 | Template fill | Format Pydantic boilerplate |
| A-1-5 | Prepend | Combine template + prompt |
| A-1-6 | Save JSON | Write to output_dir |
| A-1-7 | Collect list | Aggregate results |
| A-1-8 | Return | Return extended problems |

---

## A-2: LLM Code Generation [Complexity: 9, Budget: 9]

**Applied**: Anthropic API with retry + rate limiting

### API Signatures

```python
def generate_code(prompt: str) -> str:
    """Call Claude API to generate typed Python.
    prompt: str (extended HumanEval prompt)
    Returns: str (generated Python code)
    """
    ...

def batch_generate(problems: List[dict], output_dir: str) -> List[str]:
    """Generate code for all problems with rate limiting.
    Returns: List[str] of output file paths
    """
    ...
```

### Pseudo-code

```
1. Init Anthropic client (api_key from env)
2. For each problem:
   - Call client.messages.create(
       model="claude-sonnet-3-5-20240620",
       messages=[{"role": "user", "content": prompt}],
       temperature=0.2,
       max_tokens=512
     )
   - Extract response.content[0].text
   - Save to output_dir/{id}.py
   - Sleep 6s (10 req/min limit)
3. Return file paths
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-2-1 | Client init | Anthropic(api_key) |
| A-2-2 | Message format | Build request dict |
| A-2-3 | API call | client.messages.create |
| A-2-4 | Extract text | Parse response |
| A-2-5 | Save file | Write .py to disk |
| A-2-6 | Rate limit | time.sleep(6) |
| A-2-7 | Retry logic | 3x exponential backoff |
| A-2-8 | Batch loop | Process all problems |
| A-2-9 | Return paths | Collect file paths |

---

## A-3: Constraint Extraction [Complexity: 10, Budget: 10]

**Applied**: AST parsing (stdlib ast module)

### API Signatures

```python
def extract_constraints(python_file: str) -> list:
    """Extract SMT constraints from typed Python.
    python_file: str (path to .py)
    Returns: List[dict] with constraint predicates, [] if failed
    
    Constraint format:
    {"type": "precondition"|"postcondition"|"contract",
     "predicate": str,
     "field": str,
     "source_line": int}
    """
    ...
```

### Tensor Shapes

| Variable | Type | Note |
|----------|------|------|
| constraints | List[dict] | Per-file results |
| constraint["predicate"] | str | SMT expression |

### Pseudo-code

```
1. Read file, parse with ast.parse()
2. Find ClassDef nodes inheriting BaseModel
3. For each @validator method:
   - Extract field name from decorator
   - Find assert statements in body
   - Convert to {"type": "precondition", "predicate": ast.unparse(assert.test), ...}
4. For each FunctionDef:
   - Extract arg types, return type
   - Build {"type": "contract", "precondition": args_str, "postcondition": return_str, ...}
5. Return constraints list
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-3-1 | Read file | Load source |
| A-3-2 | Parse AST | ast.parse |
| A-3-3 | Find BaseModel | Traverse ClassDef |
| A-3-4 | Find validators | Check decorators |
| A-3-5 | Extract field | Parse decorator args |
| A-3-6 | Parse assert | Get assertion expr |
| A-3-7 | Unparse predicate | ast.unparse |
| A-3-8 | Find functions | Traverse FunctionDef |
| A-3-9 | Extract types | Parse annotations |
| A-3-10 | Return list | Aggregate constraints |

---

## A-4: Constraint Quality Verification [Complexity: 7, Budget: 7]

**Applied**: Z3 SMT solver satisfiability check

### API Signatures

```python
def check_constraint_quality(constraint: dict) -> bool:
    """Verify constraint is satisfiable (non-trivial).
    constraint: dict with "predicate" field
    Returns: True if sat, False otherwise
    """
    ...
```

### Pseudo-code

```
1. Init Z3 Solver()
2. Parse predicate to identify variable type (Int/Real/Bool)
3. Create Z3 variable
4. Convert predicate to Z3 expr (e.g., "v > 0" → Real('v') > 0)
5. solver.add(z3_expr)
6. Return solver.check() == sat
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-4-1 | Init solver | Z3 Solver() |
| A-4-2 | Parse predicate | Extract var/op/val |
| A-4-3 | Infer type | Determine Int/Real/Bool |
| A-4-4 | Create Z3 var | Declare variable |
| A-4-5 | Convert expr | Predicate to Z3 |
| A-4-6 | Check sat | solver.check() |
| A-4-7 | Return bool | sat == True |

---

## A-5: Metrics & Visualization [Complexity: 11, Budget: 11]

**Applied**: Simple arithmetic + matplotlib

### API Signatures

```python
def compute_metrics(results: list) -> dict:
    """Calculate extraction rate and quality rate.
    results: List[dict] with "constraints" and "quality_checks"
    Returns: {
        "extraction_success_rate": float,
        "programs_with_constraints": int,
        "total_programs": int,
        "constraint_quality_rate": float,
        "non_trivial_constraints": int,
        "total_extracted_constraints": int,
        "gate_result": "PASS"|"FAIL"
    }
    """
    ...

def plot_gate_metrics(metrics: dict, output_path: str):
    """Bar chart: target vs actual for extraction/quality rates."""
    ...
```

### Pseudo-code

```
1. Count programs_with_constraints (len(constraints) > 0)
2. extraction_success_rate = (programs_with_constraints / 100) * 100
3. constraint_quality_rate = (sum(quality_checks) / total_constraints) * 100
4. gate_result = "PASS" if extraction_success_rate >= 90 else "FAIL"
5. Plot bar chart with matplotlib (2 groups: extraction, quality)
6. Return metrics dict
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-5-1 | Count programs | Iterate results |
| A-5-2 | Count constraints | Sum constraint lists |
| A-5-3 | Count quality | Sum quality checks |
| A-5-4 | Compute extraction | Rate calc |
| A-5-5 | Compute quality | Rate calc |
| A-5-6 | Evaluate gate | Threshold check |
| A-5-7 | Plot gate metrics | Matplotlib bar chart |
| A-5-8 | Plot by complexity | Optional bar chart |
| A-5-9 | Plot distribution | Optional pie chart |
| A-5-10 | Save metrics | Write JSON |
| A-5-11 | Return dict | Results |

---

## Pipeline Integration

```python
def run_experiment():
    """Main pipeline."""
    # A-1
    problems = prepare_dataset("data/humaneval_pydantic", n_problems=100)
    
    # A-2
    files = batch_generate(problems, "outputs/generated_code")
    
    # A-3 + A-4
    results = []
    for f in files:
        constraints = extract_constraints(f)
        quality = [check_constraint_quality(c) for c in constraints]
        results.append({"constraints": constraints, "quality_checks": quality})
    
    # A-5
    metrics = compute_metrics(results)
    plot_gate_metrics(metrics, "figures/gate_metrics.png")
    
    with open("outputs/metrics.json", "w") as out:
        json.dump(metrics, out)
    
    return metrics
```

---

## Edge Cases

### A-1
- Empty problem → Skip, log
- Missing types → Default to "Any"

### A-2
- API timeout → Retry 3x
- Rate limit → Sleep 60s

### A-3
- Parse error → Return []
- No validators → Extract only function contracts

### A-4
- Z3 timeout → Exclude from quality rate
- Parse error → Return False

### A-5
- No constraints → quality_rate = 0
- Gate fail → Log "FAIL"

---

## Total Budget: 45/45

| Task | Budget | Used |
|------|--------|------|
| A-1 | 8 | 8 |
| A-2 | 9 | 9 |
| A-3 | 10 | 10 |
| A-4 | 7 | 7 |
| A-5 | 11 | 11 |
| **Total** | **45** | **45** |
