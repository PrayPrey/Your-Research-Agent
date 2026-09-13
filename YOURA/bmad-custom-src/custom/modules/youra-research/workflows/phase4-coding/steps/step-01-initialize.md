---
name: 'step-01-initialize'
description: 'Initialize Phase 4 workflow - Load inputs, connect Archon, check checkpoint'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'

# File References
thisStepFile: '{workflow_path}/steps/step-01-initialize.md'
nextStepFile: '{workflow_path}/steps/step-01a-data-setup.md'
continueFile: '{workflow_path}/steps/step-01b-continue.md'
workflowFile: '{workflow_path}/workflow.md'

# Input Files
phase3_folder: '{hypothesis_folder}'
prd_file: '{phase3_folder}/03_prd.md'
architecture_file: '{phase3_folder}/03_architecture.md'
logic_file: '{phase3_folder}/03_logic.md'
config_file: '{phase3_folder}/03_config.md'
experiment_brief: '{phase3_folder}/02c_experiment_brief.md'
tasks_file: '{phase3_folder}/03_tasks.yaml' # NEW : Local tasks file from Phase 3
verification_state: '{research_folder}/verification_state.yaml'

# Base Hypothesis (for INCREMENTAL - auto-detected from verification_state.yaml)
base_hypothesis_id: 'auto-detect'
base_hypothesis_id_lower: '{base_hypothesis_id|lower}'
base_hypothesis_folder: '{research_folder}/{base_hypothesis_id_lower}'
base_code_folder: '{base_hypothesis_folder}/code'
target_code_folder: '{hypothesis_folder}/code'

# Output Files
checkpoint_file: '{phase3_folder}/04_checkpoint.yaml'
checkpoint_template: '{workflow_path}/templates/04_checkpoint_template.yaml'

# Helper References
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'
state_validator: '{helpers_path}/state_validator.md'
---

# Step 1: Initialize Phase 4 Workflow (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Execute all sections in sequence - no skipping allowed
- 💾 Update checkpoint after completing initialization
- 🚫 FORBIDDEN to proceed without pipeline verification

---

## EXECUTION SEQUENCE

Execute all sections in order. Auto-proceed on success, STOP only on critical errors.

### 0. State Validation (MANDATORY FIRST STEP)

> See: `helpers/state_validator.md` for implementation details.

```python
# ============================================================================
# STATE VALIDATION - Run before any other processing
# ============================================================================
# Reference: helpers/state_validator.md

from state_validator import full_state_validation, validate_archon_sync

print("🔍 Validating verification_state.yaml...")

# Run full validation with auto-fix enabled
result = full_state_validation(research_folder, auto_fix=True)

# Check validation result
IF NOT result["success"]:
    print("❌ State validation failed!")
    print("\nCritical Errors:")
    for error in result["report"]["errors"]:
        print(f" - {error}")

    # Check if errors are recoverable
    IF any("Critical" in e or "Missing required section" in e for e in result["report"]["errors"]):
        STOP("verification_state.yaml has unrecoverable errors. Run Phase 2B again.")

# Show warnings if any
IF result["report"]["warnings"]:
    print("\n⚠️ Warnings:")
    for warning in result["report"]["warnings"][:5]: # Show first 5
        print(f" - {warning}")

# Show auto-fixes applied
IF result["report"]["auto_fixes_applied"]:
    print("\n✓ Auto-fixes applied:")
    for fix in result["report"]["auto_fixes_applied"]:
        print(f" ✓ {fix}")
    print(f"\n📁 Backup saved to: {result['backup_path']}")

# Store validated state for use in subsequent sections
verification_state = result["state"]

# Optional: Check Archon sync
pipeline_project_id = verification_state.get("metadata", {}).get("pipeline_project_id")
IF pipeline_project_id:
    archon_sync = result["report"].get("archon_sync", {})
    IF archon_sync AND NOT archon_sync.get("synced", True):
        print("\n⚠️ Archon Task Sync Issues:")
        for rec in archon_sync.get("recommendations", [])[:3]:
            print(f" - {rec}")
        # Continue but note the issues

print("✅ State validation completed")
```

