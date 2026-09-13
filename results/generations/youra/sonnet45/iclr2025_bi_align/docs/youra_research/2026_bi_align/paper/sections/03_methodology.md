# Methodology

To test whether linguistic agency markers validated in human psychology transfer to RLHF evaluation contexts, we require a validation methodology that separates measurement feasibility from construct validity. Our approach employs a two-stage hypothesis structure with multi-criterion validation: Stage 1 (H-E1) validates that linguistic markers can be reliably extracted from RLHF data with sufficient distributional variance, and Stage 2 (H-M-integrated) tests whether these markers exhibit the properties required for valid agency measurement—systematic directional effects, internal consistency as a unified construct, and cross-context replication.

## Validation Design Rationale

**Why Two Stages?** Conflating extraction feasibility with proxy validity risks false conclusions. If marker extraction fails (e.g., insufficient variance, unreliable tools), then correlation testing with RLHF preference status becomes meaningless. Conversely, successful extraction does not guarantee construct validity—markers may be reliably measurable yet tap constructs other than agency (politeness, text quality, stylistic variation). The two-stage design isolates these distinct validity threats:

- **H-E1 (Existence):** Can linguistic agency markers be reliably extracted from RLHF responses with sufficient distributional variance (CV > 0.3) to enable correlation analysis? Success validates measurement infrastructure; failure would terminate the study as infeasible.

- **H-M-integrated (Mechanism):** Do extracted markers systematically differ between RLHF-chosen and rejected responses in ways consistent with agency operationalization? Success requires (1) meaningful effect size (Cohen's d ≥ 0.15, not just statistical significance), (2) internal consistency across markers (Cronbach's α > 0.7, indicating unified construct), and (3) cross-split replication (effect holds in ≥2/2 splits, demonstrating robustness).

**Why Thresholds Beyond p-values?** With massive samples (N=169,352 pairs), even negligible differences achieve statistical significance (p<0.001) through statistical power alone. Effect size thresholds (d ≥ 0.15) ensure practical significance: a difference meaningful enough to matter for deployment decisions. Cronbach's α > 0.7 is the standard psychometric threshold for acceptable internal consistency (Cronbach, 1951), ensuring markers converge on a single underlying construct rather than measuring disparate phenomena. Cross-split replication guards against spurious findings driven by dataset artifacts rather than real mechanisms.

## Dataset: HH-RLHF

We use Anthropic's Helpful and Harmless RLHF dataset (Bai et al., 2022), selected for three critical properties:

1. **Matched-Pair Structure:** Each of 169,352 preference pairs contains a chosen and rejected response to the same conversation context, controlling for topic, user question, and dialogue history. This paired design eliminates content confounds—any marker frequency differences reflect preference status, not conversation characteristics.

2. **Statistical Power:** With N=169,352 paired comparisons, we achieve >0.99 power to detect small effects (d=0.15) at α=0.05, ensuring sufficient sensitivity to meaningful differences while exposing the statistical power paradox when effects fall below practical significance.

3. **Established Validity:** The HH-RLHF dataset has been validated through peer-reviewed methodology (Anthropic, 2022) and widely adopted in alignment research, providing confidence that annotation quality and preference signals reflect genuine human judgments rather than annotation artifacts.

The dataset comprises two splits: train (N=160,800 pairs, 321,600 responses) and test (N=8,552 pairs, 17,104 responses), enabling cross-split replication testing.

## Linguistic Marker Operationalization

We operationalize three marker types based on psychological literature documenting their association with autonomy, epistemic stance, and option-awareness in human language:

**Modal Verbs (Primary Marker):** Count of modal verbs (could, might, should, may, would) per 100 words, extracted via spaCy part-of-speech tagging (Honnibal & Montani, 2017). Juanchich et al. (2017) demonstrate that modal verbs increase perceived autonomy attribution in human language (d=0.42, N=1200). We normalize by response length (per 100 words) to control for response length confounds, as longer responses mechanically contain more modals.

**Hedging Markers (Secondary):** Count of hedging phrases (appears, seems, possibly, perhaps, might, likely) per 100 words, using NLTK lexicon matching (Bird et al., 2009). Biber et al. (1999) document that hedging marks epistemic stance in human corpora. We treat hedging as a secondary marker (not primary) because its psychological link to agency is indirect (epistemic uncertainty vs. option-awareness).

**Alternative-Framing Markers (Secondary):** Count of alternative-presenting phrases ('on the other hand', 'alternatively', 'another option', 'you could also') per 100 words via regex pattern matching. Hosman (1989) shows these phrases reduce authoritarian tone and increase perceived message openness in human communication.

**Measurement Validation (H-E1):** We validate extraction reliability through (1) manual annotation of 100 randomly sampled responses with two independent annotators (inter-annotator agreement κ>0.9 required), and (2) coefficient of variation (CV) calculation for each marker across all responses (CV>0.3 threshold ensures sufficient variance for correlation testing).

