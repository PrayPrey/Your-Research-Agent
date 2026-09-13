---
name: 'step-05a-pre-validation'
description: 'Pre-Experiment Validation - Dataset verification and Mock data detection'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'

# File References (order-independent references)
thisStepFile: '{workflow_path}/steps/step-05a-pre-validation.md'
nextStepFile: '{workflow_path}/steps/step-05b-execution.md'
prevStepFile: '{workflow_path}/steps/step-04-experiment-confirm.md'
coderStepFile: '{workflow_path}/steps/step-02-coder-loop.md'
workflowFile: '{workflow_path}/workflow.md'

# Step 5 Sub-steps (for cross-reference)
step5a: '{workflow_path}/steps/step-05a-pre-validation.md'
step5b: '{workflow_path}/steps/step-05b-execution.md'
step5c: '{workflow_path}/steps/step-05c-post-validation.md'

# Input Files
experiment_brief: '{hypothesis_folder}/02c_experiment_brief.md'
code_folder: '{hypothesis_folder}/code'

# Output Files
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'
terminal_log: '{code_folder}/terminal.log'

# Helper References
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'
mock_detection: '{helpers_path}/mock_detection.md'
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
print(f"✅ Checkpoint loaded: step={checkpoint.current_step}, dry_run={checkpoint.dry_run.status}")
```

---

# Step 5A: Pre-Experiment Validation (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required
> **Part:** 1 of 3 (5A → 5B → 5C)

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- Verify 02c dataset existence before experiment
- Detect Mock/Synthetic data usage in code
- Initialize terminal log for experiment tracking

---

## STEP GOAL

Pre-experiment mandatory validations:
1. Initialize terminal log
2. Verify 02c dataset existence
3. Detect Mock/Synthetic data usage in code
4. Verify dataset is actually used in code

---

## EXECUTION SEQUENCE

### 1. Initialize Terminal Log (MANDATORY)

🚨 **terminal.log records KEY EVENTS only (not all commands)**

```python
terminal_log = f"{code_folder}/terminal.log"

# Create terminal log header
terminal_header = f"""
================================================================================
🖥️ YouRA EXPERIMENT LOG
================================================================================
Hypothesis ID: {hypothesis_id}
Started At: {ISO8601_now}
Environment: {checkpoint.conda.env_name}
GPU Available: {checkpoint.gpu.available}

================================================================================
KEY EVENTS:
================================================================================

"""

Write(file_path=terminal_log, content=terminal_header)

# Helper function: Log KEY events only (not every command)
def log_event(event_type, message):
    '''Append key event to terminal.log'''
    Bash: echo "[{ISO8601_now}] [{event_type}] {message}" >> {terminal_log}
```

### 1.5 Dataset Existence Verification (MANDATORY)

🚨 **Verify 02c_experiment_brief.md dataset specs are satisfied BEFORE experiment**

```python
# Read experiment brief for dataset specifications
experiment_brief = Read(f"{hypothesis_folder}/02c_experiment_brief.md")

# Extract dataset specs (look for Dataset section)
dataset_section = extract_section(experiment_brief, "Dataset|Data")

dataset_info = {
    "name": extract_field(dataset_section, "name|dataset"),
    "path": extract_field(dataset_section, "path|location"),
    "size": extract_field(dataset_section, "size|samples"),
    "type": extract_field(dataset_section, "type") # custom, standard, etc.
}

print(f"📊 Dataset from 02c: {dataset_info.name}")

# Check 1: Custom dataset path
IF dataset_info.path AND dataset_info.path != "auto":
    expanded_path = expand_path(dataset_info.path) # Handle ~, env vars

    IF NOT file_or_dir_exists(expanded_path):
        error_msg = f"""
❌ DATASET NOT FOUND!

Specified in 02c_experiment_brief.md:
  Name: {dataset_info.name}
  Path: {dataset_info.path}
  Expanded: {expanded_path}

Please download the dataset before running the experiment.
Check the dataset URL/instructions in 02c_experiment_brief.md.
"""
        print(error_msg)
        log_event("ERROR", f"Dataset not found: {dataset_info.path}")

        checkpoint.dataset_verification = {
            "status": "failed",
            "reason": "path_not_found",
            "path": dataset_info.path,
            "checked_at": now()
        }
        SAVE checkpoint
        STOP("Dataset not found. Cannot proceed with experiment.")
    ELSE:
        # Check dataset size (non-empty)
        size_check = Bash: du -sh {expanded_path}
        print(f"✅ Dataset found: {expanded_path} ({size_check})")

# Check 2: Standard datasets (CIFAR, MNIST, ImageNet, etc.)
STANDARD_DATASETS = ["cifar10", "cifar100", "mnist", "fashionmnist", "imagenet",
                     "coco", "voc", "cityscapes", "ptb", "wikitext"]

