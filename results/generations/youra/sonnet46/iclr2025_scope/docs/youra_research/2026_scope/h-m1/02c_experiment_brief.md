# Experiment Design: h-m1

**Date:** 2026-05-08
**Author:** Anonymous
**Hypothesis Statement:** Layer-wise MLP activation sparsity profiles in LLaMA-3-8B are stable across diverse calibration distributions (Alpaca, WikiText-103, SST-2 val, MNLI val), with ICC > 0.75 and all pairwise Kendall's tau >= 0.6, because sparsity reflects architectural pre-training geometry rather than input-distribution artifacts.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Validates cross-distribution stability of sparsity profiles using ICC and pairwise Kendall's tau.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 PASS (MUST_WORK — CV=0.544 > 0.3, tau_calibration=0.786 >= 0.6)
**Gate Status:** MUST_WORK — ICC(3,k) > 0.75 AND all 6 pairwise Kendall's tau >= 0.6

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 ✅ PASS

### Gate Condition
**MUST_WORK:**
1. ICC(3,k) computed across 4 distributions (Alpaca, WikiText-103, SST-2 val, MNLI val) > 0.75
2. All 6 pairwise Kendall's tau values (C(4,2)=6 pairs) >= 0.6

If either condition fails, h-m3 and h-m4 are blocked (sparsity-guided allocation requires distribution-stable sparsity profiles).

---

## Continuation Context

H-E1 validated the existence of significant layer-wise activation sparsity variation in LLaMA-3.1-8B (CV=0.544 > 0.3) and cross-dataset stability for 2 distributions (Alpaca vs WikiText-103, tau=0.786). H-M1 extends this to 4 distributions and adds ICC as a stronger statistical reliability test.

**Key reuse from h-e1:**
- Measurement infrastructure: `h-e1/code/measure_sparsity.py` (forward hooks on gate_proj, epsilon=0.01)
- Data utilities: `h-e1/code/data_utils.py` (Alpaca, WikiText-103 loaders)
- Optimal epsilon: 0.01 (primary), with sensitivity check at {0.001, 0.01, 0.05, 0.1}

### Previous Hypothesis Results (if applicable)
| Metric | h-e1 Result | h-m1 Threshold |
|--------|------------|----------------|
| CV (Alpaca) | 0.544 | N/A (inherited) |
| tau (Alpaca vs WikiText-103) | 0.786 | >= 0.6 (1 of 6 pairs proven) |
| ICC(3,k) | Not tested | > 0.75 |

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "activation sparsity distribution stability measurement" (match_count=5)**
- Results: Low relevance (Archon KB primarily contains image generation/diffusion model content)
- Key insight from adjacent findings: HuggingFace PEFT docs confirm LoRA adapter architecture; accelerate hooks demonstrate layerwise hook attachment patterns

**Query 2: "LoRA rank allocation LLM fine-tuning calibration" (match_count=5)**
- Result: HuggingFace PEFT conceptual guides (similarity=0.557) — confirms PEFT/LoRA rank is a calibration-sensitive parameter
- Key insight: rank selection in LoRA directly affects parameter efficiency; calibration dataset choice is a recognized concern

**Query 3: "intraclass correlation coefficient ICC reliability measurement" (match_count=5)**
- Results: Low relevance (no matching content in Archon KB)
- Determination: ICC computation must use external Python library (pingouin); confirmed via Exa search

**Overall Archon Assessment:** Archon KB does not contain domain-specific prior cases for this exact hypothesis. Design is grounded in Exa findings + h-e1 proven infrastructure.

### Archon Code Examples

**Query 1: "activation sparsity forward hook LLM PyTorch" (match_count=5)**
- Code Example: `accelerate.hooks.attach_layerwise_casting_hooks` — demonstrates pattern for attaching forward hooks to transformer layers by name
- Pattern: `attach_layerwise_casting_hooks(model, storage_dtype=..., compute_dtype=..., skip_modules_pattern=[...])` — skip_modules_pattern relevant for excluding non-MLP layers
- Insight: Hooks can be selectively applied per-module using pattern matching; used to target only `gate_proj` layers

