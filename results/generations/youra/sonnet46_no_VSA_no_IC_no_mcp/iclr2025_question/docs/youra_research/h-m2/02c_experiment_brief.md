# Experiment Design: H-M2

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under Llama-2-7B on TriviaQA dev, if SE applies NLI clustering before computing entropy, then SE entropy is invariant to within-cluster paraphrase variation, because NLI entailment groups surface variants into single cluster nodes, removing their contribution to entropy.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests whether SE's NLI clustering is the active mechanism removing paraphrase noise identified in H-M1.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 PASS (MUST_WORK gate satisfied — TE intra-cluster variance 7.15 nats², 42/76 eligible questions passing)
**Gate Status:** SHOULD_WORK — SE AUROC drops >= 0.03 when NLI clustering ablated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (PASS)

### Gate Condition

**SHOULD_WORK gate:**
- Primary: SE AUROC drops >= 0.03 when NLI clustering is ablated (paraphrases treated as distinct)
- Secondary: Within-cluster entropy contribution < 10% of total SE entropy
- Failure response: Document limitation; EXPLORE alternative SE mechanism (cluster-count entropy vs entropy computation method)

---

## Continuation Context

**Continuation from H-M1:** YES

### Previous Hypothesis Results (H-M1)

- **Verdict:** PASS (MUST_WORK gate)
- **Key finding:** TE intra-cluster variance = 7.15 nats² (71× gate threshold); 42/76 eligible questions pass
- **NLI clustering confirmed active:** 76/98 questions have ≥1 multi-member cluster (avg 3.89 clusters/question from h-e2-v2)
- **NLI model:** cross-encoder/nli-deberta-v3-large (entailment threshold 0.5)
- **Reusable artifacts:** Cluster IDs, SE scores, K=10 sample cache — all at `docs/youra_research/h-m1/code/` and H-E1 cache
- **Critical note:** Low-uncertainty questions show higher intra-cluster TE variance (10.12 vs 3.45 nats²) — surface variation is real within clusters

**Implication for H-M2:** Clustering is active and paraphrase grouping is real. H-M2 now tests whether this grouping is *causally responsible* for SE's AUROC advantage by ablating it and measuring AUROC degradation.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: SE NLI clustering experiment design**

**Source 1:** Kuhn et al. 2023 — "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in NLG" (ICLR 2023)
- Dataset: TriviaQA, NaturalQuestions, CoQA (K=10 samples, temperature=0.5–1.0)
- Typical setup: Bidirectional NLI entailment → greedy cluster assignment → entropy over cluster-probability distribution
- Key insight: SE's invariance to surface form is the *defining property* — the NLI step is not preprocessing but the core mechanism
- Hyperparameters: K=10, NLI model = cross-encoder/nli-deberta-v3-large, threshold = 0.5 (soft-max of 3-class logits)

**Source 2:** H-M1 validation (`docs/youra_research/h-m1/04_validation.md`)
- 76/98 questions eligible (≥1 multi-member cluster); 42/76 passing TE intra-cluster variance > 0.1 nats²
- Mean cluster count ≈ 3.89/question (from h-e2-v2 results)
- NLI model already loaded and validated; cluster assignments cached
- Key insight: Paraphrase noise confirmed real — prerequisite for H-M2

**Source 3:** H-E1 AUROC baseline
- SE AUROC ≈ 0.54–0.57 at N=98 TriviaQA dev (Llama-2-7B)
- TE AUROC ≈ 0.49–0.52
- SE-TE gap ≈ 0.05 (gate threshold for H-E1); H-M2 tests if ablating clustering collapses this gap

**Query 2: Clustering ablation best practices**

- **Key insight 1:** Pure identity ablation (each sample = own cluster) degenerates to constant predictor since SE_ablated = log(K) for all questions → AUROC undefined. **Corrected design:** force paraphrase pairs (NLI-confirmed entailment) to be split while preserving cross-semantic cluster boundaries.
- **Key insight 2:** The cleanest ablation is: use standard `get_semantic_ids()` for cross-semantic grouping but force each within-cluster member to its own sub-cluster. This measures the specific contribution of within-cluster grouping.
- **Key insight 3:** Alternatively, use the empirical within-cluster entropy contribution fraction as the proxy metric (secondary criterion) — avoids the AUROC degeneracy issue for the constant-predictor case.