| Validation Result | Action |
|-------------------|--------|
| Success (no errors) | Proceed to Section 1 |
| Errors + Auto-fixed | Proceed with fixed state |
| Critical errors | STOP: "verification_state.yaml has unrecoverable errors" |

---

### 1. Verify Hypothesis State

**1a. Read verification_state.yaml**

| Result | Action |
|--------|--------|
| File exists | Proceed to step 1b |
| File not found | STOP: "verification_state.yaml missing. Run Phase 2B first." |

**1b. Check Phase 3 Completion**

Read `hypotheses.{hypothesis_id}.implementation_planning.status`:

| Status | Action |
|--------|--------|
| COMPLETED | Proceed |
| Other | STOP: "Phase 3 not completed. Run /phase3-implementation-planning first." |

**1c. Extract Pipeline Project ID**

```python
# Priority 1: metadata.pipeline_project_id
pipeline_project_id = verification_state["metadata"].get("pipeline_project_id")

# Priority 2: pipeline.project_id
if not pipeline_project_id:
    pipeline_project_id = verification_state.get("pipeline", {}).get("project_id")
    if pipeline_project_id:
        print("⚠ Using fallback location: pipeline.project_id")

# Priority 3: Per-hypothesis project
if not pipeline_project_id:
    pipeline_project_id = verification_state.get("sub_hypotheses", {}).get(
        hypothesis_id, {}
    ).get("implementation_planning", {}).get("archon_project_id")
    if pipeline_project_id:
        print("⚠ Using location: implementation_planning.archon_project_id")

# Priority 4: Raise explicit error (no unreliable search fallback)
if not pipeline_project_id:
    STOP(
        "Pipeline Project ID not found in verification_state.yaml.\n"
        "Expected locations:\n"
        " - metadata.pipeline_project_id\n"
        " - pipeline.project_id\n"
        "Resolution:\n"
        " 1. Run Phase 0 to create Pipeline Project, OR\n"
        " 2. Add pipeline_project_id manually"
    )

# Store for later use
archon_project_id = pipeline_project_id # Alias for compatibility
```

**1d. Check Prerequisites (for dependent hypotheses)**

Read `prerequisites` array from current hypothesis. For each prerequisite:

| Prerequisite Status | Gate Type | Action |
|---------------------|-----------|--------|
| `validation.status` ≠ COMPLETED | MUST_WORK | STOP: "Prerequisite {prereq_id} (MUST_WORK) not completed" |
| `validation.status` ≠ COMPLETED | SHOULD_WORK | Log warning, continue |
| `validation.status` = COMPLETED | MUST_WORK + `gate.satisfied` = false | STOP: "Prerequisite {prereq_id} (MUST_WORK) failed" |
| `validation.status` = COMPLETED | SHOULD_WORK + `gate.satisfied` = false | Log warning, continue |
| `validation.status` = COMPLETED | `gate.satisfied` = true | Continue |

### 2. Check for Existing Checkpoint

Check if `{checkpoint_file}` exists:

| Condition | Action |
|-----------|--------|
| File exists AND `current_step` > 1 | Load `{continueFile}` for resume (STOP here - continue file handles the rest) |
| File exists AND `current_step` = 1 | Continue to step 3 |
| File does not exist | Continue to step 3 |

### 3. Verify Phase 3 Outputs (Existence Only)

**Required files to verify:**

| File | Path |
|------|------|
| PRD | `{prd_file}` (03_prd.md) |
| Architecture | `{architecture_file}` (03_architecture.md) |
| Logic | `{logic_file}` (03_logic.md) |
| Config | `{config_file}` (03_config.md) |
| Experiment Brief | `{experiment_brief}` (02c_experiment_brief.md) |
| Tasks | `{tasks_file}` (03_tasks.yaml) | **NEW** |

