# Related Work

Our work connects three previously independent research areas: contamination detection, data attribution, and training data curation. We review each and highlight how their separation has obscured the curation-contamination relationship we address.

## Benchmark Contamination Detection

Detecting test data contamination in LLM training corpora has become essential for reliable evaluation. **N-gram overlap methods** identify exact or near-exact matches between training and test examples. Recent work recommends n=8 as the detection threshold, noting that larger n leads to false negatives while smaller n generates excessive false positives [ConTAM, arXiv 2411.03923]. The LLM-Decontaminator extends detection to rephrased samples through embedding similarity, addressing evasion via paraphrasing [Rethinking Benchmark Contamination, arXiv 2311.04850].

**Membership inference** approaches operate without explicit training corpus access. Min-K%++ identifies training samples as local probability maxima in model output distributions [Zhang et al., 2024]. CDD (Contamination Detection via output Distribution) complements detection with TED (Trustworthy Evaluation via output Distribution), achieving up to 66.9% contamination mitigation [Dong et al., 2024]. The Contamination Taxonomy [Palavalli et al., 2024] categorizes contamination by type (input-only, input-output) and impact mechanism.

**Limitation:** These methods detect contamination presence/absence but do not explain how curation decisions affect contamination rates. Detection operates *after* training; our work addresses the curation stage *before* training where contamination is amplified or attenuated.

## Data Attribution Methods

Data attribution identifies which training examples contribute to model predictions. **Influence functions** [Koh and Liang, 2017] approximate leave-one-out effects but scale poorly to large models. **TRAK** (Attributing Model Behavior at Scale) [Park et al., 2023] enables practical attribution through random projection, achieving 6500× speedup via the LoGra algorithm [Choe et al., 2024]. DDA addresses fitting error considerations in attribution estimation [Wu et al., 2024].

Attribution has been applied to data valuation, detecting mislabeled examples, and understanding model behavior. However, it has not been combined with contamination detection to trace *which* influential examples derive from benchmark overlap.

**Limitation:** Prior attribution work treats all high-influence examples uniformly. We distinguish between legitimate high-influence examples (valuable training signal) and contaminated high-influence examples (benchmark memorization), using CCR to quantify the distinction.

## Training Data Curation

Modern LLM training relies heavily on data curation. **DataComp-LM** [Li et al., 2024] established that model-based filtering significantly affects downstream performance, with DCLM-Baseline achieving strong results through careful selection. **SlimPajama** [Shen et al., 2023] demonstrated that global versus local deduplication strategies yield different model capabilities. **FineWeb** pipelines [Penedo et al., 2025] combine multiple filtering stages (perplexity, classifier, heuristics) for web-scale curation.

Perplexity-based filtering—selecting documents that score well against reference language models—has emerged as a core technique. RedPajama-V2 includes pre-computed `ccnet_perplexity` scores using Wikipedia-trained models, enabling researchers to filter by perplexity bucket.

**Limitation:** Curation research focuses on quality-performance relationships without analyzing contamination effects. DataComp-LM showed filtering improves benchmark scores but did not investigate whether improvements reflect genuine capability or contamination amplification. Our work fills this gap.

## Connecting the Three Areas

The gap we address is visualized in Figure 1: contamination detection identifies problematic examples, attribution traces influence, curation shapes corpus composition—but no prior work connects all three. This separation means practitioners cannot answer: "How much does my curation strategy amplify benchmark contamination, and does it matter for model capabilities?"

We introduce CCR as the connecting metric. By combining TRAK attribution with n-gram contamination detection, CCR quantifies the contamination-attributed fraction of benchmark performance. This enables direct comparison across curation strategies and causal validation through removal experiments.

Our approach differs from concurrent work on clean benchmarks (e.g., LiveCodeBench [Jain et al., 2024]) which constructs new evaluation sets to avoid contamination. We instead *measure* contamination effects to understand existing benchmarks, providing a complementary perspective on evaluation integrity.
