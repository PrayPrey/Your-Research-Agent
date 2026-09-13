# Experiment Design: H-M2

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Under the Pythia checkpoint trajectory (154 checkpoints × 16 model sizes), cumulative Wikipedia exposure increase during training correlates more strongly with MMLU score improvement than HellaSwag improvement, and Books exposure correlates more strongly with HellaSwag than MMLU, confirmed via Spearman ρ comparison on 3 representative model sizes (70M, 1B, 6.9B).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (Step 2 of 3)** — Tests whether domain-capability alignment (established by H-M1) manifests in training dynamics.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (MUST_WORK ✅ VALIDATED), H-M1 (MUST_WORK ✅ VALIDATED)
**Gate Status:** SHOULD_WORK — ρ(Wikipedia→MMLU) > ρ(Wikipedia→HellaSwag) for ≥2 of 3 model sizes

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM — Step 2 of 3 (Training Dynamics)
- **Prerequisites:** H-E1 (VALIDATED), H-M1 (VALIDATED)

### Gate Condition
**Type:** SHOULD_WORK  
**Pass:** ρ(Wikipedia→MMLU) > ρ(Wikipedia→HellaSwag) for ≥2 of 3 model sizes (70M, 1B, 6.9B); AND ρ(Books→HellaSwag) > ρ(Books→MMLU) for ≥2 of 3 model sizes  
**Fail:** EXPLORE — proceed to H-M3 with limitation documented; correlations may be masked by scale effects

---

## Continuation Context

This is a **continuation experiment** building directly on H-E1 and H-M1.

**Reused outputs from H-E1:**
- Cumulative domain exposure fractions per checkpoint (154 steps × 3 model sizes: 70M, 1B, 6.9B)
- Verified that within-family domain variation is measurable (std > 0.001 for ≥10 domains)

**Reused outputs from H-M1:**
- Confirmed Wikipedia entity density significantly > Books entity density (p < 0.05, η² > 0.1)
- Confirmed Books narrative-coherence proxy significantly > Wikipedia proxy (p < 0.05)

**Implication for H-M2:** The content-level domain differences verified by H-M1 provide the theoretical mechanism for expecting Wikipedia exposure to correlate with MMLU (factual-association tasks) and Books exposure to correlate with HellaSwag (narrative-coherence tasks).

### Previous Hypothesis Results (if applicable)
- **H-E1 VALIDATED:** Domain exposure trajectories measurable; data ordering is non-uniform; panel regression framework applicable.
- **H-M1 VALIDATED:** Domain content differences are statistically significant across The Pile's 22 domains.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Pythia checkpoint benchmark evaluation domain exposure correlation**
- No directly relevant results found. Archon KB is indexed primarily for diffusion model implementations (similarity scores 0.35–0.43, all from wrong domain).
- **Key insight extracted:** No prior implementations of this exact domain-benchmark correlation analysis exist in the KB — confirms novelty of H-M2.

**Query 2: lm-evaluation-harness MMLU HellaSwag checkpoint training dynamics**
- No relevant results (same KB domain mismatch).

**Query 3: Spearman correlation training data domain benchmark specificity**
- No relevant results.

**Assessment:** Archon KB does not contain relevant prior cases for this LLM training dynamics analysis. All implementation guidance sourced from Exa/official documentation below.

### Archon Code Examples

**Query 1: Pythia checkpoint evaluation**
- No relevant code examples (KB is diffusion-focused).

**Query 2: Spearman correlation scipy Fisher z-test**
- No relevant code examples.

**Note:** This is expected given Archon KB content. Exa searches below provide the authoritative implementation sources.

### Exa GitHub Implementations

