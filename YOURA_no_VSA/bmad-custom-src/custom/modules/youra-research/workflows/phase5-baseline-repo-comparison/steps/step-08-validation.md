---
name: 'step-08-validation'
description: 'Validate adaptation code for all 3 baselines with static analysis + runtime execution'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'

# File References
thisStepFile: '{workflow_path}/steps/step-08-validation.md'
prevStepFile: '{workflow_path}/steps/step-07-adaptation-coding.md'
nextStepFile: '{workflow_path}/steps/step-09-experiment.md'
coderStepFile: '{workflow_path}/steps/step-07-adaptation-coding.md'
workflowFile: '{workflow_path}/workflow.md'

# Reference Files
validation_templates: '{workflow_path}/_references/validation-templates.md'

# Agent Definition (Registered in .claude/agents/phase5-baseline/)
validator_agent: '.claude/agents/phase5-baseline/baseline-validator-agent.md'

# Input Files (per baseline)
checkpoint_file: '{baseline_folder}/05_baseline_checkpoint.yaml'
tasks_file: '{baseline_folder}/05_tasks.yaml'
adaptations_folder: '{baseline_folder}/adaptations/{baseline.repo_name}'
clone_path: '{baseline_folder}/baselines/{baseline.repo_name}'

# Config: Read from checkpoint.workflow_config (Source: workflow.yaml)

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 8: Adaptation Validation (Multi-Baseline)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required
> **Pattern:** Based on Phase 4 step-03-validator.md

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Validate adaptation code for **all 3 baselines** (loop)
- 🚫 FORBIDDEN to run Bash/Serena validation commands directly
- ✅ MUST use Task tool with subagent_type="baseline-validator-agent"
- 🔄 Route back to Step 7 if validation fails (cycles < 3)

## EXECUTION PROTOCOLS:

- 🎯 **FOR EACH baseline:** Check cycle limit and invoke validator sub-agent
- 💾 Invoke validator sub-agent via Task tool for each baseline
- 📖 Process validation results and update Archon tasks per baseline
- 🚫 FORBIDDEN to skip sub-agent invocation for any baseline

## CONTEXT BOUNDARIES:

- Available context: checkpoint (baselines array), Archon tasks in 'review' status per baseline
- Focus: Validation orchestration via sub-agent for **all baselines**
- Limits: Do not validate directly, do not run experiments
- Dependencies: Step 7 must have tasks in 'review' status for all baselines

---

## CRITICAL REQUIREMENT

**This step MUST invoke a sub-agent using the Task tool. DO NOT run validation directly!**

```
FORBIDDEN: Running Serena/Bash validation commands directly
REQUIRED: Use Task tool with subagent_type="baseline-validator-agent"
          (Registered at .claude/agents/phase5-baseline/baseline-validator-agent.md)
```

---

## SECTION 1: PRE-FLIGHT CHECKS

### 1.1 Cycle Limit Check

```python
# Load cycle limit from checkpoint (Single Source of Truth: workflow.yaml)
max_cycles = checkpoint["workflow_config"]["adaptation"]["max_coder_validator_cycles"]
```

| Condition | Action |
|-----------|--------|
| `checkpoint.coder_validator_cycles` ≥ max_cycles | Log to `checkpoint.last_error`, STOP (do not invoke validator), Go to Step 9 with partial results |
| `checkpoint.coder_validator_cycles` < max_cycles | Continue to Section 1.2 |

### 1.2 Query Review Tasks from YAML

<critical>

Tasks are loaded from local `05_tasks.yaml` file (NOT from Archon MCP).
**FORBIDDEN:** `mcp__archon__find_tasks` for adaptation tasks.
</critical>

**FOR EACH baseline in baselines (status == "PROCEED"):**

**Action:** Read tasks from `{tasks_file}`:

```python
# Load tasks from YAML file
tasks_data = read_yaml("{baseline_folder}/05_tasks.yaml")

# Extract review tasks for this baseline
for baseline_entry in tasks_data.baselines:
    if baseline_entry.repo_name == baseline.repo_name:
        review_tasks = [t for t in baseline_entry.tasks if t.status == "review"]
        baseline.review_tasks = review_tasks
```

| Condition | Action |
|-----------|--------|
| No review tasks for ANY baseline | No tasks to validate → Go to Step 9 |
| Review tasks found for baseline | Continue to Section 2 for this baseline |

---

