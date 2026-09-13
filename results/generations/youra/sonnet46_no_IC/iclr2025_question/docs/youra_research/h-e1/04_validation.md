# Phase 4 Validation Report: h-e1

**Generated:** 2026-08-05T07:51:26+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 2C (h-e1-v2 retry) — Phase 5 blocked pending v2

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-e1 |
| **Title** | Per-Layer Logit-Lens Hallucination Signal Existence Sweep (EXISTENCE, MUST_WORK) |
| **Phase 4 Start** | 2026-08-05T07:17:00+00:00 |
| **Phase 4 End** | 2026-08-05T07:51:26+00:00 |
| **Duration** | ~34 minutes |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 15 |
| Completed | 15 (validator PASS, all 15) |
| Failed | 0 |
| Skipped | 0 |
| Coder-Validator Cycles | 1/5 |

### Generated Files

| File | Lines | Origin |
|------|-------|--------|
| constants.py | 43 | v1 archive, copied verbatim (0 edits) |
| model.py | 60 | v1 archive, copied verbatim |
| data.py | 75 | v1 archive, copied verbatim |
| analysis.py | 121 | v1 archive, copied verbatim |
| visualize.py | 122 | v1 + NEW `plot_entropy_heatmap` (A-7/FR-5.6) |
| run_h_e1.py | 441 | v1 + A-2 (resume/donor-reuse) + A-3 (anchor pre-gate) patches |
| generate_figures.py | 91 | NEW (Phase 4 report figures) |
| tests/ (6 files) | 445 | 3 copied + 3 NEW (resume_reuse, anchor_gate, figures) |

### Task History

- **task-001** (env setup): done — torch 2.8.0+cu128 restored (matches v1 protocol env), all packages present, HF_TOKEN set, 3 models + 2 datasets in HF cache
- **task-002** (A-1 copy): done — 6 modules + 3 test files copied; paths auto-resolve; 18/18 v1 tests pass
- **task-003/009/010** (A-2 epic + subtasks): done — `resume_from_cache` (corrupt-tail truncation, header guard), `verify_cache_reuse` (10-example protocol-identity check), `run_sweep` donor short-circuit + append-mode resume; 10 new tests
- **task-004/011/012** (A-3 epic + subtasks): done — `check_anchor_and_halt` (ValueError/SystemExit contract), `run_model` per-cell anchor, `main` zero-GPU pre-flight; 4 new tests
- **task-005** (smoke): done — llama2 n=10, 7.7s, peak 13.59 GB; mistral/llama3 smoke unreached (halt fired first, by design)
- **task-006/013/014** (full sweep): partially executed — llama2/triviaqa cell completed via donor reuse + finalization; llama2/truthfulqa, mistral×2, llama3×2 intentionally NOT run (FR-4.1 halt semantics)
- **task-007** (analysis): executed read-only on the completed cell (screen → grid → gate)
- **task-008** (figures): done — 4 figures from real data (no fabricated cells)
- **task-015** (failsafe): done — pipeline continues via reflection routing

---

## Code Quality Checklist

Based on Validator Agent evaluation (sub-agent, static + runtime + behavioral):

- [✓] Syntax validation passed (35/35 pytest)
- [✓] Type hints compliance (v1 style preserved)
- [✓] API signatures match 03_logic.md (all 15 required symbols verified via Serena)
- [✓] Configuration schema match 03_config.md (17 constants verified, 0 drift)
- [✓] Cross-file dependencies resolved (all modules import in conda env)
- [✓] No obvious anti-patterns (4 advisory issues, none spec-violating)

### Issues Detected

Advisory only (validator adversarial review): double model-load in `run_model` (matches spec pseudo-code), device-unscoped peak-memory print, `analyze_all` lacks per-cell missing-artifact error handling, `question_id` traceability absent for TruthfulQA skips. None blocked validation.

---

## Experiment Results

### Execution Details

| Field | Value |
|-------|-------|
| **Mode** | auto (UNATTENDED), `bash run_experiment.sh` on H100 (CUDA_VISIBLE_DEVICES=1) |
| **Status** | blocked — A2 anchor halt gate fired on first cell (by design) |
| **Duration** | 47 s (smoke 10 + verify 10 GPU regenerations + donor copy/finalize + anchor math) |

### Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Donor protocol identity (label agreement, n=10) | 10/10 | 10/10 | ✅ PASS |
| llama2/triviaqa best intermediate AUROC (L31, adj_kl, selection n=500) | 0.6522 | ≥ 0.55 | ✅ PASS |
| depth_beats_final (0.6522 vs final-layer 0.5928) | True | True | ✅ PASS |
| Degeneracy screen retained layers | 20/32 | ≥ 5 | ✅ PASS |
| A2 anchor: final-layer entropy AUROC vs v1 ref (selection) | 0.5928 vs 0.5186 (Δ +0.0742) | Δ ≤ 0.03 | ❌ FAIL |
| A2 anchor (full-set comparison, like-for-like) | 0.5739 vs 0.5186 (Δ +0.0553) | Δ ≤ 0.03 | ❌ FAIL |
| Existence on all 6 model×dataset cells | 1/6 measured | 6/6 | ⚠️ UNMEASURED (halt) |

Top intermediate signals (llama2/triviaqa selection split): L31 adj_kl 0.6522, L17 adj_kl 0.6145, L30 adj_kl 0.6062, L16 maxprob 0.5909, L20 adj_kl 0.5903.

### Failure Details

- **Reason:** `SystemExit: A2 anchor BROKEN: llama2/triviaqa final-layer entropy AUROC=0.5928 vs reference=0.5186 (delta=+0.0742, tolerance=+/-0.03). HALT per FR-4.1`
- **Classification:** Spec-provenance flaw, NOT an implementation bug. Provenance audit of `H_E1_REFERENCES` (source `_archive/20260804T140137`) shows the reference protocol differs from the current protocol in 6 material ways: random 1000-of-7993 TriviaQA sample (vs validation[:1000]), bare-question prompt (vs Q/A template), bidirectional substring labels (vs normalized-alias exact), generation-time entropy of `generate()` scores (vs teacher-forced logit-lens L32), bfloat16 (vs fp16), full-set evaluation (vs selection split). The anchor is unsatisfiable by construction for any faithful implementation of the current protocol. The donor episode (054934) crashed at finalization before its own anchor check ever ran, so this was never previously detected.
- **Gate behavior:** correct — the fail-fast ordering (cache-reuse cell first) stopped the campaign after 47 s instead of ~2.5 h of GPU sweeps.

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Result** | PARTIAL |
| **Satisfied** | false |
| **Evaluated At** | 2026-08-05T07:47:00+00:00 |

### Criteria Evaluation

| Criterion | Target | Actual | Result |
|-----------|--------|--------|--------|
| Code executes without errors | yes | yes (halt = designed behavior) | ✅ |
| Mechanism correctly implemented | verified | validator + reality check + 35/35 tests | ✅ |
| Metrics measurable | yes | full grid on completed cell | ✅ |
| Screen health (≥5 layers) | ≥ 5 | 20 | ✅ |
| A2 anchor reproduction (±0.03) | all 6 cells | breach on cell 1 (provenance flaw) | ❌ |
| Existence on all 3 models × 2 datasets | 6/6 | 1/6 measured (passes on binding cell) | ❌ (unmeasured) |

Pass rate: 4/6 (67%) → PARTIAL (≥ 50% partial threshold, < 100% pass threshold).

### Failure Analysis

- **Reason:** A2 anchor operationalization adopted cross-protocol reference numbers as a same-protocol gate (Phase 2B/2C spec error, undetectable until the anchor check first executed).
- **Impact:** 5/6 cells unmeasured; dependents h-m1/h-m2/h-m3/h-c1 BLOCKED pending h-e1-v2.
- **Recommendations:**
  - Re-specify the anchor as protocol-internal validity (A2-v2) — done in h-e1-v2
  - Provenance-audit any numeric anchor before adopting it as a halt gate

---

## Reflection Outcome (step-06b)

