# Conclusion

One in four preference battles hides a silent failure. Analyzing 57,477 Chatbot Arena battles, we find that **23.7%** exhibit overconfident misalignment—reward models expressing high confidence on precisely the samples where human preferences diverge. This Mode 3 pattern is not a fringe phenomenon but a systematic feature of real-world alignment data.

Our 2×2 mode decomposition (entropy × variance) provides a diagnostic lens that aggregate metrics miss. While RewardBench reports overall accuracy, mode decomposition reveals *where* failures concentrate. The near-uniform distribution across four modes (23.7%–26.3%) validates that human entropy and RM variance capture orthogonal information about preference battles.

We tested two mechanistic hypotheses and falsified both. Semantic divergence is not the cause: Mode 3 response pairs show *higher* similarity than aligned pairs. Prompt subjectivity is not the cause: Mode 3 pervades all task types at roughly equal rates. The root cause of overconfident misalignment remains unknown.

**Contributions.** We provide the first quantification of overconfident RM misalignment at scale, introduce mode decomposition as an alignment diagnostic framework, and constrain the hypothesis space by ruling out two candidate mechanisms.

**Limitations.** Results rely on a single RM variance proxy; full ensemble validation is needed. Findings are Chatbot Arena-specific; generalization requires cross-dataset replication. Analysis is correlational; causal links to downstream alignment outcomes are not established.

**Future work.** The mechanism quest continues. Priority directions include: (1) style-aware embeddings that capture presentation differences; (2) RM attention analysis identifying features driving confidence on disagreement samples; (3) full multi-RM ensemble validation of mode boundaries; (4) per-battle entropy estimation with soft labels; (5) cross-dataset replication on HH-RLHF and SHP.

The 24% Mode 3 rate demonstrates that aggregate evaluation masks substantial failure patterns. Until we understand *why* reward models are confident where humans disagree, RLHF training signal in these cases remains unreliable. Mode-aware evaluation and uncertainty-calibrated reward models offer paths toward addressing this blind spot.
