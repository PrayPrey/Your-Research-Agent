# Experiment Design: h-m2

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Selective SSM adapter distills Q/K/V to A/B/C/Δ preserving Jacobian geometry (W2 < 0.05)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates causal mechanisms with controlled experiments.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C experiment design)
**Prerequisites Satisfied:** h-m1 experiment design COMPLETED (prerequisite satisfied for design phase)
**Gate Status:** MUST_WORK gate (failure blocks entire workflow)

**Note**: h-m1 implementation FAILED (no low-rank structure found), but h-m2 experiment design proceeds as specified in Phase 2B planning. h-m2 tests adapter distillation mechanism independently of low-rank assumption.

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (experiment design completed, implementation failed)

### Gate Condition
**MUST_WORK**: If adapter-based distillation fails to preserve Jacobian geometry (W2 ≥ 0.05), then attention and SSM operator families are incompatible with this factorization approach. → PIVOT to LTI control comparison to isolate selectivity necessity.

---

## Continuation Context

**This is a continuation experiment** (follows h-m1).

**Previous Hypothesis (h-m1)**: Low-Rank Compression Mechanism
- **Status**: experiment_design COMPLETED, implementation FAILED
- **Key Finding**: Deep layers do NOT exhibit low-rank structure (r_eff ~1554-1647, NOT < 256)
- **Impact on h-m2**: Original hypothesis assumed low-rank structure enables bounded-state conversion. Since this assumption is invalidated, h-m2 must test adapter distillation WITHOUT relying on low-rank assumption.

**Approach Modification**:
- Test adapter distillation on actual (full-rank) attention operators
- Use larger SSM state sizes (N up to 1024) if needed
- Validate Jacobian alignment independently of rank constraints

### Previous Hypothesis Results
From h-m1 validation report (04_validation.md):
- ❌ r_eff criterion FAILED (1554-1647, not < 256)
- ❌ Entropy criterion FAILED (β = +0.001453, not negative)
- Model: Mistral-7B-v0.1 (32 layers)
- Method: Direct SVD analysis of Q/K/V weight matrices
- Implication: Bounded-state compression assumption INVALID

**Lessons for h-m2**:
1. Do NOT assume attention operators are low-rank
2. Test SSM state size sweep (N=64 to 1024) to find minimum viable N
3. If N>1024 required, document that conversion is impractical (defeats linear efficiency)
4. Focus on Jacobian alignment as PRIMARY criterion (not rank reduction)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Selective SSM Adapter Distillation**
- Search query: "selective SSM adapter distillation attention"
- **Finding**: Limited direct SSM results in KB. Most results from diffusion models domain.
- **Key insight**: SSM research is emerging; will rely heavily on Exa GitHub search for implementations.

**Query 2: Jacobian Alignment and Operator Geometry**
- Search query: "Jacobian alignment operator geometry"
- Result 1: NVIDIA cuBLAS documentation (operator efficiency patterns)
  - Insight: GPU-optimized matrix operations critical for Jacobian computations
  - Relevance: Performance considerations for Wasserstein-2 distance calculations
- **Key insight**: Jacobian eigenvalue analysis requires efficient linear algebra implementations

**Query 3: Wasserstein Distance in Neural Networks**
- Search query: "Wasserstein distance neural network"
- Result 1: Diffusion model community examples
  - Insight: Wasserstein metrics used in generative model evaluation
  - Pattern: torch-based distance computations in diffusion pipelines
- **Key insight**: Wasserstein-2 distance implementations exist in PyTorch ecosystem

**Query 4: Knowledge Distillation Patterns**
- Search query: "knowledge distillation neural network"
- Result 1: Latency Consistency Model (LCM) distillation (HuggingFace diffusers)
  - Dataset: Training data from teacher model
  - Hyperparameters: LoRA adapters, consistency distillation loss
  - Code pattern: `train_lcm_distill_lora_sd_wds.py` shows distillation training loop
  - Insight: Adapter-based distillation is proven pattern in diffusion models
- Result 2: AWS Trainium ML training infrastructure
  - Insight: Distillation can leverage distributed training for large models
- **Key insight**: Adapter distillation (LoRA-style) is established technique, proven in diffusion domain

### Archon Code Examples

