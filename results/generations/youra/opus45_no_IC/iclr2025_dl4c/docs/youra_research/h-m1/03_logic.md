# Logic: H-M1 (Execution Trace → Token Classification)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing code — new API design, Serena skipped per rules.
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: ExecutionTraceCollector [Complexity: 9, Budget: 2+1+3+3]

**Applied**: stdlib sys.settrace line-event tracer (no external dep found in KB; standard pattern)

### API Signatures

```python
import sys
import signal
from typing import Callable, Optional

class TraceTimeoutError(Exception):
    """Raised when traced execution exceeds timeout."""

class ExecutionTraceCollector:
    def __init__(self):
        self._executed_lines: set[int] = set()
        self._target_filename: Optional[str] = None

    def trace_function(self, frame, event: str, arg) -> Optional[Callable]:
        """sys.settrace callback. Records 'line' events for target file."""
        ...

    def collect_trace(self, code_str: str, test_input: str, timeout: float = 5.0) -> set[int]:
        """Exec code_str + test_input under trace. Returns executed line numbers.
        Returns partial set on exception/timeout (never raises)."""
        ...
```

### Pseudo-code

```
collect_trace(code_str, test_input, timeout):
    1. compile code_str -> code_obj, tag with tempfile-like fake filename "<traced>"
    2. self._executed_lines = set(); self._target_filename set to compiled co_filename
    3. install SIGALRM handler raising TraceTimeoutError, signal.alarm(timeout)  # ponytail: SIGALRM is Unix-only, use threading.Timer if Windows support needed
    4. sys.settrace(self.trace_function)
    5. try: exec(code_obj + test_input, {}, {})
       except (Exception, TraceTimeoutError): pass  # swallow, keep partial trace
       finally: sys.settrace(None); signal.alarm(0)
    6. return self._executed_lines

trace_function(frame, event, arg):
    if event == "line" and frame.f_code.co_filename == self._target_filename:
        self._executed_lines.add(frame.f_lineno)
    return self.trace_function  # keep tracing local scope
```

### Tensor Shapes

N/A (no tensors — line numbers are plain `set[int]`).

### Subtasks [4/10 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Trace callback | Implement `trace_function`, filter by filename, record line events |
| L-2-2 | Compile + exec | Combine code_str + test_input into single compiled unit |
| L-2-3 | Timeout guard | SIGALRM-based timeout, partial-trace-on-timeout |
| L-2-4 | Exception safety | Catch all exceptions during exec, always restore `sys.settrace(None)` |

---

## A-3: LineToTokenMapper [Complexity: 10, Budget: 3+2+3+2]

**Applied**: HuggingFace fast-tokenizer `offset_mapping` (char span per token) → line lookup via cumulative newline offsets

### API Signatures

```python
class LineToTokenMapper:
    def __init__(self, tokenizer):
        """tokenizer: transformers.PreTrainedTokenizerFast (must support return_offsets_mapping=True)."""
        self.tokenizer = tokenizer

    def build_line_map(self, code_str: str, tokens: list[str]) -> dict[int, int]:
        """Convenience wrapper: retokenizes code_str, returns token_idx -> line_num (1-indexed)."""
        ...

    def map_offsets_to_lines(
        self,
        code_str: str,
        offset_mapping: list[tuple[int, int]],
    ) -> dict[int, int]:
        """offset_mapping: [(char_start, char_end), ...] per token, from tokenizer.
        Returns {token_idx: line_num}. Special tokens (0,0) span -> line -1 (excluded)."""
        ...
```

### Tensor Shapes / Data Shapes

| Variable | Shape | Note |
|----------|-------|------|
| offset_mapping | List[N] of (int,int) | N = num tokens, char start/end (exclusive end) |
| line_starts | List[L] | L = num lines, cumulative char offset of each line start |
| result | dict[int,int] | len <= N; keys = token idx, values = 1-indexed line num |

### Pseudo-code

