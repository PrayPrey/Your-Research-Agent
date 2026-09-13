---
name: 'mock_detection'
description: 'LLM-based reality verification for detecting mock data and model usage in experiments'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - detect_mock_usage
  - detect_mock_data
  - detect_mock_model
  - verify_real_experiment
  - format_mock_report
  - get_mock_severity

# Called By
called_by:
  - 'phase4-coding/steps/step-05c-post-validation.md'
  - 'phase5-baseline-repo-comparison/steps/step-08-validation.md'
---

# LLM-Based Reality Verification Helper

> LLM directly reads checkpoint, logs, experiment results, and experiment brief to make semantic judgments.
> Compares **expected values** (from 02c) with **actual results** for accurate mock detection.
> No pattern matching or hard-coded thresholds - relies entirely on LLM reasoning.

---

## Usage

```yaml
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'
mock_detection: '{helpers_path}/mock_detection.md'
```

---

## Main Functions

### 1. detect_mock_usage (Data/Model Verification)

```python
def detect_mock_usage(
    code_folder: str,
    detection_type: str = "data",
    checkpoint_file: str = None,
    experiment_log_file: str = None,
    tasks_file: str = None,
    # NEW: Additional context for "expected vs actual" comparison
    experiment_results_file: str = None, # experiment_results.json (actual metrics)
    experiment_brief_file: str = None # 02c_experiment_brief.md (expected values)
) -> dict:
    """
    LLM reads multiple sources to determine mock/synthetic usage.

    Key comparison: Expected values (02c) vs Actual results (experiment_results.json)

    Args:
        code_folder: Path to code folder
        detection_type: "data" or "model"
        checkpoint_file: Path to 04_checkpoint.yaml (auto-derived if None)
        experiment_log_file: Path to experiment.log (auto-derived if None)
        tasks_file: Path to 03_tasks.yaml (optional)
        experiment_results_file: Path to experiment_results.json (actual metrics)
        experiment_brief_file: Path to 02c_experiment_brief.md (expected values)

    Returns:
        - detected: bool - Mock usage detected
        - violations: list - Detected issues
        - severity: str - CRITICAL/HIGH/MEDIUM/LOW/NONE
        - summary: str - Human-readable summary
        - llm_reasoning: str - LLM's reasoning
        - confidence: float - Confidence score (0.0-1.0)
    """
    # Derive file paths
    if not checkpoint_file:
        hypothesis_folder = os.path.dirname(code_folder)
        checkpoint_file = f"{hypothesis_folder}/04_checkpoint.yaml"
    if not experiment_log_file:
        experiment_log_file = f"{code_folder}/experiment.log"
    if not experiment_results_file:
        hypothesis_folder = os.path.dirname(code_folder)
        experiment_results_file = f"{hypothesis_folder}/experiment_results.json"
    if not experiment_brief_file:
        hypothesis_folder = os.path.dirname(code_folder)
        experiment_brief_file = f"{hypothesis_folder}/02c_experiment_brief.md"

    # Read all available files
    checkpoint = Read(checkpoint_file) if file_exists(checkpoint_file) else None
    log_content = Read(experiment_log_file, last_500_lines=True) if file_exists(experiment_log_file) else None
    tasks = Read(tasks_file) if tasks_file and file_exists(tasks_file) else None
    experiment_results = Read(experiment_results_file) if file_exists(experiment_results_file) else None
    experiment_brief = Read(experiment_brief_file) if file_exists(experiment_brief_file) else None

    if not checkpoint:
        return {"detected": False, "violations": [], "severity": "NONE",
                "summary": "Checkpoint not found", "confidence": 0.0}

    # Build and execute LLM prompt with all context
    prompt = build_verification_prompt(
        checkpoint=checkpoint,
        log=log_content,
        tasks=tasks,
        detection_type=detection_type,
        experiment_results=experiment_results,
        experiment_brief=experiment_brief
    )
    llm_response = llm_analyze(prompt)

    # Parse result
    return parse_llm_response(llm_response, detection_type)
```

### 2. detect_mock_model_runtime (Model Verification Wrapper)

