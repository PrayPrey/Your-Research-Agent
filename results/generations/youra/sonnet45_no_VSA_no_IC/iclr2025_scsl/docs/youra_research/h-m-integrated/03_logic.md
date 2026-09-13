# Logic Design: H-M-INTEGRATED
## Causal Mechanism Validation

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM  
**Generated:** 2026-08-20  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-e1 code  
**Analyzed Path**: /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scsl/h-e1/  
**Relevant Symbols**: GradCAMExtractor, compute_gaia_z, perform_statistical_test, GroupTracker

---

## Component 1: Correlation Rate Resampler

### API Signatures

```python
def resample_waterbirds(
    metadata_df: pd.DataFrame,
    target_corr: float,
    seed: int = 42
) -> pd.DataFrame:
    """Resample train set to achieve target correlation.
    
    Args:
        metadata_df: cols=['y', 'place', 'split'], values y∈{0,1}, place∈{0,1}
        target_corr: correlation rate in [0.5, 1.0]
        seed: RNG seed
    
    Returns:
        resampled_df: stratified sample with target P(place|y)
    """
```

### Pseudo-code

```
1. Filter to train split: df_train = metadata_df[split == 'train']
2. Define groups: group_id = y * 2 + place  # {0,1,2,3}
3. Compute target counts per group:
   - Total samples N = len(df_train)
   - Majority groups (0,3): n_maj = (N * target_corr) / 2
   - Minority groups (1,2): n_min = (N * (1 - target_corr)) / 2
   - Round to integers, ensure sum == N
4. Resample each group with replacement to target counts:
   - For g in [0,1,2,3]: sample n_target[g] rows from df_train[group_id == g]
5. Concat resampled groups, shuffle by seed
6. Return resampled_df
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| metadata_df | [5794, 3] | Train metadata |
| resampled_df | [5794, 3] | Same size, different distribution |
| group_counts | [4] | Samples per group |

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Group count computation | Compute target counts per group from correlation rate |
| L-1-2 | Stratified resampling | Sample with replacement per group |
| L-1-3 | Deterministic shuffle | Seed-based shuffle of concatenated groups |
| L-1-4 | Validation | Verify empirical correlation == target ± 2% |
| L-1-5 | Edge case handling | Handle groups with 0 original samples (fallback to original) |

---

## Component 2: Background Swapper

### API Signatures

```python
class BackgroundSwapper:
    def __init__(
        self,
        seg_model_name: str = "nvidia/segformer-b5-finetuned-ade-640-640",
        device: str = "cuda"
    ):
        """Initialize segmentation model."""
        from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
        self.processor = SegformerImageProcessor.from_pretrained(seg_model_name)
        self.model = SegformerForSemanticSegmentation.from_pretrained(seg_model_name)
        self.model.to(device).eval()
        self.device = device
        self.bird_class_id = 3  # ADE20K 'bird' class
    
    def segment_bird(self, image: Image.Image) -> np.ndarray:
        """Extract bird mask.
        
        Args:
            image: PIL RGB [H, W, 3]
        
        Returns:
            mask: binary mask [H, W], dtype=float32 in [0, 1]
        """
    
    def swap_background(
        self,
        foreground_img: Image.Image,
        background_img: Image.Image
    ) -> Image.Image:
        """Composite foreground onto background.
        
        Args:
            foreground_img: minority sample
            background_img: majority sample (same y, opposite place)
        
        Returns:
            augmented: PIL Image [224, 224, 3]
        """
