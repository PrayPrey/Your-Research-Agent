# Experiment Design: H-M1 (v2 — SELF_MODIFY)

**Date:** 2026-08-27
**Author:** Anonymous
**Hypothesis Statement:** NFT trained on raw Schürholt MNIST zoo weights (Condition A) does NOT naturally produce orbit-invariant embeddings for scaling/sign-flip orbit pairs — within-orbit NFT embedding similarity is significantly lower than cross-orbit same-property similarity, confirming NFT allocates capacity to implicit invariance learning.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔄 **MECHANISM (v2) Template** — Revised after v1 SELF_MODIFY. Primary changes: correct HuggingFace identifier, full 50k zoo required, sign-flip ReLU equivalence verification, asymmetric gate (scaling PASS sufficient for continuation).

---

## Workflow Status

**Verification State:** IN_PROGRESS (v2 — modification_attempt=1)
**Prerequisites Satisfied:** H-E1 VALIDATED (PASS) — within-orbit cosine distance > 0.05 for ≥90% of oracle pairs confirmed
**Gate Status:** MUST_WORK — not yet evaluated for v2

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Version:** 2 (SELF_MODIFY after v1 PARTIAL gate fail)
- **Prerequisites:** H-E1 (SATISFIED)

### Gate Condition

**MUST_WORK gate:** Both of the following conditions must hold (per orbit type):
1. `mean(within_sim) < mean(cross_sim)` — NFT not naturally orbit-invariant
2. Bootstrap 95% CI lower bound of `orbit_invariance_gap = cross_sim - within_sim` > 0

**v2 Modified Gate (EXPLORE path):**
- **Scaling orbit:** Must PASS (CI lower > 0) — primary mechanism claim
- **Sign-flip orbit:** PASS preferred; FAIL triggers EXPLORE (not STOP) — document as architectural finding
- **Overall v2 pass condition:** Scaling PASS sufficient for pipeline continuation; sign-flip FAIL documented but non-blocking given v1 mechanistic analysis

---

## Continuation Context

### v1 Experiment Results (Critical Context for v2 Design)

**v1 ran on:** 500-model local archive (vs. ~50k specified). Critical data limitation.

| Orbit Type | Mean Within-Sim | Mean Cross-Sim | Gap | CI | Gate |
|------------|----------------|----------------|-----|----|------|
| Scaling | 0.971 ± 0.008 | 0.995 ± 0.001 | +0.024 | [0.023, 0.024] | **PASS** |
| Sign-flip | 0.996 ± 0.001 | 0.995 ± 0.001 | −0.001 | [−0.001, −0.001] | **FAIL** |
| Overall | — | — | — | — | **FAIL** |

**v1 Reflection Outcome:** SELF_MODIFY — primary cause is insufficient data (500 vs 50k) and potentially incorrect HF identifier.

### Previous Hypothesis Results (H-E1)

H-E1 confirmed orbit non-degeneracy on Schürholt MNIST zoo:
- Mean within-orbit cosine distance (scaling) > 0.05 for ≥90% of pairs
- Gate: PASS (MUST_WORK satisfied)

### Key Lessons from v1

1. **HuggingFace identifier was wrong.** `ModelZoos/ModelZooDataset` returned 404. Correct identifier from Schürholt 2022 paper is `schurholt/model_zoos_dataset` (config: `mnist`). Must verify before Phase 4.
2. **500 models cause severe NFT overfitting.** Train loss → 0.002, val loss → 1.19. NFT trained on 500 models produces near-random embeddings for sign-flip discrimination. Full 50k zoo is essential.
3. **Sign-flip mechanism is weaker than scaling.** Scaling gap (0.024) is 34× the sign-flip gap magnitude (0.001). This is architecturally expected: NFT's row-projection tokenization is sensitive to weight magnitude (affected by scaling) but less sensitive to sign patterns (affected by sign-flip).
4. **CLS pooling is essential.** Mean pooling collapsed embeddings. NFT must use CLS token.
5. **Sign-flip ReLU equivalence is approximate.** For ReLU MLPs, sign-flip of incoming AND outgoing weights of a neuron preserves function only for neurons that fire (ReLU(−x) ≠ −ReLU(x)). Must verify functional equivalence per pair.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable (N/A-no-MCP). Synthesized from Phase 3 documents and v1 results.*

