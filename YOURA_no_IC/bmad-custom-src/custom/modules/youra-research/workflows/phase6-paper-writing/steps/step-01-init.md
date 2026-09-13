---
name: 'step-01-init'
description: 'Create folder structure, collect figures, verify prerequisites for paper generation'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase6-paper-writing'

# File References
thisStepFile: '{workflow_path}/steps/step-01-init.md'
nextStepFile: '{workflow_path}/steps/step-02-narrative-design.md'
workflowFile: '{workflow_path}/workflow.md'
checkpointTemplate: '{workflow_path}/templates/06_paper_checkpoint_template.yaml' # 
---

# Step 1: Initialize Paper Generation

> **Step Position:** START -> **[Step 1: Initialize]** -> Step 2: Narrative Design
> **Purpose:** Create folder structure, collect figures, verify prerequisites
> **Context Isolation:** No (setup step)

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:

- 🎯 Focus only on folder creation, figure collection, and prerequisite verification
- 🚫 FORBIDDEN to skip artifact verification or figure collection steps
- 💬 Approach: Systematic setup and verification before content generation
- 📋 Ensure all required artifacts exist before proceeding to section generation

## EXECUTION PROTOCOLS:

- 🎯 Create paper folder structure with all required subdirectories
- 💾 Collect figures from Phase 4/5 outputs and register them
- 📖 Verify all required artifacts exist (verification_state.yaml, hypothesis files)
- 🚫 FORBIDDEN to proceed if critical artifacts are missing

## CONTEXT BOUNDARIES:

- Available context: verification_state.yaml, Phase 4/5 outputs
- Focus: Infrastructure setup, figure collection, prerequisite verification
- Limits: No content generation in this step, setup only
- Dependencies: Completed Phase 5 (or Phase 4 minimum)

---

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Create Output Folder Structure

Create the paper output folder structure:

```
{research_folder}/paper/
├── sections/ # Individual section files
│ ├── 00_abstract.md
│ ├── 01_introduction.md
│ ├── 02_related_work.md
│ ├── 03_methodology.md
│ ├── 04_experiments.md
│ ├── 05_results.md
│ ├── 06_discussion.md
│ └── 07_conclusion.md
├── figures/ # Collected figures from Phase 4/5
│ ├── fig_results_1.png
│ ├── fig_comparison_1.png
│ └── ...
├── 06_paper.md # Final merged paper
├── 06_references.bib # BibTeX references
└── 06_paper_checkpoint.yaml # Checkpoint file
```

**Action:** Create all folders using `mkdir -p` or equivalent.

---

## 2. Collect Figures from Phase 4 & 5

> **LLM-Autonomous Figure Collection:** Phase 4/5 generate figures dynamically based on actual research context. Do NOT expect specific filenames - discover whatever figures were generated.

### 2.1 Phase 4 Figures (Validation Results)

Search for ALL figures in Phase 4 output:

```
{hypothesis_folder}/figures/ # Primary location (LLM-autonomous)
{hypothesis_folder}/code/outputs/figures/
{hypothesis_folder}/code/outputs/*.png
{hypothesis_folder}/code/outputs/*.pdf
```

**Using Serena MCP:**
```
mcp__serena__list_dir(
  relative_path="{hypothesis_folder}/figures",
  recursive=true
)
mcp__serena__find_file(
  file_mask="*.png",
  relative_path="{hypothesis_folder}"
)
```

**Action:** Collect ALL .png/.pdf files found. Figure types and names vary based on research topic.

### 2.2 Phase 5 Figures (Baseline Comparison)

Search for ALL figures in Phase 5 output:

```
{hypothesis_folder}/baseline_comparison/figures/ # Primary location (LLM-autonomous)
{hypothesis_folder}/baseline_comparison/reports/
{hypothesis_folder}/baseline_comparison/experiments/
```

**Using Serena MCP:**
```
mcp__serena__find_file(
  file_mask="*.png",
  relative_path="{hypothesis_folder}/baseline_comparison"
)
```

**Action:** Collect ALL .png/.pdf files found. Figure types and names vary based on research topic.

### 2.3 Copy Figures to Paper Folder

Copy all collected figures to `{output_folder}/figures/` preserving original names:

**Process:**
1. List all figures found in Phase 4/5
2. Copy each to `{output_folder}/figures/` with original filename
3. Assign sequential figure numbers (fig_1, fig_2, ...) for paper references
4. Determine appropriate section for each figure based on content analysis

**Section Assignment Guidelines (LLM decides):**
| Content Type | Target Section |
|--------------|----------------|
| Architecture/model diagrams | Methodology |
| Training/learning curves | Results |
| Comparison/baseline charts | Results |
| Ablation analysis | Results |
| Other visualizations | LLM decides based on content |

### 2.5 LLM-Autonomous Figure Generation (Fallback)

> **Trigger:** If NO .png/.pdf files found in Phase 4/5 outputs
> **Purpose:** Generate figures from available JSON data sources
> **Pattern:** Same as Phase 4/5 LLM-Autonomous Figure Generation (Section 3.5)

#### 2.5.1 Trigger Check

```python
# Check if any figures were found from Phase 4/5
collected_figures = list_collected_png_pdf_files()

IF len(collected_figures) > 0:
    print(f"✅ Found {len(collected_figures)} figures from Phase 4/5. Skipping fallback generation.")
    SKIP to Section 3 (Create Figure Registry)

# No figures found - proceed with LLM-autonomous generation
print("⚠️ No figures from Phase 4/5. Initiating LLM-autonomous figure generation...")
```

#### 2.5.2 Analyze Available Data

**Step 1: Find and read data files**

```python
# 1. Find available data sources (JSON files)
json_files = []
json_files += find_files("{hypothesis_folder}/code/results/*.json")
json_files += find_files("{hypothesis_folder}/experiment_results.json")
json_files += find_files("{baseline_folder}/experiments/*.json")
json_files += find_files("{baseline_folder}/experiments/comparison_results.json")

IF len(json_files) == 0:
    print("❌ No JSON data files found. Cannot generate figures.")
    SKIP to Section 3 (Create Figure Registry with empty list)

# 2. Read JSON files and analyze data structure
FOR json_file IN json_files:
    Read(json_file)

# 3. Identify available data dimensions
data_analysis = {
    "json_files": [...], # List of found JSON files
    "has_metrics": bool, # Contains metrics data?
    "has_epoch_data": bool, # Can plot learning curves?
    "has_comparison_data": bool, # Can plot baseline comparisons?
    "has_ablation": bool, # Can plot component contributions?
    "metric_keys": [...], # Which keys are metrics?
    "comparison_methods": [...], # Methods being compared (if any)
}
```

#### 2.5.3 Analyze Research Context

**Step 2: Understand what this research is about**

```python
# Read experiment brief for research context
Read("{hypothesis_folder}/02c_experiment_brief.md")

# Also read Phase 4/5 validation reports for context
IF file_exists("{hypothesis_folder}/04_validation.md"):
    Read("{hypothesis_folder}/04_validation.md")
IF file_exists("{baseline_folder}/05_baseline_comparison.md"):
    Read("{baseline_folder}/05_baseline_comparison.md")

# Extract key information
research_context = {
    "hypothesis_type": "...", # optimizer, loss function, architecture, etc.
    "primary_metric": "...", # psi, accuracy, f1, etc.
    "key_mechanism": "...", # What makes this method unique?
    "comparison_focus": "...", # What should figures emphasize?
    "baseline_methods": [...], # What baselines were compared?
}
```

#### 2.5.4 Decide Appropriate Figures

**Step 3: LLM decides what figures to generate based on data + context**

```python
# LLM DECISION PROCESS (not hard-coded rules!)
#
# Based on:
# 1. What data keys are available in JSON files
# 2. What the research is trying to prove
# 3. What would be most informative for the paper
#
# Example decisions:
#
# IF has_comparison_data AND len(comparison_methods) > 1:
# → Generate comparison bar chart (our method vs baselines)
#
# IF has_epoch_data with loss AND metric:
# → Generate learning curves
#
# IF has_ablation in experiment_results.json:
# → Generate ablation bar chart
#
# IF research is about optimizer AND has lr_sensitivity data:
# → Generate LR sensitivity plot
#
# The LLM should NOT generate figures for data that doesn't exist!

figure_decisions = []

# LLM analyzes and adds appropriate figures:
# figure_decisions.append({
# "name": "comparison_results",
# "reason": "comparison_data with multiple methods available",
# "chart_type": "bar",
# "data_source": "comparison_results.json",
# "x_axis": "method",
# "y_axis": "primary_metric"
# })
```

