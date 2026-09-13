---
name: 'step-06-complexity-assessment'
description: 'Calculate final complexity score and validate task counts'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning'
thisStepFile: '{workflow_path}/steps/step-06-complexity-assessment.md'
nextStepFile: '{workflow_path}/steps/step-07-verify-documents.md'
workflowFile: '{workflow_path}/workflow.md'

# Task References: N/A - Orchestration workflow using Task agents instead of A/P elicitation
---

# Step 6: Overall Complexity Assessment

**Progress: Step 6 of 10** | Next: Step 7 - Verify Documents

---

## STEP GOAL:

Calculate the final overall complexity score using a structured algorithm analyzing PRD and Architecture. Validate that total task count stays within budget, applying budget rebalancing (subtask exclusion) if over budget.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:
- 🛑 NEVER use arbitrary scores - calculate complexity properly
- 🔄 Follow the scoring algorithm exactly
- ✅ ALWAYS read PRD + Architecture thoroughly

---

## EXECUTION PROTOCOLS:

- 🎯 Calculate complexity using the defined 5-factor algorithm
- 💾 Apply incremental adjustment if applicable
- 📖 Validate total task count against budget
- 🚫 FORBIDDEN: Guessing complexity; exceeding budget without rebalancing

---

## CONTEXT BOUNDARIES:

- Available context: hypothesis_id, hypothesis_folder, all 03_*.md files, task_budget_total_max
- Focus: Complexity scoring and budget validation
- Limits: Documents remain unchanged; only calculate and validate
- Dependencies: All agent outputs (03_architecture.md, 03_logic.md, 03_config.md) must exist

---

## COMPLEXITY CALCULATION

### 1. Score Components (0-30 points total)

Read PRD and Architecture, then calculate:

| Factor | Score Range | Criteria |
|--------|-------------|----------|
| **Modules** | 2-5 | ≤3: 2pts, ≤6: 4pts, >6: 5pts |
| **Integration** | 2-5 | ≤2 points: 2pts, ≤5: 4pts, >5: 5pts |
| **Novel Components** | 0-5 | All exist: 0, 1-2 new: 3pts, 3+: 5pts |
| **Testing** | 2-5 | Unit only: 2pts, +Integration: 4pts, +E2E: 5pts |
| **Dependencies** | 0-3 | 0 new: 0pts, ≤2: 2pts, >2: 3pts |

**DL Experiment Defaults**: novel_score=4, deps_score=1

### 2. Incremental Adjustment (If Applicable)

```python
if hypothesis_type == "INCREMENTAL":
    reuse_adjustment = -6 if reuse >= 70% else -4
    integration_penalty = +2 if integration >= 4 else +1
    adjusted_score = total_score + reuse_adjustment + integration_penalty
```

### 3. Determine Level (2-Tier Alignment)

| Score | Level | Recommended Tier |
|-------|-------|------------------|
| 0-15 | Simple/Moderate | LIGHT (15 tasks max) |
| 16+ | Complex | FULL (30 tasks max) |

**Tier Validation:**
- If `{{task_budget_tier}}` == LIGHT and score > 15 → Warning: Consider upgrading to FULL tier
- If `{{task_budget_tier}}` == FULL and score ≤ 15 → OK (FULL can handle simpler projects)

### 4. Budget Rebalancing (If Over Budget)

**Only execute if `total > task_budget_total_max`:**

#### 4.1 Calculate Excess

```python
excess = total - task_budget_total_max
# e.g., 18 tasks with LIGHT budget (15) → excess = 3
```

#### 4.2 Build Subtask Priority List

Read `03_logic.md` and `03_config.md`, extract all subtasks with their parent Epic complexity:

```python
all_subtasks = []

# From 03_logic.md
for subtask in logic_subtasks:
    all_subtasks.append({
        "id": subtask.id,
        "title": subtask.title,
        "parent_epic": subtask.parent_epic,
        "parent_complexity": get_epic_complexity(subtask.parent_epic),
        "source": "logic"
    })

# From 03_config.md
for subtask in config_subtasks:
    all_subtasks.append({
        "id": subtask.id,
        "title": subtask.title,
        "parent_epic": subtask.parent_epic,
        "parent_complexity": get_epic_complexity(subtask.parent_epic),
        "source": "config"
    })

# Sort by complexity ASCENDING (lowest complexity first = remove first)
all_subtasks.sort(key=lambda x: x["parent_complexity"])
```

#### 4.3 Select Subtasks to Exclude

```python
exclude_list = []
for subtask in all_subtasks:
    if len(exclude_list) >= excess:
        break
    exclude_list.append(subtask)

# Store for Step 9
{{excluded_subtasks}} = exclude_list
```

#### 4.4 Store Exclusion List

Store `{{excluded_subtasks}}` for use in Step 9:

```yaml
# In-memory or passed to Step 9
excluded_subtasks:
  - id: "L-2-3"
    reason: "Budget rebalancing - lowest complexity"
  - id: "C-4-1"
    reason: "Budget rebalancing - lowest complexity"
```

### 5. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

**UNATTENDED Mode**: Auto-progress to Step 7
**Interactive Mode**: Display menu:

"**Select an Option:** [R] Review Complexity Breakdown [C] Continue [X] Exit"

#### Menu Handling Logic:
- IF R: Display complexity breakdown and budget status, return to menu
- IF C: Load next step
- IF X: Exit workflow gracefully

#### EXECUTION RULES:
- ALWAYS halt and wait for user input after presenting menu (Interactive mode)
- ONLY proceed to next step when user selects 'C' or UNATTENDED mode is active
- After other menu items execution, return to this menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN complexity is calculated AND task count is validated (with rebalancing if over budget) AND exclusion list is stored if applicable, proceed to load and execute `{workflow_path}/steps/step-07-verify-documents.md` for document verification.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- PRD + Architecture analyzed thoroughly
- Complexity score calculated using algorithm
- Complexity level determined correctly
- Task count validated against budget
- Budget rebalancing applied if over budget

### ❌ SYSTEM FAILURE:
- Guessing complexity without algorithm
- Not providing factor breakdown
- Exceeding {{task_budget_total_max}} task maximum without rebalancing
- Skipping incremental adjustment for incremental hypotheses

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
