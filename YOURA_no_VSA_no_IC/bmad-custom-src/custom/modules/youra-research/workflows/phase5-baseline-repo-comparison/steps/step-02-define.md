---
name: 'step-02-define'
description: 'Define comparison requirements, search queries, and evaluation criteria'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'

# File References
thisStepFile: '{workflow_path}/steps/step-02-define.md'
prevStepFile: '{workflow_path}/steps/step-01-init.md'
nextStepFile: '{workflow_path}/steps/step-03-search.md'
workflowFile: '{workflow_path}/workflow.md'
checkpointFile: '{baseline_folder}/05_baseline_checkpoint.yaml'

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 2: Define Comparison Scope

## STEP GOAL:

Define baseline comparison scope and evaluation criteria based on hypothesis requirements and journey. This step creates the search strategy and evaluation framework for finding suitable baseline repositories.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus ONLY on defining scope and search strategy
- 🚫 FORBIDDEN to execute searches or clone repositories
- 💬 Extract requirements from hypothesis documents
- 📝 Generate actionable search queries

## EXECUTION PROTOCOLS:

- 🎯 Load context from Step 1 checkpoint
- 💾 Generate comparison_plan.md with search queries
- 📖 Define evaluation criteria with weights
- 🚫 FORBIDDEN to skip requirement extraction

## CONTEXT BOUNDARIES:

- Available context: Step 1 checkpoint, 03_refinement.yaml
- Focus: Search strategy and evaluation criteria only
- Limits: Do not execute searches yet
- Dependencies: Step 1 must be completed

---

---

## ⚠️ FAIR COMPARISON PRINCIPLE (CRITICAL!)

<critical>
**THIS IS THE MOST IMPORTANT PRINCIPLE OF PHASE 5**

❌ **FORBIDDEN:** Using baseline's pre-existing results for comparison
❌ **FORBIDDEN:** Comparing our model/dataset results with baseline's different model/dataset results

✅ **REQUIRED:** Baseline code MUST be re-executed with OUR conditions:
- **Same Model Architecture** as our hypothesis experiment
- **Same Dataset** as our hypothesis experiment
- **Same Hyperparameters** (LR, batch_size, epochs, seeds)
- **Same Metrics** (psi, loss, etc.)

**Why?**
- Baseline repo may have been trained on CIFAR-10, but our hypothesis uses synthetic data
- Baseline repo may use ResNet, but our hypothesis uses 2-layer MLP
- Comparing different experiments is NOT a fair comparison

**What we do:**
1. Find baseline **methodology/algorithm** (not baseline results)
2. Adapt baseline code to run on **our model/dataset**
3. Execute baseline with **identical conditions** as our Phase 4 experiment
4. Compare the NEW baseline results with our results
</critical>

---

## 2.1 Load Context

Load information saved in Step 1:

- `05_baseline_checkpoint.yaml` → Phase 4 results, journey info
- `03_refinement.yaml` → Hypothesis requirements (dataset, architecture, optimizer, measurements)

---

## 2.2 Determine Comparison Strategy Based on Journey

Determine comparison strategy based on hypothesis journey from `verification_state.yaml`.

### Strategy by Result

| Validation Result | Comparison Strategy |
|------------------|---------------------|
| **PASS** | Focus on proving **statistical advantage** over baseline |
| **PARTIAL** | **Separate** successful and failed parts when comparing with baseline |
| **FAIL** | Identify the **baseline** that baseline achieves, analyze failure causes |

### For Modified Hypotheses

If hypothesis was modified (`version > 1`):

- Understand difference between original intent and current hypothesis
- **Consider original intent** when comparing with baseline
- Reflect `lessons_learned` in baseline interpretation

---

## 2.3 Define Comparison Requirements

Define baseline selection criteria based on `03_refinement.yaml` requirements.

### Must Have (Required)

Conditions **absolutely required** for hypothesis verification:

| Requirement | Extract from Hypothesis | Search Keywords |
|-------------|------------------------|-----------------|
| Optimizer | Optimizer in `Controlled Variables` | "sgd", "vanilla sgd" |
| Gradient access | Gradient-related items in `Dependent Variables` | "backward", "grad" |
| Seed control | Reproducibility (always required) | "seed", "manual_seed" |
| Public code | Executable code (always required) | - |

### Should Have (Recommended)

Conditions **preferred** for better comparison:

| Requirement | Extract from Hypothesis | Search Keywords |
|-------------|------------------------|-----------------|
| Architecture | Architecture in `Controlled Variables` | "mlp", "feedforward" |
| Dataset type | Dataset in `Controlled Variables` | "synthetic", "mnist" |
| Hyperparameter config | Experiment configurability | "config", "--lr" |

---

## 2.4 Generate Search Queries

Extract **2-5 key keywords** from hypothesis requirements to generate search queries.

### Query Generation Rules

1. **Extract core concepts from hypothesis statement**
   - e.g., "simplicity bias", "phase transition", "SGD"

2. **Extract tech stack from requirements**
   - e.g., "pytorch", "mlp", "vanilla sgd"

3. **Combine to generate search queries** (max 10)

