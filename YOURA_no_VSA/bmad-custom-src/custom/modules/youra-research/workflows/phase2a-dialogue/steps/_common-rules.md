# Phase 2A Dialogue - Common Rules

> **Note:** This file contains shared rules that apply to ALL step files in the Phase 2A Dialogue workflow.
> Each step file should reference this file instead of duplicating these rules.

---

## MANDATORY EXECUTION RULES (READ FIRST)

### 📖 File Reading Protocol (CRITICAL)

**Complete execution of ANY step file requires reading the entire file at once.**

**File Length Detection:**
```bash
# ALWAYS check file length first if uncertain
wc -l {step_file_path}
```

**Reading Method by File Size:**

| File Size | Method | Example |
|-----------|--------|---------|
| < 2000 lines | Read entire file at once | `Read(file_path="{step_file}")` |
| ≥ 2000 lines | Read in chunks with offset/limit | `Read(file_path, offset=0, limit=2000)` then `Read(file_path, offset=2000, limit=2000)` |

**✅ Correct Reading (for files < 2000 lines):**
```python
# Read entire file at once - NO limit/offset parameters
Read(file_path="{step_file_path}")
```

**❌ Incorrect Reading (PROHIBITED for files < 2000 lines):**
```python
# DO NOT use limit/offset for small files
Read(file_path="{step_file_path}", offset=0, limit=200) # ❌ Partial reading
Read(file_path="{step_file_path}", offset=200, limit=200) # ❌ Causes section omission
```

**⚠️ CRITICAL WARNING - Decimal Sections:**

Some step files contain **decimal sections** (e.g., Section 0.1, 0.2, 1.5):
- Do NOT assume sequential whole numbers (Section 0 → Section 1)
- **Decimal sections (0.1, 0.2, 0.3, 1.5) MUST NOT be skipped**
- All sections must be executed sequentially without omission

**📋 Phase 2A Known Decimal Section Patterns:**
- `1.5` - Recursive Detection and Version Management (step-00)
- `5.5` - Create Hook Detection Files (step-00)

**🚨 INCIDENT PREVENTION:**
- Phase 2A is hypothesis validation phase - missing sections could skip critical initialization
- Missing decimal sections in step-01 could skip Round Table setup and failure context
- Missing decimal sections in step-03 could skip dialogue initialization

---

## 🚨 UNATTENDED MODE ENFORCEMENT (CRITICAL - READ EVERY STEP)

### What UNATTENDED Mode IS:

```
UNATTENDED = EXECUTE_ALL_STEPS + NO_USER_CONFIRMATION
           = Execute ALL steps completely + Skip ONLY user prompts
```

### What UNATTENDED Mode IS NOT:

```
UNATTENDED ≠ SIMPLIFIED (NOT simplification)
UNATTENDED ≠ SHORTCUT (NOT a shortcut)
UNATTENDED ≠ SKIP_STEPS (NOT skipping steps)
UNATTENDED ≠ FASTER_EXECUTION (NOT faster execution)
UNATTENDED ≠ SKIP_TO_SAVE_TOKENS (NOT token optimization)
```

### Pre-Step Self-Check (MANDATORY)

Before executing ANY step, verify:
- [ ] Am I about to skip a step-*.md file? → **VIOLATION**
- [ ] Am I about to skip an MCP tool call? → **VIOLATION**
- [ ] Am I about to skip a Task agent call? → **VIOLATION**
- [ ] Am I about to skip a MANDATORY section? → **VIOLATION**
- [ ] Am I only skipping [Y/N] user confirmation? → **ALLOWED**

### invoke-workflow = INLINE EXECUTION (CRITICAL)

**When encountering `<invoke-workflow>` tag:**
- ✅ YOU execute the workflow directly in YOUR current context
- ✅ Load target workflow's workflow.yaml AND instructions.md
- ✅ Execute each step-*.md file in order IN YOUR CONTEXT
- ❌ DO NOT spawn invoke-workflow as a Task agent
- ❌ Spawning Phase workflow as Task agent = SYSTEM FAILURE

