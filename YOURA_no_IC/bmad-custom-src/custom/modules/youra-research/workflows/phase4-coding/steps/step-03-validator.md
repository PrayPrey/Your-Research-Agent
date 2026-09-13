---
name: 'step-03-validator'
description: 'Validator Agent - Validate SDD-generated code with test gate + static analysis + runtime'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'

# File References
thisStepFile: '{workflow_path}/steps/step-03-validator.md'
nextStepFile: '{workflow_path}/steps/step-04-experiment-confirm.md'
coderStepFile: '{workflow_path}/steps/step-02-coder-loop.md'
step5File: '{workflow_path}/steps/step-05-experiment-execute.md'
workflowFile: '{workflow_path}/workflow.md'

# Agent Definition (Registered in .claude/agents/phase4-validation/)
validator_agent: '.claude/agents/phase4-validation/validator-agent.md'

# Input Files (Phase 3 Outputs)
prd_file: '{hypothesis_folder}/03_prd.md'
architecture_file: '{hypothesis_folder}/03_architecture.md'
logic_file: '{hypothesis_folder}/03_logic.md'
config_file: '{hypothesis_folder}/03_config.md'
code_folder: '{hypothesis_folder}/code'

# Output Files
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'

# Limits
max_coder_validator_cycles: 5
---

## Section 0.5: Load Checkpoint

> This ensures checkpoint state is available even after session interruption.

```python
# MANDATORY: Read checkpoint from file (context loss prevention)
checkpoint = read_yaml(checkpoint_file) # {hypothesis_folder}/04_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-initialize first.")

IF checkpoint.current_step < 2:
    STOP("ERROR: Step sequence violation. Current step: {checkpoint.current_step}")

# Log checkpoint load for debugging
print(f"✅ Checkpoint loaded: step={checkpoint.current_step}, cycle={checkpoint.coder_validator_cycles}")
```

---

# Step 3: Validator Agent (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🚫 FORBIDDEN: Running Serena/Bash validation commands directly
- ✅ REQUIRED: Use Task tool with `subagent_type="validator-agent"`
- MUST check cycle limit (max 5) before invoking validator
- MUST query review tasks before validation
- MUST route back to Step 2 (Coder) on validation failure
- MUST proceed to Step 4 after all tasks validated or cycle limit reached

---

## STEP GOAL

Validate SDD-generated code through a sub-agent using the Task tool.

**SDD Context:** Code arrives from Step 2 after passing the SDD cycle:
- 📋 SPEC: Specifications read and understood from 03_*.md files
- 🧪 TEST: Spec compliance tests generated
- ⚙️ IMPL: Implementation created to match specs
- ✅ VERIFY: Spec compliance verified via pytest

The Validator Agent performs **additional** validation beyond SDD:
1. **Test Gate (pytest)** - Run full `tests/` integration (Coder runs individual files)
2. **Static Analysis (Serena MCP)** - Verify API matches 03_logic.md
3. **Reality Tests** - Run 02c mechanism verification tests
4. **Runtime Verification** - Import checks, basic execution
5. **Error Analysis** - Map failures to specific tasks

---

## SECTION 1: PRE-FLIGHT CHECKS

### 1.1 Cycle Limit Check

```python
IF checkpoint.coder_validator_cycles >= 5:
    Log to checkpoint.last_error
    # Skip to Section 4 (proceed with partial results)
    STOP HERE - DO NOT INVOKE VALIDATOR
```

### 1.2 Query Review Tasks (Local Checkpoint)

> Implementation tasks are tracked locally per step-01-initialize.md.

```python
# Read review tasks from Local checkpoint
# Implementation tasks are in checkpoint.tasks.items, not in Archon
review_tasks = [
    task for task in checkpoint.tasks.items
    if task.get("status") == "review"
]

review_task_ids = [task["id"] for task in review_tasks]

IF len(review_task_ids) == 0:
    # No tasks to validate - skip to Section 4
    STOP HERE - DO NOT INVOKE VALIDATOR
```

---

## SECTION 2: INVOKE VALIDATOR SUB-AGENT (MANDATORY!)

### 2.1 Task Tool Invocation

#### ⚠️ MANDATORY: TASK TOOL CALL REQUIRED

