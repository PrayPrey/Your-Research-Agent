# Logic: h-e1 (EXISTENCE / PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design (no `code/` directory, no base hypothesis)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Setup config + data loading [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch/HF datasets loading pattern

### API Signatures

```python
# config.py
DATASET_ID: str = "openai_humaneval"
MODEL_ID: str = "gpt-3.5-turbo"
TEMPERATURE: float = 0.0
PYLINT_ARGS: list[str] = ["--output-format=json", "--disable=C,R"]
PYLINT_TIMEOUT_SEC: int = 30
GATE_THRESHOLD: float = 0.30
OUTPUT_DIR: str = "results/"
FIGURES_DIR: str = "figures/"

# generate.py
def load_humaneval() -> list[dict]:
    """Load HumanEval via HF datasets. Returns list of problem dicts."""
    ...
```

### Tensor Shapes

Not applicable — this is text/dict data, no tensors.

Each dict: `{task_id: str, prompt: str, canonical_solution: str, test: str, entry_point: str}`, len == 164.

### Subtasks [0/0 used]

None — single-file, straightforward HF `load_dataset` call + field extraction.

---

## A-2: LLM generation [Complexity: 8, Budget: 8]

**Applied**: Standard OpenAI API client pattern (or HF `transformers.pipeline` for local model)

### API Signatures

```python
# generate.py
def generate_solution(prompt: str) -> str:
    """Call LLM (API or local) at TEMPERATURE=0.0. Returns raw generated code string."""
    ...
```

### Pseudo-code

```
1. If MODEL_ID starts with "gpt-": call openai.ChatCompletion with system+user prompt, temperature=0
2. Else: load HF causal LM once (module-level cache), generate with do_sample=False
3. Strip markdown code fences / non-code prefix if present
4. Return code string (no execution, no validation)
```

### Subtasks [0/0 used]

None — single function, two branches (API vs local), no further decomposition needed.

---

## A-3: Pylint analysis module [Complexity: 7, Budget: 7]

**Applied**: subprocess-based static-analysis-on-generated-code pattern (pylint JSON reporter, temp-file isolation)

### API Signatures

```python
# analyze.py
def run_pylint_analysis(code: str) -> dict:
    """Write code to temp file, run pylint subprocess, parse JSON, cleanup temp file.
    Returns {total_messages: int, actionable_count: int, messages: list[dict]}."""
    ...
```

### Tensor Shapes

Not applicable.

| Field | Type | Note |
|-------|------|------|
| messages[i] | dict | pylint JSON entry: `{type, message, symbol, ...}` |
| actionable_count | int | count where `type in ('error','warning')` |

### Pseudo-code

```
1. Write `code` to tempfile.NamedTemporaryFile(suffix=".py", delete=False)
2. subprocess.run(["pylint", tmp_path, *PYLINT_ARGS], capture_output=True, timeout=PYLINT_TIMEOUT_SEC)
3. json.loads(stdout) -> messages (empty list if no output / parse fails)
4. actionable_count = sum(1 for m in messages if m["type"] in ("error", "warning"))
5. finally: os.remove(tmp_path)
6. On subprocess.TimeoutExpired: return {total_messages: 0, actionable_count: 0, messages: []}
```

### Subtasks [0/0 used]

None — single function; try/finally handles cleanup, no separate module needed.

---

## A-4: Experiment loop (train.py) [Complexity: 6, Budget: 6]

**Applied**: Standard orchestration loop pattern

### API Signatures

```python
# train.py
def run_experiment() -> list[dict]:
    """Loop over 164 HumanEval problems: generate -> analyze. Saves raw results to disk."""
    ...

def main() -> None:
    """Entry point: run_experiment() then evaluate()."""
    ...
```

### Tensor Shapes

Not applicable.

Return type: `list[dict]` len 164, each `{task_id: str, actionable_count: int, messages: list[dict], warning_codes: list[str]}`

### Pseudo-code

```
1. problems = load_humaneval()
2. results = []
3. for p in problems:
     code = generate_solution(p["prompt"])
     analysis = run_pylint_analysis(code)
     warning_codes = [m["symbol"] for m in analysis["messages"]]
     results.append({task_id: p["task_id"], actionable_count: analysis["actionable_count"],
                      messages: analysis["messages"], warning_codes: warning_codes})
4. save results -> OUTPUT_DIR/generations.json, OUTPUT_DIR/pylint_results.json
5. return results
```

### Subtasks [0/0 used]

None — single sequential loop, no parallelism/retry logic required for PoC.

---

## A-5: Metrics computation [Complexity: 5, Budget: 5]

**Applied**: Standard aggregation/counting pattern

### API Signatures

```python
# evaluate.py
def compute_metrics(results: list[dict]) -> dict:
    """Compute warning_rate, avg_warnings, distributions, gate_passed."""
    ...
```

### Tensor Shapes

Not applicable.

Return dict: `{warning_rate: float, avg_warnings: float, warning_type_distribution: dict[str,int], top_10_warning_codes: list[tuple[str,int]], gate_passed: bool}`

### Pseudo-code

```
1. n = len(results)
2. warning_rate = sum(1 for r in results if r["actionable_count"] >= 1) / n
3. avg_warnings = sum(r["actionable_count"] for r in results) / n
4. warning_type_distribution = Counter(m["type"] for r in results for m in r["messages"])
5. top_10_warning_codes = Counter(code for r in results for code in r["warning_codes"]).most_common(10)
6. gate_passed = warning_rate >= GATE_THRESHOLD
```

### Subtasks [0/0 used]

None — single function using `collections.Counter`.

---

## A-6: Visualization [Complexity: 6, Budget: 6]

**Applied**: Standard matplotlib bar/hist/pie pattern

### API Signatures

```python
# evaluate.py
def plot_gate_metrics(metrics: dict) -> None:
    """Bar chart: target (0.30) vs actual warning_rate. Saves FIGURES_DIR/gate_metrics.png."""
    ...

def plot_warning_distribution(results: list[dict]) -> None:
    """Histogram of actionable_count per problem. Saves FIGURES_DIR/warning_distribution.png."""
    ...

def plot_warning_type_breakdown(metrics: dict) -> None:
    """Pie chart of warning_type_distribution. Saves FIGURES_DIR/warning_type_breakdown.png."""
    ...

def plot_top_warning_codes(metrics: dict) -> None:
    """Bar chart of top_10_warning_codes. Saves FIGURES_DIR/top_warning_codes.png."""
    ...

def evaluate() -> dict:
    """Load results, compute_metrics, generate all 4 plots, save FIGURES_DIR results/metrics.json."""
    ...
```

### Subtasks [0/0 used]

None — 4 independent plotting functions, each a direct matplotlib call, no shared complex state.

---

## A-7: End-to-end run + gate report [Complexity: 4, Budget: 4]

**Applied**: Standard main-guard entry point

### API Signatures

```python
# train.py (extends main())
if __name__ == "__main__":
    main()  # runs run_experiment() + evaluate(), prints gate PASS/FAIL, asserts wall time < 30 min
```

### Pseudo-code

```
1. t0 = time.time()
2. results = run_experiment()
3. metrics = evaluate()
4. elapsed = time.time() - t0
5. print(f"Gate: {'PASS' if metrics['gate_passed'] else 'FAIL'} (rate={metrics['warning_rate']:.2%}, elapsed={elapsed/60:.1f}min)")
```

### Subtasks [0/0 used]

None — timing wrapper around existing `main()`, no new module.

---

## External Dependencies

None — green-field, no base hypothesis code to reuse.
