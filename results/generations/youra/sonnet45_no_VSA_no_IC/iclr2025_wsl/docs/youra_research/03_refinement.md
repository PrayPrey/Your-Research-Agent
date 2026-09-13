# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-20T04:10:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent Controller Ablation)
- **Gap ID**: Gap_1
- **Gap Title**: Unified Weight Space Embedding Methods Across Heterogeneous Architectures
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 7

**Convergence Reason**: All convergence criteria met after 7 exchanges. SPECIFIC: Clear core claim established. MECHANISM: Hierarchical VAE with 3-level architecture detailed. PREDICTIONS: P1-P3 with quantitative success criteria. NOVELTY: Architecture-invariant structure discovery represents paradigm shift. FEASIBILITY: CKA+UMAP feasibility gates, technical soundness validated. OBJECTIONS: All 5 critical gaps (dataset audit, CKA, adversarial metadata, training ablation, scope limitation) addressed by Dr. Nova Exchange 7.

### Key Insights

1. **Heterogeneity as Signal (Dr. Nova)**: Treating architectural differences as information-bearing features rather than noise enables discovery of task-invariant structure. Compositional meta-space exploits cross-architecture diversity.

2. **Equivariance Hierarchy (Prof. Pax)**: Hierarchical design resolves equivariance-expressivity tradeoff by preserving local neuron-permutation symmetries (micro-level) while sacrificing them for cross-architecture generalization (macro-level).

3. **CKA over Procrustes (Prof. Rex)**: Centered Kernel Alignment handles nonlinear relationships between architecture subspaces, essential for metric compatibility validation. Procrustes (linear-only) too restrictive.

4. **Training Procedure Confound (Prof. Rex)**: Augmentation strategies may create more weight structure than task labels. Explicit ablation transforms potential flaw into discovery opportunity.

5. **Adversarial Metadata Test (Prof. Rex)**: Demonstrates weights encode information fundamentally inaccessible to text-based inference (100% corrupted metadata → >90% task accuracy).

### Breakthrough Moments

1. **Exchange 3 (Dr. Sage)**: Framing as "Transformers for Model Zoos" clarified mechanistic novelty — weight-space analogue of BERT/GPT for code corpora, not just NFN/UNF scale-up.

2. **Exchange 4 (Prof. Pax)**: Fiber bundle geometric interpretation revealed metric compatibility (CKA alignment) as key feasibility constraint requiring empirical validation.

3. **Exchange 6 (Prof. Rex)**: Identified 5 critical gaps that could sink hypothesis despite passing experiments — dataset coverage, CKA vs Procrustes, adversarial metadata, training ablation, scope creep.

4. **Exchange 7 (Dr. Nova)**: Transformed dataset sparsity from blocker to natural experiment, strengthening robustness claims. Sparse architecture-task cells test whether task signal survives limited samples.

---

## Final Hypothesis

### Title
**Hierarchical Weight Space Embeddings for Cross-Architecture Model Property Inference**

### Core Claim
*Under heterogeneous model zoos (ModelZooDataset, SANE, ViTModelZoo) containing CNNs, Transformers, RNNs, and MLPs trained on overlapping task sets, if we train a hierarchical variational autoencoder with architecture-type-aware tokenization and three-level supervision (coarse labels → contrastive learning → zero-shot transfer), then same-task different-architecture models will cluster more tightly (measured via within-cluster sum of squares) than different-task same-architecture models, because task-level functional constraints and training-induced regularities create architecture-invariant structural features in weight distributions that persist across computational primitives (convolution vs attention vs recurrence).*

### Mechanism

**Hierarchical VAE with 3-Level Architecture:**

**Level 1: Architecture-Specific Equivariant Encoders**
- NFN (Neural Functional Networks) for CNNs: Preserves permutation equivariance over conv kernels
- UNF (Universal Neural Functionals) for Transformers/RNNs: Automatic equivariant layer construction
- Extracts task-relevant features while maintaining local neuron-permutation symmetries

**Level 2: Permutation-Invariant Pooling**
- Collapses neuron clusters into layer-level summaries (e.g., mean/sum pooling over weight tensors)
- Sacrifices fine-grained neuron-level equivariance for cross-architecture compatibility
- Retains task-relevant structure while discarding architecture-specific implementation details

**Level 3: Transformer Sequence Modeling**
- Treats layer summaries as tokens in a sequence (handles variable-length architectures)
- Architecture-type embeddings (conv, attention, MLP, recurrent) added to positional encodings
- Self-attention discovers relational structure between layer types across architectures
- Example: learns that CNN conv layers are functionally analogous to Transformer MLP blocks

