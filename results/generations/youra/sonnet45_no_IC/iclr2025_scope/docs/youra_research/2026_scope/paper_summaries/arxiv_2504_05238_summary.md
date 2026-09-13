# Federated Learning for Medical Image Classification: A Comprehensive Benchmark

## Key Metadata
- **Authors:** Zhekai Zhou et al.
- **Year:** 2025
- **Venue:** IEEE Transactions
- **Core Contribution:** Comprehensive benchmark showing no single FL algorithm consistently delivers optimal performance across all medical federated learning scenarios.

## Section Summaries

### Abstract
The federated learning paradigm is well-suited for medical image analysis as it protects privacy while training on isolated multi-center data. However, current research focuses on limited datasets centered around natural images with insufficient medical context experiments. This work conducts comprehensive evaluation of state-of-the-art federated learning algorithms across multiple medical imaging datasets, evaluating both classification performance and system metrics (communication cost, computational efficiency). Key findings: medical imaging datasets pose substantial challenges, no single algorithm consistently optimal, many may underperform. Proposes efficient method combining denoising diffusion probabilistic models with label smoothing for dataset augmentation.

### Introduction & Motivation
Medical data creates data silos due to privacy concerns - hospitals reluctant to share electronic health records and medical imaging. Federated learning (FL) addresses this by training collaboratively without data exchange. Key challenge: non-IID data across participants causes performance degradation. Existing research gaps: (1) Limited to MNIST/CIFAR-10, not medical imaging; (2) Simulated non-IID via Dirichlet distribution, not real multi-center datasets; (3) Simple networks (MLPs/CNNs), not suitable for medical complexity; (4) Insufficient comparative experiments across optimization types.

### Methodology
**Benchmark Setup:** Evaluates traditional FL optimization (FedAvg, FedProx μ=0.01, MOON μ=1.0 with contrastive loss, FedNova with normalized updates, FedRS with constrained Softmax α=0.5, Elastic Aggregation μ=0.95 τ=0.5), personalized FL (FedBN excluding batch norm from aggregation, PRR-FL α₁=0.7 α₂=0.9 with deputy-enhanced transfer), and one-shot FL (DENSE data-free distillation).

**Proposed Method:** Augments limited client datasets using conditional DDPM to generate synthetic medical images. DDPM architecture: U-Net with 3 down-sample layers, 3 up-sample layers, self-attention, ~93M parameters. Forward process adds Gaussian noise via Markov chain: $x_t = \sqrt{1-\beta_t} \cdot x_{t-1} + \sqrt{\beta_t} \cdot \epsilon$ where $\epsilon \sim N(0,I)$. Reverse process predicts noise at each step to denoise. Combines with label smoothing: $y_{soft} = (1-\alpha) \cdot y + \frac{\alpha}{K} \cdot 1$ where α∈(0,1) and K is class count, preventing overconfidence on synthetic data.

**Datasets:** 9 medical imaging datasets including ColonPath (10,009 pathology patches 1024×1024, lesion detection), NeoJaundice (2,235 photos 567×567, bilirubin level classification), Retino/DR (retinal images 2736×1824, 5-class DR severity), CRC (100K H&E-stained tissue patches, 9-class cancer detection), COVID-QU-Ex (3,728 chest X-rays, 3-class COVID diagnosis), Breast (780 ultrasound 500×500, 3-class tumor classification), TB (real multi-center from Shenzhen/India/Montgomery with feature heterogeneity).

**Training:** ResNet-50 classifier with ImageNet pre-training. Adam optimizer lr=10⁻³, β₁=0.9, β₂=0.999, weight decay=5×10⁻⁴, batch size=64, 5 local epochs per round. DDPM training iterations: $E = 10^6 \cdot K/N$ where K=categories, N=training samples. Images resized to 256×256, normalized to [-1,1].

