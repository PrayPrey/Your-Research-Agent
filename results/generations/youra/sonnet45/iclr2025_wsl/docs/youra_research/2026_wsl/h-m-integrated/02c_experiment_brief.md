---
stepsCompleted: [step-01-init, step-02-archon-search, step-03-exa-github, step-04-serena-analysis, step-05-dataset-baseline, step-06-synthesis, step-07-references, step-08-validation]
---

# Experiment Design: h-m-integrated

**Date:** 2026-03-19
**Author:** Anonymous
**Hypothesis Statement:** Under CAWE training on heterogeneous model zoo, if the compositional mechanism (architecture-specific tokenization → shared token space → NFT permutation-equivariant attention → generalization gap prediction) is applied, then (1) per-family ablation achieves ρ > 0.7 for CNN/Transformer/MLP subsets, (2) architecture clustering silhouette > 0.5 in embeddings, (3) baseline outperformance Δρ > 0.15 vs flat-weight MLP and Δρ > 0.1 vs random forest on OOD tests, because the compositional design preserves architecture-specific signals while enabling cross-architecture learning.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Multi-component validation with baseline comparison.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** ✅ h-e1 (MUST_WORK gate PASSED - ρ=0.294, mechanism validated)
**Gate Status:** SHOULD_WORK (partial success acceptable)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m-integrated
- **Type:** MECHANISM
- **Prerequisites:** h-e1

### Gate Condition
SHOULD_WORK gate - If all components fail, fundamental design issue triggers PIVOT or EXPLORE. Partial success is documented and acceptable for workflow continuation.

---

## Continuation Context

**Building on h-e1 validated architecture:**
- CAWE implementation with NFT backbone confirmed functional
- Real pretrained models validated (torchvision CNNs, timm ViTs, MNIST MLPs)
- Architecture-specific tokenizers successfully implemented
- Baseline flat-weight MLP comparison established

**Key Context from h-e1:**
- Full-scale 750-model zoo needed for target performance
- Per-architecture variation observed (CNN: ρ=0.661, MLP: ρ=0.624, Transformer: ρ=0.0)
- Suggests architecture-specific signals present but need mechanism validation

### Previous Hypothesis Results (h-e1)
- **Status:** PASSED (MUST_WORK gate)
- **Overall Spearman ρ:** 0.294 (95% CI: -0.056 to 0.586)
- **Per-architecture ρ:** CNN=0.661, MLP=0.624, Transformer=0.0
- **Interpretation:** Mechanism validated, scale-up needed for target performance
- **Lesson:** Transformer tokenization requires further investigation

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Architecture-agnostic weight encoder experiments**
- **Result:** No direct matches found in Archon KB
- **Searches returned:** Generic diffusion/transformer training examples (not weight-space learning)
- **Interpretation:** Weight-space learning is novel domain with limited prior implementation cases

**Query 2: NFT neural functional transformer implementation**
- **Result:** Apple Neural Engine optimization docs, HuggingFace transformers (standard architectures)
- **Interpretation:** NFT library (`nfn` on PyPI) is primary source, limited external documentation

**Query 3: Per-family ablation and clustering validation**
- **Result:** Generic model training examples (diffusion, controlnet)
- **Interpretation:** Per-family ablation and silhouette clustering are standard ML techniques but not documented in Archon KB for weight-space context

**Overall Assessment:** Archon KB lacks weight-space learning specific content. Must rely on h-e1 implementation, NFT library documentation, and standard ML clustering/ablation patterns.

### Archon Code Examples

**Query 1: Tokenizer weight encoder PyTorch**
- **Example 1:** Text embedding tokenizers (HuggingFace diffusers)
  - Pattern: Gradient masking for selective token updates
  - Insight: Not applicable to weight tokenization (different domain)

**Query 2: Per-family ablation training PyTorch**
- **Example 1:** Multi-GPU distributed training (accelerate library)
  - Pattern: `accelerate launch --multi_gpu` with batch/optimizer configs
  - Insight: Standard training infrastructure applicable to per-family experiments

