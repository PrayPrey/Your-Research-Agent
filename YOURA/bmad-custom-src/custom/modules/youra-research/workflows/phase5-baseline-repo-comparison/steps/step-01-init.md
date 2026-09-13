---
name: 'step-01-init'
description: 'Verify Phase 4 completion, understand hypothesis journey, create workspace'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'
references_path: '{workflow_path}/_references'

# File References
thisStepFile: '{workflow_path}/steps/step-01-init.md'
nextStepFile: '{workflow_path}/steps/step-02-define.md'
workflowFile: '{workflow_path}/workflow.md'
checkpointFile: '{baseline_folder}/05_baseline_checkpoint.yaml'
checkpointTemplate: '{workflow_path}/templates/05_baseline_checkpoint_template.yaml'

# Reference Files
hallucination_detection: '{references_path}/hallucination-detection-guide.md'
init_templates: '{references_path}/init-templates.md'

# Common Sections Reference
common_sections_ref: '{references_path}/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 1: Initialize Baseline Comparison

## STEP GOAL:

Verify Phase 4 completion, understand the hypothesis journey, and create workspace for baseline comparison. This step validates that real experiment data exists before proceeding.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus ONLY on initialization and verification
- 🚫 FORBIDDEN to look ahead to future steps or start baseline search
- 💬 Verify Phase 4 completion thoroughly before proceeding
- 🔍 DETECT hallucination/mock data patterns rigorously

## EXECUTION PROTOCOLS:

- 🎯 Verify all Phase 4 artifacts exist and are valid
- 💾 Create checkpoint file with initial state
- 📖 Extract and document hypothesis journey
- 🚫 FORBIDDEN to proceed without proper verification

## CONTEXT BOUNDARIES:

- Available context: verification_state.yaml, Phase 4 outputs
- Focus: Initialization and verification only
- Limits: Do not assume experiment validity without checking
- Dependencies: Phase 4 must be COMPLETED status

---

## 1.1 Verify Phase 4 Completion

Read `verification_state.yaml` and check ALL sub-hypotheses are completed.

### 1.1a Check Overall Workflow Status

<critical>
** FIX: State Recovery on Missing Phase Marker**

If `workflow.current_phase` is NOT "Phase 5" but all sub-hypotheses are COMPLETED,
attempt state recovery before failing.

**Common cause:** Context loss during Phase 4 → Phase 5 transition.
</critical>

**Check Path:** `workflow`

**Step 1: Read workflow status**

Read the following fields from verification_state.yaml:
- `workflow.current_phase`
- `workflow.status`

Log output: `🔍 Checking workflow state...`

**Step 2: Check for FAILED status**

| Condition | Action |
|-----------|--------|
| `workflow.status` = "FAILED" | STOP with error: "Workflow failed in earlier phase" |
| Otherwise | Continue to Step 3 |

**Step 3: Evaluate current_phase**

| Condition | Action |
|-----------|--------|
| `workflow.current_phase` = "Phase 5" | ✓ Proceed to Section 1.1b |
| `workflow.current_phase` IN ["Phase 4", "Hypothesis Loop Complete", ""] | ⚠️ Attempt state recovery (Step 4) |
| Other unexpected value | STOP with error: "Unexpected workflow.current_phase" |

**Step 4: State Recovery Attempt**

When `workflow.current_phase` is NOT "Phase 5":

1. **Check all sub-hypotheses status:**
   - Scan ALL hypotheses in `sub_hypotheses`
   - Check if EVERY hypothesis has `validation.status` = "COMPLETED"

2. **If ALL sub-hypotheses are COMPLETED:**

   Update the following fields in verification_state.yaml:

   | Field | Value |
   |-------|-------|
   | `workflow.current_phase` | "Phase 5" |
   | `workflow.sub_hypotheses_complete` | true |
   | `workflow.phase5_state_recovered` | true |
   | `workflow.phase5_state_recovered_at` | Current timestamp |

   Append recovery marker to `status_history`:

   | Field | Value |
   |-------|-------|
   | status | "STATE_RECOVERED" |
   | phase | "Phase 5" |
   | timestamp | Current timestamp |
   | trigger | "Phase 5 init state recovery" |
   | details | "workflow.current_phase recovered from context loss" |

   Save verification_state.yaml immediately.
   Log output: `✓ State recovered and saved`
   Proceed to Section 1.1b.

3. **If NOT all sub-hypotheses are COMPLETED:**

   Display detailed error message:
   - Show current `workflow.current_phase` value
   - List each sub-hypothesis with its `validation.status`
   - Provide resolution steps:
     1. Check if Phase 4 completed successfully
     2. Check hypothesis-loop Step 9 executed
     3. Manually set `workflow.current_phase = "Phase 5"` if needed

   STOP with error: "Workflow not at Phase 5 and recovery failed"

