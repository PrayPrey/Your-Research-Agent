# Research Proposal: Deliberative Evaluation Protocol with Participatory Concept Calibration (DEP-PCC) for Stakeholder-Driven AI Impact Assessment

## 1. Introduction

### 1.1 Background

Generative AI systems have rapidly proliferated across society, producing text, images, audio, and video content with profound implications for employment, creativity, information integrity, and social dynamics. As these systems become embedded in critical domains—from healthcare to education to democratic processes—the need for comprehensive evaluation frameworks that capture their broader societal impacts has become urgent. The NeurIPS Broader Impact statement requirement, introduced in 2020, represented a significant normative shift toward acknowledging that AI research carries societal consequences beyond technical performance metrics. However, this requirement exposed a fundamental gap: no standardized methodology exists for systematically assessing these broader impacts.

Current evaluation practices suffer from a critical limitation—they are designed almost exclusively by technical experts operating within academic and industry contexts. While these experts possess deep understanding of algorithmic behavior and technical failure modes, they may lack direct experience with how AI systems affect diverse communities in practice. Research by Sambasivan et al. (2021) has documented how AI systems designed without meaningful community input can perpetuate harms that technical evaluations fail to anticipate. Similarly, Solaiman et al.'s comprehensive taxonomy of AI evaluation categories, while valuable, was developed primarily through expert synthesis rather than participatory methods.

The emerging field of deliberative democracy offers promising methodological foundations for addressing this gap. Fishkin et al. (2025) have demonstrated that structured deliberative processes can elicit "considered opinions" that differ meaningfully from raw preferences, particularly when participants receive balanced informational briefings. Separately, Fortes (2025) introduced Participatory Concept Calibration (PCC), a methodology using quantitative framing to enable non-experts to validate complex conceptual translations. The Collective Constitutional AI (CCAI) project by Huang et al. (2024) further demonstrated that multi-stage public input can be integrated into AI governance at scale.

### 1.2 Research Objectives

This research proposes to develop and validate the Deliberative Evaluation Protocol with Participatory Concept Calibration (DEP-PCC), a two-tier methodology that systematically translates non-expert stakeholder concerns into validated AI evaluation criteria. Our specific objectives are:

1. **Design and implement** a structured deliberative protocol that enables non-expert stakeholders to meaningfully engage with generative AI societal impacts
2. **Develop and validate** a Participatory Concept Calibration mechanism that translates qualitative stakeholder concerns into formal, measurable evaluation criteria
3. **Empirically test** whether DEP-PCC-generated criteria achieve higher stakeholder satisfaction, comprehension, and perceived representativeness compared to expert-designed criteria alone
4. **Produce** a replicable framework and documentation standards for participatory AI evaluation design

### 1.3 Research Significance

This research addresses the workshop's central concern—broadening participation in AI evaluation—through rigorous methodological innovation. If successful, DEP-PCC would establish the first validated protocol for incorporating diverse public perspectives into AI impact assessment, potentially transforming how the AI community approaches broader impact evaluation. The methodology could inform policy recommendations for regulatory bodies seeking evidence of meaningful public input, while providing practitioners with actionable tools for stakeholder engagement. By bridging deliberative democracy methods with AI evaluation science, this work contributes to both fields while addressing an urgent societal need.

## 2. Methodology

### 2.1 Research Design Overview

DEP-PCC operates through a three-stage causal mechanism validated across two tiers of participation:

**Stage 1: Structured Deliberation** → Authentic Concern Elicitation  
**Stage 2: Participatory Concept Calibration** → Validated Translation  
**Stage 3: Two-Tier Verification** → Representativeness Confirmation

The protocol produces validated AI evaluation criteria as its primary output.

### 2.2 Tier 1: Citizens' Assembly Deliberation

#### 2.2.1 Participant Recruitment

We will recruit $n_1 = 40$ participants through stratified random sampling to ensure demographic diversity across age, gender, education level, geographic region, and prior AI familiarity. Inclusion criteria require participants to be adults (18+) with no professional AI/ML background. Participants receive compensation at $\$25$/hour for approximately 6 hours of engagement.

#### 2.2.2 Balanced AI Briefing Materials

Prior to deliberation, participants receive a 90-minute briefing session covering:
- Generative AI capabilities and limitations (30 minutes)
- Documented societal impacts—both beneficial and harmful (30 minutes)
- Existing evaluation approaches and their limitations (20 minutes)
- Interactive Q&A with neutral facilitators (10 minutes)

Materials undergo review by both AI experts and science communication specialists to ensure accuracy and accessibility. Comprehension is assessed through a 10-item quiz with a minimum threshold of 70% correct responses required for deliberation participation.

#### 2.2.3 Deliberation Protocol

The deliberation follows established citizens' assembly methodology:

**Small-Group Phase (2 hours):** Participants are divided into groups of 5-6, each with a trained facilitator. Groups address structured prompts:
- "What concerns you most about generative AI in your daily life?"
- "What harms have you witnessed or experienced?"
- "What would meaningful evaluation of these systems look like?"

Facilitators use nominal group technique to ensure equal participation. All sessions are recorded and transcribed.

**Plenary Synthesis (1.5 hours):** Groups reconvene to share findings. A structured affinity mapping process identifies cross-cutting themes. Participants vote on priority concerns using ranked-choice methodology.

**Output:** A ranked list of $k$ stakeholder concerns (typically $k = 8-15$) with qualitative descriptions and illustrative examples.

### 2.3 Stage 2: Participatory Concept Calibration (PCC)

#### 2.3.1 Initial Translation

AI evaluation experts translate each stakeholder concern $C_i$ into a candidate formal criterion $F_i$ using the following structure:

$$F_i = \langle D_i, M_i, T_i, S_i \rangle$$

Where:
- $D_i$ = Definition (precise specification of what is being evaluated)
- $M_i$ = Measurement approach (how the criterion would be assessed)
- $T_i$ = Threshold (what constitutes acceptable/unacceptable performance)
- $S_i$ = Scope (which AI systems/contexts the criterion applies to)

Each criterion is mapped to Solaiman et al.'s 7-category evaluation ontology to ensure comprehensive coverage.

#### 2.3.2 Quantitative Framing Calibration

Following Fortes (2025), we employ quantitative framing to enable stakeholder validation. For each translated criterion $F_i$, we present stakeholders with:

1. **Semantic fidelity rating:** "On a scale of 0-100, how well does this formal criterion capture your original concern?"
2. **Completeness rating:** "What percentage of your concern is addressed by this criterion?"
3. **Distortion identification:** "Does this translation add anything that wasn't part of your original concern? (Yes/No, with explanation)"

The translation fidelity score $\phi_i$ is computed as:

$$\phi_i = \frac{1}{n_v} \sum_{j=1}^{n_v} \left( 0.5 \cdot \frac{S_{ij}}{100} + 0.4 \cdot \frac{C_{ij}}{100} + 0.1 \cdot (1 - D_{ij}) \right)$$

Where $S_{ij}$, $C_{ij}$, and $D_{ij}$ are semantic fidelity, completeness, and distortion scores from validator $j$, and $n_v$ is the number of validators.

#### 2.3.3 Iterative Refinement

If $\phi_i < 0.7$, the criterion enters iterative refinement:

1. Experts revise $F_i$ based on stakeholder feedback
2. Revised criterion $F_i'$ is re-presented to stakeholders
3. Process repeats until $\phi_i \geq 0.7$ or maximum 3 iterations

**Falsification condition:** If $\phi_i < 0.5$ after 3 iterations for >50% of criteria, the PCC mechanism is considered to have failed.

### 2.4 Stage 3: Two-Tier Verification

#### 2.4.1 Tier 2 Survey Design

A broader survey ($n_2 \geq 500$) verifies representativeness of Tier 1 outputs. Participants are recruited through stratified sampling matching national demographics. The survey presents:

1. The finalized evaluation criteria with plain-language explanations
2. Satisfaction measures (7-point Likert scales) assessing:
   - "These criteria reflect concerns important to people like me"
   - "I would trust evaluations using these criteria"
   - "My perspective is represented in these criteria"
3. Comprehension test (10 items assessing understanding of criteria meaning and application)

#### 2.4.2 Representativeness Analysis

We compute the representativeness gap $\Delta_R$ as:

$$\Delta_R = |\bar{S}_{T1} - \bar{S}_{T2}|$$

Where $\bar{S}_{T1}$ and $\bar{S}_{T2}$ are mean satisfaction scores for Tier 1 and Tier 2 participants respectively.

**Falsification condition:** If $\Delta_R > 1.5$ points on the 7-point scale, representativeness is considered inadequate.

### 2.5 Experimental Validation: Comparative Study

#### 2.5.1 Design

A between-subjects randomized controlled experiment compares DEP-PCC criteria against expert-designed criteria.

**Conditions:**
- **Treatment:** Evaluation criteria generated through full DEP-PCC protocol
- **Control:** Evaluation criteria designed by AI ethics experts using standard methods (literature review, expert consultation)

Both sets of criteria address the same generative AI system (GPT-4 or equivalent) and cover the same evaluation domains.

#### 2.5.2 Participants

$N \geq 128$ participants ($n \geq 64$ per condition), recruited through stratified sampling. Participants are randomly assigned to conditions and blinded to condition labels.

#### 2.5.3 Measures

**Primary outcome:** Stakeholder satisfaction composite score (mean of 5 Likert items, $\alpha > 0.8$ required)

