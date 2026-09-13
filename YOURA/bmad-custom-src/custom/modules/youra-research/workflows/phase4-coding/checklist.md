# Phase 4: Coding & Validation - Validation Checklist

## Step Execution Tracking

### Step 1: Initialize
- [ ] **State Validation (Section 0):**
  - [ ] verification_state.yaml validated and recovered if needed
  - [ ] Auto-fixes applied (if any)
  - [ ] Archon sync checked (if pipeline_project_id exists)
- [ ] **Hypothesis State Verified:**
  - [ ] verification_state.yaml loaded
  - [ ] Phase 3 status = COMPLETED for this hypothesis
  - [ ] Prerequisites validated (MUST_WORK gates checked)
- [ ] **Pipeline Project ID extracted:**
  - [ ] metadata.pipeline_project_id → pipeline.project_id fallback
- [ ] Existing checkpoint check (resume vs fresh start)
- [ ] Phase 3 outputs verified:
  - [ ] 03_prd.md exists
  - [ ] 03_architecture.md exists
  - [ ] 03_logic.md exists
  - [ ] 03_config.md exists
  - [ ] 02c_experiment_brief.md exists
  - [ ] **03_tasks.yaml exists**
- [ ] **INCREMENTAL hypothesis handling:**
  - [ ] Base hypothesis code copied (if applicable)
  - [ ] hypothesis_type determined (FOUNDATION/INCREMENTAL)
- [ ] **Tasks loaded from 03_tasks.yaml:**
  - [ ] Tasks list extracted
  - [ ] Hypothesis Task status updated in Archon (doing)
- [ ] **Conda environment created (Section 5.5):**
  - [ ] conda_env_name stored
  - [ ] conda_path stored
- [ ] **GPU detection (Section 5.6):**
  - [ ] gpu_available determined
  - [ ] gpu_info stored
  - [ ] pytorch_cuda_needed checked
- [ ] Checkpoint initialized with tasks.items[] array
- [ ] current_step set to 1

### Step 1b: Continue (if resuming)
- [ ] Checkpoint loaded successfully
- [ ] State restored correctly
- [ ] Task status verified against checkpoint
- [ ] Generated files verified
- [ ] Resume point determined

### Step 1a: Data Setup
- [ ] Dependencies installed in conda environment
- [ ] GPU PyTorch installed (if needed)
- [ ] Dataset downloaded and prepared
- [ ] data_setup.status = "completed" in checkpoint

### Step 2: Coder Loop (SDD-Based)
- [ ] Todo tasks retrieved from checkpoint (sorted by priority)
- [ ] **FOR EACH task - SDD Cycle:**
  - [ ] **2a. Pre-Check & Start Task:**
    - [ ] Complexity-aware retry limits set
    - [ ] Task status → "doing" in checkpoint
  - [ ] **2b. SPEC: Load Specifications:**
    - [ ] reference_files used to load specific Phase 3 sections
    - [ ] experiment_brief loaded for reality tests
  - [ ] **2c. TEST: Generate Spec Compliance Tests:**
    - [ ] Test file generated: `tests/test_{module}.py`
    - [ ] Pre-impl pytest run (expect ImportError)
    - [ ] sdd_metrics.test_attempts incremented
  - [ ] **2d. IMPL: Implement to Spec:**
    - [ ] Archon KB search (MANDATORY)
    - [ ] Exa fallback (if Archon < 3 results)
    - [ ] Implementation generated
    - [ ] pytest run for spec compliance
    - [ ] impl_phase recorded (passed/failed)
  - [ ] **2e. VERIFY: Polish and Re-verify:**
    - [ ] Best practices from Archon KB applied
    - [ ] Serena analysis performed
    - [ ] Re-verify pytest (rollback if fails)
  - [ ] **2f. Update Checkpoint:**
    - [ ] Task status → "review"
    - [ ] SDD phases recorded
    - [ ] File lists updated
- [ ] coder_validator_cycles incremented
- [ ] Checkpoint saved

### Step 3: Validator
- [ ] Validator agent invoked
- [ ] **Review tasks validated:**
  - [ ] Syntax check
  - [ ] Type hints
  - [ ] API match (03_logic.md)
  - [ ] Config match (03_config.md)
  - [ ] Imports valid
  - [ ] Anti-patterns detected
  - [ ] Task completeness
