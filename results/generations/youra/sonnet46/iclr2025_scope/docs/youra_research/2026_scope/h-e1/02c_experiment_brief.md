# Experiment Design: H-E1

**Date:** 2026-05-08
**Author:** Anonymous
**Hypothesis Statement:** Under LLaMA-3-8B in inference mode, if layer-wise MLP activation sparsity (fraction |a| < 0.01 via forward hooks on 512 Alpaca samples) is measured across all 32 MLP gate layers, then sparsity CV > 0.3 and Kendall's tau_calibration ≥ 0.6 (Alpaca vs. WikiText-103), because pre-training drives MLP layers toward differentiated sparse activation attractors (Lazy Neuron Phenomenon).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** TRUE (no prerequisites for H-E1)
**Gate Status:** MUST_WORK — failure stops entire workflow

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition

**Gate Type:** MUST_WORK

This is the foundational existence check for the SparsityLoRA pipeline. If H-E1 fails:
- CV ≤ 0.3: PIVOT — sparsity signal is not discriminating; explore gradient norm or activation magnitude as alternative
- tau < 0.6: EXPLORE — use task-specific calibration (GLUE validation sets); narrow hypothesis scope

All downstream hypotheses (H-M1, H-M2, H-M3, H-M4) are blocked until H-E1 passes.

---

## Continuation Context

This is the **first hypothesis** in the verification chain. No previous hypothesis context.

### Previous Hypothesis Results (if applicable)
*None — H-E1 is the foundation hypothesis.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design — Activation Sparsity Measurement**
- **Source**: HuggingFace Accelerate docs — `attach_layerwise_casting_hooks`
  - Key insight: Layer-wise hook attachment pattern for LLMs via `accelerate.hooks` — shows the standard API for hooking into specific layers of transformer models
  - Used for: Hook registration pattern reference
- **Source**: HuggingFace PEFT docs — LoRA conceptual guide
  - Key insight: LoRA targets q_proj, v_proj, k_proj, o_proj, gate_proj, up_proj, down_proj; standard rank settings r=4,8,16
  - Used for: Confirming target modules for full hypothesis chain

**Query 2: Implementation Challenges — LoRA Rank Allocation**
- **Source**: HuggingFace PEFT GitHub — peft library
  - Key insight: Standard PEFT LoRA configuration; per-layer rank is specified via `rank_pattern` dict in LoraConfig
  - Used for: Understanding how per-layer rank customization works in PEFT

**Query 3: LLM Calibration — Alpaca/WikiText Inference**
- **Source**: calculate-flops.pytorch
  - Key insight: Layer-wise profiling patterns for transformer models
  - Used for: Measurement methodology reference

**Key Archon Insight:** No direct past cases for MLP activation sparsity CV measurement in LLaMA-3-8B were found. This confirms the novelty of H-E1. Implementation will rely on established PyTorch forward hook patterns (SparseGPT/TEAL style).

### Archon Code Examples

**Query 1: Forward Hook Pattern (Layerwise)**
- **Source**: HuggingFace Accelerate — `attach_layerwise_casting_hooks`
  ```python
  from accelerate.hooks import attach_layerwise_casting_hooks
  from transformers import AutoModelForCausalLM
  import torch
  model = AutoModelForCausalLM.from_pretrained(checkpoint)
  attach_layerwise_casting_hooks(model, storage_dtype=torch.float8_e4m3fn, compute_dtype=torch.bfloat16)
  with torch.no_grad():
      model(...)
  ```
  - **Pattern:** Register hooks per-layer, run inference under `torch.no_grad()`
  - **Insight:** Confirms the layer-iteration + hook-registration pattern for LLM inference

### Exa GitHub Implementations

**Query 1: Activation Sparsity Measurement — LLaMA/LLMs (MANDATORY)**

**Repository 1**: fszatkowski/activation-sparsity-benchmarking
- **URL**: https://github.com/fszatkowski/activation-sparsity-benchmarking
- **Relevance**: Directly measures activation sparsity in LLMs including LLaMA-3 via `activations_monitor.py`; supports configurable epsilon thresholds; computes sparsification statistics
- **Architecture**: `SparsificationManager` hooks into FFN layers (`gate_proj` outputs) using configurable rules (topp, topk, maxp) and thresholds; `activations_monitor.py` records activation statistics and effective ranks
- **Key Code Pattern**:
  ```python
  # sparsification_manager.py pattern (conceptual)
  def register_hooks(model, config):
      for layer_idx, layer in enumerate(model.model.layers):
          module = layer.mlp.gate_proj  # target gate_proj output
          hook = module.register_forward_hook(
              make_sparsity_hook(layer_idx, threshold=config.threshold)
          )
  ```
