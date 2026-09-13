# YouRA Hook System

Automation infrastructure for running the YouRA research pipeline in fully unattended mode.

## Architecture

```text
run_total_youra.py (final end-to-end orchestrator)
    |
    +- Part 1: run_pipeline_to_phase4.py (Reflection loop + state persistence)
    |   +- run_early_pipeline.py (sequential Phase 0 -> 1 -> 2A -> 2B execution)
    |   |   +- run_phase0.py / run_phase1.py / run_phase2a.py / run_phase2b.py
    |   +- run_hypothesis_loop.py (per-hypothesis Phase 2C -> 3 -> 4 loop)
    |   |   +- run_phase2c.py / run_phase3.py / run_phase4.py
    |   +- automatic return on ROUTED:
    |       +- "Phase 0"          -> run_early_pipeline.py from the beginning
    |       +- "Phase 2A-Dialogue" -> run_phase2a.py + run_phase2b.py only
    |       +- on failure, save reflection_state.json so execution can resume
    |
    +- Part 2: run_post_experiment.py (post-experiment pipeline)
        +- run_phase45.py -> [run_phase5.py] -> run_phase6.py -> run_phase65.py -> run_phase651.py
            +- [run_phase_refine.py] when --enable-refine is set
                +- tone_prompts/refine.md (prompt loading)
                +- md_to_pdf.py (automatic LaTeX + PDF conversion)

run_phase*.py (Launcher) -> hook_router.py (Router) -> phase_auto_responder.py (Responder)
    Runs Claude CLI             Routes Stop events         GPT-5.2-based auto response
```

Whenever Claude CLI stops mid-run, GPT-5.2 through OpenRouter analyzes the conversation, creates a resume prompt, and continues Claude automatically.

## Quick Start

### Full Pipeline: Phase 0 Through Phase 6.5.1 [+ Refine]

Runs everything from research idea to final paper review in one command.
When `--enable-refine` is set, the pipeline also refines the paper and generates a PDF after Phase 6.5.1.

```bash
# Text input
python .claude/hooks/run_total_youra.py "Weak supervision for image classification" --research-folder docs/youra_research/20260304_scsl

# Existing research folder
python .claude/hooks/run_total_youra.py docs/research_idea.md \
    --research-folder docs/youra_research/20260304_scsl

# Reflection count control
python .claude/hooks/run_total_youra.py docs/research_idea.md --max-reflections 5   # maximum 5
python .claude/hooks/run_total_youra.py docs/research_idea.md --max-reflections 0   # no Reflection
python .claude/hooks/run_total_youra.py docs/research_idea.md --max-reflections -1  # unlimited

# Include Phase 5; run_phase5.py must exist
python .claude/hooks/run_total_youra.py docs/research_idea.md --enable-phase5

# Include paper refinement after Phase 6.5.1
python .claude/hooks/run_total_youra.py docs/research_idea.md --enable-refine

# Per-phase timeout settings
python .claude/hooks/run_total_youra.py docs/research_idea.md \
    --timeout-phase0 1800 --timeout-hypothesis-loop 28800 --timeout-phase6 10800
```

### Resume From The Middle (`--resume-from`)

If intermediate outputs already exist from an earlier phase run, use `--resume-from` to continue from a specific phase. Resume points other than `phase0` require `--research-folder`.

```bash
# Resume from Phase 0 after a failure such as rate limit during Reflection
python .claude/hooks/run_total_youra.py dummy \
    --resume-from phase0 --research-folder docs/youra_research/20260304_scsl

# Resume from Phase 2B when Phase 0/1/2A outputs already exist
python .claude/hooks/run_total_youra.py dummy \
    --resume-from phase2b --research-folder docs/youra_research/20260304_scsl

# Resume from the Hypothesis Loop when Phase 0 through 2B outputs already exist
python .claude/hooks/run_total_youra.py dummy \
    --resume-from hypothesis-loop --research-folder docs/youra_research/20260304_scsl

# Resume from Phase 4.5 after Part 1 is complete
python .claude/hooks/run_total_youra.py dummy \
    --resume-from phase45 --research-folder docs/youra_research/20260304_scsl

# Resume from Phase 6 after Phase 4.5 is complete
python .claude/hooks/run_total_youra.py dummy \
    --resume-from phase6 --research-folder docs/youra_research/20260304_scsl

# Run only Refine after Phase 6.5.1 is complete
python .claude/hooks/run_total_youra.py dummy \
    --resume-from refine --research-folder docs/youra_research/20260304_scsl \
    --enable-refine
```