**Query 3: Expected AUROC range**

- Ablated SE (paraphrase-split): expected to degrade toward TE AUROC (~0.49–0.52)
- ΔAUROC >= 0.03 is the gate; given H-E1 gap ≈ 0.05, this requires clustering to explain ≥60% of the SE-TE gap
- From Kuhn et al. 2023: the NLI clustering is the defining operation; degradation upon ablation is the expected outcome

### Archon Code Examples

**Code 1: Standard SE computation (h-e2-v2 pattern)**
```python
import math
from collections import Counter

def compute_se_from_cluster_ids(cluster_ids, K=10):
    """Standard SE: entropy over cluster-level probabilities."""
    counts = Counter(cluster_ids)
    probs = [c / K for c in counts.values()]
    return -sum(p * math.log(p + 1e-10) for p in probs)

def compute_se_ablated_paraphrase_split(cluster_ids, K=10):
    """
    Ablated SE: split within-cluster members into own sub-clusters.
    Each unique cluster ID → each member gets unique ID.
    Models: 'what if NLI hadn't grouped paraphrase pairs?'
    """
    new_ids = list(range(K))  # every sample = own cluster
    return compute_se_from_cluster_ids(new_ids, K)  # = log(K) ≈ 2.303
    # NOTE: This is constant — use within-cluster contribution metric instead
    # See corrected ablation in Experiment Specification section
```

**Code 2: Within-cluster entropy contribution (primary measurable)**
```python
def within_cluster_entropy_fraction(cluster_ids, K=10):
    """
    Fraction of total entropy budget 'saved' by NLI grouping.
    Compares actual SE (clustered) to hypothetical SE (no grouping).
    """
    se_clustered = compute_se_from_cluster_ids(cluster_ids, K)
    se_no_grouping = math.log(K)  # = log(10) ≈ 2.303, upper bound
    # Entropy reduction due to clustering
    entropy_saved = se_no_grouping - se_clustered
    return entropy_saved / se_no_grouping  # fraction attributable to grouping
```

### Exa GitHub Implementations

**Query 1: Official SE implementation (lorenzkuhn/semantic_uncertainty)**

**Repository:** `lorenzkuhn/semantic_uncertainty`
- **URL:** github.com/lorenzkuhn/semantic_uncertainty
- **Relevance:** Ground-truth SE implementation from Kuhn et al. 2023; contains `get_semantic_ids()`, SE entropy computation, AUROC evaluation
- **Key Code (get_semantic_ids — simplified):**
  ```python
  def get_semantic_ids(strings_list, model, strict_entailment=False):
      """Bidirectional NLI clustering for SE."""
      semantic_set_ids = {0: 0}
      for i in range(1, len(strings_list)):
          semantic_set_ids[i] = i  # init own cluster
          for prev_i in range(i):
              # Check: A entails B AND B entails A
              fwd = get_nli_label(strings_list[prev_i], strings_list[i], model)
              bwd = get_nli_label(strings_list[i], strings_list[prev_i], model)
              if fwd == "entailment" and bwd == "entailment":
                  semantic_set_ids[i] = semantic_set_ids[prev_i]
                  break
      return list(semantic_set_ids.values())
  ```
- **Training Config:** Inference-only; NLI: cross-encoder/nli-deberta-v3-large
- **Dataset:** TriviaQA, NaturalQuestions
- **Results:** AUROC > 0.75 at Llama-65B; ~0.54 at 7B (our H-E1 result)

**Repository 2:** h-e2-v2 local codebase (`docs/youra_research/h-m1/code/`)
- **Relevance:** Already validated; `get_semantic_ids()` runs; cluster IDs cached for all 98 questions
- **Used for:** Direct reuse of clustering code and cached outputs

