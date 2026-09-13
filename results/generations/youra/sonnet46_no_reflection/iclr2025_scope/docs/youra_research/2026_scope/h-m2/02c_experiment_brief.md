# Experiment Design: H-M2

**Date:** 2026-05-20
**Author:** Anonymous
**Hypothesis Statement:** Joint end-to-end training of LoRA adapter parameters and Locret retaining head parameters in a single backward pass via task classification loss converges stably (no loss divergence or NaN across 3 seeds) and achieves >= B3 accuracy on LongBench-QA at 50% KV budget, because LoRA A/B matrices and Locret head weights are disjoint parameter sets with independent gradient paths.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 COMPLETED (mean Spearman rho=0.3662 < 0.7; misalignment confirmed)
**Gate Status:** MUST_WORK (unsatisfied — pending this experiment)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED ✅)

### Gate Condition
MUST_WORK: If joint training is unstable (loss divergence or NaN in any of 3 seeds), H-M3 and H-M4 are blocked. If stable AND accuracy >= B3, gate is satisfied and H-M3 proceeds.

---

## Continuation Context

**Previous hypothesis H-E1 results (loaded from verification_state.yaml):**
- H-E1 PASSED: mean Spearman ρ=0.3662 (well below 0.7 threshold), confirming that task-adapted LoRA attention patterns are systematically misaligned with LM-loss-trained Locret CIS scores across 100 MNLI examples.
- This confirms the existence precondition: joint training has a non-trivial gradient signal to contribute because eviction priorities differ between task loss and LM loss.

### Previous Hypothesis Results (if applicable)
H-E1 proven: Task-attention/eviction-score misalignment exists. LoRA A/B and Locret retaining head parameters are architecturally disjoint (confirmed in Phase 2B design review). H-M2 now tests whether joint optimization of these disjoint parameter sets is technically feasible.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "joint LoRA KV cache training optimization"**
- Result: HuggingFace PEFT docs (LoRA conceptual guide) — confirms LoRA injects A/B matrices into Q/K/V projections; separate from any attention head MLP parameters.
- Result: HuggingFace PEFT GitHub repo — LoRA filter pattern: `filter(lambda p: p.requires_grad, model.parameters())` cleanly selects only injected adapters.
- Key insight: LoRA trainable parameters are isolated via `requires_grad=True` flag on A/B matrices only; base model frozen. This is the standard pattern for disjoint parameter isolation.

**Query 2: "joint multi-parameter gradient training stability convergence"**
- Results: diffusers SDXL training scripts showing dual-optimizer pattern (UNet LoRA + text encoder LoRA in single AdamW with separate parameter groups).
- Key insight: Multiple adapter groups can safely share a single AdamW optimizer by splitting into parameter groups with independent learning rates — standard PyTorch pattern.

**Query 3: "LoRA fine-tuning LLM PEFT training stability AdamW"**
- HuggingFace PEFT docs: confirmed AdamW as standard optimizer; separate LRs for different parameter groups is best practice.
- Flash-attention repo: confirms chunked attention is compatible with gradient computation.

### Archon Code Examples

**Code Example 1: "Initialize Optimizer with LoRA Layers" (HuggingFace diffusers)**
```python
optimizer = optimizer_cls(
    lora_layers,
    lr=args.learning_rate,
    betas=(args.adam_beta1, args.adam_beta2),
    weight_decay=args.adam_weight_decay,
    eps=args.adam_epsilon,
)
```
- Pattern: Single optimizer over `lora_layers` (filtered trainable params)
- Insight: For JointLoRA-KV, extend `lora_layers` to include both LoRA A/B AND Locret retaining head weights, with separate LR entries via parameter groups.

**Code Example 2: "Configure and Add LoRA Adapters" (HuggingFace diffusers)**
```python
text_lora_config = LoraConfig(
    r=args.rank,
    lora_alpha=args.rank,
    init_lora_weights="gaussian",
    target_modules=["q_proj", "k_proj", "v_proj", "out_proj"],
)
text_encoder_one.add_adapter(text_lora_config)
lora_params = list(filter(lambda p: p.requires_grad, text_encoder_one.parameters()))
```
- Pattern: `target_modules` specifies Q/K/V projections; all other parameters remain frozen.
- Insight: Locret retaining heads are separate MLP modules appended to attention layers — NOT in `target_modules`. Their `requires_grad` is controlled independently, confirming parameter disjointness.

### Exa GitHub Implementations

**Query 1: "Locret KV cache eviction joint training LoRA LLM GitHub implementation"**

