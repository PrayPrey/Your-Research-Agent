---
name: 'step-03-architecture-agent'
description: 'Spawn Architecture Agent to design system architecture with Epic tasks'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning'
thisStepFile: '{workflow_path}/steps/step-03-architecture-agent.md'
nextStepFile: '{workflow_path}/steps/step-04-budget-allocation.md'
workflowFile: '{workflow_path}/workflow.md'

# Task References: N/A - Orchestration workflow using Task agents instead of A/P elicitation
---

# Step 3: Architecture Agent

**Progress: Step 3 of 10** | Next: Step 4 - Complexity Analysis

---

## STEP GOAL:

Spawn the Architecture Agent to design the system architecture including module structure, file organization, and Epic-level tasks with complexity scores. The agent uses Archon KB and Serena MCP for research-backed architecture decisions.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:
- 🛑 MUST use Task tool to spawn Architecture Agent
- 📖 Agent runs in INDEPENDENT context (main session stays clean)
- 🔧 Agent MUST use Archon MCP (KB search)
- 🔧 Serena MCP usage is CONDITIONAL:
  - **Base Hypothesis exists** → MANDATORY (verify actual code)
  - **Existing codebase** → MANDATORY (discover patterns)
  - **Green-field** → OPTIONAL (no code to analyze)

---

## EXECUTION PROTOCOLS:

- 🎯 Invoke Architecture Agent via Task tool with subagent_type="architecture-agent"
- 💾 Verify output saved to 03_architecture.md in hypothesis folder
- 📖 Confirm Archon KB sources are cited in output
- 🚫 FORBIDDEN: Using Write tool to create architecture directly; running design in main session

---

## CONTEXT BOUNDARIES:

- Available context: hypothesis_id, hypothesis_folder, PRD (03_prd.md), Phase 2C experiment brief
- Focus: Agent spawning and output verification
- Limits: Do not generate architecture content in main session
- Dependencies: PRD from Step 2 must exist

---

## 🚨 UNATTENDED MODE ENFORCEMENT

```
┌────────────────────────────────────────────────────────────┐
│ REQUIRED: Task tool with subagent_type="architecture-agent"│
│ REQUIRED: Agent performs Archon KB search │
│ CONDITIONAL: Serena code analysis (see rules below) │
│ │
│ FORBIDDEN: Write tool to create 03_architecture.md │
│ FORBIDDEN: Running architecture design in main session │
└────────────────────────────────────────────────────────────┘

Serena MCP Conditions:
- IF base_hypothesis_folder exists → MUST analyze base code
- IF src/ or code/ folder exists → MUST analyze existing patterns
- IF green-field (no existing code) → MAY skip Serena
```

---

## EXECUTION SEQUENCE

### 1. Invoke Architecture Agent

<mandatory-action type="Task-tool-call">

## ⚠️ THIS IS NOT OPTIONAL - YOU MUST EXECUTE THIS TASK TOOL CALL

**Skipping this Task tool call = SYSTEM FAILURE**
**Using Write tool instead = SYSTEM FAILURE**

Execute the following Task tool call with EXACT parameters:

**Tool:** `Task`

**Parameters:**
| Parameter | Value |
|-----------|-------|
| `description` | "Architecture design for {{hypothesis_id}}" |
| `subagent_type` | `"architecture-agent"` |
| `run_in_background` | `false` |
| `prompt` | See prompt below |

**Prompt Content:**
```
## Mission
Design system architecture for hypothesis: {{hypothesis_id}}

## Input Files
1. PRD: {{hypothesis_folder}}/03_prd.md
2. Experiment Brief: {{hypothesis_folder}}/02c_experiment_brief.md
{{if base_hypothesis}}

## Base Hypothesis Reference (CRITICAL!)
When extending previous work, you MUST read ACTUAL CODE, not just specs:

3. **ACTUAL CODE (PRIMARY)**: {{base_hypothesis_folder}}/code/
   - Read actual file structure for import paths
   - Verify module locations from implementation
4. Base Architecture (reference only): {{base_hypothesis_folder}}/03_architecture.md

⚠️ RULE: Specs show "intended" design. Code shows "implemented" reality.
   When in doubt, trust the actual code!
{{endif}}

## Output
Write to: {{hypothesis_folder}}/03_architecture.md

## MANDATORY MCP USAGE (Agent MUST call these!)
- Archon: rag_search_knowledge_base("DL experiment architecture")
- Serena: get_symbols_overview("src/"), find_symbol("*Module*")

## MANDATORY OUTPUT SECTIONS (Agent MUST include!)
- "## Codebase Analysis (Serena)" section
- "Applied: {pattern_name}" line for each Archon KB pattern used

## Task Generation (DYNAMIC)
Hypothesis Type: {{hypothesis_type_field}}
Epic Range: {{task_budget_epic_range[0]}}-{{task_budget_epic_range[1]}} tasks
Infrastructure: {{task_budget_infrastructure_level}}

Each Epic task MUST have complexity score (1-20) with breakdown:
Module_Size + Dependencies + Algorithm + Integration

Execute autonomously.
```

