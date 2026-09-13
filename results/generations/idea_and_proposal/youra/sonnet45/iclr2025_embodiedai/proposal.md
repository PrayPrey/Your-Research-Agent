# Research Proposal: Hierarchical Domain Bridging for Weather-Robust LLM-Based Outdoor Navigation

## 1. Title

**Hierarchical Domain Bridging for Weather-Robust LLM-Based Outdoor Navigation: Meta-Learning Perception with Zero-Shot Spatial Reasoning**

---

## 2. Introduction

### 2.1 Background

Embodied artificial intelligence has made remarkable progress in indoor environments, with agents achieving 75-85% success rates in simulation-based navigation tasks. However, the transition to outdoor urban environments presents fundamental challenges that remain largely unsolved. Current LLM-based embodied agents struggle with outdoor navigation, experiencing performance drops of ≥25 percentage points when deployed from simulation to real-world conditions, with success rates typically below 50-60%.

The outdoor environment introduces three critical challenges absent in indoor settings: (1) **weather and lighting variations** that dramatically alter visual appearance (clear vs. foggy vs. rainy conditions, day vs. night), (2) **large-scale spatial reasoning** requirements across city blocks rather than rooms, and (3) **massive sim-to-real gaps** due to the complexity of modeling atmospheric effects, dynamic elements (pedestrians, vehicles), and sensor degradation in adverse conditions.

Recent advances have established promising foundations. CityEQA (2025) demonstrated that hierarchical Planner-Manager-Actor architectures can achieve 60.7% human-level performance on city-scale navigation tasks in simulation. SpatialPrompt (2024) showed that instructing LLMs to use reference objects improves spatial reasoning by +56.2 points on Gemini 1.5 Pro. Meta-learning approaches like CoDeGa (2023) have proven effective for few-shot adaptation to large domain shifts in manipulation tasks. However, these advances remain disconnected—no existing work integrates meta-learned perception, zero-shot LLM reasoning, and systematic sim-to-real bridging for outdoor embodied agents.

The fundamental insight motivating this research is that **perception and reasoning require fundamentally different adaptation strategies**. Perception modules must adapt to low-level domain shifts (weather-induced appearance changes, lighting variations, sensor noise), while reasoning modules can leverage pre-trained language knowledge through appropriate prompting without fine-tuning. Current approaches either attempt expensive end-to-end fine-tuning (requiring thousands of samples and access to LLM weights) or rely on zero-shot transfer without adaptation (achieving only ~50% success rates). Neither approach exploits the hierarchical structure of the problem.

### 2.2 Research Objectives

This research proposes **hierarchical domain bridging** that separates perception adaptation from reasoning transfer, with three primary objectives:

**Objective 1: Develop meta-learned perception modules** that achieve ≥70% semantic segmentation accuracy (mIoU) on real-world outdoor scenes across 5-10 weather/lighting conditions, using only 10-50 labeled samples per condition for adaptation. This represents a ≥15 percentage point improvement over direct sim-to-real transfer baselines (~55% mIoU).

**Objective 2: Enable zero-shot LLM spatial reasoning transfer** that maintains ≥90% of simulation performance in real-world embodied navigation through spatial prompting techniques (reference objects + keyframes), without fine-tuning LLM parameters.

**Objective 3: Achieve ≥70% end-to-end outdoor navigation success rate** with ≤10 percentage point reality gap (sim-to-real performance drop), validated on 100 real-world navigation tasks across multiple weather conditions. This surpasses both direct transfer baselines (≤50%) and simulation-only state-of-the-art (CityEQA: 60.7%).

The research will validate these objectives through a complete pipeline: meta-training in MetaUrban simulation → GAN-based progressive domain bridging → source-free domain adaptation → real-world deployment in a 2km² urban area.

### 2.3 Significance

This research addresses critical gaps at the intersection of embodied AI, large language models, and outdoor robotics:

**Scientific Significance:**

1. **Theoretical Framework for Hierarchical Adaptation**: Formalizes the principle that perception requires domain adaptation (meta-learning) while reasoning requires only prompting (zero-shot) for outdoor embodied LLM agents. This challenges the prevailing assumption that all components need fine-tuning for domain transfer.

2. **Quantification of Outdoor Reality Gap**: Provides the first systematic decomposition of sim-to-real gaps for outdoor embodied agents into measurable components (weather-induced, lighting-induced, dynamic element-induced), extending existing indoor-focused reality gap theory.

3. **Meta-Learning Extension to Multi-Modal Agents**: Extends Controlled Deployment Gaps (CoDeGa) meta-learning framework to vision-language hierarchical agents with asymmetric adaptation strategies.

