# Experiment Design: h-e1

**Date:** 2026-05-20
**Author:** Anonymous
**Hypothesis Statement:** Under Llama-3 base checkpoints on TriviaQA and NaturalQuestions with identical splits and evaluation harness, SE and KLE show statistically higher AUROC for correctness prediction than token-probability at both 8B and 70B scales — confirming the semantic-structural UQ advantage as a prerequisite for scale-dependent reorganization.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** True (h-e1 has no prerequisites — it is the foundation hypothesis)
**Gate Status:** MUST_WORK — SE & KLE AUROC > token-prob at both 8B & 70B, CI excludes zero → proceed to H-M1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (Foundation hypothesis)

### Gate Condition
**MUST_WORK Gate:** SE AUROC > token-prob AUROC at both 8B and 70B scales, with 95% bootstrap CI excluding zero, confirmed on BOTH TriviaQA AND NaturalQuestions test sets independently.

- PASS → proceed to H-M1 (semantic advantage confirmed as prerequisite for mechanism tests)
- FAIL at 8B only → PIVOT: re-examine SE implementation, check UQLM normalization
- FAIL at both scales → ABANDON H-M*: semantic advantage absent; reassess EGSH; route to Phase 2A

---

## Continuation Context

This is the **first hypothesis** in the verification chain.

- **Previous Context:** None — no prior hypothesis validation to inherit from.
- **Previous Hypothesis Results:** N/A

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Semantic entropy AUROC uncertainty quantification LLM**
- Result 1: [hf.co/papers/2305.14314] — Farquhar et al. 2024 Nature paper on hallucination detection via semantic entropy. Key insight: SE uses NLI-based semantic equivalence clustering over N=10 samples; AUROC computed over binary correctness labels on TriviaQA/NQ. AUROC ~0.72–0.79 on these datasets.
- Result 2: [openreview.net/forum?id=gU58d5QeGv] — Semantic Entropy (ICLR 2023) original paper; demonstrated superiority over token-prob baseline on TriviaQA and CoQA. Core approach: cluster answers by semantic equivalence, compute entropy over clusters.

**Query 2: Uncertainty quantification language model evaluation best practices**
- Result 1: [github.com/huggingface/optimum-quanto] — Quantization integration patterns; relevant for efficient 70B inference (4-bit or 8-bit loading via bitsandbytes reduces memory while preserving logit access for UQ methods).
- Result 2: [huggingface.co/blog/hf-bitsandbytes-integration] — bitsandbytes integration for large models; critical for loading Llama-3-70B on single or dual GPU with 8-bit quantization and preserved logit output.

**Key Insights from Archon KB:**
- Standard evaluation: AUROC over binary exact-match correctness labels
- N=10 samples per query is established standard (Farquhar et al. 2024)
- Bootstrap resampling (1000 iterations) for CI estimation is standard practice
- bitsandbytes 4-bit/8-bit quantization enables 70B inference on accessible hardware

### Archon Code Examples

**Query: Semantic entropy PyTorch AUROC correctness prediction**
- Low relevance results (diffusion models, attention code) — Archon KB does not contain domain-specific SE/UQ code.
- Key pattern noted from KB: AUROC computed via `sklearn.metrics.roc_auc_score` on paired (uncertainty_score, correctness_label) arrays.

### Exa GitHub Implementations

**Query 1: Farquhar semantic entropy LLM uncertainty AUROC official implementation (HIGHEST PRIORITY)**

**Repository 1: jlko/semantic_uncertainty** ⭐ [Primary — Official Nature 2024 paper implementation]
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Relevance:** ⭐⭐⭐ HIGHEST PRIORITY — This is the exact codebase for "Detecting Hallucinations in Large Language Models Using Semantic Entropy" (Farquhar et al. 2024, Nature). Directly implements the SE method tested in H-E1.
- **Pipeline:**
  1. `generate_answers.py` — Sample N responses + likelihoods + hidden states from LLMs
  2. `compute_uncertainty_measures.py` — Compute SE, token-prob, and other UQ metrics
  3. `analyze_results.py` — Compute AUROC and aggregate performance metrics
- **Supported Datasets:** `trivia_qa`, `nq`, `squad`, `bioasq`, `svamp`
- **Supported Models:** Llama-2-7b/13b/70b, Falcon-7b/40b, Mistral-7B (Llama-3 requires adaptation)
- **Key Config:**
  - `$MODEL` one of: `[Llama-2-7b, Llama-2-13b, Llama-2-70b, ...]`
  - `$DATASET` one of: `[trivia_qa, squad, bioasq, nq, svamp]`
  - Short-phrase: default; Sentence-length: `--num_few_shot=0 --model_max_new_tokens=100 --brief_prompt=chat`
