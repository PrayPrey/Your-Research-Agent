---
description: 'Full automated UNATTENDED pipeline: Phase 0 → 1 → 2A → 2B → (2C → 3 → 4) × N → 4.5 → [5] → 6 → 6.5. Takes research idea file and runs entire pipeline with paper generation. Phase 5 is optional (skipped when skip_baseline_comparison=true in module.yaml).'
---

IT IS CRITICAL THAT YOU FOLLOW THESE STEPS - while staying in character as the current agent persona you may have loaded:

<steps CRITICAL="TRUE">
1. Always LOAD the FULL @_bmad/core/tasks/workflow.xml
2. READ its entire contents - this is the CORE OS for EXECUTING the specific workflow-config @bmad-custom-src/custom/modules/youra-research/workflows/full-pipeline-unattended/workflow.yaml
3. Pass the yaml path bmad-custom-src/custom/modules/youra-research/workflows/full-pipeline-unattended/workflow.yaml as 'workflow-config' parameter to the workflow.xml instructions
4. Follow workflow.xml instructions EXACTLY as written to process and follow the specific workflow config and its instructions
5. Save outputs after EACH section when generating any documents from templates
</steps>

<critical>
**Workflow Chain (v3.7 - Clean Step Numbers 0-11):**
- full-pipeline-unattended/workflow.yaml defines `hypothesis_loop_workflow`, `phase5_workflow`, `phase6_workflow`, `phase65_workflow` paths
- Step 7 in instructions.md invokes hypothesis-loop (Phase 2C → 3 → 4 only)
- Step 8 in instructions.md invokes Phase 5 separately after hypothesis-loop completes
- Step 9 in instructions.md invokes Phase 6 (Paper Writing)
- Step 10 in instructions.md invokes Phase 6.5 (Adversarial Review)
- Step 11 is Final Summary
- workflow.xml runner interprets ALL invoke-workflow tags in instructions.md automatically
- Note: invoke-workflow tags in step files are NOT interpreted (hence Step 8/9/10 exist)

**Sub-Agents (Phase 3) - MUST use Task tool:**
- architecture-agent, logic-agent, configuration-agent

**Sub-Agent (Phase 4) - MUST use Task tool:**
- Validator Agent (subagent_type="general-purpose")

**DO NOT:**
- Skip workflow.xml runner loading
- Use Write tool to directly create 03_architecture.md, 03_logic.md, 03_config.md
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

### Phase 6 - Paper Writing:
| Requirement | Tool | Purpose |
|-------------|------|---------|
| Archon KB Search | `mcp__archon__rag_search_*()` | Academic writing patterns |
| Semantic Scholar | `mcp__semantic_scholar__*()` | Citation verification |
| All Phase 0-5 Artifacts | Read tool | Content for paper sections |

### Phase 6.5 - Adversarial Review:
| Requirement | Tool | Purpose |
|-------------|------|---------|
| ClearThought (if available) | `mcp__clearthought__*()` | Structured critique |
| Multi-round review | Internal processing | Devil's Advocate review |
| Paper revision | Edit/Write tools | Apply fixes |

### Gate System & Routing (v3.7 Updated):
| Gate | Result | Action |
|------|--------|--------|
| Phase 4 MUST_WORK | PASS | → Next hypothesis (or Step 8 if all done) |
| Phase 4 MUST_WORK | FAIL | → Route to Phase 0 (Serena Memory saved) |
| Phase 4 MUST_WORK | PARTIAL (max attempts) | → Route to Phase 2A-Dialogue (Serena Memory saved) |
| Phase 5 DETERMINES_SUCCESS | PASS | → Step 9 (Phase 6) |
| Phase 5 DETERMINES_SUCCESS | PARTIAL | → Route to Phase 0 (Serena Memory saved) |
| Phase 5 DETERMINES_SUCCESS | SKIPPED | → Step 9 (Phase 6) directly (skip_baseline_comparison=true) |
| Phase 6 (no gate) | Complete | → Step 10 (Phase 6.5) |
| Phase 6.5 Convergence | Converged | → Step 11 (Final Summary) |

**v3.7 Note:** Phase 5 invoked by Step 8, Phase 6 by Step 9, Phase 6.5 by Step 10. All in instructions.md.

### invoke-workflow Execution:
When encountering `<invoke-workflow>` tag:
1. **MUST** load target workflow's workflow.yaml
2. **MUST** load target workflow's workflow.md or instructions.md completely
3. **MUST** load and execute each step-*.md file in order
4. **MUST** follow all MCP/Agent requirements in target workflow
5. **NEVER** shortcut by directly creating expected output files

**CRITICAL: invoke-workflow = INLINE EXECUTION**
- YOU execute the workflow directly in YOUR current context
- DO NOT spawn invoke-workflow as a Task agent
- invoke-workflow is NOT delegating to a sub-agent
- Task tool is ONLY for explicitly marked agents (architecture-agent, validator-agent, etc.)
- Phase 0, Phase 1, Phase 2A-Ext, Phase 2B, Phase 2C, Phase 6 all run INLINE via invoke-workflow

### Output Validation (MANDATORY):
After Phase 3 agent execution, verify each output contains:
- `Applied:` line (proves Archon KB was used)
- `## Codebase Analysis` section (if Serena was required)

**IF MISSING → DELETE file and RE-INVOKE the agent**

### FORBIDDEN Actions (= SYSTEM FAILURE):
- Write tool to create 03_architecture.md directly
- Write tool to create 03_logic.md directly
- Write tool to create 03_config.md directly
- Skipping Archon KB search before code generation
- Running Bash/Serena validation directly instead of Task tool for Validator
- Skipping step file loading (each step-*.md must be executed)
- "Simulating" agent work instead of actually spawning agents
</unattended-mode-exceptions>

ARGUMENTS: $ARGUMENTS
