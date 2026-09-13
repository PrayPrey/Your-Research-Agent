# Logic Design: H-E1 — Runtime Error Prevalence in LLM-Generated Code

**Hypothesis Type**: EXISTENCE
**Date**: 2026-03-30

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Model Integration [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard PyTorch / HuggingFace transformers inference pattern

### API Signatures

```python
# code/model.py
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Optional
from config import ExperimentConfig

class CodeGenerator:
    def __init__(self, config: ExperimentConfig):
        """Initialize with config; model/tokenizer loaded lazily via load()."""
        self.config = config
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None

    def load(self) -> None:
        """Load tokenizer and model in float16 with device_map='auto'."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        self.model.eval()

    def generate(self, prompt: str) -> str:
        """Single inference. prompt: str -> extracted code str."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        # inputs["input_ids"]: [1, L]
        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
                do_sample=False,
            )
        # output_ids: [1, L+T]
        raw = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return self.extract_code(raw)

    def generate_batch(self, problems: list[dict]) -> list[str]:
        """Iterate problems sequentially, return list of code strings (len=N)."""
        return [self.generate(format_prompt(p)) for p in problems]

    def extract_code(self, raw_output: str) -> str:
        """Extract between [BEGIN]/[DONE] markers; fallback to full response."""
        if "[BEGIN]" in raw_output and "[DONE]" in raw_output:
            start = raw_output.index("[BEGIN]") + len("[BEGIN]")
            end = raw_output.index("[DONE]")
            return raw_output[start:end].strip()
        return raw_output.strip()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Model Load | `load()`: tokenizer + float16 model, device_map auto |
| L-3-2 | Generate + Extract | `generate()` + `extract_code()` + `generate_batch()` loop |

---

## A-4: Execution Engine [Complexity: 9, Budget: 2 subtasks]

**Applied**: subprocess-execution-pattern with TimeoutExpired handler

### API Signatures

```python
# code/executor.py
import subprocess
from enum import Enum
from typing import Optional

class ErrorCategory(Enum):
    PASS = "pass"
    RUNTIME_ERROR = "runtime_error"
    WRONG_OUTPUT = "wrong_output"
    SYNTAX_ERROR = "syntax_error"
    TIMEOUT = "timeout"

def execute_code(
    code: str,
    tests: list[str],
    timeout: int = 10,
) -> tuple[ErrorCategory, Optional[str]]:
    """Run code+tests in subprocess. Returns (category, stderr or None)."""
    full_code = code + "\n" + "\n".join(tests)
    try:
        result = subprocess.run(
            ["python", "-c", full_code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        category = categorize_stderr(result.returncode, result.stderr)
        stderr = result.stderr if category != ErrorCategory.PASS else None
        return category, stderr
    except subprocess.TimeoutExpired:
        return ErrorCategory.TIMEOUT, None

def categorize_stderr(returncode: int, stderr: str) -> ErrorCategory:
    """Map returncode + stderr content to ErrorCategory."""
    if returncode == 0:
        return ErrorCategory.PASS
    if "SyntaxError" in stderr:
        return ErrorCategory.SYNTAX_ERROR
    if "Traceback (most recent call last):" in stderr:
        return ErrorCategory.RUNTIME_ERROR
    return ErrorCategory.WRONG_OUTPUT
```

### Pseudo-code (categorization priority)

```
execute_code(code, tests, timeout):
    full_code = code + "\n" + join(tests)
    try:
        result = subprocess.run(["python", "-c", full_code], timeout=timeout)
        return categorize_stderr(result.returncode, result.stderr), stderr
    except TimeoutExpired:
        return TIMEOUT, None

categorize_stderr(rc, stderr):
    if rc == 0        -> PASS
    if "SyntaxError"  -> SYNTAX_ERROR   (check before Traceback)
    if "Traceback"    -> RUNTIME_ERROR
    else              -> WRONG_OUTPUT
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Subprocess Execution | `execute_code()`: run, capture output, timeout handling |
| L-4-2 | Error Categorization | `categorize_stderr()`: priority-ordered stderr pattern matching |

---

## Data Flow

```
ExperimentConfig
  -> load_mbpp_test()       : list[dict] (500 problems)
  -> format_prompt()        : str per problem
  -> CodeGenerator.generate(): str (extracted code)
  -> execute_code()         : (ErrorCategory, Optional[str])
  -> calculate_prevalence() : dict {prevalence, ci_lower, ci_upper, ...}
  -> check_gate()           : bool (ci_lower >= 0.30)
  -> save_results() + plots
```

---

## External Dependencies

None - green-field, all modules implemented from scratch.

**Key library calls:**
- `subprocess.run(["python", "-c", full_code], capture_output=True, text=True, timeout=timeout)`
- `AutoModelForCausalLM.from_pretrained(..., torch_dtype=torch.float16, device_map="auto")`
- `proportion_confint(n_runtime, n_failures, alpha=0.05, method='wilson')`
