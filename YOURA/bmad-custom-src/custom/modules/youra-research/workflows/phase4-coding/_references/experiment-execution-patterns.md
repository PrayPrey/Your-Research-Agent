# Experiment Execution Patterns

> Reference file for Step 5 (5a, 5b, 5c): Experiment Execution
> Extracted to reduce step file size and enable reusability

---

## Dynamic Entry Point Discovery (USE SERENA MCP!)

### 1. Analyze Code Structure

```python
# List code directory
mcp__serena__list_dir(
    relative_path=code_folder,
    recursive=True
)
```

### 2. Find Entry Point Candidates

```python
# Search for main entry patterns
mcp__serena__search_for_pattern(
    substring_pattern="if __name__.*==.*['\"]__main__['\"]",
    relative_path=code_folder,
    context_lines_after=5
)

# Priority order:
# 1. main.py with if __name__ == "__main__"
# 2. run.py / run_experiment.py
# 3. train.py with main block
# 4. experiment.py
# 5. Any file with argparse and main block
```

### 3. Analyze Entry Point

```python
mcp__serena__get_symbols_overview(
    relative_path=detected_entry_point
)

# Look for: main(), run_experiment(), CLI argument parsing
```

### 4. Detect Execution Command

```python
mcp__serena__find_symbol(
    name_path_pattern="parse_args",
    relative_path=detected_entry_point,
    include_body=True
)

# OR search for argparse usage
mcp__serena__search_for_pattern(
    substring_pattern="argparse\\.ArgumentParser|add_argument",
    relative_path=detected_entry_point,
    context_lines_before=2,
    context_lines_after=5
)
```

### 5. Construct Execution Plan

```python
execution_plan = {
    "entry_point": detected_file, # e.g., "main.py"
    "command": f"python {entry_point} {args}",
    "has_quick_mode": bool, # --quick or --dry-run available?
    "has_separate_eval": bool, # separate eval.py exists?
    "detected_args": ["--epochs", "--quick"],
    "is_full_run": False, # Will be set True after smoke test passes
    "smoke_test_command": None # Populated if quick mode available
}
```

---

## Conda Environment Execution Pattern

**CRITICAL: Get conda_env_name AND conda_path from checkpoint.yaml**

```python
conda_env_name = checkpoint.conda.env_name # e.g., "youra-h-e1"
conda_path = checkpoint.conda.conda_path # e.g., "/home/anonymous/miniforge3"

# FALLBACK: If conda_path not in checkpoint (backward compatibility)
IF conda_path is null OR conda_path is empty:
    # Auto-detect conda path
    result = Bash: which conda
    IF success:
        CONDA_EXE = result.strip()
        conda_path = dirname(dirname(CONDA_EXE))
    ELSE:
        FOR path IN ["/home/anonymous/miniforge3", "/home/anonymous/miniconda3", "/opt/conda"]:
            IF exists "{path}/bin/conda":
                conda_path = path
                break

        IF conda_path is null:
            log_event("ERROR", "Conda not found")
            STOP("Conda not found. Please ensure conda is installed.")

    checkpoint.conda.conda_path = conda_path
    SAVE checkpoint
```

**ALL commands MUST initialize conda first, then use `conda run -n {conda_env_name}`!**

### Install Requirements
```bash
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pip install -r {code_folder}/requirements.txt
```

### Verify Imports
```bash
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} python -c "from {main_module} import *"
```

### Check GPU Availability
```bash
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

---

## Experiment Launch with nohup

**Session-independent execution (supports 10+ hour experiments)**

### Log Header Template

```python
log_header = f"""
================================================================================
🧪 YouRA EXPERIMENT LOG
================================================================================
Hypothesis ID: {hypothesis_id}
Timestamp: {ISO8601_now}
Environment: {conda_env_name}
Entry Point: {entry_point}
Command: python {entry_point} {args}
GPU: {gpu_info} (count: {gpu_count})
================================================================================
EXPERIMENT OUTPUT:
================================================================================

"""

Write(file_path=f"{code_folder}/experiment.log", content=log_header)
```

### Launch Command

```bash
source {conda_path}/etc/profile.d/conda.sh
cd {code_folder}

# Run experiment with output to experiment.log
nohup conda run -n {conda_env_name} python {entry_point} {args} >> experiment.log 2>&1 &

echo $! > experiment.pid
```

---

## Phased Error Check (4 minutes total)

**CRITICAL: Wait up to 4 minutes with phased checks for proper error detection**

```python
# PHASED ERROR CHECK: 30s, 90s, 180s, 240s (4 minutes total)
check_phases = [30, 90, 180, 240]
previous_wait = 0
experiment_failed = False
experiment_quick = False

FOR phase in check_phases:
    wait_time = phase - previous_wait
    print(f"⏳ Waiting {wait_time}s (total: {phase}s)...")
    sleep(wait_time)
    previous_wait = phase

    # Check process status
    ps_check = Bash(f"ps -p {pid} --no-headers 2>/dev/null")

    IF process_not_running:
        # Terminated - check for errors
        final_log = Read("{code_folder}/experiment.log")

        IF "Error" in final_log OR "Exception" in final_log OR "Traceback" in final_log:
            experiment_status = "failed"
            experiment_failed = True
            log_event("ERROR", f"Experiment failed at {phase}s")
            BREAK
        ELSE:
            IF phase < 240:
                print(f"⚠️ Process ended at {phase}s - checking if smoke test...")
                CONTINUE
            ELSE:
                experiment_status = "quick_completion"
                experiment_quick = True
                log_event("CHECK", f"Process completed at {phase}s (no errors)")
                BREAK
    ELSE:
        print(f"✅ Process running at {phase}s check")

        IF phase == 240:
            checkpoint.experiment_status = "running_detached"
            SAVE checkpoint
            log_event("CHECK", "Experiment stable after 4-minute check")
            print("✅ Experiment running stably after 4 minutes.")