- [ ] **Mechanism verification:**
  - [ ] Pre-conditions satisfied
  - [ ] Activation code found
  - [ ] Architecture compatible
  - [ ] Indicators measurable
- [ ] **Reality Check (Pattern-Free Mock Detection):**
  - [ ] general_reality_check() function exists
  - [ ] Determinism test
  - [ ] Sensitivity test
  - [ ] Smoothness test
- [ ] Passed tasks → "done"
- [ ] Failed tasks → "todo" with issues

### Step 4: Experiment Confirm
- [ ] 02c_experiment_brief.md loaded
- [ ] Gate type and success criteria extracted
- [ ] **Dry run executed (1 epoch, 1% data)**
- [ ] **Dry run passed** (no errors)
- [ ] Execution option set to "auto"
- [ ] checkpoint.dry_run.status = "passed"

### Step 5a: Pre-Validation
- [ ] Config flags scanned for mock indicators
- [ ] Dataset size checked

### Step 5b: Execution
- [ ] Experiment executed (auto/manual/load/skip)
- [ ] Results collected
- [ ] experiment_results.json saved
- [ ] **Error Escalation (if errors):**
  - [ ] Persistent errors analyzed with Phase 3 docs
  - [ ] Error Tasks registered in Archon
  - [ ] Quick Fix attempted (max 3 times)
  - [ ] Step 2 escalation (max 1 time)

### Step 5c: Post-Validation (Mock Detection)
- [ ] **Mock Data Detection:**
  - [ ] Config flags scanned
  - [ ] Experiment logs scanned
  - [ ] Metrics analyzed for anomalies
  - [ ] Dataset size checked (< 100 = suspicious)
  - [ ] Code scanned for faker/mimesis imports
- [ ] **Reality Check (Mock Model Detection):**
  - [ ] Reality check results loaded
  - [ ] Critical tests evaluated
  - [ ] If mock detected → Archon task + retry

### Step 6: Gate Processing
- [ ] **Checkpoint Completion Verified:**
  - [ ] All tasks in "review" or "done" status
- [ ] Gate type validated
- [ ] Experiment results loaded
- [ ] **Mechanism Activation Verified:**
  - [ ] Activation indicators checked
  - [ ] Mechanism effect measured
- [ ] Gate criteria evaluated
- [ ] Gate result determined (PASS/PARTIAL/FAIL)
- [ ] verification_state.yaml updated
- [ ] **Cascade handling (if failure):**
  - [ ] Dependent hypotheses identified
  - [ ] CASCADE_FAILED or BLOCKED status applied
- [ ] **Hypothesis Task updated in Archon**
- [ ] Routing determined:
  - [ ] PASS → Step 7
  - [ ] FAIL/PARTIAL + MUST_WORK → Step 6b
  - [ ] SHOULD_WORK failure → Step 7 with limitation

### Step 6b: Reflection (if gate FAIL + MUST_WORK)
- [ ] Modification limit checked (< 3 attempts)
- [ ] Reflection analysis performed:
  - [ ] What succeeded
  - [ ] What failed
  - [ ] Root cause analysis
  - [ ] Key insights
- [ ] "Meaningful findings" determination
- [ ] Decision executed:
  - [ ] If meaningful: New hypothesis version (H-*-v2)
  - [ ] If not meaningful: Marked as FAILED
- [ ] verification_state.yaml updated
- [ ] reflection_report.md saved

### Step 7: Report Generation
- [ ] Template loaded
- [ ] **LLM-Autonomous Figure Generation:**
  - [ ] Figures directory created (`{hypothesis_folder}/figures`)
  - [ ] results.csv analyzed for available data columns
  - [ ] experiment_results.json analyzed for additional data
  - [ ] 02c_experiment_brief.md analyzed for research context
  - [ ] Appropriate figures decided based on data + context
  - [ ] generate_figures.py created dynamically
  - [ ] Figures generated and registered in checkpoint
- [ ] Report sections generated:
  - [ ] Hypothesis Summary
  - [ ] Code Generation Summary
  - [ ] Code Quality Checklist
  - [ ] Experiment Results
  - [ ] Gate Evaluation
  - [ ] Next Steps
  - [ ] Appendix
