---
name: 'step-01-init'
description: 'Initialize adversarial review, validate inputs, extract ground truth from verification_state.yaml and Phase 4/5 files'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase65-adversarial-review'

# File References
thisStepFile: '{workflow_path}/steps/step-01-init.md'
nextStepFile: '{workflow_path}/steps/step-02-adversary-r1.md'
workflowFile: '{workflow_path}/workflow.md'
checkpointTemplate: '{workflow_path}/templates/065_review_checkpoint_template.yaml'
---

# Step 1: Initialize Adversarial Review with Ground Truth Extraction

> **Execution Mode**: Main Session
> **Purpose**: Validate inputs, extract ground truth from verification_state.yaml and Phase 4/5 files
> **MCP Required**: Serena (for file discovery and pattern search)

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## Prerequisites

Before executing this step, ensure:

1. Phase 6 has completed successfully
2. `06_paper.md` exists in the paper folder
3. `verification_state.yaml` exists with Phase 4/5 results
4. Serena MCP is available for file discovery

---

## Execution Sequence

### 1.1 Load Configuration

```yaml
action: "Load module.yaml and resolve paths"
source: "{project_root}/bmad-custom-src/custom/modules/youra-research/module.yaml"
resolve:
  - research_folder
  - paper_folder: "{research_folder}/paper"
  - review_folder: "{paper_folder}/review"
```

### 1.2 Validate Required Inputs

**Required File Check:**

| File | Path | Required | Purpose |
|------|------|----------|---------|
| Paper | `{paper_folder}/06_paper.md` | YES | Paper to review |
| Verification State | `{research_folder}/verification_state.yaml` | YES | Ground truth extraction |
| Ground Truth | `{paper_folder}/065_ground_truth.yaml` | YES | Accuracy verification |
| Narrative Blueprint | `{paper_folder}/06_narrative_blueprint.yaml` | Recommended | Persuasiveness checks |
| Sections | `{paper_folder}/sections/` | Recommended | Cross-section analysis |

```yaml
action: "Validate required files exist"
on_missing:
  paper: "FATAL - Cannot proceed without paper"
  verification_state: "FATAL - Cannot verify claims without ground truth"
  ground_truth: "FATAL - Cannot verify accuracy without ground truth file"
  narrative_blueprint: "WARNING - Persuasiveness checks will be limited"
  sections: "WARNING - Cross-section analysis limited"
```

---

## CRITICAL: Ground Truth Extraction

### 1.3 Read verification_state.yaml

```yaml
action: "Read and parse verification_state.yaml"
file: "{research_folder}/verification_state.yaml"

extract:
  # Main hypothesis info
  main_hypothesis:
    id: "metadata.main_hypothesis_id"
    title: "main_hypothesis.title"
    statement: "main_hypothesis.statement"

  # Phase 5 baseline comparison results (GROUND TRUTH)
  baseline_comparison:
    status: "main_hypothesis.baseline_comparison.status"
    gate_result: "main_hypothesis.baseline_comparison.gate.result"
    our_performance: "main_hypothesis.baseline_comparison.results.ours_best_psi"
    baseline_performance: "main_hypothesis.baseline_comparison.results.baseline_best_psi"
    performance_gap: "main_hypothesis.baseline_comparison.results.performance_gap"
    p_value: "main_hypothesis.baseline_comparison.results.statistical_significance.p_value"
    significant: "main_hypothesis.baseline_comparison.results.statistical_significance.significant"
    baseline_name: "main_hypothesis.baseline_comparison.selected_baseline.name"

  # Sub-hypotheses results
  sub_hypotheses: "sub_hypotheses" # All sub-hypothesis entries

  # Statistics
  statistics:
    total_sub_hypotheses: "statistics.total_sub_hypotheses"
    validated: "statistics.validated_sub_hypotheses"
    failed: "statistics.failed_sub_hypotheses"
```

### 1.4 Use Serena MCP to Find Phase 4/5 Result Files

