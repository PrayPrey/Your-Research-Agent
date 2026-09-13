# Phase 2C Experiment Design - Validation Checklist

## Step Execution Tracking

### Step 1: Initialize and Validate State
- [ ] MCP Services verified:
  - [ ] Archon MCP (MANDATORY)
  - [ ] Exa MCP (MANDATORY)
  - [ ] Serena MCP (OPTIONAL - code analysis)
- [ ] verification_state.yaml loaded/initialized:
  - [ ] IF NOT EXISTS: Parsed from Phase 2B roadmap
  - [ ] IF EXISTS: Loaded and progress displayed
- [ ] Workflow status validated (not STOPPED)
- [ ] Hypothesis selected from available list
- [ ] Per-hypothesis context loaded/generated (JIT if needed)
- [ ] Gate conditions validated
- [ ] Previous context loaded (if continuation hypothesis)
- [ ] State updated to IN_PROGRESS
- [ ] Output file created from template

### Step 2: Archon Knowledge Base Search
- [ ] `rag_search_knowledge_base` called 2-3 times
- [ ] `rag_search_code_examples` called 1-2 times
- [ ] Queries focused (2-5 keywords)
- [ ] Results relevant and documented
- [ ] MCP ERROR RETRY PROTOCOL applied (if errors)

### Step 3: Exa GitHub Search
- [ ] `get_code_context_exa` called 1-2 times
- [ ] GitHub implementations found
- [ ] Token budget reasonable (5000 tokens)
- [ ] Results analyzed and documented
- [ ] MCP ERROR RETRY PROTOCOL applied (if errors)

### Step 4: Serena Code Analysis (CONDITIONAL)
- [ ] Serena analysis triggered appropriately (complex code only)
- [ ] `get_symbols_overview` provided structure understanding
- [ ] `find_symbol` extracted core mechanism
- [ ] `search_for_pattern` found integration points
- [ ] Analysis results used in pseudo-code
- [ ] **OR:** Serena skipped (simple code or unavailable)

### Step 5: Dataset and Baseline Specification
- [ ] Dataset specification complete:
  - [ ] Exact name provided
  - [ ] Source/download link included
  - [ ] Train/val/test splits specified
  - [ ] Preprocessing pipeline detailed
- [ ] Baseline model specified:
  - [ ] Exact architecture (e.g., ResNet-32, ViT-Small)
  - [ ] Configuration detailed
  - [ ] Source cited

### Step 6: Synthesis and Specification Generation
- [ ] Core mechanism pseudo-code generated:
  - [ ] 10-30 lines
  - [ ] Based on analyzed real code
  - [ ] Input/output dimensions documented
- [ ] Training protocol specified:
  - [ ] Optimizer with all parameters
  - [ ] Learning rate and schedule
  - [ ] Batch size and epochs
  - [ ] Loss function
  - [ ] Number of random seeds (3-5; PoC: 1 seed OK)
- [ ] Evaluation metrics defined:
  - [ ] Primary metrics
  - [ ] Success criteria from Phase 2B (PoC: "proposed > baseline")
- [ ] Ablation study designed (2-4 variants)

### Step 7: References Documentation
- [ ] All Archon sources documented
- [ ] All Exa GitHub repos documented with URLs
- [ ] Serena analysis results documented (if performed)
- [ ] Previous hypothesis context documented (if continuation)
- [ ] Code snippets included with annotations

### Step 8: Quality Validation and Completion
- [ ] All validation checks executed
- [ ] Validation results displayed
- [ ] **State file updated to COMPLETED**
- [ ] Completion event logged in history
- [ ] Statistics updated
- [ ] Final summary presented
- [ ] **Pipeline Task Update (Current Hypothesis Only):**
  - [ ] Update current hypothesis experiment_design.status = COMPLETED
  - [ ] Do NOT check other hypotheses' status

---

## Pre-Execution Checks

- [ ] Phase 2B verification plan exists (02b_verification_plan.md)
- [ ] verification_state.yaml exists or can be initialized
- [ ] MCP servers available:
  - [ ] Archon (knowledge base)
  - [ ] Exa (GitHub search)
  - [ ] Serena (code analysis - optional)