**Repository 1: EleutherAI/pythia** (⭐2,852)
- **URL:** https://github.com/EleutherAI/pythia
- **Relevance:** Official Pythia repository — primary implementation source for accessing checkpoints and reconstructing training dataloader
- **Architecture used:** GPT-NeoX (autoregressive LM), 8 model sizes 70M–12B, 154 checkpoints each
- **Key infrastructure:**
  - Pre-tokenized Pile data: `EleutherAI/pythia_deduped_pile_idxmaps` (HuggingFace)
  - Dataloader reconstruction: `utils/mmap_dataset.py` + `utils/batch_viewer.py`
  - Checkpoint format: HuggingFace Hub revisions (`revision=step{N}`)
- **Training Config:**
  - Training tokens: ~299B (1 epoch on The Pile)
  - All model sizes see same data in same order
  - Checkpoint steps: 0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, then every 1000 steps
- **Dataset:** The Pile (deduplicated and non-deduplicated), 22 domains
- **Results:** Full benchmark scores at `evals/pythia-v1/*/*` in repo

**Repository 2: EleutherAI/lm-evaluation-harness** (backend for HF LLM Leaderboard)
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance:** Official evaluation framework — used by Pythia paper itself for all benchmark evaluations
- **Key code for checkpoint evaluation:**
  ```bash
  lm_eval --model hf \
      --model_args pretrained=EleutherAI/pythia-160m,revision=step100000,dtype="float" \
      --tasks mmlu,hellaswag \
      --device cuda:0 \
      --batch_size auto:4
  ```
- **Python API:**
  ```python
  import lm_eval
  results = lm_eval.simple_evaluate(
      model="hf",
      model_args="pretrained=EleutherAI/pythia-70m,revision=step143000,dtype=float",
      tasks=["mmlu", "hellaswag"],
      num_fewshot=5,  # MMLU standard
      batch_size="auto",
      device="cuda:0",
  )
  ```
- **MMLU fix:** Use `hendrycksTest-*` tasks with `--num_fewshot 5` (5-shot standard); dataset identifier changed to `cais/mmlu`
- **HellaSwag:** `hellaswag` task, standard 10-shot normalization

**Repository 3: EleutherAI/pile-preshuffled-seeds** (HuggingFace Dataset)
- **URL:** https://huggingface.co/datasets/EleutherAI/pile-preshuffled-seeds
- **Relevance:** Contains precomputed index maps for reproducing exact training data order across all Pythia checkpoints
- **Key files:** `*_doc_idx.npy`, `*_sample_idx.npy`, `*_shuffle_idx.npy`
- **Usage:** Load with `utils/mmap_dataset.py` to reconstruct which documents each checkpoint saw

**Serena Analysis Needed:** False — code from search results is clear for this observational analysis

### 🎯 Implementation Priority Assessment

**This is NOT a paper reproduction experiment** — H-M2 uses the Pythia suite and lm-evaluation-harness as established tools to compute a novel correlation analysis. Priority hierarchy:

1. **Official tools (HIGHEST):** EleutherAI/pythia + EleutherAI/lm-evaluation-harness (both are official infrastructure)
2. **Reference:** scipy.stats for Spearman ρ + Fisher z-test

**Recommended Implementation Path:**
- Primary: EleutherAI/lm-evaluation-harness v0.4 (`lm_eval.simple_evaluate`) + EleutherAI/pythia HF Hub checkpoints
- Fallback: Pre-cached Pythia eval results at `evals/pythia-v1/*/*` in Pythia repo (if compute budget insufficient)
- Justification: Official tools guarantee reproducibility; Pythia paper used lm-evaluation-harness for all evaluations

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. The lm-evaluation-harness Python API and Pythia checkpoint access patterns are straightforward; no complex local codebase requires semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Data Source:** The Pile — via Pythia exact dataloaders (for domain exposure fractions)  
**Benchmark Evaluation Data:** MMLU (full test set, 14,042 questions across 57 subjects) + HellaSwag (full validation set, 10,042 examples)