```yaml
action: "Use Serena MCP to discover actual result files"

mcp_calls:
  # Find all Phase 4 validation files
  - tool: "mcp__serena__find_file"
    params:
      file_name: "04_validation.md"
      search_path: "{research_folder}"
    store_as: "phase4_validation_files"

  # Find all Phase 5 baseline comparison files
  - tool: "mcp__serena__find_file"
    params:
      file_name: "05_baseline_comparison.md"
      search_path: "{research_folder}"
    store_as: "phase5_baseline_files"

  # Find actual experiment result files
  - tool: "mcp__serena__list_dir"
    params:
      path: "{research_folder}"
      recursive: true
    filter: "*.csv, *.json, *results*"
    store_as: "experiment_result_files"
```

### 1.5 Extract Actual Numbers from Phase 4/5 Reports

For each found validation file, extract key metrics:

```yaml
action: "Read Phase 4/5 files and extract actual numbers"

for_each: "phase4_validation_files"
extract_patterns:
  # Use Serena to search for specific patterns
  - tool: "mcp__serena__search_for_pattern"
    params:
      pattern: "worst.group.accuracy|WGA|accuracy.*\\d+\\.\\d+%"
      path: "{file_path}"
    store_as: "accuracy_mentions"

  - tool: "mcp__serena__search_for_pattern"
    params:
      pattern: "sensitivity|recall|precision|F1|FPR"
      path: "{file_path}"
    store_as: "detection_metrics"

  - tool: "mcp__serena__search_for_pattern"
    params:
      pattern: "baseline|GroupDRO|JTT|DFR|ERM"
      path: "{file_path}"
    store_as: "baseline_mentions"
```

### 1.6 Build Ground Truth Registry

Create `065_ground_truth.yaml`:

```yaml
# 065_ground_truth.yaml - Extracted from actual pipeline results
# This file contains the TRUE values that paper claims must match

created_at: "{ISO8601}"
source_files:
  verification_state: "{research_folder}/verification_state.yaml"
  phase4_validations: ["{list of found files}"]
  phase5_baselines: ["{list of found files}"]

# ============================================================================
# GROUND TRUTH: Numbers the paper MUST match or explain
# ============================================================================

main_hypothesis:
  id: "{from verification_state}"
  title: "{from verification_state}"

performance_metrics:
  # Our method's actual performance
  our_method:
    worst_group_accuracy: "{actual from Phase 4/5}"
    average_accuracy: "{actual from Phase 4/5}"
    std_deviation: "{actual from Phase 4/5}"
    seeds_used: ["{actual seeds}"]

  # Baseline actual performance
  baselines:
    ERM:
      reported_in_paper: null # To be filled from paper
      actual_from_phase5: "{from Phase 5 results}"
      match: null # true/false after comparison
    GroupDRO:
      reported_in_paper: null
      actual_from_phase5: "{from Phase 5 results}"
      match: null
    JTT:
      reported_in_paper: null
      actual_from_phase5: "{from Phase 5 results}"
      match: null
    DFR:
      reported_in_paper: null
      actual_from_phase5: "{from Phase 5 results}"
      match: null

detection_metrics:
  sensitivity: "{actual from Phase 4}"
  false_positive_rate: "{actual from Phase 4}"
  precision: "{actual from Phase 4}"
  cv_ratio: "{actual from Phase 4}"

methodology_facts:
  # Actual implementation details from code
  observation_epochs: "{actual from config/code}"
  intervention_epochs: "{actual from config/code}"
  top_k_percentage: "{actual from code}"
  upweight_factor: "{actual from code}"
  training_stages: "{single-run or 2-stage from code}"

dataset_facts:
  conflict_percentage: "{actual from data analysis}"
  total_training_samples: "{actual}"
  group_sizes: "{actual}"

# ============================================================================
# CLAIMS TO VERIFY
# ============================================================================
# Extracted from paper, to be compared against ground truth

paper_claims:
  # Will be populated by reading paper
  performance_claims: []
  methodology_claims: []
  novelty_claims: []
```

### 1.7 Extract Claims from Paper

```yaml
action: "Read paper and extract all numerical claims"

read_file: "{paper_folder}/06_paper.md"

extract_patterns:
  # Performance claims
  - pattern: "\\d+\\.\\d+%.*(?:accuracy|WGA|worst.group)"
    store_as: "performance_claims"

  # Detection claims
  - pattern: "\\d+\\.\\d+%.*(?:sensitivity|precision|FPR|recall)"
    store_as: "detection_claims"

  # Methodology claims
  - pattern: "(?:top|TOP).?\\d+%|epochs?\\s*\\d+|upweight.*\\d+"
    store_as: "methodology_claims"

  # Baseline claims
  - pattern: "(?:ERM|GroupDRO|JTT|DFR).*\\d+\\.\\d+%"
    store_as: "baseline_claims"
```