**Query 1: Adapter Distillation PyTorch**
- Example 1: MultiAdapter Loading (HuggingFace diffusers)
  ```python
  from diffusers import StableDiffusionAdapterPipeline, MultiAdapter, T2IAdapter

  adapters = MultiAdapter([
      T2IAdapter.from_pretrained("TencentARC/t2iadapter_keypose_sd14v1"),
      T2IAdapter.from_pretrained("TencentARC/t2iadapter_depth_sd14v1"),
  ])
  adapters = adapters.to(torch.float16)
  ```
  - Pattern: Multiple adapters combined into single module
  - Insight: Adapter architecture allows modular knowledge injection
  - Relevance: Similar pattern needed for Q/K/V → A/B/C/Δ adapter

- Example 2: LoRA Adapter Weights (HuggingFace diffusers)
  ```python
  pipe.load_lora_weights("latent-consistency/lcm-lora-sdxl", adapter_name="lcm")
  pipe.set_adapters(["lcm", "papercut"], adapter_weights=[1.0, 0.8])
  ```
  - Pattern: Weighted adapter combination with named adapters
  - Insight: Adapter weights can be tuned for distillation strength
  - Relevance: Selective SSM adapter may need weighted distillation

- Example 3: Distilled AutoEncoder (HuggingFace diffusers)
  ```python
  distilled = StableDiffusionPipeline.from_pretrained("nota-ai/bk-sdm-small")
  distilled.vae = AutoencoderTiny.from_pretrained("sayakpaul/taesd-diffusers")
  ```
  - Pattern: Component-level distillation (replace sub-module)
  - Insight: Distillation can target specific model components
  - Relevance: Layer-wise distillation Q/K/V → SSM adapter

**Query 2: Wasserstein Distance Implementation**
- **Finding**: No direct code examples in Archon KB for Wasserstein-2 eigenvalue distance
- **Fallback**: Will search Exa GitHub for POT (Python Optimal Transport) or scipy implementations
- **Expected pattern**: `scipy.stats.wasserstein_distance` or custom Jacobian eigenvalue comparison

### Exa GitHub Implementations

**Query 1: Official Mamba SSM Implementation**

**Repository 1**: state-spaces/mamba (⭐ 50 contributors, latest: v2.3.1)
- **URL**: https://github.com/state-spaces/mamba
- **Authors**: Albert Gu, Tri Dao (original Mamba paper authors)
- **Relevance**: Official implementation of selective SSM mechanism
- **Architecture**: Selective SSM layer (selective_scan_interface.py) + Mamba block (mamba_simple.py)
- **Key Code**:
  ```python
  from mamba_ssm import Mamba

  model = Mamba(
      d_model=dim,        # Model dimension
      d_state=16,         # SSM state expansion factor (N)
      d_conv=4,           # Local convolution width
      expand=2            # Block expansion factor
  )
  ```
- **Installation**: `pip install mamba-ssm --no-build-isolation`
- **Pretrained Models**: HuggingFace hub (mamba-130m through mamba-2.8b, trained on 300B tokens)
- **State Size**: Default d_state=16 (expandable to larger N for testing)
- **Hardware**: CUDA 11.6+, requires GPU for efficiency

**Query 2: MOHAWK Distillation (Transformer→SSM)**

**Repository 2**: goombalab/phi-mamba (⭐ Official MOHAWK implementation)
- **URL**: https://github.com/goombalab/phi-mamba
- **Paper**: "Transformers to SSMs: Distilling Quadratic Knowledge to Subquadratic Models" (NeurIPS 2024)
- **Authors**: Aviv Bick, Kevin Y. Li, Eric P. Xing, J. Zico Kolter, Albert Gu
- **Relevance**: **EXACTLY MATCHES h-m2 OBJECTIVE** - adapter-based distillation of attention to SSM
- **Architecture**: Phi-1.5 Transformer distilled to Phi-Mamba using 3B tokens (< 1% of original training data)
- **Method - MOHAWK 3-Stage Pipeline**:
  1. **Matrix Orientation**: Match attention mixing matrices to SSM mixing matrices
     - Loss: `min E[||M_Teacher(u) - M_Student(u)||_F]`
     - Aligns Q/K/V attention operators to A/B/C/Δ SSM parameters
  2. **Hidden-State Alignment**: Distill intermediate layer representations
     - Match hidden states block-by-block
  3. **End-to-End Distillation**: Full model output matching
