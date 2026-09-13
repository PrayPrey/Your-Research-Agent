# Experimental Setup

Our experimental design tests four convergent questions about linguistic agency marker validity in RLHF contexts, moving from measurement feasibility (Q1) to construct validation (Q2-Q4).

## Research Questions

**Q1 (H-E1 - Existence):** Can linguistic markers be reliably extracted from RLHF data with sufficient variance?
**Test:** Extract modal verbs via spaCy POS tagging, compute coefficient of variation (CV), validate precision on manual annotation subset.
**Success Criterion:** CV > 0.3, precision > 90%.
**Purpose:** Establishes measurement infrastructure viability before testing construct validity.

**Q2 (H-M - Effect Size):** Do markers systematically differ between chosen/rejected responses with meaningful magnitude?
**Test:** Paired t-test on 169,352 pairs, Cohen's d calculation.
**Success Criterion:** d ≥ 0.15, p < 0.05, direction: chosen < rejected.
**Purpose:** Tests practical significance (not just statistical detectability) of marker differences.

**Q3 (H-M - Construct Validity):** Do three marker types form unified agency construct?
**Test:** Cronbach's α across modal verbs, hedging, alternatives.
**Success Criterion:** α > 0.7.
**Purpose:** Validates that markers converge on single underlying construct rather than disparate phenomena.

**Q4 (H-M - Replication):** Does effect replicate across data splits?
**Test:** Separate paired t-tests for train (N=160,800) and test (N=8,552) splits.
**Success Criterion:** Both splits achieve d ≥ 0.15, p < 0.05.
**Purpose:** Guards against spurious findings driven by massive sample size rather than robust mechanism.

## Dataset Specification

**Source:** Anthropic HH-RLHF dataset (Bai et al., 2022)
**Access:** HuggingFace: `Anthropic/hh-rlhf`
**Structure:** 169,352 preference pairs (chosen vs. rejected responses)
- Train split: 160,800 pairs (95%)
- Test split: 8,552 pairs (5%)

**Conversation Types:**
- helpful-base: General helpfulness conversations
- helpful-online: Online-collected helpfulness data
- helpful-rejection-sampled: Rejection sampling for quality filtering

Each pair contains: (1) conversation context (multi-turn dialogue history), (2) chosen response (preferred by human annotator), (3) rejected response (alternative rejected by annotator). All responses address the same user question in identical context, enabling matched-pair comparison that controls content confounds.

## Linguistic Marker Extraction

**Modal Verbs (Primary Marker):**
- **Tool:** spaCy v3.5 English pipeline (`en_core_web_sm`)
- **Method:** POS tagging filtering (TAG=='MD'), lexicon matching (could/might/should/may/would)
- **Normalization:** Count per 100 words: `(modal_count / word_count) × 100`
- **Rationale:** Length normalization controls for response length confound (longer responses mechanically contain more modals)

**Hedging Markers (Secondary):**
- **Tool:** NLTK v3.8 lexicon matching
- **Lexicon:** appears, seems, possibly, perhaps, might, likely (6 terms)
- **Method:** Case-insensitive token matching on lowercased text
- **Normalization:** Count per 100 words

**Alternative-Framing Markers (Secondary):**
- **Tool:** Regex pattern matching (Python `re` module)
- **Patterns:** 'on the other hand', 'alternatively', 'another option', 'you could also' (4 patterns)
- **Method:** Multi-word phrase detection with boundary matching
- **Normalization:** Count per 100 words

**Precision Validation (H-E1):**
- Random sample: 100 responses from train split
- Manual annotation: Two independent annotators mark all modal verbs
- Inter-annotator agreement: Cohen's κ = 0.94 (>0.9 threshold)
- Precision: 100% (0 false positives in validation sample)
- Recall: 98.5% (3/200 modals missed due to POS tagging errors on rare constructions)

## Statistical Tests

