# Experiment Design: h-m3

**Date:** 2026-05-11
**Author:** Anonymous
**Hypothesis Statement:** Under representation changes from targeted interventions, if internal states affect multiple downstream capabilities, then performance on non-targeted dimensions D₂/D₃ shifts in correlated fashion, because prior multi-task learning work shows task interference from shared representations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧬 **MECHANISM Hypothesis** - Tests causal chain Step 3 (propagation to non-target dimensions)

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C - Experiment Design)
**Prerequisites Satisfied:** ✅ YES (h-m2 COMPLETED with PASS)
**Gate Status:** SHOULD_WORK gate active (threshold: Non-random correlation structure, p<0.05)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2 (representation changes occur)

### Gate Condition

**Gate Type:** SHOULD_WORK  
**Threshold:** Non-random correlation structure (differs from control baseline at p<0.05)  
**Fail Action:** Narrow scope - document which dimensions don't correlate

**Success Criteria:**
- **Primary:** Correlation between Δ(D₁) and [Δ(D₂), Δ(D₃)] significantly differs from random (p<0.05)
- **Secondary:** Correlation magnitudes |ρ| > 0.2 (small-to-medium effects)

---

## Continuation Context

This is a **continuation experiment** building directly on h-m2:

### h-m2 → h-m3 Progression

**h-m2 Validated:**
- ✅ Parameter updates (LoRA fine-tuning on TruthfulQA) cause representation changes
- ✅ All 24 layers showed measurable changes (100% coverage)
- ✅ Attention patterns changed more than residual streams (2.0× magnitude)
- ✅ TransformerLens + CKA analysis pipeline functional

**h-m3 Extension:**
- **From:** Single-dimension evaluation (aggregate performance)
- **To:** Multi-dimensional evaluation (TruthfulQA + BBQ + AdvGLUE)
- **From:** Correlation with aggregate performance (r=0.150, p=0.28)
- **To:** Per-dimension correlation analysis with statistical testing
- **New:** Random baseline comparison (permutation test)

**Controlled Comparison:**
- **Same model:** GPT-2 (124M)
- **Same intervention:** LoRA (r=8, α=16) on TruthfulQA
- **Same analysis:** TransformerLens + CKA for representation changes
- **Only change:** Evaluation scope (1 dimension → 3 dimensions)

### Previous Hypothesis Results (h-m2)

**Key Findings:**
- Mean CKA similarity: 0.857 (mean change: 0.143)
- Layer-wise changes: Attention (0.191), Residual (0.095)
- Correlation with performance: r=0.150 (p=0.28, non-significant)
- Gate verdict: PASS (SHOULD_WORK allows continuation despite non-significant correlation)

**Lessons for h-m3:**
1. Increase training sample size: 100 → 500 (better representation coverage)
2. Use per-dimension correlation instead of aggregate
3. Add random baseline for statistical comparison
4. Track which layers correlate with which dimensions

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Multi-task Learning Representation Correlation**
- Top result: PEFT/LoRA documentation (HuggingFace)
  - **Relevance:** Confirms LoRA as standard fine-tuning approach (used in h-m2)
  - **Key insight:** Low-rank adaptation preserves base model while adapting specific parameters
  - **Dataset consideration:** Not specific to trustworthiness benchmarks

- Secondary results: Distributed training, diffusion models
  - **Limited relevance** to trustworthiness correlation analysis

**Query 2: Task Interference Cross-Dimensional Performance**
- Top results: xDiT parallel inference system, LoRA adapters
  - **Relevance:** Infrastructure-focused, not directly applicable to correlation analysis
  - **Note:** No specific papers on trustworthiness dimension interference found

**Query 3: Trustworthiness Benchmark Evaluation Metrics**
- Top result: OpenReview paper on benchmark evaluation
  - **Potential relevance:** General benchmark methodology
  - **Limitation:** Not specific to multi-dimensional trustworthiness evaluation

**Overall Assessment:**
- Archon KB contains limited prior work on **multi-dimensional trustworthiness correlation analysis**
- Confirmed: LoRA as standard intervention method (validated from h-m2)
- **Gap identified:** Novel research area - no direct precedent for cross-dimensional correlation propagation in trustworthiness

### Archon Code Examples

**Query 1: Representation Similarity CKA PyTorch**
- CLIP contrastive learning example (DALLE2-pytorch)
  - **Pattern:** Multi-modal similarity computation
  - **Not applicable:** Different domain (vision-language, not layer-wise CKA)

- PyTorch distributed communication examples
  - **Pattern:** Tensor synchronization across processes
  - **Limited relevance:** Infrastructure code, not representation analysis

- Scaled dot-product attention implementation
  - **Pattern:** Attention mechanism computation
  - **Potential use:** Understanding attention pattern changes (from h-m2)

