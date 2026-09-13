---
name: 'step-08-validation'
description: 'Validate experiment design quality and complete workflow'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2c-experiment-design'
thisStepFile: '{workflow_path}/steps/step-08-validation.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{hypothesis_folder}/02c_experiment_brief.md'

# Data References
verificationStateFile: '{research_folder}/verification_state.yaml'
validationChecklist: '{workflow_path}/checklist.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/tasks/advanced-elicitation.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 8: Quality Validation and Final Review

## STEP GOAL:

Validate the complete experiment design against quality criteria, update the verification state file to mark experiment design as COMPLETED, and present the final summary to the user. This is the FINAL step of the Phase 2C workflow.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus on validation and state update
- 🚫 FORBIDDEN to skip validation checks
- 💬 Approach: Systematic quality validation
- 📋 State file MUST be updated on completion

## EXECUTION PROTOCOLS:

- 🎯 Run all validation checks from checklist
- 💾 Update state file to mark COMPLETED
- 📖 Log completion event in history
- 🚫 Never complete without all validations passed

## CONTEXT BOUNDARIES:

- Available context: Complete output file from Steps 1-7
- Focus: Validation and state management only
- Limits: Do not modify experiment content in this step
- Dependencies: All previous steps completed

---

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Display Step Start

Display: "✅ Step 8: Validating experiment design quality..."

### 2. Run Quality Validation Checklist

Load {validationChecklist} if available, else use default checks:

**Check 1: All Hyperparameters Justified?**
- Verify: Every hyperparameter has a research source or previous result
- IF NO: Mark incomplete, note which parameters lack sources

**Check 2: Dataset Choice Justified?**
- Verify: Dataset selection explained with reference
- IF NO: Flag for review

**Check 3: Mechanism Grounded in Code?**
- Verify: Pseudo-code based on analyzed/researched code, not speculation
- IF NO: Flag for additional research needed

**Check 4: No Unsupported Assumptions?**
- Verify: All claims referenced to findings
- IF NO: List unsupported claims

**Check 5: Full Traceability?**
- Verify: All specifications traceable to sources in Appendix
- IF NO: List specs without sources

Display validation results:

```
Quality Validation Results:
───────────────────────────
✅ All hyperparameters justified
✅ Dataset choice justified
✅ Mechanism grounded in code
✅ No unsupported assumptions
✅ Full traceability

Overall: PASSED / NEEDS REVIEW
```

**IF any check fails:**
- Display specific issues
- **Check UNATTENDED mode:**
  ```python
  state = load_yaml(verification_state_file)
  is_unattended = (state.workflow.execution_mode == "UNATTENDED")
  ```
- **IF is_unattended:** Note limitations in output file and CONTINUE (do not ask user)
- **IF NOT is_unattended:** Ask user: "Address issues before completing? (Y/N)"
  - IF Y: Guide user to fix issues
  - IF N: Note limitations in output file

### 3. Update State File

Read {verificationStateFile} and update:

```yaml
# Update hypothesis status
hypotheses:
  {hypothesis_id}:
    experiment_design:
      status: "COMPLETED"
      file: "{outputFile}"
      completed_at: [NOW]

# Update workflow
workflow:
  current_phase: "Phase 2C"

# Update metadata
metadata:
  last_updated: [NOW]

# Log event
history:
  - event: "Experiment design completed"
    timestamp: [NOW]
    phase: "Phase 2C"
    hypothesis_id: {hypothesis_id}
    output_file: "{outputFile}"

# Update statistics
statistics:
  phases_completed:
    phase_2c: [increment by 1]
```

Save updated state to {verificationStateFile}.

Display: "📝 State updated: {hypothesis_id} experiment design marked COMPLETED"

### 4. Generate Final Summary

Display to user:

```
🎉 **Phase 2C Complete: Experiment Design Ready**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Hypothesis**: {hypothesis_id}
**Specification Level**: 1.5 (Concrete + Pseudo-code)

**Output File**: {outputFile}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Research Sources Used**:
- Archon Knowledge Base: {archon_query_count} queries
- Exa GitHub: {exa_repo_count} repositories
- Serena Analysis: {serena_status}
- Previous Context: {previous_context_status}

**Specifications Generated**:
✓ Dataset specification
✓ Baseline model
✓ Proposed model architecture
✓ Core mechanism pseudo-code (10-30 lines)
✓ Training protocol
✓ Evaluation metrics
✓ Ablation study design
✓ Reference implementations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Next Steps**:

→ **Phase 3**: Implementation Planning
  - Input: This experiment design ({outputFile})
  - Output: PRD, Architecture Document, Archon Tasks
  - Command: /phase3-implementation-planning

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5. Present Final Options

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [P] Proceed to Phase 3 → Phase 2C Complete</action>

Display: "**What would you like to do?** [R] Review output file [N] Start next hypothesis [P] Proceed to Phase 3 [Q] Quit"

#### Menu Handling Logic:

- IF R: Display contents of {outputFile}
- IF N: Return to Step 1 to select another hypothesis
- IF P: Provide Phase 3 command and instructions
- IF Q: Display farewell and exit

#### EXECUTION RULES:

- ALWAYS halt and wait for user input
- This is the FINAL step - no automatic progression
- User decides next action

---

## CRITICAL STEP COMPLETION NOTE

This is the **FINAL STEP** of Phase 2C workflow. The workflow is complete when:
1. All validation checks pass (or limitations documented)
2. State file updated with COMPLETED status
3. Final summary presented to user

**NO NEXT STEP FILE TO LOAD** - Workflow ends here.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All validation checks executed
- Validation results displayed
- State file updated to COMPLETED
- Completion event logged in history
- Statistics updated
- Final summary presented
- User given clear next steps
- Workflow completed gracefully

### ❌ SYSTEM FAILURE:

- Skipping validation checks
- Not updating state file
- Not logging completion event
- Not presenting final summary
- Attempting to load non-existent next step

**Master Rule:** The workflow must end gracefully with state properly updated and user informed of next steps.

---

## Pipeline Task Update (Archon) - Current Hypothesis Only

<pipeline-completion>
<critical>
🔵 **PIPELINE TASK UPDATE - CURRENT HYPOTHESIS ONLY**

Update `verification_state.yaml` for the **current hypothesis** only.
Do NOT check or report on other hypotheses' status — cross-hypothesis orchestration
is handled by `run_hypothesis_loop.py`, not by Phase 2C.
</critical>

<action>**Update Current Hypothesis Status**

Update `verification_state.yaml` for the current hypothesis:
- Set `experiment_design.status` = "COMPLETED"
- Set `experiment_design.completed_at` = current timestamp

Display:
```
Phase 2C Complete for {hypothesis_id}
  experiment_design.status = COMPLETED
```

> **IMPORTANT:** Do NOT read or display other hypotheses' Phase 2C status.
> The hypothesis loop orchestrator manages cross-hypothesis progress tracking.
</action>
</pipeline-completion>

---

## Workflow Completion

Display: "✅ Phase 2C workflow completed successfully!"

**END OF WORKFLOW**