Supported `--resume-from` values:

| Phase | Skipped Phases | Part 1 Runs | Part 2 Runs |
|-------|----------------|:-----------:|:-----------:|
| `phase0` | none | O | O |
| `phase1` | Phase 0 | O, starting at Phase 1 | O |
| `phase2a` | Phase 0, 1 | O, starting at Phase 2A | O |
| `phase2b` | Phase 0, 1, 2A | O, starting at Phase 2B | O |
| `hypothesis-loop` | Phase 0, 1, 2A, 2B | O, loop only | O |
| `phase45` | all of Part 1 | X | O |
| `phase5` | Part 1 + Phase 4.5 | X | O, starting at Phase 5 |
| `phase6` | Part 1 + Phase 4.5/5 | X | O, starting at Phase 6 |
| `phase65` | Part 1 + Phase 4.5/5/6 | X | O, starting at Phase 6.5 |
| `phase651` | Part 1 + Phase 4.5/5/6/6.5 | X | O, Phase 6.5.1 only |
| `refine` | Part 1 + Phase 4.5/5/6/6.5/6.5.1 | X | O, Refine only with `--enable-refine` |

If `--resume-from` is omitted, the full pipeline starts from Phase 0.

## Reflection State Persistence (`reflection_state.json`)

If Reflection fails because of a rate limit, network error, or similar interruption, `reflection_count` is saved automatically to `.cache/reflection_state.json`. Restarting with the same `--research-folder` restores the previous Reflection count.

Behavior:
- On Reflection, save `reflection_count`, `research_folder`, and routing metadata to `reflection_state.json`.
- On restart, restore `reflection_count` when `--research-folder` matches the saved folder, even without `--resume-from`.
- If the saved folder differs, start from `reflection_count = 0` to avoid cross-pipeline contamination.
- On normal pipeline completion, delete `reflection_state.json`.
- When `--resume-from` points to a Part 2 phase such as `phase45` or `phase6`, Part 1 is skipped and any stale `reflection_state.json` is cleaned up.
- Reflection is only recorded when a MUST_WORK gate ends as ROUTED. Ctrl-C interruptions and per-phase timeout exits are separate exit paths and do not update `reflection_state.json`, so a resumed count of 0 is expected in those cases.

Example: resume after rate limit during Reflection.

```bash
# 1. Initial run -> H-M1 MUST_WORK FAIL -> Reflection 1 -> Phase 0 restart -> rate limit failure
python .claude/hooks/run_total_youra.py tasks_youra/idea.md
# Log: "Resume with: --resume-from phase0 --research-folder <path>"

# 2. Resume after rate limit resets; reflection_count=1 is preserved
python .claude/hooks/run_total_youra.py dummy \
    --resume-from phase0 --research-folder <path>
```

Pipeline flow:

```text
Part 1: run_pipeline_to_phase4.py
  Phase 0 -> 1 -> 2A -> 2B -> Hypothesis Loop (2C -> 3 -> 4 x N)
                                    |
                                    +- COMPLETE -> proceed to Part 2
                                    +- ERROR -> stop immediately
                                    +- INCOMPLETE -> stop
                                    +- ROUTED -> Reflection, return to Phase 0 or 2A and retry
                                         |    save reflection_state.json
                                         |    print resume guidance on failure
                    +--------------------+
                    v
Part 2: run_post_experiment.py
  Phase 4.5 -> [Phase 5] -> Phase 6 -> Phase 6.5 -> Phase 6.5.1
                                                      |
                                                      +- COMPLETE -> full pipeline complete
```

Exit codes:

| Code | Meaning | stdout JSON status |
|------|---------|--------------------|
| 0 | Full pipeline completed | `COMPLETE` |
| 1 | Fatal error in Part 1 or Part 2 | `ERROR` |
| 2 | Part 1 Reflection limit reached | `REFLECTION_LIMIT_REACHED` |
| 3 | Part 1 hypotheses incomplete | `INCOMPLETE` / `BLOCKED` |