**Repository 1: huangyuxiang03/Locret** (Official — ⭐ primary reference)
- **URL:** https://github.com/huangyuxiang03/Locret
- **Relevance:** Official Locret implementation supporting LLaMA-3.1-8B-instruct; exactly the base we extend.
- **Architecture:** Retaining heads = small MLP injected per attention layer: `S̃ = R([Q,K,V]) = σ([Q,K,V]W₁)W₂`; trained while backbone frozen.
- **Training Script:** `locret/train/train.py` — runs `data_gen.py` then `train.py`; hyperparameters auto-set per paper.
- **Key insight:** Original Locret trains retaining heads with LM distillation loss on QA data. JointLoRA-KV replaces this with task classification CE loss AND simultaneously trains LoRA A/B in the same backward pass.
- **Model support:** LLaMA-3.1-8B-instruct confirmed.

**Repository 2: ngocbh/trimkv** (Related — learnable KV eviction)
- **URL:** https://github.com/ngocbh/trimkv
- **Relevance:** Learnable KV retention with LoRA training scripts, includes LongBench evaluation; uses similar architectural pattern.
- **Baselines included:** LocRet, H2O, SnapKV, StreamingLLM — confirms our baseline set is standard.
- **LongBench integration:** `THUDM/LongBench` is the canonical eval framework used by the community.

**Repository 3: awslabs/keys_values** (Joint LoRA+KV fine-tuning)
- **URL:** https://github.com/awslabs/keys_values
- **Relevance:** Implements `finetune_offload_lora` mode — trains LoRA adapter weights jointly with KV cache policy in a single fine-tuning loop using custom `KVCacheScatterUpdateAndSDPAFunction` with backward support.
- **Key insight:** Confirms technical feasibility of joint LoRA + KV policy gradient computation via PyTorch autograd; replay caches used for backward pass.
- **Training config:** Separate `kv_cache.cache_length` and `chunk_size`; LoRA-specific args `lora_rank` and `lora_alpha`.

**Serena Analysis Needed:** false (code patterns sufficiently clear from Exa results)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

JointLoRA-KV is a novel combination — no single official repository exists. Implementation priority:

1. **Primary:** Extend `huangyuxiang03/Locret` training script to add LoRA injection (via HuggingFace PEFT) and replace LM distillation loss with task CE loss; both parameter groups share AdamW with separate LRs.
2. **Secondary:** Reference `awslabs/keys_values` for joint backward pass pattern (replay caches, `KVCacheScatterUpdateAndSDPAFunction`).
3. **Tertiary:** Reference `ngocbh/trimkv` for LongBench eval integration and baseline comparisons.

**Recommended Implementation Path:**
- Primary: Extend `huangyuxiang03/Locret` (`locret/train/train.py`) with PEFT LoRA injection + task CE loss
- Fallback: Build from scratch using HuggingFace PEFT + custom Locret head registration
- Justification: Locret official repo already handles LLaMA-3.1-8B retaining head registration, chunked prefill, and checkpoint management. Extending it minimizes implementation risk.

### Code Analysis (Serena MCP)

*Skipped* - No local codebase; relying on Locret official repo code from Exa search. Code patterns are sufficiently clear from Exa results: Locret retaining heads are separate MLP modules; LoRA A/B matrices are injected via PEFT `target_modules`. Both are independently parameterized with no shared tensors.

---

## Experiment Specification

### Dataset

**Dataset 1: GLUE Benchmark (Training + Stability monitoring)**
- **Name:** GLUE — MNLI, SST-2, QNLI subtasks
- **Type:** standard
- **Source:** HuggingFace Hub (`nyu-mll/glue`)
- **Splits:** train (MNLI: 392,702 / SST-2: 67,349 / QNLI: 104,743), validation (MNLI: 9,815 / SST-2: 872 / QNLI: 5,463)
- **Role in H-M2:** Training data for joint optimization; stability monitoring via training loss curves
- **Hypothesis Fit:** GLUE tasks provide task classification CE loss for joint backward pass; short-context tasks (≤512 tokens) minimize confounds from KV budget at training time

**Dataset 2: LongBench-QA (Primary Evaluation)**
- **Name:** LongBench — NarrativeQA, Qasper, MultiFieldQA-en subtasks
- **Type:** standard
- **Source:** HuggingFace Hub (`THUDM/LongBench`) or GitHub (`THUDM/LongBench`)
- **Splits:** Test sets — NarrativeQA: 200 examples / Qasper: 200 examples / MultiFieldQA-en: 150 examples (full test sets)
- **Role in H-M2:** Primary accuracy evaluation at 50% KV budget; comparison to B3 baseline
- **Hypothesis Fit:** Long-context QA meaningfully activates KV eviction at 50% budget; F1 score captures QA quality