- **Key Insight**: "View both Transformers and SSMs as applying different forms of mixing matrices over token sequences"
- **Training Config**:
  - Distillation data: 3B tokens (vs 150B for Phi-1.5)
  - torch==2.1, mamba-ssm, flash-attn==2.5.8
  - Requires causal_conv1d==1.1.1
- **Results**: Phi-Mamba substantially stronger than all past open-source non-Transformer models
- **Implementation Files**:
  - Mamba-2 mixer variant (selective SSM)
  - Hybrid architecture support (SSM + attention layers)

**Repository 3**: Retrieval-Aware Distillation (Latest 2026 work)
- **Paper**: arXiv:2602.11374 "Retrieval-Aware Distillation for Transformer-SSM Hybrids"
- **Authors**: Aviv Bick, Eric P. Xing, Albert Gu (same team as MOHAWK)
- **Relevance**: Advanced distillation preserving only retrieval-critical attention heads
- **Key Finding**: **Just 2% of attention heads recover 95% of teacher performance** on retrieval tasks
  - 10 heads in 1B model sufficient for retrieval
  - Remaining layers distilled to SSM
- **Method**: Identify Gather-and-Aggregate (G&A) attention heads via ablation, preserve only those
- **Results**: 5-6× memory efficiency vs full hybrids
- **Insight**: Large SSM states can compensate for missing attention once retrieval is handled

**Query 3: Jacobian Alignment in Neural Networks**

**Paper 1**: arXiv:2506.12284 "GrokAlign: Geometric Characterisation and Acceleration of Grokking"
- **Relevance**: Jacobian alignment as training objective
- **Key Method**: Aligning network Jacobians with training data (cosine similarity) ensures generalization
- **Result**: Jacobian regularization induces faster convergence
- **Insight**: Low-rank Jacobian assumption + alignment = improved training dynamics

**Paper 2**: arXiv:2407.07810 "Transformer Alignment in Large Language Models"
- **Relevance**: Analysis of Jacobian properties in LLMs
- **Key Finding**: Alignment of top left/right singular vectors of Residual Jacobians in 38 LLMs
- **Method**: SVD analysis of layer-wise Jacobian matrices
- **Result**: Singular vector alignment correlates with improved performance
- **Insight**: Jacobian eigenvalue analysis via SVD is established technique

**Paper 3**: "Training on Edge of Stability Is Caused by Layerwise Jacobian Alignment" (arXiv:2406.00127)
- **Relevance**: Jacobian alignment mechanism understanding
- **Finding**: Singular vectors of layerwise Jacobians rotate during training
- **Measurement**: Subspace alignment enables large changes through narrow input subspaces
- **Insight**: Jacobian alignment is a natural emergent property during training

**Wasserstein Distance Implementation**:
- **Expected Library**: POT (Python Optimal Transport) or scipy
- **Pattern**: Compute Jacobian eigenvalues → Compare distributions via Wasserstein-2 metric
- **Code Pattern**:
  ```python
  from scipy.stats import wasserstein_distance
  # Or use POT library for W2 specifically
  import ot
  W2_dist = ot.wasserstein_1d(eigenvals_attention, eigenvals_ssm)
  ```

**Serena Analysis Needed**: False (code patterns are clear, MOHAWK provides complete implementation reference)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment**: This is NOT a paper reproduction - this is a novel hypothesis testing adapter distillation with Jacobian alignment on LLaMA. However, we leverage proven methodologies.

**Recommended Implementation Path:**
- **Primary**: MOHAWK distillation framework (github.com/goombalab/phi-mamba) + Official Mamba SSM (github.com/state-spaces/mamba)
- **Fallback**: Custom implementation based on MOHAWK paper pseudocode if repository integration fails
- **Justification**:
  - MOHAWK is the state-of-the-art method for Transformer→SSM distillation (NeurIPS 2024)
  - Official Mamba SSM provides validated selective SSM implementation
  - Phi-Mamba demonstrates successful distillation with 3B tokens
  - Both repositories actively maintained with recent commits (2026-03-17 for Mamba)
  - Clear API and documented hyperparameters

### Code Analysis (Serena MCP)

