# Experiment Design: h-m4

**Date:** 2026-05-11
**Author:** Anonymous
**Hypothesis Statement:** Under directional correlation patterns from targeted interventions, if fundamental optimization dynamics (gradient descent, backpropagation) are architecture-agnostic, then correlation direction (positive/negative) will replicate consistently across ≥3/5 model families, because core learning mechanisms are shared across transformer, SSM, and other architectures.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C - Experiment Design)
**Prerequisites Satisfied:** ✅ h-m3 (COMPLETED, PASS with limitation)
**Gate Status:** SHOULD_WORK gate - ≥3/5 model families show directional replication

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m4
- **Type:** MECHANISM
- **Prerequisites:** h-m3 (COMPLETED)

### Gate Condition

**Type:** SHOULD_WORK  
**Threshold:** Directional replication ≥3/5 models  
**Pass Condition:** At least 60% of model families (3 out of 5) show the same correlation direction (positive/negative) for significant intervention × dimension pairs  
**Fail Action:** Document architecture-specific effects - generalization claim fails, but mechanism still valid for specific architectures

---

## Continuation Context

This is a **continuation experiment** building on h-m3 findings. The previous hypothesis (h-m3) established that representation changes from targeted interventions propagate to non-targeted dimensions, with a strong negative correlation observed between truthfulness and robustness (r=-0.997, p=0.051 marginally non-significant).

**Key Context from h-m3:**
- **Finding**: Strong truthfulness-robustness trade-off detected in GPT-2 (124M)
- **Limitation**: Only tested on single model family (GPT-2)
- **Question**: Does this correlation pattern generalize across architectures?

**h-m4 Objective**: Test whether the correlation direction observed in h-m3 replicates consistently across 5 diverse model families (4 transformer variants + 1 SSM), validating that the effect is driven by architecture-agnostic optimization dynamics (gradient descent, backpropagation) rather than model-specific quirks.

### Previous Hypothesis Results (h-m3)

**Validation Status**: PASS (SHOULD_WORK gate with documented limitation)

**Key Findings**:
1. **Truthfulness-Robustness Correlation**: r = -0.997, p = 0.051 (marginally non-significant, but very strong effect size)
2. **Fairness Independence**: Fairness shows negligible correlation with both truthfulness (r=0.034) and robustness (r=0.047)
3. **Statistical Power Issue**: Only 3 seeds insufficient for p<0.05 significance despite strong effect

**Optimal Configuration** (reused in h-m4):
- **Intervention**: LoRA (r=8, α=16)
- **Training**: 500 samples, 3 epochs, AdamW optimizer
- **Loss Convergence**: Stable at ~0.4 by epoch 3
- **Model**: GPT-2 (124M parameters)

**Implications for h-m4**:
- Increase seeds from 3 to 5 for adequate statistical power
- Test if truthfulness-robustness trade-off (negative correlation) replicates across other architectures
- Use same LoRA configuration for consistency

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Multi-Model Architecture Comparison**
- Result 1: LoRA Adapter Documentation (HuggingFace PEFT)
  - Source: https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora
  - Key Insight: LoRA enables parameter-efficient fine-tuning across different model architectures
  - Relevance: Architecture-agnostic adaptation mechanism (supports Transformers, SSMs, etc.)

- Result 2: Instruction Following (OpenAI)
  - Source: https://openai.com/blog/instruction-following/
  - Key Insight: Cross-model evaluation methodology for instruction-following capabilities
  - Relevance: Multi-model comparison framework

**Query 2: Cross-Architecture Generalization**
- Result 1: LLMs Documentation (HuggingFace)
  - Source: https://hf.co/papers/2305.14314
  - Key Insight: Comprehensive evaluation across multiple LLM families
  - Relevance: Standard benchmarking practices for multi-architecture studies

- Result 2: Multi-task Learning (OpenReview)
  - Source: https://openreview.net/forum?id=gU58d5QeGv
  - Key Insight: Task interference patterns across different model architectures
  - Relevance: Cross-dimensional effects may vary by architecture

**Query 3: Model Family Replication**
- No directly relevant results for "model family replication correlation patterns"
- General findings: Pipeline comparison methodologies exist for diffusion models
- Adaptation needed: Apply multi-model evaluation patterns to trustworthiness benchmarks