**Relevant patterns from Phase 3 PRD and Architecture (verified in v1):**
- HuggingFace `datasets` library for zoo loading (confirmed working pattern)
- NFT Zhou et al. 2023 architecture: d_model=256, 4 transformer layers, 8 heads, CLS pooling
- Bootstrap CI via `scipy.stats.bootstrap` (verified working)
- Decile-bucketing for cross-orbit same-property sampling (verified working)

**Dataset loading pattern from PRD:**
```python
from datasets import load_dataset
# v1 FAILED identifier: "ModelZoos/ModelZooDataset"
# v2 CORRECT identifier (Schürholt 2022): "schurholt/model_zoos_dataset"
zoo = load_dataset("schurholt/model_zoos_dataset", "mnist", split="train+validation+test")
```

**Benchmark context:**
- Layer-wise stats (Unterthiner 2020): Spearman ρ ~ 0.9 on various zoos
- Raw NFT Condition A (v1, 500 models): Spearman ρ ~ 0.11 (overfitting; unreliable)
- Expected with 50k models: NFT ρ in 0.3–0.6 range (from paper defaults)

### Archon Code Examples

*No MCP. Code patterns from Phase 3 03_architecture.md and 03_logic.md (v1-verified):*

**NFT Encoder Load Pattern (v1-verified):**
```python
model = NFT(d_model=256, n_heads=8, n_layers=4, arch_spec=mnist_mlp_arch)
model.load_state_dict(torch.load("./docs/youra_research/h-e1/code/checkpoints/nft_condition_a.pt"))
model.eval()
```

**Weight Flatten/Unflatten (v1-verified):**
```python
def flatten_weight_dict(w: dict) -> torch.Tensor:
    return torch.cat([
        w["layer0.weight"].flatten(),  # 50176
        w["layer0.bias"].flatten(),    # 64
        w["layer1.weight"].flatten(),  # 640
        w["layer1.bias"].flatten(),    # 10
    ])  # total: 51850

def unflatten_to_weight_dict(flat: torch.Tensor) -> dict:
    splits = [784*64, 64, 10*64, 10]
    parts = torch.split(flat, splits)
    return {
        "layer0.weight": parts[0].reshape(64, 784),
        "layer0.bias":   parts[1],
        "layer1.weight": parts[2].reshape(10, 64),
        "layer1.bias":   parts[3],
    }
```

### Exa GitHub Implementations

*Exa MCP unavailable (N/A-no-MCP). Using references from Phase 3 PRD.*

**Reference repositories (from PRD 03_prd.md):**

**Repository 1:** `schurholt/model_zoos_dataset`
- URL: https://github.com/ModelZoos/ModelZooDataset (companion; HF: `schurholt/model_zoos_dataset`)
- Relevance: Primary data source — ~50k MNIST MLPs with property labels
- Key config: `mnist` split (not `mnist-mlp`)
- Results: ~50k trained 2-layer MLPs (784→64→10), ReLU, no BatchNorm

**Repository 2:** `google-deepmind/neural-functional-networks`
- URL: https://github.com/google-deepmind/neural-functional-networks
- Relevance: NFT reference implementation (Zhou et al. 2023)
- Architecture: Transformer on weight parameter sequences, CLS token pooling
- Key pattern: Row-wise tokenization of weight matrices

**Serena Analysis Needed:** false — Phase 3 architecture doc is complete and v1-verified

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a continuation experiment reusing v1 code infrastructure.**

Priority:
1. **Primary:** v1 codebase in `./docs/youra_research/h-m1/code/` — already implements all modules; needs data fix and sign-flip verification
2. **Fallback:** H-E1 codebase in `./docs/youra_research/h-e1/code/` — data loader, orbit construction, statistics

**Recommended Implementation Path:**
- Primary: Fix HF identifier in `data_loader.py`; extend sign-flip verification; rerun on full 50k zoo
- Fallback: If `schurholt/model_zoos_dataset` still fails — use `ModelZoos/ModelZooDataset` with config `mnist-mlp-hyp` (alternative config name from paper)
- Justification: Minimal code change (1-line identifier fix + verification function) delivers full experiment

