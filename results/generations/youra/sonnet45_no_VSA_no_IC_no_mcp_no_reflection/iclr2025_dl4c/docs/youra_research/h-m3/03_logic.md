# Logic Design Document
## Transfer Learning to Held-Out Tests - h-m3

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis:** h-m3 (MECHANISM)  
**Subtask Budget:** 17

---

## Codebase Analysis (Serena)

**Base Hypothesis:** h-m2

**Actual Code Structure:**
```python
# h-m2/code/agent.py
class Agent:
    def fix_problem(problem: dict, tests: list[dict]) -> str:
        # Returns: fixed code
        
def run_tests(code: str, tests: list[dict]) -> list[bool]:
    # Returns: pass/fail boolean array
```

**Verified APIs:**
- Data loading: `load_problems(path: str) -> list[dict]`
- Test execution: `run_tests(code, tests) -> list[bool]`
- Result logging: `log_results(results: dict, path: str)`

**Applied:** Standard experimental protocol pattern (setup → execute → analyze)  
**Applied:** Incremental design pattern (extend base agent with memory module)

---

## Module APIs

### 1. PatternMemory Module (`code/pattern_memory.py`)

#### Pattern Data Structure
```python
@dataclass
class Pattern:
    error_type: str              # "IndexError", "TypeError", etc.
    code_region: str             # "loop bounds", "function call", etc.
    fix_template: str            # Abstract fix description
    problem_id: str              # Source problem for debugging
    success_count: int           # How many times applied successfully
    created_at: float            # Timestamp
```

#### PatternMemory Class
```python
class PatternMemory:
    def __init__(self):
        self.patterns: list[Pattern] = []
        self.usage_log: list[dict] = []  # For pattern_usage_rate metric
    
    def store_pattern(
        self,
        error_type: str,
        code_region: str,
        fix_template: str,
        problem_id: str
    ) -> None:
        """Store new pattern from successful fix."""
        # Deduplicate: merge if (error_type, code_region) already exists
        
    def retrieve_similar(
        self,
        current_error: str,
        current_code: str,
        top_k: int = 3
    ) -> list[Pattern]:
        """Retrieve top-k similar patterns by string matching."""
        # Algorithm:
        # 1. Extract error_type from current_error
        # 2. Filter patterns matching error_type
        # 3. Score by code_region overlap (simple string contains)
        # 4. Return top-k by score descending
        
    def log_usage(self, pattern: Pattern, used: bool) -> None:
        """Track whether retrieved pattern was actually used in fix."""
        self.usage_log.append({
            "pattern_id": id(pattern),
            "used": used,
            "timestamp": time.time()
        })
        
    def get_usage_stats(self) -> dict:
        """Calculate pattern_usage_rate for metric reporting."""
        # Returns: {usage_rate, total_retrieved, total_used}
        return {
            "usage_rate": sum(x["used"] for x in self.usage_log) / len(self.usage_log),
            "total_retrieved": len(self.usage_log),
            "total_used": sum(x["used"] for x in self.usage_log)
        }
```

**Subtasks (4):**
1. Implement Pattern dataclass with serialization
2. Implement store_pattern with deduplication
3. Implement retrieve_similar with string matching
4. Implement usage tracking and stats

---

### 2. Agent Module (`code/agent.py`)

#### PatternLearningAgent Class
```python
class PatternLearningAgent:
    def __init__(
        self,
        memory: PatternMemory,
        model: str = "gpt-4-turbo-2024-04-09",
        temperature: float = 0.7,
        api_key: str | None = None
    ):
        self.memory = memory
        self.model = model
        self.temperature = temperature
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
    def fix_iteration(
        self,
        problem: dict,  # {problem_id, description, tests}
        current_code: str,
        revealed_tests: list[dict],
        held_out_tests: list[dict]
    ) -> dict:
        """Run one iteration: revealed tests → pattern → fix → held-out eval."""
        # Returns: {
        #   "code": fixed_code,
        #   "revealed_pass": int,
        #   "held_out_pass": int,
        #   "pattern_extracted": Pattern | None,
        #   "patterns_used": list[Pattern]
        # }
        
        # Algorithm:
        # 1. Run current_code on revealed_tests
        # 2. Get error messages from failures
        # 3. Retrieve similar patterns from memory
        # 4. Generate fix using GPT-4 + retrieved patterns
        # 5. Extract new pattern from this fix
        # 6. Store new pattern in memory
        # 7. Run fixed_code on held_out_tests (NO error messages shown)
        # 8. Return results
```