## SECTION 2: INVOKE VALIDATOR SUB-AGENT (MANDATORY!) - Per Baseline

**FOR EACH baseline in baselines (status == "PROCEED"):**

### 2.1 Task Tool Invocation (repeat for each baseline)

<mandatory-action type="Task-tool-call">

## THIS IS NOT OPTIONAL - YOU MUST EXECUTE THIS TASK TOOL CALL FOR EACH BASELINE

**Skipping this Task tool call for any baseline = SYSTEM FAILURE**
**Running validation commands directly (Bash, Serena) without Task = SYSTEM FAILURE**

Execute the following Task tool call with EXACT parameters for each baseline:

**Tool:** `Task`

**Parameters:**
| Parameter | Value |
|-----------|-------|
| `description` | "Validate baseline adaptation code (static + runtime)" |
| `subagent_type` | `"baseline-validator-agent"` |
| `run_in_background` | `false` |
| `prompt` | See Section 2.2 below |

**Pre-requisite:** First read the validator agent definition at `.claude/agents/phase5-baseline/baseline-validator-agent.md`

**Then invoke Task tool with:**

| Parameter | Value |
|-----------|-------|
| subagent_type | "baseline-validator-agent" |
| description | "Validate baseline adaptation code (static + runtime)" |
| prompt | See Section 2.2 below |

**WAIT for sub-agent to complete and receive validation_result JSON**

</mandatory-action>

### 2.2 Validator Prompt Construction

Use the **Validator Prompt Template** from `{validation_templates}`.

Substitute the following variables:
- `{baseline_folder}`, `{repo_name}`
- `{tasks_file}` (05_tasks.yaml path)
- `{review_tasks}` (from 05_tasks.yaml, NOT Archon)
- `{conda_env_name}`, `{conda_path}`
- `{adaptations_folder}`, `{clone_path}`

---

## SECTION 3: PROCESS VALIDATION RESULTS

### 3.1 Parse Validator Output

**Action:** Parse JSON from agent output

| Condition | Action |
|-----------|--------|
| JSON parsing successful | Store in `validation_result` |
| JSON parsing failed or invalid | Log warning, set `validation_result.passed = false` |

### 3.2 Update Tasks in YAML

<critical>

Task status is updated in local `05_tasks.yaml` file (NOT Archon MCP).
**FORBIDDEN:** `mcp__archon__manage_task` for adaptation task updates.
</critical>

**For Passed Tasks:**

```python
# Update task status to done in 05_tasks.yaml
for task_id in validation_result.passed_tasks:
    task = find_task_by_id(tasks_data, task_id)
    task.status = "done"
    task.validation.static_passed = True
    task.validation.runtime_passed = True
    task.validation.validated_at = current_timestamp()

# Update budget_summary.by_status
tasks_data.budget_summary.by_status.review -= len(passed_tasks)
tasks_data.budget_summary.by_status.done += len(passed_tasks)
```

**For Failed Tasks (WITH ERROR INFO!):**

```python
# Update task status to pending with error info in 05_tasks.yaml
for failed_task in validation_result.failed_tasks:
    task = find_task_by_id(tasks_data, failed_task.task_id)
    task.status = "pending"
    task.retry_count += 1
    task.validation.static_passed = failed_task.static_passed
    task.validation.runtime_passed = failed_task.runtime_passed
    task.validation.error_info = failed_task.error_details
    task.validation.validated_at = current_timestamp()

# Update budget_summary.by_status
tasks_data.budget_summary.by_status.review -= len(failed_tasks)
tasks_data.budget_summary.by_status.pending += len(failed_tasks)
```

**Save YAML file:**

```python
write_yaml("{baseline_folder}/05_tasks.yaml", tasks_data)
```

### 3.3 Automatic Error Resolution (AUTO-FIX)

**Research Before Fix:**

**Step 1:** Search Archon KB with `mcp__archon__rag_search_knowledge_base(query="{error_type} fix", match_count=3)`

**Step 2:** Exa Fallback

| Condition | Action |
|-----------|--------|
| Archon results < 3 OR results are generic | Call `mcp__exa__get_code_context_exa(query="{error_type} pytorch fix example")` |

**Auto-Fix by Error Type:**

| Error Type | Auto-Fix Action |
|------------|-----------------|
| ModuleNotFoundError | pip install {mapped_package} |
| ImportError | pip install {mapped_package} |
| SyntaxError, TypeError | Pass to Coder (no auto-fix) |

