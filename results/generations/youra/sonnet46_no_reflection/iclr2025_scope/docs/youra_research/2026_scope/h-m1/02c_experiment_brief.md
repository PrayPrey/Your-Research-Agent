# Experiment Design: H-M1

**Date:** 2026-05-20
**Author:** Anonymous
**Hypothesis Statement:** Under LLaMA-3.1-8B PEFT fine-tuning on MNLI/SST-2/QNLI at 50% KV budget, if Locret retaining heads are trained via task classification cross-entropy loss (rather than LM distillation loss), then the resulting eviction policy retains tokens with higher task label-relevant attribution scores than LM-trained eviction, because classification gradients reward token positions whose values discriminate between output classes rather than positions that predict the next token. JointLoRA-KV achieves ≥2% higher GLUE accuracy than B1 (frozen Locret) at 50% KV budget.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 MUST_WORK gate SATISFIED (mean_rho=0.3662 < 0.7, 100/100 MNLI examples)
**Gate Status:** MUST_WORK — JointLoRA-KV GLUE accuracy ≥ B1 + 2% at 50% KV budget

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 ✅ (COMPLETED — misalignment confirmed)

### Gate Condition
MUST_WORK: JointLoRA-KV GLUE accuracy (mean across MNLI/SST-2/QNLI, 3 seeds) ≥ B1 + 2.0 percentage points at budget_ratio=0.5. If not met, pipeline reviews mechanism before proceeding.

---

## Continuation Context

**Previous Hypothesis:** H-E1 (EXISTENCE — COMPLETED)

**Proven Components from H-E1:**
- LoRA-modified attention patterns are systematically misaligned with LM-loss-trained Locret CIS scores (mean ρ=0.3662, well below 0.7)
- This confirms that task classification gradients produce qualitatively different eviction priorities than LM loss
- H-M1 directly tests whether this misalignment gap can be closed by training Locret retaining heads with task CE loss

**Key Implementation Lessons from H-E1:**
- Base model: `meta-llama/Meta-Llama-3.1-8B-Instruct` (float16)
- Locret checkpoint: `hyx21/Locret-llama-3.1-8B-instruct` (retaining heads only: fc1, fc2 per layer)
- GQA: 8 KV heads → 32 query heads via `repeat_interleave(4)` 
- Sequential model loading required for VRAM budget on H100
- `attn_implementation="eager"` required for attention access
- GPU: NVIDIA H100 NVL, `CUDA_VISIBLE_DEVICES=0`

### Previous Hypothesis Results (H-E1)
- Mean Spearman ρ = 0.3662 ± 0.0759 across 100 MNLI examples
- 100% of examples showed ρ < 0.7 (no borderline cases)
- Task-adapted LoRA attention ≠ LM-trained Locret CIS → joint training signal is meaningful
- All code ran without errors; 4 figures generated

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: LoRA KV cache joint training task loss**
- Result: HuggingFace PEFT library (github.com/huggingface/peft, similarity 0.515)
  - Key insight: PEFT LoraConfig supports `task_type=TaskType.SEQ_CLS` for classification
  - Standard pattern: `get_peft_model(model, LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","v_proj","k_proj"]))`
  - AdamW optimizer over `model.parameters()` with linear schedule with warmup
- Result: LoRA conceptual guide (huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora)
  - Key insight: LoRA A/B matrices are injected additively — gradient paths are independent from other parameter sets

**Query 2: Locret KV eviction retaining head**
- Result: FlashAttention (github.com/HazyResearch/flash-attention, similarity 0.32)
  - Key insight: GQA supported via `repeat_interleave` in `enable_gqa=True` mode — confirms H-E1 approach
  - KV cache shapes: `(batch_size, seqlen, nheads_k, headdim)` — relevant for Locret head integration

