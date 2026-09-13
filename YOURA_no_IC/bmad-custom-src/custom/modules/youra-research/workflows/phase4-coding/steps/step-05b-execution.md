---
name: 'step-05b-execution'
description: 'Experiment Execution - Entry point detection, environment setup, and experiment launch'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Helper References
entry_point_detection: '{helpers_path}/entry_point_detection.md'
conda_environment: '{helpers_path}/conda_environment.md'
experiment_monitoring: '{helpers_path}/experiment_monitoring.md'
smoke_test_detection: '{helpers_path}/smoke_test_detection.md'

# File References (order-independent references)
thisStepFile: '{workflow_path}/steps/step-05b-execution.md'
nextStepFile: '{workflow_path}/steps/step-05c-post-validation.md'
prevStepFile: '{workflow_path}/steps/step-05a-pre-validation.md'
coderStepFile: '{workflow_path}/steps/step-02-coder-loop.md'
workflowFile: '{workflow_path}/workflow.md'

# Step 5 Sub-steps (for cross-reference)
step5a: '{workflow_path}/steps/step-05a-pre-validation.md'
step5b: '{workflow_path}/steps/step-05b-execution.md'
step5c: '{workflow_path}/steps/step-05c-post-validation.md'

# Input Files
experiment_brief: '{hypothesis_folder}/02c_experiment_brief.md'
code_folder: '{hypothesis_folder}/code'

# Phase 3 Specification Files (for error analysis)
prd_file: '{hypothesis_folder}/03_prd.md'
architecture_file: '{hypothesis_folder}/03_architecture.md'
logic_file: '{hypothesis_folder}/03_logic.md'
config_file: '{hypothesis_folder}/03_config.md'

# Output Files
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'
experiment_log: '{code_folder}/experiment.log'
terminal_log: '{code_folder}/terminal.log'

# Long Experiment Support
use_nohup: true # Session-independent execution (supports 10+ hour experiments)

# Error Escalation Limits
max_quick_fix_attempts: 5
max_step2_retries: 1
---

## Section 0.5: Load Checkpoint

> This ensures checkpoint state is available even after session interruption.

```python
# MANDATORY: Read checkpoint from file (context loss prevention)
checkpoint = read_yaml(checkpoint_file) # {hypothesis_folder}/04_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-initialize first.")

IF checkpoint.current_step < 5:
    STOP("ERROR: Step sequence violation. Current step: {checkpoint.current_step}")

# Log checkpoint load for debugging
print(f"✅ Checkpoint loaded: step={checkpoint.current_step}, experiment_status={checkpoint.experiment_status}")
```

---

# Step 5B: Experiment Execution (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required
> **Part:** 2 of 3 (5A → 5B → 5C)

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- MUST use Serena MCP for entry point detection (via helper)
- MUST initialize conda environment before any Python execution
- MUST use nohup for session-independent experiment execution
- MUST perform 4-minute phased error check (30s, 90s, 180s, 240s)
- MUST verify GPU utilization if GPU available
- MUST detect and handle smoke test vs full experiment
- NEVER proceed to Step 5C with smoke test results only

---

## STEP GOAL

Dynamic entry point detection and experiment execution:
1. Analyze code structure and detect entry point
2. Setup Conda environment and install dependencies
3. Execute experiment (with nohup support)
4. 4-minute phased error check and GPU utilization verification
5. Smoke test detection and full run transition

---

## EXECUTION SEQUENCE

### 2. Dynamic Entry Point Discovery

> **REFERENCE:** Read `{entry_point_detection}` for detailed implementation

**Use the `discover_entry_point()` function from helper:**

```python
# Import from helper (conceptual - read helper file for implementation)
# See: {entry_point_detection}

result = discover_entry_point(code_folder, default_args)

IF result["success"]:
    execution_plan = result["execution_plan"]
    checkpoint.execution_plan = execution_plan
    SAVE checkpoint

    print(f"✅ Entry point: {execution_plan['entry_point']}")
    print(f" Command: {execution_plan['command']}")

    IF execution_plan["has_quick_mode"]:
        print(f"⚡ Quick mode available - two-phase execution")
ELSE:
    log_event("ERROR", f"Entry point discovery failed: {result['error']}")
    # Route to error handling
```