**Synthetic Data Policy:** ✅ CONFIRMED — both GLUE and LongBench are real, established standard benchmarks. No synthetic data.

**Loading Information:**
- Method: HuggingFace `datasets` + `THUDM/LongBench` eval scripts
- Identifier: `"nyu-mll/glue"` (GLUE); `"THUDM/LongBench"` (LongBench)
- Code:
```python
from datasets import load_dataset
# GLUE
mnli = load_dataset("nyu-mll/glue", "mnli")
sst2 = load_dataset("nyu-mll/glue", "sst2")
qnli = load_dataset("nyu-mll/glue", "qnli")
# LongBench
narrativeqa = load_dataset("THUDM/LongBench", "narrativeqa", split="test")
qasper = load_dataset("THUDM/LongBench", "qasper", split="test")
multifieldqa = load_dataset("THUDM/LongBench", "multifieldqa_en", split="test")
```

### Models

#### Baseline Model

**B3: LoRA → Sequential Locret Fine-tune (Primary Baseline)**
- **Architecture:** LLaMA-3.1-8B + LoRA (r=16, α=32, Q/K/V) → frozen LoRA → Locret retaining heads (LM distillation loss)
- **Training:** Two-stage: (1) LoRA fine-tune on GLUE CE loss, (2) freeze LoRA, train Locret retaining heads on LM distillation objective
- **Source:** `huangyuxiang03/Locret` (official training script adapted for GLUE)
- **Expected Performance:** ~1–2% below vanilla LoRA on GLUE; ~3–5% below on LongBench at 50% KV budget (from Phase 2B analysis)

**Loading Information:**
- Method: HuggingFace transformers + PEFT
- Identifier: `"meta-llama/Meta-Llama-3.1-8B"`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3.1-8B",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
lora_config = LoraConfig(
    r=16, lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj"],
    lora_dropout=0.05, bias="none"
)
model = get_peft_model(model, lora_config)
```

#### Proposed Model

**Architecture:** LLaMA-3.1-8B + LoRA (r=16) + Locret retaining heads — JOINTLY trained in single backward pass

**Core Mechanism Implementation:**

```python
# JointLoRA-KV: Single-backward-pass joint optimization
# Based on: huangyuxiang03/Locret + HuggingFace PEFT
# Source: awslabs/keys_values (joint backward pattern)

class JointLoRAKVTrainer:
    def __init__(self, model, lora_lr=1e-4, locret_lr=5e-4):
        # LoRA params: injected A/B matrices via PEFT (requires_grad=True)
        lora_params = [p for n, p in model.named_parameters()
                       if "lora_" in n and p.requires_grad]
        # Locret params: retaining head MLPs (registered separately)
        locret_params = [p for n, p in model.named_parameters()
                         if "retaining_head" in n and p.requires_grad]
        # Shared optimizer with separate LRs (disjoint parameter sets)
        self.optimizer = AdamW([
            {"params": lora_params, "lr": lora_lr},
            {"params": locret_params, "lr": locret_lr}
        ], weight_decay=0.01)

    def train_step(self, batch, kv_budget_ratio=0.5):
        # Forward: soft KV scoring during training, hard eviction at inference
        logits, soft_kv_scores = model(batch["input_ids"],
                                        kv_budget=kv_budget_ratio,
                                        training=True)
        # Single CE loss drives both LoRA and Locret gradients
        loss = F.cross_entropy(logits, batch["labels"])
        # Single backward: gradients flow to both lora_params and locret_params
        loss.backward()
        # Gradient monitoring: detect divergence (spike >2x) or NaN
        if torch.isnan(loss) or loss.item() > 2 * self.prev_loss:
            self.log_divergence_event(loss)
        self.optimizer.step(); self.optimizer.zero_grad()
        return loss
