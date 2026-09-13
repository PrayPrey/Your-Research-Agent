# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** PrayPrey
**Hypothesis Statement:** Under QA task conditions, if we measure token entropy from softmax logit distributions, then entropy values correlate with model uncertainty and question correctness.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing entropy-correctness correlation.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (PASS)
**Gate Status:** MUST_WORK (if fails, STOP - entropy signal not predictive)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
MUST_WORK: If entropy does not correlate with correctness, the core thesis (complementary signals) loses one pillar. Cannot proceed to combination hypotheses.

---

## Continuation Context

### Previous Hypothesis Results (H-E1)
- **Status:** COMPLETED (PASS)
- **Entropy Mean:** 0.1224 (std: 0.0395)
- **Consistency Mean:** 0.8693 (std: 0.0748)
- **Success Rate:** 100%
- **Variance Confirmed:** Both metrics show meaningful variance

**Key Insight from H-E1:** Entropy and consistency are computable for all questions. Entropy range [0.03, 0.18] suggests model has varying confidence levels. Ready to test correlation with correctness.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using established literature and Phase 2B context*

**Relevant Patterns:**
1. **Shannon Entropy for Uncertainty:** Token entropy = -Σ p(t) log p(t) over vocabulary. H-E1 validated implementation.
2. **Correctness Labeling:** Compare generated answer to ground truth using exact match or F1.
3. **Statistical Testing:** t-test for group comparison (correct vs incorrect), AUROC for predictive power.

### Archon Code Examples

*MCP unavailable - referencing H-E1 validated code*

From H-E1 validation:
- `entropy_module.py`: Shannon entropy over softmax logits
- `response_generator.py`: Multi-sample generation with logit access
- Embedding model: sentence-transformers/all-MiniLM-L6-v2

### Exa GitHub Implementations

*MCP unavailable - using established references*

**Key References:**
1. **Semantic Entropy (Kuhn et al., 2023):** github.com/jlko/semantic_uncertainty - Entropy clustering baseline
2. **HuggingFace Transformers:** Standard logit extraction via `output.logits`
3. **SciPy/Statsmodels:** t-test, AUROC computation

### 🎯 Implementation Priority Assessment

**CRITICAL: Build on H-E1 validated code**

**Recommended Implementation Path:**
- Primary: Extend H-E1 code with correctness evaluation
- Fallback: N/A (H-E1 code is validated)
- Justification: Reuse validated entropy computation, add correctness labels and statistical tests

### Code Analysis (Serena MCP)

*MCP unavailable - using H-E1 architecture*

From H-E1:
- Entropy computation: `compute_entropy(logits)` in entropy_module.py
- Response generation: `generate_responses(question, n_samples)` in response_generator.py
- Main pipeline: `run_experiment()` orchestrates generation + metric computation

---

## Experiment Specification

### Dataset

**Name:** TriviaQA (rc.nocontext)
**Source:** HuggingFace Datasets (mandarjoshi/trivia_qa)
**Type:** standard

**Splits:**
| Split | Size | Purpose |
|-------|------|---------|
| Validation | ~11,313 | Full evaluation (statistically meaningful) |
| Test | ~10,832 | Cross-validation if needed |

**Preprocessing:**
1. Load questions and ground-truth answers (answer.aliases list)
2. Filter: Skip questions with empty answers
3. Normalize: Lowercase, strip whitespace

**Why This Dataset:**
- Factual QA with verifiable answers
- Large scale for statistical power
- Ground truth enables correctness labeling
- Same dataset as H-E1 (continuity)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: mandarjoshi/trivia_qa, subset: rc.nocontext
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("trivia_qa", "rc.nocontext", split="validation")
```

### Models

#### Baseline Model

**Name:** Llama-2-7B-chat
**Source:** HuggingFace (meta-llama/Llama-2-7b-chat-hf)
**Why:** Open-source with logit access, validated in H-E1, representative of deployed instruction-tuned LLMs

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: meta-llama/Llama-2-7b-chat-hf
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    device_map="auto",
    torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
```

#### Proposed Model

**Architecture:** Baseline + Entropy-based uncertainty estimation

**Core Mechanism Implementation:**