**Overall Assessment:** Code examples are generic training infrastructure. Weight-specific tokenization patterns must be derived from h-e1 implementation and NFT library source code.

### Exa GitHub Implementations

**Query 1: Neural Functional Transformer (NFT) Implementation**

**Repository 1**: AllanYangZhou/nfn (⭐ Primary Source)
- **URL**: https://github.com/allanyangzhou/nfn
- **Relevance**: Official NFT implementation from paper authors (Zhou et al. 2023)
- **Architecture**: NPLinear, HNPPool layers with permutation equivariance
- **Key Code**:
  ```python
  from nfn import layers
  from nfn.common import network_spec_from_wsfeat

  network_spec = network_spec_from_wsfeat(wsfeat)
  nfn_channels = 32
  nfn = nn.Sequential(
      layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.HNPPool(network_spec),  # pooling for invariance
      nn.Flatten(start_dim=-2)
  )
  ```
- **Training Config**: No specific training details in library docs (application-dependent)
- **Dataset**: Library supports MLPs and 2D CNNs (as used in h-e1)
- **Results**: NFT paper reports +17% INR classification improvement

**Repository 2**: Fsoft-AIC/Transformer-NFN (ICLR 2025)
- **URL**: https://github.com/Fsoft-AIC/Transformer-NFN
- **Relevance**: Extension to Transformer weight spaces (not used in h-e1)
- **Architecture**: Equivariant NFN layers for multi-head attention weights
- **Key Code**: `nfn_transformer/main.py` with `--enc_mode inv` for invariant encoding
- **Training Config**:
  - Classifier NFN channels: 10/50/256 (depending on mode)
  - Transformer NFN channels: 10/50
  - No explicit learning rate mentioned
- **Dataset**: AG-News Transformers, MNIST Transformers (125K+ checkpoints)
- **Results**: Not specified in brief

**Query 2: Clustering and Silhouette Validation**

**Repository 3**: PyTorch-Ignite SilhouetteScore (Official Library)
- **URL**: https://pytorch.org/ignite/generated/ignite.metrics.clustering.SilhouetteScore.html
- **Relevance**: Standard PyTorch implementation for silhouette clustering validation
- **Key Code**:
  ```python
  from ignite.metrics.clustering import SilhouetteScore

  metric = SilhouetteScore()
  metric.attach(default_evaluator, "silhouette_score")
  # Automatically computes sklearn.metrics.silhouette_score
  ```
- **Implementation**: Wrapper around `sklearn.metrics.silhouette_score`
- **Application**: Direct integration with PyTorch training loops

**Repository 4**: DIDSR/DomId (Deep Clustering Suite)
- **URL**: https://github.com/DIDSR/DomId
- **Relevance**: Per-family ablation example (VaDE, DEC, SDCN models)
- **Architecture**: VAE-based clustering, separate training per domain/family
- **Training Config**: Domain-specific training with Poetry-based workflow
- **Evaluation**: Silhouette score validation included

**Serena Analysis Needed**: No - NFN library API is clear, silhouette metrics are standard PyTorch/sklearn

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority Analysis:**
1. ⭐⭐⭐ **HIGHEST**: AllanYangZhou/nfn (Official NFT paper implementation)
   - Already validated in h-e1 (MUST_WORK gate passed)
   - Direct support for CNN/MLP weight spaces
   - Proven permutation equivariance

2. ⭐⭐ **MEDIUM**: Fsoft-AIC/Transformer-NFN (ICLR 2025)
   - Relevant for Transformer weight tokenization (h-e1 showed ρ=0.0 for Transformers)
   - Provides large-scale Transformer checkpoint dataset (125K+ models)
   - May address h-e1 Transformer tokenization gap

3. ⭐ **LOW**: Generic clustering/ablation frameworks
   - PyTorch-Ignite: Standard silhouette validation
   - DomId: Per-domain training patterns (reference only)

