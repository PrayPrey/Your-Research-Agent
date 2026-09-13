# Experiment Design: H-M3

**Date:** 2026-08-08
**Author:** Anonymous
**Hypothesis Statement:** Amplification Index (AI) is positive for perplexity filtering vs random (AI > 0, 95% CI excludes zero)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Quantifies contamination amplification via Amplification Index metric.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 (VALIDATED, PARTIAL_PASS)
**Gate Status:** SHOULD_WORK (failure continues workflow)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (CCR variation by filtering strategy)

### Gate Condition
**SHOULD_WORK**: AI > 0 for perplexity filtering vs random, 95% CI excludes zero.
- Success: Demonstrates contaminated examples disproportionately benefit from curation
- Failure: AI ≈ 0 indicates no differential amplification; workflow continues

---

## Continuation Context

H-M3 reuses models trained in H-M1 (15 models: 3 strategies × 5 seeds). No additional training required. This is inference-only evaluation comparing performance on contaminated vs clean benchmark subsets.

### Previous Hypothesis Results (if applicable)
**H-M1 PARTIAL_PASS:**
- CCR measurement methodology validated
- Bootstrap statistics correctly detect CCR differences (diff=0.1594, p=0.0000)
- Gate conditions met with simulated data
- Models: 15 Pythia-1B checkpoints (3 filtering strategies × 5 seeds)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Limited relevant results** - Archon KB primarily contains diffusers/image generation content. Contamination detection literature not well represented.

Key insight from search: No direct Amplification Index implementations found in KB.

### Archon Code Examples

No directly relevant code examples for benchmark contamination measurement.

### Exa GitHub Implementations

**Query 1: Benchmark Contamination Detection Methods**

**Finding 1: Kernel Divergence Score (KDS)**
- **Paper**: "How Contaminated Is Your Benchmark?" (MLRP 2025)
- **URL**: https://github.com/deeplearning-wisc/kernel-divergence-score
- **Method**: Computes divergence between kernel similarity matrices before/after fine-tuning
- **Relevance**: Alternative contamination detection approach; AI uses simpler accuracy differential

**Finding 2: ConTAM Analysis Framework**
- **Paper**: "Evaluation data contamination in LLMs" (arXiv 2411.03923)
- **Method**: Estimated Performance Gain (EPG) metric - similar concept to Amplification Index
- **Key insight**: "contamination may have a much larger effect than reported"
- **Relevance**: Direct conceptual parallel to AI computation

**Finding 3: Contamination Detection Survey**
- **Paper**: "Are LLM Benchmarks Already Contaminated?" (ACL GEM 2026)
- **Taxonomy**: T1 (Exact), T2 (Syntactic), T3 (Semantic), T4 (Task-Level)
- **MMLU inflation estimates**: 6%-40% depending on model and detection method
- **Relevance**: Validates need for time-stratified clean benchmarks

**Finding 4: MMLU-CF (Contamination-Free)**
- **URL**: https://microsoft.github.io/MMLU-CF/
- **Dataset**: 10,000 test + 10,000 validation questions
- **Method**: Decontamination rules + closed-source test set
- **Relevance**: Potential clean benchmark for AI calculation

**Query 2: MMLU Evaluation with Bootstrap CI**

**Finding 1: Bootstrap CI for LLM Evaluation**
- **URL**: https://engineering.indeedblog.com/blog/2026/07/bootstrap-confidence-intervals-for-llm-evaluation/
- **Method**: Cluster bootstrap resampling inputs with all k runs
- **Code**: `percentile(statistic_on_resampled, [2.5, 97.5])` for 95% CI
- **Relevance**: EXACT method needed for AI confidence interval

**Finding 2: MMLU Evaluation Code**
- **URL**: https://github.com/HaoAreYuDong/MachineLearningLM/blob/main/src/evaluation/mmlu_eval.py
- **Method**: Log-likelihood scoring of "Answer: X" continuations
- **Metrics**: Micro accuracy (overall), macro accuracy (avg over subjects)
- **Relevance**: Standard evaluation approach

**Finding 3: MMLU-Redux**
- **URL**: https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux
- **Dataset**: 5,700 manually re-annotated questions, 6.49% error rate identified
- **Error types**: bad_question_clarity, no_correct_answer, wrong_groundtruth
- **Relevance**: Clean subset for contamination analysis

### 🎯 Implementation Priority Assessment

**For Amplification Index, no paper author implementation exists** - AI is a novel metric defined in our hypothesis.

**Recommended Implementation Path:**
- Primary: Custom implementation based on accuracy differential formula
- Fallback: Adapt EPG (Estimated Performance Gain) methodology from ConTAM
- Justification: AI = (Acc_contaminated - Acc_baseline) - (Acc_clean - Acc_baseline) is straightforward computation

