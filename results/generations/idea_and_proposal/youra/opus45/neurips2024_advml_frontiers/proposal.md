# Research Proposal: ModularShield: A Hierarchical Plug-and-Play Defense Framework Against Multimodal Jailbreak Attacks

## 1. Introduction

### 1.1 Background

Large Multimodal Models (LMMs) such as LLaVA, GPT-4V, and Gemini Pro have demonstrated remarkable capabilities in understanding and generating content across visual and textual modalities. However, this expanded capability surface has introduced novel security vulnerabilities that adversaries actively exploit. Jailbreak attacks—carefully crafted inputs designed to bypass safety mechanisms and elicit harmful outputs—have evolved from simple text-based prompts to sophisticated multimodal strategies that leverage cross-modal interactions.

Recent research has documented alarming vulnerabilities in LMMs. Visual perturbation attacks embed adversarial patterns in images that, when processed alongside benign text queries, cause models to generate harmful content. Cross-modal obfuscation attacks exploit the semantic gap between visual and textual processing pipelines, encoding malicious intent in one modality while using the other as a distraction. The JailBreakV-28K benchmark catalogues over 28,000 such attack instances across multiple categories, revealing that state-of-the-art LMMs remain vulnerable to diverse attack strategies with attack success rates (ASR) often exceeding 60%.

Existing defense mechanisms have emerged to address these threats, each targeting specific vulnerability types. UniGuard implements joint unimodal and cross-modal guardrails for pre-generation filtering. SafeMLLM employs contrastive embedding analysis to detect perturbation-level attacks. E²AT (Efficient and Effective Adversarial Training) modifies model behavior through joint multimodal optimization, achieving 34% defense improvement on specific attack categories. Q-MLLM introduces query-based detection mechanisms for identifying suspicious input patterns.

Despite these advances, a critical gap persists: no unified framework integrates these complementary defense mechanisms across abstraction levels. Each existing defense excels against specific attack types but fails against diverse, adaptive threats. When adversaries combine visual perturbations with textual jailbreaks and cross-modal obfuscation, single-layer defenses prove insufficient. This fragmentation leaves LMMs vulnerable to sophisticated multi-vector attacks that exploit the gaps between modality-specific protections.

### 1.2 Research Objectives

This research proposes ModularShield, a 4-layer hierarchical defense framework with modular plug-and-play architecture designed to provide comprehensive protection against multimodal jailbreak attacks. Our primary objectives are:

1. **Design and implement** a hierarchical defense architecture that integrates complementary defense mechanisms at appropriate abstraction levels, enabling inter-layer information flow that catches attacks bypassing individual layers.

2. **Develop** an adversarially-robust cross-modal consistency verification module using fine-tuned CLIP embeddings to detect visual-textual semantic divergence characteristic of cross-modal attacks.

3. **Evaluate** ModularShield's effectiveness against diverse attack categories (visual, textual, cross-modal, adaptive) using the JailBreakV-28K benchmark, demonstrating significant ASR reduction compared to single-layer baselines.

4. **Validate** the practical deployability of ModularShield by ensuring acceptable latency overhead and minimal utility degradation on clean inputs.

### 1.3 Significance

This research addresses a pressing need in LMM safety as these models become increasingly deployed in high-stakes applications including healthcare, education, and content moderation. The modular architecture provides three key contributions:

First, **comprehensive coverage**: by operating at multiple abstraction levels (input patterns, embedding space, cross-modal semantics, output content), ModularShield provides defense-in-depth that no single-layer approach can achieve.

Second, **practical extensibility**: the plug-and-play design enables integration of future defense innovations without architectural redesign, ensuring long-term relevance as attack strategies evolve.

Third, **theoretical advancement**: our work provides empirical evidence for the hypothesis that layered defense with inter-layer information flow provides synergistic protection benefits beyond additive combination of individual defenses.

## 2. Methodology

### 2.1 Framework Architecture

ModularShield implements a 4-layer hierarchical defense architecture where each layer operates at a distinct abstraction level and passes information to subsequent layers. Let $x = (x_v, x_t)$ denote a multimodal input comprising visual component $x_v$ and textual component $x_t$, and let $\mathcal{M}$ denote the target LMM.

**Layer 1: Input Sanitization ($\mathcal{L}_1$)**

The first layer implements pattern-based filtering to block obvious jailbreak attempts. We define a set of detection functions $\{f_1^{(i)}\}_{i=1}^{k_1}$ that identify known attack signatures:

$$\mathcal{L}_1(x) = \begin{cases} \text{BLOCK} & \text{if } \exists i: f_1^{(i)}(x) > \tau_1^{(i)} \\ (\text{PASS}, s_1) & \text{otherwise} \end{cases}$$

where $s_1 = \max_i f_1^{(i)}(x)$ represents the maximum suspicion score passed to Layer 2. Detection functions include: (a) keyword pattern matching for known jailbreak phrases, (b) image forensics for detecting adversarial perturbation artifacts, and (c) structural analysis for identifying prompt injection patterns.

