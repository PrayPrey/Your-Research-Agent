# Product Requirements Document: H-M3 Within-Prompt Quality Probe

**Hypothesis:** H-M3
**Title:** Within-Prompt Quality Probe via Chosen/Rejected Δ-Cosine Analysis
**Pipeline Phase:** 3 — Implementation Planning
**Date:** 2026-03-15
**Gate Type:** SHOULD_WORK
**Task Tier:** FULL (Budget: 30 tasks)
**Base Hypothesis:** h-m2 (INCREMENTAL)

---

## 1. Executive Summary

H-M3 tests whether human semantic accommodation is causally driven by response quality at the **within-prompt level**, using HH-RLHF's unique chosen/rejected pair structure as a natural experiment. For each conversation turn where both a chosen and a rejected response exist, we compute:

```
Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected)
```

If Δ > 0 systematically (E[Δ] > 0 with bootstrap CI lower bound > 0 across ≥ 2/3 operationalizations), this confirms that higher-quality AI responses trigger stronger human semantic accommodation at the within-prompt level — controlling for all prompt-level confounds by design.

This provides the causal mechanism test: H-M1 established tier-monotonicity (across-tier) and H-M2 established directional asymmetry (H→AI vs AI→H), but H-M3 establishes **within-prompt causal ordering**: chosen > rejected for the same human-AI exchange.

---

## 2. Research Context and Motivation

### 2.1 Position in Hypothesis Chain

```
H-E1: C_sem > 0 (VALIDATED ✅) — Semantic accommodation exists
  └─ H-M1: C_sem increases with RLHF tier (VALIDATED ✅) — Tier-monotonicity
       └─ H-M2: C_sem^H←A > C_sem^A←H (VALIDATED ✅) — Directional asymmetry
            └─ H-M3: Δ(chosen-rejected) > 0 [THIS WORK] — Within-prompt quality causal probe
                 └─ H-M4: PM-score predicts C_sem after surface controls [PENDING]
```

### 2.2 Scientific Rationale

H-M1 and H-M2 demonstrated that RLHF tier quality predicts C_sem and that accommodation is asymmetric (humans accommodate more to AI than vice versa). However, these are between-group comparisons. H-M3 uses the HH-RLHF dataset's unique structure where each conversation has both a chosen response (higher quality, RLHF-preferred) and a rejected response (lower quality, not preferred), for the **same prompt context**.

This within-pair design eliminates:
- Prompt-level confounds (same H_t, same conversation history)
- Topic-level confounds (same domain/topic)
- Length confounds (via operationalizations 2 and 3)

### 2.3 Three Operationalizations

To ensure robustness against length and embedding artifacts:

1. **Raw (OP1):** `Δ_raw = cos(H_next, A_chosen) - cos(H_next, A_rejected)` — direct comparison
2. **Length-Matched (OP2):** Truncate A_chosen to |A_rejected| tokens before embedding — controls for response length advantage of chosen responses
3. **Prompt-Projected (OP3):** Project out prompt embedding direction from both A_chosen and A_rejected before computing cosine — controls for prompt-content similarity

**Success criterion:** E[Δ] > 0 with bootstrap 95% CI lower bound > 0 in **≥ 2/3 operationalizations**, conditional on N_pairs ≥ 1000.

---

## 3. Functional Requirements

### 3.1 Data Requirements

| Requirement | Detail |
|-------------|--------|
| **Dataset** | Anthropic/hh-rlhf (HuggingFace) |
| **Splits** | helpful-base (43,835), helpful-rejection-sampled (52,421), helpful-online (22,007) |
| **Pair structure** | Each sample: `{chosen: str, rejected: str}` — full conversation with paired responses |
| **Parsing** | Extract last human turn (H_next) and both AI responses (A_chosen, A_rejected) from conversation text |
| **Minimum pairs** | N_pairs ≥ 1000 per split (empirical verification required; auto-demote gate if <1000) |
| **Cache** | Reuse h-e1/h-m1/h-m2 data cache at `.data_cache/datasets/hh-rlhf` |

### 3.2 Core Computation Requirements

#### 3.2.1 Pair Parser
- Parse HH-RLHF chosen/rejected conversation format
- Extract the final human utterance (H_next) and both AI responses for same prompt
- Handle multi-turn conversation structure (last turn extraction)
- Filter invalid pairs (missing H_next, empty responses, etc.)
- Report N_pairs per split