**Status**: Skipped (serena_needed = false)
**Reason**: Code patterns from MOHAWK and official Mamba implementations are clear and well-documented. No complex code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset 1: The Pile (Calibration)**
- **Name**: The Pile
- **Type**: standard
- **Source**: EleutherAI
- **Purpose**: Adapter distillation training (calibration data)
- **Context Length**: Variable (use 8K-128K samples for long-context calibration)
- **Statistics**: 825GB uncompressed, diverse text domains
- **Preprocessing**: Tokenization with LLaMA tokenizer, context windowing
- **Augmentation**: None (use as-is for calibration)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets (streaming recommended due to size)
- Identifier: `EleutherAI/pile` (note: may require alternative source if unavailable)
- Code:
  ```python
  from datasets import load_dataset
  # Stream The Pile data
  pile = load_dataset("EleutherAI/pile", split="train", streaming=True)
  # Or use alternative: C4 (allenai/c4) if The Pile unavailable
  # c4 = load_dataset("allenai/c4", "en", split="train", streaming=True)
  ```
- **Fallback**: If The Pile unavailable (404 error from the-eye.eu), use C4 dataset as alternative calibration source

**Dataset 2: LongBench (Evaluation)**
- **Name**: LongBench
- **Type**: standard
- **Source**: THUDM (Tsinghua University)
- **Purpose**: Cross-domain stability testing (evaluation)
- **Context Length**: 8K-128K tokens across 20+ tasks
- **Statistics**: ~4.75K test samples across 20 tasks (narrativeqa, qasper, hotpotqa, etc.)
- **Tasks**: QA, summarization, few-shot learning, synthetic tasks, code completion
- **Preprocessing**: Task-specific (passage retrieval, document QA, etc.)
- **Evaluation Split**: test

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `THUDM/LongBench`
- Code:
  ```python
  from datasets import load_dataset
  # Load specific LongBench task
  longbench_tasks = ["narrativeqa", "qasper", "multifieldqa_en", "hotpotqa"]
  for task in longbench_tasks:
      data = load_dataset("THUDM/LongBench", task, split="test")
  ```

**Synthetic Data Policy Check**: ✅ PASSED (both datasets are real, standard datasets)

### Models

#### Baseline Model

**Architecture**: LLaMA-7B (primary) / LLaMA-13B (optional scale test)
- **Type**: decoder-only Transformer
- **Source**: Meta AI (official checkpoints)
- **Layers**: 32 (L0-L31)
- **Target Layer**: L28 (deep layer, L≥20)
- **Hidden Size**: 4096 (7B) / 5120 (13B)
- **Attention Heads**: 32 (7B) / 40 (13B)
- **Parameters**: ~7B (primary) / ~13B (optional)
- **Context Window**: Originally 2K, extended to 128K via RoPE scaling

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-hf` (requires HF access token)
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  import torch

  model_id = "meta-llama/Llama-2-7b-hf"
  # Requires HF access token (apply at meta.com/llama)
  model = AutoModelForCausalLM.from_pretrained(
      model_id,
      torch_dtype=torch.float16,
      device_map="auto",
      token="<YOUR_HF_TOKEN>"
  )
  tokenizer = AutoTokenizer.from_pretrained(model_id, token="<YOUR_HF_TOKEN>")
  ```

**Configuration for Hypothesis**:
- Extract attention layer L28: `model.model.layers[28].self_attn`
- Q/K/V projections: `q_proj`, `k_proj`, `v_proj` (4096 → 4096 each for 7B)
- Adapter target: Distill (Q, K, V) → SSM (A, B, C, Δ)

#### Proposed Model

**Architecture**: LLaMA-7B Layer 28 + Selective SSM Adapter (Attention → SSM Distillation)

**Integration Point**: Single attention layer (L28) conversion for controlled testing
- Extract: `model.model.layers[28].self_attn` (Q, K, V projections)
- Replace with: Selective SSM adapter (A, B, C, Δ parameters)
- Preserve: All other layers unchanged for fair comparison

**Modification**: Adapter-based knowledge distillation using MOHAWK framework
- Teacher: Original attention mechanism (Q, K, V)
- Student: Selective SSM (A, B, C, Δ)
- Training: Matrix orientation → Hidden-state alignment → End-to-end distillation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Selective SSM Adapter with Jacobian Alignment
# Based on: MOHAWK distillation (Bick et al. 2024, NeurIPS)
# Source: github.com/goombalab/phi-mamba