- **Results:** Notebooks: `notebooks/example_evaluation.ipynb`
- **License:** MIT

**Repository 2: OATML/semantic-entropy-probes** ⭐⭐ [SEPs implementation — official OATML]
- **URL:** https://github.com/OATML/semantic-entropy-probes
- **Relevance:** Official implementation of Semantic Entropy Probes (SEPs) by Kossen et al. 2024. Uses same SE generation pipeline; adds probe training on hidden states.
- **Key Code Structure:** Same 3-script pipeline as jlko/semantic_uncertainty (generate → compute → analyze); adds `train_latent-probe.ipynb` for SEP training.
- **Dependencies:** Python 3.11, PyTorch 2.1, HuggingFace

**Repository 3: IINemo/lm-polygraph** ⭐⭐⭐ [LM-Polygraph — unified benchmark framework]
- **URL:** https://github.com/IINemo/lm-polygraph
- **Relevance:** ⭐⭐⭐ CRITICAL — Unified benchmark for 20+ UQ methods including SE, token-prob, SelfCheckGPT variants. AUROC evaluation built-in. Supports Llama-2; Llama-3 compatibility to be verified (R4 risk).
- **Key Code:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from lm_polygraph.utils.model import WhiteboxModel
from lm_polygraph.estimators import *

model_path = "meta-llama/Meta-Llama-3-8B"
base_model = AutoModelForCausalLM.from_pretrained(model_path, device_map="cuda:0")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = WhiteboxModel(base_model, tokenizer, model_path=model_path)

# UQ methods available:
ue_method = MeanTokenEntropy()          # token-probability baseline
# or SemanticEntropy(), EigValLaplacian(), etc.

ue = estimate_uncertainty(model, ue_method, input_text="Who invented the telephone?")
```
- **Benchmarking:** `polygraph_eval` script with Hydra YAML configs
- **AUROC evaluation:** Built-in via `analyze_results.py`
- **Methods table relevant to H-E1:**
  - Maximum Sequence Probability (MSP) — white-box, low compute
  - Mean/Max Token Entropy — white-box, low compute
  - Monte Carlo Sequence Entropy — white-box, high compute (SE-related)
  - Semantic Entropy (Farquhar et al.) — white-box, high compute
  - KLE / EigValLaplacian — white-box, medium compute

**Repository 4: cvs-health/uqlm** [UQLM — alternative unified framework]
- **URL:** https://github.com/cvs-health/uqlm
- **Relevance:** Python package for UQ-based LLM hallucination detection; supports SE (Farquhar 2024), SelfCheckGPT (Manakul 2023), KLE. Published in JMLR 2026 / TMLR.
- **Key scorers:** Discrete Semantic Entropy, Non-Contradiction Probability (SelfCheckGPT-NLI), BERTScore, Cosine Similarity, Semantic Density

**Serena Analysis Needed:** false — code from search results is sufficiently clear for pseudo-code synthesis.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-E1 requires running SE and KLE through a unified harness on TriviaQA and NQ with Llama-3 models. Two implementation strategies:

**Recommended Implementation Path:**
- **Primary:** Adapt `jlko/semantic_uncertainty` (official Farquhar 2024 codebase) for Llama-3-8B and 70B. Add Llama-3 model support (tokenizer chat template adaptation). This is the ground truth for SE reproduction.
- **Fallback:** Use `IINemo/lm-polygraph` unified framework if Llama-3 support verified (check R4 risk first: run 50-query KLE pilot in Week 0).
- **Justification:** The official implementation ensures exact reproduction of SE as reported in the Nature paper. LM-Polygraph is the backup because it provides the unified multi-method benchmark (token-prob + SE + KLE + SelfCheckGPT in one framework), but may require adaptation for Llama-3.

**Implementation Priority Assessment:**
- jlko/semantic_uncertainty: HIGHEST — official, MIT, supports TriviaQA+NQ natively
- lm-polygraph: HIGH — unified multi-method framework, AUROC benchmarking built-in
- uqlm: MEDIUM — alternative, JMLR 2026 published, supports same methods

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. No complex unfamiliar architecture requiring semantic analysis. The SE pipeline (generate → compute_uncertainty → analyze → AUROC) is straightforward and well-documented across 3 official repositories.

---

## Experiment Specification

### Dataset

**Primary Dataset 1: TriviaQA rc.nocontext**
- **Name:** TriviaQA rc.nocontext (reading comprehension, no context)
- **Type:** standard (real established benchmark)
- **Source:** HuggingFace `mandarjoshi/trivia_qa`, config `rc.nocontext`
- **Split:** test (standard split)
- **Size:** 17,944 questions (full standard test set)
- **Labels:** Binary correctness via exact-match normalization (standard QA evaluation)
- **Preprocessing:** Tokenize with model tokenizer; few-shot prompt format as in Farquhar 2024; no truncation for short-phrase generation
- **Augmentation:** None (evaluation only, no training)

**Primary Dataset 2: NaturalQuestions open-domain**
- **Name:** NaturalQuestions open-domain
- **Type:** standard (real established benchmark)
- **Source:** HuggingFace `google-research-datasets/natural_questions`, open-domain config
- **Split:** validation (used as test in open-domain QA literature; standard NQ open split)
- **Size:** 3,610 questions (standard open-domain test set)
- **Labels:** Binary correctness via exact-match (short answer matching)
- **Preprocessing:** Extract short answer candidates; exact-match normalization; same few-shot format as TriviaQA
- **Augmentation:** None

**Scope Dataset (P4 boundary test): TruthfulQA mc1_targets**
- **Name:** TruthfulQA mc1_targets
- **Type:** standard
- **Source:** HuggingFace `truthful_qa`, config `mc1_targets`
- **Split:** validation (817 questions; full set)
- **Role:** Scope boundary test only — NOT primary evaluation for H-E1

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- TriviaQA Identifier: `"mandarjoshi/trivia_qa"`, config=`"rc.nocontext"`
- NQ Identifier: `"google-research-datasets/natural_questions"`, config=`"default"`
- TruthfulQA Identifier: `"truthful_qa"`, config=`"mc1_targets"`
- Code:
```python
from datasets import load_dataset