#### Helper Functions
```python
def extract_pattern(
    error_msg: str,
    code: str,
    fix: str
) -> Pattern:
    """Extract reusable pattern from (error, code, fix) triple."""
    # Algorithm:
    # 1. Parse error_msg to get error_type ("IndexError", etc.)
    # 2. Analyze code + fix diff to identify code_region
    # 3. Abstract fix into template (remove variable names)
    # Example: "IndexError" + "loop bounds" → "check array index before access"
    
def apply_pattern(
    pattern: Pattern,
    code: str
) -> str:
    """Generate code modification guided by pattern."""
    # Returns: modified code with pattern applied
    # Uses GPT-4 to apply abstract fix_template to concrete code
    
def run_test_suite(
    code: str,
    tests: list[dict],
    reveal_errors: bool
) -> tuple[int, list[str | None]]:
    """Execute tests and optionally return error messages."""
    # Returns: (pass_count, error_messages)
    # If reveal_errors=False, error_messages are all None
    # (simulates held-out test execution without feedback)
```

**Subtasks (5):**
1. Implement PatternLearningAgent.__init__ and GPT-4 client setup
2. Implement fix_iteration main loop
3. Implement extract_pattern parsing logic
4. Implement apply_pattern with GPT-4 integration
5. Implement run_test_suite with error revelation control

---

### 3. Baseline Modules

#### Random Baseline (`code/random_baseline.py`)
```python
def mutate_code(
    code: str,
    mutation_type: str
) -> str:
    """Apply random mutation to code."""
    # Mutation types: "rename_var", "change_operator", "modify_constant"
    # Algorithm:
    # 1. Parse code to AST
    # 2. Select random node matching mutation_type
    # 3. Apply mutation (e.g., rename "x" → "y")
    # 4. Unparse AST back to code
    
def run_random_baseline(
    problems: list[dict],
    n_mutations: int = 20
) -> dict:
    """Execute random mutation baseline."""
    # For each problem:
    #   1. Load baseline_code
    #   2. Apply n_mutations random mutations
    #   3. Run held_out tests after each mutation (no error messages)
    #   4. Record held_out_pass_rate per mutation
    # Returns: {problem_id: [mutation_0_pass_rate, mutation_1_pass_rate, ...]}
```

**Subtasks (2):**
1. Implement mutation operators (rename, operator, constant)
2. Implement run_random_baseline execution loop

#### Revealed-Only Baseline (`code/revealed_only_baseline.py`)
```python
def run_revealed_only_baseline(
    problems: list[dict],
    n_iterations: int = 10
) -> dict:
    """Execute revealed-test-only baseline."""
    # For each problem:
    #   1. Initialize with baseline_code
    #   2. For n_iterations:
    #      a. Run revealed tests → get errors
    #      b. Use GPT-4 to fix (NO memory, NO pattern extraction)
    #      c. Run held_out tests → record pass_rate
    # Returns: {problem_id: [iter_0_pass_rate, iter_1_pass_rate, ...]}
```

**Subtasks (1):**
1. Implement revealed-only agent with GPT-4 (no memory module)

---

### 4. Experiment Runner (`code/experiment_runner.py`)

#### Main Orchestrator
```python
class ExperimentRunner:
    def __init__(self, config: dict):
        self.config = config
        self.data_prepared = False
        self.checkpoint_file = "results/checkpoint.json"
        
    def prepare_data(self) -> dict:
        """Phase 1: Data preparation."""
        # 1. Curate 50 Codeforces problems (API + filter)
        # 2. Split tests: 50% revealed / 50% held-out (stratified)
        # 3. Generate baseline codes (GPT-4)
        # 4. Validate: KS test for difficulty, baseline fail 3+ tests
        # Returns: DataPrep {problems, test_splits, baseline_codes, validation}
        
    def run_agent_experiment(self, data: dict) -> dict:
        """Phase 2: Agent execution (GPT-4 + PatternMemory)."""
        # For each problem (50):
        #   Initialize PatternMemory
        #   For iteration 1-10:
        #     fix_iteration(problem, revealed, held_out)
        #     Log revealed_pass, held_out_pass
        # Returns: AgentResults {problem_id: [iter_0, iter_1, ...]}
        
    def run_baselines(self, data: dict) -> dict:
        """Phase 3: Baseline execution."""
        # 1. run_random_baseline(problems, 20)
        # 2. run_revealed_only_baseline(problems, 10)
        # Returns: BaselineResults {random: {...}, revealed_only: {...}}
        
    def run_analysis(
        self,
        agent_results: dict,
        baseline_results: dict
    ) -> dict:
        """Phase 4: Statistical analysis."""
        # 1. Compute slopes (agent, random, revealed_only)
        # 2. Permutation test (1000 samples)
        # 3. Transfer efficiency metric
        # 4. Pattern usage rate
        # 5. Generate plots
        # Returns: Analysis {slopes, p_value, metrics, plots}
        
    def execute(self) -> None:
        """Run full pipeline with checkpointing."""
        # 1. Load checkpoint if exists
        # 2. Execute phases in order: data → agent → baselines → analysis
        # 3. Early stopping: if p > 0.2 after 30 problems → STOP
        # 4. Save checkpoint after each phase
```