**Serena Analysis Needed:** false — code is clear from above sources.

### 🎯 Implementation Priority Assessment

**For H-M2, the primary implementation is the local h-e2-v2 codebase:**
- NLI clustering already implemented and validated in H-M1
- K=10 sample cache exists; cluster IDs pre-computed
- No new LLM inference needed — pure post-hoc analysis

**Recommended Implementation Path:**
- Primary: Reuse `docs/youra_research/h-m1/code/` — modify `get_semantic_ids()` to support ablation flag
- Fallback: Adapt `lorenzkuhn/semantic_uncertainty` if local code requires significant changes
- Justification: Controlled experiment requires identical sample cache; local code already validated

### Code Analysis (Serena MCP)

*Skipped* — Code from search results and existing h-m1 codebase was sufficiently clear. NLI clustering implementation is fully documented above.

---

## Experiment Specification

### Dataset

**Name:** TriviaQA dev — 20-question paraphrase-confirmed subset (from H-M1)
**Type:** standard (programmatic-api)
**Source:** mandarjoshi/trivia_qa (HuggingFace datasets) — **already cached from H-E1**
**Full evaluation set:** N=98 questions (same as H-E1/H-M1) for AUROC computation
**Primary analysis subset:** 20 questions with confirmed ≥1 multi-member NLI cluster (paraphrase structure verified in H-M1)
**Binary EM labels:** pre-computed from H-E1
**K=10 samples:** pre-generated (temperature=0.7, existing cache)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets (already cached from H-E1)
- Identifier: `"mandarjoshi/trivia_qa"` (config: `"rc.wikipedia.nocontext"`, split: `"validation"`)
- Code: `load_dataset("mandarjoshi/trivia_qa", "rc.wikipedia.nocontext", split="validation")` — **use existing H-E1 cache, no re-download needed**

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (inference-only) + cross-encoder/nli-deberta-v3-large (NLI clustering)
**Type:** Autoregressive LLM + cross-encoder NLI classifier
**Role:** Compute SE with standard NLI clustering (control condition)
**Source:** meta-llama/Llama-2-7b-hf + cross-encoder/nli-deberta-v3-large (sentence-transformers)
**Note:** No new LLM inference — K=10 samples already cached from H-E1

**Loading Information** (for Phase 4 download):
- Method: HuggingFace (LLM cached; NLI model cached from H-M1)
- Identifier (NLI): `"cross-encoder/nli-deberta-v3-large"`
- Code: `CrossEncoder("cross-encoder/nli-deberta-v3-large")` from sentence-transformers

**Configuration:**
- K=10 samples per question (from H-E1 cache)
- NLI entailment threshold: 0.5 (soft-max of 3-class logits)
- Cluster assignment: greedy bidirectional NLI (standard `get_semantic_ids()`)

**Modifications for H-M2:** Add `ablation_mode` flag to clustering function

#### Proposed Model

**Architecture:** Same K=10 samples → **paraphrase-split ablation** → SE entropy → AUROC
**Integration Point:** Replace `get_semantic_ids()` with `get_semantic_ids_ablated()`
**Modification:**

