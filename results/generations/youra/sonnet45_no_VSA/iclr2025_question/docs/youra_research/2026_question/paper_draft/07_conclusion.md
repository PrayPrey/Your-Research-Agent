# 7. Conclusion

We set out to test whether CCP-based hallucination detection degrades when applied to creative text, hypothesizing that NLI models trained on factual corpora embed ontology-specific assumptions. Instead, we encountered a measurement validity failure: ρ_j values were **50× lower than expected** across BOTH factual and creative domains (0.01-0.04 vs 0.75-0.85), preventing hypothesis testing.

Root cause analysis identified a **task-domain gap**: DeBERTa-v3-base NLI trained on SNLI/MNLI semantic similarity tasks does not generalize to factual verification (claim-context consistency checking), assigning ~90% probability mass to "neutral" class regardless of actual entailment relationships. This failure mode is **task-agnostic** (affects factual and creative domains equally), not domain-specific as originally hypothesized.

**Lesson learned**: Measurement validity is prerequisite for hypothesis testing. When a metric produces values 50× outside expected range, "hypothesis is wrong" becomes indistinguishable from "measurement is broken." The correct response is methodological humility: replicate baseline on original domain BEFORE testing domain transfer.

**Contributions**: (1) Transparent documentation of CCP replication failure with detailed failure modes, (2) root cause hierarchy establishing NLI calibration as critical prerequisite (with claim decomposition and context pairing as contributory factors), (3) reproducibility requirements for hallucination detection papers (report raw metric distributions, validate NLI calibration, document claim extraction, provide public code).

**Call to action**: The field must adopt higher reproducibility standards. Papers should treat implementation details (NLI model choice, calibration diagnostics, claim decomposition methodology) as first-class contributions, not footnotes. Transparent failures—like this one—accelerate progress by preventing repetition of costly mistakes.

Returning to our opening provocation: we could not reproduce CCP baseline ρ_j values 50× lower than expected. The culprit: undocumented NLI training distribution mismatch (SNLI/MNLI semantic similarity ≠ factual verification). The remedy: validate NLI calibration on target task BEFORE claiming hallucination detection improvements. The broader implication: **measurement validity gates hypothesis testing** in ways papers often fail to acknowledge.

Future researchers building on CCP should prioritize: (1) NLI fine-tuning on FEVER/HotpotQA, (2) claim method comparison (NLTK vs LLM vs Spacy), (3) baseline replication on TruthfulQA factual domain, (4) only after validation succeeds, test creative domain transfer. Our negative result clears the path for methodologically rigorous follow-up work.