SELF_MODIFY is handled internally by `run_hypothesis_loop.py`.

## Partial Runs

### Part 1 Only: Phase 0 Through Phase 4

Runs through hypothesis validation only. A MUST_WORK hypothesis failure automatically returns through Reflection.

```bash
python .claude/hooks/run_pipeline_to_phase4.py docs/research_idea.md
python .claude/hooks/run_pipeline_to_phase4.py docs/research_idea.md --max-reflections 5
python .claude/hooks/run_pipeline_to_phase4.py docs/research_idea.md \
    --research-folder docs/youra_research/20260304_scsl

python .claude/hooks/run_pipeline_to_phase4.py dummy \
    --resume-from phase0 --research-folder docs/youra_research/20260304_scsl
python .claude/hooks/run_pipeline_to_phase4.py dummy \
    --resume-from phase2b --research-folder docs/youra_research/20260304_scsl
python .claude/hooks/run_pipeline_to_phase4.py dummy \
    --resume-from hypothesis-loop --research-folder docs/youra_research/20260304_scsl
```

Part 1 `--resume-from` options: `phase0`, `phase1`, `phase2a`, `phase2b`, `hypothesis-loop`.

| Code | Meaning | stdout JSON status |
|------|---------|--------------------|
| 0 | All hypotheses validated | `COMPLETE` |
| 1 | Fatal error | `ERROR` |
| 2 | Reflection limit reached | `REFLECTION_LIMIT_REACHED` |
| 3 | Incomplete hypotheses | `INCOMPLETE` / `BLOCKED` |

### Part 2 Only: Phase 4.5 Through Phase 6.5.1

Runs only the post-experiment pipeline after hypothesis validation. Requires a research folder with a completed Hypothesis Loop.

```bash
python .claude/hooks/run_post_experiment.py --research-folder docs/youra_research/20260304_scsl
python .claude/hooks/run_post_experiment.py --research-folder <path> --enable-phase5
python .claude/hooks/run_post_experiment.py --research-folder <path> \
    --timeout-phase45 7200 --timeout-phase6 10800
python .claude/hooks/run_post_experiment.py --research-folder <path> --enable-refine
python .claude/hooks/run_post_experiment.py --research-folder <path> --resume-from phase6
python .claude/hooks/run_post_experiment.py --research-folder <path> --resume-from phase65
python .claude/hooks/run_post_experiment.py --research-folder <path> --resume-from refine --enable-refine
```

Part 2 `--resume-from` options: `phase45`, `phase5`, `phase6`, `phase65`, `phase651`.

Prerequisites: `verification_state.yaml` and at least one `h-*/04_validation.md`.

| Code | Meaning |
|------|---------|
| 0 | Phase 4.5 -> [5] -> 6 -> 6.5 -> 6.5.1 completed |
| 1 | Phase failure or missing prerequisites |

## Early Pipeline: Phase 0 Through Phase 2B

Runs only Phase 0 through 2B sequentially. Each phase output is verified and retried automatically on failure.

```bash
python .claude/hooks/run_early_pipeline.py docs/research_idea.md

python .claude/hooks/run_early_pipeline.py docs/research_idea.md \
    --research-folder docs/youra_research/20260304_scsl \
    --timeout-phase0 1800 --timeout-phase2b 10800
```

After completion, stdout prints the research folder path. You can then run the Hypothesis Loop manually:

```bash
python .claude/hooks/run_hypothesis_loop.py --research-folder <printed path>
```

## Individual Phase Launchers

### Phase 0: Brainstorm

Accepts either a research idea file or a plain text topic string.

```bash
python .claude/hooks/run_phase0.py docs/research_idea.md
python .claude/hooks/run_phase0.py "Weak supervision for image classification"
python .claude/hooks/run_phase0.py docs/research_idea.md --research-folder docs/youra_research/20260304_scsl
python .claude/hooks/run_phase0.py docs/research_idea.md --timeout 1800
```

### Phase 1: Targeted Research

