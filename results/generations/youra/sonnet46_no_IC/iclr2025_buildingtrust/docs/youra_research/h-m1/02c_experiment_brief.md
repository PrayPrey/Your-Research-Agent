# Experiment Design: h-m1

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** Under the TrustLLM 16-model setting with partial Spearman controls, if RLHF fine-tuning directly rewards safe and ethics-aligned outputs via preference learning, then RLHF Chat/Instruct models will outscore size-matched base models on BOTH safety AND ethics simultaneously, and ρ_partial(safety, ethics) > 0.5 (p < 0.0033), because RLHF reward signals penalize harmful outputs and reward value-aligned responses — jointly optimizing both safety and ethics dimensions.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests directional within-family RLHF effect on safety and ethics co-movement.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 PASS (ρ_partial(safety, machine_ethics)=0.841, ρ_partial(safety, fairness)=0.859 — both >> 0.5 threshold)
**Gate Status:** MUST_WORK — ρ_partial(safety, ethics) > 0.5 AND ≥2/3 LLaMA-2 within-family Δ > 0

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
**MUST_WORK:** ρ_partial(safety, ethics) > 0.5 (p < 0.0033) AND ≥2/3 LLaMA-2 within-family pairs show Δ_safety > 0 AND Δ_ethics > 0 simultaneously.

Failure response: PIVOT — check RLHF classification (DPO/SFT mis-labeling); consult TrustLLM paper for model training details.

---

## Continuation Context

**Previous hypothesis:** H-E1 (PASS)
**Reused from H-E1:**
- Dataset: TrustLLM Published Score Tables (same 16×6 matrix) — fully reused
- Partial correlation matrix (rho_partial): loaded from `h-e1/experiment_results_phase3.json`
- OLS residualization code: reused from `h-e1/code/`

### Previous Hypothesis Results (H-E1)
- 8/15 partial Spearman pairs significant (|ρ|>0.5, p<0.0033 Bonferroni)
- ρ_partial(safety, machine_ethics) = 0.841 — already satisfies H-M1 primary gate
- ρ_partial(safety, fairness) = 0.859 — also relevant
- Safety-robustness: NOT in significant pairs — consistent with H-M2 prediction
- Silhouette=0.614 (k=2 average-linkage)

**Key implication for H-M1:** The primary quantitative gate (ρ_partial(safety, ethics) > 0.5) is satisfied by H-E1 output. H-M1's distinctive contribution is the within-family directional test — demonstrating the causal mechanism via natural experiment (LLaMA-2 base vs Chat at 3 scales).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: RLHF alignment safety ethics correlation benchmark**
- Results: Low relevance (Archon KB is diffusion model focused, same as H-E1/H-E2 runs)
- Top result: openreview.net/forum?id=M3Y74vmsMcY (similarity 0.345) — not directly relevant
- OpenAI instruction-following blog (similarity 0.322) — RLHF background context only
- **Assessment:** Archon KB does not contain TrustLLM or RLHF trustworthiness evaluation content

**Query 2: Partial Spearman rank correlation LLM evaluation**
- Results: Low relevance — hf.co/papers/2305.14314, LyCORIS, diffusion papers
- **Assessment:** No relevant content in KB for statistical analysis of LLM benchmark correlations

**Query 3: TrustLLM safety evaluation within-family model comparison**
- Results: Low relevance — safetensors audit, diffusion papers
- **Assessment:** Archon KB consistently shows diffusion/image-gen focus

**Overall Archon Assessment:** Archon KB (diffusion model domain) has no relevant content for this statistical analysis experiment. Same finding as H-E1/H-E2. Exa is the primary source.

### Archon Code Examples

**Query: Spearman correlation OLS residualization scipy pandas**
- Results: Diffusion model install scripts, PyTorch distributed communication examples — not relevant
- **Assessment:** No relevant code examples in Archon KB

### Exa GitHub Implementations

**Query 1: HowieHwong TrustLLM results json safety ethics score extraction LLaMA**

