# Experiment Design: h-m3

**Date:** 2026-03-15
**Author:** Anonymous
**Hypothesis Statement:** Within same prompt (chosen/rejected pairs), human follow-up turns show higher semantic similarity to chosen AI responses (higher PM-score) than to rejected responses (lower PM-score): Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected) > 0, surviving ≥ 2/3 length-control operationalizations (raw, length-matched truncation, prompt-projected), conditional on N_pairs ≥ 1000 per tier.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** — Within-prompt PM-quality causal probe via chosen/rejected Δ.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-e1 (VALIDATED, MUST_WORK PASSED ✅), h-m1 (VALIDATED, MUST_WORK PASSED ✅)
**Gate Status:** SHOULD_WORK — auto-demote to exploratory if N_pairs < 1000 per tier

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-e1, h-m1

### Gate Condition

**Gate Type:** SHOULD_WORK

**Pass Condition:**
- E[Δ] > 0 with bootstrap CI lower bound > 0 in ≥ 2/3 operationalizations, conditional on N_pairs ≥ 1000 per tier
- If N_pairs < 1000: auto-demote to exploratory, continue to H-M4 without gate failure

**Fail Action:**
- Demote Δ to null result; document length confound as possible explanation; H-M4 proceeds with reduced causal claim

---

## Continuation Context

**Continuation Experiment:** Yes — h-m3 extends h-e1 (existence) and h-m1 (tier-monotonicity) infrastructure.

**Dataset Continuity:** Reusing Anthropic/hh-rlhf from h-e1/h-m1 (same cache, same splits)
**Rationale:** Enables controlled within-prompt quality probe; only manipulation is chosen vs rejected response quality

**Model Continuity:** Reusing all-MiniLM-L6-v2 + paraphrase-MiniLM-L6-v2 + all-mpnet-base-v2 from h-m1
**Rationale:** Same SBERT models ensure consistency across hypothesis chain; already cached

**Configuration Continuity:** Inherited from h-e1/h-m1 validation reports

### Previous Hypothesis Results (if applicable)

**h-e1 (VALIDATED):**
- C_sem^H←A = 0.3292 (95% CI: [0.3280, 0.3304]) — existence confirmed
- Partner-specificity: cos_actual(0.3534) > cos_topic(0.2688) > cos_random(0.0241)
- n_pairs = 155,362; all Mann-Whitney p=0.0; Cohen d=1.998 (actual vs random)
- All 5 mechanism indicators True

**h-m1 (VALIDATED):**
- J-T p=0.001 across all 3 models (minilm/paraphrase/mpnet)
- Cohen d T1 vs T3: minilm=0.1826, paraphrase=0.2545, mpnet=0.2378
- Tier counts: base(43,835), RS(52,421), online(22,007); total pairs=155,362
- IPW applied (KS triggered): base=0.307, RS=0.336, online=0.364

**h-m2 (VALIDATED):**
- C_sem^H←A > C_sem^A←H in all 9 tier×model combinations
- MiniLM: 0.0853 vs 0.0395 (base), 0.0923 vs 0.0535 (RS), 0.0876 vs 0.0718 (online)
- All Mann-Whitney p<0.05; directional asymmetry confirmed

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1:** "chosen rejected pair semantic similarity RLHF" — 5 results, 0 relevant (diffusion model content)
**Query 2:** "within-prompt preference learning cosine similarity" — 3 results, 0 relevant
**Query 3:** "HH-RLHF chosen rejected response comparison" — 5 results, 0 relevant
**Query 4 (code):** "cosine similarity chosen rejected SBERT pairs" — 5 results, 0 relevant (cuBLAS CUDA ops)
**Query 5 (code):** "paired response comparison bootstrap delta" — 5 results, 0 relevant

**Total Archon queries executed:** 5
**Relevant results:** 0 — Archon KB contains diffusion model content only (consistent with h-m1, h-m2 findings)

### Archon Code Examples

No relevant code examples found. Implementation derived from:
- h-e1 codebase: `code/accommodation.py` (C_sem computation), `code/statistics.py` (bootstrap, Mann-Whitney)
- h-m1 codebase: `code/run_experiment.py` (3-model × 3-tier orchestrator), `code/embedder.py` (tier-namespaced cache)

### Exa GitHub Implementations

**Status:** Unavailable (HTTP 402) — same as h-m1, h-m2 runs.

**Fallback strategy:** Derive implementation from:
1. Established h-e1/h-m1 codebase (incremental extension)
2. HH-RLHF dataset structure documented in Bai et al. 2022 (chosen/rejected JSON fields)
3. Standard SBERT/scipy bootstrap patterns validated in prior phases

