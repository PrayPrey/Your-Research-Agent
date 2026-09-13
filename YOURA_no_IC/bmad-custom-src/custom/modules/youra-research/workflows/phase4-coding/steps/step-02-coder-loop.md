---
name: 'step-02-coder-loop'
description: 'SDD-Based Coder Agent Loop - Specification-Driven code generation per local task'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'

# File References
thisStepFile: '{workflow_path}/steps/step-02-coder-loop.md'
nextStepFile: '{workflow_path}/steps/step-03-validator.md'
step5File: '{workflow_path}/steps/step-05b-execution.md'
workflowFile: '{workflow_path}/workflow.md'

# Reference Guides (READ when needed!)
test_gen_guide: '{workflow_path}/_references/test-generation-guide.md'
code_gen_guide: '{workflow_path}/_references/code-generation-guide.md'
mcp_tools_guide: '{workflow_path}/_references/mcp-tools-guide.md'

# Input Files (Phase 2C + Phase 3 Outputs)
experiment_brief: '{hypothesis_folder}/02c_experiment_brief.md'
prd_file: '{hypothesis_folder}/03_prd.md'
architecture_file: '{hypothesis_folder}/03_architecture.md'
logic_file: '{hypothesis_folder}/03_logic.md'
config_file: '{hypothesis_folder}/03_config.md'

# Output Files
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'
code_folder: '{hypothesis_folder}/code'

# Limits
max_retries_per_task: 3
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

# Step 2: SDD-Based Coder Agent Loop (UNATTENDED Mode)

> **Mode:** UNATTENDED | **Approach:** SDD (Specification-Driven Development)

---

## STEP GOAL

| Phase | Action | Gate |
|-------|--------|------|
| 📋 **SPEC** | Read 03_*.md specs | Specs extracted |
| 🧪 **TEST** | Generate spec compliance tests | ImportError expected |
| ⚙️ **IMPL** | Implement to spec (Archon → Exa) | pytest PASS |
| ✅ **VERIFY** | Polish and re-verify | pytest STILL PASS |

Tasks transition: `todo` → `doing` → `review`. Continue until all tasks in `review`.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

| Rule | Requirement |
|------|-------------|
| 📋 SPEC FIRST | Read specs BEFORE any code |
| 🧪 TEST FROM SPEC | Tests verify spec compliance |
| ⚙️ IMPL TO SPEC | Match 03_logic.md signatures exactly |
| 📚 ARCHON FIRST | Search KB before implementing |
| 🔄 EXA FALLBACK | If Archon < 3 results → Exa (MANDATORY!) |

> 📖 **Reference Guides:**
> - TEST phase details → `{test_gen_guide}`
> - IMPL phase details → `{code_gen_guide}`
> - MCP tool usage → `{mcp_tools_guide}`

---

## EXECUTION SEQUENCE

### 0. Pre-Checks

```python
# 0a. Verify Data Setup
IF checkpoint.data_setup.status != "completed":
    STOP("Data setup incomplete. Run Step 1a first.")

# 0b. Check Step 5 Escalation
IF checkpoint.return_to_step5_after_coder == true:
    checkpoint.after_validator_goto = "step5"

# 0c. Check Cycle Limits
IF checkpoint.coder_validator_cycles >= 5:
    STOP("Max cycles reached. Proceed to Step 7.")
```

### 1. Get Todo Tasks from Checkpoint

```python
# Read tasks from checkpoint (loaded from 03_tasks.yaml in Step 1)
all_tasks = checkpoint.tasks.items # List of task objects from checkpoint

# Filter by status
todo_tasks = [t for t in all_tasks if t["status"] == "todo"]

# Priority order: Data prep (100-95) → Environment (94) → Epics (93-50) → Subtasks (49-2) → Failsafe (1)
todo_tasks = sorted(todo_tasks, key=lambda t: t.get("priority", 0), reverse=True)

print(f"📋 Todo tasks ({len(todo_tasks)}), sorted by priority:")
for t in todo_tasks[:5]: # Show first 5
    print(f" [{t.get('priority', 0):3d}] {t['title'][:50]}")

IF len(todo_tasks) == 0:
    # All tasks processed → Proceed to Validator
    GOTO Section_4 # Section renumbered
```

### 2. Task Processing Loop (SDD Cycle)

**FOR EACH task in todo_tasks:**

#### 2a. Pre-Check & Start Task