| Field | Value |
|-------|-------|
| Outcome | **MODIFIED (SELF_MODIFY)** — modification attempt 1 |
| New Hypothesis | **h-e1-v2** (READY → enters Phase 2C) |
| Modification Type | REFINEMENT (anchor operationalization only) |
| Serena Memory | `pivot_h-e1_h-e1-v2` |
| Report | `reflection_report.md` |

**A2-v2 anchor (replaces v1 numeric reproduction):** (a) donor protocol identity via ≥10-example fresh-regeneration label agreement; (b) within-sweep final-layer entropy AUROC as the baseline the best intermediate layer must beat; (c) v1-record direction consistency reported descriptively, not gated. Datasets, models, signals, thresholds, split protocol, and code are unchanged.

Not SUPERSEDED (dependent interfaces — cache schema 5+96 cols, locked test splits — unchanged); not FAIL (methodology demonstrably works on the binding cell).

---

## Next Steps

### 🔁 Workflow continues via h-e1-v2

MUST_WORK gate PARTIAL. The hypothesis was self-modified, not killed.

**Partial Results Preserved:**
- Completed tasks: 15/15 (all code validated)
- Generated files: `code/` (7 modules + 6 test files, 35/35 tests)
- Experiment results: `experiment_results.json` (1 completed cell + full anchor-failure forensics)
- Finalized cache: `results/cache_llama2_triviaqa.csv` (1000 rows, selection/test split seed 42) — **zero-GPU reuse for h-e1-v2**

**Recovery Route:**
- h-e1-v2 (READY) → Phase 2C experiment-design refresh under A2-v2 → Phase 3 (delta-only: re-spec `check_anchor_and_halt`) → Phase 4 re-run
- Dependents h-m1, h-m2, h-m3, h-c1: BLOCKED, awaiting h-e1-v2

---

## Figures

| File | Content |
|------|---------|
| `figures/auroc_vs_depth_llama2_triviaqa.png` | Corrected AUROC vs depth, 3 signals, gate + final-layer lines (headline cell) |
| `figures/anchor_check_llama2_triviaqa.png` | Anchor breach visual: observed (selection/full) vs reference ±0.03 band |
| `figures/degeneracy_screen_llama2_triviaqa.png` | 20/32 retained layers |
| `figures/entropy_heatmap_llama2.png` | Examples × layers entropy, correct vs incorrect groups (FR-5.6) |

No figures fabricated for the 5 unmeasured cells.

---

## Appendix

### Files Reference

| File | Purpose |
|------|---------|
| `04_checkpoint.yaml` | Recovery checkpoint |
| `04_validation.md` | This report |
| `experiment_results.json` | Raw experiment data + anchor forensics |
| `reflection_report.md` | Step-06b reflection analysis |
| `code/` | Validated implementation (reusable for h-e1-v2) |
| `results/` | Finalized llama2/triviaqa cell artifacts |
| `verification_state.yaml` | Updated gate status + h-e1-v2 entry |

### Checkpoint Summary

```yaml
schema_version: "3.5"
hypothesis_id: "h-e1"
created_at: "2026-08-05T07:17:47"
tasks: {total: 15, completed: 15}
coder_validator_cycles: 1
unattended_mode: true
gate_result: PARTIAL
reflection_outcome: MODIFIED
new_hypothesis_id: h-e1-v2
```

### Environment

| Item | Value |
|------|-------|
| Execution Date | 2026-08-05 |
| Mode | UNATTENDED |
| MCP Servers | Archon (task tracking + KB, KB out-of-domain null results recorded), Serena (memory + symbol analysis via validator), ClearThought (reflection) |
| Hardware | 1× H100 NVL (of 5), fp16, batch 1 |
| Env | conda youra-h-e1: python 3.10.20, torch 2.8.0+cu128, transformers 4.57.6 |

---

## Phase 2C Handoff

> **Purpose:** consumed by Phase 2C when processing h-e1-v2 and (later) dependent hypotheses.

### Source Information

| Field | Value |
|-------|-------|
| **Source Hypothesis** | h-e1 |
| **Generated At** | 2026-08-05T07:51:26+00:00 |
| **Gate Result** | PARTIAL → MODIFIED (h-e1-v2) |
| **Ready for Dependents** | No — dependents await h-e1-v2 |

