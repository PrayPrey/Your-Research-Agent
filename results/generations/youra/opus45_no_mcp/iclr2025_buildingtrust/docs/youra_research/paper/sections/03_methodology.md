# Methodology

Our experimental design systematically verifies the causal mechanism linking CoT prompting to improved confidence calibration. Rather than simply measuring end-to-end ECE improvement, we decompose the hypothesized mechanism into four testable steps and validate each independently.

## Mechanism Hypothesis

We hypothesize that CoT+confidence improves calibration through a "self-reading" mechanism:

1. CoT prompting forces the model to articulate reasoning before answering
2. This reasoning reveals epistemic uncertainty through hedging markers
3. Hedging markers appear in-context before confidence generation (due to autoregressive generation)
4. The model incorporates these uncertainty signals into its confidence estimate

This mechanism predicts a negative correlation between hedging marker count and verbalized confidence: more hedging should lead to lower confidence.

## Sub-Hypothesis Decomposition

We decompose the main hypothesis into five sub-hypotheses, each testing a specific component:

**H-E1 (Existence):** ECE can be reliably computed across all experimental conditions, with confidence extraction success rate >95%.

**H-M1 (Mechanism Step 1):** CoT prompting produces multi-step reasoning chains (>90% reasoning rate, mean steps >2.0).

**H-M2 (Mechanism Step 2):** CoT outputs contain epistemic hedging markers (>30% presence rate).

**H-M3 (Mechanism Step 3):** Hedging markers appear before confidence verbalization in the output sequence (>99% structural compliance).

**H-M4 (Mechanism Step 4):** Hedging marker count negatively correlates with verbalized confidence (Spearman r < -0.2, p < 0.05).

## Experimental Design

**Dataset:** We use TruthfulQA (Lin et al., 2022), an adversarial benchmark testing model tendency toward common misconceptions. The generation split contains 817 items, providing sufficient statistical power for correlation analysis.

**Model:** GPT-3.5-turbo via OpenAI API, with temperature=0 for deterministic outputs. This represents a widely-deployed instruction-tuned model capable of following structured prompting.

**Prompting Conditions:** Our design includes five conditions:
- Baseline: Direct answer only
- CoT-only: "Let's think step by step" + answer
- Confidence-only: Answer + "Confidence: X%"
- CoT+Confidence: CoT reasoning + answer + confidence
- Token-padding control: Random filler tokens + answer + confidence

The token-padding control tests whether any calibration improvement is merely a token-count artifact rather than meaningful uncertainty integration.

## Measurement Protocols

**Hedging Marker Detection:** We identify 17 epistemic hedging markers based on linguistic literature (Hyland, 1998): "may," "could," "might," "possibly," "perhaps," "likely," "unlikely," "but," "however," "although," "alternatively," "uncertain," "not sure," "seems," "appears," "probably," "suggest."

**Confidence Extraction:** We parse verbalized confidence from outputs using regex matching for patterns like "Confidence: X%" with fallback to percentage mentions.

**Positional Analysis:** We verify structural ordering by identifying CoT, answer, and confidence segments and confirming markers appear before confidence statements.

**Correlation Analysis:** We compute Spearman rank correlation between hedging count and confidence, with significance testing via permutation.

## Validation Criteria

Each sub-hypothesis has explicit pass/fail gates:
- H-E1: All conditions achieve >95% extraction rate, ECE in [0,1]
- H-M1: CoT reasoning rate >90%, rate difference >50% vs baseline, mean steps >2.0
- H-M2: Hedging presence rate >30%
- H-M3: CoT-before-confidence rate >99%, markers-precede rate >95%
- H-M4: Spearman r < -0.2, p < 0.05, n ≥ 500

This decomposition ensures that even if the primary ECE comparison remains inconclusive, we can identify which mechanism steps are validated versus where the chain breaks.