**Key Helper Functions:**
- `discover_entry_point()` - Complete entry point discovery (inline: code structure, candidates, CLI args, execution plan)
- `remove_quick_args()` - Remove quick/smoke test args for full run

---

### 3. Auto Execution Mode

#### 3a. Prepare Execution Environment

> **REFERENCE:** Read `{conda_environment}` for detailed implementation

**Use the `prepare_conda_env()` function from helper:**

```python
# See: {conda_environment}

env_result = prepare_conda_env(
    conda_env_name=checkpoint.conda.env_name,
    code_folder=code_folder,
    checkpoint=checkpoint,
    main_module=execution_plan["entry_point"].replace(".py", "")
)

IF env_result["success"]:
    conda_path = env_result["conda_path"]
    checkpoint.conda.conda_path = conda_path
    checkpoint.gpu = env_result["gpu_result"]
    SAVE checkpoint

    log_event("ENV", f"Environment ready. GPU: {env_result['gpu_result']['available']}")
ELSE:
    log_event("ERROR", f"Environment setup failed: {env_result['error']}")
    # Handle failed packages
    IF env_result["requirements_result"]["failed_packages"]:
        # Search Archon KB for solutions
        FOR pkg IN env_result["requirements_result"]["failed_packages"][:3]:
            mcp__archon__rag_search_knowledge_base(
                query=f"pip install error {pkg}",
                match_count=3
            )
```

**Key Helper Functions:**
- `detect_conda_path()` - Find conda installation
- `install_requirements()` - Install with fallbacks
- `verify_imports()` - Check imports work
- `check_gpu_availability()` - GPU status
- `build_conda_run_command()` - Build runnable command

---

#### 3b. Execute Main Experiment

> **REFERENCE:** Read `{experiment_monitoring}` for detailed implementation

**Use the `run_experiment()` function from helper:**

```python
# See: {experiment_monitoring}

# Check for resume first
resume_result = handle_resume(checkpoint, code_folder)

IF resume_result["action"] == "completed":
    print("✅ Experiment already completed. Proceeding to post-validation...")
    checkpoint.experiment_status = "completed"
    SAVE checkpoint
    Load, read entire file, then execute: {nextStepFile}
    STOP

ELIF resume_result["action"] == "continue_polling":
    # Already handled by handle_resume - check result
    IF resume_result["result"]["timeout"]:
        print(f"⚠️ Experiment exceeded max wait time")
        # Continue anyway - will check log for results
    checkpoint.experiment_status = resume_result["status"]
    SAVE checkpoint

ELIF resume_result["action"] == "no_experiment":
    # Fresh experiment launch
    exp_result = run_experiment(
        conda_path=checkpoint.conda.conda_path,
        conda_env_name=checkpoint.conda.env_name,
        code_folder=code_folder,
        command=execution_plan["command"],
        hypothesis_id=hypothesis_id,
        gpu_info=checkpoint.gpu,
        checkpoint=checkpoint
    )

    IF exp_result["success"]:
        checkpoint.experiment_status = exp_result["status"]
        checkpoint.experiment_pid = exp_result["pid"]
        SAVE checkpoint

    ELIF exp_result["needs_gpu_fix"]:
        # step-02 reads tasks from checkpoint.tasks.items, not from Archon
        fix_task = {
            "id": f"fix-gpu-{str(uuid4())[:8]}",
            "title": "[GPU FIX] Enable GPU usage in training code",
            "description": f"""GPU underutilization detected!
- GPU: {checkpoint.gpu.info}
- Utilization: {exp_result['gpu_check']['utilization']}%

Required:
1. model.to('cuda') or model.cuda()
2. Data tensors on GPU: tensor.to('cuda')
3. Verify device placement in forward pass""",
            "status": "todo",
            "priority": 100, # Highest priority
            "created_at": now(),
            "source": "step-05b-gpu-underutil"
        }
        checkpoint.tasks.items.append(fix_task)
        checkpoint.tasks.summary.remaining += 1

        checkpoint.current_step = 2
        SAVE checkpoint
        Load, read entire file, then execute: {coderStepFile}
        STOP

    ELSE:
        log_event("ERROR", f"Experiment failed: {exp_result['error']}")
        # Proceed to Error Handling
```

