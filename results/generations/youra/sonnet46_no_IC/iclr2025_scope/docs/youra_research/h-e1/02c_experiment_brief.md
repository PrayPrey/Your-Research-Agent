# Experiment Design: H-E1

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under pre-trained transformers {BERT-base-uncased, DeBERTa-v3-base, ViT-base-patch16-224}, erank(W₀) = exp(H(σ/‖σ‖₁)) computed fp32 before fine-tuning shows Pearson r ≥ 0.65 (one-tailed p < 0.05) with PARA oracle ranks in ≥2/3 model families.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: Pearson r ≥ 0.65 (one-tailed p < 0.05) for ≥2/3 model families. Failure stops the entire verification chain (H-M1, H-M2, H-M3 all depend on H-E1 oracle artifacts).

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous hypothesis results to load.

### Previous Hypothesis Results (if applicable)
*None — H-E1 is the foundation hypothesis with no prerequisites.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design (LoRA rank selection)**
- **Source**: HuggingFace PEFT docs — LoRA conceptual guide
  - Dataset: GLUE (standard NLU benchmark), CIFAR-10 (image classification)
  - Hyperparameters: LoraConfig with `r`, `lora_alpha`, `target_modules`
  - Key insight: PEFT library provides `get_peft_model` for seamless LoRA wrapping; per-layer rank assignment requires custom `LoraConfig` per module
- **Source**: HuggingFace PEFT GitHub (`huggingface/peft`)
  - Key insight: `model.add_adapter(lora_config, adapter_name="lora_r8")` supports multiple named adapters — enables per-rank oracle sweep without re-loading model

**Query 2: Implementation challenges (GLUE/BERT fine-tuning)**
- **Source**: HuggingFace PEFT library
  - LoRA is standard for BERT/DeBERTa GLUE fine-tuning
  - `target_modules` for DeBERTa-v3: `["query_proj", "key_proj", "value_proj"]` (FIM-LoRA paper, LAARA paper confirm this)
  - FP32 required for DeBERTa fine-tuning (FP16 causes classifier overflow — confirmed by FIM-LoRA paper)
- **Source**: AdaLoRA paper / `QingruZhang/AdaLoRA`
  - Standard GLUE hyperparameters: AdamW, lr ∈ {5e-5, 8e-5, 1e-4, 2e-4}, batch=32
  - DeBERTa-v3-base baseline MNLI: 90.0 acc with uniform LoRA r=8

**Query 3: GLUE benchmark baselines**
- **Source**: LoRA paper (microsoft/LoRA), AdaLoRA paper
  - Uniform r=8: MNLI ~84.5 (BERT-base), ~90.0 (DeBERTa-v3-base)
  - Expected validation accuracy range for MNLI: 83–91% depending on model and rank

### Archon Code Examples

**Add PEFT LoRA Adapter (HuggingFace PEFT)**
```python
from peft import LoraConfig, get_peft_model
peft_config = LoraConfig(r=8, lora_alpha=16, target_modules=["query", "value"], task_type="SEQ_CLS")
model = get_peft_model(model, peft_config)
```
- **Pattern**: `get_peft_model` wraps base model; supports `print_trainable_parameters()`
- **Insight**: For oracle sweep, instantiate fresh LoraConfig per rank r∈{4,8,16,32,64} and re-wrap model

### Exa GitHub Implementations

**Repository 1: `jonathanc.net/blog/llm-effective-rank` (SVD + erank analysis)**
- **URL**: https://jonathanc.net/blog/llm-effective-rank
- **Relevance**: Demonstrates exact fp32 per-layer SVD loop over transformer weight matrices with `torch.linalg.svd`
- **Key Code**:
  ```python
  for i in range(model.config.num_hidden_layers):
      layer = model.model.layers[i].self_attn
      with torch.no_grad():
          _, S_q, _ = torch.linalg.svd(q_proj_weight.float(), full_matrices=False)
          _, S_k, _ = torch.linalg.svd(k_proj_weight.float(), full_matrices=False)
  ```
