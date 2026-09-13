# Logic Specification: H-E1 Gradient Abnormality Detection

**Hypothesis:** h-e1  
**Type:** EXISTENCE (PoC)  
**Gate:** MUST_WORK  
**Date:** 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation - no existing base hypothesis code  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - designing new APIs

---

## Overview

Four core algorithms for gradient abnormality detection:
1. **ERM training** with per-group accuracy tracking
2. **GradCAM gradient extraction** from layer4
3. **GAIA-Z metric** computation (zero-deflation ratio)
4. **Statistical testing** with effect size measurement

---

## 1. Training with Group Tracking

### API Signature

```python
def train_with_group_tracking(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    config: dict,
    device: torch.device
) -> Tuple[nn.Module, Dict[str, Any]]:
    """Train ResNet-50 with per-group accuracy tracking.
    
    Args:
        model: ResNet-50 with 2-class output
        train_loader: Waterbirds training data
        val_loader: Validation split
        config: {lr, momentum, weight_decay, epochs, patience}
        device: cuda or cpu
    
    Returns:
        trained_model: Best checkpoint (max WGA)
        metrics: {epoch, loss, avg_acc, group_acc[0-3], wga, minority_acc}
    """
```

### Pseudo-code

```
1. optimizer = SGD(model.parameters(), lr, momentum, weight_decay)
2. scheduler = CosineAnnealingLR(T_max=epochs)
3. best_wga = 0.0
4. patience_counter = 0

5. FOR epoch in range(epochs):
6.     model.train()
7.     FOR batch in train_loader:
8.         loss = CrossEntropyLoss(model(x), y)
9.         loss.backward()
10.        optimizer.step()
11.        optimizer.zero_grad()
12.    
13.    # Validation with per-group tracking
14.    group_correct = {0:0, 1:0, 2:0, 3:0}
15.    group_total = {0:0, 1:0, 2:0, 3:0}
16.    
17.    model.eval()
18.    FOR batch in val_loader:
19.        preds = model(x).argmax(dim=1)  # [B]
20.        FOR i in range(batch_size):
21.            g = metadata[i]['group']
22.            group_total[g] += 1
23.            IF preds[i] == y[i]:
24.                group_correct[g] += 1
25.    
26.    group_acc = {g: group_correct[g]/group_total[g] for g in [0,1,2,3]}
27.    wga = min(group_acc.values())
28.    minority_acc = (group_acc[1] + group_acc[2]) / 2
29.    avg_acc = sum(group_correct.values()) / sum(group_total.values())
30.    
31.    # Early stopping on WGA
32.    IF wga > best_wga:
33.        best_wga = wga
34.        save_checkpoint(model, optimizer, epoch, metrics)
35.        patience_counter = 0
36.    ELSE:
37.        patience_counter += 1
38.    
39.    IF patience_counter >= patience:
40.        BREAK
41.    
42.    scheduler.step()
43.
44. # Final validation
45. ASSERT wga < 0.80, "Spurious learning not achieved"
46. ASSERT minority_acc >= 0.60, "A1 assumption violated"
47. ASSERT avg_acc > 0.95, "Model underfit"
48.
49. RETURN model, metrics
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x | [128, 3, 224, 224] | Batch of images |
| y | [128] | Class labels |
| preds | [128] | Predicted classes |
| metadata | [128] | Group IDs per sample |

### Edge Cases

- **WGA ≥ 80%:** Retrain with different seed
- **Minority acc < 60%:** Flag A1 violation, ABORT experiment
- **OOM:** Reduce batch_size from 128 → 64

---

## 2. GradCAM Gradient Extraction

### API Signature

```python
def extract_gradcam_gradients(
    model: nn.Module,
    test_loader: DataLoader,
    device: torch.device
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract raw gradients from GradCAM for all test samples.
    
    Args:
        model: Trained ResNet-50
        test_loader: Waterbirds test split (5794 samples)
        device: cuda or cpu
    
    Returns:
        gradients: [5794, 2048, 7, 7] raw gradient tensors
        group_ids: [5794] group membership
        predictions: [5794] predicted classes
    """
```

### Pseudo-code

```
1. target_layers = [model.layer4]
2. cam = GradCAM(model, target_layers)
3. 
4. gradients_list = []
5. group_ids_list = []
6. predictions_list = []
7. 
8. model.eval()
9. FOR batch in test_loader:
10.    x, y, metadata = batch  # x: [B,3,224,224]
11.    x = x.to(device)
12.    
13.    # Forward pass to get prediction
14.    output = model(x)  # [B, 2]
15.    pred_class = output.argmax(dim=1)  # [B]
16.    
17.    # Extract gradients per sample (GradCAM requires batch_size=1)
18.    FOR i in range(x.shape[0]):
19.        sample = x[i:i+1]  # [1,3,224,224]
20.        target = [ClassifierOutputTarget(pred_class[i].item())]
21.        
22.        # Compute GradCAM (triggers backward pass)
23.        _ = cam(input_tensor=sample, targets=target)
24.        
25.        # Extract raw gradients from internal storage
26.        raw_grad = cam.activations_and_grads.gradients[0]  # [1,2048,7,7]
27.        raw_grad = raw_grad.detach().cpu().numpy()
28.        
29.        gradients_list.append(raw_grad[0])  # [2048,7,7]
30.        group_ids_list.append(metadata[i]['group'].item())
31.        predictions_list.append(pred_class[i].item())
32.    
33.    # Clear gradient cache every 100 samples to prevent OOM
34.    IF len(gradients_list) % 100 == 0:
35.        torch.cuda.empty_cache()
36.
37. gradients = np.stack(gradients_list)  # [5794,2048,7,7]
38. group_ids = np.array(group_ids_list)  # [5794]
39. predictions = np.array(predictions_list)  # [5794]
40.
41. RETURN gradients, group_ids, predictions
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| sample | [1, 3, 224, 224] | Single image |
| output | [1, 2] | Logits |
| raw_grad | [1, 2048, 7, 7] | Layer4 gradients |
| gradients | [5794, 2048, 7, 7] | All test samples |

### Edge Cases

- **OOM during collection:** Process in batches of 100, clear cache
- **GradCAM API change:** Pin `pytorch-grad-cam==1.5.0`
- **Gradient all-zeros:** Check model.requires_grad=True

**Applied:** Standard PyTorch GradCAM pattern with per-sample processing

---

## 3. GAIA-Z Computation

### API Signature

```python
def compute_gaia_z(
    gradients: np.ndarray,
    epsilon: float = 1e-6
) -> np.ndarray:
    """Compute GAIA-Z zero-deflation ratio.
    
    Args:
        gradients: [N, C, H, W] gradient tensors
        epsilon: Near-zero threshold
    
    Returns:
        gaia_z: [N] scores in [0, 1]
    """
```

### Pseudo-code

```
1. N = gradients.shape[0]
2. gaia_z = np.zeros(N)
3. 
4. FOR i in range(N):
5.     flat_grad = gradients[i].flatten()  # [100352] = 2048×7×7
6.     
7.     # Count near-zero elements (vectorized)
8.     near_zero_mask = np.abs(flat_grad) < epsilon
9.     near_zero_count = np.sum(near_zero_mask)
10.    
11.    # Compute ratio
12.    total_elements = flat_grad.size
13.    gaia_z[i] = near_zero_count / total_elements
14.
15. # Validation
16. ASSERT np.all(gaia_z >= 0.0) and np.all(gaia_z <= 1.0)
17. ASSERT np.std(gaia_z) > 0.01, "Degenerate GAIA-Z (no variance)"
18. 
19. RETURN gaia_z
```

### Vectorized Implementation

```python
# More efficient version
def compute_gaia_z_vectorized(gradients: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
    # gradients: [N, C, H, W]
    N = gradients.shape[0]
    flat_grads = gradients.reshape(N, -1)  # [N, C*H*W]
    near_zero_counts = np.sum(np.abs(flat_grads) < epsilon, axis=1)  # [N]
    total_elements = flat_grads.shape[1]
    gaia_z = near_zero_counts / total_elements  # [N]
    return gaia_z
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| gradients[i] | [2048, 7, 7] | Single gradient tensor |
| flat_grad | [100352] | Flattened |
| gaia_z | [5794] | One score per sample |

### Edge Cases

- **All-zero gradients:** GAIA-Z = 1.0 (valid, indicates complete scattering)
- **No near-zeros:** GAIA-Z = 0.0 (valid, indicates normal gradient flow)
- **Degenerate (std=0):** Raise error, likely model/data issue

**Applied:** Vectorized numpy for numerical stability

---

## 4. Statistical Test

### API Signature

```python
def perform_statistical_test(
    gaia_z_scores: np.ndarray,
    group_ids: np.ndarray,
    minority_groups: List[int] = [1, 2],
    majority_groups: List[int] = [0, 3]
) -> Dict[str, Any]:
    """Two-sample t-test with effect size.
    
    Args:
        gaia_z_scores: [N] GAIA-Z values
        group_ids: [N] group membership
        minority_groups: Group IDs for minority
        majority_groups: Group IDs for majority
    
    Returns:
        results: {
            minority_mean, majority_mean, divergence,
            p_value, t_statistic, cohens_d,
            n_minority, n_majority,
            pass_primary, pass_secondary, gate_pass
        }
    """
```

### Pseudo-code

```
1. # Separate scores by group type
2. minority_mask = np.isin(group_ids, minority_groups)
3. majority_mask = np.isin(group_ids, majority_groups)
4. 
5. minority_scores = gaia_z_scores[minority_mask]  # [N_minority]
6. majority_scores = gaia_z_scores[majority_mask]  # [N_majority]
7. 
8. # Check non-empty
9. ASSERT len(minority_scores) > 0, "No minority samples"
10. ASSERT len(majority_scores) > 0, "No majority samples"
11.
12. # Compute means
13. mean_minority = np.mean(minority_scores)
14. mean_majority = np.mean(majority_scores)
15. divergence = mean_minority - mean_majority
16.
17. # Two-sample Welch's t-test (unequal variance)
18. t_statistic, p_value = scipy.stats.ttest_ind(
19.     minority_scores, 
20.     majority_scores, 
21.     equal_var=False
22. )
23.
24. # Cohen's d effect size
25. var_minority = np.var(minority_scores, ddof=1)
26. var_majority = np.var(majority_scores, ddof=1)
27. pooled_std = np.sqrt((var_minority + var_majority) / 2)
28.
29. # Numerical stability check
30. IF pooled_std < 1e-10:
31.     cohens_d = 0.0  # Degenerate case
32. ELSE:
33.     cohens_d = divergence / pooled_std
34.
35. # Gate evaluation
36. pass_primary = (divergence >= 0.2) AND (p_value < 0.01)
37. pass_secondary = (cohens_d >= 0.8)
38. gate_pass = pass_primary AND pass_secondary
39.
40. results = {
41.     'minority_mean': mean_minority,
42.     'majority_mean': mean_majority,
43.     'divergence': divergence,
44.     'p_value': p_value,
45.     't_statistic': t_statistic,
46.     'cohens_d': cohens_d,
47.     'n_minority': len(minority_scores),
48.     'n_majority': len(majority_scores),
49.     'pass_primary': pass_primary,
50.     'pass_secondary': pass_secondary,
51.     'gate_pass': gate_pass
52. }
53.
54. RETURN results
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| gaia_z_scores | [5794] | All test samples |
| minority_scores | [~1300] | Groups 1,2 |
| majority_scores | [~4500] | Groups 0,3 |

### Edge Cases

- **Empty groups:** Raise AssertionError with diagnostic
- **Pooled std = 0:** Set Cohen's d = 0, flag degenerate distribution
- **p-value = NaN:** Check for constant arrays, numerical issues

**Applied:** Welch's t-test from scipy.stats for unequal variance

---

## 5. Gate Evaluation Logic

### Primary Criteria

```python
# Both conditions must be met
primary_pass = (divergence >= 0.2) and (p_value < 0.01)
```

### Secondary Criteria

```python
# Large effect size required
secondary_pass = (cohens_d >= 0.8)
```

### Overall Gate

```python
gate_pass = primary_pass and secondary_pass

if gate_pass:
    print("✓ H-E1 PASSED: Gradient abnormality detected")
    proceed_to_h_m_integrated()
else:
    print("✗ H-E1 FAILED: ABANDON gradient abnormality approach")
    if divergence < 0.2:
        print(f"  Divergence insufficient: {divergence:.4f}")
    if p_value >= 0.01:
        print(f"  Not significant: p={p_value:.4e}")
    if cohens_d < 0.8:
        print(f"  Effect size weak: d={cohens_d:.2f}")
```

---

## 6. Data Flow

```
Waterbirds Dataset (5794 test samples)
    ↓
train_with_group_tracking() → trained_model.pth + metrics
    ↓ (validation: WGA<80%, minority_acc≥60%)
extract_gradcam_gradients() → gradients [5794,2048,7,7]
    ↓
compute_gaia_z() → gaia_z_scores [5794]
    ↓ (validation: std>0.01, range[0,1])
perform_statistical_test() → statistical_results.json
    ↓
Gate Decision: PASS → h-m-integrated | FAIL → ABANDON
```

---

## 7. Numerical Stability

### GAIA-Z Computation
- Use `np.abs(grad) < epsilon` to avoid signed comparison
- Epsilon = 1e-6 balances FP32 noise vs meaningful zeros

### Cohen's d Computation
- Check `pooled_std < 1e-10` before division
- Use ddof=1 for unbiased variance estimation

### Gradient Extraction
- Clear CUDA cache every 100 samples
- Detach tensors before numpy conversion

---

## 8. Performance Constraints

| Operation | Target | Strategy |
|-----------|--------|----------|
| Training | ≤3 hours | Batch size 128, early stop |
| Gradient extraction | ≤20 min | Per-sample processing |
| GAIA-Z computation | ≤1 min | Vectorized numpy |
| Statistical test | ≤1 sec | scipy.stats builtin |

---

## 9. Validation Checks

### Post-Training
```python
assert wga < 0.80, "WGA too high - spurious learning failed"
assert minority_acc >= 0.60, "A1 violation - minority acc too low"
assert avg_acc > 0.95, "Model underfit"
```

### Post-GAIA-Z
```python
assert np.std(gaia_z) > 0.01, "Degenerate GAIA-Z distribution"
assert 0.0 <= np.min(gaia_z) <= np.max(gaia_z) <= 1.0, "Invalid range"
assert 0.1 < np.median(gaia_z) < 0.9, "Suspicious median"
```

### Statistical Test
```python
assert len(minority_scores) > 0 and len(majority_scores) > 0, "Empty groups"
assert not np.isnan(p_value), "NaN p-value - check distributions"
```

---

## 10. Output Format

### Training Metrics (CSV)
```
epoch,loss,avg_acc,group_0_acc,group_1_acc,group_2_acc,group_3_acc,wga,minority_acc
0,0.45,0.87,0.92,0.65,0.70,0.95,0.65,0.675
1,0.32,0.93,0.96,0.68,0.72,0.97,0.68,0.700
...
```

### GAIA-Z Scores (CSV)
```
sample_id,group_id,is_minority,gaia_z,prediction,ground_truth,correct
0,0,False,0.32,0,0,True
1,1,True,0.54,0,0,True
...
```

### Statistical Results (JSON)
```json
{
    "minority_mean": 0.48,
    "majority_mean": 0.25,
    "divergence": 0.23,
    "p_value": 0.0032,
    "t_statistic": 2.95,
    "cohens_d": 0.87,
    "n_minority": 1299,
    "n_majority": 4495,
    "pass_primary": true,
    "pass_secondary": true,
    "gate_pass": true
}
```

---

**Document Status:** Complete  
**Total Length:** ~550 lines  
**Algorithmic Coverage:** 4/4 core functions specified  
**Edge Cases:** 12 identified and mitigated