```bash
python .claude/hooks/run_phase1.py --research-folder docs/youra_research/20260304_scsl
python .claude/hooks/run_phase1.py    # auto-detect the most recent folder
```

### Phase 2A: Hypothesis Dialogue

```bash
python .claude/hooks/run_phase2a.py --research-folder <path>
python .claude/hooks/run_phase2a.py --research-folder <path> --timeout 5400
```

### Phase 2B: Verification Planning

```bash
python .claude/hooks/run_phase2b.py --research-folder <path>
python .claude/hooks/run_phase2b.py --research-folder <path> --timeout 7200
```

### Hypothesis Loop: Phase 2C -> 3 -> 4

Reads READY hypotheses from `verification_state.yaml` and runs Phase 2C, 3, and 4 in separate Claude CLI sessions for each hypothesis.

```bash
python .claude/hooks/run_hypothesis_loop.py --research-folder <path>
python .claude/hooks/run_hypothesis_loop.py --research-folder <path> --timeout 14400
```

Flow:
1. Queue READY/IN_PROGRESS hypotheses from `verification_state.yaml` in dependency order.
2. Run Phase 2C -> 3 -> 4 for each hypothesis.
3. Process the Phase 4 gate result:
   - `PASS`: satisfy dependent prerequisites and continue.
   - `ROUTED`: emit routing information as stdout JSON and stop the loop with exit code 2.
   - `SELF_MODIFY`: mark the original completed; the new hypothesis variant is handled in the next loop iteration.
   - `FAILED`: recursively block dependent hypotheses and continue.
4. Exit with code 0 when all hypotheses complete.

Resume support: if interrupted, the loop detects IN_PROGRESS hypotheses and completed phases, then continues automatically.

Gate field compatibility: `gate` may be a string such as `gate: MUST_WORK` or a dict such as `gate: {type: MUST_WORK, satisfied: null}`.

### Phase 2C/3/4 Standalone

Use these when running a single hypothesis outside the Hypothesis Loop.

```bash
python .claude/hooks/run_phase2c.py --research-folder <path> --hypothesis h-e1
python .claude/hooks/run_phase3.py --research-folder <path> --hypothesis h-e1
python .claude/hooks/run_phase4.py --research-folder <path> --hypothesis h-e1 --timeout 7200
```

### Phase 4.5: Hypothesis Synthesis

```bash
python .claude/hooks/run_phase45.py --research-folder <path>
python .claude/hooks/run_phase45.py --research-folder <path> --timeout 5400
```

### Phase 6: Paper Writing

```bash
python .claude/hooks/run_phase6.py --research-folder <path>
python .claude/hooks/run_phase6.py --research-folder <path> --timeout 7200
```

### Phase 6.5: Adversarial Review

```bash
python .claude/hooks/run_phase65.py --research-folder <path>
python .claude/hooks/run_phase65.py --research-folder <path> --timeout 7200
```

### Phase 6.5.1: Overleaf LaTeX + PDF Generation

```bash
python .claude/hooks/run_phase651.py --research-folder <path>
python .claude/hooks/run_phase651.py --research-folder <path> --timeout 7200
```

### Refine: Paper Refinement

After Phase 6.5.1, refines `06_paper_final.md` into an evidence-grounded, neutral third-person version and generates LaTeX/PDF output.

- Model: `claude_model` from `auto_responder_config.yaml`.
- Prompt: loaded from `tone_prompts/refine.md`.
- Output: `{research_folder}/paper/refinement/06_paper_refinement.md` and `overleaf_refinement/main.pdf`.

```bash
# default
python .claude/hooks/run_phase_refine.py --research-folder <path>

# timeout
python .claude/hooks/run_phase_refine.py --research-folder <path> --timeout 1800
```

## Pipeline Connections

