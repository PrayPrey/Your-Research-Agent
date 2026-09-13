---
name: 'step-07-report-generation'
description: 'Report Generation - Generate 04_validation.md comprehensive validation report'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'

# File References
thisStepFile: '{workflow_path}/steps/step-07-report-generation.md'
nextStepFile: '{workflow_path}/steps/step-08-completion.md'
workflowFile: '{workflow_path}/workflow.md'

# Template
validation_template: '{workflow_path}/templates/04_validation_template.md'

# Input Files
verification_state: '{research_folder}/verification_state.yaml'
experiment_brief: '{hypothesis_folder}/02c_experiment_brief.md'
results_file: '{hypothesis_folder}/experiment_results.json'
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'
code_folder: '{hypothesis_folder}/code'

# Output Files
validation_report: '{hypothesis_folder}/04_validation.md'
---

## Section 0.5: Load Checkpoint

> This ensures checkpoint state is available even after session interruption.

```python
# MANDATORY: Read checkpoint from file (context loss prevention)
checkpoint = read_yaml(checkpoint_file) # {hypothesis_folder}/04_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-initialize first.")

IF checkpoint.current_step < 7:
    STOP("ERROR: Step sequence violation. Current step: {checkpoint.current_step}")

# Log checkpoint load for debugging
print(f"✅ Checkpoint loaded: step={checkpoint.current_step}, gate_result={checkpoint.gate_result}")
```

---

# Step 7: Report Generation (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- MUST load and use 04_validation_template.md for report structure
- MUST gather data from checkpoint, verification_state, experiment_results, AND code folder
- MUST extract Phase 2C handoff data (proven components, hyperparameters, lessons)
- MUST generate recommendations for dependent hypotheses
- MUST verify no template placeholders remain in final report
- MUST include reflection data if step 6b was executed

---

## STEP GOAL

Generate the comprehensive validation report (`04_validation.md`) documenting Phase 4 activities, results, and Phase 2C handoff data.

---

## EXECUTION SEQUENCE

### 1. Load Template

```python
Read(validation_template)
```

### 2. Gather Report Data

**From checkpoint:**
```python
checkpoint_data = {
    "hypothesis_id": checkpoint.hypothesis_id,
    "tasks_total": checkpoint.tasks.total,
    "tasks_completed": checkpoint.tasks.completed,
    "coder_validator_cycles": checkpoint.coder_validator_cycles,
    "task_history": checkpoint.task_history,
    "partial_results": checkpoint.partial_results,
    "last_error": checkpoint.last_error,
    "unattended_mode": checkpoint.unattended_mode
}
```

**From verification_state.yaml:**
```python
gate_data = {
    "type": hypothesis_data["gate"]["type"],
    "satisfied": hypothesis_data["gate"]["satisfied"],
    "evaluation_result": hypothesis_data["gate"]["evaluation_result"],
    "criteria_results": hypothesis_data["gate"]["criteria_results"]
}
```

**From experiment_results.json:**
```python
experiment_data = {
    "execution_mode": results["execution_mode"],
    "status": results["status"],
    "metrics": results["metrics"],
    "training": results.get("training", {})
}
```

**From code folder:**
```python
# List generated files with sizes and modification dates
mcp__serena__list_dir(relative_path=code_folder, recursive=True)
```

### 3. Extract Phase 2C Handoff Data

#### 3a. Proven Components

```python
proven_components = []
FOR component in experiment_results.components_validated:
    IF component.status == "PASS":
        proven_components.append({
            "name": component.name,
            "file": component.file,
            "type": component.type,
            "evidence": "Passed validation",
            "reusable": True
        })
```

#### 3b. Optimal Hyperparameters

```python
optimal_hyperparameters = experiment_results.hyperparameters_final
# Include achieved_metrics for context
```

#### 3c. Lessons Learned (AI Analysis)

```python
lessons_learned = {
    "what_worked": analyze_passed_components(),
    "what_didnt_work": analyze_failed_tasks(),
    "unexpected_findings": extract_anomalies(),
    "key_insight": generate_key_takeaway()
}
```

#### 3d. Recommendations for Dependents