---

## Archon Pipeline Integration

### State Management
- [ ] verification_state.yaml loaded at start
- [ ] experiment_design.status updated to IN_PROGRESS
- [ ] experiment_design.status updated to COMPLETED at end
- [ ] History events logged

### Pipeline Task Update (Step 8 - Current Hypothesis Only)
- [ ] Current hypothesis experiment_design.status = COMPLETED
- [ ] Do NOT check other hypotheses' status

---

## MCP ERROR RETRY PROTOCOL Compliance

- [ ] All MCP errors trigger retry
- [ ] 15-second delay between retry attempts
- [ ] Maximum 3 retry attempts per call
- [ ] Only skip/fail after 3 consecutive failures

---

## Progressive File System (Auto-Resume)

- [ ] All `{{UNFILLED:...}}` placeholders replaced with content
- [ ] No `{{UNFILLED:...}}` markers remain in final document
- [ ] File saved after each step
- [ ] Resume capability maintained (step markers correct)

---

## Research Quality

### Sufficient Research Sources
- [ ] ≥3 Archon knowledge base results analyzed
- [ ] ≥1 Exa GitHub repository found and analyzed
- [ ] All sources relevant to hypothesis mechanism
- [ ] Sources cover dataset, model, hyperparameters

### No Speculation
- [ ] All specifications backed by research or previous results
- [ ] No "I think..." or "probably..." statements
- [ ] No unsupported assumptions
- [ ] Every design choice has a rationale

### Code Analysis Quality (if performed)
- [ ] Serena analysis performed on complex code (if needed)
- [ ] Code structure understood and documented
- [ ] Core mechanism extracted and explained
- [ ] Integration points identified

---

## Specification Completeness

### Dataset Specification
- [ ] Exact dataset name provided
- [ ] Dataset source/download link included
- [ ] Train/val/test splits specified with counts
- [ ] Preprocessing pipeline detailed (exact parameters)
- [ ] Augmentation strategies documented (if applicable)
- [ ] Rationale for dataset choice (with references)

### Baseline Model
- [ ] Exact baseline architecture specified (e.g., ResNet-32, ViT-Small)
- [ ] Baseline configuration detailed
- [ ] Source cited (which repo/paper/previous experiment)
- [ ] Rationale for baseline choice

### Proposed Model
- [ ] Architecture clearly described (Baseline + Mechanism)
- [ ] Integration point specified (which layer, where to insert)
- [ ] Input/output dimensions documented

### Core Mechanism (Level 1.5)
- [ ] Pseudo-code provided (10-30 lines)
- [ ] Key operations documented step-by-step
- [ ] Input/output dimensions specified
- [ ] Parameters documented
- [ ] Based on analyzed real code (not invented)
- [ ] Source of pseudo-code identified (which repo/code)

### Training Protocol
- [ ] Optimizer specified with all parameters
- [ ] Learning rate value provided
- [ ] Learning rate schedule specified with parameters
- [ ] Batch size specified
- [ ] Number of epochs specified
- [ ] Loss function specified
- [ ] Number of random seeds specified (3-5; PoC: 1 seed OK)
- [ ] ALL hyperparameters justified (research source or previous result)

### Evaluation
- [ ] Primary metrics defined
- [ ] Success criteria from Phase 2B (PoC: "proposed > baseline")
- [ ] Expected baseline performance provided (from research)
- [ ] All metrics traceable to Phase 2B or research

### Ablation Study
- [ ] 2-4 ablation variants defined
- [ ] Purpose of each ablation explained
- [ ] Ablations test mechanism components (not random variations)

---

## Continuation Logic (if applicable)

### Previous Context Loading
- [ ] Previous hypothesis ID identified correctly
- [ ] Phase 4 validation report loaded (if continuation)
- [ ] Optimal hyperparameters extracted from previous
- [ ] Proven stable components identified

### Reuse Strategy
- [ ] Dataset reused if proven stable (controlled experiment)
- [ ] Hyperparameters reused if optimal
- [ ] Code structure to be reused documented
- [ ] Only mechanism is new (incremental change)
- [ ] Rationale for reuse vs. new choices explained

