# Product Requirements Document: H-M2
## Group-Balanced Gradient Propagates Through All Backbone Layers — Proxy Verification via Weight Difference + Gradient Norm Analysis

**stepsCompleted:** [1, 2, 3, 4, 5, 6, 7]
**hypothesis_id:** h-m2
**hypothesis_type:** MECHANISM
**tier:** FULL
**generated_at:** 2026-08-05T18:00:00Z
**source:** 02c_experiment_brief.md

---

## 1. Executive Summary

Implement a proxy verification experiment to confirm that GroupDRO's end-to-end training modifies ResNet-50 backbone weights at layer4 via group-balanced gradient propagation. This is a PROXY VERIFICATION hypothesis — no new training required. The experiment consists of:

1. **Layer4 weight difference analysis** — compute L2 norm of (GroupDRO − ERM) weight tensors at layer4 blocks [0,1,2] for 3 matched seed pairs. Non-zero difference = definitive gradient propagation evidence.
2. **Gradient norm analysis** — compute mean L2 gradient norm at layer4 parameters under GroupDRO loss and ERM loss for 50 training batches. Both must be > 0; different norms indicate different gradient signals.
3. **Linear probe proxy (via H-M3)** — the primary proxy confirmation: probe_acc_groupdro < probe_acc_erm on full Waterbirds test set (5,794 samples).
4. **Visualization** — layer4 weight difference bar chart per seed, gradient norm comparison box plot, backbone-to-head ratio scatter.

**Gate:** SHOULD_WORK — failure narrows but does not invalidate the pipeline. If layer4 weights differ (step 1), gradient propagation is confirmed regardless of H-M3 outcome. H-M3 provides the biological significance test.

---

## 2. Problem Statement

H-M1 confirmed that GroupDRO creates a group-balanced gradient signal (minority group fraction = 0.0501; is_robust=True mechanism verified). H-M2 addresses the second step of the causal chain: does this gradient signal propagate through all ResNet-50 layers, including the deep layer4 feature extraction layers?

This is a contested question. Izmailov 2022 (NeurIPS) argues GroupDRO's success is "largely attributed to learning a better weighting in the last linear layer" (head-only), not better features. Raymond 2026 (ICLR) shows "GDRO reshapes representation: Completeness shows task-relevant information spread across multiple dimensions." Both can be true — GroupDRO modifies BOTH backbone and head. H-M2 establishes that layer4 backbone weights DO differ between GroupDRO and ERM training, providing empirical evidence for backbone-level gradient propagation.

---

## 3. Objectives and Success Criteria

### Primary Objective
Confirm GroupDRO training modifies ResNet-50 layer4 backbone weights via group-weighted gradient propagation, establishing the mechanistic link between GroupDRO's group-balanced signal and backbone feature modification.

### Success Criteria (GATE: SHOULD_WORK)

| Check | Method | Expected Result | Level |
|-------|--------|----------------|-------|
| Layer4 weight diff > 0 | `torch.norm(gdro_layer4 - erm_layer4)` for seeds 1,2,3 | > 1e-6 for all seeds | CONFIRMED |
| Gradient norm > 0 at layer4 | `p.grad.norm()` after backward on 50 batches | > 0 for both training regimes | CONFIRMED |
| Proxy confirmation (H-M3) | `probe_acc_groupdro < probe_acc_erm` on full test set | direction matches (p < 0.10) | SUGGESTIVE |

**Gate Logic:**
- Layer4 weight L2 diff > 0 (all 3 seeds) → CONFIRMED (gradient reached layer4)
- H-M3 probe acc direction supports → PROXY CONFIRMED
- Even if H-M3 p ≥ 0.10 → SHOULD_WORK gate allows pipeline to continue

### Secondary Criteria (Non-blocking)
- Backbone-to-head ratio computed (backbone_diff / head_diff) per seed
- Per-block analysis: layer4[0], layer4[1], layer4[2] weight diffs
- Runtime: < 30 minutes (inference + gradient analysis, GPU optional)
- Figures saved to `h-m2/figures/`

### Failure Contingency
If layer4 weights are identical (L2_diff < 1e-6 for any seed) → investigate checkpoint loading issue. Scientific surprise — GroupDRO is end-to-end trained, not frozen backbone. Document as unexpected and escalate.