```python
def detect_mock_model_runtime(
    model_info: dict, # Optional parameter, ignored
    code_folder: str,
    checkpoint_file: str = None,
    experiment_log_file: str = None,
    experiment_results_file: str = None,
    experiment_brief_file: str = None
) -> dict:
    """
    Model verification wrapper. Calls detect_mock_usage with model type.

    Returns:
        - is_mock: bool
        - indicators: list
        - confidence: str - HIGH/MEDIUM/LOW
        - recommendation: str
        - llm_reasoning: str
    """
    result = detect_mock_usage(
        code_folder=code_folder,
        detection_type="model",
        checkpoint_file=checkpoint_file,
        experiment_log_file=experiment_log_file,
        experiment_results_file=experiment_results_file,
        experiment_brief_file=experiment_brief_file
    )

    # Convert confidence score to label
    confidence_str = "HIGH" if result["confidence"] >= 0.8 else "MEDIUM" if result["confidence"] >= 0.5 else "LOW"

    return {
        "is_mock": result["detected"],
        "indicators": result["violations"],
        "confidence": confidence_str,
        "recommendation": "Replace mock model" if result["detected"] else "Model appears valid",
        "llm_reasoning": result.get("llm_reasoning", "")
    }
```

### 3. verify_task_completion (Task Completion Verification)

```python
def verify_task_completion(
    tasks_file: str,
    checkpoint_file: str,
    code_folder: str = None
) -> dict:
    """
    LLM reads 03_tasks.yaml and 04_checkpoint.yaml to verify task completion.

    Args:
        tasks_file: Path to 03_tasks.yaml
        checkpoint_file: Path to 04_checkpoint.yaml
        code_folder: Path to code folder (for output_file existence check)

    Returns:
        - all_completed: bool - All tasks completed
        - incomplete_tasks: list - List of incomplete tasks
        - issues: list - Detected issues
        - llm_reasoning: str - LLM's reasoning
        - confidence: float
    """
    tasks = Read(tasks_file) if file_exists(tasks_file) else None
    checkpoint = Read(checkpoint_file) if file_exists(checkpoint_file) else None

    if not tasks or not checkpoint:
        return {"all_completed": False, "incomplete_tasks": [],
                "issues": ["Required files not found"], "confidence": 0.0}

    # LLM prompt
    prompt = f"""## Task Completion Verification

**03_tasks.yaml (Defined Tasks):**
```yaml
{tasks}
```

**04_checkpoint.yaml (Execution State):**
```yaml
{checkpoint}
```

### Questions:
1. Do all defined tasks exist in the checkpoint?
2. Is each task's status "review" or "done"?
3. Are all sdd_phases (TEST, IMPL, VERIFY) passed?
4. Is output_file specified for each task?

### Judgment Format:
**All Completed:** YES or NO
**Confidence:** (0.0 - 1.0)
**Incomplete Tasks:** (list or "None")
**Issues:** (list of issues or "None")
**Reasoning:** (explanation)
"""

    llm_response = llm_analyze(prompt)
    return parse_task_completion_response(llm_response)
```

---

## Prompt Builder (Enhanced with Expected vs Actual)

