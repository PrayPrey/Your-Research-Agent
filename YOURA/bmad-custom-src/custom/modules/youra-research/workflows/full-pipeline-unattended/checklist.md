# Full Pipeline UNATTENDED Mode - Validation Checklist

## Step Execution Tracking

### Step 0: Initialize & Resume Detection
- [ ] **Input validation:**
  - [ ] Research idea file path parsed from user input
  - [ ] Research idea file exists and is readable
  - [ ] Research idea content loaded and stored
- [ ] **MCP servers validated (MANDATORY):**
  - [ ] Archon MCP available (project management, KB search)
  - [ ] Serena MCP available (code analysis, memory)
  - [ ] Semantic Scholar MCP available (paper search)
  - [ ] Exa MCP available (GitHub, web search)
  - [ ] ClearThought MCP available (OPTIONAL - reasoning tools)
- [ ] **Research folder determined:**
  - [ ] research_output_path from config
  - [ ] research_folder path constructed
- [ ] **Resume detection logic executed:**
  - [ ] Check verification_state.yaml for ACTIVE/COMPLETED status
  - [ ] Check current_phase for Phase 6.5/6/5 or Hypothesis Loop Complete
  - [ ] Check for 03_refinement.yaml
  - [ ] Check for discussion_log.md
  - [ ] Check for 01_targeted_research.md
  - [ ] Check for 00_brainstorm_session.md
- [ ] **Resume point determined:**
  - [ ] ALREADY_COMPLETE → Step 11 (Final Summary)
  - [ ] Phase 6.5 → Step 9
  - [ ] Phase 6 → Step 8
  - [ ] Phase 5 → Step 7
  - [ ] Hypothesis Loop Complete → Step 7
  - [ ] Phase 2C/3/4 → Step 6 (Hypothesis Loop)
  - [ ] Phase 2B → Step 5
  - [ ] Phase 2A-Dialogue → Step 3
  - [ ] Phase 1 → Step 2
  - [ ] Phase 0 → Step 1 (default)
- [ ] **Resume context loaded (if resuming):**
  - [ ] Previous state read
  - [ ] Progress displayed
  - [ ] Appropriate step executed

### Step 1: Execute Phase 0 (Brainstorm)
- [ ] **Research constraints enforced (CRITICAL):**
  - [ ] NO ideas requiring manual data generation/labeling
  - [ ] NO ideas depending on external LLM APIs (OpenAI, Anthropic)
  - [ ] PREFER existing datasets (Defects4J, etc.)
  - [ ] PREFER synthetic data or self-contained experiments
- [ ] **invoke-workflow executed:**
  - [ ] phase0_workflow path resolved
  - [ ] mode: "unattended"
  - [ ] batch_mode: true
  - [ ] research_idea_content passed
- [ ] **Output verification:**
  - [ ] `00_brainstorm_session.md` exists
  - [ ] `<phase1-input>` section present
- [ ] **Recovery on failure:**
  - [ ] Re-invoke with recovery=true (if output missing)
  - [ ] ERROR_EXIT if still missing

### Step 2: Execute Phase 1 (Research)
- [ ] **invoke-workflow executed:**
  - [ ] phase1_workflow path resolved
  - [ ] mode: "unattended"
- [ ] **Output verification:**
  - [ ] `01_targeted_research.md` exists
  - [ ] `01_targeted_research_full.md` exists
- [ ] **Recovery on failure:**
  - [ ] Re-invoke with recovery=true (if outputs missing)
  - [ ] ERROR_EXIT if still missing

### Step 3: Execute Phase 2A (Self-Contained Tikitaka Dialogue)
- [ ] **invoke-workflow executed:**
  - [ ] phase2a_workflow path resolved
  - [ ] mode: "unattended"
- [ ] **Output verification:**
  - [ ] `03_refinement.yaml` exists
  - [ ] `02_synthesis.yaml` exists
  - [ ] `01_round_table/final_opinions.yaml` exists
  - [ ] `discussion_log.md` exists with `## Final Assessments`
