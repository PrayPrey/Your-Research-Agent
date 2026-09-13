# Experiment Design: h-m2

**Date:** 2026-05-11
**Author:** Anonymous
**Hypothesis Statement:** Under parameter updates from dimension-targeted interventions, if neural network layers are shared across tasks, then internal representations (attention patterns, hidden states, layer activations) change in ways that affect multiple capabilities simultaneously, because weight changes necessarily impact all downstream computations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates representation changes mechanism.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** ✅ h-m1 (COMPLETED, gate passed)
**Gate Status:** SHOULD_WORK - Correlation between representation changes and performance (p<0.05)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (Parameter updates improve target dimension)

### Gate Condition

**Type:** SHOULD_WORK
**Threshold:** Correlation between representation changes and performance (p<0.05)
**Fail Action:** Document limitation - if no representation changes detected, explore whether dimensions use disentangled subnetworks

**Interpretation:** H-M2 validates the second step of the causal chain. If parameter updates don't cause representation changes, we document this as a limitation and explore alternative mechanisms.

---

## Continuation Context

**This is a continuation experiment from h-m1.**

**Relationship to h-m1:**
- h-m1 validated that parameter updates IMPROVE target dimension (+2.32% on TruthfulQA)
- h-m2 validates that parameter updates CHANGE representations (attention patterns, hidden states)
- Both use same experimental setup for controlled comparison

**Reused from h-m1:**
- Model: GPT-2 (124M parameters)
- LoRA configuration: r=8, alpha=16, target=["c_attn"]
- Training hyperparameters: lr=1e-4, epochs=3, batch=4
- Dataset: TruthfulQA (100 training samples)

**Key Difference:**
- h-m1 focus: Target dimension performance improvement
- h-m2 focus: Internal representation changes measurement

### Previous Hypothesis Results (h-m1)

**Validation File:** docs/youra_research/20260511_buildingtrust/h-m1/04_validation.md

**Key Findings:**
- ✅ LoRA fine-tuning on TruthfulQA successful
- ✅ Mean Δ(Target): +2.32 percentage points (p < 0.001)
- ✅ 100% directional consistency across 3 replicates
- ✅ Gate PASS: All criteria met

**Proven Configuration** (inherited by h-m2):
```yaml
lora:
  rank: 8
  alpha: 16
  target_modules: ["c_attn"]
  trainable_params: 294,912 / 124,734,720 (0.24%)
  
training:
  optimizer: AdamW
  learning_rate: 1e-4
  scheduler: cosine with warmup (10%)
  batch_size: 4
  gradient_accumulation: 2
  epochs: 3
  training_samples: 100
  precision: fp32
```

**Lessons Learned:**
- GPT-2 accessible without authentication
- 3 epochs sufficient for measurable improvement
- LoRA with r=8 shows clear performance signal
- EleutherAI harness + fallback evaluator works reliably

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Representation Analysis Search**
Limited directly applicable results from Archon KB - most results focused on diffusion models and CUDA primitives rather than LLM representation analysis. Key general insight: Hook-based activation extraction is standard in PyTorch.

**Query 2: Layer Activation Extraction**
Found references to PyTorch hook patterns and casting hooks, but implementation details were generic.

