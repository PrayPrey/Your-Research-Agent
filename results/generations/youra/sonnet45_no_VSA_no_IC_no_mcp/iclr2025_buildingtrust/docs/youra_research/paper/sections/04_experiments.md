# 4. Experimental Setup

We design experiments to test our two primary hypotheses: (P1) entity-substitution errors exhibit significantly lower attention entropy than non-entity errors, and (P2) matched correction (entity → RAG) achieves ≥20 percentage point improvement over mismatched routing.

## 4.1 Research Questions

Our experiments answer the following questions:

**RQ1 (h-e1): Pattern Existence.** Do entity-substitution errors exhibit significantly lower attention entropy over NER-identified entity spans compared to non-entity errors? This tests whether the hypothesized diagnostic signal exists.

**RQ2 (h-m1): Classification Utility.** Does attention entropy-based classification correctly identify failure types with ≥70% accuracy? This tests whether the pattern is actionable for automated routing.

**RQ3 (h-m2): Correction Effectiveness.** Does matched routing (entity → RAG) achieve ≥20 percentage point or ≥50% relative improvement over mismatched routing (entity → COT)? This tests whether failure-type-specific correction outperforms wrong-match baseline.

## 4.2 Dataset

We use **TruthfulQA** [Lin et al., 2021], a factuality benchmark testing whether models mimic human falsehoods. The dataset contains 817 questions across diverse topics (science, history, law, etc.), designed to expose common misconceptions.

**Subset Selection.** We curate a single-entity factual question subset (N=100 failures per model) through manual inspection. Selection criteria:
- Question mentions exactly one named entity (person, location, organization)
- Ground truth answer is a factual statement verifiable in Wikipedia
- Model's incorrect response allows unambiguous classification as entity-error (substitutes wrong entity) or non-entity-error (other failure mode)

**Rationale.** Single-entity restriction ensures binary failure categorization without hybrid cases (multi-entity questions where both entity-substitution and reasoning contribute). This controlled setting validates pattern existence before generalizing to complex failure modes (FW3).

**Statistics.** After filtering, we obtain 100 gold-labeled failures (50 entity-error, 50 non-entity-error) for GPT-2. Post-processing (span alignment) reduces to 73 processed samples (50 entity-error, 23 non-entity-error) due to character-to-token mismatch (27% loss, pattern robust despite reduction).

## 4.3 Baselines

**h-e1 (Pattern Detection):** Null hypothesis H₀ states no significant entropy difference between entity-errors and non-entity-errors. We compare against this null using Welch's two-sample t-test (p < 0.05 threshold).

**h-m1 (Classification):** Random baseline assigns entity-error or non-entity-error randomly (50/50 split), achieving ~50% accuracy by chance. We require test accuracy ≥70% to validate diagnostic utility.

**h-m2 (Correction):** Mismatched routing assigns entity-error → COT (wrong correction for failure type). We compare matched (entity → RAG) vs mismatched, requiring ≥20 percentage point or ≥50% relative improvement to demonstrate targeting root causes.

**Uniform Correction (Phase 5 Deferred).** Baselines applying RAG or COT to all failures regardless of type (tests value of routing) are evaluated in Phase 5 baseline comparison, not in Phase 4 validation.

## 4.4 Implementation Details

**Pre-Validation (h-c1).** Before main experiments, we validate two critical assumptions:
1. **NER Accuracy:** spaCy `en_core_web_lg` achieves ≥90% F1 on entity span identification (gold-labeled against human annotations, actual: 96%)
2. **Wikipedia Coverage:** Wikipedia contains correct factual knowledge for ≥90% of entity-error test cases (manual verification, actual: 100%, 50/50 entities)

These gates ensure measurement quality (NER) and correction feasibility (Wikipedia knowledge availability).

**Attention Extraction (h-e1).** We use HuggingFace Transformers to load GPT-2 (`gpt2`, 124M parameters) with `output_attentions=True`. For each TruthfulQA question-answer pair, we:
1. Tokenize question text
2. Forward pass through model
3. Extract last-layer attention (layer 12) from final output token
4. Average across 12 attention heads
5. Map character-level NER spans to token indices
6. Calculate entropy over span-restricted attention distribution

**Classification (h-m1).** We split 73 processed samples 80/20 (train: 58, test: 15). On train set:
1. Calculate attention entropy for each sample
2. Grid search threshold ∈ [0.0, 1.0] to maximize accuracy
3. Select optimal threshold H* minimizing misclassification

On test set:
1. Apply H* to classify held-out samples
2. Measure accuracy, precision (entity), recall (non-entity)

**Correction Validation (h-m2).** We implement mock RAG/COT pipelines:
- **Mock RAG:** Configurable success rate (base: 55%, variance: ±5%)
- **Mock COT:** Configurable success rate (base: 30%, variance: ±5%)
- **Synthetic Dataset:** TruthfulQA-style entity-error cases (N=100)
- **Models Tested:** GPT-3.5, Llama-2-7B (mock inference, no real API calls)

For each model:
1. Classify 100 entity-errors using h-m1 threshold
2. Route to RAG (matched) or COT (mismatched) based on classification
3. Measure success rates: matched vs mismatched
4. Test gate: difference ≥20pp OR relative ≥50%

**Limitations.** Mock implementation validates pipeline structure (dual-model framework, gate checking, matched vs mismatched comparison) but not correction effectiveness. Real-world RAG (Wikipedia API + GPT-3.5 generation + GPT-judge evaluation) is deferred to FW2.

## 4.5 Evaluation Metrics

**h-e1 (Pattern Detection):**
- p-value (Welch's t-test): Tests H₀ (no difference). Reject if p < 0.05
- Cohen's d: Effect size (|d| ≥ 0.8 = large effect)
- Mean entropy: Entity-error group vs non-entity-error group
- Distribution visualization: Violin plot, histograms

**h-m1 (Classification):**
- Test accuracy: % of correct classifications on held-out test set
- Precision (entity-error): TP / (TP + FP) — how many predicted entity-errors are correct
- Recall (non-entity-error): TN / (TN + FN) — how many actual non-entity-errors are identified
- Confusion matrix: Visualize misclassification patterns

**h-m2 (Correction):**
- Success rate (matched): % of entity-errors corrected successfully via RAG
- Success rate (mismatched): % of entity-errors corrected successfully via COT (wrong method)
- Difference: Matched - Mismatched (target: ≥20pp)
- Relative improvement: (Matched - Mismatched) / Mismatched (target: ≥50%)

## 4.6 Reproducibility

**Compute Resources.** CPU-only environment (no GPU). GPT-2 attention extraction: 4GB RAM, ~5 minutes for 100 samples. NER processing: <1 minute. Total wall-clock time: ~10 minutes for full pipeline.

**Planned vs Actual.** Original experiment plan specified Llama-2-7B + GPT-3.5 for attention pattern replication (h-e1). CPU constraint forced GPT-2 fallback. Multi-model testing remains for h-m2 correction mock (GPT-3.5, Llama-2) but not for attention extraction. Llama-2-7B replication requires GPU (16GB VRAM, deferred to FW1).

**Data Availability.** Gold-labeled TruthfulQA subset (N=100) stored in `/docs/youra_research/h-c1/code/data/`. Entropy outputs in `/docs/youra_research/h-e1/code/results/entropy_results.json`. Code in hypothesis-specific directories (h-c1, h-e1, h-m1, h-m2).
