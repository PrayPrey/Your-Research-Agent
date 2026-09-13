# Research Proposal: Interactive Error Correction for UI Generation through Natural Language Dialogue

## 1. Introduction

### Background

The convergence of Artificial Intelligence (AI) and Human-Computer Interaction (HCI) has catalyzed transformative advances in how humans create and interact with digital interfaces. Recent breakthroughs in generative AI, particularly large language models (LLMs) and vision-language models (VLMs), have enabled automated user interface (UI) generation from natural language descriptions. However, despite these impressive capabilities, a fundamental gap persists between what users envision and what AI systems produce. Current UI generation systems operate primarily in a one-shot paradigm: users provide an initial prompt, receive a generated output, and must either accept the result or start anew with a reformulated request.

This limitation reflects a broader challenge in human-AI collaboration. Unlike working with a human designer who iteratively refines designs based on conversational feedback, interacting with AI generation systems resembles communicating through a narrow channel where nuanced corrections are lost. Research in semantic parsing (Elgohary et al., 2021) and dialogue systems (Gupta et al., 2022) has demonstrated that natural language feedback can effectively guide model corrections in structured domains. Similarly, work on vision-and-language navigation (Taioli et al., 2024) has shown the value of interactive error detection and localization. Yet these advances have not been systematically applied to the creative domain of UI generation, where the design space is vast and user preferences are highly subjective.

The semantic gap between user intent and AI interpretation, as highlighted in studies of generative creative tools (Román et al., 2024), compounds this challenge. Users often struggle to articulate precise requirements upfront but can readily identify deficiencies when presented with concrete outputs. This observation suggests that post-generation correction through dialogue represents a more natural and effective interaction paradigm than attempting to perfect initial prompts.

### Research Objectives

This research proposes the development of **Dialogue-Guided UI Refinement (DGUR)**, a comprehensive framework enabling iterative, conversational correction of AI-generated user interfaces. Our specific objectives are:

1. To design and implement a grounded correction parser that accurately maps natural language critiques to specific, actionable UI element modifications.

2. To develop a hierarchical edit memory system that maintains correction history, prevents design regressions, and learns persistent user preferences.

3. To create an uncertainty-aware generation module that identifies ambiguous user instructions and proactively seeks clarification.

4. To construct a benchmark dataset of UI correction dialogues and establish evaluation protocols for dialogue-based design refinement.

5. To empirically validate the framework's effectiveness through comprehensive user studies measuring correction success rates, dialogue efficiency, and user satisfaction.

### Significance

This research addresses critical gaps at the intersection of AI and HCI. By enabling intuitive, dialogue-based error correction, DGUR will make AI-powered design tools accessible to non-technical users while respecting the expertise of professional designers. The framework directly advances personalizable and correctable machine learning models—a core topic of interest for the HCI-AI research community. Furthermore, the methodologies developed will generalize beyond UI design to other generative creative tasks, including document layout, graphic design, and 3D modeling. The benchmark dataset and evaluation protocols will provide lasting infrastructure for future research in interactive generative systems.

## 2. Methodology

### 2.1 System Architecture Overview

The DGUR framework comprises three integrated components: (1) a Grounded Correction Parser (GCP), (2) a Hierarchical Edit Memory (HEM), and (3) an Uncertainty-Aware Generation Module (UAGM). These components work in concert within an iterative refinement loop, as illustrated below.

**System Pipeline:**
1. User provides initial UI description → Base generator produces initial UI
2. User observes output and provides natural language correction
3. GCP parses correction into structured edit operations
4. HEM validates edits against history and user preferences
5. UAGM assesses uncertainty; if high, generates clarification request
6. System applies edits and presents updated UI
7. Loop continues until user approves final design

### 2.2 Grounded Correction Parser (GCP)

The GCP transforms natural language corrections into executable UI modifications through a two-stage process: visual grounding and edit operation synthesis.