### 🎯 Implementation Priority Assessment

**This is an incremental extension of h-e1/h-m1, NOT a paper reproduction experiment.**

**Recommended Implementation Path:**
- **Primary:** Extend h-m1/h-m2 codebase (`code/accommodation.py`, `code/statistics.py`, `code/run_experiment.py`)
- **Fallback:** h-e1 baseline modules if h-m1/h-m2 code unavailable
- **Justification:** h-m3 reuses all infrastructure from prior phases; only new logic is chosen/rejected pair extraction, three-operationalization Δ computation, and N_pairs counting per tier

### Code Analysis (Serena MCP)

*Skipped* — h-m3 is an analytical extension of the h-e1/h-m1 pipeline. No complex model architecture requiring Serena analysis. The mechanism is: (1) extract chosen/rejected conversation pairs from HH-RLHF, (2) encode human follow-up turn H_next and both A_chosen, A_rejected with SBERT, (3) compute Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected) per pair, (4) apply three length-control operationalizations, (5) bootstrap CI for each Δ distribution.

---

## Experiment Specification

### Dataset

**Name:** Anthropic/hh-rlhf (chosen/rejected pairs, helpfulness splits)
**Type:** standard (real dataset, NOT synthetic ✅)
**Source:** HuggingFace Hub — `datasets.load_dataset('Anthropic/hh-rlhf', data_dir=split)`
**Splits:** helpful-base, helpful-rejection-sampled, helpful-online

**Statistics (from h-m1 validation):**
- helpful-base: 43,835 conversations
- helpful-rejection-sampled: 52,421 conversations
- helpful-online: 22,007 conversations
- Total conversations: ~118,263; each has `chosen` and `rejected` fields

**Key dataset structure for h-m3:**
```
{
  "chosen": "Human: {prompt}\n\nAssistant: {chosen_response}\n\nHuman: {human_followup}",
  "rejected": "Human: {prompt}\n\nAssistant: {rejected_response}\n\nHuman: {human_followup_same_or_different}"
}
```

**N_pairs empirical verification (CRITICAL — must run before committing to gate):**
- Filter conversations where chosen and rejected share identical prompt prefix up to first Assistant turn
- Count N_pairs per tier (must be ≥ 1000 for gate evaluation)
- If N_pairs < 1000: auto-demote to exploratory

**Preprocessing:**
- Parse conversation string to extract: prompt (P), A_chosen, H_next (from chosen), A_rejected, H_next_rejected (from rejected)
- Verify H_next is the same human turn in both chosen/rejected (same prompt, different AI response)
- If H_next differs: use chosen-side H_next as the reference (most conservative)
- Text normalization: strip whitespace, handle "Human:"/"Assistant:" prefixes
- Cache: reuse `.data_cache/datasets/hh-rlhf` (already downloaded)

**Augmentation:** None (inference-only)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- Identifier: `"Anthropic/hh-rlhf"`
- Code: `datasets.load_dataset('Anthropic/hh-rlhf', data_dir='helpful-base', cache_dir='.data_cache/datasets/hh-rlhf')`

### Models

#### Baseline Model

**Architecture:** Cosine similarity baseline (Δ = 0 null hypothesis — no quality-driven accommodation)
**Operationalization:** Permutation/shuffle baseline — Δ_shuffle = cos(H_next, A_chosen_shuffled) - cos(H_next, A_rejected_shuffled) where chosen/rejected pairs randomly permuted within same tier

**Configuration:**
- Bootstrap resamples: 1,000 (seed=42)
- Significance level: α = 0.05
- Min N_pairs threshold: 1,000 per tier

**Loading Information** (for Phase 4 download):
- Method: `sentence-transformers` (already cached)
- Identifier: `"all-MiniLM-L6-v2"` (primary); `"paraphrase-MiniLM-L6-v2"`, `"all-mpnet-base-v2"` (robustness)
- Code: `SentenceTransformer('all-MiniLM-L6-v2')`

#### Proposed Model

**Architecture:** Three-operationalization Δ framework on top of SBERT embeddings

**Integration Point:** Extends `accommodation.py::compute_csem()` with new `compute_chosen_rejected_delta()` function

**Core Mechanism Implementation:**