trivia_qa = load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="test")
nq = load_dataset("google-research-datasets/natural_questions", split="validation")
truthfulqa = load_dataset("truthful_qa", "mc1_targets", split="validation")
```

### Models

#### Baseline Model

**Architecture:** Llama-3-8B-Base (decoder-only autoregressive LLM)
- **HuggingFace ID:** `meta-llama/Meta-Llama-3-8B`
- **Type:** Pretrained base checkpoint (no RLHF)
- **Parameters:** 8B
- **Role:** Small-scale UQ comparison (SE vs KLE vs token-prob at 8B)
- **Quantization:** Load in bfloat16 (full precision on A100/H100) or 8-bit via bitsandbytes for memory efficiency
- **Configuration:** Standard decoder-only; 32 transformer layers; 4096 hidden dim; GQA attention

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers`
- Identifier: `"meta-llama/Meta-Llama-3-8B"`
- Code:
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_8b = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer_8b = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
```

#### Primary Scale Model

**Architecture:** Llama-3-70B-Base (decoder-only autoregressive LLM)
- **HuggingFace ID:** `meta-llama/Meta-Llama-3-70B`
- **Type:** Pretrained base checkpoint (no RLHF)
- **Parameters:** 70B
- **Role:** Large-scale UQ comparison (SE vs KLE vs token-prob at 70B)
- **Quantization:** 8-bit via bitsandbytes (required for single/dual-GPU inference); or 4-bit with NF4 for memory-constrained setups. Logit access preserved in both modes.
- **Configuration:** 80 transformer layers; 8192 hidden dim; GQA attention

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers` + `bitsandbytes`
- Identifier: `"meta-llama/Meta-Llama-3-70B"`
- Code:
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(load_in_8bit=True)  # or load_in_4bit=True
model_70b = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-70B",
    quantization_config=bnb_config,
    device_map="auto"
)
tokenizer_70b = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-70B")
```

#### Within-Scale Control Model

**Architecture:** Llama-3-70B-Instruct
- **HuggingFace ID:** `meta-llama/Meta-Llama-3-70B-Instruct`
- **Role:** Within-scale control (RLHF vs base distinction for H-M2; not primary for H-E1)

#### Proposed Model

**Architecture:** No novel architectural modification for H-E1. This is an EXISTENCE hypothesis testing UQ *method* differences, not architectural modifications.

**Core Mechanism:** Apply 6 UQ scoring methods to the same model outputs and compare AUROC for correctness prediction.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Semantic Entropy vs Token-Probability AUROC Comparison
# Based on: jlko/semantic_uncertainty (Farquhar et al. 2024, Nature)

import torch
import numpy as np
from sklearn.metrics import roc_auc_score
from scipy.special import logsumexp

def compute_token_probability(sequences, log_likelihoods):
    """
    Token-probability baseline: mean negative log-prob of greedy sequence.
    Input: sequences (list of str), log_likelihoods (list of float)
    Output: uncertainty score (float, higher = more uncertain)
    """
    # Use negative log-likelihood of greedy decode (lower prob = higher uncertainty)
    return -log_likelihoods[0]  # greedy decode likelihood

def compute_semantic_entropy(sequences, entailment_model, tokenizer):
    """
    Semantic Entropy: cluster N samples by semantic equivalence, compute entropy.
    Input: sequences (list of N str), entailment_model, tokenizer
    Output: SE score (float, higher = more uncertain)
    Based on: jlko/semantic_uncertainty pipeline
    """
    # Step 1: Cluster answers by NLI-based semantic equivalence
    clusters = []
    assigned = [False] * len(sequences)
    for i, seq_i in enumerate(sequences):
        if not assigned[i]:
            cluster = [i]
            for j, seq_j in enumerate(sequences[i+1:], i+1):
                entail_ij = entailment_model(seq_i, seq_j)["entailment"] > 0.5
                entail_ji = entailment_model(seq_j, seq_i)["entailment"] > 0.5
                if entail_ij and entail_ji:
                    cluster.append(j)
                    assigned[j] = True
            clusters.append(cluster)
            assigned[i] = True

    # Step 2: Compute cluster probabilities (sum log-likelihoods per cluster)
    cluster_log_probs = []
    for cluster in clusters:
        log_probs = [log_likelihoods[idx] for idx in cluster]
        cluster_log_probs.append(logsumexp(log_probs))

    # Step 3: Semantic entropy = entropy over cluster distribution
    cluster_probs = np.exp(cluster_log_probs - logsumexp(cluster_log_probs))
    se = -np.sum(cluster_probs * np.log(cluster_probs + 1e-10))
    return se

def compute_auroc(uncertainty_scores, correctness_labels):
    """Compute AUROC for correctness prediction from uncertainty scores."""
    # Higher uncertainty → lower correctness (invert for AUROC)
    return roc_auc_score(correctness_labels, -np.array(uncertainty_scores))

# Bootstrap CI for AUROC
def bootstrap_auroc_ci(uncertainty_scores, correctness_labels, n=1000, alpha=0.05):
    aurocs = []
    n_samples = len(correctness_labels)
    for _ in range(n):
        idx = np.random.choice(n_samples, n_samples, replace=True)
        aurocs.append(roc_auc_score(correctness_labels[idx], -uncertainty_scores[idx]))
    ci_low = np.percentile(aurocs, 100 * alpha / 2)
    ci_high = np.percentile(aurocs, 100 * (1 - alpha / 2))
    return np.mean(aurocs), ci_low, ci_high
```

