---
name: 'step-04-evaluate'
description: 'Evaluate candidate repositories for algorithm injection suitability (Mode B)'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'

# File References
thisStepFile: '{workflow_path}/steps/step-04-evaluate.md'
prevStepFile: '{workflow_path}/steps/step-03-search.md'
nextStepFile: '{workflow_path}/steps/step-05-select.md'
workflowFile: '{workflow_path}/workflow.md'
checkpointFile: '{baseline_folder}/05_baseline_checkpoint.yaml'

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 4: Evaluate Candidate Repositories (Mode B)

## STEP GOAL:

Score each candidate repository for **algorithm injection suitability**. In Mode B, we evaluate whether we can inject OUR algorithm into the BASELINE's environment (model, dataset, config).

**Key Question:** "Can we inject our optimizer/algorithm into this baseline's training loop while preserving their model, dataset, and config?"

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus on evaluating algorithm injection feasibility
- 📖 **MUST read README.md** for each candidate
- 🚫 FORBIDDEN to select or clone repositories (that's Step 5-6)
- 💬 Use Serena MCP for deep code analysis
- 📊 Calculate scores using defined weights: **Suitability 40%, Quality 30%, Injection Feasibility 30%**

## EXECUTION PROTOCOLS:

- 🎯 Clone candidates for analysis (shallow clone to temp)
- 📖 **MANDATORY: Read README.md for each candidate**
- 💾 Generate evaluation_matrix.md with scores
- 📖 Use Serena MCP for pattern search
- 🚫 FORBIDDEN to skip README analysis

## CONTEXT BOUNDARIES:

- Available context: repo_candidates.md, comparison_plan.md
- Focus: Evaluation and scoring only
- Limits: Do not make final selection yet
- Dependencies: Step 3 must be completed with candidates

---

---

## 4.1 Load Candidates

Load candidates from `repo_candidates.md` and evaluation criteria from checkpoint.

---

## 4.2 Deep Repository Analysis

For each candidate, perform detailed analysis using Serena MCP.

### Clone for Analysis

Clone each repository (shallow clone) to a temporary folder for analysis.

### 4.2.1 README.md Analysis (MANDATORY)

<critical>
**Mode B REQUIRES thorough understanding of baseline's environment.**
You MUST read and analyze README.md before any code analysis.
</critical>

**Read README.md:**

```python
readme_path = f"{repo_clone_path}/README.md"
Read(readme_path) # FULL READ, no limit
```

**Extract from README:**

| Information | Why Needed |
|-------------|------------|
| Model architecture description | Understand what model we'll use |
| Dataset requirements | Understand what data we'll use |
| Training procedure | Understand where to inject algorithm |
| Expected results/benchmarks | Baseline for comparison |
| Dependencies/environment | Setup requirements |

**Record README analysis:**

```yaml
readme_analysis:
  model_description: "{extracted}"
  dataset_info: "{extracted}"
  training_procedure: "{extracted}"
  expected_results: "{extracted}"
  dependencies: "{extracted}"
  readme_quality: "comprehensive|adequate|minimal|none"
```

### 4.2.2 Serena Analysis Steps

1. **Activate project**: `mcp__serena__activate_project`
2. **Find training files**: `mcp__serena__find_file` (train*.py)
3. **Find model files**: `mcp__serena__find_file` (model*.py)
4. **Find data files**: `mcp__serena__find_file` (*data*.py)

### 4.2.2a Extract All Available Datasets

<critical>
This information is used by Step 5 to compute dataset overlap across baseline candidates.
Baselines that share common datasets get a selection bonus.
</critical>

**Search README for dataset mentions:**
- Look for dataset names (CIFAR10, MNIST, ImageNet, SVHN, etc.)
- Look for dataset sections ("Datasets", "Benchmarks", "Supported datasets")
- Note which datasets have explicit loading code or configs

**Search code for dataset patterns:**

```python
mcp__serena__search_for_pattern(
    substring_pattern="CIFAR|MNIST|ImageNet|SVHN|FashionMNIST|datasets\\.load|torchvision\\.datasets",
    relative_path="{repo_clone_path}",
    paths_include_glob="*.py",
    context_lines_before=1,
    context_lines_after=2
)
```

**Record datasets_available:**

```yaml
datasets_available:
  - name: "CIFAR10"
    source: "torchvision" # torchvision | huggingface | custom
    evidence: "README + code" # Where this dataset was found
  - name: "CIFAR100"
    source: "torchvision"
    evidence: "code only"
  - name: "MNIST"
    source: "torchvision"
    evidence: "README + code"
```

**Priority:** Datasets with both README documentation AND code support are more reliable than code-only mentions.

### 4.2.3 Pattern Search

| Pattern | Purpose |
|---------|---------|
| "SGD\|torch.optim.SGD\|Adam\|optim\\." | Find optimizer creation location |
| "backward\(\)\|loss\\.backward" | Find gradient computation location |
| "seed\|random_state\|manual_seed" | Check seed control |
| "learning_rate\|--lr\|lr=" | Check LR configuration |

### 4.2.4 Algorithm Injection Point Analysis

<critical>
**Mode B Critical:** Identify where to inject our algorithm.
</critical>

**Find optimizer creation location:**

```bash
mcp__serena__search_for_pattern(
    substring_pattern="optim\\.SGD\\(|optim\\.Adam\\(|torch\\.optim\\.",
    relative_path="{repo_clone_path}",
    paths_include_glob="*.py",
    context_lines_before=2,
    context_lines_after=3
)
```

**Analyze optimizer interface:**

| Check | Method |
|-------|--------|
| Standard PyTorch optimizer? | Look for `optim.XXX(model.parameters(), lr=...)` |
| Custom optimizer? | Look for custom Optimizer class |
| Optimizer wrapper? | Look for scheduler or wrapper patterns |
| Multiple optimizers? | Check if GAN/multi-model setup |

**Record injection points:**

```yaml
injection_analysis:
  optimizer_location:
    file: "{file_path}"
    line: {line_number}
    pattern: "{optimizer_type}"
    interface: "standard|custom|wrapped"
  backward_location:
    file: "{file_path}"
    line: {line_number}
  injection_complexity: "simple|moderate|complex"
  injection_strategy: "replacement|wrapper|hook"
```

### 4.2.5 Baseline Environment Documentation

**Document the baseline's environment that we will USE:**

```yaml
baseline_environment:
  model:
    architecture: "{model_class_name}"
    source_file: "{file_path}"
    input_shape: "{if identifiable}"
  dataset:
    name: "{primary_dataset_name}"
    loading_code: "{code_snippet}"
    source: "{torchvision|huggingface|custom}"
  datasets_available:
    - name: "{dataset_1}"
      source: "{torchvision|huggingface|custom}"
      evidence: "{README + code | code only | README only}"
    - name: "{dataset_2}"
      source: "{torchvision|huggingface|custom}"
      evidence: "{README + code | code only | README only}"
  config:
    lr: "{default_lr}"
    batch_size: "{default_batch_size}"
    epochs: "{default_epochs}"
    other: "{any_other_relevant_config}"
```

---

## 4.3 Score Calculation

### Suitability Score (40%)

Score based on whether baseline's environment is suitable for our algorithm:

| Factor | Condition | Points |
|--------|-----------|--------|
| Standard optimizer | Uses torch.optim.* | High |
| Gradient access | Has loss.backward() | High |
| Seed control | Has seed setting | Medium |
| LR configurable | Can change LR via args | Medium |
| Model documented | README explains model | Medium |

### Quality Score (30%)

| Factor | Points |
|--------|--------|
| Stars ≥ 1000 | 25 |
| Stars ≥ 500 | 20 |
| Stars ≥ 100 | 15 |
| Stars ≥ 50 | 10 |
| Has comprehensive README | 25 |
| Has tests | 25 |
| Updated < 30 days | 25 |
| Updated < 180 days | 20 |
| Updated < 365 days | 15 |

### Injection Feasibility Score (30%)

<critical>
**Mode B Focus:** How easy is it to inject our algorithm?
</critical>

| Factor | Points |
|--------|--------|
| Standard optimizer interface | 30 |
| Single optimizer (not multi-model) | 25 |
| Clear training loop | 20 |
| Small codebase (< 10 files) | 15 |
| Medium codebase (< 25 files) | 10 |
| Has config file | 10 |

**Injection Complexity Penalty:**

| Complexity | Penalty |
|------------|---------|
| Simple (standard optimizer, clear loop) | 0 |
| Moderate (custom optimizer, but standard interface) | -10 |
| Complex (multiple optimizers, custom training) | -25 |

### Final Score

```
Final = (Suitability × 0.4) + (Quality × 0.3) + (Injection Feasibility × 0.3)
```

---

## 4.4 Generate evaluation_matrix.md

Create `{baseline_folder}/evaluation_matrix.md`:

```markdown
# Evaluation Matrix (Mode B - Algorithm Injection)

## Evaluation Summary
- **Total Candidates:** {count}
- **Evaluation Date:** {timestamp}
- **Scoring Weights:** Suitability 40%, Quality 30%, Injection Feasibility 30%
- **Mode:** B (Inject OUR algorithm into BASELINE's environment)

---

## Scoring Legend

| Score Range | Rating |
|-------------|--------|
| 0.8 - 1.0 | Excellent |
| 0.6 - 0.8 | Good |
| 0.4 - 0.6 | Fair |
| 0.2 - 0.4 | Poor |
| 0.0 - 0.2 | Unsuitable |

---

## Evaluation Results (Ranked)

| Rank | Repository | Suitability | Quality | Injection | **Final** |
|------|------------|-------------|---------|-----------|-----------|
| 1 | {repo} | {score} | {score} | {score} | **{score}** |
...

---

## Detailed Analysis

### 1. {repo_name} (Score: {final})

**URL:** {url}

#### README Summary
{Brief summary of what README says about model, dataset, training}

#### Baseline Environment (What We Will Use)
- **Model:** {model_architecture}
- **Dataset:** {dataset_name}
- **Config:** LR={lr}, Epochs={epochs}, Batch={batch_size}

#### Suitability Analysis
- Standard Optimizer: {yes/no} ({optimizer_type})
- Gradient Access: {yes/no}
- Seed Control: {yes/no}
- LR Configurable: {yes/no}

#### Quality Analysis
- Stars: {count}
- Has Tests: {yes/no}
- Last Updated: {date}
- README Quality: {comprehensive/adequate/minimal}

#### Algorithm Injection Analysis
- **Injection Point:** `{file}:{line}`
- **Injection Strategy:** {replacement/wrapper/hook}
- **Injection Complexity:** {simple/moderate/complex}
- **Optimizer Interface:** {standard/custom/wrapped}

#### Injection Code Preview
```python
# Current (baseline):
{current_optimizer_code}

# After injection (ours):
{proposed_injection_code}
```

---

## Recommendation

**Top Candidate:** {repo_name} (Score: {score})

**Rationale:**
{explanation focusing on injection feasibility}

**Baseline Environment We Will Use:**
- Model: {model}
- Dataset: {dataset}
- Config: {config}
```

---

## 4.5 Update Checkpoint

```yaml
current_step: 5
evaluation:
  candidates_evaluated: {count}
  baseline_environments:
    - repo: "{repo_name}"
      model: "{model_architecture}"
      dataset: "{primary_dataset_name}"
      datasets_available: ["{dataset_1}", "{dataset_2}", "{dataset_3}"] # 
      injection_point: "{file}:{line}"
      injection_complexity: "{simple|moderate|complex}"
      injection_strategy: "{replacement|wrapper|hook}"
    - repo: "{repo_name_2}"
      model: "{model_architecture}"
      dataset: "{primary_dataset_name}"
      datasets_available: ["{dataset_1}", "{dataset_2}"] # 
      injection_point: "{file}:{line}"
      injection_complexity: "{simple|moderate|complex}"
      injection_strategy: "{replacement|wrapper|hook}"
updated_at: "{timestamp}"
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Clone fails | Skip candidate, note as unverifiable |
| README not found | Lower quality score, proceed with code analysis |
| Serena analysis fails | Use basic file checks only |
| All candidates score < 0.3 | Expand search in Step 3 |
| No clear injection point | Mark as complex, lower injection score |

---

## Step Completion Criteria

- [ ] All candidates evaluated
- [ ] **README.md analyzed for each candidate**
- [ ] **Injection points identified for each candidate**
- [ ] Scores calculated
- [ ] evaluation_matrix.md saved
- [ ] Checkpoint updated

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN evaluation_matrix.md is saved with all candidates scored (including injection analysis) and checkpoint is updated, will you then immediately load, read entire file, then execute `{workflow_path}/steps/step-05-select.md` to make final selection.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### ✅ SUCCESS:
- All candidates from repo_candidates.md evaluated
- **README.md read and analyzed for EACH candidate**
- Serena MCP used for deep code analysis
- Pattern searches executed for optimizer, backward(), seed
- **Injection points identified for each repository**
- **Injection strategy determined (replacement/wrapper/hook)**
- **Baseline environments documented (model, dataset, config)**
- Suitability scores calculated (40% weight)
- Quality scores calculated (30% weight)
- **Injection Feasibility scores calculated (30% weight)**
- Final weighted scores computed
- evaluation_matrix.md saved with **injection analysis**
- Checkpoint updated with **baseline_environments**

### ❌ SYSTEM FAILURE:
- **Not reading README.md for each candidate**
- Generating scores without actual code analysis
- **Not identifying injection points**
- **Not documenting baseline environments (model, dataset, config)**
- Skipping suitability analysis
- Using wrong score weights
- Not using Serena MCP for analysis
- Not saving evaluation_matrix.md
- Not updating checkpoint

---

**Next Step:** Load and execute `step-05-select.md`