**Dataset 1: Domain Exposure Fractions (from H-E1)**
- **Name:** The Pile / Pythia preshuffled dataloader indices
- **Type:** standard (real, established)
- **Source:** EleutherAI/pythia repo + HuggingFace `EleutherAI/pythia_deduped_pile_idxmaps`
- **Role:** Provides cumulative_domain_fraction[d, t] for each domain d and checkpoint t (already computed in H-E1)
- **Reuse:** Load H-E1 output directly — no recomputation needed

**Dataset 2: MMLU Benchmark**
- **Name:** Massive Multitask Language Understanding (MMLU)
- **Type:** standard (real, established)
- **Source:** HuggingFace `cais/mmlu` (all subjects)
- **Split:** Test set (full: 14,042 questions)
- **Setting:** 5-shot, multiple choice (A/B/C/D)
- **Contamination:** Apply 13-gram decontamination audit before computing correlations

**Dataset 3: HellaSwag Benchmark**
- **Name:** HellaSwag
- **Type:** standard (real, established)
- **Source:** HuggingFace `Rowan/hellaswag` (via lm-eval-harness built-in)
- **Split:** Validation set (full: 10,042 examples)
- **Setting:** 10-shot, normalization scoring (log-likelihood comparison)
- **Contamination:** Apply 13-gram decontamination audit

**Loading Information** (for Phase 4 download):
- Method: HuggingFace (lm-eval-harness auto-downloads) + numpy memmap (Pythia dataloader)
- Identifier: `cais/mmlu` (MMLU), `Rowan/hellaswag` (HellaSwag), `EleutherAI/pythia_deduped_pile_idxmaps` (Pile)
- Code:
  ```python
  # Benchmarks: loaded automatically by lm-eval-harness
  # Pile dataloader indices (for domain exposure):
  import numpy as np
  indices = np.load("path/to/save/folder/indices.npy")  # from utils/batch_viewer.py
  ```

### Models

#### Baseline Model

**Architecture:** Pythia-70m (smallest representative model)
- **Type:** Autoregressive LM, GPT-NeoX architecture
- **Parameters:** 70M
- **Role in H-M2:** BASELINE — used to establish whether correlation pattern is visible at small scale
- **Checkpoint range:** Steps 0–143,000 (154 checkpoints), subset to ≥13 checkpoints after floor filtering

**Three Representative Model Sizes:**
| Model | Parameters | HuggingFace ID | Rationale |
|-------|------------|----------------|-----------|
| Pythia-70M | 70M | EleutherAI/pythia-70m | Small scale — tests if effect is scale-independent |
| Pythia-1B | 1B | EleutherAI/pythia-1b | Medium scale — central test |
| Pythia-6.9B | 6.9B | EleutherAI/pythia-6.9b | Large scale — prior work shows term-frequency effects emerge in larger models |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers` via `revision=step{N}` parameter
- Identifier: `EleutherAI/pythia-70m`, `EleutherAI/pythia-1b`, `EleutherAI/pythia-6.9b`
- Code:
  ```python
  # Via lm-eval-harness:
  lm_eval --model hf \
      --model_args pretrained=EleutherAI/pythia-70m,revision=step1000,dtype="float" \
      --tasks mmlu,hellaswag \
      --device cuda:0 --batch_size auto:4
  
  # Via Python API:
  import lm_eval
  results = lm_eval.simple_evaluate(
      model="hf",
      model_args="pretrained=EleutherAI/pythia-70m,revision=step1000,dtype=float",
      tasks=["mmlu", "hellaswag"],
      num_fewshot=5,
      batch_size="auto",
  )
  ```

#### Proposed Model

**Architecture:** Same Pythia checkpoints — no architectural modification needed.

H-M2 is a **correlational analysis**, not a model modification experiment. The "proposed model" is the analytical framework:
- **Baseline comparison:** Any single checkpoint score in isolation
- **Proposed analysis:** Spearman ρ between domain exposure trajectory and benchmark score trajectory across 154 checkpoints

**Core Mechanism Implementation:**

```python
# Core Mechanism: Domain-Benchmark Spearman Correlation Analysis
# Based on: scipy.stats.spearmanr + Fisher z-test (scipy.stats.fisherz)
# Source: scipy docs + Biderman et al. 2023 (term-frequency correlation methodology)