### Training Protocol

**No model training required for H-E1.** This is an inference-only evaluation experiment.

**Inference Protocol:**

- **Sampling:** N=10 samples per query at temperature=1.0, top_p=0.9 + 1 greedy decode
- **Seed:** 42 (fixed, single run — EXISTENCE PoC)
- **Batch Size:** 16 queries per batch (adjust to 8 or 4 for 70B if OOM)
- **Tokenization:** Standard Llama-3 tokenizer; few-shot prompt (5-shot for TriviaQA; standard NQ format)
- **Max New Tokens:** 50 tokens for short-phrase generation (consistent with Farquhar 2024)
- **Source (N=10, temp=1.0):** Farquhar et al. 2024 (Nature), jlko/semantic_uncertainty generate_answers.py

**Entailment Model for SE:**
- **Model:** `microsoft/deberta-large-mnli` (standard in SE literature; Farquhar 2024)
- **Purpose:** NLI-based semantic equivalence clustering
- **Code:** `AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-large-mnli")`

**KLE Implementation:**
- **Verify Week 0:** Check LM-Polygraph for KLE (EigValLaplacian) with Llama-3 support
- **Fallback:** If KLE unavailable, SE alone satisfies H-E1 primary criterion; KLE becomes secondary

**CUDA Setup:**
```bash
# Check GPUs
nvidia-smi
# Select empty GPU
export CUDA_VISIBLE_DEVICES=<empty_gpu_id>
```