```python
# Get task index for checkpoint updates
task_index = next(i for i, t in enumerate(checkpoint.tasks.items) if t["id"] == task["id"])

# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
task_complexity = task.get("complexity") # Complexity score from Phase 3
task_epic = task.get("epic") # Parent epic name
task_description = task.get("description")
task_feature = task.get("feature_tag")

# Higher complexity tasks get more implementation attempts
IF task_complexity is not None:
    IF task_complexity >= 8:
        max_impl_attempts = 5 # High complexity: more retries
        search_match_count = 8 # More Archon/Exa results
    ELIF task_complexity >= 5:
        max_impl_attempts = 4 # Medium complexity
        search_match_count = 6
    ELSE:
        max_impl_attempts = 3 # Low complexity: default
        search_match_count = 5
ELSE:
    max_impl_attempts = 3 # Default if complexity not set
    search_match_count = 5

print(f"📊 Task: {task['title']}")
print(f" Epic: {task_epic}, Complexity: {task_complexity}, Feature: {task_feature}")
print(f" Max attempts: {max_impl_attempts}, Search depth: {search_match_count}")

# Check retry limit (stored in checkpoint)
IF checkpoint.task_retry_counts.get(task["id"], 0) >= max_impl_attempts:
    CONTINUE # Skip to next task

# Check for Validator error info (retry cycles) - stored in task object
IF task.get("validation_error"):
    error_info = task["validation_error"] # {error_type, file, line, traceback}

# Start task - update status in checkpoint (NOT Archon)
checkpoint.tasks.items[task_index]["status"] = "doing"
checkpoint.tasks.items[task_index]["started_at"] = now()
checkpoint.current_task_index = task_index
checkpoint.tasks.summary.in_progress += 1

SAVE checkpoint
```

#### 2b. 📋 SPEC: Load Specifications

```python
# CRITICAL: Get conda info from checkpoint for ALL pytest calls
conda_path = checkpoint.conda.conda_path # e.g., "/home/anonymous/miniforge3"
conda_env_name = checkpoint.conda.env_name # e.g., "youra-h-e1"
conda_cmd = f"source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name}"

# Always read experiment brief for dataset and reality tests
Read(experiment_brief) # Dataset, Reality Tests

# ═══════════════════════════════════════════════════════════════════════════════
# Each task has reference_files linking to specific document sections
# ═══════════════════════════════════════════════════════════════════════════════
ref_files = task.get("reference_files", {})

# 1. Architecture Reference (Epic definition, file targets)
IF ref_files.get("architecture"):
    # ref_files.architecture = "03_architecture.md#Epic-E1"
    arch_ref = ref_files["architecture"]
    Read(architecture_file)
    # Find section matching anchor (e.g., "#Epic-E1")
    anchor = arch_ref.split("#")[1] if "#" in arch_ref else None
    # Extract: Epic description, file_path_from_spec, dependencies
    print(f"📋 Architecture: {arch_ref}")
ELSE:
    Read(architecture_file) # Fallback: read full file

# 2. Logic Reference (API signatures, pseudo-code, tensor shapes)
IF ref_files.get("logic"):
    # ref_files.logic = "03_logic.md#PMLP_API"
    logic_ref = ref_files["logic"]
    Read(logic_file)
    # Find section matching anchor (e.g., "#PMLP_API")
    anchor = logic_ref.split("#")[1] if "#" in logic_ref else None
    # Extract: class_name, methods, tensor_shapes, pseudo-code
    print(f"📋 Logic: {logic_ref}")
ELSE:
    Read(logic_file) # Fallback: read full file

# 3. Config Reference (Hyperparameters, default values)
IF ref_files.get("config"):
    # ref_files.config = "03_config.md#model_config"
    config_ref = ref_files["config"]
    Read(config_file)
    # Find section matching anchor (e.g., "#model_config")
    anchor = config_ref.split("#")[1] if "#" in config_ref else None
    # Extract: config fields, default values, dataclass structure
    print(f"📋 Config: {config_ref}")
ELSE:
    Read(config_file) # Fallback: read full file

# Extract for current task:
# - class_name, methods, tensor_shapes from 03_logic.md (via reference_files.logic)
# - config fields from 03_config.md (via reference_files.config)
# - file_path from 03_architecture.md (via reference_files.architecture)
# - reality_tests from 02c_experiment_brief.md
```

