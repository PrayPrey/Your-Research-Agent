# 3. Methodology

## 3.1 Design Philosophy: Mechanism Gate Before Behavioral Test

Building on our observation that SSD approximation quality is independently measurable, we
structure the evaluation in two sequential parts. The mechanism gate (H-M1) asks: *does SSD
approximate LLaMA-3-8B attention sub-linearly with sequence length?* The behavioral test (H-E1)
asks: *does conversion strategy produce a task-type interaction on LongBench v2?*

This sequencing is deliberate. If the mechanism gate fails (approximation degrades super-linearly),
retrieval degradation in the behavioral test would be attributable to distillation failure and
would not support claims about bounded-state architectural limits. If the mechanism gate passes,
behavioral degradation must be attributed to the SSM state update architecture — a finding with
different implications for practitioners.

**Rationale:** The mechanism gate and behavioral test are causally ordered. Interpreting behavioral
results without the mechanism gate is ambiguous; interpreting the mechanism gate without the
behavioral test is incomplete. Our design makes both explicit.

## 3.2 Mechanism Gate: SSD Frobenius Scaling (H-M1)

### 3.2.1 Setup

We load LLaMA-3-8B (`meta-llama/Llama-3.1-8B`, bfloat16) as the teacher and extract per-layer
attention matrices at target sequence lengths N ∈ {512, 1024, 2048} on 50 random inputs from
`monology/pile-uncopyrighted` (seed=42). For each of the 32 transformer layers, we materialize
the N×N attention weight matrix and the corresponding N×N SSD transfer matrix using MOHAWK's
official `materialize_mixer` implementation (`goombalab/mohawk`,
`components/cores/discrete_mamba2_ref.py`).

### 3.2.2 SSD Fitting

For each (layer, N, sample) triple, we fit an SSD block (d_state=64) by minimizing the Frobenius
distance between the SSD transfer matrix and the attention matrix:

```
L(θ) = ‖materialize_mixer(θ, N) − M_attn‖_F
```

using Adam (lr=1e-3, β=(0.9, 0.999)) for 500 steps in float32 precision. We minimize in float32
to avoid numerical instability in the SSM state accumulation. The 500-step budget is sufficient
for gate-level slope regression; the MOHAWK paper's 10,000-step budget is unnecessary for our
purpose.

**Normalization:** Raw Frobenius norm scales linearly with matrix dimension N (maximum value ∝ N
for an N×N matrix). To enable fair comparison across sequence lengths and to match MOHAWK's
reported values (≈0.097 at N=512), we use *normalized error* = raw_error / N throughout.

### 3.2.3 Gate Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Log-log slope β of normalized error vs N | ≤ 0.5 | Sub-linear scaling confirms approximation does not degrade faster than matrix size grows |
| 90th percentile normalized error at max N | ≤ 0.3 | Tail control: even worst-case layers maintain adequate approximation |

Both criteria must pass for the gate to be satisfied. Gate failure would indicate approximation
breakdown and would reframe all downstream results as "distillation failure" rather than
"architectural limit."

## 3.3 Controlled Conversion Comparison: MOHAWK-SSM vs LAWCAT (H-E1)

### 3.3.1 Fixed-Base-Model Design

**Critical design decision:** All converted models use LLaMA-3-8B as the single fixed teacher
and starting point. This eliminates the capability confound that dominates cross-family SSM
comparisons (e.g., comparing Phi-1.5 for MOHAWK vs Mistral-7B for LAWCAT would conflate
capability differences with conversion effects).

We evaluate four model variants:
- **Teacher:** LLaMA-3-8B (unconverted), evaluated directly on LongBench v2
- **MOHAWK-SSM:** MOHAWK 3-stage distillation (Stages 1+2: matrix + hidden-state alignment; Stage 3: logit distillation), ≤1B tokens, SSD mixer
- **LAWCAT:** LAWCAT 2-phase distillation (Phase 1: MSE matching on alpaca_clean; Phase 2: LoRA fine-tuning), ≤1B tokens, Conv1D + normalized gated linear attention
- **Hybrid-4:** MOHAWK Stage 3 only, retaining 4 middle attention layers (MOHAWK LayeredMambaLM hybrid)

### 3.3.2 Distillation Protocol

**MOHAWK training:**
- Stage 1: 26M tokens, lr=1e-3, batch=64, seq=2048
- Stage 2: 52M tokens, lr=1e-4, batch=64, seq=2048
- Stage 3: 922M tokens, lr=1e-4, batch=64, seq=2048
- Training data: `monology/pile-uncopyrighted` (confirmed working; C4 is rate-limited)
- Hardware: 4× H100 NVL 96GB, `torchrun --master_port 29502` (port 29501 may conflict with stale processes)

**LAWCAT training:**
- Phase 1: alpaca_clean dataset, MSE weight=1000, lr=1e-2 (native LAWCAT dataloader)
- Phase 2: LoRA (r=16, targets q/k/v/o projections)

**Key engineering decisions:**
- Model ID: `meta-llama/Llama-3.1-8B` (not `Llama-3-8B`, which does not exist on HuggingFace)
- MOHAWK checkpoint loading: `lazy_init` mode=inference (AutoModelForCausalLM fails on custom SSM architecture)
- norm_epsilon: handled via `getattr(..., 'norm_epsilon', 1e-5)` for LlamaBlock compatibility
- allow_unexpected_keys: true (for tied-embedding checkpoint loading)

### 3.3.3 Evaluation Protocol

We evaluate all four models on LongBench v2 (THUDM/LongBench, 503 questions) using multiple-choice
logit scoring. The primary metric is **normalized accuracy degradation**:

```
Δ_norm = (Acc_teacher − Acc_student) / Acc_teacher
```

computed per task category. Δ_norm ∈ [0, 1] where 0 = no degradation and 1 = complete failure.

### 3.3.4 Statistical Analysis

To test the task-type × strategy interaction (H-E1 primary gate), we fit a mixed-effects model:

```
Δ_norm ~ TaskType * Strategy + (1|Task)
```

with Holm correction for multiple comparisons. The gate requires:
- Ratio Δ_norm^MOHAWK(retrieval) / Δ_norm^LAWCAT(retrieval) ≥ 2.0
- 95% bootstrap confidence interval strictly above 1.0
- Interaction term p < 0.01 after Holm correction

## 3.4 Depth-Slope Analysis: Conv1D Mechanism Test (H-M2)

For the retrieval subset (multi-document QA and synthetic categories, 158 examples), we compute
needle depth percentile as:

```
depth_percentile = keyword_start_offset / total_context_length
```

(0.6% fallback rate when keyword not found; 111 unique depth values). We fit per-model logistic
regression:

```
P(correct) ~ DepthPercentile + (1|Task)
```

and compare β_depth coefficients between MOHAWK-SSM and LAWCAT. The gate requires
|β_depth^MOHAWK| ≥ 2× |β_depth^LAWCAT| with non-overlapping 95% CIs.

**Note:** H-M2 requires actual MOHAWK-SSM and LAWCAT checkpoints from H-E1. The statistical
pipeline is validated end-to-end (22/22 tests) but was executed under proxy conditions (identical
base LLaMA-3.1-8B for both conditions) due to a port conflict during H-E1 distillation. The
actual depth-slope comparison will be computed upon H-E1 completion.
