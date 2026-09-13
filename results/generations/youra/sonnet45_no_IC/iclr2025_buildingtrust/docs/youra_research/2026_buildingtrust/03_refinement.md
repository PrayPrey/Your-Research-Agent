# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-07-12T06:30:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap1
- **Gap Title**: Empirical Cross-Dimensional Correlation Datasets
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 criteria passed with concrete evidence; all personas participated; outcome-independent publishability ensures contribution

### Key Insights

1. **Evaluation logs as latent datasets** (Exchange 1 - Dr. Nova): Existing trustworthiness frameworks (TrustVis, MLLMGuard) already perform multi-dimensional evaluations on the same outputs but discard correlation data. The gap isn't technical infrastructure — it's conceptual. Researchers silo their evaluations.

2. **Synchronized measurement trinity** (Exchange 2 - Prof. Vera): For valid correlation analysis, we need: (1) EXACT same model checkpoint, (2) EXACT same inputs/prompts, (3) EXACT same generation parameters. Sequential perturbation testing (e.g., adversarial robustness AFTER safety) doesn't measure natural-input correlations.

3. **Outcome-independent publishability** (Exchange 12 - Dr. Ally): Three mutually exclusive hypotheses (independence, positive coupling, negative coupling) guarantee publishability regardless of results. Independence (|r|<0.2) is a valid finding, not a failure — it means dimensions are orthogonal and must be evaluated separately.

4. **Feasibility through output-based metrics** (Exchange 14 - Prof. Pax): White-box methods (attention, gradients) limit feasibility. Output-based metrics (accuracy, paraphrase consistency, lexical bias) work universally across API and open-source models.

### Breakthrough Moments

1. **Exchange 1**: Dr. Nova's insight that evaluation logs are synchronized multi-dimensional datasets in disguise — TrustVis runs AutoDAN AND safety evaluations on the SAME outputs, MLLMGuard evaluates 5 dimensions on the same responses. The correlation data already exists, just not analyzed.

2. **Exchange 12**: Dr. Ally's synthesis of three mutually exclusive outcomes (independence, positive coupling, negative coupling) with explicit thresholds, ensuring publishability regardless of empirical results. Transformed potential "negative result" into legitimate scientific contribution.

3. **Exchange 13**: Prof. Vera's complete methodological specification with preregistered analytical plan, preventing p-hacking and establishing falsification criteria via 95% confidence intervals.

---

## Final Hypothesis

### Title
Cross-Dimensional Trustworthiness Correlations Under Synchronized Evaluation

### Hypothesis ID
H-TrustCorr-v1

### Core Claim

Under synchronized evaluation (same model checkpoint, same prompts, same generation parameters), if trustworthiness dimensions (reliability, robustness, fairness) are measured on the same LLM outputs, then measurable correlations emerge following one of three patterns: **independence** (|r|<0.2), **positive coupling** (r>0.3), or **negative coupling** (r<-0.3), because dimensions share training dynamics, architectural constraints, or optimization trade-offs.

### Mechanism

**Three causal pathways:**

1. **Shared training dynamics**: Pre-training on internet text creates correlations between factual correctness (reliability) and consistent retrieval (robustness) for memorized content. Factual prompts show stronger coupling because facts are either memorized or not.

2. **Alignment tax**: RLHF fine-tuning prioritizes fairness/safety over factual accuracy, creating negative correlation between fairness and reliability on social-content questions. This empirically validates the "alignment tax" folklore.

3. **Moderation by prompt type**: Factual prompts show stronger reliability-robustness coupling (r>0.4) than reasoning/misinformation prompts (r<0.3) because facts admit single answers while reasoning admits multiple paths.

---

## Predictions

### P1 (Primary): Positive Coupling on Factual Prompts
- **Statement**: Reliability-robustness correlation r>0.3 (p<0.05) on factual prompts subset (n≈400)
- **Test Method**: Pearson correlation test on reliability vs. robustness scores for factual stratum
- **Success Criterion**: Pearson r>0.3, two-tailed p<0.05, 95% CI lower bound >0.2
- **Falsification**: If 95% CI includes or is below 0.2, prediction fails

### P2 (Secondary): Negative Coupling Overall (Alignment Tax)
- **Statement**: Fairness-reliability correlation r<-0.2 (p<0.05) overall across all 817 prompts
- **Test Method**: Pearson correlation test on fairness vs. reliability scores for full dataset
- **Success Criterion**: Pearson r<-0.2, two-tailed p<0.05, 95% CI upper bound <-0.1
- **Falsification**: If 95% CI includes or is above -0.1, prediction fails

### P3 (Secondary): Moderation by Prompt Type
- **Statement**: Correlation magnitude differs between factual vs. misinformation prompts (Fisher z-test p<0.05)
- **Test Method**: Fisher z-test comparing reliability-robustness correlation in factual vs. misinformation strata
- **Success Criterion**: Fisher z-test p<0.05, indicating significant moderation effect
- **Falsification**: If Fisher z-test p≥0.05, moderation prediction fails (correlations homogeneous)

---

## Novelty

### Key Innovation
First systematic measurement of cross-dimensional trustworthiness correlations using synchronized evaluation. Treats evaluation logs as latent correlation datasets — mines existing benchmark traces rather than building new infrastructure.

### Differentiation from Prior Work

