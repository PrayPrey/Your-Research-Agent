# Architecture: H-M-INTEGRATED
## Causal Mechanism Validation for Gradient Abnormality

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM (MUST_WORK gate)  
**Prerequisites:** h-e1 (COMPLETED)  
**Generated:** 2026-08-20  

**Applied KB Patterns:** Multi-model training sweep, WILDS dataset integration

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** patterns found from h-e1 code  
**Analyzed Path:** `h-e1/` (actual code structure)  
**Findings:** Reusable GAIA-Z pipeline (gaia_utils.py), Waterbirds loader (waterbirds_dataset.py), training loop (train_gaia.py)

---

## 1. System Overview

**Goal:** Validate 4-step causal mechanism (correlation rate → WGA → GAIA divergence → augmentation causality) across 10 models.

**Components:** 
- Resampler (correlation rate control)
- Multi-trainer (10 ResNet-50 models)
- GAIA extractor (reused from h-e1)
- Background swapper (SegFormer-based)
- Correlation analyzer (scipy.stats)

**Data Flow:**
```
Waterbirds metadata → Resampler (10 correlation rates) → Multi-trainer → 10 checkpoints
                                                                              ↓
                                      Test set (4795) → GAIA extractor → Divergence CSV
                                                                              ↓
                                                          Correlation analyzer → Results JSON
```

---

## 2. Module Structure

### 2.1 Resampler (`utils/resampler.py`)

**Dependencies:** pandas, numpy

```python
def resample_waterbirds(
    metadata_df: pd.DataFrame,
    target_correlation: float,
    seed: int = 42
) -> pd.DataFrame:
    """
    Stratified sampling to achieve target P(place|y).
    
    Args:
        metadata_df: columns [y, place, split, img_filename]
        target_correlation: float in [0.5, 1.0]
        seed: random seed
    
    Returns:
        resampled_df: subset achieving target correlation
    """
    ...
```

### 2.2 Background Swapper (`utils/augmentation.py`)

**Dependencies:** transformers, PIL, torch

```python
class BackgroundSwapper:
    def __init__(self, device: str = "cuda"):
        self.segmenter = AutoModelForSemanticSegmentation.from_pretrained(
            "nvidia/segformer-b5-finetuned-ade-640-640"
        )
        self.processor = AutoImageProcessor.from_pretrained(...)
    
    def segment_bird(self, image: PIL.Image) -> np.ndarray:
        """Extract bird mask (binary)."""
        ...
    
    def swap_background(
        self,
        image: PIL.Image,
        background_pool: List[PIL.Image]
    ) -> PIL.Image:
        """Composite foreground onto random background."""
        ...
```

### 2.3 Correlation Analyzer (`utils/analysis.py`)

**Dependencies:** scipy, matplotlib

```python
def compute_correlation(
    wga_values: np.ndarray,
    gaia_divergences: np.ndarray
) -> dict:
    """
    Pearson correlation + statistical test.
    
    Returns:
        {rho: float, p_value: float, ci_95: (float, float)}
    """
    ...

def plot_correlation_scatter(
    wga_values: np.ndarray,
    gaia_divergences: np.ndarray,
    save_path: str
):
    """Scatter plot with trendline."""
    ...
```

### 2.4 Multi-Model Trainer (`train_sweep.py`)

**Dependencies:** torch, argparse, gaia_utils (h-e1)

```python
def train_single_model(
    correlation_rate: float,
    seed: int,
    output_dir: str,
    config: ExperimentConfig
) -> str:
    """
    Train one ResNet-50 model.
    
    Returns:
        checkpoint_path: str
    """
    ...

def run_correlation_sweep(
    correlation_rates: List[float],
    base_config: ExperimentConfig,
    output_dir: str
):
    """Train 10 models sequentially."""
    ...
```

### 2.5 GAIA Divergence Extractor (`extract_gaia.py`)

**Dependencies:** gaia_utils (h-e1), torch

```python
def extract_gaia_for_model(
    model_path: str,
    test_loader: DataLoader,
    device: str
) -> pd.DataFrame:
    """
    Compute GAIA-Z for all test samples.
    
    Returns:
        df: columns [sample_id, y, place, group, gaia_z, prediction]
    """
    ...

def compute_divergence(gaia_df: pd.DataFrame) -> float:
    """
    divergence = mean(minority GAIA-Z) - mean(majority GAIA-Z)
    minority: groups [1, 2], majority: groups [0, 3]
    """
    ...
```

### 2.6 Augmentation Pipeline (`run_augmentation_test.py`)

**Dependencies:** BackgroundSwapper, extract_gaia

```python
def select_minority_samples(
    test_df: pd.DataFrame,
    model_predictions: pd.DataFrame,
    n_per_group: int = 100
) -> pd.DataFrame:
    """Select 100 waterbird-land + 100 landbird-water correctly classified."""
    ...

def run_augmentation_experiment(
    model_path: str,
    minority_samples: pd.DataFrame,
    background_pool_dir: str
) -> dict:
    """
    Returns:
        {
            original_gaia_mean: float,
            augmented_gaia_mean: float,
            reduction_pct: float,
            t_statistic: float,
            p_value: float
        }
    """
    ...
```

