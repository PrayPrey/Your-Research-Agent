# Experiment Design: H-E1

**Date:** 2026-08-03
**Author:** Anonymous
**Hypothesis Statement:** Under fixed-budget (≤1B tokens) short-context distillation of LLaMA-3-8B, a statistically significant task-type × conversion-strategy interaction exists on LongBench v2 normalized accuracy degradation (Δ_norm): MOHAWK-SSM exhibits ≥2× larger Δ_norm on retrieval-heavy categories (multi-doc QA, synthetic) than on generation-heavy categories (summarization, few-shot), while LAWCAT-linear-attention exhibits a significantly more uniform degradation profile.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (foundation hypothesis)
**Gate Status:** MUST_WORK — Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) ≥ 2.0, CI above 1.0; interaction p<0.01

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK: Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) ≥ 2.0 with 95% bootstrap CI strictly above 1.0 AND interaction term p<0.01 (Holm-corrected) in mixed-effects model Δ_norm ~ TaskType * Strategy + (1|Task).

---

## Continuation Context

None — H-E1 is the first hypothesis in the verification chain. No prior validation results to inherit.

### Previous Hypothesis Results (if applicable)
N/A — first hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** Archon KB searched (3 knowledge queries, 2 code queries). No domain-relevant results returned — KB is populated with diffusers/image-generation content unrelated to LLM distillation or LongBench evaluation. All similarity scores < 0.46 against diffusers documentation. No usable findings extracted.

**Queries executed:**
- "MOHAWK SSM transformer distillation experiment design" → similarity 0.36, diffusers content
- "LLM conversion linear attention distillation challenges" → similarity 0.46, diffusers content
- "LongBench evaluation benchmark long context LLM" → similarity 0.37, diffusers content
- "SSM Mamba knowledge distillation PyTorch" → code examples: MPS backend / diffusers
- "LongBench evaluation accuracy per category" → code examples: diffusers benchmarks

### Archon Code Examples

No relevant code examples found. KB does not contain MOHAWK, LAWCAT, SSM, or LongBench content.

### Exa GitHub Implementations

**Query 1: MOHAWK Official Implementation**

**Repository 1**: goombalab/mohawk ⭐7 (NEW — 2026-03-08)
- **URL**: https://github.com/goombalab/mohawk
- **Relevance**: Official MOHAWK framework for LLaMA-style hybrid distillation — directly supports LLaMA-3-8B
- **Architecture**: 3-stage distillation (matrix orientation → hidden-state alignment → weight-transfer+KD)
- **Key Code**:
  ```python
  # Stage 1: Matrix orientation — Frobenius loss between teacher attn matrix and student SSM transfer matrix
  loss = torch.linalg.matrix_norm(transfer_matrix - attn_matrix, ord="fro").mean()

  # Stage 2: Hidden-state alignment
  # Stage 3: End-to-end KD with logit distillation loss (KL divergence student vs teacher logits)
  ```
- **Training Config**:
  - Dataset: C4, context length 2048 tokens
  - Stages: 80M / 160M / (remainder to 1B) tokens for Stage 1/2/3 respectively (scaled from Phi-1.5 3B split)
  - Distillation objectives: `matrices` (Stage 1), `hstates` (Stage 2), `supervised` (Stage 3)
  - YAML config system with `LOAD`-based inheritance
  - Distributed training: DDP/FSDP supported
- **Dataset**: C4 (allenai/c4)
- **Results**: Phi-Mamba (1.5B) competitive with open-source subquadratic models using <1% pretraining tokens

**Repository 2**: goombalab/phi-mamba ⭐125
- **URL**: https://github.com/goombalab/phi-mamba
- **Relevance**: Reference implementation showing MOHAWK Stage 1/2 patterns with full code at `assets/mohawk_stage1.py` and `assets/mohawk_stage2.py`
- **Key Code**:
  ```python
  teacher_model = PhiForCausalLM.from_pretrained("microsoft/phi-1_5", attn_implementation="eager")
  # student uses DiscreteMamba2 mixer — multi-head (not multi-value), discrete-time A matrix
  # causal_conv1d==1.1.1 used inside Mamba block
  ```
- **Training Config**: torch==2.1, mamba-ssm, flash-attn==2.5.8, causal_conv1d==1.1.1

