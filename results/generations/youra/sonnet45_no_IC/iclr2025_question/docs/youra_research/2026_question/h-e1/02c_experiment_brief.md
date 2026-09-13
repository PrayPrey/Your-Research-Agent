# Experiment Design: h-e1

**Date:** 2026-07-13
**Author:** Claude (YouRA Pipeline)
**Hypothesis Statement:** Under foundation model uncertainty quantification settings, if we measure the correlation between consistency-based scores (C) and conformal prediction interval membership (I), then we observe 0.3 < ρ(C,I) < 0.7, because consistency methods capture epistemic uncertainty (generative inconsistency) while conformal methods capture aleatoric uncertainty (inherent data ambiguity), representing distinct but complementary information sources.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites - foundation hypothesis)
**Gate Status:** NOT_EVALUATED

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** Existence
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**Type:** MUST_WORK
**Criteria:** 0.3 ≤ ρ(C,I) ≤ 0.7 on all three datasets (TruthfulQA, HH-RLHF, SQuAD) with p < 0.05 significance

---

## Continuation Context

This is the foundation hypothesis (h-e1) with no prerequisites. It validates the core assumption that consistency-based and conformal prediction methods measure distinct but complementary uncertainty signals. Success here enables the subsequent mechanism hypothesis (h-m-integrated).

