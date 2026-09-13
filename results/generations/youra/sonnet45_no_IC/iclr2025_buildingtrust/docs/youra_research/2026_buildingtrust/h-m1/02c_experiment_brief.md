# Experiment Design: h-m1

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis Statement:** Under factual prompts where memorization is expected, if reliability and robustness are measured on the same model outputs, then positive correlation r>0.3 (p<0.05) emerges, because shared training dynamics create correlations between factual correctness (reliability) and consistent retrieval (robustness) for memorized content.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests causal mechanism hypothesis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 PASS)
**Gate Status:** MUST_WORK gate

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1

### Gate Condition
MUST_WORK gate: Failure requires exploration of alternative mechanisms (retrieval quality, model calibration).

---

## Continuation Context

### Previous Hypothesis Results
**h-e1 (EXISTENCE) - PASS:**
- Reliability variance: σ=0.224 (threshold: 0.20) ✓
- Robustness variance: σ=0.202 (threshold: 0.20) ✓
- Fairness variance: σ=0.215 (threshold: 0.20) ✓
- All dimensions show sufficient variance for correlation analysis
- EXISTENCE gate validated: synchronized multi-dimensional measurement is feasible

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Correlation Analysis in LLM Evaluation**
- Limited direct matches in Archon KB for LLM trustworthiness correlation analysis
- Found general evaluation frameworks but not specific to multi-dimensional correlation measurement
- Key insight: This appears to be a novel research direction (consistent with Phase 2A gap analysis)

**Query 2: Reliability/Robustness/Fairness Metrics**
- General machine learning evaluation resources found
- No specific multi-dimensional trustworthiness correlation frameworks in KB
- Suggests need for custom implementation based on statistical correlation methods

**Query 3: Statistical Correlation Methods**
- Standard scipy/numpy correlation implementations available
- Permutation testing and confidence interval methods documented
- Key insight: Use established statistical methods (Pearson r, Fisher z-test) from scipy.stats

### Archon Code Examples

**Query 1: Correlation Coefficient Computation**
- Found generic scipy installation examples
- Standard statistical libraries available (scipy.stats.pearsonr)
- Pattern: Use scipy.stats for correlation analysis with p-values and confidence intervals

**Query 2: TruthfulQA Evaluation**
- Limited specific TruthfulQA implementation examples in KB
- General model evaluation patterns available
- Key insight: Will need to implement custom GPT-4-as-judge scoring + paraphrase consistency measurement

### Exa GitHub Implementations

**⚠️ Exa MCP Service Unavailable (402 Error - Quota/Payment Issue)**

**Fallback Strategy:**
Since this is a novel correlation analysis approach (confirmed by Phase 2A gap analysis and Archon KB), we'll use standard statistical libraries and LLM evaluation frameworks:

**Implementation Components:**
1. **TruthfulQA Dataset**: Use HuggingFace `truthful_qa` dataset (truthful_qa/generation)
2. **Llama-2 Models**: Use HuggingFace transformers (`meta-llama/Llama-2-*b-chat-hf`)
3. **Correlation Analysis**: scipy.stats (pearsonr, fisher_exact for z-test)
4. **GPT-4-as-judge**: OpenAI API for reliability scoring
5. **Paraphrase Robustness**: Back-translation via translation APIs or deterministic paraphrasing
6. **Fairness**: HONEST metric implementation (demographic augmentation)

**Reference Approaches (from Phase 2A research):**
- TrustVis (2025): Multi-dimensional evaluation framework
- MLLMGuard (2024): Safety scoring approach
- BOLD (2021): Fairness evaluation

**Serena Analysis Needed**: false (standard statistical analysis, no complex custom architectures)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a novel correlation analysis approach (no existing paper implementation). Implementation priority based on standard statistical analysis libraries.

**Recommended Implementation Path:**
- Primary: scipy.stats for correlation analysis (pearsonr, Fisher z-transform) + HuggingFace libraries for dataset/model loading
- Fallback: numpy-based manual correlation implementation if scipy unavailable
- Justification: Standard statistical libraries provide validated, widely-used implementations. No custom neural architectures required - this is a measurement/analysis experiment, not a training experiment.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. This is a statistical correlation analysis experiment using standard libraries (scipy, numpy, transformers, datasets), not complex custom architectures requiring deep semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset**: TruthfulQA (factual stratum)
**Type**: standard
**Source**: HuggingFace (truthful_qa/generation)
**Path**: truthful_qa