### NEVER SKIP (Even to Save Tokens)

**NEVER skip these to save tokens or execution time:**
- ❌ MCP tool calls (mcp__archon__*, mcp__serena__*, etc.)
- ❌ MANDATORY sections (clearly marked in step files)
- ❌ Decimal sections (e.g., Section 1.5, 5.5)
- ❌ Hook orchestration exchanges (each persona response)
- ❌ Output YAML file updates

**Skipping any of the above = SYSTEM FAILURE**

---

### Universal Rules

- 🛑 NEVER generate content without user input (Interactive mode)
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR executing predefined workflow steps
- ⚠️ ABSOLUTELY NO TIME ESTIMATES

### Role Reinforcement

- ✅ You are a hypothesis dialogue orchestrator
- ✅ If you already have been given a name, communication_style and persona, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring hypothesis evaluation expertise, user brings research context
- ✅ Maintain collaborative professional tone throughout

---

## UNATTENDED Mode Detection

Before displaying any menu:

1. **Check Archon doing task:** `mcp__archon__find_tasks(filter_by="status", filter_value="doing")`
2. **Check description:** If task description starts with `[UNATTENDED]` → Auto-select [C] Continue
3. **Skip menu display** and proceed directly to next step

---

## Execution Architecture

Phase 2A uses **Self-Contained Tikitaka Loop** execution:
- All 6 personas (Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex) run INLINE
- Persona definitions loaded from `personas.yaml` (Single Source of Truth)
- External LLM (`orchestrate_exchange.py`) selects personas + writes one exchange per iteration
- Claude writes the other exchange per iteration (Tikitaka dual-exchange)
- No Task Agent spawning — all discussion runs in Main Session

---

## Standard Step Navigation

After completing each step:

1. Update output YAML files (e.g., `01_round_table.yaml`, `02_synthesis.yaml`)
2. Load and execute the next step file

**NEXT Step Format:** Load, read the full file, and then execute `{nextStepFile}`

---

## Success/Failure Framework

Each step has specific SUCCESS and FAILURE metrics defined in the step file itself.

**Universal Failure Conditions:**
- Skipping steps or optimizing sequences
- Not following exact instructions
- Not spawning required agents via Task tool
- Not reading complete step file before execution

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

## MCP Tools Reference (Consolidated)

> **Note:** This section provides a unified reference for all MCP tools available to Phase 2A agents.
> Individual agent files should reference this section instead of duplicating tool tables.

### Research Tools

| MCP Server | Tool | Purpose |
|------------|------|---------|
| **Archon** | `rag_search_knowledge_base` | Search knowledge base for relevant content |
| **Archon** | `rag_search_code_examples` | Find code examples and implementations |
| **Exa** | `web_search_exa` | Web search for implementations, papers |
| **Exa** | `get_code_context_exa` | GitHub code search and context |
| **Semantic Scholar** | `paper_relevance_search` | Find relevant academic papers |
| **Serena** | `list_memories` | Access cross-pipeline learning context |
| **Serena** | `read_memory` | Read specific memory file content |

### Reasoning Tools

| MCP Server | Tool | Purpose |
|------------|------|---------|
| **ClearThought** | `sequentialthinking` | Systematic step-by-step analysis |
| **ClearThought** | `mentalmodel` | First principles thinking |
| **ClearThought** | `collaborativereasoning` | Multi-perspective reasoning |
| **ClearThought** | `structuredargumentation` | Build structured arguments |
| **ClearThought** | `metacognitivemonitoring` | Self-assess reasoning quality |
| **ClearThought** | `debuggingapproach` | Systematic problem identification |

### Usage in Self-Contained Tikitaka Loop

| Step | Execution | Available Tools |
|------|-----------|-----------------|
| **step-00-initialize** | INLINE | Archon (task management), file I/O |
| **step-01-discussion** | INLINE + orchestrate_exchange.py (Bash) | All research + reasoning tools (personas run inline) |
| **step-02-structuring** | INLINE | File I/O, YAML generation |