#### 2.5.5 Generate Figure Code Dynamically

**Step 4: Write and execute matplotlib code**

```python
# For EACH decided figure, LLM generates appropriate matplotlib code
# The code should be tailored to the actual data structure

generate_figures_script = f"{output_folder}/generate_figures.py"

# LLM writes the script content based on:
# 1. Actual JSON structure from data_analysis
# 2. Figure decisions from 2.5.4
# 3. Research context from 2.5.3

script_content = '''
#!/usr/bin/env python3
"""
LLM-Generated Figure Script for Phase 6 Paper
Generated based on actual data structure and research context.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import numpy as np
from pathlib import Path

# Paths
FIGURES_DIR = Path("{output_folder}/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    # [LLM generates specific figure functions here based on data analysis]

    # Example: If comparison_results.json exists with method comparisons:
    # create_comparison_chart(data)

    # Example: If experiment_results.json has metrics over epochs:
    # create_learning_curves(data)

    print(f"Generated figures in {FIGURES_DIR}")

if __name__ == '__main__':
    main()
'''

Write(generate_figures_script, script_content)

# Execute
Bash: cd {output_folder} && python generate_figures.py
```

#### 2.5.6 Verify and Register Generated Figures

```python
# List generated figures
generated_figures = list_files("{output_folder}/figures/*.png")

IF len(generated_figures) == 0:
    print("⚠️ No figures generated. Proceeding without figures.")
ELSE:
    print(f"✅ Generated {len(generated_figures)} figures:")
    FOR fig in generated_figures:
        print(f" - {fig}")

# These figures will be registered in Section 3 (Create Figure Registry)
```

#### 2.5.7 Figure Generation Constraints

**LLM should NOT generate:**
- Figures for data that doesn't exist in the actual JSON files
- Generic placeholder figures without real data
- Figures that don't support the hypothesis validation story
- More than 5-6 figures (keep focused for paper)

**LLM MUST:**
- Base all figure decisions on actual data analysis (2.5.2)
- Verify data availability before deciding on each figure
- Generate figures that genuinely help tell the research story
- Use consistent styling (matplotlib defaults, readable fonts)

---

## 3. Create Figure Registry

> **Dynamic Registry:** The figure registry is generated based on actually discovered figures, NOT predefined templates.

Create `{output_folder}/figure_registry.yaml` dynamically:

```yaml
# Figure Registry for Paper
# Auto-generated by Phase 6 Step 1
# Based on LLM-autonomous figure discovery from Phase 4/5

figures:
  # FOR EACH discovered figure, create an entry:
  - id: "fig_{sequential_number}" # e.g., fig_1, fig_2, fig_3
    original_name: "{original_filename}" # e.g., "learning_curves.png"
    source: "{full_source_path}" # Where it was found
    target: "figures/{original_filename}" # Keep original name
    caption: "[TO BE FILLED IN SECTION GENERATION]"
    section: "{assigned_section}" # methodology, results, etc.
    width: "0.9\\textwidth"
    phase: "{phase_4|phase_5}" # Which phase generated it

  # Example entries (actual entries depend on discovered figures):
  # - id: "fig_1"
  # original_name: "optimizer_comparison.png"
  # source: "{hypothesis_folder}/figures/optimizer_comparison.png"
  # target: "figures/optimizer_comparison.png"
  # caption: "[TO BE FILLED]"
  # section: "results"
  # phase: "phase_4"

total_figures: {actual_count}
phase4_figures: {count}
phase5_figures: {count}
```

**Registry Generation Process:**
1. Iterate through all discovered figures
2. Assign sequential figure numbers
3. Analyze filename/content to determine appropriate section
4. Record source phase (Phase 4 or Phase 5)
5. Keep original filenames for traceability

---

## 4. Verify Required Artifacts

### 4.1 Core Files (REQUIRED)

| File | Path | Status |
|------|------|--------|
| verification_state.yaml | `{research_folder}/verification_state.yaml` | [ ] |
| Phase 2A Dialogue Refinement | `{research_folder}/03_refinement.yaml` | [ ] |
| Verification Plan | `{research_folder}/02b_verification_plan.md` | [ ] |

