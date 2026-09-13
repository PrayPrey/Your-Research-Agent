# Anonymous Pipeline Resume Reference (Auto-Responder + Independent Artifact Verifier)

---

## Pipeline Overview

```
Phase 0 (Brainstorm) → Phase 1 (Research) → Phase 2A-Dialogue (Hypothesis Generation)
→ Phase 2B (Planning)
→ (Phase 2C → Phase 3 → Phase 4) × N [Hypothesis Loop]
→ Phase 4.5 (Synthesis) → [Phase 5 (Baseline)] → Phase 6 (Paper) → Phase 6.5 (Review) → Phase 6.5.1 (LaTeX/PDF)
```

**Note:** Phase 5 is OPTIONAL — skipped when `pipeline_options.skip_baseline_comparison=true` in module.yaml.
When skipped, pipeline goes directly from Phase 4.5 (Synthesis) → Phase 6 (Paper Writing).

**Note:** Phase 2A-Extended has been **merged into Phase 2A-Dialogue**.
Phase 2A now includes all stages: Gap Selection → Round Table → Synthesis (with Variable Inference + H0) → Advocate-Critic Refinement.

---

## Step ↔ Phase Mapping

| Step | Phase | Output Files |
|------|-------|--------------|
| 0 | Initialize & Resume Detection | - |
| 1 | Phase 0 (Brainstorm) | `00_brainstorm_session.md` |
| 2 | Phase 1 (Research) | `01_targeted_research.md`, `01_targeted_research_full.md` |
| 3 | Phase 2A-Dialogue | `discussion_log.md`, `01_round_table/`, `02_synthesis.yaml`, `03_refinement.yaml`, `03_refinement.md` |
| 4 | Phase 2B (Planning) | `02b_verification_plan.md`, `verification_state.yaml` |
| 5 | Hypothesis Loop (2C→3→4) | `h-*/` folders, `04_checkpoint.yaml` |
| 6 | Phase 4.5 (Synthesis) | `045_validated_hypothesis.md` |
| 7 | Phase 5 (Baseline) — OPTIONAL | `05_baseline_checkpoint.yaml` |
| 8 | Phase 6 (Paper) | `paper/06_paper.md` |
| 9 | Phase 6.5 (Review) | `paper/06_paper_final.md` |
| 10 | Phase 6.5.1 (LaTeX/PDF) | `paper/overleaf/main.pdf` |

---

## Resume Detection Logic

> **Scope**: All file paths below are relative to the **current local research folder**.
> (e.g., `docs/youra_research/{timestamp}_youra_research/`)
> The hook automatically detects the active research folder from context.

Check files in **reverse order** (latest phase first):

```
1. verification_state.yaml exists?
   └─ YES: Check pipeline.status and pipeline.current_phase
       ├─ status=COMPLETED or PAPER_GENERATED → Done
       ├─ current_phase="Phase 6.5.1" → Step 10
       ├─ current_phase="Phase 6.5" → Step 9
       ├─ current_phase="Phase 6" → Step 8
       ├─ current_phase="Phase 5" → Step 7
       ├─ current_phase="Phase 5 Skipped" → Step 8 (Phase 6)
       ├─ current_phase="Hypothesis Loop Complete" → Step 6 (Phase 4.5)
       ├─ current_phase in [2C, 3, 4] → Step 5 (Hypothesis Loop)
       └─ current_phase="Phase 2B" → Step 4

2. 03_refinement.yaml OR 02_synthesis.yaml exists?
   └─ 03_refinement.yaml has convergence.final_hypothesis → Step 4 (Phase 2B)
   └─ else → Step 3 (Phase 2A-Dialogue, continue refinement)

3. 01_round_table/ exists? → Step 3 (Phase 2A-Dialogue, continue from synthesis)

4. 01_targeted_research.md exists? → Step 3 (Phase 2A-Dialogue)

5. 00_brainstorm_session.md exists? → Step 2 (Phase 1)

6. Nothing exists → Step 1 (Phase 0)
```

---

## MANDATORY: Archive Execution on Routing

<critical>
**THIS SECTION MUST BE CHECKED FIRST BEFORE ANY RESUME ACTION**

When `pipeline.status = "ROUTED"` is detected, archive operations MUST be executed
BEFORE proceeding to the routing target (Phase 0 or Phase 2A-Dialogue).

