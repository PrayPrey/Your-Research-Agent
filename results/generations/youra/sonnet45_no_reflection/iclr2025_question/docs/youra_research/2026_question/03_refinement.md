# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-12T00:58:55Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: GAP-2
- **Gap Title**: Real-time Uncertainty Estimation for Production Deployment
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 7

**Convergence Reason**: All convergence criteria met after 7 exchanges - specific core claim stated, causal mechanism explained, 3 testable predictions with criteria, novelty articulated, feasibility established (moderate), major criticisms addressed with mitigation strategies

### Key Insights

1. **Geometric properties as uncertainty encoding**: Hidden states may intrinsically encode uncertainty through spectral geometry (participation ratio, eigenvalue decay), not requiring supervised training
2. **Collapsed subspace hypothesis**: For epistemic uncertainty tasks, uncertain states exhibit lower-dimensional geometric signatures (negative correlation between PR and semantic entropy)
3. **Production viability**: Single-pass computation (<10ms) enables real-time deployment where multi-sample methods (500-2000ms) fail
4. **Interpretability advantage**: Geometric features reveal WHY uncertainty is detected (subspace compression) vs black-box probe predictions

### Breakthrough Moments

1. **Exchange 1 (Dr. Nova)**: Paradigm shift from approximating multi-sample methods to recognizing intrinsic geometric uncertainty signals - "What if the model's internal representation geometry already encodes the uncertainty signal we're looking for?"
2. **Exchange 3 (Prof. Pax)**: Mechanism paradox identification - collapsed subspace vs superposition predict opposite correlations, requiring theoretical clarity
3. **Exchange 4 (Dr. Sage)**: Uncertainty type decomposition - epistemic (collapsed) vs aleatoric (superposition) resolves the paradox
4. **Exchange 5 (Dr. Ally)**: Synthesis and refinement - negative correlation prediction for epistemic uncertainty with clear falsifiers
5. **Exchange 7 (Dr. Nova)**: Multi-geometric expansion - participation ratio as one feature in richer uncertainty manifold

---

## Final Hypothesis

### Title
Geometric Uncertainty Quantification via Hidden State Subspace Analysis

### Hypothesis ID
H-GeometricUQ-v1

### Core Claim

**Under** epistemic uncertainty conditions (factual knowledge questions in TruthfulQA),  
**If** we extract geometric features (participation ratio, eigenvalue spectrum, condition number) from layers 24-31 hidden states at pre-generation final token position,  
**Then** these features will achieve Spearman |ρ| > 0.4 correlation with ground-truth semantic entropy,  
**Because** uncertain model states exhibit lower-dimensional geometric signatures (collapsed subspaces) detectable via spectral analysis of the hidden state manifold.

### Mechanism

When an LLM encounters a factual question where it lacks confident knowledge (epistemic uncertainty), its pre-generation hidden states collapse into lower-dimensional subspaces due to lack of confident direction. This geometric compression manifests as:

1. **Participation ratio decrease** - effective dimensionality reduces
2. **Eigenvalue decay acceleration** - spectral concentration increases
3. **Condition number increase** - max/min eigenvalue ratio grows

These spectral signatures serve as intrinsic uncertainty signals without requiring multi-sample generation or external NLI models.

---

## Predictions

### P1 (Primary - EXISTENCE)
**Statement**: Participation ratio from layers 24-31 hidden states shows Spearman |ρ| > 0.4 with semantic entropy on TruthfulQA test set

**Test Method**: Compute Spearman rank correlation between PR and SE on 245-example held-out test set

**Success Criterion**: Spearman |ρ| > 0.4, 95% confidence interval excluding 0.3, p < 0.001

**Falsification**: |ρ| < 0.3 OR p > 0.05 OR confidence interval includes 0

### P2 (Secondary - PERFORMANCE)
**Statement**: Multi-geometric feature ensemble (PR + eigenvalue decay + condition number) achieves AUROC > 0.70 for binary high/low uncertainty classification

**Test Method**: Train simple linear classifier on geometric features, evaluate on test set with bootstrap confidence intervals

**Success Criterion**: AUROC > 0.70 with 95% CI excluding 0.65

**Falsification**: AUROC < 0.65 or not significantly better than random (0.50)

### P3 (Secondary - INCREMENTAL VALUE)
**Statement**: Geometric features add predictive value (ΔAUROC ≥ 0.05) beyond perplexity-only baseline

**Test Method**: Hierarchical regression - perplexity baseline → add geometric features, measure AUROC improvement via DeLong test

**Success Criterion**: ΔAUROC ≥ 0.05, DeLong test p < 0.05

**Falsification**: ΔAUROC < 0.03 or improvement not statistically significant