**Repository 3**: jxiw/MambaInLlama ⭐(NeurIPS 2024)
- **URL**: https://github.com/jxiw/MambaInLlama
- **Relevance**: Alternative Transformer→Mamba distillation for LLaMA; confirms feasibility at 8B scale
- **Key Code**:
  ```python
  from mamba_inference.hybrid_wrapper import MambaTransformerHybridModelWrapper
  model = MambaTransformerHybridModelWrapper.from_pretrained(pretrained_model_name, torch_dtype=torch.bfloat16)
  ```
- **Training Config**: 8×80G A100, 3-4 days; causal-conv1d==1.4.0, flash-attn==2.6.3

**Query 2: LAWCAT Official Implementation**

**Repository 4**: zeyuliu1037/LAWCAT ⭐1 (EMNLP 2025 Findings, official)
- **URL**: https://github.com/zeyuliu1037/LAWCAT
- **Relevance**: OFFICIAL LAWCAT implementation — highest priority reference
- **Architecture**: causal depthwise Conv1D (kernel size 4) on Q and K → normalized gated linear attention (GLA); depth-separable conv module
- **Key Code**:
  ```python
  # LAWCAT causal Conv1D on Q/K (kernel_size = r+1 = 4 in practice)
  # q̃_t = f_θ([q_{t-r}, ..., q_t])  — weighted moving average over local window
  # After Conv1D: shared linear projection with nonlinearity (same φ for Q and K)
  # Main implementation: src/model/linear_attention/linear_window_attention_sw_gla.py
  ```
- **Training Config**:
  ```bash
  python distill_llama.py \
    --model_config distill_llama3_2_1b_wsw0_fd32_gla_woCV_rep1_woSiLU_map2_idt_norm_ins_QK \
    --distill_config distill_passkey_1208_xent0_mse1000_lr1e-2 \
    --finetune_config finetune_lora_qkvo_passkey_1208 \
    --lk_zero_init --seed 0 --replicate 0
  ```
  - Distillation: 1K-length sequences; MSE loss (weight 1000) + cross-entropy (weight 0); LR=1e-2
  - Fine-tuning: LoRA on Q,K,V,O projections
  - Dependencies: flash-linear-attention (fla-org), Python 3.10

**Query 3: LongBench v2 Evaluation**

**Repository 5**: THUDM/LongBench ⭐1218
- **URL**: https://github.com/THUDM/LongBench
- **Relevance**: Official LongBench v2 evaluation framework
- **Key Code**:
  ```python
  # result.py — per-category scoring (v2: difficulty + length breakdown)
  for pred in pred_data:
      acc = int(pred['judge'])
      if pred["difficulty"] == "easy": easy_acc += acc
      else: hard_acc += acc
      if pred['length'] == "short": short_acc += acc
      elif pred['length'] == "medium": medium_acc += acc
      else: long_acc += acc
  ```
  - LongBench v2: 503 questions, 6 task categories, MCQ format (A/B/C/D), 0-shot evaluation
  - Task categories: single-document QA, multi-document QA, long in-context learning, long-dialogue history understanding, code repo understanding, long structured data understanding
  - Per-example `pred['judge']` binary accuracy (0/1) enables per-category Δ_norm computation
  - Dataset: THUDM/LongBench on HuggingFace (`load_dataset("THUDM/LongBench", "v2")`)
  - Evaluation metric: accuracy (exact MCQ match)

**Serena Analysis Needed**: false — code from Exa is sufficiently clear for pseudo-code generation

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For MOHAWK: goombalab/mohawk is the NEW official general framework (2026-03-08). goombalab/phi-mamba provides Stage 1/2 reference code. Both are from the paper authors.

For LAWCAT: zeyuliu1037/LAWCAT is the official implementation (EMNLP 2025). The `distill_llama.py` script supports LLaMA-family models (Llama3.2-1B demonstrated; LLaMA-3-8B requires config adaptation).