- [ ] **Phase 2B readiness validation:**
  - [ ] phase2b_readiness.status == "READY" in 03_refinement.yaml
  - [ ] ERROR_EXIT if status invalid
- [ ] **Recovery on failure:**
  - [ ] Re-invoke with recovery=true (if outputs missing)
  - [ ] ERROR_EXIT if still missing

### Step 4: Extract Hypothesis from Phase 2A Outputs
- [ ] **Output files located:**
  - [ ] 03_refinement.yaml parsed
  - [ ] 02_synthesis.yaml parsed
- [ ] **Validation:**
  - [ ] refinement.phase2b_readiness.status == "READY"
  - [ ] ERROR_EXIT if invalid
- [ ] **Proceed directly to Step 5 (Phase 2B)**

### Step 5: Execute Phase 2B (Planning)
- [ ] **invoke-workflow executed:**
  - [ ] phase2b_workflow path resolved
  - [ ] mode: "unattended"
- [ ] **Output verification:**
  - [ ] `02b_verification_plan.md` exists
  - [ ] `verification_state.yaml` exists
- [ ] **State file validation:**
  - [ ] Hypotheses list present
  - [ ] Dependency graph established
  - [ ] Gate configurations present
- [ ] **Recovery on failure:**
  - [ ] Re-invoke with recovery=true
  - [ ] ERROR_EXIT if still missing

### Step 6: Execute Hypothesis Loop (Phase 2C → 3 → 4)
- [ ] **Pre-invocation setup:**
  - [ ] Set execution_source = "full-pipeline" in verification_state.yaml
- [ ] **invoke-workflow executed:**
  - [ ] hypothesis_loop_workflow path resolved
  - [ ] mode: "auto" (UNATTENDED mode for hypothesis-loop)
- [ ] **Hypothesis loop handles internally (Phase 5 excluded):**
  - [ ] Loading verification_state.yaml
  - [ ] Gate validation for each hypothesis
  - [ ] Phase 2C → 3 → 4 execution (NOT Phase 5)
  - [ ] Gate result processing (PASS/PARTIAL/FAIL)
  - [ ] Serena Memory saving before routing
  - [ ] State updates and dependency management
- [ ] **Post-invocation result check (CRITICAL):**
  - [ ] DO NOT wait for user input
  - [ ] DO NOT ask "What would you like to do next?"
  - [ ] IMMEDIATELY check verification_state.yaml
- [ ] **Result routing:**
  - [ ] workflow.status == "STOPPED" → MUST_PASS_FAILURE
  - [ ] workflow.status == "ROUTED" to Phase 0 → Step 1
  - [ ] workflow.status == "ROUTED" to Phase 2A → Step 3
  - [ ] current_phase == "Hypothesis Loop Complete" → Step 7 (Phase 5)
  - [ ] workflow.status == "COMPLETED" → Step 11 (backward compat)

### Step 7: Execute Phase 5 (Baseline Comparison)
- [ ] **Pre-invocation verification:**
  - [ ] sub_hypotheses_complete == true in verification_state.yaml
  - [ ] current_phase updated to "Phase 5"
- [ ] **invoke-workflow executed:**
  - [ ] phase5_workflow path resolved
  - [ ] mode: "unattended"
- [ ] **Phase 5 handles internally:**
  - [ ] Baseline comparison for main_hypothesis
  - [ ] DETERMINES_SUCCESS gate evaluation
  - [ ] Serena Memory saving on PARTIAL
  - [ ] State updates (ROUTED or COMPLETED)
- [ ] **Post-invocation result check (CRITICAL):**
  - [ ] DO NOT wait for user input
  - [ ] IMMEDIATELY check verification_state.yaml
- [ ] **Result routing:**
  - [ ] workflow.status == "STOPPED" → MUST_PASS_FAILURE
  - [ ] workflow.status == "ROUTED" to Phase 0 → Step 1
  - [ ] workflow.status == "COMPLETED" → Step 8 (Phase 6)