### Proven Components

| Component | File | Type | Evidence | Reusable |
|-----------|------|------|----------|----------|
| `per_layer_lens_signals` | model.py | mechanism | validator + reality check (REAL_MODEL), smoke 33-state assert | ✅ |
| `resume_from_cache` / append-mode resume | run_h_e1.py | infra | 5 dedicated tests (corrupt tail, header guard, skip-written) | ✅ |
| `verify_cache_reuse` + donor short-circuit | run_h_e1.py | infra | 10/10 live label agreement on real donor; finalization test | ✅ |
| `check_anchor_and_halt` | run_h_e1.py | gate | fired correctly in production; 4 tests (pass/breach/pending/single-class) | ✅ (needs A2-v2 re-spec) |
| `degeneracy_screen` → `build_auroc_grid` → `evaluate_gate` | analysis.py | eval | executed on real cell; v1 tests | ✅ |
| `plot_entropy_heatmap` | visualize.py | figure | rendered from real cache; 3 tests | ✅ |
| Finalized llama2/triviaqa cache | results/ | data | 1000 rows, split seed 42, protocol-verified | ✅ zero-GPU |

**Reuse Notes:**
- h-e1-v2 Phase 3 should be delta-only: re-specify `check_anchor_and_halt` per A2-v2; everything else verbatim.
- `results/cache_llama2_triviaqa.csv` is FINALIZED (unlike the pending-split donor) — reuse directly, splits already assigned.
- torch 2.8.0+cu128 required (transformers 4.57.6 incompatible with torch 2.4.x — this env drifted once already; pin it).

### Lessons Learned

#### What Worked Well
- Donor-cache reuse + 10-example protocol-identity verification (0 GPU for 1000 examples)
- Fail-fast anchor ordering: doomed campaign stopped in 47 s instead of ~2.5 h
- Near-verbatim v1 code reuse: 15 tasks, 1 coder-validator cycle, 0 validation failures

#### What Didn't Work
- Cross-protocol numeric anchor: H_E1_REFERENCES came from a 6-way different protocol; ±0.03 reproduction impossible by construction
- Selection-split vs full-set comparison in the anchor check compounded the mismatch (0.5928 vs full-set 0.5739)

#### Unexpected Findings
- adj_kl (adjacent-layer KL) dominates: top-3 intermediate cells are all adj_kl (L31/L17/L30), concentrated late in the stack
- llama2/triviaqa final-layer entropy is NOT at chance under the current protocol (corrected 0.57-0.59, inverted direction) — the "final-layer FAIL 0.5186" premise was protocol-specific

#### Key Insight
> A numeric anchor is only as valid as its provenance: the same model + dataset under a different prompt/label/signal/dtype/sampling protocol produced AUROCs 0.05-0.07 apart. Anchor *direction* transferred across protocols; anchor *magnitude* did not. h-e1-v2 gates on within-protocol quantities only.

### Recommendations for Dependent Hypotheses

**Dependent Hypotheses:** h-m1, h-m2, h-m3, h-c1 (all BLOCKED awaiting h-e1-v2)

#### General Recommendations
- All dependents consume the cache schema (5+96 cols) and locked test splits — both unchanged by the v2 refinement; no dependent redesign needed
- h-m1's "final-layer mean-entropy baseline" comparisons must use within-sweep values (0.5928-class numbers), never v1-record constants

#### Warnings (What to Avoid)
- Do not cite v1-record AUROCs (0.5186 etc.) as same-protocol baselines anywhere downstream (Phase 4.5/6 writing included)
- Do not recompute or unlock test splits — `test_split_locked_llama2_triviaqa.json` already written

#### Suggested Starting Point
- Signals: adj_kl first, layers 28-31 and ~17
- Hyperparameters: N/A (training-free); seed 42, greedy, max_new_tokens 32 — unchanged

---

*This section is auto-generated for Phase 2C consumption. Edit only if necessary.*

---

*Report generated by Phase 4 Implementation & Validation Workflow*
*Anonymous Research Pipeline - Phase 4*
