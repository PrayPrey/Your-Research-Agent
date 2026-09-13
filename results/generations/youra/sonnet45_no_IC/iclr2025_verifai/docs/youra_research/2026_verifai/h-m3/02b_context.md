# Hypothesis Context: h-m3

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-14
**Main Hypothesis:** Zero-Training Pipeline Validation via Multi-Layer MCP Trace Analysis
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under constraint inference via assumption-evidence comparison, if we compare assumptions extracted from early-phase tool calls (Phase 1-3 queries) against claims extracted from later-phase results (Phase 4-6 outputs), then we can detect ≥70% of actual assumption-evidence mismatches (e.g., 'effective rank decreases' assumption vs 'effective rank increased 6.02%' claim) using semantic similarity scoring with a threshold of <0.3 for contradictions, because related concepts share terminological overlap even when contradictory.

### Type
MECHANISM (Step 3 of causal chain)

### Rationale
This hypothesis tests the core constraint inference mechanism that enables zero-training validation. After h-m2 validates that LLM extraction achieves ≥80% recall/≥70% precision, h-m3 verifies that comparing extracted assumptions against extracted claims can detect semantic contradictions (mismatches). Success proves the causal step: reliable extraction → constraint inference via semantic matching.

---

## Verification Protocol

### Conceptual Test
1. Extract assumptions from early-phase tool calls (Phase 1-3) using H-M2 validated methods
2. Extract claims from later-phase results (Phase 4-6) using H-M2 validated methods
3. Compute semantic similarity for all (assumption, claim) pairs using sentence transformers
4. Flag pairs with similarity <0.3 as potential contradictions
5. Validate against ground truth (h-e1, h-m1 known mismatches); compute recall and FP rate

### Success Criteria
- **Primary:** Mismatch detection recall ≥70% (catches most contradictions)
- **Secondary:** h-e1 and h-m1 failures correctly identified via assumption-evidence mismatch
- **Secondary:** False positive rate <30% (not flagging benign differences)

