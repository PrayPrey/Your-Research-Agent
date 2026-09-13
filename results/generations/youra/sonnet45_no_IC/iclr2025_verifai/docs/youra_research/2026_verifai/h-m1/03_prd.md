# Product Requirements Document: H-M1 Natural Language Content Validation

**Date:** 2026-07-14
**Author:** Anonymous
**Hypothesis:** h-m1 - Trace Natural Language Content Capture (Causal Step 1)
**Type:** MECHANISM (Data Analysis)
**Gate:** MUST_WORK

---

## Executive Summary

### Purpose
Validate that MCP trace tool call records contain sufficient natural language (NL) content to support downstream semantic analysis. This is a MUST_WORK gate that blocks H-M2, H-M3, and H-M4 if failed.

### Success Criteria
- ≥90% of tool calls contain ≥10 words of natural language text
- Both query parameters AND result content show NL presence
- All 596 tool calls from H-E1 validation are analyzed

### Dependencies
- **Prerequisite:** H-E1 (MCP Trace Data Availability) - COMPLETED
- **Blocks:** H-M2 (Semantic NLP Extraction) if failed

---

## Problem Statement

### Context
The three-layer MCP trace analysis framework requires natural language content for Layers 2 and 3:
- Layer 2: Extract assumptions from query parameters (requires NL text in params)
- Layer 3: Extract claims from result content (requires NL text in results)

Without sufficient NL content, semantic NLP extraction cannot proceed.

### Current State
- H-E1 validated 97.48% trace completeness (596 tool calls)
- Unknown: What percentage of tool calls contain meaningful NL text?
- Unknown: Distribution of NL content (query vs result, tool type)

### Desired State
- Quantified NL content presence rate (≥90% threshold)
- Breakdown by source (query params, results, both)
- Statistical validation ready for Phase 4 execution

---

## Functional Requirements

### FR-1: MCP Trace Loading
**Priority:** P0 (Critical)
**Description:** Load all 20 MCP trace files from H-E1 validation
**Acceptance Criteria:**
- Read 596 tool call records from `{research_folder}/mcp_traces/*.jsonl`
- Parse JSONL format: tool_name, parameters (dict), results (dict/string)
- Validate all records loaded without errors

### FR-2: Text Content Extraction
**Priority:** P0 (Critical)
**Description:** Recursively extract all string values from tool call structures
**Acceptance Criteria:**
- Extract text from `parameters` dict (query text)
- Extract text from `results` dict/string (result content)
- Exclude JSON structural keys, preserve values only
- Handle nested dicts and lists recursively

### FR-3: Natural Language Word Counting
**Priority:** P0 (Critical)
**Description:** Count natural language words using standardized methodology
**Acceptance Criteria:**
- Pattern: Words with ≥2 alphabetic characters (`\b[a-zA-Z]{2,}\b`)
- Filter: Remove punctuation-only tokens
- Count: Total words per tool call (params + results combined)
- Threshold: Mark call as NL-present if ≥10 words

**Reference:** LAION-5B and Conceptual 12M text quality filtering methodology (Archon KB)

### FR-4: NL Presence Rate Calculation
**Priority:** P0 (Critical)
**Description:** Calculate percentage of tool calls meeting NL threshold
**Acceptance Criteria:**
- Metric: (calls with ≥10 NL words) / (total calls) × 100%
- Report: Total calls, calls with NL, percentage
- Validation: Compare against 90% threshold
- Result: PASS (≥90%) or FAIL (<90%)

### FR-5: NL Content Breakdown Analysis
**Priority:** P1 (High)
**Description:** Analyze NL distribution across sources and tool types
**Acceptance Criteria:**
- Source breakdown: Query only, Result only, Both, Neither
- Tool type breakdown: Research tools vs data processing tools
- Word count distribution: 0-5, 5-10, 10-20, 20-50, 50+ bins
- Identify low-NL outliers for investigation

