# Logic: h-e1 (EXISTENCE PoC)

**Hypothesis:** h-e1 — Formal Repair Tool Operationality
**Date:** 2026-05-09
**Type:** EXISTENCE (PoC)

Applied: Python code generation evaluation pipeline
Applied: Grammar-constrained decoding LogitsProcessor pattern
Applied: Z3 LIA constraint encoding with timeout pattern
Applied: mypy.api.run structured feedback pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Data Shapes

| Name | Type | Note |
|------|------|------|
| pool | `Dict[str, List[str]]` | 164 task_ids × 20 completions |
| input_ids | `[1, seq_len]` | Tokenized prompt |
| logits | `[1, vocab_size]` | SynCode masks invalid tokens to -inf |
| eligibility | `Dict[str, bool]` | 164 boolean entries |
| mypy_results | `Dict[str, Dict]` | {task_id: {stdout, stderr, exit_code, parsed_errors}} |

---

## E-2: Baseline Pool Generation [Complexity: 14, Budget: 3 subtasks]

**Applied**: Python code generation evaluation pipeline

### API Signatures

```python
# code/baseline_generator.py
from typing import Dict, List
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class BaselineGenerator:
    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        temperature: float = 0.8,
        max_new_tokens: int = 256,
        n_samples: int = 20,
    ) -> None:
        """Initialize; model loaded lazily via load_model()."""
        ...

    def load_model(self) -> None:
        """Load CodeLlama-7B with device_map='auto'. Sets self.model, self.tokenizer."""
        ...

    def _generate_single(self, prompt: str, seed: int) -> str:
        """Generate one completion with fixed seed. Returns decoded new tokens only."""
        # torch.manual_seed(seed); transformers.set_seed(seed)
        # input_ids: [1, prompt_len]
        # output_ids: [1, prompt_len + new_tokens]
        # return decode(output_ids[0, prompt_len:])
        ...

    def generate_pool(
        self,
        problems: Dict[str, dict],  # {task_id: {prompt, ...}}
        seeds: List[int],           # [0..19]
        output_path: str,
    ) -> Dict[str, List[str]]:      # {task_id: [completion × 20]}
        """Generate N=20 completions per problem; serialize to JSONL."""
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Model loading | `load_model()` via AutoModelForCausalLM + AutoTokenizer, device_map="auto" |
| L-2-2 | Deterministic sampling loop | `_generate_single()` with torch.manual_seed + transformers.set_seed per call |
| L-2-3 | Completion extraction + JSONL | Decode new tokens only; write `{task_id, completion, seed}` JSONL lines |

---

## E-3: SynCode Pool Generation [Complexity: 16, Budget: 3 subtasks]

**Applied**: Grammar-constrained decoding LogitsProcessor pattern

### API Signatures

```python
# code/syncode_generator.py
from typing import Dict, List, Tuple
from syncode import SynCode
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class SyncodeGenerator:
    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        grammar: str = "python",
        mode: str = "grammar_mask",
        temperature: float = 0.8,
        max_new_tokens: int = 256,
        n_samples: int = 20,
    ) -> None:
        """Initialize; syn_model built via load_model()."""
        ...

    def load_model(self) -> None:
        """Load base model and wrap with SynCode. Sets self.syn_model, self.tokenizer."""
        # base_model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
        # tokenizer = AutoTokenizer.from_pretrained(model_name)
        # self.syn_model = SynCode(model=base_model, grammar="python",
        #                          tokenizer=tokenizer, mode="grammar_mask")
        ...

    def _generate_single_constrained(
        self, prompt: str, seed: int
    ) -> Tuple[str, int]:
        """Generate one grammar-constrained completion.
        Returns (completion_str, filtered_token_count)."""
        # torch.manual_seed(seed); transformers.set_seed(seed)
        # input_ids: [1, prompt_len]
        # output_ids = syn_model.generate(input_ids, ...)  logits masked: [1, vocab_size]
        # filtered_count = getattr(syn_model.grammar_decoder, "filtered_count", 0)
        # return decode(output_ids[0, prompt_len:]), filtered_count
        ...

    def generate_pool(
        self,
        problems: Dict[str, dict],
        seeds: List[int],           # [0..19]
        output_path: str,
    ) -> Dict[str, List[str]]:      # {task_id: [completion × 20]}
        """Grammar-constrained pool; JSONL includes filtered_token_count per sample."""
        ...

    def verify_constraint_active(
        self,
        pool: Dict[str, List[str]],
        filtered_counts: Dict[str, List[int]],  # {task_id: [count × 20]}
    ) -> bool:
        """Return True if filtered_count > 0 for >= 50% of problems."""
        # active = sum(1 for counts in filtered_counts.values() if any(c > 0 for c in counts))
        # return (active / len(filtered_counts)) >= 0.50
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | SynCode init + constraint verify | `load_model()` wraps base model; `verify_constraint_active()` asserts >= 50% active |
| L-3-2 | Constrained generation loop | `_generate_single_constrained()` with seed control + filtered_count capture |
| L-3-3 | JSONL serialization with metadata | Write `{task_id, completion, seed, filtered_token_count}` per JSONL line |

---

## E-4: Z3 Eligibility Checking [Complexity: 12, Budget: 1 subtask]

**Applied**: Z3 LIA constraint encoding with timeout pattern