### Variables
- **Independent Variable:** Semantic Similarity Threshold (threshold below which pairs are flagged as contradictions, range [0, 1])
- **Independent Variable:** Phase Pairing Strategy (all-pairs vs sequential-only Phase N → Phase N+1)
- **Dependent Variable:** Mismatch Detection Recall (% of ground-truth contradictions detected)
- **Controlled Variables:** Ground Truth Annotations (human-labeled contradictions from h-e1 and h-m1 failure cases), Semantic Embedding Model (same sentence-transformer model for all comparisons)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** YouRA Research Pipeline Execution Traces
- **Type:** custom (real MCP traces from this pipeline)
- **Source:** Real MCP trace logs from YouRA pipeline executions
- **Path:** {research_folder}/mcp_traces/*.jsonl
- **Hypothesis Fit:** Uses actual research pipeline traces including two known failures (h-e1, h-m1) from the failure history. Provides ground truth outcomes (success/fail) and real MCP tool calls with natural language queries and results. Dataset size: 20 executions (10 success, 10 fail) provides statistical power for Fisher's exact test while remaining manually traceable for validation.

### Selected Model
- **Name:** Pre-trained LLM for NLP Analysis + Sentence Transformer for Semantic Similarity
- **Type:** Commercial API (GPT-4 or Claude Sonnet) for extraction, sentence-transformers library for similarity
- **Source:** OpenAI API / Anthropic API for extraction, Hugging Face transformers for similarity
- **Hypothesis Fit:** Layers 2/3 require semantic NLP to extract assumptions (from query text) and claims (from result text). Pre-trained LLMs are established for this task (no custom training required, satisfying zero-training constraint from Ahn et al. approach). Sentence transformers compute semantic similarity between text pairs for contradiction detection.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For h-m3 (MECHANISM), baseline context helps understand expected improvements.

### Baseline Methods
- **Layer 1 Only (Syntactic):** Estimated 30-50% failure coverage (syntactic only, from Prof. Pax's assessment)
- **Manual Test Suite:** High precision/recall but requires human effort (NOT zero-annotation)
- **No Validation (Control):** Random prediction baseline - 50% precision/recall expected for 10/10 success/fail split

### Baseline Performance
Layer 1 syntactic validation catches 30-50% of failures (schema errors, type mismatches). Remaining 50-70% are semantic failures (reasoning contradictions) that require Layers 2/3.

### Gap Analysis
h-m3 addresses the gap between syntactic validation (Layer 1) and end-to-end validation (h-m4). By detecting assumption-evidence mismatches via semantic similarity, h-m3 enables Layer 2/3 to catch semantic failures that pass type checks but fail empirically.

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-m2 (Semantic NLP Extraction Effectiveness):** MUST_WORK gate PASSED
  - h-m2 validated that LLM extraction achieves ≥80% recall, ≥70% precision, ≥70% Kappa
  - Proven components from h-m2: Multi-vote LLM extraction, engineered prompts, stratified sampling
  - Optimal configuration: Claude Sonnet 4.5, temp=0.0, 3-vote consensus, ≥2/3 threshold

### Gate Information

**Gate Type:** SHOULD_WORK
- SHOULD_WORK: Failure documented as limitation, workflow continues with reduced target
- Acceptable threshold: ≥60% detection (relaxed from ≥70% primary target)

**Consequence if Fails:** Revise approach (not fatal) - may need synonym expansion, ontology layer, or threshold tuning

**Phase Assignment:** Phase 3 (Constraint Inference)

**Estimated Duration:** 1.5 weeks

---

## Dependency Context

### Relationship to Other Hypotheses

**h-m3 position in causal chain:**
1. ✅ h-e1: Trace data exists (97.48% completeness)
2. ✅ h-m1: NL content captured (97.48% presence)
3. ✅ h-m2: Extraction reliable (86.3% precision, 82.7% recall, 71.6% Kappa)
4. **→ h-m3: Constraint inference works (≥70% mismatch detection)** ← CURRENT
5. h-m4: Violations correlate with failures (≥70% recall, ≥80% precision, p<0.05)

**h-m3 enables:**
- h-m4 end-to-end validation (requires constraint matching to detect violations)
- Three-layer framework integration (syntactic + semantic-query + semantic-result)

**h-m3 builds on:**
- h-m2 extraction method (reuse prompts, multi-vote, stratified sampling)
- h-e1/h-m1 ground truth failures (known mismatches for validation)

---

## Previous Hypothesis Results (h-m2)

### Proven Components from h-m2
1. **Multi-Vote LLM Extraction:**
   - 3-vote consensus with ≥2/3 agreement threshold
   - Claude Sonnet 4.5, temperature 0.0 (deterministic)
   - Precision 86.3%, Recall 82.7%, Kappa 71.6%

2. **Engineered Prompts:**
   - Few-shot examples for assumption extraction (from queries)
   - Few-shot examples for claim extraction (from results)
   - Both achieve comparable performance (Assumptions: 86.1%/82.5%, Claims: 86.5%/82.9%)

3. **Stratified Sampling:**
   - Sample selection by outcome (success/fail) and tool-type (research/data/other)
   - Ensures representative coverage across 20 traces

### Lessons Learned from h-m2
- LLM extraction is effective but not perfect (13.7% hallucination, 17.3% miss rate)
- Multi-vote consensus reduces hallucinations
- Extraction quality is sufficient for downstream constraint inference (h-m3)

### Optimal Configuration (Carry Forward to h-m3)
- LLM: Claude Sonnet 4.5
- Temperature: 0.0
- Multi-vote: 3 iterations
- Consensus: ≥2/3 agreement
- Prompts: Reuse h-m2 assumption/claim prompts

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** h-m3 IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions (SHOULD_WORK, ≥60% acceptable)
3. Dependency information (h-m2 validated extraction)
4. Success criteria (≥70% mismatch detection, <30% FP rate)
5. Proven components from h-m2 (extraction method, prompts, sampling)

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for semantic similarity implementation patterns (Archon, Exa MCP)
3. Use h-m2 extraction method as baseline
4. Design constraint inference experiment (Level 1.5)
5. Output: h-m3/02c_experiment_brief.md

**Baseline Usage:**
- h-m3 (MECHANISM): Baseline = h-m2 extraction quality (86.3%/82.7%)
- h-m3 improvement = detecting contradictions among extracted items
- Success = ≥70% of ground-truth mismatches detected

---

*Optimized for single-hypothesis experiment design*
