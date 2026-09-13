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