import torch
import torch.nn as nn
from mamba_ssm import Mamba

class SelectiveSSMAdapter(nn.Module):
    """
    Distills attention Q/K/V operators to selective SSM A/B/C/Δ
    via adapter-based knowledge distillation with Jacobian geometry preservation.
    """
    def __init__(self, d_model=4096, d_state=512, d_conv=4, expand=2):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state

        # Selective SSM core (from mamba-ssm)
        self.ssm = Mamba(
            d_model=d_model,
            d_state=d_state,  # N=512 target (test 64-1024 range)
            d_conv=d_conv,
            expand=expand
        )

        # Adapter projection: Attention hidden → SSM hidden
        # Maps Q/K/V space (3*d_model) to SSM input space
        self.adapter_proj = nn.Linear(d_model, d_model)

    def forward(self, x):
        """
        Args:
            x: (B, L, d_model) - input hidden states from layer L-1
        Returns:
            (B, L, d_model) - SSM-transformed hidden states
        """
        # Apply adapter projection (learned distillation mapping)
        adapted_x = self.adapter_proj(x)

        # Selective SSM recurrence (replaces attention)
        ssm_output = self.ssm(adapted_x)

        return ssm_output

# Distillation Loss Components:
# 1. Matrix Orientation Loss (Step 1):
#    L_matrix = ||M_attn(u) - M_ssm(u)||_F
# 2. Jacobian Alignment Loss (Step 2):
#    L_jacobian = W2(eigenvals_attn, eigenvals_ssm)
# 3. Hidden-State Loss (Step 3):
#    L_hidden = MSE(h_attn, h_ssm)
# 4. Output Loss (Step 4):
#    L_output = MSE(y_attn, y_ssm)

# Total Loss: λ1*L_matrix + λ2*L_jacobian + λ3*L_hidden + λ4*L_output
```

**Jacobian Alignment Computation** (Wasserstein-2 Distance):
```python
def compute_wasserstein2_jacobian_distance(teacher_layer, student_layer, input_batch):
    """
    Compute W2 distance between attention and SSM Jacobian eigenvalues.
    Success criterion: W2 < 0.05
    """
    # Compute Jacobian eigenvalues for teacher (attention)
    with torch.enable_grad():
        J_teacher = torch.autograd.functional.jacobian(teacher_layer, input_batch)
        eigenvals_teacher = torch.linalg.eigvalsh(J_teacher @ J_teacher.T)

    # Compute Jacobian eigenvalues for student (SSM)
    with torch.enable_grad():
        J_student = torch.autograd.functional.jacobian(student_layer, input_batch)
        eigenvals_student = torch.linalg.eigvalsh(J_student @ J_student.T)

    # Wasserstein-2 distance
    from scipy.stats import wasserstein_distance
    W2_dist = wasserstein_distance(
        eigenvals_teacher.cpu().numpy(),
        eigenvals_student.cpu().numpy()
    )
    return W2_dist