---

## 4. Data Specification

### Primary Dataset

**Dataset:** Waterbirds WILDS v1.0
**Source:** WILDS benchmark (Koh et al. 2021); pre-cached from H-P0
**Download:** Pre-cached at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` (do NOT re-download)
**Manual download required:** NO — cache already present
**Loading library:** `wilds` package

```python
from wilds import get_dataset

dataset = get_dataset(dataset='waterbirds', download=False,
                      root_dir='/home/PrayPrey/.wilds_cache')

# For gradient norm analysis: train split (first 50 batches, batch_size=32)
train_data = dataset.get_subset('train')
# group label: metadata[:, 0] → group_array (0-3)
# background_label = group_array % 2 (0=land, 1=water)

# For linear probe (H-M3 proxy): FULL test split
test_data = dataset.get_subset('test')
# Full test set: 5,794 samples — NO subsampling
```

### Dataset Splits Used

| Split | Size | Purpose |
|-------|------|---------|
| Train | ~4,795 | Gradient norm analysis (first 50 batches × batch_size=32) |
| Test | 5,794 | Linear probe evaluation (full test set — no subsampling) |

**Note:** Full test set (5,794 samples) MUST be used for linear probe. Do NOT use subsets < 500 samples.

### Group Structure

| group_array | Bird | Background | Type |
|-------------|------|------------|------|
| 0 | Landbird | Land | Majority (spurious-consistent) |
| 1 | Landbird | Water | Minority (background-atypical) |
| 2 | Waterbird | Land | Minority (background-atypical) |
| 3 | Waterbird | Water | Majority (spurious-consistent) |

**Probe target:** `background_label = group_array % 2` (binary: land=0, water=1)

---

## 5. Model Specification

### Checkpoints

**Architecture:** ResNet-50 (standard torchvision)
**Source:** izmailovpavel/spurious_feature_learning (NeurIPS 2022)
**Location:** `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints/`
**Files:**
- ERM: `erm_seed1.pt`, `erm_seed2.pt`, `erm_seed3.pt`
- GroupDRO: `groupdro_seed1.pt`, `groupdro_seed2.pt`, `groupdro_seed3.pt`
- SAM: `sam_seed1.pt`, `sam_seed2.pt`, `sam_seed3.pt` (exploratory)
- DFR: `dfr_seed1.pt`, `dfr_seed2.pt`, `dfr_seed3.pt` (control — expected ≡ ERM at layer4)

**Total checkpoints analyzed:** 12 (for weight difference: 6 paired comparisons; for linear probe: all 12)

### Checkpoint Loading

```python
import torchvision.models as models
import torch

def load_resnet50(ckpt_path, device='cpu'):
    model = models.resnet50(pretrained=False)
    state = torch.load(ckpt_path, map_location=device)
    # Handle state_dict wrapper
    if 'model' in state:
        state = state['model']
    if 'state_dict' in state:
        state = state['state_dict']
    model.load_state_dict(state, strict=False)
    model.eval()
    return model
```

### Feature Extraction Protocol (IDENTICAL to H-P0 — proven working)

```python
import torch.nn.functional as F

def extract_layer4_features(model, x):
    """
    Confirmed working from H-P0 (cosine sim = 1.000000).
    """
    with torch.no_grad():
        x = model.conv1(x)
        x = model.bn1(x)
        x = model.relu(x)
        x = model.maxpool(x)
        x = model.layer1(x)
        x = model.layer2(x)
        x = model.layer3(x)
        x = model.layer4(x)           # (B, 2048, H, W)
        x = F.adaptive_avg_pool2d(x, (1, 1))  # (B, 2048, 1, 1)
        x = x.flatten(1)              # (B, 2048)
    return x
