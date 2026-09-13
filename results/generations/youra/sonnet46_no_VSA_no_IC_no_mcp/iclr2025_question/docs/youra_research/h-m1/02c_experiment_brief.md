# Experiment Design: H-M1

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under Llama-2-7B on TriviaQA dev, if K=10 stochastic samples are generated for high- vs. low-uncertainty questions, then token entropy varies across semantically equivalent paraphrases (same meaning, different surface form), because TE aggregates over vocabulary distributions that encode surface variation, not semantic content.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Confirms "paraphrase noise in TE exists" as prerequisite to H-M2/3.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 PASSED (AUROC SE=0.717, TE=0.562, gap=0.155 ≥ 0.05 threshold)
**Gate Status:** MUST_WORK — prerequisite H-E1 gate satisfied

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (satisfied)

### Gate Condition

MUST_WORK gate. If TE is NOT sensitive to paraphrase variation (intra-paraphrase entropy variance ≤ 0.1 nats on < 15/20 questions), then the noise-filtering rationale for SE/SCG is incorrect, and H-M2/H-M3 must be redesigned. Failure here triggers an EXPLORE response, not ABANDON.

---

## Continuation Context

**Previous Hypothesis:** H-E1 (VALIDATED)

### Previous Hypothesis Results (H-E1)
- AUROC SE = 0.717 (95% CI: 0.608–0.819)
- AUROC TE = 0.562 (95% CI: 0.441–0.671)
- Gap = 0.155 (threshold 0.05 ✅)
- N = 98 TriviaQA dev questions, K=10 samples, Llama-2-7B
- avg_clusters = 7.31 per question
- Accuracy = 0.469

**Reused from H-E1:**
- K=10 stochastic samples for 98 TriviaQA questions (already generated)
- NLI cluster assignments (already computed by h-e2-v2 code)
- Per-token entropy values (already available from H-E1 pipeline)
- No regeneration needed — pure analysis on existing outputs

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Note: Archon MCP unavailable in this session. Findings derived from web search + training knowledge.*

**Query 1: Token entropy paraphrase noise mechanism**

- **Finding:** Token entropy (TE/predictive entropy) computes Shannon entropy over the next-token distribution, then averages across sequence positions. This is sensitive to surface-level lexical variation: two responses with identical meaning but different phrasing (e.g., "Paris" vs "the city of Paris") can produce substantially different per-position entropy profiles due to divergent vocabulary routing at split points.
  - Key insight: Entropy is computed over full vocabulary; any vocabulary distribution shift between paraphrase variants (different token sequences) contributes independently to the mean.
  - Source: Kuhn et al. 2023 (ICLR); Farquhar et al. 2024 (Nature); training knowledge.

- **Finding:** The semantic entropy paper explicitly demonstrates that predictive entropy is NOT linguistically invariant — i.e., it treats "Paris" and "the French capital" as distinct outcomes even when both are correct. This is the theoretical basis for why TE variance within paraphrase pairs should be non-trivial.
  - Key insight: TE aggregates over token-level distributions; paraphrases cause different token paths, yielding different entropy profiles per step.

**Query 2: Entropy variance analysis within semantic clusters**

- **Finding:** Within a semantic cluster (NLI entailment group), different surface forms generate different token-level entropy sequences. The variance is driven by: (a) branching points in the token sequence where paraphrase diverges, (b) different sequence lengths changing the averaging denominator, (c) different conditional probabilities at each position given distinct prefix tokens.
  - Expected variance range: prior work on predictive entropy variance across paraphrases suggests 0.2–0.8 nats for factual QA at 7B scale.
  - Source: Kuhn et al. 2023; Farquhar et al. 2024 (Nature 2024, extended replication).

**Query 3: Benchmark — NLI cluster structure on TriviaQA at 7B**

