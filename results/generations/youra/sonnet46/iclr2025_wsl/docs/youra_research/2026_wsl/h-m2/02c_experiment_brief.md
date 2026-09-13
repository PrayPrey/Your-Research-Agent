# Experiment Design: H-M2

**Date:** 2026-03-16
**Author:** Anonymous
**Hypothesis Statement:** Permutation augmentation (flat-MLP+aug) and oracle canonicalization (flat-MLP+canon) reduce Δρ compared to flat-MLP baseline but do not match NFT-base performance, confirming that architectural equivariance provides a necessary (not merely convenient) inductive bias for permutation-robust property prediction.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests whether engineering compensations (permutation augmentation, oracle canonicalization) can substitute for architectural equivariance (NFT-base) in FC-MLP model zoo generalization gap prediction.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 ✅ PASS (flat_mlp_delta_rho=0.1595, nft_delta_rho=4.09e-6), H-M1 ✅ PASS (delta_r2=0.228, nft_delta_rho=4.71e-07)
**Gate Status:** SHOULD_WORK (non-blocking; failure narrows claim scope only)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED, MUST_WORK PASS)

### Gate Condition
**SHOULD_WORK:** Three-way ranking must hold at s=1.0:
- flat-MLP+aug: Δρ reduced but > 0.05 (partial, not full compensation)
- flat-MLP+canon: Δρ reduced but > 0.03 (oracle ceiling still suboptimal)
- NFT-base: Δρ < 0.02 (architectural solution outperforms engineering fixes)
- Ranking: NFT-base < oracle-canon < flat-MLP+aug < flat-MLP baseline

**If FAIL:** Narrow claim — "NFT competitive with oracle-canon; augmentation insufficient for full robustness." Pipeline continues to H-M3.

---

## Continuation Context

**This is a continuation experiment (H-M2 follows H-M1 in the verification chain).**

### Previous Hypothesis Results (H-M1)

From h-m1/04_validation.md:
- **NFT-base Δρ (s=1.0):** 4.71e-07 (architectural equivariance proven robust; < 0.02 threshold)
- **ΔR² (mediation):** 0.228 (equivariant attention mediates permutation robustness; > 0.10)
- **flat-MLP Δρ (s=1.0):** 0.6405 (strong baseline degradation)
- **flat-MLP+aug Δρ (s=1.0):** 0.2239 (augmentation reduces ~65% of degradation but insufficient)
- **Oracle-canon Δρ (s=1.0):** ~0.0 in H-M1 (implemented as perfect L2-norm oracle; real imperfect expected > 0.03 at s=1.0)
- **Training config proven:** Adam lr=1e-3, batch=64, epochs=50, 3 seeds {42, 123, 456}
- **Checkpoints available:** `h-m1/code/checkpoints/` (all 6 encoder × 3 seed = 18 checkpoints)
- **Data cache:** `.data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl` ✅

**H-M2 Focus:** This hypothesis directly compares the 3 compensation strategies (none, aug, canon) against NFT-base using the already-trained H-M1 checkpoints. Only the gate evaluator and figure generation need new implementation.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "permutation augmentation equivariance NFT weight space"**
- No relevant results found. Archon KB contains only diffusion/HuggingFace content.
- Similarity scores ~0.33–0.36; no semantic match to weight space learning domain.

**Query 2: "canonicalization augmentation comparison architectural inductive bias"**
- No relevant results found. Top result: OpenAI instruction-following blog (similarity 0.378).
- No content on canonicalization strategies for neural network weight spaces.

**Query 3: "model zoo property prediction encoder comparison"**
- No relevant results. Top results: ControlNet discussion, DreamBooth LoRA example.
- KB does not contain model zoo / property prediction literature.

