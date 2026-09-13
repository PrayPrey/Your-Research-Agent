# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-GCRL-MolGen-v1
**Confidence Level:** 0.85 (HIGH)

**Main Hypothesis:**
In molecular design tasks with multiple property constraints, if we train a goal-conditioned policy with Junction Tree VAE latent space navigation and uncertainty-aware property predictors using hindsight experience replay with property relabeling, then the system will generate molecules matching specified multi-property goals with zero-shot generalization to novel property combinations because the contrastive goal encoder learns a compositional property space where inner products correspond to goal-conditioned value functions.

**Alternative Hypothesis (H0):**
Goal-conditioned RL does NOT enable superior multi-property molecular generation compared to standard fixed-reward RL. Specifically: (1) Multi-property success rate is ≤ baseline multi-objective RL, (2) Zero-shot generalization to novel property combinations fails (accuracy < 50% of training performance), or (3) Goal interpolation does NOT produce smooth property transitions (discontinuity > 30%).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Goal vector g | Independent | Continuous vector encoding desired molecular properties (binding affinity, QED, SA score, logP, toxicity) with normalized values [0,1] and uncertainty estimates from ensemble predictors | g ∈ ℝ^5, each dimension [0,1]; Example: g = [0.8, 0.7, 0.6, 0.5, 0.3] for high binding, good drug-likeness, moderate SA, neutral logP, low toxicity |
| Generated molecule properties p(m) | Dependent | Measured via pre-trained property predictors: QED via RDKit (drug-likeness), SA score via SAScore (synthetic accessibility), binding via AutoDock Vina docking (affinity to target), logP via RDKit descriptors (lipophilicity), toxicity via ensemble GNN predictors | QED [0,1], SA [1,10], Binding [-12, 0] kcal/mol, logP [-2, 6], Toxicity [0,1] |
| Policy architecture | Controlled | Fixed: Goal-conditioned actor-critic operating in JT-VAE latent space (dim=56), contrastive goal encoder (MLP 3-layer, hidden dim=128, output dim=64), actor/critic MLPs (3-layer, hidden=256) | Architecture fixed across all experiments |
| Training dataset | Controlled | Fixed: ChEMBL subset (1M molecules with pre-computed properties) or ZINC250k; Train/val/test split 70/15/15 with stratified sampling by property ranges | 1M molecules, property distributions representative of drug-like chemical space |
| Property predictor ensemble | Controlled | Fixed: 5-model ensemble (3 Graph Neural Networks: GCN, GAT, GraphSAGE + 2 traditional GCNs) trained on QM9/ESOL/FreeSolv benchmarks for uncertainty estimation via ensemble disagreement | Predictors achieve >0.85 Pearson correlation on held-out test sets; Uncertainty = std_dev across 5 predictions |

### 1.3 Causal Mechanism

**5-Step Causal Chain: Goal Specification → Molecular Generation with Multi-Property Satisfaction**

