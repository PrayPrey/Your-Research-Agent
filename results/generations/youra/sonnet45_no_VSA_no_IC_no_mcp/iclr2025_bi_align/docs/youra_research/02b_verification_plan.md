# Phase 2B: Verification Plan
## Hypothesis: Bidirectional Alignment via Behavioral Coupling

**Generated**: 2026-08-25T04:25:00+00:00  
**Hypothesis ID**: H-BiAlign-v1  
**Phase 2A Source**: 03_refinement.md  

---

## Overview

The hypothesis claims bidirectional alignment emerges from coupling (correlation) between user learning rate and AI policy responsiveness, measured on multi-turn conversations. Three sub-hypotheses test: (1) user learning exists (reformulation slope), (2) AI responsiveness exists (diversity correlation), (3) coupling matters beyond individual metrics.

**Dataset**: HH-RLHF (Anthropic Helpful-Harmless RLHF, 161k conversations, multi-turn with helpfulness ratings)  
**Minimum Conversation Length**: ≥5 turns (required for slope estimation)

---

## Sub-Hypothesis 1 (h-e1): User Learning via Reformulation Slope

### Type
EXISTENCE

### Claim
Conversations with negative reformulation slope (user learning) have higher task success rates than flat/positive slope conversations, controlling for conversation length and engagement.

### Test Protocol

**Data Requirements**:
- Multi-turn conversations ≥5 turns from HH-RLHF
- User queries and AI responses per turn
- Outcome labels (successful vs. abandoned)

**Measurement Steps**:
1. Extract query pairs (turn_i, turn_i+1) per conversation
2. Compute reformulation rate per turn:
   - Semantic similarity: SBERT cosine similarity between consecutive queries
   - Syntactic distance: normalized edit distance
   - Reformulation detected if: SBERT similarity > 0.7 AND edit distance > 0.3
3. Compute reformulation slope:
   - Linear regression: reformulation_rate ~ turn_index
   - Extract slope coefficient (negative = decreasing reformulation = learning)
4. Stratify by outcome: test on successful conversations only (controls engagement decay)

**Statistical Test**:
- Logistic regression: `success ~ reformulation_slope + turn_count`
- Hypothesis: negative coefficient for reformulation_slope
- Success criterion: coefficient < 0, p < 0.05, OR > 1.2

**Falsification**:
- Coefficient NOT negative OR p ≥ 0.05 → reformulation slope does not measure learning
- Slope distribution centered at zero → no systematic learning pattern

**Data Collection**:
- No external API calls required
- Computed from HH-RLHF static dataset
- SBERT embeddings via sentence-transformers library (offline)

**Estimated Effort**: 2-3 days (data prep, reformulation detection, regression)

---

## Sub-Hypothesis 2 (h-e2): AI Responsiveness via Diversity Correlation

### Type
EXISTENCE

### Claim
AI response diversity correlates with user query diversity (Pearson r > 0.4) in well-aligned conversations (helpfulness > median).

### Test Protocol

**Data Requirements**:
- Same HH-RLHF dataset as h-e1
- Helpfulness ratings to stratify by alignment quality

**Measurement Steps**:
1. Compute query diversity per conversation:
   - Extract all user queries in conversation
   - Compute distinct-1: unique unigrams / total unigrams
2. Compute response diversity per conversation:
   - Extract all AI responses in conversation
   - Compute distinct-1: unique unigrams / total unigrams
3. Filter conversations: helpfulness rating > median (well-aligned subset)
4. Compute Pearson correlation between query diversity and response diversity

**Statistical Test**:
- Pearson correlation on (query_diversity, response_diversity) pairs
- Success criterion: r > 0.4 AND p < 0.05

**Falsification**:
- r ≤ 0.4 OR p ≥ 0.05 → AI policy not responsive to query diversity
- Negative correlation → AI uniformity increases with query diversity (anti-responsive)

**Sensitivity Analysis**:
- Test threshold robustness: correlation across r ∈ [0.3, 0.5]
- Test stratification: correlation on helpfulness quartiles (Q1, Q2, Q3, Q4)

**Data Collection**:
- No external API calls required
- Computed from HH-RLHF static dataset
- Vocabulary-based (no embeddings needed)

**Estimated Effort**: 1-2 days (diversity computation, correlation analysis)

---

## Sub-Hypothesis 3 (h-m1): Coupling Beyond Individual Metrics

### Type
MECHANISM

### Dependencies
Requires h-e1 and h-e2 to pass (need reformulation slope + diversity correlation as covariates)

### Claim
Conversations where BOTH user learning (h-e1) AND AI responsiveness (h-e2) hold have higher helpfulness ratings than conversations where only one holds. Coupling strength (correlation between reformulation slope and diversity correlation) predicts helpfulness beyond individual metrics.

### Test Protocol

**Data Requirements**:
- Same HH-RLHF dataset
- Reformulation slope (from h-e1)
- Diversity correlation (from h-e2)
- Helpfulness ratings (dependent variable)

**Measurement Steps**:
1. Compute coupling strength per conversation:
   - Coupling = Pearson(reformulation_slope, diversity_correlation)
   - Range: [-1, 1]
2. Build regression model:
   - `helpfulness ~ coupling_strength + reformulation_slope + diversity_correlation + turn_count`
