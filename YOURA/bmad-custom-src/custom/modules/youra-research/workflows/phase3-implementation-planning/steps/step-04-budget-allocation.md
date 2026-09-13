---
name: 'step-04-budget-allocation'
description: 'Analyze Epic task complexity and allocate subtask budgets to Logic/Config agents'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning'
thisStepFile: '{workflow_path}/steps/step-04-budget-allocation.md'
nextStepFile: '{workflow_path}/steps/step-05-parallel-agents.md'
workflowFile: '{workflow_path}/workflow.md'

# Task References: N/A - Orchestration workflow using Task agents instead of A/P elicitation
---

# Step 4: Subtask Budget Allocation

**Progress: Step 4 of 10** | Next: Step 5 - Parallel Agents

---

## STEP GOAL:

Analyze the Epic tasks from Architecture output and allocate subtask budgets to Logic and Configuration agents. This step ensures the total task count stays within budget (LIGHT=15, FULL=30) by prioritizing high-complexity modules for subtask decomposition.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:
- 🛑 MUST read Architecture output to extract tasks
- 📊 Calculate subtask budget based on complexity
- 🎯 Total budget: **{{task_budget_total_max}}** tasks ({{task_budget_tier}} tier: LIGHT=15, FULL=30)

---

## EXECUTION PROTOCOLS:

- 🎯 Parse 03_architecture.md to extract Epic tasks and complexity scores
- 💾 Calculate remaining budget after Epic tasks
- 📖 Allocate subtasks prioritizing highest complexity first
- 🚫 FORBIDDEN: Exceeding total task budget; allocating to low-complexity tasks first

---

## CONTEXT BOUNDARIES:

- Available context: hypothesis_id, hypothesis_folder, task_budget_total_max, 03_architecture.md
- Focus: Budget calculation and allocation to agents
- Limits: No task creation yet; allocation planning only
- Dependencies: Architecture from Step 3 must exist with complexity scores

---

## ALLOCATION SEQUENCE

### 1. Read Architecture Output

Read `{{hypothesis_folder}}/03_architecture.md` and extract:
- Epic task list with complexity scores

### 2. Calculate Subtask Budget

```python
remaining = task_budget_total_max - epic_count

# Subtask allocation by complexity (highest priority first)
Very High (18-20): 4-5 subtasks
High (14-17): 3-4 subtasks
Medium (9-13): 1-2 subtasks
Low (4-8): 0 subtasks
```

**Sort by complexity descending**, allocate until budget exhausted.

### 3. Split Between Agents

| Agent | Focus | Tasks |
|-------|-------|-------|
| **Logic Agent** | APIs, tensor shapes, pseudo-code | High complexity tasks |
| **Config Agent** | Config schemas, hyperparameters | Medium complexity tasks |

### 4. Display Allocation

```
Subtask Budget Allocation
================================================================
| Task ID | Name | Complexity | Subtasks |
|---------|------|------------|----------|
| A-3 | ModelModule | 18 (VH) | 5 |
| A-4 | Aggregation | 16 (H) | 4 |
| ... | ... | ... | ... |

Budget Summary:
- Total Budget: {{task_budget_total_max}}
- Epic Tasks: {{epic_count}}
- Subtasks: {{subtask_total}}
- Total: {{total}} / {{task_budget_total_max}}

Logic Agent: {{logic_budget}} subtasks
Config Agent: {{config_budget}} subtasks
================================================================
```

### 5. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

**UNATTENDED Mode**: Auto-progress to Step 5
**Interactive Mode**: Display menu:

"**Select an Option:** [R] Review Allocation [C] Continue [X] Exit"

#### Menu Handling Logic:
- IF R: Display allocation table with budget summary, return to menu
- IF C: Load next step
- IF X: Exit workflow gracefully

#### EXECUTION RULES:
- ALWAYS halt and wait for user input after presenting menu (Interactive mode)
- ONLY proceed to next step when user selects 'C' or UNATTENDED mode is active
- After other menu items execution, return to this menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN subtask budgets are calculated AND total tasks stay within budget AND allocation is split between Logic and Config agents, proceed to load and execute `{workflow_path}/steps/step-05-parallel-agents.md` for parallel agent spawning.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Architecture output parsed successfully
- Total tasks ≤ {{task_budget_total_max}}
- High complexity modules prioritized for subtasks
- Allocation split between Logic and Config agents

### ❌ SYSTEM FAILURE:
- Exceeding task budget
- Not prioritizing high complexity modules
- Allocating subtasks to low complexity modules first
- Not reading 03_architecture.md

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
