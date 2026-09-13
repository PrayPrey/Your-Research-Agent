# Experiment Design: h-e1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis Statement:** Under decoder-only LLMs, if we compute UQ scores for LLM outputs, then at least one method achieves AUROC > 0.55 on hallucination detection, because uncertainty signals correlate with output quality.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK - If AUROC < 0.55 for all methods, STOP pipeline

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
- **Type:** MUST_WORK
- **Pass:** At least one UQ method achieves AUROC > 0.55
- **Fail:** STOP - UQ methods do not discriminate hallucinations

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous context to inherit.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable in this session. Using web search fallback.*

### Archon Code Examples

*Archon MCP unavailable in this session.*

### Exa GitHub Implementations

**[VERIFIED - WebSearch]** Key implementations found:

**1. lorenzkuhn/semantic_uncertainty** (Official - Kuhn et al. 2023)
- **URL:** https://github.com/lorenzkuhn/semantic_uncertainty
- **Relevance:** Official implementation of semantic entropy from ICLR 2023
- **Methods:** Semantic Entropy, Predictive Entropy, Lexical Similarity, P(True)
- **Datasets:** TriviaQA, CoQA (not TruthfulQA directly)
- **Pipeline:** generate.py → clean_generations.py → get_semantic_similarities.py → compute_likelihoods.py → compute_confidence_measure.py → analyze_result.py
- **Deps:** PyTorch, HuggingFace, wandb

**2. potsawee/selfcheckgpt** (Official - Manakul et al. 2023)
- **URL:** https://github.com/potsawee/selfcheckgpt
- **Relevance:** Official SelfCheckGPT for black-box hallucination detection
- **Methods:** BERTScore, MQAG, Ngram, NLI (DeBERTa), LLMPrompt
- **Install:** `pip install selfcheckgpt`
- **Usage:** `SelfCheckNLI.predict(sentences, sampled_passages)`

**3. cvs-health/uqlm** (Production Package)
- **URL:** https://github.com/cvs-health/uqlm
- **Relevance:** Unified UQ package with multiple methods
- **Methods:** Semantic Entropy, Semantic Density, Token Probability, NLI-based
- **Install:** `pip install uqlm`
- **Framework:** LangChain integration

**4. OATML/semantic-entropy-probes** (Efficient Variant)
- **URL:** https://github.com/OATML/semantic-entropy-probes
- **Relevance:** Fast approximation of semantic entropy from hidden states

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Rationale |
|----------|---------------|-----------|
| 1 (HIGHEST) | lorenzkuhn/semantic_uncertainty | Official Kuhn 2023 - ground truth for semantic entropy |
| 2 | potsawee/selfcheckgpt | Official SelfCheckGPT - author implementation |
| 3 | cvs-health/uqlm | Production package, multiple methods, easy integration |

**Recommended Implementation Path:**
- Primary: cvs-health/uqlm (unified API, all 4 UQ methods in one package)
- Fallback: Combine lorenzkuhn/semantic_uncertainty + potsawee/selfcheckgpt
- Justification: UQLM provides consistent API for comparing methods; fallback gives author-verified implementations

### Code Analysis (Serena MCP)

*Serena MCP unavailable. Code patterns extracted from web search:*

**Semantic Entropy Pipeline (from lorenzkuhn):**
1. Generate N samples per query (typically 5-10)
2. Cluster samples by semantic similarity (NLI-based)
3. Compute entropy over cluster distribution
4. Lower entropy = higher confidence = less likely hallucination

**SelfCheckGPT Pipeline (from potsawee):**
1. Generate main response + K sample responses
2. Compare main response sentences against samples
3. Score consistency (0-1, higher = less factual)
4. Inconsistent sentences flagged as hallucinations

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA (mc1 split)
**Type:** standard
**Source:** HuggingFace datasets

**Statistics:**
- Total questions: 817
- Split: mc1 (single correct answer per question)
- Categories: 38 categories covering health, law, finance, etc.
- Labels: Binary (correct/incorrect answer selection)