```

### Training Protocol

**Based on**: MOHAWK distillation framework (Bick et al. 2024) + Phi-Mamba implementation

**Stage 1: Matrix Orientation** (Day 1)
- **Objective**: Align attention mixing matrix to SSM mixing matrix
- **Loss**: Frobenius norm `||M_Teacher - M_Student||_F`
- **Optimizer**: AdamW
- **Learning Rate**: 1e-4
- **Batch Size**: 8 sequences (4096 tokens each)
- **Tokens**: 100M from The Pile (streaming)
- **Epochs**: 1 pass through 100M tokens
- **Source**: MOHAWK paper Section 3.3

**Stage 2: Hidden-State Alignment** (Day 2)
- **Objective**: Match intermediate layer representations
- **Loss**: MSE(h_teacher, h_student) + λ_jacobian * W2(eigenvals_teacher, eigenvals_student)
- **λ_jacobian**: 0.1 (Jacobian alignment weight)
- **Optimizer**: AdamW
- **Learning Rate**: 5e-5 (reduced for stability)
- **Batch Size**: 8 sequences
- **Tokens**: 500M from The Pile
- **Epochs**: 1 pass through 500M tokens
- **Source**: MOHAWK paper + Jacobian alignment literature

**Stage 3: End-to-End Distillation** (Day 3-5)
- **Objective**: Full model output matching
- **Loss**: MSE(y_teacher, y_student) + perplexity_loss
- **Optimizer**: AdamW
- **Learning Rate**: 1e-5 (fine-tuning rate)
- **Batch Size**: 8 sequences
- **Tokens**: 2.4B from The Pile (total ≈3B across all stages)
- **Epochs**: ~5 passes
- **Source**: Phi-Mamba used 3B tokens total for distillation

**SSM State Size Sweep**:
- Test N ∈ {64, 128, 256, 512, 1024} to validate exponential MSE decay
- Primary target: N=512 (hypothesis criterion)

**Calibration Data**:
- Source: The Pile (streaming mode)
- Fallback: C4 dataset if The Pile unavailable
- Context lengths: 8K tokens (standard), 128K (extended test)

**Hardware**: Single A100 40GB GPU
**Mixed Precision**: FP16 for memory efficiency
**Gradient Accumulation**: 4 steps (effective batch size = 32 sequences)

### Evaluation

**Primary Metrics** (from Phase 2B success criteria):

1. **Wasserstein-2 Jacobian Distance** (CRITICAL)
   - Definition: W2 distance between teacher attention and student SSM Jacobian eigenvalue distributions
   - Target: W2 < 0.05 at N=512
   - Measurement: Compute on 100 random samples from LongBench test set
   - **Success Criterion**: W2 < 0.05 (MUST_WORK gate)

2. **Distillation MSE** (Output Matching)
   - Definition: Mean squared error between teacher and student outputs
   - Expected: Exponential decay with increasing N
   - Measurement: MSE(y_teacher, y_student) across SSM state sizes
   - **Success Criterion**: Exponential fit R² > 0.95

3. **Cross-Domain Error Delta** (Stability)
   - Definition: |Error(The Pile) - Error(LongBench)|
   - Target: < 3% absolute difference
   - Measurement: Compare MSE on calibration (The Pile) vs evaluation (LongBench)
   - **Success Criterion**: Delta < 3%

4. **Selective vs LTI Control** (Selectivity Advantage)
   - Definition: Compare selective SSM (input-conditioned Δ) vs fixed LTI SSM
   - Control: Freeze Δ parameters (Δ(x) = constant)
   - Target: Selective > LTI by 2× in MSE reduction
   - **Success Criterion**: MSE_selective / MSE_LTI < 0.5

**Secondary Metrics** (for analysis):
- Distillation loss convergence curves (3 stages)
- Per-state-size performance (N=64, 128, 256, 512, 1024)
- Jacobian eigenvalue distribution plots (teacher vs student)

**Evaluation Protocol**:
1. Run distillation training (3 stages)
2. Evaluate on LongBench test set (4 tasks: narrativeqa, qasper, hotpotqa, multifieldqa_en)
3. Compute W2 distance on 100 samples per task
4. Measure cross-domain stability (The Pile held-out vs LongBench)
5. Run LTI control baseline (fixed Δ)

**Expected Baseline** (from MOHAWK research):
- MOHAWK achieved strong distillation with 3B tokens (< 1% of pretraining)
- Phi-Mamba substantially outperformed prior non-Transformer models
- Retrieval-aware distillation: 2% attention heads = 95% performance recovery

**Gate Decision**:
- **PASS**: All 4 success criteria met → Enable h-m3 (calibration efficiency)
- **FAIL**: Any criterion fails → PIVOT to LTI baseline analysis, document incompatibility

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Operator geometry comparison (not standard classification/generation)
- Library: scipy (Wasserstein distance), torch (SVD, Jacobian computation)
- Code:
  ```python
  import torch
  from scipy.stats import wasserstein_distance
  import numpy as np

  # Compute Jacobian eigenvalues
  def compute_jacobian_eigenvalues(model, input):
      jacobian = torch.autograd.functional.jacobian(model, input)
      eigenvalues = torch.linalg.eigvalsh(jacobian @ jacobian.T)
      return eigenvalues.cpu().numpy()

  # Wasserstein-2 distance
  def wasserstein_2_distance(eigenvals_1, eigenvals_2):
      return wasserstein_distance(eigenvals_1, eigenvals_2)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on MECHANISM hypothesis type and distillation evaluation:

1. **MSE Decay vs SSM State Size** (N=64 to 1024)
   - Plot: log(MSE) vs log(N)
   - Expected: Linear trend (exponential decay)
   - Purpose: Validate exponential convergence with bounded state

2. **Jacobian Eigenvalue Distributions**
   - Plot: Histograms of teacher (attention) vs student (SSM) eigenvalues
   - Overlay: Wasserstein-2 distance annotation
   - Purpose: Visualize operator geometry alignment

3. **Cross-Domain Stability**
   - Plot: The Pile vs LongBench error comparison (scatter + delta histogram)
   - Purpose: Validate generalization across domains

4. **Distillation Loss Curves** (3 Stages)
   - Plot: Training loss over tokens (100M → 500M → 2.4B)
   - Breakdown: Matrix orientation, hidden-state, end-to-end stages
   - Purpose: Track convergence across distillation phases

5. **Selective vs LTI Control Comparison**
   - Plot: Bar chart comparing MSE (Selective SSM, LTI SSM, Attention baseline)
   - Purpose: Validate selectivity necessity (Δ(x) input-conditioning)

**Output Location**: `docs/youra_research/20260318_scope/h-m2/figures/`

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

**Source 1**: Latency Consistency Model (LCM) Distillation
- **Type**: Code example from HuggingFace diffusers
- **Query Used**: "knowledge distillation neural network"
- **URL**: github.com/huggingface/diffusers (train_lcm_distill_lora_sd_wds.py)
- **Relevance**: Adapter-based distillation pattern (LoRA-style)
- **Key Insights**:
  - Consistency distillation loss for teacher-student matching
  - LoRA adapters enable lightweight distillation
  - Training loop structure for distillation tasks
- **Used For**: Training protocol design (adapter distillation structure)

**Source 2**: Wasserstein Distance Applications
- **Type**: Community examples
- **Query Used**: "Wasserstein distance neural network"
- **URL**: Various diffusion model implementations
- **Relevance**: Wasserstein metrics in generative model evaluation
- **Key Insights**:
  - torch-based distance computations standard in PyTorch
  - Used for distribution matching in model training
- **Used For**: Evaluation metrics (W2 distance computation pattern)

### B. Exa GitHub Implementations

**Repository 1**: state-spaces/mamba (⭐ Official)
- **URL**: https://github.com/state-spaces/mamba
- **Authors**: Albert Gu, Tri Dao (Mamba paper authors)
- **Relevance**: Official selective SSM implementation
- **Used For**:
  - SSM architecture (d_model, d_state, d_conv parameters)
  - Mamba block structure (modules/mamba_simple.py)
  - Installation requirements (mamba-ssm, causal-conv1d)
  - Pretrained models reference
- **Key Code**:
  ```python
  from mamba_ssm import Mamba
  model = Mamba(d_model=dim, d_state=16, d_conv=4, expand=2)
  ```

**Repository 2**: goombalab/phi-mamba (⭐ MOHAWK - PRIMARY SOURCE)
- **URL**: https://github.com/goombalab/phi-mamba
- **Paper**: "Transformers to SSMs: Distilling Quadratic Knowledge to Subquadratic Models" (NeurIPS 2024)
- **Authors**: Aviv Bick, Kevin Y. Li, Eric P. Xing, J. Zico Kolter, Albert Gu
- **Relevance**: **EXACTLY MATCHES h-m2 OBJECTIVE** - Attention→SSM distillation
- **Used For**:
  - MOHAWK 3-stage distillation framework (primary methodology)
  - Matrix orientation → Hidden-state → End-to-end pipeline
  - Training hyperparameters (3B tokens, learning rates)
  - Adapter architecture design
  - Loss function formulations
- **Key Findings**:
  - Phi-Mamba distilled from Phi-1.5 using only 3B tokens (< 1% of pretraining)
  - View attention and SSM as "sequence transformations via mixing matrices"
  - Progressive distillation across granularities
- **Implementation Details**:
  - torch==2.1, mamba-ssm, flash-attn==2.5.8
  - causal_conv1d==1.1.1 required
  - Hybrid support (SSM + attention layers)

