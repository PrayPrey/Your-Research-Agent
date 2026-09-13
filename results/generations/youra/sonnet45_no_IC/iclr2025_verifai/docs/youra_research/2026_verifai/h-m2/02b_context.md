# Hypothesis Context: h-m2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-14
**Main Hypothesis:** Zero-Training Pipeline Validation via Multi-Layer MCP Trace Analysis
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under Layer 2/3 semantic NLP analysis using pre-trained LLMs, if we apply assumption extraction (Layer 2) to query parameters and claim extraction (Layer 3) to result content from traces with natural language, then we can extract ≥80% of key assumptions and claims with ≥70% inter-rater agreement (when validated against human annotation), because pre-trained LLMs are effective at extracting semantic content from scientific/technical text with appropriate prompt engineering.

### Type
MECHANISM (Step 2 of causal chain)

### Rationale
This hypothesis establishes that semantic NLP extraction from MCP trace text is reliable enough to enable downstream constraint inference. Without reliable extraction (≥80% recall, ≥70% precision), the constraint matching layer (H-M3) would suffer from "garbage in, garbage out" and fail to detect assumption-evidence mismatches.

---

## Verification Protocol

### Conceptual Test
Sample 50 tool calls from H-M1 dataset (25 queries with assumption text, 25 results with claim text). Apply LLM extraction with engineered prompts to extract assumptions from query parameters and claims from result content. Human annotators independently extract assumptions/claims from the same 50 calls. Compute recall = (LLM ∩ Human) / Human and precision = (LLM ∩ Human) / LLM to measure extraction quality.

### Success Criteria
- **Primary:** Extraction recall ≥80% (LLM finds most human-identified items)
- **Secondary:** Extraction precision ≥70% (low hallucination rate)
- **Tertiary:** Inter-rater agreement ≥70% (validated against human annotation)

### Variables (if applicable)
- **Independent Variable:** LLM Prompt Design (baseline prompt vs engineered prompt with examples)
- **Dependent Variable:** Extraction Recall (% of human-identified assumptions/claims also extracted by LLM), Extraction Precision (% of LLM-extracted items validated as correct by human raters)
- **Controlled Variables:** Text Source (query parameters Layer 2 vs result content Layer 3), LLM Model (same model across all extractions)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** YouRA Research Pipeline Execution Traces (20 MCP trace files from h-m1 validation)
- **Type:** custom (real MCP traces from research pipeline)
- **Source:** Real MCP trace logs from YouRA research pipeline executions
- **Path:** {research_folder}/mcp_traces/*.jsonl (derived from h-m1 dataset)
- **Hypothesis Fit:** Dataset contains natural language content in query parameters and result text, validated by h-m1 (≥90% NL presence). Provides ground truth for extraction validation.

### Selected Model
- **Name:** Pre-trained LLM for NLP Analysis
- **Type:** Commercial API (GPT-4 or Claude Sonnet)
- **Source:** OpenAI API / Anthropic API
- **Hypothesis Fit:** Layers 2/3 require semantic NLP to extract assumptions (from query text) and claims (from result text). Pre-trained LLMs are established for this task (no custom training required, satisfying zero-training constraint from Ahn et al. approach). Model choice is controlled variable - same LLM + prompts across all analysis runs.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- Random extraction: 50% recall/precision expected (random guess)
- Keyword matching: ~60-70% recall but low precision due to false positives
- Manual human annotation: ~100% recall/precision but not zero-annotation

### Baseline Performance
No established baseline for LLM-based assumption/claim extraction from MCP traces specifically. Pre-trained LLMs on scientific text extraction tasks typically achieve 70-85% F1 score (Chen et al. NLP research).

### Gap Analysis
Key challenge: MCP trace text is conversational/technical hybrid (not pure scientific text), may reduce extraction reliability. Prompt engineering required to achieve ≥80% recall threshold.

---

## Dependencies and Gate Conditions

### Prerequisites
- h-m1 (Trace Natural Language Content Capture) MUST be validated
  - Ensures ≥90% of tool calls contain natural language text
  - Provides dataset with confirmed NL presence for extraction

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Cannot proceed with H-M3 constraint inference (garbage in, garbage out). If extraction recall <80% OR precision <70%, workflow STOPS. Mitigation: iterate prompts or switch to hybrid approach (LLM + human review).

**Phase Assignment:** Phase 2 (Core Mechanism)

**Estimated Duration:** 2-3 weeks (includes prompt engineering iteration)

---

## Dependency Context

### Relationship to Other Hypotheses
- **Depends on:** h-m1 (provides dataset with validated NL content)
- **Enables:** h-m3 (constraint inference requires reliable extraction)
- **Enables:** h-m4 (end-to-end framework quality depends on extraction layer)
- **Critical Path Bottleneck:** Longest single hypothesis validation (2-3 weeks), highest risk (R2: LLM unreliability 40%)

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (set by Phase 2C Step 01)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. **Baseline comparison targets (CRITICAL for H-CP* hypotheses)**

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: {hypothesis_folder}/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
