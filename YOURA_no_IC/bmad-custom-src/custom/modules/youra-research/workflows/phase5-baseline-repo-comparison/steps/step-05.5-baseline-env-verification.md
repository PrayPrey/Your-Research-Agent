---
name: 'step-05.5-baseline-environment-verification'
description: 'Verify baseline environments (model, dataset, config) are accessible and compatible with our algorithm (Mode B)'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'

# File References
thisStepFile: '{workflow_path}/steps/step-05.5-baseline-env-verification.md'
prevStepFile: '{workflow_path}/steps/step-05-select.md'
nextStepFile: '{workflow_path}/steps/step-06-setup.md'
workflowFile: '{workflow_path}/workflow.md'
checkpointFile: '{baseline_folder}/05_baseline_checkpoint.yaml'

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 5.5: Verify Baseline Environments (Mode B)

## STEP GOAL:

Verify that each selected baseline's environment (model, dataset, config) is:
1. Accessible and can be set up
2. Compatible with our algorithm injection
3. Documented sufficiently for reproducibility

**Mode B Principle:** We USE baseline's environment as-is. This step verifies we CAN use it.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Verify baseline environments are usable
- 🚫 FORBIDDEN to replace or modify baseline's dataset/model/config selection
- 📖 Verify dataset is downloadable/accessible
- 🔗 Verify model code is complete and runnable
- 📊 Document what we will USE from each baseline

## EXECUTION PROTOCOLS:

- 🎯 Load baseline environments from checkpoint (from Step 4)
- 💾 Verify dataset accessibility for each baseline
- 📖 Verify model code completeness for each baseline
- 🚫 FORBIDDEN to select different datasets - we use baseline's

## CONTEXT BOUNDARIES:

