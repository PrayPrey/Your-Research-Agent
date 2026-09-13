# Phase 2B: Hypothesis Summary - CNI-Auto

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## Clarified Hypothesis

### Hypothesis ID
**H-CNI-Auto** (Causal Neuron Intervention for Automated Spurious Detection)

### Core Statement

**Main Hypothesis:**
Neurons encoding spurious correlations exhibit significantly higher observational-interventional discrepancy under distribution shift compared to core feature neurons. By systematically intervening on neuron activations and measuring this discrepancy metric, we can automatically identify spurious feature detectors without manual group annotations.

**Alternative Hypothesis (H0):**
Spurious and core neurons show similar observational-interventional discrepancy patterns under distribution shift, making automated distinction infeasible.

### Variables

| Type | Variable | Operationalization | Range/Scale |
|------|----------|-------------------|-------------|
| Independent | Neuron intervention type | Ablation (set to 0) or activation (set to mean) | Binary choice |
| Independent | Distribution shift type | Natural (validation set) or synthetic (augmentation) | Categorical |
| Dependent | Observational correlation | Pearson correlation between neuron activation and prediction on train set | [-1, 1] |
| Dependent | Interventional causality | Accuracy change when neuron is intervened upon, measured on shifted distribution | [0, 1] |
| Dependent | OI discrepancy score | \|observational_corr\| - interventional_effect | [-1, 1] |
| Controlled | Model architecture | Fixed (e.g., ResNet-50) | - |
| Controlled | Training procedure | Standard ERM training | - |
| Controlled | Dataset | Benchmark with known spurious correlations (Waterbirds, CelebA) | - |

### Causal Mechanism