**Failure to archive = Old files mix with new research = CORRUPTED PIPELINE**
</critical>

### Step 1: Detect Routing Status

Check `pipeline.status` in verification_state.yaml:

| Status | Action |
|--------|--------|
| `"ROUTED"` | **STOP** - Execute archive FIRST (Step 2-4) |
| `"ACTIVE"` | Skip this section, proceed to normal resume |
| `"COMPLETED"` | Pipeline done |

### Step 2: Check If Archive Already Exists

Look for `_archive/` folder in research folder:

| Condition | Action |
|-----------|--------|
| `_archive/` folder EXISTS | Skip to Step 4 |
| `_archive/` folder NOT FOUND | **Execute Step 3 NOW** |

### Step 3: Execute Archive (MANDATORY)

**DO NOT SKIP THIS STEP. EXECUTE IMMEDIATELY.**

**For Phase 0 Routing:**
1. Create folder: `_archive/`
2. Move ALL files to archive folder:
   - `00_brainstorm_session.md`
   - `01_targeted_research*.md`
   - `01_round_table/`
   - `02_synthesis.yaml`
   - `discussion_log.md`
   - `03_refinement.yaml`
   - `03_refinement.md`
   - `verification_state.yaml`
   - `h-*/` folders
   - ALL other research files
3. Create `_ARCHIVED.md` marker file with failure context

**For Phase 2A-Dialogue Routing:**
1. Create folder: `_archive/`
2. Move Phase 2A+ files ONLY:
   - `01_round_table/`
   - `02_synthesis.yaml`
   - `discussion_log.md`
   - `03_refinement.yaml`
   - `03_refinement.md`
   - `02b_verification_plan*.md`
   - `verification_state.yaml`
   - `h-*/` folders
3. PRESERVE these files (do NOT move):
   - `00_brainstorm_session.md`
   - `01_targeted_research*.md`
   - `papers/` folder
4. Create `_ARCHIVED.md` marker file with supersede context

### Step 4: Proceed to Routing Target

**ONLY AFTER archive is confirmed**, proceed to:

| Routing Target | Resume Action |
|----------------|---------------|
| Phase 0 | Start Step 1 (fresh brainstorm) |
| Phase 2A-Dialogue | Start Step 3 (new hypothesis generation) |

---

## Gate System

### MUST_WORK Gate (Phase 4)
| Result | Action | Serena Memory |
|--------|--------|---------------|
| PASS | → Continue to next hypothesis | - |
| MODIFIED | → New hypothesis variant, retry | - |
| FAIL | → Route to Phase 0 (Step 1) | `failure_{h_id}.md` |
| PARTIAL (max attempts) | → Route to Phase 2A-Dialogue (Step 3) | `pivot_{h_id}_{new_id}.md` |

### DETERMINES_SUCCESS Gate (Phase 5)
| Result | Action | Serena Memory |
|--------|--------|---------------|
| PASS | → Phase 6 (Step 8) | - |
| PARTIAL | → Route to Phase 0 (Step 1) | `phase5_failure_{h_id}.md` |
| SKIPPED | → Phase 6 (Step 8) directly | - (skip_baseline_comparison=true) |

---

## Artifact Verification (Independent Verifier)

**Artifact verification is handled by `pipeline_artifact_verifier.py`.**
The hook calls this script and includes its full report in the LLM prompt.

When the report shows `Fabrication detected: True`:
- The report includes a **RE-EXECUTION PLAN** with per-hypothesis restart points
- Follow the FORCE_REEXECUTE instructions in the LLM prompt (auto_responder_full.py)
- Key: if Phase 3 artifacts exist, Phase 4 MUST reference them for code generation

---

## verification_state.yaml Key Fields

```yaml
pipeline:
  status: "ACTIVE" | "COMPLETED" | "PAPER_GENERATED"
  current_phase: "Phase 2B" | "Phase 2C" | ... | "Pipeline Complete"
  current_hypothesis: "H-E1" | "ALL_COMPLETE"
  hypotheses_complete: 3          # count of completed
  hypotheses_total: 5             # total count
  timestamp: "2026-03-02T..."

hypotheses:                       # list format
  - id: "H-E1"
    type: "existence"
    order: 1
    status: "PASS" | "READY" | "IN_PROGRESS"
    gate_result: "PASS" | "PARTIAL" | "FAIL"
    dependencies: []

gate_results:
  H-E1:
    decision: "PASS"
    confidence: "HIGH"
    timestamp: "..."

phase5_plan:
  enabled: false                  # true when baseline comparison is active
```

