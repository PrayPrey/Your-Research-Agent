# Linguistic Agency Markers in RLHF Evaluation: A Validation Study

## Abstract

Reinforcement learning from human feedback (RLHF) has become standard for aligning language models, yet evaluation metrics focus on AI-side properties (helpfulness, harmlessness) with limited attention to human-side effects such as agency preservation. This study tests whether linguistic markers validated in human psychology (modal verbs, hedging language, alternative-framing phrases) can serve as computational proxies for measuring agency preservation in RLHF contexts. Using 169,352 preference pairs from the Anthropic HH-RLHF dataset, we conducted a two-stage validation: (1) feasibility testing showed that markers can be reliably extracted with high precision (100%) and sufficient variance (CV=0.781), but (2) construct validation revealed that markers do not validly measure agency preservation, failing effect size criteria (Cohen's d=-0.018, 88% below threshold of 0.15), internal consistency (Cronbach's α=0.42 vs. required 0.7), and cross-split replication (0/2 splits passed). These findings demonstrate that statistical significance (p<0.001) does not guarantee practical relevance with large samples (N=169K), and that cross-domain proxy transfer from human psychology to AI-generated text requires empirical validation rather than theoretical assumption. The negative result establishes validation requirements for future computational operationalization of bidirectional alignment metrics.

## 1. Introduction

Reinforcement learning from human feedback (RLHF) aligns language models by training on human preference judgments (Ouyang et al., 2022; Bai et al., 2022). Current evaluation focuses on AI-side metrics: response quality (AlpacaEval, MT-Bench), factual accuracy (TruthfulQA), and safety properties. The bidirectional alignment framework (Shen et al., 2024) identifies a complementary dimension: Human→AI alignment, which concerns whether alignment processes preserve human agency, critical evaluation capacity, and decision autonomy. No computational metrics currently operationalize this dimension.

Linguistic research documents associations between specific textual features and psychological constructs in human language. Juanchich et al. (2017) found that modal verbs (could, might, should) correlate with perceived autonomy attribution in controlled experiments. Biber et al. (1999) documented hedging phrases (appears, seems, possibly) as markers of epistemic stance. These findings establish that linguistic features can indicate agency-related constructs in human-authored text. Whether these associations transfer to AI-generated responses in RLHF contexts remains untested.

This study addresses the question: Can linguistic agency markers validated in human psychology serve as computational proxies for measuring agency preservation in RLHF evaluation? We employ a multi-criterion validation protocol testing (1) extraction feasibility, (2) effect size magnitude, (3) internal consistency across markers, and (4) cross-dataset replication. The validation approach treats proxy transfer as an empirical hypothesis rather than a theoretical assumption.

## 2. Related Work

**RLHF Methods and Evaluation.** RLHF trains language models by learning reward functions from human preference pairs (Ouyang et al., 2022). The HH-RLHF dataset (Bai et al., 2022) contains 161K preference pairs annotated for helpfulness and harmlessness. Standard benchmarks evaluate response quality and safety but do not measure effects on user agency. Shapira et al. (2026) identify sycophancy (over-agreement with users) as an emergent RLHF property, suggesting potential mechanisms by which preference optimization might affect agency-preserving language patterns.

**Linguistic Markers in Psychology.** Juanchich et al. (2017) demonstrate through controlled experiments that modal verbs and pronoun usage affect perceived autonomy attribution. Biber et al. (1999) document hedging markers as epistemic stance indicators in human corpora. These studies validate markers in human language but do not test transfer to AI-generated text.

**Bidirectional Alignment Framework.** Shen et al. (2024) systematically review 400+ papers and identify two alignment dimensions: AI→Human (integrating human specifications into systems) and Human→AI (preserving human agency). They note the absence of computational operationalization for the Human→AI dimension. This study tests one potential operationalization approach.

## 3. Method

### 3.1 Dataset

The Anthropic HH-RLHF dataset (Bai et al., 2022) contains 169,352 preference pairs: 160,800 in the train split and 8,552 in the test split. Each pair includes a chosen response (preferred by human annotators) and a rejected response to the same conversational context. The matched-pair structure controls for conversation topic, user question, and dialogue history.

### 3.2 Linguistic Marker Operationalization

Three marker types were extracted:

**Modal Verbs (Primary):** Counts of could, might, should, may, would per 100 words, extracted via spaCy v3.5 part-of-speech tagging (TAG=='MD').