import numpy as np
from scipy import stats

def compute_domain_benchmark_correlations(
    domain_exposure: np.ndarray,  # shape: (T, D) — T checkpoints, D domains
    benchmark_scores: dict,        # {"mmlu": (T,), "hellaswag": (T,)}
    floor_threshold: float = 0.30, # filter checkpoints with scores < floor
    model_size: str = "70m"
) -> dict:
    """
    Args:
        domain_exposure: cumulative fraction per domain per checkpoint (from H-E1)
        benchmark_scores: dict of {task: score_array} across T checkpoints
        floor_threshold: remove early checkpoints below random chance
    Returns:
        dict of Spearman rho and p-values per (domain, benchmark) pair
    """
    # Step 1: Filter floor checkpoints (all benchmarks must exceed floor)
    valid_mask = np.all(
        np.stack([benchmark_scores[b] > floor_threshold
                  for b in benchmark_scores], axis=1),
        axis=1
    )
    exposure_filtered = domain_exposure[valid_mask]
    scores_filtered = {b: s[valid_mask] for b, s in benchmark_scores.items()}

    # Step 2: Compute Spearman ρ for each (domain, benchmark) pair
    results = {}
    for domain_idx, domain_name in enumerate(PILE_DOMAINS):
        for benchmark_name, scores in scores_filtered.items():
            rho, p_val = stats.spearmanr(
                exposure_filtered[:, domain_idx], scores
            )
            results[(domain_name, benchmark_name)] = {"rho": rho, "p_val": p_val}

    # Step 3: Fisher z-test to compare ρ(Wikipedia→MMLU) vs ρ(Wikipedia→HellaSwag)
    rho_wiki_mmlu = results[("Wikipedia (en)", "mmlu")]["rho"]
    rho_wiki_hellaswag = results[("Wikipedia (en)", "hellaswag")]["rho"]
    n = valid_mask.sum()
    z_diff, p_fisher = fisher_z_test(rho_wiki_mmlu, rho_wiki_hellaswag, n)
    results["fisher_test_wiki"] = {"z": z_diff, "p": p_fisher,
                                    "directional_confirmed": rho_wiki_mmlu > rho_wiki_hellaswag}
    return results

def fisher_z_test(rho1: float, rho2: float, n: int) -> tuple:
    """One-tailed Fisher z-test for difference between two Spearman correlations."""
    z1 = np.arctanh(rho1)
    z2 = np.arctanh(rho2)
    se = np.sqrt(2.0 / (n - 3))
    z_diff = (z1 - z2) / se
    p_one_tailed = 1 - stats.norm.cdf(z_diff)  # one-tailed: H1: rho1 > rho2
    return z_diff, p_one_tailed
```

### Training Protocol

This is an **observational/correlational analysis** — no model training required. Protocol = data collection + statistical analysis.

**Phase 1: Checkpoint Evaluation (Compute-Intensive)**
- **Framework:** lm-evaluation-harness v0.4 (`pip install lm_eval[hf]`)
- **Checkpoints evaluated:** All 154 per model size × 3 model sizes = 462 evaluations
- **Tasks per checkpoint:** `mmlu` (5-shot, all subjects) + `hellaswag` (10-shot)
- **Batch size:** `auto:4` (automatic detection, recomputed every 4 steps)
- **Device:** CUDA (recommended: ≥16GB VRAM for 6.9B model)
- **Output:** JSON results files per checkpoint, organized by model size

**Checkpoint access pattern:**
```bash
# Steps: 0,1,2,4,8,16,32,64,128,256,512,1000,2000,...,143000
for STEP in 0 1 2 4 8 16 32 64 128 256 512 1000 $(seq 2000 1000 143000); do
    lm_eval --model hf \
        --model_args pretrained=EleutherAI/pythia-70m,revision=step${STEP},dtype=float \
        --tasks hendrycksTest-*,hellaswag \
        --num_fewshot 5 \
        --device cuda:0 --batch_size auto:4 \
        --output_path ./results/pythia-70m/step${STEP}.json