#### 3.2.2 Delta Computation Engine
```
Input: (H_next_embedding, A_chosen_embedding, A_rejected_embedding)
Output: delta_per_pair (float array), n_valid_pairs (int)

Operationalization 1 (raw): direct cosine difference
Operationalization 2 (length_matched): truncate A_chosen to len(A_rejected) tokens
Operationalization 3 (prompt_projected): project out prompt direction
```

#### 3.2.3 Statistical Analysis
- Bootstrap resampling (B=1000, seed=42) for CI estimation
- One-sample t-test (H0: E[Δ] = 0)
- Effect size: Cohen's d for Δ > 0
- Per-split, per-operationalization, per-model reporting
- Gate evaluation: ≥ 2/3 operationalizations with CI lower > 0

#### 3.2.4 Multi-Model Robustness
- Primary: all-MiniLM-L6-v2
- Robustness: paraphrase-MiniLM-L6-v2, all-mpnet-base-v2
- Consistent Δ > 0 pattern expected across models

### 3.3 Visualization Requirements

| Figure | Description | Priority |
|--------|-------------|----------|
| **Fig 1** | Δ distribution (violin/box) per operationalization — gate metric | MANDATORY |
| **Fig 2** | Bootstrap CI of E[Δ] per operationalization across models | MANDATORY |
| **Fig 3** | Per-split N_pairs bar chart (gate compliance check) | MANDATORY |
| **Fig 4** | Δ distribution by RLHF tier (base/RS/online) | AUTONOMOUS |
| **Fig 5** | Scatter: Δ_raw vs Δ_length_matched correlation | AUTONOMOUS |
| **Fig 6** | Summary heatmap: 3 models × 3 operationalizations × mean Δ | AUTONOMOUS |

### 3.4 Output Requirements

| Output | Path | Description |
|--------|------|-------------|
| Main results | `h-m3/results/delta_results.json` | Per-pair Δ, per-split stats, gate evaluation |
| Visualization | `h-m3/results/figures/` | 6 figures (3 mandatory, 3 autonomous) |
| Validation report | `h-m3/04_validation.md` | Gate result, key findings |
| Checkpoint | `h-m3/04_checkpoint.yaml` | Task tracking (Phase 4) |

---

## 4. Technical Constraints

### 4.1 Codebase Reuse (INCREMENTAL)

h-m3 is INCREMENTAL from h-m2. Reuse the following:

| Module | Location | Reuse Strategy |
|--------|----------|----------------|
| `accommodation.py` | `h-e1/code/` or `h-m1/code/` | Import `compute_cosine_similarity`, `batch_embed` |
| `statistics.py` | `h-e1/code/` or `h-m1/code/` | Import `bootstrap_ci`, `cohens_d`, `mannwhitney_test` |
| `run_experiment.py` | `h-m1/code/` or `h-m2/code/` | Adapt main experiment loop |
| `data_loader.py` | `h-m1/code/` or `h-m2/code/` | Reuse HH-RLHF loader; add chosen/rejected parser |

New modules required:
- `h-m3/code/delta_probe.py` — Core Δ computation with 3 operationalizations
- `h-m3/code/run_experiment.py` — Main entry point for H-M3

### 4.2 Hyperparameters (from h-e1/h-m1 optimal)

```python
BATCH_SIZE = 256
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_SEED = 42
SIGNIFICANCE_LEVEL = 0.05
MIN_N_PAIRS = 1000  # Gate auto-demote threshold
```

### 4.3 Environment

- Python ≥ 3.8
- sentence-transformers ≥ 2.2.0
- datasets (HuggingFace)
- scipy, numpy, matplotlib, seaborn
- Single GPU (CUDA_VISIBLE_DEVICES set by caller)
- Reuse existing conda/venv from h-e1/h-m1 if available

---

## 5. Success Criteria

### 5.1 Gate Evaluation (SHOULD_WORK)

**Primary gate:** E[Δ] > 0 with bootstrap 95% CI lower bound > 0 in ≥ 2/3 operationalizations

**Conditional gate (auto-demote):**
- If N_pairs < 1000 in any split → log warning, continue with available pairs but flag
- If global N_pairs < 1000 → auto-demote gate to MUST_NOT_FAIL (report as inconclusive)