```text
run_total_youra.py (final end-to-end)
|
+- Part 1: run_pipeline_to_phase4.py (automatic Reflection loop + state persistence)
|  |
|  +- [initial run] run_early_pipeline.py
|  |  +- Phase 0 (run_phase0.py)
|  |  |  +- output: docs/youra_research/<timestamp>/00_brainstorm_session.md
|  |  +- Phase 1 (run_phase1.py)
|  |  |  +- output: 01_targeted_research.md, papers/*.md
|  |  +- Phase 2A (run_phase2a.py)
|  |  |  +- output: 03_refinement.yaml, 02_synthesis.yaml, 01_round_table/final_opinions.yaml
|  |  +- Phase 2B (run_phase2b.py)
|  |     +- output: verification_state.yaml, 02b_verification_plan.md
|  |
|  +- [loop] run_hypothesis_loop.py
|  |  +- for each READY hypothesis, in dependency order:
|  |     Phase 2C -> output: <h-id>/02c_experiment_brief.md
|  |     Phase 3  -> output: <h-id>/03_prd.md, 03_architecture.md, 03_logic.md, 03_config.md
|  |     Phase 4  -> output: <h-id>/04_validation.md, 04_checkpoint.yaml, code/
|  |
|  +- [Reflection on ROUTED] automatically return based on route_to
|     +- "Phase 0"          -> rerun all of run_early_pipeline.py
|     +- "Phase 2A-Dialogue" -> rerun run_phase2a.py + run_phase2b.py only
|     +- save reflection_state.json to preserve reflection_count
|     +- log resume guidance on failure
|
+- Part 2: run_post_experiment.py
   +- Phase 4.5 (run_phase45.py)
   |  +- output: 045_validated_hypothesis.md
   +- [Phase 5] (run_phase5.py, when --enable-phase5 is set)
   |  +- output: not implemented
   +- Phase 6 (run_phase6.py)
   |  +- output: paper/06_paper.md, paper/sections/*.md, paper/06_references.bib
   +- Phase 6.5 (run_phase65.py)
   |  +- output: paper/06_paper_final.md, paper/review/065_review_summary.md
   +- Phase 6.5.1 (run_phase651.py)
   |  +- output: paper/overleaf/main.tex, paper/overleaf/sections/*.tex, paper/overleaf/output.pdf
   +- [Refine] (run_phase_refine.py, when --enable-refine is set)
      +- output: paper/refinement/06_paper_refinement.md + overleaf_refinement/main.pdf
```

### Gate Behavior

| gate_result | gate_type | Behavior | Handler |
|---|---|---|---|
| `PASS` | any | Propagate dependent hypotheses and continue | hypothesis_loop internals |
| `SELF_MODIFY` | any | Mark original completed; process the new hypothesis variant in the next iteration | hypothesis_loop internals |
| `ROUTED_*` | `SHOULD_WORK` | Ignore routing, record limitation, continue | hypothesis_loop internals |
| `ROUTED_*` | `MUST_WORK` | Emit ROUTED JSON and stop loop with exit 2 | `pipeline_to_phase4` Reflection |
| `FAILED` | `SHOULD_WORK` | Record limitation and continue | hypothesis_loop internals |
| `FAILED` | `MUST_WORK` | Emit ROUTED JSON and stop loop with exit 2 | `pipeline_to_phase4` Reflection |

## Key Files

| File | Role |
|---|---|
| `run_total_youra.py` | Final end-to-end orchestrator for Part 1 + Part 2 |
| `run_pipeline_to_phase4.py` | Part 1: Phase 0 through 4 with Reflection loop and state persistence |
| `run_post_experiment.py` | Part 2: Phase 4.5 -> [5] -> 6 -> 6.5 -> 6.5.1 |
| `run_early_pipeline.py` | Sequential Phase 0 -> 1 -> 2A -> 2B execution with verification and retry |
| `run_phase0.py` through `run_phase2b.py` | Phase 0/1/2A/2B Claude CLI launchers |
| `run_phase2c.py`, `run_phase3.py`, `run_phase4.py` | Phase 2C/3/4 Claude CLI launchers for individual hypotheses |
| `run_hypothesis_loop.py` | External state machine for repeated Phase 2C -> 3 -> 4 execution |
| `run_phase45.py` | Phase 4.5 Claude CLI launcher for hypothesis synthesis |
| `run_phase6.py` | Phase 6 Claude CLI launcher for paper writing |
| `run_phase65.py` | Phase 6.5 Claude CLI launcher for adversarial review |
| `run_phase651.py` | Phase 6.5.1 Claude CLI launcher for Overleaf LaTeX + PDF generation |
| `run_phase_refine.py` | Paper refinement launcher (neutral evidence-grounded prose) |
| `md_to_pdf.py` | Markdown -> LaTeX (ICML 2025) -> PDF conversion after refinement |
| `tone_prompts/refine.md` | Refinement prompt template |
| `phase_output_verifier.py` | Phase output verification, YAML field checks, and retry prompt generation |
| `hook_router.py` | Routes Stop events to phase-specific or general responders |
| `phase_auto_responder.py` | GPT-5.2-based conversation analysis for resume/stop decisions |
| `phase*_auto_config.yaml` | Per-phase LLM settings, completion signals, and rate limits |
| `auto_responder_config.yaml` | General auto-responder settings |
| `auto_responder_full.py` | General auto-responder implementation |
| `.cache/active_phase.json` | Current active phase information while running |
| `.cache/reflection_state.json` | Persisted Reflection state |