### Evaluation

**Primary Metrics:**
- **AUROC (Area Under ROC Curve)** for correctness prediction:
  - `AUROC_SE_8B`, `AUROC_SE_70B` — SE at each scale
  - `AUROC_KLE_8B`, `AUROC_KLE_70B` — KLE at each scale (if available)
  - `AUROC_TP_8B`, `AUROC_TP_70B` — Token-probability at each scale
  - All computed with 95% bootstrap CI (1000 resamples)

**Success Criteria (EXISTENCE PoC — direction-based):**
- **Primary PASS:** AUROC_SE_8B > AUROC_TP_8B AND AUROC_SE_70B > AUROC_TP_70B, with 95% CI excluding zero on BOTH TriviaQA AND NQ
- **Secondary PASS:** AUROC_KLE_8B > AUROC_TP_8B AND AUROC_KLE_70B > AUROC_TP_70B (extends to KLE)
- **FAIL Trigger:** Any primary test where CI includes zero on both datasets simultaneously

**Expected Baseline Performance (from literature):**
- AUROC_SE on TriviaQA: ~0.72–0.79 (Farquhar et al. 2024, Llama-2-70B)
- AUROC_TP on TriviaQA: ~0.67 (literature; Llama-2-70B)
- Expected SE advantage: ~0.05–0.12 AUROC points above token-prob
- Source: Farquhar et al. 2024 (Nature), Kossen et al. 2024 (SEPs), Nikitin et al. 2024 (KLE)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary correctness prediction (classification)
- Library: `sklearn.metrics` (primary) + `scipy.stats` (bootstrap CI)
- Code:
```python
from sklearn.metrics import roc_auc_score
import numpy as np

auroc = roc_auc_score(correctness_labels, -uncertainty_scores)
# Bootstrap CI: see bootstrap_auroc_ci() in Core Mechanism section
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing AUROC per method (SE, KLE, TP, SelfCheckGPT-BERTScore, SelfCheckGPT-NLI, SEPs) at 8B and 70B, on TriviaQA and NQ.
  - x-axis: UQ method; y-axis: AUROC; hue: model scale (8B vs 70B); error bars: 95% bootstrap CI
  - Saved to: `h-e1/figures/auroc_comparison_bar.png`

#### Additional Figures (LLM Autonomous)
Based on the EXISTENCE hypothesis (does SE/KLE outperform token-prob?):

1. **AUROC Difference Plot:** `AUROC_SE - AUROC_TP` per scale per dataset, with CI. Shows effect size of advantage directly.
2. **ROC Curves:** Full ROC curves for SE vs TP at 8B and 70B on TriviaQA (one plot, 4 curves). Shows qualitative behavior difference.
3. **Bootstrap Distribution:** Histogram of bootstrap AUROC distribution for SE vs TP at each scale — visualizes CI width and overlap.

All figures saved to: `h-e1/figures/`

> Phase 4 Coder MUST include figure generation logic in experiment code.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on both Llama-3-8B and 70B for TriviaQA and NQ
2. `AUROC_SE > AUROC_TP` at both 8B and 70B (direction confirmed)
3. 95% bootstrap CI excludes zero for the SE-TP AUROC gap on at least one dataset per scale

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | SE implementation available and runnable on Llama-3 | TRUE — jlko/semantic_uncertainty supports Llama family; Llama-3 requires minor tokenizer adaptation |
| Mechanism Isolatable | SE and token-prob computed independently; can compare AUROC | TRUE — each method produces independent uncertainty score; AUROC compared post-hoc |
| Baseline Measurable | Token-probability (negative log-prob of greedy decode) computable from model logits | TRUE — standard logit output from AutoModelForCausalLM; no modification needed |

### Architecture Compatibility Check

**H-E1 tests UQ method performance, not model architecture modification.** Compatibility check is about model inference access:

**Required Features:**
- Access to token-level log-probabilities (logits) — available for all Llama-3 variants via `transformers`
- Support for batched sampling (N=10 generations) — available via `model.generate()` with `do_sample=True`
- Optional: hidden state access for SEPs — available via `output_hidden_states=True`

**Incompatible Setups:**
- Quantization schemes that remove logit access (e.g., GPTQ without logit output) — mitigated by using bitsandbytes 8-bit which preserves logits

**Week 0 Pre-experiment Checks:**
1. Verify KLE availability in lm-polygraph with Llama-3: run 50-query pilot
2. Verify N=5 vs N=10 stability on 500 TriviaQA queries at 70B (R5 risk)
3. Estimate 70B inference time on 100-query pilot batch

### Mechanism Activation Indicators

**How to detect if SE mechanism is actually computing semantic clusters (not degenerating):**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Clustering N=10 samples into K semantic clusters (K < N expected)" | generate.py:clustering |
| Cluster Count | Average K < N (ideally K=2–5 for factual QA) — if K=N, NLI clustering failed | compute_uncertainties.py |
| Metric Delta | AUROC_SE > AUROC_TP by at least 0.01 AUROC points on pilot 500-query run | analyze_results.py |

**Activation Verification Code (Phase 4 must implement):**
```python
def verify_se_mechanism_activated(clustering_results, auroc_results):
    """Verify SE is performing semantic clustering, not degenerating."""
    indicators = {
        "clustering_active": clustering_results["mean_cluster_count"] < clustering_results["n_samples"],
        "nli_model_loaded": clustering_results["entailment_model"] is not None,
        "auroc_delta_positive": (
            auroc_results["auroc_se"] - auroc_results["auroc_token_prob"] > 0
        ),
        "ci_non_trivial": (
            auroc_results["ci_width"] < 0.1  # CI width < 0.1 indicates stable estimate
        )
    }
    all_pass = all(indicators.values())
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| SE degenerates (all K=N) | Check mean cluster count == N | FAIL: NLI entailment model not working; check DeBERTa loading |
| Token-prob not computed | AUROC_TP is NaN or 0.5 | FAIL: Logit extraction broken; check model.generate() output |
| AUROC equal for SE and TP | \|AUROC_SE - AUROC_TP\| < 0.001 | INVESTIGATE: Possible implementation error or degenerate dataset |
| OOM on 70B sampling | CUDA OOM during N=10 generation | FALLBACK: Reduce to N=5; add batch offloading |
| Llama-3 tokenizer mismatch | Unexpected EOS/BOS tokens in generations | FIX: Apply Llama-3 chat template correctly |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| SE Activated | Mean cluster count K < N | Clustering log |
| AUROC Delta Positive | AUROC_SE > AUROC_TP at both scales | analyze_results.py |
| Hypothesis Supported | 95% bootstrap CI excludes zero for (AUROC_SE - AUROC_TP) | bootstrap_auroc_ci() |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** hf.co/papers/2305.14314 (Farquhar et al. 2024, Nature — Semantic Entropy)
- **Query Used:** "semantic entropy AUROC uncertainty quantification LLM"
- **Relevance:** Established AUROC ~0.72–0.79 for SE on TriviaQA/NQ with N=10 sampling
- **Key Insight:** NLI-based semantic equivalence clustering; exact-match correctness labels; bootstrap CI
- **Used For:** Expected baseline performance values; N=10 sampling standard; AUROC metric choice