```

### Training Protocol

**Optimizer:** AdamW with separate parameter groups (confirmed by Archon/Exa)
- LoRA A/B matrices: lr=1e-4 (standard PEFT lr from HuggingFace PEFT docs)
- Locret retaining heads: lr=5e-4 (from Phase 2B controlled variables; Locret paper: higher lr for head training)
- betas=(0.9, 0.999), weight_decay=0.01, eps=1e-8

**Learning Rate Schedule:** Linear warmup (10% steps) + cosine decay
- **Source:** Standard for LLM PEFT fine-tuning (HuggingFace PEFT docs)

**Batch Size:** 8 (per GPU, gradient accumulation × 4 = effective batch 32)
- **Source:** Standard for LLaMA-3.1-8B single-GPU fine-tuning (HuggingFace PEFT forum)

**Epochs:** 3 epochs on GLUE training splits
- **Source:** Phase 2B controlled variables; standard for GLUE classification fine-tuning

**Loss Function:** Task classification cross-entropy on GLUE labels
- Applied to both LoRA logits and used to back-propagate through soft KV scores
- **Source:** H-M2 hypothesis mechanism definition

**KV Budget:** budget_ratio=0.5 (50% KV retention) during BOTH training and inference
- Soft scoring during training (differentiable), hard eviction at inference
- **Source:** Phase 2B controlled variables; EF3 (soft-to-hard training pattern)

**Seeds:** 42, 123, 456 (3 seeds for stability verification)
- **Source:** Phase 2B controlled variables — stability across seeds is the primary gate criterion

**Stability Monitoring:**
- Log training loss per step for all 3 seeds
- Flag divergence: loss spike >2× moving average OR NaN
- Flag instability: loss std across seeds > 0.1 at epoch 1 end
- **Source:** H-M2 verification protocol (Step 5 in Phase 2B spec)

### Evaluation

**Primary Metrics (LongBench-QA at 50% KV budget):**

| Task | Metric | Evaluation Script |
|------|--------|------------------|
| NarrativeQA | F1 (qa_f1_score) | THUDM/LongBench eval.py |
| Qasper | F1 (qa_f1_score) | THUDM/LongBench eval.py |
| MultiFieldQA-en | F1 (qa_f1_score) | THUDM/LongBench eval.py |
| **Mean LongBench-QA F1** | Average across 3 tasks | Primary gate metric |

**Stability Metrics (Training):**
- Loss convergence: max(loss_seed_i) / mean(loss_all_seeds) ≤ 2.0 for all seeds
- NaN events: 0 across all 3 seeds
- **Source:** H-M2 verification protocol

**Success Criteria (MUST_WORK gate):**
1. **Stability:** Zero NaN events, no divergence (loss spike >2×) across 3 seeds → Confirms gradient path disjointness
2. **Accuracy:** JointLoRA-KV mean LongBench-QA F1 ≥ B3 mean LongBench-QA F1 at 50% KV budget → Confirms no regression from joint training

**Expected Baseline B3 Performance:** ~50–60% F1 on LongBench-QA at 50% KV budget (from Locret paper: ~10% degradation from full-KV baseline; LLaMA-3.1-8B full-KV LongBench ~60–65%)

**Metrics Loading Information:**
- Task Type: QA + classification (multi-task)
- Library: THUDM/LongBench `eval.py` (qa_f1_score); `torchmetrics` or manual for GLUE accuracy
- Code:
```python
# LongBench F1 (from THUDM/LongBench/LongBench/metrics.py)
from metrics import qa_f1_score
score = qa_f1_score(prediction, ground_truth)

# GLUE accuracy (secondary)
from sklearn.metrics import accuracy_score
acc = accuracy_score(y_true, y_pred)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — JointLoRA-KV vs B3 LongBench-QA F1 (per task + mean)

#### Additional Figures (LLM Autonomous)
- Training loss curves (all 3 seeds, per-step) — for stability visualization
- Loss distribution per seed at epoch end (box plot) — to show stability consistency
- Per-task F1 breakdown (NarrativeQA, Qasper, MultiFieldQA-en) for JointLoRA-KV vs B3
- Gradient norm plot (LoRA group vs Locret group over training) — to show independent gradient paths

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error across 3 seeds
2. Zero NaN / divergence events
3. JointLoRA-KV LongBench-QA F1 ≥ B3 F1

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** HuggingFace PEFT docs — LoRA conceptual guide
- **Query:** "joint LoRA KV cache training optimization"
- **URL:** https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora
- **Key Insights:** LoRA injects A/B matrices into Q/K/V; filtered via `requires_grad`; independent from other module parameters
- **Used For:** Confirming parameter disjointness; optimizer parameter group design

**Source A.2:** HuggingFace PEFT GitHub repo
- **Query:** "LoRA fine-tuning LLM PEFT training stability AdamW"
- **URL:** https://github.com/huggingface/peft
- **Key Insights:** Standard AdamW lr=1e-4 for LoRA; `get_peft_model()` pattern; parameter filtering
- **Used For:** Training protocol (optimizer, LR)

**Source A.3:** Archon code example — "Initialize Optimizer with LoRA Layers"
- **URL:** https://huggingface-projects-docs-llms-txt.hf.space/diffusers/llms.txt
- **Key Code:** `optimizer = optimizer_cls(lora_layers, lr=lr, betas=..., weight_decay=..., eps=...)`
- **Used For:** JointLoRA-KV optimizer design (extended to two parameter groups)