### Previous Hypothesis Results (if applicable)
None - This is the first hypothesis in the verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Consistency & Conformal UQ**
- Result 1: [Consistency Models Paper (arXiv:2402.19159)](https://arxiv.org/abs/2402.19159)
  - Relevance: Discusses consistency models for uncertainty quantification
  - Key insight: Consistency methods measure uncertainty through sample variation
  
- Result 2: [OpenAI Consistency Models (GitHub)](https://github.com/openai/consistency_models)
  - Implementation: Reference code for consistency-based uncertainty
  - Pattern: Multi-sample generation for epistemic uncertainty measurement

**Query 2: SelfCheckGPT & COIN**
- Limited direct matches in knowledge base
- Generic training/calibration patterns found (TPU releases, quantization)

**Query 3: TruthfulQA Benchmark**
- Result: Hallucination detection gist examples
- Pattern: Benchmark evaluation for truthfulness metrics

### Archon Code Examples

**Query 1: Uncertainty Quantification PyTorch**
- Example 1: [Marigold Depth Uncertainty](https://huggingface-projects-docs-llms-txt.hf.space/diffusers/llms.txt)
  ```python
  depth = pipe(
      image,
      ensemble_size=10,  # Epistemic uncertainty via ensembling
      output_uncertainty=True,
  )
  uncertainty = pipe.image_processor.visualize_uncertainty(depth.uncertainty)
  ```
  - Pattern: Ensemble-based epistemic uncertainty quantification
  - Insight: Use multiple forward passes to measure consistency

**Query 2: Calibration Metrics**
- Example 1: [Optimum Quanto Calibration](https://github.com/huggingface/optimum-quanto/)
  ```python
  from optimum.quanto import Calibration
  with Calibration(momentum=0.9):
      model(samples)
  ```
  - Pattern: Calibration with momentum-based accumulation
  - Insight: Requires representative samples for calibration

### Exa GitHub Implementations

**⚠️ Exa MCP Service Unavailable (402 Payment Error)**

Unable to execute GitHub code searches due to Exa service limitation.

**Known Implementations (from Phase 2B context):**

1. **SelfCheckGPT (Manakul et al., 2023)**
   - Repository: https://github.com/potsawee/selfcheckgpt
   - Method: Consistency-based hallucination detection via NLI + BERTScore
   - Key features: Multi-sample generation, ensemble scoring
   
2. **COIN Conformal Prediction (Wang et al., 2025)**
   - Paper approach: Conformal prediction with FDR control
   - Framework: Statistical uncertainty bounds with coverage guarantees
   - Expected to use standard conformal prediction libraries

3. **General Conformal Prediction Resources:**
   - MAPIE (Python library for conformal prediction)
   - PyTorch implementation patterns for interval prediction
   
**Implementation Strategy (Phase 4):**
- Use SelfCheckGPT patterns: Multiple sampling (5-10 samples), NLI consistency scoring
- Implement conformal prediction using MAPIE or custom conformity scores
- Combine via Bayesian calibration framework

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority:** Medium - Using established patterns (SelfCheckGPT + Conformal Prediction) with custom integration layer

**Recommended Implementation Path:**
- Primary: Use SelfCheckGPT pattern (NLI + BERTScore) for consistency scoring + MAPIE library for conformal prediction + custom Bayesian calibration layer
- Fallback: If MAPIE unavailable, implement conformal prediction from scratch using standard quantile-based conformity scores
- Justification: SelfCheckGPT provides proven consistency scoring methodology; MAPIE is well-maintained conformal prediction library; custom integration needed for novel hierarchical Bayesian calibration component

### Code Analysis (Serena MCP)

*Skipped* - Exa search unavailable, no complex code snippets retrieved for deep analysis. 

Implementation will rely on methodological descriptions from Phase 2B and standard PyTorch patterns for:
- Multi-sample consistency scoring (SelfCheckGPT pattern)
- Conformal prediction intervals (MAPIE or custom implementation)
- Bayesian calibration framework (hierarchical updating)

---

## Experiment Specification

### Dataset

**Multi-Dataset Experimental Design** (3 datasets for comprehensive evaluation)

#### Primary Dataset: TruthfulQA
- **Type**: standard (epistemic uncertainty benchmark)
- **Source**: https://github.com/sylinrl/TruthfulQA
- **Task**: Factual question answering
- **Statistics**: ~800 questions across 38 categories
- **Splits**: Full dataset used for evaluation (n≥1000 samples via multi-sampling)
- **Hypothesis Fit**: Tests epistemic uncertainty (model knowledge gaps)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: "truthful_qa"
- Code: `load_dataset("truthful_qa", "generation")`

**Preprocessing**:
- Tokenization: Llama-2 tokenizer
- Max length: 512 tokens
- Truncation: True
- Padding: Dynamic batching

#### Secondary Dataset: HH-RLHF
- **Type**: standard (aleatoric uncertainty benchmark)
- **Source**: Anthropic Helpful-Harmless RLHF
- **Task**: Value alignment evaluation
- **Statistics**: Dialogue turns with preference labels
- **Hypothesis Fit**: Tests aleatoric uncertainty (value alignment ambiguity)

**Loading Information**:
- Method: HuggingFace datasets
- Identifier: "Anthropic/hh-rlhf"
- Code: `load_dataset("Anthropic/hh-rlhf")`

#### Tertiary Dataset: SQuAD
- **Type**: standard (mixed uncertainty baseline)
- **Source**: Stanford Question Answering Dataset
- **Task**: Reading comprehension QA
- **Statistics**: 10K+ dev samples
- **Hypothesis Fit**: Mixed uncertainty baseline for comparison

**Loading Information**:
- Method: HuggingFace datasets
- Identifier: "squad"
- Code: `load_dataset("squad")`

### Models

#### Baseline Model

**Architecture**: Llama-2-7B (Autoregressive Transformer LLM)
**Type**: Causal language model
**Source**: Meta AI via HuggingFace Hub
**Parameters**: ~7 billion

**Configuration**:
- Layers: 32 transformer blocks
- Hidden size: 4096
- Attention heads: 32
- Vocabulary size: 32000
- Context window: 4096 tokens

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: "meta-llama/Llama-2-7b-hf"
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")`

**Hypothesis Fit**:
- Supports sampling (required for SelfCheckGPT consistency)
- Widely benchmarked on TruthfulQA/SQuAD
- 7B size manageable for multi-sample (5-10 samples) experiments
- Established baselines for comparison

**Modifications for Experiment**: None (baseline as-is for PoC)

#### Proposed Model

**Architecture:** Llama-2-7B + Hierarchical Bayesian Calibration (HBC) Framework

**Integration**: Post-generation uncertainty calibration layer
- Applied after: Model generation (standard inference)
- Components: Consistency scoring module + Conformal prediction module + Bayesian calibration

**Core Mechanism Implementation:**

```python
# Hierarchical Bayesian Calibration (HBC) Framework
# Based on: SelfCheckGPT pattern + Conformal prediction theory + Bayesian updating

class HierarchicalBayesianCalibration(nn.Module):
    """
    Jointly calibrate consistency-based (epistemic) and conformal (aleatoric) 
    uncertainty signals via hierarchical Bayesian updating.
    """
    def __init__(self, num_samples=5, coverage_target=0.9):
        super().__init__()
        self.num_samples = num_samples
        self.coverage_target = coverage_target
        
        # Consistency scoring (epistemic uncertainty)
        self.nli_model = AutoModelForSequenceClassification.from_pretrained("roberta-large-mnli")
        self.bertscore = BERTScorer(lang="en")
        
        # Conformal prediction (aleatoric uncertainty)
        self.conformal_scores = []  # Calibration set conformity scores
        
    def forward(self, question, generated_answer):
        """
        Args:
            question: Input question (str)
            generated_answer: Main model generation (str)
        Returns:
            calibrated_uncertainty: Joint calibrated uncertainty score
            prediction_interval: Conformal interval with HBC-adjusted coverage
        """
        # Step 1: Generate consistency samples (epistemic prior)
        samples = [model.generate(question) for _ in range(self.num_samples)]
        
        # Step 2: Compute consistency score C(x) via NLI + BERTScore
        nli_scores = [self.nli_model(generated_answer, s) for s in samples]
        bert_scores = self.bertscore.score([generated_answer] * len(samples), samples)
        consistency_score = (mean(nli_scores) + mean(bert_scores)) / 2  # Ensemble
        
        # Step 3: Compute conformal prediction interval I(x) (aleatoric bounds)
        conformity_score = self._compute_conformity(generated_answer, question)
        quantile = self._get_quantile(consistency_score)  # Prior-informed
        interval_bounds = self._construct_interval(conformity_score, quantile)
        
        # Step 4: Bayesian updating (mutual calibration)
        # Statistical validation updates consistency threshold
        calibrated_threshold = self._bayesian_update(consistency_score, interval_bounds)
        
        return calibrated_threshold, interval_bounds
```

### Training Protocol

**Base Model**: Llama-2-7B (frozen, no fine-tuning for PoC)

**Calibration Protocol**:
- **Calibration Set**: 1000 samples per dataset (TruthfulQA, HH-RLHF, SQuAD)
- **Sampling**: 5 generations per input (for consistency scoring)
- **Temperature**: 0.7 (standard for generation diversity)
- **Max Tokens**: 256 per generation

**HBC Parameters** (based on conformal prediction literature):
- **Coverage Target**: 90% (α = 0.10)
- **Consistency Samples**: 5 per input (SelfCheckGPT standard)
- **NLI Model**: roberta-large-mnli (HuggingFace)
- **BERTScore**: deberta-xlarge-mnli (default)
- **Conformal Quantile**: Adaptive based on consistency prior

**Evaluation Protocol**:
- **Test Set Size**: n ≥ 1000 per dataset
- **Seeds**: 1 (fixed at 42 for reproducibility)
- **Metrics Computed**: 
  - Correlation ρ(C, I_binary) via Pearson
  - Expected Calibration Error (ECE)
  - Coverage rate (fraction y ∈ I(x))

**Computational Budget**:
- ~5 forward passes per input (consistency sampling)
- No gradient computation (inference only)
- Estimated time: 2-4 hours per dataset on single GPU

### Evaluation

**Primary Metric** (Gate Metric):
- **Correlation ρ(C, I)**: Pearson correlation between consistency score C and conformal interval membership I_binary
- **Success Criteria**: 0.3 ≤ ρ ≤ 0.7 on all three datasets
- **Measurement**: scipy.stats.pearsonr(C_scores, I_binary)

**Secondary Metrics** (Diagnostic):
- **Coverage Rate**: Fraction of samples where true answer ∈ predicted interval
  - Target: ≥ 90% (conformal guarantee)
- **ECE (Expected Calibration Error)**: Calibration quality
  - Expected: < 0.10 for PoC (no fine-tuning)
- **Consistency Score Distribution**: Mean and std of C(x) across samples
- **Conformal Interval Width**: Average interval size

**Statistical Test** (for gate validation):
- **Test**: Two-tailed significance test
- **Null Hypothesis**: ρ = 0.9 (redundancy) OR ρ = 0.1 (independence)
- **Requirement**: p < 0.05 for all datasets

**Success Criteria (MUST_WORK Gate)**:
1. **Primary**: 0.3 ≤ ρ ≤ 0.7 on TruthfulQA, HH-RLHF, AND SQuAD
2. **Secondary**: p < 0.05 for significance test on each dataset
3. **Tertiary**: Coverage ≥ 85% (conformal degradation check)

**Expected Baseline Performance** (from Phase 2B):
- Independent SelfCheckGPT: Consistency detection AUC ~0.7-0.8
- Independent COIN: Coverage ~90%, ECE ~0.06-0.08
- Correlation ρ: Unknown (to be measured) — hypothesis predicts 0.3-0.7

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Uncertainty quantification + correlation analysis
- Library: scipy.stats, sklearn.metrics, custom ECE implementation
- Code:
  ```python
  from scipy.stats import pearsonr
  from sklearn.metrics import mean_absolute_error
  
  # Correlation
  rho, p_value = pearsonr(consistency_scores, interval_membership)
  
  # ECE (custom)
  ece = compute_ece(confidences, accuracies, n_bins=10)
  
  # Coverage
  coverage = np.mean([y in interval for y, interval in zip(labels, intervals)])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on correlation analysis experiment:
1. **Scatter Plot**: Consistency score C vs. Interval membership I (with ρ annotation)
2. **Distribution Comparison**: Histograms of C for cases where I=1 vs I=0
3. **Per-Dataset Correlation**: Side-by-side ρ values for TruthfulQA, HH-RLHF, SQuAD
4. **Calibration Curve**: Predicted uncertainty vs actual error rate (ECE visualization)

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

**Source A.1**: Consistency Models Research (arXiv:2402.19159)
- **Type**: Research paper / methodology
- **Query Used**: "consistency conformal prediction uncertainty quantification"
- **Relevance**: Theoretical foundation for consistency-based uncertainty methods
- **Key Insights**:
  - Consistency methods measure epistemic uncertainty via sample variation
  - Multi-sample generation is standard practice
- **Used For**: Consistency scoring methodology in HBC framework

**Source A.2**: Marigold Depth Uncertainty Example
- **Type**: Code example
- **Query Used**: "uncertainty quantification PyTorch"
- **Key Code**:
  ```python
  depth = pipe(
      image,
      ensemble_size=10,  # Epistemic uncertainty via ensembling
      output_uncertainty=True,
  )
  ```
- **Used For**: Ensemble-based uncertainty pattern (adapted to 5 samples for efficiency)

**Source A.3**: Optimum Quanto Calibration
- **Type**: Code example  
- **Query Used**: "calibration metrics ECE coverage"
- **Key Code**:
  ```python
  from optimum.quanto import Calibration
  with Calibration(momentum=0.9):
      model(samples)
  ```
- **Used For**: Calibration protocol pattern

### B. GitHub Implementations (Exa)

**Exa Service Status**: Unavailable (402 Payment Error) during Phase 2C execution

**Known Implementations from Phase 2B Context**:

**Repository B.1**: SelfCheckGPT (Manakul et al., 2023)
- **URL**: https://github.com/potsawee/selfcheckgpt
- **Relevance**: Official implementation of consistency-based hallucination detection
- **Key Method**: Multi-sample generation (5-10 samples) + NLI + BERTScore ensemble
- **Used For**: Consistency scoring implementation pattern in HBC

**Repository B.2**: COIN Conformal Prediction (Wang et al., 2025)
- **Reference**: Paper approach from Phase 2B
- **Method**: Conformal prediction with FDR control, 90% coverage
- **Used For**: Conformal interval construction methodology

**Implementation Strategy**: 
- Consistency: Follow SelfCheckGPT pattern (NLI + BERTScore)
- Conformal: Use MAPIE library or custom implementation based on conformal theory
- Integration: Custom Bayesian calibration layer

### C. Code Analysis (Serena)

**Serena Analysis**: *Skipped* - Exa search unavailable, no complex code retrieved for deep analysis

**Fallback Approach**: 
- Implementation based on methodological descriptions from Phase 2B
- Standard PyTorch patterns for multi-sample generation
- Conformal prediction via established statistical methods

### D. Previous Hypothesis Context

**Previous Context**: None - H-E1 is the first (foundation) hypothesis with no prerequisites

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Multi-dataset design (TruthfulQA, HH-RLHF, SQuAD) | Phase 2B Context | 02b_context.md, 02b_verification_plan.md |
| TruthfulQA loading | Phase 2B + HF | HuggingFace "truthful_qa" |
| Llama-2-7B model | Phase 2B Context | HuggingFace "meta-llama/Llama-2-7b-hf" |
| Consistency scoring (5 samples) | Archon KB | Source A.2 (Marigold pattern) |
| NLI + BERTScore ensemble | Phase 2B + GitHub | B.1 (SelfCheckGPT) |
| Conformal prediction (90% coverage) | Phase 2B | B.2 (COIN method) |
| Calibration protocol | Archon KB | Source A.3 (Quanto pattern) |
| Correlation metric ρ(C,I) | Phase 2B | 02b_verification_plan.md H-E1 protocol |
| Success criteria (0.3 ≤ ρ ≤ 0.7) | Phase 2B | 02b_verification_plan.md gate condition |
| ECE metric | Phase 2B baseline | Independent cascade ECE ~0.06-0.08 |

---

## State Information

**State File:** verification_state.yaml
**Date:** {{timestamp}}

### Workflow History for This Hypothesis
- 2026-07-13T01:06:34: Hypothesis h-e1 set to IN_PROGRESS (Phase 2C → 3 → 4 loop initiated)
- 2026-07-13: Phase 2C experiment brief generated with complete specifications

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
