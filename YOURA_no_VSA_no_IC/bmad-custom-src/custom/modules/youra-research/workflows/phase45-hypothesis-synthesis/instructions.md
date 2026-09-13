# Phase 4.5: Hypothesis Synthesis 

> **Position:** Phase 4 (Hypothesis Loop) → **Phase 4.5** → Phase 5/6
> **Purpose:** Refine hypotheses based on experiment evidence; serve as SINGLE information gateway to Phase 6
> **Input:** All `h-*/04_validation.md`, `h-*/04_checkpoint.yaml`, `h-*/03_tasks.yaml`, `h-*/02c_experiment_brief.md`, `03_refinement.yaml`, `verification_state.yaml`
> **Output:** `045_validated_hypothesis.md`
> **Architecture:** Step-based (8 steps)

---

## Core Philosophy

Phase 2A theories are **motivating theories** — they may contain speculative explanations to generate testable hypotheses. Phase 4.5 transforms these into **evidence-grounded claims** by:

1. Keeping ONLY experiment-supported claims
2. Removing or weakening unsupported explanations and overclaims
3. Connecting observed phenomena to existing literature
4. Defining principled limitations based on actual failure analysis
5. Deriving future work from untested alternatives and unverified assumptions

**Phase 4.5 is the SINGLE source for Phase 6 Paper Writing.** Phase 6 does NOT read `h-*/04_validation.md` directly.

---

## Overview

| Step | Name | Purpose |
|------|------|---------|
| **01** | Initialize | Load state, verify preconditions, collect hypothesis data |
| **02** | Prediction-Result Alignment | Map P1/P2/P3 to experiment results, verify causal mechanism |
| **03** | Hypothesis Refinement | Remove overclaims, generate refined core statement |
| **04** | Theoretical Interpretation | Connect to literature, analyze unexpected findings |
| **05** | Limitations & Scope | Define principled boundary conditions |
| **06** | Future Work | Derive results-grounded future directions |
| **07** | Generate Document | Assemble `045_validated_hypothesis.md` |
| **08** | Finalize | Update state, display completion summary |

---

## Preconditions

Before executing Phase 4.5, verify:

1. **All sub-hypotheses completed Phase 4:**
   - `verification_state.yaml` → `workflow.sub_hypotheses_complete = true`
   - All sub-hypotheses in final states: VALIDATED, COMPLETED, FAILED, BLOCKED, SUPERSEDED

2. **Required files exist:**
   - At least one `h-*/04_validation.md`
   - At least one `h-*/04_checkpoint.yaml`
   - At least one `h-*/03_tasks.yaml` (Phase 3 task definitions)
   - At least one `h-*/02c_experiment_brief.md` (Phase 2C experiment design)
   - `03_refinement.yaml` (original hypothesis)
   - `verification_state.yaml` (pipeline state)

---

## Execution Rules

### UNATTENDED Mode
```
UNATTENDED = EXECUTE_ALL_STEPS + NO_USER_CONFIRMATION
- Execute ALL 8 steps sequentially
- Skip ONLY [Y/N] prompts
- NEVER skip MCP tool calls or step file reading
```

### Step Processing
1. **READ COMPLETELY**: Read each step file fully before executing
2. **FOLLOW SEQUENCE**: Steps 01-08 in order
3. **ACCUMULATE STATE**: Each step builds on previous step outputs
4. **SAVE PROGRESS**: Mental state carries across steps (no checkpoint file needed — single session)

### MCP Usage
- **Serena**: Code/experiment analysis (step-01), session memory (step-08)
- **Semantic Scholar**: Literature search for theoretical interpretation (step-04)
- **ClearThought**: Competing hypothesis analysis (step-03, step-04)
- **Archon**: Task status update (step-08)

---

## Error Handling

| Error | Action |
|-------|--------|
| `verification_state.yaml` not found | EXIT — Run Phase 2B first |
| `workflow.sub_hypotheses_complete = false` | EXIT — Run hypothesis-loop first |
| No `h-*/04_validation.md` found | EXIT — No experiments completed |
| `03_refinement.yaml` not found | EXIT — Phase 2A-Dialogue not completed |
| Semantic Scholar MCP unavailable | WARN — Skip literature connection, continue |
| ClearThought MCP unavailable | WARN — Use manual analysis, continue |
| Parsing error in validation file | WARN — Continue with available data |

---

## Quality Checklist

Before completing Phase 4.5, verify:

- [ ] All `h-*/04_validation.md` files read and processed
- [ ] All `h-*/04_checkpoint.yaml` files read and processed
- [ ] All `h-*/03_tasks.yaml` files read (planned metrics and success criteria)
- [ ] All `h-*/02c_experiment_brief.md` files read (experiment design, variables, controls)
- [ ] `03_refinement.yaml` loaded (original hypothesis)
- [ ] Planned-vs-actual comparison completed (deviation types classified)
- [ ] Every prediction (P1, P2, P3) mapped to experiment results with status
- [ ] Causal mechanism steps verified against evidence
- [ ] Refined core statement generated (differs from original)
- [ ] Overclaims identified and removed/weakened
- [ ] Assumption verification status assigned
- [ ] Theoretical interpretation connected to literature
- [ ] Unexpected findings analyzed with competing explanations
- [ ] Limitations are principled (not superficial)
- [ ] Future work grounded in experiment results
- [ ] Section 8 (Implications for Phase 6) complete with all 5 subsections
- [ ] `045_validated_hypothesis.md` written
- [ ] `verification_state.yaml` updated

---

## Invocation

**Full Pipeline:**
- Automatically invoked between hypothesis-loop and Phase 5/6

**Standalone:**
```
/phase45-hypothesis-synthesis
```

**Launcher:**
```bash
python .claude/hooks/run_phase45.py --research-folder <path>
```

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Load config from `{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml` and resolve `research_output_path`, `research_folder`.

### 2. First Step

Load, read the full file, and execute `{installed_path}/steps/step-01-init.md` to begin the workflow.

---

*Evidence-refined hypothesis with theoretical interpretation*