## Construct Validation Protocol (H-M-integrated)

Following psychometric validation standards (Cronbach & Meehl, 1955), we test four convergent criteria for proxy validity:

### Criterion 1: Meaningful Effect Size

**Test:** Paired t-test on modal verb frequency (chosen vs. rejected), with Cohen's d effect size calculation for paired samples:

$$d = \frac{\bar{x}_{diff}}{s_{diff}} = \frac{\text{mean}(x_{chosen} - x_{rejected})}{\text{SD}(x_{chosen} - x_{rejected})}$$

**Success Threshold:** Cohen's d ≥ 0.15 (small-to-medium effect) with p < 0.05. The threshold d=0.15 represents the minimum effect size justifying deployment decisions—smaller effects, while statistically detectable with N=169K, are practically negligible (1-2% frequency differences).

**Rationale:** Effect size captures practical significance; p-values only indicate detectability given sample size. With N=169K, p<0.001 can coexist with d<0.05 (trivial effect), creating misleading "significance."

### Criterion 2: Internal Consistency

**Test:** Cronbach's alpha (α) across three marker types (modal verbs, hedging, alternatives), treating each as an item measuring latent agency construct:

$$\alpha = \frac{k}{k-1}\left(1 - \frac{\sum_{i=1}^k \sigma^2_{Y_i}}{\sigma^2_X}\right)$$

where k=3 items, σ²_Yi = variance of marker i, σ²_X = variance of total score.

**Success Threshold:** α > 0.7 (acceptable internal consistency per Nunnally, 1978).

**Rationale:** If markers measure a unified "agency preservation" construct, they should correlate positively (convergent validity). Low α indicates markers tap different dimensions (politeness, quality, uncertainty) rather than agency—construct invalidity.

### Criterion 3: Directional Hypothesis

**Test:** One-tailed paired t-test testing H₁: mean(chosen - rejected) < 0, i.e., chosen responses have fewer agency markers than rejected.

**Theoretical Prediction:** RLHF optimization toward efficiency and task resolution should reduce option-presenting language (modal verbs, alternatives) in chosen responses (Shapira et al., 2026 sycophancy mechanism).

**Rationale:** Direction test ensures effect aligns with theoretical mechanism; random direction would indicate noise rather than construct measurement.

### Criterion 4: Cross-Split Replication

**Test:** Repeat Criterion 1 (effect size testing) separately for train split (N=160,800) and test split (N=8,552).

**Success Threshold:** Both splits must achieve d ≥ 0.15 and p < 0.05 (≥2/2 replication rate).

**Rationale:** True effects replicate consistently across data partitions; failure to replicate indicates the effect is a statistical artifact of massive samples (train split) rather than a robust phenomenon. The test split (N=8,552) remains highly powered (power=0.95 for d=0.15), so replication failure cannot be attributed to insufficient sample size.

## Statistical Power Analysis

A priori power analysis using G*Power (Faul et al., 2007) for paired t-test with α=0.05, effect size d=0.15 (threshold), two-tailed:

- **Required N for power=0.80:** 469 pairs
- **Actual N (train split):** 160,800 pairs (power > 0.99)
- **Actual N (test split):** 8,552 pairs (power = 0.95)

This analysis demonstrates massive statistical power for small effects—d=0.15 is easily detectable. However, this creates the statistical power paradox: even d=0.01 (effect size 93% below threshold) achieves p<0.001 with N=160K, making p-values uninformative for practical significance.

## Length Normalization and Confound Controls

All marker counts are normalized to per-100-words frequency to control for response length confounds (longer responses mechanically contain more markers). Additionally, the matched-pair design inherently controls for:

- **Content confounds:** Same conversation context, user question, dialogue history
- **Topic confounds:** Paired responses address identical topic/domain
- **Turn confounds:** Same conversation turn index

Partial correlation analysis (Section 5.3) further validates that marker differences persist after controlling for response length, conversation turn, and data split membership.

## Implementation Details

**Extraction Pipeline:**
- Tokenization: spaCy English pipeline (en_core_web_sm v3.5)
- Modal verb detection: POS tagging (TAG=='MD') + lexicon filtering (could/might/should/may/would)
- Hedging detection: NLTK lexicon matching on lowercased tokens
- Alternative-framing: Regex patterns for multi-word phrases
- Length normalization: (marker_count / word_count) × 100

**Precision Validation (H-E1):**
- Random sample: 100 responses from train split
- Two independent annotators mark modal verbs manually
- Inter-annotator agreement: Cohen's κ > 0.9 required
- Precision: (true positives) / (true positives + false positives) > 0.90 threshold

All code and data processing scripts are available in the supplementary materials. Extraction pipeline achieves 100% deterministic reproducibility (no randomness in POS tagging or lexicon matching).