### FR-6: Visualization Generation
**Priority:** P1 (High)
**Description:** Generate figures for results communication
**Acceptance Criteria:**
- Figure 1: Gate metrics comparison (actual vs 90% threshold)
- Figure 2: Word count distribution histogram
- Figure 3: NL source breakdown (stacked bar/pie chart)
- Figure 4: NL presence by tool type
- All figures saved to `{hypothesis_folder}/figures/`

### FR-7: Validation Report Generation
**Priority:** P0 (Critical)
**Description:** Generate 04_validation.md with pass/fail result
**Acceptance Criteria:**
- Gate result: PASS or FAIL (based on ≥90% threshold)
- Metrics table: NL rate, total calls, calls with NL
- Breakdown tables: Source distribution, tool type distribution
- Failure analysis if <90%
- Next steps recommendation

---

## Non-Functional Requirements

### NFR-1: Performance
- Process all 596 tool calls in <5 seconds
- Memory usage <500 MB (text extraction only)

### NFR-2: Reproducibility
- Deterministic word counting (no randomness)
- Documented regex pattern for NL word identification
- Version-controlled code and outputs

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings for public functions
- Unit tests for text extraction and word counting
- Code length: <200 lines (straightforward data processing)

### NFR-4: Error Handling
- Graceful handling of malformed JSONL lines
- Warning for unexpected tool call structures
- Fail-fast if trace files missing

---

## Data Specifications

### Input Data
**Source:** H-E1 validation outputs
**Format:** JSONL (one tool call per line)
**Location:** `{research_folder}/mcp_traces/*.jsonl`
**Volume:** 20 files, 596 tool calls total
**Fields:**
```json
{
  "tool_name": "string",
  "parameters": {/* dict with text values */},
  "results": "string or dict"
}
```

### Output Data
**File:** `{hypothesis_folder}/04_validation.md`
**Format:** Markdown with YAML frontmatter
**Required Fields:**
- `gate_result`: "PASS" or "FAIL"
- `nl_presence_rate`: float (0-100)
- `total_calls`: int
- `calls_with_nl`: int
- `threshold`: 10 (words)

**Figures:** `{hypothesis_folder}/figures/`
- `gate_metrics.png`
- `word_count_distribution.png`
- `nl_source_breakdown.png`
- `nl_by_tool_type.png`

---

## Technical Dependencies

### Required Libraries
- Python 3.8+
- `json` (stdlib) - JSONL parsing
- `re` (stdlib) - Regex word extraction
- `pathlib` (stdlib) - File path handling
- `matplotlib` - Figure generation
- `numpy` (optional) - Statistical analysis

### External Dependencies
- H-E1 trace files (prerequisite completed)
- `{research_folder}/mcp_traces/` directory with 20 .jsonl files

### No ML Dependencies
- No PyTorch/TensorFlow required (data analysis only)
- No pre-trained models required
- No GPU required

---

## Evaluation Metrics

### Primary Metrics
| Metric | Definition | Threshold | Gate |
|--------|------------|-----------|------|
| NL Presence Rate | % of calls with ≥10 NL words | ≥90% | MUST_WORK |

### Breakdown Metrics
| Metric | Definition | Purpose |
|--------|------------|---------|
| Query NL Rate | % with ≥10 words in params | Layer 2 feasibility |
| Result NL Rate | % with ≥10 words in results | Layer 3 feasibility |
| Mean Word Count | Average words per call | Distribution assessment |
| Median Word Count | Median words per call | Outlier detection |

---

## Success Criteria

### MUST_WORK Gate
**Condition:** NL presence rate ≥90%
**If PASS:**
- Proceed to H-M2 (Semantic NLP Extraction)
- Use 596 tool calls for semantic analysis
- Validate both query and result NL sources

**If FAIL:**
- STOP pipeline (blocks H-M2, H-M3, H-M4)
- Action: Enhance MCP trace logging wrappers
- Action: Re-collect traces with increased text capture
- Re-run H-E1 → H-M1 before proceeding

### Quality Checks
- ✅ Both query AND result sources show NL presence >80%
- ✅ Distribution covers all tool types (not biased to one category)
- ✅ Word count distribution shows majority >10 words
- ⚠️ If only one source (query OR result) has NL → document limitation