**Verification result:**

| Result | Action |
|--------|--------|
| All files exist | Continue to step 4 |
| Any file missing | STOP: "Missing required file: {file_path}" |

### 4. Check Previous Hypothesis Code (If INCREMENTAL)

**4a. Determine hypothesis type from prerequisites:**

| Prerequisites | Hypothesis Type | Action |
|---------------|-----------------|--------|
| Non-empty array | INCREMENTAL | Extract base hypothesis ID (first prerequisite) |
| Empty array | FOUNDATION | Skip to step 5, set `code_copied` = false |

**4b. For INCREMENTAL hypotheses:**

Base code folder path: `{research_folder}/{base_hypothesis_id_lower}/code/`

| Base Code Folder | Action |
|------------------|--------|
| Exists | Copy code to `{target_code_folder}` using `cp -r`, set `code_copied` = true |
| Does not exist | Set `code_copied` = false, continue |

**Store variables:**
- `hypothesis_type`: FOUNDATION or INCREMENTAL
- `base_hypothesis_id`: First prerequisite ID (if INCREMENTAL)
- `code_copied`: true/false
- `copied_files`: List of copied files (if copied)

### 5. Load Tasks and Update Hypothesis Status

> Archon is only used to update Hypothesis Task status to "doing".

**5a. Read tasks from local file:**

```python
import yaml

# Read 03_tasks.yaml (generated by Phase 3 step-09)
with open(tasks_file, 'r') as f:
    tasks_data = yaml.safe_load(f)

# Extract tasks list
tasks_list = tasks_data.get("tasks", [])
task_count = len(tasks_list)
tier = tasks_data.get("metadata", {}).get("tier", "LIGHT")
total_budget = tasks_data.get("metadata", {}).get("total_budget", 15)

print(f"✓ Loaded {task_count} tasks from 03_tasks.yaml")
print(f" Tier: {tier} (budget: {total_budget})")

# Validate task count
if task_count == 0:
    STOP("No tasks found in 03_tasks.yaml. Run Phase 3 step-09 again.")

if task_count > total_budget:
    print(f"⚠ Task count ({task_count}) exceeds budget ({total_budget})")

# Store for checkpoint initialization
loaded_tasks = tasks_list
```

**5b. Update Hypothesis Task status in Archon (single MCP call):**

```python
# Get hypothesis_task_id from verification_state
hypothesis_task_id = verification_state.get("metadata", {}).get(
    "hypothesis_task_mapping", {}
).get(hypothesis_id.lower())

if hypothesis_task_id:
    result = mcp__archon__manage_task(
        action="update",
        task_id=hypothesis_task_id,
        status="doing"
    )
    if result.get("success"):
        print(f"✓ Hypothesis Task {hypothesis_task_id} marked as 'doing'")
    else:
        print(f"⚠ Failed to update Hypothesis Task status")
else:
    print(f"⚠ Hypothesis Task ID not found in verification_state (continuing without Archon update)")
```

> **Note:** Implementation tasks are NO LONGER in Archon. They are tracked locally via 04_checkpoint.yaml.

### 5.5 Create Conda Virtual Environment (MANDATORY)

```bash
# Step 1: Detect conda path (CRITICAL!)
CONDA_EXE=$(which conda)
IF NOT exists:
    # Try common locations
    FOR path IN ["/home/anonymous/miniforge3", "/home/anonymous/miniconda3", "/opt/conda", "/usr/local/conda"]:
        IF exists "{path}/bin/conda":
            CONDA_EXE = "{path}/bin/conda"
            break

IF CONDA_EXE is null:
    STOP("Conda not found. Install miniforge3 or miniconda first.")

# Extract conda base path from executable
CONDA_PATH = dirname(dirname(CONDA_EXE)) # e.g., "/home/anonymous/miniforge3"

# Step 2: Initialize conda for this shell
source {CONDA_PATH}/etc/profile.d/conda.sh

# Step 3: Environment name based on hypothesis_id (lowercase, replace special chars)
env_name = "youra-{hypothesis_id_lower}" # e.g., "youra-h-e1"

# Step 4: Check if environment already exists
conda env list | grep {env_name}

IF environment NOT exists:
    # Create new conda environment with Python 3.10
    conda create -n {env_name} python=3.10 -y

    # Verify creation
    conda env list | grep {env_name}
    IF NOT exists: STOP("Failed to create conda environment")

# Step 5: Store BOTH environment name AND conda path for later steps
Store: conda_env_name = env_name
Store: conda_path = CONDA_PATH # NEW: Also store the path!
```

