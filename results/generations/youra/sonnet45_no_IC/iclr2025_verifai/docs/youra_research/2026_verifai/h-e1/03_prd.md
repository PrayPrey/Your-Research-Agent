# Product Requirements Document (PRD)
## MCP Trace Data Availability Validation - H-E1

**Version:** 1.0  
**Date:** 2026-07-13  
**Author:** Anonymous  
**Hypothesis:** h-e1 (EXISTENCE)  
**Status:** Implementation Planning

---

## Executive Summary

### Purpose
Validate that MCP (Model Context Protocol) trace logging captures complete tool call records with natural language content, establishing the foundation for downstream semantic analysis in hypotheses H-M1 through H-M4.

### Scope
Implement a trace completeness validation system that:
1. Parses 20 MCP trace files (10 successful, 10 failed pipeline executions)
2. Validates field presence (tool_name, parameters, results)
3. Checks natural language content (≥10 words per call)
4. Calculates completeness rate against ≥95% threshold
5. Generates 4 visualization figures for analysis

### Success Criteria
- **Primary:** Completeness rate ≥95% across all 20 trace files
- **Secondary:** 
  - Both h-e1 and h-m1 failure traces present and readable
  - Per-file completeness distribution analyzed
  - Natural language content validated (≥10 words)

### Gate Type
**MUST_WORK** - Failure blocks all downstream hypotheses (H-M1 through H-M4)

---

## Problem Statement

### Background
Research pipelines using MCP tool-calling architecture require validation that trace data is complete and contains sufficient natural language content for semantic analysis. Without validated trace completeness, downstream NLP-based constraint inference (Layers 2/3) cannot proceed.

### Current Limitations
- No existing tools for MCP trace validation in research pipelines
- Unknown whether MCP SDK logging captures all tool interactions
- Uncertain if traces contain sufficient NL content for semantic extraction

### Target Users
- Research pipeline developers
- Hypothesis validation system operators
- Future H-M1 through H-M4 implementers

---

## Functional Requirements

### FR-1: MCP Trace Collection
**Priority:** P0 (Critical)  
**Description:** Collect 20 MCP trace files from real YouRA pipeline executions

**Acceptance Criteria:**
- 10 successful pipeline execution traces
- 10 failed pipeline execution traces (including h-e1 and h-m1 failures)
- All traces in JSON Lines (JSONL) format
- Traces stored in `{research_folder}/mcp_traces/` directory
- Each trace file named with execution ID and outcome (success/fail)

**Dependencies:** None

---

### FR-2: JSONL Trace Parser
**Priority:** P0 (Critical)  
**Description:** Parse JSONL trace files into structured tool call records

**Acceptance Criteria:**
- Handle malformed lines gracefully (skip with warning)
- Extract tool_name, parameters, result fields
- Support streaming for large trace files
- Return list of tool call dictionaries per trace
- Log parsing errors without crashing

**Dependencies:** FR-1

**Implementation Notes:**
```python
# Core parsing logic
import json

def parse_trace(trace_file_path):
    tool_calls = []
    with open(trace_file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                tool_call = json.loads(line)
                tool_calls.append(tool_call)
            except json.JSONDecodeError as e:
                print(f"Warning: Line {line_num} malformed - {e}")
    return tool_calls
```

---

### FR-3: Completeness Validator
**Priority:** P0 (Critical)  
**Description:** Validate each tool call record for field presence and NL content

**Acceptance Criteria:**
- Check required fields: tool_name, parameters, result
- Validate parameters contains non-empty dictionary
- Validate result contains non-null value
- Count words in parameters (extract string values)
- Count words in result (convert to string if needed)
- Return True if ≥10 total words, False otherwise

**Dependencies:** FR-2

