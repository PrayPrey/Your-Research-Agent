# Logic: H-E1 (EXISTENCE / PoC)

**Applied**: Self-Debug iterative refinement (generate -> execute -> feedback -> refine)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing codebase to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Execution Sandbox [Complexity: 12, Budget: 6]

**Applied**: subprocess isolation with resource limits (stdlib `subprocess` + `resource`)

### API Signatures

```python
@dataclass
class ExecResult:
    passed: bool
    error_type: str | None      # e.g. "AssertionError", "TypeError", None if passed
    line_number: int | None     # parsed from traceback
    expected: str | None        # parsed from assertion diff, if available
    actual: str | None
    stdout: str
    stderr: str

def execute_code(
    code: str,
    tests: str,
    timeout: int = 10,
    mem_limit_mb: int = 512,
) -> ExecResult: ...

def _build_script(code: str, tests: str) -> str: ...
    # concatenates code + tests into single runnable .py source

def _set_limits(mem_limit_mb: int) -> None: ...
    # preexec_fn: resource.setrlimit(RLIMIT_AS, ...)

def _parse_traceback(stderr: str) -> tuple[str | None, int | None]: ...
    # -> (error_type, line_number)
```

### Pseudo-code

```
1. script = _build_script(code, tests)                 # combined source
2. write script to temp file
3. proc = subprocess.run(["python", tmpfile],
                          timeout=timeout,
                          preexec_fn=lambda: _set_limits(mem_limit_mb),
                          capture_output=True, text=True)
4. if proc.returncode == 0: return ExecResult(passed=True, ...)
5. else:
     error_type, line_number = _parse_traceback(proc.stderr)
     expected, actual = _extract_assertion_diff(proc.stderr)  # regex on AssertionError line
     return ExecResult(passed=False, error_type, line_number, expected, actual,
                        proc.stdout, proc.stderr)
6. on subprocess.TimeoutExpired: return ExecResult(passed=False, error_type="Timeout", ...)
```

### Subtasks [4/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Script builder | `_build_script`: merge code + test string, write to NamedTemporaryFile |
| L-2-2 | Resource limits | `_set_limits`: RLIMIT_AS via `resource` module, no network (no sandboxing needed beyond subprocess isolation) |
| L-2-3 | Subprocess runner | `execute_code`: run, capture stdout/stderr, handle timeout/non-zero exit |
| L-2-4 | Traceback parser | `_parse_traceback` + `_extract_assertion_diff`: regex-based extraction of error_type, line_number, expected/actual |

---

## A-4: Model Wrapper [Complexity: 10, Budget: 5]

**Applied**: HuggingFace `transformers` causal LM generate/refine wrapper

### API Signatures

```python
class ExecutionFeedbackRefinement:
    def __init__(
        self,
        model_id: str = "codellama/CodeLlama-7b-Instruct-hf",
        max_iterations: int = 3,
        temperature: float = 0.2,
        max_tokens: int = 512,
        top_p: float = 0.95,
    ) -> None: ...
        # loads tokenizer + model (AutoTokenizer, AutoModelForCausalLM), device_map="auto"

    def initial_generate(self, prompt: str) -> str:
        """First-attempt code generation. prompt: str -> code: str"""
        ...

    def refine_code(self, prompt: str, code: str, feedback: str) -> str:
        """Refinement given prior code + feedback. -> new code: str"""
        ...

    def generate_with_refinement(
        self,
        problem: dict,
        feedback_type: str,   # "execution" | "random"
    ) -> tuple[str, bool, int, list[str]]:
        """Runs full A-5 loop. -> (final_code, passed, iterations_used, feedback_log)"""
        ...

    def _build_refine_prompt(self, prompt: str, code: str, feedback: str) -> str: ...
        # instruct-format: f"{prompt}\n\nPrevious attempt:\n{code}\n\nFeedback:\n{feedback}\n\nFix the code:"

    def _extract_code(self, generated_text: str) -> str: ...
        # strip markdown fences ```python ... ```
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L] | tokenized prompt, batch=1 |
| generated_ids | [1, L+max_tokens] | model.generate output |

### Subtasks [1/6 used — remaining 1 shared with A-5 below]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Model init + generate | `__init__`, `initial_generate`, `refine_code`, `_extract_code`: load CodeLlama-7B-Instruct, HF `generate()` with temperature/top_p/max_tokens |

---

## A-5: Refinement Loop [Complexity: 10, Budget: 1 (remaining from 6-task pool)]

**Applied**: Self-Debug loop pattern — reuses `generate_with_refinement` signature from A-4

### Pseudo-code

```
generate_with_refinement(problem, feedback_type):
  code = initial_generate(problem["prompt"])
  feedback_log = []
  for it in range(1, max_iterations + 1):
      result = execute_code(code, problem["tests"], TIMEOUT_SEC, MEM_LIMIT_MB)
      if result.passed:
          return code, True, it, feedback_log
      feedback = (format_execution_feedback(result) if feedback_type == "execution"
                  else generate_random_feedback())
      feedback_log.append(feedback)
      code = refine_code(problem["prompt"], code, feedback)
  # final check after last refinement
  result = execute_code(code, problem["tests"], TIMEOUT_SEC, MEM_LIMIT_MB)
  return code, result.passed, max_iterations, feedback_log
```

### Subtasks [1/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Loop wiring | `generate_with_refinement`: wires sandbox.execute_code + feedback.format_* / generate_random_feedback + model refine call, early-stop on pass |

**Total subtasks used: 6/6** (L-2-1..4, L-4-1, L-5-1)

---

## Other Modules (Low Complexity — signatures only, per architecture doc)

```python
# data.py
def load_humaneval() -> list[dict]: ...
def load_mbpp() -> list[dict]: ...
def normalize_problem(raw: dict, source: str) -> dict: ...

# feedback.py
def format_execution_feedback(result: ExecResult) -> str: ...
def generate_random_feedback() -> str: ...

# train.py
def run_condition(problems: list[dict], refiner: ExecutionFeedbackRefinement, feedback_type: str) -> list[dict]: ...
def main() -> None: ...

# evaluate.py
def compute_pass_at_1(results: list[dict]) -> float: ...
def compute_pass_at_1_by_iteration(results: list[dict], k: int) -> dict[int, float]: ...
def verify_mechanism_activation(result_exec: dict, result_random: dict) -> bool: ...
def plot_gate_comparison(pass_exec: float, pass_random: float, out_path: str) -> None: ...
def plot_iteration_progression(results_exec: list[dict], out_path: str) -> None: ...
def plot_per_problem_heatmap(results_exec: list[dict], results_random: list[dict], out_path: str) -> None: ...
def main() -> None: ...
```

No pseudo-code needed — these are straightforward data/IO/plotting functions per PRD FR-1, FR-6, FR-7.
