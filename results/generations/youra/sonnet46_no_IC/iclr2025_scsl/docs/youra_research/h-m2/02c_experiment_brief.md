# Experiment Design: H-M2

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under GroupDRO training on Waterbirds WILDS, the group-balanced gradient signal from the worst-group loss propagates through all ResNet-50 layers including layer4, modifying weight updates to reduce the predictive utility of spurious background features for classification loss minimization.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (Proxy Verification via H-M3 Outcome) Template** — H-M2 is a theoretical mechanism hypothesis. It does NOT run its own new experiment independently — instead, it designs a PROXY ANALYSIS that reuses H-M3's linear probe measurements as evidence for gradient propagation. The experiment design specifies: (a) theoretical basis for gradient propagation through all layers, and (b) a gradient norm analysis that confirms non-zero gradient flow at layer4 during GroupDRO training.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 PASS (GroupDRO worst-group loss confirmed to create group-balanced gradient signal; minority_fraction=0.0501, WGA gap +0.16); H-P0 PASS (DFR ≡ ERM backbone)
**Gate Status:** SHOULD_WORK (not yet evaluated — pending this experiment + H-M3 confirmation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM (Step 2 of causal chain: GroupDRO signal → **backbone layers** → probe accuracy)
- **Prerequisites:** H-M1 (COMPLETED, PASS), H-P0 (COMPLETED, PASS)

### Gate Condition
**SHOULD_WORK gate:** Failure narrows but does not invalidate the pipeline. If gradient propagation evidence is absent (H-M3 shows no difference), this would mean the GroupDRO signal did not modify backbone layer4 weights in a way detectable by linear probing — a limitation documented and workflow continues.

---

## Continuation Context

**Previous hypothesis:** H-M1 (GroupDRO Minority Group Upweighting Creates Group-Balanced Gradient Signal) — PASS

### Previous Hypothesis Results
- H-M1 confirmed: GroupDRO `LossComputer.is_robust=True` path active (kohpangwei/group_DRO)
- Minority groups (land-bird-land + water-bird-water): fraction = 0.0501 (5.01% of training data)
- GroupDRO upweights these 240 samples via exponentiated gradient ascent on group weights q
- WGA gap: GroupDRO = 0.88 vs ERM = 0.72 (+0.16), consistent with effective upweighting
- H-P0 confirmed: DFR ≡ ERM backbone (cosine sim = 1.000000 all 3 seeds)
- Checkpoint path: `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints`
  - erm_seed{1,2,3}.pt, groupdro_seed{1,2,3}.pt, sam_seed{1,2,3}.pt, dfr_seed{1,2,3}.pt

**Key reuse:** Same Waterbirds WILDS dataset (local cache at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`), same 12 ResNet-50 checkpoints, same feature extraction protocol (layer4 → AdaptiveAvgPool2d(1,1) → flatten → D=2048).

**Critical research finding from H-M1 completion:**
Izmailov et al. (2022, NeurIPS) found that "the success of Group DRO can largely be attributed to **learning a better weighting for the features in the last linear layer**, rather than learning better features." This is the COMPETING HYPOTHESIS to H-M2. H-M2 claims backbone-level gradient modification; Izmailov 2022 claims head-only weighting improvement explains GroupDRO's gains. H-M3 will provide the decisive evidence. H-M2's theoretical case must acknowledge this contested landscape.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: GroupDRO gradient propagation backbone representation learning spurious features**
- Results: No relevant results (Archon KB contains diffusion model domain — domain mismatch)
- Similarity scores all < 0.48, topics: Marigold depth estimation, DALL-E-2, Perturbed Attention Guidance
- **Conclusion:** Archon KB has no spurious correlation / group robustness content

**Query 2: Spurious correlation linear probe ResNet feature decodability**
- Results: No relevant results (same domain mismatch)
- **Conclusion:** Archon KB cannot inform this experiment design

**Query 3: Gradient analysis ResNet layer feature extraction probe (code examples)**
- Results: No relevant code examples (diffusion pipeline code only)
- **Conclusion:** All implementation research must come from Exa

### Archon Code Examples

No relevant code examples found in Archon KB (domain mismatch — KB specialized in diffusion models).

### Exa GitHub Implementations

**Query 1: izmailovpavel spurious_feature_learning GroupDRO ResNet50 Waterbirds checkpoint gradient**

**Repository 1**: izmailovpavel/spurious_feature_learning ⭐ (Official Paper Repo)
- **URL**: https://github.com/izmailovpavel/spurious_feature_learning
- **Relevance**: Primary implementation for all 12 checkpoints used in this experiment chain
- **Key Findings:**
  - GroupDRO implementation forked from kohpangwei/group_DRO with `--dfr_data --dfr_model` flags
  - ERM training: `train_supervised.py --num_epochs=100 --weight_decay=1e-4 --batch_size=32 --init_lr=3e-3 --scheduler=cosine_lr_scheduler`
  - Spurious feature evaluation: `dfr_evaluate_spurious.py --predict_spurious` — directly computes layer-level spurious decodability
  - Feature extraction: `model.layer4 → AdaptiveAvgPool2d(1,1) → flatten → D=2048` (confirmed standard protocol)
  - **Key paper finding (Izmailov 2022, NeurIPS):** "success of Group DRO can largely be attributed to learning a better weighting for the features in the **last linear layer**, rather than learning better features" — challenges H-M2's backbone modification claim
- **Configuration Extracted:**
  - GroupDRO hyperparams: grid search over generalization adjustment C, weight_decay, learning_rate
  - Early stopping: based on worst-group accuracy on validation set
  - Batch size: 32 (Waterbirds), 100 (other datasets)

**Repository 2**: kohpangwei/group_DRO ⭐ (Official GroupDRO Algorithm)
- **URL**: https://github.com/kohpangwei/group_DRO (also at https://github.com/PolinaKirichenko/deep_feature_reweighting)
- **Relevance**: Source implementation of GroupDRO algorithm used to train the 12 checkpoints
- **Algorithm details (Sagawa et al. 2019, Algorithm 1):**
  - Maintains group weights q_g via exponentiated gradient ascent
  - Interleaves SGD on θ (model parameters including ALL backbone layers) and exponent gradient ascent on q
  - Loss = max_g E_{P_g}[ℓ(θ; (x,y))] = ∑_g q_g · mean_loss_g
  - Gradient: ∂L/∂θ = ∑_g q_g · (∂mean_loss_g/∂θ) — q-weighted gradient flows through ALL layers via standard backpropagation
- **Key insight:** SGD on θ uses the **full model parameters** (backbone + head) — group weighting modifies effective batch composition seen by all layers
- **Sample command (Waterbirds):** `python run_expt.py -s confounder -d CUB -t waterbird_complete95 -c forest2water2 --lr 0.001 --batch_size 128 --weight_decay 0.0001 --model resnet50 --n_epochs 300 --reweight_groups --robust --gamma 0.1 --generalization_adjustment 0`

**Repository 3**: kodai-utsunomiya-mdl/spurious-feature-analysis_v2 ⭐ (Gradient Flow Analysis)
- **URL**: https://github.com/kodai-utsunomiya-mdl/spurious-feature-analysis_v2
- **Relevance**: DIRECT relevance — "Analysis of Gradient Flow and Group Performance Gaps under Spurious Correlations" supports GroupDRO + Waterbirds + ResNet50 with layer4 extraction
- **Key features:**
  - Supports `debias_method: "GroupDRO"` training
  - `feature_extractor_resnet_intermediate_layer: layer4` extraction
  - Analysis includes: `analyze_jacobian_norm`, `analyze_gradient_basis`, `analyze_gap_dynamics_factors`
  - DFR evaluation via logistic regression on balanced validation set (same as H-M3 approach)
  - Confirms gradient flow analysis is a standard way to verify GroupDRO backbone modification

**Key Literature Finding:**

**Raymond et al. (ICLR 2026)**: "Alignment, Convexity and Completeness: Mechanisms Behind GroupDRO"
- **URL**: https://openreview.net/forum?id=yJzMPGtakp
- **Finding:** "Beyond the head, under end-to-end training GDRO also reshapes the representation: through a measure called **Completeness**, we show that task-relevant information is spread across multiple dimensions in GDRO while ERM tends to concentrate it in fewer"
- **Significance:** DIRECTLY supports H-M2 — GroupDRO does modify backbone representations under end-to-end training. However, head-only analysis (fixed features) shows alignment effect. The backbone modification is a SECONDARY effect.
- **Implication for H-M2 design:** H-M2's proxy verification via gradient norm analysis at layer4 is theoretically well-motivated. Raymond 2026 confirms representation reshaping occurs.

**Query 2: GroupDRO worst-group loss gradient backpropagation all layers ResNet backbone**

Additional findings:
- Sagawa et al. (2019) Algorithm 1: "The run time of the algorithm is similar to that of SGD for a given number of epochs (less than 5% difference), as run time is dominated by computation of the **loss and its gradient**." — confirms standard backprop through all layers
- CROIS paper (2022): Distinguishes backbone-training GroupDRO (end-to-end) vs head-only GroupDRO — confirms two distinct gradient propagation modes
- Challenges & Opportunities (2023): "GroupDRO solves the above optimization problem by maintaining a weight q_g for each group g and weighting the loss of examples in group g by q_g. **Stochastic gradient descent on parameter w is interleaved with gradient ascent on the weights q_g**" — confirms full parameter update

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Gradient propagation in GroupDRO is theoretically certain (standard SGD backprop through all layers with group-weighted loss). The EMPIRICAL question is whether this modifies layer4's SPURIOUS FEATURE ENCODING. H-M2 uses proxy verification: if H-M3 detects lower spurious probe accuracy in GroupDRO vs ERM, gradient propagation is confirmed.

**Recommended Implementation Path:**
- Primary: Reuse checkpoints from izmailovpavel/spurious_feature_learning (already available, same as H-P0 and H-M1)
- Fallback: Gradient norm analysis using PyTorch hooks (no training required — analyze saved checkpoints)
- Justification: H-M2 is a PROXY verification step. The 12 checkpoints are already downloaded and verified. The experiment requires only inference (no new training).

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-M2 experiment uses:
1. Standard PyTorch register_hook for gradient analysis (no novel architecture)
2. sklearn LogisticRegression for linear probe (same as H-P0/H-M1, well-understood)
3. Feature extraction identical to H-P0 verified protocol

No complex novel architecture requiring Serena semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Waterbirds WILDS
**Version:** v1.0
**Type:** standard (real, established dataset)
**Source:** WILDS benchmark (Koh et al. 2021); already verified in H-P0

**Details:**
- Full test set: 5,794 samples (4 groups: landbird-land, landbird-water, waterbird-land, waterbird-water)
- Background label: `background_label = group_array % 2` (0=land, 1=water)
- Train set: 4,795 samples (minority groups: land-bird-land 184 + water-bird-water 56 = 240 samples, 5.01%)
- Splits: Standard WILDS train/val/test — use FULL test split (5,794 samples)

**Loading Information** (for Phase 4 download):
- Method: WILDS API (already cached locally)
- Identifier: `wilds.get_dataset(dataset='waterbirds', root_dir='/home/PrayPrey/.wilds_cache')`
- Code: `dataset = get_dataset(dataset='waterbirds', download=False, root_dir='/home/PrayPrey/.wilds_cache')`

### Models

#### Baseline Model

**Architecture:** ResNet-50 pretrained on ImageNet1k
**Source:** izmailovpavel/spurious_feature_learning checkpoints (already verified in H-P0/H-M1)
**Checkpoints:**
- ERM (baseline — higher spurious encoding expected):
  - `erm_seed1.pt`, `erm_seed2.pt`, `erm_seed3.pt`
- GroupDRO (test method — lower spurious encoding predicted):
  - `groupdro_seed1.pt`, `groupdro_seed2.pt`, `groupdro_seed3.pt`
- SAM (exploratory — backbone-changing, unknown spurious effect):
  - `sam_seed1.pt`, `sam_seed2.pt`, `sam_seed3.pt`
- DFR (control — backbone-preserving, expected ≡ ERM):
  - `dfr_seed1.pt`, `dfr_seed2.pt`, `dfr_seed3.pt`

**Feature extraction protocol (IDENTICAL to H-P0, proven working):**
```python
# Confirmed working from H-P0 validation (cosine sim = 1.000000)
features = model.layer4(x)  # (B, 2048, H, W)
features = F.adaptive_avg_pool2d(features, (1, 1))  # (B, 2048, 1, 1)
features = features.flatten(1)  # (B, 2048)
```

**Loading Information** (for Phase 4 download):
- Method: torch.load (checkpoints already local)
- Identifier: Local path `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints/`
- Code: `model = torchvision.models.resnet50(); state = torch.load(ckpt_path); model.load_state_dict(state)`

#### Proposed Model

**Architecture:** Baseline (ResNet-50 ERM) — No architecture modification. H-M2 is a PROXY verification hypothesis. The "proposed" experiment is a GRADIENT NORM ANALYSIS on the existing GroupDRO checkpoint.

**Core Mechanism:** GroupDRO's end-to-end training modifies all ResNet-50 backbone layer weights via group-weighted gradient backpropagation. The mechanism is standard SGD backpropagation through all layers (including layer4) with a reweighted loss function.

**Core Mechanism Implementation:**

```python
# Core Mechanism: GroupDRO Gradient Propagation Proxy Verification
# Based on: Sagawa 2019 Algorithm 1 + standard PyTorch backprop
# Evidence source: kohpangwei/group_DRO, kodai-utsunomiya-mdl/spurious-feature-analysis_v2

def compute_layer4_gradient_norm(model, dataloader, device):
    """
    Compute mean L2 gradient norm at layer4 parameters during GroupDRO loss.
    Proxy measure: if gradient norm at layer4 is non-zero and differs from ERM,
    the group-weighted signal reached layer4.
    
    Args:
        model: ResNet-50 loaded from checkpoint
        dataloader: Waterbirds train set with group labels
    Returns:
        layer4_grad_norm (float): mean L2 norm of layer4 parameter gradients
    """
    model.train()  # Enable gradient computation
    layer4_grad_norms = []
    
    for batch_idx, (x, y, metadata) in enumerate(dataloader):
        if batch_idx >= 50:  # 50 batches sufficient for gradient norm estimate
            break
        x, y = x.to(device), y.to(device)
        group = metadata[:, 0].to(device)  # group_array column
        
        # Standard forward pass
        logits = model(x)  # Uses full ResNet-50 including layer4
        
        # Compute per-group losses (GroupDRO mechanism from H-M1)
        group_losses = []
        for g in range(4):
            mask = (group == g)
            if mask.sum() > 0:
                group_losses.append(F.cross_entropy(logits[mask], y[mask]))
        
        # Worst-group loss (GroupDRO objective)
        loss = torch.stack(group_losses).max()
        
        # Backpropagate through ALL layers (standard PyTorch autograd)
        model.zero_grad()
        loss.backward()
        
        # Measure gradient at layer4 parameters
        layer4_params = list(model.layer4.parameters())
        grad_norms = [p.grad.norm().item() for p in layer4_params if p.grad is not None]
        layer4_grad_norms.append(np.mean(grad_norms))
    
    return np.mean(layer4_grad_norms)

# Compare: ERM gradient norms vs GroupDRO gradient norms at layer4
# Theoretical prediction: gradient_norm_groupdro > 0 (gradient reaches layer4)
# Empirical question (H-M3): does this modify spurious feature encoding?
```

### Training Protocol

**Note:** H-M2 is a PROXY VERIFICATION experiment — NO NEW TRAINING. The 12 checkpoints are already trained (downloaded and verified in H-P0/H-M1). This experiment analyzes existing checkpoints.

**Experiment Type:** Inference-only + Gradient Analysis + Linear Probe

**Step 1: Gradient Norm Analysis (Proxy for gradient propagation)**
- Load each of 12 checkpoints
- Compute layer4 gradient norm under GroupDRO loss and ERM loss
- Verify: gradient norm at layer4 > 0 for GroupDRO (confirms gradient reaches layer4)
- Compare: GroupDRO vs ERM gradient norms at layer4 (quantifies magnitude difference)
- Data: Waterbirds WILDS train set (use first 50 batches of batch_size=32)

**Step 2: Weight Difference Analysis (Direct backbone modification evidence)**
```
For each seed in {1, 2, 3}:
  Load ERM and GroupDRO checkpoints
  Compute layer4 weight difference: L2_norm(W_groupdro - W_erm) per layer4.0, layer4.1, layer4.2
  Report: mean and std of weight differences across seeds
```
- Evidence: Non-zero weight difference at layer4 = GroupDRO training modified layer4 weights
- Note: Weight difference is DEFINITIVE evidence of gradient propagation (if weights differ, gradient reached layer4 during training)

**Step 3: Linear Probe (H-M3 proxy — combined with H-M3 experiment)**
- Full test set: 5,794 samples
- sklearn LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)
- Probe target: background_label = group_array % 2
- Per-checkpoint probe accuracy for all 12 checkpoints
- THIS IS THE PRIMARY EVIDENCE for H-M2 (via H-M3 outcome)

**Seeds:** 1 (fixed for each checkpoint; 3 matched pairs for statistical test)

### Evaluation

**Primary Metrics (H-M2 Proxy):**

1. **Layer4 Weight L2 Distance** (direct evidence):
   - `layer4_weight_diff_seed{k} = L2_norm(groupdro_layer4_weights_seed{k} - erm_layer4_weights_seed{k})`
   - Expected: > 0 for all seeds (definitive gradient propagation evidence)
   - Expected magnitude: similar scale to head weight differences if backbone-level change occurred

2. **Layer4 Gradient Norm under GroupDRO vs ERM Loss** (mechanism confirmation):
   - `grad_norm_groupdro_layer4_seed{k}` vs `grad_norm_erm_layer4_seed{k}`
   - Expected: both > 0 (gradient reaches layer4 in both training regimes)
   - Comparison: different norms = different gradient signals at layer4

3. **Spurious Probe Accuracy (via H-M3 measurement)**:
   - `probe_acc_groupdro_seed{k}` vs `probe_acc_erm_seed{k}` on full Waterbirds test set
   - H-M2 success criteria: probe_acc_groupdro < probe_acc_erm across seeds (proxy confirmation)

**Success Criteria (H-M2 Proxy Verification):**

| Criterion | Threshold | Result Level |
|-----------|-----------|--------------|
| Layer4 weight diff > 0 | All 3 seeds | CONFIRMED: gradient reached layer4 |
| Gradient norms at layer4 both > 0 | Both training regimes | CONFIRMED: standard backprop |
| GroupDRO probe acc < ERM probe acc | H-M3 primary test | PROXY CONFIRMATION |
| Cohen's d > 0.5 in H-M3 | H-M3 primary test | STRONG CONFIRMATION |

**Expected Baseline Performance (from H-P0 + research):**
- ERM spurious probe accuracy: ~0.90 (confirmed H-P0: ERM background probe acc = 0.900)
- GroupDRO WGA: 0.88 vs ERM WGA: 0.72 (Izmailov 2022) — indicates different backbone behavior

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification probe (background: land=0, water=1)
- Library: sklearn.metrics
- Code: `probe.score(features_test, background_labels_test)` (same as H-P0 verified protocol)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Layer4 weight L2 distance (GroupDRO-ERM) per seed, bar chart

#### Additional Figures (LLM Autonomous)
Based on the proxy verification design, the following figures communicate the mechanism:

1. **Layer4 Weight Difference Heatmap**: Per-layer (layer4.0, layer4.1, layer4.2) weight difference L2 norm for 3 seeds — shows WHERE in layer4 the gradient modified weights
2. **Gradient Norm Comparison**: ERM vs GroupDRO gradient norms at layer4 across 50 batches — box plot showing gradient magnitude distribution
3. **Weight Distance vs WGA Scatter**: Layer4 weight distance (GroupDRO-ERM) vs WGA improvement per seed — tests if larger gradient modification correlates with better WGA

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | GroupDRO uses standard SGD backprop through ALL ResNet-50 layers including layer4 (standard PyTorch autograd — theoretically certain) | TRUE |
| Mechanism Isolatable | Layer4 parameters and gradients can be extracted independently via `model.layer4.parameters()` and `.grad` attributes | TRUE |
| Baseline Measurable | ERM checkpoints load identically; weight differences computable as L2 norm | TRUE |

### Architecture Compatibility Check

ResNet-50 is FULLY COMPATIBLE with this experiment:
- Layer4 contains 3 Bottleneck blocks (layer4[0], layer4[1], layer4[2]), each with conv1/conv2/conv3/bn layers
- PyTorch autograd computes gradients at all parameters during backward pass
- `model.layer4.parameters()` returns all 27 parameter tensors in layer4
- Feature extraction confirmed working in H-P0 (cosine sim = 1.000000)

**Required Features:**
- Standard ResNet-50 architecture (confirmed — izmailovpavel checkpoints are standard torchvision ResNet-50)
- PyTorch autograd for gradient computation (standard)
- No novel architecture modifications

**Incompatible Architectures:**
- None (ResNet-50 fully supports all required operations)

> ⚠️ Weight difference analysis requires BOTH ERM and GroupDRO checkpoints at same seed — verify 3 matched pairs exist before running.

---

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Layer4 weight diff (seed k): {value:.4f}" printed for all 3 seeds | weight_analysis.py:compare_checkpoints() |
| Tensor Shape | layer4[0].conv1.weight: (64, 256, 1, 1) — unchanged (analysis, not architecture change) | model inspection |
| Metric Delta | layer4_weight_L2_diff > 0 for all seeds; probe_acc_groupdro < probe_acc_erm | evaluate_h_m2.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_gradient_propagation(erm_ckpt_path, groupdro_ckpt_path, seed):
    """
    Definitive check: if GroupDRO and ERM layer4 weights differ, gradient reached layer4.
    H-P0 proved DFR ≡ ERM (cosine_sim=1.000000). GroupDRO must differ from ERM for H-M2.
    """
    erm_model = load_resnet50(erm_ckpt_path)
    gdro_model = load_resnet50(groupdro_ckpt_path)
    
    indicators = {}
    
    # Check 1: Layer4 weight difference (definitive gradient propagation evidence)
    for block_idx in range(3):  # layer4[0], layer4[1], layer4[2]
        erm_weights = list(erm_model.layer4[block_idx].parameters())
        gdro_weights = list(gdro_model.layer4[block_idx].parameters())
        diffs = [torch.norm(g - e).item() for g, e in zip(gdro_weights, erm_weights)]
        indicators[f"layer4_block{block_idx}_diff"] = np.mean(diffs)
    
    # Check 2: Any non-zero difference = gradient propagated to layer4 during training
    indicators["gradient_reached_layer4"] = any(v > 1e-6 for v in indicators.values())
    
    # Check 3: Head weight difference (comparison baseline)
    erm_head = erm_model.fc.weight
    gdro_head = gdro_model.fc.weight
    indicators["head_weight_diff"] = torch.norm(gdro_head - erm_head).item()
    
    # Ratio: backbone_diff / head_diff — measures relative backbone modification
    backbone_diff = np.mean([v for k, v in indicators.items() if "block" in k])
    indicators["backbone_to_head_ratio"] = backbone_diff / max(indicators["head_weight_diff"], 1e-10)
    
    print(f"Seed {seed}: gradient_reached_layer4={indicators['gradient_reached_layer4']}, "
          f"backbone_to_head_ratio={indicators['backbone_to_head_ratio']:.4f}")
    
    return indicators

# Run for all 3 seeds
for seed in [1, 2, 3]:
    erm_path = f"checkpoints/erm_seed{seed}.pt"
    gdro_path = f"checkpoints/groupdro_seed{seed}.pt"
    result = verify_gradient_propagation(erm_path, gdro_path, seed)
    assert result["gradient_reached_layer4"], f"FAIL: Gradient did not reach layer4 for seed {seed}"
    print(f"  ✅ Gradient propagation confirmed at layer4 for seed {seed}")
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Layer4 weights identical (L2_diff = 0) | `torch.norm(gdro_layer4 - erm_layer4) < 1e-6` | UNEXPECTED FAIL: GroupDRO checkpoint may be corrupted or is ERM |
| Gradient norm = 0 at layer4 | `all(p.grad is None for p in model.layer4.parameters())` | FAIL: Gradient computation issue (check requires_grad=True) |
| H-M3 shows no probe accuracy difference | `probe_acc_groupdro >= probe_acc_erm` | GATE: SHOULD_WORK — document limitation, continue |
| Checkpoint mismatch | Different seeds loaded for ERM/GroupDRO pair | FAIL: Re-verify checkpoint file naming |

**Expected outcome for weight analysis:** Since GroupDRO uses full end-to-end training (not head-only like DFR), layer4 weight differences SHOULD be non-zero. H-P0 confirmed DFR ≡ ERM (frozen backbone), so GroupDRO ≠ ERM at layer4 is expected. If layer4 diff = 0, this would be scientifically surprising and require investigation.

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Gradient Reached Layer4 | TRUE (L2 diff > 0 for all 3 seeds) | weight_analysis.py output |
| Effect Measurable | Backbone-to-head ratio > 0 | ratio = backbone_diff / head_diff |
| Hypothesis Supported | H-M3 outcome: one-sided p < 0.05 (CONFIRMED) or p < 0.10 with Cohen's d > 0.5 (SUGGESTIVE) | H-M3 probe accuracy comparison |

**Note on SHOULD_WORK gate:** Even if H-M3 shows p ≥ 0.10 (REJECTED), the weight difference analysis provides a SECONDARY verification of gradient propagation. The pipeline continues regardless (SHOULD_WORK gate).

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Layer4 weight L2 distance > 0 for all 3 GroupDRO-ERM seed pairs (gradient propagation confirmed)
2. Gradient norm analysis shows non-zero gradients at layer4 under GroupDRO loss (mechanism active)
3. H-M3 linear probe outcome provides proxy: probe_acc_groupdro < probe_acc_erm (direction supports H-M2)

**Note on contested landscape (Izmailov 2022 vs Raymond 2026):**
- Izmailov 2022 claims GroupDRO success is "largely" head-weighting, not better features
- Raymond 2026 confirms "GDRO reshapes representation: Completeness shows task-relevant info spread across more dimensions"
- Both can be true: GroupDRO modifies BOTH backbone (H-M2) AND head-weighting (Izmailov 2022). The RELATIVE contribution is the unresolved question H-M3 addresses empirically.
- H-M2's weight analysis will show gradient DID reach layer4; H-M3 will show whether this translates to MEASURABLE spurious feature reduction.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**No relevant sources found** — Archon KB domain mismatch (diffusion models). All research from Exa.

### B. GitHub Implementations (Exa)

**Repository 1**: izmailovpavel/spurious_feature_learning (Official)
- **URL**: https://github.com/izmailovpavel/spurious_feature_learning
- **Query Used**: "izmailovpavel spurious_feature_learning GroupDRO ResNet50 Waterbirds checkpoint gradient"
- **Relevance**: Primary checkpoint source for all 12 ResNet-50 models
- **Key Code** (annotated):
  ```python
  # From dfr_evaluate_spurious.py — spurious feature probe evaluation
  # This is the EXACT protocol for linear probe on layer4 features
  python3 dfr_evaluate_spurious.py --data_dir=<DATA_DIR> \
      --dataset=SpuriousCorrelationDataset --model=imagenet_resnet50_pretrained \
      --ckpt_path=logs/waterbirds/erm_seed1/final_checkpoint.pt \
      --predict_spurious  # key flag: predicts spurious attribute (background)
  ```
- **Key insight**: `--predict_spurious` flag trains a probe to predict BACKGROUND (spurious attribute) — EXACTLY what H-M2/H-M3 measures
- **Used For**: Dataset loading, checkpoint loading, feature extraction protocol confirmation

**Repository 2**: kohpangwei/group_DRO (Algorithm Implementation)
- **URL**: https://github.com/kohpangwei/group_DRO (also PolinaKirichenko/deep_feature_reweighting)
- **Query Used**: "GroupDRO worst-group loss gradient backpropagation all layers ResNet backbone"
- **Relevance**: Source of GroupDRO training algorithm — confirms gradient propagation mechanism
- **Key Code** (annotated):
  ```python
  # From Algorithm 1 (Sagawa 2019) — interleaves SGD on θ and gradient ascent on q
  # q = group weights (upweights minority groups per H-M1 confirmed mechanism)
  # θ = ALL model parameters (backbone + head) — SGD updates ALL layers
  # ∂L/∂θ = ∑_g q_g · (∂mean_loss_g/∂θ) — group-weighted gradient through ALL layers
  
  sample command:
  python run_expt.py -s confounder -d CUB -t waterbird_complete95 -c forest2water2 \
      --lr 0.001 --batch_size 128 --weight_decay 0.0001 --model resnet50 \
      --n_epochs 300 --reweight_groups --robust --gamma 0.1 --generalization_adjustment 0
  ```
- **Used For**: Theoretical basis for gradient propagation through all layers

**Repository 3**: kodai-utsunomiya-mdl/spurious-feature-analysis_v2 (Gradient Flow Analysis)
- **URL**: https://github.com/kodai-utsunomiya-mdl/spurious-feature-analysis_v2
- **Relevance**: HIGHEST relevance — implements gradient flow analysis for GroupDRO + Waterbirds + ResNet layer4
- **Key features (annotated)**:
  ```yaml
  # config.yaml — directly relevant to H-M2 experiment design
  debias_method: "GroupDRO"         # GroupDRO training (H-M2 test condition)
  feature_extractor_model_name: ResNet50
  feature_extractor_resnet_intermediate_layer: layer4  # EXACT H-M2 measurement point
  analyze_jacobian_norm: true       # Gradient norm analysis (H-M2 proxy)
  analyze_gradient_basis: true      # Gradient direction analysis
  analyze_gap_dynamics_factors: true  # Group performance gap factors
  use_dfr: true                     # DFR evaluation = H-M3 linear probe protocol
  ```
- **Used For**: Pseudo-code design for gradient norm analysis, confirmation of analysis methodology

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. H-M2 uses standard PyTorch weight comparison and gradient hooks with no novel architecture.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Reports — H-P0 and H-M1

**File**: `h-p0/04_validation.md`, `h-m1/04_validation.md`

**Reused Components:**
- Dataset: Waterbirds WILDS (path: `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`) — proven stable
- Checkpoints: `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints/` — all 12 verified
- Feature extraction: layer4 → AdaptiveAvgPool2d(1,1) → flatten → D=2048 — confirmed by H-P0 cosine sim = 1.000000
- Probe: sklearn LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42) — confirmed by H-P0 ERM probe acc = 0.900

**Why Reused**: Enables controlled experiment chain — only the ANALYSIS TYPE changes (H-P0: cosine similarity; H-M1: loss weight analysis; H-M2: weight difference + gradient norm; H-M3: linear probe on full test set).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Waterbirds WILDS) | Previous validation (H-P0) | H-P0 04_validation.md |
| Checkpoint paths | Previous validation (H-P0/H-M1) | H-P0 04_validation.md |
| Feature extraction protocol | Previous validation (H-P0) | H-P0 confirmed cosine sim=1.000000 |
| GroupDRO mechanism (backprop all layers) | GitHub (Exa) | kohpangwei/group_DRO Algorithm 1 |
| Gradient norm analysis design | GitHub (Exa) | kodai-utsunomiya-mdl/spurious-feature-analysis_v2 |
| Weight difference analysis | Theory + GitHub | Sagawa 2019 + standard PyTorch |
| Contested landscape (head vs backbone) | Literature (Exa) | Izmailov 2022 NeurIPS; Raymond 2026 ICLR |
| Representation reshaping evidence | Literature (Exa) | Raymond 2026 ICLR: Completeness measure |
| Linear probe protocol | Previous validation (H-P0) | sklearn L-BFGS C=1e9 proven in H-P0 |
| Success criteria | Phase 2B | 02b_verification_plan.md H-M2 section |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05T17:55:00Z

### Workflow History for This Hypothesis

| Event | Timestamp | Details |
|-------|-----------|---------|
| H-P0 PASS | 2026-08-05T16:39:00Z | DFR≡ERM backbone confirmed; ERM probe acc=0.900 |
| H-M1 PASS | 2026-08-05T17:03:20Z | GroupDRO upweighting confirmed; minority_fraction=0.0501 |
| H-M2 IN_PROGRESS | 2026-08-05T17:50:37Z | Phase 2C started for h-m2 |

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results, domain mismatch), Exa (GitHub — izmailovpavel/spurious_feature_learning, kohpangwei/group_DRO, kodai-utsunomiya-mdl/spurious-feature-analysis_v2, Sagawa 2019, Izmailov 2022, Raymond 2026)*
*All specifications grounded in researched implementations and literature*
*Next Phase: Phase 3 - Implementation Planning*