> **🚨 THIS IS NOT OPTIONAL - YOU MUST EXECUTE THIS TASK TOOL CALL**
>
> - Skipping this Task tool call = **SYSTEM FAILURE**
> - Running validation commands directly (Bash, Serena) without Task = **SYSTEM FAILURE**

Execute the following Task tool call with EXACT parameters:

**Tool:** `Task`

**Parameters:**
| Parameter | Value |
|-----------|-------|
| `description` | "Validate Phase 4 code (static + runtime)" |
| `subagent_type` | `"validator-agent"` |
| `run_in_background` | `false` |
| `prompt` | See Section 2.2 below |

**Pre-requisite:** First read the validator agent definition:
```python
Read(validator_agent) # {workflow_path}/agents/validator-agent.md
```

Then invoke:
```python
Task(
    subagent_type="validator-agent",
    description="Validate Phase 4 code (static + runtime)",
    prompt=validator_prompt # See Section 2.2
)
```

**WAIT for sub-agent to complete and receive validation_result JSON**

### 2.2 Validator Prompt Construction

```markdown
You are the Validator Agent for Phase 4.

## Inputs
- hypothesis_folder: {hypothesis_folder}
- code_folder: {hypothesis_folder}/code/
- review_tasks: {review_tasks}
- conda_env_name: {checkpoint.conda.env_name} # e.g., "youra-h-e1"
- conda_path: {checkpoint.conda.conda_path} # e.g., "/home/anonymous/miniforge3"

## Phase 3 Specification Files (READ ALL!)
- 03_prd.md: {prd_file}
- 03_architecture.md: {architecture_file}
- 03_logic.md: {logic_file}
- 03_config.md: {config_file}

## 🚨 CRITICAL: Conda Environment Setup (MUST DO FIRST!)

Before ANY Python/pip/pytest command, you MUST:

1. **Initialize conda and install requirements:**
```bash
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pip install -r {code_folder}/requirements.txt
```

2. **All subsequent Python commands MUST source conda first:**
```bash
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pytest tests/ -v
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} python -c "import module"
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} python main.py --help
```

**DO NOT use raw `pip install` or `pytest` without `source conda.sh && conda run -n {conda_env_name}`!**

## Your Mission
Execute validation phases in order:

1. **Phase 0: Test Gate** - Run pytest FIRST (IN CONDA ENV!)
   ```bash
   source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pip install -r {code_folder}/requirements.txt
   source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pytest {code_folder}/tests/ -v
   ```
   - If tests fail → STOP and return immediately

2. **Phase 0.5: Context** - Gather per-task requirements
   - Task details already provided in review_tasks (from Local checkpoint)
   - Extract expected symbols from 03_logic.md

3. **Phase 1: Static** - Use Serena MCP
   - mcp__serena__get_symbols_overview for each file
   - mcp__serena__find_symbol to verify implementations
   - Compare against 03_logic.md specs

4. **Phase 2: Runtime** - Use Bash (IN CONDA ENV!)
   ```bash
   source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} python -c "from module import *"
   source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} python main.py --help
   ```

5. **Phase 3: Error Analysis**
   - Map errors to tasks
   - Return results in JSON (step-03-validator.md updates Local checkpoint)

## Return Format
Return a JSON object:
{
  "validation_result": {
    "passed": true|false,
    "test_gate_passed": true|false,
    "passed_tasks": ["task-id-1"],
    "failed_tasks": [{
      "task_id": "task-id-2",
      "error_details": {
        "error_type": "ImportError",
        "file": "model.py",
        "line": 5,
        "traceback": "..."
      }
    }]
  }
}

## Full Instructions
[Include content from {validator_agent}]
```

---

## SECTION 3: PROCESS VALIDATION RESULTS

### 3.1 Parse Validator Output

```python
validation_result = parse_json(agent_output)

IF validation_result is invalid:
    Log warning
    Set validation_result.passed = false
```

### 3.2 Update Local Checkpoint Tasks

> Implementation tasks are tracked locally per step-01-initialize.md.