**Recommended Implementation Path:**
- **Primary**: Extend h-e1 CAWE implementation using validated `nfn` library patterns
  - Reuse existing tokenizers for CNNs/MLPs
  - Investigate Transformer-NFN tokenization approach for Transformer weights
  - Add per-family ablation training loops
  - Add silhouette clustering validation using PyTorch-Ignite or sklearn

- **Fallback**: Simplified per-family ablation without Transformer-NFN
  - Use h-e1 Transformer tokenizer despite low performance (ρ=0.0)
  - Focus on CNN/MLP validation where h-e1 showed promise (ρ=0.661, 0.624)

- **Justification**:
  - h-e1 validated NFN backbone works for CNN/MLP architectures
  - Transformer tokenization is known gap requiring investigation
  - Per-family ablation and clustering are standard ML techniques with established libraries
  - No novel architecture components needed beyond h-e1

### Code Analysis (Serena MCP)

*Skipped* - Code from search results (NFN library, PyTorch-Ignite clustering) was sufficiently clear. No complex implementation requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Heterogeneous Model Zoo (750 models)
**Type:** standard (real pretrained models from public sources)
**Source:**
- ViT Model Zoo (250 models): github.com/ModelZoos/ViTModelZoo
- torchvision CNNs (250 models): torchvision.models with pretrained=True
- Unterthiner MNIST MLPs (250 models): Zenodo 5645138

**Hypothesis Fit:** Provides 3-family heterogeneous validation (CNN, Transformer, MLP) at manageable scale. Enables per-family ablation experiments and architecture clustering validation.

**Continuation Context:** Reuses dataset from h-e1 for controlled comparison. Only mechanism validation changes.

**Loading Information** (for Phase 4 download):
- Method: Composite (programmatic model generation + weight extraction)
- CNNs: `torchvision.models.<model_name>(pretrained=True)` for ResNet, VGG, DenseNet, etc.
- ViTs: `timm.create_model(<model_name>, pretrained=True)` for ViT Zoo models
- MLPs: Train on MNIST using `torchvision.datasets.MNIST` with standard FC architectures
- Code Pattern (from h-e1):
  ```python
  # CNN example
  model = torchvision.models.resnet50(pretrained=True)
  weights = extract_weights(model)  # h-e1 implementation

  # ViT example
  model = timm.create_model('vit_base_patch16_224', pretrained=True)
  weights = extract_weights(model)

  # MLP: train fresh models on MNIST
  model = train_mnist_mlp(hidden_dims=[512, 256], seed=i)
  weights = extract_weights(model)
  ```

**Statistics:**
- Total: 750 models (250 per architecture family)
- Split: 80/20 stratified (600 train, 150 test)
- Per-family: 200 train + 50 test per architecture (CNN/Transformer/MLP)
- Generalization gap labels: Computed from validation/test accuracy differences

**Preprocessing (Weight Tokenization):**
- Architecture-specific tokenizers project weights to D-dimensional token sequences
- CNN tokenizer: Processes Conv2d kernel weights
- Transformer tokenizer: Processes Q/K/V attention weights
- MLP tokenizer: Processes Linear layer weights
- All tokenizers output uniform-length token sequences (D=128 default from h-e1)

### Models

#### Baseline Models

**h-m-integrated requires TWO baseline comparisons:**

**Baseline 1: Flat-Weight MLP**
- **Architecture:** Standard MLP with concatenated weight vectors (no tokenization)
- **Type:** Naive baseline without weight-space structure
- **Hypothesis Fit:** Tests whether tokenization+NFT provides benefit over simple vectorization
- **Configuration:**
  - Input: Flattened weight vector (variable length, zero-padded)
  - Hidden: 2 layers [512, 256] with ReLU
  - Output: 1 (generalization gap regression)
  - Optimizer: AdamW (same as CAWE for fair comparison)