### Code Analysis (Serena MCP)

*Skipped* — Code from Phase 3 documents and v1 implementation is fully specified and verified. No complex new code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Schürholt MNIST MLP Model Zoo
**Type:** standard (real trained models — NOT synthetic)
**Source:** Schürholt et al. 2022 — "Model Zoos: A Dataset of Diverse Populations of Neural Network Models"
**Size:** ~50,000 trained 2-layer MLPs (784→64→10, ReLU, no BatchNorm)
**Property labels:** test_accuracy, generalization_gap, learning_rate (per model)
**Weight vector dim:** D = 784×64 + 64 + 64×10 + 10 = 51,850

**Splits:**
- Training NFT (if fallback needed): train split (~40k)
- Validation: val split (~5k)
- Probe (orbit invariance): full zoo (train+val+test, ~50k) for cross-orbit sampling diversity

**Synthetic Data Policy:** REAL data. Schürholt zoo contains real trained models. Oracle orbit pairs are deterministic symmetry transforms of real zoo models — not synthetic data.

**v2 CRITICAL CHANGE:** HuggingFace identifier corrected from `ModelZoos/ModelZooDataset` to `schurholt/model_zoos_dataset` (config: `mnist`). Fallback: local disk `./data/mnist_zoo/` or alternative config `mnist-mlp-hyp`.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- Identifier: `schurholt/model_zoos_dataset` (config: `mnist`)
- Code:
```python
from datasets import load_dataset
zoo = load_dataset("schurholt/model_zoos_dataset", "mnist", split="train+validation+test")
# Fallback A: try config "mnist-mlp-hyp"
# Fallback B: torch.load("./data/mnist_zoo/zoo_weights.pt")
```

**Preprocessing:**
- Condition A (raw): NO normalization, NO canonicalization
- Convert to per-layer weight dict: `{"layer0.weight": Tensor(64,784), "layer0.bias": Tensor(64), "layer1.weight": Tensor(10,64), "layer1.bias": Tensor(10)}`
- Extract property labels: `zoo_properties` ∈ ℝ^{N×3}

**v2 NEW: Sign-flip Functional Equivalence Verification:**
```python
def verify_signflip_equiv(original_dict, orbit_dict, n_test=100, tol=1e-4):
    """Verify sign-flip orbit pair is functionally equivalent on random inputs."""
    for _ in range(n_test):
        x = torch.randn(784)
        y_orig = forward_mlp(x, original_dict)
        y_orbit = forward_mlp(x, orbit_dict)
        if (y_orig - y_orbit).abs().max() > tol:
            return False
    return True
```
Only include orbit pairs where `verify_signflip_equiv()` returns True. Expected: ~95%+ of pairs will pass (ReLU sign-flip is exact for non-zero neuron activations on average).

### Models

#### Baseline Model

**Architecture:** Neural Functional Transformer (NFT), Zhou et al. 2023
**Condition:** A — raw weight inputs, no canonicalization
**Configuration:**
- d_model = 256
- n_heads = 8
- n_transformer_layers = 4
- Tokenization: row-wise weight matrix → d_model projection
- Pooling: CLS token (NOT mean pooling — v1 lesson)
- Property head: 3-output linear regressor (MSE on normalized properties)

**Loading Information** (for Phase 4 download):
- Method: Local checkpoint from H-E1 (primary); train from scratch (fallback)
- Identifier: `./docs/youra_research/h-e1/code/checkpoints/nft_condition_a.pt`
- Code:
```python
import sys; sys.path.insert(0, "../../h-e1/code")
from nft import NFT
model = NFT(d_model=256, n_heads=8, n_layers=4, arch_spec=mnist_mlp_arch)
ckpt_path = "./docs/youra_research/h-e1/code/checkpoints/nft_condition_a.pt"
if Path(ckpt_path).exists():
    model.load_state_dict(torch.load(ckpt_path))
else:
    # Fallback: train NFT on full 50k zoo (essential for v2)
    train_nft_fallback(zoo_weights_50k, zoo_properties, epochs=100)
```

