# Phase 2B - Verification Planning Validation Checklist

## Step Execution Tracking (11 Steps)

### Step 0: Init Environment
- [ ] MCP Services verified:
  - [ ] Archon MCP available
  - [ ] ClearThought MCP available
  - [ ] Exa MCP available
- [ ] **Pipeline Status Check (Archon)**
  - [ ] Pipeline Project found using `pipeline_project_title`
  - [ ] Phase 2B Task verified as "doing" status
  - [ ] pipeline_ids stored (project_id, phase2b_task_id, phase2c_task_id)
- [ ] Menu [A] [P] [C] presented and handled

### Step 1: Init Parsing
- [ ] Phase 2A Dialogue output located (03_refinement.yaml)
- [ ] **Structured Parsing completed:**
  - [ ] Section 0: Established Facts & Claim Scope
  - [ ] Section 0.5: Cross-Domain Transfer Summary (OPTIONAL)
  - [ ] Section 1: Core Statement, Variables, Causal Mechanism
  - [ ] Section 2: Experimental Setup (Dataset + Model)
  - [ ] Section 3-5: Contribution, Related Work, Phase 2B Readiness
- [ ] `{{causal_chain_count}}` detected (2-5 steps)
- [ ] `{{condition_requires_verification}}` determined
- [ ] `{{requires_transfer_validation}}` determined
- [ ] Research mode set (incremental/comprehensive)
- [ ] Menu [A] [P] [C] presented and handled

### Step 2: Input Hypothesis
- [ ] **Incremental Mode:**
  - [ ] Extracted Phase 2A information displayed
  - [ ] User confirmed or corrected data
  - [ ] Experimental Setup verified
- [ ] **Comprehensive Mode:**
  - [ ] Hypothesis input method selected
  - [ ] Hypothesis title collected
  - [ ] Extension depth selected
- [ ] Placeholders filled: hypothesis_title, extension_depth, initial_hypothesis
- [ ] Menu [A] [P] [C] presented and handled

### Step 3: Hypothesis Generation
- [ ] **Scope Reduction applied (Phase 2A)**
  - [ ] PROVE NEW claims identified
  - [ ] BUILD ON claims skipped
- [ ] **Condition Hypotheses Decision**
  - [ ] User asked if `{{condition_requires_verification}}` true
  - [ ] `{{include_condition_hypotheses}}` set
- [ ] **MCP Scientific Method calls:**
  - [ ] Incremental: 1-3 calls
  - [ ] Comprehensive: 3-5 calls
- [ ] Menu [A] [P] [C] presented and handled

### Step 4: Hypothesis Inventory
- [ ] **Hypothesis Specifications (Streamlined Format):**
  - [ ] Each hypothesis: 40-50 lines
  - [ ] Rationale: 2-3 sentences
  - [ ] Verification Protocol: 1 sentence per step
- [ ] Hypothesis inventory table generated
- [ ] Total hypotheses: 3-7 (incremental) or 8-13 (comprehensive)
- [ ] Placeholders filled: hypothesis_inventory, existence_hypotheses, mechanism_hypotheses
- [ ] Menu [A] [P] [C] presented and handled

### Step 5: Risk Analysis (NEW)
- [ ] Assumptions A1-A5 mapped to risks
- [ ] Risk-hypothesis mapping complete
- [ ] Mitigation strategies defined
- [ ] Risk summary table generated
- [ ] Placeholders filled: risk_analysis, mitigation_strategies
- [ ] Menu [A] [P] [C] presented and handled

### Step 6: Dependency Graph
- [ ] Dependency analysis completed
- [ ] **DAG Visualization generated (ASCII)**
  - [ ] Level 0 (Root): H-E1
  - [ ] Level 1-N: H-M1 through H-M{{causal_chain_count}}
  - [ ] Level N+1: H-C if applicable
- [ ] Verification phases defined with gate conditions
- [ ] Menu [A] [P] [C] presented and handled

### Step 7: Timeline Planning
- [ ] **Gantt Timeline generated (ASCII)**
  - [ ] Phases on Y-axis, weeks on X-axis
  - [ ] Gate decision points marked (◆)
- [ ] Critical path analysis completed
- [ ] Resource summary created
- [ ] Placeholders filled: dependency_graph, critical_path_analysis
- [ ] Menu [A] [P] [C] presented and handled