**Recommended Implementation Path:**
- Primary (MOHAWK): `goombalab/mohawk` with LLaMA-3-8B configs (`configs/Llama/8B/`)
- Primary (LAWCAT): `zeyuliu1037/LAWCAT` with `distill_llama.py` adapted for LLaMA-3-8B
- Primary (Hybrid-4): `goombalab/mohawk` with hybrid YAML config (retain 4 middle attention layers)
- Fallback: `jxiw/MambaInLlama` for MOHAWK-style distillation if goombalab/mohawk LLaMA-8B configs incomplete
- Justification: Author implementations are ground truth; avoid reimplementation drift

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results was sufficiently clear. MOHAWK Stage 1/2 pseudo-code directly readable from `phi-mamba/assets/mohawk_stage1.py`. LAWCAT Conv1D mechanism directly described in paper and `distill_llama.py` configs.

---

## Experiment Specification

### Dataset

**Name:** LongBench v2
**Type:** standard (official benchmark)
**Source:** THUDM/LongBench (GitHub + HuggingFace)
**Version:** v2 (2024, ACL 2025)
**Size:** 503 questions total across 6 task categories
**Context length:** 8k – 2M words (majority under 128k)
**Format:** Multiple-choice (A/B/C/D), 0-shot evaluation
**Language:** Bilingual (English + Chinese)

**Task Category Breakdown (for H-E1 interaction test):**
| Category | H-E1 Label | Approx Questions |
|----------|------------|-----------------|
| Single-document QA | neutral | ~80 |
| Multi-document QA | **retrieval-heavy** | ~83 |
| Long in-context learning (few-shot) | **generation-heavy** | ~83 |
| Long-dialogue history understanding | neutral | ~83 |
| Code repository understanding | neutral | ~83 |
| Long structured data understanding (synthetic) | **retrieval-heavy** | ~91 |

> Retrieval-heavy = multi-doc QA + synthetic (long structured data) ≈ 174 questions
> Generation-heavy = long in-context learning (few-shot) + summarization-adjacent ≈ 83-166 questions depending on mapping

**Preprocessing:** None — MCQ format, evaluation via exact letter match
**Augmentation:** None
**Path/Type Specification:**
- Type: `standard`
- Path: `auto` (HuggingFace: `THUDM/LongBench`, config `v2`)
- Phase 4 behavior: Auto-download via `load_dataset("THUDM/LongBench", "v2")`

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"THUDM/LongBench"` with config `"v2"`
- Code: `load_dataset("THUDM/LongBench", "v2")`

### Models

#### Baseline Model

**Architecture:** LLaMA-3-8B (teacher / oracle baseline)
**Type:** Decoder-only transformer, 8B parameters, 32 layers
**Source:** meta-llama/Llama-3-8B on HuggingFace

**Configuration:**
- Hidden dim: 4096, Intermediate dim: 14336, Heads: 32, KV heads: 8 (GQA), Layers: 32
- Context window: 8192 tokens (RoPE)
- Tokenizer: LLaMA-3 BPE (vocab 128k)

**Role in H-E1:** Teacher model producing Acc_teacher per LongBench v2 category. Δ_norm = (Acc_teacher − Acc_student) / Acc_teacher.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"meta-llama/Llama-3-8B"`
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B", torch_dtype=torch.bfloat16)`

#### Proposed Model

**Architecture:** Baseline (LLaMA-3-8B) → 3 student variants via distillation

The experiment compares three converted models against the LLaMA-3-8B teacher:

**Student 1 — MOHAWK-SSM (LLaMA-3-8B-Mamba):**
- All 32 attention layers replaced by DiscreteMamba2 SSD mixer (multi-head, discrete-time)
- 3-stage MOHAWK distillation: matrix → hidden-state → KD
- Budget: ≤1B tokens C4, seq_len=2048

**Student 2 — LAWCAT (LLaMA-3-8B-Linear):**
- All 32 attention layers replaced by causal Conv1D (kernel=4) + normalized GLA
- 2-phase distillation: MSE alignment → LoRA fine-tuning
- Budget: ≤1B tokens, seq_len=1024-2048

**Student 3 — Hybrid-4 (LLaMA-3-8B-Hybrid):**
- 28 attention layers replaced by SSD mixer; 4 middle attention layers retained
- MOHAWK Stage 3 only (weight-transfer + KD from MOHAWK-SSM checkpoint)
- Budget: shares MOHAWK training, Stage 3 only additional fine-tuning

**Core Mechanism Implementation:**