**CRITICAL: All subsequent package installations and executions MUST use this environment.**

Activation command for later steps:
```bash
# ALWAYS source conda first, then activate
source {conda_path}/etc/profile.d/conda.sh
conda activate {env_name}
```

### 5.6 GPU Detection & Status (MANDATORY)

🚨 **Check GPU status early to determine experiment execution strategy**

```bash
# Step 1: Check NVIDIA GPU availability
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader 2>/dev/null

IF nvidia-smi succeeds:
    gpu_available = true
    gpu_info = parse_gpu_output() # e.g., "NVIDIA GeForce RTX 3090, 24576MiB, 23000MiB"
    gpu_count = count_gpus()
    print(f"GPU: {gpu_count}x detected")
ELSE:
    gpu_available = false
    gpu_info = "No GPU detected"
    print("GPU: None (CPU mode)")

# Step 2: Check PyTorch CUDA in conda env (if GPU detected)
IF gpu_available:
    source {CONDA_PATH}/etc/profile.d/conda.sh
    conda run -n {env_name} python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')" 2>/dev/null

    IF torch.cuda.is_available() == False AND gpu_available:
        pytorch_cuda_needed = true
    ELSE:
        pytorch_cuda_needed = false

# Step 3: Store GPU status for checkpoint
Store: gpu_available = {gpu_available}
Store: gpu_info = "{gpu_info}"
Store: gpu_count = {gpu_count}
Store: pytorch_cuda_needed = {pytorch_cuda_needed}
```

### 6. Initialize Checkpoint

> This ensures consistency with 04_checkpoint_template.yaml (Single Source of Truth).