- **Insight**: Use `.float()` cast before SVD for fp32 precision; iterate over layer indices to build per-layer erank table

**Repository 2: `gist.github.com/khanghy1000` — `calculate_effective_rank_lora.py`**
- **URL**: https://gist.github.com/khanghy1000/5a3ae7473554542ed0bcd787b07d886c
- **Relevance**: EXACT erank formula implementation matching hypothesis definition
- **Key Code**:
  ```python
  def calculate_effective_rank(matrix: torch.Tensor, eps: float = 1e-10) -> float:
      S = torch.linalg.svdvals(matrix)
      S = S[S > eps]
      if S.numel() == 0:
          return 0.0
      p = S / torch.sum(S)
      entropy = -torch.sum(p * torch.log(p))
      effective_rank = torch.exp(entropy)
      return effective_rank.item()
  ```
- **Training Config**: N/A (analysis script)
- **Insight**: `svdvals` is more efficient than full `svd` when only singular values needed; eps filter removes numerical noise

**Repository 3: `microsoft/LoRA` — NLU examples with DeBERTa v2**
- **URL**: https://github.com/microsoft/LoRA
- **Relevance**: Official LoRA implementation with DeBERTa GLUE fine-tuning examples
- **Architecture**: Standard LoRA layer wrapping with `lora.Linear(in_features, out_features, r=r)`
- **Key insight**: `lora.mark_only_lora_as_trainable(model)` freezes base weights; oracle sweep needs all non-target layers frozen at r=8 baseline

**Repository 4: `QingruZhang/AdaLoRA` — DeBERTa-v3-base GLUE**
- **URL**: https://github.com/QingruZhang/AdaLoRA
- **Relevance**: Confirmed GLUE hyperparameters for DeBERTa-v3-base
- **Training Config**:
  - Optimizer: AdamW, lr=2e-4, wd not specified (use 1e-2 default)
  - Batch size: 32 (effective; gradient accumulation if needed)
  - Epochs: 10 (MNLI, large tasks); FP32 for DeBERTa
  - Target modules: `query_proj`, `key_proj`, `value_proj`
- **Results**: DeBERTa-v3-base MNLI 90.4 (AdaLoRA, 0.3M params)

**Repository 5: `sidhantls/adaptive-rank-selection-svd`**
- **URL**: https://github.com/sidhantls/adaptive-rank-selection-svd
- **Relevance**: Adaptive rank selection via SVD-based importance scoring — pattern for per-layer rank sweep
- **Insight**: Uses truncated SVD to assess layer-wise rank importance; confirms SVD-based rank analysis is tractable on transformer weight matrices

**Serena Analysis Needed**: false — code from Exa results is sufficiently clear.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

No existing PARA oracle sweep implementation found in public repos. This experiment is **novel** — no paper author's implementation exists to reproduce. The closest references are:
- AdaLoRA (dynamic rank allocation during training via SVD importance) — NOT the same as per-layer marginal oracle sweep
- FIM-LoRA (calibration-time rank allocation) — NOT the same

**Recommended Implementation Path:**
- Primary: Custom implementation based on HuggingFace PEFT `get_peft_model` + `calculate_effective_rank` from khanghy1000 gist
- Fallback: Use `microsoft/LoRA` loralib with manual per-layer rank configuration
- Justification: No existing PARA oracle sweep code — must implement from scratch using PEFT library primitives. The erank computation code is directly available and verified.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. The erank formula from khanghy1000 gist and the SVD per-layer loop from jonathanc.net blog provide complete implementation reference without requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Multi-Dataset Specification** (from Phase 2A, confirmed in Phase 2B):