**Query 3: GLUE benchmark PEFT fine-tuning**  
- Result: HuggingFace PEFT repo (similarity 0.515)
  - Confirmed: `load_dataset("glue", "mnli")` is standard loading pattern
  - LoRA for sequence classification uses `AutoModelForSequenceClassification` + `LoraConfig(task_type="SEQ_CLS")`

### Archon Code Examples

**Code Source 1: Configure and Fine-tune PEFT Model**
```python
from transformers import AutoModelForCausalLM
from peft import LoraConfig, TaskType, get_peft_model
peft_config = LoraConfig(
    r=16, lora_alpha=32,
    task_type=TaskType.CAUSAL_LM,
    target_modules=["q_proj", "k_proj", "v_proj"]
)
model = get_peft_model(model, peft_config)
```
- Pattern: Standard PEFT wrapping — used as basis for B1 and JointLoRA-KV LoRA setup

**Code Source 2: Initialize Optimizer with LoRA Layers**
```python
optimizer = optimizer_cls(
    lora_layers, lr=args.learning_rate,
    betas=(args.adam_beta1, args.adam_beta2),
    weight_decay=args.adam_weight_decay,
)
```
- Pattern: Selective optimizer over trainable params — for JointLoRA-KV we extend to include Locret head params

**Code Source 3: Scaled Dot-Product Attention (GQA)**
```python
if enable_gqa:
    key = key.repeat_interleave(query.size(-3) // key.size(-3), -3)
    value = value.repeat_interleave(query.size(-3) // value.size(-3), -3)
```
- Pattern: Confirms GQA expansion approach used in H-E1 is correct for LLaMA-3.1-8B

### Exa GitHub Implementations

**Repository 1: huangyuxiang03/Locret** (⭐ 14)
- **URL:** https://github.com/huangyuxiang03/Locret
- **Relevance:** Official Locret implementation — exact architecture used in H-M1
- **Architecture:** Retaining heads R per layer; CIS formula: `S̃ = R([Q,K,V]) = σ([Q,K,V]·W1)·W2`
  - W1 ∈ R^{(dm+2dkv)×dR}, W2 ∈ R^{dR×h/g}, dR=1024
  - Output: S̃[k] ∈ R^{h/g} — per-KV-head importance score for token k
- **Training (original):** `python train.py --model_dir <model_dir>` — trains on QA SFT dataset with LM distillation loss, frozen backbone
- **Key insight for H-M1:** Original Locret trains retaining heads with LM distillation loss + frozen LLM backbone. H-M1 replaces this with task CE loss AND jointly updates LoRA adapters.
- **Checkpoint:** `hyx21/Locret-llama-3.1-8B-instruct` (retaining heads only, .bin format)
- **Training config (original Locret):** lr=1e-4, Adam, small QA SFT dataset, <1 GPU hour

**Repository 2: huggingface/peft (sequence_classification example)**
- **URL:** https://github.com/huggingface/peft/blob/main/examples/sequence_classification/LoRA.ipynb
- **Relevance:** Standard LoRA+GLUE fine-tuning pattern
- **Key Code:**
```python
peft_config = LoraConfig(task_type="SEQ_CLS", r=8, lora_alpha=16, lora_dropout=0.1)
optimizer = AdamW(params=model.parameters(), lr=3e-4)
lr_scheduler = get_linear_schedule_with_warmup(
    optimizer=optimizer,
    num_warmup_steps=0.06 * (len(train_dataloader) * num_epochs),
    num_training_steps=(len(train_dataloader) * num_epochs),
)
```
- **Insight:** For H-M1, we extend optimizer to cover both LoRA params AND Locret head params simultaneously

**Repository 3: THUDM/LongBench**
- **URL:** https://github.com/THUDM/LongBench
- **Relevance:** LongBench evaluation framework — secondary metric for H-M1
- **Metrics:** `qa_f1_score` for narrativeqa, qasper, multifieldqa_en
- **Loading:** `load_dataset("THUDM/LongBench", "narrativeqa")` via HuggingFace datasets
- **Eval script:** `LongBench/eval.py` with `dataset2metric` mapping

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For Locret retaining heads: Official implementation is `huangyuxiang03/Locret` / `hyx21/Locret-llama-3.1-8B-instruct`. H-M1 MODIFIES the training loss (CE instead of LM distillation) while keeping the architecture identical.

