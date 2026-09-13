# Logic: H-C1 — Execution Feedback vs AI-Critic, Complexity Effect

Applied: pipeline-stage pattern (generate -> feedback -> refine -> evaluate -> compare)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: API signatures verified from base code (find_symbol/get_symbols_overview on `h-m1/code/`)
**Analyzed Path**: `docs/youra_research/h-m1/code/data_loader.py`, `sandbox_executor.py`, `config.py`
**Relevant Symbols**: `load_humaneval`, `load_mbpp`, `load_all_problems`, `SandboxExecutor.run`, `SandboxExecutor._build_script`, `ExecutionResult`, `Config`/`CFG`

**Discrepancy found vs H-M1 spec (03_logic.md)**: spec described a docker-based `SandboxExecutor` with `client.containers.run(...)`; actual code uses plain `subprocess.run` with `timeout=`, no docker dependency. `_extract_traceback` is single-underscore (private), not documented in spec's public API table. Copied files must be used as-is (subprocess version) — do not reintroduce docker.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-c1/code/base/data_loader.py (copied unmodified from h-m1/code/data_loader.py)
def load_humaneval() -> list[dict]:
    """Returns [{"id","prompt","code","tests","entry_point"}, ...] (164 items)."""
    ...

def load_mbpp() -> list[dict]:
    """Returns [{"id","prompt","code","tests","entry_point": None}, ...] (~500 items)."""
    ...

def load_all_problems() -> list[dict]:
    """load_humaneval() + load_mbpp()."""
    ...

# From: h-c1/code/base/sandbox_executor.py (copied unmodified from h-m1/code/sandbox_executor.py)
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    traceback: str
    timed_out: bool

class SandboxExecutor:
    def __init__(self, timeout_s: int = None, memory_mb: int = None):
        """Defaults pulled from CFG.timeout_s / CFG.memory_mb if None."""
        ...
    def run(self, code: str, tests: str) -> ExecutionResult:
        """subprocess.run([python, script], timeout=self.timeout_s). NOT docker."""
        ...
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, subprocess-based, not the docker version described in h-m1's own spec).

---

## A-2: ModelClient [Complexity: 10, Budget: 3+3+2+2]

**Applied**: HuggingFace `transformers` pipeline wrapper (standard PyTorch/HF pattern)

### API Signatures

```python
class ModelClient:
    def __init__(self, model_id: str = "codellama/CodeLlama-7b-Instruct-hf",
                 temperature: float = 0.2, max_new_tokens: int = 512, seed: int = 42):
        """Loads tokenizer+model once (fp16, device_map='auto'), sets seed."""
        ...

    def generate(self, prompt: str) -> str:
        """Single completion. prompt: str -> generated code str (stripped, extracted from ``` fences if present)."""
        ...
```

### Pseudo-code: generate

```
1. inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
2. out_ids = model.generate(**inputs, max_new_tokens=self.max_new_tokens,
                             temperature=self.temperature, do_sample=(temperature > 0))
3. text = tokenizer.decode(out_ids[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
4. code = extract_code_block(text)  # regex ```python\n(.*?)\n``` else raw text
5. return code
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | `__init__` model/tokenizer load | HF `from_pretrained`, fp16, device_map, set_seed |
| L-2-2 | `generate` core call | tokenize -> model.generate -> decode |
| L-2-3 | Code-block extraction | Regex fence stripping, fallback to raw text |
| L-2-4 | Init code generation loop | Call `generate()` per problem for HE+MBPP (591), retry on empty output |

---

## A-4/A-5: FeedbackMechanisms [Complexity: 8+6=14 combined, Budget: 2+2+2+2 / 2+1+2+1]

**Applied**: Standard PyTorch/text pattern — no KB pattern needed (pure string formatting)

### API Signatures

```python
from base.sandbox_executor import ExecutionResult
from model_client import ModelClient

def build_exec_feedback(exec_result: ExecutionResult) -> str:
    """Formats stderr/traceback into feedback string for refine prompt."""
    ...

def build_critic_feedback(client: ModelClient, code: str, problem: dict) -> str:
    """LLM critique from code+prompt only, no execution info. problem: {id,prompt,code,tests}."""
    ...
```

### Pseudo-code: build_exec_feedback

```
1. if exec_result.timed_out: return "Execution timed out."
2. if exec_result.exit_code == 0: return "All tests passed."
3. return f"Execution failed:\n{exec_result.traceback or exec_result.stderr}"
```

### Pseudo-code: build_critic_feedback

```
1. critic_prompt = CRITIC_PROMPT_TEMPLATE.format(problem=problem["prompt"], code=code)
   # template asks: "Review this code for correctness bugs. Do not execute it. List issues."
2. return client.generate(critic_prompt)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | `build_exec_feedback` | Format ExecutionResult (timeout/pass/fail branches) into string |
| L-4-2 | `CRITIC_PROMPT_TEMPLATE` | Fixed template, no execution info leaked |
| L-4-3 | `build_critic_feedback` | Fill template, call `client.generate` |
| L-4-4 | Feedback pipeline wiring | Call both per problem, store alongside initial code |

---

## A-6: Refiner [Complexity: 8, Budget: 2+2+2+2]

**Applied**: Self-Refine single-iteration refinement prompt pattern

### API Signatures

```python
REFINE_PROMPT_TEMPLATE: str = (
    "Problem:\n{prompt}\n\nCurrent code:\n{code}\n\nFeedback:\n{feedback}\n\n"
    "Provide corrected code only."
)

def refine_with_feedback(client: ModelClient, code: str, feedback: str, problem: dict) -> str:
    """Single-iteration refinement. Same template regardless of feedback source."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | `REFINE_PROMPT_TEMPLATE` | Fixed string template, 3 fill fields |