**Implementation Notes:**
```python
def validate_trace_completeness(tool_call):
    required_fields = ['tool_name', 'parameters', 'result']
    
    # Field presence check
    for field in required_fields:
        if field not in tool_call or tool_call[field] is None:
            return False
    
    # Non-empty check
    if not tool_call['parameters'] or len(tool_call['parameters']) == 0:
        return False
    
    # Natural language content check
    param_text = ' '.join(str(v) for v in tool_call['parameters'].values() if isinstance(v, str))
    param_words = len(param_text.split())
    
    result_text = str(tool_call['result']) if not isinstance(tool_call['result'], dict) else ' '.join(str(v) for v in tool_call['result'].values())
    result_words = len(result_text.split())
    
    return (param_words + result_words) >= 10
```

---

### FR-4: Completeness Rate Calculator
**Priority:** P0 (Critical)  
**Description:** Calculate overall completeness rate across all traces

**Acceptance Criteria:**
- Iterate through all tool calls from all 20 traces
- Count total tool calls
- Count complete tool calls (validated True)
- Calculate rate = complete / total
- Return floating point value [0, 1]

**Dependencies:** FR-3

---

### FR-5: Per-File Analysis
**Priority:** P1 (High)  
**Description:** Calculate completeness rate per trace file

**Acceptance Criteria:**
- Calculate completeness for each of 20 traces separately
- Track min/max/mean per-file rates
- Identify outlier traces (completeness <80%)
- Associate completeness with execution outcome (success/fail)

**Dependencies:** FR-4

---

### FR-6: Failure Trace Verification
**Priority:** P0 (Critical)  
**Description:** Verify h-e1 and h-m1 failure traces are present

**Acceptance Criteria:**
- Search trace filenames for 'h-e1' or 'h_e1'
- Search trace filenames for 'h-m1' or 'h_m1'
- Both traces must have outcome='fail'
- Both traces must parse successfully
- Report presence status in evaluation results

**Dependencies:** FR-2

---

### FR-7: Evaluation Metrics
**Priority:** P0 (Critical)  
**Description:** Generate evaluation report with all success criteria

**Acceptance Criteria:**
- Primary metric: completeness_rate (float)
- Threshold: 0.95
- Primary pass/fail: boolean
- Per-file statistics: min, max, mean
- Failure trace presence: h_e1_present, h_m1_present (boolean)
- Gate decision: PASS if all criteria met

**Dependencies:** FR-4, FR-5, FR-6

**Implementation Notes:**
```python
def evaluate_h_e1(traces):
    completeness_rate = calculate_completeness_rate(traces)
    primary_pass = completeness_rate >= 0.95
    
    per_file_rates = [
        sum(validate_trace_completeness(tc) for tc in trace['tool_calls']) / len(trace['tool_calls'])
        for trace in traces if len(trace['tool_calls']) > 0
    ]
    
    failure_traces = [t for t in traces if t['outcome'] == 'fail']
    h_e1_present = any('h-e1' in t['file'] or 'h_e1' in t['file'] for t in failure_traces)
    h_m1_present = any('h-m1' in t['file'] or 'h_m1' in t['file'] for t in failure_traces)
    
    return {
        'completeness_rate': completeness_rate,
        'threshold': 0.95,
        'primary_pass': primary_pass,
        'per_file_min': min(per_file_rates),
        'per_file_max': max(per_file_rates),
        'per_file_mean': sum(per_file_rates) / len(per_file_rates),
        'h_e1_present': h_e1_present,
        'h_m1_present': h_m1_present,
        'gate_passed': primary_pass and h_e1_present and h_m1_present
    }
```

---

### FR-8: Figure 1 - Gate Metrics Comparison
**Priority:** P0 (Critical)  
**Description:** Bar chart comparing target vs actual completeness

**Acceptance Criteria:**
- X-axis: Metric (Completeness Rate)
- Y-axis: Percentage [0, 100]
- Two bars: Target (95%), Actual (measured)
- Threshold line at 95%
- Color: Green if pass, Red if fail
- Save to `{hypothesis_folder}/figures/fig1_gate_metrics.png`

