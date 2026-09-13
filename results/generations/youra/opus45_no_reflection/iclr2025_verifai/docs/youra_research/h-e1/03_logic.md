# Logic: H-E1 (EXISTENCE / PoC)

**Applied**: Archon unavailable — stdlib `re`/`traceback` extraction patterns per architecture.md.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Pipeline [Complexity: 12, Budget: 12]

**Applied**: HuggingFace `datasets` load_dataset + pytest subprocess capture

### API Signatures

```python
def load_datasets() -> list[dict]:
    """Load HumanEval (164) + MBPP (500). Each item: {id, prompt, test, entry_point, source}."""
    ...

def generate_buggy_code(problem: dict, temp: float = 0.7) -> str:
    """LLM-generate an intentionally buggy solution for problem['prompt']."""
    ...

def run_pytest_capture(problem: dict, code: str) -> tuple[str, str]:
    """Write code+test to tmp file, run pytest subprocess.
    Returns (error_output, trace_output); ("","") if test passes."""
    ...

def sample_failures(problems: list[dict], n: int = 100, seed: int = 42) -> list[dict]:
    """Stratify by error type (syntax/name/type/assertion), sample n.
    Returns [{id, error_output, trace_output, error_type}]."""
    ...
```

### Pseudo-code

```
1. problems = load_datasets()  # 664 items
2. for p in problems: code = generate_buggy_code(p); err, trace = run_pytest_capture(p, code)
3. failures = [f for f in results if f.error_output]
4. group failures by error_type (regex on error_output first line: r'(\w+(?:Error|Exception)):')
5. stratified_sample(groups, n=100, seed=42)  # proportional per group
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_datasets | HF datasets.load_dataset for HumanEval + MBPP |
| L-1-2 | generate_buggy_code | LLM call, temp=0.7, prompt for intentional bug |
| L-1-3 | run_pytest_capture | subprocess pytest, capture stderr as error/trace |
| L-1-4 | sample_failures | error-type stratified sampling, seed=42 |

---

## A-2: Signal Generation [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch N/A — pure string/regex transforms per experiment brief.

### API Signatures

```python
def truncate_trace(trace_output: str, max_frames: int = 3) -> str:
    """Keep only first `max_frames` ' File "..."' blocks from trace_output."""
    ...

def mask_values(trace_output: str) -> str:
    """Replace VARIABLE_VALUE_PATTERN matches with 'var=<masked>'."""
    ...

def extract_error_only(error_output: str) -> str:
    """Return last line matching r'(\\w+(?:Error|Exception)): .+'."""
    ...

def extract_syntax_error(error_output: str) -> str:
    """Return SyntaxError line only, or "" if none present."""
    ...

def generate_signal_variants(error_output: str, trace_output: str) -> dict:
    """Returns {'C1': trace_output, 'C2': truncate_trace(...), 'C3': mask_values(...),
    'C4': extract_error_only(...), 'C5': '', 'C6': extract_syntax_error(...)}"""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | truncate_trace + mask_values | frame-limit and value-masking transforms |
| L-2-2 | extract_error_only | last error line via regex |
| L-2-3 | extract_syntax_error | SyntaxError-specific line extraction |
| L-2-4 | generate_signal_variants | assemble dict of 6 conditions per failure |

---

## A-3: AS Extractors [Complexity: 7, Budget: 7]

**Applied**: Regex extraction (stderr_parser pattern) — see architecture.md model.py.

### API Signatures

```python
@dataclass
class ASComponents:
    AS_loc: int      # 1 if file:line present, else 0
    AS_state: int     # count of var=value pairs
    AS_causal: int    # count of traceback frames

    def is_valid(self) -> bool:
        """True if all fields >= 0 (extraction did not error)."""
        ...

FILE_LINE_PATTERN = re.compile(r'File "([^"]+)", line (\d+)')
VARIABLE_VALUE_PATTERN = re.compile(r"(\w+)\s*=\s*(['\"]?[\w\d\.\-\[\]{}]+['\"]?)")
TRACEBACK_FRAME_PATTERN = re.compile(r'^\s+File "([^"]+)", line (\d+), in (\w+)', re.MULTILINE)

def extract_AS_loc(signal_text: str) -> int: ...
def extract_AS_state(signal_text: str) -> int: ...
def extract_AS_causal(signal_text: str) -> int: ...
def extract_all_components(signal_text: str) -> ASComponents: ...
```

