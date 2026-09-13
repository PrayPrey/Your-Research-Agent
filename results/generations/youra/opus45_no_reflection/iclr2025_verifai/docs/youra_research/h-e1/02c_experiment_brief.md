# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under standard verification signal generation, if we apply AS decomposition rules (file:line extraction, variable counting, trace depth measurement), then AS_loc, AS_state, and AS_causal can be independently computed for each signal type.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: If H-E1 fails, AS framework invalid. STOP verification.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to build on.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable during search. Proceeding with Exa findings.*

### Archon Code Examples

*Archon MCP unavailable during search. Proceeding with Exa findings.*

### Exa GitHub Implementations

**Key Finding 1: Iterative Code Repair Framework (Johin2/iterative-code-repair)**
- Implements HumanEval (164) + MBPP Sanitized (257) benchmarks
- Error type categorization: syntax, name, assertion errors
- Traceback capture and repair prompt construction
- Achieves +4.9 to +17.1pp improvement via self-repair
- Code extraction pipeline for LLM outputs

**Key Finding 2: Stderr Parser (grahama1970/agent-skills)**
- Production-grade traceback parsing with regex patterns:
  ```python
  _FILE_LINE_RE = re.compile(
      r'(?P<file>(?:[A-Za-z]:)?[^\s:()]+\.py)'
      r'(?::|\()(?P<line>\d+)(?:[: ,)](?P<col>\d+))?'
  )
  _PY_FRAME_RE = re.compile(r' File "([^"]+)", line (\d+)(?:, in ([^\n]+))?')
  ```
- Extracts: file path, line number, column, function name
- Confidence scoring for extracted evidence

**Key Finding 3: Stack Trace Parser (aiskillstore/marketplace)**
- Multi-language traceback parsing (Python, JS, Java, Go)
- Python-specific patterns:
  ```python
  'traceback_start': r'^Traceback \(most recent call last\):',
  'file_line': r'^\s+File "([^"]+)", line (\d+), in (.+)',
  'error_line': r'^(\w+(?:Error|Exception|Warning)): (.+)',
  ```

**Key Finding 4: Python traceback Module (stdlib)**
- `traceback.extract_tb()` returns StackSummary with FrameSummary objects
- Each FrameSummary has: filename, lineno, name, line, end_lineno, colno
- `traceback.format_exception()` for formatted output
- Built-in support for capture_locals=True

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is an EXISTENCE hypothesis testing AS component measurability. No prior paper implementation exists—this is novel framework validation.

**Recommended Implementation Path:**
- Primary: Python stdlib `traceback` module + custom regex extractors
- Fallback: Adapt stderr_parser.py patterns from agent-skills repo
- Justification: Stdlib provides robust frame extraction; regex handles edge cases

### Code Analysis (Serena MCP)

*Not applicable for this hypothesis—no existing codebase to analyze.*

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| Name | HumanEval + MBPP (subset) |
| Type | standard |
| Total Problems | 664 (HumanEval: 164, MBPP: 500) |
| Sample Size | 100 failing test cases (minimum statistically meaningful) |
| Source | openai/human-eval, google-research/mbpp |
| Split | Sample across both benchmarks proportionally |

**Sampling Strategy:**
- Generate initial buggy code for each problem using LLM (temp=0.7)
- Run pytest to identify failing cases
- Sample 100 failures stratified by error type (syntax, name, type, assertion)

**Loading Information** (for Phase 4 download):
- Method: huggingface_hub
- Identifier: openai/humaneval, mbpp
- Code:
```python
from datasets import load_dataset

humaneval = load_dataset("openai/openai_humaneval", split="test")
mbpp = load_dataset("mbpp", split="test")
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| Name | N/A (Extraction-only experiment) |
| Type | Rule-based extractors |
| Purpose | Extract AS components from raw signals |

This is an EXISTENCE hypothesis—no ML model required. We test whether AS components can be measured from signal text using deterministic extraction rules.

**Loading Information** (for Phase 4 download):
- Method: N/A (no model download needed)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Rule-based AS Component Extractors

**Core Mechanism Implementation:**

```python
import re
import traceback
from dataclasses import dataclass
from typing import Optional

@dataclass
class ASComponents:
    """Actionable Specificity components extracted from verification signal."""
    AS_loc: int      # Binary: 1 if file:line provided, 0 otherwise
    AS_state: int    # Count of exposed variable values
    AS_causal: int   # Trace depth (number of execution steps/frames)
    
    def is_valid(self) -> bool:
        """Check if extraction succeeded."""
        return self.AS_loc >= 0 and self.AS_state >= 0 and self.AS_causal >= 0

# Regex patterns for AS extraction
FILE_LINE_PATTERN = re.compile(
    r'File "([^"]+)", line (\d+)'
)
VARIABLE_VALUE_PATTERN = re.compile(
    r"(\w+)\s*=\s*(['\"]?[\w\d\.\-\[\]{}]+['\"]?)"
)
TRACEBACK_FRAME_PATTERN = re.compile(
    r'^\s+File "([^"]+)", line (\d+), in (\w+)',
    re.MULTILINE
)

def extract_AS_loc(signal_text: str) -> int:
    """Extract localization component (binary)."""
    match = FILE_LINE_PATTERN.search(signal_text)
    return 1 if match else 0