```

---

## Smoke Test Verification (CRITICAL - PREVENTS FALSE COMPLETION)

**This section MUST be executed when experiment completes within 4 minutes**

### Step 1: Check if quick/smoke mode was used

```python
command_used = execution_plan.command
is_smoke_test = False
smoke_indicators = []

# Check command line args
IF any(arg in command_used for arg in ["--quick", "--smoke", "--dry-run", "--test", "--debug", "--fast"]):
    is_smoke_test = True
    smoke_indicators.append(f"Quick mode argument detected in command: {command_used}")
```

### Step 2: Check log for smoke test indicators

```python
smoke_log_patterns = [
    "smoke test",
    "quick mode",
    "dry run",
    "debug mode",
    "epoch 1/1", # Only 1 epoch = likely smoke test
    "max_steps=1",
    "max_epochs=1",
    "running in test mode",
    "validation only",
    "skipping training"
]

FOR pattern in smoke_log_patterns:
    IF pattern.lower() in final_log.lower():
        is_smoke_test = True
        smoke_indicators.append(f"Log contains: '{pattern}'")
```

### Step 3: Check duration

```python
duration_seconds = (now() - checkpoint.experiment_started_at).total_seconds()
IF duration_seconds < 60:
    smoke_indicators.append(f"Very short duration: {duration_seconds:.1f}s")
```

### Step 4: Check output metrics

```python
IF "epoch" in final_log.lower():
    epoch_matches = regex_findall(r"epoch[:\s]+(\d+)", final_log.lower())
    IF epoch_matches AND max(int(e) for e in epoch_matches) <= 1:
        is_smoke_test = True
        smoke_indicators.append("Only 1 epoch completed")
```

### Step 5: Decision

```python
IF is_smoke_test:
    print("⚠️ SMOKE TEST DETECTED - NOT ACTUAL EXPERIMENT")
    checkpoint.smoke_test_completed = True
    checkpoint.smoke_test_results = {
        "status": "passed",
        "indicators": smoke_indicators,
        "duration_seconds": duration_seconds,
        "timestamp": now()
    }
    checkpoint.experiment_status = "smoke_test_passed"
    SAVE checkpoint

    # Relaunch WITHOUT quick mode
    full_command = remove_quick_args(execution_plan.command)
    execution_plan.command = full_command
    execution_plan.is_full_run = True
    # Re-execute experiment launch
```

### Helper: Remove Quick Arguments

```python
def remove_quick_args(command):
    quick_args = ["--quick", "--smoke", "--dry-run", "--test", "--debug", "--fast",
                  "--epochs=1", "--max_steps=1", "--max_epochs=1"]
    tokens = command.split()
    filtered = [t for t in tokens if not any(q in t for q in quick_args)]
    return " ".join(filtered)
```

---

## GPU Utilization Check

**If GPU available but not being used, STOP and fix!**

```python
IF checkpoint.gpu.available AND checkpoint.experiment_status == "running_detached":
    sleep(30) # Wait for training to start

    ps_check = Bash(f"ps -p {pid} --no-headers 2>/dev/null")

    IF process_still_running:
        gpu_util_result = Bash("nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null")

        IF gpu_util_result.success:
            gpu_utilization = int(gpu_util_result.stdout.strip().split('\n')[0])

            IF gpu_utilization < 5: # Less than 5% GPU usage
                log_event("ERROR", f"GPU underutilized: {gpu_utilization}% (expected >5%)")
                print("🚨 GPU UNDERUTILIZATION DETECTED!")

                # Kill the experiment
                Bash(f"kill -9 {pid}")

                # Return to Step 2 for GPU fix
                checkpoint.gpu_utilization = {"detected": gpu_utilization, "status": "underutilized"}
                checkpoint.experiment_status = "gpu_underutilized"
                checkpoint.current_step = 2
                SAVE checkpoint
```

---

## Post-Experiment Mock Data Verification

### Mock Data Log Patterns

```python
mock_log_patterns = [
    "using mock data",
    "using synthetic data",
    "using fake data",
    "using dummy data",
    "using random data",
    "generated random",
    "synthetic dataset",
    "mock dataset",
    "random tensor",
    "torch.randn",
    "np.random",
    "creating synthetic",
    "generating fake"
]
```

### Real Data Log Patterns

```python
real_data_patterns = [
    f"loading {dataset_info.name}",
    f"loaded {dataset_info.name}",
    f"dataset: {dataset_info.name}",
    "loading dataset",
    "data loaded",
    "train samples:",
    "test samples:",
    "training data:",
    "validation data:",
    "downloaded",
    "extracting"
]
```

### Verdict Determination

```python
mock_result_verdict = "UNKNOWN"

IF mock_evidence_in_log AND NOT real_data_evidence:
    mock_result_verdict = "MOCK_SUSPECTED"
ELIF mock_evidence_in_log AND real_data_evidence:
    mock_result_verdict = "MIXED_WARNING"
ELIF NOT mock_evidence_in_log AND real_data_evidence:
    mock_result_verdict = "REAL_DATA_CONFIRMED"
ELSE:
    mock_result_verdict = "INSUFFICIENT_EVIDENCE"
```