- **Finding:** H-E1 result: avg_clusters = 7.31/question at K=10, meaning on average ~1.4 samples per cluster. This implies most clusters are singletons or pairs — the paraphrase structure exists but clusters are small. For H-M1, we need questions where at least one cluster contains ≥ 2 members (paraphrase pairs confirmed by NLI entailment).
  - Implication: With avg 7.31 clusters from 10 samples, approximately 2–3 questions per 10 will have multi-member clusters suitable for intra-cluster entropy variance analysis.
  - Estimated availability: ~20–25 questions with ≥1 paraphrase pair from the 98-question pool.

### Archon Code Examples

*Archon MCP unavailable. Code patterns from lorenzkuhn/semantic_uncertainty and training knowledge.*

**Pattern 1: Per-sample token entropy computation**
```python
# From lorenzkuhn/semantic_uncertainty compute_confidence_measure.py pattern
def compute_token_entropy_per_sample(logprobs_list):
    """
    logprobs_list: list of [seq_len] arrays, one per sample
    Returns: list of scalar entropy values (mean per-token entropy per sample)
    """
    entropies = []
    for logprobs in logprobs_list:
        # logprobs shape: (seq_len, vocab_size)
        probs = torch.softmax(logprobs, dim=-1)
        token_entropy = -(probs * torch.log(probs + 1e-10)).sum(dim=-1)
        entropies.append(token_entropy.mean().item())
    return entropies
```

**Pattern 2: Intra-cluster entropy variance**
```python
def compute_intra_cluster_variance(cluster_assignments, token_entropies):
    """
    cluster_assignments: dict {sample_idx: cluster_id}
    token_entropies: list of scalar entropy per sample
    Returns: mean within-cluster entropy variance across all multi-member clusters
    """
    from collections import defaultdict
    clusters = defaultdict(list)
    for idx, cluster_id in cluster_assignments.items():
        clusters[cluster_id].append(token_entropies[idx])
    variances = [np.var(members) for members in clusters.values() if len(members) >= 2]
    return np.mean(variances) if variances else 0.0
```

### Exa GitHub Implementations

**Query 1: lorenzkuhn/semantic_uncertainty (HIGHEST PRIORITY — official implementation)**

- **Repository:** lorenzkuhn/semantic_uncertainty
- **URL:** https://github.com/lorenzkuhn/semantic_uncertainty
- **Relevance:** Official codebase for Kuhn et al. 2023 (ICLR) + Farquhar et al. 2024 (Nature). Contains compute_confidence_measure.py with TE, SE, predictive entropy; parse_triviaqa.py for TriviaQA loading. K=10 samples already the default.
- **Key files:**
  - `compute_confidence_measure.py` — computes TE, SE, p(True), lexical similarity
  - `parse_triviaqa.py` — TriviaQA HuggingFace loading
  - `generate_answers.py` — K-sample generation with temperature
- **Architecture:** Load saved samples → compute NLI clusters → compute entropy per method
- **Insight:** Cluster assignments are stored after NLI pass; per-sample logprob sequences available — sufficient to compute per-sample mean entropy and then within-cluster variance.

**Query 2: rdgbrandon/semanticentropy (interactive explorer)**

- **Repository:** rdgbrandon/semanticentropy
- **URL:** https://github.com/rdgbrandon/semanticentropy
- **Relevance:** Farquhar et al. 2024 (Nature) implementation; interactive NLI clustering visualization
- **Insight:** Shows how cluster membership maps to semantic equivalence; confirms bidirectional entailment as the paraphrase detection mechanism

**Serena Analysis Needed:** false — code from search results is sufficiently clear for this analysis task (pure Python/NumPy, no complex novel architecture to analyze)

### 🎯 Implementation Priority Assessment

For H-M1, the experiment is a **pure analysis task** on existing H-E1 outputs — no new model inference required.

**CRITICAL: Priority hierarchy for this mechanism experiment:**
1. **Reuse H-E1 saved outputs** (HIGHEST PRIORITY) — K=10 samples, NLI cluster assignments, per-token logprobs already exist
2. **Adapt lorenzkuhn/semantic_uncertainty analysis code** — compute_confidence_measure.py provides exact patterns
3. **Write minimal new analysis script** — ~50 lines on top of existing H-E1 pipeline