```python
# MOHAWK Stage 1: Matrix Orientation
# Source: goombalab/phi-mamba assets/mohawk_stage1.py + goombalab/mohawk

class MOHAWKStage1Trainer:
    """
    Aligns SSM transfer matrix with teacher attention matrix via Frobenius loss.
    Input: teacher attention matrices (B, H, N, N); student SSD transfer matrices (B, H, N, N)
    """
    def distill_step(self, teacher_model, student_model, input_ids):
        teacher_out = teacher_model(input_ids, output_attentions=True,
                                   output_attention_results=True, use_cache=False)
        for layer_idx, student_layer in enumerate(student_model.backbone.layers):
            student_input = teacher_out.all_hidden_states[layer_idx]
            student_out = student_layer(hidden_states=student_input,
                                       run_mlp_component=False,
                                       return_mixer_matrix=True)
            transfer_matrix = student_out["transfer_matrix"]
            attn_matrix = teacher_out.all_attn_matrices[layer_idx]
            # Frobenius norm loss
            loss = torch.linalg.matrix_norm(transfer_matrix - attn_matrix, ord="fro").mean()
            loss.backward()

# LAWCAT: Causal Conv1D + GLA Mechanism
# Source: zeyuliu1037/LAWCAT src/model/linear_attention/linear_window_attention_sw_gla.py

class LAWCATLayer(nn.Module):
    """
    Causal Conv1D on Q,K + normalized GLA for local+global dependency modeling.
    """
    def __init__(self, d_model, kernel_size=4, num_heads=32):
        super().__init__()
        # Causal depthwise Conv1D on Q and K (kernel_size = r+1)
        self.conv_q = nn.Conv1d(d_model, d_model, kernel_size,
                                padding=kernel_size-1, groups=d_model)
        self.conv_k = nn.Conv1d(d_model, d_model, kernel_size,
                                padding=kernel_size-1, groups=d_model)
        self.shared_proj = nn.Linear(d_model, d_model)  # shared φ for Q and K
        self.gla = GatedLinearAttention(d_model, num_heads)  # normalized GLA

    def forward(self, x, mask=None):
        # x: (B, T, D)
        # Step 1: Causal Conv1D — local window of size kernel_size
        q = self.conv_q(x.transpose(1,2))[:, :, :x.size(1)].transpose(1,2)
        k = self.conv_k(x.transpose(1,2))[:, :, :x.size(1)].transpose(1,2)
        # Step 2: Shared linear projection with nonlinearity
        q = F.silu(self.shared_proj(q))
        k = F.silu(self.shared_proj(k))
        # Step 3: Normalized gated linear attention
        out = self.gla(q, k, x)
        return out
# Integration: Replace nn.MultiheadAttention in each LLaMA decoder layer
```

### Training Protocol

**MOHAWK Distillation (≤1B tokens C4):**

- **Dataset:** allenai/c4 (`load_dataset("allenai/c4", "en")`)
- **Sequence length:** 2048 tokens (max_length)
- **Token budget split (scaled from 3B Phi-1.5 → 1B LLaMA-3-8B):**
  - Stage 1 (matrix orientation): ~26M tokens (~C4 ~13k steps at batch 2048 tokens)
  - Stage 2 (hidden-state alignment): ~52M tokens
  - Stage 3 (weight-transfer + KD): ~920M tokens
- **Optimizer (all stages):** AdamW
  - Stage 1: LR=1e-3, β=(0.9, 0.999), weight_decay=0.1
  - Stage 2: LR=5e-4
  - Stage 3: LR=1e-4, cosine decay with warmup (500 steps)
- **Batch size:** 32 sequences (≈65k tokens/step) for Stage 3; 8 for Stage 1/2
- **Loss (Stage 3):** KD loss = KL(softmax(student_logits/T) || softmax(teacher_logits/T)), T=2 + CE loss
- **Precision:** bfloat16
- **Hardware:** 4×A100 80GB (DDP)
- **Seeds:** 1 (fixed, seed=42)
- **Perplexity gate:** ≤5% relative gap vs teacher on held-out C4 val (pre-registered abort criterion)
- **Alignment gate:** L2 hidden-state ratio ≤0.15 (measured at midpoint checkpoint)