**Query 2: "Kendall tau correlation scipy statistics ranking" (match_count=5)**
- Results: No direct scipy.stats.kendalltau examples in KB
- Determination: Use `scipy.stats.kendalltau(sparsity_a, sparsity_b)` directly (standard API, well-documented)

### Exa GitHub Implementations

**Query 1: "LLaMA activation sparsity cross-distribution stability ICC measurement PyTorch"**

**Repository 1**: fszatkowski/activation-sparsity-benchmarking
- **URL**: https://github.com/fszatkowski/activation-sparsity-benchmarking
- **Relevance**: Systematic layerwise activation sparsity benchmarking across LLaMA-3 models with configurable rules/thresholds; sparsification_utils.py records activation statistics across layers
- **Architecture**: Forward hooks into FFN layers via SparsificationManager; configurable per-module targeting via JSON configs
- **Key Patterns**:
  - `activations_monitor.py` — records activation statistics during forward passes
  - JSON sparsification configs map module names for Llama3 architecture (gate_proj, up_proj, down_proj)
  - Support for multiple evaluation datasets (task suite)
- **Relevance to h-m1**: Provides validated framework for multi-dataset activation measurement; their activations_monitor directly inspired our multi-distribution sparsity collection strategy

**LaRoSA Paper Finding** (from arxiv.org/html/2507.01299v2):
- Explicitly tests calibration dataset stability: LLaMA2-7B and LLaMA3-8B with WikiText2 vs Alpaca
- Finding: "choice of calibration datasets has a relatively minimal effect on sparsified model performance" — supports our h-m1 hypothesis
- Key quote: "covariance matrices of input activations within the same layer exhibit a high degree of cosine similarity across different data inputs"
- Used for: Hypothesis plausibility backing; suggests ICC > 0.75 is achievable

**TEAL Paper Finding** (arxiv.org/abs/2408.14690):
- Magnitude-based activation sparsity applied across Llama-2, Llama-3, Mistral families
- Sparsity computed on hidden states throughout entire model
- Measurement: fraction of activations below magnitude threshold
- Calibration: offline calibration on WikiText using quantile threshold

**Query 2: "LLM MLP activation sparsity measurement forward hook Kendall tau"**
- Confirmed: Activation sparsity measurement via forward hooks is standard practice
- fszatkowski/activation-sparsity-benchmarking confirmed as primary reference implementation
- Jaccard similarity used in LLaDA paper (arxiv.org/pdf/2509.00454) for sparsity pattern stability — conceptually related to our Kendall's tau approach

