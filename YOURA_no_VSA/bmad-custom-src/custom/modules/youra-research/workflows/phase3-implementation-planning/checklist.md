# Phase 3: Implementation Planning - Validation Checklist

---

## Pre-Execution
- [ ] `02c_experiment_brief.md` exists
- [ ] `verification_state.yaml` exists
- [ ] Archon MCP available (MANDATORY)
- [ ] Serena MCP available (CONDITIONAL: MANDATORY if base hypothesis/existing code exists)

---

## Step Execution Tracking

### Step 1: Initialize
- [ ] Auto-resume check | verification_state loaded | Phase 2C = COMPLETED
- [ ] Pipeline project ID retrieved (metadata.pipeline_project_id → pipeline.project_id fallback)
- [ ] MCP services verified | Hypothesis ID collected
- [ ] Tier calculated: LIGHT (EXISTENCE, 15 max) | FULL (MECHANISM/COMPARISON, 30 max)
- [ ] Output folder created: `{hypothesis_folder}/`

### Step 2: PRD Generation
- [ ] Phase 2C key info extracted (ALL baselines, ALL ablations, custom metrics)
- [ ] **BMAD v6 PRD workflow invoked** (NOT Write tool)
- [ ] `03_prd.md` generated in hypothesis folder

### Step 3: Architecture Agent
- [ ] **Task tool called**: subagent_type="architecture-agent"
- [ ] MCP used: Archon KB + Serena (conditional)
- [ ] Output validation: `## Codebase Analysis (Serena)` + `Applied:` line + Epic tasks
- [ ] `03_architecture.md` created

### Step 4: Subtask Budget
- [ ] Complexity scores extracted from Epics
- [ ] Subtask budget calculated: VeryHigh=4-5, High=3-4, Medium=1-2, Low=0
- [ ] Budget split between Logic/Config agents

### Step 5: Parallel Agents
- [ ] **BOTH agents spawned in PARALLEL** (single message)
- [ ] Logic Agent: KB search + `Codebase Analysis` + `Applied:` → `03_logic.md`
- [ ] Config Agent: KB search + `Applied:` → `03_config.md`

### Step 6: Complexity Assessment
- [ ] 5-factor algorithm applied (Modules+Integration+Novel+Testing+Dependencies)
- [ ] Tier validation performed
- [ ] Budget rebalancing applied if exceeded → `{{excluded_subtasks}}`

### Step 7: Verify Documents
- [ ] All 4 documents exist: prd, architecture, logic, config

### Step 8: Upload to Pipeline Project
- [ ] Pipeline Project ID retrieved (NOT create new project)
- [ ] 5 documents uploaded: PRD, Architecture, Logic, Config, Experiment Brief
- [ ] verification_state updated with document IDs

### Step 9: Generate Tasks File
- [ ] All 4 documents parsed for tasks
- [ ] Data prep + env setup + Epic tasks + subtasks extracted
- [ ] reference_files linked for Epic tasks
- [ ] Failsafe task added (priority 1)
- [ ] `03_tasks.yaml` generated (NOT Archon tasks)
- [ ] Within budget verified

### Step 10: Validation & Summary
- [ ] All 5 files validated | Archon project verified
- [ ] 03_tasks.yaml validated (schema, budget, fields)
- [ ] Scorecard completed (/22)
- [ ] Pipeline update (current hypothesis only)

---

## Output Files
- [ ] `03_prd.md` > 5KB
- [ ] `03_architecture.md` > 5KB
- [ ] `03_logic.md` > 3KB
- [ ] `03_config.md` > 3KB
- [ ] `03_tasks.yaml` > 1KB

---

## Task Budget Compliance

| Item | Count |
|------|-------|
| Tier | ___ (LIGHT/FULL) |
| Budget | ___ (15 or 30) |
| Data Prep | ___ |
| Env Setup | ___ |
| Epic Tasks | ___/12 |
| Subtasks | ___ |
| Failsafe | 1 |
| **TOTAL** | ___/___ |

- [ ] Epic tasks: 4-12 range
- [ ] **Total ≤ Budget**

---

## MCP Compliance

### Agent Outputs
| Agent | Archon KB | Serena Analysis | Applied Line |
|-------|-----------|-----------------|--------------|
| Architecture | [ ] | [ ] | [ ] |
| Logic | [ ] | [ ] | [ ] |
| Config | [ ] | N/A | [ ] |

---

## Archon Integration

- [ ] Pipeline Project ID: _______________
- [ ] Documents uploaded: 5
- [ ] verification_state.yaml updated
- [ ] Pipeline tasks updated (conditional)

---

## Validation Scorecard

| Criteria | Max | Score |
|----------|-----|-------|
| File Existence | 5 | ___ |
| File Completeness | 4 | ___ |
| Archon Project | 2 | ___ |
| Archon Documents | 5 | ___ |
| Tasks File Valid | 3 | ___ |
| Complexity Alignment | 1 | ___ |
| Document Consistency | 2 | ___ |
| **TOTAL** | **22** | ___ |

**Status:** 20-22=EXCELLENT | 16-19=GOOD | 11-15=ACCEPTABLE | <11=INCOMPLETE

---

## Critical Failures (Immediate Fix)

- [ ] MCP not verified | verification_state not loaded | Phase 2C not COMPLETED
- [ ] Write tool used instead of BMAD workflow (PRD) or Task tool (agents)
- [ ] Agents spawned sequentially (Step 5 requires parallel)
- [ ] Archon tasks created | Separate project created
- [ ] Missing Codebase Analysis/Applied lines in outputs
- [ ] Budget exceeded without rebalancing
- [ ] 03_tasks.yaml not generated

---

**Minimum Pass:** All steps completed | All 5 files | Budget complied | Score ≥ 16/22

**Quality Score:** ___ / 22 | **Task Count:** ___ / ___ | **Date:** {{date}}