**vs. TrustVis (2025)**:
- TrustVis evaluates safety THEN robustness with adversarial perturbations (sequential, perturbed inputs)
- We measure dimensions on SAME natural inputs without perturbation; analyze correlations explicitly

**vs. MLLMGuard (2024)**:
- MLLMGuard reports per-dimension scores (Privacy, Bias, Toxicity, Truthfulness, Legality) separately
- We compute and statistically test correlations between dimensions; provide coupling vs. independence framework

**vs. BOLD (2021)**:
- BOLD focuses on fairness alone across 5 demographic domains
- We augment fairness measurement with reliability/robustness on SAME outputs; cross-dimensional correlation is our focus

---

## Experimental Design

### Dataset
- **Name**: TruthfulQA (817 prompts)
- **Stratification**: Factual (n≈400) vs. Misinformation (n≈400) for moderation test
- **Source**: HuggingFace (truthful_qa/generation)

### Models
- **Llama-2-7B-chat**: Baseline scale
- **Llama-2-13B-chat**: Medium scale
- **Llama-2-70B-chat**: Large scale
- **Rationale**: Same architecture, varying scale; tests scale as moderator

### Dimensions Measured (Output-Based Metrics)

1. **Reliability**: Accuracy against TruthfulQA ground truth
   - Metric: GPT-4-as-judge scoring (validated on n=100 sample, target ≥90% agreement)
   - Range: [0, 1] (0=incorrect, 1=correct)

2. **Robustness**: Paraphrase consistency
   - Metric: Sentence-BERT cosine similarity between original and 3 back-translated paraphrases (English→French→English)
   - Range: [0, 1] (higher = more consistent)

3. **Fairness**: Demographic bias absence
   - Metric: HONEST lexical bias score on demographic-augmented prompts ('A Black doctor...' vs. 'An Asian doctor...')
   - Range: [0, 1] (higher = fairer, less stereotype prevalence)

### Generation Parameters (Controlled)
- Temperature: 0.7
- Top-p: 0.9
- Max tokens: 256
- Seed: Fixed per prompt (42, 43, 44 for paraphrases)

### Analytical Plan (Preregistered)

1. Compute Pearson correlations for each dimension pair (reliability-robustness, reliability-fairness, robustness-fairness) per model
2. Test correlations against r=0 (two-tailed, α=0.05)
3. Classify outcomes:
   - Independence: |r|<0.2
   - Weak coupling: 0.2≤|r|<0.3
   - Moderate coupling: 0.3≤|r|<0.5
   - Strong coupling: |r|≥0.5
4. Test moderation: Fisher z-test comparing correlations between factual vs. misinformation strata (α=0.05)
5. Permutation test (n=1000 shuffles) to confirm correlations exceed chance

### Sample Size & Power
- **Total**: 817 prompts × 3 models = 2,451 data points
- **Power**: 80% to detect r≥0.18 at α=0.05 (adequate for predictions r>0.3 or r<-0.2)
- **Stratified**: n≈400 per stratum (factual, misinformation) provides 80% power for r≥0.3 per stratum

---

## Limitations

### Methodological
1. **GPT-4-as-judge dependency**: External model introduces potential bias; requires validation against human ground truth (target ≥90% agreement on n=100 sample)

2. **Fairness metric floor effect**: TruthfulQA questions don't naturally involve social groups. Demographic augmentation is a workaround that may introduce artificial bias signal. Pilot study (n=50) needed to confirm HONEST score variance ≥0.2.

3. **Back-translation semantic preservation**: English→French→English may not cover full linguistic variation space. Pilot study (n=20) with expert review needed to validate semantic preservation.

### Generalization
1. **Architecture-specific**: Results limited to Llama-2 family. Correlation patterns may differ for GPT, Claude, Gemini architectures.

2. **Language-specific**: English-only study. Cross-lingual correlations may differ.

3. **Benchmark-specific**: TruthfulQA focus limits generalization to other trustworthiness benchmarks (e.g., AdvGLUE robustness, BBQ bias).

### Scale Confounding
- Llama-2-70B may show different correlation patterns purely due to scale, not architectural principles. Mitigation: report correlations separately per model size, test generalization via meta-analysis.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria passed with concrete evidence |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (concerns mitigated with validation plans) |
| **Outcome-Independent Publishability** | Yes (independence, coupling, trade-offs all contribute) |
| **Feasibility** | Moderate (requires metric validation but technically doable) |

---

## Next Steps (Phase 2B)

1. **Metric Validation** (pre-experiment pilots):
   - GPT-4-as-judge: Validate on n=100 TruthfulQA samples with expert annotations
   - HONEST score: Pilot on n=50 demographic-augmented prompts, confirm variance ≥0.2
   - Back-translation: Pilot on n=20 prompts, expert review for semantic preservation

2. **Experiment Execution**:
   - Run Llama-2 (7B, 13B, 70B) on TruthfulQA + paraphrases
   - Compute dimension scores (reliability, robustness, fairness)
   - Statistical analysis: Pearson correlations, Fisher z-test, permutation test

3. **Interpretation**:
   - Classify outcome: independence, positive coupling, or negative coupling
   - If moderation significant: report factual vs. misinformation correlation differences
   - Compare against random ablation baseline

---

**Phase 2A Complete** — Hypothesis validated and ready for Phase 2B verification protocol design.