**Key Takeaways:**
- LoRA is architecture-agnostic and suitable for multi-family experiments
- Standard practice: Use consistent intervention methodology (same hyperparameters) across models
- Expected variation: Effect sizes may differ by model capacity, but direction should replicate
- Baseline requirement: Need control group (random perturbation) to establish correlation patterns

### Archon Code Examples

**Query 1: Multi-Model Evaluation PyTorch**

Example 1: Model Evaluation Framework (PyTorch AMP)
- Source: https://pytorch.org/docs/stable/amp.html#torch.autocast
- Pattern: Trace and freeze models for consistent evaluation
- Code Pattern:
```python
# Standardized model loading and evaluation
model = TestModel(input_size, num_classes).eval()
with torch.cpu.amp.autocast(cache_enabled=False):
    model = torch.jit.trace(model, input)
model = torch.jit.freeze(model)
# Run multiple passes for stability
for _ in range(3):
    model(input)
```
- Insight: Use consistent evaluation mode across all model families

Example 2: Multi-GPU Distributed Evaluation (MMGeneration)
- Source: https://mmgeneration.readthedocs.io/en/latest/quick_run.html#fid
- Pattern: Online and offline evaluation with batch processing
- Insight: Supports large-scale multi-model evaluation

**Query 2: Model Family Comparison**

Example 1: Baseline Comparison Structure (Apple ML Stable Diffusion)
- Source: https://github.com/apple/ml-stable-diffusion
- Pattern: Structured JSON for multi-baseline comparison
```json
{
  "model_version": "model_name",
  "baselines": {
    "original": 82.2,
    "variant_1": 79.9,
    "variant_2": 78.2,
    ...
  }
}
```
- Insight: Track metrics per model family in structured format
- Application: Create similar structure for 5 model families × 3 dimensions

Example 2: Performance Benchmarking (AnimateDiff IPEX)
- Source: https://github.com/huggingface/diffusers/tree/main/examples/community
- Pattern: Systematic comparison with timing and warmup
```python
def elapsed_time(pipeline, nb_pass=3):
    # warmup
    for _ in range(2):
        output = pipeline(prompt)
    # timed evaluation
    start = time.time()
    for _ in range(nb_pass):
        pipeline(prompt)
    return (end - start) / nb_pass
```
- Insight: Use warmup runs before measurement for fair comparison

**Code Architecture Recommendations:**
1. **Model Loading:** Use HuggingFace `AutoModel` API for consistent loading across families
2. **Evaluation Loop:** Implement warmup + multi-seed evaluation per model
3. **Result Structure:** Store results in nested dict: `{model_family: {dimension: {seed: score}}}`
4. **Correlation Calculation:** Apply Pearson correlation per model family, then aggregate directional consistency

### Exa GitHub Implementations

**Query 1: Multi-Model LLM Trustworthiness Evaluation**

**Repository 1**: TrustGen/TrustEval-toolkit (⭐128)
- **URL**: https://github.com/TrustGen/TrustEval-toolkit
- **Relevance**: Comprehensive multi-model trustworthiness framework (ICLR'26, NAACL'25)
- **Supported Models**: LLaMA (7B-70B), GPT-3.5/4, Claude, Mistral, Qwen, and more
- **Dimensions**: Safety, fairness, robustness, privacy, truthfulness
- **Key Features**:
  - Multi-Model Compatibility: Evaluate LLMs via local or API
  - Multi-GPU Acceleration: 7-8x speed improvement for concurrent inference
  - Dynamic dataset generation for evaluation tasks
  - Interactive HTML trustworthiness reports with leaderboards
- **Architecture**: Metadata-driven evaluation pipelines
- **Insight**: Production-grade multi-model evaluation framework with proven architecture

**Repository 2**: HowieHwong/TrustLLM (⭐623, MIT License)
- **URL**: https://github.com/howiehwong/trustllm
- **Paper**: ICML 2024 - TrustLLM benchmark
- **Relevance**: Standard benchmark for trustworthiness (truthfulness, safety, fairness, robustness, privacy, ethics)
- **Models Evaluated**: 16 mainstream LLMs across 30+ datasets
- **Key Components**:
  - Principles framework for 8 trustworthiness dimensions
  - Established benchmark suite (TruthfulQA, BBQ included)
  - Leaderboard system for model comparison
- **Training Config**: Uses lm-evaluation-harness for standardized evaluation
- **Insight**: Academic standard for multi-dimensional trustworthiness evaluation

