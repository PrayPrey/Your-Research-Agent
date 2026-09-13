# Logic Design: h-e1 (EXISTENCE / PoC)

**Applied**: Structured error parsing pattern + regex-based extraction (from experiment brief / Archon KB "structured error format code repair")

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Error Parser [errors.py]

**Applied**: Regex-based compiler output parsing (line/type/message extraction) + context window slicing

### API Signatures

```python
from dataclasses import dataclass
from typing import List

@dataclass
class StructuredError:
    line_number: int
    error_type: str          # e.g. "SyntaxError", "TypeError", "NameError"
    error_message: str
    code_context: List[str]  # ["12: def foo():", ...] 3 lines before/after

def parse_compiler_output(raw_output: str, source_code: str) -> StructuredError:
    """Parse traceback/exception text into StructuredError."""
    ...
```

### Pseudo-code

```
1. line_number = int(regex r'line (\d+)') or 0
2. error_type = regex r'(\w+Error|\w+Exception)' or "UnknownError"
3. error_message = regex rf'{error_type}:\s*(.+?)(\n|$)' or raw_output.strip()
4. lines = source_code.split('\n')
5. start = max(0, line_number - 3); end = min(len(lines), line_number + 2)
6. code_context = [f"{i+1}: {lines[i]}" for i in range(start, end)]
7. return StructuredError(line_number, error_type, error_message, code_context)
```

### Edge Cases
- No line number found → `line_number=0`, `code_context=[]` (start=end=0 guard via `max(0, -3)=0`).
- `line_number` exceeds `len(lines)` → clamp via `min(len(lines), ...)`.
- Empty `raw_output` (e.g. timeout) → `error_type="UnknownError"`, `error_message=""`.
- Multi-line tracebacks with nested `raise ... from ...` → regex takes first match only (acceptable for PoC).

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | line_number regex | `re.search(r'line (\d+)', ...)` |
| L-1-2 | error_type regex | `re.search(r'(\w+Error|\w+Exception)', ...)` |
| L-1-3 | error_message extraction | regex on `{error_type}:\s*(.+?)` w/ fallback |
| L-1-4 | code_context slicing | 3-line window with clamping |

---

## A-2: Prompt Formatters [prompts.py]

**Applied**: Standard PyTorch/LLM prompt templating (f-strings)

### API Signatures

```python
from errors import StructuredError

def format_structured_prompt(error: StructuredError, original_code: str) -> str:
    """Build repair prompt from StructuredError. Returns full prompt string."""
    ...

def format_raw_prompt(raw_output: str, original_code: str) -> str:
    """Build repair prompt from raw compiler text (baseline)."""
    ...
```

### Pseudo-code

```
format_structured_prompt:
  context_str = '\n'.join(error.code_context)
  return f"""Fix the following Python code error.
## Error Information
- Line: {error.line_number}
- Type: {error.error_type}
- Message: {error.error_message}
## Code Context:
{context_str}
## Full Code:
{original_code}
Provide the corrected complete code:"""

format_raw_prompt:
  return f"""Fix the following Python code based on the error.
## Compiler Output:
{raw_output}
## Code:
{original_code}
Provide the corrected complete code:"""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | structured template | header + error fields |
| L-2-2 | context block | join code_context lines |
| L-2-3 | raw template | header + raw_output |
| L-2-4 | shared code block | embed original_code in both |

---

## A-3: Data Loading [evaluate.py: load helpers]

**Applied**: Standard HuggingFace `datasets.load_dataset`

### API Signatures

```python
from typing import List, Dict

def load_benchmark_problems(benchmark: str) -> List[Dict]:
    """benchmark: 'humaneval' | 'mbpp'. Returns list of {task_id, prompt, test, entry_point}."""
    ...