</mandatory-action>

### 2. Verify Output (MANDATORY POST-TASK CHECK)

<output-validation type="auto-check">

**Read `{{hypothesis_folder}}/03_architecture.md` and verify:**

| Check | Required Content | If Missing |
|-------|------------------|------------|
| ✅ | `## Codebase Analysis (Serena)` section | **DELETE FILE & RE-INVOKE AGENT** |
| ✅ | `Applied:` line (at least 1) | **DELETE FILE & RE-INVOKE AGENT** |
| ✅ | Module structure section | Warn but continue |
| ✅ | File organization section | Warn but continue |
| ✅ | Proposed Tasks with complexity scores | **FAIL - RE-INVOKE AGENT** |
{{if base_hypothesis}}
| ✅ | External Dependencies section | **DELETE FILE & RE-INVOKE AGENT** |
| ✅ | Import paths from actual code | **DELETE FILE & RE-INVOKE AGENT** |
{{endif}}

**Validation Logic:**
```python
content = Read("{{hypothesis_folder}}/03_architecture.md")

# CRITICAL CHECKS - Missing = Agent bypass detected
IF "## Codebase Analysis" NOT in content:
    Delete("{{hypothesis_folder}}/03_architecture.md")
    GOTO "### 1. Invoke Architecture Agent" # RE-INVOKE!

IF "Applied:" NOT in content:
    Delete("{{hypothesis_folder}}/03_architecture.md")
    GOTO "### 1. Invoke Architecture Agent" # RE-INVOKE!

# Continue to next step only if validation passes
```

</output-validation>

### 3. Display Summary

```
✓ Architecture Agent Complete

Output: {{hypothesis_folder}}/03_architecture.md
Epic Tasks: {{task_count}}
Complexity Distribution: Very High/High/Medium/Low counts
```

### 4. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

**UNATTENDED Mode**: Auto-progress to Step 4
**Interactive Mode**: Display menu:

"**Select an Option:** [R] Review Architecture Summary [C] Continue [X] Exit"

#### Menu Handling Logic:
- IF R: Display architecture module summary and Epic task count, return to menu
- IF C: Load next step
- IF X: Exit workflow gracefully

#### EXECUTION RULES:
- ALWAYS halt and wait for user input after presenting menu (Interactive mode)
- ONLY proceed to next step when user selects 'C' or UNATTENDED mode is active
- After other menu items execution, return to this menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN Architecture Agent completes AND 03_architecture.md exists in hypothesis folder AND Epic tasks are within budget range with complexity scores, proceed to load and execute `{workflow_path}/steps/step-04-budget-allocation.md` for budget allocation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Task tool used with subagent_type="architecture-agent"
- Agent used Archon MCP for KB research
- Serena MCP used appropriately:
  - IF base_hypothesis → Base code analyzed with Serena
  - IF existing codebase → Patterns discovered with Serena
  - IF green-field → Serena skipped (acceptable)
- 03_architecture.md created in hypothesis folder
- Epic tasks within budget range with complexity scores
- Archon KB sources cited in output
- "Codebase Analysis" section included (even if green-field)
{{if base_hypothesis}}
- External Dependencies section included with verified import paths
- Import paths verified from actual code (not specs)
{{endif}}

### ❌ SYSTEM FAILURE:
- Not using Task tool to spawn agent
- Agent skipping Archon MCP usage
- Missing complexity scores on Epic tasks
- Tasks outside epic range for hypothesis type
- Using Write tool to create architecture directly
- **Skipping Serena when base_hypothesis exists** (MUST verify actual code)
- **Skipping Serena when existing codebase exists** (MUST discover patterns)
{{if base_hypothesis}}
- Import paths copied from specs instead of actual code
- Missing External Dependencies section
{{endif}}

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