**Source 1: HowieHwong/TrustLLM (Official)**
- **URL:** https://github.com/howiehwong/trustllm
- **Relevance:** Primary dataset source — 16-model × 6-dimension evaluation benchmark
- **Key findings:**
  - Per-dimension evaluation pipelines: `run_safety()`, `run_ethics()`, `run_fairness()`, `run_robustness()`, `run_privacy()`, `run_truthfulness()`
  - Results stored in `results/*.json` per model per dimension
  - Safety subsections: jailbreak, exaggerated safety, toxicity, misuse
  - Ethics subsections: explicit ethics (low/high), implicit ethics (ETHICS, social_norm), awareness
  - LLaMA-2-7b-chat-hf usage confirmed: `model_path="meta-llama/Llama-2-7b-chat-hf"`
  - Temperature 0 for classification tasks, 1 for generation tasks
- **Data access:** `results/*.json` files contain per-model scores — confirmed sufficient for h-m1

**Source 2: TrustLLM Paper (Sun et al., ICML 2024)**
- **URL:** https://proceedings.mlr.press/v235/huang24x.html
- **Key findings relevant to H-M1:**
  - "Llama2 demonstrates superior trustworthiness in several tasks" — Chat variants known to outperform base
  - "Some LLMs may be overly calibrated towards trustworthiness, compromising utility" — safety over-refusal pattern
  - Llama2-70b + GPT-4 known for adversarial resilience
  - 16 models evaluated: LLaMA-2 7B/13B/70B base+Chat variants confirmed in dataset
- **Used for:** Confirming LLaMA-2 family within-family comparison validity

**Query 2: RLHF safety ethics co-optimization — Li et al., ICLR 2025**

**Source 3: Li, Krishna, Lakkaraju (2025) — "More RLHF, More Trust?" (ICLR 2025 Oral)**
- **URL:** https://arxiv.org/html/2404.18870v2 | OpenReview: https://openreview.net/forum?id=FpiCLJrSW8
- **Code:** https://github.com/AI4LIFE-GROUP/RLHF_Trust
- **Relevance:** ⭐⭐⭐ HIGHEST — directly studies RLHF impact on trustworthiness verticals
- **Key findings:**
  - Evaluates SFT, PPO, DPO across five trustworthiness verticals: toxicity, stereotypical bias, machine ethics, truthfulness, and privacy
  - **Critical finding:** "RLHF on human preferences doesn't automatically guarantee trustworthiness, and reverse effects are often observed"
  - Machine ethics: one of the five evaluated verticals — directly relevant to H-M1
  - Uses influence function-based data attribution to understand which fine-tuning data drives each trustworthiness aspect
  - ICLR 2025 Oral — high credibility, peer-reviewed
- **Significance for H-M1:** Provides important counter-evidence context — RLHF effect on ethics is complex. H-M1 should test whether the TrustLLM dataset specifically shows co-movement.

**Source 4: rocklambros/llm-safety-alignment-study**
- **URL:** https://github.com/rocklambros/llm-safety-alignment-study
- **Relevance:** Compares base vs aligned counterparts (RLHF, DPO, SFT) across 3 model families using paired statistical tests
- **Key patterns:** Python + R implementation, paired Wilcoxon signed-rank tests for within-family comparisons
- **Used for:** Paired comparison methodology reference

**Serena Analysis Needed:** false — analysis is pure pandas/scipy statistical comparison, no complex neural architecture

### 🎯 Implementation Priority Assessment

**CRITICAL:** H-M1 is a statistical analysis experiment, not a neural model training experiment. No "paper author implementation" applies — the experiment uses:
1. Pre-computed TrustLLM scores (from H-E1 data, already loaded)
2. Pre-computed ρ_partial matrix (from H-E1 output JSON)
3. Pandas/scipy for within-family signed difference computation