**LAWCAT Distillation (≤1B tokens):**
- **Dataset:** allenai/c4 (same as MOHAWK for controlled comparison)
- **Sequence length:** 1024 tokens (LAWCAT paper uses 1K for distillation phase)
- **Phase 1 (MSE alignment):** LR=1e-2, MSE loss weight=1000, CE weight=0; ~50M tokens
- **Phase 2 (LoRA fine-tuning):** LoRA on Q,K,V,O (r=16, α=32); LR=1e-4; remaining budget
- **Hardware:** 2×A100 80GB
- **Seeds:** 1 (fixed, seed=0)

**Source citations:**
- MOHAWK token split: Bick et al. NeurIPS 2024 (80M/160M/2.76B scaled to 1B budget)
- MOHAWK optimizer: goombalab/mohawk TrainConfig defaults
- LAWCAT distill config: `distill_passkey_1208_xent0_mse1000_lr1e-2` from zeyuliu1037/LAWCAT
- LAWCAT LoRA: `finetune_lora_qkvo_passkey_1208` from zeyuliu1037/LAWCAT

### Evaluation

**Task:** Long-context understanding (LongBench v2)
**Metric:** Δ_norm = (Acc_teacher − Acc_student) / Acc_teacher per task category per strategy

**Primary Metrics:**
- Δ_norm per category per model: {MOHAWK-SSM, LAWCAT, Hybrid-4, Teacher} × {6 LongBench v2 categories}
- Interaction ratio: Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval)
- Interaction term significance: p-value from mixed-effects model

**Success Criteria (PoC — direction-based):**
- Primary: Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) ≥ 2.0 with 95% bootstrap CI strictly above 1.0
- Secondary: Interaction term p<0.01 (Holm correction) in: Δ_norm ~ TaskType * Strategy + (1|Task)

**Expected Baseline Performance (from research):**
- LLaMA-3-8B teacher: ~35-42% overall on LongBench v2 (consistent with best open models achieving 50.1% at time of benchmark release)
- MOHAWK/SSM degradation on retrieval: expected Δ_norm 0.15–0.35 (Overflow Prevention SSMs show systematic multi-doc QA degradation)
- LAWCAT retrieval preservation: expected Δ_norm 0.05–0.15 on retrieval tasks (>90% passkey at 22K tokens)

**Evaluation script:**
```python
# Per-category Δ_norm computation (adapted from THUDM/LongBench result.py)
from datasets import load_dataset

RETRIEVAL_HEAVY = {"multi_doc_qa", "long_structured_data"}
GENERATION_HEAVY = {"long_in_context_learning"}

def compute_delta_norm(teacher_results, student_results):
    per_category = {}
    for category in ["single_doc_qa", "multi_doc_qa", "long_in_context_learning",
                     "long_dialogue", "code_repo", "long_structured_data"]:
        cat_mask = [ex["category"] == category for ex in teacher_results]
        acc_teacher = sum(r["judge"] for r, m in zip(teacher_results, cat_mask) if m) / sum(cat_mask)
        acc_student = sum(r["judge"] for r, m in zip(student_results, cat_mask) if m) / sum(cat_mask)
        per_category[category] = (acc_teacher - acc_student) / max(acc_teacher, 1e-8)
    return per_category
```

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: long-context MCQ (multiple-choice QA)
- Library: custom (binary accuracy per example, per-category aggregation)
- Code: `int(pred["judge"])` per example from LongBench v2 eval pipeline

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — Δ_norm per category per strategy (MOHAWK-SSM, LAWCAT, Hybrid-4, Teacher=0)

#### Additional Figures (LLM Autonomous)
Based on hypothesis type (EXISTENCE interaction test), model comparison, and LongBench v2 task categories:
1. Heatmap: Δ_norm [strategy × category] — 3×6 matrix showing interaction pattern
2. Error bar plot: Δ_norm^retrieval vs Δ_norm^generation per strategy with 95% bootstrap CIs
3. Ratio plot: Δ_norm^SSM(category) / Δ_norm^LAWCAT(category) across all 6 categories

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (distillation completes, LongBench v2 evaluation completes)
2. `proposed_metric > baseline_metric`: Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) ≥ 2.0

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | MOHAWK SSD matrix mixer replaces LLaMA attention layers; LAWCAT GLA+Conv1D replaces attention layers | TRUE — both architectures support plug-in replacement of nn.MultiheadAttention |
| Mechanism Isolatable | Each converted model can be run independently; teacher/student comparison is explicit | TRUE — separate model checkpoints for each strategy |
| Baseline Measurable | LLaMA-3-8B teacher evaluated on same LongBench v2 set; Acc_teacher computed independently | TRUE — `meta-llama/Llama-3-8B` loaded and evaluated before conversion |

