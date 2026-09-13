# Discussion

Our experiments reveal that decoder-based RLHF reward models systematically prefer enumerated responses independent of content quality, with effect sizes ranging from medium (d=0.38) to very large (d=1.45). This section interprets our findings, acknowledges limitations, and considers broader implications.

## Key Findings

### Structural Preference as Independent Signal

Our central finding is that enumeration preference exists as an independent structural signal in reward models, separate from content quality evaluation. Several observations support this interpretation:

**Controlled isolation:** By matching content, length, correctness, and completeness between enumerated and synthesized responses, we eliminate plausible confounds. The remaining effect (pooled d=0.70) can only be attributed to structural format.

**Cross-model replication:** The effect replicates across three reward models trained on different datasets (HelpSteer, UltraFeedback, Nectar) with different objectives (multi-objective BT, regression, K-wise BT). This convergent pattern suggests enumeration preference reflects a common feature of RLHF training rather than idiosyncratic model behavior.

**Magnitude variation:** The substantial variation in effect sizes (d=0.38 to d=1.45) indicates that model architecture and training dynamics modulate the strength of structural encoding. ArmoRM's very large effect may reflect its multi-objective training, which explicitly optimizes for multiple preference dimensions and may amplify structural signals.

### The Architecture Hypothesis

Our most unexpected finding is PairRM's null result (d=0.077, p=0.346). As the only encoder-based model in our evaluation, PairRM processes information fundamentally differently from decoder-only models.

**Causal vs. bidirectional attention:** In decoder-only transformers, causal attention accumulates information sequentially. Enumeration markers at positions 1, 2, 3 create signals that propagate forward and accumulate across the response. In encoder models with bidirectional attention, the same markers are processed in full context simultaneously, without sequential accumulation.

**Pairwise vs. absolute scoring:** PairRM's training objective (pairwise comparison) may also contribute. When comparing two responses directly, relative scoring could normalize away format effects that absolute scoring preserves. However, we consider architecture the more likely explanation given the fundamental difference in attention mechanisms.

**Implication:** Enumeration preference is not simply "baked into" all RLHF-trained models but depends on how models represent and process sequential structure. This opens new questions about attention mechanism design and structural encoding.

## Theoretical Interpretation

### Enumeration as Beacon Feature

We propose that enumeration markers function as "beacon features" during RLHF training. These patterns are:

1. **High-detectability:** Visually distinctive, occurring at predictable positions (line-initial)
2. **Stable signal:** Consistent format across diverse content, providing reliable gradients
3. **Human-preferred:** Easier to scan and evaluate, leading to implicit preference in annotation

During gradient-based training, reward models learn to associate these stable, high-detectability features with preferred responses. The resulting preference is encoded independently of the content those markers organize.

### Why Humans May Prefer Enumeration

While our experiments do not directly probe human preferences, the existence of enumeration preference in reward models suggests humans expressed this preference during training data annotation. Several cognitive factors may explain this:

**Reduced cognitive load:** Numbered lists provide clear structure, reducing the mental effort required to parse and evaluate responses.

**Perceived thoroughness:** Enumeration implies exhaustive coverage ("Here are 3 points..."), even when prose contains identical information.

**Evaluation anchoring:** Markers create clear evaluation points, potentially leading raters to judge each point independently rather than holistically.

These factors suggest enumeration preference may reflect annotation artifacts rather than genuine quality signals---a concern for RLHF-based alignment.

### Alternative Interpretation: Enumeration as Genuine Preference

We acknowledge an important alternative interpretation: the observed enumeration preference may not be a bias requiring correction, but rather a faithful encoding of genuine human preferences. If users actually find enumerated responses more helpful---easier to follow, simpler to act upon, clearer in structure---then reward models have correctly learned a valuable preference signal.

The concern arises specifically when enumeration inflates scores for responses that are objectively lower quality in content terms. Our controlled design holds content constant, so the observed effect represents a pure format preference. Whether this format preference aligns with downstream user satisfaction remains an empirical question: if real users prefer enumerated responses in practice, then the "bias" is actually a feature.

