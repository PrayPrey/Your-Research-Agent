# Step 6 Setup Templates

> **Referenced by:** step-06-setup.md
> **Purpose:** Markdown templates for setup_log.md and code_analysis.md

---

## setup_log.md Template

```markdown
# Setup Log (Multi-Baseline)

## Setup Date: {timestamp}
## Total Baselines: {count}/{baselines_to_select}

---

## Baseline 1: {baseline_1.repo_name}

### Clone Information
| Field | Value |
|-------|-------|
| URL | {repo_url} |
| Clone Path | {clone_path} |
| Original Commit | {commit_hash} |
| Branch | youra-baseline |
| Status | {success/failed} |

### Environment Setup
| Field | Value |
|-------|-------|
| Conda Environment | baseline-{repo_name} |
| Python Version | 3.10 |
| Status | {success/failed} |

### Key Files
| Category | File |
|----------|------|
| Training | {train.py path} |
| Model | {model.py path} |

---

## Baseline 2: {baseline_2.repo_name}
{same format as above}

---

## Baseline 3: {baseline_3.repo_name}
{same format as above}

---

## Secondary Dataset

| Field | Value |
|-------|-------|
| Name | {secondary_dataset.name} |
| Cache Path | {cache_path} |
| Status | {downloaded/failed} |
| Verified | {yes/no} |
```

---

## code_analysis.md Template

```markdown
# Code Analysis (Multi-Baseline)

## Analysis Date: {timestamp}
## Total Baselines Analyzed: {count}/{baselines_to_select}

---

## Baseline 1: {baseline_1.repo_name}

### Architecture Overview
{Directory structure tree}

### Key Code Sections
- **Training Loop:** {file}:{line} - train()
- **Backward Pass:** {file}:{line}
- **Optimizer:** {type} at {file}:{line}
- **DataLoader:** {file}:{line}

### Compatibility Assessment

| Aspect | Status | Notes |
|--------|--------|-------|
| Dataset | {compatible?} | {explanation} |
| Optimizer | {compatible?} | {explanation} |
| Gradient Access | {compatible?} | {explanation} |

**Compatibility Score:** {score}%
**Strategy:** {strategy}
**Status:** {PROCEED/SKIP}

### Integration Points
{List of insertion points}

---

## Baseline 2: {baseline_2.repo_name}
{same format as above}

---

## Baseline 3: {baseline_3.repo_name}
{same format as above}

---

## Summary

| Baseline | Compatibility | Strategy | Status |
|----------|--------------|----------|--------|
| {baseline_1} | {score}% | {strategy} | PROCEED |
| {baseline_2} | {score}% | {strategy} | PROCEED |
| {baseline_3} | {score}% | {strategy} | PROCEED/SKIP |

**Baselines Proceeding:** {count}/{baselines_to_select}
```

---

## Checkpoint Update Template (6.9)

```yaml
current_step: 7
selection:
  baselines_proceeding: {count} # Number of baselines that passed compatibility
  baselines:
    - rank: 1
      repo_name: "{name}"
      clone_path: "{path}"
      conda_env: "baseline-{repo_name}"
      compatibility_score: {score}
      strategy: "{strategy}"
      status: "PROCEED|SKIP"
    - rank: 2
      repo_name: "{name}"
      clone_path: "{path}"
      conda_env: "baseline-{repo_name}"
      compatibility_score: {score}
      strategy: "{strategy}"
      status: "PROCEED|SKIP"
    - rank: 3
      repo_name: "{name}"
      clone_path: "{path}"
      conda_env: "baseline-{repo_name}"
      compatibility_score: {score}
      strategy: "{strategy}"
      status: "PROCEED|SKIP"
dataset_selection:
  primary_dataset: "{name}"
  secondary_dataset:
    name: "{name}"
    status: "downloaded|failed"
    cache_path: "{path}"
    verified: true|false
warnings: {warning list if any}
updated_at: "{timestamp}"
```