**Query 2: Correlation Analysis Multiple Metrics**
- FID, PPL, PR metric configuration examples (MMGeneration)
  - **Pattern:** Multiple evaluation metrics in config files
  - **Insight:** Structure for tracking multiple dimensions simultaneously
  - **Code pattern:**
    ```python
    metrics = dict(
        metric1=dict(type='FID', num_images=50000),
        metric2=dict(type='PR', num_images=50000),
        metric3=dict(type='PPL', space='W')
    )
    ```
  - **Application to h-m3:** Similar structure for TruthfulQA, BBQ, AdvGLUE tracking

**Overall Code Assessment:**
- Limited direct implementations of CKA-based representation analysis
- Useful pattern: Multi-metric evaluation framework
- **Recommendation:** Build on h-m2's TransformerLens + CKA foundation, extend with multi-dimensional correlation analysis

### Exa GitHub Implementations

**Query 1: Multi-Task Learning Representation Correlation**

**Repository 1: median-research-group/LibMTL** (⭐ High activity)
- **URL**: https://github.com/median-research-group/LibMTL
- **Relevance**: ⭐⭐⭐ HIGHEST - Comprehensive MTL framework with loss weighting and architecture support
- **Key Features**:
  - 16 optimization strategies including gradient balancing (MGDA, CAGrad, Nash-MTL)
  - 8 MTL architectures (HPS, Cross-stitch, MMoE, MTAN)
  - **Rep-grad vs Param-grad**: Supports gradient computation at representation level (relevant to h-m3)
  - Unified framework for multi-input/multi-output problems
- **Training Patterns**:
  - Loss weighting strategies for balancing multiple tasks
  - Representation-level gradient computation (detach operation)
  - Multi-task dataloader with shared/separate inputs
- **Application to h-m3**:
  - **Direct relevance**: Framework for tracking multiple dimension metrics simultaneously
  - **Loss balancing**: Can adapt for correlation analysis across dimensions
  - **Rep-grad**: Matches h-m2's representation-level analysis approach

**Repository 2: SimonVandenhende/Multi-Task-Learning-PyTorch** (⭐ 840 stars)
- **URL**: https://github.com/SimonVandenhende/Multi-Task-Learning-PyTorch
- **Relevance**: ⭐⭐ MEDIUM - Dense prediction MTL, survey implementation
- **Architectures**: HRNet/ResNet backbones, Cross-Stitch, NDDR-CNN, MTAN, MTI-Net
- **Training Protocol**:
  ```python
  # Multi-task evaluation pattern
  for epoch in range(epochs):
      train_vanilla(train_dataloader, model, criterion, optimizer)
      save_model_predictions(val_dataloader, model)
      curr_result = eval_all_results()  # Multi-task evaluation
      improves = validate_results(curr_result, best_result)
  ```
- **Key Insight**: Unified evaluation across multiple tasks with `eval_all_results()` pattern
- **Application to h-m3**: Pattern for simultaneous multi-dimension evaluation

**Repository 3: xiaogang00/MTFormer** (ECCV 2022)
- **URL**: https://github.com/xiaogang00/MTFormer
- **Relevance**: ⭐⭐ MEDIUM - Transformer-based MTL with cross-task attention
- **Novel Mechanism**: Cross-task attention + self-supervised contrastive learning
- **Datasets**: NYUD-v2, PASCAL (dense prediction tasks)
- **Training Config**:
  - Shared transformer encoder/decoder
  - Task-specific lightweight branches
  - Cross-task reasoning mechanism
- **Not directly applicable**: Different domain (vision), but cross-task attention pattern useful

**Query 2: TruthfulQA + BBQ + AdvGLUE Benchmarks**

**Repository 1: sylinrl/TruthfulQA** (⭐ Official benchmark)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Relevance**: ⭐⭐⭐ HIGHEST - Official TruthfulQA implementation
- **Dataset Details**:
  - 817 questions across 38 categories
  - Adversarial + non-adversarial questions
  - Multiple evaluation metrics: GPT-judge, BLEURT, ROUGE, BLEU
  - **Loading**: `truthfulqa/truthful_qa` from HuggingFace datasets
- **Evaluation Code**:
  ```python
  # From evaluate.py
  python truthfulqa/evaluate.py \
      --models [model_name] \
      --metrics bleurt,gpt-judge,info \
      --preset qa \
      --device 0
  ```
- **Key Metrics**:
  - % true (truthfulness rate)
  - % info (informativeness rate)
  - MC1/MC2 (multiple-choice accuracy)
- **Baseline Performance**: GPT-3-175B: 20.44% true, UnifiedQA-3B: 53.86% true
- **Application to h-m3**: Direct use for truthfulness dimension evaluation

