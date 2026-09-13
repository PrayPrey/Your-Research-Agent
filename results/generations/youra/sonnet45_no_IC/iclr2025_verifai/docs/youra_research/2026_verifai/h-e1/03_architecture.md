# System Architecture: h-e1
## MCP Trace Data Availability Validation

**Date:** 2026-07-13  
**Hypothesis Type:** EXISTENCE (PoC)  
**Complexity Tier:** LIGHT  
**Applied Patterns:** Modular validation pipeline, Error-tolerant parsing, Metric-driven evaluation

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** Novel MCP trace validation system - no existing codebase to analyze

---

## Architecture Overview

**Type:** Data Validation Pipeline (Non-ML)

**Core Flow:**
1. Trace File Discovery → 2. JSONL Parsing → 3. Completeness Validation → 4. Metrics Calculation → 5. Visualization

**Design Principles:**
- Error-tolerant parsing (skip malformed lines)
- Streaming for large files
- Modular validation logic
- Single-pass metric computation

---

## Module Structure

### TraceParser (`code/src/trace_parser.py`)

**Dependencies:** pathlib, json

```python
class TraceParser:
    def __init__(self, trace_folder: str): ...
    def discover_traces(self) -> list[Path]: ...
    def parse_trace_file(self, file_path: Path) -> dict: ...
    def load_all_traces(self) -> list[dict]: ...
```

### CompletenessValidator (`code/src/completeness_validator.py`)

**Dependencies:** None

```python
class CompletenessValidator:
    def validate_tool_call(self, tool_call: dict) -> bool: ...
    def count_words(self, text: str) -> int: ...
    def extract_nl_content(self, tool_call: dict) -> tuple[int, int]: ...
```

### MetricsCalculator (`code/src/metrics_calculator.py`)

**Dependencies:** CompletenessValidator

```python
class MetricsCalculator:
    def __init__(self, validator: CompletenessValidator): ...
    def calculate_overall_completeness(self, traces: list[dict]) -> float: ...
    def calculate_per_file_stats(self, traces: list[dict]) -> dict: ...
    def verify_failure_traces(self, traces: list[dict]) -> dict: ...
```

### Evaluator (`code/src/evaluator.py`)

**Dependencies:** MetricsCalculator, json

```python
class Evaluator:
    def __init__(self, calculator: MetricsCalculator): ...
    def evaluate_hypothesis(self, traces: list[dict]) -> dict: ...
    def check_gate_condition(self, results: dict) -> bool: ...
    def save_results(self, results: dict, output_path: Path) -> None: ...
```

### Visualizer (`code/src/visualizer.py`)

**Dependencies:** matplotlib, numpy

```python
class Visualizer:
    def __init__(self, output_dir: Path): ...
    def plot_gate_metrics(self, results: dict) -> None: ...
    def plot_per_file_distribution(self, traces: list[dict]) -> None: ...
    def plot_completeness_breakdown(self, traces: list[dict]) -> None: ...
    def plot_nl_content_analysis(self, traces: list[dict]) -> None: ...
    def generate_all_figures(self, traces: list[dict], results: dict) -> None: ...
```

### Main (`code/src/main.py`)

**Dependencies:** All modules above, argparse

```python
def parse_arguments() -> argparse.Namespace: ...
def setup_logging() -> None: ...
def main() -> int: ...
```

---

## File Organization

```
{hypothesis_folder}/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── trace_parser.py
│   │   ├── completeness_validator.py
│   │   ├── metrics_calculator.py
│   │   ├── evaluator.py
│   │   ├── visualizer.py
│   │   └── main.py
│   ├── config/
│   │   └── config.py
│   ├── tests/
│   │   └── test_validation.py
│   └── requirements.txt
├── figures/
│   ├── fig1_gate_metrics.png
│   ├── fig2_per_file.png
│   ├── fig3_breakdown.png
│   └── fig4_nl_content.png
├── h_e1_results.json
└── 03_architecture.md (this document)

{research_folder}/mcp_traces/
├── success_001.jsonl
├── success_002.jsonl
├── ...
├── fail_h-e1_001.jsonl
├── fail_h-m1_001.jsonl
└── ... (20 total)
```

---

## Configuration

### Config (`code/config/config.py`)

**Dependencies:** pathlib