**Recommended Implementation Path:**
- Primary: Load `hyx21/Locret-llama-3.1-8B-instruct` retaining head weights as initialization, then fine-tune jointly with LoRA using task CE loss
- Fallback: Re-initialize Locret heads from scratch and train jointly (more compute, but avoids checkpoint loading complexity)
- Justification: Starting from pretrained Locret heads provides warm initialization for the retaining head MLP weights; joint CE fine-tuning then redirects the learned importance estimation toward task-discriminative tokens

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa/Archon search results was sufficiently clear. Locret architecture is fully specified in the paper (CIS formula, W1/W2 dimensions, sigmoid activation). No complex custom layers beyond standard linear projections.

---

## Experiment Specification

### Dataset

**Primary: GLUE (MNLI, SST-2, QNLI)**
- **Name:** GLUE Benchmark
- **Type:** standard
- **Tasks:** MNLI (392k train, 9.8k val, 3 classes), SST-2 (67k train, 872 val, 2 classes), QNLI (105k train, 5.5k val, 2 classes)
- **Total evaluation samples:** ~16k validation examples across 3 tasks
- **Preprocessing:** Tokenize with LlamaTokenizer, max_length=512 (GLUE), pad_to_max_length=True
- **Augmentation:** None (classification fine-tuning)
- **Splits used:** train (fine-tuning), validation_matched/validation (evaluation)

**Secondary: LongBench-QA**
- **Name:** LongBench (THUDM)
- **Type:** standard
- **Tasks:** NarrativeQA, Qasper, MultiFieldQA-en
- **Total evaluation samples:** ~600 test examples (NarrativeQA: 200, Qasper: 200, MultiFieldQA: 150+)
- **Metric:** QA F1 score (qa_f1_score from THUDM/LongBench eval.py)
- **Splits used:** test only (evaluation)
- **Context length:** 5k–15k tokens (KV eviction meaningfully activated)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier GLUE: `"glue"` with config `"mnli"` / `"sst2"` / `"qnli"`
- Code GLUE: `load_dataset("glue", "mnli")`, `load_dataset("glue", "sst2")`, `load_dataset("glue", "qnli")`
- Identifier LongBench: `"THUDM/LongBench"` with config `"narrativeqa"` / `"qasper"` / `"multifieldqa_en"`
- Code LongBench: `load_dataset("THUDM/LongBench", "narrativeqa", split="test")`

### Models

#### Baseline Model

**B1: LoRA + Frozen Locret (Lower Bound)**
- **Architecture:** LLaMA-3.1-8B with LoRA r=16 adapters (Q/K/V projections) + Locret retaining heads (frozen, LM-trained)
- **Type:** PeftModel wrapping `meta-llama/Meta-Llama-3.1-8B-Instruct`
- **LoRA target modules:** `["q_proj", "k_proj", "v_proj"]`
- **Locret heads:** Loaded from `hyx21/Locret-llama-3.1-8B-instruct`, ALL parameters frozen during training
- **Training objective:** Task CE loss over LoRA params only; Locret heads receive no gradient updates
- **Loading:**
  - Base: `AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct", torch_dtype=torch.float16, attn_implementation="eager")`
  - LoRA: `get_peft_model(model, LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","k_proj","v_proj"]))`
  - Locret: Load `hyx21/Locret-llama-3.1-8B-instruct` retaining head weights; freeze via `param.requires_grad = False`

**B2: LoRA + kvpress heuristic eviction (Reference)**
- **Architecture:** LLaMA-3.1-8B with LoRA r=16; kvpress StreamingLLM/H2O heuristic at inference
- **Purpose:** Confirm learned eviction (JointLoRA-KV) > heuristic eviction at same budget
- **Loading:** Same LoRA setup; kvpress applied at inference only (no eviction training)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers + PEFT
- Identifier: `"meta-llama/Meta-Llama-3.1-8B-Instruct"`
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct", torch_dtype=torch.float16)`