### API Signatures

```python
# code/z3_eligibility.py
import re, ast
from typing import Dict, List, Tuple
import z3

class Z3EligibilityChecker:
    def __init__(self, timeout_ms: int = 2000) -> None:
        """Initialize with SMT solver timeout."""
        self.timeout_ms = timeout_ms

    def extract_postconditions(self, problem: dict) -> List[str]:
        """Extract assert expressions from prompt docstring.
        Returns list of expression strings (e.g. ["result > 0", "result == a + b"])."""
        # regex: re.findall(r'assert\s+(.+)', docstring_text)
        ...

    def _build_lia_formula(
        self,
        assert_exprs: List[str],
        var_names: List[str],
    ) -> Tuple[bool, object]:
        """Walk AST; accept BinOp(+,-,*), Compare, int Constant, Name only.
        Returns (True, z3_formula) or (False, None) if non-LIA ops found."""
        ...

    def check_problem(self, problem: dict) -> Tuple[bool, str]:
        """Check Z3 eligibility for one problem.
        Returns (is_eligible, reason); reason in:
        'lia_encodable' | 'no_assertions' | 'non_lia_ops' | 'z3_timeout' | 'parse_error'."""
        # postconds = extract_postconditions(problem)
        # if not postconds: return (False, "no_assertions")
        # ok, formula = _build_lia_formula(postconds, param_names)
        # solver = z3.Solver(); solver.set("timeout", self.timeout_ms)
        # solver.add(formula); result = solver.check()
        # if result == z3.unknown: return (False, "z3_timeout")
        # return (True, "lia_encodable")
        ...

    def check_all(
        self,
        problems: Dict[str, dict],
        output_path: str,
    ) -> Dict[str, bool]:           # {task_id: is_eligible}
        """Run check_problem on all problems; serialize JSON to output_path."""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | LIA extraction + Z3 check | `extract_postconditions()` regex scan; `_build_lia_formula()` AST LIA whitelist; `check_problem()` Z3 solver with timeout; `check_all()` batch + serialize |

---

## Supporting Modules (Included, No Subtask Budget)

### DataLoader

```python
# code/data_loader.py
from typing import Dict, Any
from evalplus.data import get_human_eval_plus, get_mbpp_plus

def load_humaneval_plus() -> Dict[str, Dict[str, Any]]:
    """Returns 164 HumanEval+ problem dicts keyed by task_id."""
    ...

def load_mbpp_plus() -> Dict[str, Dict[str, Any]]:
    """Returns 374 MBPP+ problem dicts keyed by task_id."""
    ...

def validate_datasets(humaneval: dict, mbpp: dict) -> bool:
    """Assert len==164 and len==374; raise ValueError on mismatch."""
    ...
```

### MypyChecker

```python
# code/mypy_checker.py
import mypy.api, tempfile, os, re
from typing import Dict, List, Tuple, Any

class MypyChecker:
    def check_code(self, code: str) -> Tuple[str, str, int]:
        """Write to temp file, run mypy.api.run(). Returns (stdout, stderr, exit_code)."""
        ...

    def parse_output(self, stdout: str) -> List[dict]:
        """Parse mypy stdout. Each entry: {line, col, error_code, message}."""
        # pattern: r':(\d+):(\d+): \w+: (.+?)(?:\s+\[(.+?)\])?$'
        ...

    def check_pool(
        self,
        pool: Dict[str, List[str]],
        output_path: str,
        sample_size: int = 50,
    ) -> Dict[str, Any]:
        """Run mypy on first completion of sample_size problems.
        Returns {task_id: {stdout, stderr, exit_code, parsed_errors}}."""
        ...
```

### MetricsEvaluator

```python
# code/metrics.py
import ast as ast_module
from typing import Dict, List, Any

class MetricsEvaluator:
    def compute_ast_failure_rate(self, pool: Dict[str, List[str]]) -> float:
        """Fraction of all completions failing ast.parse()."""
        ...

    def compute_delta_ast(
        self,
        baseline_pool: Dict[str, List[str]],
        syncode_pool: Dict[str, List[str]],
    ) -> float:
        """delta_ast = baseline_fail_rate - syncode_fail_rate. Gate: > 0."""
        ...

    def evaluate_gate(
        self,
        delta_ast: float,
        z3_rate: float,
        mypy_rate: float,
        output_path: str,
    ) -> Dict[str, Any]:
        """Return {delta_ast, z3_eligibility_rate, mypy_structured_rate, gate_pass}.
        gate_pass = delta_ast > 0 AND z3_rate >= 0.15 AND mypy_rate >= 0.90."""
        ...
```

---

## Subtasks Summary

| ID | Epic | Description |
|----|------|-------------|
| L-2-1 | E-2 | Model loading with device_map="auto" |
| L-2-2 | E-2 | Deterministic sampling loop with seed control |
| L-2-3 | E-2 | Completion extraction and JSONL serialization |
| L-3-1 | E-3 | SynCode init + verify_constraint_active() |
| L-3-2 | E-3 | Constrained generation + filtered_count capture |
| L-3-3 | E-3 | JSONL with filtered_token_count metadata |
| L-4-1 | E-4 | LIA extraction + Z3 eligibility check |

**Total: 7 / 7 subtasks**