#### 2c. 🧪 TEST: Generate Spec Compliance Tests

> 📖 **Detailed guide:** `{test_gen_guide}`
> ⚠️ **Scope:** Individual test file per task (Validator runs full `tests/` integration)

```python
# 1. Generate test file based on spec understanding (DYNAMIC, not template!)
test_filepath = f"{code_folder}/tests/test_{module_name}.py" # Per-task file!
Write(test_filepath, generated_tests)

# 2. Run pytest - Pre-Implementation Check (IN CONDA ENV!)
result = Bash(f"{conda_cmd} pytest {test_filepath} -v --tb=short")
checkpoint.sdd_metrics.test_attempts += 1

IF result.returncode == 0:
    # Tests passed before impl - module may exist or tests too weak
    IF base_hypothesis_code_copied:
        checkpoint.sdd_metrics.task_sdd_status[task["id"]]["pre_impl_check"] = "base_exists"
    ELSE:
        # Strengthen tests (max 3 retries)
        IF pre_impl_retries < 3:
            GOTO Section_2c # Regenerate stronger tests
        ELSE:
            checkpoint.sdd_metrics.pre_impl_warnings.append(task["id"])
ELSE:
    # ✅ Expected: ImportError (module not exist)
    checkpoint.sdd_metrics.task_sdd_status[task["id"]]["pre_impl_check"] = "passed"
    checkpoint.sdd_metrics.task_sdd_status[task["id"]]["test_created_at"] = now()

SAVE checkpoint
```

#### 2d. ⚙️ IMPL: Implement to Spec

> 📖 **Detailed guide:** `{code_gen_guide}`
> 📖 **MCP fallback policy:** `{mcp_tools_guide}`

```python
# 1. Search Archon KB (MANDATORY!) - : Use search_match_count from complexity
archon_results = mcp__archon__rag_search_knowledge_base(
    query=f"{task_keywords} PyTorch implementation", match_count=search_match_count
)
archon_code = mcp__archon__rag_search_code_examples(
    query=f"{class_name} implementation", match_count=search_match_count
)

# 2. Exa Fallback (if Archon insufficient)
IF len(archon_results["results"]) < 3 OR NOT relevant OR specialized_domain:
    exa_code = mcp__exa__get_code_context_exa(query=...)
    exa_web = mcp__exa__web_search_exa(query=...)

# 3. Generate implementation (DYNAMIC, not template!)
impl_filepath = f"{code_folder}/{file_path_from_spec}"
Write(impl_filepath, generated_implementation)
checkpoint.sdd_metrics.task_sdd_status[task["id"]]["impl_created_at"] = now()

# 4. Run pytest - Spec Compliance Check
impl_attempts = 0
WHILE result.returncode != 0 AND impl_attempts < max_impl_attempts:
    impl_attempts += 1
    error_info = parse_pytest_error(result.stderr)
    fix_results = search_fix_patterns(error_info) # Archon → Exa
    apply_fix(error_info, fix_results)
    result = Bash(f"{conda_cmd} pytest {test_filepath} -v --tb=short")

# 5. Record IMPL result
IF result.returncode == 0:
    checkpoint.sdd_metrics.task_sdd_status[task["id"]]["impl_phase"] = "passed"
    checkpoint.sdd_metrics.impl_phases_passed += 1
ELSE:
    checkpoint.sdd_metrics.task_sdd_status[task["id"]]["impl_phase"] = "failed"
    checkpoint.sdd_metrics.impl_phases_failed += 1
    # Mark for Validator, skip VERIFY - update in checkpoint (NOT Archon)
    checkpoint.tasks.items[task_index]["status"] = "review"
    checkpoint.tasks.items[task_index]["validation_error"] = {
        "phase": "impl",
        "message": "SDD IMPL PHASE FAILED",
        "timestamp": now()
    }
    checkpoint.tasks.summary.in_progress -= 1
    SAVE checkpoint
    CONTINUE

SAVE checkpoint
```

#### 2e. ✅ VERIFY: Polish and Re-verify

> 📖 **Detailed guide:** `{mcp_tools_guide}`