```

### Pseudo-code

```
1. if benchmark == "humaneval": ds = load_dataset("evalplus/humanevalplus")["test"]
2. elif benchmark == "mbpp": ds = load_dataset("evalplus/mbppplus")["test"]
3. else: raise ValueError(f"unknown benchmark: {benchmark}")
4. return [dict(row) for row in ds]
```

### Edge Cases
- Missing `entry_point`/`test` field in a row → skip row, log warning (do not crash whole run).
- Empty dataset (network failure) → raise `RuntimeError("no problems loaded")`.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | humaneval loader | `load_dataset("evalplus/humanevalplus")` |
| L-3-2 | mbpp loader | `load_dataset("evalplus/mbppplus")` |
| L-3-3 | row validation | skip malformed rows |

---

## A-4: Model Loading + Generation [models.py]

**Applied**: Standard HF `AutoModelForCausalLM` + OpenAI client, exponential backoff (NFR-3)

### API Signatures

```python
from typing import Tuple, Any
import torch

def load_hf_model(model_id: str) -> Tuple[Any, Any]:
    """Returns (model, tokenizer). float16, device_map='auto'."""
    ...

def generate_code(
    model_ref: Any,
    tokenizer: Any,
    prompt: str,
    is_openai: bool = False,
    max_new_tokens: int = 512,
    temperature: float = 0.0,
) -> str:
    """Generate completion. HF: greedy decode. OpenAI: chat.completions with backoff."""
    ...
```

### Pseudo-code

```
load_hf_model:
  tokenizer = AutoTokenizer.from_pretrained(model_id)
  model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
  return model, tokenizer

generate_code:
  if is_openai:
    for attempt in range(5):
      try:
        resp = openai.OpenAI().chat.completions.create(
          model="gpt-4", messages=[{"role":"user","content":prompt}],
          temperature=temperature, max_tokens=max_new_tokens)
        return resp.choices[0].message.content
      except RateLimitError:
        sleep(2 ** attempt); continue
    raise RuntimeError("GPT-4 call failed after 5 retries")
  else:
    inputs = tokenizer(prompt, return_tensors="pt").to(model_ref.device)  # [1, T]
    out = model_ref.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)  # [1, T+N]
    return tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| inputs.input_ids | [1, T] | batch_size=1 per NFR-2 |
| out | [1, T+N] | N = max_new_tokens |

### Edge Cases
- OpenAI rate limit → exponential backoff, max 5 retries, then raise.
- Model output includes markdown fences (```python ... ```) → strip in caller (repair_loop) not here.
- CUDA OOM on 34B → let it propagate (PoC scope, no retry logic required).

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | HF model load | AutoModel + AutoTokenizer, fp16, device_map=auto |
| L-4-2 | HF generate | greedy decode, slice new tokens |
| L-4-3 | OpenAI client call | chat.completions, temperature=0.0 |
| L-4-4 | backoff retry | exponential backoff on RateLimitError |

---

## A-5: Repair Loop [repair_loop.py]

**Applied**: Iterative execute-parse-repair loop, evalplus-style sandboxed exec with timeout

### API Signatures

```python
from typing import Tuple, Dict, Any

def execute_and_check(code: str, problem: Dict) -> Tuple[bool, str]:
    """Run code against problem['test'] with TIMEOUT_SEC. Returns (passed, raw_error)."""
    ...

def repair_problem(
    model_ref: Any,
    tokenizer: Any,
    problem: Dict,
    use_structured: bool,
    max_attempts: int = 5,
    is_openai: bool = False,
) -> Dict:
    """Returns {'passed': bool, 'attempts_used': int, 'error_types_seen': List[str]}."""
    ...
```

### Pseudo-code

```
execute_and_check:
  try:
    exec(code + problem['test'], globals={}, locals={}) within timeout TIMEOUT_SEC
    return (True, "")
  except TimeoutError:
    return (False, "TimeoutError: execution exceeded 3.0s")
  except Exception as e:
    return (False, traceback.format_exc())

repair_problem:
  1. code = generate_code(model_ref, tokenizer, initial_prompt(problem), is_openai)
  2. error_types_seen = []
  3. for attempt in range(1, max_attempts + 1):
       passed, raw_error = execute_and_check(code, problem)
       if passed: return {passed: True, attempts_used: attempt, error_types_seen}
       if use_structured:
         err = parse_compiler_output(raw_error, code)
         error_types_seen.append(err.error_type)
         prompt = format_structured_prompt(err, code)
       else:
         error_types_seen.append(extract_error_type_only(raw_error))  # for metrics parity
         prompt = format_raw_prompt(raw_error, code)
       code = generate_code(model_ref, tokenizer, prompt, is_openai)
  4. passed, _ = execute_and_check(code, problem)  # final attempt check
  5. return {passed, attempts_used: max_attempts, error_types_seen}
```

