# YouRA Hook System — Usage

Python orchestrator that runs the YouRA pipeline unattended: one Claude CLI session per phase, deterministic output verification, automatic resume on stop. This build uses `responder_mode: "fixed"` (no API key required).

## Full pipeline

```bash
python .claude/hooks/run_total_youra.py <idea.md | "topic string"> --enable-refine
python .claude/hooks/run_total_youra.py docs/idea.md --max-reflections 5 --timeout-phase6 10800
```

## Resume

```bash
python .claude/hooks/run_total_youra.py dummy --resume-from <point> --research-folder <path> [--enable-refine]
```

Resume points (in order): `phase0` `phase1` `phase2a` `phase2b` `hypothesis-loop` `phase45` `phase5` `phase6` `phase65` `phase651` `refine`
(`--research-folder` required for everything except `phase0`.)

## Partial runs

```bash
# Part 1 only (Phase 0 → hypothesis loop)
python .claude/hooks/run_pipeline_to_phase4.py docs/idea.md [--max-reflections N] [--resume-from <point>]

# Part 2 only (Phase 4.5 → 6.5.1 [+ Refine])
python .claude/hooks/run_post_experiment.py --research-folder <path> [--enable-refine] [--resume-from <point>]

# Phase 0–2B only
python .claude/hooks/run_early_pipeline.py docs/idea.md

# Hypothesis loop only (Phase 2C → 3 → 4 × N)
python .claude/hooks/run_hypothesis_loop.py --research-folder <path>
```

## Individual phases

All launchers accept `--timeout <seconds>`.

```bash
python .claude/hooks/run_phase0.py  <idea.md | "topic">          # Brainstorm
python .claude/hooks/run_phase1.py  --research-folder <path>     # Targeted research
python .claude/hooks/run_phase2a.py --research-folder <path>     # Hypothesis dialogue
python .claude/hooks/run_phase2b.py --research-folder <path>     # Verification plan
python .claude/hooks/run_phase2c.py --research-folder <path> --hypothesis h-e1
python .claude/hooks/run_phase3.py  --research-folder <path> --hypothesis h-e1
python .claude/hooks/run_phase4.py  --research-folder <path> --hypothesis h-e1
python .claude/hooks/run_phase45.py --research-folder <path>     # Synthesis
python .claude/hooks/run_phase6.py  --research-folder <path>     # Paper writing
python .claude/hooks/run_phase65.py --research-folder <path>     # Adversarial review
python .claude/hooks/run_phase651.py --research-folder <path>    # Overleaf LaTeX + PDF
python .claude/hooks/run_phase_refine.py --research-folder <path>  # Paper refinement
```

## Logs

```bash
tail -f .claude/hooks/.cache/run_total_youra.log      # top-level progress
tail -f .claude/hooks/.cache/run_phase6.log           # per-launcher log
tail -f .claude/hooks/.cache/phase6_output.log        # Claude CLI output
grep "TIMEOUT MARKER" .claude/hooks/.cache/*.log      # timeout events
```

## Exit codes (`run_total_youra` / `run_pipeline_to_phase4`)

`0` complete · `1` fatal error · `2` reflection limit reached · `3` incomplete/blocked hypotheses

## Known pitfalls

- Never `pkill -f "experiment.py"` — it also matches `run_post_experiment.py` of every pipeline running on the machine. Use `pkill -f "code/experiment\.py"` or the `experiment.pid` mechanism (`timeout_policy.kill_phase4_experiment`).
- After an unexpected kill, resume with `--resume-from` instead of restarting from Phase 0.
- If the hypothesis loop exits BLOCKED with `No READY or IN_PROGRESS hypotheses` (typically right after a Reflection regenerated `verification_state.yaml` with a drifted schema — e.g. `todo`/`PENDING` statuses or missing gates), run `python .claude/hooks/fix_verification_state.py docs/youra_research` and resume with `--resume-from hypothesis-loop`.