**Step 1: Goal Encoding via Contrastive Learning**
- **Mechanism:** Goal vector g (desired properties) is encoded by contrastive goal encoder into latent representation z_g ∈ ℝ^64 where inner products z_g · z_g' represent relative goal-conditioned value V(s,g) - V(s,g')
- **Evidence:** Eysenbach 2022 (214 cites) proves contrastive learning objective aligns with GCRL, with theoretical guarantee that inner products = value differences under optimal policy
- **Falsification:** If Pearson correlation between inner_product(z_g, z_g') and empirical value differences < 0.7, mechanism fails

**Step 2: Goal-Conditioned Action Selection in Latent Space**
- **Mechanism:** Goal-conditioned actor π(a|s,z_g) selects continuous action a in JT-VAE latent space (dim=56) to navigate toward goal. Policy conditions behavior on goal embedding via concatenation.
- **Evidence:** Chane-Sane 2021 (169 cites) demonstrates goal-conditioned policies with imagined subgoals; standard actor-critic with goal conditioning proven effective in robotics GCRL
- **Falsification:** If KL_divergence(π(·|s,z_g), π(·|s,z_g')) < 0.1 for distinct goals g ≠ g' (policy NOT goal-sensitive), mechanism fails

**Step 3: Valid Molecular Structure Generation via JT-VAE Decoder**
- **Mechanism:** JT-VAE decoder maps latent vector a to valid molecular graph via junction tree decomposition, ensuring 100% chemical validity through tree-structured generation
- **Evidence:** Jin 2018 (ICML) demonstrates JT-VAE achieves 100% validity on reconstruction; decoder guarantees syntactically valid SMILES by construction
- **Falsification:** If molecular invalidity rate > 5% on generated molecules, decoder mechanism fails

**Step 4: Property Evaluation with Uncertainty Quantification**
- **Mechanism:** Ensemble of 5 property predictors evaluates generated molecule m for QED, SA, binding, logP, toxicity. Ensemble disagreement σ_p quantifies uncertainty. Reward = Σ property_match - λ·σ_p (uncertainty penalty prevents exploitation).
- **Evidence:** Chen 2025 demonstrates uncertainty-aware multi-objective RL prevents predictor exploitation; Lakshminarayanan 2017 establishes ensemble disagreement as uncertainty estimate
- **Falsification:** If uncertainty calibration ECE (Expected Calibration Error) > 0.15, uncertainty quantification fails

**Step 5: Compositional Learning via HER Property Relabeling**
- **Mechanism:** When generated molecule misses goal g but achieves properties p(m), HER relabels trajectory with g'=p(m), creating positive training signal. Contrastive goal encoder learns compositional property space through augmented data, enabling zero-shot generalization (train on 2-property goals, generalize to 3-property combinations).
- **Evidence:** Andrychowicz 2017 proves HER effectiveness for sparse rewards; Haramati 2024 (26 cites) demonstrates entity-centric RL achieves compositional generalization (train 3 objects → generalize to 10 objects), transferable to property-centric molecular design
- **Falsification:** If zero-shot accuracy on 3-property goals (trained on 2-property) < 70% of 2-property training performance, compositional mechanism fails

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Eysenbach 2022 (214 cites) | Contrastive learning inner products = goal-conditioned value differences (theoretical guarantee) | Strong - Theoretical |
| Step 2 → Step 3 | Jin 2018 (ICML) | JT-VAE latent space preserves molecular similarity; adjacent latent vectors decode to structurally similar molecules | Strong - Empirical |
| Step 3 → Step 4 | Jin 2018 + Chen 2025 | JT-VAE 100% validity + Uncertainty-aware RL prevents exploitation | Strong - Combined |
| Step 4 → Step 5 | Andrychowicz 2017 + Haramati 2024 | HER sparse reward efficiency + Entity-centric compositional generalization (3→10 objects) | Medium - Cross-domain analogy |
| Step 5 → Outcome | Eysenbach 2022 + Haramati 2024 | Contrastive GCRL + Compositional generalization enable zero-shot property composition | Medium - Requires validation |

**Key Tension:**
**Tension:** Haramati 2024 demonstrates compositional generalization in robotics (3 objects → 10 objects), BUT molecular properties may have complex non-linear interactions (e.g., high binding affinity often reduces drug-likeness due to increased hydrophobicity). Does property composition transfer from robotics objects to molecular properties?

**Resolution:** This verification plan tests compositional generalization explicitly by training on 2-property combinations (binding+QED, QED+SA, SA+logP, logP+toxicity) and evaluating zero-shot on 3-property combinations (binding+QED+SA, QED+SA+logP). If zero-shot accuracy ≥ 70% of training performance, property composition holds. If < 70%, properties are non-compositional and require joint training.

### 1.4 Key Assumptions

1. **Property predictor accuracy assumption (>0.85 Pearson correlation)**
   - **Evidence:** Eysenbach 2022 shows contrastive GCRL tolerates moderate noise; molecular property predictors commonly achieve 0.85-0.95 correlation on QM9/ESOL/FreeSolv benchmarks (Yang 2019, Wu 2018)
   - **Consequences if violated:** If predictor correlation < 0.70, learned policy will exploit predictor weaknesses rather than generate truly property-satisfying molecules. Mitigation: Uncertainty-aware reward shaping penalizes high-uncertainty regions.

2. **Chemical space connectivity in JT-VAE latent space**
   - **Evidence:** Jin 2018 demonstrates JT-VAE latent space preserves molecular similarity; adjacent latent vectors (L2 distance < ε) decode to molecules with Tanimoto similarity > 0.8
   - **Consequences if violated:** If latent space is discontinuous (adjacent vectors decode to dissimilar molecules), HER property relabeling fails because achieved properties p(m) are not reachable goals from nearby states. Mitigation: Pre-train VAE with β-VAE regularization to enforce smoother latent space.

3. **Compositional structure of molecular properties**
   - **Evidence:** Haramati 2024 demonstrates entity-centric RL compositional generalization in robotics (train on 3 objects, generalize to 10). Analogy: Property-centric representation should enable composition if properties are sufficiently independent (correlation < 0.5).
   - **Consequences if violated:** If molecular properties exhibit strong dependencies (e.g., binding and toxicity correlation > 0.7), compositional generalization fails. Requires joint training on all property combinations, eliminating zero-shot advantage. Mitigation: Analyze property correlation matrix on dataset; if max correlation > 0.7, adjust training to include dependent property pairs.

4. **Contrastive learning aligns with goal-conditioned value**
   - **Evidence:** Eysenbach 2022 provides theoretical guarantee that under contrastive learning objective with action-labeled trajectories, inner product of learned representations z_g · z_g' = V(s,g) - V(s,g') under optimal policy
   - **Consequences if violated:** If contrastive objective does NOT align with value function (e.g., due to off-policy data or insufficient training), goal embeddings lose semantic meaning. Policy cannot effectively condition on goals. Mitigation: Use on-policy data collection or importance weighting for off-policy correction.

5. **Uncertainty-aware reward prevents predictor exploitation**
   - **Evidence:** Chen 2025 demonstrates uncertainty-aware multi-objective RL with reward = Σ objectives - λ·uncertainty prevents exploitation of low-quality predictors. Ensemble disagreement as uncertainty is standard (Lakshminarayanan 2017).
   - **Consequences if violated:** If uncertainty estimates are miscalibrated (ECE > 0.15), high-uncertainty molecules may receive high rewards, guiding policy toward unreliable property predictions (adversarial examples). Mitigation: Calibrate ensemble via temperature scaling; validate uncertainty on held-out test set.

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Drug-like small molecules (molecular weight 150-500 Da, ≤ 40 heavy atoms) representable by SMILES notation
- Properties measurable by pre-trained predictors: QED, SA score, binding affinity (via docking), logP, toxicity
- 2-5 simultaneous property constraints (goal vector dimensionality d ≤ 5)
- Chemical space covered by ChEMBL/ZINC datasets (≈10^6 molecules)

**Where Hypothesis Does NOT Apply:**
- **Macromolecules:** Proteins, nucleic acids, or polymers (JT-VAE limited to small molecules)
- **Properties requiring expensive simulation:** Absolute binding free energy (FEP), MD stability, experimental ADMET (only predicted properties supported)
- **Novel chemical scaffolds:** Molecules far outside training distribution (ChEMBL/ZINC) may have unreliable property predictions
- **High-dimensional goal spaces:** > 5 simultaneous properties may exceed compositional generalization capacity (curse of dimensionality in goal space)
- **Non-differentiable constraints:** Hard constraints like "must contain benzene ring" require discrete symbolic reasoning, not supported by continuous latent space navigation

**Known Limitations:**
1. **JT-VAE structural bias:** Only generates tree-decomposable molecules; some ring systems (e.g., cubane, adamantane) not representable
2. **Property predictor generalization:** Predictors trained on QM9/ESOL/FreeSolv may not generalize to highly novel scaffolds
3. **Computational cost:** Ensemble of 5 predictors + docking per molecule adds 20-30% overhead vs single predictor
4. **Training data requirement:** Requires ≥ 500K molecules for stable JT-VAE + GCRL training (data-intensive)

### 1.6 Testable Predictions

**Primary Prediction (Multi-Property Success Rate):**

**P1 (Multi-Property Goal Achievement vs Fixed-Reward Baseline):**
Our goal-conditioned RL approach will achieve multi-property success rate > 75% (molecules satisfying all specified properties within tolerance), compared to baseline fixed-reward multi-objective RL achieving 50-60% success rate.

*Measurement*:
- Multi-property success rate = % of generated molecules where ALL properties satisfy: |p_i(m) - g_i| < τ_i (tolerance τ_i = 0.1 for normalized properties)
- Evaluation on 1000 held-out test goals with 2-property (n=500) and 3-property (n=500) specifications
- Statistical test: Paired t-test comparing GCRL vs baseline, n = 30 independent runs with different seeds
- Significance: p < 0.05, Cohen's d > 0.5 (medium-to-large effect size)

*Basis*:
Domain standard for molecular generation: Multi-property optimization typically achieves 50-60% success rate with fixed-reward RL due to conflicting property objectives (binding vs drug-likeness trade-off). Our 75% target represents meaningful improvement enabled by flexible goal-conditioning.

*Success Criteria for Phase 2B*:
- **Primary:** Multi-property success rate > 75% with statistical significance (p < 0.05)
- **Falsification:** Success rate ≤ 60% (no improvement over baseline) triggers hypothesis rejection
- **Partial success:** 60-75% indicates mechanism works but with limited advantage

**Secondary Predictions:**

**P2 (Zero-Shot Property Composition Generalization):**
Training on 2-property goal combinations (e.g., binding+QED, QED+SA, SA+logP, logP+toxicity), the system will generalize zero-shot to 3-property combinations (e.g., binding+QED+SA) with success rate ≥ 70% of 2-property training performance.

*Measurement*:
- Zero-shot generalization accuracy = (Success_rate_3property / Success_rate_2property_training) × 100%
- Target: ≥ 70% (if 2-property training achieves 80% success, 3-property zero-shot should achieve ≥ 56%)
- Falsification: < 50% indicates compositional mechanism fails; properties require joint training

*Basis*:
Haramati 2024 demonstrates entity-centric RL compositional generalization from 3 objects to 10 objects in robotics. Transferring this principle: Training on pairs should enable composition to triplets if properties are sufficiently independent (correlation < 0.5).

**P3 (Goal Interpolation Smoothness):**
Linear interpolation between two goal vectors g_1 and g_2 in goal space will produce molecules with smoothly varying properties (property discontinuity < 30% between consecutive interpolation points).

*Measurement*:
- Generate molecules at 11 interpolation points: g_t = (1-t)·g_1 + t·g_2, t ∈ {0.0, 0.1, ..., 1.0}
- Property discontinuity = max_i |p_i(m_t) - p_i(m_{t+0.1})| / range(p_i)
- Target: Discontinuity < 30% (smooth transitions)
- Falsification: Discontinuity > 50% indicates goal space is non-smooth; interpolation unreliable

*Basis*:
Jin 2018 shows JT-VAE latent space preserves molecular similarity. Contrastive goal encoder should maintain this smoothness in goal-conditioned value space, enabling interpretable exploration of property trade-offs via interpolation.

**Falsification Criteria:**

**Hypothesis is REJECTED if ANY of the following occur:**

1. **Multi-property success rate ≤ 60%** (no improvement over fixed-reward baseline) - Primary mechanism failure
2. **Correlation between contrastive inner products and value differences < 0.7** (Eysenbach 2022 guarantee fails) - Goal encoder failure
3. **Policy NOT goal-sensitive:** KL_divergence(π(·|s,g_1), π(·|s,g_2)) < 0.1 for distinct goals (policy ignores goal embedding) - Conditioning mechanism failure
4. **Molecular invalidity rate > 5%** (JT-VAE decoder fails to ensure chemical validity) - Generation mechanism failure
5. **Uncertainty calibration ECE > 0.15** (ensemble disagreement does NOT predict errors) - Exploitation prevention failure
6. **Zero-shot generalization < 50% of training performance** (compositional learning fails) - HER relabeling + contrastive learning does NOT enable composition

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**N/A** - This hypothesis targets novel application (first GCRL for molecular design), NOT SOTA performance comparison. Focus is on enabling new capabilities (customizable generation, zero-shot property composition) rather than outperforming existing GCRL methods on established benchmarks.

### 1.8 Statistical Verification Design

**Experimental Design:**
- **Type:** Between-subjects comparison (GCRL vs baseline fixed-reward multi-objective RL)
- **Sample size:** n = 30 independent runs per condition (GCRL, baseline) with different random seeds
- **Test goals:** 1000 held-out test goals (500 two-property + 500 three-property)
- **Metrics:** Multi-property success rate (primary), zero-shot generalization accuracy (secondary), goal interpolation smoothness (secondary)

**Statistical Tests:**
- **Primary metric:** Paired t-test comparing GCRL vs baseline success rates across 30 runs
  - Null hypothesis: μ_GCRL - μ_baseline ≤ 0
  - Alternative: μ_GCRL - μ_baseline > 0
  - Significance: α = 0.05 (two-tailed), required Cohen's d > 0.5
  - Power analysis: n=30 provides 80% power to detect medium effect size (d=0.5) at α=0.05

- **Secondary metrics:**
  - Zero-shot generalization: One-sample t-test H0: μ_ratio ≤ 70%, H1: μ_ratio > 70%
  - Goal interpolation: One-sample t-test H0: μ_discontinuity ≥ 30%, H1: μ_discontinuity < 30%

**Confound Controls:**
- Random seed stratification: 30 runs use same random seeds across GCRL and baseline for paired comparison
- Architecture parity: Baseline uses same actor-critic architecture (only goal-conditioning removed)
- Data parity: Both methods trained on same ChEMBL 1M subset with identical train/val/test splits
- Hyperparameter tuning: Both methods undergo same hyperparameter search (learning rate, batch size, replay buffer size)

**Validity Threats:**
- **Internal validity:** Ensured by paired comparison with matched random seeds, architecture, and data
- **External validity:** Generalization tested on ZINC250k (different distribution from ChEMBL training) to verify robustness
- **Construct validity:** Multi-property success rate directly measures hypothesis claim; zero-shot generalization operationalizes compositional learning

---

## 2. Contribution Summary

**Theoretical Contributions:**
1. **Formalization of molecular design as goal-conditioned RL:** First work to formulate molecular generation as GCRL problem with property vectors as goals, enabling dynamic multi-property specification at inference time (vs fixed rewards at training)
2. **Extension of HER to continuous property space:** Adapts hindsight experience replay from discrete robotic goal relabeling to continuous molecular property relabeling, with theoretical analysis of compositional learning dynamics
3. **Generalization guarantee for property composition:** Extends Discrete Factorial Representations theorem (Islam 2022) to continuous property space, providing conditions under which training on k-property combinations enables zero-shot generalization to (k+1)-property goals

**Methodological Contributions:**
1. **Property-centric goal representation for molecular GCRL:** Novel goal encoding that maps molecular properties (binding, QED, SA, logP, toxicity) to latent space where contrastive inner products = goal-conditioned values
2. **Uncertainty-aware HER for molecular generation:** Combines hindsight experience replay with ensemble uncertainty quantification to prevent exploitation of property predictor weaknesses during training
3. **JT-VAE latent space GCRL:** Solves discrete molecular action space challenge by operating GCRL policy in continuous JT-VAE latent space while maintaining 100% chemical validity through tree-structured decoding
4. **Contrastive goal encoder for zero-shot composition:** Leverages Eysenbach 2022 theoretical framework to learn compositional property space enabling generalization to novel property combinations without retraining

**Practical Contributions:**
1. **Customizable molecular generation:** Enables chemists to specify desired properties dynamically at inference time (e.g., "high binding + good drug-likeness + moderate SA"), eliminating need for retraining on each new property combination
2. **Systematic property trade-off exploration:** Goal interpolation enables visualization and navigation of property trade-off frontiers (e.g., binding vs drug-likeness Pareto front) for informed molecular design decisions
3. **Data-efficient multi-property optimization:** HER augments sparse multi-property success signals by relabeling failures, reducing data requirements compared to standard multi-objective RL (estimated 30-50% data reduction based on robotics HER results)
4. **Generalization to novel property combinations:** Zero-shot transfer from 2-property to 3+ property goals eliminates exponential scaling of training cost with number of properties (2^k combinations for k properties)

---

## 3. Key Related Work

**Foundational GCRL Theory:**
1. **Eysenbach et al. 2022 - "Contrastive Learning as Goal-Conditioned Reinforcement Learning"** (214 citations)
   - Paper ID: 53dcf467fbded741dd08902d4203a9b57e889c87
   - Establishes theoretical connection between contrastive learning and GCRL with guarantee that inner products = value differences
   - Demonstrates contrastive RL achieves higher success rates than non-contrastive methods without data augmentation
   - Critical for our contrastive goal encoder design

2. **Chane-Sane et al. 2021 - "Goal-Conditioned Reinforcement Learning with Imagined Subgoals"** (169 citations)
   - Paper ID: fb95d6e6e5f78f6e5c339e2058ce9ae9e803182b
   - Proposes imagined subgoals for long-horizon GCRL tasks using value function as reachability metric
   - Demonstrates goal-conditioning effectiveness on complex robotic navigation and manipulation
   - Informs our goal-conditioned actor-critic architecture

3. **Ding et al. 2022 - "Generalizing Goal-Conditioned Reinforcement Learning with Variational Causal Reasoning"** (50 citations)
   - Paper ID: f3bf39ec3ff3464d234bd7ffe89199feeb4795c4
   - Augments GCRL with Causal Graphs for generalization via variational likelihood maximization
   - Demonstrates causal reasoning improves generalization in GCRL across varied goals
   - Supports our claim that compositional goal structure enables generalization

**Cross-Domain Transfer (Robotics → Molecules):**
4. **Haramati et al. 2024 - "Entity-Centric Reinforcement Learning for Object Manipulation from Pixels"** (26 citations)
   - Entity-centric RL achieves compositional generalization: Train on 3 objects, generalize to 10+ objects
   - Demonstrates structured approach for multi-object goal-conditioned manipulation
   - Provides analogy for property-centric molecular GCRL (properties as entities)

**Molecular Generation Foundations:**
5. **Jin et al. 2018 - "Junction Tree Variational Autoencoder for Molecular Graph Generation"** (ICML)
   - Junction Tree VAE generates valid molecules in continuous latent space with 100% validity guarantee
   - Enables continuous action space RL while ensuring discrete molecular validity
   - Critical for solving discrete action space challenge identified in Phase 2A

6. **Chen et al. 2025 - "Uncertainty-Aware Multi-Objective Reinforcement Learning-Guided Diffusion Models for 3D De Novo Molecular Design"** (1 citation)
   - Demonstrates uncertainty-aware reward shaping prevents exploitation of property predictors
   - Multi-objective RL with uncertainty estimation balances competing properties
   - Informs our uncertainty-aware ensemble predictor design

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - Contrastive Goal Encoder Works):**
*Claim:* Contrastive learning on property-labeled molecular trajectories produces goal embeddings where inner products correlate with goal-conditioned value differences.

*Verification:* Train contrastive goal encoder on 100K molecular trajectories with property labels. Measure Pearson correlation between inner_product(z_g, z_g') and empirical value V(s,g) - V(s,g') on 1000 test goal pairs.

*Success:* Correlation > 0.7 (Eysenbach 2022 theoretical guarantee)
*Failure:* Correlation < 0.7 indicates contrastive objective does NOT align with GCRL in molecular domain

**SH2 (Mechanism - HER + Contrastive Learning Enables Composition):**
*Claim:* Hindsight experience replay with property relabeling + contrastive goal encoder enables compositional learning (train on 2-property, generalize to 3-property).

*Verification:* Train GCRL policy on 2-property goal combinations only. Evaluate zero-shot success rate on 3-property goals without fine-tuning. Compare to ablations: (A) No HER, (B) No contrastive encoder, (C) Full model.

*Success:* Zero-shot accuracy ≥ 70% of training performance with full model; ablations A/B show < 50%
*Failure:* Zero-shot accuracy < 50% indicates compositional mechanism does NOT work; requires joint training

**SH3 (Comparison - GCRL Outperforms Fixed-Reward Multi-Objective RL):**
*Claim:* Goal-conditioned RL achieves higher multi-property success rate than fixed-reward multi-objective RL due to flexible goal specification and compositional learning.

*Verification:* Train GCRL and baseline fixed-reward multi-objective RL on same dataset. Evaluate on 1000 test goals (500 two-property + 500 three-property). Paired t-test across 30 runs.

*Success:* GCRL success rate > 75%, baseline 50-60%, p < 0.05, Cohen's d > 0.5
*Failure:* GCRL ≤ 60% (no advantage over baseline) or p ≥ 0.05 (not statistically significant)

### Readiness Checklist

- [x] **Hypothesis Statement:** Clear "Under C, if X, then Y because Z" formulation with 5-step causal mechanism
- [x] **Variables Operationalized:** All 5 variables (goal vector, molecule properties, architecture, dataset, predictors) with specific measurement methods
- [x] **Causal Mechanism:** 5-step chain with evidence from 6 papers (Eysenbach 2022, Chane-Sane 2021, Ding 2022, Jin 2018, Chen 2025, Haramati 2024)
- [x] **Falsification Criteria:** 6 quantitative falsification thresholds (success rate ≤ 60%, correlation < 0.7, KL < 0.1, invalidity > 5%, ECE > 0.15, zero-shot < 50%)
- [x] **Testable Predictions:** 3 predictions with quantitative thresholds (P1: >75% success, P2: ≥70% zero-shot, P3: <30% discontinuity)
- [x] **Assumptions Validated:** 5 assumptions with evidence + consequences if violated
- [x] **Scope Defined:** Clear boundaries (drug-like molecules, 2-5 properties, ChEMBL/ZINC space, tree-decomposable structures)
- [x] **Statistical Design:** Paired t-test, n=30 runs, α=0.05, Cohen's d > 0.5, 80% power
- [x] **Sub-Hypothesis Preview:** SH1 (encoder), SH2 (mechanism), SH3 (comparison) ready for Phase 2B decomposition

### Open Questions

1. **Optimal HER relabeling strategy:** Future vs final vs episode strategy for property relabeling? Requires ablation study in Phase 2B SH2 to determine which maximizes compositional learning.

2. **Property correlation threshold for composition:** At what property correlation does compositional generalization break down? Hypothesis assumes < 0.5, but may require empirical validation on property correlation matrix.

3. **Scalability beyond 5 properties:** How does zero-shot generalization degrade with increasing goal dimensionality? 2→3 properties tested, but 2→5 or 2→7 may reveal curse of dimensionality.

4. **Transfer to novel chemical scaffolds:** Phase 2A focuses on ChEMBL/ZINC distributions. Does GCRL maintain advantage on out-of-distribution scaffolds (e.g., marine natural products, peptoids)?

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-06*