**Three-Level Supervision:**
1. **Coarse Labels**: Bootstrap initial clustering using model zoo task metadata (ImageNet classifier, CIFAR-10, etc.)
2. **Contrastive Learning**: Triplet loss where anchor/positive = same-task different-architecture, negative = different-task. Discovers latent sub-task structure.
3. **Zero-Shot Transfer**: Validate generalization on unlabeled models (breaks dependency on supervised labels)

---

## Predictions

### P1 (Primary): Clustering Tightness
**Statement:** Same-task different-architecture model pairs cluster more tightly (lower within-cluster sum of squares) than different-task same-architecture pairs when embedded via hierarchical VAE.

**Test Method:** Bootstrap hypothesis test (n=100 resamples) comparing WCSS distributions for same-task vs different-task pairs across all architecture family combinations (CNN-Transformer, CNN-RNN, etc.)

**Success Criterion:** Mean WCSS(same-task) < Mean WCSS(different-task) with p < 0.01 (two-tailed test). Effect size Cohen's d > 0.5 (medium).

**Falsification:** If p ≥ 0.01 or d < 0.2, task structure does not significantly influence cross-architecture clustering — hypothesis refuted.

### P2: CKA Representation Similarity (Feasibility Validation)
**Statement:** CKA similarity between architecture-specific encoders exceeds 0.6 for same-task pairs and remains below 0.4 for different-task pairs.

**Test Method:** Compute CKA scores on held-out validation set (100 same-task pairs, 100 different-task pairs) after training NFN/UNF encoders.

**Success Criterion:** Median CKA(same-task) > 0.6 AND Median CKA(different-task) < 0.4

**Falsification:** If same-task CKA < 0.5 or different-task CKA > 0.5, architecture subspaces are not metrically compatible — proceed to nonlinear bridge or reject mechanism.

### P3: Adversarial Metadata Robustness
**Statement:** Zero-shot task prediction on adversarially mislabeled Hugging Face models (100% corrupted metadata) achieves >90% accuracy, proving weights encode information inaccessible to text-based inference.

**Test Method:** Collect 100 models, corrupt all metadata (swap descriptions, rename checkpoints), train hierarchical encoder on clean model zoo, test on corrupted models without metadata access.

**Success Criterion:** Task prediction accuracy > 90% on adversarially corrupted models, AND >10 percentage points higher than best metadata-based baseline.

**Falsification:** If accuracy < 85% or metadata baseline matches weight-based accuracy (within 5pp), weights do not provide unique information over metadata — reduced contribution claim.

---

## Novelty

**Key Innovation:** Hierarchical equivariance tradeoff — preserve local neuron-permutation symmetries (micro-level) while sacrificing them for cross-architecture generalization (macro-level). Operationalized via 3-level VAE combining architecture-specific encoders (NFN, UNF) with pooling and Transformer sequence modeling.

**Paradigm Shift:** First demonstration that task-level functional constraints create architecture-invariant structure in weight distributions, enabling cross-architecture model property inference on heterogeneous unlabeled collections. Treats heterogeneity as signal rather than obstacle.

**Differentiation from Prior Work:**

| Prior Work | Limitation | Our Extension |
|------------|-----------|---------------|
| NFN (Zhou 2023) | Homogeneous MLPs/CNNs only | Hierarchical pooling + sequence modeling for heterogeneous collections |
| UNF (Zhou 2024) | Single architecture at a time | Compositional meta-space across multiple architecture families |
| Task Arithmetic (Ilharco 2022) | Requires shared base model | Discovers task-invariant structure without shared ancestry |
| SANE (ICML 2024) | Homogeneous sequential processing | Architecture-type-aware tokenization for heterogeneous zoos |

---

## Experimental Design

### Datasets
- **ModelZooDataset** (NeurIPS 2022 Dataset Track): Systematic variations across architectures
- **SANE Extensions** (ICML 2024): Inhomogeneous zoo support (MultiZoo-SANE)
- **ViTModelZoo** (2025): Vision Transformer variants
- **Hugging Face Web-Scraped Models**: 100 models with adversarially corrupted metadata

### Baselines
1. **Architecture-Conditioned MLP**: Flatten weights + one-hot architecture encoding → MLP classifier
2. **ProbeGen** (Kahana et al. 2024): Deep linear probe generators (architecture-specific SOTA)
3. **SANE** (ICML 2024): Sequential weight encoder on homogeneous zoos