---

## 3. External Dependencies (h-e1)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ExperimentConfig | `from h_e1.gaia_utils import ExperimentConfig` | `h-e1/gaia_utils.py` |
| set_seed | `from h_e1.gaia_utils import set_seed` | `h-e1/gaia_utils.py` |
| create_resnet50 | `from h_e1.gaia_utils import create_resnet50` | `h-e1/gaia_utils.py` |
| compute_gaia_z | `from h_e1.gaia_utils import compute_gaia_z` | `h-e1/gaia_utils.py` |
| extract_gradcam | `from h_e1.gaia_utils import extract_gradcam` | `h-e1/gaia_utils.py` |
| WaterbirdsDataset | `from h_e1.waterbirds_dataset import WaterbirdsDataset` | `h-e1/waterbirds_dataset.py` |
| get_train_transforms | `from h_e1.gaia_utils import get_train_transforms` | `h-e1/gaia_utils.py` |
| get_eval_transforms | `from h_e1.gaia_utils import get_eval_transforms` | `h-e1/gaia_utils.py` |

**Verified from:** `h-e1/` actual implementation

---

## 4. File Organization

```
h-m-integrated/
├── code/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── resampler.py          # Correlation rate resampling
│   │   ├── augmentation.py       # BackgroundSwapper
│   │   └── analysis.py           # Pearson correlation, plotting
│   ├── train_sweep.py            # Multi-model trainer
│   ├── extract_gaia.py           # GAIA-Z extraction
│   ├── run_augmentation_test.py  # Experiment 2
│   ├── run_correlation_test.py   # Experiment 1
│   └── config.py                 # Hyperparameters (copy from h-e1)
├── checkpoints/                  # 10 model checkpoints
│   ├── model_corr_50.pt
│   ├── model_corr_55.pt
│   └── ...
├── outputs/
│   ├── gaia_divergences.csv      # 10 rows: [corr_rate, wga, divergence]
│   ├── augmentation_results.json
│   └── correlation_plot.png
└── tests/
    ├── test_resampler.py
    ├── test_augmentation.py
    └── test_analysis.py
```

---

## 5. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Setup & Resampler | Project structure + correlation rate resampling logic | 8 | 2(setup)+3(resampler)+2(tests)+1(integration) |
| E-2 | Background Swapper | SegFormer integration + compositing pipeline | 11 | 4(segmentation)+4(compositing)+2(tests)+1(pool builder) |
| E-3 | Multi-Model Training | 10-model orchestrator + checkpoint manager | 9 | 3(orchestrator)+2(checkpoint)+3(training loop)+1(logging) |
| E-4 | GAIA Extraction | Extract GAIA-Z for 10 models × 4795 test samples | 7 | 3(extraction)+2(divergence calc)+1(CSV export)+1(tests) |
| E-5 | Correlation Analyzer | Pearson correlation + plotting + statistical tests | 6 | 2(pearsonr)+2(plotting)+1(CI)+1(tests) |
| E-6 | Augmentation Experiment | Sample selection + swap + paired t-test | 8 | 3(sample selection)+2(swap pipeline)+2(t-test)+1(validation) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E-2, E-3], Low(4-8): [E-1, E-4, E-5, E-6]

**Total Complexity:** 49 (Medium tier)

---

## 6. Dependency Graph

```
PyTorch 2.0+ ──┐
               ├──> ResNet-50 training
torchvision ───┘

transformers ──> SegFormer-B5 (segmentation)

scipy.stats ───> Pearson correlation, t-test

pandas ────────> Metadata resampling, CSV export

matplotlib ────> Correlation scatter plot

PIL ───────────> Image compositing

h-e1 modules ──> GAIA-Z, GradCAM, ExperimentConfig
```

---

## 7. Interface Contracts

### 7.1 Resampler API
```python
# Input: metadata DataFrame (5794 train samples)
# Output: resampled DataFrame (size varies by correlation rate)
# Constraint: |achieved_corr - target_corr| < 0.02
```

### 7.2 BackgroundSwapper API
```python
# Input: minority image (PIL), background pool (List[PIL.Image])
# Output: augmented image (PIL)
# Constraint: Foreground pixel diff < 5%, background fully replaced
```

### 7.3 GAIA Extractor API
```python
# Input: model checkpoint path, test DataLoader (4795 samples)
# Output: DataFrame [sample_id, group, gaia_z, prediction]
# Constraint: All samples processed, GAIA-Z ∈ [0, 1]
```

### 7.4 Correlation Analyzer API
```python
# Input: wga_values (10,), gaia_divergences (10,)
# Output: {rho: float, p_value: float, ci_95: (float, float)}
# Constraint: p_value computed via two-tailed test
```

---

## 8. Computational Requirements

### 8.1 Training Phase (Experiment 1)
- **10 models × 300 epochs × ~45 batches/epoch:** 135,000 iterations
- **GPU hours:** ~30 hours (single V100)
- **Memory:** 16GB VRAM per model (ResNet-50 + batch_size=128)
- **Parallelizable:** Yes (10 independent training runs)