**Layer 2: Embedding Anomaly Detection ($\mathcal{L}_2$)**

The second layer analyzes embedding-space representations to detect perturbation-level attacks. We employ a contrastive anomaly detector trained on clean and adversarial embedding distributions:

$$\mathcal{L}_2(x, s_1) = \begin{cases} \text{BLOCK} & \text{if } d_{\text{anomaly}}(E(x)) > \tau_2 - \alpha \cdot s_1 \\ (\text{PASS}, s_2) & \text{otherwise} \end{cases}$$

where $E(x) = [E_v(x_v); E_t(x_t)]$ concatenates visual and textual embeddings, $d_{\text{anomaly}}$ measures distance to the learned clean distribution manifold, and $\alpha$ is a coupling coefficient that lowers the threshold based on Layer 1 suspicion. The anomaly score is computed as:

$$d_{\text{anomaly}}(E(x)) = \min_{c \in \mathcal{C}} \|E(x) - \mu_c\|_{\Sigma_c^{-1}}$$

where $\mathcal{C}$ represents cluster centers of clean embeddings with means $\mu_c$ and covariance matrices $\Sigma_c$.

**Layer 3: Cross-Modal Consistency Verification ($\mathcal{L}_3$)**

The third layer employs an adversarially-robust CLIP model to detect semantic divergence between visual and textual content. We fine-tune CLIP using adversarial training to improve robustness:

$$\mathcal{L}_{\text{CLIP-AT}} = \mathbb{E}_{(x_v, x_t) \sim \mathcal{D}} \left[ \max_{\|\delta\| \leq \epsilon} \ell_{\text{contrastive}}(x_v + \delta, x_t) \right]$$

The consistency score is computed as:

$$c(x) = \frac{\text{CLIP}_v(x_v) \cdot \text{CLIP}_t(x_t)}{\|\text{CLIP}_v(x_v)\| \cdot \|\text{CLIP}_t(x_t)\|}$$

Layer 3 decision incorporates information from previous layers:

$$\mathcal{L}_3(x, s_1, s_2) = \begin{cases} \text{BLOCK} & \text{if } c(x) < \tau_3 + \beta \cdot (s_1 + s_2) \\ (\text{PASS}, s_3) & \text{otherwise} \end{cases}$$

where $s_3 = 1 - c(x)$ and $\beta$ adjusts sensitivity based on accumulated suspicion.

**Layer 4: Response Verification ($\mathcal{L}_4$)**

The final layer analyzes the LMM's generated response $y = \mathcal{M}(x)$ for harmful content:

$$\mathcal{L}_4(y, s_1, s_2, s_3) = \begin{cases} \text{BLOCK} & \text{if } h(y) > \tau_4 - \gamma \cdot (s_1 + s_2 + s_3) \\ \text{ALLOW} & \text{otherwise} \end{cases}$$

where $h(y)$ is a harmfulness classifier score and $\gamma$ controls the influence of accumulated suspicion on the final threshold.

**Inter-Layer Information Flow**

The key innovation is the propagation of suspicion scores across layers, enabling earlier layers to sensitize later layers to potentially adversarial inputs. The complete framework decision is:

$$\text{ModularShield}(x) = \mathcal{L}_4(\mathcal{M}(x), \mathcal{L}_3(\mathcal{L}_2(\mathcal{L}_1(x))))$$

with early termination when any layer returns BLOCK.

### 2.2 Data Collection and Preparation

**Attack Dataset:** We utilize JailBreakV-28K, a comprehensive benchmark containing 28,000+ jailbreak attack instances categorized into:
- Visual perturbation attacks (n ≈ 7,000)
- Textual jailbreak attacks (n ≈ 7,000)
- Cross-modal obfuscation attacks (n ≈ 7,000)
- Adaptive/combined attacks (n ≈ 7,000)

We employ standardized train/validation/test splits (60%/20%/20%) to ensure reproducibility.

**Clean Evaluation Data:** Model utility is assessed using:
- VQAv2 validation set (214,354 questions)
- MMBench test set (2,974 questions)

**Adversarial CLIP Training Data:** We construct a training set of 50,000 image-text pairs with corresponding adversarial perturbations generated using PGD attacks with $\epsilon = 8/255$ and 20 iterations.

### 2.3 Experimental Design

**Independent Variables:**
1. Defense Architecture: {No Defense, UniGuard-only, SafeMLLM-only, E²AT-only, Q-MLLM-only, ModularShield}
2. Attack Type: {Visual, Textual, Cross-modal, Adaptive}

**Dependent Variables:**
1. Attack Success Rate (ASR): Percentage of attacks eliciting harmful responses
2. Model Utility: VQA accuracy on clean inputs
3. Inference Latency: Average response time per query

**Controlled Variables:**
- Base LMM: LLaVA-1.5-7B with frozen weights
- Hardware: NVIDIA A100 80GB GPUs
- Random seeds: 5 seeds per condition

**Experimental Conditions:**