**Dependencies:** FR-7

---

### FR-9: Figure 2 - Per-File Distribution
**Priority:** P1 (High)  
**Description:** Histogram of completeness rates for 20 trace files

**Acceptance Criteria:**
- X-axis: Trace file index [1-20]
- Y-axis: Completeness rate [0, 1]
- Color: Green for successful executions, Red for failed
- Mean line overlay
- Save to `{hypothesis_folder}/figures/fig2_per_file.png`

**Dependencies:** FR-5

---

### FR-10: Figure 3 - Completeness Breakdown
**Priority:** P1 (High)  
**Description:** Stacked bar chart of complete vs incomplete calls

**Acceptance Criteria:**
- Categories: Complete vs Incomplete tool calls
- Group by: Successful vs Failed executions
- Show counts (not percentages)
- Save to `{hypothesis_folder}/figures/fig3_breakdown.png`

**Dependencies:** FR-5

---

### FR-11: Figure 4 - NL Content Analysis
**Priority:** P2 (Medium)  
**Description:** Scatter plot of word counts per tool call

**Acceptance Criteria:**
- X-axis: Tool call index
- Y-axis: Word count (parameters + results)
- Threshold line at 10 words
- Color by completeness status
- Save to `{hypothesis_folder}/figures/fig4_nl_content.png`

**Dependencies:** FR-3

---

### FR-12: Main Execution Script
**Priority:** P0 (Critical)  
**Description:** End-to-end script orchestrating all components

**Acceptance Criteria:**
- Load all 20 traces from `{research_folder}/mcp_traces/`
- Parse with error handling
- Validate completeness
- Calculate all metrics
- Generate all 4 figures
- Save evaluation results to `{hypothesis_folder}/h_e1_results.json`
- Print summary to console

**Dependencies:** FR-1 through FR-11

---

## Non-Functional Requirements

### NFR-1: Performance
- Parse and validate 20 trace files in <5 minutes
- Handle traces with up to 1000 tool calls each
- Memory usage <500MB

### NFR-2: Reliability
- Graceful handling of malformed JSONL lines
- No crashes on missing fields
- Warning logs for parsing errors

### NFR-3: Maintainability
- Modular code structure (separate parser, validator, evaluator, visualizer)
- Clear function names and docstrings
- Type hints for all public functions

### NFR-4: Usability
- Console output shows progress (e.g., "Processing trace 5/20...")
- Final summary displays all metrics
- Clear pass/fail indication

---

## Data Requirements

### Input Data
**Dataset:** MCP Trace Logs (custom)
- **Location:** `{research_folder}/mcp_traces/`
- **Format:** JSON Lines (JSONL)
- **Size:** 20 files (10 success, 10 fail)
- **Structure:** Each line = one tool call with fields:
  - tool_name (string)
  - parameters (dict)
  - result (any)

**Ground Truth:**
- Execution outcomes (success/fail) encoded in filenames
- No manual annotations required

### Output Data
**Evaluation Results:**
- **File:** `{hypothesis_folder}/h_e1_results.json`
- **Format:** JSON
- **Schema:** See FR-7 implementation notes

**Figures:**
- **Directory:** `{hypothesis_folder}/figures/`
- **Files:** fig1_gate_metrics.png, fig2_per_file.png, fig3_breakdown.png, fig4_nl_content.png
- **Format:** PNG (300 DPI)

---

## Dependencies

### Python Libraries
- `json` (standard library) - JSONL parsing
- `pathlib` (standard library) - File system operations
- `matplotlib` (external) - Figure generation
- `numpy` (external) - Statistical calculations

### System Requirements
- Python 3.8+
- 500MB disk space (for traces + figures)
- No GPU required (data validation task)

---

## Implementation Modules