done
```

**Phase 2: Domain Exposure Loading**
- Load H-E1 output: `cumulative_domain_fraction[model_size][domain][checkpoint]`
- Align checkpoint indices with evaluation steps

**Phase 3: Decontamination**
- Apply 13-gram decontamination audit: compare The Pile documents seen by each checkpoint against MMLU/HellaSwag test sets
- Adjust scores: report both raw and contamination-adjusted correlations
- If adjusted delta > 3pp for any benchmark, use adjusted as primary

**Phase 4: Statistical Analysis**
- Optimizer: N/A (observational study)
- Statistical method: `scipy.stats.spearmanr` (nonparametric, handles non-linear monotonic relationships)
- Comparison test: Fisher z-test (one-tailed: H1 = ρ_wiki_mmlu > ρ_wiki_hellaswag)
- Seeds: 1 (deterministic — Spearman ρ has no randomness)
- Multiple testing: Holm-Bonferroni correction across 4 comparisons (2 directional tests × 2 domains)

### Evaluation

**Primary Metrics:**
- `rho_wiki_mmlu`: Spearman ρ(cumulative_Wikipedia_exposure[t], MMLU_score[t]) per model size
- `rho_wiki_hellaswag`: Spearman ρ(cumulative_Wikipedia_exposure[t], HellaSwag_score[t]) per model size
- `rho_books_hellaswag`: Spearman ρ(cumulative_Books_exposure[t], HellaSwag_score[t]) per model size
- `rho_books_mmlu`: Spearman ρ(cumulative_Books_exposure[t], MMLU_score[t]) per model size

**Success Criteria (PoC — directional only):**
- P1: `rho_wiki_mmlu > rho_wiki_hellaswag` for ≥2 of 3 model sizes (confirmed via Fisher z-test)
- P2: `rho_books_hellaswag > rho_books_mmlu` for ≥2 of 3 model sizes

**PoC Pass Condition:** P1 confirmed (primary); P2 as secondary

**Expected Baseline Performance (from Pythia paper + lm-eval-harness issue #497):**
- Pythia-70M MMLU at final checkpoint: ~25% (near random chance)
- Pythia-1B MMLU: ~26–28%
- Pythia-6.9B MMLU: ~26–30%
- Pythia-12B MMLU: ~26.8% (from issue #497 benchmark)
- HellaSwag: All sizes show steady improvement across 154 checkpoints (well-measured signal)
- **Key insight from Pythia paper:** Term-frequency correlation with model performance is an emergent property that strengthens in larger models — H-M2 expects stronger correlation signals at 6.9B vs 70M

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Correlation analysis (not classification/generation)
- Library: `scipy.stats` (spearmanr, norm), `numpy` (arctanh for Fisher z)
- Code:
  ```python
  from scipy import stats
  import numpy as np
  
  # Spearman correlation
  rho, p = stats.spearmanr(exposure_trajectory, benchmark_trajectory)
  
  # Fisher z-test (one-tailed)
  z1, z2 = np.arctanh(rho1), np.arctanh(rho2)
  se = np.sqrt(2.0 / (n - 3))
  z_stat = (z1 - z2) / se
  p_one_tailed = 1 - stats.norm.cdf(z_stat)
  
  # 95% CI for Spearman rho
  stderr = 1.0 / np.sqrt(n - 3)
  delta = 1.96 * stderr
  ci_lower = np.tanh(np.arctanh(rho) - delta)
  ci_upper = np.tanh(np.arctanh(rho) + delta)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of ρ(Wikipedia→MMLU) vs ρ(Wikipedia→HellaSwag) × 3 model sizes, with 95% CIs