```python
import yaml
from datetime import datetime

# ============================================================================
# STEP 6a: Load checkpoint template
# ============================================================================
# Reference: {workflow_path}/templates/04_checkpoint_template.yaml
print("📋 Loading checkpoint template...")

template_path = checkpoint_template # From frontmatter
template_content = Read(template_path)
checkpoint = yaml.safe_load(template_content)

print(f"✓ Template loaded (format version: {checkpoint.get('schema_version', 'unknown')})")

# ============================================================================
# STEP 6b: Fill dynamic values (replace {{placeholders}})
# ============================================================================
print("🔧 Filling dynamic values...")

# Timestamps
timestamp = datetime.now().isoformat()

# Prepare dynamic values map
dynamic_values = {
    "hypothesis_id": hypothesis_id,
    "timestamp": timestamp,
    "task_count": task_count,
    "unattended_mode": True, # Default for UNATTENDED pipeline
    "pipeline_project_id": pipeline_project_id,
    "hypothesis_task_id": hypothesis_task_id or "null",
    "conda_env_name": conda_env_name,
    "conda_path": conda_path,
    "gpu_available": gpu_available,
    "gpu_info": gpu_info or "null",
    "gpu_count": gpu_count,
    "pytorch_cuda_needed": pytorch_cuda_needed,
    "hypothesis_folder": hypothesis_folder,
    "hypothesis_type": hypothesis_type,
    "base_hypothesis_id": base_hypothesis_id or "null",
    "base_code_folder": base_code_folder or "null",
    "code_copied": code_copied,
    "copied_files": copied_files or []
}

# Fill placeholders in checkpoint
def fill_placeholders(obj, values):
    """Recursively replace {{placeholder}} in checkpoint with actual values."""
    if isinstance(obj, dict):
        return {k: fill_placeholders(v, values) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fill_placeholders(item, values) for item in obj]
    elif isinstance(obj, str):
        # Replace {{placeholder}} patterns
        for key, val in values.items():
            placeholder = "{{" + key + "}}"
            if placeholder in obj:
                # If entire string is placeholder, return value directly (preserve type)
                if obj == placeholder:
                    return val
                # Otherwise, string replace
                obj = obj.replace(placeholder, str(val) if val is not None else "null")
        return obj
    return obj

checkpoint = fill_placeholders(checkpoint, dynamic_values)

print(f"✓ Dynamic values filled")

# ============================================================================
# STEP 6c: Populate tasks.items[] from loaded_tasks
# ============================================================================
print("📝 Populating tasks from 03_tasks.yaml...")

checkpoint_tasks = []
for task in loaded_tasks:
    checkpoint_tasks.append({
        "id": task["id"],
        "title": task["title"],
        "status": "todo",
        "output_file": None,
        "test_file": None,
        "started_at": None,
        "completed_at": None,
        "sdd_phases": {"TEST": None, "IMPL": None, "VERIFY": None},
        "retry_count": 0,
        "priority": task.get("priority", 0), # Priority score (higher = first)
        "complexity": task.get("complexity"), # Complexity score from Phase 3
        "epic": task.get("epic"), # Parent epic name
        "description": task.get("description"), # Task description
        "feature_tag": task.get("feature_tag"), # Category tag
        "reference_files": task.get("reference_files", {
            "architecture": None,
            "logic": None,
            "config": None
        })
    })

checkpoint["tasks"]["items"] = checkpoint_tasks
checkpoint["tasks"]["summary"]["total"] = len(checkpoint_tasks)
checkpoint["tasks"]["summary"]["remaining"] = len(checkpoint_tasks)

print(f"✓ Loaded {len(checkpoint_tasks)} tasks with priority + Phase 3 metadata")

# ============================================================================
# STEP 6d: Write checkpoint file
# ============================================================================
Write(checkpoint_file, yaml.dump(checkpoint, default_flow_style=False, allow_unicode=True))
print(f"✓ Checkpoint saved: {checkpoint_file}")
```

### 7. Proceed to Next Step

**Update checkpoint:**
- Set `current_step` = 2
- Save checkpoint file

**Load next step:** Read entire file `{nextStepFile}` and execute.

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| Missing Phase 3 file | STOP with specific file error |
| **03_tasks.yaml missing** | STOP: "Run Phase 3 step-09 to generate tasks file" |
| **03_tasks.yaml empty** | STOP: "No tasks in 03_tasks.yaml" |
| **03_tasks.yaml invalid schema** | STOP: "Invalid 03_tasks.yaml schema" |
| pipeline_project_id null | STOP with instructions to run Phase 0 |
| Hypothesis Task update failed | Log warning, continue (non-blocking) |
| Checkpoint corrupted | Delete and restart |
| verification_state.yaml not found | STOP - Phase 2B incomplete |

---

## STEP COMPLETION

**Auto-proceed to `{nextStepFile}` when:**
1. All inputs verified (including 03_tasks.yaml)
2. Tasks loaded from 03_tasks.yaml
3. Hypothesis Task status updated in Archon (if available)
4. Conda environment created
5. GPU status detected
6. Checkpoint created with tasks.items[] populated

**On completion:** Load, read entire file, then execute `{nextStepFile}` (step-01a-data-setup.md)

---

#

For workflows upgrading from :
- Each task now has `reference_files` field linking to Phase 3 document sections
- `reference_files.architecture`: Link to 03_architecture.md Epic section
- `reference_files.logic`: Link to 03_logic.md API section
- `reference_files.config`: Link to 03_config.md config section
- Phase 4 Coder reads these references before implementing each task
- If `03_tasks.yaml` lacks reference_files, run Phase 3 step-09 again