| L-6-2 | `refine_with_feedback` | Format template, call `client.generate`, extract code |
| L-6-3 | Apply to exec-feedback path | refine(initial_code, exec_feedback) per problem |
| L-6-4 | Apply to critic-feedback path | refine(initial_code, critic_feedback) per problem |

---

## A-7: Evaluator [Complexity: 10, Budget: 3+3+2+2]

**Applied**: pass@1 execution-based scoring (standard code-eval pattern)

### API Signatures

```python
from base.sandbox_executor import SandboxExecutor

def pass_at_1(executor: SandboxExecutor, code: str, tests: str) -> float:
    """1.0 if exit_code==0 and not timed_out, else 0.0."""
    ...

def compare_feedback_mechanisms(
    client: "ModelClient",
    executor: SandboxExecutor,
    problem: dict,
    initial_code: str,
) -> dict:
    # {"execution_pass": float, "critic_pass": float, "execution_advantage": float}
    ...
```

### Pseudo-code: compare_feedback_mechanisms

```
1. exec_result = executor.run(initial_code, problem["tests"])
2. exec_feedback = build_exec_feedback(exec_result)
3. critic_feedback = build_critic_feedback(client, initial_code, problem)
4. exec_refined = refine_with_feedback(client, initial_code, exec_feedback, problem)
5. critic_refined = refine_with_feedback(client, initial_code, critic_feedback, problem)
6. execution_pass = pass_at_1(executor, exec_refined, problem["tests"])
7. critic_pass = pass_at_1(executor, critic_refined, problem["tests"])
8. return {"execution_pass": execution_pass, "critic_pass": critic_pass,
           "execution_advantage": execution_pass - critic_pass}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | `pass_at_1` | Run executor, threshold exit_code/timed_out to 0/1 |
| L-7-2 | `compare_feedback_mechanisms` orchestration | Wire exec/critic feedback -> refine -> re-eval |
| L-7-3 | Full-dataset loop (HE) | Iterate 164 problems, collect per-problem dict results |
| L-7-4 | Full-dataset loop (MBPP) | Iterate ~500 problems, collect per-problem dict results |

---

## A-8: Metrics [Complexity: 6, Budget: 1+2+2+1]

**Applied**: Standard aggregation, no KB pattern needed

### API Signatures

```python
def compute_complexity_effect(humaneval_results: list[dict], mbpp_results: list[dict]) -> dict:
    # {"humaneval_exec_advantage", "mbpp_exec_advantage", "complexity_effect", "hypothesis_supported"}
    ...
```

### Pseudo-code

```
1. he_adv = mean(r["execution_advantage"] for r in humaneval_results)
2. mbpp_adv = mean(r["execution_advantage"] for r in mbpp_results)
3. complexity_effect = mbpp_adv - he_adv
4. hypothesis_supported = complexity_effect > 0
5. return {"humaneval_exec_advantage": he_adv, "mbpp_exec_advantage": mbpp_adv,
           "complexity_effect": complexity_effect, "hypothesis_supported": hypothesis_supported}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Mean advantage per benchmark | `mean()` over `execution_advantage` field |
| L-8-2 | `complexity_effect` calc | mbpp_adv - he_adv |
| L-8-3 | Gate check (`hypothesis_supported`) | Threshold > 0 per PRD FR-6/success criteria |
| L-8-4 | Result dict assembly + save | Serialize to JSON-compatible dict |

---

## A-9: Visualize [Complexity: 9, Budget: 2+2+2+3]

**Applied**: matplotlib bar/scatter (standard plotting, no KB pattern)

### API Signatures

```python
def plot_exec_advantage_bar(complexity_effect_result: dict, out_path: str) -> None: ...
def plot_pass_at_1_grouped(he_results: list[dict], mbpp_results: list[dict], out_path: str) -> None: ...
def plot_error_type_breakdown(results: list[dict], out_path: str) -> None: ...
def plot_complexity_scatter(results: list[dict], out_path: str) -> None: ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | `plot_exec_advantage_bar` | 2-bar chart: HE vs MBPP exec_advantage |
| L-9-2 | `plot_pass_at_1_grouped` | 4-bar grouped chart (2 benchmarks x 2 mechanisms) |
| L-9-3 | `plot_error_type_breakdown` | Stacked bar of traceback error types per benchmark |
| L-9-4 | `plot_complexity_scatter` | Scatter: problem length/complexity proxy vs execution_advantage |

---

## A-10: Pipeline [Complexity: 8, Budget: 2+3+1+2]

**Applied**: Standard PyTorch/text pattern — sequential orchestration script

### API Signatures

```python
def main() -> None:
    # load HE + MBPP -> generate initial code -> compare_feedback_mechanisms per problem
    # -> compute_complexity_effect -> save results/experiment_results.json -> generate figures
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-10-1 | Seed + config setup | `torch.manual_seed`, `random.seed` from `CFG.seed` |
| L-10-2 | Main orchestration loop | load data -> generate -> compare -> collect results (both benchmarks) |
| L-10-3 | Results JSON save | Write `results/experiment_results.json` |
| L-10-4 | Figure generation calls | Invoke all 4 `visualize.py` functions with saved results |

---

## Note on A-1, A-3 (Complexity ≤ 6, no dedicated logic section)

- **A-1** (Setup & copy base modules): file-copy + `config.py` per Architecture `Config` dataclass — no new API design needed, use spec as-is.
- **A-3** (Initial code generation): covered by `ModelClient.generate` (A-2) applied in a loop; no separate API.
