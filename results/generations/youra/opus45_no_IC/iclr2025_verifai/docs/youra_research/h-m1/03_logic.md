# Logic: H-M1 — Grammar-Constrained Decoding

**Tier**: FULL | **Type**: MECHANISM

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Baseline Generator [Complexity: 10, Budget: 4]

**Applied**: HuggingFace AutoModelForCausalLM standard generate() pattern

### API Signatures

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class BaselineGenerator:
    def __init__(self, model_id: str, device: str = "cuda", seed: int = 1):
        """Load CodeLlama-7B in bfloat16 with device_map='auto'."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self.model.eval()
        self.seed = seed

    def generate(
        self,
        prompt: str,
        num_samples: int = 10,
        temperature: float = 0.2,
        max_new_tokens: int = 512,
    ) -> list[str]:
        """Unconstrained sampling. Returns num_samples raw code completions."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, T] | tokenized prompt |
| output_ids | [num_samples, T+max_new_tokens] | batched via num_return_sequences |

### Pseudo-code

```
1. set_seed(self.seed)  # torch.manual_seed
2. inputs = tokenizer(prompt, return_tensors="pt").to(device)  # [1, T]
3. try:
     out = model.generate(
         **inputs,
         do_sample=True,
         temperature=temperature,
         max_new_tokens=max_new_tokens,
         num_return_sequences=num_samples,
         pad_token_id=tokenizer.eos_token_id,
     )  # [num_samples, T+max_new_tokens]
4. except torch.cuda.OutOfMemoryError:
     fallback: loop num_samples times with num_return_sequences=1, torch.cuda.empty_cache() between calls
5. completions = [tokenizer.decode(o[T:], skip_special_tokens=True) for o in out]
6. return completions
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | Model/tokenizer load | `from_pretrained` with bfloat16 + device_map="auto" |
| L-A3-2 | Seeded batched generate | `model.generate` with `num_return_sequences=num_samples` |
| L-A3-3 | OOM fallback loop | Per-sample generation loop if batch OOMs |
| L-A3-4 | Decode + strip prompt | Slice generated tokens past prompt length, decode |

---

## A-4: Constrained Generator (SynCode) [Complexity: 13, Budget: 4]

**Applied**: SynCode DFA mask store wrapper (grammar_strict mode, inference-time only)

### API Signatures

```python
from syncode import Syncode

class ConstrainedGenerator:
    def __init__(
        self,
        model_id: str,
        grammar: str = "python",
        device: str = "cuda",
        seed: int = 1,
    ):
        """Wrap model_id with SynCode grammar_strict Python CFG."""
        self.syn_llm = Syncode(
            model=model_id,
            mode="grammar_strict",
            grammar=grammar,
            quantize=True,
            device=device,
        )
        self.seed = seed

    def generate(
        self,
        prompt: str,
        num_samples: int = 10,
        temperature: float = 0.2,
        max_new_tokens: int = 512,
    ) -> list[str]:
        """Grammar-constrained sampling. Returns num_samples valid-syntax completions."""
        ...
```

### Pseudo-code

```
1. set_seed(self.seed)
2. completions = []
3. for i in range(num_samples):
     try:
       out = self.syn_llm.infer(
           prompt,
           temperature=temperature,
           max_new_tokens=max_new_tokens,
       )  # str (SynCode returns single completion per infer() call)
       completions.append(out)
     except Exception as e:  # SynCode grammar/DFA build failures
       log.warning(f"SynCode infer failed sample={i}: {e}")
       completions.append("")  # counted as syntax error downstream
4. return completions
```

**Note**: SynCode's `infer()` is single-sample; no native `num_return_sequences`. Loop required (unlike baseline batch generate). Set `torch.manual_seed(seed + i)` per-iteration for sample diversity under fixed base seed.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | Syncode init | Construct `Syncode(model=, mode="grammar_strict", grammar="python", quantize=True)` |
| L-A4-2 | Per-sample infer loop | Loop `num_samples`, call `syn_llm.infer(prompt, temperature=, max_new_tokens=)` |
| L-A4-3 | Per-sample seeding | `torch.manual_seed(seed + i)` before each infer call for sample diversity |
| L-A4-4 | Error handling | Catch SynCode/DFA exceptions per-sample, log + append "" (counts as syntax error) |

---

## Evaluation Functions (`evaluate.py`)

**Applied**: Standard PyTorch/stdlib — ast-based syntax check (no complexity budget needed, Low tier per architecture)

```python
import ast

def check_syntax(code: str) -> bool:
    """True if code parses as valid Python."""
    try:
        ast.parse(code)
        return True
    except (SyntaxError, ValueError):
        return False

def compilation_error_rate(samples: list[str]) -> float:
    """errors / len(samples)."""
    if not samples:
        return 0.0
    errors = sum(1 for s in samples if not check_syntax(s))
    return errors / len(samples)

def evaluate_condition(problem_results: dict[str, list[str]]) -> dict:
    """
    problem_results: {task_id: [sample_1, ..., sample_10]}
    Returns: {"error_rate": float, "n_errors": int, "n_total": int,
              "per_problem": {task_id: error_rate}}
    """
    ...
```

---

## Data Flow

```
HumanEval problems (164 dicts: task_id, prompt)
  -> BaselineGenerator.generate(prompt) x164        -> baseline_results: {task_id: [str x10]}
  -> ConstrainedGenerator.generate(prompt) x164      -> constrained_results: {task_id: [str x10]}
  -> evaluate_condition(baseline_results)            -> baseline_stats
  -> evaluate_condition(constrained_results)         -> constrained_stats
  -> gate: constrained_stats["error_rate"] < baseline_stats["error_rate"]
  -> visualize.plot_error_rate_comparison(...) + save_summary_table(...)
```

Both generators persist raw samples to `{output_dir}/{condition}_samples.json` keyed by task_id before evaluation (crash recovery — generation is the ~4hr bottleneck per NFR-2/NFR-3).

## External Dependencies

None — first mechanism hypothesis, no base hypothesis code to reuse (per architecture Codebase Analysis).