---

## Risks and Mitigations

### Risk R1: Trace Incompleteness (Residual from H-E1)
**Probability:** LOW (H-E1 validated 97.48%)
**Impact:** MEDIUM
**Mitigation:** Reuse H-E1 validation - already confirmed complete

### Risk R2: NL Content Below Threshold
**Probability:** MEDIUM (unknown until measured)
**Impact:** HIGH (blocks entire pipeline)
**Mitigation:** 
- M2a: If 80-90%, investigate low-NL outliers and re-evaluate threshold
- M2b: If <80%, enhance MCP wrappers per original risk mitigation M1

### Risk R3: Biased NL Distribution (e.g., only in queries, not results)
**Probability:** MEDIUM
**Impact:** MEDIUM (Layer 3 may fail even if H-M1 passes)
**Mitigation:** Report source breakdown, document limitations for H-M2/H-M3

---

## Implementation Approach

### Core Components
1. **TraceLoader:** Load JSONL files, parse tool calls
2. **TextExtractor:** Recursive dict traversal, string concatenation
3. **WordCounter:** Regex-based NL word counting
4. **MetricsCalculator:** NL rate, breakdowns, distributions
5. **Visualizer:** Generate 4 required figures
6. **ReportGenerator:** Create 04_validation.md

### Pseudo-code (from Phase 2C Experiment Brief)
```python
import json, re
from pathlib import Path

def count_nl_words(text: str) -> int:
    """Count NL words (≥2 alphabetic chars)."""
    if not isinstance(text, str):
        return 0
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
    return len(words)

def extract_text_from_dict(obj) -> str:
    """Recursively extract all string values."""
    if isinstance(obj, dict):
        return ' '.join(extract_text_from_dict(v) for v in obj.values())
    elif isinstance(obj, list):
        return ' '.join(extract_text_from_dict(item) for item in obj)
    elif isinstance(obj, str):
        return obj
    return ''

def analyze_nl_content(trace_files: list[Path]) -> dict:
    """Main analysis function."""
    total_calls = 0
    calls_with_nl = 0
    
    for trace_file in trace_files:
        with open(trace_file) as f:
            for line in f:
                call = json.loads(line)
                
                param_text = extract_text_from_dict(call.get('parameters', {}))
                result_text = extract_text_from_dict(call.get('results', {}))
                
                total_words = count_nl_words(param_text) + count_nl_words(result_text)
                
                total_calls += 1
                if total_words >= 10:
                    calls_with_nl += 1
    
    nl_rate = (calls_with_nl / total_calls) * 100 if total_calls > 0 else 0
    
    return {
        'nl_presence_rate': nl_rate,
        'total_calls': total_calls,
        'calls_with_nl': calls_with_nl,
        'threshold': 10,
        'gate_result': 'PASS' if nl_rate >= 90 else 'FAIL'
    }
```

---

## Appendix: Traceability

### Phase 2C Mapping
| Phase 2C Section | PRD Section |
|------------------|-------------|
| Dataset (MCP traces) | FR-1, Data Specifications |
| Core Mechanism (text extraction) | FR-2, FR-3 |
| Evaluation (NL rate) | FR-4, Evaluation Metrics |
| Visualization | FR-6 |
| Validation Report | FR-7 |

### Research Sources (Archon KB)
- LAION-5B: Text quality filtering methodology → FR-3
- Conceptual 12M: Statistical analysis approach → FR-5
- Diffusers code: Text processing patterns → Implementation pseudo-code

### Hypothesis Context
- **Current:** H-M1 (Data validation for NL content)
- **Prerequisite:** H-E1 (Trace availability) - COMPLETED
- **Dependent:** H-M2 (Semantic NLP extraction) - requires H-M1 PASS
- **Gate Chain:** H-M1 MUST_WORK → H-M2 MUST_WORK → H-M3 SHOULD_WORK → H-M4 DETERMINES_SUCCESS

---

## Next Phase
**Phase 4:** Coding & PoC Validation
- Implement 6 core components
- Process 596 tool calls
- Generate validation report
- Determine gate pass/fail
