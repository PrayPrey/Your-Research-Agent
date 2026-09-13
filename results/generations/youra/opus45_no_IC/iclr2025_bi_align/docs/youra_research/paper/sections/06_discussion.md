# Discussion

## The Goldilocks Zone of Accommodation

Our key finding—that moderate accommodation predicts highest engagement—challenges linear extrapolations from Communication Accommodation Theory. CAT research in human-human contexts typically finds positive, monotonic relationships between convergence and rapport. Why might this differ in human-AI interaction?

We propose the **accommodation-artificiality tradeoff**: while some accommodation signals attentiveness, excessive accommodation may activate uncanny valley responses. Users may perceive an AI that mirrors their style too closely as artificial or "trying too hard." This interpretation aligns with Ciechanowski et al.'s findings on chatbot uncanny valley effects.

The tercile pattern supports this: T1 (high accommodation) underperforms T2 (moderate), suggesting a threshold beyond which accommodation becomes counterproductive. T3 (low accommodation) performs worst, confirming that some accommodation is better than none.

## Asymmetric Bidirectional Effects

AI-to-human accommodation (r=0.152) vastly exceeds human-to-AI accommodation (r=0.013)—an 11× difference. This asymmetry has theoretical and practical implications.

**Theoretical**: CAT assumes symmetric agency and motivation. In human-AI dialogue, the AI accommodates through training signals rather than social motivation; humans may not perceive a need to reciprocate with a non-human. This fundamentally alters the accommodation dynamic.

**Practical**: Designers cannot rely on natural user accommodation to improve interactions. If engagement benefits come from accommodation, the burden falls on AI systems, not users.

## Limitations

**Correlational, not causal**: We observe association between accommodation and continuation, but cannot establish causation. Users who continue conversations may differ systematically from those who don't, with accommodation as a marker rather than driver.

**Single dataset**: Our analysis uses Anthropic hh-rlhf only. While large (111K+ conversations), this represents one platform and model family. Generalization to other systems (GPT, Llama, etc.) and platforms requires replication.

**Engagement proxy**: Conversation continuation is an imperfect engagement measure. Users may continue due to dissatisfaction (needing clarification) rather than positive engagement. We lack direct satisfaction labels.

**Formality as accommodation**: Formality is one dimension of linguistic style. Users may accommodate on other dimensions (vocabulary, syntax, topic) that we don't measure. Our findings apply specifically to formality accommodation.

## Broader Implications

For **conversational AI design**: Our results suggest calibrating accommodation rather than maximizing it. A chatbot that adapts moderately to user style may outperform one that mirrors users precisely. Implementation might involve dampening accommodation strength or introducing controlled variation.

For **CAT theory**: Human-AI contexts reveal boundary conditions for accommodation predictions. The linear convergence-rapport relationship may require qualification when one interlocutor is perceived as artificial.

For **evaluation**: Accommodation metrics could supplement standard evaluation. A system that accommodates appropriately—neither too little nor too much—may better serve user needs than one optimized purely on task performance.

## Future Work

**Causal validation**: Controlled experiments manipulating AI accommodation levels would establish causation. Deploy chatbots with varied accommodation strength and measure user satisfaction directly.

**Cross-platform replication**: Test the Goldilocks pattern on LMSYS-Chat-1M and other datasets. If the inverted-U holds across platforms and model families, it suggests a general human-AI dynamic rather than dataset artifact.

**Multi-dimensional accommodation**: Extend analysis to vocabulary, syntax, and topic alignment. Accommodation trade-offs may differ across dimensions; formality may be more sensitive to over-accommodation than vocabulary.

**User perception studies**: Qualitative research could illuminate why moderate accommodation outperforms high accommodation. Do users consciously perceive differences? What triggers artificiality concerns?
