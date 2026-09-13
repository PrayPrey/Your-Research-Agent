---
name: Phase 3 Implementation Planning
description: Transform Phase 2C experiment design into Architecture (with integrated checklist), Logic, Config, and Archon tasks
web_bundle: true
workflow_type: orchestration # standard | orchestration | validation
---

# Phase 3: Implementation Planning Workflow

**Goal:** Transform Phase 2C experiment design into complete implementation plan with PRD, Architecture, Logic, Config, and Archon tasks.

**Note:** Archon tasks are extracted directly from 03_prd.md (data/environment), 03_architecture.md (epic tasks), 03_logic.md (subtasks), and 03_config.md. No separate PRP generation step.

**Your Role:** In addition to your name, communication_style, and persona, you are also an implementation planning orchestrator collaborating with a researcher. This is a partnership, not a client-vendor relationship. You bring workflow orchestration expertise and MCP service coordination, while the user brings research context, hypothesis knowledge, and domain expertise. Work together as equals to create a comprehensive implementation plan.

---

## WORKFLOW ARCHITECTURE

Uses **step-file architecture**: micro-file design, just-in-time loading, sequential enforcement.

**Step Processing:** Read complete → Follow sequence → Wait for input → Check continuation → Save state → Load next

**Modes:** Interactive (menus, confirmations) | UNATTENDED (autonomous, validation checkpoints only)

### 🚨 UNATTENDED MODE ENFORCEMENT

**SKIPS:** User confirmations, review menus, optional elaborations
**NEVER SKIPS:** Task tool, MCP calls, step execution, output generation, validation

**CRITICAL:** `UNATTENDED ≠ Skip tool calls`. Direct Write to 03_*.md = SYSTEM FAILURE.

**Required Agents:** Step 3: `architecture-agent` | Step 5: `logic-agent` + `configuration-agent` (parallel)

### 🔍 OUTPUT VALIDATION (POST-STEP AUTO-CHECK)

> 📄 **Full Reference:** See `docs/output-validation.md` for validation logic and required content table.

**Quick Rule:** After agent steps (3, 5), verify output contains:
- `## Codebase Analysis (Serena)` section
- `Applied:` line (Archon KB pattern)

If missing → Delete file → RE-INVOKE agent (max 2 retries)

### Critical Rules

🛑 Never load multiple steps | 📖 Read entire step first | 🚫 No skipping | 💾 Update frontmatter | ⏸️ Halt at menus | ⚠️ No time estimates

---

## INTENTIONAL DEVIATIONS FROM BMAD v6

This workflow intentionally extends BMAD v6 standards for YouRA research pipeline requirements:

| Deviation | Reason | Benefit |
|-----------|--------|---------|
| **UNATTENDED MODE ENFORCEMENT** | Research automation requires autonomous execution | Prevents agent bypass, ensures consistent results |
| **Spectrum Mode Configuration** | Dual Interactive/UNATTENDED execution modes | Flexible operation based on user preference |
| **OUTPUT VALIDATION (POST-STEP)** | Quality gates for agent outputs | Ensures MCP tools (Archon KB, Serena) are actually used |
| **_common-rules.md reference** | DRY principle for shared rules across 10 steps | Single source of truth, easier maintenance |
| **Task References omission** | Orchestration workflow using Task agents | A/P elicitation workflows not applicable for agent spawning |
| **Custom config path** | YouRA module isolation | Separate from core BMAD configuration |

**Compliance Note:** These deviations are documented per BMAD v6 compliance guidelines. The workflow maintains full compliance with core BMAD principles (step-file architecture, sequential enforcement, menu handling) while extending functionality for research pipeline needs.

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Load and read full config from `{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml` and resolve:

- `user_name`, `communication_language`, `output_folder`
- `research_output_path` (YouRA-specific)
- `date` as system-generated current datetime

### 2. Verify MCP Requirements

**CRITICAL**: This workflow requires **Archon MCP** for project and task management.

Before starting, verify Archon MCP is available:
- Try calling `mcp__archon__health_check()` or check available MCP tools
- If Archon MCP NOT available, STOP and inform user

### 3. First Step EXECUTION