```python
checkpoint.sdd_metrics.task_sdd_status[task["id"]]["verify_started_at"] = now()

# 1. Store pre-polish code for rollback
pre_polish_code = Read(impl_filepath)

# 2. Search best practices from Archon KB (knowledge base, NOT task management)
best_practices = mcp__archon__rag_search_knowledge_base(
    query="PyTorch best practices error handling", match_count=3
)

# 3. Analyze and polish with Serena
mcp__serena__get_symbols_overview(relative_path=impl_filepath)
# Apply polish: error handling, logging, type hints

# 4. Re-verify spec compliance (IN CONDA ENV!)
result = Bash(f"{conda_cmd} pytest {test_filepath} -v --tb=short")

IF result.returncode == 0:
    checkpoint.sdd_metrics.task_sdd_status[task["id"]]["verify_phase"] = "passed"
    checkpoint.sdd_metrics.verify_phases_passed += 1
ELSE:
    # Rollback polish
    Write(impl_filepath, pre_polish_code)
    checkpoint.sdd_metrics.task_sdd_status[task["id"]]["verify_phase"] = "rolled_back"
    checkpoint.sdd_metrics.verify_rollbacks += 1

SAVE checkpoint
```

#### 2f. Update Checkpoint & Transition to Review

```python
# Update file lists
checkpoint.partial_results.code_files_generated.append(impl_filepath)
checkpoint.partial_results.test_files_generated.append(test_filepath)
checkpoint.task_test_mapping[task["id"]] = test_filepath

# Update SDD metrics
checkpoint.sdd_metrics.tasks_completed += 1
checkpoint.sdd_phases[task["id"]] = {
    "test": task_sdd_status["pre_impl_check"],
    "impl": task_sdd_status["impl_phase"],
    "verify": task_sdd_status["verify_phase"]
}

# SDD Order Verification
IF test_created_at > impl_created_at:
    checkpoint.sdd_metrics.sdd_order_violations += 1

# Final spec compliance check (IN CONDA ENV!)
result = Bash(f"{conda_cmd} pytest {test_filepath} -v --tb=short")
IF result.returncode != 0:
    checkpoint.sdd_metrics.final_test_failures += 1
    CONTINUE

# Transition to review - update in checkpoint (NOT Archon)
checkpoint.tasks.items[task_index]["status"] = "review"
checkpoint.tasks.items[task_index]["completed_at"] = now()
checkpoint.tasks.items[task_index]["sdd_phases"] = checkpoint.sdd_phases[task["id"]]
checkpoint.tasks.summary.in_progress -= 1
checkpoint.tasks.summary.completed += 1
checkpoint.tasks.summary.remaining -= 1

checkpoint.task_history.append({
    "task_id": task["id"],
    "status": "review",
    "sdd_phases": checkpoint.sdd_phases[task["id"]],
    "timestamp": now()
})
SAVE checkpoint
```

### 3. Loop Completion

```python
# After all tasks processed
checkpoint.coder_validator_cycles += 1
checkpoint.current_step = 3
SAVE checkpoint
```

---

## 4. PROCEED TO VALIDATOR

### UNATTENDED Auto-Proceed

Display: "**Proceeding to Step 3 (Validator)...**"

#### Menu Handling Logic:

- After all tasks in "review" status, immediately load, read entire file, then execute {nextStepFile}

#### EXECUTION RULES:

- This is an UNATTENDED coder loop step with no user choices
- Proceed directly to Step 3 (Validator) after all tasks are in "review" status
- **Failure to load Step 3 = SYSTEM FAILURE**

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| Checkpoint read fails | Re-read from file, verify schema |
| Code generation fails | Increment retry count in checkpoint, set status to todo |
| Archon KB fails | Log warning, continue (KB is for research, not task mgmt) |
| pytest timeout | Increase timeout, retry |
| Checkpoint save fails | Retry 3x, log error, continue with in-memory state |
| **reference_files missing** | Fallback to reading full document |
| **anchor not found in document** | Log warning, use full document context |

> If reference_files are missing, fall back to reading complete Phase 3 documents.

---

## STEP COMPLETION

**Auto-proceed when:**
- All tasks in checkpoint have status "review" (`checkpoint.tasks.items[*].status == "review"`)
- Checkpoint updated with cycle increment (`checkpoint.coder_validator_cycles += 1`)
- Checkpoint saved to file

**Checkpoint state on completion:**
```yaml
tasks:
  summary:
    completed: {N} # All tasks transitioned
    in_progress: 0 # No tasks in progress
    remaining: 0 # All processed
  items:
    - status: "review" # All items in review
```

**On completion:** Load and execute `{nextStepFile}`