#### Proposed Model

**JointLoRA-KV**
**Architecture:** LLaMA-3.1-8B + LoRA adapters (Q/K/V) + Locret retaining heads, JOINTLY trained via task CE loss

**Core Mechanism Implementation:**

```python
# JointLoRA-KV: Joint Training of LoRA Adapters and Locret Retaining Heads
# Based on: huangyuxiang03/Locret architecture + HuggingFace PEFT LoRA training
# CIS formula: S̃ = σ([Q,K,V] @ W1) @ W2  (Locret paper Eq. 1)

class JointLoRAKVTrainer:
    """Joint trainer for LoRA adapters + Locret retaining heads via task CE loss."""

    def __init__(self, base_model, lora_config, locret_head_path,
                 lora_lr=1e-4, locret_lr=5e-4, budget_ratio=0.5):
        # Load LoRA-wrapped model
        self.model = get_peft_model(base_model, lora_config)
        # Load pre-trained Locret retaining heads (warm init from LM-trained weights)
        self.locret_heads = load_locret_heads(locret_head_path)  # fc1, fc2 per layer
        # Separate learning rates: LoRA adapters vs Locret heads
        self.optimizer = AdamW([
            {"params": self.model.parameters(), "lr": lora_lr},
            {"params": self.locret_heads.parameters(), "lr": locret_lr},
        ], weight_decay=0.01)
        self.budget_ratio = budget_ratio

    def forward_with_eviction(self, input_ids, attention_mask, labels):
        # Step 1: Forward pass with soft KV scoring (training mode)
        outputs = self.model(input_ids, attention_mask=attention_mask,
                             output_hidden_states=True)
        # Step 2: Compute CIS scores via retaining heads (soft, differentiable)
        # CIS[layer][token] = sigmoid([Q,K,V] @ W1) @ W2  -> (B, L, n_kv_heads)
        cis_scores = self.locret_heads(outputs.hidden_states)  # soft scores
        # Step 3: Apply soft budget mask during training (Gumbel-softmax or top-k)
        # Hard eviction at inference; soft weighted sum at training for gradient flow
        masked_output = apply_soft_budget(outputs.logits, cis_scores, self.budget_ratio)
        # Step 4: Task classification CE loss (NOT LM distillation loss)
        loss = F.cross_entropy(masked_output, labels)
        return loss

    def train_step(self, batch):
        self.optimizer.zero_grad()
        loss = self.forward_with_eviction(**batch)
        loss.backward()  # Gradients flow to BOTH LoRA A/B matrices AND Locret W1/W2
        torch.nn.utils.clip_grad_norm_(self.all_params(), max_norm=1.0)
        self.optimizer.step()
        return loss.item()
```

**Key design decisions:**
- **Separate LRs:** LoRA adapters (1e-4) and Locret heads (5e-4) — prevents fast-learning Locret heads from destabilizing LoRA
- **Soft scoring during training:** Allows gradient to flow through eviction decision (hard top-k is non-differentiable)
- **Hard eviction at inference:** Budget_ratio=0.5 → retain top-50% CIS tokens, evict bottom-50%
- **Warm init:** Start Locret heads from `hyx21/Locret-llama-3.1-8B-instruct` weights (not random)

### Training Protocol

**Continuation from H-E1:** H-E1 used no training (inference only). H-M1 requires full fine-tuning. Using standard PEFT/GLUE hyperparameters from Archon/Exa research.

**Optimizer:** AdamW with separate parameter groups
- LoRA parameters: lr=1e-4, weight_decay=0.01
- Locret retaining head parameters: lr=5e-4, weight_decay=0.01
- betas=(0.9, 0.999), eps=1e-8
- **Source:** PEFT LoRA sequence classification example (HuggingFace); separate LRs from Locret paper (1e-4 for retaining heads)

