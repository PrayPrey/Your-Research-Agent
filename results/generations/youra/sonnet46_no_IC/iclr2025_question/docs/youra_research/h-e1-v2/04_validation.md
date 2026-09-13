# Phase 4 Validation Report: h-e1-v2

**Generated:** 2026-08-05T10:45:00+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 4.5 (Phase 5 skipped by config)

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-e1-v2 (EXISTENCE, v2 of h-e1, modification attempt 1) |
| **Title** | Screened intermediate-layer logit-lens statistics are class-separable (AUROC ≥ 0.55) on both datasets for all three models, under the A2-v2 protocol-internal validity anchor |
| **Phase 4 Start** | 2026-08-05T08:32:38+00:00 |
| **Phase 4 End** | 2026-08-05T10:45:00+00:00 |
| **Duration** | ~2h 12m (incl. ~1h 15m GPU sweep across interrupted-and-resumed chain) |

**Statement (delta from h-e1):** identical datasets, models, signals, thresholds, split protocol, and code; the unreproducible v1 cross-protocol numeric anchor (H_E1_REFERENCES ± 0.03 halt gate) is replaced by the A2-v2 protocol-internal anchor: (a) donor-cache identity verified by ≥10-example fresh-regeneration agreement before reuse, (b) per-cell within-sweep final-layer entropy AUROC as the depth_beats_final baseline, (c) direction consistency vs the v1 record reported descriptively, never gated.

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 15 |
| Completed | 15 |
| Failed | 0 |
| Skipped | 0 |
| Coder-Validator Cycles | 1/5 |

### Generated Files

| File | Lines | Last Modified |
|------|-------|---------------|
| code/run_h_e1.py | 481 | 2026-08-05T08:37 |
| code/analysis.py | 145 | 2026-08-05T08:37 |
| code/constants.py | 58 | 2026-08-05T08:37 |
| code/generate_figures.py | 121 | 2026-08-05T08:37 |
| code/model.py | 60 | 2026-08-05T08:34 (verbatim h-e1) |
| code/data.py | 75 | 2026-08-05T08:34 (verbatim h-e1) |
| code/visualize.py | 122 | 2026-08-05T08:34 (verbatim h-e1) |
| code/run_experiment.sh | 19 | 2026-08-05T08:54 |
| code/tests/test_anchor_gate.py | 87 | 2026-08-05T08:35 (rewritten per FR-6.1) |
| code/tests/test_resume_reuse.py | 163 | 2026-08-05T08:38 (1 assertion inverted, see deviations) |
| code/tests/{test_analysis,test_data,test_figures,test_model_layout}.py | 63/45/64/58 | 2026-08-05T08:34 (verbatim h-e1) |

### Task History

All 15 tasks (D-1 bootstrap + Gap C, D-2 anchor re-spec + Gaps A/B, D-3 test rewrite, D-4 smoke, D-5 full sweep, D-6 analysis + verdict, D-7 figures, env verify, 6 subtasks, failsafe) completed in a single Coder-Validator cycle with 0 issues raised.

---

## Code Quality Checklist

Based on Validator Agent evaluation (2026-08-05T08:46):

- [✓] Syntax validation passed
- [✓] Type hints compliance
- [✓] API signatures match 03_logic.md
- [✓] Configuration schema match 03_config.md
- [✓] Cross-file dependencies resolved
- [✓] No obvious anti-patterns
- [✓] Test gate: 37/37 tests pass
- [✓] Reality check: REAL_MODEL
- [✓] Mechanism verification passed

### Issues Detected

No blocking issues. Two pre-flagged non-blocking notes:
- `visualize.py:67` still draws the retired H_E1_REFERENCES reference line in per-cell depth plots (verbatim-by-spec; gate unaffected).
- `experiment_results.json` `hypothesis_id` literal remains `"h-e1"` (cosmetic; folder path disambiguates).

---

## Experiment Results

### Execution Details