- [ ] 04_validation.md saved
- [ ] No placeholder text remaining

### Step 8: Completion
- [ ] All outputs verified:
  - [ ] 04_validation.md exists
  - [ ] code/ folder exists
  - [ ] verification_state.yaml updated
- [ ] Checkpoint archived with timestamp
- [ ] verification_state.yaml updated (final)
- [ ] **Benchmark Metrics updated:**
  - [ ] Termination quality tracked
  - [ ] Routing decision quality tracked
- [ ] **Pipeline Task Update (Current Hypothesis Only):**
  - [ ] Current hypothesis validation.status = COMPLETED
  - [ ] Do NOT check other hypotheses' status
- [ ] **Serena Memory Snapshot (current hypothesis)**
- [ ] **Return to hypothesis-loop (MANDATORY)**

---

## Pre-Execution Checks

### Phase 3 Outputs Ready
- [ ] `03_prd.md` exists and is complete
- [ ] `03_architecture.md` exists with Epic tasks
- [ ] `03_logic.md` exists with API specifications
- [ ] `03_config.md` exists with config schemas
- [ ] `02c_experiment_brief.md` exists with experiment spec
- [ ] **`03_tasks.yaml` exists**
- [ ] `verification_state.yaml` exists with gate configuration

### Archon Pipeline Connection
- [ ] Pipeline Project ID available (from verification_state.yaml)
- [ ] Hypothesis Task ID available (for status updates)

### Environment Ready
- [ ] Archon MCP server connected
- [ ] Serena MCP server connected
- [ ] Exa MCP server connected (optional)
- [ ] Python environment available
- [ ] GPU available (if needed for experiment)

---

## Output Verification

### Required Outputs

| Output | Location | Verified |
|--------|----------|----------|
| `04_validation.md` | `{hypothesis_folder}/` | [ ] |
| `04_checkpoint_archived_*.yaml` | `{hypothesis_folder}/` | [ ] |
| `experiment_results.json` | `{hypothesis_folder}/` | [ ] |
| Generated code | `{hypothesis_folder}/code/` | [ ] |
| Test files | `{hypothesis_folder}/code/tests/` | [ ] |
| LLM-generated figures (*.png) | `{hypothesis_folder}/figures/` | [ ] |
| `.phase5_ready` | `{hypothesis_folder}/` | [ ] |

### verification_state.yaml Updates

**Location Verification:**
- [ ] Updated file is at `{research_folder}/verification_state.yaml` (NOT in `{hypothesis_folder}`)
- [ ] No new `verification_state.yaml` created in `{hypothesis_folder}`

**Content Updates (in `hypotheses.{hypothesis_id}` section):**
- [ ] `validation.phase4.status: "completed"`
- [ ] `validation.phase4.completed_at` set
- [ ] `gate.satisfied` set correctly
- [ ] `gate.evaluation_result` set
- [ ] `status` updated

### Checkpoint Task Status (Local)
- [ ] All tasks in final state ("done" or "review")
- [ ] No tasks in "todo" (unless intentionally skipped)
- [ ] No tasks in "doing"
- [ ] tasks.summary counts accurate

---

## Local Task Management

### 04_checkpoint.yaml Schema
- [ ] version: "3.5" or higher
- [ ] tasks.items[] array populated from 03_tasks.yaml
- [ ] Each task has:
  - [ ] id, title, status
  - [ ] sdd_phases (TEST, IMPL, VERIFY)
  - [ ] priority
  - [ ] reference_files
  - [ ] complexity, epic, description

### Task Status Flow
```
todo → doing → review → done
```

### SDD Metrics Tracked
- [ ] tasks_completed count
- [ ] sdd_compliant_tasks count
- [ ] test_attempts count
- [ ] pre_impl_checks_passed count
- [ ] impl_phases_passed / impl_phases_failed
- [ ] verify_phases_passed / verify_rollbacks
- [ ] sdd_order_violations count

---

## Quality Assurance

### Code Quality
- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] API signatures match 03_logic.md
- [ ] Config usage matches 03_config.md
- [ ] No circular imports
- [ ] No hardcoded magic numbers
- [ ] No empty except blocks

### Report Quality (04_validation.md)
- [ ] All sections complete
- [ ] Metrics accurately recorded
- [ ] Gate evaluation correct
- [ ] Next steps appropriate
- [ ] No placeholder text remaining