**Learning Rate Schedule:** Linear warmup + linear decay
- Warmup steps: 6% of total training steps
- Total steps: len(train_dataloader) × num_epochs
- **Source:** HuggingFace PEFT sequence_classification LoRA.ipynb

**Batch Size:** 8 per device (gradient accumulation steps=4 → effective batch=32)
- **Source:** Standard PEFT GLUE fine-tuning practice; fits H100 VRAM with float16

**Epochs:** 3 per GLUE task (MNLI), 5 for SST-2 and QNLI (smaller datasets)
- **Source:** HuggingFace PEFT GLUE fine-tuning recommendations

**Loss Function:** Cross-entropy classification loss (task CE) over BOTH LoRA and Locret parameters
- `F.cross_entropy(logits, labels)` — this is the MECHANISM being tested (vs. LM distillation in original Locret)

**Seeds:** 3 seeds: 42, 123, 456 (for mean ± std reporting)

**KV Budget:** budget_ratio=0.5 (50% of KV tokens retained during training and inference)

**Gradient clipping:** max_norm=1.0 (prevents gradient explosion from joint optimization)

**Precision:** float16 (models loaded), float32 (loss computation)

**GPU:** Single H100 NVL; `CUDA_VISIBLE_DEVICES=0`

### Evaluation

**Primary Metrics (GLUE at 50% KV budget):**
- MNLI: Accuracy on validation_matched (9.8k examples)
- SST-2: Accuracy on validation (872 examples)
- QNLI: Accuracy on validation (5.5k examples)
- **Mean GLUE accuracy:** Average of MNLI/SST-2/QNLI accuracy across 3 seeds

**Secondary Metrics (LongBench-QA at 50% KV budget):**
- NarrativeQA: QA F1
- Qasper: QA F1
- MultiFieldQA-en: QA F1
- **Mean LongBench-QA F1:** Average across 3 tasks

**Success Criteria:**
- **Primary (MUST_WORK gate):** Mean GLUE accuracy of JointLoRA-KV ≥ B1 (frozen Locret) + 2.0 pp at budget_ratio=0.5
- **Secondary:** JointLoRA-KV ≥ B2 (kvpress heuristic) on GLUE
- **PoC pass condition:** Code runs without error AND proposed_metric > baseline_metric

**Expected Baseline Performance (from research):**
- Vanilla LoRA on MNLI: ~87-89% accuracy (no KV compression)
- B1 (frozen Locret): ~84-87% at 50% budget — LM-trained eviction misaligned with task → accuracy drop
- B2 (kvpress): ~85-87% at 50% budget
- JointLoRA-KV expected: ~87-90% at 50% budget (task CE eviction recovers accuracy loss)
- **Source:** Locret paper (8x compression with <10% performance loss on LongBench); PEFT GLUE baselines from HuggingFace

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: sequence_classification
- Library: `datasets` evaluate module + `sklearn.metrics` + THUDM LongBench eval.py
- GLUE Code: `evaluate.load("glue", "mnli")` → `.compute(predictions=..., references=...)`
- LongBench Code: `qa_f1_score(prediction, ground_truths)` from `THUDM/LongBench/LongBench/metrics.py`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — JointLoRA-KV vs B1 vs B2 mean GLUE accuracy at 50% budget (with error bars ± std across 3 seeds)

#### Additional Figures (LLM Autonomous)

