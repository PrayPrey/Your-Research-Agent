---
name: 'step-05-parallel-agents'
description: 'Spawn Logic and Configuration agents in parallel'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning'
thisStepFile: '{workflow_path}/steps/step-05-parallel-agents.md'
nextStepFile: '{workflow_path}/steps/step-06-complexity-assessment.md'
workflowFile: '{workflow_path}/workflow.md'

# Task References: N/A - Orchestration workflow using Task agents instead of A/P elicitation
---

# Step 5: Parallel Logic & Configuration Agents

**Progress: Step 5 of 10** | Next: Step 6 - Overall Complexity

---

## STEP GOAL:

Spawn Logic Agent and Configuration Agent in parallel to generate implementation details. Logic Agent produces API signatures, tensor shapes, and algorithms (03_logic.md). Config Agent produces YAML schemas, dataclasses, and hyperparameter defaults (03_config.md). Both must complete before proceeding.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:
- 🛑 MUST spawn BOTH agents in PARALLEL (single message, multiple Task calls)
- 📖 Each agent runs in INDEPENDENT context
- 🔧 Both agents MUST use Archon MCP (KB search)
- 🔧 Serena MCP usage is CONDITIONAL for both agents:
  - **Base Hypothesis exists** → MANDATORY (verify actual APIs/configs)
  - **Existing codebase** → MANDATORY (discover patterns)
  - **Green-field** → OPTIONAL (no code to analyze)

---

## EXECUTION PROTOCOLS:

- 🎯 Invoke BOTH agents in a SINGLE message with multiple Task calls
- 💾 Wait for both agents to complete before verifying outputs
- 📖 Confirm both outputs cite Archon KB sources
- 🚫 FORBIDDEN: Spawning agents sequentially; using Write tool to create outputs directly

---

## CONTEXT BOUNDARIES:

- Available context: hypothesis_id, hypothesis_folder, logic_budget, config_budget, 03_architecture.md, 03_prd.md
- Focus: Parallel agent spawning and output verification
- Limits: Do not generate Logic or Config content in main session
- Dependencies: Budget allocation from Step 4 required

---

## 🚨 UNATTENDED MODE ENFORCEMENT

```
┌────────────────────────────────────────────────────────────┐
│ REQUIRED: subagent_type="logic-agent" AND │
│ subagent_type="configuration-agent" │
│ REQUIRED: SINGLE message with BOTH Task calls (parallel) │
│ REQUIRED: Archon KB search for both agents │
│ CONDITIONAL: Serena code analysis (see rules below) │
│ │
│ FORBIDDEN: Write tool to create 03_logic.md directly │
│ FORBIDDEN: Write tool to create 03_config.md directly │
│ FORBIDDEN: Spawning agents sequentially │
└────────────────────────────────────────────────────────────┘

Serena MCP Conditions (applies to BOTH agents):
- IF base_hypothesis_folder exists → MUST analyze base code
- IF src/ or code/ folder exists → MUST analyze existing patterns
- IF green-field (no existing code) → MAY skip Serena
```

---

## EXECUTION SEQUENCE

### 1. Invoke BOTH Agents in Parallel

<mandatory-action type="parallel-Task-tool-calls">

## ⚠️ THIS IS NOT OPTIONAL - YOU MUST EXECUTE BOTH TASK TOOL CALLS IN A SINGLE MESSAGE

**Skipping these Task tool calls = SYSTEM FAILURE**
**Using Write tool instead = SYSTEM FAILURE**
**Executing sequentially instead of parallel = SYSTEM FAILURE**

Execute BOTH of the following Task tool calls in a **SINGLE MESSAGE**:

---

### Task 1: Logic Agent

**Tool:** `Task`

**Parameters:**
| Parameter | Value |
|-----------|-------|
| `description` | "Logic design for {{hypothesis_id}}" |
| `subagent_type` | `"logic-agent"` |
| `run_in_background` | `true` |
| `prompt` | See prompt below |

**Prompt Content:**
```
Mission: Design APIs, tensor shapes, pseudo-code

Input: 03_architecture.md, 03_prd.md
Output: {{hypothesis_folder}}/03_logic.md
Budget: {{logic_budget}} subtasks
{{if base_hypothesis}}

## Base Hypothesis Reference (CRITICAL!)
When calling methods from previous hypothesis, you MUST read ACTUAL CODE:

**ACTUAL CODE (PRIMARY)**: {{base_hypothesis_folder}}/code/
- Read actual method definitions for parameter names and types
- Verify return types from implementation

Base Logic (reference only): {{base_hypothesis_folder}}/03_logic.md

⚠️ RULE: Specs may say `forward(x, use_graph=True)` but code uses `forward(x, use_conv=True)`.
   Always verify parameter names from actual code!

Include "External Dependencies API" section with verified signatures.
{{endif}}

## MANDATORY MCP USAGE (Agent MUST call these!)
- Archon: rag_search_knowledge_base("DL API design patterns")
- Serena: find_symbol, get_symbols_overview

## MANDATORY OUTPUT SECTIONS (Agent MUST include!)
- "## Codebase Analysis (Serena)" section
- "Applied: {pattern_name}" line for each Archon KB pattern used
```

---

### Task 2: Configuration Agent (SAME MESSAGE!)

**Tool:** `Task`

**Parameters:**
| Parameter | Value |
|-----------|-------|
| `description` | "Config design for {{hypothesis_id}}" |
| `subagent_type` | `"configuration-agent"` |
| `run_in_background` | `true` |
| `prompt` | See prompt below |