### 1.8 Pre-compute Discrepancies

```yaml
action: "Compare paper claims against ground truth"

comparisons:
  - category: "performance"
    paper_value: "{from paper_claims}"
    ground_truth: "{from ground_truth.performance_metrics}"
    discrepancy: "{calculate difference}"
    severity: "{NONE if match, MAJOR if >1%, FATAL if >5%}"

  - category: "detection"
    # Same comparison logic

  - category: "baseline"
    # Same comparison logic
```

### 1.9 Initialize Checkpoint with Ground Truth Reference

Create `065_review_checkpoint.yaml` using template-first pattern from `{checkpointTemplate}`:

> Template contains full schema: `by_persona`, `human_review_notes`, `persuasiveness_checks`, `convergence.criteria`.

```python
# 1.9a: Load checkpoint template
template_path = "{checkpointTemplate}" # 065_review_checkpoint_template.yaml
template_content = Read(template_path)
checkpoint = yaml.safe_load(template_content)

# 1.9b: Fill dynamic values
checkpoint["created_at"] = now_iso8601()
checkpoint["updated_at"] = now_iso8601()
checkpoint["status"] = "IN_PROGRESS"
checkpoint["current_round"] = 1

# Input validation results
checkpoint["input_validation"]["paper_exists"] = True
checkpoint["input_validation"]["verification_state_exists"] = True
checkpoint["input_validation"]["phase4_files_found"] = len(phase4_validation_files)
checkpoint["input_validation"]["phase5_files_found"] = len(phase5_baseline_files)
checkpoint["input_validation"]["ground_truth_extracted"] = True
checkpoint["input_validation"]["narrative_blueprint_exists"] = file_exists(narrative_blueprint)

# Ground truth and narrative blueprint files
checkpoint["ground_truth_file"] = f"{paper_folder}/065_ground_truth.yaml"
checkpoint["narrative_blueprint_file"] = narrative_blueprint if file_exists(narrative_blueprint) else ""

# Pre-computed discrepancies
checkpoint["pre_computed_discrepancies"]["performance_discrepancies"] = len(performance_discrepancies)
checkpoint["pre_computed_discrepancies"]["detection_discrepancies"] = len(detection_discrepancies)
checkpoint["pre_computed_discrepancies"]["baseline_discrepancies"] = len(baseline_discrepancies)
checkpoint["pre_computed_discrepancies"]["methodology_discrepancies"] = len(methodology_discrepancies)

# Paper paths
checkpoint["input_paper"] = f"{paper_folder}/06_paper.md"
checkpoint["latest_paper_version"] = f"{paper_folder}/06_paper.md"

# Execution mode
checkpoint["execution_mode"] = "UNATTENDED" # or "INTERACTIVE"

# Timestamps
checkpoint["timestamps"]["workflow_started"] = now_iso8601()

# 1.9c: Write checkpoint file
Write(f"{review_folder}/065_review_checkpoint.yaml", yaml.dump(checkpoint))
```

---

## Output

| Artifact | Path | Description |
|----------|------|-------------|
| Ground Truth | `{paper_folder}/065_ground_truth.yaml` | Extracted actual values (from Phase 6 Step 7) |
| Checkpoint | `{review_folder}/065_review_checkpoint.yaml` | State tracking with discrepancies |

---

## Validation Gate

Before proceeding, verify:

- [ ] verification_state.yaml read successfully
- [ ] At least one Phase 4 validation file found
- [ ] Ground truth values extracted
- [ ] Paper claims extracted
- [ ] Pre-computed discrepancies logged

If any critical extraction fails:
```yaml
action: "WARN and proceed with limited verification"
note: "Some ground truth values missing - Adversary will note as UNVERIFIABLE"
```

---

## Next Step

Proceed to **Step 2: Adversary Round 1** (`step-02-adversary-r1.md`)

The Adversary Agent will receive:
- Paper file path
- Ground truth file path
- Pre-computed discrepancy summary