- Available context: selected_baselines.md, evaluation_matrix.md, checkpoint
- Focus: Environment verification only
- Limits: Do not download datasets yet (that's Step 6)
- Dependencies: Step 5 must be completed with baseline selection

---

## 5.5.1 Load Baseline Environments

Load from checkpoint (populated in Step 4):

```python
# From checkpoint
baselines = checkpoint.selection.baselines # Array of 3 selected baselines

FOR EACH baseline in baselines:
    baseline_env = checkpoint.evaluation.baseline_environments[baseline.repo_name]
    # Contains: model, dataset, injection_point, injection_complexity
```

---

## 5.5.2 Dataset Accessibility Verification

**FOR EACH baseline:**

### Check Dataset Accessibility

| Dataset Source | Verification Method |
|----------------|---------------------|
| torchvision | Verify class exists: `torchvision.datasets.{name}` |
| HuggingFace | Verify dataset ID: `datasets.load_dataset("{id}")` |
| Custom URL | Verify URL is accessible (HEAD request) |
| Local/bundled | Verify path exists in repo |

### Verification Code Pattern

```python
def verify_dataset_accessibility(baseline_env):
    dataset_info = baseline_env.dataset

    if dataset_info.source == "torchvision":
        # Check torchvision has this dataset
        import torchvision.datasets as datasets
        assert hasattr(datasets, dataset_info.name), f"Dataset {dataset_info.name} not in torchvision"
        return {"status": "accessible", "method": "torchvision"}

    elif dataset_info.source == "huggingface":
        # Check HuggingFace dataset exists (without downloading)
        from datasets import get_dataset_config_names
        try:
            get_dataset_config_names(dataset_info.name)
            return {"status": "accessible", "method": "huggingface"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    elif dataset_info.source == "custom":
        # Check if loading code is provided
        if dataset_info.loading_code:
            return {"status": "accessible", "method": "custom", "needs_review": True}
        else:
            return {"status": "needs_manual", "reason": "No loading code found"}

    return {"status": "unknown"}
```

### Record Dataset Verification

```yaml
baselines[i].dataset_verification:
  status: "accessible|needs_manual|error"
  method: "{torchvision|huggingface|custom}"
  verified_at: "{timestamp}"
  notes: "{any_notes}"
```

---

## 5.5.3 Model Code Verification

**FOR EACH baseline:**

### Check Model Completeness

| Check | Method |
|-------|--------|
| Model class exists | Serena `find_symbol` for model class |
| Model can be instantiated | Check `__init__` signature |
| Forward pass defined | Check `forward` method exists |
| Dependencies available | Check imports are standard |

### Verification Using Serena

```python
# Activate baseline project
mcp__serena__activate_project(project="{baseline.clone_path}")

# Find model class
mcp__serena__find_symbol(
    name_path_pattern="{baseline_env.model.architecture}",
    include_body=False,
    depth=1 # Get methods
)

# Verify forward method exists
mcp__serena__find_symbol(
    name_path_pattern="{model_class}/forward",
    include_body=False
)
```

### Record Model Verification

```yaml
baselines[i].model_verification:
  class_found: true|false
  forward_method: true|false
  instantiable: true|false
  verified_at: "{timestamp}"
```

---

## 5.5.4 Config Verification

**FOR EACH baseline:**

### Check Config Accessibility

| Check | Method |
|-------|--------|
| LR is configurable | Check argparse or config file |
| Epochs is configurable | Check argparse or config file |
| Batch size is configurable | Check argparse or config file |
| Seed is configurable | Check argparse or config file |

### Record Config Verification

```yaml
baselines[i].config_verification:
  lr_configurable: true|false
  epochs_configurable: true|false
  batch_size_configurable: true|false
  seed_configurable: true|false
  config_file: "{path_if_exists}"
  verified_at: "{timestamp}"
```

---

## 5.5.5 Generate environment_verification.md

Create `{baseline_folder}/environment_verification.md`:

```markdown
# Baseline Environment Verification (Mode B)

## Verification Summary

| Baseline | Dataset | Model | Config | Status |
|----------|---------|-------|--------|--------|
| {repo_1} | ✅ | ✅ | ✅ | READY |
| {repo_2} | ✅ | ✅ | ⚠️ | READY (with notes) |
| {repo_3} | ✅ | ✅ | ✅ | READY |

---

## Baseline 1: {repo_name}

### Environment We Will Use

| Component | Value | Source |
|-----------|-------|--------|
| **Model** | {model_architecture} | {model_file} |
| **Dataset** | {dataset_name} | {dataset_source} |
| **Config** | LR={lr}, Epochs={epochs}, Batch={batch} | {config_source} |

### Dataset Verification
- **Status:** {accessible|needs_manual|error}
- **Source:** {torchvision|huggingface|custom}
- **Notes:** {any_notes}

### Model Verification
- **Class Found:** {yes/no}
- **Forward Method:** {yes/no}
- **Instantiable:** {yes/no}

### Config Verification
- **LR Configurable:** {yes/no}
- **Epochs Configurable:** {yes/no}
- **Batch Size Configurable:** {yes/no}
- **Seed Configurable:** {yes/no}

### Algorithm Injection Readiness
- **Injection Point:** `{file}:{line}`
- **Injection Strategy:** {replacement|wrapper|hook}
- **Complexity:** {simple|moderate|complex}

---

## Next Step
Step 6: Clone repositories and set up environments
```

---

## 5.5.6 Update Checkpoint

```yaml
current_step: 6
environment_verification:
  verified_at: "{timestamp}"
  baselines:
    - repo_name: "{repo_1}"
      dataset_status: "accessible"
      model_status: "verified"
      config_status: "verified"
      ready_for_setup: true
    - repo_name: "{repo_2}"
      dataset_status: "accessible"
      model_status: "verified"
      config_status: "partial"
      ready_for_setup: true
      notes: "{any_notes}"
    - repo_name: "{repo_3}"
      dataset_status: "accessible"
      model_status: "verified"
      config_status: "verified"
      ready_for_setup: true
updated_at: "{timestamp}"
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Dataset not accessible | Mark baseline, try to find alternative source |
| Model code incomplete | Check if it's importable from external package |
| Config not flexible | Document manual config requirements |
| All baselines have issues | Return to Step 5 to select alternatives |

---

## Graceful Degradation

If a baseline has minor issues:

```yaml
baselines[i]:
  status: "PROCEED_WITH_CAUTION"
  issues:
    - type: "config_manual"
      description: "LR must be changed in code, not via args"
      workaround: "Edit {file} directly"
```

Continue with baseline if workaround exists. Only SKIP if fundamental issue.

---

## Step Completion Criteria

- [ ] Dataset accessibility verified for EACH baseline
- [ ] Model code completeness verified for EACH baseline
- [ ] Config flexibility verified for EACH baseline
- [ ] environment_verification.md saved
- [ ] Checkpoint updated with verification results
- [ ] At least 1 baseline is ready for setup

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN environment_verification.md is saved and checkpoint is updated with verification results, will you then immediately load, read entire file, then execute `{workflow_path}/steps/step-06-setup.md` to begin baseline setup.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### ✅ SUCCESS:
- Baseline environments loaded from checkpoint
- **Dataset accessibility verified for EACH baseline**
- **Model code completeness verified for EACH baseline**
- **Config flexibility verified for EACH baseline**
- environment_verification.md saved with all results
- Checkpoint updated with verification status
- At least 1 baseline marked as ready_for_setup

### ❌ SYSTEM FAILURE:
- **Trying to select different datasets** (Mode B uses baseline's)
- **Trying to replace baseline's model** (Mode B uses baseline's)
- Not verifying dataset accessibility
- Not verifying model completeness
- Not saving environment_verification.md
- Not updating checkpoint
- Proceeding with 0 baselines ready

---

**Next Step:** Load and execute `step-06-setup.md`
