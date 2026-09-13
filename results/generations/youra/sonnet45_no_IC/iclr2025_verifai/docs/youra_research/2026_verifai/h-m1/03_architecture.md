# System Architecture: h-m1
## Natural Language Content Validation

**Date:** 2026-07-14  
**Hypothesis Type:** MECHANISM (Data Analysis)  
**Complexity Tier:** LIGHT  
**Applied Patterns:** Modular validation pipeline, Text extraction with regex, Metric-driven evaluation

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Reusing h-e1 validation pipeline architecture  
**Analyzed Path:** docs/youra_research/h-e1/code/  
**Findings:** H-E1 implemented modular pipeline (parser → validator → calculator → evaluator → visualizer). H-M1 extends validator logic with NL-specific word counting (regex-based) while reusing identical pipeline structure.

---

## Architecture Overview

**Type:** Data Validation Pipeline (Non-ML) - Extended from H-E1

**Core Flow:**
1. Trace File Loading (reuse H-E1) → 2. NL Word Extraction → 3. NL Presence Validation → 4. Metrics Calculation → 5. Visualization

**Design Principles:**
- Reuse H-E1 TraceParser (no changes)
- Enhance CompletenessValidator with regex-based NL word counting
- Add NL-specific breakdown metrics (query vs result)
- Generate NL-focused visualizations

**Key Difference from H-E1:**
- H-E1: Field presence + simple word count (any words)
- H-M1: Natural language word count (≥2 alphabetic chars) + source breakdown

---

## Module Structure

### TraceParser (`code/src/trace_parser.py`)

**Dependencies:** pathlib, json  
**Status:** REUSED FROM H-E1 (no modifications)

```python
class TraceParser:
    def __init__(self, trace_folder: Path): ...
    def discover_traces(self) -> List[Path]: ...
    def parse_trace_file(self, file_path: Path) -> Dict: ...
    def load_all_traces(self) -> List[Dict]: ...
```

### NLContentValidator (`code/src/nl_content_validator.py`)

**Dependencies:** re, typing  
**Status:** NEW (replaces CompletenessValidator)

```python
class NLContentValidator:
    def __init__(self, min_word_count: int = 10): ...
    def count_nl_words(self, text: str) -> int: ...
    def extract_text_from_dict(self, obj) -> str: ...
    def validate_nl_presence(self, tool_call: Dict) -> Tuple[bool, int, int]: ...
    def get_source_type(self, query_words: int, result_words: int) -> str: ...
```

### MetricsCalculator (`code/src/metrics_calculator.py`)

**Dependencies:** NLContentValidator, typing  
**Status:** EXTENDED (add NL breakdown metrics)

```python
class MetricsCalculator:
    def __init__(self, validator: NLContentValidator): ...
    def calculate_nl_presence_rate(self, traces: List[Dict]) -> float: ...
    def calculate_source_breakdown(self, traces: List[Dict]) -> Dict: ...
    def calculate_tool_type_breakdown(self, traces: List[Dict]) -> Dict: ...
    def calculate_word_count_distribution(self, traces: List[Dict]) -> Dict: ...
```

### Evaluator (`code/src/evaluator.py`)

**Dependencies:** MetricsCalculator, json  
**Status:** MODIFIED (change gate condition logic)

```python
class Evaluator:
    def __init__(self, calculator: MetricsCalculator, threshold: float = 0.90): ...
    def evaluate_hypothesis(self, traces: List[Dict]) -> Dict: ...
    def check_gate_condition(self, results: Dict) -> bool: ...
    def save_results(self, results: Dict, output_path: Path) -> None: ...
```

### Visualizer (`code/src/visualizer.py`)

**Dependencies:** matplotlib, numpy  
**Status:** MODIFIED (new figures for NL analysis)

```python
class Visualizer:
    def __init__(self, output_dir: Path, dpi: int = 300): ...
    def plot_gate_metrics(self, results: Dict) -> None: ...
    def plot_word_count_distribution(self, traces: List[Dict]) -> None: ...
    def plot_nl_source_breakdown(self, results: Dict) -> None: ...
    def plot_nl_by_tool_type(self, results: Dict) -> None: ...
    def generate_all_figures(self, traces: List[Dict], results: Dict) -> None: ...
```

### Main (`code/src/main.py`)

**Dependencies:** All modules above, argparse  
**Status:** MODIFIED (update imports and print statements)

```python
def parse_arguments() -> argparse.Namespace: ...
def main() -> int: ...
```

---

## File Organization

