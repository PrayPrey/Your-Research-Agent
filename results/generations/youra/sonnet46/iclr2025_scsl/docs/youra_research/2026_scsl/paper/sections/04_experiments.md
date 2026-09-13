# 4. Experimental Setup

We design experiments to answer four specific research questions about the normalized gradient norm signal:

**RQ1:** Does g̃ achieve AUC > 0.70 for minority group prediction on Waterbirds at T_id=5, without group annotations?

**RQ2:** What is the magnitude of the minority/majority g̃ ratio at T_id ∈ {1, 3, 5, 10}, and does it exceed the 3.0x threshold?

**RQ3:** Does the ratio persist at T_id=10, confirming temporal robustness of the proxy signal beyond the initial training phase?

**RQ4:** Does BatchNorm equalize feature norms across groups (h_norm_std_ratio < 0.5), validating the mechanistic interpretation of g̃ as a prediction-residual signal?

Each RQ maps directly to a contribution: RQ1 validates the proxy signal utility, RQ2 validates signal strength, RQ3 validates temporal robustness, RQ4 validates the mechanistic interpretation.

## 4.1 Dataset

**Waterbirds** is the primary benchmark for spurious correlation robustness research [Sagawa et al., 2019]. It is constructed by compositing birds (from CUB-200 [Welinder et al., 2010]) onto backgrounds from the Places dataset [Zhou et al., 2018], creating a 95% background-bird spurious correlation in the training set.

| Split | Total | G0 (Landbird/Land) | G1 (Landbird/Water) | G2 (Waterbird/Land) | G3 (Waterbird/Water) |
|-------|-------|---------------------|----------------------|----------------------|----------------------|
| Train | 4,795 | 3,498 (72.9%) | 184 (3.8%) | 56 (1.2%) | 1,057 (22.1%) |
| Val   | 1,199 | — | — | — | — |
| Test  | 5,794 | — | — | — | — |

Groups are defined as G = y × 2 + place (y ∈ {landbird=0, waterbird=1}, place ∈ {land=0, water=1}). Minority groups G1 and G2 carry the "wrong" background-bird pairing; majority groups G0 and G3 carry the spurious background-bird correlation.

**Why Waterbirds:** Waterbirds has a well-defined, quantifiable spurious correlation, a standard 4-group structure enabling precise minority/majority evaluation, and is the primary benchmark used by all comparison methods (JTT, LfF, DFR, GroupDRO). The minority fraction (~5% total, with G2 at only 1.2%) creates a challenging proxy identification problem.

**Preprocessing:** Images resized to 256×256, center-cropped to 224×224. Training augmentation: random horizontal flip. ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]).

## 4.2 Model and Training

**Model:** ResNet-50, ImageNet pretrained (ResNet50_Weights.IMAGENET1K_V1 via torchvision). Last layer replaced with FC(2048→2) for 2-class Waterbirds classification. Total parameters: ~25M; last layer: 2048×2 + 2 = 4,098 parameters.

**Why ResNet-50:** ResNet-50 is the standard architecture for Waterbirds experiments across all comparison methods (JTT, LfF, DFR, GroupDRO all use ResNet-50). Its BatchNorm layers throughout the residual blocks are a critical architectural requirement for our method's feature equalization property.

**Training (Stage 1 — ERM):**

| Hyperparameter | Value | Source |
|---------------|-------|--------|
| Optimizer | SGD | Phase 2B specification |
| Learning rate | 0.001 | Phase 2B controlled variable |
| Momentum | 0.9 | Phase 2B controlled variable |
| Weight decay | 1e-4 | Phase 2B controlled variable |
| Batch size | 128 | Phase 2B controlled variable |
| Total epochs | 10 | Gradient norm collection range |
| Gradient norm collection epochs | {1, 3, 5, 10} | NHT temporal analysis |
| Random seed | 42 | Fixed for reproducibility |

**Implementation:** GradientNormAnalyzer registers a forward hook on `model.fc` to capture feature vectors h(xᵢ) ∈ ℝ^2048 in CPU memory. At each collection epoch, the full training set (4,795 samples) is processed in eval() mode with no BatchNorm updates, collecting g̃ᵢ for all samples via the outer-product decomposition (see Section 3.2). GPU: NVIDIA H100 NVL (CUDA_VISIBLE_DEVICES=0). Framework: PyTorch 2.10+cu128, Python 3.10.

## 4.3 Evaluation Metrics

**AUC (minority group prediction):** Binary classification AUC for predicting group membership (minority=1 for G1∪G2, majority=0 for G0∪G3) using g̃ as the score. Computed using `sklearn.metrics.roc_auc_score`. This is the primary proxy quality metric: it measures how well g̃ discriminates minority samples, regardless of threshold selection.
- **Target:** AUC > 0.70

**Minority/majority g̃ ratio:** Mean g̃ over minority samples (G1∪G2) divided by mean g̃ over majority samples (G0∪G3) at each collection epoch.
- **Target:** ratio ≥ 3.0x at T_id=5; ≥ 1.2x at T_id=10

**Balance deviation (original criterion):** Maximum within-class group deviation from uniformity in the top-25% high-norm subset. Selected as a gate criterion in Phase 2B but later diagnosed as a criterion design mismatch (Section 5.2). Reported for completeness.
- **Original target:** ≤ 0.10 (class uniformity)

**Feature norm std ratio (h_norm_std_ratio):** Standard deviation of feature norms ‖h(xᵢ)‖ divided by mean, computed per group across the training set. Measures BatchNorm equalization.
- **Target:** < 0.5 (indicating < 50% coefficient of variation, confirming equalization)

## 4.4 Reproducibility

All experiments use a fixed seed (seed=42) covering `torch.manual_seed`, `numpy.random.seed`, `random.seed`, and `torch.backends.cudnn.deterministic=True`. Code is structured as 6 modular files (~786 total lines): `src/dataset.py`, `src/model.py`, `src/train.py`, `src/evaluate.py`, `src/visualize.py`, and `run_experiment.py`. 67/67 unit and integration tests pass. All figures are generated from experiment output via deterministic matplotlib code.