| Field | Value |
|-------|-------|
| **Mode** | auto (bash run_experiment.sh; detached resume chain after session interruptions) |
| **Status** | completed (EXPERIMENT COMPLETE, exit=0, 2026-08-05T10:14:59+00:00) |
| **Scale** | 5,451 scored generations (1,817 per model: TriviaQA 1,000 + TruthfulQA 817), 3 models, 6 cells; llama2/triviaqa via verified donor cache (zero GPU) |
| **Environment** | conda youra-h-e1-v2 (py3.10.20, torch 2.8.0+cu128, transformers 4.57.1), 1× H100 (GPU 2), fp16, batch 1, seed 42, greedy decode |
| **Log** | code/experiment.log (584 lines, trap-EXIT completion marker) |

### Metrics — Gate Grid (selection split, corrected AUROC)

| Cell | Best (layer, signal) | Best AUROC | Final-layer (L32) entropy AUROC | depth_beats_final | Gate (≥ 0.55) |
|------|---------------------|-----------|-------------------------------|-------------------|---------------|
| llama2/triviaqa | L31, adj_kl | 0.6522 | 0.5928 | ✓ | ✓ |
| llama2/truthfulqa | L29, entropy | 0.7011 | 0.6669 | ✓ | ✓ |
| mistral/triviaqa | L31, maxprob | 0.6092 | 0.5447 | ✓ | ✓ |
| mistral/truthfulqa | L31, adj_kl | 0.6570 | 0.6048 | ✓ | ✓ |
| llama3/triviaqa | L28, entropy | 0.6868 | 0.5566 | ✓ | ✓ |
| llama3/truthfulqa | L31, maxprob | 0.6213 | 0.6178 | ✓ | ✓ |

Degeneracy screen retained 20 (llama2), 15 (mistral), 15 (llama3) layers — all ≥ 5 required. Mechanism verification `all_true` in 6/6 cells. `verify_v2_run_complete`: 5/5 indicators true (reuse_verified, anchor_reported, grid_nondegenerate, screen_healthy, all_cells_measured).

### A2-v2 clause-(c) direction consistency (descriptive, ungated)

| Cell | Final-layer direction | v1 record | Consistent |
|------|----------------------|-----------|------------|
| llama2/triviaqa | True | True | ✓ |
| llama2/truthfulqa | False | True | ✗ |
| mistral/triviaqa | False | False | ✓ |
| mistral/truthfulqa | False | False | ✓ |
| llama3/triviaqa | True | False | ✗ |
| llama3/truthfulqa | False | False | ✓ |

4/6 consistent with the best-proxy v1 record. The two inconsistencies are on cells the v1 record never code-verified (only llama2/triviaqa was); descriptive only per spec, no gating effect.

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Result** | **PASS** |
| **Satisfied** | true |
| **Evaluated At** | 2026-08-05T10:42:00+00:00 |

### Criteria Evaluation

| Criterion | Target | Actual | Result |
|-----------|--------|--------|--------|
| Existence: ≥1 screened (layer,signal) pair per model with selection-split corrected AUROC ≥ 0.55, both datasets | 6/6 cells | 6/6 (range 0.6092–0.7011) | ✓ PASS |
| A2-v2(a): donor-cache identity verified before reuse | verify_cache_reuse 10/10 | 10/10 | ✓ PASS |
| A2-v2(b): depth_beats_final per cell | 6/6 cells | 6/6 | ✓ PASS |
| Degeneracy screen retains ≥ 5 layers per model | ≥5 | 20 / 15 / 15 | ✓ PASS |
| A2-v2(c): direction consistency reported descriptively, ungated | reported | 6 clause-c log lines, 4/6 consistent, no halt | ✓ PASS |

---

## Next Steps

### ✅ Ready for Phase 4.5

All validation criteria met. `skip_baseline_comparison: true` in module.yaml, so Phase 5 is skipped and the pipeline proceeds to Phase 4.5 (Hypothesis Synthesis) after remaining hypotheses complete.

Immediate effect: h-e1-v2 PASS unblocks dependents h-m1 (next, MUST_WORK), then h-m2, h-m3, h-c1 (`awaiting: h-e1-v2` resolved).

---

## Appendix

### Files Reference