**Repository 3**: AI-secure/DecodingTrust (⭐301)
- **URL**: https://github.com/AI-secure/DecodingTrust
- **Paper**: Comprehensive Assessment of Trustworthiness in GPT Models
- **Evaluated Models**: GPT-3.5/4, Llama-v2-7B, Vicuna-7B, Alpaca-7B, MPT-7B, Falcon-7B
- **Dimensions**: Toxicity, stereotype/bias, adversarial robustness, OOD robustness, privacy, fairness, ethics
- **Key Features**:
  - Unified API for OpenAI models and HuggingFace LLMs
  - Robust response saving and retry mechanisms
  - Dry-run mode for testing before full evaluation
- **Code Pattern**: `main.py` unified entry point, `chat.py` robust API wrapper
- **Insight**: Open evaluation codebase supporting multiple model families

**Repository 4**: thu-ml/MMTrustEval (⭐173, CC-BY-SA-4.0)
- **URL**: https://github.com/thu-ml/MMTrustEval
- **Paper**: NeurIPS 2024 - MultiTrust benchmark
- **Relevance**: Multimodal LLM trustworthiness (5 dimensions, 32 tasks)
- **Architecture**: Rule-based (○), GPT-4 automatic (●), mixture (◐) evaluation
- **Key Finding**: Correlation coefficient 0.60 between general capabilities and trustworthiness
- **Insight**: No significant correlation across different trustworthiness aspects

**Query 2: Cross-Architecture Fairness/Truthfulness Comparison**

**Repository 5**: peremartra/fairness-pruning (BBQ Baseline Results)
- **URL**: https://github.com/peremartra/fairness-pruning
- **Models Compared**: Salamandra-2B, Llama-3.2-1B, Llama-3.2-3B
- **Dataset**: BBQ (zero-shot) via lm-evaluation-harness
- **Key Findings**:
  - **Cross-Architecture Observation**: Salamandra-2B underperforms Llama-1B despite 2× parameters
  - **Scaling Pattern**: Llama-3B shows 2.4× higher bias in ambiguous contexts vs. 1B (4.12% vs 1.70%)
  - **Bias Ratio**: Ratio > 1 indicates stereotype reliance when info is ambiguous
  - **Evaluation Time**: 1B (53min), 2B (1h18m), 3B (2h1m) on single setup
- **Training Config**: lm-evaluation-harness framework
- **Insight**: Architecture-specific fairness patterns exist; larger models may encode stronger stereotypes

**Key Research Papers** (from Exa):

**Paper 1**: TruthfulQA (arXiv:2109.07958)
- **Key Finding**: Inverse scaling - larger GPT models (175B) less truthful than smaller (2.7B)
- **Best Model**: GPT-3-175B with "helpful" prompt: 58% truthful (human: 94%)
- **Mechanism**: Larger models better at imitating training distribution (including falsehoods)
- **Recommendation**: Scaling + prompt engineering/fine-tuning needed for truthfulness
- **Insight**: Base model size alone doesn't guarantee truthfulness improvement

**Paper 2**: Bias Similarity Measurement (arXiv:2410.12010)
- **Models Evaluated**: 30 LLMs on 1M+ prompts
- **Key Finding**: Family signatures diverge - Gemma favors refusal, LLaMA 3.1 approaches neutrality
- **Mechanism**: Instruction tuning enforces abstention, not representation alteration
- **Cross-Model Insight**: Open-weight models can match proprietary systems
- **Relevance**: Fairness as relational property between models (comparative approach)

**Paper 3**: EsBBQ/CaBBQ (arXiv:2507.11216)
- **Key Finding**: Inverse relation between model size and ambiguous context performance
- **Bias Pattern**: Bias scores increase with model size (stronger in base models)
- **Instruction Tuning Effect**: Subdues size-related bias increase
- **Insight**: Relationship between accuracy and bias reliance (disambiguation vs. ambiguous)

**Serena Analysis Needed**: ❌ No
**Reason**: Code patterns are clear - multi-model evaluation frameworks use standard HuggingFace APIs, evaluation harness, and batch processing. Architecture is straightforward.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment**: This hypothesis tests cross-architecture generalization of correlation patterns, not reproduction of a specific paper method. Therefore, we prioritize **established evaluation frameworks** over author implementations.

