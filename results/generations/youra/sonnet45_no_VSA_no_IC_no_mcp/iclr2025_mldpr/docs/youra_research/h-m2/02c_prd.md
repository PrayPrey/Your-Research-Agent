# Product Requirements Document: h-m2

**Date:** 2026-08-24
**Hypothesis:** Context-aware successor graphs capture task-specific replacement paths via usage-pattern inference, providing more relevant recommendations than linear version-based succession with ≥ 70% context inference accuracy
**Phase:** 2C - Implementation Planning
**Author:** Phase 3 Planning Agent

---

## Purpose

Validate that context-aware successor graphs achieve ≥70% context inference accuracy and <50% user override rate, demonstrating task-specific replacement paths outperform linear version-based succession.

---

## Features

### F1: Python Import History Introspection
**Priority:** CRITICAL (core mechanism)
**Description:** Analyze `sys.modules` to infer user task context (classification, pretraining, robustness)
**Acceptance Criteria:**
- Pattern matching against task-specific library lists
- Return context label + confidence score
- Explicit fallback for ambiguous cases
- Achieve ≥70% accuracy on test set

### F2: Dataset Card Citation Parser
**Priority:** CRITICAL (graph construction)
**Description:** Extract successor relationships from HuggingFace dataset card descriptions
**Acceptance Criteria:**
- Parse "improved version of X" patterns
- Parse "extends X for Y task" patterns
- Return edge list with context labels
- Achieve ≥60% precision on expert validation

### F3: Context-Aware Graph Lookup
**Priority:** CRITICAL (recommendation)
**Description:** Match user context to task-specific successor edges
**Acceptance Criteria:**
- Filter graph edges by context match
- Rank by precision score
- Return None when no match found
- Outperform baseline (linear version-based succession)

### F4: Baseline System - Linear Version-Based Succession
**Priority:** CRITICAL (comparison)
**Description:** Simple string matching and version number parsing
**Acceptance Criteria:**
- Return versioned successor (e.g., "dataset-v2")
- No context awareness (same successor for all users)
- Measure as performance floor

### F5: Validation Dataset Collection
**Priority:** HIGH (evaluation)
**Description:** Labeled user task contexts for accuracy measurement
**Acceptance Criteria:**
- 500+ labeled examples
- 70/30 train/test split
- Ground truth from real HuggingFace download patterns
- Cover classification, pretraining, robustness contexts

### F6: Evaluation Metrics
**Priority:** CRITICAL (success measurement)
**Description:** Compute context accuracy, override rate, edge precision
**Acceptance Criteria:**
- Context inference accuracy on test set
- User override rate from telemetry
- Edge precision from expert validation
- Statistical test (binomial test α=0.05)

### F7: Visualization Generation
**Priority:** MEDIUM (reporting)
**Description:** Generate 4 required figures for validation report
**Acceptance Criteria:**
- Confusion matrix (context inference)
- Precision-recall curve (edge inference)
- Override rate by context type
- Successor graph visualization

---

## Non-Goals

- ML model training (this is infrastructure validation, not ML research)
- GNN-based successor ranking (future work, use simple precision scoring)
- Real-time API deployment (PoC only)
- Multi-language support (Python only)

---

## Technical Constraints

**Runtime Environment:**
- Python 3.8+
- NetworkX for graph construction
- HuggingFace API access
- Papers with Code API access

**Dependencies:**
- networkx (graph)
- requests (API)
- sklearn.metrics (evaluation)
- matplotlib (visualization)

**Data Requirements:**
- HuggingFace API: 100+ datasets with deprecation events
- Papers with Code API: citation data
- Validation dataset: 500+ labeled samples

---

## Success Metrics

**MUST_WORK Gate:**
- Context inference accuracy ≥70% (primary)
- User override rate <50% (secondary)

**If Below Threshold:**
- Context inference fails → irrelevant recommendations → adoption doesn't improve
- STOP: Blocks H-M3 and H-M4 (depend on H-M2 successor graphs)

**Expected Performance:**
- Baseline (linear version-based): ~0% context awareness
- Proposed (context-aware graphs): 70%+ accuracy

---

## Validation Protocol

**Phase 4 Implementation:**
1. Implement baseline system (linear version-based succession)
2. Implement proposed system (context-aware successor graphs)
3. Collect validation dataset (500+ labeled contexts)
4. Run context inference on test set
5. Compute metrics (accuracy, override rate, precision)
6. Generate visualizations
7. Compare proposed vs baseline

**PoC Pass Condition:**
- Code runs without error
- `proposed_accuracy > baseline_accuracy`

---

## Dependencies

**Prerequisite Hypotheses:**
- H-E1: VALIDATED (instrumentation infrastructure)

**External APIs:**
- HuggingFace Datasets Hub: https://huggingface.co/api/datasets
- Papers with Code: https://paperswithcode.com/api/v1/datasets

**Instrumentation:**
- Telemetry from H-E1 (usage pattern tracking)

---

## Risks & Mitigations

**R1: Context inference accuracy <70%**
- Mitigation: Hybrid approach (automated + explicit fallback)
- Fallback: Manual context specification UI

**R2: Edge inference precision low**
- Mitigation: Three-tier governance (automation + curator + community)
- Fallback: Manual edge curation

**R3: API rate limits**
- Mitigation: Daily scraping with caching
- Fallback: Local dataset card snapshots

---

## Appendix: Traceability

| Requirement | Phase 2B Source | Experiment Brief Section |
|-------------|----------------|-------------------------|
| Context accuracy ≥70% | 02b_verification_plan.md Section 2.2 | Evaluation (Primary Metric 1) |
| Override rate <50% | 02b_verification_plan.md Section 2.2 | Evaluation (Primary Metric 2) |
| Edge precision ≥60% | 02b_verification_plan.md Section 2.2 | Evaluation (Primary Metric 3) |
| Python import introspection | 02b_context.md Assumption A2 | Core Mechanism (Step 2) |
| Dataset card citation parsing | 02b_context.md Assumption A4 | Core Mechanism (Step 1) |
| Validation dataset 500+ samples | 02b_verification_plan.md Section 2.2 | Dataset (Validation Dataset) |

---

*PRD generated from 02c_experiment_brief.md specifications*
*Next: Architecture design (02c_architecture.md)*
