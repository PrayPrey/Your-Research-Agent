---
name: 'step-07-adaptation-coding'
description: 'Generate algorithm injection code for baseline (Mode B - Inject OUR algorithm into BASELINE)'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'

# Reference Guides (READ only the relevant one for each task!)
fair_comparison_guide: '{workflow_path}/_references/fair-comparison-principle.md'
algorithm_injection_guide: '{workflow_path}/_references/algorithm-injection.md'
adapter_metrics_guide: '{workflow_path}/_references/adapter-metrics.md'
adapter_results_guide: '{workflow_path}/_references/adapter-results.md'
adapter_training_guide: '{workflow_path}/_references/adapter-training-script.md'
adapter_tests_guide: '{workflow_path}/_references/adapter-tests.md'
adapter_changes_guide: '{workflow_path}/_references/adapter-changes-template.md'

# File References
thisStepFile: '{workflow_path}/steps/step-07-adaptation-coding.md'
prevStepFile: '{workflow_path}/steps/step-06-setup.md'
nextStepFile: '{workflow_path}/steps/step-08-validation.md'
workflowFile: '{workflow_path}/workflow.md'

# Input Files
checkpoint_file: '{baseline_folder}/05_baseline_checkpoint.yaml'
code_analysis_file: '{baseline_folder}/code_analysis.md'
tasks_file: '{baseline_folder}/05_tasks.yaml'

# Output Files (per baseline)
adaptations_folder: '{baseline_folder}/adaptations/{baseline.repo_name}'

# Config: Read from checkpoint.workflow_config (Source: workflow.yaml)
tasks_per_baseline: 4 # Mode B structural constant (not in workflow.yaml)

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 7: Algorithm Injection Coding (Mode B)

> **Mode:** UNATTENDED (Fully Automatic)
> **Reference Guides:** READ only the relevant guide for each task

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🛑 NEVER generate code without searching Archon KB first
- 📖 READ only the **relevant adapter guide** for each task (see 7.4g table)
- 📖 READ `{fair_comparison_guide}` to understand WHY we inject this way
- 🎯 Generate injection code for **all 3 baselines** (loop)
- 🚫 FORBIDDEN to validate code (that's Step 8)
- 🚫 FORBIDDEN to modify baseline's model, dataset, or config loading

---

## ⚠️ FAIR COMPARISON PRINCIPLE (MODE B)

> **READ `{fair_comparison_guide}` for complete explanation!**

**Summary:** We inject OUR **ALGORITHM** into BASELINE's **environment**.

```
PRESERVE (baseline's - DO NOT MODIFY):
  ✗ Model architecture → Keep baseline's exactly as-is
  ✗ Dataset loading → Keep baseline's exactly as-is
  ✗ Hyperparameters → Keep baseline's exactly as-is
  ✗ Training loop structure → Minimal changes only

INJECT (ours):
  ✓ Algorithm/Optimizer → Replace/wrap baseline's optimizer with ours
  ✓ Metric tracking → Add psi computation
  ✓ Results saver → Add comparison format output
```

**The ONLY difference between methods is the ALGORITHM being compared.**

---

## 7.1 Check Cycle Limits

```python
# Load cycle limit from checkpoint (Single Source of Truth: workflow.yaml)
max_cycles = checkpoint["workflow_config"]["adaptation"]["max_coder_validator_cycles"]
```

| Condition | Action |
|-----------|--------|
| `coder_validator_cycles` ≥ max_cycles | Log error, proceed to Step 9 with partial adaptation |
| `coder_validator_cycles` < max_cycles | Continue to Section 7.2 |

---

## 7.2 Load Tasks from 05_tasks.yaml

<critical>

Tasks are loaded from local `05_tasks.yaml` file (created by Step 6).
**FORBIDDEN:** `mcp__archon__manage_task(action="create")` - Archon task creation is.

**MODE B TASKS (4 per baseline):**
1. algorithm-injection
2. metric-injection
3. results-saver
4. training-script

**NO config-override, data-adapter, or model-adapter tasks!**
</critical>

### 7.2.1 Read Task File

```python
# Load tasks from YAML file
tasks_data = read_yaml("{baseline_folder}/05_tasks.yaml")

# Verify file exists and has Mode B structure
if not tasks_data:
    ERROR: "05_tasks.yaml not found. Return to Step 6 to generate tasks."

if tasks_data.metadata.mode != "B":
    ERROR: "Task file is not Mode B. Regenerate with Step 6."
```

### 7.2.2 Extract Pending Tasks

**FOR EACH baseline in tasks_data.baselines:**

```python
pending_tasks = [
    task for task in baseline.tasks
    if task.status == "pending"
]
# Sort by priority (descending)
pending_tasks.sort(key=lambda t: t.priority, reverse=True)
```

---

## 7.3 Check Task Completion Status

| Condition | Action |
|-----------|--------|
| No pending tasks for ANY baseline | All done → Go to Step 8 |
| Pending tasks found | Continue to Section 7.4 |

```python
all_done = all(
    all(task.status in ["done", "skipped"] for task in baseline.tasks)
    for baseline in tasks_data.baselines
)

if all_done:
    # Proceed to Step 8 (Validation)
    GOTO step-08-validation.md
```

---

## 7.4 Task Processing Loop

**FOR EACH task in todo_tasks:**

### 7.4a Check Retry Limit
Skip if `task_retry_counts[task.id]` ≥ 3

### 7.4b Check for Validator Error
If task description contains `=== VALIDATION FAILED ===`, extract error_info

### 7.4c Transition to Doing (YAML Update)

```python
# Update task status in 05_tasks.yaml
task.status = "doing"
write_yaml("{baseline_folder}/05_tasks.yaml", tasks_data)

# Also update budget_summary.by_status
tasks_data.budget_summary.by_status.pending -= 1
tasks_data.budget_summary.by_status.doing += 1
```

### 7.4d Load Task Context

**Read these files:**
- `code_analysis.md` - Baseline code structure with **injection points**
- `checkpoint.yaml` - Repo info, conda env, **injection_analysis**

**Baseline's Code (what we're injecting INTO):**
- `{baseline_clone_path}/train.py` - Baseline's training script
- `{baseline_clone_path}/...` - Baseline's optimizer creation location

