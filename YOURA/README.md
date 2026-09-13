# YouRA — Your Research Assistant

This directory contains the executable YouRA workflow: Claude Code slash
commands, Python launchers, hooks, BMAD workflows, prompts, and phase-specific
agents.

For repository-level installation, evaluation scripts, bundled results, and
reviewer reproduction instructions, use the root `README.md`. This file only
summarizes how the `YOURA/` workflow itself is organized and run.

## What Is Here

```text
YOURA/
+-- .claude/
|   +-- commands/   # Claude Code slash commands such as /phase0-brainstorm
|   +-- hooks/      # Python launchers, hook router, auto-responder
|   +-- prompts/    # Auto-responder/refinement prompts
|   +-- agents/     # Claude Code subagent definitions
|   +-- skills/     # Local workflow skills
+-- bmad-custom-src/
|   +-- custom/modules/youra-research/workflows/
|       +-- phase0-brainstorm/
|       +-- phase1-targeted-research/
|       +-- phase2a-dialogue/
|       +-- phase2b-planning/
|       +-- hypothesis-loop/
|       +-- phase6-paper-writing/
|       +-- phase65-adversarial-review/
|       +-- phase651-overleaf/
+-- tasks_youra/    # Example task/topic inputs
+-- docs/           # Runtime outputs are written under docs/youra_research/
+-- install_hooks.py
```

## Setup Pointer

Use the root `README.md` setup flow:

1. Create and activate one virtual environment at the repository root.
2. Run `pip install -e .` from the repository root.
3. Create `.env` at the repository root with `OPENROUTER_API_KEY` and, if
   needed, `OPENAI_API_KEY`.
4. Run `python install_hooks.py --install-deps` from `YOURA/`.

`install_hooks.py` writes absolute paths into
`YOURA/.claude/settings.local.json`. Re-run it after moving or recloning the
repository.

## Running YouRA

Run YouRA from this `YOURA/` directory.

```bash
python .claude/hooks/run_total_youra.py docs/idea.md --enable-refine
```

`--enable-refine` runs the final manuscript refinement pass after Phase 6.5.1.
The final refined manuscript is written to:

```text
docs/youra_research/<run>/paper/refinement/06_paper_refinement.md
```

If PDF generation succeeds, the compiled PDF is written to:

```text
docs/youra_research/<run>/paper/refinement/overleaf_refinement/main.pdf
```

## Short Topics

For very short research topics, do not immediately launch the full unattended
pipeline. A terse topic can make Phase 0 produce an under-specified idea and
continue before a human has shaped the direction.

In Claude Code, start from `YOURA/` and run:

```text
/phase0-brainstorm
```

Review or edit:

```text
docs/youra_research/<run>/00_brainstorm_session.md
```

Then continue from Phase 1:

```bash
python .claude/hooks/run_total_youra.py dummy \
    --resume-from phase1 \
    --research-folder docs/youra_research/<run> \
    --enable-refine
```

## Slash Commands

Claude Code exposes 18 slash commands from `.claude/commands/`. Each command
file is a thin BMAD workflow loader: it loads `_bmad/core/tasks/workflow.xml`
and passes a per-phase `workflow.yaml` under
`bmad-custom-src/custom/modules/youra-research/workflows/<phase>/` as the
configuration. The `hypothesis-*` commands directly read/write
`verification_state.yaml` instead of going through BMAD.

The commands fall into four groups: **end-to-end driver**, **per-phase
commands** (run a single phase interactively), **hypothesis-loop control**
(used between Phase 2C and Phase 5 to walk sub-hypotheses), and **utility /
monitoring**.

### End-to-end driver

| Command | What it does |
|---------|--------------|
| `/full-pipeline-unattended` | Full automated UNATTENDED pipeline: Phase 0 → 1 → 2A → 2B → (2C → 3 → 4) × N → 4.5 → \[5] → 6 → 6.5. Takes a research idea file and runs the entire pipeline through paper generation. Phase 5 is optional (skipped when `skip_baseline_comparison=true` in `module.yaml`). |

### Per-phase commands