### Step 8: Execute Phase 6 (Paper Writing)
- [ ] **Pre-invocation setup:**
  - [ ] current_phase updated to "Phase 6"
  - [ ] verification_state.yaml saved
- [ ] **invoke-workflow executed:**
  - [ ] phase6_workflow path resolved
  - [ ] mode: "unattended"
- [ ] **Phase 6 handles internally:**
  - [ ] Section-by-section paper generation
  - [ ] Citation verification with Semantic Scholar
  - [ ] ICML format compliance
  - [ ] Ground truth extraction (065_ground_truth.yaml)
  - [ ] Narrative blueprint design (06_narrative_blueprint.yaml)
- [ ] **Post-invocation output check:**
  - [ ] paper/06_paper.md exists
  - [ ] paper/065_ground_truth.yaml exists
- [ ] **Proceed to Phase 6.5:**
  - [ ] Display completion message
  - [ ] Continue to Step 9

### Step 9: Execute Phase 6.5 (Adversarial Review)
- [ ] **Pre-invocation setup:**
  - [ ] current_phase updated to "Phase 6.5"
  - [ ] verification_state.yaml saved
- [ ] **invoke-workflow executed:**
  - [ ] phase65_workflow path resolved
  - [ ] mode: "unattended"
- [ ] **Phase 6.5 handles internally:**
  - [ ] R1: Accuracy+Engagement review (Three-Persona: accuracy_checker, bored_reviewer, skeptical_expert)
  - [ ] Convergence check (Fatal=0, Major=0, persuasiveness_passed)
  - [ ] R2: Verification+Credibility review (if needed)
  - [ ] Final paper generation
  - [ ] human_review_notes collection (MINOR issues)
- [ ] **Post-invocation output check:**
  - [ ] paper/06_paper_final.md exists (or 06_paper.md as fallback)
  - [ ] paper/review/065_review_summary.md exists
- [ ] **Proceed to Phase 6.5.1:**
  - [ ] Display completion message
  - [ ] Continue to Step 10

### Step 10: Execute Phase 6.5.1 (Overleaf LaTeX + PDF)
- [ ] **Pre-invocation setup:**
  - [ ] current_phase updated to "Phase 6.5.1"
  - [ ] verification_state.yaml saved
- [ ] **invoke-workflow executed:**
  - [ ] phase651_workflow path resolved
  - [ ] mode: "unattended"
- [ ] **Phase 6.5.1 handles internally:**
  - [ ] Convert 06_paper_final.md to LaTeX (ICML 2025 format)
  - [ ] Figure insertion from figure_registry.yaml
  - [ ] PDF compilation
- [ ] **Post-invocation output check:**
  - [ ] paper/overleaf/ folder created
  - [ ] paper/overleaf/main.pdf exists (or manual compilation needed)
- [ ] **Proceed to Final Summary:**
  - [ ] Display completion message
  - [ ] Continue to Step 11

### Step 11: Final Summary
- [ ] **Final state loaded:**
  - [ ] verification_state.yaml read
  - [ ] All hypothesis statuses collected
- [ ] **Statistics calculated:**
  - [ ] Total hypotheses count
  - [ ] Completed count
  - [ ] Passed count (gate.satisfied == true)
  - [ ] Failed count
- [ ] **Paper status:**
  - [ ] Paper file path displayed
  - [ ] Final paper file path displayed
  - [ ] Review summary path displayed
- [ ] **Pipeline completion:**
  - [ ] Archon Pipeline project updated (all phases = done)
  - [ ] verification_state.yaml saved (workflow.status = "COMPLETED")
  - [ ] Final summary displayed

---

## Error Handling Steps

### MUST_PASS_FAILURE
- [ ] **Triggered when:**
  - [ ] A MUST_WORK gate failed and cannot be routed
  - [ ] Critical infrastructure failure
  - [ ] Unrecoverable validation error
  - [ ] Dependency chain broken
- [ ] **Actions:**
  - [ ] State already saved (workflow.status = "STOPPED")
  - [ ] Failure summary reported to user
  - [ ] Pipeline execution ends