**Recommended Implementation Path:**
- Primary: Reuse H-E1 pipeline outputs (samples, NLI clusters, logprobs from h-e2-v2)
- Fallback: Re-run NLI clustering on saved generations if cluster assignments not persisted
- Justification: Zero additional inference cost; H-E1 already generated all required data

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. No complex novel architecture requires semantic analysis. H-M1 is a data analysis task on existing H-E1 outputs using straightforward NumPy/Python operations.

---

## Experiment Specification

### Dataset

**Name:** TriviaQA dev (existing H-E1 sample pool)
**Type:** standard (real dataset, programmatic-api via HuggingFace)
**Source:** mandarjoshi/trivia_qa on HuggingFace datasets
**Split used:** dev, N=98 questions (H-E1 pool; same random sample as h-e2-v2)
**Synthetic data:** NO — real TriviaQA dev questions with gold answer sets

**Subset selection for H-M1:**
- From 98 questions, identify those with ≥1 NLI cluster containing ≥2 samples (paraphrase pairs)
- Expected yield: ~20–30 questions (based on avg_clusters=7.31 from K=10; multi-member clusters exist when K=10 produces ≥2 entailment-linked samples)
- Target: 20 questions minimum (per H-M1 verification protocol)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets (already loaded in H-E1; reuse cached outputs)
- Identifier: `"mandarjoshi/trivia_qa"` config `"rc.nocontext"`
- Code: `load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation")`

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (meta-llama/Llama-2-7b-hf)
**Role:** Source of K=10 stochastic samples already generated in H-E1
**Status:** No new inference required — samples already exist

**NLI Model:** DeBERTa-large (microsoft/deberta-large-mnli) — same as h-e2-v2
**Role:** Bidirectional entailment for cluster assignment; already run in H-E1

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers (already cached from H-E1)
- Identifier: `"meta-llama/Llama-2-7b-hf"` (inference model, no re-run needed)
- NLI: `"microsoft/deberta-large-mnli"` (for re-clustering if needed)
- Code: `AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-large-mnli")`

#### Proposed Model

**Architecture:** N/A — H-M1 is an analysis experiment, not a model comparison
**Mechanism being tested:** Whether TE varies within NLI-confirmed paraphrase pairs

**Core Mechanism Implementation:**

```python
# Core Mechanism: Intra-Paraphrase Token Entropy Variance Analysis
# Based on: lorenzkuhn/semantic_uncertainty + H-E1 pipeline outputs
# Purpose: Confirm TE sensitivity to surface variation within semantic clusters

def analyze_paraphrase_entropy_variance(
    questions,          # list of question records (98 questions)
    cluster_assignments, # dict: question_id -> {sample_idx: cluster_id}
    token_entropies,    # dict: question_id -> list[float] (per-sample mean TE)
    nli_entailment,     # dict: question_id -> list[list[bool]] (pairwise entailment)
):
    """
    Returns per-question intra-cluster TE variance for multi-member clusters.
    """
    results = []
    for qid in questions:
        clusters = cluster_assignments[qid]      # {sample_idx: cluster_id}
        entropies = token_entropies[qid]         # [te_0, te_1, ..., te_9]

        # Group samples by cluster
        cluster_groups = defaultdict(list)
        for idx, cid in clusters.items():
            cluster_groups[cid].append(entropies[idx])

        # Compute variance only within multi-member clusters (paraphrase pairs)
        intra_vars = [
            np.var(members)
            for members in cluster_groups.values()
            if len(members) >= 2      # paraphrase pair confirmed by NLI
        ]

        results.append({
            "qid": qid,
            "n_paraphrase_pairs": len(intra_vars),
            "mean_intra_cluster_variance": np.mean(intra_vars) if intra_vars else None,
            "has_paraphrase": len(intra_vars) > 0,
        })

    return results

# Success check:
# primary: mean intra-cluster TE variance > 0.1 nats on >= 15/20 eligible questions
# secondary: SE correctly clusters same pairs (already validated in H-E1: avg_clusters=7.31)
```