**Source A.4:** Archon code example — "Configure and Add LoRA Adapters"
- **URL:** https://huggingface-projects-docs-llms-txt.hf.space/diffusers/llms.txt
- **Key Code:** `LoraConfig(r=rank, lora_alpha=rank, target_modules=["q_proj","k_proj","v_proj","out_proj"])`
- **Used For:** LoRA configuration spec (r=16, target Q/K/V)

### B. GitHub Implementations (Exa)

**Repository B.1: huangyuxiang03/Locret** (⭐ PRIMARY)
- **URL:** https://github.com/huangyuxiang03/Locret
- **Query:** "Locret KV cache eviction joint training LoRA LLM GitHub implementation"
- **Relevance:** Official Locret implementation; supports LLaMA-3.1-8B; defines retaining head architecture
- **Architecture Extracted:**
  - Retaining head: small MLP per attention layer: `S̃ = σ([Q,K,V]W₁)W₂`
  - Training: `cd locret/train && python data_gen.py && python train.py`
  - Checkpoints: `locret/train/checkpoints/`; `convert.py` for safetensors → pytorch
- **Used For:** Baseline architecture, retaining head design, training script extension pattern

**Repository B.2: ngocbh/trimkv**
- **URL:** https://github.com/ngocbh/trimkv
- **Query:** "Locret KV cache eviction joint training LoRA LLM GitHub implementation"
- **Relevance:** Learnable KV eviction with LongBench evaluation; baseline suite includes LocRet
- **LongBench eval:** `train/llm/scripts`; eval metrics align with `THUDM/LongBench`
- **Used For:** LongBench evaluation methodology; confirming baseline set (LocRet, H2O, SnapKV)

**Repository B.3: awslabs/keys_values**
- **URL:** https://github.com/awslabs/keys_values
- **Query:** "joint LoRA adapter KV cache co-optimization single backward pass PyTorch LLM fine-tuning"
- **Relevance:** Directly implements joint LoRA fine-tuning + KV cache policy in a single training loop
- **Key Pattern:** `finetune_offload_lora` mode; replay caches for backward pass; custom `KVCacheScatterUpdateAndSDPAFunction`
- **Used For:** Joint backward pass feasibility confirmation; training stability patterns

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — no local codebase. Code from Exa search results (Locret official repo architecture, HuggingFace PEFT patterns) was sufficiently clear for pseudo-code generation.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-E1
- **Key findings reused:** Confirmed mean Spearman ρ=0.3662 (misalignment exists); 100% of 100 MNLI examples showed ρ < 0.7.
- **Why relevant to H-M2:** H-E1 confirmed that task-gradient signals differ from LM-predictive heuristics, motivating joint training. H-M2 now validates technical feasibility of the joint backward pass.
- **Controlled variables inherited:** LLaMA-3.1-8B, LoRA r=16, seeds 42/123/456, budget_ratio=0.5

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset 1 (GLUE) | Phase 2B controlled variables | 02b_verification_plan.md §1.3 |
| Dataset 2 (LongBench) | Phase 2B controlled variables | 02b_verification_plan.md §1.3 |
| Model (LLaMA-3.1-8B) | Phase 2B controlled variables | 02b_verification_plan.md §1.3 |
| LoRA config (r=16, Q/K/V) | Archon KB + Phase 2B | A.4, 02b_verification_plan.md |
| Locret retaining head arch | Exa GitHub | B.1 (official repo) |
| Optimizer (AdamW, dual LR) | Archon KB + Phase 2B | A.2, A.3, 02b_verification_plan.md |
| LoRA LR (1e-4) | Archon KB | A.2 (HuggingFace PEFT docs) |
| Locret LR (5e-4) | Phase 2B controlled variables | 02b_verification_plan.md §1.3 |
| Joint backward pattern | Exa GitHub | B.3 (awslabs/keys_values) |
| LongBench evaluation | Exa GitHub | B.2 (trimkv), B.1 (Locret) |
| Stability criteria (2× spike) | H-M2 verification protocol | 02b_verification_plan.md §H-M2 |
| Seeds (42, 123, 456) | Phase 2B controlled variables | 02b_verification_plan.md §1.3 |
| Core mechanism pseudo-code | Exa GitHub + Archon | B.1, B.3, A.3 |
| Success criteria (≥ B3 F1) | H-M2 hypothesis statement | 02b_verification_plan.md §H-M2 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-20T03:07:00+00:00

### Workflow History for This Hypothesis
- 2026-05-20T03:06:35: H-M2 set to IN_PROGRESS (external loop)
- 2026-05-20T03:07:00: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Skipped — no local codebase)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