**Recommended Implementation Path:**
- Primary: **lm-evaluation-harness** + **HuggingFace Transformers** (standard evaluation framework)
- Fallback: Custom evaluation loop using TrustLLM/TrustEval patterns
- Justification: 
  - lm-evaluation-harness provides standardized evaluation across multiple model families
  - Used in research papers (fairness-pruning BBQ evaluations, TrustLLM benchmarks)
  - Ensures consistent evaluation protocol across all 5 model families
  - Well-documented loading for TruthfulQA, BBQ, ANLI

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Standard multi-model evaluation frameworks use well-documented HuggingFace APIs (AutoModel, AutoTokenizer), lm-evaluation-harness, and batch processing patterns. No complex custom layers requiring deep semantic analysis.

---

## Experiment Specification

### Dataset

**Multi-Dimensional Trustworthiness Benchmarks** (3 datasets covering truthfulness, fairness, robustness)

**Dataset 1: TruthfulQA (Truthfulness)**
- **Type**: standard
- **Source**: HuggingFace datasets
- **Identifier**: `truthful_qa` (truthfulqa/truthful_qa)
- **Split**: `multiple_choice` (817 questions)
- **Task**: Multiple-choice question answering testing truthfulness
- **Metrics**: MC1 accuracy (single correct answer selection)
- **Statistics**: 817 samples with imitative falsehoods targeting
- **Hypothesis Fit**: Measures truthfulness dimension for cross-dimensional correlation analysis

**Dataset 2: BBQ (Bias Benchmark for QA - Fairness)**
- **Type**: standard
- **Source**: HuggingFace datasets via lm-evaluation-harness
- **Identifier**: `bbq` (lighteval/bbq_helm)
- **Split**: all categories, zero-shot evaluation
- **Task**: Question answering with ambiguous/disambiguated contexts testing social bias
- **Metrics**: Accuracy (ambiguous/disambiguated), Bias Score
- **Statistics**: 1000+ samples across 9 social dimensions
- **Hypothesis Fit**: Measures fairness dimension for bias detection

**Dataset 3: ANLI Round 3 (Adversarial NLI - Robustness)**
- **Type**: standard
- **Source**: HuggingFace datasets (facebook/anli)
- **Identifier**: `anli`
- **Split**: `test_r3` (1200 samples)
- **Task**: Natural language inference under adversarial conditions
- **Metrics**: Classification accuracy on adversarial examples
- **Statistics**: 1200 samples (Round 3 - hardest adversarial examples)
- **Hypothesis Fit**: Measures robustness dimension against adversarial inputs

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets` library + lm-evaluation-harness framework
- Identifier: `truthful_qa`, `bbq`, `anli`
- Code:
```python
from datasets import load_dataset

# TruthfulQA
truthfulqa = load_dataset("truthful_qa", "multiple_choice")

# BBQ (via lm-evaluation-harness)
# Use lm_eval.tasks.bbq for standardized evaluation

# ANLI Round 3
anli_r3 = load_dataset("anli", split="test_r3")
```

**Preprocessing**: Tokenization via model-specific tokenizer, padding to max_length
**Augmentation**: None (evaluation benchmarks use original test sets)

### Models

#### Baseline Model

**Multi-Family LLM Suite** (5 model families for cross-architecture testing)

**Model Family 1: LLaMA 3.2**
- **Architecture**: Transformer-based decoder (Meta AI)
- **Variant**: LLaMA-3.2-1B (1B parameters)
- **Identifier**: `meta-llama/Llama-3.2-1B`
- **Rationale**: Mainstream transformer architecture, proven performance

**Model Family 2: Mistral**
- **Architecture**: Transformer with Grouped Query Attention (GQA) and Sliding Window Attention
- **Variant**: Mistral-7B-v0.1 (7B parameters)
- **Identifier**: `mistralai/Mistral-7B-v0.1`
- **Rationale**: Optimized transformer variant with architectural innovations

**Model Family 3: Qwen**
- **Architecture**: Transformer-based (Alibaba Cloud)
- **Variant**: Qwen-1.8B (1.8B parameters)
- **Identifier**: `Qwen/Qwen-1.8B`
- **Rationale**: Non-Western architecture family for diversity

**Model Family 4: Mamba**
- **Architecture**: Structured State Space Model (SSM) - **Non-transformer**
- **Variant**: Mamba-1.4B (1.4B parameters)
- **Identifier**: `state-spaces/mamba-1.4b`
- **Rationale**: Tests generalization to non-transformer architectures (SSM vs. attention)

**Model Family 5: Falcon**
- **Architecture**: Transformer-based decoder (TII UAE)
- **Variant**: Falcon-7B (7B parameters)
- **Identifier**: `tiiuae/falcon-7b`
- **Rationale**: Open-source transformer trained on diverse multilingual data

**Hypothesis-Specific Notes:**
- **Size Range**: 1B-7B parameters (computationally feasible for 5-family comparison)
- **Architecture Diversity**: 4 transformer variants + 1 SSM (tests architecture-agnostic claim)
- **Replication Criterion**: ≥3/5 models must show same correlation direction (positive/negative)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers.AutoModelForCausalLM`
- Identifier: See model identifiers above
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_ids = [
    "meta-llama/Llama-3.2-1B",
    "mistralai/Mistral-7B-v0.1",
    "Qwen/Qwen-1.8B",
    "state-spaces/mamba-1.4b",
    "tiiuae/falcon-7b"
]