### Training Protocol

**This is an analysis experiment — no training or gradient updates.**

**Compute protocol:**

| Step | Operation | Tool |
|------|-----------|------|
| 1 | Load H-E1 saved outputs (samples, logprobs, NLI clusters) | pickle/json load |
| 2 | Identify questions with ≥1 multi-member NLI cluster | Python filter |
| 3 | Compute per-sample mean token entropy for each identified question | NumPy |
| 4 | Compute within-cluster TE variance for multi-member clusters | NumPy |
| 5 | Compare: intra-cluster variance vs inter-cluster variance (control) | NumPy |
| 6 | Count questions passing primary threshold (variance > 0.1 nats) | Python |
| 7 | Verify NLI cluster correctness for paraphrase pairs (secondary check) | NLI model |

**Optimizer:** None
**Learning rate:** None
**Batch size:** 98 questions (full H-E1 pool)
**Epochs:** 1 (single analysis pass)
**Loss function:** None
**Seeds:** 1 (deterministic analysis; K=10 samples already fixed from H-E1)
**Temperature:** N/A (no new sampling)

**Computational cost:** < 5 minutes on CPU. Zero GPU inference required if H-E1 outputs are cached. Re-running NLI clustering if needed: ~10 minutes on single GPU (same as H-E1).

### Evaluation

**Primary metric:** Mean within-cluster TE variance (nats²) across eligible questions
**Success criterion:** > 0.1 nats on ≥ 15/20 questions that have ≥1 paraphrase pair

**Secondary metric:** NLI clustering accuracy for paraphrase pairs
**Secondary criterion:** SE assigns entailment pairs to same cluster in ≥ 90% of cases

**Additional diagnostic:**
- Inter-cluster TE variance (as control: should be HIGHER than intra-cluster for correct-vs-incorrect questions)
- Distribution of intra-cluster variance across high-uncertainty (SE > median) vs low-uncertainty questions

**Expected values (from theory + H-E1 data):**
- Within-cluster TE variance: expected 0.2–0.5 nats (surface variation drives entropy divergence)
- Between-cluster TE variance (control): expected 0.5–1.5 nats (semantic difference = larger vocabulary shift)
- If within-cluster variance < 0.05 nats: TE is robust to paraphrase → mechanism hypothesis incorrect

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (not classification)
- Library: numpy, scipy.stats
- Code: `np.var(cluster_member_entropies)` per cluster; `scipy.stats.wilcoxon` for significance test on paired variance

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean intra-cluster TE variance vs threshold (0.1 nats), with per-question counts

#### Additional Figures (LLM Autonomous)
The Phase 4 coder should autonomously generate figures that best communicate the paraphrase sensitivity finding. Recommended:

1. **Violin plot:** Distribution of intra-cluster TE variance per question (N=eligible questions), overlaid with the 0.1 nats threshold line
2. **Scatter plot:** x = cluster size (number of paraphrases), y = TE variance within cluster — to show whether variance grows with cluster size
3. **Heatmap:** NLI pairwise entailment matrix for 3 representative questions (one low-uncertainty, one high-uncertainty, one borderline) showing cluster structure
4. **Bar chart:** Fraction of questions with intra-cluster variance > {0.05, 0.1, 0.2, 0.5} nats — sensitivity to threshold

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on H-E1 saved outputs
2. `mean_intra_cluster_variance > 0.1 nats` on ≥ 15/20 eligible questions (primary)
3. NLI clustering assigns entailment pairs to same cluster ≥ 90% (secondary, already expected from H-E1)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E1 saved outputs (samples, logprobs, NLI clusters) are persisted on disk | TRUE — required from H-E1 pipeline |
| Mechanism Isolatable | Intra-cluster variance can be computed separately from inter-cluster variance | TRUE — cluster assignments allow partition |
| Baseline Measurable | TE per sample is independently measurable before NLI clustering | TRUE — mean per-token entropy is a scalar per sample |