**Summary:** Archon KB (source: 8b1c7f40739544a6) is a diffusion model / HuggingFace documentation corpus. No relevant implementation cases for H-M2's weight-space learning domain. Design grounded instead in:
1. **H-M1 proven codebase** (Serena analysis — primary source)
2. **Zhou et al. 2023** (NFT paper, primary reference)
3. **Unterthiner et al. 2020** (FC-MLP zoo, data source)
4. **Baron & Kenny 1986** (mediation analysis methodology)

### Archon Code Examples

**Query 1: "permutation augmentation PyTorch weight space encoder"**
- Results: Token gradient zeroing, 8-bit model loading, quantization patterns.
- Rerank scores negative (-9 to -11), confirming no topical match.

**Query 2: "NFT Neural Functional Transformer encoder comparison"**
- Results: 4-bit quantization with BitsAndBytesConfig, FLOPs calculation.
- No NFT-relevant code examples in KB.

**Summary:** No applicable code examples from Archon KB. Implementation relies on H-M1 Serena-analyzed codebase.

### Exa GitHub Implementations

**Query 1:** "Zhou 2023 NFT official implementation GitHub" → 402 Payment Required (Exa API quota exhausted)
**Query 2:** "permutation augmentation canonicalization FC-MLP" → 402 Payment Required
**Query 3:** "Unterthiner model zoo flat-MLP benchmark" → 402 Payment Required

**Exa Status:** Unavailable (402). This is consistent with H-E1 and H-M1 Phase 2C executions.

**Known repositories (from literature, not Exa search):**
- NFT official: `AllanYangZhou/nfn` (Zhou et al. 2023, Neural Functional Networks)
- Unterthiner zoo: `google-research/google-research/dnn_predict_accuracy` (Unterthiner et al. 2020)
- Model Zoo / DWSNets: `AvivNavon/DWSNets` (Navon et al. 2023)

**Note:** Official NFT implementation codebase was already analyzed and adapted in H-E1/H-M1. H-M2 reuses these implementations directly.

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M2 is a continuation experiment — checkpoints and codebase already exist from H-M1.**

- **Priority 1 (HIGHEST):** H-M1 trained checkpoints (`h-m1/code/checkpoints/flat-MLPplusaug_seed*.pt`, `flat-MLPpluscanon_seed*.pt`, `NFT-base_seed*.pt`) — ground truth for controlled comparison
- **Priority 2:** H-M1 source code (`h-m1/code/src/`) — already implements all 3 encoder classes, evaluation framework
- **Priority 3:** Zhou et al. 2023 NFT reference (already integrated in H-M1)

**Recommended Implementation Path:**
- Primary: Load H-M1 checkpoints via `build_encoder()` + `evaluate_all_encoders()` framework
- Fallback: Retrain if checkpoint loading fails (same config as H-M1)
- Justification: Controlled experiment requires identical training to H-M1; checkpoints guarantee this. Only new code needed: SHOULD_WORK gate evaluator and H-M2-specific visualizations.

### Code Analysis (Serena MCP)

**Applied:** Serena semantic analysis of H-M1 codebase (`h-m1/code/src/`)

**Classes analyzed (from `models.py`):**
- `FlatMLPAugEncoder` (lines 193–223): Training-time augmentation via `apply_random_permutation_flat(x, severity=1.0, prob=AUG_APPLY_PROB)`. Kaiming uniform init. Forward: augment → net → head.
- `FlatMLPCanonEncoder` (lines 230–258): L2 normalization canonicalization via `l2_normalize_weights(x)` at both train+eval. Same architecture. Forward: canonicalize → net → head.
- `NFTEquivariantEncoder`: Equivariant attention on neuron-level representations. Permutation-invariant by construction.
- `OracleCanonEncoder`: Oracle-level canonicalization (perfect sorting). In H-M1, achieved ~0.0 Δρ.

