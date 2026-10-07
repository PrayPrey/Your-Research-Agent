# YouRA — Your Research Agent

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
|       +-- phase1-research/
|       +-- phase1-targeted-research/
|       +-- phase2a-dialogue/
|       +-- phase2b-planning/
|       +-- phase2c-experiment-design/
|       +-- phase3-implementation-planning/
|       +-- phase4-coding/
|       +-- hypothesis-loop/
|       +-- phase45-hypothesis-synthesis/
|       +-- phase6-paper-writing/
|       +-- phase65-adversarial-review/
|       +-- phase651-overleaf/
+-- tasks_youra/    # Example task/topic inputs
+-- docs/           # Runtime outputs are written under docs/youra_research/
+-- install_hooks.py  # Hook dependency installer; writes .claude/settings.local.json
+-- setup_tex.py      # TinyTeX + LaTeX package installer for PDF generation
+-- requirements.txt  # Hook runtime dependencies
+-- .env.example      # Copy of the root .env template (hooks read YOURA/.env, then ../.env)
```

## Setup Pointer

Use the root `README.md` setup flow:

1. Create and activate one virtual environment at the repository root.
2. Run `pip install -e .` from the repository root.
3. Create `.env` at the repository root with `OPENROUTER_API_KEY` and, if
   needed, `OPENAI_API_KEY`.
4. Make sure the Claude Code CLI is logged in and reachable at
   `~/.local/bin/claude` (the launchers hard-code this path; symlink it there
   if the CLI is installed elsewhere).
5. Run `python install_hooks.py --install-deps` from `YOURA/`.
6. Run `python setup_tex.py` from `YOURA/` (or use an existing TeX Live) and
   put its `bin` directory on `PATH`, so that `pdflatex`, `xelatex`, and
   `bibtex` resolve. Needed only for the PDF outputs of Phase 6.5.1 and
   `--enable-refine`.
7. Have `conda` on `PATH`; Phase 4 creates one conda environment per
   experiment and stops if it is missing.

`install_hooks.py` writes absolute paths into
`YOURA/.claude/settings.local.json`. Re-run it after moving or recloning the
repository. The unattended launchers run on Linux (WSL on Windows).

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

PDF compilation needs `xelatex` and `bibtex` on `PATH` (step 6 of the Setup
Pointer). Without them the Markdown manuscript and the `.tex` project are
still written; the compile step is skipped with a warning and no PDF is
produced.

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

Claude Code exposes 15 slash commands from `.claude/commands/`. The per-phase
command files are thin BMAD workflow loaders: they load
`_bmad/core/tasks/workflow.xml` and pass a per-phase `workflow.yaml` under
`bmad-custom-src/custom/modules/youra-research/workflows/<phase>/` as the
configuration. `/hypothesis-loop` loads the step files under
`workflows/hypothesis-loop/` directly (no `workflow.xml`), and
`/hypothesis-next` / `/hypothesis-status` are self-contained instructions
that read and write `verification_state.yaml` themselves.

The commands fall into two groups: **per-phase commands** (run a single phase
interactively) and **hypothesis-loop control** (used between Phase 2B and
Phase 4.5 to walk sub-hypotheses). Hands-off end-to-end runs use the Python
launcher `python .claude/hooks/run_total_youra.py`, not a slash command.

### Per-phase commands

| Command | Phase | What it does |
|---------|-------|--------------|
| `/phase0-brainstorm` | 0 | Interactive research-question brainstorming session. Helps the user discover, refine, and articulate research questions through adaptive facilitation. Outputs Phase 1-compatible inputs (`research_question`, `detailed_question`, `reference_papers`). |
| `/phase1-research` | 1 | Systematic data collection for deep-learning research topics. Gathers academic papers, past cases, and implementations to identify research gaps. Produces research data ready for Phase 2A hypothesis generation. |
| `/phase1-targeted` | 1 (targeted) | Targeted research scoped by specific research questions and optional reference papers. Outputs Phase 1-compatible data for hypothesis generation in Phase 2A. |
| `/phase2a-dialogue` | 2A | Hypothesis generation via 4-Perspective Round Table (Novelty, Falsifiability, Significance, Plausibility) with convergence-based discussion, followed by Synthesis and Advocate–Critic refinement dialogue (3–8 rounds). Produces a validated hypothesis ready for Phase 2B. |
| `/phase2b-planning` | 2B | Decomposes main hypotheses into detailed sub-hypotheses and establishes verification plans. Produces a verification roadmap with prioritized experiments and success criteria. |
| `/phase2c-experiment-design` | 2C | Generates detailed, research-backed experiment specifications from Phase 2B verification protocols using MCP-powered implementation search and code analysis. Produces a Level-1.5 experiment brief ready for Phase 3. |
| `/phase3-implementation-planning` | 3 | Orchestrates PRD / Architecture generation, complexity assessment, PRP creation, and Archon project initialization for hypothesis implementation. Produces an implementation-ready package (PRD, Architecture, PRP, Archon tasks) for Phase 4. |
| `/phase4-coding` | 4 | Converts Phase 3 implementation plans into working code and validates hypotheses through a Coder–Validator agent loop. Produces validated code and `04_validation.md`. |
| `/phase45-hypothesis-synthesis` | 4.5 | Refines initial hypotheses using experiment evidence from all sub-hypotheses (`h-*/04_validation.md`, `04_checkpoint.yaml`, `03_tasks.yaml`, `02c_experiment_brief.md`). Aligns predictions with results, removes overclaims, connects to literature, defines principled limitations, and derives results-grounded future work. Produces `045_validated_hypothesis.md` — the single source consumed by Phase 6. |
| `/phase6-paper-writing` | 6 | Generates an ICML-format academic paper from research-pipeline artifacts. Section-by-section generation with citation verification from Phase 0–5 outputs. |
| `/phase65-adversarial-review` | 6.5 | Multi-round adversarial review for the paper. Devil's-Advocate review with role separation to identify and fix issues before submission. |
| `/phase651-overleaf` | 6.5.1 | Converts the final reviewed paper to an Overleaf-compilable LaTeX project and compiles to PDF. |

### Hypothesis-loop control (Phase 2C → 3 → 4)

These commands are designed to be called repeatedly between Phase 2B and
Phase 4.5. They read/write `verification_state.yaml` directly. The Phase 5
(baseline comparison) step inside them is skipped while
`skip_baseline_comparison: true` in `module.yaml` (the default); there is no
separate Phase 5 slash command.

| Command | What it does |
|---------|--------------|
| `/hypothesis-loop` | Execute the hypothesis verification loop. Automatically runs Phase 2C → 3 → 4 (→ 5 when baseline comparison is enabled) for each `READY` hypothesis in dependency order with gate validation. |
| `/hypothesis-next` | Lightweight single-hypothesis executor — runs only the next `READY` hypothesis through Phase 2C → 3 → 4 (→ 5 when enabled) with gate validation. Use this when you want to step through hypotheses one at a time. |
| `/hypothesis-status` | Display a visual hypothesis verification progress dashboard. Reads `verification_state.yaml` and renders the status of every hypothesis with progress indicators. Read-only — does not mutate state. |

### When to use which

- Use `python .claude/hooks/run_total_youra.py` for hands-off end-to-end runs.
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
|   +-- 03_tasks.yaml
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