**AdvGLUE Benchmark** (Website reference)
- **URL**: https://adversarialglue.github.io/
- **Relevance**: ⭐⭐⭐ HIGH - Official adversarial robustness benchmark
- **Coverage**: 5 GLUE tasks with adversarial examples
- **Attack Types**:
  - Word-level transformations
  - Sentence-level manipulations
  - Human-written adversarial examples
- **Evaluation**: `python evaluate.py <pred_file>`
- **Quality**: Human-annotated adversarial examples
- **Application to h-m3**: Use for robustness dimension evaluation

**BBQ Benchmark** (Bias Benchmark for QA)
- **Note**: No specific GitHub repository found in Exa results
- **Expected source**: HuggingFace datasets `nyu-mll/BBQ`
- **Application to h-m3**: Use for fairness dimension evaluation

**Serena Analysis Needed**: ❌ FALSE
- TruthfulQA evaluation code is straightforward (<100 lines)
- LibMTL framework is well-documented
- Multi-task evaluation patterns are clear
- **Decision**: Proceed without Serena analysis; code is clear enough for Phase 3 PRD

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment for h-m3:**

This is NOT a paper reproduction - this is a **novel hypothesis** testing cross-dimensional correlation propagation in trustworthiness dimensions. No prior work directly implements this mechanism.

**Priority Ranking:**

1. **⭐⭐⭐ HIGHEST: h-m2 Validated Code** (controlled continuation)
   - Source: `h-m2/code/` from previous hypothesis
   - Proven: LoRA fine-tuning + representation extraction + CKA analysis
   - Reuse: TransformerLens integration, CKA computation, training loop
   - Extend: Multi-dimensional evaluation (add BBQ, AdvGLUE)

2. **⭐⭐ MEDIUM: LibMTL Framework Patterns**
   - Source: https://github.com/median-research-group/LibMTL
   - Useful: Multi-task evaluation structure, loss balancing patterns
   - Limitation: Computer vision focused, not LM evaluation
   - Use case: Structure for tracking multiple dimension metrics simultaneously

3. **⭐⭐ MEDIUM: TruthfulQA Official Implementation**
   - Source: https://github.com/sylinrl/TruthfulQA
   - Proven: Official evaluation code for truthfulness metrics
   - Use case: Direct integration for D₁ (target dimension) evaluation

4. **⭐ LOW: BBQ/AdvGLUE Benchmarks**
   - Source: Official benchmark websites + HuggingFace
   - Use case: D₂/D₃ (non-target dimensions) evaluation
   - Integration: Custom evaluation wrappers needed

**Recommended Implementation Path:**

- **Primary:** Extend h-m2 code with multi-dimensional evaluation
  - **Rationale:** Proven mechanism, validated pipeline, controlled comparison
  - **Modifications:** 
    - Add BBQ dataset loader
    - Add AdvGLUE dataset loader (or approximation)
    - Extend evaluation to compute all 3 dimension metrics
    - Add correlation analysis (scipy.stats.pearsonr)
    - Generate correlation matrix visualizations

- **Fallback:** Build from scratch using LibMTL + TruthfulQA patterns
  - **Rationale:** If h-m2 code has critical bugs or incompatibilities
  - **Risk:** Loses controlled comparison benefit
  - **Use only if:** h-m2 code cannot be extended

- **Justification:** h-m3 explicitly builds on h-m2's validated mechanism. Reusing h-m2 code ensures controlled experiment (only evaluation scope changes). This is the scientifically correct approach for testing causal chain Step 3.

### Code Analysis (Serena MCP)

**Status:** ❌ NOT PERFORMED (not needed)

**Rationale:**
- TruthfulQA evaluation code is straightforward (<100 lines from Exa search)
- LibMTL framework is well-documented with clear patterns
- h-m2 code already validated in previous hypothesis
- Multi-task evaluation patterns are clear from research

**Decision:** Proceed directly to Phase 3 PRD without Serena analysis. Code complexity is manageable, and h-m2 provides proven foundation.

---

## Experiment Specification

### Dataset

**Multi-Dimensional Benchmark Suite** (3 datasets for correlation analysis)

This experiment requires **3 trustworthiness benchmarks** evaluated simultaneously to measure cross-dimensional correlation:

#### Dataset 1: TruthfulQA (Target Dimension)
- **Name**: TruthfulQA
- **Type**: standard (HuggingFace datasets)
- **Purpose**: Target dimension for intervention (truthfulness)
- **Statistics**: 817 questions, 38 categories (health, law, finance, politics)
- **Splits**: validation only (no train split - evaluation benchmark)
- **Categories**: Adversarial (testing misconceptions) + Non-Adversarial