Based on MECHANISM hypothesis type and eviction-based architecture:
1. **Training loss curves** — JointLoRA-KV training loss per epoch (all 3 seeds) to verify convergence
2. **Per-task GLUE breakdown** — Accuracy bars for MNLI/SST-2/QNLI separately (JointLoRA-KV vs B1 vs B2)
3. **Budget sensitivity curve** — Accuracy vs budget_ratio (0.3, 0.5, 0.7) for JointLoRA-KV vs B1 (shows eviction quality across budgets)
4. **LongBench-QA F1 comparison** — Bar chart for NarrativeQA/Qasper/MultiFieldQA (JointLoRA-KV vs B1/B2)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (training loop completes for all 3 seeds)
2. `mean_glue_accuracy(JointLoRA-KV) > mean_glue_accuracy(B1)` at budget_ratio=0.5

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | LLaMA-3.1-8B has GQA attention layers — Locret retaining heads can inject into each layer's [Q,K,V] concat | TRUE |
| Mechanism Isolatable | B1 uses frozen Locret heads (no CE training); JointLoRA-KV uses CE-trained Locret heads — direct toggle | TRUE |
| Baseline Measurable | B1 (frozen Locret + LoRA CE) runs independently at 50% budget → measurable GLUE accuracy | TRUE |

### Architecture Compatibility Check

LLaMA-3.1-8B has 32 transformer layers, each with GQA attention (32 Q heads, 8 KV heads, head_dim=128). Locret retaining heads inject into each layer's attention module, taking `[Q, K, V]` as input (after projection, before softmax). The CIS MLP: W1 ∈ R^{(d_model+2*d_kv)×1024}, W2 ∈ R^{1024×8} produces per-KV-head importance scores.

**Required Features:**
- Attention layers with accessible Q, K, V tensors (requires `attn_implementation="eager"`)
- GQA with 8 KV heads (CIS output dim=8, expanded to 32 via repeat_interleave)
- LoRA injected into Q/K/V projection matrices (disjoint from Locret W1/W2)