### 3.4 Update Checkpoint

**Update the following checkpoint fields:**

| Field | Value |
|-------|-------|
| `current_step` | 8 |
| `validation.test_gate_passed` | `validation_result.test_gate_passed` |
| `validation.static_passed` | `validation_result.static_passed` |
| `validation.runtime_passed` | `validation_result.runtime_passed` |
| `validation.passed_tasks` | `validation_result.passed_tasks` |
| `validation.failed_tasks` | List of task IDs from failed_tasks |
| `coder_validator_cycles` | Increment by 1 (if validation failed) |
| `updated_at` | Current timestamp |

**Action:** Save checkpoint file

---

## SECTION 4: DETERMINE NEXT STEP

### 4.1 Routing Logic

| Condition | Next Step |
|-----------|-----------|
| `validation_result.passed` = true | `step-09-experiment.md` |
| `validation_result.passed` = false AND `coder_validator_cycles` < max_cycles | `step-07-adaptation-coding.md` (Return to Coder) |
| `validation_result.passed` = false AND `coder_validator_cycles` ≥ max_cycles | `step-09-experiment.md` (Max cycles, proceed with partial) |

<mandatory-action type="step-transition">

## MANDATORY: LOAD AND EXECUTE NEXT STEP NOW

**DO NOT stop here. DO NOT output a summary and wait for user input.**

**Based on validation result, YOU MUST immediately load and execute ONE of these:**

| Condition | Action |
|-----------|--------|
| `validation_result.passed == true` | Read and execute `step-09-experiment.md` |
| `validation_result.passed == false` AND `cycles < max_cycles` | Read and execute `step-07-adaptation-coding.md` |
| `validation_result.passed == false` AND `cycles >= max_cycles` | Read and execute `step-09-experiment.md` (partial) |

**Failure to load next step = SYSTEM FAILURE**

</mandatory-action>

---

## SECTION 5: GENERATE VALIDATION LOG

Create `{baseline_folder}/validation_log.md` using the **Validation Log Template** from `{validation_templates}`.

Include: test gate results, static analysis results, runtime validation results, task status updates, and next action.

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| Task tool fails | Retry 1 time, then log and skip validation |
| Sub-agent timeout | Log error, proceed with partial |
| Invalid JSON response | Treat as validation failed |
| Auto-fix fails | Keep in failed_tasks for Coder |

---

## STEP COMPLETION

**Step chain logic (max_cycles from checkpoint.workflow_config.adaptation.max_coder_validator_cycles):**
| Condition | Next Step |
|-----------|-----------|
| All tasks PASS | `step-09-experiment.md` |
| Any task FAIL (cycles < max_cycles) | `step-07-adaptation-coding.md` |
| Max cycles reached | `step-09-experiment.md` with partial results |

**On completion:** Load, read entire file, then execute appropriate next step file.

---

## CRITICAL STEP COMPLETION NOTE

Based on validation result, IMMEDIATELY load and execute (max_cycles from checkpoint.workflow_config):
- If PASS → `{workflow_path}/steps/step-09-experiment.md`
- If FAIL and cycles < max_cycles → `{workflow_path}/steps/step-07-adaptation-coding.md`
- If FAIL and cycles >= max_cycles → `{workflow_path}/steps/step-09-experiment.md` with partial results

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### ✅ SUCCESS:
- Cycle limit checked before proceeding
- **Review tasks loaded from 05_tasks.yaml**
- **Task tool invoked for EACH baseline** with subagent_type="baseline-validator-agent"
- Validator sub-agent completed and returned JSON result **for each baseline**
- Validation result parsed correctly for all baselines
- **Passed tasks marked as 'done' in 05_tasks.yaml** per baseline
- **Failed tasks marked as 'pending' with error info in 05_tasks.yaml** per baseline
- coder_validator_cycles incremented (if any baseline failed)
- validation_log.md generated **for all baselines**
- Checkpoint updated with validation results **for all baselines**
- Correct next step loaded based on overall result

### ❌ SYSTEM FAILURE:
- Running validation commands directly (Bash, Serena)
- Not using Task tool with baseline-validator-agent
- **Validating only 1 baseline when 3 are selected**
- Not processing sub-agent results for any baseline
- **Using mcp__archon__find_tasks or mcp__archon__manage_task for adaptation tasks**
- **Not reading/writing task status from/to 05_tasks.yaml**
- Not incrementing cycle count on failure
- Not loading next step immediately after processing
