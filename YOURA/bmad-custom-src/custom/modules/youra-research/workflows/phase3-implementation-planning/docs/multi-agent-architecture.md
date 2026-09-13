# Multi-Agent Architecture Reference

> **Reference File:** Extracted from workflow.md for file size optimization
>
> **Purpose:** Documents the multi-agent system architecture for Phase 3

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Main Orchestrator │
│ (This workflow session) │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼ │               │
┌──────────────────┐ │       ┌───────┴───────┐
│ Architecture │       │ │   Step 4 │
│ Agent (Step 3) │───────┼──────▶│ Allocate │
│ architecture- │       │ │   Budgets │
│ agent │       │ └───────┬───────┘
└──────────────────┘ │               │
                           │ ┌───────┴───────┐
                           │ ▼               ▼
                    ┌──────────────┐ ┌──────────────┐
                    │ Logic Agent │   │ Config Agent │
                    │ (Step 5) │   │ (Step 5) │
                    │ logic-agent │   │ configuration│
                    │ PARALLEL │   │ -agent │
                    └──────────────┘ └──────────────┘
```

---

## Task Budget Constraint (2-Tier System)

| Tier | Hypothesis Type | Total Max | Epic Range |
|------|-----------------|-----------|------------|
| LIGHT | EXISTENCE | 15 | 4-8 |
| FULL | MECHANISM, COMPARISON | 30 | 6-12 |

**Agent Responsibilities:**
- **Architecture Agent**: 4-12 Epic tasks (based on tier)
- **Logic Agent**: Subtasks for high-complexity modules
- **Config Agent**: Subtasks for configuration modules

---

## Agent Invocation Rules

1. **Step 3**: Spawn `Task(subagent_type="architecture-agent", ...)` for 03_architecture.md
2. **Step 5**: Spawn BOTH agents in PARALLEL:
   - `Task(subagent_type="logic-agent", ...)` for 03_logic.md
   - `Task(subagent_type="configuration-agent", ...)` for 03_config.md

**Direct Write tool usage to create agent outputs is FORBIDDEN** - agents use:
- Archon KB to search for best practices and patterns
- Serena MCP to analyze existing codebase