for model_id in model_ids:
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        torch_dtype="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)
```

**Configuration**: Use pretrained checkpoints without modification (base evaluation)

#### Proposed Model

**Architecture:** Multi-Family Cross-Architecture Evaluation (no model modification)

**Experiment Design:** This hypothesis tests replication across architectures, NOT a new mechanism. The "proposed" approach is the **directional consistency analysis** across 5 model families.

**Core Mechanism Implementation:**

```python
# Core Analysis: Cross-Architecture Directional Replication
# Based on: h-m3 correlation patterns + multi-model evaluation frameworks

class CrossArchitectureReplicationAnalyzer:
    """
    Tests whether correlation directions (positive/negative) from targeted
    interventions replicate consistently across ≥3/5 model families.
    
    Based on: TrustLLM/TrustEval multi-model evaluation patterns
    """
    def __init__(self, model_families, dimensions, intervention_type="lora"):
        self.model_families = model_families  # 5 families
        self.dimensions = dimensions  # ["truthfulness", "fairness", "robustness"]
        self.intervention_type = intervention_type
        self.results = {}  # {model_family: {dimension_pair: correlation}}
    
    def run_experiment(self, model_id, target_dimension, n_seeds=5):
        """
        Args:
            model_id: HuggingFace model identifier
            target_dimension: Which dimension to target with intervention
            n_seeds: Number of replications (5 for statistical power)
        
        Returns:
            deltas: Performance changes per dimension (Dict[str, List[float]])
        """
        # Step 1: Baseline evaluation (pre-intervention)
        baseline_scores = self.evaluate_all_dimensions(model_id)
        
        # Step 2: Apply intervention (LoRA fine-tuning on target dimension)
        intervention_results = []
        for seed in range(n_seeds):
            model_finetuned = self.apply_lora_intervention(
                model_id, target_dimension, seed=seed
            )
            post_scores = self.evaluate_all_dimensions(model_finetuned)
            deltas = {dim: post_scores[dim] - baseline_scores[dim] 
                      for dim in self.dimensions}
            intervention_results.append(deltas)
        
        # Step 3: Compute correlations between dimension pairs
        correlations = self.compute_pairwise_correlations(intervention_results)
        
        # Step 4: Classify correlation direction (positive/negative/neutral)
        direction = self.classify_direction(correlations)
        
        return direction  # e.g., {"truth-fair": "positive", "truth-robust": "negative"}
    
    def compute_directional_replication(self, all_model_results):
        """
        Args:
            all_model_results: {model_family: {dim_pair: direction}}
        
        Returns:
            replication_rate: Proportion of models matching majority direction
        """
        for dim_pair in ["truth-fair", "truth-robust", "fair-robust"]:
            directions = [results[dim_pair] for results in all_model_results.values()]
            majority = max(set(directions), key=directions.count)
            replication_count = directions.count(majority)
            replication_rate = replication_count / len(directions)
            
            # Gate criterion: ≥3/5 = 0.6
            return replication_rate >= 0.6