```python
def build_verification_prompt(
    checkpoint: str,
    log: str,
    tasks: str,
    detection_type: str,
    experiment_results: str = None,
    experiment_brief: str = None
) -> str:
    """Build LLM prompt with expected vs actual comparison context."""

    base_prompt = """## Experiment Reality Verification

You are verifying whether an experiment used REAL data/model or MOCK/SYNTHETIC substitutes.

**CRITICAL:** Compare EXPECTED values (from 02c_experiment_brief.md) with ACTUAL results (from experiment_results.json).
Suspicious patterns include:
- Results too perfect (e.g., accuracy 99.9% when target was 90%)
- Training suspiciously fast (e.g., "10 epochs in 1 second" for full dataset)
- Metrics exactly matching targets (unrealistically precise)
- No variance in metrics across runs
- Dataset size mismatch (expected: 50000, actual: 100)

"""

    # Add experiment brief (EXPECTED values)
    if experiment_brief:
        base_prompt += f"""
### 02c_experiment_brief.md (EXPECTED Values)
```markdown
{experiment_brief[:3000]} # Truncate if too long
```
**Key sections to check:**
- Dataset: Expected name, size, source
- Success Criteria: Expected metric thresholds
- Training Protocol: Expected epochs, batch size, duration
- Gate Conditions: PASS/FAIL thresholds

"""

    # Add experiment results (ACTUAL values)
    if experiment_results:
        base_prompt += f"""
### experiment_results.json (ACTUAL Results)
```json
{experiment_results[:2000]} # Truncate if too long
```
**Compare against expected values above.**

"""

    # Add checkpoint
    base_prompt += f"""
### 04_checkpoint.yaml (Execution State)
```yaml
{checkpoint[:2000]} # Truncate if too long
```

"""

    # Add log if available
    if log:
        base_prompt += f"""
### experiment.log (Training Log - last 500 lines)
```
{log[:3000]} # Truncate if too long
```
**Check for:**
- Real data loading messages (file paths, download progress)
- Realistic training progress (loss decreasing gradually, not instantly)
- Actual batch processing (iteration times, GPU utilization)

"""

    # Add tasks if available
    if tasks:
        base_prompt += f"""
### 03_tasks.yaml (Task Definitions)
```yaml
{tasks[:1000]}
```

"""

    # Add detection-specific questions
    if detection_type == "data":
        questions = """
### Verification Questions (DATA):
1. Does the experiment use the REAL dataset specified in 02c, or mock/synthetic data?
2. Are the training metrics PLAUSIBLE for the expected dataset size?
3. Does the training duration match expectations (not suspiciously fast)?
4. Is there evidence of actual data loading (file paths, download, preprocessing)?
5. Do the metrics show realistic variance (not perfectly matching targets)?
"""
    else: # model
        questions = """
### Verification Questions (MODEL):
1. Does the experiment use a REAL model or mock/passthrough model?
2. Do the training dynamics show actual learning (loss decreasing, gradients flowing)?
3. Are the parameter count and layer structure reasonable for the expected architecture?
4. Is there evidence of GPU computation (realistic batch times, memory usage)?
5. Do forward pass outputs vary appropriately with different inputs?
"""

    return base_prompt + questions + """
### Judgment Format (REQUIRED):
**Verdict:** REAL_EXPERIMENT or MOCK_DETECTED
**Confidence:** (0.0 - 1.0)
**Expected vs Actual Comparison:**
- Dataset: [Expected] vs [Actual]
- Metrics: [Expected threshold] vs [Actual value]
- Duration: [Expected] vs [Actual]
**Issues Found:** (list of specific issues or "None")
**Severity:** CRITICAL/HIGH/MEDIUM/LOW/NONE
**Reasoning:** (detailed explanation of why you reached this verdict)
"""
```

---

## Response Parsers