**Query 3: LLM Fine-tuning Representation Change**
- Result 1: HuggingFace PEFT LoRA Documentation (https://hf.co/papers/2305.14314)
  - Key insight: LoRA fine-tuning modifies specific weight matrices (attention projections)
  - Representation changes expected in attention layers where LoRA adapters applied

### Archon Code Examples

**Query 1: Activation Extraction PyTorch Hook**
- Example 1: HuggingFace Accelerate Layerwise Casting Hooks
  ```python
  from accelerate.hooks import attach_layerwise_casting_hooks
  attach_layerwise_casting_hooks(model, storage_dtype=torch.float8_e4m3fn, 
                                 compute_dtype=torch.bfloat16)
  ```
  - Pattern: Register hooks on model layers for activation interception
  - Insight: Hooks can both read and modify layer outputs

### Exa GitHub Implementations

**Query 1: LLM Representation Analysis**

**Repository 1**: TransformerLensOrg/TransformerLens (⭐ Major interpretability framework)
- **URL**: https://github.com/TransformerLensOrg/TransformerLens
- **Relevance**: **CRITICAL** - Industry-standard library for LLM activation extraction and analysis
- **Priority**: ⭐⭐⭐ HIGHEST - Designed specifically for this exact use case
- **Architecture**: Hook-based activation interception for all transformer layers
- **Key Features**:
  - `run_with_cache()` - Automatically extracts all intermediate activations
  - `run_with_hooks()` - Custom hooks for reading/modifying activations
  - Pre-integrated with HuggingFace models (GPT-2, Llama, etc.)
  - Activation patching and causal intervention built-in
- **Key Code Pattern**:
  ```python
  from transformer_lens import HookedTransformer
  
  model = HookedTransformer.from_pretrained("gpt2")
  
  # Extract all activations
  logits, cache = model.run_with_cache(tokens)
  
  # Access specific layer activations
  layer_0_attn = cache["blocks.0.attn.hook_pattern"]  # Attention patterns
  layer_0_hidden = cache["blocks.0.hook_resid_post"]  # Hidden states
  
  # Custom hook for modification
  def extract_hook(activation, hook):
      stored_activations.append(activation.clone())
      return activation
  
  model.run_with_hooks(tokens, fwd_hooks=[("blocks.0.attn.hook_pattern", extract_hook)])
  ```
- **Hook Points Available**:
  - `blocks.{i}.hook_resid_pre` - Residual stream input
  - `blocks.{i}.attn.hook_pattern` - Attention patterns
  - `blocks.{i}.hook_resid_post` - Residual stream output
  - `blocks.{i}.attn.hook_result` - Attention output
- **Training Integration**: Compatible with PEFT LoRA models
- **Documentation**: Extensive tutorials at transformerlensorg.github.io
- **Used For**: Primary implementation framework for activation extraction

**Repository 2**: davidbau/baukit (⭐ 251, David Bau's research toolkit)
- **URL**: https://github.com/davidbau/baukit
- **Relevance**: Lightweight alternative for activation tracing
- **Priority**: ⭐⭐ HIGH - Simpler API than TransformerLens
- **Architecture**: Context manager for hook-based tracing
- **Key Code**:
  ```python
  from baukit import Trace
  
  # Extract single layer activation
  with Trace(model, 'layer.name') as ret:
      _ = model(input)
      representation = ret.output  # Pre-intervention activation
  
  # Extract with modification
  def edit_fn(output, layer):
      return output * 0.5  # Modify activation
  
  with Trace(model, 'layer.name', edit_output=edit_fn) as ret:
      _ = model(input)
      modified_representation = ret.output
  ```
- **Features**:
  - `retain_input=True` - Also captures layer input
  - `clone=True` - Copy activation (avoid in-place modifications)
  - `detach=True` - Detach from computation graph
  - `edit_output=fn` - Modify activation before passing to next layer
- **Use Case**: Simple activation extraction without heavy dependencies

**Query 2: Activation Extraction PyTorch Hook**

**Repository 3**: PyTorch Official Hooks Tutorial
- **URL**: https://pytorch.org/tutorials/
- **Relevance**: Standard PyTorch hook patterns
- **Key Pattern**:
  ```python
  activations = {}
  
  def get_activation(name):
      def hook(model, input, output):
          activations[name] = output.detach()
      return hook
  
  model.layer1.register_forward_hook(get_activation('layer1'))
  model.layer2.register_forward_hook(get_activation('layer2'))
  
  output = model(x)
  # activations now contains layer1 and layer2 outputs
  ```

**Query 3: CKA Representation Similarity**

**Repository 4**: ryusudol/Centered-Kernel-Alignment (⭐ 5, Latest 2026)
- **URL**: https://github.com/ryusudol/Centered-Kernel-Alignment
- **Relevance**: **HIGHLY RELEVANT** - Fastest CKA implementation with GPU support
- **Priority**: ⭐⭐⭐ CRITICAL - Purpose-built for representation similarity
- **Key Features**:
  - 44x faster than baseline CKA implementations
  - GPU-accelerated with vectorized operations
  - Efficient memory management
  - HuggingFace model support
- **Installation**: `pip install pytorch-cka`
- **Key Code**:
  ```python
  from cka import compute_cka
  from torch.utils.data import DataLoader
  
  # Define layers to compare
  layers = [
      'layer1.0.conv1',
      'layer2.0.conv1',
      'layer3.0.conv1',
      'layer4.0.conv1',
  ]
  
  # Compute CKA between pre and post fine-tuning models
  cka_matrix = compute_cka(
      model_pre,
      model_post,
      [dataloader],
      layers=layers,
      device=device,
  )
  ```
- **Visualization**: Built-in heatmap and line chart plotting
- **Used For**: Primary CKA computation tool

**Repository 5**: RistoAle97/centered-kernel-alignment (⭐ 66)
- **URL**: https://github.com/RistoAle97/centered-kernel-alignment
- **Relevance**: Alternative CKA implementation with minibatch support
- **Installation**: `pip install ckatorch`
- **Key Formula**: Unbiased HSIC estimator for minibatch CKA
  ```
  CKA(K, L) = HSIC(K, L) / sqrt(HSIC(K, K) * HSIC(L, L))
  ```
- **Advantage**: Memory-efficient minibatch computation (doesn't require full dataset in memory)

**Repository 6**: jayroxis/CKA-similarity (⭐ 97)
- **URL**: https://github.com/jayroxis/CKA-similarity
- **Relevance**: CUDA-accelerated CKA implementation
- **Performance**: 15.3s vs 3min 8s (PyTorch vs Numpy)
- **Used For**: Reference implementation for CKA formula validation

**Repository 7**: Kornblith et al. (2019) - Original CKA Paper
- **URL**: http://proceedings.mlr.press/v97/kornblith19a/kornblith19a.pdf
- **Paper**: "Similarity of Neural Network Representations Revisited"
- **Key Insight**: CKA is invariant to orthogonal transformations and isotropic scaling
- **Benchmark**: Used to compare ResNet representations across training runs

### 🎯 Implementation Priority Assessment

**CRITICAL: This is NOT paper reproduction - this is hypothesis-driven mechanism validation**

**Priority Assessment:**
1. ⭐⭐⭐ **HIGHEST**: TransformerLens (activation extraction from LLMs)
2. ⭐⭐⭐ **CRITICAL**: pytorch-cka (CKA similarity computation)
3. ⭐⭐ **HIGH**: baukit (lightweight alternative for activation tracing)
4. ⭐ **REFERENCE**: Other CKA implementations (formula validation)

**Recommended Implementation Path:**
- **Primary**: TransformerLens + pytorch-cka
  - Rationale: TransformerLens designed for LLM activation extraction, pytorch-cka is fastest CKA implementation
  - Integration: TransformerLens extracts activations → pytorch-cka computes similarity
  - Sources: TransformerLens docs + pytorch-cka GitHub
  
- **Fallback**: baukit + ckatorch (minibatch CKA)
  - Rationale: Simpler API if TransformerLens integration issues
  - Advantage: Memory-efficient minibatch CKA computation
  
- **Justification**: 
  - TransformerLens is industry-standard for LLM interpretability research
  - Pre-integrated with HuggingFace models (GPT-2 from h-m1)
  - pytorch-cka provides GPU-accelerated CKA with 44x speedup
  - Both libraries actively maintained (2026 releases)
  - No custom implementation needed - production-ready tools available

### Code Analysis (Serena MCP)

*Not needed* - TransformerLens and pytorch-cka provide clear, well-documented APIs. Implementation patterns are straightforward:
1. Load model with TransformerLens wrapper
2. Extract pre-intervention activations with `run_with_cache()`
3. Fine-tune model (reuse h-m1 LoRA configuration)
4. Extract post-intervention activations with `run_with_cache()`
5. Compute CKA similarity with `compute_cka()` for each layer pair
6. Correlate representation changes with performance changes

---

## Experiment Specification

### Dataset

**Primary Dataset**: TruthfulQA (Target Dimension - inherited from h-m1)
- **Type**: standard (established benchmark)
- **Source**: HuggingFace datasets (truthful_qa)
- **Task**: Multiple-choice question answering (truthfulness evaluation)
- **Statistics**: 817 questions, MC2 format
- **Hypothesis Fit**: Same dataset as h-m1 for controlled comparison - we measure representation changes caused by fine-tuning on TruthfulQA

**Loading Information** (for Phase 4 download):
- Method: EleutherAI LM Evaluation Harness
- Identifier: `truthfulqa_mc2`
- Code: 
  ```python
  from lm_eval import evaluator
  results = evaluator.simple_evaluate(
      model="hf-causal",
      model_args="pretrained=<model_path>",
      tasks=["truthfulqa_mc2"],
      num_fewshot=0
  )
  ```

**Training Subset**: 100 samples (same as h-m1)
- **Rationale**: Proven sufficient in h-m1 for measurable performance improvement
- **Selection**: Random sample from TruthfulQA for fine-tuning

### Models

#### Baseline Model

**Architecture**: GPT-2 (124M parameters) - inherited from h-m1
- **Type**: Causal transformer language model
- **Rationale**: Controlled comparison with h-m1 - same model, same intervention
- **Configuration**: 
  - Layers: 12
  - Hidden size: 768
  - Attention heads: 12
  - Context length: 1024

**Loading Information** (for Phase 4 download):
- Method: TransformerLens HookedTransformer
- Identifier: `gpt2`
- Code:
  ```python
  from transformer_lens import HookedTransformer
  
  # Load GPT-2 with TransformerLens for activation extraction
  model = HookedTransformer.from_pretrained("gpt2", device="cuda")
  
  # TransformerLens provides hook points for all layers:
  # - blocks.{i}.hook_resid_pre: residual stream input
  # - blocks.{i}.attn.hook_pattern: attention patterns  
  # - blocks.{i}.hook_resid_post: residual stream output
  ```

#### Proposed Model

**Architecture:** Baseline + [Representation Analysis Mechanism]

**Core Mechanism Implementation:**

```python
# Core Mechanism: Representation Change Analysis via Activation Extraction + CKA
# Based on: TransformerLens (activation extraction) + pytorch-cka (similarity)

from transformer_lens import HookedTransformer
from cka import compute_cka
from peft import LoraConfig, get_peft_model
import torch

class RepresentationChangeAnalyzer:
    """
    Measures representation changes in neural network layers caused by
    targeted fine-tuning interventions.
    
    H-M2 Tests: Correlation between representation changes and performance (p<0.05)
    """
    def __init__(self, base_model_name="gpt2"):
        # Load model with TransformerLens for activation extraction
        self.model = HookedTransformer.from_pretrained(base_model_name)
        
        # Define layers to analyze (attention and residual stream)
        self.layers_to_analyze = [
            f"blocks.{i}.attn.hook_pattern" for i in range(12)  # Attention patterns
        ] + [
            f"blocks.{i}.hook_resid_post" for i in range(12)  # Hidden states
        ]
        
    def extract_representations_pre_intervention(self, eval_inputs):
        """
        Extract layer activations BEFORE fine-tuning intervention.
        
        Args:
            eval_inputs: Evaluation dataset inputs (tokenized)
            
        Returns:
            dict: Pre-intervention activations for each layer
        """
        pre_activations = {}
        
        # Use TransformerLens cache to extract all activations
        _, cache = self.model.run_with_cache(eval_inputs)
        
        for layer_name in self.layers_to_analyze:
            pre_activations[layer_name] = cache[layer_name].detach().cpu()
        
        return pre_activations
    
    def apply_intervention(self, target_dataset, lora_config):
        """
        Apply LoRA fine-tuning intervention (same as h-m1).
        
        Args:
            target_dataset: TruthfulQA training data (100 samples)
            lora_config: LoRA configuration from h-m1
        """
        # Convert TransformerLens model to HuggingFace for PEFT compatibility
        hf_model = self.model.to_hf_model()
        
        # Apply LoRA adapters
        lora_model = get_peft_model(hf_model, lora_config)
        
        # Fine-tune (3 epochs, lr=1e-4, batch=4 - from h-m1)
        # Training loop here...
        
        # Reload as TransformerLens model with trained LoRA weights
        self.model = HookedTransformer.from_pretrained(
            "gpt2", 
            state_dict=lora_model.state_dict()
        )
    
    def extract_representations_post_intervention(self, eval_inputs):
        """
        Extract layer activations AFTER fine-tuning intervention.
        
        Args:
            eval_inputs: Same evaluation inputs as pre-intervention
            
        Returns:
            dict: Post-intervention activations for each layer
        """
        post_activations = {}
        
        _, cache = self.model.run_with_cache(eval_inputs)
        
        for layer_name in self.layers_to_analyze:
            post_activations[layer_name] = cache[layer_name].detach().cpu()
        
        return post_activations
    
    def compute_representation_similarity(self, pre_acts, post_acts):
        """
        Compute CKA similarity between pre and post intervention representations.
        
        Args:
            pre_acts: Pre-intervention activations
            post_acts: Post-intervention activations
            
        Returns:
            dict: CKA similarity scores for each layer (1.0 = identical, 0.0 = completely different)
        """
        from cka import cka_score
        
        cka_scores = {}
        
        for layer_name in self.layers_to_analyze:
            # Flatten activations for CKA computation
            pre = pre_acts[layer_name].flatten(1)  # (batch, features)
            post = post_acts[layer_name].flatten(1)
            
            # Compute CKA similarity
            cka = cka_score(pre, post)
            cka_scores[layer_name] = cka.item()
        
        return cka_scores
    
    def correlate_with_performance(self, cka_scores, performance_change):
        """
        Correlate representation changes with performance changes.
        
        Args:
            cka_scores: CKA similarity for each layer (lower = more change)
            performance_change: Δ(TruthfulQA) from h-m1 baseline
            
        Returns:
            float: Correlation coefficient between representation change and performance
        """
        from scipy.stats import pearsonr
        
        # Convert CKA similarity to dissimilarity (change magnitude)
        rep_changes = [1.0 - cka for cka in cka_scores.values()]
        
        # Compute correlation
        # Hypothesis: Layers with larger representation changes correlate with performance improvement
        correlation, p_value = pearsonr(rep_changes, [performance_change] * len(rep_changes))
        
        return correlation, p_value

# Integration: Full pipeline
# 1. Extract pre-intervention representations
# 2. Apply LoRA fine-tuning (h-m1 configuration)
# 3. Extract post-intervention representations
# 4. Compute CKA similarity (representation change magnitude)
# 5. Correlate with TruthfulQA performance change from h-m1
```

### Training Protocol

**Intervention Method**: LoRA (Low-Rank Adaptation) fine-tuning - **INHERITED FROM h-m1**

**LoRA Configuration** (Proven in h-m1):
  - Rank: 8
  - Alpha: 16
  - Target modules: ["c_attn"] (GPT-2 attention layers)
  - Dropout: 0.1
  - Trainable parameters: 294,912 / 124,734,720 (0.24%)
  - **Source**: h-m1 validation results

**Optimizer**: AdamW
  - Parameters: default (betas=(0.9, 0.999), eps=1e-8)
  - **Source**: h-m1 validation results

**Learning Rate**: 1e-4
  - Schedule: Cosine annealing with warmup (10%)
  - **Source**: h-m1 validation results

**Batch Size**: 4 per device
  - Gradient accumulation: 2 (effective batch=8)
  - **Source**: h-m1 validation results

**Epochs**: 3
  - **Source**: h-m1 validation results (proven sufficient)

**Training Samples**: 100 (per replicate)
  - **Source**: h-m1 validation results

**Loss Function**: Causal language modeling (next-token prediction)

**Precision**: FP32
  - **Rationale**: h-m1 used fp32 successfully

**Replicates**: 3 (seeds: [42, 43, 44])
  - **Rationale**: Same seeds as h-m1 for controlled comparison
  - Enables measuring representation change consistency across replicates

**Key Difference from h-m1**:
- h-m1: Only measured performance improvement
- h-m2: Measures both performance AND representation changes (attention patterns, hidden states)

### Evaluation

**Primary Metric**: Representation Change Magnitude (1 - CKA similarity)

**Evaluation Protocol**:
1. **Pre-intervention**: Extract layer activations from base GPT-2 on evaluation set
2. **Intervention**: Apply LoRA fine-tuning (h-m1 configuration)
3. **Post-intervention**: Extract layer activations from fine-tuned model on same evaluation set
4. **Representation Change**: Compute CKA similarity for each layer
5. **Performance Change**: Load Δ(TruthfulQA) from h-m1 results (+2.32%)

**CKA Similarity Metric**:
- **Formula**: CKA(K, L) = HSIC(K, L) / sqrt(HSIC(K, K) * HSIC(L, L))
- **Range**: [0, 1] where 1.0 = identical representations, 0.0 = completely different
- **Interpretation**: (1 - CKA) measures representation change magnitude
- **Source**: Kornblith et al. (2019), implemented in pytorch-cka

**Layers to Analyze**:
- **Attention Patterns**: `blocks.{i}.attn.hook_pattern` (12 layers)
  - Shape: (batch, n_heads, seq_len, seq_len)
  - Measures: How attention distributions change after fine-tuning
- **Hidden States**: `blocks.{i}.hook_resid_post` (12 layers)
  - Shape: (batch, seq_len, d_model)
  - Measures: How residual stream representations change

**Statistical Analysis**:
- **Test**: Correlation between representation change and performance change
- **Method**: Pearson correlation coefficient
- **Null Hypothesis**: No correlation between representation changes and performance (ρ = 0)
- **Alternative**: Significant correlation exists (ρ ≠ 0)
- **Significance**: p < 0.05 (two-tailed)

**Success Criteria** (Gate: SHOULD_WORK):
- **Primary**: Significant correlation (p<0.05) between representation change magnitude and performance improvement
- **Secondary**: Representation changes detectable in >50% of layers (CKA < 1.0)
- **Interpretation**: If correlation found → mechanism validated; If not found → document as limitation

**Expected Results** (from h-m1 context):
- TruthfulQA performance: +2.32% improvement (h-m1 validated)
- Representation changes expected in attention layers (c_attn has LoRA adapters)
- Smaller changes expected in non-adapted layers (due to downstream propagation)

**Evaluation Set**: 
- Same 817 TruthfulQA questions used for baseline evaluation
- **Rationale**: Ensures representation changes measured on same distribution as performance

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Representation similarity analysis
- Libraries: 
  - TransformerLens: Activation extraction
  - pytorch-cka: CKA computation
  - scipy.stats: Correlation analysis
- Code:
  ```python
  from transformer_lens import HookedTransformer
  from cka import cka_score
  from scipy.stats import pearsonr
  
  # Extract representations
  model = HookedTransformer.from_pretrained("gpt2")
  _, pre_cache = model.run_with_cache(eval_tokens)
  
  # After fine-tuning...
  _, post_cache = model.run_with_cache(eval_tokens)
  
  # Compute CKA for each layer
  cka_scores = {}
  for layer in layers_to_analyze:
      pre_act = pre_cache[layer].flatten(1)
      post_act = post_cache[layer].flatten(1)
      cka_scores[layer] = cka_score(pre_act, post_act)
  
  # Correlate with performance change
  rep_changes = [1.0 - cka for cka in cka_scores.values()]
  perf_change = 0.0232  # From h-m1
  correlation, p_value = pearsonr(rep_changes, [perf_change] * len(rep_changes))
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Correlation between representation changes and performance

#### Additional Figures (LLM Autonomous)

Based on MECHANISM hypothesis and representation analysis, recommended visualizations:

1. **CKA Heatmap**: Pre/Post similarity across all 12 layers (attention + hidden states)
   - X-axis: Layer index (0-11)
   - Y-axis: Representation type (attention patterns, hidden states)
   - Color: CKA similarity score (1.0 = no change, 0.0 = complete change)

2. **Representation Change Magnitude**: Bar chart showing (1 - CKA) per layer
   - X-axis: Layer index
   - Y-axis: Change magnitude
   - Highlights: Layers with LoRA adapters vs. non-adapted layers

3. **Layer-wise Change Progression**: Line plot showing representation changes across depth
   - X-axis: Layer depth (0-11)
   - Y-axis: Representation change magnitude
   - Shows: Whether changes propagate or localize

4. **Attention Pattern Change Examples**: Visualization of attention patterns before/after
   - Side-by-side attention heatmaps for selected layers
   - Shows: Qualitative changes in attention distributions

5. **Correlation Scatter**: Representation change vs. performance improvement
   - X-axis: Layer representation change magnitude
   - Y-axis: Performance contribution (if measurable per-layer)
   - Regression line: Shows correlation strength

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Representation changes detectable (cosine similarity Δ > 0)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: HuggingFace PEFT LoRA Documentation
- **Type**: Knowledge base article
- **URL**: https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora
- **Query Used**: "LLM fine-tuning representation change measurement"
- **Relevance**: LoRA fine-tuning modifies specific weight matrices
- **Key Insights**:
  - LoRA adapters applied to attention projection layers
  - Weight changes localized to target modules
  - Representation changes expected in adapted layers
- **Used For**: Understanding where representation changes occur

### Archon Code Examples

**Code Source 1**: HuggingFace Accelerate Hooks
- **Query Used**: "activation extraction PyTorch hook"
- **Key Code**:
  ```python
  from accelerate.hooks import attach_layerwise_casting_hooks
  attach_layerwise_casting_hooks(model, storage_dtype=torch.float8_e4m3fn)
  ```
- **Used For**: Hook-based activation extraction pattern

### B. GitHub Implementations (Exa)

**Repository 1**: TransformerLensOrg/TransformerLens (⭐ Major framework)
- **URL**: https://github.com/TransformerLensOrg/TransformerLens
- **Query Used**: "LLM representation analysis attention hidden states PyTorch GitHub"
- **Relevance**: **CRITICAL** - Industry-standard LLM interpretability library
- **Priority**: ⭐⭐⭐ HIGHEST - Designed for this exact use case
- **Key Features**:
  - `run_with_cache()` - Automatic activation extraction
  - Pre-integrated with HuggingFace models (GPT-2, Llama, etc.)
  - Hook points for all transformer layers
  - Activation patching and causal intervention
- **Key Code**:
  ```python
  from transformer_lens import HookedTransformer
  
  model = HookedTransformer.from_pretrained("gpt2")
  logits, cache = model.run_with_cache(tokens)
  
  # Access layer activations
  attn_patterns = cache["blocks.0.attn.hook_pattern"]
  hidden_states = cache["blocks.0.hook_resid_post"]
  ```
- **Configuration**: Compatible with PEFT LoRA models
- **Documentation**: https://transformerlensorg.github.io/TransformerLens/
- **Used For**: Primary activation extraction framework

**Repository 2**: davidbau/baukit (⭐ 251)
- **URL**: https://github.com/davidbau/baukit
- **Query Used**: "activation extraction PyTorch hook fine-tuning representation change"
- **Relevance**: Lightweight activation tracing toolkit
- **Priority**: ⭐⭐ HIGH - Simpler alternative to TransformerLens
- **Key Code**:
  ```python
  from baukit import Trace
  
  with Trace(model, 'layer.name') as ret:
      _ = model(input)
      representation = ret.output
  ```
- **Features**:
  - `retain_input=True` - Capture layer inputs
  - `clone=True` - Copy activations
  - `edit_output=fn` - Modify activations
- **Used For**: Fallback activation extraction method

**Repository 3**: ryusudol/Centered-Kernel-Alignment (⭐ 5, 2026)
- **URL**: https://github.com/ryusudol/Centered-Kernel-Alignment
- **Query Used**: "cosine similarity CKA representation analysis neural network layers"
- **Relevance**: **CRITICAL** - Fastest CKA implementation with GPU acceleration
- **Priority**: ⭐⭐⭐ HIGHEST - Purpose-built for representation similarity
- **Key Features**:
  - 44x faster than baseline CKA
  - GPU-accelerated vectorized operations
  - HuggingFace model support
  - Built-in visualization (heatmaps, line charts)
- **Installation**: `pip install pytorch-cka`
- **Key Code**:
  ```python
  from cka import compute_cka
  
  layers = ['layer1', 'layer2', 'layer3']
  cka_matrix = compute_cka(
      model_pre,
      model_post,
      [dataloader],
      layers=layers,
      device=device,
  )
  ```
- **Performance**: 44x speedup on ResNet-18 (18 layers, H100 GPU)
- **Used For**: Primary CKA computation tool

**Repository 4**: RistoAle97/centered-kernel-alignment (⭐ 66)
- **URL**: https://github.com/RistoAle97/centered-kernel-alignment
- **Query Used**: "cosine similarity CKA representation analysis neural network layers"
- **Relevance**: Alternative CKA with minibatch support
- **Priority**: ⭐⭐ MEDIUM - Memory-efficient alternative
- **Installation**: `pip install ckatorch`
- **Key Formula**: Unbiased HSIC estimator
  ```
  HSIC_1(K, L) = (1 / (n(n-3))) * (tr(K̃L̃) + (1^T K̃ 1 1^T L̃ 1) / ((n-1)(n-2)))
  CKA(K, L) = HSIC(K, L) / sqrt(HSIC(K, K) * HSIC(L, L))
  ```
- **Advantage**: Doesn't require full dataset in memory
- **Used For**: Fallback if memory constraints

**Repository 5**: jayroxis/CKA-similarity (⭐ 97)
- **URL**: https://github.com/jayroxis/CKA-similarity
- **Query Used**: "CKA centered kernel alignment PyTorch implementation GitHub"
- **Relevance**: CUDA-accelerated CKA reference implementation
- **Performance**: 15.3s vs 3min 8s (PyTorch vs Numpy)
- **Used For**: Formula validation reference

**Repository 6**: Kornblith et al. (2019) - Original CKA Paper
- **URL**: http://proceedings.mlr.press/v97/kornblith19a/kornblith19a.pdf
- **Paper**: "Similarity of Neural Network Representations Revisited"
- **Key Findings**:
  - CKA invariant to orthogonal transformations and isotropic scaling
  - More robust than previous similarity metrics (SVCCA, PWCCA)
  - Successfully compared ResNet representations across training
- **Used For**: Theoretical foundation and metric validation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - TransformerLens and pytorch-cka provide clear, well-documented APIs with straightforward integration patterns.

### D. Previous Hypothesis Context

**Hypothesis**: h-m1 (Parameter Updates Improve Target Dimension)
- **Status**: COMPLETED (Gate: PASS)
- **Validation File**: docs/youra_research/20260511_buildingtrust/h-m1/04_validation.md
- **Key Results**:
  - Model: GPT-2 with LoRA (r=8, alpha=16, target=["c_attn"])
  - Training: 3 epochs, batch=4, lr=1e-4, 100 samples
  - Performance: +2.32% TruthfulQA MC2 (p < 0.001)
  - Replication: 100% directional consistency (3/3 replicates)
  - Gate: PASS (all criteria exceeded)
- **Optimal Configuration Inherited**:
  - LoRA rank=8, alpha=16, target=["c_attn"]
  - Learning rate=1e-4, cosine schedule with warmup
  - Batch size=4, gradient accumulation=2
  - Epochs=3, training samples=100
  - Seeds=[42, 43, 44]
  - Precision=fp32
- **Used For**: Exact intervention replication for controlled comparison

### E. Source-to-Specification Traceability

| Specification Component | Source(s) |
|-------------------------|-----------|
| Activation extraction framework | TransformerLens (GitHub) |
| CKA similarity computation | pytorch-cka (GitHub) |
| LoRA configuration | h-m1 validation results |
| Training protocol | h-m1 validation results (inherited) |
| Dataset (TruthfulQA) | h-m1 validation results |
| Model (GPT-2) | h-m1 validation results |
| Statistical analysis (Pearson) | Standard mechanism validation |
| CKA formula | Kornblith et al. (2019) paper |
| Hook-based extraction pattern | TransformerLens docs + baukit |
| Layer naming convention | TransformerLens canonical hooks |
| Expected performance change | h-m1 validation (+2.32%) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-11T07:10:42+00:00

### Workflow History for This Hypothesis

- **2026-05-11T07:06:51** - Hypothesis h-m2 set to IN_PROGRESS
- **2026-05-11T07:10:42** - Phase 2C started (Experiment design)

**Next:** Continue with implementation research

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
