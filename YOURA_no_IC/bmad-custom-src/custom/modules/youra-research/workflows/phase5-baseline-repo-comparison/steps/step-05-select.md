---
name: 'step-05-select'
description: 'Select top N baseline repositories for multi-baseline comparison (N from checkpoint)'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'

# File References
thisStepFile: '{workflow_path}/steps/step-05-select.md'
prevStepFile: '{workflow_path}/steps/step-04-evaluate.md'
nextStepFile: '{workflow_path}/steps/step-05.5-baseline-env-verification.md'
workflowFile: '{workflow_path}/workflow.md'
checkpointFile: '{baseline_folder}/05_baseline_checkpoint.yaml'

# Config: Read from checkpoint.workflow_config.comparison (Source: workflow.yaml)

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 5: Select Baseline Repositories (Multi-Baseline)

## STEP GOAL:

Select the **top 3 baseline repositories** based on evaluation results for multi-baseline comparison, and **merge their dataset lists** for secondary dataset selection in Step 5.5. If fewer than 3 candidates are available, proceed with what's available (graceful degradation).

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus on selecting **top 3** repositories (not just 1)
- 🔗 Merge dataset lists from all 3 selected baselines
- 🚫 FORBIDDEN to clone or setup repositories (that's Step 6)
- 💬 Use suitability as primary selection criteria
- ⚠️ Warn if any selected baseline has suitability < 0.4

## EXECUTION PROTOCOLS:

- 🎯 Load evaluation_matrix.md with scores and datasets_used
- 💾 Generate selected_baselines.md with rationale for all 3
- 📖 Verify repository accessibility via gh CLI for all 3
- 🔗 Merge datasets from all selected baselines
- 🚫 FORBIDDEN to select without documenting rationale

## CONTEXT BOUNDARIES:

- Available context: evaluation_matrix.md, checkpoint
- Focus: Selection and rationale documentation only
- Limits: Do not clone or setup yet
- Dependencies: Step 4 must be completed with scores

---

---

## 5.1 Load Evaluation Results

Load evaluation matrix and get top 3 candidates for consideration.

---

## 5.1a Load Config from Checkpoint

```python
# Load config from checkpoint (Single Source of Truth: workflow.yaml)
checkpoint = read_yaml(checkpoint_file)
wf_config = checkpoint.get("workflow_config", {})
baselines_to_select = wf_config["comparison"]["baselines_to_select"]
min_baselines_required = wf_config["comparison"]["min_baselines_required"]
dataset_overlap_weight = wf_config["comparison"]["dataset_overlap_weight"] # 
```

---

## 5.2 Multi-Baseline Selection Logic

<critical>

When selecting multiple baselines, **prefer combinations that share common datasets**.
Baselines tested on the same dataset provide a stronger, more controlled comparison
because the ONLY variable is the algorithm/codebase — not the dataset.

This is scored via `dataset_overlap_weight` from workflow.yaml (default: 0.3).
</critical>

### Selection Algorithm (Top {baselines_to_select})

**Phase 1: Filter candidates** (suitability ≥ 0.4)

```python
eligible_candidates = [c for c in all_candidates if c.suitability >= 0.4]

IF len(eligible_candidates) < min_baselines_required:
    Return to Step 3 for expanded search
```

**Phase 2: Evaluate all possible combinations with dataset overlap bonus**

```python
from itertools import combinations

best_combination = None
best_combined_score = -1

for combo in combinations(eligible_candidates, baselines_to_select):
    # 1. Base score: sum of individual final scores (normalized 0~1 each)
    base_score = sum(c.final_score for c in combo) / len(combo)

    # 2. Dataset overlap bonus: how many datasets are shared across ALL baselines
    dataset_sets = [set(d.name for d in c.datasets_available) for c in combo]
    common_datasets = set.intersection(*dataset_sets) if dataset_sets else set()
    overlap_bonus = len(common_datasets) * dataset_overlap_weight

    # 3. Combined score
    combined_score = base_score + overlap_bonus

    if combined_score > best_combined_score:
        best_combined_score = combined_score
        best_combination = combo
        best_common_datasets = common_datasets

selected_baselines = list(best_combination)
```

**Example:**
| Combination | Base Score | Common Datasets | Overlap Bonus (×0.3) | Combined |
|-------------|-----------|-----------------|---------------------|----------|
| repo-A, repo-B, repo-C | 0.75 | {CIFAR10, MNIST} | 0.6 | **1.35** ← selected |
| repo-A, repo-B, repo-D | 0.80 | {CIFAR10} | 0.3 | 1.10 |
| repo-A, repo-D, repo-E | 0.85 | {} | 0.0 | 0.85 |

**Graceful degradation:**
- If fewer than {baselines_to_select} eligible candidates exist, select all eligible ones
- If only 1 candidate: dataset overlap is N/A, use base score only
- Minimum {min_baselines_required} required to proceed

### Suitability Warnings

For each selected baseline:
- If suitability < 0.6: Output "Medium suitability" note
- If suitability < 0.4: Output "Low suitability" warning

### Dataset Merging

After selecting baselines, merge their datasets_available lists:

```python
# Merge datasets from all selected baselines
merged_datasets = {}
for baseline in selected_baselines:
    for dataset in baseline.datasets_available:
        if dataset.name not in merged_datasets:
            merged_datasets[dataset.name] = {
                "name": dataset.name,
                "used_by": [baseline.repo_name],
                "sources": {baseline.repo_name: dataset.source}
            }
        else:
            merged_datasets[dataset.name]["used_by"].append(baseline.repo_name)
            merged_datasets[dataset.name]["sources"][baseline.repo_name] = dataset.source

# Sort by usage count (most commonly used first)
sorted_datasets = sorted(merged_datasets.values(), key=lambda x: len(x["used_by"]), reverse=True)

# Record common datasets (shared by ALL selected baselines)
common_datasets = [d for d in sorted_datasets if len(d["used_by"]) == len(selected_baselines)]
```

---

## 5.3 Verify Repository Accessibility (All 3)

For each of the top 3 selected baselines, verify accessibility:

```bash
# Verify all 3 repositories
for baseline in [baseline_1, baseline_2, baseline_3]:
    gh repo view {baseline.owner}/{baseline.repo} --json name
```

**If any baseline is inaccessible:**
1. Replace with next candidate from evaluation_matrix
2. Re-merge datasets with new selection
3. If no more candidates available, proceed with fewer baselines (graceful degradation)

---

## 5.4 Determine Adaptation Strategy Preview

Based on repository analysis, preview adaptation strategy:

| Component | Effort | Description |
|-----------|--------|-------------|
| Config Override | LOW | Create config file for our parameters |
| Data Adapter | MEDIUM | Convert our data format |
| Metric Injection | MEDIUM/HIGH | Inject our metric calculations |
| Results Saver | LOW | Add our results format |

### Effort Estimation

| Total Score | Estimated Effort |
|-------------|-----------------|
| ≤ 4 | LOW (< 4 hours) |
| 5-6 | MEDIUM (4-8 hours) |
| > 6 | HIGH (> 8 hours) |

---

## 5.5 Generate selected_baselines.md

Create `{baseline_folder}/selected_baselines.md`:

```markdown
# Selected Baseline Repositories (Multi-Baseline)

## Selection Summary

| Rank | Repository | Final Score | Suitability | Status |
|------|------------|-------------|-------------|--------|
| 1 | {baseline_1_name} | {score} | {suitability} | SELECTED |
| 2 | {baseline_2_name} | {score} | {suitability} | SELECTED |
| 3 | {baseline_3_name} | {score} | {suitability} | SELECTED |

**Total Baselines Selected:** {count}/{baselines_to_select}

---

## Baseline Details

### 1. {baseline_1_name} (Primary)

| Field | Value |
|-------|-------|
| **URL** | {url} |
| **Owner** | {owner} |
| **Stars** | {count} |
| **Final Score** | {score} |
| **Suitability** | {suitability} |

**Key Characteristics:**
- SGD: {yes/no} | Gradient Access: {yes/no} | Seed Control: {yes/no}

**Datasets Used:**
| Dataset | Source | Loading Code |
|---------|--------|--------------|
| {name} | {source} | {code} |

---

### 2. {baseline_2_name}
{same format as above}

---

### 3. {baseline_3_name}
{same format as above}

---

## Common Datasets

Datasets shared by ALL selected baselines:

| Common Dataset | Shared By | Source |
|----------------|-----------|--------|
| {dataset_name} | ALL {baselines_count} baselines | {torchvision/huggingface/custom} |

**Dataset Overlap Score:** {count} common datasets
**Selection Rationale:** This combination was selected because it maximizes dataset overlap
(weight={dataset_overlap_weight}) while maintaining high individual scores.

## Merged Dataset List (for Step 5.5)

Datasets extracted from all 3 baselines, sorted by usage count:

| Dataset | Used By (count) | Baselines | Source |
|---------|-----------------|-----------|--------|
| {dataset_name} | {count}/{baselines_count} | {baseline_1, baseline_2, baseline_3} | {source} |
| {dataset_name_2} | {count}/{baselines_count} | {baseline_1} | {source} |
...

---

## Risk Assessment

### Baseline-Specific Warnings
{list warnings for each baseline if suitability < 0.6}

### Mitigation Strategies
- Detailed code analysis for all 3 in Step 6
- If one baseline fails adaptation, continue with remaining 2
- Minimum 1 baseline required to proceed

---

## Next Step
Step 5.5: Select secondary dataset from merged dataset list
```

---

## 5.6 Update Checkpoint

```yaml
current_step: 5.5
selection:
  baselines_selected: 3
  common_datasets: ["{dataset1}"] # Datasets shared by ALL selected baselines
  dataset_overlap_score: {count_of_common_datasets} # Higher = stronger comparison
  baselines:
    - rank: 1
      repo_name: "{name}"
      repo_url: "{url}"
      owner: "{owner}"
      final_score: {score}
      suitability: {score}
      datasets_available: ["{dataset1}", "{dataset2}"]
    - rank: 2
      repo_name: "{name}"
      repo_url: "{url}"
      owner: "{owner}"
      final_score: {score}
      suitability: {score}
      datasets_available: ["{dataset1}"]
    - rank: 3
      repo_name: "{name}"
      repo_url: "{url}"
      owner: "{owner}"
      final_score: {score}
      suitability: {score}
      datasets_available: ["{dataset1}", "{dataset3}"]
  merged_datasets:
    - name: "{dataset1}"
      used_by_count: 3
      used_by: ["baseline_1", "baseline_2", "baseline_3"]
    - name: "{dataset2}"
      used_by_count: 1
      used_by: ["baseline_1"]
updated_at: "{timestamp}"
```

---

## Error Handling

| Error | Action |
|-------|--------|
| One baseline inaccessible | Replace with next candidate, re-merge datasets |
| Multiple baselines inaccessible | Proceed with available (min 1 required) |
| All candidates inaccessible | Return to Step 3 for new search |
| No suitable candidates | STOP with detailed report |

---

## Step Completion Criteria

- [ ] Top 3 baselines selected (or fewer with graceful degradation)
- [ ] All selected baselines verified accessible
- [ ] Selection rationale documented for each
- [ ] Datasets merged from all selected baselines
- [ ] selected_baselines.md saved
- [ ] Checkpoint updated with baselines and merged_datasets

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN selected_baselines.md is saved with all 3 baselines (or fewer with graceful degradation), merged dataset list, and checkpoint is updated, will you then immediately load, read entire file, then execute `{workflow_path}/steps/step-05.5-baseline-env-verification.md` to select secondary dataset.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### ✅ SUCCESS:
- All candidates loaded from evaluation_matrix.md with datasets_used
- **Top 3 baselines selected** (or graceful degradation with fewer)
- Selection algorithm applied for all 3 (suitability >= 0.4 required)
- **All 3 repositories verified accessible** via gh CLI
- **Datasets merged from all selected baselines**
- Merged dataset list sorted by usage count
- selected_baselines.md saved with rationale for all 3
- **Checkpoint updated with baselines array and merged_datasets**

### ❌ SYSTEM FAILURE:
- Selecting only 1 baseline when 3 are available
- Not merging datasets from selected baselines
- Selecting without loading evaluation data
- Ignoring suitability scores
- Not verifying repository accessibility for all 3
- Not documenting selection rationale for each
- Not saving selected_baselines.md
- Not updating checkpoint with merged_datasets

---

**Next Step:** Load and execute `step-05.5-baseline-env-verification.md`