**Practical Significance:**

1. **Sample-Efficient Deployment**: Reduces real-world data requirements by 5-10× (from hundreds to 10-50 samples per condition), making outdoor embodied AI deployment feasible for research teams without large-scale data infrastructure.

2. **Zero-Shot LLM Integration**: Enables use of commercial LLM APIs (Gemini, GPT-4) without fine-tuning, reducing computational costs from $10k-100k to near-zero for LLM adaptation while maintaining superior spatial reasoning performance.

3. **Standardized Benchmark**: Establishes the first outdoor sim-to-real benchmark for LLM-based embodied agents (MetaUrban→Real protocol), enabling reproducible comparison across methods.

**Application Impact:**

The proposed approach directly addresses workshop topics (1) Spatial Intelligence and Embodied Perception, (2) Reasoning and Planning, and (3) Simulator/Benchmark Development. Successful validation would enable practical applications including autonomous delivery robots operating across weather conditions, urban surveillance systems with weather-robust perception, and assistive navigation for visually impaired users in outdoor environments. The modular architecture allows independent improvement of perception and reasoning components, accelerating development through parallel research efforts.

---

## 3. Methodology

### 3.1 Research Design Overview

The methodology follows a hierarchical experimental design with four integrated components validated through systematic ablation studies:

**Component 1**: Meta-learned perception module (weather-robust semantic segmentation)  
**Component 2**: Spatial prompting for LLM reasoning (zero-shot transfer)  
**Component 3**: GAN-based progressive domain bridging (sim-to-real gap reduction)  
**Component 4**: Source-free domain adaptation (real-world deployment)

The causal mechanism flows through five validated links:

$$\text{Meta-Training Diversity} \xrightarrow{\text{Link 1}} \text{Condition-Invariant Features} \xrightarrow{\text{Link 2}} \text{Few-Shot Real Adaptation} \xrightarrow{\text{Link 3}} \text{Semantic Understanding} \xrightarrow{\text{Link 4}} \text{Zero-Shot LLM Reasoning} \xrightarrow{\text{Link 5}} \text{Navigation Success}$$

### 3.2 Data Collection

**3.2.1 Simulation Data (Meta-Training)**

**Platform**: MetaUrban (ICLR 2025) simulator with weather/season variation support, or EmbodiedCity (2024) extended with weather rendering if MetaUrban lacks sufficient weather parameters.

**Weather Conditions** (5-10 conditions for meta-training):
- Clear day (baseline)
- Overcast (diffuse lighting)
- Light fog (visibility 100-200m)
- Heavy fog (visibility 50-100m)
- Light rain (wet surfaces, moderate visibility)
- Heavy rain (reduced visibility, sensor noise)
- Dusk (low-angle lighting, long shadows)
- Night (artificial lighting only)
- Night + rain (combined challenge)
- Snow (optional, if simulator supports)

**Data Volume**: 
- 50,000 RGB-D frames per weather condition (500,000 total for 10 conditions)
- Semantic segmentation labels: 20 classes (road, sidewalk, building, vehicle, pedestrian, vegetation, sky, traffic sign, etc.)
- GPS coordinates, IMU data, camera poses for each frame
- Navigation task annotations: 1,000 tasks per condition (10,000 total) with goal locations and optimal paths

**3.2.2 GAN Intermediate Domain Generation**

**Architecture**: CycleGAN with progressive style transfer

**Training Protocol**:
1. Train 3-5 CycleGAN models for progressive transformation:
   - GAN₁: Simulation → Light realism (subtle texture changes)
   - GAN₂: Light → Medium realism (atmospheric effects)
   - GAN₃: Medium → Heavy realism (sensor noise, dynamic elements)
   - GAN₄: Heavy → Real-world appearance (full transfer)

2. **Semantic Consistency Validation**: For each GAN output, verify that semantic labels remain >90% consistent (mIoU between original and style-transferred labels).

3. Generate 10,000 intermediate domain images per GAN step (30,000-50,000 total).

**3.2.3 Real-World Data Collection**

**Location**: San Francisco downtown 2km² area (or equivalent urban environment with diverse landmarks, moderate pedestrian/vehicle density).

**Equipment**:
- Ground robot platform: Clearpath Jackal or equivalent (wheeled, 0.5-2 m/s)
- Sensors: Intel RealSense D435i (RGB-D), GPS module (2-5m accuracy), IMU
- Compute: NVIDIA Jetson Orin (edge processing) + cloud LLM API access