#### Dataset 1: GLUE MNLI (Primary NLP Oracle Dataset)
- **Name**: GLUE Multi-Genre Natural Language Inference (MNLI)
- **Type**: standard
- **Source**: HuggingFace datasets
- **Statistics**: 392,702 train / 9,815 validation-matched / 9,832 validation-mismatched
- **Task**: 3-class NLI (entailment, neutral, contradiction)
- **Evaluation split**: validation-matched (9,815 samples) — full split, no subsampling
- **Preprocessing**: tokenize with model tokenizer, max_length=128 (BERT/DeBERTa), truncation=True, padding="max_length"
- **Augmentation**: None (standard GLUE evaluation)
- **Rationale**: 392k training samples ensures stable 3-epoch oracle runs; sufficient validation set for accurate accuracy estimation per oracle rank

#### Dataset 2: CIFAR-10 (Vision Oracle Dataset)
- **Name**: CIFAR-10
- **Type**: standard
- **Source**: HuggingFace datasets or torchvision
- **Statistics**: 50,000 train / 10,000 test
- **Task**: 10-class image classification
- **Evaluation split**: full test set (10,000 samples)
- **Preprocessing**: resize to 224×224 (ViT-base requirement), normalize with ImageNet mean=[0.485,0.456,0.406] std=[0.229,0.224,0.225]
- **Augmentation**: RandomHorizontalFlip + RandomCrop(32, padding=4) for training only
- **Rationale**: Cross-architecture validation with ViT-base; standard benchmark with fixed splits

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets` library
- Identifier: `"glue"` / `"mnli"` for GLUE MNLI; `"uoft-cs/cifar10"` or `torchvision.datasets.CIFAR10` for CIFAR-10
- Code:
  ```python
  from datasets import load_dataset
  mnli = load_dataset("glue", "mnli")  # train/validation_matched/validation_mismatched
  cifar10 = load_dataset("uoft-cs/cifar10")  # train/test
  # Alternative for CIFAR-10:
  # import torchvision; torchvision.datasets.CIFAR10(root='./data', train=True, download=True)
  ```

### Models

#### Baseline Model

**Three Pre-trained Models** (all instantiated with frozen base weights for erank computation):

| Model | HF Identifier | Architecture | Weight Matrices | SVD Feasibility |
|-------|---------------|--------------|-----------------|-----------------|
| BERT-base-uncased | `bert-base-uncased` | 12-layer encoder, 768-dim | Q/K/V/O (768×768) + intermediate (768×3072, 3072×768) per layer = 60 matrices | ✅ fp32 CPU feasible |
| DeBERTa-v3-base | `microsoft/deberta-v3-base` | 12-layer encoder, disentangled attention | query_proj/key_proj/value_proj + FFN per layer ≈ 72 matrices | ✅ fp32 CPU feasible |
| ViT-base-patch16-224 | `google/vit-base-patch16-224` | 12-layer ViT, 768-dim | Q/K/V/O + MLP (768→3072, 3072→768) per layer = 72 matrices | ✅ fp32 CPU feasible |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers `AutoModel` / task-specific heads
- Identifier: see table above
- Code:
  ```python
  from transformers import (
      AutoModelForSequenceClassification,
      AutoTokenizer,
      ViTForImageClassification
  )
  # NLP models (MNLI: 3 labels, SST-2: 2 labels)
  bert = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=3)
  deberta = AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-v3-base", num_labels=3)
  # Vision model (CIFAR-10: 10 labels)
  vit = ViTForImageClassification.from_pretrained(
      "google/vit-base-patch16-224",
      num_labels=10,
      ignore_mismatched_sizes=True  # classifier head resized
  )
  ```

#### Proposed Model

**Architecture:** Baseline + per-layer PARA oracle rank assignment

The "proposed model" in H-E1 is not a new architecture — it is the **oracle training process** that assigns the optimal rank per layer. The experiment measures whether erank(W₀) *predicts* what the oracle *discovers*.

**Core Mechanism Implementation:**

```python
# Core Mechanism: erank(W₀) Computation + PARA Oracle Rank Discovery
# Based on: khanghy1000 gist (erank formula) + jonathanc.net (SVD loop pattern)
# Phase: Pre-experiment analysis (runs once before oracle training)

import torch
from transformers import AutoModel