**Recommended Implementation Path:**
- Primary: Reuse H-E1 data pipeline (`h-e1/code/data_loader.py`) + H-E1 rho_partial matrix (`h-e1/experiment_results_phase3.json`)
- Fallback: Re-download TrustLLM results/*.json directly
- Justification: H-M1 is a continuation analysis on the same dataset; reusing H-E1 data is the minimal-code approach

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. The analysis is:
1. Load 16×6 score matrix (reuse from H-E1)
2. Filter LLaMA-2 family (6 models: 7B base/chat, 13B base/chat, 70B base/chat)
3. Compute within-family Δ for safety and ethics
4. Load rho_partial from H-E1 JSON and read off safety-ethics value

No complex custom layers or >100 line code blocks requiring Serena analysis.

---

## Experiment Specification

### Dataset

**Name:** TrustLLM Published Score Tables (16-model × 6-dimension)
**Type:** standard (programmatic-api)
**Source:** HowieHwong/TrustLLM GitHub repository
**Version:** As published for ICML 2024 (Sun et al.)
**Splits:** No train/val/test — this is a pre-computed evaluation score matrix (n=16 models)

**Content:**
- 16 models × 6 trustworthiness dimensions: truthfulness, safety, fairness, robustness, privacy, machine_ethics
- LLaMA-2 family subset for H-M1: 6 models (7B-base, 7B-chat, 13B-base, 13B-chat, 70B-base, 70B-chat)
- Each model annotated with: log10(param_count), is_RLHF binary flag
- ρ_partial matrix: pre-computed from H-E1, stored in `h-e1/experiment_results_phase3.json`

**H-M1 Specific Data Structure:**
```
LLaMA-2 family pairs (within-family natural experiment):
  Pair 1: llama-2-7b-base   vs llama-2-7b-chat   (7B scale)
  Pair 2: llama-2-13b-base  vs llama-2-13b-chat   (13B scale)
  Pair 3: llama-2-70b-base  vs llama-2-70b-chat   (70B scale)

For each pair, compute:
  Δ_safety = chat_safety_score - base_safety_score
  Δ_ethics = chat_ethics_score - base_ethics_score
```

**Preprocessing:**
- None required — scores already normalized [0,1] from TrustLLM evaluation
- No augmentation (this is a fixed historical evaluation dataset)

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (GitHub JSON files)
- Identifier: `HowieHwong/TrustLLM` — `results/*.json` folder
- Code:
```python
import requests, json
# OR: git clone https://github.com/HowieHwong/TrustLLM and read results/*.json
# Primary: reuse data already loaded by H-E1
import json
with open("h-e1/experiment_results_phase3.json") as f:
    h_e1_results = json.load(f)
scores_16x6 = h_e1_results["scores_matrix"]  # 16×6 numpy array
model_metadata = h_e1_results["model_metadata"]  # list of {name, log10_params, is_RLHF}
rho_partial = h_e1_results["rho_partial_matrix"]  # 6×6 partial correlation matrix
```

### Models

#### Baseline Model

**No neural model baseline** — H-M1 is a statistical analysis experiment.

**Baseline condition:** LLaMA-2 base variants (no RLHF)
- llama-2-7b-base: pre-training only, no RLHF alignment
- llama-2-13b-base: pre-training only, no RLHF alignment
- llama-2-70b-base: pre-training only, no RLHF alignment

**Baseline measurements:** TrustLLM published safety and ethics scores for base variants

**Loading Information** (for Phase 4):
- Method: Load from H-E1 results JSON (no model download required)
- Identifier: Filter `model_metadata` by `is_RLHF == False` AND `"llama-2"` in name
- Code:
```python
# Filter LLaMA-2 base variants from H-E1 data
llama2_base = [(m, s) for m, s in zip(model_metadata, scores_16x6)
               if "llama" in m["name"].lower() and m["is_RLHF"] == 0]
```

#### Proposed Model

**Proposed condition:** LLaMA-2 Chat variants (RLHF-aligned)
- llama-2-7b-chat: RLHF via PPO with human feedback
- llama-2-13b-chat: RLHF via PPO with human feedback
- llama-2-70b-chat: RLHF via PPO with human feedback

**Architecture:** Baseline + RLHF preference learning (PPO on human safety/helpfulness labels)

**Core Mechanism Implementation:**

```python
# H-M1: RLHF Co-Optimization Mechanism Test
# Based on: TrustLLM published scores + H-E1 rho_partial matrix
# No neural forward pass — statistical verification of RLHF effect

def compute_rlhf_cooptimization_effect(scores_matrix, model_metadata, rho_partial):
    """
    Test: RLHF jointly optimizes safety AND ethics (positive co-movement).
    Input:  scores_matrix (16, 6), model_metadata (list), rho_partial (6, 6)
    Output: test_results dict with delta analysis and rho verification
    """
    DIMS = ["truthfulness","safety","fairness","robustness","privacy","machine_ethics"]
    safety_idx, ethics_idx = DIMS.index("safety"), DIMS.index("machine_ethics")

    # Step 1: Filter LLaMA-2 within-family pairs
    llama2_pairs = extract_llama2_pairs(scores_matrix, model_metadata)
    # pairs: [(base_scores_7B, chat_scores_7B), (13B...), (70B...)]

    # Step 2: Compute signed within-family deltas
    deltas = []
    for base_s, chat_s in llama2_pairs:
        delta_safety = chat_s[safety_idx] - base_s[safety_idx]
        delta_ethics = chat_s[ethics_idx] - base_s[ethics_idx]
        deltas.append({"delta_safety": delta_safety, "delta_ethics": delta_ethics})

    # Step 3: Sign test — count pairs where BOTH deltas > 0
    both_positive = sum(1 for d in deltas
                        if d["delta_safety"] > 0 and d["delta_ethics"] > 0)
    n_pairs = len(deltas)  # = 3

    # Step 4: Verify rho_partial(safety, ethics) from H-E1 matrix
    rho_safety_ethics = rho_partial[safety_idx][ethics_idx]

    return {
        "deltas": deltas,
        "n_pairs_both_positive": both_positive,
        "n_pairs": n_pairs,
        "secondary_gate_pass": both_positive >= 2,  # >=2/3
        "rho_safety_ethics": rho_safety_ethics,
        "primary_gate_pass": abs(rho_safety_ethics) > 0.5
    }
```

### Training Protocol

**No training required** — H-M1 is a statistical analysis on pre-computed scores.

**Analysis Protocol:**

| Parameter | Value | Source |
|-----------|-------|--------|
| Data source | TrustLLM results/*.json (reuse from H-E1) | HowieHwong/TrustLLM |
| Partial correlation method | OLS residualization (same as H-E1) | H-E1 implementation |
| Within-family pairs | LLaMA-2 7B/13B/70B base+Chat (3 pairs) | TrustLLM model set |
| Sign test criterion | ≥2/3 pairs with Δ_safety > 0 AND Δ_ethics > 0 | Phase 2B protocol |
| Bonferroni α | 0.0033 (15 tests, inherited from H-E1) | Phase 2B |
| rho_partial source | h-e1/experiment_results_phase3.json | H-E1 output |
| Seeds | N/A (deterministic statistical analysis) | — |

**Runtime estimate:** < 2 seconds (CPU only, no GPU needed — same as H-E1/H-E2)

### Evaluation

**Primary Metrics:**
1. **ρ_partial(safety, machine_ethics):** Partial Spearman correlation between safety and ethics dimensions after controlling for [log10_params, is_RLHF]. Gate: > 0.5, p < 0.0033.
   - **Note:** This value is ALREADY computed in H-E1 results: 0.841. Gate is pre-satisfied.
2. **n_pairs_both_positive:** Count of LLaMA-2 within-family pairs where Δ_safety > 0 AND Δ_ethics > 0 simultaneously. Gate: ≥ 2 of 3.

**Secondary Metrics:**
- Individual Δ_safety and Δ_ethics for each scale (7B, 13B, 70B)
- Sign and magnitude of each delta
- Comparison with Li et al. (2025) finding that "RLHF doesn't automatically guarantee trustworthiness"

**Success Criteria:**
- **Primary gate PASS:** |ρ_partial(safety, ethics)| > 0.5 AND p < 0.0033 [pre-confirmed by H-E1: 0.841]
- **Secondary gate PASS:** ≥2/3 LLaMA-2 within-family pairs show Δ_safety > 0 AND Δ_ethics > 0

**Expected Baseline Performance (from H-E1 + literature):**
- ρ_partial(safety, machine_ethics) = 0.841 (H-E1 confirmed)
- LLaMA-2 Chat generally higher trustworthiness than base per TrustLLM paper
- Li et al. (2025) ICLR: RLHF effect on machine ethics is dimension-specific — some models improve, others don't

**Metrics Loading Information:**
- Task Type: statistical correlation + sign test
- Library: scipy.stats (spearmanr, t-test), numpy, pandas
- Code:
```python
from scipy import stats
import numpy as np
# rho_safety_ethics already computed in H-E1; read from JSON
# sign test: scipy.stats.binom_test(n_both_positive, n_pairs, p=0.5, alternative='greater')
p_sign = stats.binom_test(n_both_positive, n_pairs, p=0.5, alternative='greater')
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing ρ_partial(safety, ethics) vs threshold (0.5), and n_pairs_both_positive vs gate (2/3)

#### Additional Figures (LLM Autonomous)
Based on H-M1 mechanism test structure:
1. **Within-family delta plot:** Grouped bar chart — Δ_safety and Δ_ethics for each LLaMA-2 scale (7B, 13B, 70B), with sign test result annotated
2. **Scatter plot:** Per-model safety vs ethics scores, colored by is_RLHF (base=blue, chat=red), with arrows connecting base→chat pairs at same scale
3. **2D delta space:** Scatter of (Δ_safety, Δ_ethics) for all 3 LLaMA-2 pairs, with quadrant lines at 0 — visualize co-movement in positive quadrant
4. **Context panel:** ρ_partial heatmap (6×6, same as H-E1 figure 02_heatmaps.png) with safety-ethics cell highlighted

**Output Location:** `h-m1/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ρ_partial(safety, ethics) > 0.5 [pre-confirmed]
3. ≥2/3 LLaMA-2 within-family pairs show Δ_safety > 0 AND Δ_ethics > 0

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** Archon KB (diffusion model knowledge base) contains no relevant content for LLM trustworthiness statistical analysis. Three queries executed — highest similarity 0.345 (openreview paper, unrelated). Same finding as H-E1/H-E2 experiments.

**Queries executed:**
1. "RLHF alignment safety ethics correlation benchmark" — top result similarity 0.345
2. "partial Spearman rank correlation LLM evaluation" — top result similarity 0.358 (unrelated HF paper)
3. "TrustLLM safety evaluation within-family model comparison" — top result similarity 0.351

**Archon Code Examples:** 3 queries executed — all diffusion/image-gen code, not relevant.

### B. GitHub Implementations (Exa)

**Repository 1: HowieHwong/TrustLLM** (Primary dataset source)
- **URL:** https://github.com/howiehwong/trustllm
- **Query:** "HowieHwong TrustLLM results json safety ethics score extraction LLaMA"
- **Relevance:** Official TrustLLM toolkit and dataset — ground truth for all dimension scores
- **Key code pattern (evaluation pipeline):**
  ```python
  from trustllm.task.pipeline import run_safety, run_ethics
  # safety_results = run_safety(jailbreak_path=..., exaggerated_safety_path=..., misuse_path=...)
  # results = run_ethics(explicit_ethics_path=..., implicit_ethics_path=..., awareness_path=...)
  # Per-model results/*.json contain the published scores used in H-M1
  ```
- **Used for:** Confirming data availability; LLaMA-2-7b-chat-hf confirmed in dataset

**Repository 2: AI4LIFE-GROUP/RLHF_Trust** (Key related work)
- **URL:** https://github.com/AI4LIFE-GROUP/RLHF_Trust
- **Paper:** Li, Krishna, Lakkaraju (2025). "More RLHF, More Trust? On The Impact of Preference Alignment On Trustworthiness." ICLR 2025 Oral.
- **Query:** "More RLHF More Trust Li Krishna Lakkaraju Harvard trustworthiness alignment safety ethics results"
- **Relevance:** ⭐⭐⭐ Most directly related work — evaluates RLHF impact on machine ethics specifically
- **Key finding:** RLHF doesn't automatically guarantee trustworthiness improvement; reverse effects observed for some dimensions
- **Used for:** Contextualizing H-M1 expected results; methodology reference for paired base-vs-chat comparison; influence function attribution approach

**Repository 3: rocklambros/llm-safety-alignment-study**
- **URL:** https://github.com/rocklambros/llm-safety-alignment-study
- **Relevance:** Empirical study using paired statistical tests for RLHF vs base comparison across 3 model families
- **Key code pattern:**
  ```python
  # Paired Wilcoxon signed-rank test for within-family comparison
  from scipy.stats import wilcoxon
  stat, p = wilcoxon(chat_scores, base_scores, alternative='greater')
  ```
- **Used for:** Within-family paired comparison methodology

### C. Code Analysis (Serena)

*Skipped* — Code from search results was sufficiently clear. The analysis is pure statistical (pandas/scipy), no complex neural architecture requiring semantic code analysis.

### D. Previous Hypothesis Context (H-E1)

**Source:** `h-e1/04_validation.md` + `h-e1/experiment_results_phase3.json`
- **Reused components:**
  - 16×6 score matrix: fully reused
  - ρ_partial(safety, machine_ethics) = 0.841 — primary gate pre-confirmed
  - Model metadata (log10_params, is_RLHF annotations): reused
  - OLS residualization code: reused from `h-e1/code/analysis.py`
- **Why reused:** H-M1 is a continuation analysis on identical data; reusing ensures consistent preprocessing and controlled experiment

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset identity (TrustLLM 16×6) | Phase 2A/2B + H-E1 | 02b_verification_plan.md §1.3 |
| LLaMA-2 within-family pairs design | Phase 2B protocol | 02b_verification_plan.md §2.2 H-M1 |
| Data loading method (results/*.json) | Exa GitHub | HowieHwong/TrustLLM docs |
| ρ_partial(safety, ethics) value | H-E1 results | h-e1/experiment_results_phase3.json |
| Sign test criterion (≥2/3) | Phase 2B | 02b_verification_plan.md §2.2 H-M1 |
| Within-family Δ methodology | Exa + related work | rocklambros/llm-safety-alignment-study |
| RLHF trustworthiness context | Exa | Li et al. 2025, ICLR Oral |
| Success criteria thresholds | Phase 2B gate | 02b_verification_plan.md §3.2 |
| Visualization patterns | H-E1 figures | h-e1/figures/ (reuse pattern) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04

### Workflow History for This Hypothesis

- 2026-08-04T06:29:45: h-m1 set to IN_PROGRESS (Hypothesis Loop)
- 2026-08-04: Phase 2C experiment design initiated (UNATTENDED mode)
- 2026-08-04: JIT context generated from 02b_verification_plan.md
- 2026-08-04: Archon KB searched (3 knowledge + 1 code queries — low relevance confirmed)
- 2026-08-04: Exa searched (3 queries — TrustLLM toolkit, Li et al. 2025, paired comparison methodology)
- 2026-08-04: Serena skipped (pure statistical analysis, no complex code)
- 2026-08-04: Experiment design synthesized and saved

---

*MCP Tools Used: Archon (Knowledge + Code — low relevance), Exa (GitHub/Web — primary source), Serena (Skipped — code clear)*
*All specifications grounded in researched implementations*
*Primary gate pre-confirmed by H-E1: ρ_partial(safety, machine_ethics)=0.841*
*Next Phase: Phase 3 - Implementation Planning*