### Code Analysis (Serena MCP)

*Skipped* - AI computation is straightforward accuracy differential; no complex architecture to analyze.

---

## Experiment Specification

### Dataset

**Evaluation Benchmarks (2 required for AI calculation):**

| Benchmark | Role | Samples | Source |
|-----------|------|---------|--------|
| MMLU | Potentially contaminated | 14,042 | `cais/mmlu` |
| MMLU-Redux 2.0 | Clean reference (error-corrected) | 5,700 | `edinburgh-dawg/mmlu-redux-2.0` |

**Alternative clean benchmark (if Redux insufficient):**
- MMLU-CF: `microsoft/mmlu-cf` (closed-source test, open validation)

**Time-stratification approach:**
- Use MMLU questions that post-date Pile cutoff (April 2020) as "clean"
- Use pre-cutoff questions as "potentially contaminated"

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `cais/mmlu`, `edinburgh-dawg/mmlu-redux-2.0`
- Code:
```python
from datasets import load_dataset

# Original MMLU
mmlu = load_dataset("cais/mmlu", "all", split="test")

# Clean subset (error-corrected)
mmlu_redux = load_dataset("edinburgh-dawg/mmlu-redux-2.0", split="test")
# Filter to error_type == "ok" for clean questions
clean_questions = mmlu_redux.filter(lambda x: x["error_type"] == "ok")
```

### Models

#### Baseline Model

**Architecture**: Pythia-1B (from H-M1)
**Configuration**: GPT-NeoX architecture, 1B parameters
**Source**: EleutherAI/pythia-1b

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `EleutherAI/pythia-1b`
- Code:
```python
from transformers import GPTNeoXForCausalLM, AutoTokenizer

model = GPTNeoXForCausalLM.from_pretrained(
    "EleutherAI/pythia-1b",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-1b")
```

**H-M1 Model Variants** (reused, no new training):
- `random_seed{1-5}`: Random sampling baseline
- `perplexity_seed{1-5}`: Perplexity-filtered training
- `dedup_seed{1-5}`: Deduplication-filtered training

#### Proposed Model

**Architecture:** No new model - Amplification Index computed from existing H-M1 model outputs

**Core Mechanism Implementation:**

```python
# Amplification Index Computation
# Based on: ConTAM EPG methodology + custom formulation

def compute_amplification_index(
    model_outputs: Dict[str, np.ndarray],  # {model_id: predictions}
    contaminated_mask: np.ndarray,          # bool array
    clean_mask: np.ndarray,                 # bool array
    ground_truth: np.ndarray                # correct answers
) -> Tuple[float, Tuple[float, float]]:
    """
    Compute Amplification Index with bootstrap CI.
    
    AI = (Acc_contaminated - Acc_clean) for treatment
       - (Acc_contaminated - Acc_clean) for baseline
    
    Simplified for single strategy comparison:
    AI = delta_perplexity - delta_random
    where delta = Acc_contaminated - Acc_clean
    """
    results = {}
    for model_id, preds in model_outputs.items():
        correct = (preds == ground_truth)
        acc_contaminated = correct[contaminated_mask].mean()
        acc_clean = correct[clean_mask].mean()
        results[model_id] = acc_contaminated - acc_clean
    
    # Aggregate by strategy
    perplexity_deltas = [results[m] for m in results if "perplexity" in m]
    random_deltas = [results[m] for m in results if "random" in m]
    
    AI = np.mean(perplexity_deltas) - np.mean(random_deltas)
    
    # Bootstrap CI
    ci = bootstrap_confidence_interval(
        perplexity_deltas, random_deltas, 
        statistic=lambda p, r: np.mean(p) - np.mean(r),
        n_bootstrap=10000, confidence=0.95
    )
    
    return AI, ci

def bootstrap_confidence_interval(group1, group2, statistic, n_bootstrap, confidence):
    """Paired cluster bootstrap for AI confidence interval."""
    stats = []
    n = len(group1)
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        s = statistic([group1[i] for i in idx], [group2[i] for i in idx])
        stats.append(s)
    
    alpha = (1 - confidence) / 2
    return (np.percentile(stats, alpha*100), 
            np.percentile(stats, (1-alpha)*100))
```

### Training Protocol

**No training required** - H-M3 reuses H-M1 trained models.

**Inference Protocol:**
- **Models**: 15 checkpoints from H-M1 (3 strategies × 5 seeds)
- **Evaluation**: Log-likelihood MCQ scoring
- **Batch Size**: 32 (inference)
- **Precision**: FP16
- **Seeds**: Uses 5 seeds from H-M1

**Evaluation Settings:**
- Few-shot: 5-shot (standard MMLU protocol)
- Scoring: Log-probability of answer token
- Format: "Question: {q}\nA. {a}\nB. {b}\nC. {c}\nD. {d}\nAnswer:"