```

---

## 6. Functional Requirements

### FR-1: Layer4 Weight Difference Analysis (Primary)

For each seed k ∈ {1, 2, 3}:
- Load `erm_seed{k}.pt` and `groupdro_seed{k}.pt`
- For each block b ∈ {0, 1, 2} (layer4[b]):
  - Compute L2 norm of weight difference for all parameters in block b
  - `block_diff[b] = mean([torch.norm(gdro_p - erm_p) for gdro_p, erm_p in zip(gdro_block.parameters(), erm_block.parameters())])`
- Compute head weight difference for baseline: `head_diff = torch.norm(gdro_model.fc.weight - erm_model.fc.weight)`
- Compute backbone-to-head ratio: `ratio = mean(block_diffs) / max(head_diff, 1e-10)`
- Assert `any(d > 1e-6 for d in block_diffs)` → "gradient reached layer4"

```python
def verify_gradient_propagation(erm_ckpt_path, groupdro_ckpt_path, seed):
    erm_model = load_resnet50(erm_ckpt_path)
    gdro_model = load_resnet50(groupdro_ckpt_path)
    
    indicators = {}
    block_diffs = []
    
    for block_idx in range(3):
        erm_params = list(erm_model.layer4[block_idx].parameters())
        gdro_params = list(gdro_model.layer4[block_idx].parameters())
        diffs = [torch.norm(g - e).item() for g, e in zip(gdro_params, erm_params)]
        block_diff = np.mean(diffs)
        block_diffs.append(block_diff)
        indicators[f"layer4_block{block_idx}_diff"] = block_diff
    
    indicators["gradient_reached_layer4"] = any(d > 1e-6 for d in block_diffs)
    indicators["head_weight_diff"] = torch.norm(
        gdro_model.fc.weight - erm_model.fc.weight).item()
    indicators["backbone_to_head_ratio"] = (
        np.mean(block_diffs) / max(indicators["head_weight_diff"], 1e-10))
    
    print(f"Seed {seed}: gradient_reached_layer4={indicators['gradient_reached_layer4']}, "
          f"backbone_to_head_ratio={indicators['backbone_to_head_ratio']:.4f}")
    return indicators
```

### FR-2: Gradient Norm Analysis

For each method ∈ {ERM, GroupDRO} for seed 1 (representative):
- Set `model.train()` (enable gradient computation)
- Process 50 training batches (batch_size=32)
- For each batch:
  - Compute ERM loss: `F.cross_entropy(logits, y)` OR GroupDRO loss: `max_g(per_group_losses)`
  - `loss.backward()`
  - Collect `p.grad.norm().item()` for all `p` in `model.layer4.parameters()` with `p.grad is not None`
- Report: mean and std of layer4 gradient norms across 50 batches
- Assert both ERM and GroupDRO gradient norms > 0

```python
def compute_layer4_gradient_norm(model, dataloader, loss_type='erm', device='cpu', n_batches=50):
    model.train()
    layer4_grad_norms = []
    
    for batch_idx, (x, y, metadata) in enumerate(dataloader):
        if batch_idx >= n_batches:
            break
        x, y = x.to(device), y.to(device)
        logits = model(x)
        
        if loss_type == 'erm':
            loss = F.cross_entropy(logits, y)
        elif loss_type == 'groupdro':
            group = metadata[:, 0].to(device)
            group_losses = []
            for g in range(4):
                mask = (group == g)
                if mask.sum() > 0:
                    group_losses.append(F.cross_entropy(logits[mask], y[mask]))
            loss = torch.stack(group_losses).max()
        
        model.zero_grad()
        loss.backward()
        
        layer4_params = list(model.layer4.parameters())
        norms = [p.grad.norm().item() for p in layer4_params if p.grad is not None]
        if norms:
            layer4_grad_norms.append(np.mean(norms))
    
    return np.mean(layer4_grad_norms), np.std(layer4_grad_norms)
```

### FR-3: Linear Probe — Full Test Set (H-M3 Proxy)

For all 12 checkpoints (ERM×3, GroupDRO×3, SAM×3, DFR×3):
- Extract layer4 features from FULL test set (5,794 samples) — NO subsampling
- Fit sklearn LogisticRegression on train set features (same probe per checkpoint)
- Evaluate on full test set
- Probe target: `background_label = metadata[:, 0] % 2`
- Report: probe accuracy per checkpoint + mean/std per method

```python
from sklearn.linear_model import LogisticRegression

def linear_probe(train_features, train_labels, test_features, test_labels):
    probe = LogisticRegression(
        solver='lbfgs', C=1e9, max_iter=1000, random_state=42, multi_class='auto')
    probe.fit(train_features, train_labels)
    return probe.score(test_features, test_labels)