Load, read the full file and then execute `{workflow_path}/steps/step-01-initialize.md` to begin the workflow.

**Note:** `{workflow_path}` = `{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning`

---

## WORKFLOW TYPE: ORCHESTRATION

Invokes: BMAD PRD workflow → Task Agents → Archon MCP. Your role: invoke, monitor, validate, maintain continuity.

---

## WORKFLOW STEPS (10 Steps)

| Step | Agent/Type | Output |
|------|------------|--------|
| 1 | Validation | Inputs + folder created |
| 2 | BMAD workflow | 03_prd.md |
| 3 | `architecture-agent` | 03_architecture.md |
| 4-6 | Calculation + `logic-agent` + `configuration-agent` (parallel) | 03_logic.md + 03_config.md |
| 7-8 | Validation + MCP | Archon project + docs |
| 9-10 | File Gen + Validation | 03_tasks.yaml + report |

> 📄 **Full Reference:** See `docs/multi-agent-architecture.md` for architecture diagram.

**Task Budget:** LIGHT=15 (EXISTENCE) | FULL=30 (MECHANISM/COMPARISON)

---

## INPUT REQUIREMENTS

- **Required Input:** `{hypothesis_folder}/02c_experiment_brief.md` (Level 1.5 spec from Phase 2C)
- **Required Services:** Archon MCP (mandatory), Serena MCP (conditional)

**Serena MCP:** MANDATORY if base hypothesis or existing code exists; OPTIONAL for green-field.

---

## OUTPUT ARTIFACTS

**Output Location:** `{research_output_path}/youra_research/{{hypothesis_id_lower}}/` (created in Step 1)

| # | File | Content | Step |
|---|------|---------|------|
| 1 | `03_prd.md` | Requirements, data spec, dependencies | Step 2 |
| 2 | `03_architecture.md` | Modules, Epic tasks, file structure | Step 3 |
| 3 | `03_logic.md` | API signatures, algorithms | Step 5 |
| 4 | `03_config.md` | Hyperparameters, settings | Step 5 |
| 5 | `03_tasks.yaml` | 5-30 tasks (LIGHT: 5-15, FULL: 10-30) | Step 9 |
| 6 | Archon Project | 5 documents uploaded | Step 8 |

---

## EXECUTION PRINCIPLES

| Principle | Rule |
|-----------|------|
| **No Time Estimates** | Focus on WHAT, not WHEN; let workflows complete at their own pace |
| **Wait for Completion** | Never interrupt sub-workflows; proceed only after verification |
| **Validate Everything** | Check file existence, completeness, and Archon success |
| **User Confirmation** | Present [C/R/Q] menus and wait for explicit input |

---

## ⚠️ KNOWN FAILURE MODES & ERROR HANDLING

> 📄 **Full Reference:** See `docs/failure-modes.md` for detailed failure modes, tool mapping table, past mistake examples, and error handling procedures.

**Quick Reference - Tool Mapping:**
| Step | Output | Correct Method |
|------|--------|----------------|
| Step 2 | PRD | Execute **BMAD workflow** |
| Step 3 | Architecture | `Task(subagent_type="architecture-agent")` |
| Step 5 | Logic/Config | `Task(subagent_type="logic-agent")` / `configuration-agent` |
| Step 9 | 03_tasks.yaml | Parse 03_*.md + Write to YAML file |

**UNATTENDED Mode Rule:**
- ✅ MUST use defined subagent_type, execute BMAD workflow, parse docs, call MCP
- ❌ NEVER directly Write outputs without spawning agents

---

## RESUMPTION SUPPORT

Phase 3 can be resumed if interrupted:

1. Check which files exist:
   - PRD? → Resume from Step 3 (Architecture)
   - Architecture? → Resume from Step 4 (Complexity)
   - Logic + Config? → Resume from Step 7 (Verify Documents)

2. Check Archon project:
   - Project exists? → Resume from Step 9 (Tasks)
   - Tasks exist? → Resume from Step 10 (Validation)

3. Verify all previous outputs before resuming

---

## NEXT PHASE CONNECTION

After Phase 3, proceed to Phase 4 using 03_tasks.yaml (query by priority: data prep → env → implementation).

---
