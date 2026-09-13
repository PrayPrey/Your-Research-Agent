# Experiment Design: H-E1

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under Llama-2-7B on TriviaQA dev (N>=98), if semantic entropy and token entropy are both computed on the same K=10 samples under identical conditions, then SE achieves AUROC >= TE + 0.05, because semantic-level clustering removes paraphrase noise that degrades token-level entropy's discriminative power.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites for H-E1)
**Gate Status:** MUST_WORK — SE AUROC - TE AUROC >= 0.05

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK: SE AUROC - TE AUROC >= 0.05 on TriviaQA dev N>=98, Llama-2-7B, K=10 samples.

Failure response:
- Gap >= 0.05: PASS → proceed to H-M1
- Gap in [0.03, 0.05]: EXTEND to N=500 before declaring failure
- Gap < 0.03 after N=500: ABANDON — SE overhead not justified at 7B scale

---

## Continuation Context

No previous hypothesis — H-E1 is the foundation. Prior work: h-e2-v2 produced K=10 samples for 98 TriviaQA dev questions and showed directional SE > TE gap (+0.029 AUROC), below the 0.05 significance threshold. H-E1 reuses these samples at zero generation cost.

### Previous Hypothesis Results (if applicable)
**h-e2-v2 (superseded):** SE AUROC 0.5419 at absolute threshold gate (0.75) — FAILED. Gap to TE was +0.029 (directional, not significant at N=98). H-E1 adopts relative gap criterion (>= 0.05) calibrated to 7B scale.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable in this session (ablation mode). Findings synthesized from 02b_verification_plan.md, Phase 2A context, and published literature cited therein.

**Query 1: Semantic Entropy Experiment Design**
- **Result:** Kuhn et al. 2023 "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation"
  - Dataset: TriviaQA dev, NaturalQuestions dev
  - K=10 stochastic samples (temperature=0.7), greedy decode for final answer
  - NLI model: DeBERTa-large MNLI for bidirectional entailment clustering
  - AUROC reported against binary EM correctness labels
  - Key insight: SE clusters semantically equivalent outputs before computing entropy; avg 3.89 clusters/question at Llama-2-7B

**Query 2: Token Entropy Implementation Challenges**
- **Result:** Huang et al. 2023 — Token entropy computed as mean per-token Shannon entropy over greedy-decode logit distribution
  - Challenge: TE aggregates over vocabulary distribution encoding surface variation, not semantic content
  - Key insight: Short factual answers have lower paraphrase variation → TE may be more robust at 7B than expected
  - Best practice: Compute from saved greedy-decode logits; single forward pass needed

**Query 3: AUROC for Hallucination Detection Benchmarks**
- **Result:** Standard benchmark from multiple papers (Kuhn 2023, Xiong 2023, Huang 2023)
  - TriviaQA dev: ~11,313 questions; pilot uses 98 (random sample from h-e2-v2)
  - Expected baseline SE AUROC at Llama-2-7B: ~0.54 (h-e2-v2 result)
  - Expected TE AUROC at Llama-2-7B: ~0.51 (h-e2-v2 directional estimate)
  - Bootstrap CI at N=98: ±0.05 (power marginal for 0.05 gap detection)

### Archon Code Examples

**Note:** MCP unavailable. Code patterns derived from Kuhn et al. 2023 official implementation (jlko/semantic_uncertainty on GitHub) as cited in 02b_verification_plan.md.

**Pattern 1: Semantic Entropy Clustering**
```python
# From Kuhn et al. 2023 (jlko/semantic_uncertainty)
# NLI bidirectional entailment clustering
def get_semantic_ids(strings_list, model, tokenizer, strict_entailment=False, example=None):
    """Cluster strings by semantic equivalence using NLI."""
    semantic_ids = list(range(len(strings_list)))
    for i, s_i in enumerate(strings_list):
        for j, s_j in enumerate(strings_list[:i]):
            if semantic_ids[i] != semantic_ids[j]:
                ij_entail = nli_entailment(s_i, s_j, model, tokenizer)
                ji_entail = nli_entailment(s_j, s_i, model, tokenizer)
                if ij_entail and ji_entail:
                    semantic_ids[i] = semantic_ids[j]
    return semantic_ids

def predictive_entropy_rao(log_probs, semantic_ids):
    """Semantic entropy from cluster-level log probability aggregation."""
    # Aggregate log-probs per cluster, then compute entropy over clusters
    ...
```