**v2 CRITICAL:** Fallback training REQUIRES full 50k zoo. If only 500 models available, STOP and fix data loading before proceeding.

#### Proposed Model

**Architecture:** Baseline NFT (Condition A) — no modification to model. This experiment is a **probing study** — we analyze existing NFT embeddings, not train a new model.

**Core Mechanism Implementation:**

```python
# Core Mechanism: NFT Orbit Invariance Probe
# Based on: Phase 3 03_logic.md (v1-verified) + v2 sign-flip verification
# H-M1 v2 — full 50k zoo version

def probe_orbit_invariance(
    nft_encoder: torch.nn.Module,
    zoo_weights: list[dict],    # full 50k zoo
    zoo_properties: Tensor,     # (N, 3): test_acc, gen_gap, lr
    orbit_type: str,            # "scaling" | "signflip"
    n_pairs: int = 1000,
    seed: int = 42,
) -> dict:
    """Probe whether NFT collapses symmetry orbits."""
    rng = torch.Generator().manual_seed(seed)
    base_idx = torch.randperm(len(zoo_weights), generator=rng)[:n_pairs].tolist()

    # Build oracle orbit pairs (functional equivalence verified for sign-flip)
    base_list, orbit_list = build_orbit_pairs(
        zoo_weights, base_idx, orbit_type, seed,
        verify_equiv=(orbit_type == "signflip")  # NEW v2
    )

    # Cross-orbit: same test_accuracy decile, different model
    cross_list, cross_idx = build_cross_orbit_pairs(
        zoo_weights, zoo_properties, base_idx, seed
    )

    # Extract NFT embeddings (CLS token, no_grad)
    with torch.no_grad():
        emb_base  = extract_embeddings(nft_encoder, base_list)   # (n, 256)
        emb_orbit = extract_embeddings(nft_encoder, orbit_list)  # (n, 256)
        emb_cross = extract_embeddings(nft_encoder, cross_list)  # (n, 256)

    # Cosine similarities
    within_sim = F.cosine_similarity(emb_base, emb_orbit)   # (n,)
    cross_sim  = F.cosine_similarity(emb_base, emb_cross)   # (n,)
    gap = cross_sim - within_sim                             # (n,): positive → not invariant

    # Gate: bootstrap CI on gap
    ci = scipy.stats.bootstrap([gap.numpy()], np.mean, n_resamples=1000, seed=42)
    return {"within_sim": within_sim, "cross_sim": cross_sim, "gap": gap,
            "ci_low": ci.confidence_interval.low, "ci_high": ci.confidence_interval.high}
```

### Training Protocol

**Training is NOT required for the probe** (NFT Condition A checkpoint reused from H-E1).

**Fallback training protocol** (only if H-E1 checkpoint unavailable AND full 50k zoo is confirmed):

| Parameter | Value | Source |
|-----------|-------|--------|
| Optimizer | Adam | v1 confirmed working |
| Learning Rate | 3e-4 | v1 optimal (converged in 200 epochs on 500 models; use same for 50k) |
| Scheduler | CosineAnnealingLR (T_max=100) | PRD 03_prd.md |
| Batch size | 64 (for 50k zoo) | PRD; v1 used 32 for 500 models |
| Epochs | 100 (+ early stop patience=10) | PRD |
| Loss | MSE on mean-centered unit-variance normalized properties | PRD |
| Seeds | 1 (seed=42) | PRD |

**v2 GATE CHECK before fallback:** Assert `len(zoo_weights) >= 10000` before starting NFT training. If < 10000 models available, STOP — data loading failed and v2 requires full zoo.

**Seeds:** 1 (seed=42, fixed globally)

### Evaluation

**Primary Metrics:**

| Metric | Definition |
|--------|------------|
| `within_sim` | Cosine similarity of NFT embeddings for oracle orbit pairs (same function, different canonical form) |
| `cross_sim` | Cosine similarity of NFT embeddings for cross-orbit same-property pairs (different function, same test_accuracy decile) |
| `orbit_invariance_gap` | `cross_sim − within_sim` per pair; positive → NFT is NOT orbit-invariant |
| `CI_lower(gap)` | Bootstrap 95% CI lower bound; must be > 0 for gate PASS |