**Mechanism:**
Spurious neurons learn decision rules based on correlations that exist in training data but break under distribution shift (e.g., "water background → waterbird"). These neurons show:
1. **High observational correlation** on training data (neuron fires → correct prediction due to spurious correlation)
2. **Low interventional causality** under shift (ablating neuron doesn't affect accuracy because correlation is broken)

Core neurons learn invariant features (e.g., "bird shape → bird class") and show:
1. **High observational correlation** on training data (neuron fires → correct prediction due to causal relationship)
2. **High interventional causality** under shift (ablating neuron degrades accuracy because feature is causal)

**Evidence for Causal Links:**
- **Link 1 (Simplicity Bias → Spurious Learning):** Shah et al. (2020, 422 cites) proves DNNs exclusively rely on simplest features, explaining preference for spurious correlations
- **Link 2 (Neuron Specialization):** XAI literature (2025) demonstrates neurons specialize to specific features; spurious neurons specialize to spurious patterns
- **Link 3 (Distribution Shift Reveals Causality):** Causal inference theory (Pearl's do-calculus) establishes interventional distributions reveal causal vs correlational relationships

**Key Tension:**
The hypothesis assumes spurious correlations manifest in identifiable neuron groups rather than being fully distributed across the network. If representations are too distributed, neuron-level intervention may fail to reveal spurious dependencies.

### Key Assumptions

1. **Localized Representation:** Spurious correlations manifest in localized neuron groups (not fully distributed across network)
   - **Justification:** XAI research shows neurons specialize; feature visualization shows interpretable neuron activations
   - **Testability:** Can verify via neuron clustering - spurious neurons should cluster together

2. **Distribution Shift Availability:** Access to either natural shifts (validation sets from different distributions) or synthetic shifts (augmentation)
   - **Justification:** Most realistic deployment scenarios have some form of distribution variation
   - **Fallback:** Synthetic shift generation via augmentation (rotation, color jitter for vision; paraphrase for NLP)

3. **Threshold Separability:** Spurious and core neurons have distinguishable OI discrepancy distributions with learnable decision boundary
   - **Justification:** Theoretical distinction is qualitative (spurious breaks under shift, core maintains); should manifest in quantitative metric
   - **Testability:** Can validate on benchmarks with known spurious features (Waterbirds, CelebA)

4. **Neuron Redundancy is Limited:** Ablating individual neurons or small groups reveals causal role (network doesn't fully compensate via redundancy)
   - **Justification:** While DNNs have redundancy, neuron ablation studies show individual neurons contribute meaningfully
   - **Mitigation:** Group intervention testing for highly redundant architectures

### Scope & Boundaries

**Applies To:**
- Supervised deep neural networks (CNNs, Transformers) with accessible neuron activations
- Tasks with available distribution shifts (natural or synthetic)
- Image classification, text classification, multimodal classification

**Does NOT Apply To:**
- Black-box models without activation access (API-only LLMs)
- Settings with zero distribution shift information (single static dataset)
- Regression tasks (requires modification for continuous outputs)

**Known Limitations:**
- Threshold calibration requires small validation set (but NO group labels)
- Large models (billion-parameter LLMs) require neuron sampling for computational feasibility
- Synthetic shifts may not perfectly capture real distribution shifts (approximation gap)

### Testable Predictions

**Primary Prediction (P1):**
If we measure OI discrepancy on Waterbirds dataset (known spurious: water background), THEN neurons with high discrepancy (>75th percentile) will have >70% overlap with neurons that activate strongly on background features (verified via feature visualization or saliency maps).

**Secondary Predictions:**

**P2 (Clustering):**
If we cluster neurons by activation patterns and flag high-discrepancy neurons, THEN flagged neurons will form distinct clusters corresponding to known spurious patterns (e.g., background cluster, texture cluster).

**P3 (Worst-Group Improvement):**
If we retrain last layer while freezing flagged spurious neurons (force them to 0), THEN worst-group accuracy will improve by ≥5% compared to standard retraining without intervention.

**Falsification Criteria:**
- If P1 overlap < 40%, hypothesis is falsified (spurious neurons not detected)
- If P3 improvement < 2%, hypothesis has no practical utility
- If core neurons also show high OI discrepancy (>60% of core neurons in high discrepancy group), metric fails to distinguish

### Statistical Verification Design

**Experiment 1: Controlled Validation (Waterbirds)**
- Dataset: Waterbirds (known spurious correlation: water background)
- Method: Compute OI discrepancy for all neurons in final conv layer
- Validation: Compare high-discrepancy neurons to ground truth spurious feature detectors (via saliency maps)
- Metrics: Precision, Recall, F1 of spurious neuron detection
- Statistical test: Chi-square test for independence between high discrepancy and spurious feature activation
- Significance threshold: p < 0.05

**Experiment 2: Blind Discovery (CelebA)**
- Dataset: CelebA (unknown spurious correlations to discover)
- Method: Run CNI-Auto without prior knowledge, cluster flagged neurons
- Validation: Manual inspection of discovered clusters + comparison to known biases (e.g., gender, age)
- Metrics: Number of interpretable clusters discovered, cluster coherence score
- Success: Discover ≥2 interpretable spurious patterns

**Experiment 3: Robustness Improvement (Both datasets)**
- Method: Last-layer retraining with spurious neurons frozen
- Baseline: Standard last-layer retraining (DFR)
- Metrics: Worst-group accuracy, average accuracy, accuracy gap
- Statistical test: Paired t-test for worst-group accuracy improvement
- Significance: p < 0.05, effect size Cohen's d > 0.5

---

## Contribution Summary

### Theoretical Contribution
**Formal characterization of spurious vs core neurons via observational-interventional discrepancy**
- Extends causal inference framework (Pearl's do-calculus) to neuron-level DNN analysis
- Provides mathematical grounding for why spurious features are detectable: they exhibit high correlation under observational distribution but weak causal effect under interventional distribution
- Bridges XAI interpretability (neuron analysis) with causal inference (intervention theory)

### Methodological Contribution
**CNI-Auto Algorithm: 5-step automated spurious neuron detection**
1. Measure observational correlation (neuron activation vs prediction on train set)
2. Systematically intervene (ablate/activate neurons)
3. Measure interventional effect under distribution shift
4. Calibrate OI discrepancy threshold via cross-validation
5. Cluster flagged neurons to discover unknown patterns

**Key Innovation:** First method to combine neuron-level causal intervention with distribution shift testing for automated spurious detection

### Practical Contribution
**Proactive spurious pattern discovery for deployment safety**
- Enables identification of hidden shortcuts before model deployment
- No manual group annotation required (unlike Group DRO, IRM)
- Computational overhead: ~2-3x forward passes (affordable for pre-deployment analysis)
- Applicable across modalities: vision, NLP, multimodal
- Provides actionable mitigation: freeze/retrain flagged neurons

---

## Key Related Work

### XAI Interpretability (Foundation)
- **XAI shortcut analysis (2025):** Neuron spurious score concept - we extend with causal intervention framework
- **Feature visualization literature:** Validates neuron specialization assumption

### Causal Inference (Theoretical Basis)
- **Pearl's do-calculus:** Interventional vs observational distributions - we apply to neuron-level DNN analysis
- **Neuroscience causal intervention studies:** Systematic ablation protocols - we adapt to artificial neurons

### Spurious Correlation Detection (Related Methods)
- **Medical AI (2024):** Data-intrinsic detection without external data - we extend to neuron-level with causality
- **Shortcut Learning survey (Geirhos 2020):** Taxonomy of shortcuts - we provide detection method

### Robustification Methods (Comparison Baselines)
- **Group DRO:** Requires group labels - our method is label-free
- **IRM:** Requires multiple environments - our method works with single dataset + shifts
- **DFR (Deep Feature Reweighting):** Last-layer retraining - our method identifies which neurons to target

---

## Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
Spurious neurons exhibit measurably higher observational-interventional discrepancy (≥0.3 difference) compared to core neurons under distribution shift.

**SH2 (Mechanism):**
The OI discrepancy arises because spurious neurons rely on correlations that break under shift, while core neurons encode invariant causal features.

**SH3 (Comparison):**
CNI-Auto achieves ≥10% higher precision in spurious neuron detection compared to correlation-based baselines (simple neuron activation analysis without intervention).

### Readiness Checklist

- [x] Core hypothesis clearly stated with falsifiable predictions
- [x] Variables operationalized with measurement procedures
- [x] Causal mechanism articulated with supporting evidence
- [x] Key assumptions explicitly listed with justification
- [x] Scope and boundaries defined
- [x] Statistical verification design specified
- [x] Contributions differentiated from related work
- [x] Sub-hypothesis preview for Phase 2B decomposition

### Open Questions for Phase 2B

1. **Threshold Calibration:** What is optimal percentile cutoff for high discrepancy? (P1 uses 75th - needs empirical validation)
2. **Neuron Sampling Strategy:** For large models, which neurons to sample? (layer-wise, random, activation-based?)
3. **Synthetic Shift Quality:** What augmentation strategies best approximate natural shifts? (domain-specific tuning needed)
4. **Clustering Algorithm:** K-means, hierarchical, or DBSCAN for spurious pattern discovery? (experiment needed)
5. **Intervention Strength:** Ablation (0) vs activation (mean) vs continuous intervention - which reveals causality best?

---

**For Full Details:** See `02a_extended_hypothesis_full.md`

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-08*
