# Logic: H-M1 — Error Traces Contain Counterfactual Information

Applied: pipeline-stage pattern (injector -> executor -> parser -> annotator -> scorer)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, Serena skipped (no base hypothesis, no existing codebase)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: BugInjector syntax/logic [Complexity: 11, Budget: 3+2+4+2]

**Applied**: ast.NodeTransformer visitor pattern (Python stdlib)

### API Signatures

```python
import ast
import random

class BugInjector:
    def __init__(self, seed: int):
        """Seeded injector for reproducible bug generation."""
        self.rng = random.Random(seed)

    def inject_syntax_bug(self, correct_code: str) -> tuple[str, int, str]:
        """Text-level mutation (ast can't represent invalid syntax).
        Returns (buggy_code, bug_line, bug_description)."""
        ...

    def inject_logic_bug(self, correct_code: str) -> tuple[str, int, str]:
        """AST-level operator/condition mutation.
        Returns (buggy_code, bug_line, bug_description)."""
        ...

    def inject(self, correct_code: str, bug_type: str) -> tuple[str, int, str]:
        """Dispatch to inject_{bug_type}_bug. Retries up to 5x if
        validation fails (bug must not produce identical code)."""
        ...

    def inject_all_types(self, problem: dict) -> list[dict]:
        """One buggy sample per BUG_TYPES entry.
        problem: {id, prompt, code, tests}
        Returns: [{id, bug_type, buggy_code, bug_line, bug_description}, ...]"""
        ...
```

### Pseudo-code: inject_syntax_bug

```
1. candidates = find candidate lines via regex:
   - lines matching r'^(\s*(def|if|for|while|class).*):\s*$'  -> colon removal
   - lines with balanced parens r'\([^)]*\)'                  -> paren removal
   - lines with leading whitespace > 0                         -> indentation shift
2. if no candidates: raise InjectionError
3. line = rng.choice(candidates)
4. mutation = rng.choice(applicable mutations for line)
5. buggy_lines = lines.copy(); buggy_lines[line_idx] = mutate(line, mutation)
6. buggy_code = "\n".join(buggy_lines)
7. validate: ast.parse(buggy_code) MUST raise SyntaxError (else retry)
8. return buggy_code, line_idx + 1, f"{mutation} removed at line {line_idx+1}"
```

### Pseudo-code: inject_logic_bug

```
1. tree = ast.parse(correct_code)
2. class OperatorMutator(ast.NodeTransformer):
     TARGETS = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE,
                ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.And: ast.Or, ast.Or: ast.And}
     def visit_Compare(self, node):
         # mutate node.ops[0] if type in TARGETS
     def visit_BoolOp(self, node):
         # mutate node.op if type in TARGETS
3. collect all mutable nodes with lineno via single pass (visit, don't mutate yet)
4. if none found: raise InjectionError
5. target_node = rng.choice(mutable_nodes)
6. apply single mutation to target_node only (copy tree, mutate one op)
7. buggy_code = ast.unparse(mutated_tree)
8. validate: buggy_code != correct_code
9. return buggy_code, target_node.lineno, f"{orig_op} -> {new_op} at line {target_node.lineno}"
```

### Tensor Shapes

N/A (no tensors; code/text I/O only).

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | `inject_syntax_bug` | Regex candidate scan + text mutation + SyntaxError validation |
| L-2-2 | `inject_logic_bug` | AST operator/condition mutation via NodeTransformer |
| L-2-3 | `inject` dispatcher + retry loop | Dispatch by bug_type, retry on validation failure (max 5) |
| L-2-4 | `inject_all_types` | Loop over BUG_TYPES, aggregate into list[dict] schema |

---

## A-4: SandboxExecutor [Complexity: 14, Budget: 3+4+3+4]

**Applied**: docker SDK container-per-run pattern with resource limits

### API Signatures

```python
from dataclasses import dataclass
import docker

@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    traceback: str
    timed_out: bool

class SandboxExecutor:
    def __init__(self, timeout_s: int = 10, memory_mb: int = 512,
                 image: str = "python:3.10-slim"):
        """Reuses a docker.DockerClient across run() calls."""
        self.client = docker.from_env()

    def run(self, code: str, tests: str) -> ExecutionResult:
        """Writes code+tests to temp dir, mounts read-only, runs pytest
        in container with network disabled, memory/timeout limits."""
        ...

    def _build_script(self, code: str, tests: str) -> str:
        """Concatenates code + tests into single runnable pytest module."""
        ...

    def close(self) -> None:
        """Cleanup docker client."""
        ...
```

### Pseudo-code: run