```
map_offsets_to_lines(code_str, offset_mapping):
    1. line_starts = [0] + [i+1 for i, c in enumerate(code_str) if c == '\n']
       # line_starts[k] = char offset where line (k+1) begins
    2. result = {}
    3. for token_idx, (start, end) in enumerate(offset_mapping):
           if start == end == 0 and token_idx not in (first_real_token_idx): continue  # special/pad token
           # binary search: line_num = rightmost line_starts[k] <= start
           line_num = bisect_right(line_starts, start)  # 1-indexed
           result[token_idx] = line_num
           # multi-line token (rare, e.g. triple-quoted string): map to START line only
    4. return result

build_line_map(code_str, tokens):
    1. enc = self.tokenizer(code_str, return_offsets_mapping=True, add_special_tokens=False)
    2. return self.map_offsets_to_lines(code_str, enc["offset_mapping"])
```

**Multi-line/edge handling**: token spanning a `\n` (e.g. inside triple-quoted string) is mapped to its **start line** only — downstream classifier treats it as executed iff start line executed. Comments/blank lines naturally get no tokens or are excluded via AST ground truth (A-5), not here.

### Subtasks [4/10 used, 8/10 total]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Line-start index | Build cumulative newline-offset table from code_str |
| L-3-2 | Offset→line lookup | `bisect_right` binary search per token offset |
| L-3-3 | Special/multi-line tokens | Skip (0,0) special tokens; multi-line tokens map to start line |
| L-3-4 | build_line_map wrapper | Tokenize code_str with fast tokenizer, delegate to map_offsets_to_lines |

---

## A-5: GroundTruthGenerator [Complexity: 9, Budget: 3+2+3+1]

**Applied**: `ast.walk` executable-node filter + optional `coverage.py` API cross-check

### API Signatures

```python
import ast

class GroundTruthGenerator:
    def __init__(self):
        pass

    def ast_executable_lines(self, code_str: str) -> set[int]:
        """Parse code_str, return line numbers of executable statement nodes
        (excludes: ClassDef/FunctionDef signature-only lines w/o body stmt,
        docstring-only Expr(Constant(str)), comments, blank lines, pass-through decorators counted)."""
        ...

    def coverage_cross_validate(self, code_str: str, test_input: str) -> set[int]:
        """Run code_str+test_input under coverage.py, return executed line set for cross-check only."""
        ...

    def generate(self, code_str: str, test_input: str) -> set[int]:
        """Ground truth = AST-executable lines that were actually executed
        (intersection with coverage_cross_validate if coverage available, else falls back to AST-only)."""
        ...
```

### Pseudo-code

```
ast_executable_lines(code_str):
    1. tree = ast.parse(code_str)
    2. lines = set()
    3. for node in ast.walk(tree):
           if isinstance(node, ast.stmt):
               if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                  and isinstance(node.value.value, str):
                   continue  # skip docstrings
               if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                   continue  # def/class line itself not "executed" as a statement in trace sense
               lines.add(node.lineno)
               # multi-line statements: also add node.end_lineno range if node spans multiple lines
               if hasattr(node, "end_lineno") and node.end_lineno > node.lineno:
                   lines.update(range(node.lineno, node.end_lineno + 1))
    4. return lines

coverage_cross_validate(code_str, test_input):
    1. try: import coverage
       except ImportError: return set()  # cross-check optional, skip gracefully
    2. cov = coverage.Coverage(); cov.start()
    3. exec(compile(code_str + test_input, "<gt>", "exec"), {})
    4. cov.stop()
    5. return set(cov.get_data().lines("<gt>") or [])

generate(code_str, test_input):
    1. ast_lines = self.ast_executable_lines(code_str)
    2. cov_lines = self.coverage_cross_validate(code_str, test_input)
    3. return (ast_lines & cov_lines) if cov_lines else ast_lines
```

### Subtasks [2/10 used, 10/10 total]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | AST executable-line filter | Walk AST, exclude docstrings/def-class headers, expand multi-line stmt ranges |
| L-5-2 | Coverage cross-check + merge | Optional coverage.py run, intersect with AST set in `generate()` |

---

## External Dependencies (Base Hypothesis)

N/A — H-M1 has no base hypothesis code dependency (green-field, first mechanism validation building conceptually on H-E1 but no shared code module).