---

## 04_checkpoint.yaml Key Fields (Hypothesis Loop)

```yaml
hypothesis_id: "H-E1"
phase: "Phase 4 - Coding & Validation"
status: "in_progress"
started_at: "2026-03-02T..."

tasks:                            # flat dict keyed by task ID
  H-E1-T1:
    status: "completed" | "pending" | "in_progress"
    attempts: 0
    last_error: null
  H-E1-T2:
    status: "pending"
    attempts: 0
    last_error: null

metrics:
  worst_group_acc: null           # populated after experiment execution
  attention_shift: null

gate_result:
  decision: null                  # PASS/PARTIAL/FAIL (set after evaluation)
  timestamp: null
  justification: null

retry_count: 0
max_retries: 3
```

---

## Resume Prompt Template

```markdown
## Workflow
Read and follow: bmad-custom-src/custom/modules/youra-research/workflows/full-pipeline-unattended/instructions.md

## Auto-Resume Context
- Pipeline: docs/youra_research/{folder_name}
- Current Phase: {Phase X} ({Hypothesis ID})
- Progress: {N/M} hypotheses complete
- Last checkpoint: {task_id} {status}
- verification_state.yaml status: {status}
- Refer to Archon task management for task tracking

## Stop Reason
{Why pipeline paused - from recent conversation}

## Resume Instructions
**ACTION: CONTINUE IMMEDIATELY - DO NOT ASK FOR PERMISSION**
- Skip to: Step {N} ({Phase Name})
- Load hypothesis: {H-ID}
- Continue from: {specific task or action}
- Gate status: {if applicable}
- **Execute immediately without asking for confirmation**
- If experiments pending → RUN THEM NOW
- If code ready → EXECUTE IT NOW
- If phase ready → START IT NOW
```

---

## Research Folder Structure

```
docs/youra_research/{timestamp}_youra_research/
├── 00_brainstorm_session.md      # Phase 0 output
├── 01_targeted_research.md       # Phase 1 output (compact)
├── 01_targeted_research_full.md  # Phase 1 output (full)
├── papers/                       # Downloaded papers (Phase 2A input)
│   └── *.md                      # Converted paper markdown files
├── 01_round_table/               # Phase 2A output (Round Table)
│   ├── 00_metadata.yaml
│   ├── round_0.yaml
│   ├── convergence.yaml
│   └── final_opinions.yaml
├── 02_synthesis.yaml             # Phase 2A output (Synthesis + H0)
├── discussion_log.md              # Phase 2A output (Full discussion transcript)
├── 03_refinement.yaml            # Phase 2A output (Refinement)
├── 02b_verification_plan.md      # Phase 2B output
├── verification_state.yaml       # Pipeline state (Phase 2B+)
├── h-m1/                         # Hypothesis folder
│   ├── 02c_experiment_brief.md   # Phase 2C output
│   ├── 03_implementation/        # Phase 3 outputs
│   ├── 03_tasks.yaml             # Phase 3 task list
│   ├── 04_checkpoint.yaml        # Phase 4 task tracking
│   ├── 04_validation.md          # Phase 4 validation report
│   └── 05_baseline_checkpoint.yaml # Phase 5 state
├── h-m2/                         # Next hypothesis folder
├── 045_validated_hypothesis.md   # Phase 4.5 synthesis
├── _archive/                     # Archived files (on routing)
└── paper/                        # Phase 6+ outputs
    ├── 06_paper.md
    ├── 06_paper_final.md
    ├── review/
    └── overleaf/                 # Phase 6.5.1 output
        └── main.pdf
```

---

## Hypothesis Loop Detail (Step 5)

```
For each sub-hypothesis in dependency order:
  │
  ├─ Phase 2C: Experiment Design
  │   └─ Output: h-{id}/02c_experiment_brief.md
  │
  ├─ Phase 3: Implementation Planning
  │   └─ Output: h-{id}/03_implementation/, 03_tasks.yaml
  │
  └─ Phase 4: Coding & Validation
      ├─ Execute tasks from 03_tasks.yaml
      ├─ Track progress in 04_checkpoint.yaml
      └─ Gate evaluation (MUST_WORK)
          ├─ PASS → Next hypothesis
          ├─ PARTIAL → Retry or Route
          └─ FAIL → Route to Phase 0

After ALL sub-hypotheses complete:
  └─ workflow.sub_hypotheses_complete = true
  └─ Proceed to Step 6 (Phase 4.5 Synthesis)
  └─ Then Step 7 (Phase 5, or skip to Step 8 if skip_baseline_comparison=true)
```