### Edge Cases
- Initial generation already passes → `attempts_used=0` (skip repair loop entirely; adjust step 3 to check before loop or treat attempt 0 as pre-check).
- Repeated identical error across attempts (model stuck) → no early stop required for PoC; loop runs full `max_attempts`.
- `execute_and_check` timeout → run in subprocess or use `signal.alarm`/`multiprocessing` with `TIMEOUT_SEC=3.0`; treat as failure with synthetic `TimeoutError` message.
- Malformed/empty model output (no code block) → treat as failing code, `execute_and_check` raises `SyntaxError`, captured normally.

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | sandboxed exec | run code+test in subprocess with timeout |
| L-5-2 | timeout handling | catch and format TimeoutError |
| L-5-3 | exception capture | `traceback.format_exc()` on failure |
| L-5-4 | initial generation | first code attempt from problem prompt |
| L-5-5 | pre-check pass | attempt=0 short-circuit if initial passes |
| L-5-6 | structured branch | parse_compiler_output + format_structured_prompt |
| L-5-7 | raw branch | format_raw_prompt directly |
| L-5-8 | attempt loop | up to max_attempts=5 iterations |
| L-5-9 | error_types_seen tracking | append per-attempt error_type |
| L-5-10 | result dict assembly | passed/attempts_used/error_types_seen |

---

## A-6: Evaluation Pipeline [evaluate.py]

**Applied**: evalplus-style pass@1 aggregation over repair_loop results

### API Signatures

```python
from typing import Dict, List

def run_benchmark(model_name: str, benchmark: str, use_structured: bool) -> Dict:
    """Runs repair_problem over all problems. Returns
    {'pass_at_1': float, 'repair_success_rate': float, 'avg_attempts': float,
     'error_breakdown': Dict[str, int]}."""
    ...

def aggregate_results(all_results: List[Dict]) -> Dict:
    """Combine per-(model,benchmark,format) dicts into results.json structure."""
    ...
```

### Pseudo-code

```
run_benchmark:
  1. problems = load_benchmark_problems(benchmark)
  2. model_ref, tokenizer = load_hf_model(model_name) if not openai else (None, None)
  3. results = [repair_problem(model_ref, tokenizer, p, use_structured, is_openai=(model_name=="gpt-4"))
                for p in problems]
  4. pass_at_1 = mean([r['passed'] for r in results])
  5. had_error = [r for r in results if r['attempts_used'] > 0 or not r['passed']]
  6. repair_success_rate = mean([r['passed'] for r in had_error]) if had_error else 0.0
  7. avg_attempts = mean([r['attempts_used'] for r in had_error]) if had_error else 0.0
  8. error_breakdown = Counter(flatten([r['error_types_seen'] for r in results]))
  9. return {pass_at_1, repair_success_rate, avg_attempts, error_breakdown}

aggregate_results:
  return {f"{model}|{benchmark}|{'structured' if s else 'raw'}": metrics for each combo}
```

### Edge Cases
- Zero problems with errors (all pass initially) → `repair_success_rate=0.0`, `avg_attempts=0.0` (guarded above).
- 34B model + GPT-4 sequential run may exceed time budget → PoC scope, no truncation logic; document as known limitation.

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | problem iteration | loop repair_problem over all problems |
| L-6-2 | pass@1 computation | mean of passed flags |
| L-6-3 | repair_success_rate | mean passed among had_error subset |
| L-6-4 | avg_attempts | mean attempts_used among had_error subset |
| L-6-5 | error_breakdown | Counter over error_types_seen |
| L-6-6 | HF vs OpenAI branch | conditional model loading |
| L-6-7 | aggregate keying | model|benchmark|format key scheme |
| L-6-8 | results dict merge | combine all run_benchmark outputs |
| L-6-9 | zero-division guards | had_error empty checks |

