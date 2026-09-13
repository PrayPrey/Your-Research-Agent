---
name: 'step-04-experiment-confirm'
description: 'Experiment Execution Confirmation - Load experiment brief and auto-select execution option'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'

# File References
thisStepFile: '{workflow_path}/steps/step-04-experiment-confirm.md'
nextStepFile: '{workflow_path}/steps/step-05a-pre-validation.md'
workflowFile: '{workflow_path}/workflow.md'

# Input Files
experiment_brief: '{hypothesis_folder}/02c_experiment_brief.md'
verification_state: '{research_folder}/verification_state.yaml'

# Output Files
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'
---

## Section 0.5: Load Checkpoint

> This ensures checkpoint state is available even after session interruption.

```python
# MANDATORY: Read checkpoint from file (context loss prevention)
checkpoint = read_yaml(checkpoint_file) # {hypothesis_folder}/04_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-initialize first.")

IF checkpoint.current_step < 4:
    STOP("ERROR: Step sequence violation. Current step: {checkpoint.current_step}")

# Log checkpoint load for debugging
print(f"✅ Checkpoint loaded: step={checkpoint.current_step}, dry_run={checkpoint.dry_run.status}")
```

---

# Step 4: Experiment Execution Confirmation (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- MUST execute dry run before proceeding to full experiment
- MUST check for mock data before experiment execution
- MUST create Archon task on dry run failure
- Maximum 3 dry run retries before marking as blocked
- Auto-select "Auto" execution mode (no user interaction)

---

## STEP GOAL

Load the experiment brief from Phase 2C, extract success criteria, and auto-select "Auto" execution mode.

---

## EXECUTION SEQUENCE

### 1. Load Experiment Brief

```python
Read(experiment_brief)

# Extract key information
experiment_info = {
    "objective": extract("Experiment objective"),
    "hypothesis": extract("Hypothesis being tested"),
    "success_criteria": extract("Success criteria (quantitative)"),
    "runtime_estimate": extract("Expected runtime"),
    "resource_requirements": extract("GPU, memory"),
    "dataset_specs": extract("Dataset specifications")
}
```

### 2. Load Verification State

```python
Read(verification_state)

gate_info = {
    "type": hypothesis["gate"]["type"], # MUST_WORK | SHOULD_WORK
    "criteria": hypothesis["gate"]["criteria"],
    "status": hypothesis["status"]
}
```

### 3. Auto-Select Execution Option

```python
# UNATTENDED Mode: Auto-select "Auto" execution
checkpoint.experiment_option = "auto"
checkpoint.partial_results.experiment_status = "pending"
```

### 4. Dry Run (Sanity Check)

Run a quick sanity check with minimal data before committing to full experiment.

**Dry Run Configuration:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Epochs | 1 | Minimal training |
| Data subset | 1-5% or max 100 samples | Fast execution |
| Seeds | 1 | Single run only |
| LR | 1 (middle value) | Representative test |

**Execute Dry Run:**

```python
# Create dry run config
dry_run_config = {
    "epochs": 1,
    "data_subset": 0.01, # 1% of data or max 100 samples
    "seed": 0,
    "lr": experiment_info.get("learning_rates", [0.1])[len(lr_list)//2]
}

# Run dry run experiment
dry_run_result = execute_experiment(
    code_path="{hypothesis_folder}/code/",
    config=dry_run_config,
    timeout=300 # 5 minute timeout
)
```

**Dry Run Result Handling:**

| Result | Action |
|--------|--------|
| **Success** | Log "Dry run passed", proceed to Section 5 |
| **Error** | Analyze error, create fix task, return to Step 2 |

**On Dry Run Error:**

```python
IF dry_run_result.status == "error":
    # Analyze error
    error_type = classify_error(dry_run_result.error)

    # step-02 reads tasks from checkpoint.tasks.items, not from Archon
    fix_task = {
        "id": f"fix-dryrun-{str(uuid4())[:8]}",
        "title": f"[DRY RUN FIX] {error_type}",
        "description": f"Error: {dry_run_result.error}\nStack trace: {dry_run_result.stacktrace}",
        "status": "todo",
        "priority": 100, # Highest priority
        "created_at": now(),
        "source": "step-04-dryrun-error"
    }
    checkpoint.tasks.items.append(fix_task)
    checkpoint.tasks.summary.remaining += 1

    # Update checkpoint
    checkpoint.dry_run.status = "failed"
    checkpoint.dry_run.error = dry_run_result.error
    checkpoint.dry_run.retry_count += 1

    IF checkpoint.dry_run.retry_count >= 3:
        # Max retries reached, mark as blocked
        checkpoint.partial_results.experiment_status = "blocked"
        STOP with error report
    ELSE:
        # Return to Step 2 for fix
        checkpoint.current_step = 2
        SAVE checkpoint
        Load, read entire file, then execute: step-02-coder-loop.md
```

**On Dry Run Success:**

```python
IF dry_run_result.status == "success":
    checkpoint.dry_run.status = "passed"
    checkpoint.dry_run.completed_at = now()
    checkpoint.dry_run.metrics = dry_run_result.metrics
    # Proceed to Section 4.5 (Pre-execution Mock Check)
```

### 4.5 Pre-Execution Mock Data Check (MANDATORY - Before Full Experiment!)

🚨 **CRITICAL: Detect mock data BEFORE wasting compute on full experiment**