### ROUTING_PHASE0
- [ ] **Triggered when:**
  - [ ] Phase 4 FAIL: Fundamental flaw in approach
  - [ ] Phase 5 PARTIAL: Approach inferior to baseline
- [ ] **Actions:**
  - [ ] Serena Memory read for context (failure_{hypothesis_id}.md or phase5_failure_{hypothesis_id}.md)
  - [ ] Pipeline state reset for fresh start
  - [ ] Execution continues at Step 1 (Phase 0)

### ROUTING_PHASE2A
- [ ] **Triggered when:**
  - [ ] Phase 4 PARTIAL with max attempts reached
  - [ ] Hypothesis needs redesign
- [ ] **Actions:**
  - [ ] Serena Memory read for context (pivot_{h_id}_{new_h_id}.md)
  - [ ] Pipeline state reset for Phase 2A restart
  - [ ] Execution continues at Step 3 (Phase 2A)

### ERROR_EXIT
- [ ] **Triggered when:**
  - [ ] Phase output missing after recovery attempt
  - [ ] Unrecoverable error during execution
- [ ] **Actions:**
  - [ ] Partial state saved
  - [ ] Pipeline execution ends

### COMPLETE
- [ ] **Triggered when:**
  - [ ] All hypotheses processed successfully
  - [ ] workflow.status == "COMPLETED"
- [ ] **Actions:**
  - [ ] Archon Pipeline project updated
  - [ ] Final verification_state.yaml saved
  - [ ] Pipeline execution ends

---

## Pre-Execution Checks

### Input Validation
- [ ] Research idea file path provided
- [ ] Research idea file exists
- [ ] Research idea file readable (not empty)
- [ ] Content suitable for research pipeline

### MCP Server Availability
- [ ] Archon MCP server connected (MANDATORY)
- [ ] Serena MCP server connected (MANDATORY)
- [ ] Semantic Scholar MCP server connected (MANDATORY)
- [ ] Exa MCP server connected (MANDATORY)
- [ ] ClearThought MCP server connected (OPTIONAL)

### Research Constraints Validation
- [ ] No external LLM API dependencies in idea
- [ ] No manual data labeling requirements
- [ ] Dataset availability confirmed
- [ ] Self-contained experiment feasibility

---

## Archon Pipeline Integration

### Pipeline Project
- [ ] Pipeline project created/exists in Archon
- [ ] Project ID stored in verification_state.yaml
- [ ] Phase tasks created for tracking

### Phase Task Updates
- [ ] Phase 0 task: created → doing → done
- [ ] Phase 1 task: todo → doing → done
- [ ] Phase 2A task: todo → doing → done (now includes Variable Inference + H0 Generation)
- [ ] Phase 2B task: todo → doing → done
- [ ] Hypothesis Loop tasks: managed by hypothesis-loop workflow
- [ ] Final status: all phase tasks = done

### Pipeline Status Tracking
- [ ] workflow.status tracked in verification_state.yaml
- [ ] Current phase tracked
- [ ] Routing events recorded

---

## Gate Routing System

### Phase 4: MUST_WORK Gate (processed by hypothesis-loop)

| Result | Action | Serena Memory |
|--------|--------|---------------|
| PASS | → Continue to next hypothesis | None |
| MODIFIED | → New hypothesis H-*-v{n}, continue loop | None |
| FAIL | → Route to Phase 0 | `failure_{hypothesis_id}.md` |
| PARTIAL (max) | → Route to Phase 2A-Dialogue | `pivot_{h_id}_{new_h_id}.md` |

- [ ] Gate result processed by hypothesis-loop
- [ ] Routing correctly triggered
- [ ] Serena Memory saved before routing
- [ ] **:** After all sub-hypotheses done → EXIT to Step 7

### Phase 5: DETERMINES_SUCCESS Gate (processed by Step 7)