### Experiments & Results
**Main Results:** No single algorithm achieves optimal performance across all 9 datasets. Proposed method (DDPM + label smoothing) achieves best results on 7/9 datasets with highest average accuracy (88.66% vs FedAvg 85.74%). Performance varies dramatically: Elastic Aggregation outperforms FedAvg on 5 datasets but PRR-FL and DENSE underperform on most. On TB (real multi-center non-IID): FedAvg 69.47% → Proposed method 86.69% (+17.22pp gain).

| Dataset | Centralized | FedAvg | Best Traditional | Best Personalized | Proposed (DDPM+LS) |
|---------|------------|--------|------------------|-------------------|-------------------|
| ColonPath | 99.66% | 99.34% | 99.62% (Elastic) | 98.41% (FedBN) | **99.64%** |
| NeoJaundice | 83.53% | 80.53% | 82.67% (MOON) | 81.01% (FedBN) | **83.47%** |
| Retino | 86.04% | 76.13% | 82.43% (Elastic) | 78.94% (FedBN) | **85.14%** |
| TB (multi-center) | 90.13% | 69.47% | 84.72% (FedProx/MOON) | 87.12% (FedBN) | **86.69%** |

**Non-IID Impact:** TB dataset shows significant pixel distribution differences across clients (mean values: 155.1, 137.1, 110.3; std=18.4). After DDPM augmentation, distributions converge (138.6, 133.4, 114.3; std=10.4). Imbalanced NeoJaundice (3 clients with 596±201 samples) improved from 80.05% → 81.84% after balancing via generation.

**Efficiency:** Communication cost - DENSE lowest (single round) but poor accuracy (47.97% COVID, 66.02% Breast). Proposed method same as FedAvg (2.409×10⁷ params/round). Computational cost (FLOPs): FedAvg/Proposed 3.454×10¹¹, PRR-FL 6.908×10¹¹ (2× due to deputy model), MOON 1.036×10¹² (3× due to contrastive learning). Convergence: Proposed method requires 22 rounds vs FedAvg 26 rounds on TB, achieves 86.69% vs FedAvg 69.47%.

**Ablations:** DDPM alone yields 81.98% on Retino vs 85.14% with label smoothing (+3.16pp), showing label smoothing crucial for preventing synthetic data overfitting. On ColonPath (large dataset), DDPM slightly hurts (99.16% vs 99.34% baseline), indicating augmentation only helps small/heterogeneous datasets.

### Discussion & Conclusion
Key takeaway: dataset-specific challenges require adaptive FL approaches - no universal winner. Medical imaging poses unique challenges (small client datasets, equipment-induced feature heterogeneity, high-resolution images) not captured by MNIST/CIFAR benchmarks. Proposed DDPM-based augmentation widely applicable but computationally expensive (requires training 93M-parameter generative model per client). Recommendations: (1) Use DDPM+LS when GPU capacity sufficient; (2) MOON for balanced performance; (3) Elastic Aggregation or FedProx for limited resources; (4) FedProx for low-bandwidth scenarios. Limitations: fixed client count (no exploration of scaling effects).

## Key Contributions
- First comprehensive FL benchmark on medical imaging (9 datasets, 3 FL paradigms: traditional/personalized/one-shot, ResNet-50 classifier)
- Empirical evidence that FL algorithm performance is dataset-dependent - rankings change across datasets, invalidating one-size-fits-all approaches
- Novel DDPM-based data augmentation method achieving 7/9 best results, with label smoothing preventing synthetic-data overfitting
- Real multi-center dataset (TB) revealing feature heterogeneity challenges absent in simulated non-IID scenarios

## Potential Relevance
Dataset-aware method selection framework directly addresses research gap "no single optimal method across dataset diversity." Evidence that baseline comparison methodology must account for dataset characteristics (size, modality, distribution shift). Demonstrates systematic validation approach using multiple existing medical datasets with automatic evaluation (no human assessment). Computational efficiency analysis (FLOPs, communication cost) guides feasible experimental design with publicly available datasets.