| Condition | Description |
|-----------|-------------|
| C0 | Undefended LLaVA-1.5-7B baseline |
| C1 | UniGuard-only defense |
| C2 | SafeMLLM-only defense |
| C3 | E²AT-only defense |
| C4 | Q-MLLM-only defense |
| C5 | ModularShield (full 4-layer) |

**Ablation Studies:**
- ModularShield-L1: Layers 2-4 only (no input sanitization)
- ModularShield-L2: Layers 1,3,4 only (no embedding anomaly)
- ModularShield-L3: Layers 1,2,4 only (no cross-modal consistency)
- ModularShield-L4: Layers 1-3 only (no response verification)

### 2.4 Evaluation Metrics

**Primary Metric - Attack Success Rate (ASR):**
$$\text{ASR} = \frac{\text{Number of successful attacks}}{\text{Total attack attempts}} \times 100\%$$

Success is determined using the JailbreakBench standardized judge, a fine-tuned classifier achieving 95%+ agreement with human annotators.

**Secondary Metrics:**

*Model Utility:*
$$\text{Utility} = \frac{1}{|\mathcal{D}_{\text{clean}}|} \sum_{(x,y) \in \mathcal{D}_{\text{clean}}} \mathbb{1}[\mathcal{M}(x) = y]$$

*Latency Overhead:*
$$\text{Overhead} = \frac{T_{\text{ModularShield}}}{T_{\text{baseline}}}$$

*Defense Efficiency:*
$$\text{Efficiency} = \frac{\text{ASR}_{\text{baseline}} - \text{ASR}_{\text{defended}}}{\text{Latency Overhead}}$$

### 2.5 Statistical Analysis

We employ mixed-design ANOVA with Defense Architecture as between-subjects factor and Attack Type as within-subjects factor. Post-hoc comparisons use Tukey's HSD with family-wise error rate $\alpha = 0.05$. Effect sizes are reported using Cohen's d with interpretation: small (0.2), medium (0.5), large (0.8).

**Sample Size Justification:** Power analysis (G*Power) indicates n = 30 samples per condition achieves 95% power to detect medium effects (d = 0.5) at $\alpha = 0.05$. With 6 conditions × 4 attack types × 30 samples = 720 minimum experiments.

**Success Criteria:**
1. ModularShield ASR ≤ (Best baseline ASR - 20%), p < 0.05
2. Latency overhead < 2×
3. Utility degradation < 10%

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome:** We hypothesize ModularShield will achieve ASR reduction of at least 20% absolute compared to the best single-layer baseline across all attack categories. Based on preliminary analysis of component defense effectiveness:

| Attack Type | Expected Baseline ASR | Expected ModularShield ASR |
|-------------|----------------------|---------------------------|
| Visual | 45% | 20% |
| Textual | 50% | 25% |
| Cross-modal | 65% | 35% |
| Adaptive | 70% | 45% |

**Ablation Predictions:** Each layer removal should increase ASR by 5-15%, demonstrating independent contribution. Layer 3 (cross-modal consistency) is expected to show largest impact on cross-modal attacks, while Layer 1 (input sanitization) provides greatest efficiency gains through early rejection.

**Efficiency Analysis:** Early rejection at Layers 1-2 should process 40-60% of obvious attacks without invoking computationally expensive Layers 3-4, maintaining average latency overhead below 2×.

### 3.2 Scientific Impact

This research advances adversarial machine learning theory by providing empirical evidence for the **defense complementarity hypothesis**: that defense mechanisms operating at different abstraction levels provide synergistic rather than merely additive protection. The inter-layer information flow mechanism demonstrates how suspicion propagation enables adaptive threshold adjustment, a novel contribution to defense architecture design.

The modular framework establishes a **standardized integration paradigm** for LMM defenses, enabling systematic comparison of defense components and facilitating future research on optimal defense composition.

### 3.3 Practical Impact

ModularShield addresses immediate industry needs for deployable LMM safety solutions. The plug-and-play architecture enables:

1. **Incremental deployment:** Organizations can adopt individual layers based on threat models and computational budgets
2. **Continuous improvement:** New defense modules can be integrated without system redesign
3. **Customization:** Threshold parameters enable tuning for specific application requirements (high-security vs. high-throughput)

### 3.4 Broader Implications

By advancing practical LMM safety, this research contributes to responsible AI deployment in sensitive domains. The framework's transparency—with interpretable per-layer decisions—supports accountability requirements in regulated industries. Furthermore, the modular design philosophy may inform defense architectures for emerging multimodal systems incorporating audio, video, and other modalities.

### 3.5 Limitations and Future Work

We acknowledge several limitations: (1) evaluation is limited to LLaVA-1.5-7B; generalization to larger models requires validation; (2) adversarial CLIP training requires computational resources that may limit accessibility; (3) adaptive attackers with knowledge of ModularShield architecture may develop targeted evasion strategies.

Future work will explore: (1) extension to audio-visual-language models; (2) automated threshold optimization using reinforcement learning; (3) theoretical analysis of defense composition optimality; and (4) real-world deployment studies measuring long-term effectiveness against evolving threats.