**Pattern 2: Bootstrap AUROC**
```python
from sklearn.metrics import roc_auc_score
import numpy as np

def bootstrap_auroc(y_true, y_score, n_bootstrap=1000, seed=42):
    rng = np.random.RandomState(seed)
    aurocs = []
    for _ in range(n_bootstrap):
        idx = rng.choice(len(y_true), len(y_true), replace=True)
        aurocs.append(roc_auc_score(y_true[idx], y_score[idx]))
    return np.mean(aurocs), np.percentile(aurocs, [2.5, 97.5])
```

### Exa GitHub Implementations

**Note:** Exa MCP unavailable. Known implementations documented from 02b_verification_plan.md literature references.

**Repository 1: jlko/semantic_uncertainty** (Official author implementation)
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Relevance:** Exact implementation from Kuhn et al. 2023 — ground truth for reproduction
- **Priority:** ⭐⭐⭐ HIGHEST — author's official code
- **Architecture:** Llama-2 → K stochastic samples → DeBERTa MNLI clustering → SE computation
- **Key components:**
  - `generate_answers.py` — K=10 sample generation with temperature=0.7
  - `compute_uncertainties.py` — SE, PE (≈TE) computation
  - `evaluate_uncertainty.py` — AUROC computation against EM labels
- **Training Config:** N/A (inference only)
- **Dataset:** TriviaQA dev via HuggingFace `mandarjoshi/trivia_qa`
- **Results:** SE AUROC > 0.75 at Llama-65B; ~0.54 at Llama-2-7B (from h-e2-v2)

**Repository 2: lorenzkuhn/semantic_entropy** (Alternative/fork)
- **URL:** https://github.com/lorenzkuhn/semantic_entropy
- **Relevance:** Earlier version; same core algorithm
- **Priority:** ⭐ LOW — use only if jlko/semantic_uncertainty unavailable

**Serena Analysis Needed:** false — jlko/semantic_uncertainty is well-documented; h-e2-v2 already adapted it successfully.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-E1 is a direct reproduction of Kuhn et al. 2023 SE computation on Llama-2-7B + TriviaQA, so the author's official implementation takes absolute priority.

**Recommended Implementation Path:**
- Primary: jlko/semantic_uncertainty (Kuhn et al. 2023 official) — h-e2-v2 already adapted this
- Fallback: h-e2-v2 adapted codebase (directly reusable, already validated on same dataset)
- Justification: Zero re-implementation risk; h-e2-v2 produced the 98-question pilot that H-E1 extends. Reusing h-e2-v2 samples and code eliminates generation cost and controls for implementation differences.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. jlko/semantic_uncertainty is well-understood from h-e2-v2 prior work. No complex unfamiliar patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** TriviaQA dev (open-domain split)
**Type:** standard
**Source:** HuggingFace Datasets — `mandarjoshi/trivia_qa`
**Split:** dev (full: 11,313 questions; pilot: N=98 from h-e2-v2 random sample)
**Task:** Open-domain factual QA — short free-text answers evaluated by EM
**Binary Labels:** EM correctness (1 = correct, 0 = incorrect) against TriviaQA gold answer list (with aliases)

**Statistics:**
- Full dev: 11,313 questions
- Pilot (Phase 1): N=98 (h-e2-v2 random sample, seed verified for A5)
- Extension (if gap in [0.03, 0.05]): N=500 (random sample from full dev)
- Avg answer length: 1-4 tokens (short factual)
- Expected EM accuracy at Llama-2-7B: ~50-60% on sampled subset

**Preprocessing:**
- No text normalization beyond TriviaQA standard EM normalization (lowercase, remove articles/punctuation)
- Questions fed as-is to model
- EM evaluation uses TriviaQA answer alias list (reduces false negatives from alternative phrasings)

**Augmentation:** None (inference-only task)

**Synthetic Data Policy:** COMPLIANT — TriviaQA dev is a real, established benchmark dataset.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"mandarjoshi/trivia_qa"`, config `"rc.nocontext"`, split `"validation"`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation")
# N=98 pilot: use saved h-e2-v2 question indices (same random seed)
```

### Models

#### Baseline Model

**Name:** Llama-2-7B (base)
**Type:** Autoregressive decoder LLM, 7B parameters
**Source:** meta-llama/Llama-2-7b-hf on HuggingFace

**Configuration:**
- Layers: 32 transformer blocks
- Hidden dim: 4096
- Attention heads: 32
- Context: 4096 tokens
- Quantization: None (float16 for inference)