```python
def compute_token_entropy(logits: torch.Tensor) -> float:
    """
    Compute mean token entropy from logit distributions.
    
    Args:
        logits: Shape (seq_len, vocab_size)
    Returns:
        Mean entropy across generated tokens (scalar)
    """
    probs = torch.softmax(logits, dim=-1)
    log_probs = torch.log(probs + 1e-10)
    token_entropies = -torch.sum(probs * log_probs, dim=-1)
    return token_entropies.mean().item()


def evaluate_correctness(generated: str, ground_truth: list[str]) -> bool:
    """
    Check if generated answer matches any ground truth alias.
    Uses normalized exact match.
    """
    gen_normalized = generated.lower().strip()
    for alias in ground_truth:
        if alias.lower().strip() in gen_normalized:
            return True
    return False


def compute_correlation(entropies: list, correctness: list) -> dict:
    """
    Compute entropy-correctness correlation statistics.
    
    Returns:
        dict with t_stat, p_value, auroc, mean_correct, mean_incorrect
    """
    correct_entropies = [e for e, c in zip(entropies, correctness) if c]
    incorrect_entropies = [e for e, c in zip(entropies, correctness) if not c]
    
    # t-test: incorrect should have higher entropy
    t_stat, p_value = scipy.stats.ttest_ind(
        incorrect_entropies, correct_entropies
    )
    
    # AUROC: can entropy predict correctness?
    auroc = sklearn.metrics.roc_auc_score(
        correctness, 
        [-e for e in entropies]  # Invert: low entropy = high confidence = correct
    )
    
    return {
        "t_stat": t_stat,
        "p_value": p_value,
        "auroc": auroc,
        "mean_correct": np.mean(correct_entropies),
        "mean_incorrect": np.mean(incorrect_entropies)
    }
```

### Training Protocol

**Type:** Inference-only (no training required)

**Generation Parameters:**
| Parameter | Value | Justification |
|-----------|-------|---------------|
| Temperature | 0.7 | Same as H-E1, allows varied outputs |
| Top-p | 0.9 | Standard nucleus sampling |
| Max tokens | 128 | Sufficient for QA answers |
| Samples per question | 10 | Match H-E1, aggregate entropy |

**Evaluation Protocol:**
1. For each question: generate 10 responses
2. Compute mean entropy across samples
3. Evaluate correctness of majority answer
4. Aggregate entropies and correctness labels
5. Compute statistics

### Evaluation

**Primary Metrics:**

| Metric | Formula | Success Criterion |
|--------|---------|-------------------|
| t-test p-value | t-test(entropy_incorrect, entropy_correct) | p < 0.05 |
| Direction | mean(entropy_incorrect) > mean(entropy_correct) | Positive difference |
| AUROC | ROC-AUC(-entropy, correctness) | > 0.55 |

**Secondary Metrics:**
- Effect size (Cohen's d)
- Correlation coefficient (Pearson r)

**PoC Pass Condition:**
1. p-value < 0.05 for entropy difference
2. Higher entropy for incorrect answers
3. AUROC > 0.55 (better than random)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (correct/incorrect)
- Library: sklearn.metrics, scipy.stats
- Code:
```python
from sklearn.metrics import roc_auc_score
from scipy.stats import ttest_ind

auroc = roc_auc_score(y_true, y_scores)
t_stat, p_val = ttest_ind(group1, group2)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of AUROC target (0.55) vs actual, p-value threshold

#### Additional Figures (LLM Autonomous)
1. **Entropy Distribution by Correctness**: Two overlapping histograms (correct vs incorrect)
2. **ROC Curve**: AUROC visualization with confidence band
3. **Scatter Plot**: Entropy vs consistency colored by correctness (connects to H-M2)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on full validation set (~11K questions)
2. t-test p-value < 0.05 (entropy differs by correctness)
3. mean_incorrect_entropy > mean_correct_entropy (direction correct)
4. AUROC > 0.55 (entropy has predictive power)

**If PASS:** Proceed to H-M2 (consistency mechanism)
**If FAIL:** STOP workflow, entropy signal not predictive

---

## Appendix: Reference Implementations

### 1. Semantic Entropy (Kuhn et al., 2023)
- **Repository:** github.com/jlko/semantic_uncertainty
- **Relevance:** Semantic clustering over token entropy; our approach tests raw token entropy first
- **Key Insight:** They cluster similar answers before entropy; we test whether clustering is necessary

### 2. H-E1 Implementation (Internal)
- **Path:** h-e1/src/
- **Validated Components:** entropy_module.py, response_generator.py
- **Reuse:** Direct extension with correctness evaluation

### 3. TriviaQA Evaluation Standards
- **Repository:** github.com/mandarjoshi90/triviaqa
- **Relevance:** Standard F1/EM evaluation for QA
- **Note:** We use simplified exact match for PoC

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
1. H-E1 COMPLETED (PASS) - Entropy/consistency computable
2. H-M1 IN_PROGRESS - Testing entropy-correctness correlation

---

*MCP Tools Used: None (unavailable in this session)*
*Specifications based on H-E1 validated code and Phase 2B planning*
*Next Phase: Phase 3 - Implementation Planning*