### Phase 5 Transition Conditions (IMPORTANT)

To proceed to Phase 5 (Baseline Comparison), **ALL of the following conditions must be satisfied**:

1. **All Sub-Hypotheses Complete**: Every sub-hypothesis (H-M1, H-M2, ...) defined in the
   Hypothesis Loop must have completed Phase 2C → Phase 3 → Phase 4.

2. **Gate Conditions Met**: Each sub-hypothesis's MUST_WORK Gate must have a final PASS status.
   - PASS: Validation successful → Proceed to next hypothesis
   - MODIFIED: Hypothesis modified and retried → Must eventually reach PASS
   - PARTIAL/FAIL: Routing triggered → Cannot proceed to Phase 5

3. **Pipeline State Verification**: In `verification_state.yaml`:
   - `pipeline.hypotheses_complete == pipeline.hypotheses_total`
   - All `hypotheses[].status: PASS`
   - All `hypotheses[].gate_result: PASS` (not PASS_THEORETICAL)

**If even a single sub-hypothesis is incomplete or has a failed Gate status, Phase 5 cannot proceed.**

---

## CRITICAL: Task Tool Usage Restriction

**Every resume prompt MUST include this instruction to Claude:**

```
⚠️ Task Tool Pre-Call Check (MANDATORY):
Before EVERY Task tool call, verify subagent_type is in this whitelist:
  - perspective-novelty, perspective-falsifiability, perspective-significance, perspective-plausibility
  - synthesis-agent, refiner-advocate, refiner-critic
  - architecture-agent, logic-agent, configuration-agent
  - validator-agent, baseline-validator-agent
  - adversary-agent, revision-agent

If subagent_type is NOT in this list (e.g. "general-purpose") → DO NOT call Task tool.
Instead, execute the workflow INLINE (read instructions.md and run steps yourself).
```

**Why this matters:**
Phase workflows (0, 1, 2A, 2B, 2C, 5, 6, 6.5) and the Hypothesis Loop must be
executed INLINE by Claude, never spawned as Task agents. Only the 14 sub-agents
listed above are permitted to use the Task tool.

---

## CRITICAL: Dynamic Phase Detection

**The actual step/phase MUST be determined from the state file contents PROVIDED in this prompt.**

The hook already includes the full contents of:
- verification_state.yaml (under "### verification_state.yaml" section)
- 04_checkpoint.yaml (under "### 04_checkpoint.yaml" section, if exists)

### How to Determine Current Phase:

Look at the PROVIDED verification_state.yaml content and find:
- `pipeline.current_phase` → The current phase (e.g., "Phase 2B", "Phase 4", "Pipeline Complete")
- `pipeline.status` → Pipeline status (ACTIVE, COMPLETED, PAPER_GENERATED)
- `pipeline.current_hypothesis` → Which hypothesis is active (e.g., "H-E1", "ALL_COMPLETE")
- `hypotheses[]` → List of all hypotheses with status and gate_result

If in Phase 4, also look at the PROVIDED 04_checkpoint.yaml content:
- `status` → Checkpoint status (in_progress, complete_theoretical, etc.)
- `tasks` → Dict of tasks keyed by ID (e.g., H-E1-T1) with their status
- `gate_result.decision` → Gate decision (PASS/PARTIAL/FAIL or null)

### Key Fields to Extract:

From verification_state.yaml:
- Current Phase: `pipeline.current_phase`
- Pipeline Status: `pipeline.status`
- Current Hypothesis: `pipeline.current_hypothesis`
- Hypothesis Progress: `pipeline.hypotheses_complete` / `pipeline.hypotheses_total`
- Per-hypothesis: `hypotheses[].status`, `hypotheses[].gate_result`

From 04_checkpoint.yaml (Phase 4 only):
- Tasks: count completed vs total in `tasks` dict
- Gate: `gate_result.decision`
- Retry Count: `retry_count`

---