def compute_erank_all_layers(model_name: str) -> dict[str, float]:
    """
    Compute effective rank erank(W₀) = exp(H(σ/‖σ‖₁)) for all
    weight matrices in a pretrained transformer model.
    
    Args:
        model_name: HuggingFace model identifier
    Returns:
        dict mapping layer_name -> erank value
    """
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    erank_map = {}
    
    for name, param in model.named_parameters():
        # Target only 2D weight matrices (skip biases, embeddings, LayerNorm)
        if param.dim() != 2 or "embed" in name or "norm" in name:
            continue
        W = param.detach().float()  # fp32 precision (CRITICAL)
        S = torch.linalg.svdvals(W)  # singular values only (faster than full SVD)
        S = S[S > 1e-10]             # filter numerical noise
        if S.numel() == 0:
            continue
        p = S / torch.sum(S)         # normalize to probability distribution
        H = -torch.sum(p * torch.log(p))  # Shannon entropy
        erank_map[name] = torch.exp(H).item()
    
    return erank_map

def run_para_oracle_sweep(
    model_name: str,
    dataset: str,
    ranks: list = [4, 8, 16, 32, 64],
    baseline_rank: int = 8,
    n_seeds: int = 2
) -> dict[str, int]:
    """
    PARA oracle: for each target layer, train LoRA with r=ranks[i],
    all other layers frozen at baseline_rank=8. Return argmax_r(val_acc).
    """
    # For each layer l and each candidate rank r:
    #   1. Wrap model with LoRA: target layer l at rank r, all others at r=baseline_rank
    #   2. Fine-tune for specified epochs
    #   3. Record validation accuracy
    # oracle_rank[l] = argmax over r of mean(val_acc over seeds)
    oracle_rank_map = {}
    # ... [full implementation in Phase 4]
    return oracle_rank_map
```

### Training Protocol

**Optimizer**: AdamW
- Parameters: lr=2e-5 (BERT/DeBERTa MNLI), lr=1e-4 (ViT CIFAR-10)
- Weight decay: 0.01
- **Source**: AdaLoRA paper (DeBERTa GLUE), FIM-LoRA paper confirms lr=2e-4 for DeBERTa tasks; conservative 2e-5 for stability with 3-epoch MNLI

**Learning Rate Schedule**: Linear warmup + linear decay
- Warmup ratio: 0.06 (6% of total steps)
- **Source**: Standard HuggingFace Trainer default for GLUE

**Batch Size**:
- NLP (BERT/DeBERTa MNLI): 32 (effective; gradient_accumulation_steps=1 if VRAM allows)
- Vision (ViT CIFAR-10): 128
- **Source**: Phase 2B controlled variables; AdaLoRA paper confirms batch=32 for DeBERTa GLUE

**Epochs**:
- BERT/DeBERTa on MNLI: ≥3 epochs (Phase 2B requirement for stable oracle)
- ViT on CIFAR-10: ≥5 epochs (Phase 2B requirement)
- **Source**: Phase 2B 02b_verification_plan.md Section 1.1

**Loss Function**: CrossEntropyLoss (3-class NLI for MNLI; 10-class for CIFAR-10)

**Precision**: FP32 for DeBERTa (FP16 causes classifier overflow — confirmed by FIM-LoRA paper); FP16/BF16 acceptable for BERT and ViT

**Seeds**: 2 seeds per oracle point (use mean validation accuracy for argmax); fixed seeds [42, 137]

**Non-target layer LoRA rank**: baseline r=8 (frozen LoRA adapters, not updated)

> ⚠️ **EXISTENCE (PoC)**: Oracle sweep is expensive — ~5 ranks × ~72 layers × 3 models × 2 seeds = ~2,160 training runs. Parallelization across layers is the key implementation challenge.

### Evaluation

**Primary Metrics**:
- **Pearson r**: Pearson correlation coefficient between erank(W₀) vector and oracle_rank vector, computed per model family
  - Success: r ≥ 0.65, one-tailed p < 0.05 for ≥2/3 families
- **Oracle validation accuracy**: validation accuracy at oracle rank (argmax over r∈{4,8,16,32,64})
  - Confirms oracle sweep produced valid rank assignments

**Success Criteria (PoC)**:
- proposed_metric > baseline_metric: Pearson r ≥ 0.65 (positive direction confirmed)
- At least 2 of 3 model families must satisfy: r ≥ 0.65 AND one-tailed p < 0.05

**Expected Baseline Performance** (from research):
- BERT-base MNLI uniform r=8: ~84–85% accuracy (LoRA paper)
- DeBERTa-v3-base MNLI uniform r=8: ~90.0% accuracy (AdaLoRA paper)
- ViT-base CIFAR-10 uniform r=8: ~97–98% accuracy (standard benchmark)
- **Source**: LoRA paper (microsoft/LoRA), AdaLoRA paper (QingruZhang/AdaLoRA)

**Secondary metric (record but not gate)**:
- Participation ratio PR(W₀) correlation with oracle ranks (fallback metric per Phase 2B A5)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: sequence classification (MNLI, CIFAR-10); correlation analysis (scipy/numpy)
- Library: HuggingFace `evaluate` library + `scipy.stats.pearsonr`
- Code:
  ```python
  import evaluate
  from scipy.stats import pearsonr
  glue_metric = evaluate.load("glue", "mnli")  # accuracy
  acc = glue_metric.compute(predictions=preds, references=labels)["accuracy"]
  r, p_value = pearsonr(erank_vector, oracle_rank_vector)
  one_tailed_p = p_value / 2  # convert two-tailed p to one-tailed (direction test)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Scatter plot of erank(W₀) vs oracle_rank per layer for each model family, with Pearson r annotation and r=0.65 reference line