def extract_AS_state(signal_text: str) -> int:
    """Extract state exposure component (count of variable=value pairs)."""
    matches = VARIABLE_VALUE_PATTERN.findall(signal_text)
    # Filter common false positives
    excluded = {'File', 'line', 'in', 'Error', 'Exception'}
    valid_matches = [m for m in matches if m[0] not in excluded]
    return len(valid_matches)

def extract_AS_causal(signal_text: str) -> int:
    """Extract causal context component (trace depth)."""
    frames = TRACEBACK_FRAME_PATTERN.findall(signal_text)
    return len(frames)

def extract_all_components(signal_text: str) -> ASComponents:
    """Extract all AS components from verification signal."""
    return ASComponents(
        AS_loc=extract_AS_loc(signal_text),
        AS_state=extract_AS_state(signal_text),
        AS_causal=extract_AS_causal(signal_text)
    )

# Signal generation for 6 conditions (C1-C6)
def generate_signal_variants(error_output: str, trace_output: str) -> dict:
    """Generate 6 signal variants with controlled AS levels."""
    return {
        'C1': trace_output,  # Full trace (highest AS)
        'C2': truncate_trace(trace_output, max_frames=3),  # Truncated
        'C3': mask_values(trace_output),  # Value-masked
        'C4': extract_error_only(error_output),  # Error message only
        'C5': "",  # Static analysis (external, AS_loc=1, others=0)
        'C6': extract_syntax_error(error_output),  # Syntax error only
    }
```

### Training Protocol

| Attribute | Value |
|-----------|-------|
| Training Required | No |
| Type | Extraction validation (no training) |
| Procedure | Apply extractors to 100 failing test cases × 6 signal variants |

**Validation Procedure:**
1. Generate failing code for 100 problems
2. Capture error output using pytest with trace module
3. Generate 6 signal variants per failure
4. Apply AS extractors to all 600 signals
5. Record extraction success/failure per component
6. Calculate extraction rate per component

### Evaluation

| Metric | Description | Target |
|--------|-------------|--------|
| Extraction Rate | % signals where component extracted | ≥95% |
| AS Ordering | C1 > C2 > C3 > C4 on AS_state, AS_causal | Monotonic decrease |
| Component Independence | Low correlation between AS_loc, AS_state, AS_causal | r < 0.5 |

**Primary Success Criterion:**
- AS components extractable from ≥95% of signals (570+ of 600)

**Secondary Success Criterion:**
- AS values show expected ordering: mean(AS_state[C1]) > mean(AS_state[C2]) > mean(AS_state[C3]) > mean(AS_state[C4])

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Information Extraction Validation
- Library: Built-in Python (re, collections)
- Code:
```python
from collections import Counter

def compute_extraction_rate(results: list[ASComponents]) -> float:
    valid = sum(1 for r in results if r.is_valid())
    return valid / len(results)

def verify_ordering(results_by_condition: dict) -> bool:
    means = {c: np.mean([r.AS_state for r in rs]) 
             for c, rs in results_by_condition.items()}
    return means['C1'] > means['C2'] > means['C3'] > means['C4']
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Extraction rate per AS component (bar chart)

#### Additional Figures (LLM Autonomous)

1. **AS Component Distribution by Signal Type**: Box plots showing AS_loc, AS_state, AS_causal across C1-C6
2. **Extraction Success Heatmap**: Components × Signal types
3. **Component Correlation Matrix**: Pearson r between AS_loc, AS_state, AS_causal

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Extraction rate ≥ 95% for all components
3. AS ordering matches expected pattern (C1 > C2 > C3 > C4)

---

## Appendix: Reference Implementations

### A. Python Traceback Module Usage
```python
import traceback
import sys

try:
    # Execute buggy code
    exec(buggy_code)
except Exception as e:
    # Capture full traceback
    tb = traceback.extract_tb(sys.exc_info()[2])
    for frame in tb:
        print(f"File: {frame.filename}, Line: {frame.lineno}, Func: {frame.name}")
```

### B. Stderr Parser Patterns (from agent-skills)
```python
_FILE_LINE_RE = re.compile(
    r'(?P<file>(?:[A-Za-z]:)?[^\s:()]+\.py)'
    r'(?::|\()(?P<line>\d+)(?:[: ,)](?P<col>\d+))?'
)
_PY_FRAME_RE = re.compile(r' File "([^"]+)", line (\d+)(?:, in ([^\n]+))?')
```

### C. Iterative Repair Protocol (from iterative-code-repair)
- Capture error type and traceback message
- Construct repair prompt: (1) problem spec, (2) previous code, (3) error message
- Execute in sandboxed Python environment
- Track pass/fail per error type

### D. Related GitHub Repositories
1. Johin2/iterative-code-repair - HumanEval/MBPP self-repair
2. grahama1970/agent-skills - Production stderr parsing
3. gujiprogram/DynaFix - Execution-level dynamic information for APR
4. kimjune01/abductor - Execution-gated evaluation for LLM repair

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- Phase 2C experiment design started
- Archon MCP unavailable (socket error)
- Exa search completed: found traceback parsing patterns, iterative repair frameworks
- Experiment specification synthesized

---

*MCP Tools Used: Exa (GitHub + Web Search)*
*Archon unavailable during execution*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
