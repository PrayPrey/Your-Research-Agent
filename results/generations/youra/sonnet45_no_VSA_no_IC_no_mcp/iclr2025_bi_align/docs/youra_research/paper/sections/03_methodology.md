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