#### Additional Figures (LLM Autonomous)
The Phase 4 coder should autonomously include:
1. **Per-model scatter plots** (3 subplots): erank(W₀) vs oracle_rank for BERT, DeBERTa, ViT; color-coded by layer type (attention Q/K/V/O vs FFN)
2. **Layer-depth heatmaps**: erank value per layer index (depth) for each model, showing how erank varies with depth
3. **Oracle rank distribution**: histogram of oracle ranks {4,8,16,32,64} per model, showing whether oracle prefers certain ranks
4. **Bootstrap CI plot**: Pearson r with 95% bootstrap CI error bars per model family

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | All 3 models have named weight matrices accessible via `model.named_parameters()` | TRUE |
| Mechanism Isolatable | erank computation runs independently of fine-tuning (pre-experiment analysis) | TRUE |
| Baseline Measurable | Uniform r=8 LoRA baseline can be trained and evaluated independently | TRUE |

### Architecture Compatibility Check

All three target models are standard transformer encoders with multi-head attention and FFN layers. All expose weight matrices as 2D `nn.Linear` parameters accessible via `model.named_parameters()`. SVD computation via `torch.linalg.svdvals` is supported on all matrix sizes.

**Required Features:**
- Named 2D weight matrices (`param.dim() == 2`) for query/key/value/output projections and FFN layers
- HuggingFace `peft` library support for selective LoRA target modules
- `torch.linalg.svdvals` for fp32 SVD