### 8.2 GAIA Extraction
- **10 models × 4795 test samples:** 47,950 GradCAM extractions
- **GPU hours:** ~2 hours (single V100)
- **Memory:** 8GB VRAM (batch processing)

### 8.3 Augmentation Test (Experiment 2)
- **Segmentation:** 200 samples × SegFormer-B5 ~ 5 minutes (GPU)
- **Compositing:** 200 samples × PIL ~ 2 minutes (CPU)
- **GAIA-Z:** 400 samples (200 original + 200 augmented) ~ 10 minutes (GPU)
- **Total:** ~20 minutes

### 8.4 Total Budget
- **GPU hours:** ~32 hours
- **Storage:** ~5GB (10 checkpoints + GAIA-Z CSVs)
- **CPU:** Negligible (resampling, analysis)

---

## 9. Key Design Decisions

### 9.1 Why Sequential Training?
- **Rationale:** Avoid GPU contention, simplify debugging
- **Trade-off:** Longer wall-clock time (parallelizable on multi-GPU cluster)

### 9.2 Why SegFormer-B5 Over Bounding Boxes?
- **Rationale:** Pixel-level masks more accurate than manual bboxes (GroupDRO baseline)
- **Fallback:** If segmentation fails (IoU < 0.7), use bboxes

### 9.3 Why Paired t-test Over Independent?
- **Rationale:** Same samples (original vs augmented) → paired design
- **Statistical power:** Higher power for detecting reduction

---

## 10. Validation Checkpoints

### 10.1 Resampler Validation
- **Unit test:** Verify |achieved_corr - target_corr| < 0.02
- **Integration test:** Train 2 models (50%, 95%), verify WGA(50%) > WGA(95%)

### 10.2 Segmentation Quality
- **Manual inspection:** Visualize 10 random bird masks
- **Gate:** IoU > 0.7 on validation samples

### 10.3 GAIA Extraction Sanity
- **Range check:** All GAIA-Z ∈ [0, 1]
- **Minority check:** minority_gaia_mean > majority_gaia_mean (90% correlation model)

### 10.4 Statistical Tests
- **Two-tailed p-values:** α = 0.05
- **Effect sizes:** Cohen's d for augmentation test
- **Confidence intervals:** 95% for all estimates

---

## 11. Risk Mitigation

### 11.1 Training Instability
- **Risk:** Hyperparameter sensitivity across correlation rates
- **Mitigation:** Fixed hyperparameters (from h-e1), early stopping
- **Detection:** Monitor worst-group val accuracy per model

### 11.2 Segmentation Failure
- **Risk:** SegFormer produces low-quality masks
- **Mitigation:** Manual inspection, IoU threshold, fallback to bboxes
- **Detection:** IoU < 0.7 triggers fallback

### 11.3 Correlation Fails (ρ < 0.7)
- **Risk:** Step 1→3 mechanism breaks
- **Action:** Investigate which step fails (WGA vs correlation rate, GAIA vs WGA)
- **Fallback:** Reframe hypothesis (detection-only)

### 11.4 Augmentation Fails (reduction < 30%)
- **Risk:** Spurious conflict not causal
- **Action:** Visual inspection of swapped images, ablation with manual swap
- **Fallback:** Pivot to detection-only (abandon h-m-mitigate)

---

## 12. Success Criteria

**Primary Metrics:**
1. Pearson ρ(GAIA_divergence, WGA) > 0.7, p < 0.05 (Experiment 1)
2. GAIA-Z reduction ≥ 30%, p < 0.01 (Experiment 2)
3. Minority accuracy ≥ 0.60 (Experiment 3)

**Gate Logic:** (1 AND 2 AND 3) → PASS → Proceed to h-m-mitigate

**Failure Modes:**
- **Correlation fails:** Investigate Step 1 (WGA vs correlation) or Step 4 (GAIA vs WGA)
- **Augmentation fails:** Spurious conflict not causal → detection-only
- **Minority accuracy fails:** GradCAM unreliable → global regularization

---

## 13. Timeline Estimate

| Task | Duration | Dependencies |
|------|----------|--------------|
| E-1 (Setup & Resampler) | 2 days | - |
| E-2 (Background Swapper) | 3 days | - |
| E-3 (Multi-Model Training) | 2 days | E-1 |
| E-4 (GAIA Extraction) | 1 day | E-3 |
| E-5 (Correlation Analyzer) | 1 day | E-4 |
| E-6 (Augmentation Experiment) | 2 days | E-2, E-4 |
| Testing & Validation | 2 days | All |
| **Total** | 13 days | - |

**Wall-clock estimate:** ~11 days with parallelization (E-5, E-6 can run concurrently)

---

## 14. Document Metadata

- **Generated:** 2026-08-20
- **Phase:** 3 (Implementation Planning)
- **Status:** READY FOR REVIEW
- **Next Action:** Phase 4 (Implementation)
- **Estimated Implementation Duration:** 13 days