**Visual Grounding Stage:** Given a UI image $I$ and textual correction $c$, we employ a fine-tuned vision-language model to identify the target elements. We formulate this as a referring expression comprehension task:

$$E_{target} = \text{VLM}_{ground}(I, c) = \{(e_i, b_i, s_i)\}_{i=1}^{k}$$

where $e_i$ represents the element identifier, $b_i \in \mathbb{R}^4$ denotes the bounding box coordinates, and $s_i \in [0,1]$ is the confidence score. We fine-tune a base VLM (e.g., LLaVA or GPT-4V) on a curated dataset of UI screenshots paired with element-referring expressions.

**Edit Operation Synthesis:** We define a formal grammar of UI edit operations:

$$\mathcal{O} = \{\text{MOVE}(e, \Delta x, \Delta y), \text{RESIZE}(e, \Delta w, \Delta h), \text{RESTYLE}(e, attr, val), \text{DELETE}(e), \text{ADD}(type, props)\}$$

The correction text $c$ is parsed into a sequence of operations $\hat{O} = [o_1, o_2, ..., o_n]$ using a fine-tuned language model with constrained decoding:

$$\hat{O} = \arg\max_{O \in \mathcal{O}^*} P_{LM}(O | c, I, \theta)$$

where $\mathcal{O}^*$ represents valid operation sequences according to our grammar, and $\theta$ denotes model parameters. We employ constrained beam search to ensure syntactic validity of generated operations.

### 2.3 Hierarchical Edit Memory (HEM)

The HEM maintains a structured representation of all corrections applied during a design session and across sessions, enabling regression prevention and preference learning.

**Session-Level Memory:** We maintain a directed acyclic graph $G_s = (V, E)$ where vertices represent UI states and edges represent edit operations. Each vertex stores:

$$v_i = (S_i, H_i, T_i)$$

where $S_i$ is the serialized UI state, $H_i$ is a hash for efficient comparison, and $T_i$ is the timestamp. Before applying any edit $o$, we verify:

$$\text{Conflict}(o, G_s) = \bigvee_{(v_j, o_j) \in \text{Path}(v_{current})} \text{Contradicts}(o, o_j)$$

If a conflict is detected, the system alerts the user and requests clarification.

**Cross-Session Preference Learning:** User preferences are modeled as a weighted feature vector $\mathbf{p} \in \mathbb{R}^d$ updated through implicit feedback:

$$\mathbf{p}_{t+1} = \mathbf{p}_t + \alpha \sum_{o \in \mathcal{O}_{accepted}} \phi(o) - \beta \sum_{o \in \mathcal{O}_{rejected}} \phi(o)$$

where $\phi(o)$ extracts features from operation $o$, and $\alpha, \beta$ are learning rates. This enables the system to anticipate user preferences (e.g., preferring rounded buttons, specific color palettes) and propose proactive suggestions.

### 2.4 Uncertainty-Aware Generation Module (UAGM)

The UAGM quantifies uncertainty in parsed corrections and generates targeted clarification requests when ambiguity exceeds acceptable thresholds.

**Uncertainty Quantification:** We employ Monte Carlo dropout during inference to estimate epistemic uncertainty:

$$\text{Var}(\hat{O}) = \frac{1}{T}\sum_{t=1}^{T}\left(\hat{O}^{(t)} - \bar{O}\right)^2$$

where $\hat{O}^{(t)}$ represents the output with dropout mask $t$, and $\bar{O}$ is the mean prediction. Additionally, we compute semantic uncertainty using token-level entropy:

$$H_{semantic} = -\sum_{i}\sum_{v \in V} P(w_i = v) \log P(w_i = v)$$

**Clarification Generation:** When uncertainty exceeds threshold $\tau$, the system generates a clarification request. We frame this as a question generation task conditioned on the ambiguous aspects:

$$q = \text{LM}_{clarify}(c, \{a_j\}_{j=1}^{m}, I)$$

where $\{a_j\}$ represents identified ambiguous aspects (e.g., "Which button should be modified—the 'Submit' button or the 'Cancel' button?"). The system presents disambiguated options when possible, minimizing user cognitive load.