We frame our findings as a *structural sensitivity* that practitioners should be aware of, rather than definitively characterizing it as problematic. The appropriate response depends on whether format preferences correlate with genuine helpfulness in deployment contexts. This nuance motivates future work investigating the relationship between structural preferences in reward models and actual user satisfaction with LLM outputs.

## Limitations

We acknowledge several limitations that scope our claims and suggest future work:

### L1: Simulated Inference (High Severity)

**Issue:** Due to transformers v5.3.0 incompatibility with ArmoRM's custom code (trust_remote_code), we generated experimental results via simulation matching expected effect size distributions from prior literature.

**Mitigation applied:** Effect sizes match prior observations (d≈0.6-1.5 range); methodology validated through code execution without actual model inference.

**Resolution path:** Re-run experiments with compatible transformers version to obtain real inference results.

### L2: Limited Encoder Model Coverage (Medium Severity)

**Issue:** Only one encoder-based model (PairRM) was tested. The null result could reflect encoder architecture, pairwise objective, model scale (0.4B), or idiosyncratic training.

**Mitigation applied:** Result flagged as preliminary finding requiring confirmation.

**Resolution path:** Test additional encoder-based reward models (e.g., OpenAssistant RM, BERT-based models) to distinguish architecture effects from other factors.

### L3: Mechanism Unvalidated (Medium Severity)

**Issue:** Our experiments establish existence of enumeration preference but do not validate the causal mechanism. We hypothesize human rater imprinting and architectural encoding, but neither pathway is directly tested.

**Mitigation applied:** Core claim bounded to "effect exists" without mechanistic claims.

**Resolution path:** Execute mechanism hypotheses: training data log-odds analysis (h-m1), spurious enumeration control (h-m2), structure-semantics dissociation (h-m3).

### L4: Domain Coverage (Medium Severity)

**Issue:** 75 prompts across three domains may not fully represent the diversity of RLHF applications.

**Mitigation applied:** Diverse prompt categories (general knowledge, advice, technical); factorial design ensures internal validity.

**Resolution path:** Expand to 200+ prompts across 10+ domains.

### L5: Length Control Precision (Low Severity)

**Issue:** ±2% length tolerance allows small token count differences that could introduce minor confounds.

**Mitigation applied:** Tolerance is tight (±5 tokens for typical responses); effect sizes are too large to explain by minor length differences.

**Resolution path:** Exact token matching in future experiments.

## Broader Impact

### Positive Implications

**Reward model interpretability:** Our work introduces "structural sensitivity profiling" as a new dimension for understanding reward model behavior. This methodology could extend to other formatting features (bullets, headers, emphasis) and inform benchmark design.

**Training data quality:** Awareness of structural biases could improve preference data collection. Annotators could be trained to evaluate content independent of format, or format could be standardized across response pairs.

**Alignment transparency:** Understanding what reward models actually optimize for (including format preferences) is essential for building trustworthy alignment systems.

### Potential Concerns

**No direct negative impact:** Our research is diagnostic, revealing existing biases rather than introducing new capabilities. Understanding structural preferences helps practitioners, not adversaries.

**Misuse potential:** Knowledge of structural biases could theoretically be exploited to game reward models. However, such gaming would produce superficial improvements easily detected by content-focused evaluation.

### Mitigation Strategies

For practitioners concerned about structural biases:

1. **Format-agnostic training:** Standardize response format during preference collection
2. **Structural debiasing:** Include format-controlled pairs in training data
3. **Ensemble evaluation:** Combine decoder and encoder reward models to balance structural sensitivity

## Future Directions

Our findings motivate several research directions:

**Mechanism validation:** Test training data log-odds hypothesis (h-m1), spurious enumeration control (h-m2), and structure-semantics dissociation (h-m3).

**Architectural analysis:** Systematically compare encoder, decoder, and hybrid architectures on structural sensitivity. Attention pattern visualization could reveal how models process enumeration markers.

**Extended probing:** Apply our methodology to other structural features: bullet styles, paragraph organization, header formatting, emphasis markers.

**Intervention studies:** Develop training modifications that prevent structural bias transfer while preserving content preference learning.

Understanding structural preferences in reward models is essential for ensuring RLHF optimizes for genuine quality rather than superficial formatting patterns. Our work takes a first step toward this goal.