```

### Pseudo-code

**segment_bird:**
```
1. Preprocess image: inputs = processor(images=image, return_tensors="pt").to(device)
2. Forward pass: outputs = model(**inputs)  # logits: [1, num_classes, H/4, W/4]
3. Upsample to original size: logits_upsampled = interpolate(outputs.logits, size=(H, W))
4. Get class predictions: pred_classes = argmax(logits_upsampled, dim=1)[0]  # [H, W]
5. Extract bird mask: mask = (pred_classes == bird_class_id).float().cpu().numpy()
6. Morphological ops: dilate(mask, kernel=5x5) then erode(mask, kernel=3x3) to smooth edges
7. Return mask
```

**swap_background:**
```
1. Resize images to [224, 224]: fg, bg = resize(foreground_img, bg_img)
2. Extract mask: mask = segment_bird(fg)  # [224, 224]
3. Expand to 3 channels: mask_3ch = stack([mask, mask, mask], axis=2)  # [224, 224, 3]
4. Convert to arrays: fg_arr, bg_arr = np.array(fg), np.array(bg)
5. Composite: result = fg_arr * mask_3ch + bg_arr * (1 - mask_3ch)  # [224, 224, 3]
6. Convert to PIL: return Image.fromarray(result.astype('uint8'))
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| inputs['pixel_values'] | [1, 3, H, W] | Preprocessed image |
| logits | [1, num_classes, H/4, W/4] | Segmentation logits |
| pred_classes | [H, W] | Class per pixel |
| mask | [224, 224] | Binary bird mask |
| result | [224, 224, 3] | Composited RGB |

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | SegFormer integration | Load model and processor from HuggingFace |
| L-2-2 | Foreground extraction | Get bird mask via semantic segmentation |
| L-2-3 | Mask refinement | Morphological ops to smooth mask edges |
| L-2-4 | Background sampling | Random sample from majority pool (same y, opposite place) |
| L-2-5 | Alpha compositing | Blend foreground onto background using mask |
| L-2-6 | Batch processing | Process 200 samples with progress bar |
| L-2-7 | Quality check | Compute IoU on 10 random samples, validate > 0.7 |
| L-2-8 | Fallback handling | If segmentation fails (IoU < 0.5), use center crop as mask |

---

## Component 3: Correlation Analyzer

### API Signatures

```python
def analyze_correlation(
    wga_values: np.ndarray,
    gaia_divergences: np.ndarray
) -> Dict[str, float]:
    """Compute Pearson correlation + statistical test.
    
    Args:
        wga_values: [10] worst-group accuracies
        gaia_divergences: [10] minority-majority GAIA-Z gaps
    
    Returns:
        {
            'rho': float,
            'p_value': float,
            'pass_primary': bool (rho > 0.7 AND p < 0.05)
        }
    """

def plot_correlation_scatter(
    wga_values: np.ndarray,
    gaia_divergences: np.ndarray,
    save_path: str
) -> None:
    """Scatter plot with trendline."""
```

### Pseudo-code

**analyze_correlation:**
```
1. Validate inputs: assert len(wga_values) == len(gaia_divergences) == 10
2. Compute Pearson: rho, p_value = scipy.stats.pearsonr(gaia_divergences, wga_values)
3. Check gate: pass_primary = (rho > 0.7) and (p_value < 0.05)
4. Return dict
```

**plot_correlation_scatter:**
```
1. Create figure: fig, ax = plt.subplots(figsize=(8, 6))
2. Scatter plot: ax.scatter(gaia_divergences, wga_values, s=100, alpha=0.7)
3. Fit trendline: slope, intercept = np.polyfit(gaia_divergences, wga_values, deg=1)
4. Plot trendline: ax.plot(x_line, slope*x_line + intercept, 'r--', label=f'ρ={rho:.2f}')
5. Labels: ax.set_xlabel('GAIA Divergence'), ax.set_ylabel('WGA')
6. Save: plt.savefig(save_path, dpi=150, bbox_inches='tight')
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Pearson computation | scipy.stats.pearsonr wrapper with validation |
| L-3-2 | Scatter plot | Matplotlib visualization with trendline |
| L-3-3 | Results export | Save to JSON + plot to PNG |

---

## Component 4: Paired t-test for Augmentation

### API Signatures

```python
def analyze_augmentation_effect(
    original_gaia_z: np.ndarray,
    augmented_gaia_z: np.ndarray
) -> Dict[str, Any]:
    """Paired t-test for GAIA-Z reduction.
    
    Args:
        original_gaia_z: [200] baseline minority GAIA-Z
        augmented_gaia_z: [200] post-augmentation GAIA-Z
    
    Returns:
        {
            'mean_reduction_pct': float,
            'p_value': float,
            'cohens_d': float,
            'pass_primary': bool (reduction >= 30% AND p < 0.01)
        }
    """