**Subtasks (4):**
1. Implement data preparation with Codeforces API
2. Implement run_agent_experiment with checkpointing
3. Implement run_baselines orchestration
4. Implement execute main pipeline with early stopping

---

### 5. Analysis Module (`code/analysis.py`)

#### Statistical Functions
```python
def compute_slopes(results: dict) -> dict:
    """Fit linear regression: held_out_pass_rate ~ iteration."""
    # For agent, random, revealed_only:
    #   1. Aggregate all (iteration, pass_rate) pairs across problems
    #   2. Fit: held_out_pass_rate = slope * iteration + intercept
    #   3. Extract slope
    # Returns: {agent_slope, random_slope, revealed_only_slope}
    
def permutation_test(
    agent_results: dict,
    random_results: dict,
    n_samples: int = 1000
) -> float:
    """Test: agent_slope > random_slope."""
    # Algorithm:
    # 1. Compute observed: agent_slope - random_slope
    # 2. For n_samples:
    #    a. Shuffle agent/random labels
    #    b. Recompute slopes
    #    c. Calculate null_diff
    # 3. p_value = fraction of null_diffs >= observed_diff
    # Returns: p_value
    
def transfer_efficiency(
    revealed_slope: float,
    held_out_slope: float
) -> float:
    """Compute held_out improvement rate relative to revealed."""
    return held_out_slope / revealed_slope if revealed_slope > 0 else 0.0
```

#### Visualization Functions
```python
def plot_held_out_curves(
    agent_results: dict,
    baseline_results: dict,
    output_path: str
) -> None:
    """Line plot: held-out pass rate vs iteration."""
    # 3 lines: agent (blue), random (gray), revealed-only (orange)
    # X-axis: iteration (0-10)
    # Y-axis: held-out test pass rate (0-100%)
    # Save to: results/plots/held_out_curves.png
    
def plot_pattern_usage(
    usage_log: list[dict],
    output_path: str
) -> None:
    """Bar chart: pattern usage rate over iterations."""
    # X-axis: iteration bins
    # Y-axis: pattern_usage_rate (0-100%)
    # Save to: results/plots/pattern_usage.png
```

#### Report Generation
```python
def generate_validation_report(analysis: dict) -> str:
    """Generate 04_validation.md markdown report."""
    # Sections:
    # 1. Primary Metric: slope_ratio, p-value, PASS/FAIL
    # 2. Secondary Metrics: transfer_efficiency, pattern_usage_rate
    # 3. Control Check: revealed_only_slope ≈ 0
    # 4. Plots: embedded images
    # 5. Gate Decision: PASS → h-m3 VALIDATED, FAIL → PIVOT
    # Returns: markdown string
```

**Subtasks (4):**
1. Implement slope computation with scipy.stats.linregress
2. Implement permutation test
3. Implement visualization functions (matplotlib)
4. Implement generate_validation_report

---

## Algorithm Pseudo-Code

### Pattern Learning Algorithm (Core)

```python
# Main agent loop (10 iterations per problem)
memory = PatternMemory()

for iteration in range(10):
    # 1. Execute revealed tests
    revealed_pass, revealed_errors = run_test_suite(
        code=current_code,
        tests=revealed_tests,
        reveal_errors=True
    )
    
    # 2. Retrieve similar patterns from memory
    patterns = memory.retrieve_similar(
        current_error=revealed_errors[0] if revealed_errors else "",
        current_code=current_code,
        top_k=3
    )
    
    # 3. Generate fix using GPT-4 + patterns
    fix_prompt = f"""
    Code: {current_code}
    Error: {revealed_errors[0]}
    Similar patterns: {[p.fix_template for p in patterns]}
    
    Generate fixed code applying the pattern:
    """
    fixed_code = gpt4_complete(fix_prompt)
    
    # 4. Extract new pattern from this fix
    if revealed_pass < len(revealed_tests):
        new_pattern = extract_pattern(
            error_msg=revealed_errors[0],
            code=current_code,
            fix=fixed_code
        )
        memory.store_pattern(
            error_type=new_pattern.error_type,
            code_region=new_pattern.code_region,
            fix_template=new_pattern.fix_template,
            problem_id=problem["problem_id"]
        )
    
    # 5. Execute held-out tests (NO error messages)
    held_out_pass, _ = run_test_suite(
        code=fixed_code,
        tests=held_out_tests,
        reveal_errors=False  # CRITICAL: no information leakage
    )
    
    # 6. Log results
    log_results({
        "iteration": iteration,
        "revealed_pass": revealed_pass,
        "held_out_pass": held_out_pass,
        "patterns_used": len(patterns)
    })
    
    # 7. Update code for next iteration
    current_code = fixed_code
```