**Collection Protocol**:
- **Weather Coverage**: Collect data across 4-5 weather conditions (clear, overcast, light fog, light rain, dusk). Wait for natural weather variation or collect in multiple cities if timeline permits.
- **Sample Size**: 10-50 labeled images per weather condition for adaptation (40-250 total), plus 100 unlabeled images per condition for validation (500 total).
- **Labeling**: 3 independent annotators per image, majority vote for disagreements. Use Labelbox or CVAT annotation interface with 20-class semantic segmentation schema matching simulation.
- **Navigation Tasks**: 100 real-world tasks (20 per weather condition) with manually verified goal locations, distance thresholds (2m), and time limits (30 min).

**3.2.4 Spatial Reasoning Query Dataset**

- **Simulation Queries**: 500 spatial reasoning questions from EmbodiedCity/MetaUrban navigation scenarios ("Is the fountain north of the statue?", "How far is the library from the pharmacy?").
- **Real-World Queries**: 200 spatial questions from real-world navigation tasks, manually verified ground truth.

### 3.3 Algorithmic Steps

**3.3.1 Meta-Learned Perception Module**

**Base Architecture**: SpatialVLM (NeurIPS 2024) adapted for outdoor semantic segmentation.

**Meta-Learning Algorithm**: Model-Agnostic Meta-Learning (MAML) with Controlled Deployment Gaps (CoDeGa).

**Training Protocol**:

**Outer Loop** (Meta-Training across weather conditions):

For each meta-iteration $t = 1, \ldots, T_{\text{meta}}$:

1. Sample batch of weather conditions $\mathcal{W} = \{w_1, \ldots, w_K\}$ where $K=5$ tasks per batch
2. For each condition $w_i \in \mathcal{W}$:
   
   **Inner Loop** (Fast Adaptation):
   
   a. Sample support set $\mathcal{D}^{\text{sup}}_{w_i} = \{(x_j, y_j)\}_{j=1}^{N_{\text{sup}}}$ where $N_{\text{sup}}=50$ images
   
   b. Compute adapted parameters via gradient descent:
   $$\theta'_i = \theta - \alpha \nabla_\theta \mathcal{L}_{\text{seg}}(\theta; \mathcal{D}^{\text{sup}}_{w_i})$$
   where $\alpha=0.01$ is inner learning rate, $\mathcal{L}_{\text{seg}}$ is cross-entropy loss for semantic segmentation.
   
   c. Sample query set $\mathcal{D}^{\text{query}}_{w_i} = \{(x_k, y_k)\}_{k=1}^{N_{\text{query}}}$ where $N_{\text{query}}=100$ images
   
   d. Evaluate adapted model on query set:
   $$\mathcal{L}_i = \mathcal{L}_{\text{seg}}(\theta'_i; \mathcal{D}^{\text{query}}_{w_i})$$

3. **Meta-Update** (Outer Loop):
   $$\theta \leftarrow \theta - \beta \nabla_\theta \sum_{i=1}^K \mathcal{L}_i$$
   where $\beta=0.001$ is meta-learning rate.

**Controlled Deployment Gaps** (CoDeGa Integration):

- Define deployment gap $\Delta(w_{\text{train}}, w_{\text{test}})$ as distribution distance between training and test weather conditions (measured via Maximum Mean Discrepancy on feature representations).
- During meta-training, systematically vary $\Delta$ from small (clear → overcast) to large (clear → heavy fog + night) to force learning of robust adaptation strategies.

**Multi-Teacher Knowledge Distillation**:

1. Train 5 specialist teacher models $\{T_1, \ldots, T_5\}$, each on a single weather condition (clear, fog, rain, dusk, night).
2. Distill knowledge into meta-learned student model $S$ via:
   $$\mathcal{L}_{\text{distill}} = \sum_{i=1}^5 \lambda_i \text{KL}(S(x) \| T_i(x))$$
   where $\lambda_i$ are weather-specific weights (higher for rare conditions like heavy fog).

**Training Hyperparameters**:
- Meta-iterations: $T_{\text{meta}} = 10,000$
- Batch size: $K=5$ weather conditions per batch
- Inner loop steps: 5 gradient steps
- Optimizer: Adam with $\beta_1=0.9, \beta_2=0.999$
- Hardware: 4× NVIDIA A100 GPUs, 2-3 weeks training time

**3.3.2 Spatial Prompting for LLM Reasoning**

**LLM Model**: Gemini 1.5 Pro (primary) or GPT-4o (secondary comparison).

**Prompting Strategy**: Combination of SpatialPrompt (reference objects) and SpatialPrompting (keyframes).

**Prompt Template**:

```
You are navigating in an outdoor urban environment. 

REFERENCE OBJECTS (use these for spatial reasoning):
- Fountain at GPS (37.7749, -122.4194)
- Library at GPS (37.7750, -122.4180)
- Pharmacy at GPS (37.7745, -122.4200)

CURRENT KEYFRAME (most informative observation):
[Image: RGB-D frame at timestamp t=15s]
Camera pose: (37.7748, -122.4190), heading 45° NE

TASK: Navigate to the pharmacy.

SPATIAL REASONING QUERY: 
Is the pharmacy north or south of your current position?
How far is the pharmacy from the fountain?

Provide step-by-step reasoning using reference objects, then output navigation action.
```

**Keyframe Selection Algorithm**:

1. Compute information gain for each frame $f_t$ at time $t$:
   $$I(f_t) = H(\text{scene}) - H(\text{scene} | f_t)$$
   where $H$ is entropy of semantic scene representation.

2. Select top-$k$ keyframes with highest $I(f_t)$ (typically $k=3-5$ per navigation task).

3. Update keyframes dynamically as agent moves (sliding window of last 10 frames).

**Zero-Shot Reasoning Protocol**:

- **No fine-tuning**: LLM parameters remain frozen, only prompt engineering.
- **In-context learning**: Provide 2-3 example navigation scenarios in prompt (few-shot prompting).
- **Chain-of-thought**: Instruct LLM to output reasoning steps before final action.

**3.3.3 GAN-Based Progressive Domain Bridging**

**CycleGAN Architecture**:

Generator $G: X_{\text{sim}} \to X_{\text{real}}$ and inverse $F: X_{\text{real}} \to X_{\text{sim}}$

Discriminators $D_{\text{real}}, D_{\text{sim}}$

**Loss Function**:
$$\mathcal{L}_{\text{GAN}} = \mathcal{L}_{\text{adv}}(G, D_{\text{real}}) + \mathcal{L}_{\text{adv}}(F, D_{\text{sim}}) + \lambda_{\text{cyc}} \mathcal{L}_{\text{cycle}}(G, F) + \lambda_{\text{sem}} \mathcal{L}_{\text{semantic}}$$

where:
- $\mathcal{L}_{\text{adv}}$ is adversarial loss (LSGAN)
- $\mathcal{L}_{\text{cycle}} = \mathbb{E}[\|F(G(x)) - x\|_1 + \|G(F(y)) - y\|_1]$ is cycle consistency
- $\mathcal{L}_{\text{semantic}} = \mathbb{E}[\text{mIoU}(\text{seg}(x), \text{seg}(G(x)))]$ enforces semantic preservation
- $\lambda_{\text{cyc}}=10, \lambda_{\text{sem}}=5$

**Progressive Training**:

1. Train GAN₁ on simulation + light real-world augmentation (texture variation)
2. Train GAN₂ on GAN₁ output + medium augmentation (atmospheric effects)
3. Train GAN₃ on GAN₂ output + heavy augmentation (sensor noise, dynamic elements)
4. Train GAN₄ on GAN₃ output + full real-world data

Each GAN trained for 50 epochs, total training time ~1 week on 2× A100 GPUs.

**3.3.4 Source-Free Domain Adaptation (SFDA)**

**Deployment Protocol** (no access to simulation data):

1. **Temporal Clustering**: Group real-world observations by weather condition using atmospheric features (brightness, contrast, fog density estimated from RGB histograms).

2. **Pseudo-Labeling**: Use meta-learned model to generate pseudo-labels for unlabeled real-world data:
   $$\hat{y} = \arg\max_c P(c | x; \theta_{\text{meta}})$$
   Filter predictions with confidence threshold $\tau=0.9$.

3. **Weak Supervision**: Incorporate 10-50 human-labeled samples per condition via:
   $$\mathcal{L}_{\text{SFDA}} = \mathcal{L}_{\text{pseudo}}(\theta; \mathcal{D}_{\text{unlabeled}}) + \lambda_{\text{weak}} \mathcal{L}_{\text{seg}}(\theta; \mathcal{D}_{\text{labeled}})$$
   where $\lambda_{\text{weak}}=2.0$ to prioritize human labels.

4. **Online Refinement**: Update model parameters during deployment using exponential moving average:
   $$\theta_{\text{deploy}} \leftarrow 0.99 \theta_{\text{deploy}} + 0.01 \theta_{\text{updated}}$$

### 3.4 Experimental Design

**3.4.1 Experiment 1: Perception Meta-Learning Validation (Sub-Hypothesis 1)**

**Objective**: Validate that meta-training across 5-10 weather conditions improves real-world perception accuracy by ≥15pp over single-condition baseline.

**Conditions**:
- **Meta-Trained**: MAML with 5, 7, 10 weather conditions
- **Baseline**: SpatialVLM trained only on clear-day simulation
- **Ablations**: (A) No multi-teacher, (B) No CoDeGa controlled gaps, (C) No GAN intermediates

**Test Set**: 500 real-world images (100 per weather condition: clear, overcast, fog, rain, dusk)

**Metrics**:
- **Primary**: Mean Intersection-over-Union (mIoU) averaged across all classes and conditions
  $$\text{mIoU} = \frac{1}{C \cdot W} \sum_{c=1}^C \sum_{w=1}^W \frac{TP_{c,w}}{TP_{c,w} + FP_{c,w} + FN_{c,w}}$$
  where $C=20$ classes, $W=5$ weather conditions.
- **Secondary**: Per-condition mIoU, per-class IoU (especially rare classes like traffic signs in fog)

**Statistical Test**: Paired t-test comparing meta-trained vs. baseline on same test set, Bonferroni correction for multiple conditions ($\alpha' = 0.01$).

**Success Criterion**: Meta-trained (5-10 conditions) achieves ≥70% mIoU, ≥15pp higher than baseline (~55%).

**3.4.2 Experiment 2: Spatial Prompting Transfer (Sub-Hypothesis 2)**

**Objective**: Validate that spatial prompting enables LLM to maintain ≥90% of simulation spatial reasoning accuracy in real-world.

**Conditions**:
- **Prompted**: (A) Reference objects only, (B) Keyframes only, (C) Both
- **Baseline**: Standard text prompts without spatial techniques

**Test Set**: 200 real-world spatial reasoning queries from navigation tasks

**Metrics**:
- **Primary**: Accuracy (% correct answers)
- **Secondary**: Reasoning quality score (1-5 scale, human evaluation of reasoning steps)

**Procedure**:
1. Establish simulation baseline: Test all prompting strategies on 500 simulation queries
2. Deploy to real-world: Same prompting strategies on 200 real-world queries
3. Compare real-world accuracy to simulation baseline (target: ≥90% maintenance)

**Statistical Test**: Proportion test for accuracy, Wilcoxon signed-rank test for reasoning quality.

**Success Criterion**: Prompted LLM (both reference objects + keyframes) achieves ≥76.5% real-world accuracy (if sim=85%), baseline ≤63.75%.

**3.4.3 Experiment 3: End-to-End System Validation (Sub-Hypothesis 3)**

**Objective**: Validate that complete hierarchical system achieves ≥70% navigation success with ≤10pp reality gap.

**System Configurations**:
1. **Complete**: Meta-perception + spatial prompting + GAN intermediates + SFDA
2. **Direct Transfer**: Standard SpatialVLM + standard LLM prompts, no meta-learning
3. **Ablation A**: Complete without meta-learning (standard training)
4. **Ablation B**: Complete without spatial prompting (standard prompts)
5. **Ablation C**: Complete without GAN intermediates (direct sim-to-real)
6. **Ablation D**: Complete without SFDA (no online adaptation)

**Test Set**: 100 real-world navigation tasks (20 per weather condition)

**Task Protocol**:
- **Start**: Random location in 2km² test area
- **Goal**: Navigate to specified landmark (e.g., "Go to the fountain")
- **Success**: Reach within 2m of goal within 30 min
- **Failure**: Collision, timeout, or >10m off-course for >2 min

**Metrics**:
- **Primary**: Success rate (% of 100 tasks completed)
- **Secondary**: 
  - Path efficiency: Actual path length / optimal path length
  - Time efficiency: Actual time / optimal time
  - LLM query count (computational cost)
  - Reality gap: $|\text{Success}_{\text{sim}} - \text{Success}_{\text{real}}|$

**Statistical Test**: Proportion test for success rate (Complete ≥0.70 vs. Direct Transfer ≤0.50, $p<0.05$), ANOVA for ablation comparisons.

**Success Criterion**: Complete system ≥70% success, Direct Transfer ≤50%, reality gap ≤10pp, each ablation shows ≥5pp contribution.

**3.4.4 Experiment 4: Sample Efficiency Analysis**

**Objective**: Validate that GAN intermediate domains reduce adaptation sample requirement by ≥30%.

**Conditions**:
- **With GAN**: 3-5 progressive intermediate domains
- **Without GAN**: Direct sim-to-real adaptation

**Procedure**:
1. Vary real-world labeled sample count: 10, 20, 30, 40, 50, 60, 70 samples per condition
2. For each sample count, measure perception mIoU after adaptation
3. Determine sample count needed to reach 90% of fully-supervised performance (target performance)

**Metrics**:
- **Primary**: Sample efficiency (samples needed to reach target)
- **Secondary**: Learning curve (performance vs. sample count)

**Statistical Test**: Wilcoxon rank-sum test comparing sample counts between GAN vs. no-GAN conditions.

**Success Criterion**: GAN intermediates require ≤50 samples (vs. ~70 for direct), representing ≥30% reduction.

### 3.5 Evaluation Metrics

**Perception Metrics**:
- **mIoU** (Mean Intersection-over-Union): Standard semantic segmentation metric
- **Per-class IoU**: Especially for safety-critical classes (pedestrians, vehicles)
- **Rare condition performance**: mIoU on heavy fog, night rain (challenging conditions)

**Reasoning Metrics**:
- **Spatial reasoning accuracy**: % correct answers on spatial queries
- **Reasoning quality**: Human evaluation (1-5 scale) of reasoning coherence
- **Sim-to-real transfer ratio**: Real-world accuracy / Simulation accuracy

**Navigation Metrics**:
- **Success rate**: % of tasks completed successfully
- **Path efficiency**: Actual path length / Optimal path length
- **Time efficiency**: Actual time / Optimal time
- **Safety**: Collision count, near-miss count

**System-Level Metrics**:
- **Reality gap**: $|\text{Performance}_{\text{sim}} - \text{Performance}_{\text{real}}|$ (percentage points)
- **Sample efficiency**: Labeled samples needed to reach 90% target performance
- **Computational cost**: LLM API calls per task, GPU-hours for training
- **Robustness**: Performance variance across weather conditions (lower is better)

**Benchmark Comparison**:
- Compare against CityEQA (60.7% sim baseline)
- Compare against Open-Nav (zero-shot outdoor navigation, ~50-60% reported)
- Compare against direct sim-to-real transfer (≤50% expected)

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome 1: Weather-Robust Perception**

We expect meta-learned perception modules to achieve **72-75% mIoU** on real-world outdoor semantic segmentation across 5 weather conditions (clear, overcast, fog, rain, dusk), representing a **17-20 percentage point improvement** over direct transfer baselines (~55%). The multi-teacher distillation component should provide an additional **12-15pp boost** on rare conditions (heavy fog, night rain) compared to single-teacher approaches.

**Quantitative Prediction**:
- Clear day: 78-80% mIoU (easiest condition)
- Overcast/light rain: 72-75% mIoU (moderate challenge)
- Heavy fog/dusk: 68-72% mIoU (difficult conditions)
- Night rain: 65-68% mIoU (most challenging, benefits most from multi-teacher)

**Primary Outcome 2: Zero-Shot LLM Reasoning Transfer**

Spatial prompting (reference objects + keyframes) is expected to enable LLMs to maintain **90-95% of simulation spatial reasoning accuracy** in real-world embodied navigation. If simulation accuracy is 85%, real-world accuracy should reach **76.5-80.8%**, compared to **≤63.75%** for non-prompted baselines.

**Quantitative Prediction**:
- Reference objects only: 85-88% of simulation performance
- Keyframes only: 82-85% of simulation performance
- Both combined: 90-95% of simulation performance (synergistic effect)

**Primary Outcome 3: End-to-End Navigation Success**

The complete hierarchical system is expected to achieve **70-75% success rate** on 100 real-world navigation tasks, with a **reality gap of 8-10 percentage points** (simulation performance 78-85%). This surpasses:
- Direct sim-to-real transfer: 45-50% success (≥20pp improvement)
- CityEQA simulation baseline: 60.7% (≥9.3pp improvement + real-world validation)
- Open-Nav zero-shot: 50-60% (≥10pp improvement with adaptation)

**Ablation Predictions**:
- Without meta-learning: 60-65% success (10-15pp drop)
- Without spatial prompting: 62-67% success (8-13pp drop)
- Without GAN intermediates: 65-68% success (5-7pp drop)
- Without SFDA: 66-70% success (4-5pp drop)

**Primary Outcome 4: Sample Efficiency**

GAN-based progressive domain bridging is expected to reduce real-world adaptation sample requirements to **40-50 samples per weather condition** (200-250 total for 5 conditions), representing a **30-40% reduction** from direct adaptation (~70 samples per condition, 350 total). This translates to:
- Data collection time: 2-3 weeks (vs. 4-5 weeks for direct approach)
- Annotation cost: $1,500-2,000 (vs. $3,000-3,500 for direct approach at $10/image)
- Deployment feasibility: Accessible to academic research teams

### 4.2 Scientific Impact

**Theoretical Contributions**:

1. **Hierarchical Adaptation Framework**: This research will formalize the principle that perception and reasoning require asymmetric adaptation strategies for outdoor embodied LLM agents. The framework will provide theoretical analysis of when meta-learning (perception) vs. prompting (reasoning) is optimal, extending domain adaptation theory to multi-modal hierarchical systems.

2. **Outdoor Reality Gap Decomposition**: The systematic quantification of sim-to-real gaps into weather-induced (expected: 8-12pp), lighting-induced (5-8pp), and dynamic element-induced (3-5pp) components will establish a foundation for targeted gap reduction strategies. This extends existing indoor reality gap theory to outdoor-specific factors.

3. **Meta-Learning for Vision-Language Agents**: Extension of CoDeGa to multi-modal LLM agents with frozen language modules will provide insights into when hierarchical meta-learning outperforms end-to-end approaches, contributing to meta-learning theory for heterogeneous architectures.

**Methodological Contributions**:

1. **Multi-Teacher Weather Specialization**: The novel combination of weather-specialized teacher models with meta-learning (not just distillation) will establish a new paradigm for handling multi-condition robustness in outdoor robotics.

2. **Embodied Spatial Prompting**: Adaptation of SpatialPrompt to continuous sensor streams with temporal consistency (reference object tracking across frames) will bridge the gap between static image benchmarks and embodied navigation.

3. **Progressive GAN Domain Bridging**: Using GAN-generated intermediate domains as meta-training curriculum (rather than single-step transfer) will provide a systematic approach to sim-to-real gap reduction with quantifiable intermediate milestones.

4. **Standardized Outdoor Benchmark**: The MetaUrban→Real evaluation protocol with standardized metrics (success rate, mIoU, reality gap, sample efficiency) will enable reproducible comparison across methods, accelerating field progress.

### 4.3 Practical Impact

**Deployment Feasibility**:

The 5-10× reduction in data requirements (from 350+ to 40-50 samples per condition) makes real-world outdoor embodied AI deployment feasible for:
- Academic research labs with limited data collection resources
- Startups developing delivery robots without large-scale data infrastructure
- Public sector applications (city governments deploying assistive navigation systems)

**Cost Reduction**:

- **Data collection**: $1,500-2,000 (vs. $3,000-3,500 for standard fine-tuning)
- **LLM adaptation**: Near-zero (prompting vs. $10k-100k for fine-tuning)
- **Total deployment cost**: $15k-20k (meta-training + GAN + data + compute), accessible to research budgets

**Modular Architecture Benefits**:

The hierarchical design enables:
- **Parallel development**: Perception researchers improve meta-learning without LLM expertise; LLM researchers refine prompting without perception expertise
- **Rapid iteration**: Swap perception modules (e.g., upgrade to better GAN) without retraining LLM component
- **Incremental deployment**: Deploy perception module first, add LLM reasoning later

**Privacy-Preserving Deployment**:

Source-free domain adaptation enables deployment without sharing simulation data, addressing:
- Intellectual property protection (simulation assets remain proprietary)
- Bandwidth constraints (no need to transfer large simulation datasets to edge devices)
- Commercial deployment scenarios (robotics companies can deploy without exposing training data)

### 4.4 Application Domains

**Immediate Applications** (1-2 years):

1. **Autonomous Delivery Robots**: Weather-robust navigation for last-mile delivery in urban environments (Starship, Amazon Scout, etc.). Expected impact: Reduce weather-related service interruptions by 60-70%.

2. **Urban Surveillance Systems**: Multi-weather perception for security robots patrolling outdoor areas. Expected impact: Maintain ≥70% detection accuracy across all weather conditions (vs. ≤50% for non-adapted systems).

3. **Assistive Navigation**: Outdoor navigation assistance for visually impaired users with weather-aware spatial reasoning. Expected impact: Enable safe navigation in 4-5 weather conditions (vs. clear-day-only for current systems).

**Medium-Term Applications** (3-5 years):

1. **Autonomous Micromobility**: E-scooters, bikes with autonomous navigation capabilities (aligns with MetaUrban focus). Expected impact: Enable autonomous repositioning across weather conditions, reducing operational costs by 30-40%.

2. **Search and Rescue**: Outdoor robots navigating disaster zones with adverse weather/lighting. Expected impact: Extend operational envelope to fog, rain, night conditions (currently limited to clear day).

3. **Agricultural Robots**: Extend MetaCropFollow approach to urban farming, outdoor crop monitoring. Expected impact: Year-round operation across seasons and weather.

**Long-Term Vision** (5-10 years):

Integration with multi-agent systems (Workshop Topic 4) to enable:
- **Coordinated delivery fleets** with weather-aware task allocation
- **Human-robot collaboration** in outdoor construction, maintenance
- **City-scale embodied AI infrastructure** with shared spatial reasoning across agents

### 4.5 Workshop Alignment

This research directly addresses three workshop topics:

**Topic 1: Spatial Intelligence and Embodied Perception**
- Contribution: Meta-learned perception achieving ≥70% mIoU across weather conditions
- Impact: Establishes weather-robust perception as foundation for outdoor embodied AI

**Topic 2: Reasoning and Planning**
- Contribution: Zero-shot LLM spatial reasoning via prompting (≥90% sim-to-real transfer)
- Impact: Demonstrates that LLM reasoning can transfer without fine-tuning through appropriate prompting

**Topic 5: Simulator, Testbeds, Datasets, Benchmark**
- Contribution: MetaUrban→Real standardized benchmark with quantified reality gap metrics
- Impact: Enables reproducible comparison, accelerates field progress through shared evaluation infrastructure

**Future Workshop Contributions**:

The modular architecture provides a foundation for:
- **Topic 3 (Decision-Making)**: Integrate small ML models for low-level control while maintaining LLM high-level planning
- **Topic 4 (Multi-Agent)**: Extend to multi-agent coordination with shared spatial reasoning (each agent uses same meta-learned perception + spatial prompting)

### 4.6 Limitations and Future Work

**Known Limitations**:

1. **Geographic Generalization**: Real-world validation limited to single city (2km² area). Future work: Multi-city validation (Tokyo, NYC, Dubai) to assess layout generalization.

2. **Dynamic Elements**: Current approach treats moving pedestrians/vehicles as part of "outdoor environment" robustness, not explicitly modeled. Future work: Integrate predictive models for dynamic obstacle avoidance.

3. **Sensor Limitations**: Requires RGB-D + GPS + IMU; performance may degrade with RGB-only or in GPS-denied urban canyons. Future work: Visual localization fallback (SLAM-based).

4. **Task Complexity Ceiling**: Validated on moderate-complexity tasks (1-5 waypoints, 10-30 min duration). Future work: Extend to multi-day logistics, complex multi-step tasks.

**Future Research Directions**:

1. **Multi-Agent Extension**: Extend hierarchical domain bridging to multi-agent systems with shared perception modules and coordinated spatial reasoning.

2. **Continual Learning**: Integrate continual learning to adapt to new weather conditions (e.g., snow, sandstorms) without catastrophic forgetting.

3. **Human-Agent Collaboration**: Incorporate human feedback during deployment to refine spatial reasoning and perception adaptation.

4. **Safety-Critical Applications**: Extend to autonomous vehicles with formal verification of perception robustness and reasoning correctness.

### 4.7 Success Metrics Summary

**Minimum Viable Success** (Hypothesis Supported):
- Perception: ≥70% mIoU, ≥15pp over baseline
- Reasoning: ≥90% sim-to-real transfer
- Navigation: ≥70% success rate, ≤10pp reality gap
- Sample efficiency: ≤50 samples per condition

**Strong Success** (Exceeds Expectations):
- Perception: ≥75% mIoU, ≥20pp over baseline
- Reasoning: ≥95% sim-to-real transfer
- Navigation: ≥75% success rate, ≤8pp reality gap
- Sample efficiency: ≤40 samples per condition

**Transformative Success** (Field-Changing):
- Perception: ≥80% mIoU (approaching indoor-level performance)
- Reasoning: ≥98% sim-to-real transfer (near-perfect prompting)
- Navigation: ≥80% success rate, ≤5pp reality gap
- Sample efficiency: ≤30 samples per condition (10× reduction)
- Benchmark adoption: ≥10 research groups using MetaUrban→Real protocol within 2 years

**Conclusion**:

This research proposes a comprehensive solution to outdoor embodied intelligence for LLM agents through hierarchical domain bridging. By recognizing that perception and reasoning require fundamentally different adaptation strategies, we achieve sample-efficient, weather-robust outdoor navigation that surpasses existing approaches. The expected outcomes—≥70% navigation success with ≤10pp reality gap using only 10-50 adaptation samples—will make outdoor embodied AI deployment feasible for research teams and practical applications. The standardized benchmark and modular architecture will accelerate field progress, while the theoretical framework will guide future research on multi-modal hierarchical agents. Success in this research will establish a new paradigm for outdoor embodied intelligence, bridging the gap between indoor-focused embodied AI and real-world urban deployment.