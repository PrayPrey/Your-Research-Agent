# Experimental Setup

## Research Questions

Our experiments address three questions tied to the mechanism hypothesis:

**RQ1:** Does CoT prompting reliably produce reasoning chains with epistemic hedging markers?

**RQ2:** Are hedging markers structurally positioned to influence confidence generation?

**RQ3:** Does hedging marker presence correlate with lower verbalized confidence?

## Dataset

We evaluate on TruthfulQA (Lin et al., 2022), an adversarial benchmark designed to test model tendency toward common human misconceptions. TruthfulQA's generation split contains 817 questions across categories including health, law, finance, and common sense.

We select TruthfulQA for three reasons. First, it presents genuinely difficult questions where calibration matters—models should be uncertain on questions likely to elicit misconceptions. Second, the adversarial design creates variation in question difficulty, providing range for correlation analysis. Third, the moderate size (817 items) balances statistical power with computational feasibility.

## Model Configuration

We use GPT-3.5-turbo accessed via OpenAI API with the following configuration:
- Temperature: 0 (deterministic outputs)
- Max tokens: 512-1024 (sufficient for CoT + answer + confidence)
- Model: gpt-3.5-turbo (instruction-tuned, widely deployed)

We select a single model to establish proof-of-concept for the mechanism. Multi-model replication (Llama-2-70B, Claude, GPT-4) is deferred to future work.

## Evaluation Metrics

**Hedging Marker Count:** Integer count of 17 predefined epistemic markers per output. Markers are case-insensitive and include: "may," "could," "might," "possibly," "perhaps," "likely," "unlikely," "but," "however," "although," "alternatively," "uncertain," "not sure," "seems," "appears," "probably," "suggest."

**Hedging Presence Rate:** Binary indicator of whether any hedging marker appears in output.

**Verbalized Confidence:** Numerical confidence (0-100%) extracted from model output.

**Reasoning Rate:** Binary indicator of multi-step reasoning presence.

**Step Count:** Number of reasoning steps identified via sentence segmentation and transition markers.

**Spearman Correlation:** Rank correlation between hedging count and confidence, with significance computed via permutation test (10,000 permutations).

## Sub-Hypothesis Evaluation Protocol

Each sub-hypothesis has predetermined pass/fail criteria:

| Hypothesis | Gate Type | Primary Metric | Threshold |
|------------|-----------|----------------|-----------|
| H-E1 | MUST_WORK | extraction_rate | >95% |
| H-M1 | MUST_WORK | cot_reasoning_rate | >90% |
| H-M2 | SHOULD_WORK | hedging_presence_rate | >30% |
| H-M3 | SHOULD_WORK | markers_precede_rate | >95% |
| H-M4 | MUST_WORK | spearman_r | < -0.2 |

MUST_WORK gates indicate mechanism steps that must pass for the overall hypothesis to hold. SHOULD_WORK gates indicate supporting evidence that strengthens but does not determine the conclusion.

## Implementation

All experiments use cached API responses where available to ensure reproducibility. The H-M4 correlation analysis reuses outputs from H-M2 hedging detection, ensuring identical samples for both analyses (n=664 samples with valid confidence extraction).

Code implementations are modular, with separate components for:
- Confidence extraction (regex-based parsing with fallbacks)
- Hedging detection (keyword matching with position tracking)
- Positional analysis (segment identification and ordering verification)
- Correlation computation (Spearman with bootstrap confidence intervals)
