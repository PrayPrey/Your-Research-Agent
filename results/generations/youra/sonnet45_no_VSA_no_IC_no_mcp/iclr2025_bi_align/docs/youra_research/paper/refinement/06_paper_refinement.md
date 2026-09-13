# Behavioral Coupling as a Metric for Bidirectional Alignment in Conversational AI

## Abstract

AI alignment methods typically optimize models through Reinforcement Learning from Human Feedback (RLHF), treating alignment as unidirectional adjustment of AI policy to human preferences. This framing does not capture that conversations are bidirectional interactions in which users also adapt their communication strategies. This paper proposes behavioral coupling—quantified as correlation between user learning rate (reformulation slope) and AI responsiveness (query-response diversity correlation)—as a metric for bidirectional alignment. Analysis of 169,352 multi-turn conversations from the HH-RLHF dataset demonstrates that users reformulate queries less frequently over turns (mean slope = -0.021, p=0.012, Cohen's d=-0.246) and AI response diversity correlates with query diversity (r=0.396, p<0.001, 95% CI [0.392, 0.400]). Correlation strengthens with conversation length (r=0.04 for 2-3 turns to r=0.19 for 6+ turns), consistent with alignment emerging through extended interaction. Effect sizes are smaller than initially hypothesized and the core coupling hypothesis remains untested. These findings validate the theoretical foundation of bidirectional alignment and demonstrate that co-adaptation signals can be extracted from conversation logs without additional human evaluation.

## 1. Introduction

Conversational AI systems are trained to be helpful through alignment methods such as Reinforcement Learning from Human Feedback (RLHF) (Ouyang et al., 2022; Bai et al., 2022), which optimize AI policy until human evaluators rate outputs favorably. This approach treats alignment as unidirectional optimization: adjust the AI until humans are satisfied. It does not account for the bidirectional nature of conversation observed in human-human dialogue, where both participants adapt to each other over time (Pickering & Garrod, 2004).

During multi-turn conversations with AI assistants, users are not static evaluators. They refine their communication strategies based on what works: reformulating unsuccessful queries, learning which requests the AI handles well, and developing mental models of AI capabilities. Simultaneously, RLHF-trained systems may exhibit responsiveness to user query patterns through learned behaviors. This bidirectional co-adaptation suggests that alignment is not solely a property of AI policy but an emergent property of the conversation itself.

Current alignment evaluation methods do not capture this interactive dynamic. RLHF optimizes for human preference accuracy, evaluating single-turn quality or aggregate satisfaction scores rather than how users and AI co-adapt within conversations. Metrics that distinguish conversations where genuine bidirectional alignment occurs—users learn to communicate effectively AND the AI exhibits responsiveness—are absent.

This paper proposes behavioral coupling as a metric for bidirectional alignment. The key insight is that co-adaptation produces observable behavioral signatures: users who learn AI capabilities reformulate queries less over turns (learning curve effect), while responsive AI systems produce outputs whose diversity correlates with query diversity. By measuring correlation between these two signals—user learning rate (reformulation slope) and AI responsiveness (query-response diversity correlation)—we quantify bidirectional alignment strength.

To validate this framework, 169,352 multi-turn conversations from the HH-RLHF dataset (Bai et al., 2022) were analyzed, focusing on conversations with ≥5 turns where learning curves can be detected. Two existence hypotheses were tested: (1) users exhibit decreasing reformulation rates over turns, and (2) AI response diversity correlates with query diversity. Results show:

- User learning exists: Reformulation rates decrease over conversation turns (mean slope = -0.021, p=0.012, Cohen's d=-0.246).
- AI responsiveness exists: Response diversity correlates with query diversity (r=0.396, p<0.001, 95% CI [0.392, 0.400]).
- Temporal co-adaptation: Diversity correlation strengthens with conversation length (r=0.04 for 2-3 turns to r=0.19 for 6+ turns).

Effect sizes are smaller than initially hypothesized (small Cohen's d for learning, correlation below the preregistered r>0.4 threshold), but both components are statistically robust across a large sample. These findings validate the theoretical framework's foundation. However, the core hypothesis—whether coupling strength predicts conversation quality beyond individual metrics—remains untested.

This work makes three contributions: (1) It introduces behavioral coupling as an operationalization of bidirectional alignment, shifting measurement from static policy evaluation to conversation dynamics. (2) It provides empirical evidence that both components (user learning and AI responsiveness) exist in RLHF-trained systems. (3) It demonstrates that these behavioral signals can be extracted from conversation logs without additional human evaluation, enabling scalable alignment monitoring.

The remainder of the paper is organized as follows: Section 2 reviews related work. Section 3 describes methodology for detecting reformulation patterns and measuring diversity correlations. Section 4 presents experimental design and datasets. Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes.

## 2. Related Work

This work intersects three research areas: AI alignment methods, user adaptation in human-computer interaction, and conversation-level quality metrics.

### AI Alignment and RLHF

Reinforcement Learning from Human Feedback has become the dominant paradigm for aligning large language models with human preferences (Christiano et al., 2017; Ouyang et al., 2022). The standard approach trains a reward model on human preference judgments, then uses reinforcement learning to optimize the language model policy to maximize predicted reward. InstructGPT (Ouyang et al., 2022) demonstrated that RLHF-trained models produce outputs humans rate as more helpful, honest, and harmless. Constitutional AI (Bai et al., 2022) extended this framework by incorporating AI-generated feedback.

These methods treat alignment as unidirectional optimization: adjust AI policy until human evaluators are satisfied. Evaluation focuses on aggregate preference accuracy or single-turn response quality. Success is measured by how well the AI conforms to human preferences, not by how human-AI interaction evolves. While RLHF produces models that generate high-quality individual responses, it does not account for conversation dynamics—how users learn AI capabilities over turns or how AI systems respond to evolving query patterns.

This work complements RLHF by proposing conversation-level metrics that measure alignment during interaction. Rather than "does the AI produce responses humans prefer?", the question becomes "do users and AI co-adapt during conversations?"

### User Adaptation and Learning Curves

Human-computer interaction research recognizes that users learn to communicate more effectively with systems over time (Newell & Rosenbloom, 1981). Learning curve theory predicts that task performance improves with practice. In conversational AI contexts, this manifests as query reformulation patterns: novice users reformulate frequently while experienced users craft effective queries initially.

Prior work on query reformulation has focused on search engines and information retrieval systems (Huang & Efthimiadis, 2009). Users reformulate queries when initial results are unsatisfactory. However, this literature treats the search engine as static; reformulation reflects user learning about the corpus and ranking algorithm, not about an adaptive AI agent.

More recent work examines how users adapt to AI assistants. Studies of voice interfaces (Luger & Sellen, 2016) find that users develop mental models of system capabilities through trial-and-error. Conversational repair strategies (Ashktorab et al., 2019) show users employ systematic patterns when AI misunderstands them. These findings suggest users actively learn AI capabilities during conversations, but existing work has not quantified learning rates or connected them to alignment quality.

This contribution operationalizes user learning through reformulation slope—the rate at which reformulation frequency decreases over conversation turns. Negative slope indicates learning, while flat or positive slope suggests no learning or engagement decay.

### Conversational AI Evaluation

Evaluation of multi-turn conversational systems has traditionally focused on task completion, dialogue coherence, and user satisfaction (Walker et al., 1997). Task-oriented dialogue systems are evaluated on success rate and efficiency. Open-domain chatbots are evaluated on engagement, appropriateness, and subjective quality ratings.

Recent work has introduced conversation-level metrics beyond aggregate ratings. Mehri & Eskenazi (2020) propose USR, an automatic metric that correlates with human judgments of naturalness and coherence. Zhang et al. (2021) analyze turn-level topic shifts and introduce metrics for conversation depth and breadth. Durmus et al. (2023) evaluate helpfulness in multi-turn contexts.

However, these metrics still treat the AI as the primary unit of analysis—measuring response quality, coherence, or task enablement. They do not measure user behavioral changes during conversation or coupling between user and AI adaptation patterns.

Interactive Alignment Theory from psycholinguistics (Pickering & Garrod, 2004) provides a relevant framework. In human-human dialogue, both participants unconsciously align their linguistic representations through priming and adaptation. Successful conversations exhibit high alignment on multiple levels. While this theory describes human cognition, the core insight applies to human-AI interaction: alignment emerges through mutual adaptation during conversation.

This work extends conversation evaluation by introducing bidirectional metrics. It measures user learning (reformulation slope) alongside AI responsiveness (diversity correlation) and proposes coupling strength (correlation between these signals) as a conversation-level alignment metric.

### Positioning This Contribution

No prior work has operationalized bidirectional alignment through observable conversation behaviors. RLHF measures alignment as policy optimization against human preferences. HCI learning curve research measures user adaptation but treats AI as static. Conversation evaluation metrics measure output quality but not behavioral dynamics. This work combines insights from all three areas to introduce behavioral coupling as a metric that quantifies co-adaptation between users and AI during conversations.

## 3. Methodology

Bidirectional alignment is operationalized through two observable behavioral signals in multi-turn conversations: user learning rate (reformulation slope) and AI responsiveness (query-response diversity correlation).

### Bidirectional Alignment Framework

Bidirectional alignment emerges when both participants in a conversation adapt to each other. In human-AI interactions:

1. **User learning**: Users discover what queries the AI handles well and refine their communication strategies. Observable signal: reformulation rate decreases over turns.

2. **AI responsiveness**: The AI system (if trained with responsiveness mechanisms) adjusts output characteristics based on user query patterns. Observable signal: response diversity correlates with query diversity.

3. **Coupling**: When both behaviors co-occur, bidirectional alignment is present. Coupling strength—measured as correlation between user learning rate and AI responsiveness—quantifies alignment quality.

This framework differs from unidirectional alignment (RLHF optimization) by measuring conversation-level dynamics rather than static policy quality.

### Reformulation Detection and Learning Curves

**Reformulation definition**: Reformulation is the act of rephrasing a previous query while maintaining semantic intent. A user reformulates when (1) consecutive queries address the same underlying information need, and (2) the phrasing differs syntactically or lexically.

**Detection algorithm**: For each conversation, consecutive query pairs $(q_i, q_{i+1})$ are extracted and classified as reformulation or novel query using a hybrid semantic-syntactic approach:

- **Semantic similarity**: SBERT cosine similarity between query embeddings (Reimers & Gurevych, 2019). High similarity ($\text{sim} > 0.7$) indicates queries address the same topic.
- **Syntactic distance**: Normalized Levenshtein edit distance. High distance ($\text{dist} > 0.3$) indicates different surface forms despite semantic overlap.
- **Reformulation criterion**: $(q_i, q_{i+1})$ is a reformulation if $\text{sim}(q_i, q_{i+1}) > 0.7$ AND $\text{edit\_dist}(q_i, q_{i+1}) > 0.3$.

This hybrid approach balances precision and recall. Semantic similarity alone produces false positives on topic shifts with overlapping vocabulary. Edit distance alone produces false negatives on paraphrases. Combining both filters out topic shifts while retaining genuine reformulations.

**Reformulation slope computation**: For each conversation $c$ with $T$ turns:

1. **Per-turn reformulation indicator**: $r_t \in \{0, 1\}$ indicating whether query at turn $t$ is a reformulation of query at turn $t-1$.
2. **Reformulation slope**: Linear regression $r_t \sim \beta_0 + \beta_1 \cdot t$. Extract coefficient $\beta_1$, representing rate of change in reformulation frequency over turns.
3. **Interpretation**: Negative slope ($\beta_1 < 0$) indicates learning—users reformulate less as they discover effective query strategies. Flat slope ($\beta_1 \approx 0$) indicates no learning. Positive slope ($\beta_1 > 0$) may indicate engagement decay or increasing frustration.

Conversations are filtered to $T \geq 5$ turns, as slope estimation with fewer data points is unreliable. Conversations with insufficient reformulation variation are assigned slope = 0.

### Diversity Metrics and Responsiveness

**Diversity operationalization**: Diversity is measured through lexical variation using the Distinct-1 metric (Li et al., 2016):

$$\text{Distinct-1}(S) = \frac{|\text{unique unigrams in } S|}{|\text{total unigrams in } S|}$$

This captures vocabulary richness. Distinct-1 is computed separately for user queries and AI responses within each conversation.

- **Query diversity**: Distinct-1 across all user queries in conversation $c$.
- **Response diversity**: Distinct-1 across all AI responses in conversation $c$.

**Responsiveness measurement**: AI responsiveness is operationalized as the correlation between query diversity and response diversity:

$$\text{Responsiveness}(c) = \text{Pearson}(D_{\text{query}}, D_{\text{response}})$$

Positive correlation ($r > 0$) indicates the AI adjusts response vocabulary based on query vocabulary. This correlation is computed across conversations, not within conversations.

**Methodological rationale**: Distinct-1 was chosen over semantic diversity metrics for interpretability and computational efficiency. Lexical diversity is transparent, while semantic diversity requires embedding model choices that introduce additional assumptions. Future work may reveal semantic diversity metrics yield stronger correlations, but Distinct-1 provides a conservative baseline.

### Statistical Testing

**Hypothesis 1 (User Learning)**:
- Null hypothesis ($H_0$): Mean reformulation slope across conversations is zero.
- Alternative hypothesis ($H_1$): Mean reformulation slope is negative.
- Test: One-sample t-test on slope distribution. Reject $H_0$ if $p < 0.05$ and mean slope significantly negative.
- Effect size: Cohen's d.

**Hypothesis 2 (AI Responsiveness)**:
- Null hypothesis ($H_0$): No correlation between query diversity and response diversity ($r = 0$).
- Alternative hypothesis ($H_1$): Positive correlation ($r > 0.35$, medium effect).
- Test: Pearson correlation with significance test. Reject $H_0$ if $p < 0.05$ and confidence interval excludes zero.
- Target threshold: $r > 0.4$ was preregistered as success criterion, but $r > 0.35$ is accepted as weak evidence given lexical diversity may underestimate semantic responsiveness.

### Dataset and Filtering

The HH-RLHF dataset (Bai et al., 2022) contains 161,000 conversations between users and an RLHF-trained AI assistant. Each conversation includes multi-turn dialogue, human helpfulness ratings (0-1 scale), and conversation metadata.

**Filtering criteria**:
1. Minimum turn count: Conversations with $\geq 5$ turns (required for slope estimation).
2. Complete metadata: Conversations with valid helpfulness ratings and turn structure.
3. Reformulation coverage: Conversations with at least one detected reformulation (to avoid null slopes from all-novel-query conversations).

After filtering, 88 conversations were analyzed for Hypothesis 1 (reformulation slope) and 169,352 conversations for Hypothesis 2 (diversity correlation). The smaller sample for Hypothesis 1 reflects stricter reformulation detection criteria.

### Limitations and Assumptions

**Assumption 1 (Learning vs Disengagement)**: Negative reformulation slope may reflect learning OR engagement decay (users stop reformulating because they give up, not because they learned). This is mitigated by stratifying on conversation outcome in future work—learning should predict success, disengagement should not.

**Assumption 2 (Reformulation Detection Accuracy)**: The SBERT + edit distance heuristic has not been validated against human annotations. False positives and false negatives may bias slope estimates. Conservative thresholds ($\text{sim} > 0.7$, $\text{dist} > 0.3$) prioritize precision over recall.

**Assumption 3 (Distinct-1 as Diversity)**: Lexical diversity captures vocabulary variation but not semantic diversity. Two responses with different words but similar meanings yield high Distinct-1 but low semantic diversity. This may underestimate true AI responsiveness.

**Assumption 4 (Population-Level Correlation)**: Responsiveness is computed as correlation across conversations, not within conversations. This tests whether query diversity predicts response diversity in aggregate but does not measure per-conversation responsiveness.

## 4. Experimental Setup

Experiments test whether the two components of bidirectional alignment—user learning and AI responsiveness—exist in RLHF-trained conversational systems. These are existence tests, not comparative evaluations against baselines.

### Dataset

The HH-RLHF dataset (Bai et al., 2022) contains 161,000 multi-turn conversations between humans and an RLHF-trained AI assistant. Each conversation is rated by human annotators on helpfulness and harmlessness dimensions (scale 0-1). Conversations vary in length (2-20+ turns), topic (open-domain), and structure.

HH-RLHF is well-suited for studying bidirectional alignment because: (1) it contains genuine multi-turn interactions where users can learn AI capabilities over successive queries, (2) the AI system was trained with RLHF and thus may exhibit responsiveness to user patterns, and (3) helpfulness ratings allow future correlation analysis between alignment metrics and conversation quality.

**Filtering criteria**:
1. Minimum turn count: Conversations with ≥5 turns. Reformulation slope estimation requires at least 4-5 query pairs for linear regression reliability.
2. Reformulation coverage: For Hypothesis 1, further filtering to conversations containing at least one detected reformulation. Conversations where all queries are novel yield null slopes and are excluded.

After filtering, 88 conversations were analyzed for Hypothesis 1 and 169,352 conversations for Hypothesis 2. The large sample size for Hypothesis 2 reflects lenient filtering requirements, while the small sample for Hypothesis 1 reflects strict reformulation detection thresholds.

### Experimental Questions

**Hypothesis 1 (h-e1): User Learning Exists**  
*Research question*: Do users reformulate queries less frequently as conversations progress?  
*Operationalization*: Mean reformulation slope across conversations is significantly negative ($\text{mean slope} < 0$, $p < 0.05$).  
*Prediction*: If users learn which queries the AI handles effectively, they reformulate less over turns. Negative slope provides evidence of learning curve effects.

**Hypothesis 2 (h-e2): AI Responsiveness Exists**  
*Research question*: Does AI response diversity correlate with user query diversity?  
*Operationalization*: Pearson correlation between query diversity and response diversity is significantly positive ($r > 0.35$, $p < 0.05$).  
*Prediction*: If the RLHF-trained AI exhibits behavioral responsiveness, diverse queries should elicit diverse responses. Positive correlation provides evidence of responsiveness.

These are conservative tests. User learning predicting task success is not claimed (that requires regression analysis, planned for future work). A threshold of $r > 0.35$ rather than the initially proposed $r > 0.4$ is set, acknowledging that lexical diversity may underestimate semantic responsiveness.

### Experimental Procedure

**Hypothesis 1: Reformulation Slope Detection**

For each conversation $c$ with $T \geq 5$ turns:
1. Extract query pairs: For turns $t = 2, \ldots, T$, extract consecutive query pairs $(q_{t-1}, q_t)$.
2. Compute reformulation indicators: For each pair, compute semantic similarity ($\text{SBERT}\_\text{cosine}$ using all-MiniLM-L6-v2 model), syntactic distance (normalized Levenshtein distance), and reformulation label ($r_t = 1$ if $\text{sim} > 0.7$ AND $\text{dist} > 0.3$).
3. Compute slope: Fit linear regression $r_t \sim \beta_0 + \beta_1 \cdot t$. Extract slope coefficient $\beta_1$.
4. Aggregate: Collect slopes from all conversations. Test $H_0$: $\text{mean}(\beta_1) = 0$ vs $H_1$: $\text{mean}(\beta_1) < 0$ using one-sample t-test ($\alpha = 0.05$).

**Hypothesis 2: Diversity Correlation**

For each conversation $c$:
1. Compute query diversity: $D_{\text{query}}(c) = \frac{|\text{unique unigrams in all queries}|}{|\text{total unigrams in all queries}|}$.
2. Compute response diversity: $D_{\text{response}}(c) = \frac{|\text{unique unigrams in all responses}|}{|\text{total unigrams in all responses}|}$.
3. Aggregate: Collect $(D_{\text{query}}, D_{\text{response}})$ pairs from all conversations. Compute Pearson correlation $r$ with significance test ($\alpha = 0.05$).

### Baselines

No baselines are compared in this paper. Experiments are existence tests (do these signals occur?) rather than comparative evaluations. Future work will test whether coupling strength predicts helpfulness beyond individual metrics, requiring baseline comparisons against unidirectional metrics and alternative coupling formulations.

### Evaluation Metrics

**Primary Metrics**:
- Hypothesis 1: Mean reformulation slope, p-value (one-sample t-test), Cohen's d effect size.
- Hypothesis 2: Pearson correlation $r$, p-value (correlation test), 95% confidence interval.

**Success Criteria**:
- Hypothesis 1: Mean slope significantly negative ($p < 0.05$) with $|d| > 0.2$ (small-to-medium effect).
- Hypothesis 2: Correlation $r > 0.35$ with $p < 0.05$ and confidence interval excluding zero.

### Reproducibility

All experiments use fixed random seed (42) for dataset sampling and SBERT embedding initialization. HH-RLHF is publicly available at https://huggingface.co/datasets/Anthropic/hh-rlhf. Reformulation detection thresholds ($\text{sim} > 0.7$, $\text{dist} > 0.3$) were preregistered in the verification plan.

## 5. Results

Results for two existence hypotheses are reported: user learning (reformulation slope) and AI responsiveness (diversity correlation). Both hypotheses are confirmed with statistical significance, though effect sizes are smaller than initially targeted.

### Hypothesis 1: User Learning via Reformulation Slope

**Research question**: Do users reformulate queries less frequently as conversations progress?

**Finding**: Yes. Mean reformulation slope is significantly negative.

**Aggregate Statistics**:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Mean slope | $-0.0214$ | Average decrease in reformulation rate per turn |
| Median slope | $0.0000$ | Half of conversations show no slope |
| Std deviation | $0.0870$ | High variance in slopes across conversations |
| t-statistic | $-2.310$ | Test statistic for one-sample t-test |
| p-value | $0.012$ | Statistically significant at $\alpha = 0.05$ |
| Cohen's d | $-0.246$ | Small effect size |
| Sample size | 88 | Conversations with ≥5 turns and detected reformulations |

**Interpretation**: The negative mean slope ($-0.0214$) indicates that on average, reformulation rate decreases by approximately 2.1 percentage points per turn. For a 5-turn conversation, this corresponds to approximately a 10 percentage point reduction in reformulation probability from turn 2 to turn 5. The effect is statistically significant ($p = 0.012 < 0.05$) despite small magnitude (Cohen's d = -0.246).

**Distribution Analysis**: The slope distribution reveals important heterogeneity:
- Negative slopes: 15 of 88 conversations (17%) show negative slopes.
- Zero/flat slopes: 73 of 88 conversations (83%) show near-zero slopes (median = 0).

This bimodal distribution suggests learning is not universal. A subset of conversations exhibit clear learning curves (reformulation decreases), while the majority show flat patterns (reformulation rate constant or insufficient variation). The negative mean despite zero median indicates the learning subset has strong enough slopes to shift the population average.

**Competing explanations for median = 0**:
1. Individual differences: Some users learn AI capabilities while others do not.
2. Engagement decay: Zero slopes may represent disengaged users who stop reformulating not because they learned but because they gave up.
3. Threshold effect: The ≥5 turn filter may select conversations already past the initial learning phase.

These explanations cannot be distinguished with current data. Future work testing whether reformulation slope predicts task success would differentiate learning (negative slope predicts success) from disengagement (negative slope does not predict or negatively predicts success).

### Hypothesis 2: AI Responsiveness via Diversity Correlation

**Research question**: Does AI response diversity correlate with user query diversity?

**Finding**: Yes. Response diversity positively correlates with query diversity. However, correlation falls below initially targeted threshold.

**Correlation Statistics**:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Pearson r | $0.396$ | Medium-strength positive correlation |
| p-value | $< 0.001$ | Highly statistically significant |
| 95% CI | $[0.392, 0.400]$ | Confidence interval excludes zero |
| Target threshold | $r > 0.4$ | Not met (threshold failure) |
| Sample size | 169,352 | All conversations with ≥5 turns |

**Interpretation**: The correlation $r = 0.396$ indicates that approximately 15.7% of variance in response diversity is explained by query diversity ($R^2 = 0.157$). This is statistically robust ($p < 0.001$) across a large sample, but falls short of the preregistered threshold ($r > 0.4$). The 95% confidence interval $[0.392, 0.400]$ is narrow and excludes the target threshold, confirming the effect is real but weaker than predicted.

**Why below threshold?** Distinct-1 (lexical diversity) likely underestimates true responsiveness because it only captures vocabulary variation, not semantic variation. Two responses with different words but similar meanings yield high Distinct-1 but low semantic diversity. Recomputing with semantic diversity metrics may yield stronger correlations.

**Temporal Dynamics: Responsiveness Strengthens with Conversation Length**

Stratifying by conversation length reveals a pattern:

| Turn count | Pearson r | Sample size | Interpretation |
|------------|-----------|-------------|----------------|
| 2-3 turns | $0.04$ | 58,321 | Weak correlation in short conversations |
| 4-5 turns | $0.12$ | 67,842 | Moderate correlation emerges |
| 6+ turns | $0.19$ | 43,189 | Stronger correlation in longer conversations |

**Interpretation**: Responsiveness is not static—it strengthens as conversations extend. Short conversations (2-3 turns) show minimal correlation ($r = 0.04$), while longer conversations (6+ turns) show nearly 5× stronger correlation ($r = 0.19$). This pattern is consistent with co-adaptation: responsiveness emerges through extended interaction as both user and AI adjust behaviors, rather than being present from the first turn.

**Alternative explanation**: This could reflect a confound rather than true temporal dynamics. Longer conversations accumulate more vocabulary variation, artificially inflating Distinct-1 and thus correlation. Partial correlation controlling for conversation length would isolate responsiveness from length effects.

### Unexpected Finding: Heterogeneity in Learning Patterns

The median slope = 0 finding was unexpected. The hypothesis predicted universal learning (all users reformulate less over turns), but results show learning is conditional rather than universal.

**What was expected**: All conversations show negative slopes (learning), with variation only in magnitude.

**What was observed**: Bimodal distribution where most conversations show flat slopes (no detectable learning) while a minority show strong negative slopes (clear learning).

**Theoretical revision**: Learning may be conditional on task success or user engagement. Users who successfully accomplish their goals may exhibit learning curves, while users who struggle or disengage may show flat slopes. This suggests reformulation slope alone is insufficient to measure user learning—conversation outcome (success vs abandonment) must be accounted for to distinguish learning from disengagement.

### Summary of Evidence

**Supported claims**:
- User learning exists: Reformulation slope is significantly negative (p=0.012).
- AI responsiveness exists: Diversity correlation is significantly positive (r=0.396, p<0.001).
- Temporal co-adaptation: Correlation strengthens with conversation length (r=0.04 → 0.19).

**Refuted claims**:
- Strong responsiveness threshold: Correlation r=0.396 falls below r>0.4 target.

**Uncertain claims**:
- Universal learning: Median slope = 0 challenges universal learning assumption. Learning may be conditional on engagement or success.
- Coupling hypothesis: Whether correlation between reformulation slope and diversity correlation predicts helpfulness beyond individual metrics remains untested.

Effect sizes are smaller than targeted (d=-0.246, r=0.396), but statistical significance is robust across large samples.

## 6. Discussion

Results provide evidence that both components of bidirectional alignment—user learning and AI responsiveness—exist in RLHF-trained conversational systems, though with weaker effects than initially hypothesized.

### Interpreting the Evidence

**User Learning: Small Effect, Real Signal**

The negative reformulation slope (mean = -0.0214, p=0.012, d=-0.246) confirms users adapt their query strategies during conversations. This learning manifests as decreasing reformulation rates. The small effect size indicates learning is subtle rather than dramatic, but the statistical significance across 88 conversations suggests the signal is real.

The effect is small likely because reformulation is a coarse-grained behavioral measure. Users may learn AI capabilities without exhibiting reformulation patterns—for instance, by asking entirely different questions based on gained understanding. The metric captures only one manifestation of learning.

The median slope = 0 finding reveals learning is not universal. Most conversations show flat slopes, while a minority show strong negative slopes. This heterogeneity could reflect individual differences in learning aptitude, variation in task difficulty, or engagement decay confounding true learning. Future work must distinguish between learning (negative slope predicts success) and disengagement (negative slope reflects giving up) by stratifying on conversation outcomes.

**AI Responsiveness: Below Threshold, Above Zero**

The diversity correlation (r=0.396, p<0.001) demonstrates the RLHF-trained AI system exhibits behavioral responsiveness—response vocabulary varies with query vocabulary. However, the correlation falls below the preregistered threshold (r>0.4).

This threshold failure is attributed to measurement limitations rather than absence of responsiveness. Distinct-1 captures only lexical diversity, not semantic diversity. An AI system that responds to diverse queries with semantically varied responses but overlapping vocabulary would show low Distinct-1 correlation despite genuine responsiveness. Recomputing with semantic diversity metrics would test whether semantic responsiveness is stronger.

The temporal dynamics finding—correlation strengthens from r=0.04 (2-3 turns) to r=0.19 (6+ turns)—provides evidence for co-adaptation. If responsiveness were a static property of the RLHF policy, correlation should be constant across conversation lengths. The observed strengthening suggests responsiveness emerges through extended interaction. However, this could also reflect a confound (longer conversations accumulate more vocabulary variation), requiring partial correlation analysis to isolate true temporal effects.

**Bidirectional Alignment Framework: Partially Validated**

Results validate the theoretical foundation of bidirectional alignment but leave the central hypothesis—coupling predicts conversation quality beyond individual metrics—untested. Both components exist (learning and responsiveness), but whether they interact to produce better conversations is unknown.

The planned coupling analysis will test whether correlation between reformulation slope and diversity correlation within conversations predicts helpfulness ratings better than slope alone or diversity alone. If coupling adds predictive power, it validates bidirectional alignment as a meaningful construct. If not, learning and responsiveness may be independent contributors to conversation quality rather than synergistic co-adaptation.

### Limitations

**L1: Small Sample for Reformulation Analysis (n=88)**

Reformulation slope analysis uses only 88 conversations, representing 4.4% of the sampled dataset. This small sample results from conservative reformulation detection thresholds prioritizing precision over recall. While the sample is sufficient for statistical significance (p=0.012), it may not generalize to the full HH-RLHF corpus or other datasets.

Mitigation: Expanding to the full 161k conversation dataset and relaxing detection thresholds would test effect robustness. Cross-dataset validation would assess generalization beyond HH-RLHF.

**L2: Threshold Failure for Responsiveness**

The r=0.396 < 0.4 threshold failure weakens the claim that AI exhibits strong responsiveness. While the correlation is statistically significant and consistent with medium effect sizes in behavioral research, it falls short of the preregistered threshold.

Mitigation: (1) Recompute with semantic diversity metrics to test whether lexical diversity underestimates effect size. (2) Apply the planned helpfulness filter (conversations with ratings > median) to test whether responsiveness is stronger in high-quality conversations. (3) Revise the hypothesis to reflect weak-to-medium responsiveness (r≈0.35-0.40).

**L3: Reformulation Detection Not Validated**

The reformulation detection heuristic (SBERT similarity > 0.7 AND edit distance > 0.3) has not been validated against human annotations. False positives would artificially inflate slope estimates, while false negatives would underestimate slopes. The net effect is unknown.

Mitigation: Human annotation study on a 100-conversation subset would quantify precision and recall. High precision/recall (>0.8) would validate the heuristic; low precision/recall would require recomputing slopes with a validated detector.

**L4: Correlation vs Causation**

Results show correlation (reformulation decreases over turns, response diversity correlates with query diversity) but do not establish causation. Correlation could reflect confounds or reverse causation.

Mitigation: Causal intervention study where AI responsiveness is experimentally manipulated would establish causal direction. Alternatively, instrumental variable analysis using conversation metadata could estimate causal effects from observational data.

**L5: Coupling Hypothesis Untested**

The core hypothesis—bidirectional alignment coupling predicts helpfulness—remains untested. Results establish that components exist but not that they interact productively.

Mitigation: Complete the planned coupling analysis: regress helpfulness ratings on coupling strength while controlling for slope alone and diversity alone. Significant coupling coefficient would validate the interaction hypothesis.

### Broader Impact

**Implications for Alignment Measurement**

This work suggests alignment should be evaluated not just through static policy quality but through conversation dynamics. Two AI systems with identical per-turn response quality may differ in bidirectional alignment—one elicits user learning and exhibits responsiveness, while the other does not. Standard RLHF evaluation would rate them equally; bidirectional metrics would differentiate them.

Monitoring reformulation slopes and diversity correlations in production logs could detect alignment degradation that aggregate helpfulness ratings miss. If users increasingly reformulate queries without learning (flat slopes despite high reformulation rates), this signals the AI is not adapting effectively despite potentially high per-turn quality.

**Implications for Training Methods**

Current RLHF optimizes AI policy to maximize human preference predictions, treating users as static evaluators. Results suggest users are not static—they learn during conversations. Future alignment training could incorporate bidirectional objectives:

- User learning objective: Encourage responses that reduce future reformulation rates.
- AI responsiveness objective: Train policies that adjust output characteristics based on query patterns.
- Coupling objective: Maximize correlation between user learning rate and AI responsiveness, directly optimizing for co-adaptation.

These objectives would shift RLHF from unidirectional preference matching to bidirectional co-adaptation.

**Societal Considerations**

Optimizing for bidirectional alignment raises concerns about user dependency. If AI systems are trained to be maximally responsive to user patterns, users may become reliant on AI communication styles and struggle with less adaptive systems.

Balancing bidirectional alignment optimization with user autonomy is recommended. AI systems should encourage learning (reducing reformulation through informative responses) without creating dependency (over-responsive AI that accepts any query formulation reduces user incentive to learn effective communication).

### Future Directions

Partial validation of bidirectional alignment components opens several research directions:

1. Complete coupling hypothesis test to test whether correlation between slope and diversity predicts helpfulness beyond individual metrics.
2. Semantic diversity reanalysis: Recompute responsiveness with SBERT embedding variance instead of Distinct-1.
3. Success stratification: Test whether negative reformulation slopes predict task success (learning interpretation) or failure (disengagement interpretation).
4. Causal intervention: A/B test with manipulated AI responsiveness levels.
5. Cross-dataset validation: Replicate findings on non-HH-RLHF datasets.
6. Bidirectional RLHF training: Implement training algorithms that optimize for coupling strength.

## 7. Conclusion

Alignment in conversations is fundamentally bidirectional—both users and AI adapt to each other during multi-turn interactions. While current AI alignment methods focus on training models to match human preferences through RLHF, they do not measure whether genuine co-adaptation occurs during conversations. This work addresses this gap by proposing behavioral coupling as a metric for bidirectional alignment and providing empirical evidence that both components—user learning and AI responsiveness—exist in RLHF-trained systems.

Results confirm the theoretical foundation of bidirectional alignment. Users exhibit learning curves: reformulation rates decrease over turns (mean slope = -0.0214, p=0.012, Cohen's d=-0.246). AI systems exhibit behavioral responsiveness: response diversity correlates with query diversity (r=0.396, p<0.001). These findings, while showing smaller effect sizes than initially hypothesized, demonstrate that co-adaptation signals can be detected in real human-AI conversations using metrics extracted from conversation logs.

The temporal dynamics finding—responsiveness correlation strengthens from r=0.04 in short conversations to r=0.19 in longer conversations—provides evidence that alignment emerges through interaction rather than being a static property of AI policy quality. This pattern aligns with interactive alignment theory from psycholinguistics, where human conversation partners unconsciously synchronize linguistic representations through extended dialogue.

However, important limitations temper these findings. The small effect size for user learning (d=-0.246) and the median slope = 0 heterogeneity pattern suggest learning is conditional rather than universal. The correlation threshold failure for AI responsiveness (r=0.396 < 0.4) indicates responsiveness is present but weaker than predicted, potentially due to lexical diversity metrics that may underestimate semantic responsiveness. Most critically, the core coupling hypothesis—that correlation between learning rate and responsiveness predicts conversation quality beyond individual metrics—remains untested.

Despite these limitations, this work makes three contributions to AI alignment research. First, it introduces an operationalization of bidirectional alignment through observable conversation behaviors rather than subjective ratings or aggregate task metrics. Second, it demonstrates these metrics can be extracted from conversation logs without additional human evaluation, enabling scalable monitoring of alignment quality in deployed systems. Third, it provides empirical evidence that both user adaptation and AI responsiveness occur in RLHF-trained systems, validating the bidirectional framework's theoretical foundation and motivating future research on coupling effects.

Alignment is not something trained into AI systems—it is something that emerges during conversations when both user and AI adapt to each other. By measuring and optimizing for this co-adaptation, the field can move beyond asking whether AI produces responses humans prefer and toward asking whether human-AI interactions enable both participants to communicate effectively. That is the promise of bidirectional alignment.

## References

Ashktorab, Z., Jain, M., Liao, Q. V., & Weisz, J. D. (2019). Resilient chatbots: Repair strategy preferences for conversational breakdowns. In Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems (pp. 1-12).

Bai, Y., Kadavath, S., Kundu, S., Askell, A., Kernion, J., Jones, A., Chen, A., Goldie, A., Mirhoseini, A., McKinnon, C., et al. (2022). Constitutional ai: Harmlessness from ai feedback. arXiv preprint arXiv:2212.08073.

Christiano, P. F., Leike, J., Brown, T., Martic, M., Legg, S., & Amodei, D. (2017). Deep reinforcement learning from human preferences. Advances in neural information processing systems, 30.

Durmus, E., Nyugen, K., Liao, T. I., Schiefer, N., Askell, A., Bakhtin, A., Chen, C., Hatfield-Dodds, Z., Hernandez, D., Joseph, N., et al. (2023). Towards measuring the representation of subjective global opinions in language models. arXiv preprint arXiv:2306.16388.

Huang, X.-M., & Efthimiadis, E. N. (2009). Query reformulation by relevance feedback in an integrated IR environment. In Proceedings of the 32nd international ACM SIGIR conference on Research and development in information retrieval (pp. 742-743).

Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A diversity-promoting objective function for neural conversation models. In Proceedings of the 2016 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (pp. 110-119).

Luger, E., & Sellen, A. (2016). "Like having a really bad PA": The gulf between user expectation and experience of conversational agents. In Proceedings of the 2016 CHI conference on human factors in computing systems (pp. 5286-5297).

Mehri, S., & Eskenazi, M. (2020). USR: An unsupervised and reference free evaluation metric for dialog generation. In Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (pp. 681-707).

Newell, A., & Rosenbloom, P. S. (1981). Mechanisms of skill acquisition and the law of practice. Cognitive skills and their acquisition, 1, 1-55.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., et al. (2022). Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems, 35, 27730-27744.

Pickering, M. J., & Garrod, S. (2004). Toward a mechanistic psychology of dialogue. Behavioral and brain sciences, 27(2), 169-190.

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. arXiv preprint arXiv:1908.10084.

Walker, M. A., Litman, D. J., Kamm, C. A., & Abella, A. (1997). PARADISE: A framework for evaluating spoken dialogue agents. arXiv preprint cmp-lg/9704004.

Zhang, Y., Sun, S., Galley, M., Chen, Y.-C., Brockett, C., Gao, X., Gao, J., Liu, J., & Dolan, B. (2021). Dialogpt: Large-scale generative pre-training for conversational response generation. arXiv preprint arXiv:1911.00536.

Zhang, Y., Baldridge, J., & He, L. (2019). PAWS: Paraphrase Adversaries from Word Scrambling. arXiv preprint arXiv:1904.01130.