```
{hypothesis_folder}/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── trace_parser.py          [REUSED from H-E1]
│   │   ├── nl_content_validator.py  [NEW - replaces completeness_validator.py]
│   │   ├── metrics_calculator.py    [EXTENDED]
│   │   ├── evaluator.py             [MODIFIED]
│   │   ├── visualizer.py            [MODIFIED]
│   │   └── main.py                  [MODIFIED]
│   ├── config/
│   │   └── config.py                [MODIFIED - update threshold to 0.90]
│   ├── tests/
│   │   └── test_nl_validation.py    [NEW]
│   └── requirements.txt             [SAME as H-E1]
├── figures/
│   ├── fig1_gate_metrics.png
│   ├── fig2_word_count_distribution.png
│   ├── fig3_nl_source_breakdown.png
│   └── fig4_nl_by_tool_type.png
├── h_m1_results.json
└── 03_architecture.md (this document)

{research_folder}/mcp_traces/
└── [20 .jsonl files from H-E1 - NO CHANGES]
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| TraceParser | `from src.trace_parser import TraceParser` | `h-e1/code/src/trace_parser.py` |

**Reuse Strategy:** Copy trace_parser.py directly from H-E1 (no modifications required)

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation)

---

## Configuration

### Config (`code/config/config.py`)

**Dependencies:** pathlib  
**Status:** MODIFIED (update threshold)

```python
class Config:
    TRACE_FOLDER: Path
    HYPOTHESIS_FOLDER: Path
    FIGURES_DIR: Path
    RESULTS_FILE: Path
    NL_THRESHOLD: float = 0.90           # Changed from COMPLETENESS_THRESHOLD 0.95
    MIN_WORD_COUNT: int = 10
    NL_WORD_PATTERN: str = r'\b[a-zA-Z]{2,}\b'  # NEW - regex pattern
    REQUIRED_FIELDS: List[str] = ['tool_name', 'parameters', 'result']
    FIGURE_DPI: int = 300
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1 | Setup Project Structure | Copy H-E1 structure, modify config.py (threshold 0.90, add regex pattern) | 4 | Module(1) + Deps(1) + Algo(1) + Integ(1) |
| M2 | Implement NL Validator | Regex-based NL word counting, recursive text extraction, source type detection | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| M3 | Extend Metrics Calculator | NL rate, source breakdown (query/result/both/neither), tool type breakdown, word distribution | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |
| M4 | Modify Evaluator | Update gate condition (≥90% NL presence), JSON output schema | 5 | Module(2) + Deps(1) + Algo(1) + Integ(1) |
| M5 | Modify Visualizer | 4 NL-specific figures (gate, distribution histogram, source breakdown, tool type) | 12 | Module(3) + Deps(3) + Algo(3) + Integ(3) |
| M6 | Update Main Pipeline | Update imports, print messages, CLI args handling | 4 | Module(1) + Deps(1) + Algo(1) + Integ(1) |
| M7 | Integration & Testing | End-to-end validation, unit tests for regex word counting, edge case tests | 9 | Module(2) + Deps(2) + Algo(2) + Integ(3) |

**Total Complexity:** 55  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M2, M3, M5, M7], Low(4-8): [M1, M4, M6]

---

## Data Flow

### Input Processing (Reused from H-E1)
1. `TraceParser.discover_traces()` → List[Path] (20 trace files)
2. `TraceParser.parse_trace_file()` → Dict (tool_calls, outcome, file)
3. `TraceParser.load_all_traces()` → List[Dict] (all traces)

### NL Validation Pipeline (New)
4. `NLContentValidator.extract_text_from_dict()` → str (query text, result text)
5. `NLContentValidator.count_nl_words()` → int (NL word count per source)
6. `NLContentValidator.validate_nl_presence()` → (bool, query_words, result_words)
7. `NLContentValidator.get_source_type()` → str (query_only/result_only/both/neither)

### Metrics Calculation (Extended)
8. `MetricsCalculator.calculate_nl_presence_rate()` → float [0,100]
9. `MetricsCalculator.calculate_source_breakdown()` → Dict (counts by source type)
10. `MetricsCalculator.calculate_tool_type_breakdown()` → Dict (NL rate by tool type)
11. `MetricsCalculator.calculate_word_count_distribution()` → Dict (bins: 0-5, 5-10, 10-20, 20-50, 50+)

### Evaluation & Output
12. `Evaluator.evaluate_hypothesis()` → Dict (all metrics + gate decision)
13. `Evaluator.save_results()` → h_m1_results.json
14. `Visualizer.generate_all_figures()` → 4 PNG files

---

## Key Algorithm: NL Word Counting

**Pattern:** `r'\b[a-zA-Z]{2,}\b'` (words with ≥2 alphabetic characters)

**Rationale:** Excludes punctuation-only tokens, single-char symbols, numbers. Captures actual English words.

**Example:**
```python
text = "Query: search 'RAG architecture' with max_count=5"
# Standard split: ['Query:', 'search', "'RAG", "architecture'", 'with', 'max_count=5']
# NL regex match: ['Query', 'search', 'RAG', 'architecture', 'with', 'max', 'count']
# Count: 7 words
```

---

## Error Handling Strategy

### Parse Errors (Inherited from H-E1)
- **Malformed JSON Lines:** Skip line, log warning
- **Missing Files:** Raise FileNotFoundError
- **Empty Files:** Return empty tool_calls list

### Validation Errors (New)
- **Non-string Types:** Convert to string via extract_text_from_dict()
- **Empty Dicts:** Return empty string (0 word count)
- **Regex Failures:** Return 0 (invalid input)