**Incompatible Architectures:**
- Models without explicit weight matrices (e.g., weight-shared architectures) — not applicable here
- Models requiring bf16/int4 only (would prevent fp32 SVD) — not applicable (all models support fp32)

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"erank computed for N layers: mean={:.2f}, std={:.2f}"` | `compute_erank_all_layers()` |
| Tensor Shape | erank_map has `len == expected_layer_count` (≈72-80 per model) | post-computation check |
| Metric Delta | oracle_rank varies across layers (not all same rank); Pearson r > 0 | `compute_pearson_r()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(erank_map, oracle_rank_map, model_name):
    indicators = {
        "erank_computed": len(erank_map) >= 60,  # expect 60-80 layers
        "oracle_varies": len(set(oracle_rank_map.values())) > 1,  # not all same rank
        "positive_correlation": False
    }
    if indicators["erank_computed"] and indicators["oracle_varies"]:
        common_layers = set(erank_map.keys()) & set(oracle_rank_map.keys())
        erank_vec = [erank_map[k] for k in sorted(common_layers)]
        oracle_vec = [oracle_rank_map[k] for k in sorted(common_layers)]
        from scipy.stats import pearsonr
        r, _ = pearsonr(erank_vec, oracle_vec)
        indicators["positive_correlation"] = r > 0
    all_pass = all(indicators.values())
    print(f"[{model_name}] Mechanism check: {indicators}")
    return all_pass, indicators
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | erank_map length ≥ 60, oracle varies |
| Effect Measurable | Pearson r > 0 | Before/after: r > 0 direction confirmed |
| Hypothesis Supported | r ≥ 0.65, one-tailed p < 0.05, ≥2/3 families | `scipy.stats.pearsonr` on erank vs oracle_rank vectors |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (erank computation + oracle sweep + correlation)
2. Pearson r ≥ 0.65 for ≥2/3 model families (one-tailed p < 0.05)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: HuggingFace PEFT docs — LoRA conceptual guide
- **URL**: https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora
- **Query Used**: "effective rank LoRA rank selection experiment design"
- **Key Insights**: PEFT `LoraConfig` + `get_peft_model` is the standard interface; supports per-module rank via custom configs
- **Used For**: Dataset loading confirmation (GLUE/CIFAR-10 standard), LoRA wrapper pattern

**Source A.2**: HuggingFace PEFT GitHub
- **URL**: https://github.com/huggingface/peft
- **Query Used**: "GLUE benchmark BERT fine-tuning LoRA PEFT"
- **Key Code**:
  ```python
  from peft import LoraConfig, get_peft_model
  peft_config = LoraConfig(r=16, lora_alpha=32, task_type=TaskType.SEQ_CLS)
  model = get_peft_model(model, peft_config)
  ```
- **Used For**: LoRA training loop pattern; oracle sweep implementation reference

### B. GitHub Implementations (Exa)

**Repository B.1**: Jonathan Chang's effective rank blog — `jonathanc.net`
- **URL**: https://jonathanc.net/blog/llm-effective-rank
- **Query Used**: "effective rank erank SVD LoRA rank prediction pretrained transformer PyTorch"
- **Relevance**: Demonstrates per-layer SVD loop for transformer weight matrices (Q/K/V/O and FFN)
- **Key Code** (annotated):
  ```python
  # fp32 cast CRITICAL for accurate erank computation
  W = param.detach().float()
  with torch.no_grad():
      _, S, _ = torch.linalg.svd(W, full_matrices=False)
  # Used as basis for: erank computation loop in Core Mechanism pseudo-code
  ```
- **Their Results**: Found that Llama-3-8B K/V erank ≈ DeepSeek-V2's chosen KV-LoRA rank
- **Used For**: SVD loop structure; fp32 cast pattern; model-agnostic weight matrix iteration

**Repository B.2**: khanghy1000 gist — `calculate_effective_rank_lora.py`
- **URL**: https://gist.github.com/khanghy1000/5a3ae7473554542ed0bcd787b07d886c
- **Query Used**: "effective rank erank SVD LoRA rank prediction pretrained transformer PyTorch"
- **Relevance**: EXACT implementation of erank formula matching H-E1 definition
- **Key Code** (annotated):
  ```python
  # Implements: erank(W) = exp(-sum(p * log(p))) where p = S/sum(S)
  def calculate_effective_rank(matrix, eps=1e-10):
      S = torch.linalg.svdvals(matrix)  # svdvals faster than full svd
      S = S[S > eps]                    # eps filter removes numerical noise
      p = S / torch.sum(S)
      entropy = -torch.sum(p * torch.log(p))
      return torch.exp(entropy).item()
  # Used as: direct basis for compute_erank_all_layers() in Core Mechanism pseudo-code
  ```
- **Used For**: erank formula implementation (directly reused in pseudo-code)