| Result | Action | Serena Memory |
|--------|--------|---------------|
| PASS | → COMPLETED, Phase 6 ready (Step 8) | None |
| PARTIAL | → Route to Phase 0 | `phase5_failure_{hypothesis_id}.md` |

- [ ] **:** Gate result processed by Step 7 (not hypothesis-loop)
- [ ] Routing correctly triggered
- [ ] Serena Memory saved before routing

---

## Serena Memory Usage

### Memory Writes (by hypothesis-loop)
- [ ] `failure_{hypothesis_id}.md` - Phase 4 FAIL
- [ ] `pivot_{h_id}_{new_h_id}.md` - Phase 4 PARTIAL → Phase 2A
- [ ] `phase5_failure_{hypothesis_id}.md` - Phase 5 PARTIAL

### Memory Reads (on routing)
| Target Phase | Memory File |
|--------------|-------------|
| Phase 0 | `failure_*.md` or `phase5_failure_*.md` |
| Phase 2A | `pivot_*.md` |

- [ ] Memory read performed before restart
- [ ] Context used to inform new attempt

---

## Resume Detection

### Detection Priority (Latest First) - Updated (Phase 2A-Extended removed)
1. [ ] verification_state.yaml with current_phase == "Phase 6.5"
   - → Resume: Step 9 (Phase 6.5)
2. [ ] verification_state.yaml with current_phase == "Phase 6"
   - → Resume: Step 8 (Phase 6)
3. [ ] verification_state.yaml with current_phase == "Phase 5"
   - → Resume: Step 7 (Phase 5)
4. [ ] verification_state.yaml with current_phase == "Hypothesis Loop Complete"
   - → Resume: Step 7 (Phase 5)
5. [ ] verification_state.yaml with current_phase in ["Phase 2C", "Phase 3", "Phase 4"]
   - → Resume: Step 6 (Hypothesis Loop)
6. [ ] verification_state.yaml with workflow.status == ACTIVE
   - → Resume: Hypothesis Loop or Phase 2B based on current_phase
7. [ ] 03_refinement.yaml with phase2b_readiness.status == READY
   - → Resume: Step 5 (Phase 2B)
8. [ ] 01_targeted_research.md exists
   - → Resume: Step 3 (Phase 2A)
9. [ ] 00_brainstorm_session.md exists
   - → Resume: Step 2 (Phase 1)
10. [ ] No output files
   - → Start: Step 1 (Phase 0)

### Resume Quality
- [ ] Correct resume point detected
- [ ] Previous state preserved
- [ ] No duplicate work performed
- [ ] Context maintained across sessions

---

## MCP ERROR RETRY PROTOCOL Compliance

- [ ] All MCP errors trigger retry
- [ ] 15-second delay between retry attempts
- [ ] Maximum 3 retry attempts per call
- [ ] Only skip/fail after 3 consecutive failures

---

## UNATTENDED Mode Compliance

### Definition Enforcement
```
UNATTENDED = EXECUTE_ALL_STEPS + NO_USER_CONFIRMATION
```

- [ ] All steps executed completely
- [ ] No user interaction required after start
- [ ] All phases auto-transitioned
- [ ] No user confirmations requested

### Pre-Step Self-Check (MANDATORY)
- [ ] NOT skipping any step file
- [ ] NOT skipping any MCP tool call
- [ ] NOT skipping any Task agent call
- [ ] ONLY skipping [Y/N] confirmations

### Error Handling in UNATTENDED
- [ ] Errors logged but non-blocking (unless MUST_PASS)
- [ ] Recovery attempted automatically
- [ ] workflow.execution_mode: "UNATTENDED" in state file

---

## Output Verification

### Phase Outputs