```

### Pseudo-code

```
1. Validate: assert len(original_gaia_z) == len(augmented_gaia_z) == 200
2. Compute reduction: reduction = (original_gaia_z - augmented_gaia_z) / original_gaia_z * 100
3. Mean reduction: mean_reduction_pct = np.mean(reduction)
4. Paired t-test: t_stat, p_value = scipy.stats.ttest_rel(original_gaia_z, augmented_gaia_z)
5. Effect size: cohens_d = np.mean(reduction) / np.std(reduction, ddof=1)
6. Gate check: pass_primary = (mean_reduction_pct >= 30.0) and (p_value < 0.01)
7. Return dict
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Paired t-test | scipy.stats.ttest_rel with reduction computation |
| L-4-2 | Effect size | Cohen's d for within-subject design |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From h-e1 Code)

```python
# From: /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scsl/h-e1/gaia_utils.py

class GradCAMExtractor:
    def __init__(self, model: nn.Module, target_layer: nn.Module, device: torch.device):
        """Initialize GradCAM wrapper."""
    
    def extract_single(self, image: torch.Tensor, target_class: int) -> np.ndarray:
        """Extract raw gradients.
        
        Args:
            image: [1, 3, 224, 224] tensor
            target_class: predicted class ID
        
        Returns:
            gradients: [2048, 7, 7] from layer4
        """

def compute_gaia_z(gradients: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
    """Compute GAIA-Z zero-deflation ratio.
    
    Args:
        gradients: [N, C, H, W] gradient tensors
        epsilon: near-zero threshold
    
    Returns:
        gaia_z: [N] scores in [0, 1]
    """

def perform_statistical_test(
    gaia_z_scores: np.ndarray,
    group_ids: np.ndarray,
    minority_groups: List[int] = [1, 2],
    majority_groups: List[int] = [0, 3]
) -> Dict[str, Any]:
    """Two-sample t-test with divergence.
    
    Returns:
        {
            'minority_mean': float,
            'majority_mean': float,
            'divergence': float,
            'p_value': float,
            'cohens_d': float,
            'gate_pass': bool
        }
    """

class GroupTracker:
    """Per-group accuracy tracking."""
    
    def update(self, predictions: torch.Tensor, labels: torch.Tensor, group_ids: torch.Tensor):
        """Update batch results."""
    
    def compute_metrics(self) -> Dict[str, float]:
        """Returns: {group_0_acc, ..., wga, minority_acc, majority_acc, avg_acc}"""

def create_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """ResNet-50 with modified FC layer."""

def get_gradcam_layer(model: nn.Module) -> nn.Module:
    """Return model.layer4."""
```

**Verified from**: h-e1/gaia_utils.py (actual implementation)

---

## Implementation Notes

### Applied Patterns

**Component 1 (Resampler)**: Standard pandas stratified sampling with replacement  
**Component 2 (Swapper)**: HuggingFace transformers + PIL compositing  
**Component 3 (Analyzer)**: scipy.stats.pearsonr + matplotlib  
**Component 4 (t-test)**: scipy.stats.ttest_rel  

### Edge Cases

1. **Resampler**: Groups with 0 samples in original data → use original distribution
2. **Swapper**: Segmentation IoU < 0.5 → fallback to center 80% crop as mask
3. **Correlation**: Perfect correlation (rho=1.0) → numerical stability check
4. **t-test**: Zero variance in paired differences → handle division by zero

### Dependencies

- pandas, numpy (data manipulation)
- scipy (statistical tests)
- transformers (SegFormer)
- PIL (image compositing)
- matplotlib (visualization)
- torch, torchvision (inherited from h-e1)
- pytorch_grad_cam (inherited from h-e1)

---

## Metadata

- **Document Type:** Logic Design
- **Phase:** 3 (Implementation Planning)
- **Status:** READY FOR IMPLEMENTATION
- **Total Subtasks:** 18 (within budget)
- **External Dependencies:** h-e1 codebase (GAIA-Z, GradCAM, training loop)