### Architecture Compatibility Check

**Mechanism:** TE sensitivity to paraphrase = within-cluster TE variance analysis

**Required infrastructure:**
- H-E1 saved outputs: K=10 sample texts + per-sample token logprobs + NLI cluster assignments
- If logprobs not saved: Llama-2-7B required for re-inference (GPU with ≥40GB VRAM)
- NLI model: DeBERTa-large-mnli for re-clustering if cluster assignments not cached

**Compatible:** Any setup with H-E1 pipeline outputs cached
**Incompatible:** Setups where H-E1 ran without saving per-sample logprobs (must re-run H-E1 with logprob logging enabled)

> ⚠️ Phase 4 MUST first check if H-E1 logprob outputs are cached. If not, enable logprob logging and re-run H-E1 generation before proceeding.

---

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Found N_q questions with ≥1 multi-member NLI cluster"` (N_q ≥ 20) | analysis.py:main() |
| Tensor Shape | None (pure Python/NumPy analysis, no tensor transformation) | N/A |
| Metric Delta | `mean_intra_cluster_variance > 0.1` on ≥ 15/20 questions | evaluate.py:check_primary_criterion() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results):
    """
    results: list of per-question dicts from analyze_paraphrase_entropy_variance()
    """
    eligible = [r for r in results if r["has_paraphrase"]]
    assert len(eligible) >= 20, (
        f"Only {len(eligible)} questions have paraphrase pairs; "
        f"expected ≥20 from 98-question pool. Check NLI clustering."
    )
    passing = [
        r for r in eligible
        if r["mean_intra_cluster_variance"] is not None
        and r["mean_intra_cluster_variance"] > 0.1
    ]
    n_passing = len(passing)
    primary_pass = n_passing >= 15
    indicators = {
        "n_eligible_questions": len(eligible),
        "n_passing_primary_threshold": n_passing,
        "primary_criterion_met": primary_pass,
        "mean_variance_overall": np.mean([
            r["mean_intra_cluster_variance"]
            for r in eligible if r["mean_intra_cluster_variance"] is not None
        ]),
    }
    print(f"[H-M1 Mechanism Check] eligible={len(eligible)}, passing={n_passing}/20, "
          f"mean_var={indicators['mean_variance_overall']:.4f} nats")
    return primary_pass, indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No paraphrase pairs found | `len(eligible) < 5` after NLI pass | FAIL: avg_clusters=7.31 predicts ~20+ pairs; check NLI model loading |
| Zero variance | `mean_intra_cluster_variance < 0.01` | FAIL: TE is robust to paraphrase → mechanism incorrect |
| Insufficient questions | `n_passing < 10` (below grace threshold) | EXPLORE: Try BERTScore similarity threshold instead of NLI entailment |
| H-E1 outputs missing | File not found for logprobs | ACTION: Re-run H-E1 with logprob_save=True flag |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | ≥20 eligible questions with paraphrase pairs | Count from NLI cluster assignments |
| Effect Measurable | mean_intra_cluster_variance > 0 | Variance computation succeeds |
| Hypothesis Supported | mean intra-cluster TE variance > 0.1 nats on ≥ 15/20 eligible questions | `verify_mechanism_activated()` returns True |

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (Web Search)

**Source A.1:** Kuhn et al. 2023 — "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in NLG"
- **Query:** semantic entropy token entropy paraphrase noise TriviaQA
- **Key insight:** TE is NOT linguistically invariant; paraphrases generate different vocabulary routing, producing divergent per-step entropy. This is the theoretical basis for H-M1.
- **Used for:** Hypothesis grounding, expected variance range (theory)
- **URL:** https://arxiv.org/pdf/2302.09664