3. Test coupling coefficient significance

**Statistical Test**:
- Linear regression with coupling term
- Hypothesis: coupling_strength coefficient > 0
- Success criterion: coefficient > 0, p < 0.05, controlling for individual metrics

**Falsification**:
- Coupling coefficient NOT significant when controlling for components → alignment is additive (sum), not multiplicative (coupling)
- Negative coefficient → coupling anti-predicts helpfulness

**Baseline Comparisons**:
1. Individual metrics only: `helpfulness ~ reformulation_slope + diversity_correlation` (no coupling)
2. Length only: `helpfulness ~ turn_count`
3. Random baseline: permute helpfulness ratings, verify coupling correlation not spurious

**Controlled Variables**:
- Conversation length (turn_count covariate)
- User engagement decay (stratify by outcome if needed)

**Data Collection**:
- No external API calls required
- All metrics computed from HH-RLHF static dataset

**Estimated Effort**: 2-3 days (coupling computation, regression, baseline comparisons)

---

## Verification Workflow

### Phase 1: Data Preparation (Parallel)
- Load HH-RLHF dataset
- Filter conversations ≥5 turns
- Extract queries, responses, metadata (helpfulness, outcome, length)

### Phase 2: h-e1 and h-e2 (Parallel)
- **h-e1**: Compute reformulation slopes, test learning hypothesis
- **h-e2**: Compute diversity correlations, test responsiveness hypothesis

### Phase 3: h-m1 (Sequential, after h-e1 + h-e2)
- Compute coupling strength
- Run regression with coupling term
- Compare to baselines

### Phase 4: Sensitivity Analysis
- Threshold sensitivity (reformulation detection, correlation thresholds)
- Stratification robustness (helpfulness quartiles, conversation length bins)

---

## Success Criteria Summary

| Sub-Hypothesis | Type | Success Criterion | Falsification Criterion |
|----------------|------|-------------------|------------------------|
| h-e1 | EXISTENCE | Reformulation slope coefficient < 0, p < 0.05, OR > 1.2 | Coefficient ≥ 0 OR p ≥ 0.05 |
| h-e2 | EXISTENCE | Diversity correlation r > 0.4, p < 0.05 | r ≤ 0.4 OR p ≥ 0.05 |
| h-m1 | MECHANISM | Coupling coefficient > 0, p < 0.05 (controlling for components) | Coefficient NOT significant OR ≤ 0 |

**Overall Verification**: Hypothesis VALIDATED if all three sub-hypotheses pass. Hypothesis REFUTED if any existence claim (h-e1, h-e2) fails. Hypothesis WEAKENED if mechanism (h-m1) fails but existence claims hold (alignment is additive, not coupling-based).

---

## Data Collection Plan

**Primary Dataset**: HH-RLHF (Anthropic Helpful-Harmless RLHF)
- **Source**: https://huggingface.co/datasets/Anthropic/hh-rlhf
- **Size**: 161k conversations (train + test splits)
- **Structure**: Multi-turn conversations with helpfulness/harmlessness ratings
- **Availability**: Public, no API required

**Required Tools**:
- SBERT embeddings: `sentence-transformers` library (offline, no API)
- Edit distance: Python `difflib` or `Levenshtein` library
- Statistical analysis: `scipy.stats`, `statsmodels` (linear/logistic regression)

**No External Dependencies**:
- No OpenAI/Anthropic/Cohere API calls required
- All computation on static dataset
- Reproducible offline

---

## Assumptions to Verify

1. **A1 (Reformulation = Learning)**: Test by stratifying on outcome (successful convos only)
2. **A2 (Paraphrase Detection Validity)**: Dual detection (semantic + syntactic) controls topic continuity confound
3. **A3 (Diversity = Responsiveness)**: Response diversity conditioned on query diversity isolates responsiveness
4. **A4 (Statistical Power)**: Bayesian slope estimation if power weak on short conversations
5. **A5 (Threshold Validity)**: Sensitivity analysis across threshold ranges validates robustness

---

## Expected Timeline

- **Data Prep**: 1 day
- **h-e1 (User Learning)**: 2-3 days
- **h-e2 (AI Responsiveness)**: 1-2 days
- **h-m1 (Coupling Mechanism)**: 2-3 days
- **Sensitivity Analysis**: 1-2 days

**Total**: 7-11 days (1.5-2 weeks)

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Short conversations (median ~3 turns) | Filter ≥5 turns, test on longer datasets (Anthropic logs), use Bayesian slope estimation |
| Reformulation detection ambiguity | Dual detection (SBERT + edit distance), manual validation on sample |
| Threshold sensitivity | Sensitivity analysis across ranges (correlation 0.3-0.5, slope -0.05 to -0.2) |
| Observational study (no causation) | Acknowledge limitation, suggest future intervention study (A/B test with coupling-optimized AI) |

---

## Open Questions for Experimentation

1. What coupling strength threshold constitutes "good" alignment? (Empirical calibration)
2. Do coupling patterns generalize across model families (GPT vs. Claude vs. Llama)?
3. Can coupling metric predict alignment degradation over time in deployed systems?

---

*Generated for Phase 2B Verification Planning*  
*Next Step: Phase 3 Experiment Design (after verification protocols finalized)*