**Serena Analysis Needed**: false (code from h-e1 is already analyzed and understood)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment is an original measurement study (not paper reproduction). Implementation priority:
1. **Reuse h-e1/code/** — proven, validated, uses correct LLaMA-3.1-8B forward hooks
2. **fszatkowski/activation-sparsity-benchmarking** — reference for multi-dataset activation monitoring patterns
3. **pingouin.intraclass_corr()** — standard ICC(3,k) implementation

**Recommended Implementation Path:**
- Primary: Extend h-e1/code/ with 2 additional dataset loaders (SST-2 val, MNLI val) + ICC computation module
- Fallback: Fresh implementation following fszatkowski patterns
- Justification: h-e1 code was validated (16/16 tests pass, correct results), minimizes implementation risk; only new additions are dataset loading and ICC statistics

### Code Analysis (Serena MCP)

*Skipped* — H-M1 reuses measurement infrastructure from h-e1/code/. The existing code (measure_sparsity.py, data_utils.py, compute_metrics.py) was validated in h-e1 and directly applicable. New additions (ICC via pingouin, 2 additional dataset loaders) are standard library calls without complex architecture patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** 4-Distribution Calibration Set
**Type:** standard (real, established datasets via HuggingFace Hub)
**Synthetic data policy:** PASSED — all datasets are real

| Distribution | Dataset | HuggingFace ID | Split | Samples | Domain |
|--------------|---------|----------------|-------|---------|--------|
| D1: Alpaca | tatsu-lab/alpaca | `tatsu-lab/alpaca` | train | 512 | Instruction-following |
| D2: WikiText-103 | wikitext-103-raw-v1 | `wikitext` (103-raw-v1) | test | 512 chunks (128 tok) | General prose |
| D3: SST-2 val | GLUE SST-2 | `nyu-mll/glue`, subset `sst2` | validation | 512 | Sentiment (short sentences) |
| D4: MNLI val | GLUE MNLI | `nyu-mll/glue`, subset `mnli` | validation_matched | 512 | NLI (premise-hypothesis pairs) |

**Preprocessing:**
- Tokenizer: `meta-llama/Llama-3.1-8B` tokenizer (AutoTokenizer)
- Max sequence length: 512 tokens (consistent with h-e1)
- For each sample: encode text, pass through model with hooks active, collect gate_proj activations
- Alpaca: use `instruction + input + output` concatenated fields (same as h-e1)
- WikiText-103: sliding window chunks of 512 tokens (same as h-e1)
- SST-2: `sentence` field, padded/truncated to 512 tokens
- MNLI: `premise + " [SEP] " + hypothesis` concatenated, padded/truncated to 512 tokens

**Why these 4 distributions:**
- D1+D2: Proven stable in h-e1 (tau=0.786); included for ICC consistency
- D3 (SST-2): Short single-sentence inputs — tests stability under very different length distribution
- D4 (MNLI): Sentence pairs from 10 diverse genres — tests stability across multi-genre NLI inputs

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- Identifier: `tatsu-lab/alpaca`, `wikitext` (103-raw-v1), `nyu-mll/glue` (sst2, mnli)
- Code:
  ```python
  from datasets import load_dataset
  alpaca = load_dataset("tatsu-lab/alpaca", split="train")
  wikitext = load_dataset("wikitext", "wikitext-103-raw-v1", split="test")
  sst2 = load_dataset("nyu-mll/glue", "sst2", split="validation")
  mnli = load_dataset("nyu-mll/glue", "mnli", split="validation_matched")
  ```

### Models

#### Baseline Model

**Architecture:** LLaMA-3.1-8B (base pretrained model, no fine-tuning)
**Role:** Provide MLP layer activations for sparsity measurement across 4 distributions
**Configuration:**
- Layers: 32 transformer blocks, each with MLP containing gate_proj, up_proj, down_proj
- Hidden size: 4096, Intermediate size: 14336
- Activation function: SiLU (gated)
- dtype: float16 (device_map=auto)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers` (AutoModelForCausalLM)
- Identifier: `meta-llama/Llama-3.1-8B` (Note: h-e1 used Llama-3.1-8B despite pipeline spec saying Meta-Llama-3-8B; use 3.1 for consistency)
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-3.1-8B",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  model.eval()
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")
  ```

#### Proposed Model

**Architecture:** Same LLaMA-3.1-8B model — this is a MEASUREMENT experiment, not a training experiment.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Cross-Distribution Sparsity Profile Measurement
# Based on: h-e1/code/measure_sparsity.py + fszatkowski/activation-sparsity-benchmarking
# New additions: 2 extra dataset loaders + ICC(3,k) computation

def make_sparsity_hook(layer_idx, activation_store, epsilon=0.01):
    """Register forward hook on gate_proj to capture MLP activation sparsity."""
    def hook(module, input, output):
        # output shape: (batch, seq_len, 14336) for gate_proj
        with torch.no_grad():
            sparsity = (output.abs() < epsilon).float().mean().item()
        activation_store[layer_idx].append(sparsity)
    return hook

def measure_sparsity_for_distribution(model, dataloader, epsilon=0.01):
    """Measure per-layer sparsity across 512 samples for one distribution."""
    store = {i: [] for i in range(model.config.num_hidden_layers)}
    hooks = []
    for layer_idx in range(model.config.num_hidden_layers):
        h = model.model.layers[layer_idx].mlp.gate_proj.register_forward_hook(
            make_sparsity_hook(layer_idx, store, epsilon)
        )
        hooks.append(h)
    with torch.no_grad():
        for batch in dataloader:  # 512 samples total
            model(**batch)
    for h in hooks:
        h.remove()
    return {i: np.mean(store[i]) for i in range(32)}  # shape: (32,)

# Returns: sparsity_profiles[dist_name] = array of shape (32,)
# 4 distributions × 32 layers = (4, 32) matrix
```

### Training Protocol

**Type:** Measurement-only experiment — NO training/fine-tuning performed.

**Execution Protocol:**
- **Step 1: Environment Setup**
  - Load LLaMA-3.1-8B (float16, device_map=auto)
  - Set CUDA_VISIBLE_DEVICES to single GPU (H100)
  - Set seeds: numpy.random.seed(42), torch.manual_seed(42)

- **Step 2: Dataset Preparation**
  - Load 4 datasets from HuggingFace Hub (see Dataset section)
  - Sample 512 items from each, encode with tokenizer (max_length=512, padding=True, truncation=True)
  - Create DataLoaders with batch_size=8, shuffle=False

- **Step 3: Multi-Distribution Sparsity Measurement**
  - For each distribution D ∈ {Alpaca, WikiText-103, SST-2, MNLI}:
    - Run `measure_sparsity_for_distribution(model, dataloader_D, epsilon=0.01)`
    - Store result as `sparsity_profiles[D]` — shape (32,)
  - Repeat for epsilon ∈ {0.001, 0.01, 0.05, 0.1} (sensitivity analysis)

- **Step 4: Statistical Analysis**
  - Compute ICC(3,k) using pingouin across 4 distributions (targets=layers, raters=distributions)
  - Compute all 6 pairwise Kendall's tau values using scipy.stats.kendalltau
  - Check gate conditions

- **Step 5: Visualization**
  - Sparsity profile heatmap (4 distributions × 32 layers)
  - ICC confidence interval plot
  - Pairwise tau matrix heatmap
  - Gate metrics bar chart

**Dependencies:**
```
torch, transformers, datasets, numpy, scipy, pingouin, pandas, matplotlib, seaborn
```

**Compute Estimate:**
- Model load: ~15GB VRAM (float16)
- 4 distributions × 512 samples × forward pass: ~10-20 minutes on H100

### Evaluation

**Primary Metrics:**

| Metric | Definition | Gate Threshold | Expected Range |
|--------|-----------|---------------|----------------|
| ICC(3,k) | Two-way mixed, consistency, average-measures ICC across 4 distributions (targets=layers, raters=distributions) | > 0.75 | 0.80-0.95 (based on h-e1 tau=0.786 and LaRoSA calibration stability) |
| tau_min | Minimum of all 6 pairwise Kendall's tau values | >= 0.6 | 0.65-0.80 (h-e1 showed tau=0.786 for 1 pair; 6-pair minimum expected slightly lower) |
| tau_all | Individual pairwise tau values for all 6 pairs | all >= 0.6 | Report all 6 |

**ICC Computation (pingouin):**
```python
import pingouin as pg
import pandas as pd

# Build long-format DataFrame for pingouin
rows = []
for dist_name, sparsity_vec in sparsity_profiles.items():
    for layer_idx, val in enumerate(sparsity_vec):
        rows.append({"layer": layer_idx, "distribution": dist_name, "sparsity": val})
df = pd.DataFrame(rows)

# ICC(3,k): two-way mixed, consistency, k-rater (average)
icc_results = pg.intraclass_corr(data=df, targets="layer", raters="distribution", ratings="sparsity")
icc3k = icc_results[icc_results["Type"] == "ICC3k"]["ICC"].values[0]
ci_lower, ci_upper = icc_results[icc_results["Type"] == "ICC3k"]["CI95%"].values[0]
```

**Pairwise Kendall's tau:**
```python
from scipy.stats import kendalltau
import itertools

distributions = ["alpaca", "wikitext", "sst2", "mnli"]
tau_results = {}
for d1, d2 in itertools.combinations(distributions, 2):
    tau, pval = kendalltau(sparsity_profiles[d1], sparsity_profiles[d2])
    tau_results[f"{d1}_vs_{d2}"] = {"tau": tau, "pval": pval}
tau_min = min(v["tau"] for v in tau_results.values())
```

**Success Criteria:**
- GATE PASS: `icc3k > 0.75` AND `tau_min >= 0.6`
- GATE FAIL: Either condition not met → block h-m3, h-m4; log failure with LaserRank alternative routing

**Expected Baseline Performance** (from research):
- LaRoSA (2025): cosine similarity of covariance matrices between WikiText2 and Alpaca "high degree" — supports ICC > 0.75
- h-e1 result: Alpaca vs WikiText-103 tau=0.786 (1 of 6 pairs already meets threshold)
- Conservative estimate: ICC(3,k) ≈ 0.80-0.90, tau_min ≈ 0.65-0.75

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical reliability analysis (measurement study, no classification training)
- Library: `pingouin` (ICC), `scipy.stats` (Kendall's tau), `numpy` (general statistics)
- Code:
  ```python
  pip install pingouin scipy numpy pandas
  import pingouin as pg
  from scipy.stats import kendalltau
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing ICC(3,k) and tau_min vs thresholds (0.75 and 0.6 dashed lines)
  - Save to: `h-m1/figures/gate_metrics.png`

#### Additional Figures (LLM Autonomous)

1. **Sparsity Profile Heatmap** — 32 layers × 4 distributions, colormap showing sparsity values
   - Enables visual inspection of cross-distribution profile consistency
   - Save to: `h-m1/figures/sparsity_heatmap.png`

2. **Pairwise Tau Matrix** — 4×4 heatmap of all Kendall's tau values (symmetric, diagonal=1.0)
   - Shows which distribution pairs are most/least similar
   - Save to: `h-m1/figures/pairwise_tau_matrix.png`

3. **ICC Confidence Interval** — Forest plot or bar with 95% CI for ICC3k value vs threshold
   - Save to: `h-m1/figures/icc_confidence.png`

4. **Layer-by-Layer Sparsity Lines** — 4 line plots overlaid, x=layer index, y=sparsity value
   - Visually demonstrates profile similarity across distributions
   - Save to: `h-m1/figures/sparsity_profiles_overlay.png`

5. **Epsilon Sensitivity** — ICC(3,k) and tau_min vs epsilon (4 values), showing robustness
   - Save to: `h-m1/figures/epsilon_sensitivity.png`

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `icc3k > 0.75` (ICC gate)
3. All 6 pairwise `tau >= 0.6` (tau_min gate)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: HuggingFace PEFT/LoRA conceptual guides
- **Type**: Knowledge base article
- **Query Used**: "LoRA rank allocation LLM fine-tuning calibration"
- **Relevance**: Confirms LoRA rank allocation is calibration-sensitive; validates that our calibration dataset choice is a scientifically important variable
- **Key Insights**: Rank determines capacity for adaptation; calibration data affects threshold selection
- **Used For**: Motivation for studying cross-distribution stability

**Source A.2**: accelerate hooks documentation (attach_layerwise_casting_hooks)
- **Type**: Code example
- **Query Used**: "activation sparsity forward hook LLM PyTorch"
- **Key Pattern**: `attach_layerwise_casting_hooks(model, ..., skip_modules_pattern=["norm"])` — pattern for layer-selective hook attachment
- **Used For**: Confirming that layer-selective forward hook registration is a standard, supported pattern

### B. GitHub Implementations (Exa)

**Repository B.1**: fszatkowski/activation-sparsity-benchmarking
- **URL**: https://github.com/fszatkowski/activation-sparsity-benchmarking
- **Relevance**: Systematic layerwise activation sparsity benchmarking with multi-dataset support; SparsificationManager uses forward hooks on FFN layers; activations_monitor.py records per-layer stats
- **Architecture**: SparsificationManager with JSON config files specifying module names per model family; configurable rules (topp, topk, maxp); activation monitoring separate from sparsification
- **Configuration Extracted**:
  - LLaMA-3 module names: gate_proj targeted in sparsification configs
  - Evaluation via lm-evaluation-harness (multi-task, multi-dataset)
  - batch_size auto-detection
- **Used For**: Multi-dataset measurement pattern; confirmation of gate_proj as primary sparsification target in LLaMA-3 architecture

**Paper B.2**: LaRoSA (arxiv.org/html/2507.01299v2)
- **Relevance**: Directly addresses calibration dataset stability for LLaMA3-8B; reports WikiText2 vs Alpaca has "minimal effect"; covariance matrices show "high cosine similarity across different data inputs"
- **Used For**: Hypothesis plausibility backing; sets expectation that ICC > 0.75 is achievable

**Paper B.3**: TEAL — Training-Free Activation Sparsity (arxiv.org/abs/2408.14690)
- **Relevance**: Magnitude-based activation sparsity applied to LLaMA-3-8B; calibrated offline on WikiText; demonstrates consistent sparsity patterns across model families
- **Used For**: Confirms calibration methodology (offline, few-shot, WikiText common choice); epsilon-based thresholding consistent with h-e1 approach

**Paper B.4**: Activation Sparsity Benchmarking (arxiv.org/pdf/2509.00454)
- **Relevance**: Uses Jaccard similarity to measure sparsity pattern stability; shows high variance of critical sparsity across evaluation tasks — motivates our ICC approach as a more robust stability metric
- **Used For**: Justification for using Kendall's tau + ICC rather than simple correlation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — h-e1/code/ infrastructure already validated (16/16 tests passing). New additions (ICC via pingouin, 2 additional dataset loaders) are standard library calls without complex architecture patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report — h-e1
- **File**: `h-e1/04_validation.md`
- **Reused Components**:
  - Model: Llama-3.1-8B (float16, device_map=auto) — identical setup
  - Measurement: gate_proj forward hooks, epsilon=0.01, 512 samples — identical
  - Alpaca loader: `tatsu-lab/alpaca`, 512 samples, instruction+input+output concat
  - WikiText-103 loader: `wikitext-103-raw-v1`, 512 chunks of 128 tokens
  - Epsilon sweep: {0.001, 0.01, 0.05, 0.1}
- **Why Reused**: Enables controlled comparison — only statistical test and number of distributions changes; ensures any ICC > 0.75 result is attributable to genuine cross-distribution stability not measurement artifacts

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| 4-distribution dataset selection | Phase 2B plan + verification_state.yaml | h-m1 data_setup.dataset.name |
| Alpaca + WikiText-103 loading | h-e1 validated code | h-e1/code/data_utils.py |
| SST-2 val loading | HuggingFace Hub documentation | nyu-mll/glue, sst2 split |
| MNLI val loading | HuggingFace Hub documentation | nyu-mll/glue, mnli split |
| LLaMA-3.1-8B model | h-e1 validated code | h-e1/04_validation.md |
| gate_proj hook measurement | h-e1 + fszatkowski/benchmarking | B.1, h-e1/code/measure_sparsity.py |
| epsilon=0.01 primary | h-e1 Phase 4 results | h-e1/04_validation.md (all 4 epsilon pass) |
| ICC(3,k) computation | pingouin library documentation | pingouin.intraclass_corr, type ICC3k |
| Pairwise Kendall's tau | scipy.stats.kendalltau (standard API) | scipy documentation |
| Cross-distribution stability hypothesis | LaRoSA paper | arxiv B.2 |
| 0.75 ICC threshold | Phase 2B gate condition | verification_state.yaml h-m1.gate |
| 0.6 tau threshold | h-e1 proven + Phase 2B gate | verification_state.yaml h-m1.gate |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-08

### Workflow History for This Hypothesis
- h-e1 PASS (2026-05-08T10:30:00Z): prerequisites satisfied (CV=0.544, tau=0.786)
- h-m1 Phase 2C IN_PROGRESS → COMPLETED (2026-05-08)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — 5 queries), Exa (GitHub — 2 queries), Serena (skipped)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