### Module 1: trace_parser.py
- Functions: `parse_trace(file_path)`, `load_all_traces(folder_path)`
- Responsibility: JSONL parsing with error handling

### Module 2: completeness_validator.py
- Functions: `validate_trace_completeness(tool_call)`, `calculate_completeness_rate(traces)`
- Responsibility: Field presence and NL content validation

### Module 3: evaluator.py
- Functions: `evaluate_h_e1(traces)`, `per_file_analysis(traces)`
- Responsibility: Metrics calculation and gate decision

### Module 4: visualizer.py
- Functions: `plot_gate_metrics()`, `plot_per_file()`, `plot_breakdown()`, `plot_nl_content()`
- Responsibility: All 4 figure generation

### Module 5: main.py
- Functions: `main()`
- Responsibility: Orchestration and console output

---

## Success Metrics

### Gate Condition (MUST_WORK)
✅ **PASS** if:
- Completeness rate ≥ 95%
- h-e1 failure trace present and readable
- h-m1 failure trace present and readable

❌ **FAIL** if any condition not met → STOP pipeline, enhance logging, re-collect

### Deliverables Checklist
- [ ] 5 Python modules implemented
- [ ] All 12 functional requirements satisfied
- [ ] 4 figures generated
- [ ] Evaluation results JSON file created
- [ ] Console summary printed
- [ ] Gate decision determined

---

## Timeline Estimate

**Total Effort:** 6-8 hours

| Task | Effort |
|------|--------|
| FR-1: Trace collection | 2 hours |
| FR-2: Parser implementation | 1 hour |
| FR-3-4: Validator implementation | 1.5 hours |
| FR-5-7: Evaluator implementation | 1.5 hours |
| FR-8-11: Visualizer implementation | 2 hours |
| FR-12: Main script + testing | 1 hour |

---

## Risks and Mitigations

### Risk 1: Trace Incompleteness
**Probability:** Medium  
**Impact:** High (blocks hypothesis)  
**Mitigation:** M1 - Enhanced MCP trace logging wrappers before collection  
**Residual:** Low (after applying M1)

### Risk 2: Malformed JSONL
**Probability:** Low  
**Impact:** Medium  
**Mitigation:** Robust error handling in parser (FR-2)  
**Residual:** Very Low

### Risk 3: Missing Failure Traces
**Probability:** Low  
**Impact:** High  
**Mitigation:** Verify h-e1/h-m1 traces present before starting (FR-6)  
**Residual:** Very Low

---

## Appendix A: Phase 2C Mapping

| Phase 2C Item | PRD Requirement |
|---------------|-----------------|
| Dataset: MCP Trace Logs | FR-1 (Trace Collection) |
| Models: N/A (data validation) | No ML model requirements |
| Primary Metric: Completeness Rate | FR-4, FR-7 |
| Secondary Metrics: Per-file, NL presence | FR-5, FR-6 |
| Figure 1 (Gate Metrics) | FR-8 |
| Figure 2 (Per-file Distribution) | FR-9 |
| Figure 3 (Breakdown) | FR-10 |
| Figure 4 (NL Content) | FR-11 |
| Evaluation Protocol | FR-7, FR-12 |

---

## Appendix B: File Structure

```
{hypothesis_folder}/
├── 02c_experiment_brief.md (input from Phase 2C)
├── 03_prd.md (this document)
├── h_e1_results.json (output from FR-12)
└── figures/
    ├── fig1_gate_metrics.png
    ├── fig2_per_file.png
    ├── fig3_breakdown.png
    └── fig4_nl_content.png

{research_folder}/mcp_traces/
├── success_001.jsonl
├── success_002.jsonl
├── ...
├── fail_h-e1_001.jsonl
├── fail_h-m1_001.jsonl
└── ... (20 total)
```

---

**Document Status:** Ready for Phase 3 Architecture Design  
**Next Step:** Architecture Agent (Step 3) - Design module structure and Epic-level tasks