```python
class Config:
    TRACE_FOLDER: str
    HYPOTHESIS_FOLDER: str
    FIGURES_DIR: Path
    RESULTS_FILE: Path
    COMPLETENESS_THRESHOLD: float = 0.95
    MIN_WORD_COUNT: int = 10
    REQUIRED_FIELDS: list[str] = ['tool_name', 'parameters', 'result']
    FIGURE_DPI: int = 300
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Setup Project Structure | Create directory layout, requirements.txt, config.py | 4 | Module(1) + Deps(1) + Algo(1) + Integ(1) |
| E2 | Implement Trace Parser | JSONL parsing with error handling, file discovery | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| E3 | Implement Validation Logic | Field presence checks, NL content validation (≥10 words) | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| E4 | Implement Metrics Calculator | Overall rate, per-file stats, failure trace verification | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| E5 | Implement Evaluator | Gate condition logic, JSON output, console reporting | 6 | Module(2) + Deps(1) + Algo(1) + Integ(2) |
| E6 | Implement Visualizer | Generate 4 figures (gate, distribution, breakdown, NL) | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |
| E7 | Integration & Testing | Main script orchestration, end-to-end validation | 10 | Module(2) + Deps(2) + Algo(2) + Integ(4) |

**Total Complexity:** 55  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E4, E6, E7], Low(4-8): [E1, E2, E3, E5]

---

## Data Flow

### Input Processing
1. `TraceParser.discover_traces()` → List[Path] (20 trace files)
2. `TraceParser.parse_trace_file()` → dict (tool_calls, outcome, file)
3. `TraceParser.load_all_traces()` → List[dict] (all traces)

### Validation Pipeline
4. `CompletenessValidator.validate_tool_call()` → bool (per tool call)
5. `MetricsCalculator.calculate_overall_completeness()` → float [0,1]
6. `MetricsCalculator.calculate_per_file_stats()` → dict (min/max/mean)
7. `MetricsCalculator.verify_failure_traces()` → dict (h_e1_present, h_m1_present)

### Evaluation & Output
8. `Evaluator.evaluate_hypothesis()` → dict (all metrics + gate decision)
9. `Evaluator.save_results()` → h_e1_results.json
10. `Visualizer.generate_all_figures()` → 4 PNG files

---

## Error Handling Strategy

### Parse Errors
- **Malformed JSON Lines:** Skip line, log warning with line number
- **Missing Files:** Raise FileNotFoundError with clear message
- **Empty Files:** Return empty tool_calls list, continue processing

### Validation Errors
- **Missing Fields:** Return False from validate_tool_call()
- **Type Mismatches:** Convert to string for word counting
- **Division by Zero:** Check total_calls > 0 before rate calculation

### Visualization Errors
- **Empty Data:** Create placeholder figure with warning text
- **Save Failures:** Raise with full path in error message

---

## Acceptance Criteria

### E1: Setup Project Structure
- [ ] All directories created (`src/`, `config/`, `tests/`, `figures/`)
- [ ] `requirements.txt` includes: matplotlib, numpy
- [ ] `config.py` defines all constants
- [ ] `__init__.py` present in src/

### E2: Implement Trace Parser
- [ ] `discover_traces()` finds all .jsonl files
- [ ] `parse_trace_file()` handles malformed lines without crashing
- [ ] Extracted fields: tool_name, parameters, result per line
- [ ] Returns structured dict with file, outcome, tool_calls

### E3: Implement Validation Logic
- [ ] `validate_tool_call()` checks all 3 required fields
- [ ] Word counting handles strings, dicts, nested structures
- [ ] Returns True only if ≥10 total words
- [ ] Edge cases: empty params, null results return False

### E4: Implement Metrics Calculator
- [ ] Overall completeness rate = complete/total
- [ ] Per-file stats compute min/max/mean correctly
- [ ] `verify_failure_traces()` checks filename patterns (h-e1, h_e1, h-m1, h_m1)
- [ ] Returns all metrics in structured dict

### E5: Implement Evaluator
- [ ] `evaluate_hypothesis()` aggregates all metrics
- [ ] `check_gate_condition()` validates: rate ≥0.95 AND both failure traces present
- [ ] `save_results()` writes valid JSON to h_e1_results.json
- [ ] Console output shows summary with pass/fail status

### E6: Implement Visualizer
- [ ] Figure 1: Bar chart (Target vs Actual), threshold line, color-coded
- [ ] Figure 2: Histogram (20 files), mean line, success/fail colors
- [ ] Figure 3: Stacked bar (complete/incomplete), grouped by outcome
- [ ] Figure 4: Scatter plot (word counts), 10-word threshold line
- [ ] All figures save as 300 DPI PNG

### E7: Integration & Testing
- [ ] `main.py` orchestrates full pipeline: parse → validate → evaluate → visualize
- [ ] Command-line arguments: --trace_folder, --output_folder
- [ ] Progress logging: "Processing trace X/20..."
- [ ] Final console output: all metrics + gate decision
- [ ] Test with mock trace data (5 files: 3 success, 2 fail)

---

## Testing Strategy

### Unit Tests (`tests/test_validation.py`)
1. **test_parse_malformed_json**: Skip bad lines gracefully
2. **test_validate_missing_fields**: Return False for incomplete calls
3. **test_word_count_edge_cases**: Empty strings, non-string types
4. **test_completeness_calculation**: Known input → expected rate
5. **test_failure_trace_detection**: Filename pattern matching

### Integration Test
- **Mock Dataset:** 5 trace files in temp directory
- **Expected Output:** h_e1_results.json with correct schema
- **Validation:** All 4 figures created, gate decision matches manual check

---

## Dependencies

### Python Packages
```
matplotlib>=3.5.0
numpy>=1.21.0
```

### System Requirements
- Python 3.8+
- 500MB disk space
- No GPU required

---

## Success Metrics

### Gate Condition (MUST_WORK)
- **Primary:** Completeness rate ≥ 95%
- **Secondary:** h-e1 failure trace present
- **Secondary:** h-m1 failure trace present
- **Decision:** PASS if all three conditions met

### Deliverables
1. 6 Python modules (parser, validator, calculator, evaluator, visualizer, main)
2. 4 PNG figures (fig1-4)
3. 1 JSON results file (h_e1_results.json)
4. Console summary with gate decision

---

## Risk Mitigation

### Risk: Trace Files Not Present
- **Mitigation:** Pre-flight check in main.py, fail fast with clear message
- **Fallback:** Document collection instructions in README

### Risk: All Traces Incomplete (<95%)
- **Mitigation:** Log detailed per-file stats to identify problematic traces
- **Fallback:** Gate fails, enhance MCP logging, re-collect

### Risk: Malformed JSONL
- **Mitigation:** Line-by-line parsing with try/except, continue on errors
- **Impact:** Reduced total_calls, may still achieve 95% on valid lines

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Phase 4 Coder - Implement all modules per Epic tasks  
**Estimated Effort:** 6-8 hours (7 Epic tasks, LIGHT complexity tier)