#### Additional Figures (LLM Autonomous)
Based on the hypothesis (training dynamics over 154 checkpoints × domain exposure trajectories × benchmark scores), the following visualizations are recommended:

1. **Domain-Benchmark Heatmap:** Full ρ matrix heatmap across top-8 Pile domains × 2 benchmarks × 3 model sizes (3 subplots)
2. **Trajectory Plot:** Wikipedia cumulative exposure vs MMLU/HellaSwag scores over 154 checkpoints for each model size (6 line plots: 3 sizes × 2 benchmarks, with dual y-axis)
3. **Fisher z-test Forest Plot:** Point estimates and 95% CIs for the key directional comparisons (P1: wiki→MMLU vs wiki→HellaSwag; P2: books→HellaSwag vs books→MMLU)
4. **Scale Effect Plot:** How ρ(Wikipedia→MMLU) changes across all 16 model sizes (requires running full suite, optional if compute limited)
5. **Floor Filtering Diagnostic:** Show which checkpoints are filtered by the <30% floor threshold and remaining N

All figures saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E1 validated domain exposure fractions are computable and non-trivial | ✅ TRUE — H-E1 gate passed |
| Mechanism Isolatable | Spearman ρ per (domain, benchmark) pair is computed independently | ✅ TRUE — each pair is independent |
| Baseline Measurable | Null hypothesis: ρ_wiki_mmlu == ρ_wiki_hellaswag (no differential) is testable | ✅ TRUE — Fisher z-test provides H0 |

### Architecture Compatibility Check

**This is not a model modification experiment** — compatibility check applies to the analysis pipeline:

- **Required:** lm-evaluation-harness v0.4 or later; Pythia checkpoints accessible via HF Hub `revision=stepN`; H-E1 domain exposure output in compatible format
- **Required:** scipy ≥ 1.7 (spearmanr + Fisher z); numpy ≥ 1.20 (arctanh)
- **Incompatible setups:** Models without checkpoint revisions on HF Hub; lm-eval-harness versions < 0.4 (MMLU task naming changed in PR #497)

> ⚠️ Phase 4 MUST verify that Pythia checkpoints with `revision=stepN` are accessible before starting batch evaluation. If HF Hub is unavailable, fall back to pre-cached eval results in `EleutherAI/pythia` repo at `evals/pythia-v1/`.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Spearman ρ computed for {domain} × {benchmark}: rho={value}" | correlation_analysis.py:compute_correlations() |
| Data Shape | exposure_filtered.shape == (N_valid_checkpoints, 22) where N_valid > 100 | data_loader.py:filter_floor() |
| Metric Delta | rho_wiki_mmlu - rho_wiki_hellaswag > 0 for ≥2 of 3 model sizes | statistical_test.py:fisher_z_test() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results_by_model_size):
    """Verify that the domain-benchmark correlation mechanism is detectable."""
    p1_confirmed = 0  # count model sizes where rho_wiki_mmlu > rho_wiki_hellaswag
    p2_confirmed = 0  # count model sizes where rho_books_hellaswag > rho_books_mmlu

    for model_size, results in results_by_model_size.items():
        rho_wm = results[("Wikipedia (en)", "mmlu")]["rho"]
        rho_wh = results[("Wikipedia (en)", "hellaswag")]["rho"]
        rho_bh = results[("Books3", "hellaswag")]["rho"]
        rho_bm = results[("Books3", "mmlu")]["rho"]
        n_valid = results["n_valid_checkpoints"]

        print(f"[{model_size}] rho_wiki_mmlu={rho_wm:.3f}, rho_wiki_hellaswag={rho_wh:.3f}")
        print(f"[{model_size}] rho_books_hellaswag={rho_bh:.3f}, rho_books_mmlu={rho_bm:.3f}")
        print(f"[{model_size}] n_valid_checkpoints={n_valid}")

        assert n_valid >= 100, f"Floor filter removed too many checkpoints: {n_valid}"

        if rho_wm > rho_wh:
            p1_confirmed += 1
        if rho_bh > rho_bm:
            p2_confirmed += 1

    indicators = {
        "p1_directional_count": p1_confirmed,
        "p2_directional_count": p2_confirmed,
        "p1_gate_passed": p1_confirmed >= 2,   # ≥2 of 3 model sizes
        "p2_gate_passed": p2_confirmed >= 2,
    }
    mechanism_activated = indicators["p1_gate_passed"]
    return mechanism_activated, indicators
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| P1 Directional | rho_wiki_mmlu > rho_wiki_hellaswag for ≥2 of 3 model sizes | Fisher z-test (one-tailed, p < 0.10 acceptable for SHOULD_WORK gate) |
| P2 Directional | rho_books_hellaswag > rho_books_mmlu for ≥2 of 3 model sizes | Fisher z-test (one-tailed) |
| Floor Filter OK | ≥100 valid checkpoints per model size after filtering | Count after threshold |
| Mechanism Activated | TRUE | verify_mechanism_activated() returns True |
| Hypothesis Supported | P1 gate passed (p1_directional_count ≥ 2) | verify_mechanism_activated()["p1_gate_passed"] == True |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** Archon KB contained no relevant sources for this LLM training dynamics analysis (KB indexed for diffusion models). All implementation sources are from Exa searches below.