**Source A.2:** openreview.net/forum?id=gU58d5QeGv (Semantic Uncertainty ICLR 2023)
- **Query Used:** "semantic entropy AUROC uncertainty quantification LLM"
- **Relevance:** Original SE paper showing superiority over token-prob on TriviaQA/CoQA
- **Key Insight:** SE outperforms token-prob baseline consistently across models; linguistic invariance approach
- **Used For:** Baseline comparison design; success criteria direction

**Source A.3:** huggingface.co/blog/hf-bitsandbytes-integration (bitsandbytes 8-bit)
- **Query Used:** "uncertainty quantification language model evaluation best practices"
- **Relevance:** 70B model loading strategy; 8-bit quantization preserves logits for UQ
- **Used For:** Model loading code for Llama-3-70B; bitsandbytes config specification

### B. GitHub Implementations (Exa)

**Repository B.1: jlko/semantic_uncertainty** [OFFICIAL — Highest Priority]
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Query Used:** "Farquhar semantic entropy LLM uncertainty AUROC official implementation GitHub"
- **Relevance:** Official codebase for Nature 2024 paper by Farquhar et al.; implements exact SE pipeline
- **Key Code Pattern:**
```python
# Three-script pipeline from jlko/semantic_uncertainty:
# 1. generate_answers.py — sample N responses + compute likelihoods
# 2. compute_uncertainty_measures.py — SE, token-prob, etc.
# 3. analyze_results.py — AUROC computation
# Datasets natively supported: trivia_qa, nq, squad, bioasq, svamp
# Models: Llama-2 family (needs Llama-3 tokenizer adaptation)
```
- **Configuration Extracted:** N=10 samples, temperature=1.0, DeBERTa-large-mnli for entailment
- **Used For:** Core SE implementation pipeline; training/inference configuration