```

**Required output:**
```
ERM probe acc:      mean ± std across 3 seeds
GroupDRO probe acc: mean ± std across 3 seeds
SAM probe acc:      mean ± std across 3 seeds
DFR probe acc:      mean ± std across 3 seeds
```

### FR-4: Statistical Test (H-M3 Proxy Direction)

- One-sided paired t-test: H0: probe_acc_groupdro >= probe_acc_erm (3 paired seed comparisons)
- `scipy.stats.ttest_rel(erm_accs, groupdro_accs, alternative='greater')`
- Report p-value and Cohen's d

### FR-5: Visualization (Required)

1. **Layer4 Weight L2 Distance Bar Chart** (REQUIRED — Gate Metric):
   - X-axis: Seeds {1, 2, 3}; grouped bars per layer4 block {0, 1, 2}
   - Y-axis: L2 norm of weight difference (GroupDRO − ERM)
   - Save: `h-m2/figures/layer4_weight_diff.png`

2. **Gradient Norm Comparison** (Required):
   - Box plot: ERM vs GroupDRO gradient norms at layer4 across 50 batches
   - Save: `h-m2/figures/gradient_norm_comparison.png`

3. **Backbone-to-Head Ratio Scatter** (Required):
   - X-axis: seed; Y-axis: backbone_diff / head_diff
   - Save: `h-m2/figures/backbone_head_ratio.png`

4. **Layer4 Weight Difference Heatmap** (Optional):
   - Per-block (layer4[0,1,2]) weight diff across 3 seeds
   - Save: `h-m2/figures/layer4_heatmap.png`

### FR-6: Results Logging

Save structured results to `h-m2/results.json`:
```json
{
  "hypothesis_id": "h-m2",
  "gradient_reached_layer4": true,
  "layer4_weight_diffs": {
    "seed1": {"block0": 0.0, "block1": 0.0, "block2": 0.0, "backbone_to_head_ratio": 0.0},
    "seed2": {"block0": 0.0, "block1": 0.0, "block2": 0.0, "backbone_to_head_ratio": 0.0},
    "seed3": {"block0": 0.0, "block1": 0.0, "block2": 0.0, "backbone_to_head_ratio": 0.0}
  },
  "gradient_norms": {
    "erm_mean": 0.0, "erm_std": 0.0,
    "groupdro_mean": 0.0, "groupdro_std": 0.0
  },
  "linear_probe": {
    "erm_accs": [], "groupdro_accs": [], "sam_accs": [], "dfr_accs": [],
    "erm_mean": 0.0, "groupdro_mean": 0.0,
    "p_value": 0.0, "cohens_d": 0.0
  },
  "gate_result": "PASS",
  "n_test_samples": 5794
}
```

### FR-7: Validation Report

Generate `h-m2/04_validation.md` with:
- Weight difference table (3 seeds × 3 blocks)
- Gradient norm comparison table
- Linear probe results table
- Gate verdict with evidence summary
- Contested landscape note (Izmailov 2022 vs Raymond 2026)

---

## 7. Non-Functional Requirements

### NFR-1: No New Training
- All 12 checkpoints are pre-trained and locally available
- Gradient norm analysis uses model.train() for gradient computation only (no weight updates)
- No optimizer steps; no checkpoint saving

### NFR-2: Full Test Set Required
- Linear probe MUST use full test set (5,794 samples)
- Minimum acceptable: 1,000 samples if full set fails to load
- Do NOT use small subsets < 500 samples

### NFR-3: Reproducibility
- Fixed random_state=42 in LogisticRegression
- Gradient norm analysis: fixed batch order (DataLoader shuffle=False for reproducibility)
- Results are deterministic for weight difference analysis

### NFR-4: Resource Constraints
- GPU: Optional (weight difference is CPU-only; gradient norm benefits from GPU)
- Memory: < 4 GB (12 ResNet-50 models × ~100 MB each — load/analyze/unload sequentially)
- Storage: < 50 MB (results.json + figures + 04_validation.md)

### NFR-5: Reuse from H-P0 and H-M1
- Checkpoint path verified by H-P0 (cosine_sim = 1.000000)
- Dataset cache verified by H-P0 and H-M1
- Feature extraction protocol identical (layer4 → AdaptiveAvgPool2d → flatten)
- sklearn probe identical to H-P0 (C=1e9, solver='lbfgs', max_iter=1000)

---

## 8. Dependencies

### 8.1 Python Packages

```
torch>=1.9.0       # Model loading, gradient analysis, weight difference
torchvision        # ResNet-50 architecture
wilds              # Waterbirds dataset loading
sklearn            # LogisticRegression for linear probe
scipy              # scipy.stats.ttest_rel for statistical test
numpy              # Numerical computation
matplotlib         # Visualization
```

### 8.2 External Repositories (Reference — Already Available)

| Repository | Purpose |
|------------|---------|
| izmailovpavel/spurious_feature_learning | Source of 12 pre-trained checkpoints |
| kohpangwei/group_DRO | Theoretical basis for gradient propagation |
| kodai-utsunomiya-mdl/spurious-feature-analysis_v2 | Gradient analysis methodology reference |

### 8.3 Pre-conditions

- H-P0 COMPLETED and PASS ✓
- H-M1 COMPLETED and PASS ✓
- 12 checkpoints at `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints/` ✓
- Waterbirds WILDS cache at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` ✓
- Python packages: torch, torchvision, wilds, sklearn, scipy, numpy, matplotlib