## Output Verification & Retry

Each `run_phase*.py` calls `phase_output_verifier.py` after Claude CLI exits. If verification fails, the launcher retries automatically up to `MAX_RETRIES`, configured through `pipeline_retry.max_retries` in `auto_responder_config.yaml`.

Verification checks:

| Phase | File Checks | YAML Field Checks (`verification_state.yaml`) |
|-------|-------------|----------------------------------------------|
| Phase 0 | `00_brainstorm_session.md` with no unfilled placeholders and `<phase1-input>` present | - |
| Phase 1 | `01_targeted_research.md`, `01_targeted_research_full.md` | - |
| Phase 2A | `03_refinement.yaml`, `02_synthesis.yaml`, `final_opinions.yaml`, and related files | - |
| Phase 2B | `verification_state.yaml`, `02b_verification_plan.md` | - |
| Phase 2C | `02c_experiment_brief.md` | `experiment_design.status == COMPLETED`, `experiment_design.file != null` |
| Phase 3 | `03_prd.md`, `03_architecture.md`, `03_logic.md`, `03_config.md` | `implementation_planning.status == COMPLETED`, `implementation_planning.tasks_file != null` |
| Phase 4 | `04_validation.md`, `04_checkpoint.yaml` | `validation.status != NOT_STARTED`, `validation.result != null`, `gate.satisfied != null` |
| Phase 4.5 | `045_validated_hypothesis.md` with 8 required sections | `workflow.synthesis_completed == true` |
| Phase 6 | `paper/06_paper.md`, 8 section files, `06_references.bib`, `065_ground_truth.yaml`, `06_narrative_blueprint.yaml` | - |
| Phase 6.5 | `paper/06_paper_final.md`, `paper/review/065_review_summary.md`, `065_changelog.md`, `065_review_checkpoint.yaml`, `065_review_r1.md` | - |
| Phase 6.5.1 | `paper/overleaf/main.tex`, 8 section files, `references.bib`, optional `output.pdf` | - |

Retry flow:

```text
Claude CLI exits
  -> verify_and_write_json() creates .cache/{phase}_{h_id}_output_verify.json
  -> passed=false?
    -> build_retry_prompt() creates a prompt with failed checks and phase-specific fix instructions
    -> new Claude CLI retry session starts
    -> verify_and_write_json() runs again
    -> stop when passed=true
```

Phase stdout formats:

| Phase | stdout Last Line | Purpose |
|-------|------------------|---------|
| Phase 0 through 2B | research folder path string | passed to the next phase |
| Phase 2C/3 | research folder path string | not parsed directly by hypothesis_loop |
| Phase 4 | JSON gate result | used by hypothesis_loop for gate routing |
| Phase 4.5/6/6.5/6.5.1 | research folder path string | used by post_experiment |
| hypothesis_loop | JSON loop result | used by pipeline_to_phase4 for Reflection routing |
| pipeline_to_phase4 | JSON Part 1 result | used by run_total_youra to parse research_folder |
| post_experiment | JSON Part 2 result | used by run_total_youra for final result |

## Hook Flow