**Hedging Markers (Secondary):** Counts of appears, seems, possibly, perhaps, might, likely per 100 words via lexicon matching.

**Alternative-Framing (Secondary):** Counts of phrases including "on the other hand," "alternatively," "another option," "you could also" per 100 words via regex pattern matching.

All counts were normalized to per-100-words frequency to control for response length differences.

### 3.3 Validation Protocol

**Stage 1 (H-E1, Existence):** Tests whether markers can be reliably extracted with sufficient distributional variance. Success criteria: coefficient of variation (CV) > 0.3 and extraction precision > 90%.

**Stage 2 (H-M, Mechanism):** Tests construct validity through four criteria:
1. Effect size: Cohen's d ≥ 0.15 with p < 0.05 (paired t-test)
2. Internal consistency: Cronbach's α > 0.7 across three marker types
3. Directional hypothesis: chosen responses have fewer markers than rejected
4. Cross-split replication: effect replicates in both train and test splits

The threshold d=0.15 was selected to represent a minimally meaningful effect size for practical deployment decisions. Cronbach's α > 0.7 is the standard psychometric threshold for acceptable internal consistency (Nunnally, 1978).

### 3.4 Statistical Analysis

Paired t-tests were conducted on within-pair differences (chosen - rejected) for each marker type. Cohen's d for paired samples was calculated as mean(differences) / SD(differences). Cronbach's alpha was computed across the three marker types treating them as items measuring a latent construct. All analyses were performed using Python with scipy.stats and standard statistical libraries.

### 3.5 Power Analysis

With N=169,352 pairs, the study achieves >0.99 power to detect effects of d=0.15 at α=0.05. The test split alone (N=8,552) provides 0.95 power for the threshold effect size.

## 4. Experimental Setup

Extraction was performed on all 338,704 individual responses (169,352 chosen + 169,352 rejected). A random sample of 100 responses was manually annotated by two independent annotators to validate extraction precision (inter-annotator agreement κ=0.94). Statistical tests were conducted on the full dataset and separately on each data split to assess replication.

## 5. Results

### 5.1 H-E1: Extraction Feasibility

Linguistic markers were successfully extracted with the following distributional properties:

| Marker Type | Mean | SD | CV | Precision |
|-------------|------|----|----|-----------|
| Modal verbs | 2.911 | 2.272 | 0.781 | 100% |
| Hedging | 0.542 | 0.416 | 0.768 | 100% |
| Alternatives | 0.089 | 0.112 | 1.258 | 100% |

Modal verb CV (0.781) exceeded the threshold (0.3) by 161%. Extraction precision was 100% with 98.5% recall. Cross-split consistency was high (train CV=0.783, test CV=0.781, difference=0.002). H-E1 criteria were satisfied.

### 5.2 H-M: Construct Validation

**Effect Size.** Paired t-test results on 169,352 pairs:

| Marker | Chosen Mean | Rejected Mean | Difference | Cohen's d | p-value |
|--------|-------------|---------------|------------|-----------|---------|
| Modal verbs | 2.894 | 2.928 | -0.034 | -0.0181 | <0.001 |
| Hedging | 0.538 | 0.546 | -0.008 | -0.0192 | <0.001 |
| Alternatives | 0.087 | 0.091 | -0.004 | -0.0356 | <0.001 |

All three markers achieved statistical significance (p<0.001) but effect sizes were 76-88% below the threshold (d=0.15). For modal verbs, the observed d=-0.0181 represents 12% of the required threshold. The absolute frequency difference was 0.034 per 100 words (1.2% difference). Direction was consistent with theoretical predictions (chosen < rejected).

**Internal Consistency.** Cronbach's α across the three marker types was 0.42, falling 40% below the acceptable threshold (0.7). Mean inter-item correlation was 0.29, with pairwise correlations ranging from 0.22 to 0.35.

**Cross-Split Replication.** Separate analyses by data split:

| Split | N | Cohen's d | p-value | Passed |
|-------|---|-----------|---------|--------|
| Train | 160,800 | -0.0187 | <0.001 | No |
| Test | 8,552 | -0.0067 | 0.536 | No |

Neither split achieved the effect size threshold. The test split did not reach statistical significance despite 95% power to detect d=0.15 effects.

**Summary.** All four H-M criteria failed:
- Effect size: d=-0.018 vs. required d≥0.15 (88% below threshold)
- Internal consistency: α=0.42 vs. required α>0.7 (40% below threshold)
- Replication: 0/2 splits passed
- Practical significance: 1.2% frequency difference