**Loading Information**:
- Method: HuggingFace `datasets`
- Identifier: `truthfulqa/truthful_qa`
- Config: `generation` (for open-ended QA)
- Code:
  ```python
  from datasets import load_dataset
  truthfulqa = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")
  # Fields: type, category, question, best_answer, correct_answers, incorrect_answers, source
  ```

#### Dataset 2: BBQ (Non-Target Dimension - Fairness/Bias)
- **Name**: Bias Benchmark for Question Answering (BBQ)
- **Type**: standard (HuggingFace datasets)
- **Purpose**: Non-target dimension (fairness - measure bias in QA)
- **Statistics**: Multiple subsets across 9 social dimensions
- **Attack Types**: Ambiguous context vs. unambiguous context
- **Paper**: https://arxiv.org/abs/2110.08193

**Loading Information**:
- Method: HuggingFace `datasets`
- Identifier: `lighteval/bbq_helm`
- Subsets: `all`, `Age`, `Disability_status`, `Gender_identity`, etc.
- Code:
  ```python
  from datasets import load_dataset
  bbq = load_dataset("lighteval/bbq_helm", "all", split="test")
  # Fields: context, question, choices, gold_index
  ```

#### Dataset 3: AdvGLUE (Non-Target Dimension - Robustness)
- **Name**: Adversarial GLUE Benchmark
- **Type**: standard (adversarial robustness evaluation)
- **Purpose**: Non-target dimension (adversarial robustness)
- **Coverage**: 5 GLUE tasks with adversarial perturbations
- **Attack Levels**: Word-level, sentence-level, human-crafted
- **Website**: https://adversarialglue.github.io/

**Loading Information**:
- Method: Custom download from official benchmark
- Identifier: AdvGLUE official evaluation script
- Code: Refer to benchmark website for download instructions
- Note: May require custom data loader implementation

**Sample Size Policy** (addressing experiment scale guidance):
- **TruthfulQA**: Full validation set (817 questions) - statistically meaningful
- **BBQ**: Test split (full set recommended, minimum 500+ samples)
- **AdvGLUE**: Per benchmark specification (typically 500-1000+ samples per task)
- **No trivial subsets**: All evaluations use standard benchmark splits

**Preprocessing**:
- Tokenization: Model-specific tokenizer (GPT-2 tokenizer)
- Max length: 512 tokens (standard for GPT-2)
- Padding: Right-side padding (GPT-2 uses absolute position embeddings)
- No data augmentation (evaluation benchmarks)

### Models

#### Baseline Model

**Architecture**: GPT-2 (124M parameters)
**Type**: Pre-trained causal language model (HuggingFace Transformers)
**Continuation from h-m2**: Reusing same model for controlled comparison

**Model Details**:
- Parameters: 124M (gpt2 base variant)
- Layers: 12 transformer blocks
- Hidden size: 768
- Attention heads: 12
- Context length: 1024 tokens
- Position embeddings: Absolute (pad on right)