| Check | Condition | Action |
|-------|-----------|--------|
| `workflow.current_phase` | = "Phase 5" | ✓ Proceed |
| `workflow.current_phase` | ≠ "Phase 5" but all completed | ✓ Recover state and proceed |
| `workflow.current_phase` | ≠ "Phase 5" and not all completed | ✗ STOP with detailed error |
| `workflow.status` | = "FAILED" | ✗ STOP - "Workflow failed in earlier phase" |

### 1.1b Check All Sub-Hypotheses Completed

**Check Path:** `sub_hypotheses.*`

For EACH sub-hypothesis in `sub_hypotheses`:

| Check | Condition | Action |
|-------|-----------|--------|
| `validation.status` | = "COMPLETED" | ✓ Count as completed |
| `validation.status` | ≠ "COMPLETED" | ✗ STOP - "Sub-hypothesis {id} not completed" |

**Aggregate Check:**

| Metric | Condition | Action |
|--------|-----------|--------|
| All sub-hypotheses completed | `statistics.validated_sub_hypotheses` = `statistics.total_sub_hypotheses` | ✓ Proceed |
| Any sub-hypothesis incomplete | Count mismatch | ✗ STOP - "Not all sub-hypotheses completed Phase 4" |

### 1.1c Check MUST_WORK Gate Results

For EACH sub-hypothesis, check gate result:

| Check | Condition | Action |
|-------|-----------|--------|
| `gate.type` | = "MUST_WORK" | Check gate.satisfied |
| `gate.satisfied` | = true | ✓ Count as passed |
| `gate.satisfied` | = false | ✗ STOP - "Sub-hypothesis {id} failed MUST_WORK gate" |

**Save the following for each sub-hypothesis:**
- `id` → Sub-hypothesis ID
- `gate.satisfied` → Whether hypothesis succeeded
- `gate.type` → Gate type (MUST_WORK, SHOULD_WORK)
- `validation.result` → Result (PASS, PARTIAL, FAIL)

### 1.1d Read Main Hypothesis Info

**Check Path:** `main_hypothesis`

**Save the following:**
- `main_hypothesis.id` → Main hypothesis ID
- `main_hypothesis.title` → Main hypothesis title
- `main_hypothesis.statement` → Main hypothesis statement
- `main_hypothesis.controlled_variables` → Dataset, model, optimizer, hyperparameters

---

## 1.2 Understand Hypothesis Journey

> **Why important?** Understanding how the hypothesis evolved helps interpret baseline comparison results correctly.

Read `verification_state.yaml` and understand the **full journey** of this hypothesis.

### Key Questions

1. **Version Information**
   - What version is this hypothesis? (`version`)
   - How many times was it modified? (`modification_attempt`)
   - Which hypothesis was it modified from? (`modified_from`)

2. **Version History Analysis** (`version_history` array)
   - What result did each version get? (PASS/PARTIAL/FAIL)
   - Why was it modified? (`key_findings`, `modified_to`)
   - What lessons were learned?

3. **Reflection Analysis** (`reflection` section)
   - Was reflection triggered? (`triggered`)
   - Were there meaningful findings? (`has_meaningful_findings`)
   - What was learned? (`lessons_learned`)
   - Why was it modified? (`modification_rationale`)

4. **Final Validation Result** (`validation` section)
   - Result? (`result`: PASS/PARTIAL/FAIL)
   - Key findings? (`key_findings` array)
   - Success criteria met? (`success_criteria_met`)

5. **Failed Prerequisites Info** (`findings_from_failed_prerequisites`)
   - Any lessons from failed prerequisites?
   - How did this affect the current hypothesis?

### Journey Summary Output

Based on the above, output a summary using the format defined in `{init_templates}` > "Journey Summary Output Format".

---

## 1.3 Verify Required Files

Check that the following files exist:

| File | Path | Required |
|------|------|----------|
| Validation Report | `{hypothesis_folder}/04_validation.md` | ✓ |
| Experiment Results | `{hypothesis_folder}/experiment_results.json` | ✓ |
| Results CSV | `{hypothesis_folder}/code/outputs/results.csv` | ✓ |
| Measurements | `{hypothesis_folder}/code/measurements.py` | Optional |

**If files are missing:** STOP and report which files are missing.

---

## 1.4 Result Integrity Verification (Hallucination Detection)

> **Purpose:** Verify that Phase 4 results actually exist, were not fabricated, and were from real experiments (not synthetic/mock data).
>
> 📖 **REFERENCE:** Read `{hallucination_detection}` for detailed verification checks

Execute all checks from the hallucination detection guide:

1. **Basic Existence Checks** (1.4a)
   - Code files exist (train.py, model.py)
   - Results.csv has ≥10 rows
   - Data has variance > 0
   - Report values match CSV within 10%