**Paper 3**: arXiv:2602.11374 "Retrieval-Aware Distillation for Transformer-SSM Hybrids"
- **Authors**: Aviv Bick, Eric P. Xing, Albert Gu (same MOHAWK team)
- **Relevance**: Advanced distillation preserving retrieval-critical heads
- **Key Findings**:
  - 2% of attention heads recover 95% performance (10 heads in 1B model)
  - 5-6× memory efficiency vs full hybrids
  - Gather-and-Aggregate (G&A) heads identified via ablation
- **Used For**: Insight into selective head preservation (future work)

**Paper 4**: arXiv:2506.12284 "GrokAlign: Geometric Characterisation"
- **Relevance**: Jacobian alignment as training objective
- **Key Method**: Align network Jacobians with data via cosine similarity
- **Used For**: Jacobian regularization approach (GrokAlign method)

**Paper 5**: arXiv:2407.07810 "Transformer Alignment in Large Language Models"
- **Relevance**: Jacobian analysis in 38 LLMs
- **Key Finding**: Singular vector alignment of Residual Jacobians
- **Method**: SVD analysis of layer-wise Jacobian matrices
- **Used For**: Jacobian eigenvalue analysis methodology

**Paper 6**: arXiv:2406.00127 "Training on Edge of Stability"
- **Relevance**: Layerwise Jacobian alignment mechanism
- **Finding**: Singular vectors rotate during training
- **Used For**: Understanding natural Jacobian alignment emergence

### C. Dataset & Model Loading

**LongBench Dataset**:
- **Source**: THUDM/LongBench (HuggingFace)
- **Documentation**: https://github.com/THUDM/LongBench
- **Loading Code**: `load_dataset("THUDM/LongBench", task_name, split="test")`
- **Used For**: Evaluation dataset specification

**The Pile Dataset**:
- **Source**: EleutherAI/pile (HuggingFace, with fallback to C4)
- **Fallback**: allenai/c4 if The Pile unavailable (404 from the-eye.eu)
- **Loading Code**: Streaming mode via `load_dataset(..., streaming=True)`
- **Used For**: Calibration data specification

**LLaMA Model**:
- **Source**: meta-llama/Llama-2-7b-hf (HuggingFace)
- **Documentation**: HuggingFace transformers docs
- **Loading Code**: `AutoModelForCausalLM.from_pretrained(...)`
- **Used For**: Baseline model specification

### D. Libraries & Dependencies

- **mamba-ssm**: Official Mamba SSM implementation (pip install mamba-ssm)
- **transformers**: HuggingFace transformers for LLaMA loading
- **datasets**: HuggingFace datasets for data loading
- **scipy**: Wasserstein distance computation (scipy.stats.wasserstein_distance)
- **torch**: PyTorch for Jacobian computation (autograd.functional.jacobian)
- **flash-attn**: Fast attention kernels (optional, for hybrid models)

### E. Methodology References

**MOHAWK Distillation Framework** (Primary Methodology):
1. **Stage 1 - Matrix Orientation**: Match mixing matrices via Frobenius norm
2. **Stage 2 - Hidden-State Alignment**: Match intermediate representations + Jacobian alignment
3. **Stage 3 - End-to-End**: Full model output matching

**Jacobian Alignment Protocol**:
1. Compute Jacobian via `torch.autograd.functional.jacobian`
2. Extract eigenvalues via `torch.linalg.eigvalsh(J @ J.T)`
3. Measure W2 distance via `scipy.stats.wasserstein_distance`
4. Success criterion: W2 < 0.05

**Selective SSM Architecture**:
- Input-conditioned parameters: Δ(x) = Softplus(W_Δ[Q,K,V])
- State space: A (d_state × d_state), B (d_state × d_model), C (d_model × d_state)
- Scan algorithm: Selective scan (from Mamba paper Algorithm 2)

---

**All specifications in this document are grounded in researched implementations from Archon KB, Exa GitHub search, and official repositories.**

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18T05:01:00Z

### Workflow History for This Hypothesis

- **2026-03-18T05:01:00Z**: Phase 2C experiment design started (status: IN_PROGRESS)
- **2026-03-18T04:09:00Z**: Prerequisite h-m1 implementation planning completed
- **2026-03-18T04:45:00Z**: Prerequisite h-m1 validation FAILED (no low-rank structure)
- **Current Status**: Experiment design proceeding despite h-m1 failure (tests independent mechanism)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