**Functions analyzed (from `evaluate.py`):**
- `evaluate_all_encoders()` (lines 137–229): Evaluates all encoders across 6×3×4 = 72 condition combinations. Computes Δρ = ρ(s=0) - ρ(s=1.0) with paired bootstrap (n=10,000 samples). Returns DataFrame with columns [encoder, seed, severity, rho, delta_rho, ci_lower, ci_upper, p_value].
- `evaluate_gate_condition_v2()` (lines 319–406): Already computes `ranking_correct = (oracle ≤ nft ≤ aug ≤ flat-MLP)` as a boolean indicator. Reports per-encoder mean Δρ at s=1.0. **Key insight:** The H-M2 SHOULD_WORK gate is already partially implemented in H-M1's gate evaluator — H-M2 adds a dedicated SHOULD_WORK gate function.

**Serena Analysis Needed for H-M2:** Minimal. All encoder classes and evaluation logic reusable. Only new code needed: `evaluate_gate_condition_hm2()` function and H-M2-specific visualizations.

---

## Experiment Specification

### Dataset

**Name:** Unterthiner FC-MLP Zoo (MNIST subset)
**Type:** standard (real, established dataset — NOT synthetic ✅)
**Source:** Unterthiner et al. 2020 "Predicting Neural Network Accuracy from Weights"
**Splits:**
- Train: ~800 FC-MLP models (2-4 layer, MNIST)
- Test: ~200 FC-MLP models (held-out split)
- Total: ~1,000 models (statistically sufficient: >> 500 minimum)

**Preprocessing:**
- Each model's weight vector: flattened concatenation of all layer weights + biases
- L2 normalization applied per-encoder (FlatMLPCanonEncoder handles this internally)
- Target: generalization gap = (train_accuracy - test_accuracy)
- Loaded as enriched pickle: `zoo_enriched.pkl` (includes pre-computed permutation matrices)

**Augmentation (encoder-specific):**
- flat-MLP baseline: No augmentation
- flat-MLP+aug: Random neuron permutation at training time (p=0.5, severity=1.0)
- flat-MLP+canon: L2 normalization canonicalization (pre-processing, no augmentation)
- NFT-base: No augmentation needed (equivariant by architecture)

**Status:** ✅ CACHED — Dataset available at `.data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl`

**Loading Information** (for Phase 4 download):
- Method: custom (pickle load from cache)
- Identifier: `.data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl`
- Code:
```python
import pickle
with open(cache_path, 'rb') as f:
    zoo_data = pickle.load(f)
# zoo_data: dict with 'weights' (list of flat weight vectors), 'gen_gap' (targets),
# 'layer_fan_ins' (for NFT input format)
```

### Models

#### Baseline Model

**Architecture:** flat-MLP encoder (FlatMLPEncoder)
- 3-layer MLP: Linear(D→512) → ReLU → Linear(512→512) → ReLU → Linear(512→512) → ReLU → head(512→1)
- D = flattened weight dimension of FC-MLP zoo models
- Kaiming uniform initialization

**Configuration:**
- Input: (B, D) flattened weight vectors
- Output: (B, 1) generalization gap prediction
- Parameters: ~786K (D×512 + 512×512×2 + 512×1)

**Checkpoint:** `h-m1/code/checkpoints/flat-MLP_seed{42,123,456}.pt`

**Loading Information** (for Phase 4 download):
- Method: custom (load from H-M1 checkpoints)
- Identifier: `h-m1/code/checkpoints/flat-MLP_seed{seed}.pt`
- Code:
```python
from h_m1_src.models import build_encoder
model = build_encoder('flat-MLP', flat_input_dim, layer_fan_ins)
checkpoint = torch.load(ckpt_path, map_location=device)
model.load_state_dict(checkpoint['model_state_dict'])
```

#### Proposed Model

**Architecture:** 3-way comparison across compensation strategies + architectural solution

**Core Mechanism Implementation:**