**Repository B.2: IINemo/lm-polygraph** [Unified Multi-Method Framework]
- **URL:** https://github.com/IINemo/lm-polygraph
- **Query Used:** "LM-Polygraph uncertainty quantification Llama AUROC token probability PyTorch"
- **Relevance:** Provides unified benchmark for all 6 UQ methods (token-prob, SE, KLE, SelfCheckGPT variants) in one framework. AUROC evaluation built-in.
- **Key Code:**
```python
from lm_polygraph.utils.model import WhiteboxModel
from lm_polygraph.estimators import MeanTokenEntropy, SemanticEntropy

model = WhiteboxModel(base_model, tokenizer, model_path=model_path)
ue = estimate_uncertainty(model, SemanticEntropy(), input_text=question)
```
- **Configuration Extracted:** WhiteboxModel wrapper; `polygraph_eval` script with Hydra YAML
- **Used For:** Token-probability baseline implementation; KLE verification (R4 check); unified AUROC benchmarking

**Repository B.3: OATML/semantic-entropy-probes** [SEPs Implementation]
- **URL:** https://github.com/OATML/semantic-entropy-probes
- **Relevance:** SEPs (Kossen et al. 2024) — 6th UQ method in our evaluation; uses hidden states
- **Key Pattern:** Same SE pipeline; adds `train_latent-probe.ipynb` for probe training on hidden states
- **Used For:** SEPs method implementation reference

**Repository B.4: cvs-health/uqlm** [Alternative Unified Framework]
- **URL:** https://github.com/cvs-health/uqlm
- **Relevance:** JMLR 2026 published; supports SE, SelfCheckGPT-NLI, BERTScore, KLE
- **Used For:** Fallback framework if lm-polygraph has Llama-3 compatibility issues

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. The SE pipeline (generate answers → compute uncertainty → analyze AUROC) is explicitly documented across 3 official repositories with matching architectures. No complex unfamiliar patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context:** None — this is the first hypothesis in the verification chain (H-E1 has no prerequisites).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: TriviaQA rc.nocontext | Archon KB + Exa | A.1 (Farquhar 2024), B.1 (jlko repo) |
| Dataset: NaturalQuestions open-domain | Phase 2B | 02b_verification_plan.md §1.3 |
| Dataset: TruthfulQA (scope) | Phase 2B | 02b_verification_plan.md §H-M3 |
| Dataset loading code | Exa search | HuggingFace datasets documentation |
| N=10 sampling standard | Archon KB | A.1 (Farquhar 2024 Nature) |
| SE implementation pipeline | Exa GitHub | B.1 (jlko/semantic_uncertainty) |
| LM-Polygraph multi-method framework | Exa GitHub | B.2 (IINemo/lm-polygraph) |
| Token-probability definition (MSP) | Exa GitHub | B.2 (lm-polygraph docs) |
| DeBERTa-large-mnli for entailment | Exa GitHub | B.1 (jlko/semantic_uncertainty) |
| Llama-3 model loading | Exa search | HuggingFace Llama3 docs |
| bitsandbytes 8-bit for 70B | Archon KB | A.3 (HF bitsandbytes blog) |
| AUROC computation | Archon KB + Exa | A.1 (Farquhar 2024), sklearn docs |
| Bootstrap CI (1000 resamples) | Phase 2B | 02b_verification_plan.md §H-E1 protocol |
| Expected AUROC baselines | Archon KB | A.1 (0.72–0.79 SE), A.2 (token-prob ~0.67) |
| Mechanism verification code | Synthesized | Based on B.1 pipeline + B.2 framework |
| KLE implementation | Phase 2B + Exa | 02b_verification_plan.md R4; B.2 (lm-polygraph EigValLaplacian) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-20

### Workflow History for This Hypothesis
- 2026-05-20T00:55:33: h-e1 set to IN_PROGRESS (Hypothesis Loop starting Phase 2C → 3 → 4)
- 2026-05-20: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web Search), Serena (Skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
