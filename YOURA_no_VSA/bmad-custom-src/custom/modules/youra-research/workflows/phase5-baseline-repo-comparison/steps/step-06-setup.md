---
name: 'step-06-setup'
description: 'Clone selected repositories, setup environment, and analyze code for algorithm injection (Mode B)'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'

# File References
thisStepFile: '{workflow_path}/steps/step-06-setup.md'
prevStepFile: '{workflow_path}/steps/step-05.5-baseline-env-verification.md'
nextStepFile: '{workflow_path}/steps/step-07-adaptation-coding.md'
workflowFile: '{workflow_path}/workflow.md'
checkpointFile: '{baseline_folder}/05_baseline_checkpoint.yaml'

# Reference Files
setup_templates: '{workflow_path}/_references/setup-templates.md'
algorithm_injection_ref: '{workflow_path}/_references/algorithm-injection.md'
fair_comparison_ref: '{workflow_path}/_references/fair-comparison-principle.md'

# Task Template
tasks_template: '{workflow_path}/templates/05_tasks_template.yaml'
tasks_output_file: '{baseline_folder}/05_tasks.yaml'

# Config: Read from checkpoint.workflow_config (Source: workflow.yaml)

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 6: Setup & Analyze Repositories for Algorithm Injection (Mode B)

## STEP GOAL:

Clone **all 3 selected baseline repositories**, setup conda environments for each, and analyze code structure with Serena MCP to prepare for **algorithm injection**.