**Secondary outcomes:**
- Comprehension score (% correct on 15-item test)
- Perceived representativeness (3-item subscale)
- Criteria actionability (expert panel rating, 1-5 scale)

#### 2.5.4 Statistical Analysis

**Primary analysis:** Independent samples t-test comparing satisfaction scores between conditions.

$$t = \frac{\bar{X}_{DEP} - \bar{X}_{Expert}}{s_p \sqrt{\frac{2}{n}}}$$

Where $s_p$ is the pooled standard deviation.

**Effect size:** Cohen's $d$ with 95% confidence interval

$$d = \frac{\bar{X}_{DEP} - \bar{X}_{Expert}}{s_p}$$

**Success criteria:** $p < 0.05$ and $d \geq 0.5$

**Falsification criteria:** $p > 0.10$ OR $d < 0.2$

**Secondary analyses:**
- One-sample proportion test for comprehension (H₀: $\pi \leq 0.80$)
- One-sample t-test for translation fidelity (H₀: $\mu \leq 0.7$)
- Subgroup analyses by demographic characteristics

### 2.6 Data Collection and Management

All deliberation sessions are audio/video recorded with participant consent. Transcripts undergo thematic analysis using NVivo software. Quantitative data are collected through Qualtrics surveys with attention checks. Inter-rater reliability (IRR) is computed for all coded measures using Krippendorff's $\alpha$ with minimum threshold of 0.7.

### 2.7 Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Preparation | Month 1-2 | Material development, facilitator training, IRB approval |
| Tier 1 Deliberation | Month 3 | Recruitment, briefing, deliberation sessions |
| PCC Translation | Month 4 | Expert translation, iterative calibration |
| Tier 2 Verification | Month 5 | Survey deployment, representativeness analysis |
| Comparative Study | Month 6-7 | Experimental validation |
| Analysis & Writing | Month 8-9 | Statistical analysis, manuscript preparation |

## 3. Expected Outcomes & Impact

### 3.1 Primary Outcomes

We hypothesize that DEP-PCC will produce evaluation criteria demonstrating:

1. **Higher stakeholder satisfaction** ($d \geq 0.5$, $p < 0.05$) compared to expert-designed criteria, indicating that participatory methods produce criteria perceived as more legitimate and representative
2. **High comprehension** (>80% scores) among non-expert evaluators, demonstrating that PCC successfully translates complex concepts into accessible criteria
3. **Validated translation fidelity** (>0.7 verification scores), confirming that the methodology preserves stakeholder intent through formalization

### 3.2 Deliverables

1. **Validated DEP-PCC Protocol:** Complete documentation including facilitator guides, briefing materials, PCC instruments, and analysis templates
2. **Evaluation Criteria Set:** A validated set of stakeholder-derived criteria for generative AI impact assessment, mapped to existing taxonomies
3. **Empirical Evidence:** Peer-reviewed publication reporting comparative study results
4. **Policy Recommendations:** Guidelines for incorporating participatory methods into AI governance frameworks

### 3.3 Broader Impact

**For the AI Research Community:** DEP-PCC provides a rigorous methodology for operationalizing the NeurIPS Broader Impact requirement, moving beyond ad-hoc assessments toward systematic stakeholder engagement.

**For AI Governance:** The protocol offers regulators evidence-based procedures for demonstrating meaningful public input in AI oversight, addressing democratic legitimacy concerns.

**For Affected Communities:** By centering non-expert perspectives, DEP-PCC ensures that evaluation criteria reflect lived experiences of AI impacts rather than expert assumptions about what matters.

**For Evaluation Science:** The research advances understanding of how deliberative methods can be adapted for technical domains, contributing methodological innovations applicable beyond AI.

### 3.4 Limitations and Future Directions

We acknowledge several limitations. First, the resource intensity of DEP-PCC (2-3 months, trained facilitators, participant compensation) may limit adoption for lower-stakes evaluations. Future work should explore streamlined variants. Second, our initial validation occurs in Western contexts; cultural adaptation protocols require separate validation before international deployment. Third, the methodology complements rather than replaces technical evaluation—integration frameworks remain to be developed.

If primary hypotheses are falsified, this would provide valuable evidence about the limits of participatory methods in technical domains, informing alternative approaches to stakeholder engagement in AI governance.

### 3.5 Conclusion

DEP-PCC represents a systematic attempt to bridge the gap between AI evaluation science and democratic participation. By rigorously testing whether non-expert stakeholders can meaningfully contribute to evaluation criteria design, this research addresses a critical need identified by the workshop: broadening expertise involved in shaping AI evaluations. Success would establish new standards for participatory AI governance while producing more legitimate, comprehensive evaluation frameworks that reflect authentic community concerns about generative AI's societal impacts.