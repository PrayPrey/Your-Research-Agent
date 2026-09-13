# Related Work

Having established BAA measurement as an empirically open question, we review three bodies of literature that each address part of the problem — and show why none closes the gap this paper targets.

## AI-to-Human Alignment: Well-Measured, One-Directional

The dominant paradigm in AI alignment research operationalizes "alignment" as the degree to which AI outputs match human preferences, values, or intent. RLHF (Ouyang et al., 2022; Bai et al., 2022) provides preference-labeled training data collected from human raters. Benchmarks such as HELM (Liang et al., 2022), TruthfulQA (Lin et al., 2022), and BIG-Bench (Srivastava et al., 2022) measure AI performance on tasks that proxy human-valued behaviors. This literature is mature, with standardized evaluation infrastructure and reproducible scores across model generations.

A critical feature of this paradigm is that it treats human evaluators as a fixed, stable signal source — a gold standard against which model outputs are judged. The implicit assumption is that rater behavior is stationary: raters in 2024 apply the same judgment standards as raters in 2022. Whether this assumption holds as raters accumulate experience with AI-generated text has not been systematically examined. Our work is motivated in part by the observation that if rater behavior does drift — becoming less discriminating, less likely to flag subtle errors — then AI-to-human benchmark scores may be measuring a moving target.

## Human Behavioral Adaptation: Qualitative Evidence, No Measurement Framework

A smaller literature documents how human behavior adapts in response to AI quality. Dell'Acqua et al. (2023) study management consultants using AI assistance and find that AI-assisted workers progressively delegate cognitively demanding tasks to AI, producing measurable deskilling in unassisted task performance. Their effect sizes (0.3–0.5 SD in consulting task quality) motivate our choice of |τ| ≥ 0.2 as a minimum detectable effect threshold. Crucially, however, Dell'Acqua et al. measure task assignment behavior in a controlled experimental setting, not behavioral signals in naturalistic interaction logs — their finding cannot be directly generalized to general-purpose AI users.

Perez et al. (2023) demonstrate that AI sycophancy — models that agree with users regardless of correctness — suppresses human expression of disagreement. This is complementary to BAA: if AI models are trained to suppress explicit corrections, measuring correction frequency as a BAA proxy will undercount genuine disengagement. Our finding that explicit correction frequency is near-zero (base rate ~0.05% of turns) is consistent with sycophancy-driven suppression, though equally consistent with genuine absence of explicit correction behavior.

Shen et al. (2024) provide the most direct conceptual ancestor of the present work, surveying the landscape of bidirectional human-AI alignment and identifying the measurement gap at the framework level. They propose behavioral proxy dimensions but provide no empirical measurement on public interaction logs. We implement and test their implied measurement program, producing the first large-scale empirical test.

## Temporal Analysis of AI Interaction Logs

The Chatbot Arena platform (Zheng et al., 2023) provides timestamped human preference votes across model pairs, making it the natural data source for temporal preference entropy analysis (our Proxy 2). We were unable to access the primary `lmsys/chatbot_arena_conversations` dataset due to gating on HuggingFace; the publicly available `lmsys/lmsys-arena-human-preference-55k` fallback dataset contains no timestamps. This infrastructure gap blocks Proxy 2 computation in our experiments.

WildChat (Zhao et al., 2024) provides 1 million ChatGPT conversation logs with IP-hash pseudonymization, timestamps, and topic tags. Prior analyses of WildChat have focused on content characterization (e.g., harmful query prevalence), topic distribution, and model version comparison — not on behavioral trend analysis within returning-user cohorts. We introduce the returning-user cohort construction methodology (≥3 monthly appearances per IP-hash, monthly aggregation) as a novel analytical lens for this dataset.

Mann-Kendall trend analysis is standard in environmental and behavioral time series analysis (Hamed & Rao, 1998; Mann, 1945; Kendall, 1975). The Hamed-Rao modification for autocorrelated series is critical in our context: the strong ACF lag-1 = 0.634 in our prompt token count series would produce an inflated false-positive rate under the standard Mann-Kendall test. To our knowledge, no prior work has applied Hamed-Rao corrected Mann-Kendall to behavioral proxies in AI interaction logs.

## Our Position

Existing work on AI-to-human alignment does not account for human behavioral adaptation over time. Existing work on human behavioral adaptation in AI interactions (deskilling, over-reliance) uses controlled experiments, not public interaction logs. Existing temporal analyses of WildChat and LMSYS Arena do not construct returning-user cohorts or test behavioral trends. Shen et al. (2024) identify the BAA framework conceptually but provide no empirical measurement.

We occupy the gap: first empirical test of BAA directional predictions at scale, using public interaction logs, with a validated and reusable pipeline. The negative result we report — BAA disengagement not confirmed — constrains the framework and provides the methodological foundation for the future studies that can resolve it.