| Command | Phase | What it does |
|---------|-------|--------------|
| `/phase0-brainstorm` | 0 | Interactive research-question brainstorming session. Helps the user discover, refine, and articulate research questions through adaptive facilitation. Outputs Phase 1-compatible inputs (`research_question`, `detailed_question`, `reference_papers`). |
| `/phase1-research` | 1 | Systematic data collection for deep-learning research topics. Gathers academic papers, past cases, and implementations to identify research gaps. Produces research data ready for Phase 2A hypothesis generation. |
| `/phase1-targeted` | 1 (targeted) | Targeted research scoped by specific research questions and optional reference papers. Outputs Phase 1-compatible data for hypothesis generation in Phase 2A. |
| `/phase2a-dialogue` | 2A | Hypothesis generation via 4-Perspective Round Table (Novelty, Falsifiability, Significance, Plausibility) with convergence-based discussion, followed by Synthesis and Advocate–Critic refinement dialogue (3–8 rounds). Produces a validated hypothesis ready for Phase 2A Extended clarification. |
| `/phase2a-extended` | 2A (extended) | Narrows the broad project from Phase 2A to a specific testable hypothesis aligned with the user intent from Phase 0, then clarifies it with scientific rigor. Produces a focused hypothesis ready for Phase 2B. |
| `/phase2b-planning` | 2B | Decomposes main hypotheses into detailed sub-hypotheses and establishes verification plans. Produces a verification roadmap with prioritized experiments and success criteria. |
| `/phase2c-experiment-design` | 2C | Generates detailed, research-backed experiment specifications from Phase 2B verification protocols using MCP-powered implementation search and code analysis. Produces a Level-1.5 experiment brief ready for Phase 3. |
| `/phase3-implementation-planning` | 3 | Orchestrates PRD / Architecture generation, complexity assessment, PRP creation, and Archon project initialization for hypothesis implementation. Produces an implementation-ready package (PRD, Architecture, PRP, Archon tasks) for Phase 4. |
| `/phase4-coding` | 4 | Converts Phase 3 implementation plans into working code and validates hypotheses through a Coder–Validator agent loop. Produces validated code and `04_validation.md`. |
| `/phase5-baseline-repo-comparison` | 5 (optional) | Full-scale baseline comparison with `DETERMINES_SUCCESS` gate using `verification_state.yaml` v3.0. Compares the hypothesis implementation against official baseline repositories. |
| `/phase45-hypothesis-synthesis` | 4.5 | Refines initial hypotheses using experiment evidence from all sub-hypotheses (`h-*/04_validation.md`, `04_checkpoint.yaml`, `03_tasks.yaml`, `02c_experiment_brief.md`). Aligns predictions with results, removes overclaims, connects to literature, defines principled limitations, and derives results-grounded future work. Produces `045_validated_hypothesis.md` — the single source consumed by Phase 6. |
| `/phase6-paper-writing` | 6 | Generates an ICML-format academic paper from research-pipeline artifacts. Section-by-section generation with citation verification from Phase 0–5 outputs. |
| `/phase65-adversarial-review` | 6.5 | Multi-round adversarial review for the paper. Devil's-Advocate review with role separation to identify and fix issues before submission. |
| `/phase651-overleaf` | 6.5.1 | Converts the final reviewed paper to an Overleaf-compilable LaTeX project and compiles to PDF. |

### Hypothesis-loop control (Phase 2C → 3 → 4 → 5)

These commands are designed to be called repeatedly between Phase 2C and
Phase 5. They read/write `verification_state.yaml` directly.

| Command | What it does |
|---------|--------------|
| `/hypothesis-loop` | Execute the hypothesis verification loop. Automatically runs Phase 2C → 3 → 4 → 5 for each `READY` hypothesis in dependency order with gate validation. |
| `/hypothesis-next` | Lightweight single-hypothesis executor — runs only the next `READY` hypothesis through Phase 2C → 3 → 4 → 5 with gate validation. Use this when you want to step through hypotheses one at a time. |
| `/hypothesis-status` | Display a visual hypothesis verification progress dashboard. Reads `verification_state.yaml` and renders the status of every hypothesis with progress indicators. Read-only — does not mutate state. |

### When to use which

- Use `/full-pipeline-unattended` for hands-off end-to-end runs (equivalent to
  `python .claude/hooks/run_total_youra.py`).
- Use the per-phase commands when you want to inspect or steer individual
  phases interactively.
- Use the hypothesis-loop commands when iterating through sub-hypotheses —
  `/hypothesis-status` to inspect, `/hypothesis-next` to step, or
  `/hypothesis-loop` to drain the whole queue.

## Phase Outputs

A normal run creates:

```text
docs/youra_research/<run>/
+-- 00_brainstorm_session.md
+-- 01_targeted_research.md
+-- 01_targeted_research_full.md
+-- 02_synthesis.yaml
+-- 02b_verification_plan.md
+-- 03_refinement.md
+-- 03_refinement.yaml
+-- verification_state.yaml
+-- <h-id>/
|   +-- 02c_experiment_brief.md
|   +-- 03_prd.md
|   +-- 03_architecture.md
|   +-- 03_logic.md
|   +-- 03_config.md
|   +-- 04_validation.md
|   +-- 04_checkpoint.yaml
+-- 045_validated_hypothesis.md
+-- paper/
    +-- 06_paper.md
    +-- 06_paper_final.md
    +-- sections/
    +-- review/065_review_summary.md
    +-- refinement/
        +-- 06_paper_refinement.md
        +-- overleaf_refinement/main.pdf
```

## Notes

- `run_total_youra.py` is the recommended unattended entry point.
- `run_pipeline_to_phase4.py` handles Phase 0 through the hypothesis loop.
- `run_post_experiment.py` handles Phase 4.5 through refinement.
- `hook_router.py` and `phase_auto_responder.py` continue Claude Code sessions
  using the OpenRouter-backed auto-responder.