### B. GitHub Implementations (Exa)

**Repository 1: EleutherAI/pythia** (⭐2,852)
- **URL:** https://github.com/EleutherAI/pythia
- **Query:** "EleutherAI pythia dataloader pile domain token indices reconstruct training data"
- **Relevance:** Official source for Pythia checkpoints, dataloader reconstruction, and benchmark evaluation infrastructure
- **Key Code (mmap_dataset.py — dataloader index access):**
  ```python
  # utils/mmap_dataset.py — load training batch indices
  import numpy as np
  indices = np.load("path/to/save/folder/indices.npy")
  # indices shape: (N_batches, 2049) — token indices into The Pile
  ```
- **Key discovery:** `utils/batch_viewer.py` saves all batch indices as numpy arrays, enabling reconstruction of which Pile documents each checkpoint saw — the foundation of H-E1's domain exposure computation.
- **Used For:** Domain exposure fraction loading (reuse H-E1 output); checkpoint access pattern for lm-eval

**Repository 2: EleutherAI/lm-evaluation-harness** (HF LLM Leaderboard backend)
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Query:** "lm-evaluation-harness evaluate Pythia model checkpoint HuggingFace MMLU HellaSwag"
- **Key Code (checkpoint evaluation):**
  ```bash
  lm_eval --model hf \
      --model_args pretrained=EleutherAI/pythia-160m,revision=step100000,dtype="float" \
      --tasks lambada_openai,hellaswag \
      --device cuda:0 \
      --batch_size auto:4
  ```
- **Python API (preferred for batch checkpoint evaluation):**
  ```python
  import lm_eval
  results = lm_eval.simple_evaluate(
      model="hf",
      model_args="pretrained=EleutherAI/pythia-70m,revision=step1000,dtype=float",
      tasks=["mmlu", "hellaswag"],
      num_fewshot=5,
      batch_size="auto",
      device="cuda:0",
  )
  score_mmlu = results["results"]["mmlu"]["acc,none"]
  score_hellaswag = results["results"]["hellaswag"]["acc_norm,none"]
  ```