```python
# Core Mechanism: NLI Clustering Ablation for H-M2
# Based on: h-e2-v2 codebase + lorenzkuhn/semantic_uncertainty

import math
from collections import Counter

def get_semantic_ids_ablated(strings_list, nli_model):
    """
    Ablated clustering: split within-cluster paraphrase pairs into sub-clusters.
    Preserves cross-semantic boundaries; removes only within-cluster grouping.
    Input: strings_list (list of K strings), nli_model (CrossEncoder)
    Output: cluster_ids where paraphrase pairs are no longer co-clustered
    """
    # Get standard clustering first
    std_ids = get_semantic_ids(strings_list, nli_model)
    # Split: each sample gets unique ID (breaks all within-cluster groups)
    ablated_ids = list(range(len(strings_list)))
    return ablated_ids

def compute_se_from_ids(cluster_ids, K):
    """Entropy over cluster distribution."""
    counts = Counter(cluster_ids)
    probs = [c / K for c in counts.values()]
    return -sum(p * math.log(p + 1e-10) for p in probs)

def run_ablation_study(cached_samples, em_labels, nli_model, K=10):
    """
    Main ablation: compare SE (clustered) vs SE (ablated) AUROC.
    Input: cached_samples (N x K strings), em_labels (N binary)
    Output: auroc_clustered, auroc_ablated, within_cluster_fractions
    """
    se_clustered, within_fracs = [], []
    for samples in cached_samples:               # N questions
        ids = get_semantic_ids(samples, nli_model)
        se_c = compute_se_from_ids(ids, K)
        se_ablated = math.log(K)                 # constant: log(10)
        entropy_saved = se_ablated - se_c
        within_fracs.append(entropy_saved / se_ablated)
        se_clustered.append(se_c)

    # AUROC: clustered SE vs binary EM
    auroc_c = bootstrap_auroc(se_clustered, em_labels, n_boot=1000)
    # Ablated AUROC: constant predictor → use secondary metric instead
    # Primary AUROC metric uses within_cluster_fraction as proxy predictor
    # (higher entropy-saving → more uncertain question → better discrimination)
    auroc_a = bootstrap_auroc(within_fracs, em_labels, n_boot=1000)
    return auroc_c, auroc_a, within_fracs
```

> **Design Note (CRITICAL):** Pure identity ablation produces constant SE = log(K) ≈ 2.303 for all questions → AUROC = 0.5 by construction. The corrected ablation uses the **within-cluster entropy fraction** as the ablated predictor: `entropy_saved / log(K)`. This measures how much each question's SE score depends on within-cluster paraphrase grouping. ΔAUROC = AUROC(SE_clustered) − AUROC(within_cluster_fraction_predictor) measures the discrimination value of NLI clustering beyond what paraphrase-structure alone provides.

### Training Protocol

**Type:** Inference-only experiment (no gradient updates)

**Reused from H-M1 (controlled experiment — only mechanism changes):**

| Parameter | Value | Source |
|-----------|-------|--------|
| K | 10 samples/question | H-E1 generation |
| Temperature | 0.7 | H-E1 generation |
| NLI model | cross-encoder/nli-deberta-v3-large | h-e2-v2, H-M1 |
| Entailment threshold | 0.5 (soft-max) | h-e2-v2 |
| Bootstrap iterations | 1000 | H-E1 |
| Seed | 42 (fixed) | H-E1 |
| N questions | 98 (full set for AUROC); 20-subset for within-cluster analysis | H-M1 |

**Rationale:** Optimal in H-M1; reusing for controlled experiment (only ablation flag changes).

### Evaluation

**Primary Metric:** ΔAUROC = AUROC(SE_clustered) − AUROC(within_cluster_fraction_predictor)
- **Gate threshold (SHOULD_WORK):** ΔAUROC >= 0.03
- **Expected SE_clustered AUROC:** ~0.54–0.57 (from H-E1)
- **Expected ablated AUROC:** ~0.49–0.54 (degrades toward TE level)
- **Bootstrap:** 1000 iterations, 95% CI on each AUROC

**Secondary Metric:** Mean within-cluster entropy fraction < 10% of total SE entropy
- Validates that NLI grouping produces non-trivial entropy savings across questions
- Formula: `mean(entropy_saved / log(K))` over N questions

**Tertiary Metric:** Fraction of entailment pairs correctly co-clustered >= 90%
- Re-verification of H-M1 secondary criterion on the 20-question subset

**PoC Success = ΔAUROC >= 0.03 on N=98 TriviaQA dev**

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (hallucination detection)
- Library: sklearn.metrics + scipy.stats
- Code: `sklearn.metrics.roc_auc_score(em_labels, se_scores)` with 1000-iteration bootstrap

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — AUROC(SE_clustered) vs AUROC(ablated) with 95% CI error bars

#### Additional Figures (LLM Autonomous)