```
1. tmpdir = tempfile.mkdtemp()
2. script = self._build_script(code, tests)   # code + "\n" + tests
3. write script to tmpdir/test_solution.py
4. try:
     container = client.containers.run(
         image=self.image,
         command=["pytest", "/workspace/test_solution.py", "-x", "--tb=long"],
         volumes={tmpdir: {"bind": "/workspace", "mode": "ro"}},
         working_dir="/workspace",
         mem_limit=f"{self.memory_mb}m",
         network_disabled=True,
         detach=True,
         stdout=True, stderr=True,
     )
     try:
         exit_status = container.wait(timeout=self.timeout_s)
         timed_out = False
     except (requests.exceptions.ReadTimeout, docker.errors.APIError):
         container.kill()
         timed_out = True
         exit_status = {"StatusCode": -1}
     logs = container.logs(stdout=True, stderr=True).decode(errors="replace")
     stdout, stderr = split_stdout_stderr(logs)  # docker mixes streams; use separate log calls
     traceback_str = extract_traceback(stderr)   # regex: r'Traceback[\s\S]*'
   finally:
     container.remove(force=True)
     shutil.rmtree(tmpdir)
5. return ExecutionResult(stdout, stderr, exit_status["StatusCode"], traceback_str, timed_out)
```

### Tensor Shapes

N/A (subprocess/container I/O; no tensors).

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | `ExecutionResult` dataclass + `_build_script` | Merge code+tests into pytest module |
| L-4-2 | `run` container lifecycle | docker run with mem_limit, network_disabled, volume mount |
| L-4-3 | Timeout handling | `container.wait(timeout=)`, kill on ReadTimeout, set `timed_out` |
| L-4-4 | Log parsing + cleanup | Split stdout/stderr, extract traceback regex, force-remove container/tmpdir (try/finally) |

---

## A-5: TraceParser [Complexity: 13, Budget: 3+2+5+3]

**Applied**: regex-cascade heuristic extraction (per LDB reference pattern)

### API Signatures

```python
from dataclasses import dataclass, field

@dataclass
class ParsedTrace:
    line_numbers: list[int] = field(default_factory=list)
    expected: str | None = None
    actual: str | None = None
    type_info: str | None = None
    variable_state: dict = field(default_factory=dict)
    call_chain: list[str] = field(default_factory=list)

class TraceParser:
    def parse(self, result: "ExecutionResult") -> ParsedTrace:
        """Combines traceback + stderr, applies regex extractors."""
        ...

    def _extract_line_numbers(self, text: str) -> list[int]: ...
    def _extract_expected_actual(self, text: str) -> tuple[str | None, str | None]: ...
    def _extract_type_info(self, text: str) -> str | None: ...
    def _extract_variable_state(self, text: str) -> dict: ...
    def _extract_call_chain(self, text: str) -> list[str]: ...
```

### Pseudo-code: parse

```
1. text = result.traceback or result.stderr
2. if not text: return ParsedTrace()  # all empty/None defaults

3. # line_numbers: File "...", line N, in <func>
   pattern_line = r'File "[^"]+", line (\d+)'
   line_numbers = [int(m) for m in re.findall(pattern_line, text)]

4. # expected/actual: pytest assert rewrite output
   #   "assert 3 == 4" or "AssertionError: assert X == Y" or "E   assert ... == ..."
   pattern_assert = r'assert\s+(.+?)\s*==\s*(.+)'
   m = re.search(pattern_assert, text)
   if m: actual, expected = m.group(1).strip(), m.group(2).strip()
   else:
     # pytest verbose form: "E       assert 3 == 4" or "Expected: X\nActual: Y"
     m2 = re.search(r'Expected[:\s]+(.+)\nActual[:\s]+(.+)', text)
     if m2: expected, actual = m2.group(1).strip(), m2.group(2).strip()

5. # type_info: last exception class name, e.g. "TypeError: ..." / "IndexError: ..."
   pattern_type = r'\b(\w*Error|\w*Exception)\b:'
   matches = re.findall(pattern_type, text)
   type_info = matches[-1] if matches else None

6. # variable_state: locals dump if present (pytest -l / --showlocals style)
   #   "x          = 5\ny          = 'abc'"
   pattern_var = r'^(\w+)\s*=\s*(.+)$'  # re.MULTILINE, restricted to locals block
   locals_block = extract_locals_section(text)  # between "-- Locals --" markers or fallback ""
   variable_state = {m.group(1): m.group(2) for m in re.finditer(pattern_var, locals_block, re.MULTILINE)}

7. # call_chain: function names from "in <func>" on File lines
   pattern_call = r'File "[^"]+", line \d+, in (\S+)'
   call_chain = re.findall(pattern_call, text)

8. return ParsedTrace(line_numbers, expected, actual, type_info, variable_state, call_chain)
```

### Tensor Shapes

N/A (text parsing only).

### Subtasks [3/3 used — note: budget lists 3+2+5+3=13, mapped to 4 subtasks below matching regex groups]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | `_extract_line_numbers` + `_extract_call_chain` | File/line/func regex cascade |
| L-5-2 | `_extract_expected_actual` | assert-rewrite + Expected/Actual dual regex fallback |
| L-5-3 | `_extract_type_info` + `_extract_variable_state` | Exception class regex; locals-block regex with section isolation |
| L-5-4 | `parse` orchestration + empty-trace guard | Combine extractors, handle empty/no-traceback case |

---

## External Dependencies

None — green-field project, no base hypothesis code to reuse.