| File | Purpose |
|------|---------|
| `04_checkpoint.yaml` | Recovery checkpoint |
| `04_validation.md` | This report |
| `experiment_results.json` | Raw experiment data (6-cell gate grid + verdict) |
| `code/` | Implementation (7 modules + 6 test files + launcher) |
| `results/cache_{model}_{dataset}.csv` | 6 per-example streaming caches (~1.5 MB each, 5+96 cols) |
| `figures/` | 12 PNGs (gate_metrics_bar, auroc_heatmap, 7× auroc_vs_depth, degeneracy_screen, entropy_heatmap_llama2, anchor_v2_report) |
| `../verification_state.yaml` | Updated gate status (central) |

### Checkpoint Summary

```yaml
version: "3.5"
hypothesis_id: "h-e1-v2"
created_at: "2026-08-05T08:32:38+00:00"
completed_at: "2026-08-05T10:45:00+00:00"
tasks:
  total: 15
  completed: 15
coder_validator_cycles: 1
unattended_mode: true
```

### Environment

| Item | Value |
|------|-------|
| Execution Date | 2026-08-05 |
| Mode | UNATTENDED |
| MCP Servers | Archon (hypothesis task tracking); Serena unavailable this session (grep fallback used) |
| Duration | ~2h 12m wall clock (three session takeovers; detached resume chain finished autonomously) |

### Deviations (from 04_checkpoint.yaml)

- Pinned conda env `youra-h-e1` broken (torch ImportError `ncclCommResume`); ran in `youra-h-e1-v2` (torch 2.8.0+cu128, transformers 4.57.1 vs pinned 4.57.6).
- `tests/test_resume_reuse.py` had one assertion pinning the retired v1 `_archive` donor path, contradicting the mandated Gap C patch; renamed + inverted to `test_donor_constant_points_at_sibling_h_e1_results`.
- `verify_v2_run_complete` persisted via main()-side re-write of experiment_results.json (keeps analyze_all 0-edit per 03_logic.md).
- `run_experiment.sh` conda env patched to `youra-h-e1-v2`; figures step wired in.

---

## Phase 2C Handoff

> **Purpose:** Consumed by Phase 2C when processing dependent hypotheses (h-m1, h-m2, h-m3, h-c1).

### Source Information

| Field | Value |
|-------|-------|
| **Source Hypothesis** | h-e1-v2 |
| **Generated At** | 2026-08-05T10:45:00+00:00 |
| **Gate Result** | PASS |
| **Ready for Dependents** | true |

### Proven Components

| Component | File | Type | Evidence | Reusable |
|-----------|------|------|----------|----------|
| Logit-lens per-layer sweep (33 hidden states, 3 signals, answer-token averaging) | code/model.py, code/run_h_e1.py | inference pipeline | 6/6 cells measured, 37/37 tests | Yes |
| Streaming per-example cache + resume by example_id | code/run_h_e1.py | infra | survived 3 interruptions, resumed cleanly | Yes |
| Donor-cache reuse with identity verification | code/run_h_e1.py (`verify_cache_reuse`, `verify_donor_cache_path`) | infra | 10/10 agreement, zero-GPU binding cell | Yes |
| Degeneracy screen + corrected AUROC grid + evaluate_gate | code/analysis.py | evaluation | 15–20 layers retained/model, 6/6 non-degenerate grids | Yes |
| A2-v2 protocol-internal anchor (`check_anchor_and_halt` v2) | code/run_h_e1.py | validity check | per-cell anchor computed, never halts on numerics, ValueError contract guards intact | Yes |
| `verify_v2_run_complete` 5-indicator run verifier | code/analysis.py | validity check | 5/5 true on full run | Yes |
| Stratified 50/50 selection/test split, seed 42, test locked | code/data.py | protocol | splits finalized in all 6 caches | Yes — **h-m1 must reuse the locked test splits untouched** |
| 6-cell figure loop + anchor v2 report | code/generate_figures.py | reporting | 12 figures rendered | Yes |

**Reuse Notes:**
- All 6 per-example caches in `h-e1-v2/results/` contain full per-layer signal columns for **both** splits — h-m1 (test-split evaluation, frozen tuple from selection split) and h-m3 (fusion) can run **entirely from these caches with zero GPU**.
- Selection-split winners to freeze for h-m1: see gate grid above (per-cell best layer/signal).
- `V1_DIRECTION_RECORD` in constants.py is best-proxy for 5/6 cells; treat clause-c consistency as descriptive context only.