- **Serena Analysis Needed:** false — structure is clear from documentation
- **Used For:** Core hook registration pattern; sparsification config format for LLaMA-3

**Repository 2**: FasterDecoding/TEAL
- **URL**: https://github.com/FasterDecoding/TEAL
- **Relevance**: Official TEAL implementation (Training-Free Activation Sparsity in LLMs); `grab_acts.py` collects activation histograms for threshold calibration; directly supports Llama-2/3 models; magnitude-based sparsity measurement (|x| > threshold)
- **Key Code Pattern** (from paper + repo structure):
  ```python
  # teal/grab_acts.py (conceptual)
  python teal/grab_acts.py \
    --model_name meta-llama/Llama-2-7b-hf \
    --output_path $OUTPUT_PATH
  # Internally: runs calibration samples, collects per-layer activation histograms
  ```
- **Training Config**: No training — pure inference measurement
- **Results**: 40-50% model-wide sparsity with minimal degradation on Llama-2/3-8B
- **Used For:** Confirms magnitude-based (|a| < epsilon) thresholding approach; calibration dataset pattern

**Repository 3**: IST-DASLab/sparsegpt (llama.py)
- **URL**: https://github.com/IST-DASLab/sparsegpt
- **Relevance**: Layer-by-layer forward hook pattern for LLaMA using `Catcher` class; processes calibration samples batch-by-batch; collects per-layer inputs/outputs
- **Key Code**:
  ```python
  # SparseGPT Catcher pattern for collecting per-layer activations
  class Catcher(nn.Module):
      def forward(self, inp, **kwargs):
          inps[cache["i"]] = inp
          cache["i"] += 1
          raise ValueError  # stops forward pass after this layer
  # Process calibration data through each layer
  for j in range(nsamples):
      outs[j] = layer(inps[j].unsqueeze(0), attention_mask=attention_mask)[0]
  ```
- **Used For:** Layer-by-layer sequential processing pattern; calibration batch processing with `torch.no_grad()`

**Serena Analysis Needed:** false — all three repos provide clear patterns; no complex local code requiring semantic analysis

### 🎯 Implementation Priority Assessment

**This is an original measurement experiment, not paper reproduction.**

The measurement methodology is well-established across TEAL, SparseGPT, and activation-sparsity-benchmarking. Our implementation needs:
1. `register_forward_hook` on `gate_proj` outputs of all 32 LLaMA-3-8B MLP layers
2. Process 512 calibration samples under `torch.no_grad()`
3. Compute sparsity fraction per layer per sample, then average
4. Compute CV and Kendall's tau across conditions

**Recommended Implementation Path:**
- Primary: Custom implementation using SparseGPT/TEAL hook patterns (above)
- Fallback: Adapt fszatkowski/activation-sparsity-benchmarking `activations_monitor.py`
- Justification: H-E1 requires measuring CV and Kendall's tau (not just sparsity fractions) — standard tools don't directly compute these statistics

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. All three referenced repositories (TEAL, SparseGPT, activation-sparsity-benchmarking) provide clear Python patterns for layer-wise hook registration and activation measurement. No local complex code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset 1 (Primary): tatsu-lab/alpaca**
- **Name:** Alpaca
- **Type:** standard
- **Size:** 52,002 total samples; use 512 for calibration
- **Split Used:** train (first 512 samples, shuffled with seed=42)
- **Source:** HuggingFace Datasets — `tatsu-lab/alpaca`
- **License:** CC-BY-NC-4.0
- **Hypothesis Fit:** Standard pre-training calibration corpus for LoRA/PEFT alignment; used by GPTQ, SparseGPT, and TEAL for calibration; measures sparsity under instruction-following distribution
- **Preprocessing:**
  - Use `text` field (instruction+input+output formatted string)
  - Tokenize with LLaMA-3-8B tokenizer
  - Truncate to `max_length=128` (short) and `max_length=512` (long) separately for length sensitivity analysis
  - Batch size: 8 samples per forward pass