### Step 8: Dialectical Analysis (NEW)
- [ ] Thesis statement from main hypothesis
- [ ] Antithesis from H0 (null hypothesis)
- [ ] Synthesis with balanced evaluation
- [ ] Robustness assessment table
- [ ] Placeholders filled: dialectical_analysis
- [ ] Menu [A] [P] [C] presented and handled

### Step 9: Summary
- [ ] **Executive Summary (Bullet-Point Format)**
  - [ ] ~10 lines, bullet points
- [ ] **Conclusions with Subsections:**
  - [ ] Key Achievements (~3 lines)
  - [ ] Verification Execution Order
  - [ ] Critical Decision Points
  - [ ] Open Questions (~5 lines)
  - [ ] Recommendations
- [ ] **Appendices (~10 lines)**
- [ ] Placeholders filled: executive_summary, final_summary, appendices
- [ ] Menu [A] [P] [C] presented and handled

### Step 10: Finalize
- [ ] **verification_state.yaml created**
  - [ ] Template loaded
  - [ ] Pipeline Project ID retrieved
  - [ ] sub_hypotheses built
  - [ ] All metadata filled
- [ ] **Hypothesis Tasks created (Archon)**
  - [ ] Task per hypothesis
  - [ ] hypothesis_task_mapping stored
- [ ] **Pipeline Task Update**
  - [ ] Phase 2B → done
  - [ ] Phase 2C → doing
- [ ] Final menu [R] [P] [Q] presented

---

## Pre-Execution Checks

- [ ] Phase 2A Dialogue output exists (03_refinement.yaml) for incremental mode
- [ ] MCP servers available (Archon, ClearThought, Exa)

---

## Archon Pipeline Integration

### Pipeline Verification (Step 0)
- [ ] Pipeline Project found with exact `pipeline_project_title`
- [ ] Phase 2B Task status = doing
- [ ] pipeline_ids stored for Step 10

### Hypothesis Task Creation (Step 10)
- [ ] Task created per hypothesis (H-E1, H-M1, etc.)
- [ ] hypothesis_task_mapping stored in verification_state.yaml

### Pipeline Completion (Step 10)
- [ ] Phase 2B Task → done
- [ ] Phase 2C Task → doing

---

## BMAD v6 Compliance

### Workflow File
- [ ] YAML frontmatter present (name, description, web_bundle)
- [ ] Partnership Role format used
- [ ] Core Principles, Step Processing Rules, Critical Rules included
- [ ] YouRA-Specific Rules as subsection

### Step Files
- [ ] Task References in frontmatter (advancedElicitationTask, partyModeWorkflow)
- [ ] Universal Rules include communication_language rule
- [ ] Menu pattern: [A] Advanced Elicitation [P] Party Mode [C] Continue
- [ ] Menu Handling Logic section present
- [ ] SUCCESS/FAILURE metrics at end

---

## Phase 2C Integration Readiness

### verification_state.yaml
- [ ] File created in {research_output_path}
- [ ] All hypotheses included
- [ ] Gate conditions correctly mapped
- [ ] YAML structure valid

### Hypothesis Tasks (Archon)
- [ ] Task created per hypothesis
- [ ] hypothesis_task_mapping stored

---

## Critical Failures (Immediate Fix Required)

- [ ] Pipeline verification skipped
- [ ] MCP scientific method calls skipped
- [ ] Assuming fixed 3-step causal chain
- [ ] Skipping condition hypotheses decision
- [ ] Missing DAG or Gantt visualization
- [ ] verification_state.yaml not created
- [ ] Hypothesis tasks not created
- [ ] Pipeline not updated at completion
- [ ] Missing risk analysis (Step 5)
- [ ] Missing dialectical analysis (Step 8)

---

## Validation Summary

**Total Steps:** 11 (step-00 through step-10)
**New Steps:** step-05-risk-analysis, step-08-dialectical-analysis
**MANDATORY:** All steps required

**Minimum Pass Criteria:**
- All 11 steps completed
- Pipeline verified and updated
- MCP scientific method calls made
- verification_state.yaml created
- Hypothesis tasks created in Archon
- Both visualizations (DAG + Gantt) included
- Risk Analysis and Dialectical Analysis complete

---

**Validation Result:**
- ✅ PASS: All checklist items passed
- ⚠️ PASS WITH WARNINGS: Some improvements needed
- ❌ FAIL: Critical failures detected

**Reviewer:** _____________
**Date:** {{date}}
**Validator:** Phase 2B Planning Workflow (YouRA - BMAD v6)