**OUR Algorithm (what we're injecting):**
- `{hypothesis_folder}/code/...` - OUR algorithm implementation

### 7.4e Search Archon KB (MANDATORY!)

```
mcp__archon__rag_search_knowledge_base(query="{task_type} pytorch optimizer")
mcp__archon__rag_search_code_examples(query="custom optimizer implementation")
```

If Archon insufficient → Exa fallback

### 7.4f Analyze Baseline with Serena

| Purpose | Tool |
|---------|------|
| Training script overview | `mcp__serena__get_symbols_overview` |
| Find optimizer creation | `mcp__serena__search_for_pattern` pattern: "optim\\.SGD\\|optim\\.Adam" |
| Find backward pass | `mcp__serena__search_for_pattern` pattern: "loss.backward" |

### 7.4g Generate Injection Code (MODE B)

> **CRITICAL: READ only the relevant guide file for the current task!**
> **CRITICAL: DO NOT modify baseline's model, dataset, or config!**

Generate code based on task type:

| Task | Reference Guide to READ | What It Does |
|------|------------------------|--------------|
| Algorithm Injection | `{algorithm_injection_guide}` | Replace/wrap baseline's optimizer with OURS |
| Metric Injection | `{adapter_metrics_guide}` | Add psi computation at end of epoch |
| Results Saver | `{adapter_results_guide}` | Save results in comparison format |
| Training Script | `{adapter_training_guide}` | Minimal modification to baseline's train.py |

**MODE B Task Details:**

#### 1. Algorithm Injection Task

```python
# What to create: {adaptations_folder}/algorithm_injection.py
# Reference: {algorithm_injection_guide}

# Pattern 1: Optimizer Replacement
class OurOptimizer(Optimizer):
    def step(self, closure=None):
        # OUR algorithm logic here
        pass

def get_our_optimizer(model_params, **baseline_config):
    return OurOptimizer(model_params, **baseline_config)
```

**Key principle:** Our optimizer must accept the SAME parameters as baseline's optimizer (lr, momentum, etc.)

#### 2. Metric Injection Task

```python
# What to create: {adaptations_folder}/metrics.py
# Reference: {adapter_metrics_guide}

def compute_psi(model, dataloader, device):
    """Compute psi metric using baseline's model and data."""
    pass

class MetricTracker:
    """Track metrics throughout training."""
    pass
```

**Key principle:** Metric computation uses baseline's model and data, just measures our algorithm's behavior.

#### 3. Results Saver Task

```python
# What to create: {adaptations_folder}/results_saver.py
# Reference: {adapter_results_guide}

class ResultsSaver:
    """Save results in standardized comparison format."""
    def __init__(self, output_path, method_name):
        pass
```

#### 4. Training Script Task

```python
# What to modify: {baseline_clone_path}/train.py
# Reference: {adapter_training_guide}

# MINIMAL modifications:
# 1. Add sys.path setup for adaptations folder
# 2. Add imports for algorithm_injection, metrics, results_saver
# 3. Add --method argument (baseline vs ours)
# 4. Conditional optimizer replacement
# 5. Add metric tracking at end of epoch
# 6. Add results saving at end of training

# DO NOT MODIFY:
# - Data loading code
# - Model creation code
# - Hyperparameters
# - Training loop structure (except minimal injections)
```

### 7.4h Write Code AND Test File

**Part 1:** Write code file using Write tool or Serena

**Part 2:** Write test file (MANDATORY!)
- Path: `{adaptations_folder}/tests/test_{component}.py`
- Minimum 3 test methods
- Real assertions (NO placeholder tests)

### 7.4i Transition to Review (YAML Update)

1. Verify test file exists via `mcp__serena__find_file`
2. If no test → go back to 7.4h Part 2
3. Transition to review in YAML:

```python
# Update task status in 05_tasks.yaml
task.status = "review"
write_yaml("{baseline_folder}/05_tasks.yaml", tasks_data)

# Update budget_summary.by_status
tasks_data.budget_summary.by_status.doing -= 1
tasks_data.budget_summary.by_status.review += 1
```

---

## 7.5 Update Checkpoint

```yaml
current_step: 8
adaptation:
  mode: "B"
  mode_description: "Inject OUR algorithm into BASELINE's environment"
  status: "coding_complete"
  baselines:
    - repo_name: "{baseline_1}"
      tasks_completed: {count}/4
      status: "complete|partial"
      files_created:
        - "algorithm_injection.py"
        - "metrics.py"
        - "results_saver.py"
        - "train.py (modified)"
    - repo_name: "{baseline_2}"
      tasks_completed: {count}/4
      status: "complete|partial"
    - repo_name: "{baseline_3}"
      tasks_completed: {count}/4
      status: "complete|partial"
coder_validator_cycles: {count}
```

---

## 7.6 Generate CHANGES.md

> **READ `{adapter_changes_guide}` for CHANGES.md template!**

Document all changes in `{baseline_folder}/changes/CHANGES.md`

**Mode B CHANGES.md should include:**
- What files were created (algorithm_injection.py, metrics.py, results_saver.py)
- What was modified in train.py (minimal diff)
- What was NOT modified (model, dataset, config)
- How to run comparison (--method baseline vs --method ours)

---

## 7.7 Proceed to Next Step

1. Set `checkpoint.current_step = 8`
2. Save checkpoint
3. **Load and execute `step-08-validation.md`**

---

## Step Completion Criteria

- [ ] **4 adaptation tasks completed for EACH baseline** (12 total for 3 baselines)
- [ ] All tasks processed (pending → doing → review)
- [ ] Algorithm Injection implements our optimizer/algorithm
- [ ] Metric Injection computes psi without affecting training
- [ ] Results Saver outputs comparison format
- [ ] Training Script has minimal modifications (--method argument)
- [ ] **Baseline's model, dataset, config are UNCHANGED**
- [ ] Test files created for each component
- [ ] CHANGES.md generated for all baselines

---

## SUCCESS/FAILURE

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### ✅ SUCCESS:
- **Tasks loaded from 05_tasks.yaml**
- Task status updated in YAML file (pending → doing → review)
- Archon KB searched before each code generation
- **Algorithm injection replaces/wraps optimizer ONLY**
- **Baseline's model is UNCHANGED**
- **Baseline's dataset loading is UNCHANGED**
- **Baseline's config is UNCHANGED**
- Training script has minimal modifications
- Test files created for EACH component
- CHANGES.md generated

### ❌ FAILURE:
- **Creating Archon tasks with mcp__archon__manage_task**
- **Not loading tasks from 05_tasks.yaml**
- Generating code for only 1 baseline
- Code generation without Archon KB search
- Transitioning to 'review' without test file
- **Modifying baseline's model loading** (Mode B violation!)
- **Modifying baseline's dataset loading** (Mode B violation!)
- **Modifying baseline's hyperparameters** (Mode B violation!)
- **Creating data-adapter or model-adapter code** (Mode B violation!)

---

**Next Step:** Load and execute `step-08-validation.md`