- **Configuration Extracted:**
  - MMLU: 5-shot, `cais/mmlu` dataset (post PR #497 fix)
  - HellaSwag: 10-shot, normalization scoring
  - Batch size: `auto` for VRAM efficiency
- **Results (from PR #497 benchmark):** pythia-12b avg MMLU = 0.268 (5-shot)
- **Used For:** Benchmark score collection across 154 checkpoints × 3 model sizes

**Repository 3: EleutherAI/pile-preshuffled-seeds** (HuggingFace)
- **URL:** https://huggingface.co/datasets/EleutherAI/pile-preshuffled-seeds
- **Query:** "EleutherAI pythia dataloader pile domain"
- **Relevance:** Precomputed index maps for loading preshuffled Pile with exact training data order
- **Used For:** Verify H-E1 domain exposure computation methodology

**Repository 4: Pythia paper (Biderman et al., ICML 2023)**
- **URL:** https://proceedings.mlr.press/v202/biderman23a/biderman23a.pdf
- **Relevance:** Provides methodology for term-frequency × performance correlation analysis (Section 2.6) — directly analogous to H-M2's domain-exposure × benchmark correlation
- **Key insight:** "for both arithmetic and QA experiments, model sizes affect the correlation between average performance and the term frequencies, indicating that this correlation is an emergent property in larger models" — H-M2 expects stronger signals at 6.9B vs 70M
- **Used For:** Methodology grounding (Spearman ρ approach), expected effect size guidance, floor filtering rationale

### C. Code Analysis (Serena)

Serena analysis not performed — code from lm-evaluation-harness and scipy is standard and well-documented. No complex proprietary code requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** H-E1 validation output, H-M1 validation output  
**Reused Components:**
- Domain exposure trajectories: `cumulative_domain_fraction[model_size][domain][t]` (H-E1 output)
- Confirmed domain content distinctions: Wikipedia factual density > Books > GitHub; Books narrative coherence > Wikipedia (H-M1 output)
- Floor filtering threshold: ≥30% on all benchmarks (H-E1 protocol, carried forward)

**Why Reused:** Controlled experimental design — H-M2 adds benchmark evaluation layer on top of H-E1's domain exposure infrastructure

### E. Statistical Methodology Sources

**Fisher z-test for Spearman ρ comparison:**
- Source: scipy.stats documentation + StackExchange stats/18887
- Formula:
  ```
  z = (atanh(rho1) - atanh(rho2)) / sqrt(2 / (n-3))
  p_one_tailed = 1 - Phi(z)  # Phi = normal CDF
  95% CI = [tanh(atanh(rho) ± 1.96/sqrt(n-3))]
  ```
- Used For: P1 test (rho_wiki_mmlu > rho_wiki_hellaswag), P2 test (rho_books_hellaswag > rho_books_mmlu)

### F. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Checkpoint access pattern (revision=stepN) | GitHub (Exa) | Repository B.2 (lm-eval-harness README) |
| MMLU 5-shot evaluation | GitHub (Exa) | Repository B.2 (PR #497 fix) |
| HellaSwag 10-shot normalization | GitHub (Exa) | Repository B.2 (HellaSwag task README) |
| Pythia domain exposure computation | GitHub (Exa) | Repository B.1 (mmap_dataset.py) |
| Domain exposure fractions | Prior hypothesis | H-E1 validated output |
| Domain content distinctions | Prior hypothesis | H-M1 validated output |
| Spearman ρ computation | scipy stdlib | scipy.stats.spearmanr docs |
| Fisher z-test | scipy stdlib + stats.SE/18887 | Repository E |
| Floor filtering (30% threshold) | Paper (Exa) | Repository B.4 (Pythia paper Section 2.5) |
| Expected effect size (emergent at larger scale) | Paper (Exa) | Repository B.4 (Pythia paper Section 2.6) |
| Pile domain taxonomy (22 domains) | Paper | Gao et al. 2020 (The Pile, 2101.00027) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-20

### Workflow History for This Hypothesis
- 2026-08-20T09:38: H-M2 set to IN_PROGRESS (Phase 2C experiment design start)
- 2026-08-20: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results, KB is diffusion-model domain), Exa (GitHub — 4 repositories found), Serena (Code Analysis — skipped, code is clear)*
*All specifications grounded in official EleutherAI implementations and scipy standard library*
*Next Phase: Phase 3 - Implementation Planning*