**Mode B Principle:** We USE baseline's environment (model, dataset, config). We only INJECT our algorithm.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus ONLY on cloning, environment setup, and code analysis for **all 3 baselines**
- 🚫 FORBIDDEN to generate adaptation code (that's Step 7)
- 💬 Use Serena MCP for code structure analysis of each baseline
- 🔍 Identify **algorithm injection points** in each baseline (NOT data/model adapters)
- 📖 **MUST read README.md** for each baseline to understand their environment

## EXECUTION PROTOCOLS:

- 🎯 Clone **all 3 repositories** to baselines/ folder
- 💾 Create conda environment for **each baseline**
- 📖 **Read README.md for each baseline** (MANDATORY)
- 📖 Analyze **each baseline** with Serena MCP (symbols, patterns)
- 🔍 Identify **algorithm injection points** (optimizer creation, backward location)
- 🚫 FORBIDDEN to proceed without injection point analysis for all baselines

## CONTEXT BOUNDARIES:

- Available context: selected_baselines.md, environment_verification.md, checkpoint
- Focus: Setup and injection point analysis for all 3 baselines
- Limits: Do not write adaptation code yet
- Dependencies: Step 5.5 must be completed with environment verification

---

---

## 6.1 Load Context

Load information saved in Steps 5 and 5.5:

- `selected_baselines.md` → All 3 selected baselines info
- `environment_verification.md` → Verification results for each baseline
- `05_baseline_checkpoint.yaml` → baselines array, environment_verification

```python
# Load all 3 baselines from checkpoint
baselines = checkpoint.selection.baselines # Array of 3 baselines
env_verification = checkpoint.environment_verification # From Step 5.5
```

---

## 6.2 Clone All Repositories (Loop)

**FOR EACH baseline in baselines (1 to 3):**

### Clone Procedure

1. Create `{baseline_folder}/baselines/{baseline.repo_name}/` folder
2. Execute git clone for this baseline
3. Create youra-baseline branch

```bash
# For each baseline
git clone {baseline.repo_url} {baseline_folder}/baselines/{baseline.repo_name}
cd {baseline_folder}/baselines/{baseline.repo_name}
git checkout -b youra-baseline
```

### Verification (per baseline)

| Check | Method |
|-------|--------|
| Clone success | Folder exists |
| Files present | ls -la |
| Commit hash | git log -1 --format="%H" |

**Record clone status for each baseline:**

```yaml
baselines[i].clone:
  status: "success|failed"
  clone_path: "{path}"
  commit_hash: "{sha}"
```

---

## 6.3 Environment Analysis and Setup (Per Baseline)

**FOR EACH baseline in baselines (1 to 3):**

### Check Environment Files

Find the following files in each repository:

| File | Package Manager |
|------|-----------------|
| requirements.txt | pip |
| environment.yml | conda |
| pyproject.toml | pip/poetry |
| Pipfile | pipenv |

### Create Conda Environment

Environment name: `baseline-{baseline.repo_name}`

- If environment.yml exists → `conda env create -f environment.yml -n baseline-{repo_name}`
- Otherwise → `conda create -n baseline-{repo_name} python=3.10`
- If requirements.txt exists → `pip install -r requirements.txt`

**Record environment status for each baseline:**

```yaml
baselines[i].env:
  conda_env: "baseline-{repo_name}"
  status: "success|failed"
```

---

## 6.4 README.md Analysis (MANDATORY - Per Baseline)

<critical>
**Mode B REQUIRES thorough understanding of baseline's environment.**
You MUST read and analyze README.md before proceeding with code analysis.
</critical>

**FOR EACH baseline in baselines (1 to 3):**

### Read README.md

```python
readme_path = f"{clone_path}/README.md"
Read(readme_path) # FULL READ, no limit
```

### Extract from README

| Information | Why Needed |
|-------------|------------|
| Model architecture description | Understand what model we'll use |
| Dataset requirements | Understand what data we'll use |
| Training procedure | Understand where to inject algorithm |
| Expected results/benchmarks | Baseline for comparison |
| How to run training | Command line arguments, configs |

### Record README Analysis

```yaml
baselines[i].readme_analysis:
  model_description: "{extracted}"
  dataset_info: "{extracted}"
  training_procedure: "{extracted}"
  expected_results: "{extracted}"
  run_command: "{extracted}"
  readme_quality: "comprehensive|adequate|minimal|none"
```

---

## 6.5 Code Analysis with Serena MCP (Per Baseline)

**FOR EACH baseline in baselines (1 to 3):**

Use Serena MCP to analyze code structure of each baseline.

### Analysis Order (repeat for each baseline)

1. **Activate project**: `mcp__serena__activate_project(project="{clone_path}")`
2. **Directory structure**: `mcp__serena__list_dir` (recursive=True)
3. **Find training files**: `mcp__serena__find_file` (file_mask="train*.py")
4. **Find model files**: `mcp__serena__find_file` (file_mask="model*.py")

### Core Code Analysis (per baseline)

| Target | Serena Tool | What to Find |
|--------|-------------|--------------|
| Training loop | `get_symbols_overview` | train() function |
| Model definition | `find_symbol` (kind=5) | Classes |
| Optimizer setup | `search_for_pattern` | "optim.SGD", "torch.optim" |
| DataLoader | `search_for_pattern` | "DataLoader", "Dataset" |

---

## 6.6 Algorithm Injection Point Analysis (Per Baseline)

<critical>
**Mode B Critical:** Identify where to inject our algorithm.
We DO NOT replace model or dataset. We ONLY inject our optimizer/algorithm.
</critical>

**FOR EACH baseline in baselines (1 to 3):**

### Find Optimizer Creation Location

```python
mcp__serena__search_for_pattern(
    substring_pattern="optim\\.SGD\\(|optim\\.Adam\\(|torch\\.optim\\.",
    relative_path="{clone_path}",
    paths_include_glob="*.py",
    context_lines_before=2,
    context_lines_after=3
)
```

### Analyze Optimizer Interface

| Check | Method | Result |
|-------|--------|--------|
| Standard PyTorch optimizer? | Look for `optim.XXX(model.parameters(), lr=...)` | standard/custom |
| Custom optimizer class? | Look for `class XXX(Optimizer)` | yes/no |
| Optimizer wrapper? | Look for scheduler or wrapper patterns | yes/no |
| Multiple optimizers? | Check if GAN/multi-model setup | single/multiple |

### Determine Injection Strategy

| Baseline Condition | Strategy | Description |
|-------------------|----------|-------------|
| Standard optimizer (`optim.SGD`, `optim.Adam`) | REPLACEMENT | Replace optimizer class with ours |
| Custom optimizer with standard interface | WRAPPER | Wrap existing optimizer with our logic |
| Complex training loop | HOOK | Inject hooks at specific points |

### Record Injection Analysis

```yaml
baselines[i].injection_analysis:
  optimizer_location:
    file: "{file_path}"
    line: {line_number}
    current_optimizer: "{optimizer_class}"
    interface: "standard|custom|wrapped"
  backward_location:
    file: "{file_path}"
    line: {line_number}
  injection_strategy: "replacement|wrapper|hook"
  injection_complexity: "simple|moderate|complex"
```

### Injection Feasibility Score (per baseline)

| Factor | Points |
|--------|--------|
| Standard optimizer interface | 30 |
| Single optimizer (not multi-model) | 25 |
| Clear training loop | 20 |
| Small codebase (< 10 files) | 15 |
| Has config file/argparse | 10 |

**Complexity Penalty:**

| Complexity | Penalty |
|------------|---------|
| Simple (standard optimizer, clear loop) | 0 |
| Moderate (custom optimizer, but standard interface) | -10 |
| Complex (multiple optimizers, custom training) | -25 |

---

## 6.7 Generate setup_log.md (All Baselines)

Create `setup_log.md` using the template from `{setup_templates}` > "setup_log.md Template".

Populate with:
- Clone information for all 3 baselines
- Environment setup status for each
- README summary for each
- Key files identified for each

---

## 6.8 Generate code_analysis.md (All Baselines)

Create `code_analysis.md` with focus on **algorithm injection points**:

```markdown
# Code Analysis - Algorithm Injection (Mode B)

## Analysis Summary
- **Total Baselines:** {count}
- **Analysis Date:** {timestamp}
- **Mode:** B (Inject OUR algorithm into BASELINE's environment)

---

## Baseline 1: {repo_name}

### Environment We Will Use
- **Model:** {model_architecture} (from baseline)
- **Dataset:** {dataset_name} (from baseline)
- **Config:** LR={lr}, Epochs={epochs}, Batch={batch_size} (from baseline)

### Algorithm Injection Point
- **Optimizer Location:** `{file}:{line}`
- **Current Optimizer:** `{optimizer_class}`
- **Injection Strategy:** {replacement|wrapper|hook}
- **Injection Complexity:** {simple|moderate|complex}

### Code Snippet (Current)
```python
{current_optimizer_code}
```

### Code Snippet (After Injection)
```python
{proposed_injection_code}
```

### Injection Feasibility Score: {score}/100

---

## Baseline 2: {repo_name}
...

## Baseline 3: {repo_name}
...
```

---

## 6.9 Update Checkpoint

Update `05_baseline_checkpoint.yaml`:

```yaml
current_step: 7
baselines:
  - rank: 1
    repo_name: "{name}"
    clone_path: "{path}"
    commit_hash: "{sha}"
    conda_env: "baseline-{name}"
    readme_summary: "{brief_summary}"
    baseline_environment:
      model: "{model_architecture}"
      dataset: "{dataset_name}"
      config: "{lr, epochs, batch_size}"
    injection_analysis:
      optimizer_location: "{file}:{line}"
      backward_location: "{file}:{line}"
      injection_strategy: "{replacement|wrapper|hook}"
      injection_complexity: "{simple|moderate|complex}"
      injection_feasibility_score: {score}
    status: "PROCEED|SKIP"
  - rank: 2
    ...
  - rank: 3
    ...
updated_at: "{timestamp}"
```

---

## 6.10 Generate 05_tasks.yaml

<critical>

Tasks are now stored in local `05_tasks.yaml` file (NOT created in Archon MCP).
This matches Phase 4's local task management pattern for consistency.

**FORBIDDEN:** `mcp__archon__manage_task(action="create")` for adaptation tasks
**REQUIRED:** Generate `05_tasks.yaml` with all tasks before proceeding to Step 7

**MODE B TASKS:** No data-adapter, config-override, or model-adapter tasks!
We use baseline's environment as-is. Only inject algorithm + metrics + results.
</critical>

### 6.10.1 Initialize Task File

Read template from `{tasks_template}` and create `{tasks_output_file}`:

```yaml
version: "1.0"
metadata:
  hypothesis_id: "{checkpoint.hypothesis_id}"
  main_hypothesis_id: "{checkpoint.main_hypothesis_id}"
  generated_at: "{ISO8601_timestamp}"
  baselines_count: {baselines_proceeding_count}
  mode: "B"
  mode_description: "Inject OUR algorithm into BASELINE's environment"
  total_tasks: {baselines_proceeding_count * 4}
  source_context:
    phase4_code_folder: "{hypothesis_folder}/code"
    code_analysis_file: "{baseline_folder}/code_analysis.md"
    checkpoint_file: "{baseline_folder}/05_baseline_checkpoint.yaml"
```

### 6.10.2 Generate Tasks for Each PROCEED Baseline

**FOR EACH baseline where status == "PROCEED":**

Generate **4 tasks** with the following structure (Mode B):

| # | Task Type | Priority | Description |
|---|-----------|----------|-------------|
| 1 | algorithm-injection | 100 | Inject OUR algorithm/optimizer into baseline's training loop |
| 2 | metric-injection | 95 | Inject psi computation and metric tracking |
| 3 | results-saver | 90 | Save results in standardized comparison format |
| 4 | training-script | 85 | Minimal modification to baseline's train.py |

**NOTE:** No config-override, data-adapter, or model-adapter tasks in Mode B!
We use baseline's environment (model, dataset, config) as-is.

**Task ID Format:** `B{rank}-{task_type}` (e.g., `B1-algorithm-injection`, `B2-metric-injection`)

### 6.10.3 Task Details Template

```yaml
tasks:
  - task_id: "B{rank}-algorithm-injection"
    baseline_rank: {rank}
    baseline_repo: "{repo_name}"
    task_type: "algorithm-injection"
    priority: 100
    status: "pending"
    description: "Inject our optimizer/algorithm into {repo_name}'s training loop"
    injection_strategy: "{replacement|wrapper|hook}"
    injection_point:
      file: "{file_path}"
      line: {line_number}
      current_code: "{current_optimizer_creation}"
    reference_files:
      our_algorithm: "{hypothesis_folder}/code/..."
      injection_guide: "{workflow_path}/_references/algorithm-injection.md"

  - task_id: "B{rank}-metric-injection"
    baseline_rank: {rank}
    baseline_repo: "{repo_name}"
    task_type: "metric-injection"
    priority: 95
    status: "pending"
    description: "Add psi computation and metric tracking to {repo_name}"
    injection_point:
      file: "{training_file}"
      after_backward: "{line_number}"
    reference_files:
      metrics_guide: "{workflow_path}/_references/adapter-metrics.md"

  - task_id: "B{rank}-results-saver"
    baseline_rank: {rank}
    baseline_repo: "{repo_name}"
    task_type: "results-saver"
    priority: 90
    status: "pending"
    description: "Add results saving in comparison format to {repo_name}"
    reference_files:
      results_guide: "{workflow_path}/_references/adapter-results.md"

  - task_id: "B{rank}-training-script"
    baseline_rank: {rank}
    baseline_repo: "{repo_name}"
    task_type: "training-script"
    priority: 85
    status: "pending"
    description: "Minimal modification to {repo_name}'s train.py for comparison"
    dependencies: ["B{rank}-algorithm-injection", "B{rank}-metric-injection", "B{rank}-results-saver"]
    reference_files:
      training_guide: "{workflow_path}/_references/adapter-training-script.md"
```

### 6.10.4 Calculate Budget Summary

```yaml
budget_summary:
  baselines_proceeding: {count}
  tasks_per_baseline: 4
  total_tasks: {count * 4}
  by_type:
    algorithm-injection: {count}
    metric-injection: {count}
    results-saver: {count}
    training-script: {count}
  by_status:
    pending: {total_tasks}
    doing: 0
    review: 0
    done: 0
    skipped: 0
```

### 6.10.5 Write Task File

Write `05_tasks.yaml` to `{baseline_folder}/05_tasks.yaml`.

**Verification:**
- File exists and is valid YAML
- `baselines` array has entries for all PROCEED baselines
- Each baseline has exactly **4 tasks** (Mode B)
- All tasks have `status: "pending"`
- `budget_summary.total_tasks` matches actual task count
- **No config-override, data-adapter, or model-adapter tasks exist**

---

## Step Completion Criteria

- [ ] **All 3 repositories cloned** (or fewer with graceful degradation)
- [ ] Conda environment created for **each baseline**
- [ ] **README.md read and analyzed** for each baseline
- [ ] Code analysis completed for **each baseline** (using Serena)
- [ ] **Injection point analysis** completed for **each baseline**
- [ ] **Injection strategy** determined for each baseline
- [ ] setup_log.md generated (includes all baselines)
- [ ] code_analysis.md generated (includes injection points for all baselines)
- [ ] Checkpoint updated with all baselines and injection analysis
- [ ] **05_tasks.yaml generated** with 4 tasks per PROCEED baseline

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN setup_log.md, code_analysis.md, **and 05_tasks.yaml** are generated for all baselines, and checkpoint is updated, will you then immediately load, read entire file, then execute `{workflow_path}/steps/step-07-adaptation-coding.md` to begin algorithm injection coding.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### ✅ SUCCESS:
- **All 3 repositories** cloned to baselines/ folder
- youra-baseline branch created for each
- **Conda environment created for each baseline**
- Dependencies installed for each baseline
- **README.md read and analyzed for each baseline**
- Serena MCP used to analyze **each baseline**
- **Algorithm injection points identified** for each baseline
- **Injection strategy determined** (replacement/wrapper/hook) for each
- **Baseline environments documented** (model, dataset, config from baseline)
- setup_log.md saved with **all baselines' clone and env details**
- code_analysis.md saved with **injection analysis for all baselines**
- Checkpoint updated with **baselines array and injection_analysis**
- **05_tasks.yaml generated** with 4 Mode B tasks per PROCEED baseline

### ❌ SYSTEM FAILURE:
- Cloning only 1 baseline when 3 are selected
- Not creating conda environment for each baseline
- **Not reading README.md for each baseline**
- Not using Serena MCP for analysis of all baselines
- **Not identifying algorithm injection points**
- **Not determining injection strategy**
- **Creating data-adapter or model-adapter tasks** (Mode B violation!)
- **Creating config-override tasks** (Mode B violation!)
- Not saving setup_log.md or code_analysis.md with all baselines
- Not updating checkpoint with injection_analysis
- **Creating Archon tasks instead of 05_tasks.yaml**
- **Not generating 05_tasks.yaml before proceeding to Step 7**

---

**Next Step:** Load and execute `step-07-adaptation-coding.md`