**If any REQUIRED file is missing:** STOP and report error.

### 4.2 Per-Hypothesis Files

For each hypothesis with `status: COMPLETED`:

| File | Path Pattern | Required |
|------|--------------|----------|
| Experiment Brief | `{hypothesis_folder}/02c_experiment_brief.md` | Yes |
| PRD | `{hypothesis_folder}/03_prd.md` | Yes |
| Architecture | `{hypothesis_folder}/03_architecture.md` | Yes |
| Validated Hypothesis | `{research_folder}/045_validated_hypothesis.md` | **Critical** |
| Validation Report | `{hypothesis_folder}/04_validation.md` | Optional (ground truth) |
| Baseline Comparison | `{hypothesis_folder}/baseline_comparison/05_baseline_comparison.md` | If exists |

### 4.3 Optional Context Files

| File | Path | Usage |
|------|------|-------|
| Brainstorm Session | `{research_folder}/00_brainstorm_session.md` | Introduction |
| Targeted Research | `{research_folder}/01_targeted_research.md` | Related Work |
| Full Research Data | `{research_folder}/01_targeted_research_full.md` | Citations |

---

## 5. Load Main Hypothesis Info

Read `verification_state.yaml` and extract:

```yaml
main_hypothesis:
  id: "{hypothesis_id}"
  title: "{title}"
  gate_result: "PASS" # or PARTIAL, FAIL
```

---

## 6. Create Checkpoint File

> Template: `{checkpointTemplate}` (06_paper_checkpoint_template.yaml)

```python
import yaml
from datetime import datetime

# 6a: Load checkpoint template
template_path = "{checkpointTemplate}"
template_content = Read(template_path)
checkpoint = yaml.safe_load(template_content)

# 6b: Fill dynamic values
timestamp = datetime.now().isoformat()
checkpoint["created_at"] = timestamp
checkpoint["updated_at"] = timestamp
checkpoint["main_hypothesis"]["id"] = hypothesis_id
checkpoint["main_hypothesis"]["title"] = hypothesis_title
checkpoint["main_hypothesis"]["gate_result"] = gate_result

# 6c: Record figure collection results
checkpoint["figures"]["total"] = total_figures_collected
checkpoint["figures"]["from_phase4"] = phase4_figure_count
checkpoint["figures"]["from_phase5"] = phase5_figure_count
checkpoint["figures"]["registry_file"] = "figure_registry.yaml"

# 6d: Write checkpoint
checkpoint_file = f"{output_folder}/06_paper_checkpoint.yaml"
Write(checkpoint_file, yaml.dump(checkpoint, default_flow_style=False, allow_unicode=True))
print(f"✓ Checkpoint created: {checkpoint_file}")
```

| Step | Description |
|------|-------------|
| 6a | Load template from file (Story Group Architecture) |
| 6b | Fill timestamps and hypothesis info |
| 6c | Record figure collection results |
| 6d | Write checkpoint file |

---

## 7. Update Checkpoint

Update checkpoint:
- `current_step: 2`
- `updated_at: "{ISO8601}"`

---

## 8. Proceed to Next Step

**NEXT:** Load, read the full file, and then execute `{nextStepFile}` (step-02-narrative-design.md)

** Execution Model (Story Group Architecture):**
- **Steps 1, 2, 7** run in **Main Session** (full context)
- **Steps 3, 4, 5** run as **Task Agents** (Story Groups with shared context within group)
- **Step 6** runs as **Task Agent** (References, isolated context)

**CRITICAL:** Step 2 (Narrative Design) MUST complete before any section generation (Steps 3-5).

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Paper folder structure created with all required subdirectories (sections/, figures/)
- Figures collected from Phase 4/5 outputs and registered in figure_registry.yaml
- All required artifacts verified (verification_state.yaml, Phase 2A dialogue/synthesis, etc.)
- Checkpoint file created with schema (Story Group Architecture)
- Main hypothesis info loaded and documented

### ❌ SYSTEM FAILURE:

- Skipping folder creation or figure collection steps
- Not verifying required artifacts before proceeding
- Proceeding when critical artifacts (verification_state.yaml) are missing
- Not creating checkpoint file for state tracking
- Missing figure registration or improper figure naming

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