**Incompatible Architectures:**
- Pure SSM models (Mamba, RWKV) — no KV cache → Locret CIS inapplicable
- Flash Attention 2 implementation — blocks output_attentions=True; must use eager mode

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"JointLoRA-KV: Locret heads receiving CE gradients — step {step}, locret_grad_norm={norm:.4f}"` | train.py:train_step() |
| Tensor Shape | CIS output shape `(B, L, 8)` per layer, with values in (0,1) — sigmoid activated | model.py:locret_heads.forward() |
| Metric Delta | JointLoRA-KV GLUE accuracy > B1 GLUE accuracy by ≥ 2pp after training | evaluate.py:run_eval() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(training_log, b1_results, joint_results):
    """Verify JointLoRA-KV mechanism is actually working."""
    indicators = {
        # Check 1: Locret heads received gradient updates during training
        "locret_grad_received": any(
            "locret_grad_norm" in line and float(line.split("=")[1]) > 1e-6
            for line in training_log
        ),
        # Check 2: CIS output shape is correct (B, L, 8) per layer
        "cis_shape_correct": all(
            cis.shape[-1] == 8 for cis in joint_results.get("cis_samples", [])
        ),
        # Check 3: Eviction actually occurred (some tokens masked)
        "eviction_active": joint_results.get("tokens_retained_ratio", 1.0) < 0.55,
        # Check 4: Performance gap in right direction
        "accuracy_improved": (
            joint_results["mean_glue_acc"] > b1_results["mean_glue_acc"]
        ),
    }
    gate_passed = (
        indicators["locret_grad_received"] and
        indicators["cis_shape_correct"] and
        indicators["eviction_active"] and
        indicators["accuracy_improved"] and
        (joint_results["mean_glue_acc"] - b1_results["mean_glue_acc"]) >= 2.0
    )
    return gate_passed, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Locret heads not updating | `locret_grad_norm == 0` in training log | FAIL: Check optimizer param groups — Locret heads may not be in optimizer |
| CIS shape mismatch | Output shape ≠ (B, L, 8) | FAIL: GQA head count mismatch — check repeat_interleave |
| No tokens evicted | `tokens_retained_ratio ≈ 1.0` | FAIL: Budget mask not applied — check eviction hook |
| Training divergence | loss NaN or loss > 10x initial | EXPLORE: Try separate LRs, gradient clipping, lower locret_lr |
| JointLoRA-KV ≤ B1 | Gate criterion not met | EXPLORE: Check if GLUE ≤512 tokens produces minimal eviction events; supplement with LongBench |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | Locret grad_norm > 0 in training | Log check per training step |
| Effect Measurable | Δ GLUE accuracy ≠ 0 (direction test) | Before/after B1 comparison |
| Hypothesis Supported | JointLoRA-KV GLUE ≥ B1 + 2.0 pp | Mean across MNLI/SST-2/QNLI, 3 seeds |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** HuggingFace PEFT library (github.com/huggingface/peft)
- **Query Used:** "LoRA fine-tuning PEFT AdamW optimizer training loop"
- **Key Insights:**
  - Standard LoRA wrapping: `get_peft_model(model, LoraConfig(r=16, lora_alpha=32, target_modules=[...]))`
  - `AdamW(params=model.parameters(), lr=lr)` with linear warmup scheduler
  - For GLUE: `task_type="SEQ_CLS"` or add classification head on top of CausalLM
- **Used For:** LoRA setup in B1 and JointLoRA-KV; optimizer configuration

**Source A.2:** PEFT LoRA sequence classification example
- **Query Used:** "GLUE benchmark PEFT fine-tuning LLaMA accuracy"
- **Key Insights:**
  - `get_linear_schedule_with_warmup` with 6% warmup steps is standard for GLUE
  - `evaluate.load("glue", task_name)` for metric computation
  - `AutoModelForSequenceClassification` or classification head over CausalLM final hidden state
- **Used For:** Training protocol (LR schedule, warmup), evaluation metrics

**Source A.3:** FlashAttention KV cache interface (github.com/HazyResearch/flash-attention)
- **Query Used:** "KV cache eviction attention scoring PyTorch"
- **Key Insights:**
  - GQA: `key.repeat_interleave(query.size(-3) // key.size(-3), -3)` — confirms H-E1 pattern
  - KV cache shape: `(batch_size, seqlen, nheads_k, headdim)` for 8 KV heads in LLaMA-3.1-8B
- **Used For:** Architecture compatibility check; eviction budget implementation

### B. GitHub Implementations (Exa)

**Repository B.1:** huangyuxiang03/Locret (⭐ 14)
- **URL:** https://github.com/huangyuxiang03/Locret
- **Query Used:** "Locret KV cache eviction retaining head joint training LoRA LLaMA GitHub"
- **Relevance:** Official Locret codebase — ground truth for retaining head architecture
- **Key Code (CIS formula from paper):**
```python
# Retaining head R for layer i:
# S̃ = R([Q,K,V]) = σ([Q,K,V] @ W1) @ W2
# W1 ∈ R^{(dm+2*dkv) × dR}, W2 ∈ R^{dR × (h/g)}, dR=1024
# Output S̃[k] ∈ R^{h/g} = importance score per KV head for token k
cis = torch.sigmoid(qkv_concat @ self.W1) @ self.W2  # (B, L, n_kv_heads)
```
- **Training Config (original, for reference):**
  - Training on QA SFT dataset; LM distillation loss; lr=1e-4; <1 GPU hour
  - Retaining heads only updated; backbone frozen
- **Used For:** Core mechanism architecture; CIS formula in pseudo-code; warm init strategy
- **Checkpoint:** `hyx21/Locret-llama-3.1-8B-instruct`

**Repository B.2:** huggingface/peft sequence_classification
- **URL:** https://github.com/huggingface/peft/blob/main/examples/sequence_classification/LoRA.ipynb
- **Query Used:** "LoRA PEFT fine-tuning GLUE classification cross-entropy loss LLaMA-3 PyTorch training loop"
- **Key Code:**
```python
peft_config = LoraConfig(task_type="SEQ_CLS", inference_mode=False, r=8, lora_alpha=16, lora_dropout=0.1)
optimizer = AdamW(params=model.parameters(), lr=lr)
lr_scheduler = get_linear_schedule_with_warmup(optimizer=optimizer,
    num_warmup_steps=0.06*(len(train_dataloader)*num_epochs),
    num_training_steps=(len(train_dataloader)*num_epochs))
```
- **Used For:** Training protocol (optimizer, LR schedule, warmup ratio); GLUE evaluation pattern

**Repository B.3:** THUDM/LongBench
- **URL:** https://github.com/THUDM/LongBench
- **Query Used:** "LongBench THUDM dataset loading evaluation NarrativeQA Qasper Python"
- **Key Code:**
```python
dataset2metric = {
    "narrativeqa": qa_f1_score,
    "qasper": qa_f1_score,
    "multifieldqa_en": qa_f1_score,
}
# Loading: load_dataset("THUDM/LongBench", "narrativeqa", split="test")
```
- **Used For:** Secondary metric (LongBench F1); dataset loading code; eval script reference

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. Locret CIS formula is explicitly stated in paper (Eq. 1): `S̃ = σ([Q,K,V]·W1)·W2`, dimensions fully specified (W1, W2, dR=1024). No ambiguous custom layers requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-E1
- **File:** `h-e1/04_validation.md`
- **Reused Components:**
  - Base model: `meta-llama/Meta-Llama-3.1-8B-Instruct` — proven loadable, fits H100 VRAM
  - Locret checkpoint: `hyx21/Locret-llama-3.1-8B-instruct` — proven accessible and correctly loadable
  - GLUE MNLI loading: `load_dataset("glue", "mnli")` — proven working
  - GQA expansion: `repeat_interleave(4)` pattern — proven correct for 8→32 head expansion
  - Sequential model loading: LoRA first → unload → Locret — proven VRAM-safe
- **Why Reused:** Enables controlled comparison — only the training objective and optimizer configuration changes between H-E1 (inference-only) and H-M1 (joint training)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| GLUE dataset selection | Phase 2A/2B | 02b_verification_plan.md §1.3 |
| LongBench dataset selection | Phase 2A/2B | 02b_verification_plan.md §1.3 |
| LLaMA-3.1-8B model | Phase 2A/2B | 02b_verification_plan.md §1.3 |
| GLUE loading code | Exa/Archon | B.2 (PEFT notebook), A.2 |
| LongBench loading code | Exa | B.3 (THUDM/LongBench) |
| Locret CIS formula | Exa | B.1 (huangyuxiang03/Locret paper) |
| Locret head dimensions | Exa | B.1 (W1, W2, dR=1024 from paper) |
| JointLoRA-KV pseudo-code | Exa + Archon | B.1 (Locret arch) + A.1 (PEFT LoRA) |
| AdamW optimizer config | Archon | A.1, A.2 (PEFT examples) |
| LR schedule (linear warmup) | Archon | A.2 (PEFT GLUE example) |
| Separate LR for LoRA/Locret | Exa | B.1 (Locret training: 1e-4 for heads) |
| Budget_ratio=0.5 | Phase 2A/2B | 02b_verification_plan.md §1 (controlled var) |
| Seeds 42/123/456 | Phase 2A | verification_state.yaml controlled_variables |
| GQA expansion pattern | Archon + H-E1 | A.3 (FlashAttention), h-e1/04_validation.md |
| QA F1 metric | Exa | B.3 (THUDM/LongBench eval.py) |
| GLUE accuracy metric | Archon | A.2 (evaluate.load) |
| Success threshold +2pp | Phase 2B | 02b_verification_plan.md H-M1 success criteria |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-20T00:00:00

### Workflow History for This Hypothesis
- H-E1 COMPLETED 2026-05-20T04:45:00 — mean_rho=0.3662, MUST_WORK gate SATISFIED
- H-M1 set to IN_PROGRESS 2026-05-20T01:43:03 — Phase 2C → 3 → 4 pipeline started
- H-M1 experiment design IN_PROGRESS → COMPLETED (this document)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 — Implementation Planning*