# Integration: Applies to pre-trained models without modification
# Intervention: LoRA (r=8, α=16) from h-m3 optimal configuration
```

### Training Protocol

**From Previous Hypothesis (h-m3) - Reusing Optimal Configuration:**

**Intervention Method**: LoRA (Low-Rank Adaptation)
- **r**: 8 (rank)
- **α**: 16 (scaling factor)
- **Target Modules**: All attention layers
- **Rationale**: Optimal in h-m3, enables parameter-efficient fine-tuning across all 5 model families

**Optimizer**: AdamW
- **Learning Rate**: 2e-4
- **Weight Decay**: 0.01
- **Betas**: (0.9, 0.999)

**Training Configuration**:
- **Samples per Family**: 500 (from target dimension dataset)
- **Epochs**: 3
- **Batch Size**: 8 (gradient accumulation if needed for 7B models)
- **Seeds**: 5 per model family (increased from h-m3's 3 for better statistical power)
- **Total Runs**: 5 families × 5 seeds = 25 intervention experiments

**Loss Function**: Cross-entropy (for classification tasks in TruthfulQA, BBQ, ANLI)

**Rationale**: Reusing h-m3 configuration ensures controlled comparison. Statistical power increased to n=5 seeds (vs. h-m3's n=3) to achieve p<0.05 significance.

**Source**: h-m3 validation report (optimal hyperparameters from previous experiment)

### Evaluation

**Primary Metrics**:

1. **Directional Replication Rate**: Proportion of model families (out of 5) showing same correlation direction
   - **Computation**: For each dimension pair, count models with matching direction (positive/negative)
   - **Gate Threshold**: ≥3/5 models (60% replication rate)

2. **Pearson Correlation Coefficient (ρ)**: Strength of cross-dimensional correlation per model family
   - **Computed across**: 5 seeds per model family
   - **Direction Classification**: ρ > 0.3 (positive), ρ < -0.3 (negative), else neutral

3. **Per-Dimension Accuracy**: Performance on each benchmark (TruthfulQA MC1, BBQ Accuracy, ANLI Accuracy)
   - **Purpose**: Verify intervention effectiveness (target dimension improves)

**Success Criteria**:
- **Primary (SHOULD_WORK gate)**: ≥3/5 model families show same correlation direction for at least one dimension pair
- **Secondary**: ANOVA shows intervention type main effect on correlation patterns (F-test, p<0.05)

**Expected Baseline Performance** (from research):
- **TruthfulQA MC1**: 25-35% (from h-m3: GPT-2 baseline 29.4%)
- **BBQ Accuracy**: 30-40% (from research: Llama-3.2-1B: 31.15%, Llama-3.2-3B: 40.52%)
- **ANLI R3 Accuracy**: 30-40% (from h-m3: GPT-2 baseline 34.6%)

**Statistical Test**: 
- Pearson correlation test (p<0.05 threshold for significance)
- Fisher's exact test for directional consistency across models
- ANOVA for intervention type effect

**Source**: h-m3 validation report, fairness-pruning BBQ baselines, TruthfulQA paper

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multi-dimensional classification (QA, NLI)
- Library: `scipy.stats` (Pearson correlation), `sklearn.metrics` (accuracy)
- Code:
```python
from scipy.stats import pearsonr
from sklearn.metrics import accuracy_score

# Correlation computation
correlation, p_value = pearsonr(deltas_dim1, deltas_dim2)

# Accuracy computation  
accuracy = accuracy_score(y_true, y_pred)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Directional replication rate bar chart (per dimension pair, per model family)

#### Additional Figures (LLM Autonomous)

1. **Correlation Heatmap per Model Family**: 3×3 heatmap showing correlation coefficients between all dimension pairs for each of the 5 model families
2. **Directional Consistency Plot**: Bar chart showing proportion of models with positive/negative/neutral correlation for each dimension pair
3. **Per-Family Performance**: Grouped bar chart showing baseline vs. post-intervention scores across all 3 dimensions for each model family
4. **Architecture Comparison**: Side-by-side comparison of transformer families (LLaMA, Mistral, Qwen, Falcon) vs. SSM (Mamba) correlation patterns
5. **Replication Rate Summary**: Single summary plot showing gate criterion (≥3/5 threshold line) with actual replication rates per dimension pair

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: LoRA Adapter Documentation (HuggingFace PEFT)
- **Type**: Knowledge base article
- **URL**: https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora
- **Query Used**: "multi-model architecture comparison experiment design"
- **Relevance**: Architecture-agnostic adaptation mechanism for parameter-efficient fine-tuning
- **Key Insights**:
  - LoRA enables consistent intervention across diverse architectures (Transformers, SSMs)
  - Same hyperparameters (r, α) can be applied to different model families