```python
# Core Mechanism: Within-Prompt Chosen/Rejected Semantic Delta
# Based on: h-e1/h-m1 accommodation.py + RLHF pair structure (Bai et al. 2022)
# h-m3 adds three length-control operationalizations

def compute_chosen_rejected_delta(pairs, model, operationalization="raw"):
    """
    Args:
        pairs: list of (H_next, A_chosen, A_rejected) tuples
        model: SentenceTransformer instance
        operationalization: "raw" | "length_matched" | "prompt_projected"
    Returns:
        delta_values: np.array of shape (N_pairs,) — per-pair Δ scores
        n_pairs: int — number of valid pairs
    """
    H_vecs = model.encode([p[0] for p in pairs], batch_size=256, normalize_embeddings=True)
    A_chosen_vecs = model.encode([p[1] for p in pairs], batch_size=256, normalize_embeddings=True)
    A_rej_vecs = model.encode([p[2] for p in pairs], batch_size=256, normalize_embeddings=True)

    if operationalization == "length_matched":
        # Truncate A_chosen to A_rejected token length before encoding
        pairs_trunc = truncate_to_rejected_length(pairs)
        A_chosen_vecs = model.encode([p[1] for p in pairs_trunc], batch_size=256, normalize_embeddings=True)

    elif operationalization == "prompt_projected":
        # Project out prompt embedding direction from A_chosen and A_rejected
        P_vecs = model.encode([p[3] for p in pairs], batch_size=256, normalize_embeddings=True)
        A_chosen_vecs = project_out(A_chosen_vecs, P_vecs)  # A - (A·P)P
        A_rej_vecs = project_out(A_rej_vecs, P_vecs)

    cos_chosen = np.sum(H_vecs * A_chosen_vecs, axis=1)  # normalized → dot = cosine
    cos_rejected = np.sum(H_vecs * A_rej_vecs, axis=1)
    delta_values = cos_chosen - cos_rejected
    return delta_values, len(delta_values)

def bootstrap_delta_ci(delta_values, n_resamples=1000, seed=42):
    """Bootstrap mean Δ with 95% CI. Returns (mean_delta, ci_lower, ci_upper)."""
    rng = np.random.default_rng(seed)
    boot_means = [np.mean(rng.choice(delta_values, len(delta_values))) for _ in range(n_resamples)]
    return np.mean(delta_values), np.percentile(boot_means, 2.5), np.percentile(boot_means, 97.5)
```

### Training Protocol

**This is an analytical/statistical experiment (no gradient-based training).**