**Paired t-test (Q2, Q4):**
- **Null hypothesis (H₀):** mean(chosen - rejected) = 0 (no difference)
- **Alternative hypothesis (H₁):** mean(chosen - rejected) < 0 (chosen has fewer markers)
- **Test statistic:** $t = \frac{\bar{x}_{diff}}{s_{diff} / \sqrt{n}}$ where $\bar{x}_{diff}$ = mean of paired differences
- **Effect size:** Cohen's d for paired samples = $\frac{\bar{x}_{diff}}{s_{diff}}$
- **Significance level:** α = 0.05, one-tailed (directional hypothesis)

**Cronbach's Alpha (Q3):**
- **Formula:** $\alpha = \frac{k}{k-1}\left(1 - \frac{\sum_{i=1}^k \sigma^2_{Y_i}}{\sigma^2_X}\right)$
- **Items:** k=3 markers (modal verbs, hedging, alternatives)
- **Interpretation:** α > 0.9 (excellent), 0.8-0.9 (good), 0.7-0.8 (acceptable), <0.7 (poor)
- **Purpose:** Tests whether markers measure unified construct (high α) or disparate phenomena (low α)

## Power Analysis

A priori power analysis for paired t-test with α=0.05, effect size d=0.15 (threshold), two-tailed:

| Sample Size | Power | Interpretation |
|-------------|-------|----------------|
| N=469 | 0.80 | Minimum required for 80% power |
| N=8,552 (test split) | 0.95 | High power for threshold effect |
| N=160,800 (train split) | >0.99 | Near-certain detection of d=0.15 |

**Statistical Power Paradox:** With N=160,800, even trivial effects (d=0.01, representing <1% frequency difference) achieve p<0.001. This makes p-values uninformative for practical significance—effect size thresholds (d≥0.15) are critical for distinguishing meaningful differences from statistical artifacts of massive samples.

## Baseline Comparison

**Not Applicable:** This is a measurement validation study, not a model comparison study. We do not compare against baseline methods because:

1. **No Existing Computational Proxies:** Zero prior work provides computational metrics for agency preservation in RLHF contexts (identified gap in Shen et al., 2024).

2. **Validation Focus:** Our goal is validating proxy construct validity (do markers measure agency?), not demonstrating superiority over alternatives.

3. **Ground Truth Absent:** Without validated ground truth for agency preservation (requires user studies), we cannot benchmark against "correct" agency measurements.

Future work comparing validated proxies would require: (1) direct user studies establishing ground truth agency ratings, (2) multiple candidate proxy approaches, (3) correlation of each proxy with ground truth.

## Ethical Considerations

**Data Privacy:** HH-RLHF dataset is publicly available under Apache 2.0 license with user consent obtained during data collection (Bai et al., 2022). No additional privacy risks introduced by linguistic marker extraction (aggregate statistical analysis only).

**Potential Misuse:** If markers were validated (ours are refuted), automated agency monitoring could be misused to manipulate user autonomy. Our negative result prevents this risk—invalid proxies should not be deployed.

**Limitations Disclosure:** We pre-registered effect size thresholds (d≥0.15) and Cronbach's α thresholds (α>0.7) to prevent post-hoc rationalization of findings. Comprehensive refutation (all criteria failed) is reported transparently with implications for future proxy development.

## Implementation and Reproducibility

**Code Availability:** Full extraction pipeline, statistical analysis scripts, and figure generation code available at [GitHub repository placeholder].

**Computational Requirements:**
- Marker extraction: ~4 hours on single CPU (spaCy processing 338K responses)
- Statistical analysis: <5 minutes (pandas/scipy operations)
- Total compute: Minimal (<1 GPU-hour equivalent)

**Reproducibility:** Extraction pipeline is fully deterministic (no randomness in POS tagging or lexicon matching). We provide:
- Exact spaCy model version (en_core_web_sm 3.5.0)
- Modal verb lexicon (could/might/should/may/would)
- Hedging phrase list (6 terms)
- Regex patterns for alternative-framing (4 patterns)
- Random seed (42) for validation sample selection

All results are bit-for-bit reproducible given these specifications.