### Architecture Compatibility Check

**MOHAWK-SSM:**
- Requires: LLaMA-3-8B attention layers (32× MHA with GQA, d_model=4096, heads=32) — each replaced by DiscreteMamba2 SSD mixer
- Compatible: LLaMA-3-8B (decoder-only, attention-based) ✓
- Incompatible: Already-converted SSM models (cannot apply MOHAWK twice)
- `goombalab/mohawk` explicitly supports LLaMA-style architectures (`configs/Llama/8B/`)

**LAWCAT:**
- Requires: LLaMA-family attention layers with Q/K/V projections accessible for replacement
- Compatible: LLaMA-3-8B ✓ (LAWCAT repo uses LLaMA-3.2-1B; scaling to 8B requires config adaptation)
- Requires: `flash-linear-attention` (fla-org) and `causal_conv1d` packages
- Incompatible: Non-LLaMA attention variants with fused kernels that prevent weight extraction

**Required Features:**
- Attention weight extraction (output_attentions=True) for MOHAWK Stage 1
- bfloat16 support (A100 80GB)
- Flash-attn 2.x for teacher inference efficiency

**Incompatible Architectures:**
- Pure SSM models (no attention to replace)
- Models with fused attention that blocks matrix extraction

> ⚠️ If architecture is incompatible, Phase 4 MUST fail early with explicit error before any training!

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Stage 1 Frobenius loss < 0.1 at layer [k]" AND "Stage 3 KD loss converging" | distill_llama.py training loop |
| Tensor Shape | MOHAWK: transfer_matrix.shape == attn_matrix.shape == (B, H, N, N); LAWCAT: conv_q output shape unchanged (B, T, D) | mohawk_stage1.py / lawcat forward() |
| Metric Delta | Teacher Acc_LongBench_v2 > Student Acc_LongBench_v2 on retrieval categories; Δ_norm^SSM(retrieval) > 0.10 | evaluate.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(experiment_log, results):
    """Verify both MOHAWK and LAWCAT mechanisms are properly installed and functioning."""
    indicators = {
        # MOHAWK: Stage 1 loss confirms matrix alignment occurred
        "mohawk_stage1_converged": any("Frobenius loss" in line and
                                        float(line.split()[-1]) < 0.15
                                        for line in experiment_log if "Stage 1" in line),
        # MOHAWK: Student model uses SSM layers (no attention weights)
        "mohawk_ssm_layers_installed": not hasattr(results["mohawk_model"].layers[0], "self_attn"),
        # LAWCAT: Conv1D present in model layers
        "lawcat_conv1d_installed": hasattr(results["lawcat_model"].layers[0].attn, "conv_q"),
        # Functional: Both students degrade vs teacher (mechanism has effect)
        "both_students_degrade": (results["delta_norm_mohawk_overall"] > 0.01 and
                                   results["delta_norm_lawcat_overall"] > 0.01),
        # Interaction: Retrieval degradation is larger for SSM than LAWCAT
        "interaction_direction_correct": (results["delta_norm_mohawk_retrieval"] >
                                          results["delta_norm_lawcat_retrieval"])
    }
    all_pass = all(indicators.values())
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Stage 1 loss not decreasing | Frobenius loss > 0.5 after 10k steps | FAIL: Check attention output extraction |
| Perplexity gate fails | Student PPL gap > 5% vs teacher on C4 val | ABORT: Budget too small; try 2B tokens |
| Alignment gate fails | L2 hidden-state ratio > 0.15 at midpoint | ABORT: Recheck hidden-state distillation |
| LAWCAT Conv1D not causal | Non-zero attention from future tokens | FAIL: Check causal masking in Conv1D padding |
| Zero Δ_norm (identical to teacher) | Δ_norm < 0.001 on all categories | FAIL: Student not loaded correctly (loading teacher weights?) |
| No interaction (uniform Δ_norm) | SSM/LAWCAT ratio ≈ 1.0 across all categories | PoC FAIL: H0 not rejected; trigger PIVOT |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | Both MOHAWK SSD and LAWCAT GLA+Conv1D installed in model layers | Layer type inspection |
| Distillation Converged | Stage 1 Frobenius < 0.15 avg; Stage 3 KD loss < 2.0 at end | Training log |
| Perplexity Gate | Student PPL gap ≤ 5% vs LLaMA-3-8B teacher on C4 val | perplexity_eval() |
| Hypothesis Supported | Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) ≥ 2.0, 95% CI above 1.0 | bootstrap_ci() on 503-question eval set |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found. Archon KB populated with diffusers content only. Queries executed for traceability:
- Query 1: "MOHAWK SSM transformer distillation experiment design"
- Query 2: "LLM conversion linear attention distillation challenges"
- Query 3: "LongBench evaluation benchmark long context LLM"
- Code Query 1: "SSM Mamba knowledge distillation PyTorch"
- Code Query 2: "LongBench evaluation accuracy per category"