**Preprocessing:**
- Load via HuggingFace: `load_dataset("truthful_qa", "multiple_choice")`
- Filter to mc1 format
- Extract question + answer choices
- Ground truth: correct answer index

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa` (config: `multiple_choice`)
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "multiple_choice")
# mc1 has single correct answer per question
```

### Models

#### Baseline Model

**Name:** Llama-3-8B-Instruct
**Type:** decoder-only transformer
**Source:** meta-llama/Meta-Llama-3-8B-Instruct
**Parameters:** ~8B

**Configuration:**
- Context length: 8192 tokens
- Vocabulary: 128K tokens
- Quantization: None (full precision) or bfloat16

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Meta-Llama-3-8B-Instruct`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
```

#### Proposed Model

**Architecture:** Baseline + UQ Method Wrappers

No model modification required. UQ methods wrap the baseline model to compute uncertainty scores:

1. **Token Entropy:** Compute entropy from output logits
2. **Semantic Entropy:** Cluster multiple samples, compute cluster entropy
3. **P(True):** Prompt model "Is the above answer correct?"
4. **SelfCheckGPT:** Compare response consistency across samples

**Core Mechanism Implementation:**

```python
# Core Mechanism: UQ Methods for Hallucination Detection
# Based on: lorenzkuhn/semantic_uncertainty, potsawee/selfcheckgpt

import torch
import numpy as np
from scipy.stats import entropy

class UQMethodsWrapper:
    """
    Wraps LLM to compute uncertainty scores for hallucination detection.
    """
    def __init__(self, model, tokenizer, num_samples=10):
        self.model = model
        self.tokenizer = tokenizer
        self.num_samples = num_samples

    def token_entropy(self, input_ids):
        """Compute entropy from output logits."""
        with torch.no_grad():
            outputs = self.model(input_ids, return_dict=True)
            logits = outputs.logits[:, -1, :]  # (B, vocab)
            probs = torch.softmax(logits, dim=-1)
            ent = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
        return ent.mean().item()

    def semantic_entropy(self, prompt, temperature=0.7):
        """Generate samples, cluster semantically, compute entropy."""
        samples = self._generate_samples(prompt, temperature)
        clusters = self._cluster_by_nli(samples)
        cluster_probs = np.bincount(clusters) / len(clusters)
        return entropy(cluster_probs)

    def selfcheck_nli(self, response, sampled_responses):
        """Score consistency via NLI."""
        # Uses SelfCheckNLI from selfcheckgpt package
        from selfcheckgpt.modeling_selfcheck import SelfCheckNLI
        checker = SelfCheckNLI(device="cuda")
        scores = checker.predict(
            sentences=[response],
            sampled_passages=sampled_responses
        )
        return scores[0]  # Higher = more inconsistent = hallucination

# Integration: Apply to each TruthfulQA question
# Score polarity: Higher uncertainty = more likely hallucination
```

### Training Protocol

**⚠️ EXISTENCE (PoC): No training required.**

This experiment evaluates pre-trained LLM + UQ methods. No fine-tuning.

**Inference Protocol:**
- **Samples per query:** 10 (for multi-sample methods)
- **Temperature:** 0.7 (for sample diversity)
- **Max tokens:** 256
- **Seed:** 42 (fixed)
- **GPU:** 1x A100 40GB (or 2x RTX 3090)

**Compute Budget:**
- ~817 questions × 10 samples × 4 methods
- Estimated runtime: 2-4 hours on single GPU

### Evaluation

**Primary Metrics:**
- **AUROC:** Area Under ROC Curve for hallucination detection
  - X-axis: False Positive Rate
  - Y-axis: True Positive Rate
  - Threshold: Method passes if AUROC > 0.55

**Secondary Metrics:**
- AUPRC: Area Under Precision-Recall Curve
- Score distributions: Visualize separation between correct/incorrect

**Success Criteria:**
- **PoC Pass:** At least ONE method achieves AUROC > 0.55
- **Direction:** Higher uncertainty score = higher hallucination probability