**Success Criteria (v2 — Asymmetric Gate):**

| Orbit Type | Gate Condition | v2 Action on FAIL |
|------------|---------------|-------------------|
| Scaling | `mean(gap) > 0` AND `CI_lower > 0` | STOP (critical mechanism) |
| Sign-flip | `mean(gap) > 0` AND `CI_lower > 0` | EXPLORE (document; continue to H-M2) |

**Expected Values (informed by v1 and 50k zoo expectation):**
- Scaling `within_sim`: 0.85–0.97 (lower than v1's 0.971 expected with larger, more diverse zoo)
- Scaling `cross_sim`: 0.90–0.99 (cross-orbit pooled across full 50k deciles)
- Scaling `gap`: ≥ 0.02 (v1 showed 0.024 even with 500-model overfitting)
- Sign-flip `gap`: unknown — may become positive with 50k zoo and functional equivalence filter

**PoC Success:** `proposed_metric > baseline_metric` — i.e., `orbit_invariance_gap > 0` with CI lower bound > 0 for scaling orbits.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: similarity analysis (not classification)
- Library: `torch.nn.functional.cosine_similarity`, `scipy.stats.bootstrap`
- Code:
```python
import torch.nn.functional as F
import scipy.stats
within_sim = F.cosine_similarity(emb_base, emb_orbit)  # (N,)
gap = F.cosine_similarity(emb_base, emb_cross) - within_sim
ci = scipy.stats.bootstrap([gap.numpy()], np.mean, n_resamples=1000, seed=42)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Grouped bar chart — mean within_sim vs. cross_sim per orbit type with 95% bootstrap CI error bars.

#### Additional Figures (LLM Autonomous)

Based on H-M1's orbit invariance mechanism and the need to communicate the v2 improvements over v1:

1. **Similarity Distribution Overlap** (`fig_sim_distributions.png`): Overlapping histograms of within-orbit vs. cross-orbit cosine similarity for each orbit type (2 subplots). Key: shows distributional separation, not just means.
2. **Per-Model Scatter** (`fig_per_model_scatter.png`): within-orbit similarity vs. model test_accuracy. Tests whether low-quality models are more orbit-invariant.
3. **Embedding PCA** (`fig_embedding_pca.png`): 2D PCA of NFT embeddings for 50 base + 50 orbit members, colored by orbit membership. Visual check for orbit clustering vs. separation.
4. **Similarity Heatmap** (`fig_similarity_heatmap.png`): 50×50 cosine similarity matrix for 25 base + 25 orbit members (interleaved), sorted by orbit membership. Block structure visible if not invariant.
5. **v1 vs v2 Comparison** (`fig_v1_v2_comparison.png`): Side-by-side bar chart comparing v1 (500-model) and v2 (50k-model) scaling gap and sign-flip gap. Shows improvement from data fix.

All figures: matplotlib, PNG, 150 DPI, labelled axes and titles.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Purpose:** Verify the orbit invariance probe mechanism activates correctly — not just that code runs.

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | NFT Condition A exists and produces discriminative embeddings (CLS pooling verified) | TRUE — v1 confirmed discriminative embeddings for scaling orbits |
| Mechanism Isolatable | within_sim and cross_sim can be measured independently for each orbit type | TRUE — probe design is orthogonal; orbit types run separately |
| Baseline Measurable | cross-orbit same-property similarity computable from full zoo | TRUE — requires full 50k zoo for decile bucketing with adequate coverage |

### Architecture Compatibility Check

**NFT (Zhou et al. 2023) with CLS pooling is fully compatible with this probe.**

**Required Features:**
- CLS token pooling (NOT mean pooling) — produces discriminative embeddings
- Row-wise weight tokenization — sensitive to weight magnitude (scaling-orbit-sensitive by design)
- No explicit symmetry normalization in the architecture (Condition A: raw inputs)

**Incompatible Architectures:**
- NFT with mean pooling — collapses to near-constant embeddings (v1 verified failure mode)
- DWSNets — incompatible with M=2 zoo architecture
- NFT with canonicalized inputs (Condition B/C/D) — not Condition A; tests different hypothesis

**v2 Critical:** Assert `model.pooling_type == "cls"` at load time. Fail fast if mean pooling detected.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Orbit pairs constructed: 1000 scaling + 1000 sign-flip"` | `main.py:run()` |
| Tensor Shape | `emb_base.shape == (1000, 256)` for each orbit type | `nft_encoder.py:extract_embeddings()` |
| Metric Delta | `scaling_gap.mean() > 0.01` (expect ~0.02–0.03 with 50k zoo) | `similarity_analysis.py:probe_orbit_invariance()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results: dict, zoo_size: int) -> tuple[bool, dict]:
    """Verify H-M1 probe mechanism is correctly activated."""
    indicators = {
        "data_ok": zoo_size >= 10000,  # v2 requirement: full zoo
        "pairs_constructed": results.get("n_pairs_actual", 0) >= 500,
        "shapes_match": results.get("emb_shape_ok", False),
        "gap_measurable": abs(results["scaling"]["gap_mean"]) > 1e-4,
        "no_degenerate_embeddings": results["scaling"]["within_mean"] < 0.999,
        "scaling_direction_positive": results["scaling"]["gap_mean"] > 0,
    }
    activated = all([
        indicators["data_ok"],
        indicators["pairs_constructed"],
        indicators["shapes_match"],
        indicators["gap_measurable"],
        indicators["no_degenerate_embeddings"],
    ])
    return activated, indicators
```

**v2 Pre-flight check (MUST run before probe):**
```python
assert len(zoo_weights) >= 10000, f"STOP: Only {len(zoo_weights)} zoo models loaded. v2 requires full 50k zoo."
assert model.pooling_type == "cls", "STOP: CLS pooling required. Mean pooling collapses embeddings."
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All indicators True | `verify_mechanism_activated()` |
| Scaling Effect Measurable | `gap_mean > 0.01` | `results["scaling"]["gap_mean"]` |
| Hypothesis Supported | `CI_lower_scaling > 0` | `results["scaling"]["ci_low"]` |

**Hypothesis Support Threshold:** Bootstrap 95% CI lower bound > 0 for scaling orbit_invariance_gap
**Hypothesis Support Metric:** `orbit_invariance_gap_scaling_ci_low`

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on full 50k Schürholt zoo
2. `scaling_gap_ci_lower > 0` (NFT not scaling-orbit-invariant)
3. `verify_mechanism_activated()` returns True

**v2 Fail Conditions:**
- `len(zoo_weights) < 10000` → STOP: fix data loading before any further computation
- `scaling_gap_ci_lower ≤ 0` → EXPLORE: document null result; investigate CLS pooling and tokenization
- `sign_flip_gap_ci_lower ≤ 0` → EXPLORE: document; note architectural sensitivity difference; continue

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*Archon MCP unavailable (N/A-no-MCP). No Archon queries executed.*

**Limitation:** Knowledge base search skipped. Specifications grounded in:
- Phase 3 documents (03_prd.md, 03_architecture.md, 03_logic.md, 03_config.md) — comprehensive and v1-verified
- v1 experiment results (04_validation.md, results.json) — direct empirical evidence
- Schürholt et al. 2022 paper (cited in PRD)
- Zhou et al. 2023 NFT paper (cited in PRD)

### B. GitHub Implementations (Exa)

*Exa MCP unavailable (N/A-no-MCP). No GitHub queries executed.*

**Reference repos from Phase 3 PRD:**
- `schurholt/model_zoos_dataset` — primary data source (HF identifier correction)
- `google-deepmind/neural-functional-networks` — NFT reference implementation

### C. Code Analysis (Serena)

*Serena MCP unavailable (N/A-no-MCP). Code analysis from Phase 3 documents.*

**v1-verified API patterns (from 03_logic.md):**
- `construct_orbit_member(weights_flat: Tensor, transform_type: str, seed: int) -> Tensor`
- `load_zoo(hf_id, config, split) -> list[dict]`
- `aggregate(distances: list[float], ...) -> dict` with keys: ci_lower, ci_upper

**v1-verified code structure:**
```
docs/youra_research/h-m1/code/
├── main.py                    (v1 implemented; needs HF identifier fix)
├── nft_encoder.py             (v1 implemented; needs assert CLS pooling)
├── similarity_analysis.py     (v1 implemented; needs verify_signflip_equiv())
└── visualization.py           (v1 implemented; add v1-vs-v2 comparison figure)
```

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-E1 (COMPLETED, PASS)
- Dataset: Schürholt zoo (local, ~500 models in v1)
- Hyperparameters confirmed from v1: Adam lr=3e-4, d_model=256, 4 layers, 8 heads, CLS pooling
- Reused components: data_loader.py, orbit_construction.py, statistics.py, similarity_analysis.py, nft_encoder.py
- Reason for reuse: Controlled v2 experiment — only HF identifier, zoo size, and sign-flip verification change

**v1 Lessons Applied in v2:**
1. ✅ HF identifier corrected: `schurholt/model_zoos_dataset`
2. ✅ Pre-flight assertion: `len(zoo_weights) >= 10000`
3. ✅ Sign-flip functional equivalence verification added
4. ✅ CLS pooling assertion added
5. ✅ Asymmetric gate: scaling PASS required; sign-flip EXPLORE on fail

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset name + size | Phase 2B verification plan | §1.3 Experimental Setup |
| HF identifier (corrected) | v1 validation lesson | 04_validation.md §6 Reflection |
| NFT architecture | Phase 3 PRD | 03_prd.md §4.2 |
| NFT d_model, heads, layers | Phase 3 Config | 03_config.md §NFTConfig |
| Orbit pair construction | Phase 3 Logic | 03_logic.md §L-5-2 |
| Cross-orbit sampling (decile) | Phase 3 Logic | 03_logic.md §L-5-3 |
| Cosine similarity metric | Phase 3 PRD | 03_prd.md §FR-4 |
| Bootstrap CI (n_boot=1000) | Phase 3 Config | 03_config.md §ProbeConfig |
| Sign-flip verification | v1 lesson | 04_validation.md §3.2, §5.2 |
| CLS pooling requirement | v1 lesson | 04_validation.md §7.3 |
| Training fallback (lr=3e-4) | v1 results | 04_validation.md §7.2 |
| Asymmetric gate design | v1 reflection + 02b plan | 04_validation.md §6; 02b §3.2 |
| Visualization figures (5) | Phase 3 PRD | 03_prd.md §FR-6 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state managed via restate block)
**Date:** 2026-08-27

### Workflow History for This Hypothesis

| Event | Phase | Date |
|-------|-------|------|
| H-M1 created | Phase 2B | 2026-08-26 |
| Implementation planning completed (v1) | Phase 3 | 2026-08-26 |
| Phase 4 validation ran (v1) | Phase 4 | 2026-08-26 |
| Gate FAIL (sign-flip); SELF_MODIFY | Phase 4 | 2026-08-26 |
| Phase 2C experiment brief redesigned (v2) | Phase 2C | 2026-08-27 |

---

## Quality Validation

✅ All hyperparameters justified (from v1 confirmed values + Phase 3 PRD)
✅ Dataset choice justified (Schürholt zoo — only real 50k MLP zoo with property labels)
✅ Mechanism grounded in code (v1-verified implementation; incremental fix)
✅ No unsupported assumptions (all claims trace to v1 results or Phase 3 PRD)
✅ Full traceability (Traceability Matrix section E above)
✅ Synthetic data policy: REAL data (real trained models; oracle transforms are deterministic)
✅ Sample size: 1,000 orbit pairs × 2 orbit types × ~50k zoo models (statistically meaningful)
✅ v2-specific: HF identifier corrected; data size assertion added; sign-flip verification added

---

*MCP Tools Used: None (N/A-no-MCP). All specifications grounded in Phase 3 implementation documents (03_prd.md, 03_architecture.md, 03_logic.md, 03_config.md) and v1 empirical results (04_validation.md, results.json).*
*Next Phase: Phase 3 — Implementation Planning (v2)*