```python
# H-M2 Core Comparison: Engineering Compensations vs. Architectural Equivariance
# Based on: H-M1 Serena-analyzed codebase (h-m1/code/src/models.py lines 193-258)
# Sources: Zhou et al. 2023 (NFT), H-M1 validated implementation

class FlatMLPAugEncoder(nn.Module):
    """E2: Flat-MLP + random permutation augmentation at train time."""
    def forward(self, x: Tensor) -> Tensor:
        if self.training:
            # Permutation augmentation: randomly shuffle neuron ordering
            x = apply_random_permutation_flat(x, severity=1.0, prob=AUG_APPLY_PROB)
        return self.head(self.net(x))  # (B, D) → (B, 1)

class FlatMLPCanonEncoder(nn.Module):
    """E3: Flat-MLP + L2-norm canonicalization pre-processing (oracle approximation)."""
    def forward(self, x: Tensor) -> Tensor:
        # Canonicalize: normalize each weight vector to unit L2 norm (train+eval)
        x = l2_normalize_weights(x)  # (B, D) → (B, D), ||x_i||_2 = 1
        return self.head(self.net(x))  # (B, D) → (B, 1)

class NFTEquivariantEncoder(nn.Module):
    """E4: NFT — equivariant attention on neuron-level representations."""
    # Layer-wise inputs: list of (B, L_i, fan_in_i) tensors
    # Equivariant attention: attention(Q, K, V) with permutation-invariant pooling
    def forward(self, layers: list[Tensor]) -> Tensor:
        # Equivariant attention per layer → global aggregation → head
        hidden = self.nft_encoder(layers)   # permutation-equivariant
        return self.head(hidden.mean(dim=1)) # (B, 1)

# H-M2 Gate Evaluation (SHOULD_WORK)
def evaluate_gate_hm2(eval_df: pd.DataFrame) -> dict:
    s1 = eval_df[eval_df['severity'] == 1.0]
    mean_dr = {enc: s1[s1['encoder']==enc]['delta_rho'].mean()
               for enc in ['flat-MLP','flat-MLP+aug','flat-MLP+canon','NFT-base']}
    # SHOULD_WORK: aug/canon < flat-MLP but > NFT-base
    return {
        'aug_partial': mean_dr['flat-MLP+aug'] > 0.05,    # not fully compensated
        'canon_partial': mean_dr['flat-MLP+canon'] > 0.03, # oracle still suboptimal
        'nft_superior': mean_dr['NFT-base'] < 0.02,        # architecture wins
        'ranking': mean_dr['NFT-base'] < mean_dr['flat-MLP+canon'] <
                   mean_dr['flat-MLP+aug'] < mean_dr['flat-MLP'],
        'passed': all([...])  # SHOULD_WORK: all conditions met
    }
```

### Training Protocol

**Reusing H-M1 proven training configuration (continuation experiment).**

**Optimizer:** Adam
- lr = 1e-3
- weight_decay = 1e-4
- betas = (0.9, 0.999)
- **Source:** H-M1 optimal config (03_config.md), proven across 18 training runs

**Learning Rate Schedule:** StepLR
- step_size = 20 epochs
- gamma = 0.5
- **Source:** H-M1 03_config.md

**Batch Size:** 64
- **Source:** H-M1 validated (stable training across all 6 encoder types)

**Epochs:** 50
- **Source:** H-M1 converged at ~40 epochs; 50 provides safety margin

**Loss Function:** MSELoss (regression — generalization gap prediction)
- **Source:** Standard for regression on zoo property prediction (Unterthiner 2020)

**Seeds:** {42, 123, 456} (3 seeds for mean Δρ stability)
- **Source:** H-M1 used same 3 seeds; reuse enables direct cross-hypothesis comparison

**Key difference from H-M1:** H-M2 focuses on 3 encoders (flat-MLP+aug, flat-MLP+canon, NFT-base) not all 6. Checkpoints already trained in H-M1 — reuse directly; retrain only if checkpoint loading fails.