**Expected Baseline Performance** (from research):
- Token Entropy: AUROC ~0.60-0.65 (Kuhn 2023)
- Semantic Entropy: AUROC ~0.70-0.75 (Kuhn 2023, different dataset)
- Random: AUROC = 0.50

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (correct vs hallucinated)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc

auroc = roc_auc_score(y_true, uncertainty_scores)
precision, recall, _ = precision_recall_curve(y_true, uncertainty_scores)
auprc = auc(recall, precision)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing AUROC for each UQ method with 0.55 threshold line

#### Additional Figures (LLM Autonomous)

1. **ROC Curves**: Overlay ROC curves for all 4 methods
2. **Score Distributions**: Histogram/KDE of uncertainty scores for correct vs hallucinated answers
3. **Per-Category Heatmap**: AUROC by TruthfulQA category (if time permits)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- [x] `mechanism_exists`: UQ methods have published implementations
- [x] `mechanism_isolatable`: Each method computes independent score
- [x] `baseline_measurable`: Random baseline = AUROC 0.5

### Architecture Compatibility
- Model: Llama-3-8B-Instruct supports logit extraction (token entropy)
- Model: Supports temperature sampling (semantic entropy, selfcheck)
- NLI model: DeBERTa-v3-large available for semantic clustering

### Activation Indicators
- `mechanism_log_message`: "Computing {method_name} uncertainty score..."
- `tensor_shape_change`: Logits shape (B, seq_len, vocab_size) for entropy
- `metric_delta_expected`: AUROC > 0.50 (better than random)

### Mechanism Verification Code
```python
def verify_mechanism_active(scores_correct, scores_hallucinated):
    """Verify UQ mechanism produces discriminative scores."""
    # Check 1: Scores are not all identical
    assert np.std(scores_correct) > 0, "No variance in correct scores"
    assert np.std(scores_hallucinated) > 0, "No variance in hallucinated scores"
    
    # Check 2: Distribution separation exists
    mean_diff = np.mean(scores_hallucinated) - np.mean(scores_correct)
    print(f"Mean score difference: {mean_diff:.4f}")
    
    # Check 3: AUROC > random
    auroc = roc_auc_score(
        [0]*len(scores_correct) + [1]*len(scores_hallucinated),
        list(scores_correct) + list(scores_hallucinated)
    )
    assert auroc > 0.50, f"AUROC {auroc:.3f} not better than random"
    return True
```

### Hypothesis Support
- `hypothesis_support_threshold`: AUROC > 0.55
- `hypothesis_support_metric`: max(AUROC across 4 methods)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. At least one method: `AUROC > 0.55`

**If ALL methods fail (AUROC ≤ 0.55 for all):**
- Gate: MUST_WORK → Pipeline STOPS
- Conclusion: UQ methods do not discriminate hallucinations on TruthfulQA

---

## Appendix: Reference Implementations

| Repository | Methods | Stars | License |
|------------|---------|-------|---------|
| [lorenzkuhn/semantic_uncertainty](https://github.com/lorenzkuhn/semantic_uncertainty) | Semantic Entropy, P(True) | - | MIT |
| [potsawee/selfcheckgpt](https://github.com/potsawee/selfcheckgpt) | SelfCheckGPT (5 variants) | - | MIT |
| [cvs-health/uqlm](https://github.com/cvs-health/uqlm) | All methods unified | - | Apache 2.0 |
| [OATML/semantic-entropy-probes](https://github.com/OATML/semantic-entropy-probes) | Fast semantic entropy | - | MIT |

**Key Papers:**
- Kuhn et al. (2023) "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in NLG" - ICLR 2023
- Manakul et al. (2023) "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection" - EMNLP 2023
- Lin et al. (2022) "TruthfulQA: Measuring How Models Mimic Human Falsehoods" - ACL 2022

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-29

### Workflow History for This Hypothesis
- 2026-08-29: Phase 2C experiment design started
- 2026-08-29: Implementation research completed (web search fallback)
- 2026-08-29: Experiment specification synthesized

---

*MCP Tools Used: WebSearch (fallback for Archon/Exa)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