---

## A-7: Visualization [visualize.py]

**Applied**: Standard matplotlib bar/heatmap plotting

### API Signatures

```python
def plot_gate_comparison(results: Dict, out_path: str) -> None: ...       # REQUIRED
def plot_repair_success(results: Dict, out_path: str) -> None: ...
def plot_repair_iterations(results: Dict, out_path: str) -> None: ...
def plot_error_type_heatmap(results: Dict, out_path: str) -> None: ...
def plot_benchmark_comparison(results: Dict, out_path: str) -> None: ...
```

### Pseudo-code

```
plot_gate_comparison:
  1. models = [7b, 34b, gpt-4]; for each: bars = [pass_at_1(structured), pass_at_1(raw)]
  2. grouped bar chart, x=models, hue=format
  3. savefig(out_path)

plot_error_type_heatmap:
  1. rows=error_types, cols=(model,format), values=count from error_breakdown
  2. imshow / seaborn-free matplotlib pcolor
  3. savefig(out_path)
```

### Edge Cases
- Missing combo in `results` dict (e.g. run failed for one model) → skip bar/annotate "N/A", do not crash plotting.

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | gate comparison bar | required figure, pass@1 by model/format |
| L-7-2 | repair success bar | grouped bar |
| L-7-3 | iterations histogram | attempts_used distribution |
| L-7-4 | error heatmap | error_type x (model,format) matrix |
| L-7-5 | benchmark comparison | humaneval vs mbpp side-by-side |
| L-7-6 | missing-data guard | skip/annotate absent combos |

---

## A-8: Entrypoint [train.py]

**Applied**: Standard orchestration loop, deterministic seeding (NFR-1)

### API Signatures

```python
def main() -> None:
    """Loops MODELS x BENCHMARKS x {structured, raw}, writes results.json, generates figures."""
    ...
```

### Pseudo-code

```
main:
  1. set_seed(0); torch.manual_seed(0)
  2. all_results = {}
  3. for model_name in MODELS:
       for benchmark in BENCHMARKS:
         for use_structured in [True, False]:
           key = f"{model_name}|{benchmark}|{'structured' if use_structured else 'raw'}"
           all_results[key] = run_benchmark(model_name, benchmark, use_structured)
  4. json.dump(all_results, open("results.json", "w"), indent=2)
  5. plot_gate_comparison(all_results, "figures/gate_comparison.png")
  6. plot_repair_success(all_results, "figures/repair_success.png")
  7. plot_repair_iterations(all_results, "figures/repair_iterations.png")
  8. plot_error_type_heatmap(all_results, "figures/error_heatmap.png")
  9. plot_benchmark_comparison(all_results, "figures/benchmark_comparison.png")
  10. check PoC gate: count combos where structured_pass_at_1 > raw_pass_at_1; assert >= 4/6
```

### Edge Cases
- One model/benchmark combo raises (e.g. OOM on 34B) → catch per-combo, log, store `None`, continue loop; exclude from gate-check denominator but log as failure.
- `results.json` write failure (disk) → let it propagate (fail loud, PoC).

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | seed setup | fixed seeds per NFR-1 |
| L-8-2 | model x benchmark x format loop | 3x2x2 = 12 combos |
| L-8-3 | results.json write | json.dump |
| L-8-4 | figure generation calls | 5 plot functions |
| L-8-5 | gate check | count structured > raw combos |
| L-8-6 | per-combo error isolation | try/except around run_benchmark |
| L-8-7 | logging | print progress per combo |
| L-8-8 | assert PoC pass condition | >= 4 of 6 model/benchmark pairs |

---

## Config Reference [config.py]

```python
MODELS = ["codellama/CodeLlama-7b-Instruct-hf", "codellama/CodeLlama-34b-Instruct-hf", "gpt-4"]
BENCHMARKS = ["humaneval", "mbpp"]
MAX_REPAIR_ATTEMPTS = 5
TEMPERATURE = 0.0
MAX_NEW_TOKENS = 512
TIMEOUT_SEC = 3.0
```