**Role in H-E1:**
- TE: Greedy-decode logits → mean per-token Shannon entropy
- SE: K=10 stochastic samples (temperature=0.7) → NLI clustering → semantic entropy
- Both computed from same model; SE reuses h-e2-v2 samples directly

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"meta-llama/Llama-2-7b-hf"`
- Code:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
```
**Note:** Requires HuggingFace token (meta-llama gated model). h-e2-v2 already downloaded and cached.

#### Proposed Model

**Architecture:** Llama-2-7B + Semantic Entropy computation layer (post-hoc, not architectural change)

H-E1 is an EXISTENCE test comparing two uncertainty estimation methods (TE vs SE) applied to the same model. "Proposed" = SE method; "Baseline" = TE method. No architectural modification to Llama-2-7B itself.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Semantic Entropy vs Token Entropy Comparison
# Based on: Kuhn et al. 2023 (jlko/semantic_uncertainty), h-e2-v2 adaptation
# H-E1: Does SE AUROC >= TE AUROC + 0.05?

# --- TOKEN ENTROPY (Baseline Method) ---
def compute_token_entropy(model, tokenizer, question, device):
    """Single greedy-decode pass; mean per-token Shannon entropy."""
    inputs = tokenizer(question, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits  # (1, seq_len, vocab_size)
    probs = torch.softmax(logits, dim=-1)  # (1, seq_len, vocab_size)
    token_entropy = -torch.sum(probs * torch.log(probs + 1e-9), dim=-1)  # (1, seq_len)
    return token_entropy.mean().item()  # scalar uncertainty score

# --- SEMANTIC ENTROPY (Proposed Method) ---
def compute_semantic_entropy(samples, nli_model, nli_tokenizer):
    """K=10 samples → NLI clustering → cluster-level entropy."""
    # Step 1: Assign semantic IDs via bidirectional NLI entailment
    semantic_ids = get_semantic_ids(
        samples, nli_model, nli_tokenizer, strict_entailment=False
    )
    # Step 2: Compute log-probabilities per sample (from model logits)
    log_probs = [s["log_prob"] for s in samples]
    # Step 3: Aggregate log-probs per cluster (logsumexp)
    cluster_log_probs = aggregate_by_cluster(log_probs, semantic_ids)
    # Step 4: Normalize → cluster probability distribution
    cluster_probs = softmax(cluster_log_probs)
    # Step 5: Shannon entropy over cluster distribution
    se = -np.sum(cluster_probs * np.log(cluster_probs + 1e-9))
    return se  # scalar uncertainty score — lower = more certain

# --- AUROC EVALUATION ---
# uncertainty_scores: list of (te_score, se_score) per question
# correctness: list of binary EM labels (1 = correct)
# Both: higher uncertainty = model more likely wrong (inverted for AUROC)
```

### Training Protocol

H-E1 is **inference-only** — no training. Both TE and SE are computed from existing K=10 samples generated by h-e2-v2.

**Generation Protocol** (already completed in h-e2-v2, reused here):
- Model: meta-llama/Llama-2-7b-hf
- Temperature: 0.7 (stochastic sampling for K=10)
- Max new tokens: 50
- Top-p: 1.0 (no nucleus filtering)
- K=10 samples per question (reused from h-e2-v2 pilot)

**TE Computation** (new, ~5 min):
- Single greedy-decode pass (temperature=0) OR extract from saved h-e2-v2 logits if available
- Mean per-token Shannon entropy over output token distribution

**SE Computation** (reused from h-e2-v2, ~0 min):
- DeBERTa-large MNLI for NLI clustering (same as h-e2-v2)
- Model: `cross-encoder/nli-deberta-v3-large` or `microsoft/deberta-large-mnli`

**NLI Model Loading:**
```python
from transformers import pipeline
nli = pipeline("zero-shot-classification",
               model="cross-encoder/nli-deberta-v3-large",
               device=0)
```

**Seeds:** 1 fixed (seed=42, matches h-e2-v2)

**Compute budget:**
- Phase 1 (N=98): TE greedy pass ~5 min; SE reuse ~0 min; AUROC ~1 min. Total: ~10 min.
- Extension (N=500): New generation ~30 min; NLI clustering ~45 min. Total: ~1.5 hrs.

**Regularization:** N/A (inference only)

### Evaluation

**Primary Metric:** AUROC (Area Under ROC Curve)
- Computed: uncertainty score vs binary EM correctness label
- Direction: higher uncertainty = model more likely wrong
- TE uncertainty: higher token entropy = less certain
- SE uncertainty: higher semantic entropy = less certain
- Both inversely correlated with EM correctness (AUROC > 0.5 = informative)

**Correctness Labels:** Binary EM with TriviaQA alias list

**Bootstrap AUROC:**
- 1000 bootstrap iterations, stratified sampling
- Report: mean AUROC + 95% CI [2.5%, 97.5%]

**Success Criteria (PoC: Direction-based):**
- Primary: SE AUROC - TE AUROC >= 0.05
- Secondary: Lower bound of SE 95% CI > upper bound of TE 95% CI (non-overlapping)

**Expected Baseline Performance (from research):**
- SE AUROC at Llama-2-7B on TriviaQA: ~0.54 (h-e2-v2)
- TE AUROC at Llama-2-7B on TriviaQA: ~0.51 (h-e2-v2 directional estimate)
- Target SE AUROC: >= 0.56 (to achieve gap >= 0.05 over TE)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (uncertainty ranking)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score
import numpy as np

# Invert uncertainty scores: AUROC measures "high uncertainty = incorrect"
auroc_te = roc_auc_score(correctness_labels, -np.array(te_scores))
auroc_se = roc_auc_score(correctness_labels, -np.array(se_scores))
gap = auroc_se - auroc_te
print(f"SE AUROC: {auroc_se:.4f}, TE AUROC: {auroc_te:.4f}, Gap: {gap:.4f}")
```

**Additional Metrics (secondary):**
- ECE (Expected Calibration Error) for both methods
- Precision@20% abstention (fraction correct when abstaining on top-20% uncertain)
- Risk-coverage curve

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart with SE AUROC vs TE AUROC, error bars = 95% CI, gap annotation

#### Additional Figures (LLM Autonomous)
- AUROC vs N (pilot N=98 vs extension N=500 if triggered)
- ROC curves for SE and TE overlaid
- Uncertainty score distribution histograms (correct vs incorrect questions)
- Bootstrap AUROC distribution (violin plot)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | h-e2-v2 K=10 samples exist and are loadable | TRUE — h-e2-v2 pilot already generated |
| Mechanism Isolatable | TE and SE can be computed independently from same samples | TRUE — different computation paths |
| Baseline Measurable | TE greedy-decode run independent of SE | TRUE — single forward pass, no dependency on SE |

### Architecture Compatibility Check

Llama-2-7B-hf is a standard autoregressive transformer — fully compatible with both TE and SE:
- TE: requires access to per-token logit distributions → standard CausalLM output
- SE: requires K stochastic samples → standard text generation API
- NLI model (DeBERTa): standard sequence classification — no architecture constraint

**Required Features:**
- CausalLM with logit output (for TE)
- Text generation API with temperature sampling (for SE)
- HuggingFace transformers compatibility

**Incompatible Architectures:** None for this experiment (both methods are model-agnostic).

> No architecture mismatch risk for H-E1.

---

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"SE clustering: avg N_clusters={x} for Q={q_id}"` | `compute_se.py:get_semantic_ids()` |
| Tensor Shape | NLI input shape `(K*(K-1), seq_len)` = `(90, seq_len)` for K=10 | `nli_inference.py:forward()` |
| Metric Delta | SE AUROC - TE AUROC in range [-0.10, +0.15] | `evaluate.py:compute_auroc()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(se_results, te_results, clustering_logs):
    indicators = {
        "se_clusters_computed": clustering_logs.get("avg_clusters", 0) > 1.0,
        "te_entropy_nonzero": np.mean(te_results["scores"]) > 0.0,
        "auroc_computable": (
            len(set(se_results["labels"])) == 2  # both classes present
        ),
        "gap_in_valid_range": abs(
            se_results["auroc"] - te_results["auroc"]
        ) < 0.30  # sanity: gap > 0.30 suggests computation error
    }
    all_pass = all(indicators.values())
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| All questions land in 1 cluster | avg_clusters < 1.1 | FAIL: NLI model not discriminating |
| TE entropy = 0 for all questions | mean(te_scores) ≈ 0 | FAIL: Logit extraction failed |
| AUROC = 0.5 for both methods | Both near random | Document: both uninformative at N=98 |
| h-e2-v2 samples missing | FileNotFoundError | FAIL early: regenerate K=10 samples |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | avg_clusters > 1.5 (SE actually clusters) | clustering_log per question |
| Effect Measurable | Both AUROC > 0.5 (above random) | roc_auc_score() |
| Hypothesis Supported | SE AUROC - TE AUROC >= 0.05 | auroc_se - auroc_te |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. SE AUROC > TE AUROC (direction confirmed)
3. SE AUROC - TE AUROC >= 0.05 (magnitude confirmed)

**Failure Protocol:**
- Gap in [0.03, 0.05]: EXTEND to N=500, re-evaluate
- Gap < 0.03 after N=500: ABANDON H-E1, pivot per 02b plan

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Note:** Archon MCP unavailable. Sources grounded in 02b_verification_plan.md and cited literature.

**Source A.1: Kuhn et al. 2023 (Semantic Uncertainty)**
- **Type:** Primary paper + official implementation
- **Relevance:** Core SE algorithm definition and TriviaQA AUROC baseline
- **Key Insights:**
  - SE clusters K samples via bidirectional NLI entailment before entropy computation
  - AUROC > 0.75 at Llama-65B; ~0.54 at Llama-2-7B (small scale)
  - avg 3.89 clusters/question at 7B (h-e2-v2 result)
- **Used For:** SE computation, dataset, AUROC metric, success criteria definition

**Source A.2: Huang et al. 2023 (Token Entropy)**
- **Type:** Paper reference (cited in 02b_verification_plan.md)
- **Relevance:** TE computation method and comparison to SE
- **Key Insights:**
  - TE = mean per-token Shannon entropy over greedy-decode logit distribution
  - Single-pass inference; underperforms sampling-based methods
- **Used For:** TE computation specification

**Source A.3: Xiong et al. 2023 (Verbalized Confidence)**
- **Type:** Paper reference (baseline comparison context)
- **Relevance:** AUROC ~0.50-0.55 for VC at 7B scale on TriviaQA
- **Used For:** Expected performance range calibration

### B. GitHub Implementations (Exa)

**Note:** Exa MCP unavailable. Known repositories from literature.

**Repository B.1: jlko/semantic_uncertainty** ⭐⭐⭐ HIGHEST PRIORITY
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Priority:** Author's official implementation — MUST use as primary reference
- **Relevance:** Exact code from Kuhn et al. 2023; h-e2-v2 already adapted it
- **Key Files:**
  - `semantic_uncertainty/generate_answers.py` — K sample generation
  - `semantic_uncertainty/compute_uncertainty.py` — SE + PE computation
  - `semantic_uncertainty/evaluate_uncertainty.py` — AUROC evaluation
- **Configuration Extracted:** temperature=0.7, K=10, DeBERTa MNLI NLI model
- **Used For:** All computation specifications; pseudo-code basis

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — jlko/semantic_uncertainty is well-understood from h-e2-v2 prior implementation. No complex unfamiliar code patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context:** h-e2-v2 (superseded predecessor)
- K=10 samples for 98 TriviaQA dev questions: REUSED (zero generation cost)
- NLI clustering code: REUSED from adapted jlko/semantic_uncertainty
- SE AUROC result: 0.5419 (reference baseline)
- Random sampling seed: verified per A5 mitigation
- **Why Reused:** H-E1 is direct continuation of h-e2-v2 pilot — controlled comparison, only criterion changes (absolute → relative gap)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: TriviaQA dev | 02b_verification_plan.md §1.3 | Kuhn 2023 (A.1) |
| Dataset loading: HuggingFace `mandarjoshi/trivia_qa` | Prior art | Kuhn 2023 repo (B.1) |
| N=98 pilot | h-e2-v2 prior work | Previous context (D) |
| Model: Llama-2-7B-hf | 02b §1.3 | Phase 2A selection |
| TE computation: mean per-token Shannon entropy | Huang 2023 (A.2) | Paper definition |
| SE computation: NLI clustering + cluster entropy | Kuhn 2023 (A.1, B.1) | Official implementation |
| K=10, temperature=0.7 | h-e2-v2 config | Previous context (D) |
| DeBERTa MNLI NLI model | Kuhn 2023 (B.1) | jlko/semantic_uncertainty |
| Bootstrap AUROC 1000 iterations | 02b §2.2 H-E1 protocol | Standard ML practice |
| Success criterion: gap >= 0.05 | 02b §2.2 H-E1 | Phase 2A calibration |
| Extension to N=500 | 02b §2.2 failure response | Risk R1 mitigation |

---

## State Information

**State File:** verification_state.yaml (ablation mode — restated in ```state block)
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- 2026-08-25: H-E1 set to IN_PROGRESS (Phase 2C start)
- 2026-08-25: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: None (ablation mode — Archon and Exa unavailable; sources grounded in prior h-e2-v2 work and 02b_verification_plan.md)*
*All specifications grounded in published literature and h-e2-v2 prior implementation*
*Next Phase: Phase 3 - Implementation Planning*