| Phase | Output File | Location | Verified |
|-------|-------------|----------|----------|
| Phase 0 | `00_brainstorm_session.md` | `{research_folder}/` | [ ] |
| Phase 1 | `01_targeted_research.md` | `{research_folder}/` | [ ] |
| Phase 1 | `01_targeted_research_full.md` | `{research_folder}/` | [ ] |
| Phase 2A | `discussion_log.md` | `{research_folder}/` | [ ] |
| Phase 2A | `03_refinement.yaml` | `{research_folder}/` | [ ] |
| Phase 2A | `02_synthesis.yaml` | `{research_folder}/` | [ ] |
| Phase 2A | `01_round_table/final_opinions.yaml` | `{research_folder}/` | [ ] |
| Phase 2B | `02b_verification_plan.md` | `{research_folder}/` | [ ] |
| Phase 2B | `verification_state.yaml` | `{research_folder}/` | [ ] |
| Per-Hypothesis | `02c_experiment_brief.md` | `{hypothesis_folder}/` | [ ] |
| Per-Hypothesis | `03_prd.md`, `03_architecture.md` | `{hypothesis_folder}/` | [ ] |
| Per-Hypothesis | `03_logic.md`, `03_config.md` | `{hypothesis_folder}/` | [ ] |
| Per-Hypothesis | `04_validation.md` | `{hypothesis_folder}/` | [ ] |
| Per-Hypothesis | `code/` folder | `{hypothesis_folder}/` | [ ] |
| Phase 5 | `05_baseline_comparison.md` | `{research_folder}/baseline_comparison/` | [ ] |
| Phase 6 | `06_paper.md` | `{research_folder}/paper/` | [ ] |
| Phase 6.5 | `06_paper_final.md` | `{research_folder}/paper/` | [ ] |
| Phase 6.5 | `065_review_summary.md` | `{research_folder}/paper/review/` | [ ] |
| Phase 6.5.1 | `overleaf/` folder | `{research_folder}/paper/` | [ ] |

### verification_state.yaml Final State
- [ ] workflow.status = "COMPLETED"
- [ ] All hypothesis statuses finalized
- [ ] Gate results recorded
- [ ] Statistics calculated

---

## Quality Gates

### Pipeline Project
- [ ] Pipeline project created in Archon
- [ ] All phase tasks tracked
- [ ] Final status recorded

### Hypothesis Processing
- [ ] At least one hypothesis reached validation
- [ ] All READY hypotheses processed
- [ ] Gate results correctly evaluated
- [ ] Routing correctly executed

### Final Summary
- [ ] Total execution time logged
- [ ] Success/failure counts accurate
- [ ] Next steps identified (if any)

---

## Critical Failures (Immediate Fix Required)

- [ ] Input file missing or unreadable at Step 0
- [ ] MCP server unavailable (Archon, Serena, Scholar, Exa)
- [ ] Research constraints violated (external API dependencies)
- [ ] Resume detection incorrect (wrong step executed)
- [ ] invoke-workflow not used for phase execution
- [ ] Step outputs not verified before proceeding
- [ ] Post-hypothesis-loop user prompt issued (UNATTENDED violation)
- [ ] Gate routing not executed on failure
- [ ] Serena Memory not read on routing
- [ ] MUST_WORK failure not stopping pipeline
- [ ] Final state not saved to verification_state.yaml

---

## Validation Summary

**Total Checks:** 150+
**Required:** Step execution + Resume detection + Gate routing + UNATTENDED compliance + Output verification
**MANDATORY Steps:** All steps (0-10) + Error Handling

**Minimum Pass Criteria:**
- All steps executed in correct order
- Resume detection working correctly
- All invoke-workflow calls executed
- Output verification after each phase
- Gate routing correctly triggered
- Serena Memory used on routing
- UNATTENDED mode maintained throughout
- Final verification_state.yaml saved

---

**Validation Result:**
- ✅ COMPLETE: All hypotheses validated, pipeline finished
- ⚠️ ROUTED: Gate failure, routing to Phase 0 or Phase 2A
- ❌ STOPPED: MUST_WORK failure, manual intervention required

**Input File:** _______________
**Resume Point:** _______________
**Phases Completed:** ___
**Hypotheses Processed:** ___
**Final Status:** _______________

**Reviewer:** _____________
**Date:** {{date}}
**Validator:** Full Pipeline UNATTENDED Workflow (YouRA)