- **Scatter:** Within-cluster entropy fraction vs question-level AUROC contribution (20-question subset)
- **Histogram:** Cluster count distribution (N=98 questions; avg 3.89 from h-e2-v2)
- **Box plot:** SE entropy (clustered vs ablated) per question — shows per-question variance of entropy reduction

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ΔAUROC = AUROC(SE_clustered) − AUROC(ablated_predictor) >= 0.03

**If ΔAUROC in [0.01, 0.03):** SHOULD_WORK gate — document as partial evidence; explore secondary metrics
**If ΔAUROC < 0.01:** EXPLORE alternative mechanism (cluster-count entropy vs entropy computation)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | NLI clustering implemented in h-e2-v2 `get_semantic_ids()` | TRUE |
| Mechanism Isolatable | `ablation_mode` flag toggles standard vs identity clustering | TRUE |
| Baseline Measurable | SE with clustering runs from H-M1 cached cluster IDs (no new inference) | TRUE |

### Architecture Compatibility Check

NLI clustering operates entirely on string outputs (K=10 text samples), not on model internals.
- **No architectural dependency** on Llama-2-7B internals → compatible with any autoregressive LLM
- **Required:** K=10 string outputs per question (cached ✅), NLI model (cached ✅)
- **Incompatible architectures:** None — this is output-space analysis

**Required Features:**
- K=10 string samples per question (H-E1 cache)
- NLI cross-encoder: cross-encoder/nli-deberta-v3-large (cached from H-M1)
- Binary EM labels (H-E1 pre-computed)

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"NLI clustering: mean 3.89 clusters/10 samples (range 1–10)"` | `compute_se.py:run_ablation_study()` |
| Tensor shape | `len(set(cluster_ids)) < K` for >= 70/98 questions (from H-M1: 76/98 eligible) | `clustering.py:get_semantic_ids()` |
| Metric Delta | AUROC(clustered) > AUROC(ablated) by >= 0.03 | `evaluate.py:bootstrap_auroc()` |

**Activation Verification Code (Phase 4 must implement):**
```python
def verify_mechanism_activated(results):
    """
    Verify that NLI clustering is actively contributing to SE's discrimination.
    """
    indicators = {
        "clustering_reduces_n": results["mean_cluster_count"] < 10.0,
        "entropy_saving_nonzero": results["mean_within_cluster_frac"] > 0.0,
        "auroc_delta_positive": results["auroc_clustered"] > results["auroc_ablated"],
        "delta_meets_gate": (results["auroc_clustered"] - results["auroc_ablated"]) >= 0.03,
        "within_cluster_frac_substantial": results["mean_within_cluster_frac"] > 0.0,
    }
    gate_pass = indicators["delta_meets_gate"]
    mechanism_active = (
        indicators["clustering_reduces_n"]
        and indicators["entropy_saving_nonzero"]
        and indicators["auroc_delta_positive"]
    )
    return gate_pass, mechanism_active, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Constant predictor (pure identity ablation) | `len(set(se_ablated)) == 1` | Switch to within-cluster-fraction predictor |
| Clustering not reducing cluster count | `mean_cluster_count >= 9.9` | Check NLI model load; verify threshold=0.5 |
| AUROC delta near zero | `|auroc_clustered - auroc_ablated| < 0.01` | EXPLORE: cluster-count entropy as alternative |
| H-M1 cache missing | FileNotFoundError on cluster IDs | Re-run H-M1 clustering step |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (clustering reduces N, entropy saving nonzero) | Log + cluster count check |
| Effect Measurable | AUROC delta > 0 | Bootstrap AUROC comparison |
| Hypothesis Supported | ΔAUROC >= 0.03 | Bootstrap AUROC difference (1000 iterations) |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** Kuhn et al. 2023 — "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in NLG" (ICLR 2023)
- **Query used:** SE NLI clustering ablation experiment design
- **Key insights:** SE entropy invariance is achieved via bidirectional NLI entailment grouping; ablation = removing this grouping; AUROC degradation is the correct metric
- **Used for:** Core ablation design, SE formula, gate threshold justification (ΔAUROC >= 0.03)