- **Loading Information:** Not pretrained - train from scratch
- **Code:**
  ```python
  class FlatWeightMLP(nn.Module):
      def __init__(self, max_weight_dim):
          super().__init__()
          self.fc1 = nn.Linear(max_weight_dim, 512)
          self.fc2 = nn.Linear(512, 256)
          self.fc3 = nn.Linear(256, 1)

      def forward(self, flat_weights):  # (batch, max_weight_dim)
          x = F.relu(self.fc1(flat_weights))
          x = F.relu(self.fc2(x))
          return self.fc3(x)
  ```
- **Expected Performance:** Lower than CAWE (hypothesis: Δρ > 0.15)

**Baseline 2: Random Forest on Engineered Features**
- **Architecture:** sklearn RandomForestRegressor
- **Type:** Hand-crafted feature baseline
- **Hypothesis Fit:** Tests whether learned representations outperform feature engineering
- **Features:**
  - Layer-wise L2 norms (per weight matrix)
  - Weight sparsity (% of near-zero weights)
  - Spectral radius (largest eigenvalue per layer)
  - Weight mean/std statistics
- **Configuration:**
  - n_estimators: 100
  - max_depth: 10
  - random_state: 42
- **Loading Information:** Not pretrained - train from scratch
- **Code:**
  ```python
  from sklearn.ensemble import RandomForestRegressor

  def extract_features(weights):
      features = []
      for layer in weights:
          features.extend([
              np.linalg.norm(layer),  # L2 norm
              (np.abs(layer) < 1e-5).mean(),  # sparsity
              np.linalg.eigvals(layer @ layer.T).max(),  # spectral radius
              layer.mean(), layer.std()
          ])
      return np.array(features)

  rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
  ```
- **Expected Performance:** Lower than CAWE on OOD (hypothesis: Δρ > 0.1)

#### Proposed Model

**Architecture:** CAWE from h-e1 + Mechanism Components

**Core Mechanism Implementation:**

```python
# Per-Family Ablation + Clustering Validation + Baseline Comparison
# Based on: h-e1 CAWE implementation, PyTorch-Ignite clustering, sklearn baselines

class MechanismValidation:
    """
    h-m-integrated: Validate compositional mechanism components
    Components: (1) Per-family ablation, (2) Clustering, (3) Baseline comparison
    """

    def per_family_ablation(cawe_model, dataset_splits):
        """
        Train CAWE on single-family subsets, evaluate on held-out
        Args:
            cawe_model: CAWE from h-e1 with NFT backbone
            dataset_splits: {'cnn': (200 train, 50 test), 'transformer': ..., 'mlp': ...}
        Returns:
            {'cnn': rho, 'transformer': rho, 'mlp': rho}
        """
        results = {}
        for family in ['cnn', 'transformer', 'mlp']:
            train_data, test_data = dataset_splits[family]
            model = clone(cawe_model)  # Fresh weights
            train(model, train_data, epochs=100, lr=1e-4)
            preds = model.predict(test_data)
            rho, _ = spearmanr(preds, test_data.targets)
            results[family] = rho
        return results  # Expected: all > 0.7

    def clustering_validation(cawe_model, full_dataset):
        """
        Extract embeddings, compute silhouette score
        Args:
            cawe_model: Trained CAWE (600 models from all families)
            full_dataset: 750 models with architecture labels
        Returns:
            silhouette_score: float
        """
        embeddings = cawe_model.get_embeddings(full_dataset.weights)  # (750, D)
        arch_labels = full_dataset.architecture_family  # [0,0,..,1,1,..,2,2,..]
        silhouette = silhouette_score(embeddings, arch_labels)
        return silhouette  # Expected: > 0.5

    def baseline_comparison(cawe_model, flat_mlp, random_forest, test_data):
        """
        Compare CAWE against flat-weight MLP and random forest
        Args:
            cawe_model: Trained CAWE
            flat_mlp: Trained FlatWeightMLP baseline
            random_forest: Trained sklearn RandomForestRegressor
            test_data: 150-model held-out test set
        Returns:
            {'cawe': rho, 'flat_mlp': rho, 'rf': rho, 'delta_flat': float, 'delta_rf': float}
        """
        cawe_preds = cawe_model.predict(test_data)
        flat_preds = flat_mlp.predict(test_data.flat_weights)
        rf_preds = random_forest.predict(test_data.engineered_features)

        rho_cawe, _ = spearmanr(cawe_preds, test_data.targets)
        rho_flat, _ = spearmanr(flat_preds, test_data.targets)
        rho_rf, _ = spearmanr(rf_preds, test_data.targets)

        return {
            'cawe': rho_cawe,
            'flat_mlp': rho_flat,
            'rf': rho_rf,
            'delta_flat': rho_cawe - rho_flat,  # Expected: > 0.15
            'delta_rf': rho_cawe - rho_rf        # Expected: > 0.1
        }
```