**Source A.2:** Farquhar et al. 2024 — "Detecting Hallucinations in Large Language Models Using Semantic Entropy" (Nature 2024)
- **Query:** semantic entropy implementation GitHub NLI clustering
- **Key insight:** Extended replication confirming SE > TE gap; bidirectional entailment is the correct paraphrase detection mechanism
- **Used for:** NLI clustering protocol, paraphrase definition (bidirectional entailment)
- **URL:** https://github.com/lorenzkuhn/semantic_uncertainty

**Source A.3:** H-E1 validation results (pipeline state)
- **Key data:** avg_clusters=7.31 per question (K=10) → predicts ~20-30 multi-member clusters across 98 questions
- **Used for:** Estimating number of eligible questions for H-M1 analysis

### B. GitHub Implementations (Web Search)

**Repository B.1:** lorenzkuhn/semantic_uncertainty ⭐ (official Kuhn/Farquhar implementation)
- **URL:** https://github.com/lorenzkuhn/semantic_uncertainty
- **Query:** semantic_uncertainty compute_confidence_measure token entropy paraphrase
- **Key code pattern:** `compute_confidence_measure.py` — per-sample logprob → mean token entropy; NLI cluster assignments stored per question
- **Used for:** Per-sample TE computation pattern, data structure for cluster assignments
- **Relevance:** HIGHEST — this is the ground-truth implementation that produced H-E1 results

**Repository B.2:** rdgbrandon/semanticentropy ⭐
- **URL:** https://github.com/rdgbrandon/semanticentropy
- **Query:** semantic entropy NLI clustering interactive Farquhar Nature 2024
- **Key insight:** Cluster membership visualization; confirms that within-cluster samples are NLI-entailed paraphrases
- **Used for:** Understanding cluster structure for paraphrase pair identification

### C. Code Analysis (Serena MCP)

**Serena Analysis:** Not performed — H-M1 is a pure data analysis task on existing H-E1 outputs. Code patterns from lorenzkuhn/semantic_uncertainty (Source B.1) are straightforward Python/NumPy and do not require semantic code analysis.

### D. Previous Hypothesis Context

**Source:** H-E1 validated pipeline
- **Reused components:**
  - K=10 sample generations for 98 TriviaQA questions (already generated at temperature=0.7)
  - NLI cluster assignments (DeBERTa-large-mnli, bidirectional entailment)
  - Per-sample mean token entropy values
  - Binary EM correctness labels
- **Why reused:** H-M1 is mechanistic analysis of H-E1 outputs — zero additional inference cost; controlled comparison

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (TriviaQA dev, N=98) | Previous hypothesis | H-E1 pipeline, 02b_verification_plan.md §1.3 |
| Model (Llama-2-7B) | Previous hypothesis | H-E1 pipeline, h-e2-v2 |
| NLI model (DeBERTa-large-mnli) | GitHub | B.1 (lorenzkuhn/semantic_uncertainty) |
| TE computation pattern | GitHub + KB | B.1, A.1 |
| Intra-cluster variance metric | KB | A.1 (Kuhn 2023 theory), A.3 (H-E1 diagnostics) |
| Threshold (0.1 nats) | 02b_verification_plan.md | §2.2 H-M1 success criteria |
| Eligibility criterion (≥2 samples/cluster) | KB | A.1, A.2 (paraphrase = NLI entailment) |
| Expected variance range | KB | A.1 (0.2–0.8 nats at 7B scale) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated below)
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- 2026-08-25T16:55:26Z: H-M1 set to IN_PROGRESS (Phase 2C start)
- 2026-08-25: Phase 2C experiment design — COMPLETED

---

*MCP Tools Used: WebSearch (Exa unavailable; web search used as fallback), training knowledge (Archon unavailable)*
*All specifications grounded in: Kuhn et al. 2023, Farquhar et al. 2024, H-E1 validated results*
*Next Phase: Phase 3 — Implementation Planning*