**Repository B.3**: `QingruZhang/AdaLoRA`
- **URL**: https://github.com/QingruZhang/AdaLoRA
- **Query Used**: "PARA oracle per-layer LoRA rank sweep GLUE fine-tuning AdamW BERT DeBERTa"
- **Relevance**: DeBERTa-v3-base GLUE training configuration; closest existing work on layer-wise rank allocation
- **Configuration Extracted**:
  - Optimizer: AdamW, lr ∈ {5e-5, 8e-5, 1e-4, 2e-4}, batch=32, FP32
  - Target modules: `query_proj, key_proj, value_proj`
  - MNLI result: 90.4 (DeBERTa-v3-base, 0.3M params)
- **Used For**: Training hyperparameters for GLUE MNLI oracle runs

**Repository B.4**: `microsoft/LoRA`
- **URL**: https://github.com/microsoft/LoRA
- **Query Used**: "PARA oracle per-layer LoRA rank sweep GLUE fine-tuning"
- **Relevance**: Official LoRA baseline with DeBERTa v2 NLU examples; GLUE benchmark reference
- **Key Code**:
  ```python
  import loralib as lora
  layer = lora.Linear(in_features, out_features, r=8)  # per-layer rank assignment
  lora.mark_only_lora_as_trainable(model)
  ```
- **Used For**: Per-layer rank assignment pattern; baseline performance reference (MNLI 84.5 BERT, 90.0 DeBERTa)

**Repository B.5**: AdaLoRA paper (arxiv 2303.10512)
- **URL**: https://arxiv.org/pdf/2303.10512
- **Query Used**: "PARA oracle per-layer LoRA rank sweep GLUE fine-tuning AdamW BERT DeBERTa"
- **Key Findings**: Confirms DeBERTa-v3-base GLUE setup; shows rank allocation matters (AdaLoRA vs uniform LoRA); demonstrates oracle-like upper bound evaluation
- **Used For**: Training protocol hyperparameters; baseline performance expectations

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear.

The erank formula and SVD loop pattern from B.1 and B.2 are directly usable without semantic analysis of a complex codebase. The hypothesis does not require analyzing an existing implementation but rather implementing a novel oracle sweep.

### D. Previous Hypothesis Context

**Previous Context**: None — this is the first hypothesis in the verification chain.

H-E1 has no prerequisites; downstream hypotheses H-M1, H-M2, H-M3 will reuse H-E1 oracle artifacts.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| erank formula | GitHub | B.2 (khanghy1000 gist) |
| SVD fp32 loop pattern | Blog/Code | B.1 (jonathanc.net) |
| Dataset: GLUE MNLI | Phase 2A/2B | 02b_verification_plan.md §1.3 |
| Dataset: CIFAR-10 | Phase 2A/2B | 02b_verification_plan.md §1.3 |
| Dataset loading code | Archon KB | A.1 (HF PEFT docs) |
| NLP training hyperparams | GitHub | B.3 (AdaLoRA), B.5 (AdaLoRA paper) |
| ViT training hyperparams | Phase 2B | 02b_verification_plan.md |
| PEFT LoRA wrapping | Archon KB | A.2 (HF PEFT) |
| Target modules DeBERTa | Archon KB + Exa | A.2, B.3 |
| Baseline performance | GitHub | B.4 (microsoft/LoRA), B.3 (AdaLoRA) |
| Pearson r success threshold | Phase 2B | 02b_verification_plan.md §2.2 H-E1 |
| Bootstrap CI (n=1000) | Phase 2B | 02b_verification_plan.md §2.2 H-E1 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05

### Workflow History for This Hypothesis
- 2026-08-05T00:00:00: Phase 2B completed — H-E1 designated MUST_WORK, EXISTENCE type
- 2026-08-05T22:14:14: Set to IN_PROGRESS by hypothesis loop
- 2026-08-05: Phase 2C experiment design IN_PROGRESS

---

*MCP Tools Used: Archon (3 KB queries + 2 code queries), Exa (2 code context + 2 web search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