2. **Synthetic/Mock Data Detection** (1.4b)
   - Experiment log exists and has real content
   - Checkpoint has experiment PID
   - File timestamps are consistent (not bulk generated)
   - No suspicious data patterns (too perfect, identical, no progression)

3. **Execution Evidence Verification** (1.4c)
   - Check experiment.log for epoch info
   - Verify checkpoint execution evidence
   - Timestamp sanity check

### Verification Result Decision

| Result | Action |
|--------|--------|
| All checks PASS | Proceed to Step 1.5 |
| Minor warnings (1-2) | Log warnings, proceed with caution |
| Multiple warnings (3+) | STOP - "Possible hallucination/mock data detected" |
| Critical failure | STOP - "Hallucination detected" |

---

## 1.5 Read Phase 2A Refinement

Read `03_refinement.yaml` and understand the hypothesis **requirements**.

### Information to Extract

| Item | Location | Example |
|------|----------|---------|
| Dataset requirements | Variables > Controlled | "synthetic", "MNIST" |
| Architecture requirements | Variables > Controlled | "2-layer MLP" |
| Optimizer requirements | Variables > Controlled | "Vanilla SGD" |
| Measurement requirements | Dependent Variables | "ψ", "T̃_c" |
| Gradient access needed? | Dependent Variables | True/False |

---

## 1.6 Create Workspace

Create the following folder structure:

```
{hypothesis_folder}/baseline_comparison/
├── baselines/ # Cloned baseline repositories
├── adaptations/ # Adaptation code
├── experiments/ # Experiment results
│ └── results/
├── reports/ # Reports and visualizations
└── changes/ # Code change records
```

---

## 1.7 ~~Create Step-Level Archon Tasks~~ ()

> See: `{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers/archon_pipeline_creation.md`

### 1.7a Get Pipeline Project ID

```python
# Get pipeline_project_id from verification_state (still needed for Phase Task updates)
pipeline_project_id = verification_state.get("metadata", {}).get("pipeline_project_id")

IF NOT pipeline_project_id:
    # Fallback location
    pipeline_project_id = verification_state.get("pipeline", {}).get("project_id")

IF NOT pipeline_project_id:
    STOP("Pipeline Project ID not found. Run Phase 0 first.")

```

---

## 1.8 Initialize Checkpoint (Template-First Pattern)

> This ensures consistency with Phase 4's template-first execution pattern.

