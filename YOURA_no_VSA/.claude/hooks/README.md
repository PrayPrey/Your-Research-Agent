# YouRA Hook System — Quick Reference

Unattended pipeline: Phase 0 → 1 → 2A → 2B → (2C → 3 → 4)×N → 4.5 → [5] → 6 → 6.5 → 6.5.1 → [refine]

Requires: Claude CLI (`~/.local/bin/claude`), Python 3.10+, `PyYAML requests python-dotenv`, `OPENROUTER_API_KEY` in `.env`.

> **This tree (`YouRA_results_new_4_no_VSA`) is the w/o-VSA ablation arm: `--state-mode shadow` is the default for EVERY run** (full, partial, resume). Omitting it silently falls back to `normal` (full-YouRA arm) and the output is unusable as ablation data.

## Full Pipeline

```bash
# From a task file (default for this tree — note --state-mode shadow)
python .claude/hooks/run_total_youra.py tasks_youra/iclr2025_question.md \
    --research-folder docs/youra_research --enable-refine --state-mode shadow

# Options
#   --state-mode shadow|normal   normal = full-YouRA arm only; DO NOT use in this tree
#   --max-reflections 5|0|-1     reflection loop limit (default 5)
#   --enable-phase5              include Phase 5 (needs run_phase5.py)
#   --enable-refine              paper refinement + PDF after 6.5.1
#   --timeout-phase0 1800 ...    per-phase timeouts
```

Pre-run check: stale normal-mode session logs (`phase*_*.log`) in `.claude/hooks/.cache/`
cause R8-audit false positives (`CLEAN_DISABLE_FAILED`) — archive/remove them before launching.

## w/o VSA Ablation (VSA-IC, `--state-mode shadow`)

Model gets no file access to `verification_state.yaml` / `04_checkpoint.yaml` / `03_tasks.yaml`;
state is relayed via prompt context + `.ablation_shadow/`. `normal` = unchanged full-YouRA behavior.

```bash
# Clean-disable verification (ws4 spec §5; exit 1 on violation)
python .claude/hooks/ablation_audit.py
python .claude/hooks/ablation_audit.py --clean-disable-report --research-folder <path>

# Unit tests
python3 -m unittest test_ablation_state_manager
```

## Resume

Re-pass `--state-mode shadow` on every resume — the flag is not persisted; omitting it resumes in normal mode.

```bash
# Part 1 points: phase0 | phase1 | phase2a | phase2b | hypothesis-loop
# Part 2 points: phase45 | phase5 | phase6 | phase65 | phase651 | refine
python .claude/hooks/run_total_youra.py dummy \
    --resume-from phase2b --research-folder docs/youra_research/<folder> --state-mode shadow
python .claude/hooks/run_total_youra.py dummy \
    --resume-from refine --research-folder <path> --enable-refine --state-mode shadow
```

## Partial Runs

```bash
# Part 1 only (Phase 0–4, reflection loop)
python .claude/hooks/run_pipeline_to_phase4.py tasks_youra/iclr2025_question.md --state-mode shadow

# Part 2 only (Phase 4.5–6.5.1; needs verification_state.yaml + h-*/04_validation.md)
python .claude/hooks/run_post_experiment.py --research-folder <path> --state-mode shadow

# Phase 0–2B only
python .claude/hooks/run_early_pipeline.py tasks_youra/iclr2025_question.md --state-mode shadow

# Hypothesis loop only (2C→3→4 per READY hypothesis)
python .claude/hooks/run_hypothesis_loop.py --research-folder <path> --state-mode shadow
```

## Individual Phases

```bash
python .claude/hooks/run_phase0.py tasks_youra/iclr2025_question.md     # 0/1/2A pre-date VSA — no flag
python .claude/hooks/run_phase1.py   --research-folder <path>
python .claude/hooks/run_phase2a.py  --research-folder <path>
python .claude/hooks/run_phase2b.py  --research-folder <path> --state-mode shadow
python .claude/hooks/run_phase2c.py  --research-folder <path> --hypothesis h-e1 --state-mode shadow
python .claude/hooks/run_phase3.py   --research-folder <path> --hypothesis h-e1 --state-mode shadow
python .claude/hooks/run_phase4.py   --research-folder <path> --hypothesis h-e1 --state-mode shadow
python .claude/hooks/run_phase45.py  --research-folder <path> --state-mode shadow
python .claude/hooks/run_phase6.py   --research-folder <path> --state-mode shadow
python .claude/hooks/run_phase65.py  --research-folder <path> --state-mode shadow
python .claude/hooks/run_phase651.py --research-folder <path> --state-mode shadow
python .claude/hooks/run_phase_refine.py --research-folder <path>       # no state files touched — no flag
# All accept --timeout <seconds>
```

## Exit Codes

`0` complete · `1` fatal (shadow: also `CLEAN_DISABLE_FAILED`) · `2` reflection-limit/ROUTED · `3` incomplete/BLOCKED

## Logs

```bash
tail -f .claude/hooks/.cache/run_total_youra.log          # top-level
tail -f .claude/hooks/.cache/phase4_h-e1_output.log       # per-session Claude output
cat .claude/hooks/.cache/reflection_state.json            # reflection state
cat .claude/hooks/.cache/ablation_audit.json              # R8 audit result (shadow)
```
