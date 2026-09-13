# Logic: H-E1 (EVAF Existence PoC)

**Type**: EXISTENCE (PoC) — minimal APIs only

**Applied**: RLTF-style subprocess+timeout unit test harness
**Applied**: HumanEval standard eval protocol (bigcode-evaluation-harness, 3.0s/test timeout)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing codebase, no base hypothesis
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: BaselineModel [Complexity: 9, Budget: 9]

**Applied**: HF seq2seq generate() wrapper (standard PyTorch/transformers)

### API Signatures

```python
class BaselineModel:
    def __init__(self, model_id: str = "Salesforce/codet5-large", device: str = "cuda", seed: int = 42):
        """Load CodeT5 tokenizer+model, set deterministic seed."""
        ...

    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        """Greedy decode. prompt: str -> code: str"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, T] | Tokenized prompt |
| output_ids | [1, T_out] | Generated token ids |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Model load | `AutoModelForSeq2SeqLM.from_pretrained`, `torch.manual_seed(seed)` |
| L-3-2 | generate() | `model.generate(input_ids, max_new_tokens, do_sample=False)` |
| L-3-3 | Batch driver | `generate_all(problems: list[dict]) -> list[dict]` -> adds `{"generated_code": str}` per item |
| L-3-4 | Failure filter | `filter_failing(problems: list[dict]) -> list[dict]`, runs `run_unit_tests` from gating.py, keeps `all_passed=False` |

---

## A-4: FeedbackModel [Complexity: 9, Budget: 9]

**Applied**: HF causal LM chat-template generate() (standard PyTorch/transformers)

### API Signatures

```python
class FeedbackModel:
    def __init__(self, model_id: str = "codellama/CodeLlama-7b-Instruct-hf",
                 temperature: float = 0.2, max_tokens: int = 512, device: str = "cuda"):
        """Load CodeLlama in float16."""
        ...

    def critique(self, problem: dict, failing_code: str) -> str:
        """problem: {task_id, prompt, entry_point, test}. Returns raw model response (may contain ```python fence)."""
        ...
```

### Pseudo-code

```
1. instruction = build_prompt(problem["prompt"], failing_code)  # template with docstring + failing code
2. inputs = tokenizer(instruction, return_tensors="pt")
3. out = model.generate(**inputs, temperature=0.2, do_sample=True, max_new_tokens=512)
4. return tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Model load | `AutoModelForCausalLM.from_pretrained(..., torch_dtype=torch.float16)` |
| L-4-2 | Prompt builder | `_build_prompt(problem: dict, failing_code: str) -> str`, CodeLlama instruct template |
| L-4-3 | critique() | temperature-sampled generate, decode new tokens only |
| L-4-4 | Determinism | seed `torch.manual_seed(SEED)` before each call for reproducibility (NFR-2) |

---

## A-5: Execution Gating [Complexity: 13, Budget: 13]

**Applied**: RLTF-style subprocess+timeout unit test harness

### API Signatures

```python
def extract_code_from_response(response: str) -> str | None:
    """Extract first ```python ...``` fenced block. None if no fence found."""
    ...

def run_unit_tests(code: str, test_code: str, entry_point: str, timeout: float = 3.0) -> dict:
    """Run code+test_code in subprocess. -> {"all_passed": bool, "error": str | None}"""
    ...

def evaf_gate(problem: dict, failing_code: str, feedback_model: "FeedbackModel") -> dict:
    """Full EVAF step: critique -> extract -> test -> decide.
    -> {"accepted": bool, "suggestion": str|None, "has_code_suggestion": bool, "rejection_reason": str|None}
    """
    ...
```

### Pseudo-code (complex: subprocess sandboxing + gating decision)

```
run_unit_tests(code, test_code, entry_point, timeout):
    script = code + "\n" + test_code + f"\ncheck({entry_point})\n"
    write script to temp file
    proc = subprocess.run(["python", tmp_path], timeout=timeout,
                           capture_output=True, text=True,
                           env=RESTRICTED_ENV)  # no network vars, cwd=tmp dir
    if proc.returncode == 0: return {"all_passed": True, "error": None}
    else: return {"all_passed": False, "error": proc.stderr[-2000:] or "timeout"}

evaf_gate(problem, failing_code, feedback_model):
    response = feedback_model.critique(problem, failing_code)
    code = extract_code_from_response(response)
    if code is None:
        return {"accepted": False, "suggestion": response, "has_code_suggestion": False,
                "rejection_reason": "no_code_block"}
    result = run_unit_tests(code, problem["test"], problem["entry_point"])
    if result["all_passed"]:
        return {"accepted": True, "suggestion": code, "has_code_suggestion": True,
                "rejection_reason": None}
    return {"accepted": False, "suggestion": code, "has_code_suggestion": True,
            "rejection_reason": classify_error(result["error"])}  # "test_failure" | "syntax_error" | "timeout" | "runtime_error"
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Code extraction | regex ```` ```python\n(.*?)``` ```` fenced block match |
| L-5-2 | Subprocess sandbox | `subprocess.run` w/ timeout, temp dir cwd, restricted env (no network — ponytail: timeout only, add seccomp/container if needed) |
| L-5-3 | run_unit_tests() | build script, execute, parse returncode/stderr |
| L-5-4 | Error classifier | `classify_error(stderr: str) -> str`, maps stderr patterns to rejection categories |
| L-5-5 | evaf_gate() | wire critique -> extract -> test -> decision dict |

---

## A-6: EVAF Pipeline Integration [Complexity: 10, Budget: 10]

**Applied**: Standard PyTorch inference orchestration

### API Signatures

```python
def run_pipeline(problems: list[dict], baseline: "BaselineModel",
                  feedback: "FeedbackModel") -> list[dict]:
    """Full pipeline: generate -> filter failing -> gate each. -> list of evaf_gate() result dicts + task_id."""
    ...

def save_results(results: list[dict], metrics: dict, out_dir: str) -> None:
    """Write results.json and metrics.json to out_dir."""
    ...
```

### Pseudo-code

```
run_pipeline(problems, baseline, feedback):
    for p in problems: p["generated_code"] = baseline.generate(p["prompt"])
    failing = filter_failing(problems)          # from A-3
    results = []
    for p in tqdm(failing):
        r = evaf_gate(p, p["generated_code"], feedback)   # from A-5
        r["task_id"] = p["task_id"]
        results.append(r)
    return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | run_pipeline() | wire A-2 (data) -> A-3 (baseline) -> A-5 (gate) |
| L-6-2 | Progress logging | `tqdm` wrapper + timestamped log lines (NFR-2) |
| L-6-3 | save_results() | `json.dump` results list + metrics dict to `{out_dir}/results.json`, `{out_dir}/metrics.json` |
| L-6-4 | main() driver | `train.py:main()` calls load -> run_pipeline -> compute_metrics -> plots -> save_results |

---

## Metrics & Gating Support (Low complexity, reference only)

```python
def compute_metrics(results: list[dict]) -> dict:
    """-> {"accept_rate": float, "coverage": float, "rejection_breakdown": Counter}"""
    ...
```

| Field | Formula |
|-------|---------|
| accept_rate | sum(r["accepted"]) / len(results) |
| coverage | sum(r["has_code_suggestion"]) / len(results) |
| rejection_breakdown | `Counter(r["rejection_reason"] for r in results if not r["accepted"])` |

---

## External Dependencies

None — green-field, no base hypothesis code to interop with.