### Pseudo-code

```
extract_AS_state:
  matches = VARIABLE_VALUE_PATTERN.findall(signal_text)
  excluded = {'File','line','in','Error','Exception'}
  return len([m for m in matches if m[0] not in excluded])
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | ASComponents dataclass | fields + is_valid |
| L-3-2 | compile regex patterns | FILE_LINE, VARIABLE_VALUE, TRACEBACK_FRAME |
| L-3-3 | extract_AS_loc | binary file:line detection |
| L-3-4 | extract_AS_state | var=value counting w/ false-positive filter |
| L-3-5 | extract_AS_causal | frame count via TRACEBACK_FRAME_PATTERN |
| L-3-6 | extract_all_components | wraps all three into ASComponents |
| L-3-7 | edge case handling | multi-file / nested exception traces (FR-3.4) |

---

## A-4: Evaluation Pipeline [Complexity: 6, Budget: 6]

**Applied**: numpy for correlation, stdlib for extraction-rate — per PRD FR-4.

### API Signatures

```python
def compute_extraction_rate(results: list[ASComponents]) -> dict[str, float]:
    """Per-component: fraction of results where component > 0 (or is_valid for overall).
    Returns {'AS_loc': .., 'AS_state': .., 'AS_causal': .., 'overall': ..}"""
    ...

def verify_ordering(results_by_condition: dict[str, list[ASComponents]]) -> bool:
    """True if mean(AS_state[C1]) > C2 > C3 > C4."""
    ...

def compute_correlation_matrix(results: list[ASComponents]) -> "np.ndarray":
    """3x3 Pearson correlation between AS_loc, AS_state, AS_causal."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| corr | [3, 3] | order: AS_loc, AS_state, AS_causal |

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | compute_extraction_rate | per-component + overall rate over 600 signals |
| L-4-2 | verify_ordering | mean AS_state comparison C1>C2>C3>C4 |
| L-4-3 | compute_correlation_matrix | np.corrcoef over 3 component arrays |
| L-4-4 | results aggregation | build results_by_condition dict from raw extractions |
| L-4-5 | CSV export | dump per-signal ASComponents + metrics to results/ |
| L-4-6 | PoC gate check | rate>=0.95 and ordering==True -> pass/fail print |

---

## A-5: Visualization + PoC Gate [Complexity: 5, Budget: 5]

**Applied**: matplotlib bar/box/heatmap — standard patterns.

### API Signatures

```python
def plot_extraction_rate_bar(rates: dict, out_path: str) -> None: ...
def plot_component_boxplots(results_by_condition: dict, out_path: str) -> None: ...
def plot_extraction_heatmap(results_by_condition: dict, out_path: str) -> None: ...
def plot_correlation_matrix(corr: "np.ndarray", out_path: str) -> None: ...

def main() -> None:
    """Load signals -> extract -> compute metrics -> save 4 figures + CSV -> print PoC pass/fail."""
    ...
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | plot_extraction_rate_bar | mandatory gate figure |
| L-5-2 | plot_component_boxplots | AS_loc/state/causal by C1-C6 |
| L-5-3 | plot_extraction_heatmap | components x conditions success matrix |
| L-5-4 | plot_correlation_matrix | 3x3 heatmap of Pearson r |
| L-5-5 | main() orchestration | wire evaluate.py pipeline end-to-end |

---

## External Dependencies (Base Hypothesis)

None — H-E1 is a FOUNDATION hypothesis with no prior work to build on.
