# Reflection Report: h-m1
**Generated:** 2026-05-19T11:35:00+00:00
**Gate Result:** FAIL
**Gate Type:** MUST_WORK
**Reflection Outcome:** ROUTED_TO_PHASE_0

---

## 1. Experiment Summary

**Hypothesis:** Under controlled conditions, if execution reward directly signals functional incorrectness at program level, then the model reallocates probability mass toward control-flow and data-flow AST transformations (not surface edits).

**Gate Criteria (MUST_WORK):**
- Code executes without errors: ✅ PASS
- Mechanism correctly implemented: ✅ PASS (AST decomposition, SEP computation functional)
- Metrics can be measured: ✅ PASS (SEP values computed, figures generated)
- Statistical significance (Mann-Whitney p < 0.05): ❌ FAIL (p=0.4248)
- GRPO SEP > DPO SEP: ❌ FAIL (GRPO mean=0.2371, DPO mean=0.2377 — GRPO slightly lower)

---

## 2. Root Cause Analysis

### Primary Failure: Checkpoint Data Aliasing

The experiment required 27 KL-matched checkpoint pairs (10 GRPO steps × 10 DPO steps → 27 pairs at kl_tolerance=0.15). However, the H-E1 phase only produced **2 real GRPO checkpoints** (checkpoint-100, checkpoint-200) and **1 real DPO checkpoint** (base model). All other checkpoint steps (300–1000) fell back to checkpoint-100.

**Consequences:**
- 192 GRPO SEP values derived from only ~2 distinct checkpoints
- Effective statistical sample size n≈2 (massively correlated repeated measurements)
- Mann-Whitney U test invalid under these conditions (assumes independence)
- Spearman correlation returned NaN (no variance in reward/correctness axis)

### Secondary Findings:
- AST decomposition pipeline works correctly (decomposition_working=true)
- SEP values are valid and bounded [0,1]
- 5 figures generated successfully
- The mechanism infrastructure is implemented correctly

### What This Means:
The gate FAIL does NOT indicate the hypothesis is fundamentally wrong. It indicates that **the test was unable to measure the hypothesis** due to insufficient training checkpoint diversity from H-E1. With only 2 distinct GRPO model states, no meaningful differential analysis is possible.

---

## 3. Reflection Decision

**Gate Type:** MUST_WORK → FAIL → Route to Phase 0

Per workflow rules (step-06b Section 2): `gate_result == "FAIL"` → `reflection_outcome = "ROUTED_TO_PHASE_0"`.

**Assessment:** The failure is due to data infrastructure limitations (insufficient H-E1 checkpoints), not a fundamental flaw in the h-m1 mechanism hypothesis. However, the workflow enforces FAIL → Phase 0 routing.

---

## 4. Lessons Learned

**What Worked:**
- AST decomposition with FA-AST taxonomy (CONTROL_FLOW/DATA_FLOW/surface classification)
- SEP computation pipeline (compute_sep, compute_edit_distribution)
- 27-pair KL-matching framework (structural logic correct)
- Visualization pipeline (5 figures, gate_sep_comparison.png mandatory figure)
- Cacher/solution loading infrastructure

**What Didn't Work:**
- H-E1 only saved 2 GRPO checkpoints — insufficient for 27-pair analysis
- Checkpoint fallback logic silently reused checkpoint-100 ~21 times
- No early detection of checkpoint aliasing before running full analysis
- Spearman correlation undefined (NaN) — reward/correctness axis lacked variance

**Key Insight:**
The H-M1 mechanism analysis requires diverse training checkpoints across the training trajectory. Future designs must either (a) ensure H-E1 saves checkpoints at every 100 steps (steps 100–1000), or (b) redesign H-M1 to work with fewer KL-matched pairs using the 2 available checkpoints with narrower tolerance.

---

## 5. Routing Decision

- **Outcome:** ROUTED_TO_PHASE_0
- **Status Update:** h-m1 → FAILED
- **Cascade:** h-m2 (prerequisite: h-m1) → CASCADE_FAILED
- **Next Action:** Phase 0 brainstorm with lessons from h-e1 and h-m1

---

## 6. Files Preserved

| File | Purpose |
|------|---------|
| `code/` | Full implementation (AST decomp, SEP analysis, stats) |
| `outputs/sep_results.json` | Gate metrics, statistical results |
| `figures/gate_sep_comparison.png` | Mandatory gate figure |
| `figures/ast_edit_distribution.png` | AST edit type breakdown |
| `figures/ast_node_heatmap.png` | Node type frequency heatmap |
| `figures/reward_correctness_scatter.png` | Reward vs correctness scatter |
| `figures/sep_vs_kl_trajectory.png` | SEP vs KL trajectory |
| `code/experiment.log` | Full experiment execution log (164 lines) |