```python
def parse_llm_response(response: str, detection_type: str) -> dict:
    """Parse LLM response into structured result."""
    import re

    # Extract verdict
    is_mock = "mock_detected" in response.lower()

    # Extract confidence
    conf_match = re.search(r"confidence[:\s]*(\d+\.?\d*)", response.lower())
    confidence = float(conf_match.group(1)) if conf_match else 0.5
    if confidence > 1: confidence /= 100

    # Extract severity
    severity = "NONE"
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if sev.lower() in response.lower():
            severity = sev
            break

    # Extract reasoning
    reasoning_match = re.search(r"reasoning[:\s]*(.+?)(?=\n\*\*|$)", response, re.I | re.DOTALL)
    reasoning = reasoning_match.group(1).strip()[:500] if reasoning_match else ""

    # Extract issues
    violations = []
    issues_match = re.search(r"issues found[:\s]*(.+?)(?=\n\*\*|$)", response, re.I | re.DOTALL)
    if issues_match and is_mock:
        for line in issues_match.group(1).split('\n'):
            if line.strip().startswith('-'):
                violations.append({"description": line.strip()[1:].strip(), "severity": severity})

    return {
        "detected": is_mock,
        "violations": violations,
        "violation_count": len(violations),
        "severity": severity if is_mock else "NONE",
        "summary": f"{'Mock detected' if is_mock else 'Real experiment'} ({confidence:.0%} confidence)",
        "llm_reasoning": reasoning,
        "confidence": confidence,
        "detection_type": detection_type,
        "method": "llm_verification"
    }

def parse_task_completion_response(response: str) -> dict:
    """Parse task completion response."""
    import re

    all_completed = "all completed: yes" in response.lower()

    conf_match = re.search(r"confidence[:\s]*(\d+\.?\d*)", response.lower())
    confidence = float(conf_match.group(1)) if conf_match else 0.5
    if confidence > 1: confidence /= 100

    reasoning_match = re.search(r"reasoning[:\s]*(.+?)(?=\n\*\*|$)", response, re.I | re.DOTALL)
    reasoning = reasoning_match.group(1).strip()[:500] if reasoning_match else ""

    incomplete = []
    incomplete_match = re.search(r"incomplete tasks[:\s]*(.+?)(?=\n\*\*|$)", response, re.I | re.DOTALL)
    if incomplete_match and "none" not in incomplete_match.group(1).lower():
        for line in incomplete_match.group(1).split('\n'):
            if line.strip().startswith('-'):
                incomplete.append(line.strip()[1:].strip())

    issues = []
    issues_match = re.search(r"issues[:\s]*(.+?)(?=\n\*\*|$)", response, re.I | re.DOTALL)
    if issues_match and "none" not in issues_match.group(1).lower():
        for line in issues_match.group(1).split('\n'):
            if line.strip().startswith('-'):
                issues.append(line.strip()[1:].strip())

    return {
        "all_completed": all_completed,
        "incomplete_tasks": incomplete,
        "issues": issues,
        "llm_reasoning": reasoning,
        "confidence": confidence
    }
```

---

## create_mock_fix_task (Archon Task Creation)

```python
def create_mock_fix_task(project_id: str, hypothesis_feature: str, detection_result: dict,
                         fix_type: str = "data", dataset_info: dict = None) -> str:
    """Create Archon fix task when mock is detected."""

    title = f"[MOCK {fix_type.upper()} FIX] Replace with real {fix_type}"
    description = f"""🚨 Mock {fix_type} detected by LLM verification!

**LLM Analysis:**
{detection_result.get('llm_reasoning', 'N/A')}

**Severity:** {detection_result.get('severity', 'N/A')}
**Confidence:** {detection_result.get('confidence', 'N/A')}

**FIX REQUIRED:**
1. Remove mock/{fix_type} usage
2. Use real {fix_type} as specified in 02c_experiment_brief.md
"""

    result = mcp__archon__manage_task(
        action="create", project_id=project_id, title=title,
        description=description, feature=hypothesis_feature, status="todo"
    )

    return result.get("task", {}).get("id") if result.get("success") else None
```

---

## LLM Verification Flow

```
Step 5A (Pre-Experiment):
  → Read 04_checkpoint.yaml
  → Read 02c_experiment_brief.md (expected values)
  → LLM judges data setup against expectations
  → If suspicious → Step 2

Step 5C (Post-Experiment):
  → Read 04_checkpoint.yaml + experiment.log
  → Read experiment_results.json (actual results)
  → Read 02c_experiment_brief.md (expected values)
  → LLM compares expected vs actual
  → If mock detected → Step 2 (max 3 retries)

Task Completion (Optional):
  → Read 03_tasks.yaml + 04_checkpoint.yaml
  → LLM judges if all tasks completed
```

---

## Mock Detection Patterns (LLM Guidance)

The LLM should flag as MOCK_DETECTED when:

1. **Suspiciously Perfect Results:**
   - Expected accuracy: 85%, Actual: 99.99%
   - All metrics exactly at threshold (too precise)

2. **Unrealistic Training Duration:**
   - Expected: "300k timesteps, 7-10 days"
   - Actual: "Completed in 10 seconds"

3. **Dataset Size Mismatch:**
   - Expected: "CIFAR-10, 50000 samples"
   - Actual: "100 random samples"

4. **No Evidence of Real Processing:**
   - No data loading logs (file paths, download progress)
   - No GPU utilization logs
   - No gradual loss decrease

5. **Instant Convergence:**
   - Loss drops to near-zero in first epoch
   - No training dynamics visible in logs