### Checkpoint Integrity
- [ ] All state variables correct
- [ ] Task counts accurate
- [ ] History accurate
- [ ] Timestamps valid

---

## SDD (Specification-Driven Development) Compliance

### SDD Cycle Order
1. [ ] **SPEC**: Read Phase 3 specs BEFORE any code
2. [ ] **TEST**: Generate tests FROM spec
3. [ ] **IMPL**: Implement to spec
4. [ ] **VERIFY**: Polish and re-verify

### SDD Violations Check
- [ ] No TEST after IMPL (test_created_at < impl_created_at)
- [ ] No implementation without spec reading
- [ ] Tests verify spec compliance (not just coverage)

---

## Archon Integration

### Hypothesis Task Updates
- [ ] Hypothesis Task marked "doing" at start
- [ ] Hypothesis Task marked "review" at gate evaluation
- [ ] Hypothesis Task marked "done" on PASS

### Step Progress Tracking

- [ ] `current_step` updated in 04_checkpoint.yaml at each step transition
- [ ] Step progress visible in checkpoint file (not in Archon)

### Pipeline Task Update (Current Hypothesis Only)
- [ ] Current hypothesis validation.status = COMPLETED
- [ ] Do NOT check other hypotheses' status

---

## UNATTENDED Mode Handling

- [ ] UNATTENDED mode checked throughout workflow
- [ ] Auto-proceed through all steps (no user prompts)
- [ ] Error handling continues workflow when possible
- [ ] Dry run retries automated (max 3)
- [ ] Experiment retries automated (max 1)

---

## Retry Limits

| Action | Max Retries |
|--------|-------------|
| Per-task retries | 3 |
| Coder-Validator cycles | 5 |
| Dry run retries (Step 4) | 3 |
| Experiment retries | 1 (UNATTENDED) |
| Quick Fix attempts (Step 5) | 3 |
| Step 2 escalation (Step 5) | 1 |
| Mock data retries (Step 5c) | 3 |
| Mock model retries (Step 5c) | 3 |
| Modification attempts (Step 6b) | 3 |

---

## Gate Routing Summary

| Gate Result | Gate Type | Routing | Reflection? |
|-------------|-----------|---------|-------------|
| PASS | Any | → Phase 5 | No |
| FAIL | MUST_WORK | → Phase 0 | Yes |
| PARTIAL | MUST_WORK | → SUPERSEDED or SELF_MODIFY | Yes |
| FAIL/PARTIAL | SHOULD_WORK | → Phase 5 (with limitation) | No |
| FAIL/PARTIAL | DETERMINES_SUCCESS | → Phase 0 | Yes |

---

## Critical Failures (Immediate Fix Required)

- [ ] State validation not performed (Section 0)
- [ ] 03_tasks.yaml missing or empty
- [ ] Tasks created in Archon ( - use local checkpoint)
- [ ] SDD order violated (IMPL before TEST)
- [ ] reference_files not used for spec loading
- [ ] Checkpoint not saved after each task
- [ ] Dry run skipped
- [ ] Gate evaluation skipped
- [ ] verification_state.yaml location wrong (must be in research_folder)
- [ ] Not returning to hypothesis-loop after Step 8
- [ ] Waiting for user input in UNATTENDED mode

---

## Validation Summary

**Total Checks:** 200+
**Required:** Step execution + SDD compliance + Local task management + Gate evaluation + State management
**MANDATORY Steps:** All steps (1-8, conditionally 6b)

**Minimum Pass Criteria:**
- All steps completed
- All SDD phases executed correctly
- All tasks processed via local checkpoint
- Gate evaluation completed
- verification_state.yaml updated at correct location
- Return to hypothesis-loop executed

---

**Validation Result:**
- ✅ PASS: Gate passed, all outputs generated, ready for Phase 5
- ⚠️ PARTIAL: Gate partial, reflection triggered, some issues
- ❌ FAIL: Gate failed, routing to Phase 0 or Phase 2A

**Completed By:** _______________
**Date:** _______________
**Hypothesis ID:** _______________
**Gate Result:** _______________

**Reviewer:** _____________
**Date:** {{date}}
**Validator:** Phase 4 Coding Workflow (YouRA)