---

## Novelty

**Key Innovation**: Intrinsic geometric properties (participation ratio, spectral features) as interpretable uncertainty signals requiring only single forward pass, no supervised training needed for feature extraction.

**Differentiation from Prior Work**:

| Prior Work | Method | Our Difference |
|------------|--------|----------------|
| Kossen et al. (2024) | Train supervised probe to predict SE | We use intrinsic geometry (interpretable, no training) |
| Farquhar et al. (2024) | Semantic entropy via K=10 samples + NLI | We approximate with <10ms geometry computation |
| SelfCheckGPT (2023) | Sampling-based consistency (5-20 samples) | We achieve single-pass inference |

**Paradigm Shift**: From "approximate expensive methods" to "recognize intrinsic geometric uncertainty language"

---

## Experimental Design

### Dataset
- **Name**: TruthfulQA (generation config)
- **Source**: HuggingFace datasets
- **Size**: 817 questions total
- **Split**: 70/30 train/test (572 train, 245 test)
- **Fit**: Designed to elicit epistemic uncertainty - factual questions where models lack knowledge

### Model
- **Primary**: Llama-3-8B-Instruct (meta-llama/Meta-Llama-3-8B-Instruct)
- **Architecture**: Decoder-only transformer, 32 layers, 4096 hidden dim
- **Validation**: Llama-2-7B (architecture-invariance check)
- **Inference**: Frozen, bfloat16 precision

### Ground Truth
- **Semantic Entropy**: Computed via K=10 samples at T=0.7
- **NLI Model**: DeBERTa-v3-base-mnli-fever-anli
- **Clustering**: Bidirectional entailment clustering (Farquhar et al. 2024 method)

### Feature Extraction
- **Layers**: 24-31 (final 8 layers before output)
- **Position**: Final token before generation starts
- **Features**:
  - Participation ratio: trace(C)² / (||C||²_F × d)
  - Eigenvalue decay rate: power law α in λ_k ∝ k^(-α)
  - Condition number: max eigenvalue / min eigenvalue

### Baselines
1. **Perplexity**: Token-level perplexity from model logits
2. **Sequence Length**: Input length as confound control
3. **Kossen et al. Probe** (reference): Trained hidden state probe predicting SE

### Evaluation Metrics
- **Primary**: Spearman rank correlation ρ
- **Secondary**: AUROC, Pearson r, MAE, hierarchical regression ΔR²
- **Stability**: Bootstrap coefficient of variation (target CV < 0.15)

---

## Limitations

### Known Constraints
1. **Layer selection**: Layers 24-31 chosen based on proximity to output; may need adjustment for different model sizes
2. **Statistical stability**: Participation ratio from 9 samples may be unstable; requires empirical validation (bootstrap CV < 0.15)
3. **Architecture scope**: Initially validated on Llama-family; generalization to GPT-2/Mistral/Gemma requires testing
4. **Uncertainty type**: Scoped to epistemic uncertainty; aleatoric uncertainty may exhibit opposite pattern

### Does Not Address
- Cross-domain generalization beyond TruthfulQA
- Real-time latency validation in production environment
- Calibration across different confidence thresholds
- Adversarial robustness of geometric features

### Mitigation Strategies
- **Layer selection**: Ablation study across layer ranges (16-23, 20-27, 24-31)
- **Stability**: Multi-metric ensemble compensates for individual metric noise
- **Architecture**: Explicit scoping to Llama with planned cross-architecture validation
- **Position specification**: Precise protocol for different prompt formats

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met (7 exchanges) |
| **Clarity Verified** | Yes |
| **Novelty** | Strong |
| **Falsifiability** | Strong |
| **Significance** | Strong |
| **Feasibility** | Moderate (requires empirical validation) |
| **Remaining Objections** | Layer/position justification, PR stability proof, architecture generalization |

---

## Phase 2B Readiness

**Status**: READY

**SH1 (Existence)**: Geometric features must correlate with semantic entropy - Spearman |ρ| > 0.4, p < 0.001

**SH2 (Mechanism)**: Subspace collapse validated - participation ratio decreases as semantic entropy increases (negative correlation)

**SH3 (Comparison)**: Performance vs baselines - compare AUROC against Kossen et al. probe and perplexity baseline

**Open Questions**:
- Optimal layer range (ablation: 16-23, 20-27, 24-31)
- Multi-metric combination (linear vs PCA vs ensemble)
- Cross-architecture protocol (Llama → GPT-2/Mistral)
- Small-sample PR stability guarantee (bootstrap CV < 0.15)

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Convergence achieved after 7 exchanges*
*Ready for Phase 2B: Research Planning*