### Example Query Format

```
"{core_concept} implementation github pytorch"
"{optimizer} neural network training pytorch"
"{architecture} {dataset} training code"
```

---

## 2.5 Define Evaluation Criteria

### Suitability - 40%

How well does it match the hypothesis methodology?

| Item | Verification Method | Weight |
|------|---------------------|--------|
| Optimizer match | Check optimizer in code | 15% |
| Gradient access | Check backward() calls | 15% |
| Seed control | Check seed setting code | 10% |

### Quality - 30%

Is the repository quality good?

| Item | Verification Method | Weight |
|------|---------------------|--------|
| GitHub Stars | Check via API | 10% |
| Documentation | README exists | 10% |
| Recent activity | Last commit date | 10% |

### Injection Feasibility - 30%

How feasible is algorithm injection (Mode B)?

| Item | Verification Method | Weight |
|------|---------------------|--------|
| Optimizer isolation | Optimizer creation in single location | 15% |
| Training loop clarity | Clean backward/step pattern | 15% |

---

## 2.6 Define Adaptation Constraints

### Allowed Modifications

- Add new adapter files
- Config file override
- Metric logging injection (minimal code changes)
- Result format changes

### Disallowed Modifications

- Core learning algorithm changes
- Model architecture changes
- Optimizer logic changes
- Loss function changes

---

## 2.7 Define Visualization Requirements

Define figures to generate for Ours vs Baseline comparison.

### Required Figure (Mandatory)

| Figure | Description | Data Source |
|--------|-------------|-------------|
| **Metric Comparison Bar Chart** | Per-LR primary metric comparison with error bars | `comparison_data.csv` |

### Additional Figures (LLM Autonomous)

Based on experiment type and available data, generate appropriate comparison visualizations that best communicate the results. The LLM should autonomously decide what additional figures would be most informative for the specific experiment context.

### Figure Output Configuration

| Parameter | Value |
|-----------|-------|
| Output folder | `{baseline_folder}/figures/` |
| Format | PNG (300 DPI) |

---

## 2.8 Generate comparison_plan.md

Generate `{baseline_folder}/comparison_plan.md` with the above content.

### File Structure

```markdown
# Baseline Comparison Plan

## 1. Hypothesis Summary
- ID: {hypothesis_id}
- Statement: {statement}
- Validation Result: {result}

## 2. Hypothesis Journey Context
- Version: v{version}
- Modifications: {modification_attempt} times
- Key Learnings: {lessons_learned summary}

## 3. Comparison Strategy
{Strategy based on result}

## 4. Requirements
### Must Have
{Required requirements list}

### Should Have
{Recommended requirements list}

## 5. Search Queries
{Generated search query list}

## 6. Evaluation Criteria
{Evaluation criteria table}

## 7. Experimental Configuration (Must Match)
| Parameter | Value |
|-----------|-------|
| Learning Rates | [0.01, 0.1, 0.5] |
| Seeds | 5 |
| Epochs | 200 |
| Batch Size | 128 |
| Runs per Method | 15 (3 LR × 5 seeds) |

## 8. Visualization Requirements

### Required Figure (Mandatory)
- **Metric Comparison Bar Chart**: Per-LR comparison with min-max error bars

### Additional Figures (LLM Autonomous)
Generate appropriate comparison visualizations based on experiment context.

### Output Configuration
- Folder: {baseline_folder}/figures/
- Format: PNG (300 DPI)

## 9. Success Metrics
| Metric | Target |
|--------|--------|
| Direction | ours_mean > baseline_mean |
| Consistency | ours_min > baseline_mean OR ours_mean > baseline_max |
| LR Coverage | Majority of LRs show improvement |
```

---

## 2.9 Update Checkpoint

Update `05_baseline_checkpoint.yaml`:

```yaml
current_step: 2
comparison_plan:
  requirements_defined: true
  search_queries_count: {number of queries generated}
  evaluation_criteria_defined: true
```

---

## Step Completion Criteria

- [ ] Context loaded
- [ ] Journey-based comparison strategy determined
- [ ] Requirements defined (Must Have, Should Have)
- [ ] Search queries generated
- [ ] Evaluation criteria defined
- [ ] comparison_plan.md generated
- [ ] Checkpoint updated

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN comparison_plan.md is generated and checkpoint is updated, will you then immediately load, read entire file, then execute `{workflow_path}/steps/step-03-search.md` to begin repository search.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### ✅ SUCCESS:
- Context from Step 1 properly loaded
- Comparison strategy determined based on validation result
- Must Have and Should Have requirements extracted
- At least 5 search queries generated
- Evaluation criteria defined with proper weights (Suitability 40%, Quality 30%, Injection Feasibility 30%)
- comparison_plan.md saved to baseline_folder
- Checkpoint updated with step 2 complete

### ❌ SYSTEM FAILURE:
- Proceeding without loading Step 1 context
- Generating search queries without requirements extraction
- Missing Must Have requirements
- Not defining evaluation criteria weights
- Proceeding without saving comparison_plan.md
- Not updating checkpoint

---

**Next Step:** Load and execute `step-03-search.md`
