# Per-Hypothesis Context: H-M1

**Generated:** 2026-07-14
**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Status:** IN_PROGRESS

---

## Hypothesis Information

### Statement
Under MCP trace logging with configurable granularity, if we inspect the 20 collected trace files, then ≥90% of tool call records will contain natural language content in either query parameters OR result content (not just function names and types), because MCP traces are designed to capture the full context of tool interactions including text-based queries and returned documents.

### Type & Rationale
**Type:** MECHANISM (Step 1 of causal chain)

This is the first causal step validating that MCP traces contain the raw material (natural language text) needed for semantic analysis in subsequent hypotheses (H-M2, H-M3, H-M4).

### Success Criteria
- **Primary:** ≥90% of tool calls contain ≥10 words of natural language text
- **Secondary:** Both query parameters AND result content show NL presence across dataset

---

## Experimental Setup

### Dataset
**Name:** YouRA Research Pipeline Execution Traces (from H-E1 validation)
**Type:** Custom (real MCP trace logs)
**Source:** 20 MCP trace files collected in H-E1 validation
**Details:**
- 10 successful pipeline executions
- 10 failed pipeline executions
- Already validated in H-E1 with 97.48% completeness rate
- 596 total tool calls available for analysis

**Loading Information:**
- Path: `{research_folder}/mcp_traces/*.jsonl`
- Already collected and validated in H-E1 phase

### Model
**Type:** N/A (data analysis task, no ML model)
**Method:** Text extraction and word counting
- Extract query parameters from tool call records
- Extract result content from tool call records
- Count natural language words (exclude JSON keys, types, punctuation)
- Statistical analysis: percentage of calls with ≥10 NL words

### Baseline & Comparison
**Baseline:** N/A (this is a data quality check, not a model comparison)

**Expected Result:** ≥90% of tool calls contain natural language content

**Comparison Target:** Random tool calls should show consistent NL presence across:
- Query parameters (Layer 2 source)
- Result content (Layer 3 source)
- Different tool types (research vs data processing)

---

## Dependencies & Gate Conditions

### Prerequisites
- **H-E1:** MCP Trace Data Availability with Natural Language Content
  - Status: COMPLETED
  - Result: PASSED (97.48% completeness rate)
  - Output: 20 trace files with 596 tool calls

### Gate Condition
**Type:** MUST_WORK
**Condition:** ≥90% NL presence
**If Failed:** STOP - Layers 2/3 semantic NLP cannot extract assumptions/claims without text content. Would require enhanced MCP wrappers and re-collection of traces.

---

## Continuation Context

### Previous Hypothesis (H-E1)
**Status:** COMPLETED - PASSED
**Key Results:**
- Completeness rate: 97.48%
- Total traces: 20 (10 success, 10 fail)
- Total tool calls: 596
- h-e1 and h-m1 failure traces confirmed present

**Implications for H-M1:**
- All 596 tool calls from H-E1 are available for NL content analysis
- No need to collect new traces
- Can proceed directly to text extraction and word counting

### Next Hypothesis (H-M2)
**Depends on:** H-M1 passing ≥90% threshold
**Will use:** Natural language content from tool calls to extract assumptions (query text) and claims (result text) via LLM-based semantic analysis

---

## Verification Protocol

1. Load 20 trace files from H-E1 validation output
2. For each tool call record:
   - Extract query parameters (text content)
   - Extract result content (text content)
3. Count words of natural language text:
   - Exclude JSON structural keys
   - Exclude type annotations
   - Exclude punctuation-only strings
   - Count actual words (English text)
4. Calculate NL presence rate:
   - `(tool calls with ≥10 NL words) / (total tool calls) × 100%`
5. Validate ≥90% threshold
6. Analyze distribution:
   - Query vs result source split
   - Different tool types (research tools vs data processing tools)
   - Successful vs failed pipeline differences

**Expected Computation Time:** < 5 minutes (data analysis task)

---

## State Tracking

**Current Status:** IN_PROGRESS
**Phase 2C Status:** experiment_design.status = IN_PROGRESS
**Next Phase:** Phase 3 (Implementation Planning)

---

*This context file was generated from 02b_verification_plan.md Section 2.2 (H-M1 specification)*