**Permutation Stress Protocol:**
- Severity levels: s ∈ {0.0, 0.25, 0.5, 1.0}
- Bootstrap: n=10,000, Holm correction, α=0.05
- Minimum models per condition: 500 (full MNIST zoo split)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Threshold |
|--------|-----------|-----------|
| Δρ (flat-MLP+aug, s=1.0) | ρ(s=0) - ρ(s=1.0) for augmented encoder | > 0.05 (partial compensation) |
| Δρ (flat-MLP+canon, s=1.0) | ρ(s=0) - ρ(s=1.0) for canonicalized encoder | > 0.03 (oracle ceiling) |
| Δρ (NFT-base, s=1.0) | ρ(s=0) - ρ(s=1.0) for NFT encoder | < 0.02 (architectural robustness) |
| Three-way ranking | NFT-base < canon < aug < flat-MLP | All hold simultaneously |
| Bootstrap p-value | flat-MLP+aug vs NFT-base (paired, Holm) | p < 0.05 |

**Success Criteria (SHOULD_WORK):**
1. flat-MLP+aug: 0.05 < Δρ < flat-MLP Δρ (partial reduction, not full compensation)
2. flat-MLP+canon: 0.03 < Δρ < flat-MLP+aug Δρ (oracle better than aug, still < NFT)
3. NFT-base: Δρ < 0.02 (architectural equivariance dominates)
4. Strict three-way ranking: NFT < canon < aug < flat-MLP

**Expected Baseline Performance (from H-M1 validated results):**
- flat-MLP Δρ: ~0.64 (strong baseline degradation)
- flat-MLP+aug Δρ: ~0.22 (partial compensation, > 0.05 threshold)
- NFT-base Δρ: ~4.7e-7 (near-zero, confirmed)
- flat-MLP+canon Δρ: ~0.0 in H-M1 (L2 oracle; real oracle constraint → expect 0.03–0.15)

**Note on oracle-canon:** H-M1's OracleCanonEncoder used perfect L2 normalization achieving Δρ≈0. H-M2 must evaluate whether this "oracle" is a realistic upper bound or a degenerate solution. The hypothesis expects Δρ > 0.03 for any realistic canonicalization — H-M2 tests this directly.

