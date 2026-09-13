# Product Requirements Document: H-M1
# SSD Frobenius Error Scaling Gate Experiment

**stepsCompleted:** ["executive-summary", "problem-statement", "functional-requirements", "nfrs", "success-criteria"]
**Hypothesis:** H-M1
**Type:** MECHANISM (Day 0 Gate)
**Date:** 2026-08-03
**Author:** YouRA Research Pipeline (Phase 3)

---

## 1. Executive Summary

H-M1 is a Day 0 gate check experiment that measures whether the SSD (Structured State-Space Dual) matrix approximation Frobenius error scales sub-linearly with sequence length N from 512 to 8192 tokens. Using 500 C4 validation sequences and LLaMA-3-8B as the teacher model, we fit a Mamba-2 SSD block to each layer's attention matrix at each of 5 target lengths {512, 1k, 2k, 4k, 8k} and measure the Frobenius distance. The log-log slope β and 90th percentile error at N=8k serve as gate metrics. If β ≤ 0.5 AND 90th_pct ≤ 0.3, the MOHAWK distillation (14 GPU-days) proceeds; otherwise it is aborted and the hypothesis is reframed.

---

## 2. Problem Statement

**Background:** MOHAWK Stage 1 trains an SSD mixer to approximate transformer attention matrices via Frobenius loss (goombalab/phi-mamba). The paper reports SSD distance ≈ 0.097 at N=512 (Table 6). However, the paper only evaluates at short context (512 tokens). Before committing to a 14 GPU-day distillation, we must verify this approximation quality does not catastrophically degrade at long-context inference lengths (up to N=8k).

**Core Question:** Does the SSD Frobenius approximation error grow sub-linearly (slope ≤ 0.5 in log-log space) as N increases from 512 to 8k, and is the 90th percentile error at N=8k ≤ 0.3?

**Scope:** This is a measurement study, not a training run. The SSD parameters are optimized per-sample-per-length (10k steps, Adam) purely to measure approximation capacity — not to train a deployable model.

---

## 3. Functional Requirements

### FR-1: Data Pipeline — C4 Sequence Sampling
**Source:** 03_prd.md §3 FR-1 | **Priority:** P0
- Draw 500 random sequences from C4 validation split (`allenai/c4`, `en`, streaming)
- Tokenize with LLaMA-3-8B tokenizer; truncate/pad to each target length N ∈ {512, 1024, 2048, 4096, 8192}
- Fixed random seed = 42 for reproducibility
- Output: tensor of shape (500, N) for each N

### FR-2: Teacher Attention Matrix Extraction
**Source:** 03_prd.md §3 FR-2 | **Priority:** P0
- Load LLaMA-3-8B (`meta-llama/Llama-3-8B`) in bfloat16, inference mode, `output_attentions=True`
- Forward pass for each (sample, length) pair; extract per-head attention matrix (N, N) per layer
- Select 1 random head per layer per sample (following MOHAWK Table 6 protocol)
- Handle OOM: process one layer at a time; use bfloat16; fall back to 1 head if needed
- Output: attention matrix cache, shape (500, 32_layers, N, N), stored sequentially to avoid OOM

### FR-3: SSD Fitting Per Sample Per Length
**Source:** 03_prd.md §3 FR-3 | **Priority:** P0
- For each (sample, layer, length) tuple:
  - Initialize Mamba-2 SSD block with d_model=4096, d_state=64, n_heads=32 (matching LLaMA-3-8B)
  - Run 10,000 Adam optimization steps (lr=1e-3, betas=(0.9,0.999)) in fp32
  - Loss: `torch.linalg.matrix_norm(transfer_matrix - attn_matrix, ord="fro").mean()`
  - Record final Frobenius error per (sample, layer, N)
- Use `return_mixer_matrix=True` from phi-mamba phi_block to materialize N×N SSD matrix

### FR-4: Mechanism Activation Verification
**Source:** 03_prd.md §3 FR-4 | **Priority:** P0
- Verify SSD mechanism activated: shape correct, loss decreased ≥10%, finite loss
- Log per-step loss curve for first 5 samples (diagnostic)
- Fail fast if transfer_matrix shape mismatch or loss not decreasing

### FR-5: Log-Log Slope Computation
**Source:** 03_prd.md §3 FR-5 | **Priority:** P0
- Compute mean Frobenius error E(N) across 500 samples × 32 layers at each N
- Fit linear regression: log(E) = β·log(N) + const via `np.polyfit(log(Ns), log(Es), 1)`
- Compute 90th percentile error at N=8192: `np.percentile(errors_8k, 90)`
- Gate check: β ≤ 0.5 AND pct90 ≤ 0.3

