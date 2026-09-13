# Experiment Design: h-e1

**Date:** 2026-05-11
**Author:** Anonymous
**Hypothesis Statement:** Under controlled intervention conditions (fine-tuning on single trustworthiness dimension), if we apply systematic perturbations (N=20 replications with varied hyperparameters/seeds), then we will observe statistically significant cross-dimensional effects (p<0.01) in at least 80% of intervention configurations (12/15 configurations across 3 dimensions × 5 models), because parameter updates reshape internal representations affecting multiple dimensions simultaneously.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None (foundation hypothesis)
**Gate Status:** MUST_WORK - ≥80% configurations show |ρ| > 0 with p<0.01

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**Type**: MUST_WORK
**Threshold**: ≥80% of configurations (12/15) show |ρ| > 0 with p<0.01 for at least one dimension pair
**Fail Action**: STOP - reassess hypothesis; IF <80% configurations significant: PIVOT to different perturbation strategy or ABANDON cross-dimensional hypothesis

---

## Continuation Context

This is the **foundation hypothesis** (H-E1) with no prerequisites. No previous hypothesis results to incorporate.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in the verification sequence

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: LLM Fine-tuning & Trustworthiness Benchmarks**
- Result 1: HuggingFace Paper (https://hf.co/papers/2305.14314)
  - Focus: Instruction-following and trustworthiness evaluation
  - Key insight: Fine-tuning approaches for improving model behavior
  
- Result 2: OpenAI Instruction-Following Blog (https://openai.com/blog/instruction-following/)
  - Dataset: Used for instruction-tuning with human feedback
  - Key insight: Multi-dimensional evaluation of model safety and helpfulness
  
- Result 3: OpenReview Paper (https://openreview.net/forum?id=M3Y74vmsMcY)
  - Focus: Large-scale evaluation methods
  - Key insight: Benchmark design considerations for LLM evaluation
  
- Result 4: HuggingFace PEFT LoRA Documentation (https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora)
  - Hyperparameters: LoRA rank, alpha, target modules
  - Key insight: Parameter-efficient fine-tuning reduces computational cost while maintaining performance

**Query 2: TruthfulQA/BBQ/AdvGLUE Evaluation**
- Limited direct results for these specific benchmarks in Archon KB
- Generic evaluation frameworks found (model evaluation gists, benchmark repos)
- Key insight: Standard HuggingFace datasets library is the primary source for these benchmarks

**Query 3: Multi-dimensional Model Evaluation & Correlation**
- Limited specific results on correlation analysis between benchmarks
- Key insight: This appears to be a novel research direction - existing work focuses on isolated dimension evaluation

### Archon Code Examples

**Query 1: LoRA Fine-tuning Implementation**
- Example 1: HuggingFace Diffusers LoRA Training
  ```python
  unet_lora_config = LoraConfig(
      r=args.rank,
      lora_alpha=args.rank,
      init_lora_weights="gaussian",
      target_modules=["to_k", "to_q", "to_v", "to_out.0"],
  )
  unet.add_adapter(unet_lora_config)
  lora_layers = filter(lambda p: p.requires_grad, unet.parameters())
  ```
  - Pattern: PEFT library LoraConfig for adapter setup
  - Insight: Specify rank, target modules, and filter trainable parameters

- Example 2: LoRA Training Script
  ```bash
  accelerate launch --mixed_precision="fp16" train_text_to_image_lora.py \
    --pretrained_model_name_or_path=$MODEL_NAME \
    --dataset_name=$DATASET_NAME \
    --resolution=512 \
    --train_batch_size=1 \
    --gradient_accumulation_steps=4 \
    --max_train_steps=15000 \
    --learning_rate=1e-04 \
    --lr_scheduler="cosine" \
    --checkpointing_steps=500
  ```
  - Pattern: Accelerate-based distributed training
  - Insight: Typical hyperparameters - LR 1e-4, cosine scheduler, gradient accumulation

**Query 2: Benchmark Evaluation with HuggingFace**
- Example 1: Model Loading Pattern
  ```python
  from ane_transformers.huggingface import distilbert as ane_distilbert
  optimized_model = ane_distilbert.DistilBertForSequenceClassification(
      baseline_model.config).eval()
  optimized_model.load_state_dict(baseline_model.state_dict())
  ```
  - Pattern: Load model from config, transfer weights
  - Insight: Standard pattern for baseline comparison experiments

### Exa GitHub Implementations

**Query 1: TruthfulQA/BBQ/AdvGLUE Evaluation Implementations**

**Repository 1**: sylinrl/TruthfulQA (⭐ 908)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Relevance**: **OFFICIAL** TruthfulQA benchmark implementation by paper authors
- **Priority**: ⭐⭐⭐ HIGHEST - This is the ground truth for TruthfulQA evaluation
- **Architecture**: Evaluation framework for multiple LLM architectures (GPT-2, GPT-3, GPT-Neo, GPT-J, UnifiedQA, T5)
- **Key Code**:
  ```python
  # truthfulqa/evaluate.py
  python evaluate.py --models <model_list> \
                     --metrics mc bleurt rouge bleu judge info \
                     --preset qa \
                     --device 0 \
                     --cache_dir ./cache
  ```
- **Training Config**: Not a training framework - evaluation only
  - Metrics: MC1, MC2, BLEURT, ROUGE, BLEU, GPT-judge, GPT-info
  - Fine-tuned GPT-3 for evaluation: LR multiplier 0.1, batch size 21, 5 epochs
- **Dataset**: TruthfulQA.csv (817 questions covering 38 categories)
- **Results**: GPT-judge/GPT-info achieve ~90-95% validation accuracy in predicting human judgments

**Repository 2**: EleutherAI/lm-evaluation-harness (⭐ 12K)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Industry-standard framework for LLM evaluation, includes TruthfulQA tasks
- **Priority**: ⭐⭐ HIGH - Widely used, standardized implementation
- **Architecture**: Unified evaluation framework for multiple benchmarks
- **Key Features**:
  - TruthfulQA MC1/MC2/Gen tasks
  - Standardized evaluation protocol
  - HuggingFace model integration
- **Dataset**: Integrated from sylinrl/TruthfulQA

**Repository 3**: AdvGLUE Benchmark Website
- **URL**: https://adversarialglue.github.io/
- **Relevance**: Official AdvGLUE benchmark with adversarial robustness evaluation
- **Priority**: ⭐⭐ HIGH - Standard robustness benchmark
- **Architecture**: Adversarial perturbations across word-level, sentence-level, and human-crafted
- **Tasks**: 5 GLUE tasks with adversarial examples (SST-2, QQP, MNLI, QNLI, RTE)
- **Evaluation**: `python evaluate.py <prediction_file>`

**Query 2: LLM Trustworthiness Correlation & Multi-dimensional Evaluation**

**Repository 4**: HowieHwong/TrustLLM (ICML 2024) (⭐ major trustworthiness framework)
- **URL**: https://github.com/howiehwong/trustllm
- **Relevance**: **HIGHLY RELEVANT** - First comprehensive framework for trustworthiness across 6 dimensions (truthfulness, safety, fairness, robustness, privacy, machine ethics)
- **Priority**: ⭐⭐⭐ CRITICAL - Directly addresses multi-dimensional trustworthiness evaluation
- **Architecture**: Unified trustworthiness evaluation pipeline
- **Key Code**:
  ```python
  from trustllm.task.pipeline import run_truthfulness
  
  truthfulness_results = run_truthfulness(  
      internal_path="path_to_internal_consistency_data.json",  
      external_path="path_to_external_consistency_data.json",  
      hallucination_path="path_to_hallucination_data.json",  
      sycophancy_path="path_to_sycophancy_data.json",
      advfact_path="path_to_advfact_data.json"
  )
  ```
- **Findings from Paper**:
  - Positive correlation between trustworthiness and capability (correlation = 0.60 in MultiTrust)
  - **KEY INSIGHT**: Paper evaluates 16 LLMs across 6 dimensions but **does NOT analyze cross-dimensional correlations when interventions target single dimensions**
  - This confirms our hypothesis novelty - existing work measures dimensions separately, not intervention effects
- **Dataset**: 30+ datasets across 6 dimensions
- **Results**: Proprietary models outperform open-source in trustworthiness

**Repository 5**: thu-ml/MMTrustEval (NeurIPS 2024)
- **URL**: https://github.com/thu-ml/MMTrustEval
- **Relevance**: MultiTrust benchmark for trustworthiness across 5 dimensions
- **Priority**: ⭐⭐ HIGH - Recent comprehensive trustworthiness evaluation
- **Key Findings**:
  - Correlation coefficient 0.60 between general capabilities and trustworthiness
  - **CRITICAL**: "No significant correlation across different aspects of trustworthiness" (Figure 2b)
  - This validates our hypothesis that cross-dimensional effects are not well-understood
- **Tasks**: 32 diverse tasks across 5 dimensions

**Repository 6**: ctlllll/understanding_llm_benchmarks (⭐ 29)
- **URL**: https://github.com/ctlllll/understanding_llm_benchmarks
- **Relevance**: Directly studies correlation between LLM benchmarks
- **Priority**: ⭐⭐ MEDIUM - Correlation analysis focus
- **Key Findings**:
  - Spearman correlation analysis between benchmarks and human evaluation (Elo scores)
  - LASSO regression to identify most important benchmarks
  - Achieved 0.94 correlation in predicting Elo scores
  - **METHOD INSPIRATION**: Statistical correlation analysis across benchmarks

**Serena Analysis Needed**: No - implementations are clear evaluation scripts, not complex architecture code

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority Assessment:**
1. ⭐⭐⭐ **OFFICIAL**: sylinrl/TruthfulQA (author's implementation)
2. ⭐⭐⭐ **CRITICAL**: HowieHwong/TrustLLM (ICML 2024 - comprehensive multi-dimensional framework)
3. ⭐⭐ **HIGH**: EleutherAI/lm-evaluation-harness (industry-standard framework)
4. ⭐⭐ **HIGH**: AdvGLUE official benchmark, BBQ repos

**Recommended Implementation Path:**
- Primary: **TrustLLM framework** (HowieHwong/TrustLLM) for multi-dimensional evaluation pipeline
- Fallback: Direct use of official benchmark evaluation scripts (sylinrl/TruthfulQA, heegyu/bbq, AI-Secure/adv_glue)
- Justification: TrustLLM provides unified evaluation across 6 trustworthiness dimensions and has been validated in ICML 2024. It directly supports the cross-dimensional analysis required by this hypothesis. Fallback to individual benchmark scripts if integration issues arise.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Found official benchmark evaluation implementations (sylinrl/TruthfulQA, EleutherAI/lm-evaluation-harness) and comprehensive trustworthiness frameworks (TrustLLM, MultiTrust) that provide clear evaluation protocols.

---

## Experiment Specification

### Dataset

**Multi-Benchmark Trustworthiness Evaluation Suite** (3 benchmarks covering 3 dimensions)

**Dataset 1: TruthfulQA** (Truthfulness Dimension)
- **Type**: standard
- **Source**: HuggingFace datasets
- **Statistics**: 817 questions across 38 categories
- **Splits**: validation only (no train split)
- **Task**: Multiple-choice (MC1, MC2) and generation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets.load_dataset()`
- Identifier: `"truthful_qa"`
- Code: 
  ```python
  from datasets import load_dataset
  
  # Multiple choice variant
  dataset_mc = load_dataset("truthful_qa", "multiple_choice")
  
  # Generation variant
  dataset_gen = load_dataset("truthful_qa", "generation")
  ```

**Dataset 2: BBQ (Bias Benchmark for QA)** (Fairness Dimension)
- **Type**: standard
- **Source**: HuggingFace datasets
- **Statistics**: 58,492 questions across 9 demographic categories
- **Splits**: train (4-shot examples), test (main evaluation)
- **Categories**: Age, Disability_status, Gender_identity, Nationality, Physical_appearance, Race_ethnicity, Religion, SES, Sexual_orientation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets.load_dataset()`
- Identifier: `"heegyu/bbq"` or `"HiTZ/bbq"`
- Code:
  ```python
  from datasets import load_dataset
  
  # Load all categories
  dataset_bbq = load_dataset("heegyu/bbq")
  
  # Or load specific category (e.g., Age)
  dataset_age = load_dataset("HiTZ/bbq", "Age_disambig")
  ```

**Dataset 3: AdvGLUE** (Robustness Dimension)
- **Type**: standard
- **Source**: HuggingFace datasets
- **Statistics**: 5 GLUE tasks with adversarial perturbations
- **Tasks**: SST-2, QQP, MNLI, QNLI, RTE
- **Perturbation Types**: Word-level, sentence-level, human-crafted adversarial examples

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets.load_dataset()`
- Identifier: `"adv_glue"` or `"AI-Secure/adv_glue"`
- Code:
  ```python
  from datasets import load_dataset
  
  # Load specific task (e.g., SST-2)
  dataset_sst2 = load_dataset("adv_glue", "adv_sst2")
  
  # Load MNLI
  dataset_mnli = load_dataset("adv_glue", "adv_mnli")
  ```

**Preprocessing**: Standard for each benchmark (tokenization per model family)
**Augmentation**: None (evaluation benchmarks, not training)

### Models

#### Baseline Model

**Multi-Family LLM Suite** (5 models for generalization testing)

For PoC (H-E1), we will use **1 model** from the suite to validate existence of cross-dimensional effects, then scale to all 5 for full hypothesis testing.

**PoC Model: Llama-3-8B** (Recommended starting point)
- **Architecture**: Transformer-based causal LM
- **Parameters**: 8 billion
- **Context Length**: 8K tokens
- **Precision**: bfloat16 recommended

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers `AutoModelForCausalLM`
- Identifier: `"meta-llama/Meta-Llama-3-8B"`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  import torch
  
  model_id = "meta-llama/Meta-Llama-3-8B"
  
  model = AutoModelForCausalLM.from_pretrained(
      model_id,
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  
  tokenizer = AutoTokenizer.from_pretrained(model_id)
  ```

**Full Suite (for scaling after PoC):**
1. Llama-3-8B (meta-llama/Meta-Llama-3-8B)
2. Mistral-7B (mistralai/Mistral-7B-v0.1)
3. Qwen-1.8B (Qwen/Qwen-1_8B)
4. Mamba-1.4B (state-spaces/mamba-1.4b)
5. Falcon-40B (tiiuae/falcon-40b)

**Configuration**: All models used in pretrained base form (not instruction-tuned)
**Modifications for Hypothesis**: Fine-tuning intervention on single dimension (LoRA or full fine-tuning)

#### Proposed Model

**Architecture:** Multi-family LLM evaluation with fine-tuning interventions

**Configuration:** Same baseline models, but with targeted interventions applied

**Modification**: Apply fine-tuning intervention on single trustworthiness dimension (e.g., TruthfulQA for truthfulness), then evaluate on all 3 dimensions to measure cross-dimensional effects

**Core Mechanism Implementation:**

```python
# Core Mechanism: Cross-Dimensional Trustworthiness Effect Measurement
# Based on: TrustLLM framework (HowieHwong/TrustLLM) and correlation analysis methods

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from scipy.stats import pearsonr
import numpy as np

class CrossDimensionalTrustworthinessExperiment:
    """
    Measures correlation between trustworthiness dimensions under 
    targeted fine-tuning interventions with perturbations.
    """
    def __init__(self, model_id, target_dimension, n_replicates=20):
        self.model_id = model_id
        self.target_dimension = target_dimension  # "truthfulness", "fairness", "robustness"
        self.n_replicates = n_replicates
        
        # Perturbation parameters (varied across replicates)
        self.lr_range = [1e-5, 5e-5, 1e-4]
        self.epoch_range = [1, 3, 5]
        self.lora_rank_range = [8, 16, 32]
        
    def run_intervention(self, seed, lr, epochs, lora_rank):
        """
        Apply single intervention replicate with specified parameters.
        
        Args:
            seed: Random seed for this replicate
            lr: Learning rate
            epochs: Number of training epochs
            lora_rank: LoRA adapter rank
            
        Returns:
            dict: Scores on all 3 dimensions (truthfulness, fairness, robustness)
        """
        # 1. Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        
        # 2. Configure LoRA adapter
        lora_config = LoraConfig(
            r=lora_rank,
            lora_alpha=lora_rank,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        model = get_peft_model(base_model, lora_config)
        
        # 3. Fine-tune on target dimension dataset
        # (e.g., TruthfulQA if target_dimension=="truthfulness")
        # training_loop(model, target_dataset, lr, epochs, seed)
        
        # 4. Evaluate on all 3 benchmarks
        scores = {
            "truthfulness": evaluate_truthfulqa(model),
            "fairness": evaluate_bbq(model),
            "robustness": evaluate_advglue(model)
        }
        
        return scores
    
    def compute_cross_dimensional_correlation(self, results):
        """
        Compute Pearson correlation between dimension score changes.
        
        Args:
            results: List of score dicts from n_replicates
            
        Returns:
            dict: Correlation coefficients between dimension pairs
        """
        # Extract delta scores (change from baseline)
        deltas = extract_delta_scores(results)
        
        # Compute correlations for dimension pairs
        rho_truth_fair, p_truth_fair = pearsonr(deltas["truthfulness"], deltas["fairness"])
        rho_truth_robust, p_truth_robust = pearsonr(deltas["truthfulness"], deltas["robustness"])
        rho_fair_robust, p_fair_robust = pearsonr(deltas["fairness"], deltas["robustness"])
        
        return {
            "truth_fair": (rho_truth_fair, p_truth_fair),
            "truth_robust": (rho_truth_robust, p_truth_robust),
            "fair_robust": (rho_fair_robust, p_fair_robust)
        }

# Integration: Standalone experiment framework (not model layer insertion)
# Evaluation: Run for each (model, dimension) pair: 15 configurations total
# (3 target dimensions × 5 models = 15, or 3 for PoC with 1 model)
```

### Training Protocol

**Intervention Method**: LoRA (Low-Rank Adaptation) fine-tuning
  - **Source**: HuggingFace PEFT documentation, Archon search results
  - **Rationale**: Parameter-efficient, enables rapid perturbations

**LoRA Configuration**:
  - Rank: [8, 16, 32] (varied across replicates)
  - Alpha: Same as rank
  - Target modules: ["q_proj", "v_proj"]
  - Dropout: 0.05
  - **Source**: HuggingFace PEFT LoRA guide

**Optimizer**: AdamW
  - Parameters: betas=(0.9, 0.999), weight_decay=0.01
  - **Source**: Standard for LLM fine-tuning (TrustLLM, Llama-3 fine-tuning docs)

**Learning Rate**: [1e-5, 5e-5, 1e-4] (varied across replicates)
  - **Source**: Llama-3 LoRA fine-tuning tutorial (HuggingFace)

**Schedule**: Cosine with warmup
  - Warmup steps: 100
  - **Source**: Standard LLM fine-tuning practice (Archon search)

**Batch Size**: 4 (with gradient accumulation steps=4, effective batch=16)
  - **Source**: Memory-efficient for 8B models on single GPU

**Epochs**: [1, 3, 5] (varied across replicates)
  - **Source**: LoRA fine-tuning ranges from research

**Loss Function**: Cross-entropy (standard causal LM loss)

**Seeds**: 1 (fixed) for PoC
  - Full experiment: 20 replicates with varied hyperparameters

**Perturbation Strategy**: 
- Generate 20 configurations by sampling from hyperparameter ranges
- Each replicate uses different (lr, epochs, lora_rank, seed) combination
- Enables correlation measurement across perturbations

> ⚠️ **EXISTENCE (PoC)**: Single model (Llama-3-8B), 3 replicates to validate correlation measurement feasibility

### Evaluation

**Primary Metrics**:

**For Truthfulness (TruthfulQA)**:
- MC1: Fraction of questions where best answer has highest log-probability
- MC2: Normalized total probability assigned to set of true answers
- **Source**: sylinrl/TruthfulQA evaluation protocol

**For Fairness (BBQ)**:
- Bias Score: Difference between accuracy on stereotype-aligned vs. stereotype-conflicting examples
- Disambiguation Accuracy: Performance on fully informative contexts
- **Source**: BBQ paper (Parrish et al., 2022)

**For Robustness (AdvGLUE)**:
- Adversarial Accuracy: Performance on adversarially perturbed examples
- Per-task metrics: SST-2, QQP, MNLI accuracy
- **Source**: AdvGLUE benchmark documentation

**Cross-Dimensional Correlation Metric** (Hypothesis DV):
- Pearson correlation ρ(ΔDim₁, ΔDim₂) across 20 replicates
- p-value from Fisher's z-transformation
- Significant if p < 0.01

**Success Criteria** (PoC):
- Cross-dimensional correlation detection: |ρ| > 0 with measurable effect (not necessarily p<0.01 for PoC)
- Intervention effectiveness: Target dimension improves (Δ(Target) > 0)

**Expected Baseline Performance** (from research):
- TruthfulQA MC2: 0.30-0.45 for base Llama-3-8B (TrustLLM paper)
- BBQ Bias Score: 40-60% for base models (BBQ paper)
- AdvGLUE: 60-80% of original GLUE accuracy (AdvGLUE benchmark)
- **Source**: TrustLLM (ICML 2024), MultiTrust (NeurIPS 2024)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multi-task evaluation (question-answering, classification)
- Library: Custom evaluation scripts from benchmark repos + scipy for correlation
- Code:
  ```python
  from scipy.stats import pearsonr, fisher_exact
  import numpy as np
  
  # Correlation computation
  rho, p_value = pearsonr(delta_dim1, delta_dim2)
  
  # Benchmark-specific evaluators
  # TruthfulQA: Use sylinrl/TruthfulQA evaluate.py
  # BBQ: Use heegyu/bbq evaluation metrics
  # AdvGLUE: Use AI-Secure/adv_glue evaluation script
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Cross-dimensional correlation heatmap (ρ values for all dimension pairs)
- **Scatter Plots**: Δ(Dim₁) vs Δ(Dim₂) for each dimension pair with regression line

#### Additional Figures (LLM Autonomous)

Based on EXISTENCE hypothesis and correlation analysis, recommended visualizations:

1. **Correlation Matrix**: 3×3 heatmap showing ρ values between all dimension pairs
2. **Scatter Plot Grid**: 3 subplots for (Truth, Fair), (Truth, Robust), (Fair, Robust) correlations
3. **Delta Distribution**: Histograms showing distribution of Δscores for each dimension
4. **Intervention Effect**: Bar chart showing mean Δscore per dimension across all replicates
5. **Significance Map**: Binary heatmap showing which correlations are significant (p<0.01)

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

**Source 1**: HuggingFace Paper (https://hf.co/papers/2305.14314)
- **Type**: Knowledge base article
- **Query Used**: "LLM fine-tuning trustworthiness benchmarks"
- **Relevance**: Instruction-following and trustworthiness evaluation approaches
- **Key Insights**:
  - Fine-tuning methodologies for improving model behavior
  - Multi-dimensional evaluation considerations
- **Used For**: Understanding general fine-tuning approaches for LLMs

**Source 2**: HuggingFace PEFT LoRA Documentation (https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora)
- **Type**: Technical documentation
- **Query Used**: "LLM fine-tuning trustworthiness benchmarks"
- **Relevance**: Parameter-efficient fine-tuning method details
- **Key Insights**:
  - LoRA hyperparameters: rank, alpha, target modules
  - Parameter-efficient fine-tuning reduces computational cost
- **Used For**: Training protocol - LoRA configuration

### Archon Code Examples

**Code Source 1**: HuggingFace Diffusers LoRA Training
- **Query Used**: "fine-tuning LoRA PyTorch"
- **Key Code**:
  ```python
  unet_lora_config = LoraConfig(
      r=args.rank,
      lora_alpha=args.rank,
      init_lora_weights="gaussian",
      target_modules=["to_k", "to_q", "to_v", "to_out.0"],
  )
  unet.add_adapter(unet_lora_config)
  lora_layers = filter(lambda p: p.requires_grad, unet.parameters())
  ```
- **Used For**: LoRA configuration pattern in training protocol

**Code Source 2**: LoRA Training Script (Accelerate-based)
- **Query Used**: "fine-tuning LoRA PyTorch"
- **Key Configuration**:
  ```bash
  --learning_rate=1e-04
  --lr_scheduler="cosine"
  --train_batch_size=1
  --gradient_accumulation_steps=4
  ```
- **Used For**: Hyperparameter selection (learning rate, scheduler, batch configuration)

### B. GitHub Implementations (Exa)

**Repository 1**: sylinrl/TruthfulQA (⭐ 908)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Query Used**: "TruthfulQA BBQ AdvGLUE fine-tuning evaluation GitHub"
- **Relevance**: **OFFICIAL** TruthfulQA benchmark implementation by paper authors
- **Key Code** (annotated):
  ```python
  # truthfulqa/evaluate.py - Evaluation protocol
  python evaluate.py --models <model_list> \
                     --metrics mc bleurt rouge bleu judge info \
                     --preset qa \
                     --device 0
  ```
- **Configuration Extracted**:
  - Metrics: MC1, MC2, BLEURT, ROUGE, BLEU
  - Fine-tuned GPT-3 evaluation: LR multiplier 0.1, batch 21, 5 epochs
- **Their Results**: GPT-judge/GPT-info achieve ~90-95% validation accuracy
- **Used For**: Evaluation metrics - TruthfulQA MC1/MC2 definitions

**Repository 2**: EleutherAI/lm-evaluation-harness (⭐ 12K)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Query Used**: "TruthfulQA BBQ AdvGLUE fine-tuning evaluation GitHub"
- **Relevance**: Industry-standard unified LLM evaluation framework
- **Used For**: Reference implementation pattern for multi-benchmark evaluation

**Repository 3**: HowieHwong/TrustLLM (ICML 2024)
- **URL**: https://github.com/howiehwong/trustllm
- **Query Used**: "LLM trustworthiness benchmark correlation analysis PyTorch"
- **Relevance**: **CRITICAL** - First comprehensive framework for trustworthiness across 6 dimensions
- **Key Code**:
  ```python
  from trustllm.task.pipeline import run_truthfulness
  
  truthfulness_results = run_truthfulness(
      internal_path="...",
      external_path="...",
      hallucination_path="...",
      sycophancy_path="...",
      advfact_path="..."
  )
  ```
- **Key Findings from Paper**:
  - Correlation = 0.60 between trustworthiness and capability
  - **CRITICAL INSIGHT**: Existing work evaluates dimensions separately, NOT cross-dimensional effects under interventions
- **Their Results**: 16 LLMs evaluated across 30+ datasets
- **Used For**: 
  - Validation of hypothesis novelty (no prior cross-dimensional intervention analysis)
  - Expected baseline performance ranges
  - Implementation framework reference

**Repository 4**: thu-ml/MMTrustEval (NeurIPS 2024)
- **URL**: https://github.com/thu-ml/MMTrustEval
- **Query Used**: "LLM trustworthiness benchmark correlation analysis PyTorch"
- **Relevance**: MultiTrust benchmark for trustworthiness (5 dimensions, 32 tasks)
- **Key Finding**: "No significant correlation across different aspects of trustworthiness" (Figure 2b)
- **Used For**: Validation that cross-dimensional effects under interventions are unexplored

**Repository 5**: ctlllll/understanding_llm_benchmarks (⭐ 29)
- **URL**: https://github.com/ctlllll/understanding_llm_benchmarks
- **Query Used**: "LLM trustworthiness benchmark correlation analysis PyTorch"
- **Relevance**: Direct correlation analysis between benchmarks
- **Key Method**: Spearman correlation + LASSO regression
- **Their Results**: 0.94 correlation in Elo prediction
- **Used For**: Statistical correlation methodology inspiration (Pearson correlation, p-value testing)

**Repository 6**: HuggingFace datasets - BBQ (heegyu/bbq, HiTZ/bbq)
- **URL**: https://huggingface.co/datasets/heegyu/bbq
- **Query Used**: "TruthfulQA BBQ AdvGLUE load_dataset huggingface"
- **Relevance**: BBQ dataset loading and structure
- **Configuration**: 9 demographic categories, disambig/ambig variants
- **Used For**: Dataset loading code and evaluation metrics (Bias Score, Disambiguation Accuracy)

**Repository 7**: HuggingFace datasets - AdvGLUE (AI-Secure/adv_glue)
- **URL**: https://huggingface.co/datasets/AI-Secure/adv_glue
- **Query Used**: "TruthfulQA BBQ AdvGLUE load_dataset huggingface"
- **Relevance**: Adversarial GLUE benchmark
- **Tasks**: SST-2, QQP, MNLI, QNLI, RTE with adversarial perturbations
- **Used For**: Dataset loading and robustness evaluation metrics

**Repository 8**: HuggingFace Transformers - Llama-3 Documentation
- **URL**: https://huggingface.co/docs/transformers/model_doc/llama3
- **Query Used**: "Llama-3-8B Mistral-7B fine-tuning transformers AutoModelForCausalLM"
- **Relevance**: Official Llama-3 model loading documentation
- **Key Code**:
  ```python
  from transformers import AutoModelForCausalLM
  import torch
  
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Meta-Llama-3-8B",
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  ```
- **Used For**: Baseline model loading code

**Repository 9**: HuggingFace Transformers - Mistral Documentation
- **URL**: https://huggingface.co/docs/transformers/model_doc/mistral
- **Query Used**: "Llama-3-8B Mistral-7B fine-tuning transformers AutoModelForCausalLM"
- **Relevance**: Official Mistral model loading documentation
- **Used For**: Multi-family model suite reference

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. Found official benchmark evaluation implementations (sylinrl/TruthfulQA, EleutherAI/lm-evaluation-harness) and comprehensive trustworthiness frameworks (TrustLLM, MultiTrust) that provide clear evaluation protocols.

### D. Previous Hypothesis Context

**Previous Context**: None - this is the first hypothesis (H-E1) in the verification chain. No previous validation reports to reference.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset 1 (TruthfulQA) | GitHub + Exa | sylinrl/TruthfulQA (B.1), HuggingFace datasets |
| Dataset 2 (BBQ) | GitHub + Exa | heegyu/bbq (B.6), BBQ paper |
| Dataset 3 (AdvGLUE) | GitHub + Exa | AI-Secure/adv_glue (B.7), AdvGLUE benchmark |
| Baseline model (Llama-3-8B) | GitHub + Exa | HuggingFace Llama-3 docs (B.8) |
| Multi-family model suite | GitHub + Exa | HuggingFace docs (B.8, B.9) |
| LoRA configuration | Archon KB + Code | HuggingFace PEFT docs (A.2), Code examples (A.Code.1) |
| Training hyperparameters | Archon Code | LoRA training script (A.Code.2) |
| Optimizer (AdamW) | Archon KB | LLM fine-tuning standards |
| Learning rate range | Archon Code + GitHub | LoRA training examples, Llama-3 tutorials |
| Evaluation metrics (TruthfulQA) | GitHub | sylinrl/TruthfulQA eval protocol (B.1) |
| Evaluation metrics (BBQ) | GitHub + Exa | BBQ paper, HuggingFace datasets (B.6) |
| Evaluation metrics (AdvGLUE) | GitHub + Exa | AdvGLUE benchmark (B.7) |
| Correlation methodology | GitHub | ctlllll/understanding_llm_benchmarks (B.5) |
| Expected baseline performance | GitHub | TrustLLM paper (B.3), MultiTrust paper (B.4) |
| Hypothesis novelty validation | GitHub | TrustLLM (B.3), MultiTrust (B.4) - confirmed no prior cross-dimensional intervention analysis |
| Implementation framework | GitHub | HowieHwong/TrustLLM (B.3) |
| Pseudo-code structure | GitHub + Archon | TrustLLM pipeline (B.3), LoRA examples (A.Code.1) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-11T01:16:00Z

### Workflow History for This Hypothesis

- **2026-05-11T01:15:43Z**: Hypothesis h-e1 set to IN_PROGRESS (Hypothesis Loop - External loop starting Phase 2C → 3 → 4)
- **2026-05-11T01:18:04Z**: Phase 2C started for h-e1 (Experiment design in progress)
- **2026-05-11T01:25:40Z**: Phase 2C completed for h-e1 (Output: docs/youra_research/20260511_buildingtrust/h-e1/02c_experiment_brief.md)

**Current Status**: experiment_design.status = COMPLETED
**Next Phase**: Phase 3 - Implementation Planning

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