This check runs AFTER dry run passes but BEFORE full experiment execution.
Catching mock data here saves hours of wasted compute time.

```python
# Step 1: Scan for mock/synthetic data configurations (EXCLUDE tests!)
mock_config_scan = mcp__serena__search_for_pattern(
    substring_pattern="(use_synthetic|mock_mode|fake_data|dummy_data)\\s*[=:]\\s*(true|True|1|yes)",
    relative_path=code_folder,
    paths_include_glob="*.py,*.yaml,*.yml,*.json,*.toml",
    paths_exclude_glob="**/tests/**,**/test_*.py", # Exclude test files!
    context_lines_before=1,
    context_lines_after=1
)

# Step 2: Check for synthetic data generation in main code (not tests)
mock_code_scan = mcp__serena__search_for_pattern(
    substring_pattern="(generate_synthetic|create_mock|fake_|from faker import|import mimesis)",
    relative_path=f"{code_folder}",
    paths_include_glob="*.py",
    paths_exclude_glob="**/tests/**,**/test_*.py", # Exclude test files!
    context_lines_before=2,
    context_lines_after=2
)

# Step 3: Evaluate results
mock_indicators = []

IF mock_config_scan.matches:
    FOR match in mock_config_scan.matches:
        mock_indicators.append({
            "type": "config_flag",
            "file": match.file,
            "line": match.line,
            "content": match.content
        })

IF mock_code_scan.matches:
    FOR match in mock_code_scan.matches:
        # Skip if in data loading context (legitimate synthetic augmentation)
        IF "augment" not in match.content.lower():
            mock_indicators.append({
                "type": "code_pattern",
                "file": match.file,
                "line": match.line,
                "content": match.content
            })

# Step 4: Handle detection
IF len(mock_indicators) > 0:
    print("❌ MOCK DATA DETECTED BEFORE EXPERIMENT!")
    print("Detected indicators:")
    FOR indicator in mock_indicators:
        print(f" - {indicator.type}: {indicator.file}:{indicator.line}")
        print(f" {indicator.content}")

    # step-02 reads tasks from checkpoint.tasks.items, not from Archon
    fix_task = {
        "id": f"fix-mock-{str(uuid4())[:8]}",
        "title": "[PRE-CHECK MOCK FIX] Remove mock data usage",
        "description": f"""Mock data detected BEFORE experiment execution.

Indicators found:
{format_indicators(mock_indicators)}

Required fixes:
1. Remove synthetic/mock data flags from config
2. Implement real dataset loading per 02c_experiment_brief.md
3. Remove faker/mimesis usage in main code (tests are OK)

Note: Test files are allowed to use mock data.""",
        "status": "todo",
        "priority": 100, # Highest priority
        "created_at": now(),
        "source": "step-04-mock-detection"
    }
    checkpoint.tasks.items.append(fix_task)
    checkpoint.tasks.summary.remaining += 1

    # Update checkpoint
    checkpoint.pre_mock_check = {
        "status": "failed",
        "indicators": mock_indicators,
        "checked_at": now()
    }
    checkpoint.current_step = 2
    SAVE checkpoint

    # Return to Step 2 (Coder Loop) for fix
    print("⚠️ Returning to Step 2 for mock data fix...")
    Load, read entire file, then execute: step-02-coder-loop.md
    STOP # Do not proceed to Section 5!

ELSE:
    print("✅ Pre-execution mock check passed (no mock data in main code)")
    checkpoint.pre_mock_check = {
        "status": "passed",
        "checked_at": now()
    }
```

### 5. Update Checkpoint

```python
checkpoint.current_step = 4
checkpoint.partial_results.experiment_option = "auto"
checkpoint.partial_results.experiment_status = "pending"
checkpoint.partial_results.experiment_info = experiment_info
checkpoint.partial_results.gate_info = gate_info
checkpoint.dry_run.status = "passed" # Only reached if dry run succeeded
checkpoint.updated_at = now()
SAVE checkpoint
```

### 6. Proceed to Next Step

```python
checkpoint.current_step = 5
SAVE checkpoint

# Load and execute next step
Load, read entire file, then execute: {nextStepFile}
```

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| 02c_experiment_brief.md not found | STOP - file is required |
| verification_state.yaml not found | Proceed with default gate type |
| Dry run error | Create fix task, return to Step 2 |
| Dry run timeout | Retry with smaller data subset |
| Dry run max retries (3) | Mark as blocked, STOP |

---

## STEP COMPLETION

**Auto-proceed to `{nextStepFile}` when:**
1. Experiment brief loaded
2. Gate info extracted
3. "Auto" execution mode selected
4. **Dry run passed successfully**
5. Checkpoint updated

**On dry run failure:** Return to Step 2 (Coder Loop) for fix

**On completion:** Load, read entire file, then execute `{nextStepFile}` (step-05-experiment-execute.md)

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Experiment brief loaded and parsed
- Gate info extracted from verification_state.yaml
- Dry run executed with minimal config (1 epoch, 1% data)
- Dry run completed without errors
- "Auto" execution mode selected
- Checkpoint updated with dry_run.status = "passed"

### ❌ SYSTEM FAILURE:

- Skipping dry run step
- Proceeding to Step 5 without dry run success
- Not creating fix task on dry run error
- Exceeding 3 dry run retries without blocking