## 6. Discussion

### 6.1 Interpretation of Findings

The study demonstrates a separation between measurement feasibility and construct validity. Linguistic markers were reliably extractable (H-E1 validated), but they did not validly measure agency preservation (H-M refuted across all criteria).

The low internal consistency (α=0.42) and weak inter-item correlations (r=0.22-0.35) suggest the three marker types tap different constructs rather than converging on a unified agency dimension. The consistent directional pattern (chosen < rejected) with negligible magnitude indicates potential confounding: chosen responses may be slightly more direct or concise for reasons related to response quality rather than agency preservation.

### 6.2 Statistical Significance and Effect Size

With N=169,352 pairs, the study demonstrates that p<0.001 can coexist with practically negligible effects (d=-0.018). The massive sample size provides >0.99 power to detect even trivial differences, making p-values uninformative for practical significance. The failure of the effect to replicate in the test split (d=-0.007, p=0.536), despite adequate power (0.95 for d=0.15), indicates that the train-split significance may be a statistical artifact of sample size rather than a robust phenomenon.

### 6.3 Cross-Domain Transfer

The findings indicate that linguistic markers validated in human psychology (Juanchich et al., 2017) do not automatically transfer to AI-generated text in RLHF contexts. Human-authored language involves intentional communication where speakers deliberately use modal verbs to convey autonomy. AI-generated responses are produced through language model sampling optimized for preference signals, which may involve different generative processes.

### 6.4 Limitations

Results are specific to the HH-RLHF dataset (English, helpfulness-focused conversations). Generalization to other RLHF datasets, languages, or alignment methods was not tested. The study examined three specific marker types; alternative linguistic features were not explored. The analysis was conducted at the response level without stratification by conversation type or context, which may mask context-dependent patterns.

### 6.5 Implications

The negative result does not invalidate the bidirectional alignment framework (Shen et al., 2024) or the importance of agency preservation. Rather, it demonstrates that computational operationalization cannot assume proxy validity based on cross-domain analogy. Future efforts to develop agency metrics may require: (1) direct user studies correlating linguistic features with human-annotated agency perception, (2) validation of alternative linguistic or behavioral features through multi-criterion testing, or (3) methods that move beyond linguistic proxies to behavioral or interaction-based measures.

## 7. Conclusion

This study tested whether linguistic agency markers validated in human psychology could serve as computational proxies for measuring agency preservation in RLHF evaluation. Analyzing 169,352 preference pairs from the HH-RLHF dataset, we found that while markers are reliably extractable (precision=100%, CV=0.781), they fail comprehensive construct validation: effect sizes are 88% below meaningful thresholds (d=-0.018 vs. required d≥0.15 despite p<0.001), internal consistency is 40% below acceptable levels (α=0.42 vs. required α>0.7), and cross-split replication fails (0/2 splits passed).

The findings establish three contributions: (1) proxy validity requires multi-criterion empirical validation rather than theoretical assumption based on face validity, (2) statistical significance (p<0.001) achieved through large samples (N=169K) does not guarantee practical relevance without effect size thresholds, and (3) measurement feasibility (reliable extraction) is distinct from construct validity (measuring the intended construct).

The negative result prevents premature deployment of invalid automated metrics while establishing validation requirements for future computational operationalization of bidirectional alignment. Until validated proxies exist, agency preservation monitoring requires direct user studies or alternative measurement approaches with demonstrated construct validity.

## References

Bai, Y., et al. (2022). Training a helpful and harmless assistant with reinforcement learning from human feedback. Anthropic.

Biber, D., et al. (1999). Longman Grammar of Spoken and Written English. Longman.

Juanchich, M., Gourdon-Kanhukamwe, A., & Sirota, M. (2017). "I am uncertain" vs "It is uncertain": How linguistic markers of the uncertainty source affect uncertainty communication. Judgment and Decision Making, 12(5), 445-465.

Nunnally, J. C. (1978). Psychometric Theory (2nd ed.). McGraw-Hill.

Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. NeurIPS.

Shapira, N., Benade, G., & Procaccia, A. D. (2026). How RLHF amplifies sycophancy. arXiv:2602.01002.

Shen, X., et al. (2024). Towards bidirectional human-AI alignment: A systematic review. arXiv preprint.
