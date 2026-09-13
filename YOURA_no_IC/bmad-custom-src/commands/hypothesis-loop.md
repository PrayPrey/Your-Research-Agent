---
description: 'Execute hypothesis verification loop. Automatically runs Phase 2C → 3 → 4 → 5 for each READY hypothesis in dependency order with gate validation.'
---

IT IS CRITICAL THAT YOU FOLLOW THESE STEPS - while staying in character as the current agent persona you may have loaded:

<steps CRITICAL="TRUE">
1. LOAD the FULL workflow file: @bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop/workflow.md
2. READ its entire contents - this contains workflow configuration and step flow overview
3. LOAD and EXECUTE step-01-init.md from the steps/ directory
4. Follow step-file architecture: execute each step completely, then load nextStepFile
5. Save outputs after EACH phase when generating documents
</steps>

<workflow-paths>
**Entry Point (v2.0.0 - Standalone Format):**
- workflow.md: `bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop/workflow.md`
- First Step: `bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop/steps/step-01-init.md`

**Step Flow:**
```
step-01-init.md          → Parse mode + Load state
step-02-check-status.md  → Check workflow status
step-03-get-ready.md     → Get READY hypotheses queue
    ↓
┌─→ step-04-loop-start.md    → Gate validation + IN_PROGRESS
│   step-05-phase-2c.md      → Execute Phase 2C
│   step-06-phase-3.md       → Execute Phase 3
│   step-07-phase-4.md       → Execute Phase 4
│   step-08-phase4-gate.md   → Process MUST_WORK gate
│   step-09-loop-continue.md → Mode actions + loop control
└───────────────────────────────────────────────────────────┘
    ↓ (when all sub-hypotheses done)
step-10-phase-5.md       → Execute Phase 5 (main_hypothesis)
step-11-complete.md      → Completion summary
```
</workflow-paths>

<critical>
**Workflow Chain:**
- hypothesis-loop invokes Phase 2C → Phase 3 → Phase 4 → Phase 5 for each hypothesis
- Each phase has its own workflow.yaml and step-*.md files
- invoke-workflow tags MUST be followed completely (load + execute all steps)

**Sub-Agents (Phase 3) - MUST use Task tool:**
- architecture-agent (subagent_type="architecture-agent")
- logic-agent (subagent_type="logic-agent")
- configuration-agent (subagent_type="configuration-agent")

**Sub-Agent (Phase 4) - MUST use Task tool:**
- Validator Agent (subagent_type="validator-agent")

**DO NOT:**
- Skip step file loading (each step-*.md must be executed in order)
- Use Write tool to directly create 03_architecture.md, 03_logic.md, 03_config.md
- Bypass invoke-workflow execution
</critical>

<unattended-mode-exceptions CRITICAL="TRUE">
## UNATTENDED MODE - CORRECT DEFINITION

<critical>
**UNATTENDED ≠ SIMPLIFIED** (NOT simplification)
**UNATTENDED ≠ SHORTCUT** (NOT a shortcut)
**UNATTENDED ≠ SKIP_STEPS** (NOT skipping steps)

**UNATTENDED = EXECUTE_ALL + NO_USER_PROMPT**
           = Execute ALL steps completely + Skip ONLY user prompts

**Pre-Execution Self-Check (MANDATORY):**
```
□ Am I about to skip a step-*.md file? → VIOLATION
□ Am I about to skip an MCP tool call? → VIOLATION
□ Am I about to skip a Task agent call? → VIOLATION
□ Am I only skipping [Y/N] confirmation? → ALLOWED
```
</critical>

### UNATTENDED mode ONLY skips:
- User confirmations ([C] Continue, [Y/N])
- Review menus ([R] Review)
- Discussion pauses

### UNATTENDED mode **NEVER** skips (SYSTEM FAILURE if skipped):