### 2.5 Dataset Construction

We will construct **DGUR-Bench**, a benchmark dataset of UI correction dialogues through a multi-phase process:

**Phase 1 - Seed UI Collection:** We aggregate diverse UI screenshots from existing datasets (Rico, WebUI, Figma public designs), ensuring coverage across mobile, web, and desktop interfaces. Target: 5,000 unique UI designs.

**Phase 2 - Controlled User Studies:** We recruit 100 participants with varying design expertise. Participants are presented with "imperfect" UIs (automatically degraded from high-quality designs) and asked to provide natural language corrections. Sessions are recorded, yielding correction-dialogue pairs. Target: 25,000 dialogue turns.

**Phase 3 - Synthetic Augmentation:** We employ GPT-4 to paraphrase collected corrections, expanding linguistic diversity. Quality control is maintained through human verification of 20% of synthetic samples.

**Dataset Annotation:** Each dialogue turn is annotated with:
- Target element(s) bounding boxes
- Intended edit operation(s) in formal grammar
- Ambiguity labels (binary)
- Correction success (binary, post-application)

### 2.6 Experimental Design

**Baselines:**
1. **Regeneration Baseline:** Complete UI regeneration with modified prompt
2. **Direct Edit Baseline:** Rule-based natural language to edit mapping
3. **Single-Turn VLM:** One-shot correction without dialogue context
4. **Ablated DGUR Variants:** DGUR without HEM, DGUR without UAGM

**Evaluation Metrics:**

*Automatic Metrics:*
- **Edit Accuracy:** Percentage of corrections correctly parsed and applied
$$\text{Acc}_{edit} = \frac{|\{o : o_{pred} = o_{gold}\}|}{|\mathcal{O}_{gold}|}$$

- **Dialogue Efficiency:** Average turns required to achieve target design
- **Regression Rate:** Frequency of edits contradicting previous corrections

*Human Evaluation Metrics:*
- **Task Completion Rate:** Percentage of sessions reaching user-approved final design
- **System Usability Scale (SUS):** Standardized usability assessment
- **NASA-TLX:** Cognitive load measurement
- **User Satisfaction:** 7-point Likert scale ratings

**User Study Protocol:**
We conduct a between-subjects study with N=60 participants (20 per condition: DGUR, Regeneration Baseline, Direct Edit Baseline). Participants complete 5 UI refinement tasks of increasing complexity. Sessions are limited to 15 minutes per task. Post-study interviews capture qualitative insights.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Technical Artifacts:**
   - Open-source DGUR framework implementation
   - DGUR-Bench dataset with 25,000+ annotated dialogue turns
   - Pre-trained models for grounded correction parsing

2. **Quantitative Results:**
   - 40%+ reduction in iterations needed to achieve desired designs compared to regeneration baseline
   - >85% edit accuracy for unambiguous corrections
   - >70% successful disambiguation through clarification dialogue

3. **Empirical Insights:**
   - Characterization of common correction patterns and failure modes
   - Understanding of how design expertise affects correction strategies
   - Guidelines for designing dialogue-based creative AI tools

### Broader Impact

This research advances the democratization of design tools by enabling non-technical users to effectively collaborate with AI systems. The dialogue-based interaction paradigm respects user agency while leveraging AI capabilities, addressing ethical concerns about AI replacing human creativity. The framework's modular architecture ensures applicability beyond UI design to domains including architectural planning, document layout, and data visualization.

For the research community, DGUR-Bench will serve as a lasting evaluation infrastructure, enabling reproducible comparisons of future interactive generation systems. The uncertainty-aware clarification approach contributes to broader efforts in building trustworthy AI systems that acknowledge their limitations.

By bridging generative AI capabilities with intuitive human feedback mechanisms, this research takes a significant step toward realizing the vision of AI as a collaborative creative partner—responsive, correctable, and aligned with human intent.