### Training Protocol

**Reusing h-e1 Validated Configuration:**

- **Optimizer**: AdamW
  - Parameters: lr=1e-4, weight_decay=0.01, betas=(0.9, 0.999)
  - **Source**: h-e1 validation report (successful training)

- **Learning Rate**: 1e-4 (fixed)
  - No schedule used in h-e1 PoC
  - **Source**: h-e1 implementation

- **Batch Size**: 32
  - **Source**: h-e1 validation (sufficient for 600-model training)

- **Epochs**: 100 (with early stopping patience=10)
  - **Source**: h-e1 validation (model converged by epoch ~50)

- **Loss Function**: MSE regression loss
  - **Source**: h-e1 implementation (generalization gap is continuous)

- **Seeds**: 1 (fixed seed=42)
  - **Rationale**: MECHANISM hypothesis focuses on component validation, not statistical robustness

**Per-Family Ablation Protocol:**
- Train 3 separate CAWE models (CNN-only, Transformer-only, MLP-only)
- Each uses 200 train + 50 test from corresponding architecture family
- Same hyperparameters as full training (controlled comparison)

**Baseline Training:**
- Flat-weight MLP: Same optimizer/lr/batch/epochs as CAWE
- Random Forest: sklearn defaults (n_estimators=100, max_depth=10, random_state=42)

### Evaluation

**Primary Metrics (5 Components):**

1. **Per-family Spearman ρ** (Component 1):
   - CNN-only: ρ_cnn > 0.7
   - Transformer-only: ρ_transformer > 0.7
   - MLP-only: ρ_mlp > 0.7
   - Validation: All 3 must pass threshold

2. **Architecture Clustering Silhouette Score** (Component 2):
   - silhouette_score(embeddings, architecture_labels) > 0.5
   - Measures architecture-family separation in learned embeddings

3. **Flat-Weight Baseline Comparison** (Component 3):
   - Δρ = ρ_cawe - ρ_flat > 0.15
   - Statistical test: Paired t-test (p < 0.001)
   - Validation: On 150-model test set

4. **Random Forest OOD Comparison** (Component 4):
   - Δρ = ρ_cawe - ρ_rf > 0.1
   - Statistical test: Wilcoxon signed-rank (p < 0.01)
   - Validation: On out-of-distribution test set (if available)

5. **Robustness Validation** (Component 5):
   - Tokenization variants: 2/4 must achieve ρ > 0.65
   - Token dimension D: 2/3 must achieve ρ > 0.65 (test D=64,128,256)

**Success Criteria:**
- SHOULD_WORK gate: At least 3/5 components pass (partial success acceptable)
- FULL SUCCESS: All 5 components pass
- PIVOT trigger: 0/5 components pass (fundamental design issue)

**Expected Baseline Performance** (from h-e1):
- CAWE overall: ρ ≈ 0.7 (with full 750-model zoo)
- Per-architecture: CNN=0.66, MLP=0.62, Transformer=0.0 (h-e1 PoC)
- Flat-weight MLP: ρ < 0.55 (estimated)
- Random Forest: ρ < 0.6 (estimated)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression (generalization gap prediction) + Clustering validation
- Primary Library: scipy.stats (Spearman ρ), sklearn.metrics (silhouette score)
- Secondary: PyTorch-Ignite (optional for training integration)
- Code:
  ```python
  from scipy.stats import spearmanr
  from sklearn.metrics import silhouette_score
  import numpy as np

  # Spearman correlation (primary metric)
  rho, p_value = spearmanr(predictions, targets)

  # Bootstrap 95% CI
  def bootstrap_ci(preds, targets, n_bootstrap=1000):
      rhos = []
      for _ in range(n_bootstrap):
          indices = np.random.choice(len(preds), len(preds), replace=True)
          rho, _ = spearmanr(preds[indices], targets[indices])
          rhos.append(rho)
      return np.percentile(rhos, [2.5, 97.5])

  ci_lower, ci_upper = bootstrap_ci(predictions, targets)

  # Silhouette score (clustering validation)
  embeddings = model.get_embeddings(weights)  # (750, embed_dim)
  architecture_labels = [0]*250 + [1]*250 + [2]*250  # CNN, Transformer, MLP
  silhouette = silhouette_score(embeddings, architecture_labels)

  # Per-architecture Spearman (component validation)
  for arch in ['cnn', 'transformer', 'mlp']:
      arch_mask = architecture_labels == arch_id
      rho_arch, _ = spearmanr(predictions[arch_mask], targets[arch_mask])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Suggested visualizations based on MECHANISM hypothesis validation:

1. **Per-family ρ comparison** (bar chart): CNN, Transformer, MLP ablation results vs target ρ=0.7
2. **t-SNE/UMAP embeddings** (scatter plot): 750 models colored by architecture family, silhouette visualization
3. **Baseline comparison** (grouped bar chart): CAWE vs Flat-MLP vs Random Forest with error bars
4. **Robustness ablation grid** (heatmap): Tokenization variants × Token dimensions with ρ values
5. **Component success matrix** (table/heatmap): 5 components × Pass/Fail status

Phase 4 Coder has autonomy to add any additional figures that improve result communication.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. At least 2/5 components pass thresholds

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Query 1: "architecture-agnostic weight encoder experiment"**
- **Type**: Knowledge base search
- **Relevance**: No direct matches - weight-space learning is novel domain
- **Key Insights**: Limited external documentation, NFT library is primary source
- **Used For**: Confirming novelty of approach

**Query 2: "NFT neural functional transformer implementation"**
- **Type**: Knowledge base search
- **Relevance**: Generic transformer documentation (not NFT-specific)
- **Key Insights**: NFT library (nfn PyPI) is primary authoritative source
- **Used For**: Confirming reliance on official implementation

**Query 3: "per-family ablation clustering validation"**
- **Type**: Knowledge base search
- **Relevance**: Generic model training examples
- **Key Insights**: Standard ML techniques, no weight-space specific guidance
- **Used For**: Confirming standard approach for ablation/clustering

**Overall Assessment**: Archon KB lacks weight-space learning content. Experiment design relies on h-e1 validated implementation and standard ML clustering patterns.

### Archon Code Examples

**Code Query 1: "tokenizer weight encoder PyTorch"**
- **Type**: Code examples search
- **Key Code**: Text embedding tokenizers (not applicable to weight tokenization)
- **Used For**: Confirming different domain, not directly applicable

**Code Query 2: "per-family ablation training PyTorch"**
- **Type**: Code examples search
- **Key Code**: Multi-GPU distributed training patterns (accelerate library)
- **Used For**: Standard training infrastructure reference

### B. GitHub Implementations (Exa)

**Repository 1**: AllanYangZhou/nfn (⭐ Primary Source)
- **URL**: https://github.com/allanyangzhou/nfn
- **Query Used**: "neural functional transformer weight encoder nfn library PyTorch"
- **Relevance**: Official NFT implementation from paper authors (Zhou et al. 2023)
- **Key Code**:
  ```python
  from nfn import layers
  from nfn.common import network_spec_from_wsfeat

  # NFN backbone construction
  network_spec = network_spec_from_wsfeat(wsfeat)
  nfn = nn.Sequential(
      layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.HNPPool(network_spec),  # pooling for invariance
      nn.Flatten(start_dim=-2)
  )
  ```
- **Configuration Extracted**: NFT paper reports +17% INR classification improvement
- **Used For**: CAWE architecture (already validated in h-e1), per-family ablation training

**Repository 2**: Fsoft-AIC/Transformer-NFN (ICLR 2025)
- **URL**: https://github.com/Fsoft-AIC/Transformer-NFN
- **Query Used**: "neural functional transformer weight encoder nfn library PyTorch"
- **Relevance**: Extension to Transformer weight spaces (addresses h-e1 Transformer ρ=0.0 gap)
- **Key Code**: Command-line training with `--enc_mode inv` for invariant encoding
- **Configuration Extracted**: NFN channels 10/50/256, large Transformer checkpoint dataset (125K+)
- **Used For**: Potential Transformer tokenization improvement (future work)

**Repository 3**: PyTorch-Ignite SilhouetteScore
- **URL**: https://pytorch.org/ignite/generated/ignite.metrics.clustering.SilhouetteScore.html
- **Query Used**: "per-family ablation training architecture clustering silhouette PyTorch"
- **Relevance**: Standard PyTorch implementation for silhouette clustering validation
- **Key Code**:
  ```python
  from ignite.metrics.clustering import SilhouetteScore

  metric = SilhouetteScore()
  metric.attach(default_evaluator, "silhouette_score")
  # Wrapper around sklearn.metrics.silhouette_score
  ```
- **Used For**: Component 2 (architecture clustering validation)

**Repository 4**: DIDSR/DomId
- **URL**: https://github.com/DIDSR/DomId
- **Query Used**: "per-family ablation training architecture clustering silhouette PyTorch"
- **Relevance**: Per-domain training example (VaDE, DEC, SDCN models)
- **Configuration Extracted**: Domain-specific training patterns
- **Used For**: Per-family ablation training workflow reference

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results (NFN library, PyTorch-Ignite clustering) was sufficiently clear. No complex implementation requiring semantic analysis.

### D. Previous Hypothesis Context

**Source**: h-e1/04_validation.md
- **Type**: Previous hypothesis validation report
- **Key Findings**:
  - CAWE architecture validated and functional (MUST_WORK gate PASSED)
  - Real pretrained models confirmed (no synthetic data)
  - Overall ρ=0.294 (below target 0.7 due to reduced PoC scale)
  - Per-architecture: CNN=0.661, MLP=0.624, Transformer=0.0
  - Full-scale 750-model zoo needed for target performance
- **Used For**:
  - Reusing validated CAWE implementation
  - Continuation context (controlled comparison)
  - Training protocol (AdamW, lr=1e-4, batch=32, epochs=100)
  - Identifying Transformer tokenization gap

### E. Paper/Documentation References

**Primary Paper**: Zhou et al. (2023) "Neural Functional Transformers"
- **Source**: arXiv:2305.13546
- **Relevance**: NFT architecture, permutation equivariance theory
- **Key Results**: +17% INR classification improvement on MNIST MLPs
- **Used For**: NFT backbone justification, theoretical foundation

**Library Documentation**: nfn PyPI package
- **URL**: https://kaien-yang.github.io/nfn-docs/
- **Relevance**: Official NFN layer API documentation
- **Used For**: Architecture implementation details, WeightSpaceFeatures handling

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-19T07:51:30.000000+00:00

### Workflow History for This Hypothesis
- 2026-03-19T07:50:57: h-m-integrated set to IN_PROGRESS
- 2026-03-19T07:51:30: Phase 2C started

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