### Optimal Hyperparameters

Training-free (EXISTENCE PoC): no tuned training hyperparameters. Protocol constants that must stay fixed for dependents: seed 42, greedy decode, max_new_tokens=32, fp16 weights / float32 statistics, AUROC_GATE=0.55, DEGENERACY_ENTROPY_PCT=0.01, DEGENERACY_AGREEMENT_MIN=0.05.

### Lessons Learned

#### What Worked Well
- Protocol-internal anchoring (A2-v2): replacing a cross-protocol numeric reference with within-run baselines removed the unreproducible halt while keeping validity checks strong — all 6 cells measured vs 1/6 in h-e1.
- Verbatim code reuse with a surgical 3-gap patch set (Gaps A/B/C found by architecture review, all real).
- Streaming caches + example_id resume: full sweep survived a broken pinned env, a dead wrapper process, and three session takeovers without losing work.

#### What Didn't Work
- Pinning a conda env by name across hypothesis versions (env drifted/broke twice); pin by spec, verify at task start.
- v1's best-proxy direction record: 2/6 cells inconsistent — cross-run records that were never code-verified should not be trusted even descriptively without flags.

#### Unexpected Findings
- TruthfulQA final-layer entropy AUROC is relatively strong (0.60–0.67), so depth margins there are thin (llama3/truthfulqa: 0.6213 vs 0.6178, margin 0.0035). The existence gate passes, but h-m2's `intermediate ≥ final − 0.02` no-regression framing matters more than raw depth advantage on that dataset.
- Depth advantage is largest on TriviaQA (llama3: +0.130, mistral: +0.064, llama2: +0.059), consistent with the calibration-suppression story the main hypothesis proposes.

#### Key Insight
> Intermediate-layer logit-lens uncertainty signals are class-separable in every model × dataset cell, and the best screened intermediate layer beats the within-sweep final-layer entropy baseline in all 6 — the existence premise of H-LayerLensUQ-v2 is confirmed at PoC scale with a fully protocol-internal validity anchor.

### Recommendations for Dependent Hypotheses

**Dependent Hypotheses:** h-m1 (MUST_WORK, next), h-m2, h-m3, h-c1

#### General Recommendations
- Run all dependents from the finalized `h-e1-v2/results/` caches (zero GPU for analysis-only hypotheses); regenerate nothing.
- Reuse the locked test splits exactly; selection-split tuple freezing for h-m1 must use the winners in the gate grid above.
- Keep the A2-v2 anchor semantics: report anchors, never numerically halt.

#### Specific Recommendations
- **h-m1** (test AUROC ≥ 0.60 + bootstrap ΔAUROC vs final-layer entropy on TriviaQA): selection AUROCs clear 0.60 in 5/6 cells (mistral/triviaqa 0.6092 is at the boundary) — expect test-split attrition; the paired-bootstrap CI on llama2/triviaqa (Δ ≈ 0.059 at selection) is the risk item, not the level gate.
- **h-m2** (all cells ≥ 0.60 + no-regression on mistral/llama3): llama3/truthfulqa's thin depth margin (0.0035) makes the `≥ final − 0.02` clause easy but the 0.60 level clause is the binding one for mistral/triviaqa.
- **h-m3** (fusion): entropy-family and adj_kl winners differ across cells — complementarity is plausible; fit only on selection split.
- **h-c1** (cross-dataset transfer): best layers cluster at L28–L31 across datasets within each model, which favors transfer; signal identity differs by dataset in 4/6 cells — transfer the full (layer, signal, direction) tuple, not just the layer.

#### Warnings (What to Avoid)
- Do not re-derive splits or re-generate caches (breaks test-lock and donor identity).
- Do not gate anything on `V1_DIRECTION_RECORD` consistency.
- Do not trust the pinned `youra-h-e1` env; use `youra-h-e1-v2`.

#### Suggested Starting Point
- **Hyperparameters:** protocol constants above, unchanged.
- **Adjustments:** none required; h-m1 is cache-only analysis plus bootstrap machinery.

---

*This section is auto-generated for Phase 2C consumption. Edit only if necessary.*

---

*Report generated by Phase 4 Implementation & Validation Workflow*
*Anonymous Research Pipeline - Phase 4*