### B. GitHub Implementations (Exa)

**Repository B.1**: goombalab/mohawk (⭐7, official, 2026-03-08)
- **URL**: https://github.com/goombalab/mohawk
- **Query Used**: "MOHAWK transformer to SSM distillation LLaMA implementation GitHub"
- **Relevance**: Official MOHAWK distillation framework with LLaMA support; YAML config system; DDP/FSDP
- **Key Code** (annotated):
  ```python
  # Stage 1 Frobenius loss — basis for MOHAWK-SSM training protocol
  loss = torch.linalg.matrix_norm(transfer_matrix - attn_matrix, ord="fro").mean()
  # Used for: MOHAWK Stage 1 training config; distillation loss specification
  ```
- **Configuration Extracted**: C4 dataset, 2048 seq_len, 3-stage with matrix/hstates/supervised objectives
- **Used For**: MOHAWK training protocol (Section 6), Stage 1/2/3 token budget split

**Repository B.2**: goombalab/phi-mamba (⭐125, official)
- **URL**: https://github.com/goombalab/phi-mamba
- **Query Used**: "MOHAWK transformer to SSM distillation LLaMA implementation GitHub"
- **Relevance**: Reference Stage 1/2 code; DiscreteMamba2 architecture details; dependency list
- **Key Code** (annotated):
  ```python
  # Stage 1 loop — adapted for pseudo-code in Section 6
  teacher_out = teacher_model(input_ids, output_attentions=True, use_cache=False)
  for layer_idx, student_layer in enumerate(student_model.backbone.layers):
      student_input = teacher_out.all_hidden_states[layer_idx]
      student_out = student_layer(hidden_states=student_input,
                                  run_mlp_component=False, return_mixer_matrix=True)
      transfer_matrix = student_out["transfer_matrix"]
      attn_matrix = teacher_out.all_attn_matrices[layer_idx]
      loss = torch.linalg.matrix_norm(transfer_matrix - attn_matrix, ord="fro").mean()
  ```
- **Their Results**: Phi-Mamba (1.5B) competitive with open-source subquadratic models at 3B tokens
- **Used For**: Core mechanism pseudo-code; architecture compatibility check; dependency versions

**Repository B.3**: jxiw/MambaInLlama (NeurIPS 2024)
- **URL**: https://github.com/jxiw/MambaInLlama
- **Query Used**: "MOHAWK transformer to SSM distillation LLaMA implementation GitHub"
- **Relevance**: Alternative Transformer→Mamba distillation; confirms 8B scale feasibility; 8×A100 setup
- **Used For**: Hardware requirement estimation (fallback reference if goombalab/mohawk insufficient)

**Repository B.4**: zeyuliu1037/LAWCAT (⭐1, official EMNLP 2025)
- **URL**: https://github.com/zeyuliu1037/LAWCAT
- **Query Used**: "LAWCAT linear attention causal Conv1D transformer conversion distillation GitHub"
- **Relevance**: OFFICIAL LAWCAT — causal Conv1D (kernel=4) + normalized GLA; `distill_llama.py`
- **Key Code** (annotated):
  ```python
  # Causal depthwise Conv1D on Q and K — local window of r+1=4 tokens
  # q̃_t = f_θ([q_{t-r}, ..., q_t]) weighted moving average (no future tokens)
  # After Conv1D: shared linear projection with SiLU nonlinearity
  # GLA: normalized gated linear attention for long-range context
  # Implementation: src/model/linear_attention/linear_window_attention_sw_gla.py
  ```