**For Passed Tasks:**
```python
FOR task_id in validation_result.passed_tasks:
    # Find task in checkpoint and update status
    FOR idx, task in enumerate(checkpoint.tasks.items):
        IF task["id"] == task_id:
            checkpoint.tasks.items[idx]["status"] = "done"
            checkpoint.tasks.items[idx]["completed_at"] = now()
            break

    checkpoint.tasks.completed += 1
    checkpoint.task_history.append({task_id, status: "done", timestamp})
```

**For Failed Tasks (WITH ERROR INFO!):**
```python
FOR failed_task in validation_result.failed_tasks:
    # Find task in checkpoint and update status with error details
    FOR idx, task in enumerate(checkpoint.tasks.items):
        IF task["id"] == failed_task.task_id:
            checkpoint.tasks.items[idx]["status"] = "todo"
            checkpoint.tasks.items[idx]["validation_error"] = failed_task.error_details
            break

    checkpoint.tasks.remaining += 1
    checkpoint.task_history.append({task_id, status: "failed", issues, timestamp})

# SAVE checkpoint after all updates
SAVE checkpoint
```

### 3.3 Automatic Error Resolution (AUTO-FIX)

**Research Before Fix:**
```python
# 1. Search Archon KB
archon_results = mcp__archon__rag_search_knowledge_base(
    query=f"{error_type} fix", match_count=3
)

# 2. Exa Fallback if insufficient
IF len(archon_results) < 3 OR results_are_generic:
    exa_code = mcp__exa__get_code_context_exa(
        query=f"{error_type} {framework} fix example"
    )

# 3. Use Serena for context
mcp__serena__get_symbols_overview(relative_path=file)
```

**Auto-Fix by Error Type:**

| Error Type | Auto-Fix Action |
|------------|-----------------|
| ModuleNotFoundError | pip install {mapped_package} |
| ImportError | pip install {mapped_package} |
| SyntaxError | Edit fix with Serena |
| IndentationError | Edit fix with Serena |
| KeyError (config) | Add missing key from 03_config.md |
| TypeError, Logic | Pass to Coder (no auto-fix) |

**Package Mapping:**
```python
package_map = {
    "torch_geometric": "torch-geometric",
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "yaml": "pyyaml"
}
```

### 3.4 Update Checkpoint

```python
checkpoint.current_step = 3
checkpoint.partial_results.validation_passed = validation_result.passed
checkpoint.coder_validator_cycles += 1 # if failed
checkpoint.updated_at = now()
SAVE checkpoint
```

---

## SECTION 4: DETERMINE NEXT STEP

### 4.1 Routing Logic

```python
IF validation_result.passed == true:
    next_step = "step4" if not checkpoint.after_validator_goto else checkpoint.after_validator_goto
ELSE:
    IF checkpoint.coder_validator_cycles < 5:
        next_step = "step2" # Return to Coder
    ELSE:
        next_step = "step4" # Max cycles, proceed with partial
```

### UNATTENDED Conditional Auto-Proceed

Display: "**Routing based on validation result...**"

#### Menu Handling Logic:

Based on validation result, immediately load, read entire file, then execute ONE of the following:

| Condition | Action |
|-----------|--------|
| `validation_result.passed == true` | Read and execute `{nextStepFile}` (step-04) |
| `validation_result.passed == true` AND `checkpoint.after_validator_goto == "step5"` | Read and execute `{step5File}` (step-05) |
| `validation_result.passed == false` AND `cycles < 5` | Read and execute `{coderStepFile}` (step-02) |
| `validation_result.passed == false` AND `cycles >= 5` | Read and execute `{nextStepFile}` (step-04) |

#### EXECUTION RULES:

- This is an UNATTENDED validation step with no user choices
- Route to appropriate step based on validation results
- **Failure to load next step = SYSTEM FAILURE**

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

**Step chain logic:**
| Condition | Next Step |
|-----------|-----------|
| All tasks PASS | `{nextStepFile}` (step-04-experiment-confirm.md) |
| Any task FAIL (cycles < 5) | `{coderStepFile}` (step-02-coder-loop.md) |
| Max cycles reached | `{nextStepFile}` with partial results |
| Step 5 escalation return | `{step5File}` (step-05-experiment-execute.md) |

**On completion:** Load, read entire file, then execute appropriate next step file.