**Prompt Content:**
```
Mission: Design config schemas, experiment settings

Input: 03_architecture.md, 03_prd.md
Output: {{hypothesis_folder}}/03_config.md
Budget: {{config_budget}} subtasks
{{if base_hypothesis}}

## Base Hypothesis Reference (CRITICAL!)
When extending configurations from previous hypothesis, you MUST read ACTUAL CODE:

**ACTUAL CODE (PRIMARY)**: {{base_hypothesis_folder}}/code/config*.py
- Read actual dataclass definitions and default values
- Verify field names and types from implementation

Base Config (reference only): {{base_hypothesis_folder}}/03_config.md

⚠️ RULE: Specs may specify `lr: 0.01` but code uses `learning_rate: 0.1`.
   Always verify field names and defaults from actual code!

Include "Inherited Configuration" section with verified field names.
{{endif}}

## MANDATORY MCP USAGE (Agent MUST call these!)
- Archon: rag_search_knowledge_base("DL config patterns")

## MANDATORY OUTPUT SECTIONS (Agent MUST include!)
- "Applied: {pattern_name}" line for each Archon KB pattern used
```

</mandatory-action>

### 2. Wait for Both Agents

```python
AgentOutputTool(agentId=logic_agent_id, block=True)
AgentOutputTool(agentId=config_agent_id, block=True)
```

### 3. Verify Outputs (MANDATORY POST-TASK CHECK)

<output-validation type="auto-check">

**Read BOTH output files and verify:**

#### 03_logic.md Validation:

| Check | Required Content | If Missing |
|-------|------------------|------------|
| ✅ | `## Codebase Analysis (Serena)` section | **DELETE FILE & RE-INVOKE AGENT** |
| ✅ | `Applied:` line (at least 1) | **DELETE FILE & RE-INVOKE AGENT** |
| ✅ | APIs with type hints | Warn but continue |
| ✅ | Tensor shapes | Warn but continue |
{{if base_hypothesis}}
| ✅ | External Dependencies API section | **DELETE FILE & RE-INVOKE AGENT** |
{{endif}}

#### 03_config.md Validation:

| Check | Required Content | If Missing |
|-------|------------------|------------|
| ✅ | `Applied:` line (at least 1) | **DELETE FILE & RE-INVOKE AGENT** |
| ✅ | YAML schemas or dataclasses | Warn but continue |
{{if base_hypothesis}}
| ✅ | Inherited Configuration section | **DELETE FILE & RE-INVOKE AGENT** |
{{endif}}

**Validation Logic:**
```python
# Validate 03_logic.md
logic_content = Read("{{hypothesis_folder}}/03_logic.md")
IF "## Codebase Analysis" NOT in logic_content OR "Applied:" NOT in logic_content:
    Delete("{{hypothesis_folder}}/03_logic.md")
    # RE-INVOKE logic-agent ONLY

# Validate 03_config.md
config_content = Read("{{hypothesis_folder}}/03_config.md")
IF "Applied:" NOT in config_content:
    Delete("{{hypothesis_folder}}/03_config.md")
    # RE-INVOKE configuration-agent ONLY

# Continue to next step only if BOTH validations pass
```

</output-validation>

### 4. Display Summary

```
✓ Parallel Agents Complete

Logic Agent: {{logic_subtasks}}/{{logic_budget}} subtasks
Config Agent: {{config_subtasks}}/{{config_budget}} subtasks
Total: {{total}} / {{task_budget_total_max}} ✓
```

### 5. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

**UNATTENDED Mode**: Auto-progress to Step 6
**Interactive Mode**: Display menu:

"**Select an Option:** [R] Review Agent Outputs [C] Continue [X] Exit"

#### Menu Handling Logic:
- IF R: Display Logic and Config output summaries with subtask counts, return to menu
- IF C: Load next step
- IF X: Exit workflow gracefully

#### EXECUTION RULES:
- ALWAYS halt and wait for user input after presenting menu (Interactive mode)
- ONLY proceed to next step when user selects 'C' or UNATTENDED mode is active
- After other menu items execution, return to this menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN both agents complete AND 03_logic.md and 03_config.md exist in hypothesis folder AND subtask counts are within allocated budgets, proceed to load and execute `{workflow_path}/steps/step-06-complexity-assessment.md` for overall complexity assessment.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Both agents spawned in parallel (single message)
- Each agent used Archon MCP for KB research
- Serena MCP used appropriately:
  - IF base_hypothesis → Base code analyzed with Serena
  - IF existing codebase → Patterns discovered with Serena
  - IF green-field → Serena skipped (acceptable)
- 03_logic.md created in hypothesis folder
- 03_config.md created in hypothesis folder
- Subtasks within allocated budgets
- "Codebase Analysis" section included in both outputs (even if green-field)
{{if base_hypothesis}}
- External Dependencies API verified from actual code
- Inherited Configuration verified from actual code
{{endif}}

### ❌ SYSTEM FAILURE:
- Spawning agents sequentially
- Exceeding subtask budgets
- Missing Archon MCP usage in agent outputs
- Total tasks exceeding budget
- Using Write tool to create outputs directly
- **Skipping Serena when base_hypothesis exists** (MUST verify actual code)
- **Skipping Serena when existing codebase exists** (MUST discover patterns)
{{if base_hypothesis}}
- API signatures copied from specs instead of actual code
- Missing External Dependencies section in 03_logic.md
- Missing Inherited Configuration section in 03_config.md
{{endif}}

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