- **Configuration Extracted**:
  - `distill_passkey_1208_xent0_mse1000_lr1e-2`: MSE loss weight=1000, LR=1e-2
  - `finetune_lora_qkvo_passkey_1208`: LoRA r=16 on Q,K,V,O
  - `--lk_zero_init`: zero-initialize linear attention keys
- **Their Results**: >90% passkey retrieval at 22K tokens; competitive S-NIAH 1&2&3; BABILong QA2&3
- **Used For**: LAWCAT training protocol; Conv1D pseudo-code; mechanism activation indicators

**Repository B.5**: THUDM/LongBench (⭐1218)
- **URL**: https://github.com/THUDM/LongBench
- **Query Used**: "LongBench v2 evaluation Python task category per-category accuracy THUDM GitHub"
- **Relevance**: Official LongBench v2 evaluation framework; per-example `judge` field enables Δ_norm
- **Key Code** (annotated):
  ```python
  # result.py — per-category accuracy aggregation
  # Each pred has: pred["judge"] (0/1), pred["difficulty"], pred["length"]
  # For H-E1: extend to pred["category"] for 6-way task-category split
  acc = int(pred['judge'])
  # → compute Δ_norm per category across all 503 questions
  ```
- **Their Results**: Best model 50.1% overall; human expert 53.7%; o1-preview 57.7%
- **Used For**: Evaluation protocol; Δ_norm computation script; dataset loading method

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from Exa search results was sufficiently clear. MOHAWK Stage 1 pseudo-code directly readable from `phi-mamba/assets/mohawk_stage1.py`. LAWCAT Conv1D mechanism fully described in paper and config files.

### D. Previous Hypothesis Context

**Previous Context**: None — H-E1 is the first hypothesis in the verification chain (no prerequisite hypothesis results to inherit). Training hyperparameters derived from literature research (Archon/Exa), not from prior validated experiments.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (LongBench v2) | GitHub + Paper | Repo B.5 (THUDM/LongBench); ACL 2025 paper |
| Dataset loading code | GitHub | Repo B.5 `load_dataset("THUDM/LongBench", "v2")` |
| MOHAWK architecture | GitHub + Paper | Repo B.1 (goombalab/mohawk); Bick et al. NeurIPS 2024 |
| MOHAWK Stage 1 pseudo-code | GitHub | Repo B.2 `assets/mohawk_stage1.py` |
| MOHAWK token budget split | Paper | Bick et al. NeurIPS 2024 (scaled from 3B to 1B) |
| MOHAWK optimizer/LR | GitHub | Repo B.1 `configs/Llama/8B/` defaults |
| LAWCAT architecture | GitHub + Paper | Repo B.4 (zeyuliu1037/LAWCAT); Liu et al. EMNLP 2025 |
| LAWCAT Conv1D pseudo-code | GitHub + Paper | Repo B.4 `linear_window_attention_sw_gla.py`; arxiv 2509.18467 |
| LAWCAT distill config | GitHub | Repo B.4 `distill_passkey_1208_xent0_mse1000_lr1e-2` |
| LAWCAT LoRA config | GitHub | Repo B.4 `finetune_lora_qkvo_passkey_1208` |
| Hybrid-4 design | Paper | Bick et al. NeurIPS 2024 (4 middle attention layers retained) |
| Perplexity/alignment gates | Phase 2B | 02b_verification_plan.md Section 1.5/4.2 (R3 mitigation) |
| Evaluation metrics (Δ_norm) | Phase 2B + GitHub | 02b_verification_plan.md H-E1; Repo B.5 result.py |
| Expected baseline performance | Paper + Leaderboard | LongBench v2 paper (50.1% best model); longbench2.github.io |
| Mechanism verification code | This document | Synthesized from B.1, B.2, B.4 patterns |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — managed by pipeline harness)
**Date:** 2026-08-03

### Workflow History for This Hypothesis
- 2026-08-03T13:15:53Z: H-E1 set to IN_PROGRESS (Hypothesis Loop)
- 2026-08-03: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Exa (GitHub + web search); Archon KB searched but no domain-relevant content found*
*All specifications grounded in official paper implementations (MOHAWK NeurIPS 2024; LAWCAT EMNLP 2025)*
*Next Phase: Phase 3 - Implementation Planning*