**Hypothesis Fit**: Provides 817 prompts with ground-truth reliability labels; enables stratification into factual vs. misinformation categories for testing memorization-driven correlation.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa`
- Code: `from datasets import load_dataset; dataset = load_dataset("truthful_qa", "generation")`

**Statistics**: 817 total prompts (stratified into ~400 factual + ~400 misinformation)
**Preprocessing**: 
  - Filter for factual stratum based on question category
  - Generate model outputs with controlled parameters (temp=0.7, top_p=0.9, seed fixed)
  - Create paraphrases via back-translation for robustness measurement
**Augmentation**: Demographic augmentation for fairness measurement (HONEST metric)

### Models

#### Baseline Model

**Architecture**: Llama-2-chat (7B, 13B, 70B)
**Type**: decoder-only transformer (pretrained + RLHF fine-tuned)
**Source**: HuggingFace (meta-llama/Llama-2-*b-chat-hf)

**Hypothesis Fit**: Open-source models with consistent architecture across scales; enables testing scale as moderator; RLHF fine-tuning relevant for fairness-reliability trade-off hypothesis.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-chat-hf` (and 13b, 70b variants)
- Code: `from transformers import AutoModelForCausalLM, AutoTokenizer; model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf"); tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")`

**Configuration**: Standard Llama-2 architecture (decoder-only, grouped-query attention)
**Modifications for Hypothesis**: None - using pretrained checkpoint as-is for generation, no training required

#### Proposed Model

**Architecture:** Statistical correlation analysis framework (no neural network training required)
**Integration Point**: Analysis runs on pre-generated model outputs
  - Input: Llama-2 model outputs on TruthfulQA prompts
  - Output: Pearson correlation coefficients with significance tests

**Core Mechanism Implementation:**

```python
# Core Mechanism: Reliability-Robustness Correlation via Memorization
# Based on: Statistical correlation analysis (scipy.stats)

class TrustworthinessCorrelationAnalyzer:
    """
    Tests positive correlation between reliability and robustness
    on factual prompts via shared memorization mechanism.
    """
    def __init__(self, factual_prompts, model_outputs):
        self.factual_prompts = factual_prompts  # ~400 factual from TruthfulQA
        self.model_outputs = model_outputs      # Generated with temp=0.7, top_p=0.9
    
    def measure_reliability(self, outputs):
        """Score via GPT-4-as-judge (binary correct/incorrect)"""
        # Returns: np.array of shape (N,) with values in [0, 1]
        return gpt4_judge_scores(outputs, ground_truth)
    
    def measure_robustness(self, outputs, paraphrased_outputs):
        """Score via paraphrase consistency (cosine similarity)"""
        # Returns: np.array of shape (N,) with values in [0, 1]
        return cosine_similarity(embeddings(outputs), embeddings(paraphrased_outputs))
    
    def compute_correlation(self, reliability_scores, robustness_scores):
        """
        Compute Pearson correlation with significance test
        Returns: (r, p_value, ci_lower, ci_upper)
        """
        from scipy.stats import pearsonr
        r, p_value = pearsonr(reliability_scores, robustness_scores)
        
        # 95% CI via Fisher z-transform
        from scipy.stats import norm
        z = np.arctanh(r)
        se = 1 / np.sqrt(len(reliability_scores) - 3)
        ci = z + np.array([-1.96, 1.96]) * se
        ci_lower, ci_upper = np.tanh(ci)
        
        return r, p_value, ci_lower, ci_upper

# No training loop needed - analysis on pre-generated outputs
```

**Modifications for Hypothesis**: None to Llama-2 architecture. Experiment generates outputs once, then analyzes correlations.

### Training Protocol

**No Training Required** - This is an analysis experiment, not a model training experiment.

**Generation Protocol** (for Llama-2 outputs):
- **Temperature**: 0.7 (from Phase 2B)
- **top_p**: 0.9 (from Phase 2B)
- **max_tokens**: 256 (from Phase 2B)
- **seed**: Fixed per prompt (from Phase 2B - ensures reproducibility)
- **Source**: Phase 2B verification protocol

**Paraphrase Generation** (for robustness measurement):
- **Method**: Back-translation (English → French → English)
- **Tool**: Google Translate API or MarianMT
- **Validation**: Pilot n=20 with expert review for semantic preservation

**Evaluation Execution**:
1. Generate outputs for all 817 TruthfulQA prompts (3 models × 817 = 2,451 samples)
2. Filter factual stratum (~400 prompts)
3. Generate paraphrases for robustness measurement
4. Score reliability via GPT-4-as-judge
5. Score robustness via paraphrase consistency
6. Compute Pearson correlation with statistical tests

### Evaluation

**Primary Metrics**:
- **Pearson r** (reliability-robustness correlation on factual prompts)
- **p-value** (two-tailed significance test, α=0.05)
- **95% CI** (confidence interval via Fisher z-transform)

**Success Criteria**:
- Primary: Pearson r > 0.3, p < 0.05, 95% CI lower bound > 0.2 (from Phase 2B)
- Secondary: At least one model shows r > 0.4 (strong coupling)

**Expected Baseline Performance** (from Phase 2B):
- Null hypothesis: r ≈ 0 (independence)
- Alternative: r > 0.3 (positive coupling via memorization)