1. `run_phase*.py` creates `active_phase.json` and starts Claude CLI.
2. When Claude stops, `hook_router.py` runs.
3. If `active_phase.json` exists, `phase_auto_responder.py` handles the event.
4. If a completion signal is found in the conversation, stop is allowed immediately.
5. If the rate limit is exceeded, stop is allowed.
6. Otherwise, conversation context is sent to GPT-5.2.
7. GPT-5.2 responds with:
   - `PHASE_COMPLETE`: allow stop.
   - `MUST_STOP`: allow stop because human intervention is required.
   - Resume prompt: block the Stop event and send the prompt back to Claude.

## Phase Settings Summary

| Setting | Phase 0 | Phase 1 | Phase 2A | Phase 2B | Phase 2C | Phase 3 | Phase 4 | Phase 4.5 | Phase 6 | Phase 6.5 | Phase 6.5.1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LLM model | gpt-5.2 | gpt-5.2 | gpt-5.2 | gpt-5.2 | gpt-5.2 | gpt-5.2 | gpt-5.2 | gpt-5.2 | gpt-5.2 | gpt-5.2 | gpt-5.2 |
| Context size | 5,000 chars | 5,000 chars | 8,000 chars | 6,000 chars | 5,000 chars | 6,000 chars | 8,000 chars | 5,000 chars | 8,000 chars | 8,000 chars | 4,000 chars |
| Rate limit | 4/180s | 4/180s | 8/300s | 10/300s | 6/300s | 8/300s | 15/600s | 6/300s | 8/300s | 8/300s | 10/600s |
| Default timeout | 3,600s | 3,600s | 5,400s | 5,400s | 3,600s | 5,400s | 7,200s | 5,400s | 7,200s | 7,200s | 7,200s |

## Prerequisites

- Claude CLI (`~/.local/bin/claude`)
- Python 3.10+
- `PyYAML`, `requests`, `python-dotenv`
- `OPENROUTER_API_KEY` set in `.env`

## Logs

Runtime logs are stored in `.cache/`.

```bash
# Top-level logs
tail -f .claude/hooks/.cache/run_total_youra.log
tail -f .claude/hooks/.cache/run_pipeline_to_phase4.log
tail -f .claude/hooks/.cache/run_post_experiment.log
tail -f .claude/hooks/.cache/run_early_pipeline.log
tail -f .claude/hooks/.cache/run_hypothesis_loop.log

# Individual launcher logs
tail -f .claude/hooks/.cache/run_phase0.log
tail -f .claude/hooks/.cache/run_phase45.log
tail -f .claude/hooks/.cache/run_phase6.log
tail -f .claude/hooks/.cache/run_phase65.log
tail -f .claude/hooks/.cache/run_phase651.log

# Claude CLI output logs
tail -f .claude/hooks/.cache/phase0_claude_output.log
tail -f .claude/hooks/.cache/phase45_output.log
tail -f .claude/hooks/.cache/phase6_output.log
tail -f .claude/hooks/.cache/phase65_output.log
tail -f .claude/hooks/.cache/phase651_output.log

# Auto-responder logs
tail -f .claude/hooks/.cache/phase0_auto_responder.log

# Phase 2C/3/4 per-hypothesis session output logs
tail -f .claude/hooks/.cache/phase2c_h-e1_output.log
tail -f .claude/hooks/.cache/phase3_h-e1_output.log
tail -f .claude/hooks/.cache/phase4_h-e1_output.log

# Sub-logs for Reflection reruns and end-to-end subprocesses
tail -f .claude/hooks/.cache/pipeline_to_p4_early.log
tail -f .claude/hooks/.cache/pipeline_to_p4_hypothesis_loop.log
tail -f .claude/hooks/.cache/pipeline_to_p4_phase2a_reroute.log
tail -f .claude/hooks/.cache/total_part1.log
tail -f .claude/hooks/.cache/total_part2.log

# Reflection state
cat .claude/hooks/.cache/reflection_state.json

# Resume-time individual phase logs
tail -f .claude/hooks/.cache/pipeline_to_p4_resume_phase1.log
tail -f .claude/hooks/.cache/pipeline_to_p4_resume_phase2a.log
tail -f .claude/hooks/.cache/pipeline_to_p4_resume_phase2b.log
```