IF dataset_info.name.lower() in STANDARD_DATASETS:
    # Check common cache locations
    cache_paths = [
        f"~/.cache/torch/datasets/{dataset_info.name}",
        f"~/.torch/datasets/{dataset_info.name}",
        f"./data/{dataset_info.name}",
        f"{code_folder}/data/{dataset_info.name}"
    ]

    found = False
    for cache_path in cache_paths:
        IF dir_exists(expand_path(cache_path)):
            found = True
            print(f"✅ Standard dataset cached: {cache_path}")
            break

    IF NOT found:
        print(f"⚠️ Standard dataset '{dataset_info.name}' not cached.")
        print(" Will be downloaded automatically on first run.")
        print(" This may add time to the experiment start.")

# Check 3: Verify data loading code exists
data_loader_check = mcp__serena__search_for_pattern(
    substring_pattern="(DataLoader|load_data|get_dataset|Dataset)",
    relative_path=f"{code_folder}",
    paths_include_glob="*.py",
    paths_exclude_glob="**/tests/**"
)

IF NOT data_loader_check.matches:
    print("⚠️ No DataLoader pattern found in code. Verify data loading implementation.")

# Update checkpoint
checkpoint.dataset_verification = {
    "status": "passed",
    "dataset_name": dataset_info.name,
    "dataset_path": dataset_info.path,
    "checked_at": now()
}
SAVE checkpoint

log_event("DATA", f"Dataset verified: {dataset_info.name}")
print("✅ Dataset verification completed")
```

### 1.6 Mock/Synthetic Data Detection (MANDATORY - LLM-Based Verification)

🚨 **CRITICAL: LLM-based verification for Mock/Synthetic data usage**

> **Reference:** `helpers/mock_detection.md` - LLM-based reality verification

```python
# ============================================================================
# 🔍 LLM-BASED MOCK/SYNTHETIC DATA VERIFICATION
# ============================================================================
# The LLM reads checkpoint and analyzes if data setup appears to use real data

from mock_detection import detect_mock_usage

print("🔍 LLM verifying data setup for mock/synthetic usage...")

# LLM-based verification with "Expected vs Actual" comparison
# Note: In pre-validation, experiment.log and experiment_results.json don't exist yet
# But 02c_experiment_brief.md is available for expected values comparison
mock_result = detect_mock_usage(
    code_folder=code_folder,
    detection_type="data",
    checkpoint_file=f"{hypothesis_folder}/04_checkpoint.yaml",
    experiment_log_file=None, # No log yet in pre-validation
    experiment_results_file=None, # No results yet in pre-validation
    experiment_brief_file=f"{hypothesis_folder}/02c_experiment_brief.md" # Expected values available
)

# Process LLM verification result
IF mock_result["detected"]:
    print("🚨 MOCK/SYNTHETIC DATA DETECTED BY LLM VERIFICATION!")
    print("=" * 60)
    print(f"Summary: {mock_result['summary']}")
    print(f"Severity: {mock_result['severity']}")
    print(f"Confidence: {mock_result.get('confidence', 'N/A')}")
    print()
    print("LLM Reasoning:")
    print(f" {mock_result.get('llm_reasoning', 'See violations')}")
    print()

    FOR violation IN mock_result.get("violations", []):
        print(f"❌ Issue: {violation.get('description', violation.get('type', 'Unknown'))}")
        print(f" Severity: {violation.get('severity', 'N/A')}")

    log_event("ERROR", f"LLM detected mock data: {mock_result['summary']}")

    # Record in checkpoint
    checkpoint.mock_data_check = {
        "status": "FAILED",
        "method": "llm_verification",
        "violations": mock_result.get("violations", []),
        "severity": mock_result.get("severity"),
        "llm_reasoning": mock_result.get("llm_reasoning"),
        "confidence": mock_result.get("confidence"),
        "checked_at": now()
    }
    SAVE checkpoint

    # 🚨 CRITICAL: Return to Step 2 for code fix
    print("⚠️ CRITICAL: LLM detected mock/synthetic data usage!")
    print(" Main code must use REAL dataset specified in 02c_experiment_brief.md")
    print(" Returning to Step 2 for code fix...")

    # Add fix task to Local checkpoint (NOT Archon)
    fix_task = {
        "id": f"fix-mock-{str(uuid4())[:8]}",
        "title": "[MOCK DATA FIX] Replace mock/synthetic data with real dataset",
        "description": f"""🚨 Mock/Synthetic data detected by LLM verification!

{mock_result.get('summary', 'See details')}

**LLM Analysis:**
{mock_result.get('llm_reasoning', 'N/A')}

**Required dataset from 02c:** {dataset_info.name}
**Expected path:** {dataset_info.path}

**FIX REQUIRED:**
1. Remove all mock/synthetic data generation
2. Load actual dataset: {dataset_info.name}
3. Ensure DataLoader uses real data path
4. tests/ can keep mock data, but main code MUST NOT

**Severity:** {mock_result.get('severity', 'N/A')}
**Confidence:** {mock_result.get('confidence', 'N/A')}""",
        "status": "todo",
        "priority": 100, # Highest priority
        "created_at": now(),
        "source": "step-05a-llm-mock-detection"
    }
    checkpoint.tasks.items.append(fix_task)
    checkpoint.tasks.summary.remaining += 1

    checkpoint.current_step = 2
    checkpoint.return_reason = "mock_data_detected"
    SAVE checkpoint

    Load, read entire file, then execute: {coderStepFile}
    STOP