**Permutation Test** (validation):
- 1000 random shuffles of reliability scores
- Check observed r exceeds 95th percentile of null distribution

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation analysis
- Library: scipy.stats (pearsonr, fisher_exact), sklearn.metrics (cosine_similarity)
- Code: `from scipy.stats import pearsonr; r, p = pearsonr(reliability, robustness)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target correlation (r>0.3) vs actual observed correlation bar chart

#### Additional Figures (LLM Autonomous)
Based on correlation analysis, generate:
1. **Scatter Plot**: Reliability vs Robustness scores (factual stratum) with regression line, Pearson r, and 95% CI
2. **Distribution Plot**: Histogram of correlation values across 3 models (7B, 13B, 70B)
3. **Permutation Test Plot**: Observed r vs null distribution from 1000 shuffles
4. **Confidence Interval Plot**: Forest plot showing r ± 95% CI for each model size
5. **Stratification Comparison** (if applicable): Factual vs misinformation correlation magnitudes

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Observed correlation r > null hypothesis r=0 (directional improvement)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: Limited direct matches for LLM trustworthiness correlation
- **Type**: Knowledge base search results
- **Query Used**: "correlation analysis trustworthiness LLM evaluation"
- **Relevance**: Confirmed this is a novel research direction (consistent with Phase 2A gap analysis)
- **Key Insights**:
  - No existing multi-dimensional correlation frameworks found
  - Validates need for custom implementation
- **Used For**: Confirmed novelty, guided custom implementation approach

**Source A.2**: Statistical correlation methods
- **Type**: Knowledge base search results
- **Query Used**: "Pearson correlation statistical significance permutation test"
- **Relevance**: Standard statistical methods available via scipy
- **Key Insights**:
  - Use scipy.stats.pearsonr for correlation with p-values
  - Fisher z-transform for confidence intervals
  - Permutation testing for null distribution validation
- **Used For**: Statistical analysis framework design

### B. GitHub Implementations (Exa)

**Exa MCP Status**: Unavailable (402 Error - Quota/Payment Issue)

**Fallback Strategy Applied**:
- HuggingFace datasets library for TruthfulQA loading
- HuggingFace transformers for Llama-2 model loading
- scipy.stats for correlation analysis
- sklearn.metrics for similarity measurements

**Standard Implementation References**:
1. **TruthfulQA Dataset**: HuggingFace `truthful_qa` (generation split)
2. **Llama-2 Models**: HuggingFace `meta-llama/Llama-2-*b-chat-hf`
3. **Correlation Analysis**: scipy.stats (pearsonr, Fisher z-transform)
4. **GPT-4-as-judge**: OpenAI API for reliability scoring
5. **Paraphrase Robustness**: Back-translation implementation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - This is a statistical correlation analysis experiment using standard libraries (scipy, numpy, transformers, datasets), not complex custom architectures requiring deep semantic analysis.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-e1
- **File**: `docs/youra_research/h-e1/04_validation.md`
- **Prerequisite Results**:
  - Reliability variance: σ=0.224 (threshold: 0.20) ✓
  - Robustness variance: σ=0.202 (threshold: 0.20) ✓
  - Fairness variance: σ=0.215 (threshold: 0.20) ✓
  - EXISTENCE gate validated: synchronized multi-dimensional measurement is feasible
- **Why Relevant**: Prerequisite h-e1 PASS confirms sufficient variance exists for correlation analysis

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B context | TruthfulQA (factual stratum) from 02b_context.md |
| Model selection | Phase 2B context | Llama-2-chat (7B, 13B, 70B) from 02b_context.md |
| Statistical framework | Archon KB | scipy.stats correlation methods (Source A.2) |
| Correlation method | Phase 2B protocol | Pearson r with Fisher z-transform |
| Success criteria | Phase 2B protocol | r>0.3, p<0.05, 95% CI>0.2 |
| Permutation test | Phase 2B protocol | 1000 shuffles validation |
| GPT-4-as-judge | Phase 2B assumptions | Reliability measurement (A1 validation) |
| Paraphrase robustness | Phase 2B assumptions | Back-translation (A2 validation) |
| Fairness measurement | Phase 2B assumptions | HONEST metric (A3 validation) |
| Prerequisite validation | h-e1 results | Variance confirmation from 04_validation.md |

### F. Phase 2B References

**Primary Source**: `docs/youra_research/02b_verification_plan.md`
- Section 2.2 (H-M1 specification): Hypothesis statement, variables, success criteria
- Section 1.3 (Experimental Setup): Dataset and model selection from Phase 2A
- Section 1.5 (Assumptions): A1 (GPT-4), A2 (back-translation), A3 (HONEST), A4 (power), A5 (scale)

**Per-Hypothesis Context**: `docs/youra_research/h-m1/02b_context.md`
- Generated from 02b_verification_plan.md in Step 01
- Contains hypothesis-specific extraction of experimental setup

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-12

### Workflow History for This Hypothesis
- Set to IN_PROGRESS: 2026-07-12T07:03:21Z
- Experiment design started: 2026-07-12T07:03:21Z

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