### First Hypothesis (if applicable)
- [ ] Correctly identified as first hypothesis
- [ ] No attempt to load previous context
- [ ] All design from research (no reuse)

---

## Traceability & Documentation

### All Specifications Referenced
- [ ] Every hyperparameter traceable to source
- [ ] Dataset choice justified with reference
- [ ] Baseline model justified with reference
- [ ] Mechanism design based on cited code
- [ ] Training protocol based on cited sources

### Reference Implementations Appendix
- [ ] All Archon sources documented
- [ ] All Exa GitHub repos documented with URLs
- [ ] Serena analysis results documented (if performed)
- [ ] Previous hypothesis context documented (if continuation)
- [ ] Code snippets included with annotations
- [ ] Clear mapping: source → our specification

### Source Quality
- [ ] GitHub repos have reasonable stars/activity
- [ ] Archon sources are relevant
- [ ] Code snippets are from reliable implementations
- [ ] Previous results are from completed Phase 4 (if continuation)

---

## Level 1.5 Compliance

### Concrete Enough
- [ ] All hyperparameters are exact values (not ranges)
- [ ] Dataset is specific (not "image dataset")
- [ ] Model is specific (not "transformer model")
- [ ] Preprocessing has exact parameters
- [ ] No vague statements ("use standard settings")

### Not Too Concrete
- [ ] No complete file structure (that's Phase 3)
- [ ] No full code implementation (that's Phase 4)
- [ ] No task decomposition (that's Phase 3)
- [ ] No resource estimates (removed per design)

### Pseudo-code Quality
- [ ] 10-30 lines (not too long, not too short)
- [ ] Shows key operations (not full implementation)
- [ ] Documents input/output
- [ ] Based on real code (not invented)
- [ ] Sufficient for Phase 3 to understand mechanism

---

## Integration Readiness

### Phase 3 Compatible
- [ ] Output format matches Phase 3 expectations
- [ ] All information needed for PRD generation present
- [ ] All information needed for Architecture design present
- [ ] Mechanism clear enough to design tasks

### State File Updated
- [ ] experiment_design.status = COMPLETED
- [ ] experiment_design.file = output file path
- [ ] experiment_design.completed_at = timestamp
- [ ] History event logged

---

## UNATTENDED Mode Handling

- [ ] UNATTENDED mode checked in Step 8
- [ ] **IF UNATTENDED:**
  - [ ] Validation issues noted in output (not user prompt)
  - [ ] Workflow continues automatically
- [ ] **IF NOT UNATTENDED:**
  - [ ] User prompted for validation issues
  - [ ] User decides to fix or continue

---

## Critical Failures (Immediate Fix Required)

- [ ] MCP services not verified before proceeding
- [ ] verification_state.yaml not loaded/initialized
- [ ] MUST_WORK gate violations ignored
- [ ] State file not updated to COMPLETED at end
- [ ] Pseudo-code invented (not based on real code)
- [ ] Hyperparameters without sources
- [ ] Missing research sources (<3 total)
- [ ] No Exa GitHub results
- [ ] Current hypothesis status not updated to COMPLETED

---

## Validation Summary

**Total Checks:** 120+
**Required:** Step execution + MCP compliance + Research quality + Specification completeness + State management
**MANDATORY Steps:** Steps 1, 2, 3, 5, 6, 7, 8 | Step 4 CONDITIONAL (Serena)

**Minimum Pass Criteria:**
- All mandatory steps completed
- MCP tools used properly
- All specifications complete
- No speculation (everything referenced)
- State file updated
- Pipeline updated conditionally

---

**Validation Result:**
- ✅ PASS: All checklist items passed
- ⚠️ PASS WITH WARNINGS: Some improvements needed
- ❌ FAIL: Critical failures detected

**Quality Score:** ___ / 100%
**Execution Time:** ___ minutes
**Research Sources:** ___ total

**Reviewer:** _____________
**Date:** {{date}}
**Validator:** Phase 2C Experiment Design Workflow (YouRA)