ELSE:
    print("✅ LLM verification passed - data setup appears real")
    print(f" {mock_result.get('summary', 'No mock data detected')}")

    checkpoint.mock_data_check = {
        "status": "PASSED",
        "method": "llm_verification",
        "confidence": mock_result.get("confidence"),
        "checked_at": now()
    }
    SAVE checkpoint
    log_event("CHECK", "LLM mock data verification passed")
```

### 1.7 Dataset Usage Verification (MANDATORY - Strengthens Issue 2)

🚨 **Verify that the dataset specified in 02c is actually loaded in code**

```python
# ============================================================================
# 📊 DATASET USAGE VERIFICATION
# ============================================================================
# Problem: Dataset path exists but verify if code actually uses this dataset

print(f"🔍 Verifying code uses dataset: {dataset_info.name}")

dataset_usage_found = False
dataset_usage_evidence = []

# Check 1: Verify dataset name is referenced in code
dataset_name_patterns = [
    dataset_info.name,
    dataset_info.name.lower(),
    dataset_info.name.upper(),
    dataset_info.name.replace("-", "_"),
    dataset_info.name.replace("_", "-")
]

FOR pattern IN dataset_name_patterns:
    result = mcp__serena__search_for_pattern(
        substring_pattern=pattern,
        relative_path=f"{code_folder}",
        paths_include_glob="*.py",
        paths_exclude_glob="**/tests/**"
    )

    IF result.matches:
        dataset_usage_found = True
        dataset_usage_evidence.extend(result.matches)

# Check 2: Verify dataset path is used in code
IF dataset_info.path:
    path_pattern = dataset_info.path.replace("/", r"[/\\]") # Handle both / and \
    path_result = mcp__serena__search_for_pattern(
        substring_pattern=path_pattern,
        relative_path=f"{code_folder}",
        paths_include_glob="*.py,*.yaml,*.json"
    )

    IF path_result.matches:
        dataset_usage_found = True
        dataset_usage_evidence.extend(path_result.matches)

# Check 3: Standard dataset loaders (torchvision, datasets, etc.)
IF dataset_info.name.lower() in STANDARD_DATASETS:
    standard_loader_patterns = [
        f"torchvision.datasets.{dataset_info.name}",
        f"datasets.load_dataset.*{dataset_info.name}",
        f"CIFAR10|CIFAR100|MNIST|ImageNet" # Common capitalization
    ]

    FOR pattern IN standard_loader_patterns:
        result = mcp__serena__search_for_pattern(
            substring_pattern=pattern,
            relative_path=f"{code_folder}",
            paths_include_glob="*.py"
        )
        IF result.matches:
            dataset_usage_found = True
            dataset_usage_evidence.extend(result.matches)

# Process results
IF NOT dataset_usage_found:
    print(f"⚠️ WARNING: Dataset '{dataset_info.name}' not found in code!")
    print(" The code may not be using the correct dataset.")

    log_event("WARN", f"Dataset {dataset_info.name} usage not verified in code")

    checkpoint.dataset_usage_verification = {
        "status": "WARNING",
        "dataset_name": dataset_info.name,
        "evidence_found": False,
        "message": "Dataset name/path not found in code",
        "checked_at": now()
    }
    SAVE checkpoint

    # Warning only, continue (not a complete block)
    print(" Proceeding with experiment, but verify results carefully.")

ELSE:
    print(f"✅ Dataset '{dataset_info.name}' usage confirmed in code")
    print(f" Found {len(dataset_usage_evidence)} references")

    checkpoint.dataset_usage_verification = {
        "status": "PASSED",
        "dataset_name": dataset_info.name,
        "evidence_found": True,
        "reference_count": len(dataset_usage_evidence),
        "checked_at": now()
    }
    SAVE checkpoint
    log_event("DATA", f"Dataset usage verified: {len(dataset_usage_evidence)} refs")
```

---

## STEP COMPLETION

**Auto-proceed to `{nextStepFile}` when ALL conditions met:**
1. ✅ Terminal log initialized
2. ✅ Dataset existence verified (or standard dataset acknowledged)
3. ✅ Mock data check passed (no violations in main code)
4. ✅ Dataset usage verification completed

### UNATTENDED Conditional Auto-Proceed

Display: "**Routing based on pre-validation results...**"

#### Menu Handling Logic:

Based on validation results, immediately load, read entire file, then execute ONE of the following:

| Condition | Action |
|-----------|--------|
| Mock data detected | Read and execute `{coderStepFile}` (step-02) |
| All validations passed | Read and execute `{nextStepFile}` (step-05b) |

#### EXECUTION RULES:

- This is an UNATTENDED pre-validation step with no user choices
- Route to Step 2 (Coder) if mock data detected, else Step 5B
- **Failure to load next step = SYSTEM FAILURE**

---

**On completion:** Load, read entire file, then execute `{nextStepFile}` (step-05b-execution.md)