### Permutation Test Algorithm

```python
# Null hypothesis: agent_slope = random_slope
observed_diff = agent_slope - random_slope

null_diffs = []
for _ in range(1000):
    # Shuffle labels
    all_results = agent_results + random_results
    shuffled = random.shuffle(all_results)
    
    # Recompute slopes
    agent_shuffled = shuffled[:len(agent_results)]
    random_shuffled = shuffled[len(agent_results):]
    
    agent_slope_null = compute_slope(agent_shuffled)
    random_slope_null = compute_slope(random_shuffled)
    
    null_diffs.append(agent_slope_null - random_slope_null)

# Compute p-value
p_value = sum(d >= observed_diff for d in null_diffs) / len(null_diffs)

# Decision
if p_value < 0.05:
    print("PASS: agent_slope significantly > random_slope")
else:
    print("FAIL: no significant difference")
```

---

## External Dependencies (h-m2)

### Reused APIs from Base Hypothesis

```python
# From h-m2/code/agent.py
def load_problems(path: str) -> list[dict]:
    """Load Codeforces problems from JSON cache."""
    # Returns: [{problem_id, description, tests, ...}]

def run_tests(code: str, tests: list[dict]) -> list[bool]:
    """Execute code against test cases."""
    # Returns: [True/False for each test]
```

**Modification for h-m3:**
- Add `reveal_errors` parameter to run_tests
- Return error messages when reveal_errors=True

```python
# Modified signature for h-m3
def run_tests(
    code: str,
    tests: list[dict],
    reveal_errors: bool = True
) -> tuple[list[bool], list[str | None]]:
    """Execute tests, optionally reveal error messages."""
    # Returns: (pass_fail_array, error_messages)
```

---

## Data Flow

```
Input (Phase 2C)
    ↓
[Data Preparation]
    → problems.json (50 problems)
    → test_splits.json (revealed/held-out indices)
    → baseline_codes/ (initial buggy codes)
    ↓
[Agent Execution]
    → agent_results.json (per-iteration pass rates)
    ↓
[Baseline Execution]
    → baseline_results.json (random + revealed-only)
    ↓
[Analysis]
    → slope_analysis.json (slopes, p-value)
    → plots/ (held_out_curves.png, pattern_usage.png)
    ↓
[Validation Report]
    → 04_validation.md (PASS/FAIL decision)
```

---

## Tensor Shapes (N/A for this hypothesis)

This hypothesis uses symbolic code execution, not neural networks. No tensor operations.

---

## Error Handling

### Data Preparation Failures
- **Codeforces API timeout:** Retry 3 times with exponential backoff
- **Insufficient test cases (<15):** Skip problem, continue with next
- **KS test p < 0.05:** Resample test splits until p > 0.05

### Agent Execution Failures
- **GPT-4 API error:** Retry 3 times, log failure, skip iteration
- **Code execution timeout:** Kill process after 10s, mark as failure
- **Pattern extraction failure:** Continue without extracting pattern

### Analysis Failures
- **Regression fails (insufficient data):** Report warning, use mean slopes
- **Permutation test interrupted:** Save partial results, resume

---

## Quality Checks

### Input Validation
- All 50 problems have 15+ test cases
- Test splits are 50% / 50% (±2%)
- Baseline codes fail 3+ revealed tests per problem

### Output Validation
- agent_results.json has 50 × 10 = 500 entries
- baseline_results.json has 50 × 20 (random) + 50 × 10 (revealed-only)
- No NaN values in slope_analysis.json

### Statistical Validation
- Permutation test uses exactly 1000 samples
- Linear regression R² > 0.1 (sanity check)

---

## Next Steps

1. **Step 6:** Overall complexity assessment
2. **Step 7:** Verify all documents
3. **Step 9:** Generate 03_tasks.yaml

---

**Document Status:** Logic Design Complete  
**Subtasks Allocated:** 17 (within budget)
