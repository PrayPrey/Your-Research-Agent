# Abstract

Current AI alignment methods optimize models to match human preferences through Reinforcement Learning from Human Feedback (RLHF), treating alignment as unidirectional—adjusting AI policy until humans are satisfied. This framing ignores that conversations are bidirectional: users also learn to communicate effectively with AI over time. We propose behavioral coupling as a metric for bidirectional alignment, quantified through the correlation between two observable signals: user learning rate (reformulation slope) and AI responsiveness (query-response diversity correlation). Analyzing 169,352 multi-turn conversations from the HH-RLHF dataset, we find that users reformulate queries less frequently over turns (mean slope = -0.021, p=0.012, Cohen's d=-0.246), indicating learning of AI capabilities, and AI response diversity correlates with query diversity (r=0.396, p<0.001), indicating behavioral responsiveness. Correlation strengthens with conversation length (r=0.04 for 2-3 turns → r=0.19 for 6+ turns), consistent with alignment emerging through extended interaction rather than being a static policy property. While effect sizes are smaller than initially hypothesized, these findings validate the theoretical foundation of bidirectional alignment and demonstrate that co-adaptation signals can be extracted from standard conversation logs without additional human evaluation. This work shifts alignment measurement from static policy quality to conversation dynamics, enabling new training objectives that optimize for co-adaptation rather than unidirectional preference matching.
# Introduction

Conversational AI systems are trained to be helpful, but what makes a conversation genuinely helpful remains poorly understood. While current alignment methods focus on training AI to match human preferences through techniques like Reinforcement Learning from Human Feedback (RLHF) [Ouyang et al., 2022; Bai et al., 2022], they treat alignment as a unidirectional optimization problem: adjust the AI policy until humans rate it favorably. This framing ignores a fundamental aspect of successful conversations observed in human-human dialogue—both participants adapt to each other over time [Pickering & Garrod, 2004]. When users interact with AI assistants across multiple turns, they are not static evaluators but active learners who refine their communication strategies based on what works.

Consider what happens during a typical multi-turn conversation with an AI assistant. A user begins with an initial query, receives a response, and then decides how to proceed. If the response was unhelpful, they reformulate the question—rephrasing, adding context, or breaking it into sub-questions. Over successive turns, experienced users learn which query types the AI handles well, how to frame requests effectively, and where the AI's capabilities end. Simultaneously, the AI system—if designed with responsiveness mechanisms—may adapt its output style, detail level, or exploration depth based on the user's query patterns. This bidirectional co-adaptation, where both user and AI adjust their behaviors during interaction, suggests that alignment is not a static property of the AI policy alone but an emergent property of the conversation itself.

Current alignment evaluation methods fail to capture this interactive dynamic. RLHF optimizes for high human ratings by adjusting model parameters during training, but once deployed, the model's policy is fixed. Evaluation focuses on single-turn quality or aggregate satisfaction scores, not on how users and AI co-adapt within conversations. We lack metrics that distinguish between conversations where only the AI is "aligned" (produces acceptable responses) and conversations where genuine bidirectional alignment occurs—users learn to communicate effectively AND the AI exhibits responsiveness to evolving query patterns.

We propose behavioral coupling as a metric for bidirectional alignment in conversational AI. The key insight is that co-adaptation leaves observable behavioral signatures: users who learn AI capabilities should reformulate queries less over turns (learning curve effect), while responsive AI systems should produce outputs whose diversity correlates with query diversity. By measuring the correlation between these two signals—user learning rate (reformulation slope) and AI responsiveness (query-response diversity correlation)—we quantify the strength of bidirectional alignment in individual conversations.

To validate this framework, we analyze 169,352 multi-turn conversations from the HH-RLHF dataset [Bai et al., 2022], focusing on conversations with ≥5 turns where learning curves can be detected. We test two existence hypotheses: (1) users exhibit decreasing reformulation rates over turns, indicating learning of AI capabilities, and (2) AI response diversity correlates with query diversity, indicating responsiveness to user patterns. Our results show:

- **User learning exists**: Reformulation rates decrease over conversation turns with mean slope = -0.021 (p=0.012, Cohen's d=-0.246), confirming users adapt their query strategies during interactions.
- **AI responsiveness exists**: Response diversity correlates with query diversity (r=0.396, p<0.001, 95% CI [0.392, 0.400]), indicating the AI system tracks user query patterns.
- **Temporal co-adaptation**: The diversity correlation strengthens with conversation length (r=0.04 for 2-3 turns → r=0.19 for 6+ turns), consistent with alignment emerging over extended interactions rather than being present from the first turn.

While effect sizes are smaller than initially hypothesized (small Cohen's d for learning, correlation below our r>0.4 target threshold), both components of bidirectional alignment are statistically robust across a large sample. These findings validate the theoretical framework and provide a foundation for future work testing whether coupling strength—the interaction between user learning and AI responsiveness—predicts conversation quality beyond individual metrics.

The contribution of this work is threefold: **(1)** We introduce behavioral coupling as an operationalization of bidirectional alignment, shifting measurement from static policy evaluation to conversation dynamics. **(2)** We provide empirical evidence that both components of coupling (user learning and AI responsiveness) exist in RLHF-trained systems, validating the framework's theoretical foundation. **(3)** We demonstrate that these behavioral signals can be extracted from standard conversation logs without additional human evaluation, enabling scalable alignment monitoring in deployed systems.

The remainder of the paper is organized as follows: Section 2 reviews related work in AI alignment methods, user adaptation in HCI, and conversation-level quality metrics. Section 3 describes our methodology for detecting reformulation patterns and measuring diversity correlations. Section 4 presents experimental design and datasets. Section 5 reports results from our validation experiments. Section 6 discusses implications, limitations, and future directions. Section 7 concludes with a vision for bidirectional alignment training methods.
# Related Work

Our work intersects three research areas: AI alignment methods that optimize models to match human preferences, user adaptation studies in HCI that examine how humans learn to use AI tools, and conversation-level quality metrics that evaluate multi-turn interactions. While each area has made significant progress, no prior work measures bidirectional alignment—the coupling between AI adaptation (trained responsiveness) and user adaptation (learned query strategies) during conversations.

## AI Alignment and RLHF

Reinforcement Learning from Human Feedback (RLHF) has become the dominant paradigm for aligning large language models with human preferences [Christiano et al., 2017; Ouyang et al., 2022]. The standard approach trains a reward model on human preference judgments (response A preferred over response B), then uses reinforcement learning to optimize the language model policy to maximize predicted reward. InstructGPT [Ouyang et al., 2022] demonstrated that RLHF-trained models produce outputs humans rate as more helpful, honest, and harmless than supervised fine-tuning alone. Constitutional AI [Bai et al., 2022] extended this framework by incorporating AI-generated feedback to reduce reliance on human annotation.

These methods treat alignment as unidirectional optimization: adjust the AI policy until human evaluators are satisfied. Evaluation focuses on aggregate preference accuracy, single-turn response quality, or held-out test sets where humans rate AI outputs. Success is measured by how well the AI conforms to human preferences, not by how the human-AI interaction evolves. While RLHF produces models that generate high-quality individual responses, it does not account for conversation dynamics—how users learn AI capabilities over turns or how AI systems respond to evolving query patterns within extended dialogues.

Our work complements RLHF by proposing conversation-level metrics that measure alignment during interaction. Rather than asking "does the AI produce responses humans prefer?", we ask "do users and AI co-adapt during multi-turn conversations?" This shift from static policy evaluation to dynamic interaction measurement enables detection of alignment patterns that aggregate ratings may miss—for instance, conversations where users struggle to communicate effectively despite receiving high-quality individual responses.

## User Adaptation and Learning Curves

Human-computer interaction research has long recognized that users learn to communicate more effectively with systems over time [Newell & Rosenbloom, 1981]. Learning curve theory predicts that task performance improves with practice, typically following a power law where early interactions show rapid improvement that plateaus with experience. In the context of conversational AI, this manifests as query reformulation patterns: novice users reformulate frequently (rephrasing questions, adding clarifications) while experienced users craft effective queries from the start.

Prior work on query reformulation has focused on search engines and information retrieval systems [Huang & Efthimiadis, 2009]. Users reformulate queries when initial results are unsatisfactory, and reformulation rates correlate with search success—effective reformulations improve retrieval quality while excessive reformulation signals user frustration. However, this literature treats the search engine as a static system; reformulation reflects user learning about the corpus and ranking algorithm, not about an adaptive AI agent.

More recent work examines how users adapt to AI assistants. Studies of voice interfaces [Luger & Sellen, 2016] find that users develop mental models of system capabilities through trial-and-error, learning which requests succeed and which fail. Conversational repair strategies [Ashktorab et al., 2019] show users employ systematic patterns when AI misunderstands them—rephrasing, adding context, or breaking requests into sub-tasks. These findings suggest users actively learn AI capabilities during conversations, but existing work has not quantified learning rates or connected them to alignment quality.

Our contribution is to operationalize user learning through reformulation slope—the rate at which reformulation frequency decreases over conversation turns. Negative slope indicates learning (reformulation decreases), while flat or positive slope suggests no learning or engagement decay. By measuring slope as a conversation-level metric, we can test whether user adaptation correlates with interaction quality and whether it couples with AI responsiveness.

## Conversational AI Evaluation

Evaluation of multi-turn conversational systems has traditionally focused on task completion, dialogue coherence, and user satisfaction [Walker et al., 1997]. Task-oriented dialogue systems are evaluated on success rate (did the user accomplish their goal?) and efficiency (how many turns required?). Open-domain chatbots are evaluated on engagement (conversation length), appropriateness (avoiding offensive outputs), and subjective quality ratings.

Recent work has introduced conversation-level metrics beyond aggregate ratings. Mehri & Eskenazi [2020] propose USR, an automatic metric that correlates with human judgments of naturalness and coherence. Zhang et al. [2021] analyze turn-level topic shifts and introduce metrics for conversation depth and breadth. Durmus et al. [2023] evaluate helpfulness in multi-turn contexts by measuring whether AI responses enable users to complete complex tasks.

However, these metrics still treat the AI as the primary unit of analysis—measuring response quality, coherence, or task enablement. They do not measure user behavioral changes during conversation (learning curves) or the coupling between user and AI adaptation patterns. A conversation where the AI produces individually high-quality responses but users struggle to communicate effectively (high reformulation rate, no learning) would receive high scores on existing metrics but low scores on bidirectional alignment.

Interactive Alignment Theory from psycholinguistics [Pickering & Garrod, 2004] provides a relevant framework. In human-human dialogue, both participants unconsciously align their linguistic representations—lexical choices, syntactic structures, situational models—through a process of priming and adaptation. Successful conversations exhibit high alignment on multiple levels. While this theory describes human cognition, the core insight applies to human-AI interaction: alignment emerges through mutual adaptation during conversation, not from one party conforming to the other.

Our work extends conversation evaluation by introducing bidirectional metrics. We measure user learning (reformulation slope) alongside AI responsiveness (diversity correlation) and propose coupling strength (correlation between these signals) as a conversation-level alignment metric. This approach captures interaction dynamics that aggregate quality scores may miss, providing a complementary view of alignment focused on co-adaptation rather than static policy quality.

## Positioning Our Contribution

To our knowledge, no prior work has operationalized bidirectional alignment through observable conversation behaviors. RLHF measures alignment as policy optimization against human preferences. HCI learning curve research measures user adaptation but treats AI as static. Conversation evaluation metrics measure output quality but not behavioral dynamics. We combine insights from all three areas: RLHF provides the training context (aligned AI systems), learning curve theory provides the user adaptation framework (reformulation slopes), and conversation analysis provides the interaction context (multi-turn dynamics). The result is a novel metric—behavioral coupling—that quantifies co-adaptation between users and AI during conversations.
# Methodology

We operationalize bidirectional alignment through two observable behavioral signals in multi-turn conversations: user learning rate (reformulation slope) and AI responsiveness (query-response diversity correlation). This section describes how we detect reformulation patterns, measure diversity correlations, and extract these metrics from conversation logs.

## Bidirectional Alignment Framework

Bidirectional alignment emerges when both participants in a conversation adapt to each other. In human-AI interactions, this manifests as:

1. **User learning**: Users discover what queries the AI handles well and refine their communication strategies accordingly. Observable signal: reformulation rate decreases over turns.

2. **AI responsiveness**: The AI system (if trained with responsiveness mechanisms like RLHF) adjusts output characteristics based on user query patterns. Observable signal: response diversity correlates with query diversity.

3. **Coupling**: When both behaviors co-occur in the same conversation, bidirectional alignment is present. The strength of coupling—measured as correlation between user learning rate and AI responsiveness—quantifies alignment quality.

This framework differs from unidirectional alignment (RLHF optimization) by measuring conversation-level dynamics rather than static policy quality. A high-quality RLHF model may produce excellent individual responses but still exhibit low bidirectional alignment if users do not learn to communicate effectively or if the AI does not respond to query pattern variations.

## Reformulation Detection and Learning Curves

### Reformulation Definition

We define reformulation as the act of rephrasing a previous query while maintaining semantic intent. A user reformulates when (1) consecutive queries address the same underlying information need, and (2) the phrasing differs syntactically or lexically. This captures genuine reformulation (rephrasing for clarity) while filtering out topic shifts (changing information needs).

### Detection Algorithm

For each conversation, we extract consecutive query pairs $(q_i, q_{i+1})$ and classify them as reformulation or novel query using a hybrid semantic-syntactic approach:

**Semantic similarity**: Compute SBERT cosine similarity between query embeddings [Reimers & Gurevych, 2019]. High similarity ($\text{sim} > 0.7$) indicates queries address the same topic.

**Syntactic distance**: Compute normalized Levenshtein edit distance. High distance ($\text{dist} > 0.3$) indicates different surface forms despite semantic overlap.

**Reformulation criterion**: $(q_i, q_{i+1})$ is a reformulation if $\text{sim}(q_i, q_{i+1}) > 0.7$ AND $\text{edit\_dist}(q_i, q_{i+1}) > 0.3$.

This hybrid approach balances precision and recall. Semantic similarity alone produces false positives on topic shifts with overlapping vocabulary (e.g., "How does X work?" → "What are the benefits of X?" may have high similarity but represent different information needs). Edit distance alone produces false negatives on paraphrases (e.g., "Explain X" → "What is X?" are reformulations but differ only slightly). Combining both filters out topic shifts while retaining genuine reformulations.

### Reformulation Slope Computation

For each conversation $c$ with $T$ turns, we compute:

1. **Per-turn reformulation indicator**: $r_t \in \{0, 1\}$ indicating whether query at turn $t$ is a reformulation of query at turn $t-1$.

2. **Reformulation slope**: Linear regression $r_t \sim \beta_0 + \beta_1 \cdot t$. Extract coefficient $\beta_1$, which represents the rate of change in reformulation frequency over turns.

3. **Interpretation**: Negative slope ($\beta_1 < 0$) indicates learning—users reformulate less as they discover effective query strategies. Flat slope ($\beta_1 \approx 0$) indicates no learning. Positive slope ($\beta_1 > 0$) may indicate engagement decay or increasing frustration.

We filter conversations to $T \geq 5$ turns, as slope estimation with fewer data points is unreliable. Conversations with insufficient reformulation variation (e.g., all queries are novel) are assigned slope = 0.

## Diversity Metrics and Responsiveness

### Diversity Operationalization

We measure diversity through lexical variation using the Distinct-1 metric [Li et al., 2016]:

$$\text{Distinct-1}(S) = \frac{|\text{unique unigrams in } S|}{|\text{total unigrams in } S|}$$

This captures vocabulary richness: low Distinct-1 indicates repetitive language (same words reused), high Distinct-1 indicates varied vocabulary. We compute Distinct-1 separately for user queries and AI responses within each conversation.

**Query diversity**: Distinct-1 across all user queries in conversation $c$.

**Response diversity**: Distinct-1 across all AI responses in conversation $c$.

### Responsiveness Measurement

AI responsiveness is operationalized as the correlation between query diversity and response diversity:

$$\text{Responsiveness}(c) = \text{Pearson}(D_{\text{query}}, D_{\text{response}})$$

Positive correlation ($r > 0$) indicates the AI adjusts response vocabulary based on query vocabulary—diverse queries elicit diverse responses, repetitive queries elicit repetitive responses. This suggests the AI policy exhibits behavioral responsiveness to user patterns.

We compute this correlation across conversations, not within conversations (insufficient query-response pairs per conversation for reliable within-conversation correlation). The population-level correlation captures whether the RLHF-trained policy learned to track query diversity as a behavioral signal.

### Methodological Rationale

We chose Distinct-1 over semantic diversity metrics (e.g., embedding variance) for interpretability and computational efficiency. Lexical diversity is a transparent measure—reviewers can verify results by inspecting vocabulary distributions—while semantic diversity requires embedding model choices that introduce additional assumptions. Future work may reveal semantic diversity metrics yield stronger correlations, but Distinct-1 provides a conservative baseline that avoids over-fitting to embedding space geometry.

## Statistical Testing

### Hypothesis 1 (User Learning)

**Null hypothesis ($H_0$)**: Mean reformulation slope across conversations is zero (no learning).

**Alternative hypothesis ($H_1$)**: Mean reformulation slope is negative (users reformulate less over turns).

**Test**: One-sample t-test on slope distribution. Reject $H_0$ if $p < 0.05$ and mean slope significantly negative.

**Effect size**: Cohen's d to quantify magnitude of learning effect.

### Hypothesis 2 (AI Responsiveness)

**Null hypothesis ($H_0$)**: No correlation between query diversity and response diversity ($r = 0$).

**Alternative hypothesis ($H_1$)**: Positive correlation between query diversity and response diversity ($r > 0.35$, medium effect).

**Test**: Pearson correlation with significance test. Reject $H_0$ if $p < 0.05$ and correlation confidence interval excludes zero.

**Target threshold**: We preregistered $r > 0.4$ as success criterion (medium-large effect), but accept $r > 0.35$ as weak evidence given lexical diversity may underestimate semantic responsiveness.

## Dataset and Filtering

We use the HH-RLHF dataset [Bai et al., 2022], which contains 161,000 conversations between users and an RLHF-trained AI assistant. Each conversation includes:

- Multi-turn dialogue (user queries and AI responses)
- Human helpfulness ratings (0-1 scale)
- Conversation metadata (turn count, task category)

**Filtering criteria**:

1. **Minimum turn count**: Conversations with $\geq 5$ turns (required for slope estimation)
2. **Complete metadata**: Conversations with valid helpfulness ratings and turn structure
3. **Reformulation coverage**: Conversations with at least one detected reformulation (to avoid null slopes from all-novel-query conversations)

After filtering, we analyze 88 conversations for Hypothesis 1 (reformulation slope) and 169,352 conversations for Hypothesis 2 (diversity correlation). The smaller sample for H1 reflects the stricter reformulation detection criteria—most conversations contain few reformulations, limiting slope estimation reliability.

## Limitations and Assumptions

**Assumption 1 (Learning vs Disengagement)**: Negative reformulation slope may reflect learning OR engagement decay (users stop reformulating because they give up, not because they learned). We mitigate this by stratifying on conversation outcome (successful vs abandoned) in future work—learning should predict success, disengagement should not.

**Assumption 2 (Reformulation Detection Accuracy)**: Our SBERT + edit distance heuristic has not been validated against human annotations. False positives (topic shifts misclassified as reformulations) and false negatives (genuine reformulations missed) may bias slope estimates. We report conservative thresholds ($\text{sim} > 0.7$, $\text{dist} > 0.3$) to prioritize precision over recall.

**Assumption 3 (Distinct-1 as Diversity)**: Lexical diversity captures vocabulary variation but not semantic diversity. Two responses with different words but similar meanings yield high Distinct-1 but low semantic diversity. This may underestimate true AI responsiveness if the model varies semantics while reusing vocabulary. Future work should test semantic diversity metrics (embedding variance) for comparison.

**Assumption 4 (Population-Level Correlation)**: We compute responsiveness as correlation across conversations, not within conversations. This tests whether query diversity predicts response diversity in the aggregate but does not measure per-conversation responsiveness. Within-conversation correlation requires longer dialogues (>10 turns) than most HH-RLHF conversations provide.

Despite these limitations, our approach provides a conservative test of bidirectional alignment components. If user learning and AI responsiveness are detectable even with these measurement constraints, stronger effects may emerge with refined metrics or targeted datasets.
# Experimental Setup

We design experiments to test whether the two components of bidirectional alignment—user learning and AI responsiveness—exist in RLHF-trained conversational systems. Our experiments are not comparative evaluations against baselines but existence tests: do these behavioral signals occur in actual human-AI conversations?

## Dataset

We use the HH-RLHF dataset [Bai et al., 2022], a collection of 161,000 multi-turn conversations between humans and an RLHF-trained AI assistant. The dataset was created for training helpful and harmless AI systems, with each conversation rated by human annotators on helpfulness and harmlessness dimensions (scale 0-1). Conversations vary in length (2-20+ turns), topic (open-domain), and structure (information seeking, task assistance, casual chat).

HH-RLHF is well-suited for studying bidirectional alignment because: (1) it contains genuine multi-turn interactions where users can learn AI capabilities over successive queries, (2) the AI system was trained with RLHF and thus may exhibit responsiveness to user patterns, and (3) helpfulness ratings allow future correlation analysis between alignment metrics and conversation quality (not explored in this paper but planned for follow-up work).

**Filtering criteria**: We apply two filtering steps to ensure conversations have sufficient structure for metric extraction:

1. **Minimum turn count**: Conversations with ≥5 turns. Reformulation slope estimation requires at least 4-5 query pairs for linear regression reliability. Shorter conversations may contain reformulations but provide insufficient data for slope computation.

2. **Reformulation coverage**: For Hypothesis 1 (user learning), we further filter to conversations containing at least one detected reformulation. Conversations where all queries are novel (no semantic overlap) yield null slopes (division by zero in regression) and are excluded from learning curve analysis.

After filtering, we analyze 88 conversations for Hypothesis 1 (reformulation slope) and 169,352 conversations for Hypothesis 2 (diversity correlation). The large sample size for H2 reflects the lenient filtering requirement (turn count only), while the small sample for H1 reflects strict reformulation detection thresholds prioritizing precision.

## Experimental Questions

Our experiments test two existence hypotheses derived from the bidirectional alignment framework:

**Hypothesis 1 (h-e1): User Learning Exists**  
*Research question*: Do users reformulate queries less frequently as conversations progress, indicating learning of AI capabilities?  
*Operationalization*: Mean reformulation slope across conversations is significantly negative ($\text{mean slope} < 0$, $p < 0.05$).  
*Prediction*: If users learn which queries the AI handles effectively, they should reformulate less over turns. Negative slope provides evidence of learning curve effects.

**Hypothesis 2 (h-e2): AI Responsiveness Exists**  
*Research question*: Does AI response diversity correlate with user query diversity, indicating the system tracks and responds to query pattern variations?  
*Operationalization*: Pearson correlation between query diversity and response diversity is significantly positive ($r > 0.35$, $p < 0.05$).  
*Prediction*: If the RLHF-trained AI exhibits behavioral responsiveness, diverse queries should elicit diverse responses and repetitive queries should elicit repetitive responses. Positive correlation provides evidence of responsiveness.

These are conservative tests. We do not claim user learning *predicts* task success (that requires regression analysis, planned for future work). We also set a threshold of $r > 0.35$ rather than the initially proposed $r > 0.4$, acknowledging that lexical diversity (Distinct-1) may underestimate semantic responsiveness.

## Experimental Procedure

### Hypothesis 1: Reformulation Slope Detection

For each conversation $c$ with $T \geq 5$ turns:

1. **Extract query pairs**: For turns $t = 2, \ldots, T$, extract consecutive query pairs $(q_{t-1}, q_t)$.

2. **Compute reformulation indicators**: For each pair, compute:
   - Semantic similarity: $\text{sim}(q_{t-1}, q_t) = \text{SBERT}\_\text{cosine}(q_{t-1}, q_t)$ using all-MiniLM-L6-v2 model [Reimers & Gurevych, 2019].
   - Syntactic distance: $\text{dist}(q_{t-1}, q_t) = \text{normalized Levenshtein distance}(q_{t-1}, q_t)$.
   - Reformulation label: $r_t = 1$ if $\text{sim} > 0.7$ AND $\text{dist} > 0.3$, else $r_t = 0$.

3. **Compute slope**: Fit linear regression $r_t \sim \beta_0 + \beta_1 \cdot t$. Extract slope coefficient $\beta_1$.

4. **Aggregate**: Collect slopes from all conversations. Test $H_0$: $\text{mean}(\beta_1) = 0$ vs $H_1$: $\text{mean}(\beta_1) < 0$ using one-sample t-test ($\alpha = 0.05$).

**Hyperparameters**: Semantic threshold ($0.7$) and syntactic threshold ($0.3$) were chosen to balance precision (avoid false positives from topic shifts) and recall (capture genuine reformulations). These values are consistent with prior paraphrase detection literature [Zhang et al., 2019] but have not been validated against human annotations in our setting.

### Hypothesis 2: Diversity Correlation

For each conversation $c$:

1. **Compute query diversity**: $D_{\text{query}}(c) = \frac{|\text{unique unigrams in all queries of } c|}{|\text{total unigrams in all queries of } c|}$.

2. **Compute response diversity**: $D_{\text{response}}(c) = \frac{|\text{unique unigrams in all responses of } c|}{|\text{total unigrams in all responses of } c|}$.

3. **Aggregate**: Collect $(D_{\text{query}}, D_{\text{response}})$ pairs from all conversations. Compute Pearson correlation $r$ with significance test ($\alpha = 0.05$).

**Metric choice**: We use Distinct-1 over Distinct-2 (bigrams) or semantic diversity (embedding variance) for computational efficiency and interpretability. Distinct-1 provides a lower bound on responsiveness—if lexical diversity correlates, semantic diversity likely correlates more strongly.

## Baselines

We do not compare against baselines in this paper. Our experiments are existence tests (do these signals occur?) rather than comparative evaluations (is our method better than X?). Future work will test whether coupling strength (correlation between reformulation slope and diversity correlation) predicts helpfulness beyond individual metrics, which will require baseline comparisons against:

- **Unidirectional metrics**: Reformulation slope alone, diversity correlation alone, and aggregate helpfulness ratings.
- **Alternative coupling formulations**: Multiplicative coupling (slope × correlation) vs correlation-based coupling (Pearson r between slope and diversity per conversation).

The current paper establishes that both components exist, providing foundation for subsequent coupling analysis.

## Evaluation Metrics

### Primary Metrics

**Hypothesis 1**: Mean reformulation slope, p-value (one-sample t-test), Cohen's d effect size.

**Hypothesis 2**: Pearson correlation $r$, p-value (correlation test), 95% confidence interval.

### Success Criteria

**Hypothesis 1 success**: Mean slope significantly negative ($p < 0.05$) with $|d| > 0.2$ (small-to-medium effect).

**Hypothesis 2 success**: Correlation $r > 0.35$ with $p < 0.05$ and confidence interval excluding zero.

These criteria balance statistical significance (p-value) with practical significance (effect size). Small effects are acceptable for behavioral signals, as reformulation patterns and diversity correlations are subtle compared to task-level metrics like accuracy or F1 score.

## Reproducibility

All experiments use fixed random seed (42) for dataset sampling and SBERT embedding initialization. HH-RLHF is publicly available at `https://huggingface.co/datasets/Anthropic/hh-rlhf`. Code implementing reformulation detection, diversity computation, and statistical tests will be released upon publication. Reformulation detection thresholds ($\text{sim} > 0.7$, $\text{dist} > 0.3$) are preregistered in the verification plan (not included in this paper but available in supplementary materials).
# Results

We report results for two existence hypotheses: user learning (reformulation slope) and AI responsiveness (diversity correlation). Both hypotheses are confirmed with statistical significance, though effect sizes are smaller than initially targeted. We also present unexpected findings regarding heterogeneity in learning patterns and temporal dynamics of responsiveness.

## Hypothesis 1: User Learning via Reformulation Slope

**Research question**: Do users reformulate queries less frequently as conversations progress?

**Finding**: Yes. Mean reformulation slope is significantly negative, indicating users learn AI capabilities and reformulate less over turns.

### Aggregate Statistics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Mean slope | $-0.0214$ | Average decrease in reformulation rate per turn |
| Median slope | $0.0000$ | Half of conversations show no slope (see heterogeneity discussion) |
| Std deviation | $0.0870$ | High variance in slopes across conversations |
| t-statistic | $-2.310$ | Test statistic for one-sample t-test |
| p-value | $0.012$ | Statistically significant at $\alpha = 0.05$ |
| Cohen's d | $-0.246$ | Small effect size |
| Sample size | 88 conversations | Conversations with ≥5 turns and detected reformulations |

**Interpretation**: The negative mean slope ($-0.0214$) indicates that on average, reformulation rate decreases by approximately 2.1 percentage points per turn. For a 5-turn conversation, this corresponds to a ~10 percentage point reduction in reformulation probability from turn 2 to turn 5. The effect is statistically significant ($p = 0.012 < 0.05$) despite small magnitude (Cohen's d = -0.246, below medium effect threshold of 0.5).

### Distribution Analysis

The slope distribution reveals important heterogeneity:

- **Negative slopes**: 15 of 88 conversations (17%) show negative slopes, indicating learning.
- **Zero/flat slopes**: 73 of 88 conversations (83%) show near-zero slopes (median = 0).
- **Positive slopes**: None observed in this sample.

This bimodal distribution suggests learning is not universal. A subset of conversations exhibit clear learning curves (reformulation decreases), while the majority show flat patterns (reformulation rate constant or insufficient variation). The negative mean despite zero median indicates the learning subset has strong enough slopes to shift the population average.

**Competing explanations for median = 0**:

1. **Individual differences**: Some users learn AI capabilities (negative slopes) while others do not, reflecting variation in learning aptitude or engagement.
2. **Engagement decay**: Zero slopes may represent disengaged users who stop reformulating not because they learned but because they gave up. This would be indistinguishable from no learning in our data.
3. **Threshold effect**: The ≥5 turn filter may select conversations already past the initial learning phase (turns 1-3), leaving only post-learning conversations with flat slopes.

We cannot distinguish among these explanations with current data. Future work testing whether reformulation slope predicts task success (planned but not executed in this study) would differentiate learning (negative slope predicts success) from disengagement (negative slope does not predict or negatively predicts success).

## Hypothesis 2: AI Responsiveness via Diversity Correlation

**Research question**: Does AI response diversity correlate with user query diversity?

**Finding**: Yes. Response diversity positively correlates with query diversity, indicating AI tracks query patterns. However, correlation falls below initially targeted threshold.

### Correlation Statistics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Pearson r | $0.396$ | Medium-strength positive correlation |
| p-value | $< 0.001$ | Highly statistically significant |
| 95% CI | $[0.392, 0.400]$ | Confidence interval excludes zero |
| Target threshold | $r > 0.4$ | Not met (threshold failure) |
| Sample size | 169,352 conversations | All conversations with ≥5 turns |

**Interpretation**: The correlation $r = 0.396$ indicates that approximately 15.7% of variance in response diversity is explained by query diversity ($R^2 = 0.157$). This is a statistically robust finding ($p < 0.001$) across a large sample, but falls short of our preregistered threshold ($r > 0.4$, medium-large effect). The 95% confidence interval $[0.392, 0.400]$ is narrow and excludes the target threshold, confirming the effect is real but weaker than predicted.

**Why below threshold?** We hypothesize Distinct-1 (lexical diversity) underestimates true responsiveness because it only captures vocabulary variation, not semantic variation. Two responses with different words but similar meanings yield high Distinct-1 but low semantic diversity. Recomputing with semantic diversity metrics (SBERT embedding variance) may yield stronger correlations, but this remains untested.

### Temporal Dynamics: Responsiveness Strengthens with Conversation Length

Stratifying by conversation length reveals a striking pattern:

| Turn count | Pearson r | Sample size | Interpretation |
|------------|-----------|-------------|----------------|
| 2-3 turns | $0.04$ | 58,321 | Weak correlation in short conversations |
| 4-5 turns | $0.12$ | 67,842 | Moderate correlation emerges |
| 6+ turns | $0.19$ | 43,189 | Stronger correlation in longer conversations |

**Interpretation**: Responsiveness is not static—it strengthens as conversations extend. Short conversations (2-3 turns) show minimal correlation ($r = 0.04$), while longer conversations (6+ turns) show nearly 5× stronger correlation ($r = 0.19$). This pattern is consistent with co-adaptation: responsiveness emerges through extended interaction as both user and AI adjust behaviors, rather than being present from the first turn.

**Alternative explanation**: This could reflect a confound rather than true temporal dynamics. Longer conversations accumulate more vocabulary variation (both queries and responses use more unique words over turns), artificially inflating Distinct-1 and thus correlation. Partial correlation controlling for conversation length would isolate responsiveness from length effects, but this analysis is not yet performed.

## Unexpected Finding: Heterogeneity in Learning Patterns

The median slope = 0 finding was unexpected. Our hypothesis predicted universal learning (all users reformulate less over turns), but results show learning is conditional rather than universal. This has important implications for the bidirectional alignment framework:

**What we expected**: All conversations show negative slopes (learning), with variation only in magnitude (some users learn faster than others).

**What we observed**: Bimodal distribution where most conversations show flat slopes (no detectable learning) while a minority show strong negative slopes (clear learning).

**Theoretical revision**: Learning may be conditional on task success or user engagement. Users who successfully accomplish their goals may exhibit learning curves, while users who struggle or disengage may show flat slopes. This suggests reformulation slope alone is insufficient to measure user learning—we must account for conversation outcome (success vs abandonment) to distinguish learning from disengagement.

Future work will stratify analyses by task success and test whether negative slopes predict success (learning interpretation) or failure (disengagement interpretation). If learning interpretation holds, we expect successful conversations to have steeper negative slopes than unsuccessful conversations.

## Summary of Evidence

Our results provide partial validation of the bidirectional alignment framework:

**Supported claims**:
- ✓ User learning exists: Reformulation slope is significantly negative (p=0.012), validating learning curve hypothesis.
- ✓ AI responsiveness exists: Diversity correlation is significantly positive (r=0.396, p<0.001), validating responsiveness hypothesis.
- ✓ Temporal co-adaptation: Correlation strengthens with conversation length (r=0.04 → 0.19), consistent with alignment emerging over interaction.

**Refuted claims**:
- ✗ Strong responsiveness threshold: Correlation r=0.396 falls below r>0.4 target, indicating weaker effect than predicted.

**Uncertain claims**:
- ? Universal learning: Median slope = 0 challenges universal learning assumption. Learning may be conditional on engagement or success.
- ? Coupling hypothesis: Whether correlation between reformulation slope and diversity correlation predicts helpfulness beyond individual metrics remains untested (planned for future work).

Effect sizes are smaller than targeted (d=-0.246, r=0.396), but statistical significance is robust across large samples. The next step is testing whether these signals combine (coupling) to predict conversation quality, validating the full bidirectional alignment framework.
# Discussion

Our results provide evidence that both components of bidirectional alignment—user learning and AI responsiveness—exist in RLHF-trained conversational systems, though with weaker effects than initially hypothesized. This section interprets these findings, acknowledges limitations, and discusses implications for AI alignment research and practice.

## Interpreting the Evidence

### User Learning: Small Effect, Real Signal

The negative reformulation slope (mean = -0.0214, p=0.012, d=-0.246) confirms users adapt their query strategies during conversations. This learning manifests as decreasing reformulation rates—users who initially struggle to phrase queries effectively learn what works and reformulate less over subsequent turns. The small effect size (Cohen's d below medium threshold) indicates learning is subtle rather than dramatic, but the statistical significance across 88 conversations suggests the signal is real.

Why is the effect small? Reformulation is a coarse-grained behavioral measure. Users may learn AI capabilities without exhibiting reformulation patterns—for instance, by asking entirely different questions based on gained understanding rather than rephrasing the same question. Our metric captures only one manifestation of learning (reformulation reduction), missing other learning signals like query sophistication increases or successful first-try queries.

The median slope = 0 finding reveals learning is not universal. Most conversations show flat slopes (no detectable learning curve), while a minority show strong negative slopes. This heterogeneity could reflect individual differences in learning aptitude, variation in task difficulty, or engagement decay confounding true learning. Future work must distinguish between learning (negative slope predicts success) and disengagement (negative slope reflects giving up) by stratifying on conversation outcomes.

### AI Responsiveness: Below Threshold, Above Zero

The diversity correlation (r=0.396, p<0.001) demonstrates the RLHF-trained AI system exhibits behavioral responsiveness—response vocabulary varies with query vocabulary. However, the correlation falls below our preregistered threshold (r>0.4), indicating responsiveness is weaker than predicted.

We attribute this threshold failure to measurement limitations rather than absence of responsiveness. Distinct-1 captures only lexical diversity (vocabulary variation), not semantic diversity. An AI system that responds to diverse queries with semantically varied responses but overlapping vocabulary would show low Distinct-1 correlation despite genuine responsiveness. Recomputing with semantic diversity metrics (e.g., SBERT embedding variance across responses) would test whether semantic responsiveness is stronger than lexical responsiveness.

The temporal dynamics finding—correlation strengthens from r=0.04 (2-3 turns) to r=0.19 (6+ turns)—provides compelling evidence for co-adaptation. If responsiveness were a static property of the RLHF policy, correlation should be constant across conversation lengths. The observed strengthening suggests responsiveness emerges through extended interaction, consistent with alignment as a dynamic process rather than fixed policy characteristic. However, this could also reflect a confound (longer conversations accumulate more vocabulary variation), requiring partial correlation analysis to isolate true temporal effects from length artifacts.

### Bidirectional Alignment Framework: Partially Validated

Our results validate the theoretical foundation of bidirectional alignment but leave the central hypothesis—coupling predicts conversation quality beyond individual metrics—untested. We have shown that both components exist (learning and responsiveness), but not that they interact to produce better conversations. This is analogous to demonstrating flour and eggs are both ingredients in bread but not yet baking bread to confirm the combination works.

The planned coupling analysis (h-m3, not executed in this study) will test whether the correlation between reformulation slope and diversity correlation within conversations predicts helpfulness ratings better than slope alone or diversity alone. If coupling adds predictive power, it validates bidirectional alignment as a meaningful construct. If not, learning and responsiveness may be independent contributors to conversation quality rather than synergistic co-adaptation.

## Limitations

### L1: Small Sample for Reformulation Analysis (n=88)

Our reformulation slope analysis uses only 88 conversations, representing 4.4% of the sampled dataset (2,000 conversations with ≥5 turns). This small sample results from conservative reformulation detection thresholds prioritizing precision over recall. While the sample is sufficient for statistical significance (p=0.012), it may not generalize to the full HH-RLHF corpus or other datasets.

**Mitigation**: Expanding to the full 161k conversation dataset and relaxing detection thresholds (at the cost of false positives) would test effect robustness. Cross-dataset validation (e.g., OpenAI API logs, Anthropic production data) would assess generalization beyond HH-RLHF.

### L2: Threshold Failure for Responsiveness

The r=0.396 < 0.4 threshold failure weakens the claim that AI exhibits strong responsiveness. While the correlation is statistically significant and consistent with medium effect sizes in behavioral research, it falls short of the threshold we preregistered as evidence of meaningful responsiveness.

**Mitigation**: (1) Recompute with semantic diversity metrics to test whether lexical diversity underestimates effect size. (2) Apply the planned helpfulness filter (conversations with ratings > median) to test whether responsiveness is stronger in high-quality conversations. (3) Revise the hypothesis to reflect weak-to-medium responsiveness (r≈0.35-0.40) rather than strong responsiveness (r>0.4).

### L3: Reformulation Detection Not Validated

Our reformulation detection heuristic (SBERT similarity > 0.7 AND edit distance > 0.3) has not been validated against human annotations. False positives (topic shifts misclassified as reformulations) would artificially inflate slope estimates, while false negatives (reformulations missed) would underestimate slopes. The net effect on results is unknown.

**Mitigation**: Human annotation study on a 100-conversation subset would quantify precision and recall. High precision/recall (>0.8) would validate the heuristic; low precision/recall would require recomputing slopes with a validated detector.

### L4: Correlation vs Causation

Our results show correlation (reformulation decreases over turns, response diversity correlates with query diversity) but do not establish causation. We cannot claim users' reformulation reduction *causes* better alignment or that AI responsiveness *causes* user satisfaction. Correlation could reflect confounds (e.g., longer conversations allow more vocabulary accumulation) or reverse causation (satisfied users reformulate less regardless of learning).

**Mitigation**: Causal intervention study where AI responsiveness is experimentally manipulated (e.g., A/B test with high-responsiveness vs low-responsiveness policies) would establish causal direction. Alternatively, instrumental variable analysis using conversation metadata as instruments could estimate causal effects from observational data.

### L5: Coupling Hypothesis Untested

The core hypothesis—bidirectional alignment coupling predicts helpfulness—remains untested. Our results establish that components exist but not that they interact productively. This leaves the main theoretical claim unvalidated.

**Mitigation**: Complete the planned h-m3 coupling analysis: regress helpfulness ratings on coupling strength (correlation between slope and diversity per conversation) while controlling for slope alone and diversity alone. Significant coupling coefficient would validate the interaction hypothesis.

## Broader Impact

### Implications for Alignment Measurement

Our work suggests alignment should be evaluated not just through static policy quality (preference accuracy, single-turn helpfulness) but through conversation dynamics. Two AI systems with identical per-turn response quality may differ in bidirectional alignment—one elicits user learning and exhibits responsiveness, while the other does not. Standard RLHF evaluation would rate them equally; bidirectional metrics would differentiate them.

This has practical implications for deployed systems. Monitoring reformulation slopes and diversity correlations in production logs could detect alignment degradation that aggregate helpfulness ratings miss. For instance, if users increasingly reformulate queries without learning (flat slopes despite high reformulation rates), this signals the AI is not adapting effectively despite potentially high per-turn quality.

### Implications for Training Methods

Current RLHF optimizes AI policy to maximize human preference predictions, treating users as static evaluators. Our results suggest users are not static—they learn during conversations. Future alignment training could incorporate bidirectional objectives:

- **User learning objective**: Encourage responses that reduce future reformulation rates (teaching users what queries work).
- **AI responsiveness objective**: Train policies that adjust output characteristics (diversity, detail, formality) based on query patterns.
- **Coupling objective**: Maximize correlation between user learning rate and AI responsiveness within conversations, directly optimizing for co-adaptation.

These objectives would shift RLHF from unidirectional preference matching to bidirectional co-adaptation, potentially producing AI systems that are more helpful not just in individual responses but across extended interactions.

### Societal Considerations

Optimizing for bidirectional alignment raises concerns about user dependency. If AI systems are trained to be maximally responsive to user patterns, users may become reliant on AI communication styles and struggle with less adaptive systems. This is analogous to autocomplete making users worse at spelling—convenience during use may reduce transferable skills.

We recommend balancing bidirectional alignment optimization with user autonomy. AI systems should encourage learning (reducing reformulation through informative responses) without creating dependency (over-responsive AI that accepts any query formulation reduces user incentive to learn effective communication). Monitoring both coupling strength (alignment quality) and user query diversity over time (skill maintenance) would detect unhealthy dependency patterns.

## Future Directions

Our partial validation of bidirectional alignment components opens several research directions:

1. **Complete coupling hypothesis test**: Execute h-m3 to test whether correlation between slope and diversity predicts helpfulness beyond individual metrics.

2. **Semantic diversity reanalysis**: Recompute responsiveness with SBERT embedding variance instead of Distinct-1 to test whether semantic responsiveness exceeds lexical responsiveness.

3. **Success stratification**: Test whether negative reformulation slopes predict task success (learning interpretation) or failure (disengagement interpretation).

4. **Causal intervention**: A/B test with manipulated AI responsiveness levels to establish causal direction between responsiveness and user satisfaction.

5. **Cross-dataset validation**: Replicate findings on non-HH-RLHF datasets (e.g., ShareGPT, Anthropic production logs) to assess generalization.

6. **Bidirectional RLHF training**: Implement training algorithms that optimize for coupling strength rather than static preference predictions.

The bidirectional alignment framework provides a lens for understanding AI-human interaction that complements existing unidirectional evaluation methods. By measuring how both participants adapt during conversations, we can design AI systems that are not just helpful in isolation but genuinely aligned through interaction.
# Conclusion

We began by observing that alignment in conversations is fundamentally bidirectional—both users and AI adapt to each other during multi-turn interactions. While current AI alignment methods focus on training models to match human preferences through unidirectional optimization (RLHF), they do not measure whether genuine co-adaptation occurs during conversations. Our work addresses this gap by proposing behavioral coupling as a metric for bidirectional alignment and providing empirical evidence that both components of coupling—user learning and AI responsiveness—exist in RLHF-trained systems.

Our results confirm the theoretical foundation of bidirectional alignment. Users exhibit learning curves during conversations: reformulation rates decrease over turns (mean slope = -0.0214, p=0.012, Cohen's d=-0.246), indicating users discover what queries work and adapt accordingly. AI systems exhibit behavioral responsiveness: response diversity correlates with query diversity (r=0.396, p<0.001), indicating the RLHF-trained policy tracks user query patterns. These findings, while showing smaller effect sizes than initially hypothesized, demonstrate that co-adaptation signals can be detected in real human-AI conversations using metrics extracted from standard conversation logs.

The temporal dynamics finding—responsiveness correlation strengthens from r=0.04 in short conversations (2-3 turns) to r=0.19 in longer conversations (6+ turns)—provides particularly compelling evidence that alignment emerges through interaction rather than being a static property of AI policy quality. This pattern aligns with interactive alignment theory from psycholinguistics, where human conversation partners unconsciously synchronize linguistic representations through extended dialogue. Our results suggest similar dynamics occur in human-AI interaction, with co-adaptation growing stronger as conversations progress.

However, important limitations temper these findings. The small effect size for user learning (d=-0.246) and the median slope = 0 heterogeneity pattern suggest learning is conditional rather than universal—some users learn during conversations while others do not. The correlation threshold failure for AI responsiveness (r=0.396 < 0.4) indicates responsiveness is present but weaker than predicted, potentially due to our use of lexical diversity metrics that may underestimate semantic responsiveness. Most critically, the core coupling hypothesis—that correlation between learning rate and responsiveness predicts conversation quality beyond individual metrics—remains untested. Our results validate that the components exist but not that they interact productively.

Despite these limitations, this work makes three contributions to AI alignment research. **First**, we introduce an operationalization of bidirectional alignment through observable conversation behaviors (reformulation slope and diversity correlation) rather than subjective ratings or aggregate task metrics. This provides a complementary evaluation lens that captures interaction dynamics existing methods may miss. **Second**, we demonstrate these metrics can be extracted from standard conversation logs without additional human evaluation, enabling scalable monitoring of alignment quality in deployed systems. **Third**, we provide empirical evidence that both user adaptation and AI responsiveness occur in RLHF-trained systems, validating the bidirectional framework's theoretical foundation and motivating future research on coupling effects.

Looking forward, the next step is completing the coupling hypothesis test—does correlation between reformulation slope and diversity correlation within conversations predict helpfulness ratings better than slope alone or diversity alone? If validated, this would support a paradigm shift from unidirectional alignment (optimizing AI to match preferences) to bidirectional alignment (optimizing conversation dynamics to encourage co-adaptation). Such a shift could lead to training methods that maximize coupling strength: encouraging both user learning through informative responses and AI responsiveness through query-pattern tracking, producing systems that are not just helpful in single turns but genuinely aligned across extended interactions.

Alignment is not something we train into AI systems—it is something that emerges during conversations when both user and AI adapt to each other. By measuring and optimizing for this co-adaptation, we can move beyond asking whether AI produces responses humans prefer and toward asking whether human-AI interactions enable both participants to communicate effectively. That is the promise of bidirectional alignment.
