# Conclusion

We began with a detector that worked perfectly — every implementation check green, every test passing — and an AUROC of 0.4933. This juxtaposition is not a cautionary tale about experimental failure. It is how we learned where a widely-adopted hallucination detection paradigm breaks.

Our investigation of NLI-based Semantic Mode Consistency (SMC-NLI) applied to Llama-3-8B-Instruct on HaluEval QA reveals that sampling-based consistency methods operate under a regime assumption — *that hallucinated outputs are stochastically diverse across samples* — that does not hold for instruction-tuned models on structured factual QA. RLHF fine-tuning produces systematic confabulation: consistent outputs for both correct and wrong beliefs, eliminating the consistency-based discriminative signal. Mean SMC-NLI scores for correctly-labeled (0.6236) and hallucinated-labeled (0.6299) questions differ by 0.006 — noise level — confirming the mechanism fails at the distributional level, not the implementation level.

The parallel SMC-Embed evaluation (AUROC=0.4859) rules out the NLI scorer as the source of failure. The validated implementation (14/14 tests passing, 10,000 real samples, 45,000 NLI pairs) rules out engineering error. What remains is a clean negative result: the assumed hallucination regime does not characterize Llama-3-8B-Instruct on this task.

**What we leave behind:** A validated SMC pipeline (LLMSampler, SMCNLIScorer, SMCEmbedScorer) tested at scale, ready for deployment on model-task combinations where the stochastic hallucination regime holds. A regime classification framework — stochastic hallucination vs. systematic confabulation — that provides a testable prerequisite for applying these methods. A benchmark validity concern about cross-model evaluation using ChatGPT-generated labels.

**What comes next:** The stochastic hallucination regime that prior work validated on GPT-3 open-ended generation should be re-examined for instruction-tuned models on open-ended tasks (WikiBio-style biography generation, long-form QA). If the regime holds there but not on structured QA, we have a task-type boundary. If neither task type produces the stochastic regime for instruction-tuned models, the boundary is model-type — and the UQ community needs calibration-aware alternatives for RLHF-fine-tuned models. Either finding advances our understanding of when and why these methods work.

The infrastructure is validated. The regime question is open. The next experiment is clear.