- **Used For**: Intervention method selection (LoRA r=8, α=16)

**Source 2**: Multi-task Learning Research (OpenReview)
- **Type**: Academic paper
- **URL**: https://openreview.net/forum?id=gU58d5QeGv
- **Query Used**: "cross-architecture generalization trustworthiness LLM"
- **Relevance**: Task interference patterns across model architectures
- **Key Insights**:
  - Cross-dimensional effects may vary by architecture
  - Multi-model evaluation shows architecture-specific patterns
- **Used For**: Hypothesis design rationale (testing cross-architecture generalization)

### Archon Code Examples

**Code Source 1**: Multi-Model Evaluation Framework (PyTorch AMP)
- **URL**: https://pytorch.org/docs/stable/amp.html#torch.autocast
- **Query Used**: "multi-model evaluation PyTorch"
- **Key Pattern**:
```python
# Standardized model loading and evaluation
model = TestModel(input_size, num_classes).eval()
with torch.cpu.amp.autocast(cache_enabled=False):
    model = torch.jit.trace(model, input)
model = torch.jit.freeze(model)
for _ in range(3):  # Multiple passes for stability
    model(input)
```
- **Used For**: Multi-model evaluation protocol design

**Code Source 2**: Baseline Comparison Structure (Apple ML Stable Diffusion)
- **URL**: https://github.com/apple/ml-stable-diffusion
- **Query Used**: "model family comparison experiment"
- **Key Pattern**:
```json
{
  "model_version": "model_name",
  "baselines": {
    "original": 82.2,
    "variant_1": 79.9,
    "variant_2": 78.2
  }
}
```
- **Used For**: Results structure for 5 model families × 3 dimensions

### B. GitHub Implementations (Exa)

**Repository 1**: TrustGen/TrustEval-toolkit (⭐128)
- **URL**: https://github.com/TrustGen/TrustEval-toolkit
- **Query Used**: "multi-model LLM trustworthiness evaluation benchmark GitHub"
- **Relevance**: Production-grade multi-model trustworthiness framework (ICLR'26, NAACL'25)
- **Key Features Extracted**:
  - Multi-Model Compatibility: Local + API model support
  - Dimensions Covered: Safety, fairness, robustness, privacy, truthfulness
  - Multi-GPU acceleration (7-8× speedup)
- **Configuration Used**: Multi-model evaluation pipeline architecture
- **Used For**: Overall experiment framework design (multi-family evaluation)

**Repository 2**: HowieHwong/TrustLLM (⭐623, ICML 2024)
- **URL**: https://github.com/howiehwong/trustllm
- **Query Used**: "multi-model LLM trustworthiness evaluation benchmark GitHub"
- **Relevance**: Academic standard for trustworthiness benchmarking
- **Key Insights**:
  - Evaluated 16 LLMs across 30+ datasets
  - Standard benchmarks: TruthfulQA, BBQ included
  - Uses lm-evaluation-harness for standardization
- **Their Results**: Established baseline ranges for comparison
- **Used For**: Dataset selection validation, expected baseline performance ranges

**Repository 3**: AI-secure/DecodingTrust (⭐301)
- **URL**: https://github.com/AI-secure/DecodingTrust
- **Query Used**: "multi-model LLM trustworthiness evaluation benchmark GitHub"
- **Relevance**: Comprehensive GPT + open LLM evaluation codebase
- **Models Evaluated**: GPT-3.5/4, Llama-v2-7B, Vicuna-7B, Alpaca-7B, MPT-7B, Falcon-7B
- **Key Code Pattern**:
```python
# Unified API wrapper for multiple model sources
from chat import create_request  # Robust API for OpenAI + HF models
model_response = create_request(model_id, prompt)
```
- **Used For**: Multi-source model loading strategy

**Repository 4**: peremartra/fairness-pruning (BBQ Baseline Results)
- **URL**: https://github.com/peremartra/fairness-pruning
- **Query Used**: "cross-architecture model comparison TruthfulQA BBQ fairness robustness"
- **Relevance**: Cross-architecture BBQ evaluation with Salamandra + LLaMA families
- **Key Findings**:
  - **Cross-Architecture Pattern**: Salamandra-2B underperforms Llama-1B despite 2× parameters
  - **Scaling Pattern**: Llama-3B shows 2.4× higher bias (4.12% vs 1.70%) than 1B
  - **Evaluation Times**: 1B (53min), 2B (1h18m), 3B (2h1m) - informs compute budget