**From Previous Hypotheses (h-e1/h-m1) — Reusing:**
- Batch size: 256 (SBERT encoding)
- Bootstrap resamples: 1,000, seed=42 (optimal in h-e1/h-m1)
- KNN k: 5 (topic-matching — not needed for h-m3's within-prompt design)
- Significance level: α = 0.05

**Experiment Execution Protocol:**

```
Phase 1: N_pairs verification
  - Count paired conversations per tier with matching prompts
  - IF any tier < 1000: demote h-m3 to exploratory

Phase 2: Embedding computation (if N_pairs ≥ 1000)
  - Encode H_next, A_chosen, A_rejected for all pairs × 3 models
  - Cache embeddings (reuse from h-e1/h-m1 if available for overlapping turns)

Phase 3: Delta computation (3 operationalizations × 3 models × 3 tiers)
  - raw: direct cosine(H_next, A_chosen) - cosine(H_next, A_rejected)
  - length_matched: truncate A_chosen to A_rejected length, recompute
  - prompt_projected: project out prompt direction, recompute

Phase 4: Statistical tests
  - Bootstrap CI for E[Δ] per operationalization
  - Test: CI lower bound > 0
  - Linear regression: Δ ~ PM_proxy + length + bullet_density + politeness_freq

Phase 5: Gate evaluation
  - Pass: E[Δ] > 0, CI lower bound > 0 in ≥ 2/3 operationalizations
  - Auto-demote condition: N_pairs < 1000
```

**Seeds:** 42 (fixed, inherited from h-e1/h-m1)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success |
|--------|-----------|---------|
| E[Δ_raw] | Mean(cos(H_next, A_chosen) - cos(H_next, A_rejected)) | > 0, CI_lower > 0 |
| E[Δ_length] | Mean delta with length-matched truncation | > 0, CI_lower > 0 |
| E[Δ_projected] | Mean delta with prompt-direction projected out | > 0, CI_lower > 0 |
| N_pairs_per_tier | Valid chosen/rejected pair count per tier | ≥ 1000 (gate prerequisite) |
| β_PM | PM-proxy coefficient in regression model | > 0, p < 0.05 |

**Success Criteria (SHOULD_WORK gate):**
- **Primary:** E[Δ] > 0 with bootstrap CI lower bound > 0 in ≥ 2/3 of {raw, length_matched, prompt_projected}
- **Secondary:** Δ magnitude consistent across tiers; length-matched Δ > 0 (length confound controlled); β_PM > 0 in regression

**Auto-Demote Condition:** N_pairs < 1000 per tier → skip gate evaluation, mark h-m3 as exploratory

**Expected Baseline Performance (from prior work):**
- Prior surface-feature failures: d ∈ [0.036, 0.136] (word_count, hapax_ratio, PM keywords)
- h-e1 SBERT existence: C_sem = 0.3292 (semantic level much larger than surface)
- Expected Δ if hypothesis holds: E[Δ] > 0 with small-to-medium effect (d ~ 0.1-0.3 given h-m1 tier d values)
- If H0 holds: E[Δ] ≈ 0 (chosen and rejected equally close to H_next)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: paired cosine delta / statistical hypothesis test (not classification/regression)
- Library: `scipy.stats` (bootstrap, wilcoxon), `numpy` (cosine via dot product on normalized vectors)
- Code: `scipy.stats.bootstrap((delta_values,), np.mean, n_resamples=1000, random_state=42)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: E[Δ] bar chart for 3 operationalizations × 3 models with bootstrap CIs

#### Additional Figures (LLM Autonomous)

1. **Δ Distribution Plot:** Histogram of per-pair Δ values for each operationalization (shows whether effect is systematic or driven by outliers)
2. **Tier × Operationalization Heatmap:** E[Δ] values across 3 tiers × 3 operationalizations with p-values
3. **Length Confound Analysis:** Scatter plot of Δ_raw vs A_chosen_length - A_rejected_length (shows whether length drives the effect)
4. **N_pairs Bar Chart:** Valid pair counts per tier (shows whether gate prerequisite is met)
5. **Regression Coefficient Plot:** β coefficients from full mediation regression (PM_proxy + surface features)
6. **Model Robustness Grid:** E[Δ] for all 3 SBERT models × 3 operationalizations (3×3 grid)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | HH-RLHF chosen/rejected structure provides genuine within-prompt quality variation | TRUE — confirmed by Bai et al. 2022 dataset design; chosen responses selected by PM from same prompt |
| Mechanism Isolatable | Δ can be enabled (chosen vs rejected) or disabled (shuffle-permuted null) for comparison | TRUE — can permute chosen/rejected labels as null condition |
| Baseline Measurable | E[Δ] = 0 null is directly testable via bootstrap CI | TRUE — baseline is H0: E[Δ] ≤ 0 |

### Architecture Compatibility Check

**This is a statistical measurement pipeline, not a neural architecture.**

- **Required:** SBERT sentence encoder (already validated in h-e1/h-m1) + numpy cosine computation
- **Required:** HH-RLHF dataset with `chosen` and `rejected` fields (confirmed in dataset structure)
- **Incompatible conditions:** If HH-RLHF chosen/rejected do NOT share the same prompt (R3 risk) — verify empirically before proceeding
- **Prerequisite verification:** Must confirm chosen and rejected conversations derive from same H_t (identical prompt prefix before first Assistant turn)

> ⚠️ If chosen/rejected prompts differ, h-m3 must be demoted to exploratory (Assumption A3 violated)

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"N_pairs: {base_count} base, {rs_count} RS, {online_count} online"` | `run_experiment.py::count_pairs()` |
| Tensor Shape | H_vecs.shape = (N_pairs, 384), delta_values.shape = (N_pairs,) | `accommodation.py::compute_chosen_rejected_delta()` |
| Metric Delta | E[Δ_raw] > 0 with CI lower bound > 0 | `statistics.py::bootstrap_delta_ci()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results):
    indicators = {
        "n_pairs_sufficient": results["n_pairs_per_tier_min"] >= 1000,
        "delta_positive": results["mean_delta_raw"] > 0,
        "ci_lower_positive": results["ci_lower_raw"] > 0,
        "operationalizations_pass": sum([
            results["ci_lower_raw"] > 0,
            results["ci_lower_length"] > 0,
            results["ci_lower_projected"] > 0
        ]) >= 2
    }
    gate_pass = indicators["operationalizations_pass"] and indicators["n_pairs_sufficient"]
    return gate_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| N_pairs < 1000 | Count per-tier before analysis | Auto-demote to exploratory; continue to H-M4 |
| Chosen/rejected prompts differ | Verify shared prompt prefix | Demote to exploratory (R3 confirmed) |
| E[Δ] ≤ 0 | Bootstrap CI includes or crosses zero | SHOULD_WORK fail — document as null; H-M4 proceeds with reduced causal claim |
| Length confound dominant | Δ_length ≤ 0 but Δ_raw > 0 | Document length as confound; report as methodological finding |
| Δ_projected ≤ 0 only | 2/3 still pass if raw+length positive | Gate still passes; note topical confound residual |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| N_pairs Sufficient | ≥ 1,000 per tier | Per-tier pair count |
| Mean Δ Positive | E[Δ] > 0 | Bootstrap mean |
| CI Lower Bound | CI_lower > 0 in ≥ 2/3 operationalizations | `scipy.stats.bootstrap` |
| Hypothesis Supported | ≥ 2/3 operationalizations pass CI test | `verify_mechanism_activated()` |

---

## PoC Success Check (SHOULD_WORK)

**SHOULD_WORK Pass Condition:**
1. N_pairs ≥ 1,000 per tier (gate prerequisite)
2. E[Δ] > 0 with CI lower bound > 0 in ≥ 2/3 of {raw, length_matched, prompt_projected}
3. Code runs without error

**Auto-Demote Condition:** N_pairs < 1,000 per tier → h-m3 exploratory; H-M4 proceeds with reduced causal claim (no GATE failure recorded)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Queries Executed:** 8 total (5 in Step 2, 3 in Step 5)
**Relevant Results:** 0 — Archon KB contains diffusion model content (consistent with h-m1/h-m2 findings)
**Used For:** No Archon-derived hyperparameters or code patterns

### B. GitHub Implementations (Exa)

**Status:** Unavailable (HTTP 402) — same as h-m1, h-m2 runs
**Fallback:** Implementation derived from h-e1/h-m1 validated codebase (incremental extension pattern)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — h-m3 is an analytical pipeline extension with no novel architecture requiring semantic analysis. Codebase already analyzed during h-e1/h-m1 phases. The mechanism (chosen/rejected cosine delta) is a straightforward extension of `compute_csem()` in `h-m1/code/accommodation.py`.

### D. Previous Hypothesis Context

**Source:** h-e1/h-m1/h-m2 Phase 4 Validation Reports

**Reused from h-e1/h-m1:**
- Dataset: Anthropic/hh-rlhf (cached, verified)
- SBERT models: all-MiniLM-L6-v2 + paraphrase + mpnet (cached, verified)
- Code: `accommodation.py`, `statistics.py`, `embedder.py`, `data_loader.py`
- Hyperparameters: batch_size=256, bootstrap=1000, seed=42, α=0.05
- **Why reused:** Controlled comparison — only manipulation is chosen vs rejected quality label

**Key lessons from h-m1/h-m2:**
- IPW triggered (KS p < 0.05 for tier distributions) — implement IPW check for tier stratification within h-m3 too
- Tier counts: base(43,835), RS(52,421), online(22,007) — N_pairs per tier will be a subset of these
- All 3 SBERT models showed consistent directional effects in h-m1/h-m2 — expect consistency in h-m3

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A/2B + h-e1/h-m1 | 02b_verification_plan.md §1.3, §2.2 H-M3 |
| Chosen/rejected structure | Paper | Bai et al. 2022 (HH-RLHF dataset paper) |
| N_pairs threshold (≥ 1000) | Phase 2B | 02b_verification_plan.md §1.5 (A5), §2.2 H-M3 |
| Δ operationalization design | Phase 2B | 02b_verification_plan.md §2.2 H-M3 verification protocol |
| SBERT models | h-e1/h-m1 VALIDATED | h-e1/04_validation.md, h-m1/04_validation.md |
| Bootstrap hyperparameters | h-e1/h-m1 VALIDATED | bootstrap=1000, seed=42 inherited |
| Length-control rationale | Phase 2B risk analysis | 02b_verification_plan.md §4.1 R3 (length confound) |
| Prompt-projection control | Phase 2B verification protocol | 02b_verification_plan.md §2.2 H-M3 step 3c |
| Regression controls | Phase 2B | 02b_verification_plan.md §2.2 H-M3 step 5 |
| Core mechanism pseudo-code | h-e1/h-m1 codebase extension | h-m1/code/accommodation.py (incremental) |
| Gate type / success criteria | Phase 2B | 02b_verification_plan.md §3.2 gate table |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-15T13:30:00Z

### Workflow History for This Hypothesis

- 2026-03-15T13:23:26: h-m3 set to IN_PROGRESS (hypothesis loop started Phase 2C)
- 2026-03-15T13:30:00: Phase 2C experiment design IN_PROGRESS

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (8 queries — 0 relevant), Exa (unavailable, 402), Serena (skipped — analytical pipeline)*
*All specifications grounded in: h-e1/h-m1/h-m2 validated codebase + 02b_verification_plan.md*
*Next Phase: Phase 3 - Implementation Planning*