---

## 9. Evaluation Criteria

### Primary Metrics (Gate: SHOULD_WORK)

| Metric | Definition | Target | Level |
|--------|-----------|--------|-------|
| layer4_weight_diff | L2_norm(GroupDRO_layer4 − ERM_layer4) | > 1e-6 for all 3 seeds | CONFIRMED |
| gradient_norm_layer4 | mean L2 norm of layer4 gradients over 50 batches | > 0 for both ERM + GroupDRO | CONFIRMED |
| probe_acc_direction | GroupDRO probe acc < ERM probe acc | True (H-M3 proxy) | PROXY |
| p_value (one-sided) | paired t-test GroupDRO < ERM | < 0.10 (SUGGESTIVE) or < 0.05 (CONFIRMED) | SHOULD_WORK |

### Secondary Metrics

| Metric | Expected |
|--------|---------|
| backbone_to_head_ratio | > 0 (backbone modified relative to head) |
| DFR-ERM layer4 diff | ~0 (DFR uses frozen backbone — control) |
| SAM-ERM layer4 diff | > 0 (SAM also end-to-end trained) |
| ERM probe acc (background) | ~0.90 (confirmed H-P0) |

---

## 10. Out of Scope

- New model training (all checkpoints pre-trained)
- Architecture modifications to ResNet-50
- Layer-by-layer analysis below layer4 (layer1, layer2, layer3 comparisons)
- GroupDRO re-implementation (use existing checkpoints)
- Downloading new checkpoints (reuse H-P0/H-M1 cache)
- Full ablation over all possible grouping variables (background is the sole target)

---

## 11. Implementation Notes

- **Weight difference is DEFINITIVE:** If GroupDRO and ERM layer4 weights differ (they must — GroupDRO is end-to-end trained), gradient propagation is proven. This is not probabilistic.
- **DFR as control:** H-P0 showed DFR ≡ ERM (cosine_sim=1.000000). DFR-ERM layer4 diff should be ≈0 — use as negative control.
- **Load sequentially:** 12 models × ~100MB → load one pair at a time to avoid OOM.
- **Gradient analysis caution:** `model.train()` only for gradient computation; no weight updates; zero_grad() before each backward.
- **Contested landscape:** Document both Izmailov 2022 (head weighting) and Raymond 2026 (backbone reshaping) in report. H-M2 shows backbone IS modified; relative contribution is unresolved until H-M3.
- **Linear probe uses training set for fitting:** Extract features from train split, fit probe, evaluate on full test split (5,794 samples).

---

*Generated from: h-m2/02c_experiment_brief.md*
*Pipeline position: Phase 3 (Implementation Planning)*
*Gate: SHOULD_WORK — layer4 weight diff > 0 (all 3 seeds) + H-M3 proxy direction*
*Base hypothesis: H-M1 (COMPLETED, PASS)*