### Evaluation

**Primary Metrics:**
- **Amplification Index (AI)**: `mean(delta_perplexity) - mean(delta_random)`
  - Where `delta = Acc_contaminated - Acc_clean`
- **95% Bootstrap CI**: Must exclude zero for significance

**Secondary Metrics:**
- Per-strategy accuracy on contaminated subset
- Per-strategy accuracy on clean subset
- Effect size (Cohen's d)

**Success Criteria (Gate: SHOULD_WORK):**
- AI > 0 (positive amplification)
- 95% CI lower bound > 0 (statistical significance)

**Expected Results** (based on research):
- Contamination inflation estimates: 6-40% (from survey)
- Expected AI range: 0.02-0.15 (preliminary estimate)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Classification (MCQ)
- Library: Custom + numpy/scipy for bootstrap
- Code:
```python
import numpy as np
from scipy import stats

# Accuracy calculation
def compute_accuracy(predictions: np.ndarray, labels: np.ndarray) -> float:
    return (predictions == labels).mean()

# Bootstrap CI
def bootstrap_ci(data: np.ndarray, n_bootstrap: int = 10000) -> Tuple[float, float]:
    boot_means = [np.mean(np.random.choice(data, len(data), replace=True)) 
                  for _ in range(n_bootstrap)]
    return np.percentile(boot_means, 2.5), np.percentile(boot_means, 97.5)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **AI Bar Chart**: Amplification Index with 95% CI error bars
  - X-axis: Comparison (perplexity vs random)
  - Y-axis: AI value
  - Error bars: Bootstrap 95% CI
  - Reference line at AI=0

#### Additional Figures (LLM Autonomous)
- **Accuracy Heatmap**: Rows=strategies, Cols=contaminated/clean
- **Delta Distribution**: Box plot of per-seed deltas by strategy
- **Overlap Audit**: Contaminated vs clean question distribution

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: TRUE - AI is computed from accuracy differentials
- `mechanism_isolatable`: TRUE - Clean vs contaminated partitions are separable
- `baseline_measurable`: TRUE - Random strategy provides baseline

### Architecture Compatibility
- H-M1 models produce per-question accuracy scores
- Contamination labels derive from MMLU-Redux error annotations or temporal split
- Bootstrap requires minimum 5 samples per group (satisfied: 5 seeds)

### Activation Indicators
- `mechanism_log_message`: "Computing AI: contaminated_acc={x:.4f}, clean_acc={y:.4f}, delta={d:.4f}"
- `tensor_shape_change`: N/A (metric computation, not tensor operation)
- `metric_delta_expected`: AI ∈ [0.01, 0.20] indicates mechanism activation

### Mechanism Verification Code
```python
def verify_ai_mechanism(ai_value: float, ci_lower: float, ci_upper: float) -> dict:
    """Verify Amplification Index mechanism is working."""
    verification = {
        "ai_computed": ai_value is not None,
        "ai_positive": ai_value > 0,
        "ci_excludes_zero": ci_lower > 0,
        "ci_width_reasonable": (ci_upper - ci_lower) < 0.5,
        "effect_size_meaningful": abs(ai_value) > 0.01
    }
    verification["mechanism_active"] = all(verification.values())
    return verification
```

### Failure Detection
- AI = 0 exactly: Partition assignment error
- CI width > 0.5: Insufficient samples or high variance
- Negative AI: Contamination benefits random strategy more (unexpected)

### Success Criteria
- `hypothesis_support_threshold`: AI > 0, CI_lower > 0
- `hypothesis_support_metric`: "Amplification Index with 95% CI"

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. AI computed for all 5 seed pairs
3. Bootstrap CI successfully computed
4. AI > 0 AND 95% CI lower bound > 0

---

## Appendix: Reference Implementations

### Contamination Detection Methods
1. **KDS**: https://github.com/deeplearning-wisc/kernel-divergence-score
2. **ConTAM**: https://arxiv.org/abs/2411.03923 (EPG methodology)
3. **MMLU-Redux**: https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux-2.0

### MMLU Evaluation
1. **Standard eval**: https://github.com/HaoAreYuDong/MachineLearningLM/blob/main/src/evaluation/mmlu_eval.py
2. **Bootstrap CI**: https://engineering.indeedblog.com/blog/2026/07/bootstrap-confidence-intervals-for-llm-evaluation/

### Clean Benchmarks
1. **MMLU-CF**: https://microsoft.github.io/MMLU-CF/
2. **MMLU-Pro-Clean**: https://huggingface.co/datasets/adamallcock/mmlu-pro-clean

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-08

### Workflow History for This Hypothesis
- 2026-08-08: Phase 2C experiment design initiated
- 2026-08-08: MCP research completed (Archon, Exa)
- 2026-08-08: Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