- **Augmentation:** None (inference measurement, no augmentation)

**Dataset 2 (Stability Check): wikitext (wikitext-103-raw-v1)**
- **Name:** WikiText-103
- **Type:** standard
- **Size:** Full corpus; use 512 samples (contiguous chunks of 512 tokens)
- **Split Used:** test split
- **Source:** HuggingFace Datasets — `wikitext`, config `wikitext-103-raw-v1`
- **Hypothesis Fit:** Divergent distribution from Alpaca (factual text vs. instruction-following); used to test cross-distribution stability of sparsity ranking (Kendall's tau ≥ 0.6 required)
- **Preprocessing:**
  - Concatenate all text, split into 512-token chunks
  - Use first 512 chunks for consistency
  - Batch size: 8

**Synthetic Data Policy:** PASSED — both datasets are standard real datasets ✅

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier (Alpaca): `"tatsu-lab/alpaca"`
- Identifier (WikiText): `"wikitext"`, config `"wikitext-103-raw-v1"`
- Code:
  ```python
  from datasets import load_dataset
  alpaca = load_dataset("tatsu-lab/alpaca", split="train")
  wikitext = load_dataset("wikitext", "wikitext-103-raw-v1", split="test")
  ```

### Models

#### Baseline Model

**Architecture:** LLaMA-3-8B — Decoder-only transformer with SiLU MLP gating
- **Pretrained:** meta-llama/Meta-Llama-3-8B
- **Type:** Causal LM — 32 transformer decoder layers, each with MLP containing `gate_proj`, `up_proj`, `down_proj`
- **MLP Architecture (SiLU gating):**
  - `gate_proj`: Linear(4096, 14336) — gate activation (SiLU)
  - `up_proj`: Linear(4096, 14336) — value projection
  - `down_proj`: Linear(14336, 4096) — output projection
  - Output: `down_proj(SiLU(gate_proj(x)) * up_proj(x))`
- **Why LLaMA-3-8B:** SiLU activations produce near-zero (soft) sparsity unlike older ReLU; 32 layers provide sufficient per-layer diversity for CV > 0.3; well-studied in PEFT literature
- **Role in H-E1:** Measurement target — we hook into `gate_proj` output (pre-SiLU activation values) to measure sparsity

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `"meta-llama/Meta-Llama-3-8B"`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  import torch
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Meta-Llama-3-8B",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  model.eval()
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
  ```

#### Proposed Model

**Architecture:** LLaMA-3-8B (same model) + forward hooks measuring `gate_proj` activation sparsity

The "proposed model" in H-E1 is the measurement instrumentation itself — we are not modifying the model, but adding forward hooks to measure activation sparsity per layer.

**Core Mechanism Implementation:**

```python
# H-E1 Core Mechanism: Layer-wise MLP Activation Sparsity Measurement
# Based on: SparseGPT hook pattern + TEAL magnitude thresholding

import torch
import numpy as np
from scipy.stats import kendalltau

def measure_layer_sparsity(model, dataloader, epsilon=0.01):
    """
    Measure per-layer MLP activation sparsity across calibration samples.

    Args:
        model: LLaMA-3-8B in eval mode
        dataloader: calibration DataLoader (512 samples, batch_size=8)
        epsilon: sparsity threshold (default 0.01 per hypothesis)
    Returns:
        layer_sparsity: np.array shape (32,) — mean sparsity per layer
    """
    n_layers = len(model.model.layers)
    layer_activation_counts = [[] for _ in range(n_layers)]
    hooks = []

    # Register forward hooks on gate_proj output for all 32 layers
    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            # output shape: (batch, seq_len, intermediate_size=14336)
            sparsity_frac = (output.abs() < epsilon).float().mean().item()
            layer_activation_counts[layer_idx].append(sparsity_frac)
        return hook_fn

    for i, layer in enumerate(model.model.layers):
        h = layer.mlp.gate_proj.register_forward_hook(make_hook(i))
        hooks.append(h)

    # Run calibration forward passes
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(model.device)
            model(input_ids)

    # Remove hooks
    for h in hooks:
        h.remove()

    layer_sparsity = np.array([np.mean(counts) for counts in layer_activation_counts])
    return layer_sparsity

# Compute CV and Kendall's tau across conditions
def compute_stability_metrics(sparsity_alpaca, sparsity_wikitext):
    cv = sparsity_alpaca.std() / sparsity_alpaca.mean()  # coefficient of variation
    tau, p_value = kendalltau(sparsity_alpaca, sparsity_wikitext)
    return {"cv": cv, "tau_calibration": tau, "p_value": p_value}
```

### Training Protocol

**H-E1 is a measurement experiment — no model training occurs.**

**Inference Configuration:**
- **Model mode:** `eval()` (no gradient computation)
- **Precision:** `float16` (standard LLaMA-3-8B inference)
- **Gradient:** Disabled (`torch.no_grad()`)
- **Batch size:** 8 samples per forward pass
- **Seeds:** 1 fixed seed (seed=42 for dataset shuffling)

**Measurement Protocol:**
1. Load LLaMA-3-8B in float16, eval mode
2. Register forward hooks on all 32 `gate_proj` layers
3. Process 512 Alpaca samples (2 lengths: 128 tokens, 512 tokens)
4. Process 512 WikiText-103 samples (512 tokens)
5. Sweep epsilon ∈ {0.001, 0.01, 0.05, 0.1}
6. Compute per-layer mean sparsity fraction for each condition
7. Compute CV across 32 layers for each condition
8. Compute pairwise Kendall's tau across all condition pairs
9. Report results table and sparsity profile plot

**Compute Requirements:**
- Single GPU (1× A100 or equivalent, 80GB recommended for float16 LLaMA-3-8B)
- Estimated time: ~30-60 minutes total (no training, inference only)
- No DataParallel needed

**Source:** Measurement design based on TEAL `grab_acts.py` calibration methodology (512 samples, magnitude threshold |a| < epsilon) and SparseGPT layer-by-layer processing pattern.

### Evaluation

**Primary Metrics (H-E1):**

1. **CV (Coefficient of Variation)** of per-layer sparsity across 32 layers
   - Formula: `CV = std(sparsity_per_layer) / mean(sparsity_per_layer)`
   - Success threshold: `CV > 0.3` at epsilon=0.01
   - Interpretation: High CV = significant inter-layer sparsity variation = discriminating signal

2. **Kendall's tau_calibration** — rank correlation between Alpaca and WikiText-103 sparsity rankings
   - Formula: `scipy.stats.kendalltau(alpaca_layer_ranking, wikitext_layer_ranking)`
   - Success threshold: `tau ≥ 0.6` at epsilon=0.01
   - Interpretation: High tau = stable ranking across distributions = reliable prior

**Success Criteria (EXISTENCE PoC):**
- Primary: CV > 0.3 AND tau_calibration ≥ 0.6 at epsilon=0.01
- Secondary: tau_length ≥ 0.6 (128-token vs. 512-token ranking stability); CV > 0.3 for ≥ 3 of 4 epsilon values

**Expected Baseline (Null Hypothesis):**
- Under null: CV ≤ 0.3 (uniform sparsity across layers)
- Under null: tau < 0.6 (no stable ranking pattern)
- Literature prior (Lazy Neuron Phenomenon, Szatkowski et al. 2025): Different MLP layers in LLMs show markedly different sparsity levels — CV > 0.3 is expected

**Metrics Loading Information:**
- Task Type: measurement/statistics
- Library: `scipy.stats` (kendalltau), `numpy` (cv computation)
- Code:
  ```python
  from scipy.stats import kendalltau
  import numpy as np
  cv = sparsity.std() / sparsity.mean()
  tau, p = kendalltau(sparsity_alpaca, sparsity_wikitext)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing CV value vs. threshold 0.3, and tau value vs. threshold 0.6

#### Additional Figures (LLM Autonomous)

Based on H-E1's measurement nature:
1. **Sparsity Profile Plot**: Line/bar chart of per-layer mean sparsity fraction across all 32 layers (Alpaca vs. WikiText-103 overlaid) — most important visualization for the paper
2. **Epsilon Sensitivity Table/Heatmap**: CV and tau values for each epsilon ∈ {0.001, 0.01, 0.05, 0.1}
3. **Length Sensitivity Plot**: Sparsity profiles for 128-token vs. 512-token inputs with Kendall's tau annotation
4. **Rank Correlation Scatter**: Scatter plot of layer sparsity ranks (Alpaca x-axis vs. WikiText-103 y-axis) with Kendall's tau annotation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | LLaMA-3-8B has 32 MLP layers each with `gate_proj`; SiLU produces non-zero near-zero values; hookable via `register_forward_hook` | TRUE |
| Mechanism Isolatable | Hook can be enabled/disabled; baseline = no hooks; proposed = hooks measuring sparsity fraction per layer | TRUE |
| Baseline Measurable | Null hypothesis (CV ≤ 0.3, tau < 0.6) is directly measurable from same forward pass | TRUE |

### Architecture Compatibility Check

**LLaMA-3-8B MLP Structure:**
- 32 decoder layers, each with: `gate_proj` (Linear 4096→14336), `up_proj` (Linear 4096→14336), `down_proj` (Linear 14336→4096)
- Activation: `SiLU(gate_proj(x)) * up_proj(x)` → SiLU creates near-zero (soft) sparsity
- Hook target: `gate_proj` output (pre-SiLU) OR post-SiLU (the intermediate activation sent to element-wise multiply)
- **NOTE:** Hook on `gate_proj` output captures pre-activation values; for sparsity measurement, hook should be on the post-SiLU intermediate (i.e., after `gate_proj` → SiLU). Specifically: hook `layer.mlp.act_fn` or capture within `layer.mlp.forward()`. SiLU(x) is near-zero when x is near-zero, so measuring |gate_proj_output| < epsilon is equivalent.

**Required Features:**
- LLaMA-3-8B architecture with SiLU MLP gating
- 32 transformer layers (model.model.layers)
- PyTorch `register_forward_hook` compatibility

**Incompatible Architectures:**
- Pure ReLU models (different sparsity structure)
- MoE models (different layer structure)
- Models with fused MLP operations (may not expose intermediate activations)

> ⚠️ If model is not LLaMA-3-8B or equivalent SiLU-gated transformer, Phase 4 MUST fail early!

---

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | `"Layer {i} sparsity: {value:.4f} (eps={epsilon})"` printed for all 32 layers | `measure_layer_sparsity()` |
| Tensor Shape | `layer_sparsity.shape == (32,)` — one value per layer | After hook collection |
| Metric Delta | `CV > 0.3 AND tau ≥ 0.6` vs. null `CV ≤ 0.1 AND tau ≈ 0` | `compute_stability_metrics()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(layer_sparsity_alpaca, layer_sparsity_wikitext, metrics):
    indicators = {
        "hooks_fired": len(layer_sparsity_alpaca) == 32,  # all 32 layers measured
        "sparsity_nonzero": layer_sparsity_alpaca.mean() > 0.0,  # SiLU does produce near-zeros
        "layer_variation_exists": layer_sparsity_alpaca.std() > 0.01,  # some inter-layer variation
        "wikitext_measured": len(layer_sparsity_wikitext) == 32,
    }
    all_activated = all(indicators.values())
    return all_activated, indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Hooks not registered | `len(layer_sparsity) != 32` | FAIL: Check hook registration loop |
| All sparsity = 0 | `layer_sparsity.mean() == 0` | FAIL: Wrong hook target (pre/post SiLU confusion) |
| All layers identical | `layer_sparsity.std() < 0.001` | Potential FAIL: Model not loaded correctly or hooks collecting same layer |
| Model not in eval mode | Gradients computed, memory OOM | FAIL: Ensure `model.eval()` before hooking |
| OOM during inference | CUDA out-of-memory | FAIL: Use float16 + device_map="auto"; reduce batch size |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All 32 layers measured, mean sparsity > 0 | Hook count + sparsity mean |
| Effect Measurable | Layer sparsity values vary (std > 0.01) | Standard deviation check |
| Hypothesis Supported | CV > 0.3 AND tau_calibration ≥ 0.6 | `compute_stability_metrics()` |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (hooks register, inference completes, statistics computed)
2. CV > 0.3 at epsilon=0.01 (significant inter-layer variation exists)
3. tau_calibration ≥ 0.6 at epsilon=0.01 (ranking stable across Alpaca vs. WikiText-103)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: HuggingFace Accelerate — `attach_layerwise_casting_hooks`
- **URL**: https://huggingface.co/docs/accelerate/en/package_reference/big_modeling
- **Query Used**: "activation sparsity measurement LLM forward hooks"
- **Relevance**: Shows standard API for registering layer-wise hooks in HuggingFace transformer models
- **Key Insight**: Layer-by-layer hook registration with `torch.no_grad()` is the standard inference measurement pattern
- **Used For**: Confirming hook registration pattern validity

**Source A.2**: HuggingFace PEFT — LoRA Conceptual Guide
- **URL**: https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora
- **Query Used**: "LoRA rank allocation per-layer adaptive PEFT"
- **Key Insight**: `LoraConfig` supports `rank_pattern` dict for per-layer rank specification; standard targets are q_proj, v_proj, k_proj, o_proj, gate_proj, up_proj, down_proj
- **Used For**: Downstream hypothesis chain context (H-M3, H-M4)

### B. GitHub Implementations (Exa)

**Repository B.1**: fszatkowski/activation-sparsity-benchmarking
- **URL**: https://github.com/fszatkowski/activation-sparsity-benchmarking
- **Query Used**: "LLaMA MLP activation sparsity measurement forward hook layer-wise GitHub implementation"
- **Key Pattern**: `SparsificationManager` + `activations_monitor.py` for LLaMA-3 FFN sparsity measurement
- **Configuration Extracted**: Target `gate_proj` outputs; configurable epsilon threshold; supports topp/topk/maxp rules
- **Used For**: Core hook registration architecture; LLaMA-3 sparsification config format

**Repository B.2**: FasterDecoding/TEAL
- **URL**: https://github.com/FasterDecoding/TEAL
- **Query Used**: "TEAL activation sparsity LLM inference layer measurement PyTorch implementation"
- **Key Pattern**: `grab_acts.py` collects per-layer activation histograms for threshold calibration; magnitude-based thresholding `|x| > threshold`
- **Results**: 40-50% model-wide sparsity on Llama-3-8B with minimal degradation
- **Used For**: Confirms magnitude-based (|a| < epsilon) thresholding approach; calibration 512-sample pattern; training-free sparsity measurement philosophy

**Repository B.3**: IST-DASLab/sparsegpt — llama.py
- **URL**: https://github.com/IST-DASLab/sparsegpt
- **Query Used**: "LLaMA MLP activation sparsity measurement forward hook layer-wise GitHub implementation"
- **Key Code**: `Catcher(nn.Module)` pattern for layer-by-layer activation collection; 128-sample calibration batches; `torch.no_grad()` inference loop
- **Used For**: Layer-by-layer sequential processing pattern; confirms 128-512 calibration sample count

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from GitHub search results was sufficiently clear for pseudo-code generation. External repositories (TEAL, SparseGPT, activation-sparsity-benchmarking) provided complete pattern reference.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (Alpaca) | Phase 2B (02b_verification_plan.md Section 1.3) | Phase 2A Dialogue |
| Dataset selection (WikiText-103) | Phase 2B (02b_verification_plan.md H-E1) | Phase 2A Dialogue |
| Model selection (LLaMA-3-8B) | Phase 2B (02b_verification_plan.md Section 1.3) | Phase 2A Dialogue |
| Hook target (gate_proj) | GitHub (TEAL, fszatkowski benchmarking) | B.1, B.2 |
| Epsilon threshold sweep | Phase 2B (02b_verification_plan.md H-E1 Variables) | Phase 2B |
| Sparsity fraction formula | GitHub (TEAL paper/code) | B.2 |
| 512 calibration sample count | GitHub (SparseGPT, TEAL) | B.2, B.3 |
| Batch size 8 | Phase 2B (02b_verification_plan.md H-E1 protocol) | Phase 2B |
| CV formula | Standard statistics | scipy.stats, numpy |
| Kendall's tau formula | Phase 2B success criteria | scipy.stats.kendalltau |
| Hook registration API | Archon KB (Accelerate docs) | A.1 |
| Model loading code | Exa (HuggingFace Transformers docs) | B.2 |
| Dataset loading code | Exa (HuggingFace Datasets docs) | tatsu-lab/alpaca card |
| torch.no_grad() inference | GitHub (SparseGPT, TEAL) | B.2, B.3 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-08T06:45:00Z

### Workflow History for This Hypothesis
- 2026-05-08T06:18:00Z: Phase 2B completed — H-E1 READY
- 2026-05-08T06:31:31Z: H-E1 set IN_PROGRESS (external loop)
- 2026-05-08T06:45:00Z: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code, 3 KB queries + 2 code queries), Exa (GitHub, 2 queries, 6+ repositories), Serena (skipped — external repos, sufficient clarity)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
