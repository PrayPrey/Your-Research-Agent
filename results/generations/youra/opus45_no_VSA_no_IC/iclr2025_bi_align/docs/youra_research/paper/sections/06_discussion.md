# Discussion

## What Mode 3 Tells Us

The 24% Mode 3 finding reveals a substantial blind spot in RLHF training signal. In one quarter of preference battles, reward models express high confidence on samples where human voters fundamentally disagree. This is precisely the failure mode that undermines RLHF: models receive strong gradient signal toward outcomes humans did not clearly prefer.

The near-uniform mode distribution (23.7%–26.3% per cell) suggests entropy and variance capture genuinely orthogonal information. This validates the 2×2 decomposition as a diagnostic framework: aggregate metrics would report a single accuracy number, while mode decomposition reveals qualitatively distinct failure patterns.

## What Mode 3 Does Not Tell Us

Despite identifying *that* overconfident misalignment exists, we have not identified *why* it occurs. Two mechanistic hypotheses were tested and either falsified or unsupported:

**Semantic divergence (falsified)**: We expected Mode 3 pairs to show lower semantic similarity—responses different enough for humans to disagree but similar enough for RMs to conflate. Instead, Mode 3 pairs show *higher* similarity. This counterintuitive finding suggests RMs and humans weight different features: when responses are semantically similar, humans may focus on subtle stylistic, tonal, or formatting differences that RMs (and embeddings) miss.

**Prompt subjectivity (unsupported)**: We expected creative/opinion tasks to concentrate Mode 3. The data shows Mode 3 at roughly equal rates across task types (22.2% subjective vs 20.7% objective). Overconfident misalignment is not a property of certain prompt types but pervades the dataset.

## Competing Explanations

Several alternative mechanisms warrant future investigation:

| Hypothesis | Mechanism | Testable Prediction |
|------------|-----------|---------------------|
| **Style/tone** | Responses differ in presentation, not content | Style classifiers distinguish Mode 3 from Mode 1 |
| **RM feature sensitivity** | RMs attend to formatting/length humans ignore | Attention analysis shows divergent features |
| **Embedding limitations** | MiniLM misses fine-grained quality signals | Larger/domain-specific embeddings reveal differences |
| **Human evaluation noise** | High entropy reflects confusion, not preference | Response time/confidence correlates with entropy |
| **Model identity** | Humans prefer model brands, not outputs | Anonymous vs branded battles differ in Mode 3 rate |

## Limitations

**Median-split thresholding**: Our 2×2 mode classification uses median splits on entropy and variance. This methodological choice is simple and reproducible but arbitrary—tercile splits or data-driven clustering (e.g., GMM) might yield different mode boundaries. The near-uniform distribution (23.7%–26.3% per mode) could partly reflect median-split mechanics rather than genuine structure. Sensitivity analysis with alternative thresholds would strengthen conclusions.

**Single RM**: We used OpenAssistant reward model as variance proxy. True multi-RM ensemble (OpenAssistant + PairRM + ArmoRM) would provide more robust variance estimation. Mode boundaries may shift with full ensemble scoring.

**Embedding model**: all-MiniLM-L6-v2 captures semantic similarity but likely misses stylistic, tonal, and structural features. Alternative embeddings (style-aware models, discourse structure features) may reveal differences our analysis missed.

**Entropy aggregation**: Human entropy computed at model-pair level, not per-battle. Individual battles within a model pair may vary substantially. Per-battle entropy with soft labels would enable finer analysis.

**Prompt classification**: Keyword heuristics classified 75% of prompts as ambiguous (excluded). LLM-based classification or Arena metadata tags would improve coverage and accuracy.

**Chatbot Arena specific**: Results may not generalize to other preference datasets (HH-RLHF, SHP, Anthropic-HH). Cross-dataset replication is needed.

**Correlational only**: We observe associations between entropy, variance, and mode membership. We cannot establish that reducing Mode 3 would improve downstream alignment outcomes.

## Implications for Practice

**Evaluation**: RewardBench-style aggregate metrics are insufficient. Mode-aware evaluation should report performance stratified by entropy-variance quadrants, especially flagging Mode 3 accuracy.

**Training**: RLHF practitioners should consider down-weighting or excluding Mode 3 samples from training signal, as these provide unreliable gradient direction.

**Uncertainty**: Reward models should output calibrated uncertainty estimates. High confidence on high-entropy samples indicates miscalibration that could be directly penalized.

**Benchmarking**: Future benchmarks (RewardBench v2) could include mode-specific metrics alongside aggregate accuracy, enabling targeted improvement of reward model weak points.