```python
import yaml
from datetime import datetime

# ============================================================================
# STEP 1.8a: Load checkpoint template
# ============================================================================
# Reference: {workflow_path}/templates/05_baseline_checkpoint_template.yaml
print("📋 Loading checkpoint template...")

template_path = "{checkpointTemplate}" # From frontmatter
template_content = Read(template_path)
checkpoint = yaml.safe_load(template_content)

print(f"✓ Template loaded (version: {checkpoint.get('version', 'unknown')})")

# ============================================================================
# STEP 1.8a-2: Load workflow.yaml config (Single Source of Truth)
# ============================================================================
print("📋 Loading workflow.yaml config...")

workflow_yaml_path = f"{workflow_path}/workflow.yaml"
workflow_yaml = yaml.safe_load(Read(workflow_yaml_path))

wf_config = workflow_yaml.get("config", {})
wf_gate = workflow_yaml.get("gate", {}).get("criteria", {}).get("mode_b_comparison", {})
wf_comparison = wf_config.get("comparison", {})
wf_experiment = wf_config.get("experiment", {})

baselines_count = wf_experiment.get("baselines", 3)
# Calculate min_baselines_to_beat from threshold string "2/3"
threshold_str = str(wf_gate.get("baseline_win_threshold", "2/3"))
if "/" in threshold_str:
    num, den = threshold_str.split("/")
    import math
    min_baselines_to_beat = math.ceil(int(num) * baselines_count / int(den))
else:
    min_baselines_to_beat = int(float(threshold_str) * baselines_count)

print(f"✓ Workflow config loaded (baselines={baselines_count}, gate_threshold={threshold_str}, min_to_beat={min_baselines_to_beat})")

# ============================================================================
# STEP 1.8b: Fill dynamic values (replace {{placeholders}})
# ============================================================================
print("🔧 Filling dynamic values...")

# Timestamps
timestamp = datetime.now().isoformat()

# Prepare dynamic values map
dynamic_values = {
    "hypothesis_id": hypothesis_id, # e.g., "h-main"
    "main_hypothesis_id": main_hypothesis_id, # From verification_state.main_hypothesis.id
    "timestamp": timestamp,
    "hypothesis_folder": hypothesis_folder,
    "pipeline_project_id": pipeline_project_id,
    "conda_path": conda_path, # Auto-detected
    # Workflow config values (Single Source of Truth: workflow.yaml)
    "config_comparison_max_candidates": wf_comparison.get("max_candidates", 10),
    "config_comparison_baselines_to_select": wf_comparison.get("baselines_to_select", 3),
    "config_comparison_min_baselines_required": wf_comparison.get("min_baselines_required", 1),
    "config_comparison_min_stars": wf_comparison.get("min_stars", 10),
    "config_comparison_recent_activity_months": wf_comparison.get("recent_activity_months", 24),
    "config_comparison_dataset_overlap_weight": wf_comparison.get("dataset_overlap_weight", 0.3),
    "config_experiment_seeds": wf_experiment.get("seeds", 1),
    "config_experiment_baselines": baselines_count,
    "config_experiment_methods_per_baseline": wf_experiment.get("methods_per_baseline", 2),
    "config_experiment_total_runs": wf_experiment.get("total_runs", 6),
    "config_gate_baseline_win_threshold": threshold_str,
    "config_gate_min_baselines_to_beat": min_baselines_to_beat,
    "config_adaptation_max_retries": wf_config.get("max_adaptation_retries", 3),
    "config_adaptation_max_coder_validator_cycles": wf_config.get("max_coder_validator_cycles", 3),
    "config_experiment_max_retries": wf_config.get("max_experiment_retries", 2),
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
# STEP 1.8c: Populate Phase 4 context from verification_state
# ============================================================================
print("📝 Populating Phase 4 context...")

# Extract sub-hypothesis validation info
sub_hypotheses = verification_state.get("sub_hypotheses", {})
validated_count = sum(1 for h in sub_hypotheses.values()
                      if h.get("validation", {}).get("status") == "COMPLETED")
total_count = len(sub_hypotheses)

checkpoint["phase4_context"]["sub_hypotheses_validated"] = validated_count
checkpoint["phase4_context"]["sub_hypotheses_total"] = total_count
checkpoint["phase4_context"]["all_must_work_passed"] = all(
    h.get("gate", {}).get("satisfied", False)
    for h in sub_hypotheses.values()
    if h.get("gate", {}).get("type") == "MUST_WORK"
)

# Store Archon project ID
checkpoint["archon_project_id"] = pipeline_project_id

print(f"✓ Phase 4 context: {validated_count}/{total_count} sub-hypotheses validated")

# ============================================================================
# STEP 1.8d: Write checkpoint file
# ============================================================================
checkpoint_file = f"{baseline_folder}/05_baseline_checkpoint.yaml"
Write(checkpoint_file, yaml.dump(checkpoint, default_flow_style=False, allow_unicode=True))
print(f"✓ Checkpoint saved: {checkpoint_file}")
```

| Step | Description |
|------|-------------|
| 1.8a | Load template from file (NOT inline) |
| 1.8b | Fill `{{placeholder}}` values using `fill_placeholders()` |
| 1.8c | Populate Phase 4 context from verification_state |
| 1.8d | Write checkpoint file |

---

## 1.9 Update verification_state.yaml

Record baseline comparison start in `verification_state.yaml` using paths.

>
> 📖 **Templates:** See `{init_templates}` > "Verification State Updates" for all YAML templates.

### Update Sections

1. **main_hypothesis.baseline_comparison** - Initialize baseline comparison tracking
2. **episode** - Update episode status to ACTIVE
3. **workflow** - Set current_phase to "Phase 5"
4. **history** - Append Phase 5 start event

---

## Step Completion Criteria

Proceed to **Step 2** when all of the following are complete:

- [ ] Phase 4 completion verified
- [ ] Hypothesis journey understood and output
- [ ] Required files verified
- [ ] Integrity verification passed
- [ ] Workspace created
- [ ] Pipeline Project ID retrieved (for Phase Task updates)
- [ ] Checkpoint initialized
- [ ] verification_state.yaml updated

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN all initialization tasks are complete and checkpoint is created, will you then immediately load, read entire file, then execute `{workflow_path}/steps/step-02-define.md` to begin comparison scope definition.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### ✅ SUCCESS:
- Phase 4 validation status is COMPLETED
- Hypothesis journey documented with version history
- All required files exist and are valid
- No hallucination/mock data detected
- Workspace folders created
- Pipeline Project ID retrieved (for Phase Task updates)
- Checkpoint file created
- verification_state.yaml updated with baseline_comparison section

### ❌ SYSTEM FAILURE:
- Proceeding without Phase 4 COMPLETED status
- Skipping integrity verification
- Not detecting mock/synthetic data patterns
- Not retrieving Pipeline Project ID
- Not documenting hypothesis journey
- Proceeding with missing required files

---

**Next Step:** Load and execute `step-02-define.md`