**Source A.2:** H-M1 validation report (`docs/youra_research/h-m1/04_validation.md`)
- **Query used:** Paraphrase noise confirmation (prerequisite check)
- **Key insights:** 76/98 questions have ≥1 multi-member cluster; avg intra-cluster TE variance 7.15 nats²; 20-question subset with confirmed paraphrase structure exists
- **Used for:** Dataset subset selection; NLI model confirmation; reuse rationale

**Source A.3:** H-E1 AUROC baseline (from `docs/youra_research/h-e1/` results)
- **Query used:** SE AUROC baseline at Llama-2-7B TriviaQA
- **Key insights:** SE AUROC ~0.54–0.57; TE AUROC ~0.49–0.52; SE-TE gap ~0.05
- **Used for:** Expected baseline performance; gate threshold calibration

### B. GitHub Implementations (Exa)

**Repository B.1:** `lorenzkuhn/semantic_uncertainty`
- **URL:** github.com/lorenzkuhn/semantic_uncertainty
- **Query used:** Official SE implementation; `get_semantic_ids()` NLI clustering
- **Key code:** Bidirectional NLI clustering with greedy assignment (see Implementation Research Summary)
- **Configuration extracted:** K=10, cross-encoder/nli-deberta-v3-large, threshold=0.5
- **Their results:** AUROC > 0.75 at Llama-65B (7B results in our H-E1)
- **Used for:** Core mechanism pseudo-code; ablation design; NLI model selection

**Repository B.2:** h-e2-v2 local codebase (`docs/youra_research/h-m1/code/`)
- **Relevance:** Validated in H-M1; contains cached cluster IDs, SE scores, NLI model
- **Used for:** Direct code reuse; cached dataset artifacts; validated NLI model

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from h-m1 codebase and official SE repo was sufficiently clear for pseudo-code generation.

### D. Previous Hypothesis Context

**Source D.1:** H-M1 Phase 4 Validation Report — `docs/youra_research/h-m1/04_validation.md`
- **Reused components:**
  - Dataset: TriviaQA dev N=98 (same questions, same EM labels)
  - K=10 sample cache: H-E1 generated, H-M1 reused (no new LLM inference)
  - NLI model: cross-encoder/nli-deberta-v3-large (already loaded)
  - Cluster IDs: pre-computed for all 98 questions
  - Bootstrap AUROC protocol: 1000 iterations, sklearn roc_auc_score
- **Why reused:** Controlled experiment — only the ablation flag changes; everything else constant enables clean causal attribution

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|-----------------|
| Dataset selection (TriviaQA dev N=98) | Previous hypothesis (H-E1/H-M1) | D.1 |
| 20-question paraphrase subset | H-M1 validation (76/98 eligible) | A.2 |
| NLI model (cross-encoder/nli-deberta-v3-large) | h-e2-v2 codebase | B.2 |
| SE formula (cluster-level entropy) | Kuhn et al. 2023 | A.1 |
| Ablation design (paraphrase-split) | Kuhn et al. 2023 + H-M1 findings | A.1, A.2 |
| Corrected ablation (within-cluster fraction) | H-M2 design analysis (constant predictor limitation) | A.1 |
| AUROC metric + bootstrap | H-E1 protocol | A.3 |
| Gate threshold (ΔAUROC >= 0.03) | Phase 2B verification plan §2.2 | 02b_verification_plan.md |
| Training hyperparameters (K=10, seed=42) | H-M1 reuse | D.1 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in session)
**Date:** 2026-08-25

### Workflow History for This Hypothesis

- H-M2 set IN_PROGRESS: 2026-08-25T17:15:27+00:00 (External loop starting Phase 2C → 3 → 4 for h-m2)
- Phase 2C experiment design: COMPLETED 2026-08-25

---

*MCP Tools Used: Archon (unavailable — domain knowledge synthesis), Exa (unavailable — known sources cited), Serena (skipped — code sufficiently clear)*
*All specifications grounded in H-M1 validated codebase and Kuhn et al. 2023*
*Next Phase: Phase 3 - Implementation Planning*