**Statistical Tests:**
- Paired bootstrap (n=10,000): flat-MLP+aug vs NFT-base
- Paired bootstrap (n=10,000): flat-MLP+canon vs NFT-base
- Holm-corrected multiple comparisons (α=0.05)
- Effect size: Cohen's d for each pairwise comparison

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression (generalization gap prediction)
- Library: `scipy.stats.spearmanr` (primary), `numpy` (bootstrap), `sklearn.metrics` (MSE)
- Code:
```python
from scipy.stats import spearmanr
rho, p_val = spearmanr(predictions, targets)
delta_rho = rho_s0 - rho_s1  # robustness measure
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of mean Δρ at s=1.0 for all 4 encoders (flat-MLP, flat-MLP+aug, flat-MLP+canon, NFT-base) with 95% CI error bars and threshold lines (0.05, 0.03, 0.02)

#### Additional Figures (LLM Autonomous)

Based on MECHANISM hypothesis testing engineering compensation strategies:

1. **Δρ Heatmap by Encoder × Severity:** 4-encoder × 4-severity grid showing Δρ values; highlights cliff behavior of flat-MLP vs. graceful NFT
2. **ρ(s) Degradation Curves:** Line plot of Spearman ρ vs. permutation severity for all 4 encoders (with seed-level error bands); shows compensation partially slows degradation
3. **Three-way Ranking Visualization:** Scatter plot of Δρ per seed (×3) for 3 comparison encoders + flat-MLP baseline with expected threshold zones
4. **Bootstrap Distribution Overlays:** Overlapping bootstrap Δρ distributions for aug vs. NFT-base and canon vs. NFT-base comparisons

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (loads H-M1 checkpoints, evaluates on zoo test split)
2. Three-way ranking confirmed: NFT-base Δρ < flat-MLP+canon Δρ < flat-MLP+aug Δρ < flat-MLP Δρ
3. NFT-base Δρ < 0.02 (reconfirmed from H-M1)
4. flat-MLP+aug Δρ > 0.05 (augmentation insufficient for full compensation)

**Mechanism Verification Protocol:**
- **Pre-condition:** H-M1 checkpoints loadable and produce H-M1 Δρ values within ±0.01 tolerance
- **Activation indicator:** `evaluate_gate_hm2()` `ranking` field = True
- **Architecture compatibility:** ✅ All 3 encoder classes exist in H-M1 codebase (Serena confirmed)
- **Failure detection:** If aug Δρ ≤ 0.05 OR canon Δρ ≤ 0.03 → SHOULD_WORK gate fails → narrow claim
- **Success threshold:** All 4 SHOULD_WORK conditions met simultaneously

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Summary:** No topically relevant results found in Archon KB (5 searches across 3 query types). The KB (source: 8b1c7f40739544a6) contains diffusion model / HuggingFace documentation only. Not a failure — this is a niche weight-space learning domain.

**Searches executed (with 402/no-match documentation):**
1. Query: "permutation augmentation equivariance NFT weight space" → No match (top result: HuggingFace Transformers quantization, sim=0.364)
2. Query: "canonicalization augmentation comparison architectural inductive bias" → No match (top: OpenAI instruction-following, sim=0.378)
3. Query: "model zoo property prediction encoder comparison" → No match (top: ControlNet discussion, sim=0.501)
4. Code query: "permutation augmentation PyTorch weight space encoder" → No match (top: token gradient zeroing, rerank=-9.0)
5. Code query: "NFT Neural Functional Transformer encoder comparison" → No match (top: 4-bit quantization, rerank=-7.2)

### B. GitHub Implementations (Exa)

**Exa MCP Status:** Unavailable (402 Payment Required) — same as H-E1 and H-M1 Phase 2C executions.

**Known repositories (literature-grounded, not Exa-searched):**

| Repository | Relevance | Used For |
|-----------|-----------|---------|
| `AllanYangZhou/nfn` | NFT official implementation (Zhou et al. 2023) | NFTEquivariantEncoder basis |
| `google-research/dnn_predict_accuracy` | Unterthiner 2020 zoo + flat-MLP baseline | Dataset + FlatMLPEncoder basis |
| `AvivNavon/DWSNets` | Deep Weight Space equivariant architectures | Comparison context |

### C. Code Analysis (Serena)

**Serena MCP Status:** ✅ Available. Project `TEST_wsl` activated.

**Files analyzed:**
- `docs/youra_research/20260316_wsl/h-m1/code/src/models.py`
- `docs/youra_research/20260316_wsl/h-m1/code/src/evaluate.py`

**Key findings:**

**models.py:**

| Class | Lines | Purpose | H-M2 Relevance |
|-------|-------|---------|----------------|
| `FlatMLPAugEncoder` | 193–223 | Flat-MLP + train-time permutation aug | Direct: tests aug compensation |
| `FlatMLPCanonEncoder` | 230–258 | Flat-MLP + L2-norm canonicalization | Direct: tests canon compensation |
| `NFTEquivariantEncoder` | ~259+ | NFT with equivariant attention | Direct: architectural baseline |
| `OracleCanonEncoder` | ~259+ | Perfect sort canonicalization | Reference: upper bound for canon |

**evaluate.py:**

| Function | Lines | Purpose | H-M2 Relevance |
|----------|-------|---------|----------------|
| `evaluate_all_encoders` | 137–229 | Evaluate 6×3×4 conditions, compute Δρ | Reuse directly |
| `evaluate_gate_condition_v2` | 319–406 | H-M1 MUST_WORK gate + `ranking_correct` | Adapt for H-M2 SHOULD_WORK gate |

**Original `FlatMLPAugEncoder.forward` (analyzed):**
```python
def forward(self, x: Tensor) -> Tensor:
    if self.training:
        x = apply_random_permutation_flat(x, severity=self.aug_severity, prob=AUG_APPLY_PROB)
    return self.head(self.net(x))