### Experimental Protocol

**Pre-Phase 1: Dataset Coverage Audit**
- Verify ModelZooDataset + SANE + ViTModelZoo contain ≥30 models per architecture-task cell
- If sparse: treat as natural experiment testing robustness to limited samples

**Phase 1: Feasibility Gates (Early Falsification)**
- Train NFN-CNN and UNF-Transformer encoders separately
- Compute CKA + UMAP alignment metrics
- **Gate Criterion:** CKA same-task >0.6 AND different-task <0.4, OR UMAP shared-neighbor overlap >50%
- **If fails:** Hypothesis mechanism infeasible, stop without full training

**Phase 2: Hierarchical VAE Training**
- Architecture: 3-level VAE (encoders → pooling → Transformer)
- Training: Three-level supervision (coarse labels → contrastive triplet → zero-shot)
- Hyperparameters: Latent dim D=512, Transformer layers L=6, contrastive margin m=0.3

**Phase 3: Clustering Validation**
- Metric: Within-cluster sum of squares (WCSS) for same-task vs different-task pairs
- Statistical test: Bootstrap n=100, p<0.01 threshold
- Ablation: Remove architecture-type tokens → clustering should degrade by ≥15pp

**Phase 4: Zero-Shot Transfer**
- Test on adversarially mislabeled Hugging Face models (100% corrupted metadata)
- Success: >90% task prediction accuracy, >10pp over metadata baseline

**Ablation Studies:**
1. **Training Procedure vs Task**: Compare clustering for same-task different-procedure vs different-task same-procedure
2. **Architecture-Type Tokens**: Remove tokens, measure clustering degradation
3. **Pooling Strategy**: Test Set Transformer with memory vs mean pooling

---

## Limitations

### Acknowledged Scope Boundaries

1. **Discriminative Models Only**: Hypothesis explicitly scopes to CNNs, Transformers, RNNs, MLPs (discriminative function approximators). Generative models (GANs, Diffusion) excluded — weights encode sampling procedures, not discriminative functions. Deferred to future work.

2. **Inference Not Editing**: Permutation-invariant pooling (Level 2) discards neuron-level details required for fine-grained weight editing (task arithmetic, model merging). Scope limited to property inference (task prediction, clustering, zero-shot transfer). Editing requires invertible encoders — deferred to Phase 2 (future work).

3. **Dataset Coverage**: Requires ≥30 models per architecture-task cell for statistical validity. Sparse cells treated as robustness test rather than hard blocker.

4. **Training Procedure Confound**: Augmentation strategies may create more structure than task labels (Assumption A4). Explicit ablation required to disentangle sources of structure.

### Mitigation Strategies

| Limitation | Mitigation |
|-----------|------------|
| Dataset sparsity | Treat as natural experiment testing robustness to limited samples |
| Lossy pooling | Explore Set Transformer with memory (invertible pooling) in future work |
| Generative models | Reformulate task-semantic space to include "sample distribution X" as task type |
| Training confound | Run explicit ablation: same-task different-procedure vs different-task same-procedure |

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas reached consensus after 7 exchanges |
| **Clarity Verified** | Yes — core claim, mechanism, predictions all unambiguous |
| **Remaining Objections** | None — all 5 gaps addressed |
| **Phase 2B Readiness** | READY — proceed to research planning |

---

## Contribution Statement

**Scientific Contribution:** First demonstration that task-level functional constraints and training-induced regularities create architecture-invariant structural features in neural network weight distributions, enabling discovery of cross-architecture task similarity without shared base models.

**Practical Contribution:** Unlocks Hugging Face's 1M+ models as a queryable transfer learning resource via zero-shot cross-architecture model property inference on heterogeneous unlabeled collections.

**New Research Directions Enabled:**
1. **Model Archaeology**: Infer training data, augmentation strategies, optimization history from weights alone (forensics, provenance tracking)
2. **Architecture Search**: Explore design space via weight interpolation between architecture families (no shared ancestry required)
3. **Cross-Family Knowledge Distillation**: Transfer learned features across architectures without retraining (beyond current task arithmetic limitations)

---

## Next Steps

Proceed to **Phase 2B (Research Planning)** to develop detailed experimental roadmap, specify model zoo acquisition protocols, design CKA+UMAP feasibility gate implementation, and establish statistical analysis pipelines for clustering validation.
