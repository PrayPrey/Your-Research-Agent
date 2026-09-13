# Methodology

Our approach operationalizes the Human→AI alignment concept through a pipeline of extraction, independence validation, and semantic verification. Figure 1 illustrates the overall architecture: we extract agency proxies from preference data responses, compute a composite BAI score, validate its representational independence from reward through adversarial probing, and test semantic coherence of the extracted signal.

## Agency Proxy Extraction

We define four agency proxies motivated by HumanAgencyBench's dimensions of agency-preserving behavior:

**Clarifying Questions.** Binary indicator for responses containing question structures that seek clarification before providing advice. Detected via regex patterns matching interrogative forms following advisory content (e.g., "Are you asking whether...", "Do you mean...").

**Option Enumeration.** Count of explicitly enumerated alternatives presented to the user. Detected via numbered lists, "Option A/B/C" patterns, and bullet-pointed alternatives.

**Epistemic Hedging.** Ratio of uncertainty markers to total tokens. Includes modal verbs (might, could, may), epistemic adverbs (possibly, perhaps), and qualification phrases (I'm not certain, it depends).

**Explicit Deferral.** Binary indicator for responses that explicitly defer to user judgment or external expertise. Detected via phrases indicating the AI's limitations or user's superior position to decide.

For each proxy, we train a TF-IDF (n-gram 1-2, max 5000 features) plus Logistic Regression classifier using regex-generated labels as ground truth. This creates continuous probability scores suitable for aggregation.

## BAI Computation

The Bidirectional Alignment Index combines proxy probabilities with length normalization:

$$\text{BAI} = \frac{1}{4} \sum_{p \in \text{proxies}} P(p|\text{response}) \cdot \frac{1}{1 + 0.1 \cdot \log(\text{word\_count})}$$

Length normalization prevents longer responses from systematically scoring higher due to more opportunities to exhibit agency patterns. The logarithmic scaling reduces sensitivity to extreme lengths while preserving discriminative signal.

## Adversarial Probing for Representational Independence

To test whether BAI occupies a representationally independent subspace from reward, we employ gradient reversal training. The architecture consists of:

1. **Shared encoder.** Maps response representations to a hidden space (4096-dimensional, matching Llama-3-8B).

2. **Reward probe.** Linear layer predicting reward model scores, trained with standard gradient descent.

3. **BAI probe.** Linear layer predicting BAI scores, trained with gradient reversal: gradients are negated before backpropagation to the shared encoder, forcing the encoder to remove reward-predictive information.

If BAI occupies an independent subspace, the BAI probe should maintain high performance (AUROC ≥ 0.7) even after gradient reversal suppresses reward-predictive variance. Conversely, if BAI is merely a stylistic subcomponent of reward, BAI predictability should collapse when reward variance is removed.

We use DANN-style sigmoid scheduling for the gradient reversal coefficient, ramping from 0 to 1 over the first training epoch. This stabilizes early training before full adversarial pressure applies.

## Disagreement Analysis

We quantify systematic disagreement between BAI and reward through quartile-based analysis. After z-score standardization of both metrics, we identify responses in disagreement quadrants:

- **High-BAI/Low-Reward (HL):** Responses with BAI above the 75th percentile and reward below the 25th percentile.
- **Low-BAI/High-Reward (LH):** Responses with BAI below the 25th percentile and reward above the 75th percentile.

The disagreement rate is the proportion of responses in HL ∪ LH. A rate ≥ 20% indicates systematic orthogonality; ≥ 10% indicates moderate but meaningful disagreement.

## Semantic Coherence Validation

Representational independence does not guarantee semantic meaningfulness. A BAI signal that captures arbitrary variance would be technically independent but scientifically uninteresting. We test semantic coherence by clustering the disagreement slice (HL + LH responses) and checking for interpretable agency patterns.

We embed disagreement responses using all-MiniLM-L6-v2, reduce dimensions via UMAP (5 components, 15 neighbors), and cluster with BERTopic (HDBSCAN, min_cluster_size=50). For each discovered topic, we extract top keywords via c-TF-IDF and match against an agency vocabulary: clarify, prefer, might, option, perhaps, consider, alternatively, suggest, uncertain, etc.

The agency pattern rate is the proportion of topics whose top-10 keywords contain ≥ 2 agency vocabulary terms. A rate ≥ 50% indicates semantic coherence; lower rates suggest the BAI signal captures surface features rather than functional agency.

## Experimental Design Summary

We test four sub-hypotheses in dependency order:

- **H-E1 (Existence):** Agency proxies achieve AUROC ≥ 0.8 against regex labels.
- **H-M1 (Mechanism):** BAI AUROC ≥ 0.7 after gradient reversal; reward R² degrades < 2%.
- **H-M2 (Mechanism):** Disagreement rate ≥ 20% (PASS) or ≥ 10% (PARTIAL).
- **H-C1 (Condition):** Agency pattern rate ≥ 50% in clustered disagreement slice.

H-E1 and H-M1 are MUST_WORK gates; H-M2 and H-C1 are SHOULD_WORK gates that inform interpretation even if they fail.