```

**Original `FlatMLPCanonEncoder.forward` (analyzed):**
```python
def forward(self, x: Tensor) -> Tensor:
    x = l2_normalize_weights(x)
    return self.head(self.net(x))
```

**Original `evaluate_gate_condition_v2` ranking_correct indicator (analyzed):**
```python
ranking_correct = (
    oracle_mean_dr <= nft_base_mean_dr
    and nft_base_mean_dr <= flat_aug_mean_dr
    and flat_aug_mean_dr <= flat_mlp_mean_dr
)
```

**Checkpoints confirmed (Serena `list_dir`):**
```
flat-MLPplusaug_seed{42,123,456}.pt   ✅
flat-MLPpluscanon_seed{42,123,456}.pt ✅
NFT-base_seed{42,123,456}.pt          ✅
Oracle-canon_seed{42,123,456}.pt      ✅
flat-MLP_seed{42,123,456}.pt          ✅
```

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M1

**File:** `h-m1/04_validation.md`

**Reused Components:**
- Dataset: Unterthiner MNIST zoo (cached at `.data_cache/`) — proven stable, ~1,000 models
- Training checkpoints: All 6 encoder × 3 seeds (H-M1 `checkpoints/`) — consistent, reproducible
- Hyperparameters: Adam lr=1e-3, batch=64, epochs=50, StepLR (20, 0.5) — optimal in H-M1
- Evaluation framework: `evaluate_all_encoders()` + bootstrap protocol — 94/94 tests passing
- H-M2 focal encoders: flat-MLP+aug (Δρ=0.2239), flat-MLP+canon (Δρ≈0), NFT-base (Δρ=4.71e-07)

**Why Reused:** Continuation experiment requires identical training conditions — only the gate evaluator and analysis scope differ. Reusing checkpoints ensures fair apples-to-apples comparison.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|-----------------|
| Dataset selection | Phase 2B / H-M1 continuation | Unterthiner MNIST zoo (H-M1 proven) |
| Dataset cache path | Serena list_dir | `.data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl` |
| FlatMLPAugEncoder architecture | Serena analysis | `models.py` lines 193–223 |
| FlatMLPCanonEncoder architecture | Serena analysis | `models.py` lines 230–258 |
| NFTEquivariantEncoder | Zhou et al. 2023 / H-M1 | `models.py` NFT class + h-m1/04_validation.md |
| Checkpoint availability | Serena list_dir | `h-m1/code/checkpoints/` (18 files confirmed) |
| Evaluation framework | Serena analysis | `evaluate.py` lines 137–229 |
| Gate structure (ranking_correct) | Serena analysis | `evaluate.py` lines 319–406 |
| Training hyperparameters | Phase 4 H-M1 | h-m1/03_config.md + 04_validation.md |
| Success thresholds (aug >0.05, canon >0.03, NFT <0.02) | Phase 2B | 02b_verification_plan.md H-M2 section |
| Bootstrap protocol | Phase 2B / H-M1 | n=10,000, Holm correction, α=0.05 |
| Pseudo-code | Serena analyzed code | models.py + evaluate.py H-M1 codebase |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-16T14:20:00+00:00

### Workflow History for This Hypothesis
- H-M1 COMPLETED (PASS) at 2026-03-16T13:52:00 — MUST_WORK gate satisfied
- H-M2 set IN_PROGRESS at 2026-03-16T13:57:38 — External loop triggered Phase 2C
- Phase 2C initiated for H-M2 at 2026-03-16T14:15:00

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (5 KB queries, no match — documented), Exa (3 queries, 402 — documented), Serena (✅ models.py + evaluate.py analyzed)*
*All specifications grounded in H-M1 Serena-analyzed implementation + Phase 2B criteria*
*Dataset: standard (Unterthiner MNIST zoo) — NOT synthetic ✅*
*Next Phase: Phase 3 - Implementation Planning*