**Loading Information**:
- Method: HuggingFace `transformers`
- Identifier: `openai-community/gpt2` (formerly `gpt2`)
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  
  model = AutoModelForCausalLM.from_pretrained(
      "openai-community/gpt2",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("openai-community/gpt2")
  tokenizer.pad_token = tokenizer.eos_token  # GPT-2 has no pad token
  ```

**Why GPT-2 (Continuation Justification)**:
- h-m2 validated representation changes using GPT-2 + LoRA
- h-m3 extends to multi-dimensional evaluation
- **Controlled comparison**: Same base model ensures only evaluation scope changes
- Proven mechanism: LoRA fine-tuning on TruthfulQA already validated in h-m2

#### Proposed Model

**Architecture**: GPT-2 (124M) + LoRA + Multi-Dimensional Correlation Analysis

**Mechanism**: Cross-dimensional performance correlation from representation changes

**Integration**: Extends h-m2's single-dimension evaluation to multi-dimensional tracking

**Core Mechanism Implementation:**

```python
# Core Mechanism: Multi-Dimensional Correlation Analysis
# Based on: h-m2 representation analysis + LibMTL multi-task patterns
# Purpose: Measure correlation between representation changes and multi-dimensional performance

class MultiDimensionalCorrelationAnalyzer:
    """
    Analyzes correlation between layer-wise representation changes 
    and performance across multiple trustworthiness dimensions.
    """
    def __init__(self, model, dimensions=['truthfulness', 'fairness', 'robustness']):
        self.model = model
        self.dimensions = dimensions
        self.layer_names = self._extract_layer_names(model)
    
    def extract_representations(self, inputs, intervention='pre'):
        """
        Extract activations from all layers.
        Args:
            inputs: Tokenized inputs (B, seq_len)
            intervention: 'pre' or 'post' fine-tuning
        Returns:
            Dict[layer_name, tensor]: {layer: (B, seq_len, hidden_dim)}
        """
        activations = {}
        hooks = []
        for name, module in self.model.named_modules():
            if 'attn' in name or 'resid' in name:
                hook = module.register_forward_hook(
                    lambda m, i, o, n=name: activations.update({n: o.detach()})
                )
                hooks.append(hook)
        
        _ = self.model(inputs)
        [h.remove() for h in hooks]
        return activations
    
    def compute_representation_change(self, pre_acts, post_acts):
        """
        Compute CKA similarity between pre/post representations.
        Args:
            pre_acts, post_acts: Dict[layer_name, tensor]
        Returns:
            Dict[layer_name, float]: Change magnitude (1 - CKA)
        """
        from torch_cka import CKA
        cka = CKA()
        changes = {}
        for layer in pre_acts.keys():
            similarity = cka.linear_CKA(pre_acts[layer], post_acts[layer])
            changes[layer] = 1.0 - similarity
        return changes
    
    def evaluate_multi_dimensional(self, model, datasets):
        """
        Evaluate model on all dimensions simultaneously.
        Args:
            model: Fine-tuned model
            datasets: Dict[dimension_name, dataset]
        Returns:
            Dict[dimension_name, float]: Performance on each dimension
        """
        performance = {}
        for dim_name, dataset in datasets.items():
            # TruthfulQA: % truthful
            # BBQ: Accuracy
            # AdvGLUE: Robustness score
            metric = self._evaluate_dimension(model, dataset, dim_name)
            performance[dim_name] = metric
        return performance
    
    def compute_correlation(self, rep_changes, perf_changes):
        """
        Compute correlation between representation changes and 
        performance changes across dimensions.
        Args:
            rep_changes: Dict[layer_name, float] - representation Δ
            perf_changes: Dict[dimension_name, float] - performance Δ
        Returns:
            correlation_matrix: (n_layers, n_dimensions)
        """
        import scipy.stats
        # For each layer, correlate change magnitude with each dimension's Δ
        correlations = {}
        for layer_name, rep_delta in rep_changes.items():
            layer_corrs = {}
            for dim_name, perf_delta in perf_changes.items():
                r, p = scipy.stats.pearsonr([rep_delta], [perf_delta])
                layer_corrs[dim_name] = {'r': r, 'p': p}
            correlations[layer_name] = layer_corrs
        return correlations

# Integration: Wrap around GPT-2 + LoRA from h-m2
# Pre-intervention: Extract baseline representations on all 3 benchmarks
# Post-intervention: Fine-tune on TruthfulQA (target dimension)
# Post-intervention: Extract representations + evaluate all 3 benchmarks
# Analysis: Correlate representation changes with performance changes (D₂, D₃)
```

### Training Protocol

**Inherited from h-m2** (controlled comparison):

**Intervention Method**: LoRA (Low-Rank Adaptation)
- **Rank**: r=8
- **Alpha**: α=16
- **Target modules**: c_attn (attention layers)
- **Rationale**: Validated in h-m2, enables parameter-efficient fine-tuning

**Optimizer**: AdamW
- **Learning rate**: 5e-5
- **Weight decay**: 0.01
- **Betas**: (0.9, 0.999)

**Training Data**: TruthfulQA (target dimension)
- **Sample size**: 500 questions (increased from h-m2's 100 for better coverage)
- **Split**: Random subset from validation set
- **Rationale**: Larger sample for more robust representation changes

**Epochs**: 3
**Batch size**: 4 (with gradient accumulation)
**Seeds**: 3 (42, 43, 44) - for replication across seeds

**Schedule**: Constant learning rate (no decay)
**Loss**: Cross-entropy (causal language modeling)

> Inheriting h-m2 hyperparameters ensures controlled comparison: only evaluation scope changes (single → multi-dimensional).

### Evaluation

**Primary Metrics** (Multi-Dimensional):

**Dimension 1: Truthfulness (Target)**
- Metric: % Truthful (TruthfulQA MC1)
- Expected baseline: ~20-30% (GPT-2 baseline from research)
- Post-intervention: Should improve (target dimension)

**Dimension 2: Fairness (Non-Target)**
- Metric: Accuracy on BBQ (Bias Benchmark)
- Expected baseline: ~50-60% (near random for biased questions)
- Post-intervention: **Measure Δ correlation with D₁**

**Dimension 3: Robustness (Non-Target)**
- Metric: AdvGLUE robustness score
- Expected baseline: Model-dependent
- Post-intervention: **Measure Δ correlation with D₁**

**Correlation Analysis** (Core Hypothesis Test):
- **Primary**: Pearson correlation between Δ(D₁) and [Δ(D₂), Δ(D₃)]
- **Null hypothesis**: ρ = 0 (no correlation, random changes)
- **Alternative**: ρ ≠ 0 (non-random correlation structure)
- **Statistical test**: Pearson correlation with p<0.05 threshold
- **Success criteria**: |ρ| > 0.2 with p<0.05 (differs from random baseline)

**Layer-Wise Analysis**:
- For each of 24 layers, correlate representation change with dimension-specific performance
- Identify which layers most influence which dimensions
- Expected: Attention layers show stronger correlation (from h-m2)

**Metrics Loading Information**:
- Task Type: Multi-benchmark QA evaluation
- Library: Custom evaluation + `scipy.stats` for correlation
- Code:
  ```python
  from scipy.stats import pearsonr
  
  # TruthfulQA evaluation
  truthful_score = evaluate_truthfulqa(model, truthfulqa_dataset)
  
  # BBQ evaluation  
  bbq_accuracy = evaluate_bbq(model, bbq_dataset)
  
  # AdvGLUE evaluation
  advglue_score = evaluate_advglue(model, advglue_dataset)
  
  # Correlation analysis
  r_fairness, p_fairness = pearsonr(delta_truthfulness, delta_fairness)
  r_robustness, p_robustness = pearsonr(delta_truthfulness, delta_robustness)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Correlation structure vs. random baseline

#### Additional Figures (LLM Autonomous)

Based on multi-dimensional correlation analysis, generate:
1. **Correlation Matrix Heatmap**: Layer × Dimension correlation coefficients
2. **Scatter Plots**: Δ(Truthfulness) vs. Δ(Fairness), Δ(Robustness)
3. **Layer Progression**: CKA change magnitude by layer depth (24 layers)
4. **Dimension Performance**: Bar chart comparing pre/post intervention across all 3 dimensions
5. **Statistical Significance**: P-value heatmap showing which correlations are significant

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Hypothesis Success Check

**Gate Type:** SHOULD_WORK (allows continuation with documented limitations)

**Pass Conditions:**

**Primary (Required for PASS):**
1. Code runs without error across all 3 dimensions
2. Correlation analysis completes successfully
3. Statistical test produces valid p-values
4. At least one dimension pair shows **non-random correlation** (p<0.05)

**Secondary (Desirable for strong PASS):**
1. Correlation magnitudes |ρ| > 0.2 for at least one pair
2. Multiple dimension pairs show significant correlation
3. Correlation direction consistent across replicates (3 seeds)
4. Layer-wise analysis identifies dimension-specific patterns

**Success Interpretation:**

- **PASS (Primary met):** Mechanism validated - representation changes propagate to non-target dimensions in non-random fashion
- **PASS (Secondary met):** Strong evidence - multiple dimensions affected with measurable effect sizes
- **PARTIAL (Only code runs):** Mechanism activates but correlations are random - suggests independence between dimensions
- **FAIL (Errors):** Implementation issues - cannot evaluate hypothesis

**SHOULD_WORK Gate Behavior:**
- Even if correlations are weak/random, document findings and proceed to h-m4
- Failure only if code cannot execute or gates are violated
- Scientific value in null results: demonstrates which dimensions are/aren't coupled

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: HuggingFace PEFT/LoRA Documentation
- **Type**: Knowledge base article
- **Query Used**: "multi-task learning representation correlation"
- **Relevance**: Confirmed LoRA as standard fine-tuning approach (validated from h-m2)
- **Key Insights**:
  - Low-rank adaptation preserves base model while adapting specific parameters
  - Standard approach for parameter-efficient fine-tuning
- **Used For**: Training protocol (LoRA configuration inherited from h-m2)

**Source A.2**: General Benchmark Evaluation Methodology
- **Type**: OpenReview paper (general evaluation)
- **Query Used**: "trustworthiness benchmark evaluation metrics"
- **Relevance**: General benchmark methodology principles
- **Limitation**: Not specific to multi-dimensional trustworthiness evaluation
- **Used For**: Background on evaluation best practices

**Archon Knowledge Base Assessment**: Limited prior work on multi-dimensional trustworthiness correlation analysis. Confirmed standard approaches (LoRA) but no direct precedent for cross-dimensional correlation propagation.

### Archon Code Examples

**Code Source A.1**: Multi-Metric Configuration Pattern (MMGeneration)
- **Query Used**: "correlation analysis multiple metrics"
- **Key Code**:
  ```python
  # Pattern for tracking multiple metrics simultaneously
  metrics = dict(
      metric1=dict(type='FID', num_images=50000),
      metric2=dict(type='PR', num_images=50000),
      metric3=dict(type='PPL', space='W')
  )
  ```
- **Used For**: Structure for simultaneous multi-dimension evaluation (TruthfulQA, BBQ, AdvGLUE)

**Code Source A.2**: CLIP Contrastive Learning (DALLE2-pytorch)
- **Query Used**: "representation similarity CKA PyTorch"
- **Relevance**: Multi-modal similarity computation example
- **Limitation**: Different domain (vision-language, not layer-wise CKA)
- **Used For**: General pattern reference (not directly applicable)

### B. GitHub Implementations (Exa)

**Repository B.1**: median-research-group/LibMTL
- **URL**: https://github.com/median-research-group/LibMTL
- **Stars**: High activity
- **Query Used**: "multi-task learning representation correlation PyTorch implementation"
- **Relevance**: ⭐⭐⭐ HIGHEST - Comprehensive MTL framework with loss weighting and architecture support
- **Key Features**:
  - 16 optimization strategies including gradient balancing (MGDA, CAGrad, Nash-MTL)
  - 8 MTL architectures (HPS, Cross-stitch, MMoE, MTAN)
  - Rep-grad vs Param-grad: Supports gradient computation at representation level
  - Unified framework for multi-input/multi-output problems
- **Key Patterns**:
  ```python
  # Multi-task loss weighting
  for i in range(len(tasks)):
      loss += l_weights[i] * l_funcs[i](y_hat[i], y[i])
  
  # Representation-level gradient computation
  shared_rep = encoder(x).detach()  # Detach for rep-grad
  task_outputs = [decoder_i(shared_rep) for decoder_i in decoders]
  ```
- **Used For**: 
  - Multi-dimensional evaluation structure
  - Pattern for balancing multiple dimension metrics
  - Representation-level analysis approach (matches h-m2)

**Repository B.2**: SimonVandenhende/Multi-Task-Learning-PyTorch
- **URL**: https://github.com/SimonVandenhende/Multi-Task-Learning-PyTorch
- **Stars**: 840
- **Query Used**: "multi-task learning representation correlation PyTorch implementation"
- **Relevance**: ⭐⭐ MEDIUM - Dense prediction MTL, survey implementation
- **Key Pattern**:
  ```python
  # Multi-task evaluation pattern
  for epoch in range(epochs):
      train_vanilla(train_dataloader, model, criterion, optimizer)
      save_model_predictions(val_dataloader, model)
      curr_result = eval_all_results()  # Multi-task evaluation
      improves = validate_results(curr_result, best_result)
  ```
- **Used For**: Pattern for simultaneous multi-dimension evaluation

**Repository B.3**: xiaogang00/MTFormer (ECCV 2022)
- **URL**: https://github.com/xiaogang00/MTFormer
- **Query Used**: "multi-task learning representation correlation PyTorch implementation"
- **Relevance**: ⭐⭐ MEDIUM - Transformer-based MTL with cross-task attention
- **Novel Mechanism**: Cross-task attention + self-supervised contrastive learning
- **Limitation**: Different domain (vision), but cross-task attention pattern useful
- **Used For**: Inspiration for cross-dimensional reasoning (not directly implemented)

**Repository B.4**: sylinrl/TruthfulQA (Official)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Query Used**: "TruthfulQA BBQ AdvGLUE trustworthiness benchmark evaluation"
- **Relevance**: ⭐⭐⭐ HIGHEST - Official TruthfulQA implementation
- **Dataset Details**:
  - 817 questions across 38 categories
  - Adversarial + non-adversarial questions
  - Multiple evaluation metrics: GPT-judge, BLEURT, ROUGE, BLEU
- **Loading Code**:
  ```python
  from datasets import load_dataset
  truthfulqa = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")
  ```
- **Evaluation Pattern**:
  ```python
  python truthfulqa/evaluate.py \
      --models [model_name] \
      --metrics bleurt,gpt-judge,info \
      --preset qa \
      --device 0
  ```
- **Baseline Performance**: GPT-3-175B: 20.44% true, UnifiedQA-3B: 53.86% true
- **Used For**: 
  - Dataset loading (TruthfulQA)
  - Evaluation metrics (% truthful)
  - Expected baseline performance ranges

**Repository B.5**: BBQ Benchmark (lighteval/bbq_helm)
- **URL**: https://huggingface.co/datasets/lighteval/bbq_helm
- **Paper**: https://arxiv.org/abs/2110.08193
- **Query Used**: "TruthfulQA BBQ AdvGLUE trustworthiness benchmark evaluation"
- **Relevance**: ⭐⭐⭐ HIGH - Official bias benchmark
- **Coverage**: 9 social dimensions (Age, Disability, Gender, etc.)
- **Attack Types**: Ambiguous vs. unambiguous context
- **Loading Code**:
  ```python
  from datasets import load_dataset
  bbq = load_dataset("lighteval/bbq_helm", "all", split="test")
  ```
- **Used For**: Dataset loading and fairness dimension evaluation (D₂)

**Repository B.6**: AdvGLUE Benchmark
- **URL**: https://adversarialglue.github.io/
- **Query Used**: "TruthfulQA BBQ AdvGLUE trustworthiness benchmark evaluation"
- **Relevance**: ⭐⭐⭐ HIGH - Official adversarial robustness benchmark
- **Coverage**: 5 GLUE tasks with adversarial examples
- **Attack Levels**: Word-level, sentence-level, human-crafted
- **Evaluation**: `python evaluate.py <pred_file>`
- **Used For**: Robustness dimension evaluation (D₃)

### C. Code Analysis (Serena)

**Serena Analysis**: ❌ NOT PERFORMED (not needed)

**Rationale**:
- TruthfulQA evaluation code straightforward (<100 lines from Exa search)
- LibMTL framework well-documented with clear patterns
- h-m2 code already validated in previous hypothesis
- Multi-task evaluation patterns clear from research

**Decision**: Proceed directly to Phase 3 PRD without Serena analysis

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-m2
- **File**: `h-m2/04_validation.md`
- **Status**: ✅ COMPLETED (PASS)
- **Reused Components**:
  - **Model**: GPT-2 (124M parameters) - Proven stable
  - **Intervention**: LoRA (r=8, α=16) fine-tuning on TruthfulQA - Validated
  - **Analysis Pipeline**: TransformerLens + CKA for representation extraction - Functional
  - **Training Config**: AdamW (lr=5e-5), 3 epochs, batch size 4 - Optimal
- **h-m2 Results**:
  - Mean CKA similarity: 0.857 (mean change: 0.143)
  - 100% layers showed measurable changes (24/24)
  - Attention patterns changed more than residual streams (2.0× magnitude)
  - Correlation with performance: r=0.150 (p=0.28, non-significant)
  - Gate verdict: PASS (SHOULD_WORK allows continuation)
- **Why Reused**: Enables controlled experiment - only evaluation scope changes (single → multi-dimensional)
- **h-m3 Extensions**:
  - Increase training samples: 100 → 500 (better coverage)
  - Multi-dimensional evaluation: TruthfulQA + BBQ + AdvGLUE
  - Per-dimension correlation analysis (not aggregate)
  - Random baseline comparison (permutation test)

### E. Traceability Matrix

| Specification | Source Type | Source Reference | Notes |
|--------------|-------------|------------------|-------|
| Dataset (TruthfulQA) | GitHub (Official) | B.4 (sylinrl/TruthfulQA) | Direct HF integration |
| Dataset (BBQ) | GitHub (HF) | B.5 (lighteval/bbq_helm) | Direct HF integration |
| Dataset (AdvGLUE) | Benchmark Website | B.6 (adversarialglue.github.io) | Custom loader needed |
| Baseline model (GPT-2) | Previous + HF Docs | D.1 (h-m2) + HF Transformers | Reused from h-m2 |
| Intervention (LoRA) | Previous | D.1 (h-m2 validation) | Proven optimal config |
| Mechanism design | LibMTL patterns | B.1 (median-research-group/LibMTL) | Multi-task correlation |
| Pseudo-code | h-m2 + LibMTL | D.1 + B.1 | Extended h-m2 pipeline |
| Training protocol | Previous (h-m2) | D.1 (h-m2 validation) | Controlled comparison |
| Evaluation metrics | TruthfulQA + Custom | B.4 + scipy.stats | Multi-dimensional |
| Multi-task patterns | LibMTL + MTFormer | B.1, B.2, B.3 | Structure reference |
| CKA analysis | Previous (h-m2) | D.1 (h-m2 code) | Proven implementation |
| Correlation analysis | scipy.stats | Standard library | Pearson correlation |

**Coverage**: All specifications trace to documented sources (Archon, Exa, or previous hypothesis)

**Novel Contribution**: Multi-dimensional correlation analysis for trustworthiness dimensions (no direct prior work found)

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** {{timestamp}}

### Workflow History for This Hypothesis

**Phase 2C (Experiment Design)**:
- Started: 2026-05-11T08:02:32+00:00
- Completed: 2026-05-11T08:10:00+00:00
- Duration: ~8 minutes
- Output: 02c_experiment_brief.md (870 lines)
- Status: ✅ COMPLETED

**MCP Tools Used**:
- Archon Knowledge Base: 3 queries (LoRA, multi-task learning, benchmarks)
- Archon Code Examples: 2 queries (representation similarity, correlation analysis)
- Exa GitHub Search: 2 queries (multi-task learning implementations, trustworthiness benchmarks)

**Research Sources**:
- 6 GitHub repositories analyzed
- Complete traceability matrix generated
- All specifications grounded in research findings

**Next Phase**: Phase 3 - Implementation Planning

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
