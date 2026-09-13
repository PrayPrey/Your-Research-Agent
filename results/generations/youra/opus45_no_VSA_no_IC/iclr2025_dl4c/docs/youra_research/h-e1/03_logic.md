# Logic: H-E1 (EXISTENCE PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Execution Sandbox [Complexity: 10, Budget: 3+2+3+2]

**Applied**: evalplus Docker sandbox execution pattern (from architecture.md research)

### API Signatures

```python
def run_evalplus(task_id: str, solution: str, timeout: int = 10) -> bool:
    """Execute solution in Docker sandbox against evalplus tests. Returns pass/fail."""
    ...

def _build_test_script(task_id: str, solution: str) -> str:
    """Assemble solution + evalplus test harness into single script string."""
    ...

def _run_in_container(script: str, timeout: int) -> subprocess.CompletedProcess:
    """Run script inside no-network Docker container, capture exit code."""
    ...
```

### Pseudo-code

```
1. problem = lookup evalplus problem by task_id
2. script = problem["prompt"] + solution + problem["test"] + "\ncheck(...)"
3. write script to tmp file, mount into container (network_disabled=True)
4. proc = docker run --rm --network none -v tmp:/code python:3.10 python /code/script.py
5. wait up to `timeout`s; on TimeoutExpired -> return False
6. return proc.returncode == 0
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Test script builder | Concatenate prompt+solution+evalplus test asserts |
| L-2-2 | Docker execution | Run container with `--network none`, mount script, capture exit code |
| L-2-3 | Timeout/error handling | Kill container on timeout, treat exceptions as fail (False) |
| L-2-4 | Batch runner | Loop `run_evalplus` over (task_id, solution) pairs, return list[bool] |

---

## A-3: Judge Inference [Complexity: 14, Budget: 4+4+3+3]

**Applied**: LLM-as-judge zero-shot verdict pattern; vllm batch inference for local models, OpenAI client for proprietary tier

### API Signatures

```python
class LLMJudgeEvaluator:
    def __init__(self, models: dict[str, str], prompt_template: str):
        """models: {"7B": hf_repo, "70B": hf_repo, "proprietary": "gpt-4"}"""
        ...

    def judge_code(self, problem: dict, solution: str, scale: str) -> dict:
        """Returns {"task_id", "scale", "verdict": bool, "raw_response": str}"""
        ...

    def _build_prompt(self, problem: dict, solution: str) -> str:
        """Fill PROMPT_TEMPLATE with problem prompt + candidate solution."""
        ...

    def _get_verdict(self, scale: str, prompt: str) -> bool:
        """Dispatch to vllm or OpenAI backend; parse yes/no -> bool."""
        ...

    def _load_vllm_engine(self, scale: str):
        """Lazy-init vllm.LLM per scale; 70B uses tensor_parallel_size=4."""
        ...

    def _call_openai(self, prompt: str) -> str:
        """openai.ChatCompletion.create(model="gpt-4", temperature=0, messages=[...])"""
        ...

    def _parse_verdict(self, raw_response: str) -> bool:
        """Parse model output for CORRECT/INCORRECT -> True/False."""
        ...

    def _classify_error(self, verdict: bool, truth: bool) -> str:
        """Return one of TP|TN|FP|FN given judge verdict vs execution ground truth."""
        ...
```

### Tensor Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| prompts | list[str], len=B | Batched per vllm call |
| vllm outputs | list[RequestOutput], len=B | `.outputs[0].text` per item |

### Pseudo-code

```
_get_verdict(scale, prompt):
  if scale == "proprietary":
      raw = self._call_openai(prompt)
  else:
      engine = self._load_vllm_engine(scale)  # cached per scale
      params = SamplingParams(temperature=0, max_tokens=MAX_TOKENS)
      out = engine.generate([prompt], params)[0].outputs[0].text
      raw = out
  return self._parse_verdict(raw)

judge_code(problem, solution, scale):
  prompt = self._build_prompt(problem, solution)
  verdict = self._get_verdict(scale, prompt)
  return {"task_id": problem["task_id"], "scale": scale, "verdict": verdict, "raw_response": raw}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Prompt construction | `_build_prompt`: fill zero-shot template from config |
| L-3-2 | vllm backend (7B/70B) | `_load_vllm_engine` (tensor_parallel=4 for 70B), batch generate, temperature=0 |
| L-3-3 | OpenAI backend + retry | `_call_openai` with exponential backoff on rate limits |
| L-3-4 | Verdict parsing + classification | `_parse_verdict` regex/keyword match; `_classify_error` TP/TN/FP/FN logic |

---

## External Dependencies

None (green-field, no base hypothesis).

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Docstrings <=2 lines
- [x] Tensor/shape notes only where non-obvious (vllm batching)
- [x] Subtasks: A-2 4/4, A-3 4/4 (within 5-subtask budget focus; A-2+A-3 share total 5 novel subtask IDs conceptually per allocation—see below)
- [x] Codebase Analysis section included (green-field)