```python
# Find dependent hypotheses
dependents = find_hypotheses_with_this_prerequisite()

recommendations = {
    "general": generate_general_recommendations(),
    "specific": generate_specific_per_dependent(),
    "warnings": extract_from_lessons_what_didnt_work(),
    "suggested_hyperparameters": reference_optimal_params()
}
```

### 3.5 LLM-Autonomous Figure Generation

> **Purpose:** Generate research-appropriate figures by analyzing actual data structure and research context.
> **Key Principle:** LLM decides what figures to create based on data, not predefined templates.

#### 3.5.1 Create Figures Directory

```python
figures_folder = f"{hypothesis_folder}/figures"
Bash: mkdir -p {figures_folder}
```

#### 3.5.2 Analyze Available Data

**Step 1: Read data files and understand structure**

```python
# 1. Read results CSV or JSON
results_csv = f"{code_folder}/outputs/results.csv"
results_json = f"{hypothesis_folder}/experiment_results.json"

IF file_exists(results_csv):
    Read(results_csv) # Get column names and sample data
    # Example columns: epoch, loss, psi, seed, lr, accuracy, etc.
ELIF file_exists(results_json):
    Read(results_json) # JSON fallback - get metrics data

# 2. Read experiment results JSON (additional metrics)
IF file_exists(results_json):
    Read(results_json) # Get metrics, ablation data, etc.

# 3. Identify available data dimensions
data_analysis = {
    "columns": [...], # Actual column names from CSV or JSON keys
    "has_epoch_data": bool, # Can plot learning curves?
    "has_seed_variation": bool, # Can plot reproducibility?
    "has_lr_variation": bool, # Can plot LR sensitivity?
    "has_ablation": bool, # Can plot component contributions?
    "metric_columns": [...], # Which columns are metrics?
}
```

#### 3.5.3 Analyze Research Context

**Step 2: Understand what this research is about**

```python
# Read experiment brief for research context
Read(experiment_brief) # {hypothesis_folder}/02c_experiment_brief.md

# Extract key information
research_context = {
    "hypothesis_type": "...", # optimizer, loss function, architecture, etc.
    "primary_metric": "...", # psi, accuracy, f1, etc.
    "key_mechanism": "...", # What makes this method unique?
    "comparison_focus": "...", # What should figures emphasize?
}
```

#### 3.5.4 Decide Appropriate Figures

**Step 3: LLM decides what figures to generate based on data + context**

```python
# LLM DECISION PROCESS (not hard-coded rules!)
#
# Based on:
# 1. What data columns are available (CSV or JSON keys)
# 2. What the research is trying to prove
# 3. What would be most informative for Phase 6 paper
#
# Example decisions:
#
# IF research is about optimizer AND has lr variation:
# → Generate LR sensitivity plot
#
# IF research is about attention mechanism:
# → Generate attention visualization (if attention data exists)
#
# IF has epoch data with loss AND metric:
# → Generate learning curves
#
# IF has ablation_results in experiment_results.json:
# → Generate ablation bar chart
#
# IF has seed variation:
# → Generate reproducibility plot
#
# The LLM should NOT generate figures for data that doesn't exist!

figure_decisions = []

# LLM analyzes and adds appropriate figures:
# figure_decisions.append({
# "name": "learning_curves",
# "reason": "epoch, loss, and psi columns available",
# "x_axis": "epoch",
# "y_axes": ["loss", "psi"],
# "grouping": "seed" if has_seed else None
# })
```

#### 3.5.5 Generate Figure Code Dynamically

**Step 4: Write and execute matplotlib code**

```python
# For EACH decided figure, LLM generates appropriate matplotlib code
# The code should be tailored to the actual data structure

generate_figures_script = f"{code_folder}/generate_figures.py"

# LLM writes the script content based on:
# 1. Actual column names from data_analysis
# 2. Figure decisions from 3.5.4
# 3. Research context from 3.5.3

script_content = '''
#!/usr/bin/env python3
"""
LLM-Generated Figure Script for {hypothesis_id}
Generated based on actual data structure and research context.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
RESULTS_CSV = "{code_folder}/outputs/results.csv"
FIGURES_DIR = Path("{hypothesis_folder}/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(RESULTS_CSV)
    print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")

    # [LLM generates specific figure functions here based on data analysis]
    # Example: If 'epoch' and 'loss' columns exist:
    # create_learning_curves(df)

    # Example: If 'lr' column has multiple values:
    # create_lr_sensitivity(df)

    print(f"Generated figures in {FIGURES_DIR}")

if __name__ == '__main__':
    main()
'''

Write(generate_figures_script, script_content)

# Execute
Bash: cd {hypothesis_folder} && conda run -n {conda_env_name} python {generate_figures_script}
```

