# Logic: h-e2 (EXISTENCE PoC)

**Applied**: self-refine iterative feedback loop pattern (Init → Feedback → Iterate)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, Serena skipped
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-5: AI-Critic Refinement Loop [Complexity: 10, Budget: 2]

**Applied**: self-refine (Madaan et al.) iterative feedback loop pattern

### API Signatures

```python
# code/model.py
class CodeLLM:
    def __init__(self, model_id: str): ...

    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Single string in, single string out (raw completion)."""
        ...
```

```python
# code/refine.py
from model import CodeLLM

class AICriticRefinement:
    def __init__(self, generator: CodeLLM, k: int = 3):
        """k: number of refinement iterations."""
        self.generator = generator
        self.k = k

    def generate_initial(self, prompt: str) -> str:
        """Zero-shot code from problem prompt. Returns raw code string."""
        ...

    def generate_feedback(self, code: str, problem: str) -> str:
        """Same model as critic. Returns free-text critique string."""
        ...

    def refine_code(self, code: str, feedback: str, problem: str) -> str:
        """Combines code+feedback into new prompt, returns refined code string."""
        ...

    def run(self, problem: str) -> list[str]:
        """Returns k+1 code snapshots: [code_0 (init), code_1, ..., code_k]."""
        ...


class RandomFeedbackRefinement(AICriticRefinement):
    def generate_feedback(self, code: str, problem: str) -> str:
        """Overrides critic with random/nonsense text (control). Ignores code/problem args."""
        ...
```

### Tensor/String Shapes

| Variable | Type | Note |
|----------|------|------|
| prompt / problem | str | Problem statement + signature |
| code | str | Full function source (single candidate, no batching) |
| feedback | str | Free-text critique or random noise |
| run() return | list[str], len = k+1 | Index i = code after i refinement iterations |

### Pseudo-code

```
run(problem):
  code_0 = generate_initial(problem)
  snapshots = [code_0]
  code = code_0
  for i in 1..k:
      feedback = generate_feedback(code, problem)      # overridden in RandomFeedbackRefinement
      code = refine_code(code, feedback, problem)
      snapshots.append(code)
  return snapshots  # len == k+1
```

Prompt construction (both `generate_initial` and `refine_code` call `self.generator.generate(...)` with task-specific prompt strings; no new API beyond `CodeLLM.generate`):
- `generate_initial`: prompt = f"{problem}\n# Write the function."
- `generate_feedback`: prompt = f"Problem:\n{problem}\nCode:\n{code}\nCritique this code for correctness."
- `refine_code`: prompt = f"Problem:\n{problem}\nCode:\n{code}\nFeedback:\n{feedback}\nRewrite the corrected code."

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | AICriticRefinement core | Implement `__init__`, `generate_initial`, `generate_feedback`, `refine_code`, `run` in refine.py |
| L-5-2 | RandomFeedbackRefinement subclass | Override `generate_feedback` with random token/sentence sampler (seeded via config.SEED) |

---

## Notes

- `CodeLLM.generate` is the single point of contact with the model; both critic and generator calls route through it (per FR-3, same model for both roles).
- `run()` output feeds directly into `evaluate.run_tests` per snapshot to build the per-iteration pass@1 curve (A-7).
- Skipped: batching, async generation, prompt template abstraction — EXISTENCE scope only.