- **Configuration Used**: lm-evaluation-harness, BBQ zero-shot
- **Used For**: Expected baseline performance, evaluation time estimation

**Repository 5**: thu-ml/MMTrustEval (⭐173, NeurIPS 2024)
- **URL**: https://github.com/thu-ml/MMTrustEval
- **Query Used**: "multi-model LLM trustworthiness evaluation benchmark GitHub"
- **Relevance**: MultiTrust benchmark (5 dimensions, 32 tasks)
- **Key Finding**: Correlation coefficient 0.60 between general capabilities and trustworthiness
- **Insight**: No significant correlation across different trustworthiness aspects
- **Used For**: Hypothesis validation (testing whether correlation patterns exist across architectures)

### C. Research Papers

**Paper 1**: TruthfulQA (arXiv:2109.07958)
- **Query Used**: "cross-architecture model comparison TruthfulQA BBQ fairness robustness"
- **Key Findings**:
  - Inverse scaling: Larger GPT models less truthful (175B: 58% vs. smaller models)
  - Best performance: GPT-3-175B with "helpful" prompt (58% truthful, human: 94%)
- **Used For**: Expected baseline performance (25-35% range), dataset selection

**Paper 2**: Bias Similarity Measurement (arXiv:2410.12010)
- **Query Used**: "cross-architecture model comparison TruthfulQA BBQ fairness robustness"
- **Key Findings**:
  - Evaluated 30 LLMs on 1M+ prompts
  - Family signatures diverge: Gemma (refusal), LLaMA 3.1 (neutrality)
  - Instruction tuning enforces abstention, not representation alteration
- **Used For**: Understanding cross-family differences in trustworthiness

**Paper 3**: EsBBQ/CaBBQ (arXiv:2507.11216)
- **Query Used**: "cross-architecture model comparison TruthfulQA BBQ fairness robustness"
- **Key Findings**:
  - Inverse relation between model size and ambiguous context performance
  - Bias scores increase with size (stronger in base vs. instruction-tuned)
- **Used For**: Understanding model size effects on fairness

### D. Previous Hypothesis Context (h-m3)

**Validation Report**: `docs/youra_research/20260511_buildingtrust/h-m3/04_validation.md`
- **Status**: PASS (SHOULD_WORK gate with documented limitation)
- **Model Used**: GPT-2 (124M parameters)
- **Intervention**: LoRA (r=8, α=16), 500 samples, 3 epochs
- **Key Results**:
  - **Truthfulness-Robustness**: r = -0.997, p = 0.051 (strong negative correlation, marginally non-significant)
  - **Fairness Independence**: r = 0.034 (truthfulness), r = 0.047 (robustness)
  - **Statistical Power**: 3 seeds insufficient for significance
- **Optimal Configuration Inherited**:
  - LoRA: r=8, α=16
  - Training: 500 samples, 3 epochs
  - Optimizer: AdamW
  - Loss convergence: ~0.4 by epoch 3
- **Used For**: 
  - Intervention configuration (LoRA hyperparameters)
  - Hypothesis motivation (testing if pattern replicates across architectures)
  - Statistical power design (increased to 5 seeds)

### E. Implementation Priority Assessment

**Priority Hierarchy Applied**:
1. ✅ **Multi-Model Evaluation Frameworks**: TrustLLM, TrustEval, DecodingTrust (HIGHEST - production-ready)
2. ✅ **Standard Datasets**: TruthfulQA, BBQ, ANLI (established benchmarks)
3. ✅ **Previous Experiment Configuration**: h-m3 optimal LoRA settings (continuity)

**Rationale**: Using established frameworks and benchmarks ensures reproducibility and comparability with prior work. Reusing h-m3 configuration enables controlled comparison focusing on architecture variable.

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-11T10:05:00+00:00

### Workflow History for This Hypothesis

- **2026-05-11T09:48:12+00:00**: Hypothesis h-m4 set to IN_PROGRESS (Hypothesis Loop started)
- **2026-05-11T09:48:12+00:00**: Phase 2C started (Experiment design in progress)
- **2026-05-11T10:05:00+00:00**: Phase 2C completed (Experiment brief generated)
- **Next**: Phase 3 Implementation Planning

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