#### 3.5.6 Verify and Register Generated Figures

```python
# List generated figures
generated_figures = list_files(figures_folder, pattern="*.png")

# Create figure registry for Phase 6
figure_registry = {
    "generated_at": now(),
    "generation_method": "LLM-autonomous",
    "figures": []
}

FOR fig in generated_figures:
    figure_registry["figures"].append({
        "filename": fig,
        "path": f"figures/{fig}",
        "caption": "[TO BE FILLED IN PHASE 6]"
    })

# Update checkpoint
checkpoint.figures = {
    "generated": len(generated_figures) > 0,
    "folder": figures_folder,
    "files": generated_figures,
    "generation_method": "LLM-autonomous",
    "generated_at": now()
}
SAVE checkpoint

print(f"✅ Generated {len(generated_figures)} figures:")
FOR fig in generated_figures:
    print(f" - {fig}")
```

#### 3.5.7 Figure Generation Constraints

**LLM should NOT generate:**
- Figures for data that doesn't exist in the actual files
- Generic placeholder figures without real data
- Figures that don't support the hypothesis validation story

**LLM MUST:**
- Base all figure decisions on actual `02c_experiment_brief.md` analysis
- Verify data availability before deciding on each figure
- Generate figures that genuinely help validate the hypothesis

---

### 4. Generate Report Content

**Report Structure:**

```markdown
# Phase 4 Validation Report: {hypothesis_id}

**Generated:** {ISO8601}
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

## Hypothesis Summary
| Field | Value |
|-------|-------|
| **ID** | {hypothesis_id} |
| **Duration** | {calculated} |

## Code Generation Summary
### Task Statistics
| Metric | Value |
|--------|-------|
| Total Tasks | {total} |
| Completed | {completed} |
| Coder-Validator Cycles | {cycles}/5 |

### Generated Files
| File | Lines | Last Modified |
|------|-------|---------------|
{for each file}

## Code Quality Checklist
- [{✓|✗}] Syntax validation passed
- [{✓|✗}] Type hints compliance
- [{✓|✗}] API signatures match 03_logic.md

## Experiment Results
### Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
{for each metric}

## Gate Evaluation
| Field | Value |
|-------|-------|
| **Gate Type** | {type} |
| **Result** | {result} |
| **Satisfied** | {satisfied} |

## Next Steps
{based on gate result}

## Phase 2C Handoff
### Proven Components
{table of components}

### Optimal Hyperparameters
```yaml
{hyperparameters}
```

### Lessons Learned
- What Worked: {list}
- What Didn't Work: {list}
- Key Insight: {insight}

### Recommendations for Dependents
{recommendations}

## Appendix
{files reference, checkpoint state}
```

### 5. Write Report

```python
Write(validation_report, generated_content)

# Verify:
# - All sections present
# - No template placeholders remaining
# - Valid markdown syntax
```

### 6. Update Checkpoint

```python
checkpoint.current_step = 7
checkpoint.updated_at = now()
SAVE checkpoint
```

### 7. Proceed to Next Step

```python
checkpoint.current_step = 8
SAVE checkpoint

# Load and execute next step
Load, read entire file, then execute: {nextStepFile}
```

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| Template not found | Use inline default |
| Missing data | Mark as "N/A" in report |
| Write fails | Retry 3 times |

---

## STEP COMPLETION

**Step chain logic:**
| Condition | Action |
|-----------|--------|
| MUST_WORK failed | Continue to Step 8, STOP after cleanup |
| Normal flow | Continue to Step 8 for completion |

**On completion:** Load, read entire file, then execute `{nextStepFile}` (step-08-completion.md)