### FR-6: Secondary Metric — Toeplitz Comparison
**Source:** 03_prd.md §3 FR-6 | **Priority:** P1
- Compute Toeplitz baseline approximation error at each N for secondary metric
- Verify E_SSD(N) < E_Toeplitz(N) for all N (replicates MOHAWK Table 6 ordering)

### FR-7: Visualization
**Source:** 03_prd.md §3 FR-7 | **Priority:** P1
- Fig 1 (mandatory): Bar chart of 90th pct error per N vs threshold 0.3; log-log error curve with fitted slope annotation
- Fig 2: Log-log Frobenius scaling plot with regression line and slope annotation; SSD vs Toeplitz lines
- Fig 3: Violin plots of Frobenius error distribution per N (500 samples × 32 layers), 90th pct threshold line
- Fig 4: Per-layer mean Frobenius error heatmap at N=8k (32 layers × 1 head)
- All figures saved to `h-m1/figures/`

### FR-8: Gate Result Reporting
**Source:** 03_prd.md §3 FR-8 | **Priority:** P0
- Print gate decision: PASS or STOP with β and pct90 values
- Save all raw errors to `h-m1/results/errors_by_N.pkl`
- Save summary metrics to `h-m1/results/gate_metrics.json`

---

## 4. Data Specification

| Item | Value |
|------|-------|
| Text source | C4 validation (`allenai/c4`, `en`, streaming=True) |
| Sample count | 500 sequences |
| Target lengths N | {512, 1024, 2048, 4096, 8192} |
| Splits | None — measurement study, no train/val/test |
| Preprocessing | Tokenize with LLaMA-3-8B tokenizer; truncate/pad to exact N |
| Teacher model | `meta-llama/Llama-3-8B` (HuggingFace) |
| Teacher precision | bfloat16 |
| SSD fitter precision | fp32 |
| Total attention matrices | 500 × 5 lengths × 32 layers = 80,000 |

**Loading code:**
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B", torch_dtype=torch.bfloat16)
dataset = load_dataset("allenai/c4", "en", split="validation", streaming=True)
```

**Note:** No manual dataset download required — both model and dataset auto-download via HuggingFace.

---

## 5. Evaluation Metrics

| Metric | Type | Gate Threshold |
|--------|------|----------------|
| Log-log slope β | Primary | ≤ 0.5 (PASS) |
| 90th pct Frobenius error at N=8k | Primary | ≤ 0.3 (PASS) |
| E_SSD(N) < E_Toeplitz(N) | Secondary | All N |
| Mechanism activated | Diagnostic | True (shape + loss decrease) |

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Compute budget | < 1 GPU-day on 1-2 A100s |
| Memory | One layer at a time; bfloat16 teacher; handle 8192×8192 matrix per head |
| Reproducibility | Fixed seed=42; deterministic data sampling |
| Precision | bfloat16 for teacher forward; fp32 for SSD fitting |
| Error handling | OOM at large N → reduce to 1 head/layer, chunked materialization |
| Output persistence | All raw errors saved to pickle; summary to JSON |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.1.0
transformers>=4.40.0
datasets>=2.18.0
mamba_ssm>=1.2.0          # provides Mamba2 and SSD transfer matrix
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.10.0
tqdm>=4.65.0
```

### 7.2 External Repositories

| Repository | Purpose | Priority |
|------------|---------|----------|
| `goombalab/phi-mamba` | Official MOHAWK Stage 1 Frobenius loss code; phi_block with `return_mixer_matrix=True` | PRIMARY |
| `goombalab/mohawk` | LLaMA-3-8B distillation config; `matrices` objective | REFERENCE |
| `state-spaces/mamba` | Mamba-2 SSD module; precision guidance | DEPENDENCY |

---

## 8. Success Criteria

**Gate PASS (both required):**
1. Log-log slope β ≤ 0.5
2. 90th percentile Frobenius error at N=8k ≤ 0.3

**Gate PASS outcome:** Proceed to H-E1 distillation (14 GPU-day commitment). Interpretation: SSD approximation quality does not catastrophically degrade at long context — retrieval degradation is architectural bounded-state bias, not approximation breakdown.

**Gate FAIL outcome:** STOP. Abort 14 GPU-day distillation. Reframe hypothesis as "approximation-quality failure under long-context budget."

**Secondary success:** E_SSD(N) < E_Toeplitz(N) for all N — confirms MOHAWK Table 6 ordering holds at extended lengths.

---

## 9. Out of Scope

- Full MOHAWK distillation training (H-E1 scope)
- Any evaluation on downstream tasks (retrieval, QA)
- KV-cache or recurrent inference mode
- Fine-tuning or modifying LLaMA-3-8B weights