**Full SHOULD_WORK PASS:**
- ≥ 2/3 operationalizations: CI[lower] > 0
- N_pairs ≥ 1000 confirmed
- Consistent sign across ≥ 2/3 models

**Partial PASS (still PASS):**
- 2/3 operationalizations pass with N_pairs ≥ 1000
- Minor model inconsistency in 1/3 models

**FAIL:**
- < 2/3 operationalizations pass gate
- OR N_pairs < 1000 (auto-demote triggered)

### 5.2 Expected Results (Based on H-M1/H-M2 Findings)

Given that H-M1 showed tier-monotonicity (RLHF quality → C_sem) and H-M2 showed directional asymmetry, we expect:
- Δ_raw: E[Δ] ≈ 0.01-0.05 (modest positive effect)
- Length-matched may attenuate (chosen responses tend to be longer), so OP2 is a stricter test
- Prompt-projected may show cleaner signal by removing topic confound

---

## 6. Implementation Phases (Epic Structure)

### Phase A: Environment + Data Setup
- Verify h-m2/h-m1/h-e1 code availability
- Set up h-m3 code directory (symlinks or copies)
- Verify data cache (hh-rlhf already downloaded for h-m1/h-m2)
- Implement chosen/rejected pair parser
- Validate N_pairs (gate pre-check)

### Phase B: Core Delta Engine
- Implement 3 operationalizations in `delta_probe.py`
- Unit tests for each operationalization
- Batch embedding with GPU acceleration
- Per-pair Δ computation and storage

### Phase C: Statistical Analysis
- Bootstrap CI for E[Δ]
- One-sample t-test and Cohen's d
- Per-split, per-model, per-operationalization analysis
- Gate evaluation logic

### Phase D: Multi-Model Robustness
- Extend to paraphrase-MiniLM-L6-v2
- Extend to all-mpnet-base-v2
- Cross-model consistency check

### Phase E: Visualization + Reporting
- 3 mandatory figures
- 3 autonomous figures
- 04_validation.md generation
- Gate result finalization

### Phase F: Integration + Failsafe
- Full pipeline run (all splits, all models, all operationalizations)
- Error handling and graceful degradation
- Checkpoint archiving

---

## 7. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| N_pairs < 1000 in some splits | Low (helpful-base has 43k+ samples) | Gate auto-demote | Report empirical N_pairs early; continue with available pairs |
| Chosen/rejected length confound | Medium | May inflate Δ_raw | Operationalizations 2+3 specifically designed to control this |
| Δ > 0 but small effect size | Medium | Partial PASS | Report Cohen's d; SHOULD_WORK gate doesn't require large d |
| Model encoding artifacts | Low | Minor | Multi-model robustness check |
| Cache stale/missing | Low | Delay | Re-download protocol in data_loader.py |

---

## 8. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| H-E1 code (accommodation.py, statistics.py) | ✅ VALIDATED | Reuse directly |
| H-M1 code (run_experiment.py, data_loader.py) | ✅ VALIDATED | Adapt for chosen/rejected parsing |
| H-M2 code (bidirectional analysis) | ✅ VALIDATED | Reference for embedding patterns |
| HH-RLHF dataset cache | ✅ Available | `.data_cache/datasets/hh-rlhf` |
| SBERT models | ✅ Available | `~/.cache/huggingface/hub/sentence-transformers` |

---

## 9. Out of Scope

- Training or fine-tuning any model
- Modifying the HH-RLHF dataset
- Implementing RLHF training pipeline
- Cross-dataset generalization (focused on HH-RLHF)
- Any comparison beyond the within-prompt Δ analysis
- H-M4's regression analysis (separate hypothesis)

---

## 10. Acceptance Criteria Summary

| Criterion | Requirement |
|-----------|-------------|
| Code runs end-to-end | ✅ No crash, full results |
| N_pairs ≥ 1000 verified | ✅ Empirically confirmed per split |
| ≥ 2/3 operationalizations pass | ✅ E[Δ] > 0, CI lower > 0 |
| ≥ 2/3 models consistent | ✅ Sign agreement |
| 3 mandatory figures generated | ✅ delta_dist, bootstrap_ci, n_pairs_bar |
| 04_validation.md complete | ✅ Gate result recorded |
| Results JSON saved | ✅ delta_results.json |
| Builds on h-m2 codebase | ✅ No redundant reimplementation |