**Key Helper Functions:**
- `create_experiment_log_header()` - Format log header
- `launch_experiment_nohup()` - Launch with nohup
- `phased_error_check()` - 4-minute check (30s, 90s, 180s, 240s)
- `verify_gpu_utilization()` - Check GPU usage
- `poll_experiment_completion()` - UNATTENDED polling
- `handle_resume()` - Resume from checkpoint

---

### 4. Smoke Test Verification

> **REFERENCE:** Read `{smoke_test_detection}` for detailed implementation

**Use the `handle_smoke_test_detection()` function from helper:**

```python
# See: {smoke_test_detection}

IF checkpoint.experiment_status == "quick_completion":
    smoke_result = handle_smoke_test_detection(
        experiment_status=checkpoint.experiment_status,
        command_used=execution_plan["command"],
        log_file=f"{code_folder}/experiment.log",
        started_at=checkpoint.experiment_started_at,
        checkpoint=checkpoint
    )

    IF smoke_result["action"] == "RUN_FULL":
        # Update plan and re-run
        print(f"⚠️ SMOKE TEST DETECTED - Running full experiment...")
        execution_plan["command"] = smoke_result["full_command"]
        execution_plan["is_full_run"] = True
        checkpoint.update(smoke_result["checkpoint_updates"])
        SAVE checkpoint

        # Re-execute Section 3b with full command
        GOTO Section_3b

    ELSE:
        # Fast but genuine experiment
        print("✅ Fast experiment completed (not smoke test)")
        checkpoint.experiment_status = "completed"
        SAVE checkpoint
```

**Key Helper Functions:**
- `detect_smoke_test()` - Identify smoke test indicators
- `remove_quick_args()` - Clean command for full run
- `build_full_run_command()` - Prepare full command
- `validate_full_run_results()` - Verify results complete

---

## ERROR HANDLING

> **REFERENCE:** Read `_references/error-handling-patterns.md` for details

| Error | Action |
|-------|--------|
| pip install fails | Try conda → uv → pip3 → per-package (via helper) |
| Import error | Search KB for package mapping |
| Runtime error | Quick Fix (5x) → Step 2 Escalation (1x) |
| GPU OOM | Reduce batch size, retry |
| Timeout | Kill process, mark as blocked |

---

## STEP COMPLETION

**Auto-proceed to `{nextStepFile}` when ALL conditions met:**
1. ✅ Entry point detected and execution plan created
2. ✅ Conda environment prepared
3. ✅ Experiment launched (running_detached OR completed)
4. ✅ GPU utilization verified (if applicable)
5. ✅ If smoke test detected, full run has been executed

### UNATTENDED Conditional Auto-Proceed

Display: "**Routing based on execution results...**"

#### Menu Handling Logic:

Based on experiment execution results, immediately load, read entire file, then execute ONE of the following:

| Condition | Action |
|-----------|--------|
| GPU underutilization detected | Read and execute `{coderStepFile}` (step-02) |
| Smoke test passed, need full run | Re-execute Section 3b with full command |
| **FULL** experiment completed or running_detached | Read and execute `{nextStepFile}` (step-05c) |

#### EXECUTION RULES:

- This is an UNATTENDED experiment execution step with no user choices
- **NEVER proceed to Step 5C with smoke test results only!**
- Route to appropriate step based on execution results
- **Failure to load next step = SYSTEM FAILURE**

---

**On completion:** Load, read entire file, then execute `{nextStepFile}` (step-05c-post-validation.md)