### Visualization Errors (Modified)
- **Empty Word Count List:** Create placeholder with warning
- **Division by Zero:** Check total_calls > 0 before percentage calculation

---

## Acceptance Criteria

### M1: Setup Project Structure
- [ ] Directory structure matches H-E1 layout
- [ ] config.py updated: NL_THRESHOLD = 0.90, NL_WORD_PATTERN added
- [ ] requirements.txt identical to H-E1
- [ ] trace_parser.py copied from H-E1 (no modifications)

### M2: Implement NL Validator
- [ ] `count_nl_words()` uses regex pattern `r'\b[a-zA-Z]{2,}\b'`
- [ ] `extract_text_from_dict()` handles nested dicts, lists, strings
- [ ] `validate_nl_presence()` returns (bool, query_words, result_words)
- [ ] `get_source_type()` returns: query_only, result_only, both, neither
- [ ] Edge cases: empty params, null results, non-string types handled

### M3: Extend Metrics Calculator
- [ ] `calculate_nl_presence_rate()` = (calls with ≥10 NL words) / total * 100
- [ ] `calculate_source_breakdown()` counts all 4 source types
- [ ] `calculate_tool_type_breakdown()` identifies research vs data processing tools
- [ ] `calculate_word_count_distribution()` bins: 0-5, 5-10, 10-20, 20-50, 50+
- [ ] All metrics returned in structured dict

### M4: Modify Evaluator
- [ ] Gate condition: NL presence rate ≥ 90%
- [ ] JSON output schema includes: nl_presence_rate, source_breakdown, tool_type_breakdown, word_count_distribution
- [ ] Console output shows PASS/FAIL with NL rate
- [ ] save_results() writes h_m1_results.json

### M5: Modify Visualizer
- [ ] Figure 1: Gate metrics (actual vs 90% threshold) bar chart
- [ ] Figure 2: Word count distribution histogram (bins with threshold line at 10)
- [ ] Figure 3: NL source breakdown (stacked bar or pie chart)
- [ ] Figure 4: NL presence by tool type (grouped bar chart)
- [ ] All figures save as 300 DPI PNG

### M6: Update Main Pipeline
- [ ] Imports use NLContentValidator (not CompletenessValidator)
- [ ] Print messages: "H-M1: NATURAL LANGUAGE CONTENT VALIDATION"
- [ ] Threshold display: 90% (not 95%)
- [ ] Pipeline orchestration: parse → validate → calculate → evaluate → visualize

### M7: Integration & Testing
- [ ] Unit test: regex pattern matches expected words
- [ ] Unit test: source type detection (all 4 cases)
- [ ] Unit test: word count distribution binning
- [ ] Integration test: mock 5 traces → expected NL rate
- [ ] End-to-end: process 596 tool calls → h_m1_results.json + 4 figures

---

## Testing Strategy

### Unit Tests (`tests/test_nl_validation.py`)
1. **test_nl_word_counting_regex**: Validate pattern `r'\b[a-zA-Z]{2,}\b'`
2. **test_text_extraction_nested**: Recursive dict/list traversal
3. **test_source_type_detection**: All 4 categories (query/result/both/neither)
4. **test_word_count_distribution_binning**: Correct bin assignment
5. **test_nl_presence_threshold**: ≥10 words → True, <10 → False

### Integration Test
- **Mock Dataset:** 5 trace files (mix of high/low NL content)
- **Expected Output:** h_m1_results.json with correct schema
- **Validation:** All 4 figures created, NL rate matches manual count

---

## Dependencies

### Python Packages (Same as H-E1)
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
- **Primary:** NL presence rate ≥ 90%
- **Decision:** PASS if condition met, else FAIL

### Deliverables
1. 6 Python modules (parser [reused], validator [new], calculator, evaluator, visualizer, main)
2. 4 PNG figures (fig1-4)
3. 1 JSON results file (h_m1_results.json)
4. Console summary with gate decision

---

## Risk Mitigation

### Risk: NL Content Below 90% Threshold
- **Probability:** MEDIUM (unknown until measured)
- **Impact:** HIGH (blocks H-M2, H-M3, H-M4)
- **Mitigation:** 
  - If 80-90%: Analyze source breakdown, consider threshold adjustment
  - If <80%: Enhance MCP wrappers, re-collect traces per PRD R2

### Risk: Regex Pattern Too Restrictive
- **Probability:** LOW (standard pattern)
- **Impact:** MEDIUM (false negatives in word counting)
- **Mitigation:** Unit test with diverse text samples, adjust pattern if needed

### Risk: Source Imbalance (e.g., only queries have NL, not results)
- **Probability:** MEDIUM
- **Impact:** MEDIUM (Layer 3 may fail even if H-M1 passes)
- **Mitigation:** Report source breakdown in 04_validation.md, document limitation

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Phase 4 Coder - Implement all modules per Epic tasks  
**Estimated Effort:** 6-8 hours (7 Epic tasks, LIGHT complexity tier)