### Phase 2C - Experiment Design:
| Requirement | Tool | Purpose |
|-------------|------|---------|
| Archon KB Search | `mcp__archon__rag_search_*()` | Research-backed experiment specs |
| Exa Search | `mcp__exa__*()` | Implementation examples |

### Phase 3 - Implementation Planning:
| Requirement | Tool | Output |
|-------------|------|--------|
| Architecture Agent | `Task(subagent_type="architecture-agent")` | 03_architecture.md |
| Logic Agent | `Task(subagent_type="logic-agent")` | 03_logic.md |
| Config Agent | `Task(subagent_type="configuration-agent")` | 03_config.md |
| Archon KB Search | `mcp__archon__rag_search_knowledge_base()` | Inside each agent |
| Serena Analysis | `mcp__serena__get_symbols_overview()` | If codebase exists |

### Phase 4 - Coding & Validation:
| Requirement | Tool | Purpose |
|-------------|------|---------|
| Task Query | `mcp__archon__find_tasks()` | Get todo tasks |
| KB Search | `mcp__archon__rag_search_*()` | Before code generation |
| Code Analysis | `mcp__serena__get_symbols_overview()` | Understand existing code |
| Validator Agent | `Task(subagent_type="validator-agent")` | Validate generated code |

### Phase 5 - Baseline Comparison:
| Requirement | Tool | Purpose |
|-------------|------|---------|
| Baseline Validator Agent | `Task(subagent_type="baseline-validator-agent")` | Compare against baseline |
| Archon KB Search | `mcp__archon__rag_search_*()` | Best practices reference |
| Serena Analysis | `mcp__serena__*()` | Code comparison |

### invoke-workflow Execution:
When encountering `<invoke-workflow>` tag in a step file:
1. **MUST** load target workflow's workflow.yaml
2. **MUST** load target workflow's workflow.md or instructions.md completely
3. **MUST** load and execute each step-*.md file in order
4. **MUST** follow all MCP/Agent requirements in target workflow
5. **NEVER** shortcut by directly creating expected output files

### Output Validation (MANDATORY):
After Phase 3 agent execution, verify each output contains:
- `Applied:` line (proves Archon KB was used)
- `## Codebase Analysis` section (if Serena was required)

**IF MISSING → DELETE file and RE-INVOKE the agent**

### Gate System Enforcement:
**Phase 4 - MUST_WORK Gate:**
| Result | Action |
|--------|--------|
| PASS | → Continue to Phase 5 |
| FAIL | → Route to Phase 0 (save Serena Memory first) |
| PARTIAL (max attempts) | → Route to Phase 2A-Dialogue (save Serena Memory first) |

**Phase 5 - DETERMINES_SUCCESS Gate:**
| Result | Action |
|--------|--------|
| PASS | → Mark hypothesis COMPLETED |
| PARTIAL | → Route to Phase 0 (save Serena Memory first) |

**Serena Memory for Routing:**
- Phase 4 FAIL: `mcp__serena__write_memory("failure_{hypothesis_id}.md", ...)`
- Phase 4 PARTIAL: `mcp__serena__write_memory("pivot_{h_id}_{new_h_id}.md", ...)`
- Phase 5 PARTIAL: `mcp__serena__write_memory("phase5_failure_{hypothesis_id}.md", ...)`

**State Updates:**
- Update verification_state.yaml after each phase/gate completion
- Set workflow.status = "ROUTED" when routing occurs

### FORBIDDEN Actions (= SYSTEM FAILURE):
- Write tool to create 03_architecture.md directly
- Write tool to create 03_logic.md directly
- Write tool to create 03_config.md directly
- Skipping Archon KB search before code generation
- Running Bash/Serena validation directly instead of Task tool for Validator
- Skipping step file loading (each step-*.md must be executed)
- "Simulating" agent work instead of actually spawning agents
- Ignoring gate validation results
</unattended-mode-exceptions>

ARGUMENTS: $ARGUMENTS
