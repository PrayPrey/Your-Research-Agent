# 1. Introduction

Hallucination detection methods rely on NLI models to assess claim-context consistency. Claim-Conditioned Probability (CCP) aggregates token-level probabilities weighted by NLI entailment scores, reporting +0.05–0.10 ROC-AUC improvements (arxiv:2403.04696). We tested whether CCP degrades on creative text (fiction, metaphor) versus factual text, hypothesizing that NLI-based conditioning embeds factual-ontology assumptions incompatible with creative semantics.

**We could not reproduce the baseline.** Claim-type mass ratio ($\rho_j$) values were 20–80× lower than expected: median 0.0354 (factual), 0.0103 (creative) vs inferred range 0.75–0.85. Statistical tests showed no domain separation ($p = 1.0$, Cohen's $d = -0.0635$).

Root cause: DeBERTa-v3-base NLI, trained on SNLI/MNLI semantic similarity tasks, assigns ~90% probability mass to "neutral" for claim-context pairs. This NLI miscalibration for factual verification is a known issue in domain adaptation (Pan & Yang 2010; FEVER baseline papers, Thorne et al. 2018), though its impact on hallucination detection has not been systematically documented. Competing explanations remain untested: context pairing strategy (full-text vs sentence windows) and claim decomposition quality (sentence tokenization vs LLM extraction) may contribute to the failure.

Methodologically, this case study illustrates that measurement validity is prerequisite for hypothesis testing. When a metric produces values 20–80× outside the expected range across ALL conditions, you cannot distinguish "hypothesis is wrong" from "measurement is broken." Without baseline validation on the CCP paper's original dataset (which lacks public code or implementation details), we cannot confirm whether our implementation is correct.

**Contributions**:

1. **Transparent Failure Documentation**: First systematic CCP replication attempt, documenting failure modes (NLI neutral-class dominance, missing baseline validation) and competing explanations (calibration vs context pairing vs claim decomposition).

2. **Root Cause Hierarchy & Reproducibility Practices**: We rank failure modes by evidence strength (NLI calibration: Tier 1; claim decomposition + context pairing: Tier 2) and adapt Dodge et al. (2019) reproducibility checklist for hallucination detection: (R1) report raw metric distributions; (R2) validate NLI calibration on known examples; (R3) document claim decomposition with inter-method agreement; (R4) provide public code with baseline replication notebooks.

3. **Case Study of Measurement Validity Failure**: Demonstrates that when a metric deviates 20–80× from expected values across all conditions, hypothesis testing becomes logically impossible without baseline validation on the original dataset.

**Broader Impact**: With 50+ hallucination detection papers published in 2024 citing NLI-based methods, transparent failures prevent costly replication waste across labs. This work shows that implementation details (NLI model choice, context pairing, claim extraction) are first-class contributions, not afterthoughts.

The paper is organized as follows: §2 reviews related work; §3 documents our CCP implementation; §4-5 present results and root cause analysis; §6-7 discuss limitations and lessons learned